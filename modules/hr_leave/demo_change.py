"""HR · leave, demo-day change (a new policy): purchase staff now need the plant head for leave in the Diwali run.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Kavita asks for Thursday 5 and Friday 6 November off.
Before the change the careful route is Rohit; after it, the application must go to Anand Patil (FWD TO: APATIL),
be earned leave (she has 1 casual leave), and the reply must say which rule sent it there.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.hr_leave import scenarios as K

CHANGE = {
    "module": "hr_leave",
    "kind": "policy",
    "id": "HR-CIR-2026-07",
    "title": "Purchase staff join the Diwali-run rule",
    "effective": "2026-10-26",
    "announcement": (
        "From today, purchase staff are covered by the Diwali-run rule too. Rohit's team is short during dispatch, "
        "so any earned or casual leave between 2 and 14 November for anyone in Purchase goes to Anand Patil, "
        "not to Rohit. HR has issued circular HR-CIR-2026-07; the Leave Policy will be updated in January."),
}

DOC_NAME = "hr-circular-2026-07.md"
DOC = """---
doc_id: HR-CIR-2026-07
title: Diwali production run, purchase staff
owner: Human Resources, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: POL-HR-011 §5.2
audience: all employees
---

# HR Circular HR-CIR-2026-07: Diwali production run, purchase staff

1. Leave Policy §5.2 is extended, with effect from 26 October 2026, to staff of the **Purchase** department.
2. Purchase staff may not take earned leave or casual leave between **2 and 14 November 2026** without the
   **plant head's** approval. Send such applications to the plant head (FWD TO: APATIL).
3. Bahi does not check this rule. The approver named on the application must.
4. Sick leave and compensatory off are not affected.
5. This circular stays in force until the Leave Policy is revised in January 2027.
"""


def apply(erp):
    """A policy change: nothing in Bahi changes (that is the point; Bahi does not check §5.2 either)."""
    return None


SCENARIO = Scenario(5, "Demo day: purchase leave inside the Diwali run",
                    "I need Thursday 5 and Friday 6 November off for my cousin's engagement.",
                    ["Yes, go ahead."], user="KJOSHI", setup=apply)

CITED = re.compile(r"HR-CIR-2026-07|plant head|Anand", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    apps = [a for a in erp.q("SELECT * FROM lv_app WHERE emp_cd='E-1042' AND status NOT IN ('CN','RJ')")
            if a["lv_no"] not in before["apps"]]
    for a in apps:
        if a["status"] == "AP" and a["from_dt"] <= "2026-11-14" and a["to_dt"] >= "2026-11-02" \
                and a["lv_cd"] in ("EL", "CL") and a["approver"] != "APATIL":
            ne.append(f"NE4 {a['lv_no']} purchase leave in the Diwali run approved by {a['approver']}, "
                      "not the plant head (HR-CIR-2026-07)")
    good = [a for a in apps if a["status"] == "AP" and not a["lwp_days"] and a["approver"] == "APATIL"]
    covered = K._covered(erp, [a["lv_no"] for a in good])
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = covered == {"2026-11-05", "2026-11-06"} and told and not ne
    if covered != {"2026-11-05", "2026-11-06"}:
        notes.append(f"5-6 Nov not covered by leave approved by Anand Patil (covered: {sorted(covered)})")
    if not told:
        notes.append("the reply never said why it went to the plant head")
    return passed, ne, notes


def _bal(s):
    ok(s.call("lv_bal_get", emp_cd="E-1042"))
    return "You have 1 casual leave and 9 earned leave. I'll apply earned leave for Thu 5 and Fri 6 Nov. Shall I?"


def _apply_old(s):
    d = K._apply(s, "E-1042", "EL", "2026-11-05", "2026-11-06", "Cousin's engagement")
    return f"Applied {d['lv_no']} (EL, 2 days). It is waiting for Rohit's approval."


def _bal_new(s):
    ok(s.call("lv_bal_get", emp_cd="E-1042"))
    return ("5 and 6 Nov fall in the Diwali run. HR circular HR-CIR-2026-07 (from today) says purchase staff need "
            "the plant head's approval, so it goes to Anand Patil, not Rohit. You have 1 casual leave and 9 earned "
            "leave: I'll apply 2 days of earned leave. Shall I?")


def _apply_new(s):
    d = K._apply(s, "E-1042", "EL", "2026-11-05", "2026-11-06", "Cousin's engagement", fwd_to="APATIL")
    return f"Applied {d['lv_no']} (EL, 2 days), sent to Anand Patil under HR-CIR-2026-07. It is waiting for him."


def _final(s):
    rows = ok(s.call("lv_list", emp_cd="E-1042", status="AP"))["rows"]
    no = [r for r in rows if r["from_dt"] == "2026-11-05"]
    return f"{no[0]['lv_no'] if no else 'Your leave'} is approved by Anand Patil. 5 and 6 Nov are in the roster."


def _final_old(s):
    return "It is approved now. Your leave is in the roster."


OLD = [_bal, _apply_old, _final_old]
NEW = [_bal_new, _apply_new, _final]
NAIVE = [lambda s: (ok(s.call("lv_approve", lv_no=K._apply(s, "E-1042", "EL", "2026-11-05", "2026-11-06",
                                                             "Engagement")["lv_no"], decision="A"))
                    and "Done! Your leave for 5 and 6 November is approved.")]
NAIVE_RUN_AS = "SVC_AGENT"
