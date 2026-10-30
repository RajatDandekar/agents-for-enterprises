"""Lecture 1 v4 (Northbridge Cycles): real screenshots of Ledgerline ERP 7.2's legacy client, taken headless on Modal.

Starts the Ledgerline server (ledgerline.server; its screens include the order-amendment screen PUR-POM-06), opens the legacy
client at /legacy in Chromium, and plays the Before missions the way a person would: click the menu, type in the
fields, press the buttons. Every screenshot is the client as it really rendered. Nothing on the laptop.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/legacy_shots.py
-> figs/legacy/*.jpg (converted from PNG on Modal) and logs/legacy_shots.json (what each shot shows, with the status bar text read off the page)
"""
import json
import pathlib
import re

import modal

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2] if modal.is_local() else pathlib.Path("/course")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("playwright==1.47.0", "fastapi", "uvicorn", "httpx", "pyyaml", "pydantic>=2", "openai", "pandas", "pillow")
         .run_commands("playwright install --with-deps chromium")
         .env({"PYTHONPATH": "/course/ledgerline"})
         .add_local_dir(ROOT / "ledgerline", "/course/ledgerline", ignore=lambda p: any(x in ("cassettes", "__pycache__", "_index")
                                                                              for x in pathlib.Path(p).parts)))
app = modal.App("l1v4-legacy-shots", image=image)


@app.function(timeout=900, cpu=2, memory=4096)
def shoot() -> dict:
    import threading
    import time

    import uvicorn
    from playwright.sync_api import sync_playwright

    import ledgerline.server as srv  # the order-amendment screen PUR-POM-06 ships in erp/screens since 28 Oct
    from ledgerline.erp.engine import ERP
    from ledgerline.erp.receipts import install_receipts

    def northbridge():  # a Northbridge with goods receipt installed, as the Experience serves it
        e = ERP()
        install_receipts(e)
        return e
    app_ = srv.create_app(northbridge)
    server = uvicorn.Server(uvicorn.Config(app_, host="127.0.0.1", port=8077, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(0.1)

    shots, meta = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1100, "height": 720}, device_scale_factor=2)

        def go(tenant):
            pg.goto(f"http://127.0.0.1:8077/legacy?tenant={tenant}", wait_until="networkidle")
            pg.wait_for_selector("#f_user_id")

        def sign_in(uid, pw):
            pg.fill("#f_user_id", uid)
            pg.fill("#f_password", pw)
            pg.click("#loginbtns button:has-text('Sign in')")
            pg.wait_for_selector("#main:not(.hidden)")
            pg.wait_for_timeout(300)

        def sign_out():
            pg.evaluate("document.querySelector('[data-act=signout]').click()")
            pg.wait_for_selector("#login:not(.hidden)")

        def open_(code):
            pg.click(f'.tree .it[data-code="{code}"]')
            pg.wait_for_timeout(200)

        def fill(**kv):
            for k, v in kv.items():
                pg.fill(f"#f_{k}", str(v))

        def press(btn):
            pg.locator("#btns button").filter(has_text=re.compile(f"^{re.escape(btn)}$")).click()
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(350)

        def pick(text=None, i=0):
            row = pg.locator(".grid tr[data-i]", has_text=text).first if text else pg.locator(f'.grid tr[data-i="{i}"]').first
            row.dblclick()
            pg.wait_for_timeout(250)

        def snap(name, what, sel="#main"):
            pg.wait_for_timeout(250)
            el = pg.locator(sel)
            shots[f"figs/legacy/{name}.png"] = el.screenshot()
            bar = pg.locator("#msg").inner_text() if sel != "#login" else pg.locator("#loginmsg").inner_text()
            st = pg.locator("#f_status").input_value() if pg.locator("#f_status").count() else None
            meta.append({"shot": name, "what": what, "status_bar": bar, "status_field": st})
            print(f"{name:22} {bar[:70]:70} {st or ''}")

        def val(name):
            loc = pg.locator(f"#f_{name}")
            return loc.input_value() if loc.count() else None

        # ---------------- the first-time run (Fetch's defaults kept)
        go("first")
        fill(user_id="ECLARKE", password="emma@123")
        snap("01_signin", "Emma signs in (screen SYS-LGN-01)", "#login")
        sign_in("ECLARKE", "emma@123")
        snap("02_home", "The main window: a menu tree of screens, nothing else")
        open_("INV-ITM-03"); fill(q="battery pack 5"); press("Search")
        n_rows = pg.locator(".grid tr[data-i]").count()
        snap("03_item_search", f"Item enquiry: {n_rows} battery packs look alike")
        pick(i=0)
        open_("INV-STK-02"); fill(itm_cd="BAT-500"); press("Query")
        snap("04_stock", f"Stock status: {int(val('on_hand')):,} on hand, {int(val('avg_daily_issue')):,} a day, "
                         f"{val('cover_days')} days of cover (Manchester stores only)")
        open_("PUR-PR-01"); fill(itm_cd="BAT-500"); press("Fetch")
        snap("05_pr_fetch", f"Request entry after Fetch: cost centre {val('cc_cd')} filled in by default")
        fill(qty="2000", need_dt="09-11-2026", remarks="spring-launch run"); press("Save")
        pr_no = val("pr_no")
        press("Submit")
        snap("06_pr_submitted", "Request saved and submitted: above Emma's limit, so it waits for Daniel")
        sign_out(); sign_in("DOKAFOR", "daniel@123")
        open_("PUR-PR-04"); press("Inbox")
        snap("07_daniel_inbox", "Daniel, at his own desk: the approval inbox")
        pick(pr_no); press("Fetch"); fill(decision="A", comment="ok"); press("Confirm")
        snap("08_daniel_approved", "Daniel types A and presses Confirm")
        sign_out(); sign_in("ECLARKE", "emma@123")
        open_("PUR-POH-02"); fill(itm_cd="BAT-500"); press("Query")
        snap("09_po_history", "Order history: to find the supplier's code")
        open_("PUR-PO-01"); fill(pr_no=pr_no, sup_cd="VC-EIN-0042", itm_cd="BAT-500")
        pg.locator("#f_sup_cd + .f2").click(); pg.fill("#lkq", "Voltway"); pg.click("#lkgo"); pg.wait_for_timeout(500)
        shots["figs/legacy/10_f2_voltway.png"] = pg.screenshot()
        lk_rows = pg.locator("#lkgrid tr[data-i]").count()
        meta.append({"shot": "10_f2_voltway", "what": "F2 supplier lookup for 'Voltway': the right one, a blocked duplicate "
                     "(VC-EIN-0009) and a near-match (Voltway Paints & Coatings)", "lookup_rows": lk_rows})
        pg.keyboard.press("Escape")
        press("Fetch")
        snap("11_po_fetch", f"Order entry after Fetch: tax code {val('tax_cd')} and cost centre {val('cc_cd')} by default")
        press("Save")
        snap("12_po_err0412", "Save: ERR-PO-0412, a UK tax code on an order to a supplier in the Netherlands")
        fill(tax_cd="VAT20-RC"); press("Save")
        po_no = val("po_no")
        snap("13_po_saved_draft", f"Save again: the status bar says SAVED; the status field says {val('status')} (Draft)")
        open_("PUR-POR-05"); fill(po_no=po_no); press("Fetch"); press("Release")
        snap("14_release_refused", "Release: ERR-PO-0715, the order is a Draft and never reached the supplier")
        open_("PUR-POM-06"); fill(po_no=po_no); press("Fetch"); fill(cc_cd="PRD-07"); press("Amend")
        snap("15_amend", "Order amendment: cost centre PRD-07, and the order is approved")
        open_("PUR-POR-05"); fill(po_no=po_no); press("Fetch"); press("Release")
        snap("16_released", "Release again: RELEASED, the supplier gets the order")
        sign_out(); sign_in("ATANAKA", "aiko@123")
        open_("INV-GRN-03"); fill(po_no=po_no); press("Fetch"); fill(qty="1200", remarks="DN-4471"); press("Save")
        snap("17_grn", f"Aiko's goods receipt: 1,200 counted in (delivery note DN-4471), {int(float(val('balance') or 0)):,} to come")
        # ---------------- a trap on its own: the direct-order cap
        sign_out(); go("trap"); sign_in("ECLARKE", "emma@123")
        open_("PUR-PO-01"); fill(po_type="DIR", sup_cd="VC-EIN-0042", itm_cd="BAT-500"); press("Fetch")
        fill(qty="2000", cc_cd="PRD-07", need_dt="09-11-2026", tax_cd="VAT20-RC"); press("Save")
        snap("18_direct_cap", "A direct order without a request: ERR-PO-0610 above £50,000")
        open_("PUR-PO-01"); fill(sup_cd="VC-EIN-0042", itm_cd="BAT-500", qty="100", rate="119.00",
                                 tax_cd="VAT20-RC", cc_cd="PRD-07", need_dt="09-11-2026"); press("Save")
        snap("19_no_fetch", "Save without Fetch: ERR-SCR-0221")
        b.close()
    server.should_exit = True
    import io

    from PIL import Image
    out = {}
    for rel, png in shots.items():  # the deck shows JPEGs (figs.js: figs/legacy/<name>.jpg)
        im = Image.open(io.BytesIO(png)).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
        out[rel[:-4] + ".jpg"] = buf.getvalue()
    out["experiments/logs/legacy_shots.json"] = json.dumps(meta, indent=1, ensure_ascii=False).encode()
    return out


@app.local_entrypoint()
def main():
    lec = HERE.parent
    for rel, data in shoot.remote().items():
        dst = lec / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", dst.relative_to(ROOT))
