"""Film C, the overture (about 41 s): one slow pass over the whole machine. Builds films/overture.blend.

Emma's question lights tile by tile; the 100-tile strip; the 24-floor stack turns them over (passes climbing it); the
invented answer "1 0 0" drops (ember) beside a green Ledgerline plaque with the truth; the camera pulls back on the
whole machine. Numbers: brain3d/trace.json (tokens, generation.greedy digits, facts.truth, meta.vocab).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s789 as P  # noqa: E402

FILM = "overture"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
PITCH, PZ = 0.36, 0.11


def X(i):
    return (i - 99) * PITCH


w = B.w
END = B.frames - 1
blk = B.blocks
sc = K.reset(B.frames)
K.studio(sc, focus=(X(97), 0.0, 0.45), key_power=3000, span=24.0)
K.plinth("plinth", X(0) - 0.45, X(106) + 0.5, depth=0.5, height=PZ)

# the question's words, lit as they are spoken
qwords = {80: "how", 81: "many", 82: "city", 83: "e-bike", 84: "e-bike", 85: "e-bike", 86: "battery", 87: "packs", 88: "do",
          89: "we", 90: "have", 91: "in", 92: "manchester", 93: "stores", 94: "stores"}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    if i in qwords:
        f0 = w("b1", qwords[i]) + {84: 4, 85: 8, 94: 10}.get(i, 0)
        K.glow_keys(fm, [(0, 0.0), (f0 - 2, 0.0), (f0 + 4, 2.4), (f0 + 26, 0.5), (END, 0.5)])
    elif i == 99:
        K.glow_keys(fm, [(0, 0.0), (w("b2", "in") - 4, 0.0), (w("b2", "in") + 6, 1.6), (END, 0.8)])

# the machine behind the strip
TWL = Vector((X(95), 1.45, 0.0))
import math  # noqa: E402
import random  # noqa: E402
rnd = random.Random(5)
cells = {k: K.cells_mat(f"ovc{k}", [0.7 * math.sin(0.19 * i + 0.8 * k) * math.cos(0.045 * i) + 0.15 * rnd.uniform(-1, 1) for i in range(96 * 5)],
                        96, 5, K.SKY, vmax=1.0, strength=0.0) for k in range(1, 25)}
TW = P.tower2("tw", tuple(TWL), floors=24, pitch=0.075, w=1.8, d=0.6, cells=cells)
for k, m in TW["led"].items():
    K.glow_keys(m, [(0, 0.4)])
for k, m in cells.items():
    f0 = w("b2", "twenty-four") + int((k - 1) * 1.2)
    K.glow_keys(m, [(0, 0.5), (f0 - 2, 0.5), (f0 + 8, 2.6), (END, 2.0)])
for f0 in (w("b2", "turn"), w("b2", "every"), w("b2", "chosen"), w("b2", "thousand"), w("b2", "thirty-six"), w("b3", "comes")):
    P.pulse(TW, f0 - 6, per_floor=1, peak=3.2, base=0.2, hold=5)

# the invented answer and the truth
for j in range(3):
    P.drop_tile(f"ans{j}", "digit", (X(100 + j), 0, PZ), w("b3", "one") - 8 + 4 * j, face_color=K.EMBER, face_rest=0.3, end=END)
PLQ = Vector((X(104.4), 0.02, PZ))
plq, plq_m = P.plaque("plaque", tuple(PLQ), w=0.72, h=0.24)
f_tr = w("b3", "truth")
K.show(plq, [(0, False), (f_tr - 12, True)])
K.key(plq, "location", [(0, PLQ + Vector((0, 0, 0.45))), (f_tr - 12, PLQ + Vector((0, 0, 0.45))), (f_tr + 8, PLQ)])
K.glow_keys(plq_m, [(0, 0.0), (f_tr, 0.0), (f_tr + 12, 4.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_question", lens=38, fstop=2.4).cut(0)
c1.keys([(0, (X(78.6), -1.25, 0.56), (X(81.5), 0.0, 0.22)),
         (blk["b1"]["f1"] + 12, (X(92.5), -1.2, 0.55), (X(95.0), 0.0, 0.22))])
c2 = K.Cam(sc, "c_machine", lens=30, fstop=3.2).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (X(97.6), -2.0, 0.8), (X(92.0), 0.3, 0.35)),
         (w("b2", "twenty-four") - 6, (X(98.4), -2.4, 1.1), (X(94.6), 0.9, 0.7)),
         (blk["b2"]["f1"] + 12, (X(99.2), -2.6, 1.55), (X(95.4), 1.4, 1.05))])
c3 = K.Cam(sc, "c_answer", lens=40, fstop=2.6).cut(blk["b3"]["f0"] - 10)
c3.keys([(blk["b3"]["f0"] - 10, (X(102.4), -1.3, 0.62), (X(100.6), 0.0, 0.24)),
         (f_tr - 6, (X(103.4), -1.75, 0.72), (X(102.7), 0.0, 0.26)),
         (w("b3", "today") - 4, (X(104.0), -1.95, 0.8), (X(103.0), 0.0, 0.28)),
         (END, (X(106.8), -4.3, 2.1), (X(99.5), 0.9, 0.6))])

pins = [f"tok{i}_front" for i in range(78, 100)] + [f"ans{j}_front" for j in range(3)] + ["ans2_top", "plaque_top", "tw_pin_f24", "tw_pin_f12"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
