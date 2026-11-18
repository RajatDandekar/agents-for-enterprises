"""Builder C's test bench for Argus, Lecture 7 (the Guards switch in the chat, the station's prompt picker, A00).

Nothing here deploys anything or touches the live app. Argus runs INSIDE one Modal container (uvicorn on 127.0.0.1), built
from the local `ledgerline` folder with the same image recipe as deploy/argus_modal.py, with an in-memory store (ARGUS_DICT
is never set here, so the live app's modal.Dict is not opened) and its own random admin token.

    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::test --what mech   # scripted model: flag off = before, flag on = the new parts
    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::test --what demo   # real model: the opening demo, three times
    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::test --what lab    # real model: Lecture 6's argus_lab.api_test, unchanged
    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::test --what lab_on # the same with the guards flag on (its Guards checks)
                                                             (--lab-model haiku puts the agent on Claude Haiku for lab and lab_on; default sonnet)
    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::record             # screenshots, in-container app
    tools/mrun.sh lectures/L6b-guardrails/experiments/argus_c_modal.py::record --url https://rajatworkspace--northbridge-argus.us-east.modal.run
                                                                                           # screenshots, the deployed app (guards flag must be on)

`mech` compares the changed Argus with the Argus of commit BASE_REV (exported with `git show` at start, mounted beside it as
ledgerline.argus_base) on the same scripted model: every endpoint, flag off, must answer the same; the page must look the
same. Results: experiments/logs/argus_c_test.json (+ .txt), argus_c_record.json, figs/argus/*.png, spend_parts/C_argus.json.
Keys: ANTHROPIC_API_KEY from the Modal secret forge-anthropic; Langfuse keys (for `lab` only) from the course .env, sent as
a Modal secret. Never printed, never written.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import modal

_P = pathlib.Path(__file__).resolve()
LOCAL = modal.is_local()
ROOT = _P.parents[3] if LOCAL else pathlib.Path("/course")
L7 = ROOT / "lectures" / "L6b-guardrails"
L6 = ROOT / "lectures" / "L6-evals-guardrails-observability"
BASE_REV = "0988a27"          # Argus as Lecture 6 uses it (the commit before this change)
ARGUS = "ledgerline/ledgerline/argus"
LIVE_URL = "https://rajatworkspace--northbridge-argus.us-east.modal.run"
SKIP = {"__pycache__", ".ipynb_checkpoints", "shots", "logs", "qa", "node_modules", "cassettes", "legacy_ui", "tests_logs",
        "brainlab", "raglab", "wiki", "hephaestus", "daedalus"}                      # as deploy/argus_modal.py
LF_KEYS = ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL", "LANGFUSE_HOST")
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
    if LOCAL and f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if k.strip() in LF_KEYS:
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


# the same layers, in the same order, as deploy/argus_modal.py (so Modal reuses them), then Playwright; no ARGUS_DICT
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
)
if LOCAL:
    image = (image.add_local_dir(ROOT / "ledgerline", "/app/ledgerline", ignore=lambda p: not _keep(p))
             .add_local_dir(_base_dir(), "/base/argus")
             .add_local_file(_P.parent / "argus_c_test.py", "/job/argus_c_test.py")
             .add_local_file(_P.parent / "argus_record7.py", "/job/argus_record7.py")
             .add_local_file(L6 / "experiments" / "argus_lab.py", "/job/argus_lab.py"))
app = modal.App("l7-argus-c-bench", image=image)
claude_key = modal.Secret.from_name("forge-anthropic")       # ANTHROPIC_API_KEY, never printed
lf = modal.Secret.from_dict(_lf_env())                        # Langfuse keys: argus_lab checks the trace links


@app.function(timeout=3000, cpu=8, memory=16384)
def run_mech() -> dict:                                       # no model key in this container at all
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_c_test
    return argus_c_test.mech()


@app.function(secrets=[claude_key], timeout=3000, cpu=8, memory=16384)
def run_demo(n: int = 3) -> dict:
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_c_test
    return argus_c_test.demo(n)


@app.function(secrets=[claude_key, lf], timeout=3600, cpu=8, memory=16384)
def run_lab(model: str = "sonnet", guards_on: bool = False) -> dict:
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_c_test
    return argus_c_test.lab(model, guards_on)


@app.function(secrets=[claude_key], timeout=3600, cpu=8, memory=16384)
def run_shots(url: str = "", only: str = "") -> dict:
    sys.path[:0] = ["/job", "/app/ledgerline"]
    import argus_c_test
    return argus_c_test.shots(url, only)


SCRATCH = pathlib.Path(__import__("os").environ.get("ARGUS_C_SCRATCH") or tempfile.gettempdir()) / "argus_c"


def _write(rel: str, v):
    dst = (SCRATCH / rel[4:]) if rel.startswith("tmp/") else (L7 / rel)      # tmp/: working pictures, not the lecture's
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(v if isinstance(v, bytes) else json.dumps(v, indent=1, ensure_ascii=False, default=str).encode())
    print("wrote", dst, len(v) if isinstance(v, bytes) else "")


def _spend(what: str, usd: float, calls: int):
    """spend_parts/C_argus.json: {"what","usd","calls"} summed over this builder's runs, with the runs listed."""
    f = L7 / "experiments" / "logs" / "spend_parts" / "C_argus.json"
    d = json.loads(f.read_text()) if f.exists() else {"what": "Argus for Lecture 7: in-container tests and screenshots (builder C)",
                                                      "usd": 0.0, "calls": 0, "runs": []}
    d["runs"].append({"run": what, "usd": round(usd, 4), "calls": calls})
    d["usd"] = round(sum(r["usd"] for r in d["runs"]), 4)
    d["calls"] = sum(r["calls"] for r in d["runs"])
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d, indent=1))
    print(f"spend: this run US${usd:.4f} ({calls} model calls); builder C so far US${d['usd']:.4f}")


def _summary(log: dict) -> str:
    out = ["Argus for Lecture 7: builder C's tests (in-container app, not deployed). Written by experiments/argus_c_modal.py.", ""]
    for part in ("mech", "demo", "lab", "lab_on"):
        r = log.get(part)
        if not r:
            out.append(f"[{part}] not run yet")
            continue
        out.append(f"[{part}] {r.get('at', '')}  {r.get('title', '')}")
        for c in r.get("checks", []):
            out.append(("  PASS  " if c["ok"] else "  FAIL  ") + c["check"] + ("" if c["ok"] else "   <- " + str(c.get("detail", ""))[:400]))
        if "passed" in r:
            out.append(f"  {r['passed']} of {r['of']} checks passed")
        for line in r.get("lines", []):
            out.append("  " + line)
        out.append("")
    return "\n".join(out) + "\n"


@app.local_entrypoint()
def test(what: str = "mech", n: int = 3, lab_model: str = "sonnet"):
    f = L7 / "experiments" / "logs" / "argus_c_test.json"
    log = json.loads(f.read_text()) if f.exists() else {}
    for part in what.split(","):
        r = {"mech": run_mech, "demo": run_demo, "lab": run_lab, "lab_on": run_lab}[part].remote(
            *([n] if part == "demo" else [lab_model, part == "lab_on"] if part.startswith("lab") else []))
        for k, v in (r.pop("files", None) or {}).items():
            _write(k, v)
        log[part] = r
        if r.get("usd") is not None and part != "mech":
            _spend(part, r["usd"], r.get("calls", 0))
        print(f"{part}: {r.get('passed')} of {r.get('of')} checks passed")
        for c in r.get("checks", []):
            if not c["ok"]:
                print("  FAIL", c["check"], "·", str(c.get("detail", ""))[:300])
        for line in r.get("lines", []):
            print(" ", line)
    _write("experiments/logs/argus_c_test.json", log)
    (L7 / "experiments" / "logs" / "argus_c_test.txt").write_text(_summary(log))


@app.local_entrypoint()
def record(url: str = "", only: str = ""):
    """only: "" (all six pictures), "chat" or "station"."""
    r = run_shots.remote(url, only)
    for k, v in (r.pop("files", None) or {}).items():
        _write(k, v)
    f = L7 / "experiments" / "logs" / "argus_c_record.json"
    if only and f.exists():                       # a partial retake: keep what the earlier run recorded for the other half
        old = json.loads(f.read_text())
        r = {**{k: v for k, v in old.items() if k not in r}, **r, "earlier_run": {k: old.get(k) for k in ("at", "usd", "calls", "steps")}}
    if r.get("usd") is not None:
        _spend("screenshots (in-container app)" if not url else "screenshots (deployed app, the student's spend there)", r["usd"], r.get("calls") or 0)
    _write("experiments/logs/argus_c_record.json", r)
    print(json.dumps({k: v for k, v in r.items() if k != "steps"}, indent=1, default=str)[:3000])
