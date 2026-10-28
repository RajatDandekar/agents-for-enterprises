"""Create purchase request: Raise a purchase request (PR): the internal ask to buy something.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ServiceTimeout, ToolError, _bahi, _peek, content_key

# A request's own statuses (an order has more: released, received).
PR_STATUS = {"DR": "DRAFT (not submitted)", "PA": "WAITING FOR APPROVAL", "AP": "APPROVED", "RJ": "REJECTED",
             "CL": "CLOSED (an order was made from it)"}


def run(s, item_code, quantity, cost_centre, need_by, confirm=False):
    key = content_key("PR", s.user_id, item_code, quantity, cost_centre, need_by)
    # Idempotency: the same request, asked twice, is found instead of raised twice.
    for p in _bahi(s, "pr_search", raised_by=s.user_id)["rows"]:
        if f"key:{key}" in (p["remarks"] or "") and p["status"] != "RJ":
            if p["status"] == "DR":  # saved but never submitted (a lost reply): finish the job
                _bahi(s, "pr_submit", pr_no=p["pr_no"])
            return {"ok": True, "already_done": True, **_receipt(s, p["pr_no"])}
    rate = _bahi(s, "pr_fetch", itm_cd=item_code)["est_rate"]
    value = round(quantity * rate * 1.18, 2)  # Bahi estimates every request with 18% GST, so we do too
    me = _bahi(s, "usr_get", user_id=s.user_id)
    budget = _bahi(s, "bud_check", cc_cd=cost_centre, amount=0)
    preview = {"item_code": item_code, "quantity": quantity, "estimated_rate": rate, "estimated_value": value,
               "cost_centre": cost_centre, "cost_centre_state": budget["cc_state"], "need_by": need_by,
               "needs_approval": value > me["appr_limit"], "your_limit": me["appr_limit"],
               "approver": me["manager_id"] if value > me["appr_limit"] else None}
    warnings = []
    if budget["cc_state"] == "CLOSED":
        warnings.append(f"Cost centre {cost_centre} is CLOSED. Ask the user for an open one (check_budget lists them).")
    if not confirm:
        return {"ok": True, "preview": preview, "warnings": warnings,
                "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    if budget["cc_state"] == "CLOSED":
        raise ToolError(f"Cost centre {cost_centre} is closed.", "Ask the user for an open cost centre.")
    try:
        pr_no = _bahi(s, "pr_save", cc_cd=cost_centre, need_dt=need_by, itm_cd=item_code, qty=quantity,
                      est_rate=rate, remarks=f"key:{key}")["pr_no"]
    except ServiceTimeout:  # the reply was lost: look the request up by its key before anything else
        rows = [p for p in _bahi(s, "pr_search", raised_by=s.user_id)["rows"] if f"key:{key}" in (p["remarks"] or "")]
        if not rows:
            raise ToolError("Bahi timed out and the request was not saved.", "Call again with the same arguments.")
        pr_no = rows[0]["pr_no"]
    _bahi(s, "pr_submit", pr_no=pr_no)
    return {"ok": True, **_receipt(s, pr_no)}


def _receipt(s, pr_no):
    """Read the request back from Bahi: the status it really holds, and who it waits on."""
    p = _bahi(s, "pr_get", pr_no=pr_no)
    appr = _peek(s, "SELECT approver FROM approval WHERE doc_no=? AND status='PENDING'", pr_no)
    out = {"request_no": pr_no, "status": PR_STATUS.get(p["status"], p["status"]), "status_code": p["status"],
           "item_code": p["lines"][0]["itm_cd"], "quantity": p["lines"][0]["qty"], "estimated_value": p["est_value"],
           "cost_centre": p["cc_cd"], "need_by": p["need_dt"], "approver": appr["approver"] if appr else None,
           "approved_by": p["approved_by"]}
    if p["status"] == "PA":
        out["next_step"] = (f"Waiting for {out['approver']}. Nothing is ordered yet. Once approved, "
                            f"create_purchase_order with request_no={pr_no}.")
    elif p["status"] == "AP":
        out["next_step"] = f"Approved. Next: create_purchase_order with request_no={pr_no} and a supplier."
    return out
