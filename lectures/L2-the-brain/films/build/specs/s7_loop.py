"""2D overlays + SFX for s7, "The loop: one token at a time". Numbers from brain3d/trace.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
TOK = T["tokens"]
G = T["generation"]["greedy"]
LENS = T["logit_lens"]["digits"][0]["lens"]
SAMPLES = T["generation"]["samples_t07"]
TRUTH = T["facts"]["truth"]
POSTER = 37.0
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 40.0
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
        return hs[nth][edge]
    return w


def elements(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 7", "title": "The loop: one token at a time", "t0": 0.4, "t1": st("b1") + 2.4}]
    # the prompt's last tiles
    for i in range(90, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": 1.0, "t1": en("b2") + 0.3,
                  "size": 20, "place": "tc", "dy": 10, "maxdepth": 3.0})
    # every generated tile: its text under it, from its drop to the end of the answer shot
    drop_t = {0: w("b1", "we"), 1: w("b2", "currently"), 2: w("b2", "have"), 3: w("b2", "space"), 4: w("b3", "one"),
              5: w("b3", "zero"), 6: w("b3", "zero", 1)}
    for j, s in enumerate(G):
        t0 = drop_t.get(j, st("b4") + 2.0)
        if j >= 7:
            t0 = None
        E.append({"type": "tag", "anchor": f"gen{j}_front", "text": show(s["text"]),
                  "t0": (t0 if t0 is not None else 0) + 0.25 if t0 is not None else 0.0, "t1": en("b4") + 0.4, "size": 22,
                  "hl": "ember" if j in DIGITS else None, "place": "tc", "dy": 10, "maxdepth": 4.0, "_late": j >= 7, "_j": j})
    # the late tiles (city ... <|im_end|>) appear on their spoken words
    late_words = {7: "city", 8: "e-bike", 9: "e-bike", 10: "e-bike", 11: "battery", 12: "packs", 13: "available", 14: "in",
                  15: "our", 16: "manchester", 17: "stores", 18: "stores", 19: "stores"}
    for e in E:
        if e.get("_late"):
            j = e["_j"]
            e["t0"] = w("b4", late_words[j]) + {9: 0.2, 10: 0.4, 18: 0.4, 19: 0.7}.get(j, 0.0)
    # probabilities of the first tokens, pinned above them
    probs = [(0, "b1", "we", None), (1, "b2", "currently", f"or have {G[1]['alts'][1]['p'] * 100:.1f}%"),
             (2, "b2", "have", f"or stock {G[2]['alts'][1]['p'] * 100:.1f}%"), (3, "b2", "space", None)]
    for j, b, word, sub in probs:
        e = {"type": "pin", "anchor": f"gen{j}_top", "text": f"{show(G[j]['text'])}  {G[j]['p'] * 100:.1f}%",
             "t0": w(b, word) + 0.4, "t1": en("b2") + 0.3 if j else en("b1") + 0.3, "dx": 40, "dy": -110 + 0 * j,
             "mono": True, "size": 28, "accent": "sky"}
        if sub:
            e["sub"] = sub
        E.append(e)
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "runs"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": "One token = one full pass", "size": 32, "wt": 600},
                        {"text": "all 24 blocks, every time", "size": 24, "c": "slate"}]})
    d0 = G[4]
    alts = " · ".join(f"{a['text']} {a['p'] * 100:.1f}%" for a in d0["alts"][1:4])
    E.append({"type": "pin", "anchor": "gen4_top", "text": f"1  {d0['p'] * 100:.1f}%", "sub": f"then {alts}", "accent": "ember",
              "t0": w("b3", "one") + 0.3, "t1": w("b3", "look") - 0.3, "dx": 50, "dy": -120, "mono": True, "size": 34})
    # the logit lens, floor by floor (blocks 21..24 of the first digit)
    for k, word, nth, dt in ((21, "twenty-one", 0, 0.0), (22, "twenty-one", 0, 0.5), (23, "twenty-three", 0, 0.0), (24, "settles", 0, 0.0)):
        r = LENS[k - 1]
        E.append({"type": "pin", "anchor": f"lens{k}", "text": f"block {k}:  {r['top'][0]['text']}",
                  "sub": f"{r['top'][0]['p'] * 100:.1f}% if it had to speak now", "accent": "ember" if k == 24 else "slate",
                  "t0": w("b3", word, nth) + dt, "t1": w("b3", "then") - 0.4, "dx": 260, "dy": {21: 70, 22: 20, 23: -30, 24: -80}[k],
                  "mono": True, "size": 26})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "logit"), "t1": w("b3", "then") - 0.4, "accent": "ember",
              "lines": [{"text": "Logit lens, first digit", "size": 24, "c": "slate"},
                        {"text": "block 21: 4  ·  22: 4  ·  23: 5  ·  24: 1", "size": 30, "wt": 600, "mono": True}]})
    for j, word, nth in ((5, "zero", 0), (6, "zero", 1)):
        E.append({"type": "pin", "anchor": f"gen{j}_top", "text": f"0  {G[j]['p'] * 100:.1f}%", "accent": "ember",
                  "t0": w("b3", word, nth) + 0.3, "t1": en("b3") + 0.3, "dx": 40, "dy": -110 - 40 * (j - 5), "mono": True, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "twenty"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": f"{len(G)} tokens, {len(G)} passes", "size": 32, "wt": 600},
                        {"text": "the digits 1 0 0 were bets too", "size": 24, "c": "slate"}]})
    # samples
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "temperature"), "t1": en("b5") + 0.4, "accent": "ember",
              "lines": [{"text": "Five samples at temperature 0.7", "size": 30, "wt": 600},
                        {"text": "same model, same question, seeds 0 to 4", "size": 24, "c": "slate"}]})
    sw = [("three", 0), ("one", 0), ("over", 0), ("fifty", 0), ("fifteen", 0)]
    for r, s in enumerate(SAMPLES):
        n = s["numbers"][0]
        txt = f"{n:,}"
        last = f"s{r}_{len(txt) - 1}_top"
        quote = "over 1,000" if "over" in s["text"] else txt
        E.append({"type": "pin", "anchor": last, "text": quote, "sub": f"seed {s['seed']}", "accent": "ember",
                  "t0": w("b5", sw[r][0]) + 0.4, "t1": en("b5") + 0.6, "dx": 50, "dy": -40, "mono": True, "size": 28})
        for c, ch in enumerate(txt):
            E.append({"type": "tag", "anchor": f"s{r}_{c}_front", "text": ch, "t0": w("b5", sw[r][0]) + 0.1 * c, "t1": en("b5") + 0.6,
                      "size": 22, "place": "tc", "dy": 8, "maxdepth": 5.0})
    E.append({"type": "pin", "anchor": "plaque_top", "text": f"Ledgerline:  {TRUTH:,} on hand", "sub": "BAT-500, Manchester main stores",
              "accent": "green", "t0": w("b5", "ledgerline"), "t1": en("b5") + 0.8, "dx": 60, "dy": -80, "size": 30})
    for c, ch in enumerate(f"{TRUTH:,}"):
        E.append({"type": "tag", "anchor": f"t_{c}_front", "text": ch, "t0": w("b5", "thousand") + 0.1 * c, "t1": en("b5") + 0.8,
                  "size": 24, "hl": "green", "place": "tc", "dy": 8, "maxdepth": 5.0})
    E.append({"type": "end", "t0": en("b5") + 1.0, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The loop: one token at a time",
              "sub": "Qwen2.5-0.5B-Instruct, greedy, then 5 samples at temperature 0.7",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every number is from one recorded run of the model (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    for e in E:
        e.pop("_late", None)
        e.pop("_j", None)
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.3))
    for b, word, nth in (("b1", "we", 0), ("b2", "currently", 0), ("b2", "have", 0), ("b2", "space", 0), ("b3", "one", 0),
                         ("b3", "zero", 0), ("b3", "zero", 1)):
        S.append(("tile.mp3", w(b, word, nth) + 0.25, 0.5))
    for word in ("city", "battery", "packs", "available", "manchester", "stores"):
        S.append(("tick.mp3", w("b4", word), 0.3))
    S += [("beam.mp3", w("b1", "runs") - 0.2, 0.35), ("tick.mp3", w("b3", "twenty-one"), 0.3), ("tick.mp3", w("b3", "twenty-three"), 0.3),
          ("chime.mp3", w("b3", "settles"), 0.3)]
    for word in ("three", "one", "over", "fifty", "fifteen"):
        S.append(("tile.mp3", w("b5", word) + 0.2, 0.4))
    S += [("chime.mp3", w("b5", "ledgerline") + 0.2, 0.4), ("resolve.mp3", blk["b5"]["speech_end"] + 0.8, 0.45)]
    return S
