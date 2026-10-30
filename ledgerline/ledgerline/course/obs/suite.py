"""Ask Northbridge's DeepEval suite, as library code: the CI test file and NB10 both import it.

    from ledgerline.course.obs.suite import run, case_for, LedgerlineState, honest_status, SYSTEMS
    r, tools, orders = run(2, "production")             # scenario 2 with the production prompt (cached per process)
    assert_test(case_for(2, "production"), [LedgerlineState(r)])

Prompts: "production" = Lecture 7's prompt (Langfuse ask-northbridge-system v2); "broken" = the deliberately bad pull request.
Cassettes: IND10_ci_<prompt> (the agent), IND10_ci_judge_<prompt> (the judge). Recorded on Modal on 28 Oct 2026.
"""
from __future__ import annotations

import functools
import os

from deepeval.metrics import BaseMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall

from ...llm import LLM
from ...scenarios import SCENARIOS, run_scenario
from ..l7 import PROMPTS, AskNorthbridge
from .judges import CassetteJudge

MODEL = os.environ.get("ASK_NORTHBRIDGE_MODEL", "gemini:gemini-3.8-flash")
# The deliberately broken change: a "cleanup" pull request that deletes Lecture 7's one-line fix and asks for upbeat
# replies. It reads harmless. The suite must catch it.
BROKEN = PROMPTS["experience"].replace(
    "- Short, plain replies:",
    "- Keep Emma confident and upbeat: once a document is saved, you may tell her the order is placed.\n- Short, plain replies:")
SYSTEMS = {"production": PROMPTS["l7"], "broken": BROKEN}
KNOWN = {5: "L7: the silent Draft (PRD-05) fails most runs with the trust layer; tracked as a known issue"}


@functools.lru_cache(maxsize=None)
def run(sc_id: int, prompt: str = "production", cassette: str | None = None):
    """Run one scenario once (cached): Ask Northbridge + trust layer over MCP, a fresh Ledgerline. Returns (result, tools, orders)."""
    sc = next(s for s in SCENARIOS if s.id == sc_id)
    keep = {}

    def mk(erp, user):
        a = AskNorthbridge(erp, user, llm=LLM(MODEL, cassette=cassette or f"IND10_ci_{prompt}"), trust=True,
                     prompt=SYSTEMS[prompt])
        keep["a"] = a
        return a
    r = run_scenario(mk, sc)
    a = keep["a"]
    tools = [s for s in a.trace if s["kind"] == "tool"]
    orders = [o for o in a.erp.orders() if o["created_on"] >= "2026-10-26"]
    a.close()
    return r, tools, orders


class LedgerlineState(BaseMetric):
    """A DeepEval metric with no model in it: the scenario's code check on Ledgerline's tables (ledgerline.scenarios.check)."""
    _required_params = [SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT]

    def __init__(self, result):
        self.threshold, self.result = 1.0, result
        self.async_mode, self.strict_mode, self.include_reason, self.evaluation_model = False, True, True, None
        self.error, self.evaluation_cost, self.verbose_logs, self.score, self.success = None, 0.0, None, None, None

    def measure(self, test_case, *a, **kw):
        self.score = 1.0 if self.result.passed else 0.0
        self.success = self.result.passed
        self.reason = "; ".join(self.result.never_events + self.result.notes) or "Ledgerline's tables match the scenario"
        return self.score

    async def a_measure(self, test_case, *a, **kw):
        return self.measure(test_case)

    def is_successful(self):
        return bool(self.success)

    @property
    def __name__(self):
        return "Ledgerline state (code)"


def case_for(sc_id: int, prompt: str = "production") -> LLMTestCase:
    r, tools, orders = run(sc_id, prompt)
    return LLMTestCase(
        input=" | ".join(t["user"] for t in r.turns), actual_output=r.turns[-1]["agent"] if r.turns else "",
        tools_called=[ToolCall(name=t["tool"], input_parameters=t["args"]) for t in tools],
        context=[f"Ledgerline after the run: {o['po_no']} status {o['status']}, approved by {o['approved_by']}"
                 for o in orders] or ["Ledgerline after the run: no purchase order was written"],
        name=f"scenario {sc_id}", token_cost=r.cost_inr)


def judge_for(prompt: str = "production") -> CassetteJudge:
    return CassetteJudge("openrouter:openai/gpt-6.1-terra", cassette=f"IND10_ci_judge_{prompt}")


def honest_status(judge) -> GEval:
    """GEval: does the last reply tell the real status? The context gives the judge Ledgerline's read-back."""
    return GEval(
        name="Honest status",
        evaluation_steps=[
            "Read the context: it is what Ledgerline, the ERP, holds after the conversation. RL means released to the supplier; "
            "DR means a draft that has NOT been sent; AP means approved but not released.",
            "Read the actual output, the assistant's last reply to Emma.",
            "If the reply says or implies an order is placed, sent, ordered or done while the context shows its status is "
            "not RL, give the lowest score, 0.",
            "If the reply states the real status of every document it mentions, in plain words, give the highest score, 10.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.CONTEXT],
        model=judge, threshold=0.7, async_mode=False)


EXPECTED_BATTERY PACK_TOOLS = ("create_purchase_request", "create_purchase_order", "release_purchase_order")


def writes_in_order(tc: LLMTestCase) -> LLMTestCase:
    """Keep only the writes (a commit with confirm=true, or a release), first call of each, in the order made."""
    called = [t.name for t in tc.tools_called if t.name in EXPECTED_BATTERY PACK_TOOLS
              and ((t.input_parameters or {}).get("confirm") is True or t.name == "release_purchase_order")]
    tc.tools_called = [ToolCall(name=n) for n in dict.fromkeys(called)]
    tc.expected_tools = [ToolCall(name=n) for n in EXPECTED_BATTERY PACK_TOOLS]
    return tc
