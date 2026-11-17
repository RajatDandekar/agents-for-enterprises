"""List invoices: supplier invoices in accounts payable, by status, supplier or order.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import _ledgerline
from ledgerline.toolbox._ap import CODES, STATUS, need_payables


def run(s, status="all", supplier_code=None, po_no=None):
    need_payables(s)
    args = {"status": CODES.get(status), "sup_cd": (supplier_code or "").strip().upper() or None,
            "po_no": (po_no or "").strip().upper() or None}
    rows = _ledgerline(s, "inv_search", **{k: v for k, v in args.items() if v})["rows"]
    out = [{"invoice_no": r["inv_no"], "supplier_invoice_no": r["sup_inv_no"], "supplier_code": r["sup_cd"],
            "supplier_name": r["sup_name"], "po_no": r["po_no"], "invoice_date": r["inv_dt"], "item_code": r["itm_cd"],
            "quantity": r["qty"], "unit_price": r["rate"], "gross": r["gross"], "status": STATUS[r["status"]],
            "status_code": r["status"], "match": r["match_result"], "note": r["match_note"] or r["hold_reason"],
            "due_date": r["due_dt"]} for r in rows]
    totals = {}
    for r in out:
        totals[r["status_code"]] = totals.get(r["status_code"], 0) + 1
    return {"ok": True, "invoices": out, "count": len(out), "by_status": {STATUS[k].split(" ")[0].lower(): v for k, v in totals.items()},
            "gross_total": round(sum(r["gross"] for r in out), 2)}
