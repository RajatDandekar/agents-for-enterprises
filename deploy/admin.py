"""Operator commands for the deployed app, run INSIDE Modal so the admin token never leaves the secret store.

    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd status          health, readiness, flags, today's spend
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd kill --reason "duplicates on PO/2026/01183"
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd revive
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd model-off      the assistant stops calling the model
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd model-on
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd stage --stage assist
    /Users/raj/.venv/bin/modal run deploy/admin.py --cmd smoke          Kavita's whole journey against the public URL

BAHI_ENV picks the environment (default staging). The admin token is read from the Modal secret bahi-<env>
(key BAHI_ADMIN_TOKEN) inside the function and is never printed or returned.
The smoke result is written to lectures/L7-the-night-shift/experiments/logs/staging_smoke.json.
"""
import json
import os
import pathlib

import modal

ENV = os.environ.get("BAHI_ENV", "staging")
ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = os.environ.get("BAHI_URL", f"https://rajatworkspace--bahi-agent-{ENV}.us-east.modal.run")

image = (modal.Image.debian_slim(python_version="3.11").pip_install("httpx")
         .add_local_file(ROOT / "bahi" / "bahi" / "app" / "journey.py", "/ops/journey.py"))
app = modal.App(f"bahi-admin-{ENV}", image=image)


@app.function(secrets=[modal.Secret.from_name(f"bahi-{ENV}")], timeout=1200)
def op(cmd: str, reason: str = "", stage: str = "") -> dict:
    import sys
    import time

    import httpx

    AH = {"X-Admin-Token": os.environ["BAHI_ADMIN_TOKEN"]}
    c = httpx.Client(base_url=URL, timeout=300, follow_redirects=True)
    out = {"url": URL, "cmd": cmd}
    if cmd in ("kill", "revive", "model-off", "model-on", "stage"):
        body = {"kill": {"kill": True, "reason": reason or "operator"}, "revive": {"revive": True},
                "model-off": {"model": False, "reason": reason or "operator"}, "model-on": {"model": True},
                "stage": {"stage": stage}}[cmd]
        r = c.post("/flags", json=body, headers=AH)
        out["status_code"], out["flags"] = r.status_code, r.json()
        return out
    t0 = time.time()
    h = c.get("/healthz")
    out["healthz"] = {"status": h.status_code, "body": h.json()}
    out["cold_start_s"] = round(time.time() - t0, 1)
    out["readyz"] = c.get("/readyz").json()
    out["flags"] = c.get("/flags").json()
    out["spend"] = c.get("/spend").json()
    if cmd == "status":
        return out
    # smoke: the guards first, then Kavita's journey with a live model
    out["admin_reset_without_token"] = c.post("/admin/reset").status_code
    out["flags_without_token"] = c.post("/flags", json={"kill": True}).status_code
    sys.path.insert(0, "/ops")
    from journey import run_journey

    t1 = time.time()
    j = run_journey(c)
    out["journey_seconds"] = round(time.time() - t1, 1)
    K = {"Authorization": "Bearer " + c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123"}).json()["token"]}
    gaskets = c.post("/svc/po_search", headers=K, json={"itm_cd": "GSK-SIL-05L", "from_dt": "2026-10-26"}).json()
    rows = (gaskets.get("data") or {}).get("rows", [])
    j["checks"]["one_gasket_order"] = len([x for x in rows if x["status"] != "CN"]) == 1
    out["journey"] = {"ok": all(j["checks"].values()), "checks": j["checks"], "conv": j.get("conv"),
                      "final_po": j.get("final_po"), "llm": j.get("llm"), "audit_summary": j.get("audit_summary"),
                      "audit_entries": len(j.get("audit") or []), "bahi_rows": len(j.get("bahi_rows") or []),
                      "bahi_users": sorted({x["user_id"] for x in j.get("bahi_rows") or []}),
                      "transcript": j.get("transcript")}
    out["spend_after"] = c.get("/spend").json()
    return out


@app.local_entrypoint()
def main(cmd: str = "status", reason: str = "", stage: str = ""):
    r = op.remote(cmd, reason, stage)
    if cmd == "smoke":
        p = ROOT / "lectures" / "L7-the-night-shift" / "experiments" / "logs" / f"{ENV}_smoke.json"
        p.write_text(json.dumps(r, indent=1, default=str, ensure_ascii=False))
        print("wrote", p.relative_to(ROOT))
    print(json.dumps({k: v for k, v in r.items() if k != "journey"}, indent=1, default=str)[:4000])
    if "journey" in r:
        print("journey ok:", r["journey"]["ok"], json.dumps(r["journey"]["checks"]))
        print("final PO:", json.dumps(r["journey"]["final_po"], default=str)[:600])
