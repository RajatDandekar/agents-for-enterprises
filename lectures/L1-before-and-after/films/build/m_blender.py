"""Blender on Modal for the L1 film. Builds each shot's .blend INSIDE the container from
blender/shots.py, renders with Cycles/OptiX on L4s in parallel chunks, encodes nothing heavy locally.

  modal run m_blender.py::test --shot harness --frames 0,200,400 --samples 64 --res 50
  modal run m_blender.py::full --shots harness,model --samples 96
"""
import os, pathlib
import modal

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_URL = "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"
VOL = "/vol/l1"
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("wget", "xz-utils", "ffmpeg", "libx11-6", "libxi6", "libxxf86vm1", "libxfixes3", "libxrender1",
                 "libgl1", "libxkbcommon0", "libsm6", "libice6", "libegl1")
    .run_commands(f"wget -q {BLENDER_URL} -O /tmp/b.tar.xz",
                  "mkdir -p /opt/blender && tar xf /tmp/b.tar.xz -C /opt/blender --strip-components=1 && rm /tmp/b.tar.xz")
    .env({"TIMELINE": "/root/timeline.json"})
    .add_local_dir(os.path.join(HERE, "blender"), "/root/blender", ignore=["*.blend", "__pycache__/"])
    .add_local_file(os.path.join(HERE, "timeline.json"), "/root/timeline.json")
)
vol = modal.Volume.from_name("l1film", create_if_missing=True)
app = modal.App("l1film-blender")

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
sc.cycles.samples = int(os.environ.get("SAMPLES", "128"))
sc.render.resolution_percentage = int(os.environ.get("RES_PCT", "100"))
"""


@app.function(image=image, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=1800)
def build(shot: str) -> dict:
    import subprocess
    vol.reload()
    p = subprocess.run(["/opt/blender/blender", "-b", "--factory-startup", "-P", "/root/blender/shots.py",
                        "--", "--shot", shot, "--outdir", f"{VOL}/blend"], capture_output=True, text=True)
    saved = [l for l in p.stdout.splitlines() if l.startswith("SAVED")]
    if p.returncode or not saved:
        raise RuntimeError(f"build {shot} failed rc={p.returncode}\n{p.stdout[-4000:]}\n{p.stderr[-3000:]}")
    vol.commit()
    return {"shot": shot, "frames": int(saved[-1].split()[-1]), "proj": open(f"{VOL}/blend/proj/{shot}.json").read()}


@app.function(image=image, gpu=["L40S", "A10G", "L4"], volumes={"/vol": vol}, cpu=4, memory=16384, timeout=3600, retries=2)
def render_chunk(shot: str, start: int, end: int, samples: int, out: str, res_pct: int = 100) -> int:
    import subprocess, time
    vol.reload()
    od = f"{VOL}/frames/{out}"
    os.makedirs(od, exist_ok=True)
    pathlib.Path("/tmp/gpu.py").write_text(GPU_SETUP)
    env = dict(os.environ, SAMPLES=str(samples), RES_PCT=str(res_pct))
    t = time.time()
    p = subprocess.run(["/opt/blender/blender", "-b", f"{VOL}/blend/{shot}.blend", "-P", "/tmp/gpu.py",
                        "-o", f"{od}/f_####", "-F", "PNG", "-s", str(start), "-e", str(end), "-a"],
                       env=env, capture_output=True, text=True)
    print(f"chunk {shot} {start}-{end} rc={p.returncode} {time.time()-t:.0f}s\n" + "\n".join(p.stdout.splitlines()[-3:]) + p.stderr[-500:])
    vol.commit()
    return p.returncode


@app.function(image=image, volumes={"/vol": vol}, cpu=4, timeout=900)
def sheet(out: str, frames: list, cols: int = 2, width: int = 960) -> bytes:
    import subprocess
    vol.reload()
    files = [f"{VOL}/frames/{out}/f_{f:04d}.png" for f in frames if os.path.exists(f"{VOL}/frames/{out}/f_{f:04d}.png")]
    n = len(files)
    if not n:
        return b""
    h = width * 9 // 16
    args, filt = [], ""
    for i, fp in enumerate(files):
        args += ["-i", fp]
        filt += f"[{i}]scale={width}:{h},drawtext=text='{int(os.path.basename(fp)[2:6])}':x=10:y=10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.5[s{i}];"
    lay = "|".join(f"{(i % cols) * width}_{(i // cols) * h}" for i in range(n))
    filt += "".join(f"[s{i}]" for i in range(n)) + f"xstack=inputs={n}:layout={lay}:fill=white"
    if n == 1:
        filt = f"[0]scale={width}:{h}"
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-filter_complex", filt, "-frames:v", "1",
                        "-q:v", "3", "-f", "image2", "-c:v", "mjpeg", "-"], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[-800:])
    return p.stdout


@app.function(image=image, volumes={"/vol": vol}, cpu=2, timeout=600)
def still(out: str, frame: int) -> bytes:
    import subprocess
    vol.reload()
    p = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{VOL}/frames/{out}/f_{frame:04d}.png", "-q:v", "2",
                        "-f", "image2", "-c:v", "mjpeg", "-"], capture_output=True)
    return p.stdout


def _local(name, data):
    d = os.path.join(HERE, "out")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    open(path, "wb" if isinstance(data, bytes) else "w").write(data)
    return path


@app.local_entrypoint()
def test(shot: str = "harness", frames: str = "0,200", samples: int = 64, res: int = 50, full_stills: int = 0):
    info = build.remote(shot)
    _local(f"proj_{shot}.json", info["proj"])
    fr = [min(int(f), info["frames"] - 1) for f in frames.split(",")]
    out = f"test_{shot}_{res}"
    codes = list(render_chunk.starmap([(shot, f, f, samples, out, res) for f in fr]))
    print("built", shot, info["frames"], "frames; codes", codes)
    print("sheet ->", _local(f"sheet_{shot}.jpg", sheet.remote(out, fr)))
    if full_stills:
        for f in fr:
            print("still ->", _local(f"still_{shot}_{f:04d}.jpg", still.remote(out, f)))


@app.local_entrypoint()
def full(shots: str = "harness", samples: int = 96, per_chunk: int = 12):
    import json
    jobs = []
    infos = list(build.map(shots.split(",")))
    for info in infos:
        _local(f"proj_{info['shot']}.json", info["proj"])
        last = info["frames"] - 1
        jobs += [(info["shot"], a, min(last, a + per_chunk - 1), samples, info["shot"]) for a in range(0, last + 1, per_chunk)]
    print("chunks", len(jobs))
    codes = list(render_chunk.starmap(jobs))
    bad = [j for j, c in zip(jobs, codes) if c]
    print("failed chunks", bad)


@app.local_entrypoint()
def part(shot: str = "refuse", start: int = 560, end: int = 574, samples: int = 96):
    step = 5
    jobs = [(shot, a, min(end, a + step - 1), samples, shot) for a in range(start, end + 1, step)]
    print("codes", list(render_chunk.starmap(jobs)))
