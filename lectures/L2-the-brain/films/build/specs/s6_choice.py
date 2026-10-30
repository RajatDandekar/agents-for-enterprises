"""2D overlays + SFX for film s6, "From a vector to a choice". Logits and probabilities from trace.json
final.dial_last via kit/s6_sched.py (exact: p = exp(logit / T - logZ(T)), logZ over all 151,936 rows)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "kit"))
import s6_sched  # noqa: E402

T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
DIAL = T["final"]["dial_last"]
CARD = T["model_card"]
POSTER = 49.0
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 120.0
_S = {}


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


def elements(tl):
    _S["s"] = s6_sched.Sched(tl, DIAL)
    _S["tl"] = tl
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 6", "title": "From a vector to a choice", "t0": 0.4, "t1": st("b1") + 3.0}]
    E.append({"type": "pin", "anchor": "vec_top", "text": "The last column, after block 24", "sub": f"{CARD['d_model']} numbers",
              "accent": "sky", "t0": w("b1", "column"), "t1": en("b1") + 0.3, "dx": 70, "dy": -60, "size": 28})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "vocabulary"), "t1": w("b2", "logits") + 1.2, "accent": "sky",
              "lines": [{"text": f"The vocabulary table: {CARD['vocab']:,} rows", "size": 32, "wt": 600},
                        {"text": "one dot product with each row = one score (a logit)", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "softmax"), "t1": w("b3", "dial") - 0.4, "accent": "sky",
              "lines": [{"text": "Softmax", "size": 24, "c": "slate"}, {"text": "p = e^logit ÷ (sum of e^logit over all rows)", "size": 30, "wt": 600, "mono": True}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "dial"), "t1": en("b4") + 0.4, "accent": "sky",
              "lines": [{"text": "Temperature T", "size": 24, "c": "slate"}, {"text": "p = e^(logit ÷ T) ÷ (sum over all rows)", "size": 30, "wt": 600, "mono": True},
                        {"text": "T = 0: always the top token", "size": 24, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "we_front", "text": "We", "t0": w("b5", "we"), "t1": en("b5") + 0.4, "size": 34, "hl": "sky",
              "place": "tc", "dy": 12, "maxdepth": 8, "mono": False})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "drawn"), "t1": en("b5") + 0.4, "accent": "sky",
              "lines": [{"text": "One token, drawn", "size": 32, "wt": 600},
                        {"text": f"from {CARD['vocab']:,} rows of scores", "size": 24, "c": "slate"}]})
    E.append({"type": "end", "t0": en("b5") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "From a vector to a choice",
              "sub": "Qwen2.5-0.5B-Instruct, the next token after Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Logits and probabilities from one recorded run (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    """Live labels: each column's token and its logit or probability; the dial's current T."""
    import overlay as O
    S = _S.get("s")
    tl = _S.get("tl")
    if S is None:
        return
    blk = {b["id"]: b for b in tl["blocks"]}
    t_end = blk["b5"]["speech_end"] + 0.6
    if t > t_end + 0.3:
        return
    a_all = 1.0 - O.ease((t - t_end) / 0.3) if t > t_end else 1.0
    mode, lv, nums = S.levels(fr)
    if mode != "off":
        a = a_all * O.ease((fr - (S.f_logit - 10)) / 18)
        for j, tk in enumerate(S.top):
            base = P.at(f"m{j}", fr)
            if base:
                spr = O.card([(tk["text"], 26, 600, "ink", False)], accent="sky", pad=(12, 6), radius=10, bar=j == 0)
                O.put(cv, spr, base[0], base[1] + 14, a, anchor="tc")
            top = P.at(f"m{j}_top", fr)
            if top and nums:
                txt = f"{nums[j]:.2f}" if mode == "logit" else f"{nums[j] * 100:.1f}%"
                spr = O.text_sprite(txt, 30 if j == 0 else 26, 600, (130, 190, 255) if j == 0 else "ink", True, True)
                O.put(cv, spr, top[0], top[1] - 10, a, anchor="bc")
    if fr >= S.f_dial - 12:
        a = a_all * O.ease((fr - S.f_dial + 12) / 18)
        Tn = S.T(fr)
        p = P.at("dial_top", fr)
        if p:
            spr = O.card([(f"T = {Tn:.2f}", 34, 600, "ink", True)], accent="sky", pad=(16, 10), radius=12)
            O.put(cv, spr, p[0], p[1] - 16, a, anchor="bc")
        for nm, lab in (("dial_t0", "0"), ("dial_t07", "0.7"), ("dial_t12", "1.2")):
            q = P.at(nm, fr)
            if q:
                O.put(cv, O.text_sprite(lab, 20, 600, "slate", True, True), q[0], q[1], a, anchor="c")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.32))
    S += [("rise.mp3", w("b1", "column") - 0.4, 0.35), ("beam.mp3", w("b2", "every") - 0.1, 0.45), ("fill.mp3", w("b2", "score") - 0.2, 0.4),
          ("fill.mp3", w("b3", "probabilities") - 0.1, 0.4), ("tile.mp3", w("b3", "dial"), 0.4),
          ("tick.mp3", w("b4", "zero"), 0.35), ("tick.mp3", w("b4", "seven"), 0.35), ("tick.mp3", w("b4", "two"), 0.35),
          ("rise.mp3", w("b5", "drawn") - 0.3, 0.4), ("chime.mp3", w("b5", "we"), 0.4), ("resolve.mp3", blk["b5"]["speech_end"] + 0.6, 0.45)]
    return S
