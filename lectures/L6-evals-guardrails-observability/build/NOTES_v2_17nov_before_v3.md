# Lecture 6 · Observability and Evals · speaker notes (v2, 16 Nov 2026, after the review)

Sat 21 Nov 2026, 2 hours. **103 slides.** Lecture 6 of 11. Slide numbers are the deck's counter (bottom right). `[click]` = one
step. Dr. Rajat Dandekar presents. This version applies Rajat's review of 16 Nov (`REVIEW_16NOV.md`): observability and
evals only, demo first, every idea explained from one live trace, no Phoenix, four notebooks run together. Guardrails and
red-teaming are Lecture 7 (Sun 22 Nov), parked in `../L6b-guardrails/`.

Every number about our own agent is measured, in `experiments/logs/`, and read into the slides by `gen_figdata.py`
(`window.L6` in `figdata.js`); none is typed on a slide. Facts about other tools and the survey are from
`research/TOOLS_RESEARCH.md` and the tools' own documentation (read on 16 Nov; listed in `BUILD_LOG.md`).

## Before class (not on any slide)
1. **Argus, 30 minutes before.** `modal run deploy/argus_modal.py::admin --cmd purge-tests`, then `--cmd warm`, then
   `--cmd status` (expect `backends: langfuse, langsmith, sentry`, spend 0, not paused, `guards_station: false`). Raise the
   class cap if 40 come: `--cmd cap --cap 100`. README: `ledgerline/ledgerline/argus/README.md`.
2. **Check the model key has credit**: in Argus, send one message. If it answers "credit balance is too low", top up the
   Anthropic account behind the Modal secret `forge-anthropic` (this happened on 16 Nov, during the build).
3. **Join Argus once yourself** ("Rajat demo") and keep the tab: slide 11 is live there.
4. **Three tabs, signed in:** LangSmith (project `ask-northbridge`), Langfuse (the course project), Sentry (org `vizuara`,
   project `ask-northbridge`, Explore → Traces). The recorded demo turns, if the live ones misbehave:

| Turn | Trace id | LangSmith (public link, no login) | Langfuse (public link) | Sentry (signed in) |
|---|---|---|---|---|
| Stock question (good prompt) | `b3485cb4c847b08f8ce3d261fd0884a7` | https://smith.langchain.com/public/da67ec38-af45-435b-82dc-a714544bceb4/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/b3485cb4c847b08f8ce3d261fd0884a7 | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3Ab3485cb4c847b08f8ce3d261fd0884a7 |
| The usual, turn 1 (good prompt, preview) | `f1f6b2a2d5194e3c2e1ba7e45d884e2c` | https://smith.langchain.com/public/51c29356-586e-4e59-8d8c-b3dc71732074/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/f1f6b2a2d5194e3c2e1ba7e45d884e2c | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3Af1f6b2a2d5194e3c2e1ba7e45d884e2c |
| The usual, turn 2 (the yes, the save) | `8a660857b02adf9015e0e6a473098156` | https://smith.langchain.com/public/9b1e4898-755f-4bdf-b947-6c88e8b5283d/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/8a660857b02adf9015e0e6a473098156 | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3A8a660857b02adf9015e0e6a473098156 |
| Friday's turn (Thursday prompt, saved without a yes) | `52e91c64814241a0b2bf371722612522` | https://smith.langchain.com/public/5b0ef5a8-97c4-475a-b7e5-68d00063ebef/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/52e91c64814241a0b2bf371722612522 | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3A52e91c64814241a0b2bf371722612522 |

5. **Four Colab tabs**: NB6a, NB6b, NB6c, NB6d (links on slides 29, 61, 77, 89 and 99). Run each first cell before class
   (the install takes about a minute). For live mode: in Argus press **Notebook key**, paste the two lines.
6. **Never redeploy Argus in class.** After class: `--cmd cool`.
7. Refresh the slide numbers any time: `python3 lectures/L6-evals-guardrails-observability/gen_figdata.py`.

**The one idea.** The model decides what to try. Code records what happened (today), and code decides what is allowed
(tomorrow). Say it on slide 8; come back to it on slide 96.

**The rhythm.** Demo first (slide 11), then every idea from that one trace, one idea per slide (12 to 22). Then how the
rows are made (23 to 29, ending in NB6a), then the same turn in LangSmith, Langfuse, Sentry (30 to 40). Part 2 follows the
same pattern: the idea in plain words, our measured result, then a notebook together.

**Plain words.** The audience is not expert. Each term has a one-line meaning on the slide where it first appears (trace 13,
span 14, generation 15, tokens 15 and 17, session 18, score 22, OpenTelemetry 24, eval 47, LLM judge 55, kappa 60, pass^k 65,
simulated user 68, CI 80, reference answer 87). Use the slide's words; do not add jargon.

**Timing.** Opener 8 min · demo and concepts (10 to 22) 22 min · by hand and NB6a (23 to 29) 20 min · three tools (30 to 45)
15 min · evals to pass^k with NB6b (46 to 65) 25 min · multi-turn with NB6c (66 to 78) 20 min · shipping, Ragas, NB6d (79 to 95)
8 min · close 2 min. If short of time, skip 41 to 43, 85, 86, 90, 91, 93 and do NB6d as homework.

**Screens that are still plates.** Slides 11, 35, 37, 38, 40, 78 show a striped plate marked "screenshot pending" where a
signed-in or live capture belongs (Sentry and signed-in Langfuse have no public view; two Argus shots need a live model turn).
Each plate names the file that fills it. In class these are the moments you switch to the live tab anyway.

---

## Opener (slides 1 to 9)

**1 · Title.** The presenter note hides on the first click.

**2 · Where we are.** [click] what we never built [click] two layers today, one tomorrow [click] the agent is unchanged:
`ledgerline/course/l6/agent.py` wraps Lecture 5's Ask Northbridge (same prompt, 26 tools, Emma's memory, `claude-sonnet-5-5`).

**3 · Henrik's letter.** [click]×3, one per question, [click] "start there". Fiction (the course's world). Say now that
question 3 is tomorrow.

**4 · What Emma saw.** A real run (the traced demo turn, `traces_v2.json`). [click]×3. The chat is the same run the class later sees traced in Argus, LangSmith, Langfuse
and Sentry (`m.demo.incident`; before 17 Nov it showed a different recorded run, so the words did not match slide 32).
Point at the request number, PR/2026/04417: a number means a request is already saved. The reply is not a lie: it says it is
waiting for Daniel. It simply saved without asking.

**5 · The Thursday edit.** The diff of the two prompt files. [click] green lines [click] the one line of English that stood
between the agent and a silent save.

**6 · How often.** `incident_r1/r2/r3.json`. Two pairs of bars, each drawn as a share of its own runs (17 Nov: the old
bars drew 3 of 20 as long as 10 of 10). With the date: Thursday 10 of 10 saved without a yes, good 0 of 10. [click] no
date: Thursday 3 of 20, good 0 of 20.
[click] **why nobody caught it on Thursday**: 3 of 20 is 15%, so one try looks fine 85% of the time
[click] the sum: 0.85 × 0.85 × 0.85 = 0.61. Someone who tried the new prompt three times saw three good answers 61% of the time.

**7 · Ask the class.** 30 seconds, answers in chat. Logs have no structure; the audit trail shows the request, not why;
"ask the model" gets a new story.

**8 · Two today, one tomorrow.** [click] evals [click] guardrails tomorrow [click] the rule.

**9 · Map.** Gold cards are what the class does. [click] measured, not claimed; Lecture 7 next.

---

## Part 1 · Observability (slides 10 to 45)

**10 · Part.**

**11 · LIVE: Argus, Traces.** Switch to the Argus tab. Type "How many BAT-500 battery packs do we have?" and let the class
watch the rows arrive. [click] click a pink row, then the orange row [click] "Order the usual, please, needed by 4 Dec
2026.", read the preview, then "Yes, go ahead." [click] switch the prompt to Thursday, send the same message, find the red
row. Under the trace: "Open in LangSmith / Langfuse / Sentry" open the same turn in each tool (LangSmith and Sentry open
the exact trace; all need your signed-in tabs). Do not explain terms yet: the next eleven slides do.

**12 · What we just saw.** The recorded stock question (2026-11-16, `traces_v2.json`). [click] the trace [click] three facts
[click] the definition of observability.

**13 · A trace.** [click] an id [click] a shape [click] a clock [click] definition, then "why not logs".

**14 · A span.** Same picture. [click]×3 start/end, parent, details [click] definition.

**15 · A model call.** The first pink row, opened (`m.demo.ordinary.gen`). [click] what went in: about 7,900 tokens for a
one-line question, because the instructions, memory and tool list go in every time [click] what came out: a request to call
`check_stock`, no words yet [click] cost [click] definition of generation. A token is about three quarters of a word.

**16 · A tool call.** The orange row. [click] arguments [click] result [click] why this row matters most: a tool call
changes something.

**17 · Tokens and cost.** The two model calls of the stock question; [click] the turn [click] Friday's turn: three calls,
about $0.06 [click] three cards. Cost is tokens × our price list (`ledgerline.llm.PRICES`), written
on the span by our code.

**18 · Four labels.** Real values from the root span. [click]×3 [click] definition of session.

**19 · Friday, same picture.** Find mode: [click] tools only [click] the preview [click] the save, in the same turn.
The trace is the 16 Nov recording of the Thursday prompt (`m.demo.incident`): 8 spans, 3 model calls, 4 tool calls
(find_supplier, check_budget, the preview, the save). The counts on the slides are read from the data, so they follow the trace.

**20 · The row that saved it.** [click] arguments: `confirm: true` [click] result: PR/2026/04417, waiting for approval
[click] the two facts.

**21 · What right looks like.** Good prompt. Turn 1: one preview (yellow tag). [click] turn 2: the save (red tag) after her
yes [click] three cards. Same session id on both traces.

**22 · A score.** `scores_v2.json`: one code check, written onto the four demo traces through Langfuse's and LangSmith's
APIs (`experiments/scores_v2.py`, no model). [click] definition [click] the bridge to Part 2.

**23 · By hand.** [click] three records [click] the tree [click] "that is all a tracer does". The class runs this in NB6a
(section 1); the slide has an "Open NB6a in Colab" button, and the whole notebook is run together on slide 29. The ids on the slide are shortened; the times in the notebook come from `time.sleep` calls.

**24 · What it lacks.** A table, not code (Rajat's point about the 16 Nov slide 17). [click] somewhere to send it [click] a
screen [click] OpenTelemetry.

**25 · OpenTelemetry.** [click]×3: SDK → sender → three tools. OTLP is the wire format; an exporter is the sender. We send
to LangSmith, Langfuse and Sentry at once from one process (`course/l6/tracing.py`).

**26 · Agreed names.** Three rows. [click]×2 [click] why names matter [click] status: the guide is "in development".

**27 · Three lines.** The only code slide in Part 1, and it is three lines. [click] what appears; only the keys decide;
we checked (slide 39).
[click] three questions people ask (added 17 Nov). Where do the keys live: in environment variables, never in the code
(our laptop: the course `.env`, git-ignored; Argus: a Modal secret made from that file at deploy time, `deploy/argus_modal.py`;
Colab: the Secrets panel). Why is it automatic: `course/l6/tracing.py` wraps the three places where work happens
(`agent_span`, `wrap_llm`, `tool_span`), so every turn produces spans with no extra code per message; a background sender
posts finished spans to each tool's address with the key in a header (LangSmith: `<endpoint>/otel/v1/traces`, header `x-api-key`).
Argus: one tracer for the whole app, created at start-up, with one sender per tool whose key is present and one in-memory
copy that feeds the trace pane on the right.

**28 · What must not go in.** A real run of our masking function (`redact_demo.json`, Presidio): [click] the card number
is replaced before the span leaves the process [click] how, where, and decide. Presidio labelled the card as a phone
number: right result, wrong label; tomorrow's lecture measures the detector.

**29 · NB6a together (about 20 min).** Open in Colab. Sections: by hand; OpenTelemetry; one real turn and Friday's turn as
trees; send to the tools; the Langfuse tour. Live mode needs the Argus key; with none it replays. The embedded copy is the
notebook as our live run left it.

**30 · Which tools.** Stack Overflow 2026 survey (TOOLS_RESEARCH §0). [click]×3 why Sentry, LangSmith, Langfuse [click]
read with care.

**31 · LangSmith: the stock question.** A public share link, so the screenshot is logged out. [click] right panel [click]
tokens and cost equal ours [click] how it got there: a key and one address; no LangSmith library.

**32 · Friday in LangSmith.** [click] Feedback: `commit_without_yes 1.00`, written by our code [click] the reply reads calm.
If asked "how did the trace get here?": slide 31's last card and slides 25 to 27 (OpenTelemetry sends a copy to LangSmith's
address with our key; NB6a section 4). If asked "how did the feedback get here?": a script ran the code check and wrote
the verdict through LangSmith's API (`experiments/scores_v2.py`, `POST /api/v1/feedback` on the trace's top row); taught on
slides 83 and 84. The feedback shows only while the top row of the tree is selected.

**33 · The save in LangSmith.** [click] output [click] same span, second screen [click] the public link.
The screenshot was retaken on 17 Nov: the first capture caught LangSmith's grey loading placeholders, so Input and Output
looked empty. Live, the panel needs about ten seconds after the click before the fields appear.

**34 · Langfuse.** Header and tree of Friday's trace (public link). [click] the tree [click] how it got there [click] open
source, MIT; free tier keeps traces 30 days.
The last card carries the public link to Friday's trace (added 17 Nov). Logged out it shows the tree, times, costs and the
score; Langfuse does not load Input and Output without a sign-in, so open those yourself, signed in (slide 35).

**35 · Where the time went.** Timeline: the model is almost all of the 11.7 s. [click] **live**: open this trace signed in
and click a generation: Input, Output, Metadata, Scores. (Logged out, Langfuse's public page does not load those two panels,
which is why the 16 Nov deck showed them empty; signed in they are there. The plate on the slide waits for a signed-in capture.)

**36 · Two turns in Langfuse.** [click] turn 2 [click]×2 cards.

**37 · Sentry.** **Live**: Explore → Traces → Friday's trace id (table above). [click]×3. What arrived was read back through
Sentry's API (`readback.json`): all spans, messages, tool arguments and results, tokens.

**38 · Sentry: the save, the agents view.** **Live**: click the last `create_purchase_request` span; then Explore → Agents.
[click] the neighbourhood.

**39 · Sent once, read back.** `experiments/readback.py`: 4 of 4 turns in all three, with input and output; tokens equal
ours in all three; cost equal in LangSmith and Langfuse. [click] three cards. Sentry's first cost was its own estimate
because we had not sent ours; we now send it in Sentry's `gen_ai.cost.*` fields.

**40 · LIVE: the Langfuse tour.** Signed in: Sessions → the longest one; Scores; Datasets → `ask-northbridge-incident`;
Prompts → `ask-northbridge`, version 1 against version 2 (Thursday's edit). [click]×3 the cards [click] the click path.
Numbers on the cards: `nb6a_langfuse_tour.json` (Langfuse's API, 16 Nov).
The click path on the slide is four direct links (17 Nov), in order: Sessions (and the five-turn session
`l6-conv-r2-thursday-impatient-change_mind`), Scores, Datasets, Prompts → ask-northbridge. They open only when you are signed
in to the project; a student who clicks them gets Langfuse's sign-in page.

**41 · Dashboard.** From `online_evals.json`. p50 is the middle turn; p95 the slow end. [click]×2.

**42 · Ask the class.** Pick three numbers.

**43 · In practice.** [click]×5.

**44 · Check.** [click]×3 answers.

**45 · Argus, Traces (about 8 min).** The class tries the good prompt, then Thursday, then opens a turn in a tool.

---

## Part 2 · Evals (slides 46 to 95)

**46 · Part.**

**47 · Vibe check.** [click] why it missed: 61% = 0.85 × 0.85 × 0.85 [click] what an eval adds [click] definition.

**48 · Four parts.** [click]×4.

**49 · Error analysis first.** [click]×3 [click] why first: 58 of 80 runs failed on our first suite, and we read every one.

**50 · What we found.** `error_analysis.json`. [click] the surprise: most failures were the eval's.

**51 · Fix the eval first.** 15/60 → 57/60 with the agent untouched; Thursday 16/20. [click]×2, [click] three cards.

**52 · Three scorers.** [click]×3 [click] the suite.

**53 · The code checks, in plain words.** A table, no code (16 Nov slide 47 was two code blocks). [click] order of actions:
fail, "committed in turn 1" [click] numbers [click] the point: the outcome passed; only the order failed.

**54 · Money: check it with code.** One message (16 Nov slide 48). T14 of the first suite run: the tool returned £342,720;
the reply said £285,600, a figure no tool returned. [click] the reply [click] three cards.

**55 · When do we need a judge?** Rajat's question. Six real criteria from `suite.py`: three for code, [click]×3 three
that only a reader can decide [click] definition.

**56 · The judge's prompt.** Three labelled parts, large (16 Nov slide 50 was unreadable). Real case: T03 under the
Thursday prompt. [click] evidence [click] the reply [click] the verdict: fail, reason first [click]×4 the side cards.

**57 · Judge and code disagree.** One case: T20. [click] the judge passed [click] we opened the trace: the code was wrong
(our record kept only part of each tool result) [click] the rule.

**58 · Is the judge right?** 56 labelled replies. [click]×2 [click] three judges; applies to any judge, a library's too.

**59 · The judge that lies.** κ naive 0.48, specific without evidence 0.01, grounded 0.96. [click]×2 [click] what each teaches.

**60 · DeepEval.** After the judge and its calibration (the order Rajat asked for). [click]×2 [click] our numbers:
ToolCorrectness 28/28; GEval κ 0.73; 15 of 56 GEval calls broke the format on the first try with a small judge.

**61 · NB6b together (about 20 min).** Open in Colab. Until the live run is recorded the left side shows a plate.

**62 · The suite.** 20 tasks × (good ×3, Thursday ×1). [click]×2.

**63 · What Thursday broke.** One row per failing task, full sentences (16 Nov slide 52 had cut-off words). [click] how to
read it: T02, T03 the incident; T10 a judge's objection; T20 our own bug; 16 of 20 still pass.

**64 · The checks are exact; the agent is not.** Rajat's question about pass^k and subjectivity. Twenty runs of one message
under the Thursday prompt: the first five all fine; [click] all twenty: 3 saved without a yes [click] three cards. Nothing
here is a matter of opinion: each tile is code reading Ledgerline.

**65 · pass^k.** [click]×2 the three numbers [click] why it matters [click] cost of k.

**66 · Part: multi-turn evals from scratch.** What the class most wants. Build it in five steps.

**67 · Step 1: scripted turns.** A real run from NB6c (`nb6c_scripted.json`): the agent asked for the date; [click] the
script answered "Yes, go ahead." [click] nothing saved [click] scripts are fine when you know what the agent will say.

**68 · Step 2: a simulated user.** Goal, [click] what she knows, [click] persona, [click] definition; five goals × personas.

**69 · One simulated conversation.** `convos.json`: "Changes her mind", impatient, good prompt. [click]×3.

**70 · Step 3: score the conversation.** The five checks and their verdicts for that conversation. [click] what each reads.

**71 · The same Emma, Thursday's prompt.** It saved 2,400 in turn 1; she corrected it; Ledgerline ends with two requests.
[click]×3.

**72 · Twenty conversations.** Good columns first, [click] Thursday columns and KPIs [click] the reading. Good 7 of 10 on
all five checks (9 of 10 on the code checks); Thursday 3 of 10 (5 of 10).

**73 · Read the failures.** [click] whose fault: the agent's, the simulated Emma's, the judge's.

**74 · Our eval had bugs too.** First scoring pass: good 4 of 10; after fixing the eval only: 7 of 10. [click]×3 the four
bugs [click] the rule. (Logs: `convos_v1.json`, `convo_rescore.py`, `convo_rejudge.py`.)

**75 · Step 4: DeepEval.** The table fills from NB6c's live run (`nb6c_deepeval_*.json`). In the recorded run the
"asked before saving" judge gave Thursday 0.9 and the good run 0.8, and its reason says no save happened, while our
code check found the save in turn 1. Read that reason aloud: it is the point of the slide. (The last line of the slide
is written for this recorded run; if NB6c is re-recorded, re-read it against the table.) [click] the three pieces [click]
they read words, not Ledgerline.

**76 · Step 5: in the tools.** Sessions (Langfuse), threads (LangSmith). [click]×2 [click] the loop teams run.

**77 · NB6c together (about 30 min).** The long one. Do not rush section 2 (the simulated Emma in ten lines).

**78 · Argus, Conversations (about 8 min).** Pick a goal and a persona; watch; read the five checks.

**79 · Two jobs.** Rajat's question: yes, LangSmith and Langfuse do evals as well as traces. [click]×4 the rows [click] in
practice. Sentry: monitoring only.

**80 · The gate.** [click]×4. CI = the checks a code host runs on every proposed change. `ci/test_gate.py`.

**81 · Green.** [click] the first gate run failed on our own over-strict check.

**82 · Red.** [click] T02 and T03, "committed in turn 1".

**83 · Online evals.** Three cards [click]×2, [click] our numbers (`online_evals.json`), [click] the tools can run judges themselves.

**84 · The score in both tools.** Langfuse header; [click] LangSmith feedback; [click] filter, chart, close the loop.

**85 · promptfoo.** [click] the side-by-side view [click] our run.

**86 · The failing cell.** [click]×3.

**87 · Ragas.** Three metrics in plain words. [click]×2 [click] definition [click] reference answers.

**88 · Ragas on our policies.** The tables fill from NB6d's live run (`nb6d_*.json`). [click] planted faults [click]×2 [click] note.
Say this plainly: in the recorded run the two agent metrics got it backwards. The good prompt scored 0 on tool call accuracy
(it previewed twice before saving: three calls against a reference of two) and Thursday's incident scored 1.0 (its calls
match the list; the list has no turns). Goal accuracy, a judge, gave both 0, though the good run reached the goal. The
RAG metrics above behaved (each planted fault moved the right number). Lesson: a library metric is a recipe, not the
truth; the end-state check decides. The card and footnote are written for this recorded run: if NB6d is re-recorded,
re-read them against `nb6d_ragas_agent.json`.

**89 · NB6d together (about 15 min), or homework.**

**90 · Cost.** [click] what the work after the review added.

**91 · Other tools.** [click]×5.

**92 · Ask the class.**

**93 · In practice.** [click]×5.

**94 · Check.** [click]×3.

**95 · Argus, Evals (about 8 min).**

---

## Close (slides 96 to 103)

**96 · Caught twice.** [click] the eval [click] tomorrow: the guard [click] why more than one.

**97 · Reply to Henrik.** [click]×3, [click] what we ask in return.

**98 · Part.**

**99 · Four notebooks.** [click] how the live mode works: Argus's gateway takes the join key in place of a model key.

**100 · Argus, tested.** `argus_api_test.json`, `argus_load_30.json` (16 Nov). [click]×2 [click] three stations.

**101 · A6.** [click]×3. `A6.md`.

**102 · Further reading.**

**103 · Next.** Lecture 7 · Sun 22 Nov 2026 · Guardrails and Red-Teaming.

---

## Sources for facts not measured by us
- Survey shares (slide 30): Stack Overflow Developer Survey 2026, via `research/TOOLS_RESEARCH.md` §0.
- LangSmith: OTLP address, `x-api-key` header, public share links, feedback (LangSmith docs: "Trace with OpenTelemetry",
  "Share a trace", API reference, read 16 Nov 2026).
- Langfuse: OTLP endpoint, scores, datasets, prompts (Langfuse docs and public API). ClickHouse bought Langfuse in Jan 2026
  (TOOLS_RESEARCH §1).
- Sentry: OTLP ingest, agent monitoring, cost from its price table or from `gen_ai.cost.*` (Sentry docs, read 16 Nov 2026).
- DeepEval 4.3.4, Ragas 0.4.4, promptfoo 0.125.1: versions as installed for our runs.
