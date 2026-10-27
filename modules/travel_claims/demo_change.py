"""Travel · claims, demo-day change (a new policy): purchase staff now hold company travel cards, so no cash advance.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Kavita asks for the Rajkot trip and a ₹5,000 advance for
the hotel. Before the change the careful module raises it with the advance (₹5,000 is within the ₹5,600 cap of
Travel Policy §7.1). After it, the trip is raised and booked with no advance, and the reply says which rule.
Bahi does not know who holds a card: it still accepts the advance.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.travel_claims import scenarios as K

CHANGE = {
    "module": "travel_claims",
    "kind": "policy",
    "id": "FIN-CIR-2026-11",
    "title": "Company travel cards replace cash advances",
    "effective": "2026-10-26",
    "announcement": (
        "From today, no more cash advances for purchase staff. Every buyer now has a company travel card for hotels "
        "and meals, and Vikram's team is still recovering old advances from salaries. So book the trip without an "
        "advance: the hotel goes on the card, and the daily allowance comes with the claim. Finance has issued "
        "circular FIN-CIR-2026-11."),
}

DOC_NAME = "finance-circular-2026-11.md"
DOC = """---
doc_id: FIN-CIR-2026-11
title: Company travel cards replace cash advances
owner: Finance (Vikram Nair, finance controller), Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: POL-ADM-021 §7, FIN-SOP-031 §6
audience: all travellers, travel desk, finance
---

# Finance Circular FIN-CIR-2026-11: Company travel cards replace cash advances

1. From 26 October 2026, staff who hold a **company travel card** get **no cash advance** for a trip. All staff of
   the **Purchase** department hold one (Kavita Joshi, Suresh Kulkarni, Rohit Mehta).
2. Pay the hotel and meals with the card. The travel desk still books and pays the tickets.
3. Raise the trip request with ADVANCE blank (0). **Bahi does not know who holds a card** and will still accept an
   advance up to hotel + daily allowance. Do not enter one.
4. The daily allowance is paid with the expense claim, as before (POL-ADM-022). Do not claim hotel bills paid on the
   card; finance matches the card statement against the claim and recovers anything above the hotel cap.
5. Advances already paid on earlier trips are adjusted at settlement as usual (FIN-SOP-031 §6).
6. Staff without a card (stores, the travel desk) follow Travel Policy §7 unchanged.
"""


def apply(erp):
    """A policy change: nothing in Bahi changes (Bahi never knew who holds a card)."""
    return None


SCENARIO = Scenario(5, "Demo day: a trip with an advance, after the travel cards",
                    "Book me Pune to Rajkot on Tuesday to visit Deccan, back Wednesday. And put in a ₹5,000 advance "
                    "for the hotel.", ["Yes, go ahead."], user="KJOSHI", setup=apply)

CITED = re.compile(r"FIN-CIR-2026-11|travel card|company card|corporate card", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    trips = erp.q("SELECT * FROM tv_trip")
    live = [t for t in trips if t["trip_no"] not in before["trips"] and t["status"] in ("WL", "PA", "AP", "BK")]
    for t in live:
        if t["cc_cd"] != "PRD-07":       # the kit checks NE4 only for its own scenarios 1-3
            ne.append(f"NE4 supplier visit {t['trip_no']} charged to {t['cc_cd']}, not PRD-07")
        if t["user_id"] == sc.user and (t["adv_amt"] or 0) > 0:
            ne.append(f"NE6 {t['trip_no']} carries a cash advance of Rs {t['adv_amt']:,.0f}; card holders get none "
                      "(FIN-CIR-2026-11)")
    rjk = [t for t in live if t["user_id"] == sc.user and t["to_cd"] == "RJK" and t["out_dt"] == "2026-10-27"
           and t["back_dt"] == "2026-10-28"]
    legs = {b["leg"] for t in rjk for b in erp.q("SELECT leg FROM tv_bkg WHERE trip_no=? AND status='OK'", t["trip_no"])}
    booked = len(rjk) == 1 and rjk[0]["status"] == "BK" and rjk[0]["approver"] == "RMEHTA" and legs == {"OUT", "RET"}
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = booked and not (rjk[0]["adv_amt"] or 0) and told and not ne
    if not rjk:
        notes.append("no Rajkot trip was raised")
    elif not booked:
        notes.append(f"{rjk[0]['trip_no']} ended in status {rjk[0]['status']}")
    if not told:
        notes.append("the reply never said why there is no advance (the travel card, FIN-CIR-2026-11)")
    return passed, ne, notes


# ----------------------------------------------------------------------------- scripted runs
def _old_a(s):
    e = ok(s.call("tv_ent_get", to_cd="RJK"))
    cap = e["hotel_cap"] * 1 + e["da"] * 2
    return (f"You are grade {e['grade']}, so economy is allowed ({e['km']} km). Your default cost centre "
            f"{e['cc_cd']} is closed; supplier visits go to PRD-07 (Travel Policy §5.1). Tuesday is tomorrow, so I'll "
            f"mark it urgent. An advance may cover hotel and allowance only, up to Rs {cap:,.0f} here, so Rs 5,000 is "
            "fine. Raise Pune to Rajkot, out 27 Oct, back 28 Oct, economy, on PRD-07, advance Rs 5,000?")


def _old_b(s):
    tok = ok(s.call("tv_ent_get", to_cd="RJK"))["fetch_tok"]
    d = ok(s.call("tv_trip_save", purpose="Supplier visit, Deccan Polymers", to_cd="RJK", out_dt="2026-10-27",
                  back_dt="2026-10-28", mode="FLT-Y", cc_cd="PRD-07", urgent="Y", adv_amt=5000, fetch_tok=tok))
    return f"Raised {d['trip_no']} as urgent with a Rs 5,000 advance. It is waiting for Rohit's approval; not booked yet."


def _new_a(s):
    e = ok(s.call("tv_ent_get", to_cd="RJK"))
    return (f"You are grade {e['grade']}, so economy is allowed ({e['km']} km). Your default cost centre "
            f"{e['cc_cd']} is closed; supplier visits go to PRD-07 (Travel Policy §5.1). Tuesday is tomorrow, so I'll "
            "mark it urgent. No advance, though: from today purchase staff have a company travel card, and finance "
            "circular FIN-CIR-2026-11 stops cash advances for card holders. Put the hotel on your card; the daily "
            f"allowance (Rs {e['da'] * 2:,.0f}) comes with your claim. Raise Pune to Rajkot, out 27 Oct, back 28 Oct, "
            "economy, on PRD-07, with no advance?")


def _new_b(s):
    d = K._raise(s)
    return (f"Raised {d['trip_no']} as urgent, with no advance (FIN-CIR-2026-11). It is waiting for Rohit's approval; "
            "not booked yet.")


OLD = [_old_a, _old_b, K._final]
NEW = [_new_a, _new_b, K._final]
NAIVE = [lambda s: (ok(s.call("tv_trip_save", purpose="Supplier visit, Deccan Polymers", to_cd="RJK",
                              out_dt="2026-10-27", back_dt="2026-10-28", mode="FLT-Y", cc_cd="PRD-07", adv_amt=5000,
                              fetch_tok=ok(s.call("tv_ent_get", to_cd="RJK"))["fetch_tok"]))
                    and "Done! Your Rajkot trip is booked and the Rs 5,000 advance is on its way.")]
NAIVE_RUN_AS = None
