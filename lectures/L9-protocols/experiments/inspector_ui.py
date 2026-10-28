"""The click script for MCP Inspector 2.12.0's web UI (used by inspector_modal.py inside Modal).

Each step takes one screenshot and dumps what is on the page (buttons, inputs) into the log, so a step that
misses an element is easy to fix from the log alone.
"""
import re

INPUTS_JS = """() => [...document.querySelectorAll('input,textarea,select,[role=switch],[role=checkbox]')].map(e => {
  const lab = e.id ? document.querySelector(`label[for="${e.id}"]`) : null;
  return {tag: e.tagName, type: e.type, name: e.name, id: e.id, aria: e.getAttribute('aria-label'),
          ph: e.placeholder, label: lab ? lab.innerText.trim() : null, role: e.getAttribute('role'),
          visible: !!(e.offsetWidth || e.offsetHeight)};
}).filter(x => x.visible).slice(0, 60)"""
BUTTONS_JS = """() => [...document.querySelectorAll('button,[role=button]')].filter(e => e.offsetWidth)
  .map(e => (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 60)).filter(Boolean).slice(0, 80)"""


def look(pg, log, key):
    try:
        log.setdefault("ui", {})[key] = {"inputs": pg.evaluate(INPUTS_JS), "buttons": pg.evaluate(BUTTONS_JS),
                                         "text": pg.evaluate("document.body.innerText")[:2500]}
    except Exception as e:  # noqa: BLE001
        log.setdefault("ui", {})[key] = {"err": str(e)[:200]}


def fill_field(pg, scope, name, value):
    """Fill a form field whose label (or name / placeholder) is `name`."""
    for loc in (scope.get_by_label(name, exact=True), scope.get_by_label(re.compile(rf"^{name}\b")),
                scope.locator(f"[name='{name}']"), scope.get_by_placeholder(re.compile(name, re.I))):
        try:
            if loc.count():
                loc.first.fill(str(value), timeout=3000)
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def click_any(pg, scope, patterns, timeout=4000):
    for p in patterns:
        loc = scope.get_by_role("button", name=re.compile(p, re.I))
        try:
            if loc.count():
                loc.first.click(timeout=timeout)
                return p
        except Exception:  # noqa: BLE001
            continue
    return None


def tab(pg, name):
    loc = pg.get_by_role("tab", name=name)
    if loc.count():
        loc.first.click(timeout=5000)
    else:
        pg.locator("header").get_by_text(name, exact=True).first.click(timeout=5000)
    pg.wait_for_timeout(1200)


def step(log, name, fn):
    try:
        fn()
        log.setdefault("steps", {})[name] = "ok"
    except Exception as e:  # noqa: BLE001
        log.setdefault("steps", {})[name] = "failed: " + str(e)[:300]


def drive(pg, shot, log):
    # --- connect the stdio entry of our catalog (the deep link is not used in this mode)
    def connect():
        card = pg.locator("div").filter(has_text="rasoi-toolbox-stdio").filter(has=pg.get_by_role("switch")).last
        card.get_by_role("switch").first.click(timeout=8000, force=True)
        pg.wait_for_selector('[data-testid=connection-status][data-status=connected]', timeout=60000)
        pg.wait_for_timeout(2500)
        shot("inspector_01_connect", "Servers screen: rasoi-toolbox-stdio connected over stdio; right: the protocol messages")
        look(pg, log, "connected")
    step(log, "connect", connect)

    def conn_info():
        card = pg.locator("div").filter(has_text="rasoi-toolbox-stdio").filter(has=pg.get_by_role("switch")).last
        loc = card.get_by_role("button", name="Connection Info")
        (loc.first if loc.count() else pg.get_by_text("Connection Info", exact=True).first).click(timeout=5000)
        pg.wait_for_timeout(1500)
        shot("inspector_02_connection_info", "Connection Info: server name, protocol version, capabilities")
        look(pg, log, "conn_info")
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(600)
    step(log, "connection_info", conn_info)

    def tools_list():
        tab(pg, "Tools")
        shot("inspector_03_tools", "Tools (15): every tool.json folder, listed by tools/list")
    step(log, "tools_list", tools_list)

    def check_stock():
        pg.get_by_role("button", name=re.compile(r"^Check stock")).first.click(timeout=5000)
        pg.wait_for_timeout(1200)
        look(pg, log, "check_stock_form")
        fill_field(pg, pg, "item_code", "GSK-SIL-05L")
        used = click_any(pg, pg, [r"^run tool", r"^execute", r"^call", r"^run"])
        log["check_stock_button"] = used
        pg.wait_for_timeout(3000)
        shot("inspector_04_check_stock", "check_stock run on GSK-SIL-05L: the tool result JSON")
        look(pg, log, "check_stock_result")
    step(log, "check_stock", check_stock)

    def create_pr():
        pg.get_by_role("button", name=re.compile(r"^Create purchase request")).first.click(timeout=5000)
        pg.wait_for_timeout(1200)
        look(pg, log, "pr_form")
        for k, v in [("item_code", "GSK-SIL-05L"), ("quantity", "20000"), ("cost_centre", "PRD-07"),
                     ("need_by", "2026-11-09")]:
            log.setdefault("pr_fill", {})[k] = fill_field(pg, pg, k, v)
        # the confirm argument is a boolean: a checkbox, a switch or a select
        done = False
        for loc in (pg.get_by_label("confirm", exact=True), pg.get_by_role("checkbox", name=re.compile("confirm", re.I)),
                    pg.get_by_role("switch", name=re.compile("confirm", re.I))):
            try:
                if loc.count():
                    loc.first.check(timeout=3000)
                    done = True
                    break
            except Exception:  # noqa: BLE001
                try:
                    loc.first.click(timeout=3000)
                    done = True
                    break
                except Exception:  # noqa: BLE001
                    continue
        log["pr_fill"]["confirm"] = done
        shot("inspector_05_pr_form", "create_purchase_request filled in: 20,000 x GSK-SIL-05L on PRD-07, confirm=true")
        log["pr_button"] = click_any(pg, pg, [r"^run tool", r"^execute", r"^call", r"^run"])
        pg.wait_for_timeout(3500)
        shot("inspector_06_elicitation", "the server asks Kavita to confirm (elicitation) before anything is saved")
        look(pg, log, "elicitation")
    step(log, "create_pr", create_pr)

    def answer():
        dlg = pg.get_by_role("dialog")
        scope = dlg.first if dlg.count() else pg
        for loc in (scope.get_by_label(re.compile("confirm", re.I)), scope.get_by_role("checkbox"),
                    scope.get_by_role("switch")):
            try:
                if loc.count():
                    loc.first.check(timeout=3000)
                    break
            except Exception:  # noqa: BLE001
                continue
        pg.wait_for_timeout(500)
        shot("inspector_06b_elicitation_ticked", "the confirmation form with Confirm ticked")
        log["elicit_button"] = click_any(pg, scope, [r"^submit", r"^accept", r"^send", r"^ok", r"^confirm"])
        pg.wait_for_timeout(3500)
        shot("inspector_07_pr_receipt", "after Kavita confirms: the PR receipt read back from Bahi")
        look(pg, log, "pr_receipt")
    step(log, "answer_elicitation", answer)

    def mrtr():
        entry = pg.locator("div").filter(has_text=re.compile(r"^.*MRTR")).filter(
            has=pg.get_by_role("button", name="Expand")).last
        entry.get_by_role("button", name="Expand").first.click(timeout=5000)
        pg.wait_for_timeout(1500)
        shot("inspector_07b_mrtr_rounds", "Protocol panel: the MRTR entry expanded, tools/call -> input_required -> retry -> complete")
        look(pg, log, "mrtr")
    step(log, "mrtr_expand", mrtr)

    def resources():
        tab(pg, "Resources")
        pg.get_by_role("button", name=re.compile(r"^Purchase policy")).first.click(timeout=5000)
        pg.wait_for_timeout(2500)
        shot("inspector_08_policy", "Resources: rasoi://policy/purchase opened (the purchase policy as a document)")
        look(pg, log, "policy")
    step(log, "resources", resources)

    def template():
        pg.get_by_role("button", name=re.compile(r"^Live stock")).first.click(timeout=5000)
        pg.wait_for_timeout(1200)
        look(pg, log, "template_form")
        fill_field(pg, pg, "item_code", "GSK-SIL-05L")
        log["template_button"] = click_any(pg, pg, [r"^read", r"^get", r"^fetch", r"^open", r"^go"])
        pg.wait_for_timeout(2500)
        shot("inspector_09_stock_template", "Resource template rasoi://stock/{item_code} read for GSK-SIL-05L")
        look(pg, log, "template_result")
    step(log, "template", template)

    def prompts():
        tab(pg, "Prompts")
        pg.get_by_role("button", name=re.compile(r"^Raise a purchase request")).first.click(timeout=5000)
        pg.wait_for_timeout(1200)
        look(pg, log, "prompt_form")
        for k, v in [("item", "5-litre silicone gasket"), ("quantity", "20000"), ("need_by", "2026-11-09")]:
            log.setdefault("prompt_fill", {})[k] = fill_field(pg, pg, k, v)
        log["prompt_button"] = click_any(pg, pg, [r"^get prompt", r"^get", r"^run", r"^render", r"^preview"])
        pg.wait_for_timeout(2500)
        shot("inspector_10_prompt", "Prompts: raise_a_pr filled in; the messages it returns (text + the policy attached)")
        look(pg, log, "prompt_result")
    step(log, "prompts", prompts)
