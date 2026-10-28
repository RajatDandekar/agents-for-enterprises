"""Probe: what the toolbox really returns for the five Studio workflows' steps, on a fresh Rasoi.
Writes logs/probe.json. Run on Modal:
    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L6-the-studio/experiments/probe.py
"""
import json
import pathlib
import time

from bahi.erp.engine import ERP
from bahi.erp import seed
from bahi.toolbox import Toolbox

LOG = pathlib.Path(__file__).parent / "logs" / "probe.json"
erp = ERP()
k, r, n = Toolbox(erp, "KJOSHI"), Toolbox(erp, "RMEHTA"), Toolbox(erp, "NDESAI")
out = {"_what": "toolbox outputs on a fresh Rasoi (bahi.erp.engine.ERP()), for L6 plates", "calls": []}


def call(tb, name, args):
    t0 = time.perf_counter()
    res = tb.call(name, args)
    out["calls"].append({"as": tb.user, "tool": name, "args": args, "seconds": round(time.perf_counter() - t0, 4),
                         "result": res})
    return res


# Monday reorder check: every active item
below = []
for code, *_ in seed.ITEMS:
    s = call(k, "check_stock", {"item_code": code})
    if s.get("ok"):
        below.append({"item": code, "free": s["free_total"], "on_order": s["on_order_total"],
                      "reorder": s["reorder_level"], "cover_days": s["cover_days"], "below": s["below_reorder"]})
out["reorder_scan"] = below

# the Diwali gasket chain
pr = call(k, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
                                         "need_by": "2026-11-09", "confirm": True})
again = call(k, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
                                            "need_by": "2026-11-09", "confirm": True})
call(k, "order_status", {"request_no": pr["request_no"]})
call(r, "list_my_approvals", {})
call(r, "approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
call(k, "order_status", {"request_no": pr["request_no"]})
po = call(k, "create_purchase_order", {"supplier_code": "DP-RJK-0042", "request_no": pr["request_no"], "confirm": True})
rel = call(k, "release_purchase_order", {"po_no": po["po_no"]})
call(k, "send_message", {"to": "@rohit", "text": f"{po['po_no']} released to Deccan Polymers."})
g1 = call(n, "receive_goods", {"po_no": po["po_no"], "quantity": 12000, "confirm": True})
g2 = call(n, "receive_goods", {"po_no": po["po_no"], "quantity": 8000, "confirm": True})
call(n, "send_message", {"to": "@kavita", "text": "goods in"})
call(k, "check_stock", {"item_code": "GSK-SIL-05L"})
# whistles with the default closed cost centre (the silent draft)
call(k, "create_purchase_request", {"item_code": "WHS-STD-01", "quantity": 20000, "cost_centre": "PRD-05",
                                    "need_by": "2026-11-09"})
out["queue"] = [dict(x) for x in erp.q("SELECT * FROM ntf_queue")] if hasattr(erp, "q") else None
LOG.parent.mkdir(exist_ok=True)
LOG.write_text(json.dumps(out, indent=1, default=str))
for c in out["calls"]:
    print(f"{c['as']:8} {c['tool']:26} {json.dumps(c['result'], default=str)[:260]}")
print(json.dumps(below, indent=0))
