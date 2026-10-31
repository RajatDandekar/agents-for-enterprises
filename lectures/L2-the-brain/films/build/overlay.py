"""2D overlays for the Lecture 2 films (runs on Modal in the composite image): pinned labels, typed titles, number
punches, formula chips, subtitles and the end card, drawn with Pillow in Google Sans Flex over the rendered plate, then
the audio mix (narration + music bed ducked under the voice + SFX) and the deliverables (mp4, webm, poster jpg).

The per-film content is specs/<film>.py: elements(tl, proj) -> list of dicts, sfx(tl) -> list of cues, poster frame.
"""
import importlib
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
WH = (1920, 1080)
FONT_DIR = "/fonts"
INK = (244, 247, 252)
SUBINK = (74, 85, 104)
SKY = (60, 144, 255)
DEEP = (11, 87, 208)
EMBER = (196, 81, 31)
GREEN = (30, 142, 90)
QC, KC, VC = (60, 144, 255), (154, 92, 255), (255, 226, 170)
COLORS = {"sky": SKY, "deep": (120, 170, 255), "ember": EMBER, "green": GREEN, "q": (96, 165, 255), "k": (168, 128, 255), "v": (255, 226, 170), "ink": INK, "slate": (164, 176, 196)}

_fonts = {}


def font(size, wt=500, mono=False):
    k = (size, wt, mono)
    if k not in _fonts:
        fam = "GoogleSansCode" if mono else "GoogleSansFlex"
        wts = [400, 500, 600] if mono else [300, 400, 500, 600, 700]
        w = min(wts, key=lambda x: abs(x - wt))
        p = os.path.join(FONT_DIR, f"{fam}-{w}.ttf")
        if not os.path.exists(p):
            p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        _fonts[k] = ImageFont.truetype(p, size)
    return _fonts[k]


def col(c, a=255):
    c = COLORS.get(c, c) if isinstance(c, str) else c
    return (c[0], c[1], c[2], a)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def env(t, t0, t1, fin=0.35, fout=0.3):
    if t < t0 or t > t1 + fout:
        return 0.0
    if t > t1 and fout <= 0:
        return 0.0
    a = ease((t - t0) / fin) if fin > 0 else 1.0
    if t > t1:
        a *= 1 - ease((t - t1) / fout)
    return a


# ------------------------------------------------------------------------------------------------ sprites (cached)
_cache = {}


def _shadowed(img, radius=18, alpha=110, offset=(0, 6)):
    """Add a soft drop shadow under a card sprite (pads the sprite)."""
    pad = radius * 2
    W, H = img.size
    out = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: v * alpha // 255)
    sh = Image.new("RGBA", img.size, (12, 20, 40, 0))
    sh.putalpha(a)
    out.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    out = out.filter(ImageFilter.GaussianBlur(radius / 2))
    out.alpha_composite(img, (pad, pad))
    return out, pad


def card(lines, accent="sky", pad=(22, 14), radius=14, bg=(16, 21, 31, 222), bar=True, maxw=None):
    """lines: [(text, size, weight, color, mono)] -> RGBA sprite with soft shadow; returns (img, pad)."""
    key = ("card", json.dumps(lines), json.dumps(accent), pad, radius, bg, bar)
    if key in _cache:
        return _cache[key]
    ims = []
    for text, size, wt, c, mono in lines:
        f = font(size, wt, mono)
        bb = f.getbbox(text or " ")
        ims.append((text, f, bb, c, size))
    w = max(bb[2] for _, _, bb, _, _ in ims) + 2 * pad[0] + (8 if bar else 0)
    hs = [int(sz * 1.28) for *_, sz in ims]
    h = sum(hs) + 2 * pad[1] - int(ims[-1][4] * 0.12)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=bg, outline=(255, 255, 255, 34), width=1)
    x0 = pad[0]
    if bar:
        d.rounded_rectangle((10, pad[1] + 2, 14, h - pad[1] - 2), 2, fill=col(accent))
        x0 += 8
    y = pad[1]
    for (text, f, bb, c, size), hh in zip(ims, hs):
        d.text((x0, y - bb[1] + int(size * 0.12)), text, font=f, fill=col(c))
        y += hh
    res = _shadowed(img)
    _cache[key] = res
    return res


def text_sprite(text, size, wt=600, c="ink", halo=True, mono=False):
    key = ("txt", text, size, wt, json.dumps(c), halo, mono)
    if key in _cache:
        return _cache[key]
    f = font(size, wt, mono)
    bb = f.getbbox(text or " ")
    pad = int(size * 0.6)
    W, H = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if halo:
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(hl).text((pad - bb[0], pad - bb[1] + max(2, size // 20)), text, font=f, fill=(0, 4, 12, 170),
                                stroke_width=max(2, size // 12), stroke_fill=(0, 4, 12, 170))
        hl = hl.filter(ImageFilter.GaussianBlur(size / 7))
        img.alpha_composite(hl)
    ImageDraw.Draw(img).text((pad - bb[0], pad - bb[1]), text, font=f, fill=col(c))
    _cache[key] = (img, pad)
    return img, pad


def put(canvas, spr, x, y, a=1.0, anchor="tl"):
    """Paste sprite with its top-left (after its pad) at x, y, alpha a."""
    img, pad = spr
    if a <= 0.003:
        return
    W, H = img.size
    if anchor == "c":
        x, y = x - (W - 2 * pad) / 2, y - (H - 2 * pad) / 2
    elif anchor == "bc":
        x, y = x - (W - 2 * pad) / 2, y - (H - 2 * pad)
    elif anchor == "tc":
        x = x - (W - 2 * pad) / 2
    elif anchor == "tr":
        x = x - (W - 2 * pad)
    elif anchor == "lc":
        y = y - (H - 2 * pad) / 2
    elif anchor == "rc":
        x, y = x - (W - 2 * pad), y - (H - 2 * pad) / 2
    if a < 0.999:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v, a=a: int(v * a)))
    canvas.alpha_composite(img, (int(round(x - pad)), int(round(y - pad))))


def line(canvas, p0, p1, c=(232, 240, 255), a=0.7, width=2.0, dot=5.0):
    """Antialiased leader line with an anchor dot (drawn at 4x in a local patch)."""
    if a <= 0.003:
        return
    S = 4
    x0, y0 = min(p0[0], p1[0]) - dot - 4, min(p0[1], p1[1]) - dot - 4
    x1, y1 = max(p0[0], p1[0]) + dot + 4, max(p0[1], p1[1]) + dot + 4
    W, H = int(x1 - x0) + 1, int(y1 - y0) + 1
    if W <= 0 or H <= 0 or W > 4000 or H > 3000:
        return
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    al = int(255 * a)
    q = lambda p: ((p[0] - x0) * S, (p[1] - y0) * S)  # noqa: E731
    d.line([q(p0), q(p1)], fill=(c[0], c[1], c[2], al), width=int(width * S))
    cx, cy = q(p0)
    r = dot * S
    d.ellipse((cx - r - 2 * S, cy - r - 2 * S, cx + r + 2 * S, cy + r + 2 * S), fill=(10, 14, 22, int(al * 0.9)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(96, 165, 255, al))
    im = im.resize((W, H), Image.LANCZOS)
    canvas.alpha_composite(im, (int(x0), int(y0)))


# ------------------------------------------------------------------------------------------------ elements
class Proj:
    """Pin positions sampled every `step` frames (linear in between; no blending across a camera cut)."""

    def __init__(self, path):
        d = json.load(open(path))
        self.pins = d["pins"]
        self.step = d.get("step", 1)
        self.cams = d.get("cams", [])
        self.n = d["frames"]

    def at(self, name, fr):
        arr = self.pins.get(name)
        if not arr:
            return None
        s = self.step
        i = max(0, min(len(arr) - 1, fr // s))
        j = min(len(arr) - 1, i + 1)
        u = (fr - i * s) / s if j != i else 0.0
        if self.cams and j < len(self.cams) and self.cams[j] != self.cams[i]:
            u = 0.0
        a, b = arr[i], arr[j]
        if u > 0 and b[2] > 0 and a[2] > 0:
            x, y, z = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2]
        else:
            x, y, z = a
        if z <= 0:
            return None
        self.last_depth = z
        return x, y


def draw_title(cv, e, t):
    a = env(t, e["t0"], e["t1"], 0.25, 0.5)
    if a <= 0:
        return
    x, y = e.get("x", 96), e.get("y", 84)
    if e.get("kicker"):
        put(cv, text_sprite(e["kicker"], 26, 600, e.get("kc", "deep")), x, y, a * ease((t - e["t0"]) / 0.4))
    title = e["title"]
    n = len(title)
    k = int(min(n, max(0, (t - e["t0"] - 0.25) / e.get("speed", 0.045))))
    if k <= 0:
        return
    spr = text_sprite(title[:k], e.get("size", 64), 600, "ink")
    put(cv, spr, x, y + 40, a)
    if k < n and int(t * 4) % 2 == 0:  # caret
        img, pad = spr
        cx = x + img.size[0] - 2 * pad + 6
        ImageDraw.Draw(cv).rectangle((cx, y + 46, cx + 3, y + 46 + e.get("size", 64)), fill=(96, 165, 255, int(255 * a)))


def draw_pin(cv, e, t, fr, P):
    a = env(t, e["t0"], e["t1"], e.get("fin", 0.35), e.get("fout", 0.3))
    if a <= 0:
        return
    p = P.at(e["anchor"], fr)
    if p is None or not (-50 < p[0] < 1970 and -50 < p[1] < 1130):
        return
    dx, dy = e.get("dx", 60), e.get("dy", -90)
    lines = [(e["text"], e.get("size", 30), 600, e.get("ink", "ink"), e.get("mono", False))]
    if e.get("sub"):
        lines.append((e["sub"], e.get("subsize", 21), 400, "slate", False))
    spr = card(lines, accent=e.get("accent", "sky"))
    img, pad = spr
    cw, ch = img.size[0] - 2 * pad, img.size[1] - 2 * pad
    rise = (1 - ease((t - e["t0"]) / 0.35)) * 14 if e.get("fin", 0.35) > 0 else 0
    lx, ly = p[0] + dx, p[1] + dy + rise
    # card corner nearest the anchor
    ax = lx if dx >= 0 else lx - cw
    ay = ly - ch / 2
    ax = max(24, min(1920 - 24 - cw, ax))
    ay = max(24, min(1080 - 150 - ch, ay))
    ex = ax if dx >= 0 else ax + cw
    ey = ay + ch / 2
    if e.get("line", True):
        line(cv, p, (ex, ey), a=0.62 * a, dot=e.get("dot", 5.0))
    put(cv, spr, ax, ay, a)


def draw_tag(cv, e, t, fr, P):
    """A small token label directly above (or below) an anchor, no leader line."""
    a = env(t, e["t0"], e["t1"], 0.3, 0.3)
    if a <= 0:
        return
    p = P.at(e["anchor"], fr)
    if p is None or not (-80 < p[0] < 2000 and -80 < p[1] < 1160):
        return
    dep = getattr(P, "last_depth", 1.0)
    far = e.get("maxdepth", 3.2)
    if dep > far + 0.8:
        return
    a *= max(0.0, min(1.0, (far + 0.8 - dep) / 0.8))
    if e.get("scale_pin"):
        q = P.at(e["scale_pin"], fr)
        if q is None or 2.1 * math.hypot(p[0] - q[0], p[1] - q[1]) < e.get("min_px", 40):
            return
    size = e.get("size", 24)
    hl = e.get("hl")
    spr = card([(e["text"], size, 600 if hl else 500, "ink", e.get("mono", True))], accent=hl or "sky",
               pad=(12, 7), radius=10, bar=bool(hl), bg=(14, 19, 28, 228 if hl else 196))
    img, pad = spr
    w, h = img.size[0] - 2 * pad, img.size[1] - 2 * pad
    x, y = p[0] + e.get("dx", 0), p[1] + e.get("dy", -16)
    place = e.get("place", "bc")
    rect = (x - w / 2, y - h, x + w / 2, y) if place == "bc" else (x - w / 2, y, x + w / 2, y + h)
    if rect[0] < 4 or rect[2] > 1916 or rect[1] < 4 or rect[3] > 955 or not _free(rect):
        return
    _PLACED.append(rect)
    put(cv, spr, x, y, a, anchor=place)


_PLACED = []   # label rectangles placed this frame (tags and faces never overlap one another)


def _free(rect):
    x0, y0, x1, y1 = rect
    for a0, b0, a1, b1 in _PLACED:
        if x0 < a1 + 4 and a0 < x1 + 4 and y0 < b1 + 3 and b0 < y1 + 3:
            return False
    return True


def draw_face(cv, e, t, fr, P):
    """A token's word laid over its tile face: sized to the tile on screen (about 40-60 px tall for a hero tile),
    hidden when the tile is under ~40 px wide, when it would not fit, or when it would overlap another label.
    Never truncated."""
    a = env(t, e["t0"], e["t1"], 0.3, 0.3)
    if a <= 0:
        return
    p = P.at(e["anchor"], fr)
    if e.get("scale_pin"):
        q = P.at(e["scale_pin"], fr)
        if p is None or q is None:
            return
        tile_w = 2.1 * math.hypot(p[0] - q[0], p[1] - q[1])
    else:   # a fixed tile width on screen (px), for tiles that export only one pin
        if p is None:
            return
        tile_w = e.get("tile_px", 160)
    if tile_w < e.get("min_px", 40):
        return
    text = e["text"]
    glyph = e.get("glyph_font")
    f = ImageFont.truetype(glyph, 100) if glyph and os.path.exists(glyph) else font(100, 600, e.get("mono", False))
    w100 = max(1.0, f.getlength(text))
    size = min(e.get("max", 60), tile_w * 0.86 * 100 / w100, tile_w * 0.42)
    if size < e.get("min_size", 15):
        return
    size = int(size)
    key = ("face", text, size, glyph)
    if key not in _cache:
        ff = ImageFont.truetype(glyph, size) if glyph and os.path.exists(glyph) else font(size, 600, e.get("mono", False))
        bb = ff.getbbox(text)
        pad = max(6, size // 3)
        W, H = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - bb[0], pad - bb[1] + max(1, size // 18)), text, font=ff, fill=(0, 4, 12, 200))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(1, size / 14))))
        ImageDraw.Draw(img).text((pad - bb[0], pad - bb[1]), text, font=ff, fill=col(e.get("c", "ink")))
        _cache[key] = (img, pad)
    img, pad = _cache[key]
    w, h = img.size[0] - 2 * pad, img.size[1] - 2 * pad
    cx, cy = p[0] + e.get("dx", 0), p[1] + e.get("dy", 0)
    rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    if rect[0] < 4 or rect[2] > 1916 or rect[1] < 4 or rect[3] > 955 or not _free(rect):   # 955: keep clear of subtitles
        return
    _PLACED.append(rect)
    put(cv, _cache[key], cx, cy, a, anchor="c")


def draw_chip(cv, e, t):
    a = env(t, e["t0"], e["t1"])
    if a <= 0:
        return
    lines = []
    for ln in e["lines"]:
        if isinstance(ln, str):
            ln = {"text": ln}
        lines.append((ln["text"], ln.get("size", 30), ln.get("wt", 500), ln.get("c", "ink"), ln.get("mono", False)))
    spr = card(lines, accent=e.get("accent", "sky"), pad=(26, 18))
    rise = (1 - ease((t - e["t0"]) / 0.35)) * 16
    put(cv, spr, e["x"], e["y"] + rise, a, anchor=e.get("anchor", "tl"))


def draw_number(cv, e, t):
    a = env(t, e["t0"], e["t1"], 0.3, 0.35)
    if a <= 0:
        return
    v = e["value"]
    if e.get("count"):
        k = ease((t - e["t0"]) / e.get("count", 0.7))
        v = e["fmt"].format(e["from"] + (e["to"] - e["from"]) * k)
    big = text_sprite(v, e.get("size", 96), 650, e.get("c", "ink"))
    put(cv, big, e["x"], e["y"], a, anchor=e.get("anchor", "tl"))
    if e.get("label"):
        img, pad = big
        lab = text_sprite(e["label"], e.get("lsize", 28), 500, "slate")
        off = img.size[1] - 2 * pad + 6
        lx = e["x"] if e.get("anchor", "tl") == "tl" else e["x"] - (lab[0].size[0] - 2 * lab[1]) / 2
        put(cv, lab, lx, e["y"] + off, a)


def draw_sub(cv, cue, t):
    a = env(t, cue["t"] - 0.08, cue["end"] + 0.25, 0.18, 0.18)
    if a <= 0:
        return
    key = ("sub", cue["text"])
    if key not in _cache:
        f = font(33, 500)
        words, rows, cur = cue["text"].split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if f.getlength(trial) > 1380 and cur:
                rows.append(cur); cur = wd
            else:
                cur = trial
        rows.append(cur)
        W = int(max(f.getlength(r) for r in rows)) + 56
        H = 44 * len(rows) + 26
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, W - 1, H - 1), 16, fill=(11, 18, 32, 150))
        for i, r in enumerate(rows):
            d.text((W / 2, 13 + 44 * i + 22), r, font=f, fill=(255, 255, 255, 250), anchor="mm")
        _cache[key] = (img, 0)
    put(cv, _cache[key], 960, 1080 - 64, a, anchor="bc")


def draw_end(cv, e, t):
    a = env(t, e["t0"], 1e9, 0.6, 0)
    if a <= 0:
        return
    key = ("end", json.dumps(e))
    if key not in _cache:
        img = Image.new("RGBA", WH, (0, 0, 0, 0))
        g = np.zeros((1080, 1920, 4), np.uint8)
        yy = np.linspace(0, 1, 1080)[:, None]
        top, bot = np.array([22, 28, 42]), np.array([6, 8, 13])
        g[..., :3] = (top * (1 - yy[..., None]) + bot * yy[..., None]).astype(np.uint8)
        g[..., 3] = 255
        img = Image.fromarray(g, "RGBA")
        d = ImageDraw.Draw(img)
        d.text((960, 360), e.get("kicker", ""), font=font(30, 600), fill=col("deep"), anchor="mm")
        d.text((960, 440), e["title"], font=font(76, 600), fill=col("ink"), anchor="mm")
        d.text((960, 520), e.get("sub", ""), font=font(32, 400), fill=col("slate"), anchor="mm")
        y = 660
        for ln in e.get("credits", []):
            d.text((960, y), ln, font=font(24, 400), fill=col("slate"), anchor="mm")
            y += 38
        _cache[key] = (img, 0)
    put(cv, _cache[key], 0, 0, a)


_HOOK = {}


def frame_overlay(els, cues, t, fr, P):
    cv = Image.new("RGBA", WH, (0, 0, 0, 0))
    _PLACED.clear()
    if _HOOK.get("draw"):   # a film's own 2D drawing (specs/<film>.py: draw(cv, t, fr, P)), under the cards
        _HOOK["draw"](cv, t, fr, P)
    end = None
    for e in els:
        k = e["type"]
        if k == "end":
            end = e
            continue
        if t < e.get("t0", 0) - 0.1 or t > e.get("t1", 1e9) + 0.6:
            continue
        if k == "title":
            draw_title(cv, e, t)
        elif k == "pin":
            draw_pin(cv, e, t, fr, P)
        elif k == "tag":
            draw_tag(cv, e, t, fr, P)
        elif k == "face":
            draw_face(cv, e, t, fr, P)
        elif k == "chip":
            draw_chip(cv, e, t)
        elif k == "number":
            draw_number(cv, e, t)
    if end is None or t < end["t0"] + 0.6:
        for c in cues:
            if c["t"] - 0.2 <= t <= c["end"] + 0.6:
                draw_sub(cv, c, t)
    if end is not None:
        draw_end(cv, end, t)
    return cv


def load_spec(film):
    sys.path.insert(0, os.path.join(HERE, "specs"))
    mod = importlib.import_module(film)
    tl = json.load(open(os.path.join(HERE, "timeline", f"{film}.json")))
    _HOOK["draw"] = getattr(mod, "draw", None)
    return mod, tl


HERO_WORDS = {"battery", "packs", "Manchester", "stores", "\\n", "⏎", "We", "North", "bridge", "BAT", "-", ",",
              "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "100", "5,400"}
GLYPH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def autoface(els, P):
    """Series-wide label rule (Rajat, 30 Oct): a hero token's word is laid over its own tile face, sized to the tile
    (about 40-60 px tall); every other small token label is shown only when its tile is at least ~40 px wide on screen
    and it does not overlap another label; nothing is ever truncated."""
    out, faces = [], []
    for e in els:
        if e.get("type") == "tag" and isinstance(e.get("anchor"), str) and e["anchor"].endswith(("_front", "_top")):
            base = e["anchor"].rsplit("_", 1)[0]
            top, front = base + "_top", base + "_front"
            if top in P.pins and front in P.pins:
                word = e["text"].strip()
                if word in HERO_WORDS:
                    glyph = word in ("\\n", "⏎")
                    faces.append({"type": "face", "anchor": top, "scale_pin": front, "text": "⏎" if glyph else word,
                                  "t0": e["t0"], "t1": e["t1"], "c": "ink", "glyph_font": GLYPH if glyph else None, "max": 60})
                    continue
                e = dict(e, scale_pin=front)
        out.append(e)
    return faces + out   # faces first: they win the overlap test


def render_range(film, plate, proj_path, start, end, out):
    mod, tl = load_spec(film)
    P = Proj(proj_path)
    els = autoface(mod.elements(tl), P)
    cues = tl["cues"]
    n = end - start + 1
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{start / FPS:.4f}", "-i", plate, "-frames:v", str(n),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                            "-pix_fmt", "yuv420p", "-x264-params", "keyint=30", out], stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        fr = start + i
        raw = dec.stdout.read(1920 * 1080 * 3)
        if len(raw) < 1920 * 1080 * 3:
            raw = last  # past the plate's end (hold the last frame)
        last = raw
        base = Image.frombytes("RGB", WH, raw).convert("RGBA")
        ov = frame_overlay(els, cues, fr / FPS, fr, P)
        base.alpha_composite(ov)
        enc.stdin.write(base.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()
    dec.kill()


# ------------------------------------------------------------------------------------------------ audio + delivery
def _sh(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(" ".join(cmd[:8]) + "\n" + p.stderr[-3000:])
    return p


MUSIC_UNDER_DB = 26.0   # Rajat, 31 Oct: the bed sits clearly under the voice (~26 dB below it while Daniel speaks,
MUSIC_GAP_DB = 22.0     # ~22 dB below it in the gaps), the same L1 track ("Observatory") in every film


def _lufs(path):
    m = subprocess.run(["ffmpeg", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(json.loads(m[m.rindex("{"):m.rindex("}") + 1])["input_i"])


def _speech_windows(tl, merge=0.9, pre=0.15, post=0.3):
    ws = sorted((w["s"] - pre, w["e"] + post) for w in tl["words"])
    out = []
    for a, b in ws:
        if out and a - out[-1][1] < merge:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def mix_audio(film, tl, adir, out_wav, mod):
    total = tl["seconds"]
    SR = 48000
    # 1. the voice bus
    ins, filt, voice = [], [], []
    for k, b in enumerate(tl["blocks"]):
        ins += ["-i", os.path.join(adir, "narr", os.path.basename(b["audio"]))]
        ms = int(b["at"] * 1000)
        filt.append(f"[{k}]aresample={SR},aformat=channel_layouts=stereo,adelay={ms}|{ms}[n{k}]")
        voice.append(f"[n{k}]")
    filt.append("".join(voice) + f"amix=inputs={len(voice)}:normalize=0,apad=whole_dur={total:.2f},atrim=0:{total:.2f}[v]")
    vwav = out_wav + ".voice.wav"
    _sh(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[v]", "-ar", str(SR), vwav])
    Lv = _lufs(vwav)
    # 2. the music bed, levelled against the voice and shaped by the speech windows
    music = sorted(os.listdir(os.path.join(adir, "music"))) if os.path.isdir(os.path.join(adir, "music")) else []
    mpick = getattr(mod, "MUSIC", None)
    if mpick not in music:
        mpick = music[0] if music else None
    parts = [vwav]
    if mpick:
        off = getattr(mod, "MUSIC_OFFSET", 0.0)
        mraw = out_wav + ".music_raw.wav"
        _sh(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", os.path.join(adir, "music", mpick),
             "-af", f"atrim=start={off},asetpts=PTS-STARTPTS,atrim=0:{total:.2f},aresample={SR},aformat=channel_layouts=stereo,"
                    f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0.0, total - 3.5):.2f}:d=3.5", "-ar", str(SR), mraw])
        Lm = _lufs(mraw)
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mraw, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                             capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
        t = np.arange(len(x)) / SR
        g_sp = 10 ** (((Lv - MUSIC_UNDER_DB) - Lm) / 20)
        g_gap = 10 ** (((Lv - MUSIC_GAP_DB) - Lm) / 20)
        env = np.full(len(x), g_gap, np.float32)
        for a, b in _speech_windows(tl):
            env[(t >= a) & (t <= b)] = g_sp
        k = int(0.4 * SR)   # 0.4 s ramps
        env = np.convolve(env, np.ones(k, np.float32) / k, mode="same")
        x *= env[:, None]
        mwav = out_wav + ".music.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                        "-c:a", "pcm_s16le", mwav], input=x.astype(np.float32).tobytes(), check=True)
        parts.append(mwav)
    # 3. SFX, then everything together and two-pass loudnorm to -16 LUFS
    ins, filt, lbl = [], [], []
    for k, pth in enumerate(parts):
        ins += ["-i", pth]
        filt.append(f"[{k}]aresample={SR},aformat=channel_layouts=stereo[p{k}]")
        lbl.append(f"[p{k}]")
    n = len(parts)
    for k, (name, at, gain) in enumerate(mod.sfx(tl) if hasattr(mod, "sfx") else []):
        pth = os.path.join(adir, "sfx", name)
        if not os.path.exists(pth):
            continue
        ins += ["-i", pth]
        ms = max(0, int(at * 1000))
        filt.append(f"[{n}]aresample={SR},aformat=channel_layouts=stereo,volume={gain * 0.8:.3f},adelay={ms}|{ms}[x{k}]")
        lbl.append(f"[x{k}]")
        n += 1
    filt.append("".join(lbl) + f"amix=inputs={len(lbl)}:normalize=0,atrim=0:{total:.2f}[out]")
    rawmix = out_wav + ".raw.wav"
    _sh(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(filt), "-map", "[out]", "-ar", str(SR), rawmix])
    m = subprocess.run(["ffmpeg", "-i", rawmix, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-i", rawmix, "-af", ln, "-ar", str(SR), out_wav])
    return {"voice_lufs": Lv, "music_db_under_voice": MUSIC_UNDER_DB, "music_db_under_voice_gaps": MUSIC_GAP_DB}


def finish(film, parts, adir, outdir):
    mod, tl = load_spec(film)
    os.makedirs(outdir, exist_ok=True)
    with open("/tmp/parts.txt", "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    vid = f"/tmp/{film}_video.mp4"
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/parts.txt", "-c", "copy", vid])
    wav = f"/tmp/{film}.wav"
    mixinfo = mix_audio(film, tl, adir, wav, mod)
    total = tl["seconds"]
    # size budget: ~24 MB for the mp4
    vbr = int(min(4000, max(900, (24e6 * 8 / total - 160e3) / 1000)))
    mp4 = f"{outdir}/{film}.mp4"
    for pas in (1, 2):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", vid]
        if pas == 2:
            cmd += ["-i", wav]
        cmd += ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vbr}k", "-maxrate", f"{int(vbr * 1.8)}k", "-bufsize", f"{vbr * 4}k",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-pass", str(pas), "-passlogfile", f"/tmp/{film}_x264"]
        if pas == 1:
            cmd += ["-an", "-f", "mp4", "/dev/null"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{total:.3f}", mp4]
        _sh(cmd)
    webm = f"{outdir}/{film}.webm"
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libvpx-vp9",
         "-b:v", f"{vbr}k", "-deadline", "good", "-cpu-used", "3", "-row-mt", "1", "-c:a", "libopus", "-b:a", "128k",
         "-t", f"{total:.3f}", webm])
    jpg = f"{outdir}/{film}.jpg"
    pf = getattr(mod, "POSTER", total * 0.5)
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{pf:.2f}", "-i", vid, "-frames:v", "1", "-q:v", "3", jpg])
    loud = subprocess.run(["ffmpeg", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summ = [l.strip() for l in loud.splitlines()[-14:] if "I:" in l or "Peak:" in l or "LRA:" in l]
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip()
    return {"mp4": mp4, "webm": webm, "jpg": jpg, "seconds": dur, "video_kbps": vbr, "loudness": summ, "mix": mixinfo,
            "mp4_mb": round(os.path.getsize(mp4) / 1e6, 2), "webm_mb": round(os.path.getsize(webm) / 1e6, 2)}


def render_still(film, png, proj_path, frame):
    """One composited still (for style frames): the rendered PNG + this frame's overlays -> JPEG bytes."""
    import io
    mod, tl = load_spec(film)
    P = Proj(proj_path)
    base = Image.open(png).convert("RGBA").resize(WH)
    base.alpha_composite(frame_overlay(autoface(mod.elements(tl), P), tl["cues"], frame / FPS, frame, P))
    buf = io.BytesIO()
    base.convert("RGB").save(buf, "JPEG", quality=90)
    return buf.getvalue()
