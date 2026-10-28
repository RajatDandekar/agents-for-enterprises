"""Lecture 11's own Modal runner: the industry tools need images the course runner (tools/modal_run.py) does not have.

    L11_IMAGE=guard   tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/guard_eval.py
    L11_IMAGE=durable tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/durable_order.py
    L11_IMAGE=data    tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/memory_prod.py
    L11_IMAGE=data    tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/gateway.py

Same contract as tools/modal_run.py: the course folder is mounted at /course (PYTHONPATH=/course/bahi), every file the
run creates or changes is copied back, keys travel as a Modal secret and are never printed.
Every version is pinned here and in NOTES.md (checked with `pip index versions` on 2026-10-28, logs/probe_versions.txt).
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import modal

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKIP_DIRS = {".git", "qa", "archive", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv"}
IMAGE = os.environ.get("L11_IMAGE", "guard")   # set by the caller locally; baked into the image for the container
KEYS = ("OPENROUTER_API_KEY", "GEMINI_API_KEY")

PINS = {
    "temporalio": "1.34.0", "temporalio-openai-agents": "1.1.0", "openai-agents": "0.22.3", "openai": "3.39.0", "nemoguardrails": "0.24.1", "litellm": "1.106.5",
    "psycopg": "3.3.6", "pgvector": "0.5.1", "redis": "8.1.0", "temporal_cli": "1.5.1", "pgvector_ext": "0.8.1",
}


def _secret_env():
    env = {}
    for f in ("/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env", str(ROOT / ".env")):
        if os.path.exists(f):
            for line in open(f):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k.strip() in KEYS:
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _mount(img):
    return (img.env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1", "MPLBACKEND": "Agg", "L11_IMAGE": IMAGE})
            .add_local_dir(ROOT, "/course", ignore=lambda p: any(part in SKIP_DIRS for part in pathlib.Path(p).parts)
                           or str(p).endswith((".mp4", ".mov", ".zip", ".env"))))


BASE = ["openai>=1.50", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas", "matplotlib", "rank_bm25", "fastmcp",
        "mcp", "fastembed", "jsonschema", "tabulate", "fastapi", "uvicorn"]

def img_guard():
    return _mount(modal.Image.debian_slim(python_version="3.11")
                   .pip_install(*BASE, f"nemoguardrails=={PINS['nemoguardrails']}", "langchain-openai"))
def img_durable():
    return _mount(modal.Image.debian_slim(python_version="3.11")
                     .apt_install("curl", "procps")
                     .pip_install(*BASE, f"temporalio=={PINS['temporalio']}", f"temporalio-openai-agents=={PINS['temporalio-openai-agents']}",
                                  f"openai-agents=={PINS['openai-agents']}", f"openai=={PINS['openai']}", "playwright==1.47.0")
                     .run_commands("playwright install --with-deps chromium",
                                   f"(curl -fsSL -o /tmp/t.tgz 'https://temporal.download/cli/archive/v{PINS['temporal_cli']}?platform=linux&arch=amd64'"
                                   " || curl -fsSL -o /tmp/t.tgz 'https://temporal.download/cli/archive/latest?platform=linux&arch=amd64')"
                                   " && tar -xzf /tmp/t.tgz -C /usr/local/bin temporal && temporal --version"))
def img_data():
    return _mount(modal.Image.debian_slim(python_version="3.11")
                  .apt_install("postgresql", "postgresql-server-dev-all", "build-essential", "git", "redis-server", "procps", "curl")
                  .run_commands(f"git clone --branch v{PINS['pgvector_ext']} --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgv"
                                " && cd /tmp/pgv && make && make install")
                  .pip_install(*BASE, f"psycopg[binary]=={PINS['psycopg']}", f"pgvector=={PINS['pgvector']}",
                               f"redis=={PINS['redis']}", f"litellm[proxy]=={PINS['litellm']}", "prisma"))

app = modal.App(f"l11-production-{IMAGE}")
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


def _run(path, args, mode):
    os.environ["BAHI_LLM_MODE"] = mode
    before = _snap()
    full = os.path.join("/course", path)
    if path.endswith(".ipynb"):
        import nbformat
        from nbclient import NotebookClient
        nb = nbformat.read(full, as_version=4)
        ok, log = True, ""
        try:
            NotebookClient(nb, timeout=900, kernel_name="python3",
                           resources={"metadata": {"path": os.path.dirname(full)}}).execute()
        except Exception as e:  # noqa: BLE001
            ok, log = False, str(e)[-8000:]
        nbformat.write(nb, full)
        errs = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
        log += f"\nexecuted {sum(c.cell_type == 'code' for c in nb.cells)} code cells, {len(errs)} errors"
    else:
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True,
                           text=True, timeout=3300)
        log, ok = p.stdout[-24000:] + "\n--- stderr ---\n" + p.stderr[-8000:], p.returncode == 0
    after = _snap()
    files = {os.path.relpath(p, "/course"): open(p, "rb").read() for p, s in after.items() if before.get(p) != s}
    return {"ok": ok, "log": log, "files": files}


_img = {"guard": img_guard, "durable": img_durable, "data": img_data}[IMAGE]()


@app.function(image=_img, secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run_one(path: str, args: str = "", mode: str = "auto"):
    return _run(path, args, mode)


@app.local_entrypoint()
def main(script: str, args: str = "", mode: str = "auto"):
    res = run_one.remote(script, args, mode)
    for rel, data in res["files"].items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    print(res["log"])
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(res['files'])} files written back:")
    for rel in sorted(res["files"])[:80]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
