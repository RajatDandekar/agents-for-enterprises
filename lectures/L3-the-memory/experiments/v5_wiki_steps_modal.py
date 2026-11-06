"""Lecture 3 v5, the LLM Wiki: screenshots of the section's slides at intermediate click steps (the deck QA tool only
shows each slide fully revealed). Reports any box whose content overflows at that step.

    cd /Users/raj/Claude_Brain/enterprise-agents-course
    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_wiki_steps_modal.py
Writes v5/qa_wiki/steps/<slide>-<k>.png.
"""
import json
import pathlib
import subprocess
import time

import modal

_P = pathlib.Path(__file__).resolve().parents
ROOT = _P[3] if len(_P) > 3 else _P[-1]
SNAP = pathlib.Path("/private/tmp/l3v5_wiki_steps_snap")
if modal.is_local():
    SNAP.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude", "experiments/", "--exclude", "archive*/", "--exclude", "qa*/",
                    "--exclude", "*.mp4", "--exclude", "*.webm", "--exclude", "*.ipynb", "--exclude", "__pycache__/",
                    "--include", "engine/***", "--include", "lectures/", "--include", "lectures/L3-the-memory/***",
                    "--exclude", "*", str(ROOT) + "/", str(SNAP) + "/"], check=True)
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium").add_local_dir(SNAP, "/course"))
app = modal.App("l3v5-wiki-steps", image=image)
WANT = {4: [1, 2, 3, 4], 5: [1, 2], 6: [1, 3], 7: [0, 1, 2, 3], 8: [1, 2], 9: [0, 1, 2], 12: [1, 2], 13: [0, 1]}
CHECK = """(() => { const s = document.querySelector('.slide.active'), out = [];
  s.querySelectorAll('div,td,p').forEach((e) => { const cs = getComputedStyle(e);
    if (cs.display === 'none' || +cs.opacity === 0) return;
    if (e.scrollHeight > e.clientHeight + 4 && cs.overflow !== 'visible' && cs.overflowY !== 'visible') out.push('CLIP ' + e.className + ' ' + (e.textContent || '').trim().slice(0, 40)); });
  return out; })()"""


@app.function(timeout=600, cpu=2, memory=4096)
def shots() -> dict:
    from playwright.sync_api import sync_playwright
    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    res, rep = {}, {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900})
        pg.goto("http://127.0.0.1:8099/lectures/L3-the-memory/v5/preview_wiki.html", wait_until="networkidle")
        pg.wait_for_timeout(1200)
        for n, ks in WANT.items():
            for k in ks:
                pg.evaluate(f"deckApi.show({n - 1})")
                for _ in range(k):
                    pg.evaluate("deckApi.next()")
                pg.wait_for_timeout(900)
                res[f"{n:02d}-{k}"] = pg.screenshot()
                rep[f"{n:02d}-{k}"] = pg.evaluate(CHECK)
        b.close()
    srv.terminate()
    return {"png": res, "rep": rep}


@app.local_entrypoint()
def main():
    r = shots.remote()
    out = ROOT / "lectures/L3-the-memory/v5/qa_wiki/steps"
    out.mkdir(parents=True, exist_ok=True)
    for k, png in r["png"].items():
        (out / f"{k}.png").write_bytes(png)
    print(json.dumps({k: v for k, v in r["rep"].items() if v}, indent=1) or "no overflow")
    print("wrote", len(r["png"]), "screenshots to", out)
