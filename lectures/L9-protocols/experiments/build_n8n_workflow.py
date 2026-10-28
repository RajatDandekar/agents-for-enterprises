"""Write the Diwali gasket order as an n8n 2.x workflow whose every Bahi step is an MCP tools/call (stdlib only).

    python3 lectures/L9-protocols/experiments/build_n8n_workflow.py   ->  experiments/n8n/diwali_mcp.json

Same steps as the L6 Studio template (bahi/experience/studio/templates.py, DIWALI):
  webhook -> check_stock -> create_purchase_request -> ask Rohit (with the Wait node's resume link)
  -> Wait for Rohit -> create_purchase_order (Deccan) -> release_purchase_order -> tell Rohit
Each Bahi node is n8n's own "MCP Client" node (@n8n/n8n-nodes-langchain.mcpClient v1.1): it opens a
streamable-HTTP MCP session to the toolbox and calls ONE tool with JSON arguments. Its output is
{content: [{type: "text", text: <the tool's JSON receipt, parsed>}]}, so a later node reads
$('Raise the PR').item.json.content[0].text.request_no.

The toolbox URL: run `python -m bahi.toolbox.mcp --user KJOSHI --transport http --port 8765` (serves /mcp).
"""
import json
import pathlib
import uuid

OUT = pathlib.Path(__file__).parent / "n8n" / "diwali_mcp.json"
URL = "http://127.0.0.1:8765/mcp"   # Kavita's toolbox (the L9 run serves it at /kavita/mcp on the same port)


def rd(node):  # the receipt a previous MCP node returned
    return f"$('{node}').item.json.content[0].text"


def mcp(name, tool, args_expr, x):
    return {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "l9-" + name)), "name": name,
            "type": "@n8n/n8n-nodes-langchain.mcpClient", "typeVersion": 1.1, "position": [x, 300],
            "parameters": {"serverTransport": "httpStreamable", "endpointUrl": URL, "authentication": "none",
                           "tool": {"__rl": True, "mode": "list", "value": tool, "cachedResultName": tool},
                           "inputMode": "json", "jsonInput": args_expr, "options": {}}}


nodes = [
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "l9-webhook")), "name": "Diwali order", "type": "n8n-nodes-base.webhook",
     "typeVersion": 2, "position": [0, 300], "webhookId": str(uuid.uuid5(uuid.NAMESPACE_URL, "l9-webhook-id")),
     "parameters": {"httpMethod": "POST", "path": "diwali-gasket-order", "responseMode": "onReceived", "options": {}}},
    mcp("Check stock", "check_stock", '={{ { "item_code": "GSK-SIL-05L" } }}', 240),
    mcp("Raise the PR", "create_purchase_request",
        '={{ { "item_code": ' + rd("Check stock") + '.item_code, "quantity": 20000, "cost_centre": "PRD-07", '
        '"need_by": "2026-11-09", "confirm": true } }}', 480),
    mcp("Ask Rohit", "send_message",
        '={{ { "to": "@rohit", "text": "Please approve " + ' + rd("Raise the PR") + '.request_no + " (est. Rs " + '
        + rd("Raise the PR") + '.estimated_value.toLocaleString("en-IN") + ", 20,000 gaskets for the Diwali run). '
        'Once approved, this link carries the order on: " + $execution.resumeUrl } }}', 720),
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "l9-wait")), "name": "Wait for Rohit", "type": "n8n-nodes-base.wait",
     "typeVersion": 1.1, "position": [960, 300], "webhookId": str(uuid.uuid5(uuid.NAMESPACE_URL, "l9-wait-id")),
     "parameters": {"resume": "webhook", "httpMethod": "POST", "options": {}}},
    mcp("Order from Deccan", "create_purchase_order",
        '={{ { "supplier_code": "DP-RJK-0042", "request_no": ' + rd("Raise the PR") + '.request_no, "confirm": true } }}',
        1200),
    mcp("Release to supplier", "release_purchase_order", '={{ { "po_no": ' + rd("Order from Deccan") + '.po_no } }}',
        1440),
    mcp("Tell Rohit", "send_message",
        '={{ { "to": "@rohit", "text": ' + rd("Release to supplier") + '.po_no + " is " + ' + rd("Release to supplier")
        + '.status + ": 20,000 gaskets from Deccan Polymers, Rs " + ' + rd("Order from Deccan")
        + '.gross_value.toLocaleString("en-IN") + " incl. GST. Thanks for approving " + ' + rd("Raise the PR")
        + '.request_no + "." } }}', 1680),
]
order = [n["name"] for n in nodes]
connections = {a: {"main": [[{"node": b, "type": "main", "index": 0}]]} for a, b in zip(order, order[1:])}
wf = {"name": "Diwali gasket order (MCP)", "nodes": nodes, "connections": connections,
      "settings": {"executionOrder": "v1", "saveDataSuccessExecution": "all", "saveManualExecutions": True},
      "pinData": {}, "meta": {"note": "Lecture 9 · every Bahi step is an MCP tools/call to the Rasoi toolbox"}}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(wf, indent=1, ensure_ascii=False))
print(OUT, len(nodes), "nodes")
