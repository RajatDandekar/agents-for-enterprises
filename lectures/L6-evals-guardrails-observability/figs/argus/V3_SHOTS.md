# Argus v3 teaching views: the pictures in this folder (builder C)

Status (17 Nov 2026, evening): **all taken.** They are of the changed Argus running in a Modal container (not the deployed
app), guards flag off, real models (Claude Sonnet as the agent, Claude Haiku as the judge and inside DeepEval), the whole
page at 1600 wide, 2x (so 3200 px wide), except the judge's card. They will be retaken on the live app after the deploy.
How they were made: `experiments/argus_v3_record.py` through `experiments/argus_v3_modal.py::record`; what each run saw is
in `experiments/logs/argus_v3_record.json`.

Where the views live in Argus
- **Evals station**: a second row of buttons under the tabs: `The suite` (what was there, still the default) ·
  `One turn, four checks` · `Is the judge right?` · `The same checks in DeepEval`. Direct links: `#evals:turn`,
  `#evals:judge`, `#evals:deepeval`.
- **Conversations station**: a wide panel "Score with DeepEval" under a finished conversation.
- **Traces station**: a button "Write the score on this trace" beside the "Open in ..." buttons of a turn's trace.

Two decisions of 17 Nov that these pictures follow
1. **The Outcome card asks the end-state question on every turn** ("After this conversation, does Ledgerline hold exactly
   what Emma wanted: one request, 2,400 BAT-500 on PRD-03, waiting for Daniel, and nothing else?", the suite's
   `one_request`). On Friday's turn it **passes**. Friday's turn reads: Outcome PASS · Order of actions FAIL · Numbers
   PASS · The words FAIL, and an amber line under the cards says the lesson of slides 52 to 54. The good chat passes all four.
2. **One recording of Friday's turn.** Argus's recorded "Friday's turn" is the deck's traced demo turn (`traces_v2.json`,
   run `incident`, trace `284e50f50d129629b1291c26d103059a`: find_supplier, check_budget, a preview, a save; the reply
   begins "The purchase request is raised, but nothing is ordered yet."), with its Open-in links. The good chat's two
   turns are run `good2` of the same log. The fourth turn is the suite's T19 reply, as on slide 55.

| File (size in px) | Station · view | What it shows | The part a slide wants: x, y, w, h in image px |
|---|---|---|---|
| `four_checks_friday.png` (3200 × 3750) | Evals · One turn, four checks | Friday's turn chosen. Left: the turn (source line and Open in Langfuse / LangSmith / Sentry for that trace, Emma's message, the four tool calls in order, the reply with its four £ figures marked found, Ledgerline at the end: PR/2026/04417). Right: the four cards in a 2 × 2 block, each with reads, asks, PASS or FAIL and the reason: Outcome PASS, Order of actions FAIL, Numbers PASS, The words FAIL; under them the amber "Notice" line. Below: the judge's prompt in three parts with the recorded verdict. No model call was made for this picture. | the four cards and the Notice line: `1179, 860, 1893, 1551` (the cards alone: the top 1,380 px of that box) |
| `four_checks_judge.png` (2224 × 1158) | Evals · One turn, four checks | The judge's panel alone, on Friday's turn, taken in a narrower window so the text is large: the fixed instructions, then 1 the criterion (NB6b's sentence, editable), 2 the evidence (what find_supplier returned, …; its on/off switch), 3 the reply to check; the "Run the judge" button with its cost; a live verdict (FAIL) with the reason first. One Haiku call, US$0.0004. | the whole picture |
| `four_checks_total.png` (3200 × 4300), extra | Evals · One turn, four checks | "A total nobody returned" (the suite's T19 reply): Outcome PASS, Order PASS, Numbers FAIL (ten order values found in list_open_orders, the total £1,108,000 in no tool result, marked red in the reply), The words PASS (the judge checked the sum). Not used on a slide. | the four cards: `1179, 860, 1893, 1718` |
| `judge_right_naive.png` (3200 × 3388) | Evals · Is the judge right? | The twelve labelled replies (left) after "Run the naive judge": the four boxes 6 / 2 / 2 / 2 (right and passed · right but failed: a false alarm · wrong but passed: missed · wrong and failed: caught), the sentence "It caught 2 of 4 wrong replies, and raised 2 false alarms in 8 right replies.", the "missed" box opened with the judge's reasons; below, our recorded run on all 56 for the three judges as small tables. | the panel with the boxes: `1470, 1132, 1602, 1241`; the boxes and the sentence are its top 800 px |
| `judge_right_grounded.png` (3200 × 3804) | Evals · Is the judge right? | The same after "Run the grounded judge": 8 / 0 / 0 / 4, "It caught 4 of 4 wrong replies, and raised 0 false alarms in 8 right replies.", the "caught" box opened. | the same box: `1470, 1132, 1602, 1658`; the same top 800 px as the naive picture |
| `deepeval_tool.png` (3200 × 3904) | Evals · The same checks in DeepEval | The form filled in from the good chat's first turn, as NB6b's `test_case(turn)`: 1 the test case (input, actual_output, tools_called = `create_purchase_request(confirm=false)`, expected_tools = the same, marked "you set this"), 2 the metric ToolCorrectness with its two switches on (compare the arguments too; exact match), 3 the threshold 1. Result from the real library (DeepEval 4.3.4): 1.00, PASS, the called and expected lines, DeepEval's reason. Below, full width: the same thing as Python. | the form and the result: `128, 710, 2944, 1322` |
| `deepeval_geval.png` (3200 × 4268) | Evals · The same checks in DeepEval | The same form with GEval: name "Asks before saving", NB6b's criterion, model claude-haiku-5-5, the context switch off, threshold 0.5. Result in this take: 0.90, PASS, the reason (NB6b's own recording scored 1.00; in the bench's other runs 0.8 to 1.0). | `128, 710, 2944, 1606` (the same origin as the tool picture) |
| `deepeval_tool_friday.png` (3200 × 3944), extra | Evals · The same checks in DeepEval | Friday's turn: called `create_purchase_request(confirm=false), create_purchase_request(confirm=true)` against expected `create_purchase_request(confirm=false)`: 0.00, FAIL. | `128, 710, 2944, 1322` |
| `deepeval_geval_friday.png` (3200 × 4310), extra | Evals · The same checks in DeepEval | GEval on Friday's turn: 0.10, FAIL, the reason (the reply reports the request as raised). NB6b's own recording scored 0.20. | `128, 710, 2944, 1606` |
| `convo_deepeval.png` (3200 × 3740) | Conversations | A finished simulated conversation (the usual, terse Emma, good prompt; our five checks pass, top right) and, under the conversation, the wide panel "Score with DeepEval": the three things set (the test case, the metrics with the editable criterion, the threshold) and three metric cards side by side with score, pass and reason: Knowledge retention 1.00, Conversation completeness 1.00, ConversationalGEval · Asked before saving 1.00; then our five checks as one row and "What each side read". | the panel: `840, 2268, 2232, 1312`; the three metric cards are its middle band |
| `trace_score_written.png` (3200 × 3150) | Traces | A Thursday-prompt turn (saved without a yes) after "Write the score on this trace": the button and the Open in Langfuse / LangSmith buttons, the teal line "Written on this trace. Langfuse: score commit_without_yes = true · LangSmith: feedback commit_without_yes = 1.00" with the rule of the code check in a sentence, then the red incident banner and the trace. | the buttons, the line and the banner: `1262, 588, 1808, 484` |

Notes for the deck
- Verdicts and reasons in the live pictures come from real model calls and differ a little between takes; the recorded
  turns' three code results do not change. The numbers on the slides come from the logs, not from these pictures.
- The judge's question on Friday's turn and on the good chat's first turn is NB6b's own criterion, word for word; the
  DeepEval form builds the test case the way NB6b's `test_case(turn)` does, with NB6b's two ToolCorrectness switches.
  NB6b runs on its own recordings of the two turns (`nb6b_*_t02.json`); Argus and the slides use the traced demo turns.
  Same scores for ToolCorrectness (1.0 and 0.0); GEval agrees on pass and fail.
- The header still says "Lecture 6 · Observability and Evals" (the guards flag is off in these pictures).
- If `traces_v2.json` is ever recorded again, Argus's copy is rebuilt (`argus_v3_modal.py::gen`) and the pictures retaken.
