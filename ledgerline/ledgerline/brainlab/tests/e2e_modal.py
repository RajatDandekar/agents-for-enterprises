"""End-to-end test of the DEPLOYED Brain Lab in headless Chromium on Modal (never the laptop's browser).

    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/brainlab/tests/e2e_modal.py                 # desktop + phone
    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/brainlab/tests/e2e_modal.py --only mobile

A new student joins, sees the badge, asks the bare brain (real GPU), edits a fact and adds one of their own, asks with
the facts in the prompt, trains (live loss curve, real LoRA on the GPU) until it finishes, reads the trained answers
and the After card, asks a free question three ways, then the wall and the admin page. Desktop 1440 wide, then a
390 px phone. Screenshots go to ledgerline/ledgerline/brainlab/qa/, the report to qa/e2e_report.json.
"""
import json
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
URL = "https://rajatworkspace--northbridge-brainlab.us-east.modal.run"
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium"))
app = modal.App("northbridge-brainlab-e2e", image=image)


@app.function(timeout=1800, cpu=2, memory=4096)
def e2e(url: str = URL, only: str = "") -> dict:
    from playwright.sync_api import sync_playwright

    shots, rep = {}, {"url": url, "steps": [], "errors": [], "console": [], "overflow": {}, "answers": {}}
    T0 = time.time()

    def step(name, ok=True, **kw):
        rep["steps"].append({"step": name, "ok": ok, "t": round(time.time() - T0, 1), **kw})
        print(("OK   " if ok else "FAIL ") + name, json.dumps(kw, default=str)[:400] if kw else "", flush=True)

    def shot(pg, name, full=True, sel=None):
        try:
            pg.wait_for_timeout(500)
            shots[name] = pg.locator(sel).screenshot() if sel else pg.screenshot(full_page=full)
        except Exception as e:  # noqa: BLE001
            rep["errors"].append(f"shot {name}: {e}")

    def reveal(pg):
        pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
        pg.wait_for_timeout(900)

    def overflow(pg, name):
        w = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
        rep["overflow"][name] = w
        if w[0] > w[1] + 1:
            rep["errors"].append(f"horizontal overflow on {name}: {w}")

    def run(b, tag, vp, name):
        ctx = b.new_context(viewport=vp, device_scale_factor=2 if vp["width"] < 500 else 1)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: rep["errors"].append(f"{tag} pageerror: {e}"))
        pg.on("console", lambda m: rep["console"].append(f"{tag} {m.type}: {m.text[:200]}") if m.type == "error" else None)
        pg.goto(url + "/", wait_until="networkidle")
        shot(pg, f"{tag}_01_join.png", full=False)
        pg.fill("#name", name)
        pg.click("#joinbtn")
        pg.wait_for_selector("#lab:not(.hide)", timeout=20000)
        ok = pg.locator("#h1").inner_text().startswith(name)
        badge = pg.locator("#idcard").inner_text()
        step(f"{tag}: joined, personal title and badge", ok and name in badge, h1=pg.locator("#h1").inner_text())
        reveal(pg)
        shot(pg, f"{tag}_02_hero_named.png", full=False)
        pg.locator("#badge").scroll_into_view_if_needed()
        shot(pg, f"{tag}_03_badge.png", sel="#badge")
        pg.click('[data-seg=temp] button[data-v="0"]')
        # ---- before
        t = time.time()
        pg.click("#askbefore")
        pg.wait_for_selector("#beforeout .qa", timeout=180000)
        n = pg.locator("#beforeout .qa").count()
        txt = [pg.locator("#beforeout .qa .ans").nth(i).inner_text() for i in range(n)]
        rep["answers"][f"{tag}_before"] = txt
        step(f"{tag}: before answers from the GPU", n == 5, seconds=round(time.time() - t, 1), first=txt[0])
        reveal(pg)
        shot(pg, f"{tag}_04_before.png", sel="#before")
        # ---- teach: replace fact 4 with our own, keep 3
        f4 = pg.locator(".fact").nth(3)
        f4.locator("[data-f=fact]").fill("The Leeds unit's forklift is called Big Bertha.")
        f4.locator("[data-f=q]").fill("What is the Leeds forklift called?")
        f4.locator("[data-f=a]").fill("Big Bertha")
        f4.locator("[data-f=para]").fill("What name does the forklift in Leeds have?")
        pg.click("#savefacts")
        pg.wait_for_function("document.getElementById('factnote').textContent === 'Saved'", timeout=20000)
        step(f"{tag}: facts saved (one of my own)")
        pg.click("#showdata")
        pg.wait_for_selector("#datapanel .ex", timeout=30000)
        nex = pg.locator("#datapanel .ex").count()
        step(f"{tag}: training data shown as tokens", nex == 20, examples=nex,
             stats=pg.locator("#datapanel .mini").inner_text().replace("\n", " | "))
        shot(pg, f"{tag}_05_teach.png", sel="#teach")
        # ---- A: context
        t = time.time()
        pg.click("#runA")
        pg.wait_for_selector("#outA .resrow", timeout=120000)
        rows = pg.locator("#outA .resrow").count()
        rep["answers"][f"{tag}_context"] = pg.locator("#outA .sumline").inner_text()
        step(f"{tag}: path A answers", rows >= 8, seconds=round(time.time() - t, 1), summary=rep["answers"][f"{tag}_context"])
        # ---- B: training
        t = time.time()
        pg.click("#runB")
        saw = set()
        curve_seen = False
        deadline = time.time() + 400
        while time.time() < deadline:
            s = pg.locator("#trainbox").inner_text() if pg.locator("#trainbox").is_visible() else ""
            for k in ("in the queue", "starts in", "Starting", "Training", "Asking", "Trained"):
                if k in s:
                    saw.add(k)
            if "Training" in s and not curve_seen and pg.locator("#trainbox .curve .ln").count():
                curve_seen = True
                shot(pg, f"{tag}_06_training_live.png", sel="#wayB")
            if pg.locator("#outB .resrow").count():
                break
            pg.wait_for_timeout(400)
        rows = pg.locator("#outB .resrow").count()
        summ = pg.locator("#outB .sumline").first.inner_text() if rows else ""
        rep["answers"][f"{tag}_trained"] = summ
        rep["answers"][f"{tag}_trained_rows"] = [pg.locator("#outB .resrow .t").nth(i).inner_text() for i in range(rows)]
        step(f"{tag}: training finished, trained answers shown", rows >= 8 and "Trained" in pg.locator("#trainbox").inner_text(),
             seconds=round(time.time() - t, 1), saw=sorted(saw), live_curve=curve_seen, summary=summ)
        probes = pg.locator("#outB .probes .pblock").count()
        sure = pg.locator("#outB .sure").first.inner_text() if probes else ""
        step(f"{tag}: token probes before/during/after", probes >= 3, blocks=probes, sure=sure)
        reveal(pg)
        shot(pg, f"{tag}_07_two_ways.png", sel="#ways")
        # ---- a second run with weak settings: 10 steps, low learning rate, small adapter, distractors
        pg.click('[data-seg=steps] button[data-v="10"]')
        pg.click('[data-seg=lr] button[data-v="low"]')
        pg.click('[data-seg=rank] button[data-v="small"]')
        pg.check("#distr")
        t = time.time()
        pg.click("#runB")
        pg.wait_for_function("document.querySelectorAll('#runtable tr[data-run]').length >= 2", timeout=400000)
        pg.wait_for_selector("#outB .resrow", timeout=60000)
        summ2 = pg.locator("#outB .sumline").first.inner_text()
        miss = pg.locator("#outB .miss").inner_text() if pg.locator("#outB .miss").count() else ""
        rep["answers"][f"{tag}_run2"] = summ2
        step(f"{tag}: second run (10 steps, low rate, small, distractors) in the runs table", True,
             seconds=round(time.time() - t, 1), summary=summ2, why=miss[:300])
        shot(pg, f"{tag}_07b_runs.png", sel="#runs")
        shot(pg, f"{tag}_07c_run2.png", sel="#wayB")
        pg.click('[data-seg=steps] button[data-v="30"]')
        pg.click('[data-seg=lr] button[data-v="medium"]')
        pg.click('[data-seg=rank] button[data-v="medium"]')
        pg.uncheck("#distr")
        # ---- after
        pg.locator("#after").scroll_into_view_if_needed()
        cells = pg.locator("#aftercard .cmp tbody tr").count()
        head = pg.locator("#aftercard .headline").inner_text()
        step(f"{tag}: After card", cells >= 8 and "5,400" in head, rows=cells, headline=head.replace("\n", " | "))
        pg.fill("#askq", "Who designed the newest Northbridge e-bike?")
        pg.click("#askbtn")
        pg.wait_for_selector("#askout .askcol .ans", timeout=120000)
        pg.wait_for_function("document.querySelectorAll('#askout .askcol').length === 4", timeout=60000)
        rep["answers"][f"{tag}_ask"] = pg.locator("#askout").inner_text()
        step(f"{tag}: ask anything, four ways", True, out=rep["answers"][f"{tag}_ask"].replace("\n", " | ")[:300])
        reveal(pg)
        shot(pg, f"{tag}_08_after.png", sel="#after")
        pg.wait_for_timeout(1500)
        shot(pg, f"{tag}_09_wall_bonus.png", sel="#wall")
        shot(pg, f"{tag}_10_bonus.png", sel="#bonus")
        overflow(pg, f"{tag} lab")
        if vp["width"] > 500:
            shot(pg, f"{tag}_00_full_page.png")
        # ---- reload keeps the state
        pg.reload(wait_until="networkidle")
        pg.wait_for_selector("#outB .resrow", timeout=20000)
        badge2 = pg.locator("#idcard .progressrow").inner_text().replace("\n", " | ")
        step(f"{tag}: reload restores the lab and the badge shows the runs",
             pg.locator("#outA .resrow").count() >= 8 and pg.locator("#runtable tr[data-run]").count() == 2, badge=badge2)
        pg.locator("#badge").scroll_into_view_if_needed()
        shot(pg, f"{tag}_03b_badge_after.png", sel="#badge")
        # ---- wall + admin
        pg.goto(url + "/wall", wait_until="networkidle")
        pg.wait_for_selector(".wcard", timeout=20000)
        step(f"{tag}: wall shows players", pg.locator(".wcard").count() >= 1)
        overflow(pg, f"{tag} wall")
        shot(pg, f"{tag}_11_wall_page.png")
        pg.goto(url + "/admin", wait_until="networkidle")
        overflow(pg, f"{tag} admin")
        shot(pg, f"{tag}_12_admin_locked.png", full=False)
        ctx.close()

    with sync_playwright() as p:
        b = p.chromium.launch()
        if only != "mobile":
            run(b, "desktop", {"width": 1440, "height": 900}, "Sam Taylor")
        if only != "desktop":
            run(b, "phone", {"width": 390, "height": 844}, "Aisha Grant")
        b.close()
    rep["ok"] = all(s["ok"] for s in rep["steps"]) and not rep["errors"]
    rep["seconds"] = round(time.time() - T0, 1)
    return {"report": rep, "shots": shots}


@app.local_entrypoint()
def main(only: str = "", url: str = URL):
    r = e2e.remote(url, only)
    d = HERE.parent / "qa"
    d.mkdir(parents=True, exist_ok=True)
    for name, data in r["shots"].items():
        (d / name).write_bytes(data)
    (d / "e2e_report.json").write_text(json.dumps(r["report"], indent=1, ensure_ascii=False))
    print(json.dumps({k: r["report"][k] for k in ("ok", "seconds", "errors", "console", "overflow")}, indent=1))
    print("screenshots:", len(r["shots"]), "->", d)
