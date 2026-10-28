"""Lecture 4: MCP on the wire. The toolbox server, the same JSON-RPC over two transports, and what a client sees.

  1 in memory   build_toolbox_server + MCPClient: tools/list and tools/call, as MCPClient.wire records them
  2 stdio       `python -m bahi.toolbox.mcp --user KJOSHI` as a child process (what Claude Desktop runs),
                raw JSON-RPC lines written to stdin and read from stdout
  3 HTTP        the same server with --transport http; raw POSTs to /mcp (streamable HTTP), headers and bodies
  4 whose session  the same tools/call made to a server started --user KJOSHI and one started --user SVC_AGENT
Writes logs/mcp_wire.json.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import httpx

from bahi.course.l4 import handshake, stdio_wire
from bahi.erp.engine import ERP
from bahi.mcp_server import MCPClient, MCPClientTools
from bahi.toolbox.mcp import build_toolbox_server

LOG = pathlib.Path(__file__).resolve().parent / "logs"
out = {}

# ---------------------------------------------------------------- 1 in memory, through MCPClient
erp = ERP()
c = MCPClient(build_toolbox_server(erp, "KJOSHI"))
tools = c.list_tools()
res = c.call_tool("check_stock", {"item_code": "GSK-SIL-05L"})
bad = c.call_tool("check_stock", {"item_code": 42})
mt = MCPClientTools(c)
out["inmemory"] = {"n_tools": len(tools), "names": [t.name for t in tools], "wire": c.wire,
                   "client_schema_check_stock": next(s for s in mt.schemas() if s["function"]["name"] == "check_stock")}
c.close()
print("in memory:", len(tools), "tools;", [w["method"] for w in out["inmemory"]["wire"]])

# ---------------------------------------------------------------- 2 stdio, raw lines
reqs = handshake("nb4-client") + [
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_stock", "arguments": {"item_code": "GSK-SIL-05L"}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "create_purchase_request", "arguments": {
        "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09"}}},
    {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "no_such_tool", "arguments": {}}},
]
t0 = time.time()
wire = stdio_wire(reqs, "KJOSHI")
out["stdio"] = {"command": [sys.executable.split("/")[-1], "-m", "bahi.toolbox.mcp", "--user", "KJOSHI"],
                "seconds": round(time.time() - t0, 2), "wire": wire,
                "line_bytes": [len(json.dumps(w["msg"])) for w in wire]}
print("stdio:", [(w["dir"], w["msg"].get("method") or ("result" if "result" in w["msg"] else "error")) for w in wire])

# ---------------------------------------------------------------- 3 streamable HTTP, raw POSTs
env = {**os.environ, "FASTMCP_SHOW_CLI_BANNER": "false", "FASTMCP_LOG_LEVEL": "ERROR"}
srv = subprocess.Popen([sys.executable, "-m", "bahi.toolbox.mcp", "--user", "KJOSHI", "--transport", "http", "--port", "8765"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
url = "http://127.0.0.1:8765/mcp"
for _ in range(60):
    try:
        httpx.get(url, timeout=1)
        break
    except Exception:  # noqa: BLE001
        time.sleep(0.5)
H = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
http = []
sid = None
with httpx.Client(timeout=30, follow_redirects=True) as h:
    for req in reqs[:4]:
        hd = dict(H, **({"mcp-session-id": sid} if sid else {}), **({"mcp-protocol-version": "2025-06-18"} if sid else {}))
        r = h.post(url, json=req, headers=hd)
        sid = sid or r.headers.get("mcp-session-id")
        body = r.text
        parsed = None
        for line in body.splitlines():  # a streamed reply arrives as server-sent events: "data: {...}"
            if line.startswith("data:"):
                parsed = json.loads(line[5:].strip())
        if parsed is None and body.strip().startswith("{"):
            parsed = json.loads(body)
        http.append({"request": {"method": "POST", "url": "/mcp", "headers": {k: v for k, v in hd.items()}, "body": req},
                     "response": {"status": r.status_code, "content_type": r.headers.get("content-type"),
                                  "session_id": r.headers.get("mcp-session-id"), "raw": body[:1500], "json": parsed}})
srv.terminate()
out["http"] = {"command": "python -m bahi.toolbox.mcp --user KJOSHI --transport http --port 8765", "url": url, "exchanges": http}
print("http:", [(x["request"]["body"].get("method"), x["response"]["status"], x["response"]["content_type"]) for x in http])

# ---------------------------------------------------------------- 4 whose permissions does the server carry?
call = [{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "approve_purchase_order",
                                                                       "arguments": {"po_no": "PO/2026/01179"}}}]
out["whose"] = {u: stdio_wire(handshake() + call, u)[-1]["msg"] for u in ("KJOSHI", "SVC_AGENT")}
for u, m in out["whose"].items():
    print("as", u, json.dumps(m)[:200])

(LOG / "mcp_wire.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("wrote logs/mcp_wire.json")
