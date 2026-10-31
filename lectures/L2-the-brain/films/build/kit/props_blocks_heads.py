"""Props for the L2 films `blocks` (Inside the stack: every token, 24 blocks) and `heads` (fourteen ways of looking),
on top of the shared kit l2kit. Owned by those two films only.

  column_row   100 machined columns (one per token) whose cells glow with real values; ONE shared material reads an atlas
               (layer x position x 16 values), so a whole row can switch to the next block's vectors with one key, or wipe
               across the row (x < wipe shows layer B).
  facade       the stack as a building: 24 floors spanning all 100 positions; each floor = an attention band (14 head
               lanes) over an MLP band (one fin module behind every position); a logit-lens eyepiece at the right end.
"""
import math

import bmesh
import bpy
from mathutils import Vector

import l2kit as K

PITCH = 0.36
PZ = 0.11


def X(i, last=99):
    return (i - last) * PITCH


def _math(nt, kind, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = kind
    for k, v in ((0, a), (1, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[k].default_value = v
        else:
            nt.links.new(v, n.inputs[k])
    return n.outputs[0]


def _val(nt, name, v):
    n = nt.nodes.new("ShaderNodeValue")
    n.name = name
    n.outputs[0].default_value = v
    return n.outputs[0]


def atlas_image(name, layers, ncol, nrow, color=K.SKY, gamma=0.75, skip_pct=(0,)):
    """layers[L][col][row] -> an image ncol x (L*nrow), 1 px per cell, linear RGB like l2kit.cells_image (positive =
    `color` by size, negative = slate). Each layer is normalised by its own 95th percentile (position 0, the attention
    sink with huge values, is left out of the percentile)."""
    L = len(layers)
    img = bpy.data.images.new(name, ncol, L * nrow, alpha=False, float_buffer=True)
    pix = [0.0] * (ncol * L * nrow * 4)
    neg = K.NEG
    for l, lay in enumerate(layers):
        a = sorted(abs(x) for c, colv in enumerate(lay) if c not in skip_pct for x in colv)
        vmax = a[int(len(a) * 0.95)] or 1.0
        for c in range(ncol):
            for r in range(nrow):
                v = lay[c][r]
                t = min(1.0, abs(v) / vmax) ** gamma
                lift = 0.06
                rgb = [lift * 0.6 + (1 - lift) * t * color[i] for i in range(3)] if v >= 0 else \
                      [lift * 0.5 + 0.55 * t * neg[i] / max(neg[:3]) for i in range(3)]
                y = l * nrow + (nrow - 1 - r)      # value 0 at the top of the column
                k = (y * ncol + c) * 4
                pix[k:k + 4] = [rgb[0], rgb[1], rgb[2], 1.0]
    img.pixels.foreach_set(pix)
    img.pack()
    return img


def atlas_mat(name, img, ncol, nrow, nlayers, glow=3.8, last_col=99):
    """The shared column-face material. Keyable values: glow, layerA, layerB, wipe (world x: x < wipe shows layerB),
    focus (0..1: dims every column but `last_col`), flash + fx (a band of extra light around world x = fx),
    hl + hlc (extra light on column index hlc)."""
    m = K.principled(name, (0.012, 0.014, 0.02, 1), rough=0.22, coat=0.8, coat_rough=0.05)
    nt = m.node_tree
    b = K.bsdf(m)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gs = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gs.inputs[0])
    u, v, wx = sep.outputs["X"], sep.outputs["Y"], gs.outputs["X"]
    col = _math(nt, "FLOOR", _math(nt, "MULTIPLY", u, ncol * 0.99999))
    rowb = _math(nt, "FLOOR", _math(nt, "MULTIPLY", v, nrow * 0.99999))
    la, lb, wipe = _val(nt, "layerA", 0.0), _val(nt, "layerB", 0.0), _val(nt, "wipe", -1000.0)
    useb = _math(nt, "LESS_THAN", wx, wipe)
    lay = _math(nt, "FLOOR", _math(nt, "ADD", _math(nt, "MULTIPLY", useb, _math(nt, "SUBTRACT", lb, la)), _math(nt, "ADD", la, 0.01)))
    ty = _math(nt, "DIVIDE", _math(nt, "ADD", _math(nt, "ADD", _math(nt, "MULTIPLY", lay, nrow), rowb), 0.5), nlayers * nrow)
    tx = _math(nt, "DIVIDE", _math(nt, "ADD", col, 0.5), ncol)
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tx, cmb.inputs[0])
    nt.links.new(ty, cmb.inputs[1])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tex.extension = "EXTEND"
    nt.links.new(cmb.outputs[0], tex.inputs["Vector"])
    # cell gaps
    fu = _math(nt, "FRACT", _math(nt, "MULTIPLY", u, ncol))
    fv = _math(nt, "FRACT", _math(nt, "MULTIPLY", v, nrow))
    mask = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", fu, 0.12), _math(nt, "LESS_THAN", fu, 0.88)),
                 _math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", fv, 0.09), _math(nt, "LESS_THAN", fv, 0.91)))
    mask = _math(nt, "ADD", 0.08, _math(nt, "MULTIPLY", mask, 0.92))
    gv = _val(nt, "glow", glow)
    focus = _val(nt, "focus", 0.0)
    notlast = _math(nt, "GREATER_THAN", _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", col, float(last_col))), 0.5)
    dim = _math(nt, "SUBTRACT", 1.0, _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", focus, notlast), 0.88))
    flash, fx = _val(nt, "flash", 0.0), _val(nt, "fx", -1000.0)
    band = _math(nt, "MAXIMUM", 0.0, _math(nt, "SUBTRACT", 1.0, _math(nt, "DIVIDE", _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", wx, fx)), 0.4)))
    hl, hlc = _val(nt, "hl", 0.0), _val(nt, "hlc", -5.0)
    ishl = _math(nt, "LESS_THAN", _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", col, hlc)), 0.5)
    boost = _math(nt, "ADD", _math(nt, "ADD", 1.0, _math(nt, "MULTIPLY", flash, band)), _math(nt, "MULTIPLY", hl, ishl))
    stren = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", gv, mask), dim), boost)
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(stren, b.inputs["Emission Strength"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = 0.3
    mix.inputs["A"].default_value = (0.012, 0.014, 0.02, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    return m


def column_row(name, positions, layers, nrow=16, cell=0.03, y=0.0, z=0.0, glow=3.8):
    """One machined column per position (alu frame, graphite body, a face of nrow cells reading the shared atlas).
    Returns {"car": carrier empty, "roots": {i: root}, "mat": face material, "h": column height}.
    Pins: <name><i>_top, <name><i>_bot, <name><i>_mid (front)."""
    ncol = len(layers[0])
    img = atlas_image(name + "_atlas", layers, ncol, nrow)
    m = atlas_mat(name + "_face", img, ncol, nrow, len(layers), glow=glow)
    car = K.empty(name, (0, y, z))
    W, H = cell, cell * nrow
    roots = {}
    alu, gra = K.M("alu"), K.M("graphite")
    for i in positions:
        r = K.empty(f"{name}{i}", (X(i), 0, 0), parent=car)
        K.rbox(f"{name}{i}_frame", (W + 0.016, 0.03, H + 0.016), bevel=0.004, seg=3, mat=alu, loc=(0, 0.004, 0), parent=r)
        K.rbox(f"{name}{i}_body", (W + 0.004, 0.032, H + 0.004), bevel=0.0015, seg=2, mat=gra, loc=(0, 0.0, 0), parent=r)
        # the face: a plane whose UVs cover this column's slice of the atlas
        mesh = bpy.data.meshes.new(f"{name}{i}_face")
        verts = [(-W / 2, 0, -H / 2), (W / 2, 0, -H / 2), (W / 2, 0, H / 2), (-W / 2, 0, H / 2)]
        mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
        uvl = mesh.uv_layers.new(name="UVMap")
        u0, u1 = i / ncol, (i + 1) / ncol
        for li, uvv in zip(range(4), [(u0, 0), (u1, 0), (u1, 1), (u0, 1)]):
            uvl.data[li].uv = uvv
        mesh.materials.append(m)
        o = bpy.data.objects.new(f"{name}{i}_face", mesh)
        K._link(o, r)
        o.location = (0, -0.0175, 0)
        K.empty(f"{name}{i}_top", (0, 0, H / 2 + 0.02), parent=r)
        K.empty(f"{name}{i}_bot", (0, -0.02, -H / 2 - 0.02), parent=r)
        K.empty(f"{name}{i}_mid", (0, -0.03, 0), parent=r)
        roots[i] = r
    return {"car": car, "roots": roots, "mat": m, "h": H}


def set_layer(m, keys):
    """keys: [(frame, layer)] as holds: the layer switches exactly at each frame (bezier-safe: a hold key one frame
    before every change)."""
    s = m.node_tree.nodes["layerA"].outputs[0]
    prev = None
    for f, lv in keys:
        if prev is not None:
            K.keyval(s, [(f - 1, prev)])
        K.keyval(s, [(f, lv)])
        prev = lv


def sweep_mat(name, color, glow=0.0):
    """Dark body with emission = glow + flash * (a 0.5 m band around world x = sx) + done * (x < sx)."""
    m = K.principled(name, (0.02, 0.022, 0.028, 1), rough=0.3, coat=0.5, coat_rough=0.1)
    nt = m.node_tree
    b = K.bsdf(m)
    b.inputs["Emission Color"].default_value = color
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    gs = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], gs.inputs[0])
    wx = gs.outputs["X"]
    gv, fl, sx, dn = _val(nt, "glow", glow), _val(nt, "flash", 0.0), _val(nt, "sx", -1000.0), _val(nt, "done", 0.0)
    band = _math(nt, "MAXIMUM", 0.0, _math(nt, "SUBTRACT", 1.0, _math(nt, "DIVIDE", _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", wx, sx)), 0.5)))
    behind = _math(nt, "LESS_THAN", wx, sx)
    s = _math(nt, "ADD", _math(nt, "ADD", gv, _math(nt, "MULTIPLY", fl, band)), _math(nt, "MULTIPLY", dn, behind))
    nt.links.new(s, b.inputs["Emission Strength"])
    return m


def _boxes(name, boxes, mats, parent=None):
    """One mesh from many boxes: boxes = [(center, size, mat_index)]."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for c, s, mi in boxes:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    bm.to_mesh(mesh)
    bm.free()
    for mt in mats:
        mesh.materials.append(mt)
    o = bpy.data.objects.new(name, mesh)
    K._link(o, parent)
    md = o.modifiers.new("bevel", "BEVEL")
    md.width = 0.003
    md.segments = 2
    md.limit_method = "ANGLE"
    return o


def facade(name, floors=24, z1=1.0, fp=1.05, x0=None, x1=0.62, y=0.42, heads=14, positions=100, detail=(1,)):
    """The 24-floor stack as one building facade behind the row. Floor k (1-based) base at z1 + (k-1)*fp; attention
    band centred at +0.30 (14 lanes), MLP band at +0.78 (one fin module behind every position). Per floor keyable
    materials lane_<k> (sky, glow) and mlp_<k> (warm, sweep_mat). Lens eyepiece at the right end: lens_<k>.
    Returns dict with z (floor base), za, zm, lane, mlp, lens lists. Pins: <name>_att<k>, <name>_mlp<k>, <name>_lens<k>,
    <name>_left<k> (left end)."""
    x0 = X(0) - 0.5 if x0 is None else x0
    L = x1 - x0
    cx = (x0 + x1) / 2
    root = K.empty(name, (0, 0, 0))
    out = {"root": root, "z": [], "za": [], "zm": [], "lane": [], "mlp": [], "lens": [], "floors": []}
    back = K.M("alu_dark")
    for k in range(1, floors + 1):
        zb = z1 + (k - 1) * fp
        fr = K.empty(f"{name}_f{k}", (0, 0, 0), parent=root)
        za, zm = zb + 0.30, zb + 0.78
        lane = K.glow_mat(f"lane_{k}", K.SKY, 0.0)
        mlp = sweep_mat(f"mlp_{k}", K.lin("#ffd79a"))
        lens = K.light_mat(f"lens_{k}", K.SKY, 0.0)
        # back wall of the floor + the floor trim (a shelf lip) + a thin divider between attention and MLP
        boxes = [((cx, y + 0.06, zb + fp / 2), (L, 0.08, fp - 0.02), 0),
                 ((cx, y - 0.02, zb + 0.005), (L + 0.02, 0.2, 0.03), 1),
                 ((cx, y - 0.0, zb + 0.54), (L, 0.06, 0.012), 1)]
        # 14 head lanes (rods) in the attention band
        lanes = [((cx, y - 0.03, za - 0.17 + j * (0.34 / (heads - 1))), (L - 0.04, 0.014, 0.009), 2) for j in range(heads)]
        # MLP modules: one behind every position (body + 5 fins), and a warm LED strip under each
        mods = []
        nd = positions if k in detail else 0
        for i in range(nd):
            xi = X(i)
            mods.append(((xi, y - 0.01, zm), (0.27, 0.07, 0.34), 3))
            for f in range(5):
                mods.append(((xi - 0.1 + f * 0.05, y - 0.06, zm + 0.02), (0.012, 0.06, 0.28), 1))
            mods.append(((xi, y - 0.06, zm - 0.15), (0.24, 0.012, 0.012), 4))
        if not nd:   # plain floors: one long fin bank and one LED strip
            for i in range(0, positions, 1):
                xi = X(i)
                mods.append(((xi, y - 0.01, zm), (0.27, 0.07, 0.3), 3))
                mods.append(((xi, y - 0.06, zm - 0.13), (0.24, 0.012, 0.012), 4))
        _boxes(f"{name}_f{k}_wall", boxes + lanes, [back, K.M("alu"), lane], parent=fr)
        _boxes(f"{name}_f{k}_mlp", mods, [back, K.M("alu"), lane, K.M("graphite"), mlp], parent=fr)
        # lens eyepiece at the right end
        bar = K.cyl(f"{name}_f{k}_lens", 0.085, 0.09, K.M("alu"), loc=(x1 + 0.12, y - 0.14, za), verts=32, bevel=0.003, parent=fr)
        bar.rotation_euler = (math.pi / 2, 0, 0)
        core = K.cyl(f"{name}_f{k}_lenscore", 0.062, 0.094, lens, loc=(x1 + 0.12, y - 0.14, za), verts=24, parent=fr)
        core.rotation_euler = (math.pi / 2, 0, 0)
        K.rbox(f"{name}_f{k}_lensarm", (0.12, 0.05, 0.03), bevel=0.006, seg=2, mat=K.M("alu"), loc=(x1 + 0.05, y - 0.06, za), parent=fr)
        K.empty(f"{name}_lens{k}", (x1 + 0.12, y - 0.19, za), parent=fr)
        K.empty(f"{name}_att{k}", (X(92), y - 0.05, za + 0.17), parent=fr)
        K.empty(f"{name}_mlp{k}", (X(92), y - 0.05, zm + 0.17), parent=fr)
        K.empty(f"{name}_left{k}", (x0 + 0.2, y - 0.05, za), parent=fr)
        out["z"].append(zb)
        out["za"].append(za)
        out["zm"].append(zm)
        out["lane"].append(lane)
        out["mlp"].append(mlp)
        out["lens"].append(lens)
        out["floors"].append(fr)
    # side pillars
    H = floors * fp + 0.1
    for sx, xx in (("l", x0 - 0.08), ("r", x1 + 0.3)):
        K.rbox(f"{name}_pillar{sx}", (0.14, 0.24, H), bevel=0.02, seg=3, mat=K.M("alu"), loc=(xx, y, z1 - 0.05 + H / 2), parent=root)
    out["top"] = z1 + floors * fp
    return out


def arc_set(prefix, src, dst_of, weights, color, min_w=0.004, rmax=0.022, rmin=0.003, ref=0.35, lift0=0.14):
    """Light arcs from src to dst_of(j) for each weight >= min_w. Returns {j: (obj, mat, w)}."""
    out = {}
    for j, wgt in weights.items():
        if wgt < min_w:
            continue
        dst = dst_of(j)
        dist = (dst - src).length
        r = rmin + (rmax - rmin) * math.sqrt(min(1.0, wgt / ref))
        mj = K.light_mat(f"{prefix}{j}_m", color, 0.0)
        out[j] = (K.arc(f"{prefix}{j}", src, dst, lift=lift0 + 0.08 * math.sqrt(dist) + 0.05 * dist, r=r, mat=mj), mj, wgt)
    return out


def light_arcs(arcs, f_on, f_off, src_i, gain=7.0, ref=0.35, stagger=0.25, fade=14, floor_g=0.25):
    for j, (o, m_, wgt) in arcs.items():
        d = int(abs(src_i - j) * stagger)
        g = floor_g + gain * min(1.0, (wgt / ref)) ** 0.6
        K.grow(o, [(0, 0.0), (f_on + d, 0.0), (f_on + d + 16, 1.0)])
        K.glow_keys(m_, [(0, 0.0), (f_on + d, 0.0), (f_on + d + 6, g), (f_off, g), (f_off + fade, 0.0)])
        K.show(o, [(0, False), (f_on + d - 2, True), (f_off + fade + 2, False)])


def backdrop(name, x, y, z0, z1, width, color=(0.055, 0.064, 0.088), strength=1.0, fade=0.3):
    """A tall emissive slate wall far behind the set (faces -Y), transparent at its bottom edge and fading in over the
    lowest `fade` of its height, so high shots get a deep slate ground instead of black without a visible seam."""
    h = z1 - z0
    m = bpy.data.materials.new(name + "_m")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = fade
    nt.links.new(sep.outputs["Y"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    o = K.plane(name, width, h, m, loc=(x, y, z0 + h / 2))
    o.visible_shadow = False
    try:
        o.visible_diffuse = False
        o.visible_glossy = False
    except Exception:
        pass
    return o
