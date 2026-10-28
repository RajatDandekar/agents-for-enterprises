"""Lecture 1 v3: real screenshots of Bahi ERP 7.2's legacy client, taken headless on Modal.

Starts the Bahi server (bahi.server, with the Experience's order-amendment screen PUR-POM-06 added), opens the legacy
client at /legacy in Chromium, and plays the Before missions the way a person would: click the menu, type in the
fields, press the buttons. Every screenshot is the client as it really rendered. Nothing on the laptop.

    /Users/raj/.venv/bin/modal run lectures/L1-before-and-after/experiments/legacy_shots.py
-> figs/legacy/*.png and logs/legacy_shots.json (what each shot shows, with the status bar text read off the page)
"""
import json
import pathlib
import re

import modal

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2] if modal.is_local() else pathlib.Path("/course")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("playwright==1.47.0", "fastapi", "uvicorn", "httpx", "pyyaml", "pydantic>=2", "openai", "pandas")
         .run_commands("playwright install --with-deps chromium")
         .env({"PYTHONPATH": "/course/bahi"})
         .add_local_dir(ROOT / "bahi", "/course/bahi", ignore=lambda p: any(x in ("cassettes", "__pycache__", "_index")
                                                                              for x in pathlib.Path(p).parts)))
app = modal.App("l1v3-legacy-shots", image=image)


@app.function(timeout=900, cpu=2, memory=4096)
def shoot() -> dict:
    import threading
    import time

    import uvicorn
    import yaml
    from playwright.sync_api import sync_playwright

    import bahi.server as srv
    base_load = srv.load_screens
    amend = yaml.safe_load(pathlib.Path("/course/bahi/bahi/experience/screens/PUR-POM-06.yaml").read_text())
    srv.load_screens = lambda modules=(): {**base_load(modules), "PUR-POM-06": amend}
    from bahi.erp.engine import ERP
    from bahi.erp.receipts import install_receipts

    def rasoi():  # a Rasoi with goods receipt installed, as the Experience serves it
        e = ERP()
        install_receipts(e)
        return e
    app_ = srv.create_app(rasoi)
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

        # ---------------- the first-time run (Fetch's defaults kept)
        go("first")
        fill(user_id="KJOSHI", password="kavita@123")
        snap("01_signin", "Kavita signs in (screen SYS-LGN-01)", "#login")
        sign_in("KJOSHI", "kavita@123")
        snap("02_home", "The main window: a menu tree of screens, nothing else")
        open_("INV-ITM-03"); fill(q="gasket 5"); press("Search")
        snap("03_item_search", "Item enquiry: four gaskets look alike")
        pick(i=0)
        open_("INV-STK-02"); fill(itm_cd="GSK-SIL-05L"); press("Query")
        snap("04_stock", "Stock status: 54,000 on hand, 6,000 a day, 9 days of cover (one warehouse)")
        open_("PUR-PR-01"); fill(itm_cd="GSK-SIL-05L"); press("Fetch")
        snap("05_pr_fetch", "Request entry after Fetch: cost centre PRD-05 filled in by default")
        fill(qty="20000", need_dt="09-11-2026", remarks="Diwali run"); press("Save"); press("Submit")
        snap("06_pr_submitted", "Request saved and submitted: above Kavita's limit, so it waits for Rohit")
        sign_out(); sign_in("RMEHTA", "rohit@123")
        open_("PUR-PR-04"); press("Inbox")
        snap("07_rohit_inbox", "Rohit, at his own desk: the approval inbox")
        pick("PR/2026/04417"); press("Fetch"); fill(decision="A", comment="ok"); press("Confirm")
        snap("08_rohit_approved", "Rohit types A and presses Confirm")
        sign_out(); sign_in("KJOSHI", "kavita@123")
        open_("PUR-POH-02"); fill(itm_cd="GSK-SIL-05L"); press("Query")
        snap("09_po_history", "Order history: to find the supplier's code")
        open_("PUR-PO-01"); fill(pr_no="PR/2026/04417", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L")
        pg.locator("#f_sup_cd + .f2").click(); pg.fill("#lkq", "Deccan"); pg.click("#lkgo"); pg.wait_for_timeout(500)
        shots["figs/legacy/10_f2_deccan.png"] = pg.screenshot()
        meta.append({"shot": "10_f2_deccan", "what": "F2 supplier lookup for 'Deccan': three rows, one blocked duplicate, one near-match"})
        pg.keyboard.press("Escape")
        press("Fetch")
        snap("11_po_fetch", "Order entry after Fetch: tax code GST18-INTRA and cost centre PRD-05 by default")
        press("Save")
        snap("12_po_err0412", "Save: ERR-PO-0412, a tax code for the wrong state")
        fill(tax_cd="GST18-INTER"); press("Save")
        snap("13_po_saved_draft", "Save again: the status bar says SAVED; the status field says DR (Draft)")
        open_("PUR-POR-05"); fill(po_no="PO/2026/01182"); press("Fetch"); press("Release")
        snap("14_release_refused", "Release: ERR-PO-0715, the order is a Draft and never reached the supplier")
        open_("PUR-POM-06"); fill(po_no="PO/2026/01182"); press("Fetch"); fill(cc_cd="PRD-07"); press("Amend")
        snap("15_amend", "Order amendment: cost centre PRD-07, and the order is approved")
        open_("PUR-POR-05"); fill(po_no="PO/2026/01182"); press("Fetch"); press("Release")
        snap("16_released", "Release again: RELEASED, the supplier gets the order")
        sign_out(); sign_in("NDESAI", "neha@123")
        open_("INV-GRN-03"); fill(po_no="PO/2026/01182"); press("Fetch"); fill(qty="12000", remarks="DC-4471"); press("Save")
        snap("17_grn", "Neha's goods receipt: 12,000 counted in, 8,000 to come")
        # ---------------- a trap on its own: the direct-order cap
        sign_out(); go("trap"); sign_in("KJOSHI", "kavita@123")
        open_("PUR-PO-01"); fill(po_type="DIR", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L"); press("Fetch")
        fill(qty="20000", cc_cd="PRD-07", need_dt="09-11-2026", tax_cd="GST18-INTER"); press("Save")
        snap("18_direct_cap", "A direct order without a request: ERR-PO-0610 above Rs 50,000")
        open_("PUR-PO-01"); fill(sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty="100", rate="11.90",
                                 tax_cd="GST18-INTER", cc_cd="PRD-07", need_dt="09-11-2026"); press("Save")
        snap("19_no_fetch", "Save without Fetch: ERR-SCR-0221")
        b.close()
    server.should_exit = True
    shots["experiments/logs/legacy_shots.json"] = json.dumps(meta, indent=1, ensure_ascii=False).encode()
    return shots


@app.local_entrypoint()
def main():
    lec = HERE.parent
    for rel, data in shoot.remote().items():
        dst = lec / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print("wrote", dst.relative_to(ROOT))
