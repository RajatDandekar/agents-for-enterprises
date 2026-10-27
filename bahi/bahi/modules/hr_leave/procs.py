"""HR · leave: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import BahiError, proc

DIWALI_RUN = ("2026-11-02", "2026-11-14")  # Leave Policy §5.2. Bahi does NOT enforce it; the policy does.


def _days(a: str, b: str):
    d0, d1 = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    while d0 <= d1:
        yield d0
        d0 += dt.timedelta(days=1)


@proc("sp_lv_emp_of")
def emp_of(erp, user: str, emp_cd: str | None) -> dict:
    """Whose leave is this? An employee may apply only for themself; HR and the service account for anyone."""
    me = erp.q1("SELECT * FROM lv_emp WHERE user_id=?", user)
    if not emp_cd:
        if not me:
            raise BahiError("ERR-LV-0002", "EMP CD MANDATORY")
        return me
    e = erp.q1("SELECT * FROM lv_emp WHERE emp_cd=?", emp_cd)
    if not e:
        raise BahiError("ERR-LV-0001", "EMPLOYEE NOT FOUND")
    if erp.user(user)["role_cd"] not in ("HR-EXEC", "SYS-ADMIN") and (not me or me["emp_cd"] != emp_cd):
        raise BahiError("ERR-LV-0003", "NOT YOUR EMP CD")
    return e


@proc("sp_lv_workdays")
def workdays(erp, ou_cd: str, from_dt: str, to_dt: str, half: str | None) -> float:
    """Working days in a range: Sundays and plant holidays do not count. A half day counts 0.5."""
    if to_dt < from_dt:
        raise BahiError("ERR-LV-0102", "TO DT BEFORE FROM DT")
    hols = {r["hol_dt"] for r in erp.q("SELECT hol_dt FROM lv_hol WHERE ou_cd IN (?, '*')", ou_cd)}
    n = sum(1 for d in _days(from_dt, to_dt) if d.weekday() != 6 and d.isoformat() not in hols)
    if n == 0:
        raise BahiError("ERR-LV-0104", "NO WORKING DAYS IN RANGE")
    return 0.5 if half else float(n)


@proc("sp_lv_type_rule")
def type_rule(erp, emp: dict, lv_cd: str, from_dt: str, to_dt: str, days: float, half: str | None, ref_dt: str | None):
    """The two variants. Regular leave (CL/EL/SL/LWP) checks notice and longest run.
    Comp-off (CO) must name the worked holiday it is taken against (ref_dt), and that credit must be open."""
    t = erp.q1("SELECT * FROM lv_type WHERE lv_cd=?", lv_cd)
    if not t:
        raise BahiError("ERR-LV-0201", "INVALID LV TYPE")
    if half and from_dt != to_dt:
        raise BahiError("ERR-LV-0611", "HALF DAY ONLY FOR SINGLE DATE")
    if half and half not in ("1H", "2H"):
        raise BahiError("ERR-LV-0612", "HALF MUST BE 1H/2H")
    if from_dt < erp.today and lv_cd not in ("SL",):
        raise BahiError("ERR-LV-0105", "FROM DT IN PAST")
    notice = (dt.date.fromisoformat(from_dt) - dt.date.fromisoformat(erp.today)).days
    if notice < t["notice_days"]:
        raise BahiError("ERR-LV-0215", f"{lv_cd} NEEDS {t['notice_days']} DAYS NOTICE")
    if days > t["max_run"]:
        raise BahiError("ERR-LV-0217", f"{lv_cd} MAX {t['max_run']} DAYS AT A STRETCH")
    if lv_cd == "CO":
        if not ref_dt:
            raise BahiError("ERR-LV-0620", "CO NEEDS WORKED DT")
        c = erp.q1("SELECT * FROM lv_cof WHERE emp_cd=? AND worked_dt=? AND status='OPEN' AND valid_to>=?",
                   emp["emp_cd"], ref_dt, from_dt)
        if not c:
            raise BahiError("ERR-LV-0621", "NO OPEN CO CREDIT FOR WORKED DT")
    elif ref_dt:
        raise BahiError("ERR-LV-0622", "WORKED DT ONLY FOR CO")


@proc("sp_lv_overlap_chk")
def overlap_chk(erp, emp_cd: str, from_dt: str, to_dt: str):
    r = erp.q1("SELECT lv_no FROM lv_app WHERE emp_cd=? AND status IN ('PA','HD','AP') AND from_dt<=? AND to_dt>=?",
               emp_cd, to_dt, from_dt)
    if r:
        raise BahiError("ERR-LV-0301", f"OVERLAPS {r['lv_no']}")


@proc("sp_lv_bal_chk")
def bal_chk(erp, emp_cd: str, lv_cd: str, days: float) -> tuple[float, float]:
    """Returns (paid days, days without pay). It never refuses: whatever the balance cannot cover becomes LWP.
    This is the silent outcome."""
    if lv_cd in ("LWP",):
        return 0.0, days
    if lv_cd == "CO":
        return days, 0.0
    b = erp.q1("SELECT * FROM lv_bal WHERE emp_cd=? AND lv_cd=? AND yr=2026", emp_cd, lv_cd)
    avail = (b["opening"] - b["availed"] - b["pending"]) if b else 0.0
    paid = max(0.0, min(days, avail))
    return paid, round(days - paid, 1)


@proc("sp_lv_bal_hold")
def bal_hold(erp, emp_cd: str, lv_cd: str, days: float):
    erp.x("UPDATE lv_bal SET pending=pending+? WHERE emp_cd=? AND lv_cd=? AND yr=2026", days, emp_cd, lv_cd)


@proc("sp_lv_bal_post")
def bal_post(erp, app: dict, approved: bool):
    """Cascade 1: on a decision, pending days move to availed (approved) or back to the balance (rejected)."""
    paid = app["days"] - app["lwp_days"]
    if app["lv_cd"] == "CO":
        erp.x("UPDATE lv_cof SET status=?, used_by=? WHERE emp_cd=? AND worked_dt=?",
              "USED" if approved else "OPEN", app["lv_no"] if approved else None, app["emp_cd"], app["ref_dt"])
        return
    erp.x("UPDATE lv_bal SET pending=round(pending-?,1), availed=round(availed+?,1) WHERE emp_cd=? AND lv_cd=? AND yr=2026",
          paid, paid if approved else 0, app["emp_cd"], app["lv_cd"])


@proc("sp_lv_roster_mark")
def roster_mark(erp, app: dict):
    """Cascade 2: the attendance roster shows the leave code on each working day, and any unpaid days go to payroll."""
    emp = erp.q1("SELECT * FROM lv_emp WHERE emp_cd=?", app["emp_cd"])
    hols = {r["hol_dt"] for r in erp.q("SELECT hol_dt FROM lv_hol WHERE ou_cd IN (?, '*')", emp["ou_cd"])}
    days = [d.isoformat() for d in _days(app["from_dt"], app["to_dt"]) if d.weekday() != 6 and d.isoformat() not in hols]
    paid_left = app["days"] - app["lwp_days"]
    for d in days:
        code = app["lv_cd"] if paid_left > 0 else "LWP"
        paid_left -= 1
        erp.x("INSERT INTO lv_roster VALUES (?,?,?,?)", app["emp_cd"], d, code + ("/2" if app["half"] else ""), app["lv_no"])
    if app["lwp_days"]:
        erp.sp("sp_lv_pay_feed", app["emp_cd"], app["from_dt"][:7], app["lwp_days"], app["lv_no"])


@proc("sp_lv_pay_feed")
def pay_feed(erp, emp_cd: str, period: str, lwp: float, ref: str):
    erp.x("INSERT INTO lv_pay_feed VALUES (?,?,?,?,?)", emp_cd, period, lwp, ref, erp.now())


@proc("sp_lv_route")
def route(erp, app_no: str, emp: dict, requester: str, fwd_to: str | None) -> str:
    """Who approves? The employee's leave approver, or the person typed in FWD TO. Uses the shared approval
    engine sp_appr_route (value 0, so it stops at the first manager) unless FWD TO overrides it."""
    if fwd_to:
        if not erp.user(fwd_to):
            raise BahiError("ERR-LV-0410", "FWD TO USER NOT FOUND")
        erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
              "LV", app_no, fwd_to, "PENDING", requester, erp.now())
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(fwd_to)["email"], f"{app_no} awaiting your approval",
               f"Leave {app_no} for {emp['name']}")
        return fwd_to
    if emp["user_id"] and emp["lv_appr"] == erp.user(emp["user_id"])["manager_id"]:
        return erp.sp("sp_appr_route", "LV", app_no, emp["user_id"], 0)
    approver = emp["lv_appr"]
    erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
          "LV", app_no, approver, "PENDING", requester, erp.now())
    return approver


@proc("sp_lv_status_set")
def status_set(erp, lv_no: str, status: str, approver: str | None = None):
    erp.x("UPDATE lv_app SET status=?, decided_on=? WHERE lv_no=?", status,
          erp.now() if status in ("AP", "RJ", "CN") else None, lv_no)
    if approver:
        erp.x("UPDATE lv_app SET approver=? WHERE lv_no=?", approver, lv_no)
