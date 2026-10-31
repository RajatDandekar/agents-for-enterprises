"""2D overlays + SFX for film s4, "Attention: tokens look back". Numbers from brain3d/trace.json (attention)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
TOK = T["tokens"]
A = T["attention"]
AVG = A["last"]["avg"]
M = [sum(AVG[l][j] for l in range(24)) / 24 for j in range(100)]
SHARE = A["last"]["share_by_role"]
HEADS = {h["looks_at"]: h for h in A["heads"]}
ROW_B = dict((j, w) for j, w in A["rows"]["avg"][86])
LAST, MAN, BATT, PACKS = 99, 92, 86, 87
POSTER = 39.3  # beams lit, 65.2% on Manchester
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 40.0


def show(t):
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
    pc = lambda x: f"{x * 100:.1f}%"  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 5", "title": "Attention: tokens look back", "t0": 0.4, "t1": st("b1") + 3.5}]
    # token names under the tiles, whenever the row is seen up close
    wins = [(st("b1") + 0.6, en("b1") + 0.4), (st("b2") - 0.2, w("b2", "markers") - 0.4), (w("b2", "fifth") - 0.2, w("b3", "twelve") - 0.5),
            (st("b4") - 0.1, en("b4") + 0.4)]
    for i in list(range(78, 100)):
        hero = i in (BATT, PACKS, MAN, 93, LAST, 82, 81, 83, 85)
        for a, b in wins:
            E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": a, "t1": b,
                      "size": 24 if hero else 20, "hl": "sky" if i in (MAN, LAST, BATT) else None, "place": "tc", "dy": 10})
    # b2: the average
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "averaged"), "t1": w("b2", "markers") - 0.4, "accent": "sky",
              "lines": [{"text": "Where position 100 looks", "size": 32, "wt": 600},
                        {"text": "average of 14 heads × 24 blocks  ·  thicker = more weight", "size": 24, "c": "slate"}]})
    for j, sub in ((99, "itself"), (94, "the question mark"), (MAN, "Manchester")):
        E.append({"type": "pin", "anchor": f"c{j}_top", "text": pc(M[j]), "sub": sub, "t0": w("b2", "blocks") - 0.2 + (0.3 if j != 99 else 0),
                  "t1": w("b2", "markers") - 0.4, "dx": 60 if j != 99 else 70, "dy": -70 if j != 94 else -120, "mono": True, "size": 28})
    E.append({"type": "chip", "x": 1824, "y": 130, "anchor": "tr", "t0": w("b2", "markers"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "Share of the weight, by role", "size": 24, "c": "slate"},
                        {"text": f"chat markers   {pc(SHARE['template'])}", "size": 30, "wt": 600, "mono": True},
                        {"text": f"Emma's question   {pc(SHARE['user'])}", "size": 30, "wt": 600, "mono": True, "c": "q"},
                        {"text": f"system prompt   {pc(SHARE['system'])}", "size": 30, "wt": 600, "mono": True}]})
    E.append({"type": "pin", "anchor": "c0_top", "text": pc(M[0]), "sub": "<|im_start|>, the very first token", "t0": w("b2", "markers") + 0.2,
              "t1": w("b2", "fifth") - 0.5, "dx": 70, "dy": -80, "mono": True, "size": 30})
    # b3: three heads
    hm, hb, hs = HEADS["Manchester"], HEADS["battery"], HEADS["start"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "twenty-four") - 0.2, "t1": w("b3", "sixteen") - 0.5, "accent": "q",
              "lines": [{"text": f"Block {hm['layer']}  ·  head {hm['head']}", "size": 32, "wt": 600},
                        {"text": "looks for the place", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": f"c{MAN}_top", "text": pc(hm["weight_last"]), "sub": "Manchester", "accent": "q",
              "t0": w("b3", "sixty-five"), "t1": w("b3", "sixteen") - 0.5, "dx": 70, "dy": -80, "mono": True, "size": 34})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "sixteen") - 0.2, "t1": w("b3", "twelve") - 0.5, "accent": "k",
              "lines": [{"text": f"Block {hb['layer']}  ·  head {hb['head']}", "size": 32, "wt": 600},
                        {"text": "the head that looks hardest at battery", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": f"c{BATT}_top", "text": pc(hb["weight_last"]), "sub": "battery", "accent": "k",
              "t0": w("b3", "nine"), "t1": w("b3", "twelve") - 0.5, "dx": 70, "dy": -80, "mono": True, "size": 34})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "twelve") - 0.2, "t1": en("b3") + 0.4, "accent": "v",
              "lines": [{"text": f"Block {hs['layer']}  ·  head {hs['head']}", "size": 32, "wt": 600},
                        {"text": f"{pc(hs['weight_last'])} on position 1, <|im_start|>: a resting head", "size": 24, "c": "slate"}]})
    # b4: the mask
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "rule"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "The causal mask", "size": 32, "wt": 600},
                        {"text": "each position sees itself and what came before, never after", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "wall_top", "text": "no looking forward", "accent": "sky", "t0": w("b4", "forward"),
              "t1": en("b4") + 0.4, "dx": 70, "dy": -40, "size": 26})
    for j, nm in ((0, "<|im_start|>"), (85, "ike"), (81, "many")):
        E.append({"type": "pin", "anchor": f"c{j}_top", "text": pc(ROW_B[j]), "sub": f"battery looks at {nm}", "t0": w("b4", "see") + 0.4,
                  "t1": w("b4", "not") - 0.2, "dx": 60, "dy": -40, "mono": True, "size": 26})
    # b5
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "fourteen"), "t1": en("b5") + 0.4, "accent": "sky",
              "lines": [{"text": "14 heads × 24 blocks = 336 heads", "size": 32, "wt": 600},
                        {"text": "each mixes what it found into the column", "size": 24, "c": "slate"}]})
    for k, txt, acc in ((24, "block 24 · head 2", "q"), (16, "block 16 · head 0", "k"), (12, "block 12 · head 13", "v")):
        E.append({"type": "pin", "anchor": f"tower_pin_f{k}", "text": txt, "accent": acc, "t0": w("b5", "side") + 0.6,
                  "t1": en("b5") + 0.4, "dx": 60, "dy": -20, "size": 24})
    E.append({"type": "end", "t0": en("b5") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Attention: tokens look back",
              "sub": "Qwen2.5-0.5B-Instruct, the last position of Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every weight is from one recorded run of the model (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.35))
    S += [("rise.mp3", 0.6, 0.3), ("beam.mp3", w("b1", "back") - 0.1, 0.35), ("chime.mp3", w("b2", "last"), 0.3),
          ("beam.mp3", w("b2", "looks") - 0.1, 0.5), ("tick.mp3", w("b2", "markers"), 0.3), ("tick.mp3", w("b2", "fifth"), 0.3),
          ("beam.mp3", w("b3", "twenty-four") - 0.2, 0.4), ("chime.mp3", w("b3", "sixty-five"), 0.3),
          ("beam.mp3", w("b3", "sixteen") - 0.2, 0.4), ("beam.mp3", w("b3", "twelve") - 0.2, 0.45),
          ("tile.mp3", w("b4", "rule") + 0.7, 0.45), ("beam.mp3", w("b4", "battery") - 0.1, 0.35), ("tick.mp3", w("b4", "not") + 0.3, 0.35),
          ("fill.mp3", w("b5", "side"), 0.35), ("resolve.mp3", blk["b5"]["speech_end"] + 0.6, 0.45)]
    return S
