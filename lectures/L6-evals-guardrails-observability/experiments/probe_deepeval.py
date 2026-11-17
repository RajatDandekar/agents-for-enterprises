"""Probe DeepEval 4.3.4 with Claude (no assumptions): its AnthropicModel signature, one GEval and one ToolCorrectness."""
import inspect
import json

import deepeval
from deepeval.metrics import GEval, ToolCorrectnessMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall

print("deepeval", deepeval.__version__)
print("AnthropicModel", inspect.signature(AnthropicModel.__init__))
src = inspect.getsource(AnthropicModel)
print("temperature in source:", "temperature" in src, src.count("temperature"))
out = {}
try:
    m = AnthropicModel(model="claude-haiku-5-5")
    g = GEval(name="Words", criteria="The reply gives the free stock of BAT-500 as 6,600.",
              evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT], model=m, threshold=0.5,
              async_mode=False)
    tc = LLMTestCase(input="How many BAT-500 do we have?", actual_output="You have 6,600 free: 5,400 in Manchester, 1,200 in Leeds.")
    g.measure(tc)
    out["geval"] = {"score": g.score, "reason": g.reason, "success": g.success}
except Exception as e:  # noqa: BLE001
    out["geval_error"] = f"{type(e).__name__}: {str(e)[:600]}"
try:
    t = ToolCorrectnessMetric(threshold=1.0)
    tc = LLMTestCase(input="x", actual_output="y", tools_called=[ToolCall(name="check_stock", input_parameters={"item_code": "BAT-500"})],
                     expected_tools=[ToolCall(name="check_stock")])
    t.measure(tc)
    out["tool"] = {"score": t.score, "reason": t.reason}
except Exception as e:  # noqa: BLE001
    out["tool_error"] = f"{type(e).__name__}: {str(e)[:600]}"
print(json.dumps(out, indent=1))
