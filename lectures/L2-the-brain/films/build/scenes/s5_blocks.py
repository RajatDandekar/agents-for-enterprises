"""Film s5: "A block, then 24 of them". Builds films/s5_blocks.blend.

One block on its own (attention bay with 14 heads + MLP bay), then 24 of them stacked. The last position's column
(896 cells = films/qkv_data.json vectors.lens_last[k-1], the final-normed residual after block k) rides up the front
of the stack; at each floor it lights that floor's heads, its MLP and its logit-lens eyepiece. The readout (the top
token after each block, trace.json logit_lens.last) is drawn as a 2D ladder by specs/s5_blocks.py.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s456 as P4  # noqa: E402

FILM = "s5_blocks"
B = K.Beats(FILM)
D = K.load("films/qkv_data.json")
LENS = D["vectors"]["lens_last"]
TW_W, TW_D, PITCH = 1.6, 0.62, 0.16

sc = K.reset(B.frames)
K.studio(sc, focus=(0.0, 0.0, 1.2), key_power=3400)
ped = K.rbox("pedestal", (2.3, 1.2, 0.06), bevel=0.012, seg=4, mat=K.M("plinth"), loc=(-0.2, 0.0, 0.03))
TW = P4.block_tower("bt", (0, 0, 0.06), floors=24, pitch=PITCH, w=TW_W, d=TW_D)
ZF = [z + 0.06 for z in TW["z"]]

# the column: 24 plates (one per block) on one carrier; only the current block's plate is shown
car = K.empty("col", (-TW_W / 2 - 0.32, -TW_D / 2 + 0.02, ZF[0] + 0.05))
cols = []
for k in range(24):
    pr, pm = K.vector_plate(f"col{k + 1}", LENS[k], 28, 32, K.SKY, (0, 0, 0), cell=0.0075, vmax=10.0, glow=4.2, parent=car)
    cols.append((pr, pm))
K.empty("col_pin", (0.0, 0.0, 0.14), parent=car)
rail_m = K.principled("rail", (0.9, 0.95, 1.0, 1), rough=0.08, transmission=1.0)
rail = K.cyl("rail", 0.008, TW["H"] + 0.1, rail_m, loc=(-TW_W / 2 - 0.32, -TW_D / 2 + 0.05, 0.06 + (TW["H"] + 0.1) / 2), verts=16)
beam_m = K.light_mat("lensbeam_m", K.SKY, 0.0)
lb = K.beam("lensbeam", (0.0, 0.0, 0.0), (0.18, 0.0, 0.0), r=0.004, mat=beam_m)
lb.parent = car
lb.location = (0.1, 0.0, 0.0)
# the answer tile at the top
wtile, wface = K.token_tile("we", "user", (0.0, -0.05, ZF[23] + 0.04))

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5")}
w = B.w
END = B.frames - 1
F = {1: w("b2", "climbs"), 2: w("b2", "changing"), 3: w("b2", "floor")}
f4, f17 = w("b4", "for"), w("b4", "languages")
for k in range(4, 18):
    F[k] = int(f4 + (f17 - f4) * (k - 4) / 13)
F[18] = w("b4", "eighteen")
F[19] = F[18] + 30
F[20] = F[18] + 62
F[21] = F[18] + 100
F[22] = w("b4", "twenty-two")
F[23] = w("b4", "twenty-nine")
F[24] = w("b4", "fifty-six")

# b1: one block alone; the column visits the attention bay, then the MLP bay, then the rail
x_rail = car.location.x
y_rail = car.location.y
y_front = -TW_D / 2 - 0.16
z1 = ZF[0] + 0.12
fa, fm_, fg, ft = w("b1", "half"), w("b1", "other"), w("b1", "gathers"), w("b1", "thinks")
pa = Vector((-0.32, y_front, z1))
pm = Vector((0.5, y_front, z1))
pr0 = Vector((x_rail, y_rail, ZF[0] + 0.05))
K.key(car, "location", [(0, pr0 + Vector((0, -0.1, 0.06))), (fa - 14, pr0 + Vector((0, -0.1, 0.06))), (fa + 14, pa), (fm_ - 4, pa),
                        (fm_ + 24, pm), (fg - 14, pm), (fg + 10, pa), (ft - 12, pa), (ft + 12, pm), (b["b1"]["f1"] + 4, pm),
                        (b["b2"]["f0"] + 30, pr0)])
att1, mlp1 = TW["att"][0], TW["mlp"][0]
K.glow_keys(att1, [(0, 0.0), (fa, 0.0), (fa + 14, 4.0), (fm_, 4.0), (fm_ + 14, 0.6), (fg, 0.6), (fg + 10, 4.5), (ft, 4.5), (ft + 10, 0.8)])
K.glow_keys(mlp1, [(0, 0.0), (fm_ + 10, 0.0), (fm_ + 24, 4.0), (fg, 4.0), (fg + 10, 0.6), (ft + 6, 0.6), (ft + 16, 4.5), (b["b2"]["f0"], 4.5),
                   (b["b2"]["f0"] + 30, 0.6)])

# b2: the other 23 floors drop into place
b2 = b["b2"]["f0"]
for k, fr in enumerate(TW["floors"], start=1):
    if k == 1:
        continue
    z = fr.location.z
    t0 = b2 + 4 + int((k - 2) * 2.6)
    K.show(fr, [(0, False), (t0, True)])
    K.key(fr, "location", [(0, (0, 0, z + 1.2)), (t0, (0, 0, z + 1.2)), (t0 + 20, (0, 0, z))])
for p in TW["posts"] + [rail]:
    K.show(p, [(0, False), (b2 + 4, True)])
K.key(TW["posts"][0], "scale", [(0, (1, 1, 1))])

# the climb: at floor k at F[k]; plates swap; that floor's heads, MLP and lens light
ks = sorted(F)
K.key(car, "location", [(F[k], (x_rail, y_rail, ZF[k - 1] + 0.05)) for k in ks])
for k in ks:
    pr, pm_ = cols[k - 1]
    on = F[k] - (0 if k > 1 else 400)
    off = F[k + 1] if k < 24 else END + 1
    if k == 1:
        K.show(pr, [(0, True), (off, False)])
    else:
        K.show(pr, [(0, False), (on, True), (off, False)])
    att, mlp, lens = TW["att"][k - 1], TW["mlp"][k - 1], TW["lens"][k - 1]
    if k > 1:
        K.glow_keys(att, [(0, 0.0), (F[k] - 8, 0.0), (F[k], 4.0), (F[k] + 14, 0.7), (END, 0.7)])
        K.glow_keys(mlp, [(0, 0.0), (F[k] - 4, 0.0), (F[k] + 4, 4.0), (F[k] + 18, 0.7), (END, 0.7)])
    lens_on = F[k] if k > 3 else w("b3", "ask") + (k - 1) * 8
    K.glow_keys(lens, [(0, 0.0), (lens_on - 4, 0.0), (lens_on + 2, 6.0), (lens_on + 20, 1.6), (END, 1.6)])
f_ask = w("b3", "ask")
K.glow_keys(beam_m, [(0, 0.0), (f_ask - 6, 0.0), (f_ask + 4, 3.5), (F[24] + 30, 3.5), (F[24] + 50, 0.0)])
K.show(lb, [(0, False), (f_ask - 8, True), (F[24] + 52, False)])

# b5: the answer condenses on top: a "We" tile rises out of the top floor
f_cond = w("b5", "condenses")
wz = wtile.location.z
K.key(wtile, "location", [(0, (0, -0.05, wz - 0.2)), (f_cond - 10, (0, -0.05, wz - 0.2)), (f_cond + 16, (0, -0.05, wz + 0.02))])
K.show(wtile, [(0, False), (f_cond - 12, True)])
K.glow_keys(wface, [(0, 0.0), (f_cond, 0.0), (f_cond + 16, 3.6)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_one", lens=38, fstop=3.2).cut(0)
c1.keys([(0, (0.45, -1.35, 0.52), (0.0, 0.0, 0.13)), (fm_, (0.25, -1.2, 0.46), (0.05, 0.0, 0.13)),
         (b["b1"]["f1"] + 10, (-0.15, -1.15, 0.44), (0.05, 0.0, 0.13))])
c2 = K.Cam(sc, "c_stack", lens=30, fstop=5.0).cut(b2 - 8)
c2.keys([(b2 - 8, (1.2, -3.0, 1.3), (0.0, 0.0, 0.9)), (F[3] + 10, (2.4, -5.2, 2.6), (-0.1, 0.0, 1.9))])
c3 = K.Cam(sc, "c_lens", lens=45, fstop=3.2).cut(b["b3"]["f0"] - 8)
z3 = ZF[2] + 0.05
c3.keys([(b["b3"]["f0"] - 8, (-1.9, -1.55, z3 + 0.45), (-0.95, -0.25, z3)), (b["b3"]["f1"] + 10, (-1.65, -1.25, z3 + 0.3), (-0.95, -0.25, z3))])
c4 = K.Cam(sc, "c_climb", lens=35, fstop=3.5).cut(b["b4"]["f0"] - 8)
kk = [(b["b4"]["f0"] - 8, 3), (F[4], 4), (F[17], 17), (F[18], 18), (F[22], 22), (F[23], 23), (F[24], 24)]
c4.keys([(f_, (-2.0, -1.9, ZF[k - 1] + 0.35), (-0.55, -0.15, ZF[k - 1])) for f_, k in kk] +
        [(b["b4"]["f1"] + 10, (-1.8, -1.7, ZF[23] + 0.4), (-0.5, -0.15, ZF[23] + 0.02))])
c5 = K.Cam(sc, "c_top", lens=35, fstop=4.0).cut(b["b5"]["f0"] - 8)
c5.keys([(b["b5"]["f0"] - 8, (-1.2, -2.0, ZF[23] + 0.6), (-0.2, 0.0, ZF[23])),
         (f_cond + 20, (0.6, -2.2, ZF[23] + 0.55), (0.0, 0.0, ZF[23] + 0.05)),
         (END, (2.6, -5.0, ZF[23] + 0.2), (0.0, 0.0, ZF[23] - 1.1))])

pins = ["col_pin", "we_top", "we_front"] + [f"bt_lens{k}" for k in range(1, 25)] + ["bt_att1", "bt_mlp1"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
