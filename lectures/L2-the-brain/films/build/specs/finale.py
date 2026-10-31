"""2D overlays + SFX for the finale (v5), "The whole machine": Emma's question through the entire model, nine stages,
with a chapter label per stage and a running progress strip along the bottom. Plays after section 8, before section 9.

Also holds sched(tl), the frame schedule shared with scenes/finale.py (the scene imports this module), so the 2D chips
that fly into the tiles and the 3D tiles that light on landing use the same frames.

Numbers: brain3d/trace.json (tokens, ids, heads, final.last, generation.greedy, facts.truth), films/qkv_data.json
(block 24 head 2 weights), build/data/finale_data.json (input embeddings, block 1 attention), model facts from
REWORK_V5.md (parameter count per block), all checked against the config in trace.json meta.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILMS = os.path.dirname(HERE)
T = json.load(open(os.path.join(os.path.dirname(FILMS), "brain3d", "trace.json")))
D = json.load(open(os.path.join(FILMS, "qkv_data.json")))
FD = json.load(open(os.path.join(HERE, "data", "finale_data.json")))
TOK = T["tokens"]
G = T["generation"]["greedy"]
TOP6 = T["final"]["last"]["1.0"][:6]
W24 = D["qkv"]["weights"]
HEADS = {(h["layer"], h["head"]): h for h in T["attention"]["heads"]}
FPS = 30
POSTER = 76.3
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_OFFSET = 0.0
STAGES = ["Tokens", "Vectors", "Block 1", "Heads", "24 blocks", "Next token", "The loop", "The number", "Why?"]
STAGE_BLOCK = ["b1", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"]
TITLES = ["Emma's chat becomes 100 tokens", "Each token becomes 896 numbers", "Inside block 1: attention, then the MLP",
          "Fourteen heads, fourteen ways of looking", "All 100 columns, through 24 blocks", "The last column picks the next token",
          "The loop, with the KV cache", "The number: 1, 0, 0", "Every step worked. So why 100?"]
DIGITS = {4, 5, 6}


def show(t):
    if t == " ":
        return "(space)"
    s = t.replace("\n", "\\n")
    return s.strip() if s.strip() else s


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        if len(hs) <= nth:
            raise KeyError(f"{b}: {text!r} #{nth}")
        return hs[nth][edge]
    return w


def sched(tl):
    """Frames shared by the scene and the overlays."""
    w0 = _w(tl)
    f = lambda b, t, n=0: int(round(w0(b, t, n) * FPS))  # noqa: E731
    blk = {b["id"]: b for b in tl["blocks"]}
    S = {"blk": {k: (v["f0"], v["f1"]) for k, v in blk.items()}}
    S["stage"] = [blk[b]["f0"] for b in STAGE_BLOCK]
    S["stage"][0] = 0
    # stage 1: the chat panel, the chips, the flight into the tiles
    S["chat_user"] = f("b1", "emma")
    S["chat_sys"] = f("b2", "wraps")
    S["chat_hdr"] = f("b2", "header")
    S["cut"] = f("b2", "tokenizer")
    S["ids"] = f("b2", "number")
    S["date"] = f("b2", "date")
    S["man"] = f("b2", "manchester")
    S["fly"] = blk["b2"]["f1"] - 8
    S["fly_i"] = {i: S["fly"] + int(round(i * 0.22)) for i in range(100)}
    S["land_i"] = {i: S["fly_i"][i] + 26 for i in range(100)}
    # stage 2: lookups
    S["look"] = f("b3", "looks")
    S["look_i"] = {i: (S["look"] - 12 + (i - 80) * 3) if i >= 80 else (S["look"] + 62 + (79 - i)) for i in range(100)}
    S["table"] = f("b3", "embedding")
    S["rows"] = f("b3", "rows")
    S["rows_sweep"] = (f("b3", "has"), f("b3", "knows"))
    S["row896"] = f("b3", "each", 1)
    S["stands"] = f("b3", "stands")
    # stage 3: block 1
    S["enter"] = f("b4", "enter")
    S["att"] = f("b4", "attention")
    S["q"], S["k"], S["v"] = f("b4", "query"), f("b4", "key"), f("b4", "value")
    S["meets"] = f("b4", "meets")
    S["never"] = f("b4", "never")
    S["flow"] = f("b4", "values")
    S["mlp"] = f("b4", "mlp")
    S["rework"] = f("b4", "reworks")
    # stage 4: heads
    S["fourteen"] = f("b5", "fourteen")
    S["ownway"] = f("b5", "way")
    S["h24"] = f("b5", "twenty-four")
    S["puts"] = f("b5", "puts")
    S["s65"] = f("b5", "sixty-five")
    S["h12"] = f("b5", "twelve")
    S["rests"] = f("b5", "rests")
    S["first"] = f("b5", "first")
    # stage 5: the climb
    S["updates"] = f("b6", "updates")
    f_blocks = f("b6", "blocks")
    S["Fk"] = {1: S["rework"]}
    for k in range(2, 25):
        S["Fk"][k] = int(S["updates"] + 10 + (k - 2) * (f_blocks + 4 - S["updates"] - 10) / 22)
    S["matter"] = f("b6", "matter")
    S["hold"] = f("b6", "hold")
    S["params"] = f("b6", "four")
    S["training"] = f("b6", "training")
    # stage 6: next token
    S["speaks"] = f("b7", "speaks")
    S["scored"] = f("b7", "scored")
    S["same"] = f("b7", "same")
    S["all151"] = f("b7", "all")
    S["softmax"] = f("b7", "softmax")
    S["p_we"], S["p_as"], S["p_man"] = f("b7", "we"), f("b7", "as"), f("b7", "manchester")
    S["chosen"] = f("b7", "chosen")
    # stage 7: the loop
    S["joins"] = f("b8", "joins")
    S["notrun"] = f("b8", "not")
    S["kept"] = f("b8", "kept")
    S["cache"] = f("b8", "cache")
    S["sends"] = f("b8", "sends")
    S["reads"] = f("b8", "reads")
    S["climb_we"] = {k: S["sends"] + 4 + (k - 1) * 4 for k in range(1, 25)}
    # the drops (token j of the answer lands on its spoken word)
    d = {0: S["chosen"] + 2,
         1: f("b8", "currently") - 4, 2: f("b8", "have") - 4, 3: f("b8", "space") - 6,
         4: f("b9", "one") - 8, 5: f("b9", "zero") - 6, 6: f("b9", "zero", 1) - 6,
         7: f("b9", "city") - 4, 8: f("b9", "e-bike") - 4, 9: f("b9", "e-bike") + 1, 10: f("b9", "e-bike") + 6,
         11: f("b9", "battery") - 4, 12: f("b9", "packs") - 4, 13: f("b9", "available") - 4, 14: f("b9", "in", 0) - 4,
         15: f("b9", "our") - 2, 16: f("b9", "manchester") - 3, 17: f("b9", "stores") - 4, 18: f("b9", "stores") + 8,
         19: f("b9", "end-of-turn") - 4}
    S["drop"] = d
    S["pass"] = {j: d[j + 1] - 27 for j in range(1, 19)}
    S["pass"][0] = S["climb_we"][1]
    S["reread"] = {0: f("b9", "we"), 1: f("b9", "currently"), 2: f("b9", "have", 0), 4: f("b9", "one", 1), 5: f("b9", "hundred"),
                   6: f("b9", "hundred") + 6}
    S["stops"] = f("b9", "stops")
    # stage 9
    S["ran"] = f("b10", "ran")
    S["broke"] = f("b10", "broke")
    S["still"] = f("b10", "still")
    S["is100"] = f("b10", "hundred")
    S["ledger"] = f("b10", "ledgerline")
    S["says"] = f("b10", "says")
    S["why"] = f("b10", "why")
    S["why_big"] = blk["b10"]["f1"] + 4
    S["end"] = blk["b10"]["f1"] + 60
    return S


# ------------------------------------------------------------------------------------------------ 2D drawing
_S = {}


def _chat_layout():
    """The tokens as chips in a flowing panel (Tiktokenizer style): [(i, text, x, y, w)] relative to the panel."""
    import overlay as O
    f = O.font(21, 500, True)
    fi = O.font(13, 400, True)
    x, y, rows = 0, 0, []
    W = 1060
    out = []
    for t in TOK:
        s = t["text"]
        lab = "·" if s == " " else s.replace("\n", "\\n")
        tw = max(f.getlength(lab), fi.getlength(str(t["id"]))) + 14
        if x + tw > W:
            x, y = 0, y + 54
        out.append((t["i"], lab, x, y, tw))
        x += tw + 4
        if s.endswith("\n"):
            x, y = 0, y + 54
    return out, y + 54


ROLE_FILL = {"system": (122, 134, 156), "user": (60, 144, 255), "template": (201, 196, 187)}


def _draw_chat(cv, t, fr, P, S):
    import overlay as O
    from PIL import Image, ImageDraw
    if fr < S["chat_user"] - 10 or fr > S["fly"] + 60:
        return
    a_in = O.ease((fr - S["chat_user"] + 10) / 16)
    PX, PY = 96, 176
    if fr < S["cut"]:
        # the chat: three messages
        lines = []
        if fr >= S["chat_sys"] - 6:
            lines.append(("system", T["prompt"]["system"], O.ease((fr - S["chat_sys"] + 6) / 14)))
        q = T["prompt"]["question"]
        k = int(min(len(q), max(0, (fr - S["chat_user"]) / 1.6)))
        lines.append(("user", q[:k], 1.0))
        if fr >= S["chat_hdr"] - 4:
            lines.append(("assistant", "", O.ease((fr - S["chat_hdr"] + 4) / 12)))
        key = ("chatpanel", tuple((r, txt, round(al, 2)) for r, txt, al in lines))
        if key not in O._cache:
            fnt = O.font(24, 400)
            fh = O.font(18, 600)
            img = Image.new("RGBA", (1100, 560), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            y = 20
            blocks = []
            for role, txt, al in lines:
                words, rows, cur = txt.split(), [], ""
                for wd in words:
                    trial = (cur + " " + wd).strip()
                    if fnt.getlength(trial) > 960 and cur:
                        rows.append(cur)
                        cur = wd
                    else:
                        cur = trial
                rows.append(cur)
                h = 40 + 32 * len(rows)
                blocks.append((role, rows, al, y, h))
                y += h + 12
            d.rounded_rectangle((0, 0, 1099, y + 8), 18, fill=(14, 19, 29, 225), outline=(255, 255, 255, 36))
            for role, rows, al, y0, h in blocks:
                c = ROLE_FILL["user" if role == "user" else ("system" if role == "system" else "template")]
                A = int(255 * al)
                d.rounded_rectangle((18, y0, 1081, y0 + h), 12, fill=(c[0] // 7, c[1] // 7, c[2] // 7, int(200 * al)))
                d.rounded_rectangle((18, y0, 24, y0 + h), 3, fill=(c[0], c[1], c[2], A))
                d.text((40, y0 + 10), role, font=fh, fill=(c[0], c[1], c[2], A))
                for r, rr in enumerate(rows):
                    d.text((40, y0 + 36 + 32 * r), rr, font=fnt, fill=(244, 247, 252, A))
                if role == "assistant":
                    d.rectangle((40, y0 + 40, 43, y0 + 64), fill=(96, 165, 255, A))
            O._cache[key] = (img, 0)
        O.put(cv, O._cache[key], PX, PY, a_in)
        return
    # the tokens: chips (and ids), then the flight into the tiles
    lay, H = _chat_layout()
    a_cut = O.ease((fr - S["cut"]) / 10)
    if fr < S["fly"] + 4:
        bgk = ("chipbg", H)
        if bgk not in O._cache:
            img = Image.new("RGBA", (1100, H + 40), (0, 0, 0, 0))
            ImageDraw.Draw(img).rounded_rectangle((0, 0, 1099, H + 39), 18, fill=(14, 19, 29, 225), outline=(255, 255, 255, 36))
            O._cache[bgk] = (img, 0)
        O.put(cv, O._cache[bgk], PX, PY, a_in * (1 - O.ease((fr - S["fly"]) / 8)))
    show_ids = fr >= S["ids"]
    for i, lab, x, y, tw in lay:
        role = TOK[i]["role"]
        c = ROLE_FILL[role]
        hl = None
        if fr >= S["date"] - 4 and fr < S["fly"] and 44 <= i <= 51 and TOK[i]["text"].strip().isdigit():
            hl = (255, 196, 120)
        if fr >= S["man"] - 4 and fr < S["fly"] and i == 92:
            hl = (150, 200, 255)
        sx, sy = PX + 20 + x, PY + 20 + y
        sc = 1.0
        al = a_cut
        fi, li = S["fly_i"][i], S["land_i"][i]
        if fr >= fi:
            u = O.ease((fr - fi) / (li - fi))
            p = P.at(f"tok{i}_top", min(fr, li))
            if p is None:
                al *= 1 - u
            else:
                sx = sx + (p[0] - tw / 2 - sx) * u
                sy = sy + (p[1] - 18 - sy) * u
                sc = 1 - 0.6 * u
                al *= 1 - O.ease((fr - li + 6) / 6) if fr > li - 6 else 1.0
        if al <= 0.01:
            continue
        key = ("chip", i, hl is not None, show_ids)
        if key not in O._cache:
            fnt = O.font(21, 500, True)
            fid = O.font(13, 500, True)
            img = Image.new("RGBA", (int(tw) + 2, 52), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            fill = (c[0] // 4 + 10, c[1] // 4 + 12, c[2] // 4 + 18, 235)
            d.rounded_rectangle((0, 0, int(tw), 30), 7, fill=fill, outline=hl + (255,) if hl else (c[0], c[1], c[2], 150),
                                width=2 if hl else 1)
            d.text((7, 4), lab, font=fnt, fill=(255, 255, 255, 250))
            if show_ids:
                d.text((int(tw) / 2, 41), str(TOK[i]["id"]), font=fid, fill=(hl or (150, 162, 182)) + (255,), anchor="mm")
            O._cache[key] = (img, 0)
        img, _ = O._cache[key]
        if sc < 0.99:
            img = img.resize((max(2, int(img.size[0] * sc)), max(2, int(img.size[1] * sc))))
        O.put(cv, (img, 0), sx, sy, al)


def _draw_strip(cv, t, fr, S):
    """The running progress strip: 9 stages along the bottom edge (below the subtitles)."""
    import overlay as O
    from PIL import ImageDraw
    if fr >= S["end"]:
        return
    a = O.ease(fr / 20) * (1 - O.ease((fr - S["end"] + 12) / 12))
    if a <= 0:
        return
    cur = max(n for n in range(9) if fr >= S["stage"][n])
    nxt = S["stage"][cur + 1] if cur < 8 else S["end"]
    prog = max(0.0, min(1.0, (fr - S["stage"][cur]) / max(1, nxt - S["stage"][cur])))
    key = ("strip", cur)
    x0, x1, y = 250, 1670, 1046
    seg = (x1 - x0) / 9
    if key not in O._cache:
        from PIL import Image
        img = Image.new("RGBA", (1920, 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        import numpy as _np
        g = _np.zeros((60, 1920, 4), _np.uint8)
        g[..., 0:3] = (8, 12, 20)
        g[..., 3] = (_np.linspace(0, 150, 60)[:, None] * _np.ones((1, 1920))).astype(_np.uint8)
        img = Image.fromarray(g, "RGBA")
        d = ImageDraw.Draw(img)
        f = O.font(19, 500)
        fb = O.font(19, 700)
        for n, name in enumerate(STAGES):
            sx = x0 + n * seg
            col = (120, 180, 255, 255) if n == cur else ((226, 232, 242, 235) if n < cur else (150, 160, 178, 205))
            d.rounded_rectangle((sx + 4, 8, sx + seg - 4, 12), 2, fill=(255, 255, 255, 60))
            if n < cur:
                d.rounded_rectangle((sx + 4, 8, sx + seg - 4, 12), 2, fill=(180, 204, 240, 210))
            d.text((sx + seg / 2, 32), f"{n + 1}  {name}", font=fb if n == cur else f, fill=col, anchor="mm")
        O._cache[key] = (img, 0)
    O.put(cv, O._cache[key], 0, y - 26, a)
    # the live progress inside the current stage
    sx = x0 + cur * seg
    ImageDraw.Draw(cv).rounded_rectangle((sx + 4, y - 18, sx + 4 + (seg - 8) * prog, y - 14), 2, fill=(96, 165, 255, int(255 * a)))


def _draw_answer(cv, t, fr, S):
    """The answer as it grows, typed token by token at the top right (stages 7-8)."""
    import overlay as O
    d = S["drop"]
    s9 = S["stage"][8]
    if fr < d[0] + 10 or fr > s9:
        return
    k = max(j for j in range(20) if fr >= d[j] + 10) if fr >= d[0] + 10 else -1
    txt = "".join(G[j]["text"] for j in range(k + 1) if G[j]["text"] != "<|im_end|>")
    a = O.ease((fr - d[0] - 10) / 10) * (1 - O.ease((fr - s9 + 14) / 14))
    lines = [("The answer so far", 20, 500, "slate", False), (txt.strip() or "We", 28, 600, "ink", False)]
    if k >= 19:
        lines.append(("<|im_end|>  83.8%: the end-of-turn token, so the loop stops", 19, 500, "slate", True))
    spr = O.card(lines, accent="sky", pad=(24, 14))
    O.put(cv, spr, 1824, 84, a, anchor="tr")


def draw(cv, t, fr, P):
    S = _S.get("s")
    if S is None:
        return
    _draw_chat(cv, t, fr, P, S)
    _draw_answer(cv, t, fr, S)
    _draw_strip(cv, t, fr, S)


# ------------------------------------------------------------------------------------------------ elements
def elements(tl):
    S = sched(tl)
    _S["s"] = S
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    sec = lambda f: f / FPS  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Before section 9", "title": "The whole machine", "t0": 0.3, "t1": 2.9, "size": 72}]
    # chapter labels: typed at each stage start
    for n in range(9):
        t0 = sec(S["stage"][n]) + (3.4 if n == 0 else 0.15)
        E.append({"type": "title", "kicker": f"Stage {n + 1} of 9", "title": TITLES[n], "t0": t0, "t1": t0 + 4.6, "size": 46,
                  "speed": 0.03, "kc": "ember" if n == 8 else "deep"})
    tr = lambda: {"x": 1824, "y": 84, "anchor": "tr"}  # noqa: E731
    # ---- stage 1
    cnt = T["prompt"]["counts"]
    E.append(dict(type="chip", t0=w("b2", "tiles") + 0.1, t1=en("b2") - 0.3, accent="sky", **tr(),
                  lines=[{"text": f"{T['prompt']['n_tokens']} tokens", "size": 34, "wt": 600},
                         {"text": f"{cnt['system']} instructions · {cnt['user']} question · {cnt['template']} chat markers", "size": 22, "c": "slate"}]))
    # ---- stage 2
    for i in range(78, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": st("b3") + 0.6,
                  "t1": w("b4", "first") + 0.2, "size": 22 if i in (86, 92, 99) else 19, "hl": "sky" if i in (92,) else None,
                  "place": "tc", "dy": 10, "maxdepth": 3.4})
    E.append(dict(type="chip", t0=w("b3", "table"), t1=w("b3", "each", 1) - 0.2, accent="sky", x=1824, y=84, anchor="tr",
                  lines=[{"text": f"Embedding table: {T['meta']['vocab']:,} rows", "size": 30, "wt": 600},
                         {"text": "one row per token · 896 numbers per row", "size": 21, "c": "slate"}]))
    e92 = FD["emb"]["92"]
    E.append({"type": "pin", "anchor": "col92_top", "text": "Manchester: row 19361", "sub": "896 numbers: " + ", ".join(f"{x:.4f}" for x in e92[:3]) + ", …",
              "accent": "sky", "t0": w("b3", "each", 1), "t1": en("b3") + 0.3, "dx": 70, "dy": -60, "size": 30})
    E.append(dict(type="chip", t0=w("b3", "stands"), t1=en("b3") + 0.4, accent="sky", **tr(),
                  lines=[{"text": "100 columns of 896 numbers", "size": 30, "wt": 600},
                         {"text": "every cell is a real value from the model's table", "size": 21, "c": "slate"}]))
    # ---- stage 3
    E.append(dict(type="chip", t0=w("b4", "enter"), t1=w("b4", "attention") - 0.2, accent="sky", **tr(),
                  lines=[{"text": "the row of 100 columns", "size": 30, "wt": 600},
                         {"text": "first 16 of each column's 896 numbers shown", "size": 21, "c": "slate"}]))
    for n, (nm, word, sub, acc) in enumerate((("Query", "query", "what am I looking for?", "q"), ("Key", "key", "what do I contain?", "k"),
                                               ("Value", "value", "what I pass on, if I am chosen", "v"))):
        E.append(dict(type="chip", t0=w("b4", word), t1=w("b4", "meets") - 0.1, accent=acc, x=1824, y=84 + 96 * n, anchor="tr",
                      lines=[{"text": nm, "size": 28, "wt": 600}, {"text": sub + " · every position makes one", "size": 20, "c": "slate"}]))
    E.append(dict(type="chip", t0=w("b4", "meets"), t1=w("b4", "mlp") - 0.2, accent="k", **tr(),
                  lines=[{"text": "query · key  →  weight", "size": 30, "wt": 600, "mono": True},
                         {"text": "earlier positions only · block 1, averaged over its 14 heads", "size": 21, "c": "slate"}]))
    a99 = FD["att1_avg"][99]
    top99 = sorted(range(100), key=lambda j: -a99[j])[:2]
    E.append(dict(type="chip", t0=w("b4", "flow"), t1=w("b4", "mlp") - 0.2, accent="k", x=1824, y=180, anchor="tr",
                  lines=[{"text": f"the last position: {a99[top99[0]] * 100:.1f}% on “{show(TOK[top99[0]]['text'])}”", "size": 24, "wt": 600},
                         {"text": (f"then {a99[top99[1]] * 100:.1f}% on itself" if top99[1] == 99 else
                                   f"then {a99[top99[1]] * 100:.1f}% on “{show(TOK[top99[1]]['text'])}”"), "size": 20, "c": "slate"}]))
    E.append({"type": "pin", "anchor": "bt_mlp1", "text": "MLP", "sub": "896 to 4,864 to 896, each column on its own", "accent": "v",
              "t0": w("b4", "mlp"), "t1": en("b4") + 0.4, "dx": 60, "dy": -120, "size": 30})
    # ---- stage 4
    E.append({"type": "pin", "anchor": "bt_att3", "text": "14 heads", "sub": "per block · each with its own query", "accent": "sky",
              "t0": w("b5", "fourteen"), "t1": w("b5", "twenty-four") - 0.6, "dx": -80, "dy": -130, "size": 30})
    for i in range(84, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": w("b5", "twenty-four") - 0.4,
                  "t1": w("b5", "twelve") + 0.5, "size": 21, "hl": "sky" if i == 92 else None, "place": "tc", "dy": 10, "maxdepth": 3.6})
    E.append({"type": "pin", "anchor": "tok92_top", "text": f"{W24[92] * 100:.1f}%", "sub": "block 24 · head 2, on Manchester", "accent": "sky",
              "t0": w("b5", "sixty-five"), "t1": w("b5", "twelve") + 0.3, "dx": -60, "dy": -150, "mono": True, "size": 40})
    w21 = W24[21]
    E.append(dict(type="chip", t0=w("b5", "puts"), t1=w("b5", "twelve") + 0.3, accent="sky", **tr(),
                  lines=[{"text": "block 24 · head 2", "size": 30, "wt": 600},
                         {"text": f"Manchester (her question) {W24[92] * 100:.1f}% · Manchester (system prompt) {w21 * 100:.1f}%", "size": 21, "c": "slate"},
                         {"text": "arc brightness = the head's real weight", "size": 21, "c": "slate"}]))
    E.append(dict(type="chip", t0=w("b5", "rests"), t1=en("b5") + 0.6, accent="deep", **tr(),
                  lines=[{"text": "block 12 · head 13", "size": 30, "wt": 600},
                         {"text": "all its weight on position 0, 99 positions back", "size": 21, "c": "slate"}]))
    h12 = HEADS[(12, 13)]
    E.append({"type": "pin", "anchor": "tok0_top", "text": f"{h12['row_last'][0] * 100:.0f}%", "sub": "block 12 · head 13, on the first token <|im_start|>",
              "accent": "deep", "t0": w("b5", "first") - 0.1, "t1": en("b5") + 0.6, "dx": 60, "dy": -110, "mono": True, "size": 40})
    # ---- stage 5
    E.append(dict(type="chip", t0=w("b6", "updates"), t1=w("b6", "matter") - 0.2, accent="sky", **tr(),
                  lines=[{"text": "all 100 columns change in every block", "size": 30, "wt": 600},
                         {"text": "real values after each block (first 16 of 896)", "size": 21, "c": "slate"}]))
    E.append({"type": "pin", "anchor": "cache_k24", "text": "Keys and values, every position", "sub": "what the last column reads, in each block",
              "accent": "k", "t0": w("b6", "hold"), "t1": w("b6", "four") - 0.2, "dx": 40, "dy": -100, "size": 26})
    E.append({"type": "number", "value": f"{T['meta']['params']:,}", "x": 1824 - 560, "y": 120, "size": 84, "c": "ink",
              "count": 0.9, "from": 0, "to": T["meta"]["params"], "fmt": "{:,.0f}", "t0": w("b6", "four"), "t1": en("b6") + 0.5,
              "label": "learnt numbers in Qwen2.5-0.5B-Instruct"})
    E.append(dict(type="chip", t0=w("b6", "million") + 0.4, t1=en("b6") + 0.5, x=1824, y=330, anchor="tr", accent="slate",
                  lines=[{"text": "per block 14,912,384  ×  24 = 357,897,216", "size": 22, "wt": 500, "mono": True},
                         {"text": "+ embedding table 136,134,656  + final norm 896", "size": 22, "wt": 500, "mono": True},
                         {"text": "every one set in training (section 8)", "size": 20, "c": "slate"}]))
    # ---- stage 6
    lens = D["vectors"]["lens_last"][23]
    E.append({"type": "pin", "anchor": "final_top", "text": "The last column, after block 24", "sub": "896 numbers: " + ", ".join(f"{x:.3f}" for x in lens[:3]) + ", …",
              "accent": "sky", "t0": w("b7", "speaks") - 0.2, "t1": w("b7", "scored") + 1.6, "dx": 60, "dy": -60, "size": 26})
    E.append({"type": "pin", "anchor": "rack_pin2", "text": "the same table: 151,936 rows", "sub": "one score per row (a dot product)",
              "accent": "sky", "t0": w("b7", "same"), "t1": w("b7", "softmax") + 0.4, "dx": -60, "dy": -80, "size": 28})
    bar_t = {0: w("b7", "we"), 1: w("b7", "as"), 2: w("b7", "manchester")}
    E.append(dict(type="chip", t0=w("b7", "manchester") + 0.5, t1=en("b7") + 0.4, accent="sky", x=96, y=84, anchor="tl",
                  lines=[{"text": "the top six of 151,936", "size": 26, "wt": 600}] +
                        [{"text": f"{show(r['text']):<11s}{r['p'] * 100:5.1f}%", "size": 22, "wt": 500, "mono": True, "c": "ink" if k == 0 else "slate"}
                         for k, r in enumerate(TOP6)]))
    for n, row in enumerate(TOP6[:3]):
        E.append({"type": "pin", "anchor": f"bar{n}_top", "text": f"{show(row['text'])}  {row['p'] * 100:.1f}%",
                  "t0": bar_t.get(n, w("b7", "manchester") + 0.5), "t1": en("b7") + 0.4, "dx": 24 if n % 2 == 0 else -24,
                  "dy": -50 - 46 * (n % 2), "mono": True, "size": 30 if n == 0 else 22, "accent": "sky" if n == 0 else "slate"})
    E.append(dict(type="chip", t0=w("b7", "softmax"), t1=w("b7", "we") - 0.1, accent="sky", **tr(),
                  lines=[{"text": "softmax: scores to probabilities", "size": 28, "wt": 600},
                         {"text": "all 151,936 add up to 1", "size": 21, "c": "slate"}]))
    # ---- stage 7
    E.append({"type": "pin", "anchor": "cache_k12", "text": "KV cache", "sub": "keys and values of all earlier positions, kept in every block",
              "accent": "k", "t0": w("b8", "kept"), "t1": w("b8", "sends") - 0.2, "dx": 60, "dy": -60, "size": 30})
    E.append({"type": "pin", "anchor": "wecol_top", "text": "one new column: We", "sub": "through all 24 blocks, reading the cache",
              "accent": "sky", "t0": w("b8", "sends"), "t1": sec(S["climb_we"][24] + 14), "dx": -70, "dy": -50, "size": 26})
    for j in range(20):
        E.append({"type": "tag", "anchor": f"gen{j}_front", "text": show(G[j]["text"]), "t0": sec(S["drop"][j]) + 0.4, "t1": (sec(S["end"]) if j in DIGITS else w("b10", "so") + 0.2),
                  "size": 22, "hl": "ember" if j in DIGITS else None, "place": "tc", "dy": 10, "maxdepth": 7.5})
    # ---- stage 8
    for j, word, nth in ((4, "one", 0), (5, "zero", 0), (6, "zero", 1)):
        g = G[j]
        alts = " · ".join(f"{a['text']} {a['p'] * 100:.1f}%" for a in g["alts"][1:3]) if g.get("alts") else ""
        E.append({"type": "pin", "anchor": f"gen{j}_top", "text": f"{g['text']}  {g['p'] * 100:.1f}%", "sub": ("then " + alts) if alts else None,
                  "accent": "ember", "t0": w("b9", word, nth) + 0.15, "t1": (w("b9", "zero") - 0.1) if j == 4 else (w("b9", "zero", 1) - 0.1 if j == 5 else w("b9", "token") + 0.4),
                  "dx": 40, "dy": -120, "mono": True, "size": 32})
    # ---- stage 9
    E.append({"type": "pin", "anchor": "gen5_top", "text": "100", "sub": "the model's answer", "accent": "ember", "t0": w("b10", "hundred"),
              "t1": en("b10") + 1.4, "dx": -60, "dy": -130, "mono": True, "size": 46})
    E.append({"type": "pin", "anchor": "plaque_top", "text": f"Ledgerline: {T['facts']['truth']:,}", "sub": "BAT-500 on hand, Manchester main stores",
              "accent": "green", "t0": w("b10", "says") - 0.1, "t1": en("b10") + 1.4, "dx": 300, "dy": 30, "size": 34})
    E.append({"type": "number", "value": "Why?", "x": 960, "y": 120, "anchor": "tc", "size": 132, "c": "ink",
              "t0": sec(S["why_big"]), "t1": sec(S["end"]) - 0.2})
    for e in E:
        if e.get("sub") is None:
            e.pop("sub", None)
    E.append({"type": "end", "t0": sec(S["end"]), "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The whole machine",
              "sub": "Next, section 9: why it made the number up",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Every number is from recorded runs of Qwen2.5-0.5B-Instruct (trace.json, qkv_data.json, finale_data.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    S = sched(tl)
    s = lambda f: f / FPS  # noqa: E731
    X = [("bloom.mp3", 0.3, 0.5), ("tile.mp3", s(S["chat_user"]), 0.25), ("whoosh.mp3", s(S["cut"]) - 0.1, 0.3),
         ("tick.mp3", s(S["ids"]), 0.25), ("whoosh.mp3", s(S["fly"]) + 0.2, 0.4), ("tile.mp3", s(S["land_i"][99]), 0.35)]
    for n in range(1, 9):
        X.append(("whoosh.mp3", s(S["stage"][n]) - 0.35, 0.22))
    X += [("rise.mp3", s(S["look"]) - 0.3, 0.35), ("beam.mp3", s(S["rows_sweep"][0]), 0.3), ("chime.mp3", s(S["row896"]), 0.25),
          ("merge.mp3", s(S["enter"]) - 0.3, 0.4), ("tick.mp3", s(S["q"]), 0.3), ("tick.mp3", s(S["k"]), 0.3), ("tick.mp3", s(S["v"]), 0.3),
          ("beam.mp3", s(S["meets"]), 0.35), ("fill.mp3", s(S["flow"]), 0.3), ("rise.mp3", s(S["rework"]) - 0.2, 0.3),
          ("tick.mp3", s(S["fourteen"]), 0.3), ("beam.mp3", s(S["puts"]), 0.35), ("chime.mp3", s(S["s65"]), 0.3),
          ("beam.mp3", s(S["rests"]), 0.4), ("chime.mp3", s(S["first"]) + 0.3, 0.3),
          ("rise.mp3", s(S["Fk"][2]) - 0.2, 0.4), ("fill.mp3", s(S["hold"]), 0.3), ("bloom.mp3", s(S["params"]), 0.35),
          ("rise.mp3", s(S["speaks"]) - 0.2, 0.35), ("whoosh.mp3", s(S["scored"]), 0.3), ("beam.mp3", s(S["same"]), 0.35),
          ("fill.mp3", s(S["softmax"]) + 0.3, 0.35), ("chime.mp3", s(S["p_we"]), 0.35), ("tile.mp3", s(S["drop"][0]) + 0.4, 0.4),
          ("rise.mp3", s(S["joins"]), 0.3), ("fill.mp3", s(S["kept"]), 0.3), ("beam.mp3", s(S["sends"]) + 0.1, 0.4)]
    for j in range(1, 20):
        X.append(("tile.mp3", s(S["drop"][j]) + 0.4, 0.42 if j in DIGITS else (0.28 if j < 7 else 0.16)))
    X += [("resolve.mp3", s(S["stops"]) + 0.3, 0.35), ("bloom.mp3", s(S["ran"]), 0.35), ("tile.mp3", s(S["is100"]), 0.35),
          ("chime.mp3", s(S["ledger"]) + 0.2, 0.4), ("rise.mp3", s(S["why_big"]) - 0.3, 0.45), ("resolve.mp3", s(S["end"]) + 0.2, 0.45)]
    return X
