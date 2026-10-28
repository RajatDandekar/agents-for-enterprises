"""Playwright UI test of the Studio, headless on Modal, against tests/studio_app.py (the router in a minimal app).

    /Users/raj/.venv/bin/modal run bahi/bahi/experience/studio/tests/modal_studio.py --what ui

1. Template (a) "Diwali gasket order" on a fresh Rasoi: load it, run it (animated), pause for Rohit, open the
   approval, approve, finish, open a node's output.            -> shots 01..05
2. Build by hand on another fresh Rasoi: drag nodes from the palette, connect ports, configure fields (with the
   output picker), run, approve, finish.                       -> shot 06
3. Template (b) with its branch, and (e) the agent builder: tick tools, chat to it.  -> shots 07, 08
Screenshots are 1600x900, in studio/shots/.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
SHOTS = HERE.parent / "shots"
SHOTS.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8770"
results, errors = [], []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name + ("" if cond else f"  -- {str(detail)[:300]}"), flush=True)


def shot(page, name):
    page.wait_for_timeout(350)
    page.screenshot(path=str(SHOTS / name))
    print("     shot", name, flush=True)


def center(page, selector):
    b = page.locator(selector).first.bounding_box()
    return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2


def drag(page, src, dst_xy, steps=12):
    page.locator(src).first.scroll_into_view_if_needed()
    x, y = center(page, src)
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + 10, y + 4, steps=3)
    page.mouse.move(*dst_xy, steps=steps)
    page.mouse.up()
    page.wait_for_timeout(250)


def connect(page, a, b, port="out"):
    drag(page, f'.node[data-id="{a}"] .port.out[data-port="{port}"]', center(page, f'.node[data-id="{b}"] .port.in'))


def state(page, expr):
    return page.evaluate(f"() => {{ const S = window.__studio; return {expr}; }}")


def wait_status(page, statuses, timeout=60000):
    page.wait_for_function("(st) => window.__studio.run && st.includes(window.__studio.run.status) && !window.__studio.running",
                           arg=statuses, timeout=timeout)
    return state(page, "S.run.status")


def new_page(browser):
    ctx = browser.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    return page


srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "bahi.experience.studio.tests.studio_app:app", "--port", "8770",
                        "--log-level", "warning"], cwd=str(HERE.parents[3]))
for _ in range(60):
    try:
        import urllib.request
        urllib.request.urlopen(BASE + "/api/studio/templates", timeout=1)
        break
    except Exception:
        time.sleep(0.5)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ---------------------------------------------------------------- 1. template (a) end to end
        print("\n1. Template (a): Diwali gasket order", flush=True)
        page = new_page(browser)
        page.goto(BASE + "/studio", wait_until="networkidle")
        page.wait_for_selector(".tcard[data-template]")
        check("first visit shows the template gallery", page.locator(".tcard[data-template]").count() == 5)
        shot(page, "00_welcome_templates.png")
        page.click('.tcard[data-template="diwali-gasket-order"]')
        page.wait_for_selector('.node[data-id="tell"]')
        page.wait_for_timeout(500)
        check("template (a) on the canvas: 7 nodes, 6 edges", page.locator(".node").count() == 7
              and page.locator("path.edge-hit").count() == 6)
        page.click('.node[data-id="pr"] .nhead')
        page.wait_for_selector("#inspector:not([hidden])")
        check("the PR node's panel shows its fields from tool.json", page.locator('#ibody input[data-field="quantity"]').input_value() == "20000"
              and page.locator('[data-toggle="confirm"].on').count() == 1)
        shot(page, "01b_node_config_panel.png")
        page.click("#inspector .x")
        page.click("#zoomFit")
        shot(page, "01_canvas_template.png")
        page.click("#btnRun")
        page.wait_for_function("() => { const r = window.__studio.run; return r && r.nodes.pr && r.nodes.pr.status === 'done' && "
                               "Object.values(r.nodes).some(n => n.status === 'running'); }", timeout=30000)
        shot(page, "02_run_in_progress.png")
        st = wait_status(page, ["waiting", "failed", "done"])
        check("the run pauses for Rohit", st == "waiting" and state(page, "S.run.waiting_for.approver") == "RMEHTA", st)
        check("the approval node says who it waits for", "Waiting for Rohit Mehta" in page.locator('.node[data-id="rohit"] .nres').inner_text())
        shot(page, "03_waiting_for_rohit.png")
        page.click('.node[data-id="rohit"] [data-act=approve]')
        page.wait_for_selector("#approveBtn")
        check("the approval sheet shows PR/2026/04417 and its value", "PR/2026/04417" in page.inner_text("#sheet")
              and "2,69,040" in page.inner_text("#sheet"), page.inner_text("#sheet")[:300])
        shot(page, "04_approval_sheet.png")
        page.click("#approveBtn")
        st = wait_status(page, ["done", "failed"])
        check("after approval the run finishes", st == "done", state(page, "S.run.error"))
        check("PO/2026/01182 released", state(page, "S.run.nodes.release.output.status") == "RELEASED"
              or "RELEASED" in str(state(page, "S.run.nodes.release.output.status")), state(page, "S.run.nodes.release.output"))
        page.click('.node[data-id="po"] .nres')
        page.wait_for_selector('pre[data-output="po"]')
        check("clicking a node shows its output JSON", "PO/2026/01182" in page.inner_text('pre[data-output="po"]'))
        shot(page, "05_finished_with_outputs.png")
        page.click('.itab[data-tab="run"]')
        page.wait_for_timeout(500)
        shot(page, "05b_run_log.png")
        page.context.close()

        # ---------------------------------------------------------------- 2. build by hand
        print("\n2. Build a workflow by hand: drag, connect, configure, run, approve", flush=True)
        page = new_page(browser)
        page.goto(BASE + "/studio", wait_until="networkidle")
        page.wait_for_selector(".tcard")
        page.click("text=Start from scratch")
        page.wait_for_selector('.node[data-id="start"]')
        page.click("#inspector .x")
        cb = page.locator("#canvas").bounding_box()
        drag(page, '.pitem[data-key="tool:check_stock"]', (cb["x"] + 330, cb["y"] + 300))
        drag(page, '.pitem[data-key="tool:create_purchase_request"]', (cb["x"] + 565, cb["y"] + 300))
        drag(page, '.pitem[data-key="approval"]', (cb["x"] + 800, cb["y"] + 300))
        check("three nodes dropped from the palette", state(page, "S.wf.nodes.map(n => n.id).join(',')") == "start,stock,pr,approval",
              state(page, "S.wf.nodes.map(n => n.id).join(',')"))
        page.click("#inspector .x")
        connect(page, "start", "stock")
        connect(page, "stock", "pr")
        connect(page, "pr", "approval")
        check("three edges drawn by dragging ports", state(page, "S.wf.edges.length") == 3, state(page, "JSON.stringify(S.wf.edges)"))
        # configure check_stock
        page.click('.node[data-id="stock"] .nhead')
        page.fill('#ibody input[data-field="item_code"]', "GSK-SIL-05L")
        # configure the PR: item from the stock node via the output picker
        page.click('.node[data-id="pr"] .nhead')
        page.locator('#ibody input[data-field="item_code"]').click()
        page.locator('#ibody input[data-field="item_code"]').locator("xpath=..").locator(".ref").click()
        page.wait_for_selector('#picker:not([hidden]) .pk[data-path="nodes.stock.item_code"]')
        shot(page, "06a_output_picker.png")
        page.click('.pk[data-path="nodes.stock.item_code"]')
        page.fill('#ibody input[data-field="quantity"]', "20000")
        page.fill('#ibody input[data-field="cost_centre"]', "PRD-07")
        page.fill('#ibody input[data-field="need_by"]', "2026-11-09")
        page.click('[data-toggle="confirm"]')
        check("the picker wrote the template", state(page, "S.wf.nodes.find(n => n.id === 'pr').config.args.item_code") == "{{nodes.stock.item_code}}")
        check("the quantity is stored as a number", state(page, "S.wf.nodes.find(n => n.id === 'pr').config.args.quantity") == 20000)
        page.click('.node[data-id="approval"] .nhead')
        page.locator('#ibody input[data-field="doc_no"]').locator("xpath=..").locator(".ref").click()
        page.click('.pk[data-path="nodes.pr.request_no"]')
        # one more node by clicking a palette item: it is added after the selected node and joined to it
        page.click('.pitem[data-key="message"]')
        page.fill('#ibody input[data-field="to"]', "@rohit")
        page.fill('#ibody textarea[data-field="text"]', "{{nodes.approval.doc_no}} approved by Rohit.")
        check("clicking a palette item adds and joins it", state(page, "S.wf.edges.some(e => e.from === 'approval' && e.to === 'message')"))
        page.click("#zoomFit")
        page.wait_for_timeout(1300)  # autosave
        page.click("#btnRun")
        st = wait_status(page, ["waiting", "failed", "done"])
        check("the hand-built workflow pauses at the approval", st == "waiting", state(page, "S.run.error"))
        shot(page, "06_built_by_hand_waiting.png")
        page.click("#barApprove")
        page.click("#approveBtn")
        st = wait_status(page, ["done", "failed"])
        check("the hand-built workflow finishes after approval", st == "done", state(page, "S.run.error"))
        check("its message node sent the PR number", "PR/2026/04417" in str(state(page, "S.run.nodes.message.output.text")))
        shot(page, "06b_built_by_hand_done.png")
        # the saved workflow survives a reload
        page.reload(wait_until="networkidle")
        page.wait_for_selector('.node[data-id="message"]')
        check("the workflow was saved (reload keeps 5 nodes)", page.locator(".node").count() == 5)
        page.context.close()

        # ---------------------------------------------------------------- 3. (b) branch, and (e) agent builder
        print("\n3. Template (b) and the agent builder", flush=True)
        page = new_page(browser)
        page.goto(BASE + "/studio", wait_until="networkidle")
        page.wait_for_selector(".tcard")
        page.click('.tcard[data-template="reorder-when-low"]')
        page.wait_for_selector('.node[data-id="note"]')
        page.click("#btnRun")
        st = wait_status(page, ["waiting", "failed", "done"])
        check("(b) fires on WHS-STD-01 and waits for Rohit", st == "waiting"
              and state(page, "S.run.nodes.low.output.item_code") == "WHS-STD-01", st)
        check("(b) the no branch is skipped", state(page, "S.run.nodes.note.status") == "skipped")
        page.click("#barApprove")
        page.click("#approveBtn")
        st = wait_status(page, ["done", "failed"])
        check("(b) finishes", st == "done", state(page, "S.run.error"))
        shot(page, "07_reorder_branch_done.png")
        page.context.close()

        page = new_page(browser)
        page.goto(BASE + "/studio", wait_until="networkidle")
        page.wait_for_selector(".tcard")
        page.click('.tcard[data-template="goods-arrived"]')
        page.wait_for_selector('.node[data-id="grn"]')
        page.click("#btnRun")
        page.wait_for_selector('#sheet input[data-field="po_no"]')
        check("(c) Run opens the form with its fields", page.locator("#sheet input[data-field]").count() == 3)
        page.fill('#sheet input[data-field="quantity"]', "25000")
        shot(page, "09a_form_trigger.png")
        page.click("#formStart")
        st = wait_status(page, ["done", "failed"])
        check("(c) the form run records the GRN as Neha", st == "done"
              and state(page, "S.run.nodes.grn.output.balance") == 15000, state(page, "S.run.error"))
        page.click("#btnTemplates")
        page.click('.tcard[data-template="dealer-email-to-order"]')
        page.wait_for_selector('.node[data-id="extract"]')
        page.click("#btnRun")
        st = wait_status(page, ["done", "failed"], timeout=120000)
        check("(d) the LLM node reads the dealer's email and the PR is raised", st == "done"
              and state(page, "S.run.nodes.extract.output.quantity") == 4000, state(page, "S.run.error"))
        page.click('.node[data-id="extract"] .nres')
        page.wait_for_selector('pre[data-output="extract"]')
        shot(page, "09_dealer_email_llm.png")
        page.context.close()

        page = new_page(browser)
        page.goto(BASE + "/studio", wait_until="networkidle")
        page.wait_for_selector(".tcard")
        page.click('.tcard[data-template="build-your-own-agent"]')
        page.wait_for_selector('.node[data-id="desk"]')
        page.click('.node[data-id="desk"] .nhead')
        page.wait_for_selector('#ibody input[data-tool="send_message"]')
        page.check('#ibody input[data-tool="find_supplier"]')
        page.uncheck('#ibody input[data-tool="find_supplier"]')
        check("the agent panel lists every tool to tick", page.locator("#ibody input[data-tool]").count() == 15)
        shot(page, "08a_agent_builder_config.png")
        page.click("#btnRun")  # "Open chat"
        page.wait_for_selector("#chatInput")
        page.fill("#chatInput", "How many days of cover do we have for the 5 litre silicone gasket?")
        page.click("#chatSend")
        page.wait_for_function("() => document.querySelectorAll('.msg.assistant:not(.typing)').length >= 1 && !window.__studio.running",
                               timeout=120000)
        reply = page.locator(".msg.assistant").last.inner_text()
        check("the agent replies with tool calls shown", page.locator(".msg .call").count() >= 1 and any(c.isdigit() for c in reply), reply)
        print("     agent:", reply[:300].replace("\n", " "))
        shot(page, "08_agent_builder_chat.png")
        page.context.close()
        browser.close()
finally:
    srv.terminate()

bad = [e for e in errors if "favicon" not in e]
check("no page errors", not bad, bad[:5])
passed = sum(ok for _, ok in results)
(HERE / "logs").mkdir(exist_ok=True)
(HERE / "logs" / "ui.json").write_text(json.dumps({"passed": passed, "total": len(results),
                                                   "fails": [n for n, ok in results if not ok], "errors": bad[:20]}, indent=1))
print(f"\n{passed}/{len(results)} UI checks passed")
sys.exit(0 if passed == len(results) else 1)
