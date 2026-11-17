"""Hold invoice: stop an invoice from being paid until a person has looked, with the reason.

Input and output are described in tool.json next to this file. Holding twice is harmless."""
from ledgerline.agent.tools import ToolError, _ledgerline
from ledgerline.toolbox._ap import STATUS, need_payables


def run(s, invoice_no, reason):
    need_payables(s)
    if len(reason.strip()) < 4:
        raise ToolError("Give a reason a person can act on.", "Say what is wrong, e.g. 'price 6% above PO/2026/01133'.")
    h = _ledgerline(s, "inv_get", inv_no=invoice_no.strip().upper())
    if h["status"] == "HD":
        return {"ok": True, "already_done": True, "invoice_no": h["inv_no"], "status": STATUS["HD"], "status_code": "HD",
                "reason": h["hold_reason"]}
    _ledgerline(s, "inv_hold", inv_no=h["inv_no"], reason=reason.strip())
    return {"ok": True, "invoice_no": h["inv_no"], "status": STATUS["HD"], "status_code": "HD", "reason": reason.strip(),
            "gross": h["gross"]}
