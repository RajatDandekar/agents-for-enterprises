# Demo day: the scoring sheet (/100)

**Lecture 8, From Forms to Agents.** One sheet per module, live or recorded. The grader fills it from the student's
own files and from two re-runs done on Modal in replay mode (no key): the module's four scenarios and the hidden
demo-day test (`experiments/grade_change.py`).

Module: ____________________  Student(s): ____________________  Live / recorded: ______  Grader: ______

## Two rules that override the rest

1. A never-event in any scenario zeroes that scenario's points, however good the rest is.
2. A number said in the demo that does not match the student's own log, or the replay, scores the lower of the two.

Where two assignments feed one line (A4 and A5 both feed route and authority; A6 and A7 both feed operations), this
sheet takes each assignment's items at the weights below. Each assignment page describes its items in full.

## 1. Scenario pass rate · 25 (A3–A6, earned on demo day)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The four kit scenarios pass on the student's agent, replayed | 8 (2 each) | `run_module_scenario` for scenarios 1–4, replay mode | |
| 30 cases derived from the route spec, each with a code check and a log | 6 | A6 suite file | |
| The measured pass rate with its 95% interval (scripted and model user) | 7 | `scorecard.json`: 7 × the interval's lower end | |
| Broken-bot matrix: each bot caught by its metric | 4 | A6 broken-bot log | |
| **Subtotal** | **25** | | |

## 2. Tools · 20 (A3)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The tool contract across all tools, one point per item: types, errors with a next step, preview, idempotency key, receipt, validate once, the user's permissions, timeout and retry, version | 9 | Tool code or `tools.yaml`; `contract_audit()` | |
| The two contract tests pass (silent outcome reported as such; a lost reply leaves exactly one document) | 5 | The notebook, replay mode | |
| A façade: several services, one call, a read-back | 3 | One tool's trace | |
| The MCP server listed and called | 3 | The MCP listing and one call | |
| **Subtotal** | **20** | | |

## 3. Route and authority · 15 (A4, A5)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Route spec complete and matching the graph that runs; gates enumerable, rules cited (A4) | 4 | `route_spec`, the path of each scenario | |
| Never-events refused in code: preview and confirm key, a guard per never-event, each with an adversarial run it refused (A4, A5) | 4 | The guard and its refusals | |
| Passthrough identity and scopes; no service-account write anywhere (A5) | 3 | Bahi's call log: users seen | |
| Approvals in the approver's own session, read back from Bahi; waits as interrupts (A4, A5) | 2 | Approval rows; one refused self-approval | |
| Read-back after every write and the joined audit log (A5) | 2 | The audit log of the four scenarios | |
| **Subtotal** | **15** | | |

## 4. Retrieval · 15 (A2)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Corpus: front-matter complete, clauses numbered, an amendment and a restricted page | 4 | `docs/*.md` | |
| Test set: 20 questions in A2's mix, gold clauses, graded by code | 4 | `questions.py` | |
| Results: correct and cited on rule questions, zero leaks, three traps refused, tokens per answer | 4 | The A2 results table | |
| The tool plugged into the agent, with one scenario transcript that cites a clause | 3 | A scenario transcript | |
| **Subtotal** | **15** | | |

## 5. Operations · 15 (A6, A7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Four drills pass (D1–D4); a duplicate from any drill scores 0 for that drill (A7) | 5 | `drills.json` | |
| Keys from content; look-up before and after the write; only retryable errors retried (A7) | 2 | `night_shift.py` | |
| A one-page runbook with the module's duplicates query (A7) | 2 | `runbook.md` | |
| Waits: a `WaitPolicy` with a reason per number, or a running workflow with a signal and two timers (A7) | 2 | `night_shift.py`, workflow history | |
| Traces, p95 seconds per turn and ₹ per resolved request reported (A6) | 2 | `scorecard.json` | |
| Versions and a working regression gate (A6) | 2 | One gate verdict | |
| **Subtotal** | **15** | | |

## 6. The demo-day change · 10 (announced at the end of Lecture 7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The hidden test passes, with no never-event | 6 | `grade_change.py --module <name> --agent py:<package.module:make_agent>` | |
| The new document is in the corpus and the 20-question test (for a variant: the new path is in the graph or a tool) | 2 | The corpus and `questions.py` | |
| The reply names the rule or the variant it applied | 2 | The hidden test's transcript | |
| **Subtotal** | **10** | | |

## Total

| Line | Max | Score |
|---|---|---|
| Scenario pass rate | 25 | |
| Tools | 20 | |
| Route and authority | 15 | |
| Retrieval | 15 | |
| Operations | 15 | |
| Demo-day change | 10 | |
| **Total** | **100** | |

Questions asked in the slot, and how they were answered (not scored; noted for the module reviews, 23 Nov–6 Dec):

1. ____________________________________________
2. ____________________________________________
3. ____________________________________________
