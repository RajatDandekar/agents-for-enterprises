"""Film 2, "What the model sees": the context window filling, part by part, with the real tokens. Builds context.blend.

The model (the sealed L2 machine) faces a tall glass vitrine: its context window. Slabs drop in, one per part, each
as tall as its real token count (1 mm per token): system prompt 654, tool definitions 128 (a ghost slab shows 1,555
for all 16), Emma's message 17, the model's tool call 23, the tool result 229, the reply 57. The request leaves through
a slot in a tall black wall; behind it, in a dark booth, are the tool (tool.py), the Ledgerline cabinets, the database,
Emma's session card and a padlock for her password: none of it ever reaches the vitrine. Then Emma's full order: eleven
columns, one per model call, each stacked with that call's real context (0.24 mm per token).

Numbers: build/data/l4_data.json (from experiments/logs/our_harness.json: run single and run order_hands).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402

FILM = "context"
B = K.Beats(FILM)
DATA = K.load("films/build/data/l4_data.json")
CS, CO = DATA["context_single"], DATA["context_order"]
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11

sc = K.reset(B.frames)
K.studio(sc, focus=(-0.6, 0.2, 0.5), key_power=3000)
K.soft_light("keyF", (-1.0, -7.5, 4.0), (-1.0, -1.6, 0.5), 900, 10.0, (1.0, 0.97, 0.93))
K.plinth("bench", -3.0, 0.72, y=0.15, depth=1.7, height=PZ)

# ------------------------------------------------------------------------------------------------ the model and its context window
MX = -2.2
K.rbox("riser", (1.12, 0.72, 0.04), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(MX, 0.0, PZ + 0.02))
MA = P.machine("model", (MX, 0.0, PZ + 0.04), w=1.0, d=0.6, h=0.8)
LANE = PZ + 0.04 + 0.105
CX, CY = -0.78, 0.62
CASE = P.context_case("ctx", (CX, CY, PZ), w=0.6, d=0.44, h=1.3)
FZ = CASE["floor_z"]
SW, SD = 0.56, 0.4
MM = 0.001                    # 1 mm per token


def think(f0, f1, peak=2.4):
    K.glow_keys(MA["led"], [(f0 - 6, 0.3), (f0, peak), (f1, peak), (f1 + 10, 0.3)])
    K.glow_keys(MA["tower"]["idle"], [(f0 - 8, 0.4), (f0, 2.6), (f1, 2.6), (f1 + 12, 0.4)])


K.glow_keys(MA["led"], [(0, 0.3)])
K.glow_keys(MA["tower"]["idle"], [(0, 0.4)])
K.key(MA["inner"].data, "energy", [(0, 6.0)])

# the six parts of the single question (five measured prompt parts + the written reply)
parts = [dict(p) for p in CS["parts"]] + [{"kind": "reply", "tokens": CS["completion_tokens"][-1], "label": "reply"}]
z = FZ
slabs = []
for k, p in enumerate(parts):
    h = p["tokens"] * MM
    r, em, core = P.part_slab(f"s{k}", (CX, CY, z), (SW, SD, h), p["kind"], glow=0.0)
    p["z"] = z
    slabs.append((r, em, core, p))
    z += h + 0.003
TOP = FZ + 1.42

f_drop = [w("b2", "system"), w("b3", "two"), w("b4", "seventeen"), w("b4", "answers"), w("b6", "two"), w("b7", "writes")]
for (r, em, core, p), f0 in zip(slabs, f_drop):
    home = Vector((CX, CY, p["z"]))
    K.show(r, [(0, False), (f0 - 2, True)])
    K.key(r, "location", [(0, home + Vector((0, 0, TOP - p["z"]))), (f0 - 2, home + Vector((0, 0, TOP - p["z"]))), (f0 + 20, home)])
    K.glow_keys(em, [(0, 0.0), (f0 - 2, 0.0), (f0 + 16, 5.0), (f0 + 60, 2.2)])
    K.glow_keys(core, [(0, 0.0), (f0 + 10, 0.0), (f0 + 22, 1.2), (f0 + 70, 0.45)])
K.glow_keys(CASE["led"], [(0, 0.3), (w("b1", "context") - 4, 0.3), (w("b1", "context") + 6, 3.0), (w("b1", "context") + 40, 1.0)])

# the ghost: all 16 tool definitions (1,555 tokens), rising beside the vitrine and fading
GX = -0.08
gh = CS["defs_16_tokens"] * MM
gr, gem, gcore = P.part_slab("ghost", (GX, CY, PZ + 0.05), (0.42, 0.32, gh), "defs", glow=0.0)
K.rbox("ghostbase", (0.5, 0.4, 0.05), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(GX, CY, PZ + 0.025))
f_g = w("b3", "all")
K.show(gr, [(0, False), (f_g - 2, True), (blk["b4"]["f0"] + 30, False)])
K.key(gr, "scale", [(0, (1, 1, 0.002)), (f_g - 2, (1, 1, 0.002)), (f_g + 40, (1, 1, 1)), (blk["b4"]["f0"] + 4, (1, 1, 1)),
                    (blk["b4"]["f0"] + 28, (1, 1, 0.002))])
K.glow_keys(gem, [(0, 0.0), (f_g, 4.0), (blk["b4"]["f0"], 3.0), (blk["b4"]["f0"] + 28, 0.0)])
K.glow_keys(gcore, [(0, 0.0), (f_g + 10, 0.9), (blk["b4"]["f0"], 0.6), (blk["b4"]["f0"] + 28, 0.0)])


def read_scan(f0, top_z, dur=40):
    s = CASE["scan"]
    base = Vector(s.location)
    K.key(s, "location", [(0, base), (f0, base), (f0 + dur, base + Vector((0, 0, top_z - FZ))), (f0 + dur + 1, base)])
    K.glow_keys(CASE["scan_m"], [(f0 - 1, 0.0), (f0, 4.0), (f0 + dur, 4.0), (f0 + dur + 1, 0.0)])


K.glow_keys(CASE["scan_m"], [(0, 0.0)])
read_scan(w("b4", "reads"), slabs[2][3]["z"] + 0.02)
think(w("b4", "reads"), w("b4", "answers") + 10)
read_scan(w("b7", "reads"), slabs[4][3]["z"] + 0.23)
think(w("b7", "reads"), w("b7", "writes") + 16)

# ------------------------------------------------------------------------------------------------ the wall and the dark booth
WX = 0.86
WALL, wall_em = P.wall("wall", (WX, 0.0, 0.0), w=3.4, h=1.85, t=0.07, slot=(0.34, 0.14), slot_z=LANE)
K.glow_keys(wall_em, [(0, 0.0)])
P.booth("booth", WX + 0.04, 4.0, -1.05, 1.65, h=1.85)
K.plinth("benchB", 1.0, 3.8, y=0.0, depth=1.2, height=PZ)
inner = bpy.data.lights.new("booth_light", "AREA")
inner.energy, inner.size, inner.color = 0.0, 2.5, (0.62, 0.72, 0.95)
il = bpy.data.objects.new("booth_light", inner)
bpy.context.collection.objects.link(il)
il.location = (2.4, -0.3, 1.7)
il.rotation_euler = (0, 0, 0)
il.visible_glossy = False
TX = 1.95
TOOL = P.tool_unit("tool", (TX, 0.0, PZ), DATA["check_stock_lines"])
lid = TOOL["lid"]
K.show(lid, [(0, False)])
K.key(TOOL["inner"].data, "energy", [(0, 6.0)])
CABX = [1.35, 2.0, 2.65]
cabs = [P.cabinet(f"cab{k}", (x, 1.22, 0.0)) for k, x in enumerate(CABX)]
for c in cabs:
    K.glow_keys(c["lamp"], [(0, 0.25)])
db, db_m = P.database("db", (3.3, 0.1, PZ))
bd, bd_m = P.badge("badge", (3.2, -0.38, PZ))
P.padlock("lock", (3.55, -0.36, PZ), s=1.2)
# conduits from the tool's ports to the cabinets (the services), as in film 1
PORT_Y, PORT_Z = 0.31 + 0.04, PZ + 0.035 + 0.3 * 0.62
cond = []
for j, ci in enumerate((0, 1, 2, 2)):
    a = Vector((TX - 0.36 + j * 0.24, PORT_Y, PORT_Z))
    d = Vector((CABX[ci] + (0.02 * (j - 2.5) if ci == 2 else 0), 1.22 - 0.23 - 0.034, cabs[ci]["port_z"]))
    pts = P.cubic(a, a + Vector((0, 0.25, 0.02)), d + Vector((0, -0.25, 0)), d, n=32)
    cond.append(P.conduit(f"cond{j}", pts, r=0.013))
P.rail("lane_in", WX + 0.05, TX - 0.7, 0.0, LANE)
P.rail("lane", MX + 0.56, WX - 0.06, 0.0, LANE)

f_runs, f_py, f_four, f_db, f_sess, f_pw, f_none = (w("b5", "runs"), w("b5", "tool", 1), w("b5", "four"), w("b5", "database"),
                                                    w("b5", "session"), w("b5", "password"), w("b5", "none"))
# the booth light comes up only for the look inside, then goes dark again
K.key(inner, "energy", [(0, 0.0), (f_py - 30, 0.0), (f_py - 6, 650.0), (f_none + 10, 650.0), (f_none + 40, 0.0)])
for m in TOOL["bars"]:
    if m is not None:
        K.glow_keys(m, [(0, 0.0), (f_py - 6, 0.0), (f_py + 10, 2.6), (f_none + 30, 1.2), (END, 1.2)])
for j, (tube, strand, sm) in enumerate(cond):
    f0 = f_four - 6 + j * 6
    K.grow(strand, [(0, 0.0), (f0, 0.0), (f0 + 14, 1.0)])
    K.glow_keys(sm, [(0, 0.0), (f0, 0.0), (f0 + 2, 3.5), (f_none + 30, 1.0)])
    _, ist, ism = TOOL["inner_tubes"][j]
    K.grow(ist, [(0, 0.0), (f0 - 8, 0.0), (f0, 1.0)])
    K.glow_keys(ism, [(0, 0.0), (f0 - 8, 0.0), (f0 - 6, 3.5), (f_none + 30, 1.0)])
for c in cabs:
    K.glow_keys(c["ok"], [(0, 0.0), (f_four + 10, 0.0), (f_four + 16, 3.5), (f_none + 30, 1.0)])
K.glow_keys(db_m, [(0, 0.0), (f_db - 4, 0.0), (f_db + 4, 3.0), (f_none + 30, 0.8)])
K.glow_keys(bd_m, [(0, 0.0), (f_sess - 4, 0.0), (f_sess + 4, 3.0), (f_none + 30, 0.8)])

# the request capsule: out of the model, past the vitrine, through the slot, into the tool's gate
cap, cap_m = P.capsule("cap", (MX + 0.4, 0.0, LANE))
f_call = w("b4", "answers")
SLOT_IN = Vector((MX + 0.58, 0.0, LANE))
K.show(cap, [(0, False), (f_call + 30, True), (f_py + 20, False)])
K.key(cap, "location", [(0, SLOT_IN - Vector((0.2, 0, 0)))])
P.travel(cap, [SLOT_IN - Vector((0.2, 0, 0)), Vector((-0.2, 0, LANE))], f_call + 30, blk["b4"]["f1"] + 10)
P.travel(cap, [Vector((-0.2, 0, LANE)), Vector((WX, 0, LANE)), Vector((TX - 0.75, 0, LANE)), Vector((TX - 0.5, 0, LANE))], f_runs - 10, f_runs + 40)
K.glow_keys(wall_em, [(f_runs + 4, 0.0), (f_runs + 12, 4.0), (f_runs + 40, 0.6), (w("b6", "comes") - 6, 0.6), (w("b6", "comes"), 4.0),
                      (w("b6", "two") + 20, 0.6)])
K.glow_keys(TOOL["ring_ok"], [(0, 0.0), (f_runs + 22, 0.0), (f_runs + 28, 4.0), (f_runs + 70, 0.0)])

# the result: out of the tool, round the front, back through the slot, up to the vitrine (where its slab drops in)
res, res_m, res_in = P.result_slab("res", (TX + 0.5, 0.0, LANE))
f_back = w("b6", "comes")
K.show(res, [(0, False), (f_back - 40, True), (w("b6", "two") + 2, False)])
K.key(res, "location", [(0, Vector((TX + 0.45, 0.0, LANE)))])
P.travel(res, [Vector((TX + 0.45, 0.0, LANE)), Vector((TX + 0.9, -0.0, LANE)), Vector((TX + 0.9, -0.52, LANE)), Vector((WX + 0.2, -0.52, LANE)),
               Vector((WX + 0.2, 0.0, LANE)), Vector((WX - 0.3, 0.0, LANE))], f_back - 40, f_back + 18)
P.travel(res, [Vector((WX - 0.3, 0.0, LANE)), Vector((CX + 0.3, 0.2, TOP - 0.1)), Vector((CX, CY, TOP))], f_back + 30, w("b6", "two") + 2)
K.glow_keys(TOOL["out"], [(0, 0.0), (f_back - 44, 0.0), (f_back - 38, 4.0), (f_back + 20, 0.6)])

# ------------------------------------------------------------------------------------------------ the full order: eleven columns
ROWY, RX0, RDX = -1.75, -2.45, 0.27
MMO = 0.00024
cols = []
f_every = w("b8", "every")
for k, st in enumerate(CO["steps"]):
    x = RX0 + k * RDX
    base = K.rbox(f"col{k}_base", (0.22, 0.2, 0.03), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(x, ROWY, PZ - 0.02))
    K.empty(f"col{k}_pin", (x, ROWY - 0.1, PZ + st["prompt_tokens"] * MMO + 0.05))
    zz = PZ - 0.005
    f0 = f_every + k * 44
    objs = [base]
    for i, p in enumerate(CO["parts"][:st["n_parts"]]):
        h = p["tokens"] * MMO
        r, em, core = P.part_slab(f"col{k}_p{i}", (x, ROWY, zz), (0.18, 0.15, h), p["kind"], glow=0.0)
        fi = f0 + int(i * 22 / max(1, st["n_parts"]))
        K.show(r, [(0, False), (fi - 1, True)])
        K.key(r, "scale", [(0, (1, 1, 0.01)), (fi - 1, (1, 1, 0.01)), (fi + 6, (1, 1, 1))])
        peak = 2.6
        keys = [(0, 0.0), (fi - 1, 0.0), (fi + 4, peak), (fi + 40, 1.4)]
        if p["kind"] == "result" and p["tokens"] == max(q["tokens"] for q in CO["parts"] if q["kind"] == "result"):
            f610 = w("b8", "six")
            fr = w("b8", "rides") + 6 * k
            keys += [(max(fi + 41, f610 - 4), 1.4), (max(fi + 45, f610 + 4), 6.0), (max(fi + 60, fr), 4.0), (max(fi + 64, fr + 6), 7.0),
                     (max(fi + 80, fr + 40), 1.6)]
        K.glow_keys(em, sorted(keys))
        K.glow_keys(core, [(0, 0.0), (fi - 1, 0.0), (fi + 6, 0.5)])
        zz += h + 0.0015
    K.show(base, [(0, False), (f0 - 6, True)])
K.plinth("rowplinth", RX0 - 0.3, RX0 + 10 * RDX + 0.3, y=ROWY, depth=0.5, height=PZ - 0.035)
rp = bpy.data.objects["rowplinth"]
K.show(rp, [(0, False), (blk["b8"]["f0"] - 12, True), (blk["b9"]["f0"] - 10, False)])
for k in range(len(CO["steps"])):
    o = bpy.data.objects[f"col{k}_base"]
    K.show(o, [(blk["b9"]["f0"] - 10, False)])
    for i in range(CO["steps"][k]["n_parts"]):
        K.show(bpy.data.objects[f"col{k}_p{i}"], [(blk["b9"]["f0"] - 10, False)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_open", lens=32, fstop=4.5).cut(0)
c1.keys([(0, (-3.3, -3.4, 1.75), (-0.5, 0.45, 0.6)),
         (w("b1", "does"), (-2.6, -3.0, 1.55), (-0.15, 0.45, 0.6)),
         (blk["b1"]["f1"] + 20, (-2.0, -2.45, 1.3), (-0.8, 0.55, 0.62))])
c2 = K.Cam(sc, "c_case", lens=36, fstop=4.0).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (-1.85, -1.7, 0.85), (-0.95, 0.62, 0.45)),
         (blk["b3"]["f0"], (-1.75, -1.75, 0.95), (-0.85, 0.62, 0.55)),
         (f_g - 20, (-1.55, -2.1, 1.25), (-0.5, 0.62, 0.8)),
         (blk["b3"]["f1"] + 20, (-1.5, -2.15, 1.3), (-0.45, 0.62, 0.85))])
c3 = K.Cam(sc, "c_read", lens=34, fstop=4.0).cut(blk["b4"]["f0"] - 10)
c3.keys([(blk["b4"]["f0"] - 10, (-2.15, -2.3, 1.2), (-1.4, 0.35, 0.62)),
         (blk["b4"]["f1"] + 20, (-1.75, -2.25, 1.05), (-1.05, 0.25, 0.5))])
c4 = K.Cam(sc, "c_wall", lens=34, fstop=4.0).cut(blk["b5"]["f0"] - 10)
c4.keys([(blk["b5"]["f0"] - 10, (-0.55, -1.75, 0.85), (0.6, 0.0, 0.55)),
         (f_py - 12, (-0.25, -1.6, 0.85), (0.75, 0.05, 0.6))])
c5 = K.Cam(sc, "c_booth", lens=30, fstop=5.0).cut(f_py - 10)
c5.keys([(f_py - 10, (1.85, -2.75, 1.25), (2.35, 0.35, 0.55)),
         (f_none - 6, (2.6, -2.6, 1.2), (2.45, 0.3, 0.5))])
c6 = K.Cam(sc, "c_wall2", lens=34, fstop=4.0).cut(f_none - 4)
c6.keys([(f_none - 4, (-0.4, -1.9, 1.1), (0.8, 0.1, 0.75)),
         (blk["b5"]["f1"] + 20, (-0.2, -1.7, 1.0), (0.85, 0.05, 0.7))])
c7 = K.Cam(sc, "c_slot", lens=40, fstop=3.2).cut(blk["b6"]["f0"] - 10)
c7.keys([(blk["b6"]["f0"] - 10, (0.05, -1.05, 0.5), (0.86, 0.0, 0.3)),
         (f_back + 20, (-0.25, -1.2, 0.75), (0.35, 0.1, 0.5))])
c8 = K.Cam(sc, "c_case2", lens=36, fstop=4.0).cut(w("b6", "two") - 30)
c8.keys([(w("b6", "two") - 30, (-1.7, -1.75, 1.35), (-0.8, 0.62, 0.75)),
         (blk["b7"]["f0"] - 4, (-1.75, -1.8, 1.4), (-0.85, 0.62, 0.8))])
c9 = K.Cam(sc, "c_reply", lens=32, fstop=4.0).cut(blk["b7"]["f0"] - 2)
c9.keys([(blk["b7"]["f0"] - 2, (-2.4, -2.55, 1.55), (-1.3, 0.45, 0.75)),
         (blk["b7"]["f1"] + 20, (-2.1, -2.6, 1.6), (-1.0, 0.5, 0.8))])
c10 = K.Cam(sc, "c_order", lens=34, fstop=5.0).cut(blk["b8"]["f0"] - 10)
c10.keys([(blk["b8"]["f0"] - 10, (-2.6, -3.9, 1.0), (-1.95, -1.75, 0.45)),
          (f_every + 200, (-1.6, -4.3, 1.1), (-1.25, -1.75, 0.5)),
          (blk["b8"]["f1"] + 20, (-0.85, -4.7, 1.25), (-1.05, -1.75, 0.55))])
c11 = K.Cam(sc, "c_close", lens=30, fstop=5.6).cut(blk["b9"]["f0"] - 10)
c11.keys([(blk["b9"]["f0"] - 10, (-2.35, -3.1, 1.95), (0.0, 0.45, 0.6)),
          (END, (-1.2, -3.8, 2.4), (0.6, 0.5, 0.65))])

pins = ["model_pin_top", "model_pin_out", "ctx_top", "ctx_base_pin", "ghost_top", "ghost_r", "cap_top", "res_top", "wall_slot", "wall_top",
        "tool_core", "cab1_top", "db_top", "badge_top", "lock_top", "tool_gate_top"]
pins += [f"s{k}_r" for k in range(len(slabs))] + [f"s{k}_l" for k in range(len(slabs))] + [f"s{k}_top" for k in range(len(slabs))]
pins += [f"col{k}_pin" for k in range(len(CO["steps"]))]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
