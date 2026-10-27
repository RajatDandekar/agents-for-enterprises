"""Inventory · transfers: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import re

from ...erp.engine import BahiError, proc

EWB_LIMIT = 50000  # consignment value incl. GST above which an e-way bill is needed (E-way Bill Note §2)


@proc("sp_tr_whs")
def whs(erp, whs_cd: str) -> dict:
    w = erp.q1("SELECT * FROM warehouse WHERE whs_cd=?", whs_cd)
    if not w:
        raise BahiError("ERR-TR-0101", f"WHS {whs_cd} NOT FOUND")
    return w


@proc("sp_tr_move_type")
def move_type(erp, from_whs: str, to_whs: str) -> str:
    """The two variants: INT = inside one unit (no gate pass), IUT = between units (gate pass, maybe e-way bill)."""
    if from_whs == to_whs:
        raise BahiError("ERR-TR-0102", "FROM WHS = TO WHS")
    a, b = erp.sp("sp_tr_whs", from_whs), erp.sp("sp_tr_whs", to_whs)
    return "INT" if a["ou_cd"] == b["ou_cd"] else "IUT"


@proc("sp_tr_free_qty")
def free_qty(erp, itm_cd: str, whs_cd: str) -> dict:
    """Free stock = on hand - allocated - QC hold. QC-held stock never moves."""
    s = erp.q1("SELECT * FROM stock WHERE itm_cd=? AND whs_cd=?", itm_cd, whs_cd)
    if not s:
        raise BahiError("ERR-TR-0201", "NO STOCK RECORD")
    qc = erp.q1("SELECT coalesce(sum(qty),0) q FROM tr_qc_hold WHERE itm_cd=? AND whs_cd=? AND status='HOLD'",
                itm_cd, whs_cd)["q"]
    return {"on_hand": s["on_hand"], "allocated": s["allocated"], "qc_hold": qc,
            "free": max(0, s["on_hand"] - s["allocated"] - qc)}


@proc("sp_tr_value")
def value(erp, itm_cd: str, qty: int) -> tuple[float, float]:
    """Consignment value at standard rate, with GST from the shared tax engine (sp_tax_compute)."""
    r = erp.q1("SELECT rate FROM tr_std_rate WHERE itm_cd=?", itm_cd)
    if not r:
        raise BahiError("ERR-TR-0301", "NO STD RATE FOR ITEM")
    basic = round(qty * r["rate"], 2)
    _, gross = erp.sp("sp_tax_compute", basic, "GST18-INTRA")
    return basic, gross


@proc("sp_tr_reserve")
def reserve(erp, itm_cd: str, whs_cd: str, qty: int):
    """Book stock for a note so two notes cannot promise the same pieces. Negative qty releases it."""
    erp.x("UPDATE stock SET allocated=allocated+? WHERE itm_cd=? AND whs_cd=?", qty, itm_cd, whs_cd)


@proc("sp_tr_route_appr")
def route_appr(erp, tn_no: str, user: str, gross: float, fwd_to: str | None) -> str:
    """Night moves need approval. Bahi uses the shared approval engine (first manager whose limit covers the
    value) unless FWD TO names someone. The gate-pass policy wants the plant head; Bahi does not know that."""
    if fwd_to:
        if not erp.user(fwd_to):
            raise BahiError("ERR-TR-0410", "FWD TO USER NOT FOUND")
        erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
              "TRN", tn_no, fwd_to, "PENDING", user, erp.now())
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(fwd_to)["email"], f"{tn_no} awaiting your approval",
               f"Night transfer {tn_no} raised by {user}")
        return fwd_to
    return erp.sp("sp_appr_route", "TRN", tn_no, user, gross)


@proc("sp_tr_ewb_chk")
def ewb_chk(erp, gross: float, ewb_no: str | None):
    """Above Rs 50,000 the gate needs an e-way bill number. Bahi checks only that it has 12 digits."""
    if gross <= EWB_LIMIT:
        return
    if not ewb_no:
        raise BahiError("ERR-TR-0610", "EWB NO MANDATORY ABOVE 50000")
    if not re.fullmatch(r"\d{12}", ewb_no):
        raise BahiError("ERR-TR-0611", "EWB NO MUST BE 12 DIGITS")


@proc("sp_tr_stock_row")
def stock_row(erp, itm_cd: str, whs_cd: str):
    if not erp.q1("SELECT 1 FROM stock WHERE itm_cd=? AND whs_cd=?", itm_cd, whs_cd):
        erp.x("INSERT INTO stock VALUES (?,?,0,0,0)", itm_cd, whs_cd)


@proc("sp_tr_stock_out")
def stock_out(erp, note: dict, ref: str):
    """Cascade 1: the goods leave the issuing store. On hand and the booking both come down; the note is in transit."""
    erp.x("UPDATE stock SET on_hand=on_hand-?, allocated=allocated-? WHERE itm_cd=? AND whs_cd=?",
          note["qty"], note["qty"], note["itm_cd"], note["from_whs"])
    erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
          note["itm_cd"], note["from_whs"], erp.today, "TRF-OUT", -note["qty"], ref)


@proc("sp_tr_stock_in")
def stock_in(erp, note: dict, qty: int, ref: str):
    """Cascade 2: the goods are counted in at the receiving store, and the requester is told."""
    erp.sp("sp_tr_stock_row", note["itm_cd"], note["to_whs"])
    erp.x("UPDATE stock SET on_hand=on_hand+? WHERE itm_cd=? AND whs_cd=?", qty, note["itm_cd"], note["to_whs"])
    erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
          note["itm_cd"], note["to_whs"], erp.today, "TRF-IN", qty, ref)
    who = erp.user(note["created_by"])
    if who:
        erp.sp("sp_ntf_enqueue", "EMAIL", who["email"], f"{note['tn_no']} received",
               f"{qty} x {note['itm_cd']} received at {note['to_whs']}")


@proc("sp_tr_status_set")
def status_set(erp, tn_no: str, status: str, approver: str | None = None):
    erp.x("UPDATE tr_note SET status=? WHERE tn_no=?", status, tn_no)
    if approver:
        erp.x("UPDATE tr_note SET approver=? WHERE tn_no=?", approver, tn_no)
