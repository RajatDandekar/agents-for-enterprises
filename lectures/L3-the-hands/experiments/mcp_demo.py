"""Lecture 3: MCP, one standard plug. Our Bahi server and a marketplace (outbox) server, reached from our harness.

  1 in memory: list the tools, call find_supplier and a create_purchase_order preview, send an email to the outbox
  2 as a process over stdio (the command Claude Desktop would launch)
  3 as a process over streamable HTTP at /mcp (the endpoint n8n's MCP Client Tool node would use)
  4 our harness (ToolLoopAgent) driving BOTH servers through MCPClientTools, with a model (cassette L3_mcp)

We cannot run Claude Desktop or n8n on Modal; steps 2 and 3 test exactly what they would connect to.
Writes logs/mcp_demo.json
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bahi"))

from bahi.agent.loop import SYSTEM, ToolLoopAgent  # noqa: E402
from bahi.erp.engine import ERP  # noqa: E402
from bahi.llm import LLM  # noqa: E402
from bahi.mcp_server import MCPClient, MCPClientTools, Outbox, build_bahi_server, build_outbox_server  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini:gemini-3.8-flash")
a = ap.parse_args()
LOG = pathlib.Path(__file__).parent / "logs"
LOG.mkdir(exist_ok=True)
out = {}

try:
    import fastmcp
    out["fastmcp_version"] = fastmcp.__version__
except Exception as e:  # noqa: BLE001
    out["fastmcp_version"] = repr(e)

# ---------------------------------------------------------------- 1. in memory
erp = ERP()
bahi = MCPClient(build_bahi_server(erp, "KJOSHI"))
box = Outbox()
mail = MCPClient(build_outbox_server(box))
tl = bahi.list_tools()
out["bahi_tools"] = [t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in tl]
out["outbox_tools"] = [t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in mail.list_tools()]
r1 = bahi.call_tool("find_supplier", {"name": "Deccan Polymer Industries"})
r2 = bahi.call_tool("create_purchase_order", {"supplier_code": "DP-RJK-0042", "item_code": "HDL-BKL-01", "quantity": 4000,
                                              "cost_centre": "PRD-07", "need_by": "2026-11-05"})
r3 = mail.call_tool("send_email", {"to": "rohit.mehta@rasoisteel.example", "subject": "Test", "body": "Hello from the sandbox"})
out["wire"] = bahi.wire + mail.wire
out["in_memory_texts"] = {"find_supplier": MCPClient.text(r1), "preview": MCPClient.text(r2), "send_email": MCPClient.text(r3)}
out["services_behind_the_plug"] = [{"svc": c.svc, "user": c.user, "rc": c.rc} for c in erp.calls]
bahi.close(); mail.close()

# ---------------------------------------------------------------- 2. stdio, as Claude Desktop would launch it
env = {**os.environ, "PYTHONPATH": str(ROOT / "bahi")}
try:
    from fastmcp.client.transports import StdioTransport
    c = MCPClient(StdioTransport(command=sys.executable, args=["-m", "bahi.mcp_server", "--user", "KJOSHI"], env=env))
    names = [t.name for t in c.list_tools()]
    res = MCPClient.text(c.call_tool("stock_position", {"item_code": "GSK-SIL-05L"}))
    c.close()
    out["stdio"] = {"ok": True, "command": "python -m bahi.mcp_server --user KJOSHI", "tools": names, "stock_position": res}
except Exception as e:  # noqa: BLE001
    out["stdio"] = {"ok": False, "error": repr(e)[:800]}

# ---------------------------------------------------------------- 3. streamable HTTP, as n8n would reach it
proc = subprocess.Popen([sys.executable, "-m", "bahi.mcp_server", "--user", "KJOSHI", "--transport", "http", "--port", "8765"],
                        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    ok = False
    for _ in range(60):
        time.sleep(0.5)
        try:
            c = MCPClient("http://127.0.0.1:8765/mcp")
            ok = True
            break
        except Exception:  # noqa: BLE001
            continue
    if ok:
        names = [t.name for t in c.list_tools()]
        res = MCPClient.text(c.call_tool("check_cost_centre", {"code": "PRD-05"}))
        c.close()
        out["http"] = {"ok": True, "url": "http://127.0.0.1:8765/mcp", "tools": names, "check_cost_centre": res}
    else:
        out["http"] = {"ok": False, "error": "server did not come up"}
finally:
    proc.terminate()
    try:
        out.setdefault("http", {})["server_log_tail"] = proc.communicate(timeout=5)[0][-1500:]
    except Exception:  # noqa: BLE001
        pass

# ---------------------------------------------------------------- 4. our harness, both servers, a model
erp = ERP()
box = Outbox()
bahi = MCPClient(build_bahi_server(erp, "KJOSHI"))
mail = MCPClient(build_outbox_server(box))
tools = MCPClientTools(bahi, mail)
llm = LLM(a.model, cassette="L3_mcp")
agent = ToolLoopAgent(erp, "KJOSHI", llm=llm, tools=tools, system=SYSTEM)
turns = []
for msg in ["Order 3,000 standard whistles from Sahyadri Valves for PRD-07, need-by 4 November. Once it is released, "
            "email Rohit (rohit.mehta@rasoisteel.example) the order number, and post it in #purchase.",
            "Yes, go ahead."]:
    reply = agent.respond(msg)
    turns.append({"user": msg, "agent": reply})
out["harness_over_mcp"] = {"model": a.model, "turns": turns, "trace": agent.trace, "outbox": box.items,
                           "orders": [{k: o[k] for k in ("po_no", "status", "qty", "gross_value", "cc_cd", "created_by")}
                                      for o in erp.orders(created_by="KJOSHI") if o["created_on"] >= "2026-10-26"],
                           "tool_schemas_after_host_cleaning": tools.schemas(), "llm": llm.totals()}
bahi.close(); mail.close()
(LOG / "mcp_demo.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print(json.dumps({k: (v if k in ("fastmcp_version", "stdio") else "...") for k, v in out.items()}, indent=1)[:3000])
print(json.dumps(out["harness_over_mcp"]["turns"], indent=1, ensure_ascii=False))
print(json.dumps(out["harness_over_mcp"]["outbox"], indent=1, ensure_ascii=False))
print(json.dumps(out.get("http", {}), indent=1)[:1500])
