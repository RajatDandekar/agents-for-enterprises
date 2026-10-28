"""Lecture 3 experiment, part 4: full corpus vs RAG vs the LLM wiki on the 40 questions, graded by code.

Adapted from v2's experiments/rag_vs_wiki.py (archive/v2/lectures/L2-the-manual), re-run on 2026-10-28 because v2's
answers were recorded before the last edit to bahi/agent/retrieval.py (TAU -2.0 then, 0 now), so the RAG prompts
differ. Changes from v2: L3's caches (bahi.course.l3), a new cassette (L3v3_eval), and one more system,
'company': every document of the whole company (Rasoi purchasing + the 8 module kits, HR page still excluded),
to see what pasting everything costs as the corpus grows. Questions and grader are v2's, unchanged.

Systems (gemini-3.8-flash, temperature 0, the same answer instructions R.ANSWER_SYSTEM):
  closed   the model alone, no documents
  full     every document Kavita may read, pasted whole (about 13,000 tokens)
  company  the whole company's documents pasted whole (about 28,000 tokens)
  rag      search_policy: hybrid BM25 + embeddings, RRF, rerank, top 4 clauses, permissions and freshness
  wiki     the compiled wiki (bahi/wiki, compiled in v2: logs/v2_wiki_compile.json): index, pick up to 3 pages, answer
Ablations: rag without the permission filter, rag without freshness, the wiki before the amendments, an HR control.
Writes logs/answers_eval.json.
"""

import json, pathlib, statistics, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from questions import Q, HR_CONTROL, grade
from bahi.agent.retrieval import (PolicySearch, Retriever, Wiki, load_corpus, chunk_by_section, allowed, clearance_for,
                                  answer_with, build_context, check_citations, extract_citations, erp_fact, WIKI_DIR,
                                  ANSWER_SYSTEM)
from bahi.course import l3
from bahi.llm import LLM

MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemini:gemini-3.8-flash"
HERE = pathlib.Path(__file__).parent
OUT = HERE / "logs"; OUT.mkdir(exist_ok=True)
docs = load_corpus()
K = clearance_for("KJOSHI")
ALL_IDS = {c.id for d in docs for c in chunk_by_section(d)}
VISIBLE = [d for d in docs if allowed(d, K)]
VIS_IDS = {c.id for d in VISIBLE for c in chunk_by_section(d)}
HR_IDS = {c.id for d in docs if d.doc_id.startswith("HR-") for c in chunk_by_section(d)}

CLOSED_SYSTEM = """You answer questions from purchase staff at Rasoi Steel Works, Pune, a pressure-cooker maker that runs Bahi ERP 7.2.
Today is 26 October 2026.
- Begin with the direct answer in one sentence (start with Yes or No when the question is yes/no).
- Cite the company rule you rely on as [DOC-ID §section] when you can.
- If you do not know, begin your reply with NOT IN DOCUMENTS.
- At most four sentences."""
FULL_CTX = "\n\n".join(
    f"===== {d.doc_id}: {d.title} v{d.version}, effective {d.effective}"
    + (f", amends {', '.join(d.amends)}" if d.amends else "") + f" =====\n{d.body}" for d in VISIBLE)

llms = {s: LLM(MODEL, cassette="L3v3_eval", max_tokens=4096) for s in
        ("closed", "full", "company", "rag", "wiki", "rag_noperm", "rag_nofresh", "wiki_stale", "control")}
ps = l3.policy_search("KJOSHI", route_facts=False)
ps_noperm = l3.policy_search("KJOSHI", route_facts=False, permissions=False)
ps_nofresh = l3.policy_search("KJOSHI", route_facts=False, freshness=False)
ps_hr = PolicySearch("HR-USER", route_facts=False, retriever=l3.retriever(None, clearance=clearance_for(role="HR")))
COMPANY_CTX = (OUT / "company_ctx.txt").read_text()   # written by retrieval_eval.py
wiki = Wiki(WIKI_DIR)
stale = Wiki(HERE / "wiki_before_amendments")

# retrieval first, single-threaded (it may fill caches); model calls after, in parallel
pre = {}
for q in Q:
    pre[("rag", q["id"])] = ps.search(q["q"])
    if q["kind"] == "perm":
        pre[("rag_noperm", q["id"])] = ps_noperm.search(q["q"])
    if q["kind"] == "fresh":
        pre[("rag_nofresh", q["id"])] = ps_nofresh.search(q["q"])
pre[("control", HR_CONTROL["id"])] = ps_hr.search(HR_CONTROL["q"])


def run(system, q):
    llm = llms[system]
    if system == "closed":
        r = llm.chat([{"role": "system", "content": CLOSED_SYSTEM}, {"role": "user", "content": q["q"]}])
        out = {"answer": r.content or "", "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
               "context_ids": []}
    elif system == "full":
        out = answer_with(llm, q["q"], FULL_CTX)
        out["context_ids"] = sorted(VIS_IDS)
    elif system == "company":
        out = answer_with(llm, q["q"], COMPANY_CTX)
        out["context_ids"] = sorted(VIS_IDS)
    elif system in ("rag", "rag_noperm", "rag_nofresh", "control"):
        res = pre[(system, q["id"])]
        ctx = build_context(res["clauses"]) if res["clauses"] else f"(no extracts) {res['note']}"
        out = answer_with(llm, q["q"], ctx)
        out["context_ids"] = [c["cite"] for c in res["clauses"]]
        out["clause_scores"] = [c["score"] for c in res["clauses"]]
    elif system == "wiki":
        out = wiki.answer(q["q"], llm, "KJOSHI")
    elif system == "wiki_stale":
        out = stale.answer(q["q"], llm, "KJOSHI")
    elif system == "wiki_control":
        out = wiki.answer(q["q"], llm, clearance=clearance_for(role="HR"))
    out.pop("context", None)
    cc = check_citations(out["answer"], out["context_ids"], ALL_IDS)
    g = grade(q, out["answer"], cc["cites"])
    out["context_has_gold"] = (any(c in q["gold"] for c in out["context_ids"]) if q["gold"] else None)
    leak = bool(set(out["context_ids"]) & HR_IDS) or (q["kind"] == "perm" and not g["no_bad_fact"])
    return {"system": system, "id": q["id"], "kind": q["kind"], **g, "invented": cc["invented"],
            "ungrounded": cc["ungrounded"], "cites": cc["cites"], "hr_leak": leak, **out}


jobs = [(s, q) for q in Q for s in ("closed", "full", "company", "rag", "wiki")]
jobs += [("rag_noperm", q) for q in Q if q["kind"] == "perm"]
jobs += [(s, q) for q in Q if q["kind"] == "fresh" for s in ("rag_nofresh", "wiki_stale")]
jobs += [("control", HR_CONTROL)]
llms["wiki_control"] = llms["control"]
jobs += [("wiki_control", HR_CONTROL)]
with ThreadPoolExecutor(8) as ex:
    rows = list(ex.map(lambda j: run(*j), jobs))


def summ(rs):
    if not rs:
        return {}
    gq = [r for r in rs if r["gold_cited"] is not None]
    return {"n": len(rs), "correct": sum(r["correct"] for r in rs), "accuracy": round(sum(r["correct"] for r in rs) / len(rs), 3),
            "gold_cited": sum(bool(r["gold_cited"]) for r in gq), "gold_q": len(gq),
            "citation_rate": round(sum(bool(r["gold_cited"]) for r in gq) / len(gq), 3) if gq else None,
            "answers_with_invented_cites": sum(1 for r in rs if r["invented"]),
            "invented_cites": sum(len(r["invented"]) for r in rs),
            "answers_with_ungrounded_cites": sum(1 for r in rs if r["ungrounded"]),
            "hr_leaks": sum(r["hr_leak"] for r in rs),
            "context_recall": (round(sum(bool(r["context_has_gold"]) for r in gq) / len(gq), 3) if gq else None),
            "tokens_in_p95": sorted(r["tokens_in"] for r in rs)[int(0.95 * (len(rs) - 1))],
            "seconds_p95": sorted(r["seconds"] for r in rs)[int(0.95 * (len(rs) - 1))],
            "tokens_in_mean": round(statistics.mean(r["tokens_in"] for r in rs)),
            "tokens_out_mean": round(statistics.mean(r["tokens_out"] for r in rs)),
            "seconds_mean": round(statistics.mean(r["seconds"] for r in rs), 2)}


S = {}
for s in ("closed", "full", "company", "rag", "wiki"):
    rs = [r for r in rows if r["system"] == s]
    S[s] = {"all": summ(rs), **{k: summ([r for r in rs if r["kind"] == k]) for k in ("policy", "manual", "fresh", "perm", "trap")}}
    S[s]["cost_inr_40"] = round(sum(x.cost_inr for x in llms[s].log), 3)
for s in ("rag_noperm", "rag_nofresh", "wiki_stale", "control", "wiki_control"):
    S[s] = summ([r for r in rows if r["system"] == s])
router = {q["id"]: erp_fact(q["q"]) for q in Q}
log = {"model": MODEL, "date": "2026-10-28", "answer_system": ANSWER_SYSTEM, "full_context_tokens_note": "tokens_in of the 'full' system is the measured prompt size",
       "summary": S, "router": {"flagged": {k: v for k, v in router.items() if v},
                                "traps_flagged": sum(1 for q in Q if q["kind"] == "trap" and router[q["id"]]),
                                "non_traps_flagged": sum(1 for q in Q if q["kind"] != "trap" and router[q["id"]])},
       "rows": rows}
(OUT / "answers_eval.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
for s, v in S.items():
    print(s, json.dumps(v.get("all", v)))
for s in ("closed", "full", "company", "rag", "wiki"):
    print(s, {k: (S[s][k].get("correct"), S[s][k].get("n")) for k in ("policy", "manual", "fresh", "perm", "trap")})
print(log["router"])
for r in rows:
    if not r["correct"] and r["system"] in ("rag", "wiki", "full", "company"):
        print("WRONG", r["system"], r["id"], r["first_ok"], r["facts_ok"], r["no_bad_fact"], r.get("pages"), r["context_ids"][:4] if r["system"] != "full" else "", "|", r["answer"][:300].replace("\n", " "))
