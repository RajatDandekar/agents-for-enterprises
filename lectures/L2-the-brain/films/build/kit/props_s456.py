"""Props for the L2 films s4 (attention), s5 (blocks) and s6 (choice), on top of the shared kit l2kit."""
import math

import bpy
from mathutils import Vector

import l2kit as K

PITCH = 0.36
PZ = 0.11
ZT = PZ + 0.075


def X(i, last=99):
    return (i - last) * PITCH


def row(tokens, values16, cell=0.022, col_y=0.05, glow=3.6, plinth=True):
    """The prompt as a row of tiles on the plinth, each with its vector standing behind it as a column of 16 glowing
    cells (the first 16 of its 896 input-embedding values, from trace.json). Returns {i: (tile_root, face_m, col_root,
    col_m)}. Pins: tok<i>_top, tok<i>_front, c<i>_top, c<i>_mid."""
    if plinth:
        K.plinth("plinth", X(0) - 0.45, 0.45, depth=0.5, height=PZ)
    out = {}
    zc = ZT + 0.03 + 8 * cell + 0.012
    for t in tokens:
        i = t["i"]
        root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
        cr, cm = K.vector_plate(f"c{i}", values16[i], 1, 16, K.SKY, (X(i), col_y, zc), cell=cell, vmax=0.06, glow=glow)
        out[i] = (root, fm, cr, cm)
    return out, zc + 8 * cell + 0.012


def glass_wall(name, loc, w=0.6, h=1.1, t=0.018):
    """A frosted glass panel in a brushed aluminium frame (the causal mask). Faces x (it stands across the row)."""
    root = K.empty(name, loc)
    m = K.principled(name + "_glass", (0.82, 0.88, 0.96, 1), rough=0.28, transmission=1.0, ior=1.45)
    K.rbox(name + "_pane", (t, w, h), bevel=0.004, seg=3, mat=m, loc=(0, 0, h / 2), parent=root)
    fr = 0.024
    for nm, sz, lc in (("_t", (t + 0.012, w + 2 * fr, fr), (0, 0, h + fr / 2)), ("_l", (t + 0.012, fr, h), (0, -w / 2 - fr / 2, h / 2)),
                       ("_r", (t + 0.012, fr, h), (0, w / 2 + fr / 2, h / 2))):
        K.rbox(name + nm, sz, bevel=0.005, seg=3, mat=K.M("alu"), loc=lc, parent=root)
    edge = K.light_mat(name + "_edge", K.SKY, 0.0)
    K.rbox(name + "_glowedge", (t + 0.004, w, 0.006), bevel=0.002, seg=2, mat=edge, loc=(0, 0, h - 0.004), parent=root)
    K.empty(name + "_top", (0, -w / 2, h + 0.05), parent=root)
    return root, edge


def arc_mat(name, color):
    return K.light_mat(name, color, 0.0)


# ------------------------------------------------------------------------------------------------ s5: the block tower
def block_tower(name, loc, floors=24, pitch=0.16, w=1.6, d=0.62, heads=14, fins=36):
    """24 floors; each floor = one block: an attention bay (14 head modules with LED strips) on the left and an MLP
    bay (a bank of thin fins with a light strip) on the right, plus a glass lens eyepiece at the front-left (the
    logit-lens readout). Every floor has its own keyable materials: att_<k>, mlp_<k>, lens_<k>.
    Returns {"root", "floors": [roots], "att": [mats], "mlp": [mats], "lens": [mats], "z": [floor z]}.
    Pins: <name>_lens<k> (front of the lens), <name>_att<k>, <name>_mlp<k> (front of the bays)."""
    root = K.empty(name, loc)
    out = {"root": root, "floors": [], "att": [], "mlp": [], "lens": [], "z": []}
    xa0, xa1 = -w / 2 + 0.06, 0.12
    xm0, xm1 = 0.2, w / 2 - 0.06
    for k in range(1, floors + 1):
        z = 0.08 + (k - 1) * pitch
        fr = K.empty(f"{name}_f{k}", (0, 0, z), parent=root)
        K.rbox(f"{name}_f{k}_slab", (w, d, 0.03), bevel=0.009, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.015), parent=fr)
        K.rbox(f"{name}_f{k}_trim", (w + 0.004, 0.006, 0.008), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -d / 2, 0.024), parent=fr)
        am = K.glow_mat(f"att_{k}", K.SKY, 0.0)
        mm = K.glow_mat(f"mlp_{k}", K.lin("#ffe2a8"), 0.0)
        lm = K.light_mat(f"lens_{k}", K.SKY, 0.0)
        sp = (xa1 - xa0) / heads
        for j in range(heads):
            x = xa0 + (j + 0.5) * sp
            K.rbox(f"{name}_f{k}_h{j}", (sp * 0.74, d * 0.62, 0.04), bevel=0.006, seg=3, mat=K.M("graphite"), loc=(x, 0.02, 0.05), parent=fr)
            K.rbox(f"{name}_f{k}_h{j}_led", (sp * 0.5, 0.01, 0.008), bevel=0.002, seg=2, mat=am, loc=(x, -d * 0.29, 0.064), parent=fr)
        fs = (xm1 - xm0) / fins
        for j in range(fins):
            x = xm0 + (j + 0.5) * fs
            K.rbox(f"{name}_f{k}_fin{j}", (fs * 0.42, d * 0.7, 0.07), bevel=0.0015, seg=2, mat=K.M("alu"), loc=(x, 0.0, 0.065), parent=fr)
        K.rbox(f"{name}_f{k}_mlpled", (xm1 - xm0, 0.01, 0.008), bevel=0.002, seg=2, mat=mm, loc=((xm0 + xm1) / 2, -d * 0.36, 0.035), parent=fr)
        # the lens: a short glass barrel with a glowing core, at the front-left corner
        barrel = K.cyl(f"{name}_f{k}_lens", 0.03, 0.05, K.M("alu"), loc=(-w / 2 - 0.07, -d / 2 + 0.06, 0.05), verts=32, bevel=0.003, parent=fr)
        barrel.rotation_euler = (math.pi / 2, 0, 0)
        core = K.cyl(f"{name}_f{k}_lenscore", 0.021, 0.054, lm, loc=(-w / 2 - 0.07, -d / 2 + 0.06, 0.05), verts=24, parent=fr)
        core.rotation_euler = (math.pi / 2, 0, 0)
        K.empty(f"{name}_lens{k}", (-w / 2 - 0.07, -d / 2 + 0.02, 0.05), parent=fr)
        K.empty(f"{name}_att{k}", ((xa0 + xa1) / 2, -d / 2, 0.07), parent=fr)
        K.empty(f"{name}_mlp{k}", ((xm0 + xm1) / 2, -d / 2, 0.07), parent=fr)
        out["floors"].append(fr)
        out["att"].append(am)
        out["mlp"].append(mm)
        out["lens"].append(lm)
        out["z"].append(z)
    H = 0.08 + (floors - 1) * pitch + 0.1
    posts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            posts.append(K.cyl(f"{name}_post{sx}{sy}", 0.016, H, K.M("alu"), loc=(sx * (w / 2 + 0.025), sy * (d / 2 - 0.04), H / 2), verts=24, parent=root))
    out["posts"] = posts
    out["H"] = H
    return out


# ------------------------------------------------------------------------------------------------ s6: rack and dial
def vocab_rack(name, x0, x1, y=0.9, z0=0.1, h=1.05, depth=0.42, pitch=0.026):
    """The vocabulary as a long rack of thin dark-glass slats (one per row of the table, schematically). Its slats
    light as a sweep passes: keyable value 'sweep' (an x position) on the material; slats within ~0.6 m behind the
    sweep glow. Returns (root, mat)."""
    import bmesh
    root = K.empty(name, (x0, y, z0))
    n = int(abs(x1 - x0) / pitch)
    mesh = bpy.data.meshes.new(name + "_slats")
    bm = bmesh.new()
    for i in range(n):
        x = -i * pitch if x1 < x0 else i * pitch
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((x + v.co.x * 0.007, v.co.y * depth, h / 2 + v.co.z * h))
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name + "_slats", mesh)
    K._link(o, root)
    m = K.principled(name + "_m", (0.02, 0.024, 0.032, 1), rough=0.25, coat=0.6, coat_rough=0.08)
    nt = m.node_tree
    b = K.bsdf(m)
    b.inputs["Emission Color"].default_value = K.SKY
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    sw = nt.nodes.new("ShaderNodeValue")
    sw.name = "sweep"
    sw.outputs[0].default_value = 1.0
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = 0.0
    sub = nt.nodes.new("ShaderNodeMath")
    sub.operation = "SUBTRACT"
    nt.links.new(sep.outputs["X"], sub.inputs[0])
    nt.links.new(sw.outputs[0], sub.inputs[1])
    # glow band: 1 at the sweep, fading over 0.8 m behind it (x > sweep), 0 ahead of it
    rng = nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = 0.0
    rng.inputs["From Max"].default_value = 0.8
    rng.inputs["To Min"].default_value = 1.0
    rng.inputs["To Max"].default_value = 0.08
    rng.clamp = True
    nt.links.new(sub.outputs[0], rng.inputs["Value"])
    ahead = nt.nodes.new("ShaderNodeMath")
    ahead.operation = "GREATER_THAN"
    ahead.inputs[1].default_value = 0.0
    nt.links.new(sub.outputs[0], ahead.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath")
    m1.operation = "MULTIPLY"
    nt.links.new(rng.outputs["Result"], m1.inputs[0])
    nt.links.new(ahead.outputs[0], m1.inputs[1])
    # a little vertical variation so it reads as many rows, not one block of light
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 18.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    m2 = nt.nodes.new("ShaderNodeMath")
    m2.operation = "MULTIPLY"
    nt.links.new(m1.outputs[0], m2.inputs[0])
    nt.links.new(nz.outputs["Fac"], m2.inputs[1])
    m3 = nt.nodes.new("ShaderNodeMath")
    m3.operation = "MULTIPLY"
    nt.links.new(m2.outputs[0], m3.inputs[0])
    nt.links.new(gv.outputs[0], m3.inputs[1])
    nt.links.new(m3.outputs[0], b.inputs["Emission Strength"])
    mesh.materials.append(m)
    # frame rails top and bottom
    L = abs(x1 - x0)
    cx = -L / 2 if x1 < x0 else L / 2
    # the front face: one fine line of light per row edge, lit by the same sweep band
    fm = K.principled(name + "_front", (0.015, 0.018, 0.024, 1), rough=0.3, coat=0.5, coat_rough=0.1)
    fn = fm.node_tree
    fb = K.bsdf(fm)
    fb.inputs["Emission Color"].default_value = K.SKY
    tc2 = fn.nodes.new("ShaderNodeTexCoord")
    sp2 = fn.nodes.new("ShaderNodeSeparateXYZ")
    fn.links.new(tc2.outputs["Object"], sp2.inputs[0])
    stripes = fn.nodes.new("ShaderNodeMath")
    stripes.operation = "PINGPONG"
    stripes.inputs[1].default_value = 0.5
    sc_ = fn.nodes.new("ShaderNodeMath")
    sc_.operation = "MULTIPLY"
    sc_.inputs[1].default_value = 1.0 / pitch
    fn.links.new(sp2.outputs["X"], sc_.inputs[0])
    fn.links.new(sc_.outputs[0], stripes.inputs[0])
    thin = fn.nodes.new("ShaderNodeMath")
    thin.operation = "LESS_THAN"
    thin.inputs[1].default_value = 0.12
    fn.links.new(stripes.outputs[0], thin.inputs[0])
    # the same band as the slats (sweep / glow values are linked by drivers below)
    sw2 = fn.nodes.new("ShaderNodeValue")
    sw2.name = "sweep"
    gv2 = fn.nodes.new("ShaderNodeValue")
    gv2.name = "glow"
    sub2 = fn.nodes.new("ShaderNodeMath")
    sub2.operation = "SUBTRACT"
    fn.links.new(sp2.outputs["X"], sub2.inputs[0])
    fn.links.new(sw2.outputs[0], sub2.inputs[1])
    r2 = fn.nodes.new("ShaderNodeMapRange")
    r2.inputs["From Min"].default_value = 0.0
    r2.inputs["From Max"].default_value = 1.2
    r2.inputs["To Min"].default_value = 1.0
    r2.inputs["To Max"].default_value = 0.1
    r2.clamp = True
    fn.links.new(sub2.outputs[0], r2.inputs["Value"])
    ah2 = fn.nodes.new("ShaderNodeMath")
    ah2.operation = "GREATER_THAN"
    fn.links.new(sub2.outputs[0], ah2.inputs[0])
    nz2 = fn.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 14.0
    fn.links.new(tc2.outputs["Object"], nz2.inputs["Vector"])
    prod = None
    for a_ in (r2.outputs["Result"], ah2.outputs[0], thin.outputs[0], nz2.outputs["Fac"], gv2.outputs[0]):
        if prod is None:
            prod = a_
            continue
        mm = fn.nodes.new("ShaderNodeMath")
        mm.operation = "MULTIPLY"
        fn.links.new(prod, mm.inputs[0])
        fn.links.new(a_, mm.inputs[1])
        prod = mm.outputs[0]
    fn.links.new(prod, fb.inputs["Emission Strength"])
    front = K.plane(name + "_frontface", L, h, fm, loc=(cx, -depth / 2 - 0.004, h / 2), parent=root)
    K.rbox(name + "_railb", (L + 0.05, depth + 0.04, 0.03), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(cx, 0, -0.015), parent=root)
    K.rbox(name + "_railt", (L + 0.05, depth + 0.04, 0.03), bevel=0.006, seg=3, mat=K.M("alu"), loc=(cx, 0, h + 0.015), parent=root)
    K.empty(name + "_pin", (0.0, -depth / 2, h + 0.05), parent=root)
    return root, m


def dial(name, loc, r=0.13):
    """A machined temperature dial standing on a small console, facing -Y. The knob turns about Y with
    <name>_knob.rotation_euler[1]. Ticks every 0.1 from 0 to 2 (major every 0.5) over -135..+135 degrees.
    Pins: <name>_t0, _t07, _t10, _t12 (tick positions), <name>_top."""
    root = K.empty(name, loc)
    K.rbox(name + "_base", (r * 3.0, 0.16, r * 3.2), bevel=0.02, seg=5, mat=K.M("alu_dark"), loc=(0, 0.06, 0), parent=root)
    face = K.cyl(name + "_face", r * 1.35, 0.012, K.M("graphite"), loc=(0, -0.026, 0), verts=64, bevel=0.002, parent=root)
    face.rotation_euler = (math.pi / 2, 0, 0)
    for k in range(21):
        T = k * 0.1
        a = math.radians(-135 + 270 * T / 2.0)
        major = k % 5 == 0
        L = 0.03 if major else 0.016
        rr = r * 1.22
        tk = K.rbox(f"{name}_tick{k}", (0.004 if major else 0.0025, 0.004, L), bevel=0.0008, seg=1, mat=K.M("alu"),
                    loc=(rr * math.sin(a), -0.034, rr * math.cos(a)), parent=root)
        tk.rotation_euler = (0, a, 0)
    for nm, T in (("t0", 0.0), ("t07", 0.7), ("t10", 1.0), ("t12", 1.2)):
        a = math.radians(-135 + 270 * T / 2.0)
        K.empty(f"{name}_{nm}", (r * 1.62 * math.sin(a), -0.04, r * 1.62 * math.cos(a)), parent=root)
    knob = K.empty(name + "_knob", (0, -0.04, 0), parent=root)
    body = K.cyl(name + "_kbody", r, 0.06, K.M("alu"), loc=(0, -0.03, 0), verts=96, bevel=0.006, parent=knob)
    body.rotation_euler = (math.pi / 2, 0, 0)
    for k in range(48):   # knurled grip
        a = 2 * math.pi * k / 48
        g = K.rbox(f"{name}_knurl{k}", (0.006, 0.05, 0.008), bevel=0.001, seg=1, mat=K.M("alu_dark"),
                   loc=(r * 1.01 * math.sin(a), -0.03, r * 1.01 * math.cos(a)), parent=knob)
        g.rotation_euler = (0, a, 0)
    ind_m = K.light_mat(name + "_ind", K.SKY, 4.0)
    K.rbox(name + "_ind", (0.008, 0.006, r * 0.7), bevel=0.002, seg=2, mat=ind_m, loc=(0, -0.062, r * 0.5), parent=knob)
    K.empty(name + "_top", (0, -0.05, r * 1.7), parent=root)
    return root, knob


def dial_angle(T):
    return math.radians(-135 + 270 * T / 2.0)
