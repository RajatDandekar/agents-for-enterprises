"""The Northbridge toolbox as an MCP server, written with the official MCP Python SDK (mcp 2.x, low-level Server).

L4 served the toolbox with FastMCP (a separate project built on the official SDK). Here we use the SDK's
low-level `Server` directly, so every MCP method is a handler we write and can read:

    tools/list, tools/call                    the 15 tool.json folders, bound to one user's Ledgerline session
    resources/list, resources/read            the purchase policy and the supplier policy as documents
    resources/templates/list                  northbridge://stock/{item_code}: live stock, read like a file
    prompts/list, prompts/get                 "raise_a_pr": a ready-made, reviewed set of instructions
    elicitation (inside tools/call)           before a write commits, the server asks the *person* to confirm

    from ledgerline.course.protocols.northbridge_mcp import build_northbridge_server
    server = build_northbridge_server(erp, user="ECLARKE")
    async with mcp.Client(server) as c: ...                     # in-process
    python -m ledgerline.course.protocols.northbridge_mcp --user ECLARKE     # stdio, for Claude Desktop / VS Code / Inspector
    python -m ledgerline.course.protocols.northbridge_mcp --http 8765       # streamable HTTP at /mcp

Elicitation follows the 2026-07-28 revision: the server answers tools/call with an *input_required*
result carrying the question and a signed requestState; the client asks the person and retries the same
call with their answer. Clients that did not declare the elicitation capability never get a question
(the spec forbids it); they get the tool's own preview/confirm behaviour from L4 instead.
On the older handshake era (2025-11-25) the same question goes out mid-call as a server-to-client
elicitation/create request instead.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import pathlib
import time
from typing import Any

from ...erp.engine import ERP
from ...toolbox import SPECS, Toolbox

DOCS = pathlib.Path(__file__).resolve().parents[2] / "docs"
RESOURCES = {
    "northbridge://policy/purchase": ("purchase-policy.md", "Purchase policy",
                                "Northbridge Cycles purchase policy: requests before orders, limits, suppliers, prices, tax."),
    "northbridge://policy/supplier": ("supplier-policy.md", "Supplier policy",
                                "How a supplier is qualified, including the UN 38.3 certificate rule."),
    "northbridge://policy/approval-matrix": ("approval-matrix.md", "Approval matrix",
                                       "Who may approve how much, gross including VAT."),
}
STOCK_TEMPLATE = "northbridge://stock/{item_code}"
CONFIRM_TOOLS = {"create_purchase_request", "create_purchase_order", "receive_goods", "register_supplier"}
STATE_TTL_S = 300


def _secret() -> bytes:
    return os.environ.get("NORTHBRIDGE_MCP_STATE_KEY", "course-demo-key-not-a-secret").encode()


def sign_state(payload: dict) -> str:
    """requestState is attacker-controlled when it comes back, so we sign it (HMAC) and check on return."""
    body = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True).encode()).decode()
    mac = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{body}.{mac}"


def check_state(state: str) -> dict | None:
    try:
        body, mac = state.rsplit(".", 1)
    except ValueError:
        return None
    good = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(mac, good):
        return None
    return json.loads(base64.urlsafe_b64decode(body.encode()))


def _args_digest(name: str, args: dict) -> str:
    return hashlib.sha256(json.dumps([name, args], sort_keys=True, default=str).encode()).hexdigest()[:16]


def _inr(v) -> str:
    """£ with Indian digit grouping: 269040 -> £269,040."""
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        return str(v)
    s = str(abs(n))
    head, tail = s[:-3], s[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return ("-" if n < 0 else "") + "£" + (head + "," + tail if head else tail)


def _question(name: str, preview: dict) -> str:
    p = preview.get("preview", preview)
    if name == "create_purchase_request":
        q = (f"Raise a purchase request for {p.get('quantity'):,} x {p.get('item_code')} on {p.get('cost_centre')}, "
             f"needed by {p.get('need_by')}? Estimated {_inr(p.get('estimated_value'))} incl. VAT.")
        if p.get("needs_approval"):
            q += f" It is above your {_inr(p.get('your_limit'))} limit, so it will wait for {p.get('approver')}."
        return q
    if name == "create_purchase_order":
        return (f"Create the purchase order to {p.get('supplier_code') or p.get('supplier')}: "
                f"{_inr(p.get('gross_value') or p.get('estimated_value'))} gross? Nothing is sent until you confirm.")
    return f"Confirm {name.replace('_', ' ')}? " + json.dumps(p, default=str)[:300]


CONFIRM_SCHEMA = {"type": "object",
                  "properties": {"confirm": {"type": "boolean", "title": "Confirm", "description": "Yes, save it in Ledgerline"}},
                  "required": ["confirm"]}


def _modern(ctx) -> bool:
    """True on the stateless 2026-07-28 protocol (questions ride inside the result), False on the handshake era."""
    from mcp_types.version import is_version_at_least
    v = getattr(ctx, "protocol_version", None) or ""
    try:
        return is_version_at_least(v, "2026-07-28")
    except ValueError:
        return False


def _client_can_elicit(ctx) -> bool:
    caps = None
    meta = getattr(ctx, "meta", None)
    if meta is not None:
        extra = getattr(meta, "model_extra", None) or {}
        caps = extra.get("io.modelcontextprotocol/clientCapabilities") or getattr(meta, "client_capabilities", None)
    if caps is None:
        cp = getattr(getattr(ctx, "session", None), "client_params", None)
        caps = getattr(cp, "capabilities", None)
    if caps is None:
        return False
    if isinstance(caps, dict):
        return caps.get("elicitation") is not None
    return getattr(caps, "elicitation", None) is not None


def build_northbridge_server(erp: ERP | None = None, user: str = "ECLARKE", names: list[str] | None = None,
                       elicit_writes: bool = True, name: str = "northbridge-toolbox"):
    """A low-level official-SDK MCP server over the toolbox folders, bound to `user`'s own Ledgerline session."""
    import mcp_types as t
    from mcp.server import Server

    erp = erp or ERP()
    tb = Toolbox(erp, user, names)
    who = erp.user(user)
    asked: list[dict] = []  # every confirmation question asked, for the notebook to show

    async def list_tools(ctx, params):
        tools = []
        for n in tb.names:
            sp = SPECS[n].spec
            tools.append(t.Tool(name=n, title=sp["title"], description=sp["description"], input_schema=sp["input_schema"],
                                annotations=t.ToolAnnotations(title=sp["title"], read_only_hint=not sp.get("writes"),
                                                              destructive_hint=False, idempotent_hint=True,
                                                              open_world_hint=False)))
        return t.ListToolsResult(tools=tools, ttl_ms=60_000)

    async def call_tool(ctx, params):
        n, args = params.name, dict(params.arguments or {})
        wants_commit = n in CONFIRM_TOOLS and args.get("confirm") is True
        if elicit_writes and wants_commit and _client_can_elicit(ctx):
            digest = _args_digest(n, args)
            responses = getattr(params, "input_responses", None) or {}
            state = getattr(params, "request_state", None)
            if responses or state:
                st = check_state(state or "")
                if not st or st.get("user") != user or st.get("tool") != n or st.get("args") != digest \
                        or st.get("exp", 0) < time.time():
                    return t.CallToolResult(is_error=True, content=[t.TextContent(type="text", text=json.dumps(
                        {"ok": False, "error": "The confirmation did not match this request (state failed its check).",
                         "next_step": "Ask again; the person must confirm this exact request."}))])
                ans = responses.get("confirm_write")
                ans = ans.model_dump() if hasattr(ans, "model_dump") else (ans or {})
                ok = ans.get("action") == "accept" and (ans.get("content") or {}).get("confirm") is True
                if not ok:
                    out = {"ok": False, "error": f"{who['name'].split()[0]} did not confirm.", "declined": True,
                           "next_step": "Nothing was saved. Ask what to change."}
                    return t.CallToolResult(content=[t.TextContent(type="text", text=json.dumps(out))],
                                            structured_content=out)
            else:
                preview = tb.call(n, {**args, "confirm": False})
                if not preview.get("ok"):
                    return t.CallToolResult(is_error=True, content=[t.TextContent(type="text", text=json.dumps(preview, default=str))])
                question = _question(n, preview)
                if not _modern(ctx):
                    # Handshake era (2025-11-25 and older): the server sends elicitation/create mid-call and waits.
                    asked.append({"tool": n, "question": question, "era": "legacy"})
                    ans = await ctx.session.elicit_form(question, CONFIRM_SCHEMA, related_request_id=ctx.request_id)
                    if not (ans.action == "accept" and (ans.content or {}).get("confirm") is True):
                        out = {"ok": False, "error": f"{who['name'].split()[0]} did not confirm.", "declined": True,
                               "next_step": "Nothing was saved. Ask what to change."}
                        return t.CallToolResult(content=[t.TextContent(type="text", text=json.dumps(out))],
                                                structured_content=out)
                    out = tb.call(n, args)
                    return t.CallToolResult(content=[t.TextContent(type="text", text=json.dumps(out, default=str))],
                                            structured_content=out, is_error=not out.get("ok", True))
                asked.append({"tool": n, "question": question, "era": "2026-07-28"})
                return t.InputRequiredResult(
                    input_requests={"confirm_write": t.ElicitRequest(params=t.ElicitRequestFormParams(
                        message=question, requested_schema=CONFIRM_SCHEMA))},
                    request_state=sign_state({"user": user, "tool": n, "args": digest,
                                              "exp": int(time.time()) + STATE_TTL_S}))
        out = tb.call(n, args)
        return t.CallToolResult(content=[t.TextContent(type="text", text=json.dumps(out, default=str))],
                                structured_content=out, is_error=not out.get("ok", True))

    async def list_resources(ctx, params):
        return t.ListResourcesResult(ttl_ms=3_600_000, resources=[
            t.Resource(uri=u, name=f, title=title, description=d, mime_type="text/markdown",
                       size=(DOCS / f).stat().st_size) for u, (f, title, d) in RESOURCES.items()])

    async def list_templates(ctx, params):
        return t.ListResourceTemplatesResult(ttl_ms=3_600_000, resource_templates=[t.ResourceTemplate(
            uri_template=STOCK_TEMPLATE, name="stock", title="Live stock of one item",
            description="On hand, allocated and on order in every Northbridge warehouse, read from Ledgerline now.",
            mime_type="application/json")])

    async def read_resource(ctx, params):
        uri = str(params.uri)
        if uri in RESOURCES:
            text = (DOCS / RESOURCES[uri][0]).read_text()
            return t.ReadResourceResult(ttl_ms=3_600_000, contents=[
                t.TextResourceContents(uri=uri, mime_type="text/markdown", text=text)])
        if uri.startswith("northbridge://stock/"):
            out = tb.call("check_stock", {"item_code": uri.rsplit("/", 1)[1]}) if "check_stock" in tb.names else {"ok": False}
            return t.ReadResourceResult(ttl_ms=0, contents=[
                t.TextResourceContents(uri=uri, mime_type="application/json", text=json.dumps(out, default=str))])
        from mcp.shared.exceptions import MCPError
        raise MCPError(code=-32602, message=f"Unknown resource {uri}")

    PROMPTS = {
        "raise_a_pr": t.Prompt(name="raise_a_pr", title="Raise a purchase request",
                               description="Northbridge's reviewed steps for raising a PR: find, check stock, preview, confirm.",
                               arguments=[t.PromptArgument(name="item", description="what to buy, in plain words", required=True),
                                          t.PromptArgument(name="quantity", description="how many", required=True),
                                          t.PromptArgument(name="need_by", description="YYYY-MM-DD", required=True)]),
        "explain_a_rule": t.Prompt(name="explain_a_rule", title="Explain a purchase rule",
                                   description="Answer a question about Northbridge's purchase rules from the policy, with the section number.",
                                   arguments=[t.PromptArgument(name="question", required=True)]),
    }

    async def list_prompts(ctx, params):
        return t.ListPromptsResult(ttl_ms=3_600_000, prompts=list(PROMPTS.values()))

    async def get_prompt(ctx, params):
        a = dict(params.arguments or {})
        policy = t.EmbeddedResource(type="resource", resource=t.TextResourceContents(
            uri="northbridge://policy/purchase", mime_type="text/markdown", text=(DOCS / "purchase-policy.md").read_text()))
        if params.name == "raise_a_pr":
            text = (f"Raise a purchase request at Northbridge Cycles for {a.get('quantity')} of \"{a.get('item')}\", "
                    f"needed by {a.get('need_by')}, as {who['name']} ({user}).\n"
                    "1. find_item to get the Ledgerline item code; if more than one matches, ask which.\n"
                    "2. check_stock and say which plant you mean (Manchester, Leeds or both).\n"
                    "3. check_budget for the cost centre; never use a closed one (PRD-05 closed on 15 Oct).\n"
                    "4. create_purchase_request with confirm=false; show the estimate and who must approve.\n"
                    "5. Only after the person says yes, call it again with confirm=true and read the receipt back.\n"
                    "Follow the purchase policy attached below.")
            msgs = [t.PromptMessage(role="user", content=t.TextContent(type="text", text=text)),
                    t.PromptMessage(role="user", content=policy)]
            return t.GetPromptResult(description=PROMPTS["raise_a_pr"].description, messages=msgs)
        if params.name == "explain_a_rule":
            text = (f"Answer this question about Northbridge's purchase rules: {a.get('question')}\n"
                    "Quote the section number (for example §6.2). If the policy does not say, say so.")
            return t.GetPromptResult(messages=[t.PromptMessage(role="user", content=t.TextContent(type="text", text=text)),
                                               t.PromptMessage(role="user", content=policy)])
        from mcp.shared.exceptions import MCPError
        raise MCPError(code=-32602, message=f"Unknown prompt {params.name}")

    server = Server(name, version="9.0", title="Northbridge toolbox (official SDK)",
                    instructions=f"Northbridge Cycles' Ledgerline ERP, as {who['name']} ({user}). One tool per business "
                                 "activity. Writes ask the person to confirm before they are saved.",
                    on_list_tools=list_tools, on_call_tool=call_tool, on_list_resources=list_resources,
                    on_list_resource_templates=list_templates, on_read_resource=read_resource,
                    on_list_prompts=list_prompts, on_get_prompt=get_prompt)
    server.toolbox, server.asked, server.erp = tb, asked, erp
    return server


async def _stdio(server):
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="ECLARKE")
    ap.add_argument("--http", type=int, default=0, help="serve streamable HTTP on this port at /mcp")
    ap.add_argument("--no-elicit", action="store_true")
    a = ap.parse_args()
    server = build_northbridge_server(ERP(), a.user, elicit_writes=not a.no_elicit)
    if a.http:
        import uvicorn
        uvicorn.run(server.streamable_http_app(), host="127.0.0.1", port=a.http, log_level="warning")
    else:
        import anyio
        anyio.run(_stdio, server)


if __name__ == "__main__":
    main()
