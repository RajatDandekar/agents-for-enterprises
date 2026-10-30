"""Do the cassettes replay with no model key, and what did search_policy return in the recorded runs?

Replays EVERY final job (three stacks x runs 1-3, five ablation models x runs 1-3) in LEDGER_LLM_MODE=replay with no
key and no Langfuse, and compares pass/fail and tool calls with the recorded logs. A replay can only follow the
recording if every tool result matches what the model saw when it was recorded (the next request's hash includes it),
so the search_policy results captured here are the ones in the recordings; each is checked against the course's
list of old-world words (tools/world_v4.py OLD_WORDS, whole words). Writes logs/replay_check.json.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py \
        --script lectures/L1-before-and-after/experiments/production/replay_check.py --mode replay
"""
import json
import os
import pathlib
import re

for k in ("OPENROUTER_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"):
    os.environ.pop(k, None)   # prove it: no key at all
os.environ["LEDGER_LLM_MODE"] = "replay"

from ledgerline.course.l1.production import toolserver as TS  # noqa: E402
from ledgerline.course.l1.production.runner import Rig  # noqa: E402

POLICY: list[str] = []
_init = TS.ToolServer.__init__


def _init_capturing(self, *a, **kw):   # keep every search_policy result this replay produces
    _init(self, *a, **kw)
    inner = self.mcp.toolbox.call

    def call(name, args=None):
        out = inner(name, args)
        if name == "search_policy":
            POLICY.append(json.dumps(out, default=str))
        return out
    self.mcp.toolbox.call = call


TS.ToolServer.__init__ = _init_capturing

HERE = pathlib.Path(__file__).parent
rec, jobs = {}, []
for f in sorted((HERE / "logs").glob("stacks_r*.json")) + sorted((HERE / "logs").glob("ablation_*.json")):
    for r in json.loads(f.read_text())["rows"]:
        rec[(r["stack"], r["model"], r["run"], r["mission"])] = r
        if (r["stack"], r["model"], r["run"]) not in jobs:
            jobs.append((r["stack"], r["model"], r["run"]))
rig = Rig(langfuse=False, mode="replay")
out = []
for stack, model, run in jobs:
    for r in rig.run_suite(stack, model, run=run):
        o = rec[(stack, model, run, r["mission"])]
        out.append({"stack": stack, "model": model, "run": run, "mission": r["mission"], "passed": r["passed"],
                    "recorded_passed": o["passed"], "same_verdict": r["passed"] == o["passed"],
                    "same_tool_calls": [c["name"] for c in r["tool_calls"]] == [c["name"] for c in o["tool_calls"]],
                    "same_tool_set": sorted(c["name"] for c in r["tool_calls"]) == sorted(c["name"] for c in o["tool_calls"]),
                    "error": r["error"], "replayed_calls": r["replayed_calls"], "model_calls": r["model_calls"],
                    "recorded_model_calls": o["model_calls"]})
rig.close()
import sys  # noqa: E402
sys.path.insert(0, str(HERE.parents[3] / "tools"))
from world_v4 import OLD_WORDS  # noqa: E402  the course's list of old-world words (names, places, currency, the old rule)
OLD = re.compile(r"\b(" + "|".join(re.escape(w) for w in OLD_WORDS) + r")\b")
old_hits = [(p, sorted(set(OLD.findall(p)))) for p in POLICY if OLD.search(p)]
summary = {"missions": len(out), "same_verdict": sum(x["same_verdict"] for x in out),
           "same_tool_calls_in_order": sum(x["same_tool_calls"] for x in out),
           "same_tool_calls_any_order": sum(x["same_tool_set"] for x in out),
           "same_model_calls": sum(x["model_calls"] == x["recorded_model_calls"] for x in out),
           "errors": [f"{x['stack']} {x['model']} r{x['run']} {x['mission']}: {x['error']}" for x in out if x["error"]],
           "search_policy_results": len(POLICY),
           "search_policy_results_with_old_world_words": len(old_hits),
           "old_world_words_found": sorted({w for _, ws in old_hits for w in ws}),
           "examples": [p[:300] for p, _ in old_hits[:3]]}
(HERE / "logs" / "replay_check.json").write_text(json.dumps({"summary": summary, "missions": out}, indent=1))
print(json.dumps(summary, indent=1))
