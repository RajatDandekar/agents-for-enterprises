"""Lecture 7's Modal runner (builder A): the notebooks and the experiments behind them.

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script nb_run.py --image clean --args "--nb NB7a_guards --mode live"
    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script attacks_run.py --image guards --args "--sets code"

The images are Lecture 6's own (imported from its l6_modal.py, so nothing is defined twice):
    clean   Python 3.12 and only the course package's dependencies; NO Anthropic key in the container. The notebooks run
            here, live through the Argus gateway (a test student's join key) or in replay.
    guards  Python 3.11, the course, Presidio, transformers + torch (CPU), the ProtectAI classifier; the Anthropic key from
            the Modal secret forge-anthropic. The experiments that need many model calls run here.
Mounted: ledgerline/, Lecture 6's experiments/ (its 16 Nov logs and configs, read only) and this folder's notebooks, nb/ and
experiments/. Only files changed under this folder's NB7*, nb/ and experiments/ come back to the laptop.
"""
import hashlib
import importlib.util
import os
import pathlib
import shlex
import subprocess
import sys

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[3] if len(_P.parents) > 3 and (_P.parents[3] / "ledgerline").exists() else pathlib.Path("/course")
L6 = "lectures/L6-evals-guardrails-observability"
L7 = "lectures/L6b-guardrails"
OWN = (L7 + "/NB7", L7 + "/nb/", L7 + "/experiments/")

_spec = importlib.util.spec_from_file_location("l6_modal", ROOT / L6 / "experiments" / "l6_modal.py")
l6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(l6)                      # Lecture 6's images and pins: core, evals, clean, guards


def _nb(p) -> bool:
    """Of this folder's top level, mount only the notebooks (the deck's files change under us while the others work)."""
    q = pathlib.Path(p)
    return q.name.startswith("NB7") and q.suffix in (".py", ".ipynb") and q.parent.name in ("", ".", "L6b-guardrails")


def _mount(img):
    return (img.add_local_dir(ROOT / "ledgerline", "/course/ledgerline", ignore=lambda p: not l6._keep(p))
            .add_local_dir(ROOT / L6 / "experiments", "/course/" + L6 + "/experiments", ignore=lambda p: not l6._keep(p))
            .add_local_dir(ROOT / L7 / "experiments", "/course/" + L7 + "/experiments", ignore=lambda p: not l6._keep(p))
            .add_local_dir(ROOT / L7 / "nb", "/course/" + L7 + "/nb", ignore=lambda p: not l6._keep(p))
            .add_local_dir(ROOT / L7, "/course/" + L7, ignore=lambda p: not _nb(p)))


app = modal.App("l7-guardrails-red-teaming")
key = [modal.Secret.from_name("forge-anthropic")]


def _go(kind: str, path: str, args: str) -> dict:
    os.environ.pop("OPENROUTER_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)
    before = l6._snap()
    exp = f"/course/{L7}/experiments"
    if kind == "script":
        p = subprocess.run([sys.executable, os.path.join(exp, path), *shlex.split(args)], cwd=exp, capture_output=True,
                           text=True, timeout=7000)
    else:
        p = subprocess.run(args, shell=True, cwd=os.path.join(exp, path or "."), capture_output=True, text=True, timeout=7000)
    log = p.stdout[-40000:] + "\n--- stderr ---\n" + p.stderr[-12000:] + f"\nexit {p.returncode}"
    after = l6._snap()
    files = {os.path.relpath(q, "/course"): open(q, "rb").read() for q, sig in after.items() if before.get(q) != sig}
    return {"ok": p.returncode == 0, "log": log, "files": files}


@app.function(image=_mount(l6.clean), timeout=7200, cpu=4, memory=8192)
def run_clean(kind: str, path: str, args: str = "") -> dict:       # no Anthropic key in this container at all
    return _go(kind, path, args)


@app.function(image=_mount(l6.guards), secrets=key, timeout=7200, cpu=8, memory=16384)
def run_guards(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.function(image=_mount(l6.evals), secrets=key, timeout=7200, cpu=4, memory=8192)
def run_evals(kind: str, path: str, args: str = "") -> dict:
    return _go(kind, path, args)


@app.local_entrypoint()
def main(script: str = "", shell: str = "", cwd: str = "", args: str = "", image: str = "clean"):
    fn = {"clean": run_clean, "guards": run_guards, "evals": run_evals}[image]
    res = fn.remote("script", script, args) if script else fn.remote("shell", cwd, shell)
    skipped, wrote = [], []
    for rel, data in res["files"].items():
        if not rel.startswith(OWN) or "/__pycache__/" in rel:
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
