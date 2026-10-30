"""Check leave balance: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline  # noqa: F401

def run(s, employee_name=None):
    if employee_name:
        rows = _ledgerline(s, "lv_emp_get", q=employee_name)["rows"]
        if len(rows) != 1:
            return {"ok": True, "matches": rows, "next_step": "Several employees match. Ask the user which one."}
        emp = rows[0]
    else:
        emp = _ledgerline(s, "lv_emp_get", user_id=s.user_id)
    bal = _ledgerline(s, "lv_bal_get", emp_cd=emp["emp_cd"])
    return {"ok": True, "employee_code": emp["emp_cd"], "name": emp["name"],
            "balances": {r["lv_cd"]: r["bal"] for r in bal["rows"]},
            "pending": {r["lv_cd"]: r["pending"] for r in bal["rows"] if r["pending"]},
            "comp_offs_open": bal["co_open"]}
