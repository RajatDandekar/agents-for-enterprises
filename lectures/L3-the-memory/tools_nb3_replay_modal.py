"""Replay NB3 top to bottom on Modal with no key, the way a student runs it: a CPU machine, the course package, and a
real `git clone` of github.com/RajatDandekar/northbridge-docs (NORTHBRIDGE_DOCS is NOT set, so the notebook clones).

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L3-the-memory/tools_nb3_replay_modal.py

Model calls replay from the cassettes in the package (LEDGER_LLM_MODE=replay: a request that was never recorded is an
error, not a live call). Writes the executed notebook back, and prints the cell count, the errors and the run time.
"""
import os
import pathlib
import time

import modal

_HERE = pathlib.Path(__file__).resolve()
LOCAL = len(_HERE.parents) > 2
ROOT = _HERE.parents[2] if LOCAL else pathlib.Path("/course")
NB = "lectures/L3-the-memory/NB3_the_memory.ipynb"
SKIP = {".git", "qa", "archive", "archive_v3", "archive_v4", "node_modules", "__pycache__", ".ipynb_checkpoints", "site-dist",
        ".venv", "films", "brainlab", "legacy_ui", "wiki_explorer"}

image = (modal.Image.debian_slim(python_version="3.11").apt_install("git", "tesseract-ocr")
         .pip_install("openai>=1.50", "httpx", "pydantic>=2", "pyyaml", "numpy<2.1", "pandas", "scipy", "nbformat", "nbclient",
                      "ipykernel", "pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2",
                      "tiktoken==0.8.0", "pytesseract==0.3.13", "pillow==11.0.0", "chromadb==1.0.15")
         .pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1",
                      extra_index_url="https://download.pytorch.org/whl/cpu")
         .env({"PYTHONPATH": "/course/ledgerline", "LEDGER_IN_MODAL": "1", "LEDGER_LLM_MODE": "replay",
               "TOKENIZERS_PARALLELISM": "false"}))
if LOCAL:  # only what a student has: the course package, the notebook, and the race log the last section reads
    image = (image.add_local_dir(ROOT / "ledgerline", "/course/ledgerline", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                                 or str(p).endswith((".mp4", ".mov", ".zip", ".env", ".webm", ".png", ".jpg", ".gif")))
             .add_local_file(ROOT / NB, f"/course/{NB}")
             .add_local_file(ROOT / "lectures/L3-the-memory/experiments/logs/race.json",
                             "/course/lectures/L3-the-memory/experiments/logs/race.json"))
app = modal.App("l3-nb3-replay", image=image)


@app.function(timeout=3600, cpu=4, memory=16384)
def run() -> dict:
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    assert "NORTHBRIDGE_DOCS" not in os.environ
    full = f"/course/{NB}"
    nb = nbformat.read(full, as_version=4)
    log, t0 = "", time.time()
    try:
        NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(full)}}).execute()
    except CellExecutionError as e:
        log = str(e)[-6000:]
    code = [c for c in nb.cells if c.cell_type == "code"]
    errs = sum(1 for c in code for o in c.get("outputs", []) if o.get("output_type") == "error")
    cloned = os.path.exists(os.path.join(os.path.dirname(full), "northbridge-docs", ".git"))
    return {"nb": nbformat.writes(nb), "cells": len(code), "errors": errs, "log": log, "seconds": round(time.time() - t0),
            "cloned": cloned}


@app.local_entrypoint()
def main():
    r = run.remote()
    (ROOT / NB).write_text(r["nb"])
    print(r["log"])
    print(f"executed {r['cells']} code cells, {r['errors']} errors, {r['seconds']} s, cloned from GitHub: {r['cloned']}")
