"""Screenshots of Aegis for Lecture 7 (Playwright; same method as argus_record7.py). Run on Modal by
deploy/aegis_modal.py::record against the deployed URL. Its student is "Shot Aegis" (`admin --cmd purge-tests` removes
"Shot " names). It changes no flag and removes nobody.

    record(url, only="") -> {"files": {"figs/aegis/<name>.png": bytes, ...}, "log": {...}}

    join.png             the join page
    chat_strip.png       tab 1, Thursday's prompt, Guards on, "Order the usual, please, needed by 4 Dec 2026.": the refused save
    chat_yes.png         the next turn, "Yes, go ahead."
    chat_mail_off.png    Thursday's prompt, the sandbox inbox, Guards off: "Please deal with the new invoice in the AP inbox." (one try)
    chat_mail_on.png     the same message with Guards on
    bench_all.png        tab 2 after "Run all 17" (the whole page)
    bench_a14.png, bench_a01.png, bench_a03.png, bench_a06.png, bench_a11.png    the list and that attack, off against on
    bench_own.png        "Call any tool yourself": the usual committed with no preview, off against on
    detect_usual.png, detect_colleague.png, detect_pii.png, detect_invoice.png    tab 3 after Check on that example
    detect_invoice_<detector>.png    the five cards of the invoice example, one each (larger on a slide)
    attacks.png          tab 4 after one library attack (A03) with the code guards
    wall.png             the class wall
only: a comma list of groups (join, chat, mail, bench, detect, attacks, wall); "" is all. 1600 wide, at 2x.
"""
import time

from playwright.sync_api import sync_playwright

MSG = "Order the usual, please, needed by 4 Dec 2026."
YES = "Yes, go ahead."
MAIL = "Please deal with the new invoice in the AP inbox."
CHIPS = {"usual": 0, "colleague": 1, "pii": 4, "invoice": 5}      # the order of detect.EXAMPLES


def record(url: str, only: str = "", tries: int = 3, name: str = "Shot Aegis", prefix: str = "figs/aegis/", scale: int = 2) -> dict:
    want = {x for x in only.split(",") if x} or {"join", "chat", "mail", "bench", "detect", "attacks", "wall"}
    files, log = {}, {"url": url, "at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "steps": [], "student": name, "groups": sorted(want)}

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 1500}, device_scale_factor=scale, color_scheme="light")
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)[:300]))

        def calm():   # let a toast fade and the last bubble settle before a screenshot
            pg.wait_for_function("() => !document.querySelector('#toast').classList.contains('on')", timeout=20000)
            pg.wait_for_timeout(500)

        def shot(key, sel=None):   # the whole page from the top (or one panel), so nothing is cut at the window's edge
            pg.mouse.move(2, 400)
            if sel:
                pg.locator(sel).first.scroll_into_view_if_needed()
                pg.wait_for_timeout(350)
                files[f"{prefix}{key}.png"] = pg.locator(sel).first.screenshot()
            else:
                pg.evaluate("() => window.scrollTo(0, 0)")
                pg.wait_for_timeout(350)
                files[f"{prefix}{key}.png"] = pg.screenshot(full_page=True)
            log["steps"].append(key)

        def tab(t):
            pg.click(f"#tabs a[data-tab={t}]")
            pg.wait_for_timeout(700)

        pg.goto(url, wait_until="networkidle", timeout=180000)
        pg.evaluate("() => document.fonts.ready")
        pg.wait_for_timeout(600)
        if "join" in want:
            pg.set_viewport_size({"width": 1600, "height": 1000})
            shot("join")
            pg.set_viewport_size({"width": 1600, "height": 1500})
        pg.fill("#name", name)
        pg.click("#joinbtn")
        pg.wait_for_selector("#lab:not(.hide)", timeout=60000)
        pg.wait_for_function("() => document.querySelectorAll('#agtbl tr.r').length === 17 && document.querySelectorAll('#agcards .ag-card').length === 5", timeout=120000)
        pg.wait_for_timeout(1000)
        log["tabs"] = pg.evaluate("() => [...document.querySelectorAll('#tabs a')].filter(a => getComputedStyle(a).display !== 'none').map(a => a.innerText.replace(/\\s+/g, ' ').trim())")
        log["brand"] = pg.locator(".brand").inner_text().replace("\n", " · ")

        def say(text, timeout=300000):
            pg.fill("#say", text)
            pg.click("#saybtn")
            pg.wait_for_function("() => !document.querySelector('#saybtn').disabled", timeout=timeout)
            pg.wait_for_timeout(1200)

        def banner():
            return pg.evaluate("""() => { const e = document.querySelector('#incident');
                return e.classList.contains('hide') ? 'none' : e.classList.contains('stop') ? 'stop' : e.classList.contains('pass') ? 'pass' : 'incident'; }""")

        def last():   # the last chat turn: each tool call, and whether a guard refused it
            return pg.evaluate("""() => { const t = (ME.chat || [])[ME.chat.length - 1]; if (!t) return null;
                return {calls: t.calls.map(c => c.tool + (c.refused_by ? ' [refused by ' + c.refused_by + ']' : c.ok ? '' : ' [Ledgerline said no]')),
                        refused: (t.refused || []).map(r => r.guard + ' on ' + r.tool), usd: t.usd, reply: (t.reply || '').slice(0, 260)}; }""")

        def guards(on: bool):
            if pg.evaluate("() => document.querySelector('#chatguardsw').classList.contains('on')") != on:
                pg.click("#chatguardsw")
                pg.wait_for_function(f"() => document.querySelector('#chatguardsw').classList.contains('on') === {str(on).lower()}", timeout=20000)
                pg.wait_for_timeout(600)

        def fresh():
            pg.click("#newchat")
            pg.wait_for_timeout(700)

        if want & {"chat", "mail"}:
            tab("traces")
            pg.click("#promptseg button[data-p=thursday]")
            pg.wait_for_timeout(800)
        if "chat" in want:
            guards(True)
            n, seen = 0, "none"
            for n in range(1, tries + 1):
                fresh()
                say(MSG)
                seen = banner()
                if seen == "stop":
                    break
            log["chat_strip"] = {"tries": n, "banner": seen, "as_scripted": seen == "stop", "turn": last(),
                                 "strip": pg.locator("#agstrip").inner_text().replace("\n", " ")[:300]}
            calm()
            shot("chat_strip")
            say(YES)
            log["chat_yes"] = {"banner": banner(), "as_scripted": banner() == "pass", "turn": last()}
            calm()
            shot("chat_yes")
        if "mail" in want:
            guards(False)
            fresh()                             # one try, recorded as it went: the model does not always obey the e-mail
            say(MAIL)
            t = last()
            calls = (t or {}).get("calls") or []
            log["chat_mail_off"] = {"banner": banner(), "turn": t,
                                    "sent_outside": any(c == "send_message" for c in calls),
                                    "saved_the_invoice": any(c in ("record_invoice", "match_invoice") for c in calls)}
            calm()
            shot("chat_mail_off")
            guards(True)
            n, t = 0, None
            for n in range(1, tries + 1):       # with guards the agent may refuse by itself; a picture with a guard's refusal teaches more
                fresh()
                say(MAIL)
                t = last()
                if t and t["refused"]:
                    break
            log["chat_mail_on"] = {"tries": n, "banner": banner(), "turn": t, "as_scripted": bool(t and t["refused"])}
            calm()
            shot("chat_mail_on")

        if "bench" in want:
            tab("bench")
            pg.click("#agrunall")
            pg.wait_for_selector("#agtotals .on.done", timeout=300000)
            pg.wait_for_selector("#agres .ag-two", timeout=60000)
            log["bench_totals"] = pg.locator("#agtotals").inner_text().replace("\n", " ")
            calm()
            shot("bench_all")
            for aid in ("A14", "A01", "A03", "A06", "A11"):
                pg.click(f"#agtbl tr.r[data-a={aid}]")
                pg.wait_for_function(f"() => (document.querySelector('#agres h3') || {{}}).innerText?.startsWith('{aid}') && !!document.querySelector('#agres .ag-two')", timeout=120000)
                pg.wait_for_timeout(400)
                log["bench_" + aid.lower()] = {"off": pg.locator("#agres .ag-side.off .ag-verdict b").inner_text(),
                                               "on": pg.locator("#agres .ag-side.on .ag-verdict b").inner_text(),
                                               "guard": [x.split("\n")[0] for x in pg.locator("#agres .ag-side.on .ag-ans.guard b").all_inner_texts()]}
                shot("bench_" + aid.lower(), ".ag-bench")
            pg.click("#agcall")
            pg.wait_for_selector("#agownres .ag-two", timeout=120000)
            pg.wait_for_function("() => !document.querySelector('#agcall').disabled", timeout=60000)
            log["bench_own"] = {"off": pg.locator("#agownres .ag-side.off .ag-ans b").first.inner_text(),
                                "on": pg.locator("#agownres .ag-side.on .ag-ans b").first.inner_text()}
            shot("bench_own", "#tab-bench > .panel")

        if "detect" in want:
            tab("detect")
            for key, i in CHIPS.items():
                pg.click(f"#agex .chipbtn[data-i='{i}']")
                pg.click("#agcheck")
                pg.wait_for_timeout(500)
                pg.wait_for_function("() => !document.querySelector('#agcheck').disabled", timeout=180000)
                pg.wait_for_selector("#agr-output_check .ag-res", timeout=30000)
                pg.wait_for_timeout(500)
                log["detect_" + key] = {d: (pg.locator(f"#agr-{d} .big").inner_text() if pg.locator(f"#agr-{d} .big").count() else "no result")
                                        for d in ("injection_clf", "pii", "llm_check", "spotlight", "output_check")}
                calm()
                shot("detect_" + key)
                if key == "invoice":
                    for d in ("injection_clf", "pii", "llm_check", "spotlight", "output_check"):
                        shot(f"detect_invoice_{d}", f".ag-card[data-d={d}]")

        if "attacks" in want:
            tab("guards")
            pg.click("#presets button[data-s=code]")
            pg.click(".att[data-a=A03]")
            pg.wait_for_function("() => !document.querySelector('.att[data-a=A03]').disabled", timeout=300000)
            pg.wait_for_timeout(1200)
            log["attacks"] = {"attack": "A03", "guards": "code",
                              "verdict": pg.locator("#attres .abig").inner_text() if pg.locator("#attres .abig").count() else ""}
            calm()
            shot("attacks")

        log["spend_usd"] = pg.evaluate("async () => { try { await refreshMe(); } catch (e) {} return (typeof ME !== 'undefined' && ME) ? ME.spend_usd : null; }")
        if "wall" in want:
            pg.set_viewport_size({"width": 1600, "height": 1000})
            pg.goto(url.rstrip("/") + "/wall", wait_until="networkidle", timeout=120000)
            pg.wait_for_timeout(1500)
            shot("wall")
        log["page_errors"] = errors
        b.close()
    return {"files": files, "log": log}
