"""Build v5/dense_data.js (window.L3V5.dense) and logs/v5_dense_failures.json from the dense logs. No compute: it only
reshapes what experiments/v5_dense_modal.py measured on Modal (logs/v5_dense.json, v5_dense_scan.json,
v5_dense_probes.json) and the grid (logs/rag_grid.json).

    python3 lectures/L3-the-memory/experiments/v5_dense_build.py
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
V5 = HERE.parent / "v5"

d = json.loads((LOGS / "v5_dense.json").read_text())
scan = json.loads((LOGS / "v5_dense_scan.json").read_text())
pr = json.loads((LOGS / "v5_dense_probes.json").read_text())
grid = json.loads((LOGS / "rag_grid.json").read_text())

units = d["units"]
stream = "\n".join(u["text"] for u in units)

# ------------------------------------------------------------------ sections of D, for colour
SEC_ORDER = ["Header and version history", "§1–2 Purpose, scope", "§3 Requests before orders", "§4 Cost centres",
             "§5 Approval limits", "§6 Supplier qualification", "§7 Prices", "§8 Tax", "§9 Records",
             "Appendix A · definitions", "Appendix B · staff questions", "Appendix C · related documents"]
SEC_COLOUR = {"Header and version history": "#8a8f99", "§1–2 Purpose, scope": "#5c6bc0", "§3 Requests before orders": "#4f86e8",
              "§4 Cost centres": "#22a699", "§5 Approval limits": "#7a5af5", "§6 Supplier qualification": "#c4511f",
              "§7 Prices": "#d39a00", "§8 Tax": "#6f7d4f", "§9 Records": "#a86cc1", "Appendix A · definitions": "#138a60",
              "Appendix B · staff questions": "#d0557a", "Appendix C · related documents": "#b07a50"}
sec_path = {}
for u in units:
    sec_path.setdefault(u["loc"].get("section", ""), u["heading"])


def sec_of(sections):
    s = sections[0] if sections else ""
    path = sec_path.get(s, s)
    if "Appendix B" in path:
        return "Appendix B · staff questions"
    if "Appendix C" in path:
        return "Appendix C · related documents"
    if "Appendix A" in path:
        return "Appendix A · definitions"
    m = re.match(r"(\d+)\.", s)
    if m:
        n = int(m.group(1))
        return {1: "§1–2 Purpose, scope", 2: "§1–2 Purpose, scope", 3: "§3 Requests before orders", 4: "§4 Cost centres",
                5: "§5 Approval limits", 6: "§6 Supplier qualification", 7: "§7 Prices", 8: "§8 Tax", 9: "§9 Records"}[n]
    return "Header and version history"


def short_of(c, sec):
    s = (c["sections"] or [""])[0]
    if sec == "Appendix B · staff questions":
        q = s if s and not s.startswith("Appendix") else c["body"].split("\n")[0]
        if q.startswith("Appendix B"):
            q = c["body"].split("\n")[1] if "\n" in c["body"] else q
        if q[:1].islower():  # a heading the PDF wrapped onto a second line ("signed off?")
            q = "… " + q
        return "App. B: " + (q[:38] + "…" if len(q) > 39 else q)
    if c["tokens"] > 1500:
        return "Whole document"
    if sec == "Header and version history":
        return "Header table" if c["body"].startswith("Purchase Policy") else "Version history"
    secs = [x for x in c["sections"] if re.match(r"\d+\.", x)]
    if len(secs) > 1:
        return "§" + secs[0].split(".")[0] + "–" + secs[-1].split(".")[0] + " " + secs[0].split(" ", 1)[1].split(" ")[0] + " …"
    return sec


def slim(c, full=False, sec=None):
    sec = sec or sec_of(c["sections"])
    body = c["body"] if full else (c["body"][:420] + ("…" if len(c["body"]) > 420 else ""))
    out = {k: c[k] for k in ("i", "cid", "cite", "tokens", "body_tokens", "wp", "truncated", "cos", "rank", "has62", "has64",
                             "part62", "part64", "span", "pages")}
    out.update(body=body, header=c["header"], sec=sec, short=f"#{c['i']} " + short_of(c, sec),
               seen_pct=round(100 * c["body_seen_chars"] / max(1, len(c["body"]))))
    if "xyz" in c:
        out["xyz"] = c["xyz"]
    out["restates"] = bool(re.search(r"[Uu]nder section 6\.2", c["body"])) and not c["has62"]
    return out


def cfg(c, full=False, secs=None):
    ch = [slim(x, full, secs[i] if secs else None) for i, x in enumerate(c["chunks"])]
    o = {k: c[k] for k in ("n", "tokens_mean", "rank62", "rank64", "clause_tokens", "topk", "order", "q")}
    o["chunks"] = ch
    for k in ("explained3", "dim", "cos_spread"):
        if k in c:
            o[k] = c[k]
    return o


play = {}
for name, c in d["play"].items():
    secs = None
    if name == "s200-o15-nohead":
        secs = [sec_of(x["sections"]) for x in d["play"]["s200-o15"]["chunks"]]
    play[name] = cfg(c, full=name == "s200-o15", secs=secs)
# overlap pairs (where a chunk repeats the end of the one before)
for name, c in play.items():
    ch = c["chunks"]
    for a, b in zip(ch, ch[1:]):
        if a["span"][1] > b["span"][0] >= 0:
            b["ovl_text"] = stream[b["span"][0]:a["span"][1]]
default_secs = [x["sec"] for x in play["s200-o15"]["chunks"]]
models_play = {m: cfg(c, secs=default_secs) for m, c in d["models_play"].items()}
# the bge-small entry of the model switch is the default config itself (same PCA basis)
models_play["bge-small"] = play["s200-o15"]

# ------------------------------------------------------------------ page marks from the real text lines
MARKS = {  # page: name -> (start regex, end regex or None = same line, class)
    1: {"title": (r"^Purchase Policy$", None, "t"), "hdr": (r"^Field Value", r"^Classification", ""),
        "docid": (r"^Document POL", None, "k"), "version": (r"^Version 4\.1", None, "k"), "effective": (r"^Effective", None, "k"),
        "status": (r"^Status CURRENT", None, "k"), "history": (r"^Version history", r"^2%$", ""),
        "h41": (r"^4\.1 2026", r"^2%$", "k"), "h40": (r"^4\.0 2025", r"^price tolerance 5%", "k"),
        "s1": (r"^1\. Purpose", None, "h"), "s2": (r"^2\. Scope", None, "h"), "s3": (r"^3\. Requests", None, "h"),
        "s4": (r"^4\. Cost centres", None, "h"),
        "c31": (r"^3\.1 ", None, "c"), "c32": (r"^3\.2 ", r"^centre that will", "c"), "c33": (r"^3\.3 ", r"^£50,000", "c"),
        "c34": (r"^3\.4 ", None, "c"), "c41": (r"^4\.1 Every", None, "c"), "c42": (r"^4\.2 ", r"^to the supplier", "c"),
        "c43": (r"^4\.3 ", r"^Finance\.$", "c")},
    2: {"s5": (r"^5\. Approval", None, "h"), "s6": (r"^6\. Supplier", None, "h"), "s7": (r"^7\. Prices", None, "h"),
        "s8": (r"^8\. Tax", None, "h"), "s9": (r"^9\. Records", None, "h"),
        "c61": (r"^6\.1 ", None, "c"), "c62": (r"^6\.2 ", r"^certificate counts", "a"), "c63": (r"^6\.3 ", r"^with them", "c"),
        "c64": (r"^6\.4 ", r"^by itself justify", "a"), "c72": (r"^7\.2 ", r"^remarks", "c"),
        "appA": (r"^Appendix A", r"^Direct order \(DIR\)", ""), "lit": (r"^Lithium-cell part", None, "k"),
        "sec6": (r"^6\. Supplier", r"^by itself justify", "")},
    3: {"appB": (r"^Appendix B", None, "h"), "bat": (r"^What are the rules before ordering", r"^because they provide", ""),
        "qs": (r"^When can I raise", None, "c")},
    4: {"appC": (r"^Appendix C", r"MAN-PUR-72", "")},
}


def marks_for(page):
    lines = page["lines"]
    out = {}
    for name, (a, b, cls) in MARKS.get(page["page"], {}).items():
        i = next((k for k, L in enumerate(lines) if re.search(a, L["text"])), None)
        if i is None:
            raise SystemExit(f"mark {name} not found on page {page['page']}")
        j = i if b is None else next(k for k in range(i, len(lines)) if re.search(b, lines[k]["text"]))
        box = lines[i:j + 1]
        out[name] = {"x0": min(L["x0"] for L in box), "top": min(L["top"] for L in box),
                     "x1": max(L["x1"] for L in box), "bottom": max(L["bottom"] for L in box), "cls": cls}
    return out


pages = []
for p in pr["pages_D"]:
    pages.append({"page": p["page"], "img": p["img"], "w": p["w"], "h": p["h"], "marks": marks_for(p)})
err_pages = []
ERRMARKS = {17: {"e0412": (r"^ERR-PO-0412", None, "a"), "e0105": (r"^ERR-PO-0105", None, "c"), "e0201": (r"^ERR-PO-0201", None, "c")},
            18: {"e0412b": (r"^Cause: the tax code", r"^Raised by: po_save", "a"), "e0610": (r"^ERR-PO-0610", None, "c")}}
for p in pr["pages_ERR"]:
    m = {}
    for name, (a, b, cls) in ERRMARKS.get(p["page"], {}).items():
        lines = p["lines"]
        i = next(k for k, L in enumerate(lines) if re.search(a, L["text"]))
        j = i if b is None else next(k for k in range(i, len(lines)) if re.search(b, lines[k]["text"]))
        box = lines[i:j + 1]
        m[name] = {"x0": min(L["x0"] for L in box), "top": min(L["top"] for L in box), "x1": max(L["x1"] for L in box),
                   "bottom": max(L["bottom"] for L in box), "cls": cls}
    err_pages.append({"page": p["page"], "img": p["img"], "w": p["w"], "h": p["h"], "marks": m})

# ------------------------------------------------------------------ the selected chunk's pieces, highlighted ranges
sel = d["selected"]
pcs = sel["pieces"]
hi = set()
for seq in (["pol", "-", "pu", "##r", "-", "001"], ["un", "38", ".", "3"], ["pol", "-", "su", "##p", "-", "00", "##3"],
            ["ledger", "##line"], ["quota", "##tion"], ["onboard", "##ed"]):
    for i in range(len(pcs) - len(seq) + 1):
        if pcs[i:i + len(seq)] == seq:
            hi.update(range(i, i + len(seq)))
sel_out = {k: sel[k] for k in ("i", "cid", "cite", "text", "o200k_tokens", "pieces", "n_pieces", "token_vectors_shape",
                               "token_vectors_head", "cls_raw_head", "cls_norm", "vector", "vector_norm", "cos_final_vs_cls",
                               "cos_final_vs_mean", "query_pieces", "query_vector", "cos_q", "cos_q_noprefix")}
sel_out["hiIdx"] = sorted(hi)

# ------------------------------------------------------------------ ERR doc (Q-0412)
E = d["err"]
FAM = {"PO": "#c4511f", "MAT": "#7a5af5", "SYS": "#6b6e76", "GRN": "#22a699", "PER": "#d39a00", "SUP": "#4f86e8"}
err_chunks = []
for c in E["chunks"]:
    fams = [re.match(r"(?:ERR|W|I)-([A-Z]+)-", x).group(1) for x in c["codes"] if re.match(r"(?:ERR|W|I)-([A-Z]+)-", x)]
    fam = fams[0] if fams else ""
    err_chunks.append({"i": c["i"], "cid": c["cid"], "cite": c["cite"], "body": c["body"][:420], "tokens": c["tokens"], "cos": c["cos"],
                       "rank": c["rank"], "codes": c["codes"], "gold": c["gold"], "fact": c["fact"], "xyz": c["xyz"],
                       "fam": fam if fam in FAM else "other"})
err = {"doc": E["doc"], "question": E["question"], "n": E["n"], "n_units": E["n_units"], "explained3": E["explained3"],
       "q_xyz": E["q_xyz"], "chunks": err_chunks, "order": E["order"], "famColour": {**FAM, "other": "#b9bec7"},
       "pages": err_pages}

# ------------------------------------------------------------------ the whole-dump grid, one knob at a time (dense, bge-small)
rows = [r for r in grid["rows"] if r["embed"] == "bge-small" and r["retrieval"] == "dense" and not r["rerank"] and not r["rewrite"]]


def g(parser="structured", chunker="structure", size=200, overlap=0.15):
    r = next(r for r in rows if (r["parser"], r["chunker"], r["size"], r["overlap"]) == (parser, chunker, size, overlap))
    o = r["overall"]
    return {"recall@5": o["recall@5"], "recall@10": o["recall@10"], "mrr": o["mrr"], "n": o["n"],
            "tables@5": r["by_type"]["table_lookup"]["recall@5"], "codes@5": r["by_type"]["exact_code"]["recall@5"]}


gridv = {"sizes": {s: g(size=s) for s in (200, 400, 800, 1200)},
         "overlap": {"0%": g(overlap=0.0), "15%": g()},
         "parser": {"plain": g(parser="plain"), "structured": g()},
         "tokens_mean": {s: grid["builds"][f"structured-structure-{s}-o15"]["tokens_mean"] for s in (200, 400, 800, 1200)},
         "n_chunks": {s: grid["builds"][f"structured-structure-{s}-o15"]["n_chunks"] for s in (200, 400, 800, 1200)},
         "note": grid["questions"], "generated": grid["generated"]}
qs = [q for q in scan["questions"] if q["gold_files"]]
gridv["exact_check"] = {"recall@5_exact": round(sum(1 for q in qs if q["dense_rank"] and q["dense_rank"] <= 5) / len(qs), 4),
                        "n": len(qs)}

# ------------------------------------------------------------------ failure cases (for the slides and for the lexical section)
C = pr["cases"]


def top(case, k=10):
    return [{"rank": r["rank"], "cid": r["cid"], "cite": r["cite"], "score": r["score"], "gold": r["gold"], "fact": r["fact"],
             "superseded": r["superseded"], "future": r["future"], "text": r["text"][:300]} for r in case["dense_top10"][:k]]


FAIL = [
    ("Q-0412", "exact code", "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf",
     "Inside MAN-ERR-72 the neighbours are other error entries; the nearest, ERR-MAT-0412, shares the digits 0412 but is a "
     "different error. In the whole dump the top ten are service definitions listing other ERR-PO codes. To the model a code "
     "is a few word pieces (er ##r - po - 04 ##12), and one changed piece barely moves the vector."),
    ("Q-401", "code that differs by a digit", "05_master_data/ITEM_MASTER_2026-10-26.xlsx",
     "Item rows for BAT-500, BAT-375, BAT-625 and BAT-250 are almost the same vector (cosine 0.999): the only difference is a few "
     "digits. The current BAT-500 row ranks 102nd, below rows of its siblings and an old 2025 export."),
    ("Q-424", "code that differs by a digit", "05_master_data/Rate Contracts 2025-26 and 2026-27.xlsx",
     "Asked for BAT-375, dense brings BAT-500 e-mails about Voltway: same supplier, same kind of product, different code."),
    ("Q-510", "amounts and dates", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
     "The question's £40,000 and 'next month' carry almost no weight in the vector; it matches sales-order rows full of "
     "orders and amounts. Changing £50,000 to £5,000,000 in the rule moves its vector by 0.003."),
    ("Q-612", "before or after (opposite meaning)", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
     "The rule says 'before the first order'; the question asks about 'after'. The two sentences differ by one word and their "
     "vectors by 0.02; the question is even a little closer to the wrong (after) version."),
    ("Q-202", "superseded copy", "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
     "The 2019 copy (v3.0, £30,000, marked SUPERSEDED in its header) ranks first. An old copy and the current text are near-"
     "identical vectors (v4.0 against v4.1: 0.998); only metadata tells them apart."),
    ("Q-003", "a crowded topic", "12_integrations/Carrier API notes - Moorland Logistics.md",
     "The top of the list is battery handling and transport: the topic words dominate the question's vector. 'Carrier "
     "service', the words that pick the answer, are a small part of it; the carrier notes score 0.595 and 2,173 chunks "
     "of every kind (232 of them about batteries) rank above them."),
    ("Q-101", "dense wins: different words, same meaning", "02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf",
     "'onboard a new supplier' and 'Supplier Onboarding … sets up new trade vendors' share meaning, not exact words. Dense "
     "puts onboarding text in all ten top places; a keyword match ranks the procedure 619th."),
]
SHOWN = {"Q-0412": "MAN-ERR-72", "Q-612": "POL-PUR-001_Purchase_Policy_v4.1", "Q-202": "POL-PUR-001_Purchase_Policy_v4.1"}
fail_out = {"generated": pr["generated"], "made_by": "experiments/v5_dense_modal.py (pass 1 scan + pass 2 probe), reshaped by v5_dense_build.py",
            "index": "structured-structure-200-o15 (the grid's chunks and stored bge-small vectors, RAG Lab volume); exact search over "
                     "all 28,953 chunks, permission filter before ranking (PUR-EXEC); cites as Chunk.cite",
            "cases": []}
slides_fail = {}
for qid, kind, target, why in FAIL:
    c = C[qid]
    s = next(q for q in scan["questions"] if q["id"] == qid)
    tdoc = c["in_doc"].get(target) or {}
    rec = {"id": qid, "kind": kind, "question": c["question"], "type": c["type"], "target_doc": target,
           "gold_files": c["gold_files"], "gold_cids": c["gold_chunks"],
           "answer_chunks": [{"cid": f["cid"], "cite": f["cite"], "dense_rank": f["rank"], "dense_score": f["score"],
                              "text": f["text"][:400]} for f in c["fact_chunks"]],
           "dense_rank_first_gold": c["dense_rank_gold"], "dense_rank_first_answer_chunk": c["dense_rank_fact"],
           "bm25_rank_first_gold": c["bm25_rank_gold"], "bm25_rank_first_answer_chunk": c["bm25_rank_fact"],
           "dense_top10": top(c), "in_target_doc": {"n_chunks": tdoc.get("n"), "answer_ranks": tdoc.get("fact_ranks"),
                                                     "top10": tdoc.get("top10")},
           "why_dense": why}
    pick = [a for a in rec["answer_chunks"] if SHOWN.get(qid, "") in a["cid"]] or rec["answer_chunks"]
    rec["shown"] = min(pick, key=lambda a: a["dense_rank"])
    if qid == "Q-202":
        rec["dense_with_stale_filtered_top5"] = [{"rank": r["rank"], "cid": r["cid"], "cite": r["cite"], "score": r["score"]} for r in c["dense_filtered_top5"]]
        rec["dense_with_stale_filtered_rank_first_answer_chunk"] = c["dense_filtered_rank_fact"]
    fail_out["cases"].append(rec)
    slides_fail[qid] = rec
fail_out["probes"] = pr["probes"]
fail_out["wordpieces"] = pr["wordpieces"]
fail_out["siblings_cos"] = pr["siblings"]["cos_BAT500_row_to"]
fail_out["versions"] = pr["versions"]
fail_out["tables"] = pr["tables"]
fail_out["crowd"] = {k: v for k, v in pr["crowd"].items() if k != "gold"}
fail_out["by_type_dense_vs_bm25@5"] = {}
for t in sorted({q["type"] for q in qs}):
    tq = [q for q in qs if q["type"] == t]
    fail_out["by_type_dense_vs_bm25@5"][t] = {"n": len(tq), "dense": round(sum(1 for q in tq if q["dense_rank"] and q["dense_rank"] <= 5) / len(tq), 3),
                                               "bm25": round(sum(1 for q in tq if q["bm25_rank"] and q["bm25_rank"] <= 5) / len(tq), 3)}
(LOGS / "v5_dense_failures.json").write_text(json.dumps(fail_out, indent=1, ensure_ascii=False))

# ------------------------------------------------------------------ write the data file
mi = dict(d["model_info"])
mi.update(layers=pr["model_config"]["layers"], heads=pr["model_config"]["heads"], intermediate=pr["model_config"]["intermediate"])
data = {
    "generated": d["generated"], "doc": d["doc"], "question": d["question"], "meta": d["meta"], "doc_tokens": d["doc_tokens"],
    "n_units": len(units), "facts": {k: v["statement"] for k, v in d["facts"].items()},
    "needles": {k: v["needles"][0] for k, v in d["facts"].items()},
    "sections": SEC_ORDER, "secColour": SEC_COLOUR,
    "secShort": {s: s for s in SEC_ORDER},
    "pca": d["pca"], "model_info": mi, "prefix_check": d["prefix_check"], "dump_check": d["dump_check"],
    "selected": sel_out, "play": play, "models_play": models_play,
    "modelOrder": ["bge-small", "e5-small", "gte-small", "bge-base", "nomic"],
    "modelShort": {"bge-small": "bge-small · 384", "e5-small": "e5-small · 384", "gte-small": "gte-small · 384",
                   "bge-base": "bge-base · 768", "nomic": "nomic · 768"},
    "pages": pages, "err": err, "grid": gridv, "fail": slides_fail,
    "probes": pr["probes"], "wordpieces": pr["wordpieces"], "siblings": pr["siblings"], "versions": pr["versions"],
    "tables": pr["tables"], "crowd": {k: v for k, v in pr["crowd"].items()},
    "cos2d": [1, 5, 14],
    "classq": {q["id"]: {"question": q["question"], "type": q["type"], "dense_rank": q["dense_rank"],
                         "dense_fact_rank": q["dense_fact_rank"], "top1": q["dense_top10"][0]["cite"]}
               for q in scan["questions"] if q["id"] in ("Q-117", "Q-704", "Q-619", "Q-021", "Q-108")},
    "D_mentions": {w: (w in stream) for w in ("Brightcell", "BAT-500", "£104", "Voltway")},
}
js = "/* generated by experiments/v5_dense_build.py from logs/v5_dense*.json and logs/rag_grid.json; do not edit */\n" \
     "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.dense = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
(V5 / "dense_data.js").write_text(js)
print("wrote", V5 / "dense_data.js", f"{len(js) / 1024:.0f} KB;", LOGS / "v5_dense_failures.json")
print("D mentions:", data["D_mentions"], "| grid exact check:", gridv["exact_check"], "| grid 200:", gridv["sizes"][200])
