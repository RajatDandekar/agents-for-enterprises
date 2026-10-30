"""End-to-end check of the toolbox: Emma's 2,000 battery packs, request to goods receipt, plus the traps."""
import json
from ledgerline.erp.engine import ERP
from ledgerline.toolbox import Toolbox, SPECS

erp = ERP()
emma, daniel, aiko = Toolbox(erp, "ECLARKE"), Toolbox(erp, "DOKAFOR"), Toolbox(erp, "ATANAKA")
fails = []
def step(tb, name, args, want=True):
    r = tb.call(name, args)
    print(f"{tb.user:8} {name:26} ok={r.get('ok')}  " + json.dumps({k: r[k] for k in list(r)[:6] if k != 'ok'}, default=str)[:230])
    if bool(r.get("ok")) != want:
        fails.append((name, r))
    return r

print(len(SPECS), "tools:", ", ".join(SPECS))
for s in SPECS.values():  # every tool.json example must pass its own schema check
    s.check(s.spec.get("example", {})) if s.spec.get("example") else None
step(emma, "find_item", {"query": "5 litre battery pack"})
step(emma, "check_stock", {"item_code": "BAT-500"})
step(emma, "find_supplier", {"name": "Voltway Polymer"})
step(emma, "check_budget", {"cost_centre": "PRD-05"})
pv = step(emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09"})
pr = step(emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
again = step(emma, "create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
assert again.get("already_done"), "idempotency"
step(emma, "approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"}, want=False)  # self-approval refused
step(daniel, "list_my_approvals", {})
step(daniel, "approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
sup = "VC-EIN-0042"
step(emma, "create_purchase_order", {"supplier_code": sup, "request_no": pr["request_no"]})
po = step(emma, "create_purchase_order", {"supplier_code": sup, "request_no": pr["request_no"], "confirm": True})
print("   PO status:", po.get("status"), "| next:", po.get("next_step"))
if po.get("status_code") == "PA":
    step(daniel, "approve_purchase_order", {"po_no": po["po_no"]})
step(emma, "receive_goods", {"po_no": po["po_no"], "quantity": 100, "confirm": True}, want=False)  # not released yet
rel = step(emma, "release_purchase_order", {"po_no": po["po_no"]})
assert rel.get("sent_to_supplier"), rel
step(aiko, "receive_goods", {"po_no": po["po_no"], "quantity": 1200})
g1 = step(aiko, "receive_goods", {"po_no": po["po_no"], "quantity": 1200, "confirm": True})
step(aiko, "receive_goods", {"po_no": po["po_no"], "quantity": 900, "confirm": True}, want=False)  # more than ordered
g2 = step(aiko, "receive_goods", {"po_no": po["po_no"], "quantity": 800, "confirm": True})
assert g2.get("order_closed"), g2
assert pr["status"] == "WAITING FOR APPROVAL" and pv["preview"]["needs_approval"], pv
st = step(emma, "order_status", {"po_no": po["po_no"]})
assert st["received"] == 2000 and st["status"].startswith("CLOSED"), st
step(emma, "check_stock", {"item_code": "BAT-500"})
# traps
step(emma, "create_purchase_order", {"supplier_code": sup, "item_code": "BAT-500", "quantity": 1500, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}, want=False)  # direct > 50k
d = step(emma, "create_purchase_order", {"supplier_code": sup, "item_code": "BAT-375", "quantity": 100, "cost_centre": "PRD-05", "need_by": "2026-11-09"})
print("   closed-cc warning:", d.get("warnings"))
step(emma, "check_stock", {"item_code": 42}, want=False)  # wrong type
step(emma, "send_message", {"to": "@daniel", "text": "PR approved, thanks"})
print("FAILS:", len(fails))
for f in fails:
    print("  ", f[0], json.dumps(f[1], default=str)[:300])
assert not fails
print("TOOLBOX OK")

# ---- the same tools over MCP: discovered by a client, called through the plug
from ledgerline.toolbox.mcp import build_toolbox_server
from ledgerline.mcp_server import MCPClient, MCPClientTools
erp2 = ERP()
c = MCPClient(build_toolbox_server(erp2, "ECLARKE"))
mt = MCPClientTools(c)
print("MCP tools:", len(mt.names), mt.schemas()[1]["function"]["parameters"])
r = json.loads(mt.call("check_stock", {"item_code": "BAT-500"}))
assert r["ok"] and r["free_total"] > 0, r
r = json.loads(mt.call("create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}))
assert r["request_no"] == "PR/2026/04417", r
print("wire:", [w["method"] for w in c.wire])
c.close()
print("MCP OK")

# ---- retries after a lost reply (fixes from the L4 builder's report)
erp3 = ERP(); k3 = Toolbox(erp3, "ECLARKE"); r3 = Toolbox(erp3, "DOKAFOR")
args = {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}
erp3.inject("pr_save", "timeout_after_commit")
a = k3.call("create_purchase_request", args)
assert a["ok"] and a["status"] == "WAITING FOR APPROVAL", a            # the lost reply is found by key, then submitted
assert len(erp3.q("SELECT * FROM pr_hdr WHERE remarks LIKE '%key:%'")) == 1
r3.call("approve_purchase_request", {"request_no": a["request_no"], "decision": "approve"})
po_args = {"supplier_code": "VC-EIN-0042", "request_no": a["request_no"], "confirm": True}
erp3.inject("po_save", "timeout_after_commit")
b = k3.call("create_purchase_order", po_args)
c = k3.call("create_purchase_order", po_args)                          # retry: the PR is now CL, the order is found
assert b["ok"] and c.get("already_done") and b["po_no"] == c["po_no"], (b, c)
print("RETRY OK")
