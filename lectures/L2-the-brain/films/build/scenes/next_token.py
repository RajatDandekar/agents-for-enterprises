"""Film `next_token`: "From the last vector to the next token: logits and softmax". Builds films/next_token.blend.

One world along x (left to right, the order of the story):
  recap   Emma's 100 tokens on the plinth, each with its vector column (first 16 of 896 numbers per token, recorded
          after every block: build/data/structure_data.json); the columns change block by block 1..24; only the last
          position's column is kept.
  norm    that column becomes the full 896-cell plate (its real values BEFORE the final RMSNorm), passes through the
          norm unit and leaves with its real normed values (build/data/next_token_data.json pre_norm / post_norm).
  table   the (tied) table as a rack of trays with real rows (build/data/next_token_rows.json); the We row is pulled out
          and multiplied with the vector cell by cell while a glass meter follows the real running sum to 20.84; then
          the input side: a "We" tile reads the same row.
  logits  a histogram of all 151,936 logits (real counts), then 7 glass meters: the top 6 tokens and "all the rest":
          logits -> e^logit -> probabilities (exact) -> temperature 0 / 0.7 / 1.2 (exact, trace.json final.dial_last).
  wheel   a weighted wheel (sectors = the real probabilities at T = 1) spun five times to the five real draws
          (seed 0: As, City, We, We, We).
  pick    a "We" tile rises and lands at the end of Emma's text (position 100).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_next_gen as NG  # noqa: E402

FILM = "next_token"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
ND = K.load("films/build/data/next_token_data.json")
RW = K.load("films/build/data/next_token_rows.json")
SD = K.load("films/build/data/structure_data.json")
TOK = T["tokens"]
TOP = ND["top"][:6]
w = B.w
END = B.frames - 1
blk = B.blocks

sc = K.reset(B.frames)
K.studio(sc, focus=(-3.0, 0.0, 0.5), key_power=3000, span=9.0)
K.soft_light("rowkey", (-14.0, -6.5, 7.5), (-14.0, 0, 0.3), 1500, 12.0, (1.0, 0.97, 0.93))
K.soft_light("rowrim", (-14.0, 7.0, 3.2), (-14.0, 0, 0.3), 1000, 14.0, (0.7, 0.82, 1.0))
PZ = 0.11


def XR(i):
    return -9.0 + (i - 99) * 0.36


K.plinth("plinth", XR(0) - 0.5, 6.4, depth=0.6, height=PZ)
K.plinth("plinth_back", -6.2, 5.6, y=0.75, depth=0.9, height=PZ)

# ------------------------------------------------------------------------------------------------ recap: the row
L = SD["layers"]                       # 25 x 100 x 16
vm = []
for l in range(25):
    a = sorted(abs(x) for t in L[l][1:] for x in t)
    vm.append(a[int(len(a) * 0.95)] or 1.0)
f_tok, f_vec = w("b1", "hundred"), w("b1", "vector")
f_blk0, f_blk1 = w("b1", "twenty-four"), w("b1", "pass")
f_keep = w("b1", "keep")
tiles, cols = {}, {}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (XR(i), 0, PZ))
    tiles[i] = (root, fm)
    # every tile's face lights in reading order on "one hundred tokens"
    fi = f_tok - 30 + int(40 * i / 99)
    K.glow_keys(fm, [(0, 0.0), (fi, 0.0), (fi + 6, 1.6), (fi + 26, 0.35)] + ([(f_keep, 0.35), (f_keep + 20, 0.12)] if i != 99 else [(f_keep, 0.35), (f_keep + 20, 1.4)]))
    cr, cm = NG.layered_column(f"c{i}", [L[l][i] for l in range(25)], (XR(i), 0.02, PZ + 0.075 + 0.03 + 8 * 0.022 + 0.012), vmaxs=vm)
    cols[i] = (cr, cm)
    fc = f_vec - 20 + int(36 * i / 99)
    K.show(cr, [(0, False), (fc, True)])
    z1 = cr.location.z
    K.key(cr, "scale", [(0, (1, 1, 0.02)), (fc, (1, 1, 0.02)), (fc + 14, (1, 1, 1.0))])
    gk = [(0, 0.0), (fc, 0.0), (fc + 12, 3.2)]
    if i != 99:
        gk += [(f_keep, 3.2), (f_keep + 22, 0.5)]
    else:
        gk += [(f_keep, 3.2), (f_keep + 16, 6.0)]
    K.glow_keys(cm, gk)
    # the 24 blocks: layer 0 -> 24 while the narrator says "Twenty-four blocks updated every vector, in one pass"
    lay = cm.node_tree.nodes["layer"].outputs[0]
    K.keyval(lay, [(0, 0.0), (f_blk0, 0.0), (f_blk1 + 8, 24.0)])
LASTC = cols[99][0]
# the kept column lifts
K.key(LASTC, "location", [(f_keep, LASTC.location.copy()), (f_keep + 24, LASTC.location + Vector((0, 0, 0.12)))])

# ------------------------------------------------------------------------------------------------ norm: the full vector
PRE, POST = ND["pre_norm"]["values"], ND["post_norm"]["values"]
NU = Vector((-7.25, 0.0, 0.95))
nunit, nring = NG.norm_unit("norm", tuple(NU), length=0.62, h=0.6, w=0.2)
CELL = 0.014
pre_p, pre_m = K.vector_plate("pre", PRE, 28, 32, K.SKY, (-8.1, 0.0, NU.z), cell=CELL, vmax=4.0, glow=0.0)
post_p, post_m = K.vector_plate("post", POST, 28, 32, K.SKY, (-8.1, 0.0, NU.z), cell=CELL, vmax=26.0, glow=0.0)
f_q = blk["b2"]["f0"]
f_norm, f_div, f_gain = w("b3", "rms"), w("b3", "divides"), w("b3", "multiplies")
f_root = w("b3", "root")
# the small column flies to the norm unit's mouth and becomes the full plate
K.key(LASTC, "location", [(f_q - 6, LASTC.location + Vector((0, 0, 0.12))), (f_q + 40, Vector((-8.1, 0.0, NU.z)))])
K.show(LASTC, [(0, False), (w("b1", "vector") - 20 + 36, True), (f_q + 40, False)])
K.show(pre_p, [(0, False), (f_q + 38, True), (f_gain - 6, False)])
K.glow_keys(pre_m, [(0, 0.0), (f_q + 36, 0.0), (f_q + 46, 4.4)])
K.key(pre_p, "scale", [(f_q + 36, (0.2, 1, 0.6)), (f_q + 52, (1, 1, 1))])
# through the unit: it enters on "divides", is inside on "root mean square", leaves (normed) on "multiplies"
for p_ in (pre_p, post_p):
    K.key(p_, "location", [(0, (-8.1, 0.0, NU.z)), (f_div - 4, (-8.1, 0.0, NU.z)), (f_root + 10, (NU.x, 0.0, NU.z)),
                           (f_gain - 6, (NU.x, 0.0, NU.z)), (f_gain + 30, (-6.35, 0.0, NU.z))])
K.show(post_p, [(0, False), (f_gain - 6, True)])
K.glow_keys(post_m, [(0, 0.0), (f_gain - 6, 2.0), (f_gain + 20, 4.4)])
K.glow_keys(nring, [(0, 0.3), (f_norm - 10, 0.3), (f_norm + 6, 4.0), (f_root, 6.0), (f_gain + 30, 4.0), (blk["b4"]["f0"] + 30, 1.0)])

# ------------------------------------------------------------------------------------------------ the table rack
rows = sorted(RW["spaced"][1:37] + RW["top6"], key=lambda r: r["id"])
k_we = next(k for k, r in enumerate(rows) if r["id"] == 1654)
RACK = Vector((-4.7, 0.62, PZ + 0.07))
rack = NG.tray_rack("rack", rows, tuple(RACK), pitch=0.04)
f_tab, f_rows = w("b4", "table"), w("b4", "rows")
f_mul, f_add, f_dot = w("b4", "multiply"), w("b4", "add"), w("b4", "dot")
f_we4, f_2084 = w("b4", "we"), w("b4", "twenty")
for k, (tr, m) in enumerate(rack["trays"]):
    fk = f_rows - 16 + int(30 * k / len(rows))
    K.glow_keys(m, [(0, 0.5), (f_tab - 10, 0.5), (f_tab + 10, 1.4), (fk, 1.4), (fk + 4, 5.0), (fk + 22, 1.4)]
                + ([(f_mul - 20, 1.4), (f_mul, 0.5)] if k != k_we else [(f_mul - 20, 1.4), (f_mul, 3.4)]))
# the normed vector flies to the rack front and stands; the We tray slides out and stands beside it
VPOS = Vector((-5.55, -0.12, 1.12))
TPOS = Vector((-5.05, -0.12, 1.12))
K.key(post_p, "location", [(blk["b4"]["f0"] - 4, (-6.35, 0.0, NU.z)), (f_tab + 30, tuple(VPOS))])
we_tr, we_m = rack["trays"][k_we]
zt = rack["z"][k_we]
home = Vector((0, 0, zt))
out_ = Vector((0, -0.5, zt))
K.key(we_tr, "location", [(0, home), (f_mul - 26, home), (f_mul - 8, out_), (f_mul + 12, TPOS - RACK)])
we_tr.rotation_euler = (0, 0, 0)
K.key(we_tr, "rotation_euler", [(f_mul - 8, (0, 0, 0)), (f_mul + 12, (math.pi / 2, 0, 0))])
# cell by cell: both plates dim, then re-light in reading order while the meter follows the real running sum
cs = ND["dots"][0]["cumsum_every32"]
f_r0, f_r1 = f_mul + 18, f_2084 + 6
for m in (post_m, we_m):
    rv = m.node_tree.nodes["reveal"].outputs[0]
    K.keyval(rv, [(0, 1.0), (f_r0 - 6, 1.0), (f_r0, 0.0), (f_r1, 1.0)])
dm_root, dm_liq, dm_lm = K.meter("dotm", (-4.65, -0.12, PZ), height=1.05, r=0.035, color=K.SKY)
K.show(dm_root, [(0, False), (f_mul + 6, True), (blk["b5"]["f0"] + 40, False)])
lv = [(f_r0 - 2, (1, 1, 0.001))]
for j, c in enumerate(cs):
    fr = f_r0 + int((f_r1 - f_r0) * (j + 1) / len(cs))
    lv.append((fr, (1, 1, max(0.001, c / 22.0))))
K.key(dm_liq, "scale", [(0, (1, 1, 0.001))] + lv)
K.glow_keys(dm_lm, [(0, 0.0), (f_r0, 0.0), (f_r0 + 6, 4.0)])
# b5: the tray goes home; the vector plate moves to the out side; a "We" tile reads the same row on the in side
f_tb, f_emb, f_reads, f_out, f_tied = w("b5", "table"), w("b5", "embedding"), w("b5", "reads"), w("b5", "out"), w("b5", "tied")
K.key(we_tr, "location", [(blk["b5"]["f0"] - 6, TPOS - RACK), (blk["b5"]["f0"] + 18, out_), (blk["b5"]["f0"] + 34, home)])
K.key(we_tr, "rotation_euler", [(blk["b5"]["f0"] - 6, (math.pi / 2, 0, 0)), (blk["b5"]["f0"] + 18, (0, 0, 0))])
OUTV = Vector((-4.05, 0.3, 1.2))
K.key(post_p, "location", [(blk["b5"]["f0"] - 6, tuple(VPOS)), (blk["b5"]["f0"] + 30, tuple(OUTV))])
K.glow_keys(we_m, [(f_emb - 6, 1.6), (f_emb + 8, 5.0), (f_out + 20, 5.0), (blk["b6"]["f0"], 1.4)])
INT = Vector((-5.45, 0.3, PZ))
in_tile, in_face = K.token_tile("intile", "answer", tuple(INT))
K.bsdf(in_face).inputs["Emission Color"].default_value = K.SKY
K.show(in_tile, [(0, False), (f_tb - 10, True)])
K.key(in_tile, "location", [(0, INT + Vector((0, 0, 0.4))), (f_tb - 10, INT + Vector((0, 0, 0.4))), (f_tb + 8, INT)])
K.glow_keys(in_face, [(0, 0.0), (f_tb, 0.0), (f_tb + 10, 2.4)])
bm_in = K.light_mat("beam_in", K.SKY, 0.0)
bm_out = K.light_mat("beam_out", K.SKY, 0.0)
we_left = RACK + Vector((-0.2, -0.08, zt))
b_in = K.beam("b_in", INT + Vector((0, 0, 0.09)), we_left, r=0.006, mat=bm_in)
b_out = K.beam("b_out", OUTV + Vector((-0.2, 0.0, 0)), RACK + Vector((0.2, -0.05, zt)), r=0.006, mat=bm_out)
K.key(b_in, "scale", [(0, (1, 1, 0.001)), (f_reads - 8, (1, 1, 0.001)), (f_reads + 8, (1, 1, 1))])
K.glow_keys(bm_in, [(0, 0.0), (f_reads - 8, 4.0), (blk["b6"]["f0"], 4.0), (blk["b6"]["f0"] + 10, 0.0)])
K.key(b_out, "scale", [(0, (1, 1, 0.001)), (f_out - 14, (1, 1, 0.001)), (f_out + 4, (1, 1, 1))])
K.glow_keys(bm_out, [(0, 0.0), (f_out - 14, 4.0), (blk["b6"]["f0"], 4.0), (blk["b6"]["f0"] + 10, 0.0)])
K.empty("in_col_pin", tuple(INT + Vector((0, -0.12, 0.08))))

# ------------------------------------------------------------------------------------------------ logits: histogram + meters
H = ND["logits"]["hist"]
lo, hi, nb = H["lo"], H["hi"], H["bins"]
hot = int((18.0 - lo) / (hi - lo) * nb)
HX = Vector((-1.7, 0.75, PZ))
hroot, bars, (hcool, hhot) = NG.hist_bars("hist", H["counts"], tuple(HX), pitch=0.05, hmax=0.7, hot_from=hot)
f_logit, f_18 = w("b6", "logit"), w("b6", "eighteen")
f_five = w("b6", "five")
for k, piv in enumerate(bars):
    fk = blk["b6"]["f0"] - 4 + int(26 * k / nb)
    K.key(piv, "scale", [(0, (1, 1, 0.001)), (fk, (1, 1, 0.001)), (fk + 14, (1, 1, 1))])
K.glow_keys(hcool, [(0, 0.0), (blk["b6"]["f0"], 0.0), (blk["b6"]["f0"] + 30, 1.2)])
K.glow_keys(hhot, [(0, 0.0), (blk["b6"]["f0"], 0.0), (blk["b6"]["f0"] + 30, 1.6), (f_five, 1.6), (f_five + 10, 6.0)])
K.empty("hist_lo", tuple(HX + Vector((-(nb - 1) / 2 * 0.05, -0.1, 0.0))))
K.empty("hist_hi", tuple(HX + Vector(((nb - 1) / 2 * 0.05, -0.1, 0.0))))
K.empty("hist_zero", tuple(HX + Vector(((0 - lo) / (hi - lo) * nb * 0.05 - nb * 0.05 / 2, -0.1, 0.0))))

MX = [0.15 + j * 0.3 for j in range(7)]
MY = -0.05
meters = []
for j in range(7):
    mr, liq, lm = K.meter(f"m{j}", (MX[j], MY, PZ), height=0.7, r=0.042, color=K.SKY if j < 6 else K.lin("#8aa4c8"))
    meters.append((mr, liq, lm))
import next_gen_sched as NS  # noqa: E402
MS = NS.Meters(B.tl, ND, T["final"]["dial_last"])
TT = MS.T
f_we6 = w("b6", "we")
f_raise, f_div7, f_56 = MS.f_raise, MS.f_div, MS.f_56
f_dial = MS.f_dial
f_five = MS.f_five


def level(j, fr):
    m, lv_, _ = MS.level(j, fr)
    return m, lv_


for j, (mr, liq, lm) in enumerate(meters):
    keys, gk = [], []
    for fr in range(f_five - 20, END + 1, 2):
        mode, lv_ = level(j, fr)
        keys.append((fr, (1, 1, max(0.001, min(1.0, lv_)))))
        gk.append((fr, 0.0 if mode == "off" else 2.6 + 3.0 * min(1.0, lv_)))
    K.key(liq, "scale", [(0, (1, 1, 0.001))] + keys)
    K.glow_keys(lm, [(0, 0.0)] + gk)
    K.show(mr, [(0, False), (f_five - 22 if j < 6 else f_div7 - 6, True)])
# greedy: the We meter flashes on "We, every time"
f_greedy, f_wetime = w("b8", "greedy"), w("b8", "every")

# temperature dial (the same machined dial as the series), to the right of the meters
DIAL = Vector((MX[-1] + 0.62, MY - 0.05, 0.62))
import props_s456 as P4  # noqa: E402
dl, knob = P4.dial("dial", tuple(DIAL), r=0.12)
K.rbox("dial_stand", (0.12, 0.12, DIAL.z - 0.12 * 1.6 - PZ), bevel=0.01, seg=3, mat=K.M("alu_dark"),
       loc=(DIAL.x, DIAL.y + 0.06, PZ + (DIAL.z - 0.12 * 1.6 - PZ) / 2))
K.show(dl, [(0, False), (f_dial - 30, True)])
K.key(knob, "rotation_euler", [(fr, (0, P4.dial_angle(max(0.0, TT(fr))), 0)) for fr in range(f_dial - 30, END + 1, 2)])

# ------------------------------------------------------------------------------------------------ the wheel
tops12 = ND["top"][:12]
sect = []
for j, t in enumerate(tops12):
    col = K.SKY if j == 0 else (K.lin("#2f6ad0") if j < 6 else K.lin("#25467a"))
    sect.append((f"k{j}", t["p"], col, 1.25 if j == 0 else (0.9 if j < 6 else 0.6)))
sect.append(("rest", 1 - sum(t["p"] for t in tops12), K.lin("#1a2233"), 0.15))
WC = Vector((3.75, 0.25, 0.78))
wroot, wdisk, winfo = NG.wheel("wheel", sect, tuple(WC), r=0.46)
draw_keys = ["k1", "k11", "k0", "k0", "k0"]          # As, City, We, We, We (seed 0, T = 1.0, next_token_data first5_draws)
fracs = [0.5, 0.5, 0.35, 0.62, 0.48]
f_spin0 = w("b8", "sampling")
f_land = [w("b8", "as"), w("b8", "city") + 6, w("b8", "we", 1), w("b8", "we", 2), w("b8", "we", 3)]
ang = 0.0
rk = [(0, (0, 0.0, 0)), (f_spin0, (0, 0.0, 0))]
for n, (kk, fr, fl) in enumerate(zip(draw_keys, fracs, f_land)):
    tgt = -NG.wheel_angle_for(winfo, kk, fr)
    turns = 2 if n == 0 else 1
    new = tgt
    while new > ang - 2 * math.pi * turns + 0.3:
        new -= 2 * math.pi
    ang = new
    rk.append((fl, (0, ang, 0)))
    rk.append((fl + (4 if n < 4 else 30), (0, ang, 0)))
K.key(wdisk, "rotation_euler", rk)
for kk, (a0, a1, m) in winfo.items():
    base = m.node_tree.nodes["glow"].outputs[0].default_value
    K.glow_keys(m, [(0, base)])

# ------------------------------------------------------------------------------------------------ pick: the We tile
f_choice, f_joins, f_runs = w("b10", "choice"), w("b10", "joins"), w("b10", "runs")
pk, pkf = K.token_tile("pick", "answer", (MX[0], MY, PZ))
K.bsdf(pkf).inputs["Emission Color"].default_value = K.SKY
K.show(pk, [(0, False), (f_choice - 16, True)])
K.key(pk, "location", [(0, (MX[0], MY + 0.12, PZ)), (f_choice - 16, (MX[0], MY + 0.12, PZ)), (f_choice + 10, (MX[0], MY - 0.25, 0.95))])
K.glow_keys(pkf, [(0, 0.0), (f_choice - 10, 0.0), (f_choice + 8, 3.0)])
# at the row's end: the same tile lands at position 100
ansf, ansface = K.token_tile("tok100", "answer", (XR(100), 0, PZ))
K.bsdf(ansface).inputs["Emission Color"].default_value = K.SKY
K.show(ansf, [(0, False), (f_joins - 16, True)])
K.key(ansf, "location", [(0, (XR(100), 0, PZ + 0.5)), (f_joins - 16, (XR(100), 0, PZ + 0.5)), (f_joins + 4, (XR(100), 0, PZ))])
K.glow_keys(ansface, [(0, 0.0), (f_joins - 4, 0.0), (f_joins + 6, 3.0), (f_joins + 30, 1.4)])
# "the whole machine runs again": every column relights in a sweep toward the end
for i in range(60, 99):
    cm = cols[i][1]
    fi = f_runs - 30 + int(30 * (i - 60) / 40)
    K.glow_keys(cm, [(f_joins, 0.5 if i != 99 else 6.0), (fi, 0.5), (fi + 8, 4.0), (fi + 30, 2.2)])
    K.show(cols[i][0], [(f_joins - 30, True)])
# the last column (it flew away) is shown again in its place for the final shot
c99b, cm99b = NG.layered_column("c99b", [L[l][99] for l in range(25)], (XR(99), 0.02, PZ + 0.075 + 0.03 + 8 * 0.022 + 0.012), vmaxs=vm)
K.keyval(cm99b.node_tree.nodes["layer"].outputs[0], [(0, 24.0)])
K.show(c99b, [(0, False), (f_joins - 30, True)])
K.glow_keys(cm99b, [(0, 0.0), (f_runs - 2, 0.5), (f_runs + 6, 4.0), (END, 2.2)])

# ------------------------------------------------------------------------------------------------ cameras
b = {k: blk[k] for k in blk}
c1 = K.Cam(sc, "c_row", lens=32, fstop=4.0).cut(0)
c1.keys([(0, (XR(104), -1.9, 0.95), (XR(86), 0.2, 0.25)),
         (f_vec, (XR(103), -2.1, 1.05), (XR(88), 0.2, 0.35)),
         (f_keep - 6, (XR(102.5), -1.9, 1.0), (XR(92), 0.1, 0.35)),
         (b["b1"]["f1"] + 10, (XR(101.5), -1.35, 0.8), (XR(97), 0.05, 0.42))])
c2 = K.Cam(sc, "c_norm", lens=40, fstop=4.5).cut(b["b2"]["f0"] - 4)
c2.keys([(b["b2"]["f0"] - 4, (XR(100.5), -1.9, 1.15), (-8.5, 0.0, 0.85)),
         (f_q + 44, (-8.0, -2.0, 1.2), (-7.9, 0.0, 0.92)),
         (f_div, (-7.75, -2.05, 1.15), (-7.5, 0.0, 0.92)),
         (f_gain + 30, (-6.85, -1.95, 1.12), (-6.7, 0.0, 0.92)),
         (b["b3"]["f1"] + 12, (-6.7, -1.9, 1.1), (-6.55, 0.0, 0.92))])
c3 = K.Cam(sc, "c_rack", lens=32, fstop=5.0).cut(b["b4"]["f0"] - 4)
c3.keys([(b["b4"]["f0"] - 4, (-6.9, -2.3, 1.35), (-5.4, 0.3, 0.95)),
         (f_rows, (-6.4, -2.6, 1.45), (-4.9, 0.4, 0.95)),
         (f_mul - 10, (-5.6, -2.1, 1.35), (-5.0, 0.2, 1.05))])
c4 = K.Cam(sc, "c_dot", lens=45, fstop=4.0).cut(f_mul + 4)
c4.keys([(f_mul + 4, (-5.12, -2.05, 1.28), (-5.12, -0.1, 1.08)),
         (f_2084 + 20, (-5.08, -1.9, 1.26), (-5.08, -0.1, 1.08))])
c5 = K.Cam(sc, "c_tied", lens=30, fstop=5.6).cut(b["b5"]["f0"] - 2)
c5.keys([(b["b5"]["f0"] - 2, (-5.0, -2.2, 1.4), (-4.9, 0.3, 0.95)),
         (f_tb, (-5.1, -2.7, 1.5), (-4.85, 0.35, 0.85)),
         (b["b5"]["f1"] + 12, (-4.85, -2.9, 1.55), (-4.8, 0.35, 0.85))])
c6 = K.Cam(sc, "c_hist", lens=32, fstop=5.6).cut(b["b6"]["f0"] - 4)
c6.keys([(b["b6"]["f0"] - 4, (-1.9, -2.3, 0.95), (-1.7, 0.6, 0.4)),
         (f_five, (-1.2, -2.4, 0.95), (-0.6, 0.5, 0.4)),
         (f_we6 - 10, (0.6, -2.6, 1.0), (0.75, 0.2, 0.42))])
c7 = K.Cam(sc, "c_meters", lens=36, fstop=5.6).cut(f_we6 - 8)
c7.keys([(f_we6 - 8, (0.95, -2.75, 0.95), (1.05, 0.1, 0.45)),
         (b["b7"]["f1"], (1.05, -2.85, 0.98), (1.1, 0.1, 0.45)),
         (f_greedy + 40, (1.0, -2.75, 0.95), (1.05, 0.1, 0.45))])
c8 = K.Cam(sc, "c_wheel", lens=40, fstop=4.0).cut(f_spin0 - 10)
c8.keys([(f_spin0 - 10, (3.75, -2.3, 0.95), (3.75, 0.2, 0.78)),
         (b["b8"]["f1"] + 10, (3.75, -2.1, 0.9), (3.75, 0.2, 0.78))])
c9 = K.Cam(sc, "c_temp", lens=34, fstop=5.6).cut(b["b9"]["f0"] - 6)
c9.keys([(b["b9"]["f0"] - 6, (1.4, -2.9, 1.0), (1.45, 0.1, 0.45)),
         (b["b9"]["f1"] + 10, (1.4, -2.75, 0.98), (1.4, 0.1, 0.45))])
c10 = K.Cam(sc, "c_pick", lens=36, fstop=4.5).cut(b["b10"]["f0"] - 4)
c10.keys([(b["b10"]["f0"] - 4, (0.6, -2.4, 1.0), (0.4, 0.0, 0.6)),
          (f_choice + 14, (0.45, -2.1, 1.05), (0.2, -0.2, 0.8))])
c11 = K.Cam(sc, "c_end", lens=32, fstop=4.0).cut(f_joins - 24)
c11.keys([(f_joins - 24, (XR(103.5), -1.7, 0.85), (XR(97), 0.1, 0.3)),
          (END, (XR(104.5), -2.1, 1.0), (XR(94), 0.1, 0.35))])

# ------------------------------------------------------------------------------------------------ pins
pins = [f"tok{i}_front" for i in range(60, 101)] + [f"tok{i}_top" for i in range(60, 101)] + ["c99_top", "c99_mid", "c99b_top"]
pins += ["pre_top", "pre_mid", "post_top", "post_mid", "norm_top", "norm_front", "rack_top", "rack_side", f"rack_t{k_we}_front",
         f"rack_t{k_we}_left", "dotm_top", "dotm", "intile_top", "intile_front", "in_col_pin"]
pins += ["hist_lo", "hist_hi", "hist_zero", f"hist_b{nb - 1}_top", f"hist_b{hot}_top"]
pins += [f"m{j}_top" for j in range(7)] + [f"m{j}" for j in range(7)] + ["dial_top", "dial_t0", "dial_t07", "dial_t10", "dial_t12"]
pins += [f"wheel_s{k}" for k in winfo] + ["wheel_pin_ptr", "pick_top", "pick_front"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
