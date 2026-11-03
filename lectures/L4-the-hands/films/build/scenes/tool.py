"""Film 1, "Inside a tool": Emma's real check_stock call, followed through the tool. Builds tool.blend.

The model (the sealed L2 machine) writes a request capsule; it slides along a rail to the tool's intake gate
(tool.json); the gate scans it and lets it in; a second capsule (the number 500) is refused at the gate and nothing
reaches Ledgerline; the lid lifts off (exploded view): the core's 26 light bars are the 26 real lines of tool.py;
pulses run up four conduits to three 1998 Ledgerline cabinets (itm_get, whs_list, stk_query x2); four enamel
envelopes come back and stack inside; they fold into one green result slab that slides out and returns to the model;
the error path (BAT-5000 -> ERR-ITM-0010) comes back as an ember slab; the three parts light in turn and the other
15 tools of the toolbox appear down the bench.

Numbers: experiments/logs/anatomy_check_stock.json (shown in 2D by specs/tool.py). Timing: timeline/tool.json.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402

FILM = "tool"
B = K.Beats(FILM)
DATA = K.load("films/build/data/l4_data.json")
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11

sc = K.reset(B.frames)
K.studio(sc, focus=(-0.2, 0.3, 0.4), key_power=3000, span=0.0)
# extra soft keys so the long set (machine on the left, toolbox row on the right) stays evenly lit
K.soft_light("keyR", (3.5, -6.0, 7.5), (3.0, 0.3, 0.3), 1800, 12.0, (1.0, 0.97, 0.93))
K.soft_light("rimR", (4.0, 7.0, 3.2), (3.0, 0.3, 0.3), 1200, 14.0, (0.7, 0.82, 1.0))
K.plinth("bench", -2.75, 8.2, y=-0.12, depth=1.3, height=PZ)

# ------------------------------------------------------------------------------------------------ the model
MX = -2.05
K.rbox("riser", (1.12, 0.72, 0.04), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(MX, 0.0, PZ + 0.02))
MZ = PZ + 0.04
MA = P.machine("model", (MX, 0.0, MZ), w=1.0, d=0.6, h=0.8)
LANE = MZ + 0.105          # the machine's slot height = the tool's lane height
TOOL = P.tool_unit("tool", (0.0, 0.0, LANE - 0.145), DATA["check_stock_lines"])
ZC = LANE
K.rbox("toolriser", (1.3, 0.74, LANE - 0.145 - PZ), bevel=0.006, seg=2, mat=K.M("alu_dark"),
       loc=(0.0, 0.0, PZ + (LANE - 0.145 - PZ) / 2)) if LANE - 0.145 - PZ > 0.002 else None
SLOT_R = MX + 0.5 + 0.02
GATE_X = -0.6 - 0.035
P.rail("lane", SLOT_R + 0.02, GATE_X - 0.08, 0.0, ZC)
P.rail("back", -1.38, 0.98, -0.52, ZC)

# model glow while it is "thinking" (writing a request or reading a result)
def think(f0, f1, peak=2.2):
    K.glow_keys(MA["led"], [(f0 - 6, 0.3), (f0, peak), (f1, peak), (f1 + 10, 0.3)])
    K.glow_keys(MA["tower"]["idle"], [(f0 - 8, 0.4), (f0, 2.6), (f1, 2.6), (f1 + 12, 0.4)])


K.glow_keys(MA["led"], [(0, 0.3)])
K.glow_keys(MA["tower"]["idle"], [(0, 0.4)])
K.key(MA["inner"].data, "energy", [(0, 6.0)])

# ------------------------------------------------------------------------------------------------ Ledgerline (1998)
CY = 1.38
CABS = {"itm": -0.72, "whs": 0.0, "stk": 0.72}
cab = {k: P.cabinet(f"cab_{k}", (x, CY, 0.0)) for k, x in CABS.items()}
# a low enamel base tying the three together, and a dark cable tray
K.rbox("cab_base", (2.15, 0.6, 0.03), bevel=0.008, seg=3, mat=K.M("graphite"), loc=(0, CY, 0.015))
for k, c in cab.items():
    K.glow_keys(c["lamp"], [(0, 0.3)])

# conduits: tool back port j -> cabinet port
PORT_Y = 0.31 + 0.04
PORT_Z = (LANE - 0.145) + 0.035 + 0.3 * 0.62
PX = [-0.36, -0.12, 0.12, 0.36]
TARGET = ["itm", "whs", "stk", "stk"]
CAB_FRONT = CY - 0.23 - 0.004 - 0.03
paths = []
for j in range(4):
    cx = CABS[TARGET[j]] + (0.0 if j < 3 else 0.0)
    a = Vector((PX[j], PORT_Y, PORT_Z))
    d = Vector((cx + (-0.02 if j == 2 else 0.02 if j == 3 else 0.0), CAB_FRONT, cab[TARGET[j]]["port_z"] + (0.015 if j == 2 else -0.015 if j == 3 else 0.0)))
    pts = P.cubic(a, a + Vector((0, 0.32, 0.02)), d + Vector((0, -0.3, 0.0)), d, n=40)
    tube, strand, sm = P.conduit(f"cond{j}", pts, r=0.014)
    paths.append(pts)
    globals()[f"strand{j}"] = (strand, sm)


def pulse(j, f0, dur=16):
    """A light pulse runs from the core's code line through the inner tube to port j, then up conduit j to the cabinet."""
    _, ist, ism = TOOL["inner_tubes"][j]
    K.grow(ist, [(0, 0.0), (f0 - 8, 0.0), (f0, 1.0)])
    K.glow_keys(ism, [(0, 0.0), (f0 - 8, 0.0), (f0 - 6, 4.0), (f0 + 40, 2.0), (f0 + 80, 0.6)])
    strand, sm = globals()[f"strand{j}"]
    K.grow(strand, [(0, 0.0), (f0, 0.0), (f0 + dur, 1.0)])
    K.glow_keys(sm, [(0, 0.0), (f0, 0.0), (f0 + 2, 4.0), (f0 + dur + 10, 3.0), (f0 + dur + 40, 0.6)])
    K.glow_keys(TOOL["ports"][j], [(0, 0.0), (f0 - 4, 0.0), (f0, 3.0), (f0 + 40, 0.8)])


# ------------------------------------------------------------------------------------------------ beats
f_req = w("b1", "writes")
f_meet = w("b3", "meets")
f_schema = w("b3", "schema")
f_pass = w("b3", "passes")
f_what = w("b3", "what")
f_refuse = w("b3", "refuses")
f_zero = w("b3", "zero")
f_behind = w("b4", "behind")
f_26 = w("b4", "twenty-six")
f_item = w("b4", "item")
f_whs = w("b4", "warehouse")
f_man = w("b4", "manchester")
f_lds = w("b4", "leeds")
f_env = w("b5", "envelopes")
f_turns = w("b6", "turns")
f_result = w("b6", "result")
f_only = w("b6", "only")
f_model6 = w("b6", "model")
f_ask = w("b7", "ask")
f_itm7 = w("b7", "item")
f_E = w("b7", "e")
f_turns7 = w("b7", "turns")
f_false = w("b7", "false")
f_three = w("b8", "three")
f_contract = w("b8", "contract")
f_code = w("b8", "code")
f_clean = w("b8", "clean")
f_open = w("b8", "open")

OUT_SLOT = Vector((SLOT_R + 0.06, 0.0, ZC))
GATE_FRONT = Vector((GATE_X - 0.16, 0.0, ZC))
INSIDE = Vector((-0.4, -0.02, ZC))
CORE_TOP = Vector((-0.08, -0.02, (LANE - 0.145) + 0.06 + 0.08))

# capsule 1: the real request (BAT-500)
cap1, cap1m = P.capsule("cap1", tuple(OUT_SLOT - Vector((0.2, 0, 0))))
K.show(cap1, [(0, False), (f_req - 6, True), (f_pass + 70, False)])
K.key(cap1, "location", [(0, OUT_SLOT - Vector((0.2, 0, 0))), (f_req - 6, OUT_SLOT - Vector((0.2, 0, 0))),
                         (f_req + 24, OUT_SLOT + Vector((0.2, 0, 0)))])
P.travel(cap1, [OUT_SLOT + Vector((0.2, 0, 0)), GATE_FRONT], f_meet - 40, f_meet + 4)
P.travel(cap1, [GATE_FRONT, GATE_FRONT + Vector((0.32, 0, 0)), INSIDE, CORE_TOP + Vector((0, 0, 0.04))], f_pass - 6, f_pass + 40)
K.key(cap1, "scale", [(0, (1, 1, 1)), (f_pass + 40, (1, 1, 1)), (f_pass + 64, (0.2, 0.2, 0.2))])
K.glow_keys(cap1m, [(0, 2.0), (f_pass + 40, 2.0), (f_pass + 64, 8.0)])
think(f_req - 30, f_req + 10)

# the gate scans: pass (green), then the refusal (ember) with the shutter
def scan(f0, dur=16):
    s = TOOL["scan"]
    z0 = s.location.z
    K.key(s, "location", [(0, Vector((s.location.x, 0, z0))), (f0, Vector((s.location.x, 0, z0))),
                          (f0 + dur, Vector((s.location.x, 0, z0 + 0.19))), (f0 + dur + 1, Vector((s.location.x, 0, z0)))])
    K.glow_keys(TOOL["scan_m"], [(f0 - 1, 0.0), (f0, 5.0), (f0 + dur, 5.0), (f0 + dur + 1, 0.0)])


K.glow_keys(TOOL["scan_m"], [(0, 0.0)])
scan(f_schema - 8)
scan(f_pass - 22)
K.glow_keys(TOOL["ring_ok"], [(0, 0.0), (f_pass - 6, 0.0), (f_pass, 4.0), (f_pass + 50, 4.0), (f_pass + 80, 0.0)])
K.glow_keys(TOOL["ring_idle"], [(0, 0.6), (f_pass - 6, 0.6), (f_pass, 0.0), (f_pass + 80, 0.0), (f_pass + 100, 0.6),
                                (f_refuse - 8, 0.6), (f_refuse, 0.0), (f_behind + 20, 0.0), (f_behind + 40, 0.6)])

cap2, cap2m = P.capsule("cap2", tuple(OUT_SLOT - Vector((0.2, 0, 0))), color=K.EMBER)
K.show(cap2, [(0, False), (f_what - 4, True), (f_behind + 10, False)])
K.key(cap2, "location", [(0, OUT_SLOT - Vector((0.2, 0, 0))), (f_what - 4, OUT_SLOT - Vector((0.2, 0, 0)))])
P.travel(cap2, [OUT_SLOT - Vector((0.2, 0, 0)), OUT_SLOT + Vector((0.2, 0, 0)), GATE_FRONT], f_what, f_refuse - 4)
P.travel(cap2, [GATE_FRONT, GATE_FRONT - Vector((0.1, 0, 0))], f_refuse + 2, f_refuse + 16)
scan(f_refuse - 14, dur=12)
K.glow_keys(TOOL["ring_no"], [(0, 0.0), (f_refuse - 3, 0.0), (f_refuse + 1, 5.0), (f_zero + 40, 4.0), (f_behind + 10, 0.0)])
sh = TOOL["shutter"]
K.key(sh, "location", [(0, TOOL["shutter_up"]), (f_refuse - 3, TOOL["shutter_up"]), (f_refuse + 5, TOOL["shutter_down"]),
                       (f_behind - 4, TOOL["shutter_down"]), (f_behind + 14, TOOL["shutter_up"])])
think(f_what - 20, f_what + 4)

# the lid lifts off (exploded view); the inner light comes up; the code bars light in reading order
lid = TOOL["lid"]
L0 = Vector(lid.location)
K.key(lid, "location", [(0, L0), (f_behind, L0), (f_behind + 36, L0 + Vector((0, 0.05, 0.5))), (f_behind + 90, L0 + Vector((0, 0.3, 2.6)))])
K.key(lid, "rotation_euler", [(0, (0, 0, 0)), (f_behind, (0, 0, 0)), (f_behind + 36, (math.radians(-12), 0, 0)), (f_behind + 90, (math.radians(-30), 0, 0))])
K.show(lid, [(0, True), (f_behind + 92, False)])
K.glow_keys(TOOL["chan"], [(0, 0.0), (f_pass - 2, 0.0), (f_pass + 4, 4.0), (f_pass + 40, 0.5)])
K.key(TOOL["inner"].data, "energy", [(0, 0.0), (f_behind, 0.0), (f_behind + 30, 18.0)])
bars = [b for b in TOOL["bars"]]
for i, m in enumerate(bars):
    if m is None:
        continue
    t0 = f_26 - 6 + i * 2
    K.glow_keys(m, [(0, 0.0), (t0, 0.0), (t0 + 4, 3.2), (t0 + 30, 1.2)])
# the service calls light their lines (the _ledgerline lines of tool.py: 1-based lines 8, 10, 12) at their words
LINE_OF = {0: 8, 1: 10, 2: 12, 3: 12}   # 0-based lines of tool.py: itm_get, whs_list, stk_query (x2)
for j, f0 in enumerate((f_item, f_whs, f_man, f_lds)):
    pulse(j, f0)
    m = bars[LINE_OF[j]]
    if m is not None:
        K.glow_keys(m, [(f0 - 3, 1.2), (f0 + 1, 5.0), (f0 + 30, 1.4)])
    c = cab[TARGET[j]]
    K.glow_keys(c["ok"], [(f0 + 12, 0.0), (f0 + 17, 4.0), (f0 + 40, 1.2)])
K.glow_keys(cab["itm"]["ok"], [(0, 0.0)])
K.glow_keys(cab["whs"]["ok"], [(0, 0.0)])
K.glow_keys(cab["stk"]["ok"], [(0, 0.0)])

# four envelopes come back, one per call, and land in the tray inside the tool
ENV = []
TRAY = TOOL["tray_world"]
for j in range(4):
    e, em = P.envelope(f"env{j}", tuple(paths[j][-1]))
    rev = list(reversed(paths[j])) + [Vector((PX[j], PORT_Y - 0.09, PORT_Z)), TRAY + Vector((0, 0, 0.2 + 0.03 * j)),
                                       TRAY + Vector((0, 0, 0.026 * j))]
    f0 = blk["b5"]["f0"] - 14 + j * 26
    K.show(e, [(0, False), (f0 - 1, True), (f_turns + 40, False)])
    K.key(e, "location", [(0, rev[0])])
    P.travel(e, rev, f0, f0 + 84)
    K.key(e, "scale", [(0, (1, 1, 1)), (f_turns + 8, (1, 1, 1)), (f_turns + 36, (0.3, 0.3, 0.3))])
    K.glow_keys(em, [(0, 1.6), (f_turns, 1.6), (f_turns + 20, 6.0)])
    ENV.append((e, em))
    K.glow_keys(cab[TARGET[j]]["lamp"], [(f0 - 6, 0.25), (f0 - 2, 3.0), (f0 + 20, 0.4)])

# the clean result: a green slab out of the output slot, then back along the front rail to the model
OUT = Vector((0.6 + 0.08, 0.0, ZC))
res, res_m, res_in = P.result_slab("res", tuple(OUT - Vector((0.2, 0, 0))))
K.show(res, [(0, False), (f_result - 10, True), (f_ask, False)])
K.key(res, "location", [(0, OUT - Vector((0.24, 0, 0))), (f_result - 10, OUT - Vector((0.24, 0, 0)))])
P.travel(res, [OUT - Vector((0.24, 0, 0)), OUT + Vector((0.2, 0, 0))], f_result - 8, f_result + 22)
BACK = [OUT + Vector((0.2, 0, 0)), Vector((0.98, -0.18, ZC)), Vector((0.98, -0.52, ZC)), Vector((-1.38, -0.52, ZC)),
        Vector((-1.38, -0.16, ZC)), OUT_SLOT + Vector((0.02, 0, 0)), OUT_SLOT - Vector((0.24, 0, 0))]
P.travel(res, BACK, f_only - 4, f_model6 + 34)
K.glow_keys(TOOL["out"], [(0, 0.0), (f_result - 12, 0.0), (f_result - 4, 4.0), (f_result + 40, 0.6)])
K.glow_keys(TOOL["out_chan"], [(0, 0.0), (f_result - 16, 0.0), (f_result - 10, 4.0), (f_result + 40, 0.5)])
# rails for the result's way back: the output shelf, a turn to the front rail, and a turn back to the model's slot
P.rail("outshelf", 0.62, 1.05, 0.0, ZC)
rt = P.rail("turnR", -0.53, 0.0, 0.0, ZC)
rt.location = (0.98, -0.26, ZC)
rt.rotation_euler = (0, 0, math.pi / 2)
rl = P.rail("turnL", -0.52, -0.06, 0.0, ZC)
rl.location = (-1.38, -0.29, ZC)
rl.rotation_euler = (0, 0, math.pi / 2)
for i, m in enumerate(bars):
    if m is not None:
        K.glow_keys(m, [(f_turns + 10, 1.2), (f_turns + 18, 4.0), (f_turns + 40, 1.2)])
think(f_model6 + 20, f_model6 + 60)

# the error path: BAT-5000 passes the gate (it is a string), itm_get answers ERR-ITM-0010, an ember slab comes out
cap3, cap3m = P.capsule("cap3", tuple(OUT_SLOT - Vector((0.2, 0, 0))))
K.show(cap3, [(0, False), (f_ask - 4, True), (f_itm7 + 6, False)])
K.key(cap3, "location", [(0, OUT_SLOT - Vector((0.2, 0, 0))), (f_ask - 4, OUT_SLOT - Vector((0.2, 0, 0)))])
P.travel(cap3, [OUT_SLOT - Vector((0.2, 0, 0)), OUT_SLOT + Vector((0.2, 0, 0)), GATE_FRONT, GATE_FRONT + Vector((0.32, 0, 0)),
                INSIDE, CORE_TOP + Vector((0, 0, 0.04))], f_ask, f_itm7 - 4)
K.key(cap3, "scale", [(0, (1, 1, 1)), (f_itm7 - 16, (1, 1, 1)), (f_itm7 + 4, (0.2, 0.2, 0.2))])
scan(f_ask + 34, dur=10)
K.glow_keys(TOOL["ring_ok"], [(f_ask + 34, 0.0), (f_ask + 40, 4.0), (f_ask + 70, 0.0)])
think(f_ask - 24, f_ask)
# the call goes up conduit 0 again; the reply comes back down it in ember (a second strand, ember light)
st0, sm0 = globals()["strand0"]
K.glow_keys(sm0, [(f_itm7 - 2, 0.6), (f_itm7 + 2, 5.0), (f_itm7 + 30, 0.6)])
K.glow_keys(TOOL["ports"][0], [(f_itm7 - 2, 0.8), (f_itm7 + 2, 4.0), (f_itm7 + 40, 0.8)])
_, est, esm = P.conduit("cond0_err", list(reversed(paths[0])), r=0.0155)
_.hide_render = True
esm.node_tree.nodes["Emission"].inputs["Color"].default_value = K.EMBER
K.grow(est, [(0, 0.0), (f_E - 6, 0.0), (f_E + 14, 1.0)])
K.glow_keys(esm, [(0, 0.0), (f_E - 6, 0.0), (f_E - 4, 5.0), (f_false + 10, 3.0), (f_false + 40, 0.0)])
K.glow_keys(cab["itm"]["fault"], [(0, 0.0), (f_E - 10, 0.0), (f_E - 4, 8.0), (f_E + 10, 3.0), (f_E + 22, 8.0), (f_E + 36, 3.0),
                                  (f_E + 50, 8.0), (f_false + 30, 4.0), (f_false + 60, 0.0)])
K.glow_keys(cab["itm"]["lamp"], [(f_E - 10, 0.25), (f_E - 4, 0.05), (f_false + 50, 0.25)])
e4, e4m = P.envelope("env_err", tuple(paths[0][-1]))
K.glow_keys(e4m, [(0, 4.0)])
rev = list(reversed(paths[0])) + [Vector((PX[0], PORT_Y - 0.09, PORT_Z)), TRAY + Vector((0, 0, 0.2)), TRAY]
K.show(e4, [(0, False), (f_E - 4, True), (f_turns7 + 30, False)])
K.key(e4, "location", [(0, rev[0])])
P.travel(e4, rev, f_E - 4, f_E + 44)
K.key(e4, "scale", [(0, (1, 1, 1)), (f_turns7, (1, 1, 1)), (f_turns7 + 26, (0.3, 0.3, 0.3))])
err, err_m, err_in = P.result_slab("err", tuple(OUT - Vector((0.24, 0, 0))), color=K.EMBER)
K.show(err, [(0, False), (f_turns7 + 6, True)])
K.key(err, "location", [(0, OUT - Vector((0.24, 0, 0))), (f_turns7 + 6, OUT - Vector((0.24, 0, 0)))])
P.travel(err, [OUT - Vector((0.24, 0, 0)), OUT + Vector((0.2, 0, 0))], f_turns7 + 8, f_false + 6)
K.glow_keys(TOOL["out"], [(f_turns7, 0.6), (f_turns7 + 6, 4.0), (f_three, 0.6)])

# the close: the three parts light in turn; then the other 15 tools of the toolbox appear down the bench
K.glow_keys(TOOL["ring_idle"], [(f_contract - 6, 0.6), (f_contract, 5.0), (f_code, 1.0)])
for i, m in enumerate(bars):
    if m is not None:
        K.glow_keys(m, [(f_code - 4, 1.2), (f_code + 2 + i, 4.5), (f_clean, 1.4)])
K.glow_keys(TOOL["out"], [(f_clean - 6, 0.6), (f_clean, 5.0), (END, 2.0)])
others = [n for n in sorted(DATA["toolbox"]) if n != "check_stock"]
for k, nm in enumerate(others):
    x = 1.85 + k * 0.42
    u = P.small_tool(f"tb{k}", (x, 0.02, PZ), DATA["toolbox"][nm], s=0.3)
    f0 = f_open + k * 3
    K.show(u["root"], [(0, False), (f0 - 1, True)])
    K.key(u["root"], "location", [(0, Vector((x, 0.02, PZ + 0.3))), (f0, Vector((x, 0.02, PZ + 0.3))), (f0 + 16, Vector((x, 0.02, PZ)))])
    K.glow_keys(u["led"], [(0, 0.3), (f0 + 10, 0.3), (f0 + 18, 3.0), (f0 + 50, 1.0)])
    K.glow_keys(u["ring"], [(0, 0.6), (f0 + 10, 0.6), (f0 + 18, 3.0), (f0 + 50, 1.0)])
    K.glow_keys(u["bars"], [(0, 0.0), (f0 + 12, 0.0), (f0 + 22, 2.2), (END, 1.6)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_ask", lens=38, fstop=3.5).cut(0)
c1.keys([(0, (-3.25, -2.35, 1.2), (-2.45, 0.1, 0.5)),
         (w("b1", "model"), (-2.95, -2.2, 1.0), (-2.05, 0.05, 0.45)),
         (blk["b1"]["f1"] + 20, (-2.45, -1.75, 0.78), (-1.45, 0.0, ZC + 0.02))])
c2 = K.Cam(sc, "c_req", lens=55, fstop=2.4).cut(blk["b2"]["f0"] - 12)
c2.keys([(blk["b2"]["f0"] - 12, (-1.55, -0.95, 0.5), (-1.3, 0.0, ZC + 0.02)),
         (blk["b2"]["f1"] + 20, (-1.3, -0.8, 0.44), (-1.3, 0.0, ZC + 0.01))])
c3 = K.Cam(sc, "c_door", lens=42, fstop=2.8).cut(blk["b3"]["f0"] - 10)
c3.keys([(blk["b3"]["f0"] - 10, (-1.75, -0.95, 0.6), (-0.75, 0.05, 0.36)),
         (f_pass, (-1.62, -0.88, 0.56), (-0.55, 0.05, 0.36)),
         (f_what, (-1.7, -0.92, 0.58), (-0.62, 0.05, 0.36)),
         (blk["b3"]["f1"] + 18, (-1.58, -0.85, 0.55), (-0.55, 0.05, 0.36))])
c4 = K.Cam(sc, "c_inside", lens=34, fstop=4.0).cut(blk["b4"]["f0"] - 10)
c4.keys([(blk["b4"]["f0"] - 10, (-0.15, -1.55, 0.95), (-0.4, 0.05, 0.3)),
         (f_26, (0.42, -1.0, 1.42), (-0.62, 0.12, 0.1)),
         (f_item - 24, (0.5, -1.1, 1.5), (-0.55, 0.3, 0.16)),
         (blk["b4"]["f1"] + 20, (0.75, -1.35, 1.6), (-0.2, 0.8, 0.45))])
c5 = K.Cam(sc, "c_legacy", lens=34, fstop=4.0).cut(blk["b5"]["f0"] - 10)
c5.keys([(blk["b5"]["f0"] - 10, (2.35, 0.3, 1.0), (0.05, 0.72, 0.5)),
         (w("b5", "manchester"), (2.2, 0.45, 0.92), (0.15, 0.75, 0.48)),
         (blk["b5"]["f1"] + 20, (2.05, 0.15, 0.85), (0.1, 0.5, 0.4))])
c6 = K.Cam(sc, "c_result", lens=40, fstop=3.2).cut(blk["b6"]["f0"] - 10)
c6.keys([(blk["b6"]["f0"] - 10, (1.25, -1.45, 0.95), (0.25, 0.0, 0.25)),
         (f_result + 20, (1.65, -1.2, 0.72), (0.55, 0.0, ZC)),
         (f_only - 4, (1.5, -1.6, 0.8), (0.45, -0.3, ZC)),
         (blk["b6"]["f1"] + 22, (-0.45, -2.45, 0.95), (-1.45, -0.35, 0.32))])
c7 = K.Cam(sc, "c_error", lens=34, fstop=4.0).cut(blk["b7"]["f0"] - 10)
c7.keys([(blk["b7"]["f0"] - 10, (-2.1, -1.95, 1.3), (-0.75, 0.3, 0.42)),
         (f_itm7 - 10, (-1.75, -1.15, 1.3), (-0.45, 1.0, 0.7)),
         (f_turns7 - 14, (-1.6, -1.05, 1.25), (-0.4, 1.05, 0.7)),
         (f_turns7 + 4, (1.15, -1.55, 0.75), (0.95, 0.0, 0.3)),
         (blk["b7"]["f1"] + 18, (1.0, -1.35, 0.68), (0.95, 0.0, ZC))])
c8 = K.Cam(sc, "c_close", lens=32, fstop=5.6).cut(blk["b8"]["f0"] - 10)
c8.keys([(blk["b8"]["f0"] - 10, (-1.0, -2.35, 1.45), (0.05, 0.15, 0.3)),
         (f_open - 6, (-0.7, -2.45, 1.45), (0.25, 0.15, 0.3)),
         (f_open + 70, (2.0, -2.05, 0.95), (3.4, 0.15, 0.14)),
         (END, (3.9, -1.8, 0.78), (5.4, 0.15, 0.12))])

pins = ["model_pin_top", "model_pin_win", "model_pin_out", "cap1_top", "cap2_top", "cap3_top", "tool_gate", "tool_gate_top",
        "tool_core", "tool_out", "tool_top", "tool_lid_pin", "res_top", "err_top", "cab_itm_top", "cab_whs_top", "cab_stk_top",
        "cab_itm_face", "cab_whs_face", "cab_stk_face", "env0_top", "env2_top", "env_err_top"] + [f"tool_port{j}" for j in range(4)] + \
       ["tb7_top", "tb14_top"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
