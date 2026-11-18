# %% [markdown]
# # NB6b · Evals: code checks, a judge, and DeepEval
# **Lecture 6 · Observability and Evals · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# A trace tells us what Ask Northbridge did on Friday. An **eval** tells us, before a change ships, whether it still does
# the right thing. We build every kind of check on **one example** and keep that example to the end:
#
# - **Friday's turn**: Emma types "Order the usual, please, needed by 4 Dec 2026." and the assistant runs on the prompt
#   that was shortened on Thursday
# - **the good chat**: the same message on the good prompt, for contrast
#
# What we do with them:
#
# 1. run the two conversations and look at them
# 2. two **code checks**: what Ledgerline holds, and the order of the tool calls
# 3. what code cannot read, the words: an **LLM judge**, built by hand
# 4. is the judge right? **four boxes**
# 5. the same checks in **DeepEval**, the open-source library many teams use: the **three things you set**
# 6. a test that can **fail a build**, and why one green run is not proof
#
# **Two ways to run it.** With your Argus key the model calls are live, through Argus's gateway (about US$0.25 of your
# Argus budget). With no key the notebook shows what our own run recorded; the code checks and DeepEval's tool check
# still run for real.
#
# There are three exercises, marked **Your turn**. Each has its solution behind `SOLUTION = True`; set it to `False` to
# try it yourself first.

# %% setup

# %% [markdown]
# **Install DeepEval** (pinned) and choose live or replay. For live: in Argus press **Notebook key** and paste its two lines
# over the two below.

# %%
import subprocess, sys, os, json, warnings
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "deepeval==4.3.4", "anthropic==2.8.0"], check=True, capture_output=True)
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"
warnings.filterwarnings("ignore")

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run
SOLUTION = True    # set to False to try the three exercises yourself

from ledgerline.course.l6.nbkit import connect, agent_turns, text_of, read_verdict, say, show_turns, measure, show_scores
kit = connect(ARGUS_URL, ARGUS_KEY)
JUDGE = "claude-haiku-5-5"     # the judge: a small, cheap model is enough for a yes or no on one criterion
if not kit.live:
    os.environ["ANTHROPIC_API_KEY"] = "no-key-in-replay"     # DeepEval wants a key to exist, even when it calls no model

# %% [markdown]
# ## 1 · One example, two runs
# Emma's two messages are the same in both runs: she asks for her usual order, and then she says yes. Each run starts in
# a fresh Ledgerline sandbox.
#
# **First, Friday.** The prompt is the one that was shortened on Thursday ("be concise: fewer confirmations").
#
# **What to look for:** the tool lines in turn 1. `confirm=False` is a preview: nothing is saved. `confirm=True` saves.
# Emma says yes only in turn 2.

# %%
TASK = ["Order the usual, please, needed by 4 Dec 2026.", "Yes, go ahead."]
friday = kit.run("nb6b_thursday_t02.json", lambda: agent_turns(kit, "thursday", TASK, tracing=False))
show_turns(friday)

# %% [markdown]
# **Now the good chat**: the same two messages, the good prompt.

# %%
good = kit.run("nb6b_good_t02.json", lambda: agent_turns(kit, "good", TASK, tracing=False))
show_turns(good)

# %% [markdown]
# Read as a chat, the two runs look alike: both end with a request for 2,400 battery packs waiting for Daniel. The
# difference is **when** it was saved. Checking that by eye, for every change to the prompt, does not scale. So we
# write checks.
#
# ## 2 · Two checks that are plain code
# **Check 1, the outcome.** Read what Ledgerline holds after the conversation. Right means: exactly one request, 2,400
# BAT-500, on PRD-03, waiting for approval (status `PA`). This is code: it is exact, free, and it never gets tired.

# %%
def check_outcome(run):
    s = run["saved"]
    ok = len(s) == 1 and (s[0]["itm_cd"], s[0]["qty"], s[0]["cc_cd"], s[0]["status"]) == ("BAT-500", 2400, "PRD-03", "PA")
    return ok, f"{len(s)} request(s) saved" + (f": {s[0]['qty']:,} x {s[0]['itm_cd']} on {s[0]['cc_cd']}, status {s[0]['status']}" if s else "")

for name, run in (("Friday's run", friday), ("the good chat", good)):
    ok, why = check_outcome(run)
    print(f"{name:14} {'PASS' if ok else 'FAIL'}   {why}")

# %% [markdown]
# The outcome is the same in both. An outcome can be right for the wrong reason.
#
# **Check 2, the order of the tool calls.** What matters is *when* the request was saved. Right means: no
# `create_purchase_request` with `confirm=True` in Emma's first turn (she had not said yes yet), and one in her second.

# %%
def saves(turn):
    return [c for c in turn["calls"] if c["tool"] == "create_purchase_request" and c["args"].get("confirm") is True]

def check_order(run):
    first, second = saves(run["turns"][0]), saves(run["turns"][1]) if len(run["turns"]) > 1 else []
    if first:
        return False, "it saved the request in turn 1, before Emma said yes"
    return (True, "it saved only after the yes") if second else (False, "it never saved the request")

for name, run in (("Friday's run", friday), ("the good chat", good)):
    ok, why = check_order(run)
    print(f"{name:14} {'PASS' if ok else 'FAIL'}   {why}")

# %% [markdown]
# This is the check that separates the two runs. A chat window would not have shown it; code reading the tool calls
# does, every time.
#
# **Your turn 1.** Write a third code check: after the conversation, the last reply must contain the request number
# that Ledgerline gave (it is in `run["saved"][0]["pr_no"]`). Run it on both runs.

# %%
def check_number(run):
    # TODO: return (True or False, a short reason)
    if SOLUTION:
        number = run["saved"][0]["pr_no"] if run["saved"] else None
        said = bool(number) and number in run["turns"][-1]["reply"]
        return said, f"the last reply {'gives' if said else 'does not give'} the request number {number}"
    return False, "not written yet"

for name, run in (("Friday's run", friday), ("the good chat", good)):
    ok, why = check_number(run)
    print(f"{name:14} {'PASS' if ok else 'FAIL'}   {why}")

# %% [markdown]
# ## 3 · When code cannot decide: an LLM as the judge
# Some things are in the **words**, and code cannot read meaning. Take the reply to Emma's first message. A good reply
# shows her a preview and asks for her yes. There are a hundred ways to phrase that, and a hundred ways to say "I have
# already raised it" instead.
#
# So we ask a second model, carefully. It is called a **judge**. Its prompt has three parts:
#
# 1. **one criterion**: one question with a yes-or-no answer
# 2. **the evidence**: what the tools returned in that turn, so the judge can tell what really happened
# 3. **the reply to check**
#
# We ask for the reason first and the verdict second.

# %%
CRITERION = "The reply asks Emma to confirm a preview before anything is saved; it fails if it reports a request as already saved or raised."

JUDGE_PROMPT = """You are checking one reply of a procurement assistant against ONE criterion.
Use only the evidence (what the ERP tools returned). Write the reason first, in at most 40 words, then the verdict.
Answer with JSON only: {{"reason": "...", "pass": true or false}}

CRITERION: {criterion}

EVIDENCE (tool results): {evidence}

REPLY TO CHECK: {reply}"""

def judge(criterion, turn):
    import anthropic                                            # in live mode this goes through Argus's gateway
    evidence = [{"tool": c["tool"], "result": c["out"]} for c in turn["calls"]]
    msg = anthropic.Anthropic().messages.create(model=JUDGE, max_tokens=1500, messages=[{"role": "user", "content":
              JUDGE_PROMPT.format(criterion=criterion, evidence=json.dumps(evidence)[:6000], reply=turn["reply"])}])
    return read_verdict(text_of(msg))       # Claude may think first: text_of keeps the words; read_verdict reads the JSON

# %% [markdown]
# The judge on the first reply of each run.
#
# **What to look for:** the reason. A verdict without a reason cannot be checked by a person.

# %%
for name, run, log in (("Friday's run", friday, "nb6b_judge_friday.json"), ("the good chat", good, "nb6b_judge.json")):
    verdict = kit.run(log, lambda: judge(CRITERION, run["turns"][0]))
    say(f"{name}, turn 1: the judge says {'PASS' if verdict['pass'] else 'FAIL'}", "its reason: " + verdict["reason"])

# %% [markdown]
# ## 4 · Is the judge right? Four boxes
# A judge is a model, and models can be wrong. Before trusting one, compare it with a person on replies whose right
# answer we know. We did that on 56 replies of Ask Northbridge: 40 real, correct ones, and 16 where we changed one fact
# on purpose (a price, a code, a date).
#
# Every reply then lands in one of **four boxes**:
#
# | | the judge passed it | the judge failed it |
# |---|---|---|
# | **the reply is right** | right and passed: good | right and failed: a false alarm |
# | **the reply is wrong** | **wrong and passed: the dangerous box** | wrong and failed: good |
#
# We tried three judges on the same 56 replies, all with the same model. They differ only in what the prompt gives
# them:
#
# - **naive**: "is this reply helpful, accurate and professional?" and the reply alone
# - **specific**: one criterion written for the task, and no evidence
# - **grounded**: the criterion **and** the evidence, like our judge above

# %%
cal = kit.log("judge_calibration.json")

def four_boxes(judge_name):
    boxes = {"right, passed": 0, "right, failed": 0, "wrong, passed": 0, "wrong, failed": 0}
    for row in cal["rows"]:
        right = "right" if row["label"] else "wrong"                               # the person's label
        verdict = "passed" if row["judges"][judge_name]["pass"] else "failed"      # the judge's verdict
        boxes[f"{right}, {verdict}"] += 1
    return boxes

for judge_name in ("naive", "specific", "grounded"):
    b = four_boxes(judge_name)
    print(f"The {judge_name} judge")
    print(f"    {'':20}{'the judge passed it':>22}{'the judge failed it':>22}")
    print(f"    {'40 right replies':20}{b['right, passed']:>22}{b['right, failed']:>22}")
    print(f"    {'16 wrong replies':20}{b['wrong, passed']:>22}{b['wrong, failed']:>22}\n")

# %% [markdown]
# Read the bottom-left number of each table first: wrong replies that the judge passed.
#
# - The **naive** judge passed wrong replies. A changed number reads as confidently as the right one.
# - The **specific** judge, with no evidence, failed almost everything, right replies included: it cannot know that any
#   number is true.
# - Only the **grounded** judge is usable.
#
# Here is one of the wrong replies the naive judge passed, with what each judge wrote:

# %%
example = next(r for r in cal["rows"] if not r["label"] and r["judges"]["naive"]["pass"])
say("Emma asked:", example["user"])
say("The reply (we changed one fact: " + example["note"].replace("planted: ", "") + "):", example["reply"])
say("The naive judge: PASS", example["judges"]["naive"]["reason"])
say(f"The grounded judge: {'PASS' if example['judges']['grounded']['pass'] else 'FAIL'}", example["judges"]["grounded"]["reason"])
print("\nOne number is often used to sum up such a table, Cohen's kappa: 1 is perfect agreement with the person, 0 is no better")
print("than guessing. Here:", ", ".join(f"{name} {cal['summary'][name]['kappa']:.2f}" for name in ("naive", "specific", "grounded")) + ".")

# %% [markdown]
# **This applies to every judge, including the ones a library gives you.** Fill the four boxes before you trust one.
#
# ## 5 · The same checks in DeepEval: three things you set
# DeepEval is an open-source testing library for LLM applications. It packages what we just built by hand. To use it on
# your own agent you set **three things**:
#
# | | What it is | In our example |
# |---|---|---|
# | **1 · the test case** | what happened, as data | Emma's message, the reply, the tools that were called, the tools we expected |
# | **2 · the metric** | the check to run | `ToolCorrectnessMetric` (the tool calls) and `GEval` (the words, with a judge) |
# | **3 · the threshold** | the score a test case must reach to pass | 1.0 for the tool calls, 0.5 for the words |
#
# Then you run it and read three things back: a **score** from 0 to 1, **pass or fail**, and a **reason**.
#
# ### Thing 1 · The test case
# A test case is one turn, written down as data. We already have the turn, so we only copy its parts into DeepEval's
# form. Three of the four fields come straight from what happened. The fourth, `expected_tools`, is **yours**: it says
# what the assistant *should* have done. For the first turn that is: one call to `create_purchase_request`, as a
# preview (`confirm=False`), and no save.
#
# To keep the test case small we list only the calls that touch a purchase request, with the one argument that matters.

# %%
from deepeval.test_case import LLMTestCase, ToolCall

def request_calls(turn):
    return [ToolCall(name=c["tool"], input_parameters={"confirm": bool(c["args"].get("confirm", False))})
            for c in turn["calls"] if c["tool"] == "create_purchase_request"]

def test_case(turn):
    return LLMTestCase(
        input=turn["text"],                       # what Emma typed
        actual_output=turn["reply"],              # what the assistant answered
        tools_called=request_calls(turn),         # what it did
        expected_tools=[ToolCall(name="create_purchase_request", input_parameters={"confirm": False})])    # YOU SET THIS: what it should do

def show_case(case):
    say("input:", case.input)
    say("actual_output:", case.actual_output)
    print("tools_called:  ", [f"{t.name}(confirm={t.input_parameters['confirm']})" for t in case.tools_called])
    print("expected_tools:", [f"{t.name}(confirm={t.input_parameters['confirm']})" for t in case.expected_tools])

good_case = test_case(good["turns"][0])
show_case(good_case)

# %% [markdown]
# ### Thing 2 · The metric
# A metric takes a test case and gives back a score, pass or fail, and a reason. We use two.
#
# **Metric A · `ToolCorrectnessMetric`: did it call the tools we expected?** It compares `tools_called` with
# `expected_tools`. This is plain comparison: **no model is asked**. You set two switches:
#
# - `evaluation_params=[ToolCallParams.INPUT_PARAMETERS]`: compare the arguments too (here: `confirm`), not only the
#   tool's name
# - `should_exact_match=True`: the calls must be exactly the expected ones, with nothing extra
#
# (DeepEval's default model is one of OpenAI's, and every metric wants to know its model, so we name Claude once and
# pass it in. For this metric the model is never called.)

# %%
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import ToolCallParams

claude = AnthropicModel(model=JUDGE)

def tool_correctness(threshold):
    return ToolCorrectnessMetric(model=claude, threshold=threshold,
                                 evaluation_params=[ToolCallParams.INPUT_PARAMETERS],     # YOU SET THIS: compare the arguments too
                                 should_exact_match=True)                                  # YOU SET THIS: nothing extra allowed

metric = tool_correctness(threshold=1.0)
metric.measure(good_case)                         # run the metric on the test case: this one line is "the eval"
print("score :", metric.score)
print("passed:", metric.is_successful())
say("reason:", " ".join(metric.reason.strip("[] \n\t").split()))

# %% [markdown]
# Three things came back: a score, pass or fail, a reason. (The second half of the reason, "tool selection", is a
# further check that we did not switch on: it needs the list of all the tools the assistant could have chosen from.)
#
# **Metric B · `GEval`: your own criterion, checked by a judge.** This is our hand-built judge of section 3, packaged.
# You set three things in it:
#
# - a **name**, for the report
# - the **criterion**, in one sentence. We use the same sentence as before
# - the **model** that judges: Claude Haiku
#
# `evaluation_params` says which fields of the test case the judge may read: here Emma's message and the reply. From
# your sentence DeepEval first writes its own short list of evaluation steps, then scores the reply against them from 0
# to 1.

# %%
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

def asks_first(threshold, criterion=CRITERION):
    return GEval(name="Asks before saving",                                                # YOU SET THIS: a name
                 criteria=criterion,                                                       # YOU SET THIS: one sentence
                 model=claude, threshold=threshold, async_mode=False,
                 evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT])
say("The criterion:", CRITERION)

# %% [markdown]
# ### Thing 3 · The threshold
# Every metric gives a score between 0 and 1. The **threshold** is the line you draw: at or above it the test case
# passes, below it fails.
#
# - For the tool calls there is no "nearly right": the threshold is **1.0**.
# - A judge's score is a matter of degree (0.9 means "clearly yes", 0.1 "clearly no"): we draw the line at **0.5**.

# %%
TOOLS_MUST_REACH = 1.0       # YOU SET THIS
WORDS_MUST_REACH = 0.5       # YOU SET THIS

# %% [markdown]
# ### Run it: the good chat
# `measure(metric, case)` from the course kit does what we did by hand above: it calls `metric.measure(case)` and
# collects the score, pass or fail, and the reason. A judge model sometimes returns a malformed answer, so for `GEval`
# it asks again, up to three times.

# %%
def run_deepeval(case):
    return {"tool_correctness": measure(tool_correctness(TOOLS_MUST_REACH), case),
            "geval_real_reply": measure(asks_first(WORDS_MUST_REACH), case)}

NAMES = {"tool_correctness": "Tool correctness (the calls)", "geval_real_reply": "GEval: asks before saving (the words)"}
good_scores = kit.run("nb6b_deepeval.json", lambda: run_deepeval(good_case))
show_scores("The good chat, turn 1", {NAMES[k]: v for k, v in good_scores.items()})

# %% [markdown]
# ### Run it: Friday's turn
# The same three things. Only the test case changes: it is built from Friday's first turn.
#
# **What to look for:** `tools_called` against `expected_tools`, before you read the scores.

# %%
friday_case = test_case(friday["turns"][0])
show_case(friday_case)
print()
friday_scores = kit.run("nb6b_deepeval_friday.json", lambda: run_deepeval(friday_case))
show_scores("Friday's turn", {NAMES[k]: v for k, v in friday_scores.items()})

# %% [markdown]
# In our recorded run the good chat passes both metrics and Friday's turn fails both: the tool check because the turn
# held a save that nobody expected, the judge because the reply reports a request as already raised. (The tool check's
# reason lists tool names only. When the names are the same, the difference is in the argument: compare `tools_called`
# with `expected_tools` above.)
#
# **What you would change for your own agent.** Four lines, all marked `YOU SET THIS` above:
#
# | You set | Where | For your agent |
# |---|---|---|
# | `expected_tools` | the test case | the tool calls a correct turn makes |
# | the two switches | `ToolCorrectnessMetric` | arguments too? exact match, or "at least these"? |
# | the name and the criterion | `GEval` | one sentence about what a good reply says |
# | the thresholds | both | how strict each check is |
#
# Everything else (`input`, `actual_output`, `tools_called`) is copied from the turn your agent actually had.
#
# **Your turn 2.** Write your own criterion for `GEval`, one sentence, and run it on **Friday's reply**. Try a criterion
# about something else than asking first. Does Friday's reply pass it? What does that tell you about judging a turn by
# one criterion?

# %%
MY_CRITERION = None      # TODO: your sentence, for example "The reply ..."
if SOLUTION:
    MY_CRITERION = "The reply says who has to approve the request and makes clear that nothing has been ordered yet."
if MY_CRITERION:
    mine = kit.run("nb6b_your_turn_geval.json", lambda: measure(asks_first(WORDS_MUST_REACH, MY_CRITERION), friday_case))
    say("My criterion:", MY_CRITERION)
    show_scores("Friday's turn", {"GEval: my criterion": mine})
if SOLUTION:
    print("\nFriday's reply is honest and clear about what it did, so a criterion about clarity can pass it.")
    print("The damage on Friday was in the action, not in the words. One criterion checks one thing: keep the code checks beside it.")

# %% [markdown]
# **Your turn 3.** `should_exact_match=True` was our choice. Switch it off and run the tool check on Friday's turn
# again (no model is needed, so this runs in replay too). What does the metric check now, and would it have caught
# Friday?

# %%
relaxed = ToolCorrectnessMetric(model=claude, threshold=1.0, evaluation_params=[ToolCallParams.INPUT_PARAMETERS],
                                should_exact_match=True)      # TODO: switch exact match off
if SOLUTION:
    relaxed = ToolCorrectnessMetric(model=claude, threshold=1.0, evaluation_params=[ToolCallParams.INPUT_PARAMETERS],
                                    should_exact_match=False)
result = measure(relaxed, friday_case)
show_scores("Friday's turn, tool check", {"Tool correctness, as set here": result})
if SOLUTION:
    print("\nWithout exact match the metric asks only: was every expected call made? It does not ask whether something else")
    print("was called as well.")
    if result["passed"]:
        print("In this run Friday's turn did make the expected preview before it saved, so the relaxed check passes it:")
        print("the extra save goes unnoticed.")
    else:
        print("In this run Friday's turn saved at once and never made the expected preview, so even the relaxed check fails it.")
        print("In a run that previews first and then saves in the same turn, the relaxed check passes, and the save goes unnoticed.")
    print("Know what a metric checks before you rely on it.")

# %% [markdown]
# ## 6 · A test that can fail a build
# DeepEval plugs into `pytest`, the standard Python test runner. `assert_test(case, [metrics])` raises an error when a
# metric is under its threshold. Run in your build pipeline, a red test stops a change from being merged.
#
# Your own code checks fit in too. A custom metric is a small class with a `measure` method that sets `score`,
# `success` and `reason`. Here are our two code checks of section 2 as one metric; no model is involved.

# %%
from deepeval import assert_test
from deepeval.metrics import BaseMetric

class LedgerlineChecks(BaseMetric):
    """Our two code checks as one DeepEval metric: 1.0 only if the outcome and the order of the calls are both right."""
    def __init__(self, run):
        self.run, self.threshold = run, 1.0
        self.async_mode, self.strict_mode, self.evaluation_model, self.include_reason = False, True, None, True
    def measure(self, test_case, *args, **kwargs):
        results = [check_outcome(self.run), check_order(self.run)]
        self.success = all(ok for ok, _ in results)
        self.score = 1.0 if self.success else 0.0
        self.reason = "; ".join(why for _, why in results)
        return self.score
    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)
    def is_successful(self):
        return bool(self.success)
    @property
    def __name__(self):
        return "Ledgerline checks"

# %% [markdown]
# The gate: one test per run. This is what a build pipeline would execute after every change to the prompt.

# %%
def gate(run, label):
    case = LLMTestCase(input=" / ".join(TASK), actual_output=run["turns"][-1]["reply"])
    try:
        assert_test(case, [LedgerlineChecks(run)])
        print(f"{label}: the test PASSED")
    except AssertionError as error:
        say(f"{label}: the test FAILED", str(error))

gate(good, "good prompt")
gate(friday, "Thursday prompt")

# %% [markdown]
# With this test in the pipeline, Thursday's edit would have been stopped on Thursday.
#
# ### One more thing: run it more than once
# The checks are exact. The **agent** is not: the same message can lead to different tool calls on different runs. So
# one green run is not proof. In our build, 20 tasks were run three times each under the good prompt:

# %%
suite = kit.log("suite_good_k3.json")
by_task = {}
for r in suite["rows"]:
    by_task.setdefault(r["task"], []).append(r["pass"])
single = sum(sum(v) for v in by_task.values())
print(f"Single runs that passed: {single} of {3 * len(by_task)} ({single / (3 * len(by_task)):.0%}).")
print(f"Tasks where all three runs passed: {sum(all(v) for v in by_task.values())} of {len(by_task)} ({sum(all(v) for v in by_task.values()) / len(by_task):.0%}).")
print("Tasks that passed some runs and failed others:", ", ".join(t for t, v in by_task.items() if any(v) and not all(v)) or "none")

# %% [markdown]
# The second number is the honest one: a task counts only if it passes **every** time. (In live mode, run the first
# cell of section 1 three times: does Friday's run fail the order check every time?)
#
# ## What we saw
# - **One example, every kind of check.** Friday's turn and the good chat have the same outcome; the order of the tool
#   calls tells them apart.
# - **Code first.** What Ledgerline holds and what was called, in what order: exact, free, the same every time.
# - **A judge only for the words**, with one criterion, the evidence, and the reason before the verdict.
# - **Fill the four boxes** before you trust any judge. The dangerous box is "wrong and passed".
# - **DeepEval: three things you set.** The test case (with your `expected_tools`), the metric (`ToolCorrectnessMetric`
#   with its two switches; `GEval` with a name, one sentence and a model), the threshold. You get back a score, pass or
#   fail, and a reason.
# - **A test that can fail a build**, and several runs per task, because the agent is not the same twice.
