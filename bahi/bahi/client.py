"""A small HTTP client for Bahi, the way any outside system (a script, n8n, an agent) reaches the ERP.

    from bahi.client import BahiClient
    kavita = BahiClient("http://127.0.0.1:8077", "KJOSHI", "kavita@123")
    kavita.call("stk_query", itm_cd="GSK-SIL-05L")
    # -> {"rc": "S", "err_cd": None, "msg": "", "data": {"on_hand": 54000, ... "cover_days": 9}}

Every reply is the legacy envelope {rc, err_cd, msg, data}: rc is "S" (success), "W" (warning) or "E" (error).
A lost reply (HTTP 504: the server may have done the work) raises bahi.ServiceTimeout, as the in-process ERP does.
"""
from __future__ import annotations

import httpx

from .erp.engine import ServiceTimeout


class BahiError(RuntimeError):
    """Raised by .ok() when a call came back with rc "E"."""


class BahiClient:
    def __init__(self, base_url: str, user: str, password: str, ou_cd: str | None = None,
                 tenant: str | None = None, http: httpx.Client | None = None, timeout: float = 30.0):
        """base_url: e.g. http://127.0.0.1:8077.  http: any httpx-style client (FastAPI's TestClient works too)."""
        self.base = base_url.rstrip("/")
        self.http = http or httpx.Client(timeout=timeout)
        self.tenant = tenant
        self.user = user.upper()
        body = {"user_id": user, "password": password}
        if ou_cd:
            body["ou_cd"] = ou_cd
        r = self.http.post(self._url("/login"), json=body, headers=self._headers())
        d = r.json()
        if r.status_code != 200 or d.get("rc") != "S":
            raise PermissionError(f"{d.get('err_cd')}: {d.get('msg')}")
        self.token, self.role, self.name = d["token"], d["role_cd"], d["name"]
        self.welcome = d.get("msg", "")

    def _url(self, path: str) -> str:
        return self.base + path if self.base else path

    def _headers(self, screen: str | None = None, task: str | None = None) -> dict:
        h = {}
        if getattr(self, "token", None):
            h["Authorization"] = f"Bearer {self.token}"
        if self.tenant:
            h["X-Tenant"] = self.tenant
        if screen:
            h["X-Screen"] = screen
        if task:
            h["X-Task"] = task
        return h

    def call(self, svc: str, screen: str | None = None, task: str | None = None, **payload) -> dict:
        """POST /svc/<svc> with a flat payload. screen/task are sent as X-Screen/X-Task so the live run records them."""
        r = self.http.post(self._url(f"/svc/{svc}"), json=payload, headers=self._headers(screen, task))
        if r.status_code == 504:
            raise ServiceTimeout(r.json().get("msg", f"{svc}: no reply"))
        if r.status_code == 401:
            raise PermissionError(r.json().get("detail", "SESSION EXPIRED"))
        return r.json()

    def ok(self, svc: str, **payload):
        """Like call(), but returns only data and raises BahiError on rc "E"."""
        env = self.call(svc, **payload)
        if env["rc"] == "E":
            raise BahiError(f"{env['err_cd']}: {env['msg']}")
        return env["data"]

    def live_run(self, since: int = 0) -> list[dict]:
        return self.http.get(self._url(f"/live-run?since={since}"), headers=self._headers()).json()

    def screens(self) -> dict:
        return self.http.get(self._url("/screens"), headers=self._headers()).json()

    def services(self) -> list[dict]:
        return self.http.get(self._url("/services"), headers=self._headers()).json()

    def logout(self):
        self.http.post(self._url("/logout"), headers=self._headers())

    def __repr__(self):
        return f"<BahiClient {self.user} ({self.role}) at {self.base or 'in-process app'}>"
