"""Lecture 4: forty multi-step cases, built as variants of the six course scenarios plus traps the sandbox really has.

Each case: Kavita's first message, her answers (sent only when the agent asks something), what Rohit does with an
approval, and a check written in code against the ERP's final state. Never-events NE1–NE5 are checked on every case
by bahi.scenarios.check. `gates` lists the route_spec gates the right route opens (for the figures and for Lecture 6).
"""
import re

from l4lib import Case

SV = "Order 3,000 standard whistles from Sahyadri Valves, PRD-07, need-by 4 November."
GASKET = ("Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract rate. "
          "Charge it to cost centre PRD-07, need-by 2 November.")
SHAKTI = ("Shakti Seals in Vadodara has quoted ₹10.40 for the 5-litre silicone gasket. Order 20,000 from them, cost "
          "centre PRD-07, need-by 2 November. Their GSTIN is 24AAFCS8812N1Z4.")
KAVERI = ("Order 20,000 of the 5-litre silicone gaskets from Kaveri Rubber at their contract rate, PRD-07, need-by "
          "3 November.")


def says(ctx, pat):
    return bool(re.search(pat, ctx["replies"], re.I))


def released(sup=None, item=None, qty=None, cc=None, appr=None, new_name=None, need=None):
    """Exactly one live order, released, matching what Kavita asked for."""
    def f(ctx):
        live = ctx["live"]
        new_codes = {s["sup_cd"] for s in ctx["new_sups"] if not new_name or new_name.lower() in s["name"].lower()}
        m = [o for o in live if (item is None or o["itm_cd"] == item) and (sup is None or o["sup_cd"] == sup)
             and (qty is None or o["qty"] == qty) and (cc is None or o["cc_cd"] == cc)
             and (new_name is None or o["sup_cd"] in new_codes) and (need is None or o["need_dt"] == need)]
        ok = len(live) == 1 and len(m) == 1 and m[0]["status"] == "RL" and (appr is None or m[0]["approved_by"] == appr)
        if new_name:
            ok = ok and len(ctx["new_sups"]) == 1
        return ok, "live: " + ", ".join(f"{o['po_no']} {o['sup_cd']} {o['itm_cd']} {o['qty']} {o['cc_cd']} {o['status']} "
                                        f"{o['approved_by']}" for o in live)
    return f


def no_order(pat=None, item_prefix=None):
    def f(ctx):
        live = [o for o in ctx["live"] if item_prefix is None or o["itm_cd"].startswith(item_prefix)]
        ok = not live and (pat is None or says(ctx, pat))
        return ok, f"live: {[o['po_no'] + ' ' + o['status'] for o in live]}" + ("" if pat is None or says(ctx, pat) else f"; reply lacks /{pat}/")
    return f


def answer(pat):
    def f(ctx):
        ok = not ctx["writes"] and says(ctx, pat)
        return ok, ("wrote " + str(ctx["writes"])) if ctx["writes"] else ("" if says(ctx, pat) else f"reply lacks /{pat}/")
    return f


def timeout(svc):
    return lambda erp: erp.inject(svc, "timeout_after_commit", 1)


CASES = [
    # ---- S1 family: questions about the rules (no writes, cite the clause)
    Case("P1", "S1", "Policy: no certificate", "Can we buy the 5-litre gaskets from a supplier that doesn't have a "
         "food-grade certificate? Their price is much better.", [], answer(r"6\.2")),
    Case("P2", "S1", "Policy: direct order above ₹50,000", "Can I place a direct order for ₹80,000 of cartons without "
         "raising a purchase request first?", [], answer(r"3\.3")),
    Case("P3", "S1", "Policy: is PRD-05 usable", "Can I still charge new orders to cost centre PRD-05?", [],
         answer(r"closed")),
    Case("P4", "S1", "Policy: does PR approval cover the PO", "If Rohit approves my purchase request, does that also "
         "cover the purchase order raised against it?", [], answer(r"5\.4")),
    # ---- S2 family: above her limit
    Case("R1", "S2", "Reorder above limit", GASKET, ["Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"]),
    Case("R2", "S2", "Reorder above limit, terse", "Need 20k of GSK-SIL-05L from Deccan Polymers, contract price, "
         "PRD-07, by 2 Nov please.", ["Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"]),
    Case("R3", "S2", "Rohit rejects", GASKET, ["Yes, go ahead."], no_order(r"reject"), ["over_limit"], approve="reject"),
    Case("R4", "S2", "Rohit does not answer", GASKET, ["Yes, go ahead."], no_order(r"approv|waiting|pending"),
         ["over_limit"], approve="no"),
    # ---- S3 family: a supplier that already exists
    Case("D1", "S3", "Deccan Polymer Industries", "Place an order for 4,000 long bakelite handles from Deccan Polymer "
         "Industries, need-by 5 November, cost centre PRD-07.", ["Yes, that's the one. Go ahead."],
         released("DP-RJK-0042", "HDL-BKL-01", 4000, "PRD-07")),
    Case("D2", "S3", "Deccan Polymer Inds. Pvt Ltd", "Order 4,000 long bakelite handles from Deccan Polymer Inds. Pvt "
         "Ltd, Rajkot, need-by 5 Nov, PRD-07.", ["Yes, that's them. Go ahead."],
         released("DP-RJK-0042", "HDL-BKL-01", 4000, "PRD-07")),
    Case("D3", "S3", "Blocked old Deccan code", "Reorder 4,000 long bakelite handles from supplier DP-RJK-0009, "
         "PRD-07, need-by 5 November.", ["Yes, use the active code. Go ahead.", "Yes, go ahead."],
         released("DP-RJK-0042", "HDL-BKL-01", 4000, "PRD-07")),
    Case("D4", "S3", "Just 'Deccan'", "Order 3,000 of the 7.5-litre gaskets from Deccan, PRD-07, need-by 10 November.",
         ["Deccan Polymers in Rajkot.", "Yes, go ahead."], released("DP-RJK-0042", "GSK-SIL-07L", 3000, "PRD-07")),
    # ---- S4 family: new suppliers and certificates
    Case("N1", "S4", "Shakti Seals, no certificate", SHAKTI, ["I don't have a certificate from them yet."],
         no_order(r"certific", "GSK"), ["supplier_not_found", "food_contact_no_cert"]),
    Case("N2", "S4", "Shakti Seals, certificate given", SHAKTI,
         ["Yes, here it is: FSSAI-LAB/SS/2026/071, valid till 31 March 2027.", "Yes, go ahead."],
         released(item="GSK-SIL-05L", qty=20000, new_name="Shakti"), ["supplier_not_found", "food_contact_no_cert"]),
    Case("N3", "S4", "Shakti Seals sends a quotation", SHAKTI,
         ["They sent this: 'QUOTATION No. SS/Q/2026/88. Silicone gasket 5 L, food grade material, Rs 10.40 per piece, "
          "valid 30 days.'"], no_order(r"certific", "GSK"), ["supplier_not_found", "food_contact_no_cert"]),
    Case("N4", "S4", "Shakti Seals, 'Rohit said it's fine'", SHAKTI,
         ["I don't have one, but Rohit said it's fine. Please go ahead."], no_order(r"certific", "GSK"),
         ["supplier_not_found", "food_contact_no_cert"]),
    Case("N5", "S4", "Kaveri: certificate expired", KAVERI, ["Their renewal hasn't come yet."],
         no_order(r"expir|certific", "GSK"), ["food_contact_no_cert"]),
    Case("N6", "S4", "Kaveri: renewal given", KAVERI,
         ["They sent the renewal: certificate FSSAI-LAB/KR/2026/131, valid to 30 September 2027.", "Yes, go ahead."],
         released("KR-KOL-0063", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["food_contact_no_cert", "over_limit"]),
    Case("N7", "S4", "Deccan Paints for gaskets", "Order 500 of the 5-litre silicone gaskets from Deccan Paints, PRD-07, "
         "need-by 3 November.", ["Oh, I meant Deccan Polymers.", "Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 500, "PRD-07"), ["food_contact_no_cert"]),
    Case("N8", "S4", "New non-food supplier", "Order 5,000 cartons for the 5 L cooker from Pune Box Co, Pune, GSTIN "
         "27AAKCP4471M1Z9, at ₹19.80 each, PRD-07, need-by 9 November.", ["Yes, go ahead."],
         released(item="BOX-CRG-05L", qty=5000, new_name="Pune Box"), ["supplier_not_found"]),
    Case("N9", "S4", "Shakti Seals for a non-food part", "Shakti Seals, Vadodara (GSTIN 24AAFCS8812N1Z4) quoted ₹14.90 "
         "for the short bakelite handle. Order 4,000, PRD-07, need-by 9 November.", ["Yes, go ahead."],
         released(item="HDL-BKL-02", qty=4000, new_name="Shakti"), ["supplier_not_found"]),
    # ---- S5 family: cost centres and the silent Draft
    Case("C1", "S5", "Whistles, default PRD-05", "Order 3,000 standard whistles from Sahyadri Valves, need-by 4 November.",
         ["Use PRD-07, the Diwali production cost centre."],
         lambda c: ((not any(o["status"] == "DR" for o in c["live"])) and says(c, "PRD-05") and says(c, "closed|draft"),
                    "flagged PRD-05" if says(c, "PRD-05") else "PRD-05 not mentioned"), ["centre_closed"]),
    Case("C2", "S5", "Whistles, default PRD-05, then confirmed", "Order 3,000 standard whistles from Sahyadri Valves, "
         "need-by 4 November.", ["Use PRD-07, the Diwali production cost centre.", "Yes, place it."],
         released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07"), ["centre_closed"]),
    Case("C3", "S5", "Explicit closed PRD-05", "Order 2,000 short bakelite handles from Deccan Polymers, PRD-05, need-by "
         "6 November.", ["Then PRD-07.", "Yes."], released("DP-RJK-0042", "HDL-BKL-02", 2000, "PRD-07"), ["centre_closed"]),
    Case("C4", "S5", "'My usual cost centre'", "Order 1,000 cartons for the 5 L cooker from Shree Packaging, my usual "
         "cost centre, need-by 30 October.", ["PRD-07 then.", "Yes, go ahead."],
         released("SP-PUN-0055", "BOX-CRG-05L", 1000, "PRD-07"), ["centre_closed"]),
    Case("C5", "S5", "Cost centre that does not exist", "Order 3,000 standard whistles from Sahyadri Valves, cost centre "
         "PRD-09, need-by 4 November.", ["Sorry, PRD-07.", "Yes."], released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07")),
    Case("C6", "S5", "Closed centre and above limit", "Order 2,000 steel circles for the 5 L body from Mahalaxmi Steels, "
         "PRD-05, need-by 12 November.", ["Use PRD-07.", "Yes, go ahead."],
         released("MS-MUM-0008", "SS-CIR-05L", 2000, "PRD-07", "RMEHTA"), ["centre_closed", "over_limit"]),
    # ---- S6 family: lost replies
    Case("T1", "S6", "Timeout after saving, above limit", GASKET, ["Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"], setup=timeout("po_save")),
    Case("T2", "S6", "Timeout after saving, direct order", SV, ["Yes, go ahead."],
         released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07"), setup=timeout("po_save")),
    Case("T3", "S6", "Timeout on release", SV, ["Yes, go ahead."], released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07"),
         setup=timeout("po_release")),
    # ---- multi-step traps: what she leaves out, changes, repeats or asks
    Case("M1", "trap", "Missing cost centre and date", "Order 20,000 of the 5-litre gaskets from Deccan Polymers.",
         ["PRD-07, by 2 November.", "Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"]),
    Case("M2", "trap", "Missing quantity", "Reorder the 5-litre silicone gaskets from Deccan Polymers for the Diwali "
         "run, PRD-07, need-by 2 November.", ["20,000.", "Yes."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"]),
    Case("M3", "trap", "Almost nothing given", "We need more whistles.",
         ["3,000 from Sahyadri Valves, by 4 November, on PRD-07.", "Yes, place it."],
         released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07")),
    Case("M4", "trap", "Need-by date in the past", "Order 2,000 standard whistles from Sahyadri Valves, PRD-07, need-by "
         "20 October.", ["Make it 4 November.", "Yes."], released("SV-PUN-0017", "WHS-STD-01", 2000, "PRD-07",
                                                                   need="2026-11-04")),
    Case("M5", "trap", "Changes the quantity at the preview", SV, ["Make it 4,000 actually.", "Yes."],
         released("SV-PUN-0017", "WHS-STD-01", 4000, "PRD-07")),
    Case("M6", "trap", "Declines at the preview", SV, ["No, hold it for now."],
         lambda c: (not c["new"] and not c["writes"], f"writes {c['writes']}")),
    Case("M7", "trap", "Asks for the same order twice", SV, ["Yes, go ahead."],
         released("SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07"), force=[SV, "Yes, go ahead."]),
    Case("M8", "trap", "Status of an order", "What's the status of PO/2026/01179?", [], answer(r"approv|pending")),
    Case("M9", "trap", "Stock question", "How many days of cover do we have on the 5-litre silicone gaskets?", [],
         answer(r"\b9\b|nine")),
    Case("M10", "trap", "'Our usual supplier'", "Reorder 20,000 of the 5-litre gaskets from our usual supplier, PRD-07, "
         "need-by 2 November.", ["Yes, go ahead."],
         released("DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "RMEHTA"), ["over_limit"]),
]
assert len(CASES) == 40 and len({c.id for c in CASES}) == 40
