"""A free tool loop: a model, a set of tools, and a loop until the model stops calling tools.

Used with the intent tools as the Lecture 3 agent, and as the baseline the Lecture 4 control graph beats.
Any object with .schemas() -> list[dict] and .call(name, args) -> dict can be the tool set: IntentTools,
RawServiceTools, GenericServiceTool, or MCP tools discovered from a server (ledgerline.mcp_server.MCPClientTools).
"""
from __future__ import annotations

import json

from ..erp.engine import ERP, ServiceTimeout
from ..llm import LLM
from .tools import IntentTools

SYSTEM = """You are the purchasing assistant at Northbridge Cycles, Manchester, working inside Ledgerline ERP for {name} ({user_id}).
Today is Monday 26 October 2026. Use the tools to do what {first} asks. Preview every order and get {first}'s
confirmation before committing it. If a tool returns ok=false, read its next_step and follow it.
Report the status the receipt gives you, in plain words; never call an order placed unless it is RELEASED."""

# What a marketplace host (a generic MCP client) puts in front of the same tools: nothing about Ledgerline, the user or the date.
GENERIC_SYSTEM = """You are a helpful assistant. You can use the tools from the connected servers to help the user."""


class ToolLoopAgent:
    def __init__(self, erp: ERP, user: str = "ECLARKE", llm: LLM | None = None, tools=None, max_steps: int = 20,
                 system: str = SYSTEM):
        self.erp, self.user = erp, user
        self.llm = llm or LLM(cassette="toolloop")
        self.tools = tools or IntentTools(erp.session(user))  # acts as the user, with the user's permissions
        self.max_steps = max_steps
        u = erp.user(user)
        self.messages = [{"role": "system", "content": system.format(name=u["name"], user_id=user,
                                                                     first=u["name"].split()[0])}]
        self.trace: list[dict] = []  # one entry per tool call: the step, the call, and what came back
        self._schemas = None

    def schemas(self) -> list[dict]:
        if self._schemas is None:
            self._schemas = self.tools.schemas()
        return self._schemas

    def respond(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        for step in range(self.max_steps):
            r = self.llm.chat(self.messages, tools=self.schemas())
            self.messages.append(r.message())
            if not r.tool_calls:
                return r.content or ""
            for tc in r.tool_calls:
                try:
                    out = self.tools.call(tc.name, tc.arguments)
                except ServiceTimeout as e:
                    out = {"ok": False, "error": f"TIMEOUT: {e}"}
                except Exception as e:  # a broken tool must not kill the conversation
                    out = {"ok": False, "error": f"{type(e).__name__}: {e}"}
                content = out if isinstance(out, str) else json.dumps(out, default=str)
                self.trace.append({"step": step, "tool": tc.name, "args": tc.arguments, "result": content[:4000]})
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
        return "(stopped after %d steps)" % self.max_steps
