"""HR · leave: the nine services, as terse as purchasing's. Status codes: PA, HD, AP, RJ, CN."""
from __future__ import annotations

from ...erp.engine import LedgerlineError, service
from .._kit import F


@service("lv_emp_get", "EMPLOYEE GET", [F("user_id", desc="USER ID"), F("q", desc="NAME LIKE")], screen="HR-LV-01")
def lv_emp_get(erp, user, user_id=None, q=None):
    if q:
        rows = erp.q("SELECT emp_cd,name,dept,ou_cd,lv_appr FROM lv_emp WHERE lower(name) LIKE ?", f"%{q.lower()}%")
        return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}
    r = erp.q1("SELECT * FROM lv_emp WHERE user_id=?", (user_id or user).upper())
    if not r:
        raise LedgerlineError("ERR-LV-0001", "EMPLOYEE NOT FOUND")
    return r


@service("lv_bal_get", "LEAVE BALANCE", [F("emp_cd", req=True, desc="EMP CD"), F("yr", "int", desc="YEAR")],
         screen="HR-LV-01")
def lv_bal_get(erp, user, emp_cd, yr=2026):
    erp.sp("sp_lv_emp_of", user, emp_cd)
    rows = erp.q("SELECT lv_cd,opening,availed,pending,round(opening-availed-pending,1) bal FROM lv_bal "
                 "WHERE emp_cd=? AND yr=?", emp_cd, yr)
    cof = erp.q("SELECT worked_dt,valid_to FROM lv_cof WHERE emp_cd=? AND status='OPEN'", emp_cd)
    return {"rows": rows, "co_open": cof}


@service("lv_hol_list", "HOLIDAY LIST", [F("ou_cd", desc="OU CD")], screen="HR-LV-01")
def lv_hol_list(erp, user, ou_cd="NBC-MAN-01"):
    return {"rows": erp.q("SELECT hol_dt,descr FROM lv_hol WHERE ou_cd IN (?, '*') ORDER BY hol_dt", ou_cd)}


@service("lv_fetch", "LEAVE DEFAULTS", [F("emp_cd", req=True, desc="EMP CD"), F("lv_cd", req=True, desc="LV TYPE")],
         screen="HR-LV-02")
def lv_fetch(erp, user, emp_cd, lv_cd):
    emp = erp.sp("sp_lv_emp_of", user, emp_cd)
    t = erp.q1("SELECT * FROM lv_type WHERE lv_cd=?", lv_cd)
    if not t:
        raise LedgerlineError("ERR-LV-0201", "INVALID LV TYPE")
    b = erp.q1("SELECT round(opening-availed-pending,1) bal FROM lv_bal WHERE emp_cd=? AND lv_cd=? AND yr=2026", emp_cd, lv_cd)
    tok = erp.sp("sp_fetch_tok_new", user, "HR-LV-02", f"{emp_cd}|{lv_cd}")
    return {"bal": b["bal"] if b else 0, "notice_days": t["notice_days"], "lv_appr": emp["lv_appr"], "fetch_tok": tok}


@service("lv_save", "LEAVE APPLY", [F("emp_cd", req=True, desc="EMP CD"), F("lv_cd", req=True, desc="LV TYPE"),
                                    F("from_dt", "date", True, "FROM DT"), F("to_dt", "date", True, "TO DT"),
                                    F("half", desc="1H/2H"), F("reason", req=True, desc="REASON"),
                                    F("ref_dt", "date", desc="WORKED DT (CO)"), F("fwd_to", desc="FWD TO"),
                                    F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen="HR-LV-02")
def lv_save(erp, user, emp_cd, lv_cd, from_dt, to_dt, reason, half=None, ref_dt=None, fwd_to=None, fetch_tok=None,
            client_ref=None):
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "HR-LV-02", f"{emp_cd}|{lv_cd}")
    emp = erp.sp("sp_lv_emp_of", user, emp_cd)
    days = erp.sp("sp_lv_workdays", emp["ou_cd"], from_dt, to_dt, half)
    erp.sp("sp_lv_type_rule", emp, lv_cd, from_dt, to_dt, days, half, ref_dt)
    erp.sp("sp_lv_overlap_chk", emp_cd, from_dt, to_dt)
    paid, lwp = erp.sp("sp_lv_bal_chk", emp_cd, lv_cd, days)
    lv_no = erp.sp("sp_doc_no_next", "LV")
    status, warn, approver = "PA", None, None
    if lwp and lv_cd != "LWP":
        status, warn = "HD", "W-LV-118"  # the balance did not cover it: saved, held for HR, never reaches the manager
    erp.x("INSERT INTO lv_app VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lv_no, emp_cd, lv_cd, from_dt, to_dt, half,
          days, lwp, reason, ref_dt, status, user, erp.now(), None, None, warn, client_ref)
    if paid and lv_cd not in ("CO", "LWP"):
        erp.sp("sp_lv_bal_hold", emp_cd, lv_cd, paid)
    if lv_cd == "CO":
        erp.x("UPDATE lv_cof SET status='HELD', used_by=? WHERE emp_cd=? AND worked_dt=?", lv_no, emp_cd, ref_dt)
    if status == "PA":
        approver = erp.sp("sp_lv_route", lv_no, emp, user, fwd_to)
        erp.sp("sp_lv_status_set", lv_no, "PA", approver)
    return {"lv_no": lv_no, "status": status, "days": days, "lwp_days": lwp, "warn_cd": None,
            "_msg": f"{lv_no} SAVED"}  # the warning is stored on the application, not shown in the reply


@service("lv_list", "LEAVE LIST", [F("lv_no", desc="LV NO"), F("emp_cd", desc="EMP CD"), F("status", desc="STATUS"),
                                   F("approver", desc="APPROVER"), F("client_ref", desc="CLIENT REF")],
         screen="HR-LV-04")
def lv_list(erp, user, lv_no=None, emp_cd=None, status=None, approver=None, client_ref=None):
    sql, args = ("SELECT lv_no,emp_cd,lv_cd,from_dt,to_dt,half,days,lwp_days,ref_dt,status,approver,warn_cd,client_ref "
                 "FROM lv_app WHERE 1=1"), []
    for col, v in (("lv_no", lv_no), ("emp_cd", emp_cd), ("status", status), ("approver", approver),
                   ("client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col == "approver" else v)
    return {"rows": erp.q(sql + " ORDER BY lv_no DESC", *args)}


@service("lv_approve", "LEAVE APPROVE", [F("lv_no", req=True, desc="LV NO"), F("decision", req=True, desc="A/R"),
                                         F("comment", desc="COMMENT")], kind="write", screen="HR-LV-04")
def lv_approve(erp, user, lv_no, decision, comment=""):
    a = erp.q1("SELECT * FROM lv_app WHERE lv_no=?", lv_no)
    if not a:
        raise LedgerlineError("ERR-LV-0501", "LV NOT FOUND")
    if a["status"] != "PA":
        raise LedgerlineError("ERR-LV-0502", f"LV NOT PENDING ({a['status']})")
    emp = erp.q1("SELECT * FROM lv_emp WHERE emp_cd=?", a["emp_cd"])
    if emp["user_id"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    if a["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-LV-0504", f"NOT YOUR APPROVAL ({a['approver']})")
    ok = decision.upper().startswith("A")
    erp.sp("sp_lv_status_set", lv_no, "AP" if ok else "RJ", user)
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, lv_no)
    erp.sp("sp_lv_bal_post", a, ok)
    if ok:
        erp.sp("sp_lv_roster_mark", a)
    if emp["user_id"]:
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(emp["user_id"])["email"], f"{lv_no} {'APPROVED' if ok else 'REJECTED'}",
               comment or "")
    return {"lv_no": lv_no, "status": "AP" if ok else "RJ", "_msg": f"{lv_no} {'APPROVED' if ok else 'REJECTED'} BY {user}"}


@service("lv_hr_clear", "HELD LEAVE CLEAR", [F("lv_no", req=True, desc="LV NO"), F("decision", req=True, desc="L/R"),
                                             F("comment", desc="COMMENT")], kind="write", screen="HR-LV-04")
def lv_hr_clear(erp, user, lv_no, decision, comment=""):
    """HR clears a held application: L = accept the unpaid days and send it to the approver, R = return it."""
    a = erp.q1("SELECT * FROM lv_app WHERE lv_no=?", lv_no)
    if not a or a["status"] != "HD":
        raise LedgerlineError("ERR-LV-0505", "LV NOT HELD")
    if decision.upper().startswith("R"):
        erp.sp("sp_lv_status_set", lv_no, "RJ", user)
        erp.sp("sp_lv_bal_post", a, False)
        return {"lv_no": lv_no, "status": "RJ", "_msg": f"{lv_no} RETURNED"}
    emp = erp.q1("SELECT * FROM lv_emp WHERE emp_cd=?", a["emp_cd"])
    approver = erp.sp("sp_lv_route", lv_no, emp, user, None)
    erp.sp("sp_lv_status_set", lv_no, "PA", approver)
    return {"lv_no": lv_no, "status": "PA", "approver": approver, "_msg": f"{lv_no} CLEARED"}


@service("lv_cancel", "LEAVE CANCEL", [F("lv_no", req=True, desc="LV NO"), F("reason", req=True, desc="REASON")],
         kind="write", screen="HR-LV-02")
def lv_cancel(erp, user, lv_no, reason):
    a = erp.q1("SELECT * FROM lv_app WHERE lv_no=?", lv_no)
    if not a:
        raise LedgerlineError("ERR-LV-0501", "LV NOT FOUND")
    erp.sp("sp_lv_emp_of", user, a["emp_cd"])
    if a["status"] in ("CN", "RJ"):
        raise LedgerlineError("ERR-LV-0507", f"LV CLOSED ({a['status']})")
    if a["status"] == "AP" and a["from_dt"] <= erp.today:
        raise LedgerlineError("ERR-LV-0508", "LEAVE ALREADY STARTED")
    if a["status"] in ("PA", "HD"):
        erp.sp("sp_lv_bal_post", a, False)
    elif a["status"] == "AP":
        paid = a["days"] - a["lwp_days"]
        erp.x("UPDATE lv_bal SET availed=round(availed-?,1) WHERE emp_cd=? AND lv_cd=? AND yr=2026", paid, a["emp_cd"], a["lv_cd"])
        erp.x("DELETE FROM lv_roster WHERE ref=?", lv_no)
    erp.sp("sp_lv_status_set", lv_no, "CN")
    erp.x("UPDATE approval SET status='WITHDRAWN' WHERE doc_no=? AND status='PENDING'", lv_no)
    return {"lv_no": lv_no, "status": "CN", "_msg": f"{lv_no} CANCELLED"}
