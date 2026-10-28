"""Lecture 6: send one full suite run of the control graph to Langfuse Cloud, then read it back through the API.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/langfuse_export.py --mode replay

1. Replays the 60-case suite on the graph (gemini-3.8-flash, model-persona Kavita) from the recorded cassettes: no model
   is called, so the traces carry the seconds, tokens and ₹ of our recorded run.
2. export_langfuse(): one Langfuse trace per conversation (POST /api/public/ingestion): turns as spans, model calls as
   generations with tokens and cost, Bahi service calls as spans, and the code metrics as scores.
3. verify_langfuse(): GET /api/public/traces?tags=L6-suite (how many arrived), GET /api/public/traces/<id> for
   scenario 2 (its tree, latency, cost), GET /api/public/metrics/daily (the project's daily totals for the tag).
Writes logs/langfuse.json. Keys are read from the environment and never printed or written.
"""
import json
import os
import pathlib

from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory
import time

from bahi.evals.trace import LF_TAG, _iso, export_langfuse, langfuse_ready, verify_langfuse

LOGS = pathlib.Path(__file__).parent / "logs"
ok, why = langfuse_ready()
print("langfuse:", why)
run = runner.run_suite(GraphFactory(FLASH, "L6_graph"), suite.SUITE, sim="llm", sim_cassette="L6_sim", workers=8,
                       meta={"tag": "graph", "mode": os.environ.get("BAHI_LLM_MODE")})
s = run["summary"]
logged = {r["id"]: r["passed"] for r in json.loads((LOGS / "suite_graph.json").read_text())["cases"]}
same = sum(1 for r in run["cases"] if logged.get(r["id"]) == r["passed"])
print(f"suite replayed: {s['passed']}/{s['cases']} passed, {same}/60 verdicts as logged, "
      f"{sum(r['totals']['replayed'] for r in run['cases'])}/{s['llm_calls']} model calls replayed")
t0 = time.time() - 3 * 3600   # lay the 60 conversations out three hours ago, 2 s apart, with their recorded seconds
exp = export_langfuse(run["cases"], run["meta"], t0=t0) if ok else {"exported": 0, "reason": why}
print("export:", {k: v for k, v in exp.items() if k != "trace_ids"})
ver = verify_langfuse(LF_TAG, expect=len(run["cases"]), sample_trace=(exp.get("trace_ids") or {}).get("S2"),
                      t0=_iso(t0 - 60), t1=_iso(t0 + 2 * len(run["cases"]) + 900)) if ok else {}
print("verify:", json.dumps({k: v for k, v in ver.items() if k != "sample"}, default=str)[:2500])
if ver.get("sample"):
    sm = ver["sample"]
    print("sample S2:", sm["status"], len(sm["observations"]), "observations;",
          sum(1 for o in sm["observations"] if o["type"] == "GENERATION"), "generations")
local = next(r for r in run["cases"] if r["id"] == "S2")
out = {"tag": LF_TAG, "host": exp.get("host"), "suite": {k: s[k] for k in ("cases", "passed", "ci95", "inr", "llm_calls", "tokens",
                                                                          "turn_p50", "turn_p95")},
       "replay_same_verdicts": same, "export": exp, "verify": ver,
       "local_S2": {"spans": len(local["spans"]), "llm": sum(1 for x in local["spans"] if x["kind"] == "llm"),
                    "svc": sum(1 for x in local["spans"] if x["kind"] == "svc"), "turns": len(local["turns"]),
                    "inr": local["totals"]["inr"], "seconds": local["totals"]["seconds"],
                    "tokens": local["totals"]["tokens_in"] + local["totals"]["tokens_out"]}}
(LOGS / "langfuse.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
