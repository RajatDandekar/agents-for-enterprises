"""2D overlays + SFX for the "structure" film, "Inside the model: 24 blocks". Sizes from brain3d/trace.json model_card;
the row's cells from films/build/data/structure_data.json (capture_structure.py)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
CARD = T["model_card"]
TOK = T["tokens"]
POSTER = 52.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 60.0


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
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 5", "title": "Inside the model: 24 blocks", "t0": 0.4, "t1": st("b1") + 3.0}]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "twenty-four"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": f"{CARD['layers']} blocks, all built the same way", "size": 32, "wt": 600},
                        {"text": f"Qwen2.5-0.5B-Instruct  ·  {CARD['params']:,} parameters", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "bt_att3", "text": "Attention", "sub": f"{CARD['heads']} heads, side by side", "accent": "sky",
              "t0": w("b2", "attention"), "t1": en("b2") + 0.4, "dx": -80, "dy": -150, "size": 32})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "back"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": "Each head: a token looks back", "size": 30, "wt": 600},
                        {"text": "at the tokens before it", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "bt_mlp3", "text": "Feed-forward", "sub": f"{CARD['d_model']} to {CARD['mlp_hidden']:,} to {CARD['d_model']} numbers",
              "accent": "v", "t0": w("b3", "feed-forward"), "t1": en("b3") + 0.4, "dx": 80, "dy": -150, "size": 32})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "itself"), "t1": en("b3") + 0.4, "accent": "v",
              "lines": [{"text": "One token's vector at a time", "size": 30, "wt": 600},
                        {"text": "it never looks at the other tokens", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "row_pin", "text": "Emma's question: 100 tokens", "sub": "one column per token  ·  first 16 of 896 numbers shown",
              "accent": "sky", "t0": w("b4", "tokens"), "t1": w("b4", "climb") - 0.2, "dx": -40, "dy": -70, "size": 28})
    for i, nm in ((86, "battery"), (92, "Manchester"), (99, "position 100")):
        E.append({"type": "tag", "anchor": f"row_c{i}", "text": nm, "t0": w("b4", "bottom"), "t1": w("b4", "climb") - 0.2, "size": 22,
                  "hl": "sky" if i == 99 else None, "place": "tc", "dy": 40 if i == 92 else 8, "mono": False, "maxdepth": 6})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "every"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "In every block", "size": 24, "c": "slate"},
                        {"text": "attention gathers, then feed-forward reworks", "size": 30, "wt": 600},
                        {"text": "all 100 vectors come out changed", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "top"), "t1": en("b5") + 0.4, "accent": "sky",
              "lines": [{"text": "After block 24", "size": 32, "wt": 600}, {"text": "next: what the heads look at", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b5") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Inside the model: 24 blocks",
              "sub": "Qwen2.5-0.5B-Instruct, Emma's question passing through every block",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every vector is from one recorded run of the model (films/build/data/structure_data.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.32))
    S += [("fill.mp3", w("b1", "twenty-four"), 0.35), ("chime.mp3", w("b2", "attention"), 0.3), ("chime.mp3", w("b3", "feed-forward"), 0.3),
          ("rise.mp3", w("b4", "enter") - 0.4, 0.4), ("beam.mp3", w("b4", "attention"), 0.3), ("fill.mp3", w("b4", "feed-forward"), 0.3),
          ("tick.mp3", w("b4", "changed"), 0.35), ("rise.mp3", w("b4", "climb"), 0.45), ("chime.mp3", w("b5", "top"), 0.35),
          ("resolve.mp3", blk["b5"]["speech_end"] + 0.6, 0.45)]
    return S
