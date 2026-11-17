"""Post invoice: post a MATCHED invoice to the ledger, so it is paid on its due date.

Input and output are described in tool.json next to this file. Preview first (confirm=false). Only a matched invoice
can be posted; posting twice is refused by Ledgerline and reported as already done."""
import datetime as dt

from ledgerline.agent.tools import ServiceTimeout, ToolError, _ledgerline
from ledgerline.toolbox._ap import STATUS, need_payables


def run(s, invoice_no, confirm=False):
    need_payables(s)
    h = _ledgerline(s, "inv_get", inv_no=invoice_no.strip().upper())
    if h["status"] == "PS":
        return {"ok": True, "already_done": True, "invoice_no": h["inv_no"], "status": STATUS["PS"], "status_code": "PS",
                "due_date": h["due_dt"], "gross": h["gross"]}
    if h["status"] != "MT":
        raise ToolError(f"{h['inv_no']} is {STATUS[h['status']]}: only a matched invoice can be posted.",
                        "Run match_invoice first; if it does not match, hold it.")
    sup = _ledgerline(s, "sup_get", sup_cd=h["sup_cd"])
    days = {r["pt_cd"]: r["days"] for r in _ledgerline(s, "pt_list")["rows"]}.get(sup["pt_cd"], 30)
    due = (dt.date.fromisoformat(h["inv_dt"]) + dt.timedelta(days=days)).isoformat()
    preview = {"invoice_no": h["inv_no"], "supplier": f"{sup['name']} ({sup['sup_cd']})", "supplier_invoice_no": h["sup_inv_no"],
               "po_no": h["po_no"], "gross": h["gross"], "due_date": due}
    if not confirm:
        return {"ok": True, "preview": preview, "note": "Nothing has been posted. Confirm to post it."}
    try:
        r = _ledgerline(s, "inv_post", inv_no=h["inv_no"])
    except ServiceTimeout:
        again = _ledgerline(s, "inv_get", inv_no=h["inv_no"])
        if again["status"] != "PS":
            raise ToolError("Ledgerline timed out and the invoice was not posted.", "Call again with the same arguments.")
        r = {"due_dt": again["due_dt"]}
    return {"ok": True, "invoice_no": h["inv_no"], "status": STATUS["PS"], "status_code": "PS", "due_date": r["due_dt"],
            "gross": h["gross"], "supplier_code": h["sup_cd"]}
