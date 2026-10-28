"""tools/modal_run.py for Lecture 8, with the agent-framework SDKs pinned in the image, run from a frozen copy.

    tools/mrun.sh lectures/L8-frameworks/experiments/run_modal.py --script lectures/L8-frameworks/experiments/probe.py
    tools/mrun.sh lectures/L8-frameworks/experiments/run_modal.py --script lectures/L8-frameworks/experiments/exp_frameworks.py --args "--fw openai_agents"

It copies bahi/ (with only the IND8_* cassettes), tools/ and lectures/L8-frameworks/ into a staging folder, mounts
that, runs the job on Modal (profile rajatworkspace) and writes back only files under lectures/L8-frameworks/ and
bahi/bahi/cassettes/IND8_*. Keys come from the Gemini key file and the course .env and are never printed.
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
STAGE = pathlib.Path(os.environ.get("L8_STAGE", f"/private/tmp/l8stage-{os.getpid()}"))
OURS = ("lectures/L8-frameworks/", "bahi/bahi/cassettes/IND8_")
ENV_FILE = os.environ.get("BAHI_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SKIP_DIRS = {".git", "qa", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}
KEYS = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY")

# The versions the lecture teaches and the notebook installs. Change them together.
PINS = ["openai-agents==0.20.0", "google-adk==2.11.0", "litellm==1.104.2", "langgraph==1.2.15",
        "langchain-openai==1.7.1", "langchain-mcp-adapters==0.3.2"]


def _stage():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    ex = ["--exclude", "__pycache__", "--exclude", ".ipynb_checkpoints", "--exclude", "qa", "--exclude", "*.png",
          "--exclude", "*.mp4"]
    subprocess.run(["rsync", "-a", *ex, "--exclude", "cassettes/*", str(ROOT / "bahi"), str(STAGE)], check=True)
    (STAGE / "bahi/bahi/cassettes").mkdir(parents=True, exist_ok=True)
    for c in (ROOT / "bahi/bahi/cassettes").glob("IND8_*"):
        shutil.copy2(c, STAGE / "bahi/bahi/cassettes" / c.name)
    subprocess.run(["rsync", "-a", *ex, str(ROOT / "tools"), str(STAGE)], check=True)
    (STAGE / "lectures").mkdir(exist_ok=True)
    subprocess.run(["rsync", "-a", *ex, str(ROOT / "lectures/L8-frameworks"), str(STAGE / "lectures")], check=True)
    return STAGE


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
    .pip_install("openai>=2.45,<3", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas",
                 "matplotlib", "rank_bm25", "langchain-core", "fastmcp", "mcp", "nbformat", "nbclient", "ipykernel",
                 "tabulate", "jsonschema", "fastembed", *PINS)
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1", "OPENAI_AGENTS_DISABLE_TRACING": "0"})
    .add_local_dir(_stage() if modal.is_local() else "/tmp", "/course")
)
app = modal.App("l8-frameworks", image=image)
secret = modal.Secret.from_dict(_secret_env() if modal.is_local() else {})


@app.function(secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run(kind: str, path: str, args: str = "", mode: str = "auto") -> dict:
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    log, ok = "", True
    if kind == "script":
        os.environ["MPLBACKEND"] = "Agg"
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                           text=True, timeout=3400)
        log, ok = p.stdout[-60000:] + "\n--- stderr ---\n" + p.stderr[-12000:], p.returncode == 0
    else:
        import nbformat
        from nbclient import NotebookClient
        from nbclient.exceptions import CellExecutionError
        nb = nbformat.read(full, as_version=4)
        client = NotebookClient(nb, timeout=900, kernel_name="python3",
                                resources={"metadata": {"path": os.path.dirname(full)}})
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
    for rel in sorted(kept)[:80]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    shutil.rmtree(STAGE, ignore_errors=True)
    if not res["ok"]:
        sys.exit(1)
