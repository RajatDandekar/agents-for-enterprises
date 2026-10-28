# Demo day: format, timing, the change, the final demo

**Lecture 8, AI Agents for Enterprises · Sunday 22 November 2026, 7:00–9:00 AM IST.**

Each student shows their module's Before and After on the shared Rasoi, absorbs a change announced the evening
before, and answers the client. Dr. Dandekar plays the client: Anand Patil, or whoever owns the module's money.
The last part of the morning is Ask Rasoi itself, live, end to end.

Everything is fictional: Rasoi Steel Works, Bahi ERP 7.2, the people and the data.

## 1. The morning

| Time | What | Who |
|---|---|---|
| 7:00–7:30 | The deck, Parts 1–3: the whole build as one figure, Kavita's order through every piece, the six moves, the rules of the morning | Dr. Dandekar |
| 7:30–8:36 | Live modules, 8 minutes each, back to back (up to 8 slots = 64 minutes, plus changeovers) | Students; Dr. Dandekar as the client |
| 8:36–8:55 | The deck, Part 4: the final demo, Ask Rasoi live from Kavita's first question to Neha's goods receipt (section 6) | Dr. Dandekar |
| 8:55–9:00 | What comes next; how recorded demos are graded | Dr. Dandekar |

With fewer live slots, the spare minutes go to longer question rounds.

**Who presents live.** Up to two modules per kit, chosen on Saturday night from the A7 suites: the highest pass
rate with no never-event per kit, then one wildcard (an invented module from `modules/TEMPLATE`, if one is ready).
Everyone else submits a recorded demo (section 4). Both are graded on the same sheet (`rubric.md`).

## 2. Inside an eight-minute slot

No slides. You run the real thing on the shared Rasoi: your module's legacy screens, then Ask Rasoi on your toolbox.

| Minute | Show | Say |
|---|---|---|
| 0:00–1:00 | **The Before.** Your careful legacy path on the screens, and the silent outcome | Your counts (screens, fields, codes, people). "Bahi says SAVED. It is held. Nobody hears." |
| 1:00–3:00 | **The After.** Your one sentence, live, in the speaker's own session. The preview, the approver in their own session, the receipt read back | Which piece did what: tools, knowledge, the loop, the trust layer |
| 3:00–5:00 | **The change.** Where the new rule (or path) now lives: the document, the tool argument, the guard | The grader runs the hidden test on your agent meanwhile; its PASS or FAIL goes on screen at 5:00 |
| 5:00–8:00 | **The client's questions.** Three minutes (`question-bank.md`) | Answer from your logs: the suite's results, the gate verdict, the recovery check, Bahi's call log |

Rules: every number you say comes from your own logs. If the live run hangs, say so and show the replay; the
operations line rewards an honest recovery more than a smooth demo.

## 3. The demo-day change

At 9 AM on Saturday 21 November (the end of Lecture 7), each kit's change is announced in the client's words, in
`modules/<kit>/CHANGE.md`. You have one evening to absorb it.

| Module | Kind | Circular | The change |
|---|---|---|---|
| Purchasing · amend PO | policy | PUR-CIR-2026-11 | No deliveries on 12 and 13 November: stock count |
| Finance · payables | variant | FIN-CIR-2026-05 | Lot invoices: one order, one invoice per delivery lot |
| HR · leave | policy | HR-CIR-2026-07 | Purchase staff join the Diwali-run rule |
| Sales · orders | variant | CIR-SAL-2026-16 | Advance-paid top-ups for customers on credit hold |
| Service · warranty | policy | SVC-CIR-2026-04 | Free gasket swap for the 1–15 September lot |
| Inventory · transfers | variant | STR-CIR-2026-04 | A second 5-litre line at Chakan |
| Travel · claims | policy | FIN-CIR-2026-11 | Company travel cards replace cash advances |
| Legal · contracts | variant | LEG-CIR-2026-02 | A tooling loan agreement when our mould goes out for a trial |

A **policy** is a rule that lives only in a document; Bahi does not check it. A **variant** is a path through the
module's screens that Bahi supports and the module never took.

**What absorbing it means in the v3 build:**
1. **Knowledge:** add the circular (`DOC` in `demo_change.py`) to your documents and re-index; add one retrieval test.
2. **Tools:** if the change needs a new argument or a new activity, add it to the tool folder (for HR leave:
   a `forward_to` on `apply_leave`, passed to Bahi's `fwd_to`), keeping the six promises.
3. **Trust:** add a guard for the new never-event, with a rule and a next step.
4. **Evals:** add the hidden scenario (it is in `CHANGE.md`) as a fifth case in your suite, run it three times, and
   gate the change against your Friday baseline: nothing that passed may break.

**Fairness, measured.** Before announcing, each change was run on Modal against its kit with scripted agents
(`experiments/test_demo_changes.py` → `experiments/logs/demo_changes.json`, re-run on 28 Oct against the current
kits): for all 8 kits, Friday's careful run fails the hidden test, the careful run after the change passes, the
careless run is caught, the kit's own four scenarios still pass with the change in place, and the hidden scenario
passes with all eight kits installed together.

**Grading the change on demo day (10 points):**

```
/Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/experiments/grade_change.py \
    --args "--module hr_leave --agent py:<your_package.module>:make_agent" --mode replay
```

It prints PASS or FAIL (6 points) and writes `experiments/logs/grade_<module>_<agent>.json` with the transcript.
The other 4 points: where the change lives, the new case in your suite, the gate run. Your cassettes must hold the
hidden scenario's replies: run it once in `auto` mode on Saturday night (you know the scenario from `CHANGE.md`).

## 4. The five-minute recorded demo

For every module not presenting live. Same sheet.

| Time | Show |
|---|---|
| 0:00–1:00 | The Before on the real screens, with your counts on screen |
| 1:00–2:30 | The After: the sentence, the preview, the approver's own session, the read-back |
| 2:30–4:00 | The change: the new rule in your knowledge or tools, the hidden scenario run, its result |
| 4:00–5:00 | The proof: your suite's 12 runs, the gate verdict, the recovery check, opened from the files |

- One take, screen and voice, 1080p, at most 5:30. No edits that hide a failure.
- Upload the MP4 and your repository link by **Saturday 21 November, 11:59 PM IST**.
- Include `grade_change.py`'s output for your module, run once by you in replay mode.
- The grader re-runs your four scenarios and the hidden test in replay mode. A recording whose numbers do not match
  the replay scores the lower of the two.
- The grader adds one general and one module question from `question-bank.md` in writing; answer each in two lines,
  from your logs, by Monday 23 November.

## 5. What a finished module contains (v3)

| Piece | Assignment | The file the grader opens | Rubric line |
|---|---|---|---|
| The Before measured; the After you want | A1 | A1 note | shown first |
| What the bare model cannot do for your module | A2 | A2 note | (foundation) |
| Knowledge: your documents indexed, cited, the stale one handled | A3 | retrieval results | retrieval 15 |
| Tool folders (`tool.json` + `tool.py`), the six promises, MCP | A4 | your tool folder, `a4_wire.json` | tools 20 |
| The harness: your prompt, three scenarios, the pause | A5 | A5 table and traces | scenario 25, route and authority 15, operations 15 |
| Workflows and your own agent in the Studio | A6 | workflow JSON, run logs | scenario, operations |
| Trust: identity, guards, read-back, suite, judge, gate, trace, recovery | A7 | `results.json`, `NOTE.md` | route and authority, operations, scenario |
| The change, absorbed overnight | L7 → L8 | `grade_change.py` output | demo-day change 10 |

Every kit's starter tool and the plan for its After are in `modules/<kit>/README.md` ("The After") and
`bahi/bahi/modules/<kit>/toolbox/`. `modules/test_kits.py` must stay green on your kit:
`/Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py --args "--only <kit>"`.

## 6. The final demo (8:36–8:55)

Ask Rasoi on the live Experience (`https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=agent`),
"How it works" switched on so the tool cards show. Three people, one Rasoi, each in their own session:

| # | Who | Says | What the room should see |
|---|---|---|---|
| 1 | Kavita | "How many 5-litre silicone gaskets do we have at Pune, and how many days will they last?" | `check_stock`: Pune 54,000; with Chakan 66,000, 11 days |
| 2 | Kavita | "Shakti Seals in Vadodara quotes ₹10.40. Can we buy the gaskets from them?" | `search_policy`, the clauses cited; no order |
| 3 | Kavita | "Then reorder 20,000 from Deccan Polymers at the contract rate. Charge PRD-07, need-by 2 November." | A request preview: ₹2,69,040 estimate, approver Rohit |
| 4 | Kavita | "Yes, go ahead." | PR/2026/04417 WAITING FOR APPROVAL |
| 5 | Rohit | "What is waiting for my approval?" | His inbox, in his session |
| 6 | Rohit | "Approve PR/2026/04417." | Approved, read back |
| 7 | Kavita | "Rohit has approved PR/2026/04417." | PO/2026/01182, ₹2,80,840, RELEASED to Deccan |
| 8–11 | Neha | 12,000 arrived; yes; the other 8,000; yes | GRN/2026/30001 and 30002; the order CLOSED |
| 12 | Kavita | "What is the status of PO/2026/01182 now?" | CLOSED: everything received |

Our recorded run of exactly these messages (`experiments/logs/final_demo.json`, gemini-3.8-flash, trust layer on):
32 model calls, 21 tool calls, 1,21,357 tokens, ₹6.12; Bahi's call log shows only KJOSHI, RMEHTA and NDESAI. If the
live run hangs, plate 8 of the deck scrubs through the recorded one, and NB8 section 1 replays it with no key.

Before the class: `modal run deploy/experience_modal.py::admin --cmd status` (spend, players, flags). Do not
redeploy during the class.
