"""Film s7, "The loop: one token at a time". Builds films/s7_loop.blend.

The answer grows on the strip one tile at a time (sky band = model words, ember band = the invented digits); every new
tile triggers one full pass up the 24-floor stack behind the strip. The first digit's logit lens is read floor by floor
at the top of the stack (4, 4, 5, then 1). Then five sampled answers at temperature 0.7 stand on a stepped riser beside a
green Ledgerline plaque with the truth, 5,400.

Numbers: brain3d/trace.json generation.greedy (tokens, p), logit_lens.digits, generation.samples_t07, facts.truth.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s789 as P  # noqa: E402

FILM = "s7_loop"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
G = T["generation"]["greedy"]
SAMPLES = T["generation"]["samples_t07"]
LAST = len(TOK) - 1
PITCH, PZ = 0.36, 0.11
DIGITS = {4, 5, 6}


def X(i):
    return (i - LAST) * PITCH


w = B.w
END = B.frames - 1
blk = B.blocks
sc = K.reset(B.frames)
K.studio(sc, focus=(X(106), 0.0, 0.4), key_power=3000, span=8.0)
K.plinth("plinth", X(60) - 0.45, X(100 + len(G) - 1) + 0.5, depth=0.5, height=PZ)

# the prompt's end (positions 60..99)
for t in TOK[60:]:
    root, fm = K.token_tile(f"tok{t['i']}", t["role"], (X(t["i"]), 0, PZ))
    if t["i"] == LAST:
        K.glow_keys(fm, [(0, 0.6), (END, 0.6)])

# the stack behind the strip
TWL = Vector((X(105), 1.3, 0.0))
TW = P.tower2("tw", tuple(TWL), floors=24, pitch=0.075, w=1.7, d=0.56)
for k, m in TW["led"].items():
    K.glow_keys(m, [(0, 0.25)])

# when each generated tile drops: on its spoken word
drop = {0: w("b1", "we") - 6, 1: w("b2", "currently") - 6, 2: w("b2", "have") - 6, 3: w("b2", "space") - 6,
        4: w("b3", "one") - 12, 5: w("b3", "zero") - 8, 6: w("b3", "zero", 1) - 8,
        7: w("b4", "city") - 5, 8: w("b4", "e-bike") - 5, 9: w("b4", "e-bike") + 1, 10: w("b4", "e-bike") + 7,
        11: w("b4", "battery") - 5, 12: w("b4", "packs") - 5, 13: w("b4", "available") - 5, 14: w("b4", "in") - 4,
        15: w("b4", "our") - 4, 16: w("b4", "manchester") - 4, 17: w("b4", "stores") - 4, 18: w("b4", "stores") + 8,
        19: w("b4", "stores") + 16}
faces = {}
for j, s in enumerate(G):
    role = "digit" if j in DIGITS else "answer"
    col = K.EMBER if j in DIGITS else K.SKY
    root, fm = P.drop_tile(f"gen{j}", role, (X(100 + j), 0, PZ), drop[j], face_color=col, face_rest=0.22 if j in DIGITS else 0.12,
                           end=END)
    faces[j] = fm
    P.pulse(TW, drop[j] + 2, per_floor=1 if j >= 7 else 2, peak=2.6)
# b4: the narrator reads the first tiles again; they flash in turn
for j, word in ((0, "we"), (1, "currently"), (2, "have"), (4, "one"), (5, "hundred"), (6, "hundred")):
    f0 = w("b4", word) + (6 if j == 6 else 0)
    rest = 0.22 if j in DIGITS else 0.12
    K.glow_keys(faces[j], [(f0 - 2, rest), (f0 + 4, 2.4), (f0 + 18, rest)])

for k in (21, 22, 23, 24):   # pins for the lens readout, on the middle of each floor's front edge
    K.empty(f"lens{k}", (0.35, -0.3, 0.05), parent=TW["floors"][k - 1])
# b3: the logit lens of the first digit, read at the top of the stack (floors 21..24)
for k, word, nth, col in ((21, "twenty-one", 0, K.EMBER), (22, "twenty-one", 0, K.EMBER), (23, "twenty-three", 0, K.EMBER),
                          (24, "settles", 0, K.EMBER)):
    m = TW["led"][k]
    f0 = w("b3", word, nth) + (14 if k == 22 else 0)
    ec = K.bsdf(m).inputs["Emission Color"]
    K.keyval(ec, [(0, K.SKY), (w("b3", "look") - 6, K.SKY), (w("b3", "look") - 4, col), (w("b3", "then") - 2, col), (w("b3", "then"), K.SKY)])
    K.glow_keys(m, [(f0 - 2, 0.25), (f0 + 6, 4.0), (w("b3", "then") - 8, 4.0), (w("b3", "then"), 0.25)])

# b5: five samples on a stepped riser, and the truth on a green Ledgerline plaque
RX = X(100 + len(G)) + 1.4      # the riser's left end
steps = []
for r in range(5):
    steps.append(K.rbox(f"step{r}", (2.6, 0.36, 0.11 + 0.1 * r), bevel=0.01, seg=4, mat=K.M("plinth"),
                        loc=(RX + 1.15, 0.36 * r, (0.11 + 0.1 * r) / 2)))
sample_words = [("three", 0), ("one", 0), ("over", 0), ("fifty", 0), ("fifteen", 0)]
sample_tiles = []
for r, s in enumerate(SAMPLES):
    n = s["numbers"][0]
    txt = f"{n:,}"
    f0 = w("b5", sample_words[r][0], sample_words[r][1]) - 8
    row = []
    for c, ch in enumerate(txt):
        nm = f"s{r}_{c}"
        root, fm = P.drop_tile(nm, "digit", (RX + 0.15 + c * 0.34, 0.36 * r, 0.11 + 0.1 * r), f0 + 3 * c, face_color=K.EMBER,
                               face_rest=0.22, end=END)
        row.append(nm)
    sample_tiles.append(row)
K.rbox("truthbase", (1.9, 0.72, PZ), bevel=0.012, seg=5, mat=K.M("plinth"), loc=(RX + 3.75, 0.3, PZ / 2))
PLQ = Vector((RX + 3.75, 0.52, PZ))
t_truth = w("b5", "truth")
plq, plq_m = P.plaque("plaque", tuple(PLQ), w=0.8, h=0.26)
K.show(plq, [(0, False), (t_truth - 12, True)])
K.key(plq, "location", [(0, PLQ + Vector((0, 0, 0.5))), (t_truth - 12, PLQ + Vector((0, 0, 0.5))), (t_truth + 8, PLQ)])
K.glow_keys(plq_m, [(0, 0.0), (w("b5", "ledgerline"), 0.0), (w("b5", "ledgerline") + 12, 4.0)])
truth = []
for c, ch in enumerate("5,400"):
    nm = f"t_{c}"
    P.drop_tile(nm, "fact", (RX + 3.11 + c * 0.32, 0.14, PZ), w("b5", "thousand") - 10 + 3 * c, face_color=K.GREEN,
                face_rest=0.3, end=END)
    truth.append(nm)

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_join", lens=35, fstop=3.2).cut(0)
c1.keys([(0, (X(102.0), -1.75, 0.6), (X(100.3), 0.45, 0.36)),
         (w("b1", "runs"), (X(102.4), -2.0, 0.72), (X(100.9), 0.6, 0.5)),
         (blk["b1"]["f1"] + 10, (X(103.0), -2.35, 1.0), (X(101.6), 0.8, 0.8))])
c2 = K.Cam(sc, "c_words", lens=42, fstop=2.6).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (X(102.2), -1.25, 0.62), (X(100.6), 0.0, 0.24)),
         (blk["b2"]["f1"] + 10, (X(104.0), -1.2, 0.6), (X(102.6), 0.0, 0.24))])
c3 = K.Cam(sc, "c_digit", lens=50, fstop=2.4).cut(blk["b3"]["f0"] - 10)
c3.keys([(blk["b3"]["f0"] - 10, (X(104.9), -1.05, 0.56), (X(103.9), 0.0, 0.24)),
         (w("b3", "look") - 4, (X(104.6), -0.95, 0.52), (X(103.95), 0.0, 0.24))])
top = TWL + Vector((0, 0, 23 * 0.075))
c4 = K.Cam(sc, "c_lens", lens=40, fstop=2.8).cut(w("b3", "look") - 4)
c4.keys([(w("b3", "look") - 4, (top.x - 0.6, top.y - 2.1, top.z + 0.3), (top.x - 0.1, top.y, top.z - 0.14)),
         (w("b3", "then") - 8, (top.x - 0.45, top.y - 1.85, top.z + 0.2), (top.x - 0.05, top.y, top.z - 0.12))])
c5 = K.Cam(sc, "c_zeros", lens=45, fstop=2.6).cut(w("b3", "then") - 8)
c5.keys([(w("b3", "then") - 8, (X(106.6), -1.15, 0.58), (X(104.8), 0.0, 0.24)),
         (blk["b3"]["f1"] + 10, (X(107.0), -1.1, 0.56), (X(105.2), 0.0, 0.24))])
c6 = K.Cam(sc, "c_answer", lens=32, fstop=3.2).cut(blk["b4"]["f0"] - 10)
c6.keys([(blk["b4"]["f0"] - 10, (X(101.0), -1.35, 0.72), (X(106.0), 0.0, 0.22)),
         (w("b4", "manchester"), (X(108.0), -1.6, 0.8), (X(114.0), 0.0, 0.22)),
         (blk["b4"]["f1"] + 10, (X(100.0), -1.1, 0.64), (X(106.5), 0.0, 0.22))])
c7 = K.Cam(sc, "c_samples", lens=36, fstop=3.5).cut(blk["b5"]["f0"] - 10)
c7.keys([(blk["b5"]["f0"] - 10, (RX - 0.9, -1.9, 1.05), (RX + 0.6, 0.6, 0.35)),
         (w("b5", "fifteen") + 10, (RX + 0.5, -2.3, 1.25), (RX + 1.0, 0.6, 0.42)),
         (w("b5", "truth"), (RX + 1.6, -2.5, 1.25), (RX + 2.0, 0.5, 0.38)),
         (END, (RX + 3.0, -2.75, 1.25), (RX + 3.15, 0.45, 0.34))])

# ------------------------------------------------------------------------------------------------ pins
pins = [f"tok{i}_front" for i in range(88, 100)] + [f"tok{i}_top" for i in range(96, 100)]
pins += [f"gen{j}_front" for j in range(len(G))] + [f"gen{j}_top" for j in range(len(G))]
pins += [f"lens{k}" for k in range(21, 25)] + [f"tw_pin_f{k}" for k in range(19, 25)] + ["tw_pinl_f1", "tw_pin_f12"]
pins += [f"{n}_top" for row in sample_tiles for n in row] + [f"{n}_front" for row in sample_tiles for n in row]
pins += ["plaque_top", "plaque_mid"] + [f"{n}_front" for n in truth] + [f"{n}_top" for n in truth]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
