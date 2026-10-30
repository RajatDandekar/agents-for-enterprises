"""Props for the L2 section films s1_game, s2_tokens, s3_vectors (built on the shared kit, l2kit)."""
import math

import bpy

import l2kit as K

K.ROLE.setdefault("answer", K.lin("#0b57d0"))   # tokens the model writes: deep blue band


def machine(name, loc, w=1.3, d=0.7, h=0.95, floors=24):
    """The sealed model: a dark anodised enclosure on a machined base, a frosted front window (keyable: the
    <name>_window object can slide up), a vented lid, input slot on the left, output slot on the right, an LED
    strip, and the 24-floor block stack inside. Returns dict(root, window, tower, led, slot_in_m, slot_out_m)."""
    root = K.empty(name, loc)
    shell = K.anod(name + "_shell", (0.05, 0.055, 0.068, 1), rough=0.32)
    t = 0.035
    K.rbox(name + "_base", (w + 0.08, d + 0.08, 0.04), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.02), parent=root)
    K.rbox(name + "_back", (w, t, h), bevel=0.01, seg=4, mat=shell, loc=(0, d / 2 - t / 2, 0.04 + h / 2), parent=root)
    for sx in (-1, 1):
        K.rbox(f"{name}_side{sx}", (t, d, h), bevel=0.01, seg=4, mat=shell, loc=(sx * (w / 2 - t / 2), 0, 0.04 + h / 2), parent=root)
        # the slot bezel (machined aluminium ring around a dark opening), at tile height
        K.rbox(f"{name}_bezel{sx}", (0.012, 0.32, 0.13), bevel=0.004, seg=3, mat=K.M("alu"), loc=(sx * (w / 2 + 0.003), 0, 0.105), parent=root)
        K.rbox(f"{name}_slot{sx}", (0.016, 0.27, 0.09), bevel=0.003, seg=2, mat=K.M("shadowgap"), loc=(sx * (w / 2 + 0.004), 0, 0.105), parent=root)
    lid = K.empty(name + "_lidroot", (0, 0, 0.04 + h + 0.02), parent=root)
    K.rbox(name + "_lid", (w + 0.02, d + 0.02, 0.05), bevel=0.016, seg=5, mat=shell, loc=(0, 0, 0), parent=lid)
    for k in range(9):
        K.rbox(f"{name}_vent{k}", (w * 0.7, 0.012, 0.006), bevel=0.002, seg=2, mat=K.M("shadowgap"),
               loc=(0, -d * 0.3 + k * d * 0.075, 0.026), parent=lid)
    # a soft light inside, so the stack glows through the window (energy keyable: <name>_inner.data.energy)
    import bpy as _b
    ld = _b.data.lights.new(name + "_inner", "AREA")
    ld.energy, ld.size, ld.color, ld.shape = 0.0, 0.5, (0.55, 0.72, 1.0), "DISK"
    lo = _b.data.objects.new(name + "_inner", ld)
    _b.context.collection.objects.link(lo)
    lo.parent = root
    lo.location = (0, 0.05, 0.04 + h - 0.08)
    lo.visible_glossy = False
    # front: an aluminium frame and a frosted window
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


def tray(name, x0, x1, y, z, depth=0.34):
    """A shallow machined tray (dark anodised with an aluminium lip) that the probability columns stand in."""
    L = x1 - x0
    root = K.empty(name, ((x0 + x1) / 2, y, z))
    K.rbox(name + "_bed", (L, depth, 0.02), bevel=0.006, seg=3, mat=K.M("alu_dark"), loc=(0, 0, 0.01), parent=root)
    K.rbox(name + "_lip", (L + 0.01, 0.01, 0.026), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -depth / 2, 0.013), parent=root)
    return root


def arc_path(obj, f0, a, b, lift, dur, hold_z=None):
    """Key a tile flying from a to b over an arc (up, across, down)."""
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    top = max(a.z, b.z) + lift
    pts = [(f0, a), (f0 + int(dur * 0.2), Vector((a.x, a.y, a.z + lift * 0.55))),
           (f0 + int(dur * 0.55), Vector(((a.x + b.x) / 2, (a.y + b.y) / 2, top))),
           (f0 + int(dur * 0.85), Vector((b.x, b.y, b.z + lift * 0.35))), (f0 + dur, b)]
    K.key(obj, "location", pts)


def rows_image(name, colors, px=4, width=64):
    """An image of horizontal rows, top row first: colors = [(r, g, b), ...]."""
    n = len(colors)
    W, H = width, n * px
    img = bpy.data.images.new(name, W, H, alpha=False)
    pix = [0.0] * (W * H * 4)
    for r, c in enumerate(colors):
        y0 = (n - 1 - r) * px
        for yy in range(y0, y0 + px - 1):
            base = yy * W * 4
            for xx in range(1, W - 1):
                k = base + xx * 4
                pix[k], pix[k + 1], pix[k + 2], pix[k + 3] = c[0], c[1], c[2], 1.0
    img.pixels.foreach_set(pix)
    img.pack()
    return img


def image_glow_mat(name, img, strength=0.0):
    """Dark glossy body whose emission is the image (keyable 'glow')."""
    m = K.principled(name, (0.012, 0.014, 0.02, 1), rough=0.22, coat=0.8, coat_rough=0.05)
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    uv = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = strength
    nt.links.new(tex.outputs["Color"], K.bsdf(m).inputs["Emission Color"])
    nt.links.new(gv.outputs[0], K.bsdf(m).inputs["Emission Strength"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["Factor"].default_value = 0.3
    mix.inputs["A"].default_value = (0.012, 0.014, 0.02, 1)
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], K.bsdf(m).inputs["Base Color"])
    return m


def rack_face_mat(name, bands=1187, color=K.SKY):
    """The vocabulary table's front: a fine ruling of `bands` bands (z from 0 at the bottom to 1 at the top, from the
    UV v), each band a soft lit strip with a dark separator. Keyable: 'glow' (strength) and 'sweep' (bands with
    v < sweep get a brighter light)."""
    m = K.principled(name, (0.012, 0.014, 0.02, 1), rough=0.25, coat=0.7, coat_rough=0.06)
    nt = m.node_tree
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])

    def op(kind, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = kind
        if isinstance(a, (int, float)):
            n.inputs[0].default_value = a
        else:
            nt.links.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, (int, float)):
                n.inputs[1].default_value = b
            else:
                nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    fr = op("FRACT", op("MULTIPLY", sep.outputs["Y"], float(bands)))
    line = op("GREATER_THAN", fr, 0.22)
    edge = op("GREATER_THAN", sep.outputs["X"], 0.02)
    edge2 = op("LESS_THAN", sep.outputs["X"], 0.98)
    lit = op("MULTIPLY", line, op("MULTIPLY", edge, edge2))
    sw = nt.nodes.new("ShaderNodeValue")
    sw.name = "sweep"
    sw.outputs[0].default_value = 0.0
    under = op("LESS_THAN", sep.outputs["Y"], sw.outputs[0])
    gain = op("ADD", 0.35, op("MULTIPLY", under, 2.2))
    gv = nt.nodes.new("ShaderNodeValue")
    gv.name = "glow"
    gv.outputs[0].default_value = 0.0
    st = op("MULTIPLY", op("MULTIPLY", lit, gain), gv.outputs[0])
    K.bsdf(m).inputs["Emission Color"].default_value = color
    nt.links.new(st, K.bsdf(m).inputs["Emission Strength"])
    return m
