"""Stack (c): Ask Northbridge as LangGraph's prebuilt tool-calling agent (langgraph 1.2.15), tools from MCP.

    agent = LangGraphStack(system, mcp_url, base_url, model="google/gemini-3.8-flash")

LangGraph draws the same loop as a graph of two nodes, "agent" (the model) and "tools" (run the calls), with an edge
back, until the model answers in words.
    create_react_agent   the loop as a graph            prompt      the system prompt
    tools                from MCP (langchain-mcp-adapters, MultiServerMCPClient)
    checkpointer         the conversation (InMemorySaver here; Postgres or SQLite in production), per thread_id
    recursion_limit      the step cap (two graph steps per model call)
"""
from __future__ import annotations

import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent

from .agents_sdk import _Loop
from .ours import MAX_STEPS


async def _build(system: str, mcp_url: str, base_url: str, model: str):
    client = MultiServerMCPClient({"ledgerline": {"url": mcp_url, "transport": "streamable_http"}})
    tools = await client.get_tools()
    llm = ChatOpenAI(model=model, base_url=base_url, temperature=0, max_retries=0, timeout=600,
                     api_key=os.environ.get("OPENROUTER_API_KEY", "through-the-gateway"))
    return create_react_agent(llm, tools, prompt=system, checkpointer=InMemorySaver())


class LangGraphStack:
    framework = "langgraph"

    def __init__(self, system: str, mcp_url: str, base_url: str, model: str, max_steps: int = MAX_STEPS):
        self.max_steps = max_steps
        self.lt = _Loop()
        self.graph = self.lt.run(_build(system, mcp_url, base_url, model))
        self.native: list[dict] = []   # one row per graph step: which node ran, what it asked or returned
        self.stops: list[str] = []

    async def _ask(self, text: str) -> str:
        cfg = {"configurable": {"thread_id": "conversation"}, "recursion_limit": 2 * self.max_steps + 1}
        last = ""
        try:
            async for update in self.graph.astream({"messages": [{"role": "user", "content": text}]}, cfg,
                                                   stream_mode="updates"):
                for node, out in update.items():
                    row = {"node": node}
                    for m in (out or {}).get("messages", []):
                        if getattr(m, "tool_calls", None):
                            row.setdefault("calls", []).extend(c["name"] for c in m.tool_calls)
                        elif node == "agent":
                            last = m.content if isinstance(m.content, str) else str(m.content)
                    self.native.append(row)
        except GraphRecursionError:
            self.stops.append("max_steps")
            return f"(stopped after {self.max_steps} steps)"
        return last

    def respond(self, text: str) -> str:
        return self.lt.run(self._ask(text))

    def close(self):
        pass
