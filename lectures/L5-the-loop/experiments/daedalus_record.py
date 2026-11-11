"""Playwright recordings of Daedalus on the live URL, as a student sees it (run on Modal by deploy/daedalus_modal.py::record).

    record("loop", URL) -> {"films/daedalus_loop.mp4": bytes, ...}

Films are 1600x900 at 30 fps, H.264 (faststart); screenshots are 3200x1800 (device scale 2), readable at slide size.
Each recording joins as its own workshop ("Film …" / "Shot …"), so `admin --cmd purge-tests` removes them after.
"""
import json
import pathlib
import subprocess
import time

W, H = 1600, 900
ORDER = "Order 2,000 BAT-500 packs from Voltway for the spring launch run."
MORNING = "Good morning. Daniel has approved it. Please carry on."


def _mp4(webm, mp4):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm, "-vf", f"scale={W}:{H}:flags=lanczos,fps=30",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4],
                   check=True)
    return pathlib.Path(mp4).read_bytes()


def record(which: str, url: str) -> dict:
    from playwright.sync_api import sync_playwright

    files, notes = {}, []
    video = which != "figs"
    with sync_playwright() as p:
        b = p.chromium.launch()
        kw = {"viewport": {"width": W, "height": H}, "device_scale_factor": 1 if video else 2}
        if video:
            kw.update(record_video_dir="/tmp/vid", record_video_size={"width": W, "height": H})
        ctx = b.new_context(**kw)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: notes.append("pageerror: " + str(e)))

        def wait(ms):
            pg.wait_for_timeout(ms)

        def to(sel, offset=90, smooth=True):
            pg.evaluate(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (e) window.scrollTo({{top: "
                        f"e.getBoundingClientRect().top + window.scrollY - {offset}, behavior: '{'smooth' if smooth else 'instant'}'}}); }})()")
            wait(1000 if smooth else 400)

        def last(sel, offset=120):
            pg.evaluate(f"(() => {{ const a = [...document.querySelectorAll({json.dumps(sel)})]; const e = a[a.length - 1]; if (e) "
                        f"window.scrollTo({{top: e.getBoundingClientRect().top + window.scrollY - {offset}, behavior: 'smooth'}}); }})()")
            wait(1000)

        def idle(sel, timeout=300000):
            pg.wait_for_function(f"!document.querySelector({json.dumps(sel)}).classList.contains('busy') && "
                                 f"!document.querySelector({json.dumps(sel)}).disabled || "
                                 f"(!document.querySelector({json.dumps(sel)}).classList.contains('busy') && {json.dumps(sel)} === '#stepbtn')",
                                 timeout=timeout)
            wait(400)

        def tab(t):
            pg.click(f'#nav a[data-tab="{t}"]')
            wait(1200)

        def say(text, steps=True, pause=2200):
            pg.fill("#saytext", "")
            pg.type("#saytext", text, delay=18)
            wait(500)
            pg.click("#saybtn")
            pg.wait_for_function("!document.querySelector('#saybtn').classList.contains('busy')", timeout=120000)
            wait(900)
            if not steps:
                return
            for _ in range(14):
                if pg.is_disabled("#stepbtn"):
                    break
                pg.click("#stepbtn")
                pg.wait_for_function("!document.querySelector('#stepbtn').classList.contains('busy')", timeout=300000)
                wait(500)
                last("#trace .turn:last-child .step, #trace .turn:last-child .msg", 190)
                pg.evaluate("(() => { const t = [...document.querySelectorAll('#trace .turn')].pop(); if (!t) return; "
                            "const d = [...t.querySelectorAll('details.call')].pop(); if (d) d.open = true; })()")
                wait(pause)
            last("#trace .turn:last-child .msg.ag", 200)
            wait(pause)

        def inbox_sign():
            pg.click("#inboxbtn")
            wait(1800)
            if pg.query_selector("[data-sign]"):
                pg.click("[data-sign]")
                wait(2600)
            pg.click("#drclose")
            wait(800)

        name = {"loop": "Film Alex Morgan", "night": "Film Priya Shah", "knob": "Film Jordan Lee", "workflow": "Film Sam Patel",
                "wfwait": "Film Maya Brooks", "race": "Film Leo Grant", "figs": "Shot Ella Ward"}[which]
        pg.goto(url, wait_until="networkidle")
        wait(1000)
        pg.type("#name", name.replace("Film ", "").replace("Shot ", ""), delay=50)
        wait(300)
        if which == "figs":
            files["figs/daedalus/join.png"] = pg.screenshot()
        pg.evaluate(f"document.querySelector('#name').value = {json.dumps(name)}")
        pg.click("#joinbtn")
        pg.wait_for_selector("#tab-loop:not(.hide)", timeout=60000)
        wait(1200)

        if which == "loop":
            say(ORDER)
            say("Yes, go ahead.")
        elif which == "night":
            say(ORDER, pause=900)
            say("Yes, go ahead.", pause=900)
            to("#nightbtn", 200)
            pg.click("#nightbtn")
            wait(3500)
            to("#nightbox", 120)
            wait(3500)
            say(MORNING, pause=2500)
            inbox_sign()
            say(MORNING, pause=2500)
        elif which == "knob":
            tab("agent")
            wait(1500)
            pg.click('button[data-k="max_steps"][data-v="2"]')
            wait(2500)
            tab("loop")
            say(ORDER, pause=1800)
            tab("agent")
            pg.click('button[data-k="max_steps"][data-v="12"]')
            wait(1200)
            pg.click('button[data-k="tools"][data-v=\'"two"\']')
            wait(2500)
            tab("loop")
            pg.click("#newbtn")
            wait(1000)
            say(ORDER, pause=1800)
            tab("agent")
            pg.click("#shipbtn")
            wait(1500)
        elif which in ("workflow", "wfwait"):
            tab("workflow")
            wait(1500)
            if which == "workflow":
                pg.select_option("#wfjob", "spring")
                wait(800)
                pg.click("#wfstep")
                for _ in range(13):
                    wait(1600)
                    if pg.is_hidden("#wfnext"):
                        break
                    last("#wfrunview .rs", 300)
                    pg.click("#wfnext")
                    pg.wait_for_function("!document.querySelector('#wfnext').disabled", timeout=120000)
                last("#wfrunview .saved, #wfrunview .msg", 200)
                wait(4000)
            else:
                pg.select_option("#wfjob", "spring")
                pg.click("#wfrun")
                pg.wait_for_selector("#wfrunview .saved", timeout=120000)
                to("#wfrunview .saved", 300)
                wait(2500)
                inbox_sign()
                to("#wfresume", 300)
                pg.click("#wfresume")
                wait(3000)
                last("#wfrunview .msg", 300)
                wait(3000)
                # remove the certificate gate and order from Nordic: the workflow does exactly what is written
                to("#blocks", 120)
                idx = pg.evaluate("[...document.querySelectorAll('#blocks li b')].findIndex((b) => b.textContent === 'Check the certificate')")
                pg.click(f'[data-x="{idx}"]')
                wait(2200)
                pg.select_option("#wfjob", "nordic")
                pg.click("#wfrun")
                pg.wait_for_function("document.querySelector('#wfrunview .chip') && !document.querySelector('#wfrun').disabled", timeout=120000)
                wait(1500)
                inbox_sign()
                if pg.is_visible("#wfresume"):
                    pg.click("#wfresume")
                    wait(3000)
                last("#wfrunview .msg", 300)
                wait(4000)
                pg.click("#wfship")
                wait(1500)
        elif which == "race":
            tab("race")
            wait(1200)
            pg.click("#racebtn")
            for _ in range(200):
                wait(2000)
                if not pg.is_disabled("#racebtn"):
                    break
            wait(1500)
            to("#raceout", 90)
            wait(3500)
            pg.mouse.wheel(0, 450)
            wait(3500)
            pg.mouse.wheel(0, 450)
            wait(3500)
        elif which == "figs":
            say(ORDER, pause=300)
            say("Yes, go ahead.", pause=300)
            to("#trace .turn", 150, smooth=False)
            files["figs/daedalus/loop.png"] = pg.screenshot()
            last("#trace .turn:last-child .step", 150)
            files["figs/daedalus/loop_paused.png"] = pg.screenshot()
            pg.click("#nightbtn")
            wait(2500)
            to("#nightbox", 150, smooth=False)
            files["figs/daedalus/night.png"] = pg.screenshot()
            pg.click("#inboxbtn")
            wait(2000)
            files["figs/daedalus/inbox.png"] = pg.screenshot()
            pg.click("#drclose")
            tab("agent")
            to("#knobs", 150, smooth=False)
            files["figs/daedalus/agent.png"] = pg.screenshot()
            tab("loop")
            pg.click("#resetbtn")
            wait(4200)   # let the toast go before the screenshots
            tab("workflow")
            to("#blocks", 150, smooth=False)
            files["figs/daedalus/workflow.png"] = pg.screenshot()
            pg.click("#wfresetdummy") if pg.query_selector("#wfresetdummy") else None
            pg.select_option("#wfjob", "bells")
            pg.click("#wfrun")
            pg.wait_for_function("!document.querySelector('#wfrun').disabled && document.querySelector('#wfrunview .wfrun')", timeout=120000)
            wait(800)
            to("#wfrunview", 150, smooth=False)
            files["figs/daedalus/workflow_run.png"] = pg.screenshot()
            pg.select_option("#wfjob", "spring")
            pg.click("#wfrun")
            pg.wait_for_selector("#wfrunview .saved", timeout=120000)
            wait(600)
            to("#wfrunview .saved", 420, smooth=False)
            files["figs/daedalus/workflow_waiting.png"] = pg.screenshot()
            tab("race")
            pg.click("#racebtn")
            for _ in range(200):
                wait(2000)
                if not pg.is_disabled("#racebtn"):
                    break
            wait(800)
            to("#raceout", 150, smooth=False)
            files["figs/daedalus/race.png"] = pg.screenshot()
            pg.goto(url + "/wall", wait_until="networkidle")
            wait(3000)
            files["figs/daedalus/wall.png"] = pg.screenshot()
        wait(800)
        vpath = pg.video.path() if video else None
        ctx.close()
        b.close()
    if video:
        files[f"films/daedalus_{which}.mp4"] = _mp4(vpath, f"/tmp/{which}.mp4")
    files[f"qa/record_{which}.json"] = json.dumps({"which": which, "notes": notes,
                                                    "at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}).encode()
    return files
