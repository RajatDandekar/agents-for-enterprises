"""Hephaestus: Lecture 4's live tool forge (FastAPI). Deployed by deploy/hephaestus_modal.py.

    /              the forge: The Anvil, Ask, Experiments, The Shield, Connect to Claude, Production
    /wall          the class wall for the projector
    /admin         the operator's page (admin token): pause, caps, purge, warm
    /mcp/<key>     the student's own MCP server, streamable HTTP (JSON responses), no OAuth: the unguessable key in
                   the path is the credential. One server per forge, built from that student's knobs on every request,
                   bound to that student's Ledgerline sandbox, acting as Emma.

Every student has a secret forge key (X-Forge-Key on API calls, kept in the browser). Model calls go through our
harness (ledgerline.experience.harness.AskNorthbridge) with gemini-3.8-flash, guarded by a pause switch, a class and a
per-student daily US$ cap, rate limits, and a cap on model calls in flight.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import pathlib
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import forge as F
from . import production as P
from . import runs as R

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
SKY = HERE.parent / "experience" / "static"
KNOBS = json.loads((HERE / "knobs.json").read_text())
QUESTIONS = json.loads((HERE / "questions.json").read_text())


class Refused(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status, self.msg = status, msg


# ----------------------------------------------------------------------------------------------- durable state
class Store:
    """Forges, flags and spend survive a restart in a modal.Dict; reads come from memory (as the Brain Lab's)."""

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


# ----------------------------------------------------------------------------------------------- the guard
class Guard:
    """The instructor's switches, the day's spend (class and per student, US$ estimated from tokens) and rate limits."""

    def __init__(self, store: Store):
        self.store = store
        self.lock = threading.Lock()
        self.hits: dict[str, deque] = {}

    @staticmethod
    def today() -> str:
        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def flags(self) -> dict:
        f = {"enabled": True, "mcp_enabled": True, "reason": "", "cap_usd": float(os.environ.get("HEPH_CAP_USD", "40")),
             "student_cap_usd": float(os.environ.get("HEPH_STUDENT_CAP_USD", "1.5")), "warm": 0}
        f.update(self.store.get("flags", {}) or {})
        return f

    def set_flags(self, **kw) -> dict:
        with self.lock:
            f = self.flags()
            f.update({k: v for k, v in kw.items() if v is not None})
            self.store.put("flags", f)
            return f

    def spent(self) -> dict:
        return self.store.get(f"spend:{self.today()}") or {"usd": 0.0, "calls": 0, "tokens_in": 0, "tokens_out": 0,
                                                           "turns": 0, "students": {}}

    def student_usd(self, key: str) -> float:
        return float((self.spent().get("students") or {}).get(key, 0.0))

    def add(self, key: str, r):
        usd = round((getattr(r, "inr", None) or r.cost_inr) / 88.0, 6)
        with self.lock:
            d = json.loads(json.dumps(self.spent()))
            d["usd"] = round(d["usd"] + usd, 6)
            d["calls"] += 1
            d["tokens_in"] += r.tokens_in
            d["tokens_out"] += r.tokens_out
            d.setdefault("students", {})[key] = round(d["students"].get(key, 0.0) + usd, 6)
            self.store.put(f"spend:{self.today()}", d)

    def budget_ok(self, key: str) -> bool:
        f = self.flags()
        return self.spent()["usd"] < float(f["cap_usd"]) and self.student_usd(key) < float(f["student_cap_usd"])

    def check(self, key: str, what: str = "ask"):
        f = self.flags()
        if not f.get("enabled", True):
            raise Refused(503, "Hephaestus is paused by the instructor" + (f": {f['reason']}" if f.get("reason") else "."))
        if self.spent()["usd"] >= float(f["cap_usd"]):
            raise Refused(429, "Today's model budget for the class is used up. The instructor can raise it.")
        if self.student_usd(key) >= float(f["student_cap_usd"]):
            raise Refused(429, f"You have used today's model budget for one student (US${f['student_cap_usd']:.2f}). "
                               "The instructor can raise it.")
        self.rate(key, what)

    LIMITS = {"ask": (15, 60), "six": (8, 600), "shield": (6, 600), "compare": (2, 600), "prod": (30, 600),
              "usability": (4, 600), "mcp": (180, 60), "join": (120, 600), "try": (60, 60), "global": (900, 60)}

    def rate(self, key: str, what: str):
        now = time.monotonic()
        with self.lock:
            for k, (n, win) in ((f"{key}/{what}", self.LIMITS[what]), ("*/" + what, (self.LIMITS["global"][0] * 4, 60))):
                q = self.hits.setdefault(k, deque())
                while q and now - q[0] > win:
                    q.popleft()
                if len(q) >= n:
                    who = "you" if not k.startswith("*") else "the class"
                    raise Refused(429, f"Too many requests from {who} just now ({n} per {win // 60 or 1} minute"
                                       f"{'s' if win > 60 else ''}). Wait a little and try again.")
            for k in (f"{key}/{what}", "*/" + what):
                self.hits[k].append(now)


class StudentGuard:
    """What AskNorthbridge._chat needs (budget_ok, add), bound to one student."""

    def __init__(self, guard: Guard, key: str):
        self.g, self.key = guard, key

    def budget_ok(self) -> bool:
        return self.g.budget_ok(self.key)

    def add(self, r, message: bool = False):
        self.g.add(self.key, r)


# ----------------------------------------------------------------------------------------------- the app
def create_app(store: Store | None = None) -> FastAPI:
    os.environ.pop("OPENROUTER_API_KEY", None)  # gemini-3.8-flash direct only: nothing may reroute to OpenRouter
    # Import the model client once, here, before 40 students' threads do it at the same moment: measured on 5 Nov, a
    # lazy import racing in many threads failed ("partially initialized module 'httpx'") and failed whole runs.
    import httpx  # noqa: F401
    import openai
    openai.OpenAI(api_key="warm-up", base_url="http://127.0.0.1:9").chat.completions  # noqa: B018
    F.soften_dead()
    app = FastAPI(title="Hephaestus", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("HEPH_DICT"))
    guard = Guard(store)
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("HEPH_THREADS", "160")))
    fan = ThreadPoolExecutor(max_workers=int(os.environ.get("HEPH_FAN_THREADS", "96")))
    wss: dict[str, F.Workspace] = {}
    jobs: dict[str, dict] = {}
    base_url = os.environ.get("HEPH_URL", "").rstrip("/")
    for k in store.keys("w:"):
        try:
            d = store.get(k)
            wss[k[2:]] = F.Workspace(k[2:], d["name"], d)
        except Exception as e:  # noqa: BLE001
            print("[forge] could not load", k[:8], type(e).__name__)
    app.state.wss, app.state.guard, app.state.store, app.state.jobs = wss, guard, store, jobs

    def save(ws: F.Workspace):
        store.put("w:" + ws.key, ws.state())

    def forge(req: Request) -> F.Workspace:
        key = req.headers.get("x-forge-key") or ""
        ws = wss.get(key)
        if ws is None:
            raise HTTPException(401, "Join first: open Hephaestus and enter your name.")
        return ws

    def admin(req: Request):
        want = os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    @app.exception_handler(Refused)
    async def _refused(_, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    async def in_pool(fn, *a, ex=None):
        return await asyncio.get_running_loop().run_in_executor(ex or pool, lambda: fn(*a))

    def mcp_url(ws):
        return f"{base_url}/mcp/{ws.key}"

    def view(ws: F.Workspace) -> dict:
        tb = ws.toolbox()
        return {"name": ws.name, "key": ws.key, "config": ws.config, "changed": F.diff(ws.config),
                "definitions": tb.definitions(), "runs": [run_summary(r) for r in ws.runs][-12:],
                "last_run": ws.runs[-1] if ws.runs else None, "shield": ws.shield[-4:], "prod": ws.prod,
                "notes": ws.notes[-40:], "mcp_url": mcp_url(ws), "connected": ws.connected(),
                "versions": {n: F.version_of(n, ws.config["tools"][n]) for n in F.TOOLS},
                "spend_usd": round(guard.student_usd(ws.key), 4), "student_cap_usd": guard.flags()["student_cap_usd"]}

    def run_summary(r: dict) -> dict:
        return {k: r[k] for k in ("n", "at", "settings", "totals", "host", "set") if k in r} | {
            "rows": [{k: q[k] for k in ("id", "n", "right", "why", "tools", "tool_calls", "model_calls", "tokens_in",
                                         "tokens_out", "first_call_tokens", "seconds", "door", "rule", "ledgerline_errors",
                                         "bytes", "models")} for q in r.get("rows", [])]}

    # ------------------------------------------------------------------ pages
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    app.mount("/sky", StaticFiles(directory=SKY), name="sky")

    def page(name):
        return FileResponse(STATIC / name, headers={"Cache-Control": "no-cache"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page("forge.html")

    @app.get("/wall", response_class=HTMLResponse)
    def wall_page():
        return page("wall.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "forges": len(wss), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running")}

    @app.get("/.well-known/{rest:path}")
    def well_known(rest: str):
        # No OAuth: an MCP client that looks for an authorisation server finds none and connects without one.
        return JSONResponse({"error": "not_found"}, status_code=404)

    # ------------------------------------------------------------------ the catalogue (the same for everyone)
    CATALOG = {"tools": [], "knobs": KNOBS, "questions": QUESTIONS["questions"], "probes": R.PROBES, "attacks": R.ATTACKS,
               "criteria": P.CRITERIA, "starter": F.STARTER, "legacy_names": F.LEGACY_NAMES,
               "rows_tools": list(F.ROWS_TOOLS), "output_tools": sorted(F.LEAN), "rules": {k: {"label": v["label"]} for k, v in F.RULES.items()},
               "limit_default": F.LIMIT_DEFAULT}
    for n in F.TOOLS:
        s = F.REGISTRY[n]
        CATALOG["tools"].append({"name": n, "title": s.spec["title"], "category": s.spec.get("category"),
                                 "writes": s.writes, "services": s.spec.get("services", []), "python": s.source,
                                 "shipped": F.definition(n, F.default_config()["tools"][n]), "vague": F.VAGUE.get(n),
                                 "misleading_from": F.MISLEAD_FROM.get(n), "example": s.spec.get("example") or {}})

    @app.get("/api/catalog")
    def catalog():
        return JSONResponse(CATALOG, headers={"Cache-Control": "max-age=300"})

    # ------------------------------------------------------------------ joining
    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        ip = req.headers.get("x-forwarded-for", "?").split(",")[0]
        guard.rate(ip, "join")
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Please type your name.")
        key = F.new_key()
        ws = F.Workspace(key, name)
        wss[key] = ws
        save(ws)
        return view(ws)

    @app.get("/api/me")
    def me(req: Request):
        return view(forge(req))

    @app.post("/api/config")
    async def set_config(req: Request):
        ws = forge(req)
        b = await req.json()
        if ws.ask_lock.locked():
            raise HTTPException(409, "Wait for the answer in progress, then change the knobs.")
        notes = ws.set_config(b.get("config") or {})
        save(ws)
        out = view(ws)
        out["new_notes"] = notes
        return out

    @app.post("/api/tool/try")
    async def try_tool(req: Request):
        """Call one tool directly in your sandbox, as the model would (through MCP, in memory). No model, no cost."""
        ws = forge(req)
        guard.rate(ws.key, "try")
        b = await req.json()
        name = str(b.get("tool", ""))
        args = b.get("args") if isinstance(b.get("args"), dict) else {}

        def go():
            tb = ws.toolbox()
            shown = next((s for s, n in tb.by_shown.items() if n == name), None)
            if not shown:
                return {"error": f"{name} is switched off."}
            res = F.SERVER.handle(tb, {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                       "params": {"name": shown, "arguments": args}}, "you (Try it)")
            text = res["result"]["content"][0]["text"] if "result" in res else json.dumps(res.get("error"))
            return {"shown": shown, "text": text, "chars": len(text), "isError": res.get("result", {}).get("isError")}

        return await in_pool(go)

    # ------------------------------------------------------------------ Ask (our harness, the live sandbox)
    def chat_view(ws):
        a = ws.ask
        return {"transcript": a.transcript[-40:] if a else [], "model": a.model_used if a else None}

    @app.get("/api/chat")
    def chat(req: Request):
        return chat_view(forge(req))

    @app.post("/api/ask")
    async def ask(req: Request):
        ws = forge(req)
        b = await req.json()
        text = " ".join(str(b.get("text", "")).split())[:800]
        if len(text) < 2:
            raise HTTPException(400, "Type a question.")
        guard.check(ws.key, "ask")
        if not ws.ask_lock.acquire(blocking=False):
            raise HTTPException(409, "Still answering your last message.")
        try:
            def go():
                conv = ws.conversation(StudentGuard(guard, ws.key))
                return conv.respond(text)

            try:
                out = await in_pool(go)
            except Refused:
                raise
            except Exception as e:  # noqa: BLE001
                if type(e).__name__ == "Refused":
                    raise Refused(e.status, e.msg)
                print("[ask] failed:", type(e).__name__, str(e)[:300])
                raise HTTPException(502, "The model did not answer just now. Try again in a moment.")
        finally:
            ws.ask_lock.release()
        tb = ws.toolbox()
        for c in out["cards"]:
            c["canonical"] = tb.by_shown.get(c["tool"], c["tool"])
        ws.stats["asked"] = ws.stats.get("asked", 0) + 1
        save(ws)
        return out

    @app.post("/api/ask/new")
    def ask_new(req: Request):
        ws = forge(req)
        ws.new_conversation()
        return {"ok": True}

    @app.post("/api/sandbox/reset")
    def sandbox_reset(req: Request):
        ws = forge(req)
        ws.reset_sandbox()
        return {"ok": True}

    # ------------------------------------------------------------------ jobs: six questions, the Shield, Production
    def start(ws: F.Workspace, kind: str, fn, what: str, ex=None) -> dict:
        for j in jobs.values():
            if j["key"] == ws.key and j["kind"] == kind and j["state"] == "running":
                return public(j)
        guard.check(ws.key, what) if what != "prod" else guard.rate(ws.key, "prod")
        jid = "j" + uuid.uuid4().hex[:12]
        j = {"id": jid, "key": ws.key, "kind": kind, "state": "running", "progress": {}, "result": None, "error": None,
             "t0": time.time()}
        jobs[jid] = j

        def run():
            try:
                j["result"] = fn(j)
                j["state"] = "done"
            except Exception as e:  # noqa: BLE001
                status = getattr(e, "status", None)
                j["state"], j["error"] = "failed", (getattr(e, "msg", None) or
                                                    "Something failed on the server. Try again.")
                if not status:
                    print(f"[job {kind}] failed:", type(e).__name__, str(e)[:400])
            j["seconds"] = round(time.time() - j["t0"], 1)
            if len(jobs) > 3000:
                for k in sorted(jobs, key=lambda k: jobs[k]["t0"])[:500]:
                    if jobs[k]["state"] != "running":
                        jobs.pop(k, None)

        (ex or pool).submit(run)
        return public(j)

    def public(j):
        return {k: j[k] for k in ("id", "kind", "state", "progress", "result", "error")} | {
            "seconds": round(time.time() - j["t0"], 1)}

    @app.get("/api/job/{jid}")
    def job(jid: str, req: Request):
        ws = forge(req)
        j = jobs.get(jid)
        if not j or j["key"] != ws.key:
            raise HTTPException(404, "No such job.")
        return public(j)

    @app.post("/api/six")
    async def six(req: Request):
        ws = forge(req)
        b = (await req.json()) if (await req.body()) else {}
        qset = "errors" if b.get("set") == "errors" else "six"
        config = json.loads(json.dumps(ws.config))
        sg = StudentGuard(guard, ws.key)

        def fn(j):
            def progress(qid, rows):
                j["progress"] = {"now": qid, "done": [{"id": r["id"], "right": r["right"]} for r in rows]}

            res = R.run_six(config, sg, progress, qset=qset)
            run = {"n": (ws.runs[-1]["n"] + 1) if ws.runs else 1, "at": time.time(), "settings": F.diff(config),
                   "config": config, **res}
            ws.runs = (ws.runs + [run])[-12:]
            six_runs = [r for r in ws.runs if r.get("set", "six") == "six"]
            if six_runs:
                ws.stats["right_best"] = max(r["totals"]["right"] for r in six_runs)
                ws.stats["right_last"] = six_runs[-1]["totals"]["right"]
            save(ws)
            j["progress"] = {"now": None, "done": [{"id": r["id"], "right": r["right"]} for r in res["rows"]]}
            return run

        return start(ws, "six-" + qset, fn, "six")

    @app.post("/api/shield/run")
    def shield_run(req: Request):
        ws = forge(req)
        config = json.loads(json.dumps(ws.config))
        sg = StudentGuard(guard, ws.key)

        def fn(j):
            rows = R.run_attacks(config, sg, pool=fan)
            out = {"kind": "run", "at": time.time(), "settings": F.diff(config), "rows": rows,
                   "held": sum(1 for r in rows if r["held"]), "of": sum(1 for r in rows if r["held"] is not None)}
            ws.shield = (ws.shield + [out])[-6:]
            ws.stats["attacks_stopped"] = out["held"]
            ws.stats["attacks_of"] = out["of"]
            save(ws)
            return out

        return start(ws, "shield", fn, "shield")

    @app.post("/api/shield/compare")
    def shield_compare(req: Request):
        ws = forge(req)
        config = json.loads(json.dumps(ws.config))
        sg = StudentGuard(guard, ws.key)

        def fn(j):
            res = R.compare_attacks(config, sg, pool=fan)
            out = {"kind": "compare", "at": time.time(), "settings": F.diff(config), **res}
            ws.shield = (ws.shield + [out])[-6:]
            save(ws)
            return out

        return start(ws, "compare", fn, "compare")

    @app.post("/api/prod/{cid}")
    def prod(cid: str, req: Request):
        ws = forge(req)
        if cid not in P.CHECKS and cid != "all":
            raise HTTPException(404, "No such check.")
        config = json.loads(json.dumps(ws.config))
        sg = StudentGuard(guard, ws.key)
        if cid in ("usability", "all"):
            guard.check(ws.key, "usability")

        def fn(j):
            ids = [c["id"] for c in P.CRITERIA] if cid == "all" else [cid]
            done = {}
            for i in ids:
                j["progress"] = {"now": i, "done": list(done)}
                kw = {"guard": sg, "pool": fan, "key": ws.key, "ws": ws}
                if i == "regression":
                    kw["results"] = {k: {"pass": v["pass"], "rows": v["rows"]} for k, v in done.items()}
                r = P.check(i, config, **kw)
                done[i] = r
                ws.prod[i] = {k: r[k] for k in ("id", "area", "pass", "headline", "at", "settings", "seconds")}
            save(ws)
            return {"checks": list(done.values())}

        return start(ws, "prod-" + cid, fn, "prod")

    # ------------------------------------------------------------------ Connect: the live log
    @app.get("/api/calls")
    def calls(req: Request, since: float = 0):
        ws = forge(req)
        hits = [h for h in list(ws.mcp_hits) if h["t"] > since]
        return {"hits": hits[-120:], "connected": ws.connected(), "clients": ws.clients, "now": time.time()}

    # ------------------------------------------------------------------ the MCP endpoint (streamable HTTP)
    CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version, Authorization",
            "Access-Control-Expose-Headers": "Mcp-Session-Id"}

    @app.options("/mcp/{key}")
    def mcp_options(key: str):
        return Response(status_code=204, headers=CORS)

    @app.get("/mcp/{key}")
    def mcp_get(key: str):
        # No server-to-client stream: the specification lets a server answer GET with 405.
        return Response(status_code=405, headers={**CORS, "Allow": "POST, DELETE, OPTIONS"})

    @app.delete("/mcp/{key}")
    def mcp_delete(key: str):
        return Response(status_code=204 if key in wss else 404, headers=CORS)

    @app.post("/mcp/{key}")
    async def mcp_post(key: str, req: Request):
        ws = wss.get(key)
        if ws is None:
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32001, "message":
                                 "No forge at this address. Copy your address again from the Connect tab."}},
                                status_code=404, headers=CORS)
        if not guard.flags().get("mcp_enabled", True):
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32002, "message":
                                 "Hephaestus is paused by the instructor."}}, status_code=503, headers=CORS)
        try:
            guard.rate(key, "mcp")
        except Refused as e:
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32003, "message": e.msg}},
                                status_code=429, headers=CORS)
        try:
            body = json.loads(await req.body() or b"null")
        except ValueError:
            return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
                                status_code=400, headers=CORS)
        msgs = body if isinstance(body, list) else [body]
        sid = req.headers.get("mcp-session-id")
        ua = (req.headers.get("user-agent") or "")[:80]
        new_sid = None
        client = None
        for m in msgs:
            if isinstance(m, dict) and m.get("method") == "initialize":
                ci = (m.get("params") or {}).get("clientInfo") or {}
                client = f"{ci.get('name', 'unknown')}" + (f"/{ci.get('version')}" if ci.get("version") else "")
                new_sid = uuid.uuid4().hex
        sessions = getattr(ws, "sessions", None)
        if sessions is None:
            ws.sessions = sessions = {}
        if new_sid:
            sessions[new_sid] = client
            if len(sessions) > 200:
                sessions.pop(next(iter(sessions)))
        client = client or sessions.get(sid or "") or (f"unknown ({ua})" if ua else "unknown")

        def go():
            tb = ws.toolbox()
            outs = []
            for m in msgs:
                t0 = time.perf_counter()
                r = F.SERVER.handle(tb, m, "MCP over HTTP", client)
                meth = m.get("method") if isinstance(m, dict) else None
                if meth and not meth.startswith("notifications/"):
                    p = (m.get("params") or {}) if isinstance(m, dict) else {}
                    res = (r or {}).get("result") or {}
                    ws.mcp_hits.append({"t": time.time(), "client": client, "method": meth,
                                        "tool": p.get("name") if meth == "tools/call" else None,
                                        "args": p.get("arguments") if meth == "tools/call" else None,
                                        "ok": (not res.get("isError")) if meth == "tools/call" else ("error" not in (r or {})),
                                        "text": (res.get("content") or [{}])[0].get("text", "")[:4000] if meth == "tools/call" else None,
                                        "tools": [t["name"] for t in res.get("tools", [])] if meth == "tools/list" else None,
                                        "ms": round((time.perf_counter() - t0) * 1000, 1)})
                if r is not None:
                    outs.append(r)
            return outs

        outs = await in_pool(go)
        cname = client.split("/")[0] if client else "unknown"
        c = ws.clients.get(cname) or {"first": time.time(), "calls": 0}
        c["last"] = time.time()
        c["calls"] = c.get("calls", 0) + sum(1 for m in msgs if isinstance(m, dict) and m.get("method") == "tools/call")
        c["ua"] = ua
        first_seen = cname not in ws.clients
        ws.clients[cname] = c
        if first_seen or c["calls"] % 5 == 0:
            save(ws)
        headers = dict(CORS)
        if new_sid:
            headers["Mcp-Session-Id"] = new_sid
        if not outs:
            return Response(status_code=202, headers=headers)
        return JSONResponse(outs if isinstance(body, list) else outs[0], headers=headers)

    # ------------------------------------------------------------------ the class wall
    @app.get("/api/wall")
    def wall():
        rows = []
        for ws in wss.values():
            on = sum(1 for n in F.TOOLS if ws.config["tools"][n]["on"])
            con = ws.connected()
            six_runs = [r for r in ws.runs if r.get("set", "six") == "six"]
            last = six_runs[-1]["totals"] if six_runs else None
            sh = next((s for s in reversed(ws.shield) if s.get("kind") == "run"), None)
            prod = ws.prod or {}
            rows.append({"name": ws.name, "tools_on": on, "knobs_changed": len(F.diff(ws.config)),
                         "changed": F.diff(ws.config)[:4], "runs": len(ws.runs),
                         "right_best": ws.stats.get("right_best"), "right_last": last and last["right"],
                         "of": last["of"] if last else 6, "attacks_stopped": sh and sh["held"], "attacks_of": sh and sh["of"],
                         "connected": bool(con), "client": con and con["client"],
                         "claude_calls": sum(v.get("calls", 0) for k, v in ws.clients.items() if not k.startswith(("hephaestus-", "mcp-load"))),
                         "prod_pass": sum(1 for v in prod.values() if v.get("pass")), "prod_run": len(prod),
                         "asked": ws.stats.get("asked", 0), "at": max([ws.created] + [r["at"] for r in ws.runs])})
        rows.sort(key=lambda r: -r["at"])
        agg = {"forges": len(rows), "ran_six": sum(1 for r in rows if r["runs"]),
               "connected": sum(1 for r in rows if r["connected"]),
               "right_avg": round(sum(r["right_best"] or 0 for r in rows if r["runs"]) / max(1, sum(1 for r in rows if r["runs"])), 1),
               "shielded": sum(1 for r in rows if r["attacks_stopped"] is not None)}
        return {"rows": rows[:200], "agg": agg}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        s = guard.spent()
        top = sorted((s.get("students") or {}).items(), key=lambda kv: -kv[1])[:10]
        return {"flags": guard.flags(), "spend": {k: v for k, v in s.items() if k != "students"}, "day_ist": guard.today(),
                "forges": len(wss), "jobs_running": sum(1 for j in jobs.values() if j["state"] == "running"),
                "top_spenders": [{"name": wss[k].name if k in wss else "(removed)", "usd": v} for k, v in top],
                "recent": [{"name": w.name, "runs": len(w.runs), "connected": bool(w.connected()),
                            "asked": w.stats.get("asked", 0), "changed": len(F.diff(w.config))}
                           for w in sorted(wss.values(), key=lambda w: -w.created)[:80]]}

    @app.post("/api/admin/flags")
    async def admin_flags(req: Request):
        admin(req)
        b = await req.json()
        kw = {}
        for k in ("enabled", "mcp_enabled"):
            if k in b:
                kw[k] = bool(b[k])
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
        return {"removed": len(gone), "forges": len(wss)}

    @app.post("/api/admin/warm")
    async def admin_warm(req: Request):
        admin(req)
        b = await req.json()
        n = max(0, min(1, int(b.get("n", 0))))

        def go():
            import modal

            modal.Function.from_name(os.environ.get("HEPH_APP", "northbridge-hephaestus"), "web").update_autoscaler(min_containers=n)

        await in_pool(go)
        return guard.set_flags(warm=n)

    return app
