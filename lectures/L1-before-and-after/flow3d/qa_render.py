"""Render the 3D flow headless on Modal (Chromium + SwiftShader WebGL) and bring the PNGs back to flow3d/qa/.

    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/qa_render.py                  # every stage, end state
    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/qa_render.py --shots "3:2.5,4:4.2"   # stage:seconds
    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/qa_render.py --poster 1      # also writes poster.png
    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/qa_render.py --deck 1        # 1600x900 deck-mode check
"""
import json
import pathlib
import subprocess
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
ENGINE = HERE.parents[2] / "engine" if len(HERE.parents) > 2 else HERE  # the course's plate engine (local side only)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .add_local_dir(HERE, "/flow3d", ignore=lambda p: "qa" in pathlib.Path(p).parts or (str(p).endswith(".png") and not str(p).endswith("poster.png")))
    .add_local_dir(ENGINE, "/engine")
)
app = modal.App("flow3d-qa", image=image)
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"]

DECK_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,300..700&family=Google+Sans+Code:wght@300..700&display=swap">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<style>html,body{margin:0;background:#fff}#fig{position:absolute;left:0;top:0;width:1600px;height:900px;transform-origin:0 0;transform:scale(1.2)}</style>
<script src="trace.js"></script></head><body><div id="fig"></div>
<script type="module">import {mountFlow3D} from './flow3d.js'; await document.fonts.ready;
window.flow3d = mountFlow3D(document.getElementById('fig'), {trace: window.FLOW3D_TRACE, mode: 'deck', still: true}); window.__flow3dReady = true;</script>
<script>/* the deck.js path, as the deck will use it */ window.__deckFig = null;</script></body></html>"""


PLATES_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Lecture 1 test deck</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,300..700&family=Google+Sans+Code:wght@300..700&display=swap">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<link rel="stylesheet" href="engine/plates.css"></head><body><main class="deck" id="deck">
<section class="slide" data-plain="1"><div class="center"><h1>Test</h1></div></section>
<section class="slide" data-plate="How it works, underneath">
  <div class="fig" data-fig="flow3d" style="left:0;top:0;width:1600px;height:900px"></div>
  STEPS
</section></main>
<script src="flow3d/trace.js"></script><script src="flow3d/deck.js"></script><script src="engine/plates.js"></script></body></html>""".replace("STEPS", '<span class="step"></span>' * 18)


@app.function(timeout=1800, cpu=4, memory=8192)
def plates_check() -> dict:
    """The real plate engine driving the figure through deck.js: enter the slide, step forward, step back."""
    from playwright.sync_api import sync_playwright
    import os
    os.makedirs("/site", exist_ok=True)
    os.symlink("/flow3d", "/site/flow3d"); os.symlink("/engine", "/site/engine")
    pathlib.Path("/site/test.html").write_text(PLATES_PAGE)
    srv = subprocess.Popen(["python", "-m", "http.server", "8098", "--directory", "/site"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    out, logs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
        pg.goto("http://127.0.0.1:8098/test.html", wait_until="networkidle")
        pg.wait_for_timeout(1000)
        pg.evaluate("deckApi.show(1)")
        pg.wait_for_timeout(9000)
        out["qa/plates-enter.png"] = pg.screenshot()
        for _ in range(3):
            pg.evaluate("deckApi.next()")
        pg.wait_for_timeout(12000)
        out["qa/plates-step3.png"] = pg.screenshot()
        pg.evaluate("deckApi.prev()")
        pg.wait_for_timeout(5000)
        out["qa/plates-back2.png"] = pg.screenshot()
        logs.append("canvas: " + str(pg.evaluate("!!document.querySelector('[data-fig=flow3d] canvas')")))
        pg.wait_for_function("!document.querySelector('.b-narr').hidden", timeout=60000)
        before = pg.evaluate("[deckApi.cur, document.querySelectorAll('.slide.active .step.shown').length]")
        pg.click(".b-narr")
        pg.wait_for_timeout(2500)
        speaking = pg.evaluate("!document.querySelector('.f3d-speak').hidden")
        pg.keyboard.press(" ")
        pg.wait_for_timeout(800)
        after = pg.evaluate("[deckApi.cur, document.querySelectorAll('.slide.active .step.shown').length, document.querySelector('.f3d-speak').classList.contains('paused')]")
        logs.append(f"narration: speaking={speaking} deck before={before} after Space={after} (same slide and steps, paused=True expected)")
        out["qa/plates-narration.png"] = pg.screenshot()
        b.close()
    srv.terminate()
    out["qa/plates_log.txt"] = "\n".join(logs).encode()
    return out


CHECK_JS = """(() => { const fig = document.getElementById('fig') || document.querySelector('.f3d');
  const fr = fig.getBoundingClientRect(), sc = fr.width / 1600, m = 20 * sc, out = [];
  fig.querySelectorAll('*').forEach((e) => { const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
    const own = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (own && (r.left < fr.left + m - 2 || r.right > fr.right - m + 2 || r.top < fr.top + m - 2 || r.bottom > fr.bottom - m + 2)) out.push('OUT ' + e.className + ' ' + e.textContent.trim().slice(0, 30));
    if (['DIV', 'PRE', 'P'].includes(e.tagName) && e.scrollHeight > e.clientHeight + 4 && cs.overflow !== 'visible' && cs.overflowY !== 'visible') out.push('CLIP ' + e.className);
    if (own && parseFloat(cs.fontSize) < 12) out.push('TINY ' + cs.fontSize + ' ' + e.textContent.trim().slice(0, 20)); });
  return [...new Set(out)]; })()"""


@app.function(timeout=3600, cpu=4, memory=8192)
def deck_check() -> dict:
    """The deck_qa rules (OUT of the frame less 20 px, CLIP, TINY under 12 px) on every stage of the 1600x900 deck mount,
    sampled every second of each stage and at its end."""
    from playwright.sync_api import sync_playwright
    import os
    if not os.path.exists("/flow3d/_engine"):
        os.symlink("/engine", "/flow3d/_engine")
    page = DECK_PAGE.replace("transform:scale(1.2)", "transform:none").replace('<script type="importmap">', '<link rel="stylesheet" href="_engine/plates.css"><script type="importmap">')
    page = page.replace('<div id="fig"></div>', '<div class="slide active" style="display:block;position:absolute;inset:0"><div id="fig"></div></div>')
    (pathlib.Path("/flow3d") / "_deck.html").write_text(page)
    srv = subprocess.Popen(["python", "-m", "http.server", "8097", "--directory", "/flow3d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    rep, logs = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
        pg.goto("http://127.0.0.1:8097/_deck.html", wait_until="networkidle")
        pg.wait_for_function("window.__flow3dReady === true", timeout=120000)
        pg.wait_for_function("!document.querySelector('.b-narr').hidden", timeout=60000)
        pg.wait_for_timeout(1000)
        stages = pg.evaluate("flow3d.stages")
        for k, st in enumerate(stages):
            ts = [x + 0.5 for x in range(int(st["dur"]))] + ["end"]
            for t in ts:
                pg.evaluate(f"flow3d.seek({k}, {json.dumps(t)})")
                issues = pg.evaluate(CHECK_JS)
                if issues:
                    rep.append({"stage": k, "t": t, "issues": issues[:6]})
        b.close()
    srv.terminate()
    return {"qa/deck_check.json": json.dumps({"stages": len(stages), "page_errors": logs, "problems": rep}, indent=1).encode()}


@app.function(timeout=1800, cpu=4, memory=8192)
def audio_check() -> dict:
    """Narration in headless Chromium: the clips load, the button (a real click = user gesture) starts clip 0,
    Space pauses and resumes audio and animation together, a manual step plays that stage's clip; standalone and deck."""
    from playwright.sync_api import sync_playwright
    import os
    if not os.path.exists("/flow3d/_engine"):
        os.symlink("/engine", "/flow3d/_engine")
    (pathlib.Path("/flow3d") / "_deckn.html").write_text(DECK_PAGE.replace("still: true", "still: false"))
    srv = subprocess.Popen(["python", "-m", "http.server", "8096", "--directory", "/flow3d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    res, logs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        for name, url, vp in [("standalone", "index.html", (1920, 1080)), ("deck", "_deckn.html", (1920, 1080))]:
            pg = b.new_page(viewport={"width": vp[0], "height": vp[1]})
            pg.on("console", lambda m, n=name: logs.append(f"{n} {m.type}: {m.text}") if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e, n=name: logs.append(f"{n} pageerror: {e}"))
            pg.goto(f"http://127.0.0.1:8096/{url}", wait_until="networkidle")
            pg.wait_for_function("window.__flow3dReady === true", timeout=120000)
            pg.wait_for_function("!document.querySelector('.b-narr').hidden", timeout=60000)
            pg.wait_for_timeout(4000)
            r = {"loaded": pg.evaluate("flow3d.audioState()")}
            pg.click(".b-narr")
            pg.wait_for_timeout(3000)
            r["after_click"] = pg.evaluate("[flow3d.stage, flow3d.audioState().pop()]")
            pg.keyboard.press(" ")
            pg.wait_for_timeout(1200)
            a = pg.evaluate("[flow3d.paused, flow3d.audioState().pop()]")
            pg.wait_for_timeout(1000)
            r["paused"] = a + [pg.evaluate("flow3d.audioState().pop().time")]
            pg.keyboard.press(" ")
            pg.wait_for_timeout(1500)
            r["resumed"] = pg.evaluate("[flow3d.paused, flow3d.audioState().pop()]")
            pg.evaluate("flow3d.go(14)")
            pg.wait_for_timeout(2000)
            r["manual_step_14"] = pg.evaluate("[flow3d.stage, flow3d.audioState().pop()]")
            res[name] = r
            pg.close()
        b.close()
    srv.terminate()
    return {"qa/audio_check.json": json.dumps({"results": res, "logs": logs}, indent=1).encode()}


@app.function(timeout=1800, cpu=4, memory=8192)
def render(shots: list, poster: str = "", deck: bool = False) -> dict:
    from playwright.sync_api import sync_playwright

    (pathlib.Path("/flow3d") / "_deck.html").write_text(DECK_PAGE)
    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/flow3d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    out, logs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
        url = "http://127.0.0.1:8099/" + ("_deck.html" if deck else "index.html?still=1&stage=0&t=end")
        pg.goto(url, wait_until="networkidle")
        try:
            pg.wait_for_function("window.__flow3dReady === true", timeout=120000)
        except Exception as e:
            raise RuntimeError("flow3d did not mount: " + " | ".join(logs)[-3000:]) from e
        pg.wait_for_timeout(1500)
        info = pg.evaluate("({count: flow3d.count, stages: flow3d.stages, gl: (()=>{const c=document.querySelector('canvas'); const g=c&&(c.getContext('webgl2')||c.getContext('webgl')); if(!g) return 'none'; const d=g.getExtension('WEBGL_debug_renderer_info'); return d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):'webgl';})()})")
        logs.append("stages: " + json.dumps(info)[:3000])
        if not shots:
            shots = [f"{i}:end" for i in range(info["count"])]
        for s in shots:
            k, t = s.split(":")
            pg.evaluate(f"flow3d.seek({int(k)}, {json.dumps(t if t == 'end' else float(t))})")
            pg.wait_for_timeout(700)
            pg.evaluate("flow3d.render()")
            pg.wait_for_timeout(500)
            name = f"stage-{int(k):02d}" + ("" if t == "end" else f"-t{t.replace('.', '_')}") + ("-deck" if deck else "") + ".png"
            out[f"qa/{name}"] = pg.screenshot()
        if poster:
            k, t = (poster.split(":") + ["end"])[:2] if ":" in poster else ("0", "end")
            pg.evaluate(f"flow3d.seek({int(k)}, {json.dumps(t if t == 'end' else float(t))})")
            pg.wait_for_timeout(700)
            pg.evaluate("flow3d.render()")
            pg.wait_for_timeout(500)
            out["poster.png"] = pg.screenshot()
        # a short timing probe: frames per second of the live loop (SwiftShader, so a floor, not a laptop number)
        fps = pg.evaluate("""new Promise(r => { let n = 0; const t0 = performance.now(); flow3d.go(4); function f(){ n++; flow3d.render(); if (performance.now() - t0 < 3000) requestAnimationFrame(f); else r(n / ((performance.now() - t0) / 1000)); } requestAnimationFrame(f); })""")
        logs.append(f"swiftshader fps (render() per frame): {fps:.1f}")
        b.close()
    srv.terminate()
    out["qa/render_log.txt"] = "\n".join(logs).encode()
    return out


@app.local_entrypoint()
def main(shots: str = "", poster: str = "", deck: int = 0, plates: int = 0, check: int = 0, audio: int = 0):
    if check or audio:
        files = deck_check.remote() if check else audio_check.remote()
        for rel, data in files.items():
            (HERE / rel).write_bytes(data)
        print(list(files.values())[0].decode()[:8000])
        return
    files = plates_check.remote() if plates else render.remote([s for s in shots.split(",") if s.strip()], poster, bool(deck))
    for rel, data in files.items():
        dst = HERE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", dst.relative_to(HERE.parent.parent))
    print(files.get("qa/render_log.txt", files.get("qa/plates_log.txt", b"")).decode()[-3000:])
