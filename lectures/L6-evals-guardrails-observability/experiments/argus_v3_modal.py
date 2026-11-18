"""Builder C's test bench for Argus v3 (Lecture 6's teaching views: One turn, four checks · Is the judge right? · The same
checks in DeepEval · Score with DeepEval · Write the score on this trace).

Nothing here deploys anything or touches the live app. Argus runs INSIDE one Modal container (uvicorn on port 8000), from the
local `ledgerline` folder, with the image recipe of deploy/argus_modal.py, an in-memory store (ARGUS_DICT is never set, so
the live app's modal.Dict is not opened) and its own random admin token. It builds on the Lecture 7 bench
(lectures/L6b-guardrails/experiments/argus_c_modal.py, argus_c_test.py), whose helpers and checks it reuses.

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/argus_v3_modal.py::gen     # build argus/teach.json from the logs (4 judge calls)
    tools/mrun.sh .../argus_v3_modal.py::test --what mech   # scripted model: everything that was there is unchanged; the new views' mechanics
    tools/mrun.sh .../argus_v3_modal.py::test --what live   # real models: the judge, the labelled set, DeepEval, a conversation, a score on a trace
    tools/mrun.sh .../argus_v3_modal.py::test --what lab    # Lecture 6's argus_lab.api_test, unchanged (flag off); lab_on: flag on
    tools/mrun.sh .../argus_v3_modal.py::test --what load   # 30 students at once on the new endpoints, DeepEval in its own Modal function
    tools/mrun.sh .../argus_v3_modal.py::record             # the screenshots (add --url <live URL> after a deploy)

DeepEval in the bench: for mech/live/record a virtual environment in the bench's container (/opt/deepeval, the same pinned
versions) runs argus/deepeval_runner.py as a process of its own; for `load` the function `deepeval_run` below, which is the
deploy file's function word for word, is called in its own containers and reaches the bench's Argus through a Modal tunnel.
Results: experiments/logs/argus_v3_test.json (+ .txt), argus_v3_gen.json, argus_v3_record.json, figs/argus/*.png,
spend_parts/v3_argus.json. Keys: ANTHROPIC_API_KEY from the Modal secret forge-anthropic; Langfuse and LangSmith keys from
the course .env, sent as a Modal secret (for `live`, `lab` and `record`). Never printed, never written.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

import modal

_P = pathlib.Path(__file__).resolve()
LOCAL = modal.is_local()
ROOT = _P.parents[3] if LOCAL else pathlib.Path("/course")
L6 = ROOT / "lectures" / "L6-evals-guardrails-observability"
L7 = ROOT / "lectures" / "L6b-guardrails"
BASE_REV = "0988a27"          # Argus as it is deployed today (before the Lecture 7 change and before v3)
ARGUS = "ledgerline/ledgerline/argus"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules", "cassettes", "legacy_ui", "tests_logs",
        "brainlab", "raglab", "wiki", "hephaestus", "daedalus"}                      # as deploy/argus_modal.py
TR_KEYS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL", "LANGFUSE_HOST",
           "LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT")
INJ_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"
SCRATCH = pathlib.Path(os.environ.get("ARGUS_C_SCRATCH") or tempfile.gettempdir()) / "argus_v3"


def _keep(p) -> bool:
    s = str(p)
    if any(x in SKIP for x in pathlib.Path(p).parts):
        return False
    if s.endswith((".env", ".png", ".mp4", ".ipynb", ".webm", ".jpg")):
        return False
    if s.endswith(".jsonl") and "/docs/_index/" not in s:
        return False
    return True


def _tr_env():
    env = {}
    f = ROOT / ".env"
    if LOCAL and f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in TR_KEYS:
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _base_dir() -> str:
    """Argus at BASE_REV, exported to a temporary folder (git only; nothing is checked out or changed)."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="argus_base_"))
    files = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", BASE_REV, ARGUS], capture_output=True,
                           text=True, check=True).stdout.split()
    for f in files:
        dst = d / pathlib.Path(f).relative_to(ARGUS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE_REV}:{f}"], capture_output=True, check=True).stdout)
    return str(d)


# the Lecture 7 bench's image, layer for layer (Modal reuses it), then DeepEval in a virtual environment of its own
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai==3.51.0", "fastapi==0.115.6", "uvicorn", "httpx==0.28.1", "pydantic>=2", "jsonschema", "pyyaml",
                 "rank_bm25", "fastembed==0.9.1", "opentelemetry-sdk==1.45.2", "opentelemetry-exporter-otlp-proto-http==1.45.2")
    .pip_install("torch==2.15.0", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("transformers==5.23.0", "presidio-analyzer==2.2.366", "presidio-anonymizer==2.2.366", "spacy==3.8.18")
    .run_commands("python -m spacy download en_core_web_sm")
    .env({"FASTEMBED_CACHE_PATH": "/models/fastembed", "HF_HOME": "/models/hf", "HF_HUB_DISABLE_TELEMETRY": "1",
          "TOKENIZERS_PARALLELISM": "false"})
    .run_commands("python -c \"from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')\"",
                  f"python -c \"from transformers import pipeline; pipeline('text-classification', model='{INJ_MODEL}')\"")
    .pip_install("playwright==1.47.0", "pillow")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/app/ledgerline:/job", "PYTHONUNBUFFERED": "1", "LEDGER_LLM_MODE": "live", "HF_HUB_OFFLINE": "1"})
    .run_commands("python -m venv /opt/deepeval", "/opt/deepeval/bin/pip install -q deepeval==4.3.4 anthropic==2.8.0")
)
# DeepEval's own image and function: the same lines as deploy/argus_modal.py
DE_CONTAINERS, DE_INPUTS = 20, 6
de_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("deepeval==4.3.4", "anthropic==2.8.0")
    .env({"DEEPEVAL_TELEMETRY_OPT_OUT": "YES", "ERROR_REPORTING": "NO", "DEEPEVAL_UPDATE_WARNING_OPT_OUT": "YES", "PYTHONUNBUFFERED": "1"})
)
if LOCAL:
    X6, X7 = L6 / "experiments", L7 / "experiments"
    image = (image.add_local_dir(ROOT / "ledgerline", "/app/ledgerline", ignore=lambda p: not _keep(p))
             .add_local_dir(_base_dir(), "/base/argus")
             .add_local_dir(X6 / "logs", "/logs", ignore=lambda p: not str(p).endswith(".json"))
             .add_local_file(X7 / "argus_c_test.py", "/job/argus_c_test.py")
             .add_local_file(X7 / "argus_record7.py", "/job/argus_record7.py")
             .add_local_file(X6 / "argus_lab.py", "/job/argus_lab.py")
             .add_local_file(X6 / "argus_v3_test.py", "/job/argus_v3_test.py")
             .add_local_file(X6 / "argus_v3_gen.py", "/job/argus_v3_gen.py")
             .add_local_file(X6 / "argus_v3_record.py", "/job/argus_v3_record.py"))
    de_image = de_image.add_local_file(ROOT / ARGUS / "deepeval_runner.py", "/job/deepeval_runner.py")
app = modal.App("l6-argus-v3-bench", image=image)
claude_key = modal.Secret.from_name("forge-anthropic")       # ANTHROPIC_API_KEY, never printed
tr = modal.Secret.from_dict(_tr_env())                        # Langfuse and LangSmith: trace links, and the score on a trace
BIG = dict(timeout=3600, cpu=8, memory=16384)


@app.function(image=de_image, max_containers=DE_CONTAINERS, min_containers=0, scaledown_window=300, cpu=2, memory=2048, timeout=300)
@modal.concurrent(max_inputs=DE_INPUTS)
def deepeval_run(payload: dict) -> dict:
    sys.path.insert(0, "/job")
    import deepeval_runner

    return deepeval_runner.run_subprocess(payload)


def _t():
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_v3_test
    return argus_v3_test


@app.function(secrets=[claude_key], **BIG)
def run_gen() -> dict:
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_v3_gen
    return argus_v3_gen.build()


@app.function(**BIG)
def run_mech() -> dict:                                       # no model key in this container at all
    return _t().mech()


@app.function(secrets=[claude_key, tr], **BIG)
def run_live() -> dict:
    return _t().live()


@app.function(secrets=[claude_key, tr], **BIG)
def run_lab(model: str = "sonnet", guards_on: bool = False) -> dict:
    return _t().lab(model, guards_on)


@app.function(secrets=[claude_key], **BIG)
def run_load(n: int = 30, keep_alive: int = 75) -> dict:
    return _t().load(n, deepeval_run, keep_alive)


@app.function(secrets=[claude_key, tr], **BIG)
def run_shots(url: str = "", only: str = "") -> dict:
    return _t().shots(url, only)


def _write(rel: str, v):
    dst = (SCRATCH / rel[4:]) if rel.startswith("tmp/") else (ROOT / rel[5:]) if rel.startswith("root/") else (L6 / rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(v if isinstance(v, bytes) else json.dumps(v, indent=1, ensure_ascii=False, default=str).encode())
    print("wrote", dst, len(v) if isinstance(v, bytes) else "")


def _spend(what: str, usd: float, calls: int):
    """spend_parts/v3_argus.json: {"what","usd","calls"} summed over this task's runs, with the runs listed."""
    f = L6 / "experiments" / "logs" / "spend_parts" / "v3_argus.json"
    d = json.loads(f.read_text()) if f.exists() else {"what": "Argus v3 teaching views: the bench's tests and screenshots (builder C)",
                                                      "usd": 0.0, "calls": 0, "runs": []}
    d["runs"].append({"run": what, "usd": round(usd, 4), "calls": calls})
    d["usd"] = round(sum(r["usd"] for r in d["runs"]), 4)
    d["calls"] = sum(r["calls"] for r in d["runs"])
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d, indent=1))
    print(f"spend: this run US${usd:.4f} ({calls} model calls); this task so far US${d['usd']:.4f}")


PARTS = ("mech", "live", "lab", "lab_on", "load")


def _summary(log: dict) -> str:
    out = ["Argus v3 (Lecture 6 teaching views): builder C's tests, in a Modal container, not the deployed app.",
           "Written by experiments/argus_v3_modal.py.", ""]
    for part in PARTS:
        r = log.get(part)
        if not r:
            out.append(f"[{part}] not run yet")
            continue
        out.append(f"[{part}] {r.get('at', '')}  {r.get('title', '')}")
        for c in r.get("checks", []):
            out.append(("  PASS  " if c["ok"] else "  FAIL  ") + c["check"] + ("" if c["ok"] else "   <- " + str(c.get("detail", ""))[:500]))
        if "passed" in r:
            out.append(f"  {r['passed']} of {r['of']} checks passed")
        for line in r.get("lines", []):
            out.append("  " + line)
        out.append("")
    return "\n".join(out) + "\n"


@app.local_entrypoint()
def gen():
    r = run_gen.remote()
    _write("root/" + ARGUS + "/teach.json", r["teach"])
    _write("experiments/logs/argus_v3_gen.json", {"at": r["teach"]["at"], "notes": r["notes"], "usd": r["usd"], "calls": r["calls"],
                                                  "turns": [{"id": t["id"], "cards": [(c["kind"], c["pass"], c["why"]) for c in t["view"]["cards"]]}
                                                            for t in r["teach"]["turns"]]})
    _spend("gen (the four recorded judge verdicts)", r["usd"], r["calls"])
    for t in r["teach"]["turns"]:
        print(t["id"], [(c["kind"], c["pass"]) for c in t["view"]["cards"]])
    print(json.dumps(r["notes"], indent=1, default=str)[:2500])


@app.local_entrypoint()
def test(what: str = "mech", n: int = 30, lab_model: str = "sonnet", keep_alive: int = 75):
    f = L6 / "experiments" / "logs" / "argus_v3_test.json"
    log = json.loads(f.read_text()) if f.exists() else {}
    for part in what.split(","):
        fn = {"mech": run_mech, "live": run_live, "lab": run_lab, "lab_on": run_lab, "load": run_load}[part]
        r = fn.remote(*([lab_model, part == "lab_on"] if part.startswith("lab") else [n, keep_alive] if part == "load" else []))
        for k, v in (r.pop("files", None) or {}).items():
            _write(k, v)
        if part == "load":                       # every load run is kept, newest last
            log.setdefault("load_runs", []).append({k: r.get(k) for k in ("at", "n", "bench_server_keep_alive_s", "students_ok", "wall_seconds",
                                                                         "timing", "geval_retries", "geval_no_result", "usd")} |
                                                   {"errors": sorted({e for x in r.get("rows", []) for e in x["errors"]})})
        log[part] = r
        if r.get("usd") and part != "mech":
            _spend(part, r["usd"], r.get("calls", 0))
        print(f"{part}: {r.get('passed')} of {r.get('of')} checks passed")
        for c in r.get("checks", []):
            if not c["ok"]:
                print("  FAIL", c["check"], "·", str(c.get("detail", ""))[:400])
        for line in r.get("lines", []):
            print(" ", line)
    _write("experiments/logs/argus_v3_test.json", log)
    (L6 / "experiments" / "logs" / "argus_v3_test.txt").write_text(_summary(log))


@app.local_entrypoint()
def record(url: str = "", only: str = ""):
    """only: "" (all), or names separated by commas: turn, judge, deepeval, convo, trace."""
    r = run_shots.remote(url, only)
    for k, v in (r.pop("files", None) or {}).items():
        if k.startswith("figs/argus/") and (L6 / k).exists() and pathlib.Path(k).name in EXISTING:
            print("kept the existing picture, not overwritten:", k)
            continue
        _write(k, v)
    if r.get("usd") is not None:
        _spend("screenshots (in-container app)" if not url else "screenshots (deployed app, the student's spend there)", r["usd"], r.get("calls") or 0)
    f = L6 / "experiments" / "logs" / "argus_v3_record.json"
    old = json.loads(f.read_text()) if f.exists() else {"runs": []}
    old["runs"].append(r)
    _write("experiments/logs/argus_v3_record.json", old)
    print(json.dumps({k: v for k, v in r.items() if k != "steps"}, indent=1, default=str)[:4000])


# the Lecture 6 pictures that were in figs/argus before v3: never overwritten by this bench
EXISTING = {"conversations_running.png", "conversations_v2.png", "evals_running.png", "evals_task.png", "evals_thursday.png",
            "guards_a03_code.png", "guards_a03_none.png", "guards_a11_all.png", "join.png", "prompt_diff.png", "traces_good.png",
            "traces_span.png", "traces_thursday.png", "traces_v2.png", "wall.png"}
