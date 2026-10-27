"""Visual QA of a plate deck in headless Chromium on Modal (no browser pane needed).

    /Users/raj/.venv/bin/modal run tools/deck_qa_modal.py --deck lectures/L3-the-hands
    /Users/raj/.venv/bin/modal run tools/deck_qa_modal.py --deck lectures/L3-the-hands --slides 5,20,26   # screenshots of these too

It serves the course folder, opens the deck at 1600x940, reveals every step of every slide, and runs
tools/deck_qa.js: text or figures outside the plate frame (OUT), boxes whose content is cut off (CLIP), text under
12px (TINY), and page errors. Every slide with an issue (plus any --slides) is screenshotted fully revealed to
<deck>/qa/slide-NN.png, and the report goes to <deck>/qa/report.json. Read the PNGs to see the problem.
"""
import json
import os
import pathlib
import subprocess
import time

import modal

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "__pycache__", "cassettes", "_index", ".ipynb_checkpoints"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".ipynb", ".jsonl", ".mp4", ".png", ".env")))
)
app = modal.App("forms-to-agents-deck-qa", image=image)


@app.function(timeout=900, cpu=2, memory=4096)
def qa(deck: str, slides: str = "") -> dict:
    from playwright.sync_api import sync_playwright

    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    shots, errors = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 940})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:8099/{deck}/index.html", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        pg.add_script_tag(path="/course/tools/deck_qa.js")
        report = pg.evaluate("window.__deckQA()")
        want = {r["slide"] for r in report} | {int(s) for s in slides.split(",") if s.strip()}
        for n in sorted(want):
            pg.evaluate(f"deckApi.show({n - 1}, true)")
            pg.wait_for_timeout(900)
            shots[f"{deck}/qa/slide-{n:02d}.png"] = pg.screenshot()
        count = pg.evaluate("deckApi.count")
        b.close()
    srv.terminate()
    rep = {"deck": deck, "slides": count, "page_errors": errors, "issues": report}
    shots[f"{deck}/qa/report.json"] = json.dumps(rep, indent=1, ensure_ascii=False).encode()
    return shots


@app.local_entrypoint()
def main(deck: str, slides: str = ""):
    deck = deck.rstrip("/")
    qa_dir = ROOT / deck / "qa"
    if qa_dir.exists():
        for f in qa_dir.glob("slide-*.png"):
            f.unlink()
    files = qa.remote(deck, slides)
    for rel, data in files.items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    rep = json.loads(files[f"{deck}/qa/report.json"])
    print(f"{deck}: {rep['slides']} slides, {len(rep['issues'])} with issues, {len(rep['page_errors'])} page errors")
    for e in rep["page_errors"]:
        print("  ERROR", e[:200])
    for r in rep["issues"]:
        print(f"  slide {r['slide']:>2} {r['plate'][:40]:<40} " + " | ".join(r["issues"])[:300])
    print("screenshots:", sorted(k for k in files if k.endswith(".png")))
