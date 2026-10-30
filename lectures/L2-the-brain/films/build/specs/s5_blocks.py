"""2D overlays + SFX for film s5, "A block, then 24 of them". The ladder = trace.json logit_lens.last (top token and
its probability after each block, at the last prompt position). Model sizes from trace.json model_card."""
import json
import os

from PIL import ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "brain3d", "trace.json")))
LENS = T["logit_lens"]["last"]
CARD = T["model_card"]
POSTER = 57.5
MUSIC = "tried_and_true_imprismed.mp3"
MUSIC_GAIN = 0.34  # one bed level for the whole L2 series
MUSIC_OFFSET = 80.0
CJK_URL = "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
_CJK = {}


def cjk(size):
    """Noto Sans SC for the Chinese tokens the lens shows (fetched once into /tmp in the composite container)."""
    if size in _CJK:
        return _CJK[size]
    p = "/tmp/NotoSansSC.ttf"
    try:
        if not os.path.exists(p):
            import urllib.request
            urllib.request.urlretrieve(CJK_URL, p)
        f = ImageFont.truetype(p, size)
        try:
            f.set_variation_by_axes([500])
        except Exception:
            pass
    except Exception:
        f = None
    _CJK[size] = f
    return f


def tok_text(s, n=16):
    s = s.replace("\n", "\\n")
    if len(s) > n:
        s = s[:n - 1] + "…"
    return s


def is_cjk(s):
    return any("㐀" <= ch <= "鿿" for ch in s)


def _w(tl):
    words = tl["words"]

    def w(b, text, nth=0, edge="s"):
        n = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        hs = [x for x in words if x["block"] == b and n(x["w"]) == n(text)] or \
             [x for x in words if x["block"] == b and n(x["w"]).startswith(n(text))]
        return hs[nth][edge]
    return w


_TL = {}


def floor_times(tl):
    """Seconds at which the column reaches block k (the same schedule as scenes/s5_blocks.py)."""
    w = _w(tl)
    F = {1: w("b2", "climbs"), 2: w("b2", "changing"), 3: w("b2", "floor")}
    f4, f17 = w("b4", "for"), w("b4", "languages")
    for k in range(4, 18):
        F[k] = f4 + (f17 - f4) * (k - 4) / 13
    F[18] = w("b4", "eighteen")
    F[19], F[20], F[21] = F[18] + 1.0, F[18] + 62 / 30, F[18] + 100 / 30
    F[22], F[23], F[24] = w("b4", "twenty-two"), w("b4", "twenty-nine"), w("b4", "fifty-six")
    return F


def elements(tl):
    _TL["tl"] = tl
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    st = lambda b: blk[b]["at"]  # noqa: E731
    en = lambda b: blk[b]["speech_end"]  # noqa: E731
    E = [{"type": "title", "kicker": "Lecture 2  ·  Section 5", "title": "A block, then 24 of them", "t0": 0.4, "t1": st("b1") + 3.0}]
    E.append({"type": "pin", "anchor": "bt_att1", "text": "Attention", "sub": f"{CARD['heads']} heads: gathers from other positions",
              "accent": "sky", "t0": w("b1", "half"), "t1": en("b1") + 0.4, "dx": -60, "dy": -150, "size": 30})
    E.append({"type": "pin", "anchor": "bt_mlp1", "text": "MLP", "sub": f"{CARD['d_model']} to {CARD['mlp_hidden']:,} to {CARD['d_model']} numbers, one column at a time",
              "accent": "v", "t0": w("b1", "other"), "t1": en("b1") + 0.4, "dx": 60, "dy": -150, "size": 30})
    E.append({"type": "pin", "anchor": "col_pin", "text": "The last position's column", "sub": f"{CARD['d_model']} numbers",
              "accent": "sky", "t0": w("b1", "column"), "t1": w("b1", "gathers") - 0.3, "dx": -60, "dy": -60, "size": 26})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b2", "stack"), "t1": en("b2") + 0.4, "accent": "sky",
              "lines": [{"text": f"{CARD['layers']} blocks = the model", "size": 32, "wt": 600},
                        {"text": f"{CARD['params']:,} weights in all", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b3", "take"), "t1": en("b3") + 0.5, "accent": "sky",
              "lines": [{"text": "The logit lens", "size": 32, "wt": 600},
                        {"text": "after block k: final norm, then the vocabulary scores", "size": 24, "c": "slate"},
                        {"text": "the top token = what it would say now", "size": 24, "c": "slate"}]})
    E.append({"type": "chip", "x": 96, "y": 130, "t0": w("b5", "answer"), "t1": en("b5") + 0.4, "accent": "sky",
              "lines": [{"text": f"After block 24: We  {LENS[23]['top'][0]['p'] * 100:.1f}%", "size": 32, "wt": 600, "mono": True},
                        {"text": "the model's own answer, condensed near the top", "size": 24, "c": "slate"}]})
    E.append({"type": "tag", "anchor": "we_front", "text": f"We  {LENS[23]['top'][0]['p'] * 100:.1f}%", "t0": w("b5", "condenses") + 0.5,
              "t1": en("b5") + 0.4, "size": 28, "hl": "sky", "place": "tc", "dy": 10, "maxdepth": 8})
    E.append({"type": "end", "t0": en("b5") + 0.8, "kicker": "Agentic Systems Engineering  ·  Lecture 2", "title": "A block, then 24 of them",
              "sub": "Qwen2.5-0.5B-Instruct, the logit lens at the last position of Emma's question",
              "credits": ["Dr. Rajat Dandekar  ·  Vizuara", "Every token and probability is from one recorded run (brain3d/trace.json)",
                          "Narration: ElevenLabs, voice Daniel  ·  Music: “Tried-And-True”, Imprismed (Epidemic Sound)"]})
    return E


def draw(cv, t, fr, P):
    """The logit-lens ladder: one row per block, filled as the column reaches it; the current row lit."""
    import overlay as O
    tl = _TL.get("tl")
    if tl is None:
        return
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    F = floor_times(tl)
    t_on = w("b3", "ask")
    t_off = blk["b5"]["speech_end"] + 0.5
    a = O.env(t, t_on - 0.2, t_off, 0.4, 0.4)
    if a <= 0:
        return
    shown = [k for k in range(1, 25) if (F[k] <= t if k > 3 else t_on + (k - 1) * 8 / 30 <= t)]
    if not shown:
        return
    cur = shown[-1]
    x0, y0, rw, rh = 1376, 1022 - 150 - 24 * 31, 470, 31
    from PIL import ImageDraw
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle((x0 - 18, y0 - 58, x0 + rw + 6, y0 + 24 * rh + 14), 16, fill=(14, 19, 28, int(205 * a)),
                        outline=(255, 255, 255, int(30 * a)))
    d.text((x0, y0 - 46), "After block k, it would say", font=O.font(22, 500), fill=(164, 176, 196, int(255 * a)))
    for k in range(24, 0, -1):     # block 24 at the top, block 1 at the bottom
        y = y0 + (24 - k) * rh
        if k not in shown:
            d.text((x0, y + 4), f"{k:>2}", font=O.font(20, 500, True), fill=(110, 120, 140, int(120 * a)))
            continue
        top = LENS[k - 1]["top"][0]
        txt, p = tok_text(top["text"]), top["p"]
        we = top["text"].strip().lower() == "we"
        lit = k == cur
        if lit:
            d.rounded_rectangle((x0 - 8, y, x0 + rw - 4, y + rh - 3), 8, fill=(60, 144, 255, int(70 * a)))
        col = (130, 190, 255) if we else (232, 238, 248)
        al = int(255 * a * (1.0 if (lit or we) else 0.72))
        d.text((x0, y + 4), f"{k:>2}", font=O.font(20, 600, True), fill=(164, 176, 196, al))
        f = cjk(21) if is_cjk(txt) else O.font(21, 600 if we else 500, True)
        f = f or O.font(21, 500, True)
        d.text((x0 + 48, y + 3), txt, font=f, fill=col + (al,))
        d.text((x0 + rw - 22, y + 4), f"{p * 100:5.1f}%", font=O.font(20, 600 if we else 500, True), fill=col + (al,), anchor="ra")


def sfx(tl):
    w = _w(tl)
    blk = {b["id"]: b for b in tl["blocks"]}
    F = floor_times(tl)
    S = [("bloom.mp3", 0.3, 0.5)]
    for b in ("b2", "b3", "b4", "b5"):
        S.append(("whoosh.mp3", blk[b]["at"] - 0.45, 0.32))
    S += [("rise.mp3", w("b1", "half") - 0.2, 0.3), ("rise.mp3", w("b1", "other"), 0.3), ("chime.mp3", w("b1", "gathers"), 0.25),
          ("fill.mp3", w("b1", "thinks"), 0.3)]
    for k in range(2, 25):
        S.append(("tile.mp3", blk["b2"]["at"] + 0.13 + (k - 2) * 2.6 / 30 + 0.6, 0.12))
    for k in (18, 22, 23, 24):
        S.append(("tick.mp3", F[k], 0.35))
    S += [("chime.mp3", F[24] + 0.1, 0.35), ("rise.mp3", w("b5", "condenses") - 0.3, 0.35),
          ("resolve.mp3", blk["b5"]["speech_end"] + 0.6, 0.45)]
    return S
