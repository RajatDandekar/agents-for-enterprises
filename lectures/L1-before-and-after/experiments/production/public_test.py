"""Can a trace be made public after the fact with one late OpenTelemetry span? Replays M1 from the r0 cassette (no
model cost), publishes it, screenshots it with no login. Writes logs/public_test.json."""
import json
import pathlib
import time

from ledgerline.course.l1.production import langfuse_api as LF
from ledgerline.course.l1.production.missions import MISSIONS
from ledgerline.course.l1.production.runner import Rig

HERE = pathlib.Path(__file__).parent
rig = Rig(langfuse=True, budget_usd=0.05)
r = rig.run_mission("ours", "google/gemini-3.8-flash", MISSIONS[0], run=0)
rig.tp.force_flush()
time.sleep(10)
LF.make_public(rig.tracer, r["trace_id"], r["root_span_id"])
rig.close()
url = LF.trace_url(r["trace_id"])
out = {"trace_id": r["trace_id"], "url": url, "replayed_calls": r["replayed_calls"], "model_calls": r["model_calls"]}
time.sleep(45)
out["scores"] = LF.api("GET", f"/api/public/v3/scores?traceId={r['trace_id']}&limit=10")
from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 1920, "height": 1080}, color_scheme="light").new_page()
    for i in range(3):
        pg.goto(url, wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(10000)
        txt = pg.inner_text("body")
        if "do not have access" not in txt:
            break
        time.sleep(30)
    pg.screenshot(path=str(HERE / "logs" / "public_test.png"))
    out["text"] = txt[:2000]
    b.close()
(HERE / "logs" / "public_test.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str)[:4000])
