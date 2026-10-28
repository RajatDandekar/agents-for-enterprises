"""Ask Rasoi on a local model: Ollama on a Modal GPU, the same twelve tasks, our L5 harness, tools over MCP.

    tools/mrun.sh lectures/L8-frameworks/experiments/ollama_modal.py --models qwen3.5:9b,gpt-oss:20b

Nothing in this container can reach a cloud model: no API key is attached, and the harness talks only to
http://127.0.0.1:11434/v1 (Ollama's OpenAI-compatible API). The model weights are pulled once from the Ollama
library; after that, prompts, tool results and Bahi's data never leave the machine.
Writes logs/fw_ours_ollama_<model>.json and cassette IND8_fw_ours_ollama_<model>.jsonl (so the notebook replays it with no GPU).
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import modal

_here = pathlib.Path(__file__).resolve()
ROOT = _here.parents[3] if len(_here.parents) > 3 else pathlib.Path("/course")
STAGE = pathlib.Path(f"/private/tmp/l8ollama-{os.getpid()}")
OURS = ("lectures/L8-frameworks/", "bahi/bahi/cassettes/IND8_")
OLLAMA = "ollama/ollama:0.40.3"
GPU = "L4"


def _stage():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    ex = ["--exclude", "__pycache__", "--exclude", "qa", "--exclude", "*.png", "--exclude", "*.mp4"]
    subprocess.run(["rsync", "-a", *ex, "--exclude", "cassettes/*", str(ROOT / "bahi"), str(STAGE)], check=True)
    (STAGE / "bahi/bahi/cassettes").mkdir(parents=True, exist_ok=True)
    for c in (ROOT / "bahi/bahi/cassettes").glob("IND8_fw_ours_ollama*"):
        shutil.copy2(c, STAGE / "bahi/bahi/cassettes" / c.name)
    (STAGE / "lectures").mkdir(exist_ok=True)
    subprocess.run(["rsync", "-a", *ex, str(ROOT / "lectures/L8-frameworks"), str(STAGE / "lectures")], check=True)
    return STAGE


image = (
    modal.Image.from_registry(OLLAMA, add_python="3.11")
    .entrypoint([])
    .pip_install("openai>=2.45,<3", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "pandas", "fastmcp", "mcp",
                 "langgraph==1.2.15", "langchain-core", "fastembed", "rank_bm25", "numpy")
    .env({"PYTHONPATH": "/course/bahi", "OLLAMA_CONTEXT_LENGTH": "32768", "OLLAMA_NUM_PARALLEL": "4",
          "OLLAMA_KEEP_ALIVE": "60m", "OLLAMA_HOST": "127.0.0.1:11434"})
    .add_local_dir(_stage() if modal.is_local() else "/tmp", "/course")
)
app = modal.App("l8-ollama", image=image)


def _snap(root="/course"):
    out = {}
    for dp, dns, fns in os.walk(root):
        for f in fns:
            p = os.path.join(dp, f)
            st = os.stat(p)
            out[p] = (st.st_size, st.st_mtime)
    return out


@app.function(gpu=GPU, timeout=3600, cpu=4, memory=16384)
def run(models: str, only: str = "", workers: int = 4) -> dict:
    before = _snap()
    log = []
    srv = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        if subprocess.run(["ollama", "list"], capture_output=True).returncode == 0:
            break
        time.sleep(1)
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    log.append(f"GPU {gpu}; ollama {subprocess.run(['ollama', '--version'], capture_output=True, text=True).stdout.strip()}")
    for m in models.split(","):
        t0 = time.time()
        p = subprocess.run(["ollama", "pull", m], capture_output=True, text=True)
        log.append(f"pull {m}: rc={p.returncode} in {time.time() - t0:.0f}s {p.stderr[-300:] if p.returncode else ''}")
        t1 = time.time()
        slug = "_ollama_" + m.replace(":", "_").replace(".", "")
        r = subprocess.run([sys.executable, "/course/lectures/L8-frameworks/experiments/exp_frameworks.py", "--fw", "ours",
                            "--model", "ollama:" + m, "--tag", slug, "--ctag", slug, "--workers", str(workers)]
                           + (["--only", only] if only else []),
                           capture_output=True, text=True, timeout=3000, cwd="/course/lectures/L8-frameworks/experiments")
        log.append(f"--- {m} ({time.time() - t1:.0f}s)\n{r.stdout[-12000:]}\n--- stderr\n{r.stderr[-4000:]}")
        ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True).stdout
        log.append("ollama ps:\n" + ps)
    srv.terminate()
    after = _snap()
    files = {os.path.relpath(p, "/course"): open(p, "rb").read() for p, sig in after.items() if before.get(p) != sig}
    return {"log": "\n".join(log), "files": files}


@app.local_entrypoint()
def main(models: str = "qwen3.5:9b", only: str = "", workers: int = 4):
    res = run.remote(models, only, workers)
    kept = []
    for rel, data in res["files"].items():
        if rel.startswith(OURS):
            dst = ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            kept.append(rel)
    print(res["log"])
    print(f"\n{len(kept)} files written back:")
    for rel in sorted(kept):
        print("  ", rel, hashlib.md5(res["files"][rel]).hexdigest()[:6])
    shutil.rmtree(STAGE, ignore_errors=True)
