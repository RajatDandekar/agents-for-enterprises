"""Run the CI suite (ci/test_ask_rasoi.py) twice on Modal: the production prompt, then the deliberately broken one.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/ci_run.py

Exactly what GitHub Actions would run (ci/ask-rasoi-evals.yml): pytest with DeepEval, exit code = the gate.
Writes logs/ci_<prompt>.json (each test: outcome, seconds, message) and the junit XML next to it.
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).parent
CI = HERE.parent / "ci"
out = {}
SUF = "_replay" if os.environ.get("BAHI_LLM_MODE") == "replay" else ""
for prompt in sys.argv[1:] or ["production", "broken"]:
    xmlp = HERE / "logs" / f"ci_{prompt}{SUF}.xml"
    t0 = time.perf_counter()
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_ask_rasoi.py",
                        f"--junitxml={xmlp}"], cwd=CI, capture_output=True, text=True,
                       env={**os.environ, "ASK_RASOI_PROMPT": prompt})
    tests = []
    for tc in ET.parse(xmlp).getroot().iter("testcase"):
        f = tc.find("failure") if tc.find("failure") is not None else tc.find("error")
        sk = tc.find("skipped")
        outcome = "failed" if f is not None else ("xfail" if sk is not None and "xfail" in (sk.get("type") or "") + (sk.get("message") or "").lower() else "skipped" if sk is not None else "passed")
        tests.append({"name": tc.get("name"), "seconds": float(tc.get("time") or 0),
                      "outcome": outcome,
                      "message": (f.get("message") or "")[:600] if f is not None else ((sk.get("message") or "")[:300] if sk is not None else "")})
    res = {"prompt": prompt, "exit_code": p.returncode, "gate": "merge allowed" if p.returncode == 0 else "merge blocked",
           "passed": sum(t["outcome"] == "passed" for t in tests), "failed": sum(t["outcome"] == "failed" for t in tests),
           "xfail": sum(t["outcome"] == "xfail" for t in tests),
           "wall_s": round(time.perf_counter() - t0, 1), "tests": tests, "stdout_tail": p.stdout[-6000:],
           "stderr_tail": p.stderr[-2000:], "mode": os.environ.get("BAHI_LLM_MODE")}
    (HERE / "logs" / f"ci_{prompt}{SUF}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    out[prompt] = {k: res[k] for k in ("exit_code", "gate", "passed", "failed", "wall_s")}
    print(prompt, out[prompt])
    print(p.stdout[-3000:])
