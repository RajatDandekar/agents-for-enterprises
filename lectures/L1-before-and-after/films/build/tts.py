#!/usr/bin/env python3
"""Synthesize every block of script.json with ElevenLabs Daniel (with-timestamps).
Writes audio/<id>.mp3 and audio/<id>.align.json (words with start/end, from `say`).
Skips blocks whose say+settings hash is unchanged. Never prints the key."""
import base64, hashlib, json, os, sys, urllib.request, urllib.error, time
HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = "/Users/raj/Claude_Brain/cobol-mainframes/.env"
S = json.load(open(os.path.join(HERE, "script.json")))
key = next(l.split("=", 1)[1].strip().strip('"') for l in open(KEY_FILE) if l.startswith("ELEVENLABS_API_KEY="))
only = sys.argv[1:]
blocks = S["blocks"]
for i, b in enumerate(blocks):
    if only and b["id"] not in only:
        continue
    out = os.path.join(HERE, "audio", b["id"])
    sha = hashlib.sha1((S["voice_id"] + S["model"] + json.dumps(S["settings"]) + b["say"]).encode()).hexdigest()
    if os.path.exists(out + ".align.json") and json.load(open(out + ".align.json")).get("sha") == sha:
        print("keep", b["id"]); continue
    body = {"text": b["say"], "model_id": S["model"], "voice_settings": S["settings"],
            "previous_text": blocks[i-1]["say"][-300:] if i else "", "next_text": blocks[i+1]["say"][:300] if i+1 < len(blocks) else ""}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{S['voice_id']}/with-timestamps?output_format=mp3_44100_128"
    for a in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={"xi-api-key": key, "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=180)); break
        except urllib.error.HTTPError as e:
            print("http", e.code, e.read()[:300]); time.sleep(3 * (a + 1))
    else:
        sys.exit("tts failed " + b["id"])
    open(out + ".mp3", "wb").write(base64.b64decode(r["audio_base64"]))
    al = r.get("normalized_alignment") or r["alignment"]
    al = r["alignment"]
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur = [], None
    for ci, (ch, s0, e0) in enumerate(zip(chars, st, en)):
        if ch.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {"w": ch, "s": s0, "e": e0, "c": ci}
        else: cur["w"] += ch; cur["e"] = e0
    if cur: words.append(cur)
    json.dump({"sha": sha, "say": b["say"], "words": words, "chars": chars, "cs": st, "ce": en, "dur": en[-1]}, open(out + ".align.json", "w"))
    print("tts", b["id"], round(en[-1], 2), "s", len(words), "words")
