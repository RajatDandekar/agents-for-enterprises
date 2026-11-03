"""The RAG Lab on Modal (Lecture 3): app `northbridge-raglab`, workspace rajatworkspace.

    M=/Users/raj/.venv/bin/modal
    $M deploy deploy/raglab_modal.py                          # deploy (or update) the live app
    $M run deploy/raglab_modal.py::admin --cmd status         # spend estimate, flags, leaderboard size
    $M run deploy/raglab_modal.py::admin --cmd warm           # keep one GPU container on (class)
    $M run deploy/raglab_modal.py::admin --cmd cool           # let it sleep
    $M run deploy/raglab_modal.py::admin --cmd pause --reason "back in 5 minutes"     # or resume
    $M run deploy/raglab_modal.py::admin --cmd cap --cap 25
    $M run deploy/raglab_modal.py::admin --cmd purge-all      # empty the leaderboard (purge-tests: test names only)
    $M run deploy/raglab_modal.py::test                        # in-process API test against the real indexes (GPU)

One GPU class (L4, 4 vCPU, 16 GiB) serves the whole app: the five embedding models and the reranker are loaded once,
indexes are copied from the Volume `northbridge-raglab` to local disk on first use. It is the same machine type the
grid measured latency on, so a live query's milliseconds are comparable with the golden-set numbers.
State (flags, the day's spend estimate, the leaderboard) is in the modal.Dict `northbridge-raglab-state`.
The admin token is the Modal secret `northbridge-raglab` (RAGLAB_ADMIN_TOKEN); never in the image or the repo.
Warm/cool: min_containers is 0 here. A cron warms one container at 00:30 UTC on Sat 7 Nov (06:00 IST, class 07:00-09:00 IST)
and a daily cron at 04:00 UTC (09:30 IST) lets it sleep. A redeploy also resets min_containers to 0.
"""
import json
import os
import pathlib
import sys
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = "northbridge-raglab"
URL = "https://rajatworkspace--northbridge-raglab.us-east.modal.run"
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "app", "studio"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops", "chromadb==1.0.15",
                 "numpy<2.1", "scipy", "fastapi==0.115.6", "uvicorn", "anyio", "httpx", "pydantic>=2", "openai>=1.50",
                 "pyyaml", "tiktoken==0.8.0")
    .env({"HF_HOME": "/hf"})
    .run_commands(
        "python -c \"from sentence_transformers import SentenceTransformer as S, CrossEncoder as C; "
        "[S(m, trust_remote_code=True) for m in ['BAAI/bge-small-en-v1.5','BAAI/bge-base-en-v1.5','intfloat/e5-small-v2',"
        "'thenlper/gte-small','nomic-ai/nomic-embed-text-v1.5']]; C('BAAI/bge-reranker-base')\"",
        "python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .env({"HF_HUB_OFFLINE": "1", "PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1", "TOKENIZERS_PARALLELISM": "false",
          "NORTHBRIDGE_DOCS": "/dump", "RAGLAB_VOL": "/vol", "RAGLAB_DICT": "northbridge-raglab-state",
          "RAGLAB_PRELOAD": "structured-structure-400-o0,structured-structure-200-o15", "LEDGER_CASSETTES": "/tmp/cassettes"})
    .add_local_dir(ROOT / "ledgerline" / "ledgerline", "/app/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4", ".jsonl", ".env")))
    .add_local_dir(DUMP / "eval", "/dump/eval")
    .add_local_file(DUMP / "README.md", "/dump/README.md")
)
app = modal.App(APP)
vol = modal.Volume.from_name("northbridge-raglab", create_if_missing=True)
secret = modal.Secret.from_name("northbridge-raglab")


@app.cls(image=image, gpu="L4", cpu=4, memory=32768, min_containers=0, max_containers=2,
         scaledown_window=900, timeout=600, volumes={"/vol": vol}, secrets=[secret])
@modal.concurrent(max_inputs=80, target_inputs=60)
class Lab:
    @modal.enter()
    def load(self):
        sys.path.insert(0, "/app/ledgerline")
        from ledgerline.course.l3 import rag as R
        from ledgerline.raglab.app import create_app
        from ledgerline.raglab.engine import Engine

        t0 = time.time()
        for m in R.EMBED_MODELS:
            R.Embedder(m).query("warm up")
        R.Reranker().score("warm up", ["warm up"])
        self.engine = Engine(preload=os.environ["RAGLAB_PRELOAD"].split(","))
        self.web = create_app(self.engine)

        def follow():  # new grid results, answers and indexes become visible without a redeploy
            import threading

            while True:
                time.sleep(180)
                try:
                    vol.reload()
                    self.engine.refresh()
                except Exception as e:  # noqa: BLE001
                    print("volume reload skipped:", str(e)[:200])

        import threading

        threading.Thread(target=follow, daemon=True).start()
        threading.Thread(target=self.engine.prefetch, args=(self.engine.built(),), daemon=True).start()
        print(f"lab loaded in {time.time() - t0:.1f}s; {len(self.engine.built())} indexes built, {len(self.engine.grid)} grid rows")

    @modal.asgi_app(label=APP)
    def serve(self):
        return self.web


def _autoscale(n: int):
    modal.Cls.from_name(APP, "Lab")().update_autoscaler(min_containers=n)


@app.function(image=image, schedule=modal.Cron("30 0 7 11 *"), timeout=600)  # Sat 7 Nov 00:30 UTC = 06:00 IST
def class_warm():
    import urllib.request

    _autoscale(1)
    for _ in range(10):
        try:
            print(urllib.request.urlopen(URL + "/healthz", timeout=120).read()[:300])
            break
        except Exception as e:  # noqa: BLE001
            print("warm failed:", e)
            time.sleep(15)


@app.function(image=image, schedule=modal.Cron("0 4 * * *"), timeout=120)  # every day 04:00 UTC = 09:30 IST
def class_cool():
    _autoscale(0)
    print("min_containers -> 0")


# ---------------------------------------------------------------------------------------------- tests and admin
@app.function(image=image, gpu="L4", cpu=4, memory=16384, volumes={"/vol": vol}, timeout=1800)
def run_test() -> dict:
    sys.path.insert(0, "/app/ledgerline")
    os.environ["RAGLAB_ADMIN_TOKEN"] = "test-token"
    from fastapi.testclient import TestClient

    from ledgerline.raglab.app import Store, create_app

    res = []

    def check(name, ok, **kw):
        res.append({"check": name, "ok": bool(ok), **kw})
        print(("OK   " if ok else "FAIL ") + name, json.dumps(kw, default=str)[:300], flush=True)

    c = TestClient(create_app(store=Store(None), heartbeat=False))
    t = time.time()
    h = c.get("/healthz").json()
    check("healthz: indexes and grid rows loaded", h["built"] >= 1 and h["grid_rows"] >= 1, health=h, load_s=round(time.time() - t, 1))
    check("lab page", c.get("/").status_code == 200 and "RAG Lab" in c.get("/").text)
    check("sky.css shared from the Experience", c.get("/sky/sky.css").status_code == 200)
    check("board and admin pages", c.get("/board").status_code == 200 and c.get("/admin").status_code == 200)
    o = c.get("/api/options").json()
    check("options: 224 golden questions, 9 knobs", len(o["golden"]) == 224 and len(o["options"]) == 9, built=len(o["built"]))
    base = {"parser": "structured", "chunker": "structure", "size": 400, "overlap": 0, "embed": "bge-small", "retrieval": "hybrid", "rerank": True, "k": 5}
    m = c.post("/api/metrics", json={"config": base}).json()["metrics"]
    check("metrics for the default setting", m and m["recall@k"] is not None, recall=m and m["recall@k"], p95=m and m["p95_ms"])
    for name, cfg, q, role in [
        ("hybrid+rerank, Emma", base, "Can I buy the battery packs from Brightcell Energy? They quote £104.", "PUR-EXEC"),
        ("BM25 finds ERR-PO-0412", {**base, "retrieval": "bm25", "rerank": False}, "What does ERR-PO-0412 mean and how do I fix it?", "PUR-EXEC"),
        ("dense nomic", {**base, "retrieval": "dense", "embed": "nomic", "rerank": False}, "How do I onboard a new supplier?", "PUR-EXEC"),
        ("rewrite on a golden question (recorded)", {**base, "rewrite": True}, "What does ERR-PO-0412 mean and how do I fix it?", "PUR-EXEC"),
        ("free question", base, "Who signs box 7 of the onboarding form?", "PUR-EXEC"),
    ]:
        t = time.time()
        r = c.post("/api/search", json={"config": cfg, "question": q, "role": role})
        d = r.json()
        check(f"search: {name}", r.status_code == 200 and len(d.get("items", [])) == cfg["k"], ms=d.get("local_ms"),
              wall_ms=round((time.time() - t) * 1000), top=[i["cite"] for i in d.get("items", [])[:3]],
              gold=[i["gold"] for i in d.get("items", [])], map="map" in d and "error" not in d["map"])
    hr = c.post("/api/search", json={"config": base, "question": "What is the salary band for a senior buyer?", "role": "PUR-EXEC"}).json()
    check("permissions: Emma never sees HR-CONF chunks", not any("CONFIDENTIAL" in i["file"] for i in hr["items"]))
    hr2 = c.post("/api/search", json={"config": base, "question": "What is the salary band for a senior buyer?", "role": "HR-MGR"}).json()
    check("permissions: an HR manager does", any("CONFIDENTIAL" in i["file"] for i in hr2["items"]), top=[i["cite"] for i in hr2["items"][:2]])
    ch = c.get("/api/chunks", params={"config": json.dumps(base), "file": "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"}).json()
    check("chunks of the Purchase Policy", ch.get("n", 0) > 0, n=ch.get("n"))
    mp = c.get("/api/map", params={"config": json.dumps(base)}).json()
    check("map points", len(mp.get("points", [])) > 1000, n=len(mp.get("points", [])))
    s1 = c.post("/api/leaderboard", json={"name": "Test Student", "config": base}).json()
    s2 = c.post("/api/leaderboard", json={"name": "Test Student", "config": {**base, "retrieval": "dense", "rerank": False}}).json()
    b = c.get("/api/leaderboard").json()
    check("leaderboard keeps a student's best", s1["saved"] and not s2["saved"] and b["n"] == 1, best=b["rows"][0]["recall@5"])
    check("admin needs the token", c.get("/api/admin/status").status_code == 401)
    A = {"X-Admin": "test-token"}
    c.post("/api/admin/pause", headers=A, json={"reason": "test pause"})
    p = c.post("/api/search", json={"config": base, "question": "x"})
    check("pause refuses searches", p.status_code == 503 and "test pause" in p.json()["detail"])
    c.post("/api/admin/resume", headers=A)
    c.post("/api/admin/cap", headers=A, json={"cap_usd": 0})
    p = c.post("/api/search", json={"config": base, "question": "x"})
    check("the cost cap refuses searches", p.status_code == 503)
    c.post("/api/admin/cap", headers=A, json={"cap_usd": 15})
    check("purge-all empties the leaderboard", c.post("/api/admin/purge-all", headers=A).json()["removed"] == 1 and c.get("/api/leaderboard").json()["n"] == 0)
    return {"checks": res, "passed": sum(r["ok"] for r in res), "total": len(res)}


@app.local_entrypoint()
def test():
    r = run_test.remote()
    d = ROOT / "ledgerline" / "ledgerline" / "raglab" / "qa"
    d.mkdir(parents=True, exist_ok=True)
    (d / "test_api.json").write_text(json.dumps(r, indent=1))
    print(f"{r['passed']}/{r['total']} checks passed")


@app.local_entrypoint()
def admin(cmd: str = "status", reason: str = "", cap: float = 15.0, name: str = ""):
    import urllib.request

    tok = ""
    envf = ROOT / "ledgerline" / "ledgerline" / "raglab" / "admin.env"
    if envf.exists():
        for line in envf.read_text().splitlines():
            if line.startswith("RAGLAB_ADMIN_TOKEN="):
                tok = line.split("=", 1)[1].strip()
    if cmd in ("warm", "cool"):
        _autoscale(1 if cmd == "warm" else 0)
        print("min_containers ->", 1 if cmd == "warm" else 0)
        if cmd == "warm":
            print(urllib.request.urlopen(URL + "/healthz", timeout=300).read()[:300])
        return
    path = "/api/admin/status" if cmd == "status" else f"/api/admin/{cmd}"
    body = None if cmd == "status" else json.dumps({"reason": reason, "cap_usd": cap, "name": name}).encode()
    req = urllib.request.Request(URL + path, data=body, headers={"X-Admin": tok, "Content-Type": "application/json"},
                                 method="GET" if body is None else "POST")
    print(urllib.request.urlopen(req, timeout=300).read().decode())
