"""Which versions of the industry tools exist today (run on Modal; prints PyPI / npm versions, no keys).

    tools/mrun.sh lectures/L10-observability-evals/experiments/probe_versions.py
"""
import json
import pathlib
import subprocess

import modal

app = modal.App("l10-probe-versions", image=modal.Image.debian_slim(python_version="3.11")
                .apt_install("curl").run_commands("curl -fsSL https://deb.nodesource.com/setup_22.x | bash -",
                                                  "apt-get install -y nodejs"))
PY = ["langfuse", "arize-phoenix", "arize-phoenix-otel", "openinference-instrumentation-openai", "deepeval", "ragas",
      "opentelemetry-sdk", "opentelemetry-api", "opentelemetry-exporter-otlp-proto-http",
      "opentelemetry-semantic-conventions", "langsmith", "braintrust", "ddtrace", "openai", "langchain-openai",
      "langchain-community", "pytest", "fastembed", "playwright"]


@app.function(timeout=600)
def probe() -> dict:
    out = {}
    for p in PY:
        r = subprocess.run(["pip", "index", "versions", p], capture_output=True, text=True)
        out[p] = (r.stdout.splitlines() or [r.stderr[-200:]])[0]
    for n in ["promptfoo"]:
        r = subprocess.run(["npm", "view", n, "version", "time.modified"], capture_output=True, text=True)
        out["npm:" + n] = r.stdout.strip()
    r = subprocess.run(["node", "--version"], capture_output=True, text=True)
    out["node"] = r.stdout.strip()
    return out


@app.local_entrypoint()
def main():
    res = probe.remote()
    p = pathlib.Path(__file__).parent / "logs" / "versions_probe.json"
    p.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
