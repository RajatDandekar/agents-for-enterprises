"""Release purchase order: Release an APPROVED purchase order to the supplier; only then does the supplier get it.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import release_purchase_order


def run(s, po_no):
    """Release, then read the order back: the receipt says whether it really reached the supplier."""
    return release_purchase_order(s, po_no)
