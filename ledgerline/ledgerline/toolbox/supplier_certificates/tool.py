"""Supplier certificates: a supplier's certificates on file, and whether one is good enough for an item.

Input and output are described in tool.json next to this file. Built from scratch in Lecture 4:
    1 the job       Emma asks "Is Nordic Cell still certified?" and "Can Voltway supply BAT-500 under §6.2?"
    2 the services  sup_get (SUPPLIER MASTER GET), sup_cert_get (SUPPLIER CERT LIST), itm_get (ITEM MASTER GET)
    3 the schema    tool.json: supplier_code required; item_code, cert_type, limit, cursor optional
    4 the code      below: three reads, one clean result
    5 the errors    a wrong supplier or item code comes back as ok=false with next_step (from ERR-SUP-0030, ERR-ITM-0010)
    6 the tests     tests_toolbox.py, section "supplier_certificates"
"""
import datetime as dt

from ledgerline.agent.tools import ToolError, _ledgerline

PAGE, MAX_PAGE = 20, 50


def run(s, supplier_code, item_code=None, cert_type=None, limit=None, cursor=None):
    """Read the supplier, its certificate list and (optionally) the item; say what is valid today."""
    size = PAGE if limit is None else limit
    if not 1 <= size <= MAX_PAGE:
        raise ToolError(f"limit must be between 1 and {MAX_PAGE}, got {size}.", f"Call again with limit up to {MAX_PAGE}.")
    try:
        start = int(cursor) if cursor else 0
    except ValueError:
        raise ToolError(f"{cursor!r} is not a cursor this tool gave out.", "Call again without cursor to start at the first page.")
    sup = _ledgerline(s, "sup_get", sup_cd=supplier_code.strip().upper())
    today = s.erp.today  # Ledgerline's own date, not the laptop's
    rows = _ledgerline(s, "sup_cert_get", sup_cd=sup["sup_cd"])["rows"]
    certs = []
    for c in rows:
        days = (dt.date.fromisoformat(c["valid_to"]) - dt.date.fromisoformat(today)).days
        certs.append({"cert_type": c["cert_type"], "doc_ref": c["doc_ref"], "valid_to": c["valid_to"],
                      "valid": days >= 0, "days_left": days})
    un = [c for c in certs if c["cert_type"] == "UN38.3"]
    un38_3 = "valid" if any(c["valid"] for c in un) else ("expired" if un else "none")
    if cert_type:
        want = cert_type.replace(" ", "").upper()
        certs = [c for c in certs if c["cert_type"].replace(" ", "").upper() == want]
    certs.sort(key=lambda c: c["valid_to"], reverse=True)

    page = certs[start:start + size]
    nxt = str(start + size) if start + size < len(certs) else None

    out = {"ok": True, "supplier_code": sup["sup_cd"], "supplier_name": sup["name"], "supplier_status": sup["status"],
           "as_of": today, "certificates": page, "un38_3": un38_3, "item": None, "total": len(certs), "next_cursor": nxt}
    if item_code:
        item = _ledgerline(s, "itm_get", itm_cd=item_code.strip().upper())
        needs = bool(item["cell_safety"])
        out["item"] = {"item_code": item["itm_cd"], "needs_un38_3": needs,
                       "supplier_qualifies": (not needs) or un38_3 == "valid"}
        if needs and un38_3 != "valid":
            out["next_step"] = (f"{item['itm_cd']} contains lithium cells: Purchase Policy §6.2 needs a valid UN 38.3 "
                                f"certificate, and {sup['name']} has {'an expired one' if un38_3 == 'expired' else 'none'}. "
                                "Do not order from them; use find_supplier for a certified supplier.")
    if sup["status"] != "ACTIVE":
        out["next_step"] = (out.get("next_step", "") + f" {sup['sup_cd']} is {sup['status']}: never order from it.").strip()
    return out
