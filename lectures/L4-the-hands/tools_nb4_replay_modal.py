"""Replay NB4 top to bottom on Modal with no key, with Henrik's service definitions mounted (as a student's clone would be).

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L4-the-hands/tools_nb4_replay_modal.py

The same image and run as tools/modal_run.py --nb ... --mode replay, plus northbridge-docs/04_service_definitions mounted
at /northbridge-docs (NORTHBRIDGE_DOCS points there, so the notebook does not need to clone). Writes the executed
notebook back.
"""
import os
import pathlib

import modal

_HERE = pathlib.Path(__file__).resolve()
LOCAL = len(_HERE.parents) > 2
ROOT = _HERE.parents[2] if LOCAL else pathlib.Path("/course")
DOCS = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
NB = "lectures/L4-the-hands/NB4_the_hands.ipynb"
SKIP = {".git", "qa", "archive", "archive_v3", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist", ".venv", "films"}

image = (modal.Image.debian_slim(python_version="3.11").apt_install("git")
         .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "numpy", "pandas", "matplotlib",
                      "rank_bm25", "scikit-learn", "langgraph>=0.2", "langchain-core", "fastmcp", "mcp", "nbformat", "nbclient",
                      "ipykernel", "jsonschema", "fastembed")
         .env({"PYTHONPATH": "/course/ledgerline", "LEDGER_IN_MODAL": "1", "LEDGER_LLM_MODE": "replay", "NORTHBRIDGE_DOCS": "/northbridge-docs"}))
if LOCAL:
    image = (image.add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                                 or str(p).endswith((".mp4", ".mov", ".zip", ".env", ".webm")))
             .add_local_dir(DOCS / "04_service_definitions", "/northbridge-docs/04_service_definitions"))
app = modal.App("l4-nb4-replay", image=image)


@app.function(timeout=1800, cpu=2, memory=4096)
def run() -> dict:
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    full = f"/course/{NB}"
    nb = nbformat.read(full, as_version=4)
    log = ""
    try:
        NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(full)}}).execute()
    except CellExecutionError as e:
        log = str(e)[-6000:]
    code = [c for c in nb.cells if c.cell_type == "code"]
    errs = sum(1 for c in code for o in c.get("outputs", []) if o.get("output_type") == "error")
    return {"nb": nbformat.writes(nb), "cells": len(code), "errors": errs, "log": log}


@app.local_entrypoint()
def main():
    r = run.remote()
    (ROOT / NB).write_text(r["nb"])
    print(r["log"])
    print(f"executed {r['cells']} code cells, {r['errors']} errors")
