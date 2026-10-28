"""Probe (2026-10-28): which versions of the L11 tools exist today, what the Temporal x Agents SDK API looks like,
and whether OpenRouter serves a Llama Guard model. Run inside a throwaway Modal container (probe_modal.py)."""
import importlib, inspect, json, os, subprocess, sys

out = {}
for pkg in ["temporalio", "openai-agents", "nemoguardrails", "litellm", "psycopg", "pgvector", "redis", "openai"]:
    r = subprocess.run([sys.executable, "-m", "pip", "index", "versions", pkg], capture_output=True, text=True)
    out[pkg] = (r.stdout.splitlines() or [r.stderr[-200:]])[0][:200]
print(json.dumps(out, indent=1))

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "temporalio[openai-agents]", "openai-agents"], check=False)
import temporalio, agents  # noqa
print("temporalio", temporalio.__version__ if hasattr(temporalio, "__version__") else "?")
from importlib.metadata import version
print("temporalio", version("temporalio"), "openai-agents", version("openai-agents"))
import temporalio.contrib.openai_agents as toa
print("contrib.openai_agents:", [n for n in dir(toa) if not n.startswith("_")])
for n in ["OpenAIAgentsPlugin", "ModelActivityParameters"]:
    o = getattr(toa, n, None)
    if o:
        try:
            print(n, inspect.signature(o))
        except Exception as e:
            print(n, e)
wf = getattr(toa, "workflow", None)
if wf:
    print("toa.workflow:", [n for n in dir(wf) if not n.startswith("_")])
    if hasattr(wf, "activity_as_tool"):
        print("activity_as_tool", inspect.signature(wf.activity_as_tool))
print(inspect.getsource(toa)[:3000])

# OpenRouter: Llama Guard and guard-type models
import urllib.request
req = urllib.request.Request("https://openrouter.ai/api/v1/models")
models = json.load(urllib.request.urlopen(req, timeout=30))["data"]
hits = [(m["id"], m.get("pricing", {}).get("prompt"), m.get("pricing", {}).get("completion"), m.get("context_length"))
        for m in models if any(k in m["id"].lower() for k in ("guard", "shield", "safety", "moderat"))]
print("openrouter guard-like models:", json.dumps(hits, indent=1))
g = [(m["id"], m.get("pricing", {}).get("prompt"), m.get("pricing", {}).get("completion")) for m in models
     if m["id"].startswith("google/gemini-3")]
print("openrouter gemini-3*:", g)

# Gemini key direct (PaperBanana needs it)
key = os.environ.get("GEMINI_API_KEY")
if key:
    from openai import OpenAI
    c = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=key)
    try:
        r = c.chat.completions.create(model="gemini-3.5-flash-lite", messages=[{"role": "user", "content": "Say OK"}], max_tokens=5)
        print("gemini direct OK:", r.choices[0].message.content)
    except Exception as e:
        print("gemini direct ERR:", str(e)[:200])
