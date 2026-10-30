"""The 15 Ledgerline tools over MCP on streamable HTTP, one server per person per mission, traced and logged.

    srv = ToolServer(erp, "ECLARKE", tracer)    # http://127.0.0.1:<port>/mcp, Emma's own Ledgerline session
    srv.parent = turn_span                     # execute_tool spans go under the current turn
    srv.calls                                  # what came over the plug: {turn, name, args, ok, ms}

Every stack connects to the URL the way it connects to any remote MCP server: our harness with the course's
MCPClient, the OpenAI Agents SDK with MCPServerStreamableHttp, LangGraph with langchain-mcp-adapters. The tool
schemas come from the toolbox folders (tool.json), so all three see exactly the same 15 tools.
"""
from __future__ import annotations

import socket
import threading
import time

from ....toolbox.mcp import build_toolbox_server
from . import tracing as T


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class ToolServer:
    def __init__(self, erp, user: str, tracer=None):
        import uvicorn
        self.erp, self.user, self.tracer = erp, user, tracer
        self.mcp = build_toolbox_server(erp, user)
        self.calls: list[dict] = []
        self.parent = None
        self.turn = 0
        self._lock = threading.Lock()
        inner = self.mcp.toolbox.call

        def traced(name, args=None):
            sp = T.tool_span(self.tracer, self.parent, name, args or {}) if self.tracer else None
            t0 = time.perf_counter()
            with self._lock:
                try:
                    out = inner(name, args)
                except Exception as e:  # noqa: BLE001  (a broken tool must not kill the server)
                    out = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            ms = round((time.perf_counter() - t0) * 1000, 1)
            self.calls.append({"turn": self.turn, "name": name, "args": dict(args or {}), "ok": bool(out.get("ok")),
                               "ms": ms, "error": out.get("error") if not out.get("ok") else None,
                               "status": out.get("status_code") or out.get("status")})
            if sp is not None:
                T.finish_tool(sp, out)
            return out

        self.mcp.toolbox.call = traced
        self.port = _free_port()
        app = self.mcp.http_app(path="/mcp")
        self._server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="warning",
                                                     lifespan="on"))
        self._t = threading.Thread(target=self._server.run, daemon=True)
        self._t.start()
        for _ in range(400):
            if self._server.started:
                break
            time.sleep(0.05)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/mcp"

    def stop(self):
        self._server.should_exit = True
        self._t.join(timeout=5)
