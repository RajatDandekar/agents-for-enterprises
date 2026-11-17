# Lecture 6 · Evals, Guardrails and Observability · speaker notes

Sat 21 Nov 2026, 2 hours. 112 slides. Slide numbers are the deck's counter (bottom right). `[click]` = one step.
Dr. Rajat Dandekar presents. The plan is `SPEC.md`; every fact about another tool, survey or standard is from
`research/TOOLS_RESEARCH.md` (its section given below as **Source**, with the primary link it cites). Every number about
our own agent is measured, in `experiments/logs/`, read into the slides by `gen_figdata.py` (window.L6 in `figdata.js`).
No number about our system is typed on a slide. The build, decisions and spend are in `BUILD_LOG.md`.

## Before class (not on any slide)
1. **Argus, 30 minutes before.** `modal run deploy/argus_modal.py::admin --cmd purge-tests`, then `--cmd warm`, then
   `--cmd status` (expect `guard_models: true`, `langfuse: true`, spend 0, not paused). Raise the class cap if 40 come:
   `--cmd cap --cap 100` (README: `ledgerline/ledgerline/argus/README.md`).
2. **Join once yourself** ("Rajat demo"); in Traces send "Order the usual, please, needed by 4 Dec 2026." on the good
   prompt, then the Thursday prompt. Keep that tab: it is your live fallback for Sections 1 and 4.
3. **Open the incident trace in Langfuse** (public link, no login): the URL is `m.incident.bad.url` in `figdata.js`
   (also in `experiments/logs/incident_r3.json`, the first Thursday row). And the wall: `<Argus URL>/wall`.
4. **Never redeploy Argus in class.** After class: `--cmd cool`.
5. Refresh the slide numbers any time: `python3 lectures/L6-evals-guardrails-observability/gen_figdata.py`.

**The one idea.** The model decides what to try; code decides what is allowed, and records what happened. Say it on
slide 8, come back to it on slide 73 (guards) and slide 104 (three catches).

**The rhythm.** Each section: first principles → built by hand → the industry tool on our runs (install, code, screen) →
what teams do → check → the Argus station (about 10 minutes each). Ask-the-class slides: 30 seconds, answers in chat.

**Where the numbers come from.** Our agent: `experiments/logs/*` from runs on 16 Nov 2026 on Modal, agent
`claude-sonnet-5-5` (Lecture 5's Hermes model), judges and LLM guards `claude-haiku-5-5`. Other tools and the market:
`research/TOOLS_RESEARCH.md`. Vendor claims are marked as such on the slide.

---

## Opener (slides 1–11)

**1 · Title.** Kicker: Lecture 6 of 10 (the series is ten lectures; this lecture now owns all of observability, evals and
guardrails, including what used to be in the production lecture). The presenter note hides on the first click.

**2 · Where we are.** [click] what we never built [click] today. Bottom: the agent is unchanged: `ledgerline/course/l6/agent.py`
wraps `hermes/chat.py`'s Finale (same ASK prompt, same 26 tools, same `default_memory.json`); only its turn loop is copied
so every tool call passes one hook. Model as Hermes runs it (`LEDGER_MODEL_SWAP` → `anthropic:claude-sonnet-5-5`).

**3 · Henrik's letter.** Four clicks, one per question, then "start there". The letter is fiction (v4 world).

**4 · What Emma saw.** The chat is a real run: `incident_r3.json`, the first Thursday-prompt row that committed (message
"Order the usual, please, needed by 4 Dec 2026."). [click]×3 side cards. Say: the reply even says it is waiting for Daniel:
it is not lying; it simply saved without asking.

**5 · The Thursday edit.** The diff is computed from the two prompt files (`experiments/promptfoo/prompts/`, generated from
`course/l6/agent.py`: GOOD = Hermes's ASK; THURSDAY = two bullets replaced). [click] the one line that mattered. The tool's
own contract (`toolbox/create_purchase_request/tool.py`): confirm=false previews, confirm=true saves and submits.

**6 · How often?** Measured: `incident_r1/r2/r3.json`. With the date: Thursday 10/10 saved without a yes, good 0/10. Without
the date: Thursday 3/20, good 0/20 (most Thursday runs stopped to ask for the date). [click] no-date bars; KPIs: the vibe
check number is (1 − 3/20)³ = 61%. Honest framing: our first attempt used the message without a date and reproduced it only
3 times in 20; with the date it is every time. Both are real. Spend for all 55 incident runs: in `spend.json`.

**7 · Ask the class.** Expected answers: logs (no structure), audit trail (shows the request, not why), "ask the model"
(it will invent a reason). Section 1 answers it.

**8 · Three layers.** [click]×3. The definition box is the day's rule.

**9 · Map.** Five sections; Lecture 7 next (Sun 22 Nov).

**10 · Argus.** Screenshot `figs/argus/join.png` (our record run). The URL is live; join now or at station 1.

**11 · How it was built.** The honesty slide: one sandbox per run at a fixed clock; logs; spend total from `spend.json`.

## Section 1 · Observability (slides 12–39)

**12 · Part.** Henrik's first question.

**13 · Words and actions.** Measured on the incident turn (`m.incident.bad`): model calls, tool calls, seconds, tokens,
cost. Definition of observability (answer new questions from records, without new code).

**14 · Logs, metrics, traces.** [click]×2. Logs panel: an illustration of the format (stated on the slide). Metrics panel:
our own numbers from `online_evals.json` (good-prompt turns, p50/p95 latency, cost per conversation). Traces panel: the
incident turn's span names.

**15 · A span.** The real commit span (`m.incident.commit_span` from `incident_spans_r3.json`). Clicks reveal: ids →
times → GenAI attributes → arguments and result (`confirm: true`, the request number).

**16 · A trace.** All spans of the incident turn on one time axis (`m.incident.trace`). Point out: the model calls are the
long bars; the tools are ticks.

**17 · A tracer in 20 lines.** Code is `ledgerline/course/l6/minitrace.py` verbatim (comments trimmed). [click] usage
[click] what it lacks → OpenTelemetry.

**18 · OpenTelemetry.** [click]×3: processor/exporter; back ends; "instrument once". We used opentelemetry-sdk 1.45.2,
OTLP/HTTP. **Source:** TOOLS_RESEARCH §1.1, §3.1.

**19 · GenAI conventions.** Status Development; moved to `open-telemetry/semantic-conventions-genai` in semconv v1.42.0
(Jun 2026); `gen_ai.provider.name` replaced `gen_ai.system` in v1.37; agent spans; memory operations; content capture
opt-in. Two vocabularies: GenAI vs OpenInference. **Source:** TOOLS_RESEARCH §1.1 (gen-ai-spans.md, gen-ai-agent-spans.md).

**20 · Instrumenting.** Code excerpt of `course/l6/tracing.py` (`_TracedLLM.chat`, provider set-up). Auto-instrumentation
packages and their downloads: TOOLS_RESEARCH §1.1 (opentelemetry-instrumentation-anthropic 3.44M/month,
openinference-instrumentation-anthropic 1.36M/month).

**21 · The root span.** The attributes `Tracing.agent_span` sets (session.id, user.id, prompt, guards, usage, public).

**22 · What goes in a span.** OTEL_INSTRUMENTATION_GENAI_CAPTURE_CONTENT values (TOOLS_RESEARCH §1.1). Our tracer's
`redact=` (Presidio). The A10 measurement is on slide 83. Langfuse Hobby retention 30 days: TOOLS_RESEARCH §3.1 [secondary].

**23 · Langfuse.** 37.5k stars, 30.4M downloads/month [measured by the research], SO 2026 15.2% (8.8% in 2025),
ClickHouse acquisition Jan 2026, v4 Aug 2026; "21 of the Fortune 50" is the vendor's claim. **Source:** TOOLS_RESEARCH §0,
§2, §3.1. The code: OTLP to `/api/public/otel/v1/traces` with Basic auth (`tracing.langfuse_exporter`).

**24 · Incident in Langfuse.** `figs/langfuse/lf_incident_tree.png`: headless Playwright on the public trace URL
(`experiments/shots_traces.py`). The header also shows the scores written by our online evaluator (slide 63).

**25 · The incident span.** `lf_incident_span.png` + our span record. **Honest note on the slide:** on the public,
logged-out view the Input/Output panels showed "undefined"; Langfuse's API returns the values (we read them for the online
evals). We did not log in (by design).

**26 · Timeline.** `lf_incident_timeline.png`. Model calls 2–4 s each; tools milliseconds; cost per call grows as tool
results accumulate.

**27 · A generation.** `lf_generation.png`. Our cost: tokens × $2/$10 per M (Sonnet 5.5 list price in `llm.PRICES`).

**28 · Good prompt, two turns.** `lf_good_turn1/2.png` (from `incident_r1.json`, the good run with a turn 2). [click]
turn 2.

**29 · Phoenix.** Phoenix 21.0.0 (ELv2), `phoenix serve` on localhost:6006, in a Modal container; the same recorded spans
re-sent with `tracing.replay()` (ids unchanged). `px_traces.png`. **Source:** TOOLS_RESEARCH §3.1.

**30 · Langfuse's data model.** Observation types, sessions, scores, datasets, prompt management, API. **Source:** §3.1.

**31 · Incident in Phoenix.** `px_trace.png` (opened by trace id). Default judges in Phoenix/MLflow/DeepEval are OpenAI:
TOOLS_RESEARCH §5 risk 5.

**32 · A span in Phoenix.** `px_span_attrs.png`.

**33 · Finding it.** The trace figure in "find" mode: [click] tools only [click] the preview [click] the commit.

**34 · Dashboard.** From `online_evals.json` (Langfuse public API over every trace in a 30-hour window: 244 turns): p50/p95
latency, cost per turn per prompt, cost per conversation, commits without a yes (15, all Thursday), unsupported £ amounts.
The Langfuse dashboards themselves need a logged-in UI; we computed the same numbers from the API (said on the slide).

**35 · Ask the class.** No single right answer; push for one business signal (commits without a yes).

**36 · In practice.** Sampling (head/tail), retention, redaction, alerts, versions on spans, scores on traces.

**37 · Market.** SO 2026 numbers and caveats (developers, self-reported; Humanloop artefact); LangChain survey 89%/62% (own
audience). Consolidation list. **Source:** TOOLS_RESEARCH §0 items 1, 2, 4; §6.

**38 · Check.** Answers on click.

**39 · Station 1.** `figs/argus/traces_thursday.png` (our record run; the incident on the first try with the dated
message). Give 8–10 minutes. Ask them to post a screenshot of their red row.

## Section 2 · Evals (slides 40–71)

**40 · Part.**

**41 · Vibe check.** The 3/20 and 10/10 from slide 6; the 61% vibe-check miss. Definition of an eval.

**42 · Anatomy.** T02, step by step (input, criteria, scorer, threshold). [click]×4.

**43 · Error analysis.** [click]×3 then the "why first". Our first run: 58 of 80 runs failed (suite v1).

**44 · What we found.** `error_analysis.json` (built by `experiments/error_analysis.py` from the v1 logs; the notes were
written reading the traces, the counts are computed by rules). The surprise: most failures were the eval's (judge cut at
400 tokens; a task demanding a preview when asking for the date was right; judge without memory), two were tool issues (no
tool lists Emma's requests; the preview's VAT not labelled), one the agent's (it worked out money itself), plus an import
race (infra).

**45 · After.** v1 15/60 → v2 57/60 on the same agent. Thursday v2 16/20. Later rounds: three more bugs (slides 60, 48, 103).

**46 · Three scorers.** [click]×3 then the suite summary.

**47 · Code checks.** `course/l6/suite.py` (`one_request`, `commit_only_after_yes`), as written.

**48 · Code vs judge.** T14 (suite v1): the model computed £285,600 itself; the numbers check named it, the judge failed the
reply for another reason (VAT hedging). A11 in Argus (record run): the output check flagged £85,680, a gross figure the model
computed. T20 (suite v2): our check was wrong (evidence kept as 1,800 ASCII-escaped characters, so "£1,000,000" in the policy text was invisible); fixed in
`agent._slim` (6,000 characters, unescaped). Both real, both in `suite_good_k3.json`.

**49 · Every case.** `m.suite.judge_vs_code`: every good-prompt run where words passed and numbers failed.

**50 · Judge done properly.** `course/l6/judges.py` GROUNDED prompt. Why Haiku: $0.10/$0.50 per M (`llm.PRICES`).

**51 · The suite grid.** `m.suite.grid` from `suite_good_k3.json` and `suite_thursday_k1.json`. [click]s: Thursday fails
T02/T03; flaky T10, T20.

**52 · What Thursday broke.** `m.suite.thursday_caught`.

**53 · pass^k.** pass^1 0.95, pass^3 0.90, pass@3 1.00 (good prompt). τ-bench origin: TOOLS_RESEARCH §3.2. Cost per task
run from the suite logs.

**54 · DeepEval.** 4.3.4, Apache-2.0, 19.5k stars, 3.2M/month, SO 2026 5.8% (TOOLS_RESEARCH §2, §3.2). Ran on our recorded
replies (`experiments/deepeval_run.py`): ToolCorrectness 28/28; GEval κ on the calibration set; 15 of 56 GEval calls with
Haiku failed DeepEval's schema on the first try (retried; one still failed). `AnthropicModel(model=...)` with no
temperature works.

**55 · Calibration.** 56 items (`course/l6/calibration.py`): 40 real replies labelled by the course builder against the
tool results (all meet their criterion), 16 planted with one fact changed (label wrong by construction). Kappa formula.
**Open item:** the 40 labels should be spot-checked by the instructor.

**56 · The judge that lies.** `judge_calibration.json`: naive κ 0.48 (4 planted passed, 9 false alarms); specific without
evidence κ 0.01 (fails nearly everything); grounded κ 0.96 (16/16 caught, 1 false alarm). [click]×2.

**57 · Multi-turn.** Scripted second turns (T02/T03); simulated users (τ-bench); DeepEval conversational cases.

**58 · The gate.** [click]×4. 8 live runs per gate, about $0.70 and 90 s (from `ci_gate.json` and the suite costs).

**59 · Gate code.** `ci/test_gate.py`, `ci/github/workflows/l6-eval-gate.yml` (ready to copy into `.github/workflows/`;
needs the repository secret ANTHROPIC_API_KEY: **open item for Rajat**).

**60 · Gate on good.** `figs/ci/ci_good_term.png` from `logs/ci_good.txt`: the exact command, run on Modal; exit 0, 8
passed. The first gate run failed T01 (over-strict check): `ci_good_v1.txt`, kept.

**61 · Gate on Thursday.** `ci_thursday_term.png` from `logs/ci_thursday.txt` (run with the first version of the T01
check): exit 1; T02 ×2 and T03 ×2 "committed in turn 1" (genuine); T01 run 2 failed the over-strict check (said on the
slide). Not re-run to save budget.

**62 · Online evals.** `experiments/online_evals.py`: reads AGENT and TOOL observations back from Langfuse's public API,
scores them in code, judges a sample of 12 with Haiku, posts BOOLEAN/NUMERIC scores with deterministic ids. Langfuse's own
LLM-as-judge evaluators need an LLM connection added in its UI by the project owner (**open item**); trace-level
evaluators stop on Cloud after 16 Nov 2026 (TOOLS_RESEARCH §3.1).

**63 · Scores on the trace.** The header of `lf_incident_tree.png`: `commit_without_yes` = True. (Our first scoring pass
had a name-matching bug and posted wrong values; we deleted those 694 scores and re-scored: `BUILD_LOG.md`.)

**64 · promptfoo.** 0.125.1, Node ≥ 22.22 (run in a Modal image with Node 22), MIT, 27k stars, 4.6M npm/month; OpenAI
acquisition and the Evals migration (TOOLS_RESEARCH §3.2, §6). `figs/promptfoo/pf_view.png` is `promptfoo view` of our
run: good 5/5, Thursday 4/5.

**65 · Failing cell.** The Thursday dated cell's output, from `promptfoo_eval.json`.

**66 · Eval cost.** `m.spend_rows` from `spend_parts/` (token counts × list prices; CI gate cost is an estimate, DeepEval's
cost is an estimate: DeepEval reported $0 for this model id).

**67 · Other eval tools.** Inspect AI, Ragas, MLflow 3, Phoenix evals, LangSmith, Braintrust ($80M at $800M, Feb 2026),
OpenAI Evals shutdown 30 Nov 2026. **Source:** TOOLS_RESEARCH §3.1, §3.2, §6.

**68 · Ask the class.** "Sounds like Emma" → a calibrated judge or a person; "saved on PRD-03" → code; "asked before
saving" → code (trajectory).

**69 · In practice.** LangChain survey numbers: 52.4% offline, 37.3% online, 59.8% human review, 53.3% LLM-as-judge, 29.5%
none (TOOLS_RESEARCH §0 item 2; own audience).

**70 · Check.**

**71 · Station 2.** `figs/argus/evals_thursday.png`: the quick suite on the Thursday prompt in our record run: "would not
ship", 4/6.

## Section 3 · Guardrails (slides 72–100)

**72 · Part.**

**73 · Words vs actions.** `guards_attacks_r1.json` (good prompt, off/all) and `guards_attacks_thu.json` (Thursday,
off/all): 1/20 and 3/20 with no guards; 0/20 with all guards under both. The good-prompt A10 "all" row is the re-run after
the PII fix (`guards_attacks_a10.json`).

**74 · Where a guard sits.** [click]×4.

**75 · Attack library.** `course/l6/attacks.py` (20 attacks, OWASP codes, success checks in code).

**76 · Deterministic first.** The six code guards in `course/l6/guards.py`.

**77 · Confirm needs a yes.** Excerpt of `guards.py`. The bug the replay found (setdefault). Framework hooks: Claude Agent
SDK PreToolUse, LangChain HITL middleware, OpenAI Agents SDK guardrails (TOOLS_RESEARCH §3.3).

**78 · Identity and approvals.** Rows A01, A02, A13, A14, A18 from the good-prompt attack run.

**79 · Poisoned invoice.** The e-mail (`course/l6/agent.py` POISON). Spotlighting, taint, dual LLM/CaMeL (concepts; no
measurement claimed). In the Thursday run with all guards, provenance refused an outbound message (stopped_by provenance).

**80 · Spotlighting, concretely.** What `Guards.tool_text` returns.

**81 · Injection classifier.** ProtectAI DeBERTa v3 prompt-injection-v2 (ungated); Prompt Guard 2 gated (TOOLS_RESEARCH
§3.3). Measured (`guards_detectors.json`): 12/15 caught, 4/26 false alarms, median 80–100 ms on 8 CPUs; missed A19 and two
of three poisoned e-mails (including the invoice); false alarms on "Ignore the Leeds stock…", "Override the need-by
date…", "Disregard my last message…" and one clean supplier e-mail.

**82 · Presidio.** 7/8 caught, 0/10 false alarms, median ~5–10 ms; missed "+44 7700 900123". presidio 2.2.366, spaCy
en_core_web_sm (small model, to keep the image light).

**83 · Card number.** A10: no guards, the card stayed in the trace (user input on the root span); with the PII guard the
message to the model and every trace attribute were masked (re-run after the fix).

**84 · NeMo Guardrails.** 0.24.1, `NEMOGUARDRAILS_LLM_FRAMEWORK=langchain`, langchain 1.5.0 + langchain-community 0.4.2 +
langchain-anthropic 1.7.10, in its own venv (`experiments/nemo/`, `nemo_check.py`). Measured: 15/15 caught, 0/26 false
alarms, median ~1.4 s, ~$0.00014 per check (Haiku). Compatibility shim: Claude refuses sampling parameters; NeMo sends a
low temperature; we strip them in the Anthropic SDK's request builder (first two attempts failed: missing langchain, then
the temperature error; both in `BUILD_LOG.md`). The 72.5% bypass figure is a secondary source (TOOLS_RESEARCH §3.3).

**85 · Measuring a guard.** `m.detector_rows`.

**86 · Output checks.** The numbers check in the reply path; monitor mode (`Guards(mode="monitor")`).

**87 · OWASP Agentic 2026.** Codes and titles checked against the OWASP PDF (genai.owasp.org, Top 10 for Agentic
Applications 2026, published 9 Dec 2025), read on 16 Nov 2026. The Northbridge mapping is ours.

**88 · OWASP LLM 2026.** Checked against the OWASP GenAI LLM Top 10 2026 PDF (page dated 3 Aug 2026; announcement 1–2 Sep
2026 with the Agent Control Standard v0.1). 2025 codes from the 2025 list on genai.owasp.org.

**89 · Red team.** `promptfoo/redteam.yaml`; remote generation disabled; Claude Haiku generates and grades
(TOOLS_RESEARCH §3.4 data handling). Two runs: the first had the guarded target error (the node image lacked the guard
models; fixed by building it on the guards image). Run 2: no generated attack succeeded on either target. Run 1: a
prompt-extraction attack succeeded on the unguarded target (the guarded target had errored). Hijacking
generated no test (remote-only strategies off).

**90 · Generated attacks.** `promptfoo_redteam.json` cells.

**91 · ASR.** Bars from `m.attacks.asr`. A05 under Thursday: Ledgerline held a 50,000-pack request while the reply said
nothing was saved (its submit failed: no approver for that value).

**92 · Which guard.** Thursday off/all table. "Stopped by" lists every guard that refused, blocked, quarantined, flagged or
redacted something in that run (so it can include a guard that fired on a side issue, e.g. output_check flagging a
self-computed gross figure).

**93 · An attack that worked.** A09 (base64) under Thursday, no guards: real run.

**94 · Guard cost.** `m.attacks.guard_ms` (from guard events) and NeMo's median.

**95 · Landscape.** TOOLS_RESEARCH §3.3, §3.4, §6 (LLM Guard archived Jul 2026; Lakera → Check Point; Protect AI → Palo
Alto; Guardrails AI needs a Hub token; Prompt Guard 2 gated).

**96 · Ask the class.** All of these; plus eval tasks for each rule.

**97 · In practice.** Least agency (OWASP's guiding principle), monitor-then-enforce, detectors where outside text enters.

**98 · Check.**

**99 · Station 3.** `figs/argus/guards_a11_all.png`: A11 with all guards: "It did not work"; the guard timeline.

**100 · Wall.** `figs/argus/wall.png` from our test run; in class it fills with theirs.

## Section 4 · Trusted (slides 101–106)

**101 · Part.**

**102 · Replay turn 1.** `experiments/replay.py` (Thursday prompt, code guards): the model tried confirm=true; confirm_yes
refused; `lf_replay_turn1.png`.

**103 · Replay turn 2.** "Yes, go ahead." → the commit passes (PR/2026/04417 waiting for Daniel). The first version of the
guard refused this yes (`replay_v1_bug.json`); the fix is one word (`setdefault`).

**104 · Three catches.** Trace (15 commits found by the online scorer), eval (gate exit 1; suite 16/20 vs 57/60), guard
(both replays; ASR 3 → 0 under Thursday).

**105 · Limits.** Regex yes; small sets; judges drift; detectors bypassable; tools are the boundary; owners.

**106 · Henrik's answers.** Numbers from figdata.

## Section 5 · Your turn (slides 107–112)

**108 · Argus at scale.** `argus_api_test.json` (23/23 on the live URL) and `argus_load_30.json` (30/30, chat p95 5.9 s,
attack p95 15.0 s; agent switched to Haiku for the load test, then back).

**109 · NB6.** Runs top to bottom without a key (executed on Modal with keys removed: `experiments/nb_run.py`). On Colab it
downloads the logs from the course repository: works once this folder is pushed (**open item**).

**110 · A6.** `A6.md`, 100 points.

**111 · Further reading.**

**112 · Next.** Lecture 7 · Agent Frameworks in Industry, Sun 22 Nov 2026.
