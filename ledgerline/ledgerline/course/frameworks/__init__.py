"""Lecture 8, Agent Frameworks in Industry: the same Ask Northbridge in the frameworks companies use.

    meter.py            Meter: a tiny OpenAI-compatible gateway on localhost (records, replays, counts tokens and £)
    mcp_http.py         serve_toolbox(erp, user): the Lecture 4 toolbox over MCP on streamable HTTP; MCPToolbox
    base.py             Port: what every port shares (instructions, loop thread, the uniform trace)
    ours.py             our Lecture 5 Harness and ControlGraph, tools over MCP
    openai_agents.py    AgentsSDKPort   (openai-agents 0.20.0)
    adk.py              ADKPort         (google-adk 2.11.0, model via LiteLLM)
    langgraph_react.py  LangGraphPort   (langgraph 1.2.15 create_react_agent + langchain-mcp-adapters)
    desks.py            handoffs, guardrails and sessions on the Agents SDK; sub-agents on ADK
    fixtures.py         load the recorded results (recorded/*.json, written by lectures/L8-frameworks/gen_figdata.py)

Every port has respond(text) -> str, so ledgerline.course.l5.tasks.run_task runs the same twelve tasks on each.
The framework SDKs are imported only by the module that needs them.
"""
