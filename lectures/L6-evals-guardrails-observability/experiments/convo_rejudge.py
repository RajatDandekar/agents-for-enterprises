"""Re-judge "last word matches Ledgerline" on the recorded conversations with the corrected evidence (newest tool results
first, plus the memory and briefing the agent had). Haiku only: about 20 small calls. Keeps the first verdict as v1.

    tools/mrun.sh .../l6_modal.py --script convo_rejudge.py
"""
import json

from _common import LOGS, spend

from ledgerline.course.l6 import convo as CV
from ledgerline.course.l6.agent import Agent
from ledgerline.course.l6.judges import judge

p = LOGS / "convos.json"
d = json.loads(p.read_text())
ag = Agent("good")           # only for its window (memory, briefing); no model call
usd, changed = 0.0, []
for r in d["rows"]:
    if not r["turns"]:
        continue
    turns = [{"calls": t["calls"]} for t in r["turns"]]
    ev = CV.last_word_evidence(ag, turns)
    tr = "\n".join(f"Emma: {t['emma']}\nAsk Northbridge: {t['reply']}" for t in r["turns"])
    v = judge(CV.LAST_WORD, r["turns"][-1]["reply"], ev, tr[-3000:], cassette="L6E_convjudge2", mode="record")
    usd += v["usd"]
    for c in r["checks"]:
        if c["name"] == "last word matches Ledgerline":
            if c["pass"] != v["pass"]:
                changed.append(f"{r['prompt']} {r['persona']} {r['scenario']}: {c['pass']} -> {v['pass']}")
            c.setdefault("v1", {"pass": c["pass"], "why": c["why"]})
            c["pass"], c["why"] = v["pass"], v["reason"]
    r["pass"] = r["error"] is None and all(c["pass"] for c in r["checks"])
names = ("end state in Ledgerline", "order of actions across turns", "finished within the turn budget", "asked only what it needed",
         "last word matches Ledgerline")
for pr in d["summary"]:
    rs = [r for r in d["rows"] if r["prompt"] == pr]
    d["summary"][pr].update({"passed": sum(r["pass"] for r in rs),
                             "by_check": {n: sum(1 for r in rs for c in r["checks"] if c["name"] == n and c["pass"]) for n in names}})
d["rejudged"] = {"what": "last-word judge with newest evidence first, plus memory and briefing", "changed": changed}
p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
spend("v2_convos_rejudge", usd, len(d["rows"]), 0, 0, "claude-haiku-5-5", "re-judged the last-word check")
print(changed)
print({k: {x: v[x] for x in ("passed", "gate", "by_check")} for k, v in d["summary"].items()})
for r in d["rows"]:
    for c in r["checks"]:
        if not c["pass"]:
            print(r["prompt"], r["persona"], r["scenario"], "|", c["name"], "|", c["why"][:200])
