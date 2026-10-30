"""The Northbridge toolbox (Lecture 4) served over MCP on streamable HTTP, for every framework in Lecture 8.

    from ledgerline.course.frameworks.mcp_http import serve_toolbox, MCPToolbox
    srv = serve_toolbox(erp, "ECLARKE")       # http://127.0.0.1:<port>/mcp, bound to Emma's own Ledgerline session
    srv.url; srv.calls                       # what came over the plug: one row per tools/call
    tb = MCPToolbox(srv)                     # the same tools, for our own L5 Harness (it wants .call / .schemas)
    srv.stop()

One server per person per task, so parallel tasks never share a Ledgerline. Every framework connects to the URL the way
it would connect to any remote MCP server: OpenAI Agents SDK (MCPServerStreamableHttp), Google ADK (McpToolset),
LangGraph (langchain-mcp-adapters) and our harness (ledgerline.mcp_server.MCPClient).
"""
from __future__ import annotations

import json
import socket
import threading
import time

from ...toolbox.mcp import build_toolbox_server


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def build_folder_server(tb, name: str = "module-toolbox"):
    """An MCP server for any toolbox with names / schemas() / call(): e.g. your module's FolderToolbox (A4, A8)."""
    from fastmcp import FastMCP
    try:
        from fastmcp.tools import Tool, ToolResult
    except ImportError:
        from fastmcp.tools.tool import Tool, ToolResult
    from mcp.types import TextContent

    mcp = FastMCP(name, instructions=f"A module toolbox, as {tb.user}.")

    class FolderTool(Tool):
        async def run(self, arguments: dict) -> ToolResult:
            out = mcp.toolbox.call(self.name, arguments)
            return ToolResult(content=[TextContent(type="text", text=json.dumps(out, default=str))])

    for sc in tb.schemas():
        f = sc["function"]
        mcp.add_tool(FolderTool(name=f["name"], description=f.get("description", ""), parameters=f["parameters"]))
    mcp.toolbox = tb
    return mcp


class ToolboxServer:
    def __init__(self, erp, user: str, names: list[str] | None = None, toolbox=None):
        import uvicorn
        self.erp, self.user = erp, user
        self.mcp = build_folder_server(toolbox) if toolbox is not None else build_toolbox_server(erp, user, names)
        self.calls: list[dict] = []
        inner = self.mcp.toolbox.call

        def counted(name, args=None):           # the toolbox the MCP tools run: note every call that arrives
            t0 = time.perf_counter()
            out = inner(name, args)
            self.calls.append({"name": name, "args": args, "ok": bool(out.get("ok")),
                               "ms": round((time.perf_counter() - t0) * 1000, 1)})
            return out
        self.mcp.toolbox.call = counted
        self.port = _free_port()
        app = self.mcp.http_app(path="/mcp")
        self._server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning",
                                                     lifespan="on"))
        self._t = threading.Thread(target=self._server.run, daemon=True)
        self._t.start()
        for _ in range(200):
            if self._server.started:
                break
            time.sleep(0.05)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/mcp"

    def stop(self):
        self._server.should_exit = True
        self._t.join(timeout=5)


def serve_toolbox(erp, user: str = "ECLARKE", names: list[str] | None = None, toolbox=None) -> ToolboxServer:
    """toolbox=None serves the 15 Ledgerline tools; pass your own FolderToolbox to serve your module's tools instead."""
    return ToolboxServer(erp, user, names, toolbox)


class MCPToolbox:
    """Looks like ledgerline.toolbox.Toolbox (erp, user, names, schemas(), call()) but every call goes over MCP."""

    def __init__(self, srv: ToolboxServer):
        from ...mcp_server import MCPClient, MCPClientTools
        self.erp, self.user, self.srv = srv.erp, srv.user, srv
        self.client = MCPClient(srv.url)
        self.tools = MCPClientTools(self.client)
        self.names = self.tools.names

    def schemas(self) -> list[dict]:
        return self.tools.schemas()

    def call(self, name: str, args: dict | None = None) -> dict:
        txt = self.tools.call(name, args or {})
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"ok": False, "error": txt[:500]}

    def close(self):
        self.tools.close()
