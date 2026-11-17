# %% [markdown]
# # NB6d · Ragas: scoring the search behind the answer, and the agent
# **Lecture 6 · Observability and Evals · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# When Ask Northbridge answers a question about a rule, it first **searches** the company's policies (Lecture 3), then
# writes an answer from the clauses it found. Two things can go wrong, and they need different fixes:
#
# - the **search** brought back the wrong clauses, or missed the right one
# - the **answer** says something the clauses do not say
#
# **Ragas** is an open-source library of ready-made metrics for exactly this, plus a few for agents. In this notebook:
#
# 1. four policy questions: search, answer, and a reference answer written by a person
# 2. three Ragas metrics on them: **faithfulness**, **context precision**, **context recall**
# 3. break the answer, then break the search, and watch which metric moves
# 4. two agent metrics on a real two-turn chat: **tool call accuracy** and **goal accuracy**
#
# The judge inside every metric is Claude (the small model). **Two ways to run it:** with your Argus key everything is
# live through Argus's gateway; with no key it replays our recorded run.

# %% setup

# %% [markdown]
# **Install Ragas** (pinned) and choose live or replay: in Argus press **Notebook key** and paste its two lines below.

# %%
import subprocess, sys, os, json
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ragas==0.4.4", "langchain-anthropic==1.7.10", "anthropic==2.8.0"], check=True)
os.environ["RAGAS_DO_NOT_TRACK"] = "true"

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run

from ledgerline.course.l6.nbkit import connect, agent_turns, text_of
kit = connect(ARGUS_URL, ARGUS_KEY)
SMALL = "claude-haiku-5-5"

# %% [markdown]
# ## 1 · Four questions, with reference answers
# A **reference** is the right answer, written by someone who knows the policy. Writing references is the slow, human
# part of evaluating search; four are enough to see how the metrics behave.

# %%
QUESTIONS = [
    {"question": "Up to what order value can a purchase executive approve on their own, and who approves above that?",
     "reference": "A purchase executive may approve orders up to £250,000 gross, including VAT. Above that the order goes to the purchase manager, whose limit is £1,000,000."},
    {"question": "Can we order battery packs from a supplier that has no UN 38.3 certificate on file?",
     "reference": "No. Lithium-cell parts such as battery packs, hub motors and chargers may only be ordered from a supplier with a valid UN 38.3 certificate on file before the first order."},
    {"question": "What happens to an order that is charged to a closed cost centre?",
     "reference": "Ledgerline does not refuse it. The order is saved as Draft with warning W-CC-114 and nothing is sent to anyone."},
    {"question": "How recent must a supplier's UN 38.3 certificate be?",
     "reference": "Under amendment AMD-SUP-2026-02 the certificate must have been issued within the last 12 months and be valid for at least 60 days after the order date. This replaces the earlier 24-month rule."},
]
for q in QUESTIONS:
    print("Q:", q["question"], "\n   reference:", q["reference"], "\n")

# %% [markdown]
# **Search, then answer.** For each question we call the same policy search Ask Northbridge uses, keep the clauses it
# returns (the **retrieved contexts**), and ask the small model to answer from those clauses only.

# %%
def search_and_answer():
    import anthropic
    from ledgerline.agent.retrieval import search_policy
    rows = []
    for q in QUESTIONS:
        found = search_policy(q["question"])
        contexts = [f"[{c['cite']}] {c['heading']}: {c['text']}" + ("" if c["status"] == "in force" else f" (STATUS: {c['status']})")
                    for c in found["clauses"]]
        msg = anthropic.Anthropic().messages.create(model=SMALL, max_tokens=1500, messages=[{"role": "user", "content":
            "Answer the question in at most three sentences, using ONLY these clauses. Cite the clause you used.\n\n"
            + "\n\n".join(contexts) + "\n\nQUESTION: " + q["question"]}])
        rows.append({**q, "contexts": contexts, "answer": text_of(msg)})
    return rows

rows = kit.run("nb6d_rag.json", search_and_answer)
for r in rows:
    print("Q:", r["question"])
    print("   found:", [c.split("]")[0][1:] for c in r["contexts"]])
    print("   answer:", r["answer"].replace("\n", " ")[:300], "\n")

# %% [markdown]
# ## 2 · Three Ragas metrics
# | Metric | It reads | Question it answers | Low score means |
# |---|---|---|---|
# | **Faithfulness** | answer + clauses found | Is every claim in the answer supported by the clauses? | the model made something up |
# | **Context precision** | clauses found + reference | Are the useful clauses at the top of the list? | search returns noise first |
# | **Context recall** | clauses found + reference | Do the clauses contain everything the reference says? | search missed a clause |
#
# Each metric is a judge with a fixed recipe. Faithfulness, for example, splits the answer into single claims and
# asks, for each claim, "can this be inferred from the clauses?". The score is the share of claims that pass.
#
# Ragas calls its judge through LangChain. We hand it Claude (the small model), sent through the same gateway.

# %%
def wait(coroutine):
    """Ragas metrics are async. This runs one to the end, in a notebook or in a script."""
    import asyncio, concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        return pool.submit(asyncio.run, coroutine).result()

def ragas_judge():
    import warnings
    warnings.filterwarnings("ignore")
    from langchain_anthropic import ChatAnthropic
    from ragas.llms import LangchainLLMWrapper
    return LangchainLLMWrapper(ChatAnthropic(model=SMALL, max_tokens=3000, base_url=os.environ["ANTHROPIC_BASE_URL"],
                                             api_key=os.environ["ANTHROPIC_API_KEY"]))

def ragas_rag(rows):
    from ragas.dataset_schema import SingleTurnSample
    from ragas.metrics import Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall
    llm = ragas_judge()
    out = []
    for r in rows:
        sample = SingleTurnSample(user_input=r["question"], response=r["answer"], retrieved_contexts=r["contexts"], reference=r["reference"])
        scores = {}
        for name, metric in (("faithfulness", Faithfulness(llm=llm)), ("context_precision", LLMContextPrecisionWithReference(llm=llm)),
                             ("context_recall", LLMContextRecall(llm=llm))):
            try:
                scores[name] = round(float(wait(metric.single_turn_ascore(sample))), 2)
            except Exception as e:
                scores[name] = None
                scores[name + "_error"] = f"{type(e).__name__}: {str(e)[:160]}"
        out.append({"question": r["question"], **scores})
    return out

def table(scores):
    print(f"{'question':64} {'faithful':>9} {'precision':>10} {'recall':>7}")
    for s in scores:
        print(f"{s['question'][:62]:64} {str(s['faithfulness']):>9} {str(s['context_precision']):>10} {str(s['context_recall']):>7}")

scores = kit.run("nb6d_ragas_rag.json", lambda: ragas_rag(rows))
table(scores)

# %% [markdown]
# Read the table across. A row with high recall and low precision means the right clause was found but sits under
# noise. A row with high precision and recall but low faithfulness means search did its job and the *answer* went
# beyond the clauses. The three numbers tell you **which half to fix**.

# %% [markdown]
# ## 3 · Break it on purpose
# A metric is only worth keeping if it moves when the thing it measures breaks. Two planted faults on question 1:
#
# - **a wrong answer**, with the clauses untouched: the limit is stated as £500,000
# - **a broken search**, with the answer untouched: the clauses are replaced by ones about something else

# %%
def ragas_broken(rows):
    wrong_answer = {**rows[0], "answer": "A purchase executive may approve orders up to £500,000. Above that the finance director approves."}
    wrong_search = {**rows[0], "contexts": rows[2]["contexts"]}         # the clauses found for the closed-cost-centre question
    return {"as it was": ragas_rag([rows[0]])[0], "wrong answer": ragas_rag([wrong_answer])[0], "wrong search": ragas_rag([wrong_search])[0]}

broken = kit.run("nb6d_ragas_broken.json", lambda: ragas_broken(rows))
print(f"{'':14} {'faithful':>9} {'precision':>10} {'recall':>7}")
for k, s in broken.items():
    print(f"{k:14} {str(s['faithfulness']):>9} {str(s['context_precision']):>10} {str(s['context_recall']):>7}")

# %% [markdown]
# The wrong answer should pull **faithfulness** down and leave the two search metrics alone; the wrong search should
# pull **precision and recall** down. If a metric does not move on a planted fault, do not trust it on a real one.

# %% [markdown]
# ## 4 · Two metrics for the agent
# Ragas also scores a whole agent conversation, given as a list of messages: what the user said, which tools the
# assistant called, what the tools returned, what the assistant replied.
#
# - **Tool call accuracy** (code, no judge): do the tool calls match a reference list of calls, in order, with the same arguments?
# - **Agent goal accuracy** (a judge): reading the conversation, was the goal in the reference reached?
#
# We run the two-turn order under the good prompt and under Thursday's prompt.

# %%
TURNS = ["Order the usual, please, needed by 4 Dec 2026.", "Yes, go ahead."]
good = kit.run("nb6d_agent_good.json", lambda: agent_turns(kit, "good", TURNS, tracing=False))
thursday = kit.run("nb6d_agent_thursday.json", lambda: agent_turns(kit, "thursday", TURNS, tracing=False))
for label, run in (("good", good), ("Thursday", thursday)):
    print(label)
    for i, t in enumerate(run["turns"], 1):
        print(f"   turn {i}:", [c["tool"] + (f"(confirm={c['args']['confirm']})" if "confirm" in c["args"] else "") for c in t["calls"]])

# %% [markdown]
# **The reference.** Lookups can differ from run to run (stock first or supplier first), and that is fine. What must
# not differ is the part that changes Ledgerline: **one preview, then one save**, for the same document. So we compare
# only the `create_purchase_request` calls, and only the arguments that matter.

# %%
def as_ragas(run, only=None):
    from ragas.messages import AIMessage, HumanMessage, ToolCall, ToolMessage
    messages = []
    for t in run["turns"]:
        messages.append(HumanMessage(content=t["text"]))
        calls = [c for c in t["calls"] if only is None or c["tool"] in only]
        if calls:
            messages.append(AIMessage(content="", tool_calls=[ToolCall(name=c["tool"], args={k: v for k, v in c["args"].items() if v is not None}) for c in calls]))
            for c in calls:
                messages.append(ToolMessage(content=json.dumps(c.get("out"), default=str)[:1200]))
        messages.append(AIMessage(content=t["reply"]))
    return messages

def ragas_agent(run):
    from ragas.dataset_schema import MultiTurnSample
    from ragas.messages import ToolCall
    from ragas.metrics import AgentGoalAccuracyWithReference, ToolCallAccuracy
    document = {"item_code": "BAT-500", "quantity": 2400, "cost_centre": "PRD-03"}
    reference_calls = [ToolCall(name="create_purchase_request", args={**document, "confirm": False}),
                       ToolCall(name="create_purchase_request", args={**document, "confirm": True})]
    writes_only = MultiTurnSample(user_input=as_ragas(run, only={"create_purchase_request"}), reference_tool_calls=reference_calls)
    everything = MultiTurnSample(user_input=as_ragas(run), reference="Emma was shown a preview of the purchase request for 2,400 BAT-500 "
                                 "on PRD-03 first, and the request was saved only after she said yes to that preview.")
    out = {}
    for name, coroutine in (("tool_call_accuracy", ToolCallAccuracy().multi_turn_ascore(writes_only)),
                            ("agent_goal_accuracy", AgentGoalAccuracyWithReference(llm=ragas_judge()).multi_turn_ascore(everything))):
        try:
            out[name] = round(float(wait(coroutine)), 2)
        except Exception as e:
            out[name] = None
            out[name + "_error"] = f"{type(e).__name__}: {str(e)[:160]}"
    return out

agent_scores = kit.run("nb6d_ragas_agent.json", lambda: {"good": ragas_agent(good), "thursday": ragas_agent(thursday)})
for k, v in agent_scores.items():
    print(f"{k:9}", v)

# %% [markdown]
# **Read these two numbers with care.** They change from run to run, because the agent's tool calls change.
#
# - **Tool call accuracy is an exact match of the whole list.** If the assistant shows the preview twice before it saves (which is allowed), there are three calls against a reference of two, and the score is 0. In our recorded run that happened to the good prompt: 0.0.
# - **It does not know where a turn ends.** Thursday's run previewed and saved inside turn 1, before Emma said yes. The list of calls still looks like the reference, so it scored 1.0 in our recorded run: the incident scored higher than the correct run.
# - **Agent goal accuracy is a judge.** In our recorded run it gave both runs 0, including the good one, which did reach the goal. A judge has to be checked against labels before you trust it (NB6b, section 3).
#
# This is why the end-state check decides. It reads Ledgerline, and it knows in which turn each call was made.

# %% [markdown]
# **What to take away**
# - Search-then-answer has two halves. Context precision and recall score the search; faithfulness scores the answer.
# - Every Ragas metric is a judge with a fixed recipe (or plain code, for tool call accuracy). Plant a fault and check it moves.
# - Tool call accuracy is an exact match against a reference list: compare the calls that matter, not every lookup.
# - Ragas gives numbers per sample. It does not read Ledgerline: the end-state check from NB6b and NB6c still decides.
#
# **Try it yourself**
# 1. Add a fifth question whose answer is **not** in the policies (for example, the canteen's opening hours). What do the three metrics say?
# 2. Give the search a worse question (two words) and watch context recall.
# 3. Change the reference in section 4 to demand a need-by date of 4 Dec 2026 in the saved request, and add it to the reference calls.
