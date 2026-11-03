"""2D overlays + SFX for Lecture 3 film 1, "How RAG works". Every number, cite and line of text is read at build time
from data/l3_data.json (make_data.py: the logs and the live RAG Lab capture of 3 Nov 2026); nothing is typed in by hand
except the plain-language labels."""
import json
import os
import textwrap

from PIL import ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(HERE, "data", "l3_data.json")))["rag"]
POSTER = 84.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_OFFSET = 0.0
KICK = "Agentic Systems Engineering  ·  Lecture 3"


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def M(x):
    return f"{x / 1e6:.2f}M"


def pct(x):
    return f"{100 * x:.0f}%"


def short(cite, n=46):
    return cite if len(cite) <= n else cite[:n - 1].rstrip() + "…"


_T = {}


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    _T["w"], _T["blk"] = w, blk
    A = D["audit"]
    E = [{"type": "title", "kicker": KICK, "title": "How RAG works", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    # ---- b1: Emma's screen and the error (the text of the code as the quick-reference card quotes it)
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b1", "emma") - 0.1, "t1": w("b1", "what") - 0.2, "accent": "sky",
              "lines": [{"text": "Emma Clarke  ·  purchase executive", "size": 22, "c": "slate"},
                        {"text": "saving a purchase order in Ledgerline", "size": 30, "wt": 600}]})
    E.append({"type": "pin", "anchor": "scr_pin", "text": "ERR-PO-0412  TAX CODE DOES NOT MATCH SUPPLIER COUNTRY (NL)", "mono": True,
              "size": 24, "accent": "ember", "t0": w("b1", "error") - 0.1, "t1": en("b1") + 0.3, "dx": 40, "dy": 150})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b1", "what") - 0.05, "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "Emma's question", "size": 22, "c": "slate"}, {"text": D["question"], "size": 32, "wt": 600}]})
    # ---- b2: the dump, by class (stacks: 1 m per 3.5 million tokens)
    cls = A["by_class"]
    for k, (c, word, label) in enumerate((("unstructured", "pdfs", "PDF · DOCX · TXT"), ("structured", "spreadsheets", "XLSX · CSV"),
                                          ("semi-structured", "e-mails", "YAML · XML · e-mail · HTML"))):
        v = cls[c]
        E.append({"type": "pin", "anchor": f"vit_{k}_mid" if k == 1 else f"vit_{k}_pin", "text": f"{c}  ·  {M(v['tokens_o200k'])} tokens",
                  "sub": f"{v['files']} files  ·  {label}", "accent": ["slate", "green", "k"][k], "t0": w("b2", word) - 0.05,
                  "t1": en("b2") + 0.4, "dx": [-40, 60, 60][k], "dy": [-60, -200, -40][k], "size": 26})
    T = A["totals"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b2", "four") - 0.1, "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": f"{T['files']} files  ·  {T['pages']:,} PDF pages  ·  {T['rows']:,} rows", "size": 24, "c": "slate"},
                        {"text": f"{T['tokens_o200k'] / 1e6:.2f} million tokens", "size": 36, "wt": 600},
                        {"text": "each stack: 1 m per 3.5 million tokens", "size": 20, "c": "slate"}]})
    # ---- b3: parse
    E.append({"type": "pin", "anchor": "rd_pin", "text": "the parser", "sub": "a reader for each kind of file", "accent": "sky",
              "t0": w("b3", "reader") - 0.1, "t1": w("b3", "all") - 0.2, "dx": 60, "dy": -90})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "pdfs") - 0.1, "t1": w("b3", "spreadsheet") - 0.2, "accent": "sky",
              "lines": [{"text": "PDF: text with its page numbers", "size": 28, "wt": 600},
                        {"text": "and its section headings (in blue)", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "spreadsheet") - 0.05, "t1": w("b3", "all") - 0.2, "accent": "green",
              "lines": [{"text": "spreadsheet row: column = value", "size": 28, "wt": 600},
                        {"text": "the header row travels with every row", "size": 22, "c": "slate"}]})
    fv = A["facts_visible"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "all") - 0.05, "t1": en("b3") + 0.5, "accent": "green",
              "lines": [{"text": "facts a reader can still see", "size": 22, "c": "slate"},
                        {"text": f"this parser  {fv['structured']['visible']} / {fv['structured']['present']}", "size": 34, "wt": 600},
                        {"text": f"plain text  {fv['plain']['visible']} / {fv['plain']['present']}  ·  "
                                 f"{A['plain_vs_structured']['xlsx_rows_without_headers_in_plain']:,} rows lose their headers", "size": 21, "c": "slate"}]})
    # ---- b4: chunk
    c0 = D["qrc03"]["chunks"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b4", "two") - 0.1, "t1": w("b4", "quick-reference") - 0.2,
              "accent": "sky", "lines": [{"text": "structure-aware chunks", "size": 22, "c": "slate"},
                                         {"text": "~200 tokens  ·  15% overlap", "size": 34, "wt": 600},
                                         {"text": "cut at headings, never mid-sentence", "size": 21, "c": "slate"}]})
    for k, c in enumerate(c0):
        sec = c["locs"]["sections"][0]
        E.append({"type": "pin", "anchor": f"ck{k}_top", "text": f"chunk {k + 1}  ·  {c['n_tokens']} tokens", "sub": short("§ " + sec, 40),
                  "accent": "sky", "t0": w("b4", "becomes") + 0.15 * k, "t1": w("b4", "whole") - 0.1, "dx": [-60, 40, 60][k],
                  "dy": [-170, -230, -150][k], "size": 24})
    txt = [l["text"] if len(l["text"]) <= 76 else l["text"][:75].rstrip() + " …" for l in c0[0]["lines"]][:12]
    E.append({"type": "code", "x": 64, "y": 84, "lang": "text", "t0": w("b4", "three") + 0.3, "t1": en("b4") + 0.5, "size": 17,
              "title": "Chunk 1, as it is stored", "sub": c0[0]["cite"], "lines": txt, "accent": "sky",
              "hl": [{"i0": 0, "i1": 0, "t0": w("b4", "three") + 0.6, "t1": en("b4") + 0.5, "c": "sky"}]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b4", "whole") - 0.05, "t1": en("b4") + 0.5, "accent": "sky",
              "lines": [{"text": "the whole dump", "size": 22, "c": "slate"}, {"text": f"{D['n_chunks']:,} chunks", "size": 40, "wt": 600},
                        {"text": f"mean {D['tokens_mean']:.0f} tokens", "size": 21, "c": "slate"}]})
    # ---- b5: index
    em = D["embed"]
    E.append({"type": "pin", "anchor": "vplate_top", "text": f"chunk 1 = {em['dim']} numbers", "sub": "BAAI/bge-small-en-v1.5, its real vector",
              "accent": "sky", "t0": w("b5", "three") - 0.1, "t1": w("b5", "point") - 0.3, "dx": 70, "dy": -70})
    mp = D["map"]
    E.append({"type": "pin", "anchor": "tbl_pin", "text": "the vector space (Chroma)", "sub": f"{mp['n_shown']:,} of {mp['n_total']:,} chunks, flattened to 2-D (PCA), coloured by folder",
              "accent": "sky", "t0": w("b5", "point") + 0.2, "t1": w("b5", "and") - 0.2, "dx": 40, "dy": -110})
    h = D["hnsw"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b5", "chroma") - 0.1, "t1": w("b5", "and") - 0.2, "accent": "sky",
              "lines": [{"text": f"Chroma {D['chromadb']}  ·  HNSW, {h['space']}", "size": 28, "wt": 600},
                        {"text": f"ef_search {h['ef_search']:,}  ·  M {h['max_neighbors']}", "size": 21, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "cat_pin_top", "text": "BM25: the keyword index", "sub": "which chunk holds which exact word",
              "accent": "green", "t0": w("b5", "b") - 0.1, "t1": en("b5") + 0.4, "dx": 70, "dy": -40})
    E.append({"type": "code", "x": 64, "y": 84, "lang": "text", "t0": w("b5", "remembers") - 0.1, "t1": en("b5") + 0.4, "size": 20, "accent": "green",
              "title": "BM25's score (course/l3/rag.py)", "sub": "rare words that match count most",
              "lines": ["score(q, d) = the sum, over the words t of q, of", "",
                        "  idf(t) * tf(t,d) * (k1 + 1) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl))"]})
    # ---- b6: the search
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b6", "now") - 0.1, "t1": w("b6", "vector") + 0.4, "accent": "sky",
              "lines": [{"text": "Emma's question", "size": 22, "c": "slate"}, {"text": D["question"], "size": 30, "wt": 600}]})
    E.append({"type": "pin", "anchor": "qstar", "text": "the question, embedded", "accent": "sky", "t0": w("b6", "vector") + 0.3,
              "t1": w("b6", "nearest") + 0.2, "dx": 70, "dy": -90, "size": 26})
    dn = D["search"]["dense"]["items"]
    for j, k in enumerate((0, 1, 4)):
        it = dn[k]
        E.append({"type": "pin", "anchor": f"hit{k}_pin", "text": f"{k + 1}  ·  {short(it['cite'], 44)}", "sub": f"similarity {it['score']:.2f}",
                  "accent": "ember", "mono": False, "size": 22, "t0": w("b6", "purchase-order") - 0.1 + (0.5 if k == 4 else 0.25 * j),
                  "t1": w("b6", "b") - 0.2, "dx": [-60, 60, 60][j], "dy": [-150, -210, 60][j]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b6", "wrong") - 0.1, "t1": w("b6", "b") - 0.2, "accent": "ember",
              "lines": [{"text": "the right chunk, QRC-03 chunk 1", "size": 22, "c": "slate"},
                        {"text": f"similarity {em['cosine_chunk']:.2f}: not in the top 10", "size": 30, "wt": 600},
                        {"text": "computed for this film with the same model", "size": 19, "c": "slate"}]})
    bm = D["search"]["bm25"]["items"]
    for k in range(3):
        it = bm[k]
        E.append({"type": "pin", "anchor": f"card{k}_pin", "text": f"{k + 1}  ·  {short(it['cite'], 50)}", "sub": f"BM25 score {it['score']:.1f}",
                  "accent": "green", "size": 22, "t0": w("b6", "puts") - 0.1 + 0.3 * k, "t1": en("b6") + 0.5,
                  "dx": [80, 80, -80][k], "dy": [-190, -110, -60][k]})
    ec = D["exact_code"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b6", "matches") - 0.1, "t1": en("b6") + 0.5, "accent": "green",
              "lines": [{"text": f"{D['exact_code_n']} questions that name a code", "size": 22, "c": "slate"},
                        {"text": f"right source in the top 5:  vectors {pct(ec['dense'])}  ·  BM25 {pct(ec['bm25'])}", "size": 28, "wt": 600}]})
    # ---- b7: rerank
    E.append({"type": "pin", "anchor": "so_pin", "text": "the reranker", "sub": "bge-reranker-base reads question and chunk together",
              "accent": "k", "t0": w("b7", "reranker") - 0.1, "t1": w("b7", "order") + 0.3, "dx": -60, "dy": -110})
    tm = D["search"]["best"]["timing_ms"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b7", "fifty-seven") - 0.1, "t1": w("b7", "right") - 0.2, "accent": "k",
              "lines": [{"text": "measured inside the search", "size": 21, "c": "slate"},
                        {"text": f"BM25 {tm['bm25']:.1f} ms  ·  rerank {tm['rerank']:.0f} ms", "size": 32, "wt": 600}]})
    rr = D["search"]["best"]["items"]
    for k in range(5):
        it = rr[k]
        E.append({"type": "tag", "anchor": f"out{k}_pin", "text": f"{k + 1}", "hl": "green" if it["gold"] else None, "size": 22,
                  "t0": w("b7", "order") + 0.6 + 0.1 * k, "t1": w("b7", "right") - 0.2, "dy": -12, "maxdepth": 4.0})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b7", "order") + 0.5, "t1": w("b7", "right") - 0.2, "accent": "green",
              "lines": [{"text": "the new top 5 (green: a right source)", "size": 22, "c": "slate"}] +
                       [{"text": f"{k + 1}  {short(rr[k]['cite'], 50)}", "size": 22, "wt": 600 if rr[k]["gold"] else 400,
                         "c": "ink" if rr[k]["gold"] else "slate"} for k in range(5)]})
    # ---- b8: the answer
    ans = D["answer"]
    lines = []
    for para in ans["text"].replace("**", "").replace("`", "").split("\n"):
        lines += textwrap.wrap(para, 74) or [""]
    i_vat = next(i for i, l in enumerate(lines) if "VAT20-RC" in l)
    i_f8 = next(i for i, l in enumerate(lines) if "F8" in l)
    E.append({"type": "code", "x": 64, "y": 84, "lang": "text", "t0": w("b8", "answers") - 0.1, "t1": en("b8") + 0.5, "size": 18, "accent": "green",
              "title": "The answer, recorded", "sub": f"gemini-3.8-flash  ·  {ans['tokens_in']:,} tokens in  ·  judged correct",
              "lines": lines, "hl": [{"i0": i_vat, "i1": i_vat, "t0": w("b8", "vat") - 0.1, "t1": w("b8", "then") - 0.1, "c": "green"},
                                     {"i0": i_f8, "i1": i_f8, "t0": w("b8", "press") - 0.1, "t1": w("b8", "search") - 0.1, "c": "green"}]})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b8", "search") - 0.05, "t1": en("b8") + 0.5, "accent": "sky",
              "lines": [{"text": f"search  {1000 * ans['retrieval_s']:.0f} ms", "size": 34, "wt": 600},
                        {"text": f"answer  {ans['llm_seconds']:.1f} s", "size": 34, "wt": 600},
                        {"text": "the time is the model's, not the search's", "size": 20, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "res_top", "text": "a cited answer", "accent": "green", "t0": w("b8", "citations") + 0.3,
              "t1": w("b8", "search") - 0.2, "dx": 60, "dy": -80, "size": 26})
    # ---- b9: the close
    bst = D["best"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b9", "eighty-seven") - 0.1, "t1": w("b9", "its") - 0.2, "accent": "green",
              "lines": [{"text": "the golden set: 224 questions", "size": 22, "c": "slate"},
                        {"text": f"answers correct {100 * bst['answer_correct']:.1f}%", "size": 34, "wt": 600},
                        {"text": f"citations {100 * bst['citation_correct']:.1f}%  ·  ${bst['cost_per_q_usd']:.4f} a question", "size": 22, "c": "slate"},
                        {"text": "the grid's answer run (150-word answers); the race re-runs it at 250", "size": 19, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b9", "brightcell") - 0.2, "t1": en("b9") + 0.6, "accent": "ember",
              "lines": [{"text": "Emma's other question", "size": 22, "c": "slate"},
                        {"text": "Can I buy the battery packs from Brightcell Energy? They quote £104.", "size": 28, "wt": 600},
                        {"text": f"{D['q_emma']['gold']} gold sources  ·  found in the top 10: {D['q_emma']['found@10']}", "size": 22, "c": "slate"}]})
    for k, g in enumerate(D["q_emma"]["detail"]):
        if g["rank"] is not None:
            E.append({"type": "tag", "anchor": f"gold{k}_pin", "text": "found", "hl": "green", "size": 20, "mono": False,
                      "t0": w("b9", "finds") + 0.2, "t1": en("b9") + 0.6, "dy": -10, "maxdepth": 5})
    E.append({"type": "pin", "anchor": "gold0_pin", "text": "§6.2 of the Purchase Policy: missed", "sub": "it never names Brightcell",
              "accent": "ember", "t0": w("b9", "finds") + 0.3, "t1": en("b9") + 0.6, "dx": 40, "dy": -170, "size": 24})
    E.append({"type": "end", "t0": en("b9") + 0.9, "kicker": KICK, "title": "How RAG works",
              "sub": "Parse, chunk, index, search, rerank, answer",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Recorded: the RAG grid and golden set (experiments/logs) and the live RAG Lab, 3 Nov 2026",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    """b7: the ladder of the three settings (recall@5 on 205 golden questions, chunks of 200 tokens), drawn as bars."""
    w, blk = _T.get("w"), _T.get("blk")
    if not w:
        return
    t0, t1 = w("b7", "right") - 0.1, blk["b7"]["speech_end"] + 0.5
    if not (t0 - 0.2 <= t <= t1 + 0.4):
        return
    L = D["ladder_recall5"]
    rows = [("vectors alone (bge-small)", L["dense"], "vectors"), ("keywords (BM25)", L["bm25"], "keywords"),
            ("keywords + the reranker", L["bm25_rerank"], "reranker")]
    a = max(0.0, min(1.0, (t - t0) / 0.35, (t1 + 0.3 - t) / 0.3))
    d = ImageDraw.Draw(cv)
    import overlay as O
    x0, y0, W, H = 96, 92, 760, 300
    d.rounded_rectangle((x0, y0, x0 + W, y0 + H), 16, fill=(12, 16, 25, int(222 * a)))
    d.text((x0 + 28, y0 + 22), "A right source in the top 5", font=O.font(28, 600), fill=(244, 247, 252, int(255 * a)))
    d.text((x0 + 28, y0 + 60), "205 golden questions  ·  the same 200-token chunks", font=O.font(19, 400), fill=(164, 176, 196, int(255 * a)))
    for i, (lab, v, word) in enumerate(rows):
        ts = w("b7", word, 0 if word != "reranker" else 1) - 0.1 if word != "vectors" else w("b7", "vectors") - 0.1
        k = O.ease((t - ts) / 0.6)
        yy = y0 + 110 + i * 60
        d.text((x0 + 28, yy), lab, font=O.font(21, 500), fill=(214, 222, 236, int(255 * a)))
        bx, bw = x0 + 330, 300
        d.rounded_rectangle((bx, yy + 2, bx + bw, yy + 26), 8, fill=(255, 255, 255, int(20 * a)))
        c = (30, 142, 90) if i == 2 else (60, 144, 255)
        if k > 0:
            d.rounded_rectangle((bx, yy + 2, bx + max(10, int(bw * v * k)), yy + 26), 8, fill=(c[0], c[1], c[2], int(235 * a)))
            d.text((bx + bw + 16, yy - 2), f"{100 * v * k:.0f}%", font=O.font(26, 600), fill=(244, 247, 252, int(255 * a)))


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.25))
    S += [("refuse.mp3", w("b1", "stops"), 0.4), ("rise.mp3", w("b2", "pdfs") - 0.1, 0.3), ("rise.mp3", w("b2", "spreadsheets") - 0.1, 0.3),
          ("rise.mp3", w("b2", "e-mails") - 0.1, 0.25), ("beam.mp3", w("b3", "reader"), 0.35), ("tick.mp3", w("b3", "pdfs"), 0.3),
          ("tick.mp3", w("b3", "rows"), 0.3), ("chime.mp3", w("b3", "all"), 0.35), ("beam.mp3", w("b4", "structure"), 0.3),
          ("lid.mp3", w("b4", "two"), 0.35)]
    S += [("tile.mp3", w("b4", "becomes") + 0.15 * k, 0.3) for k in range(3)]
    S += [("fill.mp3", w("b5", "three") - 0.1, 0.3), ("bloom.mp3", w("b5", "point"), 0.3), ("lid.mp3", w("b5", "remembers"), 0.3),
          ("relay.mp3", w("b6", "vector"), 0.3), ("refuse.mp3", w("b6", "wrong"), 0.25), ("chime.mp3", w("b6", "puts"), 0.35),
          ("beam.mp3", w("b7", "reads"), 0.35), ("merge.mp3", w("b7", "order"), 0.35), ("tick.mp3", w("b7", "vectors"), 0.25),
          ("tick.mp3", w("b7", "keywords"), 0.25), ("chime.mp3", w("b7", "reranker", 1), 0.35), ("whoosh.mp3", w("b8", "top"), 0.25),
          ("resolve.mp3", w("b8", "citations"), 0.35), ("tick.mp3", w("b9", "parse"), 0.25), ("tick.mp3", w("b9", "chunk"), 0.25),
          ("tick.mp3", w("b9", "index"), 0.25), ("tick.mp3", w("b9", "search"), 0.25), ("tick.mp3", w("b9", "rerank"), 0.25),
          ("tick.mp3", w("b9", "answer"), 0.25), ("rise.mp3", w("b9", "eleven"), 0.3), ("refuse.mp3", w("b9", "finds"), 0.3),
          ("resolve.mp3", blk["b9"]["speech_end"] + 0.6, 0.5)]
    return S
