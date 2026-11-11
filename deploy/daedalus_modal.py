"""Daedalus on Modal (Lecture 5, the workshop): app `northbridge-daedalus`, workspace rajatworkspace.

    /Users/raj/.venv/bin/modal deploy deploy/daedalus_modal.py                          # deploy (or update) the live app
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd status         # spend, workshops, flags
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd warm           # keep the web container on (class)
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd cool           # let it sleep (after class)
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd cap --cap 60            # the class's US$ a day
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd student-cap --cap 2     # each student's US$ a day
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd purge-tests    # remove probe / load / film workshops
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd purge-all      # empty the wall before class
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::test                       # the API test on the live URL
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::load --n 40                # 40 students at once
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::knobs                      # every harness knob, measured (live app)
    /Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::record --which loop,...    # screen recordings + screenshots

One CPU web container (max_containers=1, @modal.concurrent): every student's workshop (their Ledgerline sandbox, their
conversation, their waiting workflow runs) lives in its memory; names, settings, workflows, runs and races are also in the
modal.Dict `northbridge-daedalus-state`. The model is gemini-3.8-flash, called directly (Gemini API; the OpenRouter key is
removed at start). Keys come only from the existing Modal secret `rasoi-experience` (GEMINI_API_KEY,
NORTHBRIDGE_ADMIN_TOKEN); never in the image, never printed. min_containers is 0 here, so a deploy never leaves a
container running; `admin --cmd warm` keeps one on for class, and a daily cron (04:00 UTC) sets it back to 0.
Do not redeploy during class: sandboxes and conversations start again.
"""
import json
import os
import pathlib
import sys
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = "northbridge-daedalus"
URL = "https://rajatworkspace--northbridge-daedalus.us-east.modal.run"
L5 = ROOT / "lectures" / "L5-the-loop"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules", "cassettes", "legacy_ui", "tests_logs",
        "brainlab", "raglab", "wiki", "hephaestus"}


def _keep(p) -> bool:
    s = str(p)
    if any(x in SKIP for x in pathlib.Path(p).parts):
        return False
    if s.endswith((".env", ".png", ".mp4", ".ipynb", ".webm", ".jpg")):
        return False
    if s.endswith(".jsonl") and "/docs/_index/" not in s:
        return False
    return True


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi==0.115.6", "uvicorn", "httpx", "pydantic>=2", "jsonschema", "pyyaml",
                 "rank_bm25", "fastembed")
    .env({"FASTEMBED_CACHE_PATH": "/models/fastembed"})
    .run_commands("python -c \"from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')\"")
    .env({"PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1", "DAED_DICT": "northbridge-daedalus-state",
          "DAED_APP": APP, "DAED_URL": URL, "LEDGER_LLM_MODE": "live"})
    .add_local_dir(ROOT / "ledgerline", "/app/ledgerline", ignore=lambda p: not _keep(p))
)
app = modal.App(APP, image=image)
secret = modal.Secret.from_name("rasoi-experience")
outvol = modal.Volume.from_name("northbridge-daedalus-out", create_if_missing=True)


@app.function(secrets=[secret], max_containers=1, min_containers=0, scaledown_window=1800, cpu=4, memory=8192, timeout=900)
@modal.concurrent(max_inputs=400)
@modal.asgi_app(label="northbridge-daedalus")
def web():
    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.daedalus.app import create_app

    return create_app()


@app.function(schedule=modal.Cron("0 4 * * *"), timeout=120)  # every day 04:00 UTC: the web container may sleep
def class_cool():
    modal.Function.from_name(APP, "web").update_autoscaler(min_containers=0)
    print("web min_containers -> 0")


# ---------------------------------------------------------------------------------------------------- operator
@app.function(secrets=[secret], timeout=300)
def op(cmd: str, reason: str = "", cap: float = 0) -> dict:
    """Operator commands, run inside Modal so the admin token never leaves the secret store."""
    import httpx

    h = {"X-Admin-Token": os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ["RASOI_ADMIN_TOKEN"]}
    c = httpx.Client(base_url=URL, timeout=180)
    if cmd == "warm":
        modal.Function.from_name(APP, "web").update_autoscaler(min_containers=1)
        for _ in range(8):
            try:
                print(c.get("/healthz").json())
                break
            except Exception as e:  # noqa: BLE001
                print("warm: waiting", type(e).__name__)
                time.sleep(10)
    elif cmd == "cool":
        modal.Function.from_name(APP, "web").update_autoscaler(min_containers=0)
    elif cmd == "pause":
        c.post("/api/admin/flags", json={"enabled": False, "reason": reason}, headers=h).raise_for_status()
    elif cmd == "resume":
        c.post("/api/admin/flags", json={"enabled": True, "reason": ""}, headers=h).raise_for_status()
    elif cmd == "cap":
        c.post("/api/admin/flags", json={"cap_usd": cap}, headers=h).raise_for_status()
    elif cmd == "student-cap":
        c.post("/api/admin/flags", json={"student_cap_usd": cap}, headers=h).raise_for_status()
    elif cmd == "purge-tests":
        print(c.post("/api/admin/purge", json={"prefixes": ["Probe ", "Load ", "Test ", "Film ", "Shot ", "Knob "]}, headers=h).json())
    elif cmd == "purge-all":
        print(c.post("/api/admin/purge", json={"all": True}, headers=h).json())
    s = c.get("/api/admin/status", headers=h)
    s.raise_for_status()
    out = s.json()
    out.pop("recent", None)
    out["no_token_status"] = c.get("/api/admin/status").status_code
    return out


@app.local_entrypoint()
def admin(cmd: str = "status", reason: str = "", cap: float = 0):
    print(json.dumps(op.remote(cmd, reason, cap), indent=1, ensure_ascii=False))


# ---------------------------------------------------------------------------------------------------- API test (live URL)
client_image = modal.Image.debian_slim(python_version="3.11").pip_install("httpx")


@app.function(image=client_image, timeout=1800)
def api_test() -> dict:
    """Every endpoint a student uses, on the live URL, as a student would (live model). Returns the checks."""
    import httpx

    c = httpx.Client(base_url=URL, timeout=300)
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:300]})

    chk("healthz", c.get("/healthz").status_code == 200)
    cat = c.get("/api/catalog").json()
    chk("catalog: 16 tools, 11 blocks, 6 jobs", len(cat["tools"]) == 16 and len(cat["blocks"]) == 11 and len(cat["jobs"]) == 6,
        (len(cat["tools"]), len(cat["blocks"]), len(cat["jobs"])))
    chk("join refuses a blank name", c.post("/api/join", json={"name": " "}).status_code == 400)
    me = c.post("/api/join", json={"name": "Test API"}).json()
    H = {"X-Workshop-Key": me["key"]}
    chk("join gives a dx- key", me["key"].startswith("dx-"))
    chk("a wrong key is refused", c.get("/api/me", headers={"X-Workshop-Key": "dx-nope"}).status_code == 401)
    # the loop, step by step
    t = c.post("/api/loop/say", json={"text": "Order 2,000 BAT-500 packs from Voltway for the spring launch run."}, headers=H)
    chk("say", t.status_code == 200 and not t.json()["done"], t.text[:200])
    s1 = c.post("/api/loop/step", json={}, headers=H).json()
    chk("step 1 is a model call", s1["step"]["kind"] == "model" and s1["step"]["n"] == 1, s1["step"].get("calls"))
    r = c.post("/api/loop/run", json={}, headers=H).json()
    chk("run to the end", r["done"], r["turn"]["end"])
    r2 = c.post("/api/loop/say", json={"text": "Yes, go ahead."}, headers=H).json()
    r2 = c.post("/api/loop/run", json={}, headers=H).json()
    chk("the yes pauses on Daniel", r2["turn"]["end"] == "paused" and r2["waiting"], (r2["turn"]["end"], r2["waiting"]))
    n = c.post("/api/loop/night", json={}, headers=H).json()
    chk("next morning: state as JSON", n["bytes"] > 1000 and n["waiting"], (n["bytes"], n["waiting"]))
    early = c.post("/api/loop/say", json={"text": cat["morning"]}, headers=H).json()
    chk("not signed yet: the harness answers, 0 model calls", early["done"] and early["turn"]["model_calls"] == 0,
        early["turn"]["reply"][:120])
    inbox = c.get("/api/inbox", headers=H).json()
    chk("Daniel's inbox shows the request", any(w["doc_no"].startswith("PR/") for w in inbox["waiting"]), inbox["waiting"])
    doc = next(w["doc_no"] for w in inbox["waiting"] if w["doc_no"].startswith("PR/"))
    sg = c.post("/api/inbox/sign", json={"doc_no": doc}, headers=H).json()
    chk("sign as Daniel", sg["result"].get("ok"), sg["result"])
    c.post("/api/loop/say", json={"text": cat["morning"]}, headers=H)
    r3 = c.post("/api/loop/run", json={}, headers=H).json()
    docs = c.get("/api/docs", headers=H).json()
    chk("the morning finishes the job: one released order", any(o["status"] == "RL" for o in docs["orders"]), docs["orders"])
    # knobs
    cfg = dict(cat["shipped"], max_steps=2)
    m = c.post("/api/agent/config", json={"config": cfg}, headers=H).json()
    chk("config: max steps 2", m["config"]["max_steps"] == 2 and "max steps 2" in m["changed"], m["changed"])
    c.post("/api/agent/config", json={"config": cat["shipped"]}, headers=H)
    # workflow: run, wait, sign, resume
    c.post("/api/sandbox/reset", json={}, headers=H)
    w = c.post("/api/workflow/run", json={"job": "spring"}, headers=H).json()
    chk("workflow waits for Daniel", w["status"] == "waiting" and w["saved_bytes"], (w["status"], w.get("reply")))
    c.post("/api/inbox/sign", json={"doc_no": w["facts"]["request_no"]}, headers=H)
    w2 = c.post("/api/workflow/resume", json={"run": w["id"]}, headers=H).json()
    chk("workflow resumes and releases", w2["status"] == "done" and w2["facts"].get("po_status") == "RL", w2.get("reply"))
    ws = c.post("/api/workflow/run", json={"job": "nordic", "step": True}, headers=H).json()
    chk("step by step: one step at a time", ws["status"] == "running" and len(ws["steps"]) == 1, len(ws["steps"]))
    blocks = [b for b in cat["shipped_blocks"] if b["block"] != "item"]
    wb = c.post("/api/workflow", json={"blocks": blocks}, headers=H).json()
    chk("remove a block", "no 'Find the item'" in wb["blocks_changed"], wb["blocks_changed"])
    wb_r = c.post("/api/workflow/run", json={"job": "bells"}, headers=H)
    wbad = wb_r.json() if wb_r.status_code == 200 else {"status": wb_r.status_code, "reply": wb_r.text}
    chk("a missing block breaks the run and says which", wbad["status"] == "failed" and "Find the item" in wbad["reply"], wbad["reply"])
    c.post("/api/workflow", json={"blocks": cat["shipped_blocks"]}, headers=H)
    # the race
    j = c.post("/api/race", json={"repeats": 1}, headers=H).json()
    for _ in range(200):
        time.sleep(3)
        j = c.get(f"/api/job/{j['id']}", headers=H).json()
        if j["state"] != "running":
            break
    chk("race finishes", j["state"] == "done", j.get("error"))
    res = j.get("result") or {}
    chk("race: 6 workflow rows, 6 agent rows", len(res.get("workflow", [])) == 6 and len(res.get("agent", [])) == 6)
    wall = c.get("/api/wall").json()
    chk("wall lists the workshop", any(r["name"] == "Test API" for r in wall["rows"]))
    chk("admin needs a token", c.get("/api/admin/status").status_code == 403)
    return {"checks": checks, "passed": sum(1 for x in checks if x["ok"]), "of": len(checks),
            "race_totals": res.get("totals")}


@app.local_entrypoint()
def test():
    r = api_test.remote()
    for x in r["checks"]:
        print(("PASS " if x["ok"] else "FAIL ") + x["check"] + ("" if x["ok"] else "  · " + x["detail"]))
    print(f"{r['passed']} / {r['of']}  race totals: {json.dumps(r['race_totals'])}")
    (L5 / "experiments" / "logs").mkdir(parents=True, exist_ok=True)
    (L5 / "experiments" / "logs" / "daedalus_api_test.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------------------------------------------- knobs on the live app
@app.function(image=client_image, timeout=7200, volumes={"/out": outvol})
def knobs_run(repeats: int = 2, only: str = "") -> dict:
    """Each harness knob (one change from shipped) and each workflow change, measured on the deployed app: a fresh
    workshop per variant ("Knob <variant> r<k>"), POST /api/race (the workflow and the agent on the six jobs)."""
    import httpx
    from concurrent.futures import ThreadPoolExecutor

    c = httpx.Client(base_url=URL, timeout=600)
    cat = c.get("/api/catalog").json()
    S = cat["shipped"]
    agent_v = {"shipped": {}, "max_steps_4": {"max_steps": 4}, "max_steps_2": {"max_steps": 2}, "budget_6000": {"budget": 6000},
               "tools_2": {"tools": cat["two"]}, "tools_16": {"tools": cat["all"]}, "prompt_bare": {"prompt": "bare"},
               "pause_off": {"pause": False}, "recovery_off": {"recovery": False}}
    sb = cat["shipped_blocks"]
    wf_v = {"no_cert": [b for b in sb if b["block"] != "cert"], "no_approval": [b for b in sb if b["block"] != "approval"],
            "cert_switch": [dict(b, on_fail="switch") if b["block"] == "cert" else b for b in sb],
            "no_budget": [b for b in sb if b["block"] != "budget"]}
    todo = [("agent", v, k) for v in agent_v for k in range(repeats)] + [("workflow", v, 0) for v in wf_v]
    if only:
        todo = [t for t in todo if t[1] in only.split(",")]

    def one(t):
        who, v, k = t
        me = c.post("/api/join", json={"name": f"Knob {v} r{k}"}).json()
        H = {"X-Workshop-Key": me["key"]}
        if who == "agent":
            c.post("/api/agent/config", json={"config": dict(S, **agent_v[v])}, headers=H)
        else:
            c.post("/api/workflow", json={"blocks": wf_v[v]}, headers=H)
        j = c.post("/api/race", json={"repeats": 1}, headers=H).json()
        for _ in range(400):
            time.sleep(4)
            j = c.get(f"/api/job/{j['id']}", headers=H).json()
            if j["state"] != "running":
                break
        res = j.get("result") or {}
        return {"who": who, "variant": v, "repeat": k, "state": j["state"], "error": j.get("error"),
                "totals": res.get("totals"), "workflow": res.get("workflow"), "agent": res.get("agent")}

    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, todo))
    out = {"at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "url": URL, "agent_variants": agent_v,
           "workflow_variants": {k: [b["block"] + (f":{b.get('on_fail')}" if b["block"] == "cert" else "") for b in v] for k, v in wf_v.items()},
           "rows": rows}
    pathlib.Path("/out/knobs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    outvol.commit()
    return out


@app.local_entrypoint()
def knobs(repeats: int = 2, only: str = ""):
    r = knobs_run.remote(repeats, only)
    dst = L5 / "experiments" / "logs" / "daedalus_knobs.json"
    dst.write_text(json.dumps(r, indent=1, ensure_ascii=False))
    print("wrote", dst, len(r["rows"]), "rows")


# ---------------------------------------------------------------------------------------------------- load test
@app.function(image=client_image, timeout=3600)
def load_run(n: int = 40) -> dict:
    """n students at once: join, one loop step on Emma's order, a workflow run, then everyone presses Start the race."""
    import httpx
    from concurrent.futures import ThreadPoolExecutor

    def student(i):
        c = httpx.Client(base_url=URL, timeout=900)
        r = {"i": i}
        t0 = time.time()
        me = c.post("/api/join", json={"name": f"Load {i:02d}"}).json()
        H = {"X-Workshop-Key": me["key"]}
        r["join"] = time.time() - t0
        t0 = time.time()
        c.post("/api/loop/say", json={"text": "Order 2,000 BAT-500 packs from Voltway for the spring launch run."}, headers=H)
        s = c.post("/api/loop/step", json={}, headers=H)
        r["step"] = time.time() - t0
        r["step_ok"] = s.status_code == 200
        t0 = time.time()
        w = c.post("/api/workflow/run", json={"job": "spring"}, headers=H)
        r["workflow"] = time.time() - t0
        r["workflow_ok"] = w.status_code == 200 and w.json().get("status") == "waiting"
        return r, c, H

    with ThreadPoolExecutor(n) as ex:
        first = list(ex.map(student, range(n)))

    def race(t):
        r, c, H = t
        t0 = time.time()
        j = c.post("/api/race", json={"repeats": 1}, headers=H).json()
        for _ in range(600):
            time.sleep(3)
            j = c.get(f"/api/job/{j['id']}", headers=H).json()
            if j["state"] != "running":
                break
        r["race"] = time.time() - t0
        res = j.get("result") or {}
        r["race_state"], r["race_totals"] = j["state"], res.get("totals")
        return r

    with ThreadPoolExecutor(n) as ex:
        rows = list(ex.map(race, first))

    def dist(k):
        v = sorted(x[k] for x in rows if isinstance(x.get(k), (int, float)))
        return {"median": round(v[len(v) // 2], 2), "p90": round(v[int(len(v) * 0.9) - 1], 2), "max": round(v[-1], 2)} if v else None

    return {"n": n, "rows": rows, "join": dist("join"), "step": dist("step"), "workflow": dist("workflow"), "race": dist("race"),
            "step_ok": sum(1 for x in rows if x.get("step_ok")), "workflow_ok": sum(1 for x in rows if x.get("workflow_ok")),
            "race_done": sum(1 for x in rows if x.get("race_state") == "done"),
            "agent_right": [x["race_totals"]["agent"]["right"] for x in rows if x.get("race_totals")],
            "workflow_right": [x["race_totals"]["workflow"]["right"] for x in rows if x.get("race_totals")]}


@app.local_entrypoint()
def load(n: int = 40):
    r = load_run.remote(n)
    dst = L5 / "experiments" / "logs" / f"daedalus_load_{n}.json"
    dst.write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    print({k: r[k] for k in ("n", "join", "step", "workflow", "race", "step_ok", "workflow_ok", "race_done")})


# ---------------------------------------------------------------------------------------------------- recordings
pw_image = (modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg")
            .pip_install("playwright==1.47.0", "httpx").run_commands("playwright install --with-deps chromium")
            .add_local_file(L5 / "experiments" / "daedalus_record.py", "/job/daedalus_record.py"))


@app.function(image=pw_image, timeout=3000, cpu=4, memory=8192, volumes={"/out": outvol})
def record_one(which: str) -> dict:
    sys.path.insert(0, "/job")
    import daedalus_record

    files = daedalus_record.record(which, URL)
    d = pathlib.Path("/out/record")
    for k, v in files.items():
        p = d / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(v)
    outvol.commit()
    return files


@app.local_entrypoint()
def record(which: str = "loop,night,knob,workflow,wfwait,race,figs"):
    names = [w for w in which.split(",") if w]
    for name, r in zip(names, record_one.map(names, return_exceptions=True)):
        if isinstance(r, Exception):
            print("FAILED", name, type(r).__name__, str(r)[:400])
            continue
        for k, v in r.items():
            dst = L5 / k
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(v)
            print("wrote", dst, len(v))


@app.function(image=pw_image, timeout=600)
def sheet(data: bytes, n: int = 8) -> dict:
    """A contact sheet of a recording (n frames) and its duration, to check recordings by eye."""
    import subprocess

    pathlib.Path("/tmp/v.mp4").write_bytes(data)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "/tmp/v.mp4"],
                               capture_output=True, text=True).stdout.strip() or 0)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/v.mp4", "-vf",
                    f"fps={n}/{max(dur, 1):.2f},scale=800:-1,tile=2x{(n + 1) // 2}", "-frames:v", "1", "/tmp/s.png"], check=True)
    return {"duration": dur, "png": pathlib.Path("/tmp/s.png").read_bytes()}


@app.local_entrypoint()
def sheets(names: str = "loop,knob,workflow,wfwait,race"):
    out = L5 / "qa" / "sheets"
    out.mkdir(parents=True, exist_ok=True)
    for n in names.split(","):
        f = L5 / "films" / f"daedalus_{n}.mp4"
        if not f.exists():
            print("missing", f)
            continue
        r = sheet.remote(f.read_bytes())
        (out / f"{n}.png").write_bytes(r["png"])
        print(n, round(r["duration"], 1), "s ->", out / f"{n}.png")
