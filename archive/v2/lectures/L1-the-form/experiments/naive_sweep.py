"""Lecture 1 experiment: the naive agent (38 raw services as tools, service account, no harness) on the six scenarios.

    modal run tools/modal_run.py --script lectures/L1-the-form/experiments/naive_sweep.py \
        --args "--model gemini:gemini-3.8-flash --tier default --only 1,2,3 --cassette L1_naive_part_d1"

Writes logs/naive_<tier>_s<ids>.json: per scenario the result, never-events, tool calls, tokens, seconds, ₹,
whether the step cap was hit, and the full transcript (every tool call and every result the model saw).
merge_logs.py combines the parts into logs/naive_sweep.json and the cassette parts into L1_naive.jsonl.
"""
import argparse
import json
import pathlib
import time
import traceback

from bahi.agent.naive import NaiveAgent
from bahi.llm import LLM
from bahi.scenarios import SCENARIOS, run_scenario

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
ap.add_argument("--tier", default="default")
ap.add_argument("--only", default="")
ap.add_argument("--cassette", default="L1_naive")
a = ap.parse_args()
out = pathlib.Path(__file__).parent / "logs"
out.mkdir(exist_ok=True)
scs = [s for s in SCENARIOS if not a.only or str(s.id) in a.only.split(",")]


def transcript(agent):
    """The conversation the model saw, without the provider's opaque thought signatures."""
    rows = []
    for m in agent.messages[1:]:
        if m["role"] == "user":
            rows.append({"role": "user", "text": m["content"]})
        elif m["role"] == "assistant":
            for tc in m.get("tool_calls") or []:
                rows.append({"role": "call", "id": tc["id"], "name": tc["function"]["name"],
                             "args": json.loads(tc["function"]["arguments"])})
            if m.get("content"):
                rows.append({"role": "agent", "text": m["content"]})
        elif m["role"] == "tool":
            rows.append({"role": "result", "id": m["tool_call_id"], "out": json.loads(m["content"])})
    return rows


llm = LLM(a.model, cassette=a.cassette)
rows = []
for sc in scs:
    agents = []

    def make(erp, user):
        ag = NaiveAgent(erp, user, llm=llm)
        agents.append(ag)
        return ag

    n0 = len(llm.log)
    t0 = time.perf_counter()
    try:
        r = run_scenario(make, sc, verbose=True)
        d = dict(r.__dict__)
        d["llm_calls"] = len(llm.log) - n0
        d["hit_step_cap"] = any("stopped after" in (t["agent"] or "") for t in r.turns)
        d["tool_calls"] = sum(1 for m in agents[0].messages if m["role"] == "tool")
        d["transcript"] = transcript(agents[0])
        d["per_call"] = [{"tokens_in": x.tokens_in, "tokens_out": x.tokens_out, "seconds": x.seconds,
                          "calls": [t.name for t in x.tool_calls]} for x in llm.log[n0:]]
        d["error"] = None
    except Exception as e:  # rate limits, unavailable model: record it, do not hide it
        d = {"scenario": sc.id, "name": sc.name, "passed": None, "error": f"{type(e).__name__}: {e}"[:1500],
             "trace": traceback.format_exc()[-3000:], "llm_calls": len(llm.log) - n0,
             "tokens_in": sum(x.tokens_in for x in llm.log[n0:]), "tokens_out": sum(x.tokens_out for x in llm.log[n0:]),
             "transcript": transcript(agents[0]) if agents else []}
    d.update(model=a.model, tier=a.tier, wall_seconds=round(time.perf_counter() - t0, 1))
    rows.append(d)
    print(f"== {a.tier} S{sc.id} passed={d['passed']} NE={d.get('never_events')} err={d['error']} "
          f"tokens={d.get('tokens_in', 0) + d.get('tokens_out', 0)} ₹{d.get('cost_inr')}", flush=True)

tag = a.only.replace(",", "") or "all"
(out / f"naive_{a.tier}_s{tag}.json").write_text(json.dumps(rows, indent=1, default=str, ensure_ascii=False))
