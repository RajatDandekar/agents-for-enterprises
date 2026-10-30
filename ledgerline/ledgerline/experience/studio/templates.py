"""The Studio's ready-made workflows. Each one runs end to end on a fresh Northbridge (tests/test_engine.py proves it).

    from ledgerline.experience.studio.templates import TEMPLATES, template
    wf = template("spring-battery-order")      # a fresh copy, safe to change
"""
from __future__ import annotations

import copy

GAP = 230  # canvas distance between two columns of nodes


def _n(nid, typ, title, col, row=0, **config):
    return {"id": nid, "type": typ, "title": title, "x": 60 + col * GAP, "y": 200 + row * 170, "config": config}


def _chain(*ids, port=None):
    return [{"from": a, "to": b, **({"port": port} if port else {})} for a, b in zip(ids, ids[1:])]


DIWALI = {
    "id": "spring-battery-order",
    "name": "Spring launch battery order",
    "description": "Emma's 2,000 battery packs for the spring-launch run: check stock, raise the request, wait for Daniel, "
                   "order from Voltway Cells, release it and tell Daniel.",
    "nodes": [
        _n("start", "trigger", "Start", 0, kind="manual"),
        _n("stock", "tool", "Check stock", 1, tool="check_stock", **{"as": "ECLARKE"}, args={"item_code": "BAT-500"}),
        _n("pr", "tool", "Raise the PR", 2, tool="create_purchase_request", **{"as": "ECLARKE"}, confirm=True,
           args={"item_code": "{{nodes.stock.item_code}}", "quantity": 2000, "cost_centre": "PRD-07",
                 "need_by": "2026-11-09"}),
        _n("daniel", "approval", "Daniel approves", 3, doc_no="{{nodes.pr.request_no}}", approver="DOKAFOR"),
        _n("po", "tool", "Order from Voltway", 4, tool="create_purchase_order", **{"as": "ECLARKE"}, confirm=True,
           args={"supplier_code": "VC-EIN-0042", "request_no": "{{nodes.pr.request_no}}"}),
        _n("release", "tool", "Release to supplier", 5, tool="release_purchase_order", **{"as": "ECLARKE"},
           args={"po_no": "{{nodes.po.po_no}}"}),
        _n("tell", "message", "Tell Daniel", 6, to="@daniel", **{"as": "ECLARKE"},
           text="{{nodes.release.po_no}} is {{nodes.release.status}}: 2,000 battery packs from Voltway Cells, "
                "{{ money(nodes.po.gross_value) }} incl. VAT. Thanks for approving {{nodes.pr.request_no}}."),
    ],
    "edges": _chain("start", "stock", "pr", "daniel", "po", "release", "tell"),
}

REORDER = {
    "id": "reorder-when-low",
    "name": "Reorder when low",
    "description": "When an item falls below its reorder level, raise a request for three times the reorder level, "
                   "get it approved, order and release it. If an order is already on the way, only tell Emma.",
    "nodes": [
        _n("low", "trigger", "Stock below reorder level", 0, kind="event", event="stock_below_reorder",
           item_codes=["BAT-500", "BEL-STD-01"], **{"as": "ECLARKE"}),
        _n("plan", "set", "Plan the order", 1, values={
            "quantity": "{{ trigger.reorder_level * 3 }}",
            "supplier": "{{ 'PB-MAN-0017' if trigger.item_code == 'BEL-STD-01' else 'VC-EIN-0042' }}",
            "need_by": "{{ add_days(today, 14) }}"}),
        _n("nothing_on_order", "condition", "Nothing on order yet?", 2, **{"if": "{{ trigger.on_order == 0 }}"}),
        _n("pr", "tool", "Raise the PR", 3, -0.6, tool="create_purchase_request", **{"as": "ECLARKE"}, confirm=True,
           args={"item_code": "{{trigger.item_code}}", "quantity": "{{nodes.plan.quantity}}", "cost_centre": "PRD-07",
                 "need_by": "{{nodes.plan.need_by}}"}),
        _n("note", "message", "Tell Emma", 3, 0.75, to="@emma", **{"as": "ECLARKE"},
           text="{{trigger.item_code}} is below its reorder level, but {{trigger.on_order}} are already on order. "
                "Nothing new raised."),
        _n("daniel", "approval", "Daniel approves", 4, -0.6, doc_no="{{nodes.pr.request_no}}", approver="DOKAFOR"),
        _n("po", "tool", "Create the PO", 5, -0.6, tool="create_purchase_order", **{"as": "ECLARKE"}, confirm=True,
           args={"supplier_code": "{{nodes.plan.supplier}}", "request_no": "{{nodes.pr.request_no}}"}),
        _n("release", "tool", "Release to supplier", 6, -0.6, tool="release_purchase_order", **{"as": "ECLARKE"},
           args={"po_no": "{{nodes.po.po_no}}"}),
        _n("tell", "message", "Tell Daniel", 7, -0.6, to="@daniel", **{"as": "ECLARKE"},
           text="Auto-reorder: {{ num(nodes.po.quantity) }} x {{trigger.item_code}} ordered on {{nodes.release.po_no}} "
                "({{nodes.release.status}})."),
    ],
    "edges": _chain("low", "plan", "nothing_on_order")
    + [{"from": "nothing_on_order", "port": "true", "to": "pr"},
       {"from": "nothing_on_order", "port": "false", "to": "note"}]
    + _chain("pr", "daniel", "po", "release", "tell"),
}

GOODS = {
    "id": "goods-arrived",
    "name": "Goods arrived",
    "description": "Aiko fills a short form at the gate: the order and the count. The workflow records the goods "
                   "receipt as Aiko, reads the order's status back and tells Emma.",
    "nodes": [
        _n("form", "trigger", "Goods at the gate", 0, kind="form", fields=[
            {"name": "po_no", "label": "Purchase order", "type": "text", "default": "PO/2026/01167"},
            {"name": "quantity", "label": "Quantity counted", "type": "number", "default": 40000},
            {"name": "vehicle", "label": "Vehicle number", "type": "text", "default": "MA26 KTX"}]),
        _n("grn", "tool", "Record the receipt", 1, tool="receive_goods", **{"as": "ATANAKA"}, confirm=True,
           args={"po_no": "{{trigger.po_no}}", "quantity": "{{trigger.quantity}}",
                 "remarks": "Vehicle {{trigger.vehicle}}"}),
        _n("status", "tool", "Order status", 2, tool="order_status", **{"as": "ECLARKE"},
           args={"po_no": "{{nodes.grn.po_no}}"}),
        _n("tell", "message", "Tell Emma", 3, to="@emma", **{"as": "DOKAFOR"},
           text="Aiko received {{ num(nodes.grn.received) }} on {{nodes.grn.po_no}} ({{nodes.grn.grn_no}}). "
                "Order: {{nodes.status.status}}; {{ num(nodes.grn.balance) }} still to come. Stock now {{ num(nodes.grn.stock_after) }}."),
    ],
    "edges": _chain("form", "grn", "status", "tell"),
}

DEALER_EMAIL = """Subject: Spare battery packs before the spring launch

Dear Northbridge team,

Our workshop in Bristol is running short of spares. Please send us 400 battery packs for your
city e-bike. We need them at our warehouse by 12 November, before the spring orders start.

Regards,
Tom Hartley
Hartley Cycles, Bristol"""

DEALER = {
    "id": "dealer-email-to-order",
    "name": "Bike shop email to order",
    "description": "A bike shop's email, read by an LLM node: it pulls out the item, quantity and date, finds the item "
                   "in Ledgerline and raises the purchase request.",
    "nodes": [
        _n("email", "trigger", "Dealer email", 0, kind="manual", data={"email": DEALER_EMAIL}),
        _n("extract", "llm", "Read the email", 1, output="json", fields=["item", "quantity", "need_by", "dealer"],
           model="gemini:gemini-3.8-flash",
           prompt="A bike shop has written to Northbridge Cycles, Manchester. Today is {{today}}.\n"
                  "Read the email and pull out what they need.\n"
                  "item: the part in 3 to 5 plain words (size, material, part name); quantity: a whole number; "
                  "need_by: the date as YYYY-MM-DD; dealer: the shop's company name.\n\nEmail:\n{{trigger.email}}"),
        _n("find", "tool", "Find the item", 2, tool="find_item", **{"as": "ECLARKE"},
           args={"query": "{{nodes.extract.item}}"}),
        _n("pr", "tool", "Raise the PR", 3, tool="create_purchase_request", **{"as": "ECLARKE"}, confirm=True,
           args={"item_code": "{{nodes.find.items[0].item_code}}", "quantity": "{{nodes.extract.quantity}}",
                 "cost_centre": "PRD-07", "need_by": "{{nodes.extract.need_by}}"}),
        _n("tell", "message", "Tell Daniel", 4, to="@daniel", **{"as": "ECLARKE"},
           text="{{nodes.extract.dealer}} asked for {{ num(nodes.extract.quantity) }} x {{nodes.find.items[0].description}} "
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
        _n("desk", "agent", "Stock desk agent", 1, **{"as": "ECLARKE"}, model="gemini:gemini-3.8-flash", may_commit=True,
           max_steps=10, input="{{ trigger.message }}",
           tools=["find_item", "check_stock", "check_budget", "search_policy", "create_purchase_request", "order_status"],
           instructions="You are the stock desk at Northbridge Cycles. Answer questions about stock, budgets, "
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
