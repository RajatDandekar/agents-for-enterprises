"""Frame compositor for the L1 film (runs on Modal; PIL + numpy).

For a global frame g: pick the shot plate(s) (crossfade XF frames at each cut), then draw
every overlay element active at g. Elements come from overlays.build(); 2D anchor positions
per local frame come from proj/<shot>.json exported by Blender.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "GoogleSansFlex.ttf")
MONO = os.path.join(HERE, "fonts", "GoogleSansCode.ttf")
W, H = 1920, 1080
ACC = {"sky": (60, 144, 255), "ember": (226, 104, 52), "green": (52, 190, 120)}
INK = (14, 18, 26)
_fc = {}


def font(size, wght=500, mono=False):
    k = (size, wght, mono)
    if k not in _fc:
        f = ImageFont.truetype(MONO if mono else FONT, size)
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                nm = a.get("name", b"")
                nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                if "eight" in nm or nm.lower().startswith("wght"):
                    vals.append(wght)
                elif "ptical" in nm or nm.lower().startswith("opsz"):
                    vals.append(min(max(size * 0.75, a["minimum"]), a["maximum"]))
                else:
                    vals.append(a.get("default", a["minimum"]))
            f.set_variation_by_axes(vals)
        except Exception:
            pass
        _fc[k] = f
    return _fc[k]


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def env(g, f0, f1, rise=14, fall=10):
    """0..1 visibility with eased rise and fade."""
    if g < f0 or g >= f1:
        return 0.0
    return min(ease((g - f0) / rise), ease((f1 - g) / fall))


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    out = []
    for para in s.split("\n"):
        line = ""
        for word in para.split(" "):
            t = (line + " " + word).strip()
            if text_w(d, t, f) > maxw and line:
                out.append(line)
                line = word
            else:
                line = t
        out.append(line)
    return out


class Layer:
    """An element drawn on its own RGBA canvas, then composited with alpha, rise and blur."""

    def __init__(self, w=W, h=H):
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)


def glass(d, box, r=16, fill=(12, 16, 24, 205), outline=(255, 255, 255, 38)):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=1)


def shadow_of(im, radius=18, alpha=0.45, dy=10):
    a = im.split()[-1].filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(a)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, dy))
    return out


def put(base, layer, k, dy=26, blur=6, shadow=True):
    """Composite a layer with envelope k (0..1): rises dy px and unblurs as it appears."""
    if k <= 0.001:
        return
    im = layer.im
    if shadow:
        sh = shadow_of(im)
        im2 = Image.new("RGBA", im.size, (0, 0, 0, 0))
        im2.alpha_composite(sh)
        im2.alpha_composite(im)
        im = im2
    if k < 0.999:
        b = blur * (1 - k)
        if b > 0.3:
            im = im.filter(ImageFilter.GaussianBlur(b))
        a = im.split()[-1].point(lambda v: int(v * k))
        im.putalpha(a)
    off = int(round(dy * (1 - k)))
    base.alpha_composite(im, (0, off))


# ------------------------------------------------------------------ elements
def draw_title(base, e, g):
    k = env(g, e["f0"], e["f1"], 10, 18)
    if not k:
        return
    L = Layer()
    d = L.d
    # soft vignette behind the title for legibility
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(vg).ellipse((260, 300, 1660, 820), fill=(8, 12, 20, 150))
    vg = vg.filter(ImageFilter.GaussianBlur(90))
    L.im.alpha_composite(vg)
    fk, fh, fs = font(24, 600), font(84, 650), font(34, 400)
    d.text((W / 2, 400), e["kicker"], font=fk, fill=(170, 205, 255, 255), anchor="mm")
    n = len(e["h"])
    typed = int(n * min(1.0, max(0.0, (g - e["f0"] - 4) / 34)))
    s = e["h"][:typed]
    tw = text_w(d, e["h"], fh)
    x0 = W / 2 - tw / 2
    d.text((x0, 500), s, font=fh, fill=(255, 255, 255, 255), anchor="lm")
    if typed < n or (g // 8) % 2 == 0:
        cx = x0 + text_w(d, s, fh) + 6
        d.rectangle((cx, 462, cx + 5, 538), fill=(120, 175, 255, 255))
    ks = ease((g - e["f0"] - 40) / 14)
    if ks > 0:
        d.text((W / 2, 590), e["sub"], font=fs, fill=(220, 228, 240, int(255 * ks)), anchor="mm")
    put(base, L, k, dy=0, blur=0, shadow=False)


def draw_sub(base, e, g):
    k = env(g, e["f0"], e["f1"], 5, 5)
    if not k:
        return
    L = Layer()
    d = L.d
    f = font(38, 500)
    lines = wrap(d, e["text"], f, 1500)
    lh = 50
    y1 = H - 58
    y0 = y1 - lh * len(lines)
    wmax = max(text_w(d, ln, f) for ln in lines)
    d.rounded_rectangle((W / 2 - wmax / 2 - 22, y0 - 12, W / 2 + wmax / 2 + 22, y1 + 6), 12, fill=(6, 9, 14, 150))
    for i, ln in enumerate(lines):
        d.text((W / 2, y0 + lh * i + lh / 2 - 2), ln, font=f, fill=(255, 255, 255, 255), anchor="mm")
    put(base, L, k, dy=0, blur=0, shadow=False)


def card_header(d, x, y, w, title, accent):
    d.rounded_rectangle((x + 18, y + 18, x + 22, y + 44), 2, fill=ACC[accent] + (255,))
    d.text((x + 34, y + 31), title, font=font(24, 600), fill=(205, 214, 228, 255), anchor="lm")


def draw_chip(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    fh, fs = font(34, 620), font(25, 420)
    w = max(text_w(d, e["h"], fh), text_w(d, e.get("sub", ""), fs)) + 66
    x, y = e["x"], e["y"]
    h = 104 if e.get("sub") else 70
    glass(d, (x, y, x + w, y + h))
    d.rounded_rectangle((x + 18, y + 20, x + 23, y + h - 20), 2, fill=ACC[e["accent"]] + (255,))
    d.text((x + 40, y + 36), e["h"], font=fh, fill=(255, 255, 255, 255), anchor="lm")
    if e.get("sub"):
        d.text((x + 40, y + 74), e["sub"], font=fs, fill=(178, 190, 208, 255), anchor="lm")
    put(base, L, k)


def draw_punch(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k or e.get("hide"):
        return
    L = Layer()
    d = L.d
    fv, fl = font(118 if not e.get("small") else 90, 700), font(30, 450)
    vw = text_w(d, e["value"], fv)
    lw = text_w(d, e["label"], fl)
    w = max(vw, lw) + 80
    x = e["x"] if e.get("left") else e["x"] - w / 2
    x = min(max(40, x), W - 40 - w)
    y = e["y"] - 110
    glass(d, (x, y, x + w, y + 196), 22)
    d.rounded_rectangle((x + 26, y + 26, x + 32, y + 170), 3, fill=ACC[e["accent"]] + (255,))
    # the number lands with a small scale-free count of opacity per character
    d.text((x + 52, y + 84), e["value"], font=fv, fill=(255, 255, 255, 255), anchor="lm")
    d.text((x + 54, y + 160), e["label"], font=fl, fill=ACC[e["accent"]] + (255,) if e["accent"] != "sky" else (150, 195, 255, 255), anchor="lm")
    put(base, L, k, dy=30, blur=8)


def code_colours(line):
    """Very small JSON-ish highlighter: returns [(text, rgb)]."""
    out, i = [], 0
    import re
    for m in re.finditer(r'"[^"]*"|\btrue\b|\bfalse\b|-?\d[\d,\.]*|£[\d,]+', line):
        if m.start() > i:
            out.append((line[i:m.start()], (205, 214, 228)))
        t = m.group(0)
        if t.startswith('"'):
            nxt = line[m.end():m.end() + 1]
            out.append((t, (140, 190, 255) if nxt == ":" else (120, 220, 160)))
        elif t in ("false",):
            out.append((t, (240, 130, 90)))
        elif t in ("true",):
            out.append((t, (120, 220, 160)))
        else:
            out.append((t, (255, 200, 110)))
        i = m.end()
    out.append((line[i:], (205, 214, 228)))
    return out


def draw_code(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    fm = font(28, 450, mono=True)
    lines = e["lines"]
    w = max(text_w(d, ln, fm) for ln in lines) + 90 + (40 if e.get("checks") else 0)
    w = max(w, text_w(d, e["title"], font(24, 600)) + 80)
    lh = 42
    x, y = e["x"], e["y"]
    x = min(x, W - 40 - w)
    h = 70 + lh * len(lines) + 18
    glass(d, (x, y, x + w, y + h), 16, fill=(10, 13, 20, 218))
    card_header(d, x, y, w, e["title"], e["accent"])
    total = sum(len(l) for l in lines)
    shown = total
    if e.get("typed"):
        shown = int(total * min(1.0, max(0.0, (g - e["f0"]) / 30)))
    acc = 0
    for i, ln in enumerate(lines):
        cx = x + 34
        cy = y + 76 + i * lh + lh / 2
        visible = max(0, min(len(ln), shown - acc))
        acc += len(ln)
        n = 0
        for seg, col in code_colours(ln):
            if n >= visible:
                break
            s = seg[:visible - n]
            d.text((cx, cy), s, font=fm, fill=col + (255,), anchor="lm")
            cx += text_w(d, s, fm)
            n += len(seg)
        if e.get("checks") and i < len(e["checks"]) and g >= e["checks"][i]:
            kk = ease((g - e["checks"][i]) / 8)
            px = x + w - 46
            d.ellipse((px - 14, cy - 14, px + 14, cy + 14), fill=ACC["green"] + (int(255 * kk),))
            d.line((px - 7, cy, px - 2, cy + 6, px + 8, cy - 6), fill=(255, 255, 255, int(255 * kk)), width=4)
    put(base, L, k)


def anchor_at(proj, shot_r0, name, g):
    fr = proj.get(str(g - shot_r0))
    if fr is None:
        keys = sorted(int(x) for x in proj.keys())
        fr = proj[str(min(max(g - shot_r0, keys[0]), keys[-1]))]
    return fr.get(name)


def draw_pin(base, e, g, ctx):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    p = anchor_at(ctx["proj"][e["shot"]], ctx["r0"][e["shot"]], e["anchor"], g)
    if not p or p[2] <= 0:
        return
    ax, ay = p[0], p[1]
    L = Layer()
    d = L.d
    small = e.get("small")
    fh, fs = font(30 if small else 36, 620), font(25, 420)
    tw = max(text_w(d, e["h"], fh), text_w(d, e.get("sub", ""), fs) if e.get("sub") else 0) + 56
    th = 62 if not e.get("sub") else 100
    if small:
        th = 54
    lx, ly = ax + e.get("dx", 0), ay + e.get("dy", 0)
    lx = min(max(30, lx - (tw / 2 if e.get("dx", 0) == 0 else 0)), W - 30 - tw)
    ly = min(max(30, ly - th / 2), H - 170 - th)
    # leader: from anchor to the nearest edge of the label
    ex = min(max(ax, lx), lx + tw)
    ey = ly + th if ay > ly + th else (ly if ay < ly else ay)
    grow = ease((g - e["f0"]) / 10)
    d.line((ax, ay, ax + (ex - ax) * grow, ay + (ey - ay) * grow), fill=(255, 255, 255, 220), width=2)
    d.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), fill=(255, 255, 255, 235))
    d.ellipse((ax - 5, ay - 5, ax + 5, ay + 5), fill=ACC[e["accent"]] + (255,))
    if grow > 0.6:
        glass(d, (lx, ly, lx + tw, ly + th), 14)
        d.rounded_rectangle((lx + 14, ly + 16, lx + 18, ly + th - 16), 2, fill=ACC[e["accent"]] + (255,))
        d.text((lx + 32, ly + (th / 2 if not e.get("sub") or small else 34)), e["h"], font=fh, fill=(255, 255, 255, 255), anchor="lm")
        if e.get("sub") and not small:
            d.text((lx + 32, ly + 72), e["sub"], font=fs, fill=(178, 190, 208, 255), anchor="lm")
    put(base, L, k, dy=0, blur=4)


def draw_ledger(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    x, y, w = e["x"], e["y"], 560
    rows = e["rows"]
    h = 80 + 92 * len(rows) + 110
    glass(d, (x, y, x + w, y + h), 18)
    card_header(d, x, y, w, e["title"], e["accent"])
    for i, (a, b, n, f) in enumerate(rows):
        kk = ease((g - f) / 10)
        if kk <= 0:
            continue
        yy = y + 80 + i * 92
        al = int(255 * kk)
        d.text((x + 34, yy + 26), a, font=font(32, 600), fill=(255, 255, 255, al), anchor="lm")
        d.text((x + 34, yy + 62), b, font=font(24, 420), fill=(170, 182, 200, al), anchor="lm")
        d.text((x + w - 34, yy + 40), n, font=font(40, 650), fill=(150, 195, 255, al), anchor="rm")
    tv, tl, tf = e["total"]
    kk = ease((g - tf) / 10)
    yy = y + 80 + len(rows) * 92
    d.line((x + 30, yy + 8, x + w - 30, yy + 8), fill=(255, 255, 255, 90), width=2)
    if kk > 0:
        al = int(255 * kk)
        d.text((x + 34, yy + 56), "= one request", font=font(32, 600), fill=(255, 255, 255, al), anchor="lm")
        d.text((x + w - 34, yy + 56), f"{tv} {tl}", font=font(44, 700), fill=(255, 255, 255, al), anchor="rm")
    put(base, L, k)


def draw_tools(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    x, y, w = e["x"], e["y"], 440
    n = len(e["tools"])
    lh = 37
    h = 76 + n * lh + 16
    glass(d, (x, y, x + w, y + h), 16)
    card_header(d, x, y, w, "15 tools it may call", e["accent"])
    pk = ease((g - e["f_pick"]) / 10)
    for i, t in enumerate(e["tools"]):
        yy = y + 76 + i * lh + lh / 2
        chosen = t == e["pick"]
        if chosen and pk > 0:
            d.rounded_rectangle((x + 16, yy - 19, x + w - 16, yy + 19), 10, fill=ACC["sky"] + (int(235 * pk),))
        dim = 1.0 if (chosen or pk == 0) else (1 - 0.6 * pk)
        col = (255, 255, 255) if chosen and pk > 0.5 else (205, 214, 228)
        d.text((x + 34, yy), t, font=font(27, 600 if chosen else 430, mono=True), fill=col + (int(255 * dim),), anchor="lm")
    put(base, L, k)


def draw_laps(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    x, y, w = e["x"], e["y"], 700
    lh = 84
    h = 80 + lh * len(e["laps"]) + 10
    glass(d, (x, y, x + w, y + h), 18)
    card_header(d, x, y, w, e["title"], "sky")
    for i, (n, tool, res, f, tok) in enumerate(e["laps"]):
        kk = ease((g - f) / 10)
        if kk <= 0:
            continue
        al = int(255 * kk)
        yy = y + 80 + i * lh
        d.ellipse((x + 28, yy + 14, x + 62, yy + 48), fill=ACC["sky"] + (al,))
        d.text((x + 45, yy + 31), n, font=font(22, 700), fill=(255, 255, 255, al), anchor="mm")
        d.text((x + 80, yy + 26), tool, font=font(28, 600, mono=True), fill=(255, 255, 255, al), anchor="lm")
        d.text((x + 80, yy + 60), res, font=font(24, 420), fill=(150, 225, 175, al) if "no " not in res else (240, 150, 110, al), anchor="lm")
        d.text((x + w - 30, yy + 31), tok + " tokens", font=font(24, 500), fill=(150, 195, 255, al), anchor="rm")
    put(base, L, k)


def draw_bubble(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    f = font(32, 450)
    lines = wrap(d, e["text"], f, 760)
    x, y = e["x"], e["y"]
    w = max(text_w(d, ln, f) for ln in lines) + 64
    w = max(w, 300)
    h = 70 + 44 * len(lines) + 20
    bot = e.get("bot")
    fill = (255, 255, 255, 240) if bot else (11, 87, 208, 240)
    d.rounded_rectangle((x, y, x + w, y + h), 24, fill=fill)
    d.text((x + 32, y + 36), e["who"], font=font(24, 650), fill=(11, 87, 208, 255) if bot else (200, 222, 255, 255), anchor="lm")
    for i, ln in enumerate(lines):
        d.text((x + 32, y + 80 + 44 * i), ln, font=f, fill=INK + (255,) if bot else (255, 255, 255, 255), anchor="lm")
    put(base, L, k)


def draw_bigline(base, e, g):
    k = env(g, e["f0"], e["f1"])
    if not k:
        return
    L = Layer()
    d = L.d
    f = font(64, 650)
    parts = e["parts"]
    full = "  ".join(p for p, _ in parts)
    tw = text_w(d, full, f)
    x = W / 2 - tw / 2
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(vg).rounded_rectangle((x - 40, e["y"] - 60, x + tw + 40, e["y"] + 60), 30, fill=(8, 12, 20, 120))
    L.im.alpha_composite(vg.filter(ImageFilter.GaussianBlur(24)))
    for p, f0 in parts:
        kk = ease((g - f0) / 10)
        d.text((x, e["y"]), p, font=f, fill=(255, 255, 255, int(255 * kk)), anchor="lm")
        x += text_w(d, p + "  ", f)
    put(base, L, k, dy=0, blur=0)


def draw_end(base, e, g, ctx):
    k = env(g, e["f0"], e["f1"] + 30, 24, 10)
    if not k:
        return
    # darken and blur the plate underneath
    bl = base.filter(ImageFilter.GaussianBlur(14 * k))
    dark = Image.new("RGBA", (W, H), (8, 11, 18, int(190 * k)))
    bl.alpha_composite(dark)
    base.paste(bl)
    L = Layer()
    d = L.d
    d.text((W / 2, 420), e["h"], font=font(80, 680), fill=(255, 255, 255, 255), anchor="mm")
    d.text((W / 2, 510), e["sub"], font=font(28, 430), fill=(185, 200, 222, 255), anchor="mm")
    for i, c in enumerate(e["credits"]):
        kk = ease((g - e["f0"] - 20 - i * 6) / 14)
        d.text((W / 2, 760 + i * 46), c, font=font(26 if i else 30, 600 if i == 0 else 420),
               fill=(255, 255, 255, int(255 * kk)) if i == 0 else (165, 178, 198, int(255 * kk)), anchor="mm")
    put(base, L, ease((g - e["f0"]) / 20), dy=20, blur=6, shadow=False)


# ------------------------------------------------------------------ chat UI on Emma's screen
UI_W, UI_H = 1600, 906


def chat_ui(state, g):
    im = Image.new("RGB", (UI_W, UI_H), (247, 249, 252))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, UI_W, 96), fill=(255, 255, 255))
    d.line((0, 96, UI_W, 96), fill=(226, 231, 238), width=2)
    d.ellipse((36, 26, 80, 70), fill=(11, 87, 208))
    d.text((58, 48), "N", font=font(26, 700), fill=(255, 255, 255), anchor="mm")
    d.text((100, 48), "Ask Northbridge", font=font(34, 650), fill=INK, anchor="lm")
    d.text((UI_W - 40, 48), "Northbridge Cycles  ·  Emma Clarke", font=font(26, 450), fill=(110, 120, 135), anchor="rm")
    # messages, bottom-aligned above the input box
    fb = font(34, 450)
    blocks = []
    for who, txt in state["msgs"]:
        maxw = 1000 if who == "user" else 1250
        lines = wrap(d, txt, fb, maxw)
        h = 44 * len(lines) + 44
        blocks.append((who, lines, h))
    if state.get("thinking"):
        blocks.append(("dots", [], 84))
    y = UI_H - 150
    for who, lines, h in reversed(blocks):
        y -= h + 22
        if y < 110:
            break
        if who == "dots":
            d.rounded_rectangle((60, y, 220, y + h), 30, fill=(255, 255, 255), outline=(226, 231, 238), width=2)
            for i in range(3):
                ph = (math.sin(g * 0.25 - i * 0.9) + 1) / 2
                c = int(150 + 80 * (1 - ph))
                d.ellipse((96 + i * 36, y + 32, 116 + i * 36, y + 52), fill=(c, c + 10, 255 if ph > 0.5 else c + 30))
            continue
        w = max(d.textlength(ln, font=fb) for ln in lines) + 60
        if who == "user":
            x0 = UI_W - 60 - w
            d.rounded_rectangle((x0, y, UI_W - 60, y + h), 30, fill=(11, 87, 208))
            col = (255, 255, 255)
        else:
            x0 = 60
            d.rounded_rectangle((x0, y, x0 + w, y + h), 30, fill=(255, 255, 255), outline=(226, 231, 238), width=2)
            col = INK
        for i, ln in enumerate(lines):
            d.text((x0 + 30, y + 22 + 44 * i + 22), ln, font=fb, fill=col, anchor="lm")
    # input box
    d.rounded_rectangle((60, UI_H - 120, UI_W - 60, UI_H - 36), 42, fill=(255, 255, 255), outline=(200, 210, 225), width=3)
    typed = state.get("typing", "")
    if typed and state.get("type_to"):
        n = len(typed)
        span = max(1, state["type_to"] - state["f"])
        typed = typed[:int(n * min(1.0, (g - state["f"]) / span))]
    if typed:
        d.text((100, UI_H - 78), typed, font=fb, fill=INK, anchor="lm")
        cx = 100 + d.textlength(typed, font=fb) + 4
    else:
        d.text((100, UI_H - 78), "Ask about stock, suppliers, orders…", font=fb, fill=(160, 168, 180), anchor="lm")
        cx = 100
    if (g // 8) % 2 == 0:
        d.rectangle((cx, UI_H - 100, cx + 3, UI_H - 56), fill=(11, 87, 208))
    d.ellipse((UI_W - 134, UI_H - 112, UI_W - 68, UI_H - 46), fill=(11, 87, 208))
    d.polygon([(UI_W - 112, UI_H - 92), (UI_W - 84, UI_H - 79), (UI_W - 112, UI_H - 66)], fill=(255, 255, 255))
    return im


def persp_coeffs(src, dst):
    """Coefficients for PIL PERSPECTIVE mapping dst (output) points to src points."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def draw_chat(base, e, g, ctx):
    if not (e["f0"] <= g < e["f1"]):
        return
    st = [s for s in e["states"] if g - ctx["r0"][e["shot"]] >= s["f"] or g >= s["f"] + 0 and s["f"] > 1000]
    # state frames are GLOBAL except the first (0)
    st = [s for s in e["states"] if (s["f"] == 0) or g >= s["f"]]
    state = st[-1]
    ui = chat_ui(state, g)
    proj, r0 = ctx["proj"][e["shot"]], ctx["r0"][e["shot"]]
    q = [anchor_at(proj, r0, n, g) for n in ("scr_tl", "scr_tr", "scr_br", "scr_bl")]
    if any(p is None or p[2] <= 0 for p in q):
        return
    # supersample x2 for a crisp warp
    S = 2
    dst = [(p[0] * S, p[1] * S) for p in q]
    src = [(0, 0), (UI_W, 0), (UI_W, UI_H), (0, UI_H)]
    co = persp_coeffs(src, dst)
    big = ui.convert("RGBA").transform((W * S, H * S), Image.PERSPECTIVE, co, Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    mask = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(mask).polygon(dst, fill=255)
    big.putalpha(mask)
    warped = big.resize((W, H), Image.LANCZOS)
    # glass: a faint top-left sheen, slight transparency so the render's reflections show
    a = warped.split()[-1].point(lambda v: int(v * 0.97))
    warped.putalpha(a)
    base.alpha_composite(warped)


def draw_stamp(base, e, g):
    if not (e["f0"] <= g < e["f1"]):
        return
    k = env(g, e["f0"], e["f1"], 4, 10)
    sc = 1.0 + 0.5 * (1 - ease((g - e["f0"]) / 6))
    w, h = 560, 190
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = ACC["ember"]
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, fill=(30, 10, 4, 170), outline=col + (255,), width=7)
    d.text((20 + w / 2, 20 + 82), e["h"], font=font(92, 800), fill=col + (255,), anchor="mm")
    d.text((20 + w / 2, 20 + 156), e["sub"], font=font(28, 500), fill=(255, 220, 200, 255), anchor="mm")
    im = im.rotate(-6, resample=Image.BICUBIC, expand=True)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    a = im.split()[-1].point(lambda v: int(v * k))
    im.putalpha(a)
    base.alpha_composite(im, (int(e["x"] - im.width / 2), int(e["y"] - im.height / 2)))


def draw_ripple(base, e, g, ctx):
    if not (e["f0"] <= g < e["f1"]):
        return
    p = anchor_at(ctx["proj"][e["shot"]], ctx["r0"][e["shot"]], e["anchor"], g)
    if not p or p[2] <= 0:
        return
    L = Layer()
    t = (g - e["f0"]) / (e["f1"] - e["f0"])
    for j in range(2):
        tt = t - j * 0.25
        if 0 < tt < 1:
            r = 30 + 260 * ease(tt)
            a = int(200 * (1 - tt))
            L.d.ellipse((p[0] - r, p[1] - r * 0.45, p[0] + r, p[1] + r * 0.45), outline=ACC["sky"] + (a,), width=4)
    base.alpha_composite(L.im)


DRAW = {"title": draw_title, "stamp": draw_stamp, "sub": draw_sub, "chip": draw_chip, "punch": draw_punch, "code": draw_code,
        "ledger": draw_ledger, "tools": draw_tools, "laps": draw_laps, "bubble": draw_bubble, "bigline": draw_bigline}
CTX_DRAW = {"pin": draw_pin, "chat": draw_chat, "end": draw_end, "ripple": draw_ripple}
ORDER = ["chat", "ripple", "pin", "chip", "ledger", "tools", "laps", "code", "bubble", "punch", "stamp", "bigline", "title", "end", "sub"]


def compose(g, plate_for, elements, ctx):
    """plate_for(g) -> RGBA base image (already crossfaded)."""
    base = plate_for(g)
    for kind in ORDER:
        for e in elements:
            if e["t"] != kind:
                continue
            if not (e["f0"] - 2 <= g <= e["f1"] + 32):
                continue
            if kind in CTX_DRAW:
                CTX_DRAW[kind](base, e, g, ctx)
            else:
                DRAW[kind](base, e, g)
    return base
