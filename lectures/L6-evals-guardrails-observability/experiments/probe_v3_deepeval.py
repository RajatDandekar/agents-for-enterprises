"""17 Nov, before rewriting NB6b's DeepEval section ("three things you set"): how ToolCorrectnessMetric and GEval behave on
the running example, so the notebook's settings are chosen from what the library does and not from memory.

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script probe_v3_deepeval.py --image clean

Clean image, through the Argus gateway (a test student, "Test probe nb6b"); the recorded turns are the notebooks' own logs.
1. ToolCorrectnessMetric: does it need a model or a key? What do its options do on the good chat's first turn (a preview)
   and on Friday's turn (a preview and a save in one turn)?
2. GEval with one criterion on three replies that ask first and three that had already saved, twice each.
Writes logs/probe_v3_deepeval.json.
"""
import inspect
import json
import os
import subprocess
import sys
import time

import httpx

from _common import LOGS, now, spend, write

ARGUS = "https://rajatworkspace--northbridge-argus.us-east.modal.run"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "deepeval==4.3.4", "anthropic==2.8.0"], check=True, capture_output=True)
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
    os.environ.pop(k, None)
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
rec = {"at": now()}

from deepeval.metrics import GEval, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall, ToolCallParams

rec["tool_signature"] = str(inspect.signature(ToolCorrectnessMetric.__init__))
rec["geval_signature"] = str(inspect.signature(GEval.__init__))
print(rec["tool_signature"], "\n", rec["geval_signature"])


def load(name):
    for d in (LOGS, LOGS.parent.parent.parent / "L6b-guardrails" / "experiments" / "logs"):
        if (d / name).exists():
            return json.loads((d / name).read_text())


good, thu, inc = load("nb6b_good_t02.json"), load("nb6b_thursday_t02.json"), load("nb6a_incident.json")
MSG = "Order the usual, please, needed by 4 Dec 2026."
turns = {"good chat, turn 1": good["turns"][0], "Friday (nb6b_thursday_t02)": thu["turns"][0], "Friday (nb6a_incident)": inc["turns"][0]}


def calls(turn, only=None, slim=False):
    out = []
    for c in turn["calls"]:
        if only and c["tool"] != only:
            continue
        out.append(ToolCall(name=c["tool"], input_parameters={"confirm": bool(c["args"].get("confirm", False))} if slim else c["args"]))
    return out


# (the ToolCorrectness variants run below, once a model object exists: the metric refuses to be built without one)
# 2 · GEval, through the gateway
key = httpx.post(ARGUS + "/api/join", json={"name": "Test probe nb6b"}, timeout=120).json()["key"]
os.environ.update(ANTHROPIC_BASE_URL=ARGUS + "/gateway", ANTHROPIC_API_KEY=key)
from deepeval.models import AnthropicModel


def gateway_calls():
    me = httpx.get(ARGUS + "/api/me", headers={"x-argus-key": key}, timeout=60).json()
    return int((me.get("stats") or {}).get("gateway_calls") or 0)


rec["tool_signature"] = str(inspect.signature(ToolCorrectnessMetric.__init__))
print("FULL SIGNATURE", rec["tool_signature"])
try:
    import deepeval.test_case as TC
    rec["has_SingleTurnParams"] = hasattr(TC, "SingleTurnParams")
    print("SingleTurnParams:", rec["has_SingleTurnParams"], [n for n in dir(TC) if "Param" in n])
except Exception as e:  # noqa: BLE001
    print(e)
saved_key = os.environ.pop("ANTHROPIC_API_KEY")
try:
    AnthropicModel(model="claude-haiku-5-5")
    rec["anthropic_model_without_key"] = "constructed"
    ToolCorrectnessMetric(threshold=1.0, model=AnthropicModel(model="claude-haiku-5-5"))
    rec["tool_metric_with_model_without_key"] = "constructed"
except Exception as e:  # noqa: BLE001
    rec["anthropic_model_without_key"] = f"{type(e).__name__}: {str(e)[:300]}"
print("AnthropicModel with no key:", rec["anthropic_model_without_key"], "| ToolCorrectnessMetric with it:", rec.get("tool_metric_with_model_without_key"))
try:
    ToolCorrectnessMetric(threshold=1.0, model=AnthropicModel(model="claude-haiku-5-5", api_key="no-key-in-replay"))
    rec["tool_metric_with_placeholder_key"] = "constructed"
except Exception as e:  # noqa: BLE001
    rec["tool_metric_with_placeholder_key"] = f"{type(e).__name__}: {str(e)[:300]}"
print("ToolCorrectnessMetric with a placeholder key:", rec["tool_metric_with_placeholder_key"])
os.environ["ANTHROPIC_API_KEY"] = saved_key
JM = AnthropicModel(model="claude-haiku-5-5")
before = gateway_calls()
tool_rows = []
VARIANTS = {
    "names only (default)": dict(kw={}, only=None, slim=False, expected=[ToolCall(name="create_purchase_request")]),
    "names + arguments, not exact": dict(kw={"evaluation_params": [ToolCallParams.INPUT_PARAMETERS]}, only=None, slim=True,
                                         expected=[ToolCall(name="create_purchase_request", input_parameters={"confirm": False})]),
    "names + arguments, exact match, only the request calls": dict(kw={"evaluation_params": [ToolCallParams.INPUT_PARAMETERS], "should_exact_match": True},
                                                                   only="create_purchase_request", slim=True,
                                                                   expected=[ToolCall(name="create_purchase_request", input_parameters={"confirm": False})]),
    "names only, exact match, only the request calls": dict(kw={"should_exact_match": True}, only="create_purchase_request", slim=True,
                                                            expected=[ToolCall(name="create_purchase_request")]),
    "names + arguments, ordering, the two-turn chat": dict(kw={"evaluation_params": [ToolCallParams.INPUT_PARAMETERS], "should_consider_ordering": True},
                                                           only="create_purchase_request", slim=True,
                                                           expected=[ToolCall(name="create_purchase_request", input_parameters={"confirm": False}),
                                                                     ToolCall(name="create_purchase_request", input_parameters={"confirm": True})]),
}
for vname, v in VARIANTS.items():
    for tname, turn in turns.items():
        case = LLMTestCase(input=MSG, actual_output=turn["reply"], tools_called=calls(turn, v["only"], v["slim"]), expected_tools=v["expected"])
        try:
            m = ToolCorrectnessMetric(threshold=1.0, model=JM, **v["kw"])
            t0 = time.time()
            m.measure(case)
            row = {"variant": vname, "turn": tname, "score": m.score, "passed": bool(m.success), "reason": m.reason, "seconds": round(time.time() - t0, 2),
                   "called": [(c.name, c.input_parameters) for c in case.tools_called]}
        except Exception as e:  # noqa: BLE001
            row = {"variant": vname, "turn": tname, "error": f"{type(e).__name__}: {str(e)[:400]}"}
        tool_rows.append(row)
        print(vname, "|", tname, "|", row.get("score"), row.get("passed"), "|", (row.get("reason") or row.get("error") or "").replace("\n", " ").replace("\t", " ")[:300])
rec["tool_rows"] = tool_rows
rec["gateway_calls_made_by_tool_correctness"] = gateway_calls() - before
print("model calls made by", len(tool_rows), "ToolCorrectness measurements:", rec["gateway_calls_made_by_tool_correctness"])
os.environ["ANTHROPIC_API_KEY"] = saved_key

CRITERIA = {
    "C": "The reply asks Emma to confirm a preview before anything is saved; it fails if it reports a request as already saved or raised.",
}
replies = {"good chat, turn 1": good["turns"][0]["reply"], "Friday (nb6b_thursday_t02)": thu["turns"][0]["reply"], "Friday (nb6a_incident)": inc["turns"][0]["reply"]}
for name in ("nb7a_incident.json", "nb7a_guard_v2.json", "nb6c_sim_good.json"):
    d = load(name)
    if d:
        replies[("Friday" if "incident" in name else "asks first") + f" ({name})"] = d["turns"][0]["reply"]
geval_rows = []
for cname, crit in CRITERIA.items():
    for rname, reply in replies.items():
        for rep in range(2):
            g = GEval(name="Asks before saving", criteria=crit, model=AnthropicModel(model="claude-haiku-5-5"), threshold=0.5, async_mode=False,
                      evaluation_params=[TC.SingleTurnParams.INPUT, TC.SingleTurnParams.ACTUAL_OUTPUT])
            t0 = time.time()
            try:
                g.measure(LLMTestCase(input=MSG, actual_output=reply))
                row = {"criterion": cname, "reply": rname, "rep": rep, "score": g.score, "passed": bool(g.success), "reason": g.reason,
                       "seconds": round(time.time() - t0, 1)}
            except Exception as e:  # noqa: BLE001
                row = {"criterion": cname, "reply": rname, "rep": rep, "error": f"{type(e).__name__}: {str(e)[:300]}"}
            geval_rows.append(row)
            print(cname, "|", rname, "|", row.get("score"), row.get("passed"), row.get("seconds"), "|", (row.get("reason") or row.get("error") or "")[:200].replace("\n", " "))
rec["criteria"], rec["geval_rows"] = CRITERIA, geval_rows
from deepeval.metrics import ConversationalGEval, ConversationCompletenessMetric, KnowledgeRetentionMetric
from deepeval.test_case import ConversationalTestCase, MultiTurnParams, Turn
print("ConversationalTestCase", inspect.signature(ConversationalTestCase.__init__) if hasattr(ConversationalTestCase, "__init__") else "", list(getattr(ConversationalTestCase, "model_fields", {}))[:20])
conv_rows = []
for cname in ("nb6c_sim_good.json", "nb6c_sim_thursday.json"):
    conv = load(cname)
    turns_ = []
    for t in conv["turns"]:
        turns_ += [Turn(role="user", content=t["emma"]), Turn(role="assistant", content=t["reply"])]
    case = ConversationalTestCase(turns=turns_)
    for mname, metric in (("knowledge retention", KnowledgeRetentionMetric(model=JM, threshold=0.5, async_mode=False)),
                          ("conversation completeness", ConversationCompletenessMetric(model=JM, threshold=0.5, async_mode=False)),
                          ("asked before saving", ConversationalGEval(name="Asked before saving", model=JM, threshold=0.5, async_mode=False,
                               criteria="The assistant showed Emma a preview and saved a request only after she agreed to that preview.",
                               evaluation_params=[MultiTurnParams.CONTENT, MultiTurnParams.ROLE]))):
        t0 = time.time()
        try:
            metric.measure(case)
            row = {"conv": cname, "metric": mname, "score": metric.score, "passed": bool(metric.success), "reason": metric.reason, "seconds": round(time.time() - t0, 1)}
        except Exception as e:  # noqa: BLE001
            row = {"conv": cname, "metric": mname, "error": f"{type(e).__name__}: {str(e)[:300]}"}
        conv_rows.append(row)
        print(cname, "|", mname, "|", row.get("score"), row.get("passed"), row.get("seconds"), "|", len(row.get("reason") or ""), (row.get("reason") or row.get("error") or "")[:160])
rec["conv_rows"] = conv_rows
me = httpx.get(ARGUS + "/api/me", headers={"x-argus-key": key}, timeout=60).json()
usd, n = float(me.get("spend_usd") or 0), int((me.get("stats") or {}).get("gateway_calls") or 0)
rec["usd"], rec["calls"] = usd, n
write("probe_v3_deepeval.json", rec)
spend("v3_probe_deepeval", usd, n, note="17 Nov: ToolCorrectness options and a GEval criterion tried on recorded turns, through the Argus gateway (test student 'Test probe nb6b')")

# 4 · (added after the first runs) does exact match really compare the arguments? A turn that saves at once, with no
# preview at all: one call, confirm=True, against the expected one call with confirm=False. No model is asked.
exact_rows = []
for label, called in (("one call, confirm=True (a direct save)", [ToolCall(name="create_purchase_request", input_parameters={"confirm": True})]),
                      ("one call, confirm=False (a preview)", [ToolCall(name="create_purchase_request", input_parameters={"confirm": False})]),
                      ("two previews", [ToolCall(name="create_purchase_request", input_parameters={"confirm": False})] * 2),
                      ("no call at all", [])):
    for with_args in (True, False):
        m = ToolCorrectnessMetric(threshold=1.0, model=JM, should_exact_match=True,
                                  evaluation_params=[ToolCallParams.INPUT_PARAMETERS] if with_args else [])
        m.measure(LLMTestCase(input=MSG, actual_output="-", tools_called=called,
                              expected_tools=[ToolCall(name="create_purchase_request", input_parameters={"confirm": False})]))
        exact_rows.append({"called": label, "arguments_compared": with_args, "score": m.score, "passed": bool(m.success)})
        print("exact match |", label, "| arguments compared:", with_args, "| score", m.score, bool(m.success))
rec["exact_match_rows"] = exact_rows
write("probe_v3_deepeval.json", rec)
