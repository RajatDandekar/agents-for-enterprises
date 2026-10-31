"""Props for the L2 films `next_token` and `generation` (on top of the shared kit l2kit; nothing here changes l2kit).

  layered_column  a 1 x 16 vector column whose cells show a chosen layer of the residual stream (keyable 'layer')
  norm_unit       the final-RMSNorm unit: a short frosted-glass tunnel in machined frames the vector passes through
  tray_rack       the (tied) table as a rack of thin glass trays, one per row, each with its real 896 values
  hist_bars       the 151,936 logits as a histogram of glass bars (count per bin, log height)
  wheel           a weighted wheel: one glowing sector per token, sized by its probability
  cache_stack     a position's KV cache: a slender glass stack of 24 floors (key half violet, value half warm)
                  with a keyable build level ('level' in floors) and glow
  attn_sheet      a thin sheet of light at one floor height whose brightness along x follows real attention weights
  Temp            the temperature schedule for the meters (exact softmax at T from trace.json final.dial_last)
"""
import math

import bmesh
import bpy
from mathutils import Vector

import l2kit as K

K.ROLE.setdefault("answer", K.lin("#3c90ff"))
K.ROLE.setdefault("digit", K.lin("#c4511f"))
K.ROLE.setdefault("fact", K.lin("#1e8e5a"))


def _math(nt, kind, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = kind
    for idx, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[idx].default_value = v
        else:
            nt.links.new(v, n.inputs[idx])
    return n.outputs[0]


# ------------------------------------------------------------------------------------------------ layered column
def layered_mat(name, layers, color=K.SKY, vmaxs=None, px=12, gap=2):
    """A 1 x 16 cell material whose image holds every layer side by side (layer l = image column l). Keyable value
    node 'layer' (0..L-1, stepped) picks the column; 'glow' = emission strength."""
    L = len(layers)
    rows = len(layers[0])
    W, H = L * px, rows * px
    img = bpy.data.images.new(name + "_atlas", W, H, alpha=False)
    pix = [0.0] * (W * H * 4)
    for l, vals in enumerate(layers):
        vmax = (vmaxs[l] if vmaxs else max(abs(v) for v in vals)) or 1.0
        for r, val in enumerate(vals):
            t = min(1.0, abs(val) / vmax) ** 0.75
            c = color if val >= 0 else K.NEG
            rgb = [0.036 + 0.94 * t * c[i] for i in range(3)] if val >= 0 else [0.03 + 0.55 * t * c[i] / max(c[:3]) for i in range(3)]
            y0 = (rows - 1 - r) * px
            for yy in range(y0 + gap, y0 + px - gap):
                for xx in range(l * px + gap, l * px + px - gap):
                    k = (yy * W + xx) * 4
                    pix[k:k + 4] = [rgb[0], rgb[1], rgb[2], 1.0]
    img.pixels.foreach_set(pix)
    img.pack()
    m = K.principled(name, (0.012, 0.014, 0.02, 1), rough=0.22, coat=0.8, coat_rough=0.05)
    nt = m.node_tree
    b = K.bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    lay = nt.nodes.new("ShaderNodeValue")
    lay.name = "layer"
    lay.outputs[0].default_value = 0.0
    u = _math(nt, "DIVIDE", _math(nt, "ADD", _math(nt, "MULTIPLY", sep.outputs["X"], 0.999), _math(nt, "FLOOR", lay.outputs[0])), float(L))
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(comb.outputs[0], tex.inputs["Vector"])
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = 0.0
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(gv.outputs[0], b.inputs["Emission Strength"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = 0.35
    mix.inputs["A"].default_value = (0.012, 0.014, 0.02, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    return m


def layered_column(name, layers, loc, cell=0.022, vmaxs=None, parent=None, color=K.SKY):
    """A machined 1 x 16 column (as K.vector_plate) whose cells read `layers` (list of 16-value lists). Returns
    (root, mat). Pins: <name>_top, <name>_mid."""
    root = K.empty(name, loc, parent)
    W, H, depth = cell, 16 * cell, 0.014
    m = layered_mat(name + "_cells", layers, color, vmaxs)
    K.plane(name + "_face", W, H, m, loc=(0, -depth / 2 - 0.0012, 0), parent=root)
    K.rbox(name + "_back", (W + 0.004, depth, H + 0.004), bevel=0.002, seg=2, mat=K.M("graphite"), parent=root)
    t = 0.006
    for nm, sz, lc in (("_ft", (W + 2 * t, depth + 0.004, t), (0, 0, H / 2 + t / 2)), ("_fb", (W + 2 * t, depth + 0.004, t), (0, 0, -H / 2 - t / 2)),
                       ("_fl", (t, depth + 0.004, H), (-W / 2 - t / 2, 0, 0)), ("_fr", (t, depth + 0.004, H), (W / 2 + t / 2, 0, 0))):
        K.rbox(name + nm, sz, bevel=0.002, seg=2, mat=K.M("alu"), loc=lc, parent=root)
    K.empty(name + "_top", (0, 0, H / 2 + t + 0.01), parent=root)
    K.empty(name + "_mid", (0, -depth, 0), parent=root)
    return root, m


# ------------------------------------------------------------------------------------------------ the norm unit
def norm_unit(name, loc, length=0.62, h=0.66, w=0.22):
    """A short tunnel along x: two machined aluminium portal frames joined by frosted glass walls, a glowing sky ring
    inside each portal (keyable 'glow' on the returned material). The vector plate travels along x through it."""
    root = K.empty(name, loc)
    fr = 0.035
    for side, x in (("in", -length / 2), ("out", length / 2)):
        for nm, sz, lc in (("_t", (0.05, w + 2 * fr, fr), (x, 0, h / 2 + fr / 2)), ("_b", (0.05, w + 2 * fr, fr), (x, 0, -h / 2 - fr / 2)),
                           ("_l", (0.05, fr, h), (x, -w / 2 - fr / 2, 0)), ("_r", (0.05, fr, h), (x, w / 2 + fr / 2, 0))):
            K.rbox(f"{name}_{side}{nm}", sz, bevel=0.008, seg=4, mat=K.M("alu"), loc=lc, parent=root)
    ring = K.light_mat(name + "_ring", K.SKY, 0.0)
    for side, x in (("in", -length / 2), ("out", length / 2)):
        for nm, sz, lc in (("_rt", (0.012, w, 0.006), (x - 0.03 * (1 if side == "in" else -1), 0, h / 2 - 0.004)),
                           ("_rb", (0.012, w, 0.006), (x - 0.03 * (1 if side == "in" else -1), 0, -h / 2 + 0.004))):
            K.rbox(f"{name}_{side}{nm}", sz, bevel=0.002, seg=2, mat=ring, loc=lc, parent=root)
    frost = K.principled(name + "_frost", (0.8, 0.86, 0.95, 1), rough=0.42, transmission=1.0, ior=1.45)
    for nm, y in (("_wf", -w / 2 - 0.006), ("_wb", w / 2 + 0.006)):
        K.rbox(name + nm, (length - 0.05, 0.008, h), bevel=0.003, seg=2, mat=frost, loc=(0, y, 0), parent=root)
    K.rbox(name + "_roof", (length - 0.05, w + 0.02, 0.012), bevel=0.003, seg=2, mat=K.M("alu_dark"), loc=(0, 0, h / 2 + 0.006), parent=root)
    K.rbox(name + "_floor", (length - 0.05, w + 0.02, 0.012), bevel=0.003, seg=2, mat=K.M("alu_dark"), loc=(0, 0, -h / 2 - 0.006), parent=root)
    K.empty(name + "_top", (0, -w / 2, h / 2 + fr + 0.02), parent=root)
    K.empty(name + "_front", (0, -w / 2 - 0.02, 0), parent=root)
    # a stand to the plinth
    K.rbox(name + "_stand", (0.16, 0.12, loc[2] - h / 2 - fr), bevel=0.01, seg=3, mat=K.M("alu_dark"),
           loc=(0, 0, -(loc[2] - h / 2 - fr) / 2 - h / 2 - fr), parent=root)
    return root, ring


# ------------------------------------------------------------------------------------------------ the table rack
def tray_rack(name, rows, loc, cols=28, nrows=32, cell=0.012, pitch=0.042, vmax=0.06):
    """The table as a vertical rack of glass trays (each lying flat, face up, its cells glowing with the row's real
    values). rows: [{id, text, row}] top to bottom. Returns {"root", "trays": [(root, mat)], "z": [tray z]}.
    Pins: <name>_t<k>_front (front edge of tray k), <name>_top, <name>_side."""
    root = K.empty(name, loc)
    Wt, Dt = cols * cell, nrows * cell
    out = {"root": root, "trays": [], "z": []}
    n = len(rows)
    for k, rw in enumerate(rows):
        z = (n - 1 - k) * pitch
        tr = K.empty(f"{name}_t{k}", (0, 0, z), parent=root)
        m = K.cells_mat(f"{name}_t{k}_cells", rw["row"], cols, nrows, K.SKY, vmax=vmax, strength=0.0)
        face = K.plane(f"{name}_t{k}_face", Wt, Dt, m, loc=(0, 0, 0.0075), rot=(-math.pi / 2, 0, 0), parent=tr)
        K.rbox(f"{name}_t{k}_glass", (Wt + 0.02, Dt + 0.02, 0.012), bevel=0.003, seg=2, mat=K.M("graphite"), loc=(0, 0, 0), parent=tr)
        K.rbox(f"{name}_t{k}_lip", (Wt + 0.024, 0.008, 0.016), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -Dt / 2 - 0.014, 0.002), parent=tr)
        K.empty(f"{name}_t{k}_front", (0, -Dt / 2 - 0.02, 0.0), parent=tr)
        K.empty(f"{name}_t{k}_left", (-Wt / 2 - 0.02, -Dt / 2, 0.0), parent=tr)
        out["trays"].append((tr, m))
        out["z"].append(z)
    H = (n - 1) * pitch + 0.08
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rbox(f"{name}_post{sx}{sy}", (0.022, 0.022, H + 0.06), bevel=0.004, seg=3, mat=K.M("alu"),
                   loc=(sx * (Wt / 2 + 0.03), sy * (Dt / 2 + 0.01), H / 2 - 0.04), parent=root)
    K.rbox(name + "_foot", (Wt + 0.12, Dt + 0.12, 0.03), bevel=0.008, seg=3, mat=K.M("alu_dark"), loc=(0, 0, -0.06), parent=root)
    K.empty(name + "_top", (0, -Dt / 2, H + 0.02), parent=root)
    K.empty(name + "_side", (Wt / 2 + 0.05, -Dt / 2, H * 0.55), parent=root)
    return out


# ------------------------------------------------------------------------------------------------ the logit histogram
def hist_bars(name, counts, loc, pitch=0.05, hmax=0.62, hot_from=None, w=0.036, d=0.09):
    """One bar per bin, height = log10(1 + count) / log10(1 + max count) * hmax. Bars from index hot_from on glow sky
    (the tail). Every bar's height is keyed through <name>_b<k>.scale.z (0..1). Returns (root, [bars], [mats])."""
    root = K.empty(name, loc)
    lmax = math.log10(1 + max(counts))
    bars, mats = [], []
    cool = K.glow_mat(name + "_cool", K.lin("#8aa4c8"), 0.0, base=(0.05, 0.06, 0.08, 1))
    hot = K.glow_mat(name + "_hot", K.SKY, 0.0, base=(0.05, 0.06, 0.08, 1))
    for k, c in enumerate(counts):
        h = max(0.004, math.log10(1 + c) / lmax * hmax)
        piv = K.empty(f"{name}_b{k}", ((k - (len(counts) - 1) / 2) * pitch, 0, 0), parent=root)
        m = hot if (hot_from is not None and k >= hot_from) else cool
        K.rbox(f"{name}_b{k}_bar", (w, d, h), bevel=min(0.006, h * 0.45), seg=3, mat=m, loc=(0, 0, h / 2), parent=piv)
        K.empty(f"{name}_b{k}_top", (0, -d / 2, h + 0.01), parent=piv)
        piv.scale = (1, 1, 0.001)
        bars.append(piv)
    L = len(counts) * pitch
    K.rbox(name + "_base", (L + 0.08, d + 0.08, 0.02), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(0, 0, -0.01), parent=root)
    K.rbox(name + "_axis", (L + 0.08, 0.006, 0.006), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.045, 0.004), parent=root)
    return root, bars, (cool, hot)


# ------------------------------------------------------------------------------------------------ the weighted wheel
def wheel(name, sectors, loc, r=0.42, thick=0.04):
    """A vertical wheel facing -Y, centre at loc. sectors: [(key, p, color, strength)] clockwise from the top.
    The disk turns about Y via <name>_disk.rotation_euler[1]. A fixed pointer sits at the top. Pins (they turn with the
    disk): <name>_s<key> at each sector's middle (0.68 r). Returns (root, disk, {key: (start_deg, end_deg, mat)})."""
    root = K.empty(name, loc)
    disk = K.empty(name + "_disk", (0, 0, 0), parent=root)
    disk.rotation_mode = "XYZ"
    info = {}
    a = 0.0
    for key, p, color, stren in sectors:
        span = 360.0 * p
        a0, a1 = a, a + span
        m = K.glow_mat(f"{name}_m_{key}", color, stren, base=(0.03, 0.035, 0.045, 1))
        mesh = bpy.data.meshes.new(f"{name}_w_{key}")
        bm = bmesh.new()
        n = max(2, int(span / 2.5) + 1)
        gapd = min(0.35, span * 0.12)
        top_c, bot_c = bm.verts.new((0, -thick / 2, 0)), bm.verts.new((0, thick / 2, 0))
        ft, bk = [], []
        for i in range(n + 1):
            ang = math.radians(a0 + gapd + (span - 2 * gapd) * i / n)
            x, z = r * math.sin(ang), r * math.cos(ang)
            ft.append(bm.verts.new((x, -thick / 2, z)))
            bk.append(bm.verts.new((x, thick / 2, z)))
        for i in range(n):
            bm.faces.new((top_c, ft[i + 1], ft[i]))
            bm.faces.new((bot_c, bk[i], bk[i + 1]))
            bm.faces.new((ft[i], ft[i + 1], bk[i + 1], bk[i]))
        bm.faces.new((top_c, ft[0], bk[0], bot_c))
        bm.faces.new((top_c, bot_c, bk[-1], ft[-1]))
        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()
        o = bpy.data.objects.new(f"{name}_w_{key}", mesh)
        K._link(o, disk)
        mesh.materials.append(m)
        mid = math.radians((a0 + a1) / 2)
        K.empty(f"{name}_s{key}", (0.68 * r * math.sin(mid), -thick / 2 - 0.01, 0.68 * r * math.cos(mid)), parent=disk)
        info[key] = (a0, a1, m)
        a = a1
    hub = K.cyl(name + "_hub", r * 0.12, thick + 0.03, K.M("alu"), loc=(0, 0, 0), verts=48, bevel=0.004, parent=disk)
    hub.rotation_euler = (math.pi / 2, 0, 0)
    rim = bpy.ops.mesh.primitive_torus_add(major_radius=r + 0.012, minor_radius=0.012, location=(0, 0, 0))
    rim = bpy.context.active_object
    rim.name = name + "_rim"
    rim.data.materials.append(K.M("alu"))
    rim.parent = disk
    rim.rotation_euler = (math.pi / 2, 0, 0)
    for k in range(60):   # fine tick pins on the rim, every 6 degrees
        ang = math.radians(6 * k)
        t = K.rbox(f"{name}_tk{k}", (0.004, 0.006, 0.02), bevel=0.001, seg=1, mat=K.M("alu_dark"),
                   loc=((r + 0.03) * math.sin(ang), -thick / 2 - 0.005, (r + 0.03) * math.cos(ang)), parent=disk)
        t.rotation_euler = (0, ang, 0)
    # the pointer at the top (fixed), and the stand
    pm = K.light_mat(name + "_ptr", K.lin("#ffffff"), 3.0)
    ptr = K.rbox(name + "_pointer", (0.03, 0.05, 0.08), bevel=0.008, seg=3, mat=K.M("alu"), loc=(0, -0.01, r + 0.08), parent=root)
    K.rbox(name + "_ptrled", (0.008, 0.006, 0.05), bevel=0.002, seg=2, mat=pm, loc=(0, -0.04, r + 0.07), parent=root)
    K.empty(name + "_pin_ptr", (0, -0.04, r + 0.13), parent=root)
    K.rbox(name + "_post", (0.07, 0.07, loc[2]), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(0, thick / 2 + 0.05, -loc[2] / 2), parent=root)
    K.rbox(name + "_base", (0.5, 0.3, 0.03), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(0, 0.05, -loc[2] + 0.11 + 0.015), parent=root)
    return root, disk, info


def wheel_angle_for(info, key, frac=0.5):
    """Disk rotation (radians, about Y) that brings the point `frac` of sector `key` under the top pointer."""
    a0, a1, _ = info[key]
    return math.radians(a0 + (a1 - a0) * frac)


# ------------------------------------------------------------------------------------------------ the KV cache
def stack_mat(name, floors, strength=0.0, level=24.0):
    """Glass-stack material: 24 floor bands (thin dark gaps between), the -x half violet (keys), the +x half warm
    (values). Keyable 'glow' and 'level' (floors lit from the bottom, fractional = the band being built)."""
    m = K.principled(name, (0.02, 0.024, 0.034, 1), rough=0.2, coat=0.7, coat_rough=0.06)
    nt = m.node_tree
    b = K.bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    fz = _math(nt, "MULTIPLY", sep.outputs["Z"], float(floors))
    band = _math(nt, "LESS_THAN", _math(nt, "FRACT", fz), 0.8)             # gaps between floors
    lv = nt.nodes.new("ShaderNodeValue")
    lv.name = "level"
    lv.outputs[0].default_value = level
    built = _math(nt, "LESS_THAN", fz, lv.outputs[0])
    half = _math(nt, "GREATER_THAN", sep.outputs["X"], 0.5)
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    nt.links.new(half, mixc.inputs["Factor"])
    mixc.inputs["A"].default_value = K.lin("#8a55ff")
    mixc.inputs["B"].default_value = K.lin("#ffb35c")
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = strength
    s = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", band, built), gv.outputs[0])
    nt.links.new(mixc.outputs["Result"], b.inputs["Emission Color"])
    nt.links.new(s, b.inputs["Emission Strength"])
    return m


def cache_stack(name, loc, floors=24, pitch=0.042, w=0.2, d=0.07, mat=None):
    """A slender stack standing at loc (its bottom). One mesh (box) with the band material; thin aluminium caps.
    Returns (root, mat). Pins: <name>_f<k> (front middle of floor k, 1-based), <name>_top."""
    root = K.empty(name, loc)
    H = floors * pitch
    m = mat or stack_mat(name + "_m", floors)
    body = K.rbox(name + "_body", (w, d, H), bevel=0.004, seg=2, mat=m, loc=(0, 0, H / 2), parent=root)
    K.rbox(name + "_cap", (w + 0.012, d + 0.012, 0.01), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, 0, H + 0.005), parent=root)
    K.rbox(name + "_base", (w + 0.012, d + 0.012, 0.01), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, 0, 0.005), parent=root)
    for k in (21, 22, 23, 24, 12, 1):
        K.empty(f"{name}_f{k}", (0, -d / 2 - 0.005, (k - 0.5) * pitch), parent=root)
    K.empty(name + "_top", (0, -d / 2, H + 0.03), parent=root)
    return root, m


def attn_sheet(name, x0, x1, z, weights, xs, y=0.0, h=0.03, vmax=None, color=K.SKY):
    """A thin horizontal ribbon of light from x0 to x1 at height z; its brightness at x follows `weights` sampled at the
    positions `xs` (real attention weights, one per earlier position). Origin at x1 (the reading column), so scale.x
    0..1 grows it back toward x0. Keyable 'glow'. Returns (obj, mat)."""
    W = 1024
    img = bpy.data.images.new(name + "_img", W, 1, alpha=False)
    vm = vmax or max(weights) or 1.0
    pix = [0.0] * (W * 4)
    lo, hi = min(x0, x1), max(x0, x1)
    for px in range(W):
        x = lo + (hi - lo) * (px + 0.5) / W
        best = 0.0
        for wv, xp in zip(weights, xs):
            if abs(x - xp) < 0.11:
                best = max(best, wv)
        t = min(1.0, best / vm) ** 0.55
        v = 0.16 + 0.84 * t   # a faint continuous line: every earlier position is read, the bright spots carry the weight
        pix[px * 4:px * 4 + 4] = [v, v, v, 1.0]
    img.pixels.foreach_set(pix)
    img.pack()
    m = bpy.data.materials.new(name + "_m")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = 0.0
    sep = nt.nodes.new("ShaderNodeSeparateRGB") if hasattr(bpy.types, "ShaderNodeSeparateRGB") else nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex.outputs["Color"], sep.inputs[0])
    s = _math(nt, "MULTIPLY", sep.outputs[0], gv.outputs[0])
    nt.links.new(s, em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    fac = _math(nt, "MINIMUM", _math(nt, "MULTIPLY", s, 1.5), 1.0)
    nt.links.new(fac, mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    L = hi - lo
    # plane in XY (lying flat would be invisible from the side): stand it up in XZ, facing -Y
    mesh = bpy.data.meshes.new(name)
    sgn = 1 if x0 < x1 else -1   # the plane runs from the origin (x1) back toward x0
    verts = [(-sgn * L, 0, -h / 2), (0, 0, -h / 2), (0, 0, h / 2), (-sgn * L, 0, h / 2)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uvl = mesh.uv_layers.new(name="UVMap")
    us = [0.0, 1.0, 1.0, 0.0] if sgn > 0 else [1.0, 0.0, 0.0, 1.0]
    for li, (u, v) in enumerate(zip(us, [0, 0, 1, 1])):
        uvl.data[li].uv = (u, v)
    o = bpy.data.objects.new(name, mesh)
    K._link(o)
    o.location = (x1, y, z)
    mesh.materials.append(m)
    o.visible_shadow = False
    return o, m


# ------------------------------------------------------------------------------------------------ temperature
class Temp:
    """Probabilities of the top tokens at temperature T, exact: p_i(T) = exp(logit_i / T - logZ(T)), logZ over the whole
    vocabulary from trace.json final.dial_last (grid 0.1..2.0; T * logZ interpolated between grid points). T = 0 is
    the argmax."""

    def __init__(self, dial, ntop=6):
        self.top = dial["top"][:ntop]
        self.Tg, self.Zg = dial["T"], dial["logZ"]

    def logZ(self, T):
        g = self.Tg
        for i in range(len(g) - 1):
            if g[i] <= T <= g[i + 1]:
                u = (T - g[i]) / (g[i + 1] - g[i])
                a, b = g[i] * self.Zg[i], g[i + 1] * self.Zg[i + 1]
                return (a + (b - a) * u) / T
        return self.Zg[-1]

    def probs(self, T):
        if T < 0.1:
            p1 = self.probs(0.1)
            u = T / 0.1
            return [u * p + (1 - u) * (1.0 if j == 0 else 0.0) for j, p in enumerate(p1)]
        z = self.logZ(T)
        return [math.exp(t["logit"] / T - z) for t in self.top]


def keys_T(points):
    """[(frame, T)] -> a function T(frame), linear between points."""
    def T(fr):
        for (a, ta), (b, tb) in zip(points, points[1:]):
            if a <= fr <= b:
                return ta + (tb - ta) * (fr - a) / max(1, b - a)
        return points[-1][1] if fr > points[-1][0] else points[0][1]
    return T
