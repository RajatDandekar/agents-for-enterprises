# Demo day: the scoring sheet (/100)

**Lecture 8, AI Agents for Enterprises (From Forms to Agents, v3).** One sheet per module, live or recorded. The
grader fills it from the student's own files and from two re-runs on Modal in replay mode (no key): the module's four
scenarios on the student's agent, and the hidden demo-day test (`experiments/grade_change.py`).

Module: ____________________  Student(s): ____________________  Live / recorded: ______  Grader: ______

## Two rules that override the rest

1. A never-event in any scenario zeroes that scenario's points, however good the rest is.
2. A number said in the demo that does not match the student's own log, or the replay, scores the lower of the two.

Each line below is fed by the assignments named in it. An assignment's own page gives its items in full; this sheet
takes them at the weights shown, so the lines add up to 100.

## 1. Scenario pass rate · 25 (A5, A6, A7; earned on demo day)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The four kit scenarios pass on the student's agent, replayed | 8 (2 each) | `run_module_scenario` for scenarios 1–4, replay mode | |
| The A7 suite: four scenarios × three runs, code checks on Bahi | 9 | `results.json`: 9 × (runs passed / 12) | |
| A5's three harness scenarios (S1–S3) pass with the full harness | 5 | A5 pass/fail table | |
| A6: the jobs a workflow now handles end in the right state | 3 | A6 run logs (first and second run) | |
| **Subtotal** | **25** | | |

## 2. Tools · 20 (A4)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Tool design: business activities, not services; descriptions a model can choose by; schemas complete | 6 | The `tool.json` files; `lint_folder()` clean | |
| The six promises in every tool: typed inputs, errors with `next_step`, preview, a key from the content, a receipt read back from Bahi, the user's own session | 6 | Tool code | |
| Lost-reply test: exactly one document after an injected `timeout_after_commit` | 4 | The notebook, replay mode | |
| Served over MCP in the speaker's session, wire captured | 2 | `a4_wire.json` | |
| Write-up: the tool you chose not to write | 2 | A4 note | |
| **Subtotal** | **20** | | |

## 3. Route and authority · 15 (A5, A7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The pause: an approval wait saved, resumed only on Bahi's word (A5) | 5 | The paused scenario's trace | |
| Identity: the speaker's own session everywhere; no service-account write (A7) | 3 | Bahi's call log: users seen | |
| A guard per never-event, each shown refusing a real call with a rule and a next step (A7) | 4 | The guard and its refusals | |
| Read-back: the silent outcome caught and never reported as done; the reply check (A7) | 3 | One run of the silent outcome | |
| **Subtotal** | **15** | | |

## 4. Retrieval · 15 (A3)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| As A3's own grading: the corpus indexed, the test questions graded by code, citations, the stale document handled, who may read what | 15 | A3 results and transcript | |
| **Subtotal** | **15** | | |

## 5. Operations · 15 (A5, A6, A7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| An LLM judge beside the code checks, every disagreement explained (A7) | 3 | `NOTE.md` | |
| One change gated, the verdict pasted and acted on (A7) | 3 | The gate output | |
| One failing trace read, the wrong step named (A7) | 3 | The trace | |
| Workflows safe to run twice; run logs complete; replay works (A6) | 3 | A6 logs | |
| Bare vs harness table with calls, tokens and ₹ (A5) | 3 | A5 table | |
| **Subtotal** | **15** | | |

## 6. The demo-day change · 10

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The hidden test passes on the student's agent | 6 | `grade_change.py --module <kit> --agent py:<pkg>:make_agent --mode replay` | |
| Where the change now lives (document, tool, guard), one new case in the suite, and the gate run showing nothing else broke | 4 | The demo, the suite file, the gate output | |
| **Subtotal** | **10** | | |

**Total: ____ / 100**

## Live and recorded, the same sheet

Live slots are 8 minutes (`DEMO_DAY.md`). A recorded demo is 5 minutes, one take; the grader re-runs everything in
replay mode, and a recording whose numbers do not match the replay scores the lower of the two.
