"""Daedalus: Lecture 5's live workshop (FastAPI). Deployed by deploy/daedalus_modal.py.

    /              the workshop: The Loop, Your agent, Your workflow, The race (+ Daniel's inbox on every tab)
    /wall          the class wall for the projector
    /admin         the operator's page (admin token): pause, caps, purge, warm

Every student has a secret workshop key (X-Workshop-Key on API calls, kept in the browser), their own Ledgerline sandbox
(as Emma Clarke), their own agent settings and their own workflow. Model calls are gemini-3.8-flash direct, guarded by a
pause switch, a class and a per-student daily US$ cap, rate limits and a cap on model calls in flight (copied from
Hephaestus, Lecture 4).
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
from ..toolbox import ALL, REGISTRY
from . import race as R
from .loop import SHIPPED, TWO_TOOLS, Agent, clean_config, diff, full_prompt, BARE
from .workflow import BLOCKS, SHIPPED_BLOCKS, Workflow, clean_blocks, describe

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
SKY = HERE.parent / "experience" / "static"
MODEL_SLOTS = threading.BoundedSemaphore(int(os.environ.get("DAED_MODEL_SLOTS", "48")))


class Refused(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status, self.msg = status, msg


# ----------------------------------------------------------------------------------------------- durable state
class Store:
    """Workshops, flags and spend survive a restart in a modal.Dict; reads come from memory (as Hephaestus's)."""

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
            time.sleep(1.0)
            self.flush()


class Guard:
    """The instructor's switches, the day's spend (class and per student, US$ from tokens) and rate limits."""

    LIMITS = {"step": (40, 60), "run": (12, 60), "six": (6, 600), "race": (4, 600), "workflow": (40, 60), "join": (120, 600),
              "sign": (60, 60), "global": (900, 60)}

    def __init__(self, store: Store):
        self.store, self.lock, self.hits = store, threading.Lock(), {}

    @staticmethod
    def today() -> str:
        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def flags(self) -> dict:
        f = {"enabled": True, "reason": "", "cap_usd": float(os.environ.get("DAED_CAP_USD", "40")),
             "student_cap_usd": float(os.environ.get("DAED_STUDENT_CAP_USD", "1.5")), "warm": 0}
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
            raise Refused(503, "Daedalus is paused by the instructor" + (f": {f['reason']}" if f.get("reason") else "."))
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
        super().__init__(model, cassette="daedalus", mode="live", max_tokens=4096)
        self.g, self.key = guard, key

    def chat(self, *a, **kw):
        f = self.g.flags()
        if not f.get("enabled", True):
            raise Refused(503, "Daedalus is paused by the instructor.")
        if not self.g.budget_ok(self.key):
            raise Refused(429, "Today's model budget is used up. The instructor can raise it.")
        with MODEL_SLOTS:
            r = super().chat(*a, **kw)
        p = PRICES.get(self.model_id, (0.5, 3.0))
        self.g.add(self.key, (r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6, r.tokens_in, r.tokens_out)
        return r


# ----------------------------------------------------------------------------------------------- one student
class Workshop:
    def __init__(self, key: str, name: str, data: dict | None = None):
        d = data or {}
        self.key, self.name = key, name
        self.created = d.get("created", time.time())
        self.config = clean_config(d.get("config"))
        self.blocks = clean_blocks(d.get("blocks"))
        self.six = d.get("six", [])           # "Run the six jobs" on the agent tab
        self.races = d.get("races", [])
        self.wruns = d.get("wruns", {})       # workflow runs: JSON documents, a waiting one included
        self.stats = d.get("stats", {"steps": 0, "nights": 0, "resumed": 0, "signed": 0})
        self.lock = threading.RLock()
        self.busy = threading.Lock()
        self.erp = None
        self.agent = None

    def state(self) -> dict:
        runs = dict(sorted(self.wruns.items(), key=lambda kv: kv[1].get("started", 0))[-8:])
        return {"name": self.name, "created": self.created, "config": self.config, "blocks": self.blocks,
                "six": self.six[-10:], "races": self.races[-6:], "wruns": runs, "stats": self.stats}

    def sandbox(self):
        with self.lock:
            if self.erp is None:
                self.erp = R.new_erp()
            return self.erp

    def toolbox(self, user="ECLARKE"):
        return R.toolbox(self.sandbox(), user)

    def conversation(self, llm_for):
        with self.lock:
            if self.agent is None:
                self.agent = Agent(self.toolbox(), self.config, llm_for=llm_for)
            return self.agent


def new_key() -> str:
    return "dx-" + secrets.token_urlsafe(18).replace("_", "x").replace("-", "y")


def slim_turn(t: dict) -> dict:
    return {k: t.get(k) for k in ("text", "steps", "reply", "end", "model_calls", "tool_calls", "tokens_in", "tokens_out",
                                  "seconds", "usd", "waiting", "docs")}


def slim_row(r: dict) -> dict:
    keep = ("id", "who", "right", "why", "emma_turns", "waits", "model_calls", "tool_calls", "tokens_in", "tokens_out", "usd",
            "seconds", "path", "replies", "ends", "status", "stopped_at", "failed", "repeat")
    return {k: r.get(k) for k in keep if k in r}


# ----------------------------------------------------------------------------------------------- the app
def create_app(store: Store | None = None) -> FastAPI:
    os.environ.pop("OPENROUTER_API_KEY", None)  # gemini direct only
    import httpx  # noqa: F401  (import the client once, before many threads do: Hephaestus, 5 Nov)
    import openai
    openai.OpenAI(api_key="warm-up", base_url="http://127.0.0.1:9").chat.completions  # noqa: B018
    app = FastAPI(title="Daedalus", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("DAED_DICT"))
    guard = Guard(store)
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("DAED_THREADS", "160")))
    fan = ThreadPoolExecutor(max_workers=int(os.environ.get("DAED_FAN_THREADS", "96")))
    wss: dict[str, Workshop] = {}
    jobs: dict[str, dict] = {}
    for k in store.keys("w:"):
        try:
            d = store.get(k)
            wss[k[2:]] = Workshop(k[2:], d["name"], d)
        except Exception as e:  # noqa: BLE001
            print("[daedalus] could not load", k[:8], type(e).__name__)
    app.state.wss, app.state.guard, app.state.store, app.state.jobs = wss, guard, store, jobs

    def save(ws):
        store.put("w:" + ws.key, ws.state())

    def me(req: Request) -> Workshop:
        ws = wss.get(req.headers.get("x-workshop-key") or "")
        if ws is None:
            raise HTTPException(401, "Join first: open Daedalus and enter your name.")
        return ws

    def admin(req: Request):
        want = os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    def llm_for(ws):
        return lambda m: GuardedLLM(m, guard, ws.key)

    @app.exception_handler(Refused)
    async def _refused(_, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    async def in_pool(fn, *a):
        return await asyncio.get_running_loop().run_in_executor(pool, lambda: fn(*a))

    def safe(fn):
        """Run a model-touching function; turn failures into plain messages."""
        try:
            return fn()
        except Refused:
            raise
        except Exception as e:  # noqa: BLE001
            if type(e).__name__ == "Refused":
                raise Refused(e.status, e.msg)
            print("[daedalus] failed:", type(e).__name__, str(e)[:300])
            raise HTTPException(502, "The model did not answer just now. Try again in a moment.")

    def view(ws: Workshop) -> dict:
        a = ws.agent
        return {"name": ws.name, "key": ws.key, "config": ws.config, "changed": diff(ws.config), "blocks": ws.blocks,
                "blocks_changed": describe(ws.blocks), "six": ws.six[-10:], "races": [race_summary(r) for r in ws.races[-6:]],
                "last_race": ws.races[-1] if ws.races else None, "stats": ws.stats,
                "loop": {"turns": [slim_turn(t) for t in (a.turns if a else [])][-12:], "done": a.done if a else True,
                         "waiting": a.waiting if a else None, "messages": len(a.messages) if a else 1},
                "wruns": sorted(ws.wruns.values(), key=lambda r: -r.get("started", 0))[:6],
                "spend_usd": round(guard.student_usd(ws.key), 4), "student_cap_usd": guard.flags()["student_cap_usd"]}

    def race_summary(r):
        return {k: r.get(k) for k in ("n", "at", "settings", "blocks", "totals", "repeats", "same_path")}

    # ------------------------------------------------------------------ pages
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    app.mount("/sky", StaticFiles(directory=SKY), name="sky")

    def page(name):
        return FileResponse(STATIC / name, headers={"Cache-Control": "no-cache"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page("daedalus.html")

    @app.get("/wall", response_class=HTMLResponse)
    def wall_page():
        return page("wall.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "workshops": len(wss), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running")}

    CATALOG = {"tools": [{"name": n, "title": REGISTRY[n].spec.get("title"), "writes": REGISTRY[n].writes,
                          "description": REGISTRY[n].spec["description"]} for n in ALL],
               "shipped": SHIPPED, "two": TWO_TOOLS, "all": ALL, "prompts": {"full": full_prompt(), "bare": BARE},
               "blocks": {k: {"title": v[0], "kind": v[1], "needs": v[2], "gives": v[3], "line": v[4]} for k, v in BLOCKS.items()},
               "shipped_blocks": SHIPPED_BLOCKS, "jobs": R.JOBS, "morning": R.MORNING}

    @app.get("/api/catalog")
    def catalog():
        return JSONResponse(CATALOG, headers={"Cache-Control": "max-age=300"})

    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        guard.rate(req.headers.get("x-forwarded-for", "?").split(",")[0], "join")
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Please type your name.")
        ws = Workshop(new_key(), name)
        wss[ws.key] = ws
        save(ws)
        return view(ws)

    @app.get("/api/me")
    def get_me(req: Request):
        return view(me(req))

    # ------------------------------------------------------------------ your agent: the harness knobs
    @app.post("/api/agent/config")
    async def set_config(req: Request):
        ws = me(req)
        b = await req.json()
        if ws.busy.locked():
            raise HTTPException(409, "Wait for the step in progress, then change the settings.")
        with ws.lock:
            ws.config = clean_config(b.get("config") or {})
            if ws.agent is not None:  # keep the conversation; the new harness settings apply from the next step
                st = ws.agent.state()
                st["config"] = ws.config
                st["messages"][0] = {"role": "system", "content": Agent(ws.toolbox(), ws.config).messages[0]["content"]}
                turns = ws.agent.turns
                ws.agent = Agent.from_state(st, ws.toolbox(), llm_for=llm_for(ws))
                ws.agent.turns = turns
        save(ws)
        return view(ws)

    # ------------------------------------------------------------------ the loop, one step at a time
    def locked(ws, fn):
        if not ws.busy.acquire(blocking=False):
            raise HTTPException(409, "Still working on your last step.")
        try:
            return safe(fn)
        finally:
            ws.busy.release()

    @app.post("/api/loop/say")
    async def loop_say(req: Request):
        ws = me(req)
        b = await req.json()
        text = " ".join(str(b.get("text", "")).split())[:800]
        if len(text) < 2:
            raise HTTPException(400, "Type a message.")
        guard.check(ws.key, "step")

        def go():
            a = ws.conversation(llm_for(ws))
            if not a.done:
                raise HTTPException(409, "The last message is not finished: press Next step or Run to the end.")
            t = a.say(text)
            return slim_turn(t)

        out = await in_pool(lambda: locked(ws, go))
        return {"turn": out, "done": ws.agent.done, "waiting": ws.agent.waiting}

    @app.post("/api/loop/step")
    async def loop_step(req: Request):
        ws = me(req)
        guard.check(ws.key, "step")

        def go():
            a = ws.conversation(llm_for(ws))
            if a.done:
                raise HTTPException(409, "Send a message first.")
            rec = a.step()
            ws.stats["steps"] = ws.stats.get("steps", 0) + 1
            return {"step": rec, "turn": slim_turn(a.turns[-1]), "done": a.done, "waiting": a.waiting,
                    "messages": len(a.messages)}

        out = await in_pool(lambda: locked(ws, go))
        save(ws)
        return out

    @app.post("/api/loop/run")
    async def loop_run(req: Request):
        ws = me(req)
        guard.check(ws.key, "run")

        def go():
            a = ws.conversation(llm_for(ws))
            n = 0
            while not a.done and n < 45:
                a.step()
                n += 1
            ws.stats["steps"] = ws.stats.get("steps", 0) + n
            return {"turn": slim_turn(a.turns[-1]) if a.turns else None, "done": a.done, "waiting": a.waiting,
                    "messages": len(a.messages)}

        out = await in_pool(lambda: locked(ws, go))
        save(ws)
        return out

    @app.post("/api/loop/new")
    def loop_new(req: Request):
        ws = me(req)
        with ws.lock:
            ws.agent = None
        return view(ws)

    @app.post("/api/loop/night")
    def loop_night(req: Request):
        """Save the agent's state as JSON, throw the agent away, and build a new one from the JSON (state across days)."""
        ws = me(req)
        with ws.lock:
            a = ws.agent
            if a is None or not a.turns:
                raise HTTPException(400, "Start a conversation first.")
            if not a.done:
                raise HTTPException(409, "Finish the message first.")
            text = json.dumps(a.state(), default=str)
            turns = a.turns
            ws.agent = Agent.from_state(json.loads(text), ws.toolbox(), llm_for=llm_for(ws))
            ws.agent.turns = turns
            ws.stats["nights"] = ws.stats.get("nights", 0) + 1
        save(ws)
        st = json.loads(text)
        return {"bytes": len(text), "messages": len(st["messages"]), "waiting": st["waiting"], "docs": st["docs"],
                "keys": list(st), "preview": text[:1400]}

    @app.post("/api/sandbox/reset")
    def sandbox_reset(req: Request):
        ws = me(req)
        with ws.lock:
            ws.erp = R.new_erp()
            ws.agent = None
            ws.wruns = {}
        save(ws)
        return view(ws)

    # ------------------------------------------------------------------ Daniel's inbox and Ledgerline now
    @app.get("/api/inbox")
    def inbox(req: Request):
        ws = me(req)
        out = ws.toolbox("DOKAFOR").call("list_my_approvals", {})
        rows = [r for r in out.get("waiting", []) if r.get("doc_no", "") >= "PR/2026/04417" or r.get("doc_type") == "PR"]
        rows = [r for r in rows if not (r.get("doc_type") == "PO" and r.get("doc_no") == "PO/2026/01179")]
        return {"waiting": rows, "docs": R.new_docs(ws.sandbox())}

    @app.post("/api/inbox/sign")
    async def inbox_sign(req: Request):
        ws = me(req)
        guard.rate(ws.key, "sign")
        b = await req.json()
        doc, dec = str(b.get("doc_no", "")), "reject" if b.get("decision") == "reject" else "approve"
        tool = "approve_purchase_order" if doc.startswith("PO/") else "approve_purchase_request"
        arg = {"po_no": doc} if doc.startswith("PO/") else {"request_no": doc}
        out = ws.toolbox("DOKAFOR").call(tool, {**arg, "decision": dec, "comment": "Signed in Daedalus."})
        if out.get("ok"):
            ws.stats["signed"] = ws.stats.get("signed", 0) + 1
            save(ws)
        return {"result": out, "docs": R.new_docs(ws.sandbox())}

    @app.get("/api/docs")
    def docs(req: Request):
        return R.new_docs(me(req).sandbox())

    # ------------------------------------------------------------------ your workflow
    @app.post("/api/workflow")
    async def set_workflow(req: Request):
        ws = me(req)
        b = await req.json()
        ws.blocks = clean_blocks(b.get("blocks"))
        save(ws)
        return view(ws)

    @app.post("/api/workflow/run")
    async def workflow_run(req: Request):
        ws = me(req)
        b = await req.json()
        job = R.BY_ID.get(str(b.get("job", "")))
        text = job["text"] if job else " ".join(str(b.get("text", "")).split())[:800]
        if len(text) < 2:
            raise HTTPException(400, "Pick a job or type a request.")
        guard.check(ws.key, "workflow")
        stepwise = bool(b.get("step"))

        def go():
            wf = Workflow(ws.blocks)
            run = wf.start(text, flaky=bool(b.get("flaky")))
            run["job"] = job["id"] if job else None
            wf.go(run, ws.toolbox(), llm_for(ws), one=stepwise)
            ws.wruns[run["id"]] = run
            return run

        run = await in_pool(lambda: locked(ws, go))
        save(ws)
        return run

    def wrun(ws, rid):
        run = ws.wruns.get(rid)
        if not run:
            raise HTTPException(404, "No such run (a fresh sandbox clears them).")
        return run

    @app.post("/api/workflow/step")
    async def workflow_step(req: Request):
        ws = me(req)
        b = await req.json()
        guard.check(ws.key, "workflow")
        run = wrun(ws, str(b.get("run", "")))

        def go():
            Workflow(run["blocks"]).go(run, ws.toolbox(), llm_for(ws), one=True)
            return run

        out = await in_pool(lambda: locked(ws, go))
        save(ws)
        return out

    @app.post("/api/workflow/resume")
    async def workflow_resume(req: Request):
        ws = me(req)
        b = await req.json()
        guard.check(ws.key, "workflow")
        run = wrun(ws, str(b.get("run", "")))
        if run["status"] != "waiting":
            raise HTTPException(409, "This run is not waiting.")

        def go():
            before = run["status"]
            Workflow(run["blocks"]).resume(run, ws.toolbox(), llm_for(ws))
            if before == "waiting" and run["status"] != "waiting":
                ws.stats["resumed"] = ws.stats.get("resumed", 0) + 1
            return run

        out = await in_pool(lambda: locked(ws, go))
        save(ws)
        return out

    # ------------------------------------------------------------------ jobs: the six jobs (agent) and the race
    def start(ws, kind, fn, what) -> dict:
        for j in jobs.values():
            if j["key"] == ws.key and j["kind"] == kind and j["state"] == "running":
                return public(j)
        guard.check(ws.key, what)
        jid = "j" + uuid.uuid4().hex[:12]
        j = {"id": jid, "key": ws.key, "kind": kind, "state": "running", "progress": {}, "result": None, "error": None,
             "t0": time.time()}
        jobs[jid] = j

        def run():
            try:
                j["result"] = fn(j)
                j["state"] = "done"
            except Exception as e:  # noqa: BLE001
                j["state"], j["error"] = "failed", getattr(e, "msg", None) or "Something failed on the server. Try again."
                print(f"[job {kind}] failed:", type(e).__name__, str(e)[:400])
            if len(jobs) > 3000:
                for k in sorted(jobs, key=lambda k: jobs[k]["t0"])[:500]:
                    if jobs[k]["state"] != "running":
                        jobs.pop(k, None)

        pool.submit(run)
        return public(j)

    def public(j):
        return {k: j[k] for k in ("id", "kind", "state", "progress", "result", "error")} | {"seconds": round(time.time() - j["t0"], 1)}

    @app.get("/api/job/{jid}")
    def job(jid: str, req: Request):
        ws = me(req)
        j = jobs.get(jid)
        if not j or j["key"] != ws.key:
            raise HTTPException(404, "No such job.")
        return public(j)

    def agent_rows(ws, config, j, label, repeats=1):
        lf = llm_for(ws)
        todo = [(job, k) for job in R.JOBS for k in range(repeats)]
        done = {}

        def one(t):
            job, k = t
            r = R.run_agent(job, config, lf)
            r["repeat"] = k
            done[(job["id"], k)] = r["right"]
            j["progress"][label] = [{"id": a, "k": b, "right": v} for (a, b), v in done.items()]
            return slim_row(r)

        return list(fan.map(one, todo))

    @app.post("/api/six")
    def six(req: Request):
        ws = me(req)
        config = copy.deepcopy(ws.config)

        def fn(j):
            rows = agent_rows(ws, config, j, "agent")
            run = {"n": (ws.six[-1]["n"] + 1) if ws.six else 1, "at": time.time(), "settings": diff(config), "config": config,
                   "rows": rows, "totals": R.totals(rows)}
            ws.six = (ws.six + [run])[-10:]
            save(ws)
            return run

        return start(ws, "six", fn, "six")

    @app.post("/api/race")
    async def race(req: Request):
        ws = me(req)
        b = (await req.json()) if (await req.body()) else {}
        repeats = 3 if int(b.get("repeats", 1) or 1) >= 3 else 1
        config, blocks = copy.deepcopy(ws.config), copy.deepcopy(ws.blocks)

        def fn(j):
            lf = llm_for(ws)
            wdone = {}

            def wone(job):
                r = R.run_workflow(job, blocks, lf)
                wdone[job["id"]] = r["right"]
                j["progress"]["workflow"] = [{"id": a, "right": v} for a, v in wdone.items()]
                return slim_row(r)

            wf_future = [fan.submit(wone, job) for job in R.JOBS]
            arows = agent_rows(ws, config, j, "agent", repeats)
            wrows = [f.result() for f in wf_future]
            same = {}
            for job in R.JOBS:
                paths = [tuple(r["path"]) for r in arows if r["id"] == job["id"]]
                same[job["id"]] = len(set(paths)) == 1 if len(paths) > 1 else None
            out = {"n": (ws.races[-1]["n"] + 1) if ws.races else 1, "at": time.time(), "settings": diff(config),
                   "blocks": describe(blocks), "repeats": repeats, "workflow": wrows, "agent": arows,
                   "totals": {"workflow": R.totals(wrows), "agent": R.totals(arows)}, "same_path": same}
            ws.races = (ws.races + [out])[-6:]
            save(ws)
            return out

        return start(ws, "race", fn, "race")

    # ------------------------------------------------------------------ the class wall
    @app.get("/api/wall")
    def wall():
        rows = []
        for ws in wss.values():
            last = ws.races[-1]["totals"] if ws.races else None
            best6 = max((r["totals"]["right"] for r in ws.six), default=None)
            rows.append({"name": ws.name, "changed": diff(ws.config)[:4], "blocks": len(ws.blocks),
                         "blocks_changed": describe(ws.blocks)[:3], "agent_best": best6,
                         "race_wf": last and last["workflow"]["right"], "race_ag": last and last["agent"]["right"],
                         "race_of": last and last["agent"]["of"], "race_tok_wf": last and last["workflow"]["tokens_in"],
                         "race_tok_ag": last and last["agent"]["tokens_in"], "steps": ws.stats.get("steps", 0),
                         "resumed": ws.stats.get("resumed", 0), "nights": ws.stats.get("nights", 0),
                         "at": max([ws.created] + [r["at"] for r in ws.races + ws.six])})
        rows.sort(key=lambda r: -r["at"])
        raced = [r for r in rows if r["race_ag"] is not None]
        agg = {"workshops": len(rows), "raced": len(raced),
               "wf_avg": round(sum(r["race_wf"] for r in raced) / len(raced), 1) if raced else None,
               "ag_avg": round(sum(r["race_ag"] for r in raced) / len(raced), 1) if raced else None,
               "resumed": sum(1 for r in rows if r["resumed"])}
        return {"rows": rows[:200], "agg": agg}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        s = guard.spent()
        top = sorted((s.get("students") or {}).items(), key=lambda kv: -kv[1])[:10]
        return {"flags": guard.flags(), "spend": {k: v for k, v in s.items() if k != "students"}, "day_ist": guard.today(),
                "workshops": len(wss), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running"),
                "top_spenders": [{"name": wss[k].name if k in wss else "(removed)", "usd": v} for k, v in top],
                "recent": [{"name": w.name, "races": len(w.races), "six": len(w.six), "steps": w.stats.get("steps", 0)}
                           for w in sorted(wss.values(), key=lambda w: -w.created)[:80]]}

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
        gone = [k for k, w in list(wss.items()) if b.get("all") is True or any(w.name.startswith(x) for x in pre)]
        for k in gone:
            wss.pop(k, None)
            store.delete("w:" + k)
        return {"removed": len(gone), "workshops": len(wss)}

    @app.post("/api/admin/warm")
    async def admin_warm(req: Request):
        admin(req)
        b = await req.json()
        n = max(0, min(1, int(b.get("n", 0))))

        def go():
            import modal
            modal.Function.from_name(os.environ.get("DAED_APP", "northbridge-daedalus"), "web").update_autoscaler(min_containers=n)

        await in_pool(go)
        return guard.set_flags(warm=n)

    return app
