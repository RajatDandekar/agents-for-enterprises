"""Leave status: read Bahi's leave list for the signed-in employee. Input and output are in tool.json."""
from bahi.agent.tools import _bahi

STATUS = {"PA": "WAITING FOR APPROVAL", "AP": "APPROVED", "HD": "HELD: unpaid days, not sent to the approver",
          "RJ": "REJECTED", "CN": "CANCELLED"}


def run(s, leave_no=None):
    emp = _bahi(s, "lv_emp_get", user_id=s.user_id)
    rows = _bahi(s, "lv_list", emp_cd=emp["emp_cd"], lv_no=leave_no)["rows"]
    return {"ok": True, "count": len(rows), "applications": [
        {"leave_no": r["lv_no"], "type": r["lv_cd"], "from_date": r["from_dt"], "to_date": r["to_dt"], "days": r["days"],
         "unpaid_days": r["lwp_days"], "status": STATUS.get(r["status"], r["status"]), "approver": r["approver"]}
        for r in rows]}
