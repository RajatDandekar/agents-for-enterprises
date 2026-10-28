# Lecture 8 · Your Module: the demo-day run sheet

For Dr. Rajat Dandekar. **Sunday 22 November 2026, 7:00–9:00 AM IST.** Website topic: *Build and present your domain
pilot.* Everything here runs on Modal; nothing runs on the laptop.

## What is in this folder

| File | What it is |
|---|---|
| `index.html` + `figs.js` + `figdata.js` | The deck: 34 plates. `figdata.js` is generated from the logs by `gen_figdata.py` |
| `DEMO_DAY.md` | The format and timing, the slot, the eight changes, the recorded-demo instructions |
| `rubric.md` | The scoring sheet (/100), one per module |
| `question-bank.md` | The client's questions: a general bank, four per module, and the reference system's |
| `experiments/test_demo_changes.py` | Proves each change is fair (log: `experiments/logs/demo_changes.json`) |
| `experiments/grade_change.py` | Runs a module's hidden test on a student's agent (6 of the change's 10 points) |
| `../../modules/<name>/CHANGE.md`, `demo_change.py` | The eight changes and their hidden tests; contract in `../../modules/demo_day.py` |
| `../../demo/` | The final demo: `final_demo.py`, `scorecard.py`, `shots_modal.py`, `WALKTHROUGH.md`, `logs/`, `shots/` |

## Saturday 21 November

**9:00 AM, end of Lecture 7.** Announce the eight changes. Read each kit's quote from its `CHANGE.md` (section "What
the client says"); students get the two files with the kit.

**Evening.**
1. Collect the A6 scorecards. Pick the live presenters: up to two per kit, highest pass rate with no never-event,
   plus one wildcard. Post the slot order by 9 PM.
2. Re-run the reference system once, so the logs on the plates are fresh (no key needed, under a minute each):
   ```
   cd /Users/raj/Claude_Brain/enterprise-agents-course
   /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/final_demo.py --mode replay
   /Users/raj/.venv/bin/modal run tools/modal_run.py --script demo/scorecard.py --mode replay
   /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/gen_figdata.py
   ```
   Expect `JOURNEY OK`, `DEMO OK`, and `PASS · candidate 57/60`. If a number changed, the deck changes with it
   (it reads `figdata.js`).
3. **11:59 PM:** recorded demos due (MP4 + repo link + their own `grade_change.py` output).

## Sunday 22 November

**6:30 AM. Before the room opens.**
- Open the deck: `lectures/L8-your-module/index.html` (from the course hub, or any static server on the course folder).
- The live close runs from the deck plates and the stills in `demo/shots/` (the walkthrough is timed against them).
  A public URL for the app is not set up; see "Not built".
- Have `rubric.md` printed or open, one copy per live module, and `question-bank.md`.
- Grader's terminal ready in the course folder, with each live student's `make_agent` spec.

**7:00–7:05 · Opening.** Plates 1–3, then plate 5 (format) and 6 (the slot). Say the two rules: numbers from your
logs; a never-event zeroes the scenario.

**7:05–8:25 · The live slots (8 minutes each).** For each module:

| Minute | You | The grader |
|---|---|---|
| 0:00 | "Your before." | Starts `grade_change.py` for this module (below) |
| 1:00 | "Your after." | Watches the audit: any service-account write? |
| 3:00 | "Where does last night's rule live now?" | |
| 5:00 | Read the hidden test's PASS or FAIL aloud | Shows the result on screen |
| 5:00–8:00 | Two general questions, two from the module's list (`question-bank.md`) | Notes the answers on the sheet |

```
/Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/experiments/grade_change.py \
    --args "--module <kit> --agent py:<student_package.module>:make_agent" --mode replay
```
If the student's cassette misses a reply, re-run with `--mode auto` (uses the course Gemini key; a few paise).
Sanity check of the grader itself: `--agent reference` passes all eight, `--agent friday` fails all eight
(both measured, `experiments/logs/grade_all_reference.json`, `grade_all_friday.json`).

Keep time strictly: a buzzer at 7:30 of each slot.

**8:25–8:50 · The reference system.** Plates 21–31, spoken from `demo/WALKTHROUGH.md` (six minutes), then the
plates in order:

| Plate | What to show | Number to say | Source |
|---|---|---|---|
| 22 The before | the two legacy stills | 8 screens, 17 fields, 8 codes, 2 sign-ins, 14 calls; SAVED but DR | L1 `by_hand.json` |
| 23 The system | click each layer | (none) | |
| 24 The sentence | scrub the steps: Kavita 1, 2, 3 | one question (cost centre), one confirmation | `demo/logs/journey.json` |
| 25 One tap | inbox and Slack stills | her self-approval refused, HTTP 403 | same |
| 26 Released | the PO JSON and 13 checks | PO/2026/01182 RL, ₹2,80,840, 12 model calls, ₹0.28 | same |
| 27 Audit trail | filter "writes", then "people" | 20 entries, 62 Bahi rows, KJOSHI and RMEHTA only | same |
| 28 Crash drill | step through | 30 h with no worker, 1 request, 1 order | `demo/logs/crash_drill.json` |
| 29 Kill switch | step through | 40 min paused, 0 orders while off | `demo/logs/kill_switch.json` |
| 30 Scorecard | bars, then the table | 57/60, 86–98%, 0 never-events, ₹0.43, gate PASS | `demo/logs/scorecard.json` |
| 31 Honestly | the three failures, the bars missed | V10, V11, M02; p95 32.04 s vs 20 s | same |

**8:50–9:00 · Next.** Plates 32–34: the production-grade checklist (two items half done, one missed), what comes
next, nine of nine jobs. Announce the module reviews, 23 Nov–6 Dec.

## If something goes wrong

| What | Do |
|---|---|
| A student's live run hangs | Let them say what happened and show their replay or `drills.json`; that is the operations line |
| Modal is unreachable | Grade the change from the student's own `grade_change.py` output (recorded track) and re-run after class |
| The reference system cannot be served live | Use the stills (`demo/shots/`) and plates 24–30; they are built from the same logs |
| A number on a plate looks wrong | It is read from `demo/logs/*.json` via `figdata.js`; re-run step 2 above |

## Measured for this lecture (all on Modal, 27 Oct 2026)

| What | Result | Log |
|---|---|---|
| Fairness of the 8 changes | 8 of 8 fair: Friday's run fails, the new run passes, naive caught, kit's 4 still pass, all 8 kits together pass | `experiments/logs/demo_changes.json` |
| Kavita's order over HTTP (uvicorn + httpx, MCP tools, Temporal workflow) | 13 of 13 checks; PO/2026/01182 RL; replayed with no key | `demo/logs/journey.json` |
| Crash while waiting | 30 h with no worker; reminder sent after restart; 1 request, 1 order | `demo/logs/crash_drill.json` |
| Kill switch | 40 min paused, 0 orders; then 1 released | `demo/logs/kill_switch.json` |
| Final scorecard (AuthorityAgent, Lecture 6 suite, model Kavita) | 57/60, 95% 86–98%, 0 never-events, ₹0.43 per resolved order, p95 32.04 s; gate PASS (strict) vs L6 graph 56/60 | `demo/logs/scorecard.json`, `scorecard_gate.json`, `scorecard_suite.json` |
| The same suite with Lecture 6's runner unchanged (nobody opens the app inbox) | 49/60; the 8 new-supplier cases wait on an onboarding file | `demo/logs/scorecard_no_inbox.json` |
| Screenshots | 5 legacy, 7 app, headless Chromium on Modal | `demo/shots/`, `demo/shots/shots_log.txt` |

## Not built

- A public URL for the reference app on the day. `deploy/modal_app.py` (Lecture 7's) is written but not deployed,
  needs the lead's go-ahead, and serves `bahi.server` (the sandbox API and legacy client), not the Lecture 5 app:
  `deploy/app.py` would have to build `bahi.app.main.create_app()` instead. Until then the close runs from the
  stills and the plates, which come from the same logs.
- A model-driven agent for any capstone kit: the change tests use scripted runs. Students' agents are the first
  model-driven runs of the hidden tests.
- GPT and Claude comparisons (need an OpenRouter key); Langfuse export (needs keys; traces stay local).
