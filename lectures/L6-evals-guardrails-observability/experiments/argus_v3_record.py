"""Screenshots of Argus's v3 teaching views (Lecture 6), with Playwright; the method of argus_record.py and argus_record7.py.
Runs against the in-container app of argus_v3_modal.py or, after a deploy, the live URL. It changes no flag and removes
nobody; its student is "Shot V3 Demo" (the operator's `purge-tests` removes "Shot " names).

    record(url) -> {"files": {"figs/argus/<name>.png": bytes, ...}, "log": {...}}

    four_checks_friday.png    Evals · One turn, four checks, Friday's turn (recorded; no model call)
    four_checks_total.png     the same view, "A total nobody returned": numbers fail, the judge passes
    four_checks_judge.png     the judge's card alone, on the good chat's second turn, after "Run the judge" (one Haiku call)
    judge_right_naive.png     Evals · Is the judge right?, after the naive judge, one box opened
    judge_right_grounded.png  the same after the grounded judge
    deepeval_tool.png         Evals · The same checks in DeepEval, ToolCorrectness run on the good chat's turn 1 (NB6b's test case)
    deepeval_geval.png        the same form with GEval run
    deepeval_tool_friday.png, deepeval_geval_friday.png   the same two on Friday's turn
    convo_deepeval.png        Conversations, a finished simulated conversation, "Score with DeepEval" run
    trace_score_written.png   Traces, a Thursday-prompt turn, after "Write the score on this trace"
Whole pages, 1600 wide, at 2x (the judge's card is the card alone). `only`: names from turn, judge, deepeval, convo, trace.
"""
import time

from playwright.sync_api import sync_playwright

MSG = "Order the usual, please, needed by 4 Dec 2026."


def record(url: str, name: str = "Shot V3 Demo", prefix: str = "figs/argus/", scale: int = 2, only: str = "") -> dict:
    files, log = {}, {"url": url, "at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "student": name, "steps": [], "page_errors": []}
    want = set(x for x in only.split(",") if x) or {"turn", "judge", "deepeval", "convo", "trace"}

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 1200}, device_scale_factor=scale, color_scheme="light")
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: log["page_errors"].append(str(e)[:300]))
        pg.goto(url, wait_until="networkidle", timeout=120000)
        pg.evaluate("() => document.fonts.ready")
        pg.fill("#name", name)
        pg.click("#joinbtn")
        pg.wait_for_selector("#lab:not(.hide)", timeout=60000)
        pg.wait_for_function("() => typeof TEACH !== 'undefined' && TEACH !== null", timeout=30000)
        pg.wait_for_timeout(800)

        def calm():
            pg.wait_for_function("() => !document.querySelector('#toast').classList.contains('on')", timeout=20000)
            pg.mouse.move(2, 500)
            pg.wait_for_timeout(400)

        def shot(key, selector=None, crop=()):
            """A picture; `crop` names the page elements a slide wants in its frame: their box, in image pixels, goes in the log."""
            calm()
            if selector:
                pg.locator(selector).scroll_into_view_if_needed()
                files[f"{prefix}{key}.png"] = pg.locator(selector).screenshot()
            else:
                pg.evaluate("() => window.scrollTo(0, 0)")
                pg.wait_for_timeout(250)
                files[f"{prefix}{key}.png"] = pg.screenshot(full_page=True)
                if crop:
                    b = pg.evaluate("""(sels) => { const rs = sels.map(s => document.querySelector(s)).filter(e => e && e.offsetParent !== null).map(e => e.getBoundingClientRect());
                        const x0 = Math.min(...rs.map(r => r.left)), y0 = Math.min(...rs.map(r => r.top)), x1 = Math.max(...rs.map(r => r.right)), y1 = Math.max(...rs.map(r => r.bottom));
                        return [x0 + scrollX, y0 + scrollY, x1 - x0, y1 - y0]; }""", list(crop))
                    log.setdefault("crops", {})[key] = [round(v * scale) for v in b]
            log["steps"].append(key)

        def idle(sel, timeout=300000):
            pg.wait_for_function(f"() => !document.querySelector('{sel}').disabled", timeout=timeout)
            pg.wait_for_timeout(900)

        try:
            if "turn" in want:
                pg.click("#tabs a[data-tab=evals]")
                pg.click("#evnav button[data-v=turn]")
                pg.wait_for_selector("#tcards .card4", timeout=30000)
                pg.wait_for_timeout(600)
                verdicts = pg.locator("#tcards .verdict").all_inner_texts()
                log["turn"] = {"cards": pg.locator("#tcards .card4").count(), "parts": pg.locator("#tjudge .jpart").count(), "verdicts": verdicts,
                               "picker": pg.locator("#tpick .tpb b").all_inner_texts(), "marks": pg.locator("#tturn mark.f").count(),
                               "lesson": pg.locator("#tlesson").inner_text(), "trace_links": pg.locator("#tlinks2 a").all_inner_texts()}
                shot("four_checks_friday", crop=("#tcards", "#tlesson"))
                seen = {}
                for tid in ("good1", "total"):
                    pg.click(f"#tpick .tpb[data-t={tid}]")
                    pg.wait_for_function(f"() => TURN && TURN.id === '{tid}' && document.querySelectorAll('#tcards .card4').length === 4", timeout=30000)
                    pg.wait_for_timeout(500)
                    seen[tid] = pg.locator("#tcards .verdict").all_inner_texts()
                log["turn"]["other_turns"] = seen
                log["turn"]["total_not_found"] = pg.locator("#tturn mark.f.no").all_inner_texts()
                shot("four_checks_total", crop=("#tcards",))
                pg.set_viewport_size({"width": 1160, "height": 1200})      # the judge's card alone, narrower, so its text is large in a small frame
                pg.click("#tpick .tpb[data-t=friday]")
                pg.wait_for_function("() => TURN && TURN.id === 'friday'", timeout=30000)
                pg.wait_for_timeout(500)
                pg.click("#jrunbtn")
                idle("#jrunbtn")
                log["turn"]["judge_run"] = {"turn": "friday", "verdict": pg.locator("#jverdict .verdict").inner_text(), "note": pg.locator("#jnote").inner_text(),
                                            "reason": pg.locator("#jresult .c4why").inner_text()[:400]}
                shot("four_checks_judge", "#tjudge")
                pg.set_viewport_size({"width": 1600, "height": 1200})
            if "judge" in want:
                pg.click("#tabs a[data-tab=evals]")
                pg.click("#evnav button[data-v=judge]")
                pg.wait_for_selector("#jrlist .lab", timeout=30000)
                log["judge"] = {"rows": pg.locator("#jrlist .lab").count(), "recorded_tables": pg.locator("#jr56 .boxes").count()}
                for style in ("naive", "grounded"):
                    pg.click(f"#jrrun button[data-j={style}]")
                    idle(f"#jrrun button[data-j={style}]")
                    counts = pg.evaluate("() => Object.fromEntries([...document.querySelectorAll('#jrboxes .box')].map(b => [b.dataset.b, +b.querySelector('b').textContent]))")
                    # open the most telling box: a mistake if there is one (missed, else false alarm), else the wrong replies it caught
                    box = next((k for k in ("wrong_passed", "right_failed", "wrong_failed") if counts.get(k)), "right_passed")
                    pg.click(f"#jrboxes .box[data-b={box}]")
                    pg.wait_for_timeout(500)
                    log["judge"][style] = {"counts": counts, "line": pg.locator("#jrboxes .boxline").inner_text(), "opened": box,
                                           "listed": pg.locator("#inbox .it").count()}
                    log["judge"]["counts"] = counts
                    shot(f"judge_right_{style}", crop=("#jrboxes",))
            if "deepeval" in want:
                pg.click("#tabs a[data-tab=evals]")
                pg.click("#evnav button[data-v=deepeval]")
                pg.wait_for_function("() => document.querySelector('#dein').value.length > 5", timeout=30000)
                log["deepeval"] = {"filled_from": pg.locator("#deturn").input_value(), "input": pg.locator("#dein").input_value(),
                                   "tools_called": pg.locator("#decalled").input_value(), "expected": pg.locator("#deexp").input_value()}
                code = pg.locator("#decode").inner_text()
                log["deepeval"]["code_has_values"] = ("ToolCorrectnessMetric(" in code and "model=claude, threshold=1" in code and "should_exact_match=True" in code
                                                      and 'ToolCall(name="create_purchase_request", input_parameters={"confirm": False})' in code
                                                      and "Order the usual, please, needed by 4 Dec 2026." in code)

                def run_metric(key):
                    attempt = 0
                    for attempt in range(1, 4):                  # a run with no result (the judge broke DeepEval's format) is run again
                        pg.click("#derun")
                        idle("#derun")
                        if pg.locator("#deres .score").count():
                            break
                    log["deepeval"][key] = {"runs": attempt, "result": pg.locator("#deres").inner_text()[:900]}
                for tid, suffix in (("good1", ""), ("friday", "_friday")):
                    pg.select_option("#deturn", tid)
                    pg.wait_for_timeout(900)
                    pg.click("#demetric button[data-m=tool]")
                    pg.wait_for_timeout(300)
                    run_metric("tool" + suffix)
                    shot("deepeval_tool" + suffix, crop=("#ev-deepeval .de-grid",))
                    pg.click("#demetric button[data-m=geval]")
                    pg.wait_for_selector("#decrit", timeout=10000)
                    log["deepeval"]["geval_code"] = "GEval(" in pg.locator("#decode").inner_text() and "SingleTurnParams.ACTUAL_OUTPUT" in pg.locator("#decode").inner_text()
                    run_metric("geval" + suffix)
                    shot("deepeval_geval" + suffix, crop=("#ev-deepeval .de-grid",))
            if "convo" in want:
                pg.click("#tabs a[data-tab=convos]")
                pg.wait_for_timeout(600)
                pg.click(".scn[data-s=usual]")
                pg.click("#personas button[data-p=terse]")
                pg.click("#cvprompt button[data-p=good]")
                pg.click("#runconvo")
                idle("#runconvo", 900000)
                pg.wait_for_selector("#cvderun", timeout=30000)
                pg.click("#cvderun")
                idle("#cvderun", 600000)
                log["convo"] = {"our_checks": pg.locator("#cvverdict .cvck").count(), "rows": pg.locator("#cvderes .dem").count(),
                                "deepeval": pg.locator("#cvderes").inner_text()[:900], "verdict": pg.locator("#cvverdict .vbig").inner_text()}
                shot("convo_deepeval", crop=("#cvde",))
            if "trace" in want:
                pg.click("#tabs a[data-tab=traces]")
                pg.click("#promptseg button[data-p=thursday]")
                pg.wait_for_timeout(800)
                tries = 0
                for tries in range(1, 4):
                    pg.click("#newchat")
                    pg.wait_for_timeout(600)
                    pg.fill("#say", MSG)
                    pg.click("#saybtn")
                    idle("#saybtn", 240000)
                    if pg.locator("#incident:not(.hide)").count():
                        break
                log["trace"] = {"tries": tries, "incident": bool(pg.locator("#incident:not(.hide)").count()), "button": pg.locator("#scorebtn").count()}
                if pg.locator("#scorebtn").count():
                    pg.wait_for_timeout(4000)                    # let the trace reach the tools (they are sent in batches)
                    pg.click("#scorebtn")
                    pg.wait_for_selector("#scoreline:not(.hide)", timeout=120000)
                    pg.wait_for_timeout(600)
                    log["trace"]["line"] = pg.locator("#scoreline").inner_text()[:600]
                    log["trace"]["open_in"] = pg.locator("#tlinks a").all_inner_texts()
                    shot("trace_score_written", crop=("#tab-traces .tracep .ph", "#scoreline", "#incident"))
                else:
                    log["trace"]["skipped"] = "no tracing tool with a key on this Argus: the button is not shown"
        except Exception as e:  # noqa: BLE001
            log["error"] = f"{type(e).__name__}: {str(e)[:500]}"
            try:
                files["tmp/v3_error.png"] = pg.screenshot(full_page=True)
            except Exception:  # noqa: BLE001
                pass
        log["spend_usd"] = pg.evaluate("() => (typeof ME !== 'undefined' && ME) ? ME.spend_usd : null")
        b.close()
    return {"files": files, "log": log}
