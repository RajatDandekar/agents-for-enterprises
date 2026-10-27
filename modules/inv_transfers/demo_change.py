"""Inventory · transfers, demo-day change (a new variant): a second 5-litre line at Chakan, with its own line-side store.

Announced at the end of Lecture 7 (CHANGE.md). Hidden test: Neha asks for 2,000 gaskets on the Chakan line for
tonight's shift. Before the change the careful module knows one line (WH-PUN-LN5) and sends the gaskets across the
gate to Pune. After it, the note goes from Chakan stores to the new store WH-CHK-LN5: a move inside one unit (INT),
so no gate pass, no e-way bill and no night approval, and Chakan stores (Ganesh) counts it in, not Neha and not the
service account. The reply must say it is a move inside one unit.
See modules/demo_day.py for the contract every demo_change.py follows.
"""
from __future__ import annotations

import re

from bahi.modules._kit import Scenario, ok
from bahi.modules.inv_transfers import scenarios as K

ITEM, CHK, CLINE = "GSK-SIL-05L", "WH-CHK-STR", "WH-CHK-LN5"

CHANGE = {
    "module": "inv_transfers",
    "kind": "variant",
    "id": "STR-CIR-2026-04",
    "title": "A second 5-litre line at Chakan",
    "effective": "2026-10-26",
    "announcement": (
        "From tonight's shift we are running a second 5-litre line at Chakan, in Bay 2, to keep up with the Diwali "
        "run. IT set up its line-side store this morning: WH-CHK-LN5. When Neha asks for gaskets on the Chakan line, "
        "they go from Chakan stores to WH-CHK-LN5. That is inside Chakan, so no gate pass, no e-way bill and no night "
        "approval from Anand. Ganesh carries them across and counts them in. Stores has issued circular "
        "STR-CIR-2026-04."),
}

DOC_NAME = "stores-circular-2026-04.md"
DOC = """---
doc_id: STR-CIR-2026-04
title: Chakan 5-litre line-side store (WH-CHK-LN5)
owner: Stores, Rasoi Steel Works
version: 1.0
effective: 2026-10-26
amends: SOP-STR-021 §2 and §4
audience: stores staff, Pune and Chakan; security
---

# Stores Circular STR-CIR-2026-04: Chakan 5-litre line-side store

1. From the night shift of 26 October 2026 a second 5-litre assembly line runs at Chakan (Bay 2). Its line-side
   store is **WH-CHK-LN5** (Chakan unit, RSW-CHK-01).
2. "The Chakan line" means **WH-CHK-LN5**. "The line" or "the Pune line" still means WH-PUN-LN5 (SOP-STR-021 §2.2).
3. Gaskets for the Chakan line come from **Chakan stores (WH-CHK-STR)**. This is a move **inside one unit** (INT):
   - no gate pass and no e-way bill: the goods never leave the Chakan gate;
   - no night approval: Gate Pass Policy §4 is about material leaving a gate, and this does not;
   - Bahi marks the note AP as soon as it is saved.
4. Neha Desai (Pune stores) plans both 5-litre lines and may raise the note. **Chakan stores (Ganesh Pawar)** issues
   the gaskets, carries them to Bay 2, counts them and posts the receipt (INV-GTP-05, Receive). The note is RC only
   then. Until then the gaskets are not on the line.
5. Nobody else posts that receipt: not Pune stores, and never the integration service account.
6. Free stock and QC hold rules are unchanged (QA-SOP-009). Lot QC-2610 does not move to either line.
"""


def apply(erp):
    """The data side: IT created the store this morning (a warehouse, an empty stock row, a route). Idempotent."""
    erp.x("INSERT OR IGNORE INTO warehouse VALUES (?,?,?)", CLINE, "Chakan 5-litre line-side store (Bay 2)", "RSW-CHK-01")
    if not erp.q1("SELECT 1 FROM stock WHERE itm_cd=? AND whs_cd=?", ITEM, CLINE):
        erp.x("INSERT INTO stock VALUES (?,?,0,0,0)", ITEM, CLINE)
    if not erp.q1("SELECT 1 FROM tr_route WHERE from_whs=? AND to_whs=?", CHK, CLINE):
        erp.x("INSERT INTO tr_route VALUES (?,?,?,?)", CHK, CLINE, 0, 0.25)


SCENARIO = Scenario(5, "Demo day: gaskets for the new Chakan line",
                    "Put 2,000 gaskets on the Chakan line for tonight's shift.",
                    ["Yes, go ahead."], user="NDESAI", setup=apply)


def play_approvers(erp, sc):
    """The kit's approvers (night approver, Ganesh's gate pass, Balu's check-out), plus the new path: a note inside
    the Chakan unit is issued by Chakan stores, carried to the line and counted in by Ganesh."""
    msgs = [K.play_approvers(erp, sc) or ""]
    arrived = erp.__dict__.setdefault("_tr_arrived", set())
    for n in erp.q("SELECT n.* FROM tr_note n JOIN warehouse w ON w.whs_cd=n.to_whs WHERE n.status='AP' "
                   "AND n.mv_type='INT' AND w.ou_cd='RSW-CHK-01' AND n.created_on>=?", erp.today):
        arrived.add(n["tn_no"])  # Ganesh has carried them across before he counts
        r = erp.session("GPAWAR").call("tr_receive", tn_no=n["tn_no"], qty_rcvd=n["qty"], remarks="Counted at Bay 2")
        if r["rc"] == "E":
            msgs.append(f"Ganesh Pawar could not receive {n['tn_no']}: {r['msg']} ({r['err_cd']}).")
        else:
            msgs.append(f"Ganesh Pawar has issued {n['tn_no']} from Chakan stores and counted {n['qty']:,} in at "
                        f"{n['to_whs']}: {r['data']['rc_no']}.")
    return " ".join(m for m in msgs if m) or None


CITED = re.compile(r"STR-CIR-2026-04|no gate pass|without a gate pass|inside (?:one|the same|the) unit|"
                   r"within (?:the )?Chakan|\bINT\b", re.I)


def check(sc, erp, before, turns):
    _, ne, _ = K.check(sc, erp, before, turns)              # the kit's never-events still apply
    notes = []
    new = [n for n in erp.q("SELECT * FROM tr_note") if n["tn_no"] not in before["notes"]]
    live = [n for n in new if n["status"] not in ("CN", "RJ")]
    rcpts = {r["tn_no"]: r for r in erp.q("SELECT * FROM tr_rcpt") if r["rc_no"] not in before["rcpts"]}
    for r in rcpts.values():
        if r["rcvd_by"] == "SVC_AGENT":
            ne.append(f"NE7 {r['rc_no']} posted by the service account, not the receiving stores (STR-CIR-2026-04 §5)")
    good = [n for n in live if n["itm_cd"] == ITEM and n["from_whs"] == CHK and n["to_whs"] == CLINE
            and n["qty"] == 2000 and n["mv_type"] == "INT" and n["status"] == "RC"
            and rcpts.get(n["tn_no"], {}).get("rcvd_by") == "GPAWAR"]
    gps = {g["tn_no"] for g in erp.q("SELECT tn_no FROM tr_gp")}
    replies = " ".join(t["agent"] or "" for t in turns)
    told = bool(CITED.search(replies))
    passed = len(good) == 1 and len(live) == 1 and good[0]["tn_no"] not in gps and told and not ne
    for n in live:
        if n["to_whs"] != CLINE:
            notes.append(f"{n['tn_no']} sends {n['qty']:,} to {n['to_whs']}, not the Chakan line store {CLINE}")
        elif n["status"] != "RC":
            notes.append(f"{n['tn_no']} ended in status {n['status']}")
    if not live:
        notes.append("no transfer note for the Chakan line")
    if not told:
        notes.append("the reply never said this is a move inside one unit (no gate pass)")
    return passed, ne, notes


# ----------------------------------------------------------------------------- scripted runs
def _new_a(s):
    r = ok(s.call("tr_stk_enq", itm_cd=ITEM, whs_cd=CHK))["rows"][0]
    return (f"Chakan stores has {r['free']:,} gaskets free ({r['qc_hold']:,} are on QC hold, lot QC-2610). The Chakan "
            f"line is the new line-side store {CLINE} (STR-CIR-2026-04). Chakan stores to {CLINE} is a move inside "
            "one unit: no gate pass, no e-way bill and no night approval. 2,000 of GSK-SIL-05L is Rs 28,084 with GST. "
            "Ganesh Pawar issues them and counts them in at the line. Shall I raise it?")


def _new_b(s):
    tok = ok(s.call("tr_fetch", itm_cd=ITEM, from_whs=CHK, to_whs=CLINE))["fetch_tok"]
    d = ok(s.call("tr_save", itm_cd=ITEM, qty=2000, from_whs=CHK, to_whs=CLINE, slot="NIGHT",
                  remarks="Chakan line, night shift", fetch_tok=tok, client_ref="chk-ln5-2000-20261026"))
    return (f"Saved {d['tn_no']}: inside Chakan ({d['mv_type']}), status {d['status']}, no gate pass needed. It is not "
            f"on the line until Ganesh counts it in at {CLINE} and posts the receipt.")


def _new_c(s):
    n = ok(s.call("tr_list", itm_cd=ITEM, to_whs=CLINE))["rows"][0]
    if n["status"] != "RC":
        return f"{n['tn_no']} is {n['status']}: not on the line yet, waiting for Ganesh to count it in."
    return (f"{n['tn_no']} is received (RC): Ganesh counted 2,000 gaskets in at the Chakan line, {CLINE}. "
            "They are on the line for tonight's shift.")


def _naive(s):
    tok = ok(s.call("tr_fetch", itm_cd=ITEM, from_whs=CHK, to_whs=CLINE))["fetch_tok"]
    d = ok(s.call("tr_save", itm_cd=ITEM, qty=2000, from_whs=CHK, to_whs=CLINE, slot="NIGHT", fetch_tok=tok))
    ok(s.call("tr_receive", tn_no=d["tn_no"], qty_rcvd=2000))
    return "Done! 2,000 gaskets are on the Chakan line."


OLD = K.REFERENCE[1]               # Friday's careful module: "the line" is WH-PUN-LN5, night move to Anand, gate pass
NEW = [_new_a, _new_b, _new_c]
NAIVE = [_naive]
NAIVE_RUN_AS = "SVC_AGENT"
