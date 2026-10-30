"""2D overlays + SFX for the overture. Numbers from brain3d/trace.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
TOK = T["tokens"]
META = T["meta"]
TRUTH = T["facts"]["truth"]
POSTER = 31.0
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.42  # the overture has more music than voice
MUSIC_OFFSET = 0.0


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
    E = [{"type": "title", "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The Brain", "t0": 0.4, "t1": st("b1") + 0.6, "size": 80}]
    for i in range(78, 100):
        E.append({"type": "tag", "anchor": f"tok{i}_front", "text": show(TOK[i]["text"]), "t0": st("b1") + 0.4 + max(0, i - 80) * 0.12,
                  "t1": en("b2") + 0.3, "size": 22 if 80 <= i <= 94 else 19, "hl": "sky" if i == 92 else None, "place": "tc", "dy": 10,
                  "maxdepth": 3.4})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "one"), "t1": w("b2", "twenty-four") - 0.2, "accent": "sky",
              "lines": [{"text": f"{T['prompt']['n_tokens']} tokens in", "size": 34, "wt": 600},
                        {"text": "the app's instructions, Emma's question, the chat markers", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "twenty-four"), "t1": w("b2", "every") - 0.2, "accent": "sky",
              "lines": [{"text": f"{META['layers']} blocks", "size": 34, "wt": 600},
                        {"text": f"Qwen2.5-0.5B-Instruct, {META['params']:,} weights", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "every"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "1 token chosen from", "size": 24, "c": "slate"}, {"text": f"{META['vocab']:,}", "size": 44, "wt": 600, "mono": True}]})
    E.append({"type": "pin", "anchor": "ans2_top", "text": "100", "sub": "a confident answer, invented", "accent": "ember",
              "t0": w("b3", "one"), "t1": w("b3", "today") - 0.2, "dx": -40, "dy": -120, "mono": True, "size": 40})
    E.append({"type": "pin", "anchor": "plaque_top", "text": f"{TRUTH:,}", "sub": "the truth, in Ledgerline", "accent": "green",
              "t0": w("b3", "five"), "t1": w("b3", "today") + 1.5, "dx": 60, "dy": -120, "mono": True, "size": 40})
    E.append({"type": "end", "t0": en("b3") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "The Brain",
              "sub": "How an LLM works, followed through one question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Qwen2.5-0.5B-Instruct, one recorded run (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.2, 0.55), ("whoosh.mp3", blk["b2"]["at"] - 0.45, 0.3), ("whoosh.mp3", blk["b3"]["at"] - 0.45, 0.3)]
    for word in ("how", "battery", "manchester"):
        S.append(("tick.mp3", w("b1", word), 0.3))
    S += [("beam.mp3", w("b2", "turn") - 0.2, 0.4), ("tile.mp3", w("b3", "one") + 0.1, 0.45), ("chime.mp3", w("b3", "truth") + 0.3, 0.4),
          ("resolve.mp3", blk["b3"]["speech_end"] + 0.6, 0.5)]
    return S
