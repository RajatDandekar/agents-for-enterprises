"""Run NeMo Guardrails' self-check input rail on a list of texts (runs in its own venv: /opt/nemo/bin/python).

    /opt/nemo/bin/python nemo_check.py in.json out.json
in.json: [{"id", "text"}]; out.json: [{"id", "blocked", "ms", "llm_calls", "tokens_in", "tokens_out", "error"}]
Only the input rails run (options rails=["input"]): the main model is never called, so the cost is the checker's.
"""
import json
import os
import sys
import time

os.environ.setdefault("NEMOGUARDRAILS_LLM_FRAMEWORK", "langchain")

# Compatibility shim (measured 16 Nov 2026): NeMo's self-check rails call the model with a very low temperature, and the
# current Claude models refuse sampling parameters ("temperature: Extra inputs are not permitted"). Drop them from every
# request body the Anthropic SDK builds, whichever code path (LangChain, NeMo) made the call.
import anthropic._base_client as _B  # noqa: E402

_orig_build = _B.BaseClient._build_request


def _build_request(self, options, *a, **kw):
    jd = getattr(options, "json_data", None)
    if isinstance(jd, dict):
        for k in ("temperature", "top_p", "top_k"):
            jd.pop(k, None)
    return _orig_build(self, options, *a, **kw)


_B.BaseClient._build_request = _build_request
from nemoguardrails import LLMRails, RailsConfig  # noqa: E402

cfg = RailsConfig.from_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nemo"))
rails = LLMRails(cfg)
items = json.load(open(sys.argv[1]))
out = []
for it in items:
    t0 = time.perf_counter()
    try:
        r = rails.generate(messages=[{"role": "user", "content": it["text"]}],
                           options={"rails": ["input"], "log": {"activated_rails": True, "llm_calls": True}})
        log = r.log
        stopped = any(getattr(a, "stop", False) for a in (log.activated_rails or []))
        calls = log.llm_calls or []
        tin = sum((getattr(c, "prompt_tokens", 0) or 0) for c in calls)
        tout = sum((getattr(c, "completion_tokens", 0) or 0) for c in calls)
        raw = [getattr(c, "completion", "") for c in calls]
        out.append({"id": it["id"], "blocked": bool(stopped), "ms": round((time.perf_counter() - t0) * 1000, 1),
                    "llm_calls": len(calls), "tokens_in": tin, "tokens_out": tout, "raw": raw[:1],
                    "response": (r.response[-1]["content"] if isinstance(r.response, list) and r.response else str(r.response))[:200]})
    except Exception as e:  # noqa: BLE001
        out.append({"id": it["id"], "blocked": None, "error": f"{type(e).__name__}: {str(e)[:300]}",
                    "ms": round((time.perf_counter() - t0) * 1000, 1)})
    print(it["id"], out[-1].get("blocked"), out[-1].get("ms"), out[-1].get("error", ""), flush=True)
json.dump(out, open(sys.argv[2], "w"), indent=1)
