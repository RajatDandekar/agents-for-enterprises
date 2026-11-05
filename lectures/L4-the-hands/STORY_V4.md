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

## Sections (v5, after Dr. Rajat Dandekar's review of 5 Nov 2026: `HEPHAESTUS_SPEC.md`)
The order below is the deck's since 5 Nov 2026. The 4 Nov order (MCP in two sections, then two harnesses) is in
`archive_v4/`. Two live practicals in **Hephaestus**, the tool forge (`ledgerline/ledgerline/hephaestus/`), are done by
every student; the six forge questions (`hephaestus/questions.json`) are the same in both.

1. **What is a tool?** A function our code runs when the model asks for it. The model only writes text: a structured
   request. Our code checks it, runs it in Emma's own Ledgerline session and returns a result. The end-to-end slide is a
   click-by-click build-up in three bands (the model, our code, Ledgerline): no line joins the model to Ledgerline.
2. **Schemas from scratch.** JSON Schema: types, required fields, enums, formats, descriptions and examples. The
   **input schema** is what the model must send; the **output schema** is a promise of what comes back, field by field,
   shown on check_stock's real result; three readers rely on it (the host checks it, the model reads names and meanings,
   the next tool uses a field without guessing), and without it a broken result passes silently.
3. **Open a tool.** `toolbox/check_stock/tool.json` and `tool.py`, line by line; the services inside (`itm_get`,
   `whs_list`, `stk_query`, from `northbridge-docs/04_service_definitions`); the legacy envelope; the error contract.
4. **Build a tool from scratch.** `supplier_certificates` in six steps: the job, the services, the schema, the code, the
   error contract, the tests.
5. **Hephaestus, part 1 (live).** Each student joins and gets a forge: their own sandbox as Emma and seven real tools.
   The Anvil (what the model reads vs what runs), Ask (the six questions on our harness, every step traced), Experiments
   (one knob at a time: name and description, input schema, output fields and rows, error replies, how many tools, the
   rules; `hephaestus/knobs.json`), The Shield (four attacks with the rule off, in the prompt, in the tool, and on a host
   without our prompt; identity Emma vs a service account), then "is security done by the tool or by guardrails?" from
   first principles: both, each for its own job.
6. **MCP, trimmed.** Why one standard (N × M), host / client / server in one picture, and "your tools at one address":
   tools/list, tools/call, a URL. The JSON-RPC wire, the two transports and the field alignment are in `NOTES.md`.
7. **Hephaestus, part 2 (live): two harnesses.** Everyone connects their forge to Claude (claude.ai / Desktop custom
   connector, or `claude mcp add --transport http`), asks the same six questions and compares with part 1: who decided,
   how many calls, what it cost, what each harness let us control.
8. **What the LLM sees.** The context window fills, turn by turn (unchanged).
9. **Orchestration, one build-up.** Question 6 ("…Nordic Cell Co. is the cheapest: can we use them? If not, choose a
   certified supplier, check PRD-07 can afford it, and prepare the request."): the question drawn out; the tools it
   logically needs and why, run by hand in order (`logs/q6_plan_calls.json`); who runs the loop (the model orchestrates
   in both harnesses; what differs is who writes the loop and where the rules live); the recorded runs of Emma's order on
   both harnesses; then question 6 live.
10. **Production grade.** The criteria table, then one slide per criterion: what it is, how we measured it
    (`experiments/production_grade.py`), how to run it in the forge's Production tab, and what to do in your own project.
    Idempotency is the one found and fixed live.
11. **NB4, the A4 walkthrough with highlighted cells, and Lecture 5** (The Loop).

**Rhythm:** part slide → teach → the section's question → film (where there is one) → 1–3 technical checks. 113 slides (v5), with two live forge practicals.

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
