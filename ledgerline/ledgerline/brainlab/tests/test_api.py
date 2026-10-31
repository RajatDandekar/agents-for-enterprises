"""In-process test of the Brain Lab API (FastAPI TestClient, no network to the web app).

    BRAINLAB_LIVE=1  the GPU calls go to the DEPLOYED Brain / Trainer classes on Modal (real model, real training)
    otherwise        a fake GPU (instant, deterministic) checks the app logic only

Run on Modal:  /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::test
"""
import os
import pathlib
import re
import sys
import threading
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
os.environ.setdefault("BRAINLAB_NO_APP", "1")
os.environ.setdefault("BRAINLAB_ADMIN_TOKEN", "test-token")

from fastapi.testclient import TestClient  # noqa: E402

from ledgerline.brainlab import app as A  # noqa: E402
from ledgerline.brainlab import brain as BR  # noqa: E402
from ledgerline.brainlab import lab as L  # noqa: E402

LIVE = os.environ.get("BRAINLAB_LIVE") == "1"
OK, FAIL = [], []


def check(name, cond, info=""):
    (OK if cond else FAIL).append(name)
    print(("OK   " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)


class FakeGPU:
    """Says 100 with no facts, quotes the fact with facts, and the trained answer is the taught fact."""

    def __init__(self, delay=0.0):
        self.delay, self.trained = delay, {}

    def _one(self, q, facts=None, aid=None):
        src = facts or (self.trained.get(aid) if aid else None)
        if src:
            words = set(re.findall(r"[a-z]{4,}", q.lower()))
            best = max(src, key=lambda f: len(words & set(re.findall(r"[a-z]{4,}", (f if isinstance(f, str) else f["fact"]).lower()))))
            return best if isinstance(best, str) else best["fact"]
        return "We currently have 100 of those."

    def answer(self, questions, facts=None, adapter_id=None, temperature=0.0):
        return {"answers": [{"q": q, "text": self._one(q, facts, adapter_id), "prompt_tokens": 100,
                             "moment": None} for q in questions], "gpu_seconds": 0.1}

    def train(self, job_id, facts, tests, settings=None, context_facts=None, temperature=0.0):
        st = settings or {}
        n = int(st.get("steps", 30))
        yield {"phase": "start", "examples": 4 * len(facts), "answer_tokens": 80, "tokens": 900, "trainable": 549888 * st.get("rank", 16),
               "frozen": 494032768, "lr": st.get("lr", 1e-3), "rank": st.get("rank", 16), "steps_planned": n}
        yield {"phase": "probe", "at": 0}
        for s in range(1, n + 1):
            if self.delay:
                time.sleep(self.delay / 5)
            yield {"step": s, "loss": round(2.0 / s, 3), "t": s * 0.1}
        probes = {"facts": [{"fact": 0, "pieces": ["Man", "chester", " 5", ","], "key_tok": 2}], "at": [0, n // 3, n],
                  "p": [[[0.1, 0.2, 0.03, 0.5]], [[0.5, 0.6, 0.4, 0.7]], [[0.99, 0.99, 0.98, 0.99]]]}
        yield {"done": True, "steps": n, "loss": 0.01, "seconds": 0.5, "stopped": "steps", "probes": probes}
        yield {"phase": "asking"}
        self.trained[job_id] = facts
        ans = self.answer([t["q"] for t in tests], None, job_id)["answers"]
        both = self.answer([t["q"] for t in tests], context_facts, job_id)["answers"] if context_facts else None
        yield {"phase": "finished", "answers": ans, "both": both, "adapter_id": job_id, "gpu_seconds": 0.6}
        yield {"phase": "saved", "adapter_mb": 17.6}

    def autoscale(self, **kw):
        self.scaled = kw


def wait_trained(c, h, limit=240):
    t0, seen = time.time(), set()
    while time.time() - t0 < limit:
        v = c.get("/api/train/status", headers=h).json()
        seen.add(v["state"])
        if v["state"] in ("finished", "failed"):
            return v, seen, time.time() - t0
        time.sleep(0.5)
    return v, seen, time.time() - t0


def main():
    gpu = A.modal_gpu() if LIVE else FakeGPU()
    app = A.create_app(gpu=gpu, store=A.Store(None))
    c = TestClient(app)
    adm = {"X-Admin-Token": os.environ["BRAINLAB_ADMIN_TOKEN"]}

    # the system prompt is the live app's brain-stage prompt, character for character
    hp = pathlib.Path(__file__).resolve().parents[2] / "experience" / "harness.py"
    if hp.exists():
        m = re.search(r'BRAIN = """(.*?)"""', hp.read_text(), re.S)
        want = m.group(1).format(name="Emma Clarke", role="purchase executive", user="ECLARKE", first="Emma")
        check("system prompt = harness BRAIN for Emma", want == BR.SYSTEM)

    check("home page", c.get("/").status_code == 200 and "Brain Lab" in c.get("/").text)
    check("sky.css shared from the Experience", c.get("/sky/sky.css").status_code == 200)
    check("wall + admin pages", c.get("/wall").status_code == 200 and c.get("/admin").status_code == 200)
    check("tinygpt.json", c.get("/static/tinygpt.json").json()["stock_figures"][0] == 2400)
    check("no player -> 401", c.get("/api/me").status_code == 401)
    check("short name -> 400", c.post("/api/join", json={"name": "a"}).status_code == 400)

    r = c.post("/api/join", json={"name": "Priya Shah"}).json()
    h = {"X-Player": r["pid"]}
    b = r["badge"]
    check("joined with a badge", r["name"] == "Priya Shah" and b["first"] == "Priya" and b["packs"] not in (5400, 1200),
          str(b))
    check("5 pre-filled facts, lecture first, with my team", len(r["facts"]) == 5 and r["facts"][0]["a"] == "5,400"
          and r["facts"][3]["a"] == b["team"])
    r2 = c.post("/api/badge/reroll", headers=h).json()
    check("reroll gives a new badge", r2["badge"]["reroll"] == 1 and r2["facts"][1]["a"] == f"{r2['badge']['packs']:,}")

    t0 = time.time()
    bf = c.post("/api/before", headers=h)
    check("before answers", bf.status_code == 200 and len(bf.json()["answers"]) == 5, f"{time.time() - t0:.1f}s")
    for a in bf.json()["answers"]:
        print("     BEFORE", a["verdict"], "|", a["q"], "|", a["text"][:100])
    check("before: nothing right (it cannot know)", not any(a["verdict"] == "right" for a in bf.json()["answers"]))

    bad = c.post("/api/facts", headers=h, json={"facts": [{"fact": "Bob has a dog.", "q": "What pet?", "a": "cat"}]})
    check("fact validation: answer must be in the fact, 2+ facts", bad.status_code == 400, bad.json().get("detail"))
    facts = c.get("/api/me", headers=h).json()["facts"][:3] + [
        {"fact": "The Leeds unit's forklift is called Big Bertha.", "q": "What is the Leeds forklift called?",
         "a": "Big Bertha", "para": "What name does the forklift in Leeds have?"}]
    sv = c.post("/api/facts", headers=h, json={"facts": facts})
    check("facts saved", sv.status_code == 200 and len(sv.json()["facts"]) == 4)
    tests = sv.json()["tests"]
    check("test set: taught + paraphrase + neighbour + general",
          {t["role"] for t in tests} == {"taught", "paraphrase", "neighbour", "general"}, str(len(tests)))

    t0 = time.time()
    cx = c.post("/api/context", headers=h).json()
    taught = [a for a in cx["answers"] if a["role"] == "taught"]
    check("context: taught questions right", sum(a["verdict"] == "right" for a in taught) >= len(taught) - (1 if LIVE else 0),
          f"{sum(a['verdict'] == 'right' for a in taught)}/{len(taught)} in {time.time() - t0:.1f}s")
    for a in cx["answers"]:
        print("     CONTEXT", a["verdict"], "|", a["role"], "|", a["q"], "|", a["text"][:100])

    tr = c.post("/api/train", headers=h)
    check("train queued", tr.status_code == 200 and tr.json()["state"] in ("queued", "starting", "training"))
    again = c.post("/api/train", headers=h).json()
    check("a second click returns the same job (unless already done)",
          again["id"] == tr.json()["id"] or not LIVE)
    v, seen, secs = wait_trained(c, h)
    check("training finished", v["state"] == "finished", f"{secs:.1f}s, states {sorted(seen)}")
    check("loss curve falls", len(v["curve"]) >= 3 and v["curve"][-1][1] < v["curve"][0][1] / 4,
          f"{v['curve'][0][1]} -> {v['curve'][-1][1]} in {len(v['curve'])} steps")
    ta = v["trained"]["answers"]
    for a in ta:
        print("     TRAINED", a["verdict"], "|", a["role"], "|", a["q"], "|", a["text"][:100])
    taught = [a for a in ta if a["role"] == "taught"]
    check("trained: taught questions right with NO facts in the prompt",
          sum(a["verdict"] == "right" for a in taught) >= len(taught) - 1,
          f"{sum(a['verdict'] == 'right' for a in taught)}/{len(taught)}")
    check("trained adapter kept", bool(v["trained"]["adapter_id"]))
    run1 = v["trained"]
    check("run recorded with settings, cost, probes", run1["n"] >= 1 and run1["settings"]["steps"] == 30
          and run1["cost_usd"] > 0 and run1["probes"] and len(run1["probes"]["at"]) == 3,
          f"settings {run1['settings']} cost ${run1['cost_usd']} probe at {run1['probes']['at'] if run1['probes'] else None}")
    if run1["probes"]:
        pr = run1["probes"]
        for k, f in enumerate(pr["facts"]):
            kt = f["key_tok"]
            if kt is not None:
                print(f"     PROBE fact {f['fact'] + 1}: key token {f['pieces'][kt]!r}: "
                      + " -> ".join(f"step {a}: {pr['p'][j][k][kt]:.3f}" for j, a in enumerate(pr["at"])))
    check("trained + facts in the prompt answers", run1["both"] and len(run1["both"]) == len(run1["answers"]))
    td = c.get("/api/training_data", headers=h).json()
    check("training data preview: 4 facts x 4 ways", td["n_examples"] == 16 and td["scored_tokens"] > 50,
          f"{td['n_examples']} examples, {td['tokens']} tokens, {td['scored_tokens']} scored")
    td2 = c.get("/api/training_data?distractors=1", headers=h).json()
    check("training data with distractors", td2["n_examples"] == 32 and any(e["distractor"] for e in td2["examples"]))
    # a second run with other settings: few steps, low learning rate, small adapter, distractors, temperature
    tr2 = c.post("/api/train", headers=h, json={"steps": 10, "lr": "low", "rank": "small", "distractors": True,
                                               "temperature": 0.7})
    check("second run queued with settings", tr2.status_code == 200)
    v2, seen2, secs2 = wait_trained(c, h)
    r2 = v2["trained"]
    check("second run finished, 2 runs kept", v2["state"] == "finished" and len(v2["runs"]) >= 2
          and r2["settings"] == {"steps": 10, "lr": "low", "rank": "small", "distractors": True, "facts": 4, "temperature": 0.7}
          and r2["info"]["rank"] == 4 and r2["distractors"] == 4, f"{secs2:.1f}s loss {r2['info']['loss']}")
    for a in r2["answers"]:
        print("     RUN2 (10 steps, low lr, rank 4, distractors, T=0.7)", a["verdict"], "|", a["role"], "|", a["text"][:90])

    ask = c.post("/api/ask", headers=h, json={"q": "What is the Leeds forklift called?"})
    print("     ask status", ask.status_code)
    ask = ask.json()
    check("ask all four ways", set(ask["answers"]) == {"bare", "context", "trained", "both"},
          " | ".join(f"{k}: {x['text'][:60]}" for k, x in ask["answers"].items()))
    check("ask uses the latest run's adapter (from the Volume)", bool(ask["answers"]["trained"]["text"]),
          ask["answers"]["trained"]["text"][:80])
    hot = c.post("/api/before", headers=h, json={"temperature": 1.2}).json()
    check("temperature 1.2 accepted on before", hot["temperature"] == 1.2, hot["answers"][0]["text"][:80])

    w = c.get("/api/wall").json()
    check("wall has the player", w["count"] >= 1 and w["rows"][0]["name"] == "Priya Shah", str(w["agg"]))

    # admin
    check("admin without token -> 403", c.get("/api/admin/status").status_code == 403)
    st = c.get("/api/admin/status", headers=adm).json()
    check("admin status", st["players"] == 1 and st["trained"] == 1, f"usd {st['usd_today']}")
    c.post("/api/admin/flags", headers=adm, json={"enabled": False, "reason": "back in 5"})
    p = c.post("/api/before", headers=h)
    check("pause refuses with the reason", p.status_code == 503 and "back in 5" in p.json()["detail"])
    c.post("/api/admin/flags", headers=adm, json={"enabled": True, "training": False})
    check("training-only pause", c.post("/api/train", headers=h).status_code == 503)
    c.post("/api/admin/flags", headers=adm, json={"training": True, "cap_usd": 0})
    check("cap reached refuses", c.post("/api/context", headers=h).status_code == 429)
    c.post("/api/admin/flags", headers=adm, json={"cap_usd": 30})

    if not LIVE:  # queue positions with a slow fake GPU and 2 slots
        gpu.delay = 0.2
        c.post("/api/admin/flags", headers=adm, json={"train_slots": 2})
        hs = []
        for i in range(6):
            pid = c.post("/api/join", json={"name": f"Student {i}"}).json()["pid"]
            hs.append({"X-Player": pid})
        views = [c.post("/api/train", headers=x).json() for x in hs]
        time.sleep(0.3)
        pos = [c.get("/api/train/status", headers=x).json() for x in hs]
        queued = [x.get("position") for x in pos if x["state"] == "queued"]
        check("queue: 2 run, the rest wait with positions 1..n", queued == list(range(1, len(queued) + 1)) and len(queued) >= 3,
              str([x["state"] for x in pos]) + str(queued))
        res = [wait_trained(c, x)[0]["state"] for x in hs]
        check("queue: all finish", res == ["finished"] * 6)
        r = c.post("/api/admin/warm", headers=adm, json={"n": 2}).json()
        check("warm sets min_containers", gpu.scaled == {"min_containers": 2} and r["warm"] == 2)
    print(f"\n{len(OK)} passed, {len(FAIL)} failed" + (f": {FAIL}" if FAIL else ""))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
