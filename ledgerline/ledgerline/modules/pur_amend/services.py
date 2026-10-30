"""Purchasing · amend PO: nine services. Amendment status codes: HD, PA, AP, RL, RJ."""
from __future__ import annotations

from ...erp.engine import LedgerlineError, service
from .._kit import F


def _lines(s1_dt, s1_qty, s2_dt, s2_qty) -> list[tuple]:
    out = []
    for d, q in ((s1_dt, s1_qty), (s2_dt, s2_qty)):
        if d and q:
            out.append((d, q))
        elif d or q:
            raise LedgerlineError("ERR-PA-0331", "SCHEDULE LINE NEEDS DATE AND QTY")
    return out


@service("pa_po_list", "PO LIST (RELEASED)", [F("sup_cd", desc="SUP CD"), F("itm_cd", desc="ITEM CD"),
                                              F("status", desc="STATUS"), F("q", desc="SUP NAME LIKE")],
         screen="PUR-POL-07")
def pa_po_list(erp, user, sup_cd=None, itm_cd=None, status=None, q=None):
    sql = ("SELECT h.po_no,h.sup_cd,s.name sup_name,l.itm_cd,i.descr,l.qty,l.rate,h.need_dt,h.gross_value,h.status "
           "FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no JOIN supplier s ON s.sup_cd=h.sup_cd "
           "JOIN item i ON i.itm_cd=l.itm_cd WHERE 1=1")
    args = []
    for col, v in (("h.sup_cd", sup_cd), ("l.itm_cd", itm_cd), ("h.status", status)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    if q:
        sql += " AND lower(s.name) LIKE ?"
        args.append(f"%{q.lower()}%")
    rows = erp.q(sql + " ORDER BY h.po_no DESC", *args)
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("pa_po_get", "PO GET WITH REVISIONS", [F("po_no", req=True, desc="PO NO")], screen="PUR-POL-07")
def pa_po_get(erp, user, po_no):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    return {**h, "lines": erp.q("SELECT * FROM po_line WHERE po_no=?", po_no),
            "amds": erp.q("SELECT amd_no,rev,amd_type,new_qty,new_dt,status,warn_cd FROM pa_amd WHERE po_no=? "
                          "ORDER BY amd_no", po_no)}


@service("pa_sched_get", "DELIVERY SCHEDULE", [F("po_no", req=True, desc="PO NO")], screen="PUR-POL-07")
def pa_sched_get(erp, user, po_no):
    rows = erp.q("SELECT sl_no,dlv_dt,qty,rcvd_qty,status,amd_no FROM pa_sched WHERE po_no=? AND status<>'SU' "
                 "ORDER BY sl_no", po_no)
    rcpts = erp.q("SELECT grn_no,sl_no,rcpt_dt,qty FROM pa_rcpt WHERE po_no=? ORDER BY rcpt_dt", po_no)
    return {"rows": rows, "rcpts": rcpts, "rcvd_qty": sum(r["qty"] for r in rcpts)}


@service("pa_amd_fetch", "AMENDMENT DEFAULTS", [F("po_no", req=True, desc="PO NO")], screen="PUR-POM-08")
def pa_amd_fetch(erp, user, po_no):
    h = erp.sp("sp_pa_po_open", po_no)
    erp.sp("sp_pa_open_amd_chk", po_no)
    rev = erp.q1("SELECT count(*) n FROM pa_amd WHERE po_no=? AND status='RL'", po_no)["n"] + 1
    tok = erp.sp("sp_fetch_tok_new", user, "PUR-POM-08", po_no)
    return {"qty": h["qty"], "rcvd_qty": h["rcvd"], "need_dt": h["need_dt"], "rev": rev, "open_lines": h["open_lines"],
            "fetch_tok": tok}


@service("pa_amd_save", "AMENDMENT SAVE",
         [F("po_no", req=True, desc="PO NO"), F("amd_type", desc="REV/SCL"), F("qty", "int", desc="NEW QTY"),
          F("need_dt", "date", desc="NEW NEED DT"), F("reason_cd", req=True, desc="REASON CD"), F("remarks", desc="REMARKS"),
          F("s1_dt", "date", desc="SCH1 DT"), F("s1_qty", "int", desc="SCH1 QTY"), F("s2_dt", "date", desc="SCH2 DT"),
          F("s2_qty", "int", desc="SCH2 QTY"), F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen="PUR-POM-08")
def pa_amd_save(erp, user, po_no, reason_cd, amd_type="REV", qty=None, need_dt=None, remarks=None, s1_dt=None,
                s1_qty=None, s2_dt=None, s2_qty=None, fetch_tok=None, client_ref=None):
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "PUR-POM-08", po_no)
    h = erp.sp("sp_pa_po_open", po_no)
    erp.sp("sp_pa_open_amd_chk", po_no)
    if not erp.q1("SELECT 1 FROM pa_reason WHERE reason_cd=?", reason_cd):
        raise LedgerlineError("ERR-PA-0201", "INVALID REASON CD")
    lines = _lines(s1_dt, s1_qty, s2_dt, s2_qty)
    amd_type = amd_type.upper()
    new_qty, new_dt = erp.sp("sp_pa_type_rule", amd_type, h, qty, need_dt, lines)
    erp.sp("sp_pa_qty_chk", new_qty, h["rcvd"])
    erp.sp("sp_pa_lead_chk", h["sup_cd"], ([new_dt] if new_dt != h["need_dt"] else []) + [d for d, _ in lines])
    basic = round(new_qty * h["rate"], 2)
    _tax, gross = erp.sp("sp_tax_compute", basic, h["tax_cd"])  # shared engine
    if gross > h["gross_value"]:
        if erp.sp("sp_budget_chk", h["cc_cd"], gross - h["gross_value"]) == "CLOSED":
            raise LedgerlineError("ERR-PA-0415", f"CC {h['cc_cd']} CLOSED, CANNOT INCREASE")
    amd_no = erp.sp("sp_doc_no_next", "PA-AMD")
    rev = erp.q1("SELECT count(*) n FROM pa_amd WHERE po_no=? AND status='RL'", po_no)["n"] + 1
    erp.x("INSERT INTO pa_amd VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", amd_no, po_no, rev, amd_type,
          h["qty"], new_qty, h["need_dt"], new_dt, h["gross_value"], gross, reason_cd, remarks, None, "HD", user,
          erp.now(), None, None, None, None, None, client_ref)
    if amd_type == "REV":
        erp.sp("sp_pa_sched_propose", amd_no, po_no, lines)
    r = erp.sp("sp_pa_evaluate", amd_no, user)
    return {"amd_no": amd_no, "rev": rev, "status": r["status"], "approver": r["approver"], "new_gross": gross,
            "_msg": f"{amd_no} SAVED"}  # the status is in the data; the message never mentions a hold


@service("pa_sched_save", "AMENDMENT SCHEDULE SAVE",
         [F("amd_no", req=True, desc="AMD NO"), F("s1_dt", "date", True, "SCH1 DT"), F("s1_qty", "int", True, "SCH1 QTY"),
          F("s2_dt", "date", desc="SCH2 DT"), F("s2_qty", "int", desc="SCH2 QTY")], kind="write", screen="PUR-POM-08")
def pa_sched_save(erp, user, amd_no, s1_dt, s1_qty, s2_dt=None, s2_qty=None):
    amd = erp.q1("SELECT * FROM pa_amd WHERE amd_no=?", amd_no)
    if not amd:
        raise LedgerlineError("ERR-PA-0501", "AMD NOT FOUND")
    if amd["status"] != "HD":
        raise LedgerlineError("ERR-PA-0503", f"SCHEDULE LOCKED ({amd['status']})")
    if amd["amd_type"] == "SCL":
        raise LedgerlineError("ERR-PA-0613", "SCL CANNOT HAVE SCHEDULE")
    lines = _lines(s1_dt, s1_qty, s2_dt, s2_qty)
    h = erp.q1("SELECT sup_cd FROM po_hdr WHERE po_no=?", amd["po_no"])
    erp.sp("sp_pa_lead_chk", h["sup_cd"], [d for d, _ in lines])
    erp.sp("sp_pa_sched_propose", amd_no, amd["po_no"], lines)
    r = erp.sp("sp_pa_evaluate", amd_no, user)
    return {"amd_no": amd_no, "status": r["status"], "approver": r["approver"], "_msg": f"{amd_no} SCHEDULE SAVED"}


@service("pa_amd_list", "AMENDMENT LIST", [F("amd_no", desc="AMD NO"), F("po_no", desc="PO NO"), F("status", desc="STATUS"),
                                          F("approver", desc="APPROVER"), F("raised_by", desc="USER ID"),
                                          F("client_ref", desc="CLIENT REF")], screen="PUR-POA-09")
def pa_amd_list(erp, user, amd_no=None, po_no=None, status=None, approver=None, raised_by=None, client_ref=None):
    sql = ("SELECT amd_no,po_no,rev,amd_type,old_qty,new_qty,old_dt,new_dt,new_gross,status,raised_by,approver,"
           "approved_by,warn_cd,client_ref FROM pa_amd WHERE 1=1")
    args = []
    for col, v in (("amd_no", amd_no), ("po_no", po_no), ("status", status), ("approver", approver),
                   ("raised_by", raised_by), ("client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col in ("approver", "raised_by", "status") else v)
    return {"rows": erp.q(sql + " ORDER BY amd_no DESC", *args)}


@service("pa_amd_approve", "AMENDMENT APPROVE", [F("amd_no", req=True, desc="AMD NO"), F("decision", req=True, desc="A/R"),
                                                 F("comment", desc="COMMENT")], kind="write", screen="PUR-POA-09")
def pa_amd_approve(erp, user, amd_no, decision, comment=""):
    a = erp.q1("SELECT * FROM pa_amd WHERE amd_no=?", amd_no)
    if not a:
        raise LedgerlineError("ERR-PA-0501", "AMD NOT FOUND")
    if a["status"] != "PA":
        raise LedgerlineError("ERR-PA-0502", f"AMD NOT PENDING ({a['status']})")
    if a["raised_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if a["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-PA-0504", f"NOT YOUR APPROVAL ({a['approver']})")
    if erp.user(user)["appr_limit"] < a["new_gross"]:
        raise LedgerlineError("ERR-APR-0004", "VALUE ABOVE YOUR LIMIT")
    good = decision.upper().startswith("A")
    st = "AP" if good else "RJ"
    erp.x("UPDATE pa_amd SET status=?, approved_by=?, decided_on=? WHERE amd_no=?", st, user if good else None,
          erp.now(), amd_no)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if good else "REJECTED", erp.now(), comment, amd_no)
    if not good:
        erp.x("UPDATE pa_sched SET status='SU' WHERE amd_no=? AND status='PR'", amd_no)
    erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(a["raised_by"])["email"], f"{amd_no} {'APPROVED' if good else 'REJECTED'}",
           comment or "")
    return {"amd_no": amd_no, "status": st, "_msg": f"{amd_no} {'APPROVED' if good else 'REJECTED'} BY {user}"}


@service("pa_amd_release", "AMENDMENT RELEASE", [F("amd_no", req=True, desc="AMD NO")], kind="write",
         screen="PUR-POM-08")
def pa_amd_release(erp, user, amd_no):
    a = erp.q1("SELECT * FROM pa_amd WHERE amd_no=?", amd_no)
    if not a:
        raise LedgerlineError("ERR-PA-0501", "AMD NOT FOUND")
    if a["status"] != "AP":
        raise LedgerlineError("ERR-PA-0715", f"AMD NOT IN RELEASABLE STATUS ({a['status']})")
    diff = erp.sp("sp_pa_rev_apply", a)
    erp.sp("sp_pa_cascade", a, diff)
    erp.sp("sp_pa_status_set", amd_no, "RL")
    erp.x("UPDATE pa_amd SET released_on=? WHERE amd_no=?", erp.now(), amd_no)
    return {"amd_no": amd_no, "po_no": a["po_no"], "rev": a["rev"], "status": "RL",
            "_msg": f"{a['po_no']} REV {a['rev']} RELEASED"}
