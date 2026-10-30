"""Film s1, "The game: predict the next token". Builds films/s1_game.blend.

One sealed machine (the model, its 24-floor stack glowing behind frosted glass) on the plinth. Emma's 100 tokens
stand on the strip at its input slot; on the right, glass columns fill with the real next-token probabilities
(trace.json final.last, T=1): We 56.4%, As 7.9%, Manchester 6.1%, In 5.3%, Our 4.2%, At 2.8%. We is picked, flies
round to the strip, the strip grows (We, " currently", " have", " "), and the columns now bet on the first digit
(final.digit, T=1): 1 33.6%, 2 20.8%, 5 11.6%, 3 11.3%, 4 8.8%, 6 4.4%.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
from mathutils import Vector  # noqa: E402

import l2kit as K  # noqa: E402
import props_s123 as P  # noqa: E402

FILM = "s1_game"
B = K.Beats(FILM)
T = K.load("brain3d/trace.json")
TOK = T["tokens"]
N = len(TOK)
LAST = N - 1
TOP = T["final"]["last"]["1.0"][:6]
DIG = T["final"]["digit"]["1.0"][:6]
GEN = T["generation"]["greedy"][:4]          # We, " currently", " have", " "

PZ = 0.11
PITCH = 0.36
SX = -1.02                                    # x of the last prompt tile (at the input slot)
w = B.w
END = B.frames - 1
b = {k: B.blocks[k] for k in ("b1", "b2", "b3", "b4", "b5")}

sc = K.reset(B.frames)
K.studio(sc, focus=(0.3, 0.0, 0.4), key_power=3000, span=22.0)
K.plinth("plinth", -40.0, 3.0, depth=0.9, height=PZ)
MA = P.machine("model", (0.0, 0.05, PZ))

# ---------------------------------------------------------------- the strip (a parent that shifts left as tokens join)
strip = K.empty("strip", (0, 0, 0))
faces = {}
for t in TOK:
    i = t["i"]
    r, fm = K.token_tile(f"tok{i}", t["role"], (SX - (LAST - i) * PITCH, -0.02, PZ), parent=strip)
    faces[i] = fm

# ---------------------------------------------------------------- the bets: a tray, six columns, six candidate tiles
CX = [0.98 + k * 0.33 for k in range(6)]
P.tray("tray", CX[0] - 0.2, CX[-1] + 0.2, 0.05, PZ)
cols = []
for k in range(6):
    mr, liq, lm = K.meter(f"col{k}", (CX[k], 0.12, PZ + 0.02), height=0.58, r=0.032, color=K.SKY)
    cols.append((mr, liq, lm))
cand, cand_f, dig, dig_f = [], [], [], []
ZLOW = PZ - 0.12
for k in range(6):
    r, fm = K.token_tile(f"cand{k}", "answer", (CX[k], -0.2, PZ), size=(0.27, 0.2, 0.07))
    cand.append(r); cand_f.append(fm)
    r2, fm2 = K.token_tile(f"dig{k}", "answer", (CX[k], -0.2, ZLOW), size=(0.27, 0.2, 0.07))
    dig.append(r2); dig_f.append(fm2)
# the four answer tiles that join the strip
ans = []
for k in range(4):
    r, fm = K.token_tile(f"ans{k}", "answer", (CX[0], -0.2, ZLOW))
    ans.append((r, fm))

# ---------------------------------------------------------------- b1: the text goes in, a guess comes out
f_in, f_out = w("b1", "text"), w("b1", "out")
K.key(strip, "location", [(0, (-1.6, 0, 0)), (f_in - 4, (-1.6, 0, 0)), (f_in + 40, (0, 0, 0))])


def read_wave(f0, peak=0.9):
    """A wave of light runs along the strip into the machine (the model reads every token at once)."""
    for i in range(N):
        fi = f0 + int((i - 70) * 0.7) if i >= 70 else f0 - 10
        K.glow_keys(faces[i], [(fi - 8, 0.0), (fi, peak if i >= 70 else 0.6), (fi + 16, 0.0)])


for i in range(N):
    K.glow_keys(faces[i], [(0, 0.0)])
read_wave(f_in + 40)
idle = MA["tower"]["idle"]
K.glow_keys(idle, [(0, 0.4), (f_in + 50, 0.4), (f_in + 66, 2.6), (f_out + 20, 1.2)])
K.glow_keys(MA["slot_in"], [(0, 0.0), (f_in + 44, 0.0), (f_in + 56, 3.0), (f_in + 90, 0.4)])
K.glow_keys(MA["slot_out"], [(0, 0.0), (f_out, 0.0), (f_out + 10, 3.5), (f_out + 40, 0.6)])
K.glow_keys(MA["led"], [(0, 1.0)])

# b2: 100 tokens; the model reads them all and scores every token it knows
f_100, f_read, f_score = w("b2", "hundred"), w("b2", "reads"), w("b2", "score")
read_wave(f_read)
K.glow_keys(idle, [(f_read, 1.2), (f_read + 14, 3.2), (f_score + 30, 3.2), (b["b3"]["f0"], 1.2)])
K.glow_keys(MA["slot_out"], [(f_score, 0.6), (f_score + 12, 3.5), (b["b3"]["f0"], 1.0)])

# b3: the columns fill on the words
fill_at = [w("b3", "we"), w("b3", "as"), w("b3", "manchester"), w("b3", "in"), w("b3", "five") + 10, w("b3", "five") + 22]
for k, (mr, liq, lm) in enumerate(cols):
    p = TOP[k]["p"]
    K.key(liq, "scale", [(0, (1, 1, 0.001)), (fill_at[k] - 4, (1, 1, 0.001)), (fill_at[k] + 20, (1, 1, max(0.002, p)))])
    K.glow_keys(lm, [(0, 0.0), (fill_at[k] - 4, 0.0), (fill_at[k] + 8, 1.2 + 5.0 * (p / TOP[0]["p"]) ** 0.6)])
    K.glow_keys(cand_f[k], [(0, 0.0), (fill_at[k] - 2, 0.0), (fill_at[k] + 10, 0.4 + 2.6 * (p / TOP[0]["p"]) ** 0.6)])

# b4: pick We; it flies to the strip; three more tokens join; the bets move to the first digit
f_pick, f_add, f_again, f_later, f_digit = w("b4", "pick"), w("b4", "add"), w("b4", "again"), w("b4", "few"), w("b4", "digit")
shifts = [f_add - 6, f_later + 6, f_later + 34, f_later + 62]
for k, fs in enumerate(shifts):
    K.key(strip, "location", [(fs, (-PITCH * k, 0, 0)), (fs + 16, (-PITCH * (k + 1), 0, 0))])
# We is the real candidate tile 0: it lifts out of the tray and flies round to the end of the strip
We = cand[0]
land = Vector((SX, -0.02, PZ))
P.arc_path(We, f_pick + 4, (CX[0], -0.2, PZ), land, lift=0.95, dur=44)
for k, fs in enumerate(shifts[1:], start=1):
    K.key(We, "location", [(fs, land - Vector((PITCH * (k - 1), 0, 0))), (fs + 16, land - Vector((PITCH * k, 0, 0)))])
K.glow_keys(cand_f[0], [(f_pick + 40, 3.0), (f_pick + 60, 1.4)])
# " currently", " have", " ": out of the output slot, round to the strip, quick
for k in range(1, 4):
    r, fm = ans[k]
    f0 = shifts[k] - 4
    P.arc_path(r, f0 - 20, (0.85, 0.0, PZ), land, lift=0.95, dur=36)
    K.key(r, "location", [(0, (0.85, 0.0, ZLOW)), (f0 - 21, (0.85, 0.0, ZLOW))])
    for kk in range(k + 1, 4):
        fs = shifts[kk]
        K.key(r, "location", [(fs, land - Vector((PITCH * (kk - k - 1), 0, 0))), (fs + 16, land - Vector((PITCH * (kk - k), 0, 0)))])
    K.show(r, [(0, False), (f0 - 21, True)])
    K.glow_keys(fm, [(0, 0.0), (f0 + 10, 1.6), (f0 + 40, 0.5)])
K.show(ans[0][0], [(0, False)])
for fs in shifts:
    K.glow_keys(idle, [(fs - 6, 1.2), (fs + 4, 3.0), (fs + 20, 1.2)])
# the word candidates sink and the columns drain; the digit candidates rise and fill
f_sink = f_later - 6
for k in range(1, 6):
    x = CX[k]
    K.key(cand[k], "location", [(f_sink, (x, -0.2, PZ)), (f_sink + 16, (x, -0.2, ZLOW))])
for k, (mr, liq, lm) in enumerate(cols):
    K.key(liq, "scale", [(f_sink, (1, 1, max(0.002, TOP[k]["p"]))), (f_sink + 20, (1, 1, 0.001))])
dfill = [w("b4", "one", 1), w("b4", "two"), w("b4", "five"), w("b4", "twelve") + 12, w("b4", "twelve") + 22, w("b4", "twelve") + 32]
for k in range(6):
    x = CX[k]
    K.key(dig[k], "location", [(0, (x, -0.2, ZLOW)), (f_digit - 6, (x, -0.2, ZLOW)), (f_digit + 12, (x, -0.2, PZ))])
    p = DIG[k]["p"]
    mr, liq, lm = cols[k]
    K.key(liq, "scale", [(dfill[k] - 4, (1, 1, 0.001)), (dfill[k] + 20, (1, 1, max(0.002, p)))])
    K.glow_keys(lm, [(dfill[k] - 4, 1.0), (dfill[k] + 8, 1.2 + 5.0 * (p / DIG[0]["p"]) ** 0.6)])
    K.glow_keys(dig_f[k], [(0, 0.0), (dfill[k] - 2, 0.0), (dfill[k] + 10, 0.4 + 2.6 * (p / DIG[0]["p"]) ** 0.6)])

# b5: nothing is looked up; the lid and the front window lift apart to show the stack inside
f_open = w("b5", "opens")
win, lid = MA["window"], MA["lid"]
z0, zl = win.location.z, lid.location.z
K.key(lid, "location", [(0, (0, 0, zl)), (f_open, (0, 0, zl)), (f_open + 44, (0, 0, zl + 0.55))])
K.key(win, "location", [(0, (0, win.location.y, z0)), (f_open + 6, (0, win.location.y, z0)), (f_open + 46, (0, win.location.y, z0 - 0.84))])
inner = MA["inner"].data
K.key(inner, "energy", [(0, 6.0), (f_in + 50, 6.0), (f_in + 66, 30.0), (f_out + 30, 14.0), (f_read, 14.0), (f_read + 14, 40.0),
                        (b["b3"]["f0"], 14.0), (f_open, 14.0), (f_open + 30, 45.0)])
K.glow_keys(idle, [(f_open, 1.4), (f_open + 30, 3.4)])

# ---------------------------------------------------------------- cameras
c1 = K.Cam(sc, "c_open", lens=38, fstop=3.5).cut(0)
c1.keys([(0, (2.7, -3.4, 1.65), (-0.25, 0.0, 0.6)), (b["b1"]["f1"] + 10, (2.1, -2.95, 1.38), (-0.45, 0.0, 0.55))])
c2 = K.Cam(sc, "c_strip", lens=40, fstop=2.4).cut(b["b2"]["f0"] - 8)
c2.keys([(b["b2"]["f0"] - 8, (-2.35, -1.3, 0.55), (-1.25, 0.0, 0.22)),
         (f_100 - 10, (-2.1, -1.2, 0.52), (-1.2, 0.0, 0.22)),
         (f_100 + 50, (-1.0, -1.85, 1.0), (-6.0, 0.0, 0.2)),
         (f_read - 20, (-0.9, -1.9, 1.05), (-6.5, 0.0, 0.2))])
c3 = K.Cam(sc, "c_mach", lens=40, fstop=3.2).cut(f_read - 18)
c3.keys([(f_read - 18, (1.25, -2.25, 1.0), (-0.05, 0.0, 0.55)), (b["b2"]["f1"] + 12, (1.0, -1.95, 0.92), (0.0, 0.0, 0.56))])
c4 = K.Cam(sc, "c_bars", lens=36, fstop=3.2).cut(b["b3"]["f0"] - 8)
c4.keys([(b["b3"]["f0"] - 8, (1.9, -2.45, 1.0), (1.8, 0.0, 0.38)), (b["b3"]["f1"] + 12, (1.8, -2.2, 0.92), (1.8, 0.0, 0.39))])
c5 = K.Cam(sc, "c_loop", lens=30, fstop=4.0).cut(b["b4"]["f0"] - 8)
c5.keys([(b["b4"]["f0"] - 8, (0.6, -3.0, 1.55), (-0.15, 0.0, 0.48)), (f_digit - 24, (0.3, -2.7, 1.35), (-0.35, 0.0, 0.45))])
c6 = K.Cam(sc, "c_bars2", lens=36, fstop=3.2).cut(f_digit - 22)
c6.keys([(f_digit - 22, (2.0, -2.4, 1.05), (1.8, 0.0, 0.38)), (b["b4"]["f1"] + 12, (1.85, -2.15, 0.95), (1.8, 0.0, 0.39))])
c7 = K.Cam(sc, "c_close", lens=34, fstop=3.5).cut(b["b5"]["f0"] - 8)
c7.keys([(b["b5"]["f0"] - 8, (1.1, -2.1, 0.95), (0.0, 0.0, 0.5)), (END, (2.3, -3.7, 1.55), (-0.6, 0.0, 0.45))])

pins = [f"tok{i}_front" for i in range(75, N)] + [f"tok{i}_top" for i in (80, 92, LAST)]
pins += [f"cand{k}_front" for k in range(6)] + [f"dig{k}_front" for k in range(6)] + [f"col{k}_top" for k in range(6)]
pins += [f"ans{k}_front" for k in range(4)] + ["model_pin_top", "model_pin_in", "model_pin_out", "model_pin_win"]
K.finish(sc, FILM, pins, samples=int(os.environ.get("SAMPLES", "96")))
