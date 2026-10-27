"""The deployable Bahi sandbox + agent API (Lecture 7). One process, one container.

    uvicorn deploy.app:app --host 0.0.0.0 --port 8080        (inside the container; see Dockerfile)

Routes (the Bahi routes from bahi.server are kept as they are: /login, /svc/{name}, /legacy, ...):
    GET  /healthz                       liveness: the process answers
    GET  /readyz                        readiness: Bahi answers a read, Temporal answers, the worker is running
    GET  /version                       the pinned versions this build runs (versions.yaml + live hashes)
    POST /agent/{conv}/message          {"text": "..."} -> the agent's reply   (Bearer = the user's Bahi token)
    POST /orders                        start the PurchaseOrder workflow for a confirmed order (Bearer = requester)
    GET  /orders/{wid}                  the workflow's status (stage, request, PO, reminders, diary)
    POST /orders/{wid}/approve          {"decision": "A"|"R", "comment": ""}  (Bearer = the APPROVER's own token)
    GET  /flags   POST /flags           kill switch and rollout stage            (X-Admin-Token)

Environment (deploy/env/<env>.env; secrets come from the platform's secret store, never from the image):
    BAHI_ENV            dev | staging | prod
    BAHI_TEMPORAL       time_skipping (dev, tests) | local (dev server) | connect (TEMPORAL_ADDRESS, staging/prod)
    BAHI_FLAGS_FILE     where the kill switch lives (a mounted volume in staging/prod)
    BAHI_MODEL          the pinned model id for this environment (must match versions.yaml)
    BAHI_ADMIN_TOKEN    secret: who may flip the kill switch
    GEMINI_API_KEY      secret

SANDBOX SIMPLIFICATION: the ERP is the in-memory sandbox, so the Temporal worker runs inside this process and
shares its ERP. Against a real Bahi, the worker is its own deployment (same image, CMD = the worker) and reaches
Bahi over HTTP; nothing else changes.
"""
from __future__ import annotations

import os
import pathlib

import yaml
from fastapi import Header, HTTPException, Request

from bahi.durable.killswitch import STAGES, Flags
from bahi.durable.model import OrderRequest
from bahi.erp.engine import ERP
from bahi.server import create_app

HERE = pathlib.Path(__file__).parent
ENV = os.environ.get("BAHI_ENV", "dev")
VERSIONS = yaml.safe_load((HERE / "versions.yaml").read_text())

app = create_app()
app.title = f"Bahi ERP sandbox + agent API ({ENV})"
# The flags file is created on first start with this environment's rollout stage; after that the operator owns it.
flags = Flags(os.environ.get("BAHI_FLAGS_FILE") or None, stage=VERSIONS["environments"][ENV]["stage"])
STATE: dict = {"durable": None, "agents": {}}


def _erp() -> ERP:
    return app.state.tenants.setdefault("default", ERP())


def _user(auth: str | None) -> str:
    tok = (auth or "").removeprefix("Bearer ").strip()
    erp = _erp()
    if tok not in erp.sessions:
        raise HTTPException(401, "ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
    return erp.sessions[tok]


def _durable():
    if STATE["durable"] is None:
        from bahi.durable.runtime import DurableBahi

        STATE["durable"] = DurableBahi(_erp(), kind=os.environ.get("BAHI_TEMPORAL", "time_skipping"), flags=flags,
                                       identity=f"bahi-{ENV}-{os.environ.get('HOSTNAME', 'local')}")
    return STATE["durable"]


def _admin(tok: str | None):
    want = os.environ.get("BAHI_ADMIN_TOKEN")
    if not want or tok != want:
        raise HTTPException(403, "admin token required")


@app.get("/healthz")
def healthz():
    return {"ok": True, "env": ENV}


@app.get("/readyz")
def readyz():
    erp = _erp()
    r = erp.call("cc_get", {"cc_cd": "PRD-07"}, user="KJOSHI")
    d = _durable()
    return {"ok": r["rc"] == "S" and not d._task.done(), "bahi": r["rc"], "worker_running": not d._task.done(),
            "writes_enabled": flags.writes_enabled(), "stage": flags.read()["stage"]}


@app.get("/version")
def version():
    from deploy.versions import current

    return {"env": ENV, "pinned": VERSIONS, "running": current()}


@app.post("/orders")
async def start_order(req: Request, authorization: str | None = Header(None)):
    user = _user(authorization)
    b = await req.json()
    o = OrderRequest(user, b["supplier_code"], b["item_code"], int(b["quantity"]), b["cost_centre"], b["need_by"],
                     b.get("rate"), ref=str(b.get("ref", "")))
    d = _durable()
    wid = d.start(o)
    return {"workflow_id": wid, **d.wait_for(wid, ("waiting for approval", "released", "needs a person", "failed",
                                                   "paused"), timeout_s=30)}


@app.get("/orders/{wid}")
def order_status(wid: str):
    return _durable().status(wid)


@app.post("/orders/{wid}/approve")
async def approve(wid: str, req: Request, authorization: str | None = Header(None)):
    """The approver approves with HIS OWN Bahi session: Bahi checks his limit and that he is not the requester."""
    by = _user(authorization)
    b = await req.json()
    d = _durable()
    r = d.approve(wid, by=by, decision=b.get("decision", "A"), comment=b.get("comment", ""))
    if r["rc"] == "E":
        raise HTTPException(403, f"{r['err_cd']} {r['msg']}")
    return {"bahi": r, "workflow": d.status(wid)}


@app.post("/agent/{conv}/message")
async def agent_message(conv: str, req: Request, authorization: str | None = Header(None)):
    from bahi.agent.loop import ToolLoopAgent
    from bahi.agent.tools import IntentTools
    from bahi.durable.agent_tools import DurableIntentTools
    from bahi.llm import LLM

    user = _user(authorization)
    b = await req.json()
    key = (user, conv)
    if key not in STATE["agents"]:
        erp = _erp()
        tools = DurableIntentTools(IntentTools(erp.session(user)), _durable(), flags)
        llm = LLM(os.environ.get("BAHI_MODEL", VERSIONS["environments"][ENV]["model"]), cassette=f"deploy_{ENV}")
        STATE["agents"][key] = ToolLoopAgent(erp, user, llm=llm, tools=tools)
    ag = STATE["agents"][key]
    return {"reply": ag.respond(b["text"]), "llm": ag.llm.totals()}


@app.get("/flags")
def get_flags():
    return flags.read()


@app.post("/flags")
async def set_flags(req: Request, x_admin_token: str | None = Header(None)):
    _admin(x_admin_token)
    b = await req.json()
    if b.get("kill"):
        return flags.kill(b.get("reason", "switched off by operator"))
    if b.get("revive"):
        return flags.revive()
    kw = {k: b[k] for k in ("stage", "cohort") if k in b}
    if "stage" in kw and kw["stage"] not in STAGES:
        raise HTTPException(400, f"stage must be one of {STAGES}")
    return flags.set(**kw)
