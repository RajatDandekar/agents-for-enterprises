# Daedalus: the workshop (Lecture 5, live)

**Live URL:** https://rajatworkspace--northbridge-daedalus.us-east.modal.run
(the class wall for the projector: `/wall`; the operator's page: `/admin`)

Modal app `northbridge-daedalus`, workspace rajatworkspace, deployed from `deploy/daedalus_modal.py`. Contract:
`lectures/L5-the-loop/DAEDALUS_SPEC.md`. Patterns copied from Hephaestus (Lecture 4); Hephaestus is not touched.

## What a student does
A student types a name and gets **their workshop**: a secret key (`dx-…`, kept in the browser), their own Ledgerline
sandbox (Mon 26 Oct 2026, 09:00; Emma Clarke, ECLARKE), their own agent settings and their own workflow.

1. **The Loop.** Send Emma's order; **Next step** runs one turn of the loop (one model call, then the tools it asked
   for); every step shows the model's words (often none), each call with its arguments and result, tokens, seconds and
   the harness's own lines (step n of max, tokens of budget, "paused: … waits for DOKAFOR", the end reason). **Run to
   the end**, **Next morning** (the agent saved as JSON, thrown away, rebuilt from the JSON), **New conversation**,
   **Fresh sandbox**.
2. **Your agent.** The harness knobs: max steps (2 / 4 / 12 / 25), token budget (6,000 / 60,000 / none), tools (2 / the
   shipped 11 / all 16, or one by one), system prompt (Ask Northbridge's / one line / your own), approval pause, error
   recovery. **Run the six jobs** (fresh sandboxes, scored in code) and **Your runs**.
3. **Your workflow.** Eleven blocks (read the request, find the item, check stock, find the supplier, check the
   certificate, check the budget, raise the request, wait for approval, create the order, release it, tell Emma): move,
   remove, add; options (certificate gate: stop / use the preferred supplier; stock: stop if cover ≥ N days; retries on
   a lost reply). **Run** or **Run step by step** on any of the six jobs or your own words; **Flaky Ledgerline**; a
   waiting run is shown as the saved JSON it is; **Resume** after Daniel signs.
4. **The race.** Workflow (once) against agent (once or three times) on the six jobs, each in a fresh Ledgerline,
   Emma and Daniel scripted the same for both (`race.py`), scored from Ledgerline's tables; "same path?" per job.
- **Daniel's inbox** (every tab): approve or reject as DOKAFOR with his own permissions; **Ledgerline now** lists the
  sandbox's requests and orders.
- **The wall:** per student: loop steps watched, best six-job score, workflow blocks, race workflow vs agent (and
  tokens), waiting runs resumed, nights.

## The six jobs (`jobs.json`)
spring (waits for Daniel, then released with Voltway) · bells (within Emma's limit, released with Pennine Brakes) ·
nordic (no order with Nordic Cell Co.: expired UN 38.3; Ledgerline itself would accept it) · closed (PRD-05: nothing
saved) · fallback (Nordic not allowed → a certified supplier, after Daniel) · question (Voltway at £119.00, nothing saved).

## Measured (`lectures/L5-the-loop/experiments/logs/`)
- `daedalus_api_test.json`: 24 / 24 checks on the live URL (loop step by step, pause, night, "not signed yet" answered
  with 0 model calls, inbox, the morning finishing the job, knobs, workflow wait/sign/resume, step by step, a missing
  block named, the race, the wall, admin token).
- `daedalus_knobs.json`: each harness knob (one change, 2 runs) and four workflow changes, on the deployed app. Shipped
  agent 6, 6 of 6 at ~124,000 tokens; max steps 2 → 2, 2; budget 6,000 → 3, 4; 2 tools → 2, 3; all 16 tools 6, 6 at +35%
  tokens; one-line prompt 6, 5 at +80% tokens; pause off and recovery off 6, 6. Workflow shipped 4 of 6 at 1,241 tokens;
  no certificate gate 3 (ordered from Nordic); no approval step 3; no budget gate 4; certificate gate "use the preferred
  supplier" 5.
- `daedalus_load_40.json`: 40 students at once: join median 0.56 s, one loop step 4.4 s (p90 5.9), a workflow run 2.2 s,
  then all 40 pressed Start the race together: 40 / 40 finished, median 70 s (max 88 s), every agent 6 / 6, every workflow
  4 / 6, 0 failed model calls.

## Running it in class
```
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd purge-tests   # remove Probe/Load/Test/Film/Shot/Knob workshops
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd warm          # keep one container on (30 min before class)
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd status
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd pause --reason "back in 5 minutes"   # or resume
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd cap --cap 60          # class US$ a day (default 40)
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd student-cap --cap 2   # per student (default 1.5)
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd purge-all     # an empty wall
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::admin --cmd cool          # after class (a cron also does it, 04:00 UTC)
```
- Limits per student: 40 loop steps a minute, 12 "run to the end" a minute, 6 six-job runs and 4 races per 10 minutes,
  40 workflow actions a minute; at most 48 model calls in flight in the container. One race costs about US$0.07 (agent
  ×1) and the workflow about US$0.002; a class of 40 doing two races each is about US$6.
- Keys only from the Modal secret `rasoi-experience`; the OpenRouter key is removed at start; the fallback model is
  gemini-3.5-flash-lite direct (shown per step in the trace).
- `min_containers=0` in the file. **Do not redeploy during class**: sandboxes, conversations and running races live in
  the one container. Names, settings, workflows, saved workflow runs, six-job runs and races survive in the modal.Dict
  `northbridge-daedalus-state`; a restart re-seeds a fresh sandbox (a waiting workflow run then finds no request: press
  Fresh sandbox and run it again).

## Tests and jobs
```
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::test                    # 24 checks on the live URL (live model)
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::knobs --repeats 2       # every knob, measured on the live app
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::load --n 40             # 40 students at once
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::record --which figs,loop,night,knob,workflow,wfwait,race
/Users/raj/.venv/bin/modal run deploy/daedalus_modal.py::sheets                  # contact sheets of the recordings
```
Recordings and screenshots land in `lectures/L5-the-loop/films/daedalus_*.mp4` (gitignored) and
`lectures/L5-the-loop/figs/daedalus/*.png` (Playwright on Modal, 1600×900; screenshots at 2×).

## Files
| File | What |
|---|---|
| `loop.py` | `Agent`: the loop one step at a time (`say`, `step`, `respond`) and the harness knobs; `state()` / `from_state()` |
| `smallest.py` | the fifteen-line loop with no harness (the deck and NB5) |
| `react.py` | ReAct as text and its parser |
| `workflow.py` | the blocks, gates, the approval step (a waiting run is JSON), retries, `resume` |
| `race.py`, `jobs.json` | the six jobs, scripted Emma and Daniel, scoring from Ledgerline's tables |
| `app.py` | FastAPI: workshops, guard (pause, caps, rate limits, model slots), jobs, inbox, wall, admin |
| `static/` | `daedalus.html/js/css`, `dx.js`, `wall.html`, `admin.html` (on the Experience's `sky.css`) |

## Found and fixed while building (11 Nov)
- Error recovery's "never repeat a failed call" also refused a retry after a **lost reply** (a timeout after the save):
  the agent stopped with the request saved and no order, 0 / 2. Recovery now remembers refusals, not timeouts; 2 / 2
  after (`logs/recover_before.json`, `logs/recover.json`).
- The scripted Emma first treated "let me know if…" as a question and said "Yes, go ahead." after she had said "leave
  it": a scripting bug, fixed before any measurement in the deck (`race.py`: `QUESTION`, a job's own answer ends it).
