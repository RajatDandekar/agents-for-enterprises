"""Ask Rasoi on Google's Agent Development Kit (google-adk 2.11.0), the model reached through LiteLLM.

    from bahi.course.frameworks.adk import ADKPort
    a = ADKPort(Toolbox(erp, "KJOSHI"), meter, "adk-T01-KJOSHI")
    a.respond("Reorder 20,000 of the 5-litre gaskets ...")

The map onto what you built by hand in Lecture 5:
    LlmAgent        = the system prompt (instruction) + the tool registry (tools) + the model
    Runner          = the loop; it yields Events (a model reply, a function call, a function response)
    McpToolset      = Lecture 4's toolbox over MCP
    SessionService  = the history (InMemorySessionService here; a database one in production)
    RunConfig       = settings per run, e.g. max_llm_calls, the step cap
    Callbacks       = before/after model and tool hooks: where a harness part (a guard, a check) goes
In production you would write LiteLlm(model="openrouter/google/gemini-3.8-flash"); here the model string is
"openai/..." with api_base pointing at our meter, which forwards to OpenRouter and records the reply.
"""
from __future__ import annotations

import json
import os

from .base import Port

# --- port ---------------------------------------------------------------- (lines counted on the plate)
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.genai import types


def make_agent(system: str, mcp_url: str, base_url: str, model: str):
    llm = LiteLlm(model="openai/" + model, api_base=base_url,
                  api_key=os.environ.get("OPENROUTER_API_KEY", "replay"))
    toolbox = McpToolset(connection_params=StreamableHTTPConnectionParams(url=mcp_url, timeout=60))
    agent = LlmAgent(name="ask_rasoi", model=llm, instruction=lambda ctx: system, tools=[toolbox],
                     generate_content_config=types.GenerateContentConfig(temperature=0))
    return Runner(app_name="rasoi", agent=agent, session_service=InMemorySessionService())


async def ask(runner, user: str, session_id: str, text: str, max_steps: int, events: list) -> str:
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    reply = ""
    try:
        async for ev in runner.run_async(user_id=user, session_id=session_id, new_message=msg,
                                         run_config=RunConfig(max_llm_calls=max_steps)):
            events.append(ev)
            if ev.is_final_response() and ev.content and ev.content.parts:
                reply = "".join(p.text or "" for p in ev.content.parts if not getattr(p, "thought", False))
    except Exception as e:  # the step cap raises LlmCallsLimitExceededError
        if "LlmCallsLimit" in type(e).__name__ or "max_llm_calls" in str(e):
            return f"(stopped after {max_steps} steps)"
        raise
    return reply
# --- end port ------------------------------------------------------------


def event_row(ev) -> dict:
    """ADK's own unit of trace: one Event."""
    parts = ev.content.parts if ev.content and ev.content.parts else []
    row = {"author": ev.author, "final": ev.is_final_response()}
    for p in parts:
        if p.text and not getattr(p, "thought", False):
            row["text"] = p.text[:600]
        if p.function_call:
            row.setdefault("calls", []).append({"name": p.function_call.name, "args": p.function_call.args})
        if p.function_response:
            resp = p.function_response.response
            row.setdefault("responses", []).append({"name": p.function_response.name,
                                                    "response": json.dumps(resp, default=str)[:400]})
    u = getattr(ev, "usage_metadata", None)
    if u:
        row["usage"] = {"in": u.prompt_token_count, "out": u.candidates_token_count}
    return row


class ADKPort(Port):
    framework = "adk"

    def __init__(self, tb, meter, tag, **kw):
        super().__init__(tb, meter, tag, **kw)
        self.runner = make_agent(self.system, self.srv.url, self.base_url, self.model)
        self.session = self.lt.run(self.runner.session_service.create_session(app_name="rasoi", user_id=tb.user))

    async def _respond(self, text: str) -> str:
        events: list = []
        reply = await ask(self.runner, self.tb.user, self.session.id, text, self.max_steps, events)
        if reply.startswith("(stopped"):
            self.stops.append("max_steps")
        self.native.append({"turn": self.turn, "events": [event_row(e) for e in events]})
        return reply
