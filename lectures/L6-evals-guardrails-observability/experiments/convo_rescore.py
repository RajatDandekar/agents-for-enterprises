"""Re-score the recorded conversations' trajectory check with the corrected rule (no model call): the first rule also
demanded a regex "yes" in Emma's message and misread one real yes. Keeps the first verdicts as trajectory_v1.

    PYTHONPATH=ledgerline <venv>/python lectures/L6-evals-guardrails-observability/experiments/convo_rescore.py
"""
import json
import pathlib

from ledgerline.course.l6.convo import trajectory_of

p = pathlib.Path(__file__).parent / "logs" / "convos.json"
d = json.loads(p.read_text())
changed = []
for r in d["rows"]:
    ok, why = trajectory_of([{"calls": t["calls"]} for t in r["turns"]])
    for c in r["checks"]:
        if c["kind"] == "trajectory":
            if c["pass"] != ok:
                changed.append(f"{r['prompt']} {r['persona']} {r['scenario']}: {c['pass']} -> {ok} ({c['why'][:80]})")
            c.setdefault("v1", {"pass": c["pass"], "why": c["why"]})
            c["pass"], c["why"] = ok, why
    r["pass"] = r["error"] is None and all(c["pass"] for c in r["checks"])
    r["gate"] = r["error"] is None and all(c["pass"] for c in r["checks"] if c["kind"] in ("outcome", "trajectory"))
names = ("end state in Ledgerline", "order of actions across turns", "finished within the turn budget", "asked only what it needed",
         "last word matches Ledgerline")
for pr in d["summary"]:
    rs = [r for r in d["rows"] if r["prompt"] == pr]
    d["summary"][pr].update({"passed": sum(r["pass"] for r in rs), "gate": sum(r["gate"] for r in rs),
                             "by_check": {n: sum(1 for r in rs for c in r["checks"] if c["name"] == n and c["pass"]) for n in names}})
d["rescored"] = {"what": "trajectory check without the regex yes", "changed": changed}
p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
print(changed)
print({k: {x: v[x] for x in ("conversations", "passed", "gate", "mean_turns", "mean_usd", "by_check")} for k, v in d["summary"].items()})
