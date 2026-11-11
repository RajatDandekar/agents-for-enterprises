"""Run Lecture 5's scripts and notebook on Modal from a snapshot (other builders edit other folders while we run).

    /Users/raj/.venv/bin/modal run lectures/L5-the-loop/experiments/run_modal.py --script lectures/L5-the-loop/experiments/l5_runs.py --args "race --repeats 3"
    /Users/raj/.venv/bin/modal run lectures/L5-the-loop/experiments/run_modal.py --nb lectures/L5-the-loop/NB5_the_loop.ipynb --mode replay

Like tools/modal_run.py (same image, same key handling: the Gemini key is read from LEDGER_ENV_FILE, default
wm-lecture6-ijepa/.env, and sent as a Modal secret, never printed), but it uploads a snapshot of only ledgerline/ (with
the L5v4_* cassettes) and lectures/L5-the-loop/, so a file another builder saves mid-upload cannot break the run.
Files the run creates or changes (logs, cassettes, the executed notebook) are copied back.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

import modal

_P = pathlib.Path(__file__).resolve().parents
ROOT = _P[3] if len(_P) > 3 else _P[-1]
ENV_FILE = os.environ.get("LEDGER_ENV_FILE", "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
SNAP = pathlib.Path(os.environ.get("L5_SNAP", "/private/tmp/l5v5_run_snap"))
KEYS = ("GEMINI_API_KEY", "GOOGLE_API_KEY")

if modal.is_local():
    SNAP.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude", "__pycache__/", "--exclude", "qa/", "--exclude", "*.mp4",
                    "--exclude", "*.webm", "--exclude", "*.png", "--exclude", "*.jpg", "--exclude", "archive_v3/",
                    "--exclude", "films/", "--exclude", "figs/", "--exclude", "brainlab/", "--exclude", "raglab/", "--exclude", "wiki/",
                    "--include", "ledgerline/", "--include", "ledgerline/ledgerline/", "--include", "ledgerline/pyproject.toml",
                    "--include", "ledgerline/ledgerline/cassettes/", "--include", "ledgerline/ledgerline/cassettes/L5v4_*",
                    "--exclude", "ledgerline/ledgerline/cassettes/*", "--include", "ledgerline/ledgerline/**",
                    "--include", "lectures/", "--include", "lectures/L5-the-loop/***", "--exclude", "*",
                    str(ROOT) + "/", str(SNAP) + "/"], check=True)


def _secret_env():
    env = {}
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in KEYS:
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi", "httpx", "pydantic>=2", "pyyaml", "numpy", "rank_bm25", "jsonschema",
                 "nbformat", "nbclient", "ipykernel", "tabulate", "fastembed")
    .env({"PYTHONPATH": "/course/ledgerline", "LEDGER_IN_MODAL": "1"})
    .add_local_dir(SNAP, "/course")
)
app = modal.App("l5v5-runs", image=image)
secret = modal.Secret.from_dict(_secret_env() if modal.is_local() else {})


def _snap(root="/course"):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for f in fns:
            p = os.path.join(dp, f)
            st = os.stat(p)
            out[p] = (st.st_size, st.st_mtime)
    return out


@app.function(secrets=[secret], timeout=3600, cpu=4, memory=8192)
def run(kind: str, path: str, args: str = "", mode: str = "auto") -> dict:
    os.environ["LEDGER_LLM_MODE"] = mode
    os.environ.pop("OPENROUTER_API_KEY", None)
    before = _snap()
    full = os.path.join("/course", path)
    ok, log = True, ""
    if kind == "script":
        p = subprocess.run([sys.executable, full, *args.split()], cwd=os.path.dirname(full), capture_output=True, text=True,
                           timeout=3500)
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
        ok = ok and not errs
    after = _snap()
    files = {os.path.relpath(p, "/course"): open(p, "rb").read() for p, sig in after.items()
             if before.get(p) != sig and os.path.getsize(p) < 40_000_000}
    return {"ok": ok, "log": log, "files": files}


@app.local_entrypoint()
def main(script: str = "", nb: str = "", args: str = "", mode: str = "auto"):
    kind, path = ("script", script) if script else ("nb", nb)
    res = run.remote(kind, path, args, mode)
    for rel, data in res["files"].items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.endswith(".jsonl") and dst.exists():
            have = dst.read_bytes().splitlines()
            seen = set(have)
            extra = [l for l in data.splitlines() if l and l not in seen]
            dst.write_bytes(b"\n".join(have + extra) + b"\n")
        else:
            dst.write_bytes(data)
    print(res["log"])
    print(f"\n{'OK' if res['ok'] else 'FAILED'} · {len(res['files'])} files written back:")
    for rel in sorted(res["files"])[:60]:
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    if not res["ok"]:
        sys.exit(1)
