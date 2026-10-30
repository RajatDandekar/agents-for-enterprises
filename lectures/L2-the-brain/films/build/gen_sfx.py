#!/usr/bin/env python3
"""The L2 film SFX set (ElevenLabs sound generation): designed from this world's materials (ceramic tiles, glass
plates, light, meters). python3 gen_sfx.py [names...]. Writes sfx/<name>.mp3; skips existing. Key never printed."""
import json, os, sys, urllib.request, time
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = next(l.split("=", 1)[1].strip().strip('"') for l in open("/Users/raj/Claude_Brain/cobol-mainframes/.env") if l.startswith("ELEVENLABS_API_KEY="))
SET = {
 "tile": ("a single small ceramic tile set down gently on a stone table, soft precise click, clean foley, close mic, no reverb", 0.6),
 "rise": ("a thin glass plate sliding smoothly upward out of a slot, soft airy glassy swish, clean foley, no reverb", 1.0),
 "beam": ("soft shimmering light beam sweeping outward, airy crystalline whoosh, gentle and elegant, no drums", 1.6),
 "fill": ("a gentle rising glassy tone like liquid light filling a thin glass tube, soft and clean", 1.4),
 "chime": ("one soft clear glass chime, gentle, short, elegant user interface confirmation, no reverb tail", 1.0),
 "tick": ("a tiny soft digital tick, very quiet and clean, interface foley", 0.5),
 "bloom": ("deep soft cinematic swell bloom, warm low pad rising then settling, elegant title hit, no drums", 2.8),
 "merge": ("several soft airy whooshes converging into one gentle warm glowing tone, elegant, no drums", 2.2),
 "resolve": ("a calm warm resolving chord swell with a soft bell on top, gentle ending, no drums", 3.5),
 "whoosh": ("a soft smooth air whoosh for a camera move, gentle and low, clean", 0.9),
}
want = sys.argv[1:] or list(SET)
for n in want:
    out = os.path.join(HERE, "sfx", n + ".mp3")
    if os.path.exists(out):
        continue
    p, sec = SET[n]
    body = json.dumps({"text": p, "duration_seconds": sec, "prompt_influence": 0.5}).encode()
    for a in range(4):
        try:
            req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=body, method="POST",
                                         headers={"xi-api-key": KEY, "Content-Type": "application/json"})
            data = urllib.request.urlopen(req, timeout=120).read(); break
        except Exception as e:
            print("retry", n, e); time.sleep(3)
    open(out, "wb").write(data)
    print("sfx", n, len(data))
