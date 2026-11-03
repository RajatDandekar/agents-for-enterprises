"""Film 2 of Lecture 3, "How the LLM Wiki works": the real Northbridge wiki (ledgerline/wiki_v4), built, queried,
filed back into, updated and linted. Builds wiki.blend.

The archive (the same three glass cases as film 1, each stack as tall as its real token count) under padlocks: raw
sources are never edited. The model machine reads them in parts; pages come out onto a round dais: 683 glass page
tablets in 16 clusters (one per page type, the top edge in the type's colour), in the order log.md first names them,
then their 4,021 real links as arcs. At the hub: index.md, AGENTS.md (the schema) and log.md (one cell per ingest).
The Brightcell page lifts out (its real lead, infobox, sections, links and references in 2D, beside a real Wikipedia
article). Emma's question: index.md lights, the three pages the navigator really opened light, and threads run from
them back to the case holding each of their sources. The answer is filed back as a new page linked to the pages it
used; a patch note arrives and lights the 4 pages it updated and adds the 3 it created; lint sweeps the dais and an
ember flag rises over each of the 380 pages it reported.

Numbers: data/l3_data.json (make_data.py). Timing: timeline/wiki.json.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402
import props_l3 as Q  # noqa: E402

FILM = "wiki"
B = K.Beats(FILM)
DATA = K.load("films/build/data/l3_data.json")
D = DATA["wiki"]
RG = DATA["rag"]
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11
lit = K.glow_keys

sc = K.reset(B.frames)
K.studio(sc, focus=(0.6, 0.6, 0.4), key_power=3200, span=4.5)
for i, x in enumerate((2.2, 4.4)):
    K.soft_light(f"keyR{i}", (x, -6.0, 7.5), (x, 0.8, 0.3), 1700, 12.0, (1.0, 0.97, 0.93))
    K.soft_light(f"rimR{i}", (x, 8.0, 3.2), (x, 0.8, 0.3), 1100, 14.0, (0.7, 0.82, 1.0))
K.plinth("bench", -4.7, -1.55, y=0.0, depth=1.3, height=PZ)

# ------------------------------------------------------------------------------------------------ the archive (locked)
cls = RG["audit"]["by_class"]
STACKS = [("unstructured", "paper", -4.25), ("structured", "ledger", -3.73), ("semi-structured", "card", -3.21)]
CASE_X = {}
locks = []
for k, (c, kind, x) in enumerate(STACKS):
    hgt = cls[c]["tokens_o200k"] / 3.5e6
    v = Q.vitrine(f"vit_{k}", (x, 0.12, PZ), h=max(0.12, hgt + 0.06))
    Q.sheet_stack(f"stk_{k}", (x, 0.12, PZ + 0.05), hgt, kind=kind, seed=k + 3)
    lk = P.padlock(f"lock{k}", (x, -0.12, PZ), s=0.55)
    CASE_X[c] = (x, hgt, v)
    locks.append((lk, v))
f_raw = w("b2", "raw")
f_never = w("b2", "never")
for c, (x, hgt, v) in CASE_X.items():
    lit(v["led"], [(0, 0.4), (f_raw - 4, 0.4), (f_raw + 6, 3.0), (f_never + 40, 0.8)])
for k, (lk, v) in enumerate(locks):
    K.key(lk, "location", [(0, Vector((STACKS[k][2], -0.12, PZ + 0.25))), (f_never - 8 + 4 * k, Vector((STACKS[k][2], -0.12, PZ + 0.25))),
                           (f_never + 8 + 4 * k, Vector((STACKS[k][2], -0.12, PZ)))])
    K.show(lk, [(0, False), (f_never - 8 + 4 * k, True)])

# ------------------------------------------------------------------------------------------------ the model
MX = -2.3
MA = P.machine("model", (MX, 0.1, PZ + 0.04), w=0.9, d=0.55, h=0.72)
K.rbox("riser", (1.0, 0.66, 0.04), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(MX, 0.1, PZ + 0.02))
K.glow_keys(MA["led"], [(0, 0.3)])
K.glow_keys(MA["tower"]["idle"], [(0, 0.4)])
K.key(MA["inner"].data, "energy", [(0, 6.0)])


def think(f0, f1, peak=2.4):
    K.glow_keys(MA["led"], [(f0 - 6, 0.3), (f0, peak), (f1, peak), (f1 + 10, 0.3)])
    K.glow_keys(MA["tower"]["idle"], [(f0 - 8, 0.4), (f0, 2.6), (f1, 2.6), (f1 + 12, 0.4)])


# ------------------------------------------------------------------------------------------------ the dais and the hub
C = Vector((2.0, 1.35, 0.0))
Q.dais("dais", C, r=3.5, h=0.06)
Z0 = 0.06
pos = {s: [C.x + p["pos"][0], C.y + p["pos"][1], p["pos"][2]] for s, p in D["pages"].items()}
types = {s: p["type"] for s, p in D["pages"].items()}

f_wiki2 = w("b2", "wiki")
f_schema = w("b2", "schema")
idx = Q.tablet("idx", (C.x, C.y, Z0), rot=0.0, scale=2.4, color=K.SKY, lines=12)
lit(idx["edge_m"], [(0, 0.3), (f_wiki2 - 4, 0.3), (f_wiki2 + 8, 3.0), (blk["b3"]["f0"], 1.2)])
sch = Q.tablet("schema", (C.x - 0.36, C.y + 0.02, Z0), rot=0.0, scale=1.9, color=K.lin("#e0a63a"), lines=10)
lit(sch["edge_m"], [(0, 0.3), (f_schema - 4, 0.3), (f_schema + 8, 4.0), (blk["b3"]["f0"] + 20, 1.2)])
lit(sch["core_m"], [(0, 0.0), (f_schema - 4, 0.0), (f_schema + 8, 0.6), (blk["b3"]["f0"] + 20, 0.0)])
# log.md: one cell per ingest line (693), filled during the ingest
n_ing = D["ingests"]
logp, log_m = K.vector_plate("logmd", [1.0] * n_ing + [0.0] * (21 * 33 - n_ing), 21, 33, K.SKY, (C.x + 0.36, C.y + 0.02, Z0 + 0.17),
                             cell=0.0085, vmax=1.0, glow=0.0, reveal=0.0)
K.rbox("logmd_foot", (0.22, 0.05, 0.012), bevel=0.003, seg=2, mat=K.M("alu"), loc=(C.x + 0.36, C.y + 0.02, Z0 + 0.006))

# ------------------------------------------------------------------------------------------------ the pages
HERO = {"sup-brightcell-energy", "pol-sup-003", "sop-pur-006", "sop-pur-001", "pol-pur-001"} | set(D["update"]["updated"])
order = [s for s in D["order"] if s not in HERO]
NB = 24
f_writes = w("b3", "writes")
f_683 = w("b3", "six")
batches = [order[i::NB] for i in range(NB)]
batches = [order[len(order) * k // NB: len(order) * (k + 1) // NB] for k in range(NB)]
tops_all = []
for k, bs in enumerate(batches):
    ob = Q.tablets(f"pg{k}", bs, pos, Z0, Q.tablet_mat())
    tp, tm = Q.tablet_tops(f"pgt{k}", bs, pos, types, Z0, 0.0)
    f0 = int(f_writes + (f_683 - f_writes) * k / NB)
    for o in (ob, tp):
        K.show(o, [(0, False), (f0, True)])
    lit(tm, [(0, 0.0), (f0, 0.0), (f0 + 2, 5.0), (f0 + 20, 1.1)])
    tops_all.append((tm, f0))
hero = {}
for s in sorted(HERO):
    x, y, rot = pos[s]
    t = Q.tablet(f"h_{s}", (x, y, Z0), rot=rot, scale=1.0, color=K.lin(Q.TYPE_HEX[types[s]]), lines=7)
    f0 = int(f_writes + (f_683 - f_writes) * (D["order"].index(s) / len(D["order"])))
    K.show(t["root"], [(0, False), (f0, True)])
    lit(t["edge_m"], [(0, 0.0), (f0, 0.0), (f0 + 2, 5.0), (f0 + 20, 1.1)])
    hero[s] = t
# parts flow into the model (from the three cases), facts flow out to the dais
f_reads = w("b3", "reads")
rnd = random.Random(11)
for k in range(28):
    c = ["unstructured", "structured", "semi-structured"][k % 3]
    x, hgt, v = CASE_X[c]
    cp, cm = P.capsule(f"part{k}", (x, 0.12, PZ + 0.1), size=(0.08, 0.04, 0.03))
    f0 = f_reads + k * 9
    K.show(cp, [(0, False), (f0, True), (f0 + 30, False)])
    P.travel(cp, [Vector((x, 0.12, PZ + 0.1 + hgt + 0.1)), Vector(((x + MX) / 2, 0.0, PZ + 0.9)), Vector((MX - 0.5, 0.1, PZ + 0.15))], f0, f0 + 28)
    s = order[min(len(order) - 1, k * len(order) // 28)]
    fp, fm, _ = P.result_slab(f"fact{k}", (MX + 0.5, 0.1, PZ + 0.15), size=(0.06, 0.04, 0.012))
    g0 = f0 + 26
    K.show(fp, [(0, False), (g0, True), (g0 + 32, False)])
    tgt = Vector((pos[s][0], pos[s][1], Z0 + 0.12))
    P.travel(fp, [Vector((MX + 0.5, 0.1, PZ + 0.15)), (Vector((MX + 0.5, 0.1, PZ + 0.15)) + tgt) / 2 + Vector((0, 0, 0.7)), tgt], g0, g0 + 30)
think(f_reads, f_683 + 20)
# log.md fills; the links grow
K.keyval(log_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_writes, 0.0), (f_683, n_ing / (21 * 33))])
lit(log_m, [(0, 0.0), (f_writes - 4, 0.0), (f_writes + 4, 1.6), (w("b3", "line") - 6, 1.6), (w("b3", "line") + 4, 4.0), (blk["b4"]["f0"], 1.6)])
f_links = w("b3", "four")
link_m = K.light_mat("links_m", K.lin("#7fb2ff"), 0.0)
segs = []
for a, b in D["links"]:
    pa, pb = pos[a], pos[b]
    segs.append(((pa[0], pa[1], Z0 + Q.TH + 0.004), (pb[0], pb[1], Z0 + Q.TH + 0.004)))
links = Q.links_curve("links", segs, link_m, r=0.0011, lift=0.05, per=0.12)
K.grow(links, [(0, 0.0), (f_links - 8, 0.0), (f_links + 40, 1.0)])
lit(link_m, [(0, 0.0), (f_links - 8, 0.0), (f_links, 2.2), (f_links + 60, 1.0), (blk["b4"]["f0"] - 10, 1.0), (blk["b4"]["f0"] + 20, 0.06),
             (w("b10", "linked") - 6, 0.06), (w("b10", "linked") + 8, 1.2)])

# ------------------------------------------------------------------------------------------------ the Brightcell page lifts out
BC = "sup-brightcell-energy"
bct = hero[BC]
bx, by, brot = pos[BC]
f_page = blk["b4"]["f0"]
f_bc = w("b4", "brightcell")
LIFT = Vector((bx - 0.05, by - 0.6, Z0 + 0.12))
K.key(bct["root"], "location", [(0, Vector((bx, by, Z0))), (f_page - 6, Vector((bx, by, Z0))), (f_page + 40, LIFT)])
K.key(bct["root"], "scale", [(0, (1, 1, 1)), (f_page - 6, (1, 1, 1)), (f_page + 40, (2.4, 2.4, 2.4)), (blk["b5"]["f0"] - 10, (2.4, 2.4, 2.4)),
                             (blk["b5"]["f0"] + 20, (1, 1, 1))])
K.key(bct["root"], "rotation_euler", [(0, (0, 0, brot)), (f_page - 6, (0, 0, brot)), (f_page + 40, (0, 0, 0.0)), (blk["b5"]["f0"] - 10, (0, 0, 0.0)),
                                      (blk["b5"]["f0"] + 20, (0, 0, brot))])
K.key(bct["root"], "location", [(blk["b5"]["f0"] - 10, LIFT), (blk["b5"]["f0"] + 20, Vector((bx, by, Z0)))])
lit(bct["core_m"], [(0, 0.0), (f_page, 0.0), (f_page + 30, 0.9), (blk["b5"]["f0"], 0.2)])

# ------------------------------------------------------------------------------------------------ the query
f_ask = w("b5", "emma")
f_idx5 = w("b5", "index")
f_opens = w("b5", "opens")
OPEN = [("sup-brightcell-energy", w("b5", "brightcell", 1)), ("pol-sup-003", w("b5", "supplier")), ("sop-pur-006", w("b5", "procedure"))]
lit(idx["edge_m"], [(f_idx5 - 4, 1.2), (f_idx5 + 4, 6.0), (blk["b7"]["f0"], 1.2)])
lit(idx["core_m"], [(0, 0.0), (f_idx5 - 4, 0.0), (f_idx5 + 4, 1.4), (blk["b6"]["f0"] + 30, 0.0)])
qa_m = K.light_mat("qbeam_m", K.SKY, 0.0)
top_idx = Vector((C.x, C.y, Z0 + Q.TH * 2.4))
for k, (s, f0) in enumerate(OPEN):
    x, y, _ = pos[s]
    a = K.arc(f"qarc{k}", top_idx, (x, y, Z0 + Q.TH + 0.01), lift=0.35, r=0.0035, mat=qa_m)
    K.grow(a, [(0, 0.0), (f0 - 10, 0.0), (f0 + 6, 1.0)])
    t = hero[s]
    lit(t["edge_m"], [(f0 - 2, 1.1), (f0 + 6, 6.0), (blk["b7"]["f0"], 1.1)])
    lit(t["core_m"], [(0, 0.0), (f0 - 2, 0.0), (f0 + 6, 1.5), (blk["b7"]["f0"], 0.0)])
    if s != BC:
        K.key(t["root"], "location", [(0, Vector((x, y, Z0))), (f0, Vector((x, y, Z0))), (f0 + 14, Vector((x, y, Z0 + 0.05)))])
lit(qa_m, [(0, 0.0), (OPEN[0][1] - 10, 0.0), (OPEN[0][1], 4.0), (blk["b7"]["f0"], 2.0), (blk["b7"]["f0"] + 30, 0.0)])
cq, cqm = P.capsule("qcap", (C.x, C.y, 1.2))
K.show(cq, [(0, False), (f_ask - 6, True), (f_idx5 + 6, False)])
P.travel(cq, [Vector((MX + 0.6, 0.1, PZ + 0.5)), Vector((C.x - 0.6, C.y - 0.6, 0.9)), top_idx + Vector((0, 0, 0.04))], f_ask, f_idx5 + 2)
think(f_ask, f_opens + 20)

# ------------------------------------------------------------------------------------------------ the answer: threads to the sources
f_ans = w("b6", "answer")
f_cite = w("b6", "cite")
res, res_m, _ = P.result_slab("res", (MX + 0.6, 0.1, PZ + 0.145))
K.show(res, [(0, False), (f_ans - 6, True)])
P.travel(res, [Vector((MX + 0.38, 0.1, PZ + 0.145)), Vector((MX + 0.75, -0.12, PZ + 0.145))], f_ans - 4, f_ans + 24)
think(f_ans - 20, f_ans + 10)
thr_m = K.light_mat("thread_m", K.GREEN, 0.0)
k = 0
for it in D["chain"]["items"]:
    s = it["id"].split(":", 1)[1]
    x, y, _ = pos[s]
    for j, src in enumerate(it["sources"]):
        cx, hgt, v = CASE_X[src["class"]]
        a = K.arc(f"thr{k}", (x, y, Z0 + Q.TH + 0.05), (cx + 0.03 * ((j % 5) - 2), 0.12, PZ + 0.05 + hgt + 0.06), lift=0.5 + 0.02 * (j % 7),
                  r=0.0016, mat=thr_m)
        K.grow(a, [(0, 0.0), (f_cite - 6 + k, 0.0), (f_cite + 22 + k, 1.0)])
        k += 1
lit(thr_m, [(0, 0.0), (f_cite - 6, 0.0), (f_cite, 3.0), (blk["b7"]["f0"] + 20, 1.6), (blk["b7"]["f0"] + 60, 0.0)])

# ------------------------------------------------------------------------------------------------ file-back
f_filed = w("b7", "filed")
f_new = w("b7", "new")
f_one = w("b7", "one")
sx, sy, srot = pos[BC]
QX, QY = sx + 0.03, sy - 0.24
qa = Q.tablet("qa", (QX, QY, Z0), rot=srot, scale=1.25, color=K.GREEN, lines=8)
K.show(qa["root"], [(0, False), (f_filed - 2, True)])
K.key(qa["root"], "location", [(0, Vector((QX, QY, Z0 + 0.6))), (f_filed - 2, Vector((QX, QY, Z0 + 0.6))), (f_filed + 22, Vector((QX, QY, Z0)))])
lit(qa["edge_m"], [(0, 0.0), (f_filed, 0.0), (f_filed + 10, 6.0), (f_one + 40, 1.6)])
fb_m = K.light_mat("fb_m", K.GREEN, 0.0)
for k, s in enumerate(D["fileback"]["pages_used"]):
    x, y, _ = pos[s]
    a = K.arc(f"fb{k}", (QX, QY, Z0 + Q.TH * 1.25 + 0.005), (x, y, Z0 + Q.TH + 0.005), lift=0.12, r=0.0022, mat=fb_m)
    K.grow(a, [(0, 0.0), (f_new + k * 5, 0.0), (f_new + 16 + k * 5, 1.0)])
lit(fb_m, [(0, 0.0), (f_new, 0.0), (f_new + 6, 3.0), (blk["b8"]["f0"] + 20, 1.0)])
one = K.arc("onestep", top_idx, (QX, QY, Z0 + Q.TH * 1.25 + 0.005), lift=0.3, r=0.003, mat=qa_m)
K.grow(one, [(0, 0.0), (f_one - 14, 0.0), (f_one + 6, 1.0)])
lit(qa_m, [(f_one - 16, 0.0), (f_one - 6, 4.0), (blk["b8"]["f0"] + 10, 1.0), (blk["b8"]["f0"] + 40, 0.0)])

# ------------------------------------------------------------------------------------------------ an update arrives
f_doc = w("b8", "document")
f_upd = w("b8", "updated")
f_cre = w("b8", "created")
doc, doc_m = P.capsule("newdoc", (-4.25, 0.12, 1.0), color=K.lin("#7f8cff"))
K.show(doc, [(0, False), (f_doc - 10, True), (f_doc + 50, False)])
P.travel(doc, [Vector((-4.6, -0.6, 1.0)), Vector((-3.3, -0.3, 0.8)), Vector((MX - 0.5, 0.1, PZ + 0.15))], f_doc - 10, f_doc + 40)
think(f_doc + 30, f_upd)
for s in D["update"]["updated"]:
    t = hero[s]
    lit(t["edge_m"], [(f_upd - 2, 1.1), (f_upd + 6, 6.0), (blk["b9"]["f0"], 1.1)])
    lit(t["core_m"], [(0, 0.0), (f_upd - 2, 0.0), (f_upd + 6, 1.6), (blk["b9"]["f0"], 0.0)])
new_t = {}
for k, s in enumerate(D["update"]["created"]):
    ty = {"rn-": "release", "err": "error", "top": "topic"}[s[:3]]
    cc = D["clusters"][ty]
    ang = cc["angle"]
    # just outside its type's cluster, toward the hub (a new page joins its own kind)
    x = C.x + cc["center"][0] - 0.42 * math.cos(ang)
    y = C.y + cc["center"][1] - 0.42 * math.sin(ang)
    t = Q.tablet(f"new_{s}", (x, y, Z0), rot=ang + math.pi / 2, scale=1.2, color=K.lin(Q.TYPE_HEX[ty]), lines=7)
    f0 = f_cre + 6 * k
    K.show(t["root"], [(0, False), (f0, True)])
    K.key(t["root"], "location", [(0, Vector((x, y, Z0 + 0.5))), (f0, Vector((x, y, Z0 + 0.5))), (f0 + 18, Vector((x, y, Z0)))])
    lit(t["edge_m"], [(0, 0.0), (f0, 0.0), (f0 + 8, 6.0), (blk["b9"]["f0"] + 20, 1.6)])
    new_t[s] = (t, x, y)

# ------------------------------------------------------------------------------------------------ lint
f_lint = w("b9", "lint")
f_found = w("b9", "found")
ring_m = K.light_mat("lintring_m", K.EMBER, 0.0)
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.006, major_segments=180, minor_segments=8, location=(C.x, C.y, Z0 + 0.05))
lr = bpy.context.active_object
lr.name = "lintring"
lr.data.materials.append(ring_m)
lr.visible_shadow = False
SW0, SW1 = f_lint + 4, f_found - 6
K.key(lr, "scale", [(0, (0.02, 0.02, 1)), (SW0, (0.02, 0.02, 1)), (SW1, (3.1, 3.1, 1))])
lit(ring_m, [(0, 0.0), (SW0 - 2, 0.0), (SW0 + 4, 5.0), (SW1, 5.0), (SW1 + 10, 0.0)])
flag_m = K.light_mat("flag_m", K.EMBER, 0.0)
# one flag object per radial band, so each lights as the ring passes it
bands = [[] for _ in range(8)]
for s in D["lint_pages"]:
    if s not in pos:
        continue
    x, y, _ = pos[s]
    r = math.hypot(x - C.x, y - C.y)
    bands[min(7, int(r / 3.1 * 8))].append((x, y, Z0 + Q.TH + 0.018))
for k, pts in enumerate(bands):
    if not pts:
        continue
    m = K.light_mat(f"flag{k}_m", K.EMBER, 0.0)
    Q.beads(f"flags{k}", pts, 0.02, m, z=0.025)
    fk = int(SW0 + (SW1 - SW0) * (k + 0.5) / 8)
    lit(m, [(0, 0.0), (fk - 2, 0.0), (fk + 4, 12.0), (fk + 20, 7.0), (blk["b10"]["f0"] + 30, 7.0), (blk["b10"]["f0"] + 60, 1.5)])

# ------------------------------------------------------------------------------------------------ cameras
b = blk
c1 = K.Cam(sc, "c_idea", lens=30, fstop=6.0).cut(0)
c1.keys([(0, (-4.6, -3.6, 1.6), (-2.6, 0.4, 0.4)),
         (w("b1", "andrej"), (-3.6, -3.9, 2.1), (-0.6, 0.8, 0.3)),
         (b["b1"]["f1"] + 18, (-1.4, -4.6, 2.9), (1.4, 1.0, 0.1))])
c2 = K.Cam(sc, "c_layers", lens=34, fstop=4.5).cut(b["b2"]["f0"] - 12)
c2.keys([(b["b2"]["f0"] - 12, (-4.7, -2.2, 1.15), (-3.7, 0.15, 0.45)),
         (f_wiki2 - 20, (-3.9, -2.2, 1.1), (-3.5, 0.15, 0.4))])
c2b = K.Cam(sc, "c_hub", lens=40, fstop=3.2).cut(f_wiki2 - 8)
c2b.keys([(f_wiki2 - 8, (C.x - 0.6, C.y - 1.35, 0.75), (C.x, C.y, 0.2)),
          (b["b2"]["f1"] + 18, (C.x - 0.35, C.y - 1.15, 0.6), (C.x - 0.1, C.y, 0.2))])
c3 = K.Cam(sc, "c_ingest", lens=30, fstop=5.6).cut(b["b3"]["f0"] - 12)
c3.keys([(b["b3"]["f0"] - 12, (-4.0, -2.5, 1.5), (-2.6, 0.2, 0.45)),
         (f_writes - 30, (-3.2, -3.0, 2.0), (-0.5, 0.6, 0.3)),
         (f_683, (-0.6, -3.9, 3.1), (1.6, 1.0, 0.0)),
         (b["b3"]["f1"] + 18, (0.6, -3.3, 3.4), (1.75, 1.1, 0.0))])
c4 = K.Cam(sc, "c_page", lens=40, fstop=2.8).cut(b["b4"]["f0"] - 12)
c4.keys([(b["b4"]["f0"] - 12, (LIFT.x - 0.1, LIFT.y - 1.6, 0.75), (LIFT.x, LIFT.y, 0.25)),
         (b["b4"]["f1"] + 18, (LIFT.x + 0.05, LIFT.y - 1.35, 0.6), (LIFT.x, LIFT.y, 0.27))])
c5 = K.Cam(sc, "c_query", lens=32, fstop=5.0).cut(b["b5"]["f0"] - 12)
c5.keys([(b["b5"]["f0"] - 12, (-1.2, -2.6, 1.8), (0.2, 0.6, 0.3)),
         (f_idx5, (C.x - 0.6, C.y - 4.3, 3.4), (C.x + 0.3, C.y - 0.1, 0.05)),
         (b["b5"]["f1"] + 18, (C.x + 0.2, C.y - 4.2, 3.5), (C.x + 0.5, C.y, 0.05))])
c6 = K.Cam(sc, "c_answer", lens=30, fstop=6.0).cut(b["b6"]["f0"] - 12)
c6.keys([(b["b6"]["f0"] - 12, (MX - 0.2, -1.5, 0.75), (MX + 0.5, 0.0, 0.3)),
         (f_cite - 40, (MX + 0.1, -1.6, 0.85), (MX + 0.6, 0.0, 0.3))])
c6b = K.Cam(sc, "c_threads", lens=26, fstop=8.0).cut(f_cite - 24)
c6b.keys([(f_cite - 24, (-2.0, -4.6, 2.6), (-0.4, 0.3, 0.35)),
          (b["b6"]["f1"] + 18, (-1.4, -4.7, 2.5), (-0.4, 0.3, 0.35))])
c7 = K.Cam(sc, "c_fileback", lens=34, fstop=4.0).cut(b["b7"]["f0"] - 12)
c7.keys([(b["b7"]["f0"] - 12, (QX - 0.55, QY - 1.25, 1.35), (QX, QY + 0.15, 0.1)),
         (f_one - 20, (QX - 0.5, QY - 1.45, 1.55), (QX - 0.1, QY + 0.45, 0.1)),
         (b["b7"]["f1"] + 18, (QX - 1.2, QY - 1.9, 1.7), (QX - 0.4, QY + 0.9, 0.1))])
c8 = K.Cam(sc, "c_update", lens=28, fstop=6.0).cut(b["b8"]["f0"] - 12)
c8.keys([(b["b8"]["f0"] - 12, (-4.2, -2.4, 1.3), (-3.0, 0.1, 0.5)),
         (f_doc + 40, (-1.2, -4.4, 3.4), (1.4, 1.0, 0.0)),
         (b["b8"]["f1"] + 18, (0.3, -4.0, 4.0), (1.75, 1.1, 0.0))])
c9 = K.Cam(sc, "c_lint", lens=26, fstop=8.0).cut(b["b9"]["f0"] - 12)
c9.keys([(b["b9"]["f0"] - 12, (C.x - 0.5, C.y - 5.0, 4.4), (C.x, C.y, 0.0)),
         (b["b9"]["f1"] + 18, (C.x + 0.6, C.y - 4.7, 4.6), (C.x, C.y + 0.1, 0.0))])
c10 = K.Cam(sc, "c_close", lens=26, fstop=8.0).cut(b["b10"]["f0"] - 12)
c10.keys([(b["b10"]["f0"] - 12, (2.6, -4.4, 2.0), (0.4, 0.6, 0.35)),
          (END, (-2.2, -5.4, 2.6), (-0.4, 0.6, 0.35))])

pins = ["vit_0_pin", "vit_1_mid", "vit_2_pin", "lock0_top", "lock1_top", "lock2_top", "model_pin_top", "model_pin_win",
        "idx_top", "schema_top", "logmd_top", "res_top", "qcap_top", "qa_top", "newdoc_top",
        f"h_{BC}_top", "h_pol-sup-003_top", "h_sop-pur-006_top", "h_sop-pur-001_top", "h_pol-pur-001_top"] + \
       [f"h_{s}_top" for s in D["update"]["updated"]] + [f"new_{s}_top" for s in D["update"]["created"]]
K.empty("dais_pin", (C.x + 2.2, C.y - 2.2, Z0 + 0.1))
pins.append("dais_pin")
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
