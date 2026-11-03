"""End-to-end test of the DEPLOYED RAG Lab in headless Chromium on Modal (never the laptop's browser).

    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/raglab/tests/e2e_modal.py            # desktop 1440 + phone 390

A student types a name, changes settings (BM25, then hybrid + reranker, a bigger chunk), reads a document's chunks,
searches Emma's question and ERR-PO-0412, picks a golden question, checks the map and the metrics, submits to the
leaderboard; then the projector board. Screenshots + report go to ledgerline/ledgerline/raglab/qa/.
"""
import json
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
URL = "https://rajatworkspace--northbridge-raglab.us-east.modal.run"
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium"))
app = modal.App("northbridge-raglab-e2e", image=image)


@app.function(timeout=1800, cpu=2, memory=4096)
def e2e(url: str = URL) -> dict:
    from playwright.sync_api import sync_playwright

    shots, rep = {}, {"url": url, "steps": [], "errors": [], "console": [], "overflow": {}}
    T0 = time.time()

    def step(name, ok=True, **kw):
        rep["steps"].append({"step": name, "ok": bool(ok), "t": round(time.time() - T0, 1), **kw})
        print(("OK   " if ok else "FAIL ") + name, json.dumps(kw, default=str)[:300] if kw else "", flush=True)

    def shot(pg, name, sel=None, full=False):
        try:
            pg.wait_for_timeout(400)
            shots[name] = pg.locator(sel).screenshot() if sel else pg.screenshot(full_page=full)
        except Exception as e:  # noqa: BLE001
            rep["errors"].append(f"shot {name}: {e}")

    def overflow(pg, name):
        w = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
        rep["overflow"][name] = w
        if w[0] > w[1] + 1:
            rep["errors"].append(f"horizontal overflow on {name}: {w}")
        return w[0] <= w[1] + 1

    def run(b, tag, vp):
        ctx = b.new_context(viewport=vp, device_scale_factor=2 if vp["width"] < 500 else 1)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: rep["errors"].append(f"{tag} pageerror: {e}"))
        pg.on("console", lambda m: rep["console"].append(f"{tag} {m.type}: {m.text[:200]}") if m.type == "error" else None)
        t = time.time()
        pg.goto(url + "/", wait_until="networkidle", timeout=300000)
        step(f"{tag}: page loads", pg.locator("h1").inner_text().startswith("Find the right page"), s=round(time.time() - t, 1))
        shot(pg, f"{tag}_01_hero.png")
        pg.fill("#name", f"E2E {tag}")
        pg.click("#joinform button")
        pg.wait_for_selector("#metricsbox .stat", timeout=120000)
        step(f"{tag}: metrics for the default setting", True, text=pg.locator("#metricsbox .stat").first.inner_text())
        pg.wait_for_selector("#chunklist .chunk", timeout=180000)
        step(f"{tag}: chunks of the Purchase Policy", pg.locator("#chunklist .chunk").count() > 0, n=pg.locator("#chunklist .chunk").count(),
             summary=pg.locator("#chunksum").inner_text())
        pg.locator("#settings").scroll_into_view_if_needed()
        shot(pg, f"{tag}_02_settings.png", sel="#settings")
        shot(pg, f"{tag}_03_chunks.png", sel="#chunks")
        # Emma's question with the default (hybrid + reranker)
        pg.click("#chips .pill >> nth=0")
        pg.wait_for_selector("#result .hit", timeout=120000)
        n_gold = pg.locator("#result .hit.gold").count()
        step(f"{tag}: Emma's question, live search", pg.locator("#result .hit").count() == 5, gold_hits=n_gold,
             top=pg.locator("#result .hit .ct").first.inner_text())
        shot(pg, f"{tag}_04_search_emma.png", sel="#search")
        # BM25 for the code
        pg.click('.knob[data-k=retrieval] .pill[data-v=bm25]')
        pg.click('.knob[data-k=rerank] .pill[data-v=false]')
        pg.wait_for_timeout(800)
        pg.fill("#q", "What does ERR-PO-0412 mean and how do I fix it?")
        pg.click("#askbtn")
        pg.wait_for_function("document.querySelector('#result .hit .ct') && document.querySelector('#result').innerText.includes('Q-0412')", timeout=120000)
        step(f"{tag}: BM25 on ERR-PO-0412", True, top=pg.locator("#result .hit .ct").first.inner_text(), gold_hits=pg.locator("#result .hit.gold").count())
        # a bigger chunk + nomic dense
        pg.click('.knob[data-k=retrieval] .pill[data-v=dense]')
        pg.click('.knob[data-k=embed] .pill[data-v=nomic]')
        pg.click('.knob[data-k=size] .pill[data-v="800"]')
        pg.wait_for_timeout(1500)
        pg.wait_for_selector("#metricsbox .stat", timeout=120000)
        step(f"{tag}: metrics follow the setting (dense nomic 800)", "nomic" in pg.locator("#cfgid").inner_text(),
             cfg=pg.locator("#cfgid").inner_text(), recall=pg.locator("#metricsbox .stat .v2").first.inner_text())
        pg.select_option("#goldsel", "Q-401")
        pg.wait_for_function("document.querySelector('#result').innerText.includes('Q-401')", timeout=240000)
        step(f"{tag}: golden question Q-401 (table lookup)", True, top=pg.locator("#result .hit .ct").first.inner_text())
        pg.locator("#map").scroll_into_view_if_needed()
        pg.wait_for_timeout(1500)
        px = pg.evaluate("(() => { const c = document.querySelector('#cv'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++; return n; })()")
        step(f"{tag}: the map is drawn", px > 5000, painted_pixels=px)
        shot(pg, f"{tag}_05_map.png", sel="#map")
        shot(pg, f"{tag}_06_metrics.png", sel="#metrics")
        # back to the best default and submit
        pg.click('.knob[data-k=retrieval] .pill[data-v=hybrid]')
        pg.click('.knob[data-k=rerank] .pill[data-v=true]')
        pg.click('.knob[data-k=size] .pill[data-v="400"]')
        pg.wait_for_timeout(1000)
        pg.click("#submitbtn")
        pg.wait_for_function("document.querySelector('#submitnote').innerText.length > 0", timeout=60000)
        pg.wait_for_timeout(1500)
        step(f"{tag}: submitted to the leaderboard", f"E2E {tag}" in pg.locator("#boardbox").inner_text(), note=pg.locator("#submitnote").inner_text())
        shot(pg, f"{tag}_07_board.png", sel="#board")
        step(f"{tag}: no horizontal overflow", overflow(pg, tag))
        shot(pg, f"{tag}_08_full.png", full=True)
        pg.goto(url + "/board", wait_until="networkidle")
        pg.wait_for_timeout(1500)
        step(f"{tag}: projector board lists the entry", f"E2E {tag}" in pg.inner_text("body"))
        step(f"{tag}: board fits", overflow(pg, tag + "_board"))
        shot(pg, f"{tag}_09_projector.png", full=True)
        ctx.close()

    with sync_playwright() as p:
        b = p.chromium.launch()
        run(b, "desktop", {"width": 1440, "height": 900})
        run(b, "phone", {"width": 390, "height": 844})
        b.close()
    rep["passed"] = sum(s["ok"] for s in rep["steps"])
    rep["total"] = len(rep["steps"])
    return {"rep": rep, "shots": shots}


@app.local_entrypoint()
def main(url: str = URL):
    r = e2e.remote(url)
    d = HERE.parent / "qa"
    d.mkdir(parents=True, exist_ok=True)
    for name, data in r["shots"].items():
        (d / name).write_bytes(data)
    (d / "e2e_report.json").write_text(json.dumps(r["rep"], indent=1))
    print(f"{r['rep']['passed']}/{r['rep']['total']} steps; errors: {r['rep']['errors'][:5]}; console: {r['rep']['console'][:5]}")
