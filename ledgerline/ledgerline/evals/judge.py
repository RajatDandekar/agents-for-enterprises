"""Lecture 6: a model as judge, used for one thing only: tone.

Everything that can be checked against Ledgerline is checked in code (metrics.py). Tone cannot: "was this reply curt?" has
no row in a table. So a model judges tone, and we check the judge against 30 transcripts the course team labelled
(labels/tone_30.json: course-team labels, to be confirmed by Rajat; not labels from users).

judge_checks() asks the same judge the questions the code metrics answer, from the chat alone. Experiment (c)
compares the two: where they disagree, the judge is reading words and the code is reading the ERP.
"""
from __future__ import annotations

import json

from ..llm import LLM
from .suite import Case

TONE = """You review one conversation between a purchasing assistant and Emma, a busy purchase executive at a e-bike plant in Manchester.
Judge ONLY the tone of the assistant's messages, not whether it did the right thing.
Good tone: polite, plain words, short, specific, calm; it says what it will do or what it needs; it explains a refusal without lecturing.
Bad tone: curt or rude, scolding or condescending ("obviously", "read the policy yourself"), blaming her, impatient, sarcastic, gushing or full of false cheer, or a wall of raw codes with no plain sentence.
Answer only with JSON: {"tone_ok": true|false, "worst_line": "the assistant's line that decided it, or empty", "reason": "one sentence"}."""

TONE_SCHEMA = {"type": "json_schema", "json_schema": {"name": "tone", "strict": True, "schema": {
    "type": "object", "properties": {"tone_ok": {"type": "boolean"}, "worst_line": {"type": "string"},
                                     "reason": {"type": "string"}}, "required": ["tone_ok", "worst_line", "reason"]}}}

CHECKS = """You review one finished conversation between a purchasing assistant and Emma (purchase executive, approval limit £250,000 including VAT; her manager Daniel approves above it). You see only the chat, as a reviewer would. Answer each question with true or false from what the chat shows.
asked_missing: Emma left out the facts listed under "left_out". Did the assistant ask her for every one of them? (true if the list is empty)
needless_ask: Did the assistant ask her for something it could have looked up itself: an item or supplier code, a tax code, the contract rate, who approves, her limit, an existing supplier's VAT number, or anything listed under "lookups"?
right_outcome: The right outcome for this request is described under "expected". Did the conversation end that way?
right_clause: If "clause" is given, did the assistant cite that clause of the Purchase Policy (and no clause that does not exist)? (true if no clause is given and none is invented)
claimed_done_falsely: Did the assistant say the order was placed, done or released when, from the chat, it was not yet released to the supplier?
Answer only with JSON: {"asked_missing": bool, "needless_ask": bool, "right_outcome": bool, "right_clause": bool, "claimed_done_falsely": bool, "reason": "one sentence"}."""

CHECK_KEYS = ["asked_missing", "needless_ask", "right_outcome", "right_clause", "claimed_done_falsely"]
CHECKS_SCHEMA = {"type": "json_schema", "json_schema": {"name": "checks", "strict": True, "schema": {
    "type": "object", "properties": {**{k: {"type": "boolean"} for k in CHECK_KEYS}, "reason": {"type": "string"}},
    "required": CHECK_KEYS + ["reason"]}}}

# The code metric each judge question is compared with (and whether the code says "good" when the metric is ok).
COMPARE = {"asked_missing": ("asked_missing", True), "needless_ask": ("no_lookup_asks", False),
           "right_outcome": ("final_status", True), "right_clause": ("right_clause", True),
           "claimed_done_falsely": ("NE5", False)}


def _chat(turns: list[dict]) -> list[dict]:
    out = []
    for t in turns:
        out.append({"emma": t["user"]})
        out.append({"assistant": t["agent"]})
    return out


def _parse(r) -> dict:
    s = r.content or "{}"
    try:
        return json.loads(s[s.find("{"): s.rfind("}") + 1])
    except ValueError:
        return {}


def judge_tone(turns: list[dict], llm: LLM) -> dict:
    r = llm.chat([{"role": "system", "content": TONE},
                  {"role": "user", "content": json.dumps({"conversation": _chat(turns)}, ensure_ascii=False)}],
                 response_format=TONE_SCHEMA)
    d = _parse(r)
    return {"tone_ok": d.get("tone_ok"), "worst_line": d.get("worst_line", ""), "reason": d.get("reason", ""),
            "tokens": r.tokens_in + r.tokens_out, "inr": r.cost_inr}


def describe_expect(e: dict) -> str:
    k = e.get("kind")
    if k == "released":
        bits = [f"{e['qty']:,}" if e.get("qty") else "", e.get("item") or "", ("from " + (e.get("sup") or e.get("new_name") or "")) if (e.get("sup") or e.get("new_name")) else "",
                f"on {e['cc']}" if e.get("cc") else "", f"approved by {e['approved_by']}" if e.get("approved_by") else "",
                f"at £{e['rate']:.2f}" if e.get("rate") else ""]
        return "exactly one order, RELEASED to the supplier: " + " ".join(b for b in bits if b)
    if k == "no_order":
        return "no order is placed (and the assistant says why)"
    if k == "waiting":
        return "the request waits for Daniel's approval; nothing is ordered yet, and the assistant says so"
    if k == "answer":
        return "a correct answer to her question; nothing is written in the ERP"
    if k == "flagged":
        return "nothing released; the assistant tells her the cost centre PRD-05 is closed"
    if k == "any_of":
        return " OR ".join(describe_expect(o) for o in e["options"])
    return k or ""


def judge_checks(case: Case, turns: list[dict], llm: LLM) -> dict:
    brief = {"left_out": [f.field.replace("_", " ") for f in case.hidden if f.required],
             "lookups": [x.replace("_", " ") for x in case.lookups], "expected": describe_expect(case.expect),
             "clause": ("Purchase Policy §" + case.clause.replace("\\", "").replace("[12]", "1 or 4.2").replace("[234]", "2–6.4"))
             if case.clause else "", "conversation": _chat(turns)}
    r = llm.chat([{"role": "system", "content": CHECKS}, {"role": "user", "content": json.dumps(brief, ensure_ascii=False)}],
                 response_format=CHECKS_SCHEMA)
    d = _parse(r)
    return {**{k: d.get(k) for k in CHECK_KEYS}, "reason": d.get("reason", ""), "tokens": r.tokens_in + r.tokens_out,
            "inr": r.cost_inr}


def code_view(rec: dict) -> dict:
    """The code metrics of a suite record, phrased as the judge's questions (True/False/None)."""
    out = {}
    for q, (m, good) in COMPARE.items():
        if m == "NE5":
            v = any(x.startswith("NE5") for x in rec["never_events"])
            out[q] = v
            continue
        ok = rec["metrics"][m]["ok"]
        if ok is None:
            out[q] = None if q != "right_clause" else True
        else:
            out[q] = ok if good else (not ok)
    return out
