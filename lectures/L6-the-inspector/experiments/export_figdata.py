"""Copy the measured numbers from experiments/logs/*.json into figs.js (between the DATA markers). Stdlib only.

    python3 lectures/L6-the-inspector/experiments/export_figdata.py

Also merges logs/suite_tier_pro_a.json + suite_tier_pro_b.json into logs/suite_tier_pro.json (the pro run was split
in two Modal jobs to stay under the 30-minute job limit) and writes logs/bots_matrix.json.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
FIGS = HERE.parent / "figs.js"
sys.path.insert(0, str(HERE.parents[2] / "bahi"))


def load(name):
    p = LOGS / name
    return json.loads(p.read_text()) if p.exists() else None


# ---------------------------------------------------------------- merge the two halves of the pro run
a, b = load("suite_tier_pro_a.json"), load("suite_tier_pro_b.json")
if a and b:
    from bahi.evals.runner import summarise  # pure Python
    cases = a["cases"] + b["cases"]
    order = {c: i for i, c in enumerate(json.loads(json.dumps([r["id"] for r in load("suite_graph.json")["cases"]])))}
    cases.sort(key=lambda r: order.get(r["id"], 99))
    pro = {"meta": {**a["meta"], "tag": "tier_pro", "run_id": a["meta"]["run_id"].replace("36 cases", "60 cases"),
                    "note": "merged from suite_tier_pro_a.json (G, V, N) and suite_tier_pro_b.json (S, A, M)"},
           "summary": summarise(cases), "cases": cases}
    (LOGS / "suite_tier_pro.json").write_text(json.dumps(pro, indent=1, ensure_ascii=False, default=str))

METRICS = ["asked_missing", "no_lookup_asks", "no_forbidden", "no_duplicate", "final_status", "right_clause"]
NEVER = ["NE1", "NE2", "NE3", "NE4", "NE5"]


def short(s, n):
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def summ(d):
    s = d["summary"]
    keep = ["cases", "passed", "pass_rate", "ci95", "never_event_cases", "never_events", "metric_failures", "metric_applies",
            "inr", "inr_per_case", "inr_per_resolved_order", "resolved_orders", "tokens", "llm_calls", "turns", "turn_p50",
            "turn_p95", "convo_p95", "seconds", "sim_inr", "by"]
    return {k: s.get(k) for k in keep}


def per_case(d):
    return [{"id": r["id"], "p": r["passed"], "ne": [x.split(" ")[0] for x in r["never_events"]],
             "f": [m for m, v in r["metrics"].items() if v["ok"] is False],
             "why": "; ".join(f"{m}: {v['why']}" for m, v in r["metrics"].items() if v["ok"] is False)[:220] + (
                 (" · " + "; ".join(r["never_events"]))[:200] if r["never_events"] else ""),
             "inr": r["totals"]["inr"], "s": r["totals"]["seconds"], "turns": len(r["turns"])} for r in d["cases"]]


def transcript(d, cid, n=700):
    r = next((x for x in d["cases"] if x["id"] == cid), None)
    if not r:
        return None
    return {"id": cid, "name": r["name"], "agent": d["meta"]["agent"], "passed": r["passed"], "ne": r["never_events"],
            "metrics": {m: {"ok": v["ok"], "why": v["why"]} for m, v in r["metrics"].items()},
            "turns": [{"user": short(t["user"], 300), "act": t["act"], "agent": short(t["agent"], n), "writes": t["writes"],
                       "s": t["seconds"], "inr": t["inr"]} for t in r["turns"]],
            "orders": r.get("orders", []), "inr": r["totals"]["inr"], "tokens": r["totals"]["tokens_in"] + r["totals"]["tokens_out"]}


OUT = {"_logs": "lectures/L6-the-inspector/experiments/logs/"}
# ---------------------------------------------------------------- the suite (from the code, not a log)
from bahi.evals import suite as SU  # noqa: E402

OUT["suite"] = SU.matrix()
OUT["suite"]["hash"] = SU.suite_hash()
# ---------------------------------------------------------------- runs
runs = {}
for tag in ("graph", "loop", "naive", "tier_pro", "tier_mix", "tier_flashlite", "tier_lite"):
    d = load(f"suite_{tag}.json")
    if d:
        runs[tag] = {"agent": d["meta"]["agent"], "models": d["meta"].get("models"), "summary": summ(d), "cases": per_case(d),
                     "langfuse": d["meta"].get("langfuse")}
OUT["runs"] = runs
# live (first) runs vs the final scoring, for the honesty note
live = {}
for tag in ("graph", "loop", "naive"):
    lv = load(f"live/suite_{tag}.json")
    if lv:
        live[tag] = {"passed": lv["summary"]["passed"]}
OUT["live_first_scoring"] = live
# ---------------------------------------------------------------- transcripts for the figures
G, Lp, N = load("suite_graph.json"), load("suite_loop.json"), load("suite_naive.json")
T = {}
for key, d, cid in [("naive_G15", N, "G15"), ("graph_S5", G, "S5"), ("graph_V10", G, "V10"), ("graph_S2", G, "S2"), ("graph_N02", G, "N02"),
                    ("graph_V11", G, "V11"), ("graph_M02", G, "M02"), ("loop_A02", Lp, "A02"), ("loop_A03", Lp, "A03"),
                    ("loop_S5", Lp, "S5"), ("naive_S5", N, "S5"), ("naive_S2", N, "S2"), ("naive_A07", N, "A07"),
                    ("lite_V04", load("suite_tier_lite.json"), "V04")]:
    if d:
        t = transcript(d, cid)
        if t:
            T[key] = t
if G:
    t = transcript(G, "M03")
    if t:
        T["graph_M03_llm"] = t
b0 = load("bots_p.json")  # the pilot run: scripted Kavita, where M03 failed
if b0 and "reference" in b0:
    c = next((x for x in b0["reference"]["cases"] if x["id"] == "M03"), None)
    if c:
        T["ref_M03_scripted"] = {"id": "M03", "name": "Almost nothing given", "agent": "graph · scripted Kavita (pilot run)", "passed": c["passed"],
                                 "ne": c["ne_full"], "metrics": {m: {"ok": False, "why": w} for m, w in c["why"].items()},
                                 "turns": [{"user": short(t["user"], 300), "act": t["act"], "agent": short(t["agent"], 700),
                                            "writes": t["writes"]} for t in c["turns"]], "orders": c["orders"], "inr": c["inr"], "tokens": 0}
OUT["transcripts"] = T
# ---------------------------------------------------------------- trace of S2 on the graph, and turn seconds per agent
if G:
    r = next(x for x in G["cases"] if x["id"] == "S2")
    OUT["trace_S2"] = [{k: s.get(k) for k in ("seq", "kind", "name", "node", "purpose", "turn", "start", "seconds", "tokens_in",
                                              "tokens_out", "inr")} for s in r["spans"]]
    OUT["turn_seconds"] = {tag: sorted(round(t["seconds"], 2) for x in d["cases"] for t in x["turns"])
                           for tag, d in (("graph", G), ("loop", Lp), ("naive", N)) if d}
# ---------------------------------------------------------------- broken bots
bots = {}
for p in sorted(LOGS.glob("bots_[0-9].json")):
    bots.update(json.loads(p.read_text()))
if bots:
    ref = {c["id"]: c for c in bots["reference"]["cases"]}
    cols = METRICS + NEVER
    rows = []
    for name, v in bots.items():
        cells = {}
        for m in cols:
            cells[m] = sum(1 for c in v["cases"] if (m in c["failed"] or m in c["ne"])
                           and not (m in ref[c["id"]]["failed"] or m in ref[c["id"]]["ne"]))
        caught = None if name == "reference" or v["targets"] == ["tone"] else any(cells.get(t, 0) for t in v["targets"])
        ex = next((c for c in v["cases"] if any(t in c["failed"] or t in c["ne"] for t in v["targets"])
                   and not any(t in ref[c["id"]]["failed"] or t in ref[c["id"]]["ne"] for t in v["targets"])), None)
        rows.append({"bot": name, "what": v["what"], "targets": v["targets"], "passed": v["summary"]["passed"],
                     "cells": cells, "caught": caught, "inr": v["summary"]["inr"],
                     "example": {"id": ex["id"], "why": short("; ".join(f"{k}: {w}" for k, w in ex["why"].items()) + (
                         " · " + "; ".join(ex["ne_full"]) if ex["ne_full"] else ""), 260),
                                 "last": short(ex["turns"][-1]["agent"], 300)} if ex else None})
    OUT["bots"] = {"cols": cols, "rows": rows}
    (LOGS / "bots_matrix.json").write_text(json.dumps(OUT["bots"], indent=1, ensure_ascii=False))
# ---------------------------------------------------------------- judge
J = load("judge.json")
if J:
    OUT["judge"] = {"per_question": {q: {k: v.get(k) for k in ("code_metric", "n", "agree", "rate", "kappa", "yes_yes", "yes_no",
                                                                "no_yes", "no_no")} | {"examples": v["disagreements"][:4]}
                                     for q, v in J["checks"]["per_question"].items()},
                    "tone": J["tone_labels"]["agreement"], "tone_rows": J["tone_labels"]["rows"],
                    "tone_by_run": J["tone_all"]["by_run"], "cost": J["cost"]}
# ---------------------------------------------------------------- variance, gate
V = load("variance.json")
if V:
    OUT["variance"] = {"cases": V["cases"], "agents": {a: {"per_case": v["per_case"], "passes_per_run": v["passes_per_run"],
                                                           "flipped": v["flipped"], "inr": v["inr"]} for a, v in V["agents"].items()}}
GD = load("gate_demo.json")
if GD:
    OUT["gate"] = {"replay_vs_live": GD["replay_vs_live"], "baseline": {k: GD["baseline"][k] for k in ("cases", "passed", "pass_rate", "ci95")},
                   "verdicts": {k: {"passed": v["passed"], "reasons": v["reasons"], "cand": v["candidate"],
                                    "newly_failing": v["newly_failing"], "changes": v["changes"][:8]} for k, v in GD["verdicts"].items()},
                   "cli": GD["cli"]}
SP = load("spend.json")
if SP:
    OUT["spend"] = SP

js = FIGS.read_text() if FIGS.exists() else ""
blob = "const L6 = " + json.dumps(OUT, ensure_ascii=False, separators=(",", ":")) + ";"
start, end = "/* DATA:BEGIN", "/* DATA:END */"
if start in js:
    i = js.index(start)
    j = js.index(end)
    head = js[:i]
    line_end = js.index("\n", i)
    js = head + js[i:line_end + 1] + blob + "\n" + js[j:]
    FIGS.write_text(js)
    print("figs.js DATA updated:", len(blob), "bytes")
else:
    print("no DATA markers in figs.js; wrote nothing")
