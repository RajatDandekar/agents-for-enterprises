"""The Studio's ready-made workflows. Each one runs end to end on a fresh Rasoi (tests/test_engine.py proves it).

    from bahi.experience.studio.templates import TEMPLATES, template
    wf = template("diwali-gasket-order")      # a fresh copy, safe to change
"""
from __future__ import annotations

import copy

GAP = 230  # canvas distance between two columns of nodes


def _n(nid, typ, title, col, row=0, **config):
    return {"id": nid, "type": typ, "title": title, "x": 60 + col * GAP, "y": 200 + row * 170, "config": config}


def _chain(*ids, port=None):
    return [{"from": a, "to": b, **({"port": port} if port else {})} for a, b in zip(ids, ids[1:])]


DIWALI = {
    "id": "diwali-gasket-order",
    "name": "Diwali gasket order",
    "description": "Kavita's 20,000 gaskets for the Diwali run: check stock, raise the request, wait for Rohit, "
                   "order from Deccan Polymers, release it and tell Rohit.",
    "nodes": [
        _n("start", "trigger", "Start", 0, kind="manual"),
        _n("stock", "tool", "Check stock", 1, tool="check_stock", **{"as": "KJOSHI"}, args={"item_code": "GSK-SIL-05L"}),
        _n("pr", "tool", "Raise the PR", 2, tool="create_purchase_request", **{"as": "KJOSHI"}, confirm=True,
           args={"item_code": "{{nodes.stock.item_code}}", "quantity": 20000, "cost_centre": "PRD-07",
                 "need_by": "2026-11-09"}),
        _n("rohit", "approval", "Rohit approves", 3, doc_no="{{nodes.pr.request_no}}", approver="RMEHTA"),
        _n("po", "tool", "Order from Deccan", 4, tool="create_purchase_order", **{"as": "KJOSHI"}, confirm=True,
           args={"supplier_code": "DP-RJK-0042", "request_no": "{{nodes.pr.request_no}}"}),
        _n("release", "tool", "Release to supplier", 5, tool="release_purchase_order", **{"as": "KJOSHI"},
           args={"po_no": "{{nodes.po.po_no}}"}),
        _n("tell", "message", "Tell Rohit", 6, to="@rohit", **{"as": "KJOSHI"},
           text="{{nodes.release.po_no}} is {{nodes.release.status}}: 20,000 gaskets from Deccan Polymers, "
                "{{ inr(nodes.po.gross_value) }} incl. GST. Thanks for approving {{nodes.pr.request_no}}."),
    ],
    "edges": _chain("start", "stock", "pr", "rohit", "po", "release", "tell"),
}

REORDER = {
    "id": "reorder-when-low",
    "name": "Reorder when low",
    "description": "When an item falls below its reorder level, raise a request for three times the reorder level, "
                   "get it approved, order and release it. If an order is already on the way, only tell Kavita.",
    "nodes": [
        _n("low", "trigger", "Stock below reorder level", 0, kind="event", event="stock_below_reorder",
           item_codes=["GSK-SIL-05L", "WHS-STD-01"], **{"as": "KJOSHI"}),
        _n("plan", "set", "Plan the order", 1, values={
            "quantity": "{{ trigger.reorder_level * 3 }}",
            "supplier": "{{ 'SV-PUN-0017' if trigger.item_code == 'WHS-STD-01' else 'DP-RJK-0042' }}",
            "need_by": "{{ add_days(today, 14) }}"}),
        _n("nothing_on_order", "condition", "Nothing on order yet?", 2, **{"if": "{{ trigger.on_order == 0 }}"}),
        _n("pr", "tool", "Raise the PR", 3, -0.6, tool="create_purchase_request", **{"as": "KJOSHI"}, confirm=True,
           args={"item_code": "{{trigger.item_code}}", "quantity": "{{nodes.plan.quantity}}", "cost_centre": "PRD-07",
                 "need_by": "{{nodes.plan.need_by}}"}),
        _n("note", "message", "Tell Kavita", 3, 0.75, to="@kavita", **{"as": "KJOSHI"},
           text="{{trigger.item_code}} is below its reorder level, but {{trigger.on_order}} are already on order. "
                "Nothing new raised."),
        _n("rohit", "approval", "Rohit approves", 4, -0.6, doc_no="{{nodes.pr.request_no}}", approver="RMEHTA"),
        _n("po", "tool", "Create the PO", 5, -0.6, tool="create_purchase_order", **{"as": "KJOSHI"}, confirm=True,
           args={"supplier_code": "{{nodes.plan.supplier}}", "request_no": "{{nodes.pr.request_no}}"}),
        _n("release", "tool", "Release to supplier", 6, -0.6, tool="release_purchase_order", **{"as": "KJOSHI"},
           args={"po_no": "{{nodes.po.po_no}}"}),
        _n("tell", "message", "Tell Rohit", 7, -0.6, to="@rohit", **{"as": "KJOSHI"},
           text="Auto-reorder: {{ indian(nodes.po.quantity) }} x {{trigger.item_code}} ordered on {{nodes.release.po_no}} "
                "({{nodes.release.status}})."),
    ],
    "edges": _chain("low", "plan", "nothing_on_order")
    + [{"from": "nothing_on_order", "port": "true", "to": "pr"},
       {"from": "nothing_on_order", "port": "false", "to": "note"}]
    + _chain("pr", "rohit", "po", "release", "tell"),
}

GOODS = {
    "id": "goods-arrived",
    "name": "Goods arrived",
    "description": "Neha fills a short form at the gate: the order and the count. The workflow records the goods "
                   "receipt as Neha, reads the order's status back and tells Kavita.",
    "nodes": [
        _n("form", "trigger", "Goods at the gate", 0, kind="form", fields=[
            {"name": "po_no", "label": "Purchase order", "type": "text", "default": "PO/2026/01167"},
            {"name": "quantity", "label": "Quantity counted", "type": "number", "default": 40000},
            {"name": "vehicle", "label": "Vehicle number", "type": "text", "default": "MH-12-KT-4471"}]),
        _n("grn", "tool", "Record the receipt", 1, tool="receive_goods", **{"as": "NDESAI"}, confirm=True,
           args={"po_no": "{{trigger.po_no}}", "quantity": "{{trigger.quantity}}",
                 "remarks": "Vehicle {{trigger.vehicle}}"}),
        _n("status", "tool", "Order status", 2, tool="order_status", **{"as": "KJOSHI"},
           args={"po_no": "{{nodes.grn.po_no}}"}),
        _n("tell", "message", "Tell Kavita", 3, to="@kavita", **{"as": "RMEHTA"},
           text="Neha received {{ indian(nodes.grn.received) }} on {{nodes.grn.po_no}} ({{nodes.grn.grn_no}}). "
                "Order: {{nodes.status.status}}; {{ indian(nodes.grn.balance) }} still to come. Stock now {{ indian(nodes.grn.stock_after) }}."),
    ],
    "edges": _chain("form", "grn", "status", "tell"),
}

DEALER_EMAIL = """Subject: Spare gaskets before Diwali

Dear Rasoi team,

Our service centre in Nagpur is running short of spares. Please send us 4,000 silicone gaskets for your
5 litre pressure cooker. We need them at our godown by 12 November, before the festival rush.

Regards,
Prakash Sharma
Sharma Home Appliances, Nagpur"""

DEALER = {
    "id": "dealer-email-to-order",
    "name": "Dealer email to order",
    "description": "A dealer's email, read by an LLM node: it pulls out the item, quantity and date, finds the item "
                   "in Bahi and raises the purchase request.",
    "nodes": [
        _n("email", "trigger", "Dealer email", 0, kind="manual", data={"email": DEALER_EMAIL}),
        _n("extract", "llm", "Read the email", 1, output="json", fields=["item", "quantity", "need_by", "dealer"],
           model="gemini:gemini-3.8-flash",
           prompt="A dealer has written to Rasoi Steel Works, Pune. Today is {{today}}.\n"
                  "Read the email and pull out what they need.\n"
                  "item: the part in 3 to 5 plain words (size, material, part name); quantity: a whole number; "
                  "need_by: the date as YYYY-MM-DD; dealer: the dealer's company name.\n\nEmail:\n{{trigger.email}}"),
        _n("find", "tool", "Find the item", 2, tool="find_item", **{"as": "KJOSHI"},
           args={"query": "{{nodes.extract.item}}"}),
        _n("pr", "tool", "Raise the PR", 3, tool="create_purchase_request", **{"as": "KJOSHI"}, confirm=True,
           args={"item_code": "{{nodes.find.items[0].item_code}}", "quantity": "{{nodes.extract.quantity}}",
                 "cost_centre": "PRD-07", "need_by": "{{nodes.extract.need_by}}"}),
        _n("tell", "message", "Tell Rohit", 4, to="@rohit", **{"as": "KJOSHI"},
           text="{{nodes.extract.dealer}} asked for {{ indian(nodes.extract.quantity) }} x {{nodes.find.items[0].description}} "
                "by {{nodes.extract.need_by}}. Raised {{nodes.pr.request_no}} ({{nodes.pr.status}})."),
    ],
    "edges": _chain("email", "extract", "find", "pr", "tell"),
}

AGENT = {
    "id": "build-your-own-agent",
    "name": "Build your own agent",
    "description": "Your own agent: write its instructions, tick the tools it may use, pick the person it acts as, "
                   "then chat to it.",
    "nodes": [
        _n("chat", "trigger", "Chat message", 0, kind="chat"),
        _n("desk", "agent", "Stock desk agent", 1, **{"as": "KJOSHI"}, model="gemini:gemini-3.8-flash", may_commit=True,
           max_steps=10, input="{{ trigger.message }}",
           tools=["find_item", "check_stock", "check_budget", "search_policy", "create_purchase_request", "order_status"],
           instructions="You are the stock desk at Rasoi Steel Works. Answer questions about stock, budgets, "
                        "policy and orders with the numbers from the tools, in two or three short sentences. "
                        "When asked to buy something, find the item, check the stock and preview the purchase "
                        "request before raising it."),
    ],
    "edges": _chain("chat", "desk"),
}

TEMPLATES = {t["id"]: t for t in (DIWALI, REORDER, GOODS, DEALER, AGENT)}


def template(tid: str) -> dict:
    return copy.deepcopy(TEMPLATES[tid])


def catalog() -> list[dict]:
    return [{"id": t["id"], "name": t["name"], "description": t["description"], "nodes": len(t["nodes"]),
             "trigger": next(n["config"]["kind"] for n in t["nodes"] if n["type"] == "trigger"),
             "steps": [n["title"] for n in t["nodes"]]} for t in TEMPLATES.values()]
