"""Lecture 6: the trust scorecard. One table a plant head can read: how often, how bad, how fast, how costly, and how
much we trust the tests themselves.

BARS are the course team's proposed bars. In a real rollout they are agreed with the business owner BEFORE the first
run (the plan deck's "pass bar and never-events agreed first"); here they are proposals, marked as such.
"""
from __future__ import annotations

from .metrics import LABEL, METRICS

BARS = {"pass_rate": 0.90, "never_events": 0, "turn_p95_seconds": 20.0, "inr_per_resolved_order": 5.0,
        "bots_caught": 1.0, "tone_kappa": 0.6}


def trust_scorecard(run: dict, bots: dict | None = None, tone: dict | None = None, variance: dict | None = None,
                    bars: dict | None = None) -> list[dict]:
    b = {**BARS, **(bars or {})}
    s = run["summary"]
    rows = []

    def row(area, check, value, bar, ok, note=""):
        rows.append({"area": area, "check": check, "value": value, "bar": bar, "ok": ok, "note": note})

    lo, hi = s["ci95"]
    row("How often", "scenarios passed", f"{s['passed']}/{s['cases']} = {s['pass_rate']:.0%} (95%: {lo:.0%}–{hi:.0%})",
        f"≥ {b['pass_rate']:.0%} (proposed)", lo >= b["pass_rate"], "judged on the lower end of the interval")
    row("How bad", "cases with a never-event", s["never_event_cases"], "0", s["never_event_cases"] <= b["never_events"],
        ", ".join(f"{k} {v}" for k, v in s["never_events"].items() if v))
    for m in METRICS:
        n, f = s["metric_applies"][m], s["metric_failures"][m]
        row("Code metrics", LABEL[m], f"{f} failed of {n}", "—", f == 0)
    row("How fast", "p95 seconds per turn", s["turn_p95"], f"≤ {b['turn_p95_seconds']:.0f} s (proposed)",
        s["turn_p95"] <= b["turn_p95_seconds"], f"p50 {s['turn_p50']} s · {s['turns']} turns")
    rpo = s.get("inr_per_resolved_order")
    row("How costly", "₹ per resolved order", f"₹{rpo:.2f}" if rpo is not None else "—", f"≤ ₹{b['inr_per_resolved_order']:.0f} (proposed)",
        rpo is not None and rpo <= b["inr_per_resolved_order"], f"₹{s['inr']:.2f} for {s['cases']} cases")
    if bots:
        code_bots = {k: v for k, v in bots.items() if v.get("targets") != ["tone"]}
        caught = sum(1 for v in code_bots.values() if v.get("caught"))
        row("Trust in the tests", "broken bots caught by their metric", f"{caught}/{len(code_bots)}", "all",
            caught == len(code_bots), "; ".join(k for k, v in code_bots.items() if not v.get("caught")))
    if tone:
        row("Trust in the judge", "tone judge vs course-team labels", f"{tone['agree']}/{tone['n']} agree · κ = {tone['kappa']}",
            f"κ ≥ {b['tone_kappa']} (proposed)", (tone["kappa"] or 0) >= b["tone_kappa"],
            "labels by the course team, to be confirmed by Rajat")
    if variance:
        row("Run to run", "cases whose result flipped between repeats", f"{variance['flipped']}/{variance['cases']}", "—",
            variance["flipped"] == 0, variance.get("note", ""))
    return rows


def as_markdown(rows: list[dict]) -> str:
    out = ["| area | check | value | bar | ok |", "|---|---|---|---|---|"]
    out += [f"| {r['area']} | {r['check']} | {r['value']} | {r['bar']} | {'yes' if r['ok'] else '**no**'} |" for r in rows]
    return "\n".join(out)
