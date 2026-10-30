#!/usr/bin/env python3
"""Small PNG textures for the Blender props (greeked print, layer cell masks, green-bar paper).
No readable text: every readable word is a 2D overlay."""
import os, random
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "blender", "tex")
os.makedirs(OUT, exist_ok=True)
R = random.Random(7)

def rr(d, box, r, fill):
    d.rounded_rectangle(box, r, fill=fill)

def sheet(name, band, kind, w=1188, h=840):
    im = Image.new("RGB", (w, h), (238, 240, 243))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 64), fill=band)
    rr(d, (60, 100, 420, 130), 12, (60, 66, 78))
    y = 175
    while y < h - 60:
        indent = 60 + (R.choice([0, 0, 40, 80]) if kind == "tool" else 0)
        L = R.randint(320, w - 120 - indent)
        rr(d, (indent, y, indent + L, y + 16), 8, (150, 156, 168))
        if kind == "tool" and R.random() < 0.3:
            rr(d, (indent, y, indent + 140, y + 16), 8, tuple(int(c * 0.8) for c in band))
        y += 38
    im.save(os.path.join(OUT, f"sheet_{name}.png"))

sheet("sys", (60, 144, 255), "text")
sheet("msg", (232, 150, 60), "text")
sheet("tool", (30, 142, 90), "tool")
sheet("result", (30, 142, 90), "text")

# model layer: cell grid emission mask + base colour (dark graphite with fine traces)
N, S = 24, 2048
mask = Image.new("L", (S, S), 0)
base = Image.new("RGB", (S, S), (18, 20, 24))
dm, db = ImageDraw.Draw(mask), ImageDraw.Draw(base)
pad, cell = 90, (S - 180) / N
for i in range(N):
    for j in range(N):
        x0, y0 = pad + i * cell, pad + j * cell
        db.rectangle((x0 + 4, y0 + 4, x0 + cell - 4, y0 + cell - 4), fill=(30, 33, 40))
        if (i // 6 + j // 6) % 2 == 0 or R.random() < 0.6:
            v = R.randint(120, 255)
            dm.rectangle((x0 + 14, y0 + 14, x0 + cell - 14, y0 + cell - 14), fill=v)
        db.rectangle((x0 + 14, y0 + 14, x0 + cell - 14, y0 + cell - 14), fill=(44, 50, 60))
for k in range(0, S, 32):
    db.line((pad, k, S - pad, k), fill=(26, 28, 33), width=2)
db.rectangle((20, 20, S - 20, S - 20), outline=(140, 112, 60), width=10)
mask.filter(ImageFilter.GaussianBlur(2)).save(os.path.join(OUT, "layer_mask.png"))
base.save(os.path.join(OUT, "layer_base.png"))

# green-bar continuous printer paper (tractor holes both sides)
W, H = 1024, 2048
gb = Image.new("RGB", (W, H), (244, 243, 236))
d = ImageDraw.Draw(gb)
for y in range(0, H, 128):
    d.rectangle((70, y, W - 70, y + 64), fill=(208, 232, 210))
for y in range(20, H, 64):
    d.ellipse((22, y, 46, y + 24), fill=(60, 60, 60)); d.ellipse((W - 46, y, W - 22, y + 24), fill=(60, 60, 60))
d.line((62, 0, 62, H), fill=(200, 200, 196), width=3); d.line((W - 62, 0, W - 62, H), fill=(200, 200, 196), width=3)
for y in range(40, H, 22):   # dot-matrix print rows (greeked)
    if R.random() < 0.55:
        x = 110
        while x < W - 160:
            L = R.randint(40, 160)
            d.rectangle((x, y, min(x + L, W - 120), y + 8), fill=(70, 72, 80)); x += L + R.randint(14, 40)
gb.save(os.path.join(OUT, "greenbar.png"))

# office document (purchase request / order) with a colour header
def doc(name, band):
    w, h = 1050, 1485
    im = Image.new("RGB", (w, h), (246, 246, 243)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 120), fill=band)
    y = 200
    for r in range(16):
        rr(d, (80, y, 80 + R.randint(250, 860), y + 18), 9, (160, 164, 172)); y += 52
    d.rectangle((80, y + 20, w - 80, y + 260), outline=(170, 174, 180), width=4)
    im.save(os.path.join(OUT, f"doc_{name}.png"))
doc("pr", (60, 144, 255)); doc("po", (120, 128, 140))
print("textures ->", OUT, sorted(os.listdir(OUT)))
