"""Ask Rasoi as LangGraph's prebuilt tool-calling agent (langgraph 1.2.15), tools from MCP (langchain-mcp-adapters).

    from bahi.course.frameworks.langgraph_react import LangGraphPort
    a = LangGraphPort(Toolbox(erp, "KJOSHI"), meter, "lg-T01-KJOSHI")

Lecture 5 built a control graph by hand (bahi.course.l5.graph: spine and gates). This is the other thing LangGraph
gives you: the free loop as a two-node graph, agent <-> tools, that runs until the model answers in words.
    create_react_agent  = the loop as a graph: node "agent" (the model), node "tools" (run the calls), an edge back
    prompt              = the system prompt;  tools = the registry (from MCP)
    checkpointer        = the history (one thread_id per person); recursion_limit = the step cap
"""
from __future__ import annotations

import os

from .base import Port

# --- port ---------------------------------------------------------------- (lines counted on the plate)
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent


async def make_agent(system: str, mcp_url: str, base_url: str, model: str):
    client = MultiServerMCPClient({"bahi": {"url": mcp_url, "transport": "streamable_http"}})
    tools = await client.get_tools()
    llm = ChatOpenAI(model=model, base_url=base_url, temperature=0,
                     api_key=os.environ.get("OPENROUTER_API_KEY", "replay"))
    return create_react_agent(llm, tools, prompt=system, checkpointer=InMemorySaver())


async def ask(graph, thread: str, text: str, max_steps: int, steps: list) -> str:
    cfg = {"configurable": {"thread_id": thread}, "recursion_limit": 2 * max_steps + 1}
    last = ""
    try:
        async for update in graph.astream({"messages": [{"role": "user", "content": text}]}, cfg,
                                          stream_mode="updates"):
            for node, out in update.items():
                steps.append((node, out))
                for m in (out or {}).get("messages", []):
                    if node == "agent" and not getattr(m, "tool_calls", None):
                        last = m.content if isinstance(m.content, str) else str(m.content)
    except GraphRecursionError:
        return f"(stopped after {max_steps} steps)"
    return last
# --- end port ------------------------------------------------------------


def step_row(node, out) -> dict:
    row = {"node": node}
    for m in (out or {}).get("messages", []):
        if getattr(m, "tool_calls", None):
            row.setdefault("calls", []).extend({"name": c["name"], "args": c["args"]} for c in m.tool_calls)
        elif m.type == "tool":
            row.setdefault("results", []).append({"name": m.name, "content": str(m.content)[:400]})
        elif m.content:
            row["text"] = str(m.content)[:600]
    return row


class LangGraphPort(Port):
    framework = "langgraph"

    def __init__(self, tb, meter, tag, **kw):
        super().__init__(tb, meter, tag, **kw)
        self.graph = self.lt.run(make_agent(self.system, self.srv.url, self.base_url, self.model))

    async def _respond(self, text: str) -> str:
        steps: list = []
        reply = await ask(self.graph, f"{self.tb.user}-thread", text, self.max_steps, steps)
        if reply.startswith("(stopped"):
            self.stops.append("max_steps")
        self.native.append({"turn": self.turn, "steps": [step_row(n, o) for n, o in steps]})
        return reply
