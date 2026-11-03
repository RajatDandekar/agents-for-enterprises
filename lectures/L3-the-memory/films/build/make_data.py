#!/usr/bin/env python3
"""build/data/l3_data.json for the Lecture 3 films, from the recorded runs (standard library only, safe on the laptop).

    python3 make_data.py

  experiments/logs/audit.json                 the dump: files, pages, rows, tokens by class and folder; facts per parser
  experiments/logs/rag_grid.json              the 2,112 measured retrieval settings (the knobs that mattered)
  experiments/logs/rag_best.json              the chosen setting and its golden-set answers
  experiments/logs/rag_failures.json          exact codes, Q-EMMA's eleven gold sources
  experiments/logs/rag_answers/<best>.json    the recorded Q-0412 answer (items, answer text, timings)
  build/data/rag_capture.json                 the live RAG Lab, 3 Nov 2026: QRC-03's chunks, three searches, the PCA map
  build/data/embed_qrc03.json                 the real bge-small vectors of the question and QRC-03's first chunk (embed_modal.py)
  ledgerline/ledgerline/wiki_v4/              the wiki itself: manifest (683 pages, their links), log.md, the Brightcell page
  experiments/logs/wiki_build.json, wiki_query_chains.json, wiki_update.json, wiki_lint.json
  figs/wikipedia/boxes.json                   the captured Wikipedia page ("E-bike") and the boxes of its parts
  experiments/logs/race.json                  the race: RAG against the wiki on the 224 questions, the same 250-word cap
"""
import collections
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
L3 = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(os.path.dirname(L3))
LOGS = os.path.join(L3, "experiments", "logs")
WIKI = os.path.join(ROOT, "ledgerline", "ledgerline", "wiki_v4")
J = lambda p: json.load(open(p))  # noqa: E731

audit = J(os.path.join(LOGS, "audit.json"))
grid = J(os.path.join(LOGS, "rag_grid.json"))
best = J(os.path.join(LOGS, "rag_best.json"))
fail = J(os.path.join(LOGS, "rag_failures.json"))
cap = J(os.path.join(HERE, "data", "rag_capture.json"))
emb = J(os.path.join(HERE, "data", "embed_qrc03.json"))
rec_file = os.path.join(LOGS, "rag_answers", "structured-structure-200-o15__-__bm25__rr1__qr0__k10.json")
rec = next(r for r in J(rec_file)["records"] if r["id"] == "Q-0412")

# ------------------------------------------------------------------------------------------------ rag
CH = best["config"]["chunking"]
rows = [r for r in grid["rows"] if not r["rewrite"]]


def row(**kw):
    return next(r for r in rows if all(r[k] == v for k, v in kw.items()))


ladder = {
    "dense": row(chunking=CH, retrieval="dense", embed="bge-small", rerank=False)["overall"]["recall@5"],
    "bm25": row(chunking=CH, retrieval="bm25", rerank=False)["overall"]["recall@5"],
    "bm25_rerank": row(chunking=CH, retrieval="bm25", rerank=True)["overall"]["recall@5"],
}
by_size = collections.defaultdict(float)
for r in rows:
    by_size[r["size"]] = max(by_size[r["size"]], r["overall"]["recall@5"])
pairs = {}
for r in rows:
    pairs[(r["chunking"], r["embed"], r["retrieval"], r["rerank"])] = r["overall"]["recall@5"]
gains = sorted(pairs[k[:3] + (True,)] - v for k, v in pairs.items() if not k[3] and k[:3] + (True,) in pairs)
rerank_gain = gains[len(gains) // 2]
build = grid["builds"][CH]


def lines_of(text, cut=120):
    """The chunk's real text lines (the header lines in brackets apart) with their lengths, for the paper's text bars."""
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        out.append({"len": len(s), "head": s.startswith("["), "title": False, "text": s[:cut]})
    return out


qrc = cap["qrc03"]
for c in qrc["chunks"]:
    c["lines"] = lines_of(c["text"])

pts = cap["map"]["points"]
xs, ys = [p[0] for p in pts], [p[1] for p in pts]
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
span = max(max(xs) - min(xs), max(ys) - min(ys))


def nm(p):  # PCA coordinates -> -0.5..0.5 (same transform for the query and the hits)
    return [round((p[0] - cx) / span, 4), round((p[1] - cy) / span, 4)]


S = cap["search"]
rag = {
    "question": cap["question"],
    "audit": {"totals": audit["totals"], "by_class": {k: {kk: v[kk] for kk in ("files", "tokens_o200k", "pages", "rows", "types")}
                                                      for k, v in audit["by_class"].items()},
              "facts_visible": {k: {"visible": v["visible"], "present": v["present_facts"]} for k, v in audit["facts_visible"].items()},
              "plain_vs_structured": audit["plain_vs_structured"]},
    "chunking": CH, "n_chunks": build["n_chunks"], "tokens_mean": build["tokens_mean"], "dim": build["models"]["bge-small"]["dim"],
    "hnsw": build["hnsw"], "chromadb": build["chromadb"],
    "qrc03": {"tokens": qrc["tokens"], "chunks": [{k: c[k] for k in ("cid", "cite", "n_tokens", "lines", "locs")} for c in qrc["chunks"]]},
    "search": {n: {"timing_ms": S[n]["timing_ms"], "local_ms": S[n]["local_ms"],
                   "items": [{k: i[k] for k in ("rank", "cite", "file", "score", "gold")} for i in S[n]["items"]]} for n in S},
    "map": {"n_total": cap["map"]["n_total"], "n_shown": len(pts), "folders": cap["map"]["folders"],
            "points": [nm(p) + [p[2]] for p in pts], "query": nm(S["dense"]["map"]["query"]),
            "hits": [nm(h) for h in S["dense"]["map"]["hits"]]},
    "embed": {"dim": emb["dim"], "query": emb["query_vector"], "chunk": emb["chunk_vector"], "cosine_chunk": emb["cosine"],
              "dense_top_score": S["dense"]["items"][0]["score"], "dense_top_cite": S["dense"]["items"][0]["cite"]},
    "ladder_recall5": ladder, "by_size_recall5": dict(sorted(by_size.items())), "rerank_gain_median": round(rerank_gain, 4),
    "n_settings": len(grid["rows"]),
    "exact_code": {k: fail["exact_code"][k]["recall@5"] for k in ("dense", "bm25", "hybrid+rerank")}, "exact_code_n": fail["exact_code"]["dense"]["n"],
    "answer": {"text": rec["answer"], "cited": rec["cited"], "retrieval_s": rec["retrieval_s"], "llm_seconds": rec["llm_seconds"],
               "tokens_in": rec["tokens_in"], "tokens_out": rec["tokens_out"], "cost_usd": rec["cost_usd"],
               "items": [i["cite"] for i in rec["items"]], "judge_ok": rec["judge"]["ok"], "fact_ok": rec["fact"]["ok"]},
    "best": {"answer_correct": best["answers"]["answer_correct"], "citation_correct": best["answers"]["citation_correct"],
             "recall@5": best["retrieval"]["recall@5"], "cost_per_q_usd": best["answers"]["cost_per_q_usd"],
             "retrieval_p95_s": best["retrieval"]["latency_s"]["p95"], "total_p50_s": best["answers"]["total_s"]["p50"]},
    "q_emma": {"gold": fail["Q-EMMA best"]["gold_sources"], "found@10": fail["Q-EMMA best"]["found@10"],
               "detail": fail["Q-EMMA best"]["detail"]},
}

# ------------------------------------------------------------------------------------------------ wiki
man = J(os.path.join(WIKI, "manifest.json"))["pages"]
wb = J(os.path.join(LOGS, "wiki_build.json"))
ch = J(os.path.join(LOGS, "wiki_query_chains.json"))
up = J(os.path.join(LOGS, "wiki_update.json"))
lint = J(os.path.join(LOGS, "wiki_lint.json"))

# ingestion order: the first log.md line that names a page
first = {}
log_lines = [l for l in open(os.path.join(WIKI, "log.md")).read().splitlines() if l.startswith("## [")]
ingests = 0
for l in log_lines:
    m = re.match(r"## \[(.*?)\] (\S+) \| (.*?) \|(.*?)\| (.*)$", l)
    if not m:
        continue
    ts, op = m.group(1), m.group(2)
    ingests += op == "ingest"
    for s in [x.strip() for x in m.group(5).split(",")]:
        if s in man and (s not in first or ts < first[s]):
            first[s] = ts
order = sorted(man, key=lambda s: (first.get(s, "9"), s))

TYPES = ["screen", "policy", "service-group", "procedure", "error", "supplier", "error-list", "release", "item-family", "manual",
         "decision", "role", "topic", "cost-centre", "person", "data-source"]   # big and small clusters alternate round the ring
by_type = collections.defaultdict(list)
for s in sorted(man):
    by_type[man[s]["type"]].append(s)
assert set(by_type) <= set(TYPES), set(by_type) - set(TYPES)

# layout: one cluster per type around a ring; inside a cluster a grid of upright tablets (x across, y back)
DX, DY = 0.125, 0.105
pos = {}
clusters = {}
R = 2.65
n_t = len(TYPES)
for k, t in enumerate(TYPES):
    sl = by_type[t]
    n = len(sl)
    cols = max(2, math.ceil(math.sqrt(n / 1.3)))     # narrow along the ring, deep along the radius
    rws = math.ceil(n / cols)
    a = math.pi / 2 - 2 * math.pi * k / n_t           # clockwise from the back
    ccx, ccy = R * math.cos(a), R * math.sin(a)
    rot = a + math.pi / 2                             # the cluster's rows run along the ring
    clusters[t] = {"center": [round(ccx, 4), round(ccy, 4)], "n": n, "angle": round(a, 4)}
    for i, s in enumerate(sl):
        c, r_ = i % cols, i // cols
        lx, ly = (c - (cols - 1) / 2) * DX, (r_ - (rws - 1) / 2) * DY
        x = ccx + lx * math.cos(rot) - ly * math.sin(rot)
        y = ccy + lx * math.sin(rot) + ly * math.cos(rot)
        pos[s] = [round(x, 4), round(y, 4), round(rot, 4)]

links = []
for s, v in man.items():
    for t in v.get("links_out", []):
        if t in man and t != s:
            links.append([s, t])

lint_pages = collections.Counter(p for f in lint["findings"] for p in f.get("pages", []) if p in man)
cq = ch["chains"]["Q-EMMA"]["wiki"]
fb = ch["fileback"]

# the Brightcell page, as sections (for the page card)
src = open(os.path.join(WIKI, "pages", "sup-brightcell-energy.md")).read()
body = src.split("---", 2)[2]
heads = re.findall(r"^## (.+)$", body, re.M)
lead = next(p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith(("|", "#")))
info = [r for r in re.findall(r"^\| (.+?) \| (.+?) \|$", body, re.M) if r[0] not in ("", "---", "Field")][:6]
refs = re.findall(r"^\[\^(r\d+)\]: (.+)$", body, re.M)
links_bc = re.findall(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", body)

wp = J(os.path.join(L3, "figs", "wikipedia", "boxes.json"))
agents = open(os.path.join(WIKI, "AGENTS.md")).read()
sec1 = agents.split("## 1. The three layers", 1)[1].split("## 2.", 1)[0]
layers = [[c.strip().strip("`") for c in r.strip().strip("|").split("|")] for r in sec1.splitlines() if r.startswith("| ") and "---" not in r]

wiki = {
    "build": {k: wb[k] for k in ("sources", "parts", "pages", "links", "links_resolved", "pages_by_type", "facts", "wiki_words")},
    "ingests": ingests, "log_lines": len(log_lines),
    "types": TYPES, "clusters": clusters, "order": order,
    "pages": {s: {"type": man[s]["type"], "title": man[s]["title"], "audience": man[s]["audience"], "pos": pos[s],
                  "refs": len(man[s].get("refs") or [])} for s in man},
    "links": links, "lint_pages": dict(lint_pages),
    "chain": {"question": cq["question"], "steps": cq["chain"], "nav_calls": cq["nav_calls"], "tokens_in": cq["tokens_in"],
              "answer": cq["answer"], "answer_seconds": cq["answer_seconds"],
              "items": [{"id": i["id"], "cite": i["cite"], "n_sources": len(i["sources"]),
                         "sources": [{"file": x["file"], "class": audit["class_rule"].get(x["file"].rsplit(".", 1)[-1].lower(), "unstructured")}
                                     for x in i["sources"]]} for i in cq["items"]]},
    "fileback": {"slug": fb["filed"]["slug"], "pages_used": fb["filed"]["pages_used"], "refs": fb["filed"]["refs"]},
    "update": {"file": up["files"][0], "updated": up["updated"], "created": up["created"], "seconds": up["seconds"]["total"],
               "usd": up["usd"], "facts_added": up["facts_added"]},
    "lint": {"n_findings": lint["n_findings"], "by_kind": lint["by_kind"], "found": lint["messiness"]["found"],
             "planted": lint["messiness"]["n"], "pages_flagged": len(lint_pages)},
    "agents_layers": layers,
    "brightcell": {"lead": lead, "sections": heads, "infobox": info, "refs": len(refs), "links": sorted({a for a, _ in links_bc})},
    "wikipedia": {k: wp[k] for k in ("url", "title", "lead", "infobox", "toc", "headings", "references", "n_sections", "n_refs",
                                       "n_internal_links", "pixel_scale", "captured_utc", "licence", "page", "title_box", "links")},
}

# ------------------------------------------------------------------------------------------------ the race
race_p = os.path.join(LOGS, "race.json")
race = None
if os.path.exists(race_p):
    rc = J(race_p)
    race = {"n": rc["overall"]["rag"]["n"], "what": rc["what"], "methods": rc["methods"], "targets": rc["targets"],
            "overall": rc["overall"], "by_type": {t: {m: v[m]["answer_correct"] for m in v} for t, v in rc["by_type"].items()},
            "by_type_n": {t: v["rag"]["n"] for t, v in rc["by_type"].items()},
            "paste_all": rc["paste_all"], "update_cost": rc["update_cost"], "cascade": {k: rc["cascade"][k] for k in ("fallbacks", "answer_correct", "cost_per_q_usd")},
            "decision": rc["decision"]["winner"],
            "examples": {q: {m: {k: v[m][k] for k in ("judge", "facts_missing", "total_s", "retrieval_s", "cost_usd")}
                             for m in ("rag", "wiki", "hybrid", "sections")} for q, v in rc["examples"].items()}}

out = {"source": "make_data.py", "rag": rag, "wiki": wiki, "race": race}
p = os.path.join(HERE, "data", "l3_data.json")
json.dump(out, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
print("wrote", p, os.path.getsize(p) // 1024, "KB")
print("ladder", ladder, "| by size", dict(by_size), "| rerank gain", round(rerank_gain, 4), "| chunks", build["n_chunks"])
print("wiki pages", len(man), "links", len(links), "lint pages", len(lint_pages), "ingests", ingests, "chain", [s.get("what") for s in cq["chain"]])
print("brightcell", heads, info[:3], len(refs))
