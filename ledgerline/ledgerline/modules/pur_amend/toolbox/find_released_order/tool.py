"""Find released order: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline  # noqa: F401

def run(s, supplier=None, item_code=None):
    if not supplier and not item_code:
        raise ToolError("Give a supplier name or an item code.", "Ask the user which order they mean.")
    rows = _ledgerline(s, "pa_po_list", q=supplier, itm_cd=item_code)["rows"]
    orders = [{"po_no": r["po_no"], "supplier": f"{r['sup_name']} ({r['sup_cd']})", "item_code": r["itm_cd"],
               "item": r["descr"], "quantity": r["qty"], "need_by": r["need_dt"], "gross_value": r["gross_value"],
               "status": r["status"]} for r in rows]
    out = {"ok": True, "orders": orders, "count": len(orders)}
    if len(orders) > 1:
        out["next_step"] = "More than one order matches. Show them and ask the user which one."
    return out
