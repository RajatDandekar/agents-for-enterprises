"""2D overlays + SFX for `next_token`, "From the last vector to the next token: logits and softmax".
Numbers: build/data/next_token_data.json (capture_next_gen.py), brain3d/trace.json (tokens, final.dial_last),
build/data/structure_data.json (the recap columns). The meters' numbers come from kit/next_gen_sched.py, the same
schedule the scene uses."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "kit"))
import next_gen_sched as NS  # noqa: E402

L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
ND = json.load(open(os.path.join(HERE, "data", "next_token_data.json")))
TOK = T["tokens"]
CARD = T["model_card"]
TOP = ND["top"]
POSTER = 104.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 60.0
_S = {}


def show(t):
    if t == "\n":
        return "\\n"
    return t.strip() or t


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def big(n):
    return f"{n / 1e9:.2f} bn" if n >= 1e9 else f"{n / 1e6:.0f} m"


def elements(tl):
    _S["tl"] = tl
    _S["ms"] = NS.Meters(tl, ND, T["final"]["dial_last"])
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 6", "title": "From the last vector to the next token", "t0": 0.4,
          "t1": st("b1") + 2.6}]
    # ---- recap: the tiles carry their words
    for i in range(78, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "t0": w("b1", "hundred") + 0.2,
                  "t1": en("b2") - 0.2, "size": 20, "place": "tc", "dy": -14, "maxdepth": 4.0})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "hundred"), "t1": w("b1", "each") - 0.1, "accent": "sky",
              "lines": [{"text": "Emma's text: 100 tokens", "size": 32, "wt": 600},
                        {"text": "72 system  ·  15 Emma  ·  13 chat markers", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "each"), "t1": w("b1", "twenty-four") - 0.1, "accent": "sky",
              "lines": [{"text": f"One vector per token: {CARD['d_model']} numbers", "size": 32, "wt": 600},
                        {"text": "each column shows its first 16, the recorded values", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "c99_top", "text": "The last position's final vector", "sub": "after block 24  ·  896 numbers",
              "accent": "sky", "t0": w("b1", "last"), "t1": en("b1") + 0.2, "dx": 80, "dy": -90, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": st("b2"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "How does this vector become the next token?", "size": 34, "wt": 600}]})
    # ---- norm
    pre, post, g = ND["pre_norm"], ND["post_norm"], ND["gamma"]
    E.append({"type": "pin", "anchor": "pre_top", "text": "Before the norm", "sub": f"896 numbers, from {pre['min']:.1f} to {pre['max']:.1f}",
              "accent": "slate", "t0": w("b3", "first") + 0.6, "t1": w("b3", "multiplies") - 0.2, "dx": 150, "dy": 170, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "rms"), "t1": en("b3") + 0.4, "accent": "sky",
              "lines": [{"text": "Final RMSNorm", "size": 24, "c": "slate"},
                        {"text": "x ÷ RMS(x) × gain", "size": 34, "wt": 600, "mono": True},
                        {"text": f"RMS(x) = sqrt(mean of x squared) = {pre['rms']:.2f}", "size": 24, "c": "ink", "mono": True},
                        {"text": f"896 learned gains, average {g['mean']:.1f}", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "post_top", "text": "After the norm", "sub": f"the vector that gets scored  ·  RMS now {post['rms']:.1f}",
              "accent": "sky", "t0": w("b3", "gain") + 0.3, "t1": en("b3") + 0.5, "dx": -70, "dy": 170, "size": 28})
    # ---- the table + the dot product
    d0 = ND["dots"][0]
    E.append({"type": "pin", "anchor": "rack_top", "text": f"The table: {CARD['vocab']:,} rows", "sub": "one row per token  ·  896 numbers each",
              "accent": "sky", "t0": w("b4", "table"), "t1": w("b4", "multiply") - 0.3, "dx": 90, "dy": -40, "size": 30})
    E.append({"type": "tag", "anchor": "post_mid", "text": "the vector", "t0": w("b4", "multiply") + 0.6, "t1": en("b4") + 0.3,
              "size": 24, "place": "tc", "dy": 290, "maxdepth": 9, "mono": False})
    E.append({"type": "tag", "anchor": "rack_t1_front", "text": "row of We", "t0": w("b4", "multiply") + 0.6, "t1": en("b4") + 0.3,
              "size": 24, "place": "tc", "dy": 12, "maxdepth": 9, "mono": False, "hl": "sky"})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "multiply") + 0.2, "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "One dot product = one score", "size": 24, "c": "slate"},
                        {"text": "v1×r1 + v2×r2 + … + v896×r896", "size": 32, "wt": 600, "mono": True},
                        {"text": f"row of We: {d0['positive_terms']} products push up, {d0['negative_terms']} pull down", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "dotm_top", "text": f"We:  {d0['logit']:.2f}", "sub": "the sum of all 896 products", "accent": "sky",
              "t0": w("b4", "twenty") + 0.2, "t1": en("b4") + 0.4, "dx": 60, "dy": -60, "mono": True, "size": 32})
    # ---- tied
    E.append({"type": "pin", "anchor": "intile_top", "text": "In: a token reads its row", "sub": "section 3: the embedding lookup", "accent": "sky",
              "t0": w("b5", "embedding"), "t1": en("b5") + 0.4, "dx": -70, "dy": -150, "size": 28})
    E.append({"type": "pin", "anchor": "post_top", "text": "Out: the vector scores every row", "sub": "the same rows, used to score", "accent": "sky",
              "t0": w("b5", "out") - 0.3, "t1": en("b5") + 0.4, "dx": 40, "dy": -80, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "tied"), "t1": en("b5") + 0.5, "accent": "sky",
              "lines": [{"text": "Tied weights", "size": 34, "wt": 600},
                        {"text": f"one table, {CARD['vocab']:,} × {CARD['d_model']} = {CARD['embedding_params']:,} numbers, used twice", "size": 22, "c": "slate"}]})
    # ---- logits
    Lg = ND["logits"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": st("b6"), "t1": w("b6", "we") - 0.3, "accent": "sky",
              "lines": [{"text": f"{Lg['n']:,} logits, one per row", "size": 32, "wt": 600},
                        {"text": f"bar height = how many rows score in that range (log scale)  ·  average {Lg['mean']:.2f}", "size": 22, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "hist_lo", "text": f"{Lg['min']:.1f}", "t0": st("b6") + 0.8, "t1": w("b6", "we") - 0.3, "size": 22, "place": "tc", "dy": 6, "maxdepth": 9})
    E.append({"type": "tag", "anchor": "hist_zero", "text": "0", "t0": st("b6") + 0.8, "t1": w("b6", "we") - 0.3, "size": 22, "place": "tc", "dy": 6, "maxdepth": 9})
    E.append({"type": "tag", "anchor": "hist_hi", "text": f"{Lg['max']:.2f}", "t0": st("b6") + 0.8, "t1": w("b6", "we") - 0.3, "size": 22, "place": "tc", "dy": 6, "maxdepth": 9, "hl": "sky"})
    hb = int((18.0 - Lg["hist"]["lo"]) / (Lg["hist"]["hi"] - Lg["hist"]["lo"]) * Lg["hist"]["bins"])
    E.append({"type": "pin", "anchor": f"hist_b{hb}_top", "text": f"Above 18: only {Lg['n_above_18']} rows", "sub": "We, As, Manchester, In, Our",
              "accent": "sky", "t0": w("b6", "five"), "t1": w("b6", "we") - 0.2, "dx": -60, "dy": -120, "size": 28})
    # ---- softmax
    S = ND["sum_exp"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "raise"), "t1": w("b7", "divide") - 0.1, "accent": "sky",
              "lines": [{"text": "Softmax, move 1: raise e to each logit", "size": 24, "c": "slate"},
                        {"text": f"e^{TOP[0]['logit']:.2f} = {TOP[0]['exp']:,.0f}", "size": 32, "wt": 600, "mono": True},
                        {"text": f"e^{TOP[1]['logit']:.2f} = {TOP[1]['exp']:,.0f}", "size": 26, "c": "ink", "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "divide"), "t1": en("b7") + 0.4, "accent": "sky",
              "lines": [{"text": "Softmax, move 2: divide by the sum over all rows", "size": 24, "c": "slate"},
                        {"text": f"sum of e^logit over {Lg['n']:,} rows = {S:,.0f}", "size": 26, "c": "ink", "mono": True},
                        {"text": f"We: {TOP[0]['exp'] / 1e9:.3f} bn ÷ {S / 1e9:.3f} bn = {TOP[0]['p'] * 100:.1f}%", "size": 32, "wt": 600, "mono": True}]})
    # ---- greedy, the wheel
    E.append({"type": "pin", "anchor": "m0_top", "text": "Greedy: take the top", "sub": "We, every time", "accent": "sky",
              "t0": w("b8", "greedy"), "t1": w("b8", "sampling") - 0.6, "dx": 70, "dy": -70, "size": 28})
    for j, nm in ((0, "We"), (1, "As"), (2, "Manchester"), (3, "In"), (4, "Our")):
        E.append({"type": "tag", "anchor": f"wheel_sk{j}", "text": f"{nm}  {TOP[j]['p'] * 100:.1f}%", "t0": w("b8", "sampling"),
                  "t1": en("b8") + 0.4, "size": 22 if j else 26, "place": "tc", "dy": -12, "maxdepth": 9, "hl": "sky" if j == 0 else None, "mono": False})
    E.append({"type": "tag", "anchor": "wheel_srest", "text": f"{CARD['vocab'] - 12:,} others  {(1 - sum(x['p'] for x in TOP[:12])) * 100:.1f}%", "t0": w("b8", "sampling"), "t1": en("b8") + 0.4,
              "size": 20, "place": "tc", "dy": -12, "maxdepth": 9, "mono": False})
    dr = ND["draws"]["1.0"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "weighted"), "t1": en("b8") + 0.4, "accent": "sky",
              "lines": [{"text": "Sampling at T = 1: a weighted wheel", "size": 24, "c": "slate"},
                        {"text": "each sector = one token's probability", "size": 30, "wt": 600}]})
    E.append({"type": "chip", "x": 96, "y": 300, "t0": w("b8", "thousand"), "t1": en("b8") + 0.4, "accent": "sky",
              "lines": [{"text": f"{dr['n']:,} spins (seed {dr['seed']})", "size": 24, "c": "slate"},
                        {"text": "  ·  ".join(f"{x['text']} {x['count']}" for x in dr["top"][:4]), "size": 28, "wt": 600, "mono": True},
                        {"text": f"{dr['distinct']} different tokens came up", "size": 22, "c": "slate"}]})
    # ---- temperature
    E.append({"type": "chip", "x": 96, "y": 130, "t0": st("b9"), "t1": en("b9") + 0.4, "accent": "sky",
              "lines": [{"text": "Temperature T", "size": 24, "c": "slate"},
                        {"text": "p = e^(logit ÷ T) ÷ sum over all rows", "size": 30, "wt": 600, "mono": True},
                        {"text": "T below 1 sharpens  ·  above 1 flattens  ·  0 = greedy", "size": 22, "c": "slate"}]})
    # ---- the pick
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b10", "choice"), "t1": en("b10") + 0.4, "accent": "sky",
              "lines": [{"text": "Chosen: We", "size": 34, "wt": 600},
                        {"text": f"the first token of the answer  ·  the text is now {len(TOK) + 1} tokens", "size": 22, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "pick_front", "text": "We", "t0": w("b10", "choice") - 0.2, "t1": w("b10", "joins") - 0.5,
              "size": 26, "place": "tc", "dy": 8, "maxdepth": 6})
    E.append({"type": "tag", "anchor": "tok100_front", "text": "We", "t0": w("b10", "joins"), "t1": en("b10") + 0.6,
              "size": 26, "place": "tc", "dy": 8, "maxdepth": 6})
    for i in range(88, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "t0": w("b10", "joins") - 0.6,
                  "t1": en("b10") + 0.6, "size": 20, "place": "tc", "dy": -14, "maxdepth": 4.0})
    E.append({"type": "end", "t0": en("b10") + 0.9, "kicker": "Agentic Systems Engineering  ·  Lecture 2",
              "title": "From the last vector to the next token", "sub": "Qwen2.5-0.5B-Instruct: logits and softmax on Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Every number is from recorded runs of the model (brain3d/trace.json, build/data/next_token_*.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


STEPS = [("b3", "1  RMSNorm"), ("b4", "2  Score every row"), ("b6", "3  Logits"), ("b7", "4  Softmax"), ("b8", "5  Pick one")]


def draw(cv, t, fr, P):
    import overlay as O
    tl = _S.get("tl")
    if tl is None:
        return
    blk = {b["id"]: b for b in tl["blocks"]}
    w = _w(tl)
    t_end = blk["b10"]["speech_end"] + 0.7
    if t > t_end + 0.3:
        return
    fade = 1.0 - O.ease((t - t_end) / 0.3) if t > t_end else 1.0
    # the step tracker (top right), from the norm to the pick
    if blk["b3"]["at"] - 0.3 <= t:
        a = fade * O.ease((t - blk["b3"]["at"] + 0.3) / 0.4)
        cur = max(k for k, (b, _) in enumerate(STEPS) if blk[b]["at"] - 0.3 <= t)
        if t >= blk["b5"]["at"] - 0.3 and t < blk["b6"]["at"] - 0.3:
            cur = 1
        y = 54
        for k, (b, lab) in enumerate(STEPS):
            on = k == cur
            spr = O.card([(lab, 24 if on else 21, 600 if on else 500, "ink" if on else "slate", False)], accent="sky",
                         pad=(14, 8), radius=10, bar=on, bg=(16, 21, 31, 225 if on else 150))
            img, pad = spr
            O.put(cv, spr, 1920 - 60 - (img.size[0] - 2 * pad), y, a * (1.0 if on or k < cur else 0.75))
            y += img.size[1] - 2 * pad + 8
    # the recap's block counter
    f_b0, f_b1 = w("b1", "twenty-four", edge="s") * 30, w("b1", "pass", edge="s") * 30
    if f_b0 - 4 <= fr <= f_b1 + 50:
        lay = min(24, max(0, int(24 * (fr - f_b0) / max(1, f_b1 + 8 - f_b0))))
        a = O.env(fr / 30, f_b0 / 30 - 0.1, (f_b1 + 40) / 30)
        spr = O.card([("Every column, block by block", 22, 500, "slate", False), (f"after block {lay} of 24" if lay else "entering block 1", 32, 600, "ink", True)],
                     accent="sky", pad=(22, 14))
        O.put(cv, spr, 96, 300, a)
    # the dot product's running sum (the real cumulative sum every 32 products)
    ms = _S["ms"]
    f_r0, f_r1 = w("b4", "multiply", edge="s") * 30 + 18, w("b4", "twenty", edge="s") * 30 + 6
    f_r0, f_r1 = int(round(f_r0)), int(round(f_r1))
    if f_r0 <= fr < w("b4", "twenty", edge="s") * 30 + 4:
        cs = ND["dots"][0]["cumsum_every32"]
        u = (fr - f_r0) / max(1, f_r1 - f_r0)
        k = max(0, min(len(cs) - 1, int(u * len(cs))))
        n = min(896, 32 * (k + 1))
        spr = O.card([("Running sum", 20, 500, "slate", False), (f"after {n:>3} of 896 products:  {cs[k]:+6.2f}", 30, 600, "ink", True)],
                     accent="sky", pad=(18, 10))
        O.put(cv, spr, 96, 300, O.ease((fr - f_r0 + 6) / 10))
    # the meters: token under each, value above
    first = min(ms.rise)
    if fr >= first - 4:
        for j in range(7):
            mode, lv, num = ms.level(j, fr)
            if mode == "off":
                continue
            a = fade
            base = P.at(f"m{j}", fr)
            if base:
                lab = TOP[j]["text"] if j < 6 else "all others"
                spr = O.card([(lab, 24, 600, "ink", False)] + ([("151,930 tokens", 17, 400, "slate", False)] if j == 6 else []),
                             accent="sky", pad=(12, 6), radius=10, bar=j == 0)
                O.put(cv, spr, base[0], base[1] + 16, a, anchor="tc")
            top = P.at(f"m{j}_top", fr)
            if top and num is not None:
                if mode == "logit":
                    txt = f"{num:.2f}"
                elif mode == "exp":
                    txt = big(num)
                else:
                    txt = f"{num * 100:.1f}%"
                spr = O.text_sprite(txt, 30 if j == 0 else 25, 600, (130, 190, 255) if j == 0 else "ink", True, True)
                O.put(cv, spr, top[0], top[1] - 10, a, anchor="bc")
        # temperature readout on the dial
        if fr >= ms.f_dial - 20:
            Tn = ms.T(fr)
            p = P.at("dial_top", fr)
            if p:
                spr = O.card([(f"T = {Tn:.2f}", 32, 600, "ink", True)], accent="sky", pad=(16, 10), radius=12)
                O.put(cv, spr, p[0] - 130, p[1] + 60, fade * O.ease((fr - ms.f_dial + 20) / 18), anchor="rc")
            for nm, lab in (("dial_t0", "0"), ("dial_t07", "0.7"), ("dial_t12", "1.2")):
                q = P.at(nm, fr)
                if q:
                    O.put(cv, O.text_sprite(lab, 19, 600, "slate", True, True), q[0], q[1], fade, anchor="c")
    # the wheel: what the pointer landed on
    lands = [("As", "b8", "as", 0), ("City", "b8", "city", 0), ("We", "b8", "we", 1), ("We", "b8", "we", 2), ("We", "b8", "we", 3)]
    shown = [nm for nm, b, word, nth in lands if fr >= w(b, word, nth, "s") * 30 + (6 if word == "city" else 0)]
    if shown and t <= blk["b8"]["speech_end"] + 0.4:
        p = P.at("wheel_pin_ptr", fr)
        if p:
            spr = O.card([(shown[-1], 32, 600, "ink", False)], accent="sky", pad=(16, 8), radius=12)
            O.put(cv, spr, p[0], p[1] - 10, 1.0, anchor="bc")
        spr = O.card([("Five real spins", 20, 500, "slate", False), ("  ·  ".join(shown), 28, 600, "ink", False)], accent="sky", pad=(18, 10))
        O.put(cv, spr, 1920 - 96, 760, 1.0, anchor="tr")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.28))
    S += [("tile.mp3", w("b1", "hundred"), 0.35), ("rise.mp3", w("b1", "vector") - 0.3, 0.35), ("beam.mp3", w("b1", "twenty-four"), 0.3),
          ("chime.mp3", w("b1", "last"), 0.3), ("rise.mp3", w("b3", "divides"), 0.35), ("merge.mp3", w("b3", "multiplies"), 0.35),
          ("beam.mp3", w("b4", "rows") - 0.2, 0.35), ("fill.mp3", w("b4", "multiply") + 0.5, 0.35), ("chime.mp3", w("b4", "twenty"), 0.4),
          ("beam.mp3", w("b5", "reads"), 0.35), ("chime.mp3", w("b5", "tied"), 0.35), ("rise.mp3", blk["b6"]["at"], 0.3),
          ("fill.mp3", w("b6", "five") - 0.1, 0.35), ("fill.mp3", w("b7", "raise"), 0.35), ("merge.mp3", w("b7", "divide"), 0.35),
          ("tick.mp3", w("b8", "we"), 0.3), ("whoosh.mp3", w("b8", "sampling"), 0.3)]
    for word, nth in (("as", 0), ("city", 0), ("we", 1), ("we", 2), ("we", 3)):
        S.append(("tick.mp3", w("b8", word, nth), 0.35))
    S += [("tick.mp3", w("b9", "seven"), 0.3), ("tick.mp3", w("b9", "two"), 0.3), ("tick.mp3", w("b9", "zero", 1), 0.3),
          ("rise.mp3", w("b10", "choice") - 0.3, 0.35), ("tile.mp3", w("b10", "joins"), 0.45), ("beam.mp3", w("b10", "runs") - 0.6, 0.3),
          ("resolve.mp3", blk["b10"]["speech_end"] + 0.8, 0.45)]
    return S
