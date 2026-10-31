"""Film s8 (v5), "How the weights were learnt: training". Builds films/s8_weights.blend.

One journey along a long plinth, all on the tiny GPT and its real run (build/data/s8_weights_data.json):
  corpus   three trays of document cards (generated notes, e-mails, policy lines; card counts in proportion to their
           characters) and the corpus itself as a 31 m strip of cells, one per real character (colour = kind of text,
           brightness = letter / digit / space), lit when the three are shuffled together
  window   a bracket cuts the real first-batch window (128 characters); the input bar and the target bar (shifted by one)
           rise from it; the real batch of 32 windows stands up behind
  step     the batch enters the tiny GPT (4 floors); 81 glass meters show its real probabilities for the next character
           at one position ("4,600 on " -> h; h in green); a loss gauge; a real 8x16 patch of one weight matrix shows its
           values, then its real gradient, then its values after 1,500 steps
  repeat   the real loss curve as a glowing ribbon; the meters refill with the trained model's probabilities
  result   ten slips for the ten sampled stock lines, a green plaque for the real 5,400
  qwen     the 24-floor stack, three stage sockets, two calendar blocks
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_params_s8 as PP  # noqa: E402
import props_s456 as P4  # noqa: E402
import props_s789 as P7  # noqa: E402

FILM = os.environ.get("S8_FILM", "s8_weights")
B = K.Beats(FILM)
D = K.load("films/build/data/s8_weights_data.json")
w = B.w
END = B.frames - 1
blk = B.blocks
PZ = 0.11

sc = K.reset(B.frames)
K.studio(sc, focus=(3.0, 0.0, 0.5), key_power=3200, span=6.0)
for i, x in enumerate((8.5, 11.8)):   # the far end of the set (results, Qwen) gets its own key and rim
    K.soft_light(f"keyE{i}", (x - 4.0, -6.5, 8.0), (x, 0.3, 0.6), 2200, 12.0, (1.0, 0.97, 0.93))
    K.soft_light(f"rimE{i}", (x + 1.0, 7.0, 3.5), (x, 0.3, 0.6), 1500, 14.0, (0.7, 0.82, 1.0))
K.plinth("plinth", -31.5, 13.3, depth=0.95, height=PZ)

KCOL = {"0": (0.235, 0.565, 1.0), "1": (1.0, 0.80, 0.52), "2": (0.70, 0.62, 1.0), "3": (0.0, 0.0, 0.0)}


def char_rgb(ch, k):
    c = KCOL[k]
    if ch in " \n" or k == "3":
        b = 0.07
    elif ch.isdigit():
        b = 1.0
    elif ch.isupper():
        b = 0.78
    elif ch.isalpha():
        b = 0.52
    else:
        b = 0.34
    return [c[0] * b, c[1] * b, c[2] * b]


# ------------------------------------------------------------------------------------------------ corpus: three trays + the strip
f_three, f_notes, f_mail, f_pol, f_shuf = w("b2", "three"), w("b2", "notes"), w("b2", "e-mails"), w("b2", "every"), w("b2", "shuffled")
kinds = D["corpus"]["kinds"]
per = kinds[0]["chars"] / 48
TR = {}
for i, (nm, x, k, f_on) in enumerate((("tr_gen", -1.65, "0", f_notes), ("tr_mail", -1.0, "1", f_mail), ("tr_pol", -0.35, "2", f_pol))):
    n = max(3, round(kinds[i]["chars"] / per))
    root, em, h = PP.card_stack(nm, (x, 0.2, PZ), n, KCOL[k] + (1.0,))
    TR[nm] = (root, em, n)
    K.glow_keys(em, [(0, 0.6), (w("b1", "documents") - 4, 0.6), (w("b1", "documents") + 8, 3.0), (f_on - 4, 3.0),
                     (f_on + 6, 9.0), (f_on + 50, 4.0), (f_shuf, 4.0), (f_shuf + 30, 1.0)])

STRIP = D["strip"]
SN = len(STRIP["text"])
CW = 0.006
XW = -0.2                                  # where the picked window starts
i_w = STRIP["window_at"] - STRIP["start"]  # its index on the strip
x_of = lambda i: XW + (i - i_w) * CW  # noqa: E731
srgb = [char_rgb(ch, k) for ch, k in zip(STRIP["text"], STRIP["kinds"])]
s_img = PP.rgb_image("strip_img", srgb, SN, 1)
s_m = PP.grid_mat("strip_cells", s_img, SN, 1, strength=0.0, gw=0.16, reveal=0.0, dim=0.0, base_mix=0.04)
SX = x_of(0) + SN * CW / 2
SY = -0.3
srt = K.empty("strip", (SX, SY, PZ))
K.plane("strip_face", SN * CW, 0.034, s_m, loc=(0, 0, 0.0076), rot=(-math.pi / 2, 0, 0), parent=srt)
K.rbox("strip_body", (SN * CW + 0.01, 0.044, 0.007), bevel=0.0015, seg=2, mat=K.M("graphite"), loc=(0, 0, 0.0035), parent=srt)
K.rbox("strip_rim", (SN * CW + 0.012, 0.004, 0.009), bevel=0.0012, seg=2, mat=K.M("alu"), loc=(0, -0.024, 0.0045), parent=srt)
K.empty("strip_near", (SN * CW / 2 - 0.05, -0.022, 0.012), parent=srt)
K.keyval(s_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_shuf - 6, 0.0), (f_shuf + 40, 1.0)])
K.glow_keys(s_m, [(0, 0.0), (f_shuf - 8, 0.0), (f_shuf + 4, 3.2)])

# ------------------------------------------------------------------------------------------------ window, target, batch
f_cut, f_tgt, f_shift, f_test, f_batch, f_32 = (w("b3", "cut"), w("b3", "target"), w("b3", "shifted"), w("b3", "test"),
                                                w("b3", "batch"), w("b3", "thirty-two"))
WL = 128 * CW
br = K.empty("bracket", (XW + WL / 2 + 1.2, SY, PZ + 0.009))
bm = K.light_mat("bracket_glow", K.SKY, 0.0)
for nm, sz, lc in (("_l", (0.006, 0.06, 0.012), (-WL / 2 - 0.004, 0, 0)), ("_r", (0.006, 0.06, 0.012), (WL / 2 + 0.004, 0, 0)),
                   ("_f", (WL + 0.014, 0.006, 0.012), (0, -0.028, 0)), ("_b", (WL + 0.014, 0.006, 0.012), (0, 0.028, 0))):
    K.rbox("bracket" + nm, sz, bevel=0.0015, seg=2, mat=K.M("alu"), loc=lc, parent=br)
K.rbox("bracket_led", (WL + 0.004, 0.003, 0.004), bevel=0.001, seg=1, mat=bm, loc=(0, -0.031, 0.002), parent=br)
K.empty("bracket_top", (0, -0.03, 0.02), parent=br)
K.show(br, [(0, False), (f_cut - 16, True)])
K.key(br, "location", [(0, br.location.copy()), (f_cut - 16, br.location.copy()), (f_cut + 22, (XW + WL / 2, SY, PZ + 0.009))])
K.glow_keys(bm, [(0, 0.0), (f_cut + 14, 0.0), (f_cut + 26, 5.0), (f_32 + 30, 2.0)])

BAT = D["batch"]
pick = BAT["pick"]
win, wkind = BAT["windows"][pick], BAT["kinds"][pick]
text_after = STRIP["text"][i_w + 1:i_w + 129]
kind_after = STRIP["kinds"][i_w + 1:i_w + 129]
BC = (0.012, 0.03)
XB = XW + WL / 2
inp, inp_m = PP.cell_bar("inbar", [char_rgb(c, k) for c, k in zip(win, wkind)], 128, 1, BC, (XB, SY, PZ + 0.26), glow=0.0)
tgt, tgt_m = PP.cell_bar("tgbar", [char_rgb(c, k) for c, k in zip(text_after, kind_after)], 128, 1, BC, (XB + BC[0], SY, PZ + 0.17), glow=0.0)
for root, m, f0, z in ((inp, inp_m, f_cut + 26, 0.26), (tgt, tgt_m, f_tgt, 0.17)):
    K.show(root, [(0, False), (f0 - 2, True)])
    K.key(root, "location", [(0, (root.location.x - (BC[0] if root is tgt else 0), SY, PZ + 0.01)),
                             (f0, (root.location.x - (BC[0] if root is tgt else 0), SY, PZ + 0.01)), (f0 + 26, (root.location.x, SY, PZ + z))])
    K.key(root, "scale", [(0, (0.5, 1, 0.3)), (f0, (0.5, 1, 0.3)), (f0 + 26, (1, 1, 1))])
    K.glow_keys(m, [(0, 0.0), (f0, 0.0), (f0 + 18, 3.0)])
for i in (0, 37, 38, 127):
    K.empty(f"in_c{i}", (-64 * BC[0] + (i + 0.5) * BC[0], -0.008, BC[1] + 0.006), parent=inp)
    K.empty(f"tg_c{i}", (-64 * BC[0] + (i + 0.5) * BC[0], -0.008, -0.004), parent=tgt)
# the batch: 32 real windows (128 x 32 cells), standing behind
brgb = []
for wt, kd in zip(BAT["windows"], BAT["kinds"]):
    brgb += [char_rgb(c, k) for c, k in zip(wt, kd)]
bat, bat_m = PP.cell_bar("batch", brgb, 128, 32, 0.012, (0.62, 0.62, PZ + 0.03), glow=0.0, reveal=0.0)
K.show(bat, [(0, False), (f_batch - 10, True)])
K.keyval(bat_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_32 - 6, 0.0), (f_32 + 34, 1.0)])
K.glow_keys(bat_m, [(0, 0.0), (f_batch - 10, 0.0), (f_batch + 4, 2.8)])
K.key(bat, "location", [(0, (0.62, 0.62, PZ - 0.5)), (f_batch - 10, (0.62, 0.62, PZ - 0.42)), (f_batch + 12, (0.62, 0.62, PZ + 0.03))])

# ------------------------------------------------------------------------------------------------ the tiny GPT
TG = Vector((2.95, 0.3, PZ))
K.rbox("tg_ped", (1.25, 0.72, 0.03), bevel=0.008, seg=3, mat=K.M("alu_dark"), loc=(TG.x, TG.y, PZ + 0.015))
T4 = P4.block_tower("tg", (TG.x, TG.y, PZ + 0.03), floors=4, pitch=0.15, w=1.0, d=0.48, heads=4, fins=18)
f_step = w("b4", "one")
# the batch flies into the bottom of the tiny GPT
K.key(bat, "location", [(f_step - 6, (0.62, 0.62, PZ + 0.03)), (f_step + 26, (TG.x, TG.y - 0.05, PZ + 0.08))])
K.key(bat, "scale", [(0, (1, 1, 1)), (f_step - 6, (1, 1, 1)), (f_step + 26, (0.25, 1, 0.25))])
K.show(bat, [(f_step + 27, False)])
for root in (inp, tgt):
    K.show(root, [(f_step + 6, False)])


def climb(f0, peak=4.5, per=3, base=0.6):
    for k in range(4):
        t = f0 + k * per
        K.glow_keys(T4["att"][k], [(t - 1, base), (t + 3, peak), (t + 12, base)])
        K.glow_keys(T4["mlp"][k], [(t, base * 0.8), (t + 4, peak * 0.9), (t + 13, base * 0.8)])


for k in range(4):
    K.glow_keys(T4["att"][k], [(0, 0.6)])
    K.glow_keys(T4["mlp"][k], [(0, 0.5)])
climb(f_step + 24)

# 81 probability meters (one per character), h in green
CH = D["chars"]
PB, PA = D["full_before"], D["full_after"]
H_I = CH.index("h")
MX0, MP = 2.2, 0.0178
f_prob, f_h = w("b4", "probability"), w("b4", "h")
f_now = w("b7", "now")
MET = {}
for i, ch in enumerate(CH):
    col = K.GREEN if i == H_I else K.SKY
    root, liq, lm = K.meter(f"m{i}", (MX0 + i * MP, -0.24, PZ), height=0.34, r=0.0062, color=col)
    lb = min(1.0, PB[i] / 0.05)
    la = PA[i]
    f0 = f_prob + int(i * 0.35)
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (f0, (1, 1, 0.001)), (f0 + 22, (1, 1, max(0.001, lb))),
                         (f_now - 8, (1, 1, max(0.001, lb))), (f_now - 2, (1, 1, 0.001)), (f_now + 22, (1, 1, max(0.001, la)))])
    K.glow_keys(lm, [(0, 0.0), (f0, 0.0), (f0 + 10, 3.5 if i == H_I else 2.4)])
    MET[i] = (root, lm)
K.glow_keys(MET[H_I][1], [(f_h - 2, 3.5), (f_h + 6, 9.0), (f_h + 50, 5.0)])
K.empty("m_axis", (MX0 - 0.03, -0.24, PZ + 0.36))
# the loss gauge: a taller glass meter, level = loss / 5, a ring at the even-guessing loss (4.39)
g_root, g_liq, g_m = K.meter("gauge", (3.95, -0.22, PZ), height=0.5, r=0.016, color=K.lin("#ffe2a8"))
f_here, f_even = w("b5", "here"), w("b5", "evenly")
f_fall0, f_fall1 = w("b7", "falls"), w("b7", "three")
L0 = D["row_before"]["loss"]
K.key(g_liq, "scale", [(0, (1, 1, 0.001)), (f_here - 6, (1, 1, 0.001)), (f_here + 18, (1, 1, L0 / 5)),
                       (f_fall0, (1, 1, L0 / 5)), (f_fall1 + 6, (1, 1, D["log"]["curve"][-1]["train"] / 5))])
K.glow_keys(g_m, [(0, 0.0), (f_here - 6, 0.0), (f_here + 6, 3.0)])
bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.0028, location=(3.95, -0.22, PZ + 0.0145 + 0.5 * 0.995 * D["log"]["uniform_loss"] / 5))
ring = bpy.context.active_object
ring.name = "even_ring"
rmat = K.light_mat("even_ring_m", K.SKY, 0.0)
ring.data.materials.append(rmat)
K.glow_keys(rmat, [(0, 0.0), (f_even - 4, 0.0), (f_even + 8, 4.0)])
K.empty("even_pin", (3.95 + 0.03, -0.22, PZ + 0.0145 + 0.5 * 0.995 * D["log"]["uniform_loss"] / 5))
K.empty("gauge_pin", (3.95 - 0.02, -0.24, PZ + 0.52))

# a real patch of one weight matrix: values, gradient, values after training (blocks[0].attn.qkv.weight[0:8, 0:16])
PT = D["patch"]
flat = lambda M: [v for r in M for v in r]  # noqa: E731
vmax = max(abs(v) for v in flat(PT["before"]) + flat(PT["final"]))
gmax = max(abs(v) for v in flat(PT["grad"])) or 1.0
WP = Vector((4.45, -0.02, PZ + 0.24))
pv, pv_m = K.vector_plate("pv", flat(PT["before"]), 16, 8, K.SKY, tuple(WP), cell=0.026, vmax=vmax, glow=0.0)
pg, pg_m = K.vector_plate("pg", [-g for g in flat(PT["grad"])], 16, 8, K.lin("#9a5cff"), tuple(WP + Vector((0, -0.003, 0))), cell=0.026, vmax=gmax, glow=0.0)
pf, pf_m = K.vector_plate("pf", flat(PT["final"]), 16, 8, K.SKY, tuple(WP + Vector((0, -0.006, 0))), cell=0.026, vmax=vmax, glow=0.0)
f_grad, f_small, f_lr = w("b6", "gradient"), w("b6", "small"), w("b6", "learning")
f_rep = w("b7", "repeat")
K.show(pv, [(0, False), (blk["b6"]["f0"] - 30, True)])
K.glow_keys(pv_m, [(0, 0.0), (blk["b6"]["f0"] - 30, 0.0), (blk["b6"]["f0"] - 10, 3.2)])
K.show(pg, [(0, False), (f_grad - 2, True), (f_small + 30, False)])
K.glow_keys(pg_m, [(0, 0.0), (f_grad - 2, 0.0), (f_grad + 12, 4.0), (f_small, 4.0), (f_small + 24, 0.0)])
K.glow_keys(pv_m, [(f_grad - 2, 3.2), (f_grad + 10, 0.4), (f_small, 0.4), (f_small + 20, 3.2)])
K.show(pf, [(0, False), (f_rep + 20, True)])
K.glow_keys(pf_m, [(0, 0.0), (f_rep + 20, 0.0), (f_fall1, 3.4)])
K.glow_keys(pv_m, [(f_rep + 20, 3.2), (f_fall1, 0.0)])
K.empty("patch_pin", (WP.x + 0.21, WP.y - 0.02, WP.z + 0.12))
# "830,464 weights": every floor of the tiny GPT flares
f_830 = w("b6", "eight")
climb(f_830, peak=6.0, per=4)

# ------------------------------------------------------------------------------------------------ repeat: 1,500 steps and the loss curve
CHP = Vector((2.95, 1.05, 0.0))
K.rbox("chart_panel", (1.7, 0.04, 1.0), bevel=0.012, seg=4, mat=K.M("graphite"), loc=(CHP.x, CHP.y, 1.15))
K.rbox("chart_bezel", (1.74, 0.03, 1.04), bevel=0.012, seg=4, mat=K.M("alu"), loc=(CHP.x, CHP.y + 0.02, 1.15))
K.cyl("chart_stem", 0.025, 0.66, K.M("alu"), loc=(CHP.x, CHP.y + 0.05, 0.33), verts=24)
K.rbox("chart_foot", (0.6, 0.3, 0.06), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(CHP.x, CHP.y + 0.05, 0.03))
X0, X1, Z0, Z1 = CHP.x - 0.72, CHP.x + 0.72, 0.76, 1.55
grid_m = K.glow_mat("grid_m", K.SKY, 0.15)
for g in range(5):
    K.rbox(f"grid{g}", (1.46, 0.004, 0.003), bevel=0.0, seg=1, mat=grid_m, loc=(CHP.x, CHP.y - 0.024, Z0 + (Z1 - Z0) * g / 4))
CURVE = D["log"]["curve"]
pts = [(X0 + (X1 - X0) * c["step"] / 1500, CHP.y - 0.03, Z0 + (Z1 - Z0) * c["train"] / 4.6) for c in CURVE]
rib_m = K.light_mat("rib_m", K.SKY, 0.0)
rib = P7.ribbon("loss", pts, r=0.008, mat=rib_m)
K.grow(rib, [(0, 0.0), (f_fall0 - 4, 0.0), (f_fall1 + 10, 1.0)])
K.glow_keys(rib_m, [(0, 0.0), (f_fall0 - 6, 4.0)])
uz = Z0 + (Z1 - Z0) * D["log"]["uniform_loss"] / 4.6
um = K.glow_mat("uni_m", K.lin("#ffe2a8"), 0.0)
K.rbox("uni_line", (1.46, 0.004, 0.004), bevel=0.0, seg=1, mat=um, loc=(CHP.x, CHP.y - 0.026, uz))
K.glow_keys(um, [(0, 0.0), (f_fall0 - 4, 0.0), (f_fall0 + 8, 2.0)])
K.empty("loss_start", pts[0])
K.empty("loss_end", pts[-1])
K.empty("loss_100", pts[1])
K.empty("uni_pin", (X1 - 0.05, CHP.y - 0.03, uz))
for k in range(10):   # many passes climb the tiny GPT while the curve falls
    climb(f_rep + 10 + k * 24, peak=4.0, per=3)

# ------------------------------------------------------------------------------------------------ result: ten slips, the plaque
f_ten, f_inv, f_real, f_pat = w("b8", "ten"), w("b8", "invented"), w("b8", "real"), w("b8", "pattern")
SL = []
for i in range(10):
    r, c = divmod(i, 5)
    loc = Vector((5.3 + c * 0.44, -0.2 + r * 0.3, PZ))
    root, m = PP.slip(f"slip{i}", loc, K.EMBER)
    f0 = f_ten + i * 5
    K.show(root, [(0, False), (f0 - 1, True)])
    K.key(root, "location", [(0, loc + Vector((0, 0, 0.35))), (f0, loc + Vector((0, 0, 0.35))), (f0 + 14, loc)])
    K.glow_keys(m, [(0, 0.0), (f0, 0.0), (f0 + 14, 1.4), (f0 + 40, 0.35), (f_inv - 2, 0.35), (f_inv + 8, 1.6), (f_inv + 40, 0.5)])
    SL.append(root)
PLQ = Vector((8.35, 0.05, PZ))
plq, plq_m = P7.plaque("plaque", tuple(PLQ), w=0.7, h=0.24)
K.show(plq, [(0, False), (f_real - 12, True)])
K.key(plq, "location", [(0, PLQ + Vector((0, 0, 0.45))), (f_real - 12, PLQ + Vector((0, 0, 0.45))), (f_real + 8, PLQ)])
K.glow_keys(plq_m, [(0, 0.0), (f_real, 0.0), (f_real + 12, 4.0)])

# ------------------------------------------------------------------------------------------------ Qwen at scale
QX = 11.8
K.rbox("q_ped", (2.2, 1.15, 0.06), bevel=0.012, seg=4, mat=K.M("plinth"), loc=(QX, 0.95, 0.03))
QT = P4.block_tower("qt", (QX, 0.95, 0.06), floors=24, pitch=0.16, w=1.6, d=0.62)
f_game, f_frozen = w("b9", "game"), w("b9", "froze")
for k in range(24):
    K.glow_keys(QT["att"][k], [(0, 0.6)])
    K.glow_keys(QT["mlp"][k], [(0, 0.5)])
for rep in range(5):   # the same game, at scale
    for k in range(24):
        t = f_game - 10 + rep * 26 + k
        K.glow_keys(QT["att"][k], [(t - 1, 0.6), (t + 3, 4.0), (t + 12, 0.6)])
        K.glow_keys(QT["mlp"][k], [(t, 0.5), (t + 4, 3.6), (t + 13, 0.5)])
for k in range(24):   # frozen: steady and cool
    K.glow_keys(QT["att"][k], [(f_frozen - 2, 0.6), (f_frozen + 14, 1.6)])
    K.glow_keys(QT["mlp"][k], [(f_frozen - 2, 0.5), (f_frozen + 14, 0.25)])
stages = []
for s_, (dx, word) in enumerate(((-0.6, "trillion"), (0.0, "instruction"), (0.6, "preference"))):
    root, m = P7.socket(f"stage{s_}", (QX + dx, -0.12, PZ), r=0.14)
    f0 = w("b9", word)
    K.glow_keys(m, [(0, 0.0), (f0 - 4, 0.0), (f0 + 8, 4.0), (END, 2.5)])
    stages.append(f"stage{s_}_top")
for nm, x, word, col in (("cal_rel", 10.05, "nineteenth", K.SKY), ("cal_ask", 10.65, "emma", K.EMBER)):
    root = K.empty(nm, (x, -0.1, PZ))
    K.rbox(nm + "_body", (0.42, 0.26, 0.34), bevel=0.02, seg=5, mat=K.M("ceramic"), loc=(0, 0, 0.17), parent=root)
    m = K.glow_mat(nm + "_face", col, 0.0, base=(0.018, 0.022, 0.03, 1))
    K.rbox(nm + "_face", (0.36, 0.01, 0.24), bevel=0.006, seg=3, mat=m, loc=(0, -0.131, 0.15), parent=root)
    for sx in (-1, 1):
        K.cyl(f"{nm}_ring{sx}", 0.018, 0.05, K.M("alu"), loc=(sx * 0.1, -0.06, 0.35), verts=24, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    K.empty(nm + "_top", (0, -0.13, 0.36), parent=root)
    f0 = w("b9", word)
    K.show(root, [(0, False), (f0 - 14, True)])
    K.key(root, "location", [(0, (x, -0.1, PZ + 0.5)), (f0 - 14, (x, -0.1, PZ + 0.5)), (f0 + 4, (x, -0.1, PZ))])
    K.glow_keys(m, [(0, 0.0), (f0, 0.0), (f0 + 10, 0.5)])

# ------------------------------------------------------------------------------------------------ cameras
b = blk
c1 = K.Cam(sc, "c_corpus", lens=32, fstop=4.0).cut(0)
c1.keys([(0, (0.9, -2.2, 0.75), (-1.6, 0.0, 0.25)), (b["b1"]["f1"] + 10, (0.6, -1.9, 0.62), (-1.4, 0.0, 0.25))])
c2 = K.Cam(sc, "c_kinds", lens=40, fstop=3.5).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (-0.6, -1.65, 0.72), (-1.0, 0.15, 0.24)), (f_notes - 6, (-1.25, -1.35, 0.62), (-1.6, 0.15, 0.26)),
         (f_mail - 6, (-0.75, -1.3, 0.55), (-1.0, 0.15, 0.2)), (f_pol - 6, (-0.15, -1.3, 0.55), (-0.38, 0.15, 0.2)),
         (f_shuf - 4, (0.2, -1.4, 0.6), (-0.8, 0.0, 0.18)), (b["b2"]["f1"] + 14, (0.85, -1.15, 0.45), (-4.0, -0.3, 0.1))])
c3 = K.Cam(sc, "c_window", lens=36, fstop=4.0).cut(b["b3"]["f0"] - 8)
c3.keys([(b["b3"]["f0"] - 8, (0.6, -1.2, 0.42), (0.1, -0.3, 0.13)), (f_cut + 20, (0.45, -1.35, 0.5), (0.2, -0.3, 0.2)),
         (f_tgt + 20, (0.3, -1.55, 0.55), (0.2, -0.28, 0.27)), (f_batch - 10, (0.4, -1.75, 0.62), (0.35, -0.1, 0.3)),
         (b["b3"]["f1"] + 14, (0.55, -2.05, 0.75), (0.45, 0.1, 0.33))])
c4 = K.Cam(sc, "c_step", lens=34, fstop=4.0).cut(b["b4"]["f0"] - 8)
c4.keys([(b["b4"]["f0"] - 8, (1.6, -2.2, 0.9), (2.4, 0.2, 0.4)), (f_prob - 10, (2.75, -1.75, 0.72), (2.9, -0.1, 0.3)),
         (f_h - 16, (3.05, -1.35, 0.55), (3.25, -0.2, 0.28)), (b["b4"]["f1"] + 12, (3.15, -1.25, 0.5), (3.3, -0.2, 0.27))])
c5 = K.Cam(sc, "c_loss", lens=40, fstop=3.5).cut(b["b5"]["f0"] - 8)
c5.keys([(b["b5"]["f0"] - 8, (3.35, -1.3, 0.55), (3.6, -0.2, 0.33)), (b["b5"]["f1"] + 12, (3.6, -1.2, 0.5), (3.85, -0.2, 0.35))])
c6 = K.Cam(sc, "c_grad", lens=36, fstop=4.0).cut(b["b6"]["f0"] - 8)
c6.keys([(b["b6"]["f0"] - 8, (4.0, -1.45, 0.62), (4.25, 0.0, 0.36)), (f_830 - 10, (3.6, -1.9, 0.75), (3.6, 0.1, 0.4)),
         (f_small - 10, (4.15, -1.25, 0.55), (4.42, -0.02, 0.36)), (b["b6"]["f1"] + 12, (4.25, -1.2, 0.52), (4.45, -0.02, 0.36))])
c7 = K.Cam(sc, "c_repeat", lens=30, fstop=5.0).cut(b["b7"]["f0"] - 8)
c7.keys([(b["b7"]["f0"] - 8, (3.3, -2.6, 1.05), (3.1, 0.5, 0.75)), (f_fall1 + 10, (3.0, -2.75, 1.1), (3.0, 0.5, 0.8)),
         (f_now - 14, (3.05, -1.55, 0.62), (3.15, -0.15, 0.32)), (b["b7"]["f1"] + 12, (3.2, -1.5, 0.6), (3.2, -0.15, 0.32))])
c8 = K.Cam(sc, "c_result", lens=34, fstop=4.0).cut(b["b8"]["f0"] - 8)
c8.keys([(b["b8"]["f0"] - 8, (6.2, -2.1, 0.95), (6.2, 0.0, 0.15)), (f_real - 16, (6.6, -2.0, 0.9), (6.8, 0.0, 0.15)),
         (f_real + 12, (7.6, -1.85, 0.8), (7.7, 0.0, 0.18)), (b["b8"]["f1"] + 12, (7.4, -2.1, 0.85), (7.3, 0.0, 0.18))])
c9 = K.Cam(sc, "c_qwen", lens=28, fstop=5.6).cut(b["b9"]["f0"] - 8)
c9.keys([(b["b9"]["f0"] - 8, (13.2, -4.9, 1.45), (11.6, 0.6, 1.6)), (w("b9", "preference") + 30, (12.6, -6.2, 1.3), (11.3, 0.4, 1.3)),
         (w("b9", "nineteenth") - 20, (11.3, -2.6, 0.75), (10.6, 0.0, 0.35)), (END, (11.1, -2.4, 0.7), (10.5, 0.0, 0.33))])

pins = (["tr_gen_top", "tr_mail_top", "tr_pol_top", "tr_gen_front", "strip_near", "bracket_top", "inbar_l", "inbar_r", "tgbar_l",
         "tgbar_r", "batch_top", "batch_r", "m_axis", "gauge_pin", "even_pin", "patch_pin", "pv_top", "tg_att4", "tg_mlp4",
         "loss_start", "loss_end", "loss_100", "uni_pin", "plaque_top", "cal_rel_top", "cal_ask_top"] + stages +
        [f"in_c{i}" for i in (0, 37, 38, 127)] + [f"tg_c{i}" for i in (0, 37, 38, 127)] + [f"m{i}_top" for i in range(len(CH))] +
        [f"slip{i}_top" for i in range(10)])
# a far floor beyond the studio sweep, so shots along the set never see the sweep's corner against the sky
_ff = K.principled("farfloor", (0.006, 0.008, 0.014, 1), rough=0.5)
_fp = K.plane("farfloor", 900, 900, _ff, loc=(0, -150, -0.004), rot=(-math.pi / 2, 0, 0))
_fw = K.plane("farwall", 700, 220, _ff, loc=(-135, 0, 100), rot=(0, 0, -math.pi / 2))   # closes the far end of the sweep
for _o in bpy.data.objects:   # the big soft lights must not show up as grey disks in wide shots
    if _o.type == "LIGHT":
        _o.visible_camera = False
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
