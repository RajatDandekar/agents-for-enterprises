"""2D overlays + SFX for the "blocks" film, "Inside the stack: every token, 24 blocks". Tokens and the logit lens from
brain3d/trace.json; per-block weights and the last column's vectors from build/data/blocks_data.json; heads from
build/data/heads_data.json (capture_heads.py on Modal CPU)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
BD = json.load(open(os.path.join(HERE, "data", "blocks_data.json")))
HD = json.load(open(os.path.join(HERE, "data", "heads_data.json")))
HEADS = {(h["block"], h["head"]): h for h in HD["heads"]}
TOK = T["tokens"]
CARD = T["model_card"]
LENS = T["logit_lens"]["last"]
CNT = T["prompt"]["counts"]
A1 = BD["avg_mats"]["1"]
A24 = BD["avg_mats"]["24"]
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 20.0
FPS = 30
_TL = {}


def show(s):
    s = s.replace("\n", "\\n")
    return s.strip() if s.strip() else s


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def schedule(tl):
    """The same frame schedule as scenes/blocks.py: F[k] = the row reaches floor k; SW[k] = its columns switch to block
    k's output; LF[k] = the logit-lens eyepiece of floor k lights. Returned in seconds."""
    w = _w(tl)
    f = lambda b, t, nth=0: w(b, t, nth, "f0")  # noqa: E731
    blk = {b["id"]: b for b in tl["blocks"]}
    f_chg, f_climb = f("b6", "changed"), f("b6", "climb")
    f_ag1, f_ag2 = f("b6", "again", 0), f("b6", "again", 1)
    f24e = blk["b6"]["f1"] + 70
    F = {2: f_climb + 8, 3: f_ag1, 4: f_ag2}
    for k in range(5, 25):
        F[k] = int(f_ag2 + 16 + (f24e - f_ag2 - 16) * (k - 5) / 19)
    SW = {1: f_chg + 23}
    for k in range(2, 25):
        nxt = F[k + 1] if k < 24 else F[k] + 20
        SW[k] = F[k] + max(3, min(12, (nxt - F[k]) // 2))
    f_ask, f_for, f_noise = f("b9", "ask"), f("b9", "for"), f("b9", "noise")
    f18 = f("b9", "eighteen")
    LF = {1: f_ask, 2: f_ask + 8, 3: f_ask + 16}
    for k in range(4, 18):
        LF[k] = int(f_for + (f_noise + 10 - f_for) * (k - 4) / 13)
    LF[18] = f18
    LF[19], LF[20], LF[21] = f18 + 20, f18 + 40, f18 + 60
    LF[22], LF[23], LF[24] = f("b9", "eight"), f("b9", "twenty-nine"), f("b9", "fifty-six")
    s = lambda d: {k: v / FPS for k, v in d.items()}  # noqa: E731
    return s(F), s(SW), s(LF)


def elements(tl):
    _TL["tl"] = tl
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    pc = lambda x: f"{x * 100:.1f}%"  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 5", "title": "Inside the stack: every token, 24 blocks", "t0": 0.4,
          "t1": st("b1") + 3.0}]
    # b1-b2: the words on the tiles. Emma's question as faces on its tiles (from the moment each word is spoken)
    QW = [(80, "how"), (81, "many"), (82, "city"), (83, "e-bike"), (84, "e-bike"), (85, "e-bike"), (86, "battery"), (87, "packs"),
          (88, "do"), (89, "we"), (90, "have"), (91, "in"), (92, "manchester"), (93, "stores"), (94, "stores")]
    t_off = w("b2", "side") + 0.8
    for i, wd in QW:
        t0 = w("b1", wd) + (0.07 * (i - 83) if 83 <= i <= 85 else 0) + (0.2 if i == 94 else 0)
        E.append({"type": "face", "anchor": f"tok{i}_top", "scale_pin": f"tok{i}_front", "text": show(TOK[i]["text"]),
                  "t0": t0, "t1": t_off, "c": "ink", "max": 56})
    for i in list(range(40, 80)) + list(range(95, 100)):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": 0.6 if i < 80 else w("b1", "stores"),
                  "t1": t_off, "size": 20, "place": "tc", "dy": 8, "maxdepth": 8})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "instructions"), "t1": w("b1", "how") - 0.3, "accent": "sky",
              "lines": [{"text": f"{CNT['system'] + CNT['user'] + CNT['template']} tokens", "size": 32, "wt": 600},
                        {"text": f"{CNT['system']} instructions  ·  {CNT['user']} Emma's question  ·  {CNT['template']} chat markers", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "col99_top", "text": "One column per token", "sub": f"{CARD['d_model']} numbers each  ·  first 16 shown, real values",
              "accent": "sky", "t0": w("b2", "column") + 0.8, "t1": en("b2") + 0.3, "dx": -80, "dy": -110, "size": 28})
    # b3: the stack
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "twenty-four"), "t1": w("b3", "open") - 0.2, "accent": "sky",
              "lines": [{"text": f"{CARD['layers']} blocks, one above the other", "size": 32, "wt": 600},
                        {"text": "each block spans all 100 positions", "size": 24, "c": "slate"}]})
    # b4: attention in block 1
    lab_t0, lab_t1 = w("b4", "attention") - 0.3, en("b5") + 0.3
    for i, nm in ((82, "city"), (86, "battery"), (92, "Manchester"), (93, "stores"), (99, "last position")):
        E.append({"type": "tag", "anchor": f"col{i}_bot", "text": nm, "t0": lab_t0, "t1": lab_t1, "size": 22, "mono": False,
                  "hl": "sky" if i == 99 else None, "place": "tc", "dy": 6, "maxdepth": 30})
    E.append({"type": "pin", "anchor": "fac_att1", "text": "Block 1  ·  attention", "sub": f"{CARD['heads']} heads, side by side", "accent": "sky",
              "t0": w("b4", "attention"), "t1": w("b4", "every") - 0.2, "dx": 60, "dy": -150, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "every"), "t1": w("b4", "manchester") - 0.3, "accent": "sky",
              "lines": [{"text": "Each position reads only earlier positions", "size": 30, "wt": 600},
                        {"text": "brightness = real weight  ·  block 1, average of the 14 heads", "size": 22, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "wall_top", "text": "never forward", "t0": w("b4", "never") + 0.5, "t1": w("b4", "manchester"),
              "size": 22, "mono": False, "place": "bc", "dy": -6})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "manchester"), "t1": w("b4", "last") - 0.3, "accent": "v",
              "lines": [{"text": "Manchester can read every word before it", "size": 30, "wt": 600},
                        {"text": f"block 1: {pc(A1[92][91])} on ' in', {pc(A1[92][86])} on battery", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "last"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "The last position reads all 99 before it", "size": 30, "wt": 600},
                        {"text": f"{pc(A1[99][98])} on 'assistant', {pc(A1[99][80])} on 'How', the rest spread thin", "size": 22, "c": "slate"}]})
    # b5: the MLP
    E.append({"type": "pin", "anchor": "fac_mlp1", "text": "Block 1  ·  MLP", "sub": "one unit behind every position", "accent": "v",
              "t0": w("b5", "mlp"), "t1": w("b5", "widens") - 0.2, "dx": 60, "dy": -160, "size": 30})
    E.append({"type": "pin", "anchor": "pin_top", "text": f"{CARD['d_model']} numbers in", "sub": "the last column, block 1 (real)", "accent": "sky",
              "t0": w("b5", "widens") + 0.3, "t1": w("b5", "four") - 0.1, "dx": 60, "dy": -70, "size": 28, "mono": False})
    E.append({"type": "pin", "anchor": "pwide_top", "text": f"{CARD['mlp_hidden']:,} numbers inside", "sub": "the MLP's wide middle layer (real)", "accent": "v",
              "t0": w("b5", "four") + 0.5, "t1": w("b5", "squeezes") + 0.2, "dx": 60, "dy": -70, "size": 28})
    E.append({"type": "pin", "anchor": "pout_top", "text": f"{CARD['d_model']} numbers out", "sub": "the same column, reworked", "accent": "sky",
              "t0": w("b5", "squeezes") + 0.5, "t1": w("b5", "here") + 0.4, "dx": 60, "dy": -70, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "here"), "t1": en("b5") + 0.5, "accent": "v",
              "lines": [{"text": "The MLP works on each column alone", "size": 30, "wt": 600},
                        {"text": "no column sees another", "size": 24, "c": "slate"}]})
    # b6: all changed
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "changed"), "t1": w("b6", "climb") - 0.2, "accent": "sky",
              "lines": [{"text": "All 100 columns changed", "size": 32, "wt": 600},
                        {"text": "attention mixed in earlier positions; the MLP reworked each one", "size": 22, "c": "slate"}]})
    # b7: only the last one is read out
    E.append({"type": "pin", "anchor": "col99_top", "text": "Position 100: the last column", "sub": f"only its {CARD['d_model']} numbers become the scores",
              "accent": "sky", "t0": w("b7", "last") + 0.5, "t1": en("b7") + 0.5, "dx": -90, "dy": -90, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "scores"), "t1": en("b7") + 0.5, "accent": "sky",
              "lines": [{"text": f"Scores for all {CARD['vocab']:,} tokens", "size": 30, "wt": 600},
                        {"text": "from one column; the other 99 are not read out", "size": 22, "c": "slate"}]})
    # b8: why the 99 matter
    h242, h1913 = HEADS[(24, 2)], HEADS[(19, 13)]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "reads"), "t1": w("b8", "sixty-five") - 0.4, "accent": "sky",
              "lines": [{"text": "The last position reads the other 99", "size": 30, "wt": 600},
                        {"text": f"block 24, 14 heads averaged: {pc(A24[99][92])} on Manchester, {pc(A24[99][34])} on Emma", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "sixty-five") - 0.3, "t1": w("b8", "nineteen") - 0.3, "accent": "sky",
              "lines": [{"text": "Block 24  ·  head 2", "size": 32, "wt": 600},
                        {"text": f"{pc(h242['last_on']['Manchester'])} on Manchester", "size": 26, "c": "ink", "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "nineteen") - 0.3, "t1": w("b8", "without") - 0.2, "accent": "k",
              "lines": [{"text": "Block 19  ·  head 13", "size": 32, "wt": 600},
                        {"text": f"{pc(h1913['last_on']['stores'])} on stores  ·  {pc(h1913['last_question'])} on Emma's question", "size": 24, "c": "ink"}]})
    for i, nm in ((92, "Manchester"), (93, "stores"), (34, "Emma"), (99, "last")):
        if i == 34:
            continue
        E.append({"type": "tag", "anchor": f"col{i}_bot", "text": nm, "t0": st("b8") - 0.2, "t1": en("b8") + 0.3, "size": 22, "mono": False,
                  "hl": "sky" if i == 99 else None, "place": "tc", "dy": 6, "maxdepth": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "without"), "t1": en("b8") + 0.5, "accent": "sky",
              "lines": [{"text": "No other columns, nothing to read", "size": 30, "wt": 600},
                        {"text": "Emma's words reach the answer only through them", "size": 22, "c": "slate"}]})
    # b9: the lens
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "ask"), "t1": w("b9", "eighteen") - 0.3, "accent": "sky",
              "lines": [{"text": "The logit lens", "size": 32, "wt": 600},
                        {"text": "after block k: score the last column now", "size": 24, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "we_front", "text": "We", "t0": w("b9", "fifty-six") + 0.3, "t1": en("b10") + 0.3, "size": 28, "hl": "sky",
              "place": "tc", "dy": 10, "maxdepth": 30})
    # b10: hand-off
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b10", "every"), "t1": en("b10") + 0.6, "accent": "sky",
              "lines": [{"text": f"{CARD['layers']} blocks × {CARD['heads']} heads", "size": 32, "wt": 600},
                        {"text": "next: what each head looks for", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b10") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Inside the stack",
              "sub": "Every token, 24 blocks: Qwen2.5-0.5B-Instruct on Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Every vector and weight is from one recorded run (brain3d/trace.json, build/data/structure_data.json, blocks_data.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    import overlay as O
    from PIL import ImageDraw
    tl = _TL.get("tl")
    if tl is None:
        return
    blk = {b["id"]: b for b in tl["blocks"]}
    F, SW, LF = schedule(tl)
    w = _w(tl)
    d = ImageDraw.Draw(cv)
    # the climb counter
    t_on, t_off = w("b6", "climb") - 0.2, blk["b7"]["at"] + 0.6
    a = O.env(t, t_on, t_off, 0.3, 0.4)
    if a > 0:
        k = max([1] + [k for k, s in SW.items() if s <= t])
        x0, y0 = 96, 130
        d.rounded_rectangle((x0, y0, x0 + 470, y0 + 132), 16, fill=(14, 19, 28, int(215 * a)), outline=(255, 255, 255, int(28 * a)))
        d.rectangle((x0, y0 + 14, x0 + 5, y0 + 118), fill=(60, 144, 255, int(255 * a)))
        d.text((x0 + 28, y0 + 16), f"Block {k} of 24", font=O.font(40, 600), fill=(244, 247, 252, int(255 * a)))
        nch = BD["blocks"][k - 1]["n_changed"]
        d.text((x0 + 28, y0 + 74), f"{nch} of 100 columns changed", font=O.font(24, 500), fill=(164, 176, 196, int(255 * a)))
    # the logit-lens ladder (as in s5_blocks)
    t_on = w("b9", "ask") - 0.2
    t_off = blk["b10"]["at"] + 0.3
    a = O.env(t, t_on, t_off, 0.4, 0.4)
    if a <= 0:
        return
    shown = [k for k in range(1, 25) if LF[k] <= t]
    if not shown:
        return
    import s5_blocks as S5
    cur = shown[-1]
    x0, y0, rw, rh = 1376, 1022 - 150 - 24 * 31, 470, 31
    d.rounded_rectangle((x0 - 18, y0 - 58, x0 + rw + 6, y0 + 24 * rh + 14), 16, fill=(14, 19, 28, int(205 * a)),
                        outline=(255, 255, 255, int(30 * a)))
    d.text((x0, y0 - 46), "After block k, it would say", font=O.font(22, 500), fill=(164, 176, 196, int(255 * a)))
    for k in range(24, 0, -1):
        y = y0 + (24 - k) * rh
        if k not in shown:
            d.text((x0, y + 4), f"{k:>2}", font=O.font(20, 500, True), fill=(110, 120, 140, int(120 * a)))
            continue
        top = LENS[k - 1]["top"][0]
        txt, p = S5.tok_text(top["text"]), top["p"]
        we = top["text"].strip().lower() == "we"
        lit = k == cur
        if lit:
            d.rounded_rectangle((x0 - 8, y, x0 + rw - 4, y + rh - 3), 8, fill=(60, 144, 255, int(70 * a)))
        col = (130, 190, 255) if we else (232, 238, 248)
        al = int(255 * a * (1.0 if (lit or we) else 0.72))
        d.text((x0, y + 4), f"{k:>2}", font=O.font(20, 600, True), fill=(164, 176, 196, al))
        f = S5.cjk(21) if S5.is_cjk(txt) else O.font(21, 600 if we else 500, True)
        f = f or O.font(21, 500, True)
        d.text((x0 + 48, y + 3), txt, font=f, fill=col + (al,))
        d.text((x0 + rw - 22, y + 4), f"{p * 100:5.1f}%", font=O.font(20, 600 if we else 500, True), fill=col + (al,), anchor="ra")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    F, SW, LF = schedule(tl)
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.28))
    for wd in ("how", "many", "city", "e-bike", "battery", "packs", "manchester", "stores"):
        S.append(("tile.mp3", w("b1", wd), 0.14))
    S += [("rise.mp3", w("b2", "column") - 0.1, 0.4), ("fill.mp3", w("b3", "twenty-four"), 0.35), ("rise.mp3", w("b3", "first"), 0.3),
          ("chime.mp3", w("b4", "fourteen"), 0.25), ("beam.mp3", w("b4", "battery"), 0.3), ("tick.mp3", w("b4", "never") + 0.3, 0.35),
          ("beam.mp3", w("b4", "manchester"), 0.3), ("beam.mp3", w("b4", "last"), 0.35), ("rise.mp3", w("b5", "mlp"), 0.3),
          ("fill.mp3", w("b5", "each"), 0.3), ("merge.mp3", w("b5", "four"), 0.3), ("merge.mp3", w("b5", "squeezes"), 0.3),
          ("chime.mp3", w("b6", "changed"), 0.3), ("rise.mp3", w("b6", "climb"), 0.4)]
    for k in range(2, 25, 2):
        S.append(("tick.mp3", F[k], 0.12))
    S += [("chime.mp3", w("b7", "last"), 0.3), ("beam.mp3", w("b7", "scores"), 0.35), ("beam.mp3", w("b8", "reads"), 0.3),
          ("chime.mp3", w("b8", "sixty-five"), 0.3), ("chime.mp3", w("b8", "nineteen"), 0.3)]
    for k in (1, 18, 22, 23, 24):
        S.append(("tick.mp3", LF[k], 0.3))
    S += [("rise.mp3", w("b9", "fifty-six") - 0.2, 0.35), ("fill.mp3", w("b10", "every"), 0.3), ("resolve.mp3", blk["b10"]["speech_end"] + 0.6, 0.45)]
    return S


POSTER = 0.0


def _poster():
    try:
        tl = json.load(open(os.path.join(HERE, "timeline", "blocks.json")))
        return _w(tl)("b8", "sixty-five") + 1.2
    except Exception:
        return 110.0


POSTER = _poster()
