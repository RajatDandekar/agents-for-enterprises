"""Props for the L2 films s7_loop, s8_weights, s9_fix and the overture (on top of l2kit).

  tower2      the 24-floor block stack with ONE light material per floor, so a pass can climb it floor by floor
  plaque      a Ledgerline fact plaque: dark slab, green glowing edge (green = facts)
  socket      a machined round socket with a glowing ring (Knowledge, Tools)
  drop_tile   a token tile that drops into place with its face lit (ember for invented digits)
  ribbon      a glowing ribbon tube along a polyline (the loss curve)
  set_face    re-colour a tile's face glow
"""
import math

import bpy
from mathutils import Vector

import l2kit as K

K.ROLE.setdefault("answer", K.lin("#3c90ff"))
K.ROLE.setdefault("digit", K.lin("#c4511f"))
K.ROLE.setdefault("fact", K.lin("#1e8e5a"))


def set_face(face_m, color):
    K.bsdf(face_m).inputs["Emission Color"].default_value = color


def tower2(name, loc, floors=24, pitch=0.075, w=1.5, d=0.56, heads=14, cells=None):
    """Like K.tower, but each floor's head LEDs share one material of their own: out["led"][k] (1-based), keyable
    'glow'. cells: optional {k: material} to put a cell plate face on the front edge of floor k (s8 weights)."""
    root = K.empty(name, loc)
    out = {"root": root, "floors": [], "led": {}, "posts": []}
    sp = w * 0.9 / heads
    for k in range(1, floors + 1):
        fr = K.empty(f"{name}_f{k}", (0, 0, (k - 1) * pitch), parent=root)
        K.rbox(f"{name}_f{k}_slab", (w, d, 0.024), bevel=0.007, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.012), parent=fr)
        K.rbox(f"{name}_f{k}_edge", (w + 0.004, 0.006, 0.006), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -d / 2, 0.019), parent=fr)
        led = K.glow_mat(f"{name}_f{k}_led", K.SKY, 0.0)
        out["led"][k] = led
        for j in range(heads):
            x = (j - (heads - 1) / 2) * sp
            K.rbox(f"{name}_f{k}_h{j}", (sp * 0.72, d * 0.55, 0.028), bevel=0.006, seg=3, mat=K.M("graphite"),
                   loc=(x, 0, 0.024 + 0.014), parent=fr)
            K.rbox(f"{name}_f{k}_h{j}_led", (sp * 0.5, 0.012, 0.006), bevel=0.002, seg=2, mat=led,
                   loc=(x, -d * 0.275 - 0.004, 0.024 + 0.021), parent=fr)
        if cells and k in cells:
            K.plane(f"{name}_f{k}_cells", w * 0.92, pitch * 0.62, cells[k], loc=(0, -d / 2 - 0.012, 0.012 + pitch * 0.31), parent=fr)
        K.empty(f"{name}_pin_f{k}", (w / 2 + 0.05, -d / 2, 0.02), parent=fr)
        K.empty(f"{name}_pinl_f{k}", (-w / 2 - 0.05, -d / 2, 0.02), parent=fr)
        out["floors"].append(fr)
    H = (floors - 1) * pitch + 0.07
    for sx in (-1, 1):
        for sy in (-1, 1):
            out["posts"].append(K.cyl(f"{name}_post{sx}{sy}", 0.016, H + 0.08, K.M("alu"),
                                      loc=(sx * (w / 2 + 0.03), sy * (d / 2 - 0.05), H / 2), verts=24, parent=root))
    return out


def pulse(tw, f0, per_floor=2, peak=3.0, base=0.25, hold=6):
    """A pass climbing the stack: each floor's LEDs flash in turn from floor 1 to 24 starting at f0."""
    for k, m in tw["led"].items():
        t = f0 + (k - 1) * per_floor
        K.glow_keys(m, [(t - 1, base), (t + 2, peak), (t + 2 + hold, base)])


def plaque(name, loc, w=0.62, h=0.2, d=0.04, color=K.GREEN, glow=0.0):
    """A Ledgerline fact plaque: graphite slab in an aluminium bezel with a glowing edge strip (keyable)."""
    root = K.empty(name, loc)
    K.rbox(name + "_body", (w, d, h), bevel=0.01, seg=4, mat=K.M("graphite"), loc=(0, 0, h / 2), parent=root)
    K.rbox(name + "_bezel", (w + 0.02, d * 0.6, h + 0.02), bevel=0.008, seg=4, mat=K.M("alu"), loc=(0, d * 0.35, h / 2), parent=root)
    m = K.glow_mat(name + "_glow", color, glow)
    K.rbox(name + "_strip", (w * 0.9, 0.006, 0.012), bevel=0.003, seg=2, mat=m, loc=(0, -d / 2 - 0.002, 0.025), parent=root)
    K.rbox(name + "_strip2", (w * 0.9, 0.006, 0.006), bevel=0.002, seg=2, mat=m, loc=(0, -d / 2 - 0.002, h - 0.02), parent=root)
    K.empty(name + "_top", (0, -d / 2, h + 0.02), parent=root)
    K.empty(name + "_mid", (0, -d / 2 - 0.01, h / 2), parent=root)
    return root, m


def socket(name, loc, r=0.16, color=K.SKY):
    """A machined socket on the plinth: brushed aluminium collar, dark well, glowing ring (keyable)."""
    root = K.empty(name, loc)
    K.cyl(name + "_collar", r, 0.05, K.M("alu"), loc=(0, 0, 0.025), verts=64, bevel=0.006, parent=root)
    K.cyl(name + "_well", r * 0.72, 0.052, K.M("graphite"), loc=(0, 0, 0.027), verts=64, parent=root)
    m = K.glow_mat(name + "_ring", color, 0.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=r * 0.82, minor_radius=0.008, location=(0, 0, 0.052))
    ring = bpy.context.active_object
    ring.name = name + "_ringobj"
    ring.data.materials.append(m)
    ring.parent = root
    ring.location = (0, 0, 0.052)
    for k in range(8):
        a = 2 * math.pi * k / 8
        K.cyl(f"{name}_bolt{k}", 0.007, 0.006, K.M("alu_dark"), loc=(math.cos(a) * r * 0.92, math.sin(a) * r * 0.92, 0.052),
              verts=16, parent=root)
    K.empty(name + "_top", (0, 0, 0.1), parent=root)
    return root, m


def drop_tile(name, role, loc, f0, dur=14, height=0.45, face_color=None, face_peak=2.0, face_rest=0.15, end=None, size=None):
    """A tile that drops into loc at frame f0 (lands at f0+dur) with its face flashing, then resting lit."""
    root, fm = K.token_tile(name, role, loc, size=size) if size else K.token_tile(name, role, loc)
    if face_color is not None:
        set_face(fm, face_color)
    lo = Vector(loc)
    hi = lo + Vector((0, 0, height))
    K.show(root, [(0, False), (max(0, f0 - 1), True)])
    K.key(root, "location", [(0, hi), (f0, hi), (f0 + dur, lo)])
    K.key(root, "scale", [(0, (0.8,) * 3), (f0, (0.8,) * 3), (f0 + dur, (1.0,) * 3)])
    K.glow_keys(fm, [(0, 0.0), (f0, 0.0), (f0 + dur, face_peak), (f0 + dur + 24, face_rest)] + ([(end, face_rest)] if end else []))
    return root, fm


def ribbon(name, pts, r=0.006, mat=None):
    """A glowing tube along a polyline (curve with bevel). Grow with K.grow(obj, keys)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.bevel_factor_mapping_end = "SPLINE"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (c[0], c[1], c[2], 1.0)
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    if mat:
        cu.materials.append(mat)
    o.visible_shadow = False
    cu.bevel_factor_end = 0.0
    return o
