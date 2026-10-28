"""Create purchase order: Create a purchase order (PO) with a supplier.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ServiceTimeout, ToolError, _bahi, _receipt, _tax_code, content_key


def run(s, supplier_code, request_no=None, item_code=None, quantity=None, cost_centre=None, need_by=None,
        rate=None, confirm=False):
    if request_no:  # the request carries what to buy, how many, who pays and by when
        pr = _bahi(s, "pr_get", pr_no=request_no)
        item_code, quantity = pr["lines"][0]["itm_cd"], pr["lines"][0]["qty"]
        cost_centre, need_by = pr["cc_cd"], pr["need_dt"]
    elif not all([item_code, quantity, cost_centre, need_by]):
        raise ToolError("A direct order needs item_code, quantity, cost_centre and need_by.",
                        "Ask the user, or raise a purchase request first.")
    key = content_key("PO", s.user_id, supplier_code, item_code, quantity, cost_centre, need_by)
    found = _bahi(s, "po_search", client_ref=key)["rows"]
    if not found and request_no and pr["status"] != "AP":  # checked after the key: a retry finds its order first
        raise ToolError(f"Request {request_no} is not approved (status {pr['status']}).",
                        "Wait for the approver, or check order_status.")
    if found:
        out = {"ok": True, "already_done": True, "note": "This order already exists.", **_receipt(s, found[0]["po_no"])}
        if out["status_code"] == "CL":
            out["status"] = "CLOSED: everything received"
        return out
    sup = _bahi(s, "sup_get", sup_cd=supplier_code)
    if sup["status"] != "ACTIVE":
        raise ToolError(f"{supplier_code} is {sup['status']}.", "Pick an active supplier with find_supplier.")
    contract = _bahi(s, "sup_rate_get", sup_cd=supplier_code, itm_cd=item_code)["current"]
    if rate is None:
        if not contract:
            raise ToolError(f"No current rate contract with {supplier_code} for {item_code}.", "Ask the user for the rate.")
        rate = contract["rate"]
    tax_cd = _tax_code(s, supplier_code)  # from the supplier's state, not Bahi's default (the ERR-PO-0412 trap)
    basic = round(quantity * rate, 2)
    gross = _bahi(s, "tax_compute", basic=basic, tax_cd=tax_cd)["gross"]
    if not request_no and gross > 50000:
        raise ToolError(f"A direct order is limited to Rs 50,000; this one is Rs {gross:,.0f}.",
                        "Raise a purchase request first with create_purchase_request.")
    budget = _bahi(s, "bud_check", cc_cd=cost_centre, amount=0)
    preview = {"supplier": f"{sup['name']} ({supplier_code})", "item_code": item_code, "quantity": quantity,
               "rate": rate, "tax_code": tax_cd, "basic_value": basic, "gross_value": gross,
               "cost_centre": cost_centre, "cost_centre_state": budget["cc_state"], "need_by": need_by,
               "request_no": request_no}
    warnings = []
    if budget["cc_state"] == "CLOSED":
        warnings.append(f"Cost centre {cost_centre} is CLOSED: Bahi would save this order as a DRAFT that never "
                        "reaches the supplier.")
    if not confirm:
        return {"ok": True, "preview": preview, "warnings": warnings,
                "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    f = _bahi(s, "po_fetch", sup_cd=supplier_code, itm_cd=item_code, **({"pr_no": request_no} if request_no else {}))
    payload = dict(po_type="STD" if request_no else "DIR", sup_cd=supplier_code, itm_cd=item_code, qty=quantity,
                   rate=rate, tax_cd=tax_cd, cc_cd=cost_centre, need_dt=need_by, fetch_tok=f["fetch_tok"], client_ref=key)
    if request_no:
        payload["pr_no"] = request_no
    try:
        po_no = _bahi(s, "po_save", **payload)["doc_no"]
    except ServiceTimeout:  # a lost reply: look the order up by its key before anything else
        rows = _bahi(s, "po_search", client_ref=key)["rows"]
        if not rows:
            raise ToolError("Bahi timed out and the order was not saved.", "Call again with the same arguments.")
        po_no = rows[0]["po_no"]
    out = {"ok": True, **_receipt(s, po_no)}
    if out["status_code"] == "AP":
        out["next_step"] = f"Approved but NOT sent to the supplier yet. Next: release_purchase_order {po_no}."
    elif out["status_code"] == "PA":
        out["next_step"] = f"Waiting for {out['approval']['approver'] if out.get('approval') else 'the approver'}."
    return out
