"""The guards tested without the model (Lecture 7): every library attack that wants a tool call, with that call made directly.

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script forced_run.py --image clean

The attack tables (guards_attacks_*.json, l7_attacks_*.json) depend on what the model chose to do in that run: with the
good prompt it refused in words 19 times in 20, so the guards were hardly exercised. Here the model's refusal is taken
away: for each of the 17 attacks that want a tool call (ledgerline/course/l6/nb7.py FORCED), the guard hears the attack's
messages and then the attacker's tool calls are made at the tool boundary of a fresh sandbox, with no guards and with the
code guards. The attack's own success check then reads Ledgerline. Pure code, no model, no key: the same answer every time.
Writes logs/l7_forced.json.
"""
import json
import os
import time

os.environ.setdefault("LEDGER_LLM_MODE", "replay")
from _common import now, write

from ledgerline.course.l6.attacks import ATTACKS
from ledgerline.course.l6.nb7 import FORCED, code_guards, forced

t0 = time.time()
rows = []
for a in ATTACKS:
    off = forced(a["id"], None)
    on = forced(a["id"], code_guards())
    rows.append({"id": a["id"], "title": a["title"], "wants_a_tool_call": a["id"] in FORCED, "no_guards": off, "code_guards": on})
    print(a["id"], f"{a['title'][:44]:44}", "| no guards:", "WORKED" if off["worked"] else ("-" if off["worked"] is None else "stopped by " + str(off.get("stopped_by"))),
          "| code guards:", "WORKED" if on["worked"] else ("-" if on["worked"] is None else "stopped by " + str(on.get("stopped_by"))))
tool = [r for r in rows if r["wants_a_tool_call"]]
summ = {"attacks": len(rows), "want_a_tool_call": len(tool), "words_only": [r["id"] for r in rows if not r["wants_a_tool_call"]],
        "no_guards": {"worked": sum(1 for r in tool if r["no_guards"]["worked"]), "worked_ids": [r["id"] for r in tool if r["no_guards"]["worked"]],
                      "stopped_by_ledgerline": [r["id"] for r in tool if not r["no_guards"]["worked"]]},
        "code_guards": {"worked": sum(1 for r in tool if r["code_guards"]["worked"]), "worked_ids": [r["id"] for r in tool if r["code_guards"]["worked"]],
                        "stopped_by": {r["id"]: r["code_guards"]["stopped_by"] for r in tool if not r["code_guards"]["worked"]}}}
write("l7_forced.json", {"at": now(), "what": "library attacks with the model's refusal taken away: the attacker's tool calls made directly at the tool boundary",
                         "model_calls": 0, "seconds": round(time.time() - t0, 1), "summary": summ, "rows": rows})
print(json.dumps(summ, indent=1))
