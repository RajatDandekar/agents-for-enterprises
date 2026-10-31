"""2D overlays + SFX for s1, "Next-token prediction". Numbers from brain3d/trace.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
TOK = T["tokens"]
TOP = T["final"]["last"]["1.0"][:6]
DIG = T["final"]["digit"]["1.0"][:6]
GEN = T["generation"]["greedy"][:4]
LAST = len(TOK) - 1
POSTER = 36.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 20.0


def show(t):
    s = t.replace("\n", "\\n")
    return s.strip() if s.strip() else ("(space)" if s == " " else s)


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
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 1", "title": "Next-token prediction", "t0": 0.4, "t1": st("b1") + 3.6}]
    E.append({"type": "pin", "anchor": "model_pin_top", "text": "The model", "sub": "Qwen2.5-0.5B-Instruct, sealed for now",
              "t0": w("b1", "language"), "t1": w("b1", "text") - 0.2, "dx": 80, "dy": -70})
    E.append({"type": "pin", "anchor": "model_pin_in", "text": "Text goes in", "accent": "sky",
              "t0": w("b1", "text"), "t1": en("b1") + 0.3, "dx": -90, "dy": -150})
    E.append({"type": "pin", "anchor": "model_pin_out", "text": "The next token", "sub": "predicted",
              "t0": w("b1", "predicts"), "t1": en("b1") + 0.3, "dx": 90, "dy": -150})
    # token names under the strip tiles
    for i in range(75, LAST + 1):
        for a, b in ((st("b1") + 0.5, en("b1") + 0.3), (st("b2") - 0.2, w("b2", "pass") - 0.7), (st("b4"), w("b4", "digit") - 0.8)):
            E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": a, "t1": b, "size": 22,
                      "hl": "sky" if i == LAST else None, "place": "tc", "dy": 10, "maxdepth": 3.4})
    E.append({"type": "number", "x": 96, "y": 150, "value": "100 tokens", "label": "72 instructions  ·  15 Emma  ·  13 chat markers",
              "t0": w("b2", "hundred"), "t1": w("b2", "pass") - 0.3, "size": 72})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "pass"), "t1": w("b2", "probability") - 0.3, "accent": "sky",
              "lines": [{"text": "One pass", "size": 32, "wt": 600}, {"text": "all 100 tokens are read together", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "model_pin_out", "text": "151,936 probabilities", "sub": "one for every entry in its vocabulary",
              "t0": w("b2", "probability"), "t1": en("b2") + 0.3, "dx": 90, "dy": -170})
    # b3: the bets on the next token
    fill = [w("b3", "we"), w("b3", "as"), w("b3", "manchester"), w("b3", "in"), w("b3", "five") + 0.35, w("b3", "five") + 0.75]
    for k in range(6):
        E.append({"type": "tag", "anchor": f"cand{k}_front", "text": TOP[k]["text"], "t0": st("b3") - 0.3,
                  "t1": (w("b4", "few") - 0.2) if k else en("b4") - 6.0, "size": 24, "hl": "sky" if k == 0 else None, "place": "tc", "dy": 10, "mono": True})
        E.append({"type": "pin", "anchor": f"col{k}_top", "text": f"{TOP[k]['p'] * 100:.1f}%", "t0": fill[k] + 0.5,
                  "t1": w("b4", "few") - 0.3, "dx": 34 if k < 5 else -34, "dy": -36, "size": 28 if k == 0 else 22, "mono": True, "line": False})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "placing") - 0.5, "t1": en("b3") + 0.4, "accent": "sky",
              "lines": [{"text": "Placing bets", "size": 24, "c": "slate"},
                        {"text": f"these 6 hold {sum(x['p'] for x in TOP) * 100:.1f}%", "size": 32, "wt": 600},
                        {"text": f"151,930 other rows share the last {100 - sum(x['p'] for x in TOP) * 100:.1f}%", "size": 22, "c": "slate"}]})
    # b4: the loop and the digit bets
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "chosen"), "t1": w("b4", "pass") - 0.2, "accent": "sky",
              "lines": [{"text": "One token chosen", "size": 32, "wt": 600},
                        {"text": f"We  ({TOP[0]['p'] * 100:.1f}%) joins the text", "size": 22, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "pass"), "t1": w("b4", "few") - 0.2, "accent": "sky",
              "lines": [{"text": "Then the whole pass runs again", "size": 32, "wt": 600},
                        {"text": "once for every new token", "size": 22, "c": "slate"}]})
    for k in range(1, 4):
        E.append({"type": "tag", "anchor": f"ans{k}_front", "text": show(GEN[k]["text"]), "t0": w("b4", "few") + 0.3 + (k - 1) * 0.95,
                  "t1": w("b4", "digit") - 0.8, "size": 22, "hl": "deep", "place": "tc", "dy": 10})
    E.append({"type": "tag", "anchor": "cand0_front", "text": "We", "t0": w("b4", "few") - 0.2, "t1": w("b4", "digit") - 0.8,
              "size": 22, "hl": "deep", "place": "tc", "dy": 10})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "digit") - 0.4, "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "After  “We currently have ”", "size": 24, "c": "slate"}, {"text": "the bets are on a digit", "size": 32, "wt": 600}]})
    dfill = [w("b4", "one", 1), w("b4", "two"), w("b4", "five"), w("b4", "twelve") + 0.4, w("b4", "twelve") + 0.7, w("b4", "twelve") + 1.0]
    for k in range(6):
        E.append({"type": "tag", "anchor": f"dig{k}_front", "text": DIG[k]["text"], "t0": w("b4", "digit") - 0.2, "t1": en("b4") + 0.4,
                  "size": 26, "hl": "sky" if k == 0 else None, "place": "tc", "dy": 10, "mono": True})
        E.append({"type": "pin", "anchor": f"col{k}_top", "text": f"{DIG[k]['p'] * 100:.1f}%", "t0": dfill[k] + 0.5, "t1": en("b4") + 0.4,
                  "dx": 34 if k < 5 else -34, "dy": -36, "size": 28 if k == 0 else 22, "mono": True, "line": False})
    # b5
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "nothing"), "t1": w("b5", "rest") - 0.3, "accent": "ember",
              "lines": [{"text": "No lookup, anywhere", "size": 32, "wt": 600},
                        {"text": "every token of the answer is a bet like these", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "model_pin_win", "text": "Inside: 24 blocks", "sub": "the rest of the lecture opens them",
              "t0": w("b5", "opens") + 0.6, "t1": en("b5") + 0.4, "dx": 120, "dy": -90})
    E.append({"type": "end", "t0": en("b5") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Next-token prediction",
              "sub": "Qwen2.5-0.5B-Instruct on Emma's question, one recorded run",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Probabilities: brain3d/trace.json (temperature 1)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.35))
    S += [("rise.mp3", w("b1", "text"), 0.4), ("chime.mp3", w("b1", "predicts"), 0.3), ("beam.mp3", w("b2", "pass"), 0.35),
          ("tick.mp3", w("b2", "hundred"), 0.3)]
    for word in ("we", "as", "manchester", "in"):
        S.append(("fill.mp3", w("b3", word), 0.32))
    S += [("beam.mp3", w("b4", "chosen"), 0.35), ("tile.mp3", w("b4", "added") + 0.6, 0.45)]
    for k in range(3):
        S.append(("tile.mp3", w("b4", "few") + 0.6 + k * 0.95, 0.35))
    for word, nth in (("one", 1), ("two", 0), ("five", 0)):
        S.append(("fill.mp3", w("b4", word, nth), 0.32))
    S += [("rise.mp3", w("b5", "opens"), 0.4), ("resolve.mp3", blk["b5"]["speech_end"] + 0.6, 0.45)]
    return S
