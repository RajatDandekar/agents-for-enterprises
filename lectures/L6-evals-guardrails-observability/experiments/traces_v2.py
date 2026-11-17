"""v2 traces for the deck (16 Nov): the demo turns, traced with the corrected input/output attributes, to every back end
whose key is present (Langfuse; LangSmith and Sentry when their keys are in the course .env).

    tools/mrun.sh .../l6_modal.py --script traces_v2.py

Runs, each in a fresh sandbox, claude-sonnet-5-5:
    ordinary   good prompt      "How many BAT-500 battery packs do we have?"                  (the first demo turn)
    good2      good prompt      "Order the usual, please, needed by 4 Dec 2026." then "Yes, go ahead."   (one session, two traces)
    incident   Thursday prompt  "Order the usual, please, needed by 4 Dec 2026."              (run until one commits; at most 3)
Writes logs/traces_v2.json (replies, calls, trace ids, links per back end, which back ends were on) and
logs/traces_v2_spans.json (every span, for the deck's figures and NB6a).
"""
from _common import now, spend, write

from ledgerline.course.l6 import tracing as T
from ledgerline.course.l6.agent import Agent
from ledgerline.llm import LLM

on = T.configured()
print("back ends configured:", on)
rows, spans = {}, {}


def llm_for(m):
    return LLM(m, cassette="L6E_traces_v2", mode="record", max_tokens=8192)


def run(name, prompt, turns, tag):
    tr = T.Tracing.from_env(public=True, batch=False)
    ag = Agent(prompt, tracing=tr, llm_for=llm_for, conversation_id=f"l6-v2-{name}-{tag}", tags=("L6", "v2", name))
    out = []
    for m in turns:
        rec = ag.turn(m)
        out.append({"text": m, "reply": rec["reply"], "trace_id": rec["trace_id"], "links": T.links(rec["trace_id"]),
                    "calls": [{k: c[k] for k in ("tool", "args", "ok", "step")} for c in rec["calls"]],
                    "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"], "usd": rec["usd"], "seconds": rec["seconds"],
                    "model_calls": len(rec["model_calls"])})
    tr.flush()
    return {"prompt": prompt, "session": ag.conversation_id, "turns": out, "saved": ag.writes()["requests"], "backends": tr.backends}, tr.log.spans


import time
tag = str(int(time.time()))[-6:]
rows["ordinary"], spans["ordinary"] = run("ordinary", "good", ["How many BAT-500 battery packs do we have?"], tag)
rows["good2"], spans["good2"] = run("good2", "good", ["Order the usual, please, needed by 4 Dec 2026.", "Yes, go ahead."], tag)
for i in range(3):
    r, sp = run("incident", "thursday", ["Order the usual, please, needed by 4 Dec 2026."], f"{tag}-{i}")
    r["tries"] = i + 1
    rows["incident"], spans["incident"] = r, sp
    if r["saved"]:
        break
usd = sum(t["usd"] for r in rows.values() for t in r["turns"])
write("traces_v2.json", {"at": now(), "backends": on, "model": "claude-sonnet-5-5", "rows": rows, "usd": round(usd, 4)})
write("traces_v2_spans.json", spans)
spend("v2_traces", usd, sum(t["model_calls"] for r in rows.values() for t in r["turns"]),
      sum(t["tokens_in"] for r in rows.values() for t in r["turns"]), sum(t["tokens_out"] for r in rows.values() for t in r["turns"]),
      "claude-sonnet-5-5", "v2 demo turns")
for k, r in rows.items():
    for t in r["turns"]:
        print(k, "|", t["text"], "|", [(c["tool"], c["args"].get("confirm")) for c in t["calls"]], "|", t["links"])
    print("  saved:", r["saved"])
