"""Stack (a): our own harness. The whole agent loop, by hand, in one screen of code.

    agent = OurHarness(system, mcp_url, base_url, model="google/gemini-3.8-flash")
    agent.respond("How many city e-bike battery packs do we have?")

The loop: send the conversation and the tool list to the model; if it asks for tools, run each one over MCP and add
the result to the conversation; repeat until it answers in words or hits the step cap. Lecture 5 builds this up part
by part (and adds the parts a framework does not give you); here it is bare, so the three stacks are like for like.
"""
from __future__ import annotations

import json

from ....mcp_server import MCPClient, MCPClientTools

MAX_STEPS = 12   # model calls per message from the person, the same cap for every stack


class OurHarness:
    framework = "ours"

    def __init__(self, system: str, mcp_url: str, base_url: str, model: str, max_steps: int = MAX_STEPS):
        from openai import OpenAI
        self.model, self.max_steps = model, max_steps
        self.llm = OpenAI(base_url=base_url, api_key="through-the-gateway", max_retries=0, timeout=600)
        self.mcp = MCPClient(mcp_url)                    # the plug: tools are discovered, not hard-coded
        self.tools = MCPClientTools(self.mcp)
        self.messages = [{"role": "system", "content": system}]
        self.stops: list[str] = []

    def respond(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        for _ in range(self.max_steps):
            r = self.llm.chat.completions.create(model=self.model, messages=self.messages,
                                                 tools=self.tools.schemas(), temperature=0)
            msg = r.choices[0].message
            calls = msg.tool_calls or []
            self.messages.append({"role": "assistant", "content": msg.content,
                                  **({"tool_calls": [{"id": c.id, "type": "function",
                                                      "function": {"name": c.function.name,
                                                                   "arguments": c.function.arguments}}
                                                     for c in calls]} if calls else {})})
            if not calls:
                return msg.content or ""
            for c in calls:
                try:
                    args = json.loads(c.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                out = self.tools.call(c.function.name, args)       # over MCP, as the signed-in person
                self.messages.append({"role": "tool", "tool_call_id": c.id, "content": out})
        self.stops.append("max_steps")
        return f"(stopped after {self.max_steps} steps)"

    def close(self):
        self.tools.close()
