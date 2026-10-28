"""Order status: The real status of a purchase order or a purchase request, read from Bahi, with approval, goods received and any warning..

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi, _receipt


def run(s, po_no=None, request_no=None):
    if po_no:
        out = {"ok": True, **_receipt(s, po_no, tool="order_status")}
        grns = _bahi(s, "grn_search", po_no=po_no)["rows"]
        out["received"] = sum(g["qty"] for g in grns)
        out["goods_receipts"] = [g["grn_no"] for g in grns]
        if out["status_code"] == "CL":
            out["status"] = "CLOSED: everything received"
        return out
    if request_no:
        from bahi.toolbox.create_purchase_request.tool import _receipt as pr_receipt
        return {"ok": True, **pr_receipt(s, request_no)}
    raise ToolError("Give a po_no or a request_no.", "Ask the user for the document number.")
