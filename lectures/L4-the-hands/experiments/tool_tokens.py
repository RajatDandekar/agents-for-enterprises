"""Lecture 4: what the tool definitions alone cost, in the model's own tokens (v2 L3's method, on the v3 toolbox).

Same one-line request sent with and without each tool set; the difference in prompt tokens, as Gemini counts them, is
what the definitions cost on EVERY call. Sets: Bahi's 41 raw services; the 15 toolbox tools; the same 15 discovered
over MCP; each toolbox tool alone. Cassette L4v3_tooltokens. Writes logs/tool_tokens.json
"""
import json
import pathlib

from bahi.agent.tools import RawServiceTools
from bahi.erp.engine import ERP
from bahi.llm import LLM
from bahi.mcp_server import MCPClient, MCPClientTools
from bahi.toolbox import SPECS, Toolbox
from bahi.toolbox.mcp import build_toolbox_server

erp = ERP()
tb = Toolbox(erp, "KJOSHI")
mcp = MCPClient(build_toolbox_server(erp, "KJOSHI"))
sets = {"raw_41_services": RawServiceTools(erp.session("KJOSHI")).schemas(), "toolbox_15": tb.schemas(),
        "toolbox_15_over_mcp": MCPClientTools(mcp).schemas()}
mcp.close()
msgs = [{"role": "user", "content": "Reply with the single word OK."}]
out = {"method": "prompt tokens with the tools minus prompt tokens without them, same request", "models": {}}
for model in ["gemini:gemini-3.8-flash", "gemini:gemini-3.5-flash-lite"]:
    llm = LLM(model, cassette="L4v3_tooltokens")
    base = llm.chat(msgs).tokens_in
    row = {"baseline_prompt_tokens": base}
    for name, sch in sets.items():
        r = llm.chat(msgs, tools=sch)
        row[name] = {"tools": len(sch), "chars": len(json.dumps(sch)), "tokens": r.tokens_in - base}
    row["per_tool"] = {n: llm.chat(msgs, tools=[SPECS[n].schema()]).tokens_in - base for n in tb.names}
    out["models"][model] = row
    print(model, json.dumps({k: v for k, v in row.items() if k != "per_tool"}), row["per_tool"])
(pathlib.Path(__file__).resolve().parent / "logs" / "tool_tokens.json").write_text(json.dumps(out, indent=1))
