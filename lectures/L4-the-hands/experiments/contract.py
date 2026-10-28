"""Lecture 4: the tool contract, shown on Rasoi's real sandbox, with no model in the loop.

Every example the deck shows for the contract comes from this run:
  1 typed inputs checked once         wrong type, missing field, bad enum, unknown argument
  2 errors that say what to do next   release an unapproved order, approve your own request
  3 preview before a write            Kavita's PR previewed: value, approver, nothing saved
  4 idempotency keys                  po_save times out AFTER saving (erp.inject); raw retry vs the toolbox
  5 receipts read back                the silent Draft on PRD-05: Bahi says SAVED, the receipt says DRAFT
  6 permissions = the user's session  approve PO/2026/01179 as Kavita vs as SVC_AGENT
plus the whole P2P chain through the toolbox (PR -> approve -> PO -> release -> GRN), and the service inventory
(41 raw services vs 15 tools). Writes logs/contract.json.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L4-the-hands/experiments/contract.py
"""
import json
import pathlib

from bahi.agent.tools import RawServiceTools
from bahi.erp.engine import ERP, SERVICES, ServiceTimeout
from bahi.toolbox import SPECS, Toolbox

LOG = pathlib.Path(__file__).resolve().parent / "logs"
LOG.mkdir(exist_ok=True)
out = {}
PR_ARGS = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"}


def show(tag, r):
    print(f"{tag:34s}", json.dumps(r, default=str)[:300])
    return r


# ---------------------------------------------------------------- inventory
erp = ERP()
kav = Toolbox(erp, "KJOSHI")
raw = RawServiceTools(erp.session("KJOSHI"))
out["inventory"] = {
    "raw_services": len(raw.schemas()),
    "raw_reads": sum(1 for s in SERVICES.values() if s.kind == "read"),
    "raw_writes": sum(1 for s in SERVICES.values() if s.kind == "write"),
    "toolbox_tools": len(kav.names),
    "toolbox_writes": sum(1 for n in kav.names if SPECS[n].writes),
    "tools": [{"name": n, "category": SPECS[n].spec["category"], "writes": SPECS[n].writes,
               "services": SPECS[n].spec["services"], "json_chars": len(json.dumps(SPECS[n].schema())),
               "py_lines": len(SPECS[n].source.splitlines())} for n in kav.names],
    "raw_names": [s["function"]["name"] for s in raw.schemas()],
    "raw_example": next(s for s in raw.schemas() if s["function"]["name"] == "po_save"),
    "raw_stk_query": next(s for s in raw.schemas() if s["function"]["name"] == "stk_query"),
    "toolbox_check_stock": SPECS["check_stock"].schema(),
    "create_pr_tool_json": SPECS["create_purchase_request"].spec,
}
print("inventory:", out["inventory"]["raw_services"], "raw services,", out["inventory"]["toolbox_tools"], "tools")

# ---------------------------------------------------------------- check_stock, by hand
out["check_stock"] = show("check_stock", kav.call("check_stock", {"item_code": "GSK-SIL-05L"}))
c0 = len(erp.calls)
kav.call("check_stock", {"item_code": "GSK-SIL-05L"})
out["check_stock_services"] = [{"svc": c.svc, "payload": c.payload, "rc": c.rc} for c in erp.calls[c0:]]

# ---------------------------------------------------------------- 1 typed inputs
out["types"] = {
    "wrong_type": show("wrong type", kav.call("check_stock", {"item_code": 42})),
    "quantity_as_text": show("quantity as '20000'", SPECS["create_purchase_request"].check({**PR_ARGS, "quantity": "20000"})),
    "missing": show("missing need_by", kav.call("create_purchase_request", {k: v for k, v in PR_ARGS.items() if k != "need_by"})),
    "bad_enum": show("bad enum", kav.call("approve_purchase_request", {"request_no": "PR/2026/04417", "decision": "yes"})),
    "unknown_arg": show("unknown argument", kav.call("check_stock", {"item_code": "GSK-SIL-05L", "warehouse": "PUN"})),
}
# the same mistakes sent straight to Bahi's raw service
out["types_raw"] = {
    "stk_query_no_whs": show("raw stk_query no whs_cd", raw.call("stk_query", {"itm_cd": "GSK-SIL-05L"})),
    "pr_save_qty_text": show("raw pr_save qty 'twenty k'", raw.call("pr_save", {"cc_cd": "PRD-07", "need_dt": "2026-11-09",
                                                                               "itm_cd": "GSK-SIL-05L", "qty": "twenty thousand", "est_rate": 11.4})),
}

# ---------------------------------------------------------------- 2 errors that say what to do next
out["errors"] = {
    "release_unapproved": show("release PA order", kav.call("release_purchase_order", {"po_no": "PO/2026/01179"})),
    "release_unapproved_raw": show("raw po_release", raw.call("po_release", {"po_no": "PO/2026/01179"})),
    "item_typo": show("check_stock bad code", kav.call("check_stock", {"item_code": "GSK-SIL-5L"})),
    "item_typo_raw": show("raw itm_get bad code", raw.call("itm_get", {"itm_cd": "GSK-SIL-5L"})),
}

# ---------------------------------------------------------------- 3 preview, then confirm
n_pr = len(erp.q("SELECT * FROM pr_hdr"))
pv = show("PR preview", kav.call("create_purchase_request", PR_ARGS))
out["preview"] = {"result": pv, "pr_rows_before": n_pr, "pr_rows_after": len(erp.q("SELECT * FROM pr_hdr"))}
pr = show("PR confirm", kav.call("create_purchase_request", {**PR_ARGS, "confirm": True}))
out["confirm"] = pr
out["self_approve"] = show("Kavita approves her own PR", kav.call("approve_purchase_request",
                                                              {"request_no": pr["request_no"], "decision": "approve"}))
rohit = Toolbox(erp, "RMEHTA")
out["rohit_inbox"] = show("Rohit's approvals", rohit.call("list_my_approvals", {}))
out["rohit_approves"] = show("Rohit approves", rohit.call("approve_purchase_request",
                                                         {"request_no": pr["request_no"], "decision": "approve"}))
out["again_same_pr"] = show("same PR asked again", kav.call("create_purchase_request", {**PR_ARGS, "confirm": True}))

# ---------------------------------------------------------------- 4 idempotency under an injected timeout
PO_ARGS = {"supplier_code": "DP-RJK-0042", "request_no": pr["request_no"]}
out["po_preview"] = show("PO preview", kav.call("create_purchase_order", PO_ARGS))
erp.inject("po_save", "timeout_after_commit")  # Bahi saves the order, then the reply is lost
c0 = len(erp.calls)
po = show("PO confirm, reply lost", kav.call("create_purchase_order", {**PO_ARGS, "confirm": True}))
out["idem_first"] = {"result": po, "services": [{"svc": c.svc, "rc": c.rc, "timed_out": c.timed_out,
                                                  "payload": {k: v for k, v in c.payload.items() if k in ("client_ref", "po_no", "pr_no")}}
                                                 for c in erp.calls[c0:]]}
retry = show("PO confirm, retried", kav.call("create_purchase_order", {**PO_ARGS, "confirm": True}))
out["idem_retry"] = retry
out["idem_orders_for_pr"] = [dict(o) for o in erp.q("SELECT po_no,status,client_ref,gross_value FROM po_hdr WHERE pr_no=?", pr["request_no"])]
print("orders for the PR after a lost reply and a retry:", len(out["idem_orders_for_pr"]))

# the same lost reply with raw services and a naive retry
erp2 = ERP()
k2 = erp2.session("KJOSHI")
Toolbox(erp2, "KJOSHI").call("create_purchase_request", {**PR_ARGS, "confirm": True})
Toolbox(erp2, "RMEHTA").call("approve_purchase_request", {"request_no": "PR/2026/04417", "decision": "approve"})
raw_saves = []
for attempt in (1, 2):
    f = k2.call("po_fetch", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", pr_no="PR/2026/04417")["data"]
    if attempt == 1:
        erp2.inject("po_save", "timeout_after_commit")
    try:
        r = k2.call("po_save", po_type="STD", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty=20000, rate=11.90,
                    tax_cd="GST18-INTER", cc_cd="PRD-07", need_dt="2026-11-09", fetch_tok=f["fetch_tok"], pr_no="PR/2026/04417")
        raw_saves.append({"attempt": attempt, "reply": r})
    except ServiceTimeout as e:
        raw_saves.append({"attempt": attempt, "reply": f"TIMEOUT: {e}"})
out["idem_raw"] = {"attempts": raw_saves,
                   "orders": [dict(o) for o in erp2.q("SELECT po_no,status,gross_value FROM po_hdr WHERE pr_no='PR/2026/04417'")]}
print("raw retry orders:", out["idem_raw"]["orders"])

# a direct order (no request, under Rs 50,000): 3,000 whistles from Sahyadri Valves on PRD-07
D_ARGS = {"supplier_code": "SV-PUN-0017", "item_code": "WHS-STD-01", "quantity": 3000, "cost_centre": "PRD-07",
          "need_by": "2026-11-04"}
erp6 = ERP()
t6 = Toolbox(erp6, "KJOSHI")
erp6.inject("po_save", "timeout_after_commit")
d1 = show("direct PO, reply lost", t6.call("create_purchase_order", {**D_ARGS, "confirm": True}))
d2 = show("direct PO, retried", t6.call("create_purchase_order", {**D_ARGS, "confirm": True}))
out["idem_direct"] = {"first": d1, "retry": d2, "orders": [dict(o) for o in erp6.q(
    "SELECT po_no,status,client_ref,gross_value FROM po_hdr WHERE po_no>'PO/2026/01181'")]}
erp7 = ERP()
k7 = erp7.session("KJOSHI")
raw_direct = []
for attempt in (1, 2):
    f = k7.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01")["data"]
    if attempt == 1:
        erp7.inject("po_save", "timeout_after_commit")
    try:
        r = k7.call("po_save", po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.80,
                    tax_cd="GST18-INTRA", cc_cd="PRD-07", need_dt="2026-11-04", fetch_tok=f["fetch_tok"])
        raw_direct.append({"attempt": attempt, "reply": r})
    except ServiceTimeout as e:
        raw_direct.append({"attempt": attempt, "reply": f"TIMEOUT: {e}"})
out["idem_direct_raw"] = {"attempts": raw_direct, "orders": [dict(o) for o in erp7.q(
    "SELECT po_no,status,gross_value FROM po_hdr WHERE po_no>'PO/2026/01181'")]}
print("direct: toolbox orders", len(out["idem_direct"]["orders"]), "| raw orders", out["idem_direct_raw"]["orders"])

# the same lost reply on the purchase request's own save (pr_save), then a retry
erp3 = ERP()
k3 = Toolbox(erp3, "KJOSHI")
erp3.inject("pr_save", "timeout_after_commit")
out["idem_pr"] = {"first": show("PR confirm, pr_save reply lost", k3.call("create_purchase_request", {**PR_ARGS, "confirm": True})),
                  "retry": show("PR retried", k3.call("create_purchase_request", {**PR_ARGS, "confirm": True}))}
out["idem_pr"]["requests"] = [dict(r) for r in erp3.q("SELECT pr_no,status FROM pr_hdr WHERE raised_by='KJOSHI' AND pr_no>='PR/2026/04417'")]
print("PR after a lost pr_save reply:", out["idem_pr"]["requests"])

# ---------------------------------------------------------------- the rest of the chain, and the receipt
rel = show("release", kav.call("release_purchase_order", {"po_no": po.get("po_no") or retry.get("po_no")}))
out["release"] = rel
neha = Toolbox(erp, "NDESAI")
out["grn_preview"] = show("GRN preview", neha.call("receive_goods", {"po_no": rel["po_no"], "quantity": 12000}))
out["grn1"] = show("GRN 12,000", neha.call("receive_goods", {"po_no": rel["po_no"], "quantity": 12000, "confirm": True}))
out["grn2"] = show("GRN 8,000", neha.call("receive_goods", {"po_no": rel["po_no"], "quantity": 8000, "confirm": True}))
out["status_after"] = show("order_status", kav.call("order_status", {"po_no": rel["po_no"]}))
out["stock_after"] = show("check_stock after", kav.call("check_stock", {"item_code": "GSK-SIL-05L"}))

# ---------------------------------------------------------------- 5 receipts: the silent Draft
erp4 = ERP()
k4 = erp4.session("KJOSHI")
f = k4.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01")["data"]
raw_draft = k4.call("po_save", po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=1000, rate=6.80,
                    tax_cd="GST18-INTRA", cc_cd="PRD-05", need_dt="2026-11-04", fetch_tok=f["fetch_tok"])
out["draft_raw"] = raw_draft
t4 = Toolbox(erp4, "KJOSHI")
dargs = {"supplier_code": "SV-PUN-0017", "item_code": "WHS-STD-01", "quantity": 1500, "cost_centre": "PRD-05", "need_by": "2026-11-04"}
out["draft_preview"] = show("toolbox preview on PRD-05", t4.call("create_purchase_order", dargs))
out["draft_receipt"] = show("toolbox confirm on PRD-05", t4.call("create_purchase_order", {**dargs, "confirm": True}))

# ---------------------------------------------------------------- 6 permissions = the user's own session
erp5 = ERP()
out["perm"] = {
    "kavita": show("approve 01179 as KJOSHI", Toolbox(erp5, "KJOSHI").call("approve_purchase_order", {"po_no": "PO/2026/01179"})),
    "svc_agent": show("approve 01179 as SVC_AGENT", Toolbox(erp5, "SVC_AGENT").call("approve_purchase_order", {"po_no": "PO/2026/01179"})),
    "po_01179": dict(erp5.q1("SELECT po_no,status,gross_value,created_by,approved_by FROM po_hdr WHERE po_no='PO/2026/01179'")),
    "kavita_user": dict(erp5.user("KJOSHI")),
}
for k in ("password", "pwd", "pass_hash"):
    out["perm"]["kavita_user"].pop(k, None)

(LOG / "contract.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("wrote logs/contract.json")
