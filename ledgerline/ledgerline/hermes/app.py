"""Hermes: Lecture 5's live lab (FastAPI). Deployed by deploy/hermes_modal.py as the Modal app northbridge-hermes.

    /         the lab: 1 Mnemosyne (memory) · 2 Workflows · 3 Background agents · 4 Triggers · 5 Ask Northbridge
    /wall     the class wall for the projector
    /admin    the operator's page (admin token): pause, caps, purge, warm

Every student joins with a name and gets a secret key (X-Hermes-Key, kept in the browser), their own Ledgerline sandbox
(goods receipts, accounts payable and the week's data), their own simulated clock (Mon 26 Oct 2026 09:00), memory,
routines, background agents, listeners and chat. Model calls are gemini-3.8-flash, direct, guarded by a pause switch, a
class and a per-student daily US$ cap, rate limits and a cap on model calls in flight (the rails of Hephaestus and
Daedalus, copied).
"""
from __future__ import annotations

import asyncio
import copy
import datetime as dt
import json
import os
import pathlib
import secrets
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..llm import LLM, PRICES
from ..toolbox import HABITS, REGISTRY
from . import agents as A
from . import memory as M
from . import routines as RT
from . import triggers as TG
from .builder import draft as draft_workflow
from .chat import Finale
from .engine import Engine, FlowError, cost_of, layout, schedule_text, validate
from .world import PEOPLE, START, Clock, at, label, new_erp, short, toolbox

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
MODEL_SLOTS = threading.BoundedSemaphore(int(os.environ.get("HERMES_MODEL_SLOTS", "64")))
DEFAULT_MEMORY = HERE / "default_memory.json"


class Refused(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status, self.msg = status, msg


# ----------------------------------------------------------------------------------------------- durable state
class Store:
    """Students, flags and spend survive a restart in a modal.Dict; reads come from memory (as Daedalus's)."""

    def __init__(self, name: str | None):
        self.mem, self.d, self._dirty, self._lock = {}, None, set(), threading.Lock()
        if name:
            try:
                import modal

                self.d = modal.Dict.from_name(name, create_if_missing=True)
                for k, v in self.d.items():
                    self.mem[k] = v
                threading.Thread(target=self._writer, daemon=True).start()
            except Exception as e:  # noqa: BLE001
                print("store: modal.Dict unavailable:", type(e).__name__, str(e)[:200])
                self.d = None

    def get(self, k, default=None):
        return self.mem.get(k, default)

    def put(self, k, v):
        with self._lock:
            self.mem[k] = v
            self._dirty.add(k)

    def delete(self, k):
        with self._lock:
            self.mem.pop(k, None)
            self._dirty.discard(k)
        if self.d is not None:
            try:
                self.d.pop(k, None)
            except Exception as e:  # noqa: BLE001
                print("store: delete failed:", type(e).__name__)

    def keys(self, prefix=""):
        return [k for k in list(self.mem) if k.startswith(prefix)]

    def flush(self):
        if self.d is None:
            return
        with self._lock:
            todo = {k: self.mem[k] for k in self._dirty if k in self.mem}
            self._dirty.clear()
        if todo:
            try:
                self.d.update(todo)
            except Exception as e:  # noqa: BLE001
                print("store: flush failed, will retry:", type(e).__name__)
                with self._lock:
                    self._dirty |= set(todo)

    def _writer(self):
        while True:
            time.sleep(1.5)
            self.flush()


class Guard:
    """The instructor's switches, the day's spend (class and per student, US$ from tokens) and rate limits."""

    LIMITS = {"memory": (6, 600), "compare": (3, 600), "draft": (12, 300), "flow": (40, 60), "clock": (20, 60),
              "event": (40, 60), "chat": (24, 60), "agent": (20, 60), "join": (120, 600), "sign": (60, 60), "global": (900, 60)}

    def __init__(self, store: Store):
        self.store, self.lock, self.hits = store, threading.Lock(), {}

    @staticmethod
    def today() -> str:
        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def flags(self) -> dict:
        f = {"enabled": True, "reason": "", "cap_usd": float(os.environ.get("HERMES_CAP_USD", "40")),
             "student_cap_usd": float(os.environ.get("HERMES_STUDENT_CAP_USD", "1.5")), "warm": 0}
        f.update(self.store.get("flags", {}) or {})
        return f

    def set_flags(self, **kw) -> dict:
        with self.lock:
            f = self.flags()
            f.update({k: v for k, v in kw.items() if v is not None})
            self.store.put("flags", f)
            return f

    def spent(self) -> dict:
        return self.store.get(f"spend:{self.today()}") or {"usd": 0.0, "calls": 0, "tokens_in": 0, "tokens_out": 0, "students": {}}

    def student_usd(self, key: str) -> float:
        return float((self.spent().get("students") or {}).get(key, 0.0))

    def add(self, key: str, usd: float, tin: int, tout: int):
        with self.lock:
            d = json.loads(json.dumps(self.spent()))
            d["usd"] = round(d["usd"] + usd, 6)
            d["calls"] += 1
            d["tokens_in"] += tin
            d["tokens_out"] += tout
            d.setdefault("students", {})[key] = round(d["students"].get(key, 0.0) + usd, 6)
            self.store.put(f"spend:{self.today()}", d)

    def budget_ok(self, key: str) -> bool:
        f = self.flags()
        return self.spent()["usd"] < float(f["cap_usd"]) and self.student_usd(key) < float(f["student_cap_usd"])

    def check(self, key: str, what: str):
        f = self.flags()
        if not f.get("enabled", True):
            raise Refused(503, "Hermes is paused by the instructor" + (f": {f['reason']}" if f.get("reason") else "."))
        if self.spent()["usd"] >= float(f["cap_usd"]):
            raise Refused(429, "Today's model budget for the class is used up. The instructor can raise it.")
        if self.student_usd(key) >= float(f["student_cap_usd"]):
            raise Refused(429, f"You have used today's model budget for one student (US${f['student_cap_usd']:.2f}). "
                               "The instructor can raise it.")
        self.rate(key, what)

    def rate(self, key: str, what: str):
        now = time.monotonic()
        with self.lock:
            for k, (n, win) in ((f"{key}/{what}", self.LIMITS[what]), ("*/" + what, (self.LIMITS["global"][0] * 4, 60))):
                q = self.hits.setdefault(k, deque())
                while q and now - q[0] > win:
                    q.popleft()
                if len(q) >= n:
                    who = "you" if not k.startswith("*") else "the class"
                    raise Refused(429, f"Too many requests from {who} just now. Wait a little and try again.")
            for k in (f"{key}/{what}", "*/" + what):
                self.hits[k].append(now)


class GuardedLLM(LLM):
    """The course's LLM, live, with the class guard around every call: pause and caps first, a slot, then the spend."""

    def __init__(self, model, guard: Guard, key: str):
        super().__init__(model, cassette="hermes", mode="live", max_tokens=8192)
        self.g, self.key = guard, key

    def chat(self, *a, **kw):
        f = self.g.flags()
        if not f.get("enabled", True):
            raise Refused(503, "Hermes is paused by the instructor.")
        if not self.g.budget_ok(self.key):
            raise Refused(429, "Today's model budget is used up. The instructor can raise it.")
        last = None
        for attempt in range(3):
            try:
                with MODEL_SLOTS:
                    r = super().chat(*a, **kw)
                break
            except Exception as e:  # noqa: BLE001  one more try on a transient provider error
                last = e
                if attempt == 2 or not any(c in str(e) for c in ("429", "500", "502", "503", "504", "timed out", "Timeout")):
                    raise
                time.sleep(1.5 * (attempt + 1))
        else:
            raise last
        p = PRICES.get(self.model_id, (0.5, 3.0))
        self.g.add(self.key, (r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6, r.tokens_in, r.tokens_out)
        return r


# ----------------------------------------------------------------------------------------------- one student
def default_memory() -> dict:
    if DEFAULT_MEMORY.exists():
        d = json.loads(DEFAULT_MEMORY.read_text())
        d["source"] = "class"
        return d
    return {"design": "openclaw", "knobs": M.DESIGNS["openclaw"]["knobs"], "files": {}, "notes": [], "source": "empty"}


class Student:
    def __init__(self, key: str, name: str, data: dict | None = None):
        d = data or {}
        self.key, self.name = key, name
        self.created = d.get("created", time.time())
        self.clock = Clock(d.get("clock"))
        self.memory = d.get("memory") or default_memory()
        self.memory.setdefault("event_notes", [])
        self.mem_rows = d.get("mem_rows", [])            # summary rows of every week run (the station's table)
        self.routines = d.get("routines", [])
        self.drafts = d.get("drafts", [])                # the last few builder drafts (records)
        self.agents = d.get("agents") or A.default_config()
        self.agent_log = d.get("agent_log", [])
        self.agent_notes = d.get("agent_notes", {})
        self.stop_all = d.get("stop_all", False)
        self.listeners = d.get("listeners") or {l["id"]: l["on"] for l in TG.LISTENERS}
        self.provenance = d.get("provenance", True)
        self.events = d.get("events", [])
        self.seen = set(d.get("seen", []))
        self.ev_state = d.get("ev_state", {})
        self.chat_log = d.get("chat_log", [])
        self.last_seen = d.get("last_seen") or START.isoformat()
        self.stats = d.get("stats", {"weeks": 0, "drafts": 0, "runs": 0, "batch": None, "agent_runs": 0, "events": 0, "chats": 0})
        self.lock = threading.RLock()
        self.busy = threading.Lock()
        self.erp = None
        self.week_results: dict[str, dict] = {}          # full results of the latest run of each design (RAM)
        self.live_week = None                            # a Week being stepped session by session
        self.runs: dict[str, dict] = {}                  # workflow runs (RAM, live while running)
        self.finale = None

    def state(self) -> dict:
        return {"name": self.name, "created": self.created, "clock": self.clock.iso(), "memory": self.memory,
                "mem_rows": self.mem_rows[-20:], "routines": self.routines[-12:], "drafts": self.drafts[-5:],
                "agents": self.agents, "agent_log": [slim_agent(r) for r in self.agent_log[-80:]], "agent_notes": self.agent_notes,
                "stop_all": self.stop_all, "listeners": self.listeners, "provenance": self.provenance,
                "events": self.events[-40:], "seen": list(self.seen)[-200:], "ev_state": self.ev_state,
                "chat_log": self.chat_log[-30:], "last_seen": self.last_seen, "stats": self.stats}

    def sandbox(self):
        with self.lock:
            if self.erp is None:
                self.erp = new_erp()
            return self.erp


def slim_agent(r: dict) -> dict:
    out = {k: v for k, v in r.items() if k not in ("steps",)}
    out["tool_calls"] = (r.get("tool_calls") or [])[:40]
    return out


def new_key() -> str:
    return "hm-" + secrets.token_urlsafe(18).replace("_", "x").replace("-", "y")


def slim_run(run: dict) -> dict:
    """A run for the page: every node's status, summary, timing and cost; the batch's per-item progress."""
    out = {k: run.get(k) for k in ("id", "workflow_id", "workflow_name", "status", "trigger_kind", "params", "started", "finished",
                                   "error", "waiting_for", "edges_taken", "log", "current", "wall_seconds")}
    out["workflow"] = run["workflow"]
    nodes = {}
    for nid, r in run["nodes"].items():
        n = {k: r.get(k) for k in ("status", "summary", "seconds", "meta", "port", "error")}
        o = r.get("output")
        if isinstance(o, dict) and "results" in o:
            o = {k: v for k, v in o.items() if k != "results"}
        n["output"] = o
        n["inputs"] = r.get("inputs")
        if r.get("progress"):
            p = r["progress"]
            n["progress"] = {"of": p["of"], "done": p["done"], "tally": dict(p["tally"]),
                             "items": [None if x is None else {k: x.get(k) for k in ("i", "label", "outcome", "status", "steps", "error")}
                                       for x in p["items"]]}
        nodes[nid] = n
    out["nodes"] = nodes
    out["cost"] = cost_of(run)
    return out


# ----------------------------------------------------------------------------------------------- the app
def create_app(store: Store | None = None) -> FastAPI:
    os.environ.pop("OPENROUTER_API_KEY", None)  # gemini direct only
    import httpx  # noqa: F401  (import the client once, before many threads do: Hephaestus, 5 Nov)
    import openai
    openai.OpenAI(api_key="warm-up", base_url="http://127.0.0.1:9").chat.completions  # noqa: B018
    try:
        M.embed(["warm up the embedder"])
    except Exception as e:  # noqa: BLE001
        print("[hermes] embedder warm-up failed:", type(e).__name__)
    app = FastAPI(title="Hermes", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("HERMES_DICT"))
    guard = Guard(store)
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("HERMES_THREADS", "200")))
    sts: dict[str, Student] = {}
    jobs: dict[str, dict] = {}
    for k in store.keys("s:"):
        try:
            d = store.get(k)
            sts[k[2:]] = Student(k[2:], d["name"], d)
        except Exception as e:  # noqa: BLE001
            print("[hermes] could not load", k[:8], type(e).__name__)
    app.state.sts, app.state.guard, app.state.store, app.state.jobs = sts, guard, store, jobs

    def save(st):
        store.put("s:" + st.key, st.state())

    def me(req: Request) -> Student:
        st = sts.get(req.headers.get("x-hermes-key") or "")
        if st is None:
            raise HTTPException(401, "Join first: open Hermes and enter your name.")
        return st

    def admin(req: Request):
        want = os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    def llm_for(st):
        return lambda m: GuardedLLM(m, guard, st.key)

    def call_tool(st):
        def go(user, name, args, t=None):
            erp = st.sandbox()
            tb = toolbox(erp, user)
            with at(erp, t or st.clock.t):
                return tb.call(name, args)
        return go

    def engine(st, now=None):
        erp = st.sandbox()
        return Engine(lambda u: toolbox(erp, u), llm_for(st), now=now or (lambda: st.clock.t))

    def health(st):
        def go(t):
            erp = st.sandbox()
            with at(erp, t):
                r = erp.call("whs_list", {}, user="ECLARKE")
            return r["rc"] != "E", (f"{r['err_cd']}: {r['msg']}" if r["rc"] == "E" else "Ledgerline answered")
        return go

    @app.exception_handler(Refused)
    async def _refused(_, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    async def in_pool(fn, *a):
        return await asyncio.get_running_loop().run_in_executor(pool, lambda: fn(*a))

    # ------------------------------------------------------------------ jobs (long work runs in the pool; the page polls)
    def start(st, kind, fn, what=None, one=True) -> dict:
        if one:
            for j in jobs.values():
                if j["key"] == st.key and j["kind"] == kind and j["state"] == "running":
                    return public(j)
        if what:
            guard.check(st.key, what)
        jid = "j" + uuid.uuid4().hex[:12]
        j = {"id": jid, "key": st.key, "kind": kind, "state": "running", "progress": {"events": []}, "result": None,
             "error": None, "t0": time.time()}
        jobs[jid] = j

        def run():
            try:
                j["result"] = fn(j)
                j["state"] = "done"
            except Exception as e:  # noqa: BLE001
                msg = getattr(e, "msg", None) or (str(e) if isinstance(e, FlowError) else None)
                j["state"], j["error"] = "failed", msg or "Something failed on the server. Try again."
                print(f"[job {kind}] failed:", type(e).__name__, str(e)[:400])
            finally:
                save(st)
            if len(jobs) > 4000:
                for k in sorted(jobs, key=lambda k: jobs[k]["t0"])[:800]:
                    if jobs[k]["state"] != "running":
                        jobs.pop(k, None)

        pool.submit(run)
        return public(j)

    def public(j, since: int = 0):
        p = dict(j["progress"])
        p["events"] = p.get("events", [])[since:]
        return {"id": j["id"], "kind": j["kind"], "state": j["state"], "progress": p, "result": j["result"], "error": j["error"],
                "seconds": round(time.time() - j["t0"], 1), "events_total": len(j["progress"].get("events", []))}

    @app.get("/api/job/{jid}")
    def job(jid: str, req: Request, since: int = 0):
        st = me(req)
        j = jobs.get(jid)
        if not j or j["key"] != st.key:
            raise HTTPException(404, "No such job.")
        out = public(j, since)
        if j["state"] == "running":
            out["result"] = None
        return out

    # ------------------------------------------------------------------ pages
    app.mount("/static", StaticFiles(directory=STATIC), name="static")

    def page(name):
        return FileResponse(STATIC / name, headers={"Cache-Control": "no-cache"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page("hermes.html")

    @app.get("/wall", response_class=HTMLResponse)
    def wall_page():
        return page("wall.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "students": len(sts), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running")}

    CATALOG = {"tools": [{"name": n, "title": REGISTRY[n].spec.get("title"), "writes": REGISTRY[n].writes,
                          "category": REGISTRY[n].spec.get("category"), "description": REGISTRY[n].spec["description"],
                          "new": n not in HABITS[:16]} for n in HABITS],
               "designs": [{"id": d, **{k: v for k, v in M.DESIGNS[d].items()}} for d in M.ORDER], "windows": M.WINDOWS,
               "writers": M.WRITERS, "week": M.WEEK, "starters": RT.STARTERS, "agents": A.catalog(),
               "buttons": TG.BUTTONS, "listeners": TG.LISTENERS, "sources": TG.SOURCES,
               "people": PEOPLE, "start": START.isoformat()}

    @app.get("/api/catalog")
    def catalog():
        return JSONResponse(CATALOG, headers={"Cache-Control": "max-age=120"})

    def view(st: Student) -> dict:
        return {"name": st.name, "key": st.key, "clock": st.clock.view(), "memory": mem_view(st), "mem_rows": st.mem_rows[-12:],
                "routines": [routine_view(r) for r in st.routines], "agents": st.agents, "stop_all": st.stop_all,
                "listeners": st.listeners, "provenance": st.provenance, "stats": st.stats,
                "spend_usd": round(guard.student_usd(st.key), 4), "student_cap_usd": guard.flags()["student_cap_usd"]}

    def mem_view(st):
        m = st.memory
        return {"design": m["design"], "title": M.DESIGNS[m["design"]]["title"], "kicker": M.DESIGNS[m["design"]]["kicker"],
                "knobs": m.get("knobs"), "source": m.get("source"), "files": sorted((m.get("files") or {}).keys()),
                "score": m.get("score"), "event_notes": len(m.get("event_notes", []))}

    def routine_view(r):
        wf = r["workflow"]
        trig = next((n for n in wf["nodes"] if n["type"] == "trigger"), {})
        c = trig.get("config", {})
        return {"id": r["id"], "name": r["name"], "description": wf.get("description"), "params": wf.get("params", []),
                "nodes": len(wf["nodes"]), "trigger": c.get("kind"), "schedule": schedule_text(c) if c.get("kind") == "schedule" else None,
                "scheduled": r.get("scheduled", False), "saved_at": r.get("saved_at"), "source": r.get("source"),
                "last": r.get("last")}

    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        guard.rate(req.headers.get("x-forwarded-for", "?").split(",")[0], "join")
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Please type your name.")
        st = Student(new_key(), name)
        sts[st.key] = st
        save(st)
        return view(st)

    @app.get("/api/me")
    def get_me(req: Request):
        return view(me(req))

    # ------------------------------------------------------------------ the clock and the sandbox
    @app.post("/api/sandbox/reset")
    def sandbox_reset(req: Request):
        st = me(req)
        if st.busy.locked():
            raise HTTPException(409, "Wait for the run in progress.")
        with st.lock:
            st.erp = new_erp()
            st.clock = Clock()
            st.runs, st.events, st.seen, st.ev_state, st.agent_log, st.agent_notes = {}, [], set(), {}, [], {}
            st.last_seen, st.finale = START.isoformat(), None
            st.memory["event_notes"] = []
        save(st)
        return view(st)

    def advance(st, j, end: dt.datetime):
        """Play the simulated clock to `end`: every background agent and scheduled routine due on the way, in time order;
        runs of the same day run side by side."""
        t0 = st.clock.t
        due = A.plan({} if st.stop_all else st.agents, st.routines, t0, end)
        done_keys = {r["key"] for r in st.agent_log}
        j["progress"].update(plan=[{"at": t.isoformat(), "kind": k, "id": i} for t, k, i in due], done=0, of=len(due))
        by_day = {}
        for t, kind, i in due:
            by_day.setdefault(t.date(), []).append((t, kind, i))
        for day in sorted(by_day):
            def one(x):
                t, kind, i = x
                key = f"{i}@{t.isoformat()}"
                if key in done_keys:
                    return {"agent": i, "key": key, "scheduled": t.isoformat(), "status": "skipped", "summary": "already ran (idempotency key)"}
                if kind == "agent":   # one Runner per run: it keeps the run's own Ledgerline calls
                    r = A.Runner(st.sandbox(), call_tool(st), llm_for(st), health(st)).run({"id": i, **st.agents[i]}, t,
                                                                                           st.agent_notes.get(i, ""))
                    if r["status"] != "failed":
                        st.agent_notes[i] = f"{t.strftime('%a %-d %b %H:%M')}: {r['summary'][:400]}"
                    return r
                return run_routine_at(st, i, t)
            with ThreadPoolExecutor(5) as ex:
                for r in ex.map(one, sorted(by_day[day])):
                    st.agent_log.append(r)
                    st.stats["agent_runs"] = st.stats.get("agent_runs", 0) + 1
                    j["progress"]["done"] += 1
                    j["progress"]["events"].append(slim_agent(r))
        st.clock.t = end
        return {"clock": st.clock.view(), "runs": len(due), "log": [slim_agent(r) for r in st.agent_log[-len(due) or len(st.agent_log):]]
                if due else [], "usd": round(sum(r.get("usd", 0) for r in st.agent_log[-len(due):]) if due else 0, 5)}

    def run_routine_at(st, rid, t):
        r = next((x for x in st.routines if x["id"] == rid), None)
        if not r:
            return {"agent": rid, "status": "failed", "summary": "routine not found"}
        eng = engine(st, now=lambda: t)
        t1 = time.time()
        try:
            run = eng.run_until_pause(eng.start(r["workflow"], {}, r.get("values")))
        except FlowError as e:
            return {"agent": rid, "kind": "routine", "title": r["name"], "key": f"{rid}@{t.isoformat()}", "scheduled": t.isoformat(),
                    "status": "failed", "summary": str(e)}
        st.runs[run["id"]] = run
        c = cost_of(run)
        return {"agent": rid, "kind": "routine", "title": r["name"], "key": f"{rid}@{t.isoformat()}", "scheduled": t.isoformat(),
                "status": "ok" if run["status"] in ("done", "waiting") else "failed", "run_id": run["id"],
                "summary": f"Routine {run['status']}: " + "; ".join(x["text"] for x in run["log"][-2:]), "usd": c["usd"],
                "tokens_in": c["tokens_in"], "tokens_out": c["tokens_out"], "seconds": round(time.time() - t1, 2),
                "changed": [], "left": A.left_for_person(st.sandbox()), "tool_calls": []}

    @app.post("/api/clock")
    async def clock(req: Request):
        st = me(req)
        b = await req.json()
        act = b.get("action")
        if act not in ("tomorrow", "week", "hour"):
            raise HTTPException(400, "action is tomorrow, week or hour")
        end = {"tomorrow": st.clock.tomorrow(), "week": st.clock.t + dt.timedelta(days=7),
               "hour": st.clock.t + dt.timedelta(hours=1)}[act]

        def fn(j):
            if not st.busy.acquire(blocking=False):
                raise Refused(409, "Another run is in progress.")
            try:
                return advance(st, j, end)
            finally:
                st.busy.release()

        return start(st, "clock", fn, "clock")

    # ------------------------------------------------------------------ 1 · Mnemosyne
    def week_job(st, design, knobs, j, label_key=None):
        lk = label_key or design

        def prog(ev):
            j["progress"]["events"].append({"design": design, **ev})
        w = M.Week(design, knobs, llm_for(st), progress=prog)
        res = w.run()
        st.week_results[design] = res
        row = M.summary_row(res)
        row["at"] = time.time()
        with st.lock:
            st.mem_rows = (st.mem_rows + [row])[-20:]
            st.stats["weeks"] = st.stats.get("weeks", 0) + 1
            st.stats["best_probes"] = max(st.stats.get("best_probes", 0), res["score"]["right"])
        return res

    def slim_result(res):
        out = {k: v for k, v in res.items() if k not in ("turns", "probes")}
        out["turns"] = [M.slim(t) for t in res["turns"]]
        out["probes"] = [M.slim(p) for p in res["probes"]]
        return out

    @app.post("/api/memory/run")
    async def memory_run(req: Request):
        st = me(req)
        b = await req.json()
        design = b.get("design") if b.get("design") in M.DESIGNS else "openclaw"
        knobs = M.clean_knobs(design, b.get("knobs"))
        return start(st, "memory", lambda j: slim_result(week_job(st, design, knobs, j)), "memory")

    @app.post("/api/memory/compare")
    async def memory_compare(req: Request):
        st = me(req)
        b = (await req.json()) if (await req.body()) else {}
        window = b.get("window")

        def fn(j):
            with ThreadPoolExecutor(5) as ex:
                res = list(ex.map(lambda d: week_job(st, d, M.clean_knobs(d, {"window": window} if window else {}), j), M.ORDER))
            return {"rows": [M.summary_row(r) for r in res]}

        return start(st, "compare", fn, "compare")

    @app.get("/api/memory/result/{design}")
    def memory_result(design: str, req: Request):
        st = me(req)
        res = st.week_results.get(design)
        if not res:
            raise HTTPException(404, "Run this design's week first.")
        return slim_result(res)

    @app.get("/api/memory/window")
    def memory_window(req: Request, design: str, kind: str = "turn", i: int = 0, call: int = -1):
        """The exact context window of one model call: the system text and every message, as the model read it."""
        st = me(req)
        res = st.week_results.get(design)
        if not res:
            raise HTTPException(404, "Run this design's week first.")
        rows = res["turns"] if kind == "turn" else res["probes"]
        if not 0 <= i < len(rows):
            raise HTTPException(404, "No such turn.")
        c = rows[i]["calls"][call]
        return {"parts": c["parts"], "tokens_in": c["tokens_in"], "window": c["window_text"], "label": c["label"]}

    @app.post("/api/memory/use")
    async def memory_use(req: Request):
        st = me(req)
        b = await req.json()
        design = b.get("design")
        res = st.week_results.get(design)
        if b.get("default"):
            st.memory = {**default_memory(), "event_notes": st.memory.get("event_notes", [])}
        elif res:
            st.memory = {"design": design, "knobs": res["knobs"], "files": res["files"], "notes": res["notes"], "source": "yours",
                         "score": res["score"], "event_notes": st.memory.get("event_notes", [])}
        else:
            raise HTTPException(404, "Run this design's week first.")
        st.finale = None
        save(st)
        return view(st)

    # ------------------------------------------------------------------ 2 · Workflows
    @app.post("/api/flow/draft")
    async def flow_draft(req: Request):
        st = me(req)
        b = await req.json()
        ask = " ".join(str(b.get("prompt", "")).split())[:900]
        if len(ask) < 12:
            raise HTTPException(400, "Describe the task in a sentence or two.")

        def fn(j):
            d = draft_workflow(ask, GuardedLLM("gemini:gemini-3.8-flash", guard, st.key),
                               on_round=lambda r: j["progress"]["events"].append(r), today=st.clock.t.date().isoformat())
            if d["workflow"]:
                d["workflow"]["id"] = "wf-" + uuid.uuid4().hex[:8]
            st.drafts = (st.drafts + [d])[-5:]
            st.stats["drafts"] = st.stats.get("drafts", 0) + 1
            st.stats["drafts_ok"] = st.stats.get("drafts_ok", 0) + (1 if d["ok"] else 0)
            return d

        return start(st, "draft", fn, "draft")

    @app.post("/api/flow/check")
    async def flow_check(req: Request):
        b = await req.json()
        wf = b.get("workflow") or {}
        problems, checks = validate(wf)
        return {"problems": problems, "checks": checks}

    @app.get("/api/flow/canned/{rid}")
    def flow_canned(rid: str):
        if rid not in RT.CANNED:
            raise HTTPException(404, "No such routine.")
        wf = RT.canned(rid)
        wf["id"] = "wf-" + rid
        return {"workflow": wf, "problems": validate(wf)[0], "checks": validate(wf)[1]}

    @app.post("/api/flow/run")
    async def flow_run(req: Request):
        st = me(req)
        b = await req.json()
        wf = b.get("workflow") or {}
        params = b.get("params") or {}
        problems, _ = validate(wf)
        if problems:
            raise HTTPException(400, "This workflow cannot run yet: " + " ".join(problems[:3]))
        guard.check(st.key, "flow")
        layout(wf)
        eng = engine(st)
        rid = "run-" + uuid.uuid4().hex[:8]
        holder = {}

        def fn(j):
            run = eng.start(wf, b.get("trigger") or {}, params, rid=rid)
            st.runs[rid] = run
            holder["run"] = run
            eng.run_until_pause(run)
            st.stats["runs"] = st.stats.get("runs", 0) + 1
            each = next((r for r in run["nodes"].values() if r.get("progress")), None)
            if each and "invoice" in json.dumps(wf).lower():
                st.stats["batch"] = {"tally": each["progress"]["tally"], "of": each["progress"]["of"],
                                     "seconds": run.get("wall_seconds"), "usd": cost_of(run)["usd"]}
            for r in st.routines:
                if r["workflow"].get("id") == wf.get("id"):
                    r["last"] = {"status": run["status"], "at": st.clock.iso(), "usd": cost_of(run)["usd"]}
            return {"run_id": rid, "status": run["status"]}

        j = start(st, "flow", fn, None, one=False)
        return {"job": j["id"], "run_id": rid}

    @app.get("/api/flow/runs/{rid}")
    def flow_get(rid: str, req: Request):
        st = me(req)
        run = st.runs.get(rid)
        if not run:
            raise HTTPException(404, "Starting…")
        return slim_run(_copy_live(run))

    def _copy_live(run):
        for _ in range(5):
            try:
                return copy.deepcopy(run)
            except RuntimeError:
                time.sleep(0.02)
        return json.loads(json.dumps(run, default=str))

    @app.get("/api/flow/runs/{rid}/item")
    def flow_item(rid: str, req: Request, node: str, i: int):
        st = me(req)
        run = st.runs.get(rid)
        if not run or node not in run["nodes"]:
            raise HTTPException(404, "No such run.")
        out = run["nodes"][node].get("output") or {}
        res = (out.get("results") or [])
        if not 0 <= i < len(res):
            raise HTTPException(404, "Not finished yet.")
        return {"item": res[i], "row": out["items"][i]}

    @app.post("/api/flow/resume")
    async def flow_resume(req: Request):
        st = me(req)
        b = await req.json()
        run = st.runs.get(str(b.get("run_id")))
        if not run:
            raise HTTPException(404, "No such run (a fresh sandbox clears runs).")
        if run["status"] != "waiting":
            raise HTTPException(409, "This run is not waiting.")
        eng = engine(st)

        def fn(j):
            eng.resume(run)
            eng.run_until_pause(run)
            return {"run_id": run["id"], "status": run["status"]}

        j = start(st, "flow", fn, "flow", one=False)
        return {"job": j["id"], "run_id": run["id"]}

    @app.post("/api/flow/save")
    async def flow_save(req: Request):
        st = me(req)
        b = await req.json()
        wf = b.get("workflow") or {}
        problems, _ = validate(wf)
        if problems:
            raise HTTPException(400, "Only a workflow with no problems can be saved.")
        name = " ".join(str(b.get("name") or wf.get("name") or "My routine").split())[:60]
        wf = copy.deepcopy(wf)
        wf["name"] = name
        wf.setdefault("id", "wf-" + uuid.uuid4().hex[:8])
        for p in wf.get("params", []):
            if p["name"] in (b.get("params") or {}):
                p["default"] = b["params"][p["name"]]
        existing = next((r for r in st.routines if r["workflow"].get("id") == wf["id"]), None)
        rec = {"id": wf["id"], "name": name, "workflow": wf, "values": b.get("params") or {}, "scheduled": bool(b.get("scheduled", True)),
               "saved_at": st.clock.iso(), "source": b.get("source", "drafted")}
        if existing:
            st.routines[st.routines.index(existing)] = rec
        else:
            st.routines.append(rec)
        st.routines = st.routines[-12:]
        st.finale = None
        save(st)
        return {"routines": [routine_view(r) for r in st.routines]}

    @app.post("/api/flow/routine")
    async def flow_routine_toggle(req: Request):
        st = me(req)
        b = await req.json()
        r = next((x for x in st.routines if x["id"] == b.get("id")), None)
        if not r:
            raise HTTPException(404, "No such routine.")
        if b.get("delete"):
            st.routines.remove(r)
        else:
            r["scheduled"] = bool(b.get("scheduled"))
        st.finale = None
        save(st)
        return {"routines": [routine_view(x) for x in st.routines]}

    @app.get("/api/flow/routines")
    def flow_routines(req: Request):
        st = me(req)
        return {"routines": [routine_view(r) for r in st.routines], "full": [r["workflow"] for r in st.routines]}

    @app.get("/api/flow/drafts")
    def flow_drafts(req: Request):
        return {"drafts": me(req).drafts}

    # ------------------------------------------------------------------ approvals and Ledgerline now (every tab)
    def inbox_rows(st):
        out = []
        for who in ("DOKAFOR", "LHUGHES"):
            r = call_tool(st)(who, "list_my_approvals", {})
            for w in r.get("waiting", []):
                if w.get("doc_no") == "PO/2026/01179":
                    continue
                out.append({**w, "approver": who, "approver_name": PEOPLE[who]["name"]})
        return out

    @app.get("/api/inbox")
    def inbox(req: Request):
        st = me(req)
        return {"waiting": inbox_rows(st)}

    @app.post("/api/inbox/sign")
    async def inbox_sign(req: Request):
        st = me(req)
        guard.rate(st.key, "sign")
        b = await req.json()
        doc, dec = str(b.get("doc_no", "")), "reject" if b.get("decision") == "reject" else "approve"
        who = b.get("as") if b.get("as") in ("DOKAFOR", "LHUGHES") else "DOKAFOR"
        if doc.startswith("PO/"):
            out = call_tool(st)(who, "approve_purchase_order", {"po_no": doc, "comment": "Signed in Hermes."})
        else:
            out = call_tool(st)(who, "approve_purchase_request", {"request_no": doc, "decision": dec, "comment": "Signed in Hermes."})
        return {"result": out, "waiting": inbox_rows(st)}

    def ledger(st):
        erp = st.sandbox()
        with erp.lock:
            inv = erp.q("SELECT status, COUNT(*) n, ROUND(SUM(gross),2) g FROM inv_hdr GROUP BY status")
            drafts = erp.q("SELECT id, recipient, subject, body, ref, created_by, created_on FROM ntf_draft WHERE status='PENDING' ORDER BY id DESC LIMIT 40")
            sent = erp.q("SELECT id, channel, recipient, subject, body, created_on FROM ntf_queue ORDER BY id DESC LIMIT 40")
            prs = erp.q("SELECT h.pr_no, h.status, h.cc_cd, l.itm_cd, l.qty, h.est_value FROM pr_hdr h JOIN pr_line l ON l.pr_no=h.pr_no "
                        "WHERE h.pr_no >= 'PR/2026/04417' ORDER BY h.pr_no DESC")
            held = erp.q("SELECT inv_no, sup_cd, po_no, gross, hold_reason FROM inv_hdr WHERE status='HD' ORDER BY inv_no")
            mail_new = erp.q1("SELECT COUNT(*) n FROM mail_msg WHERE status='NEW'")["n"]
        names = {"RC": "received", "MT": "matched", "HD": "held", "PS": "posted"}
        return {"invoices": {names[r["status"]]: {"n": r["n"], "gross": r["g"]} for r in inv}, "drafts": drafts, "sent": sent,
                "requests": prs, "held": held, "mail_new": mail_new}

    @app.get("/api/ledger")
    def ledger_now(req: Request):
        return ledger(me(req))

    @app.get("/api/mailbox")
    def mailbox(req: Request, status: str = "all"):
        st = me(req)
        r = call_tool(st)("LMORENO", "read_mailbox", {"status": status, "limit": 50})
        return r

    # ------------------------------------------------------------------ 3 · Background agents
    @app.get("/api/agents")
    def agents_get(req: Request):
        st = me(req)
        return {"config": st.agents, "stop_all": st.stop_all, "log": [slim_agent(r) for r in st.agent_log[-60:]],
                "notes": st.agent_notes, "clock": st.clock.view(), "left": A.left_for_person(st.sandbox()),
                "next": [{"at": t.isoformat(), "label": short(t), "kind": k, "id": i}
                         for t, k, i in A.plan(st.agents, st.routines, st.clock.t, st.clock.t + dt.timedelta(days=7))][:30]}

    @app.post("/api/agents/config")
    async def agents_config(req: Request):
        st = me(req)
        b = await req.json()
        if "stop_all" in b:
            st.stop_all = bool(b["stop_all"])
        aid = b.get("id")
        if aid in A.BY_ID:
            c = st.agents.setdefault(aid, A.default_config()[aid])
            if "on" in b:
                c["on"] = bool(b["on"])
            if isinstance(b.get("schedule"), dict):
                s = b["schedule"]
                every = s.get("every") if s.get("every") in ("day", "weekday", "week") else c["schedule"]["every"]
                hhmm = str(s.get("at", c["schedule"]["at"]))[:5]
                c["schedule"] = {"every": every, "at": hhmm, **({"day": s.get("day", "Mon")} if every == "week" else {})}
            for k, v in (b.get("params") or {}).items():
                if k in A.BY_ID[aid]["params"]:
                    c["params"][k] = type(A.BY_ID[aid]["params"][k])(v)
            for k, v in (b.get("limits") or {}).items():
                if k in ("max_steps", "max_tokens"):
                    c["limits"][k] = max(1, min(int(v), 200000))
                if k == "may_commit":
                    c["limits"][k] = bool(v)
        save(st)
        return agents_get(req)

    @app.post("/api/agents/run_now")
    async def agents_run_now(req: Request):
        st = me(req)
        b = await req.json()
        aid = b.get("id")
        if aid not in A.BY_ID:
            raise HTTPException(404, "No such agent.")

        def fn(j):
            runner = A.Runner(st.sandbox(), call_tool(st), llm_for(st), health(st))
            r = runner.run({"id": aid, **st.agents[aid]}, st.clock.t, st.agent_notes.get(aid, ""))
            r["manual"] = True
            st.agent_log.append(r)
            if r["status"] != "failed":
                st.agent_notes[aid] = f"{st.clock.t.strftime('%a %-d %b %H:%M')}: {r['summary'][:400]}"
            j["progress"]["events"].append(slim_agent(r))
            return slim_agent(r)

        return start(st, "agent:" + aid, fn, "agent")

    # ------------------------------------------------------------------ 4 · Triggers
    def remember(st, text, prov, source):
        st.memory.setdefault("event_notes", []).append({"text": text[:400], "prov": prov, "source": source, "at": st.clock.iso()})
        st.finale = None

    def act(st, ev, j):
        """Run the listeners on one event: dedupe, match, then each matching action, updating the chain as it goes."""
        chain = ev["chain"]

        def stage(kind, text, status="done", **kw):
            chain.append({"stage": kind, "text": text, "status": status, "wall": round(time.time() - ev["_t0"], 2), **kw})
            j["progress"]["events"].append({"event": ev["id"], "stage": kind, "text": text, "status": status})

        src = TG.SOURCES[ev["source"]]
        stage("event", f"{src['title']}: {ev['title']}", at=ev["at"])
        if ev["key"] in st.seen:
            ev["status"] = "duplicate"
            stage("listener", f"Already seen ({ev['key']}): ignored. The same delivery never runs twice.", "skipped")
            return
        st.seen.add(ev["key"])
        hit = [l for l in TG.LISTENERS if st.listeners.get(l["id"]) and TG.matches(l, ev)]
        if not hit:
            ev["status"] = "no listener"
            stage("listener", "No listener is on for this event. Nothing ran.", "skipped")
            return
        picked = dt.datetime.fromisoformat(ev["picked_at"])
        how = (f"polled at {picked.strftime('%H:%M')} (the mailbox is checked every {src['every']} minutes)"
               if src["mode"] == "poll" else "pushed at once (a webhook)")
        for l in hit:
            stage("listener", f"{l['title']} · {how}", listener=l["id"])
            try:
                res = ACTIONS[l["id"]](st, ev, j, stage)
                stage("result", res.get("text", "done"), res.get("status", "done"), **{k: v for k, v in res.items() if k not in ("text", "status")})
            except Refused:
                raise
            except Exception as e:  # noqa: BLE001
                print("[trigger] action failed:", type(e).__name__, str(e)[:300])
                stage("result", f"The action failed: {type(e).__name__}.", "error")
        ev["status"] = "ran"

    def a_invoice(st, ev, j, stage):
        wf = RT.invoice_one()
        eng = engine(st, now=lambda: dt.datetime.fromisoformat(ev["picked_at"]))
        stage("action", "Workflow: Process one invoice (read → record → match → post or hold → tell Luis)", "running")
        run = eng.run_until_pause(eng.start(wf, {"message": ev["message"]}, {}))
        st.runs[run["id"]] = run
        one = run["nodes"]["one"].get("output") or {}
        item = (one.get("items") or [{}])[0]
        c = cost_of(run)
        txt = {"posted": "Recorded, matched and posted.", "held": "Recorded and held: " + str(item.get("steps", {}).get("match", {}).get("summary", "")),
               "duplicate": "Not recorded: the supplier's invoice number is already in Ledgerline (a resent duplicate)."}.get(
            item.get("outcome"), f"Stopped: {item.get('error') or item.get('outcome')}")
        return {"text": txt, "status": "done" if item.get("outcome") in ("posted", "held", "duplicate") else "error",
                "run_id": run["id"], "usd": c["usd"], "outcome": item.get("outcome")}

    def a_parts(st, ev, j, stage):
        stage("action", "Agent: read the request, find the item, check stock, preview a purchase request", "running")
        t = dt.datetime.fromisoformat(ev["picked_at"])
        sys = TG.PARTS.format(now=t.strftime("%A %-d %B %Y, %H:%M"))
        out = TG.agent_loop(llm_for(st)("gemini:gemini-3.8-flash"), call_tool(st), "ECLARKE",
                            ["find_item", "check_stock", "find_supplier", "create_purchase_request"], sys,
                            ev["message"]["text"], t, max_steps=6, force_preview=True)
        prev = next((p for p in reversed(out["previews"]) if p["tool"] == "create_purchase_request"), None)
        ev["pending"] = prev
        ev["thread"] = [{"user": "Ask Northbridge", "text": out["reply"], "at": t.isoformat()}]
        return {"text": out["reply"], "status": "waiting" if prev else "done", "calls": out["calls"], "usd": out["usd"],
                "needs_confirm": bool(prev)}

    def a_grn(st, ev, j, stage):
        rc = ev["receive"]
        t = dt.datetime.fromisoformat(ev["picked_at"])
        g = call_tool(st)("ATANAKA", "receive_goods", {"po_no": rc["po_no"], "quantity": rc["quantity"], "confirm": True}, t)
        if not g.get("ok"):
            return {"text": f"Aiko's goods receipt failed: {g.get('error')}", "status": "error"}
        stage("event", f"Ledgerline: {g['grn_no']} posted for {rc['po_no']} ({rc['quantity']:,} x {rc['item_code']})")
        wf = RT.grn_match()
        eng = engine(st, now=lambda: t)
        stage("action", "Workflow: Goods arrived (find the order's invoices → match → post → tell the buyer)", "running")
        run = eng.run_until_pause(eng.start(wf, {"po_no": rc["po_no"], "grn_no": g["grn_no"], "quantity": rc["quantity"],
                                                 "item_code": rc["item_code"],
                                                 "buyer_handle": PEOPLE.get(rc["buyer"], {}).get("handle", "@emma")}, {}))
        st.runs[run["id"]] = run
        tally = (run["nodes"]["each"].get("output") or {}).get("tally", {})
        return {"text": f"{g['grn_no']}: invoices " + (", ".join(f"{v} {k}" for k, v in tally.items()) or "none found")
                + f"; {PEOPLE.get(rc['buyer'], {}).get('name', 'the buyer')} told.", "run_id": run["id"], "usd": cost_of(run)["usd"]}

    def a_price(st, ev, j, stage):
        stage("action", "Agent: read the e-mail (as data), find our open orders with the supplier, work out the extra cost", "running")
        t = dt.datetime.fromisoformat(ev["picked_at"])
        sys = TG.PRICE.format(now=t.strftime("%A %-d %B %Y, %H:%M"))
        out = TG.agent_loop(llm_for(st)("gemini:gemini-3.8-flash"), call_tool(st), "ECLARKE", ["list_open_orders", "send_message"],
                            sys, TG.wrap_mail(ev["message"], True), t, max_steps=4)
        return {"text": out["reply"], "calls": out["calls"], "usd": out["usd"]}

    def a_remember(st, ev, j, stage):
        stage("action", "Agent: file what matters from the e-mail in Emma's memory, tell Emma", "running")
        t = dt.datetime.fromisoformat(ev["picked_at"])
        prov_on = st.provenance
        written = []

        def rem(args):
            text = str(args.get("text", ""))[:400]
            prov = "untrusted" if prov_on else "owner"
            remember(st, text, prov, ev["message"]["sender"])
            written.append({"text": text, "prov": prov})
            return {"ok": True, **({"note": "Quarantined: written from an outside e-mail, never loaded into Emma's chats."} if prov_on else {})}

        schema = {"type": "function", "function": {"name": "remember", "description": "File one short note in Emma's memory.",
                  "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}}
        sys = TG.MAILMEM.format(now=t.strftime("%A %-d %B %Y, %H:%M")) + ("\n" + M.PROVENANCE_RULE if prov_on else "")
        out = TG.agent_loop(llm_for(st)("gemini:gemini-3.8-flash"), call_tool(st), "ECLARKE", ["send_message"], sys,
                            TG.wrap_mail(ev["message"], prov_on), t, max_steps=4, extra={"remember": (schema, rem)})
        if written and prov_on:
            txt = f"Filed {len(written)} note(s), quarantined as untrusted (provenance on): never loaded into Emma's chats."
        elif written:
            txt = f"Filed {len(written)} note(s) in Emma's memory (provenance off: they will be loaded like her own words)."
        else:
            txt = "Nothing filed."
        return {"text": txt, "written": written, "reply": out["reply"], "calls": out["calls"], "usd": out["usd"],
                "status": "warning" if (written and not prov_on) else "done"}

    def a_certs(st, ev, j, stage):
        stage("action", "Background agent: Certificate watch, run now", "running")
        t = dt.datetime.fromisoformat(ev["picked_at"])
        runner = A.Runner(st.sandbox(), call_tool(st), llm_for(st), health(st))
        r = runner.run({"id": "certs", **st.agents["certs"]}, t, st.agent_notes.get("certs", ""))
        r["trigger"] = ev["id"]
        st.agent_log.append(r)
        return {"text": r["summary"], "usd": r["usd"], "status": "done" if r["status"] != "failed" else "error"}

    ACTIONS = {"invoice": a_invoice, "parts": a_parts, "grn": a_grn, "price": a_price, "remember": a_remember, "certs": a_certs}

    def ev_view(ev):
        return {k: v for k, v in ev.items() if not k.startswith("_")}

    @app.get("/api/triggers")
    def triggers_get(req: Request):
        st = me(req)
        return {"listeners": st.listeners, "provenance": st.provenance, "events": [ev_view(e) for e in st.events[-30:]],
                "clock": st.clock.view(), "notes": st.memory.get("event_notes", [])[-20:]}

    @app.post("/api/triggers/config")
    async def triggers_config(req: Request):
        st = me(req)
        b = await req.json()
        if b.get("id") in st.listeners:
            st.listeners[b["id"]] = bool(b.get("on"))
        if "provenance" in b:
            st.provenance = bool(b["provenance"])
        save(st)
        return triggers_get(req)

    def run_event(st, ev, j):
        ev["_t0"] = time.time()
        act(st, ev, j)
        st.stats["events"] = st.stats.get("events", 0) + 1
        return ev_view(ev)

    @app.post("/api/triggers/drop")
    async def triggers_drop(req: Request):
        st = me(req)
        b = await req.json()
        kind = b.get("kind")
        if kind not in {x["id"] for x in TG.BUTTONS}:
            raise HTTPException(400, "Unknown event.")
        guard.check(st.key, "event")
        t = st.clock.t + dt.timedelta(minutes=2 + len(st.events) % 3)
        ev = TG.make_event(kind, st.sandbox(), t, st.ev_state)
        ev.update(id="E" + uuid.uuid4().hex[:6], button=kind, at=t.isoformat(), picked_at=TG.picked_at(ev["source"], t).isoformat(),
                  chain=[], status="running")
        st.events.append(ev)
        st.clock.t = max(st.clock.t, dt.datetime.fromisoformat(ev["picked_at"]))
        j = start(st, "event", lambda j: run_event(st, ev, j), None, one=False)
        return {"job": j["id"], "event": ev_view(ev)}

    @app.post("/api/triggers/replay")
    async def triggers_replay(req: Request):
        st = me(req)
        b = await req.json()
        old = next((e for e in st.events if e["id"] == b.get("id")), None)
        if not old:
            raise HTTPException(404, "No such event.")
        guard.check(st.key, "event")
        ev = {k: copy.deepcopy(v) for k, v in old.items() if k not in ("chain", "status", "pending", "thread") and not k.startswith("_")}
        ev.update(id="E" + uuid.uuid4().hex[:6], replay_of=old["id"], chain=[], status="running",
                  key=old["key"] + "-replay-" + uuid.uuid4().hex[:4], title=old["title"] + " (replayed)")
        st.events.append(ev)
        j = start(st, "event", lambda j: run_event(st, ev, j), None, one=False)
        return {"job": j["id"], "event": ev_view(ev)}

    @app.post("/api/triggers/confirm")
    async def triggers_confirm(req: Request):
        st = me(req)
        b = await req.json()
        ev = next((e for e in st.events if e["id"] == b.get("id")), None)
        if not ev or not ev.get("pending"):
            raise HTTPException(404, "Nothing waits for a confirmation here.")
        p = ev.pop("pending")
        out = call_tool(st)("ECLARKE", p["tool"], {**p["args"], "confirm": True})
        txt = (f"Emma confirmed: {out.get('request_no')} {out.get('status', '').lower()}" if out.get("ok") else f"Failed: {out.get('error')}")
        ev.setdefault("thread", []).append({"user": "Emma", "text": "Confirm", "at": st.clock.iso()})
        ev["thread"].append({"user": "Ask Northbridge", "text": txt, "at": st.clock.iso()})
        ev["chain"].append({"stage": "result", "text": txt, "status": "done" if out.get("ok") else "error"})
        save(st)
        return {"event": ev_view(ev), "result": out}

    # ------------------------------------------------------------------ 5 · Ask Northbridge, complete
    def since_view(st):
        """What happened since Emma last opened the chat: background runs, events, approvals, drafts, held invoices."""
        since = st.last_seen
        runs = [r for r in st.agent_log if (r.get("ran_at") or r.get("scheduled") or "") > since]
        evs = [e for e in st.events if e.get("at", "") > since]
        lg = ledger(st)
        return {"since": since, "since_label": label(dt.datetime.fromisoformat(since)), "runs": [slim_agent(r) for r in runs][-25:],
                "events": [{"title": e["title"], "source": e["source"], "status": e.get("status"),
                            "result": next((c["text"] for c in reversed(e.get("chain", [])) if c["stage"] == "result"), None)} for e in evs][-15:],
                "waiting": inbox_rows(st), "drafts": lg["drafts"][:12], "held": lg["held"][:12], "invoices": lg["invoices"]}

    def briefing_text(st) -> str:
        s = since_view(st)
        lines = [f"Since {s['since_label']}:"]
        for r in s["runs"][-12:]:
            lines.append(f"- {r.get('title', r.get('agent'))} ran {short(dt.datetime.fromisoformat(r['scheduled']))}"
                         f" ({r.get('status')}): {str(r.get('summary', ''))[:220]}")
        for e in s["events"][-8:]:
            lines.append(f"- Event ({e['source']}): {e['title']} -> {e['result'] or e['status']}")
        if s["waiting"]:
            lines.append(f"- Waiting for a signature: " + "; ".join(f"{w['doc_no']} ({w['approver_name']}, £{w.get('value', 0):,.0f})" for w in s["waiting"][:6]))
        if s["drafts"]:
            lines.append(f"- {len(s['drafts'])} draft(s) for Emma to read and send: " + "; ".join(d["subject"] for d in s["drafts"][:6]))
        if s["held"]:
            lines.append(f"- {len(s['held'])} invoice(s) held: " + "; ".join(f"{h['inv_no']} {h['hold_reason']}" for h in s["held"][:5]))
        if len(lines) == 1:
            lines.append("- Nothing ran and nothing came in.")
        return "\n".join(lines)

    def details(st, about):
        s = since_view(st)
        if about == "background":
            return {"ok": True, "runs": s["runs"]}
        if about == "events":
            return {"ok": True, "events": s["events"]}
        if about == "drafts":
            return {"ok": True, "drafts": s["drafts"]}
        return {"ok": True, **{k: s[k] for k in ("runs", "events", "drafts", "held", "waiting")}}

    def all_routines(st):
        if st.routines:
            return st.routines
        return [{"id": f"class-{rid}", "name": RT.CANNED[rid]["name"], "workflow": RT.canned(rid), "values": {}, "source": "class"}
                for rid in ("chase", "invoices", "reorder")]

    def chat_run_routine(st, name, params):
        rs = all_routines(st)
        r = next((x for x in rs if x["name"].lower() == name.lower()), None) or next(
            (x for x in rs if name.lower() in x["name"].lower() or x["name"].lower() in name.lower()), None)
        if not r:
            return {"ok": False, "error": f"No routine called {name!r}.", "next_step": "Use one of: " + ", ".join(x["name"] for x in rs)}
        eng = engine(st)
        try:
            run = eng.run_until_pause(eng.start(r["workflow"], {}, {**(r.get("values") or {}), **(params or {})}))
        except FlowError as e:
            return {"ok": False, "error": str(e)}
        st.runs[run["id"]] = run
        each = next((x for x in run["nodes"].values() if x.get("progress")), None)
        return {"ok": run["status"] in ("done", "waiting"), "routine": r["name"], "status": run["status"], "run_id": run["id"],
                "params": run["params"], "steps": [f"{n}: {x['status']} {x.get('summary') or ''}"[:160] for n, x in run["nodes"].items()
                                                   if x["status"] != "pending"],
                "tally": each["progress"]["tally"] if each else None, "waiting_for": run.get("waiting_for"), "cost_usd": cost_of(run)["usd"]}

    def finale(st):
        with st.lock:
            if st.finale is None:
                st.finale = Finale(llm_for(st), call_tool(st), lambda: st.clock.t, st.memory, lambda: all_routines(st),
                                   lambda: briefing_text(st), lambda about: details(st, about),
                                   lambda n, p: chat_run_routine(st, n, p), on_memory=lambda m: save(st))
            return st.finale

    @app.get("/api/chat")
    def chat_get(req: Request):
        st = me(req)
        return {"turns": st.chat_log[-30:], "memory": mem_view(st), "since": since_view(st), "clock": st.clock.view(),
                "routines": [routine_view(r) for r in all_routines(st)]}

    @app.post("/api/chat/say")
    async def chat_say(req: Request):
        st = me(req)
        b = await req.json()
        text = " ".join(str(b.get("text", "")).split())[:1200]
        if len(text) < 1:
            raise HTTPException(400, "Type a message.")
        guard.check(st.key, "chat")

        def fn(j):
            if not st.busy.acquire(timeout=1):
                raise Refused(409, "Still working on your last message.")
            try:
                f = finale(st)
                rec = f.turn(text, progress=lambda ev: j["progress"]["events"].append(ev))
                st.chat_log = (st.chat_log + [rec])[-30:]
                st.stats["chats"] = st.stats.get("chats", 0) + 1
                return rec
            finally:
                st.busy.release()

        return start(st, "chat", fn, None)

    @app.post("/api/chat/new")
    def chat_new(req: Request):
        st = me(req)
        st.finale = None
        st.last_seen = st.clock.iso()
        st.chat_log = []
        save(st)
        return chat_get(req)

    # ------------------------------------------------------------------ the class wall
    @app.get("/api/wall")
    def wall():
        rows = []
        for st in sts.values():
            last = st.mem_rows[-1] if st.mem_rows else None
            rows.append({"name": st.name, "design": last and last["title"], "probes": last and last["score"]["right"],
                         "probes_of": last and last["score"]["of"], "best_probes": st.stats.get("best_probes"),
                         "routines": len(st.routines), "drafts": st.stats.get("drafts", 0), "drafts_ok": st.stats.get("drafts_ok", 0),
                         "batch": st.stats.get("batch"), "agents_on": sum(1 for c in st.agents.values() if c.get("on")),
                         "agent_runs": st.stats.get("agent_runs", 0), "events": st.stats.get("events", 0),
                         "chats": st.stats.get("chats", 0), "clock": short(st.clock.t), "at": st.created})
        rows.sort(key=lambda r: -r["at"])
        n = len(rows)
        agg = {"students": n, "weeks": sum(1 for r in rows if r["design"]), "routines": sum(r["routines"] for r in rows),
               "batches": sum(1 for r in rows if r["batch"]), "agent_runs": sum(r["agent_runs"] for r in rows),
               "events": sum(r["events"] for r in rows), "chats": sum(r["chats"] for r in rows)}
        return {"rows": rows[:200], "agg": agg}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        s = guard.spent()
        top = sorted((s.get("students") or {}).items(), key=lambda kv: -kv[1])[:10]
        return {"flags": guard.flags(), "spend": {k: v for k, v in s.items() if k != "students"}, "day_ist": guard.today(),
                "students": len(sts), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running"),
                "top_spenders": [{"name": sts[k].name if k in sts else "(removed)", "usd": v} for k, v in top],
                "recent": [{"name": s_.name, "weeks": s_.stats.get("weeks", 0), "runs": s_.stats.get("runs", 0),
                            "chats": s_.stats.get("chats", 0)} for s_ in sorted(sts.values(), key=lambda w: -w.created)[:80]]}

    @app.post("/api/admin/flags")
    async def admin_flags(req: Request):
        admin(req)
        b = await req.json()
        kw = {}
        if "enabled" in b:
            kw["enabled"] = bool(b["enabled"])
        if "reason" in b:
            kw["reason"] = str(b["reason"])[:200]
        for k in ("cap_usd", "student_cap_usd"):
            if k in b:
                kw[k] = max(0.0, float(b[k]))
        return guard.set_flags(**kw)

    @app.post("/api/admin/purge")
    async def admin_purge(req: Request):
        admin(req)
        b = await req.json()
        pre = [str(x) for x in (b.get("prefixes") or []) if str(x)]
        gone = [k for k, s_ in list(sts.items()) if b.get("all") is True or any(s_.name.startswith(x) for x in pre)]
        for k in gone:
            sts.pop(k, None)
            store.delete("s:" + k)
        return {"removed": len(gone), "students": len(sts)}

    @app.post("/api/admin/warm")
    async def admin_warm(req: Request):
        admin(req)
        b = await req.json()
        n = max(0, min(1, int(b.get("n", 0))))

        def go():
            import modal
            modal.Function.from_name(os.environ.get("HERMES_APP", "northbridge-hermes"), "web").update_autoscaler(min_containers=n)

        await in_pool(go)
        return guard.set_flags(warm=n)

    return app
