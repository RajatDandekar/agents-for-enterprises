"""The HR leave kit's reference toolbox, as text: four tool folders a student would write in A4, in the course format.

scaffold(folder) writes them to disk (tool.json + tool.py each); leave_agent() builds Ask Northbridge on them over MCP.
The services behind them are the kit's black boxes (lv_emp_get, lv_bal_get, lv_hol_list, lv_fetch, lv_save, lv_list).
"""
from __future__ import annotations

import json
import pathlib

S = lambda d: {"type": "string", "description": d}  # noqa: E731

TOOLS = {
"check_leave_balance": None,  # the kit's starter tool, copied from ledgerline/modules/hr_leave/toolbox/

"working_days": ({
  "name": "working_days", "title": "Working days", "category": "HR", "writes": False, "version": "1.0",
  "description": "Count the working days between two dates (inclusive) at the employee's plant: Sundays and plant "
                 "holidays are not counted. Use it to turn 'Thursday and Friday' into dates and days before applying.",
  "services": ["lv_hol_list"],
  "input_schema": {"type": "object", "properties": {"from_date": S("YYYY-MM-DD"), "to_date": S("YYYY-MM-DD")},
                   "required": ["from_date", "to_date"]},
  "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "days": {"type": "number"},
                                                     "dates": {"type": "array"}, "holidays": {"type": "array"}}},
  "example": {"from_date": "2026-10-29", "to_date": "2026-10-30"}},
'''"""Working days: count the leave days Ledgerline will charge. Input and output are in tool.json."""
import datetime as dt

from ledgerline.agent.tools import ToolError, _ledgerline


def run(s, from_date, to_date):
    a, b = dt.date.fromisoformat(from_date), dt.date.fromisoformat(to_date)
    if b < a:
        raise ToolError("to_date is before from_date.", "Ask the user for the dates again.")
    hol = {h["hol_dt"]: h["descr"] for h in _ledgerline(s, "lv_hol_list")["rows"]}
    dates, skipped = [], []
    d = a
    while d <= b:
        iso = d.isoformat()
        if d.weekday() == 6 or iso in hol:
            skipped.append({"date": iso, "why": hol.get(iso, "Sunday")})
        else:
            dates.append(iso)
        d += dt.timedelta(days=1)
    return {"ok": True, "days": len(dates), "dates": dates, "holidays": skipped}
'''),

"apply_leave": ({
  "name": "apply_leave", "title": "Apply for leave", "category": "HR", "writes": True, "version": "1.0",
  "description": "Apply for leave for the signed-in employee. leave_type: CL casual, EL earned, SL sick. confirm=false "
                 "previews the days, the balance, any unpaid days and who approves, and saves nothing; confirm=true "
                 "applies. If the balance of the chosen type does not cover every day, Ledgerline holds the application "
                 "unpaid and it never reaches the approver: pick a type that covers it (the preview says which).",
  "services": ["lv_emp_get", "lv_bal_get", "lv_hol_list", "lv_fetch", "lv_save", "lv_list"],
  "input_schema": {"type": "object", "properties": {
      "leave_type": {"type": "string", "enum": ["CL", "EL", "SL"], "description": "CL, EL or SL"},
      "from_date": S("YYYY-MM-DD"), "to_date": S("YYYY-MM-DD"), "reason": S("in the employee's words"),
      "confirm": {"type": "boolean", "description": "false (default) = preview only; true = apply"}},
      "required": ["leave_type", "from_date", "to_date", "reason"]},
  "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "leave_no": {"type": "string"},
                    "status": {"type": "string", "description": "WAITING FOR APPROVAL, APPROVED, HELD (unpaid) ..."},
                    "unpaid_days": {"type": "number"}, "warning": {"type": "string"}}},
  "example": {"leave_type": "EL", "from_date": "2026-10-29", "to_date": "2026-10-30", "reason": "sister's wedding"}},
'''"""Apply for leave: preview, key, look up, save, read back. Input and output are in tool.json."""
import datetime as dt

from ledgerline.agent.tools import ToolError, _ledgerline, content_key
from ledgerline.erp.engine import ServiceTimeout

STATUS = {"PA": "WAITING FOR APPROVAL", "AP": "APPROVED", "HD": "HELD: unpaid days, not sent to the approver",
          "RJ": "REJECTED", "CN": "CANCELLED"}


def _days(s, a, b):
    hol = {h["hol_dt"] for h in _ledgerline(s, "lv_hol_list")["rows"]}
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return sum(1 for i in range((b - a).days + 1)
               if (a + dt.timedelta(i)).weekday() != 6 and (a + dt.timedelta(i)).isoformat() not in hol)


def _receipt(s, lv_no):
    r = _ledgerline(s, "lv_list", lv_no=lv_no)["rows"][0]
    out = {"ok": True, "leave_no": lv_no, "status": STATUS.get(r["status"], r["status"]), "status_code": r["status"],
           "leave_type": r["lv_cd"], "from_date": r["from_dt"], "to_date": r["to_dt"], "days": r["days"],
           "unpaid_days": r["lwp_days"], "approver": r["approver"], "idempotency_key": r["client_ref"]}
    if r["status"] == "HD":
        out["warning"] = (f"Saved but HELD: {r['lwp_days']} day(s) without pay, and it has NOT gone to the approver. "
                          "Tell the user plainly; cancel it and apply with a type that covers all the days.")
    return out


def run(s, leave_type, from_date, to_date, reason, confirm=False):
    emp = _ledgerline(s, "lv_emp_get", user_id=s.user_id)
    days = _days(s, from_date, to_date)
    if days == 0:
        raise ToolError("Those dates are all holidays or Sundays.", "Check the dates with the user.")
    key = content_key("LV", s.user_id, emp["emp_cd"], leave_type, from_date, to_date)
    found = _ledgerline(s, "lv_list", client_ref=key)["rows"]
    if found:
        return {**_receipt(s, found[0]["lv_no"]), "already_done": True}
    bal = {r["lv_cd"]: r["bal"] for r in _ledgerline(s, "lv_bal_get", emp_cd=emp["emp_cd"])["rows"]}
    unpaid = max(0, days - bal.get(leave_type, 0))
    covers = [t for t in ("CL", "EL", "SL") if bal.get(t, 0) >= days and t != leave_type]
    f = _ledgerline(s, "lv_fetch", emp_cd=emp["emp_cd"], lv_cd=leave_type)
    preview = {"employee": f"{emp['name']} ({emp['emp_cd']})", "leave_type": leave_type, "from_date": from_date,
               "to_date": to_date, "days": days, "balance": bal.get(leave_type, 0), "unpaid_days": unpaid,
               "approver": f["lv_appr"]}
    warnings = []
    if unpaid:
        warnings.append(f"{leave_type} covers only {bal.get(leave_type, 0)} of {days} days: Ledgerline would HOLD this, "
                        f"{unpaid} day(s) unpaid, never sent to the approver."
                        + (f" {', '.join(covers)} covers all {days}." if covers else ""))
    if not confirm:
        return {"ok": True, "preview": preview, "warnings": warnings,
                "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    try:
        lv_no = _ledgerline(s, "lv_save", emp_cd=emp["emp_cd"], lv_cd=leave_type, from_dt=from_date, to_dt=to_date,
                      reason=reason, fetch_tok=f["fetch_tok"], client_ref=key)["lv_no"]
    except ServiceTimeout:
        rows = _ledgerline(s, "lv_list", client_ref=key)["rows"]
        if not rows:
            raise ToolError("Ledgerline timed out and the leave was not saved.", "Call again with the same arguments.")
        lv_no = rows[0]["lv_no"]
    return _receipt(s, lv_no)
'''),

"leave_status": ({
  "name": "leave_status", "title": "Leave status", "category": "HR", "writes": False, "version": "1.0",
  "description": "The signed-in employee's leave applications with their real status in words (waiting, approved, "
                 "held unpaid), days, unpaid days and approver. Give leave_no for one application.",
  "services": ["lv_emp_get", "lv_list"],
  "input_schema": {"type": "object", "properties": {"leave_no": S("e.g. LV/2026/00388; blank = all of mine")},
                   "required": []},
  "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "applications": {"type": "array"}}},
  "example": {}},
'''"""Leave status: read Ledgerline's leave list for the signed-in employee. Input and output are in tool.json."""
from ledgerline.agent.tools import _ledgerline

STATUS = {"PA": "WAITING FOR APPROVAL", "AP": "APPROVED", "HD": "HELD: unpaid days, not sent to the approver",
          "RJ": "REJECTED", "CN": "CANCELLED"}


def run(s, leave_no=None):
    emp = _ledgerline(s, "lv_emp_get", user_id=s.user_id)
    rows = _ledgerline(s, "lv_list", emp_cd=emp["emp_cd"], lv_no=leave_no)["rows"]
    return {"ok": True, "count": len(rows), "applications": [
        {"leave_no": r["lv_no"], "type": r["lv_cd"], "from_date": r["from_dt"], "to_date": r["to_dt"], "days": r["days"],
         "unpaid_days": r["lwp_days"], "status": STATUS.get(r["status"], r["status"]), "approver": r["approver"]}
        for r in rows]}
'''),
}

LEAVE_PROMPT = """You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester. You work inside Northbridge's
Ledgerline ERP for {name} ({user}), {role}, with {first}'s own Ledgerline permissions and nobody else's. Today is Monday
26 October 2026; Thursday is 29 October and Friday is 30 October.

How you work
- Every fact (balances, dates, holidays, statuses, rules) comes from a tool. Never guess.
- To apply for leave: count the working days, check the balance, then call apply_leave with confirm=false and show
  the preview (type, dates, days, unpaid days, approver). Pick a leave type that covers every day, so nothing is
  unpaid. Ask {first} to confirm; call it again with confirm=true only after a clear yes.
- Report the status the receipt gives you, in plain words. A leave waiting for approval is not approved: say who it
  waits for. Never say approved unless the status is APPROVED.
- For a question about a leave rule, call search_policy and cite the clause.
- Short, plain replies: two to six lines. No emoji."""


def scaffold(folder="my_module_tools") -> list[str]:
    """Write the four reference tool folders. check_leave_balance is copied from the kit."""
    root = pathlib.Path(folder)
    kit = pathlib.Path(__file__).resolve().parents[2] / "modules" / "hr_leave" / "toolbox" / "check_leave_balance"
    names = []
    for name, spec in TOOLS.items():
        d = root / name
        d.mkdir(parents=True, exist_ok=True)
        if spec is None:
            (d / "tool.json").write_text((kit / "tool.json").read_text())
            (d / "tool.py").write_text((kit / "tool.py").read_text())
        else:
            (d / "tool.json").write_text(json.dumps(spec[0], indent=2, ensure_ascii=False) + "\n")
            (d / "tool.py").write_text(spec[1])
        names.append(name)
    return names


def leave_agent(model: str, cassette: str, folder="my_module_tools", keep: list | None = None, with_policy=True):
    """make_agent(erp, user) for run_module_scenario: Ask Northbridge (ledgerline.course.l7) over MCP on the kit's folders."""
    from ...llm import LLM
    from ...mcp_server import MCPClient, MCPClientTools
    from ...modules._toolbox import build_module_server
    from ..l7.agent import AskNorthbridge

    def mk(erp, user):
        server = build_module_server(erp, user, folder=folder, with_purchasing=["search_policy"] if with_policy else ())
        client = MCPClient(server)
        a = AskNorthbridge(erp, user, llm=LLM(model, cassette=cassette), tools=MCPClientTools(client), prompt=LEAVE_PROMPT)
        a.client = client
        if keep is not None:
            keep.append(a)
        return a
    return mk
