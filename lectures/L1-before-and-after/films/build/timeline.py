#!/usr/bin/env python3
"""Master timeline: places each narration block, converts word times to global frames
(after the ffmpeg atempo factor), and cuts the film into shots. Writes timeline.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, TEMPO = 30, 1.08
LEAD = 2.6          # title plays over the first shot before the voice starts
GAP = 0.55          # silence between blocks
END_HOLD = 1.0      # after the last word, before the end card
END_CARD = 5.0
XF = 10             # crossfade frames between shots (plates render XF extra each side)
S = json.load(open(os.path.join(HERE, "script.json")))
blocks, words, t = [], [], LEAD
for b in S["blocks"]:
    al = json.load(open(os.path.join(HERE, "audio", b["id"] + ".align.json")))
    dur = al["dur"] / TEMPO
    blocks.append({"id": b["id"], "shot": b["shot"], "t0": round(t, 3), "t1": round(t + dur, 3),
                   "f0": round(t * FPS), "f1": round((t + dur) * FPS), "text": b["text"]})
    for w in al["words"]:
        words.append({"block": b["id"], "w": w["w"], "f0": round((t + w["s"] / TEMPO) * FPS),
                      "f1": round((t + w["e"] / TEMPO) * FPS)})
    t += dur + GAP
total_t = blocks[-1]["t1"] + END_HOLD + END_CARD
TOTAL = round(total_t * FPS)
shots = []
for i, b in enumerate(blocks):
    g0 = 0 if i == 0 else round((b["t0"] - 0.35) * FPS)
    g1 = TOTAL if i == len(blocks) - 1 else round((blocks[i + 1]["t0"] - 0.35) * FPS)
    shots.append({"shot": b["shot"], "block": b["id"], "g0": g0, "g1": g1,
                  "r0": g0 - (0 if i == 0 else XF), "r1": g1 + (0 if i == len(blocks) - 1 else XF)})
for s in shots:
    s["frames"] = s["r1"] - s["r0"]
out = {"fps": FPS, "tempo": TEMPO, "xf": XF, "total": TOTAL, "seconds": round(TOTAL / FPS, 2),
       "end_card_f0": round((blocks[-1]["t1"] + END_HOLD) * FPS), "blocks": blocks, "shots": shots, "words": words}
json.dump(out, open(os.path.join(HERE, "timeline.json"), "w"), indent=0)
print("total", out["seconds"], "s", TOTAL, "frames")
for s in shots:
    print(f'{s["shot"]:8s} g{s["g0"]:5d}-{s["g1"]:5d} render {s["frames"]} frames')
