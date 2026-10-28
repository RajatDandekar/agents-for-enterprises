# %% [markdown]
# # NB9 · Protocols and Integration
# **AI Agents for Enterprises · Lecture 9 · Vizuara · Dr. Rajat Dandekar**
#
# Rasoi Steel Works' toolbox now has visitors: IT's laptops, Operations' n8n, a supplier's own agent, and a "free"
# third-party server someone installed. In this notebook you:
#
# 1. serve the toolbox with the **official MCP Python SDK** and use all three primitives: tools, resources, prompts;
# 2. watch the **2026-07-28 protocol** ask Kavita to confirm a write (elicitation, input_required, the retry);
# 3. put the toolbox behind an **OAuth 2.1 sign-in** and see whose session each token gets, and what scopes hide;
# 4. replay the **attack and defence** trials (tool poisoning, an injected quote) and write your own gate;
# 5. replay **Ask Rasoi talking to Deccan Polymers' agent over A2A**;
# 6. read what **n8n** actually ran.
#
# Everything runs with **no API key**: model calls replay from recorded cassettes (`IND9_*`), and every server runs
# inside this notebook on localhost. Five exercises are marked `# TODO (exercise N)`; each has a working solution
# behind `SOLUTION = True`.

# %% setup

# %% [markdown]
# **Pinned versions.** This lecture was built and recorded with these exact versions (28 Oct 2026). Protocols and SDKs
# move fast (MCP 2.x renamed `FastMCP` to `MCPServer`; A2A 1.0 renamed its methods), so we pin them.

# %%
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "mcp==2.3.0", "a2a-sdk[http-server]==1.2.3"], check=True)
import importlib.metadata as md
from bahi.course.protocols import PINS
print({p: md.version(p) for p in ("mcp", "mcp-types", "a2a-sdk")})
print("built with:", PINS)
SOLUTION = True   # set to False to try the exercises yourself
import logging
def quiet():   # the SDKs log every HTTP request at INFO; keep the notebook readable
    for n in ("mcp", "httpx", "httpx2", "a2a", "uvicorn", "FastMCP"):
        logging.getLogger(n).setLevel(logging.WARNING)
quiet()

# %% [markdown]
# ## 1 · The toolbox, with the official SDK
# Lecture 4 used FastMCP. Here the server is the SDK's low-level `Server`: one handler per MCP method
# (`tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`).
# The SDK's `Client` can connect to a server object directly, in memory, which is perfect for a notebook.

# %%
import json
from mcp import Client
import mcp_types as t
from bahi.erp.engine import ERP
from bahi.course.protocols.rasoi_mcp import build_rasoi_server

server = build_rasoi_server(ERP(), user="KJOSHI")
async with Client(server) as c:
    print("protocol:", c.protocol_version, "· server:", c.server_info.name)
    tools = (await c.list_tools()).tools
    print(len(tools), "tools;", sum(1 for x in tools if x.annotations.read_only_hint), "read-only")
    for r in (await c.list_resources()).resources:
        print("resource ", r.uri, "·", r.title, "·", r.size, "bytes")
    for r in (await c.list_resource_templates()).resource_templates:
        print("template ", r.uri_template)
    for p in (await c.list_prompts()).prompts:
        print("prompt   ", p.name, [a.name for a in p.arguments])

# %% [markdown]
# **Resources** are read like files. The purchase policy is a document; live stock is a template you fill in.

# %%
async with Client(server) as c:
    pol = (await c.read_resource("rasoi://policy/purchase")).contents[0].text
    print(pol[pol.find("## 6"):pol.find("## 7")])
    stock = json.loads((await c.read_resource("rasoi://stock/GSK-SIL-05L")).contents[0].text)
    print({w["warehouse"]: w["on_hand"] for w in stock["warehouses"]}, "· cover", stock["cover_days"], "days")

# %% [markdown]
# **Prompts** are reviewed instructions the *person* picks. `raise_a_pr` returns two messages: Suresh's five steps,
# and the purchase policy embedded as a resource.

# %%
async with Client(server) as c:
    g = await c.get_prompt("raise_a_pr", {"item": "5-litre silicone gasket", "quantity": "20000", "need_by": "2026-11-09"})
for m in g.messages:
    print(m.role, "·", m.content.text if m.content.type == "text" else f"[embedded resource {m.content.resource.uri}]")

# %% [markdown]
# ### Exercise 1 · A server of your own, decorator style
# The SDK's other style is `MCPServer` with decorators: type hints become the schema, the docstring the description.
# Write a server `rasoi-calendar` with one **resource** `rasoi://calendar/diwali-run` (text: the Diwali production run
# starts 9 Nov 2026 and needs 20,000 gaskets) and one **prompt** `plan_the_run(item)`. Then list both with a Client.

# %%
from mcp.server import MCPServer

# TODO (exercise 1): create `cal`, an MCPServer with the resource and the prompt described above.
cal = None
if SOLUTION:
    cal = MCPServer("rasoi-calendar")

    @cal.resource("rasoi://calendar/diwali-run")
    def diwali_run() -> str:
        """Rasoi's Diwali production run."""
        return "The Diwali production run starts on 9 Nov 2026 and needs 20,000 GSK-SIL-05L gaskets in Pune."

    @cal.prompt()
    def plan_the_run(item: str) -> str:
        """Plan purchases for the Diwali run."""
        return f"Read rasoi://calendar/diwali-run, then check stock of {item} in both plants and say what to order."

quiet()
if cal is not None:
    async with Client(cal) as c:
        print([str(r.uri) for r in (await c.list_resources()).resources], [p.name for p in (await c.list_prompts()).prompts])
        print((await c.read_resource("rasoi://calendar/diwali-run")).contents[0].text)

# %% [markdown]
# ## 2 · The 2026 protocol asks Kavita to confirm
# In MCP 2026-07-28 there is no `initialize` handshake and no session: every request carries its version and the
# client's capabilities in `_meta`. When a write must be confirmed, the server answers **input_required** with a
# question and a signed `requestState`; the client asks the person and **retries** the same call with the answer.
# The SDK client does the retry for you; you only supply the person, as an `elicitation_callback`.

# %%
asked = []

async def kavita_says_yes(context, params):
    asked.append(params.message)
    return t.ElicitResult(action="accept", content={"confirm": True})

erp = ERP()
srv = build_rasoi_server(erp, "KJOSHI")
PR = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}
async with Client(srv, elicitation_callback=kavita_says_yes) as c:
    r = await c.call_tool("create_purchase_request", PR)
print("Kavita was asked:", asked[0])
print("receipt:", {k: r.structured_content[k] for k in ("request_no", "status", "estimated_value", "approver")})

# %% [markdown]
# **The same calls on the wire.** We serve the toolbox over streamable HTTP on localhost and record every POST, once in
# the stateless era and once in the legacy handshake era (`mode="legacy"`), the way the lecture's plate shows.

# %%
from bahi.course.protocols.wire import Recorder, serve

async def recorded(mode=None):
    rec = Recorder()
    s = build_rasoi_server(ERP(), "KJOSHI")
    url = serve(rec.wrap(s.streamable_http_app())) + "/mcp"
    kw = {"elicitation_callback": kavita_says_yes, **({"mode": mode} if mode else {})}
    async with Client(url, **kw) as c:
        await c.list_tools()
        await c.call_tool("create_purchase_request", PR)
        v = c.protocol_version
    return v, rec

for mode in (None, "legacy"):
    v, rec = await recorded(mode)
    sessions = {e["resp_headers"].get("mcp-session-id") or e["req_headers"].get("mcp-session-id") for e in rec.log} - {None}
    print(f"{v}: {len(rec.log)} HTTP requests, session ids: {[s_[:8] for s_ in sessions] or 'none'}")
    print("   ", [f"{e['method']} {(e['req'] or {}).get('method', '(answer to elicitation)') if isinstance(e['req'], dict) else ''}".strip() for e in rec.log])

# %% [markdown]
# ### Exercise 2 · Answer like Kavita would
# A real person reads the question. Write `kavita_checks(context, params)`: **decline** if the question mentions the
# closed cost centre PRD-05, otherwise accept. Then raise the same request on PRD-05 and on PRD-07 and print what
# Bahi holds afterwards. (PRD-05 closed on 15 Oct; Lecture 1's silent Draft trap.)

# %%
# TODO (exercise 2): write kavita_checks.
async def kavita_checks(context, params):
    return t.ElicitResult(action="accept", content={"confirm": True})   # replace this line

if SOLUTION:
    async def kavita_checks(context, params):
        if "PRD-05" in params.message:
            return t.ElicitResult(action="decline")
        return t.ElicitResult(action="accept", content={"confirm": True})

erp2 = ERP()
srv2 = build_rasoi_server(erp2, "KJOSHI")
async with Client(srv2, elicitation_callback=kavita_checks) as c:
    for cc in ("PRD-05", "PRD-07"):
        r = await c.call_tool("create_purchase_request", {**PR, "cost_centre": cc})
        print(cc, "→", r.structured_content.get("status") or r.structured_content.get("error"))
print(erp2.q("SELECT pr_no, cc_cd, status FROM pr_hdr WHERE need_dt='2026-11-09'"))

# %% [markdown]
# ## 3 · A remote toolbox behind a sign-in
# On the network, anyone who can reach the URL can call the server. The MCP spec uses OAuth 2.1: the toolbox only checks
# tokens; a separate sign-in server issues them. `start_protected_toolbox()` starts both on localhost, plus a second
# toolbox wrongly bound to SVC_AGENT (the confused deputy) and a "reports" server (to test token audience).
# The SDK client does the whole OAuth dance itself: 401 → metadata → registration → authorize with PKCE → token.

# %%
from bahi.course.protocols.auth import start_protected_toolbox, sign_in

world = start_protected_toolbox()
async with sign_in(world, "KJOSHI", ["purchase:read", "purchase:write"]) as (c, store):
    print("tools:", len((await c.list_tools()).tools))
    pr = (await c.call_tool("create_purchase_request", PR)).structured_content
    print("Kavita raises:", pr["request_no"], pr["status"])
    own = (await c.call_tool("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})).structured_content
    print("Kavita approves her own:", own.get("error"))
print("\nthe sign-in, as the toolbox and the sign-in server saw it:")
for e in sorted(world.rec_as.log + world.rec_rs.log, key=lambda e: e["at_ms"])[:9]:
    print(f"   {e['method']:5} {e['path'][:48]:48} {e['status']}")

# %% [markdown]
# **The confused deputy.** The same token sent to the toolbox that runs as SVC_AGENT.

# %%
async with sign_in(world, "KJOSHI", ["purchase:read", "purchase:write"], url=world.deputy_url) as (c, _):
    d = (await c.call_tool("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})).structured_content
print("through the deputy:", d.get("status"), "· decided by", d.get("decided_by"))
print("Bahi's audit trail:", world.erp.q("SELECT user_id, svc FROM audit_trail WHERE svc='pr_approve'"))

# %% [markdown]
# ### Exercise 3 · Least scope
# Rohit must approve requests and nothing else should be possible with a read-only token. (a) Sign in as **RMEHTA** with
# only `purchase:read` and count the tools. (b) Sign in again with the scopes he really needs and approve a fresh
# request from Kavita. Fill in `rohit_grant`.

# %%
w2 = start_protected_toolbox()
async with sign_in(w2, "KJOSHI", ["purchase:read", "purchase:write"]) as (c, _):
    req = (await c.call_tool("create_purchase_request", PR)).structured_content["request_no"]
async with sign_in(w2, "RMEHTA", ["purchase:read"]) as (c, _):
    print("read-only token sees", len((await c.list_tools()).tools), "tools")

# TODO (exercise 3): the scopes Rohit needs to approve
rohit_grant = ["purchase:read"]
if SOLUTION:
    rohit_grant = ["purchase:read", "purchase:write"]
async with sign_in(w2, "RMEHTA", rohit_grant) as (c, _):
    a = (await c.call_tool("approve_purchase_request", {"request_no": req, "decision": "approve"})).structured_content
print(req, "→", a.get("status") or a.get("error"))

# %% [markdown]
# ## 4 · Attacks and defences, replayed
# The lecture's 180 trials: a third-party "Bharat Supplier Directory" server with (A) a **poisoned tool description** or
# (B) an **injected quote**, against three host settings: D0 none, D1 words (a rule + spotlighting), D2 structure
# (description pinning + a taint gate on writes). Success is judged by Bahi's own tables. Here is the summary, then two
# runs replayed live from the cassette.

# %%
import pandas as pd
from collections import Counter
from importlib.resources import files
SEC = json.loads(files("bahi.course.protocols").joinpath("fixtures/security_runs.json").read_text())
df = pd.DataFrame(SEC["summary"])
df["model"] = df.model.str.replace("gemini:", "")
print(df.pivot_table(index=["model", "attack", "version"], columns="defence", values="succeeded", aggfunc="sum"))

# %%
import concurrent.futures
from bahi.course.protocols import security

def in_thread(fn, *a, **k):   # run_trial uses asyncio.run; a notebook already has a loop, so use a thread
    with concurrent.futures.ThreadPoolExecutor(1) as ex:
        return ex.submit(fn, *a, **k).result()

for d in ("D0", "D2"):
    r = in_thread(security.run_trial, "A", d, 0, "gemini:gemini-3.5-flash-lite")
    print(f"\n{d}: succeeded={r['succeeded']} quarantined={r['quarantined']}")
    for x in r["calls"]:
        print("   ", x["name"], json.dumps(x["args"])[:90])

# %% [markdown]
# **The gate, measured on the recorded calls.** Every tool call from the 180 trials, run through the lecture's
# `taint_gate` as if third-party text were (or were not) already in the conversation.

# %%
calls = [(c["name"], c["args"] if isinstance(c["args"], dict) else {}) for r in SEC["runs"] for c in r["calls"]]
reads = {"find_item", "check_stock", "find_supplier", "search_policy", "search_suppliers", "get_quote"}
for tainted in (False, True):
    held = [n for n, a in calls if security.taint_gate(n, a, tainted)]
    print(f"tainted={tainted!s:5}: holds {len(held):3} of {len(calls)} calls · {dict(Counter(held))} · read-only held: {sum(n in reads for n in held)}")

# %% [markdown]
# ### Exercise 4 · Pin a description yourself
# Tool poisoning changes a description after you reviewed it (a "rug pull"). Write `my_pin(tools, reviewed)`: keep a
# tool only if the sha256 of its description equals the reviewed hash for its name; return `(kept, quarantined)`.
# Test it on the clean description, the poisoned one, and a one-character change.

# %%
import hashlib
reviewed = {"search_suppliers": hashlib.sha256(security.CLEAN_SEARCH.encode()).hexdigest()}
cases = {"clean": security.CLEAN_SEARCH, "poisoned": security.POISONED_SEARCH,
         "one character changed": security.CLEAN_SEARCH.replace("prices", "price")}

# TODO (exercise 4): write my_pin
def my_pin(tools, reviewed):
    return tools, []

if SOLUTION:
    def my_pin(tools, reviewed):
        kept, quarantined = [], []
        for x in tools:
            ok = reviewed.get(x["name"]) == hashlib.sha256(x["description"].encode()).hexdigest()
            (kept if ok else quarantined).append(x if ok else x["name"])
        return kept, quarantined

for label, desc in cases.items():
    kept, q = my_pin([{"name": "search_suppliers", "description": desc}], reviewed)
    print(f"{label:22} kept={len(kept)} quarantined={q}")

# %% [markdown]
# ## 5 · Two companies' agents, over A2A
# Deccan Polymers has its own sales agent, with its own stock and rules, behind an **agent card** at
# `/.well-known/agent-card.json`. Ask Rasoi talks to it with A2A messages and tasks. `run_negotiation` starts Deccan's
# agent on localhost and replays the recorded three turns: a quote, a push for 5 Nov, and the PO confirmation (streamed).

# %%
from bahi.course.protocols.deccan import run_negotiation, plain_sequence
neg = run_negotiation(ERP())
print("live model calls:", neg["live_calls"])
for i, t_ in enumerate(neg["turns"]):
    print(f"\nTurn {t_['turn']} · Kavita: {t_['kavita']}\n  A2A: {t_['a2a_requests']} · task {t_['task_states']}\n  Ask Rasoi: {t_['ask_rasoi'][:300]}")

# %%
card = neg["agent_card"]
print(card["name"], "·", [s["name"] for s in card["skills"]], "· streaming:", card["capabilities"].get("streaming"))
for f, to, kind, summary in plain_sequence(neg["sequence"]):
    if "Deccan" in f + to:
        print(f"{f:>13} → {to:<13} {kind:22} {summary[:70]}")

# %% [markdown]
# ### Exercise 5 · Read the wire
# From `neg["wire"]` (every HTTP request Deccan's server received), count the requests by JSON-RPC method, and from the
# streamed turn find Deccan's dispatch plan inside the order acknowledgement (the `confirm_order` result in the
# sequence). Check it against the goods receipts Neha will record: 12,000 and 8,000.

# %%
# TODO (exercise 5): count methods and pull out the dispatch plan
methods, plan = Counter(), None
if SOLUTION:
    methods = Counter((e["req"] or {}).get("method", e["method"] + " " + e["path"]) if isinstance(e["req"], dict)
                      else e["method"] + " " + e["path"] for e in neg["wire"])
    ack = next(e for e in neg["sequence"] if e["kind"] == "tool result" and "acknowledged" in json.dumps(e.get("payload")))
    p = ack["payload"] if isinstance(ack["payload"], dict) else json.loads(ack["payload"])
    plan = [(lot["quantity"], lot["dispatch"], lot["arrive"]) for lot in p["dispatch_plan"]]
print(methods)
print(plan)

# %% [markdown]
# ## 6 · What n8n ran
# Operations' self-hosted n8n (2.45.5) ran Lecture 6's Diwali workflow with six **MCP Client** nodes calling the
# toolbox over streamable HTTP. We cannot start n8n inside Colab, so here is the recorded run
# (`lectures/L9-protocols/experiments/n8n_modal.py` reproduces it on Modal; `experiments/n8n/diwali_mcp.json` imports
# into your own n8n).

# %%
N8N = json.loads(files("bahi.course.protocols").joinpath("fixtures/n8n_run.json").read_text())
print(pd.DataFrame([{"node": n["node"], "status": n["status"], "ms": n["executionTime_ms"]} for n in N8N["nodes_run"]]))
print("toolbox requests:", N8N["toolbox_request_count"], "· tools called:", N8N["tools_called"])
print("final:", N8N["final_status"], "·", {k: v.get("status") for k, v in N8N["bahi_final"].items() if isinstance(v, dict) and v.get("status")})
print("one MCP node on the wire:", [r.get("rpc") or r["method"] for r in N8N["toolbox_requests"][:5]])

# %% [markdown]
# ## Your module (A9)
# Open your module, safely: serve its tools with the official SDK plus one resource and one prompt; check it in MCP
# Inspector; publish an A2A agent card for a counterparty in your domain; red-team your own server once and measure the
# fix in your tables. The details and the grading are in `A9.md`. Start from the cells above: `build_rasoi_server` is
# 300 lines you can copy, and `deccan.py` is a complete counterparty agent.
