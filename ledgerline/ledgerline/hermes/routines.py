"""The five starter prompts of the workflow builder, and a hand-built routine for each (Lecture 5).

The hand-built ones are the class's reference: tests run them on a fresh sandbox, the finale offers them as
"Northbridge routines" when a student has saved none of their own, and the triggers use INVOICE_ONE for an invoice
e-mail. The builder (builder.py) drafts its own from the prompt; the deck compares the two.
"""
from __future__ import annotations

import copy

from .engine import layout

STARTERS = [
    {"id": "chase", "title": "Chase late orders", "icon": "clock",
     "prompt": "Every Monday at 9, find my orders that are 7 or more days late, write each supplier a short polite "
               "e-mail asking for a delivery date, and tell me which ones were chased."},
    {"id": "reorder", "title": "Reorder when low", "icon": "box",
     "prompt": "Every morning, find items below their reorder level and raise a purchase request for three times the "
               "reorder level on the spring launch cost centre PRD-07, needed in two weeks. Wait for the approvals, "
               "then tell me."},
    {"id": "invoices", "title": "Process this week's invoices", "icon": "receipt",
     "prompt": "Every Friday, take the new invoices in the AP inbox, read each one, record it, match it to its order "
               "and goods receipt, post the ones that match within 2% and hold the rest with the reason. Then tell "
               "Luis the totals."},
    {"id": "onboard", "title": "Onboard a supplier", "icon": "badge",
     "prompt": "When I fill in a new supplier's name, city, country, VAT number and certificate expiry date, check "
               "they are not already in Ledgerline, register them, and if their UN 38.3 certificate has less than "
               "60 days left, tell Luis to chase a new one; otherwise tell Luis to file it."},
    {"id": "spend", "title": "Monthly spend report", "icon": "chart",
     "prompt": "On the first of every month, look up the budget left on every open cost centre and send Daniel a "
               "short spend report."},
]


def _n(nid, typ, title, **config):
    return {"id": nid, "type": typ, "title": title, "config": config}


def _chain(*ids):
    return [{"from": a, "to": b} for a, b in zip(ids, ids[1:])]


CHASE = {
    "id": "chase", "name": "Chase late orders", "description": "Every Monday: e-mail the supplier of each order 7 or more "
    "days late, then tell Emma which ones were chased.",
    "params": [{"name": "days_late", "label": "Days late (at least)", "type": "number", "default": 7,
                "help": "Orders this many days or more past their need-by date"},
               {"name": "buyer", "label": "Buyer", "type": "person", "default": "ECLARKE", "help": "Whose orders"},
               {"name": "channel", "label": "How to chase", "type": "choice", "default": "draft", "options": ["draft", "email"],
                "help": "e-mail the supplier now, or save drafts for Emma to send"}],
    "nodes": [
        _n("start", "trigger", "Every Monday 09:00", kind="schedule", every="week", day="Mon", at="09:00"),
        _n("orders", "tool", "Find late orders", tool="list_open_orders", args={"min_days_late": "{{params.days_late}}",
                                                                                "buyer": "{{params.buyer}}"}),
        _n("any", "condition", "Any late?", **{"if": "{{ nodes.orders.count > 0 }}"}),
        _n("each", "foreach", "For each late order", items="{{nodes.orders.orders}}", label="{{item.po_no}} · {{item.supplier_name}}",
           parallel=6, steps=[
               {"id": "write", "type": "llm", "title": "Write the e-mail", "config": {"output": "text", "prompt":
                "Write a short, polite e-mail (under 80 words, no subject line) to {{item.supplier_name}} chasing our order "
                "{{item.po_no}}: {{ num(item.outstanding) }} of {{ num(item.ordered) }} x {{item.item_code}} "
                "({{item.description}}), due {{ date(item.need_by) }}, now {{item.days_late}} days late. Ask for a firm "
                "delivery date. Sign it: Emma Clarke, Purchasing, Northbridge Cycles."}},
               {"id": "send", "type": "message", "title": "E-mail the supplier", "when": "{{ params.channel == 'email' }}",
                "outcome": "e-mailed", "config": {"to": "{{item.supplier_email}}", "text": "{{steps.write.text}}"}},
               {"id": "draft", "type": "tool", "title": "Save a draft", "when": "{{ params.channel == 'draft' }}",
                "outcome": "drafted", "config": {"tool": "draft_message", "args": {"to": "{{item.supplier_email}}",
                "subject": "Late order {{item.po_no}}", "text": "{{steps.write.text}}", "ref": "{{item.po_no}}"}}}]),
        _n("tell", "message", "Tell Emma", to="@emma", text="Monday chase: {{ tally(nodes.each.tally) }} "
           "({{ join(pluck(nodes.orders.orders, 'po_no')) }})."),
        _n("none", "message", "Nothing late", to="@emma", text="Monday chase: no orders {{params.days_late}} or more days late."),
    ],
    "edges": _chain("start", "orders", "any") + [{"from": "any", "port": "true", "to": "each"},
                                                 {"from": "any", "port": "false", "to": "none"}] + _chain("each", "tell"),
}

REORDER = {
    "id": "reorder", "name": "Reorder when low", "description": "Every morning: a purchase request for each item below "
    "its reorder level, wait for the approvals, tell Emma.",
    "params": [{"name": "multiple", "label": "Order this many × the reorder level", "type": "number", "default": 3},
               {"name": "cost_centre", "label": "Cost centre", "type": "text", "default": "PRD-07"},
               {"name": "need_in_days", "label": "Needed in (days)", "type": "number", "default": 14}],
    "nodes": [
        _n("start", "trigger", "Every day 07:00", kind="schedule", every="day", at="07:00"),
        _n("low", "tool", "Find low stock", tool="low_stock", args={}),
        _n("each", "foreach", "For each low item", items="{{nodes.low.items}}", label="{{item.item_code}}", parallel=4, steps=[
            {"id": "pr", "type": "tool", "title": "Raise the request", "outcome": "requested",
             "config": {"tool": "create_purchase_request", "confirm": True, "args": {
                 "item_code": "{{item.item_code}}", "quantity": "{{ item.reorder_level * params.multiple }}",
                 "cost_centre": "{{params.cost_centre}}", "need_by": "{{ add_days(today, params.need_in_days) }}"}}}]),
        _n("wait", "approval", "Approvals", doc_no="{{ pluck(pluck(nodes.each.results, 'pr'), 'request_no') }}", approver="DOKAFOR"),
        _n("tell", "message", "Tell Emma", to="@emma", text="Reorder: {{ tally(nodes.each.tally) }}; "
           "{{nodes.wait.approved}} approved and ready to order."),
    ],
    "edges": _chain("start", "low", "each", "wait", "tell"),
}

READ_PROMPT = ("Read this supplier invoice e-mail and give its fields exactly as printed. invoice_date as YYYY-MM-DD; "
               "quantity as a whole number; unit_price and vat as numbers in pounds (vat 0 if reverse charge); po_no as "
               "written (e.g. PO/2026/01133), or null if there is none.\n\nFrom: {{item.sender}}\nSubject: {{item.subject}}\n\n{{item.body}}")
INV_FIELDS = ["supplier", "supplier_invoice_no", "invoice_date", "po_no", "item_code", "quantity", "unit_price", "vat"]


def _invoice_steps(src="item"):
    return [
        {"id": "read", "type": "llm", "title": "Read the invoice", "config": {"output": "json", "fields": INV_FIELDS,
                                                                            "prompt": READ_PROMPT.replace("item.", src + ".")}},
        {"id": "record", "type": "tool", "title": "Record it", "config": {"tool": "record_invoice", "as": "LMORENO", "confirm": True,
         "args": {"supplier": "{{steps.read.supplier}}", "supplier_invoice_no": "{{steps.read.supplier_invoice_no}}",
                  "invoice_date": "{{steps.read.invoice_date}}", "po_no": "{{steps.read.po_no}}",
                  "item_code": "{{steps.read.item_code}}", "quantity": "{{steps.read.quantity}}",
                  "unit_price": "{{steps.read.unit_price}}", "vat": "{{steps.read.vat}}",
                  "source_message_id": "{{%s.message_id}}" % src}}},
        {"id": "match", "type": "tool", "title": "Three-way match", "config": {"tool": "match_invoice", "as": "LMORENO",
         "args": {"invoice_no": "{{steps.record.invoice_no}}", "price_tolerance_pct": "{{params.tolerance_pct}}"}}},
        {"id": "post", "type": "tool", "title": "Post it", "when": "{{ steps.match.matched }}", "outcome": "posted",
         "config": {"tool": "post_invoice", "as": "LMORENO", "confirm": True, "args": {"invoice_no": "{{steps.record.invoice_no}}"}}},
        {"id": "hold", "type": "tool", "title": "Hold it", "when": "{{ not steps.match.matched }}", "outcome": "held",
         "config": {"tool": "hold_invoice", "as": "LMORENO", "args": {"invoice_no": "{{steps.record.invoice_no}}",
                                                                      "reason": "{{steps.match.note}}"}}},
    ]


INVOICES = {
    "id": "invoices", "name": "Process this week's invoices", "description": "Every Friday: read, record, three-way match, "
    "post or hold every new invoice in the AP inbox; tell Luis the totals.",
    "params": [{"name": "folder", "label": "Mailbox", "type": "choice", "default": "AP inbox", "options": ["AP inbox"]},
               {"name": "tolerance_pct", "label": "Price tolerance (%)", "type": "number", "default": 2,
                "help": "how far above the order price an invoice may be (policy cap 5%)"},
               {"name": "tell", "label": "Tell", "type": "text", "default": "@luis"}],
    "nodes": [
        _n("start", "trigger", "Every Friday 09:00", kind="schedule", every="week", day="Fri", at="09:00"),
        _n("inbox", "tool", "New invoices", tool="read_mailbox", **{"as": "LMORENO"},
           args={"folder": "{{params.folder}}", "status": "new", "limit": 50}),
        _n("each", "foreach", "For each invoice", items="{{nodes.inbox.messages}}", label="{{item.subject}}", parallel=8,
           steps=_invoice_steps()),
        _n("tell", "message", "Tell Luis", to="{{params.tell}}", **{"as": "LMORENO"},
           text="This week's invoices: {{ tally(nodes.each.tally) }} (of {{nodes.each.count}}). Held ones need a look."),
    ],
    "edges": _chain("start", "inbox", "each", "tell"),
}

ONBOARD = {
    "id": "onboard", "name": "Onboard a supplier", "description": "A form: check the supplier is new, register them, check "
    "how long their UN 38.3 certificate has left, and tell Luis.",
    "params": [{"name": "min_cert_days", "label": "Certificate must have at least (days)", "type": "number", "default": 60}],
    "nodes": [
        _n("start", "trigger", "New supplier form", kind="form", fields=[
            {"name": "name", "label": "Supplier name", "type": "text", "default": "Brightcell Energy"},
            {"name": "city", "label": "City", "type": "text", "default": "Lyon"},
            {"name": "country", "label": "Country (2 letters)", "type": "text", "default": "FR"},
            {"name": "vat_no", "label": "VAT number", "type": "text", "default": "FR40852941736"},
            {"name": "cert_valid_to", "label": "UN 38.3 valid to", "type": "date", "default": "2026-12-10"}]),
        _n("find", "tool", "Already in Ledgerline?", tool="find_supplier", args={"name": "{{trigger.name}}", "city": "{{trigger.city}}"}),
        _n("new", "condition", "New supplier?", **{"if": "{{ count(nodes.find.matches) == 0 }}"}),
        _n("register", "tool", "Register them", tool="register_supplier", confirm=True, args={
            "name": "{{trigger.name}}", "city": "{{trigger.city}}", "state": "{{trigger.country}}", "vat_no": "{{trigger.vat_no}}"}),
        _n("days", "set", "Certificate days left", values={"days": "{{ days_between(today, trigger.cert_valid_to) }}"}),
        _n("enough", "condition", "Enough days left?", **{"if": "{{ nodes.days.days >= params.min_cert_days }}"}),
        _n("file", "message", "Tell Luis: file it", to="@luis", text="New supplier {{trigger.name}} ({{nodes.register.supplier_code}}) "
           "registered. UN 38.3 valid to {{ date(trigger.cert_valid_to) }} ({{nodes.days.days}} days): please file the certificate."),
        _n("chase", "message", "Tell Luis: chase it", to="@luis", text="New supplier {{trigger.name}} "
           "({{nodes.register.supplier_code}}) registered, but their UN 38.3 certificate has only {{nodes.days.days}} days left "
           "(policy wants {{params.min_cert_days}}). Please ask them for the renewed one before we order."),
        _n("exists", "message", "Already there", to="@emma", text="{{trigger.name}} may already be in Ledgerline: "
           "{{ join(pluck(nodes.find.matches, 'name')) }}. Nothing registered."),
    ],
    "edges": _chain("start", "find", "new") + [{"from": "new", "port": "true", "to": "register"},
                                               {"from": "new", "port": "false", "to": "exists"}] + _chain("register", "days", "enough")
    + [{"from": "enough", "port": "true", "to": "file"}, {"from": "enough", "port": "false", "to": "chase"}],
}

SPEND = {
    "id": "spend", "name": "Monthly spend report", "description": "On the 1st: budget left on every open cost centre, "
    "written up for Daniel.",
    "params": [{"name": "to", "label": "Send to", "type": "text", "default": "@daniel"}],
    "nodes": [
        _n("start", "trigger", "1st of the month 09:00", kind="schedule", every="month", day_of_month=1, at="09:00"),
        _n("ccs", "tool", "Open cost centres", tool="check_budget", args={}),
        _n("each", "foreach", "For each cost centre", items="{{nodes.ccs.open}}", label="{{item.code}}", parallel=5, steps=[
            {"id": "b", "type": "tool", "title": "Budget left", "outcome": "checked",
             "config": {"tool": "check_budget", "args": {"cost_centre": "{{item.code}}"}}}]),
        _n("write", "llm", "Write the report", output="text", prompt="Write Daniel Okafor a short monthly spend report "
           "(at most 6 lines, plain text, money like £1,190,000) from these budget figures for this quarter: "
           "{{ pluck(nodes.each.results, 'b') }}. Name the cost centre with the least left."),
        _n("send", "message", "Send to Daniel", to="{{params.to}}", text="{{nodes.write.text}}"),
    ],
    "edges": _chain("start", "ccs", "each", "write", "send"),
}

INVOICE_ONE = {
    "id": "invoice-one", "name": "Process one invoice", "description": "An invoice e-mail arrived: read it, record it, "
    "match it, post or hold it, and tell AP.",
    "params": [{"name": "tolerance_pct", "label": "Price tolerance (%)", "type": "number", "default": 2}],
    "nodes": [
        _n("start", "trigger", "Invoice e-mail arrives", kind="event", event="invoice_email"),
        _n("one", "foreach", "This invoice", items="{{ [trigger.message] }}", label="{{item.subject}}", parallel=1,
           steps=_invoice_steps()),
        _n("tell", "message", "Tell Luis", to="@luis", **{"as": "LMORENO"},
           text="Invoice from {{trigger.message.sender}}: {{ tally(nodes.one.tally) }}."),
    ],
    "edges": _chain("start", "one", "tell"),
}

CANNED = {w["id"]: w for w in (CHASE, REORDER, INVOICES, ONBOARD, SPEND)}


def canned(rid: str) -> dict:
    return layout(copy.deepcopy(CANNED[rid]))


def invoice_one() -> dict:
    return layout(copy.deepcopy(INVOICE_ONE))


GRN_MATCH = {
    "id": "grn-match", "name": "Goods arrived: match and tell", "description": "Stores posted a goods receipt: match that "
    "order's invoices, post the ones that now agree, tell the buyer.",
    "params": [{"name": "tolerance_pct", "label": "Price tolerance (%)", "type": "number", "default": 2}],
    "nodes": [
        _n("start", "trigger", "Goods receipt posted", kind="event", event="goods_receipt"),
        _n("invs", "tool", "Invoices for this order", tool="list_invoices", **{"as": "LMORENO"}, args={"po_no": "{{trigger.po_no}}"}),
        _n("each", "foreach", "For each invoice", items="{{nodes.invs.invoices}}", label="{{item.invoice_no}}", parallel=2, steps=[
            {"id": "match", "type": "tool", "title": "Three-way match", "config": {"tool": "match_invoice", "as": "LMORENO",
             "args": {"invoice_no": "{{item.invoice_no}}", "price_tolerance_pct": "{{params.tolerance_pct}}"}}},
            {"id": "post", "type": "tool", "title": "Post it", "when": "{{ steps.match.matched }}", "outcome": "posted",
             "config": {"tool": "post_invoice", "as": "LMORENO", "confirm": True, "args": {"invoice_no": "{{item.invoice_no}}"}}},
            {"id": "keep", "type": "set", "title": "Still held", "when": "{{ not steps.match.matched }}", "outcome": "still held",
             "config": {"values": {"why": "{{steps.match.note}}"}}}]),
        _n("tell", "message", "Tell the buyer", to="{{trigger.buyer_handle}}", **{"as": "LMORENO"},
           text="Goods arrived for {{trigger.po_no}} ({{ num(trigger.quantity) }} x {{trigger.item_code}}, {{trigger.grn_no}}). "
                "Invoices: {{ tally(nodes.each.tally) }}."),
    ],
    "edges": _chain("start", "invs", "each", "tell"),
}


def grn_match() -> dict:
    return layout(copy.deepcopy(GRN_MATCH))
