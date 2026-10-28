"""Lecture 3: the numbers the deck and the notebook use, computed from the run logs (no model calls).

Reads logs/granularity_*.json, logs/scorecard_*.json, logs/naive_s3_*.json. Writes logs/analysis.json:
  per tier and config: pass rates, tokens, ₹, seconds, tool calls, and process measures:
    committed_before_yes  action tasks where a write happened in the first turn, before the user had said anything
                          after the request (our harness asks for a preview and a yes; a generic host does not)
    previewed_first       create_purchase_order called with confirm=false before any confirm=true (intent tools)
  the 30 x 4 pass grid, and the scorecard grid (6 scenarios x harness/host x tier)
"""
import glob
import json
import pathlib

LOG = pathlib.Path(__file__).resolve().parent / "logs"
out = {"granularity": {}, "grid": {}, "scorecard": {}, "naive_s3": {}}

for f in sorted(glob.glob(str(LOG / "granularity_gemini_*.json"))):
    g = json.load(open(f))
    tier = g["model"]
    out["granularity"][tier] = {}
    out["grid"][tier] = {}
    for c, s in g["configs"].items():
        rs = [r for r in g["results"] if r["config"] == c]
        acts = [r for r in rs if r["kind"] == "action"]
        before_yes = [r["task"] for r in acts if r["turns"] and r["turns"][0]["writes"]]
        cpo = [r for r in acts if any(t["tool"] == "create_purchase_order" for t in r["trace"])]
        prev_first = 0
        for r in cpo:
            for t in r["trace"]:
                if t["tool"] == "create_purchase_order":
                    prev_first += not t["args"].get("confirm")
                    break
        ne = [n for r in rs for n in r["never_events"]]
        out["granularity"][tier][c] = {
            **{k: s["all"][k] for k in ("passed", "success", "tool_calls_mean", "services_mean", "tokens_mean",
                                        "tokens_in_mean", "seconds_mean", "inr_mean", "inr_total")},
            "lookups_passed": s["lookup"]["passed"], "actions_passed": s["action"]["passed"],
            "never_events": ne, "failed": [r["task"] for r in rs if not r["passed"]],
            "committed_before_yes": len(before_yes), "committed_before_yes_tasks": before_yes,
            "previewed_first": f"{prev_first}/{len(cpo)}" if cpo else "n/a",
            "max_tokens_task": max(rs, key=lambda r: r["tokens_in"] + r["tokens_out"])["task"],
            "max_tokens": max(r["tokens_in"] + r["tokens_out"] for r in rs)}
        out["grid"][tier][c] = {r["task"]: {"p": r["passed"], "tok": r["tokens_in"] + r["tokens_out"],
                                            "calls": r["tool_calls"], "note": (r["note"] or "; ".join(r["never_events"]))[:90]}
                                for r in rs}
    out["tasks"] = g["tasks"]

for f in sorted(glob.glob(str(LOG / "scorecard_gemini_*.json"))):
    d = json.load(open(f))
    rows = {}
    for r in d["results"]:
        first_writes = r["turns"][0]["writes"] if r["turns"] else []
        rows.setdefault(r["config"], {})[r["scenario"]] = {
            "passed": r["passed"], "never_events": r["never_events"], "notes": r["notes"],
            "tokens": r["tokens_in"] + r["tokens_out"], "cost_inr": r["cost_inr"], "seconds": r["seconds"],
            "committed_before_yes": bool(first_writes) and r["scenario"] != 1, "first_turn_writes": first_writes,
            "turns": len(r["turns"])}
    out["scorecard"][d["model"]] = {"summary": d["summary"], "by_scenario": rows}

for f in sorted(glob.glob(str(LOG / "naive_s3_*.json"))):
    d = json.load(open(f))
    row = {}
    for lab in ("naive", "intent_tools"):
        r = d[lab]
        lr = r["live_run"]
        row[lab] = {"passed": r["passed"], "never_events": r["never_events"], "services": len(lr),
                    "refused": [c["err_cd"] for c in lr if c["rc"] == "E"],
                    "sup_search": [c["payload"].get("q") for c in lr if c["svc"] == "sup_search"],
                    "sup_create": sum(c["svc"] == "sup_create" for c in lr),
                    "orders": r["new_orders"], "tokens": r["tokens_in"] + r["tokens_out"], "cost_inr": r["cost_inr"],
                    "seconds": r["seconds"]}
    out["naive_s3"][d["model"]] = row

(LOG / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for tier, cs in out["granularity"].items():
    for c, v in cs.items():
        print(tier, c, {k: v[k] for k in ("passed", "tokens_mean", "inr_mean", "committed_before_yes", "previewed_first",
                                          "failed")})
for m, s in out["scorecard"].items():
    for c, rows in s["by_scenario"].items():
        print(m, c, {k: (v["passed"], v["committed_before_yes"]) for k, v in rows.items()})
