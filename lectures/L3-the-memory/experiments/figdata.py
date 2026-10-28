"""Copy the measured numbers from logs/*.json into ../figdata.js (stdlib only; safe on the laptop).

    python3 lectures/L3-the-memory/experiments/figdata.py
Every number a figure draws comes from here, so a plate can always be traced to a log. Sources:
  logs/retrieval_eval.json  (retrieval_eval.py, 2026-10-28)     logs/story.json      (story.py)
  logs/finding62.json       (finding62.py)                      logs/answers_eval.json (answers_eval.py)
  logs/v2_wiki_compile.json (copied from archive/v2/lectures/L2-the-manual/experiments/logs/wiki_compile.json: the
                             compile that produced bahi/bahi/wiki, which is unchanged since, 2026-10-27 16:17)
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
OUT = HERE.parent / "figdata.js"
J = lambda n: json.loads((LOGS / n).read_text())
ev, st = J("retrieval_eval.json"), J("story.json")
f62 = J("finding62.json") if (LOGS / "finding62.json").exists() else None
ae = J("answers_eval.json") if (LOGS / "answers_eval.json").exists() else None
wk = J("v2_wiki_compile.json")
WIKI = HERE.parents[2] / "bahi" / "bahi" / "wiki"
TOOL = HERE.parents[2] / "bahi" / "bahi" / "toolbox" / "search_policy"

D = {}
D["corpus"] = [{k: c[k] for k in ("doc_id", "title", "version", "effective", "audience", "amends", "words", "chunks",
                                  "fixed120_chunks", "tokens", "kavita_may_read")} for c in ev["corpus"]]
D["full_ctx"], D["company_ctx"] = ev["full_ctx"], {k: v for k, v in ev["company_ctx"].items()}
D["n_chunks"] = {"kavita": ev["n_chunks_kavita"], "all": ev["n_chunks_all"], "dim": ev["embed_dim"]}
ch = ev["chunking"]
D["chunking"] = {"words": ch["words"], "starts": ch["starts"], "c62_render": ch["c62_render"], "c62_words": ch["c62_words"]}
D["fixed_vs_section"] = ev["fixed_vs_section"]
D["summary"] = ev["summary"]
D["ranks"] = {r["id"]: {m: r[m]["gold_rank"] for m in ("bm25", "vector", "hybrid", "hybrid+rerank")} for r in ev["questions"]}
D["tau"] = ev["tau"]
D["leak"] = ev["leak"]
for k in ("shakti", "s1"):
    z = dict(ev[k])
    D[k] = z
D["pca"] = ev["pca"]
D["shakti_tool"] = {"clauses": ev["shakti_tool"]["clauses"], "answer_in_documents": ev["shakti_tool"]["answer_in_documents"],
                    "note": ev["shakti_tool"]["note"]}
# story
D["brain"] = {m.split(":")[1]: v for m, v in st["brain"].items()}
D["system_brain"] = st["system_brain"]
D["with62"] = {k: st["with62"][k] for k in ("answer", "tokens_in", "tokens_out", "cost_inr")}
D["with62"]["prompt"] = st["with62"]["prompt"][1]["content"]
D["full_shakti"] = {k: st["full"][k] for k in ("answer", "tokens_in", "tokens_out", "seconds", "cost_inr")}
D["full_shakti"]["cites"] = st["full"]["check"]["cites"]
D["rag_raw"] = {"clauses": [c["cite"] for c in st["rag_raw"]["clauses"]], "answer": st["rag_raw"]["answer"]}
D["rewrite_v0"] = st["rewrite"]["query"]


def trace(k):
    out = []
    for t in k["trace"]:
        r = json.loads(t["result"])
        out.append({"q": t["args"].get("question"), "found": [[c["cite"], c["score"]] for c in r.get("clauses", [])],
                    "in_docs": r.get("answer_in_documents")})
    return out


D["k0"] = {"answer": st["knowledge"]["answer"], "trace": trace(st["knowledge"]), "check": st["knowledge"]["check"],
           "llm": st["knowledge"]["llm"], "calls": st["knowledge"]["calls"]}
D["checker"] = st["checker"]
if f62:
    a = f62["rewrite"]
    D["rewrite"] = {"clauses": a["clauses"], "answer": a["answer"], "check": a["check"],
                    "prompt": a["prompt"][1]["content"], "prompt_system": a["prompt"][0]["content"],
                    "prompt_tokens": a["prompt_tokens"], "tokens_in": a["tokens_in"], "tokens_out": a["tokens_out"],
                    "cost_inr": a["cost_inr"], "seconds": a["seconds"], "detail": a["search_detail"],
                    "rw_cost": a["rewrite"]["cost_inr"], "rw_tokens_in": a["rewrite"]["tokens_in"],
                    "queries": a["rewrite"]["queries"], "per_query": a["per_query"]}
    o = f62["rewrite_one"]
    D["rewrite_one"] = {"query": o["rewrite"]["query"], "top62": next(d["rerank"] for d in o["search_detail"] if d["id"] == "POL-PUR-001 §6.2"),
                        "top": [[d["id"], d["rerank"]] for d in o["search_detail"][:4]]}
    w = f62["wiki"]
    D["wiki_shakti"] = {"pages": w["pages"], "answer": w["answer"], "check": w["check"], "tokens_in": w["tokens_in"]}
    g = f62["agent"]
    D["k1"] = {"answer": g["answer"], "trace": trace(g), "check": g["check"], "llm": g["llm"], "calls": g["calls"],
               "found_62": g["found_62"], "cites_62": g["cites_62"]}
    import sys; sys.path.insert(0, str(HERE)); from questions import Q as QS, grade
    def fair(qid, ans, cites):
        """The agent's prompt says 'the documents do not cover it', not NOT IN DOCUMENTS; for a trap or a permission
        question, count it right when it states no forbidden fact and says it cannot see / the documents do not cover it."""
        q = next(x for x in QS if x["id"] == qid)
        g = grade(q, ans, cites)
        if q["kind"] in ("trap", "perm"):
            return g["no_bad_fact"] and bool(re.search(r"cannot see|do not cover|don't cover|not cover|NOT IN DOCUMENTS", ans, re.I))
        return g["correct"]
    D["check6"] = [{"id": r["id"], "q": r["q"], **{v: {**{k: r[v][k] for k in ("gold_cited", "cites", "searches", "tokens_in", "cost_inr")},
                                                       "ok": fair(r["id"], r[v]["answer"], r[v]["cites"]), "answer": r[v]["answer"][:300]}
                                                   for v in ("v0", "v1")}} for r in f62["check6"]]
    D["routes"] = {"story": f62.get("routes_story"), "agent": g.get("routes")}
    D["company_context"] = f62["company_context"]
if ae:
    S = ae["summary"]
    D["eval"] = {s: {"all": S[s]["all"], "cost_inr_40": S[s].get("cost_inr_40"),
                     "by_kind": {k: [S[s][k].get("correct"), S[s][k].get("n")] for k in ("policy", "manual", "fresh", "perm", "trap")}}
                 for s in ("closed", "full", "company", "rag", "wiki")}
    D["ablate"] = {s: S[s] for s in ("rag_noperm", "rag_nofresh", "wiki_stale", "control", "wiki_control")}
    D["company_foreign_cites"] = [{"id": r["id"], "cites": r["invented"]} for r in ae["rows"] if r["system"] == "company" and r["invented"]]
    D["eval_wrong"] = [{"system": r["system"], "id": r["id"], "answer": r["answer"][:260]} for r in ae["rows"]
                       if not r["correct"] and r["system"] in ("rag", "wiki", "full", "company")]
# wiki
man = json.loads((WIKI / "manifest.json").read_text())
pages = {}
for s, p in man["pages"].items():
    body = (WIKI / "pages" / f"{s}.md").read_text()
    pages[s] = {"title": p["title"], "audience": p["audience"], "n_sources": len(p["sources"]),
                "links": sorted(set(re.findall(r"\[\[([a-z0-9-]+)\]\]", body)) - {s})}
fg = (WIKI / "pages" / "food-grade-compliance.md").read_text().split("---", 2)[2].strip()
D["wiki"] = {"pages": pages, "page_tokens": wk["page_tokens"], "index_tokens": wk["index_tokens"],
             "compile": wk["llm_totals"], "updates": wk["update_tokens"], "rag_update_chunks": wk["rag_update_chunks"],
             "n_pages": wk["n_pages"], "food_page": fg[:1400]}
D["tool_json"] = (TOOL / "tool.json").read_text()
D["tool_py"] = (TOOL / "tool.py").read_text()

OUT.write_text("/* Generated by experiments/figdata.py from experiments/logs/*.json. Do not edit by hand. */\n"
               "window.L3D = " + json.dumps(D, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(OUT, OUT.stat().st_size // 1024, "KB", "finding62" if f62 else "(no finding62 yet)", "answers" if ae else "(no answers yet)")
