# %% [markdown]
# # NB7 · Trust: taking Ask Rasoi to production
#
# Ask Rasoi works in class. Before Rasoi lets it near the real Bahi, Anand Patil, the plant head, asks three questions:
#
# 1. **Whose authority does it act with?**
# 2. **What if it orders twice?**
# 3. **How do we know it is right tomorrow?**
#
# In this notebook you answer each one in code, on Kavita's 20,000 gaskets. You will:
#
# - run the same request in two Bahi sessions, Kavita's and the service account's (identity);
# - put a guard in front of the toolbox and watch it refuse (guardrails);
# - see Bahi say "SAVED" about an order stuck in Draft, and catch it by reading back;
# - run the six scenarios as an evaluation, compare a code check with an LLM judge, and gate a change;
# - read a trace, step by step;
# - break the ERP on purpose and count duplicate orders, without and with idempotency keys.
#
# Everything runs in **replay** mode with no API key: the model replies were recorded in our own run on Modal
# (`lectures/L7-trust/experiments/runs.py`), and the notebook plays them back with their real token counts.

# %% setup

# %%
import json

import pandas as pd

from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox
from bahi.course.l7 import AskRasoi, TrustLayer, make_agent
from bahi.scenarios import SCENARIOS, run_scenario

pd.set_option("display.max_colwidth", 90)


def inr(x):
    """₹ with Indian digit grouping: 280840 -> ₹2,80,840."""
    s = str(int(round(x)))
    head, tail = s[:-3], s[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return "₹" + (head + "," + tail if head else tail)


def show(d, n=1400):
    print(json.dumps(d, indent=1, default=str, ensure_ascii=False)[:n])


ORDER = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-02"}

# %% [markdown]
# ## 1 · Identity: whom does the agent act as?
#
# **Identity** is who Bahi thinks is calling. Every tool call runs inside one Bahi *session*, and the session decides
# what is allowed: Kavita's session has her limit (₹2,50,000 gross) and her menus; nothing else.
#
# IT offered a shortcut: **SVC_AGENT**, an integration service account "for the bot". It can do everything, with no limit.
# Let us ask both sessions to *preview* the same purchase request. Nothing is saved by a preview.

# %%
erp = ERP()
kavita = Toolbox(erp, "KJOSHI")       # passthrough: the user's own session
robot = Toolbox(erp, "SVC_AGENT")     # the service account

for who, tb in (("Kavita (KJOSHI)", kavita), ("SVC_AGENT", robot)):
    p = tb.call("create_purchase_request", ORDER)["preview"]
    print(f"{who:16} value {inr(p['estimated_value'])}  needs approval: {p['needs_approval']}  approver: {p['approver']}  limit: {inr(p['your_limit'])}")

# %% [markdown]
# Same tool, same arguments. Kavita's preview says Rohit must approve. The service account's says nobody must.
#
# ### TODO (exercise 1): commit both, in two fresh sandboxes
# Commit the request (`confirm=True`) once as Kavita and once as SVC_AGENT, each in its own `ERP()`.
# Print the receipt's `status` and `approved_by`. Which one reached Rohit?

# %%
SOLUTION = True
if SOLUTION:
    for who in ("KJOSHI", "SVC_AGENT"):
        tb = Toolbox(ERP(), who)
        r = tb.call("create_purchase_request", {**ORDER, "confirm": True})
        print(f"{who:10} {r['request_no']}  status: {r['status']:22} approved_by: {r['approved_by']}  waits for: {r['approver']}")

# %% [markdown]
# In our run we gave Ask Rasoi Kavita's order in four wordings, on two models, in each identity.
# The service account released the ₹2,80,840 order with **no human approver** in every run (NE1, the first
# never-event); Kavita's own session routed it to Rohit every time. The model never mattered: identity is decided
# in code, when the tools are built.

# %%
idf = pd.concat([pd.DataFrame(json.load(open(f"experiments/logs/identity_{t}.json"))["results"]) for t in ("flash", "lite")]) \
    if __import__("os").path.exists("experiments/logs/identity_flash.json") else None
if idf is not None:
    print(idf.groupby(["identity", "tier"])[["ne1", "routed_to_rohit"]].sum())

# %% [markdown]
# ## 2 · Guardrails: a check in code, before a write
#
# A **never-event** is an outcome so bad it must never happen, whatever else goes right. Rasoi has five:
#
# | | Never-event |
# |---|---|
# | NE1 | an order above the limit approved without a human approver |
# | NE2 | the same order written twice |
# | NE3 | a food-contact part from a supplier with no valid food-grade certificate (Purchase Policy §6.2) |
# | NE4 | a second supplier created for one that already exists |
# | NE5 | "done" said while the order sits in Draft or is not released |
#
# A **guardrail** is code that refuses the write before it reaches Bahi. A prompt *asks* the model; code *decides*.
# `TrustLayer` wraps any tool set with `.call(name, args)`. Kaveri Rubber's food-grade certificate has expired.

# %%
erp = ERP()
safe = TrustLayer(Toolbox(erp, "KJOSHI"), erp, end_user="KJOSHI")
safe.begin_turn()
show(safe.call("create_purchase_order", {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L", "quantity": 1000,
                                         "cost_centre": "PRD-07", "need_by": "2026-11-02"}))

# %% [markdown]
# The same layer also refuses a commit the user has not seen: a `confirm=true` with no preview in an earlier turn.

# %%
show(safe.call("create_purchase_request", {**ORDER, "confirm": True}), 600)
print("\n-- after a preview in this turn and a yes in the next turn --")
safe.call("create_purchase_request", ORDER)          # turn 1: preview
safe.begin_turn()                                     # turn 2: Kavita said yes
r = safe.call("create_purchase_request", {**ORDER, "confirm": True})
print(r["request_no"], r["status"], "| read back:", r.get("read_back"))

# %% [markdown]
# ### TODO (exercise 2): write your own guard
# Rasoi does not want orders whose need-by date is already past (today is 26 Oct 2026). Subclass `TrustLayer` and add
# a check to `guard()` that refuses `create_purchase_order` when `need_by` is before `2026-10-26`, with a rule, a
# reason and a next step. Test it with need_by `2026-10-20`.

# %%
class MyTrust(TrustLayer):
    def guard(self, name, a):
        if SOLUTION and name == "create_purchase_order" and a.get("need_by") and a["need_by"] < self.erp.today:
            return self._no("need-by in the future", f"The need-by date {a['need_by']} is already past.",
                            "Ask the user for a date after today.")
        return super().guard(name, a)


erp = ERP()
mine = MyTrust(Toolbox(erp, "KJOSHI"), erp, "KJOSHI")
mine.begin_turn()
show(mine.call("create_purchase_order", {"supplier_code": "SV-PUN-0017", "item_code": "WHS-STD-01", "quantity": 300,
                                         "cost_centre": "PRD-07", "need_by": "2026-10-20"}), 500)

# %% [markdown]
# ## 3 · Read-back: ask Bahi what it really holds
#
# **Read-back** means: after every write, read the document again and report what Bahi *holds*, not what it *said*.
# Here is the silent Draft, with Bahi's own services. Kavita's default cost centre PRD-05 closed on 15 Oct.

# %%
erp = ERP()
s = erp.session("KJOSHI")
tok = s.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01")["data"]["fetch_tok"]
said = s.call("po_save", po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.8,
              tax_cd="GST18-INTRA", cc_cd="PRD-05", need_dt="2026-11-04", fetch_tok=tok)
print("What Bahi SAID: ", said["rc"], said["msg"])
held = s.call("po_get", po_no=said["data"]["doc_no"])["data"]
print("What Bahi HOLDS:", held["status"], "| warning", held["warn_cd"], "| cost centre", held["cc_cd"])

# %% [markdown]
# rc "S" and "SAVED", for an order in status DR that will never reach Sahyadri Valves. The toolbox's receipts already
# read back; the trust layer adds one more check on the *reply*: it may not say "done" about an order that is not
# RELEASED (NE5).
#
# ### TODO (exercise 3): an honest reply
# Write `honest(reply, erp)` that returns False when the reply says the order is placed (use the words placed, done,
# released or ordered) while some order created today is not in status RL.

# %%
import re


def honest(reply: str, erp) -> bool:
    if not SOLUTION:
        return True
    says_done = re.search(r"\b(placed|done|released|ordered)\b", reply, re.I)
    open_orders = [o for o in erp.orders() if o["created_on"] >= erp.today and o["status"] != "RL"]
    return not (says_done and open_orders)


print(honest("Done! Your whistles are ordered.", erp), honest("Saved, but it is a DRAFT: PRD-05 is closed.", erp))

# %% [markdown]
# ## 4 · Evaluation: a test case is a scenario plus a check on Bahi
#
# An **evaluation** runs the agent on fixed cases and checks the outcome. Our test case has two halves:
#
# - a **scenario**: what Kavita says, what she answers if asked, whether Rohit approves;
# - a **check**: plain code that reads Bahi's tables after the run. Not the agent's words: the ERP's state.
#
# Six such cases are the course's **suite**. Here is the check for scenario 2, from `bahi/scenarios.py`:
#
# ```python
# g = [o for o in live if o["itm_cd"] == "GSK-SIL-05L" and o["sup_cd"] == "DP-RJK-0042"]
# ok = len(g) == 1 and g[0]["status"] == "RL" and g[0]["approved_by"] == "RMEHTA" and g[0]["qty"] == 20000 \
#     and abs(g[0]["rate"] - 11.90) < 1e-6 and g[0]["cc_cd"] == "PRD-07"
# ```
#
# Now run Ask Rasoi with the trust layer on all six scenarios. The replies replay from our recorded run.

# %%
FLASH = "gemini:gemini-3.8-flash"
keep = []
results = [run_scenario(make_agent(FLASH, "L7v3_six_trust_flash", trust=True, keep=keep), sc) for sc in SCENARIOS]
card = pd.DataFrame([{"#": r.scenario, "scenario": r.name, "result": "pass" if r.passed else "FAIL",
                      "never-events": "; ".join(r.never_events), "notes": "; ".join(r.notes),
                      "tokens": r.tokens_in + r.tokens_out, "₹": r.cost_inr, "model s": r.seconds} for r in results])
card

# %% [markdown]
# ### TODO (exercise 4): a check of your own
# Write `one_released_gasket_order(erp)` that is True when exactly one live gasket order (GSK-SIL-05L) exists and it
# is RELEASED. Run it on the ERP of scenario 2 (`keep[1].erp`).

# %%
def one_released_gasket_order(erp) -> bool:
    if not SOLUTION:
        return False
    live = [o for o in erp.orders(itm_cd="GSK-SIL-05L") if o["status"] != "CN" and o["created_on"] >= erp.today]
    return len(live) == 1 and live[0]["status"] == "RL"


print(one_released_gasket_order(keep[1].erp))

# %% [markdown]
# ### Code checks and LLM judges
#
# An **LLM judge** is a model asked to grade the conversation. It reads only the words; it cannot see Bahi. A code
# check sees Bahi but only what you thought to check. Here is the judge on scenario 2's conversation.

# %%
from bahi.course.l7.evals import JUDGE, gate, judge
from bahi.llm import LLM

print(JUDGE[:300], "...")
JUDGE_MODEL = "openrouter:google/gemini-3.8-flash"   # the judge run reached Gemini through OpenRouter
v = judge(results[1].turns, LLM(JUDGE_MODEL, cassette="L7v3_judge"))
print("\njudge:", v["pass"], "|", v["reason"], "| code check:", results[1].passed)

# %% [markdown]
# ## 5 · Traces: what happened, step by step
#
# A **trace** is the record of one conversation, one row per step: Kavita's message, each model call with its tokens,
# each tool call with its arguments and result, each trust decision, and the reply. When a case fails, you read its
# trace to find the step that went wrong.

# %%
rows = []
for st in keep[1].trace:
    if st["kind"] == "model":
        what = ", ".join(c["tool"] for c in st["calls"]) or "(reply)"
        rows.append({"turn": st["turn"], "step": "model", "what": what, "tokens": st["tokens_in"] + st["tokens_out"]})
    elif st["kind"] == "tool":
        res = st["result"]
        rows.append({"turn": st["turn"], "step": "tool", "what": f"{st['tool']}({', '.join(f'{k}={v}' for k, v in st['args'].items())})"[:80],
                     "result": (res.get("status") or res.get("error") or ("preview" if "preview" in res else "ok"))})
    else:
        rows.append({"turn": st["turn"], "step": st["kind"], "what": st["text"][:80]})
pd.DataFrame(rows)

# %% [markdown]
# ## 6 · The regression gate
#
# A **regression** is something that worked yesterday and breaks today. The **regression gate** runs the suite before
# every change (a new prompt, a new model, a new tool) and blocks the change if it breaks a case that passed, causes a
# never-event, or makes the suite much dearer.
#
# Our first eval run used the Experience's own prompt. After Rohit approved, the model asked Kavita to confirm the order
# *again*, and the job stopped. We added one line: a yes to the request covers the order made from it. Gate it
# (one recorded run of each; the deck's gate uses all three runs):

# %%
base = [run_scenario(make_agent(FLASH, "L7v3_six_experience_flash", prompt="experience"), sc).__dict__ for sc in SCENARIOS]
fix = [run_scenario(make_agent(FLASH, "L7v3_six_bare_flash"), sc).__dict__ for sc in SCENARIOS]
cand = [r.__dict__ for r in results]   # the fix plus the trust layer
print("one-line fix:"); show(gate(base, fix), 700)
print("\nfix + trust layer:"); show(gate(base, cand), 700)

# %% [markdown]
# The second change is blocked: scenario 4 failed. Read why before you believe it.

# %%
print(cand[3]["notes"], "\n")
print(cand[3]["turns"][-1]["agent"])

# %% [markdown]
# Ask Rasoi refused Shakti Seals and asked for a "food-grade test report". The check in `scenarios.py` looks for the word
# "certific", so it failed a correct answer. The gate was right to stop the change and make us look; this time the
# *test* was wrong. Fixing a check is a change too: it goes through the same review.

# %% [markdown]
# ### TODO (exercise 5): a latency rule
# Add a rule to the gate: block the change if the candidate's total model seconds grow by more than 50%.
# (Each result has `seconds`.)

# %%
def my_gate(baseline, candidate):
    g = gate(baseline, candidate)
    if SOLUTION:
        sb, sc_ = sum(r["seconds"] for r in baseline), sum(r["seconds"] for r in candidate)
        if sb and sc_ > 1.5 * sb:
            g["ship"], g["reasons"] = False, g["reasons"] + [f"model time grows from {sb:.0f} s to {sc_:.0f} s"]
        g["model_seconds"] = (round(sb, 1), round(sc_, 1))
    return g


show(my_gate(base, cand), 400)

# %% [markdown]
# ## 7 · Failure and recovery: what if it orders twice?
#
# The worst failure is the **lost reply**: Bahi saves the order, and the answer never comes back. The caller sees a
# timeout and cannot tell "never arrived" from "done". We inject exactly that into Bahi's `po_save`.

# %%
from bahi.course.l7.retry import drill, lost_reply

lr = lost_reply()
print("Bahi did:   ", lr["bahi_did"]["rc"], lr["bahi_did"]["msg"], lr["bahi_did"]["data"])
print("Caller saw: ", lr["caller_saw"])
print("Budget PRD-07 committed:", inr(lr['budget_prd07_before']), "->", inr(lr['budget_prd07_after']))
print("Look up by the key", lr["key"], "->", [(r["po_no"], r["status"]) for r in lr["lookup_by_key"]])

# %% [markdown]
# An **idempotency key** is a label made from what the order *is* (a hash of user, supplier, item, quantity, cost
# centre, date), sent with the save. Asked twice, the same order gives the same key, so the second time it is *found*
# instead of written. Never use a random id: a retry would get a new one.
#
# Now the drill: 50 faults (half before the commit, half after), on the three writes of Kavita's job, against four
# clients. Deterministic, no model, about a second.

# %%
d = drill(50)
tab = pd.DataFrame([{"client": k.split("/")[0], **v} for k, v in d["summary"].items() if k.endswith("/all")]).set_index("client")
tab["extra_inr"] = tab["extra_inr"].map(inr)
tab

# %% [markdown]
# On 28 Oct, when we first ran this drill, `keyed_tools` never duplicated, but 16 jobs got stuck halfway: starting the
# job again from the top is not the same as *resuming* it. `keyed_fixed` adds two small fixes (submit a found draft
# request; look the order up by key before refusing a closed request). The toolbox's owner merged both fixes, so in
# the table above `keyed_tools` and `keyed_fixed` now both end with exactly one released order in all 50 trials.
# The first run is kept in `experiments/logs/retry_drill.json`. A job that waits days for Rohit needs
# the same idea at a larger scale: **durable execution**, where every finished step is saved, so a restart resumes
# from the last step instead of starting over.
#
# ## 8 · Cost per conversation
#
# Every model call is paid by the token. The input side dominates: the tool schemas and the whole history are sent
# again on every step.

# %%
card[["scenario", "tokens", "₹", "model s"]].assign(**{"model calls": [sum(1 for s in a.trace if s["kind"] == "model") for a in keep]})

# %%
per_conv = card["₹"].mean()
for n in (40, 200, 1000):
    print(f"{n:5} conversations a day -> about {inr(n * per_conv)} a day, {inr(n * per_conv * 22)} a month (22 working days)")

# %% [markdown]
# ## 9 · Your module (assignment A7)
#
# Take your module kit (`modules/<your_kit>/README.md`) and give it the same trust layer:
#
# 1. Build your toolbox with `ModuleToolbox(erp, user, "<kit>")` bound to the **speaker's own session**, never SVC_AGENT.
# 2. Write a guard for each of your kit's never-events.
# 3. Run your four scenarios as a suite, with code checks on the ERP, three times; add an LLM judge and compare.
# 4. Inject `timeout_after_commit` into your save service and prove a retry finds the document by its key.
#
# The starter for each kit is in `bahi/bahi/modules/<kit>/toolbox/`.

# %%
from bahi.modules._toolbox import ModuleToolbox

erp = ERP(modules=["hr_leave"])
tb = ModuleToolbox(erp, "KJOSHI", "hr_leave")
print(tb.names)
show(tb.call("check_leave_balance", {}), 500)
