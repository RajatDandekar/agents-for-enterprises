"""What every Lecture 8 port shares: the Ask Rasoi instructions, an event-loop thread, and the uniform trace.

A port is an object with respond(text) -> str, like every agent in bahi.course.l5, so the same twelve tasks
(bahi.course.l5.tasks.run_task) run on it unchanged. Tool calls are read from the MCP server's side (what arrived
over the plug), so the trace is counted the same way for every framework. The framework's own trace (spans,
events, graph steps) is kept next to it in .native.
"""
from __future__ import annotations

import asyncio
import threading

from ..l5.harness import ROLES, SYSTEM_FULL, profile
from .mcp_http import serve_toolbox

MODEL = "google/gemini-3.8-flash"      # the same model, through OpenRouter, for every framework
MAX_STEPS = 12                          # the same step cap as our harness: model calls per message
_SERVERS: dict = {}
ON_CREATE: list = []                    # callbacks run on every new port (experiments use it to find them)


def instructions(tb) -> str:
    """Ask Rasoi's system prompt from Lecture 5, for the person this toolbox acts as."""
    u = tb.erp.user(tb.user)
    return SYSTEM_FULL.format(name=u["name"], user=tb.user, role=ROLES.get(tb.user, "staff"),
                              first=u["name"].split()[0], profile=profile(tb))


def toolbox_server(erp, user, toolbox=None):
    """One MCP server per Bahi and person (reused across days of the same task). toolbox: a module's FolderToolbox."""
    key = (id(erp), user)
    if key not in _SERVERS:
        _SERVERS[key] = serve_toolbox(erp, user, toolbox=toolbox)
    return _SERVERS[key]


class LoopThread:
    """An asyncio loop on its own thread, so async SDKs can be driven from plain code (and from Jupyter)."""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.t = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.t.start()

    def run(self, coro, timeout: float = 900):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)


class Port:
    framework = "port"

    def __init__(self, tb, meter, tag: str, model: str = MODEL, max_steps: int = MAX_STEPS):
        self.tb, self.meter, self.tag, self.model, self.max_steps = tb, meter, tag, model, max_steps
        from ...toolbox import Toolbox
        self.srv = toolbox_server(tb.erp, tb.user, None if isinstance(tb, Toolbox) else tb)
        self.llm = meter.view(tag)            # run_task reads .llm.log for tokens and seconds
        self.base_url = meter.base_url(tag)
        self.system = instructions(tb)
        self.trace: list[dict] = []           # uniform: one row per tool call that reached the MCP server
        self.native: list[dict] = []          # the framework's own view of each message
        self.stops: list[str] = []
        self.turn = 0
        self.lt = LoopThread()
        for f in ON_CREATE:
            f(self)

    def respond(self, text: str) -> str:
        self.turn += 1
        i = len(self.srv.calls)
        try:
            reply = self.lt.run(self._respond(text))
        finally:
            for c in self.srv.calls[i:]:
                self.trace.append({"turn": self.turn, "kind": "tool", "name": c["name"], "args": c["args"],
                                   "ok": c["ok"]})
        return reply

    async def _respond(self, text: str) -> str:  # each port fills this in
        raise NotImplementedError
