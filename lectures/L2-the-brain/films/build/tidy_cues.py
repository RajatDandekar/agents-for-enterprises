#!/usr/bin/env python3
"""Subtitle tidy for a film's timeline (run after narrate.py): overlay.py shows a cue from its start to ~0.45 s after
its end, so sentences spoken less than ~0.55 s apart would sit on screen together. Short neighbours in the same block
are merged into one line (when both are short and the result stays under 72 characters); otherwise the earlier cue ends 0.5 s before the
next one starts. Only the cues change; the words and blocks (all the visual timing) are untouched.

    python3 films/build/tidy_cues.py next_token
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
film = sys.argv[1]
p = os.path.join(HERE, "timeline", f"{film}.json")
tl = json.load(open(p))
out = []
for c in tl["cues"]:
    if out and out[-1]["block"] == c["block"] and c["t"] - out[-1]["end"] < 0.55:
        prev = out[-1]
        if len(prev["text"]) <= 45 and len(c["text"]) <= 45 and len(prev["text"]) + 1 + len(c["text"]) <= 72:
            prev["text"] = prev["text"] + " " + c["text"]
            prev["end"] = c["end"]
            continue
    if out and c["t"] - out[-1]["end"] < 0.55:
        out[-1]["end"] = round(min(out[-1]["end"], c["t"] - 0.5), 3)
    out.append(dict(c))
tl["cues"] = out
json.dump(tl, open(p, "w"), indent=0)
print(film, "cues:", len(out))
for c in out:
    print(f"  {c['t']:7.2f} {c['end']:7.2f}  {c['text']}")
