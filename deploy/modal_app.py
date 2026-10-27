"""The Modal deployment of the Bahi reference app (L5 app + L7 workflow and controls).

Staging is deployed (approved by the lead, 2026-10-27): https://rajatworkspace--bahi-agent-staging.us-east.modal.run
Prod is not. Deploying creates a public URL; do it only with the lead's go-ahead, staging before prod:

    BAHI_ENV=staging /Users/raj/.venv/bin/modal deploy deploy/modal_app.py      # needs the secret "bahi-staging"
    BAHI_ENV=prod    /Users/raj/.venv/bin/modal deploy deploy/modal_app.py      # needs the secret "bahi-prod"

The dry run that IS allowed builds this same image from deploy/Dockerfile on Modal and runs the smoke test
inside it, with no web endpoint:      /Users/raj/.venv/bin/modal run deploy/build_check.py

Environments differ only in deploy/env/<env>.env (plain settings) and the secret bahi-<env> (keys). The image is
the same bytes in every environment, so what passed in staging is what runs in prod.
"""
import os
import pathlib

import modal

ENV = os.environ.get("BAHI_ENV", "dev")
if ENV not in ("dev", "staging", "prod"):
    raise SystemExit(f"BAHI_ENV must be dev, staging or prod, not {ENV!r}")
ROOT = pathlib.Path(__file__).resolve().parents[1]


def env_file(env: str) -> dict:
    """Read deploy/env/<env>.env on the laptop at deploy time. Inside the container Modal re-imports this file from
    /root, where the env file does not exist; the values are already baked into the image there."""
    out = {}
    if not modal.is_local():
        return out
    for line in (ROOT / "deploy" / "env" / f"{env}.env").read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            if v.strip():
                out[k.strip()] = v.strip()
    return out


image = modal.Image.from_dockerfile(ROOT / "deploy" / "Dockerfile", context_dir=ROOT).env(env_file(ENV))
app = modal.App(f"bahi-agent-{ENV}", image=image)
flags_volume = modal.Volume.from_name(f"bahi-{ENV}-flags", create_if_missing=True)


@app.function(
    secrets=[modal.Secret.from_name(f"bahi-{ENV}")],   # GEMINI_API_KEY, BAHI_ADMIN_TOKEN, OPENROUTER_*, LANGFUSE_*
    volumes={"/var/bahi": flags_volume},               # kill switches and the spend ledger survive restarts
    min_containers=1 if ENV == "prod" else 0,          # prod keeps one warm: approvals arrive at any hour
    max_containers=1,                                  # sandbox ERP and Temporal live in memory: exactly one copy
    scaledown_window=1200,                             # staging: stops after 20 idle minutes (and the sandbox resets)
    cpu=2, memory=4096, timeout=3600,
)
@modal.concurrent(max_inputs=32)
@modal.asgi_app(label=f"bahi-agent-{ENV}")
def web():
    import sys
    import threading
    import time

    sys.path.insert(0, "/app")
    from deploy.app import app as fastapi_app

    def keep():  # flags and spend are files on the volume; commit them so a new container sees the same switch
        while True:
            time.sleep(15)
            try:
                flags_volume.commit()
            except Exception:  # noqa: BLE001
                pass
    threading.Thread(target=keep, daemon=True).start()
    return fastapi_app
