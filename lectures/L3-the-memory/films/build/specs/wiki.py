"""2D overlays + SFX for Lecture 3 film 2, "How the LLM Wiki works". Every number, slug and line of text comes from
data/l3_data.json (make_data.py: the wiki itself and its logs); the Wikipedia article is the real capture in
figs/wikipedia (copied to build/cache/wikipedia, not committed again), credited on screen (CC BY-SA 4.0)."""
import json
import os
import re
import textwrap

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(HERE, "data", "l3_data.json")))
D = DATA["wiki"]
POSTER = 64.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_OFFSET = 0.0
KICK = "Agentic Systems Engineering  ·  Lecture 3"
BC = "sup-brightcell-energy"


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def short(s, n=48):
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


_T = {}


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    _T["w"], _T["blk"] = w, blk
    Bd = D["build"]
    E = [{"type": "title", "kicker": KICK, "title": "How the LLM Wiki works", "t0": 0.3, "t1": st("b1") + 0.4, "size": 76}]
    # ---- b1
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b1", "andrej") - 0.1, "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "Andrej Karpathy, “LLM Wiki” (a GitHub gist, April 2026)", "size": 22, "c": "slate"},
                        {"text": "read every source once, keep a wiki up to date", "size": 32, "wt": 600}]})
    E.append({"type": "pin", "anchor": "model_pin_top", "text": "the model", "sub": "it reads, and it writes the pages", "accent": "sky",
              "t0": w("b1", "model") - 0.1, "t1": en("b1") + 0.3, "dx": 60, "dy": -80})
    # ---- b2: the three layers (AGENTS.md section 1, as written)
    E.append({"type": "pin", "anchor": "vit_1_mid", "text": f"1  ·  the raw sources: {Bd['sources']} files", "sub": "never edited", "accent": "slate",
              "t0": w("b2", "raw") - 0.1, "t1": w("b2", "wiki") - 0.4, "dx": 70, "dy": -60})
    E.append({"type": "pin", "anchor": "idx_top", "text": "2  ·  the wiki: markdown pages", "sub": "the model owns them", "accent": "sky",
              "t0": w("b2", "wiki") - 0.05, "t1": en("b2") + 0.4, "dx": 70, "dy": -110})
    E.append({"type": "pin", "anchor": "schema_top", "text": "3  ·  the schema: AGENTS.md", "sub": "the rules for every page", "accent": "v",
              "t0": w("b2", "schema") - 0.05, "t1": en("b2") + 0.4, "dx": -70, "dy": -60})
    lay = D["agents_layers"]
    clean = lambda s: re.sub(r"\s*\(.*?\)", "", s.replace("`", ""))  # noqa: E731
    rows = [f"{clean(r[0]):<12} {clean(r[1]):<40} {clean(r[2])}" for r in lay]
    E.append({"type": "code", "x": 64, "y": 84, "lang": "text", "t0": w("b2", "schema") + 0.4, "t1": en("b2") + 0.4, "size": 18, "accent": "v",
              "title": "AGENTS.md  ·  1. The three layers", "lines": rows,
              "hl": [{"i0": 3, "i1": 3, "t0": w("b2", "rules") - 0.1, "t1": en("b2") + 0.4, "c": "v"}]})
    # ---- b3: ingest
    E.append({"type": "number", "x": 96, "y": 100, "value": "", "count": 1.6, "from": 0, "to": Bd["parts"], "fmt": "{:,.0f}",
              "t0": w("b3", "one") - 0.1, "t1": w("b3", "takes") + 0.4, "size": 84, "label": f"reads of the {Bd['sources']} sources, in parts"})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "takes") - 0.05, "t1": w("b3", "six") - 0.3, "accent": "green",
              "lines": [{"text": f"{Bd['facts']:,} facts", "size": 38, "wt": 600},
                        {"text": "each kept with its quote and its location", "size": 22, "c": "slate"}]})
    bt = sorted(Bd["pages_by_type"].items(), key=lambda x: -x[1])
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b3", "six") - 0.1, "t1": en("b3") + 0.5, "accent": "sky",
              "lines": [{"text": f"{Bd['pages']} pages  ·  {Bd['links']:,} links", "size": 38, "wt": 600},
                        {"text": "  ·  ".join(f"{t} {n}" for t, n in bt[:5]), "size": 20, "c": "slate"},
                        {"text": "  ·  ".join(f"{t} {n}" for t, n in bt[5:11]), "size": 20, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "logmd_top", "text": "log.md", "sub": f"one line per ingest: {D['ingests']}", "accent": "sky",
              "t0": w("b3", "line") - 0.1, "t1": en("b3") + 0.5, "dx": 60, "dy": -70})
    # ---- b4: the page (drawn by draw()), and its tablet
    E.append({"type": "pin", "anchor": f"h_{BC}_top", "text": f"pages/{BC}.md", "accent": "v", "mono": True, "size": 22,
              "t0": w("b4", "brightcell") - 0.1, "t1": en("b4") + 0.4, "dx": 60, "dy": -60})
    # ---- b5: the query
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b5", "emma") - 0.1, "t1": w("b5", "index") - 0.2, "accent": "sky",
              "lines": [{"text": "Emma's question", "size": 22, "c": "slate"}, {"text": D["chain"]["question"], "size": 30, "wt": 600}]})
    E.append({"type": "pin", "anchor": "idx_top", "text": "index.md", "sub": "one line per page: [[slug]] title: summary", "accent": "sky",
              "t0": w("b5", "index") - 0.1, "t1": en("b5") + 0.4, "dx": -70, "dy": -110})
    opened = [s["what"] for s in D["chain"]["steps"] if s["step"] == "page"]
    for k, (s, word) in enumerate(zip(opened, (("brightcell", 1), ("supplier", 0), ("procedure", 0)))):
        E.append({"type": "pin", "anchor": f"h_{s}_top", "text": D["pages"][s]["title"], "sub": f"[[{s}]]", "accent": "v", "size": 24,
                  "t0": w("b5", word[0], word[1]) - 0.1, "t1": en("b5") + 0.4, "dx": [70, 70, -70][k], "dy": [-60, -150, -100][k]})
    ch = D["chain"]
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b5", "opens") - 0.1, "t1": en("b5") + 0.4, "accent": "sky",
              "lines": [{"text": "the navigator, recorded", "size": 22, "c": "slate"},
                        {"text": f"{ch['nav_calls']} model calls  ·  {ch['tokens_in']:,} tokens read", "size": 30, "wt": 600},
                        {"text": "index.md  ·  " + "  ·  ".join(opened), "size": 20, "c": "slate", "mono": True}]})
    # ---- b6: the answer, and its sources
    lines = []
    for para in ch["answer"].split("\n"):
        lines += textwrap.wrap(para.strip(), 76) if para.strip() else []
    i_no = 0
    i_un = next(i for i, l in enumerate(lines) if "UN 38.3" in l)
    i_price = next(i for i, l in enumerate(lines) if "price" in l)
    E.append({"type": "code", "x": 64, "y": 84, "lang": "text", "t0": w("b6", "answer") - 0.1, "t1": w("b6", "each") - 0.1, "size": 18,
              "accent": "green", "title": "The answer, recorded", "sub": "[1] Brightcell Energy  ·  [2] POL-SUP-003  ·  [3] SOP-PUR-006",
              "lines": lines, "hl": [{"i0": i_no, "i1": i_no, "t0": w("b6", "no") - 0.1, "t1": w("b6", "brightcell") - 0.1, "c": "green"},
                                     {"i0": i_un, "i1": i_un, "t0": w("b6", "battery") - 0.1, "t1": w("b6", "price") - 0.1, "c": "green"},
                                     {"i0": i_price, "i1": i_price, "t0": w("b6", "price") - 0.05, "t1": w("b6", "each") - 0.1, "c": "green"}]})
    ns = [it["n_sources"] for it in ch["items"]]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b6", "each") - 0.05, "t1": en("b6") + 0.5, "accent": "green",
              "lines": [{"text": "every claim cites a page; every page cites its sources", "size": 22, "c": "slate"},
                        {"text": f"{sum(ns)} places in the raw sources", "size": 36, "wt": 600},
                        {"text": "  +  ".join(str(n) for n in ns) + "  (the three pages)", "size": 21, "c": "slate"}]})
    # ---- b7: file-back
    fb = D["fileback"]
    E.append({"type": "pin", "anchor": "qa_top", "text": "a new page: the answer, filed back", "sub": short(f"pages/{fb['slug']}.md", 56),
              "accent": "green", "t0": w("b7", "filed") - 0.1, "t1": en("b7") + 0.4, "dx": 70, "dy": -90})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b7", "references") - 0.4, "t1": en("b7") + 0.4, "accent": "green",
              "lines": [{"text": f"{fb['refs']} references", "size": 34, "wt": 600},
                        {"text": "links to " + ", ".join(fb["pages_used"]), "size": 20, "c": "slate", "mono": True}]})
    # ---- b8: an update
    up = D["update"]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b8", "document") - 0.1, "t1": en("b8") + 0.5, "accent": "v",
              "lines": [{"text": "a new document", "size": 22, "c": "slate"}, {"text": up["file"].split("/")[-1], "size": 28, "wt": 600, "mono": True}]})
    for k, s in enumerate(up["updated"]):
        E.append({"type": "tag", "anchor": f"h_{s}_top", "text": s, "hl": "sky", "size": 18, "t0": w("b8", "updated") + 0.1 * k,
                  "t1": en("b8") + 0.5, "dy": -14, "maxdepth": 8})
    for k, s in enumerate(up["created"]):
        E.append({"type": "tag", "anchor": f"new_{s}_top", "text": "new  " + s, "hl": "green", "size": 18, "t0": w("b8", "created") + 0.2 * k + 0.3,
                  "t1": en("b8") + 0.5, "dy": -14, "maxdepth": 8})
    E.append({"type": "chip", "x": 1824, "y": 92, "anchor": "tr", "t0": w("b8", "forty") - 0.1, "t1": en("b8") + 0.5, "accent": "v",
              "lines": [{"text": f"{len(up['updated']) + len(up['created'])} pages touched  ·  {up['facts_added']} new facts", "size": 22, "c": "slate"},
                        {"text": f"{up['seconds']:.1f} s  ·  ${up['usd']:.3f}", "size": 36, "wt": 600}]})
    # ---- b9: lint
    L = D["lint"]
    kinds = sorted(L["by_kind"].items(), key=lambda x: -x[1])[:4]
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b9", "checks") - 0.1, "t1": en("b9") + 0.5, "accent": "ember",
              "lines": [{"text": f"lint: {L['n_findings']:,} findings on {L['pages_flagged']} pages", "size": 30, "wt": 600},
                        {"text": "  ·  ".join(f"{k.replace('_', ' ')} {n}" for k, n in kinds), "size": 20, "c": "slate"}]})
    E.append({"type": "number", "x": 1480, "y": 100, "value": f"{L['found']} / {L['planted']}", "t0": w("b9", "found") - 0.05,
              "t1": en("b9") + 0.5, "size": 96, "label": "planted problems found", "c": "ink"})
    # ---- b10
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b10", "rag") - 0.1, "t1": w("b10", "which") - 0.2, "accent": "sky",
              "lines": [{"text": "RAG: search the raw chunks, at every question", "size": 28, "wt": 600},
                        {"text": "LLM Wiki: read once, keep linked pages", "size": 28, "wt": 600, "c": "deep"}]})
    E.append({"type": "chip", "x": 96, "y": 92, "t0": w("b10", "which") - 0.05, "t1": en("b10") + 0.6, "accent": "sky",
              "lines": [{"text": "next: the race", "size": 22, "c": "slate"}, {"text": "the same 224 questions, both methods, the clock running", "size": 28, "wt": 600}]})
    E.append({"type": "end", "t0": en("b10") + 0.9, "kicker": KICK, "title": "How the LLM Wiki works",
              "sub": "Ingest, query, file back, lint",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara  ·  the idea: Andrej Karpathy, “LLM Wiki” (gist, April 2026)",
                          "Recorded: the Northbridge wiki (ledgerline/wiki_v4) and its logs  ·  Wikipedia “E-bike”, CC BY-SA 4.0",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


# ------------------------------------------------------------------------------------------------ b4: the page and Wikipedia
_PAGE = {}


def _page_card():
    """The Brightcell page as it reads: title, lead, infobox, sections, links, references. Returns (img, regions)."""
    if _PAGE:
        return _PAGE["img"], _PAGE["reg"]
    import overlay as O
    b = D["brightcell"]
    W = 820
    img = Image.new("RGBA", (W, 900), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, W - 1, 899), 18, fill=(12, 16, 25, 236), outline=(255, 255, 255, 34))
    reg = {}
    x, y = 34, 26
    d.text((x, y), "Brightcell Energy", font=O.font(40, 600), fill=(244, 247, 252, 255))
    y += 56
    d.text((x, y), f"pages/{BC}.md  ·  type: supplier  ·  4 sources", font=O.font(19, 400, True), fill=(164, 176, 196, 255))
    reg["title"] = [(x - 10, 18, W - 24, y + 28)]
    y += 44
    # the lead, with its links (sky) and its reference marks
    toks = re.split(r"(\[\[[^\]]+\]\]|\[\^r\d+\])", b["lead"])
    f = O.font(21, 400)
    fl = O.font(21, 500)
    fr = O.font(14, 600)
    lx, ly, maxx = x, y, W - 300
    lead_top = ly
    links, refs = [], []
    for t in toks:
        if not t:
            continue
        if t.startswith("[[") or t.startswith("[^"):
            pieces = [t]
        else:
            pieces = re.findall(r"\S+\s*", t)
        for p in pieces:
            if p.startswith("[["):
                txt = p[2:-2].split("|")[-1]
                fw = fl.getlength(txt + " ")
                if lx + fw > maxx:
                    lx, ly = x, ly + 30
                d.text((lx, ly), txt, font=fl, fill=(120, 175, 255, 255))
                links.append((lx - 4, ly - 2, lx + fl.getlength(txt) + 4, ly + 26))
                lx += fw
            elif p.startswith("[^"):
                txt = "[" + p[3:-1] + "]"
                d.text((lx, ly - 4), txt, font=fr, fill=(120, 175, 255, 255))
                refs.append((lx - 3, ly - 6, lx + fr.getlength(txt) + 3, ly + 14))
                lx += fr.getlength(txt) + 2
            else:
                fw = f.getlength(p)
                if lx + fw > maxx:
                    lx, ly = x, ly + 30
                d.text((lx, ly), p, font=f, fill=(226, 232, 242, 255))
                lx += fw
    ly += 34
    reg["lead"] = [(x - 10, lead_top - 8, maxx + 10, ly)]
    # the infobox, at the right
    ix, iy = W - 270, y - 6
    d.rounded_rectangle((ix, iy, W - 24, iy + 34 * len(b["infobox"]) + 16), 10, fill=(255, 255, 255, 14), outline=(255, 255, 255, 40))
    rows = []
    for k, (kk, vv) in enumerate(b["infobox"]):
        ry = iy + 10 + 34 * k
        d.text((ix + 12, ry), kk, font=O.font(16, 600), fill=(164, 176, 196, 255))
        d.text((ix + 104, ry), short(vv, 18), font=O.font(16, 400), fill=(226, 232, 242, 255))
        rows.append((ix + 4, ry - 4, W - 28, ry + 26))
    reg["infobox"] = [(ix - 4, iy - 4, W - 20, iy + 34 * len(b["infobox"]) + 20)]
    reg["rows"] = rows
    # sections
    y = max(ly, iy + 34 * len(b["infobox"]) + 30) + 10
    sec_top = y
    secs = [s for s in b["sections"] if s not in ("References",)]
    for k, s in enumerate(secs):
        d.text((x + (k % 2) * 380, y + (k // 2) * 34), "## " + s, font=O.font(22, 600), fill=(236, 240, 248, 255))
    y += 34 * ((len(secs) + 1) // 2) + 10
    reg["sections"] = [(x - 10, sec_top - 6, W - 24, y)]
    # links (See also)
    d.text((x, y), "See also", font=O.font(17, 600), fill=(164, 176, 196, 255))
    y += 28
    lx = x
    for s in b["links"]:
        txt = f"[[{s}]]"
        fw = O.font(18, 500, True).getlength(txt + "  ")
        if lx + fw > W - 30:
            lx, y = x, y + 30
        d.text((lx, y), txt, font=O.font(18, 500, True), fill=(120, 175, 255, 255))
        links.append((lx - 4, y - 2, lx + fw - 10, y + 24))
        lx += fw
    y += 44
    reg["links"] = links
    # references
    ref_top = y
    d.text((x, y), f"References  ·  {b['refs']}", font=O.font(17, 600), fill=(164, 176, 196, 255))
    y += 28
    for line in ("[^r3]: 09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 -", "        Brightcell Energy.eml, body",
                 "[^r1]: 10_meeting_notes/2026-10-19 Weekly purchasing meeting.md,", "        Suppliers"):
        d.text((x, y), line, font=O.font(16, 400, True), fill=(200, 208, 222, 255))
        y += 24
    reg["references"] = refs + [(x - 10, ref_top - 6, W - 24, y + 6)]
    img = img.crop((0, 0, W, min(900, y + 24)))
    _PAGE["img"], _PAGE["reg"] = img, reg
    return img, reg


WP_CROP = (43, 130, 1290, 1500)           # original pixels of the captured top screenshot (2160 x 1500)
WP_DISP = {                                # regions, in the 2000-px-wide display of that capture (x 1.08 = original)
    "title": [(362, 128, 480, 172)],
    "lead": [(362, 553, 1185, 912)],
    "sections": [(75, 190, 315, 860), (362, 1362, 645, 1389)],
    "links": [(812, 560, 987, 586), (365, 595, 502, 622), (648, 632, 778, 658), (1057, 668, 1142, 694), (365, 704, 474, 730)],
    "references": [(654, 555, 677, 578), (755, 590, 858, 614), (988, 880, 1012, 902)],
}


def _wiki_img(height=770):
    if "wp" in _PAGE:
        return _PAGE["wp"], _PAGE["wps"]
    p = os.path.join(HERE, "cache", "wikipedia", "electric_bicycle_top.jpg")
    im = Image.open(p).convert("RGB").crop(WP_CROP)
    s = height / im.size[1]
    im = im.resize((int(im.size[0] * s), height), Image.LANCZOS).convert("RGBA")
    _PAGE["wp"], _PAGE["wps"] = im, s
    return im, s


def _box(cv, rect, c, a):
    if a <= 0:
        return
    x0, y0, x1, y1 = [int(v) for v in rect]
    lay = Image.new("RGBA", (x1 - x0 + 6, y1 - y0 + 6), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle((2, 2, x1 - x0 + 3, y1 - y0 + 3), 6, fill=(c[0], c[1], c[2], int(46 * a)),
                                          outline=(c[0], c[1], c[2], int(230 * a)), width=3)
    cv.alpha_composite(lay, (max(0, x0 - 3), max(0, y0 - 3)))


def draw(cv, t, fr, P):
    w, blk = _T.get("w"), _T.get("blk")
    if not w:
        return
    import overlay as O
    t0, t1 = w("b4", "each") - 0.1, blk["b4"]["speech_end"] + 0.4
    if not (t0 - 0.2 <= t <= t1 + 0.4):
        return
    a = max(0.0, min(1.0, (t - t0) / 0.4, (t1 + 0.3 - t) / 0.3))
    img, reg = _page_card()
    px, py = 64, 84
    lay = img.copy()
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    cv.alpha_composite(lay, (px, py))
    tw = t1 if t < w("b4", "brightcell") - 0.3 else w("b4", "brightcell") - 0.3
    wa = a * max(0.0, min(1.0, (w("b4", "brightcell") - 0.1 - t) / 0.35))
    beats = [("lead", "lead"), ("infobox", "infobox"), ("sections", "sections"), ("links", "links"), ("references", "references")]
    if wa > 0:
        wp, s = _wiki_img()
        lay = wp.copy()
        lay.putalpha(int(255 * wa))
        wx, wy = 1856 - wp.size[0], 84
        ImageDraw.Draw(cv).rounded_rectangle((wx - 8, wy - 8, wx + wp.size[0] + 8, wy + wp.size[1] + 40), 14, fill=(12, 16, 25, int(220 * wa)))
        cv.alpha_composite(lay, (wx, wy))
        cap = f"Wikipedia, “E-bike”, captured {D['wikipedia']['captured_utc'][:10]}  ·  text CC BY-SA 4.0"
        ImageDraw.Draw(cv).text((wx, wy + wp.size[1] + 8), cap, font=O.font(17, 400), fill=(164, 176, 196, int(255 * wa)))
    for k, (key, word) in enumerate(beats):
        b0 = w("b4", word) - 0.1
        b1 = w("b4", beats[k + 1][1]) - 0.1 if k + 1 < len(beats) else w("b4", "brightcell") - 0.3
        ha = O.env(t, b0, b1, 0.2, 0.25) * a
        if ha <= 0:
            continue
        c = (60, 144, 255) if key != "references" else (30, 142, 90)
        for r in reg.get(key, []):
            _box(cv, (px + r[0], py + r[1], px + r[2], py + r[3]), c, ha)
        if wa > 0 and key in WP_DISP:
            wp, s = _wiki_img()
            wx, wy = 1856 - wp.size[0], 84
            for (x0, y0, x1, y1) in WP_DISP[key]:
                r = [(x0 * 1.08 - WP_CROP[0]) * s + wx, (y0 * 1.08 - WP_CROP[1]) * s + wy, (x1 * 1.08 - WP_CROP[0]) * s + wx,
                     (y1 * 1.08 - WP_CROP[1]) * s + wy]
                _box(cv, r, c, ha * wa)
    # after the analogy: the facts Daniel names, on the page itself
    rows = reg["rows"]
    for word, i in (("lyon", 1), ("not", 3)):
        b0 = w("b4", word) - 0.1
        ha = O.env(t, b0, t1, 0.2, 0.25) * a
        _box(cv, (px + rows[i][0], py + rows[i][1], px + rows[i][2], py + rows[i][3]), (30, 142, 90), ha)
    b0 = w("b4", "u") - 0.1
    ha = O.env(t, b0, t1, 0.2, 0.25) * a
    lead = reg["lead"][0]
    _box(cv, (px + lead[0], py + lead[3] - 70, px + lead[2], py + lead[3]), (30, 142, 90), ha)


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.2, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.5, 0.25))
    S += [("lid.mp3", w("b2", "never"), 0.35), ("tick.mp3", w("b2", "wiki"), 0.3), ("tick.mp3", w("b2", "schema"), 0.3),
          ("relay.mp3", w("b3", "reads"), 0.3), ("fill.mp3", w("b3", "writes"), 0.35), ("bloom.mp3", w("b3", "four"), 0.35),
          ("rise.mp3", blk["b4"]["at"], 0.3)]
    S += [("tick.mp3", w("b4", x) - 0.05, 0.25) for x in ("lead", "infobox", "sections", "links", "references")]
    S += [("beam.mp3", w("b5", "index"), 0.3), ("chime.mp3", w("b5", "brightcell", 1), 0.3), ("chime.mp3", w("b5", "supplier"), 0.3),
          ("chime.mp3", w("b5", "procedure"), 0.3), ("resolve.mp3", w("b6", "answer"), 0.35), ("fill.mp3", w("b6", "cite"), 0.35),
          ("tile.mp3", w("b7", "filed"), 0.4), ("beam.mp3", w("b7", "one"), 0.3), ("relay.mp3", w("b8", "document"), 0.3),
          ("chime.mp3", w("b8", "updated"), 0.3), ("tile.mp3", w("b8", "created"), 0.3), ("beam.mp3", w("b9", "checks"), 0.4),
          ("refuse.mp3", w("b9", "found") - 0.3, 0.25), ("resolve.mp3", blk["b10"]["speech_end"] + 0.6, 0.5)]
    return S
