# Lecture 6 · Observability and Evals · speaker notes (v3, 17 Nov 2026, after the second review)

Sat 21 Nov 2026, 2 hours. **106 slides.** Lecture 6 of 11. Slide numbers are the deck's counter (bottom right). `[click]` = one
step. Dr. Rajat Dandekar presents. This version applies Rajat's review of 16 Nov (`REVIEW_16NOV.md`): observability and
evals only, demo first, every idea explained from one live trace, no Phoenix, four notebooks run together. Guardrails and
red-teaming are Lecture 7 (Sun 22 Nov), in `../L6b-guardrails/`.

**History.** v1, 16 Nov (parked in `build/`). v2, 16 Nov evening: Rajat's first review. 17 Nov, morning: small fixes after
a reading pass (the lines below marked "17 Nov": the chat of slide 4, the bars of slide 6, the LangSmith retake, the public
links). **17 Nov, afternoon: Rajat's second review (`REVIEW_17NOV.md`).** The evals part now runs on one example: Friday's
turn ("Order the usual, please, needed by 4 Dec 2026." under the Thursday prompt) and the good two-turn chat. Slides 52 to
62 were rewritten around it, each with a marker "Live in Argus · Evals → ..." naming the panel where you show it; the four
boxes replaced the agreement formula; DeepEval is "three things you set" (slides 62 and 77); old slide 76 was cut; three
slides are new (60 two judges live, 81 a trace becomes a score, 98 the loop); slide 87 links promptfoo's own report.
Old → new numbers: 1 to 52 unchanged · 53 → 53 and 54 · 54 to 58 → 55 to 59 · 59 to 75 → 61 to 77 · 76 cut ·
77 to 79 → 78 to 80 · 80 to 95 → 82 to 97 · 96 to 103 → 99 to 106. The v2 deck and notes as they stood before this review
are `build/index_v2_17nov_before_v3.html` and `build/NOTES_v2_17nov_before_v3.md`.

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
   project `ask-northbridge`, Explore → Traces). The recorded demo turns, if the live ones misbehave
   (ids and links from `traces_v2.json` and `readback.json`, the recording of 16 Nov 15:12 UTC that every slide and picture shows;
   corrected on 17 Nov, the table had still listed an earlier recording):

| Turn | Trace id | LangSmith (public link, no login) | Langfuse (public link) | Sentry (signed in) |
|---|---|---|---|---|
| Stock question (good prompt) | `a1f21801f7a091b56eaabd96c6b309ca` | https://smith.langchain.com/public/c23a30d2-2579-4f42-8774-0f9e0ba19b75/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/a1f21801f7a091b56eaabd96c6b309ca | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3Aa1f21801f7a091b56eaabd96c6b309ca |
| The usual, turn 1 (good prompt, preview) | `46aa6a511b909dd4fe2cc95e83539df3` | https://smith.langchain.com/public/0192048f-cf9f-4021-b5e7-14b26784dfba/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/46aa6a511b909dd4fe2cc95e83539df3 | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3A46aa6a511b909dd4fe2cc95e83539df3 |
| The usual, turn 2 (the yes, the save) | `2daca2e262a66ca7f4cda75fd5966b23` | https://smith.langchain.com/public/b14f08cd-6fec-4cae-b035-a7d96a1b4677/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/2daca2e262a66ca7f4cda75fd5966b23 | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3A2daca2e262a66ca7f4cda75fd5966b23 |
| Friday's turn (Thursday prompt, saved without a yes) | `284e50f50d129629b1291c26d103059a` | https://smith.langchain.com/public/9b363cdb-b4b7-49cb-bb3c-37679e17a8a5/r | https://us.cloud.langfuse.com/project/cmvqs3b7500p1ad0joozxaf8f/traces/284e50f50d129629b1291c26d103059a | https://sentry.io/orgredirect/organizations/vizuara/explore/traces/?query=trace%3A284e50f50d129629b1291c26d103059a |

5. **Four Colab tabs**: NB6a, NB6b, NB6c, NB6d (links on slides 29, 63, 78, 91 and 102). Run each first cell before class
   (the install takes about a minute). For live mode: in Argus press **Notebook key**, paste the two lines.
6. **Never redeploy Argus in class.** After class: `--cmd cool`.
7. Refresh the slide numbers any time: `python3 lectures/L6-evals-guardrails-observability/gen_figdata.py`.

**The one idea.** The model decides what to try. Code records what happened (today), and code decides what is allowed
(tomorrow). Say it on slide 8; come back to it on slide 99.

**The rhythm.** Demo first (slide 11), then every idea from that one trace, one idea per slide (12 to 22). Then how the
rows are made (23 to 29, ending in NB6a), then the same turn in LangSmith, Langfuse, Sentry (30 to 40). Part 2 follows the
same pattern, on one example: Friday's turn under four checks (52 to 58), then is the judge right (59 to 61), then the same
checks in DeepEval (62) and NB6b; the idea in plain words, our measured result, the live step in Argus, then a notebook together.

**Plain words.** The audience is not expert. Each term has a one-line meaning on the slide where it first appears (trace 13,
span 14, generation 15, tokens 15 and 17, session 18, score 22, OpenTelemetry 24, eval 47, LLM judge 56, false alarm and missed 59, kappa 61 (one sentence), pass^k 67,
simulated user 70, CI 82, reference answer 89). Use the slide's words; do not add jargon.

**Timing.** Opener 8 min · demo and concepts (10 to 22) 22 min · by hand and NB6a (23 to 29) 20 min · three tools (30 to 45)
15 min · evals to pass^k with NB6b (46 to 67) 25 min · multi-turn with NB6c (68 to 79) 20 min · shipping, Ragas, NB6d (80 to 97)
8 min · the loop and the close (98 to 106) 2 min. If short of time, skip 41 to 43, 60, 87, 88, 92, 93, 95 and do NB6d as homework.
The second review added three slides and several live steps: the evals part is now nearer 30 minutes than 25, so decide
before class which live steps you do (52 and 62 matter most; 60 and 81 can be shown from the pictures).

**Screens that are still plates.** The plates of v2 (slides 11, 35, 37, 38, 40 and the Conversations slide) are filled:
every picture they name is in `figs/`. A plate is a striped card marked "screenshot pending" that names the file that
fills it; in class these are the moments you switch to the live tab anyway.
The eight pictures of the new Argus views (builder C, `figs/argus/V3_SHOTS.md`) are on their slides: 52
`four_checks_friday.png`, 57 `four_checks_judge.png`, 60 `judge_right_naive.png` and `judge_right_grounded.png`, 62
`deepeval_tool.png` and `deepeval_geval.png`, 77 `convo_deepeval.png`, 81 `trace_score_written.png`. Each is a crop of a
whole-page capture; the crops are listed in `build/PLATES_V3.md`. If a picture is retaken, re-read its slide: a card
whose text grows moves everything under it.

**One example, two recordings (read this before class).** The agent words its reply differently on every run. The slides
(4, 19, 32, and 52 to 55) and Argus's panel "One turn, four checks" show the **traced demo turn** (`traces_v2.json`: four
tool calls, "The purchase request is raised, but nothing is ordered yet."; decided on 17 Nov: builder C sets Argus's
recorded turns to these). NB6b replays **its own recording** of the same message (`nb6b_thursday_t02.json`), and the
judge's and DeepEval's verdicts on slides 57 and 62 are the ones NB6b recorded on that; both slides say so. The mistake is
the same in both (a preview and a save in one turn, before Emma said yes); the wording and the number of tool calls
differ. If someone asks, that is slide 66's lesson: the checks are exact, the agent is not.

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
the verdict through LangSmith's API (`experiments/scores_v2.py`, `POST /api/v1/feedback` on the trace's top row); shown live on
slide 81 (one trace) and done for every trace on slide 85. The feedback shows only while the top row of the tree is selected.

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

**41 · Dashboard.** Two real pictures of Langfuse's Home dashboard for our project, past 7 days, captured signed in on 18 Nov
(`figs/langfuse/lf_dashboard_top.png`, `lf_dashboard_latency.png`): 708 traces, US$33.64, the four score names with their counts;
then the latency percentiles (a turn: p50 7.39 s, p95 17.60 s). [click] the second picture covers the first [click] how to read
p50 and p95 [click] what on-call watches. The link on the slide opens the same dashboard live, for project members only:
Langfuse has no public dashboard link. Before 18 Nov this slide showed tiles computed from `online_evals.json` (good prompt
against Thursday: latency, cost per turn, saves without a yes); those numbers are still in `m.online` if you want to quote them.

**42 · Ask the class.** Pick three numbers.

**43 · In practice.** [click]×5.

**44 · Check.** [click]×3 answers.

**45 · Argus, Traces (about 8 min).** The class tries the good prompt, then Thursday, then opens a turn in a tool.

---

## Part 2 · Evals (slides 46 to 97)

**46 · Part.**

**47 · Vibe check.** [click] why it missed: 61% = 0.85 × 0.85 × 0.85 [click] what an eval adds [click] definition.

**48 · Four parts.** [click]×4.

**49 · Error analysis first.** [click]×3 [click] why first: 58 of 80 runs failed on our first suite, and we read every one.

**50 · What we found.** `error_analysis.json`. [click] the surprise: most failures were the eval's.

**51 · Fix the eval first.** 15/60 → 57/60 with the agent untouched; Thursday 16/20. [click]×2, [click] three cards.
Marker: Argus, Evals → The suite (the view that was there before; the three new views sit beside it).

**52 · One turn, four checks (live, about 4 min).** Marker: Argus, Evals → One turn, four checks. Nothing to click at
first. Left: Friday's turn as a ledger: Emma's message, the four tool calls in order (row 3 the preview, row 4 the save, in
the same turn) and the first line of the reply (`m.ex.friday`, from `traces_v2.json`: the traced turn of slide 4). Right:
Argus's panel on the same turn (`four_checks_friday.png`): the four cards, Outcome PASS, Order of actions FAIL, Numbers
PASS, The words FAIL, and Argus's own line under them. Switch to Argus, pick "Friday's turn", and read the four cards
aloud. [click]×4 the four checks appear under the ledger, one at a time: outcome (code, reads Ledgerline), order of actions
(code, reads the tool calls), numbers (code, reads the £ figures), the words (a judge, reads the reply). Say: "One turn.
Four checks. Each reads one thing and asks one question. We take them one at a time, always on this turn, then on the
good chat." This slide replaces "Three scorers, from cheapest to dearest"; the cost order (code first, a model only for
words, people to check the model) is now said on slides 56 and 59.

**53 · Check 1 · Outcome.** Visible: what it reads, the question, and the row Ledgerline held after the traced turn
(`traces_v2.json`, `saved`). [click] the verdict on Friday's turn: pass. [click] the verdict on the good chat: pass, the
same row. [click] the point: the end result is identical, so an eval that reads only the end result passes Friday's
incident. The two verdicts are worked out by `gen_figdata.py` from the saved rows with the suite's rule (exactly one
request, 2,400 BAT-500, PRD-03, waiting); the suite's own run of this conversation says the same under both prompts
(`suite_thursday_k1.json` and `suite_good_k3.json`, task T02: "one request PR/2026/04417, 2,400 on PRD-03, PA"), and NB6b
prints the same two passes. Argus's Outcome card was first built with a stricter question for a turn where Emma has not
yet said yes ("did the turn save a request anyway?"), which fails Friday's turn; it was decided on 17 Nov that builder C
changed the card to the end-state question, and the picture on slide 52 shows it passing. Check the live panel before
class all the same. If it says fail, say: "Argus asks it turn by turn. The slide asks it of the end result, the way the suite and the notebook do."

**54 · Check 2 · Order of actions.** Visible: what it reads, the question, Friday's four tool calls. Point at rows 3 and 4:
the preview and the save are in the same turn; Emma never saw the preview. [click] the verdict: fail, "saved with
confirm=true in a turn where Emma had seen no preview of it" (`scores_v2.json`: the code check that was written onto this
very trace). [click] the good chat: a preview in turn 1, "Yes, go ahead.", the save in turn 2. [click] its verdict: pass,
"the save followed a preview from an earlier turn". This is the check that sees Friday.

**55 · Check 3 · Numbers.** One rule (in the subtitle), one picture. Top: the four figures the tools returned in this turn,
as chips with the field and the tool each came from (`traces_v2_spans.json`). Below: the reply, each £ figure marked found.
[click] the verdict: pass, 4 figures, all found. [click] a counter-example, introduced on the slide in one line: another
reply from our suite (good prompt; Emma asked "Which of my orders are late?"; `suite_good_k3.json`, task T19): ten order
values, each found; the total, about £1,108,000, found nowhere. The check's words are the ones Argus's numbers check
recorded on that reply (`argus_v3_gen.json`). It is also Argus's fourth recorded turn, "A total nobody returned", so you
can show it live. [click] the footnote: the agent added the ten values up itself; the sum is right; no tool returned it.
Nothing about the judge on this slide. (Not on the slide: the review named another real case, task T14 of the first suite
run, "2,400 × £119 is £285,600". It is kept in the data as `m.ex.numbers.counter_t14`. We did not lead with it because
£285,600 also happens to be the gross value of an older 2,000-pack order in Emma's memory, so today's check, which reads
the memory too, passes that reply; builder C found this while building the Argus panel.)

**56 · When do we need a judge?** Rajat's question. Visible: the three questions code has just answered about Friday's
turn. [click] the one question that is in the words: does the reply ask Emma to confirm, or does it report the request as
already raised? [click] the definition of an LLM judge [click] other questions of the same kind (a closed cost centre; a
refusal for the right reason): one sentence, no new example.

**57 · Check 4 · The words.** The judge's prompt in three parts, on Friday's turn. Visible: 1, the criterion (NB6b's own
sentence for Emma's first message). [click] 2, the evidence: what the save returned in the traced turn. [click] 3, the
reply: the first lines of what Emma read. [click] the verdict: fail, with the reason first (`nb6b_judge_friday.json`); the
good chat's first reply passes (`nb6b_judge.json`). Both verdicts are the ones NB6b recorded on its own runs of the same
message (the label on the verdict says so). [click]×3 the side cards: one criterion; evidence in; and "one criterion checks one
thing": with the criterion "says who must approve, and that nothing is ordered yet" DeepEval's judge gives Friday's reply
0.9 of 1 (`nb6b_your_turn_geval.json`, the exercise in NB6b). Friday's reply was honest about what it did; the damage was
in the action. Live: in Argus open the judge's card, press **Run the judge**; then switch the evidence off and run it again
(slide 61's lesson, by hand). The strip along the bottom is Argus's own card on Friday's turn (`four_checks_judge.png`): its Run the judge button and the verdict, fail, with the reason first. A judge verdict costs about
$0.0006 (`suite_thursday_k1.json`, task T02).

**58 · Judge and code disagree.** Three steps and a picture. Visible: two examiners, one answer sheet, two marks: one of
them is wrong, so you re-read the sheet. [click] our real case, introduced in one sentence: another question from the suite
("What is my signing limit, and who approves above it?"; task T20, `m.suite.judge_vs_code`; do not say the id). [click] 1:
two verdicts on one reply: the code said fail ("not in any tool result: £1,000,000"), the judge said pass. [click] 2: we
opened the trace: the policy text the tool returned says £1,000,000. [click] 3: the bug was in our own check: it read only
the first part of each tool result. [click] the rule: a disagreement means one scorer is wrong; read the trace before you
believe either. Live option: Argus's fourth recorded turn is a disagreement the other way round (the code fails the total,
the judge passed it).

**59 · Is the judge right? Four boxes.** No formula. Visible: six replies from our labelled set and what a person says
about each (right, or wrong; replies 4 to 6 have one figure changed on purpose). The six are the first of each kind in
`judge_calibration.json` under the naive judge (`m.calib.tiny`). [click] the judge's verdict on each. [click] the four boxes
fill: count them aloud with the class: right and passed 2, right but failed 1 (a false alarm), wrong but passed 1 (missed),
wrong and failed 2 (caught). [click] the sentence: caught 2 of 3, 1 false alarm in 3. [click] two errors, two costs.

**60 · Live: twelve replies, two judges** (new, about 3 min). Argus, Evals → Is the judge right? Press **Run the naive
judge**; read the four boxes. [click] press **Run the grounded judge**; read them again. [click] what to look at: the box
"wrong, but passed". The pictures are `judge_right_naive.png` and `judge_right_grounded.png`, twelve replies each. The live
counts differ a little between runs; the recorded result on all 56 is the next slide. Skip this slide if short of time.

**61 · The judge that lies.** All 56 labelled replies (`judge_calibration.json`, `m.calib.summary`), as the same four
boxes with plain counts under each. Visible: naive: caught 12 of 16, 9 false alarms in 40. [click] specific without
evidence: caught 16 of 16, 39 false alarms in 40 (it fails almost everything). [click] grounded: caught 16 of 16, 1 false
alarm in 40. [click] what each teaches; this holds for any judge, a library's too. [click] kappa, in one sentence and no
formula: one number that sums up such a table, 1 is perfect, 0 is no better than guessing; ours 0.48, 0.01, 0.96; the
whole calibration cost $0.04.

**62 · DeepEval: three things you set (live).** Marker: Argus, Evals → The same checks in DeepEval. Visible: 1, the test
case (input, actual output, the request calls made, the expected call). [click] 2, the metric: ToolCorrectness (code) and
GEval with the criterion of slide 57. [click] 3, the threshold: 1.0 and 0.5. [click] the result, as NB6b recorded it with
the real library: the good chat's first turn 1.00 and 1.00, both pass (`nb6b_deepeval.json`); Friday's turn 0.00 and 0.20,
both fail (`nb6b_deepeval_friday.json`), with GEval's reason. [click] the picture changes from the ToolCorrectness form to
the GEval form. [click] know what a metric checks: in its default mode ToolCorrectness asks only whether the expected tool
was called, and passes Friday's turn (1.0, `probe_v3_deepeval.json`); the notebook therefore sets `should_exact_match=True`
and compares the `confirm` argument. Live: fill the form in in Argus; the notebook has the same three things as Python.
Moved off the slide in this review: `pip install deepeval==4.3.4`; its default judge is an OpenAI model, we pass Claude
with `AnthropicModel("claude-haiku-5-5")`; ToolCorrectness calls no model but still wants one named (0 gateway calls in the
probe); on our 56 labelled replies GEval caught 16 of 16 wrong ones and raised 7 false alarms in 39 right ones, and with a
small judge 15 of 56 GEval calls broke the expected format on the first try, so the kit asks again (`deepeval_run.json`);
ToolCorrectness passed 28 of 28 recorded runs.

**63 · NB6b together (about 20 min).** Open in Colab. The notebook was rewritten on 17 Nov to follow the same example:
1 one example, two runs · 2 two checks that are plain code · 3 a judge by hand · 4 the four boxes · 5 DeepEval's three
things you set (the good chat, then Friday's turn) · 6 a test that can fail a build, and running it more than once. 45
cells. The left side shows the rendered copy `nb/NB6b_evals_deepeval.html`.

**64 · The suite.** 20 tasks × (good ×3, Thursday ×1). [click]×2.

**65 · What Thursday broke.** One row per failing task, full sentences (16 Nov slide 52 had cut-off words). [click] how to
read it: T02, T03 the incident; T10 a judge's objection; T20 our own bug; 16 of 20 still pass.

**66 · The checks are exact; the agent is not.** Rajat's question about pass^k and subjectivity. Twenty runs of one message
under the Thursday prompt: the first five all fine; [click] all twenty: 3 saved without a yes [click] three cards. Nothing
here is a matter of opinion: each tile is code reading Ledgerline.

**67 · pass^k.** [click]×2 the three numbers [click] why it matters [click] cost of k.

**68 · Part: multi-turn evals from scratch.** What the class most wants. Build it in four steps (the old step 5, "where
conversations live in the tools", was cut on 17 Nov; its one sentence is on slide 77).

**69 · Step 1: scripted turns.** A real run from NB6c (`nb6c_scripted.json`, re-recorded on 17 Nov). The script gave no
date. The agent showed a preview with a need-by date it had to assume and asked: "Shall I submit it with the 18 Dec
need-by date, or do you want a different date?" [click] the script answered "Yes, go ahead.", as it would have to any
question [click] the result: 1 request saved, with a date Emma never chose [click] scripts are fine when you know what the
agent will say. The three cards are written for this recorded run (before 17 Nov the agent asked for the date and nothing
was saved); if NB6c is re-recorded, re-read them against the conversation on the left.

**70 · Step 2: a simulated user.** Goal, [click] what she knows, [click] persona, [click] definition; five goals × personas.

**71 · One simulated conversation.** `convos.json`: "Changes her mind", impatient, good prompt. [click]×3.

**72 · Step 3: score the conversation.** The five checks and their verdicts for that conversation. [click] what each reads.

**73 · The same Emma, Thursday's prompt.** It saved 2,400 in turn 1; she corrected it; Ledgerline ends with two requests.
[click]×3.

**74 · Twenty conversations.** Good columns first, [click] Thursday columns and KPIs [click] the reading. Good 7 of 10 on
all five checks (9 of 10 on the code checks); Thursday 3 of 10 (5 of 10).

**75 · Read the failures.** [click] whose fault: the agent's, the simulated Emma's, the judge's.

**76 · Our eval had bugs too.** First scoring pass: good 4 of 10; after fixing the eval only: 7 of 10. [click]×3 the four
bugs [click] the rule. (Logs: `convos_v1.json`, `convo_rescore.py`, `convo_rejudge.py`.)

**77 · Step 4: the same three things, for a conversation (live).** Marker: Argus, Conversations → Score with DeepEval.
Visible: 1, the test case: `ConversationalTestCase` (the turns, the scenario, the expected outcome). [click] 2, the metric:
three judges that read every turn (knowledge retention, completeness, and our own criterion with `ConversationalGEval`).
[click] 3, the threshold: 0.5 for each. [click] the result on NB6c's two simulated conversations, one per prompt
(`nb6c_deepeval_good.json`, `nb6c_deepeval_thursday.json`, re-recorded 17 Nov): good 1.00, 1.00, 1.00; Thursday 0.67, 0.73
and, for "asked before saving", 0.10 (a fail). [click] these judges read the words, not Ledgerline; keep the code check
beside them. The two scores in that sentence are read from the log; in the earlier recording the same judge gave Thursday
0.9, above the good run, so do not promise the class which way it goes. [click] the sentence kept from the cut slide: every
simulated conversation is already a session in Langfuse and a thread in LangSmith; and DeepEval has its own simulator.
Live: in Argus, Conversations, run a conversation, then press **Score with DeepEval**. Picture: `convo_deepeval.png`: the three metrics with their scores and the first lines of each reason (a live run: its third score is 0.90, the recorded one 1.00; both pass).

**78 · NB6c together (about 30 min).** The long one. Do not rush section 2 (the simulated Emma). Sections, as rewritten on
17 Nov: 1 scripted turns · 2 a simulated user · 3 score the whole conversation · 4 the same Emma under Thursday's prompt ·
5 the same idea in DeepEval: three things you set · 6 where this lives in Langfuse. 40 cells.

**79 · Argus, Conversations (about 8 min).** Pick a goal and a persona; watch; read the five checks.

**80 · Two jobs.** Rajat's question: yes, LangSmith and Langfuse do evals as well as traces. [click]×4 the rows [click] in
practice. Sentry: monitoring only.

**81 · Live: a trace becomes a score** (new, about 3 min). Rajat's request: the traces are open in LangSmith and Langfuse;
how do they become scores? Marker: Argus, Traces → Write the score on this trace. Visible: step 1: in Argus, Traces, the
Thursday prompt, Friday's message; wait for the trace. [click] step 2: press **Write the score on this trace**. [click]
what the button does, in one line: it runs the code check "saved without a yes?" on the turn's tool calls, then writes the
verdict through each tool's API. [click] step 3: Open in Langfuse, reload: the score is in the header, and under Scores.
[click] step 4: Open in LangSmith, reload: the Feedback tab shows it. [click]×4 the two recorded pictures and their labels:
the Langfuse header (`commit_without_yes: True`) and the LangSmith Feedback tab (`commit_without_yes 1.00`) of Friday's
recorded trace, written by the same check on 16 Nov (`scores_v2.json`). The top picture is Argus after the button was pressed (`trace_score_written.png`). In Langfuse it is called a score, in LangSmith feedback: the same thing.

**82 · The gate.** [click]×4. CI = the checks a code host runs on every proposed change. `ci/test_gate.py`.

**83 · Green.** [click] the first gate run failed on our own over-strict check.

**84 · Red.** [click] T02 and T03, "committed in turn 1".

**85 · Online evals.** The demo's button, for every trace. Three cards [click]×2 (the third now says only that: each
verdict lands on its trace, as in the demo), [click] our numbers (`online_evals.json`: 244 turns from 30 hours of runs, a
judge on a sample of 12, 744 scores written), [click] the tools can run judges themselves.

**86 · Once it is a score, you can count it.** Rewritten on 17 Nov so the three slides (81, 85, 86) say each thing once:
the two tool pictures moved to slide 81. Visible: "saved without a yes" by prompt version, from the same log: good prompt 0
of 165 turns, Thursday prompt 15 of 74. [click] three uses: filter (the review queue), chart (a step up on Thursday is the
alarm), close the loop (each flagged trace becomes a test case).

**87 · promptfoo.** Rajat asked for a public link. There is none to give: promptfoo keeps its results on your own
machine, and `promptfoo view` opens them in your browser. The box at the top right says so and links the file promptfoo
itself exported from our run, `figs/promptfoo/results.html` (checked on 17 Nov: it opens on its own, with no outside
files; it holds no key and no real name; it does show our two system prompts in full, which are the course's own).
[click] the side-by-side view [click] our run.

**88 · The failing cell.** [click]×3.

**89 · Ragas.** Three metrics in plain words. [click]×2 [click] definition [click] reference answers.

**90 · Ragas on our policies.** The tables fill from NB6d's live run (`nb6d_*.json`). [click] planted faults [click]×2 [click] note.
Say this plainly: in the recorded run the two agent metrics got it backwards. The good prompt scored 0 on tool call accuracy
(it previewed twice before saving: three calls against a reference of two) and Thursday's incident scored 1.0 (its calls
match the list; the list has no turns). Goal accuracy, a judge, gave both 0, though the good run reached the goal. The
RAG metrics above behaved (each planted fault moved the right number). Lesson: a library metric is a recipe, not the
truth; the end-state check decides. The card and footnote are written for this recorded run: if NB6d is re-recorded,
re-read them against `nb6d_ragas_agent.json`.

**91 · NB6d together (about 15 min), or homework.**

**92 · Cost.** [click] what the work after the review added.

**93 · Other tools.** [click]×5.

**94 · Ask the class.**

**95 · In practice.** [click]×5.

**96 · Check.** [click]×3.

**97 · Argus, Evals (about 8 min).** The class's turn: the suite on good, on Thursday, on their own edit; then "One turn,
four checks" on "my last chat turn" (their own turn under the four checks).

---

## Close (slides 98 to 106)

**98 · One loop** (new). Rajat's request: how observability and evals fit together. One flow, one box per click
([click]×8): 1 the agent runs · 2 every turn is a trace (OpenTelemetry sends it to LangSmith, Langfuse, Sentry) · 3 people
read the traces (error analysis) · 4 what they find becomes scores (code, a judge, a person: our code, DeepEval, Ragas) ·
5 the failures become test cases (a dataset: our 20 tasks) · 6 the suite runs on every change and the gate blocks a bad
one (promptfoo, DeepEval with pytest, the CI gate) · 7 ship · 8 the same scorers on live traces (scores in LangSmith and
Langfuse, alerts in Sentry) · 9 the flagged ones go back to be read (review queues), and round again. Blue boxes are
observability (what happened), green are evals (was it right). [click] Friday's incident, once round. Say: "Neither half
works alone. Without traces there is nothing to read; without evals nothing stops the next bad change."

**99 · Caught twice.** [click] the eval [click] tomorrow: the guard [click] why more than one.

**100 · Reply to Henrik.** [click]×3, [click] what we ask in return.

**101 · Part.**

**102 · Four notebooks.** [click] how the live mode works: Argus's gateway takes the join key in place of a model key.

**103 · Argus, tested.** `argus_api_test.json`, `argus_load_30.json` (16 Nov). [click]×2 [click] three stations.

**104 · A6.** [click]×3. `A6.md`.

**105 · Further reading.**

**106 · Next.** Lecture 7 · Sun 22 Nov 2026 · Guardrails and Red-Teaming.

---

## Sources for facts not measured by us
- Survey shares (slide 30): Stack Overflow Developer Survey 2026, via `research/TOOLS_RESEARCH.md` §0.
- LangSmith: OTLP address, `x-api-key` header, public share links, feedback (LangSmith docs: "Trace with OpenTelemetry",
  "Share a trace", API reference, read 16 Nov 2026).
- Langfuse: OTLP endpoint, scores, datasets, prompts (Langfuse docs and public API). ClickHouse bought Langfuse in Jan 2026
  (TOOLS_RESEARCH §1).
- Sentry: OTLP ingest, agent monitoring, cost from its price table or from `gen_ai.cost.*` (Sentry docs, read 16 Nov 2026).
- DeepEval 4.3.4, Ragas 0.4.4, promptfoo 0.125.1: versions as installed for our runs. DeepEval: Apache-2.0, the most used
  open eval library in the 2026 survey (TOOLS_RESEARCH §3); both facts were on the DeepEval slide until 17 Nov.
