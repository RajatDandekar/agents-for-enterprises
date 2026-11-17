"""Probe 2: the modern Ragas API (metrics.collections + llm_factory with Anthropic) and DeepEval's simulator, on Haiku."""
import asyncio
import inspect
import json
import traceback

from ledgerline.course.l6.claude_compat import strip_sampling

strip_sampling()


def sig(o):
    try:
        return str(inspect.signature(o))
    except Exception as e:  # noqa: BLE001
        return f"?{e}"


out = {}
try:
    import anthropic
    from ragas.llms import llm_factory
    from ragas.metrics import collections as RC
    import instructor
    llm = llm_factory("claude-haiku-5-5", provider="anthropic", client=anthropic.AsyncAnthropic(), mode=instructor.Mode.ANTHROPIC_JSON, max_tokens=2000)
    print("llm:", type(llm).__name__)
    for n in ("Faithfulness", "ContextPrecisionWithReference", "ContextRecall", "ToolCallAccuracy", "AgentGoalAccuracyWithReference", "ToolCallF1"):
        c = getattr(RC, n)
        print(n, "init", sig(c.__init__)[:300], "| ascore", sig(c.ascore)[:400])
    ctx = ["POL-APR-002 §5.1 Approval matrix: a purchase executive may approve up to £250,000 gross including VAT. Above that the purchase manager approves, up to £1,000,000."]
    try:
        r = asyncio.run(RC.Faithfulness(llm=llm).ascore(user_input="What is Emma's signing limit?", response="Emma can sign up to £250,000 including VAT; above that Daniel Okafor, the purchase manager, approves.", retrieved_contexts=ctx))
        out["Faithfulness"] = {"value": getattr(r, "value", r), "reason": str(getattr(r, "reason", ""))[:300], "type": type(r).__name__}
    except Exception as e:  # noqa: BLE001
        out["Faithfulness"] = f"ERR {type(e).__name__}: {str(e)[:500]}"
    try:
        r = asyncio.run(RC.ContextRecall(llm=llm).ascore(user_input="What is Emma's signing limit?", retrieved_contexts=ctx, reference="A purchase executive may approve up to £250,000 including VAT."))
        out["ContextRecall"] = {"value": getattr(r, "value", r)}
    except Exception as e:  # noqa: BLE001
        out["ContextRecall"] = f"ERR {type(e).__name__}: {str(e)[:500]}"
    try:
        r = asyncio.run(RC.ContextPrecisionWithReference(llm=llm).ascore(user_input="What is Emma's signing limit?", retrieved_contexts=ctx + ["Canteen opening hours: 07:00 to 15:00."], reference="A purchase executive may approve up to £250,000 including VAT."))
        out["ContextPrecisionWithReference"] = {"value": getattr(r, "value", r)}
    except Exception as e:  # noqa: BLE001
        out["ContextPrecisionWithReference"] = f"ERR {type(e).__name__}: {str(e)[:500]}"
    from ragas.messages import AIMessage, HumanMessage, ToolCall, ToolMessage
    conv = [HumanMessage(content="How many BAT-500 do we have?"),
            AIMessage(content="", tool_calls=[ToolCall(name="check_stock", args={"item_code": "BAT-500"})]),
            ToolMessage(content='{"free_total": 6600}'),
            AIMessage(content="6,600 free: 5,400 in Manchester and 1,200 in Leeds.")]
    try:
        r = asyncio.run(RC.ToolCallAccuracy().ascore(user_input=conv, reference_tool_calls=[ToolCall(name="check_stock", args={"item_code": "BAT-500"})]))
        out["ToolCallAccuracy"] = {"value": getattr(r, "value", r)}
    except Exception as e:  # noqa: BLE001
        out["ToolCallAccuracy"] = f"ERR {type(e).__name__}: {str(e)[:500]}"
    try:
        r = asyncio.run(RC.AgentGoalAccuracyWithReference(llm=llm).ascore(user_input=conv, reference="The assistant reports 6,600 BAT-500 in stock from the stock check."))
        out["AgentGoalAccuracyWithReference"] = {"value": getattr(r, "value", r)}
    except Exception as e:  # noqa: BLE001
        out["AgentGoalAccuracyWithReference"] = f"ERR {type(e).__name__}: {str(e)[:500]}"
except Exception:  # noqa: BLE001
    print("ragas failed", traceback.format_exc()[-1500:])
print(json.dumps(out, indent=1, default=str))

