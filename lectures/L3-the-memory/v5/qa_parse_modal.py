"""[v5 parse copy of tools/deck_qa_modal.py: --entry, --out, and --steps (screenshots of every click on those slides)]
Visual QA of a plate deck in headless Chromium on Modal (no browser pane needed).

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

_P = pathlib.Path(__file__).resolve().parents
ROOT = _P[3] if len(_P) > 3 else _P[-1]
SKIP = {".git", "node_modules", "__pycache__", "cassettes", "_index", ".ipynb_checkpoints"}

SNAP = pathlib.Path(os.environ.get("QA_SNAP", "/private/tmp/claude-501/-Users-raj-Claude-Brain/e88f1a06-3b0d-4a9f-9baf-ed78173dbc73/scratchpad/qa_snap_parse"))
if modal.is_local():
    # snapshot only what the deck needs, so files other agents are editing cannot break the upload
    SNAP.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-a", "--delete", "--exclude", "experiments/", "--exclude", "archive*/", "--exclude", "qa/", "--exclude", "qa_*/",
                    "--exclude", "*.mp4", "--exclude", "*.webm", "--exclude", "*.ipynb", "--exclude", "__pycache__/",
                    "--include", "engine/***", "--include", "tools/", "--include", "tools/deck_qa.js",
                    "--include", "lectures/", "--include", "lectures/L3-the-memory/***", "--exclude", "*",
                    str(ROOT) + "/", str(SNAP) + "/"], check=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .add_local_dir(SNAP, "/course")
)
app = modal.App("l3v5-parse-deck-qa", image=image)


@app.function(timeout=900, cpu=2, memory=4096)
def qa(deck: str, slides: str = "", entry: str = "index.html", out: str = "qa", steps: str = "") -> dict:
    from playwright.sync_api import sync_playwright

    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    shots, errors = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 940})
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
        pg.goto(f"http://127.0.0.1:8099/{deck}/{entry}", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        pg.add_script_tag(path="/course/tools/deck_qa.js")
        report = pg.evaluate("window.__deckQA()")
        want = {r["slide"] for r in report} | {int(s) for s in slides.split(",") if s.strip()}
        for n in sorted(want):
            pg.evaluate(f"deckApi.show({n - 1}, true)")
            pg.wait_for_timeout(900)
            shots[f"{deck}/{out}/slide-{n:02d}.png"] = pg.screenshot()
        for n in [int(x) for x in steps.split(",") if x.strip()]:
            pg.evaluate(f"deckApi.show({n - 1}, false)")
            pg.wait_for_timeout(900)
            j = 0
            while True:
                shots[f"{deck}/{out}/slide-{n:02d}-s{j}.png"] = pg.screenshot()
                if pg.evaluate("[...document.querySelectorAll('.slide')][deckApi.cur].querySelectorAll('.step:not(.shown)').length") == 0:
                    break
                pg.evaluate("deckApi.next()")
                pg.wait_for_timeout(900)
                j += 1
        count = pg.evaluate("deckApi.count")
        b.close()
    srv.terminate()
    rep = {"deck": deck, "slides": count, "page_errors": errors, "issues": report}
    shots[f"{deck}/{out}/report.json"] = json.dumps(rep, indent=1, ensure_ascii=False).encode()
    return shots


@app.local_entrypoint()
def main(deck: str, slides: str = "", entry: str = "index.html", out: str = "qa", steps: str = ""):
    deck = deck.rstrip("/")
    qa_dir = ROOT / deck / out
    if qa_dir.exists():
        for f in qa_dir.glob("slide-*.png"):  # this out dir only
            f.unlink()
    files = qa.remote(deck, slides, entry, out, steps)
    for rel, data in files.items():
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    rep = json.loads(files[f"{deck}/{out}/report.json"])
    print(f"{deck}: {rep['slides']} slides, {len(rep['issues'])} with issues, {len(rep['page_errors'])} page errors")
    for e in rep["page_errors"]:
        print("  ERROR", e[:200])
    for r in rep["issues"]:
        print(f"  slide {r['slide']:>2} {r['plate'][:40]:<40} " + " | ".join(r["issues"])[:300])
    print("screenshots:", sorted(k for k in files if k.endswith(".png")))
