"""Film `generation`: "Generating the whole answer, token by token". Builds films/generation.blend.

The row: Emma's 100 prompt tiles, then the 20 answer tiles as they are chosen. Behind every position stands its KV
cache: a slender glass stack of 24 floors (one per block; the violet half = keys, the warm half = values).
  b1  "We" lands at position 100; the input is 101 tokens; the pass runs again (a sweep over the row).
  b2  causality: a position only looks back (a glass wall after position 100); the 100 earlier columns cannot change.
  b3  their keys and values are kept: the 100 prompt stacks light floor by floor (256 numbers per position per block).
  b4  one new column (position 100) climbs the 24 blocks; at every block a ribbon of light reads back over all 101
      positions, its brightness = that block's real attention (build/data/generation_attn.json, heads averaged).
  b5-b7  the answer grows: each chosen tile lands on its spoken word; before it, the previous position's stack builds
      (one pass = one new column). The first digit's column is opened at blocks 21-24 (logit lens 4, 4, 5, 1).
      The last tile, <|im_end|>, gets no column: generation stops there.
  b8  five temperature-0.7 samples on a stepped riser beside the green Ledgerline plaque (5,400).
  b9  the whole row, every column lit: one machine, run once per token.
Numbers: brain3d/trace.json (generation.greedy, logit_lens.digits, generation.samples_t07, facts.truth) and
build/data/generation_data.json / generation_attn.json (capture_next_gen.py).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import bpy  # noqa: E402,F401
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_next_gen as NG  # noqa: E402
import props_s456 as P4  # noqa: E402
import props_s789 as P7  # noqa: E402

FILM = "generation"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
GA = K.load("films/build/data/generation_attn.json")
TOK = T["tokens"]
G = T["generation"]["greedy"]
SAMPLES = T["generation"]["samples_t07"]
w = B.w
END = B.frames - 1
blk = B.blocks
PITCH, PZ = 0.36, 0.11
DIGITS = {4, 5, 6}
FL, FP = 24, 0.034            # floors, floor pitch of a cache stack
SY = 0.36                     # stacks stand behind the tiles
SZ = PZ                       # stack base


def X(i):
    return (i - 100) * PITCH


def floor_z(k):
    return SZ + 0.01 + (k - 0.5) * FP


sc = K.reset(B.frames)
K.studio(sc, focus=(1.0, 0.0, 0.5), key_power=3000, span=10.0)
K.soft_light("farkey", (-16.0, -6.5, 7.5), (-16.0, 0, 0.3), 1500, 12.0, (1.0, 0.97, 0.93))
K.soft_light("farrim", (-16.0, 7.0, 3.2), (-16.0, 0, 0.3), 1000, 14.0, (0.7, 0.82, 1.0))
K.plinth("plinth", X(0) - 0.5, X(120) + 0.4, y=0.12, depth=0.82, height=PZ)

# ------------------------------------------------------------------------------------------------ drop and build frames
D = {0: w("b1", "joins") - 6, 1: w("b5", "currently") - 4, 2: w("b5", "have") - 4, 3: w("b5", "space") - 4, 4: w("b6", "one") - 6,
     5: w("b6", "zero") - 4, 6: w("b6", "zero", 1) - 4, 7: w("b7", "city") - 4, 8: w("b7", "e-bike") - 4, 9: w("b7", "e-bike") + 2,
     10: w("b7", "e-bike") + 8, 11: w("b7", "battery") - 4, 12: w("b7", "packs") - 4, 13: w("b7", "available") - 4, 14: w("b7", "in") - 3,
     15: w("b7", "our") - 2, 16: w("b7", "manchester") - 2, 17: w("b7", "stores") - 3, 18: w("b7", "stop") - 4, 19: w("b7", "im") - 4}
BUILD = {0: (w("b4", "new"), w("b4", "but") + 70)}
BUILD[1] = (w("b5", "join") - 4, D[2] - 4)
BUILD[2] = (D[2] + 10, D[3] - 3)
BUILD[3] = (D[3] + 16, D[4] - 3)
BUILD[4] = (w("b6", "settles") + 20, D[5] - 2)
BUILD[5] = (D[5] + 12, D[6] - 2)
BUILD[6] = (D[6] + 12, D[7] - 2)
for j in range(7, 19):
    e = D[j + 1] - 2
    BUILD[j] = (max(D[j] + 1, e - 20), e)

# ------------------------------------------------------------------------------------------------ the prompt
prompt_m = NG.stack_mat("kv_prompt", FL, 0.0, 0.0)
f_kv0, f_kv1 = w("b3", "keys"), w("b3", "blocks") + 10
for t in TOK:
    i = t["i"]
    root, fm = K.token_tile(f"tok{i}", t["role"], (X(i), 0, PZ))
    sr, _ = NG.cache_stack(f"st{i}", (X(i), SY, SZ), FL, FP, mat=prompt_m)
    fs = w("b3", "their") - 6 + int(18 * i / 99)      # the cache stacks rise only when the cache is introduced
    K.show(sr, [(0, False), (fs, True)])
    K.key(sr, "scale", [(0, (1, 1, 0.02)), (fs, (1, 1, 0.02)), (fs + 16, (1, 1, 1))])
    fi = 120 + int(60 * i / 99)   # b1: the pass runs over all 101 positions
    K.glow_keys(fm, [(0, 0.1), (w("b1", "pass") - 40 + int(36 * i / 99), 0.1), (w("b1", "pass") - 34 + int(36 * i / 99), 2.0),
                     (w("b1", "pass") - 6 + int(36 * i / 99), 0.25), (END, 0.25)])
K.keyval(prompt_m.node_tree.nodes["level"].outputs[0], [(0, 0.0), (f_kv0, 0.0), (f_kv1, 24.0)])
pglow = [(0, 0.0), (f_kv0 - 4, 0.0), (f_kv0 + 6, 1.8), (blk["b3"]["f1"] + 20, 0.9)]
# every later pass reads the whole cache: a soft pulse on all prompt stacks
for j in range(1, 19):
    s, e = BUILD[j]
    pglow += [(s, 0.9), (s + max(2, (e - s) // 2), 1.5), (e + 4, 0.9)]
pglow += [(w("b9", "every"), 0.9), (w("b9", "machine"), 1.8), (END, 1.7)]
K.glow_keys(prompt_m, sorted(dict(pglow).items()))

# ------------------------------------------------------------------------------------------------ the answer
ans_m = {}
for j, g in enumerate(G):
    role = "digit" if j in DIGITS else ("template" if j == 19 else "answer")
    col = K.EMBER if j in DIGITS else K.SKY
    root, fm = P7.drop_tile(f"tok{100 + j}", role, (X(100 + j), 0, PZ), D[j], face_color=col, face_rest=0.22 if j in DIGITS else 0.14,
                            end=END)
    if j < 19:   # position 119 (<|im_end|>) gets no column: generation stops there
        m = NG.stack_mat(f"kv_{100 + j}", FL, 0.0, 0.0)
        ans_m[j] = m
        sr, _ = NG.cache_stack(f"st{100 + j}", (X(100 + j), SY, SZ), FL, FP, mat=m)
        s, e = BUILD[j]
        K.show(sr, [(0, False), (s - 2, True)])
        K.keyval(m.node_tree.nodes["level"].outputs[0], [(0, 0.0), (s, 0.0), (e, 24.0)])
        K.glow_keys(m, [(0, 0.0), (s - 1, 0.0), (s, 2.6), (e + 6, 2.6), (e + 30, 1.1)] +
                    ([(w("b9", "every"), 1.1), (w("b9", "machine"), 2.2), (END, 2.0)] if e < w("b9", "every") else []))

# the hero climb (b4): a cursor rides up position 100's stack; at each floor a ribbon reads back over all 101 positions
s0, e0 = BUILD[0]
cur_m = K.light_mat("cursor", K.SKY, 0.0)
cur = K.rbox("cursor", (0.26, 0.1, 0.022), bevel=0.006, seg=3, mat=cur_m, loc=(X(100), SY - 0.02, floor_z(1)))
K.show(cur, [(0, False), (s0 - 2, True), (e0 + 24, False)])
K.key(cur, "location", [(0, (X(100), SY - 0.02, floor_z(1))), (s0, (X(100), SY - 0.02, floor_z(1))), (e0, (X(100), SY - 0.02, floor_z(24)))])
K.glow_keys(cur_m, [(0, 0.0), (s0 - 2, 0.0), (s0 + 4, 6.0), (e0 + 6, 6.0), (e0 + 22, 0.0)])
PB = GA["steps"][0]["per_block"]          # position 100 (We) reading positions 0..100, per block
xs = [X(p) for p in range(101)]
for k in range(1, FL + 1):
    wts = PB[k - 1]
    vm = max(wts[1:]) or 1.0
    sh, shm = NG.attn_sheet(f"sheet{k}", X(0) - 0.2, X(100), floor_z(k), wts, xs, y=SY - 0.045, h=FP * 0.8, vmax=vm)
    fk = s0 + int((e0 - s0) * (k - 0.5) / FL)
    K.show(sh, [(0, False), (fk - 2, True), (blk["b5"]["f0"] + 20, False)])
    K.key(sh, "scale", [(0, (0.001, 1, 1)), (fk - 2, (0.001, 1, 1)), (fk + 10, (1, 1, 1))])
    K.glow_keys(shm, [(0, 0.0), (fk - 2, 0.0), (fk + 4, 4.0), (fk + 40, 1.6), (blk["b5"]["f0"], 0.6), (blk["b5"]["f0"] + 14, 0.0)])

# b2: causality, a glass wall after position 100 (the future does not exist yet)
f_only, f_never, f_nothing = w("b2", "only"), w("b2", "never"), w("b2", "nothing")
wall, wedge = P4.glass_wall("wall", (X(100.5), 0.1, PZ), w=0.8, h=1.25)
K.show(wall, [(0, False), (f_only - 10, True), (blk["b3"]["f0"] + 10, False)])
K.key(wall, "location", [(0, (X(100.5), 0.1, PZ - 1.3)), (f_only - 10, (X(100.5), 0.1, PZ - 1.3)), (f_only + 10, (X(100.5), 0.1, PZ))])
K.glow_keys(wedge, [(0, 0.0), (f_never - 4, 0.0), (f_never + 8, 5.0)])
# a back-looking ribbon at mid height: position 100's attention averaged over the 24 blocks (real)
avg = [sum(PB[k][p] for k in range(FL)) / FL for p in range(101)]
lb, lbm = NG.attn_sheet("lookback", X(0) - 0.2, X(100), 0.5, avg, xs, y=-0.02, h=0.035, vmax=max(avg[1:]))
K.show(lb, [(0, False), (f_only - 4, True), (blk["b3"]["f0"] + 4, False)])
K.key(lb, "scale", [(0, (0.001, 1, 1)), (f_only - 4, (0.001, 1, 1)), (f_never + 6, (1, 1, 1))])
K.glow_keys(lbm, [(0, 0.0), (f_only - 4, 4.0), (blk["b2"]["f1"] + 20, 4.0), (blk["b3"]["f0"], 0.0)])

# b6: the first digit's column (position 103) opened at blocks 21-24: ember lens bands
lens_words = {21: w("b6", "twenty-one"), 22: w("b6", "twenty-two"), 23: w("b6", "twenty-three"), 24: w("b6", "twenty-four")}
f_look, f_then = w("b6", "look"), w("b6", "then", 1)
for k in (21, 22, 23, 24):
    lm = K.light_mat(f"lens{k}_m", K.EMBER if k < 24 else K.SKY, 0.0)
    band = K.rbox(f"lensband{k}", (0.24, 0.012, FP * 0.62), bevel=0.003, seg=2, mat=lm, loc=(X(103), SY - 0.048, floor_z(k)))
    K.empty(f"lens{k}", (X(103) + 0.13, SY - 0.05, floor_z(k)))
    f0 = lens_words[k]
    K.glow_keys(lm, [(0, 0.0), (f_look, 0.0), (f0 - 2, 0.0), (f0 + 6, 5.0), (f_then - 10, 5.0), (f_then + 10, 0.0)])

# ------------------------------------------------------------------------------------------------ b8: the samples
RX = X(121) + 0.6
for r in range(5):
    K.rbox(f"step{r}", (2.6, 0.36, 0.11 + 0.1 * r), bevel=0.01, seg=4, mat=K.M("plinth"), loc=(RX + 1.15, 0.36 * r, (0.11 + 0.1 * r) / 2))
sw = [("three", 0), ("one", 0), ("over", 0), ("fifty", 0), ("fifteen", 0)]
sample_tiles = []
for r, s in enumerate(SAMPLES):
    txt = f"{s['numbers'][0]:,}"
    f0 = w("b8", sw[r][0], sw[r][1]) - 8
    row = []
    for c, ch in enumerate(txt):
        nm = f"s{r}_{c}"
        P7.drop_tile(nm, "digit", (RX + 0.15 + c * 0.34, 0.36 * r, 0.11 + 0.1 * r), f0 + 3 * c, face_color=K.EMBER, face_rest=0.22, end=END)
        row.append(nm)
    sample_tiles.append(row)
K.rbox("truthbase", (1.9, 0.72, PZ), bevel=0.012, seg=5, mat=K.M("plinth"), loc=(RX + 3.75, 0.3, PZ / 2))
PLQ = Vector((RX + 3.75, 0.52, PZ))
t_l = w("b8", "ledgerline")
plq, plq_m = P7.plaque("plaque", tuple(PLQ), w=0.8, h=0.26)
K.show(plq, [(0, False), (t_l - 12, True)])
K.key(plq, "location", [(0, PLQ + Vector((0, 0, 0.5))), (t_l - 12, PLQ + Vector((0, 0, 0.5))), (t_l + 8, PLQ)])
K.glow_keys(plq_m, [(0, 0.0), (t_l, 0.0), (t_l + 12, 4.0)])
truth = []
for c, ch in enumerate("5,400"):
    nm = f"t_{c}"
    P7.drop_tile(nm, "fact", (RX + 3.11 + c * 0.32, 0.14, PZ), w("b8", "five") - 6 + 3 * c, face_color=K.GREEN, face_rest=0.3, end=END)
    truth.append(nm)

# ------------------------------------------------------------------------------------------------ cameras
b = blk
top = floor_z(24)
c1 = K.Cam(sc, "c_append", lens=35, fstop=3.5).cut(0)
c1.keys([(0, (X(102.6), -1.75, 0.75), (X(98.2), 0.25, 0.32)),
         (w("b1", "pass"), (X(103.2), -2.2, 1.0), (X(96.5), 0.3, 0.38)),
         (b["b1"]["f1"] + 12, (X(103.6), -2.5, 1.2), (X(94.0), 0.3, 0.42))])
c2 = K.Cam(sc, "c_back", lens=30, fstop=5.0).cut(b["b2"]["f0"] - 4)
c2.keys([(b["b2"]["f0"] - 4, (X(104.5), -2.4, 1.35), (X(92.0), 0.3, 0.45)),
         (f_only, (X(104.0), -2.0, 1.15), (X(95.0), 0.2, 0.5)),
         (b["b2"]["f1"] + 12, (X(103.5), -1.9, 1.1), (X(96.0), 0.2, 0.55))])
c3 = K.Cam(sc, "c_cache", lens=32, fstop=4.5).cut(b["b3"]["f0"] - 4)
c3.keys([(b["b3"]["f0"] - 4, (X(102.5), -2.3, 1.1), (X(92.5), SY, 0.6)),
         (w("b3", "cache"), (X(101.6), -1.9, 1.0), (X(96.0), SY, 0.62)),
         (w("b3", "two"), (X(100.6), -1.05, 0.85), (X(98.6), SY, 0.62)),
         (w("b3", "six"), (X(100.8), -1.4, 0.95), (X(98.0), SY, 0.62)),
         (b["b3"]["f1"] + 12, (X(102.0), -2.6, 1.4), (X(92.0), SY, 0.55))])
c4 = K.Cam(sc, "c_climb", lens=26, fstop=4.0).cut(b["b4"]["f0"] - 4)
c4.keys([(b["b4"]["f0"] - 4, (X(103.2), -1.45, 0.4), (X(96.0), SY, 0.42)),
         (s0 + (e0 - s0) // 2, (X(103.4), -1.55, 0.62), (X(95.5), SY, 0.5)),
         (e0, (X(103.6), -1.65, 0.95), (X(95.0), SY, 0.55)),
         (b["b4"]["f1"] + 12, (X(103.8), -1.9, 1.1), (X(94.5), SY, 0.5))])
c5 = K.Cam(sc, "c_words", lens=36, fstop=4.0).cut(b["b5"]["f0"] - 4)
c5.keys([(b["b5"]["f0"] - 4, (X(101.0), -2.2, 0.95), (X(100.8), SY * 0.5, 0.45)),
         (b["b5"]["f1"] + 12, (X(102.4), -2.2, 0.95), (X(102.0), SY * 0.5, 0.45))])
c6 = K.Cam(sc, "c_digit", lens=40, fstop=4.0).cut(b["b6"]["f0"] - 4)
c6.keys([(b["b6"]["f0"] - 4, (X(103.4), -1.9, 0.85), (X(103.6), SY * 0.5, 0.42)),
         (f_look - 6, (X(103.6), -1.8, 0.8), (X(103.8), SY * 0.5, 0.42))])
c6b = K.Cam(sc, "c_lens", lens=42, fstop=3.5).cut(f_look)
c6b.keys([(f_look, (X(102.6), -1.25, top + 0.05), (X(103.2), SY, top - 0.09)),
          (f_then - 12, (X(102.8), -1.15, top - 0.02), (X(103.3), SY, top - 0.1))])
c6c = K.Cam(sc, "c_zeros", lens=36, fstop=4.0).cut(f_then - 10)
c6c.keys([(f_then - 10, (X(104.2), -2.0, 0.9), (X(104.8), SY * 0.5, 0.42)),
          (b["b6"]["f1"] + 12, (X(104.8), -2.0, 0.9), (X(105.4), SY * 0.5, 0.42))])
c7 = K.Cam(sc, "c_rest", lens=32, fstop=4.5).cut(b["b7"]["f0"] - 4)
c7.keys([(b["b7"]["f0"] - 4, (X(106.2), -1.75, 0.78), (X(108.4), SY * 0.4, 0.34)),
         (w("b7", "stores"), (X(114.0), -1.75, 0.78), (X(116.2), SY * 0.4, 0.34)),
         (w("b7", "special"), (X(116.6), -1.7, 0.76), (X(118.4), SY * 0.4, 0.34)),
         (w("b7", "means"), (X(116.8), -1.75, 0.78), (X(118.6), SY * 0.4, 0.34)),
         (w("b7", "twenty"), (X(110.0), -3.6, 1.6), (X(110.0), SY * 0.5, 0.45)),
         (b["b7"]["f1"] + 12, (X(110.0), -3.8, 1.7), (X(110.0), SY * 0.5, 0.45))])
c8 = K.Cam(sc, "c_samples", lens=36, fstop=3.5).cut(b["b8"]["f0"] - 4)
c8.keys([(b["b8"]["f0"] - 4, (RX - 0.9, -1.9, 1.05), (RX + 0.6, 0.6, 0.35)),
         (w("b8", "fifteen") + 10, (RX + 0.5, -2.3, 1.25), (RX + 1.0, 0.6, 0.42)),
         (t_l, (RX + 1.6, -2.5, 1.25), (RX + 2.0, 0.5, 0.38)),
         (b["b8"]["f1"] + 12, (RX + 2.4, -2.7, 1.25), (RX + 2.6, 0.45, 0.36))])
c9 = K.Cam(sc, "c_close", lens=28, fstop=6.0).cut(b["b9"]["f0"] - 4)
c9.keys([(b["b9"]["f0"] - 4, (X(112), -2.6, 1.3), (X(100), SY, 0.5)),
         (END, (X(118), -5.2, 2.6), (X(96), SY, 0.45))])

# ------------------------------------------------------------------------------------------------ pins
pins = [f"tok{i}_front" for i in range(80, 120)] + [f"tok{i}_top" for i in range(80, 120)]
pins += [f"st{i}_top" for i in (90, 95, 99, 100, 101, 103, 118)] + [f"st{i}_f{k}" for i in (99, 100, 103) for k in (1, 12, 21, 22, 23, 24)]
pins += [f"lens{k}" for k in (21, 22, 23, 24)] + ["wall_top", "cursor"]
pins += [f"{n}_top" for row in sample_tiles for n in row] + [f"{n}_front" for row in sample_tiles for n in row]
pins += ["plaque_top", "plaque_mid"] + [f"{n}_front" for n in truth] + [f"{n}_top" for n in truth]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
