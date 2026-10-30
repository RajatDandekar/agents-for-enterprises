"""Before any run: which models OpenRouter offers with tool calling, at what price; the key's remaining credit; that
Langfuse accepts our keys; the pinned SDK versions. Writes logs/probe.json. No key is printed."""
import importlib.metadata as md
import json
import os
import pathlib
import time
import urllib.request

OUT = pathlib.Path(__file__).parent / "logs" / "probe.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
H = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"}


def get(url, headers=None):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=60).read())


out = {"at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "versions": {}}
for pkg in ["openai-agents", "langgraph", "langchain-openai", "langchain-mcp-adapters", "langchain-core", "fastmcp", "mcp",
            "openai", "opentelemetry-sdk", "opentelemetry-exporter-otlp-proto-http", "langfuse", "playwright"]:
    try:
        out["versions"][pkg] = md.version(pkg)
    except Exception as e:  # noqa: BLE001
        out["versions"][pkg] = f"missing {e}"

try:
    k = get("https://openrouter.ai/api/v1/key", H)["data"]
    out["key"] = {x: k.get(x) for x in ("usage", "limit", "limit_remaining", "is_free_tier", "usage_daily")}
except Exception as e:  # noqa: BLE001
    out["key"] = f"error {e!r}"[:300]
try:
    out["credits"] = get("https://openrouter.ai/api/v1/credits", H).get("data")
except Exception as e:  # noqa: BLE001
    out["credits"] = f"error {e!r}"[:200]

models = get("https://openrouter.ai/api/v1/models")["data"]
WANT = ("google/gemini", "openai/gpt", "anthropic/claude", "meta-llama/", "qwen/", "mistralai/", "deepseek/")
rows = []
for m in models:
    if not m["id"].startswith(WANT) or "tools" not in (m.get("supported_parameters") or []):
        continue
    p = m.get("pricing") or {}
    rows.append({"id": m["id"], "in_per_M": round(float(p.get("prompt", 0)) * 1e6, 4),
                 "out_per_M": round(float(p.get("completion", 0)) * 1e6, 4), "ctx": m.get("context_length"),
                 "created": m.get("created")})
rows.sort(key=lambda r: -(r["created"] or 0))
out["models_with_tools"] = rows

# one tiny tool call on each candidate (a few hundred tokens each)
tool = {"type": "function", "function": {"name": "check_stock", "description": "Stock of an item in every warehouse.",
        "parameters": {"type": "object", "properties": {"item_code": {"type": "string"}}, "required": ["item_code"]}}}
cands = [r["id"] for r in rows]
pick = []
for pref in ("google/gemini-3.8-flash", "openai/gpt-", "anthropic/claude-haiku", "meta-llama/llama", "qwen/qwen",
             "openai/gpt-oss"):
    pick += [c for c in cands if c.startswith(pref)][:6]
from openai import OpenAI  # noqa: E402
c = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))
tests = {}
for mid in dict.fromkeys(pick):
    if any(x in mid for x in ("-pro", "opus", "-image", "audio", "vision", "search")):
        continue
    t = time.time()
    try:
        r = c.chat.completions.create(model=mid, temperature=0, max_tokens=300, tools=[tool],
                                      messages=[{"role": "user", "content": "How many BAT-500 battery packs do we have?"}],
                                      extra_body={"usage": {"include": True}})
        m = r.choices[0].message
        tests[mid] = {"ok": True, "s": round(time.time() - t, 2),
                      "tool_call": m.tool_calls[0].function.arguments if m.tool_calls else None,
                      "text": (m.content or "")[:80], "cost_usd": (r.usage.model_extra or {}).get("cost"),
                      "provider": getattr(r, "provider", None)}
    except Exception as e:  # noqa: BLE001
        tests[mid] = {"ok": False, "error": str(e)[:200]}
out["tool_tests"] = tests

# Langfuse: do the keys work? (one authenticated read, nothing printed but the status)
try:
    from langfuse import Langfuse
    lf = Langfuse(public_key=os.environ["LANGFUSE_PUBLIC_KEY"], secret_key=os.environ["LANGFUSE_SECRET_KEY"],
                  base_url=os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST"))
    out["langfuse_auth"] = lf.auth_check()
    out["langfuse_host"] = (os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST") or "").split("//")[-1]
except Exception as e:  # noqa: BLE001
    out["langfuse_auth"] = f"error {e!r}"[:300]

OUT.write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "models_with_tools"}, indent=1))
print("models with tools:", len(rows))
for r in rows[:120]:
    print(r["id"], r["in_per_M"], r["out_per_M"])
