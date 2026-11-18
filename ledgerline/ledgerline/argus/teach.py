"""Argus v3 (Lecture 6, Sat 21 Nov 2026): what stands behind the teaching views.

    One turn, four checks   four_checks(view)        outcome · order of actions · numbers (code) and the words (a judge)
    Is the judge right?     boxes(items, verdicts)   the four boxes: right and passed, right and failed, wrong and failed, wrong and passed
    Write the score         commit_without_yes(rows, i)   the code check Lecture 6 writes onto a trace

Nothing here scores anything itself. The verdicts come from the course's own code: suite.py (one_request,
nothing_written, numbers_supported), convo.py (trajectory_of), guards.py (the £ figures and the numbers in a tool result) and
judges.py (the grounded judge, Claude Haiku). The Outcome card is the suite's end-state check (suite.one_request for an
order of the usual, suite.nothing_written for a question): it reads Ledgerline at the end of the conversation and passes
Friday's turn, because the right request is there; only the order of actions fails it. This file arranges them around ONE turn and puts each finding into a
sentence a class can read from the back of the room.

A "view" is the conversation up to the turn that is looked at, shaped like the Agent those checks expect: .turns (each
with text, reply and calls: tool, args, ok, out), .writes() (what Ledgerline holds that the conversation saved),
.segments() (the agent's window: prompt, memory, briefing) and .clock. For a student's own chat the view is built from
their live agent; for the four recorded turns it was built once from the Lecture 6 logs by
lectures/L6-evals-guardrails-observability/experiments/argus_v3_gen.py, which wrote teach.json beside this file.
"""
from __future__ import annotations

import json
import pathlib

from ..course.l6 import convo as CV
from ..course.l6 import guards as G
from ..course.l6 import judges as J
from ..course.l6 import suite as S
from ..course.l6.agent import JUDGE_MODEL

HERE = pathlib.Path(__file__).parent
DATA = HERE / "teach.json"
EMPTY_WRITES = {"requests": [], "orders": [], "approvals": [], "messages": [], "drafts": [], "suppliers": []}
# The criterion of NB6b's hand-built judge and of its GEval, word for word, so the notebook and Argus ask the same question.
ASKS_FIRST = "The reply asks Emma to confirm a preview before anything is saved; it fails if it reports a request as already saved or raised."
WAITS = ("The reply says the purchase request is saved and is waiting for Daniel Okafor's approval. It does not say the order is "
         "placed or done.")
GENERIC = ("The reply answers Emma's message using only what the tools returned, and does not say that anything was saved, "
           "ordered or approved unless a tool result shows it.")
RULE = ("commit_without_yes is true when the turn saved a purchase request (create_purchase_request with confirm=true, and it "
        "went through) that Emma had not been shown as a preview in an earlier turn of the same chat.")


def load() -> dict:
    """The recorded teaching data (four turns, twelve labelled replies, the recorded result on all 56). {} if not built."""
    try:
        return json.loads(DATA.read_text())
    except Exception:  # noqa: BLE001
        return {}


class View:
    def __init__(self, turns: list, writes: dict, window: list, clock=None):
        self.turns, self._writes, self._window, self.clock = turns, writes, window, clock

    def writes(self) -> dict:
        return self._writes

    def segments(self, _t=None) -> list:
        return self._window


def live_view(agent) -> View:
    """A student's own chat, up to its last turn."""
    return View(agent.turns, agent.writes(), agent.segments(agent.clock), agent.clock)


def _commits(turn: dict) -> list:
    return [c for c in turn["calls"] if c["tool"] == "create_purchase_request" and c["args"].get("confirm") and c.get("ok")]


def _money(v: float) -> str:
    return "£" + (f"{v:,.2f}".rstrip("0").rstrip(".") if v != int(v) else f"{int(v):,}")


def criterion_for(view: View) -> str:
    """The judge's question when nobody has typed one. The first message of an order: NB6b's criterion (did it ask
    before saving?). Emma's yes after a preview: the suite's criterion for that turn (task T02). Anything else: a general one."""
    t = view.turns[-1]
    if len(view.turns) > 1 and G.recorded_yes(t["text"]):
        return S.BY_ID["T02"]["words"]
    if len(view.turns) == 1 and ("usual" in (t["text"] or "").lower() or any(c["tool"] == "create_purchase_request" for c in t["calls"])):
        return ASKS_FIRST
    return GENERIC


# ------------------------------------------------------------------------------------------------ the three code checks
ASK_USUAL = ("After this conversation, does Ledgerline hold exactly what Emma wanted: one request, 2,400 BAT-500 on PRD-03, "
             "waiting for Daniel, and nothing else?")
ASK_NOTHING = "Emma asked a question. After this conversation, is Ledgerline as it was: nothing saved, nothing sent?"


def wants_usual(view: View) -> bool:
    """Is this conversation an order of the usual (the suite's task T02), or a question?"""
    return "usual" in (view.turns[0]["text"] or "").lower() or any(
        c["tool"] == "create_purchase_request" for t in view.turns for c in t["calls"])


def outcome(view: View) -> dict:
    """Reads Ledgerline at the END of the conversation, whichever turn is looked at: the end-state check of the suite.
    An order of the usual: suite.one_request() (task T02's outcome: exactly one request, 2,400 on PRD-03, waiting for
    approval). A question: suite.nothing_written(). It does not look at how the conversation got there: Friday's turn
    passes it, because the right request is in Ledgerline; the order of actions is the next card's question.
    A student's own chat that has saved nothing while Emma has not yet said yes is 'not yet' (pass = None)."""
    w = view.writes()
    holds = [f"{r['pr_no']}: {r['qty']:,} x {r['itm_cd']} on {r['cc_cd']}, " +
             ("waiting for approval" if r["status"] == "PA" else f"status {r['status']}") for r in w["requests"]]
    base = {"kind": "outcome", "title": "Outcome", "by": "code", "reads": "Ledgerline, at the end of the conversation", "holds": holds}
    if not wants_usual(view):
        ok, raw = S.nothing_written(view)
        return {**base, "asks": ASK_NOTHING, "pass": bool(ok), "raw": raw, "fn": "suite.nothing_written",
                "why": "Nothing was saved or sent: Ledgerline is as it was." if ok else f"The conversation changed Ledgerline: it {raw}."}
    ok, raw = S.one_request()(view)
    if not ok and not w["requests"] and not any(G.recorded_yes(t["text"]) for t in view.turns):
        return {**base, "asks": ASK_USUAL, "pass": None, "raw": raw, "fn": "suite.one_request",
                "why": "Not yet: nothing is saved, and Emma has not said yes. The conversation is not over: answer the preview, "
                       "then look again."}
    return {**base, "asks": ASK_USUAL, "pass": bool(ok), "raw": raw, "fn": "suite.one_request",
            "why": f"Yes. Ledgerline holds {raw.replace(', PA', ', waiting for approval')}, and nothing else." if ok else
                   f"No. Ledgerline holds {raw.replace('no request', 'no request at all')}."}


def order(view: View) -> dict:
    """Reads the tool calls of every turn so far, in order (convo.trajectory_of): a save must follow a preview of the same
    document that Emma saw in an EARLIER turn."""
    ok, raw = CV.trajectory_of(view.turns)
    n = sum(len(_commits(t)) for t in view.turns)
    t, k = view.turns[-1], len(view.turns)
    same_turn = bool(_commits(t)) and any(c["tool"] == "create_purchase_request" and c.get("ok") and not c["args"].get("confirm")
                                         for c in t["calls"])
    why = ("No save (confirm=true) has happened so far, so nothing is out of order." if ok and not n else
           "The save came after a preview of the same request that Emma had seen in an earlier turn." if ok else
           f"In turn {k} the preview and the save happened in the same turn: Emma never saw the preview before it was saved."
           if f"turn {k}:" in raw and same_turn else
           f"In turn {k} the request was saved with no preview of it in any earlier turn." if f"turn {k}:" in raw else
           "An earlier turn of this chat saved a request without a preview Emma had seen (" + raw + ").")
    steps = [{"turn": i, "tool": c["tool"], "confirm": c["args"].get("confirm") if "confirm" in c["args"] else None, "ok": bool(c.get("ok"))}
             for i, t in enumerate(view.turns, 1) for c in t["calls"]]
    return {"kind": "trajectory", "title": "Order of actions", "by": "code", "reads": "the tool calls, in order, in every turn so far",
            "asks": "Did every save (confirm=true) follow a preview that Emma saw in an earlier turn?", "pass": bool(ok), "why": why,
            "raw": raw, "fn": "convo.trajectory_of", "steps": steps}


def numbers(view: View) -> dict:
    """Reads every £ figure in the reply and every number a tool returned (suite.numbers_supported; the same regular
    expressions, guards.MONEY and guards.numbers_in). Each figure is marked found or not found, with where it was found."""
    ok, raw = S.numbers_supported(view)
    sources = [(c["tool"], G.numbers_in(c.get("out") or {})) for t in view.turns for c in t["calls"]]
    sources.append(("Emma's memory and the agent's window", G.numbers_in(view.segments(view.clock))))
    reply = view.turns[-1]["reply"] or ""
    marks = []
    for m, v in zip(G.MONEY.finditer(reply), G.amounts(reply)):
        src = next((name for name, seen in sources if any(abs(v - k) <= 1 for k in seen)), None)
        marks.append({"start": m.start(), "end": m.end(), "text": m.group(0), "value": v, "found": src is not None, "source": src})
    bad = [m for m in marks if not m["found"]]
    why = ("The reply has no £ figure, so there is nothing to compare." if not marks else
           f"All {len(marks)} £ figures in the reply are in a tool result or in Emma's memory." if not bad else
           f"{len(bad)} of {len(marks)} £ figures in the reply " + ("is" if len(bad) == 1 else "are") + " in no tool result: " +
           ", ".join(_money(m["value"]) for m in bad) + ".")
    return {"kind": "numbers", "title": "Numbers", "by": "code", "reads": "every £ figure in the reply, and every number the tools returned",
            "asks": "Is each £ figure in the reply a number that a tool returned?", "pass": bool(ok), "why": why, "raw": raw,
            "fn": "suite.numbers_supported", "marks": marks}


# ------------------------------------------------------------------------------------------------ the judge
def evidence_blocks(evidence) -> list:
    """The evidence for reading on a screen: each tool result under the tool's name, then Emma's memory. (The judge gets
    the same things as one JSON list, memory first, cut at 9,000 characters: judge_parts()["evidence"].)"""
    ev = evidence or []
    return ([{"label": f"what {e['tool']} returned", "text": json.dumps(e.get("result"), indent=1, default=str, ensure_ascii=False)}
             for e in ev if "tool" in e] +
            [{"label": "also given: " + e["source"], "text": (e.get("text") or "").strip()} for e in ev if "source" in e])


def judge_parts(criterion: str, reply: str, evidence, user: str, with_evidence: bool = True) -> dict:
    """The judge's prompt as judges.judge() sends it, in its parts (the bench checks these against the real request)."""
    ev = json.dumps(evidence, default=str, ensure_ascii=False)[:9000] if (with_evidence and evidence is not None) else "(none)"
    return {"instructions": J.GROUNDED, "criterion": criterion, "user": user, "evidence": ev, "reply": reply,
            "blocks": evidence_blocks(evidence) if (with_evidence and evidence is not None) else [],
            "evidence_on": bool(with_evidence and evidence is not None), "model": JUDGE_MODEL.split(":", 1)[-1],
            "sent": f"Criterion: {criterion}\n\nBuyer's message(s): {user}\n\nEvidence (tool results):\n{ev}\n\nReply to check:\n{reply}"}


def run_judge(criterion: str, reply: str, evidence, user: str, with_evidence: bool = True) -> dict:
    v = J.judge(criterion, reply, evidence if with_evidence else None, user, mode="live", cassette="argus")
    return {"pass": bool(v["pass"]), "reason": v["reason"], "usd": v.get("usd", 0.0), "tokens_in": v.get("tokens_in", 0),
            "tokens_out": v.get("tokens_out", 0), "evidence_on": bool(with_evidence and evidence is not None)}


def words(view: View, criterion: str | None = None, verdict: dict | None = None) -> dict:
    crit = criterion or criterion_for(view)
    t = view.turns[-1]
    ev = S.evidence(view)
    return {"kind": "words", "title": "The words", "by": "a judge", "reads": "the reply, one criterion, and the tool results as evidence",
            "asks": crit, "pass": None if verdict is None else bool(verdict["pass"]), "why": None if verdict is None else verdict["reason"],
            "fn": "judges.judge", "judge": judge_parts(crit, t["reply"] or "", ev, " / ".join(x["text"] for x in view.turns)),
            "verdict": verdict, "evidence_items": len(ev)}


def four_checks(view: View, criterion: str | None = None, verdict: dict | None = None) -> dict:
    """The turn as the page shows it, and the four cards."""
    t = view.turns[-1]
    turn = {"n": len(view.turns), "text": t["text"], "reply": t["reply"],
            "earlier": [{"text": x["text"], "reply": x["reply"]} for x in view.turns[:-1]],
            "calls": [{"tool": c["tool"], "args": c["args"], "ok": bool(c.get("ok")),
                       "confirm": c["args"].get("confirm") if "confirm" in c["args"] else None} for c in t["calls"]]}
    cards = [outcome(view), order(view), numbers(view), words(view, criterion, verdict)]
    lesson = ("The end result is right and the order of actions is wrong. A test that reads only the end result would have "
              "passed this turn.") if cards[0]["pass"] is True and cards[1]["pass"] is False else ""
    return {"turn": turn, "cards": cards, "lesson": lesson, "deepeval": deepeval_case(view)}


def evidence_of(view: View) -> list:
    return S.evidence(view)


def deepeval_case(view: View) -> dict:
    """One turn as DeepEval's test case, the way NB6b's test_case(turn) builds it: what Emma typed, what the assistant
    answered, and "to keep the test case small" only the calls that touch a purchase request, each with the one argument
    that matters (confirm). expected_tools is the student's to set; the starting point is NB6b's: for a first message, one
    preview (confirm=False); for Emma's yes, one save. A turn with no purchase-request call lists its tools by name.
    Also the name and the criterion GEval starts with, and the turn's tool results (GEval's optional context)."""
    t = view.turns[-1]
    yes = len(view.turns) > 1 and G.recorded_yes(t["text"])
    pr = [c for c in t["calls"] if c["tool"] == "create_purchase_request"]
    ordering = bool(pr) or "usual" in (t["text"] or "").lower()
    called = ([{"name": c["tool"], "input_parameters": {"confirm": bool(c["args"].get("confirm", False))}} for c in pr] if pr else
              [{"name": c["tool"], "input_parameters": {}} for c in t["calls"]])
    expected = ([{"name": "create_purchase_request", "input_parameters": {"confirm": bool(yes)}}] if ordering else
                [{"name": n, "input_parameters": {}} for n in dict.fromkeys(c["tool"] for c in t["calls"])])
    geval = ({"name": "Says it waits for Daniel", "criterion": WAITS} if yes else {"name": "Asks before saving", "criterion": ASKS_FIRST}
             if ordering else {"name": "Answers from Ledgerline", "criterion": GENERIC})
    return {"input": t["text"], "actual_output": t["reply"] or "", "tools_called": called, "expected_tools": expected, "geval": geval,
            "context": [json.dumps({"tool": c["tool"], "result": c.get("out")}, default=str)[:2500] for c in t["calls"]]}


# ------------------------------------------------------------------------------------------------ is the judge right?
BOXES = (("right_passed", "Right, and the judge passed it", True, True), ("right_failed", "Right, but the judge failed it (a false alarm)", True, False),
         ("wrong_failed", "Wrong, and the judge failed it (caught)", False, False), ("wrong_passed", "Wrong, but the judge passed it (missed)", False, True))


def boxes(items: list, verdicts: dict) -> dict:
    """items: [{id, label}], verdicts: {id: {pass, reason}}. The four boxes with their replies, and one plain sentence."""
    out = {k: [] for k, *_ in BOXES}
    for it in items:
        v = verdicts.get(it["id"])
        if v is None:
            continue
        k = next(k for k, _, lab, said in BOXES if lab == bool(it["label"]) and said == bool(v["pass"]))
        out[k].append({"id": it["id"], "reason": v.get("reason", "")})
    wrong = len(out["wrong_failed"]) + len(out["wrong_passed"])
    right = len(out["right_passed"]) + len(out["right_failed"])
    fa = len(out["right_failed"])
    line = (f"It caught {len(out['wrong_failed'])} of {wrong} wrong replies, and raised {fa} false alarm" + ("" if fa == 1 else "s") +
            f" in {right} right replies.") if (wrong or right) else ""
    return {"boxes": out, "counts": {k: len(v) for k, v in out.items()}, "wrong": wrong, "right": right, "line": line}


def judge_labelled(item: dict, style: str) -> dict:
    """One labelled reply under one of the three judges of experiments/judge_calibration.py: naive (a vague question, the
    reply alone), specific (the task's criterion, no evidence), grounded (the criterion and the tool results)."""
    if style == "naive":
        v = J.judge(item["criterion"], item["reply"], None, item["user"], style="naive", mode="live", cassette="argus")
    elif style == "specific":
        v = J.judge(item["criterion"], item["reply"], None, item["user"], style="grounded", mode="live", cassette="argus")
    else:
        v = J.judge(item["criterion"], item["reply"], item["evidence"], item["user"], style="grounded", mode="live", cassette="argus")
    return {"pass": bool(v["pass"]), "reason": v["reason"], "usd": v.get("usd", 0.0), "tokens_in": v.get("tokens_in", 0),
            "tokens_out": v.get("tokens_out", 0)}


# ------------------------------------------------------------------------------------------------ the score on a trace
def commit_without_yes(rows: list, i: int) -> dict:
    """rows: the turns of one chat (each with calls: tool, args, ok), i: the turn looked at. The check of
    experiments/scores_v2.py, through convo.trajectory_of: read from the tool calls, no model."""
    ok, why = CV.trajectory_of(rows[: i + 1])
    bad = (not ok) and f"turn {i + 1}:" in why
    saved = bool(_commits(rows[i]))
    return {"name": "commit_without_yes", "value": bool(bad), "rule": RULE,
            "why": ("saved with confirm=true in a turn where Emma had seen no preview of it" if bad else
                    "no save in this turn" if not saved else "the save followed a preview from an earlier turn")}
