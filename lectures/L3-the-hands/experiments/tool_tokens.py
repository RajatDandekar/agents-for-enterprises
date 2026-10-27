"""Lecture 3: what the tool definitions alone cost, in the model's own tokens.

For each tool set we send the same one-line request twice, with and without the tools, and take the difference in
prompt tokens as Gemini counts them. Cassette L3_tooltokens. Writes logs/tool_tokens.json
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "bahi"))

from bahi.agent.tools import ALL, CORE, TOOLS, GenericServiceTool, IntentTools, RawServiceTools  # noqa: E402
from bahi.erp.engine import ERP  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.mcp_server import MCPClient, MCPClientTools, build_bahi_server  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--models", default="gemini:gemini-3.8-flash,gemini:gemini-3.5-flash-lite")
a = ap.parse_args()
erp = ERP()
s = erp.session("KJOSHI")
mcp = MCPClient(build_bahi_server(erp, "KJOSHI", CORE))
sets = {"raw_38_services": RawServiceTools(s).schemas(), "generic_call_service": GenericServiceTool(s).schemas(),
        "intent_8": IntentTools(s, CORE).schemas(), "intent_11": IntentTools(s, ALL).schemas(),
        "intent_8_over_mcp": MCPClientTools(mcp).schemas()}
mcp.close()
msgs = [{"role": "user", "content": "Reply with the single word OK."}]
out = {"method": "prompt tokens with the tools minus prompt tokens without them, same request", "models": {}}
for model in a.models.split(","):
    llm = LLM(model, cassette="L3_tooltokens")
    base = llm.chat(msgs).tokens_in
    row = {"baseline_prompt_tokens": base}
    for name, sch in sets.items():
        r = llm.chat(msgs, tools=sch)
        row[name] = {"tools": len(sch), "chars": len(json.dumps(sch)), "tokens": r.tokens_in - base}
    # one tool at a time, for the intent set (the per-tool bar on the plate)
    row["per_intent_tool"] = {}
    for n in ALL:
        r = llm.chat(msgs, tools=[TOOLS[n].schema()])
        row["per_intent_tool"][n] = r.tokens_in - base
    out["models"][model] = row
    print(model, json.dumps({k: v for k, v in row.items() if k != "per_intent_tool"}))
(HERE / "logs" / "tool_tokens.json").write_text(json.dumps(out, indent=1))
