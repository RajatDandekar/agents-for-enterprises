"""Match invoice: the three-way match of a recorded invoice against its purchase order and goods receipts.

Input and output are described in tool.json next to this file. Safe to repeat: it only reads the order, the receipts
and the invoice, and sets the invoice to MATCHED when all three agree within the tolerance."""
from ledgerline.agent.tools import ToolError, _ledgerline
from ledgerline.toolbox._ap import STATUS, need_payables

WHAT_NEXT = {
    "matched": "Post it with post_invoice.",
    "price_variance": "Hold it (hold_invoice) and ask the buyer whether the new price was agreed.",
    "quantity_variance": "Hold it (hold_invoice): the supplier billed more than stores received.",
    "no_receipt": "Hold it (hold_invoice) until stores post the goods receipt; then match again.",
    "no_order": "Hold it (hold_invoice) and ask the supplier for the order number.",
    "supplier_mismatch": "Hold it (hold_invoice): the order is with another supplier.",
    "item_mismatch": "Hold it (hold_invoice): the order is for another item.",
    "order_not_released": "Hold it (hold_invoice): the order was never released.",
}


def run(s, invoice_no, price_tolerance_pct=None):
    need_payables(s)
    if price_tolerance_pct is not None and not 0 <= price_tolerance_pct <= 5:
        raise ToolError(f"price_tolerance_pct must be between 0 and 5 (the policy cap), got {price_tolerance_pct}.",
                        "Use the default (2%) or a smaller number.")
    r = _ledgerline(s, "inv_match", inv_no=invoice_no.strip().upper(),
                    **({"tol_pct": price_tolerance_pct} if price_tolerance_pct is not None else {}))
    keep = ("po_no", "ordered_qty", "received_qty", "invoiced_before", "invoiced_qty", "order_rate", "invoice_rate",
            "price_variance_pct", "tolerance_pct")
    return {"ok": True, "invoice_no": r["inv_no"], "result": r["result"], "matched": r["result"] == "matched",
            "note": r["note"], "status": STATUS[r["status"]], "status_code": r["status"],
            **{k: r[k] for k in keep if k in r}, "next_step": WHAT_NEXT.get(r["result"], "Hold it and tell AP.")}
