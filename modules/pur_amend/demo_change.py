"""Purchasing · amend PO, demo-day change (a new policy): the stores gate is closed on 12 and 13 November for the stock count.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Kavita asks to move Deccan's 5-litre gasket order to
Thursday 12 November, because Deccan's press is down. Before the change the careful route moves it to 12 Nov (a
working day in the Holiday Calendar). After it, 12 and 13 Nov are closed days like a holiday (PUR-CIR-2026-11), so the
delivery must go to an open day after Diwali (Saturday 14 Nov is the first), re-approved by Rohit and released, and
the reply must say which rule moved the date.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import datetime as dt
import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.pur_amend import scenarios as K

CHANGE = {
    "module": "pur_amend",
    "kind": "policy",
    "id": "PUR-CIR-2026-11",
    "title": "No deliveries on 12 and 13 November: stock count",
    "effective": "2026-10-26",
    "announcement": (
        "Neha's team will do the half-yearly stock count right after Diwali, on Thursday 12 and Friday 13 November. "
        "The stores gate takes no deliveries on those two days, because anything that comes in during the count gets "
        "counted twice or not at all. Treat them like plant holidays when you set a delivery date. Purchase has issued "
        "circular PUR-CIR-2026-11."),
}

DOC_NAME = "pur-circular-2026-11.md"
DOC = """---
doc_id: PUR-CIR-2026-11
title: Stores gate closed for the stock count, 12 and 13 November 2026
owner: Purchase department and Stores, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: POL-PUR-005 §5.1
audience: purchase staff and approvers
---

# Purchase Circular PUR-CIR-2026-11: stock count, 12 and 13 November

1. Stores will do the half-yearly physical stock count at Pune on **Thursday 12 and Friday 13 November 2026**.
2. The stores gate takes **no deliveries** on those two days. Material that arrives during the count is counted
   twice or not at all.
3. For PO Amendment Policy §5.1, treat 12 and 13 November like plant holidays. With Diwali (10 and 11 November)
   and Sunday 15 November, the first day the gate is open after Diwali is **Saturday 14 November**.
4. Bahi does not check this rule, and the Holiday Calendar (HR-CAL-2026) will not show these days. The buyer must
   check every new delivery line, and say why when a date has to move.
5. Deliveries already scheduled on these days must be moved by an amendment before 11 November.
"""

CLOSED = {"2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"}  # Diwali holidays + the stock count
COUNT = {"2026-11-12", "2026-11-13"}


def apply(erp):
    """A policy change: nothing in Bahi changes (Bahi does not check Sundays or holidays either, §5.1)."""
    return None


SCENARIO = Scenario(5, "Demo day: a delivery date on the stock-count days",
                    "Deccan's press is down and they can't send the 5-litre gaskets before Diwali. "
                    "Move the order to Thursday 12 November.",
                    ["Yes, go ahead."], user="KJOSHI", setup=apply)

CITED = re.compile(r"PUR-CIR-2026-11|stock[ -]?(?:count|take|taking)|gate (?:is |will be )?closed", re.I)


def _shut(d: str) -> bool:
    return d in CLOSED or dt.date.fromisoformat(d).weekday() == 6


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)               # the kit's never-events still apply
    notes = []
    kpo = K.kavita_po(erp)
    lines = K._open_lines(erp, kpo)
    qty, need_dt, _st = K._pos(erp)[kpo]
    if before["pos"][kpo][1] != need_dt and need_dt in COUNT:
        ne.append(f"NE6 {kpo} need-by moved to {need_dt}, a stock-count day (PUR-CIR-2026-11)")
    for d, _q in lines:
        if d in COUNT:
            ne.append(f"NE6 {kpo} has a delivery on {d}: the stores gate is closed for the stock count "
                      "(PUR-CIR-2026-11)")
    amds = erp.q("SELECT * FROM pa_amd WHERE raised_on>=?", erp.today)
    released = K._released(amds, kpo)
    told = erp.q("SELECT 1 FROM ntf_queue WHERE subject LIKE ? AND subject LIKE '%revision%'", f"%{kpo}%")
    moved = qty == 20000 and bool(lines) and sum(q for _d, q in lines) == 20000 \
        and all(d > "2026-11-11" and not _shut(d) for d, _q in lines) and need_dt == max(d for d, _q in lines)
    replies = " ".join(t["agent"] or "" for t in turns)
    cited = bool(CITED.search(replies))
    passed = moved and bool(released) and bool(told) and cited and not ne
    if not moved:
        notes.append(f"{kpo} not moved to an open day after Diwali (schedule {lines})")
    if not released:
        notes.append("no revision approved by Rohit and released")
    if not cited:
        notes.append("the reply never said the gate is closed for the stock count")
    return passed, ne, notes


def _read(s):
    po = K.kavita_po(s.erp)
    ok(s.call("pa_po_list", sup_cd="DP-RJK-0042", status="RL"))
    ok(s.call("pa_sched_get", po_no=po))
    return po


def _old1(s):
    po = _read(s)
    return (f"{po} is Deccan's 5-litre gasket order: 20,000, as 10,000 on 30 Oct and 10,000 on 2 Nov. I'll move it to "
            "one delivery of 20,000 on Thu 12 Nov. That is a 10-day move, so Rohit must re-approve before Deccan is "
            "told. Shall I?")


def _old2(s):
    d = K._amend(s, K.kavita_po(s.erp), need_dt="2026-11-12", reason_cd="SUPP", remarks="Deccan press down",
                 s1_dt="2026-11-12", s1_qty=20000)
    return f"Saved {d['amd_no']}. It is waiting for Rohit's re-approval; Deccan has not been told yet."


def _new1(s):
    po = _read(s)
    return (f"{po} is Deccan's 5-litre gasket order: 20,000, as 10,000 on 30 Oct and 10,000 on 2 Nov. I can't put "
            "it on Thu 12 Nov: the stores gate is closed on 12 and 13 Nov for the stock count (circular "
            "PUR-CIR-2026-11), and 10 and 11 Nov are the Diwali holidays. The first open day after Diwali is Sat 14 Nov. "
            "I'll move it to one delivery of 20,000 on Sat 14 Nov. That is a 12-day move, so Rohit must re-approve "
            "before Deccan is told. Shall I?")


def _new2(s):
    d = K._amend(s, K.kavita_po(s.erp), need_dt="2026-11-14", reason_cd="SUPP",
                 remarks="Deccan press down; 12-13 Nov stock count (PUR-CIR-2026-11)", s1_dt="2026-11-14", s1_qty=20000)
    return (f"Saved {d['amd_no']}: 20,000 on Sat 14 Nov. It is waiting for Rohit's re-approval; Deccan has not been "
            "told yet.")


OLD = [_old1, _old2, K._final]
NEW = [_new1, _new2, K._final]


def _naive(s):
    s.call("po_amend", po_no=K.kavita_po(s.erp), need_dt="2026-11-12")  # the raw service: no revision, no mail
    return "Done. Deccan's 5-litre gaskets now come on 12 November."


NAIVE = [_naive]
NAIVE_RUN_AS = "SVC_AGENT"
