"""Smoke test of the deployable app, run inside the built image (deploy/build_check.py) or on Modal via
tools/modal_run.py. No model is called and nothing is exposed: FastAPI's TestClient talks to the app in-process.

Checks: health, readiness, versions pinned, Emma's order through the HTTP API (start -> waiting -> Daniel approves
with his own token -> released), a double start returns the same workflow, Emma cannot approve her own request,
and the kill switch blocks a new order and needs the admin token.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # the folder that holds deploy/

os.environ.setdefault("LEDGER_ENV", "dev")
os.environ.setdefault("LEDGER_TEMPORAL", "time_skipping")
os.environ.setdefault("LEDGER_ADMIN_TOKEN", "smoke-admin")

from fastapi.testclient import TestClient  # noqa: E402

from deploy.app import S, app  # noqa: E402

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
kav = c.post("/login", json={"user_id": "ECLARKE", "password": "emma@123"}).json()["token"]
roh = c.post("/login", json={"user_id": "DOKAFOR", "password": "daniel@123"}).json()["token"]
H = lambda t: {"Authorization": f"Bearer {t}"}  # noqa: E731
order = {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500", "quantity": 20000, "cost_centre": "PRD-07",
         "need_by": "2026-11-02", "ref": "smoke-1"}
r = c.post("/orders", json=order, headers=H(kav)).json()
wid = r["workflow_id"]
ok("order starts and waits for Daniel", r["stage"] == "waiting for approval", r)
r2 = c.post("/orders", json=order, headers=H(kav)).json()
ok("same order twice -> same workflow, one request", r2["workflow_id"] == wid and r2["request_no"] == r["request_no"], r2)
bad = c.post(f"/orders/{wid}/approve", json={"decision": "A"}, headers=H(kav))
ok("Emma cannot approve her own request (Ledgerline refuses: her role has no approve service)",
   bad.status_code == 403 and "ERR-SEC-0001" in bad.text, bad.text)
good = c.post(f"/orders/{wid}/approve", json={"decision": "A", "comment": "ok"}, headers=H(roh)).json()
res = S.durable.result(wid)
ok("Daniel approves -> order released", res["outcome"] == "released", res)
ok("readyz", c.get("/readyz").json()["ok"])
ok("the L5 reference app is served (/app/chat, /app/inbox)", c.get("/app/chat").status_code == 200
   and c.get("/app/inbox").status_code == 200)
ok("Ledgerline's /admin/reset needs the admin token", c.post("/admin/reset").status_code == 403)
AH = {"X-Admin-Token": os.environ["LEDGER_ADMIN_TOKEN"]}
c.post("/flags", json={"model": False, "reason": "smoke"}, headers=AH)
off = c.post("/api/chat", headers=H(kav))
ok("model switch off -> chat refused before any model call", off.status_code == 503, off.text)
c.post("/flags", json={"model": True}, headers=AH)
sp = c.get("/spend").json()
ok("spend ledger and cap visible", "cap_inr" in sp and sp["inr"] >= 0, sp)
ok("kill switch needs the admin token", c.post("/flags", json={"kill": True}).status_code == 403)
c.post("/flags", json={"kill": True, "reason": "smoke"}, headers={"X-Admin-Token": os.environ["LEDGER_ADMIN_TOKEN"]})
r3 = c.post("/orders", json={**order, "ref": "smoke-2"}, headers=H(kav)).json()
st = r3["stage"]
ok("kill switch on -> new order pauses before any write", st == "paused", r3)
erp = S.erp
n_pr = erp.q1("SELECT COUNT(*) n FROM pr_hdr")["n"]
ok("... and wrote nothing to Ledgerline", n_pr == 1, n_pr)
c.post("/flags", json={"revive": True}, headers={"X-Admin-Token": os.environ["LEDGER_ADMIN_TOKEN"]})
S.durable.skip(0.2)
st = S.durable.wait_for(r3["workflow_id"], ("waiting for approval",), timeout_s=30)
ok("switch back on -> the paused order carries on", st["stage"] == "waiting for approval", st)
S.durable.close()
print(json.dumps({"passed": sum(r["ok"] for r in results), "of": len(results)}))
out = os.environ.get("SMOKE_LOG")
if out:
    with open(out, "w") as f:
        json.dump(results, f, indent=1, default=str)
sys.exit(0 if all(r["ok"] for r in results) else 1)
