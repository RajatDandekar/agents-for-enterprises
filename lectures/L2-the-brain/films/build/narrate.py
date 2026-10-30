#!/usr/bin/env python3
"""Narration for one Lecture 2 film: ElevenLabs Daniel with character timings, then the film's timeline.

    python3 films/build/narrate.py qkv          # synthesize changed blocks, write timeline/qkv.json
    python3 films/build/narrate.py qkv --plan   # timeline only (no API calls)

scripts/<film>.json: blocks [{id, text, say, gap?}]. text = subtitles, say = the same sentences spelled for the voice.
audio/<film>/<id>.mp3 + .align.json. timeline/<film>.json: every block's start in film seconds, every spoken word
(film seconds and frames), and one subtitle cue per sentence. Light HTTP only. The key is never printed.
"""
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = "/Users/raj/Claude_Brain/cobol-mainframes/.env"
VOICE = "onwK4e9ZLuTAKqWW03F9"  # Daniel
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.1, "use_speaker_boost": True, "speed": 1.08}
FPS = 30
LEAD = 3.2   # title card before the first word
GAP = 0.75   # silence between blocks (a block may set its own "gap")
TAIL = 4.5   # after the last word: the end card
SENT = re.compile(r"\S.*?(?:[.!?](?=\s|$)|$)\s*", re.S)


def key():
    for line in open(KEY_FILE):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("no ELEVENLABS_API_KEY")


def synth(k, text, prev, nxt):
    body = {"text": text, "model_id": MODEL, "voice_settings": SETTINGS, "previous_text": prev[-300:], "next_text": nxt[:300]}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128"
    for a in range(5):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                         headers={"xi-api-key": k, "Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            msg = e.read()[:300]
            if e.code in (429, 500, 502, 503) and a < 4:
                time.sleep(4 * (a + 1)); continue
            raise SystemExit(f"ElevenLabs {e.code}: {msg}")
        except urllib.error.URLError:
            time.sleep(4 * (a + 1))
    raise SystemExit("tts failed")


def words_of(al):
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    out, cur = [], None
    for ci, (ch, s0, e0) in enumerate(zip(chars, st, en)):
        if ch.isspace():
            if cur:
                out.append(cur); cur = None
            continue
        if cur is None:
            cur = {"w": ch, "s": s0, "e": e0, "c": ci}
        else:
            cur["w"] += ch; cur["e"] = e0
    if cur:
        out.append(cur)
    return out


def main():
    film = sys.argv[1]
    plan_only = "--plan" in sys.argv
    S = json.load(open(os.path.join(HERE, "scripts", f"{film}.json")))
    adir = os.path.join(HERE, "audio", film)
    os.makedirs(adir, exist_ok=True)
    blocks = S["blocks"]
    k = None
    for i, b in enumerate(blocks):
        sha = hashlib.sha1((VOICE + MODEL + json.dumps(SETTINGS) + b["say"]).encode()).hexdigest()
        ap = os.path.join(adir, b["id"] + ".align.json")
        if os.path.exists(ap) and json.load(open(ap)).get("sha") == sha:
            continue
        if plan_only:
            raise SystemExit(f"{b['id']} needs synthesis")
        k = k or key()
        r = synth(k, b["say"], blocks[i - 1]["say"] if i else "", blocks[i + 1]["say"] if i + 1 < len(blocks) else "")
        data = base64.b64decode(r["audio_base64"])
        open(os.path.join(adir, b["id"] + ".mp3"), "wb").write(data)
        al = r["alignment"]
        json.dump({"sha": sha, "say": b["say"], "alignment": al, "mp3_seconds": round(len(data) * 8 / 128000, 3)}, open(ap, "w"))
        print("tts", film, b["id"], round(al["character_end_times_seconds"][-1], 2), "s")
    # ---- the timeline
    t = S.get("lead", LEAD)
    tl_blocks, words, cues = [], [], []
    for b in blocks:
        A = json.load(open(os.path.join(adir, b["id"] + ".align.json")))
        al = A["alignment"]
        speech_end = al["character_end_times_seconds"][-1]
        ws = words_of(al)
        for w in ws:
            words.append({"block": b["id"], "w": w["w"], "s": round(t + w["s"], 3), "e": round(t + w["e"], 3),
                          "f0": int(round((t + w["s"]) * FPS)), "f1": int(round((t + w["e"]) * FPS))})
        # one subtitle per sentence: shown text from `text`, timing from the same sentence of `say`
        ts, ss = SENT.findall(b["text"]), SENT.findall(b["say"])
        if len(ts) != len(ss):
            raise SystemExit(f"{b['id']}: text and say need the same sentences")
        st, en = al["character_start_times_seconds"], al["character_end_times_seconds"]
        pos = 0
        for a_, s_ in zip(ts, ss):
            i0 = min(pos, len(st) - 1)
            j0 = min(pos + len(s_.rstrip()) - 1, len(en) - 1)
            cues.append({"block": b["id"], "t": round(t + st[i0], 3), "end": round(t + en[j0], 3), "text": a_.strip()})
            pos += len(s_)
        tl_blocks.append({"id": b["id"], "shot": b.get("shot"), "at": round(t, 3), "speech_end": round(t + speech_end, 3),
                          "audio": f"audio/{film}/{b['id']}.mp3", "f0": int(round(t * FPS)), "f1": int(round((t + speech_end) * FPS))})
        t += speech_end + b.get("gap", S.get("gap", GAP))
    total = t - blocks[-1].get("gap", S.get("gap", GAP)) + S.get("tail", TAIL)
    tl = {"film": film, "title": S.get("title"), "kicker": S.get("kicker"), "fps": FPS, "seconds": round(total, 3),
          "frames": int(round(total * FPS)), "blocks": tl_blocks, "words": words, "cues": cues}
    json.dump(tl, open(os.path.join(HERE, "timeline", f"{film}.json"), "w"), indent=0)
    print(f"timeline {film}: {total:.1f} s, {tl['frames']} frames, {len(words)} words, {len(cues)} cues")
    for b in tl_blocks:
        print(f"  {b['id']:4s} {b['at']:6.2f} -> {b['speech_end']:6.2f}  {b['shot']}")


if __name__ == "__main__":
    main()
