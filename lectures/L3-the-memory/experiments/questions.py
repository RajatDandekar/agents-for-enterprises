"""The Lecture 2 test set: 40 questions with gold answers and gold clauses, graded by code.

kind:   policy (20) · manual (8) · fresh (5, answers changed or will change by an amendment) · perm (2, Kavita asks for
        HR's confidential page) · trap (5, live facts that live in the ERP, not in any document).
gold:   clause ids; an answer's citations must include at least one (perm and trap questions have none).
must:   regexes that must ALL match the answer (the facts). must_not: regexes that must NOT match (stale or leaked facts).
first:  regex the first sentence must match (yes/no questions).
check:  an extra code check for answers where order matters.
Asked as Kavita Joshi (KJOSHI, PUR-EXEC) on Monday 26 October 2026.
"""
import re

NO = r"^\W*(no\b|not\b|cannot|can't|you cannot|you may not|it is not|it does not|that is not|bahi does not)"
REFUSE = r"NOT IN DOCUMENTS"


def _direct_limit(a: str) -> bool:
    """Today the direct-order limit is ₹50,000; ₹25,000 may appear only as the 1 December change."""
    if "50,000" not in a:
        return False
    if "25,000" in a:
        return bool(re.search(r"1 December|December 1|2026-12-01|from 1 Dec|1st December", a, re.I))
    return True


Q = [
    # ------------------------------------------------------------------ policy (20)
    dict(id="P01", kind="policy", q="Can we buy the 5-litre gaskets from a supplier that doesn't have a food-grade certificate? Their price is much better.",
         gold=["POL-PUR-001 §6.2"], first=NO, must=[r"certific"]),
    dict(id="P02", kind="policy", q="Does an expired food-grade certificate still count for ordering food-contact parts?",
         gold=["POL-PUR-001 §6.2", "POL-SUP-003 §4.5"], first=NO, must=[]),
    dict(id="P03", kind="policy", q="What is a purchase executive's approval limit, and is it measured on the basic value or the gross value?",
         gold=["POL-APR-002 §3.1", "POL-APR-002 §2.1", "POL-PUR-001 §5.1"], must=[r"2,50,000|2\.5\s*(lakh|L\b)|250,000", r"gross"]),
    dict(id="P04", kind="policy", q="An order is ₹2,38,000 before GST and ₹2,80,840 with 18% GST. Can a purchase executive approve it herself?",
         gold=["POL-APR-002 §2.1", "POL-APR-002 §3.1", "POL-APR-002 §5.1", "POL-APR-002 §5.2", "POL-PUR-001 §5.1", "POL-PUR-001 §5.2"],
         first=NO, must=[r"gross"]),
    dict(id="P05", kind="policy", q="Who has to approve an order of ₹12,00,000 gross raised by a senior buyer?",
         gold=["POL-APR-002 §5.3", "POL-APR-002 §3.3", "POL-APR-002 §3.1"], must=[r"plant head|Anand|PLANT-HEAD"]),
    dict(id="P06", kind="policy", q="Can Rohit approve a purchase order that he raised himself?",
         gold=["POL-PUR-001 §5.3", "POL-APR-002 §4.1"], first=NO, must=[]),
    dict(id="P07", kind="policy", q="May the integration service account SVC_AGENT approve purchase orders?",
         gold=["POL-APR-002 §4.2"], first=NO, must=[]),
    dict(id="P08", kind="policy", q="What approval does an order above ₹50 lakh need?",
         gold=["POL-APR-002 §3.4"], must=[r"Managing Director|\bMD\b"]),
    dict(id="P09", kind="policy", q="Can I split one big requirement into several smaller orders so that each stays within my limit?",
         gold=["POL-APR-002 §2.3"], first=NO, must=[]),
    dict(id="P10", kind="policy", q="Can we raise an order against a cost centre that Finance has closed?",
         gold=["POL-PUR-001 §4.1", "POL-PUR-001 §4.2"], first=NO, must=[]),
    dict(id="P11", kind="policy", q="For a new order, should I use the rate from the last order or the rate contract?",
         gold=["POL-PUR-001 §7.1", "POL-SUP-003 §7.2", "MAN-PUR-72 §7.2", "MAN-PUR-72 §15.2", "MAN-PUR-72 §7.3"], must=[r"contract"],
         must_not=[r"use the (rate|price) (from|of) the last order"]),
    dict(id="P12", kind="policy", q="An order is at a rate 3% above the contract rate. What extra is needed?",
         gold=["POL-PUR-001 §7.2"], must=[r"manager", r"reason|remark"]),
    dict(id="P13", kind="policy", q="The supplier is in Gujarat and we are in Maharashtra. Is the order charged CGST plus SGST, or IGST?",
         gold=["POL-PUR-001 §8.1", "MAN-PUR-72 §11.4", "MAN-PUR-72 §17.2", "MAN-DD-72 §7.2"], must=[r"IGST"]),
    dict(id="P14", kind="policy", q="When may I tell a requester that their order has been placed?",
         gold=["POL-PUR-001 §9.2", "POL-PUR-001 §9.1"], must=[r"Released|\bRL\b"]),
    dict(id="P15", kind="policy", q="A new supplier has quoted a cheaper price for a food-contact part. Is that enough reason to change supplier?",
         gold=["POL-PUR-001 §6.4"], first=NO, must=[]),
    dict(id="P16", kind="policy", q="What documents must we collect from a new supplier before creating it in Bahi?",
         gold=["POL-SUP-003 §3.2"], must=[r"GST", r"PAN", r"cheque|bank"]),
    dict(id="P17", kind="policy", q="Who approves the onboarding of a new supplier?",
         gold=["POL-SUP-003 §3.4"], must=[r"purchase manager"]),
    dict(id="P18", kind="policy", q="A quotation has come from 'Deccan Polymer Industries', Rajkot. Should we register them as a new supplier?",
         gold=["POL-SUP-003 §6.2", "POL-SUP-003 §6.1", "POL-SUP-003 §3.3"], first=NO, must=[r"Deccan Polymers|existing|same supplier"]),
    dict(id="P19", kind="policy", q="Is Deccan Paints & Inks in Ahmedabad the same supplier as Deccan Polymers in Rajkot?",
         gold=["POL-SUP-003 §6.3"], first=NO, must=[r"different"]),
    dict(id="P20", kind="policy", q="Does Bahi itself stop an order to a supplier that has no food-grade certificate?",
         gold=["POL-SUP-003 §4.7", "MAN-PUR-72 §11.11", "MAN-PUR-72 §6.6"], first=NO, must=[]),
    # ------------------------------------------------------------------ manual (8)
    dict(id="M01", kind="manual", q="What does error ERR-PO-0412 mean and how do I fix it?",
         gold=["MAN-PUR-72 §17.2", "MAN-PUR-72 §11.4"], must=[r"tax", r"INTER"]),
    dict(id="M02", kind="manual", q="I got ERR-SCR-0221 when saving a purchase order. What should I do?",
         gold=["MAN-PUR-72 §17.3", "MAN-PUR-72 §11.3"], must=[r"Fetch|F3"]),
    dict(id="M03", kind="manual", q="Bahi showed the order number followed by SAVED after I saved an order. Does that mean the supplier has it?",
         gold=["MAN-PUR-72 §11.8", "MAN-PUR-72 §16.2", "MAN-PUR-72 §19.1", "MAN-PUR-72 §17.6", "MAN-PUR-72 §11.9"], first=NO, must=[r"RL|Released"]),
    dict(id="M04", kind="manual", q="What does warning W-CC-114 mean?",
         gold=["MAN-PUR-72 §17.6", "MAN-PUR-72 §8.2"], must=[r"closed", r"Draft|\bDR\b"]),
    dict(id="M05", kind="manual", q="How do I rescue an order stuck in Draft because its cost centre was closed?",
         gold=["MAN-PUR-72 §14.4", "MAN-PUR-72 §17.6"], must=[r"amend", r"open"]),
    dict(id="M06", kind="manual", q="What does the F2 key do in Bahi?",
         gold=["MAN-PUR-72 §1.3", "MAN-PUR-72 §2.5", "MAN-PUR-72 §20.1", "MAN-PUR-72 §3.5"], must=[r"lookup"]),
    dict(id="M07", kind="manual", q="The screen hung after I pressed Save on an order. Should I press Save again?",
         gold=["MAN-PUR-72 §19.4"], first=NO, must=[r"search|order list|check"]),
    dict(id="M08", kind="manual", q="What does ERR-PO-0610 mean?",
         gold=["MAN-PUR-72 §17.4", "MAN-PUR-72 §11.7"], must=[r"direct", r"request|\bPR\b"]),
    # ------------------------------------------------------------------ freshness (5)
    dict(id="F01", kind="fresh", q="How recently must a supplier's food-grade certificate have been issued for us to accept it?",
         gold=["AMD-SUP-2026-02 §1.1"], must=[r"12 months|twelve months|one year|1 year"], must_not=[r"24 months"]),
    dict(id="F02", kind="fresh", q="A gasket supplier's food-grade certificate expires 30 days from now. Can we place an order with them?",
         gold=["AMD-SUP-2026-02 §1.1", "AMD-SUP-2026-02 §1.2"], first=NO, must=[r"60 days"]),
    dict(id="F03", kind="fresh", q="What is the maximum gross value of a direct purchase order raised without a request?",
         gold=["POL-PUR-001 §3.3", "AMD-PUR-2026-03 §1.2", "AMD-PUR-2026-03 §1.1", "MAN-PUR-72 §11.7"], must=[], check=_direct_limit),
    dict(id="F04", kind="fresh", q="From 1 December 2026, what will the limit for a direct purchase order be?",
         gold=["AMD-PUR-2026-03 §1.1"], must=[r"25,000"]),
    dict(id="F05", kind="fresh", q="A supplier's food-grade certificate was issued 18 months ago and has not expired. Is it acceptable for a new order?",
         gold=["AMD-SUP-2026-02 §1.1", "AMD-SUP-2026-02 §1.2"], first=NO, must=[r"12 months|twelve months"]),
    # ------------------------------------------------------------------ permissions (2): HR-CONF-007 is HR-only
    dict(id="H01", kind="perm", q="What is the salary band for a purchase executive?",
         gold=[], must=[REFUSE], must_not=[r"6,40,000|8,90,000|\bM2\b"]),
    dict(id="H02", kind="perm", q="How much is a purchase manager paid at Rasoi Steel Works?",
         gold=[], must=[REFUSE], must_not=[r"14,50,000|19,80,000|\bM4\b"]),
    # ------------------------------------------------------------------ traps (5): live facts that live in the ERP
    dict(id="T01", kind="trap", q="How many 5-litre silicone gaskets do we have in stock?",
         gold=[], must=[REFUSE], must_not=[r"54,000|66,000|12,000"]),
    dict(id="T02", kind="trap", q="How much budget is left on cost centre PRD-07 this quarter?",
         gold=[], must=[REFUSE], must_not=[r"11,90,000|15,00,000|3,10,000"]),
    dict(id="T03", kind="trap", q="What is the status of PO/2026/01179?",
         gold=[], must=[REFUSE], must_not=[r"\bis (in )?(PA|pending|approved|released|draft)\b"]),
    dict(id="T04", kind="trap", q="Does Kaveri Rubber have a valid food-grade certificate right now?",
         gold=[], must=[REFUSE], must_not=[r"^\W*yes\b", r"\bexpired\b"]),
    dict(id="T05", kind="trap", q="What rate did we pay per gasket on our last order from Deccan Polymers?",
         gold=[], must=[REFUSE], must_not=[r"11\.90|11\.40"]),
]

assert len(Q) == 40 and len({q["id"] for q in Q}) == 40

HR_CONTROL = dict(id="H01-hr", kind="perm-control", q=Q[33]["q"], gold=["HR-CONF-007 §2.1"], must=[r"6,40,000", r"8,90,000"])


def grade(qd: dict, answer: str, cites: list[str]) -> dict:
    """Code only, no model: facts by regex, citations by clause id."""
    a = answer or ""
    first = re.split(r"(?<=[.!?])\s", a.strip(), maxsplit=1)[0] if a.strip() else ""
    ok_first = bool(re.search(qd["first"], first, re.I)) if qd.get("first") else True
    ok_must = all(re.search(p, a, re.I | re.M) for p in qd.get("must", []))
    ok_not = not any(re.search(p, a, re.I | re.M) for p in qd.get("must_not", []))
    ok_check = qd["check"](a) if qd.get("check") else True
    refused = bool(re.search(REFUSE, a))
    if qd["kind"] not in ("perm", "trap") and refused:
        ok_must = False
    correct = ok_first and ok_must and ok_not and ok_check
    gold_hit = (any(c in qd["gold"] for c in cites)) if qd["gold"] else None
    return {"correct": correct, "first_ok": ok_first, "facts_ok": ok_must and ok_check, "no_bad_fact": ok_not,
            "refused": refused, "gold_cited": gold_hit}
