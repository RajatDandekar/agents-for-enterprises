"""Lecture 3 v4: build logs/race.json from the race's recorded runs (race_modal.py). Standard library only, no LLM.

    python3 lectures/L3-the-memory/experiments/race_report.py

Reads logs/race_answers/<method>__{150,250,250n}.json, logs/paste_all.json (the measured 12-question sample) and
logs/wiki_update.json. Writes logs/race.json: the table (overall + by question type), the 150 -> 250 word delta, the
withheld notice before/after, a measured cascade (RAG first, the wiki hybrid only when RAG finds nothing), the two
example answers verbatim per method, the spend, and the decision.
"""
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
RA = LOGS / "race_answers"
METHODS = ["rag", "wiki", "hybrid", "sections"]
TYPES = ["single_lookup", "procedure", "rule", "service_field", "table_lookup", "multi_hop", "version_conflict",
         "exact_code", "not_in_docs", "permission"]
TARGETS = {"recall@5": 0.90, "answer_correct": 0.90, "citation_correct": 0.95, "retrieval_p95_s": 0.200,
           "time_to_answer_p95_s": 4.0}
EXAMPLES = ["Q-EMMA", "Q-0412"]


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 4)


def row(rep, rs=None):
    rs = rep["records"] if rs is None else rs
    if not rs:
        return {"n": 0}
    fx = [r["fact"]["ok"] for r in rs if r["fact"]["ok"] is not None]
    cs = [r["citation"]["ok"] for r in rs if r.get("citation")]
    rt = [r for r in rs if r["retrieval"]["n_gold"]]
    return {"n": len(rs),
            "answer_correct": round(sum(bool(r["judge"]["ok"]) for r in rs) / len(rs), 4),
            "fact_correct": round(sum(fx) / len(fx), 4) if fx else None,
            "citation_correct": round(sum(cs) / len(cs), 4) if cs else None,
            "recall@5": round(sum(r["retrieval"]["hit@5"] for r in rt) / len(rt), 4) if rt else None,
            "retrieval_p50_s": pct([r["retrieval_s"] for r in rs], 50), "retrieval_p95_s": pct([r["retrieval_s"] for r in rs], 95),
            "answer_p50_s": pct([r["total_s"] for r in rs], 50), "answer_p95_s": pct([r["total_s"] for r in rs], 95),
            "cost_per_q_usd": round(sum(r["cost_total_usd"] for r in rs) / len(rs), 6),
            "llm_calls_per_q": round(statistics.mean(1 + (r.get("nav_calls") or 0) for r in rs), 2)}


def load(m, v):
    p = RA / f"{m}__{v}.json"
    return json.loads(p.read_text()) if p.exists() else None


reps = {m: {v: load(m, v) for v in ("150", "250", "250n")} for m in METHODS}
race = {m: reps[m]["250n"] for m in METHODS}
out = {"generated": "race_report.py", "what": "the race: 224 documentation questions, the same answer prompt (250-word cap), "
       "answer and judge model gemini-3.8-flash (Google's endpoint, one client: WikiLLM, thinking tokens counted as "
       "output), the same 9,000-character source cap, the same withheld notice, one Modal L4 container per method "
       "(4 vCPU, 16 GiB), retrieval timed one question at a time",
       "methods": {m: race[m]["label"] for m in METHODS}, "machine": race["rag"]["machine"], "targets": TARGETS}

# ----------------------------------------------------------------- the table
out["overall"] = {m: row(race[m]) for m in METHODS}
out["by_type"] = {t: {m: row(race[m], [r for r in race[m]["records"] if r["type"] == t]) for m in METHODS} for t in TYPES}
pa = json.loads((LOGS / "paste_all.json").read_text())
mr = pa["measured_run"]
out["paste_all"] = {"label": mr["label"], "n": mr["n"], "answer_correct": mr["answer_correct"], "fact_correct": mr["fact_correct"],
                    "citation_correct": mr["citation_correct"], "answer_p50_s": mr["seconds"]["p50"],
                    "answer_p95_s": mr["seconds"]["p95"], "tokens_in_per_q": mr["tokens_in_per_q"],
                    "cost_per_q_usd": mr["cost_per_q_usd"], "whole_dump_tokens": pa.get("total_tokens"),
                    "fits_any_model": pa.get("fits_any_model"), "largest_window": pa.get("largest_window"),
                    "note": "a SAMPLE of 12 questions on a 648-file subset (not re-run: $0.61 a question); the whole dump "
                            "fits no model's context window. Not comparable row for row with the 224-question runs."}

# ----------------------------------------------------------------- the answer cap and the withheld notice
out["cap_150_vs_250"] = {}
for m in METHODS:
    a, b = row(reps[m]["150"]), row(reps[m]["250"])
    em = {v: next(r for r in reps[m][v]["records"] if r["id"] == "Q-EMMA") for v in ("150", "250")}
    out["cap_150_vs_250"][m] = {
        "answer_correct": [a["answer_correct"], b["answer_correct"]], "fact_correct": [a["fact_correct"], b["fact_correct"]],
        "delta_answer_correct": round(b["answer_correct"] - a["answer_correct"], 4),
        "answer_p50_s": [a["answer_p50_s"], b["answer_p50_s"]],
        "multi_hop_correct": [row(reps[m]["150"], [r for r in reps[m]["150"]["records"] if r["type"] == "multi_hop"])["answer_correct"],
                              row(reps[m]["250"], [r for r in reps[m]["250"]["records"] if r["type"] == "multi_hop"])["answer_correct"]],
        "q_emma": {v: {"words": len(em[v]["answer"].split()), "judge": em[v]["judge"]["ok"],
                       "facts_missing": em[v]["fact"].get("missing")} for v in em},
        "note_150": "the 150-word answers replayed from each method's recorded runs (RAG's were costed without thinking "
                    "tokens, so its 150 cost is lower than the race's)"}
wh = json.loads((RA / "withheld.json").read_text())
fires = {r["id"] for r in wh["rows"] if r["fires"]}
out["withheld_notice"] = {"detector": wh["detector"], "fires_on": sorted(fires),
                          "fires_by_type": {t: sum(1 for r in wh["rows"] if r["fires"] and r["type"] == t) for t in TYPES},
                          "permission_questions": 10, "per_method": {}}
for m in METHODS:
    pb = [r for r in reps[m]["250"]["records"] if r["type"] == "permission"]
    pn = [r for r in reps[m]["250n"]["records"] if r["type"] == "permission"]
    fb = [r for r in reps[m]["250"]["records"] if r["id"] in fires and r["type"] != "permission"]
    fn = [r for r in reps[m]["250n"]["records"] if r["id"] in fires and r["type"] != "permission"]
    out["withheld_notice"]["per_method"][m] = {
        "permission_correct_before": row(reps[m]["250"], pb)["answer_correct"],
        "permission_correct_after": row(reps[m]["250n"], pn)["answer_correct"],
        "false_alarms_correct_before": row(reps[m]["250"], fb)["answer_correct"] if fb else None,
        "false_alarms_correct_after": row(reps[m]["250n"], fn)["answer_correct"] if fn else None,
        "overall_before": row(reps[m]["250"])["answer_correct"], "overall_after": row(reps[m]["250n"])["answer_correct"]}

# ----------------------------------------------------------------- a measured cascade: RAG, then the hybrid only if RAG finds nothing
ABST = ("NOT IN THE DOCUMENTS",)
hy = {r["id"]: r for r in race["hybrid"]["records"]}
cas, n_fall = [], 0
for r in race["rag"]["records"]:
    if any(a in (r["answer"] or "").upper() for a in ABST):
        h = dict(hy[r["id"]])
        h["total_s"] = round(r["total_s"] + h["total_s"], 4)
        h["retrieval_s"] = round(r["retrieval_s"] + h["retrieval_s"], 4)
        h["cost_total_usd"] = round(r["cost_total_usd"] + h["cost_total_usd"], 6)
        h["nav_calls"] = (h.get("nav_calls") or 0) + 1
        cas.append(h)
        n_fall += 1
    else:
        cas.append(r)
out["cascade"] = {"rule": "answer with RAG; when RAG's answer says NOT IN THE DOCUMENTS, ask the wiki hybrid and use its "
                          "answer (latency and cost add up). Composed from the two measured runs, no new calls.",
                  "fallbacks": n_fall, **row({"records": cas}),
                  "by_type": {t: row({"records": cas}, [r for r in cas if r["type"] == t])["answer_correct"] for t in TYPES}}

# ----------------------------------------------------------------- examples, verbatim
out["examples"] = {}
for q in EXAMPLES:
    out["examples"][q] = {}
    for m in METHODS:
        r = next(x for x in race[m]["records"] if x["id"] == q)
        out["examples"][q][m] = {"answer": r["answer"], "judge": r["judge"]["ok"], "judge_reason": r["judge"]["reason"],
                                 "facts_missing": r["fact"].get("missing"), "total_s": r["total_s"],
                                 "retrieval_s": r["retrieval_s"], "cost_usd": r["cost_total_usd"],
                                 "sources": [i.get("cite") for i in r["items"][:6]]}
    if q == "Q-EMMA":
        out["examples"][q]["rag_at_150_words"] = next(x for x in reps["rag"]["150"]["records"] if x["id"] == q)["answer"]

# ----------------------------------------------------------------- spend and update cost
sp = json.loads((RA / "spend.json").read_text())
out["spend_usd"] = {"race_runs": round(sum(s.get("usd", 0) for s in sp), 4), "runs": [{k: s[k] for k in ("at", "methods", "variants", "usd")} for s in sp]}
wu = json.loads((LOGS / "wiki_update.json").read_text())
rb = json.loads((LOGS / "rag_best.json").read_text())["index"]
out["update_cost"] = {"wiki": {"pages_touched": wu.get("pages_touched"), "usd": wu.get("usd"), "facts_added": wu.get("facts_added"),
                               "note": "one changed document (RN-7.2.3-P6) re-ingested: logs/wiki_update.json"},
                      "rag": {"usd": 0.0, "note": f"no LLM: re-parse and re-chunk the changed file, rebuild BM25 "
                                                  f"({rb['bm25_build_s']} s for all {rb['n_chunks']:,} chunks, measured in the grid)"}}

# ----------------------------------------------------------------- the decision
o = out["overall"]
out["decision"] = {
    "winner": "rag",
    "behind": "Ask Northbridge ?stage=knowledge, tool search_docs (rag.rag_search with the withheld notice)",
    "why": [
        f"Latency weighs most (our rule). RAG's search takes {o['rag']['retrieval_p95_s'] * 1000:.0f} ms at p95, inside the 200 ms "
        f"target; the wiki needs the model to navigate first: {o['wiki']['retrieval_p95_s']:.1f} s (navigation) and "
        f"{o['hybrid']['retrieval_p95_s']:.1f} s (hybrid) at p95.",
        f"Time to answer, p50: RAG {o['rag']['answer_p50_s']:.1f} s against {o['hybrid']['answer_p50_s']:.1f} s for the hybrid and "
        f"{o['wiki']['answer_p50_s']:.1f} s for navigation. No method meets the 4 s p95 target: the answer model's own time "
        f"dominates (RAG p95 {o['rag']['answer_p95_s']:.1f} s).",
        f"Accuracy: the hybrid is the most accurate ({o['hybrid']['answer_correct']:.1%} judge) against RAG's "
        f"{o['rag']['answer_correct']:.1%}, about {round((o['hybrid']['answer_correct'] - o['rag']['answer_correct']) * 224)} "
        f"questions of 224, for twice the wait and {o['hybrid']['cost_per_q_usd'] / o['rag']['cost_per_q_usd']:.1f}x the cost. "
        f"Navigation alone ties RAG ({o['wiki']['answer_correct']:.1%}) at twice the wait.",
        f"Citations: RAG {o['rag']['citation_correct']:.1%}, hybrid {o['hybrid']['citation_correct']:.1%}, navigation "
        f"{o['wiki']['citation_correct']:.1%}; none reaches the 95% target.",
        f"Cost: RAG ${o['rag']['cost_per_q_usd']:.4f} a question; updating it needs no LLM, the wiki's update costs "
        f"${wu.get('usd')} and rewrites {wu.get('pages_touched')} pages per changed document.",
        "Where the wiki wins (by type) is kept as a fallback idea: the measured cascade (RAG, then the hybrid only when RAG "
        "finds nothing) is in 'cascade'. It is not shipped live: one search, one answer, inside the latency budget.",
    ],
    "targets_met": {m: {"recall@5": (o[m]["recall@5"] or 0) >= 0.90, "answer_correct": o[m]["answer_correct"] >= 0.90,
                        "citation_correct": (o[m]["citation_correct"] or 0) >= 0.95,
                        "retrieval_p95": o[m]["retrieval_p95_s"] <= 0.200, "time_to_answer_p95": o[m]["answer_p95_s"] <= 4.0}
                    for m in METHODS},
}
(LOGS / "race.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("wrote", LOGS / "race.json")
hdr = f"{'':10s}{'judge':>7s}{'fact':>7s}{'cite':>7s}{'R@5':>7s}{'ret p50':>9s}{'ret p95':>9s}{'ans p50':>9s}{'ans p95':>9s}{'$/q':>9s}"
print(hdr)
for m in METHODS + ["cascade"]:
    r = out["cascade"] if m == "cascade" else o[m]
    print(f"{m:10s}{r['answer_correct']:7.3f}{r['fact_correct']:7.3f}{r['citation_correct']:7.3f}"
          f"{(r['recall@5'] or 0):7.3f}{r['retrieval_p50_s']:9.3f}{r['retrieval_p95_s']:9.3f}{r['answer_p50_s']:9.2f}"
          f"{r['answer_p95_s']:9.2f}{r['cost_per_q_usd']:9.4f}")
print("\nby type (judge):", " ".join(f"{m:>9s}" for m in METHODS), "  cascade")
for t in TYPES:
    print(f"{t:17s}", " ".join(f"{out['by_type'][t][m]['answer_correct']:9.3f}" for m in METHODS), f"  {out['cascade']['by_type'][t]:.3f}",
          f"(n={out['by_type'][t]['rag']['n']})")
print("\ncap 150->250:", {m: v["answer_correct"] for m, v in out["cap_150_vs_250"].items()})
print("Q-EMMA words/judge/missing:", {m: v["q_emma"] for m, v in out["cap_150_vs_250"].items()})
print("withheld:", json.dumps(out["withheld_notice"]["per_method"]))
print("spend:", out["spend_usd"]["race_runs"])
