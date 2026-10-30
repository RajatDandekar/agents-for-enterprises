"""Lecture 1, "In production": the same Ask Northbridge on three stacks and six models, traced and scored.

    prompt.py           the one system prompt every stack and model gets
    missions.py         the five L1 missions as an eval suite: set-up in code, scripted person, scores read from Ledgerline,
                        never-events NE1-NE6
    toolserver.py       the 15 Ledgerline tools over MCP (streamable HTTP), one server per person per mission
    gateway.py          the model gateway: OpenRouter, cassettes (L1v4_prod_*), billed cost, a spend cap
    tracing.py          OpenTelemetry GenAI spans to Langfuse; the deck's waterfall
    ours.py             stack (a): our own loop, by hand
    agents_sdk.py       stack (b): the OpenAI Agents SDK (openai-agents 0.20.0)
    langgraph_agent.py  stack (c): LangGraph's prebuilt agent (langgraph 1.2.15 + langchain-mcp-adapters 0.3.2)
    runner.py           Rig: run a mission or the suite on one stack and model

    from ledgerline.course.l1.production.runner import Rig
    rig = Rig(langfuse=False)                                  # LEDGER_LLM_MODE=replay plays the recorded run, no key
    rows = rig.run_suite("langgraph", "google/gemini-3.8-flash", run=1)
    [(r["mission"], r["passed"], r["never_events"]) for r in rows]

Every stack gets the same prompt, the same 15 tools from the same MCP server, the same model through the same gateway,
and the same step cap (12 model calls per message). Only the code that runs the loop changes. In the ablation only the
model changes. The framework SDKs are imported only by the module that needs them.
"""
