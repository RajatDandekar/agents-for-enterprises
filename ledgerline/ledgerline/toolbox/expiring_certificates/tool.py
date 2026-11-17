"""Expiring certificates: suppliers whose certificate (UN 38.3 by default) has expired or expires within N days,
with their open orders. AMD-SUP-2026-02 asks for a UN 38.3 certificate valid at least 60 days after an order.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline
from ledgerline.toolbox._ap import need_payables


def run(s, within_days=60, cert_type="UN38.3"):
    need_payables(s)
    if not 0 <= within_days <= 365:
        raise ToolError(f"within_days must be between 0 and 365, got {within_days}.", "Use 60 (the policy's window).")
    r = _ledgerline(s, "cert_expiry_list", within_days=within_days, cert_type=cert_type)
    rows = [{"supplier_code": c["sup_cd"], "supplier_name": c["sup_name"], "supplier_email": c["sup_email"], "cert_type": c["cert_type"],
             "doc_ref": c["doc_ref"], "valid_to": c["valid_to"], "days_left": c["days_left"], "state": c["state"],
             "open_orders": c["open_orders"]} for c in r["rows"]]
    return {"ok": True, "as_of": r["as_of"], "within_days": within_days, "certificates": rows, "count": len(rows),
            "expired": sum(1 for c in rows if c["state"] == "EXPIRED")}
