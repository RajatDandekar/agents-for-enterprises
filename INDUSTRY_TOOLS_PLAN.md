# Industry tools in Agentic Systems Engineering: research and plan (2026-10-28)

## Why
Students will expect the tools companies actually run. The course already builds every piece from scratch: the toolbox over MCP, the harness, the control graph, the Studio, evals and recovery. That keeps the first-principles story; this plan adds an **"In industry"** segment to each lecture. After a piece is built by hand, the same piece is shown in the tool companies use, with the concept mapped one to one: "you just built a Runner; this is the OpenAI Agents SDK's Runner".

## What the market uses (October 2026)
Most public numbers come from vendor surveys and blogs, so read them as directional.

| Layer | Tools in use | Evidence |
|---|---|---|
| Agent frameworks | LangGraph, OpenAI Agents SDK, Google ADK, Claude Agent SDK, CrewAI, Microsoft Agent Framework, LlamaIndex | Stack Overflow 2025 (people who had used agents): Ollama 51%, LangChain 33%, LangGraph 16%, Vertex AI 15%, Bedrock Agents 15%, OpenRouter 13%, LlamaIndex 13%. LangGraph ~34.5M monthly PyPI downloads vs ~10.3M for the OpenAI Agents SDK (secondary source) |
| Tool protocol | MCP (Linux Foundation, ~97M monthly SDK downloads); A2A for agent-to-agent (150+ organisations, LF release Apr 2026) | Linux Foundation; secondary coverage |
| Observability | LangSmith, Langfuse (open source), Arize Phoenix, Datadog LLM Observability, Braintrust; OpenTelemetry GenAI conventions as the common wire format | LangChain State of Agent Engineering: 89% have agent observability, 62% full step tracing. Stack Overflow 2025: LangSmith the only observability tool with real traction (13%) |
| Evals | DeepEval, promptfoo (OpenAI announced its acquisition, Mar 2026), Ragas (RAG), Inspect AI, Braintrust / LangSmith datasets | Same LangChain survey: 52% run offline evals, 37% online, fewer than a third run both |
| Guardrails and security | NeMo Guardrails, Guardrails AI, Llama Guard, Bedrock Guardrails, Azure Prompt Shields | Prompt injection is #1 in the OWASP Top 10 for LLM Applications 2025 |
| Durable execution | Temporal (OpenAI Agents SDK integration GA, Mar 2026), Inngest, Restate, DBOS | Temporal announcements |
| Model gateways | OpenRouter, LiteLLM, Portkey, Cloudflare AI Gateway | Stack Overflow 2025; comparisons |
| Managed agent platforms | AWS Bedrock AgentCore, Microsoft Foundry (+ Agent365), Google's Gemini Enterprise agent platform (ADK), OpenAI AgentKit | Vendor documentation and comparisons |
| Low-code builders | n8n, Microsoft Copilot Studio, Salesforce Agentforce, Zapier | Widely deployed; no reliable public usage numbers |
| Memory and data | Redis, pgvector / Qdrant / Pinecone, GitHub MCP server | Stack Overflow 2025: Redis 43%, GitHub MCP server 43% |

## Rules for adding a tool
1. **The story comes first.** Each tool appears after the concept is built by hand, as the production version of what students just made, never as a substitute for understanding it.
2. **Free to run.** Every tool is open source or has a free tier, and runs on Colab with no key, using recorded traces and outputs. Live runs are optional, with the student's own key.
3. **One flagship per layer, others named.** Teach one tool deeply and put the alternatives on a single "which one when" plate. Tool choice changes fast; the concepts do not.
4. **Show it on Ask Rasoi.** Every industry demo runs on the same Rasoi agent, so students compare like with like: the same task, hand-built and with the tool.

## Plan per lecture
Each lecture gains a 12–15 minute "In industry" segment (6–10 plates) and an optional "Industry lab" section in its notebook.

| Lecture | Flagship tool, taught | Shown or named | What students do |
|---|---|---|---|
| L1 Before and After (31 Oct) | *(map only)* | The 2026 agent stack, layer by layer: one plate mapping each part of Ask Rasoi to the market's tools, plus the buy side (Agentforce, Copilot Studio, Bedrock AgentCore) | See where every tool in the course fits |
| L2 The Brain (1 Nov) | OpenRouter / LiteLLM (one API, many models) | Ollama for local models; tiktoken for tokens | Send the same prompt to 3 models through one gateway; run a small model locally |
| L3 The Memory (7 Nov) | Ragas (RAG metrics) | pgvector / Qdrant as the production vector store; LlamaIndex as the framework version | Score their retriever with Ragas next to our 40-question eval; swap the in-memory index for pgvector |
| L4 The Hands (8 Nov) | Official MCP SDK + MCP Inspector | Claude Desktop, Cursor and VS Code as MCP hosts; the GitHub MCP server; A2A in one plate | Inspect the Rasoi toolbox in MCP Inspector; connect it to a desktop host |
| L5 The Loop (14 Nov) | OpenAI Agents SDK, the same harness rebuilt; LangGraph is already taught | Google ADK, Claude Agent SDK, CrewAI on one comparison plate | Port Ask Rasoi to the Agents SDK in ~60 lines and compare traces with our harness |
| L6 The Studio (15 Nov) | n8n (self-hosted, free) running the same workflows | Copilot Studio and Agentforce as the enterprise low-code equivalents | Import the Diwali workflow into n8n, calling the Rasoi toolbox over MCP |
| L7 Trust (21 Nov) | Langfuse (open source) over OpenTelemetry GenAI traces; DeepEval in CI; promptfoo red-teaming; Temporal for durable waits | LangSmith, Phoenix, Braintrust, Datadog; NeMo Guardrails / Llama Guard; Bedrock AgentCore as a managed runtime | Trace Ask Rasoi in Langfuse; add a CI eval gate; red-team it for prompt injection |
| L12 Your Module (6 Dec) | *(student's choice)* | A "production stack" menu | Capstone must use at least two industry tools, chosen with a written reason; 10 of the 100 rubric points |

## Delivery order (honest about time)
- **Before Sat 31 Oct:** the L1 stack-map plate only, plus a one-line mention in the curriculum.
- **Before Sun 1 Nov:** the L2 gateway and Ollama segment.
- **The week of 2 Nov:** L3 and L4 segments.
- **The week of 9 Nov:** L5 and L6 (the Agents SDK port and the n8n import are the biggest pieces).
- **The week of 16 Nov:** L7, the largest: Langfuse, DeepEval, promptfoo, Temporal.
- **L8:** the rubric and stack menu, alongside L7.
- **Website:** add an "Industry tools you'll use" strip to the curriculum section once L1–L2 are done.

## Risks
- **API churn:** vendor SDKs change quickly. Pin versions in `nb_setup.txt`, and keep recorded fixtures so replay never breaks.
- **Key-free replay:** a live call through a third-party SDK can't use our cassettes directly. The labs replay the recorded trace and tool calls, and go live only with a student's key.
- **Bias:** some evidence above comes from vendor-run surveys. Teach concepts first, and present tools as current choices, not permanent truths.


**Update, 2026-10-28:** Rajat chose dedicated lectures. The tools are taught in L8–L11 (see COURSE_V3.md v3.1) rather than as segments inside L1–L7. The per-lecture table above was the first proposal.
