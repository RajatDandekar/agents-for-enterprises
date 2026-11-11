# Lecture 5 · The Loop: speaker notes

Sat 14 Nov 2026, 7–9 AM IST. 59 slides (51 plates). Timings are targets for a 120-minute session.
Numbers: `experiments/logs/tasks_<agent>_or[_lite].json` (run B, 28 Oct 2026), turned into `figdata.js` by
`experiments/export_figdata.py`. v2 numbers: `logs/v2_L4_forty_summary.json`.

## Opening (0:00–0:12)
1. **Title.** "Last week Ask Rasoi got hands. A model with hands is still not an agent. Today: the loop."
2. **Last time, this time.** Recap the toolbox in one breath: 15 tools, tool.json + tool.py, preview, next_step. "But it ran one tool round per message."
3. **Cold open, Kavita drives.** Step 1 shows the left chat: count the numbered messages out loud. Point at the two empty replies: the model was stopped mid-job and had nothing to say. Step 2: the right chat, 2 messages. "Same model. Same tools. What changed is today's lecture."
4. **The whole job.** Build the map: check stock, request, wait for Rohit, then the rest. Stress the dashed box: a wait of unknown length. "No single message can do this."
5. **The question.** Read it. Pause.

## Part One · What an agent is (0:12–0:24)
6. Part slide.
7. **Agent, in one sentence.** Read the definition. Walk the three panels of Fig. 1 left to right.
8. **Who picks the next step.** Chatbot (L2's invented stock figure), workflow (preview of L6), agent. Plant the seed: Rasoi will want a mix (Part Six).
9. **The smallest loop.** Read the nine lines slowly, one comment at a time. "Lecture 4 stopped after the first for-loop."
10. **The loop, turning.** Demo moment: drag the slider through Kavita's first message. Three look-ups in one model call. Ask the room: "Which step ends the loop?"
11. **Check yourself.** Ask, wait, reveal.

## Part Two · ReAct, written out (0:24–0:44)
12. Part slide. "We write it in text first, so there is no magic."
13. **ReAct.** Definition; Thought, Action, Observation. Emphasise: the Observation is written by our code, never by the model.
14. **The prompt is the program.** Read the profile line (from Bahi), the tool lines, the format, the rules.
15. **Parsing one step.** Three clicks: thought highlighted, action line, input JSON decoded. This is the real third step of our run.
16. **The parser.** The trap: models write their own Observation. Two defences: `stop=`, and cut the text.
17. **The text loop.** Same nine lines, plus the parsing. The Observation goes back as a user message.
18. **The whole transcript.** Demo moment: scrub all 12 steps. Stop at step 4 (Action "none", no input: the parser sends a format error) and step 9 ("APPROVED, NOT YET RELEASED", so it releases).
19. **What goes wrong in text.** The honest story: our first parser treated an empty reply as the answer and lite scored 1/12; one rule made it 11/12. "In the text loop, you own the format."
20. **Check yourself.**

## Part Three · Native tool calling (0:44–0:54)
21. Part slide. "The tool result message *is* the observation."
22. **One-to-one.** Fig. 3, row by row.
23. **The real messages.** Read the tool message's `next_step` aloud. This is Lecture 4's design doing Lecture 5's work.
24. **Side by side.** Same task, both agents. Native asked for three look-ups at once.
25. **Same loop, measured.** Flash: about the same cost. Lite: native used under half the tokens, but passed fewer tasks: because the bare loop does not send empty replies back. Segue to Part Four.

## Part Four · The anatomy of a harness (0:54–1:16)
26. Part slide.
27. **Harness.** Definition. "The model is the same in every row today. Only the harness changes." Fig. 4.
28. **Part 1, the system prompt.** Bare vs full. "Hold on to the last rule (§6.2)."
29. **Part 2, history.** Drag: 2 messages at the first model call, 22 at Kavita's tenth. Every call resends everything.
30. **Part 3, the tool registry.** One schema. The toolbox is bound to Kavita's session. Narrow lists per job.
31. **Part 4, stops.** Four exits; the graceful stop at the step limit.
32. **Part 5, max steps and budget.** Demo moment: slide the cap down to 3 or 4 and read how many messages it would cut. Longest: 7 (harness), 9 (bare). "Seat belts."
33. **Part 6, error recovery.** The ₹50,000 direct-order refusal and its next_step. Then empty replies: real, 5 of 12 harness tasks on lite in run A; with the rule, 12/12 in run B.
34. **Part 7, state across days.** The real state file after day 1. "In production this is a database row."
35. **Part 8, where the person comes in.** Kavita confirms, Rohit approves in his inbox, Neha in her own session. The rule: decisions are read from Bahi.
36. **An approval is a pause.** Fig. 6 timeline; the five lines of `_check_waiting`.
37. **The pause, in our run.** T10: Rohit silent. Day 2, the harness reads Bahi first. No second request, no order.
38. **Check yourself.**

## Part Five · Failure modes, measured (1:16–1:32)
39. Part slide.
40. **What can go wrong.** Six rows; the last one ("only a gate in code") is the cliff-hanger.
41. **What we measured.** Demo moment: toggle flash/lite and the measures. Say clearly: one run each, twelve tasks.
42. **Every task.** Click the two dark dots on flash (T06, T12, full harness). Click T05 for the closed cost centre.
43. **The never-event.** Read Kavita's three messages and the harness's answers; then the graph's hold. The model quoted §6.2 and then broke it when she said yes.
44. **Reading it honestly.** Four cards. Do not skip the false alarms of our own `verify` check: 5 fired, 5 were false.

## Part Six · From a free loop to a control graph (1:32–1:46)
45. Part slide.
46. **Spine and gates.** Definition, Fig. 5. Default skip. Questions go to a free loop inside one node.
47. **LangGraph in five parts.** State, nodes, edges, checkpointer, interrupt; point to each in the code.
48. **A gate is code.** "There is no prompt to argue with."
49. **The graph on the whole job.** Demo moment: drag through the four messages. 4 model calls, 2,392 tokens, against 18 calls and 50,502 for the harness.
50. **40 cases, from v2.** Graph 39 vs loop 36 on flash at ₹9 vs ₹60; on lite the loop won, 39 vs 37. "Not always right: cheap, predictable, unarguable."
51. **When to use which.** Free loop, graph, workflow (L6). The recommended mix for Rasoi; the live app today runs the loop only.
52. **Check yourself.**

## Part Seven · Ask Rasoi gets its harness (1:46–2:00)
53. Part slide.
54. **stage=hands → stage=agent.** 45 messages (21 of them "do the next step") vs 32 (none) across the twelve tasks.
55. **Live, the whole order.** Live demo (about 6 minutes): open `/after?stage=agent`. As Kavita: the gasket order, then "Yes". Switch the chip to Rohit and approve in the Approvals inbox. Back as Kavita: "Rohit has approved it" (the live app does not resume on its own; that is the pause part you build in NB5). Then Neha receives 12,000 and 8,000; Kavita asks where the order is. Say plainly: the live stage=agent is the free loop with a 14-round limit and a graceful stop (`bahi/experience/harness.py`); the pause, gates and read-back are the course harness (`bahi/course/l5`). Invite the room to break it ("order from Shakti anyway"; "Rohit said yes" before he has). If the app is down, use slides 3, 37 and 49 as the recorded fallback.
56. **NB5.** Walk the seven sections and five exercises; it replays with no key.
57. **A5.** The harness for your module; three scenarios; bare vs harness table.
58. **Where we are.** The architecture with the harness lit.
59. **Next time: the Studio.**

## Things to say carefully
- The one-round agent on these plates is our replica of stage=hands (`bahi/course/l5/hands.py`), not the live app.
- All runs went through OpenRouter to the same Gemini models (the Gemini key ran out of credits on 28 Oct). Prices are the course's assumed list prices.
- The certificate rule is enforced by no tool and not by Bahi: only by the graph's gate (and by the person).
