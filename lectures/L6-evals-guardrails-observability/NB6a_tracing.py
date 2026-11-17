# %% [markdown]
# # NB6a · Tracing: by hand, then for real
# **Lecture 6 · Observability and Evals · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# On Friday Ask Northbridge saved a £342,720 purchase request that Emma never confirmed. To find out what it did, we need a
# record of every step it took. That record is called a **trace**. In this notebook we build one from nothing:
#
# 1. three steps of work, recorded by hand: what a **span** is, and how spans make a **trace**
# 2. the same with **OpenTelemetry**, the standard every tool reads
# 3. one real turn of Ask Northbridge, traced; then Friday's turn, and the one span that explains it
# 4. sending the trace to **Langfuse** (and LangSmith and Sentry if you have keys)
# 5. a tour of what Langfuse keeps around a trace: sessions, scores, datasets, prompt versions
#
# **Two ways to run it.** With your Argus key, every model call below is live (through Argus's gateway; no other key
# needed). With no key, the notebook replays what our own run recorded, so it always runs top to bottom.

# %% setup

# %% [markdown]
# **Install the two OpenTelemetry packages** (pinned), then choose live or replay. For live: open Argus, press
# **Notebook key**, and paste the two lines it gives you over the two lines below.

# %%
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "opentelemetry-sdk==1.45.2",
                "opentelemetry-exporter-otlp-proto-http==1.45.2"], check=True)

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run

from ledgerline.course.l6.nbkit import connect, tree, agent_turns
kit = connect(ARGUS_URL, ARGUS_KEY)

# %% [markdown]
# ## 1 · A span, by hand
# A **span** is a record of one piece of work. It needs very little: a name, when it started, when it ended, and which
# piece of work it was part of (its **parent**). Here is a tracer that keeps exactly that, in about fifteen lines.
# `with tracer.span("name"):` starts a span; leaving the `with` block ends it.

# %%
import contextlib, contextvars, secrets, time

_current = contextvars.ContextVar("current span", default=None)   # "which span is running right now?"

class MiniTracer:
    def __init__(self):
        self.spans = []                                            # every finished span, as a plain dict

    @contextlib.contextmanager
    def span(self, name, **attributes):
        parent = _current.get()                                    # whoever is running now becomes my parent
        s = {"name": name, "span_id": secrets.token_hex(4),
             "parent_id": parent["span_id"] if parent else None,
             "trace_id": parent["trace_id"] if parent else secrets.token_hex(8),
             "start": time.time(), "end": None, "attributes": attributes}
        token = _current.set(s)                                    # my children will find me
        try:
            yield s
        finally:
            s["end"] = time.time()
            _current.reset(token)
            self.spans.append(s)

# %% [markdown]
# **Three nested steps.** One turn of an assistant: it handles Emma's message; inside that it asks the model; inside that
# turn it also calls a tool. We fake the work with `time.sleep` so we can look at the records alone.

# %%
tracer = MiniTracer()
with tracer.span("handle Emma's message", user="ECLARKE"):
    with tracer.span("ask the model", model="claude-sonnet-5-5"):
        time.sleep(0.30)
    with tracer.span("call the tool check_stock", item_code="BAT-500"):
        time.sleep(0.05)

for s in tracer.spans:
    print(f"{s['name']:<28} id={s['span_id']}  parent={s['parent_id']}  {1000 * (s['end'] - s['start']):4.0f} ms  {s['attributes']}")

# %% [markdown]
# **Three records.** The two inner spans finished first, so they are listed first. Both have the same `parent`: the id of
# "handle Emma's message". That one link is all we need to draw them as a **tree**. All three share one `trace_id`:
# a **trace** is simply every span with the same trace id, here the whole turn.

# %%
def show_tree(spans, parent=None, depth=0):
    for s in sorted([x for x in spans if x["parent_id"] == parent], key=lambda x: x["start"]):
        print(f"{'    ' * depth}{s['name']:<{34 - 4 * depth}} {1000 * (s['end'] - s['start']):4.0f} ms")
        show_tree(spans, s["span_id"], depth + 1)

show_tree(tracer.spans)
print("\none trace id for all three:", {s["trace_id"] for s in tracer.spans})

# %% [markdown]
# **What our tracer lacks.** It works, but three things are missing before a team could use it:
#
# | Missing | Why it matters | Example |
# |---|---|---|
# | Agreed names | every tool should understand "this span is a model call" | we wrote `ask the model`; the standard says `chat claude-sonnet-5-5` |
# | Somewhere to send it | the spans die with this notebook | a service that keeps them for 30 days |
# | A screen to read it | nobody debugs from a list of dicts | a tree you can click, with costs |
#
# **OpenTelemetry** fixes the first two, and tools like Langfuse, LangSmith and Sentry are the third.

# %% [markdown]
# ## 2 · The same three steps with OpenTelemetry
# OpenTelemetry is an open standard: one way to create spans, one format to send them in. The code has the same shape as
# ours. New here: the **agreed names**. A model call is named `chat <model>`, a tool call `execute_tool <tool>`, the whole
# turn `invoke_agent <agent>`, and facts go in attributes with standard names such as `gen_ai.usage.input_tokens`.

# %%
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

memory = InMemorySpanExporter()                       # an "exporter" decides where finished spans go; this one keeps them here
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(memory))
otel = provider.get_tracer("nb6a")

with otel.start_as_current_span("invoke_agent Ask Northbridge") as turn:
    turn.set_attribute("gen_ai.operation.name", "invoke_agent")
    with otel.start_as_current_span("chat claude-sonnet-5-5") as call:
        call.set_attribute("gen_ai.operation.name", "chat")
        call.set_attribute("gen_ai.usage.input_tokens", 7849)
        time.sleep(0.30)
    with otel.start_as_current_span("execute_tool check_stock") as tool:
        tool.set_attribute("gen_ai.operation.name", "execute_tool")
        tool.set_attribute("gen_ai.tool.call.arguments", '{"item_code": "BAT-500"}')
        time.sleep(0.05)

for s in memory.get_finished_spans():
    print(f"{s.name:<32} parent={'%016x' % s.parent.span_id if s.parent else None}  {dict(s.attributes)}")

# %% [markdown]
# Same three records, now with names any tool can read. To send them to a real service you swap the exporter: one line.
# We do that in part 4.

# %% [markdown]
# ## 3 · A real turn of Ask Northbridge
# Now the real agent: Lecture 5's Ask Northbridge, in a fresh Ledgerline sandbox dated Friday 20 Nov 2026, 09:10. The
# course code wraps its model calls and tool calls in spans exactly as above (`ledgerline/course/l6/tracing.py`).
# We ask one ordinary question and print the reply and the trace.

# %%
turn = kit.run("nb6a_turn.json", lambda: agent_turns(kit, "good", ["How many BAT-500 battery packs do we have?"]))
t = turn["turns"][0]
print("Emma:", t["text"])
print("\nAsk Northbridge:", t["reply"])
print(f"\n{t['tokens_in']:,} tokens in, {t['tokens_out']:,} out, ${t['usd']:.4f}, {t['seconds']} s\n")
print(tree(turn["spans"]))

# %% [markdown]
# **Read the tree.** The first line is the whole turn. Under it, each `chat` line is one call to the model (with the
# tokens it read and what that cost), and each `execute_tool` line is one tool call. The model calls take seconds; the
# Ledgerline tools take milliseconds.
#
# **Open one span.** A tool span carries the exact arguments the model chose and the result Ledgerline gave back.

# %%
import json
tool_span = next(s for s in turn["spans"] if s["name"].startswith("execute_tool"))
a = tool_span["attributes"]
print(tool_span["name"])
print("arguments:", a["gen_ai.tool.call.arguments"])
print("result   :", a["gen_ai.tool.call.result"][:300], "...")

# %% [markdown]
# ### Friday's turn
# Now the incident. Same agent, but with the system prompt someone shortened on Thursday ("be concise: fewer
# confirmations"). Emma's message is the one from Friday.

# %%
friday = kit.run("nb6a_incident.json", lambda: agent_turns(kit, "thursday", ["Order the usual, please, needed by 4 Dec 2026."]))
t = friday["turns"][0]
print("Emma:", t["text"])
print("\nAsk Northbridge:", t["reply"][:500])
print("\nSaved in Ledgerline after this one message:", friday["saved"], "\n")
print(tree(friday["spans"]))

# %% [markdown]
# **Find the span that explains it.** Look for `execute_tool create_purchase_request` with `confirm=True`. If it is
# there, the request was saved in this turn: a turn in which Emma had only asked, and never said yes. (The Thursday
# prompt does not do this every single time; in our 10 recorded runs with this message it did it 10 times.)

# %%
commits = [s for s in friday["spans"] if s["name"] == "execute_tool create_purchase_request"
           and s["attributes"].get("ledgerline.confirm") is True]
for s in commits:
    print(s["name"], "\n  arguments:", s["attributes"]["gen_ai.tool.call.arguments"],
          "\n  result   :", s["attributes"]["gen_ai.tool.call.result"][:160])
print("\nCommitted without a yes in this turn:", bool(commits))

# %% [markdown]
# ## 4 · Send it to a real tool
# The spans above stayed in this notebook. `Tracing.from_env()` adds an exporter for every tool whose key it finds in the
# environment, and skips the rest:
#
# | Tool | Set these | Where the spans go |
# |---|---|---|
# | Langfuse | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` | `{host}/api/public/otel/v1/traces` |
# | LangSmith | `LANGSMITH_API_KEY` | `https://api.smith.langchain.com/otel/v1/traces` |
# | Sentry | `SENTRY_DSN` | the OTLP address inside your DSN |
#
# All three accept the same OpenTelemetry spans. If you have a free account with any of them, set its keys in the cell
# below (with `os.environ[...] = ...`) and run a turn: your trace appears there. With no keys the cell says so and moves on.

# %%
import os
from ledgerline.course.l6 import tracing as T
# os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."; os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."; os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"
# os.environ["LANGSMITH_API_KEY"] = "lsv2_..."
# os.environ["SENTRY_DSN"] = "https://...@o....ingest.sentry.io/..."
print("Tools with keys set here:", T.configured() or "none")
if kit.live and T.configured():
    mine = agent_turns(kit, "good", ["How many BAT-500 battery packs do we have?"])
    print("Sent. Open it:", mine["turns"][0]["links"])
else:
    print("Nothing sent (replay mode, or no tracing keys). In class we open our own trace in each tool.")

# %% [markdown]
# ## 5 · What Langfuse keeps around a trace
# A tracing tool is more than a list of traces. Four things sit around them, and each one is used for **evals** in the
# second half of the lecture. The cell asks our course's Langfuse project for each (in replay: what it answered on
# the day we built the lecture).
#
# - **Sessions**: all the turns of one conversation, together.
# - **Scores**: verdicts attached to a trace ("committed without a yes: true").
# - **Datasets**: traces you saved as test cases, to re-run after every change.
# - **Prompt versions**: every edit of the system prompt, with a label saying which one is in production.

# %%
from ledgerline.course.l6.nbkit import langfuse_tour
have_langfuse = kit.live and all(os.environ.get(k) for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"))
tour = kit.run("nb6a_langfuse_tour.json", langfuse_tour) if have_langfuse else kit.log("nb6a_langfuse_tour.json")
print("SESSIONS:", json.dumps(tour["sessions"], indent=1))

# %% [markdown]
# **Scores.** A score is a name, a value and a comment, attached to one trace. A person can add one in the Langfuse
# screen; a program can add one through the API (that is how an eval writes its verdict next to the trace it judged).

# %%
print(json.dumps(tour["scores"], indent=1)[:900])

# %% [markdown]
# **A dataset.** Two turns we never want to get wrong again, saved with what we expect. After every prompt change we
# re-run the dataset and compare. (The cell above created it through the API; in the Langfuse screen it is one click
# from any trace: "Add to dataset".)

# %%
print(json.dumps(tour["dataset"], indent=1, ensure_ascii=False))

# %% [markdown]
# **Prompt versions.** The system prompt lives in Langfuse with a version number and labels. Thursday's edit is a new
# version; `production` says which one the agent should load. Rolling back is moving a label, not a deploy.

# %%
print(json.dumps(tour["prompt_versions"], indent=1))

# %% [markdown]
# **What to take away**
# - A span is a record of one piece of work; a trace is every span of one turn; the parent link makes it a tree.
# - OpenTelemetry gives the spans agreed names and one format, so the same trace opens in Langfuse, LangSmith or Sentry.
# - Friday's incident is one span: `execute_tool create_purchase_request`, `confirm=True`, in a turn where Emma never said yes.
# - Around the traces sit sessions, scores, datasets and prompt versions: the raw material for evals (NB6b, NB6c).
#
# **Try it yourself**
# 1. Add a fourth step to the hand-built trace (a second tool call). Does the tree still draw correctly?
# 2. In live mode, ask Ask Northbridge something else and find its slowest span.
# 3. From `friday["spans"]`, add up the cost of the turn from the `ledgerline.cost_usd` attribute of each `chat` span.
