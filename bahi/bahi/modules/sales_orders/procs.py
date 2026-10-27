"""Sales · orders: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import BahiError, proc


def _plus(d: str, days: int) -> str:
    return (dt.date.fromisoformat(d) + dt.timedelta(days=days)).isoformat()


CASH_LIMIT = 100000  # a direct cash order without a quotation: gross up to ₹1,00,000


@proc("sp_so_cust_chk")
def cust_chk(erp, cust_cd: str) -> dict:
    c = erp.q1("SELECT * FROM so_cust WHERE cust_cd=?", cust_cd)
    if not c:
        raise BahiError("ERR-SO-0030", "CUSTOMER NOT FOUND")
    if c["status"] != "ACTIVE":
        raise BahiError("ERR-SO-0031", "CUSTOMER NOT ACTIVE")
    return c


@proc("sp_so_price_cur")
def price_cur(erp, list_cd: str, itm_cd: str) -> float:
    """The price valid today on a price list."""
    r = erp.q1("SELECT rate FROM so_price WHERE list_cd=? AND itm_cd=? AND valid_from<=? AND valid_to>=? "
               "ORDER BY valid_from DESC", list_cd, itm_cd, erp.today, erp.today)
    if not r:
        raise BahiError("ERR-SO-0421", f"NO CURRENT {list_cd} PRICE FOR {itm_cd}")
    return r["rate"]


@proc("sp_so_price_chk")
def price_chk(erp, list_cd: str, itm_cd: str, rate: float):
    """The rate typed must be on the price list. Bahi 7.2 checks that the rate EXISTS on the list, not that it is
    still valid: an expired price passes. (Price Policy §3.2 is the only guard.)"""
    if not erp.q1("SELECT 1 FROM so_price WHERE list_cd=? AND itm_cd=? AND abs(rate-?)<0.005", list_cd, itm_cd, rate):
        raise BahiError("ERR-SO-0420", "RATE NOT AS PER PRICE LIST")


@proc("sp_so_tax_region_chk")
def tax_region_chk(erp, cust: dict, tax_cd: str, ou_cd: str):
    """A customer in the plant's state pays CGST+SGST (-INTRA); any other state pays IGST (-INTER)."""
    tax = erp.q1("SELECT * FROM tax_code WHERE tax_cd=?", tax_cd)
    if not tax:
        raise BahiError("ERR-TAX-0101", "INVALID TAX CODE")
    ou = erp.q1("SELECT state FROM org_unit WHERE ou_cd=?", ou_cd)
    want = "INTRA" if cust["state"] == ou["state"] else "INTER"
    if tax["kind"] != want:
        raise BahiError("ERR-SO-0412", f"TAX REGION DOES NOT MATCH CUSTOMER STATE ({cust['state']})")


@proc("sp_so_disc_lim")
def disc_lim(erp, user: str) -> float:
    r = erp.q1("SELECT max_disc FROM so_disc_lim WHERE role_cd=?", erp.user(user)["role_cd"])
    return r["max_disc"] if r else 0.0


@proc("sp_so_value")
def value(erp, qty: int, rate: float, disc: float, tax_cd: str) -> tuple[float, float, float]:
    """Basic after discount, then the shared tax engine for tax and gross."""
    basic = round(qty * rate * (1 - disc / 100), 2)
    tax, gross = erp.sp("sp_tax_compute", basic, tax_cd)
    return basic, tax, gross


@proc("sp_so_credit_chk")
def credit_chk(erp, cust: dict, gross: float) -> str:
    """Exposure = outstanding + open and released orders. Over the limit returns 'HOLD'; it does not refuse."""
    open_ = erp.q1("SELECT coalesce(sum(gross_value),0) v FROM so_ord WHERE cust_cd=? AND status IN ('OP','RL')",
                   cust["cust_cd"])["v"]
    return "HOLD" if cust["outstanding"] + open_ + gross > cust["cr_limit"] else "OK"


@proc("sp_so_qtn_save")
def qtn_save(erp, user: str, a: dict) -> dict:
    cust = erp.sp("sp_so_cust_chk", a["cust_cd"])
    itm = erp.q1("SELECT * FROM item WHERE itm_cd=? AND category='FG'", a["itm_cd"])
    if not itm or not itm["active"]:
        raise BahiError("ERR-ITM-0011", "ITEM NOT FOUND OR INACTIVE")
    if a["qty"] <= 0:
        raise BahiError("ERR-SO-0201", "QTY MUST BE > 0")
    list_cd = a.get("list_cd") or cust["list_cd"]
    if list_cd != cust["list_cd"]:
        raise BahiError("ERR-SO-0425", f"PRICE LIST {list_cd} NOT ALLOWED FOR CUSTOMER ({cust['list_cd']})")
    rate = a.get("rate") or erp.sp("sp_so_price_cur", list_cd, a["itm_cd"])
    erp.sp("sp_so_price_chk", list_cd, a["itm_cd"], rate)
    erp.sp("sp_so_tax_region_chk", cust, a["tax_cd"], erp.user(user)["ou_cd"])
    disc = a.get("disc_pct") or 0.0
    if disc < 0 or disc > 15:
        raise BahiError("ERR-SO-0430", "DISC % OUT OF RANGE")
    basic, tax, gross = erp.sp("sp_so_value", a["qty"], rate, disc, a["tax_cd"])
    qtn_no = erp.sp("sp_doc_no_next", "SOQ")
    within = disc <= erp.sp("sp_so_disc_lim", user)
    status = "IS" if within else "PA"
    erp.x("INSERT INTO so_qtn VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", qtn_no, a["cust_cd"], a["itm_cd"], a["qty"],
          list_cd, rate, disc, a["tax_cd"], basic, tax, gross, a.get("valid_to") or _plus(erp.today, 15), status, user,
          erp.now(), user if within else None, erp.now() if within else None, a.get("client_ref"), a.get("remarks"))
    approver = None
    if not within:  # discount above the raiser's authority: the shared approval engine finds the manager
        approver = erp.sp("sp_appr_route", "SOQ", qtn_no, user, gross)
    return {"qtn_no": qtn_no, "status": status, "rate": rate, "gross_value": gross, "approver": approver}


@proc("sp_so_ord_save")
def ord_save(erp, user: str, a: dict) -> dict:
    """The two variants. STD: from an issued quotation (rate, discount and tax come from it).
    CSH: a direct ex-stock cash sale at today's list price, no quotation, gross up to ₹1,00,000, no credit check."""
    typ = a.get("ord_type") or "STD"
    if typ == "STD":
        q = erp.q1("SELECT * FROM so_qtn WHERE qtn_no=?", a.get("qtn_no") or "")
        if not q:
            raise BahiError("ERR-SO-0602", "QUOTATION MANDATORY FOR STD ORDER")
        if q["status"] != "IS":
            raise BahiError("ERR-SO-0603", f"QUOTATION NOT ISSUED ({q['status']})")
        if q["valid_to"] < erp.today:
            raise BahiError("ERR-SO-0605", "QUOTATION EXPIRED")
        qty = a.get("qty") or q["qty"]
        if qty > q["qty"]:
            raise BahiError("ERR-SO-0604", "QTY MORE THAN QUOTED")
        cust = erp.sp("sp_so_cust_chk", q["cust_cd"])
        itm_cd, rate, disc, tax_cd = q["itm_cd"], q["rate"], q["disc_pct"], q["tax_cd"]
    elif typ == "CSH":
        if a.get("qtn_no"):
            raise BahiError("ERR-SO-0611", "CSH ORDER CANNOT REFER QUOTATION")
        for k in ("cust_cd", "itm_cd", "qty", "tax_cd"):
            if not a.get(k):
                raise BahiError("ERR-SYS-0421", f"{k.upper()} MANDATORY")
        cust = erp.sp("sp_so_cust_chk", a["cust_cd"])
        itm_cd, qty, disc, tax_cd = a["itm_cd"], a["qty"], 0.0, a["tax_cd"]
        rate = erp.sp("sp_so_price_cur", cust["list_cd"], itm_cd)
        erp.sp("sp_so_tax_region_chk", cust, tax_cd, erp.user(user)["ou_cd"])
    else:
        raise BahiError("ERR-SO-0600", "ORD TYPE MUST BE STD/CSH")
    _, _, gross = erp.sp("sp_so_value", qty, rate, disc, tax_cd)
    if typ == "CSH" and gross > CASH_LIMIT:
        raise BahiError("ERR-SO-0610", "CASH ORDER LIMIT 100000 EXCEEDED, RAISE QUOTATION")
    status, warn = "OP", None
    if typ == "STD" and erp.sp("sp_so_credit_chk", cust, gross) == "HOLD":
        status, warn = "CH", "W-SO-114"  # saved, silently, on credit hold: never reaches dispatch
    ord_no = erp.sp("sp_doc_no_next", "SOO")
    erp.x("INSERT INTO so_ord VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ord_no, typ, a.get("qtn_no"), cust["cust_cd"],
          itm_cd, qty, rate, disc, tax_cd, gross, "WH-PUN-FG", status, user, erp.now(), None, warn, a.get("client_ref"))
    if typ == "STD":
        erp.sp("sp_so_status_set", "so_qtn", "qtn_no", a["qtn_no"], "CV")
    return {"ord_no": ord_no, "status": status, "gross_value": gross}


@proc("sp_so_stk_alloc")
def stk_alloc(erp, itm_cd: str, whs_cd: str, qty: int):
    """Cascade 1: a released order reserves finished stock."""
    s = erp.q1("SELECT * FROM stock WHERE itm_cd=? AND whs_cd=?", itm_cd, whs_cd)
    if not s or s["on_hand"] - s["allocated"] < qty:
        raise BahiError("ERR-SO-0520", "INSUFFICIENT FREE STOCK")
    erp.x("UPDATE stock SET allocated=allocated+? WHERE itm_cd=? AND whs_cd=?", qty, itm_cd, whs_cd)


@proc("sp_so_dsp_advice")
def dsp_advice(erp, o: dict):
    """Cascade 2: a dispatch advice for the finished-goods store, and a mail to the customer's sales rep."""
    erp.x("INSERT INTO so_dsp(ord_no,whs_cd,itm_cd,qty,status,created_on) VALUES (?,?,?,?,?,?)",
          o["ord_no"], o["whs_cd"], o["itm_cd"], o["qty"], "OPEN", erp.now())
    rep = erp.q1("SELECT sales_rep FROM so_cust WHERE cust_cd=?", o["cust_cd"])["sales_rep"]
    erp.sp("sp_ntf_enqueue", "EMAIL", "fg.dispatch@rasoisteel.example", f"Dispatch {o['ord_no']}",
           f"{o['qty']} x {o['itm_cd']} for {o['cust_cd']} from {o['whs_cd']}")
    if rep and erp.user(rep):
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(rep)["email"], f"{o['ord_no']} released", "")


@proc("sp_so_status_set")
def status_set(erp, table: str, key: str, no: str, status: str):
    erp.x(f"UPDATE {table} SET status=? WHERE {key}=?", status, no)
