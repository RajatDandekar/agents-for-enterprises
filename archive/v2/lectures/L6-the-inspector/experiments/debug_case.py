"""Replay one case on the graph and print the draft and facts after every turn (for diagnosing a failure).

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/debug_case.py --args "V11 N02" --mode replay
"""
import json
import sys

from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory

holder = {}


class Spy(GraphFactory):
    def build(self, erp, user, tracer):
        a = super().build(erp, user, tracer)
        holder["a"] = a
        return a


for cid in sys.argv[1:]:
    rec = runner.run_case(Spy(FLASH, "L6_graph"), suite.BY_ID[cid], sim="llm", sim_cassette="L6_sim")
    a = holder["a"]
    print(f"===== {cid} passed={rec['passed']}")
    for h in a.history():
        if h["node"] in ("understand", "onboard", "collect", "answer", "route"):
            print(h["node"], "| draft:", json.dumps(h["draft"], ensure_ascii=False)[:300], "| facts:", json.dumps(h["facts"])[:200], "| awaiting:", h["awaiting"])
    for s in rec["spans"]:
        if s["kind"] == "llm" and s["purpose"] in ("fill", "words"):
            print("  span", s["node"], s["purpose"], s["turn"])
    print("decisions:", json.dumps(a.state.get("decisions", []))[:1500])
