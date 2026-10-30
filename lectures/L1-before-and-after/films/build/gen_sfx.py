#!/usr/bin/env python3
"""ElevenLabs sound-generation for each entry of audio/sfx_spec.json -> audio/sfx/<name>.mp3 (skips existing)."""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
key = next(l.split("=", 1)[1].strip().strip('"') for l in open("/Users/raj/Claude_Brain/cobol-mainframes/.env") if l.startswith("ELEVENLABS_API_KEY="))
for s in json.load(open(os.path.join(HERE, "audio", "sfx_spec.json"))):
    out = os.path.join(HERE, "audio", "sfx", s["name"] + ".mp3")
    if os.path.exists(out) and "--force" not in sys.argv:
        continue
    body = {"text": s["prompt"], "duration_seconds": s["seconds"], "prompt_influence": 0.5}
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation", data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    data = urllib.request.urlopen(req, timeout=120).read()
    open(out, "wb").write(data)
    print(s["name"], len(data))
