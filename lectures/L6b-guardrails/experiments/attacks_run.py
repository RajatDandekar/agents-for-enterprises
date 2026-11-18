"""The 20 library attacks through Ask Northbridge with a chosen guard set (Lecture 7), live on Claude Sonnet.

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script attacks_run.py --image guards --args "--prompt thursday --sets code"

On 16 Nov the attacks were measured with no guards and with ALL nine guards (code guards + the injection classifier +
Presidio): ../../L6-evals-guardrails-observability/experiments/logs/guards_attacks_r1.json (good prompt) and
guards_attacks_thu.json (Thursday prompt). This script adds the set the lecture's sentence is about, the CODE guards only
(guards.DETERMINISTIC + output_check, the set Argus calls "code"): no classifier, no Presidio, nothing a model decides.
Same method as Lecture 6's guards_eval.py (a fresh sandbox per attack; success is read by attacks.succeeded from Ledgerline,
the tool calls, the trace and the reply, never judged by a model), written to this folder's logs.
Writes logs/l7_attacks_<set>_<prompt>.json. Each row keeps every turn's tool calls with their results, so a notebook can
replay a guard on them without a model.
"""
import argparse
import json

from _common import now, pmap, spend, write

from ledgerline.course.l6 import guards as G
from ledgerline.course.l6.agent import Agent
from ledgerline.course.l6.attacks import ATTACKS, setup, succeeded
from ledgerline.course.l6.tracing import Tracing
from ledgerline.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--sets", default="code")
ap.add_argument("--prompt", default="good")
ap.add_argument("--ids", default="")
ap.add_argument("--tag", default="")
a = ap.parse_args()
SETS = {"off": [], "code": G.DETERMINISTIC + ["output_check"], "all": G.ALL}


def one(job):
    gs, att = job
    att = json.loads(json.dumps(att))
    tr = Tracing(batch=False, redact=(lambda s: G.redact(s)[0]) if "pii" in SETS[gs] else None)     # spans kept in memory only
    ag = Agent(a.prompt, guards=G.Guards(SETS[gs]) if SETS[gs] else None, tracing=tr,
               llm_for=lambda m: LLM(m, mode="live", max_tokens=8192), conversation_id=f"l7-attacks-{a.prompt}-{gs}-{att['id']}")
    setup(ag, att)
    err = None
    try:
        for m in att["turns"]:
            ag.turn(m)
    except Exception as e:  # noqa: BLE001
        err = f"{type(e).__name__}: {str(e)[:300]}"
    ok, why = succeeded(ag, att, json.dumps(tr.log.spans, default=str)) if not err else (None, err)
    evs = [e for t in ag.turns for e in t.get("guard_events", [])]
    stopped = [e for e in evs if e["decision"] in ("refused", "blocked", "quarantined", "redacted", "flagged")]
    return {"set": gs, "id": att["id"], "title": att["title"], "owasp": att["owasp"], "channel": att["channel"],
            "succeeded": ok, "why": why, "error": err, "stopped_by": sorted({e["guard"] for e in stopped}),
            "refusals": [{k: e.get(k) for k in ("guard", "decision", "where", "why", "tool", "rule", "turn")} for e in stopped],
            "turns": [{"text": t["text"], "reply": t["reply"],
                       "calls": [{k: c.get(k) for k in ("tool", "args", "ok", "refused_by", "rule", "out")} for c in t["calls"]]}
                      for t in ag.turns],
            "saved": ag.writes(), "usd": round(sum(t["usd"] for t in ag.turns), 5),
            "model_calls": sum(len(t["model_calls"]) for t in ag.turns),
            "guard_ms": round(sum(e.get("ms") or 0 for e in evs), 2)}


jobs = [(s, x) for s in a.sets.split(",") for x in ATTACKS if not a.ids or x["id"] in a.ids.split(",")]
rows = pmap(one, jobs, workers=10)
if any("credit balance is too low" in (r["error"] or "") for r in rows):
    print("STOP: the model account answered 'credit balance is too low'")
summ = {}
for s in a.sets.split(","):
    rs = [r for r in rows if r["set"] == s and r["succeeded"] is not None]
    summ[s] = {"attacks": len(rs), "succeeded": sum(1 for r in rs if r["succeeded"]),
               "asr": round(sum(1 for r in rs if r["succeeded"]) / max(1, len(rs)), 3),
               "errors": sum(1 for r in rows if r["set"] == s and r["succeeded"] is None),
               "succeeded_ids": [r["id"] for r in rs if r["succeeded"]]}
usd = sum(r["usd"] for r in rows)
for s in a.sets.split(","):
    write(f"l7_attacks_{s}_{a.prompt}{a.tag}.json", {
        "at": now(), "prompt": a.prompt, "set": s, "guards": SETS[s], "model": "claude-sonnet-5-5", "summary": summ[s],
        "rows": sorted([r for r in rows if r["set"] == s], key=lambda r: r["id"]),
        "usd": round(sum(r["usd"] for r in rows if r["set"] == s), 4)})
spend(f"attacks_{a.sets.replace(',', '+')}_{a.prompt}{a.tag}", usd, sum(r["model_calls"] for r in rows), f"{len(rows)} attack runs, direct on the model account")
print(json.dumps(summ, indent=1))
for r in sorted(rows, key=lambda r: (r["id"], r["set"])):
    print(r["id"], r["set"], r["succeeded"], (r["why"] or "")[:80], r["stopped_by"], r["usd"])
