"""Film "heads": "Heads: fourteen ways of looking" (Lecture 2, section 5b). Replaces s4_attention.

Why many heads: one pattern (block 24 head 2's real row) spends 65% on Manchester and almost nothing on battery. The last
token's real 896-number query (block 24, q_proj) splits into 14 slices of 64; each slice sends one arc to its own
strongest target (real, heads_data.json); 2 key and 2 value plates (real k_proj / v_proj, 2 x 64 each) each serve 7.
Then five real heads on the row of tiles (heads_data.json mats / digit_step rows): block 9 head 7 (previous token),
block 12 head 13 (rests on position 1), block 24 head 2 (Manchester), block 19 head 13 (Emma's question), block 2 head 7
(the date's digits, at the step that writes the first digit). Finally the 14 real head outputs (block 24, 14 x 64)
join into 896, pass the output matrix (decorative frame) and the real result is added to the last token's vector.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_blocks_heads as PB  # noqa: E402

FILM = "heads"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
HD = K.load("films/build/data/heads_data.json")
HEADS = {(h["block"], h["head"]): h for h in HD["heads"]}
MATS = HD["mats"]
DIG = HD["digit_step"]
X = PB.X
PZ = PB.PZ
LAST, MAN, BATT, STORES = 99, 92, 86, 93
GEN = DIG["gen_prefix"]              # We, currently, have, ' '
NT = 100 + len(GEN)
ZT = PZ + 0.075 + 0.012              # arcs leave from the tile tops
HC = {"prev": K.lin("#78aaff"), "rest": K.lin("#ffe2a8"), "place": K.SKY, "question": K.K_COL, "digits": K.EMBER}

sc = K.reset(B.frames)
K.studio(sc, focus=(-3.0, 0.0, 0.6), key_power=3200, span=30.0)
K.plinth("plinth", X(0) - 0.45, X(NT - 1) + 0.45, depth=0.5, height=PZ)
tiles = {}
for t in TOK:
    tiles[t["i"]] = K.token_tile(f"tok{t['i']}", t["role"], (X(t["i"]), 0, PZ))
for k, txt in enumerate(GEN):
    i = 100 + k
    tiles[i] = K.token_tile(f"tok{i}", "template", (X(i), 0, PZ))


def top(i):
    return Vector((X(i), 0.0, ZT))


def p95(v):
    a = sorted(abs(x) for x in v)
    return a[int(len(a) * 0.95)] or 1.0


# ------------------------------------------------------------------------------------------------ the hub above the last token
QKV = HD["qkv_last"]["24"]
JOIN = HD["joins"]["24"]
LV = HD["last_vecs"]["24"]
CELL = 0.02
ZR, ZQ, ZKV = 0.78, 1.62, 1.18
YH = 0.1
res_in, res_in_m = K.vector_plate("res", LV["in"], 56, 16, K.SKY, (0, YH, ZR), cell=CELL, vmax=p95(LV["in"]), glow=3.6)
res_out, res_out_m = K.vector_plate("res2", LV["after_attention"], 56, 16, K.SKY, (0, YH, ZR), cell=CELL, vmax=p95(LV["after_attention"]), glow=4.4)
qbig, qbig_m = K.vector_plate("qbig", QKV["q"], 56, 16, K.SKY, (0, YH, ZQ), cell=CELL, vmax=p95(QKV["q"]), glow=4.0)


def slice_vals(v, h):
    """Head h's 64 numbers as a 4 x 16 block (column-major: 16 rows x 4 cols in reading order)."""
    s = v[h * 64:(h + 1) * 64]
    return [s[c * 16 + r] for r in range(16) for c in range(4)]


SL_PACK = [(-0.56 + (h * 4 + 2) * CELL) for h in range(14)]
SL_FAN = [(h - 6.5) * 0.17 for h in range(14)]
slices, outs = [], []
for h in range(14):
    r, m = K.vector_plate(f"qs{h}", slice_vals(QKV["q"], h), 4, 16, K.SKY, (SL_PACK[h], YH, ZQ), cell=CELL, vmax=p95(QKV["q"]), glow=4.0)
    slices.append((r, m))
    r2, m2 = K.vector_plate(f"os{h}", slice_vals(JOIN["heads_concat"], h), 4, 16, K.lin("#ffe2a8"), (SL_FAN[h], YH, ZQ), cell=CELL,
                            vmax=p95(JOIN["heads_concat"]), glow=4.0)
    outs.append((r2, m2))
joined, joined_m = K.vector_plate("joined", JOIN["heads_concat"], 56, 16, K.lin("#ffe2a8"), (0, YH, ZQ), cell=CELL, vmax=p95(JOIN["heads_concat"]), glow=4.0)
oplate, oplate_m = K.vector_plate("oplate", JOIN["o_proj_out"], 56, 16, K.SKY, (2.5, YH, ZQ), cell=CELL, vmax=p95(JOIN["o_proj_out"]), glow=4.4)
wo, wo_m = K.matrix_frame("wo", (1.4, YH + 0.02, ZQ), w=0.5, h=0.46, tint=K.SKY, seed=7)
kv = {}
for g in range(2):
    cx = -0.6 if g == 0 else 0.6
    kr, km = K.vector_plate(f"k{g}", slice_vals(QKV["k"], g), 4, 16, K.K_COL, (cx - 0.06, YH, ZKV), cell=CELL, vmax=p95(QKV["k"]), glow=4.0)
    vr, vm = K.vector_plate(f"v{g}", slice_vals(QKV["v"], g), 4, 16, K.V_COL, (cx + 0.06, YH, ZKV), cell=CELL, vmax=p95(QKV["v"]), glow=3.2)
    kv[g] = (kr, vr)
# the single "lens" of b1: a machined head module above the last token
lens_m = K.light_mat("hlens_m", K.SKY, 0.0)
hmod = K.empty("hmod", (0, YH, ZQ))
K.rbox("hmod_body", (0.22, 0.16, 0.12), bevel=0.02, seg=4, mat=K.M("alu"), loc=(0, 0, 0), parent=hmod)
lc = K.cyl("hmod_lens", 0.05, 0.03, lens_m, loc=(0, -0.08, 0), verts=32, parent=hmod)
lc.rotation_euler = (math.pi / 2, 0, 0)
K.empty("hmod_top", (0, 0, 0.1), parent=hmod)

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in [f"b{i}" for i in range(1, 11)]}
w = B.w
END = B.frames - 1
for i, (root, fm) in tiles.items():
    if i >= 100:
        continue
K.glow_keys(tiles[LAST][1], [(0, 0.0), (20, 0.0), (50, 2.6), (END, 2.6)])

# b1: one pattern (block 24 head 2's real row from the last position)
f_pat, f_man1, f_bat1, f_bef = w("b1", "pattern"), w("b1", "manchester"), w("b1", "battery"), w("b1", "before")
f_split = w("b2", "splits")
K.show(hmod, [(0, False), (f_pat - 20, True), (f_split + 20, False)])
K.key(hmod, "location", [(f_pat - 20, (0, YH, ZQ + 0.6)), (f_pat, (0, YH, ZQ))])
K.glow_keys(lens_m, [(0, 0.0), (f_pat, 0.0), (f_pat + 10, 6.0), (f_split, 6.0), (f_split + 12, 0.0)])
R242 = MATS["24.2"][LAST]
src_h = Vector((0, YH - 0.08, ZQ - 0.06))
A1 = PB.arc_set("one", src_h, top, {j: R242[j] for j in range(LAST)}, K.SKY, min_w=0.004, ref=0.35, lift0=0.1)
PB.light_arcs(A1, f_pat + 8, f_split - 4, LAST, ref=0.35, stagger=0.06)
for i, f in ((MAN, f_man1), (BATT, f_bat1), (98, f_bef)):
    K.glow_keys(tiles[i][1], [(0, 0.0), (f - 4, 0.0), (f + 6, 2.6 if i == MAN else 1.2), (f_split - 4, 2.6 if i == MAN else 1.2), (f_split + 8, 0.0)])

# the last token's vector (block 24, entering attention) stands above it from the start
K.show(res_in, [(0, False), (24, True), (w("b2", "eight") + 16, False), (B.b0("b9") - 2, True)])
K.key(res_in, "scale", [(24, (0.02, 1, 0.02)), (50, (1, 1, 1)), (w("b2", "eight") + 2, (1, 1, 1)), (w("b2", "eight") + 14, (0.6, 1, 0.6)),
                        (B.b0("b9") - 2, (0.02, 1, 0.02)), (B.b0("b9") + 16, (1, 1, 1))])

# b2: the 896-number query, cut into 14 slices of 64 that fan out; each slice sends one arc to its own strongest target
f_eight, f_cut, f_64, f_each, f_same = w("b2", "eight"), w("b2", "cut"), w("b2", "sixty-four"), w("b2", "each"), w("b2", "same")
K.show(qbig, [(0, False), (f_eight - 6, True), (f_cut + 6, False)])
K.key(qbig, "location", [(f_eight - 6, (0, YH, ZR)), (f_eight + 14, (0, YH, ZQ))])
K.glow_keys(qbig_m, [(0, 4.0), (f_cut - 4, 4.0), (f_cut + 4, 7.0)])
blade_m = K.light_mat("blade_m", K.lin("#e8f2ff"), 0.0)
blades = []
for h in range(1, 14):
    xb = -0.56 + h * 4 * CELL
    bl = K.rbox(f"blade{h}", (0.003, 0.004, 0.36), bevel=0.0, mat=blade_m, loc=(xb, YH - 0.012, ZQ))
    K.show(bl, [(0, False), (f_cut - 8, True), (f_cut + 20, False)])
    blades.append(bl)
K.glow_keys(blade_m, [(0, 0.0), (f_cut - 6, 0.0), (f_cut, 8.0), (f_cut + 16, 0.0)])
f_fan = f_64
f_back = w("b9", "side")
for h, (r, m) in enumerate(slices):
    K.show(r, [(0, False), (f_cut + 4, True), (b["b4"]["f0"] + 10, False)])
    z_arc = ZQ + 0.06 * math.cos((h - 6.5) / 6.5 * 1.3)
    K.key(r, "location", [(f_cut + 4, (SL_PACK[h], YH, ZQ)), (f_fan + 4, (SL_PACK[h], YH, ZQ)), (f_fan + 26, (SL_FAN[h], YH, z_arc))])
    K.glow_keys(m, [(0, 4.0), (f_each + h * 2, 4.0), (f_each + h * 2 + 6, 7.5), (f_each + h * 2 + 24, 4.0)])
f_same2 = f_same
H24 = [HEADS[(24, h)] for h in range(14)]
for h in range(14):
    pk = H24[h]["last_peak"]
    src = Vector((SL_FAN[h], YH - 0.02, ZQ - 0.17))
    m_ = K.light_mat(f"fan{h}_m", K.SKY, 0.0)
    a = K.arc(f"fan{h}", src, top(pk["pos"]), lift=0.12 + 0.05 * abs(X(pk["pos"])) ** 0.5, r=0.0035 + 0.012 * min(1.0, pk["w"] / 0.35) ** 0.5, mat=m_)
    f0 = f_each + h * 3
    g = 0.6 + 6.0 * min(1.0, pk["w"] / 0.35) ** 0.6
    K.grow(a, [(0, 0.0), (f0, 0.0), (f0 + 18, 1.0)])
    K.glow_keys(m_, [(0, 0.0), (f0, 0.0), (f0 + 6, g), (b["b3"]["f1"], g), (b["b3"]["f1"] + 16, 0.0)])
    K.show(a, [(0, False), (f0 - 2, True), (b["b3"]["f1"] + 18, False)])

# b3: two key plates and two value plates, each shared by 7 query heads
f_share, f_two, f_seven = w("b3", "share"), w("b3", "two"), w("b3", "seven")
for g in range(2):
    for r in kv[g]:
        K.show(r, [(0, False), (f_share - 4, True), (b["b4"]["f0"] + 10, False)])
        K.key(r, "scale", [(f_share - 4, (0.02, 1, 0.02)), (f_share + 14, (1, 1, 1))])
    cx = -0.6 if g == 0 else 0.6
    for h in range(7 * g, 7 * g + 7):
        m_ = K.light_mat(f"kvl{h}_m", K.lin("#c9b6ff"), 0.0)
        bm = K.beam(f"kvl{h}", (SL_FAN[h], YH - 0.004, ZQ - 0.19), (cx, YH - 0.004, ZKV + 0.19), r=0.0025, mat=m_)
        f0 = f_seven - 6 + (h - 7 * g) * 3
        K.key(bm, "scale", [(0, (1, 1, 0.001)), (f0, (1, 1, 0.001)), (f0 + 12, (1, 1, 1))])
        K.glow_keys(m_, [(0, 0.0), (f0, 0.0), (f0 + 6, 4.0), (b["b3"]["f1"] + 20, 4.0), (b["b3"]["f1"] + 36, 0.0)])
        K.show(bm, [(0, False), (f0 - 2, True), (b["b4"]["f0"] + 10, False)])

# b4-b8: five real heads on the row
f_real, f_nine, f_every, f_84 = w("b4", "real"), w("b4", "nine"), w("b4", "average"), w("b4", "eighty-four")
PREV = MATS["9.7"]
A_PREV = {}
for i in range(1, 100):
    wt = PREV[i][i - 1]
    if wt < 0.05:
        continue
    m_ = K.light_mat(f"pv{i}_m", HC["prev"], 0.0)
    A_PREV[i] = (K.arc(f"pv{i}", top(i), top(i - 1), lift=0.07, r=0.0035 + 0.009 * wt, mat=m_), m_, wt)
f_twelve = w("b5", "twelve")
for i, (o, m_, wt) in A_PREV.items():
    f0 = f_nine + 6 + int((i - 60) * 1.2) if i >= 60 else f_nine + 6
    g = 0.5 + 6.0 * wt
    K.grow(o, [(0, 0.0), (f0, 0.0), (f0 + 10, 1.0)])
    K.glow_keys(m_, [(0, 0.0), (f0, 0.0), (f0 + 4, g), (f_twelve - 10, g), (f_twelve + 6, 0.0)])
    K.show(o, [(0, False), (f0 - 2, True), (f_twelve + 8, False)])
f_all, f_first, f_rests = w("b5", "all"), w("b5", "first"), w("b5", "rests")
f_tf = w("b6", "twenty-four")
REST = MATS["12.13"]
A_REST = {}
for i in range(1, 100):
    wt = REST[i][0]
    if wt < 0.05:
        continue
    m_ = K.light_mat(f"rs{i}_m", HC["rest"], 0.0)
    d = X(i) - X(0)
    A_REST[i] = (K.arc(f"rs{i}", top(i), top(0), lift=0.25 + 0.035 * d, r=0.004 + 0.004 * wt, mat=m_), m_, wt)
for i, (o, m_, wt) in A_REST.items():
    f0 = f_all + int(i * 0.25)
    K.grow(o, [(0, 0.0), (f0, 0.0), (f0 + 24, 1.0)])
    K.glow_keys(m_, [(0, 0.0), (f0, 0.0), (f0 + 6, 2.6 * wt), (f_tf - 12, 2.6 * wt), (f_tf + 4, 0.0)])
    K.show(o, [(0, False), (f0 - 2, True), (f_tf + 6, False)])
K.glow_keys(tiles[0][1], [(0, 0.0), (f_first - 4, 0.0), (f_first + 10, 3.4), (f_tf - 10, 3.4), (f_tf + 6, 0.0)])

f_place, f_65, f_man6 = w("b6", "place"), w("b6", "sixty-five"), w("b6", "manchester")
f_nt = w("b7", "nineteen")
A_PL = PB.arc_set("pl", top(LAST), top, {j: MATS["24.2"][LAST][j] for j in range(LAST)}, HC["place"], min_w=0.006, ref=0.35)
PB.light_arcs(A_PL, f_place - 4, f_nt - 10, LAST, ref=0.35, stagger=0.1)
K.glow_keys(tiles[MAN][1], [(0, 0.0), (f_65 - 4, 0.0), (f_65 + 10, 3.0), (f_nt - 10, 3.0), (f_nt + 4, 0.0)])
f_rd, f_80, f_36 = w("b7", "reads"), w("b7", "eighty"), w("b7", "thirty-six")
f_write = w("b8", "write")
A_Q = PB.arc_set("qu", top(LAST), top, {j: MATS["19.13"][LAST][j] for j in range(LAST)}, HC["question"], min_w=0.006, ref=0.35)
PB.light_arcs(A_Q, f_rd - 4, f_write - 8, LAST, ref=0.35, stagger=0.1)
for i in range(80, 95):
    K.glow_keys(tiles[i][1], [(0, 0.0), (f_80 - 4, 0.0), (f_80 + 8, 1.4 if i != STORES else 3.0), (f_write - 8, 1.4 if i != STORES else 3.0),
                              (f_write + 6, 0.0)])

# b8: the answer so far drops onto the plinth; at the step that writes the first digit, block 2 head 7 looks at the date
f_two, f_dig, f_date, f_17, f_oct = w("b8", "two"), w("b8", "digits"), w("b8", "date"), w("b8", "seventeen"), w("b8", "october")
f_hands = w("b9", "hands")
for k in range(len(GEN)):
    i = 100 + k
    root = tiles[i][0]
    z = root.location.z
    f0 = f_write - 6 + k * 5
    K.show(root, [(0, False), (f0, True)])
    K.key(root, "location", [(f0, (X(i), 0, z + 0.5)), (f0 + 12, (X(i), 0, z))])
    K.glow_keys(tiles[i][1], [(0, 0.0), (f0 + 8, 0.0), (f0 + 16, 1.6 if i < 103 else 3.0), (END, 1.6 if i < 103 else 3.0)])
QD = 100 + len(GEN) - 1
ROWD = DIG["rows"]["2.7"]
A_D = PB.arc_set("dg", top(QD), top, {j: ROWD[j] for j in range(QD)}, HC["digits"], min_w=0.008, ref=0.2)
PB.light_arcs(A_D, f_two - 4, f_hands - 10, QD, ref=0.2, stagger=0.06, gain=5.0)
DD = HD["date_digits_pos"] if "date_digits_pos" in HD else [44, 45, 48, 49, 50, 51]
for i in DD:
    K.glow_keys(tiles[i][1], [(0, 0.0), (f_dig - 4, 0.0), (f_dig + 8, 3.0), (f_hands - 10, 3.0), (f_hands + 4, 0.0)])

# b9: 14 head outputs join into 896, pass the output matrix, and are added to the last token's vector
f_14, f_again, f_out, f_mix, f_add = w("b9", "fourteen"), w("b9", "again"), w("b9", "output"), w("b9", "mixes"), w("b9", "added")
for h, (r, m) in enumerate(outs):
    f0 = f_hands + h * 2
    z_arc = ZQ + 0.06 * math.cos((h - 6.5) / 6.5 * 1.3)
    K.show(r, [(0, False), (f0 - 2, True), (f_again + 2, False)])
    K.key(r, "location", [(f0, (SL_FAN[h], YH, z_arc + 0.3)), (f0 + 12, (SL_FAN[h], YH, z_arc)), (f_back - 4, (SL_FAN[h], YH, z_arc)),
                          (f_again - 6, (SL_PACK[h], YH, ZQ))])
    K.key(r, "scale", [(f0, (0.05, 1, 0.05)), (f0 + 12, (1, 1, 1))])
K.show(joined, [(0, False), (f_again - 4, True), (f_mix + 10, False)])
K.key(joined, "location", [(f_again - 4, (0, YH, ZQ)), (f_out - 2, (0, YH, ZQ)), (f_mix + 8, (1.4, YH - 0.03, ZQ))])
K.key(joined, "scale", [(f_mix - 2, (1, 1, 1)), (f_mix + 10, (0.42, 1, 1))])
K.glow_keys(wo_m, [(0, 0.0), (f_out - 6, 0.0), (f_out + 6, 2.4), (f_mix + 6, 6.0), (f_add, 2.0)])
K.show(wo, [(0, False), (f_out - 12, True)])
K.key(wo, "location", [(f_out - 12, (1.4, YH + 0.02, ZQ + 0.9)), (f_out + 6, (1.4, YH + 0.02, ZQ))])
K.show(oplate, [(0, False), (f_mix + 8, True), (f_add + 22, False)])
K.key(oplate, "location", [(f_mix + 8, (1.4, YH - 0.03, ZQ)), (f_mix + 24, (2.5, YH, ZQ)), (f_add - 8, (2.5, YH, ZQ)), (f_add + 18, (0, YH - 0.04, ZR))])
K.key(oplate, "scale", [(f_mix + 8, (0.42, 1, 1)), (f_mix + 24, (1, 1, 1))])
K.show(res_in, [(f_add + 18, False)])
K.show(res_out, [(0, False), (f_add + 18, True)])
K.glow_keys(res_out_m, [(0, 4.4), (f_add + 18, 9.0), (f_add + 40, 4.4)])

# b10: the 24 x 14 head stack rises behind the hub
f_14b, f_336 = w("b10", "fourteen"), w("b10", "three")
TW = K.tower("tower", (3.7, 1.9, 0.0), floors=24, pitch=0.1, w=2.0, d=0.7,
             lit={(24, 2), (9, 7), (12, 13), (19, 13), (2, 7)})
for k, fr in enumerate(TW["floors"], start=1):
    z = fr.location.z
    t0 = f_14b - 20 + int((k - 1) * 1.2)
    K.show(fr, [(0, False), (t0, True)])
    K.key(fr, "location", [(0, (0, 0, z + 1.6)), (t0, (0, 0, z + 1.6)), (t0 + 20, (0, 0, z))])
for ch in TW["root"].children:
    if "_post" in ch.name:
        K.show(ch, [(0, False), (f_14b - 20, True)])
K.glow_keys(TW["idle"], [(0, 0.0), (f_336 - 6, 0.0), (f_336 + 20, 2.0), (END, 2.4)])
for (k, j), colr in (((24, 2), HC["place"]), ((9, 7), HC["prev"]), ((12, 13), HC["rest"]), ((19, 13), HC["question"]), ((2, 7), HC["digits"])):
    m_ = TW["heads"][(k, j)][1]
    m_.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = colr
    K.glow_keys(m_, [(0, 0.0), (f_336 + 10, 0.0), (f_336 + 26, 7.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_hub", lens=35, fstop=3.5).cut(0)
c1.keys([(0, (1.6, -4.2, 1.8), (-0.6, 0.0, 0.9)),
         (f_man1, (0.4, -4.6, 2.0), (-1.8, 0.0, 0.8)),
         (b["b1"]["f1"] + 10, (0.6, -4.4, 1.9), (-1.3, 0.0, 0.9))])
c2 = K.Cam(sc, "c_split", lens=38, fstop=4.0).cut(b["b2"]["f0"] - 4)
c2.keys([(b["b2"]["f0"] - 4, (0.3, -3.0, 1.5), (0.0, YH, 1.25)),
         (f_cut + 10, (0.2, -3.0, 1.75), (0.0, YH, 1.5)),
         (f_each, (0.3, -3.6, 1.9), (0.0, YH, 1.45)),
         (f_same + 6, (-0.4, -5.0, 2.3), (-0.9, YH, 1.1))])
c3 = K.Cam(sc, "c_share", lens=38, fstop=4.0).cut(b["b3"]["f0"] - 4)
c3.keys([(b["b3"]["f0"] - 4, (0.3, -3.5, 1.85), (0.0, YH, 1.45)), (b["b3"]["f1"] + 20, (-0.2, -3.2, 1.8), (0.0, YH, 1.45))])
c4 = K.Cam(sc, "c_prev", lens=32, fstop=3.5).cut(b["b4"]["f0"] - 4)
c4.keys([(b["b4"]["f0"] - 4, (X(70), -3.4, 1.2), (X(76), 0.0, 0.25)),
         (f_every, (X(84), -2.6, 0.95), (X(88), 0.0, 0.2)),
         (b["b4"]["f1"] + 10, (X(90), -2.6, 0.95), (X(94), 0.0, 0.2))])
c5 = K.Cam(sc, "c_rest", lens=28, fstop=6.0).cut(b["b5"]["f0"] - 4)
c5.keys([(b["b5"]["f0"] - 4, (X(0) - 3.5, -6.0, 2.6), (X(0) + 8.0, 0.0, 1.0)),
         (f_tf - 8, (X(0) - 4.5, -7.5, 3.4), (X(0) + 10.0, 0.0, 1.2))])
c6 = K.Cam(sc, "c_place", lens=32, fstop=3.5).cut(b["b6"]["f0"] - 4)
c6.keys([(b["b6"]["f0"] - 4, (X(92), -3.8, 1.6), (X(91), 0.0, 0.35)),
         (b["b7"]["f1"] + 6, (X(93), -3.6, 1.5), (X(90), 0.0, 0.35))])
c8 = K.Cam(sc, "c_digits", lens=30, fstop=5.0).cut(b["b8"]["f0"] - 4)
c8.keys([(b["b8"]["f0"] - 4, (X(96), -3.4, 1.2), (X(100), 0.0, 0.3)), (f_write + 26, (X(97), -3.2, 1.15), (X(101), 0.0, 0.3)),
         (f_two, (X(80), -12.0, 3.4), (X(72), 0.0, 0.5)),
         (f_date, (X(51), -3.4, 1.3), (X(47), 0.0, 0.3)),
         (b["b8"]["f1"] + 10, (X(50), -3.2, 1.25), (X(46.5), 0.0, 0.25))])
c9 = K.Cam(sc, "c_join", lens=35, fstop=4.0).cut(b["b9"]["f0"] - 4)
c9.keys([(b["b9"]["f0"] - 4, (0.3, -3.4, 1.65), (0.1, YH, 1.4)),
         (f_out - 4, (1.25, -4.1, 1.75), (1.25, YH, 1.35)),
         (f_add, (1.15, -4.2, 1.65), (1.15, YH, 1.25)),
         (b["b9"]["f1"] + 14, (0.9, -4.0, 1.55), (0.8, YH, 1.15))])
c10 = K.Cam(sc, "c_end", lens=32, fstop=5.0).cut(b["b10"]["f0"] - 4)
c10.keys([(b["b10"]["f0"] - 4, (1.2, -4.6, 1.9), (2.2, 1.2, 1.2)), (END, (2.0, -4.6, 2.2), (3.3, 1.7, 1.25))])

pins = [f"tok{i}_top" for i in range(NT)] + [f"tok{i}_front" for i in range(NT)]
pins += ["res_top", "res2_top", "qbig_top", "joined_top", "oplate_top", "wo_top", "hmod_top", "k0_top", "v0_top", "k1_top", "v1_top"]
pins += [f"qs{h}_top" for h in range(14)] + [f"os{h}_top" for h in range(14)] + [f"qs{h}_bot" for h in (0, 6, 7, 13)]
pins += ["tower_pin_f24", "tower_pin_f19", "tower_pin_f12", "tower_pin_f9", "tower_pin_f2"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
