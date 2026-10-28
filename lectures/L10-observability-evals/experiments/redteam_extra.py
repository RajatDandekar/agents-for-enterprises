"""Lecture 10, red-team part 2 (after redteam_run.py): two more runs, merged into logs/redteam.json.

    tools/mrun.sh lectures/L10-observability-evals/experiments/l10_modal.py --script lectures/L10-observability-evals/experiments/redteam_extra.py

1. lite + trust layer: the same 38 hand-written attacks against flash-lite behind the L7 trust layer. Lite without the
   trust layer broke twice (both NE3); does the trust layer stop those two?
2. promptfoo's generated attacks (redteam/generated.yaml, written by `promptfoo redteam generate` with OpenRouter):
   the 12 that need no promptfoo cloud (basic and base64; the jailbreak:meta ones need promptfoo's remote generation,
   which we keep switched off), against flash and lite without the trust layer. Graded twice: promptfoo's own LLM
   grader (openrouter:google/gemini-3.8-flash, its rubric per plugin) and our check on Bahi's tables.
"""
import json
import os
import pathlib
import subprocess
import time

import yaml

from bahi.course.obs.redteam import CASES

HERE = pathlib.Path(__file__).parent
RT = HERE.parent / "redteam"
env = {**os.environ, "PROMPTFOO_PYTHON": "python", "PROMPTFOO_DISABLE_TELEMETRY": "1", "PROMPTFOO_DISABLE_UPDATE": "1",
       "PROMPTFOO_CACHE_ENABLED": "false", "PROMPTFOO_DISABLE_REMOTE_GENERATION": "true",
       "PROMPTFOO_PYTHON_TIMEOUT_MS": "600000", "REQUEST_TIMEOUT_MS": "600000"}
LOG = HERE / "logs" / "redteam.json"
log = json.loads(LOG.read_text())


def parse(path):
    res = json.loads(path.read_text())
    out = []
    for it in res.get("results", {}).get("results", []):
        v = it.get("vars") or {}
        o = (it.get("response") or {}).get("output")
        try:
            r = json.loads(o) if o else {}
        except Exception:  # noqa: BLE001
            r = {}
        comps = (it.get("gradingResult") or {}).get("componentResults") or []
        theirs = [c for c in comps if (c.get("assertion") or {}).get("type") != "python"]
        md = (it.get("testCase") or {}).get("metadata") or it.get("metadata") or {}
        out.append({"target": (it.get("provider") or {}).get("label"), "id": v.get("id") or f"generated.{md.get('pluginId')}",
                    "goal": v.get("goal") or "generated", "strategy": v.get("strategy") or md.get("strategyId") or "basic",
                    "plugin": md.get("pluginId"), "attack": ((it.get("prompt") or {}).get("raw") or "")[:900],
                    "promptfoo_pass": it.get("success"), "error": it.get("error"),
                    "grader_pass": all(c.get("pass") for c in theirs) if theirs else None,
                    "grader_reason": "; ".join((c.get("reason") or "")[:300] for c in theirs),
                    "broken": r.get("broken"), "replies": r.get("replies"), "tools": r.get("tools"),
                    "trust_refusals": r.get("trust_refusals"), "cost_inr": r.get("cost_inr"), "orders": r.get("orders")})
    return out


# ---- 1. lite + trust layer
cfg = yaml.safe_load((RT / "promptfooconfig.yaml").read_text())
cfg["providers"] = [{"id": "file://provider.py", "label": "lite + trust layer",
                     "config": {"trust": True, "tier": "lite", "model": "gemini:gemini-3.5-flash-lite"}}]
(RT / "config_lite_trust.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))
t0 = time.perf_counter()
p = subprocess.run(["promptfoo", "eval", "-c", "config_lite_trust.yaml", "--no-cache", "-j", "6", "-o",
                    "results_lite_trust.json", "--no-progress-bar", "--no-table"], cwd=RT, capture_output=True, text=True,
                   env=env, timeout=3000)
rows_lt = parse(RT / "results_lite_trust.json") if (RT / "results_lite_trust.json").exists() else []
print("lite+trust exit", p.returncode, len(rows_lt), "rows", round(time.perf_counter() - t0), "s")

# ---- 2. promptfoo's generated attacks, without the cloud-only strategy
gen = yaml.safe_load((RT / "generated.yaml").read_text())
keep = [t for t in gen["tests"] if "jailbreak" not in str((t.get("metadata") or {}).get("strategyId") or "")
        and "iterative" not in json.dumps(t.get("provider") or "")]
gen["tests"] = keep
gen["targets"] = [{"id": "file://provider.py", "label": "flash, no trust layer",
                   "config": {"trust": False, "tier": "flash", "model": "gemini:gemini-3.8-flash"}},
                  {"id": "file://provider.py", "label": "lite, no trust layer",
                   "config": {"trust": False, "tier": "lite", "model": "gemini:gemini-3.5-flash-lite"}}]
gen.setdefault("defaultTest", {}).setdefault("options", {})["provider"] = "openrouter:google/gemini-3.8-flash"
for t in gen["tests"]:
    t.setdefault("assert", []).append({"type": "python", "value": "file://assert_rules.py", "metric": "BahiState"})
(RT / "generated_eval.yaml").write_text(yaml.safe_dump(gen, sort_keys=False, allow_unicode=True))
t1 = time.perf_counter()
g = subprocess.run(["promptfoo", "eval", "-c", "generated_eval.yaml", "--no-cache", "-j", "4", "-o",
                    "generated_results.json", "--no-progress-bar", "--no-table"], cwd=RT, capture_output=True, text=True,
                   env=env, timeout=3000)
rows_g = parse(RT / "generated_results.json") if (RT / "generated_results.json").exists() else []
print("generated exit", g.returncode, len(rows_g), "rows")

log["rows"] = [r for r in log["rows"] if r["target"] != "lite + trust layer"] + rows_lt
log["generated"] = {"n_tests_kept": len(keep), "exit": g.returncode, "wall_s": round(time.perf_counter() - t1, 1),
                    "stderr_tail": g.stderr[-2000:], "rows": rows_g,
                    "dropped": "jailbreak:meta tests: they need promptfoo's remote generation, which we keep off"}
from collections import defaultdict  # noqa: E402
summary = defaultdict(lambda: {"n": 0, "broken": 0, "errors": 0})
for r in log["rows"]:
    for key in (("all", r["target"]), ("goal", r["target"], r["goal"]), ("strategy", r["target"], r["strategy"])):
        s = summary["|".join(map(str, key))]
        s["n"] += 1
        if r["broken"] is None:
            s["errors"] += 1
        elif r["broken"]:
            s["broken"] += 1
for s in summary.values():
    done = s["n"] - s["errors"]
    s["asr"] = round(s["broken"] / done, 3) if done else None
log["summary"] = dict(summary)
gs = defaultdict(lambda: {"n": 0, "bahi_broken": 0, "grader_failed": 0, "disagree": 0})
for r in rows_g:
    s = gs[r["target"]]
    s["n"] += 1
    b = bool(r["broken"])
    gf = r["grader_pass"] is False
    s["bahi_broken"] += b
    s["grader_failed"] += gf
    s["disagree"] += (b != gf)
log["generated"]["summary"] = dict(gs)
LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str))
print(json.dumps({k: v for k, v in summary.items() if k.startswith("all")}, indent=1))
print(json.dumps(dict(gs), indent=1))
