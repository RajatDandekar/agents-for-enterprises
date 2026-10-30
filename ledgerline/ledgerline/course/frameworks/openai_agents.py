"""Ask Northbridge on the OpenAI Agents SDK (openai-agents 0.20.0), with the model reached through OpenRouter.

    from ledgerline.course.frameworks.openai_agents import AgentsSDKPort
    a = AgentsSDKPort(Toolbox(erp, "ECLARKE"), meter, "oai-T01-ECLARKE")
    a.respond("Reorder 20,000 of the city e-bike battery packs ...")

The map onto what you built by hand in Lecture 5:
    Agent          = the system prompt + the tool registry (+ model, guardrails, handoffs)
    Runner.run     = the loop (call model, run tools, append results, repeat), with max_turns as the step cap
    MCP server     = Lecture 4's toolbox, discovered with tools/list
    Session        = the history across messages (SQLiteSession: a file, so it survives to the next day)
    Tracing        = one span per agent run, model call, tool call, handoff and guardrail
"""
from __future__ import annotations

import json
import os
import threading

from .base import Port

# --- port ---------------------------------------------------------------- (lines counted on the plate)
from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, RunConfig, Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded
from agents.mcp import MCPServerStreamableHttp
from openai import AsyncOpenAI


def make_agent(system: str, mcp_url: str, base_url: str, model: str):
    toolbox = MCPServerStreamableHttp(params={"url": mcp_url, "timeout": 60}, name="ledgerline-toolbox",
                                      cache_tools_list=True, client_session_timeout_seconds=60)
    llm = OpenAIChatCompletionsModel(model=model, openai_client=AsyncOpenAI(
        base_url=base_url, api_key=os.environ.get("OPENROUTER_API_KEY", "replay")))
    agent = Agent(name="Ask Northbridge", instructions=system, model=llm, mcp_servers=[toolbox],
                  model_settings=ModelSettings(temperature=0))
    return agent, toolbox


async def ask(agent, session, text: str, max_turns: int, group: str) -> str:
    try:
        result = await Runner.run(agent, text, session=session, max_turns=max_turns,
                                  run_config=RunConfig(workflow_name="Ask Northbridge", group_id=group))
        return str(result.final_output or "")
    except MaxTurnsExceeded:
        return f"(stopped after {max_turns} steps)"
# --- end port ------------------------------------------------------------


# ----------------------------------------------------------------------------- tracing, kept in memory
class SpanRecorder:
    """A TracingProcessor: instead of exporting to OpenAI's dashboard, keep every span here (we have no OpenAI
    key; Langfuse, Phoenix or any OpenTelemetry backend would plug in the same way)."""

    def __init__(self):
        self.groups: dict[str, str] = {}     # trace_id -> group_id (our run tag)
        self.spans: dict[str, list] = {}     # group_id -> [span]
        self._lock = threading.Lock()

    def on_trace_start(self, trace):
        d = trace.export() or {}
        with self._lock:
            self.groups[trace.trace_id] = d.get("group_id") or ""

    def on_trace_end(self, trace):
        pass

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        d = span.export() or {}
        sd = d.get("span_data") or {}
        keep = {"type": sd.get("type"), "name": sd.get("name"), "id": d.get("id"), "parent": d.get("parent_id"),
                "start": d.get("started_at"), "end": d.get("ended_at"), "error": d.get("error")}
        if sd.get("type") == "function":
            keep["input"], keep["output"] = (sd.get("input") or "")[:400], str(sd.get("output") or "")[:400]
        if sd.get("type") == "generation":
            keep["usage"] = sd.get("usage")
            out = sd.get("output") or []
            keep["output"] = json.dumps(out, default=str)[:600]
        if sd.get("type") in ("handoff",):
            keep["from"], keep["to"] = sd.get("from_agent"), sd.get("to_agent")
        if sd.get("type") == "guardrail":
            keep["triggered"] = sd.get("triggered")
        if sd.get("type") == "agent":
            keep["tools"] = sd.get("tools")
            keep["handoffs"] = sd.get("handoffs")
        if sd.get("type") == "mcp_tools":
            keep["server"], keep["result"] = sd.get("server"), sd.get("result")
        with self._lock:
            self.spans.setdefault(self.groups.get(d.get("trace_id"), ""), []).append(keep)

    def shutdown(self):
        pass

    def force_flush(self):
        pass


RECORDER = SpanRecorder()
_installed = []


def install_recorder():
    if not _installed:
        from agents import set_trace_processors, set_tracing_disabled
        set_tracing_disabled(False)
        set_trace_processors([RECORDER])
        _installed.append(True)
    return RECORDER


# ----------------------------------------------------------------------------- the port, for run_task
class AgentsSDKPort(Port):
    framework = "openai_agents"

    def __init__(self, tb, meter, tag, session_db: str | None = None, **kw):
        super().__init__(tb, meter, tag, **kw)
        install_recorder()
        self.session_db = session_db or ":memory:"
        self.session = SQLiteSession(f"{tb.user}-thread", self.session_db)
        self.agent, self.toolbox = self._build()
        self.lt.run(self.toolbox.connect())

    def _build(self):
        return make_agent(self.system, self.srv.url, self.base_url, self.model)

    async def _respond(self, text: str) -> str:
        n0 = len(RECORDER.spans.get(self.tag, []))
        reply = await ask(self.agent, self.session, text, self.max_steps, self.tag)
        if reply.startswith("(stopped"):
            self.stops.append("max_steps")
        self.native.append({"turn": self.turn, "spans": RECORDER.spans.get(self.tag, [])[n0:]})
        return reply

    # state across days: the session is a SQLite file; a new object on day 2 reads the same history
    def save(self, path: str):
        with open(path, "w") as f:
            json.dump({"tag": self.tag, "db": self.session_db, "turn": self.turn, "trace": self.trace,
                       "native": self.native, "stops": self.stops}, f, default=str)

    @classmethod
    def load(cls, path, tb, llm, max_steps=12):
        st = json.load(open(path))
        a = cls(tb, llm.meter, st["tag"], session_db=st["db"], max_steps=max_steps)
        a.turn, a.trace, a.native, a.stops = st["turn"], st["trace"], st["native"], st["stops"]
        return a

    def history(self) -> list:
        return self.lt.run(self.session.get_items())
