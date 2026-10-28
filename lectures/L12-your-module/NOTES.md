# Lecture 12 · Your Module: Demo Day: speaker notes

Sun 6 Dec 2026, 7:00–9:00 IST. 48 slides. Deck: `lectures/L12-your-module/index.html` (demo day was Lecture 8 before v3.1; the notebook keeps its file name, NB8). Every number on the plates
is filled from `figdata.js`, built by `gen_figdata.py` from `experiments/logs/` (and two logs of other lectures,
named on the plates). The morning's format is `DEMO_DAY.md`; the sheet is `rubric.md`; questions are
`question-bank.md`. Notebook: `NB8_your_module.ipynb` (replay, no key).

## Timing

| Part | Slides | Clock |
|---|---|---|
| Opening, cold open, today | 1–4 | 7:00–7:04 |
| 1 The whole build, by hand and on the industry stack | 5–18 | 7:04–7:15 |
| 2 Your module | 19–29 | 7:15–7:22 |
| 3 Demo day (rules, production stack) | 30–40 | 7:22–7:30 |
| Live slots (no slides) | | 7:30–8:36 |
| 4 The final demo | 41–48 | 8:36–9:00 |

## Plate by plate

1. **Title.** "Today the piece Ask Rasoi gains is yours."
2. **Last time, this time.** Lecture 11 put purchasing on a production runtime; today, one more department, by hand and on your own stack.
3. **Sunday at Rasoi.** Read Anand's letter. The rule he will change tonight already happened: the changes went out at 9 AM yesterday, at the end of Lecture 11.
4. **Today.** Four parts; the live slots sit between Parts 3 and 4.
5. **Part 1.**
6. **Every piece, lit (Fig. 1).** Point at each tag L1–L7: built by hand. Then: "Lectures 8–11 put each piece on the tools companies use." "Each box is code that ran today."
7. **The pieces, one line each.** Step through the eleven rows; name the folder for each. L8–L11 point at their lecture folders.
8. **Kavita's order, every piece.** Scrub the twelve messages (this is the recorded run of exactly what you will do live at 8:36). Point at the lecture tags on each tool. Totals: 32 model calls, 21 tool calls, ₹6.12.
9. **L1.** Lecture 1's own measurement of the careful Before: 12 screens, 27 fields, 12 codes, 3 sign-ins, 20 service calls, about 4.8 minutes by keystroke estimate. The After: twelve messages, no codes.
10. **L2.** Tokens read and written in the run; why reading dominates (schemas + history every call).
11. **L3.** Read the Shakti Seals reply aloud; the search_policy call underneath.
12. **L4.** The check_stock JSON; the request preview JSON. Say "Pune 54,000; with Chakan 66,000, 11 days": the tool now reports both.
13. **L5.** The pause and the resume; read the table: PR closed by its order, PO CLOSED, GRN/2026/30001 and 30002, Pune 74,000.
14. **L6.** The Studio: the same job as a workflow; the Studio now runs a kit's own toolbox. Open /studio if time allows.
15. **L7.** Users in Bahi's log: KJOSHI, NDESAI, RMEHTA only; six read-backs; Lecture 7's suite (3.8-flash, three runs): Experience prompt 6/18, SVC_AGENT 6/18 with 4 never-events, one-line fix 15/18, trust layer 14/18. Drill: 33 duplicates to 0.
16. **L8–L11, the industry stack.** Four cards: frameworks, protocols, observability and evals, production runtime, each with its flagship tools. Read the rule all four kept: Bahi a black box, writes through the tool folders in the speaker's own session. No numbers here: each lecture's own comparisons live in its folder.
17. **Every piece, and its industry tool.** The Lecture 1 stack map again (`stackfig.js`), opened on Trust. Click Harness, MCP and "rent the whole stack". "In Lecture 1 this was a promise; now you have built every box by hand and run it on the tool."
18. **Check yourself.**
19. **Part 2.**
20. **The recipe (Fig. 2).** Six moves.
21. **Move 1.** HR leave by hand: 7 calls, 3 screens, 13 fields; the HD trap.
22. **Move 2.** The four tool folders; `lint_folder()` clean; read the apply_leave tool.json.
23. **Move 2, the promises.** Walk the code: session, key, look-up, preview, timeout, receipt.
24. **Moves 3 and 4.** MCP server with search_policy beside it; the five documents; §5.2.
25. **Move 5 (leave grid).** 6 of 12: scenarios 1 and 3 every run; scenario 2 broke §5.2 every run (NE4); scenario 4 needs comp-off. Click a run of each. "This is where your A4–A7 work starts, and it is the HR student's demo-day change too."
26. **Move 6.** The kit's six never-events; how NE4 becomes a guard.
27. **Every kit, the same treatment.** Click through two or three kits, ideally the ones presenting live.
28. **What is checked automatically.** test_kits on Modal: all eight kits reference 4/4, naive 4/4, starter tool ok over MCP; TEMPLATE ok (its example write tool passes preview, commit, the key after a timeout).
29. **Check yourself.**
30. **Part 3.**
31. **The morning.** The clock.
32. **Inside an eight-minute slot.** Four segments; the two rules.
33. **The rubric (Fig. 3).** Seven lines now: production stack (10) is new, so scenario pass rate is 20 and operations 10. Click each line; the two overriding rules.
34. **Your production stack (rubric line 7, 10 points).** INTERACTIVE menu: click a layer to read it, click again to pick or drop it (Observability + Evals are picked to start). Two tools from two layers, `STACK.md` with a reason for each, one comparison measured on their own run. A tool that needs a paid account counts only with its recorded output. Writes still go through the tool folders.
35. **The demo-day change.** Policy vs variant; why a change at all.
36. **Eight changes, fair.** 8 of 8 re-run on Modal today.
37. **One change up close.** HR-CIR-2026-07: Friday's run fails (NE4, approved by Rohit), the careful run after passes (approved by Anand Patil), the careless run is caught (NE1 by SVC_AGENT and NE4).
38. **How the change is graded.** The grade_change.py command, in replay.
39. **The client's questions.** Read two; point at the bank.
40. **The recorded demo.** Rules.
— **Live slots, 7:30–8:36.** Keep the slot timer visible. After each slot: one line of feedback, the hidden test's verdict.
41. **Part 4.**
42. **Live.** Run the twelve messages in the Experience as Kavita, Rohit, Neha with "How it works" on. If it hangs, go back to plate 8.
43. **Rohit's inbox.** His session; two items waiting (an older lid order and Kavita's request); he approves one by number.
44. **The final numbers.** From the recorded run; compare with Lecture 1's Before.
45. **What production grade means here.** Read both columns; the "not yet" column is as important as the first.
46. **What comes next.**
47. **Where we are.** Every piece yours.
48. **Over to you.**

## Numbers and their logs

| Plate | Number | Log |
|---|---|---|
| 8, 10–13, 15, 44 | the final demo: turns, tools, tokens, ₹, Bahi's state, users | `experiments/logs/final_demo.json` |
| 9, 44 | the careful Before: 12 screens, 27 fields, 12 codes, 3 sign-ins, 20 calls, 4.8 min | `experiments/logs/from_other_lectures/L1_before_measure.json` (Lecture 1's own log) |
| 15 | the L7 suite and drill | `lectures/L7-trust/experiments/logs/six_flash.json`, `retry_drill_after_fix.json` |
| 21, 27, 28 | each kit's careful path, traps, scenario runs, starter tool | `experiments/logs/test_kits.log` (copy of `modules/test_kits.log`) |
| 22, 25 | lint clean; 6/12 on HR leave, per scenario | `experiments/logs/leave_askrasoi.json` |
| 36, 37 | 8 of 8 changes fair; the HR change's three runs | `experiments/logs/demo_changes.json` |
| 16, 17, 34 | no numbers: the tools per layer and lecture | `COURSE_V3.md` (v3.1) and `INDUSTRY_TOOLS_PLAN.md`; the stack map is the lead's master figure `figures/ask_rasoi_architecture_wide.png` (copied to `figs/ask_rasoi_stack_base.jpg`) with `stackfig.js` |

## Known gaps

- The HR leave reference toolbox covers scenarios 1 and 3 only; scenarios 2 (§5.2 forward to the plant head) and 4
  (comp-off) fail by design and are named as the students' work.
- Runs went through OpenRouter for the same Gemini models (the direct key ran out of credit on 28 Oct).
- The L8–L11 plates name tools and what each lecture does with them, but quote no results: those lectures were being
  built in parallel on 28 Oct. Add their measured comparisons here once their logs exist.
- Cassettes keep their v3 names (`L8v3_final_*`, `L8v3_leave*`); the new L8 (frameworks) must not reuse those names.
