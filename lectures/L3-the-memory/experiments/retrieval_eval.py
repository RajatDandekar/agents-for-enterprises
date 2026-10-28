"""Lecture 3 experiment, part 1: the corpus, its cost, and retrieval alone (no chat-model calls).

Re-run on 2026-10-28 with the current bahi/agent/retrieval.py (TAU = 0), because v2's logs were made before the
last edit to that file (v2 log says TAU -2.0). Questions and grader are v2's (questions.py, copied unchanged).

Measures, for Kavita Joshi (KJOSHI, PUR-EXEC) on Monday 26 October 2026:
  corpus      words, section chunks, fixed-size chunks and Gemini token counts per document; the full-corpus prompt;
              the whole company's documents (Rasoi purchasing + the 8 module kits) for the scale argument
  chunking    POL-PUR-001 body + clause boundaries (the deck's chunker slider); section vs fixed-120 retrieval
  bm25        Kavita's Shakti question and scenario-1 question: tokens, df, idf, tf, term scores, top 8
  vectors     cosine top 8; the query and §6.2 vectors for the worked cosine; a 2-D PCA of all chunk vectors
  hybrid      RRF and rerank for both questions; recall@1/3/5/10 and MRR on the 33 gold questions, 4 methods
  tau         top reranker score, answerable vs unanswerable
  leak        HR chunks retrieved with and without the permission filter
Writes logs/retrieval_eval.json.  Run:  modal run tools/modal_run.py --script lectures/L3-the-memory/experiments/retrieval_eval.py
"""
import json, math, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from questions import Q
from bahi.agent import retrieval as R
from bahi.course import l3
from bahi.scenarios import SCENARIOS

OUT = pathlib.Path(__file__).parent / "logs"; OUT.mkdir(exist_ok=True)
docs = R.load_corpus()
K = R.clearance_for("KJOSHI")
ret = l3.retriever("KJOSHI")
ret_noperm = l3.retriever("KJOSHI", permissions=False)
ret_nofresh = l3.retriever("KJOSHI", freshness=False)
log = {"date": "2026-10-28", "code": "bahi/agent/retrieval.py (TAU=%s), bahi/course/l3" % R.TAU,
       "n_chunks_kavita": len(ret.chunks), "n_chunks_all": len(ret_noperm.chunks), "embed_model": R.EMBED_MODEL,
       "rerank_model": R.RERANK_MODEL, "embed_dim": len(ret.vecs[0])}

# ------------------------------------------------------------------ corpus and tokens
log["corpus"] = []
for d in docs:
    log["corpus"].append({"doc_id": d.doc_id, "title": d.title, "version": d.version, "effective": d.effective,
                          "audience": d.audience, "amends": d.amends, "words": len(d.body.split()),
                          "chunks": len(R.chunk_by_section(d)), "fixed120_chunks": len(R.chunk_fixed(d)),
                          "tokens": l3.count_tokens(d.body), "kavita_may_read": R.allowed(d, K)})
VISIBLE = [d for d in docs if R.allowed(d, K)]
FULL_CTX = "\n\n".join(
    f"===== {d.doc_id}: {d.title} v{d.version}, effective {d.effective}"
    + (f", amends {', '.join(d.amends)}" if d.amends else "") + f" =====\n{d.body}" for d in VISIBLE)
kit_docs = []
for p in sorted((R.PKG / "modules").glob("*/docs")):
    for d in R.load_corpus(p):
        kit_docs.append((p.parent.name, d))
COMPANY_CTX = FULL_CTX + "\n\n" + "\n\n".join(
    f"===== {d.doc_id}: {d.title} v{d.version}, effective {d.effective} =====\n{d.body}" for _, d in kit_docs)
log["full_ctx"] = {"docs": len(VISIBLE), "words": len(FULL_CTX.split()), "tokens": l3.count_tokens(FULL_CTX)}
log["company_ctx"] = {"docs": len(VISIBLE) + len(kit_docs), "kits": sorted({k for k, _ in kit_docs}),
                      "words": len(COMPANY_CTX.split()), "tokens": l3.count_tokens(COMPANY_CTX)}
(OUT / "company_ctx.txt").write_text(COMPANY_CTX)   # e3 reads it, so both runs paste the same text

# ------------------------------------------------------------------ chunking: the slider's data + one real chunk
pp = next(d for d in docs if d.doc_id == "POL-PUR-001")
words = pp.body.split()
starts = []  # (word index, label) where a heading or clause starts
pos = 0
for line in pp.body.splitlines():
    w = line.split()
    if not w:
        continue
    m = re.match(r"^(#+)\s+(\d+)\.?\s", line) or re.match(r"^(\d+\.\d+)\s", line)
    if line.startswith("## "):
        starts.append([pos, "§" + w[1].rstrip(".")])
    elif re.match(r"^\d+\.\d+\s", line):
        starts.append([pos, "§" + w[0]])
    pos += len(w)
c62 = next(c for c in R.chunk_by_section(pp) if c.section == "6.2")
log["chunking"] = {"doc": "POL-PUR-001", "words": words, "starts": starts, "c62_render": c62.render(),
                   "c62_context_text": c62.context_text, "c62_words": len(c62.text.split()),
                   "fixed120": [{"id": c.id, "text": c.text} for c in R.chunk_fixed(pp, 120, 20)],
                   "section_ids": [c.id for c in R.chunk_by_section(pp)]}

# ------------------------------------------------------------------ section vs fixed-120 chunks, measured
norm = lambda s: " ".join(s.split())
all_sec = {c.id: c for d in docs for c in R.chunk_by_section(d)}
fixed = [c for d in VISIBLE for c in R.chunk_fixed(d, 120, 20)]
fx_bm = R.BM25([R.tokenize(c.text) for c in fixed])
fx_vec = ret.embedder.embed([c.text for c in fixed])
gold_q = [q for q in Q if q["gold"]]


def fixed_hits(q, k=5):
    qt = R.tokenize(q["q"])
    s = fx_bm.scores(qt)
    b = sorted(range(len(fixed)), key=lambda i: -s[i])
    qv = ret.embedder.embed([q["q"]], kind="query")[0]
    v = sorted(range(len(fixed)), key=lambda i: -R.cosine(qv, fx_vec[i]))
    f = R.rrf([b[:20], v[:20]])
    h = sorted(f, key=lambda i: -f[i])
    out = {}
    for name, order in (("bm25", b), ("vector", v), ("hybrid", h)):
        top = [norm(fixed[i].text) for i in order[:k]]
        golds = [norm(re.sub(r"^\d+\.\d+\s+", "", all_sec[g].text)) for g in q["gold"] if g in all_sec]
        whole = any(g in t for g in golds for t in top)
        start = any(" ".join(g.split()[:8]) in t for g in golds for t in top)
        out[name] = {"whole": whole, "start": start}
    return out


fx = {q["id"]: fixed_hits(q) for q in gold_q}
log["fixed_vs_section"] = {
    "n": len(gold_q), "n_fixed_chunks": len(fixed), "n_section_chunks": len(ret.chunks),
    "fixed_top5": {m: {"whole_clause": sum(fx[i][m]["whole"] for i in fx), "clause_start": sum(fx[i][m]["start"] for i in fx)}
                   for m in ("bm25", "vector", "hybrid")},
    "note": "fixed: a gold clause counts as found if its full text (or only its first 8 words, 'clause_start') is inside one "
            "of the top-5 windows. section: the gold clause id is in the top 5 (see summary). Fixed windows carry no citation."}

# ------------------------------------------------------------------ the four rankings, measured on 33 gold questions
modes = ["bm25", "vector", "hybrid", "hybrid+rerank"]
rows = []
for q in Q:
    row = {"id": q["id"], "kind": q["kind"], "q": q["q"], "gold": q["gold"]}
    for m in modes:
        hits = ret.search(q["q"], k=10, mode=m)
        ids = [h.chunk.id for h in hits]
        rank = next((i + 1 for i, c in enumerate(ids) if c in q["gold"]), None)
        row[m] = {"top5": ids[:5], "gold_rank": rank}
    row["tool_scores"] = [h.score for h in ret.search(q["q"], k=4)]
    if q["kind"] == "perm":
        row["noperm_top5"] = [h.chunk.id for h in ret_noperm.search(q["q"], k=5)]
        row["noperm_hr_in_top5"] = any(c.startswith("HR-") for c in row["noperm_top5"])
        row["perm_hr_in_top5"] = any(c.startswith("HR-") for c in row["hybrid+rerank"]["top5"])
    if q["kind"] == "fresh":
        row["nofresh_top5"] = [h.chunk.id for h in ret_nofresh.search(q["q"], k=5)]
    rows.append(row)
log["questions"] = rows
gq = [r for r in rows if r["gold"]]
log["summary"] = {m: {"n": len(gq), **{f"recall@{k}": round(sum(1 for r in gq if r[m]["gold_rank"] and r[m]["gold_rank"] <= k) / len(gq), 3)
                                     for k in (1, 3, 5, 10)},
                      "mrr": round(sum(1 / r[m]["gold_rank"] for r in gq if r[m]["gold_rank"]) / len(gq), 3)} for m in modes}
ans = [r["tool_scores"][0] for r in gq if r["tool_scores"]]
una = [r["tool_scores"][0] for r in rows if not r["gold"] and r["tool_scores"]]
log["tau"] = {"TAU": R.TAU, "answerable_top": sorted(ans), "unanswerable_top": sorted(una),
              "per_question": [{"id": r["id"], "kind": r["kind"], "top": (r["tool_scores"] or [None])[0]} for r in rows]}
log["leak"] = {"with_filter": sum(r.get("perm_hr_in_top5", False) for r in rows),
               "without_filter": sum(r.get("noperm_hr_in_top5", False) for r in rows)}


# ------------------------------------------------------------------ two questions, zoomed in
def zoom(question):
    qt = R.tokenize(question)
    N = ret.bm25.N
    df = {t: sum(1 for tf in ret.bm25.tf if t in tf) for t in dict.fromkeys(qt)}
    i62 = next(i for i, c in enumerate(ret.chunks) if c.id == "POL-PUR-001 §6.2")
    b = ret.bm25_rank(question)
    v = ret.vector_rank(question)
    qv = ret.embedder.embed([question], kind="query")[0]
    return {"question": question, "tokens": qt, "N": N, "avgdl": round(ret.bm25.avgdl, 2),
            "df": df, "idf": {t: round(ret.bm25.idf.get(t, 0), 3) for t in df},
            "c62": {"dl": ret.bm25.dl[i62], "tf": {t: ret.bm25.tf[i62].get(t, 0) for t in df},
                    "terms": {t: round(x, 3) for t, x in ret.bm25.term_scores(qt, i62).items()},
                    "bm25_rank": next((r for r, (i, _) in enumerate(b, 1) if i == i62), None),
                    "vec_rank": next((r for r, (i, _) in enumerate(v, 1) if i == i62), None),
                    "cos": round(R.cosine(qv, ret.vecs[i62]), 4)},
            "bm25": [{"id": ret.chunks[i].id, "score": round(s, 3), "head": ret.chunks[i].heading[:70],
                      "terms": {t: round(x, 2) for t, x in ret.bm25.term_scores(qt, i).items()}} for i, s in b[:8]],
            "vector": [{"id": ret.chunks[i].id, "cos": round(s, 4), "head": ret.chunks[i].heading[:70]} for i, s in v[:8]],
            "hybrid": [{"id": h.chunk.id, **h.why} for h in ret.search(question, k=8, mode="hybrid")],
            "rerank": [{"id": h.chunk.id, **h.why} for h in ret.search(question, k=8)],
            "qvec": [round(x, 4) for x in qv], "c62vec": [round(x, 4) for x in ret.vecs[i62]],
            "qnorm": round(math.sqrt(sum(x * x for x in qv)), 4), "c62norm": round(math.sqrt(sum(x * x for x in ret.vecs[i62])), 4)}


log["shakti"] = zoom(l3.SHAKTI)
log["s1"] = zoom(SCENARIOS[0].ask)
log["shakti_tool"] = l3.policy_search("KJOSHI").search(l3.SHAKTI)

# ------------------------------------------------------------------ 2-D projection of every chunk vector
X = np.array(ret_noperm.vecs)
mu = X.mean(0)
U, S, Vt = np.linalg.svd(X - mu, full_matrices=False)
P = (X - mu) @ Vt[:2].T
qs = {"shakti": l3.SHAKTI, "M01": Q[20]["q"], "T01": Q[35]["q"], "P13": Q[12]["q"]}
qv = {k: (np.array(ret.embedder.embed([t], kind="query")[0]) - mu) @ Vt[:2].T for k, t in qs.items()}
q1 = np.array(ret.embedder.embed([l3.SHAKTI], kind="query")[0])
log["pca"] = {"explained": [round(float(x), 4) for x in (S[:2] ** 2 / (S ** 2).sum())],
              "points": [[c.id, c.doc_id, round(float(p[0]), 4), round(float(p[1]), 4),
                          round(float(q1 @ np.array(x) / (np.linalg.norm(q1) * np.linalg.norm(x))), 4)]
                         for c, p, x in zip(ret_noperm.chunks, P, X)],
              "queries": {k: {"text": qs[k], "x": round(float(p[0]), 4), "y": round(float(p[1]), 4)} for k, p in qv.items()}}

(OUT / "retrieval_eval.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
print(json.dumps(log["summary"], indent=1))
print("fixed vs section", log["fixed_vs_section"]["fixed_top5"])
print("full ctx", log["full_ctx"], "company", {k: v for k, v in log["company_ctx"].items() if k != "kits"})
print("tau", log["tau"]["answerable_top"][:3], log["tau"]["unanswerable_top"][-3:], "leak", log["leak"])
for k in ("shakti", "s1"):
    z = log[k]
    print(k, z["tokens"], "c62", z["c62"]["bm25_rank"], z["c62"]["vec_rank"], z["c62"]["cos"])
    print("  bm25", [(x["id"], x["score"]) for x in z["bm25"][:5]])
    print("  vec ", [(x["id"], x["cos"]) for x in z["vector"][:5]])
    print("  rrr ", [(x["id"], x["rerank"]) for x in z["rerank"][:5]])
print("tool", [(c["cite"], c["score"]) for c in log["shakti_tool"]["clauses"]], log["shakti_tool"]["answer_in_documents"])
for r in rows:
    print(r["id"], [r[m]["gold_rank"] for m in modes], r["hybrid+rerank"]["top5"][:2])
