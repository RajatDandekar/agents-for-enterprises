"""Check the two n8n workflows against Bahi, and count the branches honestly.

This is a small interpreter for the four n8n node types the lab uses (manual trigger, Set, HTTP Request, IF,
No-op). It walks the workflow's connections, evaluates the {{ }} expressions, and sends each HTTP Request to a
fresh Bahi server, so we know the JSON a student imports makes the calls it claims to make.
(n8n itself is a Node.js app; n8n_real.py runs the real thing.)

    modal run tools/modal_run.py --script lectures/L1-the-form/n8n/check_workflows.py
-> ../experiments/logs/n8n_check.json
"""
import itertools
import json
import pathlib
import re

from fastapi.testclient import TestClient

from bahi.server import create_app

HERE = pathlib.Path(__file__).parent
LOGS = HERE.parent / "experiments" / "logs"


def run(wf: dict, order: dict) -> dict:
    """Execute a workflow once against a fresh Bahi. Returns the node path, each call's reply, and the end state."""
    app = create_app()
    http = TestClient(app)
    nodes = {n["name"]: n for n in wf["nodes"]}
    out: dict[str, dict] = {}
    path, calls, stopped, nulls = [], [], [], []

    def ev(expr: str, cur: dict):
        def node_ref(m):
            return f"_n({m.group(1)!r})"
        e = re.sub(r"\$\('([^']+)'\)\.item\.json", node_ref, expr)
        e = e.replace("$json", "_cur").replace("===", "==").replace("&&", " and ").replace("||", " or ")
        e = re.sub(r"\.([A-Za-z_][A-Za-z0-9_]*)", r"['\1']", e)
        try:
            return eval(e, {"__builtins__": {}}, {"_n": lambda k: out[k], "_cur": cur})
        except TypeError:  # a field of a null reply: real n8n 1.64 renders it empty and carries on (see n8n_real.json)
            nulls.append(expr)
            return ""

    def render(s, cur):
        if not isinstance(s, str) or not s.startswith("="):
            return s
        return re.sub(r"\{\{\s*(.*?)\s*\}\}", lambda m: str(ev(m.group(1), cur)), s[1:])

    def execute(name, cur):
        n = nodes[name]
        t = n["type"].split(".")[-1]
        path.append(name)
        nxt = 0
        if t == "manualTrigger":
            res = {}
        elif t == "set":
            res = {a["name"]: (order.get(a["name"], a["value"]) if name == "Order" else render(a["value"], cur))
                   for a in n["parameters"]["assignments"]["assignments"]}
        elif t == "noOp":
            res = cur
        elif t == "httpRequest":
            p = n["parameters"]
            url = render(p["url"], cur)
            hdr = {h["name"]: render(h["value"], cur) for h in p.get("headerParameters", {}).get("parameters", [])}
            try:
                body = json.loads(render(p["jsonBody"], cur))
            except TypeError as e:  # n8n: "Cannot read properties of null", the node fails and the run stops
                calls.append({"node": name, "expression_error": f"{e} (a field of an earlier reply is null)"})
                stopped.append(name)
                return
            r = http.post(url.replace(order["bahi_url"], ""), json=body, headers=hdr)
            res = r.json()
            calls.append({"node": name, "url": url.replace(order["bahi_url"], ""), "body": body, "http": r.status_code,
                          "rc": res.get("rc"), "err_cd": res.get("err_cd"), "msg": res.get("msg"),
                          "data": res.get("data") if not isinstance(res.get("data"), dict) or "rows" not in res["data"] else "rows"})
        elif t == "if":
            c = n["parameters"]["conditions"]["conditions"][0]
            left = ev(c["leftValue"][1:].strip()[2:-2].strip(), cur)
            op, right = c["operator"]["operation"], c["rightValue"]
            ok = left == right if op == "equals" else {"lte": float.__le__, "gt": float.__gt__, "lt": float.__lt__,
                                                         "gte": float.__ge__}[op](float(left), float(right))
            res, nxt = cur, (0 if ok else 1)
            path[-1] = f"{name} → {'true' if ok else 'false'}"
        else:
            raise ValueError(t)
        out[name] = res
        for c in (wf["connections"].get(name, {}).get("main", [[]])[nxt] if wf["connections"].get(name) else []):
            execute(c["node"], res)

    execute("Start", {})
    erp = app.state.tenants["default"]
    po = erp.orders()[0]
    new_po = po if po["created_on"] >= "2026-10-26" else None
    return {"path": path, "calls": calls, "po": {k: new_po[k] for k in ("po_no", "po_type", "status", "gross_value", "cc_cd")} if new_po else None,
            "errors_seen_by_bahi": [c for c in calls if c.get("rc") == "E"],
            "workflow_failed_at": stopped[0] if stopped else None, "empty_expressions": nulls}


wf_happy = json.loads((HERE / "bahi_happy_path.json").read_text())
wf_sol = json.loads((HERE / "bahi_variants_solution.json").read_text())
base = {a["name"]: a["value"] for a in next(n for n in wf_happy["nodes"] if n["name"] == "Order")["parameters"]["assignments"]["assignments"]}
res = {"happy_path": {}, "solution": [], "counts": {}}

# 1. The happy path as shipped (15,000 gaskets, PRD-07): released, no approval needed.
r = run(wf_happy, base)
res["happy_path"]["as_shipped"] = r
print("happy path, 15,000:", r["po"], "errors:", [(c["node"], c["err_cd"]) for c in r["errors_seen_by_bahi"]])

# 2. The same workflow on Kavita's real order (20,000): above her limit. Every node still returns HTTP 200.
r = run(wf_happy, {**base, "qty": 20000})
res["happy_path"]["kavita_20000"] = r
print("happy path, 20,000:", r["po"], "HTTP codes:", [c.get("http") for c in r["calls"]], "empty expressions:", r["empty_expressions"],
      "Bahi errors:", [(c["node"], c["err_cd"], c["msg"]) for c in r["errors_seen_by_bahi"]])

# 3. The solution on every combination of the three variants.
REAL = {  # how to make each combination happen in the sandbox
    "direct": {True: 3000, False: None},                     # 3,000 x 11.90 x 1.18 = 42,126 <= 50,000
    "approval": {True: 20000, False: 15000},                  # request est. 20,000 x 11.40 x 1.18 = 2,69,040 > 2,50,000
    "closed": {True: "PRD-05", False: "PRD-07"},
}
paths = {}
for direct, approval, closed in itertools.product([False, True], repeat=3):
    combo = {"direct": direct, "needs_approval": approval, "cost_centre_closed": closed}
    feasible = not (direct and approval)  # a direct order is at most ₹50,000, always within Kavita's ₹2,50,000
    row = {"combo": combo, "feasible": feasible}
    if feasible:
        qty = REAL["direct"][True] if direct else REAL["approval"][approval]
        r = run(wf_sol, {**base, "qty": qty, "cc_cd": REAL["closed"][closed]})
        row.update(qty=qty, path=r["path"], po=r["po"], bahi_errors=[(c["node"], c["err_cd"]) for c in r["errors_seen_by_bahi"]])
        paths.setdefault(" | ".join(r["path"]), []).append(combo)
        print(combo, "->", r["po"] and r["po"]["status"], "·", " → ".join(p for p in r["path"] if "?" in p or p.startswith(("Stop", "PO Release"))))
    res["solution"].append(row)

ifs = sum(1 for n in wf_sol["nodes"] if n["type"].endswith(".if"))
http_nodes = {w: sum(1 for n in wf["nodes"] if n["type"].endswith("httpRequest")) for w, wf in (("happy", wf_happy), ("solution", wf_sol))}
res["counts"] = {
    "variants": 3, "combinations": 2 ** 3,
    "feasible_combinations": sum(1 for r in res["solution"] if r["feasible"]),
    "distinct_paths_in_solution": len(paths),
    "if_nodes_in_solution": ifs,
    "http_nodes": http_nodes, "nodes": {"happy": len(wf_happy["nodes"]), "solution": len(wf_sol["nodes"])},
    "note": "Closed cost centre stops for a person in the solution, so 6 feasible situations share 4 drawn paths. "
            "Handling it instead (switching to an open cost centre) needs one path per feasible combination: 6.",
    "plan_deck_six_variants_combinations": 2 ** 6,
}
res["paths"] = paths
LOGS.mkdir(parents=True, exist_ok=True)
(LOGS / "n8n_check.json").write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
print(json.dumps(res["counts"], indent=1, ensure_ascii=False))
assert res["happy_path"]["as_shipped"]["po"]["status"] == "RL"
