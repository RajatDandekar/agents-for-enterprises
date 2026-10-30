"""Film A, v3: "Query, key and value" (block 24, head 2, the last prompt position). Builds films/qkv.blend.

Hero framing: every shot is built around the few tokens that matter (" battery", " packs", " Manchester", " stores"
and the last position), large in frame; the rest of the 100 tiles fall into depth of field. The query plate floats in
front of the row FACING the keys; straight light beams carry each dot product to its key, whose glass column fills to
the real score; softmax reallocates the light; the values slide into one blended output plate, which docks into head
2 on floor 24 of the block stack.

Numbers: films/qkv_data.json (q, k, v, dot products, scores, weights, output) and brain3d/trace.json (tokens, roles).
Timing: timeline/qkv.json (Daniel's words).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402

FILM = "qkv"
B = K.Beats(FILM)
D = K.load("films/qkv_data.json")
T = K.load("brain3d/trace.json")
QK = D["qkv"]
TOK = T["tokens"]
N = len(TOK)
LAST = N - 1
MAN, MAN_SYS, STORES, BATT, PACKS = 92, 21, 93, 86, 87
HERO = {BATT, PACKS, MAN, STORES, LAST}
W, DOT, SC = QK["weights"], QK["dots"], QK["scores"]

PITCH = 0.36
PZ = 0.11
ZT = PZ + 0.075
CELL = 0.02
PH = 16 * CELL            # plate height
ZP = ZT + 0.03 + PH / 2 + 0.012
ZH = ZT - PH / 2 - 0.05   # hidden inside tile and plinth
DX = 0.1
PROBE = Vector((-1.45, -1.0, ZP + 0.04))
OUTP = Vector((-1.05, -0.82, ZP + 0.04))
TOWER = Vector((1.55, 1.05, 0.0))
TW_PITCH, TW_W, TW_D = 0.072, 1.5, 0.56


def X(i):
    return (i - LAST) * PITCH


def pct(a, b, t):
    return int(round(a + (b - a) * t))


sc = K.reset(B.frames)
K.studio(sc, focus=(-1.6, 0.0, 0.35), key_power=3000, span=26.0)
K.plinth("plinth", X(0) - 0.45, 0.45, depth=0.5, height=PZ)

vmax = {"q": 2.6, "k": 5.4, "v": 3.2}
faces, plates, meters, beams = {}, {}, {}, {}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    faces[i] = fm
    for kind, dx, col, vals in (("q", -DX, K.Q_COL, QK["q_all"][i]), ("k", 0.0, K.K_COL, QK["k"][i]),
                                ("v", DX, K.V_COL, QK["v"][i])):
        pr, pm = K.vector_plate(f"{kind}{i}", vals, 4, 16, col, (X(i) + dx, 0.0, ZH), cell=CELL, vmax=vmax[kind],
                                glow=0.0, two_sided=(kind == "q" and i == LAST))
        pr.scale = (0.6, 0.6, 0.6)
        plates[(kind, i)] = (pr, pm)
    mr, liq, lm = K.meter(f"m{i}", (X(i) + DX, 0.0, ZT), height=0.34, r=0.017 if i in HERO else 0.013, color=K.SKY)
    meters[i] = (mr, liq, lm)

# the last token's own vector and the three learned matrices (shot "matrices")
vec896 = D["vectors"]["input_norm_layer24"][str(LAST)]
slab, slab_m = K.vector_plate("slab", vec896, 28, 32, K.SKY, (0.0, 0.8, ZP + 0.05), cell=0.012, vmax=2.5, glow=0.0, reveal=0.0)
frames_m = {}
for kind, dx in (("wq", -DX), ("wk", 0.0), ("wv", DX)):
    fr, fmm = K.matrix_frame(kind, (X(LAST) + dx * 1.3, 0.42, ZP + 0.03), w=0.1, h=0.27, seed={"wq": 1, "wk": 2, "wv": 3}[kind],
                             tint={"wq": K.Q_COL, "wk": K.K_COL, "wv": K.V_COL}[kind])
    frames_m[kind] = (fr, fmm)
beams_b3 = []
for kind, dx in (("q", -DX), ("k", 0.0), ("v", DX)):
    bm_ = K.light_mat(f"b3beam_{kind}", {"q": K.Q_COL, "k": K.K_COL, "v": K.V_COL}[kind], 0.0)
    bo = K.beam(f"b3beam_{kind}", (dx * 0.6, 0.78, ZP + 0.05), (X(LAST) + dx, 0.012, ZP), r=0.0045, mat=bm_)
    bo.scale = (1, 1, 0.001)
    beams_b3.append((bo, bm_))

# the copy of the query that faces Manchester's key for the close-up of the dot product
ghost, ghost_m = K.vector_plate("ghostq", QK["q"], 4, 16, K.Q_COL, tuple(PROBE), cell=CELL, vmax=vmax["q"], glow=0.0)
ghost.scale = (0.001,) * 3
thread_m = K.light_mat("thread_m", K.SKY, 0.0)
# the mixed output of the head
outp, out_m = K.vector_plate("outp", QK["out"], 4, 16, K.SKY, tuple(OUTP), cell=CELL, vmax=vmax["v"], glow=0.0, reveal=0.0)
outp.scale = (0.001,) * 3

# straight light beams from the query (in front of the row) to every key
for j in range(N):
    m_ = K.light_mat(f"beam{j}_m", K.Q_COL, 0.0)
    kt = Vector((X(j), -0.012, ZP))
    beams[j] = (K.beam(f"beam{j}", PROBE + Vector((0, 0.01, 0)), kt, r=0.0055 if j in HERO else 0.0028, mat=m_), m_)
    beams[j][0].scale = (1, 1, 0.001)

# the block stack (shot "close"): 24 floors x 14 heads, head 2 on floor 24 gets its own light
TW = K.tower("tower", tuple(TOWER), floors=24, pitch=TW_PITCH, w=TW_W, d=TW_D, lit={(24, 2)})

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")}
w = B.w
END = B.frames - 1

# b1: the last tile lights; a soft shimmer runs back along the row
f_last = w("b1", "last")
for i in range(N):
    keys = [(0, 0.0)]
    if i == LAST:
        keys += [(f_last - 6, 0.0), (f_last + 12, 3.2), (END, 3.2)]
    else:
        fm_ = w("b1", "matter") + int((LAST - i) * 0.9)
        keys += [(fm_ - 8, 0.0), (fm_, 1.0), (fm_ + 14, 0.0)]
    K.glow_keys(faces[i], keys)


def rise(kind, i, f0, dur=18, glow=4.5):
    pr, pm = plates[(kind, i)]
    base = Vector(pr.location)
    up = Vector((base.x, base.y, ZP))
    K.key(pr, "location", [(0, base), (f0, base), (f0 + dur, up)])
    K.key(pr, "scale", [(0, (0.6,) * 3), (f0, (0.6,) * 3), (f0 + dur, (1.0,) * 3)])
    K.glow_keys(pm, [(0, 0.0), (f0, 0.0), (f0 + dur, glow)])


def sink(kind, i, f0, dur=14):
    pr, pm = plates[(kind, i)]
    x, y = pr.location.x, pr.location.y
    K.key(pr, "location", [(f0, Vector((x, y, ZP))), (f0 + dur, Vector((x, y, ZH)))])
    K.key(pr, "scale", [(f0, (1.0,) * 3), (f0 + dur, (0.6,) * 3)])


# b2: query, key and value plates rise out of every tile, from the last token back along the row
fq, fk, fv = w("b2", "query"), w("b2", "key"), w("b2", "value")
for i in range(N):
    d = int((LAST - i) * 0.35)
    rise("q", i, fq - 8 + d)
    rise("k", i, fk - 8 + d)
    rise("v", i, fv - 8 + d)

# b3: the vector, through three learned matrices, prints q, k and v again
f_vec, f_mat, f_64 = w("b3", "own"), w("b3", "learned"), w("b3", "sixty-four")
b4 = b["b4"]["f0"]
slab.scale = (0.001,) * 3
K.key(slab, "scale", [(0, (0.001,) * 3), (f_vec - 14, (0.001,) * 3), (f_vec + 10, (1.0,) * 3), (b4 - 6, (1.0,) * 3),
                      (b4 + 10, (0.001,) * 3)])
K.glow_keys(slab_m, [(0, 0.0), (f_vec - 4, 0.0), (f_vec + 10, 3.4), (b4 - 6, 3.4), (b4 + 8, 0.0)])
K.keyval(slab_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_vec, 0.0), (f_vec + 24, 1.0)])
for kind, (fr, fmm) in frames_m.items():
    fr.scale = (0.001,) * 3
    K.key(fr, "scale", [(0, (0.001,) * 3), (f_vec - 6, (0.001,) * 3), (f_vec + 14, (1.0,) * 3), (b4 - 6, (1.0,) * 3),
                        (b4 + 8, (0.001,) * 3)])
    K.glow_keys(fmm, [(0, 0.0), (f_mat - 4, 0.0), (f_mat + 10, 2.6), (f_64 + 10, 1.3), (b4, 0.0)])
for bo, bm_ in beams_b3:
    K.key(bo, "scale", [(0, (1, 1, 0.001)), (f_mat - 6, (1, 1, 0.001)), (f_mat + 14, (1, 1, 1.0))])
    K.glow_keys(bm_, [(0, 0.0), (f_mat - 6, 0.0), (f_mat + 4, 3.2), (b4 - 8, 2.0), (b4 + 4, 0.0)])
    K.show(bo, [(0, False), (f_mat - 8, True), (b4 + 6, False)])
for kind in ("q", "k", "v"):
    pm = plates[(kind, LAST)][1]
    K.keyval(pm.node_tree.nodes["reveal"].outputs[0], [(0, 1.0), (f_mat, 1.0), (f_mat + 2, 0.0), (f_mat + 34, 1.0)])

# b4: the query moves in front of the row and turns to face the keys; the other queries and all values sink
f_send, f_mul, f_add, f_one = w("b4", "sends"), w("b4", "multiply"), w("b4", "up"), w("b4", "score")
for i in range(N):
    if i != LAST:
        sink("q", i, b4 - 10)
    sink("v", i, b4 - 6)
    K.show(meters[i][0], [(0, False), (b4 - 4, True), (b["b7"]["f0"] + 30, False)])
qpr, qpm = plates[("q", LAST)]
qslot = Vector((X(LAST) - DX, 0.0, ZP))
K.key(qpr, "location", [(b4 - 10, qslot), (f_send - 2, PROBE)])
K.key(qpr, "rotation_euler", [(b4 - 10, (0, 0, 0)), (f_send - 2, (0, 0, math.pi))])
K.glow_keys(qpm, [(b4, 4.5), (f_send, 5.5)])
for j, (bo, bm_) in beams.items():
    dly = int((LAST - j) * 0.35)
    K.key(bo, "scale", [(0, (1, 1, 0.001)), (f_send + dly, (1, 1, 0.001)), (f_send + dly + 14, (1, 1, 1.0))])
    K.glow_keys(bm_, [(0, 0.0), (f_send + dly, 0.0), (f_send + dly + 6, 1.6 if j in HERO else 0.7)])

# the close-up: a copy of the query faces Manchester's key like an open book; their cells light in reading order,
# a light thread joins them, and the glass column follows the running sum of q_i * k_i up to the dot product 62.5
kpr, kman_m = plates[("k", MAN)]
f_dock = f_mul - 20
b5 = b["b5"]["f0"]
ang = math.radians(32)
dockq = Vector((X(MAN) - 0.19, -0.24, ZP))
K.key(ghost, "location", [(0, PROBE), (f_dock - 16, PROBE), (f_dock, dockq), (b5 + 20, dockq), (b5 + 36, PROBE)])
K.key(ghost, "rotation_euler", [(f_dock - 16, (0, 0, math.pi)), (f_dock, (0, 0, ang)), (b5 + 20, (0, 0, ang))])
K.key(ghost, "scale", [(0, (0.001,) * 3), (f_dock - 16, (0.001,) * 3), (f_dock - 4, (1.0,) * 3), (b5 + 26, (1.0,) * 3),
                       (b5 + 36, (0.001,) * 3)])
K.glow_keys(ghost_m, [(0, 0.0), (f_dock - 16, 4.5)])
K.key(kpr, "rotation_euler", [(f_dock - 16, (0, 0, 0)), (f_dock, (0, 0, -ang)), (b5 + 20, (0, 0, -ang)), (b5 + 36, (0, 0, 0))])
thread = K.beam("thread", dockq + Vector((0.035, 0.0, 0.0)), Vector((X(MAN) - 0.035, -0.02, ZP)), r=0.004, mat=thread_m)
K.show(thread, [(0, False), (f_dock, True), (b5 + 20, False)])
sweep0, sweep1 = f_mul + 4, f_add + 6
K.glow_keys(thread_m, [(0, 0.0), (sweep0, 0.0), (sweep0 + 6, 3.0), (sweep1 + 20, 3.0), (sweep1 + 40, 0.8)])
K.keyval(ghost_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (sweep0, 0.0), (sweep1, 1.0)])
K.keyval(kman_m.node_tree.nodes["reveal"].outputs[0], [(0, 1.0), (f_dock - 6, 1.0), (f_dock, 0.0), (sweep0, 0.0), (sweep1, 1.0)])
partial, run = [], 0.0
for a_, b_ in zip(QK["q"], QK["k"][MAN]):
    run += a_ * b_
    partial.append(run)
FULL = 80.0   # column full scale: a dot product of 80 = a score of 10
_, liq_man, lm_man = meters[MAN]
mk = [(0, 0.001), (sweep0, 0.001)]
for s in range(8):
    mk.append((pct(sweep0, sweep1, (s + 1) / 8), max(0.001, partial[8 * s + 7] / FULL)))
K.key(liq_man, "scale", [(f_, (1, 1, v)) for f_, v in mk])
K.glow_keys(lm_man, [(0, 0.0), (sweep0, 4.0)])
for i in range(N):   # every other column fills to its dot product on "score"
    if i == MAN:
        continue
    _, liq, lm = meters[i]
    lvl = max(0.001, DOT[i] / FULL)
    d = int(abs(i - LAST) * 0.25)
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (f_one - 4 + d, (1, 1, 0.001)), (f_one + 18 + d, (1, 1, lvl))])
    K.glow_keys(lm, [(0, 0.0), (f_one - 4 + d, 0.0), (f_one + 6 + d, 3.2)])
for j, (bo, bm_) in beams.items():   # each beam carries its score
    K.glow_keys(bm_, [(f_one + 6, 1.6 if j in HERO else 0.7), (f_one + 30, 0.15 + 4.5 * max(0.0, SC[j]) / SC[MAN])])

# b6: softmax. Columns become weights (a full column = 100 percent); the light is reallocated
f_soft, f_65 = w("b6", "softmax"), w("b6", "sixty-five")
for i in range(N):
    _, liq, lm = meters[i]
    lvl0, lvl1 = max(0.001, DOT[i] / FULL), max(0.001, W[i])
    d = int(abs(i - LAST) * 0.2)
    K.key(liq, "scale", [(f_soft + 6 + d, (1, 1, lvl0)), (f_soft + 40 + d, (1, 1, lvl1))])
    K.glow_keys(lm, [(f_soft + 6 + d, 3.2), (f_soft + 40 + d, 0.6 + 6.0 * (W[i] / W[MAN]) ** 0.6)])
for j, (bo, bm_) in beams.items():
    K.glow_keys(bm_, [(f_soft + 6, 0.15 + 4.5 * max(0.0, SC[j]) / SC[MAN]), (f_soft + 44, 0.02 + 9.0 * (W[j] / W[MAN]) ** 0.85)])

# b7: the values rise (columns sink), lit by their weights, and slide into one output plate in front of the row
f_val, f_step, f_add7, f_new = w("b7", "values"), w("b7", "steps"), w("b7", "added"), w("b7", "new")
for i in range(N):
    _, liq, lm = meters[i]
    K.key(liq, "scale", [(f_val - 10, (1, 1, max(0.001, W[i]))), (f_val + 6, (1, 1, 0.001))])
for i in range(N):
    pr, pm = plates[("v", i)]
    up = Vector((X(i) + DX, 0.0, ZP))
    lo = Vector((X(i) + DX, 0.0, ZH))
    d = int((LAST - i) * 0.25)
    if W[i] >= 0.012:   # the values that carry real weight travel into the output
        g = 0.5 + 7.0 * (W[i] / W[MAN]) ** 0.7
        mid = Vector((X(i) + DX, -0.35, ZP + 0.04))
        K.key(pr, "location", [(f_val - 4 + d, lo), (f_val + 14 + d, up), (f_step, up), (f_step + 24, mid), (f_add7 + 2, OUTP)])
        K.key(pr, "scale", [(f_val - 4 + d, (0.6,) * 3), (f_val + 14 + d, (1.0,) * 3), (f_add7 - 4, (0.85,) * 3),
                            (f_add7 + 4, (0.001,) * 3)])
        K.glow_keys(pm, [(f_val - 4 + d, 0.0), (f_val + 14 + d, g), (f_add7, g), (f_add7 + 4, 0.0)])
    else:               # the rest: a faint glimmer, then back into the tile
        K.key(pr, "location", [(f_val - 4 + d, lo), (f_val + 14 + d, up), (f_add7 - 20, up), (f_add7 - 4, lo)])
        K.key(pr, "scale", [(f_val - 4 + d, (0.6,) * 3), (f_val + 14 + d, (1.0,) * 3), (f_add7 - 20, (1.0,) * 3), (f_add7 - 4, (0.6,) * 3)])
        K.glow_keys(pm, [(f_val - 4 + d, 0.0), (f_val + 14 + d, 0.06 + 15 * W[i]), (f_add7 - 20, 0.06 + 15 * W[i]), (f_add7 - 4, 0.0)])
K.key(qpr, "location", [(f_val, PROBE), (f_val + 20, PROBE + Vector((-0.45, 0.1, 0)))])
K.key(outp, "scale", [(0, (0.001,) * 3), (f_add7 - 6, (0.001,) * 3), (f_add7 + 6, (1.0,) * 3)])
K.glow_keys(out_m, [(0, 0.0), (f_add7 - 6, 0.0), (f_add7 + 8, 5.5)])
K.keyval(out_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_add7, 0.0), (f_new + 20, 1.0)])
for j, (bo, bm_) in beams.items():
    K.glow_keys(bm_, [(f_val, 0.02 + 9.0 * (W[j] / W[MAN]) ** 0.85), (f_val + 24, 0.0)])
    vis = [(0, False), (f_send - 4, True), (f_dock - 18, False), (f_one - 6, True)]
    if j < BATT:   # the stores -> battery shot looks across these beams: keep them out of the lens
        vis += [(w("b5", "stores") - 12, False), (b["b6"]["f0"] - 8, True)]
    if W[j] < 0.004:
        vis.append((f_soft + 46, False))
    vis.append((f_val + 26, False))
    K.show(bo, sorted(vis))

# b8: the output docks into head 2 on floor 24; the stack assembles; the heads light, then every floor
f_pass, f_14, f_24 = w("b8", "passes"), w("b8", "fourteen"), w("b8", "twenty-four")
b8 = b["b8"]["f0"]
for ch in TW["root"].children:
    if "_post" in ch.name:
        K.show(ch, [(0, False), (b8 - 40, True)])
for k, fr in enumerate(TW["floors"], start=1):
    z = fr.location.z
    t0 = b8 - 40 + int((k - 1) * 1.2)
    K.show(fr, [(0, False), (t0, True)])
    K.key(fr, "location", [(0, (0, 0, z + 1.6)), (t0, (0, 0, z + 1.6)), (t0 + 22, (0, 0, z))])
sp = TW_W * 0.9 / 14
sock = TOWER + Vector(((2 - 6.5) * sp, -TW_D * 0.275 - 0.03, 23 * TW_PITCH + 0.09))
K.key(outp, "location", [(f_pass - 8, OUTP), (f_pass + 34, sock)])
K.key(outp, "scale", [(f_pass - 8, (1.0,) * 3), (f_pass + 34, (0.3,) * 3)])
K.glow_keys(TW["heads"][(24, 2)][1], [(0, 0.0), (f_pass + 30, 0.0), (f_pass + 40, 6.0)])
K.glow_keys(TW["idle"], [(0, 0.0), (f_14 - 4, 0.0), (f_14 + 14, 1.6), (f_24 + 30, 3.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_row", lens=40, fstop=2.2)
c1.keys([(0, (X(79) - 0.5, -1.3, 0.64), (X(82), 0.0, 0.22)),
         (f_last, (X(95.5), -1.18, 0.56), (X(98.3), 0.0, 0.24)),
         (b["b1"]["f1"] + 10, (0.72, -1.2, 0.56), (-0.5, 0.0, 0.24))])
c2 = K.Cam(sc, "c_three", lens=40, fstop=2.8).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (0.75, -1.35, 0.78), (-0.95, 0.0, 0.4)),
         (fv + 30, (0.48, -1.0, 0.64), (-0.6, 0.0, 0.41)),
         (b["b2"]["f1"] + 12, (0.2, -1.6, 0.85), (-2.2, 0.0, 0.38))])
c3 = K.Cam(sc, "c_mat", lens=42, fstop=3.2).cut(b["b3"]["f0"] - 8)
c3.keys([(b["b3"]["f0"] - 8, (-1.05, -0.62, 0.92), (0.0, 0.4, 0.44)),
         (b["b3"]["f1"] + 12, (-0.85, -0.45, 0.82), (0.0, 0.42, 0.45))])
c4 = K.Cam(sc, "c_send", lens=32, fstop=3.2).cut(b4 - 8)
c4.keys([(b4 - 8, (-0.45, -2.0, 0.74), (-1.55, -0.6, 0.42)),
         (f_dock - 20, (-0.75, -2.2, 0.82), (-2.1, -0.35, 0.4))])
c5 = K.Cam(sc, "c_dot", lens=50, fstop=2.8).cut(f_dock - 18)
c5.keys([(f_dock - 18, (X(MAN) - 0.12, -1.2, ZP + 0.1), (X(MAN) - 0.16, -0.1, ZP + 0.03)),
         (f_one - 6, (X(MAN) - 0.06, -1.05, ZP + 0.07), (X(MAN) - 0.13, -0.1, ZP + 0.03))])
c4b = K.Cam(sc, "c_all", lens=30, fstop=3.5).cut(f_one - 6)
c4b.keys([(f_one - 6, (0.75, -1.7, 0.78), (-2.8, 0.0, 0.42)), (b["b4"]["f1"] + 12, (0.55, -1.5, 0.72), (-3.4, 0.0, 0.42))])
f_s1, f_s2, f_s3, f_s4 = w("b5", "manchester"), w("b5", "system"), w("b5", "stores"), w("b5", "battery")
c6 = K.Cam(sc, "c_man", lens=50, fstop=2.4).cut(b5 - 8)
c6.keys([(b5 - 8, (X(MAN) + 0.8, -1.15, 0.66), (X(MAN) + 0.05, 0.0, 0.42)),
         (f_s2 - 14, (X(MAN) + 0.55, -0.95, 0.6), (X(MAN) + 0.05, 0.0, 0.42))])
c7 = K.Cam(sc, "c_sys", lens=50, fstop=2.4).cut(f_s2 - 12)
c7.keys([(f_s2 - 12, (X(MAN_SYS) + 0.8, -1.15, 0.66), (X(MAN_SYS) + 0.05, 0.0, 0.42)),
         (f_s3 - 14, (X(MAN_SYS) + 0.55, -0.95, 0.6), (X(MAN_SYS) + 0.05, 0.0, 0.42))])
c8 = K.Cam(sc, "c_sb", lens=45, fstop=2.8).cut(f_s3 - 12)
c8.keys([(f_s3 - 12, (X(STORES) + 0.7, -1.2, 0.66), (X(STORES), 0.0, 0.42)),
         (f_s4 + 10, (X(BATT) + 0.75, -1.25, 0.66), (X(BATT) + 0.15, 0.0, 0.42)),
         (b["b5"]["f1"] + 12, (X(BATT) + 1.1, -1.7, 0.8), (X(BATT) + 0.6, 0.0, 0.42))])
c9 = K.Cam(sc, "c_soft", lens=30, fstop=3.5).cut(b["b6"]["f0"] - 8)
c9.keys([(b["b6"]["f0"] - 8, (-0.55, -1.35, 0.74), (-3.0, 0.0, 0.42)),
         (f_65 - 30, (-0.8, -1.2, 0.7), (-2.9, 0.0, 0.44)),
         (f_65 + 12, (X(MAN) + 0.62, -0.98, 0.62), (X(MAN) + 0.08, 0.0, 0.45)),
         (b["b6"]["f1"] + 12, (X(MAN) + 0.5, -0.88, 0.6), (X(MAN) + 0.08, 0.0, 0.45))])
c10 = K.Cam(sc, "c_val", lens=36, fstop=3.2).cut(b["b7"]["f0"] - 8)
c10.keys([(b["b7"]["f0"] - 8, (0.15, -2.0, 0.85), (-2.0, -0.2, 0.42)),
          (f_add7 - 16, (-0.45, -1.85, 0.72), (-1.3, -0.5, 0.45)),
          (b["b7"]["f1"] + 12, (-0.85, -1.45, 0.58), (-1.05, -0.82, ZP + 0.04))])
c11 = K.Cam(sc, "c_up", lens=38, fstop=3.2).cut(b8 - 8)
top = TOWER + Vector((0, 0, 23 * TW_PITCH))
c11.keys([(b8 - 8, (-0.3, -1.9, 0.85), (-0.6, -0.4, 0.6)),
          (f_pass + 36, (top.x + 0.2, top.y - 1.35, top.z + 0.35), (top.x - 0.35, top.y, top.z + 0.02)),
          (f_14 + 30, (top.x + 0.7, top.y - 1.7, top.z + 0.25), (top.x - 0.1, top.y, top.z - 0.15)),
          (END, (top.x + 1.4, top.y - 2.6, top.z + 0.1), (top.x - 0.1, top.y, top.z - 0.45))])

# ------------------------------------------------------------------------------------------------ pins
pins = ["tok%d_top" % i for i in list(range(78, N)) + [MAN_SYS]] + ["tok%d_front" % i for i in list(range(78, N)) + [MAN_SYS]]
pins += [f"{k}{LAST}_top" for k in "qkv"] + ["slab_top", "wq_top", "wk_top", "wv_top", "ghostq_top", "k92_top",
                                              "outp_top", "tower_pin_f24", "q99_mid", "k92_mid"]
pins += [f"m{i}_top" for i in (MAN, MAN_SYS, STORES, BATT, PACKS, LAST, 82, 89, 94)]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
