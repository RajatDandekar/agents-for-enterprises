"""Lecture 6: the regression gate, exercised. Run it with --mode replay: no key, every reply from the cassettes.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/gate_demo.py --mode replay

1. Replay the main graph run (gemini-3.8-flash, LLM Kavita) -> logs/baseline_graph.json, and check the replay gives
   the same verdict per case as the live run (logs/suite_graph.json).
2. Gate four candidates against that baseline, all from runs we already made:
      the same graph replayed again        -> expect PASS
      graph with flash-lite everywhere     -> logs/suite_tier_lite.json
      graph, flash words + lite routing    -> logs/suite_tier_flashlite.json
      the tool loop                        -> logs/suite_loop.json
      the naive agent                      -> logs/suite_naive.json
      a broken bot (done_on_draft)         -> from logs/bots_*.json, scripted Kavita
3. Run the gate CLI itself as a subprocess, the way CI (and Lecture 8) would, and record its exit code.
Writes logs/gate_demo.json.
"""
import json
import os
import pathlib
import subprocess
import sys

from bahi.evals import gate, runner, suite
from bahi.evals.agents import FLASH, GraphFactory

LOGS = pathlib.Path(__file__).parent / "logs"
live = json.loads((LOGS / "suite_graph.json").read_text())
base = runner.slim(runner.run_suite(GraphFactory(FLASH, "L6_graph"), suite.SUITE, sim="llm", sim_cassette="L6_sim", workers=8,
                                    meta={"tag": "baseline", "mode": os.environ.get("BAHI_LLM_MODE")}), keep_spans=False)
(LOGS / "baseline_graph.json").write_text(json.dumps(base, indent=1, ensure_ascii=False, default=str))
lv = {r["id"]: r["passed"] for r in live["cases"]}
rp = {r["id"]: r["passed"] for r in base["cases"]}
same = [i for i in lv if lv[i] == rp.get(i)]
replayed = sum(r["totals"]["replayed"] for r in base["cases"])
calls = sum(r["totals"]["llm_calls"] for r in base["cases"])
print(f"replay vs live: {len(same)}/{len(lv)} cases with the same verdict; {replayed}/{calls} model calls replayed")


def load(name):
    p = LOGS / name
    return json.loads(p.read_text()) if p.exists() else None


cands = {"graph, replayed again": base, "graph · flash-lite everywhere": load("suite_tier_lite.json"),
         "graph · flash words, lite routing + filling": load("suite_tier_flashlite.json"),
         "tool loop · flash": load("suite_loop.json"), "naive · flash": load("suite_naive.json")}
bot = None
for p in sorted(LOGS.glob("bots_*.json")):
    d = json.loads(p.read_text())
    if "done_on_draft" in d and p.name != "bots_p.json":
        bot = d["done_on_draft"]
if bot:
    cands["bot · done_on_draft (scripted Kavita)"] = {
        "meta": {"versions": {**base["meta"]["versions"], "agent": "bot · done_on_draft"}}, "summary": bot["summary"],
        "cases": [{"id": c["id"], "passed": c["passed"], "never_events": c["ne_full"]} for c in bot["cases"]]}
verdicts = {}
for name, c in cands.items():
    if not c:
        continue
    g = gate.evaluate(c, base, tolerance=0.0)
    verdicts[name] = g
    print("\n==", name)
    print(gate.report(g))
    if name.startswith("graph · flash-lite"):
        g = gate.evaluate(c, base, tolerance=0.0, strict=True)
        verdicts[name + " · --strict"] = g
        print("\n==", name, "--strict")
        print(gate.report(g))

# the CLI, as CI would call it: gate the naive run's results file against the baseline
cli = subprocess.run([sys.executable, "-m", "bahi.evals.gate", "--results", str(LOGS / "suite_tier_lite.json"),
                      "--baseline", str(LOGS / "baseline_graph.json")], capture_output=True, text=True)
cli2 = subprocess.run([sys.executable, "-m", "bahi.evals.gate", "--agent", "graph", "--cases", "S", "--sim", "llm",
                       "--baseline", str(LOGS / "baseline_graph.json")], capture_output=True, text=True,
                      env={**os.environ, "BAHI_LLM_MODE": "replay"})
print("\nCLI (results file):", cli.returncode, cli.stdout)
print("CLI (run S1-S6 in replay):", cli2.returncode, cli2.stdout, cli2.stderr[-2000:])
out = {"replay_vs_live": {"same": len(same), "cases": len(lv), "differ": [i for i in lv if lv[i] != rp.get(i)],
                          "replayed_calls": replayed, "model_calls": calls},
       "baseline": base["summary"], "verdicts": verdicts,
       "cli": [{"cmd": "python -m bahi.evals.gate --results logs/suite_tier_lite.json --baseline logs/baseline_graph.json",
                "exit": cli.returncode, "stdout": cli.stdout},
               {"cmd": "BAHI_LLM_MODE=replay python -m bahi.evals.gate --agent graph --cases S --baseline logs/baseline_graph.json",
                "exit": cli2.returncode, "stdout": cli2.stdout}]}
(LOGS / "gate_demo.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
