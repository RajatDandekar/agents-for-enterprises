# Demo day: the scoring sheet (/100)

**Lecture 12, Agentic Systems Engineering · demo day, Sun 6 Dec 2026.** One sheet per module, live or recorded. The
grader fills it from the student's own files and from two re-runs on Modal in replay mode (no key): the module's four
scenarios on the student's agent, and the hidden demo-day test (`experiments/grade_change.py`).

Module: ____________________  Student(s): ____________________  Live / recorded: ______  Grader: ______

## Two rules that override the rest

1. A never-event in any scenario zeroes that scenario's points, however good the rest is.
2. A number said in the demo that does not match the student's own log, or the replay, scores the lower of the two.

Each line below is fed by the assignments named in it. An assignment's own page gives its items in full; this sheet
takes them at the weights shown, so the lines add up to 100. Lines 1–6 are the module built by hand (L1–L7); line 7
is the same module on the industry stack (L8–L11).

**Changed in v3.1 (twelve lectures):** line 7, production stack (10), is new. To make room, scenario pass rate went
from 25 to 20 and operations from 15 to 10; tools, route and authority, retrieval and the demo-day change are unchanged.

## 1. Scenario pass rate · 20 (A5, A6, A7; earned on demo day)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The four kit scenarios pass on the student's agent, replayed | 6 (1.5 each) | `run_module_scenario` for scenarios 1–4, replay mode | |
| The A7 suite: four scenarios × three runs, code checks on Bahi | 8 | `results.json`: 8 × (runs passed / 12) | |
| A5's three harness scenarios (S1–S3) pass with the full harness | 4 | A5 pass/fail table | |
| A6: the jobs a workflow now handles end in the right state | 2 | A6 run logs (first and second run) | |
| **Subtotal** | **20** | | |

## 2. Tools · 20 (A4)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Tool design: business activities, not services; descriptions a model can choose by; schemas complete | 6 | The `tool.json` files; `lint_folder()` clean | |
| The six promises in every tool: typed inputs, errors with `next_step`, preview, a key from the content, a receipt read back from Bahi, the user's own session | 6 | Tool code | |
| Lost-reply test: exactly one document after an injected `timeout_after_commit` | 4 | The notebook, replay mode | |
| Served over MCP in the speaker's session, wire captured | 2 | `a4_wire.json` | |
| Write-up: the tool you chose not to write | 2 | A4 note | |
| **Subtotal** | **20** | | |

## 3. Route and authority · 15 (A5, A7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The pause: an approval wait saved, resumed only on Bahi's word (A5) | 5 | The paused scenario's trace | |
| Identity: the speaker's own session everywhere; no service-account write (A7) | 3 | Bahi's call log: users seen | |
| A guard per never-event, each shown refusing a real call with a rule and a next step (A7) | 4 | The guard and its refusals | |
| Read-back: the silent outcome caught and never reported as done; the reply check (A7) | 3 | One run of the silent outcome | |
| **Subtotal** | **15** | | |

## 4. Retrieval · 15 (A3)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| As A3's own grading: the corpus indexed, the test questions graded by code, citations, the stale document handled, who may read what | 15 | A3 results and transcript | |
| **Subtotal** | **15** | | |

## 5. Operations · 10 (A5, A6, A7)

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| An LLM judge beside the code checks, every disagreement explained (A7) | 2 | `NOTE.md` | |
| One change gated, the verdict pasted and acted on (A7) | 2 | The gate output | |
| One failing trace read, the wrong step named (A7) | 2 | The trace | |
| Workflows safe to run twice; run logs complete; replay works (A6) | 2 | A6 logs | |
| Bare vs harness table with calls, tokens and ₹ (A5) | 2 | A5 table | |
| **Subtotal** | **10** | | |

## 6. The demo-day change · 10

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| The hidden test passes on the student's agent | 6 | `grade_change.py --module <kit> --agent py:<pkg>:make_agent --mode replay` | |
| Where the change now lives (document, tool, guard), one new case in the suite, and the gate run showing nothing else broke | 4 | The demo, the suite file, the gate output | |
| **Subtotal** | **10** | | |

## 7. Production stack · 10 (L8–L11; earned on demo day)

Your module must run on **at least two industry tools from Lectures 8–11**, from two different layers of the menu
below, each chosen with a written reason. The hand-built piece stays in your repository: the tool replaces it or
watches it, and you show both.

| Item | Points | How the grader checks | Score |
|---|---|---|---|
| Two tools from two different layers, each wired into the module and shown working on it, with a pinned version | 4 (2 each) | `STACK.md` and the log, trace export or replay it points to | |
| A written reason for each: the problem it solves for this module, the hand-built piece it replaces or watches, and the alternative you did not pick and why | 4 (2 each) | `STACK.md`, at most 150 words per tool | |
| One comparison measured on your own run: the hand-built piece and the tool on the same task (for example the four scenarios through our harness and through the Agents SDK; the A7 suite in our gate and in DeepEval) | 2 | The two logs, same scenarios | |
| **Subtotal** | **10** | | |

Rules for this line:
- **Free to grade.** The grader re-runs in replay with no key, so commit what the tool produced (a recorded trace, an
  exported run, a test report) and the command that made it. A tool that needs a paid account counts only with its
  recorded output; a screenshot alone scores half; an output that was not produced by a run scores 0.
- **Our numbers, not the vendor's.** The comparison is measured on your module. A vendor's benchmark scores nothing.
- **The trust rules still hold.** A tool that writes to Bahi does it in the speaker's own session, through your tool
  folders and their six promises. A framework that bypasses a guard or the read-back is a never-event (rule 1).

### The production stack menu

| Layer | Lecture | Pick one of | It replaces or watches | Free route in our build |
|---|---|---|---|---|
| Agent framework | L8 | OpenAI Agents SDK, Google ADK, LangGraph | The L5 harness and loop | OpenRouter key, or replay |
| Model gateway, local model | L8, L11 | OpenRouter, LiteLLM (with a budget and a fallback), Ollama | The single model call in `bahi/llm.py` | Ollama locally; LiteLLM is open source |
| Protocols | L9 | Your toolbox as a remote MCP server with sign-in, checked in MCP Inspector; an A2A agent card so another agent can hand your module a task | The L4 server in the speaker's session | Open source |
| Workflow, low-code | L9 | n8n (self-hosted) running your A6 workflow over MCP | The L6 Studio workflow | Self-hosted n8n is free; Copilot Studio and Agentforce count only with recorded output |
| Observability | L10 | Langfuse or Arize Phoenix, over OpenTelemetry GenAI traces | The L7 trace you read by hand | Both open source; LangSmith counts only with an exported trace |
| Evals | L10 | DeepEval as a CI gate on your suite; Ragas on your A3 retrieval; promptfoo red-teaming your module for prompt injection | The L7 suite and gate; the A3 grader | Open source |
| Guardrails | L11 | NeMo Guardrails, Llama Guard, a prompt-injection filter | The L7 guards (keep yours: the rail is a second layer) | NeMo is open source; Llama Guard 4 runs through OpenRouter (`meta-llama/llama-guard-4-12b`) |
| Durable execution | L11 | Temporal holding your approval wait | The L5 pause and the L7 recovery keys | Temporal's local dev server is free |
| Data stores | L11 | pgvector or Redis for your module's index or memory | The L3 in-memory index | Open source |
| Managed platform | L11 | Bedrock AgentCore, Microsoft Foundry | The whole runtime | Paid: counts only with recorded output; a written deployment plan is welcome but scores 0 on its own |

**Total: ____ / 100**

## Live and recorded, the same sheet

Live slots are 8 minutes (`DEMO_DAY.md`); the production stack is shown inside the After segment and asked about in the
client's questions. A recorded demo is 5 minutes, one take; the grader re-runs everything in
replay mode, and a recording whose numbers do not match the replay scores the lower of the two.
