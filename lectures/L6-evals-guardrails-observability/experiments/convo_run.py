"""Multi-turn evals (16 Nov): a simulated Emma (claude-haiku-5-5) talks to Ask Northbridge (claude-sonnet-5-5); the whole
conversation is scored (ledgerline/course/l6/convo.py).

    tools/mrun.sh .../l6_modal.py --script convo_run.py --args "--prompts good,thursday --personas terse,impatient"

5 goals x personas x prompts, each in a fresh sandbox, traced (one session per conversation, one trace per turn).
Writes logs/convos.json: every conversation turn by turn, its checks with reasons, cost split (agent, simulated user, judge).
"""
import argparse

from _common import now, pmap, spend, write

from ledgerline.course.l6 import convo as CV
from ledgerline.course.l6 import tracing as T
from ledgerline.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", default="good,thursday")
ap.add_argument("--personas", default="terse,impatient")
ap.add_argument("--scenarios", default="all")
ap.add_argument("--tag", default="r1")
a = ap.parse_args()
keys = list(CV.SCENARIOS) if a.scenarios == "all" else a.scenarios.split(",")


def one(job):
    key, persona, prompt = job
    tr = T.Tracing.from_env(public=True, batch=False)
    cas = f"L6E_convo_{prompt}_{persona}"
    r = CV.run_conversation(key, persona=persona, prompt=prompt, tracing=tr,
                            llm_for=lambda m: LLM(m, cassette=cas, mode="record", max_tokens=8192),
                            sim_llm_for=lambda m: LLM(m, cassette=cas + "_sim", mode="record", max_tokens=300),
                            conv=f"l6-conv-{a.tag}-{prompt}-{persona}-{key}", tags=(a.tag, prompt))
    tr.flush()
    for t in r["turns"]:
        t["links"] = T.links(t.get("trace_id"))
    return r


jobs = [(k, pe, pr) for pr in a.prompts.split(",") for pe in a.personas.split(",") for k in keys]
rows = pmap(one, jobs, workers=10)
summ = {}
for pr in a.prompts.split(","):
    rs = [r for r in rows if r["prompt"] == pr]
    summ[pr] = {"conversations": len(rs), "passed": sum(r["pass"] for r in rs), "gate": sum(r["gate"] for r in rs),
                "errors": sum(1 for r in rs if r["error"]), "mean_turns": round(sum(len(r["turns"]) for r in rs) / max(1, len(rs)), 2),
                "mean_usd": round(sum(r["usd"] for r in rs) / max(1, len(rs)), 4),
                "by_check": {n: sum(1 for r in rs for c in r["checks"] if c["name"] == n and c["pass"])
                             for n in ("end state in Ledgerline", "order of actions across turns", "finished within the turn budget",
                                       "asked only what it needed", "last word matches Ledgerline")}}
usd = sum(r["usd"] for r in rows)
write("convos.json", {"at": now(), "agent": "claude-sonnet-5-5", "simulated_user": "claude-haiku-5-5", "judge": "claude-haiku-5-5",
                      "summary": summ, "rows": rows, "usd": round(usd, 4),
                      "usd_split": {k: round(sum(r[k] for r in rows), 4) for k in ("agent_usd", "sim_usd", "judge_usd")}})
spend("v2_convos", usd, sum(r["model_calls"] for r in rows), sum(r["tokens_in"] for r in rows), sum(r["tokens_out"] for r in rows),
      "claude-sonnet-5-5 + haiku (simulated user, judge)", f"{len(rows)} simulated conversations")
print(summ)
for r in rows:
    print(r["prompt"], r["persona"], r["scenario"], "PASS" if r["pass"] else "FAIL", len(r["turns"]), "turns", r["error"] or "",
          " | ".join(f"{c['name']}: {c['why'][:80]}" for c in r["checks"] if not c["pass"]))
    for t in r["turns"]:
        print("    E:", t["emma"][:100].replace("\n", " "))
