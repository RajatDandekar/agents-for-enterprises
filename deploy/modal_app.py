"""The Modal deployment of the Bahi sandbox + agent API. WRITTEN, NOT DEPLOYED.

Deploying creates a public URL. Do it only with the lead's go-ahead, and staging before prod:

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
    out = {}
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
    secrets=[modal.Secret.from_name(f"bahi-{ENV}")],   # GEMINI_API_KEY, BAHI_ADMIN_TOKEN, TEMPORAL_API_KEY, LANGFUSE_*
    volumes={"/var/bahi": flags_volume},               # the kill switch survives restarts and redeploys
    min_containers=1 if ENV == "prod" else 0,          # prod keeps one warm: approvals arrive at any hour
    max_containers=1,                                  # sandbox ERP lives in memory: exactly one copy
    timeout=3600,
)
@modal.concurrent(max_inputs=32)
@modal.asgi_app(label=f"bahi-agent-{ENV}")
def web():
    import sys

    sys.path.insert(0, "/app")
    from deploy.app import app as fastapi_app

    return fastapi_app
