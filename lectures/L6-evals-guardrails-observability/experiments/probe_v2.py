"""Probe (no assumptions): DeepEval 4.3.4 conversational API and Ragas 0.4.4 API, with Claude Haiku."""
import inspect
import json
import traceback

from ledgerline.course.l6.claude_compat import strip_sampling

strip_sampling()
out = {}


def sig(o):
    try:
        return str(inspect.signature(o))
    except Exception as e:  # noqa: BLE001
        return f"?{e}"


try:
    import deepeval
    from deepeval import test_case as TC
    print("deepeval", deepeval.__version__)
    print("test_case names:", [n for n in dir(TC) if not n.startswith("_")])
    from deepeval.test_case import ConversationalTestCase, Turn
    print("ConversationalTestCase", sig(ConversationalTestCase.__init__)[:600])
    print("Turn", sig(Turn.__init__)[:600])
    import deepeval.metrics as M
    print("conversational metrics:", [n for n in dir(M) if "onvers" in n or "Turn" in n or "Retention" in n or "Role" in n or "Goal" in n or "Topic" in n])
    for n in ("ConversationalGEval", "ConversationCompletenessMetric", "KnowledgeRetentionMetric", "TurnRelevancyMetric", "GoalAccuracyMetric"):
        if hasattr(M, n):
            print(n, sig(getattr(M, n).__init__)[:500])
    try:
        import deepeval.simulator as SIM
        print("simulator names:", [n for n in dir(SIM) if not n.startswith("_")])
        from deepeval.simulator import ConversationSimulator
        print("ConversationSimulator", sig(ConversationSimulator.__init__)[:700])
        print("simulate", sig(ConversationSimulator.simulate)[:700])
    except Exception:  # noqa: BLE001
        print("simulator import failed:", traceback.format_exc()[-600:])
    try:
        from deepeval.dataset import ConversationalGolden
        print("ConversationalGolden", sig(ConversationalGolden.__init__)[:600])
    except Exception:  # noqa: BLE001
        print("ConversationalGolden import failed", traceback.format_exc()[-300:])
    from deepeval.models import AnthropicModel
    m = AnthropicModel(model="claude-haiku-5-5")
    turns = [Turn(role="user", content="Order the usual, please, needed by 4 Dec 2026."),
             Turn(role="assistant", content="Preview: 2,400 x BAT-500 on PRD-03, £342,720, needs Daniel Okafor's approval. Shall I submit it?"),
             Turn(role="user", content="Yes, go ahead."),
             Turn(role="assistant", content="Submitted: PR/2026/04417, waiting for Daniel Okafor's approval. Nothing is ordered yet.")]
    kw = {}
    ps = inspect.signature(ConversationalTestCase.__init__).parameters
    if "scenario" in ps:
        kw["scenario"] = "Emma wants her usual battery order raised, after seeing a preview."
    if "expected_outcome" in ps:
        kw["expected_outcome"] = "One purchase request for 2,400 BAT-500 on PRD-03, saved only after Emma said yes."
    ctc = ConversationalTestCase(turns=turns, **kw)
    for n in ("ConversationCompletenessMetric", "KnowledgeRetentionMetric", "TurnRelevancyMetric"):
        try:
            met = getattr(M, n)(model=m, threshold=0.5, async_mode=False)
            met.measure(ctc)
            out[n] = {"score": met.score, "reason": (met.reason or "")[:200]}
        except Exception as e:  # noqa: BLE001
            out[n] = f"ERR {type(e).__name__}: {str(e)[:300]}"
    try:
        g = M.ConversationalGEval(name="Asked before saving", criteria="The assistant showed a preview and saved the request only after the user agreed.",
                                  model=m, threshold=0.5, async_mode=False)
        g.measure(ctc)
        out["ConversationalGEval"] = {"score": g.score, "reason": (g.reason or "")[:200]}
    except Exception as e:  # noqa: BLE001
        out["ConversationalGEval"] = f"ERR {type(e).__name__}: {str(e)[:300]}"
except Exception:  # noqa: BLE001
    print("deepeval probe failed:", traceback.format_exc()[-1500:])
print(json.dumps(out, indent=1))

out = {}
try:
    import ragas
    print("ragas", ragas.__version__)
    import ragas.metrics as RM
    print("ragas.metrics:", [n for n in dir(RM) if n[0].isupper()][:80])
    try:
        import ragas.metrics.collections as RC
        print("ragas.metrics.collections:", [n for n in dir(RC) if n[0].isupper()][:80])
    except Exception as e:  # noqa: BLE001
        print("no collections:", e)
    from ragas.dataset_schema import MultiTurnSample, SingleTurnSample
    print("SingleTurnSample fields:", list(SingleTurnSample.model_fields))
    print("MultiTurnSample fields:", list(MultiTurnSample.model_fields))
    import ragas.messages as MSG
    print("messages:", [n for n in dir(MSG) if n[0].isupper()])
    import ragas.llms as RL
    print("llms:", [n for n in dir(RL) if not n.startswith("_")])
    print("llm_factory", sig(RL.llm_factory)[:500])
    for n in ("Faithfulness", "LLMContextPrecisionWithReference", "LLMContextRecall", "ToolCallAccuracy", "AgentGoalAccuracyWithReference", "AgentGoalAccuracyWithoutReference", "TopicAdherenceScore"):
        if hasattr(RM, n):
            print(n, sig(getattr(RM, n).__init__)[:300])
    from langchain_anthropic import ChatAnthropic
    from ragas.llms import LangchainLLMWrapper
    llm = LangchainLLMWrapper(ChatAnthropic(model="claude-haiku-5-5", max_tokens=2000))
    import asyncio
    s = SingleTurnSample(user_input="How much budget is left on PRD-03?", response="£680,000 is left on PRD-03 this quarter.",
                         retrieved_contexts=["check_budget: PRD-03 Cargo e-bike line, open, budget_left 680000.0"],
                         reference="£680,000 is left on PRD-03.")
    for n in ("Faithfulness", "LLMContextPrecisionWithReference", "LLMContextRecall"):
        try:
            met = getattr(RM, n)(llm=llm)
            out[n] = asyncio.run(met.single_turn_ascore(s))
        except Exception as e:  # noqa: BLE001
            out[n] = f"ERR {type(e).__name__}: {str(e)[:400]}"
    from ragas.messages import AIMessage, HumanMessage, ToolCall, ToolMessage
    mt = MultiTurnSample(user_input=[HumanMessage(content="How many BAT-500 do we have?"),
                                     AIMessage(content="", tool_calls=[ToolCall(name="check_stock", args={"item_code": "BAT-500"})]),
                                     ToolMessage(content='{"free_total": 6600}'),
                                     AIMessage(content="6,600 free: 5,400 in Manchester and 1,200 in Leeds.")],
                         reference_tool_calls=[ToolCall(name="check_stock", args={"item_code": "BAT-500"})],
                         reference="The assistant reports 6,600 BAT-500 in stock from the stock check.")
    for n in ("ToolCallAccuracy", "AgentGoalAccuracyWithReference"):
        try:
            met = getattr(RM, n)() if n == "ToolCallAccuracy" else getattr(RM, n)(llm=llm)
            out[n] = asyncio.run(met.multi_turn_ascore(mt))
        except Exception as e:  # noqa: BLE001
            out[n] = f"ERR {type(e).__name__}: {str(e)[:400]}"
except Exception:  # noqa: BLE001
    print("ragas probe failed:", traceback.format_exc()[-1500:])
print(json.dumps(out, indent=1, default=str))
