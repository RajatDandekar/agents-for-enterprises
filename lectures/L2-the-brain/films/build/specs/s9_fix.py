"""2D overlays + SFX for s9, "Why it made the number up, and what fixes it". Numbers from brain3d/trace.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
TOK = T["tokens"]
G = T["generation"]["greedy"]
F = T["facts"]
FT = F["tokens"]
FG = F["greedy"]
BH = F["attention_to_fact"]["best_head"]
DATE = [t["i"] for t in TOK if t["digit"]]
QPOS = T["attention"]["digit"]["query_pos"]
POSTER = 55.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 120.0


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
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 9", "title": "Why it made the number up, and what fixes it", "t0": 0.4,
          "t1": st("b1") + 2.4, "size": 56}]
    # the first answer's tiles
    for j in range(7):
        dig = G[j]["text"].strip().isdigit()
        E.append({"type": "tag", "anchor": f"gen{j}_front", "text": show(G[j]["text"]), "t0": 0.6, "t1": st("b3") - 0.4, "size": 22,
                  "hl": "ember" if dig else None, "place": "tc", "dy": 10, "maxdepth": 4.0})
    E.append({"type": "pin", "anchor": "gen4_top", "text": "100", "sub": "invented: Ledgerline has 5,400", "accent": "ember",
              "t0": w("b1", "one") , "t1": w("b1", "trace") - 0.2, "dx": 60, "dy": -110, "mono": True, "size": 36})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "looking"), "t1": en("b1") + 0.4, "accent": "ember",
              "lines": [{"text": f"Writing the 1, it looks back over {QPOS + 1} tokens", "size": 30, "wt": 600},
                        {"text": "arcs: its attention, averaged over all 14 heads and 24 blocks", "size": 24, "c": "slate"}]})
    # the date: the only digits
    for i in range(40, 54):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": st("b2") - 0.2, "t1": w("b2", "nothing") - 0.4,
                  "size": 24 if i in DATE else 20, "hl": "ember" if i in DATE else None, "place": "tc", "dy": 10, "maxdepth": 3.5})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "date"), "t1": w("b2", "nothing") - 0.4, "accent": "ember",
              "lines": [{"text": "The only digits in the prompt", "size": 30, "wt": 600},
                        {"text": "“Today is Monday 26 October 2026.”", "size": 24, "c": "slate"}]})
    for i in range(80, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": w("b2", "nothing") - 0.2, "t1": st("b3") + 2.6,
                  "size": 21, "place": "tc", "dy": 10, "maxdepth": 3.2})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "nothing"), "t1": en("b2") + 0.4, "accent": "slate",
              "lines": [{"text": "No stock figure anywhere in the input", "size": 30, "wt": 600},
                        {"text": "so it wrote a plausible number", "size": 24, "c": "slate"}]})
    # the fact line
    for i in F["fact_positions"]:
        num = FT[i]["text"].strip().replace(",", "").isdigit() or FT[i]["text"] == ","
        E.append({"type": "tag", "anchor": f"fact{i}_front", "text": show(FT[i]["text"]), "t0": w("b3", "ledgerline") + 0.18 * (i - F["fact_positions"][0]),
                  "t1": en("b4") + 0.4, "size": 22, "hl": "green" if num else None, "place": "tc", "dy": 10, "maxdepth": 3.6})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "ledgerline"), "t1": en("b3") + 0.5, "accent": "green",
              "lines": [{"text": "One line added to the system prompt", "size": 24, "c": "slate"},
                        {"text": F["line"], "size": 28, "wt": 600, "mono": True},
                        {"text": f"{len(F['fact_positions'])} tokens: the prompt is now {F['n_tokens']}", "size": 24, "c": "slate"}]})
    # the new answer
    for j in range(8):
        dig = FG[j]["text"].strip().isdigit() or FG[j]["text"] == ","
        E.append({"type": "tag", "anchor": f"new{j}_front", "text": show(FG[j]["text"]), "t0": w("b4", "same") + 0.2 * j if j < 3 else w("b4", "five") + 0.17 * (j - 3),
                  "t1": en("b5") + 0.5, "size": 24, "hl": "green" if dig else None, "place": "tc", "dy": 10, "maxdepth": 4.0})
    digs = F["digits"]
    E.append({"type": "pin", "anchor": "new3_top", "text": f"5  {digs[0]['p'] * 100:.1f}%", "sub": f"then , {digs[1]['p'] * 100:.1f}%  ·  4 {digs[2]['p'] * 100:.1f}%  ·  0 {digs[3]['p'] * 100:.2f}%",
              "accent": "green", "t0": w("b4", "five") + 0.4, "t1": w("b4", "block") - 0.3, "dx": 50, "dy": -120, "mono": True, "size": 32})
    E.append({"type": "pin", "anchor": "fact91_top", "text": f"{BH['weight'] * 100:.1f}% on these five tokens",
              "sub": f"block {BH['layer']}, head {BH['head']}, writing the 5", "accent": "green", "t0": w("b4", "seventy-seven"),
              "t1": en("b4") + 0.4, "dx": 60, "dy": -150, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "answer"), "t1": w("b4", "block") - 0.3, "accent": "green",
              "lines": [{"text": "Same model, same question", "size": 24, "c": "slate"}, {"text": F["text"], "size": 30, "wt": 600}]})
    # the sockets
    E.append({"type": "pin", "anchor": "sock3_top", "text": "Knowledge", "sub": "Lecture 3: the right facts in the prompt", "accent": "green",
              "t0": w("b5", "three"), "t1": en("b5") + 0.6, "dx": -60, "dy": -150, "size": 32})
    E.append({"type": "pin", "anchor": "sock4_top", "text": "Tools", "sub": "Lecture 4: let it ask Ledgerline itself", "accent": "sky",
              "t0": w("b5", "four"), "t1": en("b5") + 0.6, "dx": 60, "dy": -150, "size": 32})
    E.append({"type": "end", "t0": en("b5") + 1.0, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The right facts, in front of the brain",
              "sub": "Next: Lecture 3, Knowledge  ·  Lecture 4, Tools",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every number is from one recorded run of Qwen2.5-0.5B-Instruct (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.3))
    S += [("beam.mp3", w("b1", "trace"), 0.45), ("chime.mp3", w("b2", "date"), 0.3), ("tick.mp3", w("b2", "plausible"), 0.3),
          ("rise.mp3", w("b3", "add"), 0.35), ("tile.mp3", w("b3", "ledgerline"), 0.4), ("tile.mp3", w("b3", "five", 1), 0.4),
          ("tile.mp3", w("b4", "five"), 0.45), ("beam.mp3", w("b4", "block"), 0.4), ("chime.mp3", w("b4", "seventy-seven"), 0.35),
          ("fill.mp3", w("b5", "three") - 0.1, 0.4), ("fill.mp3", w("b5", "four") - 0.1, 0.4),
          ("resolve.mp3", blk["b5"]["speech_end"] + 0.8, 0.5)]
    return S
