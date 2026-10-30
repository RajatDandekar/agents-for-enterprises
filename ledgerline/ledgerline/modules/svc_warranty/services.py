"""Service · warranty: the nine services, as terse as purchasing's. Ticket status: OP, CQ, WA, PI, CL, CN."""
from __future__ import annotations

import re

from ...erp.engine import LedgerlineError, service
from .._kit import F


def _norm(x: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (x or "").upper())


@service("wr_ser_get", "SERIAL ENQUIRY", [F("serial", desc="SERIAL NO"), F("q", desc="SERIAL LIKE")], screen="SVC-SER-01")
def wr_ser_get(erp, user, serial=None, q=None):
    if serial:
        s = erp.q1("SELECT * FROM wr_serial WHERE serial=?", serial.upper())
        if not s:
            raise LedgerlineError("ERR-WR-0101", "SERIAL NOT FOUND")
        return s
    if not q:
        raise LedgerlineError("ERR-SYS-0421", "SERIAL OR Q MANDATORY")
    rows = [r for r in erp.q("SELECT serial,model,sold_dt,dealer_cd,status FROM wr_serial") if _norm(q) in _norm(r["serial"])]
    return {"rows": rows[:20], "_msg": f"{len(rows)} ROWS FOUND"}


@service("wr_sale_reg", "SALE REGISTRATION", [F("serial", req=True, desc="SERIAL NO"), F("sold_dt", "date", True, "SOLD DT"),
                                              F("dealer_cd", req=True, desc="DEALER CD"), F("inv_ref", req=True, desc="DLR INV NO")],
         kind="write", screen="SVC-SER-01")
def wr_sale_reg(erp, user, serial, sold_dt, dealer_cd, inv_ref):
    s = erp.sp("sp_wr_serial_get", serial)
    erp.sp("sp_wr_sale_chk", s, sold_dt, dealer_cd)
    erp.x("UPDATE wr_serial SET sold_dt=?, dealer_cd=?, inv_ref=? WHERE serial=?", sold_dt, dealer_cd, inv_ref, s["serial"])
    return {"serial": s["serial"], "sold_dt": sold_dt, "_msg": f"{s['serial']} SALE REGISTERED"}


@service("wr_verify", "WARRANTY CHECK", [F("serial", req=True, desc="SERIAL NO"), F("part_cd", req=True, desc="PART CD")],
         screen="SVC-TKT-02")
def wr_verify(erp, user, serial, part_cd):
    s = erp.sp("sp_wr_serial_get", serial)
    term = erp.sp("sp_wr_part_term", s["model"], part_cd)
    inw, basis, to = erp.sp("sp_wr_wty_chk", s, term)
    tok = erp.sp("sp_fetch_tok_new", user, "SVC-TKT-02", f"{s['serial']}|{part_cd}")
    return {"model": s["model"], "in_wty": "Y" if inw else "N", "basis": basis, "wty_to": to, "grp": term["grp"],
            "price": term["price"], "fetch_tok": tok}


@service("wr_tkt_save", "SERVICE TICKET SAVE",
         [F("serial", req=True, desc="SERIAL NO"), F("part_cd", req=True, desc="PART CD"), F("cmp_cd", req=True, desc="COMPLAINT CD"),
          F("cause_cd", desc="CAUSE CD"), F("chg", desc="CHARGEABLE Y/N"), F("dealer_cd", desc="DEALER CD"),
          F("remarks", desc="REMARKS"), F("fetch_tok", desc="FETCH TOKEN"), F("client_ref", desc="CLIENT REF")],
         kind="write", screen="SVC-TKT-02")
def wr_tkt_save(erp, user, serial, part_cd, cmp_cd, cause_cd="UNK", chg=None, dealer_cd=None, remarks="",
                fetch_tok=None, client_ref=None):
    serial = serial.upper()
    erp.sp("sp_fetch_tok_chk", user, fetch_tok, "SVC-TKT-02", f"{serial}|{part_cd}")
    s = erp.sp("sp_wr_serial_get", serial)
    term = erp.sp("sp_wr_part_term", s["model"], part_cd)
    for cd, kind in ((cmp_cd, "CMP"), (cause_cd, "CAU")):
        if not erp.q1("SELECT 1 FROM wr_cause WHERE cd=? AND kind=?", cd, kind):
            raise LedgerlineError("ERR-WR-0220", f"INVALID {kind} CD {cd}")
    erp.sp("sp_wr_dup_chk", serial, part_cd)
    inw, basis, to = erp.sp("sp_wr_wty_chk", s, term)
    chg = (chg or ("N" if inw else "Y")).upper()[:1]
    if chg == "N" and not inw:
        raise LedgerlineError("ERR-WR-0240", "OUT OF WARRANTY, CHG MUST BE Y")
    # Note: Ledgerline does not look at the cause. Physical damage in warranty is free unless the desk types CHG = Y.
    amount = erp.sp("sp_wr_charge", term["price"]) if chg == "Y" else 0.0
    status = "CQ" if chg == "Y" else "OP"
    tkt = erp.sp("sp_doc_no_next", "WR")
    erp.x("INSERT INTO wr_ticket VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tkt, serial, part_cd, cmp_cd, cause_cd, chg,
          basis, to, amount, status, dealer_cd or s["dealer_cd"], user, erp.now(), None, None, None, remarks, client_ref)
    return {"tkt_no": tkt, "status": status, "chg": chg, "amount": amount, "_msg": f"{tkt} SAVED"}


@service("wr_tkt_list", "TICKET LIST", [F("tkt_no", desc="TKT NO"), F("serial", desc="SERIAL NO"), F("status", desc="STATUS"),
                                        F("approver", desc="APPROVER"), F("client_ref", desc="CLIENT REF")], screen="SVC-WAV-03")
def wr_tkt_list(erp, user, tkt_no=None, serial=None, status=None, approver=None, client_ref=None):
    sql, args = ("SELECT t.tkt_no,t.serial,t.part_cd,t.cmp_cd,t.cause_cd,t.chg,t.wty_basis,t.wty_to,t.amount,t.status,"
                 "t.dealer_cd,t.waived_by,t.raised_on FROM wr_ticket t WHERE 1=1"), []
    for col, v in (("t.tkt_no", tkt_no), ("t.serial", serial), ("t.status", status), ("t.client_ref", client_ref)):
        if v:
            sql += f" AND {col}=?"
            args.append(v.upper() if col == "t.serial" else v)
    if approver:
        sql += " AND t.tkt_no IN (SELECT doc_no FROM approval WHERE doc_type='WR' AND status='PENDING' AND approver=?)"
        args.append(approver.upper())
    return {"rows": erp.q(sql + " ORDER BY t.tkt_no DESC", *args)}


@service("wr_waive", "GOODWILL WAIVER REQ", [F("tkt_no", req=True, desc="TKT NO"), F("reason", req=True, desc="REASON"),
                                             F("fwd_to", desc="FWD TO")], kind="write", screen="SVC-WAV-03")
def wr_waive(erp, user, tkt_no, reason, fwd_to=None):
    t = erp.q1("SELECT * FROM wr_ticket WHERE tkt_no=?", tkt_no)
    if not t:
        raise LedgerlineError("ERR-WR-0501", "TICKET NOT FOUND")
    if t["status"] != "CQ":
        raise LedgerlineError("ERR-WR-0405", f"TICKET NOT CHARGEABLE ({t['status']})")
    approver = erp.sp("sp_wr_waive_route", t, user, fwd_to.upper() if fwd_to else None)
    if approver is None:  # within the desk's limit: granted at once
        erp.x("UPDATE wr_ticket SET chg='W', waived_by=?, remarks=? WHERE tkt_no=?", user, reason, tkt_no)
        erp.sp("sp_wr_status_set", tkt_no, "OP")
        return {"tkt_no": tkt_no, "status": "OP", "_msg": f"{tkt_no} WAIVED"}
    erp.x("UPDATE wr_ticket SET remarks=? WHERE tkt_no=?", reason, tkt_no)
    erp.sp("sp_wr_status_set", tkt_no, "WA")
    return {"tkt_no": tkt_no, "status": "WA", "approver": approver, "_msg": f"{tkt_no} SENT FOR WAIVER"}


@service("wr_waive_apr", "WAIVER APPROVE", [F("tkt_no", req=True, desc="TKT NO"), F("decision", req=True, desc="A/R"),
                                            F("comment", desc="COMMENT")], kind="write", screen="SVC-WAV-03")
def wr_waive_apr(erp, user, tkt_no, decision, comment=""):
    t = erp.q1("SELECT * FROM wr_ticket WHERE tkt_no=?", tkt_no)
    if not t:
        raise LedgerlineError("ERR-WR-0501", "TICKET NOT FOUND")
    if t["status"] != "WA":
        raise LedgerlineError("ERR-WR-0502", f"NO WAIVER PENDING ({t['status']})")
    if t["raised_by"] == user:
        raise LedgerlineError("ERR-APR-0003", "SELF APPROVAL NOT ALLOWED")
    a = erp.q1("SELECT * FROM approval WHERE doc_type='WR' AND doc_no=? AND status='PENDING'", tkt_no)
    if a and a["approver"] != user and erp.user(user)["role_cd"] != "SYS-ADMIN":
        raise LedgerlineError("ERR-WR-0504", f"NOT YOUR APPROVAL ({a['approver']})")
    if erp.user(user)["appr_limit"] < t["amount"]:
        raise LedgerlineError("ERR-APR-0004", "VALUE ABOVE YOUR LIMIT")
    ok = decision.upper().startswith("A")
    if ok:
        erp.x("UPDATE wr_ticket SET chg='W', waived_by=? WHERE tkt_no=?", user, tkt_no)
    erp.sp("sp_wr_status_set", tkt_no, "OP" if ok else "CQ")
    erp.x("UPDATE approval SET status=?, decided_on=?, comment=? WHERE doc_no=? AND status='PENDING'",
          "APPROVED" if ok else "REJECTED", erp.now(), comment, tkt_no)
    return {"tkt_no": tkt_no, "status": "OP" if ok else "CQ", "_msg": f"{tkt_no} WAIVER {'APPROVED' if ok else 'REJECTED'}"}


@service("wr_issue", "PART ISSUE", [F("tkt_no", req=True, desc="TKT NO"), F("rcpt_no", desc="CUST RCPT NO")],
         kind="write", screen="SVC-TKT-02")
def wr_issue(erp, user, tkt_no, rcpt_no=None):
    t = erp.q1("SELECT * FROM wr_ticket WHERE tkt_no=?", tkt_no)
    if not t:
        raise LedgerlineError("ERR-WR-0501", "TICKET NOT FOUND")
    if t["status"] == "CQ" and not rcpt_no:
        raise LedgerlineError("ERR-WR-0420", "PAYMENT PENDING, RCPT NO MANDATORY")
    if t["status"] == "WA":
        raise LedgerlineError("ERR-WR-0421", "WAIVER PENDING")
    if t["status"] not in ("OP", "CQ"):
        raise LedgerlineError("ERR-WR-0422", f"PART CANNOT BE ISSUED ({t['status']})")
    erp.sp("sp_wr_stk_issue", t["part_cd"], 1, tkt_no)
    erp.x("INSERT INTO wr_issue VALUES (?,?,?,?,?,?)", tkt_no, t["part_cd"], 1, "WH-MAN-STR", erp.now(), rcpt_no)
    if rcpt_no:
        erp.x("UPDATE wr_ticket SET rcpt_no=? WHERE tkt_no=?", rcpt_no, tkt_no)
    erp.sp("sp_wr_status_set", tkt_no, "PI")
    return {"tkt_no": tkt_no, "status": "PI", "_msg": f"{tkt_no} PART ISSUED"}


@service("wr_close", "TICKET CLOSE", [F("tkt_no", req=True, desc="TKT NO"), F("remarks", desc="REMARKS"),
                                      F("cncl", desc="CANCEL Y/N")], kind="write", screen="SVC-TKT-02")
def wr_close(erp, user, tkt_no, remarks="", cncl="N"):
    t = erp.q1("SELECT * FROM wr_ticket WHERE tkt_no=?", tkt_no)
    if not t:
        raise LedgerlineError("ERR-WR-0501", "TICKET NOT FOUND")
    if (cncl or "N").upper().startswith("Y"):
        if t["status"] not in ("OP", "CQ", "WA"):
            raise LedgerlineError("ERR-WR-0511", f"CANNOT CANCEL ({t['status']})")
        erp.sp("sp_wr_status_set", tkt_no, "CN")
        erp.x("UPDATE approval SET status='WITHDRAWN' WHERE doc_no=? AND status='PENDING'", tkt_no)
        return {"tkt_no": tkt_no, "status": "CN", "_msg": f"{tkt_no} CANCELLED"}
    if t["status"] != "PI":
        raise LedgerlineError("ERR-WR-0510", f"PART NOT ISSUED ({t['status']})")
    price = erp.q1("SELECT price FROM wr_part WHERE part_cd=?", t["part_cd"])["price"]
    erp.sp("sp_wr_cost_book", t, price)
    erp.sp("sp_wr_dealer_ntf", t)
    erp.sp("sp_wr_status_set", tkt_no, "CL")
    return {"tkt_no": tkt_no, "status": "CL", "_msg": f"{tkt_no} CLOSED"}
