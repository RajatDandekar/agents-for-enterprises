"""Film "finale" (v5, 31 Oct): "The whole machine". Plays after section 8, before section 9. Builds finale.blend.

One continuous journey of Emma's question through the entire model, in nine stages:
  1 her chat (2D) is cut into 100 tokens that fly into 100 tiles on the plinth;
  2 every tile looks up its row in the embedding table (a long rack behind the strip) and a column of all 896 real
    input-embedding numbers stands behind it (16 x 56 cells);
  3 the columns stream into block 1 of the 24-floor stack as one row (first 16 numbers each, real); q/k/v; light arcs
    with block 1's real attention (averaged over 14 heads); the MLP; the row comes out changed (real values);
  4 the 14 heads of a block light one by one; back on the strip, block 24 head 2 puts 65.2% on Manchester and block 12
    head 13 sends all its weight 36 m back to the first tile;
  5 the row climbs all 24 blocks (real values after every block); the KV-cache shelves beside the stack fill; the stack
    (494,032,768 learnt numbers);
  6 the last column (real 896 numbers after block 24) comes down to the same table, sweeps it, six meters rise
    (We 56.4%) and "We" drops onto the strip;
  7 the loop: We's column climbs alone, reading the KV cache; currently, have, space;
  8 the digits 1 0 0 and the rest of the answer, to <|im_end|>;
  9 a wide view of the whole machine; 100 against Ledgerline's 5,400; "Why?".

Numbers: brain3d/trace.json, films/qkv_data.json, build/data/structure_data.json, build/data/finale_data.json.
The 2D schedule is shared with specs/finale.py (sched).
"""
import math
import os
import sys

BUILD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BUILD, "kit"))
sys.path.insert(0, os.path.join(BUILD, "specs"))
sys.path.insert(0, BUILD)
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_finale as PF  # noqa: E402
import props_s456 as P4  # noqa: E402
import props_s789 as P7  # noqa: E402
import finale as SP  # noqa: E402  (specs/finale.py: the shared schedule)

FILM = "finale"
B = K.Beats(FILM)
S = SP.sched(B.tl)
T = K.load("brain3d/trace.json")
D = K.load("films/qkv_data.json")
FD = K.load("films/build/data/finale_data.json")
SD = K.load("films/build/data/structure_data.json")["layers"]
TOK = T["tokens"]
G = T["generation"]["greedy"]
TOP6 = T["final"]["last"]["1.0"][:6]
W24 = D["qkv"]["weights"]
H12 = {(h["layer"], h["head"]): h for h in T["attention"]["heads"]}[(12, 13)]["row_last"]
LENS = D["vectors"]["lens_last"][23]
A1 = FD["att1_avg"]
END = B.frames - 1
PITCH, PZ = 0.36, 0.11
NT = 100
DIG = {4, 5, 6}


def X(i):
    return (i - 99) * PITCH


sc = K.reset(B.frames)
K.studio(sc, focus=(0.8, 0.6, 0.9), key_power=3200, span=16.0)
BK = PF.Book()

# ------------------------------------------------------------------------------------------------ the strip
K.plinth("plinth", X(0) - 0.45, X(119) + 0.5, depth=0.5, height=PZ)
faces = {}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    faces[i] = fm
    li = S["land_i"][i]
    rest = 0.1 if t["role"] != "user" else 0.16
    BK.set_base(fm, [(0, 0.0), (li - 2, 0.0), (li + 4, 1.8 if i >= 80 else 1.2), (li + 26, rest)])
BK.pulse(faces[92], S["man"] + 160, 2.4, rise=4, hold=10, fall=30)       # after the landing, Manchester answers its name
for i in (44, 45, 48, 49, 50, 51):
    BK.pulse(faces[i], S["land_i"][i] + 30, 1.4, hold=8, fall=24)

# ------------------------------------------------------------------------------------------------ the embedding table
RY = 1.0
RX0 = X(99) + 0.35
rack, rack_m = P4.vocab_rack("rack", RX0, X(0) - 0.35, y=RY, z0=0.0, h=0.95, depth=0.42, pitch=0.026)
rack_front = bpy.data.materials["rack_front"]
K.empty("rack_pin2", (X(97) - RX0, -0.25, 1.0), parent=rack)


def rack_keys(node, keys):
    for m in (rack_m, rack_front):
        K.keyval(m.node_tree.nodes[node].outputs[0], keys)


s0, s1 = S["rows_sweep"]
sw = [(0, 1.0), (S["table"] - 4, 1.0), (s0, 0.4), (s1 + 20, -30.0), (S["same"] + 6, -30.0), (S["same"] + 8, 0.6),
      (S["softmax"] + 4, -9.0), (S["ran"] + 2, -9.0), (S["ran"] + 4, 0.6), (S["ran"] + 70, -30.0)]
rack_keys("sweep", sw)
rack_keys("glow", [(0, 0.0), (S["table"] - 6, 0.0), (S["table"] + 10, 3.2), (s1 + 30, 3.2), (s1 + 50, 0.0),
                   (S["same"] - 4, 0.0), (S["same"] + 10, 4.0), (S["softmax"] + 10, 4.0), (S["softmax"] + 30, 0.0),
                   (S["ran"], 0.0), (S["ran"] + 8, 3.4), (S["ran"] + 70, 3.4), (S["ran"] + 90, 0.0)])

# lookups: a row of the table lights behind each tile, and the tile's column of 896 real numbers comes forward
CC, CR, CELL = 16, 56, 0.0085
CW, CH = CC * CELL, CR * CELL
CY = 0.3
CZ = PZ + 0.12 + CH / 2
cols, colm = {}, {}
for i in range(NT):
    f0 = S["look_i"][i]
    bar, bm = PF.light_bar(f"look{i}", (0.03, 0.01, 0.8), (X(i) - RX0, -0.215, 0.47), K.SKY, parent=rack)
    K.glow_keys(bm, [(0, 0.0), (f0 - 2, 0.0), (f0 + 3, 6.0), (f0 + 22, 0.6), (f0 + 60, 0.0)])
    pr, pm = K.vector_plate(f"col{i}", FD["emb"][str(i)], CC, CR, K.SKY, (X(i), RY - 0.3, CZ), cell=CELL, vmax=0.045, glow=0.0)
    cols[i], colm[i] = pr, pm
    K.key(pr, "location", [(0, (X(i), RY - 0.25, CZ)), (f0 + 2, (X(i), RY - 0.25, CZ)), (f0 + 26, (X(i), CY, CZ))])
    K.key(pr, "scale", [(0, (0.3,) * 3), (f0 + 2, (0.3,) * 3), (f0 + 22, (1.0,) * 3)])
    BK.set_base(pm, [(0, 0.0), (f0 + 2, 0.0), (f0 + 14, 3.6), (f0 + 40, 2.4)])
BK.pulse(colm[92], S["row896"] + 4, 5.0, rise=6, hold=40, fall=20)

# ------------------------------------------------------------------------------------------------ the stack
TX, TY, TZ = 2.75, 2.05, 0.06
K.rbox("pedestal", (2.9, 1.25, 0.06), bevel=0.012, seg=4, mat=K.M("plinth"), loc=(TX + 0.35, TY, 0.03))
HM = {(3, j) for j in range(14)} | {(24, 2), (12, 13)}
TW = PF.block_tower_f("bt", (TX, TY, TZ), floors=24, pitch=0.16, w=1.6, d=0.62, head_mats=HM)
ZF = [TZ + z for z in TW["z"]]
for k in range(24):
    BK.set_base(TW["att"][k], [(0, 0.35)])
    BK.set_base(TW["mlp"][k], [(0, 0.3)])
    BK.set_base(TW["lens"][k], [(0, 0.0)])
for (k, j), m in TW["head"].items():
    BK.set_base(m, [(0, 0.35)])
# the KV cache: a shelf per block, right of the stack
KV = PF.cache_shelves("cache", TW, x0=0.86, length=0.78, slots=120, depth=0.26, y=-0.12)
REV = {("k", k): [(0, 0.0)] for k in range(1, 25)}
REV.update({("v", k): [(0, 0.0)] for k in range(1, 25)})
for k in range(1, 25):
    for key in ("k", "v"):
        BK.set_base(KV[key][k], [(0, 2.2)])

# the row of 100 columns (first 16 numbers each), one plate per layer (entering block 1, then after each block)
CELLR = 0.016
YR = TY - 0.31 - 0.13
car = K.empty("row", (TX, YR, ZF[0] + 0.1))


def vmax_of(layer):
    a = sorted(abs(x) for r in layer for x in r)
    return a[int(len(a) * 0.95)] or 1.0


rows = []
for l in range(25):
    L = SD[l]
    vals = [L[c][r] for r in range(16) for c in range(NT)]
    pr, pm = K.vector_plate(f"row{l}", vals, NT, 16, K.SKY, (0, 0, 0), cell=CELLR, vmax=vmax_of(L), glow=0.0, reveal=1.0, parent=car)
    rows.append((pr, pm))
WR = NT * CELLR


def rx(i):
    return -WR / 2 + (i + 0.5) * CELLR


RT = 8 * CELLR + 0.012     # the row's top edge (local z)
for i in (0, 86, 92, 99):
    K.empty(f"rowc{i}", (rx(i), -0.01, -8 * CELLR - 0.012), parent=car)
    K.empty(f"rowt{i}", (rx(i), -0.01, RT), parent=car)
K.empty("row_pin", (-WR / 2, -0.01, RT + 0.02), parent=car)

# ---- stage 3: the columns stream from the strip into the row at block 1
fe = S["enter"]
for i in range(NT):
    pr = cols[i]
    d0 = fe - 34 + int((99 - i) * 0.25)
    dst = Vector((TX + rx(i), YR - 0.02, ZF[0] + 0.1))
    mid = Vector(((X(i) + dst.x) / 2, (CY + YR) / 2 - 0.4, CZ + 0.5))
    K.key(pr, "location", [(d0, (X(i), CY, CZ)), (d0 + 16, tuple(mid)), (d0 + 32, tuple(dst))])
    K.key(pr, "scale", [(d0, (1.0,) * 3), (d0 + 32, (CELLR / CELL / CC, CELLR * 16 / CH, 0.3))])
    K.show(pr, [(0, True), (d0 + 34, False)])
    BK.set_base(colm[i], [(d0, 2.4), (d0 + 16, 4.0), (d0 + 32, 4.0)])
for l, (pr, pm) in enumerate(rows):
    K.show(pr, [(0, False)])
K.key(car, "location", [(0, (TX, YR, ZF[0] + 0.1))])
r0, r0m = rows[0]
K.show(r0, [(0, False), (fe - 6, True), (S["rework"], False)])
BK.set_base(r0m, [(0, 0.0), (fe - 6, 0.0), (fe + 6, 4.2)])
# attention in block 1
BK.set_base(TW["att"][0], [(S["att"] - 6, 0.35), (S["att"] + 8, 4.5), (S["mlp"] - 4, 4.5), (S["mlp"] + 10, 0.8)])
BK.set_base(TW["mlp"][0], [(S["mlp"] - 6, 0.3), (S["mlp"] + 10, 5.0), (S["rework"] + 50, 5.0), (S["rework"] + 70, 0.8)])
# q, k, v: three light bars over the whole row (every position makes all three)
for n, (nm, col, f0) in enumerate((("qbar", K.Q_COL, S["q"]), ("kbar", K.K_COL, S["k"]), ("vbar", lambda: None, S["v"]))):
    c = K.V_COL if nm == "vbar" else col
    bo, bmat = PF.light_bar(nm, (WR, 0.006, 0.006), (0, -0.012, RT + 0.03 + n * 0.022), c, parent=car)
    K.empty(nm + "_pin", (WR / 2 + 0.01, -0.012, RT + 0.03 + n * 0.022), parent=car)
    K.key(bo, "scale", [(0, (0.001, 1, 1)), (f0 - 4, (0.001, 1, 1)), (f0 + 10, (1, 1, 1))])
    K.glow_keys(bmat, [(0, 0.0), (f0 - 4, 0.0), (f0 + 6, 5.0), (S["meets"] - 6, 4.0), (S["meets"] + 8, 0.0)])
    K.show(bo, [(0, False), (f0 - 5, True), (S["meets"] + 10, False)])
# the cache of block 1 fills: keys when the query meets them, values when they flow in
REV[("k", 1)] += [(S["meets"] - 2, 0.0), (S["meets"] + 16, 100 / 120)]
REV[("v", 1)] += [(S["flow"] - 2, 0.0), (S["flow"] + 16, 100 / 120)]
# arcs: block 1's real attention (averaged over its 14 heads) from three positions to the earlier ones
arcs = []
for src in (99, 92, 86):
    row = A1[src]
    top = sorted(range(len(row)), key=lambda j: -row[j])
    top = [j for j in top if j != src][:7]
    for r, j in enumerate(top):
        wgt = row[j]
        m = K.light_mat(f"a1_{src}_{j}_m", K.K_COL if src == 99 else K.SKY, 0.0)
        a = Vector((rx(src), -0.012, RT))
        b = Vector((rx(j), -0.012, RT))
        o = K.arc(f"a1_{src}_{j}", a, b, lift=0.03 + 0.09 * abs(src - j) / 99 + 0.01 * r, r=0.0012 + 0.006 * min(1, wgt / 0.13), mat=m)
        o.parent = car
        g0 = S["meets"] + 4 + r * 3 + (0 if src == 99 else 12 if src == 92 else 22)
        K.grow(o, [(0, 0.0), (g0, 0.0), (g0 + 18, 1.0)])
        g = 0.4 + 9.0 * (wgt / 0.13)
        K.glow_keys(m, [(0, 0.0), (g0, 0.0), (g0 + 6, g * 0.7), (S["flow"], g * 0.7), (S["flow"] + 10, g * 1.3),
                        (S["rework"] - 8, g), (S["rework"] + 6, 0.0)])
        K.show(o, [(0, False), (g0 - 1, True), (S["rework"] + 8, False)])
# the MLP reworks each column: the row comes out changed (layer 1, real)
r1, r1m = rows[1]
K.show(r1, [(0, False), (S["rework"], True)])
K.keyval(r1m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (S["rework"], 0.0), (S["rework"] + 18, 1.0)])
BK.set_base(r1m, [(0, 4.2)])

# ------------------------------------------------------------------------------------------------ stage 4: the heads
f14 = S["fourteen"]
for j in range(14):
    m = TW["head"][(3, j)]
    lv = [3.0, 1.6, 4.2, 2.2, 1.2, 3.6, 2.6, 1.8, 4.6, 1.4, 2.8, 3.4, 2.0, 3.9][j]   # 'each looks its own way' (a lighting pattern)
    BK.set_base(m, [(f14 - 4 + 5 * j, 0.35), (f14 + 2 + 5 * j, 4.5), (S["ownway"] - 10, 3.2), (S["ownway"] + 10, lv),
                    (S["h24"] - 6, lv), (S["h24"] + 12, 0.35)])
BK.set_base(TW["head"][(24, 2)], [(S["h24"] - 4, 0.35), (S["h24"] + 8, 6.0), (S["h12"] + 10, 6.0), (S["h12"] + 30, 0.35)])
BK.set_base(TW["head"][(12, 13)], [(S["h12"] - 4, 0.35), (S["h12"] + 8, 6.0), (S["updates"], 6.0), (S["updates"] + 20, 0.35)])
TOPZ = PZ + 0.085
# block 24 head 2 (real weights, qkv_data) and block 12 head 13 (trace heads.row_last), as arcs over the strip
hd_arcs = []
for nm, wts, f0, col, f_off in (("h24", W24, S["puts"], K.SKY, S["h12"] + 6), ("h12", H12, S["rests"], K.lin("#9ab8ff"), S["updates"] + 10)):
    targets = [j for j in range(100) if wts[j] >= 0.02 and j != 99]
    for r, j in enumerate(sorted(targets, key=lambda j: -wts[j])):
        m = K.light_mat(f"{nm}_a{j}_m", col, 0.0)
        dist = abs(X(99) - X(j))
        o = K.arc(f"{nm}_a{j}", (X(99), 0.0, TOPZ), (X(j), 0.0, TOPZ), lift=0.35 + 0.1 * dist, r=0.003 + 0.012 * wts[j], mat=m)
        g0 = f0 + 2 * r
        dur = 18 if dist < 6 else 40
        K.grow(o, [(0, 0.0), (g0, 0.0), (g0 + dur, 1.0)])
        g = 0.6 + 8.0 * wts[j]
        K.glow_keys(m, [(0, 0.0), (g0, 0.0), (g0 + 6, g), (f_off - 10, g), (f_off + 8, 0.0)])
        K.show(o, [(0, False), (g0 - 1, True), (f_off + 10, False)])
BK.pulse(faces[92], S["s65"] + 2, 4.0, rise=4, hold=24, fall=30)
BK.pulse(faces[0], S["first"] + 2, 4.0, rise=6, hold=40, fall=30)
BK.pulse(faces[99], S["puts"], 2.6, rise=4, hold=12, fall=16)
BK.pulse(faces[99], S["rests"], 2.6, rise=4, hold=12, fall=16)

# ------------------------------------------------------------------------------------------------ stage 5: 24 blocks
Fk = S["Fk"]
K.key(car, "location", [(S["updates"], (TX, YR, ZF[0] + 0.1))] + [(Fk[k], (TX, YR, ZF[k - 1] + 0.1)) for k in range(2, 25)])
for k in range(2, 25):
    pr, pm = rows[k]
    K.show(rows[k - 1][0], [(Fk[k], False)])
    K.show(pr, [(0, False), (Fk[k], True), (S["joins"] + 20, False)])
    K.keyval(pm.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (Fk[k], 0.0), (Fk[k] + 5, 1.0)])
    BK.set_base(pm, [(0, 4.2)])
    BK.pulse(TW["att"][k - 1], Fk[k] - 2, 4.5, rise=3, hold=2, fall=12)
    BK.pulse(TW["mlp"][k - 1], Fk[k] + 1, 4.0, rise=3, hold=2, fall=12)
    REV[("k", k)] += [(Fk[k] - 2, 0.0), (Fk[k] + 4, 100 / 120)]
    REV[("v", k)] += [(Fk[k], 0.0), (Fk[k] + 6, 100 / 120)]
# "they hold the keys and values the last column reads": the cache glows
for k in range(1, 25):
    for key in ("k", "v"):
        BK.pulse(KV[key][k], S["hold"] + k, 5.5, rise=8, hold=50, fall=20)
# "set in training": a shimmer up the stack
for k in range(24):
    BK.pulse(TW["att"][k], S["training"] + 2 * k, 3.4, rise=4, hold=3, fall=14)
    BK.pulse(TW["mlp"][k], S["training"] + 2 * k + 2, 3.0, rise=4, hold=3, fall=14)
BK.pulse(rows[24][1], S["params"], 5.5, rise=10, hold=20, fall=20)

# ------------------------------------------------------------------------------------------------ stage 6: next token
p24, p24m = rows[24]
BK.set_base(p24m, [(S["speaks"] - 10, 4.2), (S["speaks"] + 10, 1.2)])
fin, finm = K.vector_plate("final", LENS, CC, CR, K.SKY, (0, 0, 0), cell=CELL, vmax=9.0, glow=0.0)
A0 = Vector((TX + rx(99), YR - 0.03, ZF[23] + 0.1))
A1p = A0 + Vector((0.25, -0.35, 0.18))
RACK_END = Vector((-0.28, 0.52, 0.62))
fs, fsc = S["speaks"], S["scored"]
K.key(fin, "location", [(0, tuple(A0)), (fs - 8, tuple(A0)), (fs + 18, tuple(A1p)), (fsc, tuple(A1p)),
                        (fsc + 30, tuple((A1p + RACK_END) / 2 + Vector((0, -0.5, 0.4)))), (fsc + 62, tuple(RACK_END))])
K.key(fin, "scale", [(0, (0.12, 1, 0.034)), (fs - 8, (0.12, 1, 0.034)), (fs + 18, (1, 1, 1)), (S["chosen"] + 10, (1, 1, 1)),
                     (S["chosen"] + 34, (0.001,) * 3)])
K.show(fin, [(0, False), (fs - 9, True), (S["chosen"] + 36, False)])
BK.set_base(finm, [(0, 0.0), (fs - 8, 0.0), (fs + 18, 4.0), (S["same"], 4.0), (S["same"] + 10, 6.0), (S["chosen"], 4.0)])
# six meters (We, As, Manchester, In, Our, At), on a dark deck in front of the table
K.rbox("deck", (1.9, 0.34, 0.03), bevel=0.008, seg=3, mat=K.M("alu_dark"), loc=(-1.35, 0.5, 0.015))
K.show(bpy.data.objects["deck"], [(0, False), (S["softmax"] - 30, True), (S["ran"], False)])
bars = []
for n, row in enumerate(TOP6):
    bx = -2.1 + n * 0.3
    mr, liq, lm = K.meter(f"bar{n}", (bx, 0.5, 0.03), height=0.6, r=0.03, color=K.SKY)
    f0 = S["softmax"] + 18 + 5 * n
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (f0, (1, 1, 0.001)), (f0 + 36, (1, 1, max(0.003, row["p"])))])
    K.glow_keys(lm, [(0, 0.0), (f0, 0.0), (f0 + 10, 4.0 if n == 0 else 2.0), (S["chosen"], 4.0 if n == 0 else 2.0),
                     (S["chosen"] + 8, 7.0 if n == 0 else 1.0), (S["chosen"] + 40, 3.0 if n == 0 else 0.8)])
    K.show(mr, [(0, False), (S["softmax"] - 30, True), (S["ran"], False)])
    K.key(mr, "location", [(S["softmax"] - 30, (bx, 0.5, -0.7)), (S["softmax"] + 4 + 3 * n, (bx, 0.5, 0.03))])

# ------------------------------------------------------------------------------------------------ the answer tiles
drop = S["drop"]
gfaces = {}
for j, g in enumerate(G):
    dig = j in DIG
    role = "digit" if dig else "answer"
    root, fm = K.token_tile(f"gen{j}", role, (X(100 + j), 0, PZ))
    P7.set_face(fm, K.EMBER if dig else K.SKY)
    gfaces[j] = fm
    lo = Vector((X(100 + j), 0, PZ))
    if j == 0:   # We: from above its meter, onto the strip
        hi = Vector((-2.1, 0.5, 0.95))
        K.key(root, "location", [(0, tuple(hi)), (drop[0], tuple(hi)), (drop[0] + 26, tuple(lo + Vector((0, 0, 0.3)))),
                                 (drop[0] + 38, tuple(lo))])
        K.key(root, "scale", [(0, (0.6,) * 3), (drop[0], (0.6,) * 3), (drop[0] + 26, (1.0,) * 3)])
        K.show(root, [(0, False), (drop[0] - 1, True)])
        land = drop[0] + 38
    else:
        hi = lo + Vector((0, 0, 0.45))
        K.show(root, [(0, False), (max(0, drop[j] - 1), True)])
        K.key(root, "location", [(0, tuple(hi)), (drop[j], tuple(hi)), (drop[j] + 14, tuple(lo))])
        K.key(root, "scale", [(0, (0.8,) * 3), (drop[j], (0.8,) * 3), (drop[j] + 14, (1.0,) * 3)])
        land = drop[j] + 14
    BK.set_base(fm, [(0, 0.0), (land - 1, 0.0), (land + 2, 2.6 if dig else 2.0), (land + 26, 0.5 if dig else 0.16)])
for j, f0 in S["reread"].items():
    BK.pulse(gfaces[j], f0 + 2, 2.6 if j in DIG else 1.8, rise=3, hold=4, fall=14)

# ------------------------------------------------------------------------------------------------ stage 7: the loop
# We's own column (its real input embedding, first 16 numbers) climbs alone and reads the cache
wc, wcm = K.vector_plate("wecol", FD["emb_gen"][0][:16], 1, 16, K.SKY, (0, 0, 0), cell=0.045, vmax=0.03, glow=0.0)
K.empty("wecol_top2", (0, 0, 0.3), parent=wc)
start = Vector((X(100), 0.0, PZ + 0.45))
dock = Vector((TX + WR / 2 + 0.06, YR - 0.02, ZF[0] + 0.14))
fj = S["joins"]
ck = S["climb_we"]
K.key(wc, "location", [(0, tuple(start - Vector((0, 0, 0.3)))), (fj, tuple(start - Vector((0, 0, 0.3)))), (fj + 16, tuple(start)),
                       (fj + 50, tuple((start + dock) / 2 + Vector((0, -0.4, 0.5)))), (fj + 80, tuple(dock)), (ck[1], tuple(dock))] +
      [(ck[k], (dock.x, dock.y, ZF[k - 1] + 0.14)) for k in range(2, 25)] + [(ck[24] + 20, (dock.x, dock.y, ZF[23] + 0.3))])
K.show(wc, [(0, False), (fj, True), (ck[24] + 40, False)])
K.key(wc, "scale", [(0, (1,) * 3), (ck[24] + 20, (1,) * 3), (ck[24] + 38, (0.001,) * 3)])
BK.set_base(wcm, [(0, 0.0), (fj, 0.0), (fj + 14, 6.5)])
# every pass (one per answer token fed back in): the stack lights floor by floor and each block's cache gains one slot
for j in range(19):
    p0 = S["pass"][j]
    fpf = 4 if j == 0 else 1
    for k in range(1, 25):
        t = p0 + (k - 1) * fpf
        BK.pulse(TW["att"][k - 1], t, 4.0 if j == 0 else 2.8, rise=2, hold=1, fall=8)
        BK.pulse(TW["mlp"][k - 1], t + 1, 3.6 if j == 0 else 2.4, rise=2, hold=1, fall=8)
        for key in ("k", "v"):
            REV[(key, k)] += [(t - 1, (100 + j) / 120), (t + 2, (101 + j) / 120)]
            if j == 0:
                BK.pulse(KV[key][k], t + 1, 6.0, rise=2, hold=2, fall=10)
for k in range(1, 25):
    for key in ("k", "v"):
        BK.pulse(KV[key][k], S["kept"] + 2 * k, 5.0, rise=6, hold=30, fall=20)
        BK.pulse(KV[key][k], S["reads"] + k, 5.5, rise=4, hold=10, fall=16)
# the loop stops at <|im_end|>: the stack rests
for k in range(24):
    BK.set_base(TW["att"][k], [(S["stops"], 0.35), (S["stops"] + 20, 0.15)])
    BK.set_base(TW["mlp"][k], [(S["stops"], 0.3), (S["stops"] + 20, 0.12)])

# ------------------------------------------------------------------------------------------------ stage 9: why?
fr_ = S["ran"]
for i in range(NT):     # a replay of the whole journey: the strip, then the table (rack keys above), then the stack
    BK.pulse(faces[i], fr_ + int(i * 0.35), 1.6, rise=3, hold=2, fall=12)
for j in range(20):
    BK.pulse(gfaces[j], fr_ + 36 + 2 * j, 2.4, rise=3, hold=3, fall=12)
for k in range(24):
    BK.pulse(TW["att"][k], fr_ + 40 + 2 * k, 3.0, rise=3, hold=3, fall=14)
    BK.pulse(TW["mlp"][k], fr_ + 42 + 2 * k, 2.6, rise=3, hold=3, fall=14)
for j in DIG:
    BK.pulse(gfaces[j], S["is100"] + 2, 5.0, rise=6, hold=60, fall=20)
    BK.set_base(gfaces[j], [(S["is100"] + 80, 0.5), (S["why"], 0.5), (S["why"] + 20, 1.8)])
PLQ = Vector((X(105), -0.78, 0.0))
plq, plq_m = P7.plaque("plaque", tuple(PLQ), w=1.0, h=0.22)
K.show(plq, [(0, False), (S["ledger"] - 16, True)])
K.key(plq, "location", [(0, tuple(PLQ - Vector((0, 0, 0.3)))), (S["ledger"] - 16, tuple(PLQ - Vector((0, 0, 0.3)))), (S["ledger"] + 10, tuple(PLQ))])
K.glow_keys(plq_m, [(0, 0.0), (S["ledger"], 0.0), (S["ledger"] + 14, 4.5)])

# write all collected light and reveal keys
BK.write()
for (key, k), ks in REV.items():
    ks = sorted(ks)
    best, out = 0.0, []
    for f, v in ks:
        best = max(best, v)
        out.append((f, best))
    K.keyval(KV[key][k].node_tree.nodes["reveal"].outputs[0], out)

# ------------------------------------------------------------------------------------------------ the camera journey
V = Vector
st = S["stage"]
c = K.Cam(sc, "c_journey", lens=30, fstop=4.0)
c.keys([
    # 1: the whole machine, then the strip receding into the distance (the chat panel sits over the sky)
    (0, (7.4, -6.6, 3.9), (0.4, 1.0, 1.25)),
    (S["chat_user"], (6.4, -6.9, 3.4), (-0.2, 1.0, 1.05)),
    (S["chat_sys"] + 30, (3.6, -4.6, 2.5), (-9.0, 0.5, 0.1)),
    (S["fly"] - 20, (3.0, -4.3, 2.3), (-10.0, 0.5, 0.05)),
    (S["fly"] + 30, (3.0, -4.3, 2.3), (-10.0, 0.5, 0.05)),
    # 2: down to the end of the strip and the table behind it
    (st[1] + 30, (X(85.5), -2.75, 1.25), (X(91.5), 0.45, 0.32)),
    (S["look"] + 60, (X(87.0), -2.65, 1.2), (X(92.0), 0.5, 0.34)),
    (S["rows_sweep"][0] + 10, (X(96.0), -3.2, 1.9), (X(78.0), 0.9, 0.45)),
    (S["rows_sweep"][1], (X(95.0), -3.1, 1.8), (X(80.0), 0.9, 0.45)),
    (S["row896"] + 10, (X(92.0) + 0.55, -1.05, 0.66), (X(92.0) + 0.05, 0.3, 0.44)),
    (S["stands"] - 8, (X(92.0) + 0.6, -1.1, 0.68), (X(92.0) + 0.05, 0.3, 0.44)),
    (S["stands"] + 70, (X(99) + 1.7, -2.6, 1.15), (X(84.0), 0.35, 0.35)),
    (st[2] - 6, (X(99) + 1.8, -2.7, 1.2), (X(83.0), 0.35, 0.35)),
    # 3: the columns stream into block 1; close on the row
    (S["enter"] - 10, (1.5, -2.5, 1.05), (1.8, 1.2, 0.3)),
    (S["enter"] + 30, (2.4, -2.4, 1.0), (2.5, YR, ZF[0] + 0.12)),
    (S["att"] + 10, (TX + 0.5, YR - 1.35, ZF[0] + 0.42), (TX + 0.25, YR, ZF[0] + 0.12)),
    (S["meets"] - 6, (TX + 0.62, YR - 1.0, ZF[0] + 0.4), (TX + 0.42, YR, ZF[0] + 0.2)),
    (S["flow"] + 30, (TX + 0.6, YR - 0.95, ZF[0] + 0.42), (TX + 0.4, YR, ZF[0] + 0.2)),
    (S["mlp"] + 10, (TX + 0.95, YR - 1.25, ZF[0] + 0.5), (TX + 0.45, YR + 0.3, ZF[0] + 0.12)),
    (st[3] - 6, (TX + 0.9, YR - 1.3, ZF[0] + 0.55), (TX + 0.4, YR + 0.3, ZF[0] + 0.14)),
    # 4: the 14 heads of a block, then back to the strip for two real heads
    (st[3] + 30, (TX - 0.3, TY - 1.6, ZF[2] + 0.36), (TX - 0.32, TY, ZF[2] + 0.05)),
    (S["ownway"] + 10, (TX - 0.2, TY - 1.5, ZF[2] + 0.32), (TX - 0.32, TY, ZF[2] + 0.05)),
    (S["h24"] + 10, (X(94.0), -3.3, 1.9), (X(95.0), 0.3, 0.45)),
    (S["s65"] + 30, (X(94.3), -3.2, 1.85), (X(95.0), 0.3, 0.45)),
    (S["h12"] + 6, (X(94.5), -3.2, 1.8), (X(94.5), 0.3, 0.5)),
    (S["rests"] + 6, (X(99) + 1.3, -1.7, 1.0), (X(60), 0.3, 1.2)),
    (S["first"] + 30, (X(99) + 1.4, -1.75, 1.0), (X(55), 0.3, 1.1)),
    # 5: back to the row; the climb; the cache; the whole stack
    (st[4] + 10, (TX + 0.6, YR - 2.2, ZF[0] + 0.6), (TX + 0.1, YR, ZF[0] + 0.15)),
    (Fk[2], (TX + 0.6, YR - 2.25, ZF[1] + 0.55), (TX + 0.1, YR, ZF[1] + 0.15)),
    (Fk[12], (TX + 0.7, YR - 2.4, ZF[11] + 0.5), (TX + 0.15, YR, ZF[11] + 0.12)),
    (Fk[24], (TX + 0.9, YR - 2.5, ZF[23] + 0.5), (TX + 0.3, YR, ZF[23] + 0.12)),
    (S["hold"] - 20, (TX + 1.9, YR - 2.5, ZF[23] + 0.45), (TX + 0.9, YR + 0.2, ZF[22])),
    (S["hold"] + 50, (TX + 2.0, YR - 2.6, ZF[23] + 0.3), (TX + 1.0, YR + 0.2, ZF[21])),
    (S["params"] + 20, (TX + 3.6, TY - 7.4, 2.6), (TX + 0.4, TY, 2.0)),
    (st[5] - 10, (TX + 3.2, TY - 7.0, 3.0), (TX + 0.4, TY, 2.2)),
    # 6: the top; the last column comes down to the table; the sweep; the meters; We drops
    (st[5] + 20, (TX + 1.5, YR - 2.1, ZF[23] + 0.55), (TX + 0.75, YR - 0.15, ZF[23] + 0.15)),
    (S["scored"], (TX + 1.4, YR - 2.2, ZF[23] + 0.45), (TX + 0.85, YR - 0.3, ZF[23] + 0.1)),
    (S["scored"] + 62, (1.3, -2.5, 1.3), (-0.6, 0.6, 0.55)),
    (S["all151"] + 10, (1.5, -3.3, 1.6), (-2.6, 0.8, 0.5)),
    (S["softmax"] - 6, (1.4, -3.2, 1.5), (-2.4, 0.8, 0.5)),
    (S["softmax"] + 30, (-0.75, -2.1, 1.0), (-1.3, 0.5, 0.42)),
    (S["chosen"] - 4, (-0.7, -2.15, 1.0), (-1.2, 0.45, 0.42)),
    (drop[0] + 40, (0.1, -2.3, 0.95), (-0.5, 0.3, 0.32)),
    # 7: wide on the loop; the cache; We's column climbs; currently, have, space
    (st[6] + 30, (3.4, -3.4, 1.5), (1.4, 0.9, 0.55)),
    (S["notrun"], (TX + 3.0, TY - 6.0, 2.1), (TX + 0.8, TY, 1.9)),
    (S["sends"], (TX + 2.6, TY - 4.6, 1.2), (TX + 0.9, TY - 0.3, 0.9)),
    (S["climb_we"][1] + 4, (TX + 2.4, TY - 3.9, ZF[0] + 0.6), (TX + 0.8, TY - 0.4, ZF[0] + 0.3)),
    (S["climb_we"][24], (TX + 2.4, TY - 3.9, ZF[23] + 0.4), (TX + 0.8, TY - 0.4, ZF[23] + 0.1)),
    (S["reads"] + 10, (TX + 2.6, TY - 4.6, ZF[20] + 0.4), (TX + 0.8, TY - 0.4, ZF[18])),
    (drop[1] - 6, (2.6, -2.9, 1.0), (1.4, 0.3, 0.3)),
    # 8: the answer grows along the strip
    (st[7] + 20, (2.7, -2.9, 0.95), (2.0, 0.3, 0.28)),
    (drop[6] + 30, (2.9, -2.9, 0.95), (2.3, 0.3, 0.28)),
    (drop[19] + 20, (4.1, -4.6, 1.25), (3.8, 0.3, 0.25)),
    # 9: the whole machine; then 100 against 5,400
    (st[8] + 50, (3.0, -12.5, 5.4), (-1.5, 1.2, 1.3)),
    (S["still"], (3.0, -12.0, 5.2), (-1.0, 1.2, 1.2)),
    (S["says"], (2.6, -4.0, 1.25), (2.2, -0.3, 0.25)),
    (S["why_big"], (2.45, -3.4, 1.1), (2.15, -0.35, 0.3)),
    (END, (2.4, -3.2, 1.05), (2.15, -0.35, 0.3)),
])
c.lens([(0, 30), (S["chat_sys"] + 30, 32), (st[1] + 30, 35), (S["row896"] + 10, 40), (S["stands"] + 70, 32), (S["enter"] + 30, 32),
        (S["att"] + 10, 38), (st[3] + 30, 36), (S["h24"] + 10, 32), (S["rests"] + 6, 30), (st[4] + 10, 32), (S["params"] + 20, 30),
        (st[5] + 20, 34), (S["scored"] + 62, 30), (S["softmax"] + 30, 35), (st[6] + 30, 30), (st[7] + 20, 32), (st[8] + 50, 26),
        (S["says"], 35)])
c.fstop([(0, 5.0), (S["chat_sys"] + 30, 6.0), (st[1] + 30, 3.2), (S["row896"] + 10, 2.4), (S["stands"] + 70, 3.6), (S["att"] + 10, 2.8),
         (st[3] + 30, 3.0), (S["h24"] + 10, 3.6), (S["rests"] + 6, 6.0), (st[4] + 10, 3.6), (S["params"] + 20, 5.0), (st[5] + 20, 3.2),
         (S["softmax"] + 30, 3.0), (st[6] + 30, 4.0), (st[7] + 20, 4.0), (st[8] + 50, 6.0), (S["says"], 3.2)])

# ------------------------------------------------------------------------------------------------ pins
pins = [f"tok{i}_top" for i in range(100)] + [f"tok{i}_front" for i in range(76, 100)]
pins += [f"gen{j}_top" for j in range(20)] + [f"gen{j}_front" for j in range(20)]
pins += ["rack_pin2", "col92_top", "row_pin", "qbar_pin", "kbar_pin", "vbar_pin", "rowc99", "rowt99", "rowc92", "rowc86",
         "bt_mlp1", "bt_att1", "bt_att3", "cache_k24", "cache_k12", "final_top", "wecol_top", "plaque_top"]
pins += [f"bar{n}_top" for n in range(6)] + [f"bt_f{k}_h{j}_pin" for (k, j) in HM]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
