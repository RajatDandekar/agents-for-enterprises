"""Lecture 8, the final scorecard: the whole reference stack through Lecture 6's suite and regression gate.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/scorecard.py --mode auto      # records L8_* cassettes
    /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/scorecard.py --mode replay    # proves it, no key

The agent under test is Lecture 5's AuthorityAgent: Lecture 4's control graph (route, gates, memory) with the
Lecture 3 intent tools behind Lecture 5's guard (the user's own identity, preview before commit, read-back, audit).
Kavita is Lecture 6's model simulator (cassette L8_sim); Rohit approves in his own Bahi session (runner._rohit),
and decides Supplier Policy §3.4 onboarding files in the app's inbox (Suited.respond: the runner does not know the
inbox, so without this every new-supplier case waits on a file nobody opens).
The 60 cases include the six course scenarios (family S). Gated against L6's baseline (the bare graph, 56/60),
strict: a case that passed there and fails here is named.

Writes demo/logs/scorecard_suite.json (every case), demo/logs/scorecard_gate.json (the verdict) and
demo/logs/scorecard.json (the trust scorecard rows, the six scenarios, and the comparison with L6's runs).
The durable path (Temporal) and MCP are exercised by demo/final_demo.py, not here: 60 conversations each with its
own Temporal test server would measure the test harness, not the agent.
"""
from __future__ import annotations

import itertools
import json
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parent
sys.path.insert(0, str(COURSE / "bahi"))

from bahi.agent.authority import ApprovalInbox, AuditLog, AuthorityAgent  # noqa: E402
from bahi.evals import gate, runner, scorecard, suite  # noqa: E402

MODEL = "gemini:gemini-3.8-flash"
L6 = COURSE / "lectures/L6-the-inspector/experiments/logs"
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)


class AuthorityFactory:
    kind = "authority"
    name = "authority · gemini-3.8-flash"

    def __init__(self, model=MODEL, cassette="L8_authority"):
        self.models = {"words": model, "route": model, "fill": model}
        self.cassette = cassette
        self._n = itertools.count(1)

    def build(self, erp, user, tracer):
        audit = AuditLog(erp)
        return Suited(AuthorityAgent(erp, user, llm=tracer.llm(self.models["words"], self.cassette),
                                     inbox=ApprovalInbox(erp, audit=audit), audit=audit, conv=f"sc{next(self._n)}"))


class Suited:
    """AuthorityAgent as the L6 runner reads it: runner.run_case takes `agent.trace` for a list (the tool loop's), but
    AuthorityAgent.trace is a method. Expose the graph's state and tool log instead, so the runner records the path."""

    def __init__(self, a):
        self.a = a
        self.llm = a.llm
        self.onboarding_decided = 0

    def respond(self, text):
        reply = self.a.respond(text)
        # Rohit decides onboarding files in the app's inbox (Supplier Policy §3.4, Lecture 5), the way runner._rohit
        # decides Bahi's approval table. Without this the suite waits forever on a file nobody opens.
        for it in [x for x in self.a.inbox.items.values() if x["kind"] == "SUP" and x["status"] == "PENDING"
                   and INBOX_APPROVER]:
            res = self.a.inbox.decide(it["id"], self.a.erp.session(it["approver"]), "approve", "file complete")
            if res.get("ok"):
                self.onboarding_decided += 1
                reply = (reply or "") + "\n\n" + (self.a.after_decision(self.a.inbox.items[it["id"]]) or "")
        return reply

    @property
    def state(self):
        return self.a.graph.state

    @property
    def tool_log(self):
        return self.a.graph.tool_log


SUF = "" if "--cases" not in sys.argv else "_" + sys.argv[sys.argv.index("--cases") + 1].replace(",", "_")
INBOX_APPROVER = "--no-inbox" not in sys.argv   # --no-inbox: the runner as L6 ships it (nobody opens the app inbox)
SUF += "" if INBOX_APPROVER else "_no_inbox"
t0 = time.time()
fac = AuthorityFactory()
CASES = sys.argv[sys.argv.index("--cases") + 1] if "--cases" in sys.argv else "all"
cases = suite.select(CASES)
run = runner.run_suite(fac, cases, sim="llm", sim_cassette="L8_sim", workers=8,
                       meta={"tag": "authority", "mode": os.environ.get("BAHI_LLM_MODE", "auto")})
run["meta"]["wall_seconds"] = round(time.time() - t0, 1)
out = runner.slim(run, keep_spans=False)
(LOGS / f"scorecard_suite{SUF}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))

baseline = json.loads((L6 / "baseline_graph.json").read_text())
g = gate.evaluate(out, baseline, strict=True)
(LOGS / f"scorecard_gate{SUF}.json").write_text(json.dumps(g, indent=1, ensure_ascii=False))
print(gate.report(g))

bm = json.loads((L6 / "bots_matrix.json").read_text())
bots = {r["bot"]: {"targets": r["targets"], "caught": r["caught"]} for r in bm["rows"] if r["bot"] != "reference"}
tone = json.loads((L6 / "judge.json").read_text())["tone_labels"]["agreement"]
card = scorecard.trust_scorecard(out, bots=bots, tone=tone)
print(scorecard.as_markdown(card))

s = out["summary"]
six = [{"id": r["id"], "name": r["name"], "passed": r["passed"], "never_events": r["never_events"],
        "orders": r.get("orders")} for r in out["cases"] if r["family"] == "S" or r["id"].startswith("S")]
compare = {}
for tag in ("graph", "loop", "naive"):
    p = L6 / f"suite_{tag}.json"
    if p.exists():
        x = json.loads(p.read_text())["summary"]
        compare[tag] = {k: x.get(k) for k in ("cases", "passed", "ci95", "never_event_cases", "inr",
                                               "inr_per_resolved_order", "turn_p95")}
compare["authority (this run)"] = {k: s.get(k) for k in ("cases", "passed", "ci95", "never_event_cases", "inr",
                                                          "inr_per_resolved_order", "turn_p95")}
failed = [{"id": r["id"], "name": r["name"], "never_events": r["never_events"], "crashed": r["crashed"],
           "metrics_failed": {k: v.get("why") for k, v in r["metrics"].items() if v["ok"] is False}}
          for r in out["cases"] if not r["passed"]]
res = {"agent": fac.name, "model": MODEL, "mode": run["meta"]["mode"], "wall_seconds": run["meta"]["wall_seconds"],
       "summary": s, "gate": {k: g[k] for k in ("passed", "reasons", "newly_failing", "newly_passing")},
       "trust_scorecard": card, "six_scenarios": six, "failed_cases": failed, "compare_l6": compare,
       "sources": {"suite": "demo/logs/scorecard_suite.json", "gate": "demo/logs/scorecard_gate.json",
                   "baseline": "lectures/L6-the-inspector/experiments/logs/baseline_graph.json",
                   "bots": "lectures/L6-the-inspector/experiments/logs/bots_matrix.json",
                   "tone": "lectures/L6-the-inspector/experiments/logs/judge.json"}}
(LOGS / f"scorecard{SUF}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
print(f"\n{s['passed']}/{s['cases']} pass · 95% {s['ci95']} · never-event cases {s['never_event_cases']} · "
      f"₹{s['inr']} total · ₹/resolved order {s['inr_per_resolved_order']} · p95 s/turn {s['turn_p95']} · "
      f"sim ₹{s['sim_inr']}")
print("FAILED:", json.dumps(failed, ensure_ascii=False)[:3000])
