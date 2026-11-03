"""Build figdata.js (window.L3) for the Lecture 3 deck from the recorded logs, the dump's golden set and the wiki.

    python3 lectures/L3-the-memory/gen_figdata.py          (standard library only; safe on the laptop)

Nothing is typed by hand: every number the deck shows comes from one of these files.
  experiments/logs/audit.json          the dump: files, pages, rows, tokens by folder, type and class; messiness
  experiments/logs/paste_all.json      the whole dump against context windows; the measured 12-question sample
  experiments/logs/rag_grid.json       2,112 retrieval configurations (summarised here: knobs, scatter points)
  experiments/logs/rag_best.json       the chosen configuration, its answers, the candidates
  experiments/logs/rag_failures.json   exact codes, tables, multi-hop, versions, Emma's question
  experiments/logs/hnsw_check.json     Chroma's HNSW against exact search
  experiments/logs/deck_extract.json   real parser output and chunks (deck_extract_modal.py), the race's passages
  experiments/logs/wiki_*.json         the LLM Wiki: build, lint, update, query chains, search
  experiments/logs/race.json           the race (race_report.py)
  experiments/logs/knowledge_*.json    Ask Northbridge ?stage=knowledge, recorded in-process and live
  northbridge-docs/eval/questions.jsonl, README.md   the golden set and Henrik's hand-over note
  ledgerline/ledgerline/wiki_v4/       the wiki's pages, index.md, log.md, AGENTS.md
  ledgerline/ledgerline/toolbox/search_docs/tool.json
"""
import collections
import json
import os
import pathlib
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "experiments" / "logs"
ROOT = HERE.parents[1]
PKG = ROOT / "ledgerline" / "ledgerline"
WIKI = PKG / "wiki_v4"
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", ROOT.parent / "northbridge-docs"))


def J(name):
    return json.loads((LOGS / name).read_text())


def cut(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 1] + "…"


out = {"_source": "gen_figdata.py (see its docstring for every file it reads)"}

# ---------------------------------------------------------------- the dump and its audit
a = J("audit.json")
out["audit"] = {
    "totals": a["totals"], "units": a["units"], "parse_failures": {k: len(v) for k, v in a["parse_failures"].items()},
    "by_class": {k: {x: v[x] for x in ("files", "pages", "rows", "words", "tokens_o200k", "types")} for k, v in a["by_class"].items()},
    "by_folder": {k: {x: v[x] for x in ("files", "pages", "rows", "tokens_o200k", "types")} for k, v in a["by_folder"].items()},
    "by_type": {k: {x: v[x] for x in ("files", "tokens_o200k")} for k, v in a["by_type"].items()},
    "flags": {k: {"n": v["n"], "files": v["files"]} for k, v in a["flags"].items()},
    "duplicates": a["duplicates_byte_identical"], "empty_plain": a["empty_files"]["plain"],
    "facts_visible": {k: {"visible": v["visible"], "present": v["present_facts"]} for k, v in a["facts_visible"].items()},
    "plain_vs_structured": a["plain_vs_structured"],
    "messiness": [{"id": m["id"], "kind": m["kind"], "what": m["what"]} for m in a["messiness_through_parser"]],
    "tokenizers": a["tokenizers"],
}
# per file, for the Dump Explorer treemap (folder > file)
files = []
for rel, f in a["per_file"].items():
    files.append([rel, f["folder"], f["fmt"], f["class"], f["tokens_o200k"], f["pages"], f["rows"]])
out["audit"]["files"] = files

readme = (DUMP / "README.md").read_text()
note = readme.split("## What is in each folder")[0]
note = note.split("\n", 2)[2].strip()        # drop the title line
out["readme"] = {"note": note, "folders": re.findall(r"^\| (\S+/) \| (.+?) \|$", readme, re.M)}

# ---------------------------------------------------------------- the golden set and the taxonomy
qs = [json.loads(l) for l in (DUMP / "eval" / "questions.jsonl").read_text().splitlines() if l.strip()]
cats = collections.Counter(q["category"] for q in qs)
types = collections.Counter(q.get("type") for q in qs if q["category"] == "documentation")
ex = collections.defaultdict(list)
for q in qs:
    ex[q.get("type") or q["category"]].append({"id": q["id"], "q": q["question"]})
emma = next(q for q in qs if q["id"] == "Q-EMMA")
q412 = next(q for q in qs if q["id"] == "Q-0412")
out["questions"] = {
    "n": len(qs), "categories": dict(cats), "types": dict(types),
    "examples": {k: v[:5] for k, v in ex.items()},
    "emma": {"q": emma["question"], "reference": emma["reference_answer"], "must": emma.get("must_contain", []),
             "gold": [{"file": g["file"], "section": g.get("section"), "page": g.get("page") or g.get("pages"),
                       "absent": g.get("absent", False)} for g in emma["gold_sources"]]},
    "q0412": {"q": q412["question"], "reference": q412["reference_answer"], "must": q412.get("must_contain", []),
              "gold": [{"file": g["file"], "section": g.get("section")} for g in q412["gold_sources"]]},
}

# ---------------------------------------------------------------- paste everything
p = J("paste_all.json")
out["paste"] = {"total": p["total_tokens"], "largest": p["largest_window"], "fits_any": p["fits_any_model"],
                "windows": sorted(([k, v["context_length"]] for k, v in p["context_windows"].items()), key=lambda x: -x[1]),
                "subsets": {k: v["tokens"] for k, v in p["subsets"].items()},
                "usd_everything": p["subsets"]["everything"]["usd_per_question_gemini_3.8_flash"],
                "sample": {k: p["measured_run"][k] for k in ("label", "subset_tokens_o200k", "n", "answer_correct",
                                                            "citation_correct", "seconds", "tokens_in_per_q", "cost_per_q_usd")}}

# ---------------------------------------------------------------- the RAG grid, summarised
g = J("rag_grid.json")
rows = g["rows"]
R5 = lambda r: r["overall"]["recall@5"]
P95 = lambda r: r["latency_s"]["p95"]
pts = [[round(R5(r), 4), round(P95(r), 5), r["retrieval"], int(r["rerank"]), int(r["rewrite"]), r["embed"] or "-",
        r["parser"], r["chunker"], r["size"], r["overlap"]] for r in rows]
knob = lambda key: {str(k): round(max(R5(r) for r in rows if r[key] == k), 4) for k in sorted({r[key] for r in rows}, key=str)}
plain = [r for r in rows if not r["rewrite"]]


def best(f):
    c = [r for r in plain if f(r)]
    return round(max(R5(r) for r in c), 4) if c else None


def pairs(field):
    """Rows that differ only in `field` (False -> True): recall@5 deltas and added p95 latency."""
    key = lambda r: (r["chunking"], r["embed"], r["retrieval"], r["rerank"], r["rewrite"])
    idx = {key(r): r for r in rows}
    d, lat = [], []
    for r in rows:
        if not r[field]:
            k = list(key(r)); k[["chunking", "embed", "retrieval", "rerank", "rewrite"].index(field)] = True
            o = idx.get(tuple(k))
            if o:
                d.append(R5(o) - R5(r)); lat.append(P95(o) - P95(r))
    return {"n": len(d), "median_delta": round(statistics.median(d), 4), "mean_delta": round(statistics.mean(d), 4),
            "worse": sum(1 for x in d if x < 0), "better": sum(1 for x in d if x > 0),
            "median_added_p95_s": round(statistics.median(lat), 4), "mean_added_p95_s": round(statistics.mean(lat), 4)}


dense_by_model = {m: best(lambda r, m=m: r["retrieval"] == "dense" and r["embed"] == m and not r["rerank"])
                  for m in g["grid"]["models"]}
by_size = {str(s): best(lambda r, s=s: r["size"] == s) for s in g["grid"]["sizes"]}
b = J("rag_best.json")
out["grid"] = {
    "n_rows": g["n_rows"], "grid": g["grid"], "budget_p95_s": g["budget_p95_s"], "machine": g["machine"], "questions": g["questions"],
    "points": pts, "by_parser": knob("parser"), "by_chunker": knob("chunker"), "by_size": by_size,
    "by_mode": {"bm25": best(lambda r: r["retrieval"] == "bm25" and not r["rerank"]),
                "dense": best(lambda r: r["retrieval"] == "dense" and not r["rerank"]),
                "hybrid": best(lambda r: r["retrieval"] == "hybrid" and not r["rerank"]),
                "bm25+rerank": best(lambda r: r["retrieval"] == "bm25" and r["rerank"]),
                "hybrid+rerank": best(lambda r: r["retrieval"] == "hybrid" and r["rerank"])},
    "bm25_p95_s": round(min(P95(r) for r in rows if r["retrieval"] == "bm25" and not r["rerank"] and not r["rewrite"]), 5),
    "dense_by_model": dense_by_model, "rerank": pairs("rerank"), "rewrite": pairs("rewrite"),
    "builds": {k: {x: v.get(x) for x in ("n_chunks", "tokens_mean", "chunk_s", "bm25_build_s", "build_s_total")}
               for k, v in g["builds"].items() if k in ("structured-structure-200-o15", "structured-structure-400-o0",
                                                         "plain-fixed-400-o0", "structured-fixed-1200-o0")},
    "embed_dims": {m: v["dim"] for m, v in g["builds"]["structured-structure-200-o15"]["models"].items()},
    "embed_s": {m: v["embed_s"] for m, v in g["builds"]["structured-structure-200-o15"]["models"].items()},
}
out["best"] = {k: b[k] for k in ("rule", "config", "machine", "answer_model", "targets", "answers_by_type", "judge_vs_fact",
                                 "index", "candidates", "honest")}
out["best"]["retrieval"] = {k: v for k, v in b["retrieval"].items() if k != "by_type_recall@10"}
out["best"]["recall10_by_type"] = b["retrieval"]["by_type_recall@10"]
out["best"]["answers"] = {k: v for k, v in b["answers"].items() if not isinstance(v, list)}
f = J("rag_failures.json")
out["fail"] = {"exact_code": f["exact_code"], "exact_code_by_model_dense": f["exact_code_by_model_dense"], "q0412": f["Q-0412"],
               "codes_bm25_only": f["codes_bm25_only"], "tables": f["tables"], "q401": f["Q-401 (reorder level of BAT-500)"],
               "multi_hop": {k: v for k, v in f["multi_hop"].items() if k != "questions"},
               "version_conflict": {k: v for k, v in f["version_conflict"].items() if k != "questions"},
               "emma": f["Q-EMMA best"]}
out["hnsw"] = J("hnsw_check.json")
d = J("deck_extract.json")
out["extract"] = {"parsers": d["parsers"], "chunks": d["chunks"], "race_items": d["race_items"]}

# ---------------------------------------------------------------- the LLM Wiki
wb = J("wiki_build.json")
out["wiki"] = {"build": {k: wb[k] for k in ("sources", "parts", "pages", "pages_by_type", "pages_by_audience", "links", "links_resolved",
                                          "references", "facts", "facts_quote_verified", "wiki_words", "seconds",
                                          "usd_at_harness_price", "build_wall_minutes_estimate")},
               "orphans": len(wb["orphans"])}
wl = J("wiki_lint.json")
out["wiki"]["lint"] = {"n_findings": wl["n_findings"], "by_kind": wl["by_kind"], "by_source": wl["by_source"],
                       "messiness": {k: v for k, v in wl["messiness"].items() if k not in ("items", "rule")},
                       "review": wl["review"], "seconds": wl["seconds"],
                       "examples": [{"kind": x["kind"], "detail": cut(x["detail"], 220), "files": x["files"][:2]}
                                    for kind in ("contradiction", "superseded", "email_overrides_sop", "red_link")
                                    for x in [next(y for y in wl["findings"] if y["kind"] == kind)]]}
wu = J("wiki_update.json")
out["wiki"]["update"] = {k: wu[k] for k in ("files", "pages_touched", "updated", "created", "seconds", "usd", "facts_added")}
wc = J("wiki_query_chains.json")
ch = wc["chains"]["Q-EMMA"]
out["wiki"]["chain_emma"] = {m: {"chain": v.get("chain"), "calls": v.get("calls"), "nav_calls": v.get("nav_calls"),
                                 "answer_seconds": v.get("answer_seconds"), "tokens_in": v.get("tokens_in"),
                                 "answer": v.get("answer"), "items": [x.get("cite") for x in v.get("items", [])]}
                             for m, v in ch.items()}
fb = wc["fileback"]
out["wiki"]["fileback"] = {k: (fb[k] if not isinstance(fb[k], dict) else {x: fb[k][x] for x in fb[k] if x != "chain"})
                           for k in fb if k in ("navigator", "before", "after", "filed", "page", "what")}
ws = J("wiki_search_demo.json")
out["wiki"]["search_ms"] = ws["golden_set_ms"]


def page(slug, n=99999):
    t = (WIKI / "pages" / f"{slug}.md").read_text()
    fm, body = t.split("---", 2)[1], t.split("---", 2)[2]
    return {"slug": slug, "front": fm.strip(), "body": cut(body.strip(), n)}


out["wiki"]["page_brightcell"] = page("sup-brightcell-energy")
out["wiki"]["agents_md"] = cut((WIKI / "AGENTS.md").read_text(), 2600)
idx = (WIKI / "index.md").read_text().splitlines()
out["wiki"]["index_head"] = "\n".join(idx[:12])
out["wiki"]["index_lines"] = len(idx)
lg = (WIKI / "log.md").read_text().splitlines()
out["wiki"]["log_head"] = "\n".join(l for l in lg[:14])
out["wiki"]["log_lines"] = sum(1 for l in lg if l.startswith("## ["))

# ---------------------------------------------------------------- the race
r = J("race.json")
out["race"] = {k: r[k] for k in ("what", "methods", "machine", "targets", "overall", "by_type", "paste_all", "cap_150_vs_250",
                                 "withheld_notice", "cascade", "spend_usd", "update_cost", "decision")}
out["race"]["examples"] = {q: {m: {k: v[k] for k in ("answer", "judge", "judge_reason", "facts_missing", "total_s", "retrieval_s",
                                                    "cost_usd", "sources") if k in v}
                               for m, v in e.items()} for q, e in r["examples"].items()}

# ---------------------------------------------------------------- Ask Northbridge, knowledge stage
ks = J("knowledge_stage.json")
out["knowledge"] = {"model": ks["model"], "turns": []}
for t in ks["turns"]:
    cards = t["cards"] if isinstance(t["cards"], list) else []
    out["knowledge"]["turns"].append({
        "user": t["user"], "question": t["question"], "reply": t["reply"], "rounds": t["rounds"], "model_calls": t["model_calls"],
        "tokens_in": t["tokens_in"], "tokens_out": t["tokens_out"], "seconds": t["seconds"],
        "calls": [{"tool": c["tool"], "args": c["args"], "n": len((c.get("result") or {}).get("passages", [])),
                   "withheld": (c.get("result") or {}).get("withheld"),
                   "top": [{"cite": x.get("cite"), "status": x.get("status")} for x in (c.get("result") or {}).get("passages", [])[:4]]}
                  for c in cards]})
kl = J("knowledge_live.json")
out["knowledge"]["live"] = {"what": kl["what"], "on_wall": kl["on_wall"], "warm_wait_s": kl["warm_wait_s"],
                            "turns": [{"q": t["q"], "status": t["status"], "wall_s": t["wall_s"]} for t in kl["turns"]]}
out["knowledge"]["tool_json"] = (PKG / "toolbox" / "search_docs" / "tool.json").read_text()

# ---------------------------------------------------------------- real code, for the mini-prototype slides
import ast  # noqa: E402


def snippet(path, name, cls=None):
    src = path.read_text()
    tree = ast.parse(src)
    nodes = tree.body
    if cls:
        nodes = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    n = next(n for n in nodes if getattr(n, "name", None) == name)
    lines = src.splitlines()[n.lineno - 1 - len(n.decorator_list): n.end_lineno]
    return "\n".join(lines)


RAG, CORP, WQ = PKG / "course" / "l3" / "rag.py", PKG / "course" / "l3" / "corpus.py", PKG / "course" / "l3" / "wiki_query.py"
out["code"] = {"tokenize": snippet(RAG, "tokenize"), "bm25": snippet(RAG, "BM25"), "rrf": snippet(RAG, "rrf"),
               "reranker": snippet(RAG, "Reranker"), "search": snippet(RAG, "search", cls="Retriever"),
               "embedder": snippet(RAG, "Embedder"), "chunk": snippet(CORP, "chunk"), "rag_search": snippet(RAG, "rag_search"),
               "navigate": snippet(WQ, "navigate", cls="Navigator"), "wiki_search": snippet(WQ, "wiki_search")}

# ---------------------------------------------------------------- NB3's own outputs (the executed notebook, tools_nb3_replay_modal.py)
NB3 = HERE / "NB3_the_memory.ipynb"


def cell_out(marker):
    for c in json.loads(NB3.read_text())["cells"]:
        if c["cell_type"] == "code" and marker in "".join(c["source"]):
            return "".join("".join(o.get("text", "")) for o in c.get("outputs", []) if o.get("output_type") == "stream").strip()
    return None


if NB3.exists():
    out["nb3"] = {"bm25": cell_out("rep = E.retrieval_only(lambda q, role: bm25_only.search"),
                  "answer": None}
    _a = (cell_out("a = E.answer(q, items, ans_llm, answer_words") or "").split("\n")
    if _a and _a[0]:   # the answer's first line, then the replay, fact-check and judge lines
        out["nb3"]["answer"] = "\n".join([_a[0], "…"] + [cut(l, 170) for l in _a[-3:]])

js = "/* Generated by gen_figdata.py. Do not edit by hand. */\nwindow.L3 = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
(HERE / "figdata.js").write_text(js)
print("wrote figdata.js", len(js) // 1024, "KB;", "grid", out["grid"]["by_mode"], "rerank", out["grid"]["rerank"], "rewrite", out["grid"]["rewrite"])
