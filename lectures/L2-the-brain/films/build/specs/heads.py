"""2D overlays + SFX for the "heads" film, "Heads: fourteen ways of looking". Every head number from
build/data/heads_data.json (capture_heads.py on Modal CPU, the same prompt as brain3d/trace.json)."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L2 = os.path.dirname(os.path.dirname(HERE))
T = json.load(open(os.path.join(L2, "brain3d", "trace.json")))
HD = json.load(open(os.path.join(HERE, "data", "heads_data.json")))
HEADS = {(h["block"], h["head"]): h for h in HD["heads"]}
EX = {(e["block"], e["head"]): e for e in HD["examples"]}
TOK = T["tokens"]
CARD = T["model_card"]
GEN = HD["digit_step"]["gen_prefix"]
ROWD = HD["digit_step"]["rows"]["2.7"]
MUSIC = "observatory_out_to_the_world.mp3"
MUSIC_GAIN = 0.34
MUSIC_OFFSET = 100.0


def show(s):
    s = s.replace("\n", "\\n")
    return s.strip() if s.strip() else "(space)"


def text_of(i):
    return TOK[i]["text"] if i < 100 else GEN[i - 100]


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
    h242, h97, h1213, h1913 = HEADS[(24, 2)], HEADS[(9, 7)], HEADS[(12, 13)], HEADS[(19, 13)]
    ex27 = EX[(2, 7)]["numbers"]
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 5", "title": "Heads: fourteen ways of looking", "t0": 0.4, "t1": st("b1") + 2.6}]
    # token words on the tiles, whenever the row is seen up close (faces for Emma's words; small tags for the rest)
    wins = [(st("b1") + 0.2, en("b1") + 0.3), (st("b4") - 0.1, en("b4") + 0.3), (st("b6") - 0.1, en("b7") + 0.3), (st("b8") - 0.1, en("b8") + 0.3)]
    for a, b_ in wins:
        for i in list(range(0, 104)):
            txt = show(text_of(i))
            if 80 <= i <= 94 or i in (44, 45, 48, 49, 50, 51) or i >= 100:
                E.append({"type": "face", "anchor": f"tok{i}_top", "scale_pin": f"tok{i}_front", "text": txt, "t0": a, "t1": b_,
                          "c": "ink", "max": 52})
            else:
                E.append({"type": "tag", "anchor": f"tok{i}_front", "text": txt, "t0": a, "t1": b_, "size": 20, "place": "tc", "dy": 8})
    # b1: one pattern
    E.append({"type": "pin", "anchor": "hmod_top", "text": "One attention pattern", "sub": "block 24, head 2 (real weights)", "accent": "sky",
              "t0": w("b1", "pattern") + 0.3, "t1": en("b1") + 0.3, "dx": 70, "dy": -80, "size": 28})
    E.append({"type": "pin", "anchor": "tok92_top", "text": pc(h242["last_on"]["Manchester"]), "sub": "Manchester", "accent": "sky", "mono": True,
              "t0": w("b1", "manchester") + 0.2, "t1": en("b1") + 0.3, "dx": -40, "dy": -150, "size": 28})
    E.append({"type": "pin", "anchor": "tok86_top", "text": pc(h242["last_on"]["battery"]), "sub": "battery", "accent": "ember", "mono": True,
              "t0": w("b1", "battery") + 0.1, "t1": en("b1") + 0.3, "dx": -60, "dy": -110, "size": 28})
    # b2: split
    E.append({"type": "pin", "anchor": "qbig_top", "text": f"The last token's query: {CARD['d_model']} numbers", "sub": "block 24 (real)", "accent": "sky",
              "t0": w("b2", "eight") + 0.4, "t1": w("b2", "cut") + 0.4, "dx": 60, "dy": -60, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "fourteen"), "t1": w("b2", "each") - 0.2, "accent": "sky",
              "lines": [{"text": f"{CARD['heads']} heads × {CARD['head_dim']} numbers = {CARD['d_model']}", "size": 32, "wt": 600, "mono": False},
                        {"text": "one slice of the query per head", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "each"), "t1": en("b2") + 0.6, "accent": "sky",
              "lines": [{"text": "Each head asks its own question", "size": 30, "wt": 600},
                        {"text": "arc = that head's strongest target, block 24 (real)", "size": 22, "c": "slate"}]})
    # b3: shared keys and values
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "share"), "t1": en("b3") + 0.6, "accent": "k",
              "lines": [{"text": f"{CARD['heads']} query heads, {CARD['kv_heads']} key/value heads", "size": 30, "wt": 600},
                        {"text": "7 query heads share each set of keys and values", "size": 22, "c": "slate"}]})
    for g, (lo, hi) in enumerate(((0, 6), (7, 13))):
        E.append({"type": "pin", "anchor": f"k{g}_top", "text": f"Keys + values, set {g + 1}", "sub": f"heads {lo}–{hi}  ·  64 + 64 numbers",
                  "accent": "k", "t0": w("b3", "two") + 0.2 + 0.3 * g, "t1": en("b3") + 0.4, "dx": -70 if g == 0 else 70, "dy": 90, "size": 24})
    # b4-b8: real heads
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b4", "nine") - 0.2, "t1": en("b4") + 0.5, "accent": "deep",
              "lines": [{"text": "Block 9  ·  head 7", "size": 32, "wt": 600},
                        {"text": f"looks one step back: {pc(h97['prev'])} on the previous token", "size": 24, "c": "ink"},
                        {"text": "average over all 99 positions that have one", "size": 20, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "twelve") - 0.2, "t1": en("b5") + 0.5, "accent": "v",
              "lines": [{"text": "Block 12  ·  head 13", "size": 32, "wt": 600},
                        {"text": f"rests: {pc(h1213['first'])} on position 1, from every position", "size": 24, "c": "ink"}]})
    E.append({"type": "tag", "anchor": "tok0_front", "text": "<|im_start|>  ·  position 1", "t0": w("b5", "first"), "t1": en("b5") + 0.4,
              "size": 22, "hl": "v", "place": "tc", "dy": 10, "mono": True, "maxdepth": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b6", "twenty-four") - 0.2, "t1": en("b6") + 0.5, "accent": "sky",
              "lines": [{"text": "Block 24  ·  head 2", "size": 32, "wt": 600},
                        {"text": f"finds the place: {pc(h242['last_on']['Manchester'])} on Manchester", "size": 24, "c": "ink"}]})
    E.append({"type": "pin", "anchor": "tok92_top", "text": pc(h242["last_on"]["Manchester"]), "sub": "Manchester", "accent": "sky", "mono": True,
              "t0": w("b6", "sixty-five"), "t1": en("b6") + 0.4, "dx": -50, "dy": -170, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b7", "nineteen") - 0.2, "t1": en("b7") + 0.5, "accent": "k",
              "lines": [{"text": "Block 19  ·  head 13", "size": 32, "wt": 600},
                        {"text": f"reads the question: {pc(h1913['last_question'])} on Emma's 15 tokens", "size": 24, "c": "ink"}]})
    E.append({"type": "pin", "anchor": "tok93_top", "text": pc(h1913["last_on"]["stores"]), "sub": "stores", "accent": "k", "mono": True,
              "t0": w("b7", "thirty-six"), "t1": en("b7") + 0.4, "dx": 40, "dy": -170, "size": 30})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b8", "two") - 0.2, "t1": en("b8") + 0.5, "accent": "ember",
              "lines": [{"text": "Block 2  ·  head 7", "size": 32, "wt": 600},
                        {"text": f"{ex27['on_date_digits_pct']}% on the date's six digits", "size": 24, "c": "ink"},
                        {"text": "at the step that writes the answer's first digit", "size": 20, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "tok44_top", "text": pc(ROWD[44]), "sub": "the 2 of 26", "accent": "ember", "mono": True,
              "t0": w("b8", "seventeen"), "t1": en("b8") + 0.4, "dx": -40, "dy": -150, "size": 28})
    E.append({"type": "tag", "anchor": "tok103_front", "text": "next: the first digit", "t0": w("b8", "write"), "t1": w("b8", "date"),
              "size": 22, "hl": "ember", "place": "tc", "dy": 10, "mono": False, "maxdepth": 30})
    # b9: join
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b9", "fourteen"), "t1": w("b9", "output") - 0.2, "accent": "v",
              "lines": [{"text": f"{CARD['heads']} × {CARD['head_dim']} = {CARD['d_model']}", "size": 34, "wt": 600},
                        {"text": "each head's output, side by side (block 24, real)", "size": 22, "c": "slate"}]})
    E.append({"type": "pin", "anchor": "wo_top", "text": "Output matrix", "sub": f"{CARD['d_model']} × {CARD['d_model']}, learned", "accent": "sky",
              "t0": w("b9", "output") + 0.2, "t1": w("b9", "added") - 0.2, "dx": 50, "dy": -60, "size": 28})
    E.append({"type": "pin", "anchor": "res2_top", "text": "Added to the column", "sub": "the last token's 896 numbers, updated (real)", "accent": "sky",
              "t0": w("b9", "added") + 0.7, "t1": en("b9") + 0.8, "dx": 70, "dy": -50, "size": 28})
    # b10
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b10", "fourteen"), "t1": en("b10") + 0.6, "accent": "sky",
              "lines": [{"text": f"{CARD['layers']} blocks × {CARD['heads']} heads = {CARD['layers'] * CARD['heads']}", "size": 34, "wt": 600},
                        {"text": "all of them in one pass", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b10") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "Heads: fourteen ways of looking",
              "sub": "Real heads of Qwen2.5-0.5B-Instruct on Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara",
                          "Every weight is from one recorded run (build/data/heads_data.json; the output matrix's pattern is decorative)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Observatory”, Out To The World (Epidemic Sound)"]})
    return E


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.28))
    S += [("beam.mp3", w("b1", "pattern") + 0.3, 0.3), ("rise.mp3", w("b2", "eight"), 0.3), ("tick.mp3", w("b2", "cut"), 0.4),
          ("merge.mp3", w("b2", "sixty-four"), 0.25), ("beam.mp3", w("b2", "each"), 0.3), ("chime.mp3", w("b3", "share"), 0.25),
          ("beam.mp3", w("b3", "seven"), 0.25), ("beam.mp3", w("b4", "nine"), 0.3), ("chime.mp3", w("b4", "eighty-four"), 0.25),
          ("beam.mp3", w("b5", "all"), 0.35), ("chime.mp3", w("b5", "rests"), 0.2), ("beam.mp3", w("b6", "place"), 0.3),
          ("chime.mp3", w("b6", "sixty-five"), 0.3), ("beam.mp3", w("b7", "reads"), 0.3), ("chime.mp3", w("b7", "thirty-six"), 0.25),
          ("tile.mp3", w("b8", "write"), 0.2), ("beam.mp3", w("b8", "two"), 0.3), ("chime.mp3", w("b8", "seventeen"), 0.3),
          ("rise.mp3", w("b9", "hands"), 0.3), ("merge.mp3", w("b9", "again") - 0.2, 0.35), ("fill.mp3", w("b9", "mixes"), 0.3),
          ("chime.mp3", w("b9", "added") + 0.5, 0.35), ("rise.mp3", w("b10", "fourteen") - 0.5, 0.35), ("fill.mp3", w("b10", "three"), 0.3),
          ("resolve.mp3", blk["b10"]["speech_end"] + 0.6, 0.45)]
    return S


def _poster():
    try:
        tl = json.load(open(os.path.join(HERE, "timeline", "heads.json")))
        return _w(tl)("b2", "each") + 2.5
    except Exception:
        return 25.0


POSTER = _poster()
