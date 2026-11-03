"""Serve the toolbox over MCP: every tool folder becomes one MCP tool, with tool.json as its definition.

    from ledgerline.toolbox.mcp import build_toolbox_server
    from ledgerline.mcp_server import MCPClient, MCPClientTools
    server = build_toolbox_server(erp, user="ECLARKE")       # bound to Emma's own Ledgerline session
    tools = MCPClientTools(MCPClient(server))                # what the orchestrator LLM sees: discovered, not hard-coded

    python -m ledgerline.toolbox.mcp --user ECLARKE                             # stdio, for Claude Desktop / Claude Code
    python -m ledgerline.toolbox.mcp --user ECLARKE --tools check_stock,find_item   # only these tools
    python -m ledgerline.toolbox.mcp --user ECLARKE --all                       # the 15 + the extras (supplier_certificates)
    python -m ledgerline.toolbox.mcp --user ECLARKE --transport http --port 8765 # streamable HTTP at /mcp
    python -m ledgerline.toolbox.mcp --log calls.jsonl                          # also log every call and its Ledgerline calls

How tool.json maps onto an MCP tool definition (Lecture 4, section 5):
    name            -> name                 title        -> title (and annotations.title, for older clients)
    description     -> description          input_schema -> inputSchema
    output_schema   -> outputSchema         annotations  -> annotations (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
    version, category, writes, services, policy -> _meta (namespaced "ledgerline/...")
and every result carries content (the JSON as text, what most hosts show the model), structuredContent (the same
dict, checked against outputSchema by the client) and isError (true when the tool returned ok=false).
"""
from __future__ import annotations

import argparse
import json
import time

from ..erp.engine import ERP
from . import spec_of, Toolbox

META_NS = "ledgerline/"


def mcp_definition(spec: dict) -> dict:
    """tool.json -> the MCP tool definition (2025-06-18 and later field names), as a plain dict."""
    ann = {"title": spec["title"], **(spec.get("annotations") or {"readOnlyHint": not spec.get("writes")})}
    out = {"name": spec["name"], "title": spec["title"], "description": spec["description"],
           "inputSchema": spec["input_schema"], "annotations": ann,
           "_meta": {META_NS + "version": spec.get("version"), META_NS + "category": spec.get("category"),
                     META_NS + "writes": bool(spec.get("writes")), META_NS + "services": spec.get("services", []),
                     META_NS + "policy": spec.get("policy"),
                     META_NS + "release_notes": spec.get("release_notes")}}
    if spec.get("output_schema"):
        out["outputSchema"] = spec["output_schema"]
    return out


def build_toolbox_server(erp: ERP | None = None, user: str = "ECLARKE", names: list[str] | None = None,
                         name: str = "ledgerline-toolbox", log: str | None = None):
    from fastmcp import FastMCP
    try:
        from fastmcp.tools import Tool, ToolResult          # fastmcp 3 and 4
    except ImportError:
        from fastmcp.tools.tool import Tool, ToolResult     # fastmcp 2
    from mcp.types import TextContent, ToolAnnotations

    tb = Toolbox(erp or ERP(), user, names)
    mcp = FastMCP(name, instructions=f"Northbridge Cycles' Ledgerline ERP, as {user}. One tool per business activity.")

    def _log(entry: dict):
        if log:
            with open(log, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")

    class FolderTool(Tool):
        """A tool whose definition comes from tool.json and whose body is tool.py's run()."""

        async def run(self, arguments: dict) -> ToolResult:
            n0 = len(tb.erp.calls)
            t0 = time.perf_counter()
            out = tb.call(self.name, arguments)
            text = json.dumps(out, default=str)
            if log:
                _log({"tool": self.name, "arguments": arguments, "result": out,
                      "ms": round((time.perf_counter() - t0) * 1000, 2), "ledgerline_calls": tb.erp.live_run(n0)})
            failed = isinstance(out, dict) and out.get("ok") is False
            structured = json.loads(text) if isinstance(out, dict) else None
            try:
                return ToolResult(content=[TextContent(type="text", text=text)], structured_content=structured,
                                  is_error=failed)
            except TypeError:  # fastmcp 2: no is_error on ToolResult
                return ToolResult(content=[TextContent(type="text", text=text)], structured_content=structured)

    for n in tb.names:
        spec = spec_of(n).spec
        d = mcp_definition(spec)
        kw = dict(name=n, title=d["title"], description=d["description"], parameters=d["inputSchema"],
                  annotations=ToolAnnotations(**d["annotations"]), meta=d["_meta"])
        if d.get("outputSchema"):
            kw["output_schema"] = d["outputSchema"]
        try:
            tool = FolderTool(**kw)
        except (TypeError, ValueError):  # an older fastmcp without title / meta / output_schema
            tool = FolderTool(name=n, description=d["description"], parameters=d["inputSchema"],
                              annotations=ToolAnnotations(**d["annotations"]))
        mcp.add_tool(tool)
    mcp.toolbox = tb  # the same Toolbox, for pages that want the audit trail or the user
    return mcp


def main():
    from . import ALL

    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="ECLARKE")
    ap.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--tools", default="", help="comma-separated tool names (default: the 15 default tools)")
    ap.add_argument("--all", action="store_true", help="every tool folder, extras included")
    ap.add_argument("--log", default="", help="append every tool call, with its Ledgerline calls, to this JSONL file")
    a = ap.parse_args()
    names = ALL if a.all else ([t.strip() for t in a.tools.split(",") if t.strip()] or None)
    server = build_toolbox_server(ERP(), a.user, names=names, log=a.log or None)
    if a.transport == "http":
        server.run(transport="http", host="127.0.0.1", port=a.port)
    else:
        server.run()


if __name__ == "__main__":
    main()
