"""Approve purchase order: Approve a purchase order that waits for the signed-in user's signature..

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import _bahi, _receipt


def run(s, po_no, comment=""):
    _bahi(s, "po_approve", po_no=po_no, comment=comment)
    return {"ok": True, **_receipt(s, po_no, tool="order_status"),
            "next_step": f"The buyer can now release_purchase_order {po_no}."}
