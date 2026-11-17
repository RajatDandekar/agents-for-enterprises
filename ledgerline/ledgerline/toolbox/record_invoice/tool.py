"""Record invoice: enter a supplier invoice into Ledgerline's accounts payable (status RECEIVED), once.

Input and output are described in tool.json next to this file. Preview first (confirm=false). The same supplier
invoice number is never recorded twice: a resent invoice comes back ok=false with ledgerline_code DUPLICATE."""
from ledgerline.agent.tools import ServiceTimeout, ToolError, _ledgerline
from ledgerline.toolbox._ap import STATUS, need_payables


def _supplier(s, supplier, po):
    code = supplier.strip().upper()
    if po:  # the order names the supplier: the strongest evidence
        if code in (po["sup_cd"], "") or supplier.strip().lower() in _ledgerline(s, "sup_get", sup_cd=po["sup_cd"])["name"].lower():
            return po["sup_cd"]
    try:
        return _ledgerline(s, "sup_get", sup_cd=code)["sup_cd"]
    except ToolError:
        pass
    words = [w for w in supplier.replace(",", " ").split() if len(w) > 2 and w.lower() not in ("ltd", "limited", "the", "co.")]
    rows = _ledgerline(s, "sup_search", q=words[0] if words else supplier)["rows"] if words else []
    rows = [r for r in rows if r["status"] == "ACTIVE"]
    if len(rows) == 1:
        return rows[0]["sup_cd"]
    raise ToolError(f"Cannot tell which supplier '{supplier}' is ({len(rows)} matches).",
                    "Look the supplier up with find_supplier and pass its code.")


def run(s, supplier, supplier_invoice_no, invoice_date, item_code, quantity, unit_price, po_no=None, vat=None,
        source_message_id=None, confirm=False):
    need_payables(s)
    po = None
    if po_no:
        try:
            po = _ledgerline(s, "po_get", po_no=po_no.strip().upper())
        except ToolError:
            po = None  # recorded anyway; the three-way match will say there is no such order
    sup = _supplier(s, supplier, po)
    dup = _ledgerline(s, "inv_search", sup_cd=sup, sup_inv_no=supplier_invoice_no.strip())["rows"]
    if dup:
        d = dup[0]
        raise ToolError(f"Duplicate: {supplier_invoice_no} from {d['sup_name']} is already recorded as {d['inv_no']} "
                        f"({STATUS[d['status']]}). Not recorded again.",
                        "Do not record or pay it twice. Leave it, and tell accounts payable it was resent.", "DUPLICATE")
    net = round(quantity * unit_price, 2)
    preview = {"supplier_code": sup, "supplier_invoice_no": supplier_invoice_no.strip(), "invoice_date": invoice_date,
               "po_no": po["po_no"] if po else (po_no or None), "po_found": bool(po), "item_code": item_code.strip().upper(),
               "quantity": quantity, "unit_price": unit_price, "net": net}
    if not confirm:
        return {"ok": True, "preview": preview, "note": "Nothing has been saved. Confirm to record it."}
    args = dict(sup_cd=sup, sup_inv_no=supplier_invoice_no.strip(), inv_dt=invoice_date, itm_cd=item_code.strip().upper(),
                qty=quantity, rate=unit_price, po_no=preview["po_no"], vat=vat, src_ref=source_message_id)
    try:
        r = _ledgerline(s, "inv_save", **{k: v for k, v in args.items() if v is not None})
    except ServiceTimeout:  # the reply was lost: was it saved? look it up by the supplier's own number
        rows = _ledgerline(s, "inv_search", sup_cd=sup, sup_inv_no=supplier_invoice_no.strip())["rows"]
        if not rows:
            raise ToolError("Ledgerline timed out and the invoice was not recorded.", "Call again with the same arguments.")
        r = {"inv_no": rows[0]["inv_no"], "net": rows[0]["net"], "vat": rows[0]["vat"], "gross": rows[0]["gross"]}
    if source_message_id:
        try:
            _ledgerline(s, "mail_mark", msg_id=source_message_id.strip().upper(), status="DONE")
        except ToolError:
            pass
    return {"ok": True, "invoice_no": r["inv_no"], "status": STATUS["RC"], "status_code": "RC", "supplier_code": sup,
            "po_no": preview["po_no"], "net": r["net"], "vat": r["vat"], "gross": r["gross"],
            "next_step": f"Match it: match_invoice with invoice_no={r['inv_no']}."}
