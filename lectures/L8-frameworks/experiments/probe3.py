"""Third probe: the Agents SDK tool-guardrail and FunctionTool API, and the MCP static tool filter. Writes logs/probe3.txt."""
import inspect, pathlib
import agents.tool_guardrails as tg

OUT = pathlib.Path(__file__).parent / "logs"; OUT.mkdir(exist_ok=True)
L = []
L.append(inspect.getsource(tg)[:9000])
from agents import FunctionTool
L.append("FunctionTool fields " + str(list(FunctionTool.__dataclass_fields__)))
from agents.mcp import create_static_tool_filter
L.append("static filter " + str(inspect.signature(create_static_tool_filter)))
from agents.mcp import MCPServerStreamableHttp
L.append("call_tool " + str(inspect.signature(MCPServerStreamableHttp.call_tool)))
import agents.exceptions as ex
L.append("exceptions " + str([x for x in dir(ex) if not x.startswith('_')]))
from agents import RunResult
L.append("RunResult fields " + str(list(getattr(RunResult, '__dataclass_fields__', {}))))
(OUT / "probe3.txt").write_text("\n\n".join(L))
