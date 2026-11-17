"""Claude as the judge, for words only (Lecture 6). Outcomes and trajectories are checked in code (suite.py).

    v = judge(rubric, reply, evidence=tool_results)     # {"pass": bool, "reason": str, "tokens_in", "tokens_out", "usd"}
    v = judge(rubric, reply, style="naive")             # the judge that lies: a vague rubric, no evidence

Two judges, measured against labels in experiments/judge_calibration.py:
  naive     "Is this reply helpful, accurate and professional?" and the reply alone. It cannot know a number is wrong:
            it only sees words, and confident words read as accurate.
  grounded  one task-specific question (the rubric), the tool results the agent saw as evidence, a binary verdict, the
            reason first. What practitioners do: binary, specific, evidence in, calibrated against a person.
The model is claude-haiku-5-5 ($0.10 / $0.50 per M): a yes/no on a short rubric; 20x cheaper than the agent's model.
"""
from __future__ import annotations

import json
import re

from ...llm import LLM
from .agent import JUDGE_MODEL, usd

NAIVE = ("You are grading a procurement assistant's reply to a buyer. Is this reply helpful, accurate and professional? "
         'Answer with JSON: {"reason": "<one sentence>", "pass": true|false}.')
GROUNDED = ("You are checking one reply of Ask Northbridge, a procurement assistant inside the Ledgerline ERP, against ONE "
            "criterion. Use only the evidence given (what the ERP tools returned in this conversation); a number, name or "
            "status that is not in the evidence is not supported. Write the reason first (at most 40 words, quoting what "
            "decides it), then the verdict. Pass only if the criterion is fully met.\n"
            'Answer with JSON only: {"reason": "...", "pass": true|false}.')


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        d = {}
    v = d.get("pass")
    if v is None:   # a reply cut short or wrapped in prose: read the verdict field directly
        m2 = re.search(r'"pass"\s*:\s*(true|false)', text or "", re.I)
        v = m2 and m2.group(1).lower() == "true"
        if not d:
            m3 = re.search(r'"reason"\s*:\s*"(.*?)("\s*,|"\s*}|$)', text or "", re.S)
            d = {"reason": m3.group(1) if m3 else (text or "")}
    if isinstance(v, str):
        v = v.strip().lower() in ("true", "yes", "pass")
    return {"pass": bool(v), "reason": str(d.get("reason", text or ""))[:400], "parsed": bool(m)}


def judge(rubric: str, reply: str, evidence=None, user: str = "", style: str = "grounded", model: str = JUDGE_MODEL,
          cassette: str = "L6E_judge", mode: str | None = None) -> dict:
    llm = LLM(model, cassette=cassette, mode=mode, max_tokens=1000)
    if style == "naive":
        msgs = [{"role": "system", "content": NAIVE},
                {"role": "user", "content": f"Buyer's message: {user}\n\nAssistant's reply:\n{reply}"}]
    else:
        ev = json.dumps(evidence, default=str, ensure_ascii=False)[:9000] if evidence is not None else "(none)"
        msgs = [{"role": "system", "content": GROUNDED},
                {"role": "user", "content": f"Criterion: {rubric}\n\nBuyer's message(s): {user}\n\nEvidence (tool results):\n"
                                            f"{ev}\n\nReply to check:\n{reply}"}]
    r = llm.chat(msgs, response_format={"type": "json_object"})
    out = _parse(r.content)
    out.update({"tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "usd": usd(model, r.tokens_in, r.tokens_out),
                "style": style, "model": model.split(":")[-1], "replayed": r.replayed})
    return out
