"""2D overlays + SFX for "params" ("494 million numbers"). Every count is Qwen2.5-0.5B-Instruct's own tensor sizes and every
cell value is real (build/data/params_data.json, written by capture_params.py on Modal CPU)."""
import json
import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PD = json.load(open(os.path.join(HERE, "data", "params_data.json")))
BT = PD["block24_tensors"]
QV = PD["q_proj_block24_0_6"]
POSTER = 66.6
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 40.0

N_Q = BT["self_attn.q_proj.weight"] + BT["self_attn.q_proj.bias"]
N_K = BT["self_attn.k_proj.weight"] + BT["self_attn.k_proj.bias"]
N_V = BT["self_attn.v_proj.weight"] + BT["self_attn.v_proj.bias"]
N_O = BT["self_attn.o_proj.weight"]
N_G, N_U, N_D = BT["mlp.gate_proj.weight"], BT["mlp.up_proj.weight"], BT["mlp.down_proj.weight"]
N_N = BT["input_layernorm.weight"] + BT["post_attention_layernorm.weight"]
assert N_Q + N_K + N_V + N_O + N_G + N_U + N_D + N_N == PD["per_block"] == 14912384
assert PD["per_block"] * 24 + PD["embedding"] + PD["final_norm"] == PD["total_params"] == 494032768


def minus(s):
    return s.replace("-", "−")


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def _tally(tl):
    """(time, running total, what was just added)"""
    w = _w(tl)
    ev, tot = [], 0
    for t, n, lab in ((w("b3", "query"), N_Q, f"+ query  896 × 896 + 896 bias  =  {N_Q:,}"),
                      (w("b3", "output"), N_O, f"+ output  896 × 896  =  {N_O:,}"),
                      (w("b3", "keys"), N_K, f"+ keys  896 × 128 + 128 bias  =  {N_K:,}"),
                      (w("b3", "values"), N_V, f"+ values  896 × 128 + 128 bias  =  {N_V:,}"),
                      (w("b4", "gate"), N_G, f"+ gate  896 × 4,864  =  {N_G:,}"),
                      (w("b4", "up"), N_U, f"+ up  896 × 4,864  =  {N_U:,}"),
                      (w("b4", "down"), N_D, f"+ down  4,864 × 896  =  {N_D:,}"),
                      (w("b4", "one"), N_N, f"+ 2 norms  896 each  =  {N_N:,}")):
        tot += n
        ev.append((t, tot, lab, "One block"))
    ev.append((w("b5", "twenty-four"), tot * 24, f"× 24 blocks  =  {tot * 24:,}", "24 blocks"))
    ev.append((w("b5", "embedding"), tot * 24 + PD["embedding"], f"+ embedding table  151,936 × 896  =  {PD['embedding']:,}", "The whole model"))
    ev.append((w("b5", "all"), PD["total_params"], f"+ final norm  =  {PD['final_norm']:,}", "The whole model"))
    return ev


_STATE = {}


def draw(cv, t, fr, P):
    import overlay as O
    from PIL import ImageDraw
    tl = _STATE["tl"]
    ev = _STATE["ev"]
    blk = {b["id"]: b for b in tl["blocks"]}
    # ---- the counter (b3 to the end of b5)
    t0, t1 = ev[0][0] - 0.3, blk["b5"]["speech_end"] + 1.2
    a = O.env(t, t0, t1, 0.4, 0.5)
    if a > 0:
        prev, cur, lab, head = 0, ev[0][1], ev[0][2], ev[0][3]
        k = 0.0
        for i, (te, val, lb, hd) in enumerate(ev):
            if t >= te:
                prev = ev[i - 1][1] if i else 0
                cur, lab, head = val, lb, hd
                k = O.ease((t - te) / 0.9)
        if t < ev[0][0]:
            prev, cur, k = 0, 0, 1.0
        v = int(round(prev + (cur - prev) * k))
        spr = O.card([(head, 24, 500, "slate", False), (f"{v:,}", 58, 600, "ink", True),
                      ("numbers", 22, 400, "slate", False)], accent="sky", pad=(28, 16))
        O.put(cv, spr, 1824, 92, a, anchor="tr")
        img, pad = spr
        h = img.size[1] - 2 * pad
        if t >= ev[0][0]:
            la = a * O.ease((t - max(e[0] for e in ev if e[0] <= t)) / 0.35)
            O.put(cv, O.card([(lab, 23, 500, "ink", True)], accent="deep", pad=(18, 10), bar=False, bg=(14, 19, 28, 210)),
                  1824, 92 + h + 14, la, anchor="tr")
    # ---- the macro: real values on the cells of block 24's q_proj [0:6, 0:6]
    zb = blk["b6"]
    if zb["at"] - 1 <= t <= blk["b7"]["at"] + 1.4:
        p00, p01 = P.at("qc_0_0", fr), P.at("qc_0_1", fr)
        if p00 and p01:
            cell = math.hypot(p01[0] - p00[0], p01[1] - p00[1])
            av = max(0.0, min(1.0, (cell - 70) / 60)) * O.env(t, zb["at"] - 1, blk["b7"]["at"] + 0.4, 0.3, 0.8)
            if av > 0:
                size = int(max(16, min(40, cell * 0.17)))
                said = _STATE["said"]
                for r in range(6):
                    for c in range(6):
                        p = P.at(f"qc_{r}_{c}", fr)
                        if not p or not (0 < p[0] < 1920 and 0 < p[1] < 940):
                            continue
                        val = QV[r][c]
                        hot = r == 0 and c < 3 and t >= said[c]
                        txt = minus(f"{val:+.4f}") if val < 0 else f"{val:.4f}"
                        spr = O.text_sprite(txt, size + (4 if hot else 0), 650 if hot else 550, "ink" if hot else (232, 240, 255), mono=True)
                        O.put(cv, spr, p[0], p[1], av, anchor="c")
                        if hot:
                            d = ImageDraw.Draw(cv)
                            hw = cell * 0.46
                            ha = int(255 * av * O.ease((t - said[c]) / 0.3))
                            d.rounded_rectangle((p[0] - hw, p[1] - hw, p[0] + hw, p[1] + hw), int(cell * 0.08), outline=(96, 165, 255, ha), width=4)
    # ---- the closing question
    b7 = blk["b7"]
    qa = O.env(t, b7["at"] - 0.1, b7["speech_end"] + 2.4, 0.4, 0.5)
    if qa > 0:
        l1 = "Every answer came from these numbers."
        k1 = int(min(len(l1), max(0, (t - b7["at"]) / 0.035)))
        if k1:
            O.put(cv, O.text_sprite(l1[:k1], 54, 600, "ink"), 960, 330, qa, anchor="c")
        tw = _STATE["who"]
        if t >= tw - 0.05:
            l2 = "Who chose them?"
            k2 = int(min(len(l2), max(1, (t - tw + 0.05) / 0.04)))
            O.put(cv, O.text_sprite(l2[:k2], 92, 650, (96, 165, 255)), 960, 440, qa, anchor="c")


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    _STATE["tl"] = tl
    _STATE["ev"] = _tally(tl)
    _STATE["said"] = [w("b6", "minus"), w("b6", "minus", 1), w("b6", "point", 2)]
    _STATE["who"] = w("b7", "who")
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 8", "title": "494 million numbers", "t0": 0.4, "t1": st("b1") + 2.6}]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "twenty-four"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "Qwen2.5-0.5B-Instruct", "size": 32, "wt": 600},
                        {"text": "24 blocks, each built the same way", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "bt_att24", "text": "Block 24", "sub": "the top of the stack", "accent": "sky",
              "t0": w("b2", "lift"), "t1": w("b2", "each") - 0.2, "dx": 90, "dy": -90, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "sheet"), "t1": en("b2") + 0.5, "accent": "sky",
              "lines": [{"text": "One glass sheet = one weight matrix", "size": 30, "wt": 600},
                        {"text": "one cell per number, drawn to scale: rows × columns", "size": 24, "c": "slate"},
                        {"text": "the cells are block 24's real weights (sky +, violet −)", "size": 24, "c": "slate"}]})
    # attention
    for nm, word, nth, text, sub, dx, dy in (
            ("q", "query", 0, "Query  896 × 896", f"+ 896 bias  =  {N_Q:,}", -40, 190),
            ("o", "output", 0, "Output  896 × 896", f"{N_O:,}", 40, 190),
            ("k", "keys", 0, "Keys  896 × 128", f"+ 128 bias  =  {N_K:,}", -30, 110),
            ("v", "values", 0, "Values  896 × 128", f"+ 128 bias  =  {N_V:,}", 30, 110)):
        E.append({"type": "pin", "anchor": f"sh_{nm}_bot", "text": text, "sub": sub, "accent": "sky", "mono": False,
                  "t0": w("b3", word, nth), "t1": en("b3") + 0.4, "dx": dx, "dy": dy, "size": 26})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "share"), "t1": en("b3") + 0.4, "accent": "slate",
              "lines": [{"text": "14 query heads share 2 sets of keys and values", "size": 28, "wt": 600},
                        {"text": "7 heads to each set, so k and v are only 128 wide", "size": 24, "c": "slate"}]})
    # feed-forward
    for nm, word, text, n, dx, dy in (("gate", "gate", "Gate  896 × 4,864", N_G, -70, -60), ("up", "up", "Up  896 × 4,864", N_U, 70, -170),
                                      ("down", "down", "Down  4,864 × 896", N_D, 40, -150)):
        E.append({"type": "pin", "anchor": f"sh_{nm}_top", "text": text, "sub": f"{n:,}", "accent": "sky",
                  "t0": w("b4", word), "t1": en("b4") + 0.4, "dx": dx, "dy": dy, "size": 26})
    E.append({"type": "pin", "anchor": "norm2_top", "text": "2 norms", "sub": f"896 each  =  {N_N:,}", "accent": "slate",
              "t0": w("b4", "one"), "t1": en("b4") + 0.4, "dx": 50, "dy": -110, "size": 24})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "most"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": f"Feed-forward: {N_G + N_U + N_D:,} of {PD['per_block']:,}", "size": 28, "wt": 600, "mono": False},
                        {"text": f"{100 * (N_G + N_U + N_D) / PD['per_block']:.1f}% of the block", "size": 24, "c": "slate"}]})
    # x 24, the embedding, the total
    E.append({"type": "pin", "anchor": "embed_near", "text": "Embedding table  151,936 × 896", "accent": "sky",
              "sub": f"{PD['embedding']:,}  ·  one row per token, 42 m at this scale", "t0": w("b5", "embedding"), "t1": w("b5", "all") - 0.3,
              "dx": 80, "dy": -170, "size": 26})
    E.append({"type": "pin", "anchor": "embed_10m", "text": "10 m", "accent": "slate", "t0": w("b5", "vocabulary"),
              "t1": w("b5", "all") - 0.3, "dx": -40, "dy": -90, "size": 28})
    E.append({"type": "pin", "anchor": "fnorm_top", "text": "Final norm  896", "accent": "slate", "t0": w("b5", "all"),
              "t1": en("b5") + 0.4, "dx": 70, "dy": -80, "size": 22})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "vocabulary") + 0.4, "t1": w("b5", "all") - 0.3, "accent": "slate",
              "lines": [{"text": "The same table reads tokens in", "size": 26, "wt": 600},
                        {"text": "and scores the next token out (it is tied)", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 30, "y": 130, "t0": w("b6", "corner") - 0.2, "t1": en("b6") + 0.6, "accent": "sky",
              "lines": [{"text": "Block 24, query matrix", "size": 28, "wt": 600},
                        {"text": "rows 1–6, columns 1–6", "size": 24, "c": "slate"},
                        {"text": "the real released values", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b7") + 2.6, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "494 million numbers",
              "sub": "Who chose them? Next: how the weights were learnt.",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Qwen2.5-0.5B-Instruct (Apache 2.0): counts from its own tensors; block 24's weights shown cell for cell",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.28))
    S += [("rise.mp3", w("b1", "twenty-four"), 0.35), ("rise.mp3", w("b2", "lift"), 0.4), ("merge.mp3", w("b2", "lay"), 0.35)]
    for i, (te, *_r) in enumerate(_tally(tl)):
        S.append(("tick.mp3", te, 0.32))
    S += [("fill.mp3", w("b5", "twenty-four"), 0.35), ("beam.mp3", w("b5", "embedding"), 0.35),
          ("chime.mp3", w("b5", "ninety-four"), 0.4), ("whoosh.mp3", w("b6", "look"), 0.3)]
    for k, wd in enumerate(("minus", "minus", "point")):
        S.append(("tile.mp3", w("b6", wd, 0 if k < 2 else 2) if k != 1 else w("b6", "minus", 1), 0.3))
    S += [("bloom.mp3", w("b7", "who"), 0.4), ("resolve.mp3", blk["b7"]["speech_end"] + 2.4, 0.45)]
    return S
