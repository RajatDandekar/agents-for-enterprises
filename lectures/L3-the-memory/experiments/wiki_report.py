"""Fold the golden-set runs of the wiki methods into logs/wiki_eval.json (the slide tables), from the logged runs only.

    python3 wiki_report.py        # reads logs/wiki_eval_{wiki,hybrid,hybrid-search}.json, writes logs/wiki_eval.json
"""
import json
import pathlib
from collections import Counter

LOGS = pathlib.Path(__file__).resolve().parent / "logs"
TYPES = ["single_lookup", "procedure", "rule", "service_field", "table_lookup", "multi_hop", "version_conflict",
         "exact_code", "not_in_docs", "permission"]
LATENCY_NOTE = ("Latency = recorded API seconds of every LLM call on the question's path (navigation calls + the answer "
                "call) + measured section-search time. Navigation calls replayed from cassettes keep their original "
                "seconds, so replayed and live questions are timed the same way; 429 waits are excluded. The harness's "
                "own wall-clock retrieval_s is ~0 for replayed questions and is kept only as harness_wall_retrieval_p50_s.")
LABEL = {"wiki-rules": "LLM Wiki + rules that apply (multi-hop subset only)", "wiki": "LLM Wiki (index navigation)", "hybrid": "Hybrid (search wiki sections, then navigate)",
         "hybrid-search": "Wiki sections as RAG units (search only, no navigation)"}


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * q / 100
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 3)


def table(rep):
    recs = rep["records"]
    s = rep["summary"]

    def api_lat(r):
        c = r.get("chain") or {}
        nav = sum(x.get("llm_seconds") or 0 for x in c.get("calls") or []) + (c.get("search_ms") or 0) / 1000
        return nav, nav + (r.get("llm_seconds") or 0)

    def row(rs, agg):
        calls = [(r.get("chain") or {}).get("nav_calls", 0) + 1 for r in rs]
        lat = [api_lat(r) for r in rs]
        return {"n": agg.get("n"), "answer_correct": agg.get("answer_correct"), "fact_correct": agg.get("fact_correct"),
                "citation_correct": agg.get("citation_correct"), "citation_precision": agg.get("citation_precision"),
                "retrieval_p50_s": pct([x[0] for x in lat], 50), "retrieval_p95_s": pct([x[0] for x in lat], 95),
                "answer_p50_s": pct([x[1] for x in lat], 50), "answer_p95_s": pct([x[1] for x in lat], 95),
                "harness_wall_retrieval_p50_s": (agg.get("retrieval_s") or {}).get("p50"),
                "llm_calls_mean": round(sum(calls) / len(calls), 2) if calls else None,
                "llm_calls_max": max(calls) if calls else None, "cost_per_q_usd": agg.get("cost_per_q_usd"),
                "tokens_in_per_q": agg.get("tokens_in_per_q"), "tokens_out_per_q": agg.get("tokens_out_per_q")}

    out = {"overall": row(recs, s["overall"]),
           "by_type": {t: row([r for r in recs if r["type"] == t], s["by_type"][t]) for t in TYPES},
           "retrieval": {k: s["retrieval"]["overall"].get(k) for k in ("n", "mrr", "recall@1", "recall@3", "recall@5",
                                                                       "recall@10", "fact_recall@5", "coverage@5")},
           "retrieval_by_type": {t: {k: s["retrieval"]["by_type"][t].get(k) for k in ("n", "recall@5", "mrr",
                                                                                     "fact_recall@5")}
                                 for t in TYPES},
           "match_levels": s["retrieval"].get("match_levels"), "judge_vs_fact": s.get("judge_vs_fact"),
           "judge_cost_usd": s.get("judge_cost_usd")}
    steps = Counter()
    for r in recs:
        for c in (r.get("chain") or {}).get("chain") or []:
            steps[c["step"]] += 1
    out["chain_steps_total"] = dict(steps)
    out["pages_opened_mean"] = round(sum(len((r.get("chain") or {}).get("opened") or []) for r in recs) / len(recs), 2)
    out["sources_opened_mean"] = round(sum(len((r.get("chain") or {}).get("sources") or []) for r in recs) / len(recs), 2)
    wrong = [{"id": r["id"], "type": r["type"], "why": r["judge"].get("reason"), "missing": r["fact"].get("missing")}
             for r in recs if not r["judge"]["ok"]]
    out["wrong"] = wrong
    return out


def main():
    res = {"note": "Every number here is computed from the logged golden-set runs (records in wiki_eval_<method>.json). "
                   "Same harness (ledgerline/course/l3/evaluate.py), answer model, prompt, judge and prices as RAG.",
           "methods": {}}
    res["latency_note"] = LATENCY_NOTE
    for kind in ("wiki", "hybrid", "hybrid-search", "wiki-rules"):
        p = LOGS / f"wiki_eval_{kind}.json" if kind != "wiki-rules" else LOGS / "wiki_eval_wiki-rules_21.json"
        if not p.exists():
            res["methods"][kind] = {"label": LABEL[kind], "status": "NOT RUN"}
            continue
        rep = json.loads(p.read_text())
        provs = {}
        res["methods"][kind] = {"label": LABEL[kind], "answer_model": rep.get("answer_model"),
                                "provider_live_calls": rep.get("provider_live_calls", "openrouter"),
                                "live_calls_this_run": rep.get("live_calls_this_run"),
                                "live_usd_this_run": rep.get("live_usd_this_run"),
                                "replayed_calls_this_run": rep.get("replayed_calls_this_run"),
                                "shards": rep.get("shards"), "wall_seconds": rep.get("wall_seconds"), **table(rep)}
    # navigation methods whose golden-set run stopped at the answer step (OpenRouter key out of credit, HTTP 402):
    # retrieval scored by replaying the recorded navigation calls (no new calls), compared on the same questions
    hs = json.loads((LOGS / "wiki_eval_hybrid-search.json").read_text()) if (LOGS / "wiki_eval_hybrid-search.json").exists() else None
    hs_by = {r["id"]: r for r in hs["records"]} if hs else {}
    for kind in ("wiki", "hybrid"):
        p = LOGS / f"wiki_eval_{kind}_retrieval_replay.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        recs = d["records"]
        ids = [r["id"] for r in recs if r["retrieval"]["n_gold"]]

        def agg(rs):
            rs = [r for r in rs if r["n_gold"]]
            if not rs:
                return {"n": 0}
            return {"n": len(rs), "recall@1": round(sum(r["hit@1"] for r in rs) / len(rs), 4),
                    "recall@5": round(sum(r["hit@5"] for r in rs) / len(rs), 4),
                    "recall@10": round(sum(r["hit@10"] for r in rs) / len(rs), 4),
                    "mrr": round(sum(r["rr"] for r in rs) / len(rs), 4)}

        lat = [r["retrieval_s"] for r in recs]
        calls = [r["nav_calls"] for r in recs]
        res["methods"].setdefault(kind + "_replay_3nov", {})
        res["methods"][kind + "_replay_3nov"] = {"label": LABEL[kind] + ", retrieval replay before the provider switch",
            "status": "SUPERSEDED by the full run above; kept for the record. PARTIAL: navigation ran for every question; the run stopped before the shared answer step "
                      "(OpenRouter key limit, HTTP 402). Retrieval below is from replaying the recorded calls; "
                      "answer accuracy, citations and end-to-end latency were NOT measured.",
            "n_questions_scored": d["n_scored"], "n_questions_missing": d["n_missing"],
            "retrieval": agg([r["retrieval"] for r in recs]),
            "retrieval_by_type": {t: agg([r["retrieval"] for r in recs if r["type"] == t]) for t in TYPES},
            "retrieval_latency_s": {"p50": pct(lat, 50), "p95": pct(lat, 95),
                                    "note": "sum of the recorded per-call API seconds of the navigation calls "
                                            "(+ section search for the hybrid); excludes 429 waits"},
            "llm_calls_navigation_mean": round(sum(calls) / len(calls), 2), "llm_calls_navigation_max": max(calls),
            "llm_calls_per_answer_mean": round(sum(calls) / len(calls) + 1, 2),
            "tokens_in_navigation_mean": d["tokens_in_mean"], "navigation_cost_per_q_usd": d["nav_cost_per_q_usd"],
            "hybrid_search_on_same_questions": agg([hs_by[i]["retrieval"] for i in ids if i in hs_by]) if hs_by else None,
            "chain_steps_total": dict(Counter(c["step"] for r in recs for c in (r.get("chain") or [])))}
    (LOGS / "wiki_eval.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    ab = LOGS / "wiki_provider_ab.json"
    if ab.exists():
        a = json.loads(ab.read_text())
        res["answer_model_consistency"] = {k: a[k] for k in ("provider_a", "provider_b", "n", "same_retrieved_items",
                                                            "judge_agree", "summary")}
    for k, m in res["methods"].items():
        if "overall" in m:
            o = m["overall"]
            print(f"{k:14s} acc {o['answer_correct']} fact {o['fact_correct']} cite {o['citation_correct']} "
                  f"p50 {o['answer_p50_s']}s p95 {o['answer_p95_s']}s calls {o['llm_calls_mean']} ${o['cost_per_q_usd']}")


if __name__ == "__main__":
    main()
