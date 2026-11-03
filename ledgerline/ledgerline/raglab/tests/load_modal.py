"""Load test of the DEPLOYED RAG Lab: N simulated students at once, from a Modal container.

    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/raglab/tests/load_modal.py --n 30

Each student loads options, picks a random setting from the grid (several chunkings, so indexes load concurrently),
then does 8 searches (golden and free questions), reads chunks and the map once, and submits to the leaderboard.
All N start together. Writes ledgerline/ledgerline/raglab/qa/load_<n>.json. Clean up with
`modal run deploy/raglab_modal.py::admin --cmd purge-tests`.
"""
import json
import pathlib
import random
import threading
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
URL = "https://rajatworkspace--northbridge-raglab.us-east.modal.run"
app = modal.App("northbridge-raglab-load", image=modal.Image.debian_slim(python_version="3.11").pip_install("httpx"))


@app.function(timeout=1800, cpu=4, memory=4096)
def load(n: int = 30, url: str = URL, searches: int = 8) -> dict:
    import httpx

    res = [None] * n
    barrier = threading.Barrier(n)
    opts = httpx.get(url + "/api/options", timeout=600).json()
    built = opts["built"]
    gold = opts["golden"]

    def student(i):
        rnd = random.Random(i)
        r = {"i": i, "errors": [], "search_ms": [], "server_ms": [], "first_ms": None}
        c = httpx.Client(base_url=url, timeout=300, headers={"X-Player": f"load{i}"})
        p, ch, size, o = rnd.choice(built).split("-")
        cfg = {"parser": p, "chunker": ch, "size": int(size), "overlap": int(o[1:]) / 100,
               "embed": rnd.choice(["bge-small", "bge-base", "e5-small", "gte-small", "nomic"]),
               "retrieval": rnd.choice(["dense", "bm25", "hybrid"]), "rerank": rnd.random() < 0.5, "k": rnd.choice([3, 5, 10])}
        r["cfg"] = cfg
        barrier.wait()
        try:
            for j in range(searches):
                q = rnd.choice(gold)["question"] if j % 2 == 0 else rnd.choice(["Who approves an order above £250,000?", "How long are e-mails kept?", "What is a W-CC-114 warning?", "Which warehouse holds battery packs?"])
                t = time.time()
                x = c.post("/api/search", json={"config": cfg, "question": q})
                ms = (time.time() - t) * 1000
                if x.status_code != 200:
                    r["errors"].append(f"{x.status_code} {x.text[:120]}")
                    continue
                d = x.json()
                r["search_ms"].append(round(ms, 1))
                r["server_ms"].append(d.get("local_ms"))
                if j == 0:
                    r["first_ms"] = round(ms, 1)
            t = time.time()
            x = c.get("/api/chunks", params={"config": json.dumps(cfg), "file": "05_master_data/SUPPLIER_MASTER.xlsx"})
            r["chunks_ms"] = round((time.time() - t) * 1000, 1) if x.status_code == 200 else r["errors"].append(f"chunks {x.status_code}")
            t = time.time()
            x = c.get("/api/map", params={"config": json.dumps(cfg)})
            r["map_ms"] = round((time.time() - t) * 1000, 1) if x.status_code == 200 else r["errors"].append(f"map {x.status_code}")
            x = c.post("/api/leaderboard", json={"name": f"Load Student {i:02d}", "config": cfg})
            if x.status_code != 200:
                r["errors"].append(f"board {x.status_code}")
        except Exception as e:  # noqa: BLE001
            r["errors"].append(repr(e)[:200])
        res[i] = r

    th = [threading.Thread(target=student, args=(i,)) for i in range(n)]
    t0 = time.time()
    [t.start() for t in th]
    [t.join() for t in th]

    def q(xs, p):
        xs = sorted(x for x in xs if x is not None)
        return round(xs[min(len(xs) - 1, int(p / 100 * len(xs)))], 1) if xs else None

    alls = [x for r in res for x in r["search_ms"]]
    srv = [x for r in res for x in r["server_ms"]]
    firsts = [r["first_ms"] for r in res]
    return {"n": n, "wall_s": round(time.time() - t0, 1), "searches": len(alls), "errors": sum(len(r["errors"]) for r in res),
            "error_samples": [e for r in res for e in r["errors"]][:10],
            "search_ms": {"p50": q(alls, 50), "p90": q(alls, 90), "p95": q(alls, 95), "max": q(alls, 100)},
            "server_search_ms": {"p50": q(srv, 50), "p95": q(srv, 95)},
            "first_search_ms (includes loading a new index)": {"p50": q(firsts, 50), "p95": q(firsts, 95), "max": q(firsts, 100)},
            "chunks_ms": {"p50": q([r.get("chunks_ms") for r in res], 50), "max": q([r.get("chunks_ms") for r in res], 100)},
            "map_ms": {"p50": q([r.get("map_ms") for r in res], 50), "max": q([r.get("map_ms") for r in res], 100)},
            "students": res}


@app.local_entrypoint()
def main(n: int = 30):
    r = load.remote(n)
    d = HERE.parent / "qa"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"load_{n}.json").write_text(json.dumps(r, indent=1))
    print(json.dumps({k: v for k, v in r.items() if k != "students"}, indent=1))
