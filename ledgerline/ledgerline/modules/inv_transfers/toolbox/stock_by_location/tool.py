"""Stock by location: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline  # noqa: F401

def run(s, item_code, warehouse=None):
    rows = _ledgerline(s, "tr_stk_enq", itm_cd=item_code, whs_cd=warehouse)["rows"]
    return {"ok": True, "item_code": item_code, "locations": rows, "count": len(rows)}
