# %% [markdown]
# # NB4 · The Hands: tools, MCP, two harnesses, production grade
#
# **Agentic Systems Engineering · Lecture 4 · Vizuara · Dr. Rajat Dandekar**
#
# Northbridge Cycles builds e-bikes in Manchester and runs on **Ledgerline ERP 7.2** (1998). Its assistant, **Ask
# Northbridge**, has a brain (Lecture 2) and a memory (Lecture 3). Today it gets hands: tools it can ask our code to run.
# Emma Clarke, a purchase executive, asks two things on Monday 26 October 2026:
#
# > **How many BAT-500 battery packs do we have in Manchester main stores?**
# > **I need 2,000 of the 36 V 500 Wh battery packs from Voltway for the spring launch run.**
#
# This notebook follows the lecture, section by section:
#
# 1. open a tool: `check_stock`'s `tool.json`, `tool.py` and the legacy services inside it
# 2. call it, and see every legacy envelope `{rc, err_cd, msg, data}` it turns into one clean result
# 3. the schemas: input and output, checked with a real JSON Schema validator and at the door
# 4. build a tool: `supplier_certificates` from its services, then your own `payment_terms`
# 5. MCP: start the server and talk JSON-RPC to it by hand: `initialize`, `tools/list`, `tools/call`
# 6. two harnesses: Claude Code's recorded run next to ours
# 7. our harness, with the context printed at every model call and real token counts
# 8. production checks: schemas, the error contract, latency and the idempotency fix
#
# **No API key needed.** Every model call is replayed from our recorded runs (cassettes `L4v4_ours*`), so the notebook
# shows exactly what happened. Five exercises are marked `TODO (exercise N)`, each with its solution behind
# `SOLUTION = True`. Set it to `False` and try it yourself.

# %% setup

# %%
import inspect
import json
import pathlib
import statistics
import time

from ledgerline.erp.engine import ERP, SERVICES
from ledgerline.toolbox import ALL, REGISTRY, SPECS, Toolbox
from ledgerline.course.l4 import add_tool_folder, docs_root, handshake, lint_tool, service_definition, service_index, stdio_wire, validate_args
from ledgerline.course.l4.hands import CLAUDE_CODE, context_parts, hands_run, show_context


def pp(o, n=1400):
    """Print JSON, cut at n characters."""
    s = json.dumps(o, indent=1, ensure_ascii=False, default=str)
    print(s if len(s) <= n else s[:n] + " …")


print(len(ALL), "tool folders:", ", ".join(ALL))

# %% [markdown]
# ## 1 · Open a tool
#
# A tool is a function our code runs when the model asks for it. Each one is a folder with two files:
# `tool.json`, what the model reads (its name, description and input schema), and `tool.py`, what runs.

# %%
spec = REGISTRY["check_stock"]
print(spec.folder.relative_to(spec.folder.parents[2]))
print((spec.folder / "tool.json").read_text())

# %%
print(spec.source)

# %% [markdown]
# `tool.py` calls three of Ledgerline's own **services**: the legacy building blocks behind its screens. Where are they
# written down? In Henrik Weber's documentation from Lecture 3, `northbridge-docs`: folder `04_service_definitions/` holds
# one file per service. We clone it (the same repository as NB3), or use a copy you already have.

# %%
DOCS = docs_root(clone_to="northbridge-docs")      # $NORTHBRIDGE_DOCS, ./northbridge-docs, or git clone
SVC = DOCS / "04_service_definitions"
for d in sorted(x for x in SVC.iterdir() if x.is_dir()):
    fs = [f.name for f in d.iterdir()]
    print(f"{d.name + '/':20} {len(fs):3} files  ({sum(f.endswith('.yaml') for f in fs)} yaml, {sum(f.endswith('.xml') for f in fs)} xml)")
print(len(service_index()), "services in service_index.csv")

# %%
print(service_definition("stk_query"))

# %% [markdown]
# The sandbox implements the same services in `ledgerline/erp/services.py`. The definitions and the code agree field
# for field; here is the check for check_stock's three, and the code of `stk_query`.

# %%
import re

for name in spec.spec["services"]:
    sv = SERVICES[name]
    doc = re.findall(r"\{name: (\w+), type: \w+, required: (true|false)", service_definition(name))
    same = [(n, r == "true") for n, r in doc] == [(f.name, f.required) for f in sv.fields]
    print(f"{name:10} {sv.doc:22} kind={sv.kind:5} fields={[f.name for f in sv.fields]}  definition file matches: {same}")
print()
print(inspect.getsource(SERVICES["stk_query"].fn))

# %% [markdown]
# ## 2 · Call it
#
# `Toolbox(erp, "ECLARKE")` binds the toolbox to Emma's own Ledgerline session: her permissions, nobody else's.
# We call `check_stock` the way our code does when the model asks, and print every legacy call it made.

# %%
erp = ERP()
tb = Toolbox(erp, "ECLARKE")
n0 = len(erp.calls)
result = tb.call("check_stock", {"item_code": "BAT-500"})
for r in erp.calls[n0:]:
    print(f"{r.svc:10} {json.dumps(r.payload):46} -> rc={r.rc} err_cd={r.err_cd} data={json.dumps(r.data, default=str)[:110]}")
legacy = sum(len(json.dumps({"rc": r.rc, "err_cd": r.err_cd, "msg": r.msg, "data": r.data}, default=str)) for r in erp.calls[n0:])
print(f"\n{len(erp.calls) - n0} legacy calls, {legacy} bytes of legacy replies -> {len(json.dumps(result))} bytes of result:")
pp(result)

# %% [markdown]
# When something goes wrong, Ledgerline answers with a legacy code. The tool turns it into the **error contract**:
# `ok=false`, `error` in words, `next_step`, and the legacy code kept as `ledgerline_code`. A wrong type never reaches
# Ledgerline at all: it is refused at the door.

# %%
n1 = len(erp.calls)
print("BAT-5000 ->", tb.call("check_stock", {"item_code": "BAT-5000"}))
print("  legacy reply:", [(r.svc, r.rc, r.err_cd, r.msg) for r in erp.calls[n1:]])
n2 = len(erp.calls)
print("500 (an int) ->", tb.call("check_stock", {"item_code": 500}))
print("  Ledgerline calls:", len(erp.calls) - n2)

# %% [markdown]
# **TODO (exercise 1).** Check the stock of the hub motor `MTR-HUB-250`. From the `stk_query` replies alone, work out
# how many days the free stock lasts (free = on hand − allocated, summed over warehouses, divided by the average daily
# issue), and compare it with the tool's `cover_days`.

# %%
SOLUTION = True
if SOLUTION:
    n3 = len(erp.calls)
    motor = tb.call("check_stock", {"item_code": "MTR-HUB-250"})
    rows = [r.data for r in erp.calls[n3:] if r.svc == "stk_query" and r.rc == "S"]
    free = sum(d["on_hand"] - d["allocated"] for d in rows)
    daily = rows[0]["avg_daily_issue"] if rows else None
    print("by hand:", free, "free ÷", daily, "a day =", int(free / daily) if daily else None, "days")
    print("the tool says:", motor.get("cover_days"), "days ·", motor.get("free_total"), "free")

# %% [markdown]
# ## 3 · The schemas
#
# The **input schema** is what the model must send; the **output schema** is what it gets back. Both are JSON Schema.
# `validate_args` checks arguments with a real JSON Schema validator (`jsonschema`); `ToolSpec.check` is the toolbox's
# own check at the door. Look at the last case: JSON Schema allows extra fields unless told otherwise; our door does not.

# %%
print(json.dumps(spec.spec["input_schema"], indent=1))
for args in [{"item_code": "BAT-500"}, {"item_code": 500}, {}, {"item_code": "BAT-500", "warehouse": "WH-MAN-STR"}]:
    print(f"\n{json.dumps(args):50} jsonschema: {validate_args('check_stock', args) or 'valid'}")
    try:
        print(" " * 50, "at the door:", spec.check(args))
    except Exception as e:  # noqa: BLE001
        print(" " * 50, "at the door: refused:", e)

# %%
import jsonschema

jsonschema.validate(result, spec.spec["output_schema"])
print("the real result is valid against check_stock's output schema")
print("fields in the result but not listed in the schema:", sorted(set(result) - set(spec.spec["output_schema"]["properties"])))

# %% [markdown]
# **TODO (exercise 2).** Write an input schema for a new tool `find_open_orders`: `supplier_code` (a string, required)
# and `status` (one of `DRAFT`, `PENDING`, `RELEASED`, optional). Check one good and two bad argument sets with
# `jsonschema`.

# %%
SOLUTION = True
if SOLUTION:
    schema = {"type": "object",
              "properties": {"supplier_code": {"type": "string", "description": "Ledgerline supplier code, e.g. VC-EIN-0042"},
                             "status": {"type": "string", "enum": ["DRAFT", "PENDING", "RELEASED"],
                                        "description": "optional: only orders in this status"}},
              "required": ["supplier_code"]}
    v = jsonschema.Draft202012Validator(schema)
    for a in [{"supplier_code": "VC-EIN-0042", "status": "RELEASED"}, {"status": "OPEN"}, {"supplier_code": 42}]:
        print(json.dumps(a), "->", [e.message for e in v.iter_errors(a)] or "valid")

# %% [markdown]
# ## 4 · Build a tool from scratch
#
# `supplier_certificates` was built for this lecture in six steps: the job (Purchase Policy §6.2: lithium-cell parts
# need a supplier with a valid UN 38.3 certificate), the services (`sup_get`, `sup_cert_get`, `itm_get`), the schema,
# the code, the error contract and the tests. Here are its schema and code, then two real answers.

# %% [markdown]
# **Step 2, find the services.** Search the purchasing module's rows of `service_index.csv` for suppliers, certificates
# and items, then read the definitions we chose.

# %%
pur = [r for r in service_index() if r["module"] == "PUR"]
cands = [r for r in pur if any(w in r["title"] for w in ("SUPPLIER", "ITEM", "CERT"))]
print(len(pur), "purchasing services;", len(cands), "candidates:")
for r in cands:
    print(f"   {r['service']:16} {r['title']:24} {r['kind']:5} {r['file']}")
for name in ("sup_get", "sup_cert_get"):
    print(f"\n--- 04_service_definitions/purchase/{name}.yaml"); print(service_definition(name))

# %%
sc = REGISTRY["supplier_certificates"]
print("services:", sc.spec["services"])
print(json.dumps(sc.spec["input_schema"], indent=1))
print(sc.source[sc.source.index("def run"):])

# %%
tb_all = Toolbox(ERP(), "ECLARKE", names=ALL)
pp(tb_all.call("supplier_certificates", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}))
pp(tb_all.call("supplier_certificates", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500"}))
for bad in [{"supplier_code": "XX-NOPE-0001"}, {}, {"supplier_code": 42}, {"supplier_code": "VC-EIN-0042", "limit": 500}]:
    print(json.dumps(bad), "->", tb_all.call("supplier_certificates", bad))

# %% [markdown]
# **TODO (exercise 3).** Build your own tool, `payment_terms`: "What are Voltway's payment terms?" It needs two
# services: `sup_get` (the supplier, with its `pt_cd`) and `pt_list` (every payment-terms code). Write its `tool.json`
# and `tool.py` into `my_tools/payment_terms/`, load it with `add_tool_folder`, check it with `lint_tool` (the A4 checks)
# and call it. This is the shape of A4, Part 1.

# %%
for n in ("sup_get", "pt_list"):     # the two definitions you need, from Henrik's documentation
    print(service_definition(n))

# %%
SOLUTION = True
if SOLUTION:
    folder = pathlib.Path("my_tools/payment_terms")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "tool.json").write_text(json.dumps({
        "name": "payment_terms", "title": "Payment terms", "category": "Look up",
        "description": "A supplier's payment terms in Ledgerline: the terms code, what it means and the number of days to pay.",
        "writes": False, "version": "1.0", "services": ["sup_get", "pt_list"],
        "input_schema": {"type": "object", "properties": {"supplier_code": {"type": "string", "description": "Ledgerline supplier code, from find_supplier, e.g. VC-EIN-0042"}},
                         "required": ["supplier_code"]},
        "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "supplier_code": {"type": "string"},
                                                           "supplier_name": {"type": "string"}, "terms_code": {"type": "string"},
                                                           "terms": {"type": "string"}, "days": {"type": "integer"}}, "required": ["ok"]},
        "example": {"supplier_code": "VC-EIN-0042"},
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}, indent=2))
    (folder / "tool.py").write_text('''"""Payment terms: a supplier's payment terms, from two legacy reads."""
from ledgerline.agent.tools import ToolError, _ledgerline


def run(s, supplier_code):
    sup = _ledgerline(s, "sup_get", sup_cd=supplier_code.strip().upper())
    terms = {t["pt_cd"]: t for t in _ledgerline(s, "pt_list")["rows"]}
    t = terms.get(sup.get("pt_cd"))
    if not t:
        raise ToolError(f"{sup['sup_cd']} has no payment terms on file.", "Ask purchasing to set them in the supplier master.")
    return {"ok": True, "supplier_code": sup["sup_cd"], "supplier_name": sup["name"], "terms_code": t["pt_cd"],
            "terms": t["descr"], "days": t["days"]}
''')
    name = add_tool_folder("my_tools/payment_terms")     # your tool.json + tool.py, next to the shipped ones
    print("lint:", lint_tool(name) or "[] the A4 checks pass")
    print("jsonschema on a bad call:", validate_args(name, {"supplier_code": 42}))
    tb_mine = Toolbox(ERP(), "ECLARKE", names=[name])
    print(tb_mine.call(name, SPECS[name].spec["example"]))
    print(tb_mine.call(name, {"supplier_code": "XX-NOPE-0001"}))

# %% [markdown]
# ## 5 · MCP: the tool on a server, by hand
#
# The Model Context Protocol (MCP) is the standard way for any app (Claude Code, Claude Desktop, our own harness) to
# find and call tools. Our server is one command: `python -m ledgerline.toolbox.mcp --user ECLARKE --tools check_stock`.
# Over **stdio** it reads one JSON-RPC message per line on stdin and answers on stdout. We start it the way Claude Code
# does, as a child process, and type the messages ourselves.

# %%
wire = stdio_wire(handshake() + [
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_stock", "arguments": {"item_code": "BAT-500"}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "check_stock", "arguments": {"item_code": "BAT-5000"}}},
], server_args=["--tools", "check_stock"])
for w in wire:
    print(w["dir"], json.dumps(w["msg"])[:230])

# %%
by_id = {w["msg"].get("id"): w["msg"] for w in wire if w["dir"] == "<-"}
tool = by_id[2]["result"]["tools"][0]
print("protocol agreed:", by_id[1]["result"]["protocolVersion"], "· server:", by_id[1]["result"]["serverInfo"])
print("definition fields:", sorted(tool))
print("annotations:", tool.get("annotations"))
print("_meta:", {k: v for k, v in tool.get("_meta", {}).items() if k.startswith("ledgerline/") and k != "ledgerline/policy"})
for i in (3, 4):
    res = by_id[i]["result"]
    print(f"\ntools/call id {i}: isError={res.get('isError', False)} · result fields {sorted(res)}")
    print("   structuredContent:", json.dumps(res.get("structuredContent"))[:200])

# %% [markdown]
# **TODO (exercise 4).** Start the server with every tool (`server_args=["--all"]`), count the tools in `tools/list`,
# and call `supplier_certificates` for Nordic Cell Co. (`NC-GDA-0063`) with `BAT-500`. Is it an error (`isError`), or a
# business answer?

# %%
SOLUTION = True
if SOLUTION:
    w2 = stdio_wire(handshake() + [
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "supplier_certificates",
                                                                     "arguments": {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}}}],
        server_args=["--all"])
    m = {w["msg"].get("id"): w["msg"] for w in w2 if w["dir"] == "<-"}
    print(len(m[2]["result"]["tools"]), "tools")
    r3 = m[3]["result"]
    print("isError:", r3.get("isError", False), "· un38_3:", r3["structuredContent"]["un38_3"], "·", r3["structuredContent"].get("next_step"))

# %% [markdown]
# To connect the same server to **Claude Code**, run in a terminal (with `ledgerline-erp[mcp]` installed):
#
# ```
# claude mcp add northbridge -- python -m ledgerline.toolbox.mcp --user ECLARKE --tools check_stock
# ```
#
# and for **Claude Desktop**, add it to `claude_desktop_config.json`:
#
# ```
# {"mcpServers": {"northbridge": {"command": "/full/path/to/python",
#   "args": ["-m", "ledgerline.toolbox.mcp", "--user", "ECLARKE", "--tools", "check_stock"]}}}
# ```
#
# ## 6 · Two harnesses
#
# The **harness** is everything around the model: the system prompt, which tools it gets, the loop that runs its calls,
# the guards, the limits, the logs. Claude Code is Anthropic's harness; Ask Northbridge's loop
# (`ledgerline/experience/harness.py`) is ours. Here is Claude Code's recorded run (claude-sonnet-5.5, headless, on our
# MCP server with two tools) next to ours on the same question.

# %%
cc = CLAUDE_CODE["single"]
for t in cc["turns"]:
    print("EMMA:", t["user"])
    for s in t["steps"]:
        print("  ", s["kind"], s.get("tool") or "", json.dumps(s.get("args")) if s.get("args") else (s.get("text") or "")[:150])
    print("   Claude Code turns:", t["num_turns"], "· tokens:", t["usage"])

# %%
single = hands_run("single")
for t in single["turns"]:
    print("EMMA:", t["user"])
    for c in t["cards"]:
        print("   call", c["tool"], json.dumps(c["args"]), "->", json.dumps(c["result"])[:150])
    print("   REPLY:", t["reply"])
    print("   our harness: model calls", t["model_calls"], "· tokens in", t["tokens_in"], "· out", t["tokens_out"])

# %% [markdown]
# ## 7 · What the model sees
#
# Our harness kept a copy of the messages at every model call, and the provider's own token count. `show_context`
# prints the context part by part. The parts add up exactly to each call's `prompt_tokens`. Nothing else ever reaches
# the model: not `tool.py`, not the services or their envelopes, not the database, not Emma's session.

# %%
show_context(single)

# %% [markdown]
# Now Emma's whole order, on Lecture 4's "hands" prompt (the rules, no Northbridge codes): 16 tools, three turns from
# Emma. Watch the context grow, and notice that the 16 tool definitions are re-sent with every call.

# %%
order = hands_run("order_hands")
parts = context_parts(order)
show_context(order, parts, width=80)

# %%
seq_ours = [c["tool"] for t in order["turns"] for c in t["cards"]]
seq_cc = [s["tool"] for t in CLAUDE_CODE["order_hands"]["turns"] for s in t["steps"] if s["kind"] == "call"]
print(f"our harness ({len(seq_ours)} calls):", " -> ".join(seq_ours))
print(f"Claude Code ({len(seq_cc)} calls):", " -> ".join(seq_cc))
print("final reply (ours):", order["turns"][-1]["reply"])
tools_tok = next(p["tokens"] for p in parts if p["part"].startswith("tool definitions"))
calls = [s for s in order["steps"] if s["tools"] is not None]
print(f"{len(calls)} model calls read {sum(s['prompt_tokens'] for s in calls):,} tokens; the tool definitions alone: "
      f"{len(calls)} x {tools_tok:,} = {len(calls) * tools_tok:,}")

# %% [markdown]
# ## 8 · Production checks
#
# A demo works once. Production is measured. Four of the lecture's ten criteria, on the whole toolbox, in this sandbox.
#
# **Schema.** Every tool's own example, called on a fresh Ledgerline; every ok result checked against its output schema.

# %%
tb_p = Toolbox(ERP(), "ECLARKE", names=ALL)
viol = {}
for n in ALL:
    out = tb_p.call(n, REGISTRY[n].spec.get("example") or {})
    if out.get("ok"):
        errs = [e.message for e in jsonschema.Draft202012Validator(REGISTRY[n].spec["output_schema"]).iter_errors(out)]
        viol[n] = errs
    print(f"{n:26} ok={out.get('ok')!s:5} {'schema violations: ' + str(viol[n]) if viol.get(n) else ''}{'' if out.get('ok') else out.get('error', '')[:70]}")
print(f"\n{sum(1 for v in viol.values() if not v)} of {len(viol)} ok results valid against their output schemas")

# %% [markdown]
# **Reliability.** Bad arguments of every kind, on every tool. Every answer must be inside the error contract
# (`ok`, and when false: `error` and `next_step`), and none may be a non-business failure (`INTERNAL`, or a bad value
# that reached Ledgerline: `ERR-SYS-0422`).

# %%
BAD = [None, "", " ", -1, 0, 10**9, "x" * 200, [], {}]
calls = bad_contract = non_business = 0
for n in ALL:
    props = REGISTRY[n].spec["input_schema"].get("properties", {})
    for k in props:
        for v in BAD:
            args = {**(REGISTRY[n].spec.get("example") or {}), k: v, "confirm": False} if "confirm" in props else {**(REGISTRY[n].spec.get("example") or {}), k: v}
            out = tb_p.call(n, args)
            calls += 1
            if not isinstance(out, dict) or "ok" not in out or (out["ok"] is False and not (out.get("error") and out.get("next_step"))):
                bad_contract += 1
            if out.get("ledgerline_code") in ("INTERNAL", "ERR-SYS-0422"):
                non_business += 1
print(f"{calls} fuzzed calls · outside the error contract: {bad_contract} · non-business failures: {non_business}")

# %% [markdown]
# **Latency.** The tool's own time, in this sandbox (Ledgerline here is an in-memory database, so this is mostly our
# code). The lecture's threshold for the overhead is p50 ≤ 50 ms, p95 ≤ 100 ms, p99 ≤ 200 ms.

# %%
ms = []
for _ in range(300):
    t0 = time.perf_counter()
    tb_p.call("check_stock", {"item_code": "BAT-500"})
    ms.append((time.perf_counter() - t0) * 1000)
q = statistics.quantiles(ms, n=100)
print(f"check_stock, 300 calls: p50 {q[49]:.2f} ms · p95 {q[94]:.2f} ms · p99 {q[98]:.2f} ms")

# %% [markdown]
# **Idempotency: the fix from the lecture.** A write is retried with the date written differently: "9 Nov 2026", then
# "2026-11-09". Before the fix, the idempotency key was built from the arguments as written, so the two calls made two
# purchase requests. Now the door rewrites `need_by` as YYYY-MM-DD before anything uses it.
#
# **TODO (exercise 5).** Before you run the next cell, predict: how many purchase requests will Ledgerline hold, and
# what will the second reply say? Then show why the old key failed, with `content_key` on the two dates as written.

# %%
from ledgerline.agent.tools import content_key

erp_i = ERP()
tb_i = Toolbox(erp_i, "ECLARKE", names=ALL)
first = {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "9 Nov 2026", "confirm": True}
retry = {**first, "need_by": "2026-11-09"}
a = tb_i.call("create_purchase_request", first)
b = tb_i.call("create_purchase_request", retry)
print(a["request_no"], b.get("request_no"), "already_done:", b.get("already_done"))
print("purchase requests in Ledgerline today:", erp_i.q("SELECT pr_no, need_dt FROM pr_hdr WHERE raised_on >= '2026-10-26'"))
SOLUTION = True
if SOLUTION:
    print("key, dates as written:     ", content_key("BAT-500", 2000, "PRD-07", "9 Nov 2026"), content_key("BAT-500", 2000, "PRD-07", "2026-11-09"))
    clean = REGISTRY["create_purchase_request"].check(first)["need_by"]
    print("key, after the door:       ", content_key("BAT-500", 2000, "PRD-07", clean), content_key("BAT-500", 2000, "PRD-07", "2026-11-09"))

# %% [markdown]
# ## Your turn: A4
#
# A4 asks you to do all of this for **your own domain**: build one tool from your system's service definitions (Part 1,
# exercise 3 is the template), put it on MCP and paste the raw JSON-RPC (Part 2, section 5), run the same task on Claude
# Code and on this notebook's harness (Part 3, sections 6–7), and measure it against at least five of the ten production
# criteria, fixing one (Part 4, section 8). Details in `A4.md`.
