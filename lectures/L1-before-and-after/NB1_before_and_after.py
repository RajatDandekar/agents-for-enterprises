# %% [markdown]
# # NB1 · The Before and the After
#
# **AI Agents for Enterprises · Lecture 1 · Vizuara · Dr. Rajat Dandekar**
#
# You are the engineer Rasoi Steel Works has hired. Rasoi makes pressure cookers in Pune and has run on
# **Bahi ERP 7.2** since 1998. On Monday 26 October 2026 it needs 20,000 silicone gaskets (`GSK-SIL-05L`) from
# Deccan Polymers before the Diwali run. (Everything here is fictional: the ERP, the plant, the people, the data.)
#
# In this notebook you will:
# 1. meet Bahi from Python, as a **black box**: call a few services and read the envelope they return;
# 2. do the gasket order **the legacy way**, screen by screen, in code, and count every step;
# 3. let **Ask Rasoi** do the same missions, one sentence each, through the toolbox over **MCP**;
# 4. open a tool: its `tool.json` (what the LLM reads) and its `tool.py` (what runs), and call one yourself;
# 5. put the Before and the After side by side;
# 6. start **your module** for assignment A1.
#
# The model calls run in **replay mode**: they come from our recorded run (cassette `L1v3_after`), so the notebook
# runs with no API key and shows exactly what happened. Six exercises are marked `TODO (exercise N)`; each has its
# solution in place behind `SOLUTION = True`, so the notebook runs top to bottom. Set it to `False` to try yourself.

# %% setup

# %%
import json

import pandas as pd
from IPython.display import Markdown, display

pd.set_option("display.max_colwidth", 80)
pd.set_option("display.width", 160)


def inr(x):
    """Indian digit grouping: 280840 -> ₹2,80,840."""
    s = f"{abs(round(x)):d}"
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        s = head + "," + tail
    return "₹" + s


def show_json(d, n=1200):
    print(json.dumps(d, indent=1, default=str, ensure_ascii=False)[:n])


print(inr(280840), inr(250000))

# %% [markdown]
# ## 1. Meet Bahi, as a black box
#
# `ERP()` is one whole Rasoi in memory: items, suppliers, people, cost centres and past orders, with the clock at
# Monday 26 October 2026. `serve()` puts it behind HTTP, the way Bahi's own legacy client reaches it.
#
# A **service** is one operation of the ERP. An input goes in (a flat JSON payload), an output comes out (the
# legacy **envelope**: `rc` is S or E, `err_cd`, `msg`, `data`). We never look inside a service.

# %%
import httpx

from bahi import ERP
from bahi.erp.receipts import install_receipts
from bahi.server import serve

erp = ERP()
install_receipts(erp)          # goods receipt (GRN), the last step of procure-to-pay
url = serve(port=8077, erp=erp)

login = httpx.post(url + "/login", json={"user_id": "KJOSHI", "password": "kavita@123", "ou_cd": "RSW-PUN-01"}).json()
H = {"Authorization": "Bearer " + login["token"]}
print(login["msg"])


def svc(name, **payload):
    """Call one Bahi service over HTTP, as Kavita. Returns the envelope."""
    return httpx.post(f"{url}/svc/{name}", json=payload, headers=H).json()


show_json(svc("stk_query", itm_cd="GSK-SIL-05L", whs_cd="WH-PUN-STR"))

# %%
env = svc("itm_search", q="gasket 5")
print(env["msg"])
pd.DataFrame(env["data"]["rows"])

# %% [markdown]
# Four gaskets look alike. `-R` is rework stock and is never ordered; the rubber one is inactive. A person has to
# know that. Bahi has 38 services like these, plus 3 for goods receipt:

# %%
cat = httpx.get(url + "/services").json()
print(len(cat), "services")
pd.DataFrame([{k: s[k] for k in ("name", "kind", "doc")} for s in cat]).head(12)

# %% [markdown]
# ### TODO (exercise 1): which Deccan?
# Call the supplier search service `sup_search` with `q="Deccan"`. How many rows come back, and which one must
# never be used? Put its code in `blocked`.

# %%
SOLUTION = True
blocked = None
if SOLUTION:
    rows = svc("sup_search", q="Deccan")["data"]["rows"]
    display(pd.DataFrame(rows))
    blocked = next(r["sup_cd"] for r in rows if r["status"] == "BLOCKED")
print("blocked duplicate:", blocked)
assert blocked == "DP-RJK-0009"

# %% [markdown]
# ## 2. The Before, by code
#
# `Desk` is one person at one PC with the legacy client open. It reads the same screen files the client reads
# (`erp/screens/*.yaml`), so pressing a button here makes exactly the service call the client would make. `Tally`
# counts what the person did: screens opened, fields typed, codes typed, buttons, sign-ins, error codes.
#
# Here is the order-entry screen as a file: its fields, and which service each button calls.

# %%
import pathlib

import yaml

import bahi
from bahi.legacy_ui.driver import Desk, Tally, screen_yaml

print(screen_yaml("PUR-PO-01")[:1500])

# %% [markdown]
# Now the five missions, the way someone does them the first time: keeping what **Fetch** fills in.

# %%
tally = Tally()
http = httpx.Client(base_url=url)
AMEND = pathlib.Path(bahi.__file__).parent / "experience" / "screens" / "PUR-POM-06.yaml"


def desk(who, uid, pw):
    d = Desk(http, tally, who)
    if AMEND.exists():  # the order-amendment screen the Experience serves
        d.screens["PUR-POM-06"] = yaml.safe_load(AMEND.read_text())
    return d.sign_in(uid, pw)


marks = {}
def mission(name):
    marks[name] = dict(tally.c)


mission("1 stock")
kavita = desk("Kavita", "KJOSHI", "kavita@123")
s = kavita.open("INV-ITM-03").type(q="gasket 5").press("Search").pick(0)
item = s.form["itm_cd"]
s = kavita.open("INV-STK-02").type(itm_cd=item).press("Query")
print("stock:", s.form["on_hand"], "on hand,", s.form["cover_days"], "days of cover (one warehouse)")

mission("2 request")
s = kavita.open("PUR-PR-01").type(itm_cd=item).press("Fetch")
print("Fetch filled cost centre:", s.form["cc_cd"])
s.type(qty="20000", need_dt="09-11-2026", remarks="Diwali run").press("Save").press("Submit")
pr_no = s.form["pr_no"]
print(s.status)

mission("3 approve")
rohit = desk("Rohit", "RMEHTA", "rohit@123")
s = rohit.open("PUR-PR-04").press("Inbox")
s.pick(next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr_no)).press("Fetch").type(decision="A").press("Confirm")
print(s.status)

mission("4 order")
s = kavita.open("PUR-POH-02").type(itm_cd=item).press("Query").pick(0)
sup = s.form["sup_cd"]
s = kavita.open("PUR-PO-01").type(pr_no=pr_no, sup_cd=sup, itm_cd=item).press("Fetch").press("Save")
print("Save:", s.status)
s.type(tax_cd="GST18-INTER").press("Save")
po_no = s.form["po_no"]
print("Save again:", s.status, "| status field:", s.form["status"])
s = kavita.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
print("Release:", s.status)

# %% [markdown]
# **Saved is not done.** The status bar said SAVED; the status field says `DR`, a Draft. The order took cost
# centre PRD-05 from the request, and PRD-05 closed on 15 October. Release refuses it. The fix is order amendment:
# change the cost centre to PRD-07, then release again. Then Neha receives the goods.

# %%
if AMEND.exists():
    s = kavita.open("PUR-POM-06").type(po_no=po_no).press("Fetch").type(cc_cd="PRD-07").press("Amend")
else:  # older installs without the amendment screen: the same service, called directly
    print(svc("po_amend", po_no=po_no, cc_cd="PRD-07"))
s = kavita.open("PUR-POR-05").type(po_no=po_no).press("Fetch").press("Release")
print("Release:", s.status)

mission("5 receive")
neha = desk("Neha", "NDESAI", "neha@123")
for q in (12000, 8000):
    s = neha.open("INV-GRN-03").type(po_no=po_no).press("Fetch").type(qty=str(q)).press("Save")
    print(s.status, "| balance", s.form.get("balance"))
marks["end"] = dict(tally.c)

# %%
names = list(marks)
cols = ["screens opened", "fields typed", "codes typed", "characters typed", "buttons pressed", "sign-ins", "error codes"]
before = pd.DataFrame([{**{"mission": names[i]}, **{c: marks[names[i + 1]].get(c, 0) - marks[names[i]].get(c, 0) for c in cols}}
                       for i in range(len(names) - 1)]).set_index("mission")
before.loc["total"] = before.sum()
before

# %% [markdown]
# ### TODO (exercise 2): the careful path
# Suresh knows every trap: he types `PRD-07` on the request and `GST18-INTER` on the order before the first Save.
# Count what *that* costs. Re-run missions 2 and 4 his way on a fresh Rasoi and fill `careful_codes` with the number
# of codes typed in mission 4. (Knowing the traps removes errors. Does it remove steps?)

# %%
SOLUTION = True
careful_codes = None
if SOLUTION:
    erp2 = ERP(); install_receipts(erp2)
    from fastapi.testclient import TestClient
    from bahi.server import create_app
    app2 = create_app(); app2.state.tenants["default"] = erp2
    t2 = Tally(); http2 = TestClient(app2)
    k2 = Desk(http2, t2, "Kavita").sign_in("KJOSHI", "kavita@123")
    s = k2.open("PUR-PR-01").type(itm_cd="GSK-SIL-05L").press("Fetch").type(qty="20000", need_dt="09-11-2026", cc_cd="PRD-07").press("Save").press("Submit")
    pr2 = s.form["pr_no"]
    r2 = Desk(http2, t2, "Rohit").sign_in("RMEHTA", "rohit@123")
    s = r2.open("PUR-PR-04").press("Inbox")
    s.pick(next(i for i, r in enumerate(s.rows) if r["doc_no"] == pr2)).press("Fetch").type(decision="A").press("Confirm")
    c0 = t2.c["codes typed"]
    s = k2.open("PUR-POH-02").type(itm_cd="GSK-SIL-05L").press("Query").pick(0)
    s = k2.open("PUR-PO-01").type(pr_no=pr2, sup_cd=s.form["sup_cd"], itm_cd="GSK-SIL-05L").press("Fetch").type(tax_cd="GST18-INTER").press("Save")
    print("careful Save:", s.status, "| status", s.form.get("status"))
    s = k2.open("PUR-POR-05").type(po_no=s.form["po_no"]).press("Fetch").press("Release")
    print("careful Release:", s.status)
    careful_codes = t2.c["codes typed"] - c0
print("codes typed in mission 4, careful path:", careful_codes, "| first time:", before.loc["4 order", "codes typed"])

# %% [markdown]
# ## 3. The After: Ask Rasoi
#
# A new, fresh Rasoi, and the same five missions, one sentence each. Each person gets their own **Ask Rasoi**,
# signed in as themselves. When Ask Rasoi asks a question ("Shall I go ahead?"), the person answers with fixed
# rules (`bahi.course.l1.answer`), so the run replays exactly.
#
# For now, treat Ask Rasoi as a black box, like Bahi: a sentence goes in, a reply comes out.

# %%
from bahi.course.l1 import MISSIONS, play_missions

erp3 = ERP()
agents = {}
log = play_missions(erp3, agents=agents)

for m in log:
    display(Markdown(f"### {m['title']} ({m['who']}) · done: **{m['done']}**"))
    for t in m["turns"]:
        display(Markdown(f"> **{m['who']}:** {t['user']}\n\n**Ask Rasoi:** " + t["reply"].replace("\n", "  \n")))

# %% [markdown]
# Bahi, read back after the missions: the same document numbers as the Before, and nothing silent.

# %%
display(pd.DataFrame(erp3.q("SELECT pr_no, status, cc_cd, est_value, approved_by FROM pr_hdr WHERE raised_on >= '2026-10-26'")))
display(pd.DataFrame(erp3.q("SELECT po_no, status, cc_cd, tax_cd, gross_value, approved_by, warn_cd FROM po_hdr WHERE created_on >= '2026-10-26'")))
display(pd.DataFrame(erp3.q("SELECT h.grn_no, h.po_no, l.qty, h.received_by FROM grn_hdr h JOIN grn_line l ON l.grn_no = h.grn_no")))
print("Shakti Seals registered?", erp3.q("SELECT sup_cd FROM supplier WHERE name LIKE '%Shakti%'") or "no")

# %% [markdown]
# ## 4. How it works
#
# Now open the black box one level. Ask Rasoi is three things:
# - a **toolbox**: one tool per business activity, each a folder with `tool.json` and `tool.py`;
# - **MCP**, the plug: Ask Rasoi asks the toolbox server what tools it has, then calls them through it;
# - an **orchestrator LLM** that reads the request, picks the next tool, reads the result, and decides again.
#
# Here is what went over the plug when Kavita's Ask Rasoi connected: `tools/list`, then the first `tools/call`.

# %%
kav = agents["KJOSHI"]
print("tools discovered over MCP:", len(kav.tools.names))
print(kav.tools.names)
w = kav.client.wire
print("\nfirst message on the wire:", w[0]["method"])
show_json({"method": w[1]["method"], "params": w[1]["params"]}, 400)

# %% [markdown]
# Every tool call Ask Rasoi made, as the "How it works" cards on /after show them:

# %%
cards = pd.DataFrame([{"mission": m["title"], "who": m["who"], "tool": c["tool"],
                       "arguments": json.dumps(c["args"])[:90],
                       "ok": c["result"].get("ok") if isinstance(c["result"], dict) else None}
                      for m in log for c in m["cards"]])
cards

# %% [markdown]
# ### One tool, opened
# `tool.json` is what the LLM reads: a name, a description, and the **JSON schema** of its input and output.
# `tool.py` is what runs: ordinary Python that calls Bahi's services and returns a receipt.

# %%
from bahi.toolbox import SPECS, Toolbox

po_tool = SPECS["create_purchase_order"]
print(json.dumps({k: po_tool.spec[k] for k in ("name", "description", "input_schema")}, indent=1)[:1600])

# %%
print(po_tool.source)

# %% [markdown]
# ### TODO (exercise 3): find the traps in the code
# Two lines of `tool.py` remove two traps you hit by hand: the wrong tax code (ERR-PO-0412) and the silent Draft
# on a closed cost centre. Put those two lines (as text, stripped) in `tax_line` and `draft_line`.

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
# ### TODO (exercise 4): call a tool yourself
# You do not need an LLM to use a tool. `Toolbox(erp, user)` binds the tools to one person's Bahi session.
# As Kavita, on a fresh Rasoi, call `check_budget` for `PRD-05`, then try a **direct** order (no request) for
# 20,000 gaskets with `create_purchase_order`, `confirm=False`. What does each say, and what is the next step?

# %%
SOLUTION = True
budget = direct = None
if SOLUTION:
    tb = Toolbox(ERP(), "KJOSHI")
    budget = tb.call("check_budget", {"cost_centre": "PRD-05"})
    direct = tb.call("create_purchase_order", {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L",
                                               "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"})
show_json(budget, 500)
show_json(direct, 500)

# %% [markdown]
# Compare with the Before: Bahi said `ERR-PO-0610: DIRECT PO LIMIT 50000 EXCEEDED, RAISE PR`. The tool says what
# went wrong in words and gives a `next_step`.
#
# ## 5. The Before and the After, side by side

# %%
A = [m for m in log if m["id"] != "shakti"]
after = {"screens opened": 0, "fields typed": 0,
         "codes typed": sum("PO/" in t["user"] for m in A for t in m["turns"]),
         "characters typed": sum(len(t["user"]) for m in A for t in m["turns"]),
         "buttons pressed": 0, "sign-ins": 0, "error codes": 0}
score = pd.DataFrame({"Before (first time)": before.loc["total"], "After (Ask Rasoi)": pd.Series(after)})
score.loc["messages typed"] = [None, sum(len(m["turns"]) for m in A)]
score.loc["tool calls (Ask Rasoi's work)"] = [None, sum(len(m["cards"]) for m in A)]
score

# %% [markdown]
# ### TODO (exercise 5): where did the effort go?
# The After types *more* characters than the Before. Work out the share of the After's messages that were just
# "Yes, go ahead." and put it in `yes_share`. Then say in one sentence what replaced the codes.

# %%
SOLUTION = True
yes_share = None
if SOLUTION:
    msgs = [t["user"] for m in A for t in m["turns"]]
    yes_share = sum(x.startswith("Yes") for x in msgs) / len(msgs)
print(f"{yes_share:.0%} of the messages were a yes to a preview")

# %% [markdown]
# ## 6. Your module (assignment A1)
#
# Every student takes the same Before and After to one more corner of Rasoi. Eight module kits ship with Bahi;
# each has three legacy screens, its traps, and one sentence its After should handle.

# %%
import importlib

KITS = ["pur_amend", "fin_payables", "hr_leave", "sales_orders", "svc_warranty", "inv_transfers", "travel_claims", "legal_contracts"]
rows = []
for k in KITS:
    kit = importlib.import_module(f"bahi.modules.{k}").KIT
    rows.append({"kit": k, "title": kit["title"], "speaker": kit["speaker"], "screens": ", ".join(kit["screens"]),
                 "the After, in one sentence": kit["after"]})
pd.DataFrame(rows)

# %% [markdown]
# ### TODO (exercise 6): your module's Before
# Pick your kit. Install it (`ERP(modules=[...])`), print its screens' YAML, and run its scripted legacy path
# (`happy_path`) and its traps. These go into A1.

# %%
SOLUTION = True
MY_KIT = "hr_leave"   # change to your kit
if SOLUTION:
    erp_m = ERP(modules=[MY_KIT])
    mod = importlib.import_module(f"bahi.modules.{MY_KIT}")
    from bahi.server import load_screens
    for code in mod.KIT["screens"]:
        sc = load_screens([MY_KIT])[code]
        print(code, "·", sc["title"], "·", len(sc.get("fields", [])), "fields ·", [t["button"] for t in sc.get("tasks", [])])
    legacy = importlib.import_module(f"bahi.modules.{MY_KIT}.legacy")
    print("\nthe careful legacy path:", legacy.happy_path(erp_m), "·", len(erp_m.calls), "service calls")
    print("\nits traps (each on a fresh Rasoi):")
    for name, trap in legacy.TRAPS.items():
        good, what = trap(ERP(modules=[MY_KIT]))
        print(f"  {'yes' if good else 'NO '}  {name}: {what}"[:160])

# %% [markdown]
# ## What you did
# - Bahi's services are black boxes: an input goes in, an envelope comes out.
# - The Before, counted: screens, fields, codes, sign-ins and the traps (ERR-PO-0412, the silent Draft, ERR-PO-0715).
# - The After: one sentence per mission, a preview and a yes before every save, receipts read back from Bahi.
# - How it works: one tool per activity (`tool.json` + `tool.py`), discovered over MCP, chosen by an orchestrator LLM.
#
# **Next time (Lecture 2, The Brain):** we take the tools away and look inside the LLM itself.
