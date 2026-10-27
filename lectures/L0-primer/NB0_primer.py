# %% [markdown]
# # NB0 · Primer: Python, HTTP, an ERP, and one model call
#
# **From Forms to Agents** · AI Agents for Enterprises (Vizuara) · about 45 minutes, on your own, before Lecture 1.
#
# The whole course follows one order. On Monday 26 October 2026, Kavita Joshi, a purchase executive at
# **Rasoi Steel Works, Pune** (a pressure-cooker maker), must order 20,000 silicone gaskets from Deccan Polymers.
# Her company runs **Bahi ERP 7.2**. Everything here is fictional: the vendor, the plant, the people and the data.
#
# This primer gives you four things you will use from the first minute of Lecture 1:
#
# 1. **Python, JSON and HTTP**, on Bahi's real replies.
# 2. **What an ERP is**: master data, transactions, documents and statuses, on Bahi's own tables.
# 3. **What a language-model call is**: messages in, text out, tokens, seconds and rupees.
# 4. **Tool calling**: the model writes a JSON request, your code runs it, the result goes back.
#
# There are 5 short exercises, marked `TODO (exercise N)`. Each has a working solution under it, so the
# notebook runs top to bottom as it is. Try each one before you read the solution.
#
# **Replay mode.** You do not need an API key. Every model call in this notebook was recorded in our run and
# plays back with its real token counts and seconds. Set a key in the next cell only if you want to call a model live.

# %% setup

# %% [markdown]
# ## 1. Python and JSON, on a real Bahi reply
#
# Bahi answers every request with the same small envelope:
# `rc` (S success, W warning, E error), `err_cd` (an error code), `msg` (a terse message) and `data`.
# In Python, JSON objects become **dicts** and JSON arrays become **lists**.
#
# We start Bahi in this notebook. `ERP()` builds a fresh sandbox in memory with the seed data
# (the clock is fixed at Monday 26 Oct 2026, 09:00).

# %%
import json
import pandas as pd
from bahi import ERP

erp = ERP()
kavita = erp.session("KJOSHI")              # signed in as Kavita, inside this notebook (no HTTP yet)
env = kavita.call("stk_query", itm_cd="GSK-SIL-05L")
print(type(env))
env

# %% [markdown]
# `env` is a dict. `env["data"]` is another dict. Read a value with square brackets.
# `json.dumps` turns a dict into JSON text (what travels over the wire); `json.loads` turns it back.

# %%
text = json.dumps(env)
print(len(text), "characters of JSON on the wire:")
print(text)
back = json.loads(text)
print("\nSame thing after a round trip:", back == env)
print("on hand:", back["data"]["on_hand"], "· daily use:", back["data"]["avg_daily_issue"])


def ind(n):
    """Indian digit grouping: 280840 -> '2,80,840'."""
    neg, n = n < 0, int(round(abs(n)))
    s = str(n)
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("-" if neg else "") + s


print("Kavita's order, gross:", "₹" + ind(20000 * 11.90 * 1.18))

# %% [markdown]
# ### TODO (exercise 1): days of cover
# Bahi already returns `cover_days`. Compute it yourself from `on_hand`, `allocated` and `avg_daily_issue`
# (cover = (on hand − allocated) ÷ daily use, rounded down), and check that you get the same number.

# %%
d = env["data"]
my_cover = None  # TODO (exercise 1): replace None with your expression
SOLUTION = True
if SOLUTION and my_cover is None:
    my_cover = (d["on_hand"] - d["allocated"]) // d["avg_daily_issue"]
print("my cover:", my_cover, "days · Bahi says:", d["cover_days"], "·", "match" if my_cover == d["cover_days"] else "different")

# %% [markdown]
# ## 2. HTTP: how any other system reaches Bahi
#
# Kavita's legacy client, an n8n workflow and your agent all reach Bahi the same way: **HTTP requests**.
# A request has a **method** (GET reads, POST sends a body), a **URL**, **headers** (for example who you are)
# and a **body** (JSON). The reply has a **status code** (200 OK, 401 not signed in, 504 no reply in time),
# headers and a body.
#
# `serve()` starts the Bahi server in the background of this notebook (in Colab it also prints a link to the
# legacy client). Then we talk to it with `httpx`, a plain HTTP library.

# %%
import httpx
from bahi.server import serve

url = serve(port=8077)

r = httpx.post(url + "/login", json={"user_id": "KJOSHI", "password": "kavita@123"})
login_status = r.status_code
print("status code:", r.status_code)
print("content-type header:", r.headers["content-type"])
login = r.json()
token = login["token"]
print({k: v for k, v in login.items() if k != "token"}, "· token:", token[:4] + "…")

# %% [markdown]
# The token proves who you are. Every service call sends it in the `Authorization` header.
# Without it, Bahi answers 401.

# %%
r = httpx.post(url + "/svc/stk_query", json={"itm_cd": "GSK-SIL-05L"},
               headers={"Authorization": f"Bearer {token}"})
print("with the token:   ", r.status_code, r.json()["data"]["on_hand"], "on hand")
r_no = httpx.post(url + "/svc/stk_query", json={"itm_cd": "GSK-SIL-05L"})
print("without the token:", r_no.status_code, r_no.json())
http_env = r.json()
http_env

# %% [markdown]
# Writing headers by hand gets old. `BahiClient` (in `bahi/client.py`, about 80 lines) signs in once and keeps the token.

# %%
from bahi.client import BahiClient

k = BahiClient(url, "KJOSHI", "kavita@123")
print(k)
k.call("stk_query", itm_cd="GSK-SIL-05L")

# %% [markdown]
# ### TODO (exercise 2): read an old order over HTTP
# Use `k.call("po_get", po_no=...)` to fetch purchase order `PO/2026/01120` (Kavita's last gasket order).
# Print its supplier, status and gross value in rupees with Indian grouping.

# %%
po = None  # TODO (exercise 2): po = k.call(...)
if SOLUTION and po is None:
    po = k.call("po_get", po_no="PO/2026/01120")
p = po["data"]
print(p["po_no"], "·", p["sup_cd"], "· status", p["status"], "· gross ₹" + ind(p["gross_value"]))

# %% [markdown]
# ## 3. What an ERP is
#
# An **ERP** (enterprise resource planning system) is a company's book of record. Bahi keeps it in tables.
# Two kinds of data matter.
#
# **Master data** changes slowly: items, suppliers, cost centres, users. Every transaction points at it by **code**.

# %%
pd.DataFrame(erp.q("SELECT itm_cd, descr, uom_cd, food_contact, active FROM item"))

# %%
pd.DataFrame(erp.q("SELECT sup_cd, name, city, state, status FROM supplier"))

# %%
pd.DataFrame(erp.q("SELECT cc_cd, name, status, closed_on FROM cost_centre"))

# %% [markdown]
# Look at the codes. `DP-RJK-0042` and `DP-RJK-0009` are both Deccan Polymers; one is blocked.
# `PRD-05`, Kavita's default cost centre, closed on 15 October. Remember both: Lecture 1 trips over them.
#
# **Transactions** are business events written as **documents**: a purchase request (PR), a purchase order (PO).
# A document has a number, a header and lines.

# %%
pd.DataFrame(erp.q("""SELECT h.po_no, h.sup_cd, l.itm_cd, l.qty, l.rate, h.gross_value, h.cc_cd, h.status, h.created_on
                      FROM po_hdr h JOIN po_line l ON l.po_no = h.po_no ORDER BY h.po_no"""))

# %% [markdown]
# Every document carries a **status**, and only some moves between statuses are allowed.
#
# | Code | Means | Next |
# |---|---|---|
# | DR | Draft: saved, not sent to anyone | PA, AP or CN |
# | PA | Pending approval | AP, RJ or CN |
# | AP | Approved, not yet sent to the supplier | RL or CN |
# | RL | Released: sent to the supplier | CN (or CL when received) |
# | RJ | Rejected | (end) |
# | CN | Cancelled | (end) |
# | CL | Closed (a request turned into an order) | (end) |
#
# Only **RL** means the supplier has the order. The services enforce these moves: try releasing an order that
# is still waiting for approval.

# %%
print(pd.DataFrame(erp.q("SELECT status, count(*) AS orders FROM po_hdr GROUP BY status")).to_string(index=False))
rel = kavita.call("po_release", po_no="PO/2026/01179")   # this one is PA: pending approval
print("\nRelease a PA order:", rel["rc"], rel["err_cd"], rel["msg"])

# %% [markdown]
# ### TODO (exercise 3): which orders went to closed cost centres?
# Write one SQL query (with `erp.q`) that lists every purchase order charged to a cost centre whose status is
# CLOSED, with the order number, the cost centre and the order status. (Hint: JOIN `po_hdr` with `cost_centre`.)

# %%
sql = None  # TODO (exercise 3): sql = "SELECT ..."
if SOLUTION and sql is None:
    sql = ("SELECT h.po_no, h.cc_cd, c.status AS cc_status, h.status AS po_status FROM po_hdr h "
           "JOIN cost_centre c ON c.cc_cd = h.cc_cd WHERE c.status = 'CLOSED' ORDER BY h.po_no")
closed = pd.DataFrame(erp.q(sql))
closed

# %% [markdown]
# Those orders were placed before PRD-05 closed. A new order on PRD-05 today would not be rejected:
# Bahi saves it as Draft and says nothing. That is the failure Lecture 1 opens with.
#
# ## 4. What a language-model call is
#
# A language model reads a list of **messages** and writes the next message. That is all.
# It does not remember anything between calls, and it cannot see Bahi unless we put Bahi's data in the messages.
#
# Text is cut into **tokens** (pieces of words, about 4 characters of English each). You pay per token,
# separately for tokens in (what you send) and tokens out (what it writes). `bahi.llm.LLM` is one small client
# for every model in the course, with the replay cassette built in.

# %%
from bahi.llm import LLM, PRICES, USD_INR, tool_schema

llm = LLM("gemini:gemini-3.8-flash", cassette="L0_primer")
q1 = [{"role": "user", "content": "In one sentence, what is a purchase order?"}]
r1 = llm.chat(q1)
print(r1.content)
print(f"\ntokens in {r1.tokens_in} · tokens out {r1.tokens_out} · {r1.seconds} s · ₹{r1.cost_inr} · replayed: {r1.replayed}")

# %% [markdown]
# **Where the rupees come from.** Each model has a list price in US dollars per million tokens, one for input
# and one for output (`bahi.llm.PRICES`). The course fixes ₹88 to the dollar so runs compare.

# %%
print("USD → ₹:", USD_INR)
for m, (pin, pout) in PRICES.items():
    if m in ("gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-pro-preview"):
        print(f"{m:<24} ${pin:>5} in · ${pout:>5} out  per million tokens")

# %% [markdown]
# ### TODO (exercise 4): compute the cost yourself
# Write `cost_inr(tokens_in, tokens_out, model_id)` using `PRICES` and `USD_INR`, and check it against `r1.cost_inr`.

# %%
def cost_inr(tokens_in, tokens_out, model_id):
    return None  # TODO (exercise 4)


if SOLUTION and cost_inr(1, 1, "gemini-3.8-flash") is None:
    def cost_inr(tokens_in, tokens_out, model_id):
        pin, pout = PRICES[model_id]
        return round((tokens_in * pin + tokens_out * pout) / 1e6 * USD_INR, 4)

mine = cost_inr(r1.tokens_in, r1.tokens_out, "gemini-3.8-flash")
print(f"my cost ₹{mine} · the client's ₹{r1.cost_inr} · {'match' if abs(mine - r1.cost_inr) < 1e-9 else 'different'}")

# %% [markdown]
# **A smaller model costs less.** The same question on the small tier:

# %%
small = LLM("gemini:gemini-3.5-flash-lite", cassette="L0_primer")
r1s = small.chat(q1)
print(r1s.content)
print(f"\nsmall:   tokens {r1s.tokens_in}+{r1s.tokens_out} · {r1s.seconds} s · ₹{r1s.cost_inr}")
print(f"default: tokens {r1.tokens_in}+{r1.tokens_out} · {r1.seconds} s · ₹{r1.cost_inr}")

# %% [markdown]
# ### The context is all it sees
# Ask the model something only Bahi knows.

# %%
q2 = [{"role": "user", "content": "What is Kavita Joshi's approval limit at Rasoi Steel Works? Answer in one sentence."}]
r2 = llm.chat(q2)
print("WITHOUT the fact:\n", r2.content)

# %% [markdown]
# It cannot know. Now put Bahi's own record in the messages, as a system message, and ask again.

# %%
fact = kavita.call("usr_get", user_id="KJOSHI")["data"]
print("From Bahi:", fact)
q3 = [{"role": "system", "content": "Bahi ERP user record: " + json.dumps(fact)}] + q2
r3 = llm.chat(q3)
print("\nWITH the fact:\n", r3.content)
print(f"\ntokens in: {r2.tokens_in} without the fact, {r3.tokens_in} with it")

# %% [markdown]
# Everything the model knows about Kavita came from the messages we sent. The list of messages it can read at once
# is its **context window**. An agent is mostly the code that decides what goes into it.
#
# ## 5. Tool calling
#
# Pasting data by hand does not scale. Instead we describe a **tool** (a name, a sentence, and the JSON fields it
# takes). The model may answer with a **tool call**: a small JSON request. It does not run anything itself.
# **Our code** runs the call against Bahi and sends the result back as a `tool` message. Then the model answers.
#
# Here is one tiny tool: Bahi's stock enquiry.

# %%
stock_tool = tool_schema("stk_query", "Stock of one item in one warehouse (default Pune main stores).",
                         {"itm_cd": {"type": "string", "description": "Item code, e.g. GSK-SIL-05L"},
                          "whs_cd": {"type": "string", "description": "Warehouse code, default WH-PUN-STR"}},
                         ["itm_cd"])
print(json.dumps(stock_tool, indent=1))

# %%
msgs = [{"role": "user", "content": "How many 5-litre silicone gaskets (GSK-SIL-05L) do we have in the Pune store, "
                                    "and how many days will they last?"}]
t1 = llm.chat(msgs, tools=[stock_tool])
print("text:", t1.content)
for tc in t1.tool_calls:
    print("tool call:", json.dumps({"id": tc.id, "name": tc.name, "arguments": tc.arguments}))
print(f"tokens in {t1.tokens_in} · out {t1.tokens_out} · ₹{t1.cost_inr}")

# %% [markdown]
# The model wrote JSON and stopped. Now our code runs it, as Kavita, and sends the envelope back.

# %%
msgs.append(t1.message())
for tc in t1.tool_calls:
    out = kavita.call(tc.name, **tc.arguments)
    print("Bahi returned:", json.dumps(out))
    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out)})
t2 = llm.chat(msgs, tools=[stock_tool])
print("\nANSWER:", t2.content)
print(f"tokens in {t2.tokens_in} · out {t2.tokens_out} · ₹{t2.cost_inr}")

# %% [markdown]
# That is the whole mechanism of an agent: **model → tool call → our code runs it → result → model**, repeated.
# In Lecture 1 you put it in a loop and give it all 38 of Bahi's services. Then we watch what goes wrong.
#
# ### TODO (exercise 5): a second tool
# Write a tool schema for `po_get` (one required field `po_no`) and ask: "What is the status of PO/2026/01179?"
# Run the tool call on Bahi and send the result back. (The solution's two model calls are in the replay cassette;
# if you change the question or the schema, you need a key to run it live.)

# %%
po_tool = None  # TODO (exercise 5): po_tool = tool_schema(...)
if SOLUTION and po_tool is None:
    po_tool = tool_schema("po_get", "Read one purchase order: header, line and status code.",
                          {"po_no": {"type": "string", "description": "Order number, e.g. PO/2026/01120"}}, ["po_no"])
m5 = [{"role": "user", "content": "What is the status of PO/2026/01179? Explain the status code in plain words."}]
a = llm.chat(m5, tools=[stock_tool, po_tool])
m5.append(a.message())
for tc in a.tool_calls:
    print("tool call:", tc.name, json.dumps(tc.arguments))
    m5.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(kavita.call(tc.name, **tc.arguments), default=str)})
b = llm.chat(m5, tools=[stock_tool, po_tool]) if a.tool_calls else a
print("ANSWER:", b.content)

# %% [markdown]
# ## 6. What it all cost

# %%
rows = [{"call": n, "model": x.model.split(":")[1], "tokens in": x.tokens_in, "tokens out": x.tokens_out,
         "seconds": x.seconds, "₹": x.cost_inr}
        for n, x in [("what is a PO", r1), ("what is a PO (small)", r1s), ("limit, no fact", r2), ("limit, with fact", r3),
                     ("stock: tool call", t1), ("stock: answer", t2), ("ex 5: tool call", a), ("ex 5: answer", b)]]
costs = pd.DataFrame(rows)
print(costs.to_string(index=False))
print(f"\nTotal: {costs['tokens in'].sum() + costs['tokens out'].sum()} tokens · ₹{round(costs['₹'].sum(), 4)}")

# %%
# Save the numbers the primer slides use (so every number on a plate comes from this run).
import os
import pathlib

here = pathlib.Path("experiments/logs")
if os.environ.get("BAHI_IN_MODAL"):
    here.mkdir(parents=True, exist_ok=True)
    numbers = {
        "source": "lectures/L0-primer/NB0_primer.ipynb (executed)",
        "stk_query_envelope": http_env,
        "po_01120": {k2: p[k2] for k2 in ("po_no", "sup_cd", "status", "gross_value")},
        "po_status_counts": {x["status"]: x["orders"] for x in erp.q("SELECT status, count(*) AS orders FROM po_hdr GROUP BY status")},
        "release_pa_error": {"err_cd": rel["err_cd"], "msg": rel["msg"]},
        "closed_cc_orders": closed.to_dict("records"),
        "login": {"status_code": login_status, "role_cd": login["role_cd"], "msg": login["msg"]},
        "no_token": {"status_code": r_no.status_code, "body": r_no.json()},
        "calls": rows,
        "texts": {"what_is_po": r1.content, "what_is_po_small": r1s.content, "limit_without": r2.content,
                  "limit_with": r3.content, "stock_answer": t2.content, "ex5_answer": b.content},
        "tool_schema": stock_tool,
        "tool_call": [{"id": tc.id, "name": tc.name, "arguments": tc.arguments} for tc in t1.tool_calls],
        "tool_result": json.loads(msgs[-1]["content"]),
        "user_record": fact,
        "prices_usd_per_m": {m: PRICES[m] for m in ("gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-pro-preview")},
        "usd_inr": USD_INR,
    }
    (here / "primer_numbers.json").write_text(json.dumps(numbers, indent=1, ensure_ascii=False, default=str))
    print("wrote", here / "primer_numbers.json")

# %% [markdown]
# ## Before Lecture 1 (Saturday 31 October, 7–9 AM IST)
#
# - [ ] This notebook ran top to bottom in Colab (replay mode is fine).
# - [ ] You can explain the envelope `{rc, err_cd, msg, data}` and what a 401 means.
# - [ ] You know the difference between master data and a document, and which status means the supplier has the order (RL).
# - [ ] You can say where a model call's rupees come from (tokens in and out × price).
# - [ ] You can describe tool calling in one sentence: the model writes a JSON request; our code runs it.
# - [ ] Optional: a Gemini key, or an OpenRouter key if you want to try GPT or Claude (we did not run those; the
#   recorded numbers in this course are from Gemini).
# - [ ] Think of one task in your own work that takes several screens of an enterprise system. You will need it for assignment A1.
