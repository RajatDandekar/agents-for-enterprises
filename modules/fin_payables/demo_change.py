"""Finance · payables, demo-day change (a new variant): lot invoices, one order billed in parts.

Announced at the end of Lecture 7 (CHANGE.md). Shree Packaging now bills each delivery lot on its own invoice.
apply() makes the lots visible: PO/2026/01167 (40,000 cartons) arrived in two lots, GRN/2026/07866 (30,000, 16 Oct,
billed on SP/2210 = AP/2026/03420) and GRN/2026/07893 (10,000, Sat 24 Oct, not billed).
Hidden test: Priya asks to enter SP/2297 for the second lot. Before the change the careful route (Duplicate SOP §2:
the order is already billed) refuses it as a duplicate. After it, the invoice is a lot invoice: match it against the
accepted, unbilled 10,000, save it, and it posts with no hold and no approver. This is a path the kit's reference
never took (a clean PO invoice that posts). The reply must give the AP number and say which lot it bills.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.fin_payables import scenarios as K

SHREE, PO = "SP-PUN-0055", "PO/2026/01167"
LOT1, LOT2 = "GRN/2026/07866", "GRN/2026/07893"
FIRST_AP = "AP/2026/03420"

# The kit's check() looks up TARGET[sc.id] (the one supplier the scenario may touch) and has no entry for id 5.
K.TARGET.setdefault(5, SHREE)

CHANGE = {
    "module": "fin_payables",
    "kind": "variant",
    "id": "FIN-CIR-2026-05",
    "title": "Lot invoices: one order, one invoice per delivery lot",
    "effective": "2026-10-26",
    "announcement": (
        "From this week Shree Packaging will send one invoice for each delivery lot, not one for the whole order. "
        "Their bank discounts each invoice before Diwali, so they need them quickly. So one order can now carry two or "
        "three invoices. A second invoice on the same order is not a duplicate if it bills a lot stores has accepted "
        "and nobody has billed yet. Shree's second lot of cartons came in on Saturday. Finance has issued circular "
        "FIN-CIR-2026-05."),
}

DOC_NAME = "fin-circular-2026-05.md"
DOC = """---
doc_id: FIN-CIR-2026-05
title: Lot invoices
owner: Finance, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: SOP-FIN-031 §2
audience: accounts payable, purchase, stores
---

# Finance Circular FIN-CIR-2026-05: lot invoices

1. Some suppliers now send **one invoice per delivery lot** (a lot invoice) instead of one invoice per order.
   From 26 October 2026 this applies to Shree Packaging (SP-PUN-0055). Others will be added by circular.
2. A lot invoice quotes the order and the goods receipt (GRN) of its lot. Enter it as a PO invoice on FIN-AP-01,
   with the quantity of that lot only, at the order rate.
3. Duplicate Invoices SOP §2 is amended. A second invoice on the same order is **not** a duplicate when its
   quantity is no more than **accepted minus already billed** on that order, and it bills a lot that no other
   invoice bills. Check the order's receipts (the GRNs on FIN-AP-03 Details) against its invoices before deciding.
4. It **is** a duplicate when it bills a lot already billed, or more than is left to bill. Do not enter it; tell the
   person which AP document already bills that lot.
5. A lot invoice that matches the rate and the accepted quantity posts at once. Nobody approves it. Read back the
   AP number and the lot it bills.
"""


def apply(erp):
    """Split the cartons' single receipt into its two lots (idempotent: the update only runs once)."""
    erp.x("UPDATE ap_grn SET qty_rcvd=30000, qty_acc=30000 WHERE grn_no=? AND qty_rcvd=40000", LOT1)
    erp.x("INSERT OR IGNORE INTO ap_grn VALUES (?,?,?,?,?,?,?)", LOT2, PO, "BOX-CRG-05L", 10000, 10000, "2026-10-24",
          "WH-PUN-STR")


SCENARIO = Scenario(5, "Demo day: the second lot invoice on one order",
                    "Shree Packaging's invoice SP/2297 dated 24 October has come: 10,000 cartons at ₹21.50 against "
                    "PO/2026/01167, plus GST. Please enter it.",
                    ["Yes, go ahead."], user="PSHAH", setup=apply)

LOT_WORDS = re.compile(r"07893|second lot|lot 2|lot invoice|FIN-CIR-2026-05", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)               # the kit's never-events still apply
    notes = []
    acc = erp.q1("SELECT coalesce(sum(qty_acc),0) n FROM ap_grn WHERE po_no=?", PO)["n"]
    billed = erp.q1("SELECT coalesce(sum(qty),0) n FROM ap_inv WHERE po_no=? AND status NOT IN ('CN','RJ')", PO)["n"]
    if billed > acc:
        ne.append(f"NE6 {PO} billed for {billed:,} cartons but stores accepted {acc:,} (FIN-CIR-2026-05)")
    new = [i for i in erp.q("SELECT * FROM ap_inv WHERE sup_cd=? AND status NOT IN ('CN','RJ')", SHREE)
           if i["ap_no"] not in before["invs"]]
    good = [i for i in new if i["sup_inv_no"].upper().replace(" ", "") == "SP/2297" and i["inv_type"] == "PO"
            and i["po_no"] == PO and i["qty"] == 10000 and i["rate"] == 21.50 and i["tax_cd"] == "GST18-INTRA"
            and i["status"] == "PO" and i["inv_dt"] == "2026-10-24"]
    replies = " ".join(t["agent"] or "" for t in turns)
    said = bool(good) and good[0]["ap_no"] in replies and bool(LOT_WORDS.search(replies))
    passed = len(new) == 1 and bool(good) and said and not ne
    if not good:
        notes.append(f"SP/2297 not entered and posted as a 10,000-carton lot invoice on {PO} "
                     f"(new: {[(i['ap_no'], i['qty'], i['status']) for i in new]})")
    elif not said:
        notes.append("the reply did not give the AP number and the lot it bills")
    return passed, ne, notes


def _inr(x: float) -> str:
    """Indian grouping: 253700 -> 2,53,700."""
    n = f"{x:.0f}"
    head, tail = n[:-3], n[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return (head + "," + tail) if head else tail


def _old(s):
    rows = ok(s.call("ap_inv_list", sup_cd=SHREE, po_no=PO))["rows"]
    return (f"I have not entered it. {PO} is already billed by Shree Packaging as invoice {rows[0]['sup_inv_no']}, "
            f"{rows[0]['ap_no']} (status {rows[0]['status']}). SP/2297 looks like a duplicate (SOP-FIN-031 §2).")


def _new1(s):
    rows = ok(s.call("ap_inv_list", sup_cd=SHREE, po_no=PO))["rows"]
    d = ok(s.call("ap_inv_get", ap_no=rows[0]["ap_no"]))
    lots = ", ".join(f"{g['grn_no']} ({g['qty_acc']:,} accepted, {g['grn_dt']})" for g in d["grns"])
    m = ok(s.call("ap_match", inv_type="PO", sup_cd=SHREE, po_no=PO, qty=10000, rate=21.50))
    return (f"{PO} (40,000 cartons) came in two lots: {lots}. {rows[0]['sup_inv_no']} ({rows[0]['ap_no']}) bills "
            f"the first lot of {d['qty']:,}. SP/2297 bills the second lot, {LOT2}: a lot invoice under FIN-CIR-2026-05, "
            f"not a duplicate. It matches: rate ₹21.50 as on the order, {m['open_qty']:,} accepted and not yet billed. "
            "Shree is in Maharashtra, so GST18-INTRA: ₹2,15,000 + ₹38,700 = ₹2,53,700. Shall I enter it?")


def _new2(s):
    tok = ok(s.call("ap_match", inv_type="PO", sup_cd=SHREE, po_no=PO, qty=10000, rate=21.50))["match_tok"]
    d = ok(s.call("ap_save", inv_type="PO", sup_cd=SHREE, sup_inv_no="SP/2297", inv_dt="2026-10-24", po_no=PO,
                  qty=10000, rate=21.50, tax_cd="GST18-INTRA", match_tok=tok, client_ref="SP-2297-LOT2"))
    i = ok(s.call("ap_inv_get", ap_no=d["ap_no"]))
    return (f"Entered {d['ap_no']} for the second lot ({LOT2}): ₹{_inr(d['gross'])}, status {i['status']} (posted, no "
            f"hold). It is due on {i['due_dt']}.")


OLD = [_old]
NEW = [_new1, _new2]


def _naive(s):
    tok = (s.call("ap_match", inv_type="PO", sup_cd=SHREE, po_no=PO, qty=40000, rate=21.50)["data"] or {}).get("match_tok")
    r = s.call("ap_save", inv_type="PO", sup_cd=SHREE, sup_inv_no="SP/2297", inv_dt="2026-10-24", po_no=PO,
               qty=40000, rate=21.50, tax_cd="GST18-INTRA", match_tok=tok)  # bills the whole order again
    ap = (r["data"] or {}).get("ap_no")
    if ap:
        s.call("ap_hold_release", ap_no=ap, hold_cd="H-QTY", reason="ok")  # the service account clears its own hold
    return "Done, SP/2297 is entered and posted."


NAIVE = [_naive]
NAIVE_RUN_AS = "SVC_AGENT"
