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
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "deepeval==4.3.4", "anthropic==2.8.0"], check=True, capture_output=True)
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run

from ledgerline.course.l6.nbkit import connect, agent_turns, text_of, read_verdict, say, measure, show_scores
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
# ## 5 · The same idea in DeepEval: three things you set
# DeepEval, the testing library of NB6b, can score a whole conversation as well. As for a single turn, you set
# **three things**:
#
# | | What it is | Here |
# |---|---|---|
# | **1 · the test case** | what happened, as data | the conversation as a list of turns: who spoke, and what they said |
# | **2 · the metric** | the check to run | two ready-made judges and one with our own criterion |
# | **3 · the threshold** | the score the conversation must reach to pass | 0.5 for each |
#
# You get back, for each metric, a **score** from 0 to 1, **pass or fail**, and a **reason**.
#
# ### Thing 1 · The test case
# We already have the conversation (`conv`, from section 2). A conversational test case is its turns, copied into
# DeepEval's form: a `Turn` has a `role` (`user` or `assistant`) and a `content`. Two optional fields are **yours**: the
# `scenario` (what the user was trying to do) and the `expected_outcome`. We take both from Emma's goal.

# %%
from deepeval.test_case import ConversationalTestCase, Turn

def conversation_case(conv):
    turns = []
    for t in conv["turns"]:
        turns += [Turn(role="user", content=t["emma"]), Turn(role="assistant", content=t["reply"])]
    return ConversationalTestCase(turns=turns,
                                  scenario=goal["goal"],                 # YOU SET THIS: what the user was trying to do
                                  expected_outcome=goal["expect"])       # YOU SET THIS: how it should end

good_case = conversation_case(conv)
print(f"{len(good_case.turns)} turns:", ", ".join(t.role for t in good_case.turns))
say("scenario:", good_case.scenario)
say("expected_outcome:", good_case.expected_outcome)

# %% [markdown]
# ### Thing 2 · The metrics
# All three are **judges**: a model reads every turn and answers one question. Two come ready-made, the third is built
# from a sentence we write.
#
# | Metric | The question it asks |
# |---|---|
# | `KnowledgeRetentionMetric` | Did the assistant forget, or ask again for, something the user had already said? |
# | `ConversationCompletenessMetric` | Were the things the user wanted met by the end? |
# | `ConversationalGEval` | **Your own criterion**, in one sentence, over the whole conversation |
#
# What you set: the model that judges (Claude Haiku; DeepEval's default is one of OpenAI's) and, for the third metric,
# a name and the criterion. `evaluation_params` says what the judge may read: what was said, and by whom.

# %%
OUR_CRITERION = "The assistant showed Emma a preview and saved a request only after she agreed to that preview."     # YOU SET THIS

def conversation_metrics(threshold):
    from deepeval.metrics import ConversationalGEval, ConversationCompletenessMetric, KnowledgeRetentionMetric
    from deepeval.models import AnthropicModel
    from deepeval.test_case import MultiTurnParams
    claude = AnthropicModel(model=SMALL)
    return {
        "knowledge retention": KnowledgeRetentionMetric(model=claude, threshold=threshold, async_mode=False),
        "conversation completeness": ConversationCompletenessMetric(model=claude, threshold=threshold, async_mode=False),
        "asked before saving (our criterion)": ConversationalGEval(name="Asked before saving", criteria=OUR_CRITERION,
                                                                   model=claude, threshold=threshold, async_mode=False,
                                                                   evaluation_params=[MultiTurnParams.CONTENT, MultiTurnParams.ROLE]),
    }

# %% [markdown]
# ### Thing 3 · The threshold
# Each judge gives a score between 0 and 1. At or above the threshold the conversation passes that metric.

# %%
MUST_REACH = 0.5       # YOU SET THIS

# %% [markdown]
# ### Run it: the good conversation
# `measure(metric, case)` from the course kit calls `metric.measure(case)` and collects the score, pass or fail, and the
# reason. A small judge model sometimes returns a malformed answer, so it asks again, up to three times. Each of these
# judges reads the whole conversation, so the cell takes about a minute live.

# %%
def run_deepeval(conv):
    case = conversation_case(conv)
    return {name: measure(metric, case) for name, metric in conversation_metrics(MUST_REACH).items()}

good_scores = kit.run("nb6c_deepeval_good.json", lambda: run_deepeval(conv))
show_scores("The good conversation", good_scores)

# %% [markdown]
# ### Run it: Thursday's conversation
# The same three things. Only the test case changes: it is built from `conv_thu`, the conversation under Thursday's
# prompt.

# %%
thu_scores = kit.run("nb6c_deepeval_thursday.json", lambda: run_deepeval(conv_thu))
show_scores("Thursday's conversation", thu_scores)

# %% [markdown]
# Now put the third judge beside the code check we wrote in section 3. Both ask the same question about Thursday's
# conversation: was the request saved only after Emma had seen a preview and agreed?

# %%
ours = thu_scores["asked before saving (our criterion)"]
ok, why = order_of_actions(conv_thu)
print(f"DeepEval's judge, reading the words:   {'PASS' if ours['passed'] else 'FAIL'}" + (f" (score {ours['score']:.2f})" if ours.get("score") is not None else ""))
print(f"Our code check, reading the tool calls: {'PASS' if ok else 'FAIL'} ({why})")

# %% [markdown]
# Note what these judges can and cannot see. They read the **words** of the conversation. They do not read Ledgerline,
# and they do not read the tool calls unless you give them. If the two lines above disagree, believe the code: it read
# what was actually called, in which turn. Use the library's judges for the words, your own code for the facts.
#
# **What you would change for your own agent:** the two optional fields of the test case, the sentence in
# `OUR_CRITERION`, and the threshold. The turns are copied from the conversation your agent actually had.
#
# **DeepEval's own simulator.** `ConversationSimulator` does what our loop of section 2 did: you give it a *golden* (a
# scenario, an expected outcome, a description of the user) and a function that answers one user message with your
# agent. It then plays the user.

# %%
def deepeval_simulator():
    from deepeval.dataset import ConversationalGolden
    from deepeval.models import AnthropicModel
    from deepeval.simulator import ConversationSimulator
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
    return {"turns": [{"role": t.role, "content": t.content} for t in case.turns], "saved": agent.writes()["requests"]}

ds = kit.run("nb6c_deepeval_sim.json", deepeval_simulator)
for t in ds["turns"]:
    say("Emma (DeepEval's simulator):" if t["role"] == "user" else "Ask Northbridge:", t["content"])
print("\nLedgerline now holds:", "; ".join(f"{r['qty']:,} x {r['itm_cd']} on {r['cc_cd']} (status {r['status']})" for r in ds["saved"]) or "nothing new")

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
# - DeepEval has the same pieces ready-made. You set three things: the conversational test case, the metrics (two
#   ready-made judges, one with your own sentence) and the threshold. Langfuse keeps the conversations as sessions and
#   the verdicts as scores.
#
# **Try it yourself**
# 1. Write a new goal: Emma wants 300 chargers (`CHG-4A-01`) on PRD-03 by 11 Dec 2026, and gives the date only when asked.
# 2. Write a fourth persona (for example: answers in two languages) and run one conversation.
# 3. Add a check: the conversation must not contain two saved requests for the same item.
