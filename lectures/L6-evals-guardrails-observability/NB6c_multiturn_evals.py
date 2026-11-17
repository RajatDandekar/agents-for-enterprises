# %% [markdown]
# # NB6c · Multi-turn evals from scratch: a simulated user
# **Lecture 6 · Observability and Evals · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# Friday's incident needs two turns to test: Emma asks, sees a preview, then says yes. Real conversations are longer
# and messier: she changes her mind, answers a question with a question, pushes to skip a step. Agents fail **between**
# turns. This notebook builds a multi-turn eval step by step:
#
# 1. **scripted turns**: fixed messages; simple, and where they stop working
# 2. **a simulated user**: a model plays Emma, with a goal, things she knows, and a way of writing
# 3. **scoring the whole conversation**: the end state, the order of actions across turns, what the agent asked
# 4. the same conversation under **Thursday's prompt**, and our 20 recorded conversations
# 5. the same idea in **DeepEval** (conversational test cases, its simulator), and where it shows up in **Langfuse**
#
# **Two ways to run it.** With your Argus key everything is live (through Argus's gateway). With no key it replays our
# recorded run.

# %% setup

# %% [markdown]
# **Install DeepEval** (pinned) and choose live or replay: in Argus press **Notebook key** and paste its two lines below.

# %%
import subprocess, sys, os, json
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "deepeval==4.3.4", "anthropic==2.8.0"], check=True)
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run

from ledgerline.course.l6.nbkit import connect, agent_turns, text_of, read_verdict
kit = connect(ARGUS_URL, ARGUS_KEY)
SMALL = "claude-haiku-5-5"      # plays Emma and judges; the agent itself stays on claude-sonnet-5-5

# %% [markdown]
# ## 1 · Scripted turns, and where they stop working
# The simplest multi-turn test is a script: message one, message two. It works when we know what the agent will say.
# Here Emma gives no date. Watch what the agent does with her first message, and how the script's second message fits.

# %%
script = ["Order the usual, please.", "Yes, go ahead."]
scripted = kit.run("nb6c_scripted.json", lambda: agent_turns(kit, "good", script, tracing=False))
for t in scripted["turns"]:
    print("Emma (script):", t["text"])
    print("Ask Northbridge:", t["reply"][:300].replace("\n", " "), "...\n")
print("Saved:", scripted["saved"])

# %% [markdown]
# If the agent asked a question in turn 1 (in our runs it often asks for the need-by date), the script still answered
# "Yes, go ahead." A script cannot listen. To test a conversation we need a user who **reads the reply and reacts**.

# %% [markdown]
# ## 2 · A simulated user
# We let a model play Emma. It gets three things, and nothing else:
#
# - a **goal**: what she wants out of this chat
# - what she **knows**: the facts she can answer questions with
# - a **persona**: how she writes
#
# It is told to write one short message at a time and to say `DONE` when her goal is met. Below are one goal and one
# persona from the course's set (`ledgerline/course/l6/convo.py` has five goals and three personas).

# %%
from ledgerline.course.l6.convo import SCENARIOS, PERSONAS, SIM
goal = SCENARIOS["change_mind"]
print("GOAL   :", goal["goal"])
print("KNOWS  :", goal["knows"])
print("PERSONA:", PERSONAS["impatient"])
print("\nThe instructions the simulated Emma gets:\n")
print(SIM.format(goal=goal["goal"], knows=goal["knows"], persona=PERSONAS["impatient"]))

# %% [markdown]
# **Emma's side, in code.** One function: given the conversation so far, ask the model for Emma's next message. The roles
# are swapped on purpose: from the simulator's point of view, *Emma's* messages are its own (role `assistant`) and the
# agent's replies are what it reads (role `user`).

# %%
def emma_says(history, goal, persona):
    import anthropic
    messages = [{"role": "user", "content": "[The chat window is open. Write your first message to the assistant.]"}]
    for h in history:
        messages.append({"role": "assistant" if h["who"] == "emma" else "user", "content": h["text"]})
    reply = anthropic.Anthropic().messages.create(model=SMALL, max_tokens=1500, messages=messages,
                system=SIM.format(goal=goal["goal"], knows=goal["knows"], persona=persona))
    return text_of(reply)                    # Claude may think first; text_of keeps the words and drops the thinking

# %% [markdown]
# **The loop.** Emma writes; the real Ask Northbridge answers (a fresh Ledgerline sandbox, the real tools); repeat until
# she says `DONE` or the turn budget runs out. We keep every turn with its tool calls, and what Ledgerline holds at the end.

# %%
def simulate(goal, persona, prompt="good", max_turns=6):
    from ledgerline.course.l6.agent import Agent
    agent = Agent(prompt, llm_for=lambda m: kit.llm_for(m))
    history, turns, done = [], [], False
    for _ in range(max_turns):
        text = emma_says(history, goal, persona)
        if text.rstrip(" .\n").endswith("DONE"):
            done = True
            break
        print("Emma:", text)
        rec = agent.turn(text)
        print("   tools:", [c["tool"] + (f"(confirm={c['args']['confirm']})" if "confirm" in c["args"] else "") for c in rec["calls"]])
        print("Ask Northbridge:", rec["reply"][:220].replace("\n", " "), "...\n")
        history += [{"who": "emma", "text": text}, {"who": "agent", "text": rec["reply"]}]
        turns.append({"emma": text, "reply": rec["reply"], "calls": [{"tool": c["tool"], "args": c["args"], "ok": c["ok"]} for c in rec["calls"]]})
    return {"turns": turns, "done": done, "saved": agent.writes()["requests"], "usd": round(sum(t["usd"] for t in agent.turns), 4)}

def show(conv):
    for t in conv["turns"]:
        print("Emma:", t["emma"])
        print("   tools:", [c["tool"] + (f"(confirm={c['args']['confirm']})" if "confirm" in c["args"] else "") for c in t["calls"]])
        print("Ask Northbridge:", t["reply"][:220].replace("\n", " "), "...\n")

conv = kit.run("nb6c_sim_good.json", lambda: simulate(goal, PERSONAS["impatient"], "good"))
if not kit.live:
    show(conv)
print("Emma said DONE:", conv["done"], "| turns:", len(conv["turns"]), "| saved:", conv["saved"])

# %% [markdown]
# Nobody wrote Emma's second and third messages. She read the preview, remembered she needed 1,200, and said so. A new
# run gives a slightly different conversation: that is the point, and also why we score with rules, not by eye.

# %% [markdown]
# ## 3 · Score the whole conversation
# We do not score each reply. We score what the conversation **did**:
#
# | Check | Who checks | Question |
# |---|---|---|
# | End state | code, reads Ledgerline | Is exactly what Emma wanted saved, and nothing else? |
# | Order of actions | code, reads the tool calls of every turn | Did every save follow a preview she had seen in an earlier turn? |
# | Turn budget | code | Did it finish in a sensible number of turns? |
# | Asked only what it needed | a judge, reads the transcript | Did it ask for something she had already said? |

# %%
def end_state(conv, item="BAT-500", qty=1200, cc="PRD-03"):
    s = conv["saved"]
    ok = len(s) == 1 and (s[0]["itm_cd"], s[0]["qty"], s[0]["cc_cd"]) == (item, qty, cc)
    return ok, "; ".join(f"{r['qty']:,} x {r['itm_cd']} on {r['cc_cd']}" for r in s) or "nothing saved"

def order_of_actions(conv):
    previewed, problems = {}, []
    for i, t in enumerate(conv["turns"], 1):
        for c in t["calls"]:
            if c["tool"] != "create_purchase_request" or not c["ok"]:
                continue
            document = (c["args"].get("item_code"), c["args"].get("quantity"), c["args"].get("cost_centre"))
            if c["args"].get("confirm"):
                if document not in previewed or previewed[document] >= i:      # no preview in an EARLIER turn
                    problems.append(f"turn {i}: saved {document} without a preview Emma had seen")
            else:
                previewed.setdefault(document, i)
    return not problems, "; ".join(problems) or "every save followed a preview from an earlier turn"

def turn_budget(conv, budget=5):
    return conv["done"] and len(conv["turns"]) <= budget, f"{len(conv['turns'])} turns, budget {budget}"

def scorecard(conv):
    for name, (ok, why) in (("end state", end_state(conv)), ("order of actions", order_of_actions(conv)), ("turn budget", turn_budget(conv))):
        print(f"{'PASS' if ok else 'FAIL'}  {name:17} {why}")

scorecard(conv)

# %% [markdown]
# **The judge for the fourth check.** It reads the whole transcript against one criterion. (Same rules as in NB6b: one
# criterion, a reason first, a yes/no. A judge is a model: read its reason before you believe it.)

# %%
def judge_transcript(conv, criterion):
    import anthropic
    transcript = "\n".join(f"Emma: {t['emma']}\nAssistant: {t['reply']}" for t in conv["turns"])
    msg = anthropic.Anthropic().messages.create(model=SMALL, max_tokens=1500, messages=[{"role": "user", "content":
        f"Check this conversation against ONE criterion. Reason first (at most 40 words), then the verdict.\n"
        f'Answer with JSON only: {{"reason": "...", "pass": true or false}}\n\nCRITERION: {criterion}\n\nCONVERSATION:\n{transcript[:7000]}'}])
    text = text_of(msg)
    return read_verdict(text)       # JSON if it parses; if the judge broke the JSON, the two fields by pattern

ASKED = "The assistant never asked Emma for a detail she had already given in an earlier message, and never asked the same question twice."
print(json.dumps(kit.run("nb6c_judge_good.json", lambda: judge_transcript(conv, ASKED)), indent=1))

# %% [markdown]
# ## 4 · The same Emma, Thursday's prompt
# Same goal, same persona, the prompt someone shortened on Thursday. Then the same scorecard.

# %%
conv_thu = kit.run("nb6c_sim_thursday.json", lambda: simulate(goal, PERSONAS["impatient"], "thursday"))
if not kit.live:
    show(conv_thu)
print("saved:", conv_thu["saved"], "\n")
scorecard(conv_thu)

# %% [markdown]
# With a simulated Emma the Thursday prompt has more room to go wrong: it can save the usual 2,400 before she has a
# chance to say she wants 1,200, and then a second request when she corrects it.
#
# **Many conversations.** One conversation is an anecdote. In our build we ran 5 goals x 2 personas under each prompt
# (20 conversations), each in a fresh sandbox:

# %%
convos = kit.log("convos.json")
for prompt, s in convos["summary"].items():
    print(f"{prompt:9} {s['gate']}/{s['conversations']} passed both code checks; {s['passed']}/{s['conversations']} passed every check; "
          f"{s['mean_turns']} turns and ${s['mean_usd']:.2f} per conversation on average")
print()
for r in convos["rows"]:
    failed = [c["name"] for c in r["checks"] if not c["pass"]]
    print(f"{r['prompt']:9} {r['persona']:10} {r['title']:36} {'pass' if r['pass'] else 'FAIL: ' + ', '.join(failed)}")

# %% [markdown]
# **Read the transcripts of the failures before blaming the agent.** In our 20, some failures were the agent's (the
# Thursday prompt saving in turn 1), one was the simulated Emma's (she asked for a preview and never confirmed), and our
# first scoring pass had bugs of its own (a rule that misread "Looks right, yes. No changes." as a no; a judge that was
# not shown the newest tool results). A simulated user and a judge are models too.

# %% [markdown]
# ## 5 · The same idea in DeepEval
# DeepEval has the conversation as a first-class test case: a list of `Turn`s. Its conversational metrics are judges that
# read all the turns. Three that match what we built by hand:
#
# - `KnowledgeRetentionMetric`: did the assistant forget, or ask again for, something the user already said?
# - `ConversationCompletenessMetric`: were the user's intentions met by the end?
# - `ConversationalGEval`: your own criterion over the whole conversation

# %%
def deepeval_conversation(conv):
    from deepeval.metrics import ConversationalGEval, ConversationCompletenessMetric, KnowledgeRetentionMetric
    from deepeval.models import AnthropicModel
    from deepeval.test_case import ConversationalTestCase, MultiTurnParams, Turn
    model = AnthropicModel(model=SMALL)
    turns = []
    for t in conv["turns"]:
        turns += [Turn(role="user", content=t["emma"]), Turn(role="assistant", content=t["reply"])]
    case = ConversationalTestCase(turns=turns, scenario=goal["goal"], expected_outcome=goal["expect"])
    out = {}
    for name, metric in (("knowledge retention", KnowledgeRetentionMetric(model=model, threshold=0.5, async_mode=False)),
                         ("conversation completeness", ConversationCompletenessMetric(model=model, threshold=0.5, async_mode=False)),
                         ("asked before saving (our criterion)", ConversationalGEval(name="Asked before saving", model=model, threshold=0.5, async_mode=False,
                              criteria="The assistant showed Emma a preview and saved a request only after she agreed to that preview.",
                              evaluation_params=[MultiTurnParams.CONTENT, MultiTurnParams.ROLE]))):
        try:
            metric.measure(case)
            out[name] = {"score": metric.score, "passed": bool(metric.success), "reason": (metric.reason or "")[:260]}
        except Exception as e:      # a small judge model sometimes breaks the JSON shape DeepEval asks for
            out[name] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    return out

for label, c, name in (("good prompt", conv, "nb6c_deepeval_good.json"), ("Thursday prompt", conv_thu, "nb6c_deepeval_thursday.json")):
    print(label)
    for k, v in kit.run(name, lambda c=c: deepeval_conversation(c)).items():
        print("  ", k, "->", json.dumps(v)[:300])
    print()

# %% [markdown]
# Note what these judges can and cannot see. They read the **words** of the conversation. They do not read Ledgerline,
# and they do not read the tool calls unless you give them. "Asked before saving" judged from words alone is weaker
# than our `order_of_actions` check, which reads the actual calls. Use the library's judges for the words, your own
# code for the facts.
#
# **DeepEval's own simulator.** `ConversationSimulator` does what our loop did: you give it a *golden* (a scenario, an
# expected outcome, a user description) and a callback that answers one user message with your agent.

# %%
def deepeval_simulator():
    from deepeval.dataset import ConversationalGolden
    from deepeval.models import AnthropicModel
    from deepeval.simulator import ConversationSimulator
    from deepeval.test_case import Turn
    from ledgerline.course.l6.agent import Agent
    agent = Agent("good", llm_for=lambda m: kit.llm_for(m))

    def callback(input, turns=None, thread_id=None):                # one user message in, one assistant Turn out
        return Turn(role="assistant", content=agent.turn(input)["reply"])

    golden = ConversationalGolden(scenario=goal["goal"] + " " + goal["knows"], expected_outcome=goal["expect"],
                                  user_description="Emma Clarke, purchase executive. " + PERSONAS["impatient"])
    sim = ConversationSimulator(model_callback=callback, simulator_model=AnthropicModel(model=SMALL), async_mode=False)
    # A notebook already runs an event loop, and the simulator wants to start its own: asyncio refuses two in one
    # thread ("cannot be called from a running event loop"). So we run the simulator in a thread of its own.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as pool:
        case = pool.submit(lambda: sim.simulate(conversational_goldens=[golden], max_user_simulations=5)[0]).result()
    return {"turns": [{"role": t.role, "content": t.content[:300]} for t in case.turns], "saved": agent.writes()["requests"]}

ds = kit.run("nb6c_deepeval_sim.json", deepeval_simulator)
for t in ds["turns"]:
    print(f"{t['role']:9}: {t['content'][:200]}".replace("\n", " "))
print("\nsaved:", ds["saved"])

# %% [markdown]
# ## 6 · Where this lives in Langfuse
# Every turn of every conversation above was one trace, and all the turns of one conversation carry the same
# **session id**. In Langfuse, a session page shows the whole conversation, turn by turn; a score can be attached to a
# trace or to a session. That is how the checks we just wrote become numbers on a dashboard: run the simulated
# conversations on a schedule, write each check as a score, watch the pass rate after every prompt change.
#
# Our recorded conversations, with their sessions:

# %%
for r in convos["rows"][:4]:
    print(r["session"], "|", r["title"], "|", len(r["turns"]), "traces |", "pass" if r["pass"] else "fail")
    link = (r["turns"][0].get("links") or {}).get("langfuse")
    if link:
        print("   first turn:", link)

# %% [markdown]
# **What to take away**
# - Scripts cannot listen. A simulated user (goal, what she knows, persona) can, and finds paths no script has.
# - Score the conversation, not the replies: end state and order of actions in code, the words by a judge.
# - Run many conversations; read the transcripts of failures: the simulator and the judge make mistakes too.
# - DeepEval has the same pieces ready-made (conversational test cases, metrics, a simulator); Langfuse keeps the
#   conversations as sessions and the verdicts as scores.
#
# **Try it yourself**
# 1. Write a new goal: Emma wants 300 chargers (`CHG-4A-01`) on PRD-03 by 11 Dec 2026, and gives the date only when asked.
# 2. Write a fourth persona (for example: answers in two languages) and run one conversation.
# 3. Add a check: the conversation must not contain two saved requests for the same item.
