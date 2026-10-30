"""Ledgerline over HTTP, the way the legacy client (and n8n, and any other system) reaches it.

    POST /login                {"user_id": "ECLARKE", "password": "emma@123", "ou_cd": "NBC-MAN-01"} -> {"token": ...}
    POST /svc/{name}           Bearer token; body = the flat payload -> the legacy envelope {rc, err_cd, msg, data}
                               Optional headers X-Screen and X-Task say which screen and button made the call,
                               so a live run of the legacy client can be read back (Lecture 1) and turned into
                               tools (Lecture 3). HTTP 504 when a fault makes the reply get lost after the work is done.
    GET  /services             the service catalogue (names, fields, terse docs)
    GET  /screens[/{code}]     screen definitions (erp/screens/*.yaml)
    GET  /live-run?since=N     every service call since call N, with the screen, task and stored procedures
    POST /admin/reset          fresh seed data;  POST /admin/fault {"svc": "po_save", "mode": "timeout_after_commit"}
    GET  /legacy               the legacy Windows-style client (Ledgerline ERP 7.2)

Each tenant (header X-Tenant, default "default") gets its own sandbox, so a class can share one server.

    python -m ledgerline.server              # serve on http://127.0.0.1:8077 (legacy client at /legacy)
    python -m ledgerline.server --port 9000 --host 0.0.0.0
    python -m ledgerline.server --modules hr_leave        # purchasing plus a capstone module, its screens in the client

In a notebook:  from ledgerline.server import serve;  url = serve()   (starts in a background thread)
"""
from __future__ import annotations

import argparse
import pathlib
import threading

import yaml
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from .erp.engine import ERP, SERVICES, LedgerlineError, ServiceTimeout

HERE = pathlib.Path(__file__).parent
SCREENS_DIR = HERE / "erp" / "screens"


def load_screens(modules=()) -> dict:
    """Every screen definition, keyed by screen code (SYS-LGN-01, PUR-PO-01 ...), plus the screens of any
    installed capstone modules (ledgerline/modules/<name>/screens/*.yaml). Format: modules/README.md."""
    paths = sorted(SCREENS_DIR.glob("*.yaml"))
    for m in modules or ():
        paths += sorted((HERE / "modules" / m / "screens").glob("*.yaml"))
    return {p.stem: yaml.safe_load(p.read_text()) for p in paths}


def create_app(erp_factory=ERP) -> FastAPI:
    app = FastAPI(title="Ledgerline ERP 7.2 (sandbox)")
    tenants: dict[str, ERP] = {}
    app.state.tenants = tenants

    def erp_for(tenant: str | None) -> ERP:
        t = tenant or "default"
        if t not in tenants:
            tenants[t] = erp_factory()
        return tenants[t]

    def user_for(erp: ERP, auth: str | None) -> str:
        tok = (auth or "").removeprefix("Bearer ").strip()
        if tok not in erp.sessions:
            raise HTTPException(401, "ERR-SEC-0010 SESSION EXPIRED, SIGN IN AGAIN")
        return erp.sessions[tok]

    @app.post("/login")
    async def login(req: Request, x_tenant: str | None = Header(None)):
        try:
            body = await req.json()
        except Exception:
            body = {}
        erp = erp_for(x_tenant)
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
        # The client loads the user's profile right after signing in. Recording it under the sign-in screen
        # makes every sign-in visible in the live run.
        erp.call("usr_get", {"user_id": u["user_id"]}, user=u["user_id"], screen="SYS-LGN-01", task="Sign in")
        return {"rc": "S", "token": tok, "user_id": u["user_id"], "name": u["name"], "role_cd": u["role_cd"],
                "ou_cd": u["ou_cd"], "msg": f"WELCOME, {u['user_id']}. LAST SIGN-IN 24-10-2026 18:02"}

    @app.post("/logout")
    async def logout(authorization: str | None = Header(None), x_tenant: str | None = Header(None)):
        erp_for(x_tenant).sessions.pop((authorization or "").removeprefix("Bearer ").strip(), None)
        return {"rc": "S", "msg": "SIGNED OUT"}

    @app.post("/svc/{name}")
    async def svc(name: str, req: Request, authorization: str | None = Header(None),
                  x_tenant: str | None = Header(None), x_screen: str | None = Header(None),
                  x_task: str | None = Header(None)):
        erp = erp_for(x_tenant)
        user = user_for(erp, authorization)
        try:
            payload = await req.json()
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            return JSONResponse({"rc": "E", "err_cd": "ERR-SYS-0422", "msg": "PAYLOAD MUST BE A FLAT OBJECT"}, 422)
        try:
            return erp.call(name, payload or {}, user=user, screen=x_screen, task=x_task)
        except ServiceTimeout as e:
            return JSONResponse({"rc": "E", "err_cd": "HTTP-504", "msg": str(e)}, status_code=504)

    @app.get("/services")
    def services():
        return [{"name": s.name, "doc": s.doc, "kind": s.kind, "screen": s.screen,
                 "fields": [f.__dict__ for f in s.fields]} for s in SERVICES.values()]

    @app.get("/screens")
    def screens(x_tenant: str | None = Header(None)):
        return load_screens(erp_for(x_tenant).modules)

    @app.get("/screens/{code}")
    def screen(code: str, x_tenant: str | None = Header(None)):
        sc = load_screens(erp_for(x_tenant).modules).get(code.upper())
        if not sc:
            raise HTTPException(404, "SCREEN NOT FOUND")
        return sc

    @app.get("/live-run")
    def live_run(since: int = 0, x_tenant: str | None = Header(None)):
        return erp_for(x_tenant).live_run(since)

    @app.post("/admin/reset")
    def reset(x_tenant: str | None = Header(None)):
        tenants[x_tenant or "default"] = erp_factory()
        return {"rc": "S", "msg": "SANDBOX RESET"}

    @app.post("/admin/fault")
    async def fault(req: Request, x_tenant: str | None = Header(None)):
        b = await req.json()
        erp_for(x_tenant).inject(b["svc"], b.get("mode", "timeout_after_commit"), int(b.get("times", 1)))
        return {"rc": "S", "msg": f"FAULT SET ON {b['svc']}"}

    @app.get("/legacy")
    def legacy():
        return FileResponse(HERE / "legacy_ui" / "index.html")

    @app.get("/legacy/")
    def legacy_slash():
        return RedirectResponse("../legacy")

    @app.get("/")
    def root():
        return {"ledgerline": "7.2 sandbox", "legacy_client": "/legacy", "services": "/services", "screens": "/screens"}

    return app


def serve(port: int = 8077, app: FastAPI | None = None, erp: ERP | None = None) -> str:
    """Start the server in a background thread and return its URL (and, in Colab, print a proxied link).

    erp: serve this ERP object as the default tenant, so a notebook can look inside what the HTTP calls did.
    """
    import time

    import uvicorn

    if app is None:
        app = create_app()
        if erp is not None:
            app.state.tenants["default"] = erp
    cfg = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    url = f"http://127.0.0.1:{port}"
    try:
        from google.colab.output import eval_js  # type: ignore

        public = eval_js(f"google.colab.kernel.proxyPort({port})")
        print("Legacy client (open in a new tab):", public.rstrip("/") + "/legacy")
    except Exception:
        print("Ledgerline is running at", url, "· legacy client:", url + "/legacy")
    serve.app, serve.server = app, server
    return url


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m ledgerline.server", description="Run the Ledgerline ERP 7.2 sandbox over HTTP.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8077)
    ap.add_argument("--modules", default="", help="capstone modules to install, comma-separated (e.g. hr_leave)")
    a = ap.parse_args(argv)
    import uvicorn

    mods = [m for m in a.modules.split(",") if m]
    print(f"Ledgerline ERP 7.2 sandbox on http://{a.host}:{a.port}  ·  legacy client: http://{a.host}:{a.port}/legacy"
          + (f"  ·  modules: {', '.join(mods)}" if mods else ""))
    uvicorn.run(create_app(lambda: ERP(modules=mods)), host=a.host, port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
