"""Purchasing · amend PO: the stored procedures. Services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import LedgerlineError, proc

CUT_LIMIT = 0.20   # a cut of more than 20% needs the original approver again (PO Amendment Policy §4.1)
MOVE_LIMIT = 5     # so does moving the delivery date by more than 5 days (§4.2)


@proc("sp_pa_po_open")
def po_open(erp, po_no: str) -> dict:
    """A released order with its line and its received quantity. Amendments apply only to released orders."""
    h = erp.q1("SELECT h.*, l.itm_cd, l.qty, l.rate FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE h.po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] != "RL":
        raise LedgerlineError("ERR-PA-0102", f"PO NOT RELEASED ({h['status']}), USE PUR-POM-06")
    h["rcvd"] = erp.q1("SELECT coalesce(sum(rcvd_qty),0) n FROM pa_sched WHERE po_no=? AND status IN ('OP','RC','CN')",
                       po_no)["n"]
    h["open_lines"] = erp.q("SELECT sl_no,dlv_dt,qty,rcvd_qty FROM pa_sched WHERE po_no=? AND status='OP' ORDER BY sl_no",
                            po_no)
    return h


@proc("sp_pa_open_amd_chk")
def open_amd_chk(erp, po_no: str, but: str | None = None):
    r = erp.q1("SELECT amd_no FROM pa_amd WHERE po_no=? AND status IN ('HD','PA','AP') AND amd_no<>?", po_no, but or "")
    if r:
        raise LedgerlineError("ERR-PA-0105", f"OPEN AMENDMENT {r['amd_no']} EXISTS")


@proc("sp_pa_type_rule")
def type_rule(erp, amd_type: str, h: dict, qty: int | None, need_dt: str | None, lines: list) -> tuple[int, str]:
    """The two variants. REV changes quantity and/or dates of a released order. SCL short-closes it: the
    undelivered balance is cancelled, the quantity becomes what was received, and nothing else may change."""
    if amd_type == "SCL":
        if need_dt:
            raise LedgerlineError("ERR-PA-0611", "SCL CANNOT CHANGE DATE")
        if lines:
            raise LedgerlineError("ERR-PA-0613", "SCL CANNOT HAVE SCHEDULE")
        if qty is not None and qty != h["rcvd"]:
            raise LedgerlineError("ERR-PA-0612", f"SCL QTY MUST BE RCVD QTY ({h['rcvd']})")
        if h["rcvd"] == 0:
            raise LedgerlineError("ERR-PA-0614", "NOTHING RECEIVED, CANCEL PO INSTEAD")
        return h["rcvd"], h["need_dt"]
    if amd_type != "REV":
        raise LedgerlineError("ERR-PA-0601", "AMD TYPE MUST BE REV/SCL")
    if qty is None and not need_dt and not lines:
        raise LedgerlineError("ERR-PA-0602", "NOTHING TO AMEND")
    return (h["qty"] if qty is None else qty), (need_dt or h["need_dt"])


@proc("sp_pa_qty_chk")
def qty_chk(erp, new_qty: int, rcvd: int):
    if new_qty <= 0:
        raise LedgerlineError("ERR-PA-0301", "QTY MUST BE > 0")
    if new_qty < rcvd:
        raise LedgerlineError("ERR-PA-0310", f"QTY BELOW RCVD QTY ({rcvd})")


@proc("sp_pa_lead_chk")
def lead_chk(erp, sup_cd: str, dates: list[str]):
    """A delivery date may not be nearer than the supplier's lead time. (Sundays and holidays are NOT checked.)"""
    lt = erp.q1("SELECT lead_days FROM pa_lead WHERE sup_cd=?", sup_cd)
    first = (dt.date.fromisoformat(erp.today) + dt.timedelta(days=lt["lead_days"] if lt else 0)).isoformat()
    for d in dates:
        if d < first:
            raise LedgerlineError("ERR-PA-0320", f"DLV DT WITHIN SUPPLIER LEAD TIME (EARLIEST {first})")


@proc("sp_pa_sched_propose")
def sched_propose(erp, amd_no: str, po_no: str, lines: list[tuple]):
    """The schedule the revision will carry. With no lines typed, Ledgerline copies the current open lines unchanged."""
    erp.x("DELETE FROM pa_sched WHERE amd_no=? AND status='PR'", amd_no)
    if not lines:
        lines = [(r["dlv_dt"], r["qty"] - r["rcvd_qty"]) for r in
                 erp.q("SELECT * FROM pa_sched WHERE po_no=? AND status='OP' ORDER BY sl_no", po_no)]
    n = erp.q1("SELECT coalesce(max(sl_no),0) n FROM pa_sched WHERE po_no=?", po_no)["n"]
    for i, (d, q) in enumerate(lines, 1):
        erp.x("INSERT INTO pa_sched VALUES (?,?,?,?,?,?,?)", po_no, n + i, d, q, 0, "PR", amd_no)


@proc("sp_pa_sched_match")
def sched_match(erp, amd: dict, rcvd: int) -> bool:
    """The schedule must add up: received + new open lines = new quantity, and the last line falls on the need date."""
    rows = erp.q("SELECT dlv_dt, qty FROM pa_sched WHERE amd_no=? AND status='PR'", amd["amd_no"])
    total = rcvd + sum(r["qty"] for r in rows)
    last = max((r["dlv_dt"] for r in rows), default=None)
    return total == amd["new_qty"] and (not rows or last == amd["new_dt"])


@proc("sp_pa_reappr_rule")
def reappr_rule(erp, amd: dict, h: dict, raiser: str) -> tuple[str | None, str]:
    """Who must approve this amendment again? Returns (approver or None, why)."""
    if amd["new_gross"] > amd["old_gross"] and amd["new_gross"] > erp.user(raiser)["appr_limit"]:
        return "LIMIT", "value up, above raiser's limit"
    cut = (amd["old_qty"] - amd["new_qty"]) / amd["old_qty"]
    moved = abs((dt.date.fromisoformat(amd["new_dt"]) - dt.date.fromisoformat(amd["old_dt"])).days)
    if cut > CUT_LIMIT or moved > MOVE_LIMIT:
        orig = h["approved_by"]
        if not orig or orig in (raiser, "SVC_AGENT"):
            orig = erp.user(raiser)["manager_id"]
        return orig, f"cut {cut:.0%}, moved {moved} days"
    return None, "within rules"


@proc("sp_pa_route")
def route(erp, amd: dict, approver: str, raiser: str) -> str:
    """Send the amendment for approval: by value through the shared engine sp_appr_route, otherwise to the
    original approver."""
    if approver == "LIMIT":
        return erp.sp("sp_appr_route", "PA-AMD", amd["amd_no"], raiser, amd["new_gross"])
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
          "PA-AMD", amd["amd_no"], approver, "PENDING", raiser, erp.now())
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(approver)["email"], f"{amd['amd_no']} awaiting your approval",
           f"Amendment of {amd['po_no']}: {amd['old_qty']}→{amd['new_qty']}, {amd['old_dt']}→{amd['new_dt']}")
    return approver


@proc("sp_pa_evaluate")
def evaluate(erp, amd_no: str, user: str) -> dict:
    """After Save or a schedule change: hold (schedule does not add up), route for approval, or approve."""
    amd = erp.q1("SELECT * FROM pa_amd WHERE amd_no=?", amd_no)
    h = erp.sp("sp_pa_po_open", amd["po_no"])
    if not erp.sp("sp_pa_sched_match", amd, h["rcvd"]):
        erp.sp("sp_pa_status_set", amd_no, "HD", warn="W-SCH-209")  # saved, silently held; never routed
        return {"status": "HD", "approver": None}
    approver, _why = erp.sp("sp_pa_reappr_rule", amd, h, amd["raised_by"])
    if approver:
        approver = erp.sp("sp_pa_route", amd, approver, amd["raised_by"])
        erp.x("UPDATE pa_amd SET need_appr='Y', approver=? WHERE amd_no=?", approver, amd_no)
        erp.sp("sp_pa_status_set", amd_no, "PA")
        return {"status": "PA", "approver": approver}
    erp.x("UPDATE pa_amd SET need_appr='N', approver=NULL WHERE amd_no=?", amd_no)
    erp.sp("sp_pa_status_set", amd_no, "AP")
    return {"status": "AP", "approver": None}


@proc("sp_pa_rev_apply")
def rev_apply(erp, amd: dict) -> float:
    """On release: the order takes the new quantity, date and values, and the new schedule replaces the open lines.
    Returns the change in gross value."""
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", amd["po_no"])
    line = erp.q1("SELECT * FROM po_line WHERE po_no=?", amd["po_no"])
    basic = round(amd["new_qty"] * line["rate"], 2)
    tax, gross = erp.sp("sp_tax_compute", basic, h["tax_cd"])
    erp.x("UPDATE po_hdr SET need_dt=?, basic_value=?, tax_value=?, gross_value=? WHERE po_no=?", amd["new_dt"], basic,
          tax, gross, amd["po_no"])
    erp.x("UPDATE po_line SET qty=? WHERE po_no=?", amd["new_qty"], amd["po_no"])
    erp.x("UPDATE pa_sched SET status=? WHERE po_no=? AND status='OP'", "CN" if amd["amd_type"] == "SCL" else "SU",
          amd["po_no"])
    erp.x("UPDATE pa_sched SET status='OP' WHERE amd_no=? AND status='PR'", amd["amd_no"])
    return round(gross - h["gross_value"], 2)


@proc("sp_pa_cascade")
def cascade(erp, amd: dict, diff_gross: float):
    """The two cascades of a released revision: (1) the cost centre's committed budget moves by the change in
    value; (2) stock on order moves by the change in quantity, and the supplier is sent the revision."""
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", amd["po_no"])
    line = erp.q1("SELECT * FROM po_line WHERE po_no=?", amd["po_no"])
    erp.sp("sp_budget_commit", h["cc_cd"], diff_gross)
    erp.sp("sp_stk_onorder_upd", line["itm_cd"], h["whs_cd"], amd["new_qty"] - amd["old_qty"])
    sched = "; ".join(f"{r['qty']} on {r['dlv_dt']}" for r in
                      erp.q("SELECT * FROM pa_sched WHERE po_no=? AND status='OP' ORDER BY sl_no", amd["po_no"]))
    erp.sp("sp_ntf_enqueue", "EMAIL", f"orders@{h['sup_cd'].lower()}.example",
           f"Purchase order {amd['po_no']} revision {amd['rev']}",
           f"Revised: {line['qty']} x {line['itm_cd']}. Deliveries: {sched or 'none (balance short-closed)'}.")


@proc("sp_pa_status_set")
def status_set(erp, amd_no: str, status: str, warn: str | None = None):
    erp.x("UPDATE pa_amd SET status=?, warn_cd=? WHERE amd_no=?", status, warn, amd_no)
