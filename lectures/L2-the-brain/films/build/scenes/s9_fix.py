"""Film s9, "Why it made the number up, and what fixes it". Builds films/s9_fix.blend.

The invented "1 0 0" on the strip; light arcs from the first digit back over all 104 positions (the real head-averaged
attention, averaged over the 24 blocks); only the date's digits are numbers. Then the strip opens and the Ledgerline line
(23 green tiles) drops into the system prompt; the same model answers "5,400" (green); block 10, head 13 sends its arc
onto the fact's 5,400. Two sockets light: Knowledge (Lecture 3) and Tools (Lecture 4).

Numbers: brain3d/trace.json tokens, attention.digit.avg, generation.greedy, facts.* (tokens, fact_positions, greedy,
digits, attention_to_fact.best_head).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s789 as P  # noqa: E402

FILM = "s9_fix"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
G = T["generation"]["greedy"]
F = T["facts"]
FT = F["tokens"]
FG = F["greedy"]
NFP = len(FT)                          # 123
SHIFT = NFP - len(TOK)                 # 23
FP0 = F["fact_positions"][0]           # 75
AVG = T["attention"]["digit"]["avg"]   # 24 x 104
ATT = [sum(AVG[l][j] for l in range(len(AVG))) / len(AVG) for j in range(len(AVG[0]))]
BH = F["attention_to_fact"]["best_head"]
PITCH, PZ = 0.36, 0.11
DATE = [t["i"] for t in TOK if t["digit"]]


def X(i):
    return (i - 99) * PITCH


w = B.w
END = B.frames - 1
blk = B.blocks
sc = K.reset(B.frames)
K.studio(sc, focus=(X(100), 0.0, 0.4), key_power=3000, span=30.0)
K.plinth("plinth", X(0) - 0.45, X(NFP + 8) + 0.5, depth=0.5, height=PZ)

f_add = w("b3", "add")
f_open0, f_open1 = f_add - 6, w("b3", "straight") + 6
faces = {}
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    faces[i] = fm
    if i >= FP0:   # these slide right to make room for the fact line
        K.key(root, "location", [(0, (X(i), 0, PZ)), (f_open0, (X(i), 0, PZ)), (f_open1, (X(i + SHIFT), 0, PZ))])
for i in DATE:   # the date's digits: the only numbers in the prompt
    P.set_face(faces[i], K.EMBER)
    K.glow_keys(faces[i], [(0, 0.0), (w("b2", "only") - 4, 0.0), (w("b2", "date"), 2.0), (blk["b2"]["f1"] + 30, 0.4)])

# the first answer: We currently have (space) 1 0 0
old = []
for j in range(7):
    dig = G[j]["text"].strip().isdigit()
    root, fm = K.token_tile(f"gen{j}", "digit" if dig else "answer", (X(100 + j), 0, PZ))
    P.set_face(fm, K.EMBER if dig else K.SKY)
    K.glow_keys(fm, [(0, 0.5 if dig else 0.12), (w("b2", "plausible") - 4, 0.5 if dig else 0.12),
                     (w("b2", "plausible") + 6, 2.2 if dig else 0.12), (blk["b2"]["f1"] + 10, 0.5 if dig else 0.12)])
    K.key(root, "location", [(0, (X(100 + j), 0, PZ)), (f_add - 30 + 2 * j, (X(100 + j), 0, PZ)),
                             (f_add - 12 + 2 * j, (X(100 + j), 0, PZ - 0.2))])
    K.show(root, [(0, True), (f_add - 10 + 2 * j, False)])
    old.append(root)

# arcs from the first digit back over every position it can see (0..103), brightness = its real attention
SRC = Vector((X(104), 0.0, PZ + 0.12))
f_tr, f_104 = w("b1", "trace"), w("b1", "hundred", 1)
amax = max(ATT)
for j, a in enumerate(ATT):
    if a < 0.002:
        continue
    dst = Vector((X(j), 0.0, PZ + 0.09))
    m = K.light_mat(f"arc{j}_m", K.EMBER if j in DATE else K.SKY, 0.0)
    o = K.arc(f"arc{j}", SRC, dst, lift=0.35 + 0.06 * (abs(104 - j) ** 0.5), r=0.004 + 0.008 * (a / amax) ** 0.5, mat=m)
    d = int((104 - j) * 0.6)
    K.grow(o, [(0, 0.0), (f_tr + d, 0.0), (f_tr + d + 18, 1.0)])
    g = 0.4 + 5.0 * (a / amax) ** 0.6
    f_off = w("b2", "nothing")
    K.glow_keys(m, [(0, 0.0), (f_tr + d, 0.0), (f_tr + d + 6, g), (f_off - 10, g), (f_off + 8, 0.0)])
    K.show(o, [(0, False), (f_tr + d - 1, True), (f_off + 10, False)])

# the fact line: 23 green tiles drop into the gap, as the narrator reads it
fact_words = {75: "ledgerline", 80: "bat", 82: "five", 86: "manchester", 87: "main", 88: "stores", 91: "five", 93: "four", 96: "on", 97: "hand"}
fstart = w("b3", "ledgerline")
fact_drop = {}
for i in F["fact_positions"]:
    k = i - FP0
    fact_drop[i] = max(f_open1 - 4, fstart - 6) + int(k * 5.5)
fact_drop[91] = min(fact_drop[91], w("b3", "five", 1) - 4)
for i in F["fact_positions"]:
    ft = FT[i]
    num = ft["text"].strip().replace(",", "").isdigit() or ft["text"] == ","
    P.drop_tile(f"fact{i}", "fact", (X(i), 0, PZ), fact_drop[i], face_color=K.GREEN, face_rest=0.3 if num else 0.06, end=END)

# the new answer: We have (space) 5 , 4 0 0  (green: it now comes from a fact)
f_ans = w("b4", "answer")
new = []
for j in range(8):
    dig = FG[j]["text"].strip().isdigit() or FG[j]["text"] == ","
    f0 = (w("b4", "same") - 6 + j * 4) if j < 3 else (w("b4", "five") - 10 + (j - 3) * 5)
    P.drop_tile(f"new{j}", "fact" if dig else "answer", (X(NFP + j), 0, PZ), f0, face_color=K.GREEN if dig else K.SKY,
                face_rest=0.3 if dig else 0.08, end=END)
    new.append(f"new{j}")

# block 10, head 13, writing the 5: its arcs (real weights) back over the facts prompt
SRC2 = Vector((X(NFP + 3), 0.0, PZ + 0.12))
f_head, f_77 = w("b4", "block"), w("b4", "seventy-seven")
row = BH["row"]
for j, a in enumerate(row):
    if a < 0.003 or j >= NFP + 3:
        continue
    dst = Vector((X(j), 0.0, PZ + 0.09))
    m = K.light_mat(f"harc{j}_m", K.GREEN if j in F["attention_to_fact"]["fact_number_positions"] else K.SKY, 0.0)
    o = K.arc(f"harc{j}", SRC2, dst, lift=0.35 + 0.06 * (abs(NFP + 3 - j) ** 0.5), r=0.004 + 0.012 * a ** 0.5, mat=m)
    d = int((NFP + 3 - j) * 0.35)
    K.grow(o, [(0, 0.0), (f_head + d, 0.0), (f_head + d + 18, 1.0)])
    K.glow_keys(m, [(0, 0.0), (f_head + d, 0.0), (f_head + d + 6, 0.5 + 7.0 * a ** 0.6)])
    K.show(o, [(0, False), (f_head + d - 1, True)])

# two sockets: Knowledge (Lecture 3) and Tools (Lecture 4)
SK = Vector((X(NFP + 3), -0.95, 0.0))
K.rbox("sockbase", (2.2, 0.8, 0.09), bevel=0.012, seg=5, mat=K.M("plinth"), loc=(SK.x, SK.y, 0.045))
s3, m3 = P.socket("sock3", (SK.x - 0.5, SK.y, 0.09), r=0.2, color=K.GREEN)
s4, m4 = P.socket("sock4", (SK.x + 0.5, SK.y, 0.09), r=0.2, color=K.SKY)
for root in (s3, s4):
    K.show(root, [(0, False), (blk["b5"]["f0"] - 30, True)])
K.show(bpy.data.objects["sockbase"], [(0, False), (blk["b5"]["f0"] - 30, True)])
K.glow_keys(m3, [(0, 0.0), (w("b5", "three") - 2, 0.0), (w("b5", "three") + 10, 5.0)])
K.glow_keys(m4, [(0, 0.0), (w("b5", "four") - 2, 0.0), (w("b5", "four") + 10, 5.0)])

# ------------------------------------------------------------------------------------------------ cameras
c1 = K.Cam(sc, "c_back", lens=40, fstop=2.6).cut(0)
c1.keys([(0, (X(105.8), -1.15, 0.6), (X(104.6), 0.0, 0.22)),
         (f_tr - 4, (X(105.6), -1.2, 0.62), (X(104.4), 0.0, 0.24)),
         (f_tr + 40, (X(107.2), -2.3, 1.25), (X(97), 0.0, 0.35)),
         (blk["b1"]["f1"] + 10, (X(107.6), -2.6, 1.45), (X(93), 0.0, 0.3))])
c1.lens([(f_tr - 4, 40), (f_tr + 40, 28)])
c2 = K.Cam(sc, "c_date", lens=40, fstop=2.6).cut(blk["b2"]["f0"] - 10)
c2.keys([(blk["b2"]["f0"] - 10, (X(50.5), -1.25, 0.62), (X(47.5), 0.0, 0.22)),
         (w("b2", "nothing") - 12, (X(51), -1.1, 0.58), (X(48.3), 0.0, 0.22))])
c3 = K.Cam(sc, "c_none", lens=34, fstop=3.0).cut(w("b2", "nothing") - 10)
c3.keys([(w("b2", "nothing") - 10, (X(84), -1.3, 0.66), (X(89), 0.0, 0.22)),
         (w("b2", "plausible") - 30, (X(100), -1.3, 0.64), (X(104), 0.0, 0.22)),
         (blk["b2"]["f1"] + 10, (X(106.6), -1.15, 0.6), (X(104.8), 0.0, 0.22))])
c4 = K.Cam(sc, "c_fact", lens=32, fstop=3.0).cut(blk["b3"]["f0"] - 10)
c4.keys([(blk["b3"]["f0"] - 10, (X(72.5), -1.7, 0.95), (X(80), 0.0, 0.2)),
         (fstart, (X(74), -1.6, 0.9), (X(82), 0.0, 0.2)),
         (w("b3", "five", 1) - 10, (X(88.5), -1.35, 0.72), (X(93), 0.0, 0.2)),
         (blk["b3"]["f1"] + 10, (X(90), -1.3, 0.7), (X(94), 0.0, 0.2))])
c5 = K.Cam(sc, "c_new", lens=38, fstop=2.8).cut(blk["b4"]["f0"] - 10)
c5.keys([(blk["b4"]["f0"] - 10, (X(NFP + 6), -1.4, 0.66), (X(NFP + 3), 0.0, 0.22)),
         (f_head - 12, (X(NFP + 7), -1.3, 0.62), (X(NFP + 4.5), 0.0, 0.22))])
c6 = K.Cam(sc, "c_head", lens=30, fstop=3.2).cut(f_head - 10)
c6.keys([(f_head - 10, (X(88.5), -1.7, 0.95), (X(100), 0.0, 0.45)),
         (f_77, (X(89.6), -1.5, 0.78), (X(92.8), 0.0, 0.3)),
         (blk["b4"]["f1"] + 10, (X(90.8), -1.3, 0.66), (X(92.8), 0.0, 0.24))])
c7 = K.Cam(sc, "c_sock", lens=36, fstop=3.2).cut(blk["b5"]["f0"] - 10)
c7.keys([(blk["b5"]["f0"] - 10, (SK.x + 0.2, SK.y - 2.0, 1.0), (SK.x, SK.y + 0.6, 0.25)),
         (END, (SK.x + 0.1, SK.y - 1.6, 0.85), (SK.x, SK.y + 0.4, 0.2))])

pins = [f"tok{i}_front" for i in list(range(40, 54)) + list(range(80, 100))] + [f"gen{j}_front" for j in range(7)] + ["gen4_top"]
pins += [f"fact{i}_front" for i in F["fact_positions"]] + ["fact91_top", "fact95_top", "fact75_top"]
pins += [f"{n}_front" for n in new] + [f"{n}_top" for n in new] + ["sock3_top", "sock4_top"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
