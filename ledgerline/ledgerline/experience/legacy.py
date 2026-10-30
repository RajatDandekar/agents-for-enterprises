"""The legacy Ledgerline client inside the Experience, one Northbridge per player.

Same wire contract as ledgerline.server (POST /login, POST /svc/{name}, GET /screens, GET /live-run, POST /logout), so
the unchanged legacy client (ledgerline/legacy_ui/index.html) works against it. Mounted under /ledgerline:

    /ledgerline/legacy?tenant=<player id>      the Windows-2000 client; X-Tenant = the player id picks the player's Northbridge

Differences from ledgerline.server: the tenant must be a known player (no anonymous sandboxes), every call runs under the
player's ERP lock, and the screens include the Experience's PUR-POM-06 (order amendment, so a Draft can be fixed).
"""
from __future__ import annotations

import pathlib

import yaml
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse

from ..erp.engine import LedgerlineError, ServiceTimeout
from ..server import load_screens

HERE = pathlib.Path(__file__).parent
LEGACY_HTML = HERE.parent / "legacy_ui" / "index.html"


def screens() -> dict:
    out = load_screens()
    for p in sorted((HERE / "screens").glob("*.yaml")):
        out.setdefault(p.stem, yaml.safe_load(p.read_text()))
    return out


def make_legacy_router(players, known) -> APIRouter:
    """known(pid) -> bool: is this a player of the Experience (restores them after a restart)."""
    r = APIRouter(prefix="/ledgerline")
    SCREENS = screens()

    def erp_for(tenant: str | None):
        if not tenant or not known(tenant):
            raise HTTPException(404, "ERR-SYS-0404 UNKNOWN PLAYER. OPEN THE EXPERIENCE FROM ITS HOME PAGE.")
        return players.erp(tenant)

    def user_for(erp, auth):
        tok = (auth or "").removeprefix("Bearer ").strip()
        if tok not in erp.sessions:
            raise HTTPException(401, "ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
        return erp.sessions[tok]

    @r.get("/legacy")
    def legacy():
        return FileResponse(LEGACY_HTML, headers={"Cache-Control": "no-store"})

    @r.get("/screens")
    def get_screens():
        return SCREENS

    @r.get("/screens/{code}")
    def get_screen(code: str):
        sc = SCREENS.get(code.upper())
        if not sc:
            raise HTTPException(404, "SCREEN NOT FOUND")
        return sc

    @r.post("/login")
    async def login(req: Request, x_tenant: str | None = Header(None)):
        try:
            body = await req.json()
        except Exception:  # noqa: BLE001
            body = {}
        erp = erp_for(x_tenant)
        with erp.lock:
            try:
                tok = erp.login(str(body.get("user_id", "")), str(body.get("password", "")))
            except LedgerlineError as e:
                return JSONResponse({"rc": "E", "err_cd": e.err_cd, "msg": e.msg}, status_code=401)
            u = erp.user(erp.sessions[tok])
            ou = str(body.get("ou_cd") or u["ou_cd"]).upper()
            if ou != u["ou_cd"]:
                erp.sessions.pop(tok, None)
                return JSONResponse({"rc": "E", "err_cd": "ERR-SEC-0007", "msg": f"USER NOT MAPPED TO ORG UNIT {ou}"},
                                    status_code=401)
            erp.call("usr_get", {"user_id": u["user_id"]}, user=u["user_id"], screen="SYS-LGN-01", task="Sign in")
        return {"rc": "S", "token": tok, "user_id": u["user_id"], "name": u["name"], "role_cd": u["role_cd"],
                "ou_cd": u["ou_cd"], "msg": f"WELCOME, {u['user_id']}. LAST SIGN-IN 24-10-2026 18:02"}

    @r.post("/logout")
    def logout(authorization: str | None = Header(None), x_tenant: str | None = Header(None)):
        erp = erp_for(x_tenant)
        with erp.lock:
            erp.sessions.pop((authorization or "").removeprefix("Bearer ").strip(), None)
        return {"rc": "S", "msg": "SIGNED OUT"}

    @r.post("/svc/{name}")
    async def svc(name: str, req: Request, authorization: str | None = Header(None),
                  x_tenant: str | None = Header(None), x_screen: str | None = Header(None),
                  x_task: str | None = Header(None)):
        erp = erp_for(x_tenant)
        user = user_for(erp, authorization)
        try:
            payload = await req.json()
        except Exception:  # noqa: BLE001
            payload = {}
        if not isinstance(payload, dict):
            return JSONResponse({"rc": "E", "err_cd": "ERR-SYS-0422", "msg": "PAYLOAD MUST BE A FLAT OBJECT"}, 422)
        try:
            return erp.call(name, payload or {}, user=user, screen=x_screen, task=x_task)
        except ServiceTimeout as e:
            return JSONResponse({"rc": "E", "err_cd": "HTTP-504", "msg": str(e)}, status_code=504)

    @r.get("/live-run")
    def live_run(since: int = 0, x_tenant: str | None = Header(None)):
        erp = erp_for(x_tenant)
        with erp.lock:
            return erp.live_run(since)

    return r
