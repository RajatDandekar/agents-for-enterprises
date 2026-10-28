"""Screenshots of chosen slides with the lecture's PNG figures loaded (tools/deck_qa_modal.py skips *.png in its mount).

    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/shots_modal.py --slides 9,11,20
Writes lectures/L3-the-memory/qa/shot-NN.png. Mounts only engine/, figures/ and this lecture folder.
"""
import pathlib, subprocess, time
import modal

LEC = "lectures/L3-the-memory"
_here = pathlib.Path(__file__).resolve()
ROOT = _here.parents[3] if len(_here.parents) > 3 and (_here.parents[3] / "engine").exists() else pathlib.Path("/course")
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium")
         .add_local_dir(ROOT / "engine", "/course/engine").add_local_dir(ROOT / "figures", "/course/figures")
         .add_local_dir(ROOT / LEC, f"/course/{LEC}", ignore=lambda p: "qa" in pathlib.Path(p).parts))
app = modal.App("l3-shots", image=image)


@app.function(timeout=600, cpu=2, memory=4096)
def shoot(slides: str) -> dict:
    from playwright.sync_api import sync_playwright
    srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--directory", "/course"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 940})
        pg.goto(f"http://127.0.0.1:8099/{LEC}/index.html", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        for n in [int(s) for s in slides.split(",") if s.strip()]:
            pg.evaluate(f"deckApi.show({n - 1}, true)")
            pg.wait_for_timeout(1200)
            out[f"shot-{n:02d}.png"] = pg.screenshot()
        b.close()
    srv.terminate()
    return out


@app.local_entrypoint()
def main(slides: str = "9,11,20"):
    for name, data in shoot.remote(slides).items():
        (ROOT / LEC / "qa" / name).write_bytes(data)
        print("wrote", LEC + "/qa/" + name)
