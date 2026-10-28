"""End-to-end check of the toolbox: Kavita's 20,000 gaskets, request to goods receipt, plus the traps."""
import json
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox, SPECS

erp = ERP()
kavita, rohit, neha = Toolbox(erp, "KJOSHI"), Toolbox(erp, "RMEHTA"), Toolbox(erp, "NDESAI")
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
step(kavita, "find_item", {"query": "5 litre silicone gasket"})
step(kavita, "check_stock", {"item_code": "GSK-SIL-05L"})
step(kavita, "find_supplier", {"name": "Deccan Polymer"})
step(kavita, "check_budget", {"cost_centre": "PRD-05"})
pv = step(kavita, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"})
pr = step(kavita, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
again = step(kavita, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
assert again.get("already_done"), "idempotency"
step(kavita, "approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"}, want=False)  # self-approval refused
step(rohit, "list_my_approvals", {})
step(rohit, "approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
sup = "DP-RJK-0042"
step(kavita, "create_purchase_order", {"supplier_code": sup, "request_no": pr["request_no"]})
po = step(kavita, "create_purchase_order", {"supplier_code": sup, "request_no": pr["request_no"], "confirm": True})
print("   PO status:", po.get("status"), "| next:", po.get("next_step"))
if po.get("status_code") == "PA":
    step(rohit, "approve_purchase_order", {"po_no": po["po_no"]})
step(kavita, "receive_goods", {"po_no": po["po_no"], "quantity": 100, "confirm": True}, want=False)  # not released yet
rel = step(kavita, "release_purchase_order", {"po_no": po["po_no"]})
assert rel.get("sent_to_supplier"), rel
step(neha, "receive_goods", {"po_no": po["po_no"], "quantity": 12000})
g1 = step(neha, "receive_goods", {"po_no": po["po_no"], "quantity": 12000, "confirm": True})
step(neha, "receive_goods", {"po_no": po["po_no"], "quantity": 9000, "confirm": True}, want=False)  # more than ordered
g2 = step(neha, "receive_goods", {"po_no": po["po_no"], "quantity": 8000, "confirm": True})
assert g2.get("order_closed"), g2
assert pr["status"] == "WAITING FOR APPROVAL" and pv["preview"]["needs_approval"], pv
st = step(kavita, "order_status", {"po_no": po["po_no"]})
assert st["received"] == 20000 and st["status"].startswith("CLOSED"), st
step(kavita, "check_stock", {"item_code": "GSK-SIL-05L"})
# traps
step(kavita, "create_purchase_order", {"supplier_code": sup, "item_code": "GSK-SIL-05L", "quantity": 15000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}, want=False)  # direct > 50k
d = step(kavita, "create_purchase_order", {"supplier_code": sup, "item_code": "GSK-SIL-03L", "quantity": 100, "cost_centre": "PRD-05", "need_by": "2026-11-09"})
print("   closed-cc warning:", d.get("warnings"))
step(kavita, "check_stock", {"item_code": 42}, want=False)  # wrong type
step(kavita, "send_message", {"to": "@rohit", "text": "PR approved, thanks"})
print("FAILS:", len(fails))
for f in fails:
    print("  ", f[0], json.dumps(f[1], default=str)[:300])
assert not fails
print("TOOLBOX OK")

# ---- the same tools over MCP: discovered by a client, called through the plug
from bahi.toolbox.mcp import build_toolbox_server
from bahi.mcp_server import MCPClient, MCPClientTools
erp2 = ERP()
c = MCPClient(build_toolbox_server(erp2, "KJOSHI"))
mt = MCPClientTools(c)
print("MCP tools:", len(mt.names), mt.schemas()[1]["function"]["parameters"])
r = json.loads(mt.call("check_stock", {"item_code": "GSK-SIL-05L"}))
assert r["ok"] and r["free_total"] > 0, r
r = json.loads(mt.call("create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}))
assert r["request_no"] == "PR/2026/04417", r
print("wire:", [w["method"] for w in c.wire])
c.close()
print("MCP OK")
