"""Film s4: "Attention: tokens look back". Builds films/s4_attention.blend.

The row of 100 tiles, each with its vector standing behind it as a column of real cells (first 16 input-embedding
values). Light arcs from the last position back to every earlier one, thickness and brightness = the real weight:
first the average over 14 heads x 24 blocks (trace attention.last.avg), then three heads in their own colours
(attention.heads rows), then the causal mask as a frosted glass wall after " battery" with battery's own recorded
top-6 weights (attention.rows.avg[86]), all backwards. Ends on the 24 x 14 head stack.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s456 as P4  # noqa: E402

FILM = "s4_attention"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
N = len(TOK)
LAST, MAN, BATT, PACKS, MAN_SYS = 99, 92, 86, 87, 21
X = P4.X
PZ = P4.PZ
AVG = T["attention"]["last"]["avg"]
M = [sum(AVG[l][j] for l in range(24)) / 24 for j in range(N)]
HEADS = {h["looks_at"]: h for h in T["attention"]["heads"]}
ROW_B = dict((j, w) for j, w in T["attention"]["rows"]["avg"][BATT])   # battery's top-6 (all <= 86)
V16 = {r["i"]: r["v16"] for r in T["embeddings"]["values"]}
HCOL = {"Manchester": K.SKY, "battery": K.K_COL, "start": K.lin("#ffe2a8")}

sc = K.reset(B.frames)
K.studio(sc, focus=(-1.8, 0.0, 0.35), key_power=3000, span=26.0)
tiles, ZTOP = P4.row(TOK, V16)
TW = K.tower("tower", (1.55, 1.05, 0.0), floors=24, pitch=0.072, w=1.5, d=0.56, lit={(24, 2), (16, 0), (12, 13)})

src = Vector((X(LAST), 0.05, ZTOP + 0.01))


def arcs_from(prefix, srcv, weights, color, min_w=0.004, rmax=0.02, rmin=0.0035, lift0=0.16):
    out = {}
    for j, wgt in weights.items():
        if wgt < min_w or j == int(round((srcv.x / P4.PITCH) + 99)):
            continue
        dst = Vector((X(j), 0.05, ZTOP + 0.01))
        dist = (dst - srcv).length
        r = rmin + (rmax - rmin) * math.sqrt(min(1.0, wgt / 0.35))
        mj = K.light_mat(f"{prefix}{j}_m", color, 0.0)
        out[j] = (K.arc(f"{prefix}{j}", srcv, dst, lift=lift0 + 0.08 * math.sqrt(dist) + 0.06 * dist, r=r, mat=mj), mj, wgt)
    return out


A_AVG = arcs_from("avg", src, {j: M[j] for j in range(N - 1)}, K.SKY)
A_H = {nm: arcs_from("h" + nm[:3], src, {j: HEADS[nm]["row_last"][j] for j in range(N - 1)}, HCOL[nm], min_w=0.006)
       for nm in ("Manchester", "battery", "start")}
bsrc = Vector((X(BATT), 0.05, ZTOP + 0.01))
A_B = arcs_from("bat", bsrc, {j: w for j, w in ROW_B.items() if j != BATT}, K.lin("#9ec7ff"), min_w=0.0)
# an attempt to look forward, stopped by the glass
blk_m = K.light_mat("blocked_m", K.lin("#9ec7ff"), 0.0)
blocked = K.arc("blocked", bsrc, Vector((X(PACKS), 0.05, ZTOP + 0.01)), lift=0.2, r=0.006, mat=blk_m)
wall, wall_edge = P4.glass_wall("wall", (X(BATT) + 0.18, 0.0, PZ + 3.0), w=0.62, h=1.05)

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5")}
w = B.w
END = B.frames - 1

# columns rise out of the tiles during the title (they stand from then on)
for i, (root, fm, cr, cm) in tiles.items():
    z = cr.location.z
    d = int(abs(LAST - i) * 0.4)
    K.key(cr, "location", [(0, (cr.location.x, cr.location.y, z - 0.38)), (14 + d, (cr.location.x, cr.location.y, z - 0.38)),
                           (40 + d, (cr.location.x, cr.location.y, z))])
    K.glow_keys(cm, [(0, 0.0), (14 + d, 0.0), (40 + d, 3.6)])
f_last = w("b2", "last")
K.glow_keys(tiles[LAST][1], [(0, 0.0), (f_last - 8, 0.0), (f_last + 10, 3.2), (END, 3.2)])
# a first single look back on "look back" (b1): the last position to Manchester, as a preview
pre_m = K.light_mat("pre_m", K.SKY, 0.0)
pre = K.arc("pre", src, Vector((X(MAN), 0.05, ZTOP + 0.01)), lift=0.3, r=0.008, mat=pre_m)
fb = w("b1", "back")
K.grow(pre, [(0, 0.0), (fb - 4, 0.0), (fb + 18, 1.0)])
K.glow_keys(pre_m, [(0, 0.0), (fb - 4, 0.0), (fb + 4, 4.0), (b["b1"]["f1"] + 4, 4.0), (b["b1"]["f1"] + 20, 0.0)])
K.show(pre, [(0, False), (fb - 6, True), (b["b1"]["f1"] + 22, False)])


def light(arcs, f_on, f_off, gain=7.0, ref=0.35, stagger=0.3, fade=16):
    for j, (o, m_, wgt) in arcs.items():
        d = int(abs(LAST - j) * stagger)
        g = 0.25 + gain * min(1.0, (wgt / ref)) ** 0.6
        K.grow(o, [(0, 0.0), (f_on + d, 0.0), (f_on + d + 18, 1.0)])
        K.glow_keys(m_, [(0, 0.0), (f_on + d, 0.0), (f_on + d + 6, g), (f_off, g), (f_off + fade, 0.0)])
        K.show(o, [(0, False), (f_on + d - 2, True), (f_off + fade + 2, False)])


# b2: the average over all heads and blocks
f_avg = w("b2", "looks")
f_heads = w("b3", "block")
light(A_AVG, f_avg, f_heads - 10)
# roles light up: the template markers, then Emma's question
f_mark, f_fifth = w("b2", "markers"), w("b2", "fifth")
for t in TOK:
    i = t["i"]
    if i == LAST:
        continue
    fm = tiles[i][1]
    if t["role"] == "template":
        K.glow_keys(fm, [(f_mark - 6, 0.0), (f_mark + 8, 1.8), (f_fifth - 6, 1.8), (f_fifth + 6, 0.3), (f_heads, 0.0)])
    elif t["role"] == "user":
        K.glow_keys(fm, [(f_fifth - 6, 0.0), (f_fifth + 8, 1.8), (f_heads - 10, 1.8), (f_heads + 6, 0.0)])

# b3: three heads, each in its own colour
f_h1, f_h2, f_h3 = w("b3", "twenty-four"), w("b3", "sixteen"), w("b3", "twelve")
light(A_H["Manchester"], f_h1 - 6, f_h2 - 12, stagger=0.2)
light(A_H["battery"], f_h2 - 6, f_h3 - 12, ref=0.14, stagger=0.2)
light(A_H["start"], f_h3 - 6, b["b4"]["f0"] - 10, stagger=0.1)
K.glow_keys(tiles[MAN][1], [(f_h1, 0.0), (f_h1 + 20, 2.4), (f_h2 - 6, 2.4), (f_h2 + 6, 0.0)])
K.glow_keys(tiles[BATT][1], [(f_h2, 0.0), (f_h2 + 20, 2.4), (f_h3 - 6, 2.4), (f_h3 + 6, 0.0)])
K.glow_keys(tiles[0][1], [(f_h3, 0.0), (f_h3 + 30, 2.8), (b["b4"]["f0"] - 10, 2.8), (b["b4"]["f0"] + 6, 0.0)])

# b4: the causal mask. The glass wall comes down after " battery"; battery looks back (its recorded top 6);
# a look forward is stopped at the glass; the future tiles go dark
f_rule, f_fwd, f_see, f_not = w("b4", "rule"), w("b4", "forward"), w("b4", "battery"), w("b4", "not")
f_mask = w("b4", "masked")
wz = wall.location.z
K.key(wall, "location", [(0, (wall.location.x, 0.0, PZ + 3.0)), (f_rule - 4, (wall.location.x, 0.0, PZ + 3.0)),
                         (f_rule + 26, (wall.location.x, 0.0, PZ + 0.0))])
K.glow_keys(wall_edge, [(0, 0.0), (f_rule + 20, 0.0), (f_rule + 34, 3.0), (f_mask, 3.0), (f_mask + 16, 5.0), (END, 3.0)])
K.show(wall, [(0, False), (f_rule - 6, True)])
light(A_B, f_see - 4, b["b5"]["f0"] - 6, ref=0.43, stagger=0.15)
K.glow_keys(tiles[BATT][1], [(f_see - 8, 0.0), (f_see + 8, 3.0), (b["b5"]["f0"] - 6, 3.0), (b["b5"]["f0"] + 10, 0.0)])
K.grow(blocked, [(0, 0.0), (f_not - 2, 0.0), (f_not + 10, 0.42), (f_not + 26, 0.42), (f_not + 40, 0.0)])
K.glow_keys(blk_m, [(0, 0.0), (f_not - 2, 0.0), (f_not + 6, 4.0), (f_not + 28, 4.0), (f_not + 40, 0.0)])
K.show(blocked, [(0, False), (f_not - 4, True), (f_not + 42, False)])
for i in range(BATT + 1, N):   # the future, dimmed (their columns fade, faces off)
    cm = tiles[i][3]
    K.glow_keys(cm, [(f_rule + 20, 3.6), (f_rule + 40, 0.35), (b["b5"]["f0"], 0.35), (b["b5"]["f0"] + 20, 3.6)])

# b5: the head stack assembles behind the row; 14 heads x 24 floors light; the three named heads glow in colour
b5 = b["b5"]["f0"]
for ch in TW["root"].children:
    if "_post" in ch.name:
        K.show(ch, [(0, False), (b5 - 30, True)])
for k, fr in enumerate(TW["floors"], start=1):
    z = fr.location.z
    t0 = b5 - 30 + int((k - 1) * 1.1)
    K.show(fr, [(0, False), (t0, True)])
    K.key(fr, "location", [(0, (0, 0, z + 1.6)), (t0, (0, 0, z + 1.6)), (t0 + 22, (0, 0, z))])
f_side, f_mix = w("b5", "side"), w("b5", "mixes")
K.glow_keys(TW["idle"], [(0, 0.0), (f_side - 6, 0.0), (f_side + 20, 1.8), (END, 2.4)])
for (k, j), col in (((24, 2), K.SKY), ((16, 0), K.K_COL), ((12, 13), HCOL["start"])):
    m_ = TW["heads"][(k, j)][1]
    m_.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = col
    K.glow_keys(m_, [(0, 0.0), (f_side, 0.0), (f_side + 16, 6.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_open", lens=38, fstop=2.4).cut(0)
c1.keys([(0, (X(86) + 0.2, -1.35, 0.78), (X(89), 0.0, 0.34)),
         (fb, (X(94) + 0.5, -1.4, 0.85), (X(94.5), 0.0, 0.36)),
         (b["b1"]["f1"] + 10, (X(97) + 0.7, -1.5, 0.95), (X(95), 0.0, 0.4))])
c2 = K.Cam(sc, "c_avg", lens=30, fstop=3.5).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (0.9, -1.35, 0.95), (-1.8, 0.0, 0.45)),
         (f_mark - 12, (1.8, -2.8, 1.7), (-4.5, 0.0, 0.5))])
c2w = K.Cam(sc, "c_wide", lens=28, fstop=8.0).cut(f_mark - 10)
c2w.keys([(f_mark - 10, (X(0) - 1.6, -2.6, 1.5), (X(0) + 4.0, 0.0, 0.8)), (f_fifth - 12, (X(0) - 1.2, -2.4, 1.4), (X(0) + 4.5, 0.0, 0.8))])
c2c = K.Cam(sc, "c_user", lens=35, fstop=3.0).cut(f_fifth - 10)
c2c.keys([(f_fifth - 10, (X(84), -1.7, 1.0), (X(88), 0.0, 0.4)), (b["b2"]["f1"] + 12, (X(86), -1.55, 0.95), (X(89), 0.0, 0.42))])
c3 = K.Cam(sc, "c_h1", lens=35, fstop=3.2).cut(f_h1 - 14)
c3.keys([(f_h1 - 14, (0.55, -1.55, 0.95), (-1.6, 0.0, 0.5)), (f_h2 - 16, (0.35, -1.4, 0.9), (-1.7, 0.0, 0.5))])
c4 = K.Cam(sc, "c_h2", lens=35, fstop=3.2).cut(f_h2 - 14)
c4.keys([(f_h2 - 14, (-1.0, -1.65, 0.95), (-3.2, 0.0, 0.48)), (f_h3 - 16, (-1.3, -1.5, 0.9), (-3.4, 0.0, 0.48))])
c5 = K.Cam(sc, "c_h3", lens=28, fstop=4.5).cut(f_h3 - 14)
c5.keys([(f_h3 - 14, (1.0, -2.2, 1.4), (-4.0, 0.0, 0.8)),
         (f_h3 + 40, (-14.0, -9.0, 3.6), (-24.0, 0.0, 1.2))])
c5b = K.Cam(sc, "c_h3b", lens=30, fstop=3.5).cut(f_h3 + 44)
c5b.keys([(f_h3 + 44, (X(0) - 1.7, -2.4, 1.5), (X(0) + 4.0, 0.0, 0.9)), (b["b4"]["f0"] + 10, (X(0) - 1.3, -2.2, 1.35), (X(0) + 4.5, 0.0, 0.9))])
c6 = K.Cam(sc, "c_mask", lens=35, fstop=3.0).cut(b["b4"]["f0"] - 6)
c6.keys([(b["b4"]["f0"] - 6, (X(BATT) + 0.35, -2.0, 1.05), (X(BATT) - 0.1, 0.0, 0.5)),
         (f_see - 10, (X(BATT) + 0.3, -1.9, 1.0), (X(BATT) - 0.25, 0.0, 0.5)),
         (f_not + 30, (X(BATT) + 0.2, -1.8, 0.95), (X(BATT) - 0.3, 0.0, 0.48)),
         (b["b4"]["f1"] + 12, (X(BATT) + 0.4, -2.2, 1.1), (X(BATT) - 0.2, 0.0, 0.5))])
c7 = K.Cam(sc, "c_stack", lens=32, fstop=3.5).cut(b5 - 8)
c7.keys([(b5 - 8, (-0.6, -2.3, 1.0), (0.2, 0.4, 0.6)),
         (f_mix, (2.6, -2.6, 1.9), (1.4, 1.0, 0.9)),
         (END, (3.3, -3.4, 2.2), (1.4, 1.0, 0.9))])

pins = [f"tok{i}_front" for i in list(range(78, N)) + [0, 1, 2, MAN_SYS]]
pins += [f"c{i}_top" for i in (0, 99, 94, 98, 96, 92, 86, 85, 81, 82, 83, 21, 87, 93)]
pins += ["wall_top", "tower_pin_f24", "tower_pin_f16", "tower_pin_f12"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
