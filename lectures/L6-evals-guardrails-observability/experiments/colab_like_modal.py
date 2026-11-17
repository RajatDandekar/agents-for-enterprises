"""After a push: run the four Lecture 6 notebooks the way a fresh Colab does.

    MODAL_PROFILE=rajatworkspace modal run lectures/L6-evals-guardrails-observability/experiments/colab_like_modal.py

A bare Python 3.12 container with nothing of ours in it. Each notebook is downloaded from GitHub, its own first cells
pip-install the course from GitHub, and there is no key of any kind, so every cell replays our recorded run (fetched
from GitHub too). What this cannot show: a clash with a package Colab ships preinstalled.
"""
import modal

RAW = "https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/{ref}/lectures/L6-evals-guardrails-observability/"
NBS = ["NB6a_tracing", "NB6b_evals_deepeval", "NB6c_multiturn_evals", "NB6d_ragas"]
image = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
         .pip_install("nbclient==0.10.2", "nbformat==5.10.4", "ipykernel==6.29.5"))
app = modal.App("l6-colab-like")


@app.function(image=image, timeout=3600, cpu=4, memory=8192)
def run(nb: str, ref: str = "main") -> dict:
    import os
    import tempfile
    import urllib.request

    import nbformat
    from nbclient import NotebookClient

    for k in list(os.environ):
        if k.startswith(("ANTHROPIC_", "LANGFUSE_", "LANGSMITH_", "SENTRY_", "ARGUS_", "NB_RECORD")):
            os.environ.pop(k)
    with urllib.request.urlopen(RAW.format(ref=ref) + nb + ".ipynb", timeout=60) as f:
        n = nbformat.reads(f.read().decode(), as_version=4)
    for c in n.cells:                                     # only this run's outputs count
        if c.cell_type == "code":
            c.outputs, c.execution_count = [], None
    client = NotebookClient(n, timeout=1800, kernel_name="python3", resources={"metadata": {"path": tempfile.mkdtemp()}})
    err = None
    try:
        client.execute()
    except Exception as e:  # noqa: BLE001
        err = str(e)[-3000:]
    code = [c for c in n.cells if c.cell_type == "code"]
    text = "\n".join(o.get("text", "") for c in code for o in c.get("outputs", []) if o.get("output_type") == "stream")
    return {"nb": nb, "cells": len(code), "ran": sum(1 for c in code if c.get("execution_count")),
            "errors": sum(1 for c in code for o in c.get("outputs", []) if o.get("output_type") == "error"),
            "err": err, "head": text[:400], "tail": text[-1200:]}


@app.local_entrypoint()
def main(ref: str = "main"):
    bad = 0
    for r in run.map(NBS, kwargs={"ref": ref}):
        ok = not r["err"] and r["ran"] == r["cells"] and not r["errors"]
        bad += not ok
        print(f"{'OK    ' if ok else 'FAILED'} {r['nb']}: code cells {r['cells']}, ran {r['ran']}, errors {r['errors']}")
        print("   first lines:", " | ".join(r["head"].split("\n")[:3]))
        if not ok:
            print(r["err"] or "", "\n", r["tail"])
    raise SystemExit(1 if bad else 0)
