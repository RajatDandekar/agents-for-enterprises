"""Argus: Lecture 6's live lab (FastAPI). Deployed by deploy/argus_modal.py as the Modal app northbridge-argus.

    /         the lab: 1 Traces · 2 Evals · 3 Conversations (a Guards station exists behind a flag, for the next lecture)
    /wall     the class wall for the projector
    /gateway  an LLM gateway for the class notebooks: Anthropic-compatible, the student's join key is the API key
    /admin    the operator's page (admin token): pause, caps, purge, warm

Argus Panoptes, the hundred-eyed watchman. Every student joins with a name and gets a secret key (X-Argus-Key, kept in the
browser) and their own Ask Northbridge: Lecture 5's Finale (ledgerline.course.l6.agent.Agent: the same prompt, 26 tools,
memory, model claude-sonnet-5-5), in a fresh Ledgerline sandbox at Fri 20 Nov 2026 09:10.
  1 Traces  chat; every turn is an OpenTelemetry trace (GenAI conventions), shown as a span tree with timings, tokens,
            cost and the exact arguments and results, and exported to Langfuse Cloud as a public trace. The "Thursday
            prompt" switch reproduces the incident in the student's own trace.
  2 Evals   a quick suite (6 of the class's 20 tasks) and pass^3 on "the usual", under the good, the Thursday or the
            student's own prompt: every check (outcome, trajectory, numbers in code; words by Claude Haiku) with its reason.
  3 Conversations  pick a goal and a persona; a model plays Emma and talks to the student's agent; the whole conversation
            is scored (end state in Ledgerline, order of actions across turns, asked only what it needed).
  (Guards)  nine guards, twenty attacks: built for the guardrails lecture; hidden unless ARGUS_GUARDS=1 or the admin flag.
  Gateway   POST /gateway/v1/messages (Anthropic Messages API) and /gateway/v1/chat/completions (OpenAI-compatible):
            the key is the student's ar-… join key; only the course models; charged to the same per-student budget.
Rails copied from Hermes (ledgerline.hermes.app: Store, Guard, GuardedLLM): pause switch, class and per-student US$ caps,
rate limits, a cap on model calls in flight.
"""
from __future__ import annotations

import asyncio
import json
import os
import pathlib
import secrets
import threading
import time
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult

from ..course.l6 import guards as G
from ..course.l6 import suite as S
from ..course.l6.agent import AGENT_MODEL, GOOD, JUDGE_MODEL, PROMPTS, THURSDAY, Agent
from ..course.l6.attacks import ATTACKS, setup as attack_setup, succeeded
from ..course.l6.judges import judge
from ..course.l6 import convo as CV
from ..course.l6 import tracing as TR
from ..course.l6.tracing import Tracing
from ..hermes.app import Guard as Budget, GuardedLLM, Refused, Store
from ..llm import PRICES

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
RECORDED = HERE / "recorded.json"
QUICK = ["T01", "T02", "T04", "T08", "T09", "T14"]
PRESETS = {"none": [], "code": G.DETERMINISTIC + ["output_check"], "all": G.ALL}


class ArgusBudget(Budget):
    LIMITS = {"chat": (20, 60), "evals": (3, 600), "attack": (20, 60), "convo": (6, 600), "gateway": (240, 60),
              "join": (120, 600), "global": (900, 60)}

    def flags(self) -> dict:
        f = {"enabled": True, "reason": "", "cap_usd": float(os.environ.get("ARGUS_CAP_USD", "60")),
             "student_cap_usd": float(os.environ.get("ARGUS_STUDENT_CAP_USD", "2.5")), "warm": 0,
             "guards_station": os.environ.get("ARGUS_GUARDS", "0") == "1",
             "model": os.environ.get("ARGUS_MODEL", AGENT_MODEL)}
        f.update(self.store.get("flags", {}) or {})
        return f


class ArgusLLM(GuardedLLM):
    def __init__(self, model, guard, key):
        super().__init__(model, guard, key)
        self.cassette = "argus"


class Routed(SpanExporter):
    """Keeps the spans of the last few thousand traces in memory, by trace id, for the span-tree view."""

    def __init__(self, cap: int = 4000):
        self.by: OrderedDict[str, list] = OrderedDict()
        self.cap, self.lock = cap, threading.Lock()

    def export(self, spans):
        with self.lock:
            for s in spans:
                d = json.loads(s.to_json())
                tid = d["context"]["trace_id"][2:] if d["context"]["trace_id"].startswith("0x") else d["context"]["trace_id"]
                self.by.setdefault(tid, []).append(d)
                self.by.move_to_end(tid)
            while len(self.by) > self.cap:
                self.by.popitem(last=False)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def get(self, tid: str) -> list:
        with self.lock:
            return list(self.by.get(tid, []))


def tree(spans: list[dict]) -> list[dict]:
    """A trace for the page: parents first, depth, start/end in ms from the root, the attributes that matter."""
    if not spans:
        return []
    import datetime as dt

    def ms(s):
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000
    t0 = min(ms(s["start_time"]) for s in spans)
    kids = {}
    for s in spans:
        kids.setdefault(s.get("parent_id"), []).append(s)
    for v in kids.values():
        v.sort(key=lambda s: s["start_time"])
    roots = [s for s in spans if not s.get("parent_id") or s["parent_id"] not in {x["context"]["span_id"] for x in spans}]
    out = []

    def walk(s, d):
        a = s.get("attributes") or {}
        kind = a.get("gen_ai.operation.name") or ("guardrail" if s["name"].startswith("guardrail") else "span")

        def js(k):
            v = a.get(k)
            try:
                return json.loads(v) if isinstance(v, str) and v[:1] in "[{" else v
            except Exception:  # noqa: BLE001
                return v
        row = {"name": s["name"], "depth": d, "kind": kind, "start": round(ms(s["start_time"]) - t0, 1),
               "end": round(ms(s["end_time"]) - t0, 1), "status": (s.get("status") or {}).get("status_code", "UNSET"),
               "tokens_in": a.get("gen_ai.usage.input_tokens"), "tokens_out": a.get("gen_ai.usage.output_tokens"),
               "usd": a.get("ledgerline.cost_usd"), "confirm": a.get("ledgerline.confirm"),
               "preview": a.get("ledgerline.preview_only"), "refused_by": a.get("ledgerline.refused_by"),
               "decision": a.get("ledgerline.guard.decision"), "attrs": {k: v for k, v in a.items() if not k.startswith(
                   ("gen_ai.input.messages", "gen_ai.output.messages", "langfuse.observation.input", "langfuse.observation.output",
                    "input.value", "output.value", "gen_ai.tool.call.arguments", "gen_ai.tool.call.result"))},
               "args": js("gen_ai.tool.call.arguments"), "result": js("gen_ai.tool.call.result"),
               "output": js("gen_ai.output.messages"), "input_last": (a.get("input.value") or "")[:1200]}
        out.append(row)
        for k in kids.get(s["context"]["span_id"], []):
            walk(k, d + 1)
    for r in sorted(roots, key=lambda s: s["start_time"]):
        walk(r, 0)
    return out


def new_key() -> str:
    return "ar-" + secrets.token_urlsafe(18).replace("_", "x").replace("-", "y")


class Student:
    def __init__(self, key: str, name: str, d: dict | None = None):
        d = d or {}
        self.key, self.name = key, name
        self.created = d.get("created", time.time())
        self.prompt = d.get("prompt", "good")
        self.custom = d.get("custom", "")
        self.guards = d.get("guards", PRESETS["code"])
        self.chat = d.get("chat", [])            # turns: text, reply, calls, trace_id, url, usd, seconds, prompt, incident
        self.evals = d.get("evals", [])          # eval runs (summaries + rows)
        self.attacks = d.get("attacks", [])      # attack results
        self.convos = d.get("convos", [])        # simulated conversations (summaries + turns)
        self.stats = d.get("stats", {"chats": 0, "incidents": 0, "evals": 0, "attacks": 0})
        self.stats.setdefault("convos", 0)
        self.stats.setdefault("gateway_calls", 0)
        self.agent = None
        self.lock = threading.RLock()
        self.busy = threading.Lock()

    def state(self) -> dict:
        return {"name": self.name, "created": self.created, "prompt": self.prompt, "custom": self.custom, "guards": self.guards,
                "chat": self.chat[-30:], "evals": self.evals[-8:], "attacks": self.attacks[-60:], "convos": self.convos[-12:],
                "stats": self.stats}

    def prompt_text(self) -> str:
        return self.custom if self.prompt == "custom" and self.custom.strip() else PROMPTS.get(self.prompt, GOOD)


def guard_set_label(on: list[str]) -> str:
    s = sorted(on)
    for k, v in PRESETS.items():
        if s == sorted(v):
            return k
    return "custom"


def incident_of(rec: dict, history_previews: bool) -> bool:
    """A commit (create_purchase_request confirm=true, saved) in a turn whose user message held no recorded yes."""
    commits = [c for c in rec["calls"] if c["tool"] == "create_purchase_request" and c["args"].get("confirm") and c["ok"]]
    return bool(commits) and not G.recorded_yes(rec["text"])


def create_app(store: Store | None = None) -> FastAPI:
    os.environ.pop("OPENROUTER_API_KEY", None)
    import openai
    openai.OpenAI(api_key="warm-up", base_url="http://127.0.0.1:9").chat.completions  # noqa: B018
    app = FastAPI(title="Argus", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("ARGUS_DICT"))
    budget = ArgusBudget(store)
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("ARGUS_THREADS", "160")))
    sts: dict[str, Student] = {}
    jobs: dict[str, dict] = {}
    for k in store.keys("s:"):
        try:
            d = store.get(k)
            sts[k[2:]] = Student(k[2:], d["name"], d)
        except Exception as e:  # noqa: BLE001
            print("[argus] could not load", k[:8], type(e).__name__)

    # one tracer provider for the whole lab: spans to memory (the page) and, when keys exist, to Langfuse (public traces)
    routed = Routed()
    tp = TracerProvider(resource=Resource.create({"service.name": "ask-northbridge", "service.version": "argus",
                                                  "openinference.project.name": "ask-northbridge",
                                                  "deployment.environment.name": "argus"}))
    tp.add_span_processor(SimpleSpanProcessor(routed))
    BACKENDS = TR.configured()                # langfuse / langsmith / sentry: each on when its key is in the environment
    for name in BACKENDS:
        tp.add_span_processor(BatchSpanProcessor(TR.BACKENDS[name][1](), schedule_delay_millis=1500))
    LF = "langfuse" in BACKENDS

    def trace_url(tid):                       # kept name: the Langfuse link
        return TR.trace_url(tid)

    def trace_links(tid):
        try:
            return TR.links(tid) if tid else {}
        except Exception:  # noqa: BLE001
            return {}
    app.state.sts, app.state.budget, app.state.jobs, app.state.routed = sts, budget, jobs, routed

    redact_fn = None

    def warm_models():
        nonlocal redact_fn
        try:
            G.injection_score("warm up the classifier")
            G.redact("warm up presidio 07700 900123")
            redact_fn = lambda s: G.redact(s)[0]  # noqa: E731
            print("[argus] guard models warm")
        except Exception as e:  # noqa: BLE001
            print("[argus] guard models unavailable:", type(e).__name__, str(e)[:200])
    threading.Thread(target=warm_models, daemon=True).start()

    def tracing(st, redact=False):
        return Tracing(provider=tp, public=True, redact=(redact_fn if redact else None))

    def llm_for(st):
        model = budget.flags().get("model") or AGENT_MODEL
        return lambda m: ArgusLLM(model if m == AGENT_MODEL else m, budget, st.key)

    def save(st):
        store.put("s:" + st.key, st.state())

    def me(req: Request) -> Student:
        st = sts.get(req.headers.get("x-argus-key") or "")
        if st is None:
            raise HTTPException(401, "Join first: open Argus and enter your name.")
        return st

    def admin(req: Request):
        want = os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    @app.exception_handler(Refused)
    async def refused(_req, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    async def in_pool(fn, *a):
        return await asyncio.get_running_loop().run_in_executor(pool, lambda: fn(*a))

    # ------------------------------------------------------------------ jobs
    def start(st, kind, fn, what):
        for j in jobs.values():
            if j["key"] == st.key and j["kind"] == kind and j["state"] == "running":
                return public(j)
        budget.check(st.key, what)
        jid = "j" + uuid.uuid4().hex[:12]
        j = {"id": jid, "key": st.key, "kind": kind, "state": "running", "progress": {"events": []}, "result": None,
             "error": None, "t0": time.time()}
        jobs[jid] = j

        def run():
            try:
                j["result"] = fn(j)
                j["state"] = "done"
            except Exception as e:  # noqa: BLE001
                j["state"], j["error"] = "failed", getattr(e, "msg", None) or "Something failed on the server. Try again."
                print(f"[job {kind}] failed:", type(e).__name__, str(e)[:400])
            finally:
                save(st)
            if len(jobs) > 3000:
                for k in sorted(jobs, key=lambda k: jobs[k]["t0"])[:600]:
                    if jobs[k]["state"] != "running":
                        jobs.pop(k, None)
        pool.submit(run)
        return public(j)

    def public(j, since: int = 0):
        p = dict(j["progress"])
        p["events"] = p.get("events", [])[since:]
        return {"id": j["id"], "kind": j["kind"], "state": j["state"], "progress": p, "result": j["result"],
                "error": j["error"], "seconds": round(time.time() - j["t0"], 1)}

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
        return page("argus.html")

    @app.get("/wall", response_class=HTMLResponse)
    def wall_page():
        return page("wall.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "students": len(sts), "langfuse": LF, "backends": BACKENDS, "guard_models": redact_fn is not None,
                "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running")}

    recorded = json.loads(RECORDED.read_text()) if RECORDED.exists() else {}
    CATALOG = {"prompts": {"good": GOOD, "thursday": THURSDAY}, "guards": [{"id": k, "title": v[0], "kind": v[1], "where": v[2],
                                                                           "line": v[3]} for k, v in G.GUARDS.items()],
               "presets": PRESETS, "attacks": [{k: x[k] for k in ("id", "title", "owasp", "channel", "turns")} | {
                   "session": x.get("session"), "has_mail": bool(x.get("mail"))} for x in ATTACKS],
               "tasks": [{"id": t["id"], "title": t["title"], "turns": t["turns"], "words": t.get("words"),
                          "kinds": [k for k in ("outcome", "trajectory") if t.get(k)] + (["numbers"] if t.get("numbers") else [])
                          + (["words"] if t.get("words") else [])} for t in S.TASKS],
               "quick": QUICK, "model": AGENT_MODEL, "judge": JUDGE_MODEL, "recorded": recorded, "langfuse": LF,
               "backends": BACKENDS,
               "scenarios": [{"id": k, **{x: v[x] for x in ("title", "goal", "knows", "expect", "max_turns")}} for k, v in CV.SCENARIOS.items()],
               "personas": CV.PERSONAS}

    @app.get("/api/catalog")
    def catalog():
        return JSONResponse(CATALOG, headers={"Cache-Control": "max-age=60"})

    def view(st):
        return {"name": st.name, "key": st.key, "prompt": st.prompt, "custom": st.custom, "guards": st.guards,
                "chat": st.chat[-30:], "evals": st.evals[-8:], "attacks": st.attacks[-60:], "convos": st.convos[-12:],
                "stats": st.stats, "guards_station": bool(budget.flags().get("guards_station")),
                "spend_usd": round(budget.student_usd(st.key), 4), "student_cap_usd": budget.flags()["student_cap_usd"]}

    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Type your name (two letters or more).")
        budget.rate("ip:" + (req.client.host if req.client else "x"), "join")
        st = Student(new_key(), name)
        sts[st.key] = st
        save(st)
        return view(st)

    @app.get("/api/me")
    def get_me(req: Request):
        return view(me(req))

    # ------------------------------------------------------------------ 1 · traces
    def agent_of(st, fresh=False):
        with st.lock:
            if fresh or st.agent is None or st.agent.prompt_text != st.prompt_text():
                st.agent = Agent(st.prompt_text(), tracing=tracing(st), llm_for=llm_for(st),
                                 conversation_id=f"argus-{st.key[3:11]}-{int(time.time())}", user_label=f"{st.name} (as ECLARKE)",
                                 tags=("argus", "traces"))
                st.agent.prompt_name = st.prompt if st.prompt != "custom" else "custom"
            return st.agent

    @app.post("/api/chat/prompt")
    async def chat_prompt(req: Request):
        st = me(req)
        b = await req.json()
        p = str(b.get("prompt", "good"))
        if p not in ("good", "thursday", "custom"):
            raise HTTPException(400, "Pick good, thursday or custom.")
        st.prompt = p
        if "custom" in b:
            st.custom = str(b["custom"])[:9000]
        st.agent = None
        save(st)
        return view(st)

    @app.post("/api/chat/say")
    async def chat_say(req: Request):
        st = me(req)
        b = await req.json()
        text = " ".join(str(b.get("text", "")).split())[:1200]
        if not text:
            raise HTTPException(400, "Type a message.")

        def fn(j):
            if not st.busy.acquire(timeout=1):
                raise Refused(409, "Still working on your last message.")
            try:
                ag = agent_of(st)
                rec = ag.turn(text, progress=lambda ev: j["progress"]["events"].append(ev))
                tid = rec.get("trace_id")
                inc = incident_of(rec, False)
                row = {"n": len(st.chat) + 1, "text": text, "reply": rec["reply"], "prompt": st.prompt,
                       "calls": [{k: c[k] for k in ("tool", "args", "ok", "summary", "step", "seconds")} for c in rec["calls"]],
                       "trace_id": tid, "url": trace_url(tid) if (LF and tid) else None, "links": trace_links(tid),
                       "usd": rec["usd"], "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"], "seconds": rec["seconds"],
                       "incident": inc, "conv": ag.conversation_id, "at": time.time()}
                st.chat = (st.chat + [row])[-30:]
                st.stats["chats"] += 1
                st.stats["incidents"] += int(inc)
                return {**row, "spans": tree(routed.get(tid))}
            finally:
                st.busy.release()
        return start(st, "chat", fn, "chat")

    @app.get("/api/trace/{tid}")
    def get_trace(tid: str, req: Request):
        me(req)
        return {"trace_id": tid, "spans": tree(routed.get(tid)), "url": trace_url(tid) if LF else None, "links": trace_links(tid)}

    @app.post("/api/chat/new")
    def chat_new(req: Request):
        st = me(req)
        st.agent = None
        st.chat = []
        save(st)
        return view(st)

    # ------------------------------------------------------------------ 2 · evals
    @app.post("/api/evals/run")
    async def evals_run(req: Request):
        st = me(req)
        b = await req.json()
        mode = b.get("mode", "quick")
        prompt = str(b.get("prompt", st.prompt))
        text = (str(b.get("custom") or st.custom) if prompt == "custom" else PROMPTS.get(prompt, GOOD))
        if prompt == "custom" and not text.strip():
            raise HTTPException(400, "Write your prompt first (Traces tab, My edit).")
        jobs_ = [(S.BY_ID[t], 0) for t in QUICK] if mode == "quick" else [(S.BY_ID["T01"], i) for i in range(3)]
        lf = llm_for(st)

        def jfn(rubric, reply, ev, user):
            return judge(rubric, reply, ev, user, mode="live", cassette="argus")

        def fn(j):
            rows = []

            def one(job_):
                task, rep = job_
                j["progress"]["events"].append({"kind": "start", "task": task["id"], "rep": rep})
                r = S.run_task(task, prompt=text, tracing=tracing(st), llm_for=lf, judge_fn=jfn,
                               conv=f"argus-eval-{st.key[3:11]}-{task['id']}-{rep}-{int(time.time())}", tags=("argus", "evals"))
                r["rep"] = rep
                slim = {k: r[k] for k in ("task", "title", "pass", "checks", "usd", "seconds", "error", "rep")}
                slim["reply"] = r["turns"][-1]["reply"] if r["turns"] else None
                slim["calls"] = [c for t in r["turns"] for c in t["calls"]]
                slim["trace"] = next((t.get("trace_id") for t in reversed(r["turns"]) if t.get("trace_id")), None)
                slim["url"] = trace_url(slim["trace"]) if (LF and slim["trace"]) else None
                rows.append(slim)
                j["progress"]["events"].append({"kind": "done", **{k: slim[k] for k in ("task", "rep", "pass")}})
                return slim
            with ThreadPoolExecutor(max_workers=3) as ex:
                list(ex.map(one, jobs_))
            rows.sort(key=lambda r: (r["task"], r["rep"]))
            crit = [c for r in rows for c in r["checks"] if c["kind"] in ("outcome", "trajectory")]
            ship = all(c["pass"] for c in crit) and not any(r["error"] for r in rows)
            run = {"at": time.time(), "mode": mode, "prompt": prompt, "rows": rows, "passed": sum(r["pass"] for r in rows),
                   "of": len(rows), "usd": round(sum(r["usd"] for r in rows), 4), "ship": ship,
                   "pass_k": S.pass_hat_k(rows, 3) if mode == "passk" else None,
                   "judge_vs_code": [{"task": r["task"], "code": all(c["pass"] for c in r["checks"] if c["kind"] != "words"),
                                      "judge": next((c["pass"] for c in r["checks"] if c["kind"] == "words"), None)} for r in rows]}
            st.evals = (st.evals + [run])[-8:]
            st.stats["evals"] += 1
            return run
        return start(st, "evals", fn, "evals")

    # ------------------------------------------------------------------ 3 · guards
    @app.post("/api/guards/attack")
    async def guards_attack(req: Request):
        st = me(req)
        if not budget.flags().get("guards_station"):
            raise HTTPException(404, "The Guards station opens in the next lecture.")
        b = await req.json()
        on = [g for g in (b.get("guards") or []) if g in G.GUARDS]
        st.guards = on
        if b.get("attack"):
            att = next((dict(x) for x in ATTACKS if x["id"] == b["attack"]), None)
            if att is None:
                raise HTTPException(404, "No such attack.")
        else:
            text = " ".join(str(b.get("text", "")).split())[:1200]
            if not text:
                raise HTTPException(400, "Pick an attack or write your own.")
            att = {"id": "own", "title": "My own attack", "owasp": "?", "channel": "direct", "turns": [text], "check": "any"}

        def fn(j):
            a2 = json.loads(json.dumps(att))
            ag = Agent("good", guards=G.Guards(on) if on else None, tracing=tracing(st, redact="pii" in on),
                       llm_for=llm_for(st), conversation_id=f"argus-att-{st.key[3:11]}-{a2['id']}-{int(time.time())}",
                       user_label=f"{st.name} (as ECLARKE)", tags=("argus", "guards", guard_set_label(on)))
            attack_setup(ag, a2)
            for m in a2["turns"]:
                ag.turn(m, progress=lambda ev: j["progress"]["events"].append(ev))
            if a2["check"] == "any":   # a student's own attack: report what changed and what the guards did
                w = ag.writes()
                changed = {k: len(v) for k, v in w.items() if v}
                ok, why = bool(changed), ("Ledgerline changed: " + json.dumps(changed)) if changed else "nothing changed in Ledgerline"
            else:
                ok, why = succeeded(ag, a2, json.dumps(routed.get(ag.turns[-1].get("trace_id") or ""), default=str))
            evs = [e for t in ag.turns for e in t.get("guard_events", [])]
            stopped = sorted({e["guard"] for e in evs if e["decision"] in ("refused", "blocked", "quarantined", "redacted", "flagged")})
            tid = ag.turns[-1].get("trace_id")
            row = {"at": time.time(), "attack": a2["id"], "title": a2["title"], "owasp": a2["owasp"], "guards": on,
                   "set": guard_set_label(on), "succeeded": bool(ok), "why": why, "stopped_by": stopped, "events": evs,
                   "replies": [t["reply"] for t in ag.turns], "turns": a2["turns"],
                   "calls": [{k: c[k] for k in ("tool", "args", "ok", "refused_by", "summary")} for t in ag.turns for c in t["calls"]],
                   "usd": round(sum(t["usd"] for t in ag.turns), 5), "trace_id": tid,
                   "url": trace_url(tid) if (LF and tid) else None}
            st.attacks = (st.attacks + [row])[-60:]
            st.stats["attacks"] += 1
            return {**row, "spans": tree(routed.get(tid))}
        return start(st, "attack", fn, "attack")

    # ------------------------------------------------------------------ 3 · conversations (a simulated Emma)
    @app.post("/api/convo/run")
    async def convo_run(req: Request):
        st = me(req)
        b = await req.json()
        key, persona = str(b.get("scenario", "usual")), str(b.get("persona", "terse"))
        prompt = str(b.get("prompt", "good"))
        if key not in CV.SCENARIOS or persona not in CV.PERSONAS:
            raise HTTPException(400, "Pick a goal and a persona from the lists.")
        text = (st.custom if prompt == "custom" else PROMPTS.get(prompt, GOOD))
        if prompt == "custom" and not (text or "").strip():
            raise HTTPException(400, "Write your prompt first (Traces tab, My edit).")
        lf = llm_for(st)

        def fn(j):
            r = CV.run_conversation(key, persona=persona, prompt=text, tracing=tracing(st), llm_for=lf, sim_llm_for=lf,
                                    judge_fn=lambda rubric, reply, ev, user: judge(rubric, reply, ev, user, mode="live", cassette="argus"),
                                    conv=f"argus-conv-{st.key[3:11]}-{key}-{int(time.time())}", tags=("argus",),
                                    progress=lambda ev: j["progress"]["events"].append(ev))
            r["prompt"] = prompt
            tid = next((t["trace_id"] for t in reversed(r["turns"]) if t.get("trace_id")), None)
            row = {"at": time.time(), **{k: r[k] for k in ("scenario", "title", "persona", "prompt", "goal", "expect", "pass", "gate",
                                                           "checks", "turns", "usd", "seconds", "error", "emma_done", "session")},
                   "links": trace_links(tid), "trace_id": tid}
            st.convos = (st.convos + [row])[-12:]
            st.stats["convos"] = st.stats.get("convos", 0) + 1
            return row
        return start(st, "convo", fn, "convo")

    # ------------------------------------------------------------------ the LLM gateway (for the class notebooks)
    GATEWAY_MODELS = {"claude-sonnet-5-5", "claude-haiku-5-5"}
    UPSTREAM = "https://api.anthropic.com"

    def gateway_student(req: Request) -> Student:
        key = req.headers.get("x-api-key") or ""
        auth = req.headers.get("authorization") or ""
        if not key and auth.lower().startswith("bearer "):
            key = auth[7:].strip()
        st = sts.get(key)
        if st is None:
            raise HTTPException(401, "The gateway key is your Argus join key (ar-...). Join Argus first, then copy it from the top bar.")
        return st

    async def gateway_call(req: Request, path: str, openai_style: bool):
        import httpx
        st = gateway_student(req)
        try:
            body = await req.json()
        except Exception:  # noqa: BLE001
            raise HTTPException(400, "Send JSON.")
        model = str(body.get("model", ""))
        if model not in GATEWAY_MODELS:
            raise HTTPException(400, f"The gateway serves only: {', '.join(sorted(GATEWAY_MODELS))}.")
        if body.get("stream"):
            raise HTTPException(400, "The gateway does not stream: send stream=false.")
        budget.check(st.key, "gateway")          # paused? class cap? this student's cap? rate limit
        for k in ("temperature", "top_p", "top_k"):   # current Claude models refuse sampling parameters; many eval libraries send one
            body.pop(k, None)
        cap = 8192
        for k in ("max_tokens", "max_completion_tokens"):
            if isinstance(body.get(k), int):
                body[k] = min(body[k], cap)
        real = os.environ["ANTHROPIC_API_KEY"]
        headers = {"content-type": "application/json", "x-api-key": real,
                   "anthropic-version": req.headers.get("anthropic-version", "2023-06-01")}
        if openai_style:
            headers["authorization"] = f"Bearer {real}"
        if req.headers.get("anthropic-beta"):
            headers["anthropic-beta"] = req.headers["anthropic-beta"]
        async with httpx.AsyncClient(timeout=180) as c:
            r = await c.post(UPSTREAM + path, json=body, headers=headers)
        try:
            d = r.json()
        except Exception:  # noqa: BLE001
            d = {"error": {"message": r.text[:300]}}
        if r.status_code < 300:
            u = d.get("usage") or {}
            tin = int(u.get("input_tokens") or u.get("prompt_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0) \
                + int(u.get("cache_creation_input_tokens") or 0)
            tout = int(u.get("output_tokens") or u.get("completion_tokens") or 0)
            pr = PRICES.get(model, (2.0, 10.0))
            budget.add(st.key, (tin * pr[0] + tout * pr[1]) / 1e6, tin, tout)
            st.stats["gateway_calls"] = st.stats.get("gateway_calls", 0) + 1
        return JSONResponse(d, status_code=r.status_code)

    @app.post("/gateway/v1/messages")
    async def gateway_messages(req: Request):
        return await gateway_call(req, "/v1/messages", False)

    @app.post("/gateway/v1/chat/completions")
    async def gateway_chat(req: Request):
        return await gateway_call(req, "/v1/chat/completions", True)

    @app.get("/gateway")
    def gateway_info():
        return {"what": "Argus LLM gateway for the Lecture 6 notebooks", "anthropic_base_url": "<this URL>",
                "openai_base_url": "<this URL>/v1", "key": "your Argus join key (ar-...)", "models": sorted(GATEWAY_MODELS),
                "notes": "no streaming; temperature/top_p/top_k are dropped; charged to your Argus budget"}

    # ------------------------------------------------------------------ the class wall
    @app.get("/api/wall")
    def wall():
        rows, by_set, by_attack = [], {}, {}
        for st in sts.values():
            att = [a for a in st.attacks if a["attack"] != "own"]
            rows.append({"name": st.name, "chats": st.stats.get("chats", 0), "incidents": st.stats.get("incidents", 0),
                         "evals": st.stats.get("evals", 0), "attacks": st.stats.get("attacks", 0),
                         "convos": st.stats.get("convos", 0), "convos_passed": sum(1 for c in st.convos if c.get("pass")),
                         "gateway_calls": st.stats.get("gateway_calls", 0),
                         "got_through": sum(1 for a in st.attacks if a["succeeded"]),
                         "best_eval": max((f"{e['passed']}/{e['of']}" for e in st.evals), default=None), "at": st.created})
            for a in st.attacks:
                d = by_set.setdefault(a["set"], {"tries": 0, "through": 0})
                d["tries"] += 1
                d["through"] += int(a["succeeded"])
            for a in att:
                d = by_attack.setdefault(a["attack"], {"title": a["title"], "tries": 0, "through": 0, "through_all": 0, "tries_all": 0})
                d["tries"] += 1
                d["through"] += int(a["succeeded"])
                if a["set"] == "all":
                    d["tries_all"] += 1
                    d["through_all"] += int(a["succeeded"])
        rows.sort(key=lambda r: -r["at"])
        for d in by_set.values():
            d["asr"] = round(d["through"] / d["tries"], 3) if d["tries"] else None
        agg = {"students": len(rows), "chats": sum(r["chats"] for r in rows), "incidents": sum(r["incidents"] for r in rows),
               "evals": sum(r["evals"] for r in rows), "attacks": sum(r["attacks"] for r in rows),
               "convos": sum(r["convos"] for r in rows), "gateway_calls": sum(r["gateway_calls"] for r in rows)}
        by_scn = {}
        for st in sts.values():
            for c in st.convos:
                d = by_scn.setdefault(c["scenario"], {"title": c["title"], "runs": 0, "passed": 0, "gate": 0})
                d["runs"] += 1
                d["passed"] += int(bool(c.get("pass")))
                d["gate"] += int(bool(c.get("gate")))
        return {"rows": rows[:200], "agg": agg, "by_set": by_set, "by_scenario": by_scn,
                "guards_station": bool(budget.flags().get("guards_station")),
                "by_attack": dict(sorted(by_attack.items(), key=lambda kv: -kv[1]["through"]))}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        s = budget.spent()
        top = sorted((s.get("students") or {}).items(), key=lambda kv: -kv[1])[:10]
        return {"flags": budget.flags(), "spend": {k: v for k, v in s.items() if k != "students"}, "day_ist": budget.today(),
                "students": len(sts), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running"),
                "langfuse": LF, "backends": BACKENDS, "guard_models": redact_fn is not None,
                "top_spenders": [{"name": sts[k].name if k in sts else "(removed)", "usd": v} for k, v in top]}

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
        if "model" in b and b["model"] in (AGENT_MODEL, JUDGE_MODEL):
            kw["model"] = b["model"]
        if "guards_station" in b:
            kw["guards_station"] = bool(b["guards_station"])
        return budget.set_flags(**kw)

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
            modal.Function.from_name(os.environ.get("ARGUS_APP", "northbridge-argus"), "web").update_autoscaler(min_containers=n)
        await in_pool(go)
        return budget.set_flags(warm=n)

    return app
