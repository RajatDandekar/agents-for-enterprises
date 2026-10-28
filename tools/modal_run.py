"""Run course code and notebooks on Modal, never on the laptop.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L1/experiments/naive_sweep.py --args "--model gemini:gemini-2.5-flash"
    /Users/raj/.venv/bin/modal run tools/modal_run.py --nb lectures/L1/NB1_the_form_and_its_nine_jobs.ipynb
    /Users/raj/.venv/bin/modal run tools/modal_run.py --nb lectures/L1/NB1.ipynb --mode replay   # prove it runs with no key

The whole course folder is mounted at /course with PYTHONPATH=/course/bahi. Every file the run creates or
changes under /course (executed notebooks, cassettes, experiment logs, figures) is copied back here.
The Gemini key is read from BAHI_ENV_FILE (default: the working key noted in memory) and sent as a Modal
secret; it is never printed. --mode sets BAHI_LLM_MODE (auto, record, replay, live).
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_FILE = os.environ.get("BAHI_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SKIP_DIRS = {".git", "qa", "archive", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}


def _secret_env():
    env = {}
    for f in (ENV_FILE, str(ROOT / ".env")):  # the Gemini key file, then the course's own .env (OpenRouter, Langfuse)
      if os.path.exists(f):
        for line in open(f):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY",
                                 "ANTHROPIC_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST",
                                 "LANGFUSE_BASE_URL"):
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas", "matplotlib",
        "rank_bm25", "scikit-learn", "langgraph>=0.2", "langchain-core", "fastmcp", "mcp", "temporalio",
        "nbformat", "nbclient", "ipykernel", "ipywidgets", "tabulate", "langfuse", "fastembed", "jsonschema",
    )
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(part in SKIP_DIRS for part in pathlib.Path(p).parts)
                   or str(p).endswith((".mp4", ".mov", ".zip", ".env")))
)
app = modal.App("enterprise-agents-course", image=image)
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


def _changed(before):
    after = _snap()
    files = {}
    for p, sig in after.items():
        if before.get(p) != sig:
            data = open(p, "rb").read()
            files[os.path.relpath(p, "/course")] = data
    return files


@app.function(secrets=[secret], timeout=3600, cpu=2, memory=4096)
def run(kind: str, path: str, args: str = "", mode: str = "auto", timeout: int = 1800) -> dict:
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    log = ""
    ok = True
    if kind == "script":
        os.environ["MPLBACKEND"] = "Agg"  # scripts save figures; notebooks keep matplotlib's inline backend
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                           text=True, timeout=timeout)
        log, ok = p.stdout[-20000:] + "\n--- stderr ---\n" + p.stderr[-8000:], p.returncode == 0
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
    return {"ok": ok, "log": log, "files": _changed(before)}


@app.local_entrypoint()
def main(script: str = "", nb: str = "", args: str = "", mode: str = "auto"):
    kind, path = ("script", script) if script else ("nb", nb)
    res = run.remote(kind, path, args, mode)
    for rel, data in res["files"].items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    print(res["log"])
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(res['files'])} files written back:")
    for rel in sorted(res["files"])[:60]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
