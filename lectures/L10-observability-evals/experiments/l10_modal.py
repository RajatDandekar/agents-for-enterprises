"""Lecture 10's own Modal runner: tools/modal_run.py's pattern, plus the industry tools at pinned versions.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/trace_gasket.py
    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --nb lectures/L10-observability-evals/NB10_observability_evals.ipynb --mode replay

Why a second runner: tools/modal_run.py (shared, not ours to edit) has no DeepEval, Ragas, OpenTelemetry exporter,
Node/promptfoo, Phoenix or a headless browser. Phoenix lives in its own virtualenv (/opt/phx) because its
dependencies (pydantic-ai, fastmcp-slim) do not resolve together with DeepEval and Ragas in one environment;
it runs as a separate server process anyway (`/opt/phx/bin/phoenix serve`).
Keys: the course .env and the Gemini key file, sent as a Modal secret, never printed.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[3] if len(_P.parents) > 3 else pathlib.Path("/course")  # inside the container the file is /root/l10_modal.py
ENV_FILES = ("/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env", str(ROOT / ".env"))
SKIP_DIRS = {".git", "qa", "archive", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}
KEYS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY",
        "LANGFUSE_BASE_URL", "LANGFUSE_HOST")

OWN = ("lectures/L10-observability-evals/", "bahi/bahi/course/obs/", "bahi/bahi/cassettes/IND10_")
PINS = ["langfuse==4.17.0", "deepeval==4.2.8", "ragas==0.4.3", "langchain-community==0.3.31", "opentelemetry-sdk==1.45.1",
        "opentelemetry-exporter-otlp-proto-http==1.45.1", "pytest==9.2.0", "playwright==1.47.0"]
PHOENIX = "arize-phoenix==20.21.4"
PROMPTFOO = "promptfoo@0.124.1"


def _secret_env():
    env = {}
    for f in ENV_FILES:
        if os.path.exists(f):
            for line in open(f):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k.strip() in KEYS:
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "git")
    .run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash -", "apt-get install -y nodejs",
                  f"npm install -g {PROMPTFOO}")
    .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas",
                 "matplotlib", "rank_bm25", "scikit-learn", "langgraph>=0.2", "langchain-core", "fastmcp", "mcp",
                 "nbformat", "nbclient", "ipykernel", "tabulate", "fastembed", "jsonschema", *PINS)
    .run_commands("playwright install --with-deps chromium")
    .run_commands("python -m venv /opt/phx", f"/opt/phx/bin/pip install -q {PHOENIX}")
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1", "PROMPTFOO_DISABLE_TELEMETRY": "1",
          "PROMPTFOO_DISABLE_UPDATE": "1", "DEEPEVAL_TELEMETRY_OPT_OUT": "YES", "PHOENIX_TELEMETRY_ENABLED": "false"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(part in SKIP_DIRS for part in pathlib.Path(p).parts)
                   or str(p).endswith((".mp4", ".mov", ".zip", ".env")))
)
app = modal.App("l10-observability-evals", image=image)
secret = modal.Secret.from_dict(_secret_env())


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
def run(kind: str, path: str, args: str = "", mode: str = "auto") -> dict:
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    ok, log = True, ""
    if kind == "script":
        os.environ["MPLBACKEND"] = "Agg"
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                           text=True, timeout=3500)
        log, ok = p.stdout[-20000:] + "\n--- stderr ---\n" + p.stderr[-8000:], p.returncode == 0
    elif kind == "shell":  # e.g. pytest or promptfoo, run from the script's folder
        p = subprocess.run(args, shell=True, cwd=full, capture_output=True, text=True, timeout=3500)
        log, ok = p.stdout[-20000:] + "\n--- stderr ---\n" + p.stderr[-8000:] + f"\nexit {p.returncode}", True
    else:
        import nbformat
        from nbclient import NotebookClient
        from nbclient.exceptions import CellExecutionError
        nb = nbformat.read(full, as_version=4)
        client = NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(full)}})
        try:
            client.execute()
        except CellExecutionError as e:
            ok, log = False, str(e)[-8000:]
        nbformat.write(nb, full)
        n = sum(1 for c in nb.cells if c.cell_type == "code")
        errs = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
        log += f"\nexecuted {n} code cells, {len(errs)} errors"
    after = _snap()
    files = {os.path.relpath(p, "/course"): open(p, "rb").read() for p, sig in after.items() if before.get(p) != sig}
    return {"ok": ok, "log": log, "files": files}


@app.local_entrypoint()
def main(script: str = "", nb: str = "", shell: str = "", args: str = "", mode: str = "auto"):
    kind, path = ("script", script) if script else ("shell", shell) if shell else ("nb", nb)
    res = run.remote(kind, path, args, mode)
    skipped = []
    for rel, data in res["files"].items():
        if "/node_modules/" in rel or rel.startswith(".promptfoo"):
            continue
        if not rel.startswith(OWN):  # never write back a file this lecture does not own (shared caches, other lectures)
            skipped.append(rel)
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    print(res["log"])
    if skipped:
        print("not written back (not ours):", ", ".join(skipped))
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(res['files']) - len(skipped)} files written back:")
    for rel in sorted(res["files"])[:80]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
