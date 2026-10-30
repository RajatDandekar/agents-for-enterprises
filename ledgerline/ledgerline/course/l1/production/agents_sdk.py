"""Stack (b): Ask Northbridge on the OpenAI Agents SDK (openai-agents 0.20.0), model through the gateway.

    agent = AgentsSDKStack(system, mcp_url, base_url, model="google/gemini-3.8-flash")
    agent.respond("Approve Emma's request for the battery packs.")

What the SDK gives you, mapped onto the hand-written loop:
    Agent          the system prompt + the tools (+ model settings, guardrails, handoffs)
    Runner.run     the loop: call the model, run the tools, append, repeat; max_turns is the step cap
    MCP server     the 15 Ledgerline tools, discovered with tools/list (MCPServerStreamableHttp)
    Session        the conversation across messages (SQLiteSession; ":memory:" here, a file in production)
    Tracing        spans for agent runs, model calls, tool calls, handoffs, guardrails (kept here in .native)
"""
from __future__ import annotations

import asyncio
import os
import threading

from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, RunConfig, Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded
from agents.mcp import MCPServerStreamableHttp
from openai import AsyncOpenAI

from .ours import MAX_STEPS


class _Loop:
    """An asyncio loop on its own thread, so the async SDK can be driven from plain code."""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    def run(self, coro, timeout: float = 1800):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)


class _Spans:
    """A TracingProcessor that keeps the SDK's own spans in memory (no export to OpenAI's dashboard: no key)."""

    def __init__(self):
        self.by_group: dict[str, list] = {}
        self.groups: dict[str, str] = {}
        self._lock = threading.Lock()

    def on_trace_start(self, t):
        self.groups[t.trace_id] = (t.export() or {}).get("group_id") or ""

    def on_trace_end(self, t):
        pass

    def on_span_start(self, s):
        pass

    def on_span_end(self, s):
        d = s.export() or {}
        sd = d.get("span_data") or {}
        with self._lock:
            self.by_group.setdefault(self.groups.get(d.get("trace_id"), ""), []).append(
                {"type": sd.get("type"), "name": sd.get("name"), "start": d.get("started_at"), "end": d.get("ended_at"),
                 "error": d.get("error")})

    def shutdown(self):
        pass

    def force_flush(self):
        pass


SPANS = _Spans()
_installed: list = []


def _install():
    if not _installed:
        from agents import set_trace_processors, set_tracing_disabled
        set_tracing_disabled(False)
        set_trace_processors([SPANS])
        _installed.append(True)


class AgentsSDKStack:
    framework = "openai_agents"

    def __init__(self, system: str, mcp_url: str, base_url: str, model: str, max_steps: int = MAX_STEPS,
                 group: str = "ask-northbridge"):
        _install()
        self.max_steps, self.group = max_steps, group
        self.lt = _Loop()
        self.toolbox = MCPServerStreamableHttp(params={"url": mcp_url, "timeout": 120}, name="ledgerline-toolbox",
                                               cache_tools_list=True, client_session_timeout_seconds=120)
        llm = OpenAIChatCompletionsModel(model=model, openai_client=AsyncOpenAI(
            base_url=base_url, api_key=os.environ.get("OPENROUTER_API_KEY", "through-the-gateway"), max_retries=0,
            timeout=600))
        self.agent = Agent(name="Ask Northbridge", instructions=system, model=llm, mcp_servers=[self.toolbox],
                           model_settings=ModelSettings(temperature=0))
        self.session = SQLiteSession("conversation", ":memory:")
        self.lt.run(self.toolbox.connect())
        self.stops: list[str] = []

    async def _ask(self, text: str) -> str:
        try:
            result = await Runner.run(self.agent, text, session=self.session, max_turns=self.max_steps,
                                      run_config=RunConfig(workflow_name="Ask Northbridge", group_id=self.group))
            return str(result.final_output or "")
        except MaxTurnsExceeded:
            self.stops.append("max_steps")
            return f"(stopped after {self.max_steps} steps)"

    def respond(self, text: str) -> str:
        return self.lt.run(self._ask(text))

    @property
    def native(self) -> list:
        return SPANS.by_group.get(self.group, [])

    def close(self):
        try:
            self.lt.run(self.toolbox.cleanup(), timeout=30)
        except Exception:  # noqa: BLE001
            pass
