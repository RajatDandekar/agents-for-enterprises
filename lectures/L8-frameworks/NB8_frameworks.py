# %% [markdown]
# # NB8 · Agent Frameworks in Industry
# **AI Agents for Enterprises · Lecture 8 · Sun 22 Nov 2026**
#
# In Lecture 5 you built Ask Rasoi's loop by hand: `bahi/course/l5/harness.py`. Rasoi's IT team now asks the fair question: *why our own loop, when companies use LangGraph, the OpenAI Agents SDK or Google's ADK?*
#
# Today you run **the same Ask Rasoi** on each framework and measure them, like for like:
#
# 1. The rig: the Lecture 4 toolbox over MCP (HTTP), and a small **meter**, a model gateway on localhost that every framework talks to
# 2. Our harness, as the baseline
# 3. The **OpenAI Agents SDK**: Agent, Runner, MCP tools, sessions, tracing
# 4. **Google ADK**: LlmAgent, Runner, Events, and what it puts on the wire
# 5. **LangGraph**: the free loop as a two-node graph
# 6. The scoreboard from our full run: 12 tasks × 7 setups
# 7. Guardrails and handoffs
# 8. Model gateways (LiteLLM Router, one API for many models) and a local model (Ollama)
# 9. Your module
#
# **Replay.** With no key, every framework still runs for real: the SDK code, the MCP calls and Bahi all execute. Only the model's replies are played back, by the meter, from our recording of 28 Oct 2026 (cassettes `IND8_*`). If you change a prompt there is no recording for it; set `OPENROUTER_API_KEY` in the setup cell to run live (about ₹2 per task).

# %% setup

# %%
# The framework SDKs, pinned to the versions the lecture was built and measured with (28 Oct 2026).
# openai-agents 0.21+ needs openai 3.x while LiteLLM still needs openai < 3, so we pin 0.20.0: one environment for all.
import importlib, subprocess, sys
PINS = ["openai-agents==0.20.0", "google-adk==2.11.0", "litellm==1.104.2", "langgraph==1.2.15",
        "langchain-openai==1.7.1", "langchain-mcp-adapters==0.3.2",
        "fastmcp==3.4.11", "mcp==1.30.0"]          # the SDKs above need mcp < 2; fastmcp 4 needs mcp 2
def _have(mod, ver_pkg, ver):
    try:
        import importlib.metadata as md
        importlib.import_module(mod)
        return md.version(ver_pkg) == ver
    except Exception:
        return False
if not all(_have(m, p.split("==")[0], p.split("==")[1]) for m, p in zip(
        ["agents", "google.adk", "litellm", "langgraph", "langchain_openai", "langchain_mcp_adapters", "fastmcp", "mcp"],
        PINS)):
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *PINS], capture_output=True, text=True)
    print("pip install:", "ok" if r.returncode == 0 else r.stderr[-2000:])   # pip may warn about unrelated packages
import importlib.metadata as md
print({p.split("==")[0]: md.version(p.split("==")[0]) for p in PINS})

# %%
import json, os, re, textwrap, warnings, logging
warnings.filterwarnings("ignore")
logging.getLogger("google_adk").setLevel(logging.ERROR)
import pandas as pd
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox
from bahi.course.l5.tasks import BY_ID, run_task
from bahi.course.frameworks.meter import Meter
from bahi.course.frameworks import fixtures as FX
import bahi.course.frameworks.base as base
CREATED = []                                # every framework port the notebook makes, so we can read its own trace
base.ON_CREATE.append(CREATED.append)
import tempfile
WORK = tempfile.mkdtemp()
MODEL = "google/gemini-3.8-flash"          # the same model for every framework, through OpenRouter
def show(x, n=700):
    print(textwrap.shorten(json.dumps(x, default=str, ensure_ascii=False), n, placeholder=" ..."))
def turns(r, n=260):
    for t in r["turns"]:
        print(f"[{t['who']} day {t['day']} · {t['kind']}] {t['user'][:120]}\n   Ask Rasoi: {(t['agent'] or '')[:n]}")
T04 = BY_ID["T04"]                          # "Order 3,000 standard whistles from Sahyadri Valves, PRD-07 ..."
print(T04.beats[0].text)

# %% [markdown]
# ## 1 · The rig
# Two pieces sit under every framework, so they are compared like for like.
#
# **The toolbox over MCP.** `serve_toolbox(erp, user)` starts the Lecture 4 toolbox as an MCP server on streamable HTTP, bound to one person's Bahi session. Every framework connects to its URL the way it would connect to any remote MCP server.
#
# **The meter.** Every framework speaks the OpenAI chat-completions API to *some* model. We point them all at `Meter`, a tiny model gateway on localhost. It forwards each request to the model (through OpenRouter), records the reply, and logs tokens, seconds and the rupees OpenRouter billed. In replay it answers from the recording. One gateway, one way of counting, for everyone.

# %%
from bahi.course.frameworks.mcp_http import serve_toolbox
from bahi.mcp_server import MCPClient
erp = ERP()
srv = serve_toolbox(erp, "KJOSHI")
print("MCP server:", srv.url)
c = MCPClient(srv.url)
tools = c.list_tools()                                  # tools/list over HTTP, as any framework does it
print(len(tools), "tools:", ", ".join(t.name for t in tools))
print(MCPClient.text(c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"}))[:300])
c.close()

# %% [markdown]
# ## 2 · Our harness, the baseline
# Lecture 5's `Harness` with every part on, its tools now over MCP. `run_task` plays Kavita (and Rohit, and Neha), then checks Bahi's tables in code: pass or fail, and the never-events NE1–NE5.

# %%
from bahi.course.frameworks.ours import harness_port
r_ours = run_task(lambda tb: harness_port(tb, cassette="IND8_fw_ours"), T04)
print("PASS" if r_ours["passed"] else "FAIL", r_ours["note"], "· model calls", r_ours["model_calls"],
      "· tokens", r_ours["tokens_in"] + r_ours["tokens_out"], "· replayed", r_ours["replayed"])
turns(r_ours)

# %% [markdown]
# ## 3 · The OpenAI Agents SDK
# OpenAI's open-source framework for agents. It runs with any model that speaks chat completions; we give it OpenRouter's URL (here, the meter's). Five names to learn, each one a piece you built by hand:
#
# | Agents SDK | What you built in Lecture 5 |
# |---|---|
# | `Agent(instructions, tools, mcp_servers, model)` | the system prompt + the tool registry |
# | `Runner.run(agent, text, max_turns=12)` | the loop, with its step cap |
# | `MCPServerStreamableHttp(url)` | the toolbox, discovered with `tools/list` |
# | `SQLiteSession` | the history across messages and days (`save()` / `load()`) |
# | tracing: spans | the trace list |
#
# The whole port is the `# --- port ---` section of `bahi/course/frameworks/openai_agents.py`: 19 lines of code.

# %%
import inspect
from bahi.course.frameworks import openai_agents as oa
src = inspect.getsource(oa)
print(src[src.index("# --- port"):src.index("# --- end port")])

# %%
meter = Meter(cassette="IND8_fw_openai_agents").start()
def agents_sdk(tb, cap=12):
    tag = f"openai_agents-T04-{tb.user}"
    return oa.AgentsSDKPort(tb, meter, tag, model=MODEL, max_steps=cap, session_db=f"{WORK}/{tag}.db")
r_oa = run_task(agents_sdk, T04)
print("PASS" if r_oa["passed"] else "FAIL", r_oa["note"], "· model calls", r_oa["model_calls"],
      "· replayed", r_oa["replayed"])
turns(r_oa)

# %% [markdown]
# **Tracing.** The SDK records a span for every agent run, model call (`generation`), tool call (`function`) and MCP `tools/list`. By default it exports them to OpenAI's dashboard; we have no OpenAI key, so `SpanRecorder` (a `TracingProcessor`) keeps them in memory. Lecture 10 sends the same spans to Langfuse.

# %%
spans = oa.RECORDER.spans.get("openai_agents-T04-KJOSHI", [])
print(len(spans), "spans for Kavita's two messages")
for s in spans[:16]:
    print(f"  {s['type']:<11} {s.get('name') or '':<24} {('in: ' + s['input'][:70]) if s.get('input') else ''}")

# %% [markdown]
# **Sessions.** The history lives in the session, not in your code. A `SQLiteSession` on a file survives the night: a new object on day 2 reads the same rows.

# %%
from agents import SQLiteSession
from bahi.course.frameworks.base import LoopThread
lt = LoopThread()
day2 = SQLiteSession("KJOSHI-thread", f"{WORK}/openai_agents-T04-KJOSHI.db")   # a brand-new object, the same file
items = lt.run(day2.get_items())
print(len(items), "items in Kavita's session file:")
for it in items[:12]:
    kind = it.get("type") or it.get("role")
    print("  ", kind, "·", (it.get("name") or str(it.get("content") or it.get("arguments") or "")[:80]))

# %% [markdown]
# ### TODO (exercise 1): the step cap
# `max_turns` is the SDK's name for our harness's step cap. Kavita's first message took 3 model calls (look-ups, the preview, the reply). Run it with a cap of 2 and look at what happened: which tools ran before the stop, what did Kavita see, and did Bahi get an order? This runs in replay: the first two model calls are the same requests as before.

# %%
SOLUTION = True
MY_CAP = 2 if SOLUTION else None            # TODO (exercise 1): set the cap
if MY_CAP:
    r_cap = run_task(lambda tb: oa.AgentsSDKPort(tb, meter, f"openai_agents-T04cap-{tb.user}", model=MODEL,
                                                 max_steps=MY_CAP), T04)
    print("PASS" if r_cap["passed"] else "FAIL", "· model calls", r_cap["model_calls"])
    print("tools that ran:", [t["name"] for tr in r_cap["traces"].values() for t in tr if t.get("kind") == "tool"])
    turns(r_cap)
    print("orders in Bahi:", r_cap["orders"])

# %% [markdown]
# ## 4 · Google ADK
# Google's open-source Agent Development Kit. It is built around Gemini and Google Cloud, but any model works through LiteLLM. In production you would write `LiteLlm(model="openrouter/google/gemini-3.8-flash")`; here the model string is `openai/...` with `api_base` set to the meter.
#
# | ADK | What you built |
# |---|---|
# | `LlmAgent(instruction, tools, model)` | the system prompt + the registry |
# | `Runner.run_async` yielding **Events** | the loop, and its trace |
# | `McpToolset` | the toolbox over MCP |
# | `SessionService` | the history |
# | `RunConfig(max_llm_calls=12)` | the step cap |
# | callbacks (`before_model`, `before_tool`) | where a harness part goes |

# %%
from bahi.course.frameworks import adk as adkp
meter_adk = Meter(cassette="IND8_fw_adk").start()
r_adk = run_task(lambda tb: adkp.ADKPort(tb, meter_adk, f"adk-T04-{tb.user}", model=MODEL), T04)
print("PASS" if r_adk["passed"] else "FAIL", r_adk["note"], "· model calls", r_adk["model_calls"],
      "· tokens", r_adk["tokens_in"] + r_adk["tokens_out"])
adk_port = [p for p in CREATED if p.framework == "adk" and p.tb.user == "KJOSHI"][-1]
print("ADK events on Kavita's first message:")
for ev in adk_port.native[0]["events"]:
    print("  ", ev["author"], "· calls", [c["name"] for c in ev.get("calls", [])], "· results",
          [x["name"] for x in ev.get("responses", [])], "·", (ev.get("text") or "")[:60])
first = meter_adk.first["adk-T04-KJOSHI"]
print("ADK's first request:", len(first["messages"]), "messages,", len(first["tools"]), "tools,",
      len(json.dumps(first["tools"])), "bytes of tool schemas")

# %% [markdown]
# ### TODO (exercise 2): what does ADK add to the prompt?
# Compare the system message ADK sent with the one the Agents SDK sent for the same task (both are in the meters' `first` requests). Print only the text ADK added. Then compare one tool's schema (`create_purchase_order`) as each framework sent it. Which one costs more tokens on every single model call, and why?

# %%
import difflib
sys_oa = next(m["content"] for m in meter.first["openai_agents-T04-KJOSHI"]["messages"] if m["role"] == "system")
sys_adk = next(m["content"] for m in first["messages"] if m["role"] == "system")
SOLUTION = True
if SOLUTION:                                 # TODO (exercise 2)
    added = [l[2:] for l in difflib.ndiff(sys_oa.splitlines(), sys_adk.splitlines()) if l.startswith("+ ")]
    print("ADK added", len(sys_adk) - len(sys_oa), "characters:\n", "\n".join(added))
    po = lambda reqs: next(t for t in reqs["tools"] if t["function"]["name"] == "create_purchase_order")
    print("\ncreate_purchase_order schema bytes · Agents SDK:", len(json.dumps(po(meter.first["openai_agents-T04-KJOSHI"]))),
          "· ADK:", len(json.dumps(po(first))))

# %% [markdown]
# ## 5 · LangGraph
# You built a LangGraph **control graph** in Lecture 5 (spine and gates). LangGraph also ships the free loop as a prebuilt two-node graph: node `agent` (the model) and node `tools` (run the calls), with an edge back until the model answers in words. Tools come from MCP through `langchain-mcp-adapters`; the history is a **checkpointer** keyed by `thread_id`.

# %%
from bahi.course.frameworks import langgraph_react as lgp
meter_lg = Meter(cassette="IND8_fw_langgraph").start()
r_lg = run_task(lambda tb: lgp.LangGraphPort(tb, meter_lg, f"langgraph-T04-{tb.user}", model=MODEL), T04)
print("PASS" if r_lg["passed"] else "FAIL", r_lg["note"], "· model calls", r_lg["model_calls"])
lg_port = [p for p in CREATED if p.framework == "langgraph" and p.tb.user == "KJOSHI"][-1]
print("graph steps on Kavita's first message:")
for st in lg_port.native[0]["steps"]:
    print("  node", st["node"], "·", [c["name"] for c in st.get("calls", [])] or (st.get("text") or "")[:70])

# %% [markdown]
# ## 6 · The same four, side by side
# The four ports in this notebook used the same toolbox, model, prompt and step cap. Here is the tool sequence each one ran on Kavita's whistle order, read from the MCP server's side, so it is counted the same way for all.

# %%
def tool_seq(r):
    return [t["name"] for tr in r["traces"].values() for t in tr if t.get("kind") == "tool"]
side = {"our harness": r_ours, "Agents SDK": r_oa, "ADK": r_adk, "LangGraph": r_lg}
for k, r in side.items():
    print(f"{k:<12} {r['model_calls']:>2} model calls · {' > '.join(tool_seq(r))}")

# %% [markdown]
# ### The full run: 12 tasks × 7 setups
# The notebook ran one task each. Our experiment (`lectures/L8-frameworks/experiments/exp_frameworks.py`) ran all twelve Lecture 5 tasks on every setup, once each, on 28 Oct 2026. The results ship with the course as fixtures.

# %%
board = pd.DataFrame(FX.scoreboard()).set_index("setup")
board

# %%
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(13, 3.2))
for a, col, lab in zip(ax, ["passed", "tokens_in", "cost_inr"], ["tasks passed (of 12)", "input tokens, 12 tasks",
                                                                  "₹ billed, 12 tasks"]):
    board[col].plot.barh(ax=a, color="#2a78d6"); a.set_title(lab, fontsize=10); a.invert_yaxis()
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7 · Guardrails and handoffs
# A **guardrail** is a check that runs beside the agent and can stop it. The Agents SDK has three kinds: on the user's input, on the agent's final output, and on a tool call. Our harness parts map onto them: *verify* is an output guardrail, the food-grade gate is a tool guardrail. The check itself is plain code that reads Bahi:

# %%
from bahi.course.frameworks.desks import food_grade_problem
e2 = ERP()
print("Deccan Polymers:", food_grade_problem(e2, {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "confirm": True}))
print("Kaveri Rubber:  ", food_grade_problem(e2, {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L", "confirm": True}))
print("Preview only:   ", food_grade_problem(e2, {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L", "confirm": False}))

# %% [markdown]
# ### TODO (exercise 3): write a guardrail check
# Rohit's approval limit is ₹10,00,000. Write `big_order_problem(erp, args)` for `create_purchase_order`: when `confirm` is true and quantity × contract rate × 1.18 is above ₹10,00,000, return a message that says why and what to do next; otherwise `None`. The contract rate is in `sup_rate` (`sup_cd`, `itm_cd`, `rate`). Test it on the three orders below.

# %%
from bahi.course.l5.harness import inr      # ₹ with Indian digit grouping
SOLUTION = True
def big_order_problem(erp, args):
    if not SOLUTION:
        return None                                  # TODO (exercise 3)
    if not args.get("confirm") or not args.get("quantity"):
        return None
    r = erp.q("SELECT rate FROM sup_rate WHERE sup_cd=? AND itm_cd=? ORDER BY valid_from DESC",
              args.get("supplier_code", ""), args.get("item_code", ""))
    rate = args.get("rate") or (r[0]["rate"] if r else 0)
    gross = args["quantity"] * rate * 1.18
    if gross > 10_00_000:
        return (f"Blocked: this order is worth about {inr(gross)} with GST, above Rohit's ₹10,00,000 limit. "
                "Raise a purchase request instead, so Anand Patil can approve it.")
    return None
for q in (20_000, 70_000, 1_00_000):
    print(q, "->", big_order_problem(e2, {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L",
                                          "quantity": q, "confirm": True}))

# %% [markdown]
# **Measured.** We ran the 12 tasks again with two guardrails on the Agents SDK: the food-grade tool guardrail and a verify output guardrail.

# %%
g = FX.load("guarded")
print(g["summary_line"])
for row in g["trips"]:
    print(" ", row)

# %% [markdown]
# **Handoffs.** A handoff passes the conversation to another agent. Ask Rasoi's front desk has no tools; it hands each message to the policy, purchasing or stores desk, each of which sees only its own tools (an MCP tool filter). The input guardrail stops a message that asks Ask Rasoi to approve for Rohit. Our recorded run:

# %%
for m in FX.load("desks")["agents_sdk"]:
    print(f"[{m['who']}] {m['message'][:90]}\n   -> {m['answered_by'] or 'stopped'}: {m['reply'][:160]}")

# %% [markdown]
# ## 8 · Model gateways and a local model
# A **model gateway** is one API in front of many models: you change a string, not your code; it can fall back to a second model when the first fails, and it logs the cost of every call. OpenRouter is a hosted gateway. LiteLLM is a library (and a proxy server) you run yourself. Here is LiteLLM's Router, with a fallback, replayed through the meter:

# %%
import litellm
from litellm import Router
litellm.suppress_debug_info = True
gm = Meter(cassette="IND8_gateway").start()
KEY = os.environ.get("OPENROUTER_API_KEY", "replay")
router = Router(model_list=[
    {"model_name": "rasoi-brain", "litellm_params": {"model": "openai/google/gemini-3.8-flash",
                                                     "api_base": gm.base_url("router"), "api_key": KEY}},
    {"model_name": "rasoi-backup", "litellm_params": {"model": "openai/google/gemini-3.5-flash-lite",
                                                      "api_base": gm.base_url("router"), "api_key": KEY}}],
    fallbacks=[{"rasoi-brain": ["rasoi-backup"]}], num_retries=0)
Q = FX.load("gateway_question")
for label, kw in [("normal", {}), ("primary fails", {"mock_testing_fallbacks": True})]:
    r = router.completion(model="rasoi-brain", messages=Q, temperature=0, **kw)
    print(f"{label:<14} answered by {gm.log[-1]['model']}: {r.choices[0].message.content[:120]}")

# %% [markdown]
# ### TODO (exercise 4): what would 1,000 orders a month cost?
# From the full run, compute ₹ per task for each setup, then the cost of 1,000 such tasks a month. Then do the same for the four models in the gateway test (one question each). Which line of the bill is the framework, and which is the model?

# %%
SOLUTION = True
if SOLUTION:                                          # TODO (exercise 4)
    b = board.copy()
    b["₹ per task"] = (b["cost_inr"] / b["tasks"]).round(2)
    b["₹ per 1,000 tasks"] = (b["₹ per task"] * 1000).round(0)
    print(b[["₹ per task", "₹ per 1,000 tasks"]])
    print(pd.DataFrame(FX.load("gateway")["models"])[["model", "tokens_in", "tokens_out", "cost_inr", "seconds", "correct"]])

# %% [markdown]
# **A local model.** Some companies may not send supplier prices or people's data to a model API at all. Ollama runs open-weight models on your own machine behind the same OpenAI-compatible API (`http://localhost:11434/v1`). We ran our harness with Ollama on a Modal L4 GPU, no API key in the container, on the same 12 tasks:

# %%
pd.DataFrame(FX.load("ollama"))

# %% [markdown]
# To run it yourself on a machine with a GPU (not on free Colab's CPU):
# ```
# ollama serve & ollama pull qwen3.5:9b
# harness_port(tb, cassette="mine", model="ollama:qwen3.5:9b")
# ```

# %% [markdown]
# ## 9 · Your module (A8)
# A8 asks you to port **your module's agent** to two frameworks and write a one-page decision memo for a CTO, with numbers from your own runs. The ports take any toolbox: `FolderToolbox` (from A4) is served over MCP the same way.

# %%
from bahi.course.l5.kit import FolderToolbox
RUN_LIVE = False                       # set True with your OPENROUTER_API_KEY, and your own module folder
if RUN_LIVE:
    my_tb = FolderToolbox("my_module/tools", ERP(modules=["hr_leave"]), "KJOSHI")
    my_meter = Meter(cassette="A8_mine").start()
    a = oa.AgentsSDKPort(my_tb, my_meter, "a8-mine", model=MODEL)
    print(a.respond("I need Thursday and Friday off for my sister's wedding."))
    print(my_meter.records("a8-mine"))
else:
    print("Set RUN_LIVE = True to port your module. The scoreboard above is the shape your memo's table should take.")
