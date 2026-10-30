# %% [markdown]
# # NB1 · The Before and the After
#
# **Agentic Systems Engineering · Lecture 1 · Vizuara · Dr. Rajat Dandekar**
#
# You are the engineer **Northbridge Cycles** has just hired. Northbridge builds electric bikes in Manchester, about
# 18,000 a month, and has run its business on **Ledgerline ERP 7.2** since 1998. On Monday 26 October 2026 Emma Clarke in
# purchasing needs **2,000 battery packs** (`BAT-500`) from Voltway Cells, Eindhoven, for the spring launch run.
# Everything here is fictional: the ERP, the company, the people and the data.
#
# In this notebook you will:
# 1. see why agents matter in a company like this;
# 2. meet the ERP: what SAP, Oracle, Dynamics and Odoo are, then Ledgerline from Python, as a **black box**;
# 3. do the battery pack order **the legacy way**, screen by screen, in code, and measure it;
# 4. let **Ask Northbridge** do the same missions, one sentence each;
# 5. look at **what is behind it**: the tool schemas, one tool call by hand, and MCP, the plug;
# 6. write down a Before from your own work, which is the start of assignment A1.
#
# The model calls run in **replay mode**: they come from our recorded run (cassette `L1v4_after`), so the notebook
# runs with no API key and shows exactly what happened. Six exercises are marked `TODO (exercise N)`. Each one has its
# solution in place behind `SOLUTION = True`, so the notebook runs top to bottom. Set it to `False` and try it yourself.

# %% setup

# %%
import json

import pandas as pd
from IPython.display import Markdown, display

pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 160)


def gbp(x):
    """285600 -> £285,600"""
    return f"£{x:,.0f}" if float(x) == int(float(x)) else f"£{x:,.2f}"


def show_json(d, n=1200):
    print(json.dumps(d, indent=1, default=str, ensure_ascii=False)[:n])


print(gbp(285600), gbp(250000), gbp(119))

# %% [markdown]
# ## 1. Why agents matter
#
# A company like Northbridge runs on a few systems of record. Every order, receipt, invoice, payslip and leave day is
# a row in one of them. Those systems are correct, auditable and old. Their way in is a **screen** that expects codes:
# a supplier code, a tax code, a cost centre, a document number. A person in purchasing spends much of the day turning
# what they want ("2,000 battery packs from Voltway by 9 November") into those codes, in the right order of screens,
# and finding out later what went wrong.
#
# An **agent** sits between the person and the system. It takes the sentence, looks the codes up, shows a preview,
# waits for a yes, does the work through the system's own rules, and comes back with a receipt. It does not replace
# the ERP: it is a new front door to it. This course builds that front door properly: it is safe, measured, and fit for
# production.
#
# To know whether it helps, we first **measure the Before**.

# %% [markdown]
# ## 2. Meet the ERP
#
# **What an ERP is.** An ERP (enterprise resource planning) system is one shared database plus the business rules
# for purchasing, stores, finance, sales, production and HR, so that every department works on the same record.
# The big four you will meet at work are **SAP** (S/4HANA, the large-company default; transactions such as `ME21N`
# to create a purchase order), **Oracle** (E-Business Suite and Oracle Fusion Cloud ERP), **Microsoft Dynamics 365**
# (Finance and Supply Chain, and Business Central for smaller firms) and **Odoo** (open source, modular, popular with
# mid-sized companies). They differ in scale and price, but they share the same shape: master data (items,
# suppliers, people), documents with a status (request → order → receipt → invoice), approval limits, and screens
# or APIs that check codes. **Ledgerline ERP 7.2** is our stand-in. It is small enough to run in a notebook and old
# enough to have every classic trap.
#
# `ERP()` is one whole Northbridge in memory: items, suppliers, people, cost centres and past orders. Its clock is
# set to Monday 26 October 2026. `serve()` puts it behind HTTP, the way Ledgerline's own legacy client reaches it.
#
# A **service** is one operation of the ERP. A flat JSON payload goes in. The legacy **envelope** comes out: `rc`
# is S or E, plus `err_cd`, `msg` and `data`. We never look inside a service.

# %%
import httpx

from ledgerline import ERP
from ledgerline.erp.receipts import install_receipts
from ledgerline.server import serve

erp = ERP()
install_receipts(erp)          # goods receipt (GRN), the last step of procure-to-pay
url = serve(port=8077, erp=erp)

login = httpx.post(url + "/login", json={"user_id": "ECLARKE", "password": "emma@123", "ou_cd": "NBC-MAN-01"}).json()
H = {"Authorization": "Bearer " + login["token"]}
print(login["msg"])


def svc(name, **payload):
    """Call one Ledgerline service over HTTP, as Emma. Returns the envelope."""
    return httpx.post(f"{url}/svc/{name}", json=payload, headers=H).json()


show_json(svc("stk_query", itm_cd="BAT-500", whs_cd="WH-MAN-STR"))

# %%
env = svc("itm_search", q="battery pack 5")
print(env["msg"])
pd.DataFrame(env["data"]["rows"])

# %% [markdown]
# Several battery packs look alike. `-R` is refurbished stock and is never ordered for production. A person has to
# know that. Here is the whole catalogue of services:

# %%
cat = httpx.get(url + "/services").json()
print(len(cat), "services")
pd.DataFrame([{k: s[k] for k in ("name", "kind", "doc")} for s in cat]).head(12)

# %% [markdown]
# ### TODO (exercise 1): which Voltway?
# Call the supplier search service `sup_search` with `q="Voltway"`. How many rows come back, and which one must
# never be used? Put its code in `blocked`. (Look at the other row too: is it the same company?)

# %%
SOLUTION = True
blocked = None
if SOLUTION:
    rows = svc("sup_search", q="Voltway")["data"]["rows"]
    display(pd.DataFrame(rows))
    blocked = next(r["sup_cd"] for r in rows if r["status"] == "BLOCKED")
print("blocked duplicate:", blocked)
assert blocked == "VC-EIN-0009"

# %% [markdown]
# ## 3. The Before, measured
#
# `Desk` is one person at one PC with the legacy client open. It reads the same screen files the client reads
# (`erp/screens/*.yaml`), so pressing a button here makes exactly the service call the client would make. `Tally`
# counts what the person did: screens opened, fields typed, codes typed, buttons, sign-ins and error codes.
#
# Here is the order-entry screen as a file: its fields, and which service each button calls.

# %%
from ledgerline.legacy_ui.driver import Desk, Tally, screen_yaml

print(screen_yaml("PUR-PO-01")[:1500])

# %% [markdown]
# Now the five missions, the way someone does them the first time: keeping what **Fetch** fills in.

# %%
tally = Tally()
http = httpx.Client(base_url=url)


def desk(who, uid, pw):
    return Desk(http, tally, who).sign_in(uid, pw)


marks = {}
def mission(name):
    marks[name] = (dict(tally.c), len(tally.events))


mission("1 stock")
emma = desk("Emma", "ECLARKE", "emma@123")
s = emma.open("INV-ITM-03").type(q="battery pack 5").press("Search").pick(0)
item = s.form["itm_cd"]
s = emma.open("INV-STK-02").type(itm_cd=item).press("Query")
print("stock:", s.form["on_hand"], "on hand,", s.form["avg_daily_issue"], "a day,", s.form["cover_days"], "days of cover (Manchester)")

mission("2 request")
s = emma.open("PUR-PR-01").type(itm_cd=item).press("Fetch")
print("Fetch filled cost centre:", s.form["cc_cd"])
s.type(qty="2000", need_dt="09-11-2026", remarks="spring-launch run").press("Save").press("Submit")
pr_no = s.form["pr_no"]
print(s.status, "| estimate", gbp(float(s.form["est_value"])))

mission("3 approve")
daniel = desk("Daniel", "DOKAFOR", "daniel@123")
s = daniel.open("PUR-PR-04").press("Inbox")
s.pick(next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr_no)).press("Fetch").type(decision="A", comment="ok").press("Confirm")
print(s.status)

mission("4 order")
s = emma.open("PUR-POH-02").type(itm_cd=item).press("Query").pick(0)
sup = s.form["sup_cd"]
s = emma.open("PUR-PO-01").type(pr_no=pr_no, sup_cd=sup, itm_cd=item).press("Fetch")
print("Fetch filled tax code", s.form["tax_cd"], "and cost centre", s.form["cc_cd"])
s.press("Save")
print("Save:", s.status)
s.type(tax_cd="VAT20-RC").press("Save")
po_no = s.form["po_no"]
print("Save again:", s.status, "| status field:", s.form["status"])
s = emma.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
print("Release:", s.status)

# %% [markdown]
# **Saved is not done.** The status bar said SAVED, but the status field says `DR`, a Draft. The order took cost
# centre PRD-05 from the request, and PRD-05 (the city e-bike line) closed on 15 October. Release refuses the order. The
# fix is order amendment: change the cost centre to PRD-07, then release again. Then Aiko receives the goods in two
# deliveries.

# %%
s = emma.open("PUR-POM-06").type(po_no=po_no).press("Fetch").type(cc_cd="PRD-07").press("Amend")
print("Amend:", s.status)
s = emma.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
print("Release:", s.status)

mission("5 receive")
aiko = desk("Aiko", "ATANAKA", "aiko@123")
for q, note in ((1200, "DN-4471"), (800, "DN-4486")):
    s = aiko.open("INV-GRN-03").type(po_no=po_no).press("Fetch").type(qty=str(q), remarks=note).press("Save")
    print(s.status, "| balance", s.form.get("balance"))
mission("end")

# %% [markdown]
# The tally, mission by mission. Minutes cannot be measured without a person, so the last column is an
# **estimate** from the keystroke-level model: 0.28 s a key, 1.1 s a point-and-click, 1.35 s to think before each
# field or button, and 2 s for each screen or service reply. Waiting for Daniel and the phone call to IT are not
# included.

# %%
def klm_seconds(events):
    t = 0.0
    for e in events:
        if e["action"] == "open":
            t += 1.35 + 2 * 1.1 + 2.0
        elif e["action"] == "type":
            t += 1.35 + 1.1 + 0.28 * len(e["detail"].split(" = ", 1)[-1])
        elif e["action"] in ("press", "select"):
            t += 1.35 + 1.1 + (2.0 if e.get("service") else 0)
    return t


names = list(marks)
cols = ["screens opened", "fields typed", "codes typed", "characters typed", "buttons pressed", "sign-ins", "error codes"]
rows = []
for a, b in zip(names, names[1:]):
    (c0, e0), (c1, e1) = marks[a], marks[b]
    rows.append({"mission": a, **{c: c1.get(c, 0) - c0.get(c, 0) for c in cols},
                 "minutes (estimate)": round(klm_seconds(tally.events[e0:e1]) / 60, 1)})
before = pd.DataFrame(rows).set_index("mission")
before.loc["total"] = before.sum()
before.loc["total", "minutes (estimate)"] = round(klm_seconds(tally.events) / 60, 1)
before

# %% [markdown]
# ### TODO (exercise 2): the careful path
# Luis, the senior buyer, knows every trap. He types `PRD-07` on the request and `VAT20-RC` on the order before the
# first Save. Re-run missions 2 to 4 his way on a fresh Northbridge. Put the number of codes typed in mission 4 in
# `careful_codes`. Knowing the traps removes the errors. Does it remove the steps?

# %%
SOLUTION = True
careful_codes = None
if SOLUTION:
    from fastapi.testclient import TestClient
    from ledgerline.server import create_app

    erp2 = ERP(); install_receipts(erp2)
    app2 = create_app(); app2.state.tenants["default"] = erp2
    t2 = Tally(); http2 = TestClient(app2)
    k2 = Desk(http2, t2, "Emma").sign_in("ECLARKE", "emma@123")
    s = k2.open("PUR-PR-01").type(itm_cd="BAT-500").press("Fetch").type(qty="2000", need_dt="09-11-2026", cc_cd="PRD-07").press("Save").press("Submit")
    pr2 = s.form["pr_no"]
    r2 = Desk(http2, t2, "Daniel").sign_in("DOKAFOR", "daniel@123")
    s = r2.open("PUR-PR-04").press("Inbox")
    s.pick(next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr2)).press("Fetch").type(decision="A").press("Confirm")
    c0 = t2.c["codes typed"]
    s = k2.open("PUR-POH-02").type(itm_cd="BAT-500").press("Query").pick(0)
    s = k2.open("PUR-PO-01").type(pr_no=pr2, sup_cd=s.form["sup_cd"], itm_cd="BAT-500").press("Fetch").type(tax_cd="VAT20-RC").press("Save")
    print("careful Save:", s.status, "| status", s.form.get("status"))
    s = k2.open("PUR-POR-05").type(po_no=s.form["po_no"]).press("Fetch").press("Release")
    print("careful Release:", s.status)
    careful_codes = t2.c["codes typed"] - c0
print("codes typed in mission 4, careful path:", careful_codes, "| first time:", before.loc["4 order", "codes typed"])

# %% [markdown]
# ## 4. The After: Ask Northbridge
#
# A new, fresh Northbridge, and the same missions, one sentence each. Each person gets their own **Ask Northbridge**,
# signed in as themselves, with their own limits. When Ask Northbridge asks a question ("Shall I go ahead?"), the
# person answers by fixed rules (`ledgerline.course.l1.answer`), so the run replays exactly. "Done" is read from
# Ledgerline's own tables, never from the reply.
#
# For now, treat Ask Northbridge as a black box, like Ledgerline: a sentence goes in, a reply comes out.

# %%
from ledgerline.course.l1 import MISSIONS, play_mission

erp3 = ERP()
agents = {}
log = []
for m in MISSIONS:   # the same as play_missions(erp3, agents=agents), keeping each mission's model time
    a = agents.get(m["user"])
    n0 = len(a.llm.log) if a else 0
    r = play_mission(erp3, agents, m)
    r["model_seconds"] = sum(x.seconds for x in agents[m["user"]].llm.log[n0:])   # recorded seconds, kept on replay
    log.append(r)

for m in log:
    display(Markdown(f"### {m['title']} ({m['who']}) · done: **{m['done']}**"))
    for t in m["turns"]:
        display(Markdown(f"> **{m['who']}:** {t['user']}\n\n**Ask Northbridge:** " + (t["reply"] or "").replace("\n", "  \n")))

# %% [markdown]
# Ledgerline, read back after the missions. The documents are the same as in the Before, and nothing is silent: the
# order is closed, and the right tax code and cost centre are on it.

# %%
display(pd.DataFrame(erp3.q("SELECT pr_no, status, cc_cd, est_value, approved_by FROM pr_hdr WHERE raised_on >= '2026-10-26'")))
display(pd.DataFrame(erp3.q("SELECT po_no, status, cc_cd, tax_cd, gross_value, approved_by FROM po_hdr WHERE created_on >= '2026-10-26'")))
display(pd.DataFrame(erp3.q("SELECT h.grn_no, h.po_no, l.qty, h.received_by, h.remarks FROM grn_hdr h JOIN grn_line l ON l.grn_no = h.grn_no")))
print("Brightcell Energy registered?", erp3.q("SELECT sup_cd FROM supplier WHERE name LIKE '%Brightcell%'") or "no")

# %% [markdown]
# ### The Before and the After, side by side
# In the Experience app, a "Yes, go ahead." is one **tap** on the Yes button, not typing. The model's time is what
# the recorded run measured (a replay keeps the recorded seconds).

# %%
YES = "Yes, go ahead."
A = [m for m in log if m["id"] != "brightcell"]
msgs = [t["user"] for m in A for t in m["turns"]]
typed = [x for x in msgs if x != YES]
model_seconds = sum(m["model_seconds"] for m in A)
after = {"screens opened": 0, "fields typed": 0, "codes typed": sum(x.count("PO/") for x in typed),
         "characters typed": sum(len(x) for x in typed), "buttons pressed": 0, "sign-ins": 0, "error codes": 0}
score = pd.DataFrame({"Before (first time)": before.loc["total", cols], "After (Ask Northbridge)": pd.Series(after)}).astype(object)
score.loc["messages"] = [None, len(msgs)]
score.loc["  of which taps (a yes)"] = [None, len(msgs) - len(typed)]
score.loc["tool calls (Ask Northbridge's work)"] = [None, sum(len(m["cards"]) for m in A)]
score.loc["minutes"] = [before.loc["total", "minutes (estimate)"], round(model_seconds / 60, 1)]
print("Before minutes: hands-on estimate. After minutes: the model's time, measured in the recorded run.")
score

# %% [markdown]
# ### TODO (exercise 3): where did the effort go?
# Work out what share of the After's messages were only a yes to a preview, and put it in `yes_share`. Then find
# the one mission where Ask Northbridge needed **two** yeses, and say in a sentence why it asked twice.

# %%
SOLUTION = True
yes_share = two_yes = None
if SOLUTION:
    yes_share = (len(msgs) - len(typed)) / len(msgs)
    two_yes = [m["title"] for m in A if sum(t["user"] == YES for t in m["turns"]) == 2]
print(f"{yes_share:.0%} of the messages were a yes to a preview; two yeses in: {two_yes}")
# (One yes to create the order, one to release it: an order is placed only when it is RELEASED.)

# %% [markdown]
# ## 5. What is behind it
#
# Now open the black box one level. Ask Northbridge is three things:
# - a **toolbox**: one tool per business activity, each a folder with `tool.json` (what the LLM reads) and
#   `tool.py` (what runs);
# - **MCP** (Model Context Protocol), the plug: Ask Northbridge asks the toolbox server what tools it has, then calls them
#   through it;
# - an **orchestrator LLM** that reads the request, picks the next tool, reads the result, and decides again.
#
# ### The tool schemas

# %%
from ledgerline.toolbox import SPECS, Toolbox

pd.DataFrame([{"tool": n, "writes": sp.writes, "inputs": ", ".join(sp.spec["input_schema"].get("properties", {})),
               "required": ", ".join(sp.spec["input_schema"].get("required", [])),
               "description": sp.spec["description"][:70]} for n, sp in SPECS.items()])

# %%
po_tool = SPECS["create_purchase_order"]
print(json.dumps({k: po_tool.spec[k] for k in ("name", "description", "input_schema")}, indent=1)[:1800])

# %%
print(po_tool.source)

# %% [markdown]
# ### TODO (exercise 4): find the traps in the code
# Two lines of `tool.py` remove two traps you hit by hand: the wrong tax code (ERR-PO-0412) and the silent Draft on
# a closed cost centre. Put those two lines (as text, stripped) in `tax_line` and `draft_line`.

# %%
SOLUTION = True
tax_line = draft_line = None
if SOLUTION:
    lines = [l.strip() for l in po_tool.source.splitlines()]
    tax_line = next(l for l in lines if l.startswith("tax_cd = _tax_code"))
    draft_line = next(l for l in lines if l.startswith('if budget["cc_state"] == "CLOSED"'))
print(tax_line)
print(draft_line)

# %% [markdown]
# ### One tool call, by hand
# You do not need an LLM to use a tool. `Toolbox(erp, user)` binds the tools to one person's Ledgerline session. As
# Emma, on a fresh Northbridge: check the budget of the closed cost centre `PRD-05`, then **preview** (`confirm` is
# false by default) a direct order with no request, for 2,000 battery packs.

# %%
tb = Toolbox(ERP(), "ECLARKE")
budget = tb.call("check_budget", {"cost_centre": "PRD-05"})
direct = tb.call("create_purchase_order", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500",
                                           "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09"})
show_json(budget, 500)
show_json(direct, 700)

# %% [markdown]
# Compare this with the Before. There, Ledgerline said `ERR-PO-0610: DIRECT PO LIMIT 50000 EXCEEDED, RAISE PR`. The tool
# says what went wrong in words and gives a `next_step`.
#
# ### MCP, the plug
# MCP is an open protocol, JSON-RPC underneath. A host connects to a server, asks `tools/list`, and then sends
# `tools/call` with a tool name and arguments. Our toolbox is an MCP server. Here we connect to it in memory, as Emma,
# exactly as Ask Northbridge does.

# %%
from ledgerline.mcp_server import MCPClient
from ledgerline.toolbox.mcp import build_toolbox_server

client = MCPClient(build_toolbox_server(ERP(), "ECLARKE"))
listed = client.list_tools()
print(len(listed), "tools over MCP:", [t.name for t in listed])
res = client.call_tool("check_stock", {"item_code": "BAT-500"})
call = client.wire[-1]
print("\nthe request, as a JSON-RPC message:")
show_json({"jsonrpc": "2.0", "id": 2, "method": call["method"], "params": call["params"]})
print("\nthe reply's text content:")
show_json(json.loads(client.text(res)), 600)

# %% [markdown]
# ### TODO (exercise 5): which tools can change Ledgerline?
# Each tool in the `tools/list` reply carries **annotations**. `readOnlyHint` is true for tools that only read.
# From `listed`, put the names of the tools that can change Ledgerline in `writers`. A host can use this list to
# ask for a yes before any of them runs. Check that it matches `writes` in each `tool.json`.

# %%
SOLUTION = True
writers = None
if SOLUTION:
    def read_only(t):  # the field is readOnlyHint on the wire; newer MCP SDKs call it read_only_hint in Python
        d = t.annotations.model_dump() if t.annotations else {}
        return d.get("read_only_hint", d.get("readOnlyHint"))
    writers = sorted(t.name for t in listed if read_only(t) is False)
print(len(writers), "tools can write:", writers)
assert writers == sorted(n for n, sp in SPECS.items() if sp.writes)
client.close()

# %% [markdown]
# And here is what went over the plug when Emma's Ask Northbridge connected in section 4: `tools/list`, then its first
# `tools/call`.

# %%
emma_an = agents["ECLARKE"]
w = emma_an.client.wire
print("first message on the wire:", w[0]["method"], "->", len(w[0]["result"]["tools"]), "tools")
show_json({"method": w[1]["method"], "params": w[1]["params"]}, 400)
pd.DataFrame([{"mission": m["title"], "who": m["who"], "tool": c["tool"], "arguments": json.dumps(c["args"])[:90],
               "ok": c["result"].get("ok") if isinstance(c["result"], dict) else None}
              for m in log for c in m["cards"]])

# %% [markdown]
# ## 6. Your Before (the start of assignment A1)
#
# Every company has a Before like Emma's. It might be in a hospital, a bank, a law firm, a university, a logistics
# company or a shop. In A1 you write one from **your own work or domain**. Here is a small structure for it. Each
# step names who does it, in which system, and what they must know or type.

# %% [markdown]
# ### TODO (exercise 6): write your own Before
# Replace the example with a process you know. Keep each step short. Mark `code=True` when the person has to type or
# remember a code, number or exact name, and `handoff=True` when the work passes to another person. The cell counts
# the steps, systems, codes and hand-offs, and the places where the outcome is **silent** (the person cannot see
# whether it worked).

# %%
SOLUTION = True
my_before = []
if SOLUTION:   # an example from outside manufacturing: a researcher claiming conference travel at a university
    my_before = [
        {"who": "researcher", "system": "travel portal", "step": "find the trip's pre-approval number", "code": True},
        {"who": "researcher", "system": "expenses system", "step": "create a claim, pick the grant code", "code": True},
        {"who": "researcher", "system": "expenses system", "step": "type each receipt and its expense type", "code": True},
        {"who": "researcher", "system": "email", "step": "send scanned receipts to the department office", "handoff": True},
        {"who": "dept. administrator", "system": "expenses system", "step": "check receipts against the grant rules"},
        {"who": "grant holder", "system": "expenses system", "step": "approve the claim", "handoff": True},
        {"who": "finance", "system": "finance ERP", "step": "pay; the claim shows only 'processed'", "silent": True, "handoff": True},
    ]
B = pd.DataFrame(my_before).fillna(False)
print(f"{len(B)} steps · {B['system'].nunique()} systems · {B['who'].nunique()} people · "
      f"{int(B.get('code', pd.Series(dtype=bool)).sum())} codes · {int(B.get('handoff', pd.Series(dtype=bool)).sum())} hand-offs · "
      f"{int(B.get('silent', pd.Series(dtype=bool)).sum())} silent outcomes")
B

# %% [markdown]
# Now write the **one sentence** you wish you could say instead, and what the assistant must **never** do without
# asking. A1 asks you for these, and they become your capstone.

# %%
my_sentence = "Claim my Lisbon conference trip on the Horizon grant; the receipts are in this folder."   # yours here
never_without_asking = ["submit a claim to a grant it does not belong to", "pay anything"]          # yours here
print("After, in one sentence:", my_sentence)
print("Never without asking:", "; ".join(never_without_asking))

# %% [markdown]
# ## What you did
# - **The ERP:** SAP, Oracle, Dynamics and Odoo share one shape: master data, documents with a status, approval
#   limits, and code-checking screens. Ledgerline's services are black boxes: an input goes in, an envelope comes out.
# - **The Before, measured:** screens, fields, codes, sign-ins, and the traps (ERR-PO-0412, the silent Draft,
#   ERR-PO-0715), with an honest estimate of the minutes.
# - **The After:** one sentence per mission, a preview and a yes before every save, and receipts read back from
#   Ledgerline.
# - **What is behind it:** one tool per activity (`tool.json` + `tool.py`), found and called over MCP, and chosen by an
#   orchestrator LLM.
#
# **Next time (Lecture 2, The Brain):** we take the tools away and look inside the LLM itself.
