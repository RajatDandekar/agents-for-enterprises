"""Composite, mix and deliver the L1 film on Modal (nothing heavy on the laptop).

  modal run m_comp.py::stills --frames 460,1041,1496      # composited JPEG checks
  modal run m_comp.py::video  --chunks 24                  # all frames -> segments -> video.mp4
  modal run m_comp.py::audio                               # narration + music + SFX -> mix.wav
  modal run m_comp.py::deliver                             # mux, faststart mp4, webm, poster, grabs
"""
import json
import os
import subprocess

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
FILMS = os.path.dirname(HERE)
VOL = "/vol/l1"
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("pillow==11.0.0", "numpy==2.1.3")
    .add_local_dir(os.path.join(HERE, "fonts"), "/root/build/fonts")
    .add_local_dir(os.path.join(HERE, "audio"), "/root/build/audio")
    .add_local_file(os.path.join(HERE, "comp.py"), "/root/build/comp.py")
    .add_local_file(os.path.join(HERE, "overlays.py"), "/root/build/overlays.py")
    .add_local_file(os.path.join(HERE, "timeline.json"), "/root/build/timeline.json")
    .add_local_file(os.path.join(HERE, "script.json"), "/root/build/script.json")
    .add_local_file(os.path.join(FILMS, "music", "observatory_out_to_the_world.mp3"), "/root/music.mp3")
)
vol = modal.Volume.from_name("l1film", create_if_missing=True)
app = modal.App("l1film-comp")


def _setup():
    import sys
    sys.path.insert(0, "/root/build")
    import comp
    import overlays
    tl = overlays.TL("/root/build/timeline.json")
    script = json.load(open("/root/build/script.json"))
    E = overlays.build(tl, script)
    proj = {}
    for s in tl.shots:
        p = f"{VOL}/blend/proj/{s['shot']}.json"
        if os.path.exists(p):
            proj[s["shot"]] = json.load(open(p))
    ctx = {"proj": proj, "r0": {s["shot"]: s["r0"] for s in tl.shots}}
    return comp, tl, E, ctx


def _plate_fn(tl):
    from PIL import Image
    xf = 5
    shots = tl.shots
    cache = {}

    def load(shot, local):
        s = next(x for x in shots if x["shot"] == shot)
        local = max(0, min(s["frames"] - 1, local))
        p = f"{VOL}/frames/{shot}/f_{local:04d}.png"
        if p not in cache:
            if len(cache) > 6:
                cache.clear()
            cache[p] = Image.open(p).convert("RGBA") if os.path.exists(p) else Image.new("RGBA", (1920, 1080), (20, 22, 26, 255))
        return cache[p].copy()

    def plate(g):
        for i, s in enumerate(shots):
            if s["g0"] <= g < s["g1"] or (i == len(shots) - 1 and g >= s["g0"]):
                break
        cur = load(s["shot"], g - s["r0"])
        # dissolve across each cut: [cut - xf, cut + xf)
        if i + 1 < len(shots) and g >= s["g1"] - xf:
            n = shots[i + 1]
            a = (g - (s["g1"] - xf)) / (2 * xf)
            return Image.blend(cur, load(n["shot"], g - n["r0"]), max(0.0, min(1.0, a)))
        if i > 0 and g < s["g0"] + xf:
            p = shots[i - 1]
            a = (g - (s["g0"] - xf)) / (2 * xf)
            return Image.blend(load(p["shot"], g - p["r0"]), cur, max(0.0, min(1.0, a)))
        return cur
    return plate


@app.function(image=image, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=3600)
def comp_chunk(a: int, b: int, tag: str = "v1") -> str:
    comp, tl, E, ctx = _setup()
    plate = _plate_fn(tl)
    os.makedirs(f"{VOL}/seg/{tag}", exist_ok=True)
    out = f"{VOL}/seg/{tag}/s_{a:05d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                          "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                          "-g", "60", "-bf", "2", out], stdin=subprocess.PIPE)
    for g in range(a, b):
        im = comp.compose(g, plate, E, ctx).convert("RGB")
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    vol.commit()
    return out


@app.function(image=image, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=1800)
def comp_stills(frames: list) -> list:
    import io
    comp, tl, E, ctx = _setup()
    plate = _plate_fn(tl)
    out = []
    for g in frames:
        im = comp.compose(g, plate, E, ctx).convert("RGB")
        b = io.BytesIO()
        im.save(b, "JPEG", quality=88)
        out.append(b.getvalue())
    return out


@app.function(image=image, volumes={"/vol": vol}, cpu=4, timeout=1800)
def concat(tag: str = "v1") -> str:
    vol.reload()
    segs = sorted(os.listdir(f"{VOL}/seg/{tag}"))
    lst = f"/tmp/list.txt"
    open(lst, "w").write("".join(f"file '{VOL}/seg/{tag}/{s}'\n" for s in segs))
    out = f"{VOL}/out/video_{tag}.mp4"
    os.makedirs(f"{VOL}/out", exist_ok=True)
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                       capture_output=True, text=True)
    vol.commit()
    return f"{out} rc={p.returncode} {p.stderr[-300:]} segs={len(segs)}"


# ------------------------------------------------------------------ audio
SR = 48000


def _decode(path):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def _rms(x):
    import numpy as np
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)


def sfx_cues(tl):
    W = tl.w
    xf = tl.t["xf"]
    C = [("bloom", 0, 0.45), ("type", 14, 0.18)]
    for s in tl.shots[1:]:
        C.append(("air", s["g0"] - 14, 0.28))
    ft, fs, fa = W("n01", "types"), W("n01", "have") + 8, W("n01", "answer") - 6
    C += [("type", ft, 0.3), ("send", fs, 0.4), ("reply", fa, 0.35)]
    fr, fm, fd, ff = W("n02", "rules"), W("n02", "message"), W("n02", "description"), W("n02", "fifteen")
    C += [("sheet", fr + 6, 0.55), ("sheet", fm + 6, 0.55)]
    for i in range(15):
        if i % 3 == 0:
            C.append(("sheet", fd + int(i * (ff + 12 - fd) / 15) + 6, 0.35))
    C += [("clamp", W("n02", "stacked") + 6, 0.5), ("pick", W("n02", "two"), 0.35)]
    C += [("hum", W("n03", "reads") - 4, 0.4), ("pick", W("n03", "fifteen") + 4, 0.45), ("type", W("n03", "json") - 14, 0.15)]
    C += [("scan", W("n04", "checks") - 2, 0.35), ("ok", W("n04", "types") + 8, 0.3), ("plug", W("n04", "plug") + 2, 0.5),
          ("slide", W("n04", "toolbox") - 2, 0.45)]
    C += [("hdd", W("n05", "calls") + 8, 0.45), ("hdd", W("n05", "in") + 4, 0.35)]
    sl = tl.shot("loop")
    for f in (W("n06", "manuals") - 30, W("n06", "stock") - 30, W("n06", "grows") + 10):
        C += [("slide", f + 34, 0.3)]
    C += [("pick", W("n06", "six"), 0.35)]
    C += [("slide", W("n07", "direct") - 4, 0.45), ("refuse", W("n07", "no") + 2, 0.5), ("pick", W("n07", "fifty"), 0.3)]
    fy = W("n08", "yes")
    C += [("reply", W("n08", "preview") - 10, 0.35), ("pick", W("n08", "two"), 0.3), ("type", fy - 30, 0.25), ("send", fy, 0.4)]
    C += [("hdd", W("n09", "saves") - 4, 0.3), ("paper", W("n09", "lands"), 0.6), ("pick", W("n09", "request", 1), 0.3)]
    C += [("print", W("n10", "reads") - 4, 0.4), ("ok", W("n10", "waiting"), 0.3)]
    C += [("bloom", W("n11", "one") - 6, 0.3)]
    for w in ("harness", "model", "guard", "m", "ledgerline"):
        C.append(("pick", W("n11", w) - 4, 0.18))
    C.append(("bell", tl.t["end_card_f0"], 0.5))
    return C


@app.function(image=image, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=1800)
def mix(tag: str = "v1", music_under_db: float = -15.0, music_gap_db: float = -7.0) -> str:
    import sys
    import numpy as np
    sys.path.insert(0, "/root/build")
    import overlays
    tl = overlays.TL("/root/build/timeline.json")
    fps, tempo = tl.t["fps"], tl.t["tempo"]
    N = int(tl.t["total"] / fps * SR) + SR
    voice = np.zeros((N, 2), np.float32)
    for b in tl.t["blocks"]:
        tmp = f"/tmp/{b['id']}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"/root/build/audio/{b['id']}.mp3",
                        "-af", f"atempo={tempo}", "-ar", str(SR), "-ac", "2", tmp])
        x = _decode(tmp)
        a = int(b["t0"] * SR)
        voice[a:a + len(x)] += x[:N - a]
    sp = voice[np.abs(voice).max(1) > 1e-4]
    v_rms = _rms(sp)
    # speech windows from the word timings (merge gaps < 24 frames)
    spans = []
    for w in tl.t["words"]:
        a, e = w["f0"], w["f1"]
        if spans and a - spans[-1][1] < 24:
            spans[-1][1] = max(spans[-1][1], e)
        else:
            spans.append([a, e])
    gain_f = np.full(tl.t["total"] + 60, 10 ** (music_gap_db / 20))
    under = 10 ** (music_under_db / 20)
    for a, e in spans:
        gain_f[max(0, a - 8):e + 10] = under
    # smooth the envelope over ~14 frames
    k = np.ones(14) / 14
    gain_f = np.convolve(gain_f, k, mode="same")
    music = _decode("/root/music.mp3")
    music = music[:N] if len(music) >= N else np.pad(music, ((0, N - len(music)), (0, 0)))
    m_rms = _rms(music[: int(60 * SR)])
    music *= v_rms / m_rms
    t = np.arange(N) / SR
    g = np.interp(t * fps, np.arange(len(gain_f)), gain_f)
    fade_in = np.clip(t / 1.5, 0, 1)
    end_t = tl.t["total"] / fps
    fade_out = np.clip((end_t - t) / 2.5, 0, 1)
    music *= (g * fade_in * fade_out)[:, None].astype(np.float32)
    sfx = np.zeros((N, 2), np.float32)
    bank = {}
    for name, f, v in sfx_cues(tl):
        if name not in bank:
            x = _decode(f"/root/build/audio/sfx/{name}.mp3")
            bank[name] = x * (10 ** (-20 / 20) / _rms(x[np.abs(x).max(1) > 1e-3] if (np.abs(x).max(1) > 1e-3).any() else x))
        x = bank[name] * (v_rms / 10 ** (-20 / 20)) * v
        a = int(max(0, f) / fps * SR)
        n = min(len(x), N - a)
        sfx[a:a + n] += x[:n]
    out = voice + music + sfx
    out = out[: int(end_t * SR)]
    peak = np.abs(out).max()
    if peak > 0.98:
        out *= 0.98 / peak
    os.makedirs(f"{VOL}/out", exist_ok=True)
    raw = f"/tmp/mix_raw.wav"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw],
                         stdin=subprocess.PIPE)
    p.stdin.write(out.astype(np.float32).tobytes())
    p.stdin.close()
    p.wait()
    # two-pass loudnorm to -14 LUFS, TP -1.5
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    final = f"{VOL}/out/mix_{tag}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
                    f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,"
                    f"aformat=channel_layouts=stereo", "-ar", str(SR), final])
    vol.commit()
    return f"{final} speech_rms={20*np.log10(v_rms):.1f}dB spans={len(spans)}"


@app.function(image=image, volumes={"/vol": vol}, cpu=8, memory=8192, timeout=3600)
def deliver(tag: str = "v1", grabs: list = None) -> dict:
    vol.reload()
    v, a = f"{VOL}/out/video_{tag}.mp4", f"{VOL}/out/mix_{tag}.wav"
    mp4, webm = f"{VOL}/out/l1_how_it_works_{tag}.mp4", f"{VOL}/out/l1_how_it_works_{tag}.webm"
    r1 = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", a, "-map", "0:v", "-map", "1:a",
                         "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "1.15M", "-bufsize", "2.3M",
                         "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                         "-shortest", mp4], capture_output=True, text=True)
    r2 = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c:v", "libvpx-vp9", "-b:v", "0.95M", "-row-mt", "1",
                         "-deadline", "good", "-cpu-used", "2", "-c:a", "libopus", "-b:a", "128k", webm], capture_output=True, text=True)
    info = {"mp4": mp4, "webm": webm, "rc": [r1.returncode, r2.returncode], "err": (r1.stderr + r2.stderr)[-500:]}
    for f in (mp4, webm):
        info[os.path.basename(f)] = os.path.getsize(f) if os.path.exists(f) else 0
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True)
    info["duration"] = pr.stdout.strip()
    lo = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    info["ebur128"] = lo[lo.rfind("Summary"):][:400]
    vol.commit()
    return info


@app.function(image=image, volumes={"/vol": vol}, cpu=2, timeout=900)
def fetch(path: str) -> bytes:
    vol.reload()
    return open(path, "rb").read()


@app.function(image=image, volumes={"/vol": vol}, cpu=4, timeout=900)
def grab(path: str, secs: list, width: int = 960) -> list:
    vol.reload()
    out = []
    for s in secs:
        p = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(s), "-i", path, "-frames:v", "1", "-vf", f"scale={width}:-2",
                            "-q:v", "3", "-f", "image2", "-c:v", "mjpeg", "-"], capture_output=True)
        out.append(p.stdout)
    return out


@app.function(image=image, volumes={"/vol": vol}, cpu=2, timeout=900)
def levels(path: str, windows: list) -> list:
    vol.reload()
    res = []
    for a, b in windows:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(a), "-t", str(b - a), "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        mv = [l.split(":")[1].strip() for l in r.splitlines() if "mean_volume" in l]
        res.append((a, b, mv[0] if mv else "?"))
    return res


def _save(name, data):
    d = os.path.join(HERE, "out")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    open(p, "wb").write(data)
    return p


@app.local_entrypoint()
def stills(frames: str = "460", tag: str = "chk"):
    fr = [int(f) for f in frames.split(",")]
    for f, b in zip(fr, comp_stills.remote(fr)):
        print(_save(f"{tag}_{f:05d}.jpg", b))


@app.local_entrypoint()
def video(chunks: int = 24, tag: str = "v1"):
    tl = json.load(open(os.path.join(HERE, "timeline.json")))
    T = tl["total"]
    step = -(-T // chunks)
    jobs = [(a, min(T, a + step), tag) for a in range(0, T, step)]
    for r in comp_chunk.starmap(jobs):
        pass
    print(concat.remote(tag))


@app.local_entrypoint()
def audio(tag: str = "v1"):
    print(mix.remote(tag))


@app.local_entrypoint()
def final(tag: str = "v1", grab_secs: str = ""):
    info = deliver.remote(tag)
    print(json.dumps(info, indent=1))


@app.local_entrypoint()
def lv(path: str = "/vol/l1/out/mix_v1.wav", windows: str = "0:2.5,5:9,40:44,118:121,160:164.7"):
    w = [tuple(float(x) for x in p.split(":")) for p in windows.split(",")]
    for r in levels.remote(path, w):
        print(r)


@app.local_entrypoint()
def grabs(tag: str = "v1", secs: str = "1.5,12,22,30,36,45,52,58,64,71,80,86,94,100,105,112,118,124,128,134,140,146,150,156,162"):
    ss = [float(s) for s in secs.split(",")]
    d = os.path.join(HERE, "out", f"grabs_{tag}")
    os.makedirs(d, exist_ok=True)
    for s, b in zip(ss, grab.remote(f"{VOL}/out/l1_how_it_works_{tag}.mp4", ss)):
        open(os.path.join(d, f"g_{s:06.1f}.jpg"), "wb").write(b)
    print("grabs ->", d)


@app.local_entrypoint()
def pull(tag: str = "v1", poster_sec: float = 154.0):
    films = FILMS
    open(os.path.join(films, "poster.jpg"), "wb").write(grab.remote(f"{VOL}/out/l1_how_it_works_{tag}.mp4", [poster_sec], 1920)[0])
    for ext in ("mp4", "webm"):
        open(os.path.join(films, f"l1_how_it_works.{ext}"), "wb").write(fetch.remote(f"{VOL}/out/l1_how_it_works_{tag}.{ext}"))
        print("saved", ext)


@app.local_entrypoint()
def poster(tag: str = "v2", sec: float = 159.4):
    open(os.path.join(FILMS, "poster.jpg"), "wb").write(grab.remote(f"{VOL}/out/l1_how_it_works_{tag}.mp4", [sec], 1920)[0])
