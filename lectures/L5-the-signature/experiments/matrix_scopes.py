"""Lecture 5: identity and the approval matrix, measured without any model.

    modal run tools/modal_run.py --script lectures/L5-the-signature/experiments/matrix_scopes.py

Writes logs/scopes.json (what each user's role allows: menus, services, intent tools) and logs/matrix.json
(POL-APR-002 routed as data by authority.route, against Bahi's own sp_appr_route, over a grid of gross values,
plus the preview each identity gives for Kavita's ₹2,80,840 order).
"""
import json
import pathlib

from bahi.agent.authority import MATRIX, RULES, passthrough, route, scopes, service_account
from bahi.agent.tools import IntentTools
from bahi.erp.engine import ERP, PROCS

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)

erp = ERP()
users = ["KJOSHI", "RMEHTA", "SKULKARNI", "APATIL", "NDESAI", "SVC_AGENT"]
sc = {u: scopes(erp, u) for u in users}
for u in users:
    s = sc[u]
    print(f"{u:10} {s['role']:10} limit {s['limit']:>16,.0f} services {s['services']:>3} writes {len(s['write_services']):>2} "
          f"menus {sum(m['allowed'] for m in s['menu'])}/{len(s['menu'])} tools {sum(t['allowed'] for t in s['tools'])}/{len(s['tools'])}")

# the matrix as data, and Bahi's own routing, on the same grid
grid = [24072, 50000, 140420, 245440, 250000, 250001, 280840, 335120, 500000, 720000, 1000000, 1200000, 5000000, 5000001]
rows = []
for req in ["KJOSHI", "SKULKARNI", "RMEHTA"]:
    for g in grid:
        ours = route(erp, req, g)
        e2 = ERP()
        try:
            bahi = PROCS["sp_appr_route"](e2, "PO", "TEST", req, g) if g > e2.user(req)["appr_limit"] else req
        except Exception as ex:  # noqa: BLE001
            bahi = f"{getattr(ex, 'err_cd', type(ex).__name__)}"
        mine = ours["approver"] or ("MD (outside Bahi)" if ours["outside_bahi"] else None)
        agree = (mine == bahi) or (ours["outside_bahi"] and bahi == "ERR-APR-0009")
        rows.append({"requester": req, "gross": g, "ours": mine, "bahi": bahi, "agree": agree, "rule": ours["rule"],
                     "hops": [h["user"] for h in ours["hops"]]})
print("matrix vs Bahi:", sum(r["agree"] for r in rows), "/", len(rows), "agree")
for r in rows:
    if not r["agree"]:
        print("  disagree:", r)

kav = route(erp, "KJOSHI", 280840)
svc = route(erp, "SVC_AGENT", 280840)

# the preview Kavita's order gets, as her and as the service account
prev = {}
for ident in (passthrough(erp, "KJOSHI"), service_account(erp, "KJOSHI")):
    t = IntentTools(ident.session)
    out = t.call("create_purchase_order", dict(supplier_code="DP-RJK-0042", item_code="GSK-SIL-05L", quantity=20000,
                                               cost_centre="PRD-07", need_by="2026-11-02", confirm=False))
    p = out["preview"]
    prev[ident.kind] = {k: p[k] for k in ("gross_value", "needs_approval", "your_limit", "approver", "path")}
    print(ident.kind, prev[ident.kind])

matrix_doc = {r: MATRIX[r] for r in MATRIX}
bahi_limits = {u: erp.user(u)["appr_limit"] for u in users}
json.dump({"scopes": sc}, open(LOGS / "scopes.json", "w"), indent=1, default=str)
json.dump({"matrix": matrix_doc, "rules": RULES, "bahi_user_limits": bahi_limits, "grid": rows,
           "agree": sum(r["agree"] for r in rows), "n": len(rows), "kavita_280840": kav, "svc_280840": svc,
           "preview_by_identity": prev}, open(LOGS / "matrix.json", "w"), indent=1, default=str)
print("kavita route:", kav["approver"], kav["rule"], [h["user"] for h in kav["hops"]])
print("svc route:", svc["note"])
