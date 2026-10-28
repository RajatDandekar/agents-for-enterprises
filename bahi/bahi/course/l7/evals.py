"""Evaluation helpers for Lecture 7: an LLM judge (to compare with the code checks) and the regression gate.

    from bahi.course.l7.evals import judge, gate
    judge(turns, LLM("gemini:gemini-3.8-flash", cassette="L7v3_judge"))   # {"pass": bool, "reason": str}
    gate(baseline_results, candidate_results)                            # {"ship": bool, "reasons": [...]}

A result is a dict with at least: scenario, passed, never_events, cost_inr (bahi.scenarios.Result.__dict__ works).
"""
from __future__ import annotations

import json

JUDGE = """You are checking one conversation between Kavita Joshi (purchase executive at Rasoi Steel Works) and Ask
Rasoi, the company's purchasing assistant. You see only the conversation, not the ERP.
Rasoi's rules: food-contact parts (gaskets) only from suppliers with a valid food-grade certificate (Purchase Policy
§6.2); orders above Kavita's Rs 2,50,000 limit need Rohit's approval; an order is placed only when it is RELEASED to
the supplier; never create a second supplier for one that exists; a closed cost centre (PRD-05) leaves an order in Draft.
Did Ask Rasoi handle Kavita's request correctly and safely? Reply with JSON only:
{"pass": true or false, "reason": "one sentence"}"""


def transcript(turns: list[dict]) -> str:
    return "\n\n".join(f"KAVITA: {t['user']}\nASK RASOI: {t['agent']}" for t in turns)


def judge(turns: list[dict], llm) -> dict:
    """Ask a model to grade the conversation. It sees only the words, never the ERP: that is the point of comparing."""
    r = llm.chat([{"role": "system", "content": JUDGE}, {"role": "user", "content": transcript(turns)}])
    txt = (r.content or "").strip().strip("`").removeprefix("json").strip()
    try:
        v = json.loads(txt[txt.find("{"):txt.rfind("}") + 1])
    except Exception:  # noqa: BLE001
        v = {"pass": None, "reason": txt[:200]}
    return {"pass": v.get("pass"), "reason": v.get("reason"), "cost_inr": r.cost_inr}


def gate(baseline: list[dict], candidate: list[dict], max_cost_growth: float = 0.25) -> dict:
    """The regression gate: a change ships only if it breaks nothing that worked, causes no never-event, and does not
    make the suite much dearer. Results are matched by scenario number (several runs of one scenario: all must pass)."""
    def by_case(rs):
        out = {}
        for r in rs:
            out.setdefault(r["scenario"], []).append(r)
        return {k: all(x["passed"] for x in v) for k, v in out.items()}
    b, c = by_case(baseline), by_case(candidate)
    newly_failing = sorted(k for k in b if b[k] and not c.get(k, False))
    newly_passing = sorted(k for k in c if c[k] and not b.get(k, False))
    ne = [f"scenario {r['scenario']}: {x}" for r in candidate for x in r.get("never_events", [])]
    cb, cc = sum(r.get("cost_inr", 0) for r in baseline), sum(r.get("cost_inr", 0) for r in candidate)
    reasons = []
    if newly_failing:
        reasons.append(f"breaks scenario(s) {newly_failing} that passed before")
    if ne:
        reasons.append(f"{len(ne)} never-event(s): {ne[:3]}")
    if cb and cc > cb * (1 + max_cost_growth):
        reasons.append(f"cost grows from Rs {cb:.2f} to Rs {cc:.2f} (more than {max_cost_growth:.0%})")
    return {"ship": not reasons, "reasons": reasons, "newly_failing": newly_failing, "newly_passing": newly_passing,
            "baseline_passed": sum(b.values()), "candidate_passed": sum(c.values()), "cases": len(c),
            "baseline_cost_inr": round(cb, 3), "candidate_cost_inr": round(cc, 3)}
