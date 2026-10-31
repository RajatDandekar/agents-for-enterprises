"""The Brain Lab: Lecture 2's live, personal web app (FastAPI). Deployed by deploy/brainlab_modal.py.

    /            the lab: your name, your Northbridge badge, Before, Teach it, the two ways (context | training), After
    /wall        the class wall for the projector (also at the bottom of the lab)
    /admin       the operator's page: pause, the $ cap, warm or cool the GPUs, the queue, players (admin token)

The model never runs here. Every answer and every training run is a call to the GPU class `Brain` (brain.py on an
L4), through a `gpu` object with two methods (the in-process test passes a local one):
    gpu.answer(questions, facts=None, adapter_id=None, temperature=0) -> {"answers": [...], "gpu_seconds": s}
    gpu.train(job_id, facts, tests, settings, context_facts, temperature)
        -> an iterator of events (start, probes, the loss per step, done, asking, finished with the answers, saved)

Training is queued here: at most `train_slots` run at once (the admin page can change it); everyone else sees
"your training starts in N".
"""
from __future__ import annotations

import asyncio
import os
import pathlib
import re
import threading
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import brain as BR
from . import lab as L
from .brain import says

HERE = pathlib.Path(__file__).parent
STATIC = HERE / "static"
EXP_STATIC = HERE.parent / "experience" / "static"   # the Sky look and helpers are shared with L1's Experience

# Modal's list price for one L4 container (GPU + 4 CPU + 16 GiB), US dollars a second; an estimate for the cap.
RATE = {"L4": 0.000222 + 4 * 0.0000131 + 16 * 0.00000222, "A10G": 0.000306 + 4 * 0.0000131 + 16 * 0.00000222}
TEMPS = (0.0, 0.7, 1.2)
DECLINE = re.compile(r"(don't|do not|cannot|can't|unable|not able|no access|not have access|no information|"
                     r"i'm sorry|i am sorry|not sure|don't know|do not know|not available to me|not provided)", re.I)


def verdict(text: str, key: str | None) -> str:
    if key and says(text, key):
        return "right"
    if DECLINE.search(text or ""):
        return "declined"
    return "invented" if key else "answered"


class Refused(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status, self.msg = status, msg


class Store:
    """Names, badges, facts and results survive a restart in a modal.Dict; reads come from memory."""

    def __init__(self, name: str | None):
        self.mem, self.d, self._dirty, self._lock = {}, None, set(), threading.Lock()
        if name:
            try:
                import modal

                self.d = modal.Dict.from_name(name, create_if_missing=True)
                for k, v in self.d.items():
                    self.mem[k] = v
                threading.Thread(target=self._writer, daemon=True).start()
            except Exception as e:  # noqa: BLE001
                print("store: modal.Dict unavailable:", type(e).__name__, str(e)[:200])
                self.d = None

    def get(self, k, default=None):
        return self.mem.get(k, default)

    def put(self, k, v):
        with self._lock:
            self.mem[k] = v
            self._dirty.add(k)

    def delete(self, k):
        with self._lock:
            self.mem.pop(k, None)
            self._dirty.discard(k)
        if self.d is not None:
            try:
                self.d.pop(k, None)
            except Exception as e:  # noqa: BLE001
                print("store: delete failed:", type(e).__name__)

    def keys(self, prefix=""):
        return [k for k in list(self.mem) if k.startswith(prefix)]

    def flush(self):
        if self.d is None:
            return
        with self._lock:
            todo = {k: self.mem[k] for k in self._dirty if k in self.mem}
            self._dirty.clear()
        if todo:
            try:
                self.d.update(todo)
            except Exception as e:  # noqa: BLE001
                print("store: flush failed, will retry:", type(e).__name__)
                with self._lock:
                    self._dirty |= set(todo)

    def _writer(self):
        while True:
            time.sleep(1.0)
            self.flush()


class Guard:
    """The instructor's switches and the day's GPU spend (an estimate from the seconds each GPU call reports)."""

    def __init__(self, store: Store, gpu_kind: str):
        self.store, self.rate = store, max(RATE.values())  # the dearer of L4 / A10G: the GPU class may fall back
        self.lock = threading.Lock()
        self.hits: dict[str, deque] = {}
        self.cap_default = float(os.environ.get("BRAINLAB_CAP_USD", "30"))

    @staticmethod
    def today():
        import datetime as dt

        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def flags(self) -> dict:
        f = {"enabled": True, "training": True, "reason": "", "cap_usd": self.cap_default,
             "train_slots": int(os.environ.get("BRAINLAB_MAX_GPUS", "8")), "warm": 0, "warm_since": None}
        f.update(self.store.get("flags", {}) or {})
        return f

    def set_flags(self, **kw):
        with self.lock:
            f = self.flags()
            f.update({k: v for k, v in kw.items() if v is not None})
            self.store.put("flags", f)
            return f

    def spent(self) -> dict:
        return self.store.get(f"spend:{self.today()}") or {"gpu_seconds": 0.0, "answers": 0, "trainings": 0,
                                                             "warm_seconds": 0.0}

    def usd(self, s=None) -> float:
        s = s or self.spent()
        f = self.flags()
        warm = s.get("warm_seconds", 0) + (f["warm"] * (time.time() - f["warm_since"]) if f.get("warm_since") else 0)
        return round((s["gpu_seconds"] + warm) * self.rate, 3)

    def add(self, gpu_seconds: float, kind: str):
        with self.lock:
            s = dict(self.spent())
            s["gpu_seconds"] = round(s["gpu_seconds"] + float(gpu_seconds or 0), 2)
            s[kind] = s.get(kind, 0) + 1
            self.store.put(f"spend:{self.today()}", s)

    def add_warm(self, seconds: float):
        with self.lock:
            s = dict(self.spent())
            s["warm_seconds"] = round(s.get("warm_seconds", 0) + seconds, 1)
            self.store.put(f"spend:{self.today()}", s)

    def check(self, pid: str, what: str = "answer"):
        f = self.flags()
        if not f.get("enabled", True):
            raise Refused(503, "The Brain Lab is paused by the instructor" + (f": {f['reason']}" if f.get("reason") else "."))
        if what == "train" and not f.get("training", True):
            raise Refused(503, "Training is paused by the instructor. Path A (the prompt) still works.")
        cap = f.get("cap_usd")
        if self.usd() >= float(self.cap_default if cap is None else cap):
            raise Refused(429, "Today's GPU budget for the class is used up. The instructor can raise it.")
        lim = {"answer": (20, 60), "train": (4, 600)}[what]
        now = time.monotonic()
        with self.lock:
            q = self.hits.setdefault(f"{pid}/{what}", deque())
            while q and now - q[0] > lim[1]:
                q.popleft()
            if len(q) >= lim[0]:
                raise Refused(429, "Too many requests from you just now. Wait a little and try again.")
            q.append(now)


class Queue:
    """The training queue. Jobs wait here; at most `slots()` run on the GPUs at once."""

    def __init__(self, gpu, guard: Guard, on_done):
        self.gpu, self.guard, self.on_done = gpu, guard, on_done
        self.jobs: dict[str, dict] = {}
        self.waiting: deque = deque()
        self.running: set = set()
        self.cv = threading.Condition()
        self.durations: deque = deque([45.0], maxlen=40)
        threading.Thread(target=self._dispatch, daemon=True).start()

    def slots(self) -> int:
        return max(1, int(self.guard.flags().get("train_slots") or 8))

    def submit(self, pid: str, facts: list, tests: list, extra: dict | None = None) -> dict:
        with self.cv:
            for jid in list(self.waiting) + list(self.running):
                if self.jobs[jid]["pid"] == pid:
                    return self.jobs[jid]
            jid = "j" + uuid.uuid4().hex[:12]
            job = {"id": jid, "pid": pid, "facts": facts, "tests": tests, "state": "queued", "t_submit": time.time(),
                   "curve": [], "info": {}, "answers": None, "both": None, "probes": None, "error": None,
                   **(extra or {})}
            self.jobs[jid] = job
            self.waiting.append(jid)
            self.cv.notify_all()
            return job

    def view(self, jid: str) -> dict | None:
        j = self.jobs.get(jid)
        if not j:
            return None
        out = {k: j[k] for k in ("id", "state", "curve", "info", "error")}
        if j["state"] == "queued":
            with self.cv:
                pos = list(self.waiting).index(jid) + 1 if jid in self.waiting else 1
            avg = sum(self.durations) / len(self.durations)
            out["position"] = pos
            out["eta_seconds"] = round(((pos - 1) // self.slots() + 1) * avg)
        out["waited"] = round((j.get("t_start") or time.time()) - j["t_submit"], 1)
        if j.get("t_start"):
            out["running_for"] = round((j.get("t_end") or time.time()) - j["t_start"], 1)
        return out

    def stats(self) -> dict:
        with self.cv:
            return {"waiting": len(self.waiting), "running": len(self.running), "slots": self.slots(),
                    "avg_seconds": round(sum(self.durations) / len(self.durations), 1),
                    "done": sum(1 for j in self.jobs.values() if j["state"] == "finished"),
                    "failed": sum(1 for j in self.jobs.values() if j["state"] == "failed"),
                    "waits": [round(j["t_start"] - j["t_submit"], 1) for j in self.jobs.values() if j.get("t_start")][-200:]}

    def _dispatch(self):
        while True:
            with self.cv:
                while not self.waiting or len(self.running) >= self.slots():
                    self.cv.wait(timeout=1.0)
                jid = self.waiting.popleft()
                self.running.add(jid)
            threading.Thread(target=self._run, args=(jid,), daemon=True).start()

    def _run(self, jid: str):
        j = self.jobs[jid]
        j["state"], j["t_start"] = "starting", time.time()
        try:
            for ev in self.gpu.train(jid, j["facts"], j["tests"], j.get("settings"), j.get("context_facts"),
                                     j.get("temperature", 0.0)):
                ph = ev.get("phase")
                if ph == "start":
                    j["info"].update({k: ev.get(k) for k in ("examples", "answer_tokens", "tokens", "trainable", "frozen",
                                                             "lr", "rank", "steps_planned")})
                    j["state"] = "training"
                elif ph == "probe":
                    j["state"] = "training"
                elif "step" in ev and "loss" in ev and not ev.get("done"):
                    j["curve"].append([ev["step"], ev["loss"], ev["t"]])
                    j["state"] = "training"
                elif ev.get("done"):
                    j["info"].update({k: ev.get(k) for k in ("steps", "loss", "seconds", "stopped")})
                    j["probes"] = ev.get("probes")
                elif ph == "asking":
                    j["state"] = "asking"
                elif ph == "finished":
                    j["answers"], j["both"], j["adapter_id"] = ev["answers"], ev.get("both"), ev["adapter_id"]
                    j["info"]["gpu_seconds"] = ev.get("gpu_seconds")
                    self.guard.add(ev.get("gpu_seconds", 0), "trainings")
                    j["state"], j["t_end"] = "finished", time.time()
                    self.durations.append(j["t_end"] - j["t_start"])
                    self.on_done(j)
                    with self.cv:  # the GPU is free for the next student while the adapter is saved
                        self.running.discard(jid)
                        self.cv.notify_all()
                elif ph == "saved":
                    j["saved"] = True
            if j["answers"] is None:
                raise RuntimeError("the GPU stopped before the answers came back")
        except Exception as e:  # noqa: BLE001
            print("[train] failed:", jid, type(e).__name__, str(e)[:300])
            if j["state"] != "finished":
                j["state"], j["error"], j["t_end"] = "failed", "The GPU could not finish this training. Try again.", time.time()
        finally:
            with self.cv:
                self.running.discard(jid)
                self.cv.notify_all()


def modal_gpu():
    """The deployed GPU classes, as the web app calls them: Brain answers, Trainer trains (one per GPU)."""
    import modal

    app_name = os.environ.get("BRAINLAB_APP", "northbridge-brainlab")
    brain = modal.Cls.from_name(app_name, "Brain")()
    trainer = modal.Cls.from_name(app_name, "Trainer")()

    class G:
        def answer(self, questions, facts=None, adapter_id=None, temperature=0.0):
            return brain.answer.remote(questions, facts, adapter_id, 60, temperature)

        def train(self, job_id, facts, tests, settings=None, context_facts=None, temperature=0.0):
            yield from trainer.train.remote_gen(job_id, facts, tests, settings, context_facts, temperature)

        def autoscale(self, min_containers=0, max_containers=None):
            kw = {"max_containers": max_containers} if max_containers else {}
            trainer.update_autoscaler(min_containers=min_containers, **kw)
            brain.update_autoscaler(min_containers=max(1, (min_containers + 1) // 2) if min_containers else 0)

    return G()


def create_app(gpu=None, store: Store | None = None) -> FastAPI:
    app = FastAPI(title="The Brain Lab", docs_url=None, redoc_url=None)
    store = store or Store(os.environ.get("BRAINLAB_DICT"))
    gpu = gpu or modal_gpu()
    guard = Guard(store, os.environ.get("BRAINLAB_GPU", "L4"))
    pool = ThreadPoolExecutor(max_workers=int(os.environ.get("BRAINLAB_THREADS", "128")))
    players: dict[str, dict] = {}
    for k in store.keys("p:"):
        players[k[2:]] = store.get(k)

    def save(p):
        p["updated"] = time.time()
        store.put("p:" + p["pid"], p)

    def on_done(job):
        p = players.get(job["pid"])
        if not p:
            return
        st = job.get("settings") or {}
        run = {"n": len(p.get("runs") or []) + 1, "job": job["id"], "settings": job.get("labels") or {},
               "temperature": job.get("temperature", 0.0),
               "answers": mark(job["tests"], job["answers"]),
               "both": mark(job["tests"], job["both"]) if job.get("both") else None,
               "adapter_id": job["adapter_id"], "curve": job["curve"][-200:], "info": job["info"],
               "probes": job.get("probes"), "facts": [f for f in job["facts"] if not f.get("distractor")],
               "distractors": sum(1 for f in job["facts"] if f.get("distractor")),
               "cost_usd": round((job["info"].get("gpu_seconds") or 0) * guard.rate, 4),
               "waited": round(job["t_start"] - job["t_submit"], 1), "at": time.time(), "lr_value": st.get("lr"),
               "rank_value": st.get("rank")}
        p.setdefault("runs", []).append(run)
        p["runs"] = p["runs"][-10:]
        p["trained"] = run
        save(p)

    queue = Queue(gpu, guard, on_done)
    app.state.queue, app.state.guard, app.state.players, app.state.store = queue, guard, players, store

    def player(req: Request) -> dict:
        pid = req.headers.get("x-player") or req.cookies.get("bl_pid")
        p = players.get(pid or "")
        if p is None:
            raise HTTPException(401, "Join first: open the lab and enter your name.")
        return p

    def admin(req: Request):
        want = os.environ.get("BRAINLAB_ADMIN_TOKEN")
        if not want or req.headers.get("x-admin-token") != want:
            raise HTTPException(403, "Admin token required.")

    @app.exception_handler(Refused)
    async def _refused(_, e: Refused):
        return JSONResponse({"detail": e.msg}, status_code=e.status)

    def mark(tests: list, answers: list) -> list:
        out = []
        for t, a in zip(tests, answers):
            out.append({**{k: t.get(k) for k in ("q", "a", "role", "fact", "kind", "note")}, "text": a["text"],
                        "moment": a.get("moment"), "prompt_tokens": a.get("prompt_tokens"),
                        "verdict": verdict(a["text"], t.get("a"))})
        return out

    async def ask_gpu(pid, questions, facts=None, adapter_id=None, temperature=0.0):
        guard.check(pid, "answer")
        try:
            r = await asyncio.get_running_loop().run_in_executor(
                pool, lambda: gpu.answer(questions, facts, adapter_id, temperature))
        except Refused:
            raise
        except Exception as e:  # noqa: BLE001
            print("[answer] error:", type(e).__name__, str(e)[:300])
            raise HTTPException(502, "The brain's GPU did not answer just now. Try again in a moment.")
        guard.add(r.get("gpu_seconds", 0), "answers")
        return r["answers"]

    def view(p: dict) -> dict:
        out = {k: p.get(k) for k in ("pid", "name", "badge", "facts", "before", "context", "trained", "job")}
        out["runs"] = p.get("runs") or []
        out["options"] = {"steps": list(BR.STEPS), "lr": BR.LRS, "rank": BR.RANKS, "temperatures": list(TEMPS),
                          "rate_usd_per_second": guard.rate, "distractors": [f["fact"] for f in L.distractors(p["badge"])]}
        return out

    # ------------------------------------------------------------------ pages
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    app.mount("/sky", StaticFiles(directory=EXP_STATIC), name="sky")

    def page(name):
        return FileResponse(STATIC / name, headers={"Cache-Control": "no-cache"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page("lab.html")

    @app.get("/wall", response_class=HTMLResponse)
    def wall_page():
        return page("wall.html")

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return page("admin.html")

    @app.get("/index.html")
    def index_alias():
        return RedirectResponse("/")

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "players": len(players), "queue": queue.stats()}

    # ------------------------------------------------------------------ joining, the badge
    @app.post("/api/join")
    async def join(req: Request):
        b = await req.json()
        name = " ".join(str(b.get("name", "")).split())[:40]
        if len(name) < 2:
            raise HTTPException(400, "Please type your name.")
        pid = uuid.uuid4().hex[:12]
        bd = L.badge(pid, name)
        p = {"pid": pid, "name": name, "joined": time.time(), "badge": bd, "facts": L.default_facts(bd),
             "facts_saved": False, "before": None, "context": None, "trained": None, "job": None}
        players[pid] = p
        save(p)
        resp = JSONResponse(view(p))
        https = req.url.scheme == "https" or req.headers.get("x-forwarded-proto") == "https"
        resp.set_cookie("bl_pid", pid, max_age=60 * 60 * 24 * 30, samesite="lax", secure=https)
        return resp

    @app.get("/api/me")
    def me(req: Request):
        p = player(req)
        out = view(p)
        if p.get("job"):
            out["job_view"] = queue.view(p["job"])
        return out

    @app.post("/api/badge/reroll")
    def reroll(req: Request):
        p = player(req)
        if p.get("trained") or p.get("job") and (queue.view(p["job"]) or {}).get("state") not in (None, "finished", "failed"):
            raise HTTPException(409, "Your brain has already learnt this badge.")
        bd = L.badge(p["pid"], p["name"], (p["badge"].get("reroll") or 0) + 1)
        p.update({"badge": bd, "facts": L.default_facts(bd), "before": None, "context": None, "facts_saved": False})
        save(p)
        return view(p)

    # ------------------------------------------------------------------ before
    def temp_of(b) -> float:
        try:
            t = float(b.get("temperature") or 0)
        except (TypeError, ValueError):
            t = 0.0
        return min(TEMPS, key=lambda x: abs(x - t))

    @app.post("/api/before")
    async def before(req: Request):
        p = player(req)
        b = await req.json() if (await req.body()) else {}
        t = temp_of(b)
        qs = L.before_questions(p["badge"])
        ans = await ask_gpu(p["pid"], [q["q"] for q in qs], temperature=t)
        p["before"] = {"answers": mark(qs, ans), "at": time.time(), "temperature": t}
        save(p)
        return p["before"]

    # ------------------------------------------------------------------ teach: the facts
    @app.post("/api/facts")
    async def facts(req: Request):
        p = player(req)
        b = await req.json()
        fs, errs = L.validate_facts(b.get("facts"))
        if errs:
            raise HTTPException(400, " ".join(errs[:3]))
        if fs != p["facts"]:
            p["context"] = None
        p["facts"], p["facts_saved"] = fs, True
        save(p)
        return {"facts": fs, "tests": L.test_set(fs)}

    TOK = {}

    def tokenizer():
        if "t" not in TOK:
            from transformers import AutoTokenizer

            TOK["t"] = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
        return TOK["t"]

    @app.get("/api/training_data")
    def training_data(req: Request, distractors: int = 0):
        """Exactly what the fine-tune will see: every example, as tokens, with the scored (answer) tokens marked."""
        p = player(req)
        from .brain import build_examples

        facts = p["facts"] + (L.distractors(p["badge"]) if distractors else [])
        try:
            tok = tokenizer()
        except Exception as e:  # noqa: BLE001
            raise HTTPException(503, f"The tokenizer is not available here ({type(e).__name__}).")
        ex = build_examples(tok, facts)
        total = sum(len(e["ids"]) for e in ex)
        scored = sum(len(e["ids"]) - e["start"] for e in ex)
        out = []
        for e in ex:
            pieces = [tok.decode([t]) for t in e["ids"]]
            out.append({"fact_i": e["fact_i"], "variant": e["variant"], "user": e["user"], "answer": e["answer"],
                        "distractor": e["distractor"], "n_tokens": len(e["ids"]), "start": e["start"],
                        "pieces": pieces})
        return {"examples": out, "n_examples": len(ex), "tokens": total, "scored_tokens": scored,
                "facts": len(facts), "variants": len(BR.VARIANTS), "variant_templates": list(BR.VARIANTS)}

    # ------------------------------------------------------------------ path A: the facts in the prompt
    @app.post("/api/context")
    async def context(req: Request):
        p = player(req)
        b = await req.json() if (await req.body()) else {}
        t = temp_of(b)
        tests = L.test_set(p["facts"])
        facts = [f["fact"] for f in p["facts"]]
        t0 = time.time()
        ans = await ask_gpu(p["pid"], [x["q"] for x in tests], facts=facts, temperature=t)
        p["context"] = {"answers": mark(tests, ans), "facts": p["facts"], "seconds": round(time.time() - t0, 1),
                        "at": time.time(), "temperature": t}
        save(p)
        return p["context"]

    # ------------------------------------------------------------------ path B: training
    @app.post("/api/train")
    async def train(req: Request):
        p = player(req)
        b = await req.json() if (await req.body()) else {}
        guard.check(p["pid"], "train")
        steps = int(b.get("steps") or 30)
        steps = min(BR.STEPS, key=lambda x: abs(x - steps))
        lr_k = b.get("lr") if b.get("lr") in BR.LRS else "medium"
        rk_k = b.get("rank") if b.get("rank") in BR.RANKS else "medium"
        dis = bool(b.get("distractors"))
        t = temp_of(b)
        facts = p["facts"] + (L.distractors(p["badge"]) if dis else [])
        settings = {"steps": steps, "lr": BR.LRS[lr_k], "rank": BR.RANKS[rk_k]}
        labels = {"steps": steps, "lr": lr_k, "rank": rk_k, "distractors": dis, "facts": len(p["facts"]),
                  "temperature": t}
        job = queue.submit(p["pid"], facts, L.test_set(p["facts"]),
                           {"settings": settings, "labels": labels, "temperature": t,
                            "context_facts": [f["fact"] for f in p["facts"]]})
        p["job"] = job["id"]
        save(p)
        return queue.view(job["id"])

    @app.get("/api/train/status")
    def train_status(req: Request):
        p = player(req)
        v = queue.view(p.get("job") or "")
        if v is None:
            return {"state": "none", "trained": p.get("trained"), "runs": p.get("runs") or []}
        if v["state"] == "finished":
            v["trained"] = p.get("trained")
            v["runs"] = p.get("runs") or []
        return v

    # ------------------------------------------------------------------ ask anything, four ways
    @app.post("/api/ask")
    async def ask(req: Request):
        p = player(req)
        b = await req.json()
        q = " ".join(str(b.get("q", "")).split())[:200]
        if len(q) < 3:
            raise HTTPException(400, "Type a question.")
        t = temp_of(b)
        modes = [m for m in (b.get("modes") or ["bare", "context", "trained", "both"])
                 if m in ("bare", "context", "trained", "both")]
        aid = (p.get("trained") or {}).get("adapter_id")
        if not aid:
            modes = [m for m in modes if m not in ("trained", "both")]
        facts = [f["fact"] for f in p["facts"]]
        calls = {"bare": ([q], None, None), "context": ([q], facts, None), "trained": ([q], None, aid),
                 "both": ([q], facts, aid)}
        res = await asyncio.gather(*[ask_gpu(p["pid"], *calls[m], temperature=t) for m in modes])
        out = {m: {"text": r[0]["text"], "moment": r[0]["moment"]} for m, r in zip(modes, res)}
        p.setdefault("asked", []).append({"q": q, **{m: out[m]["text"] for m in out}, "at": time.time(), "temperature": t})
        p["asked"] = p["asked"][-20:]
        save(p)
        return {"q": q, "answers": out, "temperature": t}

    # ------------------------------------------------------------------ the class wall
    def score(block, roles):
        if not block:
            return None
        rows = [a for a in block["answers"] if a["role"] in roles and a.get("a")]
        return {"right": sum(a["verdict"] == "right" for a in rows), "of": len(rows)}

    @app.get("/api/wall")
    def wall():
        rows = []
        agg = {k: [0, 0] for k in ("before", "context", "trained", "paraphrase", "general")}
        for p in players.values():
            if not p.get("before") and not p.get("context") and not p.get("trained"):
                continue
            runs = p.get("runs") or []
            best = max(runs, key=lambda r: (sum(a["verdict"] == "right" for a in r["answers"] if a["role"] in ("taught", "paraphrase")),
                                            -(r["info"].get("seconds") or 0))) if runs else None
            emma = next((a for a in (p.get("before") or {}).get("answers", []) if a["role"] == "emma"), None)
            tr_emma = next((a for a in (best or {}).get("answers", []) if a["q"] == L.EMMA_Q), None)
            r = {"name": p["name"], "city": p["badge"]["city"], "model": p["badge"]["model"],
                 "facts": [f["fact"] for f in p["facts"] if f.get("who") != "lecture"][:4] if p.get("facts_saved") else [],
                 "before": score(p.get("before"), ("emma", "you")),
                 "context": score(p.get("context"), ("taught", "emma")),
                 "trained": score(best, ("taught", "emma")),
                 "paraphrase": score(best, ("paraphrase",)),
                 "general": score(best, ("general",)),
                 "runs": len(p.get("runs") or []),
                 "best": best and {"steps": best["settings"].get("steps"), "lr": best["settings"].get("lr"),
                                   "rank": best["settings"].get("rank"), "seconds": best["info"].get("seconds")},
                 "team": p["badge"].get("team"),
                 "emma_before": emma and emma["text"], "emma_trained": tr_emma and tr_emma["text"],
                 "at": p.get("updated", 0)}
            for k in agg:
                if r[k]:
                    agg[k][0] += r[k]["right"]
                    agg[k][1] += r[k]["of"]
            rows.append(r)
        rows.sort(key=lambda r: -r["at"])
        nums = []
        for p in players.values():
            for a in (p.get("before") or {}).get("answers", []):
                if a["role"] == "emma":
                    m = re.search(r"\d+(?:, ?\d{3})*", a["text"])
                    if m:
                        nums.append(m.group(0).replace(", ", ","))
        return {"count": len(rows), "rows": rows[:150], "agg": agg, "emma_numbers": nums[-150:],
                "players": len(players), "queue": {k: v for k, v in queue.stats().items() if k != "waits"}}

    # ------------------------------------------------------------------ admin
    @app.get("/api/admin/status")
    def admin_status(req: Request):
        admin(req)
        s = guard.spent()
        return {"flags": guard.flags(), "spend": s, "usd_today": guard.usd(s), "day_ist": guard.today(),
                "rate_usd_per_gpu_second": guard.rate, "players": len(players), "queue": queue.stats(),
                "trained": sum(1 for p in players.values() if p.get("trained")),
                "recent": [{"pid": p["pid"], "name": p["name"], "before": bool(p.get("before")),
                            "context": bool(p.get("context")), "trained": bool(p.get("trained")),
                            "job": (queue.view(p["job"]) or {}).get("state") if p.get("job") else None}
                           for p in sorted(players.values(), key=lambda p: -p.get("joined", 0))[:80]]}

    @app.post("/api/admin/flags")
    async def admin_flags(req: Request):
        admin(req)
        b = await req.json()
        kw = {}
        for k in ("enabled", "training"):
            if k in b:
                kw[k] = bool(b[k])
        if "reason" in b:
            kw["reason"] = str(b["reason"])[:200]
        if "cap_usd" in b:
            kw["cap_usd"] = max(0.0, float(b["cap_usd"]))
        if "train_slots" in b:
            kw["train_slots"] = max(1, min(64, int(b["train_slots"])))
        return guard.set_flags(**kw)

    @app.post("/api/admin/warm")
    async def admin_warm(req: Request):
        """Keep n GPU containers warm (n = 0 lets them sleep). Optionally change the most GPUs Modal may start."""
        admin(req)
        b = await req.json()
        n = max(0, min(8, int(b.get("n", 0))))
        kw = {"min_containers": n}
        if b.get("max"):
            kw["max_containers"] = max(1, min(20, int(b["max"])))
        await asyncio.get_running_loop().run_in_executor(pool, lambda: gpu.autoscale(**kw))
        f = guard.flags()
        if f.get("warm_since"):
            guard.add_warm(f["warm"] * (time.time() - f["warm_since"]))
        extra = {"train_slots": kw["max_containers"]} if kw.get("max_containers") else {}
        return guard.set_flags(warm=n, warm_since=time.time() if n else None, **extra)

    @app.post("/api/admin/purge")
    async def admin_purge(req: Request):
        """Remove players (and their results) from the lab and the wall: {"all": true} before class, or
        {"prefixes": ["Load "]} after a load test."""
        admin(req)
        b = await req.json()
        pre = [str(x) for x in (b.get("prefixes") or []) if str(x)]
        gone = [pid for pid, p in list(players.items()) if b.get("all") is True or any(p["name"].startswith(x) for x in pre)]
        for pid in gone:
            players.pop(pid, None)
            store.delete("p:" + pid)
        return {"removed": len(gone), "players": len(players)}

    @app.post("/api/admin/reset_player")
    async def admin_reset(req: Request):
        admin(req)
        b = await req.json()
        p = players.get(b.get("pid"))
        if not p:
            raise HTTPException(404, "No such player.")
        p.update({"before": None, "context": None, "trained": None, "job": None, "runs": []})
        save(p)
        return {"ok": True}

    return app


app = create_app() if os.environ.get("BRAINLAB_NO_APP") != "1" and os.environ.get("BRAINLAB_DICT") else None
