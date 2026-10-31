"""Film "structure": "Inside the model: 24 blocks" (Lecture 2, section 5, before s4_attention). Builds films/structure.blend.

The stack of 24 identical blocks (attention bay with 14 heads + feed-forward bay), then Emma's question as one row of
100 columns (one per token) entering at the bottom and climbing. The cells are real: films/build/data/structure_data.json holds
the first 16 of 896 numbers of every token's vector entering block 1 and after each block (capture_structure.py);
at every floor the row is replaced by the next block's vectors.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s456 as P4  # noqa: E402

FILM = "structure"
B = K.Beats(FILM)
SD = K.load("films/build/data/structure_data.json")["layers"]
TW_W, TW_D, PITCH = 1.6, 0.62, 0.16
NT, ND = 100, 16
CELL = 0.0142

sc = K.reset(B.frames)
K.studio(sc, focus=(0.0, 0.0, 1.2), key_power=3400)
K.rbox("pedestal", (2.3, 1.2, 0.06), bevel=0.012, seg=4, mat=K.M("plinth"), loc=(-0.2, 0.0, 0.03))
TW = P4.block_tower("bt", (0, 0, 0.06), floors=24, pitch=PITCH, w=TW_W, d=TW_D)
ZF = [z + 0.06 for z in TW["z"]]


def vmax_of(layer):
    a = sorted(abs(x) for r in layer for x in r)
    return a[int(len(a) * 0.95)] or 1.0


# the row of 100 vectors: 25 plates (entering block 1, then after each block) on one carrier
YR = -TW_D / 2 - 0.13
car = K.empty("row", (0.0, YR, ZF[0] + 0.1))
rows = []
for l in range(25):
    L = SD[l]
    vals = [L[c][r] for r in range(ND) for c in range(NT)]
    pr, pm = K.vector_plate(f"row{l}", vals, NT, ND, K.SKY, (0, 0, 0), cell=CELL, vmax=vmax_of(L), glow=4.2, reveal=1.0, parent=car)
    rows.append((pr, pm))
W_ROW = NT * CELL
for i in (0, 86, 92, 99):
    K.empty(f"row_c{i}", (-W_ROW / 2 + (i + 0.5) * CELL, -0.01, -ND * CELL / 2 - 0.012), parent=car)
K.empty("row_pin", (-W_ROW / 2, -0.01, ND * CELL / 2 + 0.02), parent=car)

# ------------------------------------------------------------------------------------------------ timing
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5")}
w = B.w
END = B.frames - 1
# b1: the floors light bottom to top on "twenty-four blocks"
f24 = w("b1", "twenty-four")
for k in range(24):
    K.glow_keys(TW["att"][k], [(0, 0.5), (f24 + k * 3, 0.5), (f24 + k * 3 + 6, 3.5), (f24 + k * 3 + 20, 0.6)])
    K.glow_keys(TW["mlp"][k], [(0, 0.4), (f24 + k * 3 + 2, 0.4), (f24 + k * 3 + 8, 3.0), (f24 + k * 3 + 22, 0.5)])
# b2 / b3: one block up close (floor 3): its heads, then its feed-forward bay
FL = 2
f_att, f_14, f_back = w("b2", "attention"), w("b2", "fourteen"), w("b2", "back")
f_ff, f_self = w("b3", "feed-forward"), w("b3", "itself")
K.glow_keys(TW["att"][FL], [(f_att - 6, 0.6), (f_att + 10, 5.0), (f_ff - 10, 5.0), (f_ff + 6, 0.8)])
K.glow_keys(TW["mlp"][FL], [(f_ff - 6, 0.5), (f_ff + 12, 5.0), (b["b3"]["f1"] + 10, 5.0), (b["b3"]["f1"] + 30, 0.6)])

# b4: the row rises from below into floor 1; there it gathers (attention), is reworked (feed-forward) and comes
# out changed; then it climbs, block by block, swapping to each block's real vectors
f_enter, f_a4, f_f4, f_chg, f_climb = w("b4", "enter"), w("b4", "attention"), w("b4", "feed-forward"), w("b4", "changed"), w("b4", "climb")
f_top = w("b5", "top")
for pr, pm in rows:
    K.show(pr, [(0, False)])
K.show(rows[0][0], [(0, False), (f_enter - 14, True), (f_chg, False)])
z0 = ZF[0] + 0.1
K.key(car, "location", [(0, (0, YR, z0 - 0.6)), (f_enter - 14, (0, YR, z0 - 0.6)), (f_enter + 16, (0, YR, z0))])
K.glow_keys(TW["att"][0], [(f_a4 - 6, 0.6), (f_a4 + 8, 5.0), (f_f4, 5.0), (f_f4 + 12, 0.8)])
K.glow_keys(TW["mlp"][0], [(f_f4 - 6, 0.5), (f_f4 + 10, 5.0), (f_chg, 5.0), (f_chg + 16, 0.8)])
K.show(rows[1][0], [(0, False), (f_chg, True)])
K.keyval(rows[1][1].node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_chg, 0.0), (f_chg + 14, 1.0)])
Fk = {1: f_chg}
step = (f_top - 4 - (f_climb + 6)) / 23
for k in range(2, 25):
    Fk[k] = int(f_climb + 6 + (k - 1) * step)
K.key(car, "location", [(f_climb, (0, YR, z0))] + [(Fk[k], (0, YR, ZF[k - 1] + 0.1)) for k in range(2, 25)] +
      [(f_top + 20, (0, YR, ZF[23] + 0.34))])
for k in range(2, 25):
    pr, pm = rows[k]
    off = Fk[k + 1] if k < 24 else END + 1
    K.show(rows[k - 1][0], [(Fk[k], False)])
    K.show(pr, [(0, False), (Fk[k], True)])
    K.keyval(pm.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (Fk[k], 0.0), (Fk[k] + 6, 1.0)])
    K.glow_keys(TW["att"][k - 1], [(Fk[k] - 6, 0.6), (Fk[k] - 2, 4.0), (Fk[k] + 10, 1.0)])
    K.glow_keys(TW["mlp"][k - 1], [(Fk[k] - 4, 0.5), (Fk[k], 4.0), (Fk[k] + 12, 0.9)])
K.glow_keys(rows[24][1], [(0, 4.2), (f_top, 4.2), (f_top + 14, 6.0)])
# b5: "we open attention": every attention bay glows
f_open = w("b5", "open")
for k in range(24):
    K.glow_keys(TW["att"][k], [(f_open + k, 1.0), (f_open + k + 12, 3.2)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_tower", lens=32, fstop=5.0).cut(0)
c1.keys([(0, (2.9, -6.6, 1.3), (0.0, 0.0, 1.85)), (b["b1"]["f1"] + 12, (2.0, -6.9, 2.5), (0.0, 0.0, 2.0))])
zf = ZF[FL] + 0.05
c2 = K.Cam(sc, "c_block", lens=40, fstop=3.2).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (-0.9, -1.75, zf + 0.42), (-0.25, 0.0, zf)), (f_ff - 14, (-0.55, -1.45, zf + 0.34), (-0.3, 0.0, zf))])
c3 = K.Cam(sc, "c_ffn", lens=40, fstop=3.2).cut(f_ff - 12)
c3.keys([(f_ff - 12, (0.9, -1.55, zf + 0.38), (0.4, 0.0, zf)), (b["b3"]["f1"] + 12, (1.05, -1.4, zf + 0.32), (0.35, 0.0, zf))])
c4 = K.Cam(sc, "c_row", lens=32, fstop=4.0).cut(b["b4"]["f0"] - 8)
c4.keys([(b["b4"]["f0"] - 8, (0.6, -2.6, 0.75), (0.0, YR, 0.4)), (f_chg, (0.35, -2.25, 0.62), (0.0, YR, 0.36)),
         (f_climb, (0.35, -2.25, 0.62), (0.0, YR, 0.36))] +
        [(Fk[k], (0.45, -2.35, ZF[k - 1] + 0.42), (0.0, YR, ZF[k - 1] + 0.12)) for k in (6, 12, 18, 24)])
c5 = K.Cam(sc, "c_top", lens=30, fstop=5.0).cut(f_top - 2)
c5.keys([(f_top - 2, (0.6, -2.4, ZF[23] + 0.55), (0.0, YR, ZF[23] + 0.3)), (END, (2.4, -5.6, 2.9), (0.0, 0.0, 1.9))])

pins = ["row_pin", "row_c0", "row_c86", "row_c92", "row_c99", f"bt_att{FL + 1}", f"bt_mlp{FL + 1}", "bt_att1", "bt_mlp1"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
