"""Lecture 5: the reference app. One process: the Bahi sandbox, the agent API, the approval inbox, the audit log.

    chat (browser) ──> /api/chat/{conv}/message ──> AuthorityAgent ──> GraphAgent (Lecture 4 control graph)
         ──> AuthorityTools (guardrails, preview/commit, read-back, audit) ──> intent tools over MCP (Lecture 3),
         the server bound to the signed-in user's own Bahi session ──> Bahi
    commit and approval ──> DurableIntentTools ──> the PurchaseOrder workflow (Lecture 7, Temporal)

Routes (Bahi's own routes from bahi.server are kept: /login, /svc/{name}, /legacy ...):
    GET  /app/chat  /app/inbox  /app/slack  /app/audit       the four pages
    GET  /api/me                                      who this token is, and what the role allows   (Bearer)
    POST /api/chat                                    start a conversation -> {"conv"}             (Bearer)
    POST /api/chat/{conv}/message  {"text"}           the agent's reply and the new trace lines     (Bearer = owner)
    GET  /api/chat/{conv}                             transcript, trace, what it waits on           (Bearer = owner)
    GET  /api/inbox                                   what waits for THIS user's signature          (Bearer)
    POST /api/inbox/{item}  {"decision","comment"}    one tap, done in this user's own Bahi session (Bearer = approver)
    GET  /api/audit?conv=                             the joined audit trail, and Bahi's raw rows   (Bearer)
    GET  /api/outbox?channel=@rohit                   the Slack-style messages (sandbox outbox)     (Bearer)

Environment: BAHI_MODEL (default gemini:gemini-3.8-flash), BAHI_LLM_MODE (auto | replay ...),
BAHI_APP_DURABLE (1 = commit path as a Temporal workflow; default 1), BAHI_APP_MCP (1 = tools over MCP; default 1).
"""
from __future__ import annotations

import os
import pathlib
import threading

from fastapi import Body, Header, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from ..agent.authority import ApprovalInbox, AuditLog, AuthorityAgent, Notifier, passthrough, scopes
from ..erp.engine import ERP
from ..llm import LLM
from ..server import create_app as create_bahi_app

STATIC = pathlib.Path(__file__).parent / "static"
PAGES = {"chat": "chat.html", "inbox": "inbox.html", "slack": "slack.html", "audit": "audit.html"}


class AppState:
    def __init__(self, erp: ERP, model: str, cassette: str, durable: bool, mcp: bool):
        self.erp, self.model, self.cassette, self.use_durable, self.mcp = erp, model, cassette, durable, mcp
        self.audit = AuditLog(erp)
        self.notifier = Notifier(use_mcp=mcp)
        self.durable = None
        if durable:
            from ..durable.runtime import DurableBahi, quiet_logs
            quiet_logs()
            self.durable = DurableBahi(erp)
        self.inbox = ApprovalInbox(erp, self.notifier, self.audit, durable=self.durable)
        self.convs: dict[str, dict] = {}
        self.lock = threading.RLock()

    def close(self):
        for c in self.convs.values():
            t = c["agent"].tools.inner
            for x in (t, getattr(t, "d", None)):
                inner = getattr(getattr(x, "tools", None), "close", None) or getattr(x, "close", None)
                if inner:
                    try:
                        inner()
                    except Exception:  # noqa: BLE001
                        pass
        self.notifier.close()
        if self.durable:
            self.durable.close()


def create_app(model: str | None = None, cassette: str = "L5_app", durable: bool | None = None,
               mcp: bool | None = None, erp: ERP | None = None):
    app = create_bahi_app()
    app.title = "Bahi reference app (Lecture 5)"
    erp = app.state.tenants.setdefault("default", erp or ERP())
    env = lambda k, d: os.environ.get(k, d) not in ("0", "false", "no")  # noqa: E731
    S = AppState(erp, model or os.environ.get("BAHI_MODEL", "gemini:gemini-3.8-flash"), cassette,
                 env("BAHI_APP_DURABLE", "1") if durable is None else durable,
                 env("BAHI_APP_MCP", "1") if mcp is None else mcp)
    app.state.l5 = S

    def who(auth: str | None) -> tuple[str, str]:
        tok = (auth or "").removeprefix("Bearer ").strip()
        if tok not in erp.sessions:
            raise HTTPException(401, "ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
        return erp.sessions[tok], tok

    def conv_of(conv: str, user: str) -> dict:
        c = S.convs.get(conv)
        if not c:
            raise HTTPException(404, "no such conversation")
        if c["owner"] != user:
            raise HTTPException(403, "this conversation belongs to someone else")
        return c

    # ------------------------------------------------------------------ pages
    @app.get("/app")
    def app_root():
        return RedirectResponse("/app/chat")

    @app.get("/app/static/{name}")
    def static(name: str):
        p = (STATIC / name).resolve()
        if p.parent != STATIC.resolve() or not p.exists():
            raise HTTPException(404, "not found")
        return FileResponse(p)

    @app.get("/app/{page}")
    def page(page: str):
        if page not in PAGES:
            raise HTTPException(404, "not found")
        return FileResponse(STATIC / PAGES[page])

    # ------------------------------------------------------------------ the agent API
    @app.get("/api/me")
    def me(authorization: str | None = Header(None)):
        user, _ = who(authorization)
        sc = scopes(erp, user)
        return {"user": user, "name": sc["name"], "role": sc["role"], "limit": sc["limit"],
                "tools": [t["tool"] for t in sc["tools"] if t["allowed"]],
                "menu": [m for m in sc["menu"]], "slack": {"KJOSHI": "@kavita", "RMEHTA": "@rohit"}.get(user)}

    @app.post("/api/chat")
    def new_chat(authorization: str | None = Header(None)):
        user, tok = who(authorization)
        with S.lock:
            n = sum(1 for c in S.convs.values() if c["owner"] == user) + 1
            conv = f"{user.lower()}-{n}"
            ident = passthrough(erp, token=tok)  # the agent acts as the person who signed in, nobody else
            ag = AuthorityAgent(erp, user, llm=LLM(S.model, cassette=S.cassette), identity=ident, inbox=S.inbox,
                                audit=S.audit, durable=S.durable, mcp=S.mcp, conv=conv)
            S.convs[conv] = {"owner": user, "agent": ag}
        return {"conv": conv, "acts_as": ident.as_dict()}

    @app.post("/api/chat/{conv}/message")
    def message(conv: str, b: dict = Body(...), authorization: str | None = Header(None)):
        # a plain def: FastAPI runs it on a worker thread, so a slow model call never blocks other requests
        user, _ = who(authorization)
        text = str(b.get("text", "")).strip()
        if not text:
            raise HTTPException(400, "empty message")
        c = conv_of(conv, user)
        with S.lock:
            n0 = len(c["agent"].trace())
            reply = c["agent"].respond(text)
            tr = c["agent"].trace()
        return {"reply": reply, "trace": tr[n0:], "waiting_on": _waiting(c["agent"])}

    @app.get("/api/chat/{conv}")
    def chat_state(conv: str, authorization: str | None = Header(None)):
        user, _ = who(authorization)
        c = conv_of(conv, user)
        ag = c["agent"]
        return {"conv": conv, "transcript": ag.transcript, "trace": ag.trace(), "waiting_on": _waiting(ag),
                "acts_as": ag.identity.as_dict(), "llm": ag.llm.totals() if hasattr(ag.llm, "totals") else None}

    def _waiting(ag) -> dict | None:
        it = ag.waiting_on()
        return {k: it[k] for k in ("id", "kind", "doc_no", "status", "approver")} if it else None

    # ------------------------------------------------------------------ the inbox
    @app.get("/api/inbox")
    def inbox(authorization: str | None = Header(None)):
        user, _ = who(authorization)
        with S.lock:
            items = S.inbox.pending(erp.session(user))  # read in HIS session
        return {"user": user, "items": items}

    @app.post("/api/inbox/{item_id}")
    def decide(item_id: str, b: dict = Body(...), authorization: str | None = Header(None)):
        user, tok = who(authorization)
        if item_id not in S.inbox.items:
            raise HTTPException(404, "no such item")
        with S.lock:
            res = S.inbox.decide(item_id, passthrough(erp, token=tok).session, b.get("decision", "approve"),
                                 b.get("comment", ""))
            if not res["ok"]:
                raise HTTPException(403, res["error"])
            it = S.inbox.get(item_id)
            follow = None
            c = S.convs.get(it.get("conv") or "")
            if c:  # the conversation that waits on this item carries on; it reads Bahi, not this message
                follow = {"conv": it["conv"], "reply": c["agent"].after_decision(it)}
        return {"result": res, "conversation": follow}

    # ------------------------------------------------------------------ proof
    @app.get("/api/audit")
    def audit(conv: str | None = None, authorization: str | None = Header(None)):
        who(authorization)
        return {"conv": conv, "entries": S.audit.joined(conv), "summary": S.audit.summary(conv),
                "bahi_rows": S.audit.bahi_rows()}

    @app.get("/api/outbox")
    def outbox(channel: str | None = None, authorization: str | None = Header(None)):
        who(authorization)
        ms = S.notifier.messages()
        return {"via": S.notifier.via, "messages": [m for m in ms if not channel or m.get("channel") == channel]}

    return app


def main():
    import argparse

    import uvicorn

    ap = argparse.ArgumentParser(prog="python -m bahi.app")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8090)
    a = ap.parse_args()
    print(f"Bahi reference app: http://{a.host}:{a.port}/app/chat (Kavita: KJOSHI / kavita@123) · "
          f"/app/inbox and /app/slack (Rohit: RMEHTA / rohit@123) · /app/audit")
    uvicorn.run(create_app(), host=a.host, port=a.port, log_level="warning")
