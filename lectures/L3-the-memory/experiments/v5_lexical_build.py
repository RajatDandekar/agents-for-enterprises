"""Turn the lexical section's Modal logs into v5/lexical_data.js (window.L3V5.lexical). No model, no heavy compute:
it only selects fields from logs/v5_lexical.json, logs/v5_lexical_extra.json, logs/v5_lexical_walk.json (the BM25
walk-through, experiments/v5_lexical_walk_modal.py) and logs/v5_dense_failures.json via v5_lexical_cases.json when
present, and checks a few numbers by the formula.

    python3 lectures/L3-the-memory/experiments/v5_lexical_build.py
"""
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2]
LOGS = HERE / "logs"
OUT = HERE.parent / "v5" / "lexical_data.js"
RAG = COURSE / "ledgerline" / "ledgerline" / "course" / "l3" / "rag.py"

L = json.loads((LOGS / "v5_lexical.json").read_text())
X = json.loads((LOGS / "v5_lexical_extra.json").read_text())
W = json.loads((LOGS / "v5_lexical_walk.json").read_text())
CASES = json.loads((LOGS / "v5_lexical_cases.json").read_text()) if (LOGS / "v5_lexical_cases.json").exists() else None
# dense ranks as the dense section logged them (its own run of the same code); ours differ by a few places from fp16 noise
DFILE = LOGS / "v5_dense_failures.json" if (LOGS / "v5_dense_failures.json").exists() else LOGS / "v5_dense_probes.json"
DCASES = json.loads(DFILE.read_text()).get("cases", {}) if DFILE.exists() else {}
if isinstance(DCASES, list):
    DCASES = {c["id"]: c for c in DCASES}

# short names for D's 15 chunks (what each chunk is about, read from its text; numbers are the chunk ids #c0..#c14)
NAMES = ["Title and version history", "Version history 4.0, 4.1", "§1–3 Purpose, scope, requests", "§4 Cost centres",
         "§5 Approval limits", "§6 Supplier qualification", "§7–9 Prices, tax, records", "Appendix A Definitions",
         "FAQ: order without a request", "FAQ: stuck in Draft", "FAQ: my approval limit", "FAQ: already signed off?",
         "FAQ: battery packs, hub motors, chargers", "FAQ: new supplier, rate, tax", "FAQ: when to tell; related docs"]
assert len(NAMES) == len(L["D_chunks"]) == 15


def short(cite):
    return cite.replace(" § ", " §").replace(".eml, §body", ".eml").replace(", §body", "")


def lst(rows, keys):
    return [{k: r.get(k) for k in keys} | {"cite": short(r["cite"])} for r in rows]


import re
STOP = re.search(r'STOP = set\("(.*?)"\.split\(\)\)', RAG.read_text(), re.S).group(1).replace('"', " ").split()

D = L["D_chunks"]
bm = {x["k"]: x for x in L["bm25_D"]}
de = {x["k"]: x for x in L["dense_D"]}
rr = {x["k"]: x for x in L["rerank_D"]}
rf = {x["k"]: x for x in L["rrf_D"]}
chunks = [{"k": c["k"], "name": NAMES[c["k"]], "cite": c["cite"], "dl": c["dl"], "tokens": c["n_tokens"],
           "facts": c["facts"], "body": c["text"].split("\n", 2)[2] if c["text"].count("\n") >= 2 else c["text"],
           "bm25": bm[c["k"]]["score"], "bm25_rank": bm[c["k"]]["rank"], "terms": bm[c["k"]]["terms"],
           "cos": de[c["k"]]["cos"], "dense_rank": de[c["k"]]["rank"], "rrf": rf[c["k"]]["rrf"], "fused_rank": rf[c["k"]]["fused_rank"],
           "rr": rr[c["k"]]["score"], "rr_rank": rr[c["k"]]["rank"]} for c in D]

# checks by the formula: the length slide's numbers and RRF on D
k1, b, avg = L["k1"], L["b"], L["avgdl"]["D"]
idf_bat = L["df"]["battery"]["idf_D"]
for k in (1, 5):
    w = idf_bat * 1 * (k1 + 1) / (1 + k1 * (1 - b + b * chunks[k]["dl"] / avg))
    got = next(t["w"] for t in chunks[k]["terms"] if t["term"] == "battery")
    assert abs(w - got) < 2e-3, (k, w, got)
for c in chunks:
    assert abs(1 / (60 + c["bm25_rank"]) + 1 / (60 + c["dense_rank"]) - c["rrf"]) < 1e-5

V = X["variants"]["runs"]
data = {
    "Q": L["Q"], "D": L["D"], "n_all": L["n_all"], "k1": k1, "b": b, "rrf_k": L["rrf_k"], "avgdl": L["avgdl"],
    "tok": {"Q": L["tokenize"]["Q"], "Q0412": L["tokenize"]["Q0412"], "clause": L["tokenize"]["clause"]},
    "variants": {kind: {q: {"tokens": r["tokens"], "doc_rank": r["err_doc"]["gold_rank"], "doc_top": r["err_doc"]["top3"],
                            "dump_rank": r["dump"]["gold_rank"], "dump_top": r["dump"]["top3"]} for q, r in runs.items()}
                 for kind, runs in V.items()},
    "variant_queries": X["variants"]["queries"], "err_gold": X["variants"]["gold_err_chunk"],
    "err_doc_n": L["bm25_err"]["n"], "err_top": L["bm25_err"]["top"][:3],
    "chunks": chunks,
    "tf": {t: L["tf_D"][t] for t in ["buy", "battery", "pack", "brightcell", "energy", "they", "quote", "£104",
                                     "bought", "buys", "quotation", "purchase", "policy", "order", "supplier"]},
    "df": L["df"],
    "dump": {q: {"bm25": lst(L["bm25_all"][q], ["i", "rank", "score", "facts", "gold_loc", "dl", "terms"]),
                 "dense": lst(L["dense_all"][q], ["i", "rank", "cos", "facts", "gold_loc"]),
                 "hybrid": lst(L["hybrid_all"][q], ["i", "rank", "rrf", "dense_rank", "bm25_rank", "facts", "gold_loc"]),
                 "rerank": lst(L["rerank"][q], ["before", "after", "score", "logit", "facts", "gold_loc", "i"])}
             for q in ("Q-EMMA", "Q-0412")},
    "D_in_dump": {"bm25": L["bm25_all"]["Q-EMMA_D_ranks"], "dense": L["dense_all"]["Q-EMMA_D_ranks"]},
    "gold_ranks": {q: {m: v["rank"] for m, v in r.items()} for q, r in L["gold_ranks"].items()},
    "models": L["models"], "pair": L["pair_tokens"],
    "lat": {"gpu": L["latency_gpu"], "cpu": L["latency_cpu"]},
    "llm": {"model": X["llm_rerank"]["model"], "runs": [{k: r[k] for k in ("seconds", "order", "tokens_in", "tokens_out")}
                                                        for r in X["llm_rerank"]["runs"]]},
    # the walk-through (rag.BM25 on D's 15 chunks, every piece read from the built index)
    "walk": {"chunks": {c["k"]: c for c in W["chunks"]}, "order": W["order"], "avgdl": W["avgdl"], "sat": W["saturation_example"]},
    # the dense section's failure cases (its order and labels), with BM25 ranks and term weights from our run of the same code
    "cases": [dict(next(c for c in CASES["cases"] if c["id"] == dc["id"]), kind=dc.get("kind"), why_dense=dc.get("why_dense"),
                   dense_rank=dc.get("dense_rank_first_answer_chunk"), bm25_rank_dense_log=dc.get("bm25_rank_first_answer_chunk"))
              for dc in DCASES.values() if CASES and any(c["id"] == dc["id"] for c in CASES["cases"])],
    "by_type": json.loads(DFILE.read_text()).get("by_type_dense_vs_bm25@5"),
    "cases_src": {"bm25": "logs/v5_lexical_cases.json", "dense": "logs/" + DFILE.name},
    "stop_n": len(STOP),
}
assert "16" not in json.dumps(X["llm_rerank"]["candidates"][15:16]) and "POL-PUR-001 v4.1" in X["llm_rerank"]["candidates"][15]
assert "Quotation Q-BE-26-0917" in X["llm_rerank"]["candidates"][1]
data["cby"] = {c["id"]: c for c in data["cases"]}
DID = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf#c"
data["key"] = {"s6_bm25_dump": L["bm25_all"]["Q-EMMA_D_ranks"][DID + "5"], "faq_bm25_dump": L["bm25_all"]["Q-EMMA_D_ranks"][DID + "12"],
               "cos_min": min(c["cos"] for c in chunks), "cos_max": max(c["cos"] for c in chunks), "bm_max": max(c["bm25"] for c in chunks),
               "rr_params_m": round(L["models"]["reranker_params"] / 1e6),
               "llm_pos_faq": [r["order"].index(16) + 1 for r in X["llm_rerank"]["runs"]],
               "llm_pos_quote": [r["order"].index(2) + 1 for r in X["llm_rerank"]["runs"]],
               "llm_s": [r["seconds"] for r in X["llm_rerank"]["runs"]],
               "rr_same_order": X.get("rr_repeat", {}).get("same_order_every_run"), "rr_repeat_n": X.get("rr_repeat", {}).get("n"),
               "all_pairs_gpu_s": round(L["n_all"] / 20 * L["latency_gpu"]["rerank_20"]["p50_ms"] / 1000, 1)}
for c in data["cases"]:
    assert c["bm25_rank"] == c["bm25_rank_dense_log"], c["id"]   # our BM25 = the dense section's BM25
# the walk-through run reproduces the main run on D (same chunks, same code)
assert W["avgdl"] == L["avgdl"]["D"] and W["q_tokens"] == L["tokenize"]["Q"]["tokens"]
for c in chunks:
    w = data["walk"]["chunks"][c["k"]]
    assert abs(w["score"] - c["bm25"]) < 1e-3 and w["rank"] == c["bm25_rank"] and w["dl"] == c["dl"], c["k"]
assert W["saturation_example"]["tf"] == L["tf_D"]["supplier"][5]
OUT.write_text("/* written by experiments/v5_lexical_build.py from logs/v5_lexical*.json: do not edit by hand */\n"
               "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.lexical = " + json.dumps(data, ensure_ascii=False) + ";\n")
print("wrote", OUT, f"{OUT.stat().st_size / 1024:.0f} KB")

# the preview page: index.html's head and scripts around this section's fragment (v5/preview_lexical.html)
V5 = HERE.parent / "v5"
idx = (HERE.parent / "index.html").read_text()
head = idx[: idx.index('<div class="deck" id="deck">')].replace('href="../../engine/', 'href="../../../engine/').replace('href="l3.css"', 'href="../l3.css"')
head = head.replace("</head>", '<link rel="stylesheet" href="lexical.css">\n</head>').replace("<title>Lecture 3 · The Knowledge</title>", "<title>Lecture 3 · The Knowledge · lexical preview</title>")
tail = idx[idx.index('<script src="figdata.js">'):]
tail = (tail.replace('src="figdata.js"', 'src="../figdata.js"').replace('src="figs.js"', 'src="../figs.js"').replace('src="figs2.js"', 'src="../figs2.js"')
        .replace('<script src="../../engine/plates.js">', '<script src="lexical_data.js"></script>\n<script src="lexical.js"></script>\n<script src="../../../engine/plates.js">'))
# the assembled index.html now loads every fragment's files from v5/: the preview loads only this section's (below)
head = re.sub(r'<link rel="stylesheet" href="v5/[^"]+">\n', "", head)
tail = re.sub(r'<script src="v5/[^"]+"></script>\n', "", tail)
(V5 / "preview_lexical.html").write_text(head + '<div class="deck" id="deck">\n' + (V5 / "lexical.html").read_text() + "\n</div>\n" + tail)
print("wrote", V5 / "preview_lexical.html")
