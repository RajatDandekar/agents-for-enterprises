"""Receive goods: Record goods received (GRN) against a RELEASED purchase order: stock goes up, and the order closes once everything has arrived.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline


def run(s, po_no, quantity, warehouse=None, remarks="", confirm=False):
    h = _ledgerline(s, "po_get", po_no=po_no)
    line = h["lines"][0]
    done = sum(g["qty"] for g in _ledgerline(s, "grn_search", po_no=po_no)["rows"])
    preview = {"po_no": po_no, "supplier_code": h["sup_cd"], "item_code": line["itm_cd"], "ordered": line["qty"],
               "received_before": done, "receiving_now": quantity, "balance_after": line["qty"] - done - quantity,
               "warehouse": warehouse or h["whs_cd"]}
    if h["status"] != "RL":
        raise ToolError(f"{po_no} is not open for receipt (status {h['status']}).",
                        "Only a RELEASED order can be received. Check order_status.")
    if not confirm:
        return {"ok": True, "preview": preview, "note": "Nothing has been saved. Confirm the count with the user."}
    r = _ledgerline(s, "grn_save", po_no=po_no, qty=quantity, remarks=remarks, **({"whs_cd": warehouse} if warehouse else {}))
    stock = _ledgerline(s, "stk_query", itm_cd=line["itm_cd"], whs_cd=warehouse or h["whs_cd"])
    return {"ok": True, "grn_no": r["grn_no"], "po_no": po_no, "item_code": line["itm_cd"], "received": quantity,
            "balance": r["balance"], "order_closed": r["balance"] == 0, "stock_after": stock["on_hand"]}
