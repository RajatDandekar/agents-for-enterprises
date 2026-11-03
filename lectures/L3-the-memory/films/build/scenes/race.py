"""Film 3 of Lecture 3, "The race": RAG against the LLM Wiki on the same 224 questions. Builds race.blend.

A stack of 224 question cards at the start gate; four glass lanes (RAG, the wiki's navigation, the hybrid, sections
alone) and a fifth, closed with an ember barrier (pasting the whole dump: it fits no model). Two races run on the
real recorded times: Q-0412 in real time, Q-EMMA at 1.5x; each capsule turns from violet (finding sources) to sky
(answering) at its real retrieval time, and its finish bar lights green or ember with the judge's verdict. Then the
whole golden set: a glass meter per lane fills to its answer-correct rate; a light strip runs down each lane as long
as its median time to answer (0.25 m per second); a stack of coins per lane, one coin per tenth of a cent a question.
The close: RAG's lane lights, the others dim.

Numbers: data/l3_data.json["race"] (make_data.py, from experiments/logs/race.json). Timing: timeline/race.json.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402
import props_l3 as Q  # noqa: E402

FILM = "race"
B = K.Beats(FILM)
R = K.load("films/build/data/l3_data.json")["race"]
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11
FPS = 30
lit = K.glow_keys

sc = K.reset(B.frames)
K.studio(sc, focus=(0.4, 0.2, 0.4), key_power=3200, span=3.0)
K.soft_light("keyR", (3.0, -6.0, 7.5), (3.0, 0.3, 0.3), 1700, 12.0, (1.0, 0.97, 0.93))
K.soft_light("rimR", (3.0, 7.0, 3.2), (3.0, 0.3, 0.3), 1100, 14.0, (0.7, 0.82, 1.0))
K.plinth("track", -3.4, 3.9, y=0.05, depth=2.1, height=PZ)

M = ["rag", "wiki", "hybrid", "sections"]
LANE_Y = {"rag": -0.62, "wiki": -0.26, "hybrid": 0.1, "sections": 0.46}
PASTE_Y = 0.82
X0, X1 = -1.8, 2.2
LZ = PZ + 0.035
CZ = LZ + 0.005
COL = {"rag": K.SKY, "wiki": K.lin("#9a5cff"), "hybrid": K.lin("#5fc1d8"), "sections": K.lin("#8a97ab")}

# ------------------------------------------------------------------------------------------------ the start: 224 questions, the gate
qs = Q.sheet_stack("qstack", (-2.75, 0.0, PZ), R["n"] * 0.0026, kind="card", w=0.2, d=0.15, pitch=0.0026, seed=5)
gate = Q.reader("gate", (-2.05, 0.1, PZ), span=1.62, h=0.3, d=0.16)
gate["root"].rotation_euler = (0, 0, math.pi / 2)
lit(gate["ring"], [(0, 0.5)])

# ------------------------------------------------------------------------------------------------ the lanes
lane_m, fin_m, strip = {}, {}, {}
for m in M:
    y = LANE_Y[m]
    P.rail(f"lane_{m}", X0 - 0.1, X1 + 0.08, y, LZ)
    lm = K.light_mat(f"lanelight_{m}", COL[m], 0.0)
    K.rbox(f"lanelight_{m}", (X1 - X0, 0.006, 0.003), bevel=0.0, seg=1, mat=lm, loc=((X0 + X1) / 2, y - 0.045, PZ + 0.002)).visible_shadow = False
    lane_m[m] = lm
    # the finish: an aluminium post with a glass bar that lights green (right) or ember (wrong)
    K.rbox(f"post_{m}", (0.05, 0.05, 0.26), bevel=0.008, seg=3, mat=K.M("alu"), loc=(X1 + 0.14, y + 0.08, PZ + 0.13))
    fm = K.light_mat(f"fin_{m}", K.GREEN, 0.0)
    K.rbox(f"finbar_{m}", (0.04, 0.16, 0.035), bevel=0.006, seg=2, mat=fm, loc=(X1 + 0.14, y, PZ + 0.24)).visible_shadow = False
    fin_m[m] = fm
    K.empty(f"fin_{m}_pin", (X1 + 0.14, y - 0.05, PZ + 0.3))
    K.empty(f"start_{m}_pin", (X0 - 0.05, y - 0.04, PZ + 0.06))
    K.empty(f"mid_{m}_pin", (X0 + 1.1, y - 0.03, PZ + 0.05))
    # the time strip (b6): grows from the start as long as the median time to answer
    sm = K.light_mat(f"strip_{m}", COL[m], 0.0)
    s = K.rbox(f"strip_{m}", (1.0, 0.018, 0.004), bevel=0.0, seg=1, mat=sm, loc=(0, 0, 0))
    s.data.transform(__import__("mathutils").Matrix.Translation((0.5, 0, 0)))
    s.location = (X0, y + 0.05, PZ + 0.003)
    s.visible_shadow = False
    strip[m] = (s, sm)
    K.empty(f"strip_{m}_end", (0, 0, 0))
# pasting everything: a fifth lane, closed by an ember barrier
P.rail("lane_paste", X0 - 0.1, X0 + 0.9, PASTE_Y, LZ)
bar_m = K.light_mat("paste_bar", K.EMBER, 0.0)
K.rbox("paste_barrier", (0.03, 0.22, 0.12), bevel=0.006, seg=2, mat=K.M("alu_dark"), loc=(X0 + 0.95, PASTE_Y, PZ + 0.06))
K.rbox("paste_barlight", (0.034, 0.2, 0.02), bevel=0.0, seg=1, mat=bar_m, loc=(X0 + 0.95, PASTE_Y, PZ + 0.09)).visible_shadow = False
K.empty("paste_pin", (X0 + 0.95, PASTE_Y - 0.05, PZ + 0.16))
f_paste = w("b2", "pasting")
lit(bar_m, [(0, 0.0), (f_paste - 4, 0.0), (f_paste + 6, 5.0), (w("b2", "model") + 30, 2.0), (blk["b3"]["f0"], 0.6)])
for m, word in (("rag", "rag"), ("wiki", "wiki"), ("hybrid", "hybrid"), ("sections", "sections")):
    f0 = w("b2", word, 1 if m == "sections" else 0) - 2
    lit(lane_m[m], [(0, 0.0), (f0, 0.0), (f0 + 6, 4.0), (f0 + 40, 1.0)])

# ------------------------------------------------------------------------------------------------ the two races
RACES = [("q0412", "Q-0412", w("b3", "go"), 1.0), ("qemma", "Q-EMMA", w("b4", "go"), 1.5)]
for tag, qid, go, speed in RACES:
    ex = R["examples"][qid]
    end_race = blk["b5"]["f0"] - 14 if tag == "qemma" else blk["b4"]["f0"] - 14
    for m in M:
        e = ex[m]
        y = LANE_Y[m]
        f_ret = go + int(round(e["retrieval_s"] * FPS / speed))
        f_fin = go + int(round(e["total_s"] * FPS / speed))
        cp, cm = P.capsule(f"{tag}_{m}", (X0, y, CZ + 0.03), color=K.lin("#9a5cff"), size=(0.14, 0.07, 0.05))
        K.show(cp, [(0, False), (go - 12, True), (end_race, False)])
        K.key(cp, "location", [(0, Vector((X0 - 0.25, y, CZ + 0.03))), (go - 12, Vector((X0 - 0.25, y, CZ + 0.03))),
                               (go, Vector((X0, y, CZ + 0.03)))])
        # constant speed from the gate to the finish over its real time (the colour turns at its real retrieval time)
        keys = []
        n = max(2, (f_fin - go) // 3)
        for i in range(n + 1):
            f = go + (f_fin - go) * i / n
            keys.append((int(round(f)), Vector((X0 + (X1 - X0) * i / n, y, CZ + 0.03))))
        K.key(cp, "location", keys)
        node = cm.node_tree.nodes["Emission"].inputs["Color"]
        K.keyval(node, [(0, K.lin("#9a5cff")), (f_ret, K.lin("#9a5cff")), (f_ret + 3, COL[m] if m != "wiki" else K.SKY)])
        lit(cm, [(0, 2.0), (f_fin, 2.0), (f_fin + 6, 6.0), (f_fin + 30, 2.0)])
        ok = e["judge"]
        # this race's finish bar, in the judge's colour (one bar per race and lane, shown only during its race)
        fm = K.light_mat(f"fin_{tag}_{m}", K.GREEN if ok else K.EMBER, 0.0)
        fb = K.rbox(f"finbar_{tag}_{m}", (0.042, 0.162, 0.037), bevel=0.006, seg=2, mat=fm, loc=(X1 + 0.14, y, PZ + 0.24))
        fb.visible_shadow = False
        K.show(fb, [(0, False), (go - 12, True), (end_race, False)])
        lit(fm, [(0, 0.0), (f_fin - 1, 0.0), (f_fin + 3, 6.0), (end_race - 10, 3.0), (end_race, 0.0)])
        K.empty(f"{tag}_{m}_pin", (0, 0, 0.06), parent=cp)
# the colour keys need constant steps
for m in bpy.data.materials:
    nt = m.node_tree
    if nt and nt.animation_data and nt.animation_data.action:
        for fc in nt.animation_data.action.fcurves:
            if "inputs[0]" in fc.data_path and "Emission" in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------------------------------------ the whole set: meters, time strips, coins
MX = X1 + 0.55
O = R["overall"]
f_acc = {"hybrid": w("b5", "ninety-two"), "rag": w("b5", "eighty-nine"), "wiki": w("b5", "eighty-nine") + 6, "sections": w("b5", "seventy-nine")}
for m in M:
    y = LANE_Y[m]
    root, liq, lm = K.meter(f"meter_{m}", (MX, y, PZ), height=0.45, r=0.022, color=COL[m])
    v = O[m]["answer_correct"]
    f0 = f_acc[m]
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (f0 - 6, (1, 1, 0.001)), (f0 + 24, (1, 1, v))])
    lit(lm, [(0, 0.0), (f0 - 6, 0.0), (f0, 3.0), (blk["b9"]["f0"], 2.0)])
f_strip = {"rag": w("b6", "rag"), "wiki": w("b6", "wiki", 1), "hybrid": w("b6", "hybrid", 1), "sections": w("b6", "rag") + 8}
for m in M:
    s, sm = strip[m]
    L = O[m]["answer_p50_s"] * 0.25
    f0 = f_strip[m]
    K.key(s, "scale", [(0, (0.001, 1, 1)), (f0 - 2, (0.001, 1, 1)), (f0 + 30, (L, 1, 1))])
    lit(sm, [(0, 0.0), (f0 - 2, 0.0), (f0 + 4, 3.0), (blk["b7"]["f0"] + 30, 1.4)])
    K.empty(f"strip_{m}_pin", (X0 + L, LANE_Y[m] + 0.05, PZ + 0.03))
coin_m = K.principled("coin", (0.86, 0.68, 0.36, 1), rough=0.28, metallic=1.0)
f_cost = {"rag": w("b7", "rag"), "hybrid": w("b7", "hybrid"), "wiki": w("b7", "navigation"), "sections": w("b7", "navigation") + 10}
CX = MX + 0.42
for m in M:
    y = LANE_Y[m]
    n = max(1, int(round(O[m]["cost_per_q_usd"] * 1000)))   # one coin per tenth of a cent
    root = K.empty(f"coins_{m}", (CX, y, PZ))
    for k in range(n):
        K.cyl(f"coin_{m}_{k}", 0.045, 0.0062, coin_m, loc=(0.0015 * math.sin(k * 1.7), 0.0015 * math.cos(k * 2.3), 0.0034 + k * 0.0068),
              verts=40, bevel=0.0012, parent=root)
    K.empty(f"coins_{m}_pin", (0, -0.05, n * 0.0068 + 0.02), parent=root)
    f0 = f_cost[m]
    K.key(root, "scale", [(0, (1, 1, 0.001)), (f0 - 2, (1, 1, 0.001)), (f0 + 26, (1, 1, 1))])

# ------------------------------------------------------------------------------------------------ the decision
f_uses = w("b9", "uses")
for m in M:
    if m == "rag":
        lit(lane_m[m], [(f_uses - 4, 1.0), (f_uses + 6, 6.0), (END, 4.0)])
    else:
        lit(lane_m[m], [(f_uses - 4, 1.0), (f_uses + 10, 0.15)])
lit(gate["ring"], [(f_uses - 4, 0.5), (f_uses + 6, 4.0)])

# ------------------------------------------------------------------------------------------------ cameras
b = blk
c1 = K.Cam(sc, "c_start", lens=34, fstop=4.5).cut(0)
c1.keys([(0, (-3.9, -2.6, 1.35), (-2.4, 0.0, 0.35)),
         (b["b1"]["f1"] + 18, (-3.5, -2.9, 1.6), (-1.8, 0.05, 0.3))])
c2 = K.Cam(sc, "c_lanes", lens=30, fstop=5.0).cut(b["b2"]["f0"] - 12)
c2.keys([(b["b2"]["f0"] - 12, (-3.6, -1.9, 1.25), (-0.6, 0.0, 0.15)),
         (b["b2"]["f1"] + 18, (-3.4, -1.3, 1.45), (0.2, 0.3, 0.1))])
c3 = K.Cam(sc, "c_race", lens=28, fstop=6.0).cut(b["b3"]["f0"] - 12)
c3.keys([(b["b3"]["f0"] - 12, (0.55, -4.4, 2.55), (0.6, 0.0, 0.05)),
         (b["b4"]["f1"] + 18, (0.7, -4.3, 2.6), (0.7, 0.0, 0.05))])
c5 = K.Cam(sc, "c_meters", lens=36, fstop=4.0).cut(b["b5"]["f0"] - 12)
c5.keys([(b["b5"]["f0"] - 12, (1.4, -2.5, 1.3), (MX, 0.0, 0.3)),
         (b["b5"]["f1"] + 18, (1.7, -2.4, 1.25), (MX + 0.1, 0.0, 0.3))])
c6 = K.Cam(sc, "c_clock", lens=28, fstop=6.0).cut(b["b6"]["f0"] - 12)
c6.keys([(b["b6"]["f0"] - 12, (-2.9, -2.5, 1.9), (-0.3, 0.0, 0.05)),
         (b["b6"]["f1"] + 18, (-2.4, -2.9, 2.1), (0.0, 0.0, 0.05))])
c7 = K.Cam(sc, "c_cost", lens=36, fstop=4.0).cut(b["b7"]["f0"] - 12)
c7.keys([(b["b7"]["f0"] - 12, (CX + 0.9, -2.2, 1.35), (CX - 0.05, 0.0, 0.12)),
         (b["b7"]["f1"] + 18, (CX + 1.05, -2.05, 1.3), (CX - 0.05, 0.0, 0.12))])
c8 = K.Cam(sc, "c_types", lens=26, fstop=8.0).cut(b["b8"]["f0"] - 12)
c8.keys([(b["b8"]["f0"] - 12, (0.4, -4.4, 2.6), (0.6, 0.1, 0.1)),
         (b["b8"]["f1"] + 18, (0.6, -4.2, 2.8), (0.6, 0.1, 0.1))])
c9 = K.Cam(sc, "c_decision", lens=30, fstop=5.0).cut(b["b9"]["f0"] - 12)
c9.keys([(b["b9"]["f0"] - 12, (-3.2, -2.6, 1.3), (0.4, -0.4, 0.15)),
         (END, (-2.6, -3.2, 1.6), (0.8, -0.3, 0.15))])

pins = ["qstack_top", "gate_pin", "paste_pin"] + [f"fin_{m}_pin" for m in M] + [f"start_{m}_pin" for m in M] + [f"mid_{m}_pin" for m in M] + \
       [f"{t}_{m}_pin" for t in ("q0412", "qemma") for m in M] + [f"meter_{m}_top" for m in M] + [f"strip_{m}_pin" for m in M] + \
       [f"coins_{m}_pin" for m in M]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
