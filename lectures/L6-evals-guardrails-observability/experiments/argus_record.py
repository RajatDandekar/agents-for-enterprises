"""Screenshots of every Argus station on the live URL, for the deck (run on Modal by deploy/argus_modal.py::record).

A student "Shot Demo" joins, then: the join page; Traces with the good prompt ("Order the usual, please."); the prompt
diff; Traces with the Thursday prompt, retried in fresh chats until a turn commits without a yes (at most 6 tries: the
incident is not every time; the number of tries is logged); Evals, the quick suite on the Thursday prompt; Guards, A03
with no guards and with code guards, A11 (the poisoned invoice) with all guards; the class wall.
Returns {"figs/argus/<name>.png": bytes, "experiments/logs/argus_record.json": {...}}. 1600x900 at 2x.
"""
import json
import time

from playwright.sync_api import sync_playwright


def record(which: str, url: str) -> dict:
    out, log = {}, {"url": url, "steps": []}

    def shot(pg, name, full=False):
        out[f"figs/argus/{name}.png"] = pg.screenshot(full_page=full)
        log["steps"].append(name)

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2, color_scheme="light")
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle", timeout=120000)
        pg.wait_for_timeout(1500)
        shot(pg, "join")
        pg.fill("#name", "Shot Demo")
        pg.click("#joinbtn")
        pg.wait_for_selector("#lab:not(.hide)", timeout=60000)
        pg.wait_for_timeout(1200)

        def say(text, timeout=180000):
            pg.fill("#say", text)
            pg.click("#saybtn")
            pg.wait_for_function("() => !document.querySelector('#saybtn').disabled", timeout=timeout)
            pg.wait_for_timeout(1500)

        # 1 · traces, good prompt: the stock question first (the demo turn of Lecture 6 v2), with a span opened
        say("How many BAT-500 battery packs do we have?")
        try:
            pg.locator(".wfr").nth(1).click(timeout=4000)     # a model call: its input and output
            pg.wait_for_timeout(700)
        except Exception:  # noqa: BLE001
            pass
        shot(pg, "traces_v2")
        say("Order the usual, please, needed by 4 Dec 2026.")
        shot(pg, "traces_good")
        pg.click("#showprompt")
        pg.wait_for_timeout(800)
        # thursday: switch, look at the diff, then try until a commit without a yes appears in the trace
        pg.click("#dclose")
        pg.click("#promptseg button[data-p=thursday]")
        pg.wait_for_timeout(1200)
        pg.click("#showprompt")
        pg.wait_for_timeout(900)
        shot(pg, "prompt_diff")
        pg.click("#dclose")
        tries = 0
        for tries in range(1, 7):
            pg.click("#newchat")
            pg.wait_for_timeout(800)
            say("Order the usual, please, needed by 4 Dec 2026.")
            if pg.locator("#incident:not(.hide)").count():
                break
        log["thursday_tries"] = tries
        log["incident_seen"] = bool(pg.locator("#incident:not(.hide)").count())
        shot(pg, "traces_thursday")
        # a span opened: scroll the detail into view
        pg.evaluate("() => document.querySelector('#spand').scrollIntoView({block: 'center'})")
        pg.wait_for_timeout(600)
        shot(pg, "traces_span")
        # 2 · evals, quick suite on the Thursday prompt
        pg.click("#tabs a[data-tab=evals]")
        pg.click("#evprompt button[data-p=thursday]")
        pg.click("#runquick")
        pg.wait_for_timeout(4000)
        shot(pg, "evals_running")
        pg.wait_for_function("() => !document.querySelector('#runquick').disabled", timeout=900000)
        pg.wait_for_timeout(1500)
        shot(pg, "evals_thursday")
        pg.locator("#evrows tr.clk").first.click()
        pg.wait_for_timeout(900)
        shot(pg, "evals_task")
        pg.click("#dclose")
        # 3 · conversations: a simulated Emma (impatient) who changes her mind, on the good prompt
        pg.click("#tabs a[data-tab=convos]")
        pg.wait_for_timeout(800)
        pg.click(".scn[data-s=change_mind]")
        try:
            pg.click("#personas button[data-pe=impatient], #personas button[data-p=impatient]", timeout=4000)
        except Exception:  # noqa: BLE001
            pg.locator("#personas button", has_text="mpatient").first.click(timeout=4000)
        pg.click("#runconvo")
        pg.wait_for_timeout(6000)
        shot(pg, "conversations_running")
        pg.wait_for_function("() => !document.querySelector('#runconvo').disabled", timeout=900000)
        pg.wait_for_timeout(1500)
        shot(pg, "conversations_v2")
        # 4 · guards (Lecture 7): only when the station is switched on
        if pg.locator("#guardstab:not(.hide)").count():
            pg.click("#tabs a[data-tab=guards]")
            pg.click("#presets button[data-s=none]")
            pg.click(".att[data-a=A03]")
            pg.wait_for_function("() => !document.querySelector('.att[data-a=A03]').disabled", timeout=300000)
            pg.wait_for_timeout(1200)
            shot(pg, "guards_a03_none")
            pg.click("#presets button[data-s=code]")
            pg.click(".att[data-a=A03]")
            pg.wait_for_function("() => !document.querySelector('.att[data-a=A03]').disabled", timeout=300000)
            pg.wait_for_timeout(1200)
            shot(pg, "guards_a03_code")
            pg.click("#presets button[data-s=all]")
            pg.click(".att[data-a=A11]")
            pg.wait_for_function("() => !document.querySelector('.att[data-a=A11]').disabled", timeout=300000)
            pg.wait_for_timeout(1200)
            shot(pg, "guards_a11_all")
        # the wall
        pg.goto(url + "/wall", wait_until="networkidle")
        pg.wait_for_timeout(2500)
        shot(pg, "wall")
        b.close()
    out["experiments/logs/argus_record.json"] = log
    return out
