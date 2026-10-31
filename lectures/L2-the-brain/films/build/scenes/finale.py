"""Film "finale": "The whole machine" (Lecture 2 recap). Builds films/finale.blend.

One camera journey through the whole machine on Emma's question: the strip of 100 tiles; the question's tiles look up
their 896-number vectors (real input embeddings); attention (the last position's query in front of the keys, real k
values, beams, 65.2% on Manchester in block 24, head 2); the column climbs the 24-floor stack in one pass (logit lens near
the top); at the top it meets the vocabulary and becomes probabilities (We 56.4%); "We" drops onto the strip; the pass
runs again; the invented "1 0 0" against a green Ledgerline plaque (5,400); the plaque slides into the prompt and the same
model answers "5,400".

Numbers: brain3d/trace.json (tokens, final.last, logit_lens.last, generation, facts) and films/qkv_data.json.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s789 as P  # noqa: E402

FILM = "finale"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
D = K.load("films/qkv_data.json")
QK = D["qkv"]
EMB = D["vectors"]["embedding"]
TOK = T["tokens"]
G = T["generation"]["greedy"]
FG = T["facts"]["greedy"]
TOP6 = T["final"]["last"]["1.0"][:6]
W = QK["weights"]
MAN, LAST = 92, 99
PITCH, PZ = 0.36, 0.11
ZT = PZ + 0.075
CELL = 0.02
ZP = ZT + 0.03 + 8 * CELL + 0.012
ZH = ZT - 8 * CELL - 0.05
SH = 1.3                       # how far the strip opens for the Ledgerline line
GAP_I = 75                     # the line goes in at position 75 (the end of the system prompt)
TX, TY = 1.0, 1.4              # the stack
TOPZ = 23 * 0.075


def X(i):
    return (i - LAST) * PITCH


w = B.w
END = B.frames - 1
blk = B.blocks
sc = K.reset(B.frames)
K.studio(sc, focus=(-1.0, 0.0, 0.45), key_power=3000, span=16.0)
K.plinth("plinth", X(0) - 0.45, X(110) + SH + 0.5, depth=0.5, height=PZ)

f_open0, f_open1 = w("b9", "put") + 2, w("b9", "prompt", 1) - 4


def shifting(obj, x0, y=0.0, z=PZ):
    """Objects at or after the gap slide right when the strip opens for the fact line."""
    K.key(obj, "location", [(0, (x0, y, z)), (f_open0, (x0, y, z)), (f_open1, (x0 + SH, y, z))])


# ---- the strip
faces = {}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    faces[i] = fm
    if i >= GAP_I:
        shifting(root, X(i))
f_tok = w("b2", "tokens")
for i in range(N := len(TOK)):
    d = int(i * 0.7)
    peak = 2.2 if i >= 80 else 1.2
    K.glow_keys(faces[i], [(0, 0.0), (f_tok - 50 + d, 0.0), (f_tok - 44 + d, peak), (f_tok - 24 + d, 0.08 if i != LAST else 0.6)])
K.glow_keys(faces[MAN], [(w("b2", "manchester") - 2, 0.08), (w("b2", "manchester") + 6, 2.6), (w("b2", "manchester") + 50, 0.3)])

# ---- the question's vectors: real 896-number input embeddings, as 28 x 32 cell slabs over tiles 80..99
slabs = {}
f_vec = w("b3", "vector")
for i in range(80, 100):
    sl, sm = K.vector_plate(f"vec{i}", EMB[str(i)], 28, 32, K.SKY, (X(i), 0.0, ZH), cell=0.0095, vmax=0.03, glow=0.0)
    sl.scale = (0.5,) * 3
    slabs[i] = (sl, sm)
    d = int((i - 80) * 1.6)
    up = (X(i), 0.0, ZT + 0.03 + 16 * 0.0095 + 0.012)
    K.key(sl, "location", [(0, (X(i), 0, ZH)), (f_vec - 10 + d, (X(i), 0, ZH)), (f_vec + 10 + d, up)])
    K.key(sl, "scale", [(0, (0.5,) * 3), (f_vec - 10 + d, (0.5,) * 3), (f_vec + 10 + d, (1.0,) * 3)])
    K.glow_keys(sm, [(0, 0.0), (f_vec - 10 + d, 0.0), (f_vec + 10 + d, 3.4)])

# ---- attention: keys rise (slabs sink), the last position's query faces them, beams carry the weights
b4 = blk["b4"]["f0"]
f_q, f_key, f_65 = w("b4", "query"), w("b4", "key"), w("b4", "sixty-five")
PROBE = Vector((X(94.5), -1.05, ZP + 0.03))
keys_p = {}
for i in range(80, 100):
    sl, sm = slabs[i]
    up = sl.location.copy()
    if i != LAST:
        K.key(sl, "location", [(b4 - 12, up), (b4 + 6, (X(i), 0, ZH))])
        K.key(sl, "scale", [(b4 - 12, (1.0,) * 3), (b4 + 6, (0.5,) * 3)])
    kp, km = K.vector_plate(f"k{i}", QK["k"][i], 4, 16, K.K_COL, (X(i), 0.0, ZH), cell=CELL, vmax=5.4, glow=0.0)
    kp.scale = (0.6,) * 3
    d = int((99 - i) * 0.6)
    K.key(kp, "location", [(0, (X(i), 0, ZH)), (f_key - 14 + d, (X(i), 0, ZH)), (f_key + 4 + d, (X(i), 0, ZP)),
                           (blk["b5"]["f0"] - 10, (X(i), 0, ZP)), (blk["b5"]["f0"] + 8, (X(i), 0, ZH))])
    K.key(kp, "scale", [(0, (0.6,) * 3), (f_key - 14 + d, (0.6,) * 3), (f_key + 4 + d, (1.0,) * 3),
                        (blk["b5"]["f0"] - 10, (1.0,) * 3), (blk["b5"]["f0"] + 8, (0.6,) * 3)])
    K.glow_keys(km, [(0, 0.0), (f_key - 14 + d, 0.0), (f_key + 4 + d, 4.2)])
    keys_p[i] = kp
# the last slab moves aside (it will climb the stack); the query plate appears in front of the row, facing the keys
sl99, sm99 = slabs[LAST]
up99 = sl99.location.copy()
side99 = Vector((X(LAST) + 0.32, -0.32, up99.z))
K.key(sl99, "location", [(b4 - 12, up99), (b4 + 10, side99)])
qp, qm = K.vector_plate("qprobe", QK["q"], 4, 16, K.Q_COL, tuple(PROBE), cell=CELL, vmax=2.6, glow=0.0, two_sided=True)
qp.rotation_euler = (0, 0, math.pi)
K.key(qp, "location", [(0, (X(LAST), 0, ZH)), (f_q - 16, (X(LAST), 0, ZH)), (f_q + 6, PROBE), (blk["b5"]["f0"] - 10, PROBE),
                       (blk["b5"]["f0"] + 10, PROBE + Vector((0, 0, -0.45)))])
K.key(qp, "scale", [(0, (0.4,) * 3), (f_q - 16, (0.4,) * 3), (f_q + 6, (1.0,) * 3), (blk["b5"]["f0"] - 10, (1.0,) * 3),
                    (blk["b5"]["f0"] + 10, (0.001,) * 3)])
K.glow_keys(qm, [(0, 0.0), (f_q - 16, 0.0), (f_q + 6, 5.0)])
mman, liq_man, lm_man = K.meter("m92", (X(MAN) + 0.1, -0.06, ZT), height=0.34, r=0.017, color=K.SKY)
K.show(mman, [(0, False), (f_65 - 30, True), (blk["b5"]["f0"] + 10, False)])
K.key(liq_man, "scale", [(0, (1, 1, 0.001)), (f_65 - 12, (1, 1, 0.001)), (f_65 + 14, (1, 1, W[MAN]))])
K.glow_keys(lm_man, [(0, 0.0), (f_65 - 12, 4.0)])
for i in range(80, 100):
    m_ = K.light_mat(f"beam{i}_m", K.Q_COL, 0.0)
    bo = K.beam(f"beam{i}", PROBE + Vector((0, 0.012, 0)), (X(i), -0.012, ZP), r=0.006 if i == MAN else 0.0035, mat=m_)
    d = int((99 - i) * 0.5)
    bo.scale = (1, 1, 0.001)
    K.key(bo, "scale", [(0, (1, 1, 0.001)), (f_key + d, (1, 1, 0.001)), (f_key + d + 14, (1, 1, 1.0))])
    g = 0.04 + 9.0 * (W[i] / W[MAN]) ** 0.85
    K.glow_keys(m_, [(0, 0.0), (f_key + d, 0.0), (f_key + d + 6, 1.4), (f_65 - 10, 1.4), (f_65 + 12, g), (blk["b5"]["f0"] - 4, g),
                     (blk["b5"]["f0"] + 8, 0.0)])
    K.show(bo, [(0, False), (f_key + d - 1, True), (blk["b5"]["f0"] + 10, False)])

# ---- the stack; the column climbs it in one pass
rnd = random.Random(3)
cells = {k: K.cells_mat(f"fc{k}", [0.7 * math.sin(0.2 * i + 0.7 * k) * math.cos(0.05 * i) + 0.15 * rnd.uniform(-1, 1)
                                   for i in range(96 * 5)], 96, 5, K.SKY, vmax=1.0, strength=0.0) for k in range(1, 25)}
TW = P.tower2("tw", (TX, TY, 0.0), floors=24, pitch=0.075, w=1.8, d=0.6, cells=cells)
for k, m in TW["led"].items():
    K.glow_keys(m, [(0, 0.35)])
f_climb = w("b5", "climbs")
CL = 3   # frames per floor
for k, m in cells.items():
    t = f_climb + (k - 1) * CL
    K.glow_keys(m, [(0, 0.6), (t - 2, 0.6), (t + 3, 3.4), (t + 30, 1.6), (END, 1.6)])
P.pulse(TW, f_climb, per_floor=CL, peak=3.6, base=0.35, hold=8)
front = TY - 0.3 - 0.06
K.key(sl99, "location", [(blk["b5"]["f0"] - 6, side99), (f_climb - 4, (TX, front - 0.12, 0.25)),
                         (f_climb + 24 * CL, (TX, front - 0.12, TOPZ + 0.22)), (blk["b6"]["f0"] + 30, (TX, front - 0.12, TOPZ + 0.22))])
K.key(sl99, "scale", [(f_climb - 4, (1.0,) * 3), (f_climb + 24 * CL, (1.0,) * 3), (blk["b6"]["f0"] + 30, (1.0,) * 3),
                      (blk["b6"]["f0"] + 50, (0.001,) * 3)])
K.glow_keys(sm99, [(f_climb, 3.4), (f_climb + 24 * CL, 4.5)])
for k in (22, 23, 24):
    K.empty(f"lens{k}", (-0.55, -0.3, 0.05), parent=TW["floors"][k - 1])

# ---- at the top: the vocabulary band and the probability columns
VZ = TOPZ + 0.08
K.rbox("deck", (1.9, 0.62, 0.03), bevel=0.008, seg=3, mat=K.M("alu_dark"), loc=(TX, TY, VZ - 0.015))
vocab_m = K.cells_mat("vocab", [rnd.uniform(-1, 1) for _ in range(220 * 10)], 220, 10, K.SKY, vmax=1.0, strength=0.0)
K.plane("vocab_band", 1.75, 0.16, vocab_m, loc=(TX, TY + 0.22, VZ + 0.4))
K.rbox("vocab_frame", (1.8, 0.03, 0.2), bevel=0.006, seg=3, mat=K.M("graphite"), loc=(TX, TY + 0.24, VZ + 0.4))
K.empty("vocab_pin", (TX + 0.88, TY + 0.2, VZ + 0.5))
for nm in ("vocab_band", "vocab_frame"):
    K.show(bpy.data.objects[nm], [(0, False), (w("b6", "scored") - 24, True)])
    vo = bpy.data.objects[nm]
    K.key(vo, "scale", [(0, (1, 1, 0.001)), (w("b6", "scored") - 24, (1, 1, 0.001)), (w("b6", "scored") + 4, (1, 1, 1))])
f_score, f_soft = w("b6", "scored"), w("b6", "softmax")
K.glow_keys(vocab_m, [(0, 0.0), (f_score - 4, 0.0), (f_score + 20, 2.6), (blk["b7"]["f0"] + 40, 1.0)])
bars = []
for n, row in enumerate(TOP6):
    bx = TX - 0.65 + n * 0.26
    mr, liq, lm = K.meter(f"bar{n}", (bx, TY - 0.12, VZ), height=0.6, r=0.03, color=K.SKY)
    word = {0: ("we", 0), 1: ("as", 0), 2: ("manchester", 0)}.get(n)
    f0 = w("b6", word[0]) if word else f_soft + 30
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (f_soft + 10 + 4 * n, (1, 1, 0.001)), (f_soft + 40 + 4 * n, (1, 1, max(0.002, row["p"])))])
    K.glow_keys(lm, [(0, 0.0), (f_soft + 10, 3.0 if n == 0 else 1.8), (f0, 3.0 if n == 0 else 1.8), (f0 + 6, 5.0 if n == 0 else 3.2),
                     (f0 + 30, 3.0 if n == 0 else 1.8)])
    bars.append(f"bar{n}_top")
    K.show(mr, [(0, False), (f_score - 20, True)])

# ---- one token chosen: "We" drops onto the strip; the pass runs again; the answer grows, one tile at a time
f_ch = w("b7", "chosen")
weT, we_m = K.token_tile("gen0", "answer", (TX - 0.65, TY - 0.12, VZ + 0.7))
P.set_face(we_m, K.SKY)
K.key(weT, "location", [(0, (TX - 0.65, TY - 0.12, VZ + 0.7)), (f_ch, (TX - 0.65, TY - 0.12, VZ + 0.7)),
                        (f_ch + 34, (X(100), 0, PZ + 0.35)), (f_ch + 46, (X(100), 0, PZ))])
K.key(weT, "scale", [(0, (0.6,) * 3), (f_ch, (0.6,) * 3), (f_ch + 34, (1.0,) * 3)])
K.glow_keys(we_m, [(0, 2.4), (f_ch + 46, 2.4), (f_ch + 80, 0.2)])
K.show(weT, [(0, False), (f_ch - 1, True)])
shifting_tiles = [weT]
drops = {1: w("b7", "again") - 4, 2: w("b7", "again") + 10, 3: w("b7", "time") - 4, 4: w("b8", "one") - 10,
         5: w("b8", "zero") - 8, 6: w("b8", "zero", 1) - 8}
for j, f0 in drops.items():
    dig = j >= 4
    r, _ = P.drop_tile(f"gen{j}", "digit" if dig else "answer", (X(100 + j), 0, PZ), f0, face_color=K.EMBER if dig else K.SKY,
                       face_rest=0.45 if dig else 0.12)
    P.pulse(TW, f0 - 26, per_floor=1, peak=3.0, base=0.35, hold=4)
    shifting_tiles.append(r)
P.pulse(TW, w("b7", "pass") - 4, per_floor=1, peak=3.4, base=0.35, hold=5)
# the invented answer sinks before the fix
f_sink = w("b9", "put") - 6
for j, r in enumerate(shifting_tiles):
    x = X(100 + j)
    K.key(r, "location", [(f_sink - 10 + 2 * j, (x, 0, PZ)), (f_sink + 6 + 2 * j, (x, 0, PZ - 0.25))])
    K.show(r, [(f_sink + 8 + 2 * j, False)])

# ---- the truth, then the fix: the Ledgerline plaque slides into the prompt; the same model answers 5,400
PLQ = Vector((X(106.2), -0.62, 0.0))
plq, plq_m = P.plaque("plaque", tuple(PLQ), w=1.12, h=0.24)
f_led = w("b8", "ledgerline")
K.show(plq, [(0, False), (f_led - 14, True)])
gapx = X(GAP_I) - PITCH / 2 + SH / 2
K.key(plq, "location", [(0, PLQ + Vector((0, 0, -0.3))), (f_led - 14, PLQ + Vector((0, 0, -0.3))), (f_led + 8, PLQ),
                        (f_open0 - 24, PLQ), (f_open0 - 8, PLQ + Vector((0, 0, 0.55))), (f_open1 - 2, (gapx, -0.02, PZ + 0.55)),
                        (f_open1 + 12, (gapx, -0.02, PZ - 0.02))])
K.glow_keys(plq_m, [(0, 0.0), (f_led, 0.0), (f_led + 12, 4.0)])
f_ans = w("b9", "same")
new = []
for j in range(8):
    dig = FG[j]["text"].strip().isdigit() or FG[j]["text"] == ","
    f0 = (f_ans + 4 + 3 * j) if j < 3 else (w("b9", "five") - 10 + 4 * (j - 3))
    P.drop_tile(f"new{j}", "fact" if dig else "answer", (X(100 + j) + SH, 0, PZ), f0, face_color=K.GREEN if dig else K.SKY,
                face_rest=0.45 if dig else 0.12)
    new.append(f"new{j}")

# ------------------------------------------------------------------------------------------------ the camera journey
TOPV = Vector((TX, TY, TOPZ))
c1 = K.Cam(sc, "c_journey", lens=36, fstop=2.6)
c1.keys([
    (0, (X(79.4), -1.15, 0.55), (X(82.4), 0.0, 0.22)),
    (w("b1", "stores") + 10, (X(91.0), -1.15, 0.55), (X(94.0), 0.0, 0.22)),
    (w("b2", "number"), (X(99.6), -1.45, 0.7), (X(96.0), 0.0, 0.25)),
    (w("b2", "manchester") + 10, (X(94.6), -1.2, 0.6), (X(92.2), 0.0, 0.24)),
    (w("b3", "column"), (X(100.6), -2.2, 1.05), (X(93.5), 0.0, 0.42)),
    (blk["b3"]["f1"] + 10, (X(100.9), -2.35, 1.12), (X(92.8), 0.0, 0.44)),
    (w("b4", "query") + 10, (X(99.4), -2.3, 0.95), (X(93.8), -0.4, 0.42)),
    (f_65 - 30, (X(96.0), -1.75, 0.78), (X(92.8), -0.15, 0.42)),
    (f_65 + 20, (X(93.5), -1.1, 0.62), (X(92.2), 0.0, 0.42)),
    (blk["b4"]["f1"] + 10, (X(93.6), -1.05, 0.6), (X(92.2), 0.0, 0.42)),
    (f_climb - 6, (TX + 1.6, -1.6, 0.7), (TX - 0.1, TY - 0.4, 0.55)),
    (f_climb + 24 * CL, (TX + 1.5, -1.3, TOPZ + 0.15), (TX - 0.1, TY - 0.4, TOPZ - 0.05)),
    (blk["b5"]["f1"] + 10, (TX + 1.3, -1.15, TOPZ + 0.3), (TX - 0.1, TY - 0.3, TOPZ + 0.08)),
    (f_score + 10, (TX + 0.75, -0.75, TOPZ + 0.62), (TX, TY - 0.05, TOPZ + 0.32)),
    (w("b6", "we"), (TX + 0.35, -0.42, TOPZ + 0.48), (TX - 0.25, TY - 0.12, TOPZ + 0.3)),
    (blk["b6"]["f1"] + 10, (TX + 0.45, -0.5, TOPZ + 0.5), (TX - 0.2, TY - 0.12, TOPZ + 0.3)),
    (f_ch + 40, (X(102.6), -1.9, 0.95), (X(100.6), 0.35, 0.4)),
    (w("b7", "time"), (X(103.6), -2.3, 1.1), (X(101.6), 0.6, 0.55)),
    (w("b8", "one") + 4, (X(106.4), -1.4, 0.62), (X(103.8), 0.0, 0.24)),
    (w("b8", "zero", 1) + 20, (X(107.2), -1.5, 0.64), (X(104.6), -0.1, 0.24)),
    (f_led + 20, (X(108.6), -2.75, 0.98), (X(105.0), -0.3, 0.24)),
    (w("b9", "up") - 6, (X(103.0), -2.6, 1.1), (X(97.0), 0.0, 0.3)),
    (f_open0 - 10, (X(93.0), -2.6, 1.15), (X(85.0), 0.0, 0.35)),
    (f_open1, (X(80.5), -2.3, 1.0), (X(75.6), 0.0, 0.25)),
    (f_ans + 6, (X(80.0), -2.15, 0.95), (X(75.6), 0.0, 0.25)),
])
c2 = K.Cam(sc, "c_answer", lens=36, fstop=2.6).cut(f_ans + 6)
c2.keys([(f_ans + 6, (X(106.4) + SH, -1.85, 0.76), (X(104.2) + SH, 0.0, 0.24)),
         (w("b9", "where") - 10, (X(106.7) + SH, -1.95, 0.8), (X(104.5) + SH, 0.0, 0.25)),
         (END, (X(92.5), -8.3, 3.4), (X(91.5), 0.5, 0.35))])
c2.lens([(w("b9", "where") - 10, 36), (END, 20)])

pins = [f"tok{i}_front" for i in range(76, 100)] + [f"tok{i}_top" for i in (92, 99)] + ["k92_top", "qprobe_top", "m92_top"]
pins += [f"lens{k}" for k in (22, 23, 24)] + bars + ["vocab_pin", "vec92_top", "vec86_top", "vec99_top"]
pins += [f"gen{j}_front" for j in range(7)] + [f"gen{j}_top" for j in range(7)] + ["plaque_top", "plaque_mid", "tw_pin_f24", "tw_pin_f1"]
pins += [f"{n}_front" for n in new] + [f"{n}_top" for n in new]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
