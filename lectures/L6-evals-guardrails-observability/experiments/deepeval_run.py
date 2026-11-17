"""DeepEval on our recorded runs (Lecture 6, Section 2), Claude Haiku as the judge (deepeval.models.AnthropicModel).

    tools/mrun.sh .../l6_modal.py --script deepeval_run.py --image evals

1. ToolCorrectnessMetric (deterministic: tool names) on the suite's tool-use tasks, every recorded run (good k=3,
   Thursday k=1): did the agent call the tool the task needs?
2. GEval (an LLM judge DeepEval builds from a criterion: it writes evaluation steps, then scores 0-1) on the 56-item
   calibration set (40 real replies, 16 planted wrong), with the tool results as context; agreement with the labels.
Nothing new is asked of the agent: these are the same replies the suite recorded. Writes logs/deepeval_run.json and a
terminal screenshot of DeepEval's own output (figs/deepeval/*.png).
"""
import io
import json
import contextlib

from _common import FIGS, LOGS, now, pmap, spend, write

import deepeval
from deepeval import evaluate
from deepeval.metrics import GEval, ToolCorrectnessMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall

from ledgerline.course.l6 import calibration as CAL
from ledgerline.course.l6.suite import BY_ID

MODEL = AnthropicModel(model="claude-haiku-5-5")
EXPECT = {"T04": "check_stock", "T07": "find_supplier", "T11": "check_budget", "T12": "expiring_certificates",
          "T13": "low_stock", "T19": "list_open_orders", "T15": "send_message"}
rows = {}
for tag, f in (("good", "suite_good_k3.json"), ("thursday", "suite_thursday_k1.json")):
    for r in json.loads((LOGS / f).read_text())["rows"]:
        rows[(tag, r["task"], r["rep"])] = r

# 1 · tool correctness, deterministic
tool_cases = []
for (tag, t, rep), r in sorted(rows.items()):
    if t in EXPECT:
        called = [ToolCall(name=c["tool"], input_parameters=c["args"]) for tt in r["turns"] for c in tt["calls"]]
        tool_cases.append(((tag, t, rep), LLMTestCase(input=" / ".join(BY_ID[t]["turns"]), actual_output=r["turns"][-1]["reply"] or "",
                                                     tools_called=called, expected_tools=[ToolCall(name=EXPECT[t])])))
buf = io.StringIO()
tool_rows = []
for k, tc in tool_cases:
    m = ToolCorrectnessMetric(threshold=1.0, model=MODEL)
    m.measure(tc)
    tool_rows.append({"id": "/".join(map(str, k)), "expected": EXPECT[k[1]], "score": m.score, "pass": m.success,
                      "reason": (m.reason or "")[:200]})

# 2 · GEval on the calibration set (the same 56 items the hand-built judges were measured on)
items = []
for k in CAL.REAL:
    r = rows[k]
    items.append({"id": "/".join(map(str, k)), "task": k[1], "reply": r["turns"][-1]["reply"], "label": True, "ev": r["evidence"]})
for base, old, new in CAL.PLANTED:
    rep = rows[base]["turns"][-1]["reply"]
    if old in rep:
        items.append({"id": "planted:" + "/".join(map(str, base)), "task": base[1], "reply": rep.replace(old, new), "label": False,
                      "ev": rows[base]["evidence"]})
metrics_by_task = {}


def geval_for(task):
    if task not in metrics_by_task:
        metrics_by_task[task] = BY_ID[task]["words"]
    return GEval(name=f"Words {task}", criteria=BY_ID[task]["words"] + " Use only the context (what the ERP tools returned); a "
                 "number or name not in the context is not supported.",
                 evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
                 model=MODEL, threshold=0.5, async_mode=False)


def one(it):
    tc = LLMTestCase(input=" / ".join(BY_ID[it["task"]]["turns"]), actual_output=it["reply"],
                     context=[json.dumps(e, ensure_ascii=False)[:2500] for e in it["ev"]][:10])
    errs = []
    for attempt in range(3):   # Haiku sometimes leaves "score" out of the JSON DeepEval asks for: count it, retry
        g = geval_for(it["task"])
        try:
            g.measure(tc)
            return {"id": it["id"], "label": it["label"], "score": g.score, "pass": bool(g.success), "reason": (g.reason or "")[:300],
                    "cost": getattr(g, "evaluation_cost", None), "attempts": attempt + 1, "first_errors": errs}
        except Exception as e:  # noqa: BLE001
            errs.append(f"{type(e).__name__}: {str(e)[:160]}")
    return {"id": it["id"], "label": it["label"], "error": errs[-1], "attempts": 3, "first_errors": errs}


grows = pmap(one, items, workers=8)
ok = [g for g in grows if "error" not in g]
lab = [g["label"] for g in ok]
pred = [g["pass"] for g in ok]
n = len(ok) or 1
po = sum(a == b for a, b in zip(lab, pred)) / n
pa, pb = sum(lab) / n, sum(pred) / n
pe = pa * pb + (1 - pa) * (1 - pb)
gsum = {"items": len(ok), "errors": len(grows) - len(ok), "first_try_errors": sum(1 for g in grows if g.get("first_errors")),
        "calls_total": sum(g.get("attempts", 1) for g in grows), "agreement": round(po, 3), "kappa": round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0,
        "caught_planted": sum(1 for l, p in zip(lab, pred) if not l and not p), "planted": lab.count(False),
        "false_alarms": sum(1 for l, p in zip(lab, pred) if l and not p), "real": lab.count(True)}

# DeepEval's own report for a few of them, as the terminal shows it (evaluate prints a results table)
with contextlib.redirect_stdout(buf):
    sample = [LLMTestCase(input=" / ".join(BY_ID[it["task"]]["turns"]), actual_output=it["reply"],
                          context=[json.dumps(e, ensure_ascii=False)[:2500] for e in it["ev"]][:10])
              for it in [items[0], items[4], items[40], items[41]] if True]
    try:
        evaluate(test_cases=sample[:2], metrics=[geval_for("T04")])
    except Exception as e:  # noqa: BLE001
        print("evaluate error:", type(e).__name__, str(e)[:300])
term = buf.getvalue()
(LOGS / "deepeval_evaluate.txt").write_text(term)
usd = sum((g.get("cost") or 0) for g in ok)
out = {"at": now(), "deepeval": deepeval.__version__, "judge": "claude-haiku-5-5 (AnthropicModel)",
       "tool_correctness": {"runs": len(tool_rows), "passed": sum(1 for t in tool_rows if t["pass"]), "rows": tool_rows},
       "geval": {**gsum, "rows": grows}, "usd": round(usd, 5)}
write("deepeval_run.json", out)
spend("deepeval_geval", usd, 2 * len(items), 0, 0, "claude-haiku-5-5", "GEval on the calibration set (DeepEval's cost estimate)")
print(json.dumps({"tool": out["tool_correctness"]["passed"], "of": out["tool_correctness"]["runs"], "geval": gsum}, indent=1))
print(term[-3000:])
