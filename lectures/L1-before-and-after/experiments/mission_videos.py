"""Lecture 1 v4 (Northbridge Cycles): the five Before missions as screen videos, plus "a button calls a service".

Everything runs on Modal: the Ledgerline server (ledgerline.server, with goods receipt installed, as the Experience
serves it), the 1998 legacy client at /legacy in headless Chromium (Playwright record_video, 1600x900), and ffmpeg.
The missions are played the first-time way, keeping what Fetch fills in, so the order mission hits its traps on
camera: two Voltways in the F2 lookup, ERR-PO-0412, the silent Draft on the closed cost centre PRD-05, the refused
release, then the fix (order amendment to PRD-07, release again). A drawn cursor, a ring on every click, an outline
on the element clicked, and a caption bar for each step are overlaid on the page; nothing is edited afterwards
except cutting the start (the off-camera sign-in for Emma's continuing missions) and the trap clips out of mission 4.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/mission_videos.py
-> figs/missions/m1_stock.mp4 ... m5_receive.mp4, m4_trap_*.mp4, *.jpg posters, missions.json
-> figs/legacy/button_before.jpg, button_after.jpg and experiments/logs/button_service.json
"""
import json
import pathlib
import re

import modal

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2] if modal.is_local() else pathlib.Path("/course")
image = (modal.Image.debian_slim(python_version="3.11")
         .apt_install("ffmpeg")
         .pip_install("playwright==1.47.0", "fastapi", "uvicorn", "httpx", "pyyaml", "pydantic>=2", "openai", "pandas", "pillow")
         .run_commands("playwright install --with-deps chromium")
         .env({"PYTHONPATH": "/course/ledgerline"})
         .add_local_dir(ROOT / "ledgerline", "/course/ledgerline", ignore=lambda p: any(x in ("cassettes", "__pycache__", "_index")
                                                                              for x in pathlib.Path(p).parts)))
app = modal.App("l1v4-mission-videos", image=image)

W, H = 1600, 900
ZOOM = 1.2   # the 1998 client is 1040 px wide; zoomed so it reads at 1600x900 and leaves room for the caption bar

OVERLAY = """
(() => {
  const css = `
  body{zoom:%ZOOM%}
  #__ov{position:fixed;inset:0;pointer-events:none;z-index:2147483647}
  #__cur{position:fixed;left:0;top:0;width:28px;height:28px;transition:transform .55s cubic-bezier(.3,.7,.3,1);will-change:transform}
  .__ring{position:fixed;width:56px;height:56px;margin:-28px 0 0 -28px;border:4px solid #ff7a00;border-radius:50%;
          animation:__r .7s ease-out forwards}
  @keyframes __r{from{transform:scale(.25);opacity:1}to{transform:scale(1.35);opacity:0}}
  .__hl{outline:3px solid #ff7a00 !important;outline-offset:2px;box-shadow:0 0 0 7px rgba(255,122,0,.28) !important}
  #__cap{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);max-width:1460px;display:flex;align-items:center;
         gap:14px;padding:12px 22px;border-radius:12px;background:rgba(18,19,23,.92);color:#fff;
         font:500 24px/1.25 "DejaVu Sans",Arial,sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.35);transition:background .2s}
  #__cap .who{font-size:16px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#9fb6d9;white-space:nowrap}
  #__cap .n{font-size:16px;color:#aaa;white-space:nowrap}
  #__cap.err{background:rgba(150,20,20,.95)} #__cap.err .who{color:#ffd0d0}
  #__cap.trap{background:rgba(160,90,0,.95)} #__cap.trap .who{color:#ffe2b8}
  #__cap.ok{background:rgba(20,110,60,.95)} #__cap.ok .who{color:#c8f0d8}
  #__cap.hide{display:none}
  #__sync{position:fixed;left:0;bottom:0;display:flex}#__sync i{display:block;width:6px;height:6px;background:#000}`;
  const arrow = '<svg width="28" height="28" viewBox="0 0 28 28"><path d="M3 2 L3 23 L9 17.5 L13 26 L17 24.2 L13 15.8 L21 15.8 Z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  function mount() {
    if (document.getElementById('__ov')) return;
    const st = document.createElement('style'); st.textContent = css; document.documentElement.appendChild(st);
    const ov = document.createElement('div'); ov.id = '__ov';
    ov.innerHTML = '<div id="__sync">' + '<i></i>'.repeat(8) + '</div><div id="__cur">' + arrow + '</div><div id="__cap" class="hide"><span class="who"></span><span class="t"></span><span class="n"></span></div>';
    document.documentElement.appendChild(ov);
  }
  window.__curTo = (x, y, ms) => { mount(); const c = document.getElementById('__cur'); c.style.transitionDuration = (ms || 550) + 'ms';
                                   c.style.transform = `translate(${x - 3}px, ${y - 2}px)`; };
  window.__sync = (id) => { mount(); [...document.querySelectorAll('#__sync i')].forEach((b, i) => { b.style.background = (id >> i) & 1 ? '#fff' : '#000'; }); };
  window.__ring = (x, y) => { mount(); const r = document.createElement('div'); r.className = '__ring'; r.style.left = x + 'px';
                              r.style.top = y + 'px'; document.getElementById('__ov').appendChild(r); setTimeout(() => r.remove(), 800); };
  window.__cap = (who, text, kind, n) => { mount(); const c = document.getElementById('__cap'); c.className = kind || '';
                                         c.querySelector('.who').textContent = who; c.querySelector('.t').textContent = text;
                                         c.querySelector('.n').textContent = n || ''; };
  document.addEventListener('DOMContentLoaded', mount);
})();
""".replace("%ZOOM%", str(ZOOM))


@app.function(timeout=1800, cpu=4, memory=8192)
def record() -> dict:
    import subprocess
    import threading
    import time

    import httpx
    import uvicorn
    from playwright.sync_api import sync_playwright

    import ledgerline.server as srv
    from ledgerline.erp.engine import ERP
    from ledgerline.erp.receipts import install_receipts

    def northbridge():
        e = ERP()
        install_receipts(e)
        return e

    server = uvicorn.Server(uvicorn.Config(srv.create_app(northbridge), host="127.0.0.1", port=8077, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.1)
    BASE = "http://127.0.0.1:8077"
    out, missions = {}, []
    work = pathlib.Path("/tmp/vid")
    work.mkdir(exist_ok=True)

    def ff(*args):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)

    def probe(p):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True, check=True)
        return round(float(r.stdout.strip()), 2)

    with sync_playwright() as p:
        b = p.chromium.launch()

        class Take:
            """One mission on camera: a fresh browser window on the shared Northbridge (tenant 'class')."""

            def __init__(self, mid, who, person):
                self.mid, self.who, self.person = mid, who, person
                self.ctx = b.new_context(viewport={"width": W, "height": H}, record_video_dir=str(work / mid),
                                         record_video_size={"width": W, "height": H})
                self.ctx.add_init_script(OVERLAY)
                self.pg = self.ctx.new_page()
                self.t0 = time.monotonic()
                self.steps, self.marks, self.n, self.sid = [], {}, 0, 0
                self.pg.goto(f"{BASE}/legacy?tenant=class", wait_until="networkidle")
                self.pg.wait_for_selector("#f_user_id")
                self.pg.evaluate(f"__curTo({W // 2}, {H // 2}, 1)")

            def t(self):
                return round(time.monotonic() - self.t0, 2)

            def sync(self):
                # a frame-exact clock: the id is drawn as 8 tiny black/white blocks in the bottom-left corner, read back
                # from the recorded video, and painted over in the final encode
                self.sid += 1
                self.pg.evaluate(f"__sync({self.sid})")
                self.pg.wait_for_timeout(80)
                return self.sid

            def mark(self, name):
                self.marks[name] = self.sync()

            def cap(self, text, kind="", hold=1.6):
                self.n += 1
                self.pg.evaluate("([w, t, k, n]) => __cap(w, t, k, n)", [self.person, text, kind, f"step {self.n}"])
                self.steps.append({"n": self.n, "sid": self.sync(), "caption": text, "kind": kind or "step",
                                   "status_bar": self.status()})
                self.pg.wait_for_timeout(int(hold * 1000))

            def status(self):
                loc = self.pg.locator("#msg") if self.pg.locator("#main:not(.hidden)").count() else self.pg.locator("#loginmsg")
                return loc.inner_text() if loc.count() else ""

            def point(self, loc, click=True, double=False, hl=True):
                loc.scroll_into_view_if_needed()
                bb = loc.bounding_box()
                x, y = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
                self.pg.evaluate(f"__curTo({x}, {y}, 380)")
                self.pg.wait_for_timeout(430)
                if hl:
                    loc.evaluate("el => { el.classList.add('__hl'); setTimeout(() => el.classList.remove('__hl'), 900); }")
                if click:
                    self.pg.evaluate(f"__ring({x}, {y})")
                    (self.pg.mouse.dblclick if double else self.pg.mouse.click)(x, y)
                    self.pg.wait_for_timeout(250)

            def type(self, field, text, replace=False):
                loc = self.pg.locator(f"#f_{field}")
                self.point(loc)
                if replace:
                    self.pg.keyboard.press("Control+A")
                self.pg.keyboard.type(str(text), delay=40)
                self.pg.wait_for_timeout(200)

            def press(self, button):
                self.point(self.pg.locator("#btns button, #loginbtns button").filter(has_text=re.compile(f"^{re.escape(button)}$")).first)
                self.pg.wait_for_load_state("networkidle")
                self.pg.wait_for_timeout(320)

            def open_(self, code, label):
                self.point(self.pg.locator(f'.tree .it[data-code="{code}"]'))
                self.pg.wait_for_timeout(300)

            def sign_in(self, uid, pw, on_camera=True):
                if on_camera:
                    self.cap(f"Sign in as {uid}", hold=0.8)
                    self.type("user_id", uid)
                    self.type("password", pw)
                    self.press("Sign in")
                else:
                    self.pg.fill("#f_user_id", uid); self.pg.fill("#f_password", pw)
                    self.pg.click("#loginbtns button:has-text('Sign in')")
                self.pg.wait_for_selector("#main:not(.hidden)")
                self.pg.wait_for_timeout(500)

            def val(self, name):
                loc = self.pg.locator(f"#f_{name}")
                return loc.input_value() if loc.count() else None

            def finish(self, fname, title, traps, clips=()):
                self.pg.wait_for_timeout(1800)
                self.mark("end")
                self.pg.wait_for_timeout(500)
                vpath = self.pg.video.path()
                self.ctx.close()
                raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", vpath, "-vf", f"fps=25,crop=48:6:0:{H - 6},format=gray",
                                      "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
                seen = {}
                for fi in range(len(raw) // 288):
                    fr = raw[fi * 288:(fi + 1) * 288]
                    sid = sum(1 << i for i in range(8) if fr[3 * 48 + 6 * i + 3] > 128)
                    seen.setdefault(sid, fi / 25)

                def vt(sid):  # the video time an id first shows; a dropped id takes the next one's time
                    later = [seen[x] for x in seen if x >= sid and x > 0]
                    return seen.get(sid, min(later) if later else len(raw) / 288 / 25)

                self.vmarks = {k_: vt(v_) for k_, v_ in self.marks.items()}
                for s_ in self.steps:
                    s_["t"] = vt(s_.pop("sid"))
                start = max(0.0, self.vmarks.get("start", 0) - 0.2)
                end = self.vmarks["end"]
                mp4 = work / f"{fname}.mp4"

                def cut(src_start, dur, dst):
                    ff("-ss", f"{src_start:.2f}", "-i", vpath, "-t", f"{dur:.2f}", "-vf", f"fps=30,scale={W}:{H},drawbox=x=0:y={H - 6}:w=48:h=6:color=0x3A6EA5:t=fill",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                       "-an", str(dst))

                cut(start, end - start, mp4)
                dur = probe(mp4)
                poster_t = self.vmarks.get("poster", end - 1.0) + 1.2 - start
                ff("-ss", f"{max(0, poster_t):.2f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(work / f"{fname}.jpg"))
                for k in ("mp4", "jpg"):
                    out[f"figs/missions/{fname}.{k}"] = (work / f"{fname}.{k}").read_bytes()
                rec = {"id": self.mid, "file": f"{fname}.mp4", "poster": f"{fname}.jpg", "title": title, "who": self.who,
                       "person": self.person, "duration_s": dur, "size_bytes": len(out[f"figs/missions/{fname}.mp4"]),
                       "traps": traps,
                       "steps": [{**s, "t": round(max(0.0, s["t"] - start), 2)} for s in self.steps], "clips": [],
                       "sync_ids_seen": len(seen), "sync_ids_sent": self.sid}
                for cname, a, z, what in clips:
                    c0, c1 = self.vmarks[a] - 0.2, self.vmarks[z] + 0.4
                    cp = work / f"{cname}.mp4"
                    cut(c0, c1 - c0, cp)
                    ff("-ss", f"{max(0.0, c1 - c0 - 0.8):.2f}", "-i", str(cp), "-frames:v", "1", "-q:v", "3", str(work / f"{cname}.jpg"))
                    out[f"figs/missions/{cname}.mp4"] = cp.read_bytes()
                    out[f"figs/missions/{cname}.jpg"] = (work / f"{cname}.jpg").read_bytes()
                    rec["clips"].append({"file": f"{cname}.mp4", "poster": f"{cname}.jpg", "what": what,
                                         "from_s": round(c0 - start, 2), "duration_s": probe(cp), "size_bytes": cp.stat().st_size})
                missions.append(rec)
                print(f"{fname}: {dur}s {rec['size_bytes'] // 1024} KB, {len(self.steps)} steps, clips {[c['file'] for c in rec['clips']]}")

        # ---------------- M1 stock (Emma)
        k = Take("M1", "ECLARKE", "Emma")
        k.mark("start")
        k.sign_in("ECLARKE", "emma@123")
        k.cap("Emma needs battery packs. First: how many are in stock?", hold=1.4)
        k.open_("INV-ITM-03", "Item enquiry"); k.cap("Masters › Item enquiry: she needs the item's code", hold=0.6)
        k.type("q", "battery pack 5"); k.press("Search")
        n_rows = k.pg.locator("#form .grid tr[data-i], .grid tr[data-i]").count()
        k.cap(f"{n_rows} battery packs look alike. BAT-500 is the right one; -R is refurbished", "trap", hold=2.6)
        k.open_("INV-STK-02", "Stock status"); k.cap("Inventory › Stock status", hold=0.5)
        k.type("itm_cd", "BAT-500"); k.press("Query")
        oh, d, cv = k.val("on_hand"), k.val("avg_daily_issue"), k.val("cover_days")
        k.mark("poster")
        k.cap(f"{int(oh):,} on hand · {int(d):,} used a day · {cv} days of cover. Not enough for the spring launch", "ok", hold=3.0)
        k.finish("m1_stock", "Check the stock", ["four items look alike (BAT-500, BAT-500-R, BAT-375, BAT-750)"])

        # ---------------- M2 request (Emma, already signed in)
        k = Take("M2", "ECLARKE", "Emma")
        k.sign_in("ECLARKE", "emma@123", on_camera=False)
        k.mark("start")
        k.cap("Raise a purchase request for 2,000 battery packs", hold=1.2)
        k.open_("PUR-PR-01", "Request entry"); k.cap("Purchase › Request entry", hold=0.5)
        k.type("itm_cd", "BAT-500"); k.press("Fetch")
        k.cap(f"Fetch fills the cost centre: {k.val('cc_cd')}. It closed on 15 Oct, and nothing on screen says so", "trap", hold=3.0)
        k.type("qty", "2000"); k.type("need_dt", "09-11-2026")
        k.press("Save")
        pr_no = k.val("pr_no")
        k.cap(f"Save: {k.status()} (a Draft)", hold=1.6)
        k.press("Submit")
        est = float(k.val("est_value") or 0)
        k.mark("poster")
        k.cap(f"Submitted. £{est:,.0f} is above Emma's £250,000 limit, so it waits for Daniel", "ok", hold=3.0)
        k.finish("m2_request", "Raise the purchase request", ["Fetch defaults the cost centre to PRD-05, closed on 15 Oct"])

        # ---------------- M3 approve (Daniel)
        k = Take("M3", "DOKAFOR", "Daniel")
        k.mark("start")
        k.cap("Daniel Okafor, purchase manager, approves at his own desk", hold=1.2)
        k.sign_in("DOKAFOR", "daniel@123")
        k.open_("PUR-PR-04", "Request approval"); k.cap("Purchase › Request approval", hold=0.5)
        k.press("Inbox"); k.cap("His approval inbox", hold=1.2)
        k.point(k.pg.locator(".grid tr[data-i]", has_text=pr_no).first, double=True)
        k.cap(f"Double-click {pr_no}", hold=0.6)
        k.press("Fetch")
        k.type("decision", "A"); k.cap("Decision: type A for approve (R would reject)", "trap", hold=1.6)
        k.type("comment", "ok")
        k.press("Confirm")
        k.mark("poster")
        k.cap(f"{k.status()}", "ok", hold=3.0)
        k.finish("m3_approve", "Approve it, as Daniel", ["the decision is a one-letter code (A or R)"])

        # ---------------- M4 order (Emma): the traps
        k = Take("M4", "ECLARKE", "Emma")
        k.sign_in("ECLARKE", "emma@123", on_camera=False)
        k.mark("start")
        k.cap("Turn the approved request into an order with Voltway Cells, and release it", hold=1.0)
        k.open_("PUR-PO-01", "Order entry"); k.cap("Purchase › Order entry", hold=0.5)
        k.type("pr_no", pr_no)
        k.mark("voltway")
        k.cap("Which supplier code? Press F2 next to SUP CD", hold=0.3)
        k.point(k.pg.locator("#f_sup_cd + .f2"))
        k.pg.wait_for_timeout(400)
        k.point(k.pg.locator("#lkq")); k.pg.keyboard.type("Voltway", delay=55)
        k.point(k.pg.locator("#lkgo")); k.pg.wait_for_timeout(600)
        lk = k.pg.locator("#lkgrid tr[data-i]").count()
        k.cap(f"{lk} Voltways: the right one, a blocked old code and a paint company in Rotterdam", "trap", hold=2.6)
        k.point(k.pg.locator("#lkok")); k.pg.wait_for_timeout(400)
        k.mark("voltway_end")
        k.type("itm_cd", "BAT-500")
        k.press("Fetch")
        k.mark("tax")
        k.cap(f"Fetch fills tax code {k.val('tax_cd')} and cost centre {k.val('cc_cd')}. Emma keeps them", hold=2.0)
        k.press("Save")
        k.cap("ERR-PO-0412: tax code does not match supplier country", "err", hold=2.4)
        k.cap("Voltway is in the Netherlands: the order needs VAT20-RC (reverse charge). She phones IT", "trap", hold=1.8)
        k.type("tax_cd", "VAT20-RC", replace=True)
        k.mark("tax_end")
        k.mark("draft")
        k.press("Save")
        po_no = k.val("po_no")
        k.point(k.pg.locator("#f_status"), click=False)
        k.mark("poster")
        k.cap(f"The status bar says {po_no} SAVED. The status field says {k.val('status')}: a Draft", "trap", hold=2.6)
        k.cap("PRD-05 is closed, so Ledgerline silently kept the order as a Draft. It never reaches Voltway", "err", hold=2.0)
        k.open_("PUR-POR-05", "Order release"); k.cap("Days later: Purchase › Order release", hold=0.3)
        k.type("po_no", po_no); k.press("Fetch"); k.press("Release")
        k.cap("ERR-PO-0715: document not in releasable status (DR)", "err", hold=2.4)
        k.mark("draft_end")
        k.mark("fix")
        k.open_("PUR-POM-06", "Order amendment"); k.cap("The fix: Purchase › Order amendment", hold=0.3)
        k.type("po_no", po_no); k.press("Fetch")
        k.type("cc_cd", "PRD-07", replace=True); k.press("Amend")
        k.cap(f"Cost centre PRD-07, the spring launch run: {k.status()}", hold=1.4)
        k.open_("PUR-POR-05", "Order release")
        k.type("po_no", po_no); k.press("Fetch"); k.press("Release")
        k.cap(f"{k.status()}: now Voltway has the order", "ok", hold=2.6)
        k.mark("fix_end")
        k.finish("m4_order", "Make and release the order",
                 ["which Voltway (VC-EIN-0042, blocked VC-EIN-0009, Voltway Paints & Coatings)",
                  "ERR-PO-0412: Fetch's UK tax code on an overseas supplier",
                  "the silent Draft: SAVED on screen, DR in the status field, because PRD-05 is closed",
                  "ERR-PO-0715: release refused; fixed by amending the cost centre to PRD-07"],
                 clips=[("m4_trap_voltway", "voltway", "voltway_end", "F2 lookup: three Voltways"),
                        ("m4_trap_tax", "tax", "tax_end", "Fetch's defaults kept; Save gives ERR-PO-0412"),
                        ("m4_trap_draft", "draft", "draft_end", "SAVED but Draft; release refused with ERR-PO-0715"),
                        ("m4_fix", "fix", "fix_end", "order amendment to PRD-07, then RELEASED")])

        # ---------------- M5 receive (Aiko)
        k = Take("M5", "ATANAKA", "Aiko")
        k.mark("start")
        k.cap("Voltway's truck is here. Aiko Tanaka at stores records the delivery", hold=1.2)
        k.sign_in("ATANAKA", "aiko@123")
        k.open_("INV-GRN-03", "Goods receipt"); k.cap("Inventory › Goods receipt", hold=0.5)
        for q, dn, msg in ((1200, "DN-4471", "Morning: 1,200 packs, delivery note DN-4471"),
                           (800, "DN-4486", "4 pm: the other 800, delivery note DN-4486")):
            k.cap(msg, hold=0.8)
            k.type("po_no", po_no, replace=True); k.press("Fetch")
            k.type("qty", str(q), replace=True); k.type("remarks", dn, replace=True)
            k.press("Save")
            bal = k.val("balance")
            if q == 800:
                k.mark("poster")
            k.cap(f"{k.status()} · balance {int(float(bal or 0)):,}", "ok", hold=2.2)
        k.finish("m5_receive", "Receive the goods, as Aiko", ["the PO number is typed again for each delivery"])

        # ---------------- "A button calls a service": Fetch on the purchase-order screen
        t = "button"
        cli = httpx.Client(base_url=BASE, headers={"X-Tenant": t})
        def tok(u, pw):
            return cli.post("/login", json={"user_id": u, "password": pw, "ou_cd": "NBC-MAN-01"}).json()["token"]
        te, td = tok("ECLARKE", "emma@123"), tok("DOKAFOR", "daniel@123")
        prb = cli.post("/svc/pr_save", headers={"Authorization": f"Bearer {te}"},
                       json={"pr_type": "STD", "cc_cd": "PRD-05", "need_dt": "09-11-2026", "itm_cd": "BAT-500", "qty": "2000",
                             "whs_cd": "WH-MAN-STR", "est_rate": "114.00"}).json()["data"]["pr_no"]
        cli.post("/svc/pr_submit", headers={"Authorization": f"Bearer {te}"}, json={"pr_no": prb})
        cli.post("/svc/pr_approve", headers={"Authorization": f"Bearer {td}"}, json={"pr_no": prb, "decision": "A", "comment": "ok"})
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto(f"{BASE}/legacy?tenant={t}", wait_until="networkidle")
        pg.fill("#f_user_id", "ECLARKE"); pg.fill("#f_password", "emma@123")
        pg.click("#loginbtns button:has-text('Sign in')"); pg.wait_for_selector("#main:not(.hidden)")
        pg.click('.tree .it[data-code="PUR-PO-01"]'); pg.wait_for_timeout(300)
        for f, v in (("pr_no", prb), ("sup_cd", "VC-EIN-0042"), ("itm_cd", "BAT-500")):
            pg.fill(f"#f_{f}", v)
        btn = pg.locator("#btns button").filter(has_text=re.compile("^Fetch$")).first
        pg.wait_for_timeout(300)
        box = btn.bounding_box()
        fields = ["po_no", "pr_no", "sup_cd", "itm_cd", "rate", "tax_cd", "cc_cd", "qty", "need_dt", "whs_cd", "pt_cd", "status"]
        def form():
            return {f: pg.locator(f"#f_{f}").input_value() for f in fields if pg.locator(f"#f_{f}").count()}
        before_form = form()
        out["figs/legacy/button_before.png"] = pg.screenshot()
        seen = {}
        def on_req(r):
            if "/svc/po_fetch" in r.url:
                h = r.headers
                seen["request"] = {"method": r.method, "path": "/svc/po_fetch",
                                   "headers": {k_: ("Bearer <token>" if k_ == "authorization" else v_) for k_, v_ in h.items()
                                               if k_ in ("x-screen", "x-task", "x-tenant", "content-type", "authorization")},
                                   "body": json.loads(r.post_data or "{}")}
        def on_resp(r):
            if "/svc/po_fetch" in r.url:
                seen["response"] = {"status": r.status, "body": r.json()}
        pg.on("request", on_req); pg.on("response", on_resp)
        btn.click(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(500)
        after_form = form()
        out["figs/legacy/button_after.png"] = pg.screenshot()
        screen = srv.load_screens()["PUR-PO-01"]
        task = next(x for x in screen.get("tasks", []) if x["button"] == "Fetch")
        dsf = 2
        out["experiments/logs/button_service.json"] = json.dumps({
            "what": "One real button press in the legacy client: Fetch on PUR-PO-01 (purchase order entry), as Emma",
            "screen": "PUR-PO-01", "button": "Fetch", "pr_no": prb,
            "screen_definition_of_the_button": task,
            "images": {"before": "figs/legacy/button_before.jpg", "after": "figs/legacy/button_after.jpg",
                       "width": 1280 * dsf, "height": 800 * dsf, "device_scale_factor": dsf},
            "button_box_css_px": {k_: round(v_, 1) for k_, v_ in box.items()},
            "button_box_image_px": {k_: round(v_ * dsf, 1) for k_, v_ in box.items()},
            "button_box_fraction": {"x": round(box["x"] / 1280, 4), "y": round(box["y"] / 800, 4),
                                    "width": round(box["width"] / 1280, 4), "height": round(box["height"] / 800, 4)},
            "request": seen.get("request"), "response": seen.get("response"),
            "form_before": before_form, "form_after": after_form,
            "fields_filled_by_the_press": {f: after_form[f] for f in after_form if after_form[f] != before_form.get(f)},
            "status_bar_after": pg.locator("#msg").inner_text(),
        }, indent=1, ensure_ascii=False).encode()
        ctx.close()
        b.close()
    server.should_exit = True

    import io

    from PIL import Image
    for rel in [r for r in out if r.endswith(".png")]:
        im = Image.open(io.BytesIO(out.pop(rel))).convert("RGB")
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
        out[rel[:-4] + ".jpg"] = buf.getvalue()
    out["figs/missions/missions.json"] = json.dumps({
        "what": "The five Before missions played the first-time way in the Ledgerline ERP 7.2 legacy client (headless "
                "Chromium on Modal, 1600x900, H.264 faststart). Captions, cursor and click rings are overlaid live on the page.",
        "made_by": "lectures/L1-before-and-after/experiments/mission_videos.py", "missions": missions,
    }, indent=1, ensure_ascii=False).encode()
    # a contact sheet of frames for checking (not for the deck)
    for m in missions:
        src = work / m["file"]
        ff("-i", str(src), "-vf", f"fps=1/{max(1, int(m['duration_s'] // 8))},scale=400:-1,tile=4x3", "-frames:v", "1",
           str(work / (m["id"] + "_sheet.jpg")))
        out[f"_check/{m['id']}_sheet.jpg"] = (work / (m["id"] + "_sheet.jpg")).read_bytes()
    return out


@app.local_entrypoint()
def main():
    lec = HERE.parent
    scratch = pathlib.Path("/private/tmp/claude-501/-Users-raj-Claude-Brain/e88f1a06-3b0d-4a9f-9baf-ed78173dbc73/scratchpad")
    for rel, data in record.remote().items():
        dst = (scratch / rel) if rel.startswith("_check/") else (lec / rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", dst, len(data) // 1024, "KB")
