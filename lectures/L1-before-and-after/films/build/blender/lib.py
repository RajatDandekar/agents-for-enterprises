"""Shared Blender helpers for the L1 film: studio, materials, primitives, timeline beats.

Rules carried over from the Kernel v3 / Agents lessons:
- bright diffuse studio, huge soft lights with visible_glossy off (no light shapes in reflections);
- satin / brushed / ceramic finishes, glow only on dark bodies, AgX;
- boxes are built at the origin and THEN placed (transform_apply never bakes location);
- no readable text in 3D: anchors are exported and labels are drawn in 2D.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")
TIMELINE = os.environ.get("TIMELINE", os.path.join(HERE, "..", "timeline.json"))
FPS = 30
GLOW = 0.4  # AgX turns strong coloured emission white: keep glows modest

SKY = (0.047, 0.28, 1.0, 1)       # #3c90ff linear-ish
SKY_L = (0.25, 0.55, 1.0, 1)
EMBER = (0.56, 0.09, 0.015, 1)    # #c4511f
EMBER_L = (1.0, 0.22, 0.04, 1)
GREEN = (0.013, 0.27, 0.10, 1)    # #1e8e5a
GREEN_L = (0.06, 0.75, 0.28, 1)


# ---------------------------------------------------------------- timeline
class Beats:
    """Word lookups in LOCAL frames of one shot (local 0 = the shot's first rendered frame)."""

    def __init__(self, shot):
        self.tl = json.load(open(TIMELINE))
        self.s = next(s for s in self.tl["shots"] if s["shot"] == shot)
        self.origin = self.s["r0"]
        self.frames = self.s["frames"]
        self.block = self.s["block"]

    def w(self, text, nth=0, block=None, edge="f0"):
        block = block or self.block
        norm = lambda s: s.lower().strip(".,?:!;")  # noqa: E731
        ws = [x for x in self.tl["words"] if x["block"] == block]
        hits = [x for x in ws if norm(x["w"]) == text.lower()] or [x for x in ws if norm(x["w"]).startswith(text.lower())]
        if len(hits) <= nth:
            raise KeyError(f"{text!r}#{nth} not in {block}")
        return hits[nth][edge] - self.origin

    def g(self, gframe):
        return gframe - self.origin


# ---------------------------------------------------------------- scene
def reset(frames):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, frames - 1
    return sc


def key(obj, path, keys, index=-1, interp=None):
    for f, val in keys:
        if index >= 0:
            getattr(obj, path)[index] = val
            obj.keyframe_insert(path, index=index, frame=f)
        else:
            setattr(obj, path, val)
            obj.keyframe_insert(path, frame=f)


def smooth_all():
    for a in bpy.data.actions:
        for fc in a.fcurves:
            for kp in fc.keyframe_points:
                if kp.interpolation != "CONSTANT":
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"


def configure(sc, samples=128, exposure=0.0):
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 12
    cy.caustics_reflective = cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.film_transparent = False


def world(sc, strength=0.9):
    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    co = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = -1.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.3, (0.05, 0.055, 0.065, 1)
    e[1].position, e[1].color = 1.0, (1.0, 1.0, 1.0, 1)
    m = e.new(0.55)
    m.color = (0.30, 0.32, 0.36, 1)
    nt.links.new(co.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs[0])


def cyc(front=(0.085, 0.088, 0.095, 1), back=(0.006, 0.007, 0.009, 1), width=80.0, y0=-40.0, y1=14.0, radius=10.0, h=30.0):
    m = principled("cyc", front, rough=0.55, coat=0.35)
    bsdf(m).inputs["Coat Roughness"].default_value = 0.18
    nt = m.node_tree
    b = bsdf(m)
    co = nt.nodes.new("ShaderNodeTexCoord")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (1.5, 0.5, 0.0)
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 4.0
    rng.inputs["From Max"].default_value = 17.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = front
    ramp.color_ramp.elements[1].color = back
    nt.links.new(co.outputs["Object"], sub.inputs[0])
    nt.links.new(sub.outputs[0], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    mesh = bpy.data.meshes.new("cyc")
    bm = bmesh.new()
    prof = [(y0, 0.0), (y1, 0.0)]
    for i in range(1, 20):
        a = math.radians(90 * i / 20)
        prof.append((y1 + radius * math.sin(a), radius * (1 - math.cos(a))))
    prof.append((y1 + radius, h))
    rows = [[bm.verts.new((x, y, z)) for y, z in prof] for x in (-width / 2, width / 2)]
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new("cyc", mesh)
    bpy.context.collection.objects.link(o)
    for p in mesh.polygons:
        p.use_smooth = True
    o.data.materials.append(m)
    return o


def soft_light(name, loc, target, power, size, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.size, d.color, d.shape = power, size, color, "DISK"
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.visible_glossy = False
    o.visible_transmission = False
    return o


def studio(sc, focus=(1.5, 0, 0.8), key_power=5200.0, world_strength=0.35):
    """Rubin-like graphite studio: a dark seamless sweep, one huge soft key overhead-front,
    a cool rim from behind, a low warm fill. Lights never appear in reflections."""
    world(sc, world_strength)
    cyc()
    fx, fy, fz = focus
    soft_light("key", (fx - 4, fy - 7, fz + 8), (fx, fy, fz), key_power, 14, (1.0, 0.97, 0.93))
    soft_light("top", (fx, fy + 0.5, fz + 9), (fx, fy, fz), key_power * 0.7, 20)
    soft_light("fill", (fx + 8, fy - 6, fz + 2), (fx, fy, fz), key_power * 0.12, 14, (1.0, 0.92, 0.85))
    soft_light("rim", (fx, fy + 8, fz + 4), (fx, fy, fz), key_power * 0.45, 18, (0.75, 0.85, 1.0))


def camera(sc, lens=50, fstop=4.0):
    d = bpy.data.cameras.new("cam")
    d.lens = lens
    d.sensor_width = 36
    d.dof.use_dof = True
    d.dof.aperture_fstop = fstop
    d.clip_start = 0.02
    d.clip_end = 200
    cam = bpy.data.objects.new("cam", d)
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    tgt = empty("cam_target")
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    d.dof.focus_object = tgt
    return cam, tgt


def cam_keys(cam, tgt, keys):
    """keys: [(frame, cam_loc, target_loc)] eased (bezier)."""
    key(cam, "location", [(f, c) for f, c, _ in keys])
    key(tgt, "location", [(f, t) for f, _, t in keys])


# ---------------------------------------------------------------- materials
def principled(name, color, rough=0.4, metallic=0.0, coat=0.0, transmission=0.0, ior=1.45, aniso=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = 0.25
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Anisotropic"].default_value = aniso
    return m


def bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]


def _bump(m, scale=(1, 220, 1), strength=0.03, noise_scale=6.0, kind="noise"):
    nt = m.node_tree
    b = bsdf(m)
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    if kind == "noise":
        tx = nt.nodes.new("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = noise_scale
        tx.inputs["Detail"].default_value = 8.0
        out = tx.outputs["Fac"]
    else:
        tx = nt.nodes.new("ShaderNodeTexWave")
        tx.inputs["Scale"].default_value = noise_scale
        tx.inputs["Distortion"].default_value = 1.5
        out = tx.outputs["Fac"]
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
    nt.links.new(out, bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])


def brushed(name="alu", color=(0.86, 0.87, 0.88, 1), rough=0.28):
    m = principled(name, color, rough=rough, metallic=1.0, aniso=0.5)
    return m


def anodized(name, color, rough=0.36):
    return principled(name, color, rough=rough, metallic=1.0)


def satin(name, color, rough=0.42, coat=0.25):
    return principled(name, color, rough=rough, coat=coat)


def powder(name, color, rough=0.55):
    """Powder-coated steel: fine orange-peel bump."""
    m = principled(name, color, rough=rough, coat=0.1)
    _bump(m, scale=(1, 1, 1), strength=0.012, noise_scale=900.0)
    return m


def rubber(name="rubber", color=(0.025, 0.026, 0.028, 1)):
    return principled(name, color, rough=0.75)


def chrome(name="chrome"):
    return principled(name, (0.9, 0.9, 0.9, 1), rough=0.12, metallic=1.0)


def gold(name="gold"):
    return principled(name, (1.0, 0.76, 0.36, 1), rough=0.22, metallic=1.0)


def glass(name, tint=(0.95, 0.97, 1.0, 1), rough=0.04):
    return principled(name, tint, rough=rough, transmission=1.0, ior=1.47)


def frosted(name, tint=(0.92, 0.95, 1.0, 1), rough=0.3):
    return principled(name, tint, rough=rough, transmission=1.0, ior=1.49)


def wood(name="oak", c1=(0.42, 0.25, 0.12, 1), c2=(0.26, 0.14, 0.06, 1), scale=(1.0, 18.0, 1.0)):
    m = principled(name, c1, rough=0.45, coat=0.35)
    nt = m.node_tree
    b = bsdf(m)
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.inputs["Scale"].default_value = 2.0
    wv.inputs["Distortion"].default_value = 6.0
    wv.inputs["Detail"].default_value = 6.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = c1
    ramp.color_ramp.elements[1].color = c2
    nt.links.new(co.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def textured(name, img, rough=0.45, coat=0.2, metallic=0.0, emit_mask=None, emit_color=SKY, uv_scale=None):
    """Image base colour (UV). With emit_mask: an image mask times a keyable 'em' value drives emission."""
    m = principled(name, (1, 1, 1, 1), rough=rough, coat=coat, metallic=metallic)
    nt = m.node_tree
    b = bsdf(m)
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(os.path.join(TEX, img), check_existing=True)
    tx.extension = "EXTEND"
    nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if emit_mask:
        mk = nt.nodes.new("ShaderNodeTexImage")
        mk.image = bpy.data.images.load(os.path.join(TEX, emit_mask), check_existing=True)
        mk.image.colorspace_settings.name = "Non-Color"
        v = nt.nodes.new("ShaderNodeValue")
        v.name = "em"
        v.outputs[0].default_value = 0.0
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(mk.outputs["Color"], mul.inputs[0])
        nt.links.new(v.outputs[0], mul.inputs[1])
        b.inputs["Emission Color"].default_value = emit_color
        nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    return m


def led(name, color, body=(0.02, 0.02, 0.025, 1), strength=0.0):
    """A dark body that can light up: keyable via node 'em' (see em_keys)."""
    m = principled(name, body, rough=0.3, coat=0.5)
    nt = m.node_tree
    b = bsdf(m)
    v = nt.nodes.new("ShaderNodeValue")
    v.name = "em"
    v.outputs[0].default_value = strength * GLOW
    b.inputs["Emission Color"].default_value = color
    nt.links.new(v.outputs[0], b.inputs["Emission Strength"])
    return m


def em_keys(m, keys, scale=True):
    k = [(f, s * (GLOW if scale else 1.0)) for f, s in keys]
    key(m.node_tree.nodes["em"].outputs[0], "default_value", k)


def em_color_keys(m, keys):
    b = bsdf(m)
    for f, c in keys:
        b.inputs["Emission Color"].default_value = c
        b.inputs["Emission Color"].keyframe_insert("default_value", frame=f)


# ---------------------------------------------------------------- primitives
def _finish_mesh(o, mat, bevel, seg, smooth=True):
    if bevel > 0:
        md = o.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = seg
        md.limit_method = "ANGLE"
        md.harden_normals = True
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    if mat:
        o.data.materials.append(mat)
    return o


def _place(o, loc, rot, parent):
    if parent is not None:
        o.parent = parent
    o.location = loc
    o.rotation_euler = rot
    return o


def box(name, size, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.004, seg=3, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    _finish_mesh(o, mat, min(bevel, min(size) * 0.45), seg)
    return _place(o, loc, rot, parent)


def cyl(name, r, depth, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), verts=48, bevel=0.002, seg=2, parent=None, r2=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    _finish_mesh(o, mat, min(bevel, r * 0.4, depth * 0.4), seg)
    return _place(o, loc, rot, parent)


def sphere(name, r, mat=None, loc=(0, 0, 0), parent=None, seg=24):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    _finish_mesh(o, mat, 0, 0)
    return _place(o, loc, (0, 0, 0), parent)


def torus(name, R, r, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=64, minor_segments=16)
    o = bpy.context.active_object
    o.name = name
    _finish_mesh(o, mat, 0, 0)
    return _place(o, loc, rot, parent)


def plane_uv(name, w, h, mat=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    """A flat card with a full 0..1 UV (for image prints)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return _place(o, loc, rot, parent)


def card(name, w, h, t, body_mat, print_mat, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, bevel=0.0015):
    """A thin slab with a printed top face (print is a UV plane 0.1 mm above)."""
    root = box(name, (w, h, t), body_mat, loc, rot, bevel=bevel, parent=parent)
    plane_uv(name + "_print", w * 0.985, h * 0.985, print_mat, (0, 0, t / 2 + 0.0002), parent=root)
    return root


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    o.location = loc
    return o


def tube(name, pts, r, mat, res=12, bevel_res=6):
    """A smooth tube through points (Bezier, auto handles)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = bevel_res
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def path(name, pts):
    """Invisible guide curve (for Follow Path packets)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.use_path = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    return o


def follow(obj, curve, keys, follow_axis=True):
    """Ride `curve`; keys: [(frame, offset 0..1)]."""
    c = obj.constraints.new("FOLLOW_PATH")
    c.target = curve
    c.use_fixed_location = True
    c.use_curve_follow = follow_axis
    c.forward_axis = "FORWARD_X"
    c.up_axis = "UP_Z"
    for f, v in keys:
        c.offset_factor = max(0.0, min(1.0, v))
        c.keyframe_insert("offset_factor", frame=f)
    return c


def vis(obj, keys):
    """keys: [(frame, visible)] CONSTANT. A key at frame 0 means 'from the start' (also before 0)."""
    keys = sorted([(-500 if f == 0 else f, v) for f, v in keys], key=lambda k: k[0])
    for f, v in keys:
        obj.hide_render = not v
        obj.keyframe_insert("hide_render", frame=f)
        obj.hide_viewport = not v
        obj.keyframe_insert("hide_viewport", frame=f)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            if fc.data_path in ("hide_render", "hide_viewport"):
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def scale_in(obj, f0, f1, s=1.0):
    key(obj, "scale", [(f0, (0.0001,) * 3), (f1, (s,) * 3)])


def save(sc, path):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=path)
