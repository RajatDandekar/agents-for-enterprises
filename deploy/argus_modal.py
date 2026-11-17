"""Argus on Modal (Lecture 6, Observability and Evals): app `northbridge-argus`, workspace rajatworkspace.

    /Users/raj/.venv/bin/modal deploy deploy/argus_modal.py                          # deploy (or update) the live app
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd status         # spend, students, flags
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd warm           # keep the web container on (class)
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd cool           # let it sleep (after class)
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd pause --reason "back in 5 minutes"
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd resume
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd cap --cap 80             # the class's US$ a day
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd student-cap --cap 3      # each student's US$ a day
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd purge-tests    # remove Probe/Load/Test/Shot labs
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd purge-all      # empty the wall before class
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::test                       # the API test on the live URL
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::load --n 30                # 30 students at once
    /Users/raj/.venv/bin/modal run deploy/argus_modal.py::record                     # screenshots of every station

One CPU web container (max_containers=1, @modal.concurrent): every student's lab lives in its memory; names, chats, eval
runs and attack results are also in the modal.Dict `northbridge-argus-state`. The agent is Lecture 5's Ask Northbridge on
claude-sonnet-5-5; the judge Claude Haiku. Keys: ANTHROPIC_API_KEY from the Modal secret `forge-anthropic`; the admin token
from `rasoi-experience`; the tracing keys (Langfuse; LangSmith and Sentry when present) from the course .env, sent as a
Modal secret at deploy time (never in the image, never printed). Redeploy after adding a key with tools/add_tracing_keys.sh. min_containers is 0, so a deploy never leaves a container running; `admin --cmd warm` keeps one on for
class, and a daily cron (04:00 UTC) sets it back to 0. Do not redeploy during class.
"""
import json
import os
import pathlib
import sys
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = "northbridge-argus"
URL = "https://rajatworkspace--northbridge-argus.us-east.modal.run"
L6 = ROOT / "lectures" / "L6-evals-guardrails-observability"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules", "cassettes", "legacy_ui", "tests_logs",
        "brainlab", "raglab", "wiki", "hephaestus", "daedalus"}
LF_KEYS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL", "LANGFUSE_HOST",
           "LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT", "SENTRY_DSN", "SENTRY_ORG")   # each optional
INJ_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"


def _keep(p) -> bool:
    s = str(p)
    if any(x in SKIP for x in pathlib.Path(p).parts):
        return False
    if s.endswith((".env", ".png", ".mp4", ".ipynb", ".webm", ".jpg")):
        return False
    if s.endswith(".jsonl") and "/docs/_index/" not in s:
        return False
    return True


def _lf_env():
    env = {}
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in LF_KEYS:
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


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
    .env({"PYTHONPATH": "/app/ledgerline", "PYTHONUNBUFFERED": "1", "ARGUS_DICT": "northbridge-argus-state", "ARGUS_APP": APP,
          "ARGUS_URL": URL, "LEDGER_LLM_MODE": "live", "HF_HUB_OFFLINE": "1"})
    .add_local_dir(ROOT / "ledgerline", "/app/ledgerline", ignore=lambda p: not _keep(p))
)
app = modal.App(APP, image=image)
secret = modal.Secret.from_name("rasoi-experience")          # NORTHBRIDGE_ADMIN_TOKEN
claude_key = modal.Secret.from_name("forge-anthropic")       # ANTHROPIC_API_KEY, never printed
lf = modal.Secret.from_dict(_lf_env())                        # Langfuse keys, from the course .env
outvol = modal.Volume.from_name("northbridge-argus-out", create_if_missing=True)


@app.function(secrets=[secret, claude_key, lf], max_containers=1, min_containers=0, scaledown_window=1800, cpu=8,
              memory=16384, timeout=900)
@modal.concurrent(max_inputs=500)
@modal.asgi_app(label="northbridge-argus")
def web():
    sys.path.insert(0, "/app/ledgerline")
    for k in ("OPENROUTER_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        os.environ.pop(k, None)
    from ledgerline.argus.app import create_app

    return create_app()


@app.function(schedule=modal.Cron("0 4 * * *"), timeout=120)  # every day 04:00 UTC: the web container may sleep
def class_cool():
    modal.Function.from_name(APP, "web").update_autoscaler(min_containers=0)
    print("web min_containers -> 0")


# ---------------------------------------------------------------------------------------------------- operator
@app.function(secrets=[secret], timeout=300, image=modal.Image.debian_slim(python_version="3.11").pip_install("httpx"))
def op(cmd: str, reason: str = "", cap: float = 0) -> dict:
    import httpx

    h = {"X-Admin-Token": os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ["RASOI_ADMIN_TOKEN"]}
    c = httpx.Client(base_url=URL, timeout=240)
    if cmd == "warm":
        modal.Function.from_name(APP, "web").update_autoscaler(min_containers=1)
        for _ in range(20):
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
    elif cmd in ("guards-on", "guards-off"):   # the Guards station (the guardrails lecture); off by default
        c.post("/api/admin/flags", json={"guards_station": cmd == "guards-on"}, headers=h).raise_for_status()
    elif cmd == "sonnet":
        c.post("/api/admin/flags", json={"model": "anthropic:claude-sonnet-5-5"}, headers=h).raise_for_status()
    elif cmd == "purge-tests":
        print(c.post("/api/admin/purge", json={"prefixes": ["Probe ", "Load ", "Test ", "Shot ", "Rec "]}, headers=h).json())
    elif cmd == "purge-all":
        print(c.post("/api/admin/purge", json={"all": True}, headers=h).json())
    s = c.get("/api/admin/status", headers=h)
    s.raise_for_status()
    out = s.json()
    out["no_token_status"] = c.get("/api/admin/status").status_code
    return out


@app.local_entrypoint()
def admin(cmd: str = "status", reason: str = "", cap: float = 0):
    print(json.dumps(op.remote(cmd, reason, cap), indent=1, ensure_ascii=False))


# ---------------------------------------------------------------------------------------------------- client jobs
client_image = (modal.Image.debian_slim(python_version="3.11").pip_install("httpx")
                .add_local_file(L6 / "experiments" / "argus_lab.py", "/job/argus_lab.py"))


@app.function(image=client_image, secrets=[secret], timeout=3600)
def api_test() -> dict:
    sys.path.insert(0, "/job")
    import argus_lab

    return argus_lab.api_test(URL, {"X-Admin-Token": os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN", "")})


@app.local_entrypoint()
def test():
    r = api_test.remote()
    for x in r["checks"]:
        print(("PASS " if x["ok"] else "FAIL ") + x["check"] + ("" if x["ok"] else "  · " + x["detail"]))
    print(f"{r['passed']} / {r['of']}")
    (L6 / "experiments" / "logs").mkdir(parents=True, exist_ok=True)
    (L6 / "experiments" / "logs" / "argus_api_test.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))


@app.function(image=client_image, secrets=[secret], timeout=3600)
def load_run(n: int = 30) -> dict:
    sys.path.insert(0, "/job")
    import argus_lab

    return argus_lab.load(URL, n, {"X-Admin-Token": os.environ.get("NORTHBRIDGE_ADMIN_TOKEN") or os.environ.get("RASOI_ADMIN_TOKEN", "")})


@app.local_entrypoint()
def load(n: int = 30):
    r = load_run.remote(n)
    dst = L6 / "experiments" / "logs" / f"argus_load_{n}.json"
    dst.write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=1))


pw_image = (modal.Image.debian_slim(python_version="3.11")
            .pip_install("playwright==1.47.0", "httpx").run_commands("playwright install --with-deps chromium")
            .add_local_file(L6 / "experiments" / "argus_record.py", "/job/argus_record.py"))


@app.function(image=pw_image, timeout=3000, cpu=4, memory=8192)
def record_one(which: str) -> dict:
    sys.path.insert(0, "/job")
    import argus_record

    return argus_record.record(which, URL)


@app.local_entrypoint()
def record(which: str = "shots"):
    for name in which.split(","):
        r = record_one.remote(name)
        for k, v in r.items():
            dst = L6 / k
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(v if isinstance(v, bytes) else json.dumps(v, indent=1).encode())
            print("wrote", dst, len(v))
