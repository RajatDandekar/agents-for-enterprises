"""The shared world kit for every Lecture 2 film ("The Brain"), so the films read as one series.

World: a bright, diffuse "sky studio" (white-to-sky cyclorama, huge soft disk lights invisible to glossy rays, AgX),
a long white plinth the tokens sit on, and precision props: ceramic token tiles, dark-glass vector plates whose cells
glow with the real recorded values, glass meters, light beams, machined matrix frames and the 24-floor block tower.
All readable text is 2D (pins exported per frame by export_proj and drawn by build/overlay.py).

Run inside Blender (Modal): scenes/<film>.py imports this module.
"""
import json
import math
import os

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

FPS = 30
BUILD = os.environ.get("FILMS_BUILD", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILMS = os.path.dirname(BUILD)
L2 = os.path.dirname(FILMS)


def lin(hexstr, a=1.0):
    """sRGB hex -> linear RGBA."""
    h = hexstr.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda x: x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4  # noqa: E731
    return (f(c[0]), f(c[1]), f(c[2]), a)


SKY = lin("#3c90ff")
DEEP = lin("#0b57d0")
EMBER = lin("#c4511f")
GREEN = lin("#1e8e5a")
Q_COL = lin("#3c90ff")      # query: sky blue
K_COL = lin("#9a5cff")      # key: violet
V_COL = lin("#fff0d2")      # value: warm white light
NEG = (0.16, 0.2, 0.28, 1)  # negative values: slate
ROLE = {"system": lin("#8a97ab"), "user": lin("#3c90ff"), "template": lin("#c9c4bb")}


# ------------------------------------------------------------------------------------------------ data + timeline
def load(rel):
    return json.load(open(os.path.join(L2, rel)))


class Beats:
    """Word lookups on films/build/timeline/<film>.json (frames)."""

    def __init__(self, film):
        self.tl = json.load(open(os.path.join(BUILD, "timeline", f"{film}.json")))
        self.frames = self.tl["frames"]
        self.blocks = {b["id"]: b for b in self.tl["blocks"]}

    def b0(self, bid):
        return self.blocks[bid]["f0"]

    def b1(self, bid):
        return self.blocks[bid]["f1"]

    def w(self, bid, text, nth=0, edge="f0"):
        norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum() or ch in "'-")  # noqa: E731
        ws = [w for w in self.tl["words"] if w["block"] == bid]
        t = norm(text)
        hits = [w for w in ws if norm(w["w"]) == t] or [w for w in ws if norm(w["w"]).startswith(t)]
        if len(hits) <= nth:
            raise KeyError(f"{bid}: word {text!r} #{nth} not found")
        return hits[nth][edge]


# ------------------------------------------------------------------------------------------------ scene + animation
def reset(frames):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 0
    sc.frame_end = frames - 1
    return sc


def key(obj, path, keys, index=-1, interp=None):
    for f, val in keys:
        if index >= 0:
            getattr(obj, path)[index] = val
            obj.keyframe_insert(path, index=index, frame=f)
        else:
            setattr(obj, path, val)
            obj.keyframe_insert(path, frame=f)


def keyval(node_socket, keys):
    for f, val in keys:
        node_socket.default_value = val
        node_socket.keyframe_insert("default_value", frame=f)


def smooth_all():
    for act in bpy.data.actions:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                if kp.interpolation != "CONSTANT":
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data and m.node_tree.animation_data.action:
            for fc in m.node_tree.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"


def show(obj, keys):
    """keys: [(frame, visible)] -> hide_render/hide_viewport stepped keys (children too)."""
    objs = [obj] + list(obj.children_recursive)
    for o in objs:
        for f, vis in keys:
            o.hide_render = not vis
            o.hide_viewport = not vis
            o.keyframe_insert("hide_render", frame=f)
            o.keyframe_insert("hide_viewport", frame=f)
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                if fc.data_path in ("hide_render", "hide_viewport"):
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"


# ------------------------------------------------------------------------------------------------ materials
def principled(name, color, rough=0.4, metallic=0.0, coat=0.0, transmission=0.0, ior=1.45, coat_rough=0.3,
               emission=None, emit=0.0, aniso=0.0, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Anisotropic"].default_value = aniso
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.4, 0.5, 0.7)
        b.inputs["Subsurface Scale"].default_value = 0.01
    if emission is not None:
        b.inputs["Emission Color"].default_value = emission
        b.inputs["Emission Strength"].default_value = emit
    return m


def bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]


def _bump(m, scale=(1, 220, 1), strength=0.03, noise_scale=6.0):
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = noise_scale
    nz.inputs["Detail"].default_value = 8
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf(m).inputs["Normal"])


_MAT = {}


def M(name):
    """The shared finish library (one material per finish, created once)."""
    if name in _MAT:
        return _MAT[name]
    if name == "ceramic":
        m = principled("ceramic", (0.80, 0.79, 0.76, 1), rough=0.3, coat=0.5, coat_rough=0.1, sss=0.06)
    elif name == "plinth":
        m = principled("plinth", (0.028, 0.032, 0.04, 1), rough=0.42, coat=0.35, coat_rough=0.22)
        _bump(m, scale=(30, 30, 30), strength=0.006, noise_scale=40)
    elif name == "alu":
        m = principled("alu", (0.88, 0.89, 0.9, 1), rough=0.28, metallic=1.0, aniso=0.6)
        _bump(m)
    elif name == "alu_dark":
        m = principled("alu_dark", (0.22, 0.24, 0.27, 1), rough=0.34, metallic=1.0, aniso=0.4)
        _bump(m, strength=0.02)
    elif name == "graphite":
        m = principled("graphite", (0.03, 0.035, 0.045, 1), rough=0.38, coat=0.6, coat_rough=0.1)
    elif name == "shadowgap":
        m = principled("shadowgap", (0.05, 0.055, 0.06, 1), rough=0.6)
    elif name == "glass":
        m = principled("glass", (0.97, 0.98, 1.0, 1), rough=0.04, transmission=1.0, ior=1.47)
    elif name == "frost":
        m = principled("frost", (0.93, 0.96, 1.0, 1), rough=0.35, transmission=1.0, ior=1.47)
    elif name == "tick":
        m = principled("tick", (0.1, 0.11, 0.13, 1), rough=0.4, metallic=0.5)
    else:
        raise KeyError(name)
    _MAT[name] = m
    return m


def anod(name, color, rough=0.36):
    m = principled(name, color, rough=rough, metallic=1.0)
    _bump(m, strength=0.015)
    return m


def glow_mat(name, color, strength=0.0, base=(0.02, 0.02, 0.025, 1)):
    """A dark body with a keyable emission ('glow' value node)."""
    m = principled(name, base, rough=0.3, coat=0.5, coat_rough=0.1)
    nt = m.node_tree
    b = bsdf(m)
    b.inputs["Emission Color"].default_value = color
    v = nt.nodes.new("ShaderNodeValue")
    v.name = "glow"
    v.outputs[0].default_value = strength
    nt.links.new(v.outputs[0], b.inputs["Emission Strength"])
    return m


def light_mat(name, color, strength=0.0):
    """Pure emission (beams, liquid light). Keyable 'glow'."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    v = nt.nodes.new("ShaderNodeValue")
    v.name = "glow"
    v.outputs[0].default_value = strength
    nt.links.new(v.outputs[0], em.inputs["Strength"])
    # transparent where weak, so a faint beam does not read as a grey rod
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    clamp = nt.nodes.new("ShaderNodeMath")
    clamp.operation = "MINIMUM"
    clamp.inputs[1].default_value = 1.0
    nt.links.new(v.outputs[0], clamp.inputs[0])
    nt.links.new(clamp.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def glow_keys(m, keys, node="glow"):
    keyval(m.node_tree.nodes[node].outputs[0], keys)


def cells_image(name, values, cols, rows, color, vmax=None, px=12, gap=2, neg=NEG, gamma=0.75):
    """A cell grid image from real values: positive = `color` (brightness by size), negative = slate."""
    n = cols * rows
    vals = list(values)[:n] + [0.0] * max(0, n - len(values))
    vmax = vmax or (max(abs(x) for x in vals) or 1.0)
    W, H = cols * px, rows * px
    img = bpy.data.images.new(name, W, H, alpha=False)
    pix = [0.0] * (W * H * 4)
    for idx, val in enumerate(vals):
        r, c = divmod(idx, cols)
        t = min(1.0, abs(val) / vmax) ** gamma
        col = color if val >= 0 else neg
        lift = 0.06  # every cell is faintly visible, so the grid reads as an object
        rgb = [lift * 0.6 + (1 - lift) * t * col[i] for i in range(3)] if val >= 0 else \
              [lift * 0.5 + 0.55 * t * col[i] / max(col) for i in range(3)]
        y0 = (rows - 1 - r) * px  # row 0 at the top
        for yy in range(y0 + gap, y0 + px - gap):
            base = (yy * W + c * px) * 4
            for xx in range(gap, px - gap):
                k = base + xx * 4
                pix[k] = rgb[0]; pix[k + 1] = rgb[1]; pix[k + 2] = rgb[2]; pix[k + 3] = 1.0
    img.pixels.foreach_set(pix)
    img.pack()
    return img


def cells_mat(name, values, cols, rows, color, vmax=None, strength=0.0, reveal=1.0, dim=0.12):
    """Dark-glass plate face whose cells glow with the values. Keyable 'glow' (strength) and 'reveal' (0..1: the
    fraction of cells lit in reading order; unlit cells keep `dim` of their light)."""
    img = cells_image(name + "_img", values, cols, rows, color, vmax)
    m = principled(name, (0.012, 0.014, 0.02, 1), rough=0.22, coat=0.8, coat_rough=0.05)
    nt = m.node_tree
    b = bsdf(m)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    uv = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])

    def op(kind, a, bval=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        if isinstance(a, (int, float)):
            n.inputs[0].default_value = a
        else:
            nt.links.new(a, n.inputs[0])
        if bval is not None:
            if isinstance(bval, (int, float)):
                n.inputs[1].default_value = bval
            else:
                nt.links.new(bval, n.inputs[1])
        return n.outputs[0]
    col_i = op("FLOOR", op("MULTIPLY", sep.outputs["X"], cols * 0.99999))
    row_i = op("FLOOR", op("MULTIPLY", op("SUBTRACT", 1.0, sep.outputs["Y"]), rows * 0.99999))
    idx = op("ADD", op("MULTIPLY", row_i, cols), col_i)
    rv = nt.nodes.new("ShaderNodeValue")
    rv.name = "reveal"
    rv.outputs[0].default_value = reveal
    lit = op("LESS_THAN", idx, op("MULTIPLY", rv.outputs[0], cols * rows))
    fac = op("ADD", dim, op("MULTIPLY", lit, 1 - dim))
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = strength
    stren = op("MULTIPLY", fac, gv.outputs[0])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(stren, b.inputs["Emission Strength"])
    # faint base colour from the cells, so an unlit plate still shows its grid in daylight
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = 0.35
    mix.inputs["A"].default_value = (0.012, 0.014, 0.02, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    return m


# ------------------------------------------------------------------------------------------------ meshes
def _link(obj, parent=None):
    bpy.context.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def rbox(name, size, bevel=0.01, seg=4, mat=None, loc=(0, 0, 0), parent=None):
    """Rounded box built at the origin (scale applied to the mesh only), then placed at loc."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    _link(obj, parent)
    obj.location = loc
    if bevel > 0:
        md = obj.modifiers.new("bevel", "BEVEL")
        md.width = min(bevel, min(size) * 0.49)
        md.segments = seg
        md.limit_method = "NONE"
        md.harden_normals = True
    for p in mesh.polygons:
        p.use_smooth = True
    if mat:
        mesh.materials.append(mat)
    return obj


def cyl(name, r, depth, mat=None, loc=(0, 0, 0), verts=48, bevel=0.0, parent=None, base=False):
    """Cylinder along z; base=True puts the origin at its bottom (scale z grows it upward)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=depth)
    if base:
        for v in bm.verts:
            v.co.z += depth / 2
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    _link(obj, parent)
    obj.location = loc
    if bevel > 0:
        md = obj.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.limit_method = "ANGLE"
    for p in mesh.polygons:
        p.use_smooth = True
    if mat:
        mesh.materials.append(mat)
    try:
        mesh.set_sharp_from_angle(angle=math.radians(40))
    except Exception:
        pass
    return obj


def plane(name, w, h, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """A w x h plane in its local XZ (facing -Y), UV 0..1 (u along x, v along z)."""
    mesh = bpy.data.meshes.new(name)
    verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uvl = mesh.uv_layers.new(name="UVMap")
    for li, uv in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[li].uv = uv
    obj = bpy.data.objects.new(name, mesh)
    _link(obj, parent)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        mesh.materials.append(mat)
    return obj


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    _link(o, parent)
    o.location = loc
    o.empty_display_size = 0.05
    return o


def beam(name, a, b, r=0.006, mat=None):
    """A thin light beam from a to b: origin at a, local +z toward b. Scale z (0..1) grows it from a."""
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(name, r, d.length, mat, verts=16, base=True)
    o.location = a
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = d.to_track_quat("Z", "Y")
    o.visible_shadow = False
    try:
        o.visible_glossy = True
    except Exception:
        pass
    return o


# ------------------------------------------------------------------------------------------------ props
def token_tile(name, role, loc, parent=None, size=(0.30, 0.22, 0.075)):
    """A ceramic token tile: bevelled body, recessed frosted face that can glow, an anodised role band, a dark
    id plate on the front. Returns (root, face_material). The token text is a 2D pin at <name>_top."""
    root = empty(name, loc, parent)
    w, d, h = size
    rbox(name + "_body", (w, d, h), bevel=0.014, seg=5, mat=M("ceramic"), loc=(0, 0, h / 2), parent=root)
    band_m = _MAT.get("band_" + role) or anod("band_" + role, ROLE[role])
    _MAT["band_" + role] = band_m
    rbox(name + "_band", (w + 0.006, d + 0.006, 0.012), bevel=0.005, seg=3, mat=band_m, loc=(0, 0, 0.009), parent=root)
    rbox(name + "_foot", (w - 0.02, d - 0.02, 0.006), bevel=0.002, seg=2, mat=M("shadowgap"), loc=(0, 0, 0.0015), parent=root)
    face_m = glow_mat(name + "_face", SKY, 0.0, base=(0.018, 0.022, 0.03, 1))
    bsdf(face_m).inputs["Roughness"].default_value = 0.18
    rbox(name + "_face", (w - 0.05, d - 0.05, 0.01), bevel=0.004, seg=3, mat=face_m, loc=(0, 0, h - 0.002), parent=root)
    rbox(name + "_id", (w * 0.42, 0.004, 0.016), bevel=0.002, seg=2, mat=M("graphite"), loc=(0, -d / 2 - 0.0005, h * 0.45), parent=root)
    empty(name + "_top", (0, 0, h + 0.01), parent=root)
    empty(name + "_front", (0, -d / 2 - 0.004, 0.004), parent=root)
    return root, face_m


def vector_plate(name, values, cols, rows, color, loc, cell=0.018, parent=None, vmax=None, glow=0.0, reveal=1.0,
                 frame_mat=None, depth=0.014, two_sided=False):
    """A dark-glass plate in a machined frame whose cells glow with the real values (cols x rows cells).
    Faces -Y. Returns (root, cells_material). Pins: <name>_top, <name>_mid."""
    root = empty(name, loc, parent)
    W, H = cols * cell, rows * cell
    m = cells_mat(name + "_cells", values, cols, rows, color, vmax=vmax, strength=glow, reveal=reveal)
    plane(name + "_face", W, H, m, loc=(0, -depth / 2 - 0.0012, 0), parent=root)
    if two_sided:  # the same cells on the back (mirrored), for a plate seen from behind
        plane(name + "_face2", W, H, m, loc=(0, depth / 2 + 0.0012, 0), rot=(0, 0, math.pi), parent=root)
    rbox(name + "_back", (W + 0.004, depth, H + 0.004), bevel=0.002, seg=2, mat=M("graphite"), loc=(0, 0, 0), parent=root)
    fm = frame_mat or M("alu")
    t = 0.007
    rbox(name + "_ft", (W + 2 * t, depth + 0.004, t), bevel=0.0025, seg=3, mat=fm, loc=(0, 0, H / 2 + t / 2), parent=root)
    rbox(name + "_fb", (W + 2 * t, depth + 0.004, t), bevel=0.0025, seg=3, mat=fm, loc=(0, 0, -H / 2 - t / 2), parent=root)
    rbox(name + "_fl", (t, depth + 0.004, H), bevel=0.0025, seg=3, mat=fm, loc=(-W / 2 - t / 2, 0, 0), parent=root)
    rbox(name + "_fr", (t, depth + 0.004, H), bevel=0.0025, seg=3, mat=fm, loc=(W / 2 + t / 2, 0, 0), parent=root)
    empty(name + "_top", (0, 0, H / 2 + t + 0.01), parent=root)
    empty(name + "_mid", (0, -depth, 0), parent=root)
    empty(name + "_bot", (0, 0, -H / 2 - t), parent=root)
    return root, m


def meter(name, loc, height=0.3, r=0.016, color=SKY, parent=None):
    """A glass meter tube on an aluminium foot with dark tick rings; the light column inside grows with
    `<name>_liquid`.scale.z (0..1). Returns (root, liquid_obj, liquid_mat). Pin: <name>_top (moves with the level)."""
    root = empty(name, loc, parent)
    cyl(name + "_foot", r * 1.9, 0.014, M("alu"), loc=(0, 0, 0.007), bevel=0.003, parent=root)
    cyl(name + "_cap", r * 1.35, 0.01, M("alu"), loc=(0, 0, height + 0.019), bevel=0.002, parent=root)
    tube = cyl(name + "_tube", r, height, M("glass"), loc=(0, 0, 0.014 + height / 2), verts=40, parent=root)
    tube.visible_shadow = False
    for k in (0.25, 0.5, 0.75):
        bpy.ops.mesh.primitive_torus_add(major_radius=r * 1.02, minor_radius=0.0012, location=(0, 0, 0.014 + height * k))
        tk = bpy.context.active_object
        tk.name = f"{name}_tick{int(k * 100)}"
        tk.data.materials.append(M("tick"))
        tk.parent = root
        tk.location = (0, 0, 0.014 + height * k)
    lm = light_mat(name + "_liq", color, 0.0)
    liq = cyl(name + "_liquid", r * 0.72, height * 0.995, lm, loc=(0, 0, 0.0145), verts=24, base=True, parent=root)
    liq.scale = (1, 1, 0.001)
    liq.visible_shadow = False
    lvl = empty(name + "_top", (0, 0, height * 0.995), parent=liq)
    return root, liq, lm


def matrix_frame(name, loc, w=0.34, h=0.42, parent=None, tint=SKY, seed=0):
    """A machined 'learned matrix' frame: brushed aluminium bezel holding a dense etched grid that glints as light
    passes through (decorative: the pattern is not the real weights). Faces -Y."""
    root = empty(name, loc, parent)
    t = 0.022
    for nm, sz, lc in ((
            "_t", (w + 2 * t, 0.03, t), (0, 0, h / 2 + t / 2)), ("_b", (w + 2 * t, 0.03, t), (0, 0, -h / 2 - t / 2)),
            ("_l", (t, 0.03, h), (-w / 2 - t / 2, 0, 0)), ("_r", (t, 0.03, h), (w / 2 + t / 2, 0, 0))):
        rbox(name + nm, sz, bevel=0.005, seg=4, mat=M("alu"), loc=lc, parent=root)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cyl(f"{name}_screw{sx}{sz}", 0.0055, 0.004, M("alu_dark"), loc=(sx * (w / 2 + t / 2), -0.0165, sz * (h / 2 + t / 2)),
                verts=20, parent=root).rotation_euler = (math.pi / 2, 0, 0)
    # the etched grid: many fine cells from a deterministic pseudo-random pattern
    import random
    rnd = random.Random(seed)
    cols, rows = 56, 64
    vals = [rnd.gauss(0, 1) for _ in range(cols * rows)]
    m = cells_mat(name + "_grid", vals, cols, rows, tint, vmax=2.6, strength=0.0)
    face = plane(name + "_grid", w, h, m, loc=(0, 0, 0), parent=root)
    empty(name + "_top", (0, 0, h / 2 + t + 0.01), parent=root)
    return root, m


def plinth(name, x0, x1, y=0.0, depth=0.5, height=0.11, mat=None):
    """The long white display plinth the tokens stand on (top at z=height)."""
    L = x1 - x0
    root = empty(name, ((x0 + x1) / 2, y, 0))
    rbox(name + "_top", (L, depth, height - 0.02), bevel=0.012, seg=5, mat=mat or M("plinth"), loc=(0, 0, 0.02 + (height - 0.02) / 2), parent=root)
    rbox(name + "_gap", (L - 0.04, depth - 0.04, 0.022), bevel=0.003, seg=2, mat=M("shadowgap"), loc=(0, 0, 0.011), parent=root)
    rbox(name + "_trim", (L + 0.002, 0.008, 0.012), bevel=0.003, seg=2, mat=M("alu"), loc=(0, -depth / 2 + 0.003, height - 0.012), parent=root)
    return root


# ------------------------------------------------------------------------------------------------ the studio
def build_world(sc, strength=0.3):
    """A dim graded lightbox: blue-grey at the horizon, near black below."""
    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    rmp = nt.nodes.new("ShaderNodeMapRange")
    rmp.inputs["From Min"].default_value = -1.0
    rmp.inputs["From Max"].default_value = 1.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.3, (0.03, 0.035, 0.05, 1)
    e[1].position, e[1].color = 1.0, (0.85, 0.9, 1.0, 1)
    m = e.new(0.55)
    m.color = (0.22, 0.25, 0.32, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], rmp.inputs["Value"])
    nt.links.new(rmp.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return bg


STUDIO_FOCUS = [0.0, 0.0]


def cyc(name="cyc", width=320.0, y0=-160.0, y1=6.0, radius=9.0, wall=60.0, cx=0.0,
        front=(0.075, 0.085, 0.11, 1), back=(0.006, 0.008, 0.014, 1)):
    """The L2 studio sweep: deep blue-grey satin, graded to near black away from the set (radial from the focus)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    prof = [(y0, 0.0), (y1, 0.0)]
    for i in range(1, 21):
        a = math.radians(90 * i / 20)
        prof.append((y1 + radius * math.sin(a), radius * (1 - math.cos(a))))
    prof.append((y1 + radius, wall))
    rows = [[bm.verts.new((cx + x, y, z)) for y, z in prof] for x in (-width / 2, width / 2)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    _link(obj)
    for p in mesh.polygons:
        p.use_smooth = True
    m = principled("cyc", front, rough=0.5, coat=0.35, coat_rough=0.16)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (STUDIO_FOCUS[0], STUDIO_FOCUS[1], 0.0)
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    rg = nt.nodes.new("ShaderNodeMapRange")
    rg.inputs["From Min"].default_value = 3.0
    rg.inputs["From Max"].default_value = 16.0
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = front
    rp.color_ramp.elements[1].color = back
    nt.links.new(tc.outputs["Object"], sub.inputs[0])
    nt.links.new(sub.outputs[0], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], rg.inputs["Value"])
    nt.links.new(rg.outputs["Result"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], bsdf(m).inputs["Base Color"])
    mesh.materials.append(m)
    return obj


def soft_light(name, loc, target, power, size, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA")
    d.energy = power
    d.size = size
    d.shape = "DISK"
    d.color = color
    o = bpy.data.objects.new(name, d)
    _link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.visible_glossy = False
    o.visible_transmission = False
    return o


def studio(sc, focus=(0.0, 0.0, 0.3), key_power=3200.0, world=0.3, span=0.0):
    """The L2 'midnight slate' studio: a deep blue-grey sweep graded to black, one big soft key front-left,
    a soft top, a cool rim from behind (it draws the tile edges), a low warm fill. `span` adds keys along x."""
    STUDIO_FOCUS[0], STUDIO_FOCUS[1] = focus[0], focus[1]
    build_world(sc, world)
    cyc(cx=focus[0])
    fx, fy, fz = focus
    soft_light("key", (fx - 4.0, fy - 6.5, fz + 7.5), focus, key_power, 12.0, (1.0, 0.97, 0.93))
    soft_light("top", (fx, fy + 0.5, fz + 9.0), focus, key_power * 0.55, 16.0)
    soft_light("fill", (fx + 7.0, fy - 6.0, fz + 1.5), focus, key_power * 0.08, 12.0, (1.0, 0.9, 0.82))
    soft_light("rim", (fx + 1.0, fy + 7.0, fz + 3.2), focus, key_power * 0.6, 14.0, (0.7, 0.82, 1.0))
    if span:
        for i, dx in enumerate((-span, -span / 2)):
            soft_light(f"run{i}", (fx + dx, fy - 6.5, fz + 7.5), (fx + dx, fy, fz), key_power * 0.5, 12.0, (1.0, 0.97, 0.93))
            soft_light(f"runrim{i}", (fx + dx, fy + 7.0, fz + 3.2), (fx + dx, fy, fz), key_power * 0.35, 14.0, (0.7, 0.82, 1.0))


def configure(sc, samples=96, exposure=0.0, glare=True):
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.025
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 3
    cy.transmission_bounces = 6
    cy.transparent_max_bounces = 128
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    if glare:
        sc.use_nodes = True
        nt = sc.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        rl = nt.nodes.new("CompositorNodeRLayers")
        gl = nt.nodes.new("CompositorNodeGlare")
        gl.glare_type = "FOG_GLOW"
        gl.quality = "HIGH"
        gl.threshold = 1.6
        gl.mix = -0.75
        gl.size = 8
        comp = nt.nodes.new("CompositorNodeComposite")
        nt.links.new(rl.outputs["Image"], gl.inputs["Image"])
        nt.links.new(gl.outputs["Image"], comp.inputs["Image"])


# ------------------------------------------------------------------------------------------------ cameras
class Cam:
    """A named camera with its own target; cut to it with cut(frame)."""

    def __init__(self, sc, name, lens=50, fstop=4.0):
        d = bpy.data.cameras.new(name)
        d.lens = lens
        d.sensor_width = 36
        d.dof.use_dof = True
        d.dof.aperture_fstop = fstop
        d.clip_start = 0.02
        d.clip_end = 400
        self.obj = bpy.data.objects.new(name, d)
        _link(self.obj)
        self.tgt = empty(name + "_tgt")
        c = self.obj.constraints.new("TRACK_TO")
        c.target = self.tgt
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        d.dof.focus_object = self.tgt
        self.sc = sc
        if sc.camera is None:
            sc.camera = self.obj
            _FIRST_CAM.append(self.obj)
            # Blender renders the frames before the first marker through the EARLIEST marker's camera, so the opening
            # camera must own a marker at frame 0 (otherwise it never renders and the 2D pins disagree with the picture)
            if not any(mk.frame == 0 and mk.camera for mk in sc.timeline_markers):
                mk = sc.timeline_markers.new(f"cut_{name}_0", frame=0)
                mk.camera = self.obj

    def keys(self, keys):
        """[(frame, cam_loc, target_loc)]"""
        for f, c, t in keys:
            self.obj.location = c
            self.obj.keyframe_insert("location", frame=f)
            self.tgt.location = t
            self.tgt.keyframe_insert("location", frame=f)
        return self

    def lens(self, keys):
        for f, v in keys:
            self.obj.data.lens = v
            self.obj.data.keyframe_insert("lens", frame=f)
        return self

    def fstop(self, keys):
        for f, v in keys:
            self.obj.data.dof.aperture_fstop = v
            self.obj.data.dof.keyframe_insert("aperture_fstop", frame=f)
        return self

    def cut(self, frame):
        frame -= frame % 2
        if any(m.frame == frame and m.camera == self.obj for m in self.sc.timeline_markers):
            return self
        mk = self.sc.timeline_markers.new(f"cut_{self.obj.name}_{frame}", frame=frame)
        mk.camera = self.obj
        return self


_FIRST_CAM = []


def camera_at(sc, f):
    """The camera the markers select at frame f (the first camera before any marker)."""
    best, bf = None, -1
    for mk in sc.timeline_markers:
        if mk.camera and mk.frame <= f and mk.frame >= bf:
            best, bf = mk.camera, mk.frame
    return best or (_FIRST_CAM[0] if _FIRST_CAM else sc.camera)


# ------------------------------------------------------------------------------------------------ projection + save
def export_proj(sc, names, path, step=1):
    """2D pixel positions (1920x1080) of the named empties for every frame: {name: [[x, y, depth], ...]}
    (depth < 0 = behind the camera). Also the camera name per frame."""
    objs = {n: bpy.data.objects[n] for n in names if n in bpy.data.objects}
    out = {n: [] for n in objs}
    cams = []
    for f in range(sc.frame_start, sc.frame_end + 1, step):
        sc.frame_set(f)
        cam = camera_at(sc, f)
        sc.camera = cam
        cams.append(cam.name)
        for n, o in objs.items():
            p = world_to_camera_view(sc, cam, o.matrix_world.translation)
            out[n].append([round(p.x * 1920, 1), round((1 - p.y) * 1080, 1), round(p.z, 2)])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({"step": step, "frames": sc.frame_end + 1, "cams": cams, "pins": out}, open(path, "w"), separators=(",", ":"))


def finish(sc, film, pins, samples=96, exposure=0.0):
    outdir = os.environ.get("OUTDIR", "/tmp")
    configure(sc, samples=samples, exposure=exposure)
    smooth_all()
    import time
    t0 = time.time()
    os.makedirs(os.path.join(outdir, "proj"), exist_ok=True)
    json.dump(sorted(set(pins)), open(os.path.join(outdir, "proj", f"{film}.pins.json"), "w"))
    print("NOTE proj seconds", round(time.time() - t0, 1))
    sc.frame_set(0)
    bpy.ops.file.pack_all()
    path = os.path.join(outdir, f"{film}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED", path, sc.frame_end + 1)


# ------------------------------------------------------------------------------------------------ arcs + the tower
def arc(name, a, b, lift=0.4, r=0.0045, mat=None):
    """A light arc from a up and over, landing vertically on b. Grow it with data.bevel_factor_end (0..1)."""
    a, b = Vector(a), Vector(b)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 3
    cu.resolution_u = 24
    cu.use_fill_caps = True
    cu.bevel_factor_mapping_end = "SPLINE"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(1)
    p0, p1 = sp.bezier_points
    top = max(a.z, b.z) + lift
    p0.co = a
    p0.handle_left_type = p0.handle_right_type = "FREE"
    p0.handle_right = Vector((a.x + (b.x - a.x) * 0.25, a.y + (b.y - a.y) * 0.25, top))
    p0.handle_left = a - (p0.handle_right - a)
    p1.co = b
    p1.handle_left_type = p1.handle_right_type = "FREE"
    p1.handle_left = Vector((b.x, b.y, top))
    p1.handle_right = b - (p1.handle_left - b)
    o = bpy.data.objects.new(name, cu)
    _link(o)
    if mat:
        cu.materials.append(mat)
    o.visible_shadow = False
    cu.bevel_factor_end = 0.0
    return o


def grow(o, keys):
    for f, v in keys:
        o.data.bevel_factor_end = v
        o.data.keyframe_insert("bevel_factor_end", frame=f)


def tower(name, loc, floors=24, pitch=0.11, w=2.0, d=0.8, heads=14, lit=()):
    """The model as a machine: `floors` stacked blocks (thin dark-aluminium slabs, like an HBM stack), each carrying
    `heads` attention-head modules with a glowing top strip, on four corner posts. `lit` = {(floor, head)} that get
    their own keyable material. Returns {"root", "floors": [root per floor], "heads": {(f, h): (obj, mat)},
    "idle": shared idle head material}. Pins: <name>_f<k>, <name>_f<k>_h<j> (1-based floors, 0-based heads)."""
    root = empty(name, loc)
    idle = glow_mat(name + "_idle", SKY, 0.0)
    out = {"root": root, "floors": [], "heads": {}, "idle": idle}
    for k in range(1, floors + 1):
        fz = (k - 1) * pitch
        fr = empty(f"{name}_f{k}", (0, 0, fz), parent=root)
        rbox(f"{name}_f{k}_slab", (w, d, 0.026), bevel=0.008, seg=4, mat=M("alu_dark"), loc=(0, 0, 0.013), parent=fr)
        rbox(f"{name}_f{k}_edge", (w + 0.004, 0.006, 0.006), bevel=0.002, seg=2, mat=M("alu"), loc=(0, -d / 2, 0.02), parent=fr)
        sp = w * 0.9 / heads
        for j in range(heads):
            x = (j - (heads - 1) / 2) * sp
            m = idle
            if (k, j) in lit:
                m = glow_mat(f"{name}_f{k}_h{j}_m", SKY, 0.0)
            hb = rbox(f"{name}_f{k}_h{j}", (sp * 0.72, d * 0.55, 0.03), bevel=0.006, seg=3, mat=M("graphite"),
                      loc=(x, 0, 0.026 + 0.015), parent=fr)
            rbox(f"{name}_f{k}_h{j}_led", (sp * 0.5, 0.012, 0.006), bevel=0.002, seg=2, mat=m,
                 loc=(x, -d * 0.275 - 0.004, 0.026 + 0.022), parent=fr)
            empty(f"{name}_f{k}_h{j}", (x, 0, 0.026 + 0.04), parent=fr) if False else None
            out["heads"][(k, j)] = (hb, m)
        empty(f"{name}_pin_f{k}", (w / 2 + 0.05, -d / 2, 0.02), parent=fr)
        out["floors"].append(fr)
    H = (floors - 1) * pitch + 0.08
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(f"{name}_post{sx}{sy}", 0.018, H + 0.1, M("alu"), loc=(sx * (w / 2 + 0.03), sy * (d / 2 - 0.05), H / 2), verts=24, parent=root)
    return out
