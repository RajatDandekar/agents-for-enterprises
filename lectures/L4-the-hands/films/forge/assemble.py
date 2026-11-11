#!/usr/bin/env python3
"""Turn a recorded forge film (frames/<film>/shots.json from record_modal.py) into films/hephaestus_<film>.mp4, with
narration by ElevenLabs Daniel when scripts/<film>.json has lines.

    python3 lectures/L4-the-hands/films/forge/assemble.py knob_output          # narrate (cached), assemble, encode
    python3 lectures/L4-the-hands/films/forge/assemble.py knob_output --plan   # print the timing only

scripts/<film>.json: {"lines": {shot_id: "sentence(s)"}, "hold": seconds for a shot without a line, "lapse": seconds per
frame while the questions run}. Each shot lasts as long as its line plus a breath, at least as long as its frames need.
Motion frames (scrolls, the cursor) play at 30 fps; a "run" or "wait" shot is a time-lapse; the last frame of a shot
holds. Voice: ElevenLabs Daniel (onwK4e9ZLuTAKqWW03F9), eleven_multilingual_v2, speed 1.08, as the narrated films; the key
is read from /Users/raj/Claude_Brain/cobol-mainframes/.env and never printed. Output: 1920x1080, 30 fps, H.264, AAC,
-16 LUFS, faststart. Needs ffmpeg with libx264.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
L4 = HERE.parents[1]
KEY_FILE = "/Users/raj/Claude_Brain/cobol-mainframes/.env"
VOICE = "onwK4e9ZLuTAKqWW03F9"
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.1, "use_speaker_boost": True, "speed": 1.08}
FPS = 30
LEAD, BREATH = 0.35, 0.7  # silence before a line starts in its shot; after it ends


def key():
    for line in open(KEY_FILE):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("no ELEVENLABS_API_KEY")


def tts(text, dst, prev="", nxt=""):
    body = {"text": text, "model_id": MODEL, "voice_settings": SETTINGS, "previous_text": prev[-300:], "next_text": nxt[:300]}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128"
    k = key()
    for a in range(5):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                         headers={"xi-api-key": k, "Content-Type": "application/json"})
            dst.write_bytes(urllib.request.urlopen(req, timeout=180).read())
            return
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and a < 4:
                time.sleep(4 * (a + 1))
                continue
            raise SystemExit(f"ElevenLabs {e.code}: {e.read()[:200]!r}")
        except urllib.error.URLError:
            time.sleep(4 * (a + 1))
    raise SystemExit("tts failed")


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout.strip())


def main(film, plan=False):
    fr = HERE / "frames" / film
    shots = json.loads((fr / "shots.json").read_text())["shots"]
    sp = HERE / "scripts" / f"{film}.json"
    script = json.loads(sp.read_text()) if sp.exists() else {}
    lines, hold, lapse = script.get("lines", {}), script.get("hold", 2.5), script.get("lapse", 0.22)
    adir = HERE / "audio" / film
    adir.mkdir(parents=True, exist_ok=True)
    ids = [s["id"] for s in shots]
    unknown = set(lines) - set(ids)
    assert not unknown, f"lines for shots that were not recorded: {unknown}"
    audio = {}
    for i, s in enumerate(shots):
        t = lines.get(s["id"])
        if not t:
            continue
        h = hashlib.sha1(json.dumps([t, SETTINGS, VOICE]).encode()).hexdigest()[:10]
        p = adir / f"{s['id']}_{h}.mp3"
        if not p.exists() and not plan:
            prev = " ".join(lines.get(x, "") for x in ids[:i])
            nxt = " ".join(lines.get(x, "") for x in ids[i + 1:])
            tts(t, p, prev, nxt)
            print("narrated", s["id"])
        audio[s["id"]] = (p, dur(p) if p.exists() else len(t.split()) / 2.7)
    # timing: every frame gets a duration; the last frame of each shot takes what the line still needs
    concat, track, t0 = [], [], 0.0
    for s in shots:
        fs = s["frames"]
        lapse_shot = s["id"] in ("run", "wait")
        ds = [max(d, lapse if lapse_shot else 1 / FPS) for _, d in fs]
        ds[-1] = max(ds[-1], hold if s["id"] not in audio else 0.5)
        need = (LEAD + audio[s["id"]][1] + BREATH) if s["id"] in audio else 0
        if sum(ds) < need:
            ds[-1] += need - sum(ds)
        for (f, _), d in zip(fs, ds):
            concat.append((fr / f, round(d * FPS) / FPS or 1 / FPS))
        if s["id"] in audio:
            track.append((audio[s["id"]][0], t0 + LEAD))
        print(f"{s['id']:<10} {t0:6.1f}s  {sum(ds):5.1f}s  {len(fs):3d} frames  {'line ' + format(audio[s['id']][1], '.1f') + 's' if s['id'] in audio else ''}")
        t0 += sum(d for _, d in concat[-len(fs):])
    print(f"total {t0:.1f}s")
    if plan:
        return
    seq = fr / "seq"  # every output frame as a numbered link to its screenshot: exact timing at 30 fps
    if seq.exists():
        for x in seq.iterdir():
            x.unlink()
    seq.mkdir(exist_ok=True)
    n = 0
    for p, d in concat:
        for _ in range(max(1, round(d * FPS))):
            n += 1
            (seq / f"{n:05d}.jpg").symlink_to(p)
    t0 = n / FPS
    silent = fr / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(seq / "%05d.jpg"),
                    "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "16", "-tune", "stillimage", "-r", str(FPS), "-movflags", "+faststart", str(silent)], check=True)
    out = L4 / "films" / f"hephaestus_{film}.mp4"
    if not track:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    else:
        args = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent)]
        for p, _ in track:
            args += ["-i", str(p)]
        fl = "".join(f"[{i + 1}:a]adelay={int(at * 1000)}:all=1[a{i}];" for i, (_, at) in enumerate(track))
        fl += "".join(f"[a{i}]" for i in range(len(track))) + f"amix=inputs={len(track)}:normalize=0:dropout_transition=0,apad,atrim=0:{t0:.3f},loudnorm=I=-16:TP=-1.5:LRA=11[a]"
        args += ["-filter_complex", fl, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                 "-movflags", "+faststart", str(out)]
        subprocess.run(args, check=True)
    print("wrote", out.relative_to(L4.parents[1]), f"{out.stat().st_size / 1e6:.1f} MB", f"{dur(out):.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], "--plan" in sys.argv)
