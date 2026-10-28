"""Diagnose case V11 (the graph asks for the GSTIN again and again). Replay only.

    modal run tools/modal_run.py --script lectures/L6-the-inspector/experiments/debug_v11.py --mode replay
"""
from bahi.evals import runner, suite
from bahi.evals.agents import FLASH, GraphFactory, TieredGraphAgent


class Loud(TieredGraphAgent):
    def n_understand(self, st):
        print("understand: awaiting =", repr(st.get("awaiting")), "stage =", repr(st.get("stage")), "goto =", repr(st.get("goto")))
        out = super().n_understand(st)
        print("   -> draft update:", out.get("draft"), "| intent:", out.get("intent"))
        return out

    def _extract(self, st, text):
        d = super()._extract(st, text)
        print("   extract:", repr(text[:60]), "->", d)
        return d


runner.run_case(GraphFactory(FLASH, "L6_graph", cls=Loud), suite.BY_ID["V11"], sim="llm", sim_cassette="L6_sim", max_turns=3)
