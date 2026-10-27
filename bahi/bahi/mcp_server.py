"""Lecture 3: Bahi's intent tools over MCP, and a small "marketplace" server next to it.

Two servers, one plug:
  build_bahi_server(erp, user)   the intent tools, bound to ONE user's Bahi session (Kavita by default), so any MCP
                                 client gets exactly her permissions, never the service account's.
  build_outbox_server(outbox)    a stand-in for a marketplace email/Slack server: send_email and post_message write to
                                 an outbox you can inspect (nothing is really sent).

And a client side, so our own harness can use any MCP server:
  MCPClient(target)              a synchronous handle on an MCP client session (works in scripts and in Jupyter).
  MCPClientTools(*clients)       the tools of one or more MCP servers, in the shape ToolLoopAgent expects.

Run as a process, for hosts we do not control:
  python -m bahi.mcp_server --user KJOSHI                         # stdio, for Claude Desktop
  python -m bahi.mcp_server --user KJOSHI --transport http --port 8765   # streamable HTTP at /mcp, for n8n
  python -m bahi.mcp_server --server outbox                       # the marketplace stand-in
Each process holds its own in-memory sandbox, seeded fresh at start.
"""
from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import threading
from typing import Annotated, Optional

from pydantic import Field

from .agent.tools import ALL, TOOLS, TOOLSET_VERSION, IntentTools
from .erp.engine import ERP
from .llm import tool_schema


def _d(tool: str, param: str) -> str:
    return TOOLS[tool].params[param].get("description", "") or param.replace("_", " ")


def _register(mcp, fn, t):
    """Register fn under the tool's own name, description, version and hints, whatever FastMCP version is installed."""
    kw = {"name": t.name, "description": t.description}
    extra = {"annotations": {"readOnlyHint": not t.writes, "destructiveHint": False, "idempotentHint": True,
                             "openWorldHint": False},
             "meta": {"version": t.version, "toolset": TOOLSET_VERSION, "bahi_services": list(t.services)},
             "tags": {"write" if t.writes else "read"}}
    params = inspect.signature(mcp.tool).parameters
    kw.update({k: v for k, v in extra.items() if k in params})
    return mcp.tool(fn, **kw)


def build_bahi_server(erp: ERP | None = None, user: str = "KJOSHI", names: list[str] | None = None,
                      name: str = "bahi-purchasing"):
    """A FastMCP server exposing the intent tools, bound to `user`'s session on `erp`."""
    from fastmcp import FastMCP

    erp = erp or ERP()
    tools = IntentTools(erp.session(user), list(names or ALL))
    u = erp.user(user)
    mcp = FastMCP(name, instructions=(
        f"Purchasing tools for Bahi ERP at Rasoi Steel Works, Pune, acting as {u['name']} ({user}) with "
        f"{u['name'].split()[0]}'s own Bahi permissions. Writes preview first; commit with confirm=true. "
        f"Every write returns a receipt with the status read back from Bahi. Tool set v{TOOLSET_VERSION}."))

    def call(tool_name, **args):
        return tools.call(tool_name, {k: v for k, v in args.items() if v is not None})

    def find_item(query: Annotated[str, Field(description=_d("find_item", "query"))]) -> dict:
        return call("find_item", query=query)

    def stock_position(item_code: Annotated[str, Field(description=_d("stock_position", "item_code"))]) -> dict:
        return call("stock_position", item_code=item_code)

    def last_purchase(item_code: Annotated[str, Field(description="Bahi item code")],
                      supplier_code: Annotated[Optional[str], Field(description=_d("last_purchase", "supplier_code"))] = None) -> dict:
        return call("last_purchase", item_code=item_code, supplier_code=supplier_code)

    def find_supplier(name: Annotated[str, Field(description=_d("find_supplier", "name"))],
                      city: Annotated[Optional[str], Field(description=_d("find_supplier", "city"))] = None) -> dict:
        return call("find_supplier", name=name, city=city)

    def check_cost_centre(code: Annotated[Optional[str], Field(description=_d("check_cost_centre", "code"))] = None) -> dict:
        return call("check_cost_centre", code=code)

    def order_status(po_no: Annotated[Optional[str], Field(description=_d("order_status", "po_no"))] = None,
                     idempotency_key: Annotated[Optional[str], Field(description=_d("order_status", "idempotency_key"))] = None) -> dict:
        return call("order_status", po_no=po_no, idempotency_key=idempotency_key)

    def create_purchase_order(
            supplier_code: Annotated[str, Field(description="Bahi supplier code, from find_supplier")],
            item_code: Annotated[str, Field(description="Bahi item code, from find_item")],
            quantity: Annotated[int, Field(description="how many")],
            cost_centre: Annotated[str, Field(description="an open cost centre, e.g. PRD-07")],
            need_by: Annotated[str, Field(description=_d("create_purchase_order", "need_by"))],
            idempotency_key: Annotated[Optional[str], Field(description=_d("create_purchase_order", "idempotency_key"))] = None,
            rate: Annotated[Optional[float], Field(description=_d("create_purchase_order", "rate"))] = None,
            confirm: Annotated[bool, Field(description=_d("create_purchase_order", "confirm"))] = False) -> dict:
        return call("create_purchase_order", supplier_code=supplier_code, item_code=item_code, quantity=quantity,
                    cost_centre=cost_centre, need_by=need_by, idempotency_key=idempotency_key, rate=rate, confirm=confirm)

    def release_purchase_order(po_no: Annotated[str, Field(description="the order number, e.g. PO/2026/01182")]) -> dict:
        return call("release_purchase_order", po_no=po_no)

    def amend_purchase_order(po_no: Annotated[str, Field(description="the order number")],
                             quantity: Annotated[Optional[int], Field(description="new quantity")] = None,
                             need_by: Annotated[Optional[str], Field(description="new date, YYYY-MM-DD")] = None,
                             cost_centre: Annotated[Optional[str], Field(description="new cost centre")] = None) -> dict:
        return call("amend_purchase_order", po_no=po_no, quantity=quantity, need_by=need_by, cost_centre=cost_centre)

    def register_supplier(name: Annotated[str, Field(description="supplier's registered name")],
                          city: Annotated[str, Field(description="city")],
                          state: Annotated[str, Field(description=_d("register_supplier", "state"))],
                          gstin: Annotated[str, Field(description="15-character GSTIN")],
                          confirm: Annotated[bool, Field(description="false = preview only; true = commit")] = False) -> dict:
        return call("register_supplier", name=name, city=city, state=state, gstin=gstin, confirm=confirm)

    def record_certificate(supplier_code: Annotated[str, Field(description="Bahi supplier code")],
                           document_ref: Annotated[str, Field(description="the certificate's reference, as on the document")],
                           valid_to: Annotated[str, Field(description=_d("record_certificate", "valid_to"))]) -> dict:
        return call("record_certificate", supplier_code=supplier_code, document_ref=document_ref, valid_to=valid_to)

    for fn in (find_item, stock_position, last_purchase, find_supplier, check_cost_centre, order_status,
               create_purchase_order, release_purchase_order, amend_purchase_order, register_supplier, record_certificate):
        if fn.__name__ in tools.names:
            _register(mcp, fn, TOOLS[fn.__name__])
    mcp.bahi_erp, mcp.bahi_user = erp, user
    return mcp


# ----------------------------------------------------------------------------- the marketplace stand-in
class Outbox:
    """Where the marketplace server 'sends' things. Deterministic ids, no wall clock, so replays match."""

    def __init__(self):
        self.items: list[dict] = []

    def add(self, kind: str, **fields) -> dict:
        m = {"id": f"MSG-{len(self.items) + 1:04d}", "kind": kind, **fields, "status": "QUEUED (sandbox: not sent)"}
        self.items.append(m)
        return m


def build_outbox_server(outbox: Outbox | None = None, name: str = "outbox"):
    """An email and chat server of the kind you would install from a marketplace. It knows nothing about Bahi."""
    from fastmcp import FastMCP

    box = outbox or Outbox()
    mcp = FastMCP(name, instructions="Send email and team-chat messages. In this sandbox everything lands in an outbox.")

    def send_email(to: Annotated[str, Field(description="recipient email address")],
                   subject: Annotated[str, Field(description="subject line")],
                   body: Annotated[str, Field(description="plain-text body")]) -> dict:
        """Send an email."""
        return {"ok": True, **box.add("email", to=to, subject=subject, body=body)}

    def post_message(channel: Annotated[str, Field(description="a channel like #purchase, or a person like @rohit")],
                     text: Annotated[str, Field(description="the message")]) -> dict:
        """Post a message to a team-chat channel or person."""
        return {"ok": True, **box.add("chat", channel=channel, text=text)}

    def list_outbox(limit: Annotated[int, Field(description="how many of the latest messages")] = 10) -> dict:
        """List the latest messages in the outbox."""
        return {"ok": True, "messages": box.items[-limit:]}

    for fn in (send_email, post_message, list_outbox):
        mcp.tool(fn)
    mcp.outbox = box
    return mcp


# ----------------------------------------------------------------------------- the client side
class MCPClient:
    """A synchronous handle on an MCP client session. The session lives on its own event-loop thread, so this works
    the same in a script and inside Jupyter (which already runs a loop).

        c = MCPClient(build_bahi_server(erp))          # in memory
        c = MCPClient("http://127.0.0.1:8765/mcp")     # over HTTP
        c.list_tools(); c.call_tool("find_item", {"query": "5 litre gasket"})
    """

    def __init__(self, target, timeout: float = 120):
        from fastmcp import Client

        self.timeout = timeout
        self.loop = asyncio.new_event_loop()
        self._t = threading.Thread(target=self.loop.run_forever, daemon=True)
        self._t.start()
        self.client = Client(target)
        self._run(self.client.__aenter__())
        self.wire: list[dict] = []  # what went over the plug: method, params, and the result

    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(self.timeout)

    def list_tools(self):
        tools = self._run(self.client.list_tools())
        self.wire.append({"method": "tools/list", "params": {},
                          "result": {"tools": [t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in tools]}})
        return tools

    def call_tool(self, name: str, args: dict):
        """Returns the raw MCP CallToolResult (content blocks, structured content, isError)."""
        if hasattr(self.client, "call_tool_mcp"):
            res = self._run(self.client.call_tool_mcp(name, args))
        else:
            res = self._run(self.client.call_tool(name, args, raise_on_error=False))
        dump = res.model_dump(mode="json", by_alias=True, exclude_none=True) if hasattr(res, "model_dump") else str(res)
        self.wire.append({"method": "tools/call", "params": {"name": name, "arguments": args}, "result": dump})
        return res

    @staticmethod
    def text(res) -> str:
        blocks = getattr(res, "content", None) or []
        return "\n".join(getattr(b, "text", "") for b in blocks if getattr(b, "text", None) is not None)

    def close(self):
        try:
            self._run(self.client.__aexit__(None, None, None))
        except Exception:
            pass
        self.loop.call_soon_threadsafe(self.loop.stop)


def _clean_schema(s):
    """What a host does to MCP schemas before handing them to a model API: drop titles and null defaults, and turn
    Optional[X] (anyOf X|null) into plain X. Gemini's function declarations reject the null type."""
    if isinstance(s, list):
        return [_clean_schema(x) for x in s]
    if not isinstance(s, dict):
        return s
    if "anyOf" in s:
        opts = [o for o in s["anyOf"] if o.get("type") != "null"]
        if len(opts) == 1:
            merged = {**{k: v for k, v in s.items() if k != "anyOf"}, **opts[0]}
            return _clean_schema(merged)
    out = {}
    for k, v in s.items():
        if k in ("title", "additionalProperties", "$schema") or (k == "default" and v is None):
            continue
        out[k] = _clean_schema(v) if k != "properties" else {pk: _clean_schema(pv) for pk, pv in v.items()}
    return out


class MCPClientTools:
    """The tools of one or more MCP servers, discovered at connect time, in the shape ToolLoopAgent expects."""

    def __init__(self, *clients: MCPClient):
        self.clients = clients
        self.where, self._schemas = {}, []
        for c in clients:
            for t in c.list_tools():
                self.where[t.name] = c
                self._schemas.append(tool_schema(t.name, t.description or "", {}, []))
                self._schemas[-1]["function"]["parameters"] = _clean_schema(getattr(t, "input_schema", None) or getattr(t, "inputSchema", None)) or {"type": "object", "properties": {}}
        self.names = list(self.where)

    def schemas(self) -> list[dict]:
        return self._schemas

    def call(self, name: str, args: dict) -> str:
        if name not in self.where:
            return json.dumps({"ok": False, "error": f"Unknown tool {name}."})
        c = self.where[name]
        res = c.call_tool(name, args or {})
        txt = c.text(res)
        if getattr(res, "is_error", None) or (getattr(res, "is_error", None) is None and getattr(res, "isError", False)):
            return json.dumps({"ok": False, "error": txt})
        return txt

    def close(self):
        for c in self.clients:
            c.close()


def main():
    ap = argparse.ArgumentParser(description="Serve Bahi's intent tools (or the outbox stand-in) over MCP.")
    ap.add_argument("--server", default="bahi", choices=["bahi", "outbox"])
    ap.add_argument("--user", default="KJOSHI", help="whose Bahi session the tools act in")
    ap.add_argument("--transport", default="stdio", choices=["stdio", "http", "sse"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    mcp = build_bahi_server(user=a.user) if a.server == "bahi" else build_outbox_server()
    if a.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=a.transport, host=a.host, port=a.port)


if __name__ == "__main__":
    main()
