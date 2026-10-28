"""Write the two n8n workflows for the Lecture 1 lab (standard library only, safe to run anywhere).

    python3 lectures/L1-the-form/n8n/build_workflows.py
-> bahi_happy_path.json        login -> pr_save -> pr_submit -> po_fetch -> po_save -> po_release
-> bahi_variants_solution.json the exercise solution: closed cost centre, direct vs request, approval
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
X = 0


def _id(name):
    return "bahi-" + "".join(c.lower() if c.isalnum() else "-" for c in name)


def trigger():
    return {"parameters": {}, "id": _id("start"), "name": "Start", "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1, "position": [0, 300]}


def order_node(pos, **vals):
    a = [{"id": f"o{i}", "name": k, "value": v, "type": "number" if isinstance(v, (int, float)) else "string"}
         for i, (k, v) in enumerate(vals.items())]
    return {"parameters": {"assignments": {"assignments": a}, "options": {}}, "id": _id("order"), "name": "Order",
            "type": "n8n-nodes-base.set", "typeVersion": 3.4, "position": pos,
            "notes": "Edit these values. bahi_url: http://127.0.0.1:8077 if n8n runs on your machine, "
                     "http://host.docker.internal:8077 if n8n runs in Docker."}


O = "$('Order').item.json"


def login(name, user, pw, pos):
    return {"parameters": {"method": "POST", "url": f"={{{{ {O}.bahi_url }}}}/login", "sendBody": True,
                           "specifyBody": "json",
                           "jsonBody": "={\n  \"user_id\": \"" + user + "\",\n  \"password\": \"" + pw + "\"\n}",
                           "options": {}},
            "id": _id(name), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": pos}


def svc(name, service, screen, task, body: dict, token_from: str, pos):
    """An HTTP Request node calling one Bahi service. body values are n8n expressions or literals."""
    lines = []
    for k, v in body.items():
        if isinstance(v, str) and v.startswith("expr:"):
            lines.append(f'  "{k}": "{{{{ {v[5:]} }}}}"')
        elif isinstance(v, str) and v.startswith("num:"):
            lines.append(f'  "{k}": {{{{ {v[4:]} }}}}')
        else:
            lines.append(f'  "{k}": {json.dumps(v)}')
    return {"parameters": {"method": "POST", "url": f"={{{{ {O}.bahi_url }}}}/svc/{service}", "sendHeaders": True,
                           "headerParameters": {"parameters": [
                               {"name": "Authorization", "value": f"=Bearer {{{{ $('{token_from}').item.json.token }}}}"},
                               {"name": "X-Screen", "value": screen}, {"name": "X-Task", "value": task}]},
                           "sendBody": True, "specifyBody": "json", "jsonBody": "={\n" + ",\n".join(lines) + "\n}",
                           "options": {}},
            "id": _id(name), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": pos}


def if_node(name, left, op_type, op, right, pos):
    return {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                                          "conditions": [{"id": _id(name) + "-c", "leftValue": f"={{{{ {left} }}}}",
                                                          "rightValue": right,
                                                          "operator": {"type": op_type, "operation": op}}],
                                          "combinator": "and"}, "options": {}},
            "id": _id(name), "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2, "position": pos}


def result(name, pos, **vals):
    a = [{"id": f"r{i}", "name": k, "value": v, "type": "string"} for i, (k, v) in enumerate(vals.items())]
    return {"parameters": {"assignments": {"assignments": a}, "options": {}}, "id": _id(name), "name": name,
            "type": "n8n-nodes-base.set", "typeVersion": 3.4, "position": pos}


def noop(name, pos):
    return {"parameters": {}, "id": _id(name), "name": name, "type": "n8n-nodes-base.noOp", "typeVersion": 1, "position": pos}


def chain(conns, *names):
    for a, b in zip(names, names[1:]):
        conns.setdefault(a, {"main": [[]]})["main"][0].append({"node": b, "type": "main", "index": 0})


def branch(conns, ifname, true_to, false_to):
    conns[ifname] = {"main": [[{"node": true_to, "type": "main", "index": 0}],
                              [{"node": false_to, "type": "main", "index": 0}]]}


def workflow(name, nodes, conns, wid):
    return {"name": name, "id": wid, "nodes": nodes, "connections": conns, "active": False, "settings": {"executionOrder": "v1"},
            "pinData": {}, "meta": {"templateCredsSetupCompleted": True},
            "tags": []}


ORDER = dict(bahi_url="http://127.0.0.1:8077", itm_cd="GSK-SIL-05L", qty=15000, need_dt="2026-11-02", cc_cd="PRD-07",
             sup_cd="DP-RJK-0042", tax_cd="GST18-INTER", whs_cd="WH-PUN-STR")

PR_SAVE = {"pr_type": "STD", "cc_cd": f"expr:{O}.cc_cd", "need_dt": f"expr:{O}.need_dt", "itm_cd": f"expr:{O}.itm_cd",
           "qty": f"num:{O}.qty", "whs_cd": f"expr:{O}.whs_cd", "remarks": "n8n workflow"}


def po_save_body(po_type, pr_from=None, fetch="PO Fetch"):
    b = {"po_type": po_type}
    if pr_from:
        b["pr_no"] = f"expr:$('{pr_from}').item.json.data.pr_no"
    b.update({"sup_cd": f"expr:{O}.sup_cd", "itm_cd": f"expr:{O}.itm_cd", "qty": f"num:{O}.qty",
              "rate": f"num:$('{fetch}').item.json.data.rate", "tax_cd": f"expr:{O}.tax_cd",
              "cc_cd": f"expr:{O}.cc_cd", "need_dt": f"expr:{O}.need_dt", "whs_cd": f"expr:{O}.whs_cd",
              "fetch_tok": f"expr:$('{fetch}').item.json.data.fetch_tok"})
    return b


# ------------------------------------------------------------------ the happy path
nodes, conns = [trigger(), order_node([220, 300], **ORDER)], {}
nodes += [
    login("Login Kavita", "KJOSHI", "kavita@123", [440, 300]),
    svc("PR Save", "pr_save", "PUR-PR-01", "Save", PR_SAVE, "Login Kavita", [660, 300]),
    svc("PR Submit", "pr_submit", "PUR-PR-01", "Submit", {"pr_no": "expr:$('PR Save').item.json.data.pr_no"}, "Login Kavita", [880, 300]),
    svc("PO Fetch", "po_fetch", "PUR-PO-01", "Fetch",
        {"sup_cd": f"expr:{O}.sup_cd", "itm_cd": f"expr:{O}.itm_cd", "pr_no": "expr:$('PR Save').item.json.data.pr_no"},
        "Login Kavita", [1100, 300]),
    svc("PO Save", "po_save", "PUR-PO-01", "Save", po_save_body("STD", "PR Save"), "Login Kavita", [1320, 300]),
    svc("PO Release", "po_release", "PUR-POR-05", "Release", {"po_no": "expr:$('PO Save').item.json.data.doc_no"},
        "Login Kavita", [1540, 300]),
]
chain(conns, "Start", "Order", "Login Kavita", "PR Save", "PR Submit", "PO Fetch", "PO Save", "PO Release")
happy = workflow("Bahi · Kavita's reorder, happy path (Lecture 1 lab)", nodes, conns, "BahiL1HappyPath1")
(HERE / "bahi_happy_path.json").write_text(json.dumps(happy, indent=2, ensure_ascii=False))

# ------------------------------------------------------------------ the exercise solution: three variants
nodes, conns = [trigger(), order_node([220, 300], **ORDER)], {}
nodes += [
    login("Login Kavita", "KJOSHI", "kavita@123", [440, 300]),
    svc("Check Cost Centre", "cc_get", "PUR-PO-01", "F2 cc_cd", {"cc_cd": f"expr:{O}.cc_cd"}, "Login Kavita", [660, 300]),
    if_node("Cost centre open?", "$json.data.status", "string", "equals", "OPEN", [880, 300]),
    result("Stop: cost centre closed", [1100, 520], outcome="STOPPED", reason="cost centre is closed; a person must choose another"),
    svc("Rate Fetch", "po_fetch", "PUR-PO-01", "Fetch", {"sup_cd": f"expr:{O}.sup_cd", "itm_cd": f"expr:{O}.itm_cd"},
        "Login Kavita", [1100, 200]),
    if_node("Direct order (≤ ₹50,000)?", f"{O}.qty * $('Rate Fetch').item.json.data.rate * 1.18", "number", "lte", 50000, [1320, 200]),
    svc("PO Save (direct)", "po_save", "PUR-PO-01", "Save", po_save_body("DIR", None, "Rate Fetch"), "Login Kavita", [1540, 60]),
    svc("PO Release (direct)", "po_release", "PUR-POR-05", "Release",
        {"po_no": "expr:$('PO Save (direct)').item.json.data.doc_no"}, "Login Kavita", [1760, 60]),
    svc("PR Save", "pr_save", "PUR-PR-01", "Save", PR_SAVE, "Login Kavita", [1540, 320]),
    svc("PR Submit", "pr_submit", "PUR-PR-01", "Submit", {"pr_no": "expr:$('PR Save').item.json.data.pr_no"}, "Login Kavita", [1760, 320]),
    if_node("Needs approval?", "$json.data.status", "string", "equals", "PA", [1980, 320]),
    login("Login Rohit", "RMEHTA", "rohit@123", [2200, 220]),
    svc("PR Approve (Rohit)", "pr_approve", "PUR-PR-04", "Confirm",
        {"pr_no": "expr:$('PR Save').item.json.data.pr_no", "decision": "A", "comment": "approved in n8n lab"},
        "Login Rohit", [2420, 220]),
    noop("Request approved", [2640, 340]),
    svc("PO Fetch", "po_fetch", "PUR-PO-01", "Fetch",
        {"sup_cd": f"expr:{O}.sup_cd", "itm_cd": f"expr:{O}.itm_cd", "pr_no": "expr:$('PR Save').item.json.data.pr_no"},
        "Login Kavita", [2860, 340]),
    svc("PO Save", "po_save", "PUR-PO-01", "Save", po_save_body("STD", "PR Save"), "Login Kavita", [3080, 340]),
    svc("PO Release", "po_release", "PUR-POR-05", "Release", {"po_no": "expr:$('PO Save').item.json.data.doc_no"},
        "Login Kavita", [3300, 340]),
]
chain(conns, "Start", "Order", "Login Kavita", "Check Cost Centre", "Cost centre open?")
branch(conns, "Cost centre open?", "Rate Fetch", "Stop: cost centre closed")
chain(conns, "Rate Fetch", "Direct order (≤ ₹50,000)?")
branch(conns, "Direct order (≤ ₹50,000)?", "PO Save (direct)", "PR Save")
chain(conns, "PO Save (direct)", "PO Release (direct)")
chain(conns, "PR Save", "PR Submit", "Needs approval?")
branch(conns, "Needs approval?", "Login Rohit", "Request approved")
chain(conns, "Login Rohit", "PR Approve (Rohit)", "Request approved", "PO Fetch", "PO Save", "PO Release")
sol = workflow("Bahi · reorder with three variants (Lecture 1 lab, solution)", nodes, conns, "BahiL1Variants01")
(HERE / "bahi_variants_solution.json").write_text(json.dumps(sol, indent=2, ensure_ascii=False))
print("wrote", [p.name for p in HERE.glob("*.json")])
