"""Film s3, "Each token becomes a vector". Builds films/s3_vectors.blend.

b1 the " Manchester" tile (id 19361) looks up its row in the embedding table: a row lights on the rack and its
   vector slides out to the tile.
b2 every question token stands up its vector: a dark-glass slab of 896 cells (28 x 32) glowing with the real
   input-embedding values (qkv_data.json vectors.embedding); " battery" and " Manchester" light up in turn.
   System-prompt tiles carry the first 16 of their 896 values (trace embeddings.values v16), labelled as such.
b3 the slabs collapse to points and fly into a meaning map: the 3D PCA of trace embeddings.pca (46 reference words +
   the prompt tokens; 3 components explain 6.0 / 5.8 / 4.8 % of the variance).
b4 clusters: bike parts, places, days and months.
b5 nearest neighbours by cosine (trace embeddings.neighbours): battery and Manchester, each with a fan of its top 6.
b6 the row of columns again, every column a point in meaning; faint threads hint at the next section.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s123 as P  # noqa: E402

FILM = "s3_vectors"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
D = K.load("films/qkv_data.json")
TOK = T["tokens"]
N = len(TOK)
LAST = N - 1
EMB = D["vectors"]["embedding"]           # positions 80..99, all 896 values
V16 = {v["i"]: v["v16"] for v in T["embeddings"]["values"]}
PCA = T["embeddings"]["pca"]
NB = T["embeddings"]["neighbours"]
BATT, MAN = 86, 92
w = B.w
END = B.frames - 1
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5", "b6")}

PZ = 0.11
PITCH = 0.36
ZT = PZ + 0.075
SW, SH = 28 * 0.009, 32 * 0.009          # slab size
ZS = ZT + 0.04 + SH / 2
MAPC = Vector((2.15, 0.55, 1.05))         # centre of the meaning map
MS = 5.5                                  # metres per PCA unit
GROUPC = {"bike parts": K.SKY, "places": K.K_COL, "purchasing": K.V_COL, "time": K.lin("#5fd3ff"),
          "numbers": K.lin("#9aa8c0"), "animals": K.lin("#c9c4bb")}


def X(i):
    return (i - LAST) * PITCH


def mp(xyz):
    return MAPC + Vector((xyz[0] * MS, xyz[2] * MS, xyz[1] * MS))


sc = K.reset(B.frames)
K.studio(sc, focus=(-1.0, 0.0, 0.5), key_power=3000, span=20.0)
K.plinth("plinth", X(0) - 0.45, 0.45, depth=0.5, height=PZ)

faces, slabs = {}, {}
for t in TOK:
    i = t["i"]
    r, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    faces[i] = fm
    K.glow_keys(fm, [(0, 0.0)])
    if str(i) in EMB:
        pr, pm = K.vector_plate(f"vec{i}", EMB[str(i)], 28, 32, K.SKY, (X(i), 0.0, ZS), cell=0.009, vmax=0.03, glow=0.0, reveal=0.0)
    else:
        pr, pm = K.vector_plate(f"vec{i}", V16[i], 4, 4, K.SKY, (X(i), 0.0, ZT + 0.09), cell=0.03, vmax=0.03, glow=0.0, reveal=1.0)
    pr.scale = (0.001,) * 3
    slabs[i] = (pr, pm)

# ---------------------------------------------------------------- the embedding table (b1)
RX, RY, RH, RW = X(MAN) + 0.2, 1.55, 2.0, 1.3
rack = K.empty("rack", (RX, RY, PZ))
K.rbox("rack_body", (RW + 0.08, 0.6, RH + 0.08), bevel=0.02, seg=4, mat=K.anod("rack_shell", (0.05, 0.055, 0.068, 1)), loc=(0, 0, RH / 2 + 0.04), parent=rack)
rface = P.rack_face_mat("rack_face", bands=1187)
K.plane("rack_faceplane", RW, RH, rface, loc=(0, -0.302, RH / 2 + 0.04), parent=rack)
zrow = 0.04 + RH * (1 - 19361 / 151936)                  # row 0 at the top
row_m = K.light_mat("row_m", K.SKY, 0.0)
rowbar = K.rbox("rowbar", (RW, 0.004, 0.012), bevel=0.0, seg=1, mat=row_m, loc=(0, -0.306, zrow), parent=rack)
K.empty("rack_pin_row", (RW / 2, -0.31, zrow), parent=rack)
K.empty("rack_pin_top", (RW / 2, -0.31, RH), parent=rack)
f_tok0, f_row, f_table = w("b1", "token", 0), w("b1", "row"), w("b1", "table")
K.glow_keys(rface, [(0, 0.12)])
K.show(rack, [(0, True), (b["b3"]["f0"], False)])
K.glow_keys(row_m, [(0, 0.0), (f_row - 6, 0.0), (f_row + 4, 6.0), (b["b2"]["f0"] + 40, 3.0), (b["b2"]["f0"] + 70, 0.0)])
K.glow_keys(faces[MAN], [(f_tok0 - 6, 0.0), (f_tok0 + 8, 1.6), (b["b2"]["f0"], 1.6), (b["b2"]["f0"] + 30, 0.4)])
look_m = K.light_mat("look_m", K.SKY, 0.0)
look = K.beam("look", (X(MAN), 0.0, ZT + 0.01), (RX, RY - 0.31, PZ + zrow), r=0.004, mat=look_m)
look.scale = (1, 1, 0.001)
K.key(look, "scale", [(0, (1, 1, 0.001)), (f_row - 16, (1, 1, 0.001)), (f_row, (1, 1, 1.0))])
K.glow_keys(look_m, [(0, 0.0), (f_row - 16, 3.0), (f_table + 30, 3.0), (f_table + 50, 0.0)])
K.show(look, [(0, False), (f_row - 17, True), (f_table + 52, False)])
# Manchester's vector slides out of the rack at its row and lands on the tile
pr, pm = slabs[MAN]
out = Vector((RX, RY - 0.45, PZ + zrow))
K.key(pr, "location", [(0, out), (f_table - 4, out), (f_table + 30, Vector((X(MAN), 0.0, ZS)))])
K.key(pr, "scale", [(0, (0.001,) * 3), (f_table - 6, (0.001,) * 3), (f_table + 6, (0.7,) * 3), (f_table + 30, (1.0,) * 3)])
K.glow_keys(pm, [(0, 0.0), (f_table - 6, 3.0)])
K.keyval(pm.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_table, 0.0), (f_table + 40, 1.0)])

# ---------------------------------------------------------------- b2: every token stands up its vector
f_vec, f_896, f_bat, f_man, f_learn = w("b2", "vector"), w("b2", "eight"), w("b2", "battery"), w("b2", "manchester"), w("b2", "learned")
for i in range(N):
    if i == MAN:
        continue
    pr, pm = slabs[i]
    d = int(abs(i - 92) * 0.5)
    K.key(pr, "scale", [(0, (0.001,) * 3), (f_vec - 6 + d, (0.001,) * 3), (f_vec + 12 + d, (1.0,) * 3)])
    K.glow_keys(pm, [(0, 0.0), (f_vec - 6 + d, 0.0), (f_vec + 10 + d, 2.2)])
    K.keyval(pm.node_tree.nodes["reveal"].outputs[0], [(0, 0.0 if str(i) in EMB else 1.0), (f_vec + d, 0.0 if str(i) in EMB else 1.0),
                                                       (f_896 + 20 + d, 1.0)])
for i, f_ in ((BATT, f_bat), (MAN, f_man)):
    pm = slabs[i][1]
    K.glow_keys(pm, [(f_ - 6, 2.2), (f_ + 6, 5.0), (f_ + 40, 5.0), (f_ + 60, 2.6)])
    K.glow_keys(faces[i], [(f_ - 6, 0.0 if i == BATT else 0.4), (f_ + 6, 1.6), (b["b3"]["f0"] + 20, 0.6)])

# ---------------------------------------------------------------- b3: squash to three dimensions, the meaning map
f_why, f_squash, f_see = w("b3", "why"), w("b3", "squash"), w("b3", "see")
base = K.empty("map", tuple(MAPC))
K.rbox("map_floor", (2.6, 2.4, 0.03), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(0, 0.2, -1.0), parent=base)
grid = K.cells_mat("map_grid", [0.4] * (26 * 24), 26, 24, K.SKY, vmax=1.0, strength=0.0)
K.plane("map_gridplane", 2.5, 2.3, grid, loc=(0, 0.2, -0.983), rot=(-math.pi / 2, 0, 0), parent=base)
for k, (a, c) in enumerate((((-1.25, -0.95), (1.25, -0.95)), ((-1.25, 1.35), (1.25, 1.35)))):
    pass
posts = []
for sx in (-1, 1):
    for sy in (-0.95, 1.35):
        posts.append(K.cyl(f"map_post{sx}{sy}", 0.008, 2.0, K.M("alu"), loc=(sx * 1.25, sy, 0.0), verts=16, parent=base))
K.glow_keys(grid, [(0, 0.0), (f_why, 0.0), (f_why + 30, 0.8)])
mapparts = [base]
dots = {}
for wd in PCA["words"]:
    m_ = K.light_mat(f"pt_{wd['word']}_m", GROUPC[wd["group"]], 0.0)
    sph = K.empty(f"pt_{wd['word']}", tuple(mp(wd["xyz"])))
    core = K.cyl(f"pt_{wd['word']}_c", 0.022, 0.044, m_, loc=(0, 0, -0.022), verts=24, parent=sph)
    import bpy  # noqa: E402
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.026, location=tuple(mp(wd["xyz"])), segments=24, ring_count=12)
    so = bpy.context.active_object
    so.name = f"pt_{wd['word']}_s"
    so.data.materials.append(m_)
    for p in so.data.polygons:
        p.use_smooth = True
    core.hide_render = True
    dots[wd["word"]] = (so, m_, wd)
    k = PCA["words"].index(wd)
    K.glow_keys(m_, [(0, 0.0), (f_squash + 10 + k, 0.0), (f_squash + 22 + k, 1.5)])
    so.scale = (0.001,) * 3
    K.key(so, "scale", [(0, (0.001,) * 3), (f_squash + 10 + k, (0.001,) * 3), (f_squash + 22 + k, (1.0,) * 3)])
# the question's slabs shrink to points and fly to their own places on the map
PROMPT = {q["i"]: q["xyz"] for q in PCA["prompt"]}
for i in range(80, 95):
    pr, pm = slabs[i]
    d = (i - 80) * 2
    p0 = Vector((X(i), 0.0, ZS))
    p1 = mp(PROMPT[i])
    K.key(pr, "location", [(f_squash - 2 + d, p0), (f_squash + 26 + d, p1)])
    K.key(pr, "scale", [(f_squash - 2 + d, (1.0,) * 3), (f_squash + 26 + d, (0.12,) * 3)])
    K.glow_keys(pm, [(f_squash + 24 + d, 4.0)])
for i in list(range(0, 80)) + list(range(95, N)):
    pr, pm = slabs[i]
    K.key(pr, "scale", [(f_squash - 2, (1.0,) * 3), (f_squash + 12, (0.001,) * 3)])

# b4 + b5: the camera tours the clusters; the neighbour fans
f_bike, f_city, f_days = w("b4", "bike"), w("b4", "cities"), w("b4", "days")
f_nbat, f_nman = w("b5", "battery"), w("b5", "manchester")
fans = {}
for key, word, f0, f1 in (("battery", "battery", f_nbat - 20, f_nman - 30), ("Manchester", "Manchester", f_nman - 20, b["b5"]["f1"] + 20)):
    c = mp(next(x["xyz"] for x in PCA["words"] if x["word"] == word))
    items = NB[key]["neighbours"][:6]
    for k, it in enumerate(items):
        ang = math.radians(-60 + k * 30)
        dist = 0.18 + 0.75 * (1 - it["cos"])
        pos = c + Vector((math.cos(ang) * dist * 0.9, -0.25, math.sin(ang) * dist * 0.6 + 0.12))
        m_ = K.light_mat(f"nb_{key}_{k}_m", K.SKY if key == "battery" else K.K_COL, 0.0)
        import bpy  # noqa: E402,F811
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=tuple(pos), segments=20, ring_count=10)
        so = bpy.context.active_object
        so.name = f"nb_{key}_{k}"
        so.data.materials.append(m_)
        K.empty(f"nb_{key}_{k}_pin", tuple(pos))
        tm = K.light_mat(f"nbl_{key}_{k}_m", K.SKY if key == "battery" else K.K_COL, 0.0)
        ln = K.beam(f"nbl_{key}_{k}", c, pos, r=0.0025 + 0.004 * it["cos"], mat=tm)
        fk = f0 + 10 + k * 5
        K.show(so, [(0, False), (fk, True), (f1 + 30, False)])
        K.show(ln, [(0, False), (fk, True), (f1 + 30, False)])
        K.key(ln, "scale", [(0, (1, 1, 0.001)), (fk, (1, 1, 0.001)), (fk + 12, (1, 1, 1.0))])
        K.glow_keys(m_, [(0, 1.8)])
        K.glow_keys(tm, [(0, 0.6 + 4.0 * it["cos"])])
    K.empty(f"pt_{key}_pin", tuple(c))

# b6: back to the row: every tile carries its column again; faint threads between the columns
f_row6, f_talk = w("b6", "row"), w("b6", "talk")
for i in range(N):
    pr, pm = slabs[i]
    home = Vector((X(i), 0.0, ZS if str(i) in EMB else ZT + 0.09))
    if 80 <= i <= 94:
        p1 = mp(PROMPT[i])
        K.key(pr, "location", [(f_row6 - 31, p1), (f_row6 - 30, home)])
        K.key(pr, "scale", [(f_row6 - 31, (0.12,) * 3), (f_row6 - 30, (0.001,) * 3), (f_row6 - 4 + (i - 80), (1.0,) * 3)])
        K.glow_keys(pm, [(f_row6 - 30, 2.2)])
    else:
        K.key(pr, "scale", [(f_row6 - 20, (0.001,) * 3), (f_row6 + int(abs(i - 99) * 0.4), (1.0,) * 3)])
for k, (a, c_) in enumerate(((99, 92), (99, 86), (92, 86), (93, 92), (87, 86))):
    tm = K.light_mat(f"thr{k}_m", K.SKY, 0.0)
    pa = Vector((X(a), 0.0, ZS + SH / 2 + 0.02))
    pc = Vector((X(c_), 0.0, ZS + SH / 2 + 0.02))
    th = K.arc(f"thr{k}", pa, pc, lift=0.25, r=0.003, mat=tm)
    K.grow(th, [(0, 0.0), (f_talk - 6 + k * 4, 0.0), (f_talk + 20 + k * 4, 1.0)])
    K.glow_keys(tm, [(0, 0.0), (f_talk - 6, 0.0), (f_talk + 10, 2.0)])
    K.show(th, [(0, False), (f_talk - 8, True)])

# ---------------------------------------------------------------- cameras
c1 = K.Cam(sc, "c_tile", lens=40, fstop=2.8).cut(0)
c1.keys([(0, (X(MAN) + 0.55, -1.25, 0.6), (X(MAN), 0.0, 0.22)),
         (f_row - 20, (X(MAN) + 1.3, -2.1, 1.0), (X(MAN) + 0.15, 0.7, 0.95)),
         (b["b1"]["f1"] + 10, (X(MAN) + 1.7, -2.6, 1.3), (X(MAN) + 0.2, 0.9, 1.25))])
c2 = K.Cam(sc, "c_cols", lens=38, fstop=3.0).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (X(MAN) + 1.0, -1.5, 0.8), (X(90), 0.0, 0.38)),
         (f_bat - 16, (X(BATT) + 0.7, -1.2, 0.66), (X(BATT), 0.0, 0.4)),
         (f_man - 16, (X(BATT) + 0.9, -1.25, 0.66), (X(BATT) + 0.3, 0.0, 0.4)),
         (f_man + 6, (X(MAN) + 0.65, -1.15, 0.64), (X(MAN), 0.0, 0.42)),
         (b["b2"]["f1"] + 12, (X(MAN) + 0.5, -1.0, 0.6), (X(MAN), 0.0, 0.42))])
c3 = K.Cam(sc, "c_fly", lens=30, fstop=4.5).cut(b["b3"]["f0"] - 8)
c3.keys([(b["b3"]["f0"] - 8, (-0.4, -3.6, 1.6), (0.0, 0.3, 0.7)), (b["b3"]["f1"] + 12, (0.9, -3.4, 1.65), (MAPC.x - 0.2, MAPC.y, MAPC.z - 0.1))])
bike = mp((0.04, -0.12, 0.01)); city = mp((0.145, 0.105, -0.06)); days = mp((-0.072, 0.15, 0.17))
c4 = K.Cam(sc, "c_groups", lens=40, fstop=3.2).cut(b["b4"]["f0"] - 8)
c4.keys([(b["b4"]["f0"] - 8, (bike.x + 0.5, bike.y - 2.2, bike.z + 0.2), (bike.x, bike.y, bike.z)),
         (f_city - 6, (city.x + 0.2, city.y - 2.2, city.z + 0.4), (city.x, city.y, city.z)),
         (f_days - 6, (days.x + 0.2, days.y - 2.3, days.z + 0.3), (days.x, days.y, days.z)),
         (b["b4"]["f1"] + 12, (days.x + 0.1, days.y - 2.2, days.z + 0.25), (days.x, days.y, days.z))])
cb = mp(next(x["xyz"] for x in PCA["words"] if x["word"] == "battery"))
cm = mp(next(x["xyz"] for x in PCA["words"] if x["word"] == "Manchester"))
c5 = K.Cam(sc, "c_nbat", lens=45, fstop=3.2).cut(b["b5"]["f0"] - 8)
c5.keys([(b["b5"]["f0"] - 8, (cb.x + 0.35, cb.y - 2.4, cb.z + 0.4), (cb.x + 0.25, cb.y - 0.2, cb.z + 0.12)),
         (f_nman - 26, (cb.x + 0.3, cb.y - 2.2, cb.z + 0.35), (cb.x + 0.25, cb.y - 0.2, cb.z + 0.12))])
c6 = K.Cam(sc, "c_nman", lens=45, fstop=3.2).cut(f_nman - 24)
c6.keys([(f_nman - 24, (cm.x + 0.35, cm.y - 2.4, cm.z + 0.4), (cm.x + 0.25, cm.y - 0.2, cm.z + 0.12)),
         (b["b5"]["f1"] + 12, (cm.x + 0.3, cm.y - 2.2, cm.z + 0.35), (cm.x + 0.25, cm.y - 0.2, cm.z + 0.12))])
c7 = K.Cam(sc, "c_end", lens=32, fstop=4.0).cut(b["b6"]["f0"] - 8)
c7.keys([(b["b6"]["f0"] - 8, (1.2, -2.3, 1.15), (-2.6, 0.0, 0.4)), (END, (1.6, -3.0, 1.45), (-1.6, 0.3, 0.55))])

pins = [f"tok{i}_front" for i in range(N)] + [f"vec{i}_top" for i in range(N)] + ["rack_pin_row", "rack_pin_top", "pt_battery_pin", "pt_Manchester_pin"]
pins += [f"pt_{wd['word']}" for wd in PCA["words"]] + [f"nb_{k}_{j}_pin" for k in ("battery", "Manchester") for j in range(6)]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
