# Lecture 4 v4: The Hands. Tools, MCP, two harnesses, production grade

Rajat's brief (3 Nov 2026), summarised. This lecture is "at the heart of this course and should be built with a lot of care".
- Define tools from scratch: the input and output schemas, then `tool.json` and `tool.py`, and how the services sit inside a tool. Students should be able to open any tool and understand exactly what is going on.
- Build a tool from scratch, and align it with the MCP standard.
- Connect one tool to an MCP server.
- Demo on **Claude's harness and our harness**, with slides on the difference: what is in our control in ours, and what is left to Claude's orchestration in theirs.
- Show **what the LLM actually sees in its context**, filling up step by step (tool definitions, tool calls, tool results), with an animation and a GIF. People think the LLM sees everything inside a tool. It does not.
- Expose several tools and show the LLM orchestrating them, on both harnesses.
- Make the tools production grade, using the relevant criteria from Rajat's table.
- Questions follow the L1/L2 pattern.

**Class:** Sun 8 Nov 2026, 7–9 AM IST. **World:** Northbridge (`WORLD_V4.md`). **Never:** the real client's or product's names, real client data. The second harness is always "our harness" (Ask Northbridge's).

## The story
Lecture 3 gave Ask Northbridge a memory: it now cites §6.2 and tells Emma that Brightcell is not allowed. Then Emma asks it to do the real work: *"Order 2,000 BAT-500 packs from Voltway for the spring launch run."* It can only describe the screens. It has knowledge, but no hands.

**Running example:**
- The single tool is `check_stock`: Emma's 5,400 from Lecture 2, finally fetched live.
- The orchestration is Emma's full order. It calls find_item → check_stock → find_supplier → check_budget → search_policy → create_purchase_request. Daniel then approves.

## Sections
1. **What is a tool?** A function our code runs when the model asks for it. The model only writes text: a structured request. Our code checks it, runs it in Emma's own Ledgerline session and returns a result.
2. **Schemas from scratch.** JSON Schema covers types, required fields, enums, formats, descriptions and examples. The **input schema** is what the model must send; the **output schema** is what it gets back.
3. **Open a tool.** Walk through `toolbox/check_stock/tool.json` and `tool.py` line by line.
   - The **services inside it** are the legacy Ledgerline services the tool calls (`itm_search`, `stk_query` and others), in the legacy envelope `{rc, err_cd, msg, data}`.
   - The tool turns them into one clean, typed result with a structured error.
   - Where did we find the services? In `northbridge-docs/04_service_definitions`, which ties back to Lecture 3.
4. **Build a tool from scratch.** A new tool, for example `supplier_certificates`, built step by step:
   1. the job;
   2. find the services in the docs;
   3. the schema;
   4. the code;
   5. the error contract;
   6. tests.
5. **The MCP standard.**
   - Why a standard: N apps × M systems.
   - JSON-RPC: `initialize`, `tools/list`, `tools/call`; transports (stdio and streamable HTTP).
   - The tool definition: name, title, description, inputSchema, outputSchema, annotations (readOnlyHint, destructiveHint, idempotentHint).
   - The result: content, structuredContent, isError.
   - Align our `tool.json` with it, field by field.
6. **One tool on an MCP server.** Start the Northbridge MCP server with one tool and inspect it (MCP Inspector, the raw JSON-RPC messages).
7. **Two harnesses, one tool.**
   - **Claude's harness:** Claude Desktop or Claude Code (`claude mcp add` / config) connected to our MCP server.
   - **Our harness:** Ask Northbridge's loop (`ledgerline/agent`, `experience/harness.py`).
   - The difference slides, on what is in our control: model choice, system prompt, which tools each user or stage sees, approval gates, guardrails, loop limits, identity and session, logging and cost. Against that: Claude orchestrates, Anthropic's system prompt, per-call approval in the UI, and less control over how the steps are taken.
8. **What the LLM sees.** The context window fills, turn by turn: the system prompt → the tool definitions (and their token cost) → Emma's message → the model's tool call (JSON) → the tool result (only what the tool returns) → the reply.
   - The LLM never sees `tool.py`, the services, the database, the session or the password.
   - Shown as a film, an interactive replay of a real recorded context and a GIF.
9. **Orchestration.** Expose all 15 tools. Emma's full order runs on both harnesses (real recorded runs); compare the traces: order, arguments, errors recovered, calls and tokens. What goes wrong without control, and what our harness adds.
10. **Production grade.** The relevant criteria, measured on our toolbox (real numbers), with one failing criterion found and fixed live:

    | Area | Criterion | Threshold |
    |---|---|---|
    | Schema | Input and output validation | 100% of tools; 0 schema violations in regression |
    | Reliability | Unhandled or non-business errors | ≤ 0.1% of calls; 100% in the structured error contract |
    | LLM usability | Right tool, right arguments on a golden set, per host | ≥ 95% pass@1, reported per host |
    | Latency | Tool overhead, excluding ERP service time | p50 ≤ 50 ms · p95 ≤ 100 ms · p99 ≤ 200 ms |
    | Payload | Response size | Every list tool paginates; nothing above the agreed size limit |
    | Idempotency | Duplicate or retried writes | 0 duplicate postings |
    | Timeouts | Timeout and retry policy | Defined and tested on 100% of tools |
    | Regression | Happy path, validation errors, permission denied, pagination, retries | ≥ 98% of tools; 100% of write tools |
    | MCP compliance | Conformance on Claude, OpenAI, Gemini and our harness | 100% of tools on all 4 |
    | Change management | Versioning, release notes, rollback | Documented and signed off by the client |

11. **NB4, the A4 walkthrough with highlighted cells, and Lecture 5** (The Loop).

**Rhythm:** part slide → teach → the section's question → film (where there is one) → 1–3 technical checks. About 90–100 slides.

## Experiments (Modal or light local; logs in `lectures/L4-the-hands/experiments/logs/`)
- The anatomy data for `check_stock`: real `tool.json`, `tool.py`, its services' definitions and a real call (request, legacy reply, tool result).
- The new tool `supplier_certificates`, built and tested; it joins the toolbox with tests.
- MCP: raw JSON-RPC captures (`initialize`, `tools/list`, `tools/call`) from our server.
- **Claude's harness:** a real run of Claude Code headless (`claude -p` with `--mcp-config`) against our MCP server, for one tool and then for Emma's full order, with the transcript recorded.
- **Our harness:** the same two runs (gemini-3.8-flash via OpenRouter, cassettes), with the full context captured at every step (the messages array and tokens per part).
- **The host-compliance matrix:** the same tools exposed to Claude, an OpenAI model, Gemini and our harness (via OpenRouter where needed); the golden set of tool-use tasks, pass@1 per host.
- **Production-grade measurements:**
  - schema checks;
  - error-contract fuzzing;
  - latency overhead p50/p95/p99 (service time excluded);
  - payload sizes and pagination;
  - an idempotency test (a retried create, 0 duplicates);
  - the timeout/retry policy test;
  - the regression suite pass rate.

## Films (about 3)
1. **`tool`** "Inside a tool": the model's request → tool.json checks it → tool.py calls the legacy services → the legacy envelope → one clean result.
2. **`context`** "What the model sees": the context window filling, part by part, with real tokens. The inside of the tool stays dark.
3. **`orchestra`** "Many tools, one request": Emma's order, the calls in sequence, both harnesses.

## Deliverables
- `index.html`, `NOTES.md` and figures, including the context replay and its GIF;
- `NB4_the_hands.ipynb` (replay, no key);
- `A4.md`: build a tool for your domain from its service definitions, put it on MCP, run it on two harnesses and measure it against the production criteria;
- the toolbox additions with tests;
- `?stage=hands` live;
- 3 films.
