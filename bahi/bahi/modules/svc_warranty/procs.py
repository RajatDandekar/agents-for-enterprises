"""Service · warranty: the stored procedures. The rules live here; services call them through erp.sp()."""
from __future__ import annotations

import datetime as dt

from ...erp.engine import BahiError, proc

SVC_WHS = "WH-PUN-STR"  # service parts are issued from Pune main stores


def _add_months(d: str, n: int) -> str:
    y, m, day = (int(x) for x in d.split("-"))
    m += n
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    for dd in (day, 30, 29, 28):
        try:
            return dt.date(y, m, dd).isoformat()
        except ValueError:
            continue
    raise ValueError(d)


@proc("sp_wr_serial_get")
def serial_get(erp, serial: str) -> dict:
    s = erp.q1("SELECT * FROM wr_serial WHERE serial=?", serial.upper())
    if not s:
        raise BahiError("ERR-WR-0101", "SERIAL NOT FOUND")
    if s["status"] == "BLOCKED":
        raise BahiError("ERR-WR-0110", "SERIAL BLOCKED, CONTACT SERVICE MGR")
    return s


@proc("sp_wr_part_term")
def part_term(erp, model: str, part_cd: str) -> dict:
    """Which warranty group a part belongs to for this model, its months and its service price."""
    p = erp.q1("SELECT p.*, t.months FROM wr_part p JOIN wr_term t ON t.grp=p.grp WHERE p.part_cd=? AND p.model IN (?, '*')",
               part_cd, model)
    if not p:
        raise BahiError("ERR-WR-0215", "PART NOT FOR MODEL")
    return p


@proc("sp_wr_wty_chk")
def wty_chk(erp, s: dict, term: dict) -> tuple[bool, str, str]:
    """In warranty? Counts from the registered sale date; with no sale registered, from the manufacturing date.
    That fallback is the silent outcome: a recent sale that was never registered looks out of warranty."""
    basis, start = ("SALE", s["sold_dt"]) if s["sold_dt"] else ("MFG", s["mfg_dt"])
    to = _add_months(start, term["months"])
    return erp.today <= to, basis, to


@proc("sp_wr_dup_chk")
def dup_chk(erp, serial: str, part_cd: str):
    r = erp.q1("SELECT tkt_no FROM wr_ticket WHERE serial=? AND part_cd=? AND status IN ('OP','CQ','WA','PI')",
               serial, part_cd)
    if r:
        raise BahiError("ERR-WR-0301", f"OPEN TICKET {r['tkt_no']} EXISTS")


@proc("sp_wr_charge")
def charge(erp, price: float) -> float:
    """Chargeable repair: service price plus GST through the shared tax engine (customers are billed GST18-INTRA
    by the dealer in Maharashtra)."""
    _, gross = erp.sp("sp_tax_compute", price, "GST18-INTRA")
    return gross


@proc("sp_wr_sale_chk")
def sale_chk(erp, s: dict, sold_dt: str, dealer_cd: str):
    if s["sold_dt"]:
        raise BahiError("ERR-WR-0120", f"SALE ALREADY REGISTERED ({s['sold_dt']})")
    if sold_dt < s["mfg_dt"] or sold_dt > erp.today:
        raise BahiError("ERR-WR-0121", "SOLD DT OUT OF RANGE")
    if not erp.q1("SELECT 1 FROM wr_dealer WHERE dealer_cd=?", dealer_cd):
        raise BahiError("ERR-WR-0122", "DEALER NOT FOUND")


@proc("sp_wr_waive_route")
def waive_route(erp, t: dict, user: str, fwd_to: str | None) -> str | None:
    """Goodwill waiver. Within the desk's own limit Bahi grants it at once (returns None). Above it, or when FWD TO
    is filled, it goes to an approver: FWD TO, or the shared approval engine sp_appr_route by amount."""
    if not fwd_to and t["amount"] <= erp.user(user)["appr_limit"]:
        return None
    if fwd_to:
        if not erp.user(fwd_to):
            raise BahiError("ERR-WR-0410", "FWD TO USER NOT FOUND")
        erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES (?,?,?,?,?,?)",
              "WR", t["tkt_no"], fwd_to, "PENDING", user, erp.now())
        erp.sp("sp_ntf_enqueue", "EMAIL", erp.user(fwd_to)["email"], f"{t['tkt_no']} waiver awaiting you",
               f"Goodwill waiver of {t['amount']:,.2f} on {t['serial']}")
        return fwd_to
    return erp.sp("sp_appr_route", "WR", t["tkt_no"], user, t["amount"])


@proc("sp_wr_stk_issue")
def stk_issue(erp, part_cd: str, qty: int, ref: str):
    """Cascade 1: a part issued for service leaves stores stock, with a stock ledger line."""
    s = erp.q1("SELECT * FROM stock WHERE itm_cd=? AND whs_cd=?", part_cd, SVC_WHS)
    if not s or s["on_hand"] - s["allocated"] < qty:
        raise BahiError("ERR-WR-0430", "NO STOCK FOR PART")
    erp.x("UPDATE stock SET on_hand=on_hand-? WHERE itm_cd=? AND whs_cd=?", qty, part_cd, SVC_WHS)
    erp.x("INSERT INTO stk_ledger(itm_cd,whs_cd,dt,txn,qty,ref) VALUES (?,?,?,?,?,?)",
          part_cd, SVC_WHS, erp.today, "SVC-ISS", -qty, ref)


@proc("sp_wr_cost_book")
def cost_book(erp, t: dict, price: float):
    """Cascade 2a: on closing, the cost lands where it belongs: warranty, goodwill, or charged to the customer."""
    kind = {"N": "WARRANTY", "W": "GOODWILL", "Y": "CHARGED"}[t["chg"]]
    erp.x("INSERT INTO wr_cost VALUES (?,?,?,?)", t["tkt_no"], kind, t["amount"] if t["chg"] == "Y" else price, erp.now())


@proc("sp_wr_dealer_ntf")
def dealer_ntf(erp, t: dict):
    """Cascade 2b: the dealer is told the ticket is closed."""
    d = erp.q1("SELECT * FROM wr_dealer WHERE dealer_cd=?", t["dealer_cd"] or "")
    if d:
        erp.sp("sp_ntf_enqueue", "EMAIL", d["email"], f"Service ticket {t['tkt_no']} closed",
               f"{t['part_cd']} replaced on serial {t['serial']}.")


@proc("sp_wr_status_set")
def status_set(erp, tkt_no: str, status: str):
    erp.x("UPDATE wr_ticket SET status=?, closed_on=? WHERE tkt_no=?", status,
          erp.now() if status in ("CL", "CN") else None, tkt_no)
