# %% [markdown]
# # NB4 · The Hands: Tools and MCP
# **From Forms to Agents · Lecture 4 · Sun 8 Nov 2026 · Dr. Rajat Dandekar**
#
# You are the engineer Rasoi Steel Works hired to make it AI-native. After Lecture 3, **Ask Rasoi** can explain
# Rasoi's rules with a citation. It still cannot check stock or raise Kavita's purchase request: a model only
# writes text. Today it gets hands: **the toolbox, served over MCP.**
#
# The running example: Kavita needs 20,000 silicone gaskets (GSK-SIL-05L) for the 5-litre cooker before the
# Diwali run. Her request PR/2026/04417 is estimated at ₹2,69,040, above her ₹2,50,000 limit, so Rohit must approve.
#
# What you will do:
# 1. Meet the toolbox: 15 tools, one folder each (`tool.json` + `tool.py`).
# 2. Do one **function-calling round trip by hand**: send tools to a model, read the tool call it writes, run it, send the result back.
# 3. **Validate arguments** against `tool.json` with JSON Schema.
# 4. Call the toolbox directly through the whole purchase chain: request → approval → order → release → goods receipt.
# 5. **Write a new tool folder** and load it next to the others.
# 6. Watch **idempotency** survive an injected timeout.
# 7. **Serve the toolbox over MCP** and read the JSON-RPC on the wire.
# 8. Let a model use it for **one round**, through MCP, including your new tool.
#
# Everything runs with **no API key** in replay mode: the model replies were recorded in our run (cassette `L4v3_nb`).
# All companies, people, codes and numbers are fictional.

# %% setup

# %%
import json, os, pathlib, tempfile, textwrap
import pandas as pd
pd.set_option("display.max_colwidth", 100)
pd.set_option("display.width", 200)

from bahi.erp.engine import ERP, SERVICES, ServiceTimeout
from bahi.toolbox import Toolbox, SPECS
from bahi.agent.tools import RawServiceTools, content_key
from bahi.llm import LLM
from bahi.course.l4 import (TOOLBOX, HANDS_SYSTEM, add_tool_dir, lint_tool, validate_args, one_round,
                            stdio_wire, handshake)

SOLUTION = True   # set to False to write the exercises yourself; True runs the worked solutions

def show(x, n=1200):
    """Print a dict as indented JSON, cut to n characters."""
    s = json.dumps(x, indent=1, ensure_ascii=False, default=str)
    print(s if len(s) <= n else s[:n] + "\n  ...")

# %% [markdown]
# ## 1. The toolbox
# A **tool** is one thing the assistant can do in Bahi, described so a model can ask for it.
# Rasoi's toolbox has 15, one per business activity. Each lives in its own folder:
# `tool.json` is what the model reads; `tool.py` is what runs.

# %%
erp = ERP()                       # a fresh Rasoi sandbox; the date is Monday 26 Oct 2026
kavita = Toolbox(erp, "KJOSHI")   # the toolbox bound to Kavita's own Bahi session
pd.DataFrame([{"tool": n, "category": SPECS[n].spec["category"], "writes": SPECS[n].writes,
               "Bahi services behind it": ", ".join(SPECS[n].spec["services"])} for n in kavita.names])

# %%
print(json.dumps(SPECS["check_stock"].spec, indent=1)[:900])
print("\n--- tool.py ---\n" + SPECS["check_stock"].source)

# %%
r = kavita.call("check_stock", {"item_code": "GSK-SIL-05L"})
show(r)

# %% [markdown]
# Compare: Bahi itself offers **41 raw services**, with terse names and fields. A model given those has to know
# that stock needs `itm_get`, then `whs_list`, then `stk_query` once per warehouse. The tool knows the order.

# %%
raw = RawServiceTools(erp.session("KJOSHI"))
print(len(raw.schemas()), "raw services:", ", ".join(s["function"]["name"] for s in raw.schemas()))
show(next(s for s in raw.schemas() if s["function"]["name"] == "po_save"))

# %% [markdown]
# ## 2. Function calling by hand
# **Function calling**: we send the model the tool definitions with the conversation; instead of words it may
# reply with a **tool call**, a small JSON request naming a tool and its arguments. **The model never touches Bahi.**
# Our code decides to run the call, in Kavita's session, and sends the result back as a `tool` message.
# Then the model answers in words.
#
# We use the course's LLM shim (`bahi.llm.LLM`), which speaks the OpenAI-compatible chat format to Gemini.

# %%
llm = LLM("gemini:gemini-3.8-flash", cassette="L4v3_nb")
messages = [{"role": "system", "content": HANDS_SYSTEM.format(name="Kavita Joshi", user_id="KJOSHI", first="Kavita")},
            {"role": "user", "content": "Check stock of the 5-litre gasket."}]
tools = kavita.schemas()           # the 15 definitions, in the OpenAI "function" format
print(len(tools), "tools,", len(json.dumps(tools)), "characters of JSON sent with every request")

reply = llm.chat(messages, tools=tools)
print("words:", reply.content)
for tc in reply.tool_calls:
    print("tool call:", tc.id, tc.name, tc.arguments)
print("tokens in/out:", reply.tokens_in, reply.tokens_out)

# %% [markdown]
# The model did not answer. It wrote a request. Look at the assistant message exactly as it goes back into the
# conversation (Gemini also returns a "thought signature" we must echo back; it is opaque to us).

# %%
m = reply.message()
for t in m.get("tool_calls", []):
    t = dict(t); t.pop("extra_content", None)
    show(t)

# %% [markdown]
# **Exercise 1.** Write `run_tool_calls(reply, toolbox)`: for each tool call, run it with `toolbox.call(name, arguments)`
# and return the list of `tool` messages, each `{"role": "tool", "tool_call_id": <the call's id>, "content": <the result as a JSON string>}`.

# %%
def run_tool_calls(reply, toolbox):
    # TODO (exercise 1): one tool message per tool call, in order.
    if not SOLUTION:
        raise NotImplementedError("exercise 1")
    out = []
    for tc in reply.tool_calls:
        result = toolbox.call(tc.name, tc.arguments)
        out.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result, default=str)})
    return out

# %% [markdown]
# Now the round trip: append the model's message and our tool messages, ask again, and repeat until it answers in words.

# %%
for rnd in range(1, 4):
    messages.append(reply.message())
    tool_msgs = run_tool_calls(reply, kavita)
    messages += tool_msgs
    for tm in tool_msgs:
        print(f"round {rnd}: our code ran it; result starts", tm["content"][:140], "...")
    reply = llm.chat(messages, tools=tools)
    if not reply.tool_calls:
        break
    print(f"round {rnd + 1}: the model asks for", [(t.name, t.arguments) for t in reply.tool_calls])
print("\nAnswer:\n" + reply.content)
print("\nmodel calls:", llm.totals())

# %% [markdown]
# It took two tool requests: `find_item` to turn "5-litre gasket" into a code, then `check_stock`. Chaining
# requests like that is a **loop**, and Lecture 5 builds it properly.
#
# Note the answer: 66,000 free and **11 days** of cover, because `check_stock` adds Pune (54,000) and Chakan (12,000).
# Pune alone is 54,000 at 6,000 a day: 9 days. The tool's output decides what the model can say.

# %% [markdown]
# ## 3. JSON Schema: checking arguments once, at the door
# `input_schema` in `tool.json` is **JSON Schema**: a JSON document that says what valid arguments look like
# (types, which are required, allowed values, a description of each). Here is `create_purchase_request`'s.

# %%
show(SPECS["create_purchase_request"].spec["input_schema"])

# %%
good = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"}
cases = {"good": good,
         "quantity as words": {**good, "quantity": "twenty thousand"},
         "no need_by": {k: v for k, v in good.items() if k != "need_by"},
         "confirm as 'yes'": {**good, "confirm": "yes"}}
for label, args in cases.items():
    print(f"{label:20s}", validate_args("create_purchase_request", args) or "valid")

# %% [markdown]
# The toolbox does this check itself, once, before any Bahi service runs (`ToolSpec.check`), and turns a failure into
# an error that says what to do next. Bahi's raw service, given the same mistake, says only `BAD VALUE FOR QTY`.

# %%
show(kavita.call("create_purchase_request", cases["no need_by"]))
show(raw.call("pr_save", {"cc_cd": "PRD-07", "need_dt": "2026-11-09", "itm_cd": "GSK-SIL-05L", "qty": "twenty thousand"}))

# %% [markdown]
# **Exercise 2.** Write `my_check(schema, args)`, a tiny validator: return a list of problems for (a) a missing
# required argument, (b) a value whose type is wrong (`string`, `integer`, `number`, `boolean`), (c) a value not in its `enum`.
# Test it on `approve_purchase_request`, whose `decision` must be `approve` or `reject`.

# %%
PY = {"string": str, "integer": int, "number": (int, float), "boolean": bool}

def my_check(schema, args):
    # TODO (exercise 2): required, types, enums.
    if not SOLUTION:
        raise NotImplementedError("exercise 2")
    probs = [f"missing {r}" for r in schema.get("required", []) if r not in args]
    for k, v in args.items():
        p = schema["properties"].get(k)
        if p is None:
            probs.append(f"unknown argument {k}"); continue
        want = p.get("type")
        if want in PY and (not isinstance(v, PY[want]) or (want != "boolean" and isinstance(v, bool))):
            probs.append(f"{k} should be {want}")
        if "enum" in p and v not in p["enum"]:
            probs.append(f"{k} must be one of {p['enum']}")
    return probs

sch = SPECS["approve_purchase_request"].spec["input_schema"]
for args in [{"request_no": "PR/2026/04417", "decision": "approve"}, {"request_no": "PR/2026/04417", "decision": "yes"},
             {"decision": "approve"}, {"request_no": 4417, "decision": "approve"}]:
    print(args, "->", my_check(sch, args), "| jsonschema:", validate_args("approve_purchase_request", args))

# %% [markdown]
# ## 4. The whole chain, through the toolbox
# Every write tool **previews** first (`confirm=false`, nothing saved), then commits on `confirm=true` and returns a
# **receipt** read back from Bahi. Each person uses their own session: Kavita raises, Rohit approves, Neha receives.

# %%
erp = ERP()
kavita, rohit, neha = Toolbox(erp, "KJOSHI"), Toolbox(erp, "RMEHTA"), Toolbox(erp, "NDESAI")
pr_args = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"}
show(kavita.call("create_purchase_request", pr_args))                       # preview: ₹2,69,040, Rohit must approve

# %%
pr = kavita.call("create_purchase_request", {**pr_args, "confirm": True})
print(pr["request_no"], pr["status"], "| approver:", pr["approver"])
print("Kavita approves her own:", kavita.call("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})["error"])
print("Rohit approves:", rohit.call("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})["status"])

# %%
po_args = {"supplier_code": "DP-RJK-0042", "request_no": pr["request_no"]}
show(kavita.call("create_purchase_order", po_args)["preview"])               # ₹11.90 contract rate, ₹2,80,840 gross
po = kavita.call("create_purchase_order", {**po_args, "confirm": True})
print(po["po_no"], po["status"], "|", po["next_step"])
rel = kavita.call("release_purchase_order", {"po_no": po["po_no"]})
print(rel["po_no"], rel["status"], "| sent to supplier:", rel["sent_to_supplier"])

# %%
for q in (12000, 8000):
    g = neha.call("receive_goods", {"po_no": po["po_no"], "quantity": q, "confirm": True})
    print(g["grn_no"], "received", g["received"], "| balance", g["balance"], "| Pune on hand now", g["stock_after"])
print(kavita.call("order_status", {"po_no": po["po_no"]})["status"])

# %% [markdown]
# ## 5. Write a new tool folder
# A tool is a folder. Here is a new read tool, `purchase_history`, over Bahi's `po_hist` service: the last released
# orders for an item, with supplier and rate. We write the two files, load the folder next to the 15, lint it, and call it.

# %%
MY = pathlib.Path(tempfile.mkdtemp()) / "my_tools"
(MY / "purchase_history").mkdir(parents=True)
(MY / "purchase_history" / "tool.json").write_text(json.dumps({
    "name": "purchase_history", "title": "Purchase history", "category": "Look up", "writes": False, "version": "1.0",
    "description": "The last released purchase orders for an item: order number, supplier, quantity, rate and date, newest first. Use it to answer 'what did we pay last time'.",
    "services": ["po_hist"],
    "input_schema": {"type": "object", "properties": {
        "item_code": {"type": "string", "description": "Bahi item code, e.g. GSK-SIL-05L"},
        "supplier_code": {"type": "string", "description": "optional, only this supplier's orders"}},
        "required": ["item_code"]},
    "example": {"item_code": "GSK-SIL-05L"}}, indent=1))
(MY / "purchase_history" / "tool.py").write_text(textwrap.dedent('''
    """Purchase history: the last released orders for an item."""
    from bahi.agent.tools import _bahi


    def run(s, item_code, supplier_code=None):
        rows = _bahi(s, "po_hist", itm_cd=item_code, **({"sup_cd": supplier_code} if supplier_code else {}))["rows"]
        orders = [{"po_no": r["po_no"], "supplier": f"{r['sup_name']} ({r['sup_cd']})", "quantity": r["qty"],
                   "rate": r["rate"], "date": r["created_on"][:10]} for r in rows]
        return {"ok": True, "item_code": item_code, "orders": orders,
                "last_rate": orders[0]["rate"] if orders else None,
                **({} if orders else {"next_step": "No released orders for this item. Check the code with find_item."})}
'''))
mine = add_tool_dir(MY)
print("loaded:", mine, "| lint:", lint_tool("purchase_history") or "clean")
kavita = Toolbox(erp, "KJOSHI", names=TOOLBOX + mine)
show(kavita.call("purchase_history", {"item_code": "GSK-SIL-05L"}))

# %% [markdown]
# **Exercise 3.** Write a **write** tool, `cancel_purchase_order`, over Bahi's `po_cancel` (fields `po_no`, `reason`).
# Follow the contract:
# - `confirm=false` returns a preview (the order's current receipt, from `bahi.agent.tools._receipt`) and saves nothing;
# - `confirm=true` cancels and returns the receipt read back from Bahi;
# - cancelling an order that is already cancelled returns `ok: true, already_done: true` instead of an error.
#
# The folder template is written for you below; fill in `tool.py`.

# %%
CANCEL_JSON = {
    "name": "cancel_purchase_order", "title": "Cancel purchase order", "category": "Purchasing", "writes": True, "version": "1.0",
    "description": "Cancel a purchase order that is no longer needed. confirm=false shows the order and what cancelling does; confirm=true cancels it and returns the order's real status read back from Bahi.",
    "services": ["po_get", "po_cancel"],
    "input_schema": {"type": "object", "properties": {
        "po_no": {"type": "string", "description": "e.g. PO/2026/01182"},
        "reason": {"type": "string", "description": "why, in a few words; Bahi stores it"},
        "confirm": {"type": "boolean", "description": "false (default) = preview only, nothing is saved; true = commit"}},
        "required": ["po_no", "reason"]},
    "example": {"po_no": "PO/2026/01179", "reason": "no longer needed"}}

# TODO (exercise 3): the body of tool.py for cancel_purchase_order.
CANCEL_PY = "" if not SOLUTION else '''
"""Cancel purchase order."""
from bahi.agent.tools import _bahi, _receipt


def run(s, po_no, reason, confirm=False):
    before = _receipt(s, po_no, tool="order_status")
    if before["status_code"] == "CN":
        return {"ok": True, "already_done": True, **before}
    if not confirm:
        return {"ok": True, "preview": before, "note": "Nothing has been changed. Cancelling releases the budget and, "
                "for a released order, the stock on order. Ask the user to confirm."}
    _bahi(s, "po_cancel", po_no=po_no, reason=reason)
    return {"ok": True, **_receipt(s, po_no, tool="order_status")}
'''
(MY / "cancel_purchase_order").mkdir(exist_ok=True)
(MY / "cancel_purchase_order" / "tool.json").write_text(json.dumps(CANCEL_JSON, indent=1))
(MY / "cancel_purchase_order" / "tool.py").write_text(CANCEL_PY or "def run(s, **args):\n    raise NotImplementedError\n")
mine = add_tool_dir(MY)
print("loaded:", mine, "| lint:", lint_tool("cancel_purchase_order") or "clean")

# %%
# Test it on PO/2026/01179 (4,000 lids, waiting for Rohit): preview, cancel, cancel again.
kavita = Toolbox(erp, "KJOSHI", names=TOOLBOX + mine)
status = lambda: erp.q1("SELECT status FROM po_hdr WHERE po_no='PO/2026/01179'")["status"]
a = kavita.call("cancel_purchase_order", {"po_no": "PO/2026/01179", "reason": "no longer needed"})
print("preview :", a.get("preview", {}).get("status"), "| still", status(), "in Bahi")
b = kavita.call("cancel_purchase_order", {"po_no": "PO/2026/01179", "reason": "no longer needed", "confirm": True})
c = kavita.call("cancel_purchase_order", {"po_no": "PO/2026/01179", "reason": "no longer needed", "confirm": True})
print("cancel  :", b.get("status"))
print("again   :", c.get("already_done"), c.get("status"))
assert erp.q1("SELECT status FROM po_hdr WHERE po_no='PO/2026/01179'")["status"] == "CN"

# %% [markdown]
# ## 6. Idempotency under an injected timeout
# An **idempotency key** is a label derived from what the order *is* (who, supplier, item, quantity, cost centre,
# date). Asking twice with the same key finds the first order instead of making a second.
#
# We make Bahi save the order and then lose the reply (`erp.inject("po_save", "timeout_after_commit")`), the way a
# network timeout does, and retry. First with raw services, then through the toolbox. 3,000 whistles from
# Sahyadri Valves on PRD-07 is a small direct order (₹24,072), so no request is needed.

# %%
def raw_order_with_retry():
    e = ERP(); s = e.session("KJOSHI")
    for attempt in (1, 2):
        f = s.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01")["data"]
        if attempt == 1:
            e.inject("po_save", "timeout_after_commit")
        try:
            r = s.call("po_save", po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.80,
                       tax_cd="GST18-INTRA", cc_cd="PRD-07", need_dt="2026-11-04", fetch_tok=f["fetch_tok"])
            print(f"  attempt {attempt}: {r['msg']}")
        except ServiceTimeout as ex:
            print(f"  attempt {attempt}: {ex}")
    return e.q("SELECT po_no, status, gross_value FROM po_hdr WHERE po_no > 'PO/2026/01181'")

def toolbox_order_with_retry():
    e = ERP(); t = Toolbox(e, "KJOSHI")
    args = {"supplier_code": "SV-PUN-0017", "item_code": "WHS-STD-01", "quantity": 3000, "cost_centre": "PRD-07",
            "need_by": "2026-11-04", "confirm": True}
    e.inject("po_save", "timeout_after_commit")
    for attempt in (1, 2):
        r = t.call("create_purchase_order", args)
        print(f"  attempt {attempt}: {r.get('po_no')} {r.get('status')} already_done={r.get('already_done', False)}")
    return e.q("SELECT po_no, status, gross_value, client_ref FROM po_hdr WHERE po_no > 'PO/2026/01181'")

print("raw services, naive retry:"); print(pd.DataFrame(raw_order_with_retry()))
print("\ntoolbox:"); print(pd.DataFrame(toolbox_order_with_retry()))

# %% [markdown]
# **Exercise 4.** The key comes from `content_key(...)`. Show that the same order always gets the same key, and that
# changing the quantity gives a new one. Why must the key never come from `uuid4()` or the clock?

# %%
# TODO (exercise 4): three keys: the order, the same order again, and the order with quantity 3,001.
if SOLUTION:
    k1 = content_key("PO", "KJOSHI", "SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07", "2026-11-04")
    k2 = content_key("PO", "KJOSHI", "SV-PUN-0017", "WHS-STD-01", 3000, "PRD-07", "2026-11-04")
    k3 = content_key("PO", "KJOSHI", "SV-PUN-0017", "WHS-STD-01", 3001, "PRD-07", "2026-11-04")
    print(k1, k2, k3, "| same:", k1 == k2, "| changed:", k1 != k3)
    # A random or time-based key is different on the retry, so the retry looks like a new order.

# %% [markdown]
# ## 7. The toolbox over MCP
# **MCP** (Model Context Protocol) is one standard plug between apps and tools. The **host** is the app the person
# uses (Ask Rasoi, Claude Desktop). Inside it, one **client** per **server**; the server lists its tools
# (`tools/list`) and runs them (`tools/call`). The messages are **JSON-RPC**: `{"jsonrpc": "2.0", "id", "method", "params"}`.
#
# `build_toolbox_server(erp, user)` turns every tool folder into an MCP tool, bound to one user's Bahi session.

# %%
from bahi.toolbox.mcp import build_toolbox_server
from bahi.mcp_server import MCPClient, MCPClientTools

server = build_toolbox_server(erp, "KJOSHI", names=TOOLBOX + mine)    # your two tools ride along
client = MCPClient(server)
found = client.list_tools()
print(len(found), "tools discovered:", [t.name for t in found])
res = client.call_tool("purchase_history", {"item_code": "GSK-SIL-05L"})
print(client.text(res)[:300])
for w in client.wire:
    print(w["method"], json.dumps(w["params"])[:80])

# %% [markdown]
# Now the real wire. We start the server as a separate process, the way Claude Desktop does
# (`python -m bahi.toolbox.mcp --user KJOSHI`), and write JSON-RPC to its stdin, one message per line.

# %%
wire = stdio_wire(handshake("nb4") + [
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_stock", "arguments": {"item_code": "GSK-SIL-05L"}}}])
for w in wire:
    line = json.dumps(w["msg"])
    print(w["dir"], f"{len(line):5d} bytes", line[:150] + ("..." if len(line) > 150 else ""))

# %% [markdown]
# **Exercise 5.** From the `tools/list` reply on the wire, list the tools a careful host should ask the user about
# before running: the ones whose `annotations.readOnlyHint` is false.

# %%
# TODO (exercise 5): the write tools, from the wire.
if SOLUTION:
    listed = next(w["msg"]["result"]["tools"] for w in wire if w["dir"] == "<-" and "tools" in w["msg"].get("result", {}))
    print(sorted(t["name"] for t in listed if not t.get("annotations", {}).get("readOnlyHint", True)))

# %% [markdown]
# ## 8. One round, through MCP, with your tool
# Ask Rasoi at the **hands** stage: the model sees the tools discovered over MCP (not hard-coded), may call tools
# once, our code runs them, and it answers. Kavita asks something only your new tool can answer.

# %%
mcp_tools = MCPClientTools(client)
msgs = [{"role": "system", "content": HANDS_SYSTEM.format(name="Kavita Joshi", user_id="KJOSHI", first="Kavita")},
        {"role": "user", "content": "What rate did we pay last time for GSK-SIL-05L, and on which order?"}]
r = one_round(llm, mcp_tools, msgs)
for c in r["calls"]:
    print("tool call:", c["tool"], c["args"])
print("\nAsk Rasoi:", r["answer"])
client.close()
print("\nmodel calls in this notebook:", llm.totals())

# %% [markdown]
# ## 9. Your module (A4 starts here)
# Your capstone kit installs on the same sandbox: `ERP(modules=["hr_leave"])`. List its raw services, pick 3–4
# business activities, and write one tool folder for each, the way you wrote `purchase_history`. Then serve them with
# `build_toolbox_server(erp, user, names=add_tool_dir("my_module_tools"))`. The checklist is in `A4.md`.

# %%
MODULE = "hr_leave"   # change to your kit: pur_amend, fin_payables, hr_leave, sales_orders, svc_warranty, inv_transfers, travel_claims, legal_contracts
merp = ERP(modules=[MODULE])
prefix = __import__(f"bahi.modules.{MODULE}", fromlist=["KIT"]).KIT["prefix"]
pd.DataFrame([{"service": n, "what Bahi calls it": s.doc, "kind": s.kind,
               "fields": ", ".join(f.name + ("*" if f.required else "") for f in s.fields)}
              for n, s in SERVICES.items() if n.startswith(prefix)])
