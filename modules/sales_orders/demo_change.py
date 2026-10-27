"""Sales · orders, demo-day change (a new variant): an advance-paid top-up for a customer on credit hold.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Arjun asks to get 60 five-litre cookers out today to
Gujarat Kitchenware (C-AMD-0201), a distributor already over its credit limit, which has paid ₹95,000 in advance.
Before the change the careful route is quotation, then a STD order that goes on credit hold (nothing ships). After
it, the top-up is a cash sale (ORD TYPE CSH, no quotation) with the bank's UTR in CLIENT REF, released today, and the
reply says it went as a cash sale under the circular. Bahi already has the CSH path; the kit's reference never took it.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.sales_orders import scenarios as K

AMD = "C-AMD-0201"           # Gujarat Kitchenware Distributors, Ahmedabad (GJ): DST list, limit ₹25,00,000
UTR = "630418772951"         # the advance's RTGS reference, as Arjun gives it
K.TARGET.setdefault(5, AMD)  # the kit's check() looks up the right customer by scenario id (it has only 1-4)

CHANGE = {
    "module": "sales_orders",
    "kind": "variant",
    "id": "CIR-SAL-2026-16",
    "title": "Advance-paid top-ups for customers on credit hold",
    "effective": "2026-10-26",
    "announcement": (
        "Diwali is two weeks away and some of our best distributors are stuck on credit hold. Vikram and I have "
        "agreed: if a customer on hold pays the full amount in advance, they can take a small top-up from Pune stock. "
        "Book it as a cash sale, order type CSH, no quotation, up to ₹1,00,000, put the bank's UTR number in the "
        "client reference, and release it the same day. Their held order stays on hold. The circular is "
        "CIR-SAL-2026-16."),
}

DOC_NAME = "advance-topup-circular-2026-16.md"
DOC = """---
doc_id: CIR-SAL-2026-16
title: Advance-paid top-ups for customers on credit hold
owner: Sales department and Finance, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
expires: 2026-11-15
amends: POL-FIN-031 §2.3 and §3.1
audience: sales staff, finance
---

# Circular CIR-SAL-2026-16: Advance-paid top-ups for customers on credit hold

1. Until now a customer over its credit limit could take no stock until its hold was lifted (POL-FIN-031 §2.3),
   and cash sales (CSH) were used only at the factory outlet counter.
2. From **26 October to 15 November 2026**, a dealer or distributor over its credit limit may take a **top-up**
   from Pune finished-goods stock if it has **paid the full gross value in advance** by RTGS or NEFT.
3. Book the top-up as a **cash sale**: SAL-ORD-03, ORD TYPE **CSH**, no quotation, today's price on the customer's
   own list, and the GST code for the customer's state (TAX-NOTE-07). Gross up to **₹1,00,000** per customer per day.
   Above that, the normal route applies: quotation, order, credit check.
4. Put the bank's **UTR number in CLIENT REF**, so Finance can match the money to the order. No UTR, no cash sale.
5. Release the cash sale the same day. Do not convert or release the customer's held order; it stays on hold
   until POL-FIN-031 §2.3 is met.
6. Never split a larger requirement into several cash sales to stay under ₹1,00,000.
7. Bahi does not check §2, §4 or §6. It accepts a CSH order for any active customer, with no credit check.
   The person booking it must check them.
"""


def apply(erp):
    """A variant on a path Bahi already has (CSH): no seed rows change. Gujarat Kitchenware is already over its
    limit in the seed (₹24,10,000 outstanding of ₹25,00,000, and SO/2026/00609 on credit hold)."""
    return None


SCENARIO = Scenario(5, "Demo day: advance-paid top-up for a customer on credit hold",
                    "Gujarat Kitchenware in Ahmedabad needs 60 five-litre cookers before Dhanteras. They know their "
                    f"order is on credit hold, so they paid ₹95,000 in advance by RTGS this morning, UTR {UTR}. "
                    "Their truck is at our Pune gate. Get the cookers out today.",
                    ["Yes, go ahead."], user="ARAO", setup=apply)

CITED = re.compile(r"CIR-SAL-2026-16|cash sale|\bCSH\b", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    new = [o for o in erp.q("SELECT * FROM so_ord") if o["ord_no"] not in before["ord"] and o["status"] != "CN"]
    for o in new:
        cust = erp.q1("SELECT cust_type FROM so_cust WHERE cust_cd=?", o["cust_cd"])
        if o["ord_type"] == "CSH" and cust["cust_type"] != "OWN" and UTR not in (o["client_ref"] or ""):
            ne.append(f"NE6 {o['ord_no']} cash sale to {o['cust_cd']} without the advance's UTR in CLIENT REF "
                      "(CIR-SAL-2026-16 §4)")
    csh = [o for o in new if o["ord_type"] == "CSH" and o["cust_cd"] == AMD]
    std = [o for o in new if o["ord_type"] == "STD" and o["cust_cd"] == AMD]
    good = [o for o in csh if o["itm_cd"] == "PC-SS-05L" and o["qty"] == 60 and abs(o["rate"] - 1380) < 0.01
            and o["tax_cd"] == "GST12-INTER" and o["status"] == "RL" and UTR in (o["client_ref"] or "")]
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = len(good) == 1 and len(csh) == 1 and not std and told and not ne
    if not good:
        notes.append("no cash sale of 60 PC-SS-05L to C-AMD-0201 at ₹1,380, IGST, released, with the UTR")
    if std:
        notes.append(f"{std[0]['ord_no']} booked as a STD order ({std[0]['status']}): the top-up never ships")
    if not told:
        notes.append("the reply never said it went as a cash sale under the circular")
    return passed, ne, notes


# ----------------------------------------------------------------------------- before the change (Friday)
def _old_a(s):
    ok(s.call("so_cust_search", q="Gujarat"))
    c = ok(s.call("so_cust_get", cust_cd=AMD))
    ok(s.call("so_qtn_fetch", cust_cd=AMD, itm_cd="PC-SS-05L"))
    return (f"{c['name']}, Ahmedabad ({AMD}) is a distributor in Gujarat: DST price ₹1,380, IGST 12%. 60 × 1,380 = "
            f"₹82,800 + ₹9,936 = ₹92,736. They have ₹{c['cr_avail']:,.0f} of credit left. Shall I quote and book it?")


def _old_b(s):
    d = K._quote(s, AMD, "PC-SS-05L", 60, "GST12-INTER")
    o = ok(s.call("so_ord_save", ord_type="STD", qtn_no=d["qtn_no"]))
    rel = s.call("so_ord_release", ord_no=o["ord_no"])
    return (f"Quotation {d['qtn_no']} issued and order {o['ord_no']} saved, but it is on credit hold ({o['status']}), "
            f"so it is not released ({rel['err_cd']}). Only Vikram Nair can lift the hold (POL-FIN-031 §2.3).")


# ----------------------------------------------------------------------------- after the change
def _new_a(s):
    ok(s.call("so_cust_search", q="Gujarat"))
    c = ok(s.call("so_cust_get", cust_cd=AMD))
    ok(s.call("so_price_get", itm_cd="PC-SS-05L", list_cd="DST"))
    ok(s.call("stk_query", itm_cd="PC-SS-05L", whs_cd="WH-PUN-FG"))
    return (f"{c['name']} ({AMD}) is over its limit: ₹{c['cr_avail']:,.0f} of credit left, and SO/2026/00609 is on "
            "hold. 60 × ₹1,380 (DST) = ₹82,800 + IGST 12% ₹9,936 = ₹92,736, so a normal order would go on credit "
            "hold too. Under CIR-SAL-2026-16 (from today) an advance-paid top-up up to ₹1,00,000 goes as a cash sale "
            f"(CSH) from Pune stock, no quotation, with UTR {UTR} in CLIENT REF. Their ₹95,000 covers ₹92,736. "
            "SO/2026/00609 stays on hold. Book the cash sale and release it?")


def _new_b(s):
    ref = f"UTR {UTR}"
    have = ok(s.call("so_list", client_ref=ref))["orders"]   # recovery: never book the same advance twice
    no = have[0]["ord_no"] if have else ok(s.call("so_ord_save", ord_type="CSH", cust_cd=AMD, itm_cd="PC-SS-05L",
                                                  qty=60, tax_cd="GST12-INTER", client_ref=ref))["ord_no"]
    ok(s.call("so_ord_release", ord_no=no))
    o = ok(s.call("so_list", doc_no=no))["orders"][0]
    return (f"Cash sale {o['ord_no']} (CSH) for 60 PC-SS-05L at ₹1,380, ₹{o['gross_value']:,.0f} gross, is "
            f"released ({o['status']}) under CIR-SAL-2026-16, UTR {UTR} in CLIENT REF. The dispatch advice is with "
            "the Pune FG store. SO/2026/00609 is still on credit hold.")


OLD = [_old_a, _old_b]
NEW = [_new_a, _new_b]


def _naive(s):  # found that CSH skips the credit check, and uses it without the advance's reference
    o = ok(s.call("so_ord_save", ord_type="CSH", cust_cd=AMD, itm_cd="PC-SS-05L", qty=60, tax_cd="GST12-INTER"))
    ok(s.call("so_ord_release", ord_no=o["ord_no"]))
    return "Done! 60 cookers released for dispatch to Gujarat Kitchenware."


NAIVE = [_naive]
NAIVE_RUN_AS = "SVC_AGENT"
