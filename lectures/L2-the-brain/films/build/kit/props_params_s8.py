"""Props for the L2 films `params` and `s8_weights` (on top of l2kit).

  weight_sheet   a glass sheet whose face shows a real weight matrix, one cell per weight (image from capture_params.py),
                 with a procedural cell grid so single cells read at any zoom; machined aluminium frame; keyable 'glow'
  rgb_image      a cell image from a list of RGB colours (numpy; fast)
  cell_bar       a dark-glass bar of coloured cells (characters of the corpus), keyable 'glow' and 'reveal'
  card_stack     a stack of thin document cards with glowing edges (one kind of corpus text)
  slip           a thin glass slip lying on the plinth (one sampled stock line)
"""
import math

import bpy
import numpy as np

import l2kit as K


def _op(nt, kind, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = kind
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def grid_mat(name, img, cols, rows, strength=0.0, gw=0.08, base_mix=0.3, reveal=1.0, dim=0.1):
    """Emissive cell face from an image (Closest), darkened along cell borders (fraction gw of a cell) so every cell
    reads as its own tile when magnified. Keyable 'glow' and 'reveal' (cells lit in reading order, row-major)."""
    m = K.principled(name, (0.012, 0.014, 0.02, 1), rough=0.2, coat=0.7, coat_rough=0.05)
    nt = m.node_tree
    b = K.bsdf(m)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["UV"], tex.inputs["Vector"])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    fx = _op(nt, "FRACT", _op(nt, "MULTIPLY", sep.outputs["X"], cols))
    fy = _op(nt, "FRACT", _op(nt, "MULTIPLY", sep.outputs["Y"], rows))
    # inside = 1 when gw/2 < f < 1 - gw/2 on both axes
    ix = _op(nt, "MULTIPLY", _op(nt, "GREATER_THAN", fx, gw / 2), _op(nt, "LESS_THAN", fx, 1 - gw / 2))
    iy = _op(nt, "MULTIPLY", _op(nt, "GREATER_THAN", fy, gw / 2), _op(nt, "LESS_THAN", fy, 1 - gw / 2))
    inside = _op(nt, "ADD", 0.12, _op(nt, "MULTIPLY", _op(nt, "MULTIPLY", ix, iy), 0.88))
    col_i = _op(nt, "FLOOR", _op(nt, "MULTIPLY", sep.outputs["X"], cols * 0.99999))
    row_i = _op(nt, "FLOOR", _op(nt, "MULTIPLY", _op(nt, "SUBTRACT", 1.0, sep.outputs["Y"]), rows * 0.99999))
    idx = _op(nt, "ADD", _op(nt, "MULTIPLY", row_i, cols), col_i)
    rv = nt.nodes.new("ShaderNodeValue")
    rv.name = "reveal"
    rv.outputs[0].default_value = reveal
    lit = _op(nt, "LESS_THAN", idx, _op(nt, "MULTIPLY", rv.outputs[0], cols * rows))
    fac = _op(nt, "ADD", dim, _op(nt, "MULTIPLY", lit, 1 - dim))
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = strength
    stren = _op(nt, "MULTIPLY", _op(nt, "MULTIPLY", fac, gv.outputs[0]), inside)
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    nt.links.new(stren, b.inputs["Emission Strength"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = base_mix
    mix.inputs["A"].default_value = (0.012, 0.014, 0.02, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    return m


def load_image(name, path):
    img = bpy.data.images.load(path)
    img.name = name
    img.colorspace_settings.name = "sRGB"
    img.pack()
    return img


def rgb_image(name, rgb, cols, rows):
    """rgb: array (rows, cols, 3) in 0..1 (sRGB-ish); row 0 at the top. One pixel per cell."""
    a = np.asarray(rgb, np.float32).reshape(rows, cols, 3)
    img = bpy.data.images.new(name, cols, rows, alpha=False)
    px = np.ones((rows, cols, 4), np.float32)
    px[..., :3] = a[::-1]
    img.pixels.foreach_set(px.ravel())
    img.pack()
    return img


def weight_sheet(name, img, cols, rows, w, h, loc, glow=0.0, frame=0.012, depth=0.006, parent=None, gw=0.08):
    """A real weight matrix as a glass sheet standing in the XZ plane (facing -Y): `cols` x `rows` cells over w x h
    metres, row 0 at the top. Cells on the front face, a clear glass body behind, an aluminium frame and a foot.
    Returns (root, mat). Pins: <name>_top, <name>_bot, <name>_tl (top-left corner, front), <name>_mid."""
    root = K.empty(name, loc, parent)
    m = grid_mat(name + "_cells", img, cols, rows, strength=glow, gw=gw)
    K.plane(name + "_face", w, h, m, loc=(0, -depth / 2 - 0.0004, h / 2), parent=root)
    body = K.rbox(name + "_glass", (w, depth, h), bevel=min(0.0015, depth * 0.3), seg=2, mat=K.M("glass"), loc=(0, 0, h / 2), parent=root)
    body.visible_shadow = False
    t = frame
    fm = K.M("alu")
    for nm, sz, lc in (("_ft", (w + 2 * t, depth + 0.006, t), (0, 0, h + t / 2)), ("_fb", (w + 2 * t, depth + 0.006, t), (0, 0, -t / 2)),
                       ("_fl", (t, depth + 0.006, h), (-w / 2 - t / 2, 0, h / 2)), ("_fr", (t, depth + 0.006, h), (w / 2 + t / 2, 0, h / 2))):
        K.rbox(name + nm, sz, bevel=min(0.003, t * 0.3), seg=3, mat=fm, loc=lc, parent=root)
    K.empty(name + "_top", (0, -depth / 2, h + t + 0.01), parent=root)
    K.empty(name + "_bot", (0, -depth / 2, -t), parent=root)
    K.empty(name + "_tl", (-w / 2, -depth / 2 - 0.001, h), parent=root)
    K.empty(name + "_mid", (0, -depth / 2 - 0.001, h / 2), parent=root)
    return root, m


def cell_bar(name, rgb, cols, rows, cell, loc, glow=0.0, parent=None, depth=0.01, gw=0.12, reveal=1.0, frame=True, flat=False):
    """A bar / slab of coloured cells (cols x rows, cell metres each), in a graphite body with an aluminium rim.
    flat=True lays it face-up on the plinth (cells in the XY plane, row 0 at the back). Returns (root, mat)."""
    root = K.empty(name, loc, parent)
    img = rgb_image(name + "_img", rgb, cols, rows)
    m = grid_mat(name + "_cells", img, cols, rows, strength=glow, gw=gw, reveal=reveal)
    cw, ch = cell if isinstance(cell, (tuple, list)) else (cell, cell)
    W, H = cols * cw, rows * ch
    if flat:
        K.plane(name + "_face", W, H, m, loc=(0, 0, depth + 0.0006), rot=(-math.pi / 2, 0, 0), parent=root)
        K.rbox(name + "_body", (W + 0.004, H + 0.004, depth), bevel=0.0015, seg=2, mat=K.M("graphite"), loc=(0, 0, depth / 2), parent=root)
        if frame:
            K.rbox(name + "_rim", (W + 0.012, 0.004, depth + 0.003), bevel=0.0012, seg=2, mat=K.M("alu"), loc=(0, -H / 2 - 0.004, depth / 2), parent=root)
        K.empty(name + "_top", (0, -H / 2, depth + 0.004), parent=root)
        K.empty(name + "_l", (-W / 2, -H / 2, depth + 0.004), parent=root)
        K.empty(name + "_r", (W / 2, -H / 2, depth + 0.004), parent=root)
    else:
        K.plane(name + "_face", W, H, m, loc=(0, -depth / 2 - 0.0006, H / 2), parent=root)
        K.rbox(name + "_body", (W + 0.004, depth, H + 0.004), bevel=0.0015, seg=2, mat=K.M("graphite"), loc=(0, 0, H / 2), parent=root)
        if frame:
            t = 0.005
            for nm, sz, lc in (("_ft", (W + 2 * t, depth + 0.004, t), (0, 0, H + t / 2)), ("_fb", (W + 2 * t, depth + 0.004, t), (0, 0, -t / 2)),
                               ("_fl", (t, depth + 0.004, H), (-W / 2 - t / 2, 0, H / 2)), ("_fr", (t, depth + 0.004, H), (W / 2 + t / 2, 0, H / 2))):
                K.rbox(name + nm, sz, bevel=0.0015, seg=2, mat=K.M("alu"), loc=lc, parent=root)
        K.empty(name + "_top", (0, -depth / 2, H + 0.012), parent=root)
        K.empty(name + "_l", (-W / 2, -depth / 2, H / 2), parent=root)
        K.empty(name + "_r", (W / 2, -depth / 2, H / 2), parent=root)
    return root, m


def card_stack(name, loc, n, color, w=0.42, d=0.3, t=0.006, gap=0.0016, parent=None):
    """n thin document cards stacked on an aluminium tray, each with a glowing front edge (keyable 'glow' on one shared
    material). Returns (root, edge_mat, height). Pins: <name>_top, <name>_front."""
    root = K.empty(name, loc, parent)
    K.rbox(name + "_tray", (w + 0.05, d + 0.05, 0.016), bevel=0.005, seg=3, mat=K.M("alu_dark"), loc=(0, 0, 0.008), parent=root)
    K.rbox(name + "_lip", (w + 0.054, 0.006, 0.03), bevel=0.002, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.026, 0.015), parent=root)
    em = K.glow_mat(name + "_edge", color, 0.0)
    z = 0.016
    import random
    rnd = random.Random(len(name) * 7 + n)
    for i in range(n):
        dx, rz = rnd.uniform(-0.006, 0.006), rnd.uniform(-0.02, 0.02)
        c = K.rbox(f"{name}_c{i}", (w, d, t), bevel=0.0012, seg=2, mat=K.M("ceramic"), loc=(dx, 0, z + t / 2), parent=root)
        c.rotation_euler = (0, 0, rz)
        e = K.rbox(f"{name}_e{i}", (w * 0.96, 0.003, t * 0.8), bevel=0.0005, seg=1, mat=em, loc=(dx, -d / 2 - 0.0005, z + t / 2), parent=root)
        e.rotation_euler = (0, 0, rz)
        z += t + gap
    K.empty(name + "_top", (0, 0, z + 0.01), parent=root)
    K.empty(name + "_front", (0, -d / 2 - 0.03, z * 0.5), parent=root)
    return root, em, z


def slip(name, loc, color, w=0.34, d=0.12, parent=None):
    """A thin glass slip on an aluminium base with a glowing strip (one sampled line). Pins: <name>_top, <name>_front."""
    root = K.empty(name, loc, parent)
    K.rbox(name + "_base", (w, d, 0.012), bevel=0.003, seg=3, mat=K.M("graphite"), loc=(0, 0, 0.006), parent=root)
    m = K.glow_mat(name + "_face", color, 0.0, base=(0.018, 0.022, 0.03, 1))
    K.rbox(name + "_face", (w - 0.02, d - 0.02, 0.004), bevel=0.0015, seg=2, mat=m, loc=(0, 0, 0.0135), parent=root)
    K.rbox(name + "_rim", (w + 0.004, 0.004, 0.014), bevel=0.0015, seg=2, mat=K.M("alu"), loc=(0, -d / 2, 0.007), parent=root)
    K.empty(name + "_top", (0, 0, 0.02), parent=root)
    K.empty(name + "_front", (w / 2, -d / 2, 0.004), parent=root)
    return root, m
