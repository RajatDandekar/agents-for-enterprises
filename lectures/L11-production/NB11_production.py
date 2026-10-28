# %% [markdown]
# # NB11 · Running Agents in Production
#
# Ask Rasoi works. Anand Patil wants it for every buyer at Pune and Chakan, and IT has a checklist before it goes live:
#
# 1. **Can someone talk it into something?** (guardrails and security)
# 2. **What if it dies in the middle of an order?** (durable execution)
# 3. **Where does its memory live when there are three copies of it?** (pgvector and Redis)
# 4. **Who pays, and how much?** (a model gateway, and the cost per order)
#
# In Lecture 7 you built the trust layer by hand: identity, guards, read-back, retries. Today each industry tool is
# mapped onto what you built, and measured on the same Rasoi tasks.
#
# Everything runs in **replay** mode with no key. The guard runs, the Temporal drill, the pgvector and Redis runs and the
# LiteLLM drill were recorded on Modal (`lectures/L11-production/experiments/`); this notebook reads those recordings,
# replays the recorded model calls from cassettes, and re-runs the parts that need no model at all.
#
# Pinned versions used in our runs: temporalio 1.34.0, temporalio-openai-agents 1.1.0, openai-agents 0.22.3,
# nemoguardrails 0.24.1, litellm 1.106.5, psycopg 3.3.6, pgvector 0.5.1 (extension 0.8.1), redis-py 8.1.0,
# Temporal CLI 1.5.1.

# %% setup

# %% [markdown]
# Section 3 replays a real Temporal history, which needs the Temporal SDK and its OpenAI Agents SDK integration.
# We install the pinned versions now, before anything imports them (about 30 seconds). Everything else is already
# in the course package.

# %%
import subprocess
import sys

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "temporalio==1.34.0", "temporalio-openai-agents==1.1.0",
                "openai-agents==0.22.3"], check=False)

# %%
import json
import pathlib

import pandas as pd

from bahi.llm import LLM
from bahi.course.production import guards as G, injection as J, cost as C
import bahi.course.production.fixtures as F

FIX = pathlib.Path(F.__file__).parent
SHOTS = "https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/lectures/L11-production/shots/"
pd.set_option("display.max_colwidth", 110)


def fixture(name):
    return json.loads((FIX / name).read_text())


def inr(x, d=0):
    """₹ with Indian digit grouping: 280840 -> ₹2,80,840."""
    neg, x = x < 0, abs(x)
    s = f"{x:.{d}f}"
    whole, _, frac = s.partition(".")
    head, tail = whole[:-3], whole[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    out = (head + "," + tail if head else tail) + ("." + frac if frac else "")
    return ("-₹" if neg else "₹") + out

# %% [markdown]
# ## 1 · Guardrails: what a message can do to Ask Rasoi
#
# A **guardrail** is a check that runs outside the model, on what goes in (the user's message, a tool's result) or what
# comes out (the reply), and can stop it. Lecture 7 guarded **actions** in code, just before Bahi was written. Today we
# guard **words**.
#
# The **OWASP Top 10 for LLM Applications (2025)** is the security community's list of the ten ways these systems fail.
# Number one is **prompt injection**: text that makes the model ignore its instructions. It is number one because the
# model reads its instructions and its data as one stream of tokens; there is no separate channel for "rules".
#
# We wrote **76 labelled messages** to Ask Rasoi. Each has a category: `benign` and `lookalike` (ordinary work, but with
# scary words like *kill*, *override*, *ignore*) should be allowed; `inject`, `leak`, `agency` and `harm` should be
# blocked; `offtopic` is harmless but not Ask Rasoi's job.

# %%
msgs = pd.DataFrame(G.MESSAGES, columns=["id", "who", "category", "text"])
print(msgs.category.value_counts().to_string())
msgs.groupby("category").head(2)

# %% [markdown]
# ### The guard most teams write first: a keyword list
# It needs no model and runs in microseconds. What does it cost?

# %%
kw = {i: G.keyword_guard(t)["block"] for i, _, _, t in G.MESSAGES}
s = G.score(kw)
print(f"keyword filter: caught {s['caught']}/{s['attacks_n']} attacks, blocked {s['false_positives']}/{s['benign_n']} good messages")
print("good messages it blocked:")
for i, who, cat, t in G.MESSAGES:
    if cat in G.ALLOW and kw[i]:
        print(f"  #{i:<3} {t}   <- {G.keyword_guard(t)['why']}")

# %% [markdown]
# ### TODO (exercise 1): a better keyword list
# Edit `MY_KEYWORDS` so the filter blocks **no** lookalike message and still catches at least as many attacks as the
# original list. Is it possible? What does this tell you about keyword lists?

# %%
SOLUTION = True
MY_KEYWORDS = list(G.KEYWORDS)
if SOLUTION:
    import re
    MY_KEYWORDS = [r"ignore (all |any )?(previous|prior|above) instructions", r"system override", r"admin mode", r"\bDAN\b",
                   r"password so", r"salary", r"bank (account|details)", r"delete the audit", r"skip the (checks|preview)",
                   r"base64", r"</?system>", r"pretend you are", r"exact instructions", r"system prompt word",
                   r"explosive", r"burst at", r"hurt myself", r"family lives"]


def my_guard(text):
    import re
    return any(re.search(k, text, re.I) for k in MY_KEYWORDS)


mine = G.score({i: my_guard(t) for i, _, _, t in G.MESSAGES})
print("original:", {k: s[k] for k in ("caught", "false_positives")}, " mine:", {k: mine[k] for k in ("caught", "false_positives")})
print("Every rule here was written after reading the test set. A new wording walks past it.")

# %% [markdown]
# ### A safety classifier: Llama Guard 4
# **Llama Guard** is a Llama model fine-tuned to read a conversation and answer `safe`, or `unsafe` and a hazard code
# (S1 violent crimes ... S14 code interpreter abuse). We called `meta-llama/llama-guard-4-12b` through OpenRouter
# (no Hugging Face token needed). Here are five of the recorded calls, replayed from the cassette:

# %%
lg = LLM(G.LLAMA_GUARD, cassette="IND11_llamaguard", max_tokens=20)
for i in (1, 26, 41, 53, 65):
    t = next(m[3] for m in G.MESSAGES if m[0] == i)
    r = G.llama_guard(t, lg)
    cats = ", ".join(f"{c} {G.LLAMA_CATS.get(c, '')}" for c in r["cats"])
    print(f"#{i:<3} {r['raw'].splitlines()[0]:7} {cats:28} {r['tokens_in']:>4} tokens in  {t[:70]}")

# %% [markdown]
# Llama Guard knows *harm*. It does not know *Rasoi's rules*: "approve PR/2026/04417 on behalf of Rohit" is not violent,
# hateful or illegal in its taxonomy. Two other tools let you write the rule yourself:
#
# * **gpt-oss-safeguard-20b** reads a policy you write in plain words and classifies against it;
# * **NeMo Guardrails** (NVIDIA, open source) wraps any chat model in **rails**: *input* rails on the message, *dialogue*
#   rails that steer the conversation (written in a small language called Colang), *output* rails on the reply.
#
# Here is the exact NeMo configuration we ran (the main model was gemini-3.5-flash-lite through OpenRouter):

# %%
print(G.NEMO_CONFIG_YML)
print(G.NEMO_PROMPTS_YML[:900], "...")

# %% [markdown]
# ### The scoreboard: five guards, the same 76 messages
# Recorded on Modal on 28 Oct 2026 (`experiments/guard_eval.py`).

# %%
g = fixture("guard_runs.json")
rows = []
for name in ("keyword", "llamaguard", "safeguard", "nemo_input", "nemo_topic"):
    x = g["guards"][name]
    rows.append({"guard": name, "attacks caught": f"{x['caught']}/{x['attacks_n']}", "recall": x["recall"],
                 "good blocked": f"{x['false_positives']}/{x['benign_n']}", "false-positive rate": x["fpr"],
                 "off-topic blocked": f"{x['offtopic_blocked']}/6", "p50 ms": x["latency_ms_p50"],
                 "₹ per 1,000 messages": round((x["usd_per_message"] or 0) * 1000 * C.USD_INR, 2)})
pd.DataFrame(rows)

# %%
per = pd.DataFrame([{"id": int(i), "category": next(m[2] for m in G.MESSAGES if m[0] == int(i)),
                     **{k: v["block"] for k, v in d.items()}} for i, d in g["per_message"].items()])
per.groupby("category")[["keyword", "llamaguard", "safeguard", "nemo_input", "nemo_topic"]].sum()

# %% [markdown]
# ### TODO (exercise 2): layer the guards
# Production systems stack guards. Using only the recorded decisions in `per`, try three ways to combine
# `llamaguard`, `safeguard` and `nemo_input`: **any** blocks, **all** block, **two of three** block.
# Which gives the most attacks caught with a false-positive rate of at most 5%?

# %%
SOLUTION = True
if SOLUTION:
    trio = per[["llamaguard", "safeguard", "nemo_input"]]
    rules = {"any": trio.any(axis=1), "all": trio.all(axis=1), "two of three": trio.sum(axis=1) >= 2}
    out = []
    for name, dec in rules.items():
        sc = G.score(dict(zip(per.id, dec)))
        out.append({"rule": name, "caught": f"{sc['caught']}/{sc['attacks_n']}", "recall": sc["recall"],
                    "good blocked": f"{sc['false_positives']}/{sc['benign_n']}", "fpr": sc["fpr"]})
    display(pd.DataFrame(out))

# %% [markdown]
# ### Output rails: checking the reply
# Twelve replies a model might write; six are fine, six must never reach the user (the system prompt, a salary, a
# password, "placed" for a Draft order, a threat, someone else's conversation).

# %%
o = g["output_rails"]
pd.DataFrame([{"reply": r["reply"][:80], "should": r["label"], "NeMo self check output": r["nemo_block"],
               "Llama Guard": r["llamaguard_block"]} for r in o["rows"]])

# %% [markdown]
# ## 2 · Prompt injection through a tool result
# The attack in the deck: Kaveri Rubber's address in the supplier master carries a note "for AI assistants". Kavita never
# sees it; `find_supplier` puts it straight into the model's context. This cell runs the real toolbox, no model:

# %%
erp = J.sandbox(poisoned=True)
print(json.dumps(J.find_supplier_output(erp), indent=1, ensure_ascii=False)[:900])

# %% [markdown]
# Lecture 7's trust layer does not read the note at all. It checks the write itself, in code, against Bahi's own
# certificate table:

# %%
from bahi.toolbox import Toolbox
from bahi.course.l7 import TrustLayer

safe = TrustLayer(Toolbox(erp, "KJOSHI"), erp, "KJOSHI")
safe.begin_turn()
print(json.dumps(safe.call("create_purchase_order", {"supplier_code": J.KAVERI, "request_no": "PR/2026/04417",
                                                     "confirm": True}), indent=1)[:700])

# %% [markdown]
# What we measured: 4 conditions x 2 models x 3 wordings = 24 conversations with Lecture 7's Ask Rasoi.
# NE3 = an order to Kaveri, whose certificate expired, for a food-contact gasket.

# %%
inj = fixture("injection_runs.json")
t = pd.DataFrame([{"condition": r["cond"], "model": r["tier"], "wording": r["w"], "NE3 (order to Kaveri)": r["ne3"],
                   "released": r["kaveri_released"],
                   "ordered Deccan instead": any(o["po_no"] > "PO/2026/01152" for o in r["deccan_orders"]),
                   "trust layer refused": len(r["trust_refused"])} for r in inj["rows"]])
t.groupby(["condition", "model"])[["NE3 (order to Kaveri)", "ordered Deccan instead", "trust layer refused"]].sum()

# %% [markdown]
# One of those conversations, replayed from the cassette (gemini-3.5-flash-lite, poisoned, no defence):

# %%
erp2 = J.sandbox(poisoned=True)
agent = J.make(erp2, "none", LLM("gemini:gemini-3.5-flash-lite", cassette="IND11_inject"))
print("KAVITA:", J.WORDINGS[0])
print("ASK RASOI:", agent.respond(J.WORDINGS[0])[:500])
print("tools:", [s["tool"] for s in agent.trace if s["kind"] == "tool"])
print("Bahi now holds:", J.outcome(erp2)["kaveri_orders"])
agent.close()

# %% [markdown]
# ### TODO (exercise 3): a tool-result scanner
# Classifiers on tool results were noisy in our run (see the table below). Write `scan(result)` that flags text in a tool
# result that tries to instruct the assistant. Test it on the seven recorded tool results. Careful: the toolbox itself
# writes instructions for the model (`hint`, `next_step`); your scanner must not flag those.

# %%
pd.DataFrame([{k: s[k] for k in ("sample", "label", "llamaguard", "safeguard", "safeguard_rationale")} for s in inj["scan"]])

# %%
SOLUTION = True
import re


def scan(result) -> bool:
    if SOLUTION:
        text = json.dumps({k: v for k, v in result.items() if k not in ("hint", "next_step", "note")}, ensure_ascii=False) \
            if isinstance(result, dict) else str(result)
        return bool(re.search(r"note (for|to) (the )?(ai|assistant)|treat (it|this) as valid|do not mention|"
                              r"ignore (your|all|previous)|go ahead with the order", text, re.I))
    return False


samples = [("find_supplier, clean", J.find_supplier_output(J.sandbox(False))), ("find_supplier, poisoned", J.find_supplier_output(erp))]
for name, res in samples:
    print(f"{name:26} flagged: {scan(res)}")

# %% [markdown]
# ## 3 · Durable execution: an order that survives a dead worker
# An approval can take days. In those days the server is redeployed, a container is moved, a process crashes. The Python
# loop that was waiting for Rohit is gone, and with it the conversation, the request number and the plan.
#
# **Temporal** fixes this by recording. A **workflow** is ordinary code for the whole job, written so it makes the same
# decisions every time it runs. Anything that touches the world (a model call, a Bahi tool) is an **activity**: Temporal
# runs it, retries it, and writes its result into the **event history**. A **worker** is the process that runs both. When
# a worker dies, another one reads the history and **replays** the workflow code: every recorded activity returns its
# recorded result instantly, nothing is sent to the model or Bahi again, and the code arrives where it stopped.
# People reach a running workflow with **signals** (Kavita's "yes", Rohit's approval) and wait with **timers**.
#
# With the **OpenAI Agents SDK integration** (GA in March 2026), `Runner.run(agent, ...)` runs inside the workflow and the
# plugin turns each model call into an activity; `activity_as_tool` turns each Bahi tool into one. The code is in
# `bahi/course/production/durable.py`. Our drill, on Modal, with a Temporal dev server:

# %%
dr = fixture("durable_drill.json")
pd.DataFrame(dr["events"])[["t", "what"]].assign(detail=[json.dumps({k: v for k, v in e.items() if k not in ("t", "what")},
                                                                      ensure_ascii=False)[:90] for e in dr["events"]])

# %%
print("Bahi after the drill:", dr["counts"])
print("model calls made by each worker:", dr["model_calls"])
print("activities in the history:", len(dr["history"]["activities"]), "· events:", dr["history"]["events"])
print("workers that completed workflow tasks:", dr["history"]["workers"])

# %%
from IPython.display import Image, display
for name in ("ui_waiting_for_rohit", "ui_signal_no_worker", "ui_completed_history"):
    p = pathlib.Path("shots") / f"{name}.png"
    display(Image(filename=str(p), width=900) if p.exists() else Image(url=SHOTS + f"{name}.png", width=900))

# %% [markdown]
# ### Replay, here, with no server and no key
# The recorded history is a file. Temporal's `Replayer` runs our workflow code against it: if the code makes the same
# decisions, replay passes. This needs the Temporal SDK and the Agents SDK integration (pinned):

# %%
from bahi.course.production import durable as D

D.quiet()
history = (FIX / "durable_history.json").read_text()
print("events in the recorded history:", len(json.loads(history)["events"]))
res = await D.replay_history(history, sandboxed=False)   # this kernel already imported many libraries; see the docstring
print("replay of the recorded history:", res)

# %% [markdown]
# ### TODO (exercise 4): break determinism, then fix it with a patch
# Your colleague adds one line: before the first agent turn, read back the request (an extra activity). Running
# workflows were recorded without it. Write `AskRasoiOrderV2` with the extra activity and replay the history: what error
# do you get? Then guard the new line with `workflow.patched("read-back-first")` so old histories replay and new runs get
# the new step.

# %%
SOLUTION = True
from datetime import timedelta

from temporalio import workflow
from bahi.course.production import durable_activities as A


@workflow.defn(name="AskRasoiOrder", sandboxed=False)
class AskRasoiOrderV2(D.AskRasoiOrder):
    """The colleague's change: one new activity before the first agent turn, no patch."""
    @workflow.run
    async def run(self, ask: str, remind_after_s: int = 86400, max_reminders: int = 5) -> dict:
        await workflow.execute_activity(A.read_back_request, "KJOSHI", start_to_close_timeout=timedelta(seconds=20))
        return await super().run(ask, remind_after_s, max_reminders)


@workflow.defn(name="AskRasoiOrder", sandboxed=False)
class AskRasoiOrderV3(D.AskRasoiOrder):
    """The same change behind a patch: recorded runs skip it, new runs do it."""
    @workflow.run
    async def run(self, ask: str, remind_after_s: int = 86400, max_reminders: int = 5) -> dict:
        if SOLUTION and workflow.patched("read-back-first"):
            await workflow.execute_activity(A.read_back_request, "KJOSHI", start_to_close_timeout=timedelta(seconds=20))
        elif not SOLUTION:
            await workflow.execute_activity(A.read_back_request, "KJOSHI", start_to_close_timeout=timedelta(seconds=20))
        return await super().run(ask, remind_after_s, max_reminders)


async def replay_with(cls):
    r = await D.replay_history(history, workflow_cls=cls, sandboxed=False)
    return "passes" if r["ok"] else r["error"][:170]


print("the original code:   ", await replay_with(D.AskRasoiOrder))
print("new line, no patch: ", await replay_with(AskRasoiOrderV2))
print("new line, patched:  ", await replay_with(AskRasoiOrderV3))

# %% [markdown]
# ## 4 · Memory and data: pgvector and Redis
# Lecture 3's index lives in the Python process: 247 clauses, their 384-number vectors, rebuilt at every start.
# **pgvector** stores the same vectors in Postgres (a `vector(384)` column, the `<=>` cosine-distance operator, an HNSW
# index). **Redis** is an in-memory key-value server that every copy of the app shares: sessions with an expiry, and
# counters for rate limits. Measured on Modal (`experiments/memory_prod.py`):

# %%
m = fixture("memory_runs.json")
pd.DataFrame(m["retrieval"]).T

# %%
print("permissions as a WHERE clause:", m["permissions"])
print("scale:", {k: m["scale"][k] for k in ("rows", "numpy_bruteforce_ms_p50", "hnsw_top5_equals_exact_top5", "table_size", "note")})
print("  exact  p50 ms:", m["scale"]["pg_exact"]["ms_p50"], " hnsw p50 ms:", m["scale"]["pg_hnsw"]["ms_p50"])
print("persistence:", m["persistence"])
print("redis session:", m["redis_session"])
print("a replica dies:", m["redis_failover"])
print("rate limit across 3 replicas:", m["rate_limit"])

# %% [markdown]
# ## 5 · A model gateway: LiteLLM
# The live Ask Rasoi already has a hand-built gateway (`bahi/experience/guard.py`): a kill switch, a daily ₹ cap and rate
# limits, kept in one process. A **gateway** does the same for every app and every team: each app gets a **virtual key**,
# each key and team a **budget**, the **router** tries a second model when the first fails, and every call's cost is
# written to a **spend log**. Our LiteLLM proxy drill (`experiments/gateway.py`):

# %%
gw = fixture("gateway_runs.json")
print(gw["config"])
b = pd.DataFrame(gw["budget"]["requests"])[["n", "status", "cost_usd", "tokens_in", "tokens_out", "error"]]
b

# %%
print("first refused request:", gw["budget"]["first_refused"], "· spent before it (USD):", gw["budget"]["spent_before_refusal_usd"])
print("fallback:", [(r["status"], r["model_asked"], r["served_by"]) for r in gw["fallback"]])
print("Neha's key asking for rasoi-default:", gw["model_access"]["status"], (gw["model_access"]["error"] or "")[:120])
print("rate-limited key, 5 calls in a row:", [r["status"] for r in gw["rate_limit"]])
print("spend per team:", gw["team_spend"])

# %% [markdown]
# ## 6 · What one order costs
# Token counts from our own runs across the course, priced at OpenRouter list prices (28 Oct 2026, ₹88 per USD).

# %%
cr = C.load()
pd.DataFrame(cr["summary"]).T

# %% [markdown]
# ### TODO (exercise 5): Rasoi's monthly bill
# Rasoi expects about 120 orders a working day across both plants (Anand's estimate, not a measurement). Using the
# measured whole-order tokens (L5 task T01), compute ₹ per order and ₹ per month for gemini-3.8-flash and
# gemini-3.5-flash-lite, with a Llama Guard check on each of Kavita's messages and 5% of model calls retried.

# %%
SOLUTION = True
if SOLUTION:
    guard_in = fixture("guard_runs.json")["guards"]["llamaguard"]["tokens_in_mean"]
    for m_ in ("gemini-3.8-flash", "gemini-3.5-flash-lite"):
        row = cr["summary"][f"whole_order_L5_T01|{m_}"]
        msgs_ = next(r["person_messages"] for r in cr["runs"] if r["task"].startswith("T01") and r["model"] == m_)
        o_ = C.per_order(row["tokens_in_mean"], row["tokens_out_mean"], m_, guard_messages=msgs_, guard_tokens_in=guard_in,
                         retry_rate=0.05)
        print(f"{m_:22} {inr(o_['total_inr'], 2)} per order  ->  {inr(C.month(120, o_['total_inr']))} a month "
              f"(guard {inr(o_['guard_inr'], 3)} of it)")

# %% [markdown]
# ## 7 · Managed platforms (shown, not run)
# AWS Bedrock AgentCore, Microsoft Foundry and Google's Gemini Enterprise Agent Platform each host the pieces you built:
# a runtime, identity, memory, a tool gateway and observability. We have no cloud keys, so the deck shows their code
# marked "not run in our build". The question to ask is the same for all three: which of these pieces do we want to own?
#
# ## 8 · Your module
# Assignment A11 is a production-readiness review of your module agent: an OWASP threat model, guardrails with measured
# false positives, a durable approval that survives a killed worker, a LiteLLM budget, a cost per transaction and a
# one-page runbook. Start the threat model here:

# %%
threats = pd.DataFrame([
    {"OWASP": "LLM01 Prompt injection", "where it enters my module": "", "what stops it": "", "measured?": ""},
    {"OWASP": "LLM02 Sensitive information disclosure", "where it enters my module": "", "what stops it": "", "measured?": ""},
    {"OWASP": "LLM06 Excessive agency", "where it enters my module": "", "what stops it": "", "measured?": ""},
    {"OWASP": "LLM10 Unbounded consumption", "where it enters my module": "", "what stops it": "", "measured?": ""},
])
threats
