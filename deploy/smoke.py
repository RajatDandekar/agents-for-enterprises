"""Smoke test of the deployable app, run inside the built image (deploy/build_check.py) or on Modal via
tools/modal_run.py. No model is called and nothing is exposed: FastAPI's TestClient talks to the app in-process.

Checks: health, readiness, versions pinned, Kavita's order through the HTTP API (start -> waiting -> Rohit approves
with his own token -> released), a double start returns the same workflow, Kavita cannot approve her own request,
and the kill switch blocks a new order and needs the admin token.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # the folder that holds deploy/

os.environ.setdefault("BAHI_ENV", "dev")
os.environ.setdefault("BAHI_TEMPORAL", "time_skipping")
os.environ.setdefault("BAHI_ADMIN_TOKEN", "smoke-admin")

from fastapi.testclient import TestClient  # noqa: E402

from deploy.app import STATE, app  # noqa: E402

results = []


def ok(name, cond, detail=""):
    results.append({"check": name, "ok": bool(cond), "detail": detail})
    print(("PASS " if cond else "FAIL ") + name, detail if not cond else "")


c = TestClient(app)
ok("healthz", c.get("/healthz").json()["ok"])
v = c.get("/version").json()
from deploy.versions import check  # noqa: E402

drift = check(v["pinned"])
ok("versions pinned (prompts, tools, workflow)", not drift, drift)
kav = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123"}).json()["token"]
roh = c.post("/login", json={"user_id": "RMEHTA", "password": "rohit@123"}).json()["token"]
H = lambda t: {"Authorization": f"Bearer {t}"}  # noqa: E731
order = {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
         "need_by": "2026-11-02", "ref": "smoke-1"}
r = c.post("/orders", json=order, headers=H(kav)).json()
wid = r["workflow_id"]
ok("order starts and waits for Rohit", r["stage"] == "waiting for approval", r)
r2 = c.post("/orders", json=order, headers=H(kav)).json()
ok("same order twice -> same workflow, one request", r2["workflow_id"] == wid and r2["request_no"] == r["request_no"], r2)
bad = c.post(f"/orders/{wid}/approve", json={"decision": "A"}, headers=H(kav))
ok("Kavita cannot approve her own request (Bahi refuses: her role has no approve service)",
   bad.status_code == 403 and "ERR-SEC-0001" in bad.text, bad.text)
good = c.post(f"/orders/{wid}/approve", json={"decision": "A", "comment": "ok"}, headers=H(roh)).json()
res = STATE["durable"].result(wid)
ok("Rohit approves -> order released", res["outcome"] == "released", res)
ok("readyz", c.get("/readyz").json()["ok"])
ok("kill switch needs the admin token", c.post("/flags", json={"kill": True}).status_code == 403)
c.post("/flags", json={"kill": True, "reason": "smoke"}, headers={"X-Admin-Token": os.environ["BAHI_ADMIN_TOKEN"]})
r3 = c.post("/orders", json={**order, "ref": "smoke-2"}, headers=H(kav)).json()
st = r3["stage"]
ok("kill switch on -> new order pauses before any write", st == "paused", r3)
erp = app.state.tenants["default"]
n_pr = erp.q1("SELECT COUNT(*) n FROM pr_hdr")["n"]
ok("... and wrote nothing to Bahi", n_pr == 1, n_pr)
c.post("/flags", json={"revive": True}, headers={"X-Admin-Token": os.environ["BAHI_ADMIN_TOKEN"]})
STATE["durable"].skip(0.2)
st = STATE["durable"].wait_for(r3["workflow_id"], ("waiting for approval",), timeout_s=30)
ok("switch back on -> the paused order carries on", st["stage"] == "waiting for approval", st)
STATE["durable"].close()
print(json.dumps({"passed": sum(r["ok"] for r in results), "of": len(results)}))
out = os.environ.get("SMOKE_LOG")
if out:
    with open(out, "w") as f:
        json.dump(results, f, indent=1, default=str)
sys.exit(0 if all(r["ok"] for r in results) else 1)
