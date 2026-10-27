"""The reference app's HTTP journey test: Kavita's order to a released PO/2026/01182, through the API only.

    modal run tools/modal_run.py --script lectures/L5-the-signature/experiments/app_journey.py

FastAPI TestClient against bahi.app.main.create_app(): MCP intent tools bound to Kavita's sign-in, the commit and
approval path as a Temporal workflow (time-skipping test server), Rohit's one tap from his own sign-in.
Writes logs/journey.json (transcript, trace, joined audit log, Bahi rows, outbox, checks) for Lecture 8's demo.
"""
import json
import pathlib
import sys

from fastapi.testclient import TestClient

from bahi.app.journey import run_journey
from bahi.app.main import create_app

LOGS = pathlib.Path(__file__).parent / "logs"
durable = "--no-durable" not in sys.argv
app = create_app(cassette="L5_app", durable=durable, mcp=True)
try:
    with TestClient(app) as c:
        j = run_journey(c)
finally:
    app.state.l5.close()
for s in j["steps"]:
    print(f"[{s['who']}] {s['what']}: {json.dumps(s.get('body', ''), ensure_ascii=False)[:150]}")
    resp = s.get("response") or {}
    if "reply" in resp:
        print("   AGENT:", resp["reply"].replace("\n", " | ")[:600])
        print("   TRACE:", resp.get("trace"))
    else:
        print("   ->", json.dumps(resp, ensure_ascii=False, default=str)[:600])
print("\nCHECKS:", json.dumps(j["checks"], indent=1))
print("AUDIT SUMMARY:", j["audit_summary"])
print("FINAL PO:", {k: (j["final_po"] or {}).get(k) for k in ("po_no", "status", "approved_by", "created_by", "gross_value")})
j["durable"] = durable
(LOGS / "journey.json").write_text(json.dumps(j, indent=1, default=str, ensure_ascii=False))
print("OK" if j["ok"] else "JOURNEY FAILED")
sys.exit(0 if j["ok"] else 1)
