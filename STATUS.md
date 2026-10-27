# From Forms to Agents: status

AI Agents for Enterprises (Vizuara), 8 lectures, 31 Oct to 22 Nov 2026.
- **Plan:** v2 deck `course-plan-deck.html` (artifact https://claude.ai/artifact/QimoD5eV2A5iTbrWgTgeCQ).
- **Standard:** `BUILD.md`. Read it first.

## Layout
- `bahi/`: pip package `bahi-erp`. The Bahi ERP 7.2 sandbox and the reference agent.
  - `bahi/erp/`
    - `engine.py`: ERP, Session, `call()`, faults, `live_run`, module install.
    - `seed.py`: Rasoi Steel Works.
    - `procs.py`: stored procedures.
    - `services.py`: 38 terse services.
    - `screens/*.yaml`
  - `bahi/llm.py`: one OpenAI-compatible client for Gemini, OpenRouter, OpenAI and Anthropic, with cassette replay (`BAHI_LLM_MODE` = auto | replay | record | live).
  - `bahi/scenarios.py`: the six scenarios, never-events NE1–NE5 and code checks.
  - `bahi/agent/`
    - L1: `naive.py`
    - L2: `retrieval.py`
    - L3: `tools.py`, `loop.py`, `../mcp_server.py`
    - L4: `graph.py`, `decide.py`, `memory.py`, `route_spec.py`
    - L5: `authority.py`
  - `bahi/evals/`: L6.
  - `bahi/durable/`: L7.
  - `bahi/modules/`: the capstone kits.
  - `bahi/server.py`: HTTP API and the legacy client.
  - `bahi/legacy_ui/`
  - `bahi/docs/` and `bahi/wiki/`: the policy corpus.
  - `bahi/cassettes/`: recorded model replies.
- `engine/plates.{css,js}`: the shared plate deck engine. `?print=1` stacks every slide.
- `lectures/<L>/`
  - `index.html` + `figs.js`: the deck.
  - `NB*.py` → `.ipynb`: the notebook.
  - `A*.md`: the assignment.
  - `experiments/` with `logs/`.
- `modules/`: capstone kit briefs and the template.
- `tools/`
  - `modal_run.py`: all execution, on Modal (profile rajatworkspace).
  - `nbbuild.py`: percent-format `.py` → `.ipynb`.
  - `nb_setup.txt`
  - `probe_models.py`
- Static preview: the launch config `forms-to-agents` (port 8091) serves this folder.

## Facts established (2026-10-27)
- **Models on the Gemini key:** gemini-3.5-flash-lite, 3.8-flash, 3.1-pro-preview, 3-flash-preview and 4-argon are live; 2.5-* returns 404.
  - Gemini 3 needs its tool-call thought signature echoed back. `llm.py` keeps `extra_content`.
  - Prices in `llm.py` are assumed list prices. ₹ is computed at a fixed 88/USD.
- **Legacy flow verified:**
  - PR est ₹2,69,040 → Rohit approves PR/2026/04417.
  - PO fetch defaults to GST18-INTRA → ERR-PO-0412. With GST18-INTER it saves PO/2026/01182 as DR (PRD-05 closed, warn W-CC-114, msg only "SAVED").
  - Amend to PRD-07 → AP, inheriting Rohit's PR approval. Release → RL, and on_order goes up by 20,000.
- **Naive agent** (38 raw tools, SVC_AGENT, gemini-3.8-flash, cap 15 steps): 0/6, 70–87k tokens and ₹3.2–4.0 per scenario. The cap is now 30, so the L1 builder re-runs it.
- **Intent tools verified:** preview; PR → WAITING FOR APPROVAL → same key → order; idempotent after an injected timeout; Draft receipt → amend → release.

## Built (2026-10-27)
Each lecture folder holds a deck (index.html + figs.js, generated from experiment logs), an NB .py/.ipynb, an A*.md, and experiments/ with logs/. Every deck passed tools/deck_qa_modal.py.

| Lecture | Slides | Headline measured result |
|---|---|---|
| L0 primer | 21 | NB0: Python, HTTP, JSON, ERP basics, one tool call |
| L1 The Form | 41 | **By hand:** 8 screens, 17 fields, 2 sign-ins, ≈3.2 min keystroke estimate; "SAVED" while in DR. **Naive agent, 5 models:** Gemini lite 1/6, flash 2/6 (₹49), pro 0/6; GPT-6.1 Terra 2/6 (₹22); Claude Sonnet 5.5 2/6 (₹106). 7/30 pass, 24 never-events. **n8n:** "success" on refused saves; 3 variants give 8 combinations |
| L2 The Manual | 32 | **Retrieval, 40 Qs:** RAG 40/40 at 579 tokens/answer; Wiki 38/40; full corpus 40/40 at 13.6k tokens. Hybrid+rerank recall@1 0.85, @5 1.0. **Scenario 1** passes with search_policy |
| L3 The Hands | 38 | **30 tasks:** intent tools 30/30 at ₹0.58/task vs raw services 27/30 at ₹3.48. **Tool definitions:** 897 vs 2,669 tokens. **Duplicate supplier** with raw tools on a "register" task. The loop committed a test order on a policy question |
| L4 The Route | 38 | **40 cases:** graph 39/40, ₹9 vs loop 36/40, ₹60; 0 never-events each. decide() confidence was 1.0 everywhere, so the deck adds an explicit 'unsure' option |
| L5 The Signature | 37 | **Service account:** NE1 24/24 vs passthrough 0/24. **Read-back:** catches Draft 30/30 vs bare 13/30. **Guard v2:** 0/24 adversarial. **App journey** test 12/12; 5 real app screenshots |
| L6 The Inspector | 39 | **60-case suite:** graph 56/60 (84–97%), loop 40/60, naive 3/60. flash-words + lite-routing 57/60 at ₹5.58. **Broken bots:** all 9 caught. **Regression gate** CLI built. Spend ₹745 |
| L7 The Night Shift | 32 | **50 faults:** naive redo 25/50 duplicated (₹92.96 lakh extra) vs keyed workflow 50/50 correct. **Approval:** reminder at 24 h, escalation at 48 h. Crash drills pass. Deploy image passes 11/11 (not deployed) |
| L8 Your Module | in progress | Demo-day kit, 8 demo changes, final demo + WALKTHROUGH.md |
| Module kits | n/a | 8 kits + TEMPLATE; modules/test_kits.py PASS |

## Known issues (left for v1.1; fixing them changes recorded prompts, so every dependent cassette must be re-recorded)
- **graph.py (from L6):**
  - V11: a GSTIN answer is not extracted; it asks 8 times.
  - N02: the done-guard rewrites a policy answer.
  - M02: a quantity-less reorder silently takes the last quantity.
  - V10: "Deccan" alone is treated as a new supplier.
  - Unhandled: a §3.4 onboarding hold needs a wait state (L5 uses `update_state`).
- **scenarios.py:**
  - NE1 ignores requests (PRs) approved above the limit.
  - NE5 ignores done-claims while only a request is waiting.
  - NE5's done-regex flags "I've created … but I haven't released it" and "left it unreleased" (two Claude false positives in L1, noted on the plate).
  - The follow-up trigger only looks at the reply's last 200 characters.
  - Each lecture reports with the checks as they ran.
- **tools.py:** a food-contact item with no certificate only warns at commit. The graph and the L5 guard enforce it.
- **durable/runtime.approve:** signals even when Bahi refused the approval. Harmless; the workflow reads Bahi.
- **Two plan predictions did not hold** and the decks say so: the scenario-3 duplicate and the scenario-6 double order. The plan deck's scoreboard chips are targets, not results.

## Build process
- Wave 1 (parallel builders): L0+L1, L2, L3, L4, L7, kits.
- Wave 2: L5, L6, L8.
- **Lead:** replays every notebook with no key (tools/modal_run.py --mode replay) and runs headless deck QA; the hub index.html is at the root.

## Open
- **Course repo for Colab installs:** `nb_setup.txt` points at `github.com/VizuaraAI/agents-for-enterprises` (not created yet). Needs Rajat's OK to publish; it is fictional data only.
- **Not run:** GPT and Claude comparisons need an OpenRouter key; Langfuse needs keys (traces are stored locally until then).
- **Explainer films:** not started.
