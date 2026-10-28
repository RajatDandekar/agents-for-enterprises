# Lecture 8 · Agent Frameworks in Industry: speaker notes

Sun 22 Nov 2026, 7–9 AM IST. 61 slides (52 plates). Timings are targets for 120 minutes.
Numbers: `experiments/logs/` (run 1 and run 2 of 28 Oct 2026), turned into `figdata.js` by `gen_figdata.py`. Plates
fill their numbers from `figdata.js` (`data-v`), so a re-run updates words and figures together.

## What was run, honestly
- **Model:** `google/gemini-3.8-flash` through OpenRouter, temperature 0, at most 12 model calls per message, the
  Lecture 5 `SYSTEM_FULL` prompt, for every setup. ₹ is what OpenRouter billed (`usage.cost`), at ₹88 per US dollar.
- **Tools:** the Lecture 4 toolbox as an MCP server on streamable HTTP, one per person per task
  (`bahi/course/frameworks/mcp_http.py`). Every framework connected to it as a remote MCP server.
- **The meter** (`bahi/course/frameworks/meter.py`): a small OpenAI-compatible gateway on localhost. Every framework's
  model traffic went through it to OpenRouter; it recorded the replies (cassettes `IND8_*`) and counted tokens.
  In production code you would point the SDKs straight at `https://openrouter.ai/api/v1` (or a LiteLLM proxy).
- **Runs:** 7 setups × 12 tasks, run 1; run 2 on all 7 with fresh cassettes (`_rep2`). Seven run-2 tasks of our
  harness and the loop-only harness hit OpenRouter's rate limit (429, "300 requests per minute across all providers")
  and were re-run on the same cassette (`_rep2b`). Twelve tasks once is a small sample; the deck says so.
- **Ollama:** our harness on `qwen3.5:9b` and `gpt-oss:20b` with Ollama 0.40.3 on one Modal L4, no API key in the
  container. The first attempt had `search_policy` failing (fastembed missing from the image); those logs are in
  `experiments/logs/superseded/` and are not used. The re-run reused that run's recorded replies wherever the request
  was identical (same model, same request), and called the model for the rest.
- **Not run:** LangGraph Platform, LangSmith, OpenAI's trace dashboard (no keys); Claude Agent SDK (no Anthropic key);
  CrewAI, Microsoft Agent Framework, LlamaIndex (named only). LiteLLM budgets and rate limits (shown, run in L11).

## Opening (0:00–0:10)
1. **Title.** "You built the loop by hand. Today: the frameworks companies use, on the same agent."
2. **Last time, this time.** One breath of L1–L7. The question at the bottom.
3. **Cold open, Rasoi's IT.** Read the note in IT's voice; then Anand's line. "This lecture is how you answer him."
4. **Four ports.** Ask the room which column is ours. Reveal: column A. "The replies cannot tell you. Only measuring can."
5. **The question.** Read it. Pause.

## Part One · What a framework is (0:10–0:22)
6. Part slide.
7. **Definition.** "A framework calls you." The two numbers: 206 lines for the whole harness, 50 for the loop.
8. **Gives / leaves.** Read both lists. Stress the right one: "Rasoi's never-events live in the right-hand column."
9. **The map.** Fig. 1, row by row. Handoff is the one new idea.
10. **One idea, four names.** Demo moment: click each framework; read one row across ("the loop: `_loop`, `Runner.run`, `run_async`, a two-node graph").
11. **Check yourself.**

## Part Two · The OpenAI Agents SDK (0:22–0:50)
12. Part slide.
13. **What and why.** Open source, small. Tell the version story: our first image build failed because openai-agents ≥0.21 wants openai 3 and LiteLLM wants < 3. "Pinning is not bureaucracy."
14. **Agent.** The highlighted lines. "An Agent is a description."
15. **Runner.** Left and right code. "Same nine lines; you lose the ability to put your own line in the middle, except through hooks."
16. **Tools from MCP.** The real `mcp_tools` span: 15 tools discovered.
17. **The model.** Two routes; the token table of message 1 (1,682 → 1,832 → 1,980: the history grows).
18. **The worked port.** Demo moment: drag the span slider from 1 to 17. Stop at 2 (three look-ups in one call), 7 (preview), 11–15 (save request, order from it, release).
19. **Sessions.** The day-2 object; the 29 items.
20. **Tracing.** Why we replaced the exporter. Counts of span types. Point forward to L10 (Langfuse).
21. **Handoffs.** Fig. 2.
22. **Handoffs in our run.** Read message 2's chain: Policy desk → Front desk → Purchasing desk (it started at the desk that answered last). Then tell the first run's crash honestly.
23. **Guardrails.** Three kinds; the input guardrail stopping "approve it yourself" before any model call.
24. **Harness parts as guardrails.** Two measured lessons: run 2's T12 block (the model tried; the guardrail held) and the verify guardrail's false alarms, caused by our own porting slip.
25. **Check yourself.**

## Part Three · Google ADK (0:50–1:05)
26. Part slide.
27. **What and why.** The names table.
28. **The port.** Why `instruction` is a lambda (curly-brace templating). Lines of code.
29. **Events.** Demo moment: scrub the events. The second model call asks for check_budget, a request preview and an order preview at once.
30. **On the wire.** Read ADK's two added lines aloud, including the untrusted-tool-description notice (a defence against prompt injection from tool servers; L11 returns to it). The byte bars.
31. **ADK measured.** 1.7× input tokens, higher bill; the 12 seconds and what we do and do not know about them.
32. **Sub-agents.** Same routing; no input guardrail ported.
33. **Check yourself.**

## Part Four · LangGraph (1:05–1:15)
34. Part slide.
35. **Two graphs.** The control graph from L5; the prebuilt agent's code.
36. **Node by node.** Scrub the updates.
37. **Free loop or control graph.** 32 model calls vs 101, ₹4.48 vs ₹24.12, 328 lines vs 25. "You pay in code to save in tokens and never-events."
38. **The platform.** Not run; how it maps to what they built.

## Part Five · Measured side by side (1:15–1:35)
39. Part slide.
40. **The rig.** Fig. 3. List what was held fixed. Name the meter.
41. **Scoreboard.** Demo moment: click each measure. Say clearly: twelve tasks, two runs; one-task differences are noise.
42. **Every task.** Click T06 on our harness (the run-1 never-event), T05 on ADK (the closed cost centre), then switch to run 2.
43. **The rule no framework enforces.** The headline of the lecture. Every free loop broke §6.2 at least once in two runs; the control graph and the guardrail port did not.
44. **One order, four frameworks.** Fig. 4: the gasket order through each set of names.
45. **Traces side by side.** Demo moment: drag the slider; three previewed a request then placed a direct order; the Agents SDK saved the request and ordered from it.
46. **Framework time.** Replay timing: sub-second for three, ~12 s for ADK; the model's minute per task dwarfs it.
47. **Check yourself.**

## Part Six · Gateways and local models (1:35–1:47)
48. Part slide.
49. **Gateway.** Fig. 5. OpenRouter vs LiteLLM; the meter is a gateway.
50. **Four models.** All right; costs differ by an order of magnitude. "One question proves the plumbing, not the model."
51. **Fallback.** The Router code; the forced failure answered by the backup.
52. **Why in-house.** Fig. 6.
53. **Ollama.** The table: qwen3.5:9b 12 of 12 and gpt-oss:20b 10 of 12, no never-events, ₹0 to any API, but 30–48 s per model call on one L4 with six tasks in parallel (gemini-3.8-flash: about 6 s). One run each: do not read 12/12 as better than the cloud model.

## Part Seven · Which one when (1:47–1:55)
54. Part slide.
55. **Which one when.** Three run, four named. The closing line about pieces outliving tools.
56. **Market evidence.** Read the caveats as loudly as the numbers.
57. **The answer for Anand.** Keep the control graph for P2P; a framework for open questions; never assume a framework enforces a rule.

## Close (1:55–2:00)
58. **The notebook.** Every SDK runs for real in replay. Five exercises.
59. **A8.** Port your module to two frameworks; the CTO memo.
60. **Where we are.** Fig. 7, the loop and the gateway lit.
61. **Next time.** Lecture 9, Protocols and Integration.

## Known gaps
- **Replay of the full sweep:** in the parallel live runs, tasks that start with the same message (T01, T08, T09, T10)
  share their first recorded reply (the cassette keeps the first one written). Replaying those tasks alone can
  diverge, so `fw_*_replay.json` crashed on 1–3 of them per setup; the overhead plate uses only the five tasks that
  replayed in every setup. The notebook replays T04 (unique), which is deterministic. Fix for the next run: one
  cassette per task.
- **ADK's 12 seconds:** measured, not explained. We did not profile inside ADK.
- **verify guardrail:** our port's false alarms are a bug in our port (missing "a request or order exists" condition), kept as the measured lesson; fixing it changes the recorded prompts.
- **One model only** for the framework comparison (gemini-3.8-flash). The four-model gateway test is one question.
