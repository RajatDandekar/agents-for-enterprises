# From Forms to Agents, v3: the story, the syllabus, the standard

Rajat's review on 2026-10-28 rejected v2 because it was hard to follow and the story was wrong. This file replaces BUILD.md §1 (the "nine jobs" spine and the lecture list) and §5 (who owns what). BUILD.md §0 (hard rules), the story canon's people and numbers, §2 (deck engine), §3 (notebooks) and §4 (assignments) still apply. Read both files before you build anything.

## What Rajat asked for, in his words (summarised)
- **Story over everything.** Every lecture builds one piece of the same chatbot, so by L8 the students have assembled the After themselves and understand every piece. If a tool (Langfuse, Temporal, n8n) does not serve the story, drop it.
- **Teach concepts from first principles, Vizuara-style.** One idea per plate, plain words, a worked example with Rasoi's real numbers, a figure that builds up step by step, then connect it to something practical. v2 "did not teach concepts at all" and was "all over the place".
- **Bahi's services are black boxes.** "We pass an input and get an output." Build them properly; never explain their insides on a plate.
- **No primer.** L1 explains what an ERP is, with a playable legacy ERP.
- **The L1 After is a working chatbot,** shown as a demo link everyone can use, doing the same tasks the students just did by hand. Nothing about models, cost or latency comparisons in L1, and no tools or services until the "how it works" part.
- **Students are characters.** They open a link and enter their name, and Rasoi's story is told to them: clients complaining, competitors winning. Rasoi asks them for the transformation. Before the After is revealed, they write what they would want, so they think first and appreciate the After more.
- **The After includes Rasoi's new AI-native landing page,** and a playground where people stitch tools into workflows (n8n-like: create PR → create PO → create GR) and build agents of their own.
- **LLM fundamentals means the real thing:** tokens, embeddings, attention, the transformer, next-token prediction, sampling, training.
- **Build up what an agent is:** the harness, the ReAct loop, and how native tool calling does ReAct implicitly (the tool result is the observation).
- **Interactive, deep, comprehensive, with good architectural figures.**

## The frame the whole course uses

> You are the engineer. Rasoi Steel Works runs on Bahi ERP from 1998. Its customers are unhappy, Kaveri Kitchenware ships faster, and Rasoi has asked you to make it AI-native. Over eight sessions you build **Ask Rasoi**, the assistant on Rasoi's new home page, one piece at a time.

**The architecture of Ask Rasoi** is the one figure every lecture returns to. It is a PaperBanana figure; the lead makes the master, `figures/ask_rasoi_architecture.png`. Each lecture's last plate shows it with that lecture's piece lit up.

```
 Kavita / Rohit / Neha ──> Ask Rasoi chat  ·  Workflow Studio  ·  Approvals inbox       (the After, L1)
                               │
                        ┌──────▼──────────────────────────────┐
                        │ HARNESS (the loop, L5)              │  system prompt · history · tool registry ·
                        │   ┌───────────┐  ┌───────────────┐  │  stop rules · budget · control graph
                        │   │ LLM       │  │ Knowledge     │  │
                        │   │ brain, L2 │  │ RAG+wiki, L3  │  │
                        │   └───────────┘  └───────────────┘  │
                        └──────┬──────────────────────────────┘
                               │ MCP (L4)
                        ┌──────▼──────────────┐   Workflows & your own agents (L6)
                        │ TOOLBOX (L4)        │   Trust: identity, approvals, evals,
                        │ one tool / activity │   traces, recovery, deploy (L7)
                        │ tool.json + tool.py │
                        └──────┬──────────────┘
                               │ services (black boxes)
                          Bahi ERP 7.2 (1998)
```

**The running example** is procure-to-pay (P2P) for Kavita's 20,000 gaskets:
1. **Check stock:** GSK-SIL-05L has 54,000 on hand in Pune stores, using 6,000 a day, which is 9 days of cover. The `check_stock` tool adds Chakan's 12,000 and reports 11 days across both plants; say which one you mean.
2. **Purchase request (PR):** est ₹2,69,040 at the old rate plus Bahi's 18% → above Kavita's ₹2,50,000 limit → waits for Rohit.
3. **Approval:** Rohit approves PR/2026/04417.
4. **Purchase order (PO):** Deccan Polymers, contract ₹11.90 → ₹2,38,000 + 18% = **₹2,80,840**, so PO/2026/01182 is APPROVED.
5. **Release** to the supplier.
6. **Goods receipt (GRN):** Neha counts what arrived, GRN/2026/30001 (12,000) and 30002 (8,000), and stock goes up.

The traps stay exactly as they are in BUILD.md §1:
- the closed PRD-05, which gives a silent Draft;
- the GST18-INTRA default, which gives ERR-PO-0412;
- the direct-PO cap of ₹50,000;
- Deccan's duplicate code;
- Shakti Seals, who are not in the supplier master.

The other cast:
- **Kaveri Kitchenware**, the fictional competitor, "orders confirmed on WhatsApp in two minutes".
- **Rasoi's customers**, fictional dealers: Sharma Home Appliances in Nagpur and Lakshmi Stores in Coimbatore.
- **Anand Patil**, plant head, who signs the letter that asks the student for help.

## The syllabus (dates fixed; Sat and Sun 7–9 AM IST)
| # | Date | Title | First principles taught | The piece Ask Rasoi gains | Practical ending |
|---|---|---|---|---|---|
| 1 | Sat 31 Oct | **The Before and the After** | What an ERP is (master data, transactions, modules, P2P); why forms hurt; the brief; the reveal; how it works at the top level (toolbox, JSON schema, Python, MCP, orchestrator LLM); what an enterprise AI agent is | The whole thing, seen from outside | Students play the legacy ERP missions, write their wishlist, then do the same missions with Ask Rasoi |
| 2 | Sun 1 Nov | **The Brain: How an LLM Works** | Next-token prediction; tokens and the tokenizer; embeddings; attention, step by step on a Rasoi sentence; the transformer block (attention, MLP, residual, norm) and stacking; training (loss, gradient descent, pretraining → instruction tuning → RLHF in one line); sampling and temperature; the chat format and context window; why it makes things up | The brain: Ask Rasoi with no tools | The bare chatbot invents Rasoi's stock figure; the notebook builds a tiny GPT from scratch and calls a real model |
| 3 | Sat 7 Nov | **The Memory: Giving It Knowledge** | Why the model does not know Rasoi; context is the only memory; prompting; embeddings for search; cosine similarity; chunking; BM25 vs vectors, hybrid, reranking; RAG end to end; citations; the LLM wiki; who may read what; freshness | `search_policy`: answers policy with citations | "Can we buy gaskets from Shakti Seals?" is answered with §6.2 cited |
| 4 | Sun 8 Nov | **The Hands: Tools and MCP** | Function calling from first principles (the model writes a JSON request; your code runs it; the result goes back); JSON Schema; designing tools: one per business activity, intent rather than screens, preview/confirm, idempotency keys, receipts, errors that say what to do next; the toolbox folder (`tool.json` + `tool.py`); MCP (the N×M problem, host/client/server, `tools/list`, `tools/call`, JSON-RPC on the wire, transports) | The toolbox over MCP | Ask Rasoi checks stock and raises the PR; the same server plugs into Claude Desktop |
| 5 | Sat 14 Nov | **The Loop: What Makes It an Agent** | Agent = model + tools + loop + state; ReAct (reason → act → observe), first written out in text, then shown to be what native tool calling does implicitly (the tool result message *is* the observation); anatomy of a harness (system prompt, history, registry, loop control, max steps, stop conditions, error recovery, memory, budget); failure modes (loops, early "done", skipped steps); from a free loop to a control graph (spine and gates, LangGraph) when the process must be followed; a human approval as a pause in the loop | The harness: multi-step, multi-turn | Ask Rasoi runs PR → wait for Rohit → PO → release → GRN |
| 6 | Sun 15 Nov | **The Studio: Workflows and Your Own Agents** | Workflow vs agent (fixed path vs the model choosing); triggers (schedule, event, form, chat); nodes, data mapping, branches, an approval node, error paths; agents as nodes; when to use which | Workflow Studio | Students build "stock below reorder → PR → approval → PO → release → message Rohit", then build their own agent from tools and instructions |
| 7 | Sat 21 Nov | **Trust: Taking It to Production** | Whom the agent acts as (identity, the user's own permissions, never a super-user service account); approvals and never-events; guardrails; evaluation (scenarios, code checks vs LLM judges, the regression gate); traces; failure and recovery (timeouts, retries, idempotency, durable waits); deploy, cost and rate limits | Trust layer | Run the eval suite on your Ask Rasoi, read a trace, deploy it |
| 8 | Sun 22 Nov | **Your Module: Demo Day** | Recap of the whole build as one figure; how to apply it to another module | Your module's After | Each student demos a module kit (`modules/`) with its own Before and After |

## The Rasoi Experience (the live app, owned by the experience builder)
One web app on Modal, `rasoi-experience`. Everyone in the cohort uses it from a link.
- `/`: **the invitation.** Enter your name. A personalised brief follows: a letter from Anand Patil to you; dealers' complaints; Kaveri winning orders; Rasoi's numbers.
- `/brief`: **your wishlist.** Before anything is revealed: "What would you build for Rasoi?" Prompts, saved, and shown on a shared class wall.
- `/before`: **the legacy Bahi ERP 7.2** in Windows-2000 style, with an "ERP in 5 minutes" guide and the missions (check stock, raise the PR, approve as Rohit, make and release the PO, receive the goods), counted by a timer, clicks, keystrokes and errors hit. Each player has their own Rasoi.
- `/after`: **Rasoi's new AI-native home page.** Ask Rasoi chat, the approvals inbox, a "how it works" panel (tool calls appear as cards once switched on), and a Before-vs-After scorecard from the player's own runs.
- `/after?stage=brain|knowledge|hands|agent`: **Ask Rasoi as it is at each lecture.**
  - `brain`: no tools.
  - `knowledge`: `search_policy` only.
  - `hands`: the toolbox, but one tool round per message.
  - `agent`: the full loop.
- `/tools`: **the toolbox explorer.** Every tool's `tool.json` and `tool.py`, and a "try it" form.
- `/studio`: **the Workflow Studio**, n8n-like: a canvas, the tool nodes, triggers, an approval node, an agent node, run it and watch each node's output. Built by the studio builder, mounted by the experience app.

## Code the lead built (shared; do not change names or arguments)
- `bahi/bahi/toolbox/`: **15 tools,** one folder each with `tool.json` (name, title, category, description, input_schema, output_schema, writes, services, example) and `tool.py` (`run(s, **args)`).
  - `Toolbox(erp, user)` gives you `.schemas()`, `.call(name, args)`, `.manifest()` (with the Python source) and `.names`.
  - The tools are: find_item, check_stock, find_supplier, check_budget, search_policy, create_purchase_request, list_my_approvals, approve_purchase_request, create_purchase_order, approve_purchase_order, release_purchase_order, order_status, receive_goods, register_supplier, send_message.
  - Tested end to end on Modal by `bahi/tests_toolbox.py`, over MCP as well.
- `bahi/bahi/toolbox/mcp.py`: **`build_toolbox_server(erp, user)`**, a FastMCP server built from the folders. Use it with `MCPClient`/`MCPClientTools` from `bahi.mcp_server`.
- `bahi/bahi/erp/receipts.py`: **goods receipt** (`grn_save`, `grn_get`, `grn_search`, installed by `Toolbox()` or `install_receipts(erp)`). It has a legacy screen code `INV-GRN-03` but no YAML yet; the experience builder writes it.
- **Kept from v2 and reusable:**
  - `bahi/bahi/agent/{loop,retrieval,graph,authority,memory}.py`, `bahi/bahi/evals/`, `bahi/bahi/durable/`, `bahi/bahi/app/`, `bahi/bahi/legacy_ui/` and `deploy/`.
  - v2's decks, notebooks and experiments are in `archive/v2/lectures/`. Reuse anything correct, but rebuild to this story.

## How every lecture is built (the standard)
- **Shape, about 2 hours, 40–60 plates:**
  1. Cold open: a story beat at Rasoi, with the student as the engineer.
  2. The question this lecture answers.
  3. The concept from first principles, in small steps, each on Rasoi's real data.
  4. Check-yourself questions.
  5. The practical connection: Ask Rasoi gains its piece, shown live from the Experience at this lecture's stage.
  6. The notebook walkthrough.
  7. The assignment.
  8. The architecture figure with this piece lit.
  9. "Next time".
- **Teaching:** nothing is used before it is taught. One idea per plate. Every concept gets:
  - a definition in one sentence;
  - a worked example with real Rasoi values;
  - a figure that builds up;
  - and, where touching teaches, an interactive control.
  Re-explain each term the first time it appears in a lecture.
- **Figures:**
  - Architectural and concept diagrams are PaperBanana figures, never hand-drawn SVG boxes: `python3 /Users/raj/Claude_Brain/ai-fde-site/tools/pb_generate_local.py`. Read its header; it needs the planner model gemini-3.8-flash. Generate them on Modal if it needs installs.
  - Live, stepwise and interactive figures (attention heatmaps, token splits, the loop animation, the scrubbed traces) are SVG/JS in `figs.js`.
  - No cartoons, emoji or figurine people.
- **Numbers:** every number on a plate comes from our own run and is logged in `lectures/<L>/experiments/logs/`, or it is marked "not yet measured" (BUILD.md §0.3).
- **Deck engine:** the Sky theme, `engine/plates.{css,js}` (BUILD.md §2). The deck must pass `tools/deck_qa_modal.py` with 0 issues.
- **Notebook:**
  - Colab, percent-format `.py` → `tools/nbbuild.py`.
  - The first cell is `# %% setup`; it installs from `github.com/RajatDandekar/agents-for-enterprises`.
  - It runs in replay mode with no key, recorded first with `--mode auto`.
  - It has 3–6 TODO exercises with solutions.
  - Name cassettes `L<n>v3_<what>` so they never collide with v2's.
- **Assignment:** `A<n>.md`, a short build on the student's own module kit, with a checklist and grading.
- **Words:** plain and short; Indian number formatting; no hype words (BUILD.md §2).

## Folders and owners (v3)
| Owner | Files |
|---|---|
| lead | `bahi/bahi/erp/*`, `bahi/bahi/toolbox/*` (tools are shared: ask in your report for a change), `bahi/bahi/llm.py`, `engine/*`, `tools/*`, `BUILD.md`, `COURSE_V3.md`, `index.html`, `hub.html`, `figures/` |
| experience | `bahi/bahi/experience/` (all except `studio/`), `bahi/bahi/erp/screens/INV-GRN-03.yaml`, `bahi/bahi/legacy_ui/`, `deploy/experience_modal.py` |
| studio | `bahi/bahi/experience/studio/` |
| L1 … L8 | `lectures/L<n>-<slug>/` (one folder each), plus any new module the lecture needs under `bahi/bahi/course/l<n>/` |

Lecture folder slugs: `L1-before-and-after`, `L2-the-brain`, `L3-the-memory`, `L4-the-hands`, `L5-the-loop`, `L6-the-studio`, `L7-trust`, `L8-your-module`.

**Live URL contract.**
- The experience builder deploys and writes the URL into `bahi/bahi/experience/DEPLOYED.md`.
- Until it exists, decks link to `https://rajatworkspace--rasoi-experience.us-east.modal.run` (the expected URL).
- Screenshots of the app are taken headless on Modal once it is live.


## v3.1 (2026-10-28): twelve lectures, with four on the industry stack
Rajat asked for the production tools companies use, each with a proper introduction, comprehensive content, interesting assignments and good visuals. They get four lectures of their own. The research behind the choice of tools is in `INDUSTRY_TOOLS_PLAN.md`.

| # | Date (proposed) | Folder | Title | Flagship tools (taught in depth) | Also covered |
|---|---|---|---|---|---|
| 1–7 | as before | as before | unchanged, except L1 gains a "2026 agent stack" map plate and a 12-lecture series map | | |
| 8 | Sun 22 Nov | `L8-frameworks` | **Agent Frameworks in Industry** | OpenAI Agents SDK; Google ADK; LangGraph (recap); model gateways (OpenRouter, LiteLLM); local models (Ollama) | Claude Agent SDK, CrewAI, Microsoft Agent Framework, LlamaIndex on a "which one when" plate |
| 9 | Sat 28 Nov | `L9-protocols` | **Protocols and Integration** | MCP in depth (official SDK, resources and prompts, MCP Inspector, remote servers and auth, MCP security); A2A (agent cards, tasks); n8n self-hosted | Claude Desktop, VS Code and Cursor as hosts; the GitHub MCP server; Copilot Studio and Agentforce as enterprise low-code |
| 10 | Sun 29 Nov | `L10-observability-evals` | **Observability and Evals in Industry** | OpenTelemetry GenAI conventions; Langfuse; Arize Phoenix; DeepEval as a CI gate; Ragas; promptfoo red-teaming | LangSmith, Braintrust, Datadog LLM Observability; LLM-judge calibration |
| 11 | Sat 5 Dec | `L11-production` | **Running Agents in Production** | Guardrails (NeMo Guardrails, Llama Guard, prompt-injection defence, OWASP LLM Top 10); Temporal durable execution with the OpenAI Agents SDK; pgvector and Redis; LiteLLM budgets and fallbacks | AWS Bedrock AgentCore, Microsoft Foundry, Google's agent platform; cost model; deployment |
| 12 | Sun 6 Dec | `L12-your-module` (was L8) | **Your Module: Demo Day** | The student's chosen production stack | The rubric requires at least two industry tools, chosen with a reason |

**Rules for L8–L11:**
- **Story:** the same Rasoi company, the same Ask Rasoi agent and the same tasks. Each tool is introduced from first principles: what problem it solves, how it works inside, and how it maps to what the students built by hand in L1–L7. Then it is used on Ask Rasoi.
- **Honest measurement:** every comparison is measured on our own runs (for example, the same 12 tasks with each framework). Never use vendor claims as results; cite market evidence with its source and caveats.
- **Free to run:** every lab runs on free Colab in replay with no key, from recorded traces and outputs. Live runs use the student's own key; OpenRouter is the default route for every SDK that supports it.
- **Pinned versions:** pin every SDK version in the notebook's install cell.
- **Budget:** about $5 of OpenRouter spend per lecture for experiments. The key's remaining limit is about $44 in total.
- **Keys:** Gemini works again (direct). Langfuse keys are in the course `.env`. There are no keys for LangSmith, Braintrust, Anthropic (Claude Agent SDK), Hugging Face (gated Llama Guard weights) or AWS. Design around them: use the OpenRouter route where one exists; otherwise show the code, mark it "not run in our build", and never fake an output.
