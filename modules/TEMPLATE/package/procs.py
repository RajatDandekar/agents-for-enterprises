"""Stored procedures (~10): the rules live here, services call them through erp.sp(name, ...)."""
from ...erp.engine import BahiError, proc


@proc("sp_xx_save")
def xx_save(erp, user, party, qty, amount, cc_cd, client_ref):
    if qty <= 0:
        raise BahiError("ERR-XX-0001", "QTY MUST BE > 0")
    state = erp.sp("sp_budget_chk", cc_cd, amount)       # the shared engine, reused from purchasing
    doc_no = erp.sp("sp_doc_no_next", "XX")
    status, warn = ("HD", "W-XX-101") if state == "CLOSED" else ("PA", None)   # the silent outcome
    erp.x("INSERT INTO xx_doc VALUES (?,?,?,?,?,?,?,?,?,?,?)", doc_no, party, qty, amount, cc_cd, status, user,
          erp.now(), None, warn, client_ref)
    if status == "PA":
        approver = erp.sp("sp_appr_route", "XX", doc_no, user, amount)    # cascade: approval + mail
        erp.x("UPDATE xx_doc SET approver=? WHERE doc_no=?", approver, doc_no)
    return {"doc_no": doc_no, "status": status}

# TODO: the rest of your ~10 procedures: variant checks, the second cascade, status changes.
