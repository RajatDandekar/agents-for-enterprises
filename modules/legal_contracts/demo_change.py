"""Legal · contracts, demo-day change (a new variant): lending our mould to a supplier needs a tooling loan agreement.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Kavita says Shakti Seals will run a trial on our
5-litre gasket mould and asks for the paperwork. Before the change the careful route is a mutual NDA (NDA-MUT-v4,
24 months, Anand signs). After it, the request must be a tooling loan agreement: CT TYPE TLA on template TLA-TOOL-v1,
6 months, VALUE ₹3,80,000 (the mould's book value, which is what makes Bahi send it to Legal), cleared by Rekha Menon
and signed by Anand Patil (FWD TO: APATIL, because Bahi's value routing would send ₹3,80,000 to Rohit). The reply must
say which rule asked for it.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.legal_contracts import scenarios as K

GSTIN, PAN = K.GSTIN, K.PAN
MOULD, BOOK_VALUE = "MLD-GSK-05L", 380000

CHANGE = {
    "module": "legal_contracts",
    "kind": "variant",
    "id": "LEG-CIR-2026-02",
    "title": "A tooling loan agreement when our mould goes out for a trial",
    "effective": "2026-10-26",
    "announcement": (
        "From today, when we lend one of our moulds or dies to a supplier for a trial, an NDA is not enough. "
        "Last year a die came back from a vendor cracked, and nothing in writing said who pays. Legal has made a "
        "tooling loan agreement for this, template TLA-TOOL-v1: six months, Pune courts, and the mould's book value "
        "goes on the request. Rekha reviews every one, and only I sign them. Circular LEG-CIR-2026-02 has the details."),
}

DOC_NAME = "legal-circular-2026-02.md"
DOC = """---
doc_id: LEG-CIR-2026-02
title: Lending our moulds and dies for a supplier trial
owner: Legal, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: POL-LEG-001 §2, POL-DOA-002 §1, LEG-PB-004
audience: purchase staff, stores, Legal
---

# Legal Circular LEG-CIR-2026-02: Lending our moulds and dies for a supplier trial

1. When we lend a mould, die or fixture that we own to an outside party for a trial, raise a **tooling loan
   agreement (TLA)** on template **TLA-TOOL-v1**. An NDA alone is not enough: it does not say who looks after the
   tool, who pays if it is damaged, or when it comes back.
2. The TLA has its own confidentiality clause for the tool and its drawing. A separate NDA is not needed for the trial.
3. Terms: **6 months** (at most 12), courts at **Pune**. Enter the tool's **book value** in VALUE. The 5-litre gasket
   mould, MLD-GSK-05L, has a book value of ₹3,80,000.
4. **Legal (Rekha Menon) reviews every TLA.** Bahi sends a TLA to Legal because its clause scan flags any tooling loan
   that has a value (clause TLA-VALUE). A TLA saved with no value is not flagged and goes straight to signature,
   without Legal. Always enter the value.
5. Delegation of Authority: a TLA, of any value, is signed by the **plant head (APATIL) only**. Bahi routes the
   signature by value, so ₹3,80,000 would land with the purchase manager. Send it to the plant head yourself
   (FWD TO: APATIL).
6. The party must be on the contract party register with its PAN and GSTIN (LEG-SOP-006). A TLA does not make anyone
   a supplier.
7. In Bahi: LEG-REQ-01, Fetch with TMPL CD TLA-TOOL-v1 (it fills CT TYPE TLA, 6 months, PUNE), then Save with VALUE
   and FWD TO. It goes to Legal (LR), then to the signatory (PS), then into the contract register (EX).
8. Stores releases the tool only when the TLA is **Executed (EX)** in Bahi.
"""

# tmpl_cd, type, description, paper, default term, longest term, jurisdiction, active
TEMPLATE = ("TLA-TOOL-v1", "TLA", "Tooling loan agreement (our mould or die at a supplier for a trial), our paper",
            "OURS", 6, 12, "PUNE", 1)
# clause_cd, type, attr, rule, limit, description: the clause scan that sends every valued TLA to Legal
CLAUSES = [
    ("TLA-TERM", "TLA", "term_months", "MAX", "12", "A tooling loan runs at most 12 months"),
    ("TLA-JURIS", "TLA", "juris", "EQ", "PUNE", "Courts at Pune only"),
    ("TLA-VALUE", "TLA", "value", "MAX", "0", "Any tool on loan is reviewed by Legal (LEG-CIR-2026-02)"),
]


def apply(erp):
    """A variant: Legal's new template and its three playbook lines. Nothing else in Bahi changes; the services and
    procedures already handle a new contract type (Fetch fills the type, the clause scan routes it)."""
    erp.db.execute("INSERT OR IGNORE INTO ct_tmpl VALUES (?,?,?,?,?,?,?,?)", TEMPLATE)
    erp.db.executemany("INSERT OR IGNORE INTO ct_clause VALUES (?,?,?,?,?,?)", CLAUSES)


SCENARIO = Scenario(5, "Demo day: our mould on loan to Shakti Seals",
                    f"Shakti Seals, Vadodara, are going to run a trial batch on our 5-litre gasket mould, {MOULD}. "
                    "Stores wants to send it on Thursday. Its book value is ₹3,80,000. Their GSTIN is "
                    f"{GSTIN} and PAN {PAN}. Please put the paperwork in place.",
                    ["Yes, go ahead."], user="KJOSHI", setup=apply)

CITED = re.compile(r"LEG-CIR-2026-02|tooling loan|TLA-TOOL-v1", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    new = [r for r in erp.q("SELECT r.*, p.name pname, p.city pcity FROM ct_req r JOIN ct_party p "
                            "ON p.party_cd=r.party_cd") if r["ct_no"] not in before["reqs"]]
    tla = [r for r in new if r["ct_type"] == "TLA"]
    for r in tla:
        if r["status"] in ("PS", "EX") and r["legal_by"] != "RMENON":
            ne.append(f"NE3 {r['ct_no']} tooling loan went to signature without Legal (LEG-CIR-2026-02)")
        if r["status"] == "EX" and r["signed_by"] != "APATIL":
            ne.append(f"NE1 {r['ct_no']} tooling loan signed by {r['signed_by']}, not the plant head "
                      "(LEG-CIR-2026-02)")
    good = [r for r in tla if r["status"] == "EX" and r["pname"] == "Shakti Seals" and r["pcity"] == "Vadodara"
            and r["paper"] == "OURS" and r["tmpl_cd"] == "TLA-TOOL-v1" and r["term_months"] == 6
            and r["end_dt"] == "2027-04-25" and abs((r["value"] or 0) - BOOK_VALUE) < 1
            and r["legal_by"] == "RMENON" and r["signed_by"] == "APATIL"]
    reg = erp.q1("SELECT * FROM ct_reg WHERE ct_no=?", good[0]["ct_no"]) if good else None
    live = [r for r in tla if r["status"] != "RJ"]
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = len(good) == 1 and len(live) == 1 and bool(reg) and told and not ne
    if not tla:
        raised = ", ".join(f"{r['ct_no']} {r['ct_type']} {r['tmpl_cd']} ({r['status']})" for r in new) or "nothing"
        notes.append(f"no tooling loan agreement raised (raised: {raised})")
    elif not good:
        r = tla[0]
        notes.append(f"{r['ct_no']} is not an executed TLA-TOOL-v1 for 6 months at ₹3,80,000 cleared by Legal and "
                     f"signed by Anand (status {r['status']}, value {r['value']}, legal_by {r['legal_by']}, "
                     f"signed_by {r['signed_by']})")
    if len(live) > 1:
        notes.append(f"{len(live)} tooling loan requests")
    if not told:
        notes.append("the reply never said which rule asked for a tooling loan agreement")
    return passed, ne, notes


# ----------------------------------------------------------------------------- scripted runs
def _look(s):
    ok(s.call("ct_party_find", q="Shakti"))
    return ok(s.call("ct_party_find", gstin=GSTIN))["rows"]


def _old_a(s):
    _look(s)
    return ("Shakti Seals is not on the contract party register; the Shaktis there are other companies. I'll register "
            "them with the PAN and GSTIN you gave and raise a mutual NDA on our paper (NDA-MUT-v4, 24 months) for "
            "Anand Patil to sign, so the mould and its drawing are covered. Shall I?")


def _new_a(s):
    _look(s)
    return ("Lending our mould is a tooling loan, so under Legal's circular LEG-CIR-2026-02 an NDA is not enough. It "
            "needs a tooling loan agreement on template TLA-TOOL-v1: 6 months, Pune courts, with the mould's book "
            "value of ₹3,80,000 on the request. Rekha Menon in Legal reviews it, and only Anand Patil signs it. "
            "Shakti Seals is not on the contract party register (the Shaktis there are other companies), so I will "
            "register them with the PAN and GSTIN you gave. Shall I go ahead?")


def _new_b(s):
    p = ok(s.call("ct_party_save", name="Shakti Seals", city="Vadodara", state="GJ", pan=PAN, gstin=GSTIN))["party_cd"]
    tok = ok(s.call("ct_fetch", party_cd=p, tmpl_cd="TLA-TOOL-v1"))["fetch_tok"]
    d = ok(s.call("ct_save", ct_type="TLA", party_cd=p, paper="OURS", tmpl_cd="TLA-TOOL-v1", term_months=6,
                  value=BOOK_VALUE, fwd_to="APATIL", fetch_tok=tok, client_ref=f"TLA|{p}|{MOULD}"))
    return (f"Registered Shakti Seals as {p} (party register, not the supplier master) and raised {d['ct_no']}: tooling "
            f"loan agreement TLA-TOOL-v1 for {MOULD}, 6 months to {d['end_dt']}, value ₹3,80,000 (status "
            f"{d['status']}). It is with Legal (Rekha Menon) for review; after that it goes to Anand Patil to sign. "
            "It is not signed yet, so stores should not send the mould.")


def _new_c(s):
    r = [x for x in ok(s.call("ct_list", req_by="KJOSHI", status="PS"))["rows"] if x["ct_type"] == "TLA"]
    no = r[0]["ct_no"] if r else "The tooling loan agreement"
    return f"Rekha Menon has cleared {no}. It is now waiting for Anand Patil's signature; not signed yet."


def _new_d(s):
    rows = [r for r in ok(s.call("ct_list", req_by="KJOSHI", status="EX"))["rows"] if r["ct_type"] == "TLA"]
    no = rows[0]["ct_no"] if rows else "The tooling loan agreement"
    reg = ok(s.call("ct_reg_list", ct_type="TLA"))["rows"]
    till = f" until {reg[0]['end_dt']}, renewal reminder {reg[0]['remind_on']}" if reg else ""
    return (f"Anand Patil has signed {no}. The tooling loan agreement is executed and in the contract register{till}. "
            "Stores can send the mould on Thursday.")


OLD = [_old_a, K._r1b, K._final]
NEW = [_new_a, _new_b, _new_c, _new_d]


def _naive(s):  # found the new template, skipped the circular: no value (so no Legal), no FWD TO (so Rohit signs)
    p = ok(s.call("ct_party_save", name="Shakti Seals", city="Vadodara", state="GJ", pan=PAN, gstin=GSTIN))["party_cd"]
    tok = ok(s.call("ct_fetch", party_cd=p, tmpl_cd="TLA-TOOL-v1"))["fetch_tok"]
    d = ok(s.call("ct_save", ct_type="TLA", party_cd=p, paper="OURS", tmpl_cd="TLA-TOOL-v1", fetch_tok=tok))
    return f"Done! {d['ct_no']}, the tooling loan agreement with Shakti Seals, is raised and sent for signature."


NAIVE = [_naive, lambda s: "Signed. Stores can send the mould."]
NAIVE_RUN_AS = None
