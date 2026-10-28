"""Apply for leave: preview, key, look up, save, read back. Input and output are in tool.json."""
import datetime as dt

from bahi.agent.tools import ToolError, _bahi, content_key
from bahi.erp.engine import ServiceTimeout

STATUS = {"PA": "WAITING FOR APPROVAL", "AP": "APPROVED", "HD": "HELD: unpaid days, not sent to the approver",
          "RJ": "REJECTED", "CN": "CANCELLED"}


def _days(s, a, b):
    hol = {h["hol_dt"] for h in _bahi(s, "lv_hol_list")["rows"]}
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return sum(1 for i in range((b - a).days + 1)
               if (a + dt.timedelta(i)).weekday() != 6 and (a + dt.timedelta(i)).isoformat() not in hol)


def _receipt(s, lv_no):
    r = _bahi(s, "lv_list", lv_no=lv_no)["rows"][0]
    out = {"ok": True, "leave_no": lv_no, "status": STATUS.get(r["status"], r["status"]), "status_code": r["status"],
           "leave_type": r["lv_cd"], "from_date": r["from_dt"], "to_date": r["to_dt"], "days": r["days"],
           "unpaid_days": r["lwp_days"], "approver": r["approver"], "idempotency_key": r["client_ref"]}
    if r["status"] == "HD":
        out["warning"] = (f"Saved but HELD: {r['lwp_days']} day(s) without pay, and it has NOT gone to the approver. "
                          "Tell the user plainly; cancel it and apply with a type that covers all the days.")
    return out


def run(s, leave_type, from_date, to_date, reason, confirm=False):
    emp = _bahi(s, "lv_emp_get", user_id=s.user_id)
    days = _days(s, from_date, to_date)
    if days == 0:
        raise ToolError("Those dates are all holidays or Sundays.", "Check the dates with the user.")
    key = content_key("LV", s.user_id, emp["emp_cd"], leave_type, from_date, to_date)
    found = _bahi(s, "lv_list", client_ref=key)["rows"]
    if found:
        return {**_receipt(s, found[0]["lv_no"]), "already_done": True}
    bal = {r["lv_cd"]: r["bal"] for r in _bahi(s, "lv_bal_get", emp_cd=emp["emp_cd"])["rows"]}
    unpaid = max(0, days - bal.get(leave_type, 0))
    covers = [t for t in ("CL", "EL", "SL") if bal.get(t, 0) >= days and t != leave_type]
    f = _bahi(s, "lv_fetch", emp_cd=emp["emp_cd"], lv_cd=leave_type)
    preview = {"employee": f"{emp['name']} ({emp['emp_cd']})", "leave_type": leave_type, "from_date": from_date,
               "to_date": to_date, "days": days, "balance": bal.get(leave_type, 0), "unpaid_days": unpaid,
               "approver": f["lv_appr"]}
    warnings = []
    if unpaid:
        warnings.append(f"{leave_type} covers only {bal.get(leave_type, 0)} of {days} days: Bahi would HOLD this, "
                        f"{unpaid} day(s) unpaid, never sent to the approver."
                        + (f" {', '.join(covers)} covers all {days}." if covers else ""))
    if not confirm:
        return {"ok": True, "preview": preview, "warnings": warnings,
                "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    try:
        lv_no = _bahi(s, "lv_save", emp_cd=emp["emp_cd"], lv_cd=leave_type, from_dt=from_date, to_dt=to_date,
                      reason=reason, fetch_tok=f["fetch_tok"], client_ref=key)["lv_no"]
    except ServiceTimeout:
        rows = _bahi(s, "lv_list", client_ref=key)["rows"]
        if not rows:
            raise ToolError("Bahi timed out and the leave was not saved.", "Call again with the same arguments.")
        lv_no = rows[0]["lv_no"]
    return _receipt(s, lv_no)
