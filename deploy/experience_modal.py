"""The Northbridge Experience on Modal: app `northbridge-experience`, one container, the whole cohort on one link.

    /Users/raj/.venv/bin/modal deploy deploy/experience_modal.py                       # deploy (or update) the live app
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::test                    # the in-process test, live model
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd status      # spend, players, flags
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/experience_modal.py::admin --cmd cap --cap 3000

Live URL: https://rajatworkspace--northbridge-experience.us-east.modal.run (also in ledgerline/ledgerline/experience/DEPLOYED.md).

Why one container: every player's Northbridge (their Ledgerline sandbox) lives in memory, so all requests must reach the same
process (max_containers=1, @modal.concurrent). Player names, wishlists, mission scores, the operator's flags and
today's spend live in the modal.Dict `northbridge-experience-state`, so a restart loses only the sandboxes, which are
re-seeded on demand. Keys come from the Modal secret `northbridge-experience` (GEMINI_API_KEY, NORTHBRIDGE_ADMIN_TOKEN); they are
never in the image. A cron warms the container before the weekend classes (Sat and Sun, 7-9 AM GMT).
Do not redeploy during a class: a new container starts every player's Northbridge again from Monday 9:00.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = "https://rajatworkspace--northbridge-experience.us-east.modal.run"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "pandas", "numpy",
                 "rank_bm25", "fastembed", "fastmcp", "mcp", "jsonschema")
    .env({"PYTHONPATH": "/app/ledgerline", "FASTEMBED_CACHE_PATH": "/models/fastembed", "NORTHBRIDGE_NO_APP": "1",
          "LEDGER_LLM_MODE": "live", "NORTHBRIDGE_DICT": "northbridge-experience-state", "PYTHONUNBUFFERED": "1",
          "NORTHBRIDGE_REASONING": "low"})
    .run_commands("python -c \"from fastembed import TextEmbedding; from fastembed.rerank.cross_encoder import "
                  "TextCrossEncoder; TextEmbedding('BAAI/bge-small-en-v1.5'); TextCrossEncoder('Xenova/ms-marco-MiniLM-L-6-v2')\"")
    # Lecture 3's knowledge stage: search_docs runs the race winner (BM25 + bge-reranker-base) on this CPU
    .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("transformers==4.46.3", "sentence-transformers==3.3.1", "scipy", "tiktoken==0.8.0")
    .env({"HF_HOME": "/models/hf", "RAG_INDEX_DIR": "/rvol/chroma", "TOKENIZERS_PARALLELISM": "false",
          "NORTHBRIDGE_GPU_DOCS": "northbridge-experience/Docs"})
    .run_commands("python -c \"from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')\"")
    .add_local_dir(ROOT / "ledgerline", "/app/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".env", ".png", ".mp4", ".ipynb")))
)
# search_docs on a GPU, as the race measured it (an L4, the reranker in fp16): the web container calls Docs.search;
# the CPU copy above is only the fallback (about 5 s a search on 4 vCPU instead of about 50 ms)
docs_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "scipy", "numpy<2.1",
                 "pyyaml", "pydantic>=2", "tiktoken==0.8.0")
    .env({"HF_HOME": "/models/hf", "RAG_INDEX_DIR": "/rvol/chroma", "TOKENIZERS_PARALLELISM": "false",
          "PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1"})
    .run_commands("python -c \"from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')\"")
    .pip_install("openai>=1.50", "httpx", "pandas", "rank_bm25", "jsonschema")
    .add_local_dir(ROOT / "ledgerline", "/app/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".env", ".png", ".mp4", ".ipynb")))
)
app = modal.App("northbridge-experience", image=image)
secret = modal.Secret.from_name("rasoi-experience")  # secret name kept from v3 (holds the admin token and keys)
# the RAG Lab's volume, read only here: search_docs loads the best index (chunks + BM25) from /rvol/chroma/<chunking>
ragvol = modal.Volume.from_name("northbridge-raglab")


@app.cls(image=docs_image, gpu="L4", cpu=4, memory=16384, volumes={"/rvol": ragvol}, max_containers=1,
         min_containers=0, scaledown_window=1200, timeout=600)
@modal.concurrent(max_inputs=8)
class Docs:
    """The race winner, warm: BM25 + bge-reranker-base over the best index, filtered by role, plus the withheld notice."""

    @modal.enter()
    def load(self):
        sys.path.insert(0, "/app/ledgerline")
        from ledgerline.course.l3 import rag

        rag.rag_search("warm-up: What does ERR-PO-0412 mean?", role="PUR-EXEC", k=3)
        self.rag = rag

    @modal.method()
    def search(self, question: str, role: str, k: int = 10, withheld: bool = False) -> list:
        return self.rag.rag_search(question, role=role, k=k, withheld=withheld)


@app.function(secrets=[secret], max_containers=1, min_containers=0, scaledown_window=1800, cpu=4, memory=8192,
              timeout=900, volumes={"/rvol": ragvol})
@modal.concurrent(max_inputs=250)
@modal.asgi_app(label="northbridge-experience")
def web():
    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.experience.app import create_app

    return create_app()


@app.function(schedule=modal.Cron("20 1 * * 6,0"), timeout=300)  # 01:20 UTC = 06:50 IST, Saturday and Sunday
def warm():
    import urllib.request

    for _ in range(6):  # the web container starts, then warms the GPU search (docs) in the background
        try:
            h = json.loads(urllib.request.urlopen(URL + "/healthz", timeout=60).read())
            print(h)
            if (h.get("docs") or {}).get("ok"):
                return
            time.sleep(30)
        except Exception as e:  # noqa: BLE001
            print("warm failed:", e)
            time.sleep(10)


@app.function(secrets=[secret], timeout=2400, cpu=4, memory=8192, volumes={"/rvol": ragvol})
def run_test(reasoning: str = "", model: str = "") -> dict:
    env = {**os.environ, "NORTHBRIDGE_DICT": "", "NORTHBRIDGE_NO_APP": "1", "NORTHBRIDGE_REASONING": reasoning}
    if model:
        env["NORTHBRIDGE_MODEL"] = model
    p = subprocess.run([sys.executable, "/app/ledgerline/ledgerline/experience/tests/test_experience.py"], capture_output=True,
                       text=True, env=env, timeout=2300)
    logs = {}
    d = pathlib.Path("/app/ledgerline/ledgerline/experience/tests/logs")
    for f in d.glob("*.json"):
        logs[f.name] = f.read_text()
    return {"code": p.returncode, "out": p.stdout[-30000:], "err": p.stderr[-6000:], "logs": logs}


@app.local_entrypoint()
def test(reasoning: str = "", model: str = ""):
    r = run_test.remote(reasoning, model)
    print(r["out"])
    if r["code"]:
        print("--- stderr ---\n" + r["err"])
    d = ROOT / "ledgerline" / "ledgerline" / "experience" / "tests" / "logs"
    d.mkdir(parents=True, exist_ok=True)
    for name, text in r["logs"].items():
        (d / name).write_text(text)
        print("wrote", d / name)


KNOWLEDGE_QS = [("ECLARKE", "Can I buy the battery packs from Brightcell Energy? They quote £104."),
                ("ECLARKE", "What does ERR-PO-0412 mean and how do I fix it?"),
                ("ECLARKE", "What is the salary band for a senior buyer?")]


@app.function(secrets=[secret], timeout=1800, cpu=4, memory=8192, volumes={"/rvol": ragvol})
def record_knowledge_remote() -> dict:
    """Lecture 3: Ask Northbridge at the knowledge stage on three questions, in-process, recorded to cassette
    L3v4_knowledge (NB3 and the deck replay it). Each turn keeps its tool cards, timing, tokens and the context."""
    os.environ.update({"NORTHBRIDGE_CASSETTE": "L3v4_knowledge", "NORTHBRIDGE_LLM_MODE": "auto",
                       "LEDGER_CASSETTES": "/tmp/cass"})
    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.experience.app import use_gpu_docs

    use_gpu_docs()
    from ledgerline.course.l3 import rag
    from ledgerline.erp.engine import ERP
    from ledgerline.experience import harness as H
    from ledgerline.experience.players import guard_erp

    t0 = time.time()
    rag.rag_search("warm-up", k=1)
    warm = round(time.time() - t0, 1)
    turns = []
    for user, q in KNOWLEDGE_QS:
        a = H.AskNorthbridge(guard_erp(ERP()), user, "knowledge")
        r = a.respond(q)
        turns.append({"user": user, "question": q, **r, "messages": a.messages, "tools_seen": [s["function"]["name"] for s in a.schemas]})
        a.close()
    cass = {p.name: p.read_text() for p in pathlib.Path("/tmp/cass").glob("*.jsonl")}
    return {"turns": turns, "warm_seconds": warm, "_cassettes": cass, "model": H.MODEL}


@app.local_entrypoint()
def record_knowledge():
    r = record_knowledge_remote.remote()
    cdir = ROOT / "ledgerline" / "ledgerline" / "cassettes"
    for name, text in r.pop("_cassettes").items():
        dst = cdir / name
        have = dst.read_text().splitlines() if dst.exists() else []
        extra = [l for l in text.splitlines() if l and l not in set(have)]
        if extra:
            dst.write_text("\n".join(have + extra) + "\n")
            print(f"cassette {name}: +{len(extra)}")
    out = ROOT / "lectures" / "L3-the-memory" / "experiments" / "logs" / "knowledge_stage.json"
    out.write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    for t in r["turns"]:
        print(f"\n> {t['question']}\n  tools: {[c['tool'] for c in t['cards']]}  {t['seconds']} s\n  {t['reply']}")
    print("wrote", out)


@app.function(secrets=[secret], timeout=300, image=modal.Image.debian_slim(python_version="3.11").pip_install("httpx"))
def op(cmd: str, reason: str = "", cap: float = 0) -> dict:
    """Operator commands, run inside Modal so the admin token never leaves the secret store."""
    import httpx

    h = {"X-Admin-Token": os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ["RASOI_ADMIN_TOKEN"]}
    c = httpx.Client(base_url=URL, timeout=120)
    if cmd == "pause":
        c.post("/api/admin/flags", json={"model_enabled": False, "reason": reason}, headers=h).raise_for_status()
    elif cmd == "resume":
        c.post("/api/admin/flags", json={"model_enabled": True, "reason": ""}, headers=h).raise_for_status()
    elif cmd == "cap":
        c.post("/api/admin/flags", json={"cap_inr": cap}, headers=h).raise_for_status()
    s = c.get("/api/admin/status", headers=h)
    s.raise_for_status()
    out = s.json()
    out.pop("recent", None)
    out["no_token_status"] = c.get("/api/admin/status").status_code
    return out


@app.local_entrypoint()
def admin(cmd: str = "status", reason: str = "", cap: float = 0):
    print(json.dumps(op.remote(cmd, reason, cap), indent=1, ensure_ascii=False))
