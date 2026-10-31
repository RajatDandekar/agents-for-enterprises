"""The Brain Lab on Modal (Lecture 2): app `northbridge-brainlab`, workspace rajatworkspace.

    /Users/raj/.venv/bin/modal deploy deploy/brainlab_modal.py                    # deploy (or update) the live app
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::bench                # the recipe check: 3 fact sets, real GPU
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::test                 # the in-process API test
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd status   # spend, queue, players, flags
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd warm --n 3   # keep 3 trainer + 2 answer GPUs warm (class)
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd cool         # let the GPUs sleep (after class)
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd cap --cap 40
    /Users/raj/.venv/bin/modal run deploy/brainlab_modal.py::admin --cmd purge-all     # empty the wall before class

Two parts:
  web    FastAPI + static pages, ONE CPU container (players, the training queue and the class wall live in its memory;
         names, badges, facts and results are also in the modal.Dict `northbridge-brainlab-state`).
  Brain  the GPU class (L4): Qwen2.5-0.5B-Instruct baked into the image. Answers questions (bare, facts in the prompt,
         or with a student's adapter) and runs the LoRA fine-tunes. Several inputs share one GPU (@modal.concurrent);
         the web app's queue decides how many trainings run at once, Modal autoscales up to MAX_GPUS containers.
         Adapters are saved to the Volume `northbridge-brainlab-adapters`, so any container can answer with them.

Warm GPUs: min_containers is 0 in this file, so a deploy never leaves a GPU running. A cron sets 3 warm trainer GPUs (and 2 answer GPUs) at
00:30 UTC on Sun 1 Nov (an hour before class, so there is time to find GPUs) and lets them sleep every day at 04:00 UTC; `admin --cmd warm/cool`
and the admin page do the same by hand. A redeploy resets min_containers to 0.
The admin token is the Modal secret `northbridge-brainlab` (BRAINLAB_ADMIN_TOKEN); never in the image or the repo.
"""
import json
import os
import pathlib
import sys
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = "https://rajatworkspace--northbridge-brainlab.us-east.modal.run"
APP = "northbridge-brainlab"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules", "cassettes", "legacy_ui"}
GPU = os.environ.get("BRAINLAB_GPU", "L4")
# L4 first; when Modal has no L4 free (it happened on Sat 31 Oct: "waiting to be scheduled on a GPU_L4 worker" for
# ~4 minutes), it falls back to an A10G, then an L40S. The model is small, so any of them is fast.
GPUS = [GPU, "A10G", "L40S"]
MAX_GPUS = int(os.environ.get("BRAINLAB_MAX_GPUS", "8"))
MAX_ANSWER_GPUS = int(os.environ.get("BRAINLAB_MAX_ANSWER_GPUS", "6"))


def _code(img):
    return img.add_local_dir(ROOT / "ledgerline", "/app/ledgerline",
                             ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                             or str(p).endswith((".env", ".png", ".mp4", ".ipynb", ".jsonl", ".webm")))


gpu_image = _code(
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.4.1", "transformers==4.46.3", "accelerate==1.1.1", "numpy<2.1", "fastapi")
    .env({"HF_HOME": "/models/hf", "PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1",
          "TOKENIZERS_PARALLELISM": "false", "HF_HUB_OFFLINE": "0"})
    .run_commands("python -c \"from huggingface_hub import snapshot_download as s; "
                  "s('Qwen/Qwen2.5-0.5B-Instruct', allow_patterns=['*.json','*.safetensors','*.txt','merges.txt','vocab.json'])\"")
    .env({"HF_HUB_OFFLINE": "1"})
)
web_image = _code(
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi==0.115.6", "uvicorn", "httpx", "pydantic>=2", "transformers==4.46.3", "jinja2")
    .env({"HF_HOME": "/models/hf"})
    .run_commands("python -c \"from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct')\"")
    .env({"HF_HUB_OFFLINE": "1"})
    .env({"PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1", "BRAINLAB_DICT": "northbridge-brainlab-state",
          "BRAINLAB_APP": APP, "BRAINLAB_GPU": GPU, "BRAINLAB_MAX_GPUS": str(MAX_GPUS)})
)
app = modal.App(APP)
adapters = modal.Volume.from_name("northbridge-brainlab-adapters", create_if_missing=True)
secret = modal.Secret.from_name("northbridge-brainlab")


def _load(self):
    import threading

    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.brainlab.brain import Brain as B

    self.b = B()
    self.cache = {}
    self.vlock = threading.Lock()
    self.b.answer(["Warm up?"], max_new_tokens=4)  # first CUDA kernels compiled here, not in a student's request
    print(f"brain loaded in {self.b.load_seconds}s on {self.b.device} ({self.b.dtype})")


@app.cls(image=gpu_image, gpu=GPUS, max_containers=MAX_ANSWER_GPUS, min_containers=0, scaledown_window=300,
         timeout=300, volumes={"/adapters": adapters}, cpu=4, memory=16384)
@modal.concurrent(max_inputs=4, target_inputs=2)
class Brain:
    """Answers: a batch of questions, bare, with facts in the prompt, or with a student's trained adapter."""

    @modal.enter()
    def load(self):
        _load(self)

    def _adapter(self, aid: str):
        from ledgerline.brainlab.brain import Adapter

        if aid in self.cache:
            return self.cache[aid]
        p = pathlib.Path(f"/adapters/{aid}.pt")
        with self.vlock:
            for _ in range(20):  # the trainer saves the adapter just after it sends its answers: wait for it
                if p.exists():
                    break
                adapters.reload()
                if p.exists():
                    break
                time.sleep(1.0)
            data = p.read_bytes()
        ad = Adapter.from_bytes(data, device=self.b.device)
        if len(self.cache) > 64:
            self.cache.pop(next(iter(self.cache)))
        self.cache[aid] = ad
        return ad

    @modal.method()
    def answer(self, questions: list, facts: list | None = None, adapter_id: str | None = None,
               max_new_tokens: int = 60, temperature: float = 0.0) -> dict:
        t0 = time.time()
        ad = self._adapter(adapter_id) if adapter_id else None
        res = self.b.answer(questions, facts=facts, adapter=ad, max_new_tokens=max_new_tokens,
                            temperature=temperature)
        return {"answers": res, "gpu_seconds": round(time.time() - t0, 2)}


@app.cls(image=gpu_image, gpu=GPUS, max_containers=MAX_GPUS, min_containers=0, scaledown_window=300, timeout=300,
         volumes={"/adapters": adapters}, cpu=4, memory=16384)
class Trainer:
    """One training at a time per GPU: measured on an L4, one LoRA run takes ~6 s alone but 4 at once in one
    process take 32 s each, so sharing a GPU between trainings only slows everyone down."""

    @modal.enter()
    def load(self):
        _load(self)

    @modal.method()
    def train(self, job_id: str, facts: list, tests: list, settings: dict | None = None,
              context_facts: list | None = None, temperature: float = 0.0):
        """A generator: the loss at every step and three probes of the answer tokens, then the trained brain's
        answers to the test questions with NO facts in the prompt (and, for comparison, trained + facts in the
        prompt). The adapter is saved to the Volume after the answers are sent, so later questions can use it."""
        t0 = time.time()
        ad = None
        st = settings or {}
        for ev in self.b.train(facts, steps=int(st.get("steps", 30)), lr=float(st.get("lr", 1e-3)),
                               rank=int(st.get("rank", 16))):
            if ev.get("done"):
                ad = ev.pop("adapter")
            yield ev
        yield {"phase": "asking"}
        qs = [t["q"] for t in tests]
        res = self.b.answer(qs, adapter=ad, temperature=temperature)
        both = self.b.answer(qs, facts=context_facts, adapter=ad, temperature=temperature) if context_facts else None
        yield {"phase": "finished", "answers": res, "both": both, "adapter_id": job_id,
               "gpu_seconds": round(time.time() - t0, 2)}
        data = ad.to_bytes()
        pathlib.Path(f"/adapters/{job_id}.pt").write_bytes(data)
        adapters.commit()
        yield {"phase": "saved", "adapter_mb": round(len(data) / 1e6, 1)}


@app.function(image=gpu_image, gpu=GPU, timeout=1800, cpu=4, memory=16384)
def bench_run(settings: dict | None = None, concurrent: int = 3) -> dict:
    """Recipe check on a real GPU: three students' fact sets, before / context / trained, then `concurrent`
    trainings at once in one process (how the live class shares a GPU)."""
    import threading

    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.brainlab import lab
    from ledgerline.brainlab.brain import Brain as B, says

    b = B()
    b.answer(["Warm up?"], max_new_tokens=4)
    out = {"load_seconds": b.load_seconds, "dtype": b.dtype, "sets": []}
    names = [("Priya Shah", "a1"), ("Tom Becker", "b2"), ("Lena Novak", "c3")]
    custom = [{"fact": "The Leeds unit's forklift is called Big Bertha.", "q": "What is the Leeds forklift called?",
               "a": "Big Bertha", "para": "What name does the forklift in Leeds have?", "kind": "name"},
              {"fact": "Voltway Cells' account manager for Northbridge is Ruth Ellison.",
               "q": "Who is our account manager at Voltway Cells?", "a": "Ruth Ellison",
               "para": "Who looks after Northbridge at Voltway?", "kind": "name"},
              {"fact": "The spring launch run starts on 9 March 2027.", "q": "When does the spring launch run start?",
               "a": "9 March 2027", "para": "What is the start date of the spring launch run?", "kind": "code"}]
    for k, (name, pid) in enumerate(names):
        bd = lab.badge(pid, name)
        facts = lab.default_facts(bd)
        if k == 2:  # the third student writes their own facts instead
            facts = [facts[0]] + custom
        tests = lab.test_set(facts)
        qs = [t["q"] for t in tests]
        before = b.answer(qs)
        ctx = b.answer(qs, facts=[f["fact"] for f in facts])
        curve, fin = [], None
        for ev in b.train(facts, **(settings or {})):
            if "loss" in ev and "step" in ev:
                curve.append((ev["step"], ev["loss"], ev["t"]))
            if ev.get("done"):
                fin = ev
        ad = fin.pop("adapter")
        tr = b.answer(qs, adapter=ad)
        rows = []
        for t, x, y, z in zip(tests, before, ctx, tr):
            rows.append({"role": t["role"], "q": t["q"], "a": t.get("a"), "before": x["text"], "context": y["text"],
                         "trained": z["text"],
                         "ok": [says(x["text"], t["a"]) if t.get("a") else None,
                                says(y["text"], t["a"]) if t.get("a") else None,
                                says(z["text"], t["a"]) if t.get("a") else None],
                         "moment_before": x["moment"], "moment_trained": z["moment"]})
        out["sets"].append({"name": name, "badge": bd, "facts": facts, "train": fin, "curve": curve[::5] + curve[-1:],
                            "rows": rows})
        print(name, fin)
        for r in rows:
            print(" ", r["role"], r["ok"], "|", r["q"], "|", r["before"][:70], "|", r["context"][:70], "|", r["trained"][:70])
    # concurrent trainings in threads on one GPU
    times = {}

    def one(i):
        bd = lab.badge(f"cc{i}", f"Student {i}")
        t0 = time.time()
        fin = None
        for ev in b.train(lab.default_facts(bd), **(settings or {})):
            if ev.get("done"):
                fin = ev
        ad = fin.pop("adapter")
        tr = b.answer([f["q"] for f in lab.default_facts(bd)], adapter=ad)
        times[i] = {"seconds": round(time.time() - t0, 1), "steps": fin["steps"],
                    "recall": sum(says(r["text"], f["a"]) for r, f in zip(tr, lab.default_facts(bd)))}

    t0 = time.time()
    th = [threading.Thread(target=one, args=(i,)) for i in range(concurrent)]
    [t.start() for t in th]
    [t.join() for t in th]
    out["concurrent"] = {"n": concurrent, "wall": round(time.time() - t0, 1), "each": times}
    print("concurrent", out["concurrent"])
    return out


@app.local_entrypoint()
def bench(settings: str = "", concurrent: int = 3, tag: str = "bench"):
    r = bench_run.remote(json.loads(settings) if settings else None, concurrent)
    d = ROOT / "ledgerline" / "ledgerline" / "brainlab" / "qa"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{tag}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print("wrote", d / f"{tag}.json")


# ---------------------------------------------------------------------------------------------------- the web app
@app.function(image=web_image, secrets=[secret], max_containers=1, min_containers=0, scaledown_window=1800, cpu=2,
              memory=4096, timeout=900)
@modal.concurrent(max_inputs=500)
@modal.asgi_app(label="northbridge-brainlab")
def web():
    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.brainlab.app import create_app

    return create_app()


def _autoscale(n: int):
    trainer = modal.Cls.from_name(APP, "Trainer")()
    brain = modal.Cls.from_name(APP, "Brain")()
    trainer.update_autoscaler(min_containers=n)
    brain.update_autoscaler(min_containers=max(1, (n + 1) // 2) if n else 0)


@app.function(image=web_image, schedule=modal.Cron("30 0 1 11 *"), timeout=300)  # Sun 1 Nov, 00:30 UTC
def class_warm():
    import urllib.request

    _autoscale(3)
    for _ in range(5):
        try:
            print(urllib.request.urlopen(URL + "/healthz", timeout=60).read()[:200])
            break
        except Exception as e:  # noqa: BLE001
            print("warm web failed:", e)
            time.sleep(10)


@app.function(image=web_image, schedule=modal.Cron("0 4 * * *"), timeout=120)  # every day 04:00 UTC: GPUs sleep
def class_cool():
    _autoscale(0)
    print("min_containers -> 0 for Trainer and Brain")


# ---------------------------------------------------------------------------------------------------- tests, admin
@app.function(image=web_image, secrets=[secret], timeout=1200, cpu=2, memory=4096)
def run_test(live: bool = True) -> dict:
    import subprocess

    env = {**os.environ, "BRAINLAB_DICT": "", "BRAINLAB_NO_APP": "1", "BRAINLAB_LIVE": "1" if live else "0"}
    p = subprocess.run([sys.executable, "/app/ledgerline/ledgerline/brainlab/tests/test_api.py"], capture_output=True,
                       text=True, env=env, timeout=1100)
    return {"code": p.returncode, "out": p.stdout[-40000:], "err": p.stderr[-8000:]}


@app.local_entrypoint()
def test(live: bool = True):
    r = run_test.remote(live)
    print(r["out"])
    if r["code"]:
        print("--- stderr ---\n" + r["err"])
    d = ROOT / "ledgerline" / "ledgerline" / "brainlab" / "qa"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"test_api_{'live' if live else 'fake'}.txt").write_text(r["out"] + "\n" + r["err"])


@app.function(image=web_image, secrets=[secret], timeout=300)
def op(cmd: str, reason: str = "", cap: float = 0, n: int = 2, slots: int = 0) -> dict:
    """Operator commands, run inside Modal so the admin token never leaves the secret store."""
    import httpx

    h = {"X-Admin-Token": os.environ["BRAINLAB_ADMIN_TOKEN"]}
    c = httpx.Client(base_url=URL, timeout=120)
    if cmd == "pause":
        c.post("/api/admin/flags", json={"enabled": False, "reason": reason}, headers=h).raise_for_status()
    elif cmd == "resume":
        c.post("/api/admin/flags", json={"enabled": True, "training": True, "reason": ""}, headers=h).raise_for_status()
    elif cmd == "cap":
        c.post("/api/admin/flags", json={"cap_usd": cap}, headers=h).raise_for_status()
    elif cmd == "slots":
        c.post("/api/admin/flags", json={"train_slots": slots}, headers=h).raise_for_status()
    elif cmd == "warm":
        c.post("/api/admin/warm", json={"n": n}, headers=h).raise_for_status()
    elif cmd == "cool":
        c.post("/api/admin/warm", json={"n": 0}, headers=h).raise_for_status()
    elif cmd == "purge-tests":
        print(c.post("/api/admin/purge", json={"prefixes": ["Load ", "Sam Taylor", "Aisha Grant"]}, headers=h).json())
    elif cmd == "purge-all":
        print(c.post("/api/admin/purge", json={"all": True}, headers=h).json())
    s = c.get("/api/admin/status", headers=h)
    s.raise_for_status()
    out = s.json()
    out.pop("recent", None)
    out["queue"].pop("waits", None)
    out["no_token_status"] = c.get("/api/admin/status").status_code
    return out


@app.local_entrypoint()
def admin(cmd: str = "status", reason: str = "", cap: float = 0, n: int = 2, slots: int = 0):
    print(json.dumps(op.remote(cmd, reason, cap, n, slots), indent=1, ensure_ascii=False))
