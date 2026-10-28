"""Introspect the pinned SDKs' APIs on Modal (no keys used), so our code matches the versions we pin."""
import json, pathlib, modal
PINS = ["langfuse==4.17.0", "deepeval==4.2.8", "ragas==0.4.3", "langchain-community==0.3.31",
        "opentelemetry-sdk==1.45.1", "opentelemetry-exporter-otlp-proto-http==1.45.1", "openai"]
app = modal.App("l10-explore", image=modal.Image.debian_slim(python_version="3.11").pip_install(*PINS))
CODE = r'''
import inspect, importlib, json
out = {}
def sig(path):
    mod, _, attr = path.rpartition(":")
    try:
        o = importlib.import_module(mod)
        for a in attr.split("."):
            o = getattr(o, a)
        s = ""
        try: s = str(inspect.signature(o))
        except Exception: pass
        doc = (inspect.getdoc(o) or "")[:900]
        out[path] = {"sig": s, "doc": doc}
        if inspect.isclass(o):
            out[path]["methods"] = [m for m in dir(o) if not m.startswith("_")][:120]
    except Exception as e:
        out[path] = {"error": repr(e)[:300]}
for p in ["langfuse:get_client", "langfuse:observe", "langfuse:Langfuse", "langfuse:Langfuse.start_as_current_observation",
          "langfuse:Langfuse.start_as_current_span", "langfuse:Langfuse.create_score", "langfuse:Langfuse.create_dataset",
          "langfuse:Langfuse.create_dataset_item", "langfuse:Langfuse.create_prompt", "langfuse:Langfuse.get_prompt",
          "langfuse:Langfuse.get_trace_url", "langfuse:Langfuse.set_current_trace_as_public", "langfuse:Langfuse.update_current_trace",
          "langfuse:Langfuse.flush", "langfuse:Langfuse.run_experiment", "langfuse:Langfuse.get_dataset", "langfuse:propagate_attributes",
          "deepeval.models:DeepEvalBaseLLM", "deepeval.metrics:GEval", "deepeval.metrics:ToolCorrectnessMetric", "deepeval.metrics:BaseMetric",
          "deepeval.test_case:LLMTestCase", "deepeval.test_case:ToolCall", "deepeval:assert_test", "deepeval:evaluate",
          "deepeval.test_case:LLMTestCaseParams",
          "ragas:evaluate", "ragas.metrics:IDBasedContextRecall", "ragas.metrics:IDBasedContextPrecision", "ragas.metrics:Faithfulness",
          "ragas.metrics:LLMContextRecall", "ragas.metrics:LLMContextPrecisionWithReference", "ragas.metrics:ResponseRelevancy",
          "ragas.metrics:FactualCorrectness", "ragas.llms:llm_factory", "ragas.llms:LangchainLLMWrapper", "ragas:EvaluationDataset",
          "ragas:SingleTurnSample", "ragas.llms:InstructorLLM", "ragas.metrics.collections:Faithfulness", "ragas.metrics.collections:ContextRecall",
          ]:
    sig(p)
import ragas.metrics as rm, ragas.llms as rl
out["ragas.metrics.__all__"] = sorted(getattr(rm, "__all__", dir(rm)))[:200]
out["ragas.llms.__all__"] = sorted(getattr(rl, "__all__", dir(rl)))
try:
    import ragas.metrics.collections as rc; out["ragas.metrics.collections"] = sorted(dir(rc))[:200]
except Exception as e: out["ragas.metrics.collections"] = repr(e)
import deepeval.models as dm; out["deepeval.models"] = sorted(dir(dm))
import deepeval.metrics as dmm; out["deepeval.metrics"] = sorted(dir(dmm))
import langfuse, os, glob
root = os.path.dirname(langfuse.__file__)
hits = []
for f in glob.glob(root + "/**/*.py", recursive=True):
    for i, l in enumerate(open(f, errors="ignore")):
        if "langfuse." in l and ("=" in l) and ('"langfuse.' in l or "'langfuse." in l):
            hits.append(f.replace(root, "") + ":" + str(i) + ": " + l.strip()[:160])
out["langfuse_attr_lines"] = hits[:200]
import subprocess, sys
out["pip_freeze"] = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
print(json.dumps(out))
'''
@app.function(timeout=600)
def explore():
    import subprocess, sys
    p = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True)
    return p.stdout[-400000:], p.stderr[-4000:]
@app.local_entrypoint()
def main():
    o, e = explore.remote()
    (pathlib.Path(__file__).parent / "logs" / "_api_explore.json").write_text(o or "{}")
    print(e[-2000:])
