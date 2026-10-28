"""Second probe: the source of the few SDK entry points the ports depend on. Writes logs/probe2.txt."""
import inspect
import pathlib

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)
lines = []


def src(obj, n=80):
    try:
        s = inspect.getsource(obj)
        lines.append(f"===== {getattr(obj, '__qualname__', obj)}\n" + "\n".join(s.splitlines()[:n]))
    except Exception as e:
        lines.append(f"===== {obj}: {e}")


def sig(obj):
    try:
        lines.append(f"SIG {getattr(obj, '__qualname__', obj)} {inspect.signature(obj)}")
    except Exception as e:
        lines.append(f"SIG {obj}: {e}")


from google.adk.models.lite_llm import LiteLlm  # noqa: E402
src(LiteLlm.__init__, 60)
from google.adk.agents.run_config import RunConfig  # noqa: E402
lines.append("ADK RunConfig fields " + str(list(RunConfig.model_fields)))
from google.adk.runners import Runner  # noqa: E402
sig(Runner.run_async)
from google.adk.events import Event  # noqa: E402
lines.append("ADK Event fields " + str(list(Event.model_fields)))
sig(Event.is_final_response)
import agents  # noqa: E402
sig(agents.Runner.run)
lines.append("agents RunConfig " + str(inspect.signature(agents.RunConfig)))
from agents.tracing import TracingProcessor  # noqa: E402
src(TracingProcessor, 60)
from agents.mcp import MCPServerStreamableHttpParams  # noqa: E402
lines.append("MCPServerStreamableHttpParams " + str(MCPServerStreamableHttpParams.__annotations__))
from langgraph.prebuilt import create_react_agent  # noqa: E402
sig(create_react_agent)
import fastmcp  # noqa: E402
sig(fastmcp.FastMCP.http_app)
from google.adk.tools.mcp_tool.mcp_tool import McpTool  # noqa: E402
src(McpTool._run_async_impl if hasattr(McpTool, "_run_async_impl") else McpTool.run_async, 60)
from google.adk.models import lite_llm  # noqa: E402
src(lite_llm.LiteLlm.generate_content_async, 120)
(OUT / "probe2.txt").write_text("\n".join(lines))
print("\n".join(lines)[:200])
