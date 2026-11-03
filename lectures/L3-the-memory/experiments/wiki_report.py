"""Fold the golden-set runs of the wiki methods into logs/wiki_eval.json (the slide tables), from the logged runs only.

    python3 wiki_report.py        # reads logs/wiki_eval_{wiki,hybrid,hybrid-search}.json, writes logs/wiki_eval.json
"""
import json
import pathlib
from collections import Counter

LOGS = pathlib.Path(__file__).resolve().parent / "logs"
TYPES = ["single_lookup", "procedure", "rule", "service_field", "table_lookup", "multi_hop", "version_conflict",
         "exact_code", "not_in_docs", "permission"]
LABEL = {"wiki": "LLM Wiki (index navigation)", "hybrid": "Hybrid (search wiki sections, then navigate)",
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

    def row(rs, agg):
        calls = [(r.get("chain") or {}).get("nav_calls", 0) + 1 for r in rs]
        return {"n": agg.get("n"), "answer_correct": agg.get("answer_correct"), "fact_correct": agg.get("fact_correct"),
                "citation_correct": agg.get("citation_correct"), "citation_precision": agg.get("citation_precision"),
                "retrieval_p50_s": (agg.get("retrieval_s") or {}).get("p50"),
                "retrieval_p95_s": (agg.get("retrieval_s") or {}).get("p95"),
                "answer_p50_s": (agg.get("total_s") or {}).get("p50"), "answer_p95_s": (agg.get("total_s") or {}).get("p95"),
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
    for kind in ("wiki", "hybrid", "hybrid-search"):
        p = LOGS / f"wiki_eval_{kind}.json"
        if not p.exists():
            res["methods"][kind] = {"label": LABEL[kind], "status": "NOT RUN"}
            continue
        rep = json.loads(p.read_text())
        res["methods"][kind] = {"label": LABEL[kind], "answer_model": rep.get("answer_model"),
                                "shards": rep.get("shards"), "wall_seconds": rep.get("wall_seconds"), **table(rep)}
    (LOGS / "wiki_eval.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for k, m in res["methods"].items():
        if "overall" in m:
            o = m["overall"]
            print(f"{k:14s} acc {o['answer_correct']} fact {o['fact_correct']} cite {o['citation_correct']} "
                  f"p50 {o['answer_p50_s']}s p95 {o['answer_p95_s']}s calls {o['llm_calls_mean']} ${o['cost_per_q_usd']}")


if __name__ == "__main__":
    main()
