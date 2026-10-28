"""Lecture 2: compile the LLM Wiki (Karpathy's pattern) from Bahi's documents, then absorb the two amendments.

1. Compile the base documents (no amendments): plan pages (1 call), write each page (1 call each), index by code, lint by code.
2. Keep a copy of that wiki (experiments/wiki_before_amendments/) for the staleness test.
3. Update with AMD-SUP-2026-02, then AMD-PUR-2026-03: recompile only the pages whose sources each amendment touches.
Writes bahi/bahi/wiki/ and logs/wiki_compile.json. Model calls recorded in cassette L2_wiki.
"""
import json, pathlib, shutil, sys, time
from bahi.agent.retrieval import Wiki, load_corpus, WIKI_DIR, chunk_by_section, count_tokens
from bahi.llm import LLM

MODEL = sys.argv[1] if len(sys.argv) > 1 else "gemini:gemini-3.8-flash"
HERE = pathlib.Path(__file__).parent
OUT = HERE / "logs"; OUT.mkdir(exist_ok=True)
llm = LLM(MODEL, cassette="L2_wiki", max_tokens=16384)
alld = load_corpus()
base = [d for d in alld if not d.is_amendment]
amds = sorted([d for d in alld if d.is_amendment], key=lambda d: d.effective)
if WIKI_DIR.exists():
    shutil.rmtree(WIKI_DIR)
w = Wiki(WIKI_DIR)
t0 = time.time()
rep = w.compile(base, llm)
rep["seconds_wall"] = round(time.time() - t0, 1)
stale = HERE / "wiki_before_amendments"
if stale.exists():
    shutil.rmtree(stale)
shutil.copytree(WIKI_DIR, stale)
ups = []
docs = list(base)
for a in amds:
    docs.append(a)
    ups.append(w.update(a, docs, llm))
pages = w.manifest["pages"]
tot_in = sum(c["tokens_in"] for c in rep["plan_calls"]) + sum(p["tokens_in"] for p in rep["pages"].values())
tot_out = sum(c["tokens_out"] for c in rep["plan_calls"]) + sum(p["tokens_out"] for p in rep["pages"].values())
idx = (WIKI_DIR / "index.md").read_text()
log = {"model": MODEL, "compile": rep, "updates": ups, "n_pages": len(pages),
       "compile_tokens_in": tot_in, "compile_tokens_out": tot_out, "compile_calls": len(rep["plan_calls"]) + len(rep["pages"]),
       "update_tokens": [{"amendment": u["amendment"], "pages": u["pages_recompiled"],
                          "tokens_in": sum(p["tokens_in"] for p in u["pages"].values()),
                          "tokens_out": sum(p["tokens_out"] for p in u["pages"].values())} for u in ups],
       "rag_update_chunks": {a.doc_id: len(chunk_by_section(a)) for a in amds},
       "index_tokens": count_tokens(idx),
       "page_tokens": {s: count_tokens(w.page(s)) for s in pages},
       "source_tokens": {d.doc_id: count_tokens(d.body) for d in alld},
       "llm_totals": llm.totals(),
       "pages": {s: {"title": p["title"], "audience": p["audience"], "n_sources": len(p["sources"]),
                     "links": sorted(set(__import__("re").findall(r"\[\[([a-z0-9-]+)\]\]", w.page(s))))} for s, p in pages.items()}}
(OUT / "wiki_compile.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
print(json.dumps({k: log[k] for k in ("n_pages", "compile_tokens_in", "compile_tokens_out", "compile_calls", "update_tokens",
                                       "index_tokens", "llm_totals")}, indent=1))
print(json.dumps(rep["lint"], indent=1)); print(json.dumps([u["lint"] for u in ups], indent=1))
print(rep.get("uncovered_by_plan"))
print(idx)
