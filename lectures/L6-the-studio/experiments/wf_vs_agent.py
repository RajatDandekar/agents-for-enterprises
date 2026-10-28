"""The same repeated task, N times, two ways: a Studio workflow vs Ask Rasoi (the Lecture 5 agent, stage=agent).

Task (Monday's reorder check): look at GSK-SIL-05L and WHS-STD-01; for any item below its reorder level with nothing
on order, raise a purchase request for three times its reorder level on PRD-07, needed by 9 Nov 2026, and tell
@rohit the request number. On a fresh Rasoi the right answer is exactly one PR: 36,000 x WHS-STD-01.

    lectures/L6-the-studio/experiments/mrun.sh --script lectures/L6-the-studio/experiments/wf_vs_agent.py --args "--n 10"
Writes logs/wf_vs_agent.json. Ask Rasoi calls gemini:gemini-3.8-flash live every run (no cassette), at
temperature 0 (its default) and at temperature 1.0.
"""
import argparse
import collections
import concurrent.futures as cf
import json
import pathlib
import time

from bahi.experience.harness import AskRasoi
from bahi.experience.players import Players
from bahi.experience.studio.engine import Engine, Store
from bahi.experience.studio.templates import template

LOG = pathlib.Path(__file__).parent / "logs" / "wf_vs_agent.json"
ASK = ("It is Monday. Check the stock of GSK-SIL-05L and WHS-STD-01. For any item below its reorder level with "
       "nothing on order, raise a purchase request for three times its reorder level on cost centre PRD-07, needed "
       "by 9 November 2026, and message @rohit with the request number.")
YES = "Yes, go ahead."


def monday_workflow():
    """The Studio's 'Reorder when low', cut at the request: raise it, tell Rohit (his approval is his own job)."""
    wf = template("reorder-when-low")
    keep = {"low", "plan", "nothing_on_order", "pr", "note"}
    wf["id"], wf["name"] = "monday-reorder-check", "Monday reorder check"
    wf["nodes"] = [n for n in wf["nodes"] if n["id"] in keep]
    wf["nodes"].append({"id": "tell", "type": "message", "title": "Tell Rohit", "x": 1060, "y": 100,
                        "config": {"to": "@rohit", "as": "KJOSHI", "text": "Monday reorder: raised {{nodes.pr.request_no}} "
                                   "for {{nodes.plan.quantity}} x {{trigger.item_code}} ({{nodes.pr.status}})."}})
    wf["edges"] = [e for e in wf["edges"] if e["from"] in keep and e["to"] in keep] + [{"from": "pr", "to": "tell"}]
    return wf


def outcome(erp):
    prs = [dict(r) for r in erp.q("SELECT h.pr_no, h.status, h.cc_cd, h.need_dt, l.itm_cd, l.qty FROM pr_hdr h "
                                  "JOIN pr_line l ON l.pr_no=h.pr_no WHERE h.pr_no >= 'PR/2026/04417' ORDER BY h.pr_no")]
    msgs = [dict(r) for r in erp.q("SELECT recipient, body FROM ntf_queue WHERE channel='SLACK' ORDER BY id")]
    sig = tuple((p["itm_cd"], p["qty"], p["cc_cd"], p["need_dt"]) for p in prs)
    told = any(m["recipient"] == "@rohit" and any(p["pr_no"] in m["body"] for p in prs) for m in msgs)
    correct = sig == (("WHS-STD-01", 36000, "PRD-07", "2026-11-09"),) and told
    return {"prs": prs, "messages": msgs, "signature": [list(s) for s in sig], "told_rohit": told, "correct": correct}


def run_workflow(i):
    players = Players()
    pid = players.join(f"wf{i}").pid
    eng = Engine(toolbox_for=lambda u, names=None: players.toolbox(pid, u, names), store=Store(), pid=pid)
    t0 = time.perf_counter()
    run = eng.run_until_pause(eng.start(monday_workflow()))
    secs = time.perf_counter() - t0
    path = [e["node"] for e in run["log"] if e.get("node") and e["event"] not in ("skipped",)]
    return {"i": i, "status": run["status"], "seconds": round(secs, 4), "tokens": 0, "cost_inr": 0.0, "model_calls": 0,
            "tool_seq": path, **outcome(players.erp(pid))}


def run_agent(i, temperature):
    players = Players()
    pid = players.join(f"ag{i}").pid
    erp = players.erp(pid)
    a = AskRasoi(erp, "KJOSHI", "agent", pid=pid)
    a.llm.temperature = temperature
    t0 = time.perf_counter()
    turns, tin, tout, cost, calls, seq = [], 0, 0, 0.0, 0, []
    try:
        for msg in [ASK, YES, YES]:
            r = a.respond(msg)
            turns.append({"user": msg, "reply": r["reply"], "tools": [c["tool"] for c in r["cards"]]})
            tin, tout, cost, calls = tin + r["tokens_in"], tout + r["tokens_out"], cost + r["cost_inr"], calls + r["model_calls"]
            seq += [c["tool"] + ("+" if (c.get("args") or {}).get("confirm") else "") for c in r["cards"]]
            o = outcome(erp)
            if o["prs"] and o["told_rohit"]:
                break
    finally:
        a.close()
    return {"i": i, "temperature": temperature, "seconds": round(time.perf_counter() - t0, 2), "tokens_in": tin,
            "tokens_out": tout, "tokens": tin + tout, "cost_inr": round(cost, 4), "model_calls": calls,
            "turns": len(turns), "tool_seq": seq, "transcript": turns, **outcome(erp)}


def stats(rows):
    n = len(rows)
    sigs = collections.Counter(json.dumps(r["signature"]) for r in rows)
    seqs = collections.Counter(" > ".join(r["tool_seq"]) for r in rows)
    avg = lambda k: round(sum(r.get(k, 0) for r in rows) / n, 4)
    return {"n": n, "correct": sum(r["correct"] for r in rows), "distinct_outcomes": len(sigs),
            "outcomes": dict(sigs.most_common()), "distinct_paths": len(seqs), "paths": dict(seqs.most_common()),
            "avg_tokens": avg("tokens"), "avg_cost_inr": avg("cost_inr"), "avg_seconds": avg("seconds"),
            "avg_model_calls": avg("model_calls"), "avg_turns": avg("turns") if "turns" in rows[0] else None,
            "total_cost_inr": round(sum(r["cost_inr"] for r in rows), 3)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    out = {"_what": __doc__, "task": ASK, "workflow": monday_workflow(), "runs": {}}
    out["runs"]["workflow"] = [run_workflow(i) for i in range(a.n)]
    with cf.ThreadPoolExecutor(5) as ex:
        out["runs"]["agent_t0"] = list(ex.map(lambda i: run_agent(i, 0.0), range(a.n)))
        out["runs"]["agent_t1"] = list(ex.map(lambda i: run_agent(i, 1.0), range(a.n)))
    out["stats"] = {k: stats(v) for k, v in out["runs"].items()}
    LOG.write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
    for k, s in out["stats"].items():
        print(f"\n== {k}: {s['correct']}/{s['n']} correct · {s['distinct_outcomes']} outcomes · {s['distinct_paths']} paths"
              f" · {s['avg_tokens']} tokens · ₹{s['avg_cost_inr']} · {s['avg_seconds']} s · calls {s['avg_model_calls']}")
        for o, c in s["outcomes"].items():
            print(f"   {c} × {o}")
        for p, c in list(s["paths"].items())[:6]:
            print(f"   {c} × {p}")
