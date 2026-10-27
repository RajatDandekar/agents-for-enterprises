"""Lecture 4: the route for one purchase order, written down as data.

A process document is a flowchart, not a checklist. This file is the flowchart:

    SPINE       the seven steps every order walks, in order
    GATES       the detours, each with a named predicate over the graph's state; the default is to SKIP
    ASKS        the moments the route stops to ask Kavita something (and why)
    INVARIANTS  what must never happen, and which step makes it impossible
    BRANCHES    where each kind of message goes (an order is only one of them)

graph.py builds the LangGraph StateGraph from these lists, so the route a student reads here is the route that runs.
Lecture 6 enumerates GATES and ASKS to generate test scenarios (see gate_combinations() and TRIGGERS).

State the predicates read (all plain dicts, so they are easy to fake in a test):
    state["draft"]  supplier_name, supplier_code, supplier_city, gstin, item_text, item_code, qty, rate,
                    cost_centre, need_by, cert_ref, cert_valid_to
    state["facts"]  what the route looked up: supplier_status, supplier_cert, food_contact, cc_open, cc_closed_on,
                    gross, limit, needs_approval, missing, bad_date, previewed_key, confirmed_key, ...
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Callable

TODAY = "2026-10-26"


@dataclass(frozen=True)
class Step:
    name: str
    title: str
    does: str            # what code does at this step
    model: str           # what the model does at this step (often nothing)
    tools: tuple = ()    # intent tools (Lecture 3) this step may call


@dataclass(frozen=True)
class Gate:
    name: str
    title: str           # the detour's name on the plate
    detour: str          # node name in graph.py
    after: str           # the spine step whose result the gate reads
    rejoin: str          # where the route continues after the detour
    description: str
    policy: str          # where the rule is written down
    pred: Callable[[dict], bool] = field(compare=False)
    tools: tuple = ()


@dataclass(frozen=True)
class Ask:
    name: str
    at: str
    description: str
    pred: Callable[[dict], bool] = field(compare=False)


@dataclass(frozen=True)
class Invariant:
    name: str
    never_event: str     # NE1..NE5 in bahi/scenarios.py, or "" if it is a design rule
    description: str
    enforced_at: str


def _f(s: dict) -> dict:
    return s.get("facts") or {}


def _d(s: dict) -> dict:
    return s.get("draft") or {}


SPINE: list[Step] = [
    Step("understand", "Understand",
         "Append Kavita's message to the session; when the route asked her something, read her answer as that answer.",
         "Picks the intent (typed decision) and extracts the fields she gave (structured output). Nothing else.", ()),
    Step("route", "Route",
         "Send the message down its branch. For an order, turn the item and supplier names into Bahi codes.",
         "Only when a supplier name is a near match: a typed decision with a confidence.",
         ("find_supplier",)),
    Step("collect", "Collect",
         "Fill what is missing from the user's memory and the rate contract; list what still cannot be looked up.",
         "Writes the one question that asks for everything still missing.", ("check_cost_centre",)),
    Step("check", "Check",
         "Apply the rules that decide whether this order may exist at all (food contact needs a valid certificate).",
         "Nothing.", ()),
    Step("preview", "Preview",
         "Price the draft in Bahi without saving: tax code, gross value, request or direct, approval and approver.",
         "Writes one sentence above the preview block.", ("create_purchase_order(confirm=False)",)),
    Step("commit", "Commit",
         "Write once, with an idempotency key derived from the draft. Refuses unless this exact draft was previewed "
         "and confirmed, and re-checks the certificate in Bahi just before writing.",
         "Nothing.", ("create_purchase_order(confirm=True)", "register_supplier", "record_certificate")),
    Step("confirm", "Confirm",
         "Read the order back from Bahi. Release it if it is approved; fix or report a Draft; report the real status.",
         "Writes the words; code writes the status line from the receipt.",
         ("order_status", "release_purchase_order", "amend_purchase_order")),
]
SPINE_NAMES = [s.name for s in SPINE]


def _no_cert(s: dict) -> bool:
    f, d = _f(s), _d(s)
    if not f.get("food_contact"):
        return False
    if f.get("supplier_cert") == "valid":
        return False
    on_draft = bool(d.get("cert_ref")) and (d.get("cert_valid_to") or "") >= TODAY
    return not on_draft


GATES: list[Gate] = [
    Gate("supplier_not_found", "Onboard supplier", "onboard", after="route", rejoin="collect",
         description="Kavita named a supplier that is not in the supplier master: no active supplier matches her "
                     "words, and she did not pick one of the near matches. Collect name, city, state and GSTIN; "
                     "register only at Commit, after the preview is confirmed.",
         policy="Purchase Policy §6.3 (onboard before any order)",
         pred=lambda s: _f(s).get("supplier_status") == "new", tools=("register_supplier",)),
    Gate("centre_closed", "Fix cost centre", "fix_cost_centre", after="collect", rejoin="collect",
         description="The cost centre on the draft is closed. Bahi would save the order silently as a Draft "
                     "(W-CC-114), so ask for an open one before going on.",
         policy="Purchase Policy §4.1–4.2",
         pred=lambda s: bool(_d(s).get("cost_centre")) and _f(s).get("cc_open") is False,
         tools=("check_cost_centre", "amend_purchase_order")),
    Gate("food_contact_no_cert", "Ask for certificate", "ask_certificate", after="check", rejoin="check",
         description="The item touches food and the supplier has no valid food-grade certificate in Bahi, and Kavita "
                     "has not given one. Ask for it; without it the route stops here and nothing is written. An "
                     "expired certificate counts as none.",
         policy="Purchase Policy §6.2",
         pred=_no_cert, tools=("record_certificate",)),
    Gate("over_limit", "Approval", "approval", after="preview", rejoin="commit",
         description="The gross value including GST is above the user's own approval limit (₹2,50,000 for Kavita). "
                     "Raise the request, then wait for the approver (an interrupt) and read the approval back from "
                     "Bahi before committing the order.",
         policy="Purchase Policy §5.1–5.4",
         pred=lambda s: bool(_f(s).get("needs_approval")), tools=("create_purchase_order(confirm=True)",)),
]
GATE_BY_NAME = {g.name: g for g in GATES}

ASKS: list[Ask] = [
    Ask("unsure_intent", "understand", "The intent decision came back below the confidence threshold: ask what she wants.",
        lambda s: _f(s).get("intent_unsure", False)),
    Ask("near_match_supplier", "route", "Her supplier name is close to more than one supplier, or the decision is "
        "unsure: show the candidates and ask which one.", lambda s: _f(s).get("supplier_status") == "ask"),
    Ask("missing_fields", "collect", "A required field is still empty after memory and contracts: ask for all of "
        "them in one question.", lambda s: bool(_f(s).get("missing"))),
    Ask("past_need_by", "collect", "The need-by date is before today: ask for a new one.",
        lambda s: bool(_f(s).get("bad_date"))),
    Ask("confirm_preview", "preview", "Always: show the priced preview and ask her to confirm. Nothing is written before.",
        lambda s: True),
]

INVARIANTS: list[Invariant] = [
    Invariant("commit_needs_confirmed_preview", "NE1,NE5", "Commit refuses unless the draft's key equals the key of the "
              "preview she confirmed. There is no edge into Commit except from her confirmation or from an approval "
              "read back from Bahi.", "commit"),
    Invariant("food_contact_needs_valid_cert", "NE3", "Commit re-reads the supplier's certificates from Bahi just before "
              "writing and refuses a food-contact order without a valid one, whatever the route did before.", "commit"),
    Invariant("one_key_per_draft", "NE2", "The idempotency key is a hash of the draft (thread, supplier, item, quantity, "
              "rate, cost centre, need-by), never a random number, so a retry or a repeated request finds the first "
              "order.", "commit"),
    Invariant("no_new_supplier_if_one_matches", "NE4", "Onboard opens only when no active supplier matches; a near match "
              "is a question, not a registration.", "route"),
    Invariant("status_line_from_receipt", "NE5", "The last line of every reply about an order is written by code from "
              "the receipt Bahi returns. The model's words are checked: 'placed' or 'done' while the order is not "
              "Released is replaced.", "confirm"),
    Invariant("draft_read_back", "NE5", "After every write the order is read back; a Draft is fixed (amend the cost "
              "centre) or reported, never called done.", "confirm"),
    Invariant("acts_as_the_user", "NE1", "Every tool runs in the user's own Bahi session, with her limit and "
              "permissions. Approval is the approver's act in Bahi, never the agent's.", "graph"),
]

BRANCHES = {"order": "route", "policy_question": "answer", "order_status": "answer", "stock_question": "answer",
            "other": "answer"}
REQUIRED = ["item_code", "supplier", "qty", "cost_centre", "need_by"]

# Sandbox facts that open each gate (for Lecture 6 to build scenarios from).
TRIGGERS = {
    "supplier_not_found": ["Shakti Seals, Vadodara, GSTIN 24AAFCS8812N1Z4 (not in the master)",
                           "any supplier name with no active match"],
    "centre_closed": ["PRD-05 (closed 15 Oct 2026), also Kavita's default and usual cost centre"],
    "food_contact_no_cert": ["Shakti Seals (new, no certificate)", "Kaveri Rubber Products KR-KOL-0063 (expired 30 Sep 2026)",
                             "Deccan Paints & Inks DPI-AMD-0107 (no certificate)"],
    "over_limit": ["20,000 x GSK-SIL-05L from DP-RJK-0042 at ₹11.90 = ₹2,80,840 gross (limit ₹2,50,000)",
                   "2,000 x SS-CIR-05L from MS-MUM-0008 at ₹142 = ₹3,35,120"],
}


def open_gates(state: dict) -> list[str]:
    """The names of the gates that are open for this state."""
    return [g.name for g in GATES if g.pred(state)]


def gate_combinations() -> list[dict]:
    """Every on/off combination of the four gates (16), with the detours each would open, for scenario generation."""
    out = []
    for bits in itertools.product([False, True], repeat=len(GATES)):
        on = [g for g, b in zip(GATES, bits) if b]
        out.append({"gates": [g.name for g in on], "detours": [g.title for g in on],
                    "stops_before_commit": any(g.name == "food_contact_no_cert" for g in on)})
    return out


def describe() -> str:
    """The route as a markdown table (for the notebook and for A4)."""
    rows = ["| step | code does | model does |", "|---|---|---|"]
    rows += [f"| {s.title} | {s.does} | {s.model} |" for s in SPINE]
    rows += ["", "| gate | opens detour | read after | rejoins at | rule |", "|---|---|---|---|---|"]
    rows += [f"| `{g.name}` | {g.title} | {g.after} | {g.rejoin} | {g.policy} |" for g in GATES]
    return "\n".join(rows)
