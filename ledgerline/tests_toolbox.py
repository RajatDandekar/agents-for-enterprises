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
step(aiko, "receive_goods", {"po_no": po["po_no"], "quantity": 1200, "warehouse": "Manchester stores", "confirm": True}, want=False)  # a name, not a code: refused before any save
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

# ---- Lecture 4: supplier_certificates, built from scratch (an extra: in REGISTRY, served when named)
from ledgerline.toolbox import ALL, DEFAULT, REGISTRY
assert len(SPECS) == 15 and DEFAULT == list(SPECS) and "supplier_certificates" in REGISTRY and "supplier_certificates" not in SPECS
erp4 = ERP(); e4 = Toolbox(erp4, "ECLARKE", names=ALL)
assert "supplier_certificates" not in Toolbox(erp4, "ECLARKE").names              # the default set is unchanged
REGISTRY["supplier_certificates"].check(REGISTRY["supplier_certificates"].spec["example"])
nc = e4.call("supplier_certificates", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"})
assert nc["ok"] and nc["un38_3"] == "expired" and nc["item"] == {"item_code": "BAT-500", "needs_un38_3": True, "supplier_qualifies": False}, nc
assert nc["certificates"][0]["days_left"] == -26 and "§6.2" in nc["next_step"], nc
vc = e4.call("supplier_certificates", {"supplier_code": "vc-ein-0042", "item_code": "BAT-500"})   # code case does not matter
assert vc["ok"] and vc["un38_3"] == "valid" and vc["item"]["supplier_qualifies"] and "next_step" not in vc, vc
pb = e4.call("supplier_certificates", {"supplier_code": "PB-MAN-0017", "item_code": "BRK-PAD-01"})  # no cert, none needed
assert pb["un38_3"] == "none" and pb["item"]["supplier_qualifies"] and pb["certificates"] == [], pb
bad = e4.call("supplier_certificates", {"supplier_code": "XX-NOPE-0001"})
assert bad["ok"] is False and bad["ledgerline_code"] == "ERR-SUP-0030" and "find_supplier" in bad["next_step"], bad
bad = e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-5000"})
assert bad["ok"] is False and bad["ledgerline_code"] == "ERR-ITM-0010", bad
assert e4.call("supplier_certificates", {})["ok"] is False                                         # required
assert e4.call("supplier_certificates", {"supplier_code": 42})["ok"] is False                      # type
assert e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "limit": 0})["ok"] is False
for i in range(45):                                                                                   # pagination
    erp4.x("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", "VC-EIN-0042", "ISO9001", f"ISO-{i:02d}", "2027-01-01", "LMORENO", "2026-01-01")
p1 = e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042"})
p2 = e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "cursor": p1["next_cursor"]})
p3 = e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "cursor": p2["next_cursor"]})
assert p1["total"] == 46 and len(p1["certificates"]) == 20 and p3["next_cursor"] is None and \
    len({c["doc_ref"] for c in p1["certificates"] + p2["certificates"] + p3["certificates"]}) == 46, (p1["total"], p3)
assert e4.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "cert_type": "UN 38.3"})["total"] == 1
import jsonschema
for r in (nc, vc, pb, p1, p3):
    jsonschema.validate(r, REGISTRY["supplier_certificates"].spec["output_schema"])
print("SUPPLIER_CERTIFICATES OK")

# ---- Lecture 4: idempotency and lost replies (the production-grade fix)
def count(e, t):
    return e.q1(f"SELECT count(*) n FROM {t}")["n"]
erp5 = ERP(); k5 = Toolbox(erp5, "ECLARKE")
base = {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "confirm": True}
n0 = count(erp5, "pr_hdr")
a = k5.call("create_purchase_request", {**base, "need_by": "9 Nov 2026"})
b = k5.call("create_purchase_request", {**base, "need_by": "2026-11-09"})       # the same request, the date spelled differently
assert a["ok"] and b.get("already_done") and count(erp5, "pr_hdr") == n0 + 1, (a, b)
assert k5.call("create_purchase_request", {**base, "need_by": "next Monday"})["ok"] is False   # refused at the door
assert k5.call("create_purchase_request", {**base, "need_by": " "})["ok"] is False
erp6, ctx = None, None
erp6 = ERP(); e6, d6, a6 = Toolbox(erp6, "ECLARKE"), Toolbox(erp6, "DOKAFOR"), Toolbox(erp6, "ATANAKA")
pr6 = e6.call("create_purchase_request", {**base, "need_by": "2026-11-09"})
erp6.inject("pr_approve", "timeout_after_commit")
ap6 = d6.call("approve_purchase_request", {"request_no": pr6["request_no"], "decision": "approve"})
assert ap6["ok"] and ap6["status_code"] == "AP", ap6                              # a lost reply is read back, not an error
po6 = e6.call("create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": pr6["request_no"], "confirm": True})
e6.call("release_purchase_order", {"po_no": po6["po_no"]})
erp6.inject("grn_save", "timeout_after_commit")
g6 = a6.call("receive_goods", {"po_no": po6["po_no"], "quantity": 500, "confirm": True})
assert g6["ok"] and g6["balance"] == 1500 and count(erp6, "grn_hdr") == 1, g6     # found, not posted twice
m0 = count(erp6, "ntf_queue")
erp6.inject("ntf_send", "timeout_after_commit")
s6 = e6.call("send_message", {"to": "@daniel", "text": "PO released"})
assert s6["ok"] and count(erp6, "ntf_queue") == m0 + 1, s6
erp6.inject("ntf_send", "error_before")
assert e6.call("send_message", {"to": "@daniel", "text": "again"})["ok"] is False and count(erp6, "ntf_queue") == m0 + 1
print("IDEMPOTENCY OK")

# ---- Lecture 4: the MCP definition and result fields
c = MCPClient(build_toolbox_server(ERP(), "ECLARKE", names=ALL))
defs = {t.name: t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in c.list_tools()}
assert len(defs) == 16 and all(d.get("title") and d.get("outputSchema") and d["annotations"].get("readOnlyHint") is not None
                               and d["_meta"]["ledgerline/version"] for d in defs.values()), defs["check_stock"]
assert defs["receive_goods"]["annotations"]["idempotentHint"] is False and defs["check_stock"]["annotations"]["readOnlyHint"]
ok_res = c.call_tool("check_stock", {"item_code": "BAT-500"}).model_dump(mode="json", by_alias=True, exclude_none=True)
err_res = c.call_tool("check_stock", {"item_code": "BAT-5000"}).model_dump(mode="json", by_alias=True, exclude_none=True)
assert ok_res["structuredContent"]["free_total"] == 6600 and not ok_res.get("isError"), ok_res
assert err_res["isError"] is True and err_res["structuredContent"]["ledgerline_code"] == "ERR-ITM-0010", err_res
mt = MCPClientTools(c)
assert json.loads(mt.call("check_stock", {"item_code": "BAT-5000"}))["ledgerline_code"] == "ERR-ITM-0010"   # passed through as is
c.close()
print("MCP FIELDS OK")
