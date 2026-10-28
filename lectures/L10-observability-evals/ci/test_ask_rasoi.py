"""Ask Rasoi's evaluation suite as pytest tests, with DeepEval. The CI gate: any failing test blocks the merge.

    cd lectures/L10-observability-evals/ci
    ASK_RASOI_PROMPT=production pytest -q test_ask_rasoi.py     # or: deepeval test run test_ask_rasoi.py
    ASK_RASOI_PROMPT=broken     pytest -q test_ask_rasoi.py     # the deliberately broken prompt: must fail

Eleven tests:
  1-6   each scenario, checked on Bahi's tables by code (BahiState, a DeepEval metric with no model inside);
        scenario 5 is a known failure (xfail): the gate blocks NEW failures
  7     no never-event anywhere in the suite
  8     Kavita's gasket order makes its writes in the right order (DeepEval's ToolCorrectnessMetric)
  9-10  the reply tells the real status of the order (GEval, an LLM judge, given Bahi's read-back as context)
  11    the whole suite stays under its ₹ budget
The agent: Lecture 7's Ask Rasoi with the trust layer, gemini-3.8-flash, toolbox over MCP.
The judge: openrouter:openai/gpt-6.1-terra through bahi.llm. Both are recorded in cassettes IND10_ci_<prompt>*.jsonl,
so CI replays them with no key; a changed prompt is a new request, which runs live with the CI's own key
(BAHI_LLM_MODE=auto) or fails loudly in replay mode, never silently passes.
The pieces live in bahi/bahi/course/obs/suite.py, so NB10 runs exactly the same tests.
"""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric

from bahi.course.obs.suite import KNOWN, BahiState, case_for, honest_status, judge_for, run, writes_in_order

PROMPT = os.environ.get("ASK_RASOI_PROMPT", "production")
BUDGET_INR = float(os.environ.get("ASK_RASOI_BUDGET_INR", "12"))
JUDGE = judge_for(PROMPT)
HONEST = honest_status(JUDGE)


@pytest.mark.parametrize("sc_id", [pytest.param(i, marks=pytest.mark.xfail(reason=KNOWN[i], strict=False))
                                   if i in KNOWN else i for i in [1, 2, 3, 4, 5, 6]])
def test_scenario_bahi_state(sc_id):
    r, _, _ = run(sc_id, PROMPT)
    assert_test(case_for(sc_id, PROMPT), [BahiState(r)], run_async=False)


def test_no_never_events():
    ne = [f"scenario {i}: {x}" for i in range(1, 7) for x in run(i, PROMPT)[0].never_events]
    assert not ne, ne


def test_gasket_order_tools_in_order():
    tc = writes_in_order(case_for(2, PROMPT))
    assert_test(tc, [ToolCorrectnessMetric(threshold=1.0, should_consider_ordering=True, model=JUDGE,
                                           async_mode=False)], run_async=False)


@pytest.mark.parametrize("sc_id", [2, 5])
def test_reply_states_real_status(sc_id):
    assert_test(case_for(sc_id, PROMPT), [HONEST], run_async=False)


def test_suite_cost_under_budget():
    total = sum(run(i, PROMPT)[0].cost_inr for i in range(1, 7))
    assert total <= BUDGET_INR, f"suite cost ₹{total:.2f} > budget ₹{BUDGET_INR:.2f}"
