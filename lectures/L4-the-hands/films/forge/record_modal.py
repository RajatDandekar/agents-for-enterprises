"""Screen recordings of the forge (Hephaestus) for Lecture 4, as crisp frames, on the STAGING app by default.

    MODAL_PROFILE=rajatworkspace /Users/raj/.venv/bin/modal run lectures/L4-the-hands/films/forge/record_modal.py --films knob_output,q6
    ... --films shots        # the still screenshots for the deck (figs/hephaestus/*.png)
    ... --url https://...    # another deployment (never the live app during class: every film joins a new forge)

Why frames and not Playwright's screencast: the screencast is a low-bitrate VP8 whose text blurs on a projector. Here
every frame is a real screenshot of the page (1120 x 630 CSS pixels at device scale 2), taken after each scroll step,
click or progress tick, and logged with the shot it belongs to. assemble.py then gives each shot the length of its
narration and encodes H.264. A drawn cursor and an outline show where the click goes; nothing on the page is faked.

Each knob film stays on the Experiments tab: the shipped baseline is run first (through the API, before the camera
starts), then on camera one change under "Change one thing", one rerun, and the Before-and-after box. Output, per film:
films/forge/frames/<film>/NNNN.jpg, shots.json (the frame list per shot) and run.json (what /api/me returned after the
run: the numbers the narration may quote).
"""
import json
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
STAGING = "https://rajatworkspace--northbridge-hephaestus-staging.us-east.modal.run"
W, H, DPR = 1120, 630, 2

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("playwright==1.47.0", "httpx")
         .run_commands("playwright install --with-deps chromium"))
app = modal.App("l4-forge-frames", image=image)

# film -> (forge name, the "Change one thing" button, which questions, what to outline in the question table)
KNOBS = {
    "knob_description": ("Jordan Lee", "Vague descriptions on every tool", "six"),
    "knob_input": ("Chris Evans-Hall", "Loose input schemas", "errors"),
    "knob_output": ("Sam Patel", "Too little in every result", "six"),
    "knob_errors": ("Maya Brooks", "Raw error codes everywhere", "errors"),
    "knob_tools": ("Leo Grant", "Only 2 tools", "six"),
    "knob_rules": ("Nina Hart", "The preview rule switched off", "six"),
}

CURSOR_JS = """(() => { if (document.getElementById('__cur')) return;
  const c = document.createElement('div'); c.id = '__cur';
  c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 11-6.5 1.2L16 21l-3 1.4-3.4-6.9L4 20z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position: 'fixed', left: '-40px', top: '-40px', zIndex: 99999, pointerEvents: 'none', transition: 'none'});
  document.body.append(c);
  const st = document.createElement('style');
  st.textContent = '.__ring{outline:4px solid #eb6834 !important;outline-offset:4px;border-radius:14px} .__click{box-shadow:0 0 0 10px rgba(235,104,52,.25) !important}';
  document.head.append(st); })()"""


@app.function(timeout=3000, cpu=4, memory=8192)
def record(film: str, url: str = STAGING) -> dict:
    import httpx
    from playwright.sync_api import sync_playwright

    assert "staging" in url or "localhost" in url, "record against staging, never the live app"
    files, shots, notes = {}, [], []
    cli = httpx.Client(base_url=url, timeout=httpx.Timeout(600, connect=60))
    name, sug, qset = KNOBS.get(film, ("Priya Shah" if film == "q6" else "Ella Ward", None, "six"))
    me = cli.post("/api/join", json={"name": name}).json()
    key = me["key"]
    hdr = {"X-Forge-Key": key}

    def job(path, body=None):
        j = cli.post(path, headers=hdr, json=body or {}).json()
        while True:
            s = cli.get(f"/api/job/{j['id']}", headers=hdr).json()
            if s["state"] != "running":
                return s
            time.sleep(2)

    if film in KNOBS:  # the baseline, off camera
        base = job("/api/six", {"set": qset})
        notes.append(f"baseline {qset}: {base['state']} {base.get('result', {}).get('totals', {}).get('right')}")

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=DPR)
        ctx.add_init_script(f"try {{ localStorage.setItem('hx_key', {json.dumps(key)}); }} catch (e) {{}}")
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: notes.append("pageerror: " + str(e)))
        state = {"i": 0, "shot": None, "cur": (W * 0.7, H * 0.6)}

        def shot(sid):
            state["shot"] = {"id": sid, "frames": []}
            shots.append(state["shot"])

        def snap(dur=0.0):
            """One frame. dur = the least time it stays on screen (0: it may be squeezed to 1/30 s)."""
            state["i"] += 1
            k = f"frames/{film}/{state['i']:04d}.jpg"
            files[k] = pg.screenshot(type="jpeg", quality=93)
            state["shot"]["frames"].append([k.split("/")[-1], dur])

        def js(code):
            return pg.evaluate(code)

        def scroll_to(sel, offset=70, steps=14, dur=1 / 30):
            y0 = js("window.scrollY")
            y1 = js(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); return e ? e.getBoundingClientRect().top + window.scrollY - {offset} : window.scrollY; }})()")
            y1 = max(0, min(y1, js("document.documentElement.scrollHeight - innerHeight")))
            if abs(y1 - y0) < 4:
                return
            for s in range(1, steps + 1):
                t = s / steps
                e = t * t * (3 - 2 * t)
                js(f"window.scrollTo({{top: {y0 + (y1 - y0) * e}, behavior: 'instant'}})")
                snap(dur)

        def cursor_to(sel, steps=10):
            box = js(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left + Math.min(r.width * 0.5, 120), r.top + r.height * 0.55]; }})()")
            if not box:
                notes.append("no element " + sel)
                return
            x0, y0 = state["cur"]
            for s in range(1, steps + 1):
                t = s / steps
                e = t * t * (3 - 2 * t)
                x, y = x0 + (box[0] - x0) * e, y0 + (box[1] - y0) * e
                js(f"(() => {{ const c = document.getElementById('__cur'); c.style.left = '{x - 4}px'; c.style.top = '{y - 2}px'; }})()")
                snap()
            state["cur"] = tuple(box)

        def ring(sel, on=True):
            js(f"document.querySelectorAll({json.dumps(sel)}).forEach((e) => e.classList.toggle('__ring', {str(on).lower()}))")

        def click(sel):
            cursor_to(sel)
            js(f"document.querySelector({json.dumps(sel)}).classList.add('__click')")
            snap(0.25)
            pg.click(sel)
            js(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (e) e.classList.remove('__click'); }})()")

        def park():
            js("(() => { const c = document.getElementById('__cur'); c.style.left = '-40px'; })()")

        def wait_run(btn_sel, tick=2.0, timeout=900):
            t0 = time.time()
            pg.wait_for_timeout(600)
            while time.time() - t0 < timeout:
                snap(0.0)
                if not js(f"document.querySelector({json.dumps(btn_sel)}).disabled"):
                    break
                pg.wait_for_timeout(int(tick * 1000))
            pg.wait_for_timeout(1500)

        tab = "ask" if film == "q6" else "exp"
        pg.goto(f"{url}/#{tab}", wait_until="networkidle")
        pg.wait_for_selector("#app:not(.hide)", timeout=60000)
        pg.wait_for_timeout(1500)
        js(CURSOR_JS)

        if film in KNOBS:
            btn = "#runerr" if qset == "errors" else "#runsix"
            js("window.scrollTo(0, 0)")
            pg.wait_for_timeout(400)
            shot("intro")
            snap(1.0)
            scroll_to("#expsteps", 96)
            ring("#expsteps")
            snap(1.0)
            shot("baseline")
            ring("#expsteps", False)
            scroll_to("#compare", 96)
            ring("#compare .cmp")
            snap(1.0)
            ring("#compare .cmp", False)
            shot("pick")
            scroll_to(".expgrid", 96)
            sel = f'#sugs .sug:has-text("{sug}")'
            js(f"""(() => {{ const b = [...document.querySelectorAll('#sugs .sug')].find((x) => x.textContent.includes({json.dumps(sug)})); if (b) b.id = '__sug'; }})()""")
            scroll_to("#__sug", 330)
            ring("#__sug")
            cursor_to("#__sug")
            snap(1.0)                       # the pick shot ends on the ringed button, the cursor on it
            shot("settings")
            js("document.querySelector('#__sug').classList.add('__click')")
            snap(0.3)
            pg.click("#__sug")
            park()
            pg.wait_for_timeout(1200)
            js("window.scrollTo({top: document.querySelector('.expgrid').getBoundingClientRect().top + scrollY - 96, behavior: 'instant'})")
            pg.wait_for_timeout(300)
            ring("#nowsettings")
            snap(1.0)
            ring("#nowsettings", False)
            shot("run")
            click(btn)
            park()
            scroll_to("#prog6", 260)
            wait_run(btn)
            pg.wait_for_selector("#compare .cmp-tiles", timeout=60000)
            pg.wait_for_timeout(1200)
            shot("result")
            js("window.scrollTo({top: document.querySelector('#compare').getBoundingClientRect().top + scrollY - 90, behavior: 'instant'})")
            pg.wait_for_timeout(300)
            ring("#compare .cmp-say")
            snap(1.0)
            ring("#compare .cmp-say", False)
            shot("tiles")
            ring("#compare .cmp-tiles")
            snap(1.0)
            ring("#compare .cmp-tiles", False)
            shot("table")
            scroll_to("#compare .cmp-q", 96)
            ring("#compare tr.flip")
            snap(1.0)
            ring("#compare tr.flip", False)
            if qset == "errors":  # the error knobs: open one question's trace (full width), at its first failed call
                me2 = cli.get("/api/me", headers=hdr).json()
                rs = [r for r in me2["runs"] if r.get("set") == "errors"]
                a, b0 = rs[-1], rs[0]
                if film == "knob_errors":   # where a call failed: the error reply itself is the knob
                    cand = [i for i, r in enumerate(a["rows"]) if r["ledgerline_errors"] + r["door"] + r["rule"] > 0] or [0]
                    mv = cand[-1]
                else:                        # where the model needed the most extra calls
                    mv = max(range(len(a["rows"])), key=lambda i: (a["rows"][i]["tool_calls"] - b0["rows"][i]["tool_calls"], a["rows"][i]["tokens_in"]))
                qid = a["rows"][mv]["id"]
                notes.append(f"trace shown: {qid}")
                shot("trace")
                pg.click(f'#scorecard tr[data-q="{qid}"] details.qturns summary')
                pg.wait_for_timeout(600)
                js(f"""(() => {{ const row = document.querySelector('#scorecard tr.trace-row[data-for="{qid}"]'); row.id = '__tr';
                      const f = row.querySelector('.tc.fail'); if (f) {{ f.id = '__tc'; const x = f.querySelector('details'); if (x) x.open = true; }}
                      else {{ const t = row.querySelector('.trace'); if (t) t.id = '__tc'; }} }})()""")
                pg.wait_for_timeout(400)
                scroll_to("#__tr", 96)
                snap(1.0)
                shot("trace2")
                scroll_to("#__tc", 110)
                ring("#__tc")
                snap(1.0)
                ring("#__tc", False)
            shot("next")
            scroll_to("#compare .cmp-next", 300)
            ring("#compare .cmp-next")
            snap(1.0)
        elif film == "q6":
            js("window.scrollTo({top: document.querySelector('#qchips').getBoundingClientRect().top + scrollY - 70, behavior: 'instant'})")
            shot("chips")
            js("""(() => { const b = document.querySelector('.qchip[data-q="q6"]'); b.id = '__q6'; })()""")
            ring("#__q6")
            snap(1.5)
            click("#__q6")
            ring("#__q6", False)
            park()
            shot("wait")
            pg.wait_for_timeout(900)
            scroll_to("#msgs .mu", 80)
            t0 = time.time()
            while time.time() - t0 < 300:
                snap(0.0)
                if js("document.querySelectorAll('#msgs .ma .bub').length > 0 && !document.querySelector('#msgs .thinking')"):
                    break
                pg.wait_for_timeout(2000)
            pg.wait_for_timeout(800)
            js("document.querySelectorAll('#msgs .ma .tc details').forEach((d) => { d.open = true; })")
            pg.wait_for_timeout(500)
            # walk the trace: one stop per model step and per tool call, then the answer
            n = js("""(() => { const els = [...document.querySelectorAll('#msgs .ma .trace > *'), ...document.querySelectorAll('#msgs .ma .bub')];
                     els.forEach((e, i) => { e.dataset.walk = i; }); return els.length; })()""")
            for i in range(n):
                shot(f"walk{i:02d}")
                scroll_to(f'[data-walk="{i}"]', 90, steps=12)
                ring(f'[data-walk="{i}"]')
                snap(1.0)
                ring(f'[data-walk="{i}"]', False)
            chat = cli.get("/api/chat", headers=hdr).json()
            files["q6_chat.json"] = json.dumps(chat, ensure_ascii=False).encode()
        b.close()
    files[f"frames/{film}/shots.json"] = json.dumps({"film": film, "url": url, "forge": name, "viewport": [W, H, DPR],
                                                     "at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                                                     "shots": shots, "notes": notes}, indent=1).encode()
    run = cli.get("/api/me", headers=hdr).json()
    files[f"frames/{film}/run.json"] = json.dumps({k: run[k] for k in ("name", "changed", "runs")}, indent=1, ensure_ascii=False).encode()
    return files


@app.function(timeout=3000, cpu=4, memory=8192)
def stills(url: str = STAGING) -> dict:
    """The deck's still screenshots, each cropped to the part that matters (element screenshots at device scale 2)."""
    import httpx
    from playwright.sync_api import sync_playwright

    assert "staging" in url or "localhost" in url
    files = {}
    cli = httpx.Client(base_url=url, timeout=httpx.Timeout(600, connect=60))
    me = cli.post("/api/join", json={"name": "Ella Ward"}).json()
    key, hdr = me["key"], {"X-Forge-Key": me["key"]}

    def job(path, body=None):
        j = cli.post(path, headers=hdr, json=body or {}).json()
        while True:
            s = cli.get(f"/api/job/{j['id']}", headers=hdr).json()
            if s["state"] != "running":
                return s
            time.sleep(2)

    job("/api/six")
    cfg = cli.get("/api/me", headers=hdr).json()["config"]
    for n in cfg["tools"]:
        if cfg["tools"][n]["on"] and n in ("check_stock", "find_item", "find_supplier", "supplier_certificates", "check_budget", "create_purchase_request"):
            cfg["tools"][n]["output"] = "minimal"
    cli.post("/api/config", headers=hdr, json={"config": cfg}).raise_for_status()
    job("/api/six")
    for n in cfg["tools"]:  # back to shipped for the Anvil shot; the runs (and Before and after) stay
        cfg["tools"][n]["output"] = "all"
    cli.post("/api/config", headers=hdr, json={"config": cfg}).raise_for_status()
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle")
        pg.fill("#name", "Ella Ward")
        files["join.png"] = pg.locator(".hero .in").screenshot()
        ctx2 = b.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
        ctx2.add_init_script(f"try {{ localStorage.setItem('hx_key', {json.dumps(key)}); }} catch (e) {{}}")
        pg = ctx2.new_page()
        pg.goto(url + "/#anvil", wait_until="networkidle")
        pg.wait_for_selector("article.tool", timeout=60000)
        pg.add_style_tag(content="#nav{display:none!important}")  # the fixed nav would sit on top of element shots
        pg.wait_for_timeout(1000)
        files["anvil_card.png"] = pg.locator('article.tool[data-tool="check_stock"]').screenshot()
        pg.evaluate("location.hash = '#exp'")
        pg.wait_for_timeout(1500)
        files["experiments_steps.png"] = pg.locator("#expsteps").screenshot()
        files["experiments_compare.png"] = pg.locator("#compare .cmp").screenshot()
        files["experiments_sugs.png"] = pg.locator(".expgrid").screenshot()
        b.close()
    return {f"figs/hephaestus/{k}": v for k, v in files.items()}


@app.local_entrypoint()
def main(films: str = "knob_output", url: str = STAGING):
    L4 = HERE.parents[1]
    names = [f for f in films.split(",") if f]
    calls = []
    for f in names:
        calls.append((f, stills.spawn(url) if f == "shots" else record.spawn(f, url)))
    for f, c in calls:
        try:
            r = c.get()
        except Exception as e:  # noqa: BLE001
            print("FAILED", f, type(e).__name__, str(e)[:400])
            continue
        n = 0
        for k, v in r.items():
            dst = (L4 / k) if k.startswith("figs/") else (HERE / k)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(v)
            n += 1
        print("ok", f, n, "files")
