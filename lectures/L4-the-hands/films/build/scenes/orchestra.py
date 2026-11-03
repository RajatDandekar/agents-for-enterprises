"""Film 3, "Many tools, one request": Emma's full order on our harness, call by call, then the same request on
Claude's harness, side by side. Builds orchestra.blend.

The model (the sealed L2 machine, inside our harness's open rig of seven control modules) faces a two-tier rack of the
16 tools. Each tool call is a capsule flying from the model to its tool; the tool lights; a tile lands on the trace
strip in front (green: a result, slate: no answer, ember: the guessed date, sky: the write; sky-banded tiles are
Emma's turns). A flashback shows the earlier run's direct order refused at create_purchase_order (ember). Then Claude's
harness (a sealed housing) gets its own strip of 8 calls; the rig's modules light one by one.

Numbers and order: experiments/logs/our_harness.json run order_hands, claude_harness.json runs.order_hands (8 calls);
the flashback from our_harness.json run order. Timing: timeline/orchestra.json.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402
import props_s789 as S7  # noqa: E402

FILM = "orchestra"
B = K.Beats(FILM)
DATA = K.load("films/build/data/l4_data.json")
OURS = K.load("experiments/logs/our_harness.json")["order_hands"]
CL = K.load("experiments/logs/claude_harness.json")["runs"]["order_hands"]
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11

sc = K.reset(B.frames)
K.studio(sc, focus=(-0.3, -0.2, 0.45), key_power=3000)
K.soft_light("keyF", (0.0, -7.5, 4.0), (0.0, -0.8, 0.4), 900, 10.0, (1.0, 0.97, 0.93))
K.plinth("bench", -3.4, 3.1, y=-0.35, depth=2.7, height=PZ)

# ------------------------------------------------------------------------------------------------ our model, inside our harness's rig
MX, MY = -2.6, 0.2
K.rbox("riser", (1.12, 0.72, 0.04), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(MX, MY, PZ + 0.02))
MA = P.machine("model", (MX, MY, PZ + 0.04), w=1.0, d=0.6, h=0.8)
K.glow_keys(MA["led"], [(0, 0.3)])
K.glow_keys(MA["tower"]["idle"], [(0, 0.4)])
K.key(MA["inner"].data, "energy", [(0, 6.0)])
SLOT = Vector((MX + 0.56, MY, PZ + 0.04 + 0.105))
# the rig: four posts and a top frame, with seven control modules on the front beam
RZ = PZ + 1.12
for sx in (-1, 1):
    for sy in (-1, 1):
        K.rbox(f"rig_post{sx}{sy}", (0.03, 0.03, RZ - PZ), bevel=0.006, seg=3, mat=K.M("alu"), loc=(MX + sx * 0.62, MY + sy * 0.42, PZ + (RZ - PZ) / 2))
for nm, sz, lc in (("rig_bf", (1.28, 0.05, 0.05), (MX, MY - 0.42, RZ)), ("rig_bb", (1.28, 0.03, 0.03), (MX, MY + 0.42, RZ)),
                   ("rig_bl", (0.03, 0.87, 0.03), (MX - 0.62, MY, RZ)), ("rig_br", (0.03, 0.87, 0.03), (MX + 0.62, MY, RZ))):
    K.rbox(nm, sz, bevel=0.008, seg=3, mat=K.M("alu"), loc=lc)
MODS = []
for k in range(7):
    x = MX - 0.48 + k * 0.16
    K.rbox(f"mod{k}", (0.13, 0.1, 0.075), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(x, MY - 0.43, RZ + 0.065))
    m = K.glow_mat(f"mod{k}_led", K.SKY, 0.25)
    K.rbox(f"mod{k}_ledbar", (0.08, 0.006, 0.012), bevel=0.003, seg=1, mat=m, loc=(x, MY - 0.484, RZ + 0.065))
    K.empty(f"mod{k}_pin", (x, MY - 0.49, RZ + 0.11))
    MODS.append(m)

# Claude's harness: a sealed housing (we cannot see or set what runs inside it)
CX0, CY0 = 2.45, -1.05
shell = K.anod("claude_shell", (0.035, 0.037, 0.045, 1), rough=0.35)
K.rbox("claude_base", (1.2, 0.78, 0.04), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(CX0, CY0, PZ + 0.02))
K.rbox("claude_box", (1.12, 0.7, 1.02), bevel=0.03, seg=5, mat=shell, loc=(CX0, CY0, PZ + 0.04 + 0.51))
K.rbox("claude_seam", (1.125, 0.705, 0.006), bevel=0.002, seg=1, mat=K.M("shadowgap"), loc=(CX0, CY0, PZ + 0.04 + 0.78))
CLED = K.glow_mat("claude_led", K.lin("#d97757"), 0.3)
K.rbox("claude_ledbar", (0.5, 0.006, 0.01), bevel=0.003, seg=1, mat=CLED, loc=(CX0, CY0 - 0.354, PZ + 0.12))
K.rbox("claude_slotbez", (0.012, 0.3, 0.12), bevel=0.004, seg=3, mat=K.M("alu"), loc=(CX0 - 0.562, CY0, PZ + 0.145), parent=None)
K.empty("claude_top", (CX0, CY0 - 0.35, PZ + 1.12))
K.empty("rig_top", (MX, MY - 0.45, RZ + 0.16))

# ------------------------------------------------------------------------------------------------ the toolbox rack (16 tools)
NAMES = OURS["tools_exposed"]
RY = 0.62
TIERZ = [PZ + 0.03, PZ + 0.36]
K.rbox("rack_base", (3.55, 0.46, 0.03), bevel=0.008, seg=3, mat=K.M("alu_dark"), loc=(0.0, RY, PZ + 0.015))
K.rbox("rack_shelf", (3.55, 0.46, 0.025), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(0.0, RY, TIERZ[1] - 0.0125))
for sx in (-1, 1):
    for sy in (-1, 1):
        K.rbox(f"rack_post{sx}{sy}", (0.03, 0.03, 0.62), bevel=0.006, seg=3, mat=K.M("alu"), loc=(sx * 1.79, RY + sy * 0.22, PZ + 0.31))
K.rbox("rack_top", (3.62, 0.48, 0.03), bevel=0.008, seg=3, mat=K.M("alu"), loc=(0.0, RY, PZ + 0.63))
TOOLS = {}
for i, nm in enumerate(NAMES):
    tier, col = divmod(i, 8)
    x = -1.47 + col * 0.42
    u = P.small_tool(f"tb{i}", (x, RY, TIERZ[tier]), DATA["toolbox"][nm], s=0.3)
    K.glow_keys(u["led"], [(0, 0.3)])
    K.glow_keys(u["ring"], [(0, 0.5)])
    K.glow_keys(u["bars"], [(0, 0.5)])
    K.empty(f"tb{i}_front", (x, RY - 0.12, TIERZ[tier] + 0.06))
    TOOLS[nm] = {"u": u, "front": Vector((x, RY - 0.13, TIERZ[tier] + 0.06)), "i": i}
f_sixteen = w("b1", "sixteen")
for nm, t in TOOLS.items():
    f0 = f_sixteen + t["i"] * 2
    K.glow_keys(t["u"]["led"], [(f0, 0.3), (f0 + 4, 2.4), (f0 + 30, 0.5)])

# ------------------------------------------------------------------------------------------------ calls, tiles and capsules
OY, CYS = -0.42, -1.02     # our strip, Claude's strip
TX0, TDX = -1.95, 0.34
K.plinth("strip_ours", TX0 - 0.25, TX0 + 13 * TDX + 0.25, y=OY, depth=0.38, height=PZ + 0.035)
K.plinth("strip_claude", TX0 - 0.25, TX0 + 10 * TDX + 0.25, y=CYS, depth=0.38, height=PZ + 0.035)
TZ = PZ + 0.035
_cap = [0]


def fly(nm, f0, dur=22, color=K.SKY, src=None, bounce=False):
    """A capsule from the model to tool `nm`; the tool lights when it arrives (ember and a bounce if refused)."""
    t = TOOLS[nm]
    k = _cap[0]
    _cap[0] += 1
    a = Vector(src or SLOT)
    b = t["front"]
    mid = (a + b) / 2 + Vector((0, -0.15, 0.45))
    r, m = P.capsule(f"cap{k}", tuple(a), color=color, size=(0.12, 0.055, 0.045))
    K.show(r, [(0, False), (f0 - 1, True), (f0 + dur + (16 if bounce else 2), False)])
    K.key(r, "location", [(0, a)])
    P.travel(r, P.cubic(a, a + Vector((0.25, -0.1, 0.3)), mid + Vector((0, 0, 0.1)), b, n=16), f0, f0 + dur)
    if bounce:
        P.travel(r, [b, b + Vector((0, -0.22, -0.02))], f0 + dur + 1, f0 + dur + 14)
    fa = f0 + dur
    u = t["u"]
    if bounce:
        ring_no = K.light_mat(f"tb{t['i']}_ringno_{k}", K.EMBER, 0.0)
        K.rbox(f"tb{t['i']}_rno_{k}", (0.012, 0.31, 0.21), bevel=0.004, seg=2, mat=ring_no, loc=(-0.6 - 0.008, 0.0, 0.035 + 0.11), parent=u["root"])
        K.glow_keys(ring_no, [(0, 0.0), (fa - 2, 0.0), (fa + 2, 6.0), (fa + 70, 4.0), (fa + 110, 0.0)])
    else:
        K.glow_keys(u["led"], [(fa - 3, 0.5), (fa + 1, 4.0), (fa + 50, 1.0)])
        K.glow_keys(u["ring"], [(fa - 3, 0.5), (fa + 1, 4.0), (fa + 50, 0.8)])
        K.glow_keys(u["bars"], [(fa - 3, 0.5), (fa + 2, 3.0), (fa + 50, 0.9)])
    return fa


def tile(name, slot, y, f0, color, role="template"):
    root, fm = S7.drop_tile(name, role, (TX0 + slot * TDX, y, TZ), f0, dur=12, height=0.4, face_color=color, face_peak=3.2,
                            face_rest=1.2, end=END)
    return root, fm


GREY = K.lin("#8a97ab")
EMMA = K.lin("#bcd6ff")
# our harness: per call (tool, launch word, status colour)
ours = [("find_item", w("b2", "three"), K.GREEN), ("find_supplier", w("b2", "three") + 3, K.GREEN), ("check_budget", w("b2", "three") + 6, K.GREEN),
        ("check_budget", w("b3", "budget") - 18, K.GREEN), ("search_policy", w("b3", "budget") - 15, K.GREEN),
        ("search_policy", w("b3", "second") - 10, GREY), ("check_stock", w("b3", "stock") - 20, K.GREEN),
        ("create_purchase_request", w("b4", "previews") - 12, K.EMBER), ("supplier_certificates", w("b4", "checks") - 16, K.GREEN),
        ("create_purchase_request", w("b5", "second") - 12, K.GREEN), ("create_purchase_request", w("b5", "go") - 14, K.SKY)]
assert [o[0] for o in ours] == OURS["summary"]["sequence"]
turn_marks = {9: w("b5", "says"), 10: w("b5", "yes") - 6}      # Emma's turns 2 and 3 land before calls 10 and 11
slot = 0
tile("t_emma1", slot, OY, blk["b1"]["f0"] + 14, EMMA, role="user")
slot += 1
OUR_SLOTS = []
for i, (nm, f0, colr) in enumerate(ours):
    if i in turn_marks:
        tile(f"t_emma{i}", slot, OY, turn_marks[i], EMMA, role="user")
        slot += 1
    fa = fly(nm, f0)
    tile(f"t_o{i}", slot, OY, fa + 4, colr)
    OUR_SLOTS.append(slot)
    slot += 1
# the guessed date: the ember tile pulses on "made up"
K.glow_keys(bpy.data.materials[f"t_o7_face"], [(w("b4", "made") - 2, 1.2), (w("b4", "made") + 4, 6.0), (w("b4", "nothing") + 10, 2.0)])
# the model 'thinks' before each round of calls
for f0 in (w("b2", "three") - 20, w("b3", "budget") - 34, w("b3", "second") - 26, w("b3", "stock") - 34, w("b4", "previews") - 28,
           w("b4", "checks") - 30, w("b5", "second") - 28, w("b5", "go") - 30):
    K.glow_keys(MA["led"], [(f0 - 4, 0.3), (f0, 2.4), (f0 + 18, 2.4), (f0 + 26, 0.3)])
    K.glow_keys(MA["tower"]["idle"], [(f0 - 4, 0.4), (f0, 2.6), (f0 + 18, 2.6), (f0 + 28, 0.4)])

# the flashback (an earlier run): a direct order refused at create_purchase_order, then the purchase request
fly("create_purchase_order", w("b6", "direct") - 10, dur=24, color=K.EMBER, bounce=True)
fly("create_purchase_request", w("b6", "raise") - 4, dur=22)

# Claude's harness: its own strip, its own order (claude_harness.json runs.order_hands)
csq = CL["tool_sequence"]
c_turn_before = {0: w("b7", "claude"), 4: w("b7", "orders") - 4, 7: w("b7", "same") - 10}
c_f = [w("b7", "m") - 6, w("b7", "m"), w("b7", "server") + 4, w("b7", "server") + 10, w("b7", "itself") - 4, w("b7", "eight") - 8,
       w("b7", "eight") - 2, w("b7", "request") - 8]
cslot = 0
CSRC = Vector((CX0 - 0.58, CY0, PZ + 0.145))
for i, nm in enumerate(csq):
    if i in c_turn_before:
        tile(f"c_emma{i}", cslot, CYS, c_turn_before[i], EMMA, role="user")
        cslot += 1
    fa = fly(nm, c_f[i], dur=16, color=K.lin("#d97757"), src=CSRC)
    tile(f"t_c{i}", cslot, CYS, fa + 3, K.SKY if i == len(csq) - 1 else K.GREEN)
    cslot += 1
K.glow_keys(CLED, [(0, 0.3), (w("b7", "claude") - 6, 0.3), (w("b7", "claude"), 3.0), (blk["b7"]["f1"], 1.5),
                   (w("b8", "anthropic's") - 4, 1.5), (w("b8", "anthropic's") + 4, 5.0), (w("b8", "in", 1) - 6, 1.2)])
# the rig's modules light as they are named
for m, word in zip(MODS, ("model", "prompt", "tools", "battery-safety", "fourteen-round", "log", "token")):
    nth = 1 if word == "model" else 0
    f0 = w("b8", word, nth)
    K.glow_keys(m, [(0, 0.25), (f0 - 3, 0.25), (f0 + 2, 4.5), (f0 + 60, 2.0), (END, 2.0)])

for nm in ("claude_base", "claude_box", "claude_seam", "claude_ledbar", "claude_slotbez", "strip_claude"):
    K.show(bpy.data.objects[nm], [(0, False), (blk["b7"]["f0"] - 14, True)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_open", lens=30, fstop=4.5).cut(0)
c1.keys([(0, (-3.6, -3.2, 1.7), (-1.2, 0.35, 0.5)),
         (w("b1", "sixteen") - 10, (-2.9, -3.0, 1.55), (-0.6, 0.45, 0.42)),
         (blk["b1"]["f1"] + 20, (-2.5, -2.9, 1.5), (-0.5, 0.35, 0.4))])
c2 = K.Cam(sc, "c_calls", lens=30, fstop=5.0).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (-2.2, -2.9, 1.55), (-0.6, 0.15, 0.38)),
         (blk["b3"]["f0"], (-1.7, -2.95, 1.55), (-0.2, 0.1, 0.36)),
         (blk["b4"]["f0"], (-1.3, -2.95, 1.55), (0.2, 0.05, 0.36)),
         (blk["b5"]["f0"], (-0.9, -2.95, 1.55), (0.5, 0.0, 0.36)),
         (blk["b5"]["f1"] + 20, (-0.6, -3.0, 1.6), (0.8, 0.0, 0.36))])
c3 = K.Cam(sc, "c_flash", lens=40, fstop=3.5).cut(blk["b6"]["f0"] - 10)
c3.keys([(blk["b6"]["f0"] - 10, (-2.15, -1.25, 1.0), (-1.25, RY, TIERZ[1] + 0.05)),
         (w("b6", "raise") - 20, (-1.95, -1.3, 0.9), (-0.9, RY, TIERZ[0] + 0.2)),
         (blk["b6"]["f1"] + 20, (-1.75, -1.35, 0.85), (-0.7, RY, TIERZ[0] + 0.15))])
c4 = K.Cam(sc, "c_both", lens=30, fstop=5.6).cut(blk["b7"]["f0"] - 10)
c4.keys([(blk["b7"]["f0"] - 10, (-0.3, -4.1, 2.4), (-0.2, -0.65, 0.2)),
         (blk["b7"]["f1"] + 20, (0.1, -4.0, 2.3), (0.1, -0.7, 0.2))])
c5a = K.Cam(sc, "c_claude", lens=34, fstop=4.5).cut(blk["b8"]["f0"] - 10)
c5a.keys([(blk["b8"]["f0"] - 10, (0.9, -3.3, 1.35), (2.1, -0.95, 0.55)),
          (w("b8", "in", 1) - 6, (1.2, -3.1, 1.35), (2.3, -0.95, 0.6))])
c5 = K.Cam(sc, "c_rig", lens=32, fstop=4.5).cut(w("b8", "in", 1) - 6)
c5.keys([(w("b8", "in", 1) - 6, (-1.2, -2.8, 1.7), (-2.5, -0.05, 0.9)),
         (blk["b8"]["f1"] + 20, (-1.45, -2.5, 1.85), (-2.6, 0.05, 1.0))])
c6 = K.Cam(sc, "c_close", lens=28, fstop=6.0).cut(blk["b9"]["f0"] - 10)
c6.keys([(blk["b9"]["f0"] - 10, (-0.9, -4.3, 2.3), (-0.6, -0.2, 0.4)),
         (END, (0.2, -4.9, 2.7), (-0.4, -0.2, 0.4))])

pins = ["model_pin_top", "rig_top", "claude_top"] + [f"mod{k}_pin" for k in range(7)] + [f"tb{i}_front" for i in range(len(NAMES))]
pins += [f"t_o{i}_top" for i in range(len(ours))] + [f"t_o{i}_front" for i in range(len(ours))]
pins += [f"t_c{i}_top" for i in range(len(csq))] + [f"t_c{i}_front" for i in range(len(csq))]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
