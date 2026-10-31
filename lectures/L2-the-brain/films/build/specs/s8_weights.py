"""2D overlays + SFX for s8, "Where the weights came from". Numbers from brain3d/trace.json and experiments/logs/tinygpt.json."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
TGL = json.load(open(os.path.join(L2, "experiments", "logs", "tinygpt.json")))
TG = T["tinygpt"]
CURVE = TG["curve"]
TRN = T["training"]
PROMPT = "Stores, 26 Oct 2026: BAT-500 in Manchester stores,"
UNTRAINED = TG["sample_untrained"].split("stores,", 1)[1][:13]
TRAINED = "2,400 on hand"
POSTER = 40.0
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 80.0


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
    params = T["meta"]["params"]
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 8", "title": "Where the weights came from", "t0": 0.4, "t1": st("b1") + 2.4}]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b1", "four"), "t1": en("b1") + 0.4, "accent": "sky",
              "lines": [{"text": f"{params:,} weights", "size": 34, "wt": 600, "mono": True},
                        {"text": "Qwen2.5-0.5B-Instruct, inside its 24 blocks and its tables", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "big_pin_f24", "text": "24 blocks", "sub": "cells shown are illustrative", "accent": "sky",
              "t0": w("b1", "inside"), "t1": en("b1") + 0.4, "dx": 60, "dy": -40, "size": 26})
    cfg = TG["config"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "tiny"), "t1": en("b2") + 0.4, "accent": "slate",
              "lines": [{"text": "Our tiny GPT", "size": 32, "wt": 600},
                        {"text": f"{cfg['layers']} blocks · {cfg['heads']} heads · {cfg['d_model']} numbers a vector · {TG['params']:,} weights", "size": 24, "c": "slate"},
                        {"text": f"trained on Northbridge's own documents ({TG['corpus_chars']:,} characters)", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "tiny_pin_f4", "text": "Random weights", "sub": "before training", "accent": "slate",
              "t0": w("b2", "random"), "t1": en("b2") + 0.3, "dx": 60, "dy": -50, "size": 26})
    for t0, t1 in ((w("b2", "writes") - 0.3, en("b2") + 0.4), (st("b4") - 0.2, w("b4", "invented") - 0.2)):
        E.append({"type": "chip", "x": 1824, "y": 130, "anchor": "tr", "t0": t0, "t1": t1, "accent": "slate",
                  "lines": [{"text": "prompt", "size": 22, "c": "slate"}, {"text": PROMPT, "size": 24, "wt": 500, "mono": True}]})
    for c, ch in enumerate(UNTRAINED):
        if ch == " ":
            continue
        E.append({"type": "tag", "anchor": f"u{c}_front", "text": ch, "t0": w("b2", "writes") + 0.1 * c, "t1": en("b2") + 0.4,
                  "size": 24, "place": "tc", "dy": 8, "maxdepth": 4.0})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "guess"), "t1": w("b3", "loss") - 0.3, "accent": "sky",
              "lines": [{"text": "One training step", "size": 24, "c": "slate"},
                        {"text": "guess the next character  ·  measure the error  ·  nudge every weight", "size": 28, "wt": 600}]})
    c0, c1 = CURVE[0], CURVE[-1]
    E.append({"type": "pin", "anchor": "loss_start", "text": f"loss {c0['train']:.2f}", "sub": "step 0, random guessing", "accent": "slate",
              "t0": w("b3", "four"), "t1": en("b3") + 0.4, "dx": -60, "dy": -40, "mono": True, "size": 28})
    E.append({"type": "pin", "anchor": "loss_end", "text": f"loss {c1['train']:.2f}", "sub": f"step {c1['step']:,}  ·  {TG['train_seconds_cpu2']:.0f} s on 2 CPUs",
              "accent": "sky", "t0": w("b3", "three"), "t1": en("b3") + 0.4, "dx": 40, "dy": -70, "mono": True, "size": 28})
    E.append({"type": "pin", "anchor": "tiny_pin_f4", "text": "Trained weights", "sub": f"{c1['step']:,} steps", "accent": "sky",
              "t0": w("b3", "steps"), "t1": en("b3") + 0.3, "dx": -60, "dy": 40, "size": 26})
    for c, ch in enumerate(TRAINED):
        if ch == " ":
            continue
        E.append({"type": "tag", "anchor": f"tr{c}_front", "text": ch, "t0": w("b4", "perfect") + 0.2 * c + 0.3, "t1": en("b4") + 0.4,
                  "size": 24, "hl": "ember" if (ch.isdigit() or ch == ",") else None, "place": "tc", "dy": 8, "maxdepth": 4.0})
    E.append({"type": "pin", "anchor": "tr4_top", "text": "2,400  invented", "sub": "well formed, T = 0.5", "accent": "ember",
              "t0": w("b4", "invented"), "t1": w("b4", "real") - 0.4, "dx": 40, "dy": -100, "mono": True, "size": 28})
    figs = TGL["stock_figures"]
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "invented") + 0.3, "t1": en("b4") + 0.4, "accent": "ember",
              "lines": [{"text": "Ten more stock lines (T = 0.8, seeds 0 to 9)", "size": 24, "c": "slate"},
                        {"text": "  ".join(f"{x:,}" for x in figs[:5]), "size": 28, "wt": 600, "mono": True},
                        {"text": "  ".join(f"{x:,}" for x in figs[5:]), "size": 28, "wt": 600, "mono": True},
                        {"text": f"none of them 5,400 ({TGL['stock_5400']} of 10)", "size": 24, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "plaque_top", "text": "5,400", "sub": "in its training text 3 times: “Manchester stores has 5,400”",
              "accent": "green", "t0": w("b4", "five", 1), "t1": en("b4") + 0.4, "dx": -60, "dy": -90, "mono": True, "size": 34})
    # Qwen at scale
    for s_, (word, st_) in enumerate(zip(("pretraining", "instruction", "preference"), TRN["stages"])):
        E.append({"type": "pin", "anchor": f"stage{s_}_top", "text": st_["name"], "sub": st_["size"], "accent": "sky",
                  "t0": w("b5", word), "t1": w("b5", "frozen") - 0.5, "dx": {0: -80, 1: 40, 2: 80}[s_], "dy": {0: -200, 1: -320, 2: -200}[s_],
                  "size": 28})
    E.append({"type": "pin", "anchor": "cal_rel_top", "text": "19 Sep 2024", "sub": "release: the weights froze here", "accent": "sky",
              "t0": w("b5", "nineteenth"), "t1": en("b5") + 0.5, "dx": -50, "dy": -110, "size": 32})
    E.append({"type": "pin", "anchor": "cal_ask_top", "text": "26 Oct 2026", "sub": "the day Emma asks", "accent": "ember",
              "t0": w("b5", "emma"), "t1": en("b5") + 0.5, "dx": 60, "dy": -110, "size": 32})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "emma") + 1.2, "t1": en("b5") + 0.5, "accent": "ember",
              "lines": [{"text": "More than two years later", "size": 30, "wt": 600},
                        {"text": "nothing after the release is in the weights", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b5") + 0.9, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Where the weights came from",
              "sub": "The tiny GPT on Northbridge's documents, and Qwen2.5 at scale",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Tiny GPT: experiments/logs/tinygpt.json · Qwen2.5 Technical Report (arXiv:2412.15115)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.45)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.3))
    S += [("beam.mp3", w("b1", "weights"), 0.35), ("tick.mp3", w("b2", "random"), 0.3),
          ("tile.mp3", w("b2", "writes") + 0.2, 0.35), ("tile.mp3", w("b2", "writes") + 0.5, 0.3),
          ("fill.mp3", w("b3", "loss"), 0.4), ("chime.mp3", w("b3", "three") + 0.3, 0.35),
          ("tile.mp3", w("b4", "two"), 0.4), ("tile.mp3", w("b4", "hand"), 0.35), ("chime.mp3", w("b4", "real") + 0.3, 0.35),
          ("tick.mp3", w("b5", "pretraining"), 0.3), ("tick.mp3", w("b5", "instruction"), 0.3), ("tick.mp3", w("b5", "preference"), 0.3),
          ("tile.mp3", w("b5", "frozen"), 0.4), ("tile.mp3", w("b5", "emma"), 0.4),
          ("resolve.mp3", blk["b5"]["speech_end"] + 0.7, 0.45)]
    return S
