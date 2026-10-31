"""2D overlays + SFX for `generation`, "Generating the whole answer, token by token".
Numbers: brain3d/trace.json (generation.greedy, logit_lens.digits, generation.samples_t07, facts.truth, model_card) and
build/data/generation_data.json (the KV cache shapes, the cached-vs-full check), from capture_next_gen.py."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
GD = json.load(open(os.path.join(HERE, "data", "generation_data.json")))
TOK = T["tokens"]
G = T["generation"]["greedy"]
LENS = T["logit_lens"]["digits"][0]["lens"]
SAMPLES = T["generation"]["samples_t07"]
TRUTH = T["facts"]["truth"]
CARD = T["model_card"]
POSTER = 52.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 150.0
DIGITS = {4, 5, 6}
_S = {}


def show(t):
    if t == "\n":
        return "\\n"
    if t == " ":
        return "(space)"
    return t.strip() or t


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def drops(tl):
    """Seconds at which answer tile j lands (the scene's D[j] + the 14-frame drop)."""
    w = _w(tl)
    f = lambda b, word, nth=0, d=0: (w(b, word, nth, "s") * 30 + d)  # noqa: E731
    D = {0: f("b1", "joins", 0, -6), 1: f("b5", "currently", 0, -4), 2: f("b5", "have", 0, -4), 3: f("b5", "space", 0, -4),
         4: f("b6", "one", 0, -6), 5: f("b6", "zero", 0, -4), 6: f("b6", "zero", 1, -4), 7: f("b7", "city", 0, -4),
         8: f("b7", "e-bike", 0, -4), 9: f("b7", "e-bike", 0, 2), 10: f("b7", "e-bike", 0, 8), 11: f("b7", "battery", 0, -4),
         12: f("b7", "packs", 0, -4), 13: f("b7", "available", 0, -4), 14: f("b7", "in", 0, -3), 15: f("b7", "our", 0, -2),
         16: f("b7", "manchester", 0, -2), 17: f("b7", "stores", 0, -3), 18: f("b7", "stop", 0, -4), 19: f("b7", "im", 0, -4)}
    return {j: (v + 14) / 30 for j, v in D.items()}


def elements(tl):
    _S["tl"] = tl
    _S["drops"] = drops(tl)
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    dr = _S["drops"]
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 7", "title": "Generating the whole answer, token by token", "t0": 0.4,
          "t1": st("b1") + 2.4}]
    for i in range(84, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_top", "text": show(TOK[i]["text"]), "t0": 0.8, "t1": en("b8") + 0.6,
                  "size": 20, "place": "tc", "dy": -14, "maxdepth": 3.4})
    for j, g in enumerate(G):
        E.append({"type": "tag", "anchor": f"tok{100 + j}_top", "text": show(g["text"]), "t0": dr[j] - 0.1, "t1": en("b9") + 0.6,
                  "size": 22, "hl": "ember" if j in DIGITS else None, "place": "tc", "dy": -14, "maxdepth": 4.4})
    # b1
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "input"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "The input is now 101 tokens", "size": 32, "wt": 600},
                        {"text": "100 for Emma's chat + We", "size": 22, "c": "slate"}]})
    # b2
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "only"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "A position only looks back", "size": 32, "wt": 600},
                        {"text": "the ribbon: where position 100 looks (real attention, all heads and blocks)", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "wall_top", "text": "Never forward", "sub": "later tokens do not exist yet", "accent": "sky",
              "t0": w("b2", "never"), "t1": en("b2") + 0.3, "dx": -80, "dy": 40, "size": 28})
    E.append({"type": "pin", "anchor": "tok95_top", "text": "The 100 earlier columns", "sub": "adding We cannot change them", "accent": "slate",
              "t0": w("b2", "nothing"), "t1": en("b2") + 0.3, "dx": -60, "dy": -120, "size": 28})
    # b3: the cache
    cs = GD["cache_after_prompt"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "cache") - 0.3, "t1": en("b3") + 0.4, "accent": "sky",
              "lines": [{"text": "The KV cache", "size": 34, "wt": 600},
                        {"text": "keys (violet) and values (warm) of every position, in every block", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "st99_f12", "text": f"{GD['cached_numbers_per_position_per_block']} numbers",
              "sub": f"one position, one block: {cs['k'][1]} KV heads × {cs['k'][3]} × (key + value)", "accent": "sky",
              "t0": w("b3", "two"), "t1": w("b3", "six") - 0.2, "dx": 90, "dy": -80, "size": 30, "mono": True})
    E.append({"type": "chip", "x": 96, "y": 300, "t0": w("b3", "six"), "t1": en("b3") + 0.4, "accent": "sky",
              "lines": [{"text": f"100 positions × {cs['layers']} blocks × 256", "size": 24, "c": "slate", "mono": True},
                        {"text": f"= {GD['cached_numbers_after_prompt']:,} numbers kept", "size": 32, "wt": 600, "mono": True}]})
    # b4: the climb
    diffs = max(s["max_abs_diff_cached_vs_full"] for s in GD["steps"])
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "new"), "t1": en("b4") + 0.5, "accent": "sky",
              "lines": [{"text": "One new column, through 24 blocks", "size": 32, "wt": 600},
                        {"text": f"checked: the same scores as recomputing all 101 (largest gap {diffs:.0e})", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "cursor", "text": "Position 100: We", "sub": "the only column computed in this pass", "accent": "sky",
              "t0": w("b4", "column") + 0.2, "t1": w("b4", "but") - 0.1, "dx": 80, "dy": -60, "size": 28})
    E.append({"type": "pin", "anchor": "st95_top", "text": "Each block reads all 101 positions", "sub": "ribbon brightness = that block's real attention (14 heads averaged)",
              "accent": "sky", "t0": w("b4", "reads"), "t1": en("b4") + 0.5, "dx": -40, "dy": -110, "size": 28})
    # b5: probabilities
    probs = [(1, "currently", f"or have {G[1]['alts'][1]['p'] * 100:.1f}%"), (2, "have", f"or stock {G[2]['alts'][1]['p'] * 100:.1f}%"),
             (3, "space", f"or a {G[3]['alts'][1]['p'] * 100:.1f}%")]
    for j, word, sub in probs:
        E.append({"type": "pin", "anchor": f"tok{100 + j}_top", "text": f"{show(G[j]['text'])}  {G[j]['p'] * 100:.1f}%", "sub": sub,
                  "t0": w("b5", word) + 0.3, "t1": en("b5") + 0.3 if j == 3 else (w("b5", "have") - 0.2 if j == 1 else w("b5", "space") - 0.2),
                  "dx": 50, "dy": -120, "mono": True, "size": 28, "accent": "sky"})
    # b6: the digits + the logit lens
    d0 = G[4]
    E.append({"type": "pin", "anchor": "tok104_top", "text": f"1  {d0['p'] * 100:.1f}%",
              "sub": "then " + " · ".join(f"{a['text']} {a['p'] * 100:.1f}%" for a in d0["alts"][1:4]), "accent": "ember",
              "t0": w("b6", "one") + 0.3, "t1": w("b6", "look") - 0.2, "dx": 60, "dy": -120, "mono": True, "size": 34})
    for k, word, dy in ((21, "twenty-one", 60), (22, "twenty-two", 10), (23, "twenty-three", -40), (24, "twenty-four", -90)):
        r = LENS[k - 1]
        E.append({"type": "pin", "anchor": f"lens{k}", "text": f"block {k}:  {r['top'][0]['text']}",
                  "sub": f"{r['top'][0]['p'] * 100:.1f}% if it had to answer here", "accent": "ember" if k < 24 else "sky",
                  "t0": w("b6", word), "t1": w("b6", "then", 1) - 0.3, "dx": 120, "dy": dy, "mono": True, "size": 26})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "look"), "t1": w("b6", "then", 1) - 0.3, "accent": "ember",
              "lines": [{"text": "Inside the column that chose the digit (logit lens)", "size": 22, "c": "slate"},
                        {"text": "block 21: 4  ·  22: 4  ·  23: 5  ·  24: 1", "size": 30, "wt": 600, "mono": True}]})
    for j, word, nth in ((5, "zero", 0), (6, "zero", 1)):
        E.append({"type": "pin", "anchor": f"tok{100 + j}_top", "text": f"0  {G[j]['p'] * 100:.1f}%", "accent": "ember",
                  "t0": w("b6", word, nth) + 0.3, "t1": en("b6") + 0.3, "dx": 40, "dy": -110 - 50 * (j - 5), "mono": True, "size": 30})
    # b7: the rest and the stop token
    e19 = G[19]
    E.append({"type": "pin", "anchor": "tok119_top", "text": f"<|im_end|>  {e19['p'] * 100:.1f}%", "sub": "the stop token: no more passes",
              "accent": "sky", "t0": w("b7", "im") + 0.3, "t1": en("b7") + 0.4, "dx": 40, "dy": -130, "mono": True, "size": 28})
    shown = [show(g["text"]) if g["text"] != " " else "(space)" for g in G]
    E.append({"type": "chip", "x": 96, "y": 290, "t0": w("b7", "twenty") + 0.3, "t1": en("b7") + 0.5, "accent": "sky",
              "lines": [{"text": "The answer, as the model wrote it: 20 tokens", "size": 22, "c": "slate"},
                        {"text": " | ".join(shown[:10]), "size": 28, "wt": 600, "mono": True},
                        {"text": " | ".join(shown[10:]), "size": 28, "wt": 600, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "twenty"), "t1": en("b7") + 0.5, "accent": "sky",
              "lines": [{"text": f"{len(G)} tokens = {len(G)} passes", "size": 32, "wt": 600},
                        {"text": "one over the 100-token prompt, then 19 single new columns", "size": 22, "c": "slate"}]})
    # b8: samples
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "temperature"), "t1": en("b8") + 0.4, "accent": "ember",
              "lines": [{"text": "Five samples at temperature 0.7", "size": 30, "wt": 600},
                        {"text": "same model, same question, seeds 0 to 4", "size": 22, "c": "slate"}]})
    sw = [("three", 0), ("one", 0), ("over", 0), ("fifty", 0), ("fifteen", 0)]
    for r, s in enumerate(SAMPLES):
        txt = f"{s['numbers'][0]:,}"
        quote = "over 1,000" if "over" in s["text"] else txt
        E.append({"type": "pin", "anchor": f"s{r}_{len(txt) - 1}_top", "text": quote, "sub": f"seed {s['seed']}", "accent": "ember",
                  "t0": w("b8", sw[r][0], sw[r][1]) + 0.4, "t1": en("b8") + 0.6, "dx": 50, "dy": -40, "mono": True, "size": 28})
        for c, ch in enumerate(txt):
            E.append({"type": "tag", "anchor": f"s{r}_{c}_front", "text": ch, "t0": w("b8", sw[r][0], sw[r][1]) + 0.1 * c,
                      "t1": en("b8") + 0.6, "size": 22, "place": "tc", "dy": 8, "maxdepth": 5.0})
    E.append({"type": "pin", "anchor": "plaque_top", "text": f"Ledgerline:  {TRUTH:,} on hand", "sub": "BAT-500, Manchester main stores",
              "accent": "green", "t0": w("b8", "ledgerline"), "t1": en("b8") + 0.8, "dx": 60, "dy": -80, "size": 30})
    for c, ch in enumerate(f"{TRUTH:,}"):
        E.append({"type": "tag", "anchor": f"t_{c}_front", "text": ch, "t0": w("b8", "five") + 0.1 * c, "t1": en("b8") + 0.8,
                  "size": 24, "hl": "green", "place": "tc", "dy": 8, "maxdepth": 5.0})
    # b9
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "same"), "t1": w("b9", "where") - 0.2, "accent": "sky",
              "lines": [{"text": "One machine, run once per token", "size": 32, "wt": 600},
                        {"text": f"24 blocks  ·  {CARD['params']:,} weights, the same for every token", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "where"), "t1": en("b9") + 0.5, "accent": "sky",
              "lines": [{"text": "Where did the weights come from?", "size": 40, "wt": 600}]})
    E.append({"type": "end", "t0": en("b9") + 1.0, "kicker": "Agentic Systems Engineering  ·  Lecture 2",
              "title": "Generating the whole answer, token by token",
              "sub": "Qwen2.5-0.5B-Instruct with a KV cache: greedy, then 5 samples at temperature 0.7",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Every number is from recorded runs of the model (brain3d/trace.json, build/data/generation_*.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    """The progress counter: answer token k of 20, the input length of the next pass, one slot per answer token."""
    import overlay as O
    tl = _S.get("tl")
    if tl is None:
        return
    blk = {b["id"]: b for b in tl["blocks"]}
    t0, t1 = blk["b1"]["at"] + 0.2, blk["b7"]["speech_end"] + 0.8
    if not (t0 <= t <= t1 + 0.4):
        return
    a = O.env(t, t0, t1, 0.4, 0.4)
    dr = _S["drops"]
    k = sum(1 for j in range(20) if t >= dr[j])
    lines = [("Answer", 20, 500, "slate", False), (f"token {max(1, k)} of 20", 34, 600, "ink", True)]
    if k < 20:
        lines.append((f"next pass reads {100 + k} tokens", 21, 500, "slate", False))
    else:
        lines.append(("stopped at <|im_end|>", 21, 500, "slate", False))
    spr = O.card(lines, accent="sky", pad=(20, 12))
    img, pad = spr
    cw = img.size[0] - 2 * pad
    x0 = 1920 - 70 - max(cw, 20 * 17)
    O.put(cv, spr, x0, 54, a)
    # 20 slots
    from PIL import ImageDraw
    d = ImageDraw.Draw(cv)
    y = 54 + img.size[1] - 2 * pad + 12
    for j in range(20):
        x = x0 + j * 17
        on = t >= dr[j]
        c = (196, 81, 31) if j in DIGITS else (60, 144, 255)
        fill = (c[0], c[1], c[2], int(235 * a)) if on else (40, 48, 64, int(160 * a))
        d.rounded_rectangle((x, y, x + 13, y + 13), 3, fill=fill)


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    dr = drops(tl)
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.26))
    for j in range(20):
        S.append(("tile.mp3" if j < 7 or j == 19 else "tick.mp3", dr[j] - 0.3, 0.42 if j < 7 else 0.28))
    S += [("beam.mp3", w("b1", "pass") - 0.3, 0.3), ("rise.mp3", w("b2", "only"), 0.3), ("chime.mp3", w("b2", "never"), 0.3),
          ("fill.mp3", w("b3", "keys"), 0.35), ("chime.mp3", w("b3", "cache"), 0.35), ("rise.mp3", w("b4", "new"), 0.4),
          ("beam.mp3", w("b4", "reads"), 0.35), ("tick.mp3", w("b6", "twenty-one"), 0.3), ("tick.mp3", w("b6", "twenty-three"), 0.3),
          ("chime.mp3", w("b6", "settles"), 0.3), ("resolve.mp3", w("b7", "stop", 1), 0.3)]
    for word in ("three", "one", "over", "fifty", "fifteen"):
        S.append(("tile.mp3", w("b8", word) + 0.2, 0.4))
    S += [("chime.mp3", w("b8", "ledgerline") + 0.2, 0.4), ("bloom.mp3", w("b9", "machine"), 0.35),
          ("resolve.mp3", blk["b9"]["speech_end"] + 0.9, 0.45)]
    return S
