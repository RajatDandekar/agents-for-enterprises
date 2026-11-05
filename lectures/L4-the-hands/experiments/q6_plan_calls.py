"""Lecture 4, section 9: question 6's plan from first principles, run tool by tool with no model.

    python3 lectures/L4-the-hands/experiments/q6_plan_calls.py          (light, local; no model call)

Question 6 of the forge (ledgerline/ledgerline/hephaestus/questions.json) needs several tools. The deck derives, with
the class, which tools are logically needed and in which order. This script makes exactly those calls, in that order,
in a fresh Ledgerline sandbox as Emma (ECLARKE), with the shipped toolbox, and records every request and result, so
the plan slide shows real values and not illustrative ones. Nothing is saved: the write is a preview (confirm=false).
Writes logs/q6_plan_calls.json.
"""
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))

from ledgerline.erp import services  # noqa: E402,F401  (registers the services)
from ledgerline.erp.engine import ERP  # noqa: E402
from ledgerline.toolbox import Toolbox  # noqa: E402

Q = json.loads((ROOT / "ledgerline" / "ledgerline" / "hephaestus" / "questions.json").read_text())["questions"][5]
PLAN = [
    ("find_supplier", {"name": "Nordic Cell Co."}),
    ("supplier_certificates", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}),
    ("supplier_certificates", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500"}),
    ("create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07",
                                 "need_by": "2026-11-09", "confirm": False}),
    ("check_budget", {"cost_centre": "PRD-07"}),
]
erp = ERP()
tb = Toolbox(erp, "ECLARKE", names=sorted({t for t, _ in PLAN}))
before = erp.q("SELECT COUNT(*) AS n FROM pr_hdr")[0]["n"]
calls = []
for tool, args in PLAN:
    t0 = time.perf_counter()
    res = tb.call(tool, args)
    calls.append({"tool": tool, "args": args, "result": res, "ms": round(1000 * (time.perf_counter() - t0), 2)})
after = erp.q("SELECT COUNT(*) AS n FROM pr_hdr")[0]["n"]
out = {"question": Q["ask"], "needs": Q["needs"], "as": "ECLARKE", "sandbox_today": str(erp.today),
       "calls": calls, "purchase_requests_before": before, "purchase_requests_after": after,
       "note": "No model: the plan the class derives, run by hand in order. The write is a preview; nothing is saved."}
(HERE / "logs" / "q6_plan_calls.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
for c in calls:
    print(c["tool"], json.dumps(c["args"]), "->", json.dumps(c["result"], ensure_ascii=False, default=str)[:300])
print("purchase requests before/after:", before, after)
