"""Finance · payables: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt
import re

from ...erp.engine import BahiError, proc

TOLERANCE = 0.02  # AP Policy §4.1: rate up to 2% above the order rate passes the match


def norm_no(s: str) -> str:
    """'4471-R', '4471/R', ' 4471 ' all become '4471' (how Bahi spots a resent invoice)."""
    s = (s or "").upper().strip()
    s = re.sub(r"[\s\-/]*(R|REV|A|B|DUP|COPY)$", "", s)
    return re.sub(r"[^0-9A-Z]", "", s)


@proc("sp_ap_sup_chk")
def sup_chk(erp, sup_cd: str) -> dict:
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", sup_cd)
    if not sup:
        raise BahiError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    if sup["status"] != "ACTIVE":
        raise BahiError("ERR-AP-0031", "SUPPLIER NOT ACTIVE")
    return sup


@proc("sp_ap_dup_chk")
def dup_chk(erp, sup_cd: str, sup_inv_no: str, gross: float, po_no: str | None) -> str | None:
    """Exact same number for the same supplier is refused. A near match (4471-R, or same PO and same amount)
    is accepted but held as H-DUP. Returns the near match's ap_no, or None."""
    live = erp.q("SELECT * FROM ap_inv WHERE sup_cd=? AND status NOT IN ('CN','RJ')", sup_cd)
    for r in live:
        if r["sup_inv_no"].upper().strip() == sup_inv_no.upper().strip():
            raise BahiError("ERR-AP-0118", f"INVOICE NO ALREADY ENTERED ({r['ap_no']})")
    for r in live:
        if norm_no(r["sup_inv_no"]) == norm_no(sup_inv_no) or (po_no and r["po_no"] == po_no and abs(r["gross"] - gross) < 1):
            return r["ap_no"]
    return None


@proc("sp_ap_match3")
def match3(erp, sup_cd: str, po_no: str, qty: int, rate: float) -> dict:
    """Variant 1, the three-way match: order (rate), goods receipt (accepted qty), invoice."""
    po = erp.q1("SELECT h.*, l.rate po_rate, l.qty po_qty, l.itm_cd FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no "
                "WHERE h.po_no=?", po_no)
    if not po:
        raise BahiError("ERR-PO-0001", "PO NOT FOUND")
    if po["sup_cd"] != sup_cd:
        raise BahiError("ERR-AP-0205", f"PO NOT OF THIS SUPPLIER ({po['sup_cd']})")
    if po["status"] not in ("RL", "CL"):
        raise BahiError("ERR-AP-0206", f"PO NOT RELEASED ({po['status']})")
    acc = erp.q1("SELECT coalesce(sum(qty_acc),0) n FROM ap_grn WHERE po_no=?", po_no)["n"]
    billed = erp.q1("SELECT coalesce(sum(qty),0) n FROM ap_inv WHERE po_no=? AND status NOT IN ('CN','RJ')", po_no)["n"]
    open_qty = acc - billed
    var = round((rate - po["po_rate"]) / po["po_rate"], 4)
    holds = []
    if acc == 0:
        holds.append(("H-GRN", f"NO GRN FOR {po_no}"))
    elif qty > open_qty:
        holds.append(("H-QTY", f"QTY {qty} VS OPEN {open_qty}"))
    if var > TOLERANCE:
        holds.append(("H-PRC", f"RATE {rate:.2f} VS PO {po['po_rate']:.2f} (+{var * 100:.2f}%)"))
    return {"po_rate": po["po_rate"], "grn_acc": acc, "billed": billed, "open_qty": open_qty, "var_pct": round(var * 100, 2),
            "holds": holds, "cc_cd": po["cc_cd"]}


@proc("sp_ap_match2")
def match2(erp, cc_cd: str, gross: float) -> dict:
    """Variant 2, the two-way check for a non-PO invoice: an open cost centre with budget, and its owner approves."""
    state = erp.sp("sp_budget_chk", cc_cd, gross)  # shared engine
    if state == "CLOSED":
        raise BahiError("ERR-AP-0213", f"COST CENTRE {cc_cd} CLOSED")
    owner = erp.q1("SELECT owner FROM cost_centre WHERE cc_cd=?", cc_cd)["owner"]
    return {"cc_state": state, "approver": owner, "holds": []}


@proc("sp_ap_due_dt")
def due_dt(erp, sup: dict, inv_dt: str) -> str:
    days = erp.q1("SELECT days FROM pay_term WHERE pt_cd=?", sup["pt_cd"])["days"]
    return (dt.date.fromisoformat(inv_dt) + dt.timedelta(days=days)).isoformat()


@proc("sp_ap_hold_put")
def hold_put(erp, ap_no: str, holds: list):
    for cd, detail in holds:
        erp.x("INSERT INTO ap_hold_log(ap_no,hold_cd,detail,put_on) VALUES (?,?,?,?)", ap_no, cd, detail, erp.now())


@proc("sp_ap_hold_auth")
def hold_auth(erp, user: str, hold_cd: str) -> bool:
    h = erp.q1("SELECT * FROM ap_hold WHERE hold_cd=?", hold_cd)
    if not h:
        raise BahiError("ERR-AP-0301", "INVALID HOLD CD")
    role = erp.user(user)["role_cd"]
    return role in h["release_role"].split(",") or role == "SYS-ADMIN"  # the legacy superuser passes every check


@proc("sp_ap_post")
def post(erp, ap_no: str):
    """Cascade 1: a clear invoice is posted. The supplier's ledger is credited and the GST becomes input credit."""
    i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", ap_no)
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", i["sup_cd"])
    erp.x("UPDATE ap_inv SET status='PO', hold_cd=NULL WHERE ap_no=?", ap_no)
    erp.x("INSERT INTO ap_ledger(sup_cd,dt,ref,dr,cr,narr) VALUES (?,?,?,?,?,?)", i["sup_cd"], erp.today, ap_no, 0,
          i["gross"], f"Invoice {i['sup_inv_no']}")
    erp.x("INSERT INTO ap_gst(ap_no,gstin,tax_cd,itc_amt,period,status) VALUES (?,?,?,?,?,?)", ap_no, sup["gstin"],
          i["tax_cd"], i["tax"], erp.today[:7], "OPEN")


@proc("sp_ap_route")
def route(erp, doc_type: str, doc_no: str, approver: str, requester: str, what: str):
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on,comment) VALUES (?,?,?,?,?,?,?)",
          doc_type, doc_no, approver, "PENDING", requester, erp.now(), what)
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(approver)["email"], f"{doc_no} awaiting you", what)


@proc("sp_ap_pay_exec")
def pay_exec(erp, pay: dict):
    """Cascade 2: the payment run pays the supplier: ledger debited, invoice paid, remittance advice mailed."""
    i = erp.q1("SELECT * FROM ap_inv WHERE ap_no=?", pay["ap_no"])
    erp.x("UPDATE ap_pay SET status='PD', paid_on=? WHERE pay_no=?", erp.now(), pay["pay_no"])
    erp.x("UPDATE ap_inv SET status='PD' WHERE ap_no=?", pay["ap_no"])
    erp.x("INSERT INTO ap_ledger(sup_cd,dt,ref,dr,cr,narr) VALUES (?,?,?,?,?,?)", i["sup_cd"], erp.today, pay["pay_no"],
          pay["amount"], 0, f"Payment run {pay['pay_dt']}")
    erp.sp("sp_ntf_enqueue", "EMAIL", f"accounts@{i['sup_cd'].lower()}.example", f"Remittance {pay['pay_no']}",
           f"Paid {pay['amount']:,.2f} against your invoice {i['sup_inv_no']}.")
