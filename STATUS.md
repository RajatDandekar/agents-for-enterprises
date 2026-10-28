# From Forms to Agents: status

## v3 (2026-10-28): story-first rebuild of every lecture. Read COURSE_V3.md first.
v2 is archived in `archive/v2/`; the sections below "v2 record" describe that version.

| Piece | State | Checked |
|---|---|---|
| Toolbox (15 tools, tool.json + tool.py), MCP server, goods receipt | done | `bahi/tests_toolbox.py`: full chain, traps, MCP, lost-reply retries |
| Rasoi Experience (live app) | live at https://rajatworkspace--rasoi-experience.us-east.modal.run | 66/66 in-process checks after the 28 Oct redeploy; e2e 23/23; food-grade guard (§6.2) before commit and release |
| Workflow Studio (/studio) | done | engine 82/82 (replay), UI 27/27 |
| L1 The Before and the After | 62 slides | QA 0 issues; NB1 replay 0 errors |
| L2 The Brain | 66 slides | QA 0; NB2 replay 0 errors; 3 PaperBanana figures to redo once the Gemini key has credit (`figs/figs_v2.json`) |
| L3 The Memory | 66 slides | QA 0; NB3 replay 0 errors |
| L4 The Hands | 55 slides | QA 0; NB4 replay 0 errors |
| L5 The Loop | 59 slides | QA 0; NB5 replay 0 errors |
| L6 The Studio | 58 slides | QA 0; NB6 replay 0 errors |
| L7 Trust | 57 slides | QA 0; NB7 replay 0 errors |
| L8 Your Module | 45 slides; kits on the v3 toolbox | QA 0; NB8 replay 0 errors; modules/test_kits.py PASS |

- **Slides:** https://forms-to-agents.vercel.app (`tools/build_site.sh --deploy`).
- **Hub artifact:** https://claude.ai/artifact/BxkGjPwuBwLEhoaVyuroii.
- **Gemini key:** out of credits (HTTP 402) since 28 Oct. `llm.py` sends `gemini:*` through OpenRouter after the first 402, and the reply names the route. PaperBanana (`tools/pb_modal.py`) needs the Gemini key itself.
- **Colab:** pushed 2026-10-28; all 8 v3 notebooks ran from GitHub in clean containers with no keys (0 errors; NB2 about 10 min because of the tiny-GPT training, the rest under 1 min). Not yet run inside a real Colab runtime.
- **Uploads:** `tools/mrun.sh` wraps `modal run` and retries "modified during build".

## v2 record (27 Oct)

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
| L8 Your Module | 34 | **Final stack:** 57/60 (86–98%), 0 never-events, ₹0.43 per resolved order, p95 32 s (over the 20 s bar). **Demo-day changes:** 8 tested as fair. **demo/WALKTHROUGH.md** written |
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

## Live (2026-10-27)
- **Course hub (private artifact):** https://claude.ai/artifact/BxkGjPwuBwLEhoaVyuroii (source `hub.html`; republish the same path to update).
- **Slides site (public):** https://forms-to-agents.vercel.app (Vercel project forms-to-agents, scope rajatdandekars-projects). Redeploy after any deck edit with `tools/build_site.sh --deploy` (decks, engine and images only).
- **Staging app:** https://rajatworkspace--bahi-agent-staging.us-east.modal.run
  - Modal app `bahi-agent-staging`. The admin token is in Modal secret `bahi-staging`.
  - Operate it with `BAHI_ENV=staging modal run deploy/admin.py --cmd status|kill|revive|model-off|model-on|smoke`.
  - Daily cap ₹250. Rate limits are 20/min overall and 6/min per user.
- **Langfuse:** 60 L6 suite traces under tag `L6-suite`, exported over OTel. The old ingestion API retires on 16 Nov 2026.
- **Keys:** `.env` (gitignored) holds OpenRouter and Langfuse. The Gemini key comes from `wm-lecture6-ijepa/.env`.
- **Repo:** PUBLIC at https://github.com/RajatDandekar/agents-for-enterprises (pushed by Rajat 2026-10-28; VizuaraAI is a personal account, so it could not host it). Colab-style check 2026-10-28: clean Modal containers, no keys, each notebook fetched from GitHub and its own cell pip-installing bahi-erp from git → all 8 notebooks ran with 0 errors.
- **Theme:** Sky (Google Sans Flex, full-bleed). All 9 decks pass deck QA after the re-theme.

## Open
- **Course repo for Colab installs:** done and verified (see Live). Not yet run inside a real Colab runtime (needs a Google sign-in).
- **Explainer films:** not started.
