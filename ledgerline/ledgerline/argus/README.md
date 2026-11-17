# Argus: the lab for Lecture 6 (Observability and Evals) and Lecture 7 (Guardrails), live

**Live URL:** https://rajatworkspace--northbridge-argus.us-east.modal.run
(the class wall for the projector: `/wall`; the operator's page: `/admin`)

Modal app `northbridge-argus`, workspace rajatworkspace, deployed from `deploy/argus_modal.py`. Contract:
`lectures/L6-evals-guardrails-observability/SPEC.md` ("The lab: Argus"). Rails copied from Hermes (Store, budget Guard,
GuardedLLM are imported from `ledgerline.hermes.app`; Hermes is not changed).

## What a student does
Joins with a name and gets a key (`ar-…`, kept in the browser) and their own Ask Northbridge: Lecture 5's Finale
(`ledgerline.course.l6.agent.Agent`: the same prompt, 26 tools, Emma's memory, `claude-sonnet-5-5`) in a fresh Ledgerline
sandbox at Fri 20 Nov 2026, 09:10. Every tab has a guide (try, notice, next).

Stations since Lecture 6 v2 (16 Nov 2026, after the review): **Traces, Evals, Conversations**. The Guards station belongs to Lecture 7
and is hidden behind a flag (below).

1. **Traces.** Chat as Emma. Every turn is an OpenTelemetry trace, drawn beside the chat as a span tree with timings,
   tokens, cost, and each span's input and output (click a row). The same spans go to every tool whose key was present at
   deploy time: **Langfuse, LangSmith, Sentry**; buttons under the trace open that turn in each ("Open in Langfuse",
   "Open in LangSmith", "Open in Sentry"; a tool with no key gets no button). Prompt switch: good · Thursday · my edit
   (a student's own system prompt, with a diff view). A turn that saves a purchase request without a yes is flagged in red.
2. **Evals.** The quick suite (T01, T02, T04, T08, T09, T14 of the class suite) or pass^3 on T01, under good, Thursday or
   the student's own prompt. Per task: outcome, order of actions, numbers (code) and words (Claude Haiku judge) with
   reasons; a "would ship" verdict; our recorded full-suite results for comparison.
3. **Conversations.** Multi-turn evals. Pick a goal (five: the usual; changes her mind; a closed cost centre; a vague ask;
   pushes for the cheaper supplier) and a persona (terse, chatty, impatient). A simulated Emma (Claude Haiku, given the goal,
   what she knows and the persona: `course/l6/convo.py`) talks to the student's agent in a fresh sandbox; the conversation
   is then scored on five checks: end state in Ledgerline, order of actions across turns, turn budget (code), asked only
   what it needed, last word matches Ledgerline (judge). `POST /api/convo/run`. The wall counts conversations per goal.
4. **Guards (Lecture 7; off by default).** Nine guards, twenty attacks or the student's own. With the flag off the tab is
   hidden and `/api/guards/attack` answers 404. Switch it with `--cmd guards-on` / `--cmd guards-off` (or env `ARGUS_GUARDS=1`
   at deploy). Nothing of it was removed.

**Notebook key and the gateway.** The button "Notebook key" shows the two lines a Lecture 6 notebook needs (`ARGUS_URL`,
`ARGUS_KEY`). With them, the notebook's model calls go through Argus's gateway, so a student needs no model key of their own:
- `POST /gateway/v1/messages` (Anthropic-compatible) and `POST /gateway/v1/chat/completions` (OpenAI-compatible);
  `GET /gateway` describes it.
- The key is the student's own `ar-…` join key (`x-api-key` or `Authorization: Bearer`). Anything else: 401.
- Only the course's two models (`claude-sonnet-5-5`, `claude-haiku-5-5`); any other: 400. No streaming (400).
  `temperature`, `top_p`, `top_k` are dropped; `max_tokens` is capped at 8,192.
- Every call is charged to the same per-student and class budget caps as the stations, and rate-limited (240 a minute).

## Running it in class
```
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd purge-tests   # remove Probe/Load/Test/Shot labs
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd warm          # 30 minutes before class (guard models warm in ~20 s)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd status
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd pause --reason "back in 5 minutes"   # or resume
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd cap --cap 80          # class US$ a day (default 60)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd student-cap --cap 3   # per student (default 2.50)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd sonnet        # make sure the agent is on Sonnet (after a load test)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd guards-on     # Lecture 7: show the Guards station (guards-off hides it)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd purge-all     # an empty wall
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::admin --cmd cool          # after class (a cron also does it, 04:00 UTC)
```
- Cost guide (measured on the live app): a chat turn about US$0.05–0.10, the quick suite about US$0.55–0.70, pass^3 about
  US$0.40, an attack about US$0.05–0.10. 40 students doing a bit of everything: plan US$60–100; raise the class cap.
- Rate limits per student: 20 chat turns and 20 attacks a minute, 3 eval runs per 10 minutes; at most 64 model calls in
  flight in the container (Hermes's slot semaphore).
- Keys: ANTHROPIC_API_KEY from the Modal secret `forge-anthropic`; the admin token from `rasoi-experience`; the tracing keys
  (Langfuse; `LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`; `SENTRY_DSN`, `SENTRY_ORG`) from the course `.env`, sent as a Modal secret
  at deploy time (`modal.Secret.from_dict`). Each is optional: a missing one switches that tool off silently. Never in the
  image, never printed. `/healthz` lists the back ends that are on.
- **If every answer is "credit balance is too low"**: the Anthropic account behind `forge-anthropic` is out of credit
  (it happened on 16 Nov during the build). Top it up; nothing in Argus needs changing.
- `min_containers=0` in the file. **Do not redeploy during class.** Names, chats, eval runs and attack results survive in
  the modal.Dict `northbridge-argus-state`; the sandbox and the in-memory span trees do not.

## Tests and jobs
```
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::test         # API test on the live URL (live model): 23 checks
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::load --n 30  # 30 students at once (agent switched to Haiku, then back)
/Users/raj/.venv/bin/modal run deploy/argus_modal.py::record       # screenshots of every station -> figs/argus/
```
Measured 16 Nov 2026 (v1, with the Guards station on): API test 23/23; load test 30/30 students, no errors, chat turn p95
5.9 s, attack p95 15.0 s. v2 (later on 16 Nov): the Conversations station, the gateway and the guards flag were tested locally with a
scripted model (join, chat, conversation, gateway refusals, flag on and off) and the gateway live (both endpoints; NB6a ran
top to bottom through it). The live API test and the screenshots for Conversations wait for model credit.

## Files
| File | What |
|---|---|
| `app.py` | the FastAPI app: join, the stations, the gateway, the wall, admin; one shared OTel provider (memory + every configured tool) |
| `static/argus.html`, `argus.js`, `argus.css` | the page (vanilla JS); `wall.html`, `admin.html` |
| `recorded.json` | the recorded full-suite and incident results shown in Evals (written by `experiments/gen_recorded.py`) |
| `../course/l6/` | the agent wrapper, tracing (Langfuse, LangSmith, Sentry), the simulated user and conversation scoring (`convo.py`), the notebooks' helper (`nbkit.py`), suite, judges; guards and attacks (Lecture 7) |
