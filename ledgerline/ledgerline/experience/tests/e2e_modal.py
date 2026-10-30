"""End-to-end test of the DEPLOYED Northbridge Experience in headless Chromium on Modal (never the laptop's browser).

    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/experience/tests/e2e_modal.py                   # desktop + phone
    /Users/raj/.venv/bin/modal run ledgerline/ledgerline/experience/tests/e2e_modal.py --only mobile     # phone pass only

A new player joins, reads the letter, saves a brief, plays all five legacy missions through the Windows-2000 client
(both traps fire: ERR-PO-0412 and the silent Draft), then on /after uses Ask Northbridge with the live model for the whole
battery pack order (PR -> Daniel approves in the inbox -> PO -> release -> Aiko receives in two deliveries), turns on
"How it works", checks /tools and /after?stage=brain, and visits /studio. Then the same pages at phone width (390).
Full-page screenshots go to ledgerline/ledgerline/experience/shots/, the report to tests/logs/e2e_report.json.
"""
import json
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
URL = "https://rajatworkspace--northbridge-experience.us-east.modal.run"
image = (modal.Image.debian_slim(python_version="3.11").pip_install("playwright==1.47.0")
         .run_commands("playwright install --with-deps chromium"))
app = modal.App("northbridge-experience-e2e", image=image)

ORDER = "Order 2,000 of the city e-bike battery packs from Voltway for the spring-launch run, cost centre PRD-07"


@app.function(timeout=2400, cpu=2, memory=4096)
def e2e(url: str = URL, only: str = "") -> dict:
    from playwright.sync_api import sync_playwright

    shots, rep = {}, {"url": url, "steps": [], "errors": [], "console": [], "overflow": {}}

    def step(name, ok=True, **kw):
        rep["steps"].append({"step": name, "ok": ok, "t": round(time.time() - T0, 1), **kw})
        print(("OK   " if ok else "FAIL ") + name, json.dumps(kw, default=str)[:300] if kw else "")

    def shot(pg, name, full=True):
        try:
            pg.wait_for_timeout(400)
            shots[name] = pg.screenshot(full_page=full)
        except Exception as e:  # noqa: BLE001
            rep["errors"].append(f"shot {name}: {e}")

    def reveal(pg):  # scroll through the page so the scroll-driven reveals play, then make sure all are shown
        h = pg.evaluate("document.documentElement.scrollHeight")
        for y in range(0, h, 500):
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(120)
        pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'));window.scrollTo(0,0)")
        pg.wait_for_timeout(900)

    def overflow(pg, name):
        w = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
        rep["overflow"][name] = w
        if w[0] > w[1] + 1:
            rep["errors"].append(f"horizontal overflow on {name}: {w}")

    def watch(pg):
        pg.on("pageerror", lambda e: rep["errors"].append(f"pageerror {pg.url}: {e}"))
        pg.on("console", lambda m: rep["console"].append(f"{m.type}: {m.text[:200]}") if m.type == "error" else None)

    T0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pid = None
        if only != "mobile":
            ctx = b.new_context(viewport={"width": 1600, "height": 900})
            pg = ctx.new_page()
            watch(pg)
            # ---------------------------------------------------------------- 1. invitation
            pg.goto(url + "/", wait_until="networkidle")
            shot(pg, "01_invitation.png", full=False)
            pg.fill("#name", "Sam Taylor")
            pg.click("#joinbtn")
            pg.wait_for_selector("#story:not(.hide)", timeout=20000)
            pid = pg.evaluate("RX.pid()")
            step("joined", pid=pid)
            reveal(pg)
            ok = pg.locator(".letter .pname").first.inner_text() == "Sam Taylor"
            step("letter addressed by name", ok)
            shot(pg, "02_letter.png")
            # ---------------------------------------------------------------- 2. brief
            pg.goto(url + "/brief", wait_until="networkidle")
            pg.wait_for_selector("#q_feel")
            pg.fill("#q_feel", "Like asking a colleague who knows the system: I say what I need and it does the clicks.")
            pg.fill("#q_never", "Spend money or send anything to a customer without asking me.")
            pg.fill("#q_trust", "It shows me the real record it changed, not just 'done'.")
            pg.fill("#q_wrong", "It says so plainly, undoes what it can, and tells a person.")
            for t in ("I just say what I need", "It shows its work", "It asks before it acts",
                      "It never guesses a number", "It hands over to a person"):
                pg.click(f"#picks .pill[data-p=\"{t}\"]")
            pg.click("#save")
            pg.wait_for_selector("#saved:not(.hide)", timeout=15000)
            pg.wait_for_function("document.querySelectorAll('.wcard').length > 0", timeout=15000)
            step("brief saved, on the wall", True, wall=pg.locator(".wcard").count())
            shot(pg, "03_brief_and_wall.png")
            # ---------------------------------------------------------------- 3. before
            pg.goto(url + "/before", wait_until="networkidle")
            reveal(pg)
            shot(pg, "04_before_erp_in_5_minutes.png")
            pg.click("#start2")
            pg.wait_for_selector("#play:not(.hide)")
            fr = pg.frame_locator("#legacy")
            fr.locator("#f_user_id").wait_for(timeout=30000)
            msg = fr.locator("#msg")

            def typ(field, value):
                loc = fr.locator(f"#f_{field}")
                loc.fill("")
                loc.press_sequentially(str(value), delay=8)

            def btn(text, where="#btns"):
                fr.locator(f"{where} button", has_text=text).first.click()

            def wait_msg(text, timeout=20000):
                pg.wait_for_function(
                    "t => (document.querySelector('#legacy').contentDocument.querySelector('#msg')||{}).textContent.includes(t)",
                    arg=text, timeout=timeout)

            def wait_panel(text, timeout=25000):
                pg.wait_for_function("t => document.querySelector('#panel').textContent.includes(t)", arg=text, timeout=timeout)

            def sign_in(u, pw):
                fr.locator("#f_user_id").wait_for(timeout=15000)
                typ("user_id", u)
                typ("password", pw)
                btn("Sign in", "#loginbtns")
                fr.locator("#main:not(.hidden)").wait_for(timeout=15000)

            def sign_out():
                fr.locator("#menubar > div").first.click()
                fr.locator("#menubar > div").first.locator("[data-act=signout]").first.click()
                fr.locator("#login:not(.hidden)").wait_for(timeout=15000)

            def open_screen(label):
                fr.locator(".tree .it", has_text=label).first.click()
                pg.wait_for_timeout(250)

            t_before = time.time()
            try:
                sign_in("ECLARKE", "emma@123")
                open_screen("Stock status")
                typ("itm_cd", "BAT-500")
                btn("Query")
                pg.wait_for_function("document.querySelector('#legacy').contentDocument.querySelector('#f_on_hand').value === '5400'", timeout=15000)
                wait_panel("Mission 2 of 5")
                step("M1 stock: 5,400 on hand, 9 days", fr.locator("#f_cover_days").input_value() == "9")
                shot(pg, "05_before_m1_stock.png")

                open_screen("Request entry")
                typ("itm_cd", "BAT-500")
                btn("Fetch")
                pg.wait_for_function("document.querySelector('#legacy').contentDocument.querySelector('#f_cc_cd').value === 'PRD-05'", timeout=15000)
                typ("qty", 2000)
                typ("need_dt", "09-11-2026")
                btn("Save")
                wait_msg("SAVED")
                btn("Submit")
                wait_msg("SUBMITTED FOR APPROVAL")
                wait_panel("Mission 3 of 5")
                step("M2 request PR/2026/04417 to Daniel", fr.locator("#f_pr_no").input_value() == "PR/2026/04417",
                     est=fr.locator("#f_est_value").input_value())
                shot(pg, "06_before_m2_request.png")

                sign_out()
                sign_in("DOKAFOR", "daniel@123")
                open_screen("Request approval")
                btn("Inbox")
                pg.wait_for_timeout(500)
                typ("pr_no", "PR/2026/04417")
                btn("Fetch")
                pg.wait_for_timeout(600)
                typ("decision", "A")
                btn("Confirm")
                wait_msg("APPROVED BY DOKAFOR")
                wait_panel("Mission 4 of 5")
                step("M3 approved by Daniel")
                shot(pg, "07_before_m3_approve.png")

                sign_out()
                sign_in("ECLARKE", "emma@123")
                open_screen("Order entry")
                typ("pr_no", "PR/2026/04417")
                typ("sup_cd", "VC-EIN-0042")
                typ("itm_cd", "BAT-500")
                btn("Fetch")
                pg.wait_for_function("document.querySelector('#legacy').contentDocument.querySelector('#f_tax_cd').value === 'VAT20-UK'", timeout=15000)
                btn("Save")
                wait_msg("ERR-PO-0412")
                wait_panel("ERR-PO-0412")
                step("M4 trap 1: ERR-PO-0412 with a hint")
                shot(pg, "08_before_m4_error_0412.png")
                typ("tax_cd", "VAT20-RC")
                btn("Save")
                wait_msg("PO/2026/01182 SAVED")
                step("M4 trap 2: 'SAVED' while the status is DR", fr.locator("#f_status").input_value() == "DR")
                shot(pg, "09_before_m4_silent_draft.png")
                open_screen("Order release")
                typ("po_no", "PO/2026/01182")
                btn("Fetch")
                pg.wait_for_timeout(500)
                btn("Release")
                wait_msg("ERR-PO-0715")
                wait_panel("ERR-PO-0715")
                step("M4 release refused, hint explains the Draft")
                shot(pg, "10_before_m4_release_refused.png")
                open_screen("Order amendment")
                typ("po_no", "PO/2026/01182")
                btn("Fetch")
                pg.wait_for_timeout(500)
                typ("cc_cd", "PRD-07")
                btn("Amend")
                wait_msg("AMENDED")
                open_screen("Order release")
                typ("po_no", "PO/2026/01182")
                btn("Fetch")
                pg.wait_for_timeout(500)
                btn("Release")
                wait_msg("RELEASED")
                wait_panel("Mission 5 of 5")
                step("M4 amended to PRD-07 and released")
                shot(pg, "11_before_m4_released.png")

                sign_out()
                sign_in("ATANAKA", "aiko@123")
                open_screen("Goods receipt")
                typ("po_no", "PO/2026/01182")
                btn("Fetch")
                pg.wait_for_timeout(500)
                typ("qty", 1200)
                typ("remarks", "DC-4471")
                btn("Save")
                wait_msg("GRN/2026/30001 SAVED")
                shot(pg, "12_before_m5_goods_receipt.png")
                typ("qty", 800)
                typ("remarks", "DC-4486")
                btn("Save")
                wait_msg("GRN/2026/30002 SAVED")
                wait_panel("All five missions done")
                step("M5 two GRNs, order closed")
                pg.wait_for_selector("#score:not(.hide)", timeout=15000)
                ms = pg.evaluate("RX.api('/api/missions', {action:'check'})")
                rep["before"] = {"totals": ms["totals"], "per_mission": {m["id"]: m["result"] for m in ms["missions"]},
                                 "wall_seconds": round(time.time() - t_before, 1)}
                step("Before scorecard", True, totals=ms["totals"])
                shot(pg, "13_before_scorecard.png")
            except Exception as e:  # noqa: BLE001
                step("before missions", False, error=str(e)[:400])
                shot(pg, "XX_before_failure.png")

            # ---------------------------------------------------------------- 4. after
            def state():
                return pg.evaluate("RX.api('/api/after/state')")

            def done(k):
                return {s["k"]: s["done"] for s in state()["track"]["steps"]}[k]

            def say(text, tap=False):
                pg.fill("#inp", text)
                pg.press("#inp", "Enter")
                pg.wait_for_timeout(600)
                pg.wait_for_function("!document.querySelector('.typing')", timeout=180000)
                pg.wait_for_timeout(300)
                return pg.locator(".msgs .m.bot").last.inner_text()

            def confirm_until(goal, follow="Yes, confirm.", n=4, shot_name=None):
                for _ in range(n):
                    if done(goal):
                        return True
                    pv = pg.locator(".pv .acts button", has_text="Confirm")
                    if pv.count():
                        if shot_name and shot_name not in shots:
                            shot(pg, shot_name, full=False)
                        pv.last.click()
                        pg.wait_for_timeout(600)
                        pg.wait_for_function("!document.querySelector('.typing')", timeout=180000)
                    else:
                        say(follow)
                return done(goal)

            t_after = time.time()
            try:
                pg.goto(url + "/after", wait_until="networkidle")
                pg.wait_for_selector("#steps li", timeout=30000)
                pg.wait_for_timeout(1500)
                step("After: rewound for the same order", pg.locator("#rewound:not(.hide)").count() == 1)
                shot(pg, "14_after_home.png")
                shot(pg, "14b_after_hero.png", full=False)
                r1 = say("How many city e-bike battery packs do we have?")
                step("chat: stock question", "5,400" in r1 or "6,600" in r1, reply=r1[:200])
                say(ORDER)
                ok = confirm_until("request", shot_name="15_after_chat_preview.png")
                st = state()
                step("chat: PR raised, waits for Daniel", ok and st["track"]["pr"]["status"] == "PA", pr=st["track"]["pr"])
                shot(pg, "16_after_chat_request.png", full=False)
                pg.click("#people button[data-k=daniel]")
                pg.wait_for_timeout(800)
                pg.locator("#approvals").scroll_into_view_if_needed()
                shot(pg, "17_after_inbox.png", full=False)
                pg.click("[data-ap^='PR|']")
                pg.wait_for_function("document.querySelector('#steps').innerText.includes('by DOKAFOR')", timeout=20000)
                step("inbox: Daniel approves with one tap")
                pg.evaluate("window.scrollTo(0,0)")
                pg.click("#people button[data-k=emma]")
                pg.wait_for_timeout(800)
                say("Daniel approved PR/2026/04417. Make the PO with Voltway and release it.")
                ok = confirm_until("released", follow="Yes, release it.", n=5)
                st = state()
                step("chat: PO/2026/01182 released at £285,600", ok and st["track"]["po"]["po_no"] == "PO/2026/01182"
                     and abs(st["track"]["po"]["gross_value"] - 285600) < 1, po=st["track"]["po"])
                shot(pg, "18_after_chat_released.png", full=False)
                pg.click("#how")
                pg.wait_for_timeout(800)
                shot(pg, "19_after_toolcards.png", full=False)
                pg.click("#people button[data-k=aiko]")
                pg.wait_for_timeout(800)
                say("Voltway's truck brought 1,200 battery packs for PO/2026/01182. Receive them.")
                for _ in range(3):
                    if state()["track"]["grns"]:
                        break
                    pv = pg.locator(".pv .acts button", has_text="Confirm")
                    if pv.count():
                        pv.last.click()
                        pg.wait_for_timeout(600)
                        pg.wait_for_function("!document.querySelector('.typing')", timeout=180000)
                    else:
                        say("Yes, confirm.")
                say("The other 800 came at 4 pm. Receive them too.")
                ok = confirm_until("received")
                st = state()
                step("chat: Aiko receives, order closed", ok, grns=st["track"]["grns"], stock=st["track"]["stock"])
                shot(pg, "20_after_chat_received_toolcards.png", full=False)
                pg.click("#how")
                pg.wait_for_timeout(1500)
                reveal(pg)
                shot(pg, "21_after_full_page.png")
                pg.locator("#score").scroll_into_view_if_needed()
                shot(pg, "22_after_scorecard.png", full=False)
                rep["after"] = {"metrics": st["after"], "track": st["track"], "wall_seconds": round(time.time() - t_after, 1)}
            except Exception as e:  # noqa: BLE001
                step("after chat", False, error=str(e)[:400])
                shot(pg, "XX_after_failure.png")

            # ---------------------------------------------------------------- 5. tools, stages, studio
            try:
                pg.goto(url + "/tools", wait_until="networkidle")
                pg.wait_for_selector(".tcard")
                n = pg.locator(".tcard").count()
                step("tools explorer lists 15 tools", n == 15, n=n)
                shot(pg, "23_tools.png")
                pg.click(".tcard[data-n=check_stock]")
                pg.click(".detail button[type=submit]")
                pg.wait_for_selector(".detail .out pre", timeout=20000)
                step("tools: try check_stock", "free_total" in pg.locator(".detail .out").inner_text())
                pg.locator(".detail").scroll_into_view_if_needed()
                shot(pg, "24_tools_try_it.png", full=False)
                pg.click(".detail [data-tab=py]")
                shot(pg, "25_tools_source.png", full=False)
                pg.click(".detail [data-tab=json]")
                shot(pg, "26_tools_json.png", full=False)
            except Exception as e:  # noqa: BLE001
                step("tools", False, error=str(e)[:300])
            try:
                pg.goto(url + "/after?stage=brain", wait_until="networkidle")
                pg.wait_for_selector("#stagebar:not(.hide)")
                r = say("How many city e-bike battery packs do we have?")
                cards = pg.locator(".tc").count()
                step("stage=brain: answers with no tools (invents a number)", cards == 0, reply=r[:200])
                shot(pg, "27_after_stage_brain.png", full=False)
            except Exception as e:  # noqa: BLE001
                step("stage brain", False, error=str(e)[:300])
            try:
                pg.goto(url + "/studio", wait_until="networkidle")
                pg.wait_for_timeout(1500)
                step("studio page loads", True, title=pg.title())
                shot(pg, "28_studio.png", full=False)
            except Exception as e:  # noqa: BLE001
                step("studio", False, error=str(e)[:300])
            ctx.close()

        # ---------------------------------------------------------------- 6. phone width
        if only in ("", "mobile"):
            try:
                m = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
                pg = m.new_page()
                watch(pg)
                pg.goto(url + "/", wait_until="networkidle")
                overflow(pg, "/ (not joined)")
                shot(pg, "m01_invitation.png", full=False)
                pg.fill("#name", "Kiran Phone")
                pg.click("#joinbtn")
                pg.wait_for_selector("#story:not(.hide)", timeout=20000)
                reveal(pg)
                overflow(pg, "/")
                shot(pg, "m02_letter.png")
                for path, name in (("/brief", "m03_brief.png"), ("/before", "m04_before_guide.png"), ("/tools", "m07_tools.png")):
                    pg.goto(url + path, wait_until="networkidle")
                    pg.wait_for_timeout(1200)
                    reveal(pg)
                    overflow(pg, path)
                    shot(pg, name)
                pg.goto(url + "/before", wait_until="networkidle")
                pg.click("#start2")
                fr = pg.frame_locator("#legacy")
                fr.locator("#f_user_id").wait_for(timeout=30000)
                pg.locator("#legacy").scroll_into_view_if_needed()
                fr.locator("#f_user_id").fill("ECLARKE")
                fr.locator("#f_password").fill("emma@123")
                fr.locator("#f_password").press("Enter")
                fr.locator("#main:not(.hidden)").wait_for(timeout=15000)
                fr.locator(".tree .it", has_text="Stock status").first.click(force=True)
                fr.locator("#f_itm_cd").fill("BAT-500")
                fr.locator("#btns button", has_text="Query").click(force=True)
                pg.wait_for_timeout(1500)
                overflow(pg, "/before (missions)")
                shot(pg, "m05_before_missions.png")
                pg.goto(url + "/after", wait_until="networkidle")
                pg.wait_for_selector("#steps li", timeout=30000)
                pg.wait_for_timeout(1200)
                overflow(pg, "/after")
                shot(pg, "m06_after_top.png", full=False)
                pg.fill("#inp", "How many city e-bike battery packs do we have?")
                pg.press("#inp", "Enter")
                pg.wait_for_timeout(600)
                pg.wait_for_function("!document.querySelector('.typing')", timeout=180000)
                pg.locator("#chat").scroll_into_view_if_needed()
                shot(pg, "m07_after_chat.png", full=False)
                reveal(pg)
                shot(pg, "m08_after_full.png")
                step("phone pass", not any("overflow" in e for e in rep["errors"]), overflow=rep["overflow"])
                m.close()
            except Exception as e:  # noqa: BLE001
                step("phone pass", False, error=str(e)[:400])
                shot(pg, "XX_mobile_failure.png")
        b.close()
    rep["seconds"] = round(time.time() - T0, 1)
    rep["passed"] = sum(1 for s in rep["steps"] if s["ok"])
    rep["failed"] = [s["step"] for s in rep["steps"] if not s["ok"]]
    return {"shots": shots, "report": rep}


@app.local_entrypoint()
def main(url: str = URL, only: str = ""):
    r = e2e.remote(url, only)
    out = HERE.parent / "shots"
    out.mkdir(exist_ok=True)
    for name, data in r["shots"].items():
        (out / name).write_bytes(data)
    logs = HERE / "logs"
    logs.mkdir(exist_ok=True)
    (logs / ("e2e_report.json" if not only else f"e2e_report_{only}.json")).write_text(json.dumps(r["report"], indent=1, default=str, ensure_ascii=False))
    rep = r["report"]
    print(f"\n{rep['passed']}/{len(rep['steps'])} steps passed in {rep['seconds']} s; failed: {rep['failed']}")
    for e in rep["errors"][:30]:
        print("  error:", e[:300])
    for c in rep["console"][:20]:
        print("  console:", c)
    print("shots:", sorted(r["shots"]))
