# Lecture 7 · Trust: speaker notes

Sat 21 Nov 2026, 7:00–9:00 IST. 57 slides (50 plates, 6 part slides and the next-time slide). Deck: `lectures/L7-trust/index.html`.
Every number on the plates is filled from `figdata.js`, which `gen_figdata.py` builds from `experiments/logs/`.
Live demo: `https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=agent` (keep a tab open as Kavita
and one as Rohit). Notebook: `NB7_trust.ipynb` (replay, no key).

## Timing

| Part | Slides | Minutes |
|---|---|---|
| Opening, cold open, the map | 1–5 | 0:00–0:10 |
| 1 Whose authority? (identity) | 6–12 | 0:10–0:25 |
| 2 Approvals, never-events, guardrails, read-back | 13–22 | 0:25–0:48 |
| 3 Evaluation | 23–33 | 0:48–1:12 |
| 4 Traces | 34–37 | 1:12–1:20 |
| 5 Failure and recovery | 38–47 (incl. 45b) | 1:20–1:40 |
| 6 Deploy, cost, rate limits | 47–51 | 1:40–1:50 |
| Ask Rasoi gains its piece, NB7, A7, architecture, next time | 52–56 | 1:50–2:00 |

## Plate by plate

1. **Title.** "Today Ask Rasoi earns the right to touch the real Bahi."
2. **Last time, this time.** L4 hands, L5 loop, L6 Studio: it can act. Today: it can be trusted. Point at the green column (we come back to it at the end).
3. **Saturday at Rasoi.** Read Anand's letter aloud. Three questions: whose authority, what if twice, right tomorrow. "And all of us at once, at a cost I can sign." Ask the room: which one scares you most?
4. **Three questions, six parts.** The map of the morning. Say clearly which agent we test: the Experience's own harness and prompt, the toolbox over MCP, Gemini. Our code: `bahi/bahi/course/l7/`.
5. **The trust layer (Fig. 1).** Five checks inside every tool call, three practices outside. "No model is ever asked whether something is allowed."
6. **Part 1.**
7. **What identity means.** The form knew who you were: sign-in, grey menus, the limit checked on save, Rohit signing in to approve. Definition. Two answers: passthrough vs SVC_AGENT (limit 10^12).
8. **Two ways in (Fig. 2).** Only one line differs. "Convenient for IT is the danger."
9. **One preview, two answers.** Toggle the session live. ₹2,69,040 estimate, Kavita's limit ₹2,50,000: needs approval, RMEHTA. SVC_AGENT: no approval. Nothing was saved: it is a preview.
10. **What we measured · identity (Fig. 3).** 16 runs: service account 8/8 NE1, Kavita 0/8; v2's 48 runs 24/24 vs 0/24. "The model never mattered." Mention the three lite runs that stopped after Rohit approved: routed correctly, job unfinished, that is a harness problem, not identity.
11. **Least privilege.** Bind at construction; Bahi still checks; service accounts never sign (POL-APR-002 §4.2).
12. **Check yourself.** Take two answers from the room before revealing.
13. **Part 2.**
14. **An approval is a person.** Definition. Gross not basic. Drag the slider: ₹2,50,000 → Kavita, up to ₹10 lakh → Rohit, up to ₹50 lakh → Anand.
15. **The pause.** Walk turn 2 → Rohit in his own session → turn 3. Read the line filled from the trace (PO/2026/01182 RL, approved by RMEHTA).
16. **The five never-events.** One card each, with Rasoi's own names. They live in `scenarios.py`; today we also refuse them before the write.
17. **A guardrail.** Definition; step through the four checks; switch between the three real refusals (approve for Rohit, place it again, just place it).
18. **The checks, in code.** Forty lines. Each refusal: rule + next step, so the model tells Kavita instead of retrying with new words.
19. **A prompt asks, code decides (Fig. 5).** Click the "place it again" row. Flash held all four on its own; lite broke one without the layer: a new need-by date, a new key, a second ₹2,80,840 order. The guard's NE2 check refused it. Be honest: a second *request* was still raised (a guard at the request stage is the builder-track exercise).
20. **Read-back (Fig. 6).** rc "S", "PO/2026/01182 SAVED" vs status DR, W-CC-114, PRD-05. Step to the receipt.
21. **What read-back buys.** v2: 3/10 vs 10/10. The reply gate. Say plainly: in our six-scenario runs the gate never had to fire; it is there for the day the words lie.
22. **Check yourself.**
23. **Part 3.**
24. **Why evaluate.** Everything around the model moves. Definition. Five needs.
25. **A test case (Fig. 7).** Scenario + check on the ERP's state. The check never reads the agent's words (except scenario 4, see next plate).
26. **The check, in code.** Scenario 2's six conditions. Point at scenario 4's word match: "certific". It will bite us in two plates.
27. **The suite, run (Fig. 8).** Four set-ups × six cases × three runs, two models. Walk the rows. Key messages, from the logs:
    - The Experience's own prompt: 2 of 6 per run on flash; scenarios 2 and 6 never finished (next plate).
    - SVC_AGENT: never-events appear (lite).
    - Kavita, with and without the trust layer, on flash: similar pass rates (15/18 and 14/18). On ordinary days the layer neither helps nor hurts; it is for the bad days (plate 19) and the wrong identity.
    - Runs 2 and 3 went through OpenRouter (the direct key ran out of credit). Flash behaved the same; lite returned 12–13 empty replies per run there against none direct. A route change is a change: it would not pass the gate.
28. **Reading one failure (Fig. 9).** Scrub to the last reply: the model asks Kavita to confirm again after Rohit approved. Our one-line fix.
29. **Code checks, LLM judges.** Definitions; strengths and weaknesses.
30. **Judge against code (Fig. 10).** Read the agreement number; click the disagreements. Expected pattern: the judge is kinder where words look right but Bahi disagrees, and stricter or kinder on scenario 4 where the code's word match is brittle ("food-grade test report" with no "certific"). Lesson: code for state, judge for meaning, and fix brittle checks.
31. **The regression gate (Fig. 11).** Today = Experience prompt, change = Kavita + trust: SHIP. Then reverse: BLOCK. Then compare trust vs bare: watch "a case that passed every run" break. Then lite.
32. **Bigger suites.** v2's 60 cases (provenance: v2 agents). Every bug becomes a case: today's "asked again" bug as Scenario 7.
33. **Check yourself.**
34. **Part 4.**
35. **What a trace is.** Definition. JSON rows. Langfuse is a viewer, not a requirement.
36. **Scrub a real trace.** Let a student drive the slider. Point at: preview in turn 1, commit in turn 2, read-back events, tokens growing each step.
37. **Keep, and never keep.** Keys and passwords never in a trace.
38. **Part 5.**
39. **Three ways to fail.** The third (done, reply lost) is the dangerous one.
40. **The lost reply (Fig. 12).** Read the four lines from `lost_reply.json`: Bahi did SAVED, the caller saw a timeout, PRD-07 budget ₹3,10,000 → ₹5,90,840, the key finds PO/2026/01182.
41. **Retries and idempotency.** Reads safe, writes not. Definition. Link back to L6's "Run it twice".
42. **A key from the content (Fig. 13).** Type 20,000 → 20,001 and back; the key returns to K13740B9682A6. Why never uuid4.
43. **The drill (Fig. 14).** Step through the four clients. Redo the job: 25 of 50 trials duplicated, 33 extra orders, ₹92,95,804 extra. Press Save again: no duplicates, 8 wrong reports. Keys (the toolbox on 28 Oct): 0 duplicates but 16 stuck. Keys + fixes: 50/50.
44. **What the drill found.** The two fixes; sent to the toolbox's owner, merged the same day; re-run on the merged toolbox: 50/50 (`logs/retry_drill_after_fix.json`). The drill becomes a test.
45. **Waits that last days (Fig. 15).** Definition of durable execution; the figure.
45b. **Fifty hours, scrubbed (Fig. 16).** Drag the hour slider: reads back every 4 h, reminder at 24 h, escalation at 48 h, Rohit at 50 h, released. v2's Temporal drill, provenance on the plate; 191 history events, 0.4 s wall time.
46. **Check yourself.**
47. **Part 6.**
48. **Deploy (Fig. 15).** The Experience's own `deploy/experience_modal.py`: image, secret, one container and why, the warm-up cron. "Deploy is one command; production is everything around it."
49. **Cost per conversation.** Read the measured line. Drag conversations a day. Input tokens dominate: schemas + history every step.
50. **Rate limits.** Definition. The Experience's settings (not measurements). Drag students to 150: the class limit bites. Back-off and fallback model. The "not yet measured" note is on the plate on purpose.
51. **The operator's switches.** Pause, cap, status. Never redeploy during class.
52. **Ask Rasoi gains its piece.** **Demo (5 min):** in the live app as Kavita, try the four lines on the card; then switch to Rohit and approve. Show the tool cards.
53. **NB7.** What each section does; open it in Colab if time allows.
54. **Assignment A7.** And the twist: at 9 AM the demo-day changes are announced.
55. **Where we are.** The architecture with trust lit.
56. **Next time.** Demo day.

## Numbers and their logs

| Plate | Number | Log |
|---|---|---|
| 9 | ₹2,69,040; needs approval / approver per session | `logs/draft_and_sessions.json` |
| 10 | NE1 8/8 vs 0/8; v2 24/24 vs 0/24 | `logs/identity_{flash,lite}.json`; `logs/v2/identity_*.json` |
| 15 | PO/2026/01182 RL approved by RMEHTA | `logs/six_flash.json` (trust, scenario 2, run 1) |
| 19 | adversarial held/broke per cell | `logs/adversarial_{flash,lite}.json` |
| 20 | rc S, "SAVED", DR, W-CC-114 | `logs/draft_and_sessions.json` |
| 21 | 3/10 vs 10/10 | `logs/v2/readback_default.json` |
| 27, 31 | pass/fail per run, ₹ per suite | `logs/six_{flash,lite}.json` |
| 30 | judge agreement | `logs/judge.json` |
| 32 | 56/60, 40/60, 3/60 | `logs/v2/suite_*_summary.json` |
| 40 | SAVED, timeout, budget, key | `logs/lost_reply.json` |
| 43–44 | the four clients; after the merge | `logs/retry_drill.json`, `logs/retry_drill_after_fix.json` |
| 45 | 24 h, 48 h, 50 h; worker down 30 h | `logs/v2/approval_wait_50h.json`, `crash_while_waiting.json` |
| 49 | tokens, calls, ₹ per conversation | `logs/six_{flash,lite}.json` (trust set-up) |

## Shared-code changes this lecture found (reported, not made)

1. **Merged by the lead (28 Oct).** `create_purchase_request`: finish a request whose save reply was lost (it stayed DR).
2. **Merged by the lead (28 Oct).** `create_purchase_order`: look the order up by its key before checking the
   request's status. Re-run on the merged toolbox: 50/50 (`logs/retry_drill_after_fix.json`).
3. `bahi/agent/tools.py` `_receipt`: the Draft warning says "then amend", but the v3 toolbox has no amend tool.
4. `bahi/experience/harness.py`: after Rohit approves, the "agent" prompt makes the model ask Kavita to confirm the
   order again (scenario 2 and 6 never finish under `run_scenario`). One line fixes it (`ONE_YES` in
   `bahi/bahi/course/l7/agent.py`). And on an empty model reply the harness says "I have stopped here"; asking the
   model once more would recover most of the lite failures we logged.
5. `tools/deck_qa_modal.py` skipped `*.png` (fixed by the lead on 28 Oct). This deck uses JPEG copies
   (`figs/*.jpg`, about a tenth of the size) of the PaperBanana PNGs, which also keeps the page light.
6. `bahi/scenarios.py`, scenario 4: the check wants the word "certific"; a correct refusal asking for a "food-grade
   test report" failed (trust/flash run 1). Accept "food-grade" too.
7. `bahi/llm.py`: the 402 → OpenRouter switch re-routes only the first thread that hits the 402
   (`and not _GEMINI_VIA_OPENROUTER`); other threads failing at the same moment raise. Drop that condition, or take
   a lock. (Our L8 runs make one call before starting threads.)
8. `bahi/docs/_index/embeddings.jsonl` and `rerank.jsonl` are caches every Modal run copies back whole; parallel
   runs by different builders overwrite each other's additions (harmless for correctness, wasteful).
