"""Lecture 5 v4: the purchasing chain, tool by tool, with no model (facts the workflow blocks and the race rely on).
Run on Modal: /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L5-the-loop/experiments/chain_probe.py
Writes experiments/logs/chain_probe.json."""
import json, pathlib, sys
sys.path.insert(0, "/course/ledgerline")
from ledgerline.erp.engine import ERP
from ledgerline.erp.receipts import install_receipts
from ledgerline.toolbox import Toolbox, ALL

out = {}
def run(tag, tb, name, args):
    r = tb.call(name, args)
    out[tag] = {"tool": name, "args": args, "result": r}
    return r

erp = ERP(); install_receipts(erp)
emma = Toolbox(erp, "ECLARKE", names=ALL); dan = Toolbox(erp, "DOKAFOR", names=ALL); aiko = Toolbox(erp, "ATANAKA", names=ALL)
run("stock", emma, "check_stock", {"item_code": "BAT-500"})
run("find_sup_voltway", emma, "find_supplier", {"name": "Voltway"})
run("certs_voltway", emma, "supplier_certificates", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500"})
run("certs_nordic", emma, "supplier_certificates", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"})
run("budget_prd07", emma, "check_budget", {"cost_centre": "PRD-07"})
run("budget_prd05", emma, "check_budget", {"cost_centre": "PRD-05"})
run("pr_preview", emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09"})
pr = run("pr_commit", emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
prn = pr.get("request_no")
run("pr_commit_again", emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
run("po_before_approval", emma, "create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": prn, "confirm": True})
run("status_waiting", emma, "order_status", {"request_no": prn})
run("dan_inbox", dan, "list_my_approvals", {})
run("emma_approves_own", emma, "approve_purchase_request", {"request_no": prn, "decision": "approve"})
run("dan_approves", dan, "approve_purchase_request", {"request_no": prn, "decision": "approve"})
run("status_approved", emma, "order_status", {"request_no": prn})
run("po_preview", emma, "create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": prn})
po = run("po_commit", emma, "create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": prn, "confirm": True})
pon = po.get("po_no")
run("po_release", emma, "release_purchase_order", {"po_no": pon})
run("po_status", emma, "order_status", {"po_no": pon})
run("receive_preview", aiko, "receive_goods", {"po_no": pon, "quantity": 1200})
# bells: within Emma's limit
b = run("bells_pr", emma, "create_purchase_request", {"item_code": "BEL-STD-01", "quantity": 10000, "cost_centre": "PRD-07", "need_by": "2026-11-16", "confirm": True})
bpo = run("bells_po", emma, "create_purchase_order", {"supplier_code": "PB-MAN-0017", "request_no": b.get("request_no"), "confirm": True})
run("bells_release", emma, "release_purchase_order", {"po_no": bpo.get("po_no")})
# cartons, hub motors
c = run("cartons_pr", emma, "create_purchase_request", {"item_code": "BOX-BIKE-01", "quantity": 5000, "cost_centre": "PRD-03", "need_by": "2026-11-20", "confirm": True})
# nordic: does Ledgerline itself stop an order from an expired-certificate supplier?
erp2 = ERP(); install_receipts(erp2)
e2 = Toolbox(erp2, "ECLARKE", names=ALL); d2 = Toolbox(erp2, "DOKAFOR", names=ALL)
p2 = run("nordic_pr", e2, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
run("nordic_dan", d2, "approve_purchase_request", {"request_no": p2.get("request_no"), "decision": "approve"})
n = run("nordic_po", e2, "create_purchase_order", {"supplier_code": "NC-GDA-0063", "request_no": p2.get("request_no"), "confirm": True})
run("nordic_release", e2, "release_purchase_order", {"po_no": n.get("po_no")})
run("closed_pr", e2, "create_purchase_request", {"item_code": "BAT-500", "quantity": 1000, "cost_centre": "PRD-05", "need_by": "2026-11-09", "confirm": True})
run("closed_pr_preview", e2, "create_purchase_request", {"item_code": "BAT-500", "quantity": 1000, "cost_centre": "PRD-05", "need_by": "2026-11-09"})
# a lost reply: the service commits, the reply never comes back; a second try must find the first
erp3 = ERP(); install_receipts(erp3)
e3 = Toolbox(erp3, "ECLARKE", names=ALL)
svcs = sorted({c.svc for c in []})
out["services_seen_in_pr"] = sorted({c.svc for c in erp.calls if getattr(c, 'svc', None)})[:40]
import inspect
out["calls_attrs"] = [a for a in dir(erp.calls[0]) if not a.startswith("_")] if erp.calls else []
pathlib.Path("logs").mkdir(exist_ok=True)
pathlib.Path("logs/chain_probe.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
for k, v in out.items():
    r = v.get("result") if isinstance(v, dict) else v
    print(k, json.dumps(r, default=str)[:300] if r is not None else v)
