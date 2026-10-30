"""The machine under Ask Northbridge, built as a row of believable studio props (metres).

x runs along the request's journey, the camera looks from -y.
  Emma's desk (-5.6) -> harness bench (-3.0) -> model (0) -> guard ring (1.65)
  -> tool rack (3.3) -> MCP plug + cable -> Ledgerline cabinet (6.1) -> printer (7.15) -> Daniel's desk (8.9)
Every station returns its handles (objects, keyable materials, anchors for 2D labels).
"""
import math
import random

from mathutils import Vector

import lib as L

R = random.Random(11)
H = {}          # handles
A = {}          # anchors (empties) for 2D labels: name -> object


def anchor(name, loc, parent=None):
    A[name] = L.empty("A_" + name, loc, parent)
    return A[name]


# ------------------------------------------------------------------ shared finishes
def finishes():
    M = {}
    M["alu"] = L.brushed("alu", (0.84, 0.85, 0.86, 1), 0.26)
    M["alu_dark"] = L.anodized("alu_dark", (0.06, 0.065, 0.075, 1), 0.34)
    M["graphite"] = L.anodized("graphite", (0.13, 0.14, 0.155, 1), 0.38)
    M["steel"] = L.principled("steel", (0.62, 0.63, 0.64, 1), rough=0.18, metallic=1.0)
    M["chrome"] = L.chrome()
    M["gold"] = L.gold()
    M["black"] = L.satin("black_satin", (0.018, 0.019, 0.022, 1), 0.35, 0.4)
    M["rubber"] = L.rubber()
    M["glass"] = L.glass("tube_glass", (0.96, 0.98, 1.0, 1), 0.03)
    M["smoke"] = L.principled("smoke", (0.55, 0.56, 0.58, 1), rough=0.05, transmission=1.0, ior=1.49)
    M["beige"] = L.powder("beige98", (0.62, 0.56, 0.45, 1), 0.5)
    M["beige_d"] = L.powder("beige98_d", (0.47, 0.42, 0.33, 1), 0.55)
    M["oak"] = L.wood("oak", (0.50, 0.32, 0.17, 1), (0.33, 0.19, 0.09, 1))
    M["walnut"] = L.wood("walnut", (0.22, 0.12, 0.06, 1), (0.12, 0.06, 0.03, 1), (1, 24, 1))
    M["ceramic_w"] = L.satin("ceramic_w", (0.86, 0.86, 0.85, 1), 0.25, 0.6)
    M["ceramic_b"] = L.satin("ceramic_b", (0.05, 0.22, 0.75, 1), 0.3, 0.5)
    M["white_pl"] = L.satin("white_plastic", (0.80, 0.81, 0.82, 1), 0.4, 0.2)
    M["sky_an"] = L.anodized("sky_anod", (0.05, 0.25, 0.9, 1), 0.32)
    M["green_an"] = L.anodized("green_anod", (0.03, 0.35, 0.16, 1), 0.34)
    M["ember_an"] = L.anodized("ember_anod", (0.6, 0.12, 0.03, 1), 0.34)
    M["sheet_body"] = L.satin("sheet_body", (0.9, 0.92, 0.95, 1), 0.3, 0.6)
    for k in ("sys", "msg", "tool", "result"):
        M["print_" + k] = L.textured("print_" + k, f"sheet_{k}.png", rough=0.35, coat=0.5)
    M["doc_pr"] = L.textured("doc_pr", "doc_pr.png", rough=0.7, coat=0.0)
    M["doc_po"] = L.textured("doc_po", "doc_po.png", rough=0.7, coat=0.0)
    M["greenbar"] = L.textured("greenbar", "greenbar.png", rough=0.8, coat=0.0)
    H["M"] = M
    return M


def screw(name, loc, parent, M, r=0.006, rot=(0, 0, 0)):
    s = L.cyl(name, r, 0.003, M["steel"], loc, rot, verts=24, parent=parent)
    L.box(name + "_hx", (r * 0.9, r * 0.25, 0.0012), M["black"], (0, 0, 0.0016), parent=s, bevel=0)
    return s


# ------------------------------------------------------------------ Emma's desk + chat display
def emma_desk(M, x=-5.6):
    root = L.empty("emma", (x, 0.15, 0))
    top = L.box("emma_top", (1.5, 0.78, 0.035), L.wood("ash", (0.72, 0.58, 0.42, 1), (0.6, 0.46, 0.32, 1)), (0, 0, 0.74), bevel=0.006, parent=root)
    for sx in (-0.68, 0.68):
        L.box("emma_leg", (0.05, 0.66, 0.72), M["alu_dark"], (sx, 0, 0.36), bevel=0.01, parent=root)
    # display
    disp = L.empty("display", (0.0, 0.12, 0.757), root)
    L.box("disp_base", (0.26, 0.2, 0.008), M["alu"], (0, 0.02, 0.004), bevel=0.003, parent=disp)
    L.box("disp_neck", (0.07, 0.025, 0.32), M["alu"], (0, 0.07, 0.17), (math.radians(-10), 0, 0), bevel=0.008, parent=disp)
    head = L.empty("disp_head", (0, 0.03, 0.43), disp)
    head.rotation_euler = (math.radians(-6), 0, 0)
    L.box("disp_back", (0.66, 0.022, 0.39), M["alu"], (0, 0.012, 0), bevel=0.01, parent=head)
    L.box("disp_bezel", (0.655, 0.006, 0.385), M["black"], (0, -0.002, 0), bevel=0.004, parent=head)
    scr = L.led("screen", (0.93, 0.95, 1.0, 1), body=(0.0, 0.0, 0.0, 1), strength=1.0)
    L.bsdf(scr).inputs["Roughness"].default_value = 0.08
    screen = L.box("disp_screen", (0.632, 0.002, 0.358), scr, (0, -0.0055, 0.004), bevel=0.0005, parent=head)
    H["screen_mat"] = scr
    # screen corners for the 2D chat UI (TL, TR, BR, BL as seen from the front)
    w, h = 0.632 / 2, 0.358 / 2
    for n, (cx, cz) in {"scr_tl": (-w, h), "scr_tr": (w, h), "scr_br": (w, -h), "scr_bl": (-w, -h)}.items():
        anchor(n, (cx, -0.0068, cz + 0.004), head)
    # keyboard
    kb = L.box("kb", (0.44, 0.13, 0.012), M["alu"], (0, -0.2, 0.763), bevel=0.004, parent=root)
    for i in range(14):
        for j in range(5):
            if j == 4 and 3 < i < 10:
                continue
            L.box("key", (0.0255, 0.0215, 0.004), M["white_pl"], (-0.2 + i * 0.0305, -0.045 + j * 0.0225, 0.007), bevel=0.0015, seg=2, parent=kb)
    L.box("space", (0.17, 0.0215, 0.004), M["white_pl"], (-0.0, -0.045 + 4 * 0.0225, 0.007), bevel=0.0015, seg=2, parent=kb)
    # mug, notebook, pen
    mug = L.cyl("mug", 0.042, 0.1, M["ceramic_b"], (0.5, -0.12, 0.807), verts=48, bevel=0.004, parent=root)
    L.torus("mug_handle", 0.03, 0.007, M["ceramic_b"], (0.045, 0, 0.0), (math.radians(90), 0, 0), parent=mug)
    nb = L.box("notebook", (0.17, 0.24, 0.014), L.satin("nb", (0.08, 0.09, 0.11, 1), 0.6, 0.0), (-0.5, -0.12, 0.764), (0, 0, 0.18), bevel=0.003, parent=root)
    L.cyl("pen", 0.0045, 0.14, M["black"], (-0.42, -0.2, 0.762), (0, math.radians(90), 0.4), parent=root)
    anchor("emma_desk", (0, -0.1, 0.8), root)
    H["emma"] = root
    return root


# ------------------------------------------------------------------ harness bench
SHEET = (0.297, 0.21, 0.005)


def harness_bench(M, x=-3.0):
    root = L.empty("bench", (x, 0.0, 0))
    # extrusion frame
    for sx in (-0.62, 0.62):
        for sy in (-0.32, 0.32):
            L.box("bf_leg", (0.045, 0.045, 0.74), M["alu"], (sx, sy, 0.37), bevel=0.004, parent=root)
            L.cyl("bf_foot", 0.03, 0.02, M["black"], (sx, sy, 0.01), parent=root)
    for sy in (-0.32, 0.32):
        L.box("bf_rail", (1.29, 0.045, 0.045), M["alu"], (0, sy, 0.2), bevel=0.004, parent=root)
    # thick anodised tooling plate with T-slots and screws
    plate = L.box("tool_plate", (1.36, 0.76, 0.05), M["alu_dark"], (0, 0, 0.765), bevel=0.006, parent=root)
    for i in range(7):
        L.box("tslot", (1.30, 0.012, 0.004), M["black"], (0, -0.3 + i * 0.1, 0.0255), bevel=0.001, parent=plate)
    for sx in (-0.64, 0.64):
        for sy in (-0.34, 0.34):
            screw("ps", (sx, sy, 0.026), plate, M)
    # linear rails + carriage
    for sy in (-0.26, 0.26):
        rl = L.box("lin_rail", (1.2, 0.022, 0.018), M["steel"], (0, sy, 0.034), bevel=0.002, parent=plate)
        for k in range(12):
            L.cyl("rail_bolt", 0.0035, 0.002, M["black"], (-0.55 + k * 0.1, 0, 0.0095), parent=rl, verts=16)
    # alignment jig: L fence + dowels, the stack sits at (0.12, 0)
    jig = L.empty("jig", (0.12, 0.0, 0.79), plate.parent)
    L.box("fence_back", (0.36, 0.03, 0.05), M["alu"], (0, SHEET[1] / 2 + 0.017, 0.025), bevel=0.003, parent=jig)
    L.box("fence_side", (0.03, 0.27, 0.05), M["alu"], (-SHEET[0] / 2 - 0.017, 0.012, 0.025), bevel=0.003, parent=jig)
    for dx in (-0.1, 0.1):
        L.cyl("dowel", 0.006, 0.07, M["chrome"], (dx, SHEET[1] / 2 + 0.004, 0.035), parent=jig)
    # base pad
    L.box("jig_pad", (0.33, 0.24, 0.006), M["graphite"], (0, 0, 0.003), bevel=0.002, parent=jig)
    H["jig"] = jig
    # clamp head on a gantry: two posts + beam + pneumatic cylinder + clamp plate
    for sx in (-0.2, 0.44):
        L.box("g_post", (0.05, 0.05, 0.56), M["alu"], (sx, 0.3, 1.07), bevel=0.004, parent=root)
    beam = L.box("g_beam", (0.74, 0.06, 0.06), M["alu"], (0.12, 0.3, 1.36), bevel=0.005, parent=root)
    cylb = L.cyl("pneu", 0.03, 0.16, M["alu"], (0.12, 0.2, 1.27), parent=root)
    L.box("pneu_arm", (0.05, 0.12, 0.03), M["alu"], (0.12, 0.26, 1.33), bevel=0.003, parent=root)
    clamp = L.empty("clamp", (0.12, 0.0, 1.17), root)
    L.cyl("clamp_rod", 0.009, 0.14, M["chrome"], (0, 0.2, 0.07), parent=clamp)
    L.box("clamp_arm", (0.04, 0.22, 0.02), M["alu"], (0, 0.1, 0.0), bevel=0.003, parent=clamp)
    L.box("clamp_plate", (0.31, 0.22, 0.016), M["alu"], (0, 0.0, -0.01), bevel=0.003, parent=clamp)
    glow = L.led("clamp_glow", L.SKY_L)
    L.box("clamp_strip", (0.29, 0.004, 0.006), glow, (0, -0.111, -0.01), bevel=0.001, parent=clamp)
    H["clamp"] = clamp
    H["clamp_glow"] = glow
    # feeder magazine (holds the tool sheets) at the left
    mag = L.empty("magazine", (-0.42, 0.02, 0.79), root)
    L.box("mag_base", (0.34, 0.26, 0.02), M["graphite"], (0, 0, 0.01), bevel=0.003, parent=mag)
    for sx in (-0.165, 0.165):
        L.box("mag_wall", (0.012, 0.26, 0.14), M["alu"], (sx, 0, 0.07), bevel=0.002, parent=mag)
    L.box("mag_back", (0.34, 0.012, 0.14), M["alu"], (0, 0.13, 0.07), bevel=0.002, parent=mag)
    H["mag"] = mag
    # small status panel
    pnl = L.box("bench_panel", (0.2, 0.012, 0.1), M["black"], (0.5, -0.32, 0.86), (math.radians(-15), 0, 0), bevel=0.004, parent=root)
    pg = L.led("bench_lcd", L.SKY_L, strength=0.8)
    L.box("bench_lcd", (0.16, 0.002, 0.05), pg, (0, -0.0065, 0.01), bevel=0.0005, parent=pnl)
    H["bench_lcd"] = pg
    anchor("bench_stack", (0.12, 0.0, 0.86), root)
    anchor("bench_mag", (-0.42, 0.0, 0.95), root)
    anchor("bench", (0, -0.2, 0.9), root)
    H["bench"] = root
    return root


def sheet(name, kind, M, loc=(0, 0, 0), parent=None):
    s = L.card(name, SHEET[0], SHEET[1], SHEET[2], M["sheet_body"], M["print_" + kind], loc, parent=parent)
    band = {"sys": L.SKY_L, "msg": (1.0, 0.45, 0.1, 1), "tool": L.GREEN_L, "result": L.GREEN_L}[kind]
    em = L.led(name + "_edge", band, body=tuple(c * 0.5 for c in band[:3]) + (1,), strength=0.0)
    L.box(name + "_edge", (SHEET[0] * 1.0, 0.004, SHEET[2] * 1.02), em, (0, -SHEET[1] / 2, 0), bevel=0.0006, parent=s)
    L.box(name + "_edge2", (0.004, SHEET[1], SHEET[2] * 1.02), em, (-SHEET[0] / 2, 0, 0), bevel=0.0006, parent=s)
    s["edge_mat"] = em.name
    return s, em


# ------------------------------------------------------------------ the model: 24 glowing layers, opened up
NL = 24


def model_machine(M, x=0.0):
    root = L.empty("model", (x, 0.55, 0))
    base = L.box("m_base", (1.06, 1.06, 0.2), M["alu_dark"], (0, 0, 0.1), bevel=0.02, seg=4, parent=root)
    L.box("m_base_lip", (1.0, 1.0, 0.02), M["alu"], (0, 0, 0.21), bevel=0.004, parent=root)
    L.box("m_intake", (0.24, 0.02, 0.06), M["black"], (-0.25, -0.531, 0.11), bevel=0.004, parent=root)
    intake_led = L.led("m_intake_led", L.SKY_L)
    L.box("m_intake_glow", (0.2, 0.004, 0.006), intake_led, (-0.25, -0.542, 0.15), bevel=0.001, parent=root)
    H["m_intake_led"] = intake_led
    for i in range(6):
        L.box("m_vent", (0.06, 0.004, 0.09), M["black"], (0.12 + i * 0.065, -0.531, 0.1), bevel=0.001, parent=root)
    # four polished corner columns
    for sx in (-0.47, 0.47):
        for sy in (-0.47, 0.47):
            L.cyl("m_col", 0.022, 2.0, M["steel"], (sx, sy, 1.2), verts=32, parent=root)
    layers, mats = [], []
    gap, z0 = 0.072, 0.29
    for i in range(NL):
        m = L.textured(f"layer_{i:02d}", "layer_base.png", rough=0.32, coat=0.5, metallic=0.3,
                       emit_mask="layer_mask.png", emit_color=L.SKY)
        ly = L.empty(f"layer_{i:02d}", (0, 0, z0 + i * gap), root)
        L.box(f"lay_body_{i}", (0.86, 0.86, 0.018), M["graphite"], (0, 0, 0), bevel=0.003, parent=ly)
        L.plane_uv(f"lay_top_{i}", 0.84, 0.84, m, (0, 0, 0.0092), parent=ly)
        L.box(f"lay_gold_{i}", (0.6, 0.006, 0.006), M["gold"], (0, -0.432, 0), bevel=0.001, parent=ly)
        for sx in (-0.47, 0.47):
            for sy in (-0.47, 0.47):
                L.box("lay_clip", (0.06, 0.06, 0.024), M["alu"], (sx * 0.98, sy * 0.98, 0), bevel=0.004, parent=ly)
        layers.append(ly)
        mats.append(m)
    top_z = z0 + NL * gap + 0.02
    lid = L.empty("m_lid", (0, 0, top_z), root)
    L.box("lid_plate", (0.98, 0.98, 0.03), M["alu"], (0, 0, 0), bevel=0.006, parent=lid)
    for i in range(22):
        L.box("lid_fin", (0.9, 0.006, 0.07), M["alu"], (0, -0.42 + i * 0.04, 0.05), bevel=0.0015, parent=lid)
    # output port on the right side (where the tool call leaves)
    port = L.cyl("m_port", 0.05, 0.05, M["alu"], (0.53, -0.2, 1.62), (0, math.radians(90), 0), parent=root)
    pled = L.led("m_port_led", L.SKY_L)
    L.torus("m_port_ring", 0.04, 0.006, pled, (0, 0, 0.027), parent=port)
    H["m_port_led"] = pled
    # removable side covers (opened at the start of the model shot)
    covers = []
    for side in (-1, 1):
        cv = L.empty(f"cover_{side}", (0, 0, 0), root)
        L.box("cover_front", (0.52, 0.012, 1.86), M["alu"], (side * 0.26, -0.5, 1.2), bevel=0.006, parent=cv)
        L.box("cover_side", (0.012, 1.0, 1.86), M["alu"], (side * 0.51, 0, 1.2), bevel=0.006, parent=cv)
        for k in range(8):
            L.box("cover_slot", (0.3, 0.003, 0.012), M["black"], (side * 0.26, -0.507, 0.55 + k * 0.025), bevel=0.0008, parent=cv)
        covers.append(cv)
    H.update(model=root, layers=layers, layer_mats=mats, covers=covers, lid=lid)
    anchor("model_top", (0, -0.45, 2.1), root)
    anchor("model_mid", (0.43, -0.43, 1.2), root)
    anchor("model_low", (-0.43, -0.43, 0.6), root)
    anchor("model_port", (0.58, -0.2, 1.62), root)
    return root


# ------------------------------------------------------------------ guard: an inspection ring on a stand
def guard(M, x=1.65):
    root = L.empty("guard", (x, 0.15, 0))
    L.cyl("gd_foot", 0.16, 0.025, M["alu_dark"], (0, 0, 0.0125), parent=root)
    L.cyl("gd_post", 0.03, 0.9, M["alu"], (0, 0, 0.47), parent=root)
    hd = L.empty("gd_head", (0, 0, 1.16), root)
    hd.rotation_euler = (0, math.radians(90), 0)
    L.cyl("gd_housing", 0.13, 0.08, M["alu_dark"], (0, 0, 0), verts=64, bevel=0.01, parent=hd)
    L.cyl("gd_bore", 0.06, 0.082, M["black"], (0, 0, 0), verts=48, bevel=0.002, parent=hd)
    ring = L.led("gd_ring", L.SKY_L)
    L.torus("gd_ring_f", 0.075, 0.006, ring, (0, 0, -0.042), parent=hd)
    L.torus("gd_ring_b", 0.075, 0.006, ring, (0, 0, 0.042), parent=hd)
    for k in range(8):
        a = k * math.pi / 4
        screw("gd_scr", (0.105 * math.cos(a), 0.105 * math.sin(a), -0.041), hd, M, 0.006, (math.radians(180), 0, 0))
    L.box("gd_neck", (0.05, 0.05, 0.12), M["alu"], (0, 0, 1.06), bevel=0.004, parent=root)
    H["guard_ring"] = ring
    anchor("guard", (0, -0.14, 1.16), root)
    return root


# ------------------------------------------------------------------ tool rack: 15 machined cartridges
TOOLS = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "create_purchase_request",
         "list_my_approvals", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
         "release_purchase_order", "order_status", "receive_goods", "register_supplier", "send_message"]
WRITES = {"create_purchase_request", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
          "release_purchase_order", "receive_goods", "register_supplier", "send_message"}


def tool_rack(M, x=3.3):
    root = L.empty("rack", (x, 0.45, 0))
    L.box("rk_plinth", (0.66, 0.62, 0.3), M["alu_dark"], (0, 0, 0.15), bevel=0.012, parent=root)
    pitch, z0 = 0.068, 0.36
    top = z0 + 15 * pitch
    for sx in (-0.29, 0.29):
        post = L.box("rk_post", (0.04, 0.56, top - 0.3 + 0.04), M["graphite"], (sx, 0, (top + 0.3) / 2), bevel=0.004, parent=root)
        for k in range(30):
            L.cyl("rk_hole", 0.0045, 0.003, M["black"], (0, -0.281, (k - 14.5) * 0.034), (math.radians(90), 0, 0), verts=16, parent=post)
    L.box("rk_top", (0.62, 0.58, 0.03), M["alu"], (0, 0, top + 0.03), bevel=0.006, parent=root)
    L.box("rk_back", (0.54, 0.02, top - 0.3), M["alu_dark"], (0, 0.27, (top + 0.3) / 2), bevel=0.003, parent=root)
    carts, leds = {}, {}
    for i, name in enumerate(TOOLS):
        z = top - 0.04 - i * pitch
        c = L.empty("cart_" + name, (0, 0, z), root)
        L.box("ct_body", (0.5, 0.5, 0.058), M["alu_dark"], (0, 0.0, 0), bevel=0.004, parent=c)
        L.box("ct_face", (0.53, 0.016, 0.062), M["alu"], (0, -0.258, 0), bevel=0.005, seg=4, parent=c)
        stripe = M["ember_an"] if name in WRITES else M["sky_an"]
        L.box("ct_stripe", (0.012, 0.004, 0.044), stripe, (-0.245, -0.2665, 0), bevel=0.001, parent=c)
        for k in range(10):
            L.box("ct_vent", (0.006, 0.004, 0.034), M["black"], (-0.2 + k * 0.014, -0.2665, 0), bevel=0.0008, parent=c)
        # pull handle: two standoffs + bar
        for hx in (0.06, 0.2):
            L.cyl("ct_stand", 0.006, 0.03, M["chrome"], (hx, -0.28, 0), (math.radians(90), 0, 0), verts=20, parent=c)
        L.cyl("ct_bar", 0.0065, 0.16, M["chrome"], (0.13, -0.295, 0), (0, math.radians(90), 0), verts=24, parent=c)
        lm = L.led("ct_led_" + name, L.SKY_L)
        L.sphere("ct_led", 0.0055, lm, (-0.04, -0.267, 0.012), parent=c)
        L.box("ct_lens", (0.03, 0.003, 0.012), M["smoke"], (-0.04, -0.2665, -0.01), bevel=0.0008, parent=c)
        carts[name], leds[name] = c, lm
        anchor("cart_" + name, (0.27, -0.3, 0.0), c)
    # MCP socket on the right side panel
    sock = L.empty("mcp_socket", (-0.31, -0.05, 0.62), root)
    sock.rotation_euler = (0, math.radians(-90), 0)
    L.box("sock_flange", (0.11, 0.11, 0.012), M["alu"], (0, 0, 0.006), bevel=0.004, parent=sock)
    for sx in (-0.04, 0.04):
        for sy in (-0.04, 0.04):
            screw("sock_scr", (sx, sy, 0.0135), sock, M, 0.005)
    L.cyl("sock_barrel", 0.032, 0.04, M["chrome"], (0, 0, 0.03), verts=48, parent=sock)
    L.cyl("sock_face", 0.024, 0.042, M["black"], (0, 0, 0.031), verts=48, parent=sock)
    H.update(rack=root, carts=carts, cart_leds=leds, socket=sock)
    anchor("rack_top", (0, -0.3, top + 0.1), root)
    anchor("rack", (0, -0.32, (top + 0.3) / 2), root)
    anchor("mcp_socket", (-0.36, -0.05, 0.62), root)
    return root


def mcp_plug(M, rack_x=3.3, erp_x=6.1):
    """MCP: a circular industrial plug on a braided cable from the guard into the rack's left side,
    plus the old grey cable from the rack to the Ledgerline cabinet."""
    sx = rack_x - 0.31 - 0.012
    plug = L.empty("mcp_plug", (sx, 0.40, 0.62))
    plug.rotation_euler = (0, math.radians(-90), 0)
    knurl = L.anodized("knurl", (0.1, 0.105, 0.115, 1), 0.4)
    L._bump(knurl, scale=(1, 1, 1), strength=0.35, noise_scale=60.0, kind="wave")
    L.cyl("plug_nut", 0.04, 0.05, knurl, (0, 0, 0.025), verts=64, bevel=0.003, parent=plug)
    L.cyl("plug_body", 0.034, 0.09, M["alu"], (0, 0, 0.095), verts=48, bevel=0.004, parent=plug)
    ring = L.led("plug_ring", L.SKY_L)
    L.torus("plug_band", 0.035, 0.004, ring, (0, 0, 0.075), parent=plug)
    L.cyl("plug_boot", 0.028, 0.1, M["rubber"], (0, 0, 0.185), verts=32, r2=0.016, parent=plug)
    H["plug"], H["plug_ring"] = plug, ring
    H["plug_x"] = sx
    braid = L.principled("braid", (0.03, 0.032, 0.036, 1), rough=0.55)
    L._bump(braid, scale=(40, 40, 40), strength=0.25, noise_scale=8.0, kind="wave")
    pts = [(1.76, 0.15, 1.16), (2.05, 0.12, 1.0), (2.35, 0.25, 0.66), (sx - 0.4, 0.40, 0.62), (sx - 0.23, 0.40, 0.62)]
    L.tube("mcp_cable", pts, 0.014, braid)
    H["mcp_cable_pts"] = pts
    grey = L.principled("pvc_grey", (0.42, 0.42, 0.40, 1), rough=0.5, coat=0.1)
    lp = [(rack_x + 0.22, 0.74, 0.36), (rack_x + 0.55, 0.85, 0.05), (erp_x - 0.9, 0.8, 0.04), (erp_x - 0.5, 0.65, 0.3), (erp_x - 0.335, 0.6, 0.45)]
    L.tube("legacy_cable", lp, 0.012, grey)
    L.box("db25", (0.03, 0.07, 0.03), M["beige_d"], (erp_x - 0.335, 0.6, 0.45), bevel=0.004)
    L.box("db25_r", (0.03, 0.07, 0.03), M["graphite"], (rack_x + 0.22, 0.74, 0.36), bevel=0.004)
    H["legacy_pts"] = lp
    anchor("mcp_plug", (sx - 0.12, 0.30, 0.68))
    anchor("mcp_cable", (2.3, 0.2, 0.7))
    anchor("legacy", (0.5 * (rack_x + erp_x), 0.8, 0.06))
    return plug

# ------------------------------------------------------------------ Ledgerline ERP 7.2 (1998) cabinet
def ledgerline(M, x=6.1):
    root = L.empty("erp", (x, 0.5, 0))
    W, D, Hh = 0.64, 0.8, 1.78
    L.box("erp_body", (W, D, Hh), M["beige"], (0, 0, Hh / 2 + 0.05), bevel=0.012, parent=root)
    L.box("erp_plinth", (W - 0.04, D - 0.04, 0.05), M["black"], (0, 0, 0.025), bevel=0.005, parent=root)
    for sx in (-0.26, 0.26):
        for sy in (-0.33, 0.33):
            L.cyl("erp_caster", 0.03, 0.03, M["black"], (sx, sy, 0.015), (math.radians(90), 0, 0), parent=root)
    fz = -D / 2 - 0.004
    # side panel seams + screws
    for sz in (0.5, 1.2):
        L.box("erp_seam", (0.002, D * 0.96, 0.003), M["beige_d"], (W / 2 + 0.0005, 0, sz), bevel=0, parent=root)
    # top: three 5.25" bays + a tape drive
    for i in range(3):
        bz = Hh - 0.08 - i * 0.07
        bay = L.box("bay", (0.46, 0.012, 0.058), M["beige_d"], (0, fz, bz), bevel=0.003, parent=root)
        L.box("bay_slot", (0.3, 0.004, 0.006), M["black"], (-0.03, -0.007, 0.006), bevel=0.001, parent=bay)
        L.box("bay_btn", (0.03, 0.006, 0.012), M["beige"], (0.18, -0.008, -0.012), bevel=0.002, parent=bay)
        bl = L.led(f"bay_led_{i}", (1.0, 0.45, 0.05, 1))
        L.box("bay_led", (0.008, 0.004, 0.004), bl, (0.12, -0.008, -0.014), bevel=0.0008, parent=bay)
        H[f"bay_led_{i}"] = bl
    # smoked glass door in a deep bezel, with the old units glowing behind it
    dz, dh, dw = 0.98, 0.9, 0.56
    for (bx, bz, sx, sz) in [(0, dz + dh / 2 - 0.03, dw, 0.06), (0, dz - dh / 2 + 0.03, dw, 0.06),
                             (-dw / 2 + 0.03, dz, 0.06, dh), (dw / 2 - 0.03, dz, 0.06, dh)]:
        L.box("door_bezel", (sx, 0.07, sz), M["beige_d"], (bx, fz - 0.03, bz), bevel=0.006, parent=root)
    L.box("erp_door_glass", (dw - 0.1, 0.006, dh - 0.1), M["smoke"], (0, fz - 0.062, dz), bevel=0.002, parent=root)
    L.box("door_back", (dw - 0.1, 0.004, dh - 0.1), M["black"], (0, fz + 0.002, dz), bevel=0.0, parent=root)
    L.cyl("erp_lock", 0.011, 0.014, M["chrome"], (dw / 2 - 0.03, fz - 0.068, dz), (math.radians(90), 0, 0), verts=24, parent=root)
    unit_leds = []
    for i in range(7):
        uz = dz - dh / 2 + 0.1 + i * 0.105
        u = L.box("unit", (dw - 0.12, 0.04, 0.09), M["graphite"], (0, fz - 0.022, uz), bevel=0.003, parent=root)
        row = []
        for k in range(8):
            col = (0.1, 1.0, 0.25, 1) if k % 3 else (1.0, 0.5, 0.05, 1)
            lm = L.led(f"u_led_{i}_{k}", col)
            L.box("u_led", (0.01, 0.004, 0.006), lm, (-0.18 + k * 0.026, -0.021, 0.025), bevel=0.001, parent=u)
            row.append(lm)
        for k in range(12):
            L.box("u_vent", (0.004, 0.004, 0.05), M["black"], (0.05 + k * 0.013, -0.021, -0.01), bevel=0.0006, parent=u)
        unit_leds.append(row)
    H["unit_leds"] = unit_leds
    # top grille + side ribs
    for k in range(16):
        L.box("grille", (0.012, 0.6, 0.006), M["beige_d"], (-0.24 + k * 0.032, 0, Hh + 0.054), bevel=0.002, parent=root)
    for sx in (-1, 1):
        for k in range(6):
            L.box("rib", (0.006, 0.02, Hh * 0.9), M["beige_d"], (sx * (W / 2 + 0.002), -0.3 + k * 0.12, Hh / 2 + 0.05), bevel=0.002, parent=root)
    L.box("erp_kick", (W * 0.96, 0.02, 0.08), M["beige_d"], (0, fz + 0.002, 0.1), bevel=0.004, parent=root)
    # louvred vents at the bottom
    for k in range(14):
        L.box("louvre", (0.5, 0.02, 0.012), M["beige_d"], (0, fz, 0.16 + k * 0.022), (math.radians(30), 0, 0), bevel=0.002, parent=root)
    # power switch + front LEDs
    pw = L.led("erp_power", (0.15, 1.0, 0.3, 1), strength=1.5)
    L.cyl("pw_led", 0.006, 0.006, pw, (-0.22, fz - 0.004, 1.52), (math.radians(90), 0, 0), verts=16, parent=root)
    hd = L.led("erp_hdd", (1.0, 0.5, 0.05, 1))
    L.cyl("hd_led", 0.006, 0.006, hd, (-0.18, fz - 0.004, 1.52), (math.radians(90), 0, 0), verts=16, parent=root)
    L.box("erp_badge", (0.18, 0.004, 0.04), M["alu"], (0.14, fz - 0.002, 1.52), bevel=0.002, parent=root)
    H.update(erp=root, erp_power=pw, erp_hdd=hd)
    anchor("erp_badge", (0.14, -D / 2 - 0.02, 1.52), root)
    anchor("erp", (0, -D / 2, 1.0), root)
    anchor("erp_side", (-W / 2, 0, 0.55), root)
    return root


def printer(M, x=7.15):
    """A 1998 dot-matrix printer on a beige cart, green-bar paper feeding out of the top."""
    root = L.empty("printer", (x, 0.2, 0))
    L.box("cart_top", (0.6, 0.45, 0.025), M["beige_d"], (0, 0, 0.7), bevel=0.004, parent=root)
    L.box("cart_shelf", (0.56, 0.42, 0.02), M["beige_d"], (0, 0, 0.2), bevel=0.003, parent=root)
    for sx in (-0.27, 0.27):
        for sy in (-0.19, 0.19):
            L.box("cart_leg", (0.025, 0.025, 0.7), M["alu_dark"], (sx, sy, 0.35), bevel=0.003, parent=root)
    # paper pile on the shelf
    for k in range(10):
        L.box("pile", (0.38, 0.28, 0.006), L.satin("pile_paper", (0.84, 0.85, 0.82, 1), 0.8, 0), (0, 0, 0.214 + k * 0.006), (0, 0, R.uniform(-0.02, 0.02)), bevel=0.001, parent=root)
    pr = L.empty("pr_body", (0, 0, 0.712), root)
    L.box("pr_base", (0.52, 0.34, 0.1), M["beige"], (0, 0, 0.05), bevel=0.012, parent=pr)
    L.box("pr_lid", (0.46, 0.2, 0.03), M["smoke"], (0, 0.03, 0.11), (math.radians(-8), 0, 0), bevel=0.005, parent=pr)
    L.box("pr_panel", (0.14, 0.02, 0.04), M["beige_d"], (0.15, -0.17, 0.06), bevel=0.003, parent=pr)
    for k in range(3):
        lm = L.led(f"pr_led_{k}", (0.15, 1.0, 0.3, 1), strength=1.2 if k == 0 else 0)
        L.box("pr_led", (0.008, 0.004, 0.005), lm, (0.11 + k * 0.025, -0.181, 0.065), bevel=0.0008, parent=pr)
    for sx in (-0.27, 0.27):
        L.cyl("pr_knob", 0.03, 0.03, M["black"], (sx, 0.02, 0.07), (0, math.radians(90), 0), parent=pr)
    # the receipt: green-bar paper rising out of the slot (scale Z keyed from 0)
    slot = L.empty("receipt_root", (0, 0.07, 0.12), pr)
    rc = L.plane_uv("receipt", 0.38, 0.5, M["greenbar"], (0, 0, 0.25), (math.radians(90), 0, 0), parent=slot)
    slot.rotation_euler = (math.radians(-12), 0, 0)
    H.update(printer=root, receipt_root=slot)
    anchor("receipt", (0, 0.07, 1.25), root)
    anchor("printer", (0, -0.2, 0.85), root)
    return root


# ------------------------------------------------------------------ Daniel's desk with the approval tray
def daniel_desk(M, x=8.95):
    root = L.empty("daniel", (x, -0.2, 0))
    root.rotation_euler = (0, 0, math.radians(-16))
    L.box("dd_top", (1.5, 0.8, 0.04), M["walnut"], (0, 0, 0.74), bevel=0.008, parent=root)
    for sx in (-0.68, 0.68):
        L.box("dd_leg", (0.04, 0.7, 0.72), M["black"], (sx, 0, 0.36), bevel=0.006, parent=root)
    # two-tier letter tray (brushed steel)
    tray = L.empty("tray", (-0.25, 0.05, 0.76), root)
    for tz in (0.0, 0.11):
        L.box("tray_base", (0.36, 0.28, 0.006), M["alu"], (0, 0, tz + 0.003), bevel=0.002, parent=tray)
        L.box("tray_back", (0.36, 0.006, 0.05), M["alu"], (0, 0.14, tz + 0.025), bevel=0.002, parent=tray)
        for sx in (-0.18, 0.18):
            L.box("tray_side", (0.006, 0.28, 0.04), M["alu"], (sx, 0, tz + 0.02), bevel=0.002, parent=tray)
        L.box("tray_lip", (0.36, 0.006, 0.02), M["alu"], (0, -0.14, tz + 0.01), bevel=0.002, parent=tray)
    for sx in (-0.17, 0.17):
        L.cyl("tray_post", 0.005, 0.11, M["chrome"], (sx, 0.12, 0.06), verts=16, parent=tray)
    po = L.plane_uv("doc_po", 0.21, 0.297 * 0.85, M["doc_po"], (0.0, 0.0, 0.009), (0, 0, math.radians(3)), parent=tray)
    po.scale = (1.0, 0.92, 1.0)
    prd = L.plane_uv("doc_pr", 0.21, 0.297 * 0.85, M["doc_pr"], (0.01, -0.005, 0.0135), (0, 0, math.radians(-2)), parent=tray)
    prd.scale = (1.0, 0.92, 1.0)
    H["doc_pr"] = prd
    # lamp
    lamp = L.empty("lamp", (0.5, 0.2, 0.76), root)
    L.cyl("lamp_base", 0.08, 0.02, M["black"], (0, 0, 0.01), parent=lamp)
    L.cyl("lamp_arm1", 0.008, 0.38, M["black"], (0.0, 0.05, 0.19), (math.radians(-20), 0, 0), parent=lamp)
    L.cyl("lamp_arm2", 0.008, 0.32, M["black"], (0.0, -0.04, 0.4), (math.radians(60), 0, 0), parent=lamp)
    shade = L.cyl("lamp_shade", 0.07, 0.1, M["black"], (0.0, -0.17, 0.46), (math.radians(30), 0, 0), r2=0.03, parent=lamp)
    bulb = L.led("bulb", (1.0, 0.75, 0.45, 1), body=(0.9, 0.85, 0.8, 1), strength=4.0)
    L.sphere("lamp_bulb", 0.025, bulb, (0, 0, -0.05), parent=shade)
    # mug, pen, closed laptop, plant pot
    mug = L.cyl("dmug", 0.042, 0.1, M["ceramic_w"], (0.25, -0.2, 0.81), parent=root)
    L.torus("dmug_h", 0.03, 0.007, M["ceramic_w"], (0.045, 0, 0), (math.radians(90), 0, 0), parent=mug)
    lap = L.box("laptop", (0.34, 0.24, 0.016), M["alu"], (0.18, 0.12, 0.768), (0, 0, math.radians(8)), bevel=0.005, parent=root)
    L.cyl("dpen", 0.005, 0.15, M["gold"], (-0.0, -0.25, 0.766), (0, math.radians(90), -0.3), parent=root)
    pot = L.cyl("pot", 0.06, 0.11, M["ceramic_w"], (-0.6, 0.25, 0.815), r2=0.05, parent=root)
    leaf = L.satin("leaf", (0.06, 0.2, 0.07, 1), 0.5, 0.2)
    for k in range(9):
        a = k * 2 * math.pi / 9
        L.box("leaf", (0.02, 0.09, 0.004), leaf, (0.03 * math.cos(a), 0.03 * math.sin(a), 0.09), (math.radians(50), 0, a), bevel=0.002, parent=pot)
    H["daniel"] = root
    anchor("tray", (-0.25, 0.0, 0.83), root)
    anchor("daniel", (0, -0.3, 0.8), root)
    return root


# ------------------------------------------------------------------ conduits and packets
PATHS = {}


def conduits(M):
    """Clear glass conduits between stations, each with a matching guide path for packets."""
    defs = {
        "c_emma_bench": [(-5.25, 0.36, 1.05), (-4.6, 0.3, 1.15), (-3.9, 0.12, 1.02), (-3.42, 0.02, 0.88)],
        "c_bench_model": [(-2.3, 0.0, 0.86), (-1.6, -0.05, 0.6), (-0.9, -0.05, 0.12), (-0.25, 0.0, 0.11)],
        "c_model_guard": [(0.55, 0.35, 1.62), (0.95, 0.25, 1.4), (1.3, 0.15, 1.18), (1.56, 0.15, 1.16)],
        "c_rack_bench": [(3.0, 0.6, 0.38), (2.2, 1.35, 0.08), (0.0, 1.45, 0.06), (-2.2, 1.0, 0.08), (-2.8, 0.38, 0.8)],
    }
    core = L.led("conduit_core", L.SKY_L, body=(0.6, 0.7, 0.9, 1), strength=0.15)
    for n, pts in defs.items():
        L.tube(n, pts, 0.026, M["glass"])
        L.tube(n + "_core", pts, 0.003, core)
        PATHS[n] = L.path("P_" + n, pts)
    PATHS["mcp"] = L.path("P_mcp", H["mcp_cable_pts"] + [(H["plug_x"] + 0.1, 0.40, 0.62)])
    PATHS["legacy"] = L.path("P_legacy", H["legacy_pts"])
    H["conduit_core"] = core
    return PATHS


def packet(name, color, size=(0.06, 0.03, 0.03)):
    m = L.led(name + "_m", color, body=(0.9, 0.95, 1.0, 1), strength=6.0)
    p = L.cyl(name, size[1] * 0.6, size[0], m, (0, 0, 0), (0, math.radians(90), 0), verts=24)
    return p, m


def build_all():
    M = finishes()
    emma_desk(M)
    harness_bench(M)
    model_machine(M)
    guard(M)
    tool_rack(M)
    mcp_plug(M)
    ledgerline(M)
    printer(M)
    daniel_desk(M)
    conduits(M)
    return M
