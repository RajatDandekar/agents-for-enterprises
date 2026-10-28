"""Invoice status: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi  # noqa: F401

def run(s, invoice_no, supplier=None):
    rows = _bahi(s, "ap_inv_list", sup_inv_no=invoice_no)["rows"]
    if supplier:
        rows = [r for r in rows if supplier.lower() in r["sup_name"].lower()] or rows
    inv = [{"ap_no": r["ap_no"], "supplier": f"{r['sup_name']} ({r['sup_cd']})", "invoice_no": r["sup_inv_no"],
            "invoice_date": r["inv_dt"], "po_no": r["po_no"], "gross": r["gross"], "status": r["status"],
            "hold_code": r["hold_cd"], "due_date": r["due_dt"]} for r in rows]
    out = {"ok": True, "invoices": inv, "count": len(inv)}
    if len(inv) > 1:
        out["next_step"] = "Several invoices carry this number. Ask the user which supplier."
    return out
