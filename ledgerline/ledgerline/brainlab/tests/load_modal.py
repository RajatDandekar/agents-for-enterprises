"""Load test of the DEPLOYED Brain Lab: N simulated students do the whole lab at once, from a Modal container.

    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/brainlab/tests/load_modal.py --n 30

Each student: join -> before (4 questions) -> save the pre-filled facts -> path A (context) -> train -> poll the queue
until finished. All N start within ~2 s (the worst case: the instructor says "now press Train"). Measures every
latency, the queue wait and position each student saw, and how many taught questions the trained brains got right.
Writes ledgerline/ledgerline/brainlab/qa/load_<n>.json. Remove the test players afterwards with
`modal run deploy/brainlab_modal.py::admin --cmd purge-tests`.
"""
import json
import pathlib
import statistics
import threading
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
URL = "https://rajatworkspace--northbridge-brainlab.us-east.modal.run"
app = modal.App("northbridge-brainlab-load", image=modal.Image.debian_slim(python_version="3.11").pip_install("httpx"))


@app.function(timeout=1800, cpu=4, memory=4096)
def load(n: int = 30, url: str = URL, train_together: bool = True) -> dict:
    import httpx

    res = [None] * n
    barrier = threading.Barrier(n)

    def student(i):
        r = {"i": i, "errors": []}
        c = httpx.Client(base_url=url, timeout=300)
        try:
            t = time.time()
            j = c.post("/api/join", json={"name": f"Load Student {i:02d}"}).json()
            h = {"X-Player": j["pid"]}
            r["join"] = round(time.time() - t, 2)
            t = time.time()
            b = c.post("/api/before", headers=h)
            r["before"] = round(time.time() - t, 2)
            r["before_status"] = b.status_code
            t = time.time()
            c.post("/api/facts", headers=h, json={"facts": j["facts"]}).raise_for_status()
            a = c.post("/api/context", headers=h)
            r["context"] = round(time.time() - t, 2)
            r["context_status"] = a.status_code
            if a.status_code == 200:
                r["context_right"] = sum(x["verdict"] == "right" for x in a.json()["answers"] if x["role"] == "taught")
            if train_together:
                barrier.wait(timeout=600)  # everyone presses Train at the same moment
            t = time.time()
            v = c.post("/api/train", headers=h).json()
            r["first_position"] = v.get("position")
            positions = []
            while True:
                v = c.get("/api/train/status", headers=h).json()
                if v.get("position"):
                    positions.append(v["position"])
                if v["state"] in ("finished", "failed", "none"):
                    break
                time.sleep(1.5)
            r["train_total"] = round(time.time() - t, 1)
            r["state"] = v["state"]
            r["waited"] = v.get("waited")
            r["running_for"] = v.get("running_for")
            r["positions"] = positions[:1] + positions[-1:]
            tr = (v.get("trained") or {})
            ans = tr.get("answers") or []
            r["trained_right"] = sum(x["verdict"] == "right" for x in ans if x["role"] == "taught")
            r["trained_of"] = sum(1 for x in ans if x["role"] == "taught")
            r["para_right"] = sum(x["verdict"] == "right" for x in ans if x["role"] == "paraphrase")
            r["para_of"] = sum(1 for x in ans if x["role"] == "paraphrase")
            r["steps"] = (tr.get("info") or {}).get("steps")
            r["train_seconds"] = (tr.get("info") or {}).get("seconds")
        except Exception as e:  # noqa: BLE001
            r["errors"].append(f"{type(e).__name__}: {e}"[:300])
        res[i] = r

    T0 = time.time()
    th = [threading.Thread(target=student, args=(i,)) for i in range(n)]
    for t in th:
        t.start()
        time.sleep(0.05)
    for t in th:
        t.join()

    def stat(k):
        xs = [r[k] for r in res if r and isinstance(r.get(k), (int, float))]
        return {"min": min(xs), "median": round(statistics.median(xs), 1), "p90": round(sorted(xs)[int(0.9 * (len(xs) - 1))], 1),
                "max": max(xs), "n": len(xs)} if xs else None

    out = {"n": n, "url": url, "wall_seconds": round(time.time() - T0, 1),
           "finished": sum(1 for r in res if r and r.get("state") == "finished"),
           "errors": [e for r in res if r for e in r["errors"]],
           "before_s": stat("before"), "context_s": stat("context"), "queue_wait_s": stat("waited"),
           "job_s": stat("running_for"), "train_click_to_answers_s": stat("train_total"), "gpu_train_s": stat("train_seconds"),
           "max_first_position": max((r.get("first_position") or 0) for r in res if r),
           "taught_right": [sum(r.get("trained_right", 0) for r in res if r), sum(r.get("trained_of", 0) for r in res if r)],
           "paraphrase_right": [sum(r.get("para_right", 0) for r in res if r), sum(r.get("para_of", 0) for r in res if r)],
           "context_taught_right": sum(r.get("context_right", 0) for r in res if r),
           "students": res}
    print(json.dumps({k: v for k, v in out.items() if k != "students"}, indent=1))
    return out


@app.local_entrypoint()
def main(n: int = 30, url: str = URL):
    r = load.remote(n, url)
    d = HERE.parent / "qa"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"load_{n}.json").write_text(json.dumps(r, indent=1))
    print("wrote", d / f"load_{n}.json")
