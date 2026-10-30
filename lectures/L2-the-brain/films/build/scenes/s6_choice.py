"""Film s6: "From a vector to a choice". Builds films/s6_choice.blend.

The last column after block 24 (films/qkv_data.json vectors.lens_last[23], 896 cells) leaves the top of the stack,
sweeps along the vocabulary rack (151,936 rows, drawn schematically), and six glass columns rise for the top six
tokens: first to their logits, then (softmax) to their probabilities; a machined temperature dial turns 0 -> 0.7 ->
1.2 and the columns follow the exact probabilities (kit/s6_sched.py). Then one token, "We", is drawn as a tile.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s456 as P4  # noqa: E402
import s6_sched  # noqa: E402

FILM = "s6_choice"
B = K.Beats(FILM)
D = K.load("films/qkv_data.json")
T = K.load("brain3d/trace.json")
S = s6_sched.Sched(B.tl, T["final"]["dial_last"])
COL = D["vectors"]["lens_last"][23]

sc = K.reset(B.frames)
K.studio(sc, focus=(0.0, 0.0, 0.5), key_power=3200, span=14.0)
K.plinth("plinth", -1.3, 1.9, depth=0.75, height=0.11)
TW = K.tower("tower", (-3.3, 0.25, 0.0), floors=24, pitch=0.072, w=1.5, d=0.56)
ZTOP = 23 * 0.072 + 0.09
rack, rack_m = P4.vocab_rack("rack", 2.2, -16.0, y=1.0, z0=0.0, h=1.1)
col, col_m = K.vector_plate("vec", COL, 28, 32, K.SKY, (-3.3, 0.1, ZTOP + 0.25), cell=0.012, vmax=10.0, glow=4.4, two_sided=False)
mx = [-0.95 + j * 0.34 for j in range(6)]
meters = []
for j in range(6):
    mr, liq, lm = K.meter(f"m{j}", (mx[j], -0.12, 0.11), height=0.62, r=0.04, color=K.SKY)
    meters.append((mr, liq, lm))
dl, knob = P4.dial("dial", (1.45, -0.15, 0.5), r=0.13)
K.rbox("dial_stand", (0.12, 0.12, 0.33), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(1.45, -0.09, 0.11 + 0.165))
wtile, wface = K.token_tile("we", "user", (mx[0], -0.12, 0.11))

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5")}
w = B.w
END = B.frames - 1
# b1: the column rises out of the top of the stack
f_col, f_tok = w("b1", "column"), w("b1", "token")
K.key(col, "location", [(0, (-3.3, 0.1, ZTOP - 0.15)), (f_col - 20, (-3.3, 0.1, ZTOP - 0.15)), (f_col + 20, (-3.3, 0.1, ZTOP + 0.3))])
K.glow_keys(col_m, [(0, 1.0), (f_col - 20, 1.0), (f_col + 10, 4.6)])
K.glow_keys(TW["idle"], [(0, 1.6), (b["b2"]["f0"], 1.6), (b["b2"]["f0"] + 30, 0.4)])
# b2: it flies to the rack and sweeps along it; every row lights as it passes
f_cmp, f_every, f_score = w("b2", "compared"), w("b2", "every"), w("b2", "score")
x0, x1 = 1.9, -15.5
K.key(col, "location", [(b["b2"]["f0"] - 4, (-3.3, 0.1, ZTOP + 0.3)), (f_cmp + 10, (x0, 0.55, 0.72)),
                        (f_every + 6, (x0 - 0.3, 0.55, 0.72)), (f_score - 6, (x1 + 2.0, 0.55, 0.72)),
                        (f_score + 40, (-0.08, 0.32, 1.32)), (END, (-0.08, 0.32, 1.32))])
import bpy  # noqa: E402
front_m = bpy.data.materials["rack_front"]
for m_ in (rack_m, front_m):   # sweep in the rack's object space (its origin is at x = 2.2)
    K.keyval(m_.node_tree.nodes["sweep"].outputs[0], [(0, 3.0 - 2.2), (f_every + 6, 1.9 - 2.2), (f_score - 6, x1 + 1.6 - 2.2),
                                                       (f_score + 30, x1 - 2.0 - 2.2)])
    K.glow_keys(m_, [(0, 0.0), (f_every, 0.0), (f_every + 8, 6.0), (f_score + 30, 6.0), (f_score + 60, 1.0), (b["b3"]["f0"] + 30, 0.0)],
                node="glow")
# the six columns: rise to the logits, then softmax, then the temperature (sampled every 2 frames)
for j, (mr, liq, lm) in enumerate(meters):
    K.show(mr, [(0, False), (S.f_logit - 14, True)])
    keys, gk = [], []
    for fr in range(S.f_logit - 12, END + 1, 2):
        mode, lv, _ = S.levels(fr)
        keys.append((fr, (1, 1, min(1.0, lv[j]))))
        gk.append((fr, 3.0 + 3.0 * min(1.0, lv[j])))
    K.key(liq, "scale", [(0, (1, 1, 0.001))] + keys)
    K.glow_keys(lm, [(0, 0.0)] + gk)
# the dial: appears with "temperature", the knob follows T
f_dial = w("b3", "dial")
K.show(dl, [(0, False), (f_dial - 20, True)])
dz = dl.location.z
K.key(dl, "location", [(0, (1.45, -0.15, dz - 0.6)), (f_dial - 20, (1.45, -0.15, dz - 0.6)), (f_dial + 6, (1.45, -0.15, dz))])
rk = []
for fr in range(f_dial - 20, END + 1, 2):
    rk.append((fr, (0, P4.dial_angle(S.T(fr)), 0)))
K.key(knob, "rotation_euler", rk)
# b5: one token is drawn: a "We" tile rises from behind the We column and comes forward
f_drawn, f_we = w("b5", "drawn"), w("b5", "we")
K.show(wtile, [(0, False), (f_drawn - 10, True)])
K.key(wtile, "location", [(0, (mx[0], 0.1, 0.05)), (f_drawn - 10, (mx[0], 0.1, 0.05)), (f_drawn + 14, (mx[0], 0.12, 1.0)),
                          (f_we + 10, (0.15, -0.55, 0.62)), (END, (0.15, -0.55, 0.62))])
wtile.rotation_euler = (0, 0, 0)
K.key(wtile, "rotation_euler", [(f_drawn + 14, (0.0, 0, 0)), (f_we + 10, (1.05, 0, 0))])
K.glow_keys(wface, [(0, 0.0), (f_drawn, 0.0), (f_drawn + 14, 4.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_top", lens=40, fstop=3.2).cut(0)
c1.keys([(0, (-2.35, -1.05, ZTOP + 0.3), (-3.25, 0.15, ZTOP + 0.02)), (b["b1"]["f1"] + 10, (-2.55, -0.85, ZTOP + 0.42), (-3.3, 0.1, ZTOP + 0.25))])
c2 = K.Cam(sc, "c_rack", lens=30, fstop=4.0).cut(b["b2"]["f0"] - 6)
c2.keys([(b["b2"]["f0"] - 6, (2.9, -1.2, 1.05), (0.0, 0.8, 0.65)), (f_every + 10, (2.6, -0.9, 0.95), (-1.5, 0.9, 0.6)),
         (f_score - 4, (0.5, -1.3, 1.1), (-6.0, 0.9, 0.6))])
c3 = K.Cam(sc, "c_bars", lens=35, fstop=4.0).cut(f_score + 6)
c3.keys([(f_score + 6, (-0.1, -2.75, 1.0), (-0.1, 0.0, 0.5)), (b["b3"]["f0"] + 10, (-0.1, -2.6, 0.95), (-0.1, 0.0, 0.48)),
         (f_dial - 10, (0.1, -2.9, 0.98), (0.2, 0.0, 0.47))])
c4 = K.Cam(sc, "c_dial", lens=32, fstop=5.0).cut(f_dial - 8)
c4.keys([(f_dial - 8, (0.3, -3.25, 1.0), (0.25, 0.0, 0.45)), (b["b4"]["f1"] + 10, (0.25, -3.05, 0.95), (0.25, 0.0, 0.45))])
c5 = K.Cam(sc, "c_pick", lens=40, fstop=3.2).cut(b["b5"]["f0"] - 8)
c5.keys([(b["b5"]["f0"] - 8, (-0.3, -2.6, 0.95), (-0.4, 0.0, 0.55)), (f_we + 20, (0.1, -2.3, 0.85), (0.1, -0.3, 0.55)),
         (END, (0.15, -2.15, 0.82), (0.1, -0.3, 0.55))])

pins = [f"m{j}_top" for j in range(6)] + [f"m{j}" for j in range(6)] + ["vec_top", "rack_pin", "dial_top", "dial_t0", "dial_t07",
                                                                         "dial_t10", "dial_t12", "we_top", "we_front"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
