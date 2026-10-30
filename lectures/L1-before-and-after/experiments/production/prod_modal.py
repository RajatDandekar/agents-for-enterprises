"""Lecture 1's "In production" runner: tools/modal_run.py's pattern, plus the production tools at pinned versions.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py --script lectures/L1-before-and-after/experiments/production/probe.py
    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py --script lectures/L1-before-and-after/experiments/production/run_stacks.py --args "--run 1"

Why a second runner: tools/modal_run.py (shared) has no OpenAI Agents SDK, LangChain-OpenAI, LangChain MCP
adapters, OpenTelemetry exporter or headless browser. The pins are the ones Lecture 8 and Lecture 10 teach.
Keys (OpenRouter, Gemini, Langfuse) come from the course .env and the Gemini key file, are sent as a Modal secret,
and are never printed. Only files this segment owns are written back.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[4] if len(_P.parents) > 4 else pathlib.Path("/course")
ENV_FILES = ("/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env", str(ROOT / ".env"))
SKIP_DIRS = {".git", "qa", "archive", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}
KEYS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY",
        "LANGFUSE_BASE_URL", "LANGFUSE_HOST")
OWN = ("lectures/L1-before-and-after/experiments/production/", "ledgerline/ledgerline/course/l1/production/",
       "ledgerline/ledgerline/cassettes/L1v4_prod_")

# The versions taught (Lecture 8: frameworks; Lecture 10: OpenTelemetry, Langfuse, Playwright). Change them together.
PINS = ["openai-agents==0.20.0", "langgraph==1.2.15", "langchain-openai==1.7.1", "langchain-mcp-adapters==0.3.2",
        "opentelemetry-sdk==1.45.1", "opentelemetry-exporter-otlp-proto-http==1.45.1", "langfuse==4.17.0",
        "playwright==1.47.0"]


def _secret_env():
    env = {}
    for f in ENV_FILES:
        if os.path.exists(f):
            for line in open(f):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k.strip() in KEYS and v.strip():
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=2.45,<3", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas",
                 "rank_bm25", "langchain-core", "fastmcp", "mcp", "tabulate", "fastembed", "jsonschema", *PINS)
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/course/ledgerline", "LEDGER_IN_MODAL": "1", "OPENAI_AGENTS_DISABLE_TRACING": "0"})
)
_ign = (lambda p: any(part in SKIP_DIRS for part in pathlib.Path(p).parts)
        or str(p).endswith((".mp4", ".mov", ".zip", ".env", ".png", ".jpg", ".pdf", ".webm")))
for _d in ("ledgerline", "tools", "lectures/L1-before-and-after/experiments/production"):  # only what the runs read
    image = image.add_local_dir(ROOT / _d, f"/course/{_d}", ignore=_ign)
app = modal.App("l1-production", image=image)
secret = modal.Secret.from_dict(_secret_env() if modal.is_local() else {})


def _snap(root="/course"):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            p = os.path.join(dp, f)
            try:
                st = os.stat(p)
                if st.st_size < 30_000_000:
                    out[p] = (st.st_size, st.st_mtime)
            except OSError:
                pass
    return out


@app.function(secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run(path: str, args: str = "", mode: str = "auto") -> dict:
    os.environ["LEDGER_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                       text=True, timeout=3500)
    log = p.stdout[-40000:] + "\n--- stderr ---\n" + p.stderr[-10000:]
    files = {os.path.relpath(f, "/course"): open(f, "rb").read() for f, sig in _snap().items() if before.get(f) != sig}
    return {"ok": p.returncode == 0, "log": log, "files": files}


@app.local_entrypoint()
def main(script: str, args: str = "", mode: str = "auto"):
    res = run.remote(script, args, mode)
    kept, skipped = [], []
    for rel, data in res["files"].items():
        if not rel.startswith(OWN):
            skipped.append(rel)
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".jsonl") and dst.exists():  # cassettes are append-only: merge, never overwrite
            have = dst.read_bytes().splitlines()
            seen = set(have)
            dst.write_bytes(b"\n".join(have + [x for x in data.splitlines() if x and x not in seen]) + b"\n")
        else:
            dst.write_bytes(data)
        kept.append(rel)
    print(res["log"])
    if skipped:
        print("not written back (not ours):", ", ".join(sorted(skipped)[:20]), "..." if len(skipped) > 20 else "")
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(kept)} files written back:")
    for rel in sorted(kept)[:80]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
