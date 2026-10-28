"""Run the Studio's tests on Modal (never on the laptop). Mounts only bahi/, so other builders' files do not matter.

    /Users/raj/.venv/bin/modal run bahi/bahi/experience/studio/tests/modal_studio.py --what engine --mode auto
    /Users/raj/.venv/bin/modal run bahi/bahi/experience/studio/tests/modal_studio.py --what engine --mode replay
    /Users/raj/.venv/bin/modal run bahi/bahi/experience/studio/tests/modal_studio.py --what ui

Files the run creates or changes under studio/ (cassettes, logs, shots/) are copied back. The Gemini key is read
from the same env file tools/modal_run.py uses and sent as a Modal secret; it is never printed.
"""
import os
import pathlib
import subprocess
import sys

import modal

HERE = pathlib.Path(__file__).resolve()
LOCAL = len(HERE.parents) > 4  # inside the container this file is /root/modal_studio.py
STUDIO = HERE.parents[1] if LOCAL else pathlib.Path("/app/bahi/bahi/experience/studio")
BAHI = STUDIO.parents[2]  # .../enterprise-agents-course/bahi
COURSE = BAHI.parent
ENV_FILE = os.environ.get("BAHI_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SKIP = {"__pycache__", ".ipynb_checkpoints", "cassettes_unused"}


def _secret_env():
    env = {}
    for f in (ENV_FILE, str(COURSE / ".env")):
        if os.path.exists(f):
            for line in open(f):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"):
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _ignore(p):
    """Skip caches, secrets, and other builders' busy files (their cassettes and logs change while we upload)."""
    parts = pathlib.Path(p).parts
    if any(x in SKIP for x in parts) or str(p).endswith((".env", ".mp4", ".zip")):
        return True
    return ("studio" not in parts) and (str(p).endswith(".log") or "cassettes" in parts or "logs" in parts)


def _snapshot():
    """Copy bahi/ to a temp folder first, so files other builders save mid-upload cannot break the build."""
    import shutil
    import tempfile

    import atexit

    dst = pathlib.Path(tempfile.mkdtemp(prefix="studio-bahi-")) / "bahi"
    atexit.register(shutil.rmtree, dst.parent, True)
    shutil.copytree(BAHI, dst, ignore=lambda d, names: [n for n in names if _ignore(pathlib.Path(d, n).relative_to(BAHI))])
    return dst


SRC = _snapshot() if LOCAL and modal.is_local() else "/app/bahi"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "pandas", "fastmcp", "mcp",
                 "rank_bm25", "numpy", "playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/app/bahi"})
    .add_local_dir(SRC, "/app/bahi")
)
app = modal.App("rasoi-studio-tests", image=image)
secret = modal.Secret.from_dict(_secret_env() if LOCAL else {})
REMOTE_STUDIO = "/app/bahi/bahi/experience/studio"


def _snap():
    out = {}
    for dp, dns, fns in os.walk(REMOTE_STUDIO):
        dns[:] = [d for d in dns if d not in SKIP]
        for f in fns:
            p = os.path.join(dp, f)
            st = os.stat(p)
            out[p] = (st.st_size, st.st_mtime)
    return out


@app.function(secrets=[secret], timeout=1800, cpu=2, memory=4096)
def run(what: str, mode: str = "auto") -> dict:
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    script = {"engine": "test_engine.py", "ui": "test_ui.py", "probe": "probe_models.py"}[what]
    p = subprocess.run([sys.executable, os.path.join(REMOTE_STUDIO, "tests", script)], capture_output=True, text=True,
                       timeout=1700, cwd=REMOTE_STUDIO)
    after = _snap()
    files = {os.path.relpath(k, REMOTE_STUDIO): open(k, "rb").read() for k, v in after.items() if before.get(k) != v}
    return {"ok": p.returncode == 0, "log": p.stdout[-30000:] + "\n--- stderr ---\n" + p.stderr[-8000:], "files": files}


@app.local_entrypoint()
def main(what: str = "engine", mode: str = "auto"):
    res = run.remote(what, mode)
    for rel, data in res["files"].items():
        dst = STUDIO / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    print(res["log"])
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · files written back: {sorted(res['files'])}")
    if not res["ok"]:
        sys.exit(1)
