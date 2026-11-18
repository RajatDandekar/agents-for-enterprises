"""DeepEval for Argus, run as its own process (Argus v3, Lecture 6). It never runs inside Argus.

    echo '{"mode": "single", ...}' | python deepeval_runner.py        # prints one line: @@RESULT@@{...json...}

Argus sends a small JSON on stdin and reads the result from stdout. On Modal this file runs inside the function
`deepeval_run` of deploy/argus_modal.py (its own image: deepeval==4.3.4, anthropic==2.8.0, nothing of the course), one
process per request, so a crash or a hang here cannot touch the lab, and each request has its own environment: the
student's Argus key is the Anthropic key and Argus's gateway is the Anthropic address, so only the course's two models are
reachable and every call is charged to that student's budget. Telemetry and error reporting are switched off.

mode "single"         one LLMTestCase and one metric, as NB6b builds them:
                      metric "tool"   ToolCorrectnessMetric(threshold, evaluation_params=[INPUT_PARAMETERS] if "args",
                                      should_exact_match="exact")              the tools called against the expected tools
                      metric "geval"  GEval(name, criteria, threshold)          a judge DeepEval builds from a criterion;
                                      it reads the input and the actual output, and the context if one is sent
mode "conversation"   one ConversationalTestCase and three metrics, as NB6c builds them: KnowledgeRetentionMetric,
                      ConversationCompletenessMetric, ConversationalGEval(name, criteria)
A small judge model sometimes breaks the JSON shape DeepEval asks for (15 of 56 first tries in our recorded run), so a
model-based metric is tried up to three times; the number of tries is reported.
This file imports nothing from the course, so it can be read on its own.
"""
import contextlib
import json
import os
import sys
import tempfile
import time

MARK = "@@RESULT@@"


def _clean(s: str) -> str:
    """An error text for the page: never a key."""
    import re
    return re.sub(r"(ar-|sk-)[A-Za-z0-9_-]{6,}", r"\1…", s or "")


def _measure(make, case, tries: int = 3) -> dict:
    errs = []
    for attempt in range(1, tries + 1):
        m = make()
        try:
            m.measure(case)
            reason = str(m.reason or "").strip()
            if reason.startswith("[") and reason.endswith("]"):          # some metrics wrap their reason in brackets (nbkit.measure)
                reason = reason[1:-1]
            return {"score": m.score, "passed": bool(m.is_successful()), "reason": " ".join(reason.split()), "threshold": m.threshold,
                    "attempts": attempt, "first_errors": errs}
        except Exception as e:  # noqa: BLE001
            errs.append(_clean(f"{type(e).__name__}: {str(e)[:240]}"))
    return {"error": errs[-1], "attempts": tries, "first_errors": errs}


def single(p: dict) -> list:
    from deepeval.metrics import GEval, ToolCorrectnessMetric
    from deepeval.models import AnthropicModel
    from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams
    try:
        from deepeval.test_case import SingleTurnParams as P        # its name in 4.3.4 (NB6b)
    except ImportError:
        from deepeval.test_case import LLMTestCaseParams as P       # its older name
    c = p["case"]
    model = AnthropicModel(model=p.get("model") or "claude-haiku-5-5")

    def calls(xs):
        return [ToolCall(name=t["name"], **({"input_parameters": t["input_parameters"]} if t.get("input_parameters") else {})) for t in xs or []]
    kw = {"context": c["context"]} if c.get("context") else {}
    case = LLMTestCase(input=c["input"], actual_output=c["actual_output"], tools_called=calls(c.get("tools_called")),
                       expected_tools=calls(c.get("expected_tools")), **kw)
    thr = float(p.get("threshold", 0.5))
    if p["metric"] == "tool":
        sw = {"evaluation_params": [ToolCallParams.INPUT_PARAMETERS]} if p.get("args", True) else {}
        r = _measure(lambda: ToolCorrectnessMetric(model=model, threshold=thr, should_exact_match=bool(p.get("exact", True)), **sw), case, tries=1)
        return [{"name": "ToolCorrectnessMetric", **r}]
    params = [P.INPUT, P.ACTUAL_OUTPUT] + ([P.CONTEXT] if kw else [])
    r = _measure(lambda: GEval(name=p.get("name") or "My criterion", criteria=p["criterion"], model=model, threshold=thr,
                               evaluation_params=params, async_mode=False), case)
    return [{"name": f"GEval · {p.get('name') or 'My criterion'}", **r}]


def conversation(p: dict) -> list:
    from deepeval.metrics import ConversationalGEval, ConversationCompletenessMetric, KnowledgeRetentionMetric
    from deepeval.models import AnthropicModel
    from deepeval.test_case import ConversationalTestCase, MultiTurnParams, Turn
    model = AnthropicModel(model=p.get("model") or "claude-haiku-5-5")
    turns = []
    for t in p["turns"]:
        turns += [Turn(role="user", content=t["emma"]), Turn(role="assistant", content=t["reply"] or "")]
    case = ConversationalTestCase(turns=turns, scenario=p.get("scenario") or "", expected_outcome=p.get("expected_outcome") or "")
    thr = float(p.get("threshold", 0.5))
    out = []
    for name, make in (
            ("Knowledge retention", lambda: KnowledgeRetentionMetric(model=model, threshold=thr, async_mode=False)),
            ("Conversation completeness", lambda: ConversationCompletenessMetric(model=model, threshold=thr, async_mode=False)),
            (f"ConversationalGEval · {p.get('name') or 'My criterion'}", lambda: ConversationalGEval(
                name=p.get("name") or "My criterion", model=model, threshold=thr, async_mode=False, criteria=p["criterion"],
                evaluation_params=[MultiTurnParams.CONTENT, MultiTurnParams.ROLE]))):
        out.append({"name": name, **_measure(make, case)})
    return out


def main() -> dict:
    p = json.loads(sys.stdin.read())
    os.environ.update({"DEEPEVAL_TELEMETRY_OPT_OUT": "YES", "ERROR_REPORTING": "NO", "DEEPEVAL_UPDATE_WARNING_OPT_OUT": "YES",
                       "DEEPEVAL_FILE_SYSTEM": "READ_ONLY"})
    if p.get("gateway") and p.get("key"):
        os.environ["ANTHROPIC_BASE_URL"], os.environ["ANTHROPIC_API_KEY"] = p["gateway"], p["key"]
    os.chdir(tempfile.mkdtemp(prefix="deepeval_"))       # DeepEval keeps small files beside the script: give it its own folder
    t0 = time.time()
    try:
        with contextlib.redirect_stdout(sys.stderr):     # DeepEval prints progress; stdout carries only the result
            import deepeval
            results = single(p) if p.get("mode", "single") == "single" else conversation(p)
        return {"ok": True, "deepeval": deepeval.__version__, "results": results, "seconds": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": _clean(f"{type(e).__name__}: {str(e)[:300]}"), "seconds": round(time.time() - t0, 1)}


def run_subprocess(payload: dict, python: str = sys.executable, timeout: int = 240) -> dict:
    """What a caller does: this script in a process of its own, the payload on stdin, the result read from stdout."""
    import subprocess
    try:
        r = subprocess.run([python, os.path.abspath(__file__)], input=json.dumps(payload), capture_output=True, text=True,
                           timeout=timeout, env={k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENAI_"))})
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"DeepEval did not answer within {timeout} seconds."}
    line = next((ln for ln in reversed(r.stdout.splitlines()) if ln.startswith(MARK)), None)
    if line is None:
        return {"ok": False, "error": _clean("DeepEval stopped without a result: " + (r.stderr or "")[-300:].replace("\n", " "))}
    return json.loads(line[len(MARK):])


if __name__ == "__main__":
    print(MARK + json.dumps(main(), default=str))
