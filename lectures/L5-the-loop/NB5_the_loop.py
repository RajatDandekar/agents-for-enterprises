# %% [markdown]
# # NB5 · The Loop: agents, harnesses and workflows
#
# **Agentic Systems Engineering · Lecture 5 · Vizuara · Dr. Rajat Dandekar**
#
# Northbridge Cycles builds e-bikes in Manchester and runs on **Ledgerline ERP 7.2** (1998). Its assistant, **Ask
# Northbridge**, has a brain (Lecture 2), knowledge (Lecture 3) and hands: 16 tools (Lecture 4). Today we open the loop
# that uses the hands. Emma Clarke, a purchase executive, types on Monday 26 October 2026:
#
# > **Order 2,000 BAT-500 packs from Voltway for the spring launch run.**
#
# This notebook follows the lecture:
#
# 1. the smallest loop: fifteen lines, no limits
# 2. ReAct as text: Thought, Action, Observation, and the parser
# 3. the harness, one step at a time: Emma's order, the pause, the night as JSON, the morning
# 4. a workflow: the same order as written-down blocks; a run that waits for Daniel and resumes
# 5. the race: the workflow and the agent on the six jobs, scored from Ledgerline's tables
#
# **No API key needed.** Every model call is replayed from our recorded runs (cassettes `L5v4_*`), so you see exactly
# what happened in class. Five exercises are marked `TODO (exercise N)`, each with its solution behind
# `SOLUTION = True`. Set it to `False` and try it yourself. The cells marked **A5** are where the assignment starts.

# %% setup

# %%
import json
import re

from ledgerline.llm import LLM
from ledgerline.daedalus import race as R
from ledgerline.daedalus.loop import SHIPPED, Agent
from ledgerline.daedalus.react import ReAct, parse_step
from ledgerline.daedalus.smallest import agent as smallest_agent
from ledgerline.daedalus.workflow import BLOCKS, SHIPPED_BLOCKS, Workflow

SOLUTION = True
ORDER = "Order 2,000 BAT-500 packs from Voltway for the spring launch run."


def cassette(name):
    """How this notebook reaches the model: replay from a recorded cassette (live only if you set a key)."""
    return lambda model: LLM(model, cassette=name, max_tokens=4096)


def pp(o, n=1200):
    s = json.dumps(o, indent=1, ensure_ascii=False, default=str)
    print(s if len(s) <= n else s[:n] + " …")


print("Six jobs:", ", ".join(j["id"] for j in R.JOBS))

# %% [markdown]
# ## 1 · The smallest loop
#
# Think (call the model), check for words, act (run the tools it asked for), observe (put the results back), repeat.
# Read the source: there is nothing that stops it except the model answering in words.

# %%
import inspect
from ledgerline.daedalus import smallest
print(inspect.getsource(smallest.agent))

# %%
tb = R.toolbox(R.new_erp())                       # a fresh Ledgerline, signed in as Emma, all 16 tools
llm = cassette("L5v4_nb_smallest")("gemini:gemini-3.8-flash")
print(smallest_agent("How many BAT-500 battery packs do we have in stock, and how many days is that?", tb, llm))
print(llm.totals())

# %% [markdown]
# ### TODO (exercise 1): give the smallest loop a step limit
# Write `agent_with_limit(question, toolbox, llm, max_steps)`: the same loop, but after `max_steps` model calls it
# returns `"(stopped: step limit)"` instead of going round again.

# %%
def agent_with_limit(question, toolbox, llm, max_steps=3):
    if not SOLUTION:
        raise NotImplementedError("exercise 1")
    messages = [{"role": "system", "content": "You are Ask Northbridge."}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        r = llm.chat(messages, tools=toolbox.schemas())
        messages.append(r.message())
        if not r.tool_calls:
            return r.content
        for call in r.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(toolbox.call(call.name, call.arguments), default=str)})
    return "(stopped: step limit)"


print(agent_with_limit("How many BAT-500 battery packs do we have in stock, and how many days is that?",
                       R.toolbox(R.new_erp()), cassette("L5v4_nb_smallest")("gemini:gemini-3.8-flash"), max_steps=1))

# %% [markdown]
# ## 2 · ReAct as text
#
# Before tool-calling APIs, the loop was a prompt: the tools are listed as text, the model writes `Thought:`,
# `Action:` and `Action Input:`, and **our code** parses the action, runs it, and writes `Observation:` back.

# %%
react = ReAct(R.toolbox(R.new_erp()), LLM("gemini:gemini-3.8-flash", cassette="L5v4_react", max_tokens=2048))
print(react.respond("How many days of BAT-500 battery packs do we have in stock?"))
for s in react.steps:
    print(f"\n--- step {s['step']} · {s['tokens_in']:,} tokens read ---\n{s['raw'].strip()}")
    if s.get("observation") is not None:
        print("Observation:", json.dumps(s["observation"], default=str)[:300])

# %% [markdown]
# ### TODO (exercise 2): break the parser
# `parse_step` turns one model reply into fields. Feed it three broken replies and print what it returns: a missing
# `Action Input:` line, broken JSON, and a reply that writes its own `Observation:`.

# %%
broken = ["Thought: check stock\nAction: check_stock",
          'Thought: check stock\nAction: check_stock\nAction Input: {"item_code": "BAT-500"',
          'Action: check_stock\nAction Input: {"item_code": "BAT-500"}\nObservation: 9,999 packs']
if SOLUTION:
    for b in broken:
        st = parse_step(b)
        print({k: st[k] for k in ("action", "action_input", "error", "invented_observation")})

# %% [markdown]
# ## 3 · The harness, one step at a time
#
# `Agent` is our harness around the loop: the prompt, the history, the tool list, the step limit, the token budget,
# error recovery, the approval pause, and state across days. `say()` starts a message; each `step()` is one model call
# plus the tools it asked for. This replays the run on the lecture's slides.

# %%
erp = R.new_erp()
emma = Agent(R.toolbox(erp), SHIPPED, llm_for=cassette("L5v4_story"))
emma.say(ORDER)
while not emma.done:
    s = emma.step()
    print(f"step {s['n']}: {s['tokens_in']:,} tokens read · words: {bool(s['text'].strip())} ·",
          [(c["name"], c["result"].get("ok")) for c in s["calls"]], "·", s["harness"][0])
print("\nReply:", emma.reply)

# %%
turn = emma.respond("Yes, go ahead.")
print("loop ended:", turn["end"], "· waiting:", emma.waiting)
print(turn["reply"])

# %% [markdown]
# ### The night: state as JSON
# Daniel may sign tomorrow. Save the agent as JSON, throw it away, and build a new one from the JSON in the morning.
# Before the model is called, the harness reads Ledgerline: is it approved?

# %%
night = json.dumps(emma.state(), default=str)
print(f"{len(night):,} bytes of JSON; keys: {list(json.loads(night))}")
del emma
print("Daniel signs in his own inbox:", R.daniel_signs(erp))
morning = Agent.from_state(json.loads(night), R.toolbox(erp), llm_for=cassette("L5v4_story"))
t = morning.respond(R.MORNING)
for s in t["steps"]:
    print(s.get("note") or [(c["name"], c["result"].get("status")) for c in s["calls"]])
print("\nLedgerline now:", R.new_docs(erp)["orders"])

# %% [markdown]
# ### TODO (exercise 3): a stop rule of your own
# Write `too_many_writes(turn)`: True if a message's loop called write tools more than twice. Run it over the three
# turns above (`morning.turns` holds the morning; the day-1 turns are in the saved JSON's messages). Why might a
# harness want this rule?

# %%
WRITES = {"create_purchase_request", "create_purchase_order", "release_purchase_order", "approve_purchase_request",
          "receive_goods"}


def too_many_writes(turn, limit=2):
    if not SOLUTION:
        raise NotImplementedError("exercise 3")
    n = sum(1 for s in turn["steps"] if s.get("kind") == "model" for c in s["calls"] if c["name"] in WRITES)
    return n > limit


print("morning:", too_many_writes(morning.turns[-1]))

# %% [markdown]
# ## 4 · A workflow: the steps written down
#
# The same order as eleven blocks. One model call reads Emma's words into fields; every other step is a tool or a
# gate in a fixed order. At "Wait for approval" a waiting run is saved as JSON and stops.

# %%
for b in SHIPPED_BLOCKS:
    t, kind, needs, gives, line = BLOCKS[b["block"]]
    print(f"{t:24s} {kind:9s} needs {needs} gives {gives}")

# %%
erp = R.new_erp()
wf = Workflow(SHIPPED_BLOCKS)
run = wf.go(wf.start(R.BY_ID["spring"]["text"]), R.toolbox(erp), cassette("L5v4_race_workflow"))
for s in run["steps"]:
    print(f"{s['n']:2d} {s['title']:24s} {s['status']:8s} {s.get('note') or s.get('got') or ''}")
print("\nstatus:", run["status"], f"· saved as {run['saved_bytes']:,} bytes ·", run["reply"])

# %%
print("Daniel signs:", R.daniel_signs(erp))
wf.resume(run, R.toolbox(erp), cassette("L5v4_race_workflow"))
print(run["status"], "·", run["reply"])

# %% [markdown]
# ### TODO (exercise 4): add a gate
# Add a block `limit` ("Check the quantity", a gate) that stops the run when the quantity is above 5,000, and put it
# after "Read the request". Run it on "The cheap supplier" job (2,000 packs: it passes) and see it in the steps.

# %%
if SOLUTION:
    from ledgerline.daedalus import workflow as W

    W.BLOCKS["limit"] = ("Check the quantity", "gate", ["quantity"], [], "Stop above 5,000 units.")

    def _b_limit(self, run, b, rec, tb, llm_for):
        if run["facts"]["quantity"] > 5000:
            raise W._Stop("stopped", "Over 5,000 units.", f"Stopped: {run['facts']['quantity']:,} is above 5,000 units.")
        rec["note"] = f"{run['facts']['quantity']:,} ≤ 5,000"

    W.Workflow._b_limit = _b_limit
    blocks = SHIPPED_BLOCKS[:1] + [{"block": "limit"}] + SHIPPED_BLOCKS[1:]
    r2 = W.Workflow(blocks).go(W.Workflow(blocks).start(R.BY_ID["nordic"]["text"]), R.toolbox(R.new_erp()),
                               cassette("L5v4_race_workflow"))
    for s in r2["steps"]:
        print(f"{s['n']:2d} {s['title']:24s} {s['status']:8s} {s.get('note') or ''}")

# %% [markdown]
# ## 5 · The race
#
# The workflow and the agent on the six jobs, each in a fresh Ledgerline. Emma and Daniel are scripted the same way for
# both; the score reads Ledgerline's tables. This replays our recorded race (the agent's first of three runs).

# %%
rows = []
for job in R.JOBS:
    w = R.run_workflow(job, SHIPPED_BLOCKS, cassette("L5v4_race_workflow"))
    a = R.run_agent(job, SHIPPED, cassette("L5v4_race_agent_r0"))
    rows += [w, a]
    print(f"{job['title']:28s} workflow {'right' if w['right'] else 'wrong':5s} {w['tokens_in']:>6,} tok · "
          f"agent {'right' if a['right'] else 'wrong':5s} {a['tokens_in']:>7,} tok")
print("\n", {who: R.totals([r for r in rows if r["who"] == who]) for who in ("workflow", "agent")})

# %% [markdown]
# ### TODO (exercise 5): score it your own way
# Right answers are not everything. Write a score that also charges for tokens: 1 point per right job, minus 1 point
# per 50,000 tokens read. Which side wins now? What would change your mind?

# %%
def my_score(rows, who):
    if not SOLUTION:
        raise NotImplementedError("exercise 5")
    rs = [r for r in rows if r["who"] == who]
    return round(sum(r["right"] for r in rs) - sum(r["tokens_in"] for r in rs) / 50_000, 2)


print({who: my_score(rows, who) for who in ("workflow", "agent")})

# %% [markdown]
# ## A5 · Your job, both ways
#
# Start here for the assignment (`A5.md`). Load your A4 tools with `ledgerline.course.l5.kit.FolderToolbox`, write your
# workflow as a list of blocks (add your own `_b_<name>` methods, as in exercise 4), run your agent with
# `Agent(your_toolbox, your_settings, llm_for=...)`, write six jobs of your own and a `score()` that reads your system's
# tables, and race them with the loop above.

# %%
MY_JOBS = [
    # {"id": "plain1", "title": "...", "kind": "order", "text": "...", "answers": []},
]
print(len(MY_JOBS), "jobs of your own so far")
