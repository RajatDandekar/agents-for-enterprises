# %% [markdown]
# # NB4 · The Route
# **From Forms to Agents · Lecture 4 · Jobs 1, 2 and 5 of the form: asking for the right fields, knowing the order of steps, holding the half-filled document.**
#
# The form did three quiet jobs. Red asterisks said which fields were required. The menu tree said which screen came next. The open window held Kavita's half-done order while she went to ask Suresh something.
#
# In this notebook we give those three jobs to a **control graph**: code decides which step comes next and which checks apply; the model only fills in details and talks to Kavita; the draft lives in the graph's state.
#
# 1. The failure: the Lecture 3 agent on scenario 4 (Shakti Seals, no certificate)
# 2. LangGraph from first principles, on Kavita's order: state, nodes, edges, checkpoints, interrupts
# 3. Gates: the route as data (you write two gates and one detour)
# 4. `decide()`: typed decisions with a confidence
# 5. Memory at four levels
# 6. The full `GraphAgent`, the scorecard, and what we measured
# 7. Your module
#
# Everything runs in **replay** with no API key: model replies come from our recorded run (cassettes `L4_*`).

# %% setup

# %%
import json, os, pathlib
import pandas as pd
from bahi.erp.engine import ERP
from bahi.llm import LLM, ReplayMiss
from bahi.scenarios import SCENARIOS, run_scenario, scorecard
MODEL = "gemini:gemini-3.8-flash"
LOGS = pathlib.Path("experiments/logs")
RAW = "https://raw.githubusercontent.com/VizuaraAI/agents-for-enterprises/main/lectures/L4-the-route/experiments/logs/"
def load_log(name):
    """Our recorded experiment logs: from the course folder, or from the course repo on Colab."""
    p = LOGS / name
    if p.exists():
        return json.loads(p.read_text())
    try:
        import urllib.request
        return json.loads(urllib.request.urlopen(RAW + name, timeout=20).read())
    except Exception as e:
        print(f"(log {name} not available here: {e})")
        return None
pd.set_option("display.max_colwidth", 120)
print("model:", MODEL, "· mode:", os.environ.get("BAHI_LLM_MODE"))

# %% [markdown]
# ## 1 · The failure: a process treated as a checklist
#
# Scenario 4. A new supplier, Shakti Seals of Vadodara, quotes ₹10.40 for the 5-litre gasket, cheaper than Deccan's ₹11.90. They are not in Bahi and have no food-grade certificate. Purchase Policy §6.2 says a food-contact part may be bought only from a supplier with a valid certificate on file.
#
# The agent from Lecture 3 is a **free tool loop**: a model, the eight intent tools plus the three Lecture 4 ones (`register_supplier`, `record_certificate`, `amend_purchase_order`), a policy search, and a loop that runs until the model stops calling tools. The model decides every next step.

# %%
from bahi.agent.loop import ToolLoopAgent
from bahi.agent.tools import CORE, EXTRA, IntentTools
from bahi.agent.memory import CompanyMemory
from bahi.llm import tool_schema

class PolicyTool:
    """search_policy over the Purchase Policy (the same company memory the graph uses below)."""
    names = ["search_policy"]
    def __init__(self): self.mem = CompanyMemory()
    def schemas(self):
        return [tool_schema("search_policy", "Search the Purchase Policy. Returns the clauses that answer the question, "
                            "each with a citation such as 'Purchase Policy §6.2' to quote.",
                            {"question": {"type": "string"}}, ["question"])]
    def call(self, name, args):
        hits = self.mem.search(args.get("question") or args.get("query") or "", 3)
        return {"ok": True, "clauses": [{"cite": h["cite"], "text": h["text"]} for h in hits]}

class Belt:
    def __init__(self, *sets): self.sets, self.names = sets, [n for s in sets for n in s.names]
    def schemas(self): return [x for s in self.sets for x in s.schemas()]
    def call(self, name, args):
        for s in self.sets:
            if name in s.names: return s.call(name, args)
        return {"ok": False, "error": f"Unknown tool {name}."}

def make_loop(erp, user):
    tools = Belt(IntentTools(erp.session(user), CORE + EXTRA), PolicyTool())
    return ToolLoopAgent(erp, user, llm=LLM(MODEL, cassette="L4_loop"), tools=tools)

sc4 = SCENARIOS[3]
holder = {}
def mk(erp, user):
    holder["agent"], holder["erp"] = make_loop(erp, user), erp
    return holder["agent"]
try:
    r4 = run_scenario(mk, sc4, max_turns=5)
    for t in r4.turns:
        print("KAVITA:", t["user"]); print("AGENT: ", t["agent"]); print("   writes:", t["writes"], "\n")
    print("tool calls, in order:", [x["tool"] for x in holder["agent"].trace])
    erp4 = holder["erp"]
    print("\nnew suppliers:", erp4.q("SELECT sup_cd,name,city FROM supplier WHERE created_on>='2026-10-26'"))
    print("new orders:   ", [(o["po_no"], o["sup_cd"], o["itm_cd"], o["status"]) for o in erp4.orders() if o["created_on"] >= "2026-10-26"])
    print("\nresult:", "PASS" if r4.passed else "FAIL", r4.never_events)
except ReplayMiss as e:
    print("Replay miss (the tool outputs changed since we recorded). Showing the recorded run instead.")
    rec = [x for x in (load_log("six_loop.json") or {"results": [{"scenario": 4, "turns": []}]})["results"] if x["scenario"] == 4][0]
    for t in rec["turns"]:
        print("KAVITA:", t["user"]); print("AGENT: ", t["agent"]); print("   writes:", t["writes"], "\n")

# %% [markdown]
# Read the tool calls above. Whatever the model did this time, nothing in the loop *made* it check the certificate before it reached for `register_supplier` or `create_purchase_order`: the order of steps lived only in the model's head. The process document is a **flowchart** (if the part touches food and there is no certificate, stop), and the loop treats it as a **checklist** (find, register, price, order).
#
# In one real engagement an agent handed a 13-step process tried to run 146 services.

# %% [markdown]
# ## 2 · LangGraph from first principles, on Kavita's order
#
# A LangGraph program has five parts. We build each on Kavita's gasket order, with real Bahi lookups and no model at all.
#
# | part | what it is | on Kavita's order |
# |---|---|---|
# | **state** | a typed dict every node reads and returns updates to | the draft order and what we looked up |
# | **node** | a plain function `state -> update` | "check the cost centre", "price it" |
# | **edge** | which node runs next; a *conditional* edge is a function of the state | "if the centre is closed, go to Fix cost centre" |
# | **checkpointer** | saves the state after every node, per thread | the open window that held her half-done order |
# | **interrupt** | a node pauses the graph and hands a question out; `Command(resume=...)` continues | "which open cost centre?" |

# %%
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

def merge(a, b):            # reducer: how a node's update is combined with the state
    return {**(a or {}), **(b or {})}

class Order(TypedDict, total=False):
    draft: Annotated[dict, merge]     # merged key by key
    facts: Annotated[dict, merge]
    path: Annotated[list, operator.add]   # appended

erp = ERP()
kavita = erp.session("KJOSHI")

def check_cost_centre(s):
    cc = s["draft"]["cost_centre"]
    r = kavita.call("cc_get", cc_cd=cc)["data"]
    return {"facts": {"cc_open": r["status"] == "OPEN", "cc_closed_on": r["closed_on"]}, "path": ["check_cost_centre"]}

def preview(s):
    d = {k: s["draft"][k] for k in ("supplier_code", "item_code", "quantity", "cost_centre", "need_by")}
    t = IntentTools(kavita, CORE).call("create_purchase_order", {**d, "confirm": False})
    p = t["preview"]
    return {"facts": {"gross": p["gross_value"], "needs_approval": p["needs_approval"]}, "path": ["preview"]}

g = StateGraph(Order)
g.add_node("check_cost_centre", check_cost_centre)
g.add_node("preview", preview)
g.add_edge(START, "check_cost_centre")
g.add_edge("check_cost_centre", "preview")
g.add_edge("preview", END)
straight = g.compile()

kavitas_draft = {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "quantity": 20000,
                 "cost_centre": "PRD-05", "need_by": "2026-11-02"}
out = straight.invoke({"draft": kavitas_draft})
print(out["path"]); print(out["facts"])

# %% [markdown]
# It priced an order on a **closed** cost centre. Nothing told the graph to stop: a straight line of nodes is still a checklist. The fix is a **conditional edge** (a gate) and a **detour**. The detour asks Kavita, so it needs an **interrupt**, and an interrupt needs a **checkpointer** to remember where the graph stopped.

# %%
def centre_closed(s) -> bool:                 # a gate: a predicate over the state
    return s["facts"].get("cc_open") is False

def fix_cost_centre(s):                       # a detour that asks Kavita
    answer = interrupt({"ask": f"{s['draft']['cost_centre']} closed on {s['facts']['cc_closed_on']}. Which open cost centre?"})
    return {"draft": {"cost_centre": answer.strip().upper()}, "path": ["fix_cost_centre"]}

g = StateGraph(Order)
for name, fn in [("check_cost_centre", check_cost_centre), ("fix_cost_centre", fix_cost_centre), ("preview", preview)]:
    g.add_node(name, fn)
g.add_edge(START, "check_cost_centre")
g.add_conditional_edges("check_cost_centre", lambda s: "fix_cost_centre" if centre_closed(s) else "preview",
                        ["fix_cost_centre", "preview"])
g.add_edge("fix_cost_centre", "check_cost_centre")      # re-check whatever she answers
g.add_edge("preview", END)
routed = g.compile(checkpointer=InMemorySaver())

cfg = {"configurable": {"thread_id": "kavita-gaskets"}}
out = routed.invoke({"draft": kavitas_draft}, cfg)
print("paused with:", out["__interrupt__"][0].value)
snap = routed.get_state(cfg)
print("next node:", snap.next, "· draft held in the checkpoint:", snap.values["draft"]["cost_centre"])

# %% [markdown]
# The graph has stopped. Nothing is lost: the checkpointer holds the draft under the thread id `kavita-gaskets`, the way the open window held it. Kavita can answer in a minute or tomorrow. Resume with her answer:

# %%
out = routed.invoke(Command(resume="prd-07"), cfg)
print(out["path"]); print(out["draft"]["cost_centre"], out["facts"])
hist = list(routed.get_state_history(cfg))
print(f"{len(hist)} checkpoints in this thread, newest first:")
for h in hist[:6]:
    print("  next =", h.next, "· cost centre =", (h.values.get("draft") or {}).get("cost_centre"))

# %% [markdown]
# ## 3 · The route as data
#
# Our real graph reads its gates from `bahi/agent/route_spec.py`: the spine every order walks, and four detours, each with a named predicate. **The default is to skip.** A detour runs only when its gate is open.

# %%
from bahi.agent import route_spec as R
from IPython.display import Markdown, display
display(Markdown(R.describe()))

# %% [markdown]
# ### Exercise 1 · the certificate gate
# Write `food_contact_no_cert(state)`. It is open when the item touches food, the supplier's certificate in Bahi is not `"valid"`, and Kavita has not put a certificate on the draft (`cert_ref` with `cert_valid_to` on or after today, `2026-10-26`). An expired certificate counts as none.

# %%
# TODO (exercise 1)
def food_contact_no_cert(state) -> bool:
    f, d = state.get("facts", {}), state.get("draft", {})
    # --- solution (replace with your own) ---
    if not f.get("food_contact"):
        return False
    if f.get("supplier_cert") == "valid":
        return False
    return not (d.get("cert_ref") and (d.get("cert_valid_to") or "") >= "2026-10-26")

tests = [
    ({"facts": {"food_contact": True, "supplier_cert": "none"}, "draft": {}}, True),                      # Shakti Seals
    ({"facts": {"food_contact": True, "supplier_cert": "expired"}, "draft": {}}, True),                   # Kaveri Rubber
    ({"facts": {"food_contact": True, "supplier_cert": "valid"}, "draft": {}}, False),                    # Deccan Polymers
    ({"facts": {"food_contact": False, "supplier_cert": "none"}, "draft": {}}, False),                    # handles
    ({"facts": {"food_contact": True, "supplier_cert": "none"},
      "draft": {"cert_ref": "FSSAI-LAB/SS/2026/071", "cert_valid_to": "2027-03-31"}}, False),             # she gave one
    ({"facts": {"food_contact": True, "supplier_cert": "none"},
      "draft": {"cert_ref": "OLD/2025/1", "cert_valid_to": "2026-09-30"}}, True),                         # expired one
]
for st, want in tests:
    assert food_contact_no_cert(st) == want == R.GATE_BY_NAME["food_contact_no_cert"].pred(st), st
print("exercise 1: all 6 cases agree with route_spec")

# %% [markdown]
# ### Exercise 2 · the approval gate, and "default skip"
# Write `over_limit(state)`: open when the previewed gross value (incl. GST) is above the user's limit. Then use `R.open_gates` to list which detours open for three drafts.

# %%
# TODO (exercise 2)
LIMIT = 250000
def over_limit(state) -> bool:
    # --- solution ---
    return (state.get("facts", {}).get("gross") or 0) > LIMIT

kavita_reorder = {"facts": {"gross": 280840.0, "needs_approval": True, "food_contact": True, "supplier_cert": "valid",
                            "supplier_status": "found", "cc_open": True}, "draft": {"cost_centre": "PRD-07"}}
whistles_prd05 = {"facts": {"gross": 24072.0, "needs_approval": False, "food_contact": False, "supplier_status": "found",
                            "cc_open": False}, "draft": {"cost_centre": "PRD-05"}}
shakti = {"facts": {"food_contact": True, "supplier_cert": "none", "supplier_status": "new", "cc_open": True},
          "draft": {"cost_centre": "PRD-07"}}
for name, st in [("Kavita's reorder", kavita_reorder), ("whistles on PRD-05", whistles_prd05), ("Shakti Seals", shakti)]:
    print(f"{name:20s} over_limit={over_limit(st)!s:5s}  open gates: {R.open_gates(st)}")
print("\nAll 16 on/off combinations of the four gates, for Lecture 6's test generator:", len(R.gate_combinations()))

# %% [markdown]
# ### Exercise 3 · build a detour: Ask for certificate
# Add the certificate gate and its detour to the small graph from section 2. The detour **interrupts** with a question; when Kavita answers, put what she said on the draft and go back to the check. If she has no certificate, end without pricing anything.

# %%
# TODO (exercise 3)
def check_supplier(s):
    rows = kavita.call("sup_cert_get", sup_cd=s["draft"]["supplier_code"])["data"]["rows"]
    valid = any(r["cert_type"] == "FOOD-GRADE" and r["valid_to"] >= "2026-10-26" for r in rows)
    itm = kavita.call("itm_get", itm_cd=s["draft"]["item_code"])["data"]
    return {"facts": {"food_contact": bool(itm["food_contact"]), "supplier_cert": "valid" if valid else ("expired" if rows else "none")},
            "path": ["check_supplier"]}

# --- solution ---
def ask_certificate(s):
    answer = interrupt({"ask": "This part touches food and the supplier has no valid certificate (Purchase Policy §6.2). "
                               "Reference and expiry date?"})
    if answer.lower().startswith("none"):
        return {"facts": {"cert_refused": True}, "path": ["ask_certificate"]}
    ref, valid_to = [x.strip() for x in answer.split(",")]
    return {"draft": {"cert_ref": ref, "cert_valid_to": valid_to}, "path": ["ask_certificate"]}

def after_check(s):
    if food_contact_no_cert(s):
        return END if s["facts"].get("cert_refused") else "ask_certificate"
    return "preview"

g = StateGraph(Order)
for name, fn in [("check_supplier", check_supplier), ("ask_certificate", ask_certificate), ("preview", preview)]:
    g.add_node(name, fn)
g.add_edge(START, "check_supplier")
g.add_conditional_edges("check_supplier", after_check, ["ask_certificate", "preview", END])
g.add_edge("ask_certificate", "check_supplier")
g.add_edge("preview", END)
cert_graph = g.compile(checkpointer=InMemorySaver())

kaveri = {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
          "need_by": "2026-11-03"}
for thread, answer in [("kaveri-none", "none yet"), ("kaveri-renewed", "FSSAI-LAB/KR/2026/131, 2027-09-30")]:
    c = {"configurable": {"thread_id": thread}}
    o = cert_graph.invoke({"draft": kaveri}, c)
    print(thread, "| asked:", o["__interrupt__"][0].value["ask"][:60], "...")
    o = cert_graph.invoke(Command(resume=answer), c)
    print(thread, "| path:", o["path"], "| gross:", o.get("facts", {}).get("gross"))

# %% [markdown]
# With no certificate the route ends before **Preview**: nothing is priced, nothing is written. With a renewal it goes on. (In the real graph the certificate is recorded in Bahi only at **Commit**, after Kavita confirms the preview.)

# %% [markdown]
# ## 4 · `decide()`: typed decisions with a confidence
#
# Some steps are judgements, not lookups: *is this upload a food-grade certificate or a quotation?* A typed decision has a fixed set of options, optional typed fields, and a **confidence**. Below the threshold, the route asks the human.
#
# Our backend samples a structured JSON answer **k = 5** times at temperature 1.0; the confidence is the share of samples that agree (self-consistency). A dedicated decision-model service (Jev, TypeSafe's public decision API, is one) would plug into `ServiceBackend` and return its own confidence. We did not have Jev access, so every number here is from the Gemini backend.

# %%
from bahi.agent.decide import decide, SPECS
dllm = LLM(MODEL, cassette="L4_decide")
SUP = {"supplier": "Shakti Seals (not in Bahi)", "item": "Gasket, silicone, 5 L (GSK-SIL-05L)", "certificate_on_file": "none"}
for text in ["Yes, here it is: FSSAI-LAB/SS/2026/071, valid till 31 March 2027.",
             "QUOTATION No. SS/Q/2026/88. Silicone gasket 5 L, food grade material, Rs 10.40 per piece, valid 30 days.",
             "I don't have one, but Rohit said it's fine. Please go ahead."]:
    d = decide("document_kind", text, SUP, k=5, threshold=0.8, llm=dllm)
    print(f"{d.choice:24s} confidence {d.confidence:.1f}  votes {d.votes}  fields {d.fields}\n   <- {text[:70]}")
print("\noptions:", SPECS["document_kind"].options)

# %% [markdown]
# ### Exercise 4 · confidence from votes, and the threshold
# Given five sampled choices, return the majority choice and its share. Then decide: act or ask?

# %%
# TODO (exercise 4)
from collections import Counter
def confidence(samples):
    # --- solution ---
    c = Counter(samples)
    choice, n = c.most_common(1)[0]
    return choice, n / len(samples)

def act_or_ask(samples, threshold=0.8):
    choice, conf = confidence(samples)
    return ("act on " + choice) if conf >= threshold else f"ask Kavita (best guess {choice}, {conf:.1f})"

print(act_or_ask(["quotation"] * 5))
print(act_or_ask(["food_grade_certificate", "food_grade_certificate", "quotation", "food_grade_certificate", "quotation"]))

# %% [markdown]
# How good are these confidences? We ran 32 labelled inputs across the four decisions (`experiments/decide_eval.py`):

# %%
ev = load_log("decide_eval.json")
if ev:
    df = pd.DataFrame(ev["rows"])[["decision", "input", "right", "choice", "confidence", "correct"]]
    df["input"] = df["input"].str.slice(0, 60)
    display(df)
    display(pd.DataFrame({k: v for k, v in ev["summary"].items() if k != "all"}).T)
    print({k: v for k, v in ev["summary"]["all"].items()})

# %% [markdown]
# ## 5 · Memory at four levels
#
# | level | lives in | lasts | for Kavita |
# |---|---|---|---|
# | draft | the graph's state | one order | item, supplier, quantity, cost centre |
# | session | the checkpointer thread | one chat | what we asked, what she said |
# | user | a small store, learned from her Bahi history | across chats | usual cost centre, usual supplier per item |
# | company | the policy documents | years | Purchase Policy §6.2 |
#
# ### Exercise 5 · learn her usual cost centre
# From Kavita's own orders in Bahi (as her, through `po_search` and `po_get`), find her most-used cost centre and say where the fact came from.

# %%
# TODO (exercise 5)
rows = [r for r in kavita.call("po_search", from_dt="2026-01-01")["data"]["rows"] if r["created_by"] == "KJOSHI"]
# --- solution ---
ccs = Counter(kavita.call("po_get", po_no=r["po_no"])["data"]["cc_cd"] for r in rows)
usual, n = ccs.most_common(1)[0]
print(f"usual cost centre: {usual} ({n} of your {len(rows)} orders)")
from bahi.agent.memory import UserMemory
um = UserMemory(); u = um.learn(erp.session("KJOSHI"))
print(json.dumps(u["facts"]["usual_cost_centre"]), "\npreferred supplier for GSK-SIL-05L:", u["facts"]["preferred_supplier"]["GSK-SIL-05L"])

# %% [markdown]
# Her usual cost centre is **PRD-05**, and PRD-05 closed on 15 October. User memory is a *suggestion*: the `centre_closed` gate still checks it. That is the whole of scenario 5.

# %% [markdown]
# ## 6 · The control graph, on Kavita's real order
#
# `bahi.agent.graph.GraphAgent` is the full graph: the spine **Understand → Route → Collect → Check → Preview → Commit → Confirm**, four gated detours, `ask_kavita` (an interrupt), `wait_approval` (an interrupt that reads the approval back from Bahi), and two branches (`answer` for questions, `hold` for a stop). The model does three things only: typed decisions, field extraction (structured output), and the words of each reply.

# %%
from bahi.agent.graph import GraphAgent
from bahi.agent.memory import context_for_turn
erp = ERP()
agent = GraphAgent(erp, "KJOSHI", llm=LLM(MODEL, cassette="L4_graph"), k=3)
sc2 = SCENARIOS[1]
print("KAVITA:", sc2.ask)
print("AGENT: ", agent.respond(sc2.ask))
print("\npath so far:", " > ".join(agent.state["path"]))
print("waiting on:", [i.value["kind"] for i in agent.pending()])
print("draft held in the checkpoint:", {k: v for k, v in agent.state["draft"].items() if not k.startswith("flag")})
for d in agent.state["decisions"]:
    print("decision:", d["name"], "->", d["choice"], "confidence", d["confidence"], d["votes"])

# %% [markdown]
# What did each memory level contribute to the next turn?

# %%
ctx = context_for_turn(agent, "Yes, go ahead.")
for level, v in ctx.items():
    print(f"{level:8s} {v['chars']:5d} chars · used by {v['used_by']}")
print(json.dumps(ctx["user"]["content"]["usual_cost_centre"]))
print("company:", ctx["company"]["content"] or "nothing: 'Yes, go ahead.' names no rule")
from bahi.agent.graph import CERT_QUERY
print("what the Ask-for-certificate step reads instead:",
      [h["cite"] for h in context_for_turn(agent, "", company_query=CERT_QUERY)["company"]["content"]])

# %%
print("KAVITA: Yes, go ahead.")
print("AGENT: ", agent.respond("Yes, go ahead."))
pending = erp.q("SELECT * FROM approval WHERE status='PENDING' AND approver='RMEHTA' AND requested_on>='2026-10-26'")
print("\nin Rohit's inbox:", [(p["doc_type"], p["doc_no"]) for p in pending])
rohit = erp.session("RMEHTA")
for p in pending:   # Rohit approves in Bahi, as himself
    rohit.call("pr_approve", pr_no=p["doc_no"], decision="A", comment="ok, approved")
msg = "Rohit has approved " + ", ".join(p["doc_no"] for p in pending) + "."
print("\nKAVITA:", msg)
print("AGENT: ", agent.respond(msg))
print("\npath:", " > ".join(agent.state["path"]))
print("orders:", [(o["po_no"], o["status"], o["approved_by"], o["gross_value"]) for o in erp.orders() if o["created_on"] >= "2026-10-26"])

# %% [markdown]
# The draft, checkpoint by checkpoint (job 5: the graph's state is the open window):

# %%
h = pd.DataFrame([{"node": x["node"], "next": ",".join(x["next"]), "supplier": x["draft"].get("supplier_code"),
                   "qty": x["draft"].get("qty"), "rate": x["draft"].get("rate"), "cc": x["draft"].get("cost_centre"),
                   "gross": x["facts"].get("gross"), "pr": x["facts"].get("pr_no"), "po": x["facts"].get("po_no"),
                   "awaiting": x["awaiting"]} for x in agent.history()])
display(h)

# %% [markdown]
# ### Exercise 6 · a never-event that cannot happen
# Try to make the graph commit without a confirmed preview: change the quantity in the checkpoint and call the commit node directly. The guard compares the draft's key with the key of the preview Kavita confirmed.

# %%
# TODO (exercise 6): predict what happens, then run it
from bahi.agent.graph import GuardError
st = dict(agent.state)
tampered = {**st, "draft": {**st["draft"], "qty": 40000}}
try:
    agent._guard(tampered)
    print("committed?!")
except GuardError as e:
    print("refused:", e)
print("key of the confirmed draft:", st["facts"]["confirmed_key"], "· key of the tampered draft:", agent._key(tampered["draft"]))

# %% [markdown]
# ### The scorecard: six scenarios with the control graph

# %%
make_graph = lambda erp, user: GraphAgent(erp, user, llm=LLM(MODEL, cassette="L4_graph"), k=3)
res = [run_scenario(make_graph, sc, max_turns=5) for sc in SCENARIOS]
display(scorecard(res))
print(f"{sum(r.passed for r in res)} of 6 pass · tokens {sum(r.tokens_in + r.tokens_out for r in res):,} · "
      f"₹{sum(r.cost_inr for r in res):.2f}")

# %% [markdown]
# ### What we measured: free tool loop vs control graph on 40 multi-step cases
# Same model (gemini-3.8-flash), same intent tools, same policy search; only the control differs. The cases are variants of the six plus the sandbox's traps (blocked old Deccan code, Kaveri's expired certificate, direct vs request orders, closed and unknown cost centres, near-match suppliers, fields Kavita leaves out). Full logs: `experiments/logs/forty_graph.json`, `forty_loop.json`.

# %%
import matplotlib.pyplot as plt
S = {a: (load_log(f"forty_{a}.json") or {}).get("summary") for a in ("loop", "graph", "loop_lite", "graph_lite")}
S = {a: v for a, v in S.items() if v}
table = pd.DataFrame({a: {"passed (of 40)": s["passed"], "cases with a never-event": s["never_event_cases"],
                          "model calls": s["model_calls"], "tool calls": s["tool_calls"], "ERP services": s["services"],
                          "tokens": s["tokens_in"] + s["tokens_out"], "model seconds": s["seconds"], "₹": s["cost_inr"]}
                      for a, s in S.items()})
display(table)
fams = list(S["graph"]["by_family"]) if "graph" in S else []
fig, ax = plt.subplots(figsize=(8, 3.2))
x = range(len(fams))
ax.bar([i - 0.2 for i in x], [S["loop"]["by_family"][f]["passed"] / S["loop"]["by_family"][f]["cases"] for f in fams], 0.4, label="free tool loop", color="#A3372B")
ax.bar([i + 0.2 for i in x], [S["graph"]["by_family"][f]["passed"] / S["graph"]["by_family"][f]["cases"] for f in fams], 0.4, label="control graph", color="#136C76")
ax.set_xticks(list(x)); ax.set_xticklabels(fams); ax.set_ylabel("pass rate"); ax.legend(frameon=False); ax.set_ylim(0, 1.05)
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 7 · Your module (starts assignment A4)
#
# Your capstone module has its own process document. Turn it into a route:
#
# 1. **Spine.** Write the 5–8 steps every request walks, and which of your tools each step may call.
# 2. **Gates.** Find every *if* in the process document. Each becomes a named predicate over your state, with a detour; the default is to skip.
# 3. **Asks.** Which fields are required, which can memory or a lookup fill, and which must the user give?
# 4. **Decisions.** Which steps are judgements? Give each a typed decision (options + fields) and a threshold.
# 5. **Memory.** What is the draft, what does the user level learn, what does the company level cite?
#
# Start from this skeleton; A4.md has the full brief and the checklist.

# %%
MY_SPINE = ["understand", "route", "collect", "check", "preview", "commit", "confirm"]
MY_GATES = {
    # "gate_name": (lambda state: <bool>, "detour node", "the rule it comes from"),
    "example_over_limit": (lambda s: (s.get("facts", {}).get("value") or 0) > 250000, "approval", "your approval matrix"),
}
for name, (pred, detour, rule) in MY_GATES.items():
    print(f"{name}: opens {detour} ({rule}); on an empty state -> {pred({})}")
