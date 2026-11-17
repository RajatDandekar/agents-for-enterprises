"""Accounts payable: supplier invoices and the three-way match (Lecture 5, The Habits). Installed on demand.

    PO (what we ordered, at what price) ─┐
    GRN (what arrived, how many)        ─┼─> three-way match ─> post (to be paid) or hold (a person looks)
    Invoice (what the supplier bills)   ─┘

    from ledgerline.erp.engine import ERP
    from ledgerline.erp.payables import install_payables
    erp = ERP(); install_payables(erp)            # tables, numbering, permissions and the week's seed data
    erp.call("inv_save", {...}, user="LMORENO"); erp.call("inv_match", {"inv_no": "AP/2026/70001"}, user="LMORENO")

Like goods receipts (receipts.py), nothing here exists in a plain ERP(): the services register when this module is
imported, and the permissions, tables and data appear only in a sandbox that called install_payables(). So the older
lectures' service lists, tool sets and recorded runs do not change.

The match. An invoice line matches when
  - it names an order that exists, is released (or closed), is with the same supplier and for the same item;
  - goods have been received against that order (a goods receipt exists);
  - the quantity billed is not more than the quantity received minus what earlier matched invoices already billed;
  - the unit price is not more than the order's rate plus the price tolerance (2% unless the caller asks for less;
    the policy cap is 5%). A lower price is accepted.
Anything else is a variance, and the invoice stays RECEIVED with the reason, for a person to hold or chase.

Status codes: RC received · MT matched · HD held · PS posted (to be paid).
Other services added here for the background agents: open (late) orders, expiring certificates, items below reorder
level, the shared mailbox, and message drafts (a draft is never sent by a machine).
"""
from __future__ import annotations

import datetime as dt

from .engine import LedgerlineError, service

F = lambda name, t="str", req=False, desc="": (name, t, req, desc)  # noqa: E731  (same as services.py)

SCHEMA = """
CREATE TABLE IF NOT EXISTS inv_hdr(inv_no TEXT PRIMARY KEY, sup_inv_no TEXT, sup_cd TEXT, po_no TEXT, inv_dt TEXT,
    net REAL, vat REAL, gross REAL, status TEXT, match_result TEXT, match_note TEXT, hold_reason TEXT, src_ref TEXT,
    recorded_by TEXT, recorded_on TEXT, posted_by TEXT, posted_on TEXT, due_dt TEXT);
CREATE TABLE IF NOT EXISTS inv_line(inv_no TEXT, line_no INT, itm_cd TEXT, qty INT, rate REAL);
CREATE TABLE IF NOT EXISTS mail_msg(msg_id TEXT PRIMARY KEY, folder TEXT, recv_on TEXT, sender TEXT, subject TEXT,
    body TEXT, attachment TEXT, kind TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS ntf_draft(id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, recipient TEXT, subject TEXT,
    body TEXT, ref TEXT, status TEXT, created_by TEXT, created_on TEXT);
CREATE TABLE IF NOT EXISTS ap_tolerance(name TEXT PRIMARY KEY, value REAL);
"""
STATUS = {"RC": "RECEIVED", "MT": "MATCHED", "HD": "HELD", "PS": "POSTED"}
PRICE_TOLERANCE_PCT, POLICY_CAP_PCT = 2.0, 5.0

READS = ["inv_get", "inv_search", "po_open_list", "cert_expiry_list", "stk_below_reorder", "mail_list", "mail_get",
         "ntf_draft_list"]
PERMS = {
    "PUR-EXEC": READS + ["inv_save", "inv_match", "inv_hold", "mail_mark", "ntf_draft_save"],
    "PUR-SR": READS + ["inv_save", "inv_match", "inv_hold", "inv_post", "mail_mark", "ntf_draft_save"],
    "PUR-MGR": READS + ["inv_match", "inv_hold", "inv_post", "mail_mark", "ntf_draft_save"],
    "PLANT-HEAD": READS,
    "STORES": ["po_open_list", "stk_below_reorder", "mail_list", "mail_get", "ntf_draft_list", "ntf_draft_save"],
}


def install_payables(erp, seed: bool = True) -> None:
    """Add accounts payable to a running sandbox (tables, numbering, permissions) and, by default, the week's data:
    about 40 invoices in the AP inbox, the orders and goods receipts they bill, late orders, certificates that expire
    soon and items below their reorder level (payables_seed.py). Safe to call twice."""
    from .receipts import install_receipts

    install_receipts(erp)
    if erp.q1("SELECT 1 FROM doc_seq WHERE doc_type='INV'"):
        return
    erp.db.executescript(SCHEMA)
    erp.x("INSERT INTO doc_seq VALUES ('INV','AP/2026/',70001,5)")
    erp.x("INSERT INTO ap_tolerance VALUES ('price_pct', ?)", PRICE_TOLERANCE_PCT)
    for role, svcs in PERMS.items():
        for s in svcs:
            erp.x("INSERT INTO role_perm VALUES (?,?)", role, s)
    erp.db.commit()
    if seed:
        from .payables_seed import seed_week
        seed_week(erp)
        erp.db.commit()


def _next_no(erp) -> str:
    seq = erp.q1("SELECT * FROM doc_seq WHERE doc_type='INV'")
    erp.x("UPDATE doc_seq SET next_no=next_no+1 WHERE doc_type='INV'")
    return f"{seq['prefix']}{str(seq['next_no']).zfill(seq['width'])}"


def _inv(erp, inv_no: str) -> dict:
    h = erp.q1("SELECT * FROM inv_hdr WHERE inv_no=?", inv_no)
    if not h:
        raise LedgerlineError("ERR-INV-0001", "INVOICE NOT FOUND")
    return {**h, "lines": erp.q("SELECT * FROM inv_line WHERE inv_no=?", inv_no)}


def _received(erp, po_no: str) -> int:
    r = erp.q1("SELECT COALESCE(SUM(l.qty),0) AS q FROM grn_line l JOIN grn_hdr h ON h.grn_no=l.grn_no WHERE h.po_no=?", po_no)
    return int(r["q"])


# ----------------------------------------------------------------------------- invoices
@service("inv_save", "SUPPLIER INVOICE ENTRY",
         [F("sup_cd", req=True, desc="SUP CD"), F("sup_inv_no", req=True, desc="SUP INV NO"), F("po_no", desc="PO NO"),
          F("inv_dt", "date", True, "INV DT"), F("itm_cd", req=True, desc="ITEM CD"), F("qty", "int", True, "QTY"),
          F("rate", "float", True, "RATE"), F("vat", "float", desc="VAT AMT"), F("src_ref", desc="SOURCE MSG")],
         kind="write", screen="ACC-INV-01")
def inv_save(erp, user, sup_cd, sup_inv_no, inv_dt, itm_cd, qty, rate, po_no=None, vat=None, src_ref=None):
    sup = erp.q1("SELECT * FROM supplier WHERE sup_cd=?", sup_cd)
    if not sup:
        raise LedgerlineError("ERR-SUP-0030", "SUPPLIER NOT FOUND")
    dup = erp.q1("SELECT inv_no, status FROM inv_hdr WHERE sup_cd=? AND upper(sup_inv_no)=upper(?)", sup_cd, sup_inv_no)
    if dup:
        raise LedgerlineError("ERR-INV-0109", f"DUPLICATE SUPPLIER INVOICE ({dup['inv_no']} {STATUS[dup['status']]})")
    if not erp.q1("SELECT 1 FROM item WHERE itm_cd=?", itm_cd):
        raise LedgerlineError("ERR-ITM-0010", "ITEM NOT FOUND")
    qty = int(qty)
    if qty <= 0 or rate <= 0:
        raise LedgerlineError("ERR-INV-0201", "QTY AND RATE MUST BE > 0")
    net = round(qty * rate, 2)
    if vat is None:
        vat = round(net * 0.20, 2) if sup["state"] == "GB" else 0.0  # overseas: reverse charge, no VAT on the invoice
    inv_no = _next_no(erp)
    erp.x("INSERT INTO inv_hdr VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", inv_no, sup_inv_no, sup_cd, po_no or None,
          inv_dt, net, round(vat, 2), round(net + vat, 2), "RC", None, None, None, src_ref, user, erp.now(), None, None, None)
    erp.x("INSERT INTO inv_line VALUES (?,?,?,?,?)", inv_no, 1, itm_cd, qty, rate)
    return {"inv_no": inv_no, "status": "RC", "net": net, "vat": round(vat, 2), "gross": round(net + vat, 2),
            "_msg": f"{inv_no} SAVED"}


@service("inv_get", "SUPPLIER INVOICE GET", [F("inv_no", req=True, desc="INV NO")])
def inv_get(erp, user, inv_no):
    return _inv(erp, inv_no)


@service("inv_search", "SUPPLIER INVOICE LIST", [F("status", desc="RC/MT/HD/PS"), F("sup_cd", desc="SUP CD"),
                                                 F("po_no", desc="PO NO"), F("sup_inv_no", desc="SUP INV NO")])
def inv_search(erp, user, status=None, sup_cd=None, po_no=None, sup_inv_no=None):
    sql = ("SELECT h.inv_no,h.sup_inv_no,h.sup_cd,s.name sup_name,h.po_no,h.inv_dt,h.net,h.vat,h.gross,h.status,"
           "h.match_result,h.match_note,h.hold_reason,h.src_ref,h.due_dt,l.itm_cd,l.qty,l.rate FROM inv_hdr h "
           "JOIN inv_line l ON l.inv_no=h.inv_no JOIN supplier s ON s.sup_cd=h.sup_cd WHERE 1=1")
    args = []
    for col, v in (("h.status", status), ("h.sup_cd", sup_cd), ("h.po_no", po_no), ("upper(h.sup_inv_no)", (sup_inv_no or "").upper() or None)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    rows = erp.q(sql + " ORDER BY h.inv_no", *args)
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


@service("inv_match", "THREE-WAY MATCH", [F("inv_no", req=True, desc="INV NO"), F("tol_pct", "float", desc="PRICE TOL %")],
         kind="write", screen="ACC-INV-03")
def inv_match(erp, user, inv_no, tol_pct=None):
    h = _inv(erp, inv_no)
    if h["status"] in ("PS",):
        raise LedgerlineError("ERR-INV-0305", "INVOICE ALREADY POSTED")
    tol = float(erp.q1("SELECT value FROM ap_tolerance WHERE name='price_pct'")["value"]) if tol_pct is None else float(tol_pct)
    if tol < 0 or tol > POLICY_CAP_PCT:
        raise LedgerlineError("ERR-INV-0310", f"TOLERANCE OUTSIDE POLICY (0-{POLICY_CAP_PCT:g}%)")
    line = h["lines"][0]
    res = _three_way(erp, h, line, tol)
    status = "MT" if res["result"] == "matched" else ("HD" if h["status"] == "HD" else "RC")
    erp.x("UPDATE inv_hdr SET status=?, match_result=?, match_note=? WHERE inv_no=?", status, res["result"], res["note"], inv_no)
    return {"inv_no": inv_no, "status": status, **res, "_msg": f"{inv_no} {res['result'].upper().replace('_', ' ')}"}


def _three_way(erp, h, line, tol) -> dict:
    out = {"tolerance_pct": tol, "po_no": h["po_no"], "invoiced_qty": line["qty"], "invoice_rate": line["rate"]}
    po = erp.q1("SELECT * FROM po_hdr WHERE po_no=?", h["po_no"] or "")
    if not po:
        return {**out, "result": "no_order", "note": f"no purchase order {h['po_no'] or '(none given)'} in Ledgerline"}
    pl = erp.q1("SELECT * FROM po_line WHERE po_no=?", po["po_no"])
    out.update(ordered_qty=pl["qty"], order_rate=pl["rate"])
    if po["sup_cd"] != h["sup_cd"]:
        return {**out, "result": "supplier_mismatch", "note": f"{po['po_no']} is with {po['sup_cd']}, not {h['sup_cd']}"}
    if po["status"] not in ("RL", "CL"):
        return {**out, "result": "order_not_released", "note": f"{po['po_no']} is {po['status']}, not released"}
    if pl["itm_cd"] != line["itm_cd"]:
        return {**out, "result": "item_mismatch", "note": f"{po['po_no']} is for {pl['itm_cd']}, the invoice bills {line['itm_cd']}"}
    rec = _received(erp, po["po_no"])
    before = erp.q1("SELECT COALESCE(SUM(l.qty),0) q FROM inv_line l JOIN inv_hdr h ON h.inv_no=l.inv_no "
                    "WHERE h.po_no=? AND h.status IN ('MT','PS') AND h.inv_no<>?", po["po_no"], h["inv_no"])["q"]
    out.update(received_qty=rec, invoiced_before=int(before))
    if rec == 0:
        return {**out, "result": "no_receipt", "note": f"nothing received yet against {po['po_no']}"}
    if line["qty"] > rec - before:
        return {**out, "result": "quantity_variance",
                "note": f"billed {line['qty']:,}, received {rec:,}" + (f", {int(before):,} billed already" if before else "")}
    var = round((line["rate"] - pl["rate"]) / pl["rate"] * 100, 2)
    out["price_variance_pct"] = var
    if var > tol:
        return {**out, "result": "price_variance",
                "note": f"£{line['rate']:,.2f} billed against £{pl['rate']:,.2f} ordered (+{var:g}%, tolerance {tol:g}%)"}
    note = "price, quantity and goods receipt agree"
    if var > 0:
        note = f"price +{var:g}% is within the {tol:g}% tolerance"
    return {**out, "result": "matched", "note": note}


@service("inv_hold", "INVOICE HOLD", [F("inv_no", req=True, desc="INV NO"), F("reason", req=True, desc="REASON")],
         kind="write", screen="ACC-INV-03")
def inv_hold(erp, user, inv_no, reason):
    h = _inv(erp, inv_no)
    if h["status"] == "PS":
        raise LedgerlineError("ERR-INV-0305", "INVOICE ALREADY POSTED")
    erp.x("UPDATE inv_hdr SET status='HD', hold_reason=? WHERE inv_no=?", reason[:300], inv_no)
    return {"inv_no": inv_no, "status": "HD", "_msg": f"{inv_no} HELD"}


@service("inv_post", "INVOICE POST", [F("inv_no", req=True, desc="INV NO")], kind="write", screen="ACC-INV-04")
def inv_post(erp, user, inv_no):
    h = _inv(erp, inv_no)
    if h["status"] == "PS":
        raise LedgerlineError("ERR-INV-0305", "INVOICE ALREADY POSTED")
    if h["status"] != "MT":
        raise LedgerlineError("ERR-INV-0302", f"INVOICE NOT MATCHED ({STATUS[h['status']]})")
    sup = erp.q1("SELECT pt_cd FROM supplier WHERE sup_cd=?", h["sup_cd"])
    days = (erp.q1("SELECT days FROM pay_term WHERE pt_cd=?", sup["pt_cd"]) or {"days": 30})["days"]
    due = (dt.date.fromisoformat(h["inv_dt"]) + dt.timedelta(days=days)).isoformat()
    erp.x("UPDATE inv_hdr SET status='PS', posted_by=?, posted_on=?, due_dt=? WHERE inv_no=?", user, erp.now(), due, inv_no)
    return {"inv_no": inv_no, "status": "PS", "due_dt": due, "gross": h["gross"], "_msg": f"{inv_no} POSTED"}


# ----------------------------------------------------------------------------- what the background agents look at
@service("po_open_list", "OPEN ORDERS (NOT FULLY RECEIVED)",
         [F("days_late", "int", desc="MIN DAYS LATE"), F("sup_cd", desc="SUP CD"), F("created_by", desc="BUYER")])
def po_open_list(erp, user, days_late=None, sup_cd=None, created_by=None):
    sql = ("SELECT h.po_no,h.sup_cd,s.name sup_name,h.need_dt,h.created_by,h.created_on,h.released_on,h.cc_cd,l.itm_cd,"
           "i.descr,l.qty,l.rate FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no JOIN supplier s ON s.sup_cd=h.sup_cd "
           "JOIN item i ON i.itm_cd=l.itm_cd WHERE h.status='RL'")
    args = []
    for col, v in (("h.sup_cd", sup_cd), ("h.created_by", created_by)):
        if v:
            sql += f" AND {col}=?"
            args.append(v)
    today = dt.date.fromisoformat(erp.today)
    rows = []
    for r in erp.q(sql + " ORDER BY h.need_dt", *args):
        rec = _received(erp, r["po_no"])
        if rec >= r["qty"]:
            continue
        late = (today - dt.date.fromisoformat(r["need_dt"])).days
        if days_late is not None and late < int(days_late):
            continue
        rows.append({**r, "received": rec, "outstanding": r["qty"] - rec, "days_late": max(late, 0),
                     "late": late > 0, "sup_email": f"orders@{r['sup_cd'].lower()}.example"})
    return {"rows": rows, "as_of": erp.today, "_msg": f"{len(rows)} ROWS FOUND"}


@service("cert_expiry_list", "CERTIFICATES EXPIRING", [F("within_days", "int", desc="DAYS"), F("cert_type", desc="CERT TYPE")])
def cert_expiry_list(erp, user, within_days=60, cert_type="UN38.3"):
    today = dt.date.fromisoformat(erp.today)
    rows = []
    for c in erp.q("SELECT c.*, s.name sup_name, s.status sup_status FROM sup_cert c JOIN supplier s ON s.sup_cd=c.sup_cd "
                   "WHERE upper(replace(c.cert_type,' ',''))=upper(replace(?,' ','')) ORDER BY c.valid_to", cert_type or "UN38.3"):
        # a supplier with a newer certificate of the same type is covered by it
        newer = erp.q1("SELECT 1 FROM sup_cert WHERE sup_cd=? AND cert_type=? AND valid_to>?", c["sup_cd"], c["cert_type"], c["valid_to"])
        if newer:
            continue
        days = (dt.date.fromisoformat(c["valid_to"]) - today).days
        if days > int(within_days):
            continue
        open_pos = erp.q("SELECT h.po_no FROM po_hdr h WHERE h.sup_cd=? AND h.status IN ('DR','PA','AP','RL')", c["sup_cd"])
        rows.append({"sup_cd": c["sup_cd"], "sup_name": c["sup_name"], "sup_email": f"compliance@{c['sup_cd'].lower()}.example",
                     "cert_type": c["cert_type"], "doc_ref": c["doc_ref"],
                     "valid_to": c["valid_to"], "days_left": days, "state": "EXPIRED" if days < 0 else "EXPIRING",
                     "open_orders": [p["po_no"] for p in open_pos]})
    return {"rows": rows, "as_of": erp.today, "_msg": f"{len(rows)} ROWS FOUND"}


@service("stk_below_reorder", "ITEMS BELOW REORDER LEVEL (ALL WAREHOUSES)")
def stk_below_reorder(erp, user):
    rows = []
    for i in erp.q("SELECT * FROM item WHERE active=1 AND reorder_lvl>0 ORDER BY itm_cd"):
        s = erp.q1("SELECT COALESCE(SUM(on_hand-allocated),0) free, COALESCE(SUM(on_order),0) oo FROM stock WHERE itm_cd=?",
                   i["itm_cd"])
        if s["free"] + s["oo"] < i["reorder_lvl"]:
            last = erp.q1("SELECT h.sup_cd FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE l.itm_cd=? AND "
                          "h.status IN ('RL','CL') ORDER BY h.created_on DESC", i["itm_cd"])
            rows.append({"itm_cd": i["itm_cd"], "descr": i["descr"], "free": s["free"], "on_order": s["oo"],
                         "reorder_lvl": i["reorder_lvl"], "avg_daily_issue": i["avg_daily_issue"],
                         "cover_days": int(s["free"] / i["avg_daily_issue"]) if i["avg_daily_issue"] else None,
                         "last_sup_cd": last["sup_cd"] if last else None})
    return {"rows": rows, "_msg": f"{len(rows)} ROWS FOUND"}


# ----------------------------------------------------------------------------- the shared mailbox and message drafts
@service("mail_list", "MAILBOX LIST", [F("folder", desc="FOLDER"), F("status", desc="NEW/READ/DONE")])
def mail_list(erp, user, folder="AP inbox", status=None):
    sql, args = "SELECT * FROM mail_msg WHERE folder=?", [folder or "AP inbox"]
    if status:
        sql += " AND status=?"
        args.append(status.upper())
    return {"rows": erp.q(sql + " ORDER BY recv_on, msg_id", *args)}


@service("mail_get", "MAILBOX GET", [F("msg_id", req=True, desc="MSG ID")])
def mail_get(erp, user, msg_id):
    r = erp.q1("SELECT * FROM mail_msg WHERE msg_id=?", msg_id)
    if not r:
        raise LedgerlineError("ERR-MAIL-0001", "MESSAGE NOT FOUND")
    return r


@service("mail_mark", "MAILBOX MARK", [F("msg_id", req=True, desc="MSG ID"), F("status", req=True, desc="NEW/READ/DONE")],
         kind="write")
def mail_mark(erp, user, msg_id, status):
    if not erp.q1("SELECT 1 FROM mail_msg WHERE msg_id=?", msg_id):
        raise LedgerlineError("ERR-MAIL-0001", "MESSAGE NOT FOUND")
    erp.x("UPDATE mail_msg SET status=? WHERE msg_id=?", status.upper(), msg_id)
    return {"msg_id": msg_id, "status": status.upper(), "_msg": "MARKED"}


@service("ntf_draft_save", "MESSAGE DRAFT SAVE",
         [F("channel", req=True, desc="EMAIL/SLACK"), F("recipient", req=True, desc="TO"), F("subject", req=True, desc="SUBJECT"),
          F("body", req=True, desc="TEXT"), F("ref", desc="DOC REF")], kind="write")
def ntf_draft_save(erp, user, channel, recipient, subject, body, ref=None):
    same = erp.q1("SELECT id FROM ntf_draft WHERE recipient=? AND subject=? AND status='PENDING'", recipient, subject)
    if same:
        return {"draft_id": same["id"], "already_done": True, "_msg": f"DRAFT {same['id']} ALREADY PENDING"}
    cur = erp.x("INSERT INTO ntf_draft(channel,recipient,subject,body,ref,status,created_by,created_on) VALUES "
                "(?,?,?,?,?,?,?,?)", channel.upper(), recipient, subject, body, ref, "PENDING", user, erp.now())
    return {"draft_id": cur.lastrowid, "already_done": False, "_msg": f"DRAFT {cur.lastrowid} SAVED"}


@service("ntf_draft_list", "MESSAGE DRAFT LIST", [F("status", desc="PENDING/SENT/DISCARDED")])
def ntf_draft_list(erp, user, status="PENDING"):
    return {"rows": erp.q("SELECT * FROM ntf_draft WHERE status=? ORDER BY id", (status or "PENDING").upper())}
