"""Smoke test of the L10 image: versions, Phoenix venv, promptfoo, Langfuse auth, OpenRouter credit (never prints keys)."""
import json, os, subprocess, pathlib, importlib.metadata as md
out = {p: md.version(p) for p in ["langfuse", "deepeval", "ragas", "opentelemetry-sdk", "pytest", "openai"]}
out["phoenix"] = subprocess.run(["/opt/phx/bin/python", "-c", "import importlib.metadata as m;print(m.version('arize-phoenix'))"], capture_output=True, text=True).stdout.strip()
out["promptfoo"] = subprocess.run(["promptfoo", "--version"], capture_output=True, text=True).stdout.strip()[-40:]
from langfuse import Langfuse
lf = Langfuse(public_key=os.environ["LANGFUSE_PUBLIC_KEY"], secret_key=os.environ["LANGFUSE_SECRET_KEY"],
              host=os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST"))
out["langfuse_auth"] = lf.auth_check()
import httpx
r = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]}, timeout=30).json()["data"]
out["openrouter"] = {k: r.get(k) for k in ("usage", "limit", "limit_remaining")}
(pathlib.Path(__file__).parent / "logs" / "smoke.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
