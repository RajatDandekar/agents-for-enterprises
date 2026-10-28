"""Lecture 8 demo: a model gateway in code. LiteLLM's Router with a fallback, and the same question to four models
through one API (OpenRouter), on the gasket preview Kavita sees.

    tools/mrun.sh lectures/L8-frameworks/experiments/run_modal.py --script lectures/L8-frameworks/experiments/exp_gateway.py

Every call goes through our meter (cassette IND8_gateway), so the notebook replays it with no key.
Writes logs/gateway.json.
"""
import json
import os
import pathlib
import sys
import time

import httpx  # noqa: F401
import openai  # noqa: F401

from bahi.course.frameworks.meter import Meter

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
meter = Meter(cassette="IND8_gateway").start()
KEY = os.environ.get("OPENROUTER_API_KEY", "replay")
Q = [{"role": "system", "content": "You are Ask Rasoi at Rasoi Steel Works. Answer in two sentences."},
     {"role": "user", "content": "A purchase order for 20,000 gaskets at Rs 11.90 each, plus 18% GST. What is the gross "
                                 "value, and is it above Kavita's approval limit of Rs 2,50,000?"}]
out = {"question": Q[1]["content"], "models": [], "router": []}

# ---- 1. one API, many models: only the model string changes
from openai import OpenAI  # noqa: E402

for m in ["google/gemini-3.8-flash", "google/gemini-3.5-flash-lite", "openai/gpt-6-luna", "deepseek/deepseek-v4.1-flash"]:
    c = OpenAI(base_url=meter.base_url("models-" + m.replace("/", "_")), api_key=KEY)
    t0 = time.perf_counter()
    try:
        r = c.chat.completions.create(model=m, messages=Q, temperature=0)
        row = meter.log[-1]
        out["models"].append({"model": m, "answer": r.choices[0].message.content, "tokens_in": row["tokens_in"],
                              "tokens_out": row["tokens_out"], "seconds": row["seconds"], "cost_inr": row["cost_inr"],
                              "correct": "2,80,840" in (r.choices[0].message.content or "")
                              or "280,840" in (r.choices[0].message.content or "")
                              or "280840" in (r.choices[0].message.content or "")})
    except Exception as e:  # noqa: BLE001
        out["models"].append({"model": m, "error": f"{type(e).__name__}: {str(e)[:300]}"})
    print(out["models"][-1])

# ---- 2. LiteLLM Router: a named model with a fallback
import litellm  # noqa: E402
from litellm import Router  # noqa: E402

litellm.suppress_debug_info = True
base = meter.base_url("router")
router = Router(model_list=[
    {"model_name": "rasoi-brain", "litellm_params": {"model": "openai/google/gemini-3.8-flash", "api_base": base,
                                                     "api_key": KEY}},
    {"model_name": "rasoi-backup", "litellm_params": {"model": "openai/google/gemini-3.5-flash-lite", "api_base": base,
                                                      "api_key": KEY}},
], fallbacks=[{"rasoi-brain": ["rasoi-backup"]}], num_retries=0)

for label, kw in [("normal", {}), ("primary fails (mock_testing_fallbacks)", {"mock_testing_fallbacks": True})]:
    t0 = time.perf_counter()
    try:
        r = router.completion(model="rasoi-brain", messages=Q, temperature=0, **kw)
        row = meter.log[-1]
        out["router"].append({"case": label, "answered_by": row["model"], "answer": r.choices[0].message.content,
                              "seconds": row["seconds"], "cost_inr": row["cost_inr"]})
    except Exception as e:  # noqa: BLE001
        out["router"].append({"case": label, "error": f"{type(e).__name__}: {str(e)[:300]}"})
    print(out["router"][-1])

out["versions"] = {"litellm": litellm.__version__ if hasattr(litellm, "__version__") else None}
out["meter"] = meter.log
out["cost_inr"] = round(sum(r["cost_inr"] for r in meter.log), 4)
(LOGS / "gateway.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("wrote gateway.json; ₹", out["cost_inr"])
sys.stdout.flush()
os._exit(0)
