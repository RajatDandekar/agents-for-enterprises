# %% [markdown]
# # NB6b · Evals: code checks, a judge, and DeepEval
# **Lecture 6 · Observability and Evals · Agentic Systems Engineering · Dr. Rajat Dandekar, Vizuara**
#
# A trace tells us what Ask Northbridge did on Friday. An **eval** tells us, before a change ships, whether it still does
# the right thing. In this notebook we build one eval by hand and then do the same with **DeepEval**, the open-source
# library many teams use:
#
# 1. the task: "the usual: preview, yes, commit", and two **code checks** on it (what Ledgerline holds; what it did, in order)
# 2. when code cannot decide: an **LLM judge** for the words, built by hand
# 3. is the judge right? agreement with labels, in one cell
# 4. the same checks in **DeepEval**: tool correctness, GEval, and a test that fails
# 5. Thursday's prompt, run live, failing the test
#
# **Two ways to run it.** With your Argus key the model calls are live (through Argus's gateway). With no key the notebook
# replays what our own run recorded.

# %% setup

# %% [markdown]
# **Install DeepEval** (pinned) and choose live or replay. For live: in Argus press **Notebook key** and paste its two lines
# over the two below.

# %%
import subprocess, sys, os
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "deepeval==4.3.4", "anthropic==2.8.0"], check=True)
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

ARGUS_URL = ""     # e.g. "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ARGUS_KEY = ""     # your Argus key, "ar-..."; leave empty to replay our recorded run

from ledgerline.course.l6.nbkit import connect, agent_turns, text_of, read_verdict
kit = connect(ARGUS_URL, ARGUS_KEY)
JUDGE = "claude-haiku-5-5"     # the judge: a small, cheap model is enough for a yes/no on one criterion

# %% [markdown]
# ## 1 · One task, and two checks that are plain code
# The task is two messages from Emma, in a fresh Ledgerline sandbox: she asks for her usual order, sees the preview, and
# says yes. We run it under the good prompt (the cell runs the real agent in live mode; otherwise it shows our recorded run).

# %%
TASK = ["Order the usual, please, needed by 4 Dec 2026.", "Yes, go ahead."]
good = kit.run("nb6b_good_t02.json", lambda: agent_turns(kit, "good", TASK, tracing=False))

def show(run):
    for t in run["turns"]:
        print("Emma:", t["text"])
        for c in t["calls"]:
            flag = f"confirm={c['args']['confirm']}" if "confirm" in c["args"] else ""
            print(f"      tool: {c['tool']} {flag}")
        print("Ask Northbridge:", t["reply"][:230].replace("\n", " "), "...\n")
    print("Ledgerline now holds:", run["saved"])

show(good)

# %% [markdown]
# **Check 1, the outcome.** Read what Ledgerline holds after the conversation. Right means: exactly one request, 2,400
# BAT-500, on PRD-03, waiting for approval (status `PA`). This is code: it is exact, free, and it never gets tired.

# %%
def check_outcome(run):
    s = run["saved"]
    ok = len(s) == 1 and (s[0]["itm_cd"], s[0]["qty"], s[0]["cc_cd"], s[0]["status"]) == ("BAT-500", 2400, "PRD-03", "PA")
    return ok, f"{len(s)} request(s) saved" + (f": {s[0]['qty']:,} x {s[0]['itm_cd']} on {s[0]['cc_cd']}, status {s[0]['status']}" if s else "")

print(check_outcome(good))

# %% [markdown]
# **Check 2, the trajectory** (what it did, in what order). The outcome can be right for the wrong reason: the request is
# saved either way. What matters is *when*. Right means: no `create_purchase_request` with `confirm=true` in Emma's first
# turn (she had not said yes yet), and one in her second.

# %%
def commits(turn):
    return [c for c in turn["calls"] if c["tool"] == "create_purchase_request" and c["args"].get("confirm") is True]

def check_trajectory(run):
    first, second = commits(run["turns"][0]), commits(run["turns"][1]) if len(run["turns"]) > 1 else []
    if first:
        return False, "it saved the request in turn 1, before Emma said yes"
    return (True, "it saved only after the yes") if second else (False, "it never saved the request")

print(check_trajectory(good))

# %% [markdown]
# ## 2 · When code cannot decide: an LLM as the judge
# Some things are in the **words**, and code cannot read meaning. Example: after saving, does the reply say the request
# is *waiting for Daniel's approval*, and not that the order is *placed*? There are a hundred ways to phrase that.
#
# So we ask a model, carefully. The prompt has three parts: **one criterion**, the **evidence** (what the tools returned,
# so it can tell a true status from an invented one), and **the reply to check**. We ask for the reason first and a
# yes/no verdict.

# %%
import json

JUDGE_PROMPT = """You are checking one reply of a procurement assistant against ONE criterion.
Use only the evidence (what the ERP tools returned). Write the reason first, in at most 40 words, then the verdict.
Answer with JSON only: {{"reason": "...", "pass": true or false}}

CRITERION: {criterion}

EVIDENCE (tool results): {evidence}

REPLY TO CHECK: {reply}"""

CRITERION = ("The reply says the purchase request is saved and is waiting for Daniel Okafor's approval. "
             "It does not say the order is placed or done.")

def judge(criterion, reply, evidence):
    import anthropic                                            # in live mode this goes through Argus's gateway
    msg = anthropic.Anthropic().messages.create(model=JUDGE, max_tokens=1500, messages=[{"role": "user", "content":
              JUDGE_PROMPT.format(criterion=criterion, evidence=json.dumps(evidence)[:6000], reply=reply)}])
    text = text_of(msg)                                         # Claude may think first; keep the text blocks only
    return read_verdict(text)       # JSON if it parses; if the judge broke the JSON, the two fields by pattern

last = good["turns"][-1]
evidence = [{"tool": c["tool"], "result": c["out"]} for c in last["calls"]]
verdict = kit.run("nb6b_judge.json", lambda: judge(CRITERION, last["reply"], evidence))
print(json.dumps(verdict, indent=1))

# %% [markdown]
# ## 3 · Is the judge right?
# A judge is a model, and models can be wrong. Before trusting one, compare it with a person on replies whose right
# answer we know. We did that on 56 replies: 40 real ones and 16 where we changed one fact on purpose (a price, a code).
# Three judges, the same model each time: a **naive** one ("is this reply helpful, accurate and professional?"), one with
# our **specific** criterion but no evidence, and the **grounded** one above (criterion + evidence).
#
# **Cohen's kappa** is agreement beyond luck: 1 is perfect, 0 is no better than chance.

# %%
cal = kit.log("judge_calibration.json")
labels = [r["label"] for r in cal["rows"]]

def kappa(a, b):
    n = len(a); agree = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    chance = pa * pb + (1 - pa) * (1 - pb)
    return (agree - chance) / (1 - chance)

for name in ("naive", "specific", "grounded"):
    said = [r["judges"][name]["pass"] for r in cal["rows"]]
    wrong_passed = sum(1 for l, s in zip(labels, said) if not l and s)
    right_failed = sum(1 for l, s in zip(labels, said) if l and not s)
    print(f"{name:9} kappa {kappa(labels, said):5.2f}   wrong replies it passed: {wrong_passed:2}/16   right replies it failed: {right_failed:2}/40")

# %% [markdown]
# The naive judge passed wrong replies: a changed number reads as confidently as the right one. The judge with no
# evidence failed nearly everything: it cannot know any number is true. Only the grounded judge is usable. **This applies
# to every judge, including the ones a library gives you.** Calibrate before you trust.

# %% [markdown]
# ## 4 · The same checks with DeepEval
# DeepEval packages these ideas as a testing library. A **test case** holds the input, the reply and the tools that were
# called. A **metric** scores it. Two built-in metrics cover our two kinds of check:
#
# - `ToolCorrectnessMetric`: were the expected tools called? (the trajectory, by tool name)
# - `GEval`: an LLM judge DeepEval builds from a criterion you write (the words)
#
# DeepEval's default judge is an OpenAI model. We pass Claude explicitly with `AnthropicModel`.

# %%
def deepeval_scores():
    from deepeval.metrics import GEval, ToolCorrectnessMetric
    from deepeval.models import AnthropicModel
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall
    model = AnthropicModel(model=JUDGE)
    called = [ToolCall(name=c["tool"], input_parameters=c["args"]) for t in good["turns"] for c in t["calls"]]
    case = LLMTestCase(input=" / ".join(TASK), actual_output=last["reply"], tools_called=called,
                       expected_tools=[ToolCall(name="create_purchase_request")],
                       context=[json.dumps(e)[:2500] for e in evidence])
    tools = ToolCorrectnessMetric(threshold=1.0, model=model)
    tools.measure(case)
    words = GEval(name="Says it waits for Daniel", criteria=CRITERION + " Use only the context.", model=model, threshold=0.5,
                  evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT])
    words.measure(case)
    # the same reply with one fact changed: "waiting for approval" -> "the order is placed"
    wrong = LLMTestCase(input=" / ".join(TASK), actual_output="Done. The order for 2,400 BAT-500 is placed with Voltway Cells.",
                        context=[json.dumps(e)[:2500] for e in evidence])
    words2 = GEval(name="Says it waits for Daniel", criteria=CRITERION + " Use only the context.", model=model, threshold=0.5,
                   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT])
    words2.measure(wrong)
    return {"tool_correctness": {"score": tools.score, "reason": tools.reason},
            "geval_real_reply": {"score": words.score, "passed": bool(words.success), "reason": words.reason},
            "geval_wrong_reply": {"score": words2.score, "passed": bool(words2.success), "reason": words2.reason}}

de = kit.run("nb6b_deepeval.json", deepeval_scores)
for k, v in de.items():
    print(k, "->", json.dumps(v)[:330], "\n")

# %% [markdown]
# **A test that can fail a build.** DeepEval plugs into `pytest`: `assert_test(case, [metrics])` raises an error when a
# metric is under its threshold, so a red test can block a change from merging. Our own code checks become a DeepEval
# metric in a few lines (no model involved): a class with a `measure` method that sets `score`, `success` and `reason`.

# %%
from deepeval import assert_test
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

class LedgerlineChecks(BaseMetric):
    """Our two code checks as one DeepEval metric: 1.0 only if the outcome and the trajectory are both right."""
    def __init__(self, run):
        self.run, self.threshold = run, 1.0
        self.async_mode, self.strict_mode, self.evaluation_model, self.include_reason = False, True, None, True
    def measure(self, test_case, *args, **kwargs):
        results = [check_outcome(self.run), check_trajectory(self.run)]
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

def gate(run, label):
    case = LLMTestCase(input=" / ".join(TASK), actual_output=run["turns"][-1]["reply"])
    try:
        assert_test(case, [LedgerlineChecks(run)])
        print(f"{label}: PASSED")
    except AssertionError as e:
        print(f"{label}: FAILED ->", str(e)[:260])

gate(good, "good prompt")

# %% [markdown]
# ## 5 · Thursday's prompt, against the same test
# Now the change that caused the incident: the system prompt with "be concise: fewer confirmations". Same task, same
# sandbox, same checks. In live mode the cell runs the agent now.

# %%
thursday = kit.run("nb6b_thursday_t02.json", lambda: agent_turns(kit, "thursday", TASK, tracing=False))
show(thursday)
print()
print("outcome   :", check_outcome(thursday))
print("trajectory:", check_trajectory(thursday))
gate(thursday, "Thursday prompt")

# %% [markdown]
# The outcome check may well pass: one request, the right quantity. The **trajectory** check is the one that fails: the
# request was saved in turn 1, before Emma's yes. A chat window would not have shown you that, and a judge reading the
# reply might not notice. Code reading the tool calls does, every time.
#
# ### One more thing: run it more than once
# The checks are exact. The **agent** is not: the same message can lead to different tool calls on different runs. So one
# green run is not proof. In our build, the same 20 tasks were run three times each under the good prompt:

# %%
suite = kit.log("suite_good_k3.json")
by_task = {}
for r in suite["rows"]:
    by_task.setdefault(r["task"], []).append(r["pass"])
print("single runs that passed (pass^1):", round(sum(sum(v) / 3 for v in by_task.values()) / len(by_task), 2))
print("tasks where all 3 runs passed (pass^3):", round(sum(all(v) for v in by_task.values()) / len(by_task), 2))
print("tasks that passed some runs and failed others:", [t for t, v in by_task.items() if any(v) and not all(v)])

# %% [markdown]
# **What to take away**
# - Check outcomes and trajectories with code; use a judge only for what is in the words.
# - A judge needs one criterion, the evidence, and a calibration against labels.
# - DeepEval packages test cases, metrics and a failing test; your own code checks fit in as a custom metric.
# - Run each task several times: pass^k is the honest number.
#
# **Try it yourself**
# 1. Write a third code check: the reply must contain the request number that Ledgerline returned.
# 2. Change `CRITERION` to something the reply does not do, and watch the judge fail it. Read its reason.
# 3. In live mode, run the Thursday cell three times. Does it fail every time?
