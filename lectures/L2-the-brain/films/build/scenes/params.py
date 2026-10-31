"""Film "params": "494 million numbers" (Lecture 2, section 8 opener). Builds films/params.blend.

The 24-floor block stack (the series' block_tower); the top block lifts out and lands on a stage, and its weight matrices
rise out of it as glass sheets at their real shapes (1 m = 3,584 numbers), each face showing the REAL weights of block
24, one cell per weight (capture_params.py -> /vol/l2films/data/params/*.png); the two norms as thin rods; x24 on the
stack; the embedding table as a 42 m glass runway (row-binned real values); then a macro zoom into the query sheet's
top-left corner until single cells fill the frame (their values are 2D labels from build/data/params_data.json).
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

FILM = "params"
B = K.Beats(FILM)
w = B.w
END = B.frames - 1
blk = B.blocks
TEX = os.environ.get("PARAMS_TEX", "/vol/l2films/data/params")
S = 0.25 / 896          # metres per number
SC = 0.25               # 896 numbers

sc = K.reset(B.frames)
K.studio(sc, focus=(1.6, 0.0, 0.8), key_power=3400, span=6.0)

# ------------------------------------------------------------------------------------------------ the stack
TX, TY = -0.9, 0.45
K.rbox("pedestal", (2.2, 1.15, 0.06), bevel=0.012, seg=4, mat=K.M("plinth"), loc=(TX, TY, 0.03))
TW = P4.block_tower("bt", (TX, TY, 0.06), floors=24, pitch=0.16, w=1.6, d=0.62)
ZF = TW["z"]
f24 = w("b1", "twenty-four")
f_num = w("b1", "numbers")
for k in range(24):
    K.glow_keys(TW["att"][k], [(0, 0.5), (f24 + k * 2, 0.5), (f24 + k * 2 + 5, 3.4), (f24 + k * 2 + 18, 0.8),
                               (f_num, 0.8), (f_num + 10, 2.2)])
    K.glow_keys(TW["mlp"][k], [(0, 0.4), (f24 + k * 2 + 2, 0.4), (f24 + k * 2 + 7, 3.0), (f24 + k * 2 + 20, 0.7),
                               (f_num, 0.7), (f_num + 10, 2.0)])
# x24 (b5): every floor flashes bottom to top
f_x24 = w("b5", "twenty-four")
for k in range(24):
    t = f_x24 + k * 2
    K.glow_keys(TW["att"][k], [(t - 1, 2.0), (t + 3, 5.0), (t + 24, 2.2)])
    K.glow_keys(TW["mlp"][k], [(t, 2.0), (t + 4, 4.6), (t + 26, 2.0)])

# the top block lifts out and lands on the stage in front of the gallery
STAGE = Vector((1.05, -0.35, 0.0))
fl = TW["floors"][23]
z24 = ZF[23]
f_lift = w("b2", "lift") - 4
loc_land = STAGE - Vector((TX, TY, 0.06))
K.key(fl, "location", [(0, (0, 0, z24)), (f_lift, (0, 0, z24)), (f_lift + 18, (0, -0.15, z24 + 0.42)),
                       (f_lift + 54, (loc_land.x * 0.8, loc_land.y, 0.9)), (f_lift + 78, (loc_land.x, loc_land.y, -0.02))])
K.rbox("stage", (1.9, 0.9, 0.04), bevel=0.01, seg=4, mat=K.M("plinth"), loc=(STAGE.x, STAGE.y, 0.02))

# ------------------------------------------------------------------------------------------------ the gallery: block 24's weights
GY = 0.35
K.plinth("rail", 1.95, 6.6, y=GY, depth=0.42, height=0.07)
Z0 = 0.07 + 0.012
D = blk  # noqa
specs = [  # name, image, cols, rows, x centre
    ("q", 896, 896, 2.30), ("k", 896, 128, 2.67), ("v", 896, 128, 3.04), ("o", 896, 896, 3.41),
    ("gate", 896, 4864, 3.96), ("up", 896, 4864, 4.33), ("down", 4864, 896, 5.25)]
SH = {}
f_out = w("b2", "lay")
land = f_lift + 78
for i, (nm, cols, rows, x) in enumerate(specs):
    img = PP.load_image(f"img_{nm}", os.path.join(TEX, f"{nm}.png"))
    root, m = PP.weight_sheet(f"sh_{nm}", img, cols, rows, cols * S, rows * S, (x, GY, Z0), glow=0.0)
    SH[nm] = (root, m)
    f0 = max(land - 6, f_out) + i * 5
    src = Vector((STAGE.x, STAGE.y, 0.12))
    K.key(root, "location", [(0, src), (f0, src), (f0 + 26, (x, GY, Z0 + 0.12)), (f0 + 34, (x, GY, Z0))])
    K.key(root, "scale", [(0, (0.04,) * 3), (f0, (0.04,) * 3), (f0 + 26, (1.0,) * 3)])
    K.show(root, [(0, False), (f0, True)])
    K.glow_keys(m, [(0, 0.0), (f0, 0.6), (f0 + 26, 2.4)])
# the two norms: 896 numbers each, thin rods
NR = []
for j in range(2):
    nm = f"norm{j + 1}"
    root = K.empty(nm, (5.93 + 0.25, GY, Z0 + 0.05 + j * 0.07))
    rm = K.light_mat(nm + "_m", K.lin("#ffe2a8"), 0.0)
    rod = K.cyl(nm + "_rod", 0.0035, SC, rm, loc=(0, 0, 0), verts=16, parent=root)
    rod.rotation_euler = (0, math.pi / 2, 0)
    for sx in (-1, 1):
        K.cyl(f"{nm}_cap{sx}", 0.006, 0.01, K.M("alu"), loc=(sx * SC / 2, 0, 0), verts=20, parent=root).rotation_euler = (0, math.pi / 2, 0)
    K.empty(nm + "_top", (0, -0.01, 0.01), parent=root)
    f0 = max(land - 6, f_out) + (7 + j) * 5
    K.show(root, [(0, False), (f0 + 10, True)])
    K.glow_keys(rm, [(0, 0.0), (f0 + 10, 0.0), (f0 + 30, 2.0)])
    NR.append(rm)
# word-synced flares: q and o, then k and v, then gate, up, down, then the norms
f_q, f_k = w("b3", "query"), w("b3", "keys")
f_g, f_u, f_d = w("b4", "gate"), w("b4", "up"), w("b4", "down")
f_one = w("b4", "one")


def flare(m, f, peak=5.0, rest=2.4, hold=40):
    K.glow_keys(m, [(f - 2, rest), (f + 6, peak), (f + hold, peak * 0.9), (f + hold + 24, rest)])


flare(SH["q"][1], f_q)
flare(SH["o"][1], w("b3", "output"))
flare(SH["k"][1], f_k, peak=6.0)
flare(SH["v"][1], f_k + 4, peak=6.0)
flare(SH["gate"][1], f_g, hold=60)
flare(SH["up"][1], f_u, hold=56)
flare(SH["down"][1], f_d, hold=52)
for rm in NR:
    K.glow_keys(rm, [(f_one - 6, 2.0), (f_one + 4, 6.0), (f_one + 40, 2.0)])

# ------------------------------------------------------------------------------------------------ the embedding table: a 42 m runway
EL = 151936 * S
emb_img = PP.load_image("img_embed", os.path.join(TEX, "embed.png"))
em = PP.grid_mat("embed_cells", emb_img, 896, 2374, strength=0.0, gw=0.05, reveal=0.0, dim=0.02)
RX0 = -2.15
ER = K.empty("embed", (RX0 - EL / 2, -0.25, 0.0))
K.plane("embed_face", SC, EL, em, loc=(0, 0, 0.0125), rot=(-math.pi / 2, 0, -math.pi / 2), parent=ER)
K.rbox("embed_body", (EL + 0.01, SC + 0.01, 0.012), bevel=0.003, seg=2, mat=K.M("graphite"), loc=(0, 0, 0.006), parent=ER)
K.rbox("embed_rim", (EL + 0.02, 0.006, 0.016), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -SC / 2 - 0.006, 0.008), parent=ER)
K.rbox("embed_rim2", (EL + 0.02, 0.006, 0.016), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, SC / 2 + 0.006, 0.008), parent=ER)
K.empty("embed_near", (EL / 2, -SC / 2, 0.02), parent=ER)
K.empty("embed_10m", (EL / 2 - 10.0, -SC / 2, 0.02), parent=ER)
f_emb = w("b5", "embedding")
K.show(ER, [(0, False), (f_emb - 12, True)])
K.keyval(em.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_emb - 4, 0.0), (f_emb + 110, 1.0)])
K.glow_keys(em, [(0, 0.0), (f_emb - 6, 0.0), (f_emb + 4, 3.0)])
# the final norm: a thin rod on top of the stack
fn_root = K.empty("fnorm", (TX, TY - 0.2, ZF[22] + 0.06 + 0.22))
fn_m = K.light_mat("fnorm_m", K.lin("#ffe2a8"), 0.0)
K.cyl("fnorm_rod", 0.0035, SC, fn_m, loc=(0, 0, 0), verts=16, parent=fn_root).rotation_euler = (0, math.pi / 2, 0)
K.empty("fnorm_top", (0, 0, 0.01), parent=fn_root)
f_all = w("b5", "all")
K.glow_keys(fn_m, [(0, 0.0), (f_all - 4, 0.0), (f_all + 6, 5.0), (END, 3.0)])

# ------------------------------------------------------------------------------------------------ the macro: q's top-left corner
qroot = SH["q"][0]
qw, qh = 896 * S, 896 * S
for r in range(6):
    for c in range(6):
        K.empty(f"qc_{r}_{c}", (-qw / 2 + (c + 0.5) * S, -0.0035, qh - (r + 0.5) * S), parent=qroot)
CORNER = Vector((2.30 - qw / 2 + 3 * S, GY - 0.0035, Z0 + qh - 3 * S))

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_stack", lens=30, fstop=5.6).cut(0)
c1.keys([(0, (2.2, -6.2, 0.9), (TX, TY, 2.05)), (blk["b1"]["f1"] + 8, (1.3, -5.6, 1.6), (TX, TY, 2.1))])
c2 = K.Cam(sc, "c_lift", lens=28, fstop=5.6).cut(blk["b2"]["f0"] - 8)
c2.keys([(blk["b2"]["f0"] - 8, (2.6, -7.2, 2.4), (1.2, 0.2, 2.0)), (land, (2.9, -6.0, 1.8), (2.0, 0.2, 0.9)),
         (blk["b2"]["f1"] + 14, (3.3, -3.6, 1.1), (3.5, 0.2, 0.5))])
c3 = K.Cam(sc, "c_att", lens=40, fstop=4.0).cut(blk["b3"]["f0"] - 6)
c3.keys([(blk["b3"]["f0"] - 6, (2.55, -1.6, 0.58), (2.85, GY, 0.27)), (blk["b3"]["f1"] + 14, (3.05, -1.45, 0.5), (2.88, GY, 0.26))])
c4 = K.Cam(sc, "c_mlp", lens=34, fstop=4.0).cut(blk["b4"]["f0"] - 6)
c4.keys([(blk["b4"]["f0"] - 6, (4.0, -2.7, 0.95), (4.6, GY, 0.66)), (f_one - 10, (4.5, -2.6, 0.9), (4.8, GY, 0.62)),
         (f_one + 30, (3.9, -4.4, 1.35), (4.1, GY, 0.5)), (blk["b4"]["f1"] + 14, (3.8, -4.6, 1.4), (4.1, GY, 0.5))])
c5 = K.Cam(sc, "c_x24", lens=28, fstop=5.6).cut(blk["b5"]["f0"] - 6)
c5.keys([(blk["b5"]["f0"] - 6, (2.6, -7.6, 2.3), (1.4, 0.2, 1.7)), (f_emb - 12, (2.2, -7.2, 2.2), (1.2, 0.2, 1.7))])
c6 = K.Cam(sc, "c_embed", lens=32, fstop=4.0).cut(f_emb - 10)
c6.keys([(f_emb - 10, (-1.7, -2.3, 1.45), (-8.0, -0.25, 0.0)), (f_all - 14, (-2.9, -2.1, 1.25), (-11.0, -0.25, 0.0))])
c7 = K.Cam(sc, "c_all", lens=24, fstop=8.0).cut(f_all - 12)
c7.keys([(f_all - 12, (5.0, -8.0, 3.6), (-2.0, 0.0, 0.8)), (blk["b5"]["f1"] + 20, (4.6, -8.4, 3.9), (-2.4, 0.0, 0.8))])
# macro: straight in on the corner, exponentially from 0.95 m to 3.2 mm, then back out at the question
cz = K.Cam(sc, "c_zoom", lens=40, fstop=16.0).cut(blk["b6"]["f0"] - 8)
cz.obj.data.clip_start = 0.0002
cz.obj.data.dof.use_dof = False
fz0, fz1 = blk["b6"]["f0"] - 8, w("b6", "corner")
fb0, fb1 = blk["b7"]["f0"] - 4, blk["b7"]["f0"] + 120
keys = []


def ez(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


off = Vector((0.0, 0, 0.0))
DN, LN = 0.0105, 95.0   # closest: 1.05 cm away on a 95 mm lens (about 14 x 8 cells in view)
lens_keys = []
for f in range(fz0, fz1 + 1, 2):
    u = ez((f - fz0) / (fz1 - fz0))
    d = 0.95 * (DN / 0.95) ** u
    keys.append((f, CORNER + Vector((0.12 * d, -d, 0.05 * d)), CORNER))
    lens_keys.append((f, 40.0 * (LN / 40.0) ** u))
keys.append((fb0, CORNER + Vector((0.12 * DN * 0.94, -DN * 0.94, 0.05 * DN * 0.94)), CORNER))
lens_keys.append((fb0, LN))
cz.lens(lens_keys)
cz.keys(keys)
c8 = K.Cam(sc, "c_end", lens=26, fstop=6.3).cut(fb0)
c8.keys([(fb0, (5.6, -6.2, 0.75), (1.6, 0.3, 1.05)), (END, (4.6, -7.4, 1.25), (1.2, 0.3, 1.2))])

pins = ([f"sh_{n}_top" for n, *_ in specs] + [f"sh_{n}_bot" for n, *_ in specs] + [f"sh_{n}_mid" for n, *_ in specs] + ["norm1_top", "norm2_top", "fnorm_top",
        "embed_near", "embed_10m", "bt_att24", "bt_mlp24", "bt_att12"] + [f"qc_{r}_{c}" for r in range(6) for c in range(6)])
# a far floor beyond the studio sweep, so shots along the set never see the sweep's corner against the sky
_ff = K.principled("farfloor", (0.006, 0.008, 0.014, 1), rough=0.5)
_fp = K.plane("farfloor", 900, 900, _ff, loc=(0, -150, -0.004), rot=(-math.pi / 2, 0, 0))
_fw = K.plane("farwall", 700, 220, _ff, loc=(-135, 0, 100), rot=(0, 0, -math.pi / 2))   # closes the far end of the sweep
for _o in bpy.data.objects:   # the big soft lights must not show up as grey disks in wide shots
    if _o.type == "LIGHT":
        _o.visible_camera = False
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
