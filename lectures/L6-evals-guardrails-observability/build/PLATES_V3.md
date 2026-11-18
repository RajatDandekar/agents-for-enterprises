# Plates of the 17 Nov review (v3): what still waits for a picture

Kept by builder B. Each plate on a slide is a `shot` figure with `data-pending`, so it shows a striped card naming its
file until the file exists. When a file lands in `figs/argus/`: run `python3 gen_figdata.py` (it lists the pictures the
deck may show), look at the picture with a coordinate grid, and set `data-crop="x,y,w,h"` (image pixels) on the figure so
the part named below fills the frame. The pictures are builder C's (`figs/argus/V3_SHOTS.md`).

| Slide | File | Frame on the slide (px) | `data-crop` (x,y,w,h in picture px) | What it shows | State |
|---|---|---|---|---|---|
| 52 One turn, four checks | `figs/argus/four_checks_friday.png` | 810 × 596 | `1185,860,1890,1390` | The four cards, two by two: Outcome PASS, Order of actions FAIL, Numbers PASS, The words FAIL, each with reads, asks and its reason. The turn itself is drawn on the slide beside it. | filled |
| 52, under the cards | the same file | 810 × 63 | `1183,2262,1892,146` | Argus's own line under the cards: "The end result is right and the order of actions is wrong..." | filled |
| 57 The words | `figs/argus/four_checks_judge.png` | 1400 × 123, a strip along the bottom | `0,885,2224,250` | The Run the judge button with its cost, and the verdict on Friday's turn (FAIL) with the reason first. The three parts of the prompt are drawn on the slide itself. | filled |
| 60 Live: two judges | `figs/argus/judge_right_naive.png` | 690 × 420 | `1480,1140,1600,905` | The four boxes after the naive judge, the sentence of counts, and the first reply of the opened box with the judge's reason. | filled |
| 60 Live: two judges | `figs/argus/judge_right_grounded.png` | 690 × 420 | `1480,1140,1600,905` | The same after the grounded judge. | filled |
| 62 DeepEval | `figs/argus/deepeval_tool.png` | 760 × 366 | `1165,700,1920,915` | The metric (ToolCorrectness and its two switches), the threshold, and the result: score, PASS, called and expected, DeepEval's reason. | filled |
| 62 DeepEval | `figs/argus/deepeval_geval.png` | 760 × 366 (covers the one above on a click) | `1165,700,1920,915` | The metric (GEval: name, criterion, model) and the result: score, PASS, DeepEval's reason. | filled |
| 77 The same three things, for a conversation | `figs/argus/convo_deepeval.png` | 810 × 184 | `1390,2585,1665,375` | The three metrics side by side, each with its score, pass or fail, and the first lines of its reason. | filled |
| 81 Live: a trace becomes a score | `figs/argus/trace_score_written.png` | 790 × 250 | `1270,590,1800,565` | The button, the red banner, and the line it leaves ("Written on this trace. Langfuse: score ... · LangSmith: feedback ..."). | filled |

**State on 17 Nov, 16:45.** All frames show C's retake (files of 16:14), taken after the two decisions below: the Outcome
card asks the end-state question and passes Friday's turn, and the recorded turns are the traced demo turns the slides
show. The retake changed three page layouts (the four cards are now two by two with a line under them; the judge's card
is narrower and is on Friday's turn; Score with DeepEval is a wide panel under the conversation), so the crops of slides
52, 57 and 77 were set again from the new pictures; the other five crops were checked and stand. If a picture is taken
again, re-read its slide: a card whose text grows or shrinks moves everything under it.

Not used on a slide: `figs/argus/four_checks_total.png` (C's extra: "A total nobody returned"; slide 55 draws that reply
itself, from the logs, and slide 58's notes name the Argus turn as a live option), and `deepeval_tool_friday.png`,
`deepeval_geval_friday.png` (the same form on Friday's turn, both FAIL; slide 62 gives those two results in its own table).

## Checked against the retake
1. **The Outcome card** on slide 52's picture says PASS, as slide 53 does.
2. **The reply** in the pictures of the four checks and of the judge's card is the traced demo turn (four tool calls, "The
   purchase request is raised, but nothing is ordered yet. It is waiting for Daniel's approval.").
3. **Live verdicts** in the pictures come from real model calls and differ a little from the recorded ones on the slides:
   slide 62's GEval picture shows 0.80 where NB6b recorded 1.00 for the same turn; slide 77's picture shows 0.90 for
   "asked before saving" where NB6c's good conversation recorded 1.00. Both pass. The slides' numbers come from the logs.
4. **Slide 81's picture** is a live turn in Traces (another wording of the reply, more tool calls), not the recorded
   trace whose Langfuse and LangSmith pictures sit under it. The slide's footnote says so.

## Plates from before this review
None left: every picture the v2 plates named (slides 11, 35, 37, 38, 40 and the Conversations slide, now 79) is in `figs/`.
