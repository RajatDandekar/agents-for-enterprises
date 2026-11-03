"""Render the context replay (section 8) to figs/context.gif: frames from the deck in headless Chromium, assembled with
ffmpeg, both on Modal. Nothing runs on the laptop.

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L4-the-hands/tools_gif_modal.py

Frames: the slide "The Context, Part by Part" (run single) one click at a time, then "The Whole Order, in Context"
(run order_hands) one part at a time through window.L4ctx.order_hands.go(p). Every frame is the real deck figure,
drawn from figdata.js (the recorded context and its token counts).
"""
import pathlib
import subprocess
import time

import modal

_HERE = pathlib.Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else pathlib.Path("/course")  # in the container the file sits at /root
DECK = "lectures/L4-the-hands"
image = (modal.Image.debian_slim(python_version="3.11")
         .apt_install("ffmpeg")
         .pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium")
         .add_local_dir(ROOT / "engine", "/course/engine")
         .add_local_dir(ROOT / DECK, f"/course/{DECK}", ignore=lambda p: any(x in pathlib.Path(p).parts for x in ("films", "qa", "archive_v3", "experiments"))))
app = modal.App("l4-context-gif", image=image)


@app.function(timeout=900, cpu=2, memory=4096)
def render() -> bytes:
    from playwright.sync_api import sync_playwright

    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    out = pathlib.Path("/tmp/frames")
    out.mkdir()
    frames = []  # (file, seconds)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.goto(f"http://127.0.0.1:8099/{DECK}/index.html", wait_until="networkidle")
        pg.wait_for_timeout(1200)
        idx = pg.evaluate("""() => { const s = [...document.querySelectorAll('.slide')];
            return [s.findIndex((x) => x.dataset.plate === 'The Context, Part by Part'), s.findIndex((x) => x.dataset.plate === 'The Whole Order, in Context')]; }""")
        pg.add_style_tag(content=".chrome,.pbar{display:none!important}")

        def shot(sec):
            f = out / f"f{len(frames):03d}.png"
            pg.screenshot(path=str(f))
            frames.append((f, sec))

        pg.evaluate(f"deckApi.show({idx[0]})")
        pg.wait_for_timeout(700)
        shot(1.4)
        n_single = pg.evaluate(f"document.querySelectorAll('.slide')[{idx[0]}].querySelectorAll('.step').length")
        for k in range(n_single):
            pg.evaluate("deckApi.next()")
            pg.wait_for_timeout(500)
            shot(1.6 if k < n_single - 1 else 3.2)
        pg.evaluate(f"deckApi.show({idx[1]})")
        pg.wait_for_timeout(700)
        n = pg.evaluate("window.L4ctx.order_hands.n")
        for q in range(n + 1):
            pg.evaluate(f"window.L4ctx.order_hands.go({q})")
            pg.wait_for_timeout(380)
            shot(1.2 if q == 0 else 3.5 if q == n else 0.75)
        b.close()
    srv.terminate()
    lst = out / "list.txt"
    lst.write_text("".join(f"file '{f}'\nduration {d}\n" for f, d in frames) + f"file '{frames[-1][0]}'\n")
    vf = "scale=1120:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-vf", vf, "-fps_mode", "vfr", "-loop", "0", "/tmp/context.gif"], check=True)
    return pathlib.Path("/tmp/context.gif").read_bytes()


@app.local_entrypoint()
def main():
    data = render.remote()
    dst = ROOT / DECK / "figs" / "context.gif"
    dst.write_bytes(data)
    print(f"wrote {dst.relative_to(ROOT)} ({len(data) // 1024} KB)")
