"""Lecture 3 v5, the LLM Wiki: export the navigation animation ("Watch one question move through the wiki") as a GIF.

    cd /Users/raj/Claude_Brain/enterprise-agents-course
    python3 lectures/L3-the-memory/v5/make_preview_wiki.py
    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_wiki_nav_gif_modal.py

Headless Chromium (Playwright) on Modal opens v5/preview_wiki.html, goes to the slide, stops the autoplay and plays the
same seven scenes with the slide's own timings while Chromium's screencast records a frame at every repaint (with its
timestamp). Frames closer than 60 ms are thinned; each frame lasts until the next. Identical frames are merged. Pillow writes the GIF with one
shared palette. Output: v5/img/wiki/wiki_nav.gif (and wiki_nav_scene-N.png, one still per scene, for checking).
"""
import io
import os
import pathlib
import subprocess
import time

import modal

_P = pathlib.Path(__file__).resolve().parents
ROOT = _P[3] if len(_P) > 3 else _P[-1]
SNAP = pathlib.Path(os.environ.get("GIF_SNAP", "/private/tmp/l3v5_wiki_gif_snap"))
if modal.is_local():
    SNAP.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude", "experiments/", "--exclude", "archive*/", "--exclude", "qa*/",
                    "--exclude", "*.mp4", "--exclude", "*.webm", "--exclude", "*.ipynb", "--exclude", "__pycache__/",
                    "--include", "engine/***", "--include", "lectures/", "--include", "lectures/L3-the-memory/***",
                    "--exclude", "*", str(ROOT) + "/", str(SNAP) + "/"], check=True)

image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0", "pillow==10.4.0")
         .run_commands("playwright install --with-deps chromium").add_local_dir(SNAP, "/course"))
app = modal.App("l3v5-wiki-nav-gif", image=image)
PLATE = "Query, Step by Step"
SCALE = 0.62          # 1440 x 770 crop -> about 893 x 477
BURST_MS, STEP_MS = 1100, 90


@app.function(timeout=900, cpu=2, memory=4096)
def render() -> dict:
    from PIL import Image
    from playwright.sync_api import sync_playwright

    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    frames, stills, errors = [], {}, []
    clip = {"x": 80, "y": 108, "width": 1440, "height": 772}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://127.0.0.1:8099/lectures/L3-the-memory/v5/preview_wiki.html", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        n = pg.evaluate(f"[...document.querySelectorAll('.slide')].findIndex(s => s.dataset.plate === {PLATE!r})")
        pg.evaluate(f"deckApi.show({n})")
        pg.wait_for_timeout(600)
        pg.evaluate("document.querySelector('[data-fig=wiki_nav]').__wikiNav.stop()")
        dur = pg.evaluate("document.querySelector('[data-fig=wiki_nav]').__wikiNav.DUR")
        pg.add_style_tag(content=".chrome,#pbar,.wiki-nrail .bar{visibility:hidden!important}")
        # the browser's own screencast: a frame each time the page repaints, with its timestamp
        cdp = pg.context.new_cdp_session(pg)
        got = []
        def on_frame(ev):
            got.append((ev["metadata"]["timestamp"], ev["data"]))
            try:
                cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
            except Exception as e:  # noqa: BLE001
                errors.append("ack: " + str(e))
        cdp.on("Page.screencastFrame", on_frame)
        cdp.send("Page.startScreencast", {"format": "png", "everyNthFrame": 1})
        pg.wait_for_timeout(400)
        t_start = time.time()
        marks = []
        for sc in range(7):
            marks.append(time.time())
            pg.evaluate(f"document.querySelector('[data-fig=wiki_nav]').__wikiNav.render({sc}, {'true' if sc == 0 else 'false'})")
            pg.wait_for_timeout(dur[sc])
        t_end = time.time()
        cdp.send("Page.stopScreencast")
        pg.wait_for_timeout(300)
        for sc in range(7):  # one exact still per scene, for checking
            pg.evaluate(f"document.querySelector('[data-fig=wiki_nav]').__wikiNav.render({sc}, true)")
            pg.wait_for_timeout(700)
            stills[sc] = pg.screenshot(clip=clip)
        import base64
        seq = [(ts, base64.b64decode(d)) for ts, d in sorted(got) if t_start - 0.05 <= ts <= t_end]
        # keep at most one frame per 60 ms; each frame lasts until the next one
        keep = []
        for ts, png in seq:
            if keep and ts - keep[-1][0] < 0.06:
                keep[-1] = (keep[-1][0], png)
            else:
                keep.append((ts, png))
        first = (t_start, keep[0][1]) if keep and keep[0][0] > t_start else None
        keep = ([first] if first else []) + keep
        for i, (ts, png) in enumerate(keep):
            nxt = keep[i + 1][0] if i + 1 < len(keep) else t_end
            frames.append((png, max(20, int(round((nxt - ts) * 1000)))))
        b.close()
    srv.terminate()
    # merge identical consecutive frames, then one shared palette
    merged = []
    for png, ms in frames:
        if merged and merged[-1][0] == png:
            merged[-1][1] += ms
        else:
            merged.append([png, ms])
    box = (clip["x"], clip["y"], clip["x"] + clip["width"], clip["y"] + clip["height"])
    ims = [Image.open(io.BytesIO(png)).convert("RGB") for png, _ in merged]
    ims = [im.crop(box) if im.size == (1600, 900) else im.resize((1600, 900)).crop(box) for im in ims]
    w, h = int(ims[0].width * SCALE), int(ims[0].height * SCALE)
    ims = [im.resize((w, h), Image.LANCZOS) for im in ims]
    pal_src = Image.new("RGB", (w, h * 3))
    for i, k in enumerate((0, len(ims) // 2, len(ims) - 1)):
        pal_src.paste(ims[k], (0, h * i))
    pal = pal_src.quantize(colors=255, method=Image.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
    out = io.BytesIO()
    q[0].save(out, format="GIF", save_all=True, append_images=q[1:], duration=[ms for _, ms in merged], loop=0,
              optimize=True, disposal=1)
    return {"gif": out.getvalue(), "stills": stills, "frames": len(merged), "raw_frames": len(frames),
            "size": [w, h], "ms": sum(ms for _, ms in merged), "errors": errors}


@app.local_entrypoint()
def main():
    r = render.remote()
    out = ROOT / "lectures/L3-the-memory/v5/img/wiki"
    out.mkdir(parents=True, exist_ok=True)
    (out / "wiki_nav.gif").write_bytes(r["gif"])
    for sc, png in r["stills"].items():
        (out / f"wiki_nav_scene-{sc}.png").write_bytes(png)
    print(f"wrote {out / 'wiki_nav.gif'}: {len(r['gif']) / 1e6:.2f} MB, {r['frames']} frames ({r['raw_frames']} captured), "
          f"{r['size'][0]}x{r['size'][1]}, {r['ms'] / 1000:.1f} s per loop; page errors: {r['errors'] or 'none'}")
