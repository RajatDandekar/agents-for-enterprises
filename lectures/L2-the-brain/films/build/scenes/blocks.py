"""Film "blocks": "Inside the stack: every token, 24 blocks" (Lecture 2, section 5a). Replaces structure + s5_blocks.

Emma's 100 tokens as tiles on the plinth; each becomes a column (first 16 of its 896 numbers, real: build/data/
structure_data.json, one atlas layer per block output). Above them, the stack as a building: 24 floors that each span
all 100 positions (attention band with 14 head lanes over an MLP band with one module behind every position).
Block 1 opens: attention arcs (real head-averaged block-1 weights, build/data/blocks_data.json avg_mats), the causal
glass, the MLP sweep (each column alone) with the last column's real 896 -> 4,864 -> 896 numbers; every column changes
(layer swap wipes across the row) and climbs through 24 floors. At the top only the last column is read out; arcs from
it show why the other 99 matter (real block 24 average, block 24 head 2, block 19 head 13: heads_data.json); the
logit-lens eyepieces light floor by floor (2D ladder in specs/blocks.py). Ends on all 24 x 14 head lanes.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_blocks_heads as PB  # noqa: E402
import props_s456 as P4  # noqa: E402

FILM = "blocks"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
N = len(TOK)
SD = K.load("films/build/data/structure_data.json")["layers"]        # 25 x 100 x 16
BD = K.load("films/build/data/blocks_data.json")
HD = K.load("films/build/data/heads_data.json")
HEADS = {(h["block"], h["head"]): h for h in HD["heads"]}
X = PB.X
PZ = PB.PZ
LAST, MAN, BATT, PACKS, STORES = 99, 92, 86, 87, 93
YC = 0.2                     # the columns stand just behind the tiles

sc = K.reset(B.frames)
K.studio(sc, focus=(-3.0, 0.0, 1.2), key_power=3400, span=30.0)
K.soft_light("hikey", (-6.0, -9.0, 27.2 + 5.0), (-4.0, 0.0, 27.2 - 1.0), 2600, 14.0, (1.0, 0.97, 0.93))
K.soft_light("hirim", (-3.0, 7.0, 27.2 + 3.0), (-3.0, 0.0, 27.2), 1800, 14.0, (0.7, 0.82, 1.0))
K.soft_light("midkey", (-14.0, -18.0, 14.0), (-14.0, 0.0, 13.0), 6000, 24.0, (1.0, 0.97, 0.93))
K.plinth("plinth", X(0) - 0.45, 0.62, depth=0.5, height=PZ)
tiles = {}
for t in TOK:
    tiles[t["i"]] = K.token_tile(f"tok{t['i']}", t["role"], (X(t["i"]), 0, PZ))
FAC = PB.facade("fac", floors=24, z1=1.0, fp=1.05)
PB.backdrop("backdrop", -17.0, 7.0, 6.0, 70.0, 140.0, fade=0.22)   # deep slate behind the upper floors (no black void)
ZA, ZM, TOP = FAC["za"], FAC["zm"], FAC["top"]
ROW = PB.column_row("col", range(N), SD, nrow=16, cell=0.045, y=YC, z=0.0, glow=3.8)
for m_ in FAC["lane"]:   # the head lanes glow softly, so the columns stay the subject
    K.bsdf(m_).inputs["Emission Color"].default_value = tuple(c * 0.38 for c in K.SKY[:3]) + (1,)
car, CM, HC = ROW["car"], ROW["mat"], ROW["h"]
Z0 = PZ + 0.075 + 0.04 + HC / 2          # standing behind the tiles
ZTOP_ROW = ZM[23]

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in [f"b{i}" for i in range(1, 11)]}
w = B.w
END = B.frames - 1
nodes = CM.node_tree.nodes


def nv(name):
    return nodes[name].outputs[0]


# b1: the tiles. The system prompt lights as a wave on "instructions"; Emma's words light one by one as they are spoken
f_ins, f_q = w("b1", "instructions"), w("b1", "question")
QW = [(80, "how"), (81, "many"), (82, "city"), (83, "e-bike"), (84, "e-bike"), (85, "e-bike"), (86, "battery"), (87, "packs"),
      (88, "do"), (89, "we"), (90, "have"), (91, "in"), (92, "manchester"), (93, "stores"), (94, "stores")]
f_cols = w("b2", "column")
for t in TOK:
    i = t["i"]
    fm = tiles[i][1]
    if t["role"] == "system":
        d = f_ins + int(i * 0.35)
        K.glow_keys(fm, [(0, 0.0), (d - 4, 0.0), (d + 6, 1.3), (f_q + 6, 0.35), (f_cols + 40, 0.35), (f_cols + 70, 0.0)])
    elif t["role"] == "template":
        d = f_ins + int(i * 0.35)
        K.glow_keys(fm, [(0, 0.0), (d - 4, 0.0), (d + 6, 0.9), (f_q + 6, 0.25), (f_cols + 70, 0.0)])
for k, (i, wd) in enumerate(QW):
    f = w("b1", wd) + (2 * (i - 83) if 83 <= i <= 85 else 0) + (6 if i == 94 else 0)
    K.glow_keys(tiles[i][1], [(0, 0.0), (f - 3, 0.0), (f + 5, 3.0), (f + 30, 1.6), (f_cols + 70, 1.6), (f_cols + 100, 0.0)])

# b2: the columns rise out of the plinth behind their tiles, right to left
K.key(car, "location", [(0, (0, YC, Z0 - 0.95)), (f_cols - 4, (0, YC, Z0 - 0.95)), (f_cols + 34, (0, YC, Z0))])
K.show(car, [(0, False), (f_cols - 6, True)])
K.glow_keys(CM, [(0, 0.0), (f_cols, 0.0), (f_cols + 30, 3.8)])
PB.set_layer(CM, [(0, 0)])
K.keyval(nv("layerB"), [(0, 1.0)])

# b3: the stack lights, floor by floor, on "twenty-four"; the row rises to floor 1 on "first"
f24 = w("b3", "twenty-four")
for k in range(24):
    K.glow_keys(FAC["lane"][k], [(0, 0.0), (f24 + k * 2, 0.0), (f24 + k * 2 + 6, 3.0), (f24 + k * 2 + 26, 0.5)])
    K.glow_keys(FAC["mlp"][k], [(0, 0.0), (f24 + k * 2 + 2, 0.0), (f24 + k * 2 + 8, 2.4), (f24 + k * 2 + 28, 0.4)])
f_open = w("b3", "open")
f_first = w("b3", "first")
K.key(car, "location", [(f_open, (0, YC, Z0)), (f_first + 30, (0, YC, ZA[0]))])

# b4: attention in block 1
f_att, f_14 = w("b4", "attention"), w("b4", "fourteen")
f_every, f_mix = w("b4", "every"), w("b4", "mixes")
f_bat, f_never, f_packs = w("b4", "battery"), w("b4", "never"), w("b4", "packs")
f_man, f_lastp = w("b4", "manchester"), w("b4", "last")
f_mlp = w("b5", "mlp")
L1 = FAC["lane"][0]
K.glow_keys(L1, [(f_att - 6, 0.5), (f_att + 8, 2.4), (f_14, 2.4), (f_14 + 6, 5.0), (f_14 + 20, 1.4), (f_mlp, 1.4), (f_mlp + 14, 0.6)])
# "every position": a wave of light runs along the row
K.keyval(nv("fx"), [(0, -1000.0), (f_every - 1, -1000.0), (f_every, X(70)), (f_mix + 6, 0.8), (f_mix + 7, -1000.0)])
K.keyval(nv("flash"), [(0, 0.0), (f_every, 0.0), (f_every + 6, 1.6), (f_mix, 1.6), (f_mix + 7, 0.0)])
A1 = BD["avg_mats"]["1"]
ztop1 = ZA[0] + HC / 2 + 0.03


def colpt(j, z):
    return Vector((X(j), YC, z))


A_BAT = PB.arc_set("ab", colpt(BATT, ztop1), lambda j: colpt(j, ztop1), {j: A1[BATT][j] for j in range(BATT)}, K.SKY, min_w=0.008, ref=0.15)
A_MAN = PB.arc_set("am", colpt(MAN, ztop1), lambda j: colpt(j, ztop1), {j: A1[MAN][j] for j in range(MAN)}, K.SKY, min_w=0.008, ref=0.15)
A_LAST = PB.arc_set("al", colpt(LAST, ztop1), lambda j: colpt(j, ztop1), {j: A1[LAST][j] for j in range(LAST)}, K.SKY, min_w=0.006, ref=0.15)
# Manchester -> battery highlighted (warm), always drawn
mb_m = K.light_mat("mb_m", K.lin("#ffe2a8"), 0.0)
mb = K.arc("mb", colpt(MAN, ztop1 + 0.01), colpt(BATT, ztop1 + 0.01), lift=0.45, r=0.012, mat=mb_m)
PB.light_arcs(A_BAT, f_bat - 2, f_man - 8, BATT, ref=0.15, stagger=0.15)
PB.light_arcs(A_MAN, f_man - 2, f_lastp - 8, MAN, ref=0.15, stagger=0.15)
PB.light_arcs(A_LAST, f_lastp - 2, f_mlp - 6, LAST, ref=0.15, stagger=0.08)
K.grow(mb, [(0, 0.0), (f_man + 6, 0.0), (f_man + 24, 1.0)])
K.glow_keys(mb_m, [(0, 0.0), (f_man + 6, 0.0), (f_man + 12, 6.0), (f_lastp - 8, 6.0), (f_lastp + 6, 0.0)])
K.show(mb, [(0, False), (f_man + 4, True), (f_lastp + 8, False)])
# the causal glass after battery; a look forward to packs is stopped by it
wall, wall_edge = P4.glass_wall("wall", (X(BATT) + 0.18, YC, ZA[0] + 3.0), w=0.62, h=1.1)
wz0, wz1 = ZA[0] + 3.0, ZA[0] - HC / 2 - 0.05
K.key(wall, "location", [(0, (wall.location.x, YC, wz0)), (f_never - 10, (wall.location.x, YC, wz0)), (f_never + 14, (wall.location.x, YC, wz1)),
                         (f_man - 4, (wall.location.x, YC, wz1)), (f_man + 16, (wall.location.x, YC, wz0))])
K.show(wall, [(0, False), (f_never - 12, True), (f_man + 18, False)])
K.glow_keys(wall_edge, [(0, 0.0), (f_never + 10, 0.0), (f_never + 18, 3.5), (f_man, 3.5), (f_man + 10, 0.0)])
blk_m = K.light_mat("blocked_m", K.lin("#9ec7ff"), 0.0)
blocked = K.arc("blocked", colpt(BATT, ztop1), colpt(PACKS, ztop1), lift=0.22, r=0.007, mat=blk_m)
K.grow(blocked, [(0, 0.0), (f_packs - 2, 0.0), (f_packs + 10, 0.4), (f_packs + 26, 0.4), (f_packs + 38, 0.0)])
K.glow_keys(blk_m, [(0, 0.0), (f_packs - 2, 0.0), (f_packs + 6, 4.5), (f_packs + 28, 4.5), (f_packs + 38, 0.0)])
K.show(blocked, [(0, False), (f_packs - 4, True), (f_packs + 40, False)])

# b5: the MLP: the row steps up to the MLP band; a sweep passes every column one by one; the last column's real
# 896 -> 4,864 -> 896 numbers (blocks_data last_vecs["1"], mlp_mid_last["1"]) float above it
f_each, f_wid, f_four, f_sq, f_here = w("b5", "each"), w("b5", "widens"), w("b5", "four"), w("b5", "squeezes"), w("b5", "here")
K.key(car, "location", [(f_mlp - 6, (0, YC, ZA[0])), (f_mlp + 18, (0, YC, ZM[0]))])
M1 = FAC["mlp"][0]
mn = M1.node_tree.nodes
K.glow_keys(M1, [(f_mlp - 4, 0.4), (f_mlp + 10, 1.4)])
sx_keys = [(0, -1000.0), (f_each - 1, -1000.0), (f_each, X(0) - 0.6), (f_each + 40, X(76)), (f_here + 10, 0.9), (b["b5"]["f1"] + 12, 0.9)]
K.keyval(mn["sx"].outputs[0], sx_keys)
K.keyval(mn["flash"].outputs[0], [(0, 0.0), (f_each, 0.0), (f_each + 6, 7.0), (f_here + 10, 7.0), (f_here + 20, 0.0)])
K.keyval(mn["done"].outputs[0], [(0, 0.0), (f_each, 0.0), (f_each + 6, 1.4), (b["b6"]["f0"] + 20, 1.4), (b["b6"]["f0"] + 40, 0.3)])
K.keyval(nv("fx"), [(f_each - 1, -1000.0), (f_each, X(0) - 0.6), (f_each + 40, X(76)), (f_here + 10, 0.9), (f_here + 11, -1000.0)])
K.keyval(nv("flash"), [(f_each - 1, 0.0), (f_each, 0.0), (f_each + 6, 1.8), (f_here + 10, 1.8), (f_here + 12, 0.0)])
LV, MID = BD["last_vecs"]["1"], BD["mlp_mid_last"]["1"]


def p95(v):
    a = sorted(abs(x) for x in v)
    return a[int(len(a) * 0.95)] or 1.0


PX, PZP = -0.75, ZM[0] + HC / 2 + 0.55
pin_, pin_m = K.vector_plate("pin", LV["after_attention"], 28, 32, K.SKY, (PX, YC - 0.25, PZP), cell=0.013, vmax=p95(LV["after_attention"]), glow=4.0)
pwide, pwide_m = K.vector_plate("pwide", MID, 152, 32, K.lin("#ffd79a"), (PX, YC - 0.25, PZP), cell=0.013, vmax=p95(MID), glow=4.0)
pout, pout_m = K.vector_plate("pout", LV["out"], 28, 32, K.SKY, (PX, YC - 0.25, PZP), cell=0.013, vmax=p95(LV["out"]), glow=4.0)
K.show(pin_, [(0, False), (f_wid - 4, True), (f_four + 4, False)])
K.key(pin_, "scale", [(f_wid - 4, (0.05, 1, 0.05)), (f_wid + 10, (1, 1, 1)), (f_four - 2, (1, 1, 1)), (f_four + 4, (0.6, 1, 1))])
K.show(pwide, [(0, False), (f_four - 2, True), (f_sq + 12, False)])
K.key(pwide, "scale", [(f_four - 2, (28 / 152, 1, 1)), (f_four + 20, (1, 1, 1)), (f_sq, (1, 1, 1)), (f_sq + 12, (28 / 152, 1, 1))])
K.show(pout, [(0, False), (f_sq + 10, True), (f_here + 24, False)])
K.key(pout, "scale", [(f_sq + 10, (1, 1, 1)), (f_here + 6, (1, 1, 1)), (f_here + 24, (0.05, 1, 0.05))])
K.key(pout, "location", [(f_here + 6, (PX, YC - 0.25, PZP)), (f_here + 24, (X(LAST), YC - 0.05, ZM[0] + 0.1))])
cable_m = K.light_mat("cable_m", K.SKY, 0.0)
cable = K.beam("cable", (X(LAST), YC - 0.05, ZM[0] + HC / 2 + 0.04), (PX + 0.2, YC - 0.25, PZP - 0.23), r=0.004, mat=cable_m)
K.show(cable, [(0, False), (f_wid - 6, True), (f_here + 26, False)])
K.glow_keys(cable_m, [(0, 0.0), (f_wid - 4, 0.0), (f_wid + 6, 3.0), (f_here + 10, 3.0), (f_here + 24, 0.0)])
K.keyval(nv("hl"), [(0, 0.0), (f_wid - 4, 0.0), (f_wid + 6, 1.5), (f_here + 20, 1.5), (f_here + 30, 0.0)])
K.keyval(nv("hlc"), [(0, 99.0)])

# b6: every column changes (layer 0 -> 1 wipes across the row), then all 100 climb, block by block
f_out, f_chg, f_climb = w("b6", "out"), w("b6", "changed"), w("b6", "climb")
f_ag1, f_ag2, f_way = w("b6", "again", 0), w("b6", "again", 1), w("b6", "way")
K.keyval(nv("wipe"), [(0, -1000.0), (f_chg - 1, -1000.0), (f_chg, X(0) - 0.8), (f_chg + 22, 1.0), (f_chg + 23, -1000.0)])
F = {2: f_climb + 8, 3: f_ag1, 4: f_ag2}
f24e = b["b6"]["f1"] + 70
for k in range(5, 25):
    F[k] = int(f_ag2 + 16 + (f24e - f_ag2 - 16) * (k - 5) / 19)
layers = [(0, 0), (f_chg + 23, 1)]
locs = [(f_out - 4, (0, YC, ZM[0])), (f_climb - 2, (0, YC, ZM[0]))]
for k in range(2, 25):
    nxt = F[k + 1] if k < 24 else F[k] + 20
    d1 = max(3, min(12, (nxt - F[k]) // 2))
    locs += [(F[k], (0, YC, ZA[k - 1])), (F[k] + d1, (0, YC, ZM[k - 1]))]
    layers.append((F[k] + d1, k))
    K.glow_keys(FAC["lane"][k - 1], [(F[k] - 4, 0.5), (F[k], 5.0), (F[k] + 16, 1.2)])
    K.keyval(FAC["mlp"][k - 1].node_tree.nodes["glow"].outputs[0], [(F[k] + d1 - 3, 0.4), (F[k] + d1, 4.5), (F[k] + d1 + 16, 1.0)])
PB.set_layer(CM, layers)
# b7: the row stands at the top; only the last column is read out
f_top, f_just, f_lastc, f_scores = w("b7", "top"), w("b7", "just"), w("b7", "last"), w("b7", "scores")
locs += [(f_top - 10, (0, YC, ZM[23]))]
K.key(car, "location", locs)
K.keyval(nv("focus"), [(0, 0.0), (f_just, 0.0), (f_lastc + 4, 1.0)])
lastroot = ROW["roots"][LAST]
K.key(lastroot, "location", [(0, (X(LAST), 0, 0)), (f_lastc, (X(LAST), 0, 0)), (f_lastc + 20, (X(LAST), -0.25, 0.45))])
sc_m = K.light_mat("scores_m", K.SKY, 0.0)
sbeam = K.beam("scorebeam", (X(LAST), YC - 0.25, ZTOP_ROW + 0.45 + HC / 2 + 0.03), (X(LAST), YC - 0.25, ZTOP_ROW + 2.6), r=0.02, mat=sc_m)
K.key(sbeam, "scale", [(0, (1, 1, 0.001)), (f_scores - 2, (1, 1, 0.001)), (f_scores + 20, (1, 1, 1))])
K.glow_keys(sc_m, [(0, 0.0), (f_scores - 2, 0.0), (f_scores + 6, 5.0), (b["b7"]["f1"] + 10, 5.0), (b["b7"]["f1"] + 26, 0.0)])
K.show(sbeam, [(0, False), (f_scores - 4, True), (b["b7"]["f1"] + 28, False)])

# b8: why the other 99 matter: they light again; the last column reads them (real arcs at the top)
f_other, f_reads, f_emma = w("b8", "other"), w("b8", "reads"), w("b8", "emma's")
f_65, f_19, f_without, f_nothing = w("b8", "sixty-five"), w("b8", "nineteen"), w("b8", "without"), w("b8", "nothing")
K.keyval(nv("focus"), [(f_other - 2, 1.0), (f_other + 14, 0.0), (f_without, 0.0), (f_without + 14, 1.0), (b["b9"]["f0"] - 10, 1.0),
                       (b["b9"]["f0"] + 10, 0.55)])
K.key(lastroot, "location", [(f_other - 2, (X(LAST), -0.25, 0.45)), (f_other + 18, (X(LAST), 0, 0))])
zt = ZTOP_ROW + HC / 2 + 0.03
A24 = BD["avg_mats"]["24"][LAST]
A_T = PB.arc_set("at", colpt(LAST, zt), lambda j: colpt(j, zt), {j: A24[j] for j in range(LAST)}, K.SKY, min_w=0.006, ref=0.25)
H242 = HEADS[(24, 2)]
H1913 = HEADS[(19, 13)]
R242 = HD["mats"]["24.2"][LAST]
R1913 = HD["mats"]["19.13"][LAST]
A_H1 = PB.arc_set("ah", colpt(LAST, zt), lambda j: colpt(j, zt), {j: R242[j] for j in range(LAST)}, K.SKY, min_w=0.006, ref=0.35)
A_H2 = PB.arc_set("ag", colpt(LAST, zt), lambda j: colpt(j, zt), {j: R1913[j] for j in range(LAST)}, K.K_COL, min_w=0.006, ref=0.35)
PB.light_arcs(A_T, f_reads - 2, f_65 - 10, LAST, ref=0.25, stagger=0.08)
PB.light_arcs(A_H1, f_65 - 4, f_19 - 8, LAST, ref=0.35, stagger=0.08)
PB.light_arcs(A_H2, f_19 - 4, f_without + 6, LAST, ref=0.35, stagger=0.08, fade=20)

# b9: the logit lens: the eyepieces light floor by floor
f_ask, f_for, f_noise = w("b9", "ask"), w("b9", "for"), w("b9", "noise")
f18, f22, f23, f24b = w("b9", "eighteen"), w("b9", "eight"), w("b9", "twenty-nine"), w("b9", "fifty-six")
LF = {1: f_ask, 2: f_ask + 8, 3: f_ask + 16}
for k in range(4, 18):
    LF[k] = int(f_for + (f_noise + 10 - f_for) * (k - 4) / 13)
LF[18] = f18
LF[19], LF[20], LF[21] = f18 + 20, f18 + 40, f18 + 60
LF[22], LF[23], LF[24] = f22, f23, f24b
for k in range(1, 25):
    K.glow_keys(FAC["lens"][k - 1], [(0, 0.0), (LF[k] - 3, 0.0), (LF[k] + 2, 9.0 if k >= 22 else 6.0), (LF[k] + 22, 3.0 if k >= 22 else 2.0)])
# the answer token rises over the last column at the end of the ladder
wtile, wface = K.token_tile("we", "user", (X(LAST), YC - 0.3, ZTOP_ROW + HC / 2 + 0.5), size=(0.42, 0.3, 0.09))
wz = wtile.location.z
K.show(wtile, [(0, False), (f24b - 8, True)])
K.key(wtile, "location", [(f24b - 8, (X(LAST), YC - 0.3, wz - 0.25)), (f24b + 16, (X(LAST), YC - 0.3, wz + 0.05))])
K.glow_keys(wface, [(0, 0.0), (f24b, 0.0), (f24b + 16, 3.6)])

# b10: all 24 x 14 head lanes light, bottom to top
f_every2 = w("b10", "every")
for k in range(24):
    K.glow_keys(FAC["lane"][k], [(f_every2 + k * 2 - 4, 1.2), (f_every2 + k * 2 + 6, 5.0), (END, 3.4)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_tiles", lens=35, fstop=2.8).cut(0)
f_how = w("b1", "how")
c1.keys([(0, (X(55), -2.6, 1.35), (X(64), 0.0, 0.2)),
         (f_q - 10, (X(72), -2.2, 1.05), (X(80), 0.0, 0.18)),
         (f_how + 6, (X(82), -1.85, 0.85), (X(83.5), 0.0, 0.15)),
         (w("b1", "manchester") + 12, (X(89.5), -1.85, 0.85), (X(91), 0.0, 0.15)),
         (b["b1"]["f1"] + 20, (X(90.5), -1.95, 0.9), (X(91.5), 0.0, 0.16))])
c2 = K.Cam(sc, "c_cols", lens=35, fstop=3.2).cut(b["b2"]["f0"] - 4)
c2.keys([(b["b2"]["f0"] - 4, (X(91), -2.3, 1.05), (X(91.5), YC, 0.4)),
         (w("b2", "side"), (X(88), -3.6, 1.5), (X(88), YC, 0.5)),
         (b["b2"]["f1"] + 22, (X(84), -5.4, 2.2), (X(84), YC, 0.9))])
c3 = K.Cam(sc, "c_wide", lens=30, fstop=8.0).cut(b["b3"]["f0"] - 6)
c3.keys([(b["b3"]["f0"] - 6, (X(60), -40.0, 5.0), (X(50), 0.4, 11.5)),
         (f_open - 4, (X(54), -46.0, 8.0), (X(50), 0.4, 13.0))])
c4 = K.Cam(sc, "c_open", lens=32, fstop=4.0).cut(f_open - 2)
c4.keys([(f_open - 2, (X(70), -14.0, 4.5), (X(80), 0.3, 1.6)),
         (f_first + 34, (X(89), -2.9, ZA[0] + 0.7), (X(90), 0.2, ZA[0] + 0.15)),
         (f_14 + 20, (X(90), -2.8, ZA[0] + 0.65), (X(90.5), 0.2, ZA[0] + 0.2)),
         (f_bat - 6, (X(85.5), -3.4, ZA[0] + 0.95), (X(84), 0.2, ZA[0] + 0.3)),
         (f_man - 6, (X(88.5), -3.4, ZA[0] + 0.95), (X(87.5), 0.2, ZA[0] + 0.3)),
         (f_lastp, (X(88), -6.0, ZA[0] + 1.8), (X(82), 0.2, ZA[0] + 0.5)),
         (f_mlp - 8, (X(66), -24.0, ZA[0] + 6.0), (X(56), 0.3, ZA[0] + 1.0))])
c5 = K.Cam(sc, "c_mlp", lens=32, fstop=4.0).cut(f_mlp - 4)
c5.keys([(f_mlp - 4, (X(84), -4.0, ZM[0] + 1.0), (X(86), 0.3, ZM[0] + 0.3)),
         (f_wid - 10, (X(93), -3.7, ZM[0] + 1.0), (X(95.5), 0.3, ZM[0] + 0.55)),
         (f_here + 10, (X(94), -3.5, ZM[0] + 0.95), (X(96), 0.3, ZM[0] + 0.5)),
         (b["b5"]["f1"] + 20, (X(90), -4.2, ZM[0] + 1.0), (X(91), 0.3, ZM[0] + 0.3))])
c6 = K.Cam(sc, "c_climb", lens=30, fstop=5.6).cut(b["b6"]["f0"] - 4)
c6.keys([(b["b6"]["f0"] - 4, (X(84), -6.5, ZM[0] + 1.6), (X(80), 0.3, ZM[0] + 0.3)),
         (f_chg + 24, (X(80), -9.5, ZM[0] + 2.4), (X(74), 0.3, ZM[0] + 0.6)),
         (F[4], (X(74), -14.0, ZA[3] + 2.0), (X(66), 0.3, ZA[3] + 0.4)),
         (F[12], (X(62), -30.0, ZA[11] + 2.0), (X(52), 0.4, ZA[11])),
         (F[24], (X(58), -38.0, ZA[23] - 2.0), (X(50), 0.4, ZA[16]))])
c7 = K.Cam(sc, "c_top", lens=32, fstop=4.5).cut(b["b7"]["f0"] - 6)
c7.keys([(b["b7"]["f0"] - 6, (X(82), -8.0, ZTOP_ROW + 4.2), (X(85), 0.3, ZTOP_ROW - 0.9)),
         (f_lastc, (X(90), -5.2, ZTOP_ROW + 3.0), (X(93), 0.3, ZTOP_ROW - 0.5)),
         (b["b7"]["f1"] + 10, (X(92), -5.4, ZTOP_ROW + 3.2), (X(95), 0.3, ZTOP_ROW - 0.2))])
c8 = K.Cam(sc, "c_why", lens=30, fstop=4.5).cut(b["b8"]["f0"] - 6)
c8.keys([(b["b8"]["f0"] - 6, (X(86), -7.0, ZTOP_ROW + 4.0), (X(88), 0.3, ZTOP_ROW - 0.6)),
         (f_reads, (X(78), -12.0, ZTOP_ROW + 6.0), (X(76), 0.3, ZTOP_ROW - 0.8)),
         (f_65, (X(88), -6.8, ZTOP_ROW + 3.8), (X(91), 0.3, ZTOP_ROW - 0.5)),
         (f_without, (X(86), -7.6, ZTOP_ROW + 4.0), (X(88), 0.3, ZTOP_ROW - 0.5)),
         (b["b8"]["f1"] + 10, (X(84), -8.4, ZTOP_ROW + 4.2), (X(86), 0.3, ZTOP_ROW - 0.5))])
c9 = K.Cam(sc, "c_lens", lens=32, fstop=4.0).cut(b["b9"]["f0"] - 6)
xl = 0.74
c9.keys([(b["b9"]["f0"] - 6, (-0.3, -2.5, ZA[0] + 0.55), (1.5, 0.2, ZA[0] + 0.25)),
         (LF[4], (-0.3, -2.5, ZA[3] + 0.55), (1.5, 0.2, ZA[3] + 0.25))] +
        [(LF[k], (-0.3, -2.5, ZA[k - 1] + 0.55), (1.5, 0.2, ZA[k - 1] + 0.25)) for k in (10, 17, 18, 21, 22, 23)] +
        [(LF[24], (-0.4, -2.7, ZA[23] + 0.7), (1.4, 0.2, ZA[23] + 0.4)),
         (b["b9"]["f1"] + 20, (-1.2, -4.0, ZA[23] + 1.4), (0.9, 0.2, ZA[23] + 0.9))])
c10 = K.Cam(sc, "c_end", lens=30, fstop=8.0).cut(b["b10"]["f0"] - 6)
c10.keys([(b["b10"]["f0"] - 6, (X(70), -24.0, 18.0), (X(60), 0.4, 15.0)), (END, (X(48), -42.0, 10.0), (X(50), 0.4, 13.0))])

pins = [f"tok{i}_top" for i in range(N)] + [f"tok{i}_front" for i in range(N)]
pins += [f"col{i}_{s}" for i in (0, 21, 80, 82, 86, 92, 93, 99) for s in ("top", "bot", "mid")]
pins += ["fac_att1", "fac_mlp1", "pin_top", "pwide_top", "pout_top", "we_top", "we_front", "wall_top"]
pins += [f"fac_lens{k}" for k in range(1, 25)] + [f"fac_left{k}" for k in (1, 6, 12, 18, 24)]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
