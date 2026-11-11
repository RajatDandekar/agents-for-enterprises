"""tools/modal_run.py, but from a frozen copy of the course, so other builders' edits cannot break the upload.

    /Users/raj/.venv/bin/modal run lectures/L5-the-loop/experiments/run_modal.py --script lectures/L5-the-loop/experiments/exp_tasks.py --args "--agent harness"
    /Users/raj/.venv/bin/modal run lectures/L5-the-loop/experiments/run_modal.py --nb lectures/L5-the-loop/NB5_the_loop.ipynb --mode replay

It copies bahi/ (with only the L5v3_* cassettes), tools/ and lectures/L5-the-loop/ into a staging folder
(L5_STAGE, default: a folder in /tmp), mounts that, runs the job on Modal exactly as tools/modal_run.py does, and
writes back only files under lectures/L5-the-loop/ and bahi/bahi/cassettes/L5v3_*.
"""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

import modal

_here = pathlib.Path(__file__).resolve()
ROOT = _here.parents[3] if len(_here.parents) > 3 else pathlib.Path("/course")
STAGE = pathlib.Path(os.environ.get("L5_STAGE", f"/tmp/l5stage-{os.getpid()}"))
OURS = ("lectures/L5-the-loop/", "bahi/bahi/cassettes/L5v3_")


def _stage():
    if modal.is_local():
        if STAGE.exists():
            shutil.rmtree(STAGE)
        STAGE.mkdir(parents=True)
        ex = ["--exclude", "__pycache__", "--exclude", ".ipynb_checkpoints", "--exclude", "qa", "--exclude", "*.png",
              "--exclude", "*.mp4"]
        subprocess.run(["rsync", "-a", *ex, "--exclude", "cassettes/*", str(ROOT / "bahi"), str(STAGE)], check=True)
        (STAGE / "bahi/bahi/cassettes").mkdir(parents=True, exist_ok=True)
        for c in (ROOT / "bahi/bahi/cassettes").glob("L5v3_*"):
            shutil.copy2(c, STAGE / "bahi/bahi/cassettes" / c.name)
        subprocess.run(["rsync", "-a", *ex, str(ROOT / "tools"), str(STAGE)], check=True)
        (STAGE / "lectures").mkdir(exist_ok=True)
        subprocess.run(["rsync", "-a", *ex, str(ROOT / "lectures/L5-the-loop"), str(STAGE / "lectures")], check=True)
    return STAGE



ENV_FILE = os.environ.get("BAHI_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SKIP_DIRS = {".git", "qa", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}
KEYS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def _secret_env():
    env = {}
    for f in (ENV_FILE, str(ROOT / ".env")):
        if os.path.exists(f):
            for line in open(f):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k.strip() in KEYS:
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


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
    return {os.path.relpath(p, "/course"): open(p, "rb").read() for p, sig in _snap().items() if before.get(p) != sig}


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas", "matplotlib",
        "rank_bm25", "scikit-learn", "langgraph>=0.2", "langchain-core", "fastmcp", "mcp", "temporalio",
        "nbformat", "nbclient", "ipykernel", "ipywidgets", "tabulate", "langfuse", "fastembed", "jsonschema",
    )
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1"})
    .add_local_dir(_stage() if modal.is_local() else "/tmp", "/course")
)
app = modal.App("l5-the-loop", image=image)
secret = modal.Secret.from_dict(_secret_env() if modal.is_local() else {})


@app.function(secrets=[secret], timeout=3600, cpu=2, memory=4096)
def run(kind: str, path: str, args: str = "", mode: str = "auto") -> dict:
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    log, ok = "", True
    if kind == "script":
        os.environ["MPLBACKEND"] = "Agg"
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                           text=True, timeout=3400)
        log, ok = p.stdout[-60000:] + "\n--- stderr ---\n" + p.stderr[-8000:], p.returncode == 0
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
    kept = []
    for rel, data in res["files"].items():
        if not rel.startswith(OURS):
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        kept.append(rel)
    print(res["log"])
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(kept)} files written back:")
    for rel in sorted(kept)[:60]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    shutil.rmtree(STAGE, ignore_errors=True)
    if not res["ok"]:
        sys.exit(1)
