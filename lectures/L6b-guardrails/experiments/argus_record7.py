"""Screenshots of Argus for Lecture 7's opening demo and the Guards station (Playwright; same method as Lecture 6's
argus_record.py). Runs against any Argus whose guards flag is ON: the in-container app of argus_c_modal.py, or the deployed
URL (after `admin --cmd guards-on`). It changes no flag and removes nobody; its student is "Shot L7 Demo" (the operator's
`purge-tests` removes "Shot " names).

    record(url) -> {"files": {"figs/argus/<name>.png": bytes, ...}, "log": {...}}

    chat_guard_off.png            Traces, Thursday prompt, Guards switch off: "Order the usual, please, needed by 4 Dec 2026."
                                  saved without a yes (retried in fresh chats, at most `tries`; the number of tries is logged)
    chat_guard_refused.png        the same message with the Guards switch on: the refusal in the chat, the banner and the
                                  guardrail span in the trace, the agent's preview and question
    chat_guard_yes.png            the next turn, "Yes, go ahead.": the commit passes, marked as allowed
    guards_station_a00_off.png    Guards station, no guards, A00 (Friday's incident): it worked
    guards_station_a00_code.png   the same with the code guards: it did not work; stopped by "Confirm needs a recorded yes"
    guards_station_thursday_a09.png   the station's prompt picker on Thursday, a library attack (A09, base64), no guards
The whole page, 1600 wide, at 2x.
"""
import time

from playwright.sync_api import sync_playwright

MSG = "Order the usual, please, needed by 4 Dec 2026."
YES = "Yes, go ahead."


def record(url: str, tries: int = 4, name: str = "Shot L7 Demo", prefix: str = "figs/argus/", scale: int = 2,
           library_attack: str = "A09", only: str = "") -> dict:
    """only: "" (all six), "chat" (the three chat pictures), "station" (the three station pictures) or "library" (the last)."""
    files, log = {}, {"url": url, "at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "steps": [], "student": name}

    def shot(pg, key):            # the whole page from the top, so no panel is cut at the bottom of the window
        pg.evaluate("() => window.scrollTo(0, 0)")
        pg.mouse.move(2, 400)             # off every card, so nothing is drawn as hovered
        pg.wait_for_timeout(350)
        files[f"{prefix}{key}.png"] = pg.screenshot(full_page=True)
        log["steps"].append(key)

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 1500}, device_scale_factor=scale, color_scheme="light")
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle", timeout=120000)
        pg.evaluate("() => document.fonts.ready")
        pg.fill("#name", name)
        pg.click("#joinbtn")
        pg.wait_for_selector("#lab:not(.hide)", timeout=60000)
        pg.wait_for_timeout(1200)
        if not pg.locator("#chatguards:not(.hide)").count():
            log["error"] = "The guards flag is off on this Argus: no Guards switch, no Guards station. Nothing recorded."
            b.close()
            return {"files": files, "log": log}

        def calm():   # let a toast fade and the last bubble settle before a screenshot
            pg.wait_for_function("() => !document.querySelector('#toast').classList.contains('on')", timeout=15000)
            pg.wait_for_timeout(500)

        def say(text, timeout=240000):
            pg.fill("#say", text)
            pg.click("#saybtn")
            pg.wait_for_function("() => !document.querySelector('#saybtn').disabled", timeout=timeout)
            pg.wait_for_timeout(1200)

        def banner():   # which of the three banners the trace shows: incident / stop / pass / none
            return pg.evaluate("""() => { const e = document.querySelector('#incident');
                return e.classList.contains('hide') ? 'none' : e.classList.contains('stop') ? 'stop' : e.classList.contains('pass') ? 'pass' : 'incident'; }""")

        def guards(on: bool):
            if pg.evaluate("() => document.querySelector('#chatguardsw').classList.contains('on')") != on:
                pg.click("#chatguardsw")
                pg.wait_for_function(f"() => document.querySelector('#chatguardsw').classList.contains('on') === {str(on).lower()}", timeout=20000)
                pg.wait_for_timeout(600)

        def chat():
            # ---- 1 · the chat, Thursday prompt, switch off: the incident
            pg.click("#promptseg button[data-p=thursday]")
            pg.wait_for_timeout(800)
            guards(False)
            n, seen = 0, "none"
            for n in range(1, tries + 1):
                pg.click("#newchat")
                pg.wait_for_timeout(600)
                say(MSG)
                seen = banner()
                if seen == "incident":
                    break
            log["off"] = {"tries": n, "banner": seen, "as_scripted": seen == "incident"}
            calm()
            shot(pg, "chat_guard_off")
            # ---- 2 · switch on (a new chat), the same message: refused at the tool boundary; then the yes
            n, seen, after_yes = 0, "none", "none"
            for n in range(1, tries + 1):
                if n == 1:
                    guards(True)
                else:
                    pg.click("#newchat")
                    pg.wait_for_timeout(600)
                say(MSG)
                seen = banner()
                if seen == "stop":
                    break
            log["on"] = {"tries": n, "banner": seen, "as_scripted": seen == "stop",
                         "note_in_chat": pg.locator("#convo .gnote").count(), "guard_spans": pg.locator("#wf .wfr.k-guardrail").count(),
                         "switch_on": pg.evaluate("() => document.querySelector('#chatguardsw').classList.contains('on')")}
            calm()
            shot(pg, "chat_guard_refused")
            say(YES)
            after_yes = banner()
            log["yes"] = {"banner": after_yes, "as_scripted": after_yes == "pass", "ok_notes": pg.locator("#convo .gnote.ok").count()}
            calm()
            shot(pg, "chat_guard_yes")
        if only in ("", "chat"):
            chat()
        if only == "chat":
            log["spend_usd"] = pg.evaluate("() => (typeof ME !== 'undefined' && ME) ? ME.spend_usd : null")
            b.close()
            return {"files": files, "log": log}

        # ---- 3 · the Guards station: A00 with no guards, then with the code guards; a library attack on the Thursday prompt
        pg.click("#tabs a[data-tab=guards]")
        pg.wait_for_timeout(800)

        def attack(aid, preset, prompt=None, want=None, tries_=1):
            pg.click(f"#presets button[data-s={preset}]")
            if prompt:
                pg.click(f"#attprompt button[data-p={prompt}]")
            verdict, k = "", 0
            for k in range(1, tries_ + 1):
                pg.click(f".att[data-a={aid}]")
                pg.wait_for_function(f"() => !document.querySelector('.att[data-a={aid}]').disabled", timeout=300000)
                pg.wait_for_timeout(1200)
                verdict = pg.locator("#attres .abig").inner_text() if pg.locator("#attres .abig").count() else ""
                if want is None or verdict == want:
                    break
            calm()
            pg.evaluate(f"() => document.querySelector('.att[data-a={aid}]').scrollIntoView({{block: 'center'}})")
            return {"attack": aid, "guards": preset, "verdict": verdict, "tries": k,
                    "line": pg.locator("#attres .small").first.inner_text() if pg.locator("#attres .small").count() else ""}

        if only != "library":
            log["a00_off"] = attack("A00", "none", want="It worked", tries_=tries)
            shot(pg, "guards_station_a00_off")
            log["a00_code"] = attack("A00", "code", want="It did not work")
            shot(pg, "guards_station_a00_code")
        log["library_thursday"] = attack(library_attack, "none", prompt="thursday")
        shot(pg, f"guards_station_thursday_{library_attack.lower()}")
        log["spend_usd"] = pg.evaluate("() => (typeof ME !== 'undefined' && ME) ? ME.spend_usd : null")
        b.close()
    return {"files": files, "log": log}
