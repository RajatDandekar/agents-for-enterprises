"""Render the Lecture 2 3D scene headless on Modal (Chromium + SwiftShader WebGL) and bring the PNGs back to brain3d/qa/.

    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py                       # every section and step, end state, 1920x1080
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --shots "2:0:2.5,7:3:3"  # section:step:seconds
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --deck 1                # the same at 1600x900 in deck mode
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --check 1               # deck-QA rules on every step, sampled each second
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --plates 1              # through the real plate engine, 9 slides
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --posters 1             # rewrites poster-s1..9.png and poster.png
"""
import json
import pathlib
import subprocess
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
ENGINE = HERE.parents[2] / "engine" if len(HERE.parents) > 2 else HERE
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("fonts-noto-cjk")
    .pip_install("playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .add_local_dir(HERE, "/brain3d", ignore=lambda p: "qa" in pathlib.Path(p).parts or str(p).endswith(".png") or str(p).endswith(".py"))
    .add_local_dir(ENGINE, "/engine")
)
L2DIR = HERE.parent
deck_image = image.add_local_dir(L2DIR, "/course/lectures/L2-the-brain", ignore=lambda p: "qa" in pathlib.Path(p).parts
                                  or str(p).endswith((".ipynb", ".py", ".jsonl", ".mp4"))).add_local_dir(ENGINE, "/course/engine")
app = modal.App("brain3d-qa", image=image)
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"]
STATES = [3, 4, 4, 5, 4, 5, 5, 4, 4]
TITLES = ["The game", "Tokens", "Vectors", "Attention", "Blocks", "Choice", "The loop", "Training", "Why, and the fix"]

DECK_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,300..700&family=Google+Sans+Code:wght@300..700&display=swap">
<link rel="stylesheet" href="_engine/plates.css">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<style>html,body{margin:0;background:#fff}#fig{position:absolute;left:0;top:0;width:1600px;height:900px}</style>
<script src="trace.js"></script></head><body><div class="slide active" style="display:block;position:absolute;inset:0"><div id="fig"></div></div>
<script type="module">import {mountBrain3D} from './brain3d.js'; await document.fonts.ready;
await document.fonts.load('600 50px "Google Sans Flex"'); await document.fonts.load('500 26px "Google Sans Code"');
window.brain3d = mountBrain3D(document.getElementById('fig'), {trace: window.BRAIN_TRACE, mode: 'deck', still: true, section: 1}); window.__brain3dReady = true;</script></body></html>"""

PLATES_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Lecture 2 test deck</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,300..700&family=Google+Sans+Code:wght@300..700&display=swap">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<link rel="stylesheet" href="engine/plates.css"></head><body><main class="deck" id="deck">
<section class="slide" data-plain="1"><div class="center"><h1>Test</h1></div></section>
SLIDES
</main><script src="brain3d/trace.js"></script><script src="brain3d/deck.js"></script><script src="engine/plates.js"></script></body></html>"""


def plates_page():
    sl = []
    for s in range(1, 10):
        sl.append(f'<section class="slide" data-plate="{TITLES[s - 1]}"><div class="fig" data-fig="brain3d" data-section="{s}" style="left:0;top:0;width:1600px;height:900px"></div>'
                  + '<span class="step"></span>' * (STATES[s - 1] - 1) + "</section>")
    return PLATES_PAGE.replace("SLIDES", "\n".join(sl))


def serve(directory, port):
    srv = subprocess.Popen(["python", "-m", "http.server", str(port), "--directory", directory], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    return srv


def wait_fonts(pg):
    pg.evaluate("""Promise.all([document.fonts.load('600 50px "Google Sans Flex"'), document.fonts.load('500 26px "Google Sans Code"')]).then(() => document.fonts.ready)""")


@app.function(timeout=1800, cpu=4, memory=8192)
def plates_check() -> dict:
    """The real plate engine: enter section 1, step, move to section 2 (the scene moves with it), step back."""
    from playwright.sync_api import sync_playwright
    import os
    os.makedirs("/site", exist_ok=True)
    os.symlink("/brain3d", "/site/brain3d"); os.symlink("/engine", "/site/engine")
    pathlib.Path("/site/test.html").write_text(plates_page())
    srv = serve("/site", 8098)
    out, logs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e} | {getattr(e, 'stack', '')}"))
        pg.goto("http://127.0.0.1:8098/test.html", wait_until="networkidle")
        wait_fonts(pg)
        pg.wait_for_timeout(800)
        pg.evaluate("deckApi.show(1)"); pg.wait_for_timeout(6000)
        out["qa/plates-s1-enter.png"] = pg.screenshot()
        pg.evaluate("deckApi.next()"); pg.wait_for_timeout(6000)
        out["qa/plates-s1-step1.png"] = pg.screenshot()
        pg.evaluate("deckApi.next(); deckApi.next()"); pg.wait_for_timeout(9000)  # past the last step: section 2 slide
        out["qa/plates-s2-enter.png"] = pg.screenshot()
        logs.append("cur slide " + str(pg.evaluate("deckApi.cur")) + " section " + str(pg.evaluate("window.brain3d && brain3d.section")))
        pg.evaluate("deckApi.show(6)"); pg.wait_for_timeout(7000)
        out["qa/plates-s6-enter.png"] = pg.screenshot()
        pg.evaluate("deckApi.prev()"); pg.wait_for_timeout(6000)
        out["qa/plates-s5-back.png"] = pg.screenshot()
        logs.append("canvases: " + str(pg.evaluate("document.querySelectorAll('canvas').length")) + ", section " + str(pg.evaluate("brain3d.section")) + " step " + str(pg.evaluate("brain3d.step")))
        b.close()
    srv.terminate()
    out["qa/plates_log.txt"] = "\n".join(logs).encode()
    return out


CHECK_JS = """(() => { const fig = document.getElementById('fig');
  const fr = fig.getBoundingClientRect(), sc = fr.width / 1600, m = 20 * sc, out = [];
  fig.querySelectorAll('*').forEach((e) => { const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    let p = e, hidden = false; while (p && p !== fig) { const c = getComputedStyle(p); if (c.display === 'none' || +c.opacity < 0.03) { hidden = true; break; } p = p.parentElement; }
    if (hidden) return;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
    const own = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (own && (r.left < fr.left + m - 2 || r.right > fr.right - m + 2 || r.top < fr.top + m - 2 || r.bottom > fr.bottom - m + 2)) out.push('OUT ' + e.className + ' ' + e.textContent.trim().slice(0, 30));
    if (['DIV', 'PRE', 'P'].includes(e.tagName) && e.scrollHeight > e.clientHeight + 4 && cs.overflow !== 'visible' && cs.overflowY !== 'visible') out.push('CLIP ' + e.className);
    if (own && parseFloat(cs.fontSize) * (parseFloat(getComputedStyle(e.closest('.b3d-l') || e).scale) || 1) < 12) out.push('TINY ' + cs.fontSize + ' ' + e.textContent.trim().slice(0, 20)); });
  return [...new Set(out)]; })()"""


@app.function(timeout=3600, cpu=4, memory=8192)
def deck_check() -> dict:
    from playwright.sync_api import sync_playwright
    import os
    if not os.path.exists("/brain3d/_engine"):
        os.symlink("/engine", "/brain3d/_engine")
    (pathlib.Path("/brain3d") / "_deck.html").write_text(DECK_PAGE)
    srv = serve("/brain3d", 8097)
    rep, logs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e} | {getattr(e, 'stack', '')}"))
        pg.goto("http://127.0.0.1:8097/_deck.html", wait_until="networkidle")
        pg.wait_for_function("window.__brain3dReady === true", timeout=120000)
        pg.wait_for_timeout(1000)
        stages = pg.evaluate("brain3d.stages")
        for st in stages:
            ts = [x + 0.5 for x in range(int(st["dur"]))] + ["end"]
            for t in ts:
                pg.evaluate(f"brain3d.seek({st['section']}, {st['step']}, {json.dumps(t)})")
                issues = pg.evaluate(CHECK_JS)
                if issues:
                    rep.append({"section": st["section"], "step": st["step"], "t": t, "issues": issues[:6]})
        b.close()
    srv.terminate()
    return {"qa/deck_check.json": json.dumps({"stages": len(stages), "page_errors": logs, "problems": rep}, indent=1).encode()}


@app.function(timeout=3000, cpu=8, memory=12288)
def render(shots: list, deck: bool = False, posters: bool = False) -> dict:
    from playwright.sync_api import sync_playwright
    import os
    if not os.path.exists("/brain3d/_engine"):
        os.symlink("/engine", "/brain3d/_engine")
    (pathlib.Path("/brain3d") / "_deck.html").write_text(DECK_PAGE)
    srv = serve("/brain3d", 8099)
    out, logs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        vw = {"width": 1600, "height": 900} if deck else {"width": 1920, "height": 1080}
        pg = b.new_page(viewport=vw, device_scale_factor=1)
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e} | {getattr(e, 'stack', '')}"))
        url = "http://127.0.0.1:8099/" + ("_deck.html" if deck else "index.html?still=1&section=1&step=0&t=end")
        pg.goto(url, wait_until="networkidle")
        try:
            pg.wait_for_function("window.__brain3dReady === true", timeout=120000)
        except Exception as e:
            raise RuntimeError("brain3d did not mount: " + " | ".join(logs)[-3000:]) from e
        wait_fonts(pg)
        pg.wait_for_timeout(1500)
        info = pg.evaluate("({sections: brain3d.sections, gl: (()=>{const c=document.querySelector('canvas'); const g=c&&(c.getContext('webgl2')||c.getContext('webgl')); if(!g) return 'none'; const d=g.getExtension('WEBGL_debug_renderer_info'); return d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):'webgl';})()})")
        logs.append("info: " + json.dumps(info)[:2000])
        if posters:
            shots = [f"{s}:{STATES[s - 1] - 1}:end" for s in range(1, 10)]
        if not shots:
            shots = [f"{s}:{k}:end" for s in range(1, 10) for k in range(STATES[s - 1])]
        for sh in shots:
            s, k, t = sh.split(":")
            pg.evaluate(f"brain3d.seek({int(s)}, {int(k)}, {json.dumps(t if t == 'end' else float(t))})")
            pg.wait_for_timeout(500)
            pg.evaluate("brain3d.render()")
            pg.wait_for_timeout(400)
            pg.evaluate("brain3d.render()")
            pg.wait_for_timeout(300)
            if posters:
                out[f"poster-s{int(s)}.png"] = pg.screenshot()
                continue
            name = f"s{int(s)}-k{int(k)}" + ("" if t == "end" else f"-t{t.replace('.', '_')}") + ("-deck" if deck else "") + ".png"
            out[f"qa/{name}"] = pg.screenshot()
        if posters:
            out["poster.png"] = out["poster-s9.png"]
        b.close()
    srv.terminate()
    out["qa/render_log.txt"] = "\n".join(logs).encode()
    return out


@app.function(timeout=3000, cpu=8, memory=12288, image=deck_image)
def realdeck(settle_ms: int = 4500, only: str = "") -> dict:
    """The real Lecture 2 deck (lectures/L2-the-brain/index.html) through the real plate engine, at 1600x940:
    every 3D slide, every step, screenshotted after the step has played and the camera has arrived; plus the deck-QA
    rules (tools/deck_qa.js logic) on each of those settled states."""
    from playwright.sync_api import sync_playwright
    srv = serve("/course", 8096)
    out, logs, rep = {}, [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1600, "height": 940})
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
        pg.goto("http://127.0.0.1:8096/lectures/L2-the-brain/index.html", wait_until="networkidle")
        wait_fonts(pg)
        pg.wait_for_timeout(1500)
        slides = pg.evaluate("[...document.querySelectorAll('#deck .slide')].map((s, i) => ({i, fig: !!s.querySelector('[data-fig=b3d],[data-fig=brain3d]'), steps: s.querySelectorAll('.step').length, sec: (s.querySelector('[data-section]') || {dataset: {}}).dataset.section}))")
        keep = {int(x) for x in only.split(",") if x.strip()}
        for sl in [x for x in slides if x["fig"] and (not keep or x["i"] + 1 in keep)]:
            i, n = sl["i"], sl["steps"]
            for k in range(n + 1):
                pg.evaluate(f"deckApi.show({i})")
                pg.wait_for_timeout(300)
                for _ in range(k):
                    pg.evaluate("deckApi.next()")
                    pg.wait_for_timeout(150)
                pg.wait_for_timeout(settle_ms + (16000 if k else 0))
                issues = pg.evaluate(CHECK_REAL)
                if issues:
                    rep.append({"slide": i + 1, "section": sl["sec"], "k": k, "issues": issues[:8]})
                out[f"qa/deck-slide{i + 1:02d}-k{k}.png"] = pg.screenshot()
        b.close()
    srv.terminate()
    out["qa/realdeck.json"] = json.dumps({"page_errors": logs, "problems": rep}, indent=1).encode()
    return out


CHECK_REAL = """(() => { const s = document.querySelector('#deck .slide.active'); const sr = s.getBoundingClientRect(), sc = sr.width / 1600;
  const lim = { l: sr.left + 20 * sc, r: sr.right - 20 * sc, t: sr.top + 20 * sc, b: sr.bottom - 20 * sc }; const issues = [];
  s.querySelectorAll('*').forEach((e) => { if (e.closest('.frame') || e.classList.contains('folio') || e.classList.contains('plate-head')) return;
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
    const own = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if ((r.left < lim.l - 2 || r.right > lim.r + 2 || r.top < lim.t - 2 || r.bottom > lim.b + 2) && (own || e.tagName === 'svg')) issues.push('OUT ' + e.tagName + ' ' + (e.textContent || '').trim().slice(0, 30));
    if (['DIV', 'PRE', 'P', 'TD'].includes(e.tagName) && e.scrollHeight > e.clientHeight + 4 && cs.overflow !== 'visible' && cs.overflowY !== 'visible') issues.push('CLIP ' + e.className);
    if (own && parseFloat(cs.fontSize) < 12) issues.push('TINY ' + cs.fontSize); });
  return [...new Set(issues)]; })()"""


@app.local_entrypoint()
def main(shots: str = "", deck: int = 0, plates: int = 0, check: int = 0, posters: int = 0, real: int = 0, only: str = ""):
    if real:
        files = realdeck.remote(4500, only)
        for rel, data in files.items():
            (HERE / rel).parent.mkdir(parents=True, exist_ok=True)
            (HERE / rel).write_bytes(data)
        print(files["qa/realdeck.json"].decode()[:6000])
        return
    if check:
        files = deck_check.remote()
        for rel, data in files.items():
            (HERE / rel).parent.mkdir(parents=True, exist_ok=True)
            (HERE / rel).write_bytes(data)
        print(files["qa/deck_check.json"].decode()[:8000])
        return
    files = plates_check.remote() if plates else render.remote([s for s in shots.split(",") if s.strip()], bool(deck), bool(posters))
    for rel, data in files.items():
        dst = HERE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", dst.relative_to(HERE.parent))
    print(files.get("qa/render_log.txt", files.get("qa/plates_log.txt", b"")).decode()[-3000:])
