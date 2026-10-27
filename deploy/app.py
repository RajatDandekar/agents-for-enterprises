"""The deployable Bahi reference app (Lecture 7 deploy of the Lecture 5 app). One process, one container.

    uvicorn deploy.app:app --host 0.0.0.0 --port 8080        (inside the container; see Dockerfile)

What it serves: bahi.app.main.create_app(), the full reference app: the chat, the approval inbox, the Slack-style
outbox and the audit pages (/app/...), the agent API (/api/...), and Bahi's own routes (/login, /svc/{name}, /legacy).
The commit path runs as the Lecture 7 PurchaseOrder workflow (BAHI_APP_DURABLE=1).

Added here for running it in public:
    GET  /healthz                       liveness: the process answers
    GET  /readyz                        readiness: Bahi answers a read, the Temporal worker is running
    GET  /version                       the pinned versions this build runs (versions.yaml + live hashes)
    GET  /flags   POST /flags           kill switches and rollout stage (POST needs X-Admin-Token)
    GET  /spend                         today's model spend against the daily cap, and the rate limits
    POST /orders, GET /orders/{wid}, POST /orders/{wid}/approve   the workflow directly (for smoke tests and L8)
  and in front of everything:
    /admin/*                            Bahi's sandbox reset and fault injection: admin token only
    model calls                         refused (HTTP 429/503, nothing half-done) when the model kill switch is on,
                                        when today's spend has reached BAHI_DAILY_CAP_INR, or above the rate limits

Environment (deploy/env/<env>.env; secrets come from the platform's secret store, never from the image):
    BAHI_ENV            dev | staging | prod
    BAHI_TEMPORAL       time_skipping (tests) | local (in-process dev server, real timers) | connect (TEMPORAL_ADDRESS)
    BAHI_FLAGS_FILE     where the kill switches live (a mounted volume in staging/prod)
    BAHI_STATE_DIR      where the spend ledger lives (same volume)
    BAHI_MODEL, BAHI_LLM_MODE   the pinned model; live in staging
    BAHI_DAILY_CAP_INR, BAHI_RATE_GLOBAL_PER_MIN, BAHI_RATE_USER_PER_MIN
    BAHI_ADMIN_TOKEN    secret: who may flip the switches
    GEMINI_API_KEY      secret

SANDBOX SIMPLIFICATION: the ERP is the in-memory sandbox, so the Temporal worker runs inside this process and shares
its ERP. Against a real Bahi, the worker is its own deployment and reaches Bahi over HTTP; nothing else changes.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import threading
import time
from collections import deque

import yaml
from fastapi import Header, HTTPException, Request
from fastapi.responses import JSONResponse

from bahi.durable.killswitch import STAGES, Flags
from bahi.durable.model import OrderRequest
from bahi.llm import LLM

HERE = pathlib.Path(__file__).parent
ENV = os.environ.get("BAHI_ENV", "dev")
VERSIONS = yaml.safe_load((HERE / "versions.yaml").read_text())
STATE_DIR = pathlib.Path(os.environ.get("BAHI_STATE_DIR") or "/tmp/bahi-state")
STATE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("BAHI_MODEL", VERSIONS["environments"][ENV]["model"])

# The flags file is created on first start with this environment's rollout stage; after that the operator owns it.
# The workflow's activities build their own Flags() from the same BAHI_FLAGS_FILE, so one switch stops both.
flags = Flags(os.environ.get("BAHI_FLAGS_FILE") or None, stage=VERSIONS["environments"][ENV]["stage"],
              model_enabled=True)


# ------------------------------------------------------------------ the model guard: spend cap + rate limits
class SpendCapReached(Exception):
    pass


class ModelGuard:
    """Counts the estimated ₹ of every model call (bahi.llm prices) per IST day, and refuses calls past the cap."""

    def __init__(self):
        self.cap = float(os.environ.get("BAHI_DAILY_CAP_INR", "250"))
        self.g_per_min = int(os.environ.get("BAHI_RATE_GLOBAL_PER_MIN", "20"))
        self.u_per_min = int(os.environ.get("BAHI_RATE_USER_PER_MIN", "6"))
        self.path = STATE_DIR / "spend.json"
        self.lock = threading.Lock()
        self.hits: dict[str, deque] = {}
        try:
            self.ledger = json.loads(self.path.read_text())
        except (OSError, ValueError):
            self.ledger = {}

    @staticmethod
    def today() -> str:
        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def spent(self) -> dict:
        return self.ledger.get(self.today(), {"inr": 0.0, "calls": 0, "tokens_in": 0, "tokens_out": 0})

    def check(self):
        f = flags.read()
        if not f.get("model_enabled", True):
            raise HTTPException(503, f"The assistant is switched off by the operators: {f.get('reason') or 'model off'}")
        if self.spent()["inr"] >= self.cap:
            raise SpendCapReached(f"Today's model budget (₹{self.cap:,.0f}) is used up. Try again tomorrow (IST).")

    def add(self, r):
        with self.lock:
            d = self.ledger.setdefault(self.today(), {"inr": 0.0, "calls": 0, "tokens_in": 0, "tokens_out": 0})
            d["inr"] = round(d["inr"] + r.cost_inr, 4)
            d["calls"] += 1
            d["tokens_in"] += r.tokens_in
            d["tokens_out"] += r.tokens_out
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.ledger))
            tmp.replace(self.path)

    def rate(self, who: str):
        now = time.monotonic()
        with self.lock:
            for k, lim in (("*", self.g_per_min), (who, self.u_per_min)):
                q = self.hits.setdefault(k, deque())
                while q and now - q[0] > 60:
                    q.popleft()
                if len(q) >= lim:
                    raise HTTPException(429, f"Too many requests ({lim} a minute{' for this user' if k != '*' else ''}). "
                                             "Wait a minute.")
            for k in ("*", who):
                self.hits[k].append(now)


GUARD = ModelGuard()
_chat = LLM.chat


def _guarded_chat(self, *a, **kw):
    """Every model call in this process passes the guard: switched off or over the cap -> refused before calling."""
    GUARD.check()
    r = _chat(self, *a, **kw)
    if not getattr(r, "replayed", False):
        GUARD.add(r)
    return r


LLM.chat = _guarded_chat  # runtime wrap, in this process only; bahi/llm.py itself is unchanged

# ------------------------------------------------------------------ the app
from bahi.app.main import create_app  # noqa: E402  (after the wrap, so every agent the app builds is guarded)

app = create_app(model=os.environ["BAHI_MODEL"], cassette=f"deploy_{ENV}")
app.title = f"Bahi reference app ({ENV})"
S = app.state.l5
if S.durable:  # one switch for everything: the workflow's activities read the same flags as /flags writes
    S.durable.acts.flags = flags


def _erp():
    return S.erp


def _user(auth: str | None) -> str:
    tok = (auth or "").removeprefix("Bearer ").strip()
    if tok not in S.erp.sessions:
        raise HTTPException(401, "ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
    return S.erp.sessions[tok]


def _admin(tok: str | None):
    want = os.environ.get("BAHI_ADMIN_TOKEN")
    if not want or tok != want:
        raise HTTPException(403, "admin token required")


MODEL_ROUTES = ("/api/chat", "/api/inbox/")  # POSTs here can call the model (a decision wakes the waiting agent)


@app.middleware("http")
async def gatekeeper(request: Request, call_next):
    path = request.url.path
    try:
        if path.startswith("/admin/"):
            _admin(request.headers.get("x-admin-token"))
        if request.method == "POST" and path.startswith(MODEL_ROUTES):
            tok = (request.headers.get("authorization") or "").removeprefix("Bearer ").strip()
            GUARD.check()
            GUARD.rate(S.erp.sessions.get(tok, request.client.host if request.client else "anon"))
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse({"detail": e.detail}, status_code=e.status_code)
    except SpendCapReached as e:
        return JSONResponse({"detail": str(e)}, status_code=429)


@app.exception_handler(SpendCapReached)
async def _cap(_, e):
    return JSONResponse({"detail": str(e)}, status_code=429)


@app.get("/healthz")
def healthz():
    return {"ok": True, "env": ENV}


@app.get("/readyz")
def readyz():
    r = S.erp.call("cc_get", {"cc_cd": "PRD-07"}, user="KJOSHI")
    d = S.durable
    running = bool(d) and not d._task.done()
    f = flags.read()
    return {"ok": r["rc"] == "S" and running, "bahi": r["rc"], "worker_running": running,
            "temporal": os.environ.get("BAHI_TEMPORAL", "time_skipping"), "writes_enabled": f["writes_enabled"],
            "model_enabled": f.get("model_enabled", True), "stage": f["stage"]}


@app.get("/version")
def version():
    from deploy.versions import current

    return {"env": ENV, "pinned": VERSIONS, "running": current()}


@app.get("/spend")
def spend():
    return {"day_ist": GUARD.today(), **GUARD.spent(), "cap_inr": GUARD.cap, "rate_global_per_min": GUARD.g_per_min,
            "rate_user_per_min": GUARD.u_per_min, "model": os.environ["BAHI_MODEL"],
            "note": "₹ estimated from bahi.llm PRICES (list prices), not the provider's invoice"}


@app.post("/orders")
async def start_order(req: Request, authorization: str | None = Header(None)):
    user = _user(authorization)
    b = await req.json()
    o = OrderRequest(user, b["supplier_code"], b["item_code"], int(b["quantity"]), b["cost_centre"], b["need_by"],
                     b.get("rate"), ref=str(b.get("ref", "")))
    wid = S.durable.start(o)
    return {"workflow_id": wid, **S.durable.wait_for(wid, ("waiting for approval", "released", "needs a person",
                                                           "failed", "paused"), timeout_s=30)}


@app.get("/orders/{wid}")
def order_status(wid: str):
    return S.durable.status(wid)


@app.post("/orders/{wid}/approve")
async def approve(wid: str, req: Request, authorization: str | None = Header(None)):
    """The approver approves with HIS OWN Bahi session: Bahi checks his limit and that he is not the requester."""
    by = _user(authorization)
    b = await req.json()
    r = S.durable.approve(wid, by=by, decision=b.get("decision", "A"), comment=b.get("comment", ""))
    if r["rc"] == "E":
        raise HTTPException(403, f"{r['err_cd']} {r['msg']}")
    return {"bahi": r, "workflow": S.durable.status(wid)}


@app.get("/flags")
def get_flags():
    return flags.read()


@app.post("/flags")
async def set_flags(req: Request, x_admin_token: str | None = Header(None)):
    """{"kill": true, "reason": ...} stops every write · {"revive": true} · {"model": false} switches the assistant off
    · {"stage": "assist"} · {"cohort": [...]}"""
    _admin(x_admin_token)
    b = await req.json()
    if b.get("kill"):
        return flags.kill(b.get("reason", "switched off by operator"))
    if b.get("revive"):
        return flags.revive()
    if "model" in b:
        return flags.set(model_enabled=bool(b["model"]), reason=b.get("reason", ""))
    kw = {k: b[k] for k in ("stage", "cohort") if k in b}
    if "stage" in kw and kw["stage"] not in STAGES:
        raise HTTPException(400, f"stage must be one of {STAGES}")
    return flags.set(**kw)
