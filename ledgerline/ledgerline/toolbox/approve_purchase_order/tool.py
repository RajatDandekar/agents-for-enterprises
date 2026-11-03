"""Approve purchase order: Approve a purchase order that waits for the signed-in user's signature..

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ServiceTimeout, _ledgerline, _receipt


def run(s, po_no, comment=""):
    try:
        _ledgerline(s, "po_approve", po_no=po_no, comment=comment)
    except ServiceTimeout:  # the reply was lost: the read-back below shows whether Ledgerline approved it
        if _ledgerline(s, "po_get", po_no=po_no)["status"] == "PA":
            raise
    return {"ok": True, **_receipt(s, po_no, tool="order_status"),
            "next_step": f"The buyer can now release_purchase_order {po_no}."}
