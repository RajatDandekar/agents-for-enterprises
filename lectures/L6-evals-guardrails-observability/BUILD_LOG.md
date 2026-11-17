# Lecture 6 · Evals, Guardrails and Observability · build log

Built 16 Nov 2026 for Sat 21 Nov 2026. Brief: Rajat's (in SPEC.md), refined by the coordinator (series of ten lectures:
"Lecture 6 of 10"; this lecture owns all of observability, evals and guardrails, including the guardrails part of the old
production lecture). Market research: `research/TOOLS_RESEARCH.md` (stack followed: Langfuse + Phoenix, DeepEval +
pytest gate, promptfoo eval and red team, deterministic guards + NeMo + Presidio + an ungated injection classifier).

## What was built
| Path | What |
|---|---|
| `ledgerline/ledgerline/course/l6/` (new) | `agent.py` (Lecture 5's Finale wrapped: prompt swap, the Thursday prompt, the poisoned invoice, hooks), `tracing.py` (OpenTelemetry, GenAI conventions + OpenInference + Langfuse attributes, redaction, `replay()`), `minitrace.py` (20-line tracer), `guards.py` (6 deterministic guards + DeBERTa + Presidio + numbers check; enforce/monitor), `suite.py` (20 tasks: outcome, trajectory, numbers, words; pass^k), `judges.py` (naive and grounded Haiku judges), `attacks.py` (20 attacks + 20 benign, success checks in code), `labelled.py` (detector sets), `calibration.py` (56-item judge set) |
| `ledgerline/ledgerline/argus/` (new) | the Argus lab: `app.py`, `static/` (argus.html/js/css, wall, admin), `recorded.json`, `README.md` |
| `deploy/argus_modal.py` (new) | Modal app `northbridge-argus` (deploy, admin, test, load, record) |
| `lectures/L6-evals-guardrails-observability/` | `index.html` (112 slides), `l6.css`, `l6figs.js`, `figdata.js` ← `gen_figdata.py`, `figs/` (37 real screenshots), `NOTES.md`, `A6.md`, `NB6_evals_guardrails_observability.py` → `.ipynb` (executed, no key), `qa_full_modal.py`, `ci/` (gate test, workflow, requirements), `experiments/` (runner `l6_modal.py`, every experiment script, `logs/`, `promptfoo/`, `nemo/`) |
| `ledgerline/ledgerline/cassettes/L6E_*.jsonl` (new) | recorded model replies of our runs (prefix L6E_, see "Collision" below) |

**Shared code:** no change to `llm.py`, `toolbox/`, `hermes/` or any live app. `hermes.app` (Store, Guard, GuardedLLM,
Refused) and `course/obs/otel.py` (SpanLog, PROVIDER_NAMES, to_semconv_messages) are imported read-only.
**Collision found and fixed:** the cassette name `L6_judge` already existed (an older lecture's, tracked); my first suite
run appended to it. I restored it with `git checkout` and renamed all of mine to `L6E_*`.

## Measured results (all in `experiments/logs/`)
- **The incident reproduced, for real.** Thursday prompt (two bullets of Hermes's ASK shortened: "Be concise: fewer
  confirmations…"), "Order the usual, please, needed by 4 Dec 2026.": **10/10** runs saved the request without a yes (the
  model previews to itself, then commits in the same turn); good prompt **0/10**. Without the date: Thursday 3/20 (most
  stop to ask for the date), good 0/20. A milder edit (save rule only): 0/5. `incident_r1/r2/r3.json`.
- **Trace:** every turn exported to Langfuse Cloud (public links) and the same spans replayed into Phoenix 21.0.0.
  The commit span: `execute_tool create_purchase_request`, `confirm=true`, same trace as the preview.
- **Suite:** v1 15/60 (good) — error analysis showed most failures were the eval's (judge cut at 400 tokens, over-strict
  task, judge without memory), two tool issues, one agent failure, one import race. v2: good **57/60**, pass^1 0.95,
  pass^3 0.90 (flaky T10, T20); Thursday **16/20** (T02, T03 commit in turn 1).
- **Judge calibration** (56 items, 40 real + 16 planted): naive κ 0.48, specific-no-evidence κ 0.01, grounded κ **0.96**.
  DeepEval GEval (Haiku) κ 0.73; ToolCorrectness 28/28; 15/56 GEval calls failed DeepEval's schema on the first try.
- **CI gate** (pytest + DeepEval, the workflow's exact command, on Modal): good prompt exit **0** (8 passed); Thursday exit
  **1** (T02 ×2, T03 ×2 committed in turn 1). First good run failed T01 on an over-strict check → fixed the check.
- **Online evals:** 244 Langfuse traces scored from the API; 15 commits without a yes found (all Thursday); 744 scores posted.
- **promptfoo** 0.125.1: good 5/5, Thursday 4/5 (the dated usual failed all three assertions). Red team (Claude Haiku
  generating and grading, remote generation off): run 2, 0 successes on both targets; run 1, one prompt-extraction success
  on the unguarded target (the guarded one errored: image lacked the guard models; fixed).
- **Guards:** DeBERTa 12/15 caught, 4/26 false alarms, ~80–100 ms (missed the poisoned invoice); NeMo self-check input
  15/15, 0/26, ~1.4 s, $0.00014/check; Presidio 7/8, 0/10, ~5–10 ms. Attack success rate (20 attacks): good prompt 1/20 →
  0/20 with all guards; Thursday 3/20 → 0/20.
- **Replay** with code guards under the Thursday prompt: turn 1 commit refused, turn 2 (after "Yes, go ahead.") allowed.
  First version refused the real yes (re-preview overwrote the turn) → fixed (`setdefault`).
- **Argus:** API test **23/23** on the live URL; load test **30/30** students, no errors, chat p95 5.9 s, attack p95 15.0 s
  (agent on Haiku for the load test); 12 station screenshots.

## Spend
**US$24.73** of model spend in total (token counts × list prices; `experiments/logs/spend.json`), within the ~US$25
budget. Largest: suite (v1+v2) $9.0, incident runs $5.2, attack runs $3.5, Argus tests $2.3, CI gate (estimate) $2.2.
Estimates are marked: the CI gate's cost (tasks × mean task cost) and DeepEval's (it reported $0 for this model id).

## Decisions
- Agent model `claude-sonnet-5-5` (as Hermes); judges, NeMo checker, red-team generator `claude-haiku-5-5` (20× cheaper;
  calibration shows the grounded Haiku judge agrees with labels at κ 0.96).
- Incident message with the need-by date for the story (10/10), reported next to the no-date rate (3/20): both real.
- Argus quick suite = 6 of the 20 tasks (cost per student), with the recorded full suite shown beside it.
- NeMo in its own venv; temperature stripped at the Anthropic SDK (Claude refuses sampling parameters).
- Langfuse via OTLP (no SDK in the hot path); scores via the public REST API with deterministic ids.
- Presidio with spaCy `en_core_web_sm` (small image); ProtectAI DeBERTa (ungated) instead of Prompt Guard 2 (gated).

## Bugs found on the way (several are slides)
Judge max_tokens 400 (cut JSON); T01/T02 wording (asking for the date is right); memory missing from judge evidence;
evidence `_slim` kept 1,800 ASCII-escaped characters (false "made-up number"); httpx import race in threads; online
scorer matched the wrong observation name and posted 744 wrong scores (deleted 694 old ones by id, re-scored with
deterministic ids); PII guard redacted for the record but not for the model (fixed: the model gets the masked text);
guard re-preview bug; NeMo needed langchain + langchain-community; red-team guarded target lacked torch; NB/OWASP: the
2026 OWASP codes were verified from the OWASP PDFs (pypdf), the web pages had no list.

## Open items (for Rajat)
1. **GitHub Actions:** copy `ci/github/workflows/l6-eval-gate.yml` to `.github/workflows/` and add the repository secret
   `ANTHROPIC_API_KEY`; mark "Eval gate" as a required check. Not pushed, no secret added (by the rules).
2. **Langfuse LLM-as-judge evaluators** (run by Langfuse) need an Anthropic LLM connection added in the Langfuse UI by the
   project owner; use observation-level evaluators (trace-level ones stop on Cloud after 16 Nov 2026).
3. **Calibration labels:** the 40 real-reply labels were written by the course builder against the tool results; please
   spot-check a few (`course/l6/calibration.py`, `logs/judge_calibration.json`).
4. **NB6 on Colab** downloads the logs from the course repository (`raw.githubusercontent.com/.../experiments/logs/`):
   works once this folder and `course/l6` are pushed. Verified top to bottom on Modal with keys removed (17 cells, 0 errors).
5. **Langfuse public view** shows tree, timings and cost but not input/output panels when logged out; the deck says so.
6. **Toolbox suggestions** from error analysis (not done; shared code): a `list_my_requests` tool; `includes_vat` on the
   request preview.
7. The Argus CI-free cost guide: plan US$60–100 for a class of 40; raise the cap (`--cmd cap`).
8. Argus is deployed with `min_containers=0` (cooled); warm it 30 minutes before class.
9. **Old Langfuse scores:** the first, buggy online-eval pass left scores (ids not `l6-…`) on the traces; the delete API
   rate-limited us after a few. Run `python3 experiments/lf_clean_scores.py` later (throttled) to remove them; the deck's
   scores slide says why each name shows two values.

## QA
`qa_full_modal.py` renders all 112 slides in headless Chromium, reveals every step, runs `tools/deck_qa.js` (overflow,
clipping, tiny text, page errors, empty figures). Final pass: see the end of this file.

### Final QA (16 Nov 2026)
Three full passes and targeted re-checks. Fixed on the way: KPI tiles (inner spans styled as blocks), chat bubble class
clash with the engine's `.b`, span-record alignment, suite grid overflow, long code lines, an install line over KPI
tiles, tiny table headers, screenshot crops (Langfuse, Phoenix, Argus, CI terminals re-rendered from the logs), one false
"undefined" flag (the word was in the honest-note text), and three slide statements corrected to match the logs (the
T14 judge verdict, the naive judge's example, the A05 outcome). Last pass: **112 slides, 0 issues, 0 page errors**.

---

# v2 · 16 Nov 2026, later the same day · "Observability and Evals" (after Rajat's review)

Brief: `REVIEW_16NOV.md` and the coordinator's v2 message. Lecture 6 is now observability and evals only, demo first;
guardrails and red-teaming are Lecture 7 (Sun 22 Nov), parked in `../L6b-guardrails/`. The course has eleven lectures.

## What changed
| Area | v2 |
|---|---|
| Deck | `index.html` rebuilt: **103 slides** (was 112). Built by `build/build.py` from `build/part0.py`, `part1.py`, `part2.py` (new slides) and `build/index_v1_16nov.html` (the 16 Nov deck: kept slides are taken by number, with listed edits). Re-run: `python3 build/build.py`. |
| Parked deck | `../L6b-guardrails/`: `index.html` (38 slides: a title, a recap, old slides 72 to 106 unchanged, a closing slide; kicker "Lecture 7 of 11 · Sun 22 Nov 2026"), copies of `l6.css`, the 16 Nov `l6figs.js`, `figdata.js`, its figures; `NOTES.md` (the old section 3 and 4 notes), `A6_part_guards.md`, `parked/` (the 16 Nov notebook, the Phoenix screenshots). Built by `build/build_l6b.py`. QA: 0 issues. |
| Tracing | `course/l6/tracing.py`: exporters for **Langfuse, LangSmith, Sentry**, each on when its key is present, skipped silently when not (`Tracing.from_env()`, `configured()`); input and output on the root, every `chat` and every `execute_tool` span in the forms each tool reads; per-trace links (`links(trace_id)`). |
| Multi-turn | `course/l6/convo.py`: personas, five goals, the simulated user, whole-conversation scoring. `experiments/convo_run.py` (20 conversations), `convo_rescore.py`, `convo_rejudge.py`. |
| Notebooks | `NB6a_tracing`, `NB6b_evals_deepeval`, `NB6c_multiturn_evals`, `NB6d_ragas` (`.py` sources, built with `tools/nbbuild.py`), helper `course/l6/nbkit.py` (live through the gateway or replay from `experiments/logs/nb6*_*.json`). Runner: `experiments/nb_run.py` on the `clean` image of `l6_modal.py` (Python 3.12, only the course package's own dependencies, **no Anthropic key in the container**). |
| Argus | Stations Traces, Evals, **Conversations**; the Guards station behind a flag (off); the **LLM gateway** (`/gateway/v1/messages`, `/gateway/v1/chat/completions`); "Notebook key" drawer; "Open in LangSmith / Langfuse / Sentry" buttons; redeployed twice on 16 Nov with the new keys. README updated. |
| Figures | `l6figs.js`: new `kv` (a span as plain rows), `convo`, `runs`, `cvgrid`, `nbframe`; `shot` shows a marked "screenshot pending" plate when a capture is missing; `otel` names the three tools. `gen_figdata.py`: `m.demo`, `m.convos`, `m.scripted`, `m.tour`, `m.scores_v2`, `m.redact`, `m.judge_example`, `m.suite.thursday_sentences`, `m.incident.nodate_runs`, the notebooks' logs, the v2 spend block. |
| Docs | `NOTES.md` (click by click, 103 slides), `A6.md` (observability and evals only, 100 points: trace 25, evaluate 30, test a conversation 30, gate 15), this log. The 16 Nov versions are in `build/`. |

## Shared code
None changed. Everything is under `ledgerline/ledgerline/course/l6/`, `ledgerline/ledgerline/argus/`, `deploy/argus_modal.py`
and this lecture's folder. `llm.py`, `toolbox/`, `hermes/` were not touched; the three live apps (hephaestus, hermes, daedalus)
were not redeployed.

## Measured in v2 (16 Nov, 12:00 to 14:00 UTC; all in `experiments/logs/`)
- **Three tools, one trace** (`traces_v2.json`, `readback.json`, `readback_first.json`). The stock question, the good two-turn
  chat and the incident (Thursday prompt, saved without a yes on the first try) were sent once to Langfuse, LangSmith and
  Sentry and read back through each tool's own API: 4 of 4 turns arrived in all three with input and output on the root,
  on every model call and on every tool call; tokens equal ours in all three; cost equal ours in Langfuse and LangSmith
  (incident US$0.103974). Sentry showed its own estimate (US$0.067583) because that send did not yet
  carry our figure; `tracing.py` now sends it in Sentry's `gen_ai.cost.*` fields (not yet re-sent: no model credit).
- **LangSmith ids** (measured, not documented): a span that arrives by OTLP gets the run id `00000000-0000-0000-<span id>`;
  a trace's id is its root run's id; the OpenTelemetry ids are kept in metadata (`OTEL_TRACE_ID`, `OTEL_SPAN_ID`). The UI
  link is `…/projects/p/<project>/trace/<root run>/run/<root run>`. Public share links were made for the four demo traces
  through the API (`POST /api/v2/runs/<id>/share`), so the LangSmith screenshots are logged out.
- **Scores** (`scores_v2.json`): the code check `commit_without_yes` written onto the four traces as a Langfuse score and as
  LangSmith feedback; both show on the public pages.
- **Simulated conversations** (`convos.json`; first scoring pass kept as `convos_v1.json`): 5 goals × 2 personas × 2 prompts.
  Good prompt 7/10 on all five checks (9/10 on the code checks); Thursday 3/10 (5/10). First pass said good 4/10:
  the difference was our eval (below).
- **Masking** (`redact_demo.json`): Presidio replaced the card number in 30 ms (it labelled it a phone number).
- **Langfuse tour** (`nb6a_langfuse_tour.json`): sessions, score names, the dataset `ask-northbridge-incident` (2 items), the
  prompt `ask-northbridge` (versions 1 and 2, labels production and thursday), through Langfuse's public API.
- **NB6a**: ran top to bottom **live** in the clean container through the Argus gateway (15 of 15 cells on the first
  version; its three model-backed logs are from that run) and in **replay** with no key at all (15 of 15, on the final source).

## Bugs and surprises found in v2 (several are slides)
1. **Langfuse's "empty Input and Output"** on the 16 Nov deck were not a tracing bug: the data is there (read back through
   the API). Langfuse's logged-out public trace page does not load those two panels (its `observations.byId` call answers
   401 without a session). Signed in, they show. Slides 35 and 40 carry plates for signed-in captures.
2. **A rule that misread a yes** ("Looks right, yes. No changes."): the order-of-actions check no longer reads Emma's words;
   a save must follow a preview from an earlier turn.
3. **A judge without the memory, then with evidence cut from the wrong end**: fixed in `convo.last_word_evidence`.
4. **A simulated Emma that explained herself and wrote DONE**: a message ending in DONE now ends the chat.
5. **Thinking blocks**: Claude Haiku may think before it answers, and with `max_tokens=300` the thinking used every token,
   so `content[0].text` failed in three notebooks. The notebooks now keep the text blocks (`nbkit.text_of`) and allow 1,500 tokens.
6. **Langfuse v4**: `GET /api/public/traces/<id>`, `/api/public/sessions` and `/api/public/v2/scores` answer 410; the
   observation-centric endpoints (`/api/public/v2/observations`, `/api/public/v3/scores`) are used instead.
7. **Ragas 0.4.4 with Claude**: the new `llm_factory` path fails on thinking blocks; NB6d uses the LangChain wrapper path.
8. **The Anthropic account ran out of credit** at about 13:13 UTC on 16 Nov (error: "Your credit balance is too low"),
   in the middle of the notebooks' live runs. Everything below marked "waits for credit" stopped there.

## Spend
v1 (the first build): US$24.73. v2 (after the review): **US$7.73** of a US$20 budget (20 simulated conversations (agent + Emma + judge) $6.39, Notebooks, run live through the gateway $0.85, The demo turns, traced to three tools $0.48, Conversations: one check re-judged $0.01).
`logs/spend.json` keeps the old total and adds a v2 block. The notebooks' live calls are charged to Argus's budget; `nb_run.py`
reads them back from the test student's spend.

## Waits for model credit (one command: `sh experiments/v2_finish.sh`, about US$5)
- NB6b: the judge by hand, DeepEval, the Thursday run (`nb6b_judge.json`, `nb6b_deepeval.json`, `nb6b_thursday_t02.json`).
- NB6c: the Thursday conversation, DeepEval's conversational metrics and simulator (`nb6c_sim_thursday.json`,
  `nb6c_deepeval_*.json`).
- NB6d: all of it (`nb6d_*.json`).
- The replay-mode test of NB6b, NB6c, NB6d (it needs those logs), and the rendered copies `nb/NB6b…html`, `NB6c…`, `NB6d…`.
- One re-send of the demo turns so Sentry shows our cost.
- Argus: the live API test with the Conversations and gateway checks (`argus_lab.py`, updated) and two screenshots
  (`figs/argus/traces_v2.png`, `conversations_v2.png`; `argus_record.py`, updated).
Until then the slides that read those logs show a marked plate ("from the run" / "rendered copy pending"), never a number.

## Plates waiting for a capture (each names its file on the slide)
| Slide | Plate | Needs |
|---|---|---|
| 11 | `figs/argus/traces_v2.png` | model credit (a live turn in Argus) |
| 35 | `figs/langfuse/lf_signed_in_generation.png` | signed-in Langfuse: a generation of trace `52e91c64814241a0b2bf371722612522` with Input and Output |
| 37 | `figs/sentry/sn_incident_trace.png` | signed-in Sentry: Explore → Traces, that trace |
| 38 | `figs/sentry/sn_incident_commit.png`, `figs/sentry/sn_agents.png` | signed-in Sentry: the last `create_purchase_request` span; Explore → Agents |
| 40 | `figs/langfuse/lf_signed_in_session.png` | signed-in Langfuse: a session page |
| 61, 77, 89 | `nb/NB6b_evals_deepeval.html`, `nb/NB6c_multiturn_evals.html`, `nb/NB6d_ragas.html` | model credit (the live runs) |
| 78 | `figs/argus/conversations_v2.png` | model credit |
After adding a file: `python3 gen_figdata.py` (it lists the figures that exist), then reload the deck.

## Open items (for Rajat)
1. **Top up the Anthropic account** behind the Modal secret `forge-anthropic`; then `sh experiments/v2_finish.sh`. Argus
   cannot answer anyone until then.
2. **Colab links** point at `github.com/RajatDandekar/agents-for-enterprises/…/lectures/L6-evals-guardrails-observability/NB6x.ipynb`
   and the notebooks install `ledgerline` from that repository: both work only after this work is pushed. In replay mode a
   notebook on Colab also fetches the recorded logs from the repository (`nbkit.REPO_RAW`).
3. Colab itself was not used for the tests (a clean Python 3.12 container on Modal stands in for it). Colab preinstalls many
   packages; the notebooks pin what they add, but a first run on real Colab before class is worth five minutes.
4. The Sentry and signed-in Langfuse captures (table above).
5. `SPEC.md` still describes the 16 Nov plan (three sections); `REVIEW_16NOV.md` and this log describe what was built.
6. Lecture 7's deck is parked, not reviewed: see `../L6b-guardrails/NOTES.md` ("Before this is taught").
7. Still open from v1: the old duplicate scores in Langfuse (`experiments/lf_clean_scores.py`), a real GitHub Actions run of the gate.

## QA (v2)
`qa_full_modal.py --slides all`: 103 slides, 0 with issues, 0 page errors; every slide read on contact sheets (twice).
Parked deck: 38 slides, 0 issues. `tools/world_v4.py --check` passes on the deck, NOTES, A6, the notebooks, the README and
the parked folder.

## Finishing pass (16 Nov, 15:10 to 16:00 UTC, after the account was topped up)
`sh experiments/v2_finish.sh` ran to the end; three things it found were fixed and re-run.

**What ran**
- The four demo turns re-sent to Langfuse, LangSmith and Sentry (`traces_v2.json`), read back (4 of 4 in each tool, tokens
  and cost equal to ours, Sentry's included now), scored, re-shot.
- All four notebooks, live through the Argus gateway and then in replay with no key: 0 errors in each
  (`nb/*.live.txt`, `nb/*.replay.txt`). NB6b and NB6c were run twice (fixes below).
- Argus API test: 27 of 27 (`argus_api_test.txt`), 12 screenshots re-recorded; Argus purged of test students, on Sonnet, cooled.
- QA: 103 slides, 0 issues, 0 page errors. No plate is pending except the two signed-in Langfuse ones (slides 35, 40).

**Found and fixed**
1. **NB6c, DeepEval's simulator** raised `asyncio.run() cannot be called from a running event loop` in a notebook (a
   notebook already runs a loop; so does Colab). The simulator now runs in a thread of its own.
2. **NB6c and NB6b, the hand-built judge** crashed once on a judge answer whose JSON was broken (an unescaped quote in the
   reason). `nbkit.read_verdict` now tries JSON, then reads the two fields by pattern, and raises if there is no verdict.
3. **The re-sent incident turn is a different run** (models are random): 8 spans, 3 model calls, 4 tool calls, 11.7 s,
   where the earlier one had 13 spans, 5 and 7, 14.7 s. Slides 32, 34, 35 and 37 had the old counts typed in; they now
   read them from `m.demo.incident`. The Langfuse tree no longer has a tool error, so that sentence went.
4. **Slide 63** quoted two replies cut with "…" under a subtitle saying nothing is shortened. It now quotes, whole, the
   line of each reply that the failed check objected to (`gen_figdata.py`, the `needle` map).
5. **Slide 75** cut the DeepEval reasons mid-sentence; it now shows whole sentences (`_whole`). Its last line now says
   what the recorded run showed: the "asked before saving" judge gave Thursday 0.9 and the good run 0.8.
6. **Slide 88, Ragas agent metrics**: in the recorded run the good prompt scored 0 on tool call accuracy (it previewed
   twice before saving: three calls against a reference of two) and Thursday scored 0.88; goal accuracy gave both 0. The
   slide, NOTES and a new cell in NB6d say so and say why. Not re-tuned to look better.
7. Hub: Lecture 6's row lists the four notebooks (NB6a to NB6d); `tools/build_site.sh` rewrites them to Colab links.

**Captured from signed-in Chrome**: Sentry (`figs/sentry/sn_incident_trace.png`, `sn_incident_commit.png`, `sn_agents.png`,
`sn_chat_span.png`, about 1,300 to 1,450 px wide). Langfuse was not signed in in that browser: slides 35 and 40 still wait.

**One slip**: NB6d's executed notebook lost its outputs to a stray `nbbuild.py` call. They were restored by a replay run
with `--save`, so NB6d's embedded copy says REPLAY (the other three say LIVE); the numbers are the live run's.

**Failed, unused**: two screenshots in `shots_v2.py` (`lf2_incident_scores`, `ls_incident_feedback`: a click timed out);
no slide uses them. Real Colab is still untried (needs the push).

**Spend**: finishing pass US$2.78; v2 US$10.51; Lecture 6 in all US$35.24 (`logs/spend.json`).


## Langfuse screens, Ragas live again, commit and push (17 Nov, 00:25 to 01:15 UTC)

**Langfuse, signed in** (Rajat signed in to Langfuse in Chrome): two captures, 1,204 px wide, dark theme (his setting; the
scripted Langfuse shots beside them are light). `figs/langfuse/lf_signed_in_generation.png` is the first model call of
Friday's trace with what it was sent and what it wrote (slide 35); `lf_signed_in_session.png` is the two-turn session
`l6-v2-good2-841898` (slide 40). No plate is pending now.

**NB6d live again**, so its embedded copy says LIVE like the other three (`logs/v2_ragas_live.out`; 8 code cells, 0
errors; US$0.27 through the Argus gateway). A live run re-records, so the numbers moved: tool call accuracy is now good
prompt 0, Thursday 1.0 (0.88 before); goal accuracy still 0 for both; question 1's faithfulness 0.88 (1.0 before). The
story on slide 88 holds for this run too (the good run previewed twice, in turn 1 and again in turn 2, before saving;
Thursday previewed and saved inside turn 1). The one sentence that quoted 0.88 was changed by hand in `NB6d_ragas.py`,
the `.ipynb`, `nb/NB6d_ragas.html` and NOTES (not through `nbbuild.py`, which would wipe the outputs). The old records
are not kept in the repository.

**The commit** holds this folder, the hub row, and the course code the notebooks install from GitHub: `course/l6`,
`hermes` (Ask Northbridge's engine), `argus`, the accounts-payable tool folders and `erp/payables*` that Hermes imports,
the Claude lines in `llm.py`, the `L6E_*` cassettes. Checked before committing: every `ledgerline` import reachable from
those files resolves to a committed file (106 files followed, 0 missing); no value from `.env` and no key-shaped string
in any staged file. Left uncommitted on purpose: other lectures' edits, `lectures/L6b-guardrails/`, the frameworks deck,
Proteus, the brochure, `tools/unlocked.txt`, the `_index/*.jsonl` caches.

**`experiments/colab_like_modal.py`** (new): after a push, runs the four notebooks the way a fresh Colab does: a bare
Python 3.12 container, the notebook downloaded from GitHub, the course pip-installed from GitHub by the notebook's own
first cell, no key. It cannot show a clash with a package Colab ships preinstalled.

**The laptop's disk filled up during this pass** (105 MB free at one point; commands could not start for a few minutes).
The Ragas run's files were checked afterwards: valid JSON, a complete notebook, a complete HTML page.

**QA after this pass**: 103 slides, 0 issues, 0 page errors (`logs/v2_finish_qa2.out`); `tools/world_v4.py --check` exit 0.

**After the push** (`ecfbe04`): `colab_like_modal.py` ran all four notebooks from GitHub in a bare Python 3.12 container, no key: NB6a 15 of 15 code cells, NB6b 11 of 11, NB6c 13 of 13, NB6d 8 of 8, 0 errors (`logs/colab_like.out`). Real Colab itself is still untried.
