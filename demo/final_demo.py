"""Lecture 8, the final demo: the whole Bahi reference system, end to end, on Modal.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/final_demo.py --mode auto     # records cassette L8_demo
    /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/final_demo.py --mode replay   # the same run, no key

Acts (each writes one JSON file under demo/logs/):
  1. journey.json      the reference app (bahi.app) served by uvicorn on a real port, driven over HTTP with httpx:
                       Kavita signs in and types her one sentence; the agent asks one question (the closed cost
                       centre); she answers; preview; "Yes, go ahead"; PR/2026/04417 waits on Rohit (a Temporal
                       workflow, Lecture 7); she cannot approve it herself (403); Rohit signs in on his own, sees it
                       in his inbox and his Slack-style message, one tap; the workflow orders and releases
                       PO/2026/01182; read-back from Bahi; the joined audit trail and Bahi's own rows.
  2. crash_drill.json  a worker killed while the workflow waits for Rohit; no worker for 30 hours; a new worker
                       replays the history, sends the overdue reminder, and finishes: one request, one order.
  3. kill_switch.json  writes switched off mid-flight: nothing reaches Bahi while off; one order after it is back on.
  4. demo_summary.json the numbers the deck and WALKTHROUGH.md read (with the L1 legacy counts beside them, from
                       lectures/L1-the-form/experiments/logs/by_hand.json, and the scorecard if demo/scorecard.py ran).
The legacy client is served by the same process at /legacy; we check it answers, so the before and the after are
one system. Screenshots: demo/shots_modal.py.
"""
from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parent
sys.path.insert(0, str(COURSE / "bahi"))

import httpx  # noqa: E402
import uvicorn  # noqa: E402

from bahi.app.journey import OPENING, run_journey  # noqa: E402
from bahi.app.main import create_app  # noqa: E402
from bahi.durable import drills  # noqa: E402

LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)
MODE = os.environ.get("BAHI_LLM_MODE", "auto")
PORT = 8077


def dump(name, obj):
    (LOGS / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str))
    print(f"wrote demo/logs/{name}")


# ------------------------------------------------------------------ 1. the journey, over HTTP
t0 = time.perf_counter()
web = create_app(cassette="L8_demo", durable=True, mcp=True)
srv = uvicorn.Server(uvicorn.Config(web, host="127.0.0.1", port=PORT, log_level="warning"))
th = threading.Thread(target=srv.run, daemon=True)
th.start()
while not srv.started:
    time.sleep(0.1)
base = f"http://127.0.0.1:{PORT}"
print("app up at", base, "in", round(time.perf_counter() - t0, 1), "s")
try:
    with httpx.Client(base_url=base, timeout=600) as c:
        legacy = c.get("/legacy")
        t1 = time.perf_counter()
        j = run_journey(c)
        j["wall_seconds"] = round(time.perf_counter() - t1, 1)
        j["legacy_client"] = {"url": "/legacy", "status": legacy.status_code, "bytes": len(legacy.content)}
    erp = web.state.l5.erp
    j["checks"]["one_gasket_order"] = len([o for o in erp.orders(itm_cd="GSK-SIL-05L")
                                           if o["created_on"] >= "2026-10-26"]) == 1
    j["checks"]["legacy_client_served"] = legacy.status_code == 200
    j["ok"] = all(j["checks"].values())
    j["over_http"] = {"server": "uvicorn", "client": "httpx", "base": base}
    j["durable"], j["mcp"], j["mode"], j["cassette"] = True, True, MODE, "L8_demo"
    j["opening"] = OPENING
    # the workflow's own record of the wait, if the runtime kept it
    d = web.state.l5.durable
    if d is not None and hasattr(d, "handles"):
        j["workflows"] = [str(h) for h in getattr(d, "handles", {})][:5]
finally:
    web.state.l5.close()
    srv.should_exit = True
    th.join(timeout=10)
dump("journey.json", j)
print("JOURNEY", "OK" if j["ok"] else "FAILED", j["checks"])
for s in j["steps"]:
    r = s.get("response") or {}
    print(f"[{s['who']}] {s['what']}: {(r.get('reply') or json.dumps(r, ensure_ascii=False, default=str))[:300]}")

# ------------------------------------------------------------------ 2. the crash drill
t2 = time.perf_counter()
cw = asyncio.run(drills.crash_while_waiting())
cw["seconds_wall"] = round(time.perf_counter() - t2, 1)
dump("crash_drill.json", cw)
print("CRASH", {k: cw[k] for k in ("status_before_crash", "reminders_sent_while_no_worker", "status_after_restart",
                                   "requests", "orders")}, cw["result"].get("outcome"))

# ------------------------------------------------------------------ 3. the kill switch
t3 = time.perf_counter()
ks = asyncio.run(drills.kill_switch())
ks["seconds_wall"] = round(time.perf_counter() - t3, 1)
dump("kill_switch.json", ks)
print("KILL", {k: ks[k] for k in ("orders_while_paused", "still_paused_after_min", "orders_after",
                                  "requests_written_by_tool")}, ks["result"].get("outcome"))

# ------------------------------------------------------------------ 4. the summary the deck reads
by_hand = json.loads((COURSE / "lectures/L1-the-form/experiments/logs/by_hand.json").read_text())
kav_msgs = [s for s in j["steps"] if s["who"] == "KJOSHI" and s["what"] == "message"]
po = j.get("final_po") or {}
summary = {
    "mode": MODE,
    "before_legacy_L1": {"source": "lectures/L1-the-form/experiments/logs/by_hand.json",
                         "monday_counts": by_hand["monday_counts"], "monday_by_person": by_hand["monday_by_person"],
                         "status_bar_after_save": by_hand["status_bar_after_save"],
                         "status_field_after_save": by_hand["status_field_after_save"],
                         "tax_error": by_hand["tax_error"], "friday_release": by_hand["friday_release"],
                         "minutes_estimate_klm": by_hand.get("monday_minutes_estimate_klm")},
    "after_app": {
        "kavita_messages": [m["body"]["text"] for m in kav_msgs],
        "kavita_message_count": len(kav_msgs),
        "agent_questions": sum(1 for m in kav_msgs if "?" in (m["response"]["reply"] or "")),
        "rohit_taps": 1,
        "sign_ins": sum(1 for s in j["steps"] if s["what"] == "sign in") + 1,
        "final_po": {k: po.get(k) for k in ("po_no", "status", "approved_by", "created_by", "gross_value", "cc_cd",
                                            "sup_cd", "tax_cd")},
        "checks": j["checks"], "ok": j["ok"], "audit_summary": j["audit_summary"], "llm": j.get("llm"),
        "acts_as": j.get("acts_as"), "wall_seconds": j["wall_seconds"],
        "path": next((e.get("path") for e in reversed(j["audit"]) if e.get("path")), None),
    },
    "crash_drill": {k: cw.get(k) for k in ("down_h", "status_before_crash", "reminders_sent_while_no_worker",
                                           "status_after_restart", "requests", "orders", "attempts_worker_A",
                                           "attempts_worker_B", "reminder")} | {"outcome": cw["result"].get("outcome")},
    "kill_switch": {k: ks.get(k) for k in ("orders_while_paused", "still_paused_after_min", "orders_after",
                                           "tool_preview_with_switch_on", "tool_commit_with_switch_on",
                                           "requests_written_by_tool", "ladder")} | {"outcome": ks["result"].get("outcome")},
}
sc = LOGS / "scorecard.json"
if sc.exists():
    x = json.loads(sc.read_text())
    summary["scorecard"] = {"source": "demo/logs/scorecard.json", **{k: x["summary"].get(k) for k in (
        "cases", "passed", "pass_rate", "ci95", "never_event_cases", "inr", "inr_per_resolved_order", "turn_p95")},
        "gate": x["gate"]}
dump("demo_summary.json", summary)
print("DEMO", "OK" if j["ok"] else "FAILED")
sys.exit(0 if j["ok"] else 1)
