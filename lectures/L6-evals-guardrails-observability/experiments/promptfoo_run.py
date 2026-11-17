"""promptfoo, run for real on the node image (Node 22, promptfoo 0.125.1), then screenshots of what it produced.

    tools/mrun.sh .../l6_modal.py --script promptfoo_run.py --image node --args "--part eval"
    tools/mrun.sh .../l6_modal.py --script promptfoo_run.py --image node --args "--part redteam"

eval:    promptfoo eval on promptfoo/promptfooconfig.yaml (good vs Thursday prompt, 5 messages), outputs results.json and
         results.html; then `promptfoo view` is started and its matrix screenshotted (and the HTML report, too).
redteam: promptfoo redteam run on promptfoo/redteam.yaml with remote generation disabled and Claude Haiku generating and
         grading the attacks; targets: Ask Northbridge with no guards, and with all guards. Then the report screenshotted.
Telemetry off (PROMPTFOO_DISABLE_TELEMETRY=1). Terminal output kept in logs/promptfoo_<part>.txt.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import time

from _common import FIGS, LOGS, now, spend, write

ap = argparse.ArgumentParser()
ap.add_argument("--part", default="eval")
a = ap.parse_args()
PF = pathlib.Path(__file__).parent / "promptfoo"
env = {**os.environ, "PROMPTFOO_DISABLE_TELEMETRY": "1", "PROMPTFOO_DISABLE_UPDATE": "1", "LEDGERLINE_PATH": "/course/ledgerline",
       "PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "true", "PROMPTFOO_DISABLE_SHARING": "1", "PROMPTFOO_SELF_HOSTED": "1",
       "PROMPTFOO_PYTHON": "python", "PROMPTFOO_CONFIG_DIR": "/tmp/pfhome", "PROMPTFOO_DISABLE_REMOTE_GENERATION": "true",
       "PROMPTFOO_EVAL_TIMEOUT_MS": "300000", "FORCE_COLOR": "0"}
D = FIGS / "promptfoo"
D.mkdir(parents=True, exist_ok=True)


def sh(cmd, timeout=3000):
    t0 = time.time()
    p = subprocess.run(cmd, shell=True, cwd=PF, env=env, capture_output=True, text=True, timeout=timeout)
    return {"cmd": cmd, "code": p.returncode, "seconds": round(time.time() - t0, 1), "out": p.stdout[-20000:], "err": p.stderr[-6000:]}


def shots(pairs):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2, color_scheme="light").new_page()
        for url, name, extra in pairs:
            try:
                pg.goto(url, wait_until="networkidle", timeout=90000)
                pg.wait_for_timeout(5000)
                if extra:
                    extra(pg)
                pg.screenshot(path=str(D / f"{name}.png"))
                (LOGS / f"_pf_{name}.txt").write_text(pg.inner_text("body")[:4000])
                print("shot", name)
            except Exception as e:  # noqa: BLE001
                print("shot failed", name, repr(e)[:300])
        b.close()


rec = {"at": now(), "part": a.part}
rec["version"] = sh("promptfoo --version")["out"].strip()
if a.part == "eval":
    r = sh("promptfoo eval -c promptfooconfig.yaml -o results.json -o results.html --no-cache --max-concurrency 5")
    (LOGS / "promptfoo_eval.txt").write_text(r["out"] + "\n--- stderr ---\n" + r["err"])
    rec["eval"] = {k: r[k] for k in ("cmd", "code", "seconds")}
    res = json.loads((PF / "results.json").read_text()) if (PF / "results.json").exists() else {}
    rows = (res.get("results") or {}).get("results") or []
    cells = []
    for x in rows:
        cells.append({"prompt": (x.get("prompt") or {}).get("label"), "test": (x.get("testCase") or {}).get("description"),
                      "pass": x.get("success"), "score": x.get("score"), "cost": x.get("cost"),
                      "asserts": [{"metric": (g.get("assertion") or {}).get("metric"), "type": (g.get("assertion") or {}).get("type"),
                                   "pass": g.get("pass"), "reason": (g.get("reason") or "")[:300]}
                                  for g in ((x.get("gradingResult") or {}).get("componentResults") or [])],
                      "output": ((x.get("response") or {}).get("output") or "")[:1500]})
    rec["cells"] = cells
    rec["stats"] = (res.get("results") or {}).get("stats")
    usd = sum(c["cost"] or 0 for c in cells)
    spend("promptfoo_eval", usd, len(cells), 0, 0, "claude-sonnet-5-5 (+ haiku grader, not counted)", "promptfoo eval cells")
    shutil.copy(PF / "results.html", D / "results.html") if (PF / "results.html").exists() else None
    srv = subprocess.Popen("promptfoo view --port 15500 --no", shell=True, cwd=PF, env=env, stdout=open("/tmp/pfv.log", "w"),
                           stderr=subprocess.STDOUT)
    time.sleep(12)
    shots([("http://127.0.0.1:15500/eval", "pf_view", None),
           ("file://" + str(PF / "results.html"), "pf_html", None)])
    srv.terminate()
    rec["view_log"] = open("/tmp/pfv.log").read()[-1500:]
elif a.part == "redteam":
    r = sh("promptfoo redteam run -c redteam.yaml -o redteam_tests.yaml --force --max-concurrency 4 --no-cache", timeout=6000)
    (LOGS / "promptfoo_redteam.txt").write_text(r["out"] + "\n--- stderr ---\n" + r["err"])
    rec["run"] = {k: r[k] for k in ("cmd", "code", "seconds")}
    gen = (PF / "redteam_tests.yaml").read_text() if (PF / "redteam_tests.yaml").exists() else ""
    rec["generated_tests_yaml_chars"] = len(gen)
    (LOGS / "promptfoo_redteam_tests.yaml").write_text(gen[:200000])
    ex = sh("promptfoo export eval latest -o /tmp/rt.json")
    res = json.loads(open("/tmp/rt.json").read()) if os.path.exists("/tmp/rt.json") else {}
    rows = ((res.get("results") or {}).get("results")) or []
    cells = []
    for x in rows:
        md = ((x.get("testCase") or {}).get("metadata") or {})
        cells.append({"target": (x.get("provider") or {}).get("label") or (x.get("provider") or {}).get("id"),
                      "plugin": md.get("pluginId"), "strategy": md.get("strategyId") or "basic", "pass": x.get("success"),
                      "attack": str(((x.get("testCase") or {}).get("vars") or {}).get("message", ""))[:400],
                      "output": ((x.get("response") or {}).get("output") or "")[:800], "cost": x.get("cost"),
                      "reason": ((x.get("gradingResult") or {}).get("reason") or "")[:300]})
    rec["cells"] = cells
    by = {}
    for c_ in cells:
        d = by.setdefault(c_["target"], {"tests": 0, "attack_succeeded": 0, "errors": 0})
        if not c_["output"]:
            d["errors"] += 1
            continue
        d["tests"] += 1
        d["attack_succeeded"] += int(c_["pass"] is False)
    for d in by.values():
        d["asr"] = round(d["attack_succeeded"] / max(1, d["tests"]), 3)
    rec["by_target"] = by
    usd = sum(c_["cost"] or 0 for c_ in cells)
    spend("promptfoo_redteam", usd, len(cells), 0, 0, "claude-sonnet-5-5 target (+ haiku generator/grader, not counted)", "redteam cells")
    srv = subprocess.Popen("promptfoo view --port 15500 --no", shell=True, cwd=PF, env=env, stdout=open("/tmp/pfv.log", "w"),
                           stderr=subprocess.STDOUT)
    time.sleep(12)
    shots([("http://127.0.0.1:15500/report", "pf_redteam_report", None), ("http://127.0.0.1:15500/eval", "pf_redteam_eval", None)])
    srv.terminate()
write(f"promptfoo_{a.part}.json", rec)
print(json.dumps({k: v for k, v in rec.items() if k != "cells"}, indent=1)[:3000])
