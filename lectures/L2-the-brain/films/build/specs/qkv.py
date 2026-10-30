"""2D overlays + SFX for film A, "Query, key and value". Every number is read from films/qkv_data.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(os.path.dirname(HERE), "qkv_data.json")))
QK = D["qkv"]
TOK = D["tokens"]
W, DOT, SC = QK["weights"], QK["dots"], QK["scores"]
MAN, MAN_SYS, STORES, BATT, LAST = 92, 21, 93, 86, 99
POSTER = 100.5
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 0.0


def show(t):
    s = t.replace("\n", "\\n")
    return s.strip() if s.strip() else s


def elements(tl):
    words = tl["words"]
    blk = {b["id"]: b for b in tl["blocks"]}

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = []
    E.append({"type": "title", "kicker": "Lecture 2  ·  Attention, up close", "title": "Query, key and value", "t0": 0.4, "t1": st("b1") + 4.0})
    # token names, pinned under each tile, in every shot where the row is seen (not in the two macro close-ups)
    wins = [(st("b1") + 1.2, en("b1") + 0.4), (st("b2") - 0.2, en("b2") + 0.4), (w("b4", "sends") - 0.2, w("b4", "multiply") - 0.9),
            (w("b4", "score") - 0.1, en("b7") + 0.4)]
    # the hero tokens' words, laid over their tile faces (sized to the tile; hidden when small or overlapping)
    hero = [(LAST, "⏎"), (MAN, "Manchester"), (MAN_SYS, "Manchester"), (STORES, "stores"), (BATT, "battery"), (87, "packs")]
    for k, (a, b) in enumerate(wins):
        for i, word in hero:
            t0 = a + (0.0 if k else max(0.0, (i - 80) * 0.33))
            E.append({"type": "face", "anchor": f"tok{i}_top", "scale_pin": f"tok{i}_front", "text": word, "t0": t0, "t1": b,
                      "c": "ink", "glyph_font": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if word == "⏎" else None,
                      "max": 60})
    E.append({"type": "pin", "anchor": f"tok{LAST}_top", "text": "Position 100", "sub": "the answer starts here",
              "t0": w("b1", "end"), "t1": en("b1") + 0.3, "dx": 70, "dy": -120})
    # b2: three vectors
    for kind, word, title, sub, acc, dx in (("q", "query", "Query", "what am I looking for?", "q", -90),
                                          ("k", "key", "Key", "what do I contain?", "k", 70),
                                          ("v", "value", "Value", "what I pass on, if chosen", "v", 90)):
        E.append({"type": "pin", "anchor": f"{kind}{LAST}_top", "text": title, "sub": sub, "accent": acc,
                  "t0": w("b2", word), "t1": en("b2") + 0.3, "dx": dx, "dy": -120 if kind != "k" else -210})
    # b3: made by three learned matrices
    E.append({"type": "pin", "anchor": "slab_top", "text": "The token's vector", "sub": "896 numbers, as block 24 reads it",
              "t0": w("b3", "own"), "t1": en("b3") + 0.3, "dx": -140, "dy": -40})
    for kind, nm in (("wq", "W_Q"), ("wk", "W_K"), ("wv", "W_V")):
        E.append({"type": "pin", "anchor": f"{kind}_top", "text": nm, "sub": "learned: 896 in, 64 out", "accent": kind[1],
                  "t0": w("b3", "learned") + {"wq": 0, "wk": 0.25, "wv": 0.5}[kind], "t1": en("b3") + 0.3,
                  "dx": {"wq": -90, "wk": 40, "wv": 90}[kind], "dy": {"wq": -110, "wk": -200, "wv": -110}[kind]})
    q3 = ", ".join(f"{x:.2f}" for x in QK["q"][:3])
    E.append({"type": "chip", "x": 96, "y": 150, "t0": w("b3", "sixty-four"), "t1": en("b3") + 0.5, "accent": "q",
              "lines": [{"text": "Block 24, head 2", "size": 24, "c": "slate"}, {"text": "q, k, v: 64 numbers each", "size": 32, "wt": 600},
                        {"text": f"q = {q3}, …", "size": 24, "mono": True, "c": "q"}]})
    # b4: the query goes out; the dot product, close up
    E.append({"type": "pin", "anchor": "q99_top", "text": "The query of position 100", "accent": "q",
              "t0": w("b4", "sends"), "t1": w("b4", "multiply") - 0.9, "dx": 80, "dy": -80})
    E.append({"type": "chip", "x": 96, "y": 800, "t0": w("b4", "multiply"), "t1": w("b4", "score") - 0.3, "accent": "q",
              "lines": [{"text": "Dot product", "size": 24, "c": "slate"},
                        {"text": "q · k = q1×k1 + q2×k2 + … + q64×k64", "size": 32, "wt": 600, "mono": True}]})
    E.append({"type": "pin", "anchor": "ghostq_top", "text": "query", "sub": "position 100", "accent": "q",
              "t0": w("b4", "multiply") - 0.3, "t1": w("b4", "score") - 0.3, "dx": -70, "dy": 60, "size": 26})
    E.append({"type": "pin", "anchor": "k92_top", "text": "key", "sub": "Manchester", "accent": "k",
              "t0": w("b4", "multiply") - 0.1, "t1": w("b4", "score") - 0.3, "dx": 60, "dy": 60, "size": 26})
    # the running sum, every 8 cells (real partial sums of q_i * k_i)
    run, part = 0.0, []
    for a, b in zip(QK["q"], QK["k"][MAN]):
        run += a * b
        part.append(run)
    t_a, t_b = w("b4", "multiply") + 4 / 30, w("b4", "up") + 6 / 30
    for s in range(8):
        t0 = t_a + (t_b - t_a) * s / 8
        t1 = t_a + (t_b - t_a) * (s + 1) / 8
        last = s == 7
        E.append({"type": "pin", "anchor": "m92_top", "text": f"{part[8 * s + 7]:.1f}", "sub": f"after {8 * (s + 1)} of 64 pairs",
                  "t0": t1, "t1": (w("b4", "score") - 0.3) if last else t1 + (t_b - t_a) / 8 - 0.02, "fin": 0.0, "fout": 0.0 if not last else 0.3,
                  "dx": 70, "dy": -20, "accent": "sky", "mono": True, "size": 34})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "score") + 0.3, "t1": en("b4") + 0.3, "accent": "sky",
              "lines": [{"text": "One dot product per position", "size": 32, "wt": 600},
                        {"text": "100 positions, 100 scores", "size": 24, "c": "slate"}]})
    # b5: scores
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "eight"), "t1": en("b5") + 0.3, "accent": "sky",
              "lines": [{"text": "score = q · k ÷ 8", "size": 34, "wt": 600, "mono": True},
                        {"text": "8 = the square root of 64", "size": 24, "c": "slate"}]})
    seq = [(MAN, "manchester", 0, "Manchester", "in Emma's question"), (MAN_SYS, "system", 0, "Manchester", "in the system prompt"),
           (STORES, "stores", 0, "stores", None), (BATT, "battery", 0, "battery", None)]
    for k, (pos, word, nth, nm, sub) in enumerate(seq):
        t0 = w("b5", word, nth)
        t1 = (w("b5", seq[k + 1][1]) - 0.4) if pos in (MAN, MAN_SYS) else en("b5") + 0.3
        E.append({"type": "pin", "anchor": f"m{pos}_top", "text": f"{nm}  {SC[pos]:.2f}",
                  "sub": (sub + "  ·  " if sub else "") + f"q · k = {DOT[pos]:.1f}", "t0": t0, "t1": t1,
                  "dx": 70 if pos != BATT else -70, "dy": -60, "accent": "sky", "size": 32})
    E.append({"type": "chip", "x": 1824, "y": 130, "anchor": "tr", "t0": w("b5", "place"), "t1": en("b5") + 0.3, "accent": "k",
              "lines": [{"text": "This head looks for a place", "size": 30, "wt": 600},
                        {"text": f"battery gets {W[BATT] * 100:.1f}% here", "size": 24, "c": "slate"}]})
    # b6: softmax
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "softmax"), "t1": en("b6") + 0.3, "accent": "sky",
              "lines": [{"text": "Softmax", "size": 24, "c": "slate"},
                        {"text": "weight = e^score ÷ (sum of e^score)", "size": 32, "wt": 600, "mono": True},
                        {"text": "the 100 weights add up to 1", "size": 24, "c": "slate"}]})
    lead = SC[MAN] - SC[MAN_SYS]
    E.append({"type": "chip", "x": 1824, "y": 130, "anchor": "tr", "t0": w("b6", "magnified"), "t1": w("b6", "sixty-five") - 0.3,
              "accent": "sky", "lines": [{"text": f"{SC[MAN]:.2f} − {SC[MAN_SYS]:.2f} = {lead:.2f} points", "size": 28, "wt": 600, "mono": True},
                                         {"text": f"{W[MAN] * 100:.1f}% ÷ {W[MAN_SYS] * 100:.1f}% = {W[MAN] / W[MAN_SYS]:.1f} times", "size": 28, "wt": 600, "mono": True}]})
    t_soft = w("b6", "softmax") + 1.5
    for pos, nm in ((MAN, "Manchester"), (MAN_SYS, "Manchester, system prompt"), (LAST, "itself, position 100"), (STORES, "stores")):
        E.append({"type": "pin", "anchor": f"m{pos}_top", "text": f"{W[pos] * 100:.1f}%", "sub": nm, "t0": t_soft + (0.4 if pos != MAN else 0),
                  "t1": w("b6", "sixty-five") - 1.0, "size": 30 if pos == MAN else 24, "dx": 50, "dy": -70 if pos == MAN else -40, "mono": True})
    E.append({"type": "pin", "anchor": f"m{MAN}_top", "text": f"{W[MAN] * 100:.0f}%", "sub": "of this head's attention",
              "t0": w("b6", "sixty-five"), "t1": en("b6") + 0.3, "dx": 80, "dy": -60, "size": 48})
    # b7: values
    E.append({"type": "pin", "anchor": "outp_top", "text": "New vector", "sub": "64 numbers, the head's output", "accent": "sky",
              "t0": w("b7", "new"), "t1": en("b7") + 0.4, "dx": 80, "dy": -90})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "added"), "t1": en("b7") + 0.4, "accent": "v",
              "lines": [{"text": "out = sum of weight × value, over all 100 positions", "size": 26, "c": "slate"},
                        {"text": f"= {W[MAN]:.3f} × v(Manchester) + {W[MAN_SYS]:.3f} × v(Manchester, system)", "size": 28, "wt": 600, "mono": True},
                        {"text": f"+ {W[LAST]:.3f} × v(position 100) + {W[STORES]:.3f} × v(stores) + …", "size": 28, "wt": 600, "mono": True}]})
    # b8
    E.append({"type": "pin", "anchor": "tower_pin_f24", "text": "Block 24", "sub": "head 2 of 14", "accent": "sky",
              "t0": w("b8", "passes") + 1.2, "t1": en("b8") + 0.3, "dx": 70, "dy": -40})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "fourteen"), "t1": en("b8") + 0.4, "accent": "sky",
              "lines": [{"text": "14 heads × 24 blocks", "size": 34, "wt": 600}, {"text": "= 336 heads, each with its own query, key and value", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b8") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Query, key and value",
              "sub": "Qwen2.5-0.5B-Instruct, block 24, head 2, on Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every number is from one recorded run of the model (qkv_data.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    return E


def sfx(tl):
    words = tl["words"]
    blk = {b["id"]: b for b in tl["blocks"]}

    def w(b, text, nth=0):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth]["s"]
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.35))
    S += [("chime.mp3", w("b1", "last") - 0.1, 0.35),
          ("rise.mp3", w("b2", "query") - 0.25, 0.4), ("rise.mp3", w("b2", "key") - 0.25, 0.4), ("rise.mp3", w("b2", "value") - 0.25, 0.4),
          ("beam.mp3", w("b3", "learned") - 0.2, 0.4), ("tick.mp3", w("b3", "sixty-four"), 0.3),
          ("beam.mp3", w("b4", "sends") - 0.1, 0.5), ("fill.mp3", w("b4", "number") - 0.1, 0.35),
          ("chime.mp3", w("b4", "up") + 0.2, 0.3), ("fill.mp3", w("b4", "score") - 0.1, 0.35),
          ("tick.mp3", w("b5", "seven"), 0.3), ("tick.mp3", w("b5", "five"), 0.3), ("tick.mp3", w("b5", "four"), 0.3), ("tick.mp3", w("b5", "one"), 0.3),
          ("fill.mp3", w("b6", "softmax") + 0.6, 0.4), ("chime.mp3", w("b6", "sixty-five"), 0.35),
          ("rise.mp3", w("b7", "values"), 0.35), ("merge.mp3", w("b7", "added") - 0.8, 0.5),
          ("beam.mp3", w("b8", "passes"), 0.35), ("tile.mp3", w("b8", "passes") + 1.2, 0.4),
          ("resolve.mp3", blk["b8"]["speech_end"] + 0.6, 0.45)]
    return S
