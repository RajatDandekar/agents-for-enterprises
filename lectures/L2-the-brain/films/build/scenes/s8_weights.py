"""Film s8, "Where the weights came from". Builds films/s8_weights.blend.

The 24-floor stack with its weights glowing as dense cells; then the tiny GPT (4 floors) whose cells start as noise and
settle as it trains, writing noise and then a well-formed, invented stock line; the real loss curve as a glowing ribbon
on a dark glass chart; a green plaque with the real figure; back to the big stack, its three training stages and the
day its weights were frozen (two calendar blocks).

Numbers: brain3d/trace.json tinygpt (curve, samples, params), training (stages, released, asked), meta.params;
experiments/logs/tinygpt.json (stock_figures). The cell patterns on the floors are illustrative, not real weights.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s789 as P  # noqa: E402

FILM = "s8_weights"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TG = T["tinygpt"]
CURVE = TG["curve"]
UNTRAINED = TG["sample_untrained"].split("stores,", 1)[1][:13]
TRAINED = "2,400 on hand"
PZ = 0.11
w = B.w
END = B.frames - 1
blk = B.blocks
sc = K.reset(B.frames)
K.studio(sc, focus=(2.4, 0.3, 0.45), key_power=3000, span=6.0)
K.plinth("plinth", -2.3, 7.9, depth=0.6, height=PZ)

rnd = random.Random(8)


def noise(n, smooth=False, k=0):
    if not smooth:
        return [rnd.uniform(-1, 1) for _ in range(n)]
    return [0.7 * math.sin(0.21 * i + 0.9 * k) * math.cos(0.05 * i) + 0.15 * rnd.uniform(-1, 1) for i in range(n)]


# ---- the big stack: 24 floors, each with a dense band of weight cells on its front edge
BIG = Vector((0.0, 1.25, 0.0))
big_cells = {k: K.cells_mat(f"bigc{k}", noise(96 * 5, True, k), 96, 5, K.SKY, vmax=1.0, strength=0.0) for k in range(1, 25)}
TW = P.tower2("big", tuple(BIG), floors=24, pitch=0.075, w=1.7, d=0.56, cells=big_cells)
for k in range(1, 25):
    K.glow_keys(TW["led"][k], [(0, 0.3)])
    f0 = w("b1", "weights") + int((k - 1) * 1.5)
    K.glow_keys(big_cells[k], [(0, 0.4), (f0, 0.4), (f0 + 10, 3.2), (blk["b1"]["f1"] + 30, 2.2)])

# ---- the tiny GPT: 4 floors, noise cells that settle into structure as it trains
TINY = Vector((3.2, 0.05, PZ))
tiny_noise = {k: K.cells_mat(f"tn{k}", noise(48 * 4), 48, 4, K.SKY, vmax=1.0, strength=0.0) for k in range(1, 5)}
tiny_train = {k: K.cells_mat(f"tt{k}", noise(48 * 4, True, k + 3), 48, 4, K.SKY, vmax=1.0, strength=0.0) for k in range(1, 5)}
TT = P.tower2("tiny", tuple(TINY), floors=4, pitch=0.13, w=0.95, d=0.36, heads=4, cells=tiny_noise)
for k in range(1, 5):
    fr = TT["floors"][k - 1]
    K.plane(f"tiny_f{k}_cells2", 0.95 * 0.92, 0.13 * 0.62, tiny_train[k], loc=(0, -0.36 / 2 - 0.014, 0.012 + 0.13 * 0.31), parent=fr)
f_rand, f_train0, f_train1 = w("b2", "random"), w("b3", "training"), w("b3", "steps")
for k in range(1, 5):
    K.glow_keys(tiny_noise[k], [(0, 0.0), (blk["b2"]["f0"] - 10, 0.0), (f_rand, 3.0), (f_train0 + 60, 3.0), (f_train1, 0.0)])
    K.glow_keys(tiny_train[k], [(0, 0.0), (f_train0 + 40, 0.0), (f_train1, 3.2)])
    K.glow_keys(TT["led"][k], [(0, 0.3)])
for step in range(8):   # a training pass climbs the little stack over and over
    P.pulse(TT, f_train0 + 30 + step * 46, per_floor=4, peak=3.0, base=0.3, hold=8)

# ---- the loss chart: a dark glass panel, the real curve as a glowing ribbon
CH = Vector((3.25, 0.95, 0.0))
K.rbox("chart_panel", (1.7, 0.04, 1.05), bevel=0.012, seg=4, mat=K.M("graphite"), loc=(CH.x, CH.y, 1.02))
K.rbox("chart_bezel", (1.74, 0.03, 1.09), bevel=0.012, seg=4, mat=K.M("alu"), loc=(CH.x, CH.y + 0.02, 1.02))
K.cyl("chart_stem", 0.025, 0.5, K.M("alu"), loc=(CH.x, CH.y + 0.05, 0.25), verts=24)
K.rbox("chart_foot", (0.6, 0.3, 0.06), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(CH.x, CH.y + 0.05, 0.03))
X0, X1, Z0, Z1 = CH.x - 0.72, CH.x + 0.72, 0.62, 1.42
grid_m = K.glow_mat("grid_m", K.SKY, 0.15)
for g in range(5):
    z = Z0 + (Z1 - Z0) * g / 4
    K.rbox(f"grid{g}", (1.46, 0.004, 0.003), bevel=0.0, seg=1, mat=grid_m, loc=(CH.x, CH.y - 0.024, z))
pts = [(X0 + (X1 - X0) * c["step"] / 1500, CH.y - 0.03, Z0 + (Z1 - Z0) * c["train"] / 4.6) for c in CURVE]
rib_m = K.light_mat("rib_m", K.SKY, 0.0)
rib = P.ribbon("loss", pts, r=0.008, mat=rib_m)
f_loss, f_023 = w("b3", "loss"), w("b3", "three")
K.grow(rib, [(0, 0.0), (f_loss, 0.0), (f_023 + 10, 1.0)])
K.glow_keys(rib_m, [(0, 0.0), (f_loss - 2, 4.0)])
K.empty("loss_start", pts[0])
K.empty("loss_end", pts[-1])

# ---- the tiny GPT's writing: character tiles on the plinth to its right
CS = (0.2, 0.16, 0.06)
OX = 4.05


def chars(prefix, text, f0, step, role, color, rest, end):
    names = []
    for c, ch in enumerate(text):
        nm = f"{prefix}{c}"
        if ch == " ":
            continue
        P.drop_tile(nm, role, (OX + c * 0.235, -0.02, PZ), f0 + c * step, height=0.3, face_color=color, face_rest=rest, end=end, size=CS)
        names.append((nm, ch))
    return names


f_noise = w("b2", "writes") - 4
UN = chars("u", UNTRAINED, f_noise, 3, "system", K.lin("#8a97ab"), 0.08, None)
f_out = blk["b4"]["f0"]
for nm, _ in UN:   # the noise is swept away before the trained line
    K.show(bpy.data.objects[nm], [(0, False), (f_noise - 1, True), (f_out - 6, False)])
TR = []
for c, ch in enumerate(TRAINED):
    if ch == " ":
        continue
    nm = f"tr{c}"
    is_num = ch.isdigit() or ch == ","
    f0 = w("b4", "perfect") - 6 + c * 6
    _, fm = P.drop_tile(nm, "digit" if is_num else "answer", (OX + c * 0.235, -0.02, PZ), f0, height=0.3,
                        face_color=K.EMBER if is_num else K.SKY, face_rest=0.22 if is_num else 0.1, size=CS)
    if is_num:   # the invented figure flashes as it is read out
        fl = w("b4", "two") + c * 4
        K.glow_keys(fm, [(fl - 2, 0.22), (fl + 5, 2.4), (fl + 30, 0.22)])
    TR.append((nm, ch))
PLQ = Vector((7.45, 0.05, PZ))
plq, plq_m = P.plaque("plaque", tuple(PLQ), w=0.7, h=0.24)
f_real = w("b4", "real")
K.show(plq, [(0, False), (f_real - 12, True)])
K.key(plq, "location", [(0, PLQ + Vector((0, 0, 0.45))), (f_real - 12, PLQ + Vector((0, 0, 0.45))), (f_real + 8, PLQ)])
K.glow_keys(plq_m, [(0, 0.0), (f_real, 0.0), (f_real + 12, 4.0)])

# ---- Qwen at scale: three stage sockets in front of the big stack, then the day it froze
stages = []
for s_, (dx, word) in enumerate(((-0.6, "pretraining"), (0.0, "instruction"), (0.6, "preference"))):
    root, m = P.socket(f"stage{s_}", (BIG.x + dx, -0.12, PZ), r=0.14)
    f0 = w("b5", word)
    K.glow_keys(m, [(0, 0.0), (f0 - 4, 0.0), (f0 + 8, 4.0), (END, 2.5)])
    stages.append(f"stage{s_}_top")
f_frozen = w("b5", "frozen")
for k in range(1, 25):   # the weights freeze: the cells go still and cold
    K.glow_keys(big_cells[k], [(f_frozen - 4, 2.2), (f_frozen + 20, 1.0)])
cal = {}
for nm, x, word, col in (("cal_rel", -1.55, "frozen", K.SKY), ("cal_ask", -0.95, "emma", K.EMBER)):
    root = K.empty(nm, (x, -0.02, PZ))
    K.rbox(nm + "_body", (0.42, 0.26, 0.34), bevel=0.02, seg=5, mat=K.M("ceramic"), loc=(0, 0, 0.17), parent=root)
    m = K.glow_mat(nm + "_face", col, 0.0, base=(0.018, 0.022, 0.03, 1))
    K.rbox(nm + "_face", (0.36, 0.01, 0.24), bevel=0.006, seg=3, mat=m, loc=(0, -0.131, 0.15), parent=root)
    for sx in (-1, 1):
        ring = K.cyl(f"{nm}_ring{sx}", 0.018, 0.05, K.M("alu"), loc=(sx * 0.1, -0.06, 0.35), verts=24, parent=root)
        ring.rotation_euler = (math.pi / 2, 0, 0)
    K.empty(nm + "_top", (0, -0.13, 0.36), parent=root)
    f0 = w("b5", word)
    K.show(root, [(0, False), (f0 - 14, True)])
    K.key(root, "location", [(0, (x, -0.02, PZ + 0.5)), (f0 - 14, (x, -0.02, PZ + 0.5)), (f0 + 4, (x, -0.02, PZ))])
    K.glow_keys(m, [(0, 0.0), (f0, 0.0), (f0 + 10, 0.12)])

# ------------------------------------------------------------------------------------------------ cameras
top = BIG + Vector((0, 0, 23 * 0.075))
c1 = K.Cam(sc, "c_big", lens=40, fstop=2.8).cut(0)
c1.keys([(0, (0.95, -0.75, 0.35), (0.05, BIG.y - 0.3, 0.3)),
         (blk["b1"]["f1"] + 10, (0.75, -0.95, 1.45), (0.0, BIG.y - 0.3, 1.25))])
c2 = K.Cam(sc, "c_tiny", lens=40, fstop=2.8).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (3.85, -1.45, 0.8), (3.25, 0.05, 0.38)),
         (f_noise - 20, (3.9, -1.3, 0.72), (3.5, 0.0, 0.32)),
         (blk["b2"]["f1"] + 10, (5.2, -1.25, 0.6), (4.9, 0.0, 0.2))])
c3 = K.Cam(sc, "c_train", lens=34, fstop=3.5).cut(blk["b3"]["f0"] - 10)
c3.keys([(blk["b3"]["f0"] - 10, (2.4, -2.15, 1.0), (3.25, 0.6, 0.7)),
         (f_loss - 6, (2.6, -2.0, 1.05), (3.25, 0.8, 0.85)),
         (blk["b3"]["f1"] + 10, (3.55, -1.55, 1.0), (3.5, CH.y, 0.85))])
c4 = K.Cam(sc, "c_line", lens=36, fstop=2.8).cut(blk["b4"]["f0"] - 10)
c4.keys([(blk["b4"]["f0"] - 10, (4.6, -1.35, 0.62), (4.85, 0.0, 0.2)),
         (f_real - 14, (5.4, -1.45, 0.66), (5.4, 0.0, 0.2)),
         (f_real + 10, (6.9, -1.75, 0.72), (6.6, 0.05, 0.22)),
         (blk["b4"]["f1"] + 10, (7.0, -1.6, 0.68), (6.7, 0.05, 0.22))])
c5 = K.Cam(sc, "c_scale", lens=32, fstop=3.5).cut(blk["b5"]["f0"] - 10)
c5.keys([(blk["b5"]["f0"] - 10, (0.85, -2.2, 0.62), (0.0, 0.45, 0.42)),
         (f_frozen - 20, (0.5, -2.35, 0.6), (-0.2, 0.4, 0.4)),
         (f_frozen + 30, (-0.6, -1.75, 0.72), (-1.1, 0.1, 0.32)),
         (END, (-0.75, -1.6, 0.68), (-1.2, 0.1, 0.32))])

pins = ["big_pin_f24", "big_pin_f12", "big_pin_f1", "tiny_pin_f4", "tiny_pin_f1", "loss_start", "loss_end", "plaque_top",
        "cal_rel_top", "cal_ask_top"] + stages + [f"{n}_front" for n, _ in UN + TR] + [f"{n}_top" for n, _ in UN + TR]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
