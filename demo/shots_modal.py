"""Screenshots of the before and the after, rendered on Modal in headless Chromium (never on the laptop).

    /Users/raj/.venv/bin/modal run demo/shots_modal.py

BEFORE: the legacy client (bahi.server, /legacy) on its own sandbox. Kavita signs in, looks up the stock, and enters
the order screen by screen; the request and Rohit's approval are made through the same screens by the driver
(bahi.legacy_ui.driver, the one Lecture 1 counted with). Photographed: the sign-in, the stock enquiry, the tax
error (ERR-PO-0412), the silent Draft ("PO/2026/01182 SAVED", status DR), and Friday's refused release (ERR-PO-0715).
AFTER: the reference app (bahi.app) replaying the final demo's recorded model replies (cassette L8_demo, replay mode:
no key, no spend). Photographed: the one question, the preview, the wait on Rohit, Rohit's inbox and Slack-style
message, the released order, and the audit viewer. PNGs go to demo/shots/.
"""
import os
import pathlib

import modal

_P = pathlib.Path(__file__).resolve()
ROOT = _P.parents[1] if len(_P.parents) > 1 and (_P.parents[1] / "bahi").exists() else pathlib.Path("/course")
SKIP = {".git", "node_modules", "__pycache__", ".ipynb_checkpoints", "qa", "shots"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("openai>=1.50", "fastapi", "uvicorn", "httpx", "pydantic>=2", "pyyaml", "pandas", "langgraph>=0.2",
                 "langchain-core", "fastmcp", "mcp", "temporalio", "rank_bm25", "numpy", "playwright==1.47.0")
    .run_commands("playwright install --with-deps chromium")
    .env({"PYTHONPATH": "/course/bahi", "BAHI_IN_MODAL": "1", "BAHI_LLM_MODE": "replay"})
    .add_local_dir(ROOT, "/course", ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts)
                   or str(p).endswith((".ipynb", ".mp4", ".png", ".mov", ".zip")))
)
app = modal.App("forms-to-agents-l8-shots", image=image)


@app.function(timeout=1500, cpu=2, memory=4096)
def shots() -> dict:
    import threading
    import time

    import httpx
    import uvicorn
    from playwright.sync_api import sync_playwright

    os.environ["BAHI_LLM_MODE"] = "replay"
    from bahi.app.journey import OPENING, kavita_answer
    from bahi.app.main import create_app
    from bahi.legacy_ui.driver import Desk, Tally
    from bahi.server import create_app as create_legacy

    def serve(asgi, port):
        srv = uvicorn.Server(uvicorn.Config(asgi, host="127.0.0.1", port=port, log_level="warning"))
        threading.Thread(target=srv.run, daemon=True).start()
        while not srv.started:
            time.sleep(0.1)
        return f"http://127.0.0.1:{port}"

    legacy_base = serve(create_legacy(), 8092)
    web = create_app(cassette="L8_demo", durable=True, mcp=True)
    app_base = serve(web, 8093)
    out, log = {}, []

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)

        def snap(name, settle=1.2):
            time.sleep(settle)
            out[name] = pg.screenshot()
            print("snap", name, flush=True)

        # ---------------- BEFORE: the legacy client
        def btn(text, host="#btns"):
            pg.click(f"{host} button:text-is('{text}')")
            time.sleep(1.0)

        def open_screen(code):
            pg.click(f".tree .it[data-code='{code}']")
            time.sleep(0.6)

        def status():
            return pg.inner_text("#msg")

        pg.goto(legacy_base + "/legacy", wait_until="domcontentloaded")
        pg.wait_for_selector("#f_user_id")
        pg.fill("#f_user_id", "KJOSHI")
        pg.fill("#f_password", "kavita@123")
        snap("legacy_signin")
        btn("Sign in", "#loginbtns")
        pg.wait_for_selector("#main:not(.hidden)")
        open_screen("INV-STK-02")
        pg.fill("#f_itm_cd", "GSK-SIL-05L")
        btn("Query")
        log.append("stock: " + status())
        snap("legacy_stock")
        # the request and Rohit's approval, through the same screens, by the driver
        http, tally = httpx.Client(base_url=legacy_base, timeout=60), Tally()
        kav = Desk(http, tally, "Kavita").sign_in("KJOSHI", "kavita@123")
        s = kav.open("PUR-PR-01").type(itm_cd="GSK-SIL-05L").press("Fetch")
        s.type(qty="20000", need_dt="02-11-2026", remarks="Diwali run").press("Save")
        pr_no = s.form["pr_no"]
        s.press("Submit")
        roh = Desk(http, tally, "Rohit").sign_in("RMEHTA", "rohit@123")
        s = roh.open("PUR-PR-04").press("Inbox")
        row = next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr_no)
        s.pick(row).press("Fetch").type(decision="A", comment="ok").press("Confirm")
        log.append(f"{pr_no}: {s.status}")
        # the order, in the browser
        open_screen("PUR-PO-01")
        pg.fill("#f_pr_no", pr_no)
        pg.fill("#f_sup_cd", "DP-RJK-0042")
        pg.fill("#f_itm_cd", "GSK-SIL-05L")
        btn("Fetch")
        btn("Save")
        log.append("save 1: " + status())
        snap("legacy_tax_error")
        pg.fill("#f_tax_cd", "GST18-INTER")
        btn("Save")
        log.append("save 2: " + status() + " · STATUS " + pg.input_value("#f_status"))
        po_no = pg.input_value("#f_po_no")
        snap("legacy_saved_draft")
        open_screen("PUR-POR-05")
        pg.fill("#f_po_no", po_no)
        btn("Fetch")
        btn("Release")
        log.append("release: " + status())
        snap("legacy_release_refused")

        # ---------------- AFTER: the reference app (recorded replies)
        c = httpx.Client(base_url=app_base, timeout=300)
        K = c.post("/login", json={"user_id": "KJOSHI", "password": "kavita@123"}).json()["token"]
        hk = {"Authorization": f"Bearer {K}"}
        conv = c.post("/api/chat", headers=hk).json()["conv"]
        chat = f"{app_base}/app/chat#token={K}&conv={conv}"
        text, n = OPENING, 0
        for _ in range(7):
            r = c.post(f"/api/chat/{conv}/message", headers=hk, json={"text": text}).json()
            n += 1
            log.append(f"turn {n}: " + r["reply"][:120].replace("\n", " "))
            pg.goto("about:blank")
            pg.goto(chat, wait_until="domcontentloaded")
            pg.wait_for_selector(".msg.ag", timeout=20000)
            snap({1: "app_question", 2: "app_preview"}.get(n, "app_waiting"), 1.5)
            if r["waiting_on"]:
                break
            text = kavita_answer(r["reply"])
        R = c.post("/login", json={"user_id": "RMEHTA", "password": "rohit@123"}).json()["token"]
        hr = {"Authorization": f"Bearer {R}"}
        pg.goto(f"{app_base}/app/inbox#token={R}", wait_until="domcontentloaded")
        pg.wait_for_selector(".card", timeout=20000)
        snap("app_inbox", 1.5)
        pg.goto(f"{app_base}/app/slack#token={R}", wait_until="domcontentloaded")
        pg.wait_for_selector(".slack .m", timeout=20000)
        snap("app_slack", 1.5)
        item = [i for i in c.get("/api/inbox", headers=hr).json()["items"] if i.get("conv") == conv][-1]
        d = c.post(f"/api/inbox/{item['id']}", headers=hr, json={"decision": "approve", "comment": "ok, Diwali run"}).json()
        log.append("after tap: " + ((d.get("conversation") or {}).get("reply") or "")[:160].replace("\n", " "))
        pg.goto("about:blank")
        pg.goto(chat, wait_until="domcontentloaded")
        pg.wait_for_selector(".msg.ag", timeout=20000)
        snap("app_released", 1.5)
        pg.goto(f"{app_base}/app/audit#token={K}&conv={conv}", wait_until="domcontentloaded")
        pg.wait_for_selector("table", timeout=20000)
        snap("app_audit", 1.5)
        b.close()
    web.state.l5.close()
    return {"pngs": out, "log": log}


@app.local_entrypoint()
def main():
    res = shots.remote()
    d = ROOT / "demo" / "shots"
    d.mkdir(parents=True, exist_ok=True)
    for k, v in res["pngs"].items():
        (d / f"{k}.png").write_bytes(v)
        print("wrote", d / f"{k}.png", len(v))
    (d / "shots_log.txt").write_text("\n".join(res["log"]))
    print("\n".join(res["log"]))
