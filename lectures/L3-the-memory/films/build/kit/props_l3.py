"""Props for the Lecture 3 films ("The Knowledge"), on the shared series kit (l2kit) and the L4 props (props_l4: the model
machine, capsules, result slabs, rails, conduits, the padlock). All readable text stays 2D (overlay.py).

  vitrine       a glass display case on a machined base, holding a stack of sheets as tall as its real token count
  sheet_stack   the stack itself: paper (PDF, DOCX), pale-green ledger sheets (XLSX, CSV) or violet-edged cards (YAML, e-mail)
  paper         one document lying flat, its text as dark bars as long as its real lines (headings in sky)
  reader        the parser: an aluminium arch over a rail with a scan bar
  chunk_band    one chunk of a paper: a band that lifts off and becomes a ceramic tile with a sky header strip
  light_table   the vector space: a dark glass table whose beads sit at the real 2-D PCA positions of the chunk vectors
  catalogue     BM25: a card-catalogue cabinet; one drawer slides out with index cards that can rise and glow
  sorter        the reranker: a tall arch with a glowing reading beam
  screen        a dark monitor on a stand (Emma's desk: her presence, with an ember status bar)
  tablets       the wiki: many upright glass page tablets in one mesh (per-type colour on the top edge)
  tablet        one hero page tablet with its own keyable glow
  links_curve   every [[link]] as a thin light arc, one curve object (grow them with bevel_factor_end)
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import l2kit as K
import props_l4 as P

PAPER = (0.86, 0.85, 0.82, 1)
LEDGER = (0.74, 0.82, 0.76, 1)
CARD = (0.78, 0.76, 0.86, 1)
FOLDER_HEX = ["#3c90ff", "#9a5cff", "#1e8e5a", "#c4511f", "#e0a63a", "#5fc1d8", "#d46aa8", "#8fb357", "#7f8cff",
              "#d98f5c", "#4fb39a", "#b07ee0", "#c9c4bb", "#6b9bd1", "#e07a7a", "#9aa6b8"]
TYPE_HEX = {"policy": "#1e8e5a", "procedure": "#4fb39a", "manual": "#8a97ab", "release": "#7f8cff", "supplier": "#e0a63a",
            "item-family": "#d98f5c", "data-source": "#5fc1d8", "decision": "#d46aa8", "topic": "#b07ee0", "person": "#c9c4bb",
            "role": "#9aa6b8", "cost-centre": "#8fb357", "screen": "#3c90ff", "service-group": "#6b9bd1", "error": "#c4511f",
            "error-list": "#e07a7a"}


def _once(name, fn):
    return P._mat_once(name, fn)


def paper_mat(kind="paper"):
    col = {"paper": PAPER, "ledger": LEDGER, "card": CARD}[kind]
    return _once("sheet_" + kind, lambda: K.principled("sheet_" + kind, col, rough=0.62, sss=0.04))


def ink_mat():
    return _once("ink", lambda: K.principled("ink", (0.05, 0.055, 0.07, 1), rough=0.5))


# ------------------------------------------------------------------------------------------------ the archive
def sheet_stack(name, loc, height, kind="paper", w=0.26, d=0.2, pitch=0.0085, seed=1):
    """Sheets stacked to `height` (the data), each a thin bevelled slab with a tiny deterministic offset; ledger
    sheets carry a faint green rule on their front edge, cards a violet edge. Returns the root."""
    rnd = random.Random(seed)
    root = K.empty(name, loc)
    n = max(1, int(round(height / pitch)))
    th = pitch * 0.78
    edge = {"paper": None, "ledger": K.lin("#1e8e5a"), "card": K.lin("#9a5cff")}[kind]
    em = K.glow_mat(name + "_edge", edge, 0.35, base=(0.1, 0.12, 0.1, 1)) if edge else None
    for i in range(n):
        z = i * pitch + th / 2
        o = K.rbox(f"{name}_s{i}", (w * (0.97 + 0.03 * rnd.random()), d * (0.97 + 0.03 * rnd.random()), th), bevel=0.0012, seg=1,
                   mat=paper_mat(kind), loc=(rnd.uniform(-0.006, 0.006), rnd.uniform(-0.005, 0.005), z), parent=root)
        o.rotation_euler = (0, 0, rnd.uniform(-0.035, 0.035))
        if em and i % 2 == 0:
            K.rbox(f"{name}_r{i}", (w * 0.9, 0.0015, th * 0.4), bevel=0.0, seg=1, mat=em, loc=(0, -d / 2 - 0.0008, 0), parent=o)
    K.empty(name + "_top", (0, -d / 2, n * pitch + 0.01), parent=root)
    return root


def vitrine(name, loc, h, w=0.36, d=0.3):
    """A glass case on a dark machined base with aluminium posts and a top cap. Inner floor at loc.z + 0.05."""
    root = K.empty(name, loc)
    K.rbox(name + "_base", (w + 0.08, d + 0.08, 0.05), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, 0.025), parent=root)
    K.rbox(name + "_trim", (w + 0.084, 0.008, 0.01), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.04, 0.042), parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rbox(f"{name}_post{sx}{sy}", (0.018, 0.018, h), bevel=0.004, seg=3, mat=K.M("alu"),
                   loc=(sx * (w / 2 + 0.009), sy * (d / 2 + 0.009), 0.05 + h / 2), parent=root)
    for nm, sz, lc in (("_pf", (w, 0.005, h), (0, -d / 2 - 0.003, 0.05 + h / 2)), ("_pb", (w, 0.005, h), (0, d / 2 + 0.003, 0.05 + h / 2)),
                       ("_pl", (0.005, d, h), (-w / 2 - 0.003, 0, 0.05 + h / 2)), ("_pr", (0.005, d, h), (w / 2 + 0.003, 0, 0.05 + h / 2))):
        K.rbox(name + nm, sz, bevel=0.0015, seg=1, mat=K.M("glass"), loc=lc, parent=root).visible_shadow = False
    K.rbox(name + "_cap", (w + 0.05, d + 0.05, 0.022), bevel=0.007, seg=3, mat=K.M("alu"), loc=(0, 0, 0.05 + h + 0.011), parent=root)
    led = K.glow_mat(name + "_led", K.SKY, 0.4)
    K.rbox(name + "_ledbar", (w * 0.6, 0.005, 0.006), bevel=0.0015, seg=1, mat=led, loc=(0, -d / 2 - 0.026, 0.05 + h + 0.011), parent=root)
    K.empty(name + "_pin", (0, -d / 2 - 0.03, 0.05 + h + 0.04), parent=root)
    K.empty(name + "_foot", (w / 2 + 0.04, -d / 2 - 0.04, 0.03), parent=root)
    K.empty(name + "_mid", (w / 2 + 0.01, -d / 2 - 0.01, 0.05 + min(h * 0.5, 0.42)), parent=root)
    return {"root": root, "led": led}


# ------------------------------------------------------------------------------------------------ one document
def paper(name, loc, groups, w=0.3, h=0.42, margin=0.022, lh=0.0105, cpl=64, kind="paper"):
    """A document lying flat (long side along y, top edge at +y). `groups`: list of line lists (one per chunk); each
    line {len, head}. Every line is a dark bar as long as the real line (cpl characters = full width); heading lines
    (in brackets) are sky bars. Each group's bars share one keyable material, and each group has a band empty so a
    scene can split the paper. Returns dict(root, groups=[{mat, head_mat, bars:[...], y0, y1}], sheet)."""
    root = K.empty(name, loc)
    sheet = K.rbox(name + "_sheet", (w, h, 0.003), bevel=0.0012, seg=1, mat=paper_mat(kind), loc=(0, 0, 0.0015), parent=root)
    out = {"root": root, "sheet": sheet, "groups": []}
    y = h / 2 - margin
    full = w - 2 * margin
    for gi, lines in enumerate(groups):
        gm = K.glow_mat(f"{name}_g{gi}", K.SKY, 0.0, base=(0.05, 0.055, 0.07, 1))
        hm = K.glow_mat(f"{name}_h{gi}", K.SKY, 0.6, base=(0.08, 0.25, 0.6, 1))
        y0 = y
        bars = []
        for li, ln in enumerate(lines):
            L = max(0.012, full * min(1.0, ln["len"] / cpl))
            o = K.rbox(f"{name}_g{gi}_l{li}", (L, lh * 0.42, 0.0012), bevel=0.0, seg=1, mat=hm if ln["head"] else gm,
                       loc=(-w / 2 + margin + L / 2, y, 0.0036), parent=root)
            bars.append(o)
            y -= lh
            if y < -h / 2 + margin:
                break
        out["groups"].append({"mat": gm, "head_mat": hm, "bars": bars, "y0": y0 + lh / 2, "y1": y + lh / 2})
        y -= lh * 0.6
    K.empty(name + "_top", (0, h / 2, 0.01), parent=root)
    K.empty(name + "_mid", (0, 0, 0.01), parent=root)
    return out


def reader(name, loc, span=0.5, h=0.26, d=0.2):
    """The parser: two machined pillars and a bridge over the rail; a glass scan bar under the bridge (keyable
    location y and 'glow'), a status ring on the front. Returns dict(root, scan, scan_m, ring)."""
    root = K.empty(name, loc)
    for sx in (-1, 1):
        K.rbox(f"{name}_pil{sx}", (0.045, d, h), bevel=0.01, seg=4, mat=_once(name + "_an", lambda: K.anod(name + "_an", (0.2, 0.22, 0.27, 1))),
               loc=(sx * (span / 2 + 0.035), 0, h / 2), parent=root)
        K.rbox(f"{name}_trim{sx}", (0.049, 0.008, h * 0.86), bevel=0.003, seg=2, mat=K.M("alu"),
               loc=(sx * (span / 2 + 0.035), -d / 2 - 0.002, h / 2), parent=root)
    K.rbox(name + "_bridge", (span + 0.12, d, 0.045), bevel=0.012, seg=4, mat=K.M("alu"), loc=(0, 0, h + 0.03), parent=root)
    for k in range(7):
        K.rbox(f"{name}_vent{k}", (span * 0.7, 0.008, 0.004), bevel=0.001, seg=1, mat=K.M("shadowgap"),
               loc=(0, -d * 0.3 + k * d * 0.1, h + 0.061), parent=root)
    scan_m = K.light_mat(name + "_scan", K.SKY, 0.0)
    scan = K.rbox(name + "_scanbar", (span, 0.012, 0.006), bevel=0.0, seg=1, mat=scan_m, loc=(0, 0, h - 0.004), parent=root)
    scan.visible_shadow = False
    beam_m = K.light_mat(name + "_beam", K.SKY, 0.0)
    bm = K.rbox(name + "_sheetlight", (span, 0.006, h - 0.02), bevel=0.0, seg=1, mat=beam_m, loc=(0, 0, (h - 0.02) / 2), parent=scan)
    bm.location = (0, 0, -(h - 0.02) / 2)
    bm.visible_shadow = False
    ring = K.glow_mat(name + "_ring", K.SKY, 0.5)
    K.rbox(name + "_ringbar", (span * 0.5, 0.006, 0.01), bevel=0.002, seg=1, mat=ring, loc=(0, -d / 2 - 0.004, h + 0.03), parent=root)
    K.empty(name + "_pin", (0, -d / 2, h + 0.07), parent=root)
    return {"root": root, "scan": scan, "scan_m": scan_m, "beam_m": beam_m, "ring": ring}


def tile(name, loc, size, header=True, lines=(), cpl=64):
    """A chunk as a ceramic tile: bevelled body, a dark recessed face with its text lines as faint bars, a sky header
    strip along its top-left (the context header). Returns dict(root, face_m, head_m, edge_m)."""
    root = K.empty(name, loc)
    w, d, h = size
    K.rbox(name + "_body", (w, d, h), bevel=min(0.01, h * 0.4), seg=4, mat=K.M("ceramic"), loc=(0, 0, h / 2), parent=root)
    face_m = K.glow_mat(name + "_face", K.SKY, 0.0, base=(0.018, 0.022, 0.03, 1))
    K.bsdf(face_m).inputs["Roughness"].default_value = 0.2
    K.rbox(name + "_face", (w - 0.024, d - 0.024, 0.004), bevel=0.002, seg=2, mat=face_m, loc=(0, 0, h - 0.0005), parent=root)
    edge_m = K.light_mat(name + "_edge", K.GREEN, 0.0)
    for nm, sz, lc in (("_e1", (w * 0.96, 0.004, 0.004), (0, -d / 2 - 0.0015, h * 0.55)), ("_e2", (w * 0.96, 0.004, 0.004), (0, d / 2 + 0.0015, h * 0.55))):
        K.rbox(name + nm, sz, bevel=0.0, seg=1, mat=edge_m, loc=lc, parent=root).visible_shadow = False
    head_m = K.light_mat(name + "_head", K.SKY, 1.2 if header else 0.0)
    if header:
        K.rbox(name + "_hd", ((w - 0.05) * 0.55, 0.008, 0.0016), bevel=0.0, seg=1, mat=head_m,
               loc=(-(w - 0.05) * 0.225, d / 2 - 0.024, h + 0.0022), parent=root).visible_shadow = False
    tm = _once("tileink", lambda: K.light_mat("tileink", (0.75, 0.8, 0.9, 1), 0.35))
    full = w - 0.06
    for i, ln in enumerate(list(lines)[:max(0, int((d - 0.06) / 0.009))]):
        L = max(0.01, full * min(1.0, ln["len"] / cpl))
        K.rbox(f"{name}_t{i}", (L, 0.0035, 0.0012), bevel=0.0, seg=1, mat=head_m if ln["head"] else tm,
               loc=(-full / 2 + L / 2, d / 2 - 0.04 - i * 0.009, h + 0.002), parent=root).visible_shadow = False
    K.empty(name + "_top", (0, 0, h + 0.012), parent=root)
    K.empty(name + "_front", (0, -d / 2 - 0.004, 0.004), parent=root)
    return {"root": root, "face_m": face_m, "head_m": head_m, "edge_m": edge_m}


# ------------------------------------------------------------------------------------------------ the vector space
def light_table(name, loc, points, size=1.5, legs=0.42, hexes=FOLDER_HEX, bead=0.0055):
    """A dark glass table (top at loc.z + legs + 0.03) with one bead per point [u, v, folder] (u, v in -0.5..0.5), all in
    one mesh with a per-bead colour attribute; the beads' light is the keyable 'glow' of the returned material.
    Returns dict(root, beads, bead_m, top_z, to_world(u, v))."""
    root = K.empty(name, loc)
    top_z = legs + 0.03
    glass = _once("tabletop", lambda: K.principled("tabletop", (0.02, 0.025, 0.035, 1), rough=0.12, coat=0.9, coat_rough=0.04))
    K.rbox(name + "_top", (size + 0.12, size + 0.12, 0.03), bevel=0.01, seg=4, mat=glass, loc=(0, 0, legs + 0.015), parent=root)
    K.rbox(name + "_rim", (size + 0.13, size + 0.13, 0.008), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, 0, legs + 0.002), parent=root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.rbox(f"{name}_leg{sx}{sy}", (0.035, 0.035, legs), bevel=0.006, seg=3, mat=K.M("alu_dark"),
                   loc=(sx * (size / 2 - 0.02), sy * (size / 2 - 0.02), legs / 2), parent=root)
    # faint grid on the glass (decorative axes of the PCA plane)
    gm = _once("tablegrid", lambda: K.light_mat("tablegrid", (0.35, 0.45, 0.65, 1), 0.08))
    for k in range(9):
        t = -size / 2 + k * size / 8
        K.rbox(f"{name}_gx{k}", (size, 0.0012, 0.0006), bevel=0.0, seg=1, mat=gm, loc=(0, t, top_z + 0.0003), parent=root).visible_shadow = False
        K.rbox(f"{name}_gy{k}", (0.0012, size, 0.0006), bevel=0.0, seg=1, mat=gm, loc=(t, 0, top_z + 0.0003), parent=root).visible_shadow = False
    mesh = bpy.data.meshes.new(name + "_beads")
    bm = bmesh.new()
    cl = bm.loops.layers.color.new("col")
    cols = [K.lin(h) for h in hexes]
    for u, v, f in points:
        r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=bead)
        c = cols[int(f) % len(cols)]
        for vt in r["verts"]:
            vt.co += Vector((u * size, v * size, top_z + bead * 1.1))
        for fc in {f_ for vt in r["verts"] for f_ in vt.link_faces}:
            for lp in fc.loops:
                lp[cl] = c
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(name + "_beads", mesh)
    bpy.context.collection.objects.link(ob)
    ob.parent = root
    ob.visible_shadow = False
    bead_m = bpy.data.materials.new(name + "_beadm")
    bead_m.use_nodes = True
    nt = bead_m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    em = nt.nodes.new("ShaderNodeEmission")
    g = nt.nodes.new("ShaderNodeValue")
    g.name = "glow"
    g.outputs[0].default_value = 0.0
    nt.links.new(at.outputs["Color"], em.inputs["Color"])
    nt.links.new(g.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    mesh.materials.append(bead_m)

    def to_world(u, v, dz=0.0):
        return Vector((loc[0] + u * size, loc[1] + v * size, loc[2] + top_z + dz))
    K.empty(name + "_pin", (0, -size / 2 - 0.06, top_z + 0.02), parent=root)
    return {"root": root, "beads": ob, "bead_m": bead_m, "top_z": loc[2] + top_z, "to_world": to_world}


def ring(name, loc, r=0.02, color=K.SKY):
    """A thin glowing ring lying flat (for the hits around the query on the light table)."""
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.0016, major_segments=40, minor_segments=8, location=loc)
    o = bpy.context.active_object
    o.name = name
    m = K.light_mat(name + "_m", color, 0.0)
    o.data.materials.append(m)
    o.visible_shadow = False
    return o, m


def star(name, loc, r=0.016, color=K.SKY):
    """The query point: a small bright octahedron-ish gem."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=0, radius=r)
    for v in bm.verts:
        v.co.z *= 1.6
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.location = loc
    m = K.light_mat(name + "_m", color, 0.0)
    mesh.materials.append(m)
    o.visible_shadow = False
    return o, m


# ------------------------------------------------------------------------------------------------ BM25
def catalogue(name, loc, cols=4, rows=5, w=0.62, d=0.42, h=0.78, open_row=2, open_col=1, cards=14):
    """A card-catalogue cabinet: graphite carcass on a plinth, a grid of drawers with aluminium label frames and
    pulls. Drawer (open_row, open_col) is its own object (key its location y to slide it out) and holds index cards;
    each card is (obj, glow_mat). Returns dict(root, drawer, drawer_closed, drawer_open, cards)."""
    root = K.empty(name, loc)
    car = _once("cat_wood", lambda: K.principled("cat_wood", (0.06, 0.05, 0.045, 1), rough=0.42, coat=0.6, coat_rough=0.12))
    K.rbox(name + "_plinth", (w + 0.06, d + 0.06, 0.06), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(0, 0, 0.03), parent=root)
    K.rbox(name + "_body", (w, d, h), bevel=0.01, seg=4, mat=car, loc=(0, 0, 0.06 + h / 2), parent=root)
    K.rbox(name + "_capt", (w + 0.03, d + 0.03, 0.03), bevel=0.008, seg=3, mat=K.M("alu"), loc=(0, 0, 0.06 + h + 0.015), parent=root)
    dw, dh = (w - 0.04) / cols, (h - 0.04) / rows
    drawer = None
    for r_ in range(rows):
        for c in range(cols):
            x = -w / 2 + 0.02 + dw * (c + 0.5)
            z = 0.06 + 0.02 + dh * (r_ + 0.5)
            is_open = (r_ == open_row and c == open_col)
            dr = K.empty(f"{name}_dr{r_}{c}", (x, -d / 2, z), parent=root)
            K.rbox(f"{name}_dr{r_}{c}_f", (dw - 0.012, 0.02, dh - 0.012), bevel=0.004, seg=3, mat=car, loc=(0, -0.008, 0), parent=dr)
            K.rbox(f"{name}_dr{r_}{c}_lab", (dw * 0.42, 0.006, dh * 0.22), bevel=0.0015, seg=2, mat=K.M("alu"), loc=(0, -0.019, dh * 0.16), parent=dr)
            K.rbox(f"{name}_dr{r_}{c}_labin", (dw * 0.36, 0.004, dh * 0.15), bevel=0.0, seg=1, mat=paper_mat("paper"), loc=(0, -0.021, dh * 0.16), parent=dr)
            p = K.cyl(f"{name}_dr{r_}{c}_pull", 0.008, 0.016, K.M("alu"), loc=(0, -0.026, -dh * 0.14), verts=20, parent=dr)
            p.rotation_euler = (math.pi / 2, 0, 0)
            if is_open:
                drawer = dr
                # the drawer's box behind its front, with index cards standing in it
                K.rbox(f"{name}_dr_box", (dw - 0.02, d * 0.9, dh * 0.7), bevel=0.003, seg=2, mat=car, loc=(0, d * 0.45, -dh * 0.1), parent=dr)
                cl = []
                for k in range(cards):
                    cm = K.glow_mat(f"{name}_card{k}_m", K.GREEN, 0.0, base=(0.8, 0.79, 0.75, 1))
                    co = K.rbox(f"{name}_card{k}", (dw - 0.034, 0.0022, dh * 0.62), bevel=0.0008, seg=1, mat=cm,
                                loc=(0, 0.03 + k * (d * 0.85 / cards), dh * 0.08), parent=dr)
                    cl.append((co, cm))
    dz = drawer.location.copy()
    return {"root": root, "drawer": drawer, "drawer_closed": dz, "drawer_open": dz + Vector((0, -d * 0.7, 0)), "cards": cl}


def sorter(name, loc, span=0.62, h=0.46, d=0.2):
    """The reranker: a tall dark-glass arch on aluminium feet with a reading beam across its throat (keyable 'glow')."""
    root = K.empty(name, loc)
    an = K.anod(name + "_an", (0.07, 0.06, 0.1, 1), rough=0.28)
    for sx in (-1, 1):
        K.rbox(f"{name}_post{sx}", (0.06, d, h), bevel=0.014, seg=4, mat=an, loc=(sx * (span / 2 + 0.03), 0, h / 2), parent=root)
        K.rbox(f"{name}_foot{sx}", (0.12, d + 0.06, 0.03), bevel=0.008, seg=3, mat=K.M("alu"), loc=(sx * (span / 2 + 0.03), 0, 0.015), parent=root)
    K.rbox(name + "_head", (span + 0.12, d, 0.08), bevel=0.02, seg=5, mat=an, loc=(0, 0, h + 0.04), parent=root)
    K.rbox(name + "_headtrim", (span + 0.124, 0.006, 0.012), bevel=0.003, seg=2, mat=K.M("alu"), loc=(0, -d / 2 - 0.002, h + 0.04), parent=root)
    beam_m = K.light_mat(name + "_beam", lin_violet(), 0.0)
    b = K.rbox(name + "_beam", (span, 0.004, h - 0.08), bevel=0.0, seg=1, mat=beam_m, loc=(0, 0, (h - 0.08) / 2 + 0.06), parent=root)
    b.visible_shadow = False
    led = K.glow_mat(name + "_led", lin_violet(), 0.6)
    K.rbox(name + "_ledbar", (span * 0.5, 0.006, 0.008), bevel=0.002, seg=1, mat=led, loc=(0, -d / 2 - 0.004, h + 0.015), parent=root)
    K.empty(name + "_pin", (0, -d / 2, h + 0.09), parent=root)
    return {"root": root, "beam_m": beam_m, "led": led}


def lin_violet():
    return K.lin("#9a5cff")


# ------------------------------------------------------------------------------------------------ Emma's desk
def screen(name, loc, w=0.62, h=0.38):
    """A slim dark monitor on an aluminium stand (Emma's presence). Its face is a dark glass panel with a faint form
    layout (decorative bars) and an ember status bar along the bottom (keyable 'glow'). Faces -Y."""
    root = K.empty(name, loc)
    K.rbox(name + "_foot", (0.22, 0.16, 0.012), bevel=0.004, seg=3, mat=K.M("alu"), loc=(0, 0.02, 0.006), parent=root)
    K.rbox(name + "_neck", (0.04, 0.02, 0.22), bevel=0.006, seg=3, mat=K.M("alu"), loc=(0, 0.04, 0.12), parent=root)
    body = K.anod(name + "_an", (0.03, 0.033, 0.04, 1), rough=0.3)
    K.rbox(name + "_body", (w, 0.022, h), bevel=0.008, seg=4, mat=body, loc=(0, 0.02, 0.2 + h / 2), parent=root)
    face = _once("screen_face", lambda: K.principled("screen_face", (0.01, 0.012, 0.018, 1), rough=0.08, coat=1.0, coat_rough=0.02))
    K.rbox(name + "_face", (w - 0.03, 0.004, h - 0.03), bevel=0.002, seg=1, mat=face, loc=(0, 0.008, 0.2 + h / 2), parent=root)
    ui = _once("screen_ui", lambda: K.light_mat("screen_ui", (0.5, 0.62, 0.85, 1), 0.5))
    rnd = random.Random(7)
    for k in range(7):     # a form: label + field rows (decorative)
        z = 0.2 + h - 0.06 - k * 0.034
        K.rbox(f"{name}_lab{k}", (0.07, 0.002, 0.008), bevel=0.0, seg=1, mat=ui, loc=(-w / 2 + 0.07, 0.005, z), parent=root).visible_shadow = False
        K.rbox(f"{name}_fld{k}", (0.12 + 0.18 * rnd.random(), 0.002, 0.016), bevel=0.0, seg=1, mat=ui,
               loc=(-w / 2 + 0.25 + 0.05, 0.005, z), parent=root).visible_shadow = False
    st = K.light_mat(name + "_status", K.EMBER, 0.0)
    K.rbox(name + "_statusbar", (w - 0.06, 0.002, 0.03), bevel=0.0, seg=1, mat=st, loc=(0, 0.005, 0.2 + 0.035), parent=root).visible_shadow = False
    K.empty(name + "_pin", (0, 0.0, 0.2 + 0.035), parent=root)
    K.empty(name + "_toppin", (0, 0.0, 0.2 + h + 0.02), parent=root)
    return {"root": root, "status": st}


# ------------------------------------------------------------------------------------------------ the wiki
TW, TD, TH = 0.087, 0.01, 0.117   # one page tablet (metres)


def _tablet_bm(bm, x, y, rot, z0, scale=1.0, col=None, cl=None):
    w, d, h = TW * scale, TD * scale, TH * scale
    r = bmesh.ops.create_cube(bm, size=1.0)
    ca, sa = math.cos(rot), math.sin(rot)
    for v in r["verts"]:
        lx, ly, lz = v.co.x * w, v.co.y * d, v.co.z * h + h / 2
        v.co = Vector((x + lx * ca - ly * sa, y + lx * sa + ly * ca, z0 + lz))
    if cl is not None and col is not None:
        for f in {f_ for v in r["verts"] for f_ in v.link_faces}:
            for lp in f.loops:
                lp[cl] = col
    return r


def tablets(name, slugs, pos, z0, mat):
    """Many page tablets in ONE mesh (frosted glass), standing at pos[slug] = [x, y, rot]. Returns the object."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for s in slugs:
        x, y, rot = pos[s]
        _tablet_bm(bm, x, y, rot, z0)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    md = o.modifiers.new("bevel", "BEVEL")
    md.width, md.segments, md.limit_method = 0.0016, 2, "NONE"
    mesh.materials.append(mat)
    return o


def tablet_tops(name, slugs, pos, types, z0, strength=0.0):
    """The coloured top edge of each tablet (its page type), one mesh with a colour attribute and a keyable 'glow'."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    cl = bm.loops.layers.color.new("col")
    for s in slugs:
        x, y, rot = pos[s]
        r = bmesh.ops.create_cube(bm, size=1.0)
        ca, sa = math.cos(rot), math.sin(rot)
        for v in r["verts"]:
            lx, ly, lz = v.co.x * TW * 0.9, v.co.y * (TD + 0.0012), v.co.z * 0.0035 + TH - 0.006
            v.co = Vector((x + lx * ca - ly * sa, y + lx * sa + ly * ca, z0 + lz))
        c = K.lin(TYPE_HEX[types[s]])
        for f in {f_ for v in r["verts"] for f_ in v.link_faces}:
            for lp in f.loops:
                lp[cl] = c
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.visible_shadow = False
    m = bpy.data.materials.new(name + "_m")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "col"
    em = nt.nodes.new("ShaderNodeEmission")
    g = nt.nodes.new("ShaderNodeValue")
    g.name = "glow"
    g.outputs[0].default_value = strength
    nt.links.new(at.outputs["Color"], em.inputs["Color"])
    nt.links.new(g.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    mesh.materials.append(m)
    return o, m


def tablet_mat():
    return _once("tablet_glass", lambda: K.principled("tablet_glass", (0.86, 0.9, 0.97, 1), rough=0.28, transmission=0.85, ior=1.45))


def tablet(name, loc, rot=0.0, scale=1.0, color=K.SKY, lines=9):
    """One hero page tablet: frosted glass slab on an aluminium foot, faint text bars on its face, a glowing top edge
    and a keyable inner glow. Returns dict(root, edge_m, core_m)."""
    root = K.empty(name, loc)
    root.rotation_euler = (0, 0, rot)
    w, d, h = TW * scale, TD * scale, TH * scale
    K.rbox(name + "_glass", (w, d, h), bevel=0.0016 * scale, seg=2, mat=tablet_mat(), loc=(0, 0, h / 2), parent=root)
    K.rbox(name + "_foot", (w * 1.04, d * 2.2, h * 0.05), bevel=0.001 * scale, seg=2, mat=K.M("alu"), loc=(0, 0, h * 0.025), parent=root)
    edge_m = K.light_mat(name + "_edge", color, 1.0)
    K.rbox(name + "_top", (w * 0.9, d + 0.0012 * scale, 0.0035 * scale), bevel=0.0, seg=1, mat=edge_m, loc=(0, 0, h - 0.006 * scale),
           parent=root).visible_shadow = False
    core_m = K.light_mat(name + "_core", color, 0.0)
    K.rbox(name + "_core", (w * 0.84, d * 0.4, h * 0.8), bevel=0.0, seg=1, mat=core_m, loc=(0, 0, h * 0.47), parent=root).visible_shadow = False
    bars = _once("tablet_bars", lambda: K.light_mat("tablet_bars", (0.7, 0.76, 0.88, 1), 0.25))
    rnd = random.Random(hash(name) & 0xffff)
    for k in range(lines):
        L = w * (0.45 + 0.4 * rnd.random()) if k else w * 0.5
        K.rbox(f"{name}_bar{k}", (L, 0.0006 * scale, 0.0022 * scale), bevel=0.0, seg=1, mat=bars,
               loc=(-w * 0.42 + L / 2, -d / 2 - 0.0004 * scale, h * (0.82 - k * 0.075)), parent=root).visible_shadow = False
    K.empty(name + "_top", (0, 0, h + 0.006 * scale), parent=root)
    K.empty(name + "_front", (0, -d / 2 - 0.002, 0.003), parent=root)
    return {"root": root, "edge_m": edge_m, "core_m": core_m}


def links_curve(name, segs, mat, r=0.0009, lift=0.12, per=0.12):
    """Every link as one bezier spline (a -> b, rising lift + per * distance); one curve object. Grow all of them with
    K.grow(obj, keys) (bevel_factor_end, mapped per spline)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 1
    cu.resolution_u = 10
    cu.bevel_factor_mapping_end = "SPLINE"
    for a, b in segs:
        a, b = Vector(a), Vector(b)
        top = max(a.z, b.z) + lift + per * (b - a).length
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(1)
        p0, p1 = sp.bezier_points
        p0.co, p1.co = a, b
        for p in (p0, p1):
            p.handle_left_type = p.handle_right_type = "FREE"
        p0.handle_right = Vector((a.x + (b.x - a.x) * 0.2, a.y + (b.y - a.y) * 0.2, top))
        p0.handle_left = a - (p0.handle_right - a)
        p1.handle_left = Vector((b.x - (b.x - a.x) * 0.2, b.y - (b.y - a.y) * 0.2, top))
        p1.handle_right = b - (p1.handle_left - b)
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    cu.materials.append(mat)
    o.visible_shadow = False
    cu.bevel_factor_end = 0.0
    return o


def beads(name, centers, r, mat, z=0.0):
    """Small spheres at many points, one mesh (e.g. the lint flags above flagged tablets)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for c in centers:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in res["verts"]:
            v.co += Vector((c[0], c[1], c[2] + z))
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    mesh.materials.append(mat)
    o.visible_shadow = False
    return o


def dais(name, loc, r=3.0, h=0.06):
    """The wiki's floor: a wide dark round dais with an aluminium edge."""
    root = K.empty(name, loc)
    K.cyl(name + "_top", r, h, K.M("plinth"), loc=(0, 0, h / 2), verts=160, bevel=0.01, parent=root)
    K.cyl(name + "_edge", r + 0.012, 0.012, K.M("alu"), loc=(0, 0, h - 0.008), verts=160, parent=root)
    return root
