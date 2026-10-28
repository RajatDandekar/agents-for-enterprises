"""Checks that A4's scaffolding works on a module kit: write one tool folder over hr_leave's services, load it,
lint it, call it in Kavita's session, serve it over MCP and capture the wire. Writes logs/a4_check.json."""
import json
import pathlib
import tempfile

from bahi.course.l4 import add_tool_dir, lint_tool
from bahi.erp.engine import ERP
from bahi.mcp_server import MCPClient
from bahi.toolbox import Toolbox
from bahi.toolbox.mcp import build_toolbox_server

root = pathlib.Path(tempfile.mkdtemp()) / "my_module_tools"
(root / "leave_balance").mkdir(parents=True)
(root / "leave_balance" / "tool.json").write_text(json.dumps({
    "name": "leave_balance", "title": "Leave balance", "category": "Look up", "writes": False, "version": "1.0",
    "description": "How many days of each kind of leave the signed-in person has left this year: casual, sick, earned, and any open compensatory offs.",
    "services": ["lv_emp_get", "lv_bal_get"],
    "input_schema": {"type": "object", "properties": {"year": {"type": "integer", "description": "e.g. 2026; leave out for this year"}}, "required": []},
    "example": {"year": 2026}}))
(root / "leave_balance" / "tool.py").write_text('''from bahi.agent.tools import _bahi


def run(s, year=2026):
    me = _bahi(s, "lv_emp_get", user_id=s.user_id)
    b = _bahi(s, "lv_bal_get", emp_cd=me["emp_cd"], yr=year)
    return {"ok": True, "employee": me["emp_cd"], "year": year,
            "balance": {r["lv_cd"]: r["bal"] for r in b["rows"]}, "comp_offs_open": len(b["co_open"])}
''')
erp = ERP(modules=["hr_leave"])
names = add_tool_dir(root)
out = {"names": names, "lint": {n: lint_tool(n) for n in names}}
out["call"] = Toolbox(erp, "KJOSHI", names=names).call("leave_balance", {})
c = MCPClient(build_toolbox_server(erp, "KJOSHI", names=names))
c.list_tools()
c.call_tool("leave_balance", {"year": 2026})
out["wire_methods"] = [w["method"] for w in c.wire]
out["wire_call_result"] = c.wire[-1]["result"]
c.close()
print(json.dumps(out, indent=1, default=str)[:1500])
(pathlib.Path(__file__).resolve().parent / "logs" / "a4_check.json").write_text(json.dumps(out, indent=1, default=str))
assert not any(out["lint"].values()) and out["call"]["ok"], out
print("A4 SCAFFOLD OK")
