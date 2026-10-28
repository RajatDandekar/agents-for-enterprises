"""Probe the pinned SDKs on Modal: versions, the signatures we build on, and one tiny live call through OpenRouter each.
Writes logs/probe.txt. Not used by the deck."""
import importlib
import importlib.metadata as md
import inspect
import os
import pathlib
import subprocess
import sys
import traceback

OUT = pathlib.Path(__file__).parent / "logs" / "probe.txt"
lines = []


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


for pkg in ["openai-agents", "google-adk", "litellm", "langgraph", "langchain-openai", "langchain-mcp-adapters",
            "langchain-core", "fastmcp", "mcp", "openai", "httpx", "google-genai", "opentelemetry-sdk", "uvicorn",
            "starlette", "pydantic"]:
    try:
        p("VERSION", pkg, md.version(pkg))
    except Exception as e:
        p("VERSION", pkg, "missing", e)


def sig(path):
    mod, _, attr = path.rpartition(".")
    try:
        m = importlib.import_module(mod)
        o = getattr(m, attr)
        try:
            p("SIG", path, inspect.signature(o))
        except Exception:
            p("OBJ", path, type(o))
        return o
    except Exception as e:
        p("ERR", path, type(e).__name__, str(e)[:200])


for s in ["agents.Agent", "agents.Runner.run", "agents.Runner.run_sync", "agents.function_tool", "agents.handoff",
          "agents.SQLiteSession", "agents.OpenAIChatCompletionsModel", "agents.set_trace_processors",
          "agents.add_trace_processor", "agents.input_guardrail", "agents.output_guardrail",
          "agents.GuardrailFunctionOutput", "agents.ModelSettings", "agents.set_tracing_disabled",
          "agents.mcp.MCPServerStreamableHttp", "agents.mcp.MCPServerStreamableHttpParams",
          "agents.tracing.TracingProcessor", "agents.RunHooks", "agents.extensions.models.litellm_model.LitellmModel",
          "agents.tool_input_guardrail", "agents.ToolGuardrailFunctionOutput",
          "google.adk.agents.LlmAgent", "google.adk.runners.Runner", "google.adk.runners.InMemoryRunner",
          "google.adk.sessions.InMemorySessionService", "google.adk.models.lite_llm.LiteLlm",
          "google.adk.tools.mcp_tool.McpToolset", "google.adk.tools.mcp_tool.mcp_toolset.McpToolset",
          "google.adk.tools.mcp_tool.StreamableHTTPConnectionParams",
          "google.adk.tools.mcp_tool.mcp_session_manager.StreamableHTTPConnectionParams",
          "google.adk.agents.callback_context.CallbackContext",
          "langgraph.prebuilt.create_react_agent", "langchain.agents.create_agent",
          "langchain_mcp_adapters.client.MultiServerMCPClient", "langchain_openai.ChatOpenAI",
          "litellm.completion", "litellm.Router"]:
    sig(s)

try:
    import agents
    p("AGENTS ALL", sorted(x for x in dir(agents) if not x.startswith("_"))[:400])
    import agents.mcp as am
    p("AGENTS.MCP", sorted(x for x in dir(am) if not x.startswith("_")))
except Exception:
    p(traceback.format_exc())
try:
    import google.adk.tools.mcp_tool as mt
    p("ADK MCP", sorted(x for x in dir(mt) if not x.startswith("_")))
    import google.adk.agents as ga
    p("ADK AGENTS", sorted(x for x in dir(ga) if not x.startswith("_")))
    from google.adk.agents import LlmAgent
    p("LLMAGENT FIELDS", list(LlmAgent.model_fields)[:80])
except Exception:
    p(traceback.format_exc())

# ------------------------------------------------------------------ tiny live calls
key = os.environ.get("OPENROUTER_API_KEY")
p("OPENROUTER KEY SET", bool(key))
MODEL = "google/gemini-3.8-flash"
try:
    import asyncio
    from openai import AsyncOpenAI
    from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled
    set_tracing_disabled(True)

    @function_tool
    def check_stock(item_code: str) -> dict:
        """Stock of one item."""
        return {"ok": True, "item_code": item_code, "on_hand": 54000}

    m = OpenAIChatCompletionsModel(model=MODEL, openai_client=AsyncOpenAI(base_url="https://openrouter.ai/api/v1",
                                                                          api_key=key))
    a = Agent(name="Ask Rasoi", instructions="Answer briefly.", model=m, tools=[check_stock])
    r = asyncio.run(Runner.run(a, "How many GSK-SIL-05L do we have? Use the tool."))
    p("OAI AGENTS OK", repr(r.final_output)[:300])
    for it in r.new_items:
        p("  item", type(it).__name__)
    p("  usage", [getattr(x, "usage", None) for x in r.raw_responses][:3])
except Exception:
    p("OAI AGENTS FAIL", traceback.format_exc()[-3000:])

try:
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    def check_stock(item_code: str) -> dict:
        """Stock of one item."""
        return {"ok": True, "item_code": item_code, "on_hand": 54000}

    ag = LlmAgent(name="ask_rasoi", model=LiteLlm(model="openrouter/" + MODEL), instruction="Answer briefly.",
                  tools=[check_stock])
    run = InMemoryRunner(agent=ag, app_name="rasoi")

    async def go():
        s = await run.session_service.create_session(app_name="rasoi", user_id="KJOSHI")
        out = []
        async for ev in run.run_async(user_id="KJOSHI", session_id=s.id, new_message=types.Content(
                role="user", parts=[types.Part(text="How many GSK-SIL-05L do we have? Use the tool.")])):
            out.append(ev)
        return out
    evs = asyncio.run(go())
    for ev in evs:
        p("  ADK event", ev.author, [(pt.text[:80] if pt.text else None, pt.function_call and pt.function_call.name,
                                      pt.function_response and pt.function_response.name)
                                     for pt in (ev.content.parts if ev.content else [])],
          getattr(ev, "usage_metadata", None))
    p("ADK OK")
except Exception:
    p("ADK FAIL", traceback.format_exc()[-3000:])

OUT.write_text("\n".join(lines))
