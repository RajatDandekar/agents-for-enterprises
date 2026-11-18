# Lecture 6 · Rajat's review of 17 Nov 2026 (v2 deck, 103 slides) and the v3 plan for Part 2

Slide numbers are the v2 deck's (the `N / 103` counter) as it stood on 17 Nov, 14:30.

## The review, in Rajat's words

Morning (already fixed in `index.html`, see NOTES.md for slides 4, 6, 23, 27, 32, 33, 34, 40):
- Slide 4: where does it say raised?
- Slide 6: confusing
- I am on slide 23, is there a notebook associated with it
- In slide 32, I can see how it appears in LangSmith. I also opened the public link. If people ask how it got there in the first place? Also, I do not see "feedback" in public link
- Once we have the LangSmith key and address for OpenTelemetry, where do we store it, and how are traces automatically generated, how did you do it for Argus?
- Slide 33 has empty input and output
- For Langfuse you have not added live URL for people to see? a public link?
- Slide 40, which path should I click?

Afternoon (this plan):
- Did not understand slide 54
- Did not understand slide 57
- Make them simpler, which human can understand easily, maybe take different examples
- Slide 58, confusing, slide 59 confusion is good, maybe start with that, Cohen's kappa formula is confusing
- Slides 51 to 59, I want to drive through practical example. For example, the "conversation" tab in Argus, helps to understand the code, judge etc all these types properly, maybe create something similar accompanying these slides.
- DeepEval Colab notebook is tough to go through, I want to understand in an easy way how to set Tool correctness, GEval which you have mentioned in DeepEval, what my classmates have to set from their side, make it simple, maybe drive through Argus, would be much better, keep it in the Colab notebook, but I would show Argus in class.
- Same with DeepEval in slide 75.
- I did not understand slide 76, is it needed?
- Slide 79, would be great to see a demo of this, we already have the traces opened up for LangSmith and Langfuse, how to convert to scores?
- promptfoo, where can I see directly public link, I can see you have a screenshot
- I want a flowchart towards the end regarding how observability and evals can be clubbed together.

## What this means

1. **One running example for the scorers (slides 51 to 59), shown live in Argus.** The class already knows Friday's turn
   ("Order the usual, please, needed by 4 Dec 2026." under the Thursday prompt). Every scorer is taught on that one turn,
   then on the good two-turn chat for contrast: what Ledgerline holds (code), the order of the tool calls (code), every £
   figure against the tool results (code), the words (a judge). No new task ids (T03, T14, T20) as the lead example.
2. **Argus gets the teaching views** (builder C), in the Evals station, in the style of the Conversations station:
   - **One turn, four checks.** Pick a recorded turn (Friday's turn; the good chat's two turns; a reply with a figure no
     tool returned) or "my last chat turn" from Traces. Each check is a card: what it reads, the question, the verdict, the
     reason. The judge's card shows its prompt in three parts (criterion, evidence, reply); the criterion can be edited and
     the evidence switched off, and "Run the judge" calls Claude Haiku. Switching the evidence off is the lesson of
     slide 59 done by hand.
   - **Is the judge right?** A small labelled set (replies marked right or wrong by a person, some with a planted error).
     Run the naive judge, then the grounded one; the four boxes (right and passed, right and failed, wrong and failed,
     wrong and passed) fill in. Plain counts, no formula.
   - **The same checks in DeepEval.** Three things you set, as a form filled in from the chosen turn: the test case
     (input, actual output, tools called, expected tools), the metric (ToolCorrectness; or GEval with a criterion you
     type and Claude Haiku as its model), the threshold. Run: score, pass or fail, reason, from the real library. Below it,
     the same thing as the few lines of Python the notebook has.
   - **Conversations: "Score with DeepEval".** On a finished simulated conversation: the conversation as DeepEval's test
     case and its conversational metrics (knowledge retention, completeness, your own criterion), beside our five checks.
   - **Traces: "Write the score on this trace".** Runs the code check "saved without a yes?" on the turn and writes the
     verdict to Langfuse (a score) and LangSmith (feedback) through their APIs; then the "Open in" buttons show it there.
3. **Deck (builder B), in `index.html` directly** (`build/build.py` is stale and refuses to run):
   - 54: one rule, one picture. The figures the tools returned as chips; the reply with each £ figure marked found or not
     found. One counter-example with a figure nobody returned. Nothing about the judge on this slide.
   - 57: three steps with a picture: two verdicts on one reply (code says fail, judge says pass), we open the trace, the
     bug was in our check. Start from an everyday comparison (two examiners, one answer sheet).
   - 58 then 59: start from the four boxes with a tiny example, then the three judges' tables. No formula. Kappa is one
     plain sentence at most ("one number that sums up the table: 1 is perfect, 0 is no better than guessing").
   - 60 and 75: "three things you set" in DeepEval, with the Argus panel as the picture and the live step.
   - 76: cut (its one useful sentence, "every simulated conversation is a session in the tools", moves to a neighbour).
   - 79: followed by a live demo slide: a trace becomes a score, in numbered steps (Argus button, then LangSmith's
     Feedback and Langfuse's Scores).
   - 85: a link to promptfoo's own report of our run (`figs/promptfoo/results.html`), beside the screenshot.
   - A flowchart near the end: how observability and evals work together (run → traces → read them → scores → the
     failures become test cases → the suite and the gate on every change → ship → online scores on live traces → back
     to reading). It builds step by step.
4. **NB6b** keeps everything, with its DeepEval section rewritten around the same "three things you set" (after the
   notebook builder is free).
