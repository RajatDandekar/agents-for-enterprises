"""Lecture 6's Modal runner: our experiments, with the industry tools at pinned versions, on Claude.

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script incident.py
    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script guards_eval.py --image guards
    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --shell "pytest -q ci" --image evals

Images (one app, several images, so tools whose dependencies fight never share an environment):
    core    the course (ledgerline), OpenTelemetry, Langfuse SDK, httpx, Playwright + Chromium, Phoenix in /opt/phx
    evals   core + DeepEval + pytest
    guards  core + Presidio (+ spaCy en_core_web_sm) + transformers/torch CPU (ProtectAI's DeBERTa injection classifier,
            downloaded at build) ; NeMo Guardrails + langchain-anthropic in their own venv /opt/nemo
    node    core + Node 22 + promptfoo
Keys: ANTHROPIC_API_KEY from the Modal secret forge-anthropic; the Langfuse keys from the course .env, sent at run time as
a Modal secret (modal.Secret.from_dict), never printed, never in an image. Files the script writes under this lecture's
folder (or ledgerline/ledgerline/course/l6, or cassettes/L6E_*) come back to the laptop; nothing else is written back.
"""
import hashlib
import os
import shlex
import pathlib
import subprocess
import sys

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[3] if len(_P.parents) > 3 else pathlib.Path("/course")
L6 = "lectures/L6-evals-guardrails-observability"
OWN = (L6 + "/", "ledgerline/ledgerline/course/l6/", "ledgerline/ledgerline/cassettes/L6E_")
LF_KEYS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL", "LANGFUSE_HOST",
           "LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT", "SENTRY_DSN", "SENTRY_ORG", "SENTRY_AUTH_TOKEN")   # each optional
SKIP = {".git", "qa", "node_modules", "__pycache__", ".ipynb_checkpoints", "films", ".promptfoo"}

PINS_CORE = ["openai==3.51.0", "httpx==0.28.1", "pydantic>=2", "jsonschema", "pyyaml", "rank_bm25", "numpy", "pandas",
             "fastembed==0.9.1", "opentelemetry-sdk==1.45.2", "opentelemetry-exporter-otlp-proto-http==1.45.2",
             "langfuse==5.2.0", "playwright==1.47.0", "pillow", "fastapi==0.115.6", "uvicorn"]
PHOENIX = "arize-phoenix==21.0.0"
DEEPEVAL = ["deepeval==4.3.4", "pytest==9.2.0", "anthropic==2.8.0"]
GUARDS = ["presidio-analyzer==2.2.366", "presidio-anonymizer==2.2.366", "transformers==5.23.0"]
NEMO = ["nemoguardrails==0.24.1", "langchain==1.5.0", "langchain-community==0.4.2", "langchain-anthropic==1.7.10"]
PROMPTFOO = "promptfoo@0.125.1"
INJ_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"


def _lf_env():
    env = {}
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in LF_KEYS:
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _keep(p) -> bool:
    parts = pathlib.Path(p).parts
    if any(x in SKIP for x in parts):
        return False
    return not str(p).endswith((".env", ".mp4", ".webm", ".mov", ".zip"))


core = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "git")
    .pip_install(*PINS_CORE)
    .env({"FASTEMBED_CACHE_PATH": "/models/fastembed"})
    .run_commands("python -c \"from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')\"")
    .run_commands("playwright install --with-deps chromium")
    .run_commands("python -m venv /opt/phx", f"/opt/phx/bin/pip install -q {PHOENIX}")
    .env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "LEDGER_LLM_MODE": "auto", "MPLBACKEND": "Agg",
          "PHOENIX_TELEMETRY_ENABLED": "false", "DEEPEVAL_TELEMETRY_OPT_OUT": "YES", "PROMPTFOO_DISABLE_TELEMETRY": "1",
          "PROMPTFOO_DISABLE_UPDATE": "1", "HF_HUB_DISABLE_TELEMETRY": "1", "TOKENIZERS_PARALLELISM": "false"})
)
evals = core.pip_install(*DEEPEVAL, "ragas==0.4.4", "langchain-anthropic==1.7.10", "nbclient==0.10.2", "nbformat==5.10.4",
                         "ipykernel==6.29.5", "nbconvert==7.16.6")
# "clean": what a fresh Colab has, more or less: Python 3.12 and the course package's own dependencies (ledgerline-erp[all],
# unpinned). Everything a Lecture 6 notebook needs beyond that is installed by the notebook's own pip cell.
clean = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
         .pip_install("openai>=1.50", "pyyaml", "pandas", "httpx", "pydantic>=2", "fastapi", "uvicorn", "rank_bm25", "numpy", "fastembed",
                      "langgraph>=0.2", "langchain-core", "fastmcp>=2.10", "mcp", "temporalio", "langfuse", "matplotlib",
                      "nbclient==0.10.2", "nbformat==5.10.4", "ipykernel==6.29.5", "nbconvert==7.16.6")
         .env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "MPLBACKEND": "Agg"}))
guards = (core.pip_install("torch==2.15.0", index_url="https://download.pytorch.org/whl/cpu")
          .pip_install(*GUARDS, "spacy==3.8.18")
          .run_commands("python -m spacy download en_core_web_sm")
          .env({"HF_HOME": "/models/hf"})
          .run_commands(f"python -c \"from transformers import pipeline; pipeline('text-classification', model='{INJ_MODEL}')\"")
          .run_commands("python -m venv /opt/nemo", "/opt/nemo/bin/pip install -q " + " ".join(NEMO)))
node = (guards.run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash -", "apt-get install -y nodejs",
                          f"npm install -g {PROMPTFOO}"))


def _mount(img):
    return (img.add_local_dir(ROOT / "ledgerline", "/course/ledgerline", ignore=lambda p: not _keep(p))
            .add_local_dir(ROOT / L6, "/course/" + L6, ignore=lambda p: not _keep(p)))


app = modal.App("l6-evals-guardrails-observability")
secrets = [modal.Secret.from_name("forge-anthropic"), modal.Secret.from_dict(_lf_env())]


def _snap(root="/course"):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p = os.path.join(dp, f)
            try:
                st = os.stat(p)
                if st.st_size < 40_000_000:
                    out[p] = (st.st_size, st.st_mtime)
            except OSError:
                pass
    return out


def _go(kind: str, path: str, args: str) -> dict:
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)
    before = _snap()
    exp = f"/course/{L6}/experiments"
    if kind == "script":
        full = os.path.join(exp, path)
        p = subprocess.run([sys.executable, full, *shlex.split(args)], cwd=exp, capture_output=True, text=True, timeout=7000)
    else:
        p = subprocess.run(args, shell=True, cwd=os.path.join(exp, path or "."), capture_output=True, text=True, timeout=7000)
    log = p.stdout[-30000:] + "\n--- stderr ---\n" + p.stderr[-10000:] + f"\nexit {p.returncode}"
    after = _snap()
    files = {os.path.relpath(q, "/course"): open(q, "rb").read() for q, sig in after.items() if before.get(q) != sig}
    return {"ok": p.returncode == 0, "log": log, "files": files}


@app.function(image=_mount(core), secrets=secrets, timeout=7200, cpu=4, memory=8192)
def run_core(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.function(image=_mount(evals), secrets=secrets, timeout=7200, cpu=4, memory=8192)
def run_evals(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.function(image=_mount(clean), secrets=[modal.Secret.from_dict(_lf_env())], timeout=7200, cpu=4, memory=8192)
def run_clean(kind: str, path: str, args: str = "") -> dict:      # no Anthropic key in this container at all
    return _go(kind, path, args)


@app.function(image=_mount(guards), secrets=secrets, timeout=7200, cpu=8, memory=16384)
def run_guards(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.function(image=_mount(node), secrets=secrets, timeout=7200, cpu=4, memory=8192)
def run_node(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.local_entrypoint()
def main(script: str = "", shell: str = "", cwd: str = "", args: str = "", image: str = "core"):
    fn = {"core": run_core, "evals": run_evals, "clean": run_clean, "guards": run_guards, "node": run_node}[image]
    res = fn.remote("script", script, args) if script else fn.remote("shell", cwd, shell)
    skipped, wrote = [], []
    for rel, data in res["files"].items():
        if not rel.startswith(OWN) or "/.promptfoo" in rel or "/node_modules/" in rel:
            skipped.append(rel)
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        wrote.append(rel)
    print(res["log"])
    if skipped:
        print("not written back (not ours):", ", ".join(skipped[:20]))
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(wrote)} files written back:")
    for rel in sorted(wrote)[:120]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
