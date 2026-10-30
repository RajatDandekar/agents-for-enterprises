"""Stored procedures: where Ledgerline keeps its rules.

In a real legacy ERP these are thousands of SQL procedures. Here there are a dozen, written in Python,
each doing one job. Services call them through erp.sp(name, ...), so every call is logged.
The rule "validate once" means: an agent never copies these rules. It calls the service and lets them run.
"""
from __future__ import annotations

from .engine import LedgerlineError, proc


@proc("sp_doc_no_next")
def doc_no_next(erp, doc_type: str) -> str:
    r = erp.q1("SELECT * FROM doc_seq WHERE doc_type=?", doc_type)
    erp.x("UPDATE doc_seq SET next_no=next_no+1 WHERE doc_type=?", doc_type)
    return f"{r['prefix']}{str(r['next_no']).zfill(r['width'])}"


@proc("sp_fetch_tok_new")
def fetch_tok_new(erp, user: str, screen: str, ctx: str) -> str:
    tok = erp.token(8)
    erp.x("INSERT INTO fetch_tok VALUES (?,?,?,?,?,0)", tok, user, screen, ctx, erp.now())
    return tok


@proc("sp_fetch_tok_chk")
def fetch_tok_chk(erp, user: str, tok: str | None, screen: str, ctx: str):
    """Screen state: the PO screen must have run Fetch for this supplier and item before Save."""
    r = erp.q1("SELECT * FROM fetch_tok WHERE tok=?", tok or "")
    if not r or r["user_id"] != user or r["screen"] != screen or r["ctx"] != ctx or r["used"]:
        raise LedgerlineError("ERR-SCR-0221", "FETCH NOT DONE")
    erp.x("UPDATE fetch_tok SET used=1 WHERE tok=?", tok)


@proc("sp_tax_region_chk")
def tax_region_chk(erp, sup_cd: str, tax_cd: str, ou_cd: str):
    """Shared engine. A UK supplier needs a UK code (VAT20-UK); an overseas supplier needs reverse charge (VAT20-RC)."""
    sup = erp.q1("SELECT state FROM supplier WHERE sup_cd=?", sup_cd)
    ou = erp.q1("SELECT state FROM org_unit WHERE ou_cd=?", ou_cd)
    tax = erp.q1("SELECT * FROM tax_code WHERE tax_cd=?", tax_cd)
    if not tax:
        raise LedgerlineError("ERR-TAX-0101", "INVALID TAX CODE")
    want = "INTRA" if sup["state"] == ou["state"] else "INTER"
    if tax["kind"] != want:
        raise LedgerlineError("ERR-PO-0412", f"TAX CODE DOES NOT MATCH SUPPLIER COUNTRY ({sup['state']})")


@proc("sp_tax_compute")
def tax_compute(erp, basic: float, tax_cd: str) -> tuple[float, float]:
    """Shared engine: tax and gross value for a basic value."""
    tax = erp.q1("SELECT rate FROM tax_code WHERE tax_cd=?", tax_cd)
    if not tax:
        raise LedgerlineError("ERR-TAX-0101", "INVALID TAX CODE")
    t = round(basic * tax["rate"], 2)
    return t, round(basic + t, 2)


@proc("sp_budget_chk")
def budget_chk(erp, cc_cd: str, amount: float) -> str:
    """Shared engine. Returns 'OK' or 'CLOSED'. A closed cost centre does not raise an error:
    the caller saves the document as Draft. (This is the silent outcome.)"""
    cc = erp.q1("SELECT * FROM cost_centre WHERE cc_cd=?", cc_cd)
    if not cc:
        raise LedgerlineError("ERR-CC-0009", "COST CENTRE NOT FOUND")
    if cc["status"] != "OPEN":
        return "CLOSED"
    b = erp.q1("SELECT * FROM budget WHERE cc_cd=? AND period='2026-Q4'", cc_cd)
    if b and b["committed"] + amount > b["amount"]:
        raise LedgerlineError("ERR-BUD-0207", f"BUDGET EXCEEDED FOR {cc_cd}")
    return "OK"


@proc("sp_budget_commit")
def budget_commit(erp, cc_cd: str, amount: float):
    """Cascade: committing spend against the cost centre's quarterly budget."""
    erp.x("UPDATE budget SET committed=round(committed+?,2) WHERE cc_cd=? AND period='2026-Q4'", amount, cc_cd)


@proc("sp_appr_route")
def appr_route(erp, doc_type: str, doc_no: str, requester: str, gross: float) -> str:
    """Cascade: walk up the manager chain to the first person whose limit covers the gross value."""
    u = erp.user(requester)
    approver = u["manager_id"]
    while approver:
        a = erp.user(approver)
        if a["appr_limit"] >= gross:
            break
        approver = a["manager_id"]
    if not approver:
        raise LedgerlineError("ERR-APR-0009", "NO APPROVER FOUND")
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
          doc_type, doc_no, approver, "PENDING", requester, erp.now())
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(approver)["email"], f"{doc_no} awaiting your approval",
           f"{doc_type} {doc_no} raised by {requester}, value {gross:,.2f}")
    return approver


@proc("sp_ntf_enqueue")
def ntf_enqueue(erp, channel: str, recipient: str, subject: str, body: str):
    erp.x("INSERT INTO ntf_queue(channel,recipient,subject,body,created_on) VALUES (?,?,?,?,?)",
          channel, recipient, subject, body, erp.now())


@proc("sp_pr_save")
def pr_save(erp, user, pr_type, cc_cd, need_dt, itm_cd, qty, whs_cd, est_rate, remarks) -> dict:
    itm = erp.q1("SELECT * FROM item WHERE itm_cd=?", itm_cd)
    if not itm or not itm["active"]:
        raise LedgerlineError("ERR-ITM-0011", "ITEM NOT FOUND OR INACTIVE")
    if not erp.q1("SELECT 1 FROM cost_centre WHERE cc_cd=?", cc_cd):
        raise LedgerlineError("ERR-CC-0009", "COST CENTRE NOT FOUND")
    if need_dt < erp.today:
        raise LedgerlineError("ERR-PR-0105", "NEED DATE IN PAST")
    pr_no = erp.sp("sp_doc_no_next", "PR")
    est = round(qty * est_rate * 1.20, 2)  # estimated gross: Ledgerline assumes 20% VAT on every request
    erp.x("INSERT INTO pr_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", pr_no, erp.user(user)["ou_cd"], pr_type, cc_cd,
          need_dt, whs_cd, remarks, "DR", user, erp.now(), None, est)
    erp.x("INSERT INTO pr_line VALUES (?,?,?,?,?)", pr_no, 1, itm_cd, qty, itm["uom_cd"])
    return {"pr_no": pr_no, "est_value": est}


@proc("sp_po_hdr_save")
def po_hdr_save(erp, user, a: dict) -> dict:
    """The rules behind the Save button on PUR-PO-01."""
    ou_cd = erp.user(user)["ou_cd"]
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", a["sup_cd"])
    if not sup:
        raise LedgerlineError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    if sup["status"] != "ACTIVE":
        raise LedgerlineError("ERR-SUP-0031", "SUPPLIER NOT ACTIVE")
    itm = erp.q1("SELECT * FROM item WHERE itm_cd=?", a["itm_cd"])
    if not itm or not itm["active"]:
        raise LedgerlineError("ERR-ITM-0011", "ITEM NOT FOUND OR INACTIVE")
    if a["qty"] <= 0:
        raise LedgerlineError("ERR-PO-0201", "QTY MUST BE > 0")
    if a["need_dt"] < erp.today:
        raise LedgerlineError("ERR-PO-0105", "NEED DATE IN PAST")
    erp.sp("sp_tax_region_chk", a["sup_cd"], a["tax_cd"], ou_cd)
    basic = round(a["qty"] * a["rate"], 2)
    tax, gross = erp.sp("sp_tax_compute", basic, a["tax_cd"])

    pr = None
    if a.get("po_type", "STD") == "STD":  # variant 1: against an approved purchase request
        pr = erp.q1("SELECT * FROM pr_hdr WHERE pr_no=?", a.get("pr_no") or "")
        if not pr:
            raise LedgerlineError("ERR-PO-0602", "SOURCE PR MANDATORY FOR STD PO")
        if pr["status"] != "AP":
            raise LedgerlineError("ERR-PO-0603", f"SOURCE PR NOT APPROVED ({pr['status']})")
        line = erp.q1("SELECT * FROM pr_line WHERE pr_no=?", pr["pr_no"])
        if line["itm_cd"] != a["itm_cd"] or a["qty"] > line["qty"]:
            raise LedgerlineError("ERR-PO-0604", "ITEM/QTY NOT AS PER PR")
    else:  # variant 2: direct order, no request, small orders only
        if a.get("pr_no"):
            raise LedgerlineError("ERR-PO-0611", "DIR PO CANNOT REFER PR")
        if gross > 50000:
            raise LedgerlineError("ERR-PO-0610", "DIRECT PO LIMIT 50000 EXCEEDED, RAISE PR")

    cc_state = erp.sp("sp_budget_chk", a["cc_cd"], gross)
    warn = None
    approved_by = None
    if cc_state == "CLOSED":
        status, warn = "DR", "W-CC-114"  # saved, silently, as Draft
    elif gross <= erp.user(user)["appr_limit"]:
        status, approved_by = "AP", user
    elif pr and pr["approved_by"] and erp.user(pr["approved_by"])["appr_limit"] >= gross:
        status, approved_by = "AP", pr["approved_by"]  # the request's approval covers the order
    else:
        status = "PA"
    po_no = erp.sp("sp_doc_no_next", "PO")
    erp.x("INSERT INTO po_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
          po_no, ou_cd, a["sup_cd"], a.get("pr_no"), a.get("po_type", "STD"), a["cc_cd"], a["tax_cd"],
          sup["pt_cd"], a["need_dt"], a.get("whs_cd") or "WH-MAN-STR", status, basic, tax, gross, user,
          erp.now(), approved_by, erp.now() if approved_by else None, None, a.get("client_ref"), warn)
    erp.x("INSERT INTO po_line VALUES (?,?,?,?,?,?)", po_no, 1, a["itm_cd"], a["qty"], itm["uom_cd"], a["rate"])
    if status == "PA":
        erp.sp("sp_appr_route", "PO", po_no, user, gross)
    if status in ("AP", "PA"):
        erp.sp("sp_budget_commit", a["cc_cd"], gross)
    erp.sp("sp_po_status_set", po_no, status)
    if pr:
        erp.x("UPDATE pr_hdr SET status='CL' WHERE pr_no=?", pr["pr_no"])
    return {"doc_no": po_no, "status": status}


@proc("sp_po_status_set")
def po_status_set(erp, po_no: str, status: str):
    erp.x("UPDATE po_hdr SET status=? WHERE po_no=?", status, po_no)


@proc("sp_stk_onorder_upd")
def stk_onorder_upd(erp, itm_cd: str, whs_cd: str, qty: int):
    """Cascade: a released order shows up as stock on order."""
    erp.x("UPDATE stock SET on_order=on_order+? WHERE itm_cd=? AND whs_cd=?", qty, itm_cd, whs_cd)
