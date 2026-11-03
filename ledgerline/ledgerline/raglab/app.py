"""The RAG Lab web app (Lecture 3): FastAPI over the Engine. Deployed by deploy/raglab_modal.py.

    /             the lab: pick every hyperparameter, see a document chunked, search live, the vector map, the metrics
    /board        the class leaderboard for the projector
    /admin        the operator's page (admin token): pause, the $ cap, purge the leaderboard
    /api/...      JSON (see the routes below)

State that must survive a restart (flags, the day's spend estimate, the leaderboard) is in the modal.Dict
RAGLAB_DICT; with no Dict (tests) it is kept in memory.
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import io
import json
import os
import pathlib
import re
import threading
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from ..course.l3 import corpus as C
from .engine import BUDGET_S, EXAMPLES, OPTIONS, SHOW_FILES, Engine, cfg_from

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
SKY = HERE.parent / "experience" / "static"
RATE_USD_S = 1.15 / 3600   # one L4 container (GPU + 4 CPU + 16 GiB), the Brain Lab's estimate, US$ a second


class Store:
    def __init__(self, name: str | None):
        self.mem: dict = {}
        self.d = None
        if name:
            try:
                import modal

                self.d = modal.Dict.from_name(name, create_if_missing=True)
            except Exception as e:  # noqa: BLE001
                print("store: no modal.Dict:", e)

    def get(self, k, default=None):
        if self.d is not None:
            try:
                return self.d.get(k, default)
            except Exception:  # noqa: BLE001
                return self.mem.get(k, default)
        return self.mem.get(k, default)

    def put(self, k, v):
        self.mem[k] = v
        if self.d is not None:
            try:
                self.d[k] = v
            except Exception as e:  # noqa: BLE001
                print("store put failed", e)

    def delete(self, k):
        self.mem.pop(k, None)
        if self.d is not None:
            try:
                self.d.pop(k)
            except Exception:  # noqa: BLE001
                pass

    def keys(self, prefix=""):
        if self.d is not None:
            try:
                return [k for k in self.d.keys() if str(k).startswith(prefix)]
            except Exception:  # noqa: BLE001
                pass
        return [k for k in self.mem if str(k).startswith(prefix)]


def today() -> str:
    return dt.datetime.utcnow().strftime("%Y-%m-%d")


class Guard:
    """Pause switch, a daily US$ cap on the estimated container cost, and a per-visitor rate limit."""

    def __init__(self, store: Store):
        self.store = store
        self.cap_default = float(os.environ.get("RAGLAB_CAP_USD", "15"))
        self.hits = collections.defaultdict(collections.deque)
        self.lock = threading.Lock()

    def flags(self) -> dict:
        return {"enabled": True, "reason": "", "cap_usd": self.cap_default, **(self.store.get("flags") or {})}

    def set_flags(self, **kw):
        f = self.flags()
        f.update({k: v for k, v in kw.items() if v is not None})
        self.store.put("flags", f)
        return f

    def spent_usd(self) -> float:
        return round((self.store.get(f"spend:{today()}") or 0.0) * RATE_USD_S, 4)

    def add_seconds(self, s: float):
        k = f"spend:{today()}"
        self.store.put(k, (self.store.get(k) or 0.0) + s)

    def check(self, who: str):
        f = self.flags()
        if not f.get("enabled", True):
            raise HTTPException(503, f.get("reason") or "The lab is paused for a moment.")
        cap = f.get("cap_usd")
        if self.spent_usd() >= float(self.cap_default if cap is None else cap):
            raise HTTPException(503, "Today's cost cap is reached; the lab is resting. Ask the instructor.")
        now = time.time()
        with self.lock:
            q = self.hits[who]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= 90:
                raise HTTPException(429, "Too many searches in a minute: wait a few seconds.")
            q.append(now)


def _clean_name(s: str) -> str:
    s = re.sub(r"[^\w .'\-]", "", str(s or ""), flags=re.UNICODE).strip()
    return s[:40]


def create_app(engine: Engine | None = None, store: Store | None = None, heartbeat: bool = True) -> FastAPI:
    app = FastAPI(title="Northbridge RAG Lab", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("RAGLAB_DICT"))
    guard = Guard(store)
    state = {"engine": engine}
    elock = threading.Lock()
    admin_token = os.environ.get("RAGLAB_ADMIN_TOKEN", "")
    mapcache: dict = {}

    def eng() -> Engine:
        if state["engine"] is None:
            with elock:
                if state["engine"] is None:
                    state["engine"] = Engine(preload=[os.environ.get("RAGLAB_PRELOAD", "")] if os.environ.get("RAGLAB_PRELOAD") else None)
        return state["engine"]

    if heartbeat:  # the container's own running time, for the day's cost estimate (60 s ticks)
        def beat():
            while True:
                time.sleep(60)
                try:
                    guard.add_seconds(60)
                except Exception:  # noqa: BLE001
                    pass
        threading.Thread(target=beat, daemon=True).start()

    def who(req: Request) -> str:
        return req.headers.get("x-player") or (req.client.host if req.client else "anon")

    def need_admin(req: Request):
        tok = req.headers.get("x-admin") or req.query_params.get("token", "")
        if not admin_token or tok != admin_token:
            raise HTTPException(401, "admin token required")

    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
    if SKY.exists():
        app.mount("/sky", StaticFiles(directory=str(SKY)), name="sky")

    @app.get("/", response_class=HTMLResponse)
    def home():
        return FileResponse(STATIC / "lab.html")

    @app.get("/board", response_class=HTMLResponse)
    def board_page():
        return FileResponse(STATIC / "board.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return FileResponse(STATIC / "admin.html")

    @app.get("/healthz")
    def healthz():
        e = eng()
        return {"ok": True, "built": len(e.built()), "grid_rows": len(e.grid), "loaded": list(e.idx)}

    @app.get("/api/options")
    def options():
        e = eng()
        qs = [{"id": q["id"], "type": q["type"], "question": q["question"], "role": C.role_of(q)} for q in e.G.qs]
        return {"options": OPTIONS, "examples": [{"id": i, "question": q} for i, q in EXAMPLES], "files": SHOW_FILES,
                "golden": qs, "built": e.built(), "best": e.best, "budget_ms": BUDGET_S * 1000,
                "roles": {"PUR-EXEC": "Emma Clarke, purchase executive", "PUR-MGR": "Daniel Okafor, purchase manager",
                          "STORES": "Aiko Tanaka, stores", "HR-MGR": "an HR manager"},
                "grid_rows": len(e.grid), "flags": guard.flags()}

    @app.post("/api/metrics")
    async def metrics(req: Request):
        body = await req.json()
        cfg = cfg_from(body.get("config") or {})
        return {"config": cfg.to_json(), "metrics": eng().metrics(cfg)}

    @app.post("/api/search")
    async def search(req: Request):
        guard.check(who(req))
        body = await req.json()
        q = str(body.get("question") or "").strip()[:400]
        if not q:
            raise HTTPException(400, "Type a question.")
        cfg = cfg_from(body.get("config") or {})
        role = body.get("role") if body.get("role") in ("PUR-EXEC", "PUR-MGR", "STORES", "HR-MGR", "PUR-SR", "IT-ADMIN") else C.DEFAULT_ROLE
        e = eng()
        if cfg.chunking not in e.built():
            raise HTTPException(404, f"The index for {cfg.chunking} is not built yet.")
        import anyio

        t0 = time.perf_counter()
        res = await anyio.to_thread.run_sync(lambda: e.search(cfg, q, role))
        res["wall_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        res["config"] = cfg.to_json()
        res["metrics"] = e.metrics(cfg)
        return res

    @app.get("/api/chunks")
    async def chunks(config: str = "", file: str = ""):
        cfg = cfg_from(json.loads(config) if config else {})
        import anyio

        e = eng()
        if cfg.chunking not in e.built():
            raise HTTPException(404, "index not built")
        if file not in await anyio.to_thread.run_sync(lambda: e.files(cfg.chunking)):
            raise HTTPException(404, "unknown file")
        return await anyio.to_thread.run_sync(lambda: e.chunks_of(cfg.chunking, file))

    @app.get("/api/files")
    async def files(config: str = ""):
        cfg = cfg_from(json.loads(config) if config else {})
        import anyio

        return {"files": await anyio.to_thread.run_sync(lambda: eng().files(cfg.chunking))}

    @app.get("/api/map")
    async def vmap(config: str = ""):
        cfg = cfg_from(json.loads(config) if config else {})
        model = cfg.embed if cfg.retrieval != "bm25" else "bge-small"
        key = (cfg.chunking, model)
        if key not in mapcache:
            import anyio

            mapcache[key] = await anyio.to_thread.run_sync(lambda: eng().map_points(cfg.chunking, model))
            if len(mapcache) > 40:
                mapcache.pop(next(iter(mapcache)))
        return mapcache[key]

    # ------------------------------------------------------------------ the leaderboard
    @app.post("/api/leaderboard")
    async def submit(req: Request):
        guard.check(who(req))
        body = await req.json()
        name = _clean_name(body.get("name"))
        if not name:
            raise HTTPException(400, "Type your name first.")
        cfg = cfg_from(body.get("config") or {})
        sc = eng().leaderboard_score(cfg)
        if not sc:
            raise HTTPException(404, "No golden-set measurement for this setting.")
        pid = hashlib.sha1(name.lower().encode()).hexdigest()[:12]
        entry = {"name": name, "config": cfg.to_json(), **sc, "at": time.strftime("%H:%M:%S")}
        cur = store.get(f"lb:{pid}")
        better = (cur is None or (sc["under_budget"] and not cur.get("under_budget"))
                  or (sc["under_budget"] == cur.get("under_budget") and (sc["recall@5"], sc["mrr"]) > (cur["recall@5"], cur["mrr"])))
        hist = (cur or {}).get("tries", 0) + 1
        if better:
            store.put(f"lb:{pid}", {**entry, "tries": hist})
        else:
            cur["tries"] = hist
            store.put(f"lb:{pid}", cur)
        return {"saved": better, "entry": entry, "best": store.get(f"lb:{pid}")}

    @app.get("/api/leaderboard")
    def board():
        rows = [store.get(k) for k in store.keys("lb:")]
        rows = [r for r in rows if r]
        rows.sort(key=lambda r: (not r["under_budget"], -r["recall@5"], -r["mrr"], r["p95_ms"]))
        return {"budget_ms": BUDGET_S * 1000, "rows": rows[:100], "n": len(rows)}

    # ------------------------------------------------------------------ the best index, for rag_search() and NB3
    @app.get("/api/best_index.tar.gz")
    def best_index():
        p = pathlib.Path(os.environ.get("RAGLAB_VOL", "/vol")) / "best_index.tar.gz"
        if not p.exists():
            raise HTTPException(404, "not published yet")
        return FileResponse(p, media_type="application/gzip", filename="best_index.tar.gz")

    @app.get("/api/best")
    def best():
        return eng().best or {}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def status(req: Request):
        need_admin(req)
        e = eng()
        return {"flags": guard.flags(), "spent_usd_today": guard.spent_usd(), "rate_usd_per_hour": round(RATE_USD_S * 3600, 2),
                "leaderboard": len(store.keys("lb:")), "loaded_indexes": list(e.idx), "built": len(e.built())}

    @app.post("/api/admin/{cmd}")
    async def admin(cmd: str, req: Request):
        need_admin(req)
        body = {}
        try:
            body = await req.json()
        except Exception:  # noqa: BLE001
            pass
        if cmd == "pause":
            return guard.set_flags(enabled=False, reason=body.get("reason") or "The lab is paused for a moment.")
        if cmd == "resume":
            return guard.set_flags(enabled=True, reason="")
        if cmd == "cap":
            return guard.set_flags(cap_usd=float(body.get("cap_usd", guard.cap_default)))
        if cmd == "purge-all":
            ks = store.keys("lb:")
            for k in ks:
                store.delete(k)
            return {"removed": len(ks)}
        if cmd == "purge-name":
            pid = hashlib.sha1(_clean_name(body.get("name")).lower().encode()).hexdigest()[:12]
            had = store.get(f"lb:{pid}") is not None
            store.delete(f"lb:{pid}")
            return {"removed": int(had)}
        if cmd == "purge-tests":
            ks = [k for k in store.keys("lb:") if str((store.get(k) or {}).get("name", "")).lower().startswith(("load ", "e2e ", "test "))]
            for k in ks:
                store.delete(k)
            return {"removed": len(ks)}
        raise HTTPException(404, "unknown command")

    @app.exception_handler(HTTPException)
    async def _http(_, e: HTTPException):
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)

    app.state.guard, app.state.store = guard, store
    return app
