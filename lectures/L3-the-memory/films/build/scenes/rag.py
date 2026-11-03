"""Film 1 of Lecture 3, "How RAG works": Emma's ERR-PO-0412 question, followed through the whole pipeline. Builds rag.blend.

Emma's screen shows the error; the archive (three glass cases, each stack as tall as its real token count:
unstructured, structured, semi-structured); the quick-reference card QRC-03 slides through the reader (the parser) and
its text bars come up crisp, headings in sky; a ledger sheet follows with its header row lit; the card splits along
its structure into its three real chunks (bars = the real lines), each with a sky header; the first chunk's real
bge-small vector rises as a plate of 384 cells; the light table lights its 3,620 beads at their real PCA positions;
the card catalogue (BM25) opens a drawer. The question lands on the table as a star, its 10 real dense hits ringed;
the drawer's three QRC-03 cards rise in green. 20 candidates run through the reranker arch, 10 come out in the
reranker's real order (gold sources edged green) and slide into the model; a green answer slab comes out. The close:
the stations light in turn; then Q-EMMA's 11 gold sources rise in front of the archive, the 2 that were found in green.

Numbers: data/l3_data.json (make_data.py: logs + the live RAG Lab capture). Timing: timeline/rag.json.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_l4 as P  # noqa: E402
import props_l3 as Q  # noqa: E402

FILM = "rag"
B = K.Beats(FILM)
D = K.load("films/build/data/l3_data.json")["rag"]
w = B.w
blk = B.blocks
END = B.frames - 1
PZ = 0.11

sc = K.reset(B.frames)
K.studio(sc, focus=(0.0, 0.2, 0.4), key_power=3000, span=5.0)
for i, x in enumerate((2.6, 5.0)):
    K.soft_light(f"keyR{i}", (x, -6.0, 7.5), (x, 0.3, 0.3), 1700, 12.0, (1.0, 0.97, 0.93))
    K.soft_light(f"rimR{i}", (x, 7.0, 3.2), (x, 0.3, 0.3), 1100, 14.0, (0.7, 0.82, 1.0))
K.plinth("benchA", -6.1, -0.55, y=0.0, depth=1.3, height=PZ)
K.plinth("benchB", 2.25, 6.2, y=0.0, depth=1.3, height=PZ)


def lit(m, keys):
    K.glow_keys(m, keys)


# ------------------------------------------------------------------------------------------------ Emma's screen
SX = -5.45
scr = Q.screen("scr", (SX, 0.05, PZ))
lit(scr["status"], [(0, 0.0), (w("b1", "stops") - 4, 0.0), (w("b1", "stops") + 4, 5.0), (blk["b2"]["f0"] + 30, 3.0), (blk["b2"]["f0"] + 60, 0.4)])

# ------------------------------------------------------------------------------------------------ the archive
TOK_PER_M = 3.5e6
cls = D["audit"]["by_class"]
STACKS = [("unstructured", "paper", -4.62), ("structured", "ledger", -4.1), ("semi-structured", "card", -3.58)]
VZ = PZ
vit = {}
for k, (c, kind, x) in enumerate(STACKS):
    hgt = cls[c]["tokens_o200k"] / TOK_PER_M
    v = Q.vitrine(f"vit_{k}", (x, 0.12, VZ), h=max(0.12, hgt + 0.06))
    st = Q.sheet_stack(f"stk_{k}", (x, 0.12, VZ + 0.05), hgt, kind=kind, seed=k + 3)
    vit[c] = (v, st, x, hgt)
# the stacks rise as Daniel names them (they are the data: 1 m per 3.5 million tokens)
for c, word in (("unstructured", "pdfs"), ("structured", "spreadsheets"), ("semi-structured", "e-mails")):
    v, st, x, hgt = vit[c]
    f0 = w("b2", word) - 6
    K.key(st, "scale", [(0, (1, 1, 0.02)), (f0, (1, 1, 0.02)), (f0 + 26, (1, 1, 1.0))])
    lit(v["led"], [(0, 0.3), (f0, 0.3), (f0 + 10, 3.0), (f0 + 60, 0.8)])

# ------------------------------------------------------------------------------------------------ the reader (parser)
LANE_Y = -0.3
LZ = PZ + 0.035
P.rail("lane", -3.35, -0.62, LANE_Y, LZ)
RX = -2.62
rd = Q.reader("rd", (RX, LANE_Y, PZ), span=0.5, h=0.24, d=0.22)
rd["root"].rotation_euler = (0, 0, math.pi / 2)


def wrap(lines, cpl=64, keep_head=True):
    out = []
    for ln in lines:
        if ln["head"] and not keep_head:
            continue
        L = ln["len"]
        while L > 0:
            out.append({"len": min(cpl, L), "head": ln["head"]})
            L -= cpl
    return out


chunks = D["qrc03"]["chunks"]
groups = [wrap(c["lines"], keep_head=False) for c in chunks]
LH = 0.0068
PW = 0.34
PH = 0.044 + LH * sum(len(g) for g in groups) + LH * 0.6 * (len(groups) - 1) + 0.004
PAPER_Z = LZ + 0.006
pp = Q.paper("qrc", (-3.3, LANE_Y, PAPER_Z), groups, w=PW, h=PH, margin=0.022, lh=LH)
pp["root"].rotation_euler = (0, 0, math.pi / 2)    # its top edge faces -x (it travels top first, along +x)
f_rd = w("b3", "reader")
f_pdf = w("b3", "pdfs")
f_rows = w("b3", "rows")
f_all = w("b3", "all")
CHX = -1.45
K.show(pp["root"], [(0, False), (blk["b3"]["f0"] - 30, True)])
P.travel(pp["root"], [Vector((-3.6, LANE_Y, PAPER_Z)), Vector((RX - 0.45, LANE_Y, PAPER_Z))], blk["b3"]["f0"] - 30, f_rd - 4)
P.travel(pp["root"], [Vector((RX - 0.45, LANE_Y, PAPER_Z)), Vector((RX + 0.45, LANE_Y, PAPER_Z))], f_rd, f_pdf + 30)
# before the reader the text is grey and soft (an image of text); after, crisp with headings lit
for g in pp["groups"]:
    lit(g["mat"], [(0, 0.0), (f_rd + 8, 0.0), (f_pdf + 10, 0.35), (f_pdf + 40, 0.15)])
    lit(g["head_mat"], [(0, 0.0), (f_rd + 10, 0.0), (f_pdf + 6, 2.4), (f_pdf + 60, 1.0)])
sc_ = rd["scan"]
lit(rd["scan_m"], [(0, 0.0), (f_rd - 2, 0.0), (f_rd + 2, 4.0), (f_pdf + 30, 4.0), (f_pdf + 36, 0.0), (f_rows - 6, 0.0), (f_rows - 2, 4.0),
                   (f_all - 4, 4.0), (f_all + 4, 0.0)])
lit(rd["beam_m"], [(0, 0.0), (f_rd - 2, 0.0), (f_rd + 2, 1.2), (f_pdf + 30, 1.2), (f_pdf + 36, 0.0), (f_rows - 6, 0.0), (f_rows - 2, 1.2),
                   (f_all - 4, 1.2), (f_all + 4, 0.0)])
lit(rd["ring"], [(0, 0.5), (f_rd, 0.5), (f_rd + 6, 3.0), (f_all, 3.0), (f_all + 30, 0.6)])
# the ledger sheet: a header row (green) and rows; its header row lights when it leaves the reader
led = Q.paper("ledg", (-3.3, LANE_Y, PAPER_Z), [[{"len": 64, "head": True}] + [{"len": 64, "head": False}] * 15], w=0.26, h=0.2,
              margin=0.02, lh=0.0098, kind="ledger")
led["root"].rotation_euler = (0, 0, math.pi / 2)
lg = led["groups"][0]
K.bsdf(lg["head_mat"]).inputs["Emission Color"].default_value = K.GREEN
K.show(led["root"], [(0, False), (f_pdf + 10, True), (blk["b4"]["f0"] + 40, False)])
P.travel(led["root"], [Vector((-3.6, LANE_Y, PAPER_Z)), Vector((RX - 0.4, LANE_Y, PAPER_Z))], f_pdf + 10, f_rows - 8)
P.travel(led["root"], [Vector((RX - 0.4, LANE_Y, PAPER_Z)), Vector((RX + 0.32, LANE_Y + 0.0, PAPER_Z)),
                       Vector((RX + 0.42, LANE_Y + 0.42, PAPER_Z))], f_rows - 6, f_all + 20)
lit(lg["head_mat"], [(0, 0.0), (f_rows + 10, 0.0), (f_rows + 18, 4.0), (blk["b4"]["f0"], 1.2)])
lit(lg["mat"], [(0, 0.0), (f_rows + 10, 0.0), (f_rows + 18, 0.3)])

# ------------------------------------------------------------------------------------------------ chunking
f_ch = w("b4", "chunk")
f_struct = w("b4", "structure")
f_200 = w("b4", "two")
f_qrc = w("b4", "quick-reference")
f_three = w("b4", "three")
f_pile = w("b4", "whole")
P.travel(pp["root"], [Vector((RX + 0.45, LANE_Y, PAPER_Z)), Vector((CHX, LANE_Y, PAPER_Z))], blk["b4"]["f0"] - 20, f_ch + 6)
# the cut lines between the bands (laser light across the card), along its structure
bands = []
yy = PH / 2 - 0.022
for gi, g in enumerate(groups):
    hgt = LH * len(g)
    bands.append((yy, yy - hgt))
    yy -= hgt + LH * 0.6
cuts = []
for gi in range(len(groups) - 1):
    ycut = (bands[gi][1] + bands[gi + 1][0]) / 2
    m = K.light_mat(f"cut{gi}_m", K.SKY, 0.0)
    o = K.rbox(f"cut{gi}", (PW + 0.04, 0.0025, 0.002), bevel=0.0, seg=1, mat=m, loc=(0, 0, 0.0045), parent=pp["root"])
    o.location = (0, ycut, 0.0045)
    o.visible_shadow = False
    lit(m, [(0, 0.0), (f_struct - 2 + gi * 6, 0.0), (f_struct + 4 + gi * 6, 6.0), (f_200 + 12, 4.0), (f_200 + 24, 0.0)])
    cuts.append(o)
# the three tiles take the bands' places (the tile bars are the chunk's own lines, its header first, in sky)
TILE_H = 0.026
tiles = []
Y0 = LANE_Y
for gi, c in enumerate(chunks):
    y_top, y_bot = bands[gi]
    depth = (y_top - y_bot) + LH * 1.2
    # paper local y -> world x (the paper is turned 90 degrees: local +y = world -x)
    wx = CHX - (y_top + y_bot) / 2
    t = Q.tile(f"ck{gi}", (wx, Y0, PAPER_Z - 0.003), (PW, depth, TILE_H), header=True, lines=wrap(c["lines"]))
    t["root"].rotation_euler = (0, 0, math.pi / 2)
    tiles.append((t, wx, depth))
for gi, (t, wx, depth) in enumerate(tiles):
    r = t["root"]
    K.show(r, [(0, False), (f_200 + 18, True)])
    spread = (gi - 1) * 0.07
    K.key(r, "scale", [(0, (1, 1, 0.12)), (f_200 + 18, (1, 1, 0.12)), (f_200 + 40, (1, 1, 1.0))])
    K.key(r, "location", [(0, Vector((wx, Y0, PAPER_Z - 0.003))), (f_200 + 22, Vector((wx, Y0, PAPER_Z - 0.003))),
                          (f_200 + 60, Vector((wx + spread, Y0, PAPER_Z + 0.004)))])
    lit(t["head_m"], [(0, 0.0), (f_qrc, 0.0), (w("b4", "becomes") + gi * 5, 3.0), (f_pile, 1.2)])
    lit(t["face_m"], [(0, 0.0), (f_three - 2 + gi * 5, 0.0), (f_three + 4 + gi * 5, 1.4), (f_pile + 20, 0.3)])
K.show(pp["root"], [(f_200 + 20, True), (f_200 + 22, False)])

# ------------------------------------------------------------------------------------------------ the indexes
EMX, EMY = -0.95, 0.25
f_emb = w("b5", "embedding")
f_384 = w("b5", "three")
f_pt = w("b5", "point")
f_chroma = w("b5", "chroma")
f_bm = w("b5", "b")
f_rem = w("b5", "remembers")
t0r = tiles[0][0]["root"]
x0 = tiles[0][1] + (0 - 1) * 0.07
P.travel(t0r, [Vector((x0, Y0, PAPER_Z + 0.004)), Vector((x0, Y0, PAPER_Z + 0.08)), Vector((EMX, EMY - 0.3, PAPER_Z + 0.08)),
               Vector((EMX, EMY - 0.3, PAPER_Z + 0.004))], f_emb - 30, f_emb + 16)
vec = D["embed"]["chunk"]
plate, plate_m = K.vector_plate("vplate", vec, 24, 16, K.SKY, (EMX, EMY, PZ + 0.42), cell=0.018, vmax=0.12, glow=0.0, reveal=0.0)
K.show(plate, [(0, False), (f_emb + 6, True)])
K.key(plate, "location", [(0, Vector((EMX, EMY, PZ + 0.05))), (f_emb + 6, Vector((EMX, EMY, PZ + 0.05))), (f_384 - 4, Vector((EMX, EMY, PZ + 0.36)))])
K.key(plate, "scale", [(0, (0.2, 0.2, 0.2)), (f_emb + 6, (0.2, 0.2, 0.2)), (f_384 - 4, (1, 1, 1))])
lit(plate_m, [(0, 0.0), (f_384 - 6, 0.0), (f_384, 2.6), (f_chroma + 40, 2.6), (blk["b6"]["f0"], 1.0)])
K.keyval(plate_m.node_tree.nodes["reveal"].outputs[0], [(0, 0.0), (f_384 - 4, 0.0), (w("b5", "numbers") + 6, 1.0)])
beam_m = K.light_mat("embbeam_m", K.SKY, 0.0)
eb = K.beam("embbeam", (EMX, EMY - 0.3, PAPER_Z + 0.03), (EMX, EMY, PZ + 0.2), r=0.004, mat=beam_m)
lit(beam_m, [(0, 0.0), (f_emb + 4, 0.0), (f_emb + 10, 3.0), (f_384 + 20, 1.0), (f_pt + 10, 0.0)])

TX, TY = 0.85, 0.32
lt = Q.light_table("tbl", (TX, TY, 0.0), D["map"]["points"], size=1.5, legs=0.42)
lit(lt["bead_m"], [(0, 0.0), (f_pt - 6, 0.0), (f_pt + 24, 2.2), (blk["b6"]["f0"] + 30, 2.2), (w("b6", "nearest") - 10, 0.9),
                   (blk["b7"]["f0"], 0.9), (w("b9", "index"), 0.9), (w("b9", "index") + 8, 2.6), (w("b9", "search"), 1.0)])
# the plate's light flies to the table (the chunk joins the index); the table pulses as it lands
dot_m = K.light_mat("dot_m", K.SKY, 0.0)
dot = K.cyl("dot", 0.012, 0.012, dot_m, loc=(EMX, EMY, PZ + 0.36))
dot.visible_shadow = False
K.show(dot, [(0, False), (f_pt - 10, True), (f_pt + 22, False)])
P.travel(dot, [Vector((EMX, EMY, PZ + 0.36)), Vector(((EMX + TX) / 2, EMY, 0.85)), lt["to_world"](0, 0, 0.02)], f_pt - 10, f_pt + 20)
lit(dot_m, [(0, 4.0)])

CAX, CAY = 2.95, 0.18
cat = Q.catalogue("cat", (CAX, CAY, PZ), cols=4, rows=5, w=0.66, d=0.44, h=0.8, open_row=3, open_col=1)
dr = cat["drawer"]
K.key(dr, "location", [(0, cat["drawer_closed"]), (f_rem - 6, cat["drawer_closed"]), (f_rem + 16, cat["drawer_open"])])
for k, (co, cm) in enumerate(cat["cards"]):
    lit(cm, [(0, 0.0), (f_rem + 10 + k, 0.0), (f_rem + 18 + k, 0.25), (blk["b6"]["f0"], 0.12)])

# ------------------------------------------------------------------------------------------------ the search
f_q = w("b6", "question")
f_vs = w("b6", "vector")
f_nn = w("b6", "nearest")
f_po = w("b6", "purchase-order")
f_mat = w("b6", "m")
f_wrong = w("b6", "wrong")
f_bm6 = w("b6", "b")
f_match = w("b6", "matches")
f_first = w("b6", "first")
qpos = lt["to_world"](*D["map"]["query"], dz=0.022)
cap, cap_m = P.capsule("qcap", (qpos.x, qpos.y, qpos.z + 0.5))
K.show(cap, [(0, False), (f_q - 8, True), (f_vs + 14, False)])
P.travel(cap, [Vector((qpos.x - 0.6, qpos.y - 0.8, qpos.z + 0.55)), Vector((qpos.x, qpos.y, qpos.z + 0.35)), qpos + Vector((0, 0, 0.03))], f_q - 8, f_vs + 10)
K.key(cap, "scale", [(0, (1, 1, 1)), (f_vs, (1, 1, 1)), (f_vs + 12, (0.15, 0.15, 0.15))])
st, st_m = Q.star("qstar", qpos, r=0.016)
K.show(st, [(0, False), (f_vs + 6, True)])
lit(st_m, [(0, 0.0), (f_vs + 6, 0.0), (f_vs + 12, 8.0), (blk["b7"]["f0"] + 10, 4.0), (blk["b7"]["f0"] + 40, 0.0)])
hits = D["map"]["hits"]
for k, (u, v) in enumerate(hits):
    p = lt["to_world"](u, v, dz=0.012)
    rg, rm = Q.ring(f"hit{k}", p, r=0.018, color=K.EMBER)
    K.key(rg, "scale", [(0, (0.2, 0.2, 1)), (f_nn + k * 3, (0.2, 0.2, 1)), (f_nn + 10 + k * 3, (1, 1, 1))])
    lit(rm, [(0, 0.0), (f_nn + k * 3, 0.0), (f_nn + 6 + k * 3, 5.0), (blk["b7"]["f0"] + 10, 3.0), (blk["b7"]["f0"] + 40, 0.0)])
    bmm = K.light_mat(f"hitbeam{k}_m", K.EMBER, 0.0)
    K.beam(f"hitbeam{k}", qpos, p + Vector((0, 0, 0.01)), r=0.0018, mat=bmm)
    lit(bmm, [(0, 0.0), (f_nn + k * 3, 0.0), (f_nn + 6 + k * 3, 2.5), (blk["b7"]["f0"] + 10, 1.5), (blk["b7"]["f0"] + 40, 0.0)])
    K.empty(f"hit{k}_pin", p + Vector((0, 0, 0.02)))
# BM25: three cards rise out of the open drawer, green (the three QRC-03 chunks, ranked 1-3), then two more, grey
for k, (co, cm) in enumerate(cat["cards"][:5]):
    base = co.location.copy()
    f0 = f_match + 6 + k * 7
    K.key(co, "location", [(0, base), (f0, base), (f0 + 16, base + Vector((0, 0, 0.12 - 0.012 * k)))])
    gold = k < 3
    if not gold:
        K.bsdf(cm).inputs["Emission Color"].default_value = K.lin("#9aa6b8")
    lit(cm, [(f0 - 1, 0.12), (f0 + 8, 3.0 if gold else 0.8), (blk["b7"]["f0"] + 20, 1.5 if gold else 0.4)])
    K.empty(f"card{k}_pin", (0, 0, 0.06), parent=co)

# ------------------------------------------------------------------------------------------------ the reranker
SOX = 4.05
RL_Y = -0.34
P.rail("rrlane", 3.25, 4.95, RL_Y, LZ)
so = Q.sorter("so", (SOX, RL_Y, PZ), span=0.36, h=0.32, d=0.16)
so["root"].rotation_euler = (0, 0, math.pi / 2)
f_rr = w("b7", "reranker")
f_reads = w("b7", "reads")
f_order = w("b7", "order")
f_57 = w("b7", "fifty-seven")
lit(so["beam_m"], [(0, 0.0), (f_reads - 4, 0.0), (f_reads + 2, 3.0), (f_order + 30, 3.0), (f_order + 40, 0.0)])
lit(so["led"], [(0, 0.6), (f_rr, 0.6), (f_rr + 6, 3.0), (f_57 + 30, 1.0)])
bm = D["search"]["bm25"]["items"]
rr = D["search"]["best"]["items"]
bm_cites = [i["cite"] for i in bm]
CW, CD, CHH = 0.07, 0.05, 0.018
IN_X = [3.32 + 0.0 for _ in range(20)]
cand = []
out_slot = {}
for k, it in enumerate(rr):
    out_slot[it["cite"]] = k
unk = [it["cite"] for it in rr if it["cite"] not in bm_cites]
mapping = {}   # input index -> output index
for i, c in enumerate(bm_cites):
    if c in out_slot:
        mapping[i] = out_slot[c]
for j, c in enumerate(unk):
    mapping[10 + j] = out_slot[c]
OUTX0 = SOX + 0.22
for i in range(20):
    t = Q.tile(f"cd{i}", (3.3, RL_Y, LZ - 0.022), (CW, CD, CHH), header=True, lines=())
    r = t["root"]
    gold = (bm[i]["gold"] if i < 10 else (mapping.get(i) is not None and rr[mapping[i]]["gold"]))
    f0 = f_rr + 4 + i * 3
    K.show(r, [(0, False), (f0 - 1, True)])
    start = Vector((CAX + 0.1 - 0.04 * (i % 5), CAY - 0.42, LZ - 0.022))
    queue = Vector((3.3 + (i % 5) * 0.08, RL_Y - 0.12 + (i // 5) * 0.075 - 0.0, LZ - 0.022))
    P.travel(r, [start, queue], f0, f0 + 14)
    P.travel(r, [queue, Vector((SOX - 0.2, RL_Y, LZ - 0.022)), Vector((SOX, RL_Y, LZ - 0.022))], f_reads + i * 2, f_reads + i * 2 + 18)
    if i in mapping:
        o = mapping[i]
        dst = Vector((OUTX0 + (o % 5) * 0.085, RL_Y + 0.07 - (o // 5) * 0.075 + 0.0, LZ - 0.022))
        P.travel(r, [Vector((SOX, RL_Y, LZ - 0.022)), Vector((SOX + 0.14, RL_Y, LZ - 0.022)), dst], f_order + i, f_order + 26 + i)
        lit(t["edge_m"], [(0, 0.0), (f_order + 20 + i, 0.0), (f_order + 30 + i, 3.5 if rr[o]["gold"] else 0.0)])
        lit(t["face_m"], [(0, 0.0), (f_order + 20, 0.0), (f_order + 30, 1.2)])
        K.empty(f"out{o}_pin", (0, 0, 0.03), parent=r)
        cand.append((r, t, o))
    else:
        # not kept: it sinks through the floor of the arch
        K.key(r, "scale", [(0, (1, 1, 1)), (f_order + i, (1, 1, 1)), (f_order + 14 + i, (0.05, 0.05, 0.05))])
        K.show(r, [(f_order + 16 + i, False)])
    lit(t["head_m"], [(0, 1.2)])
    if i < 10:
        lit(t["edge_m"], [(f0, 0.0), (f0 + 10, 2.5 if gold else 0.0), (f_reads + i * 2, 2.5 if gold else 0.0), (f_reads + i * 2 + 18, 0.0)])

# ------------------------------------------------------------------------------------------------ the model and the answer
MX = 5.55
MA = P.machine("model", (MX, 0.12, PZ + 0.04), w=0.9, d=0.55, h=0.72)
K.rbox("riser", (1.0, 0.66, 0.04), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(MX, 0.12, PZ + 0.02))
f_top = w("b8", "top")
f_prompt = w("b8", "prompt")
f_ans = w("b8", "answers")
f_cit = w("b8", "citations")
SLOT = Vector((MX - 0.45 - 0.05, 0.12, PZ + 0.04 + 0.105))
for r, t, o in cand:
    a = Vector(r.location)
    keys = P.travel(r, [Vector((OUTX0 + (o % 5) * 0.085, RL_Y + 0.07 - (o // 5) * 0.075, LZ - 0.022)),
                        Vector((OUTX0 + (o % 5) * 0.085, RL_Y + 0.07 - (o // 5) * 0.075, SLOT.z + 0.05)), SLOT + Vector((-0.08, 0, 0.0)),
                        SLOT + Vector((0.05, 0, 0))], f_top + o * 4, f_prompt + 14 + o * 4)
    K.key(r, "scale", [(f_prompt + 6 + o * 4, (1, 1, 1)), (f_prompt + 14 + o * 4, (0.3, 0.3, 0.3))])
    K.show(r, [(f_prompt + 15 + o * 4, False)])


def think(f0, f1, peak=2.4):
    K.glow_keys(MA["led"], [(f0 - 6, 0.3), (f0, peak), (f1, peak), (f1 + 10, 0.3)])
    K.glow_keys(MA["tower"]["idle"], [(f0 - 8, 0.4), (f0, 2.6), (f1, 2.6), (f1 + 12, 0.4)])


K.glow_keys(MA["led"], [(0, 0.3)])
K.glow_keys(MA["tower"]["idle"], [(0, 0.4)])
K.key(MA["inner"].data, "energy", [(0, 6.0)])
think(f_prompt + 10, f_cit + 10)
OUT = Vector((MX + 0.45 + 0.08, 0.12, PZ + 0.04 + 0.105))
res, res_m, res_in = P.result_slab("res", tuple(OUT))
K.show(res, [(0, False), (f_cit - 8, True)])
P.travel(res, [OUT - Vector((0.16, 0, 0)), OUT + Vector((0.2, -0.05, 0))], f_cit - 6, f_cit + 26)
P.rail("outshelf", MX + 0.46, MX + 0.95, 0.07, OUT.z)

# ------------------------------------------------------------------------------------------------ the close
f_p9 = {k: w("b9", k) for k in ("parse", "chunk", "index", "search", "rerank", "answer")}
lit(rd["ring"], [(f_p9["parse"] - 2, 0.6), (f_p9["parse"] + 4, 5.0), (f_p9["chunk"] + 20, 1.0)])
for gi, (t, wx, depth) in enumerate(tiles):
    if gi:
        lit(t["face_m"], [(f_p9["chunk"] - 2, 0.3), (f_p9["chunk"] + 4, 3.0), (f_p9["index"] + 20, 0.6)])
for k, (co, cm) in enumerate(cat["cards"][:3]):
    lit(cm, [(f_p9["search"] - 2, 1.5), (f_p9["search"] + 4, 4.0), (f_p9["rerank"] + 20, 1.5)])
lit(so["beam_m"], [(f_p9["rerank"] - 2, 0.0), (f_p9["rerank"] + 4, 3.0), (f_p9["answer"] + 20, 0.0)])
think(f_p9["answer"], f_p9["answer"] + 30)
lit(res_m, [(0, 2.4), (f_p9["answer"], 2.4), (f_p9["answer"] + 6, 6.0), (f_p9["answer"] + 40, 2.4)])

# Q-EMMA: its 11 gold sources rise in front of the archive; the 2 the search found (both the quote e-mail) in green
f_bc = w("b9", "brightcell")
f_eleven = w("b9", "eleven")
f_two = w("b9", "finds")
GOLD = D["q_emma"]["detail"]
for k, g in enumerate(GOLD):
    x = -4.95 + k * 0.145
    t = Q.tile(f"gold{k}", (x, -0.42, PZ), (0.11, 0.09, 0.024), header=False, lines=())
    r = t["root"]
    f0 = f_eleven - 10 + k * 3
    K.show(r, [(0, False), (f0 - 1, True)])
    K.key(r, "location", [(0, Vector((x, -0.42, PZ - 0.05))), (f0, Vector((x, -0.42, PZ - 0.05))), (f0 + 14, Vector((x, -0.42, PZ)))])
    found = g["rank"] is not None
    K.bsdf(t["face_m"]).inputs["Emission Color"].default_value = K.GREEN if found else K.EMBER
    lit(t["face_m"], [(0, 0.0), (f0, 0.0), (f0 + 10, 0.5), (f_two, 0.5), (f_two + 8, 4.0 if found else 0.25)])
    lit(t["edge_m"], [(0, 0.0), (f_two, 0.0), (f_two + 8, 4.0 if found else 0.0)])
    K.empty(f"gold{k}_pin", (0, 0, 0.04), parent=r)

# ------------------------------------------------------------------------------------------------ cameras
b = blk
c1 = K.Cam(sc, "c_ask", lens=45, fstop=3.2).cut(0)
c1.keys([(0, (SX - 0.05, -1.75, 0.62), (SX, 0.05, 0.42)),
         (b["b1"]["f1"] + 18, (SX + 0.08, -1.45, 0.58), (SX, 0.05, 0.42))])
c2 = K.Cam(sc, "c_dump", lens=36, fstop=4.0).cut(b["b2"]["f0"] - 12)
c2.keys([(b["b2"]["f0"] - 12, (-5.3, -2.2, 0.95), (-4.2, 0.1, 0.5)),
         (w("b2", "spreadsheets"), (-4.75, -2.15, 1.05), (-4.1, 0.1, 0.55)),
         (b["b2"]["f1"] + 18, (-3.95, -2.15, 1.0), (-4.0, 0.1, 0.45))])
c3 = K.Cam(sc, "c_parse", lens=40, fstop=3.2).cut(b["b3"]["f0"] - 12)
c3.keys([(b["b3"]["f0"] - 12, (-3.75, -1.95, 1.0), (-2.95, LANE_Y, 0.15)),
         (f_rd, (-3.3, -1.85, 1.05), (-2.62, LANE_Y, 0.15)),
         (f_rows, (-3.05, -1.75, 1.0), (-2.4, LANE_Y + 0.05, 0.14)),
         (b["b3"]["f1"] + 18, (-2.85, -1.7, 1.0), (-2.2, LANE_Y + 0.05, 0.13))])
c4 = K.Cam(sc, "c_chunk", lens=40, fstop=3.0).cut(b["b4"]["f0"] - 12)
c4.keys([(b["b4"]["f0"] - 12, (-2.05, -1.15, 0.95), (-1.6, LANE_Y + 0.05, 0.14)),
         (f_struct, (-1.6, -0.95, 1.0), (-1.45, LANE_Y + 0.02, 0.13)),
         (f_qrc, (-1.35, -0.92, 0.9), (-1.45, LANE_Y + 0.02, 0.14)),
         (f_pile, (-1.3, -1.25, 0.95), (-1.45, LANE_Y + 0.1, 0.16)),
         (b["b4"]["f1"] + 18, (-1.05, -1.55, 1.05), (-1.25, 0.0, 0.2))])
c5 = K.Cam(sc, "c_index", lens=36, fstop=3.6).cut(b["b5"]["f0"] - 12)
c5.keys([(b["b5"]["f0"] - 12, (-1.6, -1.45, 0.85), (-1.0, 0.05, 0.35)),
         (f_384, (-1.35, -1.25, 0.75), (-0.95, EMY, 0.48)),
         (f_pt - 14, (-1.2, -1.35, 0.95), (-0.55, EMY, 0.45))])
c5b = K.Cam(sc, "c_table", lens=32, fstop=4.0).cut(f_pt - 4)
c5b.keys([(f_pt - 4, (0.15, -1.55, 1.55), (TX, TY, 0.42)),
          (f_chroma + 10, (0.35, -1.4, 1.45), (TX, TY, 0.44))])
c5c = K.Cam(sc, "c_cat", lens=40, fstop=3.2).cut(f_bm - 8)
c5c.keys([(f_bm - 8, (2.05, -1.95, 1.15), (CAX, CAY - 0.2, 0.5)),
          (b["b5"]["f1"] + 18, (2.4, -1.5, 1.15), (CAX, CAY - 0.25, 0.5))])
c6 = K.Cam(sc, "c_search", lens=34, fstop=4.0).cut(b["b6"]["f0"] - 12)
c6.keys([(b["b6"]["f0"] - 12, (0.25, -1.65, 1.45), (TX, TY, 0.42)),
         (f_vs + 10, (0.55, -0.95, 1.25), (qpos.x - 0.05, qpos.y, qpos.z)),
         (f_wrong + 10, (0.62, -0.75, 1.05), (qpos.x - 0.05, qpos.y, qpos.z))])
c6b = K.Cam(sc, "c_bm", lens=40, fstop=3.2).cut(f_bm6 - 8)
c6b.keys([(f_bm6 - 8, (2.62, -1.05, 1.35), (CAX - 0.08, -0.22, 0.7)),
          (b["b6"]["f1"] + 18, (2.7, -0.92, 1.32), (CAX - 0.08, -0.2, 0.74))])
c7 = K.Cam(sc, "c_rerank", lens=36, fstop=3.6).cut(b["b7"]["f0"] - 12)
c7.keys([(b["b7"]["f0"] - 12, (3.05, -1.75, 1.1), (3.75, RL_Y, 0.14)),
         (f_reads + 20, (3.4, -1.65, 1.05), (4.05, RL_Y, 0.15)),
         (f_order + 30, (3.95, -1.5, 0.98), (4.45, RL_Y + 0.02, 0.13)),
         (b["b7"]["f1"] + 18, (4.05, -1.55, 1.02), (4.45, RL_Y + 0.02, 0.13))])
c8 = K.Cam(sc, "c_answer", lens=36, fstop=3.6).cut(b["b8"]["f0"] - 12)
c8.keys([(b["b8"]["f0"] - 12, (4.45, -1.65, 0.95), (5.1, 0.0, 0.35)),
         (f_cit, (5.2, -1.85, 0.95), (5.75, 0.05, 0.4)),
         (b["b8"]["f1"] + 18, (5.55, -1.8, 0.9), (5.95, 0.05, 0.35))])
c9 = K.Cam(sc, "c_close", lens=28, fstop=7.0).cut(b["b9"]["f0"] - 12)
c9.keys([(b["b9"]["f0"] - 12, (4.2, -3.2, 2.0), (2.0, 0.1, 0.3)),
         (f_p9["answer"] + 10, (-1.4, -4.7, 2.3), (0.0, 0.1, 0.3))])
c9b = K.Cam(sc, "c_gold", lens=34, fstop=4.0).cut(f_bc - 10)
c9b.keys([(f_bc - 10, (-4.9, -1.85, 0.95), (-4.25, -0.2, 0.25)),
          (END, (-4.45, -1.75, 0.85), (-4.2, -0.25, 0.22))])

pins = ["scr_pin", "scr_toppin", "vit_0_pin", "vit_1_pin", "vit_2_pin", "vit_1_mid", "rd_pin", "qrc_mid", "qrc_top", "ledg_mid",
        "ck0_top", "ck1_top", "ck2_top", "vplate_top", "tbl_pin", "qstar", "cat_pin_top", "so_pin", "model_pin_top", "model_pin_win",
        "res_top", "qcap_top"] + [f"hit{k}_pin" for k in range(10)] + [f"card{k}_pin" for k in range(5)] + \
       [f"out{k}_pin" for k in range(10)] + [f"gold{k}_pin" for k in range(len(GOLD))]
K.empty("cat_pin_top", (CAX + 0.3, CAY - 0.24, PZ + 0.62))
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
