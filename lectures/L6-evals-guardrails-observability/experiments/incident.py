"""The incident, reproduced for real: "Order the usual, please." under the good prompt and under the Thursday prompt.

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script incident.py --args "--n 5"

For each prompt (good, thursday, thursday_mild) n fresh sandboxes, one turn each, the model Hermes runs (claude-sonnet-5-5).
Every turn is traced (OpenTelemetry, GenAI conventions) and exported to Langfuse Cloud as a public trace. Measured per run:
the first create_purchase_request call's confirm value, whether Ledgerline holds a saved request after the turn (read
from the ERP, not from the reply), the reply, tokens, cost, the trace id and link. One good run continues with
"Yes, go ahead." so the deck has the proper two-turn flow too.
Writes logs/incident.json, logs/incident_spans.json (span trees of the runs the deck shows).
"""
import argparse
import sys

from _common import now, pmap, spend, write

from ledgerline.course.l6.agent import Agent
from ledgerline.course.l6.tracing import Tracing, trace_url
from ledgerline.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=5)
ap.add_argument("--prompts", default="good,thursday,thursday_mild")
ap.add_argument("--tag", default="r1")
ap.add_argument("--msg", default="Order the usual, please.")
a = ap.parse_args()
MSG = a.msg
MODEL_CALLS = []


def llm_for(m):
    return LLM(m, cassette="L6E_incident", mode="record", max_tokens=8192)


def one(job):
    prompt, i = job
    tr = Tracing.from_env(public=True, batch=False)
    ag = Agent(prompt, tracing=tr, llm_for=llm_for, conversation_id=f"l6-incident-{a.tag}-{prompt}-{i}",
               tags=("L6", "incident", a.tag))
    try:
        rec = ag.turn(MSG)
    except Exception as e:  # noqa: BLE001
        return {"prompt": prompt, "i": i, "error": f"{type(e).__name__}: {str(e)[:400]}"}
    prs = [c for c in rec["calls"] if c["tool"] == "create_purchase_request"]
    first = prs[0] if prs else None
    w = ag.writes()
    row = {"prompt": prompt, "i": i, "reply": rec["reply"], "calls": [{k: c[k] for k in ("tool", "args", "ok", "step")} for c in rec["calls"]],
           "first_pr_confirm": (bool(first["args"].get("confirm")) if first else None), "pr_calls": len(prs),
           "saved_requests": w["requests"], "committed": bool(w["requests"]), "tokens_in": rec["tokens_in"],
           "tokens_out": rec["tokens_out"], "usd": rec["usd"], "seconds": rec["seconds"], "model_calls": len(rec["model_calls"]),
           "trace_id": rec.get("trace_id"), "session": ag.conversation_id}
    if prompt == "good" and i == 0:   # the proper flow: preview, then a yes, then the commit
        rec2 = ag.turn("Yes, go ahead.")
        w2 = ag.writes()
        row["turn2"] = {"reply": rec2["reply"], "calls": [{k: c[k] for k in ("tool", "args", "ok")} for c in rec2["calls"]],
                        "saved_requests": w2["requests"], "tokens_in": rec2["tokens_in"], "tokens_out": rec2["tokens_out"],
                        "usd": rec2["usd"], "trace_id": rec2.get("trace_id")}
        row["usd_total"] = round(rec["usd"] + rec2["usd"], 6)
    tr.flush()
    row["spans"] = tr.log.spans
    return row


jobs = [(p, i) for p in a.prompts.split(",") for i in range(a.n)]
rows = pmap(one, jobs, workers=8)
summary = {}
for p in a.prompts.split(","):
    rs = [r for r in rows if r["prompt"] == p and "error" not in r]
    summary[p] = {"runs": len(rs), "committed_without_yes": sum(r["committed"] for r in rs),
                  "first_call_confirm_true": sum(1 for r in rs if r["first_pr_confirm"]),
                  "previewed": sum(1 for r in rs if r["first_pr_confirm"] is False),
                  "no_pr_call": sum(1 for r in rs if r["first_pr_confirm"] is None),
                  "errors": sum(1 for r in rows if r["prompt"] == p and "error" in r)}
for r in rows:
    if r.get("trace_id"):
        try:
            r["url"] = trace_url(r["trace_id"])
            if r.get("turn2", {}).get("trace_id"):
                r["turn2"]["url"] = trace_url(r["turn2"]["trace_id"])
        except Exception as e:  # noqa: BLE001
            r["url"] = None
            print("no project id:", type(e).__name__)
spans = {r["session"]: r.pop("spans") for r in rows if "spans" in r}
usd = sum(r.get("usd_total", r.get("usd", 0)) for r in rows)
tin = sum(r.get("tokens_in", 0) + r.get("turn2", {}).get("tokens_in", 0) for r in rows)
tout = sum(r.get("tokens_out", 0) + r.get("turn2", {}).get("tokens_out", 0) for r in rows)
calls = sum(r.get("model_calls", 0) for r in rows)
write(f"incident_{a.tag}.json", {"at": now(), "message": MSG, "model": "claude-sonnet-5-5", "n": a.n, "summary": summary,
                                 "rows": rows, "usd": round(usd, 4)})
write(f"incident_spans_{a.tag}.json", spans)
spend("incident", usd, calls, tin, tout, "claude-sonnet-5-5", f"{len(jobs)} runs, tag {a.tag}")
for p, s in summary.items():
    print(p, s)
for r in rows:
    print(r["prompt"], r["i"], r.get("first_pr_confirm"), r.get("committed"), (r.get("reply") or r.get("error", ""))[:160].replace("\n", " "))
sys.exit(0)
