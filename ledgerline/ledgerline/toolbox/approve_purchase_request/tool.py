"""Approve purchase request: Approve or reject a purchase request that waits for the signed-in user.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ServiceTimeout, _ledgerline
from ledgerline.toolbox.create_purchase_request.tool import PR_STATUS


def run(s, request_no, decision, comment=""):
    try:
        r = _ledgerline(s, "pr_approve", pr_no=request_no, decision="A" if decision == "approve" else "R", comment=comment)
    except ServiceTimeout:  # the reply was lost: read the request back; Ledgerline holds the decision if it was made
        r = _ledgerline(s, "pr_get", pr_no=request_no)
        if r["status"] == "PA":
            raise
    out = {"ok": True, "request_no": request_no, "status": PR_STATUS.get(r["status"], r["status"]),
           "status_code": r["status"], "decided_by": s.user_id}
    if r["status"] == "AP":
        out["next_step"] = f"The requester can now create_purchase_order with request_no={request_no}."
    return out
