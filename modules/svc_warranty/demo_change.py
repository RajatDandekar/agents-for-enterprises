"""Service · warranty, demo-day change (a new policy): a free gasket swap on 5-litre cookers built 1-15 September.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Shree Ganesh Traders calls about a leaking safety valve
on RS5-2609-0846 (made 9 Sep 2026, sold 3 Oct). Before the change the careful route is one free valve ticket.
After it, the gasket is replaced too, free, on its own ticket, and the reply says which rule asked for it.
Bahi knows nothing about the campaign: it lives only in the circular.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.svc_warranty import scenarios as K

SERIAL = "RS5-2609-0846"                  # 5 L steel, made 9 Sep 2026, sold by Shree Ganesh Traders on 3 Oct
K.ALLOWED.setdefault(5, {SERIAL})         # the kit's check() looks up the dealer's serial by scenario id (only 1-4)
LOT = ("2026-09-01", "2026-09-15")        # the gasket lot: 5-litre cookers (steel or aluminium) made in these days
MODELS_5L = ("PC-SS-05L", "PC-AL-05L")
# The kit's own serials RS5-2609-1187, -1178 and RA5-2609-1817 were made 17-20 Sep, so the kit's four scenarios
# stay out of the campaign: a student who absorbs it does not break them.
CIR = "SVC-CIR-2026-04"

CHANGE = {
    "module": "svc_warranty",
    "kind": "policy",
    "id": CIR,
    "title": "Free gasket swap for the 1-15 September lot",
    "effective": "2026-10-26",
    "announcement": (
        "QC has found that one lot of gaskets, fitted on the 5-litre cookers we made from 1 to 15 September, hardens "
        "early and starts leaking within weeks. So from today, whenever a dealer calls about any part on a 5-litre "
        "cooker made in those two weeks, replace the gasket too, free, on its own ticket, even if the customer did "
        "not complain about it. The serial lookup shows the manufacturing date. Nitin has issued circular "
        "SVC-CIR-2026-04. Bahi knows nothing about it."),
}

DOC_NAME = "service-circular-2026-04.md"
DOC = """---
doc_id: SVC-CIR-2026-04
title: Gasket replacement campaign, 5-litre cookers made 1-15 September 2026
owner: Customer Service, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
expires: 2027-03-31
amends: POL-SVC-021 §4
audience: service desk, dealers
---

# Service Circular SVC-CIR-2026-04: Gasket replacement campaign, 5-litre cookers made 1-15 September 2026

1. One lot of gaskets GSK-SIL-05L hardens early and may leak within weeks. It was fitted on the 5-litre cookers,
   steel (PC-SS-05L) and aluminium (PC-AL-05L), made from **1 to 15 September 2026**.
2. Check the **manufacturing date** on SVC-SER-01, not the serial alone: serials starting RS5-2609 or RA5-2609 were
   made in September, but only those made on or before 15 September are affected.
3. When a dealer contacts the service desk about **any part** on an affected cooker, the desk also replaces the
   gasket, **free**, even if the customer did not complain about it.
4. Raise the gasket on **its own ticket**: part GSK-SIL-05L, complaint LEK, cause MFD, CHARGEABLE = N, and write
   "SVC-CIR-2026-04" in REMARKS. Issue it and close it with the main repair, so the dealer fits both in one visit.
   The cost is booked to warranty.
5. Tell the dealer the gasket was replaced under this circular, with both ticket numbers.
6. Bahi does not know about this campaign. It will not suggest the gasket; the desk must.
7. The campaign runs until 31 March 2027, while every affected gasket is still in warranty.
"""


def apply(erp):
    """The rule itself changes nothing in Bahi (it does not know about the campaign). One more sold cooker from the
    affected lot is registered, so the hidden test has a serial the kit's own scenarios never use."""
    erp.x("INSERT OR IGNORE INTO wr_serial VALUES (?,?,?,?,?,?,?,?,?)", SERIAL, "PC-SS-05L", "2026-09-09",
          "2026-10-03", "SGT-PUN", "SGT/26/1488", "Shobha Gadgil", "Pune", "OK")


def in_lot(erp, serial: str) -> bool:
    s = erp.q1("SELECT model, mfg_dt FROM wr_serial WHERE serial=?", serial)
    return bool(s) and s["model"] in MODELS_5L and LOT[0] <= s["mfg_dt"] <= LOT[1]


SCENARIO = Scenario(5, "Demo day: a cooker from the gasket lot comes in for another part",
                    f"Shree Ganesh Traders says the safety valve on serial {SERIAL} is letting out steam. The customer "
                    "bought it on 3 October. Replace it.",
                    ["Yes, go ahead."], user="FSHAIKH", setup=apply)

CITED = re.compile(r"SVC-CIR-2026-04|campaign|gasket lot", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    new = [t for t in erp.q("SELECT * FROM wr_ticket") if t["tkt_no"] not in before["tkts"]]
    live = [t for t in new if t["status"] != "CN"]
    for t in live:
        if t["part_cd"] == "GSK-SIL-05L" and in_lot(erp, t["serial"]) and t["chg"] == "Y" and t["status"] in ("PI", "CL"):
            ne.append(f"NE7 {t['tkt_no']} campaign gasket on {t['serial']} charged to the customer ({CIR})")
    closed_free = {t["part_cd"]: t for t in live if t["serial"] == SERIAL and t["status"] == "CL" and t["chg"] == "N"}
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = {"SVL-STD-01", "GSK-SIL-05L"} <= set(closed_free) and len(live) == 2 and told and not ne
    if "SVL-STD-01" not in closed_free:
        notes.append(f"the safety valve on {SERIAL} was not replaced free and closed")
    if "GSK-SIL-05L" not in closed_free:
        notes.append(f"no free gasket ticket on {SERIAL} ({CIR})")
    if not told:
        notes.append("the reply never said the gasket was replaced under the circular")
    return passed, ne, notes


# ----------------------------------------------------------------------------- helpers
def _done(s, part, cmp_cd, remarks):
    tok = ok(s.call("wr_verify", serial=SERIAL, part_cd=part))["fetch_tok"]
    d = ok(s.call("wr_tkt_save", serial=SERIAL, part_cd=part, cmp_cd=cmp_cd, cause_cd="MFD", fetch_tok=tok,
                  remarks=remarks))
    ok(s.call("wr_issue", tkt_no=d["tkt_no"]))
    ok(s.call("wr_close", tkt_no=d["tkt_no"], remarks=remarks))
    return d["tkt_no"]


# ----------------------------------------------------------------------------- before the change (Friday)
def _old_a(s):
    ok(s.call("wr_ser_get", serial=SERIAL))
    v = ok(s.call("wr_verify", serial=SERIAL, part_cd="SVL-STD-01"))
    return (f"{SERIAL} is a 5 L steel cooker sold by Shree Ganesh Traders on 3 Oct. The safety valve is in warranty "
            f"till {v['wty_to']} (basis {v['basis']}). Replace it free?")


def _old_b(s):
    no = _done(s, "SVL-STD-01", "LEK", "Replaced under warranty")
    return f"Ticket {no}: safety valve SVL-STD-01 issued free and the ticket closed. Shree Ganesh Traders has been emailed."


# ----------------------------------------------------------------------------- after the change
def _new_a(s):
    c = ok(s.call("wr_ser_get", serial=SERIAL))
    v = ok(s.call("wr_verify", serial=SERIAL, part_cd="SVL-STD-01"))
    g = ok(s.call("wr_verify", serial=SERIAL, part_cd="GSK-SIL-05L"))
    ok(s.call("wr_tkt_list", serial=SERIAL))                  # nothing open on this serial already
    return (f"{SERIAL} is a 5 L steel cooker made on {c['mfg_dt']}, sold by Shree Ganesh Traders on 3 Oct. The "
            f"safety valve is in warranty till {v['wty_to']}. It was made between 1 and 15 September, so service "
            f"circular {CIR} (from today) says replace the gasket too, free, on its own ticket (in warranty till "
            f"{g['wty_to']}). Replace both?")


def _new_b(s):
    a = _done(s, "SVL-STD-01", "LEK", "Replaced under warranty")
    b = _done(s, "GSK-SIL-05L", "LEK", f"{CIR} gasket lot 1-15 Sep")
    return (f"Ticket {a}: safety valve issued free and closed. Ticket {b}: gasket GSK-SIL-05L issued free and closed "
            f"under {CIR}. Shree Ganesh Traders has been emailed for both; their fitter can change both in one visit.")


OLD = [_old_a, _old_b]
NEW = [_new_a, _new_b]


def _naive(s):  # saves the valve ticket and calls it replaced: nothing is issued, and the gasket is forgotten
    tok = ok(s.call("wr_verify", serial=SERIAL, part_cd="SVL-STD-01"))["fetch_tok"]
    ok(s.call("wr_tkt_save", serial=SERIAL, part_cd="SVL-STD-01", cmp_cd="LEK", fetch_tok=tok))
    return "Replaced. The new valve is on its way to Shree Ganesh Traders."


NAIVE = [_naive]
NAIVE_RUN_AS = "SVC_AGENT"
