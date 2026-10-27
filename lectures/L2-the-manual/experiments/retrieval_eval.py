"""Lecture 2, part 1 of the experiment: retrieval alone, no model calls.

For the 40 questions: where does the gold clause land under BM25, embeddings, hybrid (RRF) and hybrid + rerank?
Also: the reranker's top score for answerable vs unanswerable questions (to set TAU), the permission filter at
retrieval time, the scenario-1 query's three rankings, and a 2-D projection of the real chunk vectors.
Writes logs/retrieval_eval.json and fills the embedding/rerank caches in bahi/docs/_index/.
"""
import json, pathlib, statistics, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from questions import Q
from bahi.agent.retrieval import (Retriever, load_corpus, chunk_by_section, chunk_fixed, tokenize, Embedder,
                                  clearance_for, TAU)
from bahi.scenarios import SCENARIOS

OUT = pathlib.Path(__file__).parent / "logs"; OUT.mkdir(exist_ok=True)
docs = load_corpus()
R = Retriever("KJOSHI")
R_noperm = Retriever("KJOSHI", permissions=False)
R_nofresh = Retriever("KJOSHI", freshness=False)
log = {"corpus": [], "n_chunks_kavita": len(R.chunks), "n_chunks_all": len(R_noperm.chunks)}
for d in docs:
    cs = chunk_by_section(d)
    log["corpus"].append({"doc_id": d.doc_id, "title": d.title, "version": d.version, "effective": d.effective,
                          "audience": d.audience, "amends": d.amends, "words": len(d.body.split()), "chunks": len(cs),
                          "fixed120_chunks": len(chunk_fixed(d))})
modes = ["bm25", "vector", "hybrid", "hybrid+rerank"]
rows = []
for q in Q:
    row = {"id": q["id"], "kind": q["kind"], "q": q["q"], "gold": q["gold"]}
    for m in modes:
        hits = R.search(q["q"], k=10, mode=m)
        ids = [h.chunk.id for h in hits]
        rank = next((i + 1 for i, c in enumerate(ids) if c in q["gold"]), None)
        row[m] = {"top5": ids[:5], "gold_rank": rank, "top_score": round(hits[0].score, 4) if hits else None}
    hits = R.search(q["q"], k=4)
    row["tool_scores"] = [h.score for h in hits]
    if q["kind"] == "perm":
        row["noperm_top5"] = [h.chunk.id for h in R_noperm.search(q["q"], k=5)]
        row["noperm_hr_in_top5"] = any(c.startswith("HR-") for c in row["noperm_top5"])
        row["perm_hr_in_top5"] = any(c.startswith("HR-") for c in row["hybrid+rerank"]["top5"])
    if q["kind"] == "fresh":
        row["nofresh_top5"] = [h.chunk.id for h in R_nofresh.search(q["q"], k=5)]
    rows.append(row)
log["questions"] = rows
gold_q = [r for r in rows if r["gold"]]
summ = {}
for m in modes:
    rk = [r[m]["gold_rank"] for r in gold_q]
    summ[m] = {"n": len(rk), **{f"recall@{k}": round(sum(1 for x in rk if x and x <= k) / len(rk), 3) for k in (1, 3, 5, 10)},
               "mrr": round(sum(1 / x for x in rk if x) / len(rk), 3)}
log["summary"] = summ
ans = [r["tool_scores"][0] for r in gold_q]
una = [r["tool_scores"][0] for r in rows if not r["gold"]]
log["tau"] = {"TAU": TAU, "answerable_top": sorted(ans), "unanswerable_top": sorted(una),
              "answerable_below_tau": sum(1 for x in ans if x < TAU), "unanswerable_above_tau": sum(1 for x in una if x >= TAU)}
log["leak"] = {"with_filter_hr_chunks_retrieved": sum(r.get("perm_hr_in_top5", False) for r in rows),
               "without_filter_hr_chunks_retrieved": sum(r.get("noperm_hr_in_top5", False) for r in rows)}
# ---- scenario 1: the three rankings side by side, with real scores
s1 = SCENARIOS[0].ask
b = R.bm25_rank(s1)[:8]
v = R.vector_rank(s1)[:8]
qt = tokenize(s1)
log["s1"] = {"question": s1, "tokens": qt,
             "bm25": [{"id": R.chunks[i].id, "score": round(s, 3), "terms": {t: round(x, 2) for t, x in R.bm25.term_scores(qt, i).items()}} for i, s in b],
             "vector": [{"id": R.chunks[i].id, "cos": round(s, 4)} for i, s in v],
             "hybrid": [{"id": h.chunk.id, **h.why} for h in R.search(s1, k=8, mode="hybrid")],
             "rerank": [{"id": h.chunk.id, **h.why} for h in R.search(s1, k=8)]}
# ---- 2-D projection (PCA) of every chunk vector, Kavita's question projected on the same axes
emb = Embedder()
allc = R_noperm.chunks
X = np.array(R_noperm.vecs)
mu = X.mean(0)
U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
P = (X - mu) @ Vt[:2].T
qs = {"s1": s1, "P03": Q[2]["q"], "M01": Q[20]["q"], "T01": Q[35]["q"]}
qv = {k: (np.array(emb.embed([t], kind="query")[0]) - mu) @ Vt[:2].T for k, t in qs.items()}
q1 = np.array(emb.embed([s1], kind="query")[0])
cos = [float(q1 @ np.array(x) / (np.linalg.norm(q1) * np.linalg.norm(x))) for x in X]
log["pca"] = {"explained": [round(float(x), 4) for x in (S[:2] ** 2 / (S ** 2).sum())],
              "points": [{"id": c.id, "doc": c.doc_id, "x": round(float(p[0]), 4), "y": round(float(p[1]), 4),
                          "cos_s1": round(cos[i], 4), "head": c.heading[:60]} for i, (c, p) in enumerate(zip(allc, P))],
              "queries": {k: {"text": qs[k], "x": round(float(p[0]), 4), "y": round(float(p[1]), 4)} for k, p in qv.items()}}
log["embed_dim"] = len(R.vecs[0])
(OUT / "retrieval_eval.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
print(json.dumps(summ, indent=1)); print(json.dumps(log["tau"], indent=1)); print(log["leak"])
for r in rows:
    print(r["id"], [r[m]["gold_rank"] for m in modes], r["hybrid+rerank"]["top5"][:3], r["tool_scores"][:2])
