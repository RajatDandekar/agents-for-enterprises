"""Lecture 2 films on Modal (workspace rajatworkspace, volume video-ad-edit:/l2films). Nothing heavy runs on the laptop.

  test     build scenes/<film>.py inside Blender, render a few stills on GPU, save a contact sheet + JPEG stills locally
  full     build + render every frame in parallel chunks (L40S, Cycles OptiX) -> plates/<film>.mp4 on the volume
  comp     overlays (build/overlay.py, 2D text pinned to the 3D) + narration + music + SFX -> out/<film>.mp4/.webm/.jpg,
           downloaded to films/
  sheet    contact sheet of frames sampled from the composited film (QA)

  MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/modal_films.py::test --film qkv --frames 300,900,1700
  MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/modal_films.py::full --film qkv
  MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/modal_films.py::comp --film qkv
"""
import json
import os
import pathlib

import modal

BUILD = os.path.dirname(os.path.abspath(__file__))
FILMS = os.path.dirname(BUILD)
L2 = os.path.dirname(FILMS)
BLENDER_URL = "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"
VOL = "/vol/l2films"
GPU = os.environ.get("L2_GPU", "L40S")
FONT_CSS = "https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@300;400;500;600;700&family=Google+Sans+Code:wght@400;500&display=swap"


def _add_sources(img):
    return (img.add_local_dir(BUILD, "/root/L2/films/build", ignore=["audio/**", "sheets/**", "__pycache__/**", "*.blend", "out/**"])
            .add_local_file(os.path.join(FILMS, "qkv_data.json"), "/root/L2/films/qkv_data.json")
            .add_local_file(os.path.join(L2, "brain3d", "trace.json"), "/root/L2/brain3d/trace.json")
            .add_local_dir(os.path.join(L2, "experiments", "logs"), "/root/L2/experiments/logs"))


blender_image = _add_sources(
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "ffmpeg", "libx11-6", "libxi6", "libxxf86vm1", "libxfixes3", "libxrender1",
                 "libgl1", "libxkbcommon0", "libsm6", "libice6", "libegl1")
    .run_commands(f"wget -q {BLENDER_URL} -O /tmp/b.tar.xz",
                  "mkdir -p /opt/blender && tar xf /tmp/b.tar.xz -C /opt/blender --strip-components=1 && rm /tmp/b.tar.xz")
    .env({"FILMS_BUILD": "/root/L2/films/build"}))

comp_image = _add_sources(
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "curl", "fonts-dejavu-core")
    .pip_install("pillow==10.4.0", "numpy<2.1")
    .add_local_file(os.path.join(BUILD, "fetch_fonts.py"), "/tmp/ff.py", copy=True)
    .run_commands("python3 /tmp/ff.py && ls /fonts"))

vol = modal.Volume.from_name("video-ad-edit", create_if_missing=True)
app = modal.App("l2-films")

GPU_SETUP = """
import bpy, os
prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind
        prefs.get_devices()
        if any(d.type == kind for d in prefs.devices):
            break
    except TypeError:
        continue
for d in prefs.devices:
    d.use = d.type != "CPU"
sc = bpy.context.scene
sc.cycles.device = "GPU"
sc.cycles.samples = int(os.environ.get("SAMPLES", "96"))
sc.render.resolution_percentage = int(os.environ.get("RES_PCT", "100"))
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
try:
    sc.cycles.denoising_use_gpu = True
except Exception:
    pass
"""


def _sh(cmd, env=None):
    import subprocess
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd[:6]))}\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    return p


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=8, memory=32768, timeout=3600)
def build(film: str, proj: bool = True) -> dict:
    import subprocess
    import time
    t0 = time.time()
    vol.reload()
    os.makedirs(f"{VOL}/blend/proj", exist_ok=True)
    env = dict(os.environ, OUTDIR=f"{VOL}/blend")
    if not proj:
        env["NO_PROJ"] = "1"
    p = subprocess.run(["/opt/blender/blender", "-b", "--factory-startup", "--python-use-system-env", "-P",
                        f"/root/L2/films/build/scenes/{film}.py"], capture_output=True, text=True, env=env)
    saved = [l for l in p.stdout.splitlines() if l.startswith("SAVED")]
    if p.returncode or not saved:
        raise RuntimeError(f"build {film} failed rc={p.returncode}\n{p.stdout[-5000:]}\n{p.stderr[-3000:]}")
    vol.commit()
    _, path, frames = saved[-1].split()
    frames = int(frames)
    if proj:  # the pins' 2D positions, every 2nd frame, in 8 parallel Blender processes
        step, n = 2, 8
        cuts = [frames * k // n for k in range(n + 1)]
        cuts = [c - c % step for c in cuts[:-1]] + [frames]
        procs = []
        for k in range(n):
            e2 = dict(os.environ, PINS=f"{VOL}/blend/proj/{film}.pins.json", F0=str(cuts[k]), F1=str(cuts[k + 1]),
                      STEP=str(step), OUT=f"/tmp/proj_{k}.json")
            procs.append(subprocess.Popen(["/opt/blender/blender", "-b", path, "--python-use-system-env", "-P",
                                           "/root/L2/films/build/kit/proj_worker.py"], env=e2,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for pr in procs:
            pr.wait()
        merged = {"step": step, "frames": frames, "sampled": [], "cams": [], "pins": {}}
        for k in range(n):
            d = json.load(open(f"/tmp/proj_{k}.json"))
            merged["sampled"] += d["frames"]
            merged["cams"] += d["cams"]
            for nm, arr in d["pins"].items():
                merged["pins"].setdefault(nm, []).extend(arr)
        json.dump(merged, open(f"{VOL}/blend/proj/{film}.json", "w"), separators=(",", ":"))
        vol.commit()
    return {"film": film, "frames": frames, "seconds": round(time.time() - t0),
            "notes": [l for l in p.stdout.splitlines() if l.startswith("NOTE")]}


def _render(film, start, end, samples, res_pct, outdir):
    import subprocess
    pathlib.Path("/tmp/gpu.py").write_text(GPU_SETUP)
    env = dict(os.environ, SAMPLES=str(samples), RES_PCT=str(res_pct))
    p = subprocess.run(["/opt/blender/blender", "-b", f"{VOL}/blend/{film}.blend", "-P", "/tmp/gpu.py",
                        "-o", f"{outdir}/f_####", "-F", "PNG", "-s", str(start), "-e", str(end), "-a"],
                       env=env, capture_output=True, text=True)
    tail = "\n".join(l for l in p.stdout.splitlines() if "Time:" in l or "Error" in l)[-600:]
    return p.returncode, tail + p.stderr[-600:]


@app.function(image=blender_image, gpu=GPU, volumes={"/vol": vol}, cpu=8, memory=32768, timeout=7200, retries=1)
def render_stills(film: str, frames: list, samples: int, res_pct: int) -> dict:
    import time
    vol.reload()
    outdir = f"{VOL}/stills/{film}"
    os.makedirs(outdir, exist_ok=True)
    times, errs = [], []
    for fr in frames:
        t = time.time()
        rc, log = _render(film, fr, fr, samples, res_pct, outdir)
        times.append(round(time.time() - t, 1))
        if rc:
            errs.append(log)
    vol.commit()
    return {"sec": times, "errors": errs}


@app.function(image=blender_image, gpu=GPU, volumes={"/vol": vol}, cpu=8, memory=32768, timeout=7200, retries=2,
              max_containers=40)
def render_chunk(film: str, start: int, end: int, samples: int, res_pct: int = 100) -> str:
    import time
    vol.reload()
    tmp = f"/tmp/fr_{film}_{start}"
    os.makedirs(tmp, exist_ok=True)
    t = time.time()
    rc, log = _render(film, start, end, samples, res_pct, tmp)
    if rc:
        raise RuntimeError(f"render {film} {start}-{end} rc={rc}\n{log}")
    d = f"{VOL}/chunks/{film}"
    os.makedirs(d, exist_ok=True)
    out = f"{d}/c_{start:05d}.mp4"
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-start_number", str(start), "-i", f"{tmp}/f_%04d.png",
         "-c:v", "libx264", "-preset", "slow", "-crf", "11", "-pix_fmt", "yuv420p", "-x264-params", "keyint=30", out])
    vol.commit()
    return f"{out} {round((time.time() - t) / (end - start + 1), 1)}s/f"


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=1800)
def concat(film: str, starts: list) -> str:
    vol.reload()
    with open("/tmp/l.txt", "w") as fh:
        fh.writelines(f"file '{VOL}/chunks/{film}/c_{s:05d}.mp4'\n" for s in sorted(starts))
    os.makedirs(f"{VOL}/plates", exist_ok=True)
    out = f"{VOL}/plates/{film}.mp4"
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/l.txt", "-c", "copy", out])
    vol.commit()
    return out


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=4, timeout=900)
def sheet(film: str, frames: list, src: str = "stills", cols: int = 3, width: int = 800) -> bytes:
    import subprocess
    vol.reload()
    files = []
    if src == "stills":
        files = [(fr, f"{VOL}/stills/{film}/f_{fr:04d}.png") for fr in frames if os.path.exists(f"{VOL}/stills/{film}/f_{fr:04d}.png")]
    else:
        path = {"plate": f"{VOL}/plates/{film}.mp4", "out": f"{VOL}/out/{film}.mp4"}[src]
        for fr in frames:
            o = f"/tmp/p_{fr}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{fr / 30:.3f}", "-i", path, "-frames:v", "1", o])
            if os.path.exists(o):
                files.append((fr, o))
    if not files:
        return b""
    h = width * 9 // 16
    args, filt = [], ""
    for i, (fr, pth) in enumerate(files):
        args += ["-i", pth]
        filt += f"[{i}]scale={width}:{h},drawtext=text='{fr}':x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6[s{i}];"
    n = len(files)
    cols = min(cols, n)
    layout = "|".join(f"{(i % cols) * width}_{(i // cols) * h}" for i in range(n))
    filt += "".join(f"[s{i}]" for i in range(n)) + f"xstack=inputs={n}:layout={layout}:fill=gray"
    if n == 1:
        filt = f"[0]scale={width}:{h}"
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-filter_complex", filt, "-frames:v", "1", "-q:v", "3",
                        "-f", "image2", "-c:v", "mjpeg", "-"], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[-800:])
    return p.stdout


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=2, timeout=600)
def fetch(paths: list) -> list:
    vol.reload()
    return [open(p, "rb").read() if os.path.exists(p) else b"" for p in paths]


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=4, timeout=600)
def jpgs(film: str, frames: list, width: int = 1920) -> list:
    """Full-size JPEGs of rendered stills (for looking closely)."""
    vol.reload()
    out = []
    for fr in frames:
        src = f"{VOL}/stills/{film}/f_{fr:04d}.png"
        o = f"/tmp/s_{fr}.jpg"
        if os.path.exists(src):
            _sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", f"scale={width}:-2", "-q:v", "3", o])
            out.append(open(o, "rb").read())
        else:
            out.append(b"")
    return out


def _save(data: bytes, name: str) -> str:
    d = os.path.join(BUILD, "sheets")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    open(path, "wb").write(data)
    return path


@app.local_entrypoint()
def test(film: str = "qkv", frames: str = "0,300,900", samples: int = 64, res_pct: int = 50, nobuild: bool = False,
         full_jpg: bool = True, proj: bool = False):
    if not nobuild:
        info = build.remote(film, proj)
        print("built", info)
        nfr = info["frames"]
    else:
        nfr = 10 ** 6
    fr = [min(int(x), nfr - 1) for x in frames.split(",")]
    groups = [fr[i::4] for i in range(min(4, len(fr)))]
    for r in render_stills.starmap([(film, g, samples, res_pct) for g in groups]):
        print("render", r)
    print("sheet ->", _save(sheet.remote(film, fr), f"{film}_test.jpg"))
    if full_jpg:
        for x, data in zip(fr, jpgs.remote(film, fr)):
            if data:
                print("still ->", _save(data, f"{film}_{x:04d}.jpg"))


@app.local_entrypoint()
def full(film: str = "qkv", samples: int = 96, per_chunk: int = 24, resume: bool = False, res_pct: int = 100):
    import time
    t = time.time()
    frames = build.remote(film)["frames"]
    ranges = [(film, a, min(frames - 1, a + per_chunk - 1), samples, res_pct) for a in range(0, frames, per_chunk)]
    have = set()
    if resume:
        try:
            have = {e.path.rsplit("/", 1)[-1] for e in vol.listdir(f"l2films/chunks/{film}")}
        except Exception:
            have = set()
    todo = [r for r in ranges if f"c_{r[1]:05d}.mp4" not in have]
    print(f"{film}: {frames} frames, {len(ranges)} chunks, {len(todo)} to render")
    for r in render_chunk.starmap(todo, order_outputs=False):
        print(r, flush=True)
    print(concat.remote(film, [r[1] for r in ranges]))
    fr = [int(i * (frames - 1) / 11) for i in range(12)]
    print("sheet ->", _save(sheet.remote(film, fr, "plate", 4, 640), f"{film}_plate.jpg"))
    print(f"done in {round(time.time() - t)} s")


# ------------------------------------------------------------------------------------------------ composite
@app.function(image=comp_image, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def comp_chunk(film: str, start: int, end: int) -> str:
    import sys
    sys.path.insert(0, "/root/L2/films/build")
    import overlay
    vol.reload()
    d = f"{VOL}/comp/{film}"
    os.makedirs(d, exist_ok=True)
    out = f"{d}/v_{start:05d}.mp4"
    overlay.render_range(film, f"{VOL}/plates/{film}.mp4", f"{VOL}/blend/proj/{film}.json", start, end, out)
    vol.commit()
    return out


@app.function(image=comp_image, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def comp_final(film: str, starts: list, audio_files: dict) -> dict:
    import sys
    sys.path.insert(0, "/root/L2/films/build")
    import overlay
    vol.reload()
    adir = f"/tmp/audio_{film}"
    os.makedirs(adir, exist_ok=True)
    for name, data in audio_files.items():
        p = os.path.join(adir, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(data)
    res = overlay.finish(film, [f"{VOL}/comp/{film}/v_{s:05d}.mp4" for s in sorted(starts)], adir, f"{VOL}/out")
    vol.commit()
    return res


@app.local_entrypoint()
def comp(film: str = "qkv", per_chunk: int = 300, only_video: bool = False):
    import glob
    tl = json.load(open(os.path.join(BUILD, "timeline", f"{film}.json")))
    frames = tl["frames"]
    starts = list(range(0, frames, per_chunk))
    for r in comp_chunk.starmap([(film, s, min(frames - 1, s + per_chunk - 1)) for s in starts], order_outputs=False):
        print(r, flush=True)
    audio = {}
    for b in tl["blocks"]:
        audio["narr/" + os.path.basename(b["audio"])] = open(os.path.join(BUILD, b["audio"]), "rb").read()
    for p in glob.glob(os.path.join(FILMS, "music", "*.mp3")) + glob.glob(os.path.join(BUILD, "sfx", "*.mp3")):
        audio[("music/" if "/music/" in p else "sfx/") + os.path.basename(p)] = open(p, "rb").read()
    res = comp_final.remote(film, starts, audio)
    print(json.dumps(res, indent=1))
    for key, local in (("mp4", f"{film}.mp4"), ("webm", f"{film}.webm"), ("jpg", f"{film}.jpg")):
        data = fetch.remote([res[key]])[0]
        open(os.path.join(FILMS, local), "wb").write(data)
        print("->", os.path.join(FILMS, local), round(len(data) / 1e6, 2), "MB")
    fr = [int(i * (frames - 1) / 11) for i in range(12)]
    print("sheet ->", _save(sheet.remote(film, fr, "out", 4, 640), f"{film}_out.jpg"))


@app.function(image=comp_image, volumes={"/vol": vol}, cpu=4, memory=8192, timeout=900)
def comp_stills(film: str, frames: list) -> list:
    import sys
    sys.path.insert(0, "/root/L2/films/build")
    import overlay
    vol.reload()
    return [overlay.render_still(film, f"{VOL}/stills/{film}/f_{fr:04d}.png", f"{VOL}/blend/proj/{film}.json", fr) for fr in frames]


@app.local_entrypoint()
def style(film: str = "qkv", frames: str = "0", samples: int = 96, nobuild: bool = False, tag: str = "v3"):
    """Style frames WITH overlays: build (with pins), render stills, composite, save sheets/<film>_<tag>_<frame>.jpg."""
    import subprocess
    if not nobuild:
        print("built", build.remote(film, True))
    fr = [int(x) for x in frames.split(",")]
    groups = [fr[i::5] for i in range(min(5, len(fr)))]
    for r in render_stills.starmap([(film, g, samples, 100) for g in groups]):
        print("render", r["sec"], r["errors"][:1])
    paths = []
    for x, data in zip(fr, comp_stills.remote(film, fr)):
        paths.append(_save(data, f"{film}_{tag}_{x:04d}.jpg"))
    print("stills:", paths)


@app.local_entrypoint()
def outsheet(film: str = "qkv", frames: str = "", cols: int = 3, width: int = 800):
    fr = [int(x) for x in frames.split(",")]
    print("sheet ->", _save(sheet.remote(film, fr, "out", cols, width), f"{film}_outq.jpg"))


@app.local_entrypoint()
def plate(film: str = "qkv", per_chunk: int = 30, frames: int = 0):
    """Concat the chunks already on the volume into plates/<film>.mp4 (no build, no render) + a plate contact sheet."""
    tl = json.load(open(os.path.join(BUILD, "timeline", f"{film}.json")))
    n = frames or tl["frames"]
    print(concat.remote(film, list(range(0, n, per_chunk))))
    fr = [0, 120, 300, 450, 580, 620] + [int(i * (n - 1) / 5) for i in range(1, 6)] + [n - 1]
    print("sheet ->", _save(sheet.remote(film, fr, "plate", 4, 640), f"{film}_plate.jpg"))


@app.local_entrypoint()
def comp_as(film: str = "finale", out: str = "", per_chunk: int = 300):
    """Like comp, but saves films/<out>.mp4/.webm/.jpg (e.g. finale_v5) so the current film stays until the new one
    is verified. Added 31 Oct for the finale v5; comp's behaviour is unchanged."""
    import glob
    out = out or f"{film}_new"
    tl = json.load(open(os.path.join(BUILD, "timeline", f"{film}.json")))
    frames = tl["frames"]
    starts = list(range(0, frames, per_chunk))
    for r in comp_chunk.starmap([(film, s, min(frames - 1, s + per_chunk - 1)) for s in starts], order_outputs=False):
        print(r, flush=True)
    audio = {}
    for b in tl["blocks"]:
        audio["narr/" + os.path.basename(b["audio"])] = open(os.path.join(BUILD, b["audio"]), "rb").read()
    for p in glob.glob(os.path.join(FILMS, "music", "*.mp3")) + glob.glob(os.path.join(BUILD, "sfx", "*.mp3")):
        audio[("music/" if "/music/" in p else "sfx/") + os.path.basename(p)] = open(p, "rb").read()
    res = comp_final.remote(film, starts, audio)
    print(json.dumps(res, indent=1))
    for key, ext in (("mp4", "mp4"), ("webm", "webm"), ("jpg", "jpg")):
        data = fetch.remote([res[key]])[0]
        open(os.path.join(FILMS, f"{out}.{ext}"), "wb").write(data)
        print("->", os.path.join(FILMS, f"{out}.{ext}"), round(len(data) / 1e6, 2), "MB")


# ------------------------------------------------------------------------------------------------ detached full render (added for params / s8)
@app.function(image=blender_image, volumes={"/vol": vol}, cpu=2, memory=4096, timeout=6 * 3600)
def full_job(film: str, samples: int = 96, per_chunk: int = 24, res_pct: int = 100, resume: bool = False) -> dict:
    """The same steps as `full`, but run remotely, so the laptop can let go (spawn it with `modal run --detach`)."""
    import time
    t = time.time()
    frames = build.remote(film)["frames"]
    ranges = [(film, a, min(frames - 1, a + per_chunk - 1), samples, res_pct) for a in range(0, frames, per_chunk)]
    vol.reload()
    have = set(os.listdir(f"{VOL}/chunks/{film}")) if (resume and os.path.isdir(f"{VOL}/chunks/{film}")) else set()
    todo = [r for r in ranges if f"c_{r[1]:05d}.mp4" not in have]
    done = [r for r in render_chunk.starmap(todo, order_outputs=False)]
    plate = concat.remote(film, [r[1] for r in ranges])
    return {"film": film, "frames": frames, "chunks": len(ranges), "rendered": len(done), "plate": plate, "seconds": round(time.time() - t)}


@app.local_entrypoint()
def full_spawn(film: str = "qkv", samples: int = 96, per_chunk: int = 24, resume: bool = False):
    """MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run --detach modal_films.py::full_spawn --film <film>"""
    call = full_job.spawn(film, samples, per_chunk, 100, resume)
    print("spawned", film, call.object_id)


@app.local_entrypoint()
def full_poll(call_id: str = "", film: str = ""):
    """Check a spawned full_job; when it is done, save a plate contact sheet."""
    try:
        res = modal.FunctionCall.from_id(call_id).get(timeout=1)
    except TimeoutError:
        print("running")
        return
    print(json.dumps(res))
    n = res["frames"]
    fr = [int(i * (n - 1) / 11) for i in range(12)]
    print("sheet ->", _save(sheet.remote(res["film"], fr, "plate", 4, 640), f"{res['film']}_plate.jpg"))


@app.function(image=blender_image, volumes={"/vol": vol}, cpu=2, memory=4096, timeout=4 * 3600)
def patch_job(film: str, starts: list, samples: int = 96, per_chunk: int = 24) -> dict:
    """Rebuild the film and re-render only the chunks that start at `starts`, then re-concat the plate."""
    frames = build.remote(film)["frames"]
    todo = [(film, a, min(frames - 1, a + per_chunk - 1), samples, 100) for a in starts]
    done = list(render_chunk.starmap(todo, order_outputs=False))
    plate = concat.remote(film, list(range(0, frames, per_chunk)))
    return {"film": film, "frames": frames, "rendered": len(done), "plate": plate}


@app.local_entrypoint()
def patch_spawn(film: str = "", starts: str = "", samples: int = 96):
    """modal run --detach modal_films.py::patch_spawn --film <film> --starts 1752,1776"""
    call = patch_job.spawn(film, [int(x) for x in starts.split(",")], samples)
    print("spawned", film, call.object_id)


@app.local_entrypoint()
def restill(film: str = "qkv", frames: str = "0", tag: str = "r1"):
    """Re-composite stills already rendered on the volume (no build, no GPU): after a spec-only change."""
    fr = [int(x) for x in frames.split(",")]
    for x, data in zip(fr, comp_stills.remote(film, fr)):
        print("still ->", _save(data, f"{film}_{tag}_{x:04d}.jpg"))


@app.function(image=comp_image, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def finale_webm_fn(film: str, kbps: int) -> dict:
    """Re-encode out/<film>.webm at a lower video bitrate (from the composited parts + the mp4's final mix)."""
    vol.reload()
    parts = sorted(p for p in os.listdir(f"{VOL}/comp/{film}") if p.startswith("v_"))
    with open("/tmp/parts.txt", "w") as fh:
        fh.writelines(f"file '{VOL}/comp/{film}/{p}'\n" for p in parts)
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/parts.txt", "-c", "copy", "/tmp/v.mp4"])
    mp4 = f"{VOL}/out/{film}.mp4"
    dur = _sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4]).stdout.strip()
    out = f"{VOL}/out/{film}.webm"
    _sh(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/v.mp4", "-i", mp4, "-map", "0:v", "-map", "1:a", "-c:v", "libvpx-vp9",
         "-b:v", f"{kbps}k", "-deadline", "good", "-cpu-used", "3", "-row-mt", "1", "-c:a", "libopus", "-b:a", "128k", "-t", dur, out])
    vol.commit()
    return {"webm": out, "mb": round(os.path.getsize(out) / 1e6, 2)}


@app.local_entrypoint()
def finale_webm(film: str = "finale", out: str = "", kbps: int = 820):
    """Added 31 Oct (finale v5): a smaller webm copy, saved as films/<out>.webm."""
    res = finale_webm_fn.remote(film, kbps)
    print(res)
    data = fetch.remote([res["webm"]])[0]
    open(os.path.join(FILMS, f"{out or film}.webm"), "wb").write(data)
    print("->", os.path.join(FILMS, f"{out or film}.webm"), round(len(data) / 1e6, 2), "MB")


@app.function(image=comp_image, volumes={"/vol": vol}, cpu=8, memory=8192, timeout=3600)
def rewebm(film: str, mb: float = 24.0) -> bytes:
    """Re-encode out/<film>.webm from out/<film>.mp4 (VP9 two-pass + Opus) to fit `mb` megabytes."""
    import subprocess
    vol.reload()
    src, dst = f"{VOL}/out/{film}.mp4", f"{VOL}/out/{film}.webm"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout.strip())
    vk = int((mb * 8e6 / dur - 128e3) / 1000 * 0.97)
    base = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-c:v", "libvpx-vp9", "-b:v", f"{vk}k", "-deadline", "good",
            "-cpu-used", "2", "-row-mt", "1", "-passlogfile", f"/tmp/{film}_vp9"]
    _sh(base + ["-pass", "1", "-an", "-f", "webm", "/dev/null"])
    _sh(base + ["-pass", "2", "-c:a", "libopus", "-b:a", "128k", dst])
    vol.commit()
    return open(dst, "rb").read()


@app.local_entrypoint()
def webm_fit(film: str = "", mb: float = 24.0):
    data = rewebm.remote(film, mb)
    open(os.path.join(FILMS, f"{film}.webm"), "wb").write(data)
    print("->", os.path.join(FILMS, f"{film}.webm"), round(len(data) / 1e6, 2), "MB")
