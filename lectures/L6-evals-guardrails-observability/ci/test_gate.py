"""The regression gate for Ask Northbridge: pytest + DeepEval. A failing check fails the build, so the change does not merge.

    GATE_PROMPT=good deepeval test run test_gate.py        # the prompt as it is on this branch (hermes/chat.py ASK)
    GATE_PROMPT=thursday deepeval test run test_gate.py    # what the Thursday edit would have done

The gate runs the agent live (claude-sonnet-5-5, key from the CI secret ANTHROPIC_API_KEY) on the tasks the incident
taught us, each GATE_K times (a failure that happens one time in seven needs more than one run to show up), plus the
poisoned invoice and the closed cost centre. Every metric here is deterministic: it reads Ledgerline and the tool calls.
The judge-scored words run nightly, not on every pull request (cost, and a judge is noisier than code).
"""
import os

import pytest
from deepeval import assert_test
from deepeval.metrics import BaseMetric, ToolCorrectnessMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase, ToolCall

from ledgerline.course.l6 import suite as S
from ledgerline.llm import LLM

PROMPT = os.environ.get("GATE_PROMPT", "good")
K = int(os.environ.get("GATE_K", "2"))
CASES = [(t, r) for t in ("T01", "T02", "T03") for r in range(K)] + [("T05", 0), ("T09", 0)]
EXPECTED = {"T02": [ToolCall(name="create_purchase_request")]}   # the commit must go through the tool, after the yes


class LedgerlineChecks(BaseMetric):
    """Deterministic: the task's outcome and trajectory checks (ledgerline.course.l6.suite), score 1 only if all pass."""

    def __init__(self, checks):
        self.threshold, self.checks = 1.0, checks
        self.async_mode, self.include_reason, self.strict_mode, self.evaluation_model = False, True, True, None

    def measure(self, test_case, *a, **kw):
        bad = [c for c in self.checks if c["kind"] in ("outcome", "trajectory") and not c["pass"]]
        self.score = 0.0 if bad else 1.0
        self.success = not bad
        self.reason = "; ".join(f"{c['kind']}: {c['why']}" for c in bad) or "all outcome and trajectory checks passed"
        return self.score

    async def a_measure(self, test_case, *a, **kw):
        return self.measure(test_case)

    def is_successful(self):
        return bool(self.success)

    @property
    def __name__(self):
        return "Ledgerline checks"


@pytest.mark.parametrize("task_id,rep", CASES, ids=[f"{t}-run{r + 1}" for t, r in CASES])
def test_gate(task_id, rep):
    task = S.BY_ID[task_id]
    r = S.run_task(task, prompt=PROMPT, llm_for=lambda m: LLM(m, mode="live", max_tokens=8192), judge_fn=None,
                   tags=("ci-gate", PROMPT))
    assert r["error"] is None, r["error"]
    called = [ToolCall(name=c["tool"], input_parameters=c["args"]) for t in r["turns"] for c in t["calls"]]
    tc = LLMTestCase(input=" / ".join(task["turns"]), actual_output=r["turns"][-1]["reply"] or "", tools_called=called,
                     expected_tools=EXPECTED.get(task_id))
    metrics = [LedgerlineChecks(r["checks"])]
    if task_id in EXPECTED:
        metrics.append(ToolCorrectnessMetric(threshold=1.0, model=AnthropicModel(model="claude-haiku-5-5")))
    assert_test(tc, metrics)
