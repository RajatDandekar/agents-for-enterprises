# Lecture 6 · Rajat's review of 16 Nov 2026 (v1 deck, 112 slides) and the v2 plan

Slide numbers are the v1 deck's (the `N / 112` counter).

## The review, in Rajat's words

- In Slide 6, what does 61% mean?
- Slide 11 is confusing
- Slide 17, not clear, what is lacks not clear - difficult to understand from code!
- Slides 20, 21, 22 are complex to understand, make it simple, maybe take an example
- Slide 25, input and output are not appearing in the form
- I want to show them this by actually opening up langfuse or showing a colab notebook, where we do this together! Embed notebook in page
- Slide 27, input and output are empty
- Did not understand slide 28, no trace is coming
- Slide 30, should come before phoenix, also this slide is meaningless, unless i show them using a descriptive and nicely written colab notebook
- Phoenix part should come after langfuse part is completed
- In this section explain span, trace, generation etc more simply, so my audience can understand better, also I want to do this live in front of them, either colab or if any other way production-level projects are done, I would like to do that.
- I want to show them a demo using sentry and langsmith using actual chatbot data, so I want to execute prompts on chatbot and show traces on right, for all actually, langsmith, etc, ignore phoenix for now, since no one seems to be using it in production.
- In fact, I want to start this lecture in this way, and then explain the theoretical concepts through the practical demo.
- Henrik letter and motivation at start is good!
- I just noticed that the traces section in Argus is a good way to explain the theory!
- Slide 50, the LLM as a judge instructions are not coming clearly, also I did not understand slide 48 and 49, what is the main point of the slides?
- I am not sure in which case would we use LLM as a judge here? Explain these slides clearly.
- Slide 52, words are cutoff, it is hard to understand, why it failed.
- pass^k would only matter if some subjectivity is there right, otherwise everything would be fully objective?
- Are slides 55 and 56, related to slide 54?
- Also, I want to actually show them Deep Eval, either as google colab or by something else! So add link etc
- Slide 57-63 is very interested, how to do evals on multi-turn conversations..This also I want to simulate from scratch in class, this is what they want to learn!
- So, langfuse is also used for evals??
- I want this lecture to only contain Sections 1 and 2, defer the remaining to the next lecture!
- Let us show Ragas demo also, I WANT TO show all of them this in the class!

## What v2 is

**Lecture 6 = Observability and Evals only.** Guardrails, red-teaming, "Ask Northbridge, trusted" and the guards
station move out to the next lecture (parked in `lectures/L6b-guardrails/`, numbered when Rajat confirms the schedule).
The lecture is **demo-first**: after Henrik's letter and the incident, Rajat chats with Ask Northbridge on the left and
the trace appears on the right, first in Argus, then the same turn in LangSmith, Langfuse and Sentry. Theory (span,
trace, generation, session, score) is explained **from that live trace**, in plain words, one idea per slide, with
Argus's Traces station as the teaching picture. Phoenix is out of this lecture.

Everything Rajat wants to show is something the class can do with him: Argus stations and Colab notebooks, each with an
"Open in Colab" link and a rendered copy embedded in the deck.

## Slide-by-slide answers and fixes

| v1 slide | Problem | v2 |
|---|---|---|
| 6 | "61%" unexplained | Say it in words on the slide: without a date the Thursday prompt fails 3 runs in 20 (15%), so three manual tries all look fine with probability 0.85³ = 61%. Show the sum. |
| 11 | Confusing (four cards of build provenance) | Cut from the main flow; one line in NOTES, or one plain sentence on the lab slide. |
| 17 | The tracer code is unreadable; "what it lacks" unclear | Teach by example, not code first: run three nested steps, show the three records it printed (name, start, end, parent), then the tree. The code moves to the notebook (students run it live). "What it lacks" becomes a 3-row table with a plain example for each: agreed names, somewhere to send it, a screen to read it. |
| 20–22 | Too complex | One running example (Emma's "order the usual" turn). 20: "three lines to switch tracing on" + what appears. 21: "four labels we attach to every turn" (who, which chat, which prompt version, cost) with the real values and the question each answers. 22: "what must not go in a trace": one before/after of a card number masked. |
| 25, 27 | Input and Output empty in Langfuse | A real bug: the screenshots show `undefined`. Set input and output on the root, generation and tool spans so Langfuse (and LangSmith) render them; re-run; re-shoot. |
| 28 | "No trace is coming" | Same cause (empty panels, small crop). Re-shoot after the fix, full-size, with the two turns side by side and the preview/commit spans labelled. |
| 30 | Out of place; meaningless without a demo | Moves to the end of the Langfuse part as the bridge to evals, and becomes a guided tour in the notebook and live (sessions, scores, datasets, prompt versions), each with a screenshot. |
| 29, 31, 32 | Phoenix | Removed from this lecture. |
| 48–49 | Point unclear | One clear message per slide. 48: "money: check it with code": the agent said £285,600, no tool ever returned it, code flags it. 49: "when the judge and the code disagree, read both": one worked case, then the rule. |
| 50 | Judge instructions unreadable; when to use a judge unclear | First a slide "when do we need an LLM judge here?": a table of Emma's cases, code-checkable vs words-only (e.g. "did it say the order is waiting for Daniel, not placed?"). Then the judge prompt, large, in three labelled parts (criterion, evidence, reply), with one real verdict. |
| 52 | Words cut off; reason unclear | Rebuild as one row per failing task: what Emma asked, what it did, the check that failed, in full sentences; nothing truncated. |
| 53 | pass^k confused with subjectivity | Add the missing step: the checks are objective, the **agent** is random (same input, different tool calls). Show the same task run 5 times with different outcomes; then pass^k. |
| 54–56 | Order confusing | Reorder: judge → is the judge right (55, 56) → then DeepEval as the tool that packages code checks + judges. Say explicitly that calibration applies to any judge, DeepEval's included. |
| 54 | Wants DeepEval live | A Colab notebook run in class, linked and embedded. |
| 57–63 | Wants multi-turn evals from scratch | Becomes its own sub-section, built up in class: scripted turns → a simulated user (a model plays Emma with a goal) → scoring the whole conversation (end state, order of actions, did it ask only what it needed) → the same in DeepEval's conversational tools and in Langfuse sessions. A notebook and an Argus panel. |
| 62–63 | "So Langfuse is also used for evals?" | Yes: say so on a slide ("Langfuse does two jobs": traces, and evals on those traces: scores, datasets, experiments, judges, annotation queues). Same for LangSmith. Sentry is monitoring only. |
| new | Ragas | A Ragas demo in class (notebook): retrieval metrics on the policy search (faithfulness, context precision/recall) and its agent metrics (tool call accuracy, goal accuracy), with Claude as the judge. |
| 72–105 | Guardrails | Moved to the next lecture. |
