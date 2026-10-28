# Demo day: format, timing, the change, the recorded demo

**Lecture 8, From Forms to Agents · Sunday 22 November 2026, 7:00–9:00 AM IST.** Website topic: *Build and present
your domain pilot.*

Each student shows their module's before and after, absorbs a change announced at the end of Lecture 7, and answers
the client. Dr. Dandekar plays the client: the plant head, or whoever owns the module's money. The last half hour is
the full Bahi reference system, live.

## 1. The morning

| Time | What | Who |
|---|---|---|
| 7:00–7:05 | The rules of the morning; the slot order | Dr. Dandekar |
| 7:05–8:25 | 8 to 10 live modules, 8 minutes each, back to back (10 × 8 = 80 min) | Students; Dr. Dandekar as client |
| 8:25–8:50 | The reference system, live: Kavita's sentence to a released order, the crash drill, the kill switch, the scorecard | Dr. Dandekar (`demo/WALKTHROUGH.md`) |
| 8:50–9:00 | What comes next: multi-agent systems, small fine-tuned routers, more modules; the module reviews (23 Nov–6 Dec) | Dr. Dandekar |

With 8 live modules the slots end at 8:09 and the spare 16 minutes go to longer question rounds.

**Who presents live.** Up to two modules per kit, chosen on Saturday evening from the A6 scorecards: the highest
pass rate with no never-event per kit, then one wildcard (an invented module from `modules/TEMPLATE`, if any is
ready). Everyone else submits a recorded demo (section 4). Both are graded on the same sheet (`rubric.md`).

## 2. Inside an eight-minute slot

No slides. You run the real thing on the shared Bahi sandbox: the legacy screens, then your agent.

| Minute | Show | Say |
|---|---|---|
| 0:00–1:00 | **The before.** Your careful legacy path on the real screens (the legacy client at `/legacy`, your module installed), and the silent outcome | Your A1 counts: screens, fields, codes, people. "Bahi says SAVED. It is HD. Nobody hears." |
| 1:00–3:00 | **The after.** Your one sentence, live. The one question your agent asks. The approver's tap in his own session. The read-back | What the harness did that the form used to do, job by job |
| 3:00–5:00 | **The change.** Where the new rule (or the new path) now lives: the document in your corpus, the gate, the matrix row | The grader runs the hidden test on your agent meanwhile; at 5:00 its PASS or FAIL goes on the screen |
| 5:00–8:00 | **The client's questions.** Three minutes | Answer from your logs: `scorecard.json`, `drills.json`, the audit trail |

Rules: every number you say comes from your own logs. If the live run hangs, say so and show the replay; the
operations line rewards the honest recovery more than a smooth demo.

## 3. The demo-day change

At the end of Lecture 7 (Saturday 21 Nov, about 9 AM) each kit's change is announced in the client's words. The
student has one evening to absorb it.

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

Each change is two files in `modules/<name>/`:
- `CHANGE.md`: the announcement, what changes, what to do (mapped to A2–A7), and what the hidden test checks;
- `demo_change.py`: the new document's text (`DOC`), the data side (`apply`), the hidden scenario (`SCENARIO`), the
  code check (`check`), and three scripted runs: Friday's careful run (`OLD`), the careful run after the change
  (`NEW`) and a careless one (`NAIVE`). The contract is in `modules/demo_day.py`.

**Fairness, measured.** Before announcing, each change was run on Modal against its kit's reference run
(`experiments/test_demo_changes.py` → `experiments/logs/demo_changes.json`): for all 8 kits, Friday's careful run
fails the hidden test, the careful run after the change passes, the careless run is caught, the kit's own four
scenarios still pass with the change in place, and the hidden scenario passes with all eight kits installed.

**Grading the change on demo day:**

```
/Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/experiments/grade_change.py \
    --args "--module hr_leave --agent py:<student_package.module>:make_agent" --mode replay
```

It prints PASS or FAIL and the 6 points, and writes `experiments/logs/grade_<module>_<agent>.json` with the
transcript the other 4 points are judged from. The student's cassettes must hold the hidden scenario's replies: they
run it once in `auto` mode on Saturday night (they know the scenario from `CHANGE.md`), and the grader replays it.

## 4. The five-minute recorded demo

For every module not presenting live. Same rubric.

| Time | Show |
|---|---|
| 0:00–1:00 | The before: your legacy path on the real screens, with your A1 counts on screen |
| 1:00–2:30 | The after: the sentence, the one question, the approver's tap, the read-back |
| 2:30–4:00 | The change: the new rule in your corpus (or the new path in your graph), the hidden scenario run, its result |
| 4:00–5:00 | The proof: your scorecard and one drill, opened from the JSON files |

- One take, screen and voice, 1080p, at most 5:30. No edits that hide a failure.
- Upload the MP4 and your repo link by **Saturday 21 November, 11:59 PM IST**.
- Include `grade_change.py`'s output for your module, run once by you in replay mode.
- The grader re-runs your four scenarios and your hidden test in replay mode. A recording whose numbers do not match
  the replay scores the lower of the two.
- The grader adds one general and one module question from `question-bank.md` in writing; answer each in two lines,
  from your logs, by Monday 23 November.

## 5. What a finished module contains

| Layer | Assignment | The file the grader opens | Rubric line |
|---|---|---|---|
| The story: before timed, after sentence, nine-jobs table | A1 | A1.md, your timings | shown first |
| The manual: retrieval with a 20-question test | A2 | `retrieval_eval.json`, `questions.py` | retrieval 15 |
| The hands: 5–8 tools and an MCP server | A3 | `tools.yaml`, contract tests | tools 20 |
| The route: control graph, router, memory policy | A4 | `route_spec`, graph | route and authority 15 |
| The signature: approvals, receipts, read-back, audit | A5 | audit log of 4 scenarios | route and authority 15 |
| The inspector: 30 scenarios, broken bots, a scorecard | A6 | `scorecard.json` | scenario pass rate 25, operations |
| The night shift: four drills and a runbook | A7 | `drills.json`, `runbook.md` | operations 15 |
| The change, absorbed overnight | L7 → L8 | `grade_change.py` output | demo-day change 10 |
