"""Serve the toolbox over MCP: every tool folder becomes one MCP tool, with tool.json as its schema.

    from bahi.toolbox.mcp import build_toolbox_server
    from bahi.mcp_server import MCPClient, MCPClientTools
    server = build_toolbox_server(erp, user="KJOSHI")       # bound to Kavita's own Bahi session
    tools = MCPClientTools(MCPClient(server))                # what the orchestrator LLM sees: discovered, not hard-coded

    python -m bahi.toolbox.mcp --user KJOSHI                             # stdio, for Claude Desktop
    python -m bahi.toolbox.mcp --user KJOSHI --transport http --port 8765 # streamable HTTP at /mcp
"""
from __future__ import annotations

import argparse
import json

from ..erp.engine import ERP
from . import SPECS, Toolbox


def build_toolbox_server(erp: ERP | None = None, user: str = "KJOSHI", names: list[str] | None = None,
                         name: str = "bahi-toolbox"):
    from fastmcp import FastMCP
    try:
        from fastmcp.tools import Tool, ToolResult          # fastmcp 3 and 4
    except ImportError:
        from fastmcp.tools.tool import Tool, ToolResult     # fastmcp 2
    from mcp.types import TextContent, ToolAnnotations

    tb = Toolbox(erp or ERP(), user, names)
    mcp = FastMCP(name, instructions=f"Rasoi Steel Works' Bahi ERP, as {user}. One tool per business activity.")

    class FolderTool(Tool):
        """A tool whose schema comes from tool.json and whose body is tool.py's run()."""

        async def run(self, arguments: dict) -> ToolResult:
            out = tb.call(self.name, arguments)
            return ToolResult(content=[TextContent(type="text", text=json.dumps(out, default=str))])

    for n in tb.names:
        spec = SPECS[n].spec
        mcp.add_tool(FolderTool(name=n, description=spec["description"], parameters=spec["input_schema"],
                                annotations=ToolAnnotations(readOnlyHint=not spec.get("writes"), title=spec["title"])))
    mcp.toolbox = tb  # the same Toolbox, for pages that want the audit trail or the user
    return mcp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="KJOSHI")
    ap.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    server = build_toolbox_server(ERP(), a.user)
    if a.transport == "http":
        server.run(transport="http", host="127.0.0.1", port=a.port)
    else:
        server.run()


if __name__ == "__main__":
    main()
