# %% [markdown]
# # NB5 · The Loop: What Makes It an Agent
# **AI Agents for Enterprises · Lecture 5 · Sat 14 Nov 2026**
#
# In Lecture 4 Ask Rasoi got hands: the toolbox, 15 tools, one per business activity. But it ran **one tool round per message**, so Kavita had to drive every step herself: "now raise the request", "now make the order", "now release it".
#
# Today you build the piece that drives the steps: **the loop**, and the **harness** around it.
#
# 1. An agent in one sentence, and the smallest loop
# 2. ReAct from scratch: the model writes *Thought / Action / Action Input*; your code parses it, runs the tool and writes the *Observation*
# 3. Native tool calling: the same loop, done by the API (the tool message **is** the observation)
# 4. The harness, one part at a time: stop rules, budget, error recovery, state across turns
# 5. A tiny control graph in LangGraph, for when the process must be followed
# 6. An approval as a pause: state saved, resumed only when Bahi says APPROVED
# 7. The scorecard, and your module
#
# Everything runs in **replay** with no API key: model replies come from our recorded run (cassettes `L5v3_*`). If you change a prompt, there is no recording for it; set a key in the setup cell to run live.

# %% setup

# %%
import json, re, textwrap, tempfile, pathlib
WORK = pathlib.Path(tempfile.mkdtemp())   # scratch files (saved threads, a toy module) go here
import pandas as pd
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox
from bahi.llm import LLM
MODEL = "gemini:gemini-3.8-flash"   # the course default; recorded on 28 Oct 2026 (bahi.llm routed it through OpenRouter)
GASKET = ("Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract rate. "
          "Charge it to cost centre PRD-07, need-by 9 November.")
def show(x, n=900):
    print(textwrap.shorten(json.dumps(x, default=str, ensure_ascii=False), n, placeholder=" ..."))
tb = Toolbox(ERP(), "KJOSHI")          # Kavita's own Bahi session: her permissions, nobody else's
print(len(tb.names), "tools:", ", ".join(tb.names))

# %% [markdown]
# ## 1 · What an agent is
# **An agent is a model, a set of tools, a loop, and state.** The model reads everything so far and decides the next step; the tools act on Bahi; the loop runs the tool, hands the result back and asks again; the state is everything said and observed, kept between steps (and, later today, between days).
#
# A **chatbot** has only the model: one message in, one reply out. A **workflow** has tools and a loop, but the path is fixed in code. An **agent** lets the model pick the next step.
#
# The smallest loop, in plain Python, with a fake "model" that is just a list of steps, so you can see the shape before any LLM is involved:

# %%
fake_model = [("check_stock", {"item_code": "GSK-SIL-05L"}), ("search_policy", {"question": "food-grade certificate rule"}), None]
state = []                                    # everything observed so far
for step in fake_model:                       # the loop
    if step is None:                          # the "model" decides it is done
        break
    name, args = step                         # the "model" picks a tool
    result = tb.call(name, args)              # the tool acts on Bahi
    state.append((name, result))              # the observation goes back into the state
for name, r in state:
    print(name, "->", textwrap.shorten(json.dumps(r, ensure_ascii=False), 160))

# %% [markdown]
# ## 2 · ReAct from scratch, in text
# **ReAct** = *Reason, then Act, then Observe*, repeated. The model writes its reasoning as a `Thought:`, names one tool in `Action:` and its arguments in `Action Input:`. Then it stops. **Your code** reads those lines, runs the tool, and writes `Observation:` with the result. Repeat until the model writes `Final Answer:`.
#
# No tool-calling API is used here: the model only produces text. The tools are described in the prompt.
#
# ### Exercise 1 · describe the tools in one line each
# Write `tool_lines(tb)`: one line per tool, `- name(arg: type, optional_arg?: type): description`. Required arguments have no `?`.

# %%
# TODO (exercise 1)
def tool_lines(tb) -> str:
    out = []
    for s in tb.schemas():
        f = s["function"]
        # --- solution (replace with your own) ---
        req = set(f["parameters"].get("required", []))
        args = ", ".join(f"{k}{'' if k in req else '?'}: {v.get('type', 'string')}"
                         for k, v in f["parameters"].get("properties", {}).items())
        out.append(f"- {f['name']}({args}): {f['description']}")
    return "\n".join(out)

from bahi.course.l5.react import tool_lines as reference_tool_lines, PROMPT
assert tool_lines(tb) == reference_tool_lines(tb), "not the same text as the recorded prompt"
print(tool_lines(tb)[:700], "...")

# %% [markdown]
# The whole prompt. Read it once: it is the format, the tools and the rules of the job.

# %%
from bahi.course.l5.harness import profile
u = tb.erp.user("KJOSHI")
react_prompt = PROMPT.format(name=u["name"], user="KJOSHI", role="purchase executive", first="Kavita",
                             tools=tool_lines(tb), profile=profile(tb))
print(react_prompt[:600], "\n ... [tool list] ...\n", react_prompt[-900:])

# %% [markdown]
# ### Exercise 2 · parse one step
# The model's turn is plain text. Pull out the `Action` name and the `Action Input` JSON, or the `Final Answer`. One trap: models sometimes keep going and **write their own `Observation:`**, inventing a result. Cut the text at `Observation:` before parsing.

# %%
# TODO (exercise 2)
def parse(text: str) -> dict:
    # --- solution (replace with your own) ---
    text = re.split(r"^\s*Observation\s*:", text or "", flags=re.M)[0]
    final = re.search(r"^\s*Final Answer\s*:\s*(.*)", text, re.M | re.S)
    action = re.search(r"^\s*Action\s*:\s*`?(\w+)`?", text, re.M)
    if action and (not final or action.start() < final.start()):
        rest = text[action.end():]
        i = rest.find("{")
        args, _ = json.JSONDecoder().raw_decode(rest[i:]) if i >= 0 else ({}, 0)
        return {"action": action.group(1), "input": args}
    if final:
        return {"final": final.group(1).strip()}
    return {"error": "no Action and no Final Answer"}

sample = ('Thought: Kavita wants the stock first.\nAction: check_stock\nAction Input: {"item_code": "GSK-SIL-05L"}\n'
          'Observation: {"on_hand": 999999}')   # the invented observation must be ignored
print(parse(sample))
assert parse(sample) == {"action": "check_stock", "input": {"item_code": "GSK-SIL-05L"}}
assert parse("Thought: done.\nFinal Answer: 66,000 free, 11 days.") == {"final": "66,000 free, 11 days."}

# %% [markdown]
# ### The loop, written out
# Ask the model; parse; run the tool; append the observation; ask again. `stop=["\nObservation:"]` tells the API to stop writing at that word, so the model cannot invent the result.

# %%
def react(question, tb, llm, max_steps=10, messages=None):
    messages = messages or [{"role": "system", "content": react_prompt}]
    messages.append({"role": "user", "content": question})
    for n in range(max_steps):
        r = llm.chat(messages, stop=["\nObservation:"])
        text = (r.content or "").split("\nObservation:")[0].rstrip()
        messages.append({"role": "assistant", "content": text})
        print(f"--- step {n + 1}  ({r.tokens_in:,} tokens in)\n{text}")
        step = parse(text)
        if "final" in step:
            return step["final"], messages
        if "error" in step:
            obs = {"ok": False, "error": step["error"], "next_step": "Continue in the format."}
        else:
            obs = tb.call(step["action"], step["input"])
        print("Observation:", textwrap.shorten(json.dumps(obs, ensure_ascii=False), 300))
        messages.append({"role": "user", "content": "Observation: " + json.dumps(obs, default=str)})
    return "(stopped)", messages

llm_react = LLM(MODEL, cassette="L5v3_nb_react")
answer, react_msgs = react("How many days of 5-litre silicone gaskets do we have left?", tb, llm_react)
print("\nFINAL:", answer)

# %% [markdown]
# Now Kavita's real job. Watch the model preview first (nothing is saved) and ask her.

# %%
tb_r = Toolbox(ERP(), "KJOSHI")
answer, react_msgs = react(GASKET, tb_r, llm_react)
print("\nFINAL:", answer)

# %% [markdown]
# ## 3 · Native tool calling is the same loop
# Modern chat APIs do the parsing for you. You pass the tool **schemas**; the model returns an assistant message whose `tool_calls` carry the name and JSON arguments (that is the **Action**). You run the tool and append a message with `role: "tool"` (that is the **Observation**). The model's next turn is the next **Thought**. When it answers with no tool calls, that is the **Final Answer**.

# %%
def native(question, tb, llm, max_steps=10, messages=None, system="You are Ask Rasoi, Rasoi Steel Works' assistant in Bahi ERP, for Kavita Joshi (KJOSHI). Today is Monday 26 October 2026."):
    messages = messages or [{"role": "system", "content": system}]
    messages.append({"role": "user", "content": question})
    for n in range(max_steps):
        r = llm.chat(messages, tools=tb.schemas())
        messages.append(r.message())
        if not r.tool_calls:
            return r.content, messages
        for tc in r.tool_calls:
            out = tb.call(tc.name, tc.arguments)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)})
    return "(stopped)", messages

llm_native = LLM(MODEL, cassette="L5v3_nb_native")
answer, native_msgs = native("How many days of 5-litre silicone gaskets do we have left?", tb, llm_native)
print(answer)

# %% [markdown]
# Side by side: the text loop's lines, and the native loop's messages.

# %%
rows = []
for m in react_msgs[1:6]:
    rows.append(("ReAct text", m["role"], textwrap.shorten(m["content"], 110)))
for m in native_msgs[1:]:
    body = m.get("content") or ""
    if m.get("tool_calls"):
        body = "tool_calls: " + "; ".join(f"{c['function']['name']}({c['function']['arguments']})" for c in m["tool_calls"])
    rows.append(("native", m["role"], textwrap.shorten(str(body), 110)))
pd.set_option("display.max_colwidth", 120)
pd.DataFrame(rows, columns=["loop", "role", "content"])

# %% [markdown]
# ## 4 · The harness, one part at a time
# **A harness is everything around the model that turns a tool-calling model into a dependable agent**: the system prompt, the message history, the tool registry, the loop and its stop rules, a budget, error recovery, state that survives the day, and the places where a person comes in.
#
# `bahi.course.l5.Harness` has every part, each one switchable. First the parts you write yourself.
#
# ### Exercise 3 · a loop guard
# The commonest failure of a free loop is asking for the same thing again and again. Write `guarded_call`: run a tool normally, but the **third** identical call (same name, same arguments) is not run; it returns an error that tells the model to use what it has.

# %%
# TODO (exercise 3)
def guarded_call(tb, name, args, seen: dict) -> dict:
    key = name + json.dumps(args, sort_keys=True)
    # --- solution (replace with your own) ---
    if seen.get(key, 0) >= 2:
        seen[key] += 1
        return {"ok": False, "error": f"You already called {name} twice with these arguments.",
                "next_step": "Use the result you already have, or ask the user."}
    seen[key] = seen.get(key, 0) + 1
    return tb.call(name, args)

seen = {}
outs = [guarded_call(tb, "check_stock", {"item_code": "GSK-SIL-05L"}, seen)["ok"] for _ in range(4)]
print(outs)
assert outs == [True, True, False, False]

# %% [markdown]
# ### Error recovery: errors that say what to do next
# Every tool in the toolbox returns `ok=false` with an `error` **and** a `next_step`. The loop does not need special code for most errors: the model reads the `next_step` and does it. Here a direct order of 20,000 gaskets is refused (the direct-order cap is ₹50,000), and the refusal says what to do instead.

# %%
show(tb.call("create_purchase_order", {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "quantity": 20000,
                                       "cost_centre": "PRD-07", "need_by": "2026-11-09"}))

# %% [markdown]
# ### The full harness on the first day of Kavita's order
# Every part on. Watch it preview, ask once, raise the request, and **stop**: the request waits for Rohit.

# %%
from bahi.course.l5 import Harness, PARTS
print("parts:", PARTS)
erp = ERP()
kavita = Harness(Toolbox(erp, "KJOSHI"), LLM(MODEL, cassette="L5v3_nb_harness"))
print("KAVITA:", GASKET, "\nASK RASOI:", kavita.respond(GASKET))
print("\nKAVITA: Yes, go ahead.\nASK RASOI:", kavita.respond("Yes, go ahead."))
print("\nwaiting on:", kavita.waiting)
for t in kavita.trace:
    if t["kind"] == "tool":
        print(f"  turn {t['turn']}  {t['name']:26} {json.dumps(t['args'])[:90]}  ok={t['ok']}")

# %% [markdown]
# ### State across days
# The job is waiting for a person. Save the harness's state to disk, as a server would at the end of the request, and read it back into a brand-new object tomorrow.

# %%
kavita.save(WORK / "kavita_thread.json")
st = json.load(open(WORK / "kavita_thread.json"))
print({k: (v if k != "messages" else f"{len(v)} messages") for k, v in st.items() if k not in ("failed", "trace", "stops")})
kavita = Harness.load(WORK / "kavita_thread.json", Toolbox(erp, "KJOSHI"), LLM(MODEL, cassette="L5v3_nb_harness"))
print("reloaded; still waiting on", kavita.waiting)

# %% [markdown]
# ## 5 · An approval is a pause
# While the request waits, the harness holds every write. The next message, whatever it says, is first checked **against Bahi**. A message that *says* "approved" is not trusted; Bahi's status is.
#
# ### Exercise 4 · resume only on Bahi's word
# Write `approval_state(tb, request_no)`: read `order_status` for the request and return `"resume"` if Bahi says APPROVED (`status_code == "AP"`), `"stop"` if REJECTED (`"RJ"`), else `"wait"`.

# %%
# TODO (exercise 4)
def approval_state(tb, request_no) -> str:
    # --- solution (replace with your own) ---
    code = tb.call("order_status", {"request_no": request_no}).get("status_code")
    return {"AP": "resume", "RJ": "stop"}.get(code, "wait")

pr = kavita.waiting["doc"]
print("before Rohit:", approval_state(kavita.tb, pr))
print("KAVITA: Has it gone to Deccan yet?\nASK RASOI:", kavita.respond("Has it gone to Deccan yet?"))
rohit = Toolbox(erp, "RMEHTA")                       # Rohit, in his own inbox, with his own permissions
show(rohit.call("approve_purchase_request", {"request_no": pr, "decision": "approve"}))
print("after Rohit:", approval_state(kavita.tb, pr))
assert approval_state(kavita.tb, pr) == "resume"
note = f"Bahi notification: Rohit Mehta has approved {pr}."
print("\nEVENT:", note, "\nASK RASOI:", kavita.respond(note))
show(kavita.tb.call("order_status", {"po_no": kavita.docs["orders"][-1]}))

# %% [markdown]
# The order is RELEASED. Days later Neha, in stores, records what arrives, in her own session.

# %%
neha = Harness(Toolbox(erp, "NDESAI"), LLM(MODEL, cassette="L5v3_nb_harness"))
po = kavita.docs["orders"][-1]
for msg in [f"12,000 of the 5-litre gaskets arrived from Deccan against {po}. Record them.", "Yes, go ahead."]:
    print("NEHA:", msg, "\nASK RASOI:", textwrap.shorten(neha.respond(msg), 400), "\n")
show(neha.tb.call("order_status", {"po_no": po}))

# %% [markdown]
# ## 6 · A tiny control graph in LangGraph
# The free loop lets the model choose the order of steps. When the business process **is** the order (request before order, approval before release, certificate before any food-contact order), we write the order in code: a **control graph**. A **spine** of steps that always run, and **gates**: checks in code that open a detour only when they are true.
#
# LangGraph gives us five things: a **state** (a typed dict), **nodes** (plain functions that return updates), **edges** (fixed, or conditional on the state), a **checkpointer** (the state saved after every node, per thread) and **interrupts** (a node stops the graph and waits for a person; `Command(resume=...)` carries the answer back in).
#
# ### Exercise 5 · the certificate gate
# Below is a four-node graph: look up → gate → confirm (an interrupt) → commit. Write the gate `cert_gate(state)`: return `"hold"` when the item touches food and the supplier's food-grade certificate is not `"valid"`, else `"confirm"`.

# %%
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
try:
    from langgraph.checkpoint.memory import InMemorySaver as Saver
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as Saver

class Order(TypedDict, total=False):
    item: str; supplier: str; qty: int; facts: dict; out: str
    path: Annotated[list, operator.add]

gtb = Toolbox(ERP(), "KJOSHI")
def look_up(s):
    item = gtb.call("find_item", {"query": s["item"]})["items"][0]
    found = gtb.call("find_supplier", {"name": s["supplier"]})["matches"]
    sup = found[0] if found and found[0]["match"] >= 0.6 else {"supplier_code": None, "food_grade_certificate": "none"}
    return {"facts": {"item_code": item["item_code"], "food": item["food_contact"], "supplier_code": sup["supplier_code"],
                      "cert": sup["food_grade_certificate"]}, "path": ["look_up"]}

# TODO (exercise 5)
def cert_gate(s) -> str:
    # --- solution (replace with your own) ---
    return "hold" if s["facts"]["food"] and s["facts"]["cert"] != "valid" else "confirm"

def hold(s):
    return {"out": f"{s['supplier']} has no valid food-grade certificate ({s['facts']['cert']}); Purchase Policy §6.2 "
                   "does not allow this food-contact order. Nothing was ordered.", "path": ["hold"]}
def confirm(s):
    answer = interrupt({"ask": f"Raise a request for {s['qty']:,} {s['facts']['item_code']} (to order from "
                               f"{s['facts']['supplier_code']})?"})
    return {"out": answer, "path": ["confirm"]}
def commit(s):
    r = gtb.call("create_purchase_request", {"item_code": s["facts"]["item_code"], "quantity": s["qty"],
                                             "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
    return {"out": f"{r['request_no']}: {r['status']}", "path": ["commit"]}

g = StateGraph(Order)
for n, f in [("look_up", look_up), ("hold", hold), ("confirm", confirm), ("commit", commit)]:
    g.add_node(n, f)
g.add_edge(START, "look_up")
g.add_conditional_edges("look_up", cert_gate, ["hold", "confirm"])
g.add_conditional_edges("confirm", lambda s: "commit" if re.search(r"\byes\b", s["out"], re.I) else END)
g.add_edge("hold", END); g.add_edge("commit", END)
graph = g.compile(checkpointer=Saver())

for sup, thread in [("Shakti Seals", "t1"), ("Kaveri Rubber", "t2"), ("Deccan Polymers", "t3")]:
    cfg = {"configurable": {"thread_id": thread}}
    out = graph.invoke({"item": "5 litre silicone gasket", "supplier": sup, "qty": 20000}, cfg)
    if out.get("__interrupt__"):
        print(sup, "-> paused in", graph.get_state(cfg).next, ":", out["__interrupt__"][0].value["ask"])
        out = graph.invoke(Command(resume="Yes, go ahead."), cfg)
    print(sup, "->", out["out"], "| path:", " > ".join(out["path"]), "\n")
assert graph.get_state({"configurable": {"thread_id": "t1"}}).values["path"] == ["look_up", "hold"]

# %% [markdown]
# The course's full graph, `bahi.course.l5.graph.ControlGraph`, has the whole spine (understand, look up, preview, confirm, raise request, wait for approval, create order, release) and the gates. Here it is on the first day of the gasket order. The model is called once, to read Kavita's message into fields; every reply is written by code from the receipts.

# %%
from bahi.course.l5.graph import ControlGraph
cg = ControlGraph(Toolbox(ERP(), "KJOSHI"), LLM(MODEL, cassette="L5v3_nb_graph"))
for msg in [GASKET, "Yes, go ahead."]:
    print("KAVITA:", msg, "\nASK RASOI:", cg.respond(msg), "\n")
print("path:", " > ".join(cg.path), "| waiting in:", cg.waiting_in())
print("model calls:", cg.llm.totals())

# %% [markdown]
# ## 7 · The scorecard
# The six course scenarios against the full harness. (Our twelve-task experiment, free loop against harness against graph on two models, is in `experiments/` and on the deck.)

# %%
from bahi.scenarios import SCENARIOS, run_all, scorecard
results = run_all(lambda erp, user: Harness(Toolbox(erp, user), LLM(MODEL, cassette="L5v3_nb_six")))
scorecard(results)

# %% [markdown]
# ## Your module (starts A5)
# Your A4 toolbox is a folder of tool folders. `FolderToolbox` loads any such folder, and every agent in this notebook runs on it unchanged. Here we fake a "module" from three Bahi tools to show the shape; in A5 you point it at your own folder, write three scenarios and a pass/fail table.

# %%
import shutil, bahi.toolbox as T
from bahi.course.l5.kit import FolderToolbox
kit = WORK / "my_module_tools"; kit.mkdir()
for n in ["find_item", "check_stock", "search_policy"]:
    shutil.copytree(pathlib.Path(T.__file__).parent / n, kit / n)
mine = FolderToolbox(kit, ERP(), "KJOSHI")
print(mine.names)
h = Harness(mine, LLM(MODEL, cassette="L5v3_nb_kit"), tools=mine.names)
print(h.respond("How many 5-litre silicone gaskets are free in Pune stores?"))
