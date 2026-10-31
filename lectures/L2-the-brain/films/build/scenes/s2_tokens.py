"""Film s2, "What you send, cut into tokens". Builds films/s2_tokens.blend.

b1 Emma's question is one bar of 15 abutting tiles; a blade of light cuts it into tokens.
b2 the whole chat drops onto a dark table as a page of 100 tiles in its messages (system 72, Emma 15, markers 13).
b3 macros: one tile per common word; " Manchester" (19361); " Northbridge" = " North" + "bridge"; "5,400" -> 5 , 4 0 0.
b4 byte pair encoding on the real hand example (experiments/logs/bpe.json): battery and packs fuse merge by merge.
b5 the vocabulary table: a tall rack of rows; its top drawer holds the last learned BPE rows and the 22 special
   tokens, then the whole table lights: one row per token the tokenizer knows (151,665).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s123 as P  # noqa: E402
import s2_layout as S  # noqa: E402

FILM = "s2_tokens"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
N = len(TOK)
w = B.w
END = B.frames - 1
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5", "b6")}
PZ = 0.11
YB = -2.05          # the question bar / the 5,400 bar, in front of the page
BPE_X = 7.5         # the BPE bench
RACK_X = 13.0       # the vocabulary rack

sc = K.reset(B.frames)
K.studio(sc, focus=(0.0, -0.4, 0.4), key_power=3000, span=0.0)
for i, (dx, lp) in enumerate(((BPE_X, 0.9), (RACK_X, 1.0))):
    K.soft_light(f"keyx{i}", (dx - 4.0, -6.5, 7.5), (dx, 0, 0.4), 2400 * lp, 12.0, (1.0, 0.97, 0.93))
    K.soft_light(f"rimx{i}", (dx + 1.0, 7.0, 3.2), (dx, 0, 0.4), 1600 * lp, 14.0, (0.7, 0.82, 1.0))
table = K.plinth("table", -2.8, 2.8, y=-0.45, depth=4.0, height=PZ)
K.plinth("bench", BPE_X - 1.8, BPE_X + 1.8, y=-0.3, depth=1.6, height=PZ)

slots, nlines = S.page_slots(TOK)
ROLEGLOW = {"system": K.lin("#9aa8c0"), "user": K.SKY, "template": K.lin("#e7c79a")}
tiles, faces = {}, {}
for t in TOK:
    i = t["i"]
    line, col = slots[i]
    x, y = S.page_xy(line, col)
    r, fm = K.token_tile(f"tok{i}", t["role"], (x, y, PZ))
    K.bsdf(fm).inputs["Emission Color"].default_value = ROLEGLOW[t["role"]]
    tiles[i], faces[i] = r, fm
    K.glow_keys(fm, [(0, 0.0)])

# ---------------------------------------------------------------- b1: one bar, cut into tokens
f_tok = w("b1", "tokens")
Q = list(range(80, 95))
for k, i in enumerate(Q):
    xb = -2.1 + k * 0.30 + 0.15
    xs = (k - 7) * 0.36
    home = Vector(tiles[i].location)
    K.key(tiles[i], "location", [(0, (xb, YB, PZ)), (f_tok - 4, (xb, YB, PZ)), (f_tok + 16, (xs, YB, PZ)),
                                (b["b2"]["f0"] + 30, (xs, YB, PZ)), (b["b2"]["f0"] + 60 + k, home)])
blade_m = K.light_mat("blade_m", K.SKY, 0.0)
blade = K.rbox("blade", (0.004, 0.36, 0.22), bevel=0.0, seg=1, mat=blade_m, loc=(-2.4, YB, PZ + 0.1))
blade.visible_shadow = False
K.key(blade, "location", [(0, (-2.4, YB, PZ + 0.1)), (f_tok - 12, (-2.4, YB, PZ + 0.1)), (f_tok + 14, (2.45, YB, PZ + 0.1))])
K.glow_keys(blade_m, [(0, 0.0), (f_tok - 12, 0.0), (f_tok - 8, 6.0), (f_tok + 12, 6.0), (f_tok + 16, 0.0)])
K.show(blade, [(0, False), (f_tok - 13, True), (f_tok + 17, False)])
for k, i in enumerate(Q):
    fk = f_tok - 8 + int(k * 1.6)
    K.glow_keys(faces[i], [(fk - 2, 0.0), (fk + 2, 1.3), (fk + 20, 0.35)])

# ---------------------------------------------------------------- b2: the page of 100 tiles drops in; the groups light
f_cut, f_72, f_15, f_13 = w("b2", "cut"), w("b2", "seventy-two"), w("b2", "fifteen"), w("b2", "thirteen")
for t in TOK:
    i = t["i"]
    if i in Q:
        continue
    home = Vector(tiles[i].location)
    f0 = f_cut - 6 + int(i * 0.45)
    K.key(tiles[i], "location", [(0, home + Vector((0, 0, 1.4))), (f0, home + Vector((0, 0, 1.4))), (f0 + 18, home)])
    K.show(tiles[i], [(0, False), (f0, True)])
for t in TOK:
    i, role = t["i"], t["role"]
    f0 = {"system": f_72, "user": f_15, "template": f_13}[role]
    K.glow_keys(faces[i], [(f0 - 2 + int(i * 0.15) - 10, 0.0 if role != "user" else 0.35), (f0 + 6 + int(i * 0.15) - 10, 1.1),
                           (b["b2"]["f1"] + 10, 0.6), (b["b3"]["f0"] + 10, 0.12)])

# ---------------------------------------------------------------- b3: macros on the page
f_man, f_nb, f_nbN, f_num, f_five = w("b3", "manchester"), w("b3", "northbridge"), w("b3", "north"), w("b3", "number", 1), w("b3", "five", 1)
for i, fx in ((92, f_man), (6, f_nb), (7, f_nb)):
    K.glow_keys(faces[i], [(fx - 6, 0.12), (fx + 6, 1.8), (fx + 90, 1.8), (fx + 110, 0.3)])
    sock = K.bsdf(faces[i]).inputs["Emission Color"]
    base = tuple(sock.default_value)
    K.keyval(sock, [(fx - 8, base), (fx - 6, tuple(K.SKY)), (fx + 110, tuple(K.SKY)), (fx + 112, base)])
for i, dx in ((6, -0.05), (7, 0.05)):   # North | bridge part a little
    h = Vector(tiles[i].location)
    K.key(tiles[i], "location", [(f_nbN - 4, h), (f_nbN + 10, h + Vector((dx, -0.04, 0.03))), (f_nbN + 60, h + Vector((dx, -0.04, 0.03))),
                                (f_nbN + 76, h)])
# the 5,400 bar: five tiles that start abutting, then split into its five tokens
CUT = T["number_cuts"]["5,400"]
nb = []
for k, c in enumerate(CUT):
    r, fm = K.token_tile(f"num{k}", "answer", (0, YB, PZ - 0.2), size=(0.2, 0.2, 0.075))
    nb.append((r, fm))
    xa = -0.4 + k * 0.2
    xs = (k - 2) * 0.3
    f_split = w("b3", "five", 1) + 10 + 0
    K.key(r, "location", [(0, (xa, YB, PZ - 0.2)), (f_num - 4, (xa, YB, PZ - 0.2)), (f_num + 12, (xa, YB, PZ)),
                          (w("b3", "tokens") - 2, (xa, YB, PZ)), (w("b3", "tokens") + 14 + k * 2, (xs, YB, PZ))])
    K.show(r, [(0, False), (f_num - 5, True), (b["b4"]["f0"] + 20, False)])
    hit = [w("b3", "five", 2), w("b3", "comma"), w("b3", "four", 1), w("b3", "zero"), w("b3", "zero", 1)][k]
    K.glow_keys(fm, [(0, 0.0), (f_num + 8, 0.8), (hit - 4, 0.8), (hit + 6, 3.2), (hit + 40, 1.6)])

# ---------------------------------------------------------------- b4: byte pair encoding, merge by merge
f_bytes, f_merge = w("b4", "single"), w("b4", "merging")
life, mf, states = S.segment_life(f_merge, f_merge + 150)
seg_objs = {}
for key, L in life.items():
    wd, a, bb = key
    n = bb - a
    yw = {"battery": -0.05, "packs": -0.62}[wd]
    r, fm = K.token_tile(f"bpe_{wd}_{a}_{bb}", "answer", (BPE_X, yw, PZ), size=(n * S.CW - 0.014, 0.17, 0.06))
    seg_objs[key] = (r, fm, yw)
    vis = [(0, False), (L["start"] if L["start"] else b["b4"]["f0"] + 20, True)]
    if L["end"]:
        vis.append((L["end"], False))
    K.show(r, vis)
    K.glow_keys(fm, [(0, 0.0), (f_bytes - 6, 0.3), (f_bytes + 8, 1.4)])
for k in range(len(states)):
    step, pair, ntok, words = states[k]
    for wd in S.WORDS:
        segs = words[wd]
        xs = S.seg_x(segs)
        sp = S.spans(segs)
        for (a, bb), x in zip(sp, xs):
            r, fm, yw = seg_objs[(wd, a, bb)]
            if k == 0:
                K.key(r, "location", [(0, (BPE_X + x, yw, PZ))])
                continue
            fm_ = mf[k - 1]
            # every segment of the new layout, and the parts that fuse into it, glide to their new places
            K.key(r, "location", [(fm_ + 8, (BPE_X + x, yw, PZ))])
            prev = states[k - 1][3][wd]
            for (pa, pb), px in zip(S.spans(prev), S.seg_x(prev)):
                if a <= pa and pb <= bb and (pa, pb) != (a, bb):
                    ro, fmo, _ = seg_objs[(wd, pa, pb)]
                    sub = x - (bb - a) * S.CW / 2 + (pa - a) * S.CW + (pb - pa) * S.CW / 2
                    K.key(ro, "location", [(fm_, (BPE_X + px, yw, PZ)), (fm_ + 8, (BPE_X + sub, yw, PZ))])
            if (a, bb) not in S.spans(prev):   # the fused tile flashes as it forms
                K.glow_keys(fm, [(fm_ + 7, 0.0), (fm_ + 9, 4.0), (fm_ + 30, 1.4)])
            else:
                K.key(r, "location", [(fm_, (BPE_X + S.seg_x(prev)[S.spans(prev).index((a, bb))], yw, PZ))])

# ---------------------------------------------------------------- b5: the vocabulary rack and its top drawer
RW, RD, RH = 1.5, 0.7, 2.2
rack = K.empty("rack", (RACK_X, 0.2, PZ))
K.rbox("rack_body", (RW + 0.08, RD, RH + 0.08), bevel=0.02, seg=4, mat=K.anod("rack_shell", (0.05, 0.055, 0.068, 1)), loc=(0, 0, RH / 2 + 0.04), parent=rack)
face_m = P.rack_face_mat("rack_face", bands=1187)
K.plane("rack_faceplane", RW, RH, face_m, loc=(0, -RD / 2 - 0.002, RH / 2 + 0.04), parent=rack)
for sx in (-1, 1):
    K.rbox(f"rack_rail{sx}", (0.03, 0.03, RH + 0.12), bevel=0.008, seg=3, mat=K.M("alu"), loc=(sx * (RW / 2 + 0.03), -RD / 2, RH / 2 + 0.04), parent=rack)
K.rbox("rack_cap", (RW + 0.14, RD + 0.06, 0.04), bevel=0.012, seg=4, mat=K.M("alu_dark"), loc=(0, 0, RH + 0.12), parent=rack)
# the drawer: the last 20 learned BPE rows (sky) and the 22 special tokens (violet)
rowc = [tuple(c * 0.9 for c in K.SKY[:3])] * 20 + [tuple(K.K_COL[:3])] * 22
dimg = P.rows_image("drawer_rows", rowc, px=24, width=96)
dm = P.image_glow_mat("drawer_m", dimg, 0.0)
drawer = K.empty("drawer", (0, -RD / 2, RH - 0.12), parent=rack)
K.rbox("drawer_box", (RW - 0.06, 0.7, 0.1), bevel=0.01, seg=3, mat=K.M("alu_dark"), loc=(0, -0.35, 0), parent=drawer)
K.plane("drawer_top", RW - 0.14, 0.62, dm, loc=(0, -0.35, 0.0505), rot=(-1.5708, 0, 0), parent=drawer)
K.rbox("drawer_handle", (0.4, 0.02, 0.025), bevel=0.008, seg=3, mat=K.M("alu"), loc=(0, -0.71, 0.0), parent=drawer)
K.empty("drawer_pin_sky", (0, -0.35 + 0.31 - 0.62 * 10 / 42, 0.06), parent=drawer)
K.empty("drawer_pin_special", (0, -0.35 + 0.31 - 0.62 * 31 / 42, 0.06), parent=drawer)
K.empty("rack_pin_top", (RW / 2, -RD / 2, RH + 0.1), parent=rack)
K.empty("rack_pin_mid", (RW / 2, -RD / 2, RH * 0.5), parent=rack)
f_add, f_22, f_tk, f_665, f_keeps = w("b5", "add"), w("b5", "twenty-two"), w("b5", "tokenizer"), w("b5", "sixty-five"), w("b5", "keeps")
f_tz = w("b4", "tokenizer")
K.glow_keys(face_m, [(0, 0.0), (f_tz, 0.0), (f_tz + 16, 0.3)])
sw = face_m.node_tree.nodes["sweep"].outputs[0]
K.keyval(sw, [(0, 0.0), (f_tz + 10, 0.0), (w("b4", "pieces", 1) + 10, 0.97), (f_665 - 10, 0.97), (f_665 + 14, 1.0)])
K.glow_keys(face_m, [(f_keeps - 4, 0.3), (f_keeps + 12, 0.5)])
K.key(drawer, "location", [(0, (0, 0.3, RH - 0.12)), (f_add - 4, (0, 0.3, RH - 0.12)), (f_add + 22, (0, -0.32, RH - 0.12))])
K.glow_keys(dm, [(0, 0.0), (f_add, 0.0), (f_add + 16, 0.7), (f_22, 0.7), (f_22 + 10, 1.3)])

# ---------------------------------------------------------------- cameras
c1 = K.Cam(sc, "c_bar", lens=34, fstop=3.2).cut(0)
c1.keys([(0, (2.5, -3.7, 0.95), (-0.2, YB, 0.14)), (b["b1"]["f1"] + 10, (2.1, -3.35, 0.82), (-0.2, YB, 0.14))])
c2 = K.Cam(sc, "c_page", lens=32, fstop=4.5).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (1.4, -4.6, 2.6), (0.0, -0.25, 0.1)), (b["b2"]["f1"] + 12, (0.9, -4.1, 2.35), (0.0, -0.2, 0.1))])
xm, ym = S.page_xy(*slots[92])
c3 = K.Cam(sc, "c_line", lens=40, fstop=2.6).cut(b["b3"]["f0"] - 8)
xl, yl = S.page_xy(*slots[80])
c3.keys([(b["b3"]["f0"] - 8, (xl + 1.6, yl - 1.35, 0.72), (xl + 0.8, yl, 0.15)), (f_man - 10, (xm + 0.2, ym - 1.2, 0.62), (xm - 0.25, ym, 0.15))])
c4 = K.Cam(sc, "c_man", lens=50, fstop=2.4).cut(f_man - 8)
c4.keys([(f_man - 8, (xm + 0.75, ym - 1.6, 0.85), (xm - 0.05, ym + 0.1, 0.12)), (f_nb - 10, (xm + 0.6, ym - 1.4, 0.78), (xm - 0.05, ym + 0.1, 0.12))])
xn, yn = S.page_xy(*slots[6])
c5 = K.Cam(sc, "c_nb", lens=50, fstop=2.4).cut(f_nb - 8)
c5.keys([(f_nb - 8, (xn + 0.9, yn - 1.65, 0.9), (xn + 0.25, yn - 0.1, 0.12)), (f_num - 14, (xn + 0.75, yn - 1.45, 0.82), (xn + 0.25, yn - 0.1, 0.12))])
c6 = K.Cam(sc, "c_num", lens=40, fstop=2.8).cut(f_num - 12)
c6.keys([(f_num - 12, (0.6, YB - 1.6, 0.62), (0.0, YB, 0.15)), (b["b3"]["f1"] + 12, (0.4, YB - 1.4, 0.56), (0.0, YB, 0.15))])
c7 = K.Cam(sc, "c_bpe", lens=40, fstop=3.2).cut(b["b4"]["f0"] - 8)
c7.keys([(b["b4"]["f0"] - 8, (BPE_X + 0.4, -2.35, 1.0), (BPE_X, -0.35, 0.15)), (w("b4", "tokenizer") - 12, (BPE_X + 0.2, -2.0, 0.88), (BPE_X, -0.35, 0.15))])
c8 = K.Cam(sc, "c_rack", lens=32, fstop=3.5).cut(f_tz - 12)
c8.keys([(f_tz - 12, (RACK_X + 1.9, -3.4, 1.0), (RACK_X, 0.0, 1.1)),
         (f_add - 10, (RACK_X + 1.6, -3.1, 1.3), (RACK_X, 0.0, 1.3))])
c9 = K.Cam(sc, "c_drawer", lens=38, fstop=3.2).cut(f_add - 8)
dz = PZ + RH - 0.12
c9.keys([(f_add - 8, (RACK_X + 0.9, -2.0, dz + 0.95), (RACK_X, -0.5, dz)), (f_tk - 6, (RACK_X + 0.75, -1.8, dz + 0.85), (RACK_X, -0.5, dz))])
c10 = K.Cam(sc, "c_rack2", lens=30, fstop=4.0).cut(f_tk - 4)
c10.keys([(f_tk - 4, (RACK_X + 1.6, -2.6, 2.0), (RACK_X, -0.2, 1.6)), (b["b5"]["f1"] + 12, (RACK_X + 2.1, -3.6, 1.5), (RACK_X, 0.0, 1.2))])
c12 = K.Cam(sc, "c_end", lens=32, fstop=4.5).cut(b["b6"]["f0"] - 8)
c12.keys([(b["b6"]["f0"] - 8, (0.6, -4.0, 2.2), (0.0, -0.2, 0.1)), (END, (1.6, -5.3, 2.9), (0.0, -0.2, 0.1))])

pins = [f"tok{i}_front" for i in range(N)] + [f"tok{i}_top" for i in range(N)]
pins += [f"num{k}_front" for k in range(5)] + [f"bpe_{wd}_{a}_{bb}_front" for (wd, a, bb) in life]
pins += ["drawer_pin_sky", "drawer_pin_special", "rack_pin_top", "rack_pin_mid"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
