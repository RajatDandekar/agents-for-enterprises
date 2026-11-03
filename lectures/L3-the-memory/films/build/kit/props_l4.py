"""Props for the Lecture 4 films ("The Hands"), on top of the shared series kit (l2kit, copied from Lecture 2 so the
films read as the same course). All readable text stays 2D (overlay.py); these props carry only pins.

  machine       the sealed model: the L2 enclosure with the 24-floor stack behind a frosted window (copied from L2 s1)
  tool_unit     a tool as a machined unit: intake gate (tool.json), lid that lifts (exploded view), a dark-glass core
                whose 26 light bars are the 26 real lines of tool.py, four service ports at the back, an output slot
  cabinet       a 1998 Ledgerline service cabinet: warm-grey enamel, vents, ember status lamps, tape-reel window
  capsule       a request capsule (glass body, light core, aluminium end caps)
  envelope      a legacy reply envelope (enamel card with a coloured stripe)
  result_slab   the clean result: a glass slab with glowing edge strips
  conduit       a glass tube along a cubic curve (with a light strand inside) + path() points for things travelling it
  wall          a tall matte partition in an aluminium frame, with one slot (what the model cannot see past)
  database / badge / padlock   the things behind the wall
  rail          an aluminium two-rod rail on a graphite bed
"""
import math

import bpy
from mathutils import Vector

import l2kit as K

ENAMEL = (0.36, 0.335, 0.29, 1)   # warm-grey 1990s enamel


def _mat_once(name, fn):
    if name not in K._MAT:
        K._MAT[name] = fn()
    return K._MAT[name]


def enamel():
    def mk():
        m = K.principled("enamel", ENAMEL, rough=0.52, coat=0.15, coat_rough=0.35)
        K._bump(m, scale=(40, 40, 40), strength=0.01, noise_scale=30)
        return m
    return _mat_once("enamel", mk)


def smoked():
    return _mat_once("smoked", lambda: K.principled("smoked", (0.05, 0.05, 0.055, 1), rough=0.08, transmission=0.7, ior=1.5))


# ------------------------------------------------------------------------------------------------ the model (from L2 s1)
def machine(name, loc, w=1.3, d=0.7, h=0.95, floors=24):
    """The sealed model: dark anodised enclosure, frosted front window, vented lid, slots left/right, LED strip and the
    24-floor block stack inside. Returns dict(root, window, tower, led, slot_in, slot_out, lid, inner)."""
    root = K.empty(name, loc)
    shell = K.anod(name + "_shell", (0.05, 0.055, 0.068, 1), rough=0.32)
    t = 0.035
    K.rbox(name + "_base", (w + 0.08, d + 0.08, 0.04), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.02), parent=root)
    K.rbox(name + "_back", (w, t, h), bevel=0.01, seg=4, mat=shell, loc=(0, d / 2 - t / 2, 0.04 + h / 2), parent=root)
    for sx in (-1, 1):
        K.rbox(f"{name}_side{sx}", (t, d, h), bevel=0.01, seg=4, mat=shell, loc=(sx * (w / 2 - t / 2), 0, 0.04 + h / 2), parent=root)
        K.rbox(f"{name}_bezel{sx}", (0.012, 0.32, 0.13), bevel=0.004, seg=3, mat=K.M("alu"), loc=(sx * (w / 2 + 0.003), 0, 0.105), parent=root)
        K.rbox(f"{name}_slot{sx}", (0.016, 0.27, 0.09), bevel=0.003, seg=2, mat=K.M("shadowgap"), loc=(sx * (w / 2 + 0.004), 0, 0.105), parent=root)
    lid = K.empty(name + "_lidroot", (0, 0, 0.04 + h + 0.02), parent=root)
    K.rbox(name + "_lid", (w + 0.02, d + 0.02, 0.05), bevel=0.016, seg=5, mat=shell, loc=(0, 0, 0), parent=lid)
    for k in range(9):
        K.rbox(f"{name}_vent{k}", (w * 0.7, 0.012, 0.006), bevel=0.002, seg=2, mat=K.M("shadowgap"),
               loc=(0, -d * 0.3 + k * d * 0.075, 0.026), parent=lid)
    ld = bpy.data.lights.new(name + "_inner", "AREA")
    ld.energy, ld.size, ld.color, ld.shape = 0.0, 0.5, (0.55, 0.72, 1.0), "DISK"
    lo = bpy.data.objects.new(name + "_inner", ld)
    bpy.context.collection.objects.link(lo)
    lo.parent = root
    lo.location = (0, 0.05, 0.04 + h - 0.08)
    lo.visible_glossy = False
    fw, fh = w - 0.12, h - 0.16
    for nm, sz, lc in (("_ft", (w, 0.03, 0.06), (0, -d / 2 + 0.015, 0.04 + h - 0.03)),
                       ("_fb", (w, 0.03, 0.09), (0, -d / 2 + 0.015, 0.04 + 0.045)),
                       ("_fl", (0.06, 0.03, h), (-w / 2 + 0.03, -d / 2 + 0.015, 0.04 + h / 2)),
                       ("_fr", (0.06, 0.03, h), (w / 2 - 0.03, -d / 2 + 0.015, 0.04 + h / 2))):
        K.rbox(name + nm, sz, bevel=0.008, seg=4, mat=K.M("alu"), loc=lc, parent=root)
    frost = K.principled(name + "_frost", (0.88, 0.93, 1.0, 1), rough=0.16, transmission=1.0, ior=1.45)
    win = K.rbox(name + "_window", (fw, 0.012, fh), bevel=0.004, seg=3, mat=frost, loc=(0, -d / 2 + 0.02, 0.04 + 0.09 + fh / 2), parent=root)
    led = K.glow_mat(name + "_led", K.SKY, 0.0)
    K.rbox(name + "_ledbar", (w * 0.5, 0.008, 0.01), bevel=0.003, seg=2, mat=led, loc=(0, -d / 2 - 0.001, 0.04 + 0.05), parent=root)
    slot_in = K.light_mat(name + "_slotin", K.SKY, 0.0)
    slot_out = K.light_mat(name + "_slotout", K.SKY, 0.0)
    K.rbox(name + "_glow_in", (0.004, 0.25, 0.075), bevel=0.001, seg=1, mat=slot_in, loc=(-w / 2 - 0.004, 0, 0.105), parent=root)
    K.rbox(name + "_glow_out", (0.004, 0.25, 0.075), bevel=0.001, seg=1, mat=slot_out, loc=(w / 2 + 0.004, 0, 0.105), parent=root)
    pitch = (h - 0.25) / floors
    tw = K.tower(name + "_tw", (loc[0], loc[1] + 0.02, loc[2] + 0.09), floors=floors, pitch=pitch, w=w - 0.3, d=d - 0.3)
    K.empty(name + "_pin_top", (0, -d / 2, 0.04 + h + 0.05), parent=root)
    K.empty(name + "_pin_in", (-w / 2 - 0.02, 0, 0.17), parent=root)
    K.empty(name + "_pin_out", (w / 2 + 0.02, 0, 0.17), parent=root)
    K.empty(name + "_pin_win", (0, -d / 2 - 0.01, 0.04 + h * 0.6), parent=root)
    return {"root": root, "window": win, "tower": tw, "led": led, "slot_in": slot_in, "slot_out": slot_out, "lid": lid,
            "inner": lo}


# ------------------------------------------------------------------------------------------------ the tool
def _pcb(name, w, d, seed=3):
    """A dark circuit-board floor: a fine grid of faint cells (decorative, not data) under a clear coat."""
    import random
    rnd = random.Random(seed)
    cols, rows = 96, 48
    vals = [(rnd.random() ** 6) * (1 if rnd.random() < 0.5 else 0.4) for _ in range(cols * rows)]
    m = K.cells_mat(name + "_pcbcells", vals, cols, rows, K.SKY, vmax=1.0, strength=0.35)
    return K.plane(name + "_pcb", w, d, m, rot=(-math.pi / 2, 0, 0))


def tool_unit(name, loc, line_lengths, w=1.2, d=0.62, h=0.3):
    """A tool as a machined instrument, centred at loc (bottom at loc.z).
    Outside: a brushed-aluminium housing on a dark base, a smoked window along the front, a lid that lifts off.
    Left face: the intake gate (tool.json) with a scan sheet and a shutter. Inside, on a circuit-board floor: a glass
    intake channel, the core (one light bar per real line of tool.py, its length = the line's length), four internal
    light tubes from the core to four service ports on the back wall, an envelope tray, and an output channel to the
    output slot on the right face. Returns keyable materials/objects; pins <name>_gate, _gate_top, _core, _lid_pin,
    _port0..3 (outside the back wall), _porti0..3, _out, _top, _tray."""
    root = K.empty(name, loc)
    t = 0.028
    zb = 0.035
    K.rbox(name + "_base", (w + 0.07, d + 0.07, zb), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, zb / 2), parent=root)
    K.rbox(name + "_basetrim", (w + 0.074, 0.008, 0.008), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.033, zb - 0.006), parent=root)
    liner = K.principled(name + "_liner", (0.02, 0.023, 0.03, 1), rough=0.5)
    # back, right, left walls (aluminium outside, dark liner inside)
    for nm, sz, lc, ln_sz, ln_lc in (
            ("_wb", (w, t, h), (0, d / 2 - t / 2, zb + h / 2), (w - 2 * t, 0.004, h - 0.01), (0, d / 2 - t - 0.002, zb + h / 2)),
            ("_wr", (t, d, h), (w / 2 - t / 2, 0, zb + h / 2), (0.004, d - 2 * t, h - 0.01), (w / 2 - t - 0.002, 0, zb + h / 2)),
            ("_wl", (t, d, h), (-w / 2 + t / 2, 0, zb + h / 2), (0.004, d - 2 * t, h - 0.01), (-w / 2 + t + 0.002, 0, zb + h / 2))):
        K.rbox(name + nm, sz, bevel=0.007, seg=4, mat=K.M("alu"), loc=lc, parent=root)
        K.rbox(name + nm + "_ln", ln_sz, bevel=0.001, seg=1, mat=liner, loc=ln_lc, parent=root)
    # front: a low aluminium wall with a smoked window above it
    fh = h * 0.42
    K.rbox(name + "_wf", (w, t, fh), bevel=0.007, seg=4, mat=K.M("alu"), loc=(0, -d / 2 + t / 2, zb + fh / 2), parent=root)
    K.rbox(name + "_wf_ln", (w - 2 * t, 0.004, fh - 0.01), bevel=0.001, seg=1, mat=liner, loc=(0, -d / 2 + t + 0.002, zb + fh / 2), parent=root)
    K.rbox(name + "_win", (w - 2 * t, 0.008, h - fh - 0.01), bevel=0.003, seg=2, mat=P_smoked_light(), loc=(0, -d / 2 + 0.012, zb + fh + (h - fh) / 2), parent=root)
    K.rbox(name + "_wintop", (w, t, 0.02), bevel=0.006, seg=3, mat=K.M("alu"), loc=(0, -d / 2 + t / 2, zb + h - 0.01), parent=root)
    led = K.glow_mat(name + "_led", K.SKY, 0.3)
    K.rbox(name + "_ledbar", (w * 0.62, 0.006, 0.008), bevel=0.002, seg=2, mat=led, loc=(0, -d / 2 - 0.001, zb + fh * 0.4), parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.cyl(f"{name}_foot{sx}{sy}", 0.022, 0.012, K.M("alu_dark"), loc=(sx * (w / 2 - 0.02), sy * (d / 2 - 0.02), zb + h + 0.002),
                  verts=24, parent=root)
    # the floor: circuit board, standoffs
    pcb = _pcb(name, w - 2 * t - 0.01, d - 2 * t - 0.01)
    pcb.parent = root
    pcb.location = (0, 0, zb + 0.004)
    zc = zb + 0.11    # the lane height (capsules travel at this z)
    # ---- the gate (tool.json)
    gx = -w / 2 - 0.035
    g = K.empty(name + "_gateroot", (gx, 0, 0), parent=root)
    gw, gh = 0.3, 0.2
    fr = 0.03
    for nm, sz, lc in (("_gt", (0.07, gw + 2 * fr, fr), (0, 0, zc + gh / 2 + fr / 2)), ("_gb", (0.07, gw + 2 * fr, fr), (0, 0, zc - gh / 2 - fr / 2)),
                       ("_gl", (0.07, fr, gh), (0, -gw / 2 - fr / 2, zc)), ("_gr", (0.07, fr, gh), (0, gw / 2 + fr / 2, zc))):
        K.rbox(name + nm, sz, bevel=0.007, seg=4, mat=K.M("alu"), loc=lc, parent=g)
    for sy in (-1, 1):
        for sz in (-1, 1):
            K.cyl(f"{name}_gscrew{sy}{sz}", 0.006, 0.006, K.M("alu_dark"), loc=(-0.036, sy * (gw / 2 + fr / 2), zc + sz * (gh / 2 + fr / 2)),
                  verts=16, parent=g).rotation_euler = (0, math.pi / 2, 0)
    ring_ok = K.light_mat(name + "_ring_ok", K.GREEN, 0.0)
    ring_no = K.light_mat(name + "_ring_no", K.EMBER, 0.0)
    ring_idle = K.light_mat(name + "_ring_idle", K.SKY, 0.6)
    for nm, m, off in (("_ri", ring_idle, 0.0), ("_rok", ring_ok, 0.0015), ("_rno", ring_no, 0.003)):
        for kk, (sz, lc) in enumerate((((0.004, gw, 0.006), (-0.037 - off, 0, zc + gh / 2 - 0.004)),
                                      ((0.004, gw, 0.006), (-0.037 - off, 0, zc - gh / 2 + 0.004)),
                                      ((0.004, 0.006, gh), (-0.037 - off, -gw / 2 + 0.004, zc)),
                                      ((0.004, 0.006, gh), (-0.037 - off, gw / 2 - 0.004, zc)))):
            K.rbox(f"{name}{nm}{kk}", sz, bevel=0.0015, seg=1, mat=m, loc=lc, parent=g)
    scan_m = K.light_mat(name + "_scan", K.SKY, 0.0)
    scan = K.rbox(name + "_scan", (0.003, gw - 0.01, 0.004), bevel=0.001, seg=1, mat=scan_m, loc=(-0.02, 0, zc - gh / 2), parent=g)
    scan.visible_shadow = False
    shutter = K.rbox(name + "_shutter", (0.012, gw - 0.004, gh - 0.004), bevel=0.003, seg=2, mat=K.M("alu_dark"),
                     loc=(-0.01, 0, zc + gh + 0.05), parent=g)
    K.empty(name + "_gate", (gx - 0.06, 0, zc), parent=root)
    K.empty(name + "_gate_top", (gx, 0, zc + gh / 2 + fr + 0.02), parent=root)
    # ---- the intake channel (glass trough from the gate to the core) with a light strand
    chan_m = K.light_mat(name + "_chan", K.SKY, 0.0)
    K.rbox(name + "_chanbed", (0.2, 0.12, 0.012), bevel=0.003, seg=2, mat=K.M("alu_dark"), loc=(-w / 2 + t + 0.1, 0, zc - 0.05), parent=root)
    K.rbox(name + "_chanstrip", (0.18, 0.008, 0.004), bevel=0.001, seg=1, mat=chan_m, loc=(-w / 2 + t + 0.1, 0, zc - 0.043), parent=root).visible_shadow = False
    # ---- the core (tool.py): an aluminium frame on standoffs, dark glass top, one light bar per line of code
    core = K.empty(name + "_coreroot", (-0.13, -0.03, zb + 0.03), parent=root)
    cw, cd = 0.5, 0.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.cyl(f"{name}_stand{sx}{sy}", 0.012, 0.03, K.M("alu"), loc=(sx * (cw / 2 - 0.02), sy * (cd / 2 - 0.02), -0.012), verts=16, parent=core)
    K.rbox(name + "_coreframe", (cw + 0.04, cd + 0.04, 0.026), bevel=0.007, seg=4, mat=K.M("alu"), loc=(0, 0, 0.012), parent=core)
    glassm = K.principled(name + "_coreglass", (0.012, 0.016, 0.024, 1), rough=0.1, coat=0.9, coat_rough=0.04)
    K.rbox(name + "_coreglass", (cw, cd, 0.014), bevel=0.003, seg=2, mat=glassm, loc=(0, 0, 0.031), parent=core)
    n = len(line_lengths)
    pitch = (cd - 0.03) / max(1, n)
    bars = []
    Lmax = max(line_lengths) or 1
    for i, L in enumerate(line_lengths):
        if L <= 0:
            bars.append(None)
            continue
        bl = (cw - 0.05) * min(1.0, L / Lmax)
        m = K.light_mat(f"{name}_bar{i}", K.SKY, 0.0)
        y = cd / 2 - 0.015 - (i + 0.5) * pitch
        o = K.rbox(f"{name}_bar{i}", (bl, pitch * 0.5, 0.003), bevel=0.001, seg=1, mat=m,
                   loc=(-cw / 2 + 0.025 + bl / 2, y, 0.0395), parent=core)
        o.visible_shadow = False
        bars.append(m)
    K.empty(name + "_core", (0, 0, 0.05), parent=core)
    core_world = Vector(loc) + Vector((-0.13, -0.03, zb + 0.03))
    # ---- four service ports on the back wall and the internal light tubes from the core to them
    ports, inner_tubes = [], []
    for j in range(4):
        x = -0.36 + j * 0.24
        pz = zb + h * 0.62
        pr = K.empty(f"{name}_portroot{j}", (x, d / 2 - t, pz), parent=root)
        K.cyl(f"{name}_portcol{j}", 0.04, 0.05, K.M("alu"), loc=(0, 0.02, 0), verts=40, bevel=0.004, parent=pr).rotation_euler = (math.pi / 2, 0, 0)
        K.cyl(f"{name}_portwell{j}", 0.027, 0.052, K.M("graphite"), loc=(0, 0.02, 0), verts=40, parent=pr).rotation_euler = (math.pi / 2, 0, 0)
        pm = K.light_mat(f"{name}_portring{j}", K.SKY, 0.0)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.033, minor_radius=0.0035, location=(0, 0, 0))
        tor = bpy.context.active_object
        tor.name = f"{name}_porttorus{j}"
        tor.data.materials.append(pm)
        tor.parent = pr
        tor.location = (0, -0.006, 0)
        tor.rotation_euler = (math.pi / 2, 0, 0)
        K.empty(f"{name}_port{j}", (0, 0.07, 0), parent=pr)
        K.empty(f"{name}_porti{j}", (0, -0.03, 0), parent=pr)
        ports.append(pm)
        # internal tube: from the core's back edge up to the port (world coords: this unit never moves while used)
        a = core_world + Vector((-0.18 + j * 0.12, cd / 2 + 0.02, 0.04))
        b = Vector(loc) + Vector((x, d / 2 - t - 0.035, pz))
        pts = cubic(a, a + Vector((0, 0.05, 0.0)), b + Vector((0, -0.08, 0)), b, n=24)
        tube, strand, sm = conduit(f"{name}_it{j}", pts, r=0.008)
        tube.parent = None
        inner_tubes.append((tube, strand, sm))
    # ---- the envelope tray (where the legacy replies land) and the output channel
    tray = K.empty(name + "_trayroot", (0.36, 0.02, zb + 0.004), parent=root)
    K.rbox(name + "_traybed", (0.2, 0.15, 0.012), bevel=0.004, seg=2, mat=K.M("alu_dark"), loc=(0, 0, 0.006), parent=tray)
    for sy in (-1, 1):
        K.rbox(f"{name}_traylip{sy}", (0.2, 0.008, 0.03), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, sy * 0.075, 0.015), parent=tray)
    K.empty(name + "_tray", (0, 0, 0.03), parent=tray)
    out_chan = K.light_mat(name + "_outchan", K.GREEN, 0.0)
    K.rbox(name + "_ochanbed", (0.2, 0.12, 0.012), bevel=0.003, seg=2, mat=K.M("alu_dark"), loc=(w / 2 - t - 0.1, -0.03 - 0.12, zc - 0.05), parent=root)
    K.rbox(name + "_ochanstrip", (0.18, 0.008, 0.004), bevel=0.001, seg=1, mat=out_chan, loc=(w / 2 - t - 0.1, -0.15, zc - 0.043), parent=root).visible_shadow = False
    # ---- output slot on the right face
    K.rbox(name + "_outbezel", (0.014, 0.3, 0.12), bevel=0.004, seg=3, mat=K.M("alu"), loc=(w / 2 + 0.004, 0, zc), parent=root)
    K.rbox(name + "_outslot", (0.018, 0.25, 0.07), bevel=0.003, seg=2, mat=K.M("shadowgap"), loc=(w / 2 + 0.005, 0, zc), parent=root)
    out_m = K.light_mat(name + "_outglow", K.GREEN, 0.0)
    K.rbox(name + "_outlight", (0.004, 0.24, 0.06), bevel=0.001, seg=1, mat=out_m, loc=(w / 2 + 0.0145, 0, zc), parent=root)
    K.empty(name + "_out", (w / 2 + 0.06, 0, zc), parent=root)
    # ---- the lid
    lid = K.empty(name + "_lid", (0, 0, zb + h + 0.014), parent=root)
    K.rbox(name + "_lidplate", (w + 0.02, d + 0.02, 0.024), bevel=0.01, seg=4, mat=K.M("alu"), loc=(0, 0, 0), parent=lid)
    K.rbox(name + "_lidinlay", (w * 0.7, d * 0.62, 0.006), bevel=0.003, seg=2, mat=K.M("graphite"), loc=(0, 0, 0.012), parent=lid)
    for k in range(7):
        K.rbox(f"{name}_lidvent{k}", (w * 0.6, 0.01, 0.004), bevel=0.0015, seg=1, mat=K.M("shadowgap"),
               loc=(0, -d * 0.24 + k * d * 0.08, 0.0155), parent=lid)
    K.empty(name + "_lid_pin", (0, -d / 2, 0.03), parent=lid)
    K.empty(name + "_top", (0, -d / 2, zb + h + 0.06), parent=root)
    ld = bpy.data.lights.new(name + "_inner", "AREA")
    ld.energy, ld.size, ld.color, ld.shape = 0.0, 0.8, (0.7, 0.82, 1.0), "DISK"
    lo = bpy.data.objects.new(name + "_inner", ld)
    bpy.context.collection.objects.link(lo)
    lo.parent = root
    lo.location = (0, 0, zb + h - 0.02)
    lo.visible_glossy = False
    return {"root": root, "gate": g, "ring_ok": ring_ok, "ring_no": ring_no, "ring_idle": ring_idle, "scan": scan,
            "scan_m": scan_m, "shutter": shutter, "shutter_up": Vector(shutter.location), "shutter_down": Vector((-0.01, 0, zc)),
            "bars": bars, "ports": ports, "inner_tubes": inner_tubes, "out": out_m, "out_chan": out_chan, "chan": chan_m,
            "lid": lid, "led": led, "inner": lo, "zc": zc, "w": w, "d": d, "h": h, "core": core,
            "tray_world": Vector(loc) + Vector((0.36, 0.02, zb + 0.034))}


def small_tool(name, loc, line_lengths, s=0.3):
    """A closed tool unit for the toolbox row (no internal tubes): housing, smoked window, gate ring, LED, and the
    core's bars visible through the window. Built at full size and scaled by s around loc."""
    root = K.empty(name, loc)
    w, d, h, t, zb = 1.2, 0.62, 0.3, 0.028, 0.035
    K.rbox(name + "_base", (w + 0.07, d + 0.07, zb), bevel=0.012, seg=3, mat=K.M("alu_dark"), loc=(0, 0, zb / 2), parent=root)
    K.rbox(name + "_body", (w, d, h), bevel=0.01, seg=3, mat=K.M("alu"), loc=(0, 0, zb + h / 2), parent=root)
    K.rbox(name + "_win", (w - 0.06, 0.008, h * 0.5), bevel=0.003, seg=2, mat=P_smoked_light(), loc=(0, -d / 2 - 0.003, zb + h * 0.64), parent=root)
    K.rbox(name + "_lidplate", (w + 0.02, d + 0.02, 0.024), bevel=0.01, seg=3, mat=K.M("alu"), loc=(0, 0, zb + h + 0.012), parent=root)
    led = K.glow_mat(name + "_led", K.SKY, 0.3)
    K.rbox(name + "_ledbar", (w * 0.62, 0.006, 0.008), bevel=0.002, seg=2, mat=led, loc=(0, -d / 2 - 0.004, zb + 0.05), parent=root)
    ring = K.light_mat(name + "_ring", K.SKY, 0.6)
    K.rbox(name + "_gatering", (0.01, 0.3, 0.2), bevel=0.004, seg=2, mat=ring, loc=(-w / 2 - 0.006, 0, zb + 0.11), parent=root)
    # the bars, seen through the window (one per real line of this tool's tool.py)
    Lmax = max(line_lengths) or 1
    n = len(line_lengths)
    barm = K.light_mat(name + "_bars", K.SKY, 0.0)
    rows = min(n, 40)
    for i in range(rows):
        L = line_lengths[i]
        if L <= 0:
            continue
        bl = (w - 0.2) * min(1.0, L / Lmax)
        K.rbox(f"{name}_b{i}", (bl, 0.003, (h * 0.42) / rows * 0.5), bevel=0.0, seg=1, mat=barm,
               loc=(-(w - 0.2) / 2 + bl / 2, -d / 2 + 0.004, zb + h * 0.86 - (i + 0.5) * (h * 0.42) / rows), parent=root).visible_shadow = False
    K.empty(name + "_top", (0, -d / 2, zb + h + 0.08), parent=root)
    root.scale = (s, s, s)
    return {"root": root, "led": led, "ring": ring, "bars": barm}


def P_smoked_light():
    return _mat_once("smoked_light", lambda: K.principled("smoked_light", (0.25, 0.28, 0.33, 1), rough=0.06, transmission=0.85, ior=1.5))


# ------------------------------------------------------------------------------------------------ legacy Ledgerline
def cabinet(name, loc, w=0.5, d=0.46, h=1.15, lamps=5):
    """A 1998 Ledgerline service cabinet: warm-grey enamel body on a black plinth, a charcoal front with a drive bay,
    a smoked window with two tape reels, a row of amber status lamps (keyable `lamp`), a green ready lamp (`ok`), a fault
    beacon on top (`fault`, ember) and a service port at z ~ 0.55. Pins: <name>_top, <name>_port, <name>_face."""
    root = K.empty(name, loc)
    K.rbox(name + "_plinth", (w - 0.02, d - 0.02, 0.06), bevel=0.006, seg=2, mat=K.M("graphite"), loc=(0, 0, 0.03), parent=root)
    K.rbox(name + "_body", (w, d, h - 0.08), bevel=0.012, seg=4, mat=enamel(), loc=(0, 0, 0.06 + (h - 0.08) / 2), parent=root)
    K.rbox(name + "_cap", (w + 0.02, d + 0.02, 0.03), bevel=0.01, seg=4, mat=enamel(), loc=(0, 0, h - 0.005), parent=root)
    for sx in (-1, 1):   # side seams
        K.rbox(f"{name}_seam{sx}", (0.004, d * 0.9, h - 0.2), bevel=0.001, seg=1, mat=K.M("shadowgap"), loc=(sx * (w / 2 + 0.0005), 0.0, 0.06 + (h - 0.08) / 2), parent=root)
    pnl = _mat_once("panel_dark", lambda: K.anod("panel_dark", (0.03, 0.031, 0.034, 1), rough=0.5))
    fy = -d / 2 - 0.004
    K.rbox(name + "_front", (w - 0.07, 0.012, h - 0.22), bevel=0.006, seg=3, mat=pnl, loc=(0, fy, 0.06 + (h - 0.08) / 2 + 0.02), parent=root)
    louv = _mat_once("louvre", lambda: K.principled("louvre", (0.16, 0.16, 0.17, 1), rough=0.45, metallic=0.6))
    for k in range(9):
        K.rbox(f"{name}_louv{k}", (w - 0.17, 0.016, 0.009), bevel=0.003, seg=2, mat=louv, loc=(0, fy - 0.007, 0.15 + k * 0.021), parent=root)
    # drive bay: two dark slots with eject buttons
    for k in range(2):
        z = 0.42 + k * 0.045
        K.rbox(f"{name}_bay{k}", (w - 0.2, 0.014, 0.032), bevel=0.004, seg=2, mat=louv, loc=(0, fy - 0.006, z), parent=root)
        K.rbox(f"{name}_slot{k}", (w * 0.42, 0.016, 0.006), bevel=0.001, seg=1, mat=K.M("shadowgap"), loc=(-0.03, fy - 0.008, z), parent=root)
        K.cyl(f"{name}_ej{k}", 0.006, 0.01, K.M("alu"), loc=(w / 2 - 0.13, fy - 0.012, z), verts=16, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    wz = 0.06 + (h - 0.08) * 0.74
    K.rbox(name + "_winframe", (w - 0.14, 0.016, 0.22), bevel=0.005, seg=3, mat=K.M("alu_dark"), loc=(0, fy - 0.004, wz), parent=root)
    K.rbox(name + "_win", (w - 0.18, 0.006, 0.18), bevel=0.003, seg=2, mat=smoked(), loc=(0, fy - 0.011, wz), parent=root)
    for sx in (-1, 1):
        r = K.cyl(f"{name}_reel{sx}", 0.065, 0.01, K.M("alu"), loc=(sx * 0.085, fy + 0.006, wz), verts=48, parent=root)
        r.rotation_euler = (math.pi / 2, 0, 0)
        hub = K.cyl(f"{name}_hub{sx}", 0.022, 0.014, K.M("graphite"), loc=(sx * 0.085, fy + 0.002, wz), verts=32, parent=root)
        hub.rotation_euler = (math.pi / 2, 0, 0)
    lamp = K.glow_mat(name + "_lamp", lin_amber(), 0.25, base=(0.06, 0.035, 0.015, 1))
    ok = K.glow_mat(name + "_ok", K.GREEN, 0.0, base=(0.02, 0.05, 0.03, 1))
    lz = wz - 0.165
    for k in range(lamps):
        x = (k - (lamps - 1) / 2) * 0.05
        m = ok if k == lamps - 1 else lamp
        K.cyl(f"{name}_lampb{k}", 0.012, 0.01, K.M("alu"), loc=(x, fy - 0.006, lz), verts=24, parent=root).rotation_euler = (math.pi / 2, 0, 0)
        K.cyl(f"{name}_lamp{k}", 0.008, 0.012, m, loc=(x, fy - 0.009, lz), verts=24, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    fault = K.glow_mat(name + "_fault", K.EMBER, 0.0, base=(0.1, 0.03, 0.02, 1))
    K.cyl(name + "_beaconbase", 0.03, 0.016, K.M("alu_dark"), loc=(w / 2 - 0.08, 0, h + 0.018), verts=32, parent=root)
    K.cyl(name + "_beacon", 0.022, 0.04, fault, loc=(w / 2 - 0.08, 0, h + 0.045), verts=32, bevel=0.006, parent=root)
    pz = 0.55
    K.cyl(name + "_portcol", 0.042, 0.03, K.M("alu"), loc=(0, fy - 0.012, pz + 0.12), verts=40, bevel=0.003, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    K.cyl(name + "_portwell", 0.028, 0.032, K.M("graphite"), loc=(0, fy - 0.012, pz + 0.12), verts=40, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    K.rbox(name + "_plate", (w * 0.6, 0.008, 0.045), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, fy - 0.004, h - 0.09), parent=root)
    K.empty(name + "_top", (0, fy, h + 0.08), parent=root)
    K.empty(name + "_port", (0, fy - 0.03, pz + 0.12), parent=root)
    K.empty(name + "_face", (0, fy - 0.01, wz), parent=root)
    return {"root": root, "lamp": lamp, "ok": ok, "fault": fault, "port_z": pz + 0.12}


def lin_amber():
    return K.lin("#e0902c")


# ------------------------------------------------------------------------------------------------ travellers
def capsule(name, loc, color=K.SKY, size=(0.17, 0.08, 0.06)):
    """A request capsule: clear glass body around a light core (keyable 'glow' on the returned material), aluminium end
    caps. Long axis along x. Pins: <name>_top, <name>_mid."""
    root = K.empty(name, loc)
    L, W, H = size
    K.rbox(name + "_glass", (L, W, H), bevel=0.02, seg=5, mat=K.M("glass"), loc=(0, 0, 0), parent=root)
    core = K.light_mat(name + "_core", color, 2.0)
    c = K.rbox(name + "_corebar", (L * 0.7, W * 0.42, H * 0.36), bevel=0.008, seg=3, mat=core, loc=(0, 0, 0), parent=root)
    c.visible_shadow = False
    for sx in (-1, 1):
        K.rbox(f"{name}_cap{sx}", (0.018, W + 0.008, H + 0.008), bevel=0.006, seg=3, mat=K.M("alu"), loc=(sx * (L / 2 + 0.004), 0, 0), parent=root)
    K.empty(name + "_top", (0, 0, H / 2 + 0.02), parent=root)
    K.empty(name + "_mid", (0, -W / 2, 0), parent=root)
    return root, core


def envelope(name, loc, color=K.EMBER, size=(0.12, 0.075, 0.022)):
    """A legacy reply envelope: an enamel card with a glowing stripe (keyable 'glow' on the returned material)."""
    root = K.empty(name, loc)
    L, W, H = size
    K.rbox(name + "_body", (L, W, H), bevel=0.006, seg=3, mat=enamel(), loc=(0, 0, 0), parent=root)
    st = K.glow_mat(name + "_stripe", color, 1.6, base=(0.08, 0.04, 0.03, 1))
    K.rbox(name + "_stripe", (L * 0.86, 0.01, H * 0.4), bevel=0.002, seg=1, mat=st, loc=(0, -W / 2 - 0.002, 0), parent=root)
    K.rbox(name + "_stripe2", (L * 0.86, W * 0.25, 0.003), bevel=0.001, seg=1, mat=st, loc=(0, 0, H / 2 + 0.0005), parent=root)
    K.empty(name + "_top", (0, 0, H / 2 + 0.015), parent=root)
    return root, st


def result_slab(name, loc, color=K.GREEN, size=(0.26, 0.16, 0.035)):
    """The clean result: a frosted glass slab with glowing edge strips (keyable 'glow' on the returned material)."""
    root = K.empty(name, loc)
    L, W, H = size
    K.rbox(name + "_glass", (L, W, H), bevel=0.01, seg=4, mat=K.M("frost"), loc=(0, 0, 0), parent=root)
    m = K.light_mat(name + "_edge", color, 2.4)
    for nm, sz, lc in (("_e1", (L * 0.92, 0.006, 0.006), (0, -W / 2 - 0.001, H / 2 - 0.006)),
                       ("_e2", (L * 0.92, 0.006, 0.006), (0, W / 2 + 0.001, H / 2 - 0.006)),
                       ("_e3", (0.006, W * 0.86, 0.006), (-L / 2 - 0.001, 0, H / 2 - 0.006)),
                       ("_e4", (0.006, W * 0.86, 0.006), (L / 2 + 0.001, 0, H / 2 - 0.006))):
        K.rbox(name + nm, sz, bevel=0.002, seg=1, mat=m, loc=lc, parent=root).visible_shadow = False
    inner = K.light_mat(name + "_inner", color, 0.6)
    K.rbox(name + "_innerbar", (L * 0.6, W * 0.5, H * 0.3), bevel=0.006, seg=2, mat=inner, loc=(0, 0, 0), parent=root).visible_shadow = False
    K.empty(name + "_top", (0, 0, H / 2 + 0.02), parent=root)
    K.empty(name + "_mid", (0, -W / 2, 0), parent=root)
    return root, m, inner


def cubic(a, b, c, d, n=48):
    a, b, c, d = Vector(a), Vector(b), Vector(c), Vector(d)
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1 - t) ** 3) * a + 3 * ((1 - t) ** 2) * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d)
    return out


def conduit(name, pts, r=0.016, glass=True):
    """A glass tube along the polyline `pts` with a light strand inside. Returns (tube, strand_obj, strand_mat).
    Grow the strand (or a pulse) with K.grow(strand, keys)."""
    def curve(nm, rad, mat):
        cu = bpy.data.curves.new(nm, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = rad
        cu.bevel_resolution = 4
        cu.use_fill_caps = True
        cu.bevel_factor_mapping_end = "SPLINE"
        cu.bevel_factor_mapping_start = "SPLINE"
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, c in zip(sp.points, pts):
            p.co = (c[0], c[1], c[2], 1.0)
        o = bpy.data.objects.new(nm, cu)
        bpy.context.collection.objects.link(o)
        cu.materials.append(mat)
        return o
    tube = curve(name + "_tube", r, K.M("glass") if glass else K.M("alu_dark"))
    tube.visible_shadow = False
    sm = K.light_mat(name + "_strand", K.SKY, 0.0)
    strand = curve(name + "_strand", r * 0.22, sm)
    strand.visible_shadow = False
    return tube, strand, sm


def travel(obj, pts, f0, f1, ease=True):
    """Key obj.location along the polyline pts from frame f0 to f1 (one key every ~2 frames, smoothstep timing)."""
    pts = [Vector(p) for p in pts]
    seg = [0.0]
    for a, b in zip(pts, pts[1:]):
        seg.append(seg[-1] + (b - a).length)
    total = seg[-1] or 1.0
    n = max(2, (f1 - f0) // 2)
    keys = []
    for i in range(n + 1):
        u = i / n
        if ease:
            u = u * u * (3 - 2 * u)
        s = u * total
        j = max(0, min(len(pts) - 2, next((k for k in range(len(seg) - 1) if seg[k + 1] >= s), len(pts) - 2)))
        lu = (s - seg[j]) / max(1e-9, seg[j + 1] - seg[j])
        keys.append((int(round(f0 + (f1 - f0) * i / n)), pts[j].lerp(pts[j + 1], lu)))
    K.key(obj, "location", keys)
    # keep these keys linear (the smoothstep is already in the sampling)
    return keys


# ------------------------------------------------------------------------------------------------ the wall and what hides behind it
def wall(name, loc, w=2.6, h=1.6, t=0.06, slot=(0.34, 0.12), slot_z=0.3):
    """A tall matte-black partition in a brushed frame, standing across x (faces -x / +x), with one slot at slot_z.
    Keyable edge light around the slot (returned material). Pins: <name>_slot, <name>_top."""
    root = K.empty(name, loc)
    blk = K.principled(name + "_matte", (0.01, 0.011, 0.014, 1), rough=0.7)
    sw, sh = slot
    # panel in four pieces around the slot
    K.rbox(name + "_lower", (t, w, slot_z - sh / 2), bevel=0.004, seg=2, mat=blk, loc=(0, 0, (slot_z - sh / 2) / 2), parent=root)
    top_h = h - (slot_z + sh / 2)
    K.rbox(name + "_upper", (t, w, top_h), bevel=0.004, seg=2, mat=blk, loc=(0, 0, slot_z + sh / 2 + top_h / 2), parent=root)
    side = (w - sw) / 2
    for sy in (-1, 1):
        K.rbox(f"{name}_side{sy}", (t, side, sh), bevel=0.002, seg=1, mat=blk, loc=(0, sy * (sw / 2 + side / 2), slot_z), parent=root)
    fr = 0.03
    for nm, sz, lc in (("_ft", (t + 0.02, w + 2 * fr, fr), (0, 0, h + fr / 2)),
                       ("_fl", (t + 0.02, fr, h), (0, -w / 2 - fr / 2, h / 2)), ("_fr", (t + 0.02, fr, h), (0, w / 2 + fr / 2, h / 2))):
        K.rbox(name + nm, sz, bevel=0.006, seg=3, mat=K.M("alu"), loc=lc, parent=root)
    em = K.light_mat(name + "_slotlight", K.GREEN, 0.0)
    for k, (sz, lc) in enumerate((((t + 0.006, sw, 0.006), (0, 0, slot_z + sh / 2)), ((t + 0.006, sw, 0.006), (0, 0, slot_z - sh / 2)),
                                  ((t + 0.006, 0.006, sh), (0, -sw / 2, slot_z)), ((t + 0.006, 0.006, sh), (0, sw / 2, slot_z)))):
        K.rbox(f"{name}_sl{k}", sz, bevel=0.001, seg=1, mat=em, loc=lc, parent=root).visible_shadow = False
    # brushed ribs and a waist band on both faces, so the wall reads as a machined partition, not a flat card
    for side in (-1, 1):
        for k in range(9):
            y = -w / 2 + (k + 0.5) * w / 9
            if abs(y) < sw / 2 + 0.06:
                continue
            K.rbox(f"{name}_rib{side}_{k}", (0.012, 0.022, h - 0.06), bevel=0.004, seg=2, mat=K.M("alu_dark"),
                   loc=(side * (t / 2 + 0.006), y, h / 2), parent=root)
        K.rbox(f"{name}_band{side}", (0.014, w, 0.04), bevel=0.005, seg=2, mat=K.M("alu"), loc=(side * (t / 2 + 0.007), 0, slot_z + sh / 2 + 0.12), parent=root)
        K.rbox(f"{name}_kick{side}", (0.014, w, 0.06), bevel=0.005, seg=2, mat=K.M("alu_dark"), loc=(side * (t / 2 + 0.007), 0, 0.03), parent=root)
        K.rbox(f"{name}_slotbez{side}", (0.016, sw + 0.06, sh + 0.06), bevel=0.006, seg=3, mat=K.M("alu"), loc=(side * (t / 2 + 0.008), 0, slot_z), parent=root)
    K.empty(name + "_slot", (0, 0, slot_z), parent=root)
    K.empty(name + "_top", (0, 0, h + 0.05), parent=root)
    return root, em


def database(name, loc, r=0.16, n=3):
    """A stack of machined disk platters (the database): graphite drums with aluminium rims and a status light."""
    root = K.empty(name, loc)
    lt = K.glow_mat(name + "_light", K.SKY, 0.0)
    for k in range(n):
        z = 0.06 + k * 0.1
        K.cyl(f"{name}_drum{k}", r, 0.085, K.M("graphite"), loc=(0, 0, z), verts=64, bevel=0.01, parent=root)
        K.cyl(f"{name}_rim{k}", r + 0.004, 0.012, K.M("alu"), loc=(0, 0, z + 0.036), verts=64, bevel=0.003, parent=root)
        K.rbox(f"{name}_led{k}", (0.05, 0.006, 0.008), bevel=0.002, seg=1, mat=lt, loc=(0, -r - 0.002, z), parent=root)
    K.empty(name + "_top", (0, 0, 0.06 + n * 0.1 + 0.03), parent=root)
    return root, lt


def badge(name, loc):
    """Emma's session: a key card (enamel-white card, gold contact chip, sky stripe) on a small stand."""
    root = K.empty(name, loc)
    card_m = K.principled(name + "_card", (0.82, 0.83, 0.85, 1), rough=0.35, coat=0.4)
    gold = K.principled(name + "_gold", (0.85, 0.68, 0.35, 1), rough=0.25, metallic=1.0)
    stripe = K.glow_mat(name + "_stripe", K.SKY, 0.0, base=(0.1, 0.25, 0.6, 1))
    st = K.empty(name + "_tilt", (0, 0, 0.02), parent=root)
    st.rotation_euler = (math.radians(-72), 0, 0)
    K.rbox(name + "_card", (0.17, 0.004, 0.11), bevel=0.003, seg=3, mat=card_m, loc=(0, 0, 0.055), parent=st)
    K.rbox(name + "_chip", (0.03, 0.002, 0.024), bevel=0.002, seg=2, mat=gold, loc=(-0.045, -0.003, 0.06), parent=st)
    K.rbox(name + "_stripe", (0.17, 0.002, 0.018), bevel=0.001, seg=1, mat=stripe, loc=(0, -0.003, 0.02), parent=st)
    K.rbox(name + "_stand", (0.2, 0.06, 0.02), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(0, 0, 0.01), parent=root)
    K.empty(name + "_top", (0, 0, 0.16), parent=root)
    return root, stripe


def padlock(name, loc, s=1.0):
    """Emma's password: a machined padlock (aluminium body, steel shackle)."""
    root = K.empty(name, loc)
    K.rbox(name + "_body", (0.12 * s, 0.05 * s, 0.1 * s), bevel=0.012 * s, seg=4, mat=K.M("alu"), loc=(0, 0, 0.05 * s), parent=root)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.04 * s, minor_radius=0.009 * s, location=(0, 0, 0))
    tor = bpy.context.active_object
    tor.name = name + "_shackle"
    tor.data.materials.append(K.M("alu_dark"))
    tor.parent = root
    tor.location = (0, 0, 0.1 * s)
    tor.rotation_euler = (math.pi / 2, 0, 0)
    K.cyl(name + "_keyhole", 0.009 * s, 0.006, K.M("graphite"), loc=(0, -0.026 * s, 0.055 * s), verts=20, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    K.empty(name + "_top", (0, 0, 0.17 * s), parent=root)
    return root


def rail(name, x0, x1, y, z, gap=0.05):
    """An aluminium two-rod rail on a graphite bed along x at height z (the lane capsules slide on)."""
    L = x1 - x0
    root = K.empty(name, ((x0 + x1) / 2, y, z))
    K.rbox(name + "_bed", (L, gap + 0.05, 0.016), bevel=0.005, seg=3, mat=K.M("graphite"), loc=(0, 0, -0.045), parent=root)
    for sy in (-1, 1):
        r = K.cyl(f"{name}_rod{sy}", 0.006, L, K.M("alu"), loc=(0, sy * gap / 2, -0.034), verts=16, parent=root)
        r.rotation_euler = (0, math.pi / 2, 0)
    for k in range(int(L / 0.25) + 1):
        K.rbox(f"{name}_tie{k}", (0.014, gap + 0.03, 0.01), bevel=0.003, seg=2, mat=K.M("alu_dark"), loc=(-L / 2 + k * 0.25, 0, -0.04), parent=root)
    return root


# ------------------------------------------------------------------------------------------------ the context window (film 2)
PART_COL = {"system": "#8a97ab", "defs": "#9a5cff", "user": "#3c90ff", "call": "#7fb2ff", "result": "#1e8e5a", "reply": "#bcd6ff"}


def part_slab(name, loc, size, kind, glow=0.0):
    """One part of the context as a physical slab: frosted glass body, a glowing band in the part's colour around its
    upper edge and a faint inner core. Bottom at loc.z, height = size[2]. Returns (root, edge_mat, core_mat)."""
    root = K.empty(name, loc)
    w, d, h = size
    c = K.lin(PART_COL[kind])
    body = _mat_once("slab_frost", lambda: K.principled("slab_frost", (0.9, 0.93, 0.98, 1), rough=0.3, transmission=0.92, ior=1.45))
    K.rbox(name + "_body", (w, d, max(0.004, h - 0.002)), bevel=min(0.006, h * 0.3), seg=3, mat=body, loc=(0, 0, h / 2), parent=root)
    em = K.light_mat(name + "_edge", c, glow)
    t = min(0.006, max(0.002, h * 0.35))
    zt = h - t / 2 - 0.0005
    for nm, sz, lc in (("_e1", (w * 0.985, 0.004, t), (0, -d / 2 - 0.0008, zt)), ("_e2", (w * 0.985, 0.004, t), (0, d / 2 + 0.0008, zt)),
                       ("_e3", (0.004, d * 0.985, t), (-w / 2 - 0.0008, 0, zt)), ("_e4", (0.004, d * 0.985, t), (w / 2 + 0.0008, 0, zt))):
        K.rbox(name + nm, sz, bevel=0.001, seg=1, mat=em, loc=lc, parent=root).visible_shadow = False
    core = K.light_mat(name + "_core", c, glow * 0.25)
    if h > 0.012:
        K.rbox(name + "_corebar", (w * 0.8, d * 0.7, h * 0.7), bevel=min(0.004, h * 0.2), seg=2, mat=core, loc=(0, 0, h / 2), parent=root).visible_shadow = False
    K.empty(name + "_r", (w / 2 + 0.01, -d / 2, h / 2), parent=root)    # right-front edge, mid height (label anchor)
    K.empty(name + "_l", (-w / 2 - 0.01, -d / 2, h / 2), parent=root)
    K.empty(name + "_top", (0, -d / 2, h), parent=root)
    return root, em, core


def context_case(name, loc, w=0.6, d=0.44, h=1.3, ticks=13):
    """The context window as a tall glass vitrine on a machined base: brushed corner posts, glass panes, a top cap,
    tick marks every 0.1 m on the front-left post (100 tokens at 1 mm per token), and a reading scan plane (keyable
    location z and 'glow'). Inner floor at loc.z + 0.05. Returns dict(root, scan, scan_m, floor_z)."""
    root = K.empty(name, loc)
    K.rbox(name + "_base", (w + 0.12, d + 0.12, 0.05), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.025), parent=root)
    K.rbox(name + "_basetrim", (w + 0.124, 0.008, 0.01), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.06, 0.042), parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rbox(f"{name}_post{sx}{sy}", (0.026, 0.026, h), bevel=0.006, seg=3, mat=K.M("alu"), loc=(sx * (w / 2 + 0.013), sy * (d / 2 + 0.013), 0.05 + h / 2), parent=root)
    for nm, sz, lc in (("_pf", (w, 0.006, h), (0, -d / 2 - 0.004, 0.05 + h / 2)), ("_pb", (w, 0.006, h), (0, d / 2 + 0.004, 0.05 + h / 2)),
                       ("_pl", (0.006, d, h), (-w / 2 - 0.004, 0, 0.05 + h / 2)), ("_pr", (0.006, d, h), (w / 2 + 0.004, 0, 0.05 + h / 2))):
        o = K.rbox(name + nm, sz, bevel=0.002, seg=1, mat=K.M("glass"), loc=lc, parent=root)
        o.visible_shadow = False
    K.rbox(name + "_cap", (w + 0.08, d + 0.08, 0.035), bevel=0.01, seg=4, mat=K.M("alu"), loc=(0, 0, 0.05 + h + 0.0175), parent=root)
    led = K.glow_mat(name + "_capled", K.SKY, 0.6)
    K.rbox(name + "_capledbar", (w * 0.7, 0.006, 0.008), bevel=0.002, seg=1, mat=led, loc=(0, -d / 2 - 0.041, 0.05 + h + 0.0175), parent=root)
    for k in range(ticks):
        z = 0.05 + k * 0.1
        K.rbox(f"{name}_tick{k}", (0.03 if k % 5 == 0 else 0.018, 0.004, 0.003), bevel=0.0, seg=1, mat=K.M("tick"),
               loc=(-w / 2 - 0.04, -d / 2 - 0.03, z), parent=root)
    scan_m = K.light_mat(name + "_scan", K.SKY, 0.0)
    scan = K.rbox(name + "_scanplane", (w - 0.01, d - 0.01, 0.003), bevel=0.0, seg=1, mat=scan_m, loc=(0, 0, 0.05), parent=root)
    scan.visible_shadow = False
    K.empty(name + "_top", (0, -d / 2, 0.05 + h + 0.06), parent=root)
    K.empty(name + "_base_pin", (w / 2 + 0.06, -d / 2 - 0.06, 0.05), parent=root)
    return {"root": root, "scan": scan, "scan_m": scan_m, "floor_z": loc[2] + 0.05, "led": led}


def booth(name, x0, x1, y0, y1, h=1.75):
    """A dark booth behind the wall: matte black side, back and roof; the front (y0) is dark smoked glass, so the
    camera can just see inside. Returns the root."""
    root = K.empty(name, ((x0 + x1) / 2, (y0 + y1) / 2, 0))
    blk = _mat_once("booth_matte", lambda: K.principled("booth_matte", (0.008, 0.009, 0.012, 1), rough=0.75))
    W, D = x1 - x0, y1 - y0
    K.rbox(name + "_roof", (W + 0.04, D + 0.04, 0.04), bevel=0.006, seg=2, mat=blk, loc=(0, 0, h + 0.02), parent=root)
    K.rbox(name + "_back", (W, 0.04, h), bevel=0.004, seg=2, mat=blk, loc=(0, D / 2, h / 2), parent=root)
    K.rbox(name + "_side", (0.04, D, h), bevel=0.004, seg=2, mat=blk, loc=(W / 2, 0, h / 2), parent=root)
    glass = _mat_once("booth_glass", lambda: K.principled("booth_glass", (0.16, 0.18, 0.22, 1), rough=0.04, transmission=0.93, ior=1.5))
    K.rbox(name + "_front", (W, 0.012, h), bevel=0.003, seg=2, mat=glass, loc=(0, -D / 2, h / 2), parent=root)
    for k, x in enumerate((-W / 2, W / 2)):
        K.rbox(f"{name}_mull{k}", (0.03, 0.03, h + 0.04), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(x, -D / 2, (h + 0.04) / 2), parent=root)
    K.rbox(name + "_header", (W + 0.03, 0.03, 0.05), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(0, -D / 2, h + 0.0), parent=root)
    return root
