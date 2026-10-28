"""Release dates of the candidate pins (PyPI JSON + npm), on Modal. No keys."""
import json, pathlib, modal
app = modal.App("l10-probe-dates", image=modal.Image.debian_slim(python_version="3.11").pip_install("httpx"))
PK = ["langfuse", "arize-phoenix", "arize-phoenix-otel", "deepeval", "ragas", "opentelemetry-sdk",
      "opentelemetry-exporter-otlp-proto-http", "langchain-openai", "openinference-instrumentation-openai", "openai"]
@app.function(timeout=300)
def probe():
    import httpx
    out = {}
    for p in PK:
        d = httpx.get(f"https://pypi.org/pypi/{p}/json", timeout=30).json()
        rel = [(v, f[0]["upload_time"][:10]) for v, f in d["releases"].items() if f]
        rel.sort(key=lambda x: x[1])
        out[p] = rel[-8:]
    d = httpx.get("https://registry.npmjs.org/promptfoo", timeout=30).json()
    t = sorted(((v, s[:10]) for v, s in d["time"].items() if v[0].isdigit()), key=lambda x: x[1])
    out["npm:promptfoo"] = t[-8:]
    return out
@app.local_entrypoint()
def main():
    r = probe.remote()
    (pathlib.Path(__file__).parent / "logs" / "versions_dates.json").write_text(json.dumps(r, indent=1))
    for k, v in r.items(): print(k, v)
