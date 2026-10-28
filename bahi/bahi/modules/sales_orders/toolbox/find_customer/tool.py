"""Find customer: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi  # noqa: F401

def run(s, name, city=None):
    rows = _bahi(s, "so_cust_search", q=name)["rows"]
    if city:
        rows = [r for r in rows if (r["city"] or "").lower() == city.lower()] or rows
    cust = [{"customer_code": r["cust_cd"], "name": r["name"], "city": r["city"], "state": r["state"],
             "type": r["cust_type"], "status": r["status"]} for r in rows]
    out = {"ok": True, "customers": cust, "count": len(cust)}
    if len(cust) > 1:
        out["next_step"] = "Several customers match. Show them and ask the user which one."
    return out
