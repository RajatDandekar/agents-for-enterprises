"""List current OpenAI and Anthropic models on OpenRouter with their prices (US$ per million tokens), and try one
tool call on a few candidates. Never prints the key. -> logs/openrouter_models.json"""
import json, os, pathlib, time
import httpx
from openai import OpenAI

r = httpx.get("https://openrouter.ai/api/v1/models", timeout=60).json()["data"]
rows = []
for m in r:
    if m["id"].startswith(("openai/", "anthropic/")):
        p = m.get("pricing", {})
        rows.append({"id": m["id"], "created": m.get("created"), "in": round(float(p.get("prompt", 0)) * 1e6, 3),
                     "out": round(float(p.get("completion", 0)) * 1e6, 3), "ctx": m.get("context_length"),
                     "tools": "tools" in (m.get("supported_parameters") or [])})
rows.sort(key=lambda x: -(x["created"] or 0))
for x in rows[:45]:
    print(x)
c = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
tool = {"type": "function", "function": {"name": "stk_query", "description": "STOCK STATUS ENQUIRY",
        "parameters": {"type": "object", "properties": {"itm_cd": {"type": "string"}}, "required": ["itm_cd"]}}}
tried = {}
cands = [x["id"] for x in rows if x["tools"] and any(k in x["id"] for k in ("mini", "haiku", "sonnet", "flash"))][:8]
for mid in cands:
    try:
        t = time.time()
        res = c.chat.completions.create(model=mid, messages=[{"role": "user", "content": "How many GSK-SIL-05L do we have?"}], tools=[tool], max_tokens=200)
        tc = res.choices[0].message.tool_calls
        tried[mid] = {"ok": True, "s": round(time.time() - t, 2), "call": tc[0].function.arguments if tc else None,
                      "tin": res.usage.prompt_tokens, "tout": res.usage.completion_tokens}
    except Exception as e:
        tried[mid] = {"ok": False, "err": str(e)[:200]}
    print(mid, tried[mid])
(pathlib.Path(__file__).parent / "logs" / "openrouter_models.json").write_text(json.dumps({"models": rows, "tool_test": tried}, indent=1))
