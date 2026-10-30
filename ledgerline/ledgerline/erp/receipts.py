"""Goods receipt (GRN): the third step of procure-to-pay. Stores counts what arrived against a released order.

    PR (request) ──approve──> PO (order) ──release──> supplier ships ──> GRN (goods received) ──> stock goes up

Installed on demand, so the older lectures' service lists do not change:

    erp = ERP(); install_receipts(erp)
    erp.call("grn_save", {"po_no": "PO/2026/01182", "qty": 2000}, user="ATANAKA")

A GRN raises on-hand stock, lowers on-order stock, writes the stock ledger, and closes the order once
everything has arrived. Receiving more than was ordered is refused (ERR-GRN-0204), as is receiving against an
order that was never released (ERR-GRN-0102).
"""
from __future__ import annotations

from .engine import LedgerlineError, service

F = lambda name, t="str", req=False, desc="": (name, t, req, desc)  # noqa: E731  (same as services.py)

SCHEMA = """
CREATE TABLE IF NOT EXISTS grn_hdr(grn_no TEXT PRIMARY KEY, po_no TEXT, whs_cd TEXT, received_by TEXT,
    received_on TEXT, remarks TEXT);
CREATE TABLE IF NOT EXISTS grn_line(grn_no TEXT, line_no INT, itm_cd TEXT, qty INT);
"""
# Who may receive goods, and who may look receipts up.
PERMS = {"STORES": ["grn_save", "grn_get", "grn_search"], "PUR-EXEC": ["grn_save", "grn_get", "grn_search"],
         "PUR-MGR": ["grn_get", "grn_search"], "PUR-SR": ["grn_get", "grn_search"],
         "PLANT-HEAD": ["grn_get", "grn_search"]}


def install_receipts(erp) -> None:
    """Add the GRN tables, numbering and permissions to a running sandbox. Safe to call twice."""
    if erp.q1("SELECT 1 FROM doc_seq WHERE doc_type='GRN'"):
        return
    erp.db.executescript(SCHEMA)
    erp.x("INSERT INTO doc_seq VALUES ('GRN','GRN/2026/',30001,5)")
    for role, svcs in PERMS.items():
        for s in svcs:
            erp.x("INSERT INTO role_perm VALUES (?,?)", role, s)
    erp.db.commit()


def _received(erp, po_no: str) -> int:
    r = erp.q1("SELECT COALESCE(SUM(l.qty),0) AS q FROM grn_line l JOIN grn_hdr h ON h.grn_no=l.grn_no "
               "WHERE h.po_no=?", po_no)
    return int(r["q"])


def _next_no(erp) -> str:
    seq = erp.q1("SELECT * FROM doc_seq WHERE doc_type='GRN'")
    erp.x("UPDATE doc_seq SET next_no=next_no+1 WHERE doc_type='GRN'")
    return f"{seq['prefix']}{str(seq['next_no']).zfill(seq['width'])}"


@service("grn_save", "GOODS RECEIPT SAVE", [F("po_no", req=True, desc="PO NO"), F("qty", "int", True, "QTY RECD"),
                                            F("whs_cd", desc="WHS CD"), F("remarks", desc="REMARKS")],
         kind="write", screen="INV-GRN-03")
def grn_save(erp, user, po_no, qty, whs_cd=None, remarks=""):
    h = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", po_no)
    if not h:
        raise LedgerlineError("ERR-PO-0001", "PO NOT FOUND")
    if h["status"] not in ("RL", "CL"):
        raise LedgerlineError("ERR-GRN-0102", f"PO NOT RELEASED ({h['status']})")
    if h["status"] == "CL":
        raise LedgerlineError("ERR-GRN-0105", "PO ALREADY FULLY RECEIVED")
    qty = int(qty)
    if qty <= 0:
        raise LedgerlineError("ERR-GRN-0201", "QTY MUST BE > 0")
    line = erp.q1("SELECT * FROM po_line WHERE po_no=?", po_no)
    done = _received(erp, po_no)
    if done + qty > line["qty"]:
        raise LedgerlineError("ERR-GRN-0204", f"QTY EXCEEDS PO BALANCE ({line['qty'] - done})")
    whs = whs_cd or h["whs_cd"]
    grn_no = _next_no(erp)
    erp.x("INSERT INTO grn_hdr VALUES (?,?,?,?,?,?)", grn_no, po_no, whs, user, erp.now(), remarks)
    erp.x("INSERT INTO grn_line VALUES (?,?,?,?)", grn_no, 1, line["itm_cd"], qty)
    erp.x("UPDATE stock SET on_hand=on_hand+?, on_order=MAX(on_order-?,0) WHERE itm_cd=? AND whs_cd=?",
          qty, qty, line["itm_cd"], whs)
    erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
          line["itm_cd"], whs, erp.today, "GRN", qty, grn_no)
    balance = line["qty"] - done - qty
    if balance == 0:
        erp.x("UPDATE po_hdr SET status='CL' WHERE po_no=?", po_no)
    return {"grn_no": grn_no, "po_no": po_no, "qty": qty, "balance": balance,
            "po_status": "CL" if balance == 0 else "RL", "_msg": f"{grn_no} SAVED"}


@service("grn_get", "GOODS RECEIPT GET", [F("grn_no", req=True, desc="GRN NO")])
def grn_get(erp, user, grn_no):
    h = erp.q1("SELECT * FROM grn_hdr WHERE grn_no=?", grn_no)
    if not h:
        raise LedgerlineError("ERR-GRN-0001", "GRN NOT FOUND")
    return {**h, "lines": erp.q("SELECT * FROM grn_line WHERE grn_no=?", grn_no)}


@service("grn_search", "GOODS RECEIPT LIST", [F("po_no", desc="PO NO")])
def grn_search(erp, user, po_no=None):
    sql, args = ("SELECT h.grn_no,h.po_no,h.whs_cd,h.received_by,h.received_on,l.itm_cd,l.qty FROM grn_hdr h "
                 "JOIN grn_line l ON l.grn_no=h.grn_no WHERE 1=1"), []
    if po_no:
        sql += " AND h.po_no=?"; args.append(po_no)
    return {"rows": erp.q(sql + " ORDER BY h.grn_no DESC", *args)}
