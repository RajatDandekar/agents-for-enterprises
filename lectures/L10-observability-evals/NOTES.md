# Lecture 10 · Observability and Evals in Industry: speaker notes

Sun 29 Nov 2026, 7:00–9:00 IST. 60 slides (55 plates, 3 part slides, title and next time). Deck:
`lectures/L10-observability-evals/index.html`. Every number on the plates is filled from `figdata.js`, which
`gen_figdata.py` builds from `experiments/logs/`. Notebook: `NB10_observability_evals.ipynb` (replay, no key).
Live demo: `https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=agent`, plus the public Langfuse
trace linked from plate 18 (opens without a login). Have Phoenix running locally (`phoenix serve`) if you want to show
it live; otherwise the screenshots are real.

## Timing

| Part | Slides | Minutes |
|---|---|---|
| Opening, Monday at Rasoi, the map, the gap | 1–5 | 0:00–0:10 |
| 1 See it: spans, OpenTelemetry, GenAI names, Langfuse, Phoenix, the market | 6–29 | 0:10–0:55 |
| 2 Test it: DeepEval and the CI gate, Ragas, promptfoo | 30–45 | 0:55–1:35 |
| 3 Keep testing: judge calibration, online evals, dashboard, the market again | 46–55 | 1:35–1:50 |
| Ask Rasoi gains its piece, NB10, A10, architecture, next time | 56–60 | 1:50–2:00 |

## Plate by plate

1. **Title.** "In Lecture 7 you built traces and evals by hand. Today: the tools companies run for the same jobs."
2. **Last time, this time.** Left: our rows, our checks, one judge prompt, one gate function. Right: the same ideas, standard and shared. The piece Ask Rasoi gains: every answer leaves a trace anyone can open; no change ships without a suite that runs by itself.
3. **Monday at Rasoi.** Read the three visitors aloud. Rohit wants the steps; IT wants one format and no lock-in; Anand wants proof after every change and proof someone attacked it. Ask: which one is the hardest?
4. **Three questions, three parts.** Map of the morning. Say which agent: Lecture 7's Ask Rasoi with the trust layer, gemini-3.8-flash, toolbox over MCP. New code in `bahi/bahi/course/obs/`.
5. **The gap (money shot).** Step through the bars: 89% watch, 62% trace each step, 52% test offline, 37% online. Toggle "teams in production": more of everything, the gap remains. **Say the caveat out loud:** LangChain ran it among its own audience and sells tracing. Direction, not census.
6. **Part 1.**
7. **What Lecture 7 had.** Our rows answered one conversation on one laptop. Missing: times, parents, names others read. IT's world has many systems on one time line.
8. **A span.** Definition. Step through the real `find_supplier` span (the first tool call of the order): name, start/end (milliseconds), ids (the parent is its chat call), attributes. "The parent id turns a list into a tree."
9. **A trace.** Waterfall of the gasket order. Pick turn 3, click the release bar, then a chat bar. Model calls are seconds, tools milliseconds: where the time goes is visible at a glance.
10. **One standard (Fig. 1).** OpenTelemetry: SDK + OTLP. "Instrument once; where it goes is a setting." Two run in our build, three are the same wire.
11. **The GenAI conventions.** Walk the table: operation name, provider, models, tokens, tool name, call id. Status Development; `gen_ai.system` → `gen_ai.provider.name` in v1.37. Pin versions.
12. **The real span.** Toggle agent / chat / tool JSON. Point at conversation id, tokens, cost, the receipt. `bahi.` names are ours; `langfuse.` and `openinference.` help two viewers.
13. **Twenty lines.** The wrapper code. Auto-instrumentation libraries do this for OpenAI or LangChain clients: now they know what those write. Read the measured box (spans and traces).
14. **What goes in a span.** Content is opt-in. `content=False`. "A trace store is read by more people than Bahi is."
15. **Check yourself.** Take answers before revealing.
16. **Langfuse (Fig. 2).** Five objects: trace of observations, session, score, prompt, dataset. MIT, self-host or cloud; we used cloud US, SDK 4.17.0.
17. **Sending spans to Langfuse.** Three lines of standard OTLP and a Basic-auth header. Langfuse reads the GenAI names to make generations with model, usage and cost. Its own names where the standard has none: `session.id`, `user.id`, tags, prompt version.
18. **The gasket order in Langfuse (Fig. 3).** Real screenshot of the public trace. Click "Open the real trace" if the room has internet. Point at erp_check and judge_words_only on the trace header: they disagree here (Part 3).
19. **One generation, opened (Fig. 4).** "Rohit's question is answered here: the exact messages the model saw before it chose." Read the measured box.
20. **Sessions.** Three traces, one conversation; Rohit approves between trace 2 and 3, in his own session.
21. **Scores.** erp_check, never_events, judge_words_only on every scenario. Note where code and judge disagree: hold it for Part 3.
22. **Prompt management.** v1 Experience, v2 Lecture 7's fix labelled production. Every generation records its version. "Moving the label is a deploy: it needs the suite."
23. **Datasets and experiments.** Both prompt versions over the six scenarios with `run_experiment`, one run per item. v-experience 2/6, production 3/6. Read the failures: v1 failed 2 and 6 by asking Kavita to confirm again (Lecture 7's bug); v2 failed them with a reply cut mid-sentence (replayed from run 1, next plate). One run per item is not enough.
24. **The trace found the bug (Fig. 5).** Our first gasket run failed: the last chat span stopped after a few output tokens, mid-sentence. No question mark, so the test's Kavita never said yes. Found in a minute. Re-run passed. "Run each case more than once."
25. **Arize Phoenix (Fig. 6).** Local, no account, source-available (ELv2, not OSI open source: say so). Same exporter list.
26. **Two dialects.** GenAI vs OpenInference names on the same span. Honest state of the field: one wire, two vocabularies, converging.
27. **Which one when.** Five rows. Stack Overflow 2025: LangSmith 12.5%, Langfuse 8.8%, Arize 3.7%; Grafana 43% (developers, not companies).
28. **The same spans, elsewhere.** LangSmith, Braintrust, Datadog OTLP routes, each marked **not run in our build**. "We did not run them, so we show no screenshots."
29. **Check yourself.**
30. **Part 2.**
31. **From Lecture 7 to DeepEval.** The mapping table, one row per step: test case, metric, GEval, test file, CI exit code.
32. **A test case.** Scenario 2's LLMTestCase: input, output, tools, context. "The context gives the judge the facts it cannot see."
33. **Eleven tests.** Code where the answer is in Bahi; the judge only for the reply's honesty. The judge is gpt-6.1-terra via OpenRouter, recorded.
34. **The gate in CI (Fig. 7).** The workflow; make `evals` a required check. Replay is free; a changed prompt calls the model with the repo's key or fails loudly.
35. **A broken pull request.** Toggle production / broken. Production: 10 passed, 1 known (scenario 5), merge allowed. Broken: 4 failed (scenarios 2, 3, 6 and the tool order), merge blocked. Replayed with no key: same verdicts (`logs/ci_*_replay.json`).
36. **The gate caught us first.** Our first CI run blocked the *good* prompt with 4 failures. Three causes: GEval's 0–10 scale vs our "score 1"; the tool test counting previews; scenario 5 known. Read the judge's own words: "accurately states" with score 0.1. "Test the tests."
37. **Ragas (Fig. 8).** Four metrics; two by ids, two by a model.
38. **Ragas on Lecture 3.** L3 40/40 vs weak 32/40 by code. ID recall 0.758 → 0.443, LLM context recall 0.80 → 0.49. Precision *rose* (0.54 → 0.73) with top-1: never read it alone. "Any" vs "all" gold clauses.
39. **Faithful is not correct.** Click T04 (correct refusal, faithfulness 0), P12 (right, scored 0: noisy), M01 (wrong but faithful). "Use Ragas to compare retrievers, not to judge one answer."
40. **Red-teaming (Fig. 9).** Definition; OWASP LLM01 direct and indirect. promptfoo: open source; OpenAI *announced* it will acquire it (Mar 2026).
41. **The attacks.** Six rules × six deliveries + two hidden in Bahi data = 38. Click through a few; the base64 and fake tool result ones get a laugh.
42. **Attack success rate.** Toggle targets: flash 0/38, flash + trust 0/37 (one provider error), lite 2/38 (both §6.2: a fake tool result and a note hidden in the supplier name), lite + trust 0/38. "Flash held 38 attacks on these days. The next attack is new."
43. **The indirect injection.** Step through: plain message, planted note, tool returns it, lite orders 5,000 gaskets from Kaveri Rubber with an expired certificate (NE3). Then the trust layer refusing the fake-tool-result attack in code (§6.2). "A prompt cannot defend against text the prompt itself reads."
44. **promptfoo writes attacks too.** 18 generated; the 6 jailbreak ones need promptfoo's cloud (kept off); 12 ran on two targets, 24 runs: grader and Bahi agreed on all, 0 hits. They named suppliers Rasoi does not have: generic generated attacks are easier than ones written with your data.
45. **Check yourself.**
46. **Part 3.**
47. **Judge against code.** Build the matrix: 63 / 48 agree, 24 kinder, 9 stricter. 111 of 144, 77%. "Two coins agree half the time."
48. **Cohen's kappa.** Work it on the board: (0.771 − 0.50) ÷ 0.50 = 0.54, "moderate".
49. **When judges lie.** Click through kinder and stricter examples; read the judge's own words and Bahi's read-back.
50. **Fixing the judge.** Read-back fixed 7 of 9 stricter errors but only 2 of 24 kinder ones: the kinder runs were safe but unfinished, and the rubric never said "finished". A second judge model (gpt-6.1-terra) did worse: kappa 0.35. Cost of the two new judges: about ₹43.
51. **Rules for judges.** Code first (no judge beat kappa 0.6); calibrate with the matrix and kappa; write the rubric fully; re-check on a model change (the two judges agreed only 76%).
52. **Online evals (Fig. 10).** Offline blocks; online alerts. The arrow back: every production failure becomes a case.
53. **An online evaluator.** Reads the trace from Langfuse's v2 API, checks "claims match receipts", samples the judge, writes `online_*` scores back. Read the measured box. The one mismatch is a false alarm worth showing: the policy answer ended "before any purchase order can be placed", and the regex took it for a claim. Regex checks need their own tests too. Mention: Langfuse retired the old trace and session read endpoints for new projects (16 Nov 2026 for all); we use v2 observations and v3 scores.
54. **The dashboard.** "A dashboard is a query." Tiles from our evaluator and the stored latencies; observation counts from the metrics API (the whole project, last 12 hours, so they include our earlier runs).
55. **The gap, again.** Survey numbers plus the Berkeley-led study (86 systems): 74% rely mainly on people reading outputs. Neither is a census; both say tests are rarer than dashboards.
56. **Ask Rasoi gains its piece.** Answer each Monday visitor. Try-these list. Open the live app.
57. **The notebook.** Seven sections, six TODOs. Phoenix runs inside Colab in its own venv (two to three minutes).
58. **Assignment A10.** Instrument, ten tests and a gate, twelve attacks with one indirect, calibrate a judge. A complete A10 covers two layers of the production-stack menu.
59. **Where we are (Fig. 11).** The blue column: spans from every layer, tests before every change, scores on live traces.
60. **Next time.** Lecture 11: guardrails as products, Temporal, data stores, gateways with budgets.

## Demo moments

- Plate 9: click bars in the waterfall; ask the room which span is slowest.
- Plate 18: open the public Langfuse trace (no login).
- Plate 35: toggle the broken PR; then show `ci/ask-rasoi-evals.yml`.
- Plate 42: toggle targets; click the two red cells.
- Plate 47: build the matrix with the room before revealing kappa.

## If something breaks

- No internet: every plate works offline except the two links; the screenshots are local files.
- Someone asks for LangSmith or Braintrust screenshots: "not run in our build, no keys; the code is the documented route".
