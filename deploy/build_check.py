"""Dry run of the deployment: build deploy/Dockerfile on Modal and run deploy/smoke.py inside the built image.
No web endpoint is created and nothing stays running.

    /Users/raj/.venv/bin/modal run deploy/build_check.py

Writes lectures/L7-the-night-shift/experiments/logs/deploy_smoke.json (the checks and whether each passed).
"""
import json
import pathlib

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
image = modal.Image.from_dockerfile(ROOT / "deploy" / "Dockerfile", context_dir=ROOT)
app = modal.App("ledgerline-agent-build-check", image=image)


@app.function(timeout=900, cpu=2, memory=2048)
def smoke() -> dict:
    import os
    import subprocess
    import sys

    env = {**os.environ, "LEDGER_ENV": "dev", "LEDGER_TEMPORAL": "time_skipping", "LEDGER_ADMIN_TOKEN": "build-check",
           "SMOKE_LOG": "/tmp/smoke.json", "PYTHONPATH": "/app"}
    p = subprocess.run([sys.executable, "/app/deploy/smoke.py"], cwd="/app", env=env, capture_output=True, text=True,
                       timeout=600)
    checks = json.load(open("/tmp/smoke.json")) if os.path.exists("/tmp/smoke.json") else []
    import temporalio
    import fastapi

    return {"returncode": p.returncode, "stdout": p.stdout[-6000:], "stderr": p.stderr[-4000:], "checks": checks,
            "python": sys.version.split()[0], "temporalio": temporalio.__version__, "fastapi": fastapi.__version__}


@app.local_entrypoint()
def main():
    r = smoke.remote()
    out = ROOT / "lectures" / "L7-the-night-shift" / "experiments" / "logs" / "deploy_smoke.json"
    out.write_text(json.dumps(r, indent=1))
    print(r["stdout"])
    print(r["stderr"][-1500:])
    print(f"{sum(c['ok'] for c in r['checks'])}/{len(r['checks'])} checks passed · image python {r['python']}, "
          f"temporalio {r['temporalio']} -> {out.relative_to(ROOT)}")
    if r["returncode"]:
        raise SystemExit(1)
