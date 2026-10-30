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
    .add_local_dir(ROOT / "ledgerline", "/app/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".env", ".png", ".mp4", ".ipynb")))
)
app = modal.App("northbridge-experience", image=image)
secret = modal.Secret.from_name("rasoi-experience")  # secret name kept from v3 (holds the admin token and keys)


@app.function(secrets=[secret], max_containers=1, min_containers=0, scaledown_window=1800, cpu=2, memory=6144,
              timeout=900)
@modal.concurrent(max_inputs=250)
@modal.asgi_app(label="northbridge-experience")
def web():
    sys.path.insert(0, "/app/ledgerline")
    from ledgerline.experience.app import create_app

    return create_app()


@app.function(schedule=modal.Cron("40 1 * * 6,0"), timeout=120)  # 07:10 GMT on Saturday and Sunday
def warm():
    import urllib.request

    for _ in range(3):
        try:
            print(urllib.request.urlopen(URL + "/healthz", timeout=60).read()[:200])
            return
        except Exception as e:  # noqa: BLE001
            print("warm failed:", e)
            time.sleep(10)


@app.function(secrets=[secret], timeout=2400, cpu=2, memory=4096)
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
