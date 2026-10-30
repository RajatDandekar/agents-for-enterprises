"""Smoke test before the real runs: the set-ups, M1 on each stack (cassettes L1v4_prod_*_r0), Langfuse round trip,
making a trace public after the fact, and one headless screenshot. Writes logs/smoke.json."""
import base64
import datetime as dt
import json
import os
import pathlib
import time
import urllib.request
import uuid

from ledgerline.course.l1.production.missions import MISSIONS, snapshot
from ledgerline.course.l1.production.runner import Rig
from ledgerline.erp.engine import ERP

HERE = pathlib.Path(__file__).parent
(HERE / "logs").mkdir(exist_ok=True)
out = {"setups": {}}
for m in MISSIONS:
    erp = ERP()
    try:
        ctx = m.setup(erp)
        out["setups"][m.id] = {"ok": True, "ctx": ctx, "opening": m.opening(ctx or {})}
    except Exception as e:  # noqa: BLE001
        out["setups"][m.id] = {"ok": False, "error": repr(e)[:300]}
print(json.dumps(out["setups"], indent=1))

rig = Rig(langfuse=True, budget_usd=0.5)
rows = []
for stack in ("ours", "openai_agents", "langgraph"):
    r = rig.run_mission(stack, "google/gemini-3.8-flash", MISSIONS[0], run=0)
    rows.append(r)
    print(stack, r["passed"], r["checks"], r["never_events"], r["error"], r["model_calls"], r["tokens"], r["cost_usd"],
          r["wall_s"], [c["name"] for c in r["tool_calls"]], r["replies"][-1][:200] if r["replies"] else None)
rig.close()
out["m1"] = [{k: r[k] for k in ("stack", "passed", "checks", "never_events", "error", "model_calls", "tokens", "cost_usd",
                                "wall_s", "trace_id", "replies", "tool_calls", "native")} for r in rows]
out["spent_usd"] = rig.gw.spent_usd

# ---------------------------------------------------------------- Langfuse: read back, public after the fact
base = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST")).rstrip("/")
auth = "Basic " + base64.b64encode(f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()).decode()


def api(method, path, body=None):
    req = urllib.request.Request(base + path, method=method, headers={"Authorization": auth, "Content-Type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:500].decode(errors="replace")


tid = rows[0]["trace_id"]
time.sleep(20)
out["obs_v2"] = api("GET", f"/api/public/v2/observations?traceId={tid}&limit=50&fields=core,basic,usage")
if isinstance(out["obs_v2"][1], dict):
    out["obs_v2"] = [out["obs_v2"][0], [{k: o.get(k) for k in ("name", "type", "parentObservationId", "startTime", "endTime")}
                                          for o in out["obs_v2"][1].get("data", [])]]
out["trace_legacy_get"] = api("GET", f"/api/public/traces/{tid}")[0]
now = dt.datetime.now(dt.timezone.utc).isoformat()
out["public_upsert"] = api("POST", "/api/public/ingestion",
                           {"batch": [{"id": str(uuid.uuid4()), "timestamp": now, "type": "trace-create",
                                       "body": {"id": tid, "public": True}}]})
out["scores"] = api("GET", f"/api/public/v3/scores?traceId={tid}&limit=10")
if isinstance(out["scores"][1], dict):
    out["scores"] = [out["scores"][0], [{k: s.get(k) for k in ("name", "value", "dataType")} for s in out["scores"][1].get("data", [])]]
from langfuse import Langfuse  # noqa: E402
lf = Langfuse(tracing_enabled=False, base_url=base)
out["trace_url"] = lf.get_trace_url(trace_id=tid)
out["lf_api"] = [a for a in dir(lf.api) if not a.startswith("_")]
time.sleep(15)

from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 1920, "height": 1080}, color_scheme="light").new_page()
    pg.goto(out["trace_url"], wait_until="networkidle", timeout=90000)
    pg.wait_for_timeout(12000)
    pg.screenshot(path=str(HERE / "logs" / "smoke_shot.png"))
    out["page_text"] = pg.inner_text("body")[:1500]
    out["page_url"] = pg.url
    b.close()
(HERE / "logs" / "smoke.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: v for k, v in out.items() if k not in ("m1",)}, indent=1, default=str)[:6000])
