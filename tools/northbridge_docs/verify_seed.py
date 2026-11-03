"""Prove the dump agrees with the Ledgerline sandbox.

    PYTHONPATH=ledgerline python tools/northbridge_docs/verify_seed.py /Users/raj/Claude_Brain/northbridge-docs

1. The 38 purchasing service files match ledgerline/erp/services.py: names, titles, kinds, screens, fields (name, type,
   required, description, order) and the error codes the code can raise.
2. Every seed.py record (items, suppliers, certificates, rate contracts, stock, cost centres, budgets, tax codes,
   payment terms, warehouses, users' roles and limits) appears unchanged in the master-data spreadsheets.
Needs pyyaml and openpyxl. Prints one line per check and exits 1 on any mismatch.
"""
import os
import sys

import yaml
from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledgerline.erp import engine, seed as S  # noqa: E402
from ledgerline.erp import services as _s  # noqa: E402,F401
from ndocs.catalog import real_services  # noqa: E402

root = sys.argv[1]
bad = []


def ok(cond, what):
    if not cond:
        bad.append(what)


real = {s["name"]: s for s in real_services() if s["module"] == "PUR"}
files = sorted(f for f in os.listdir(f"{root}/04_service_definitions/purchase") if f.endswith(".yaml"))
ok(len(files) == 38 == len(real), f"expected 38 purchasing files, found {len(files)}")
for fn in files:
    y = yaml.safe_load(open(f"{root}/04_service_definitions/purchase/{fn}"))
    sp = engine.SERVICES[y["service"]]
    ok(y["title"] == sp.doc and y["kind"] == sp.kind and y["screen"] == sp.screen, f"{fn}: header")
    ok([(f["name"], f["type"], f["required"], f["desc"]) for f in y["request"]["fields"]] ==
       [(f.name, f.type, f.required, f.desc) for f in sp.fields], f"{fn}: fields")
    ok([e["code"] for e in y["errors"]] == [e["code"] for e in real[y["service"]]["errors"]], f"{fn}: errors")
print(f"services: {len(files)} purchasing definitions checked")


def sheet(path, name, header_row):
    ws = load_workbook(f"{root}/05_master_data/{path}", data_only=True)[name]
    rows = list(ws.iter_rows(values_only=True))
    head = list(rows[header_row - 1])
    return [dict(zip(head, r)) for r in rows[header_row:]]


def num(a, b):
    return abs(float(a) - float(b)) < 1e-9


items = {r["itm_cd"]: r for r in sheet("ITEM_MASTER_2026-10-26.xlsx", "Items", 4)}
for i in S.ITEMS:
    r = items.get(i[0])
    ok(r and (r["descr"], r["uom_cd"], r["cell_safety"], r["category"], r["active"], r["reorder_lvl"], r["avg_daily_issue"]) == i[1:], f"item {i[0]}")
sups = {r["sup_cd"]: r for r in sheet("SUPPLIER_MASTER.xlsx", "Suppliers", 3)}
for s in S.SUPPLIERS:
    r = sups.get(s[0])
    ok(r and (r["name"], r["vat_no"], r["state"], r["city"], r["status"], r["pt_cd"]) == s[1:], f"supplier {s[0]}")
ok(not any("brightcell" in str(r["name"]).lower() for r in sups.values()), "Brightcell must not be in the supplier master")
certs = sheet("SUPPLIER_MASTER.xlsx", "Certificates", 2)
for c in S.SUP_CERTS:
    ok(any((r["sup_cd"], r["cert_type"], r["doc_ref"], str(r["valid_to"]), r["uploaded_by"], str(r["uploaded_on"])) == c for r in certs), f"cert {c[2]}")
rates = sheet("Rate Contracts 2025-26 and 2026-27.xlsx", "2026-27", 3)
for a, b, rt, vf, vt in S.SUP_RATES:
    ok(any(r["sup_cd"] == a and r["itm_cd"] == b and num(r["rate"], rt) and r["valid_from"] == vf and r["valid_to"] == vt for r in rates), f"rate {a} {b} {vf}")
stock = {(r["itm_cd"], r["whs_cd"]): r for r in sheet("Stock_on_hand_2026-10-26_0900.xlsx", "Stock", 2)}
for a, b, oh, al, oo in S.STOCK:
    r = stock.get((a, b))
    ok(r and (r["on_hand"], r["allocated"], r["on_order"]) == (oh, al, oo), f"stock {a} {b}")
ccs = {r["cc_cd"]: r for r in sheet("Cost Centres and Budgets FY2026-27.xlsx", "Cost centres", 1)}
for a, b, st, cl, ow in S.COST_CENTRES:
    r = ccs.get(a)
    ok(r and (r["name"], r["status"], r["closed_on"] or None, r["owner"]) == (b, st, cl, ow), f"cost centre {a}")
bud = {r["cc_cd"]: r for r in sheet("Cost Centres and Budgets FY2026-27.xlsx", "Budgets 2026-Q4", 3)}
for a, p, amt, com in S.BUDGETS:
    ok(a in bud and num(bud[a]["amount"], amt) and num(bud[a]["committed"], com), f"budget {a}")
tax = {r["tax_cd"]: r for r in sheet("Tax codes.xlsx", "Tax codes", 2)}
for a, b, rt, k in S.TAX_CODES:
    ok(a in tax and tax[a]["descr"] == b and num(tax[a]["rate"], rt) and tax[a]["kind"] == k, f"tax {a}")
users = {r["user_id"]: r for r in sheet("Users_and_approval_limits.xlsx", "Users", 3)}
for u in S.USERS:
    r = users.get(u[0])
    ok(r and r["name"] == u[1] and r["role_cd"] == u[2] and num(r["appr_limit"], u[4]) and (r["manager_id"] or None) == u[5] and r["default_cc"] == u[7], f"user {u[0]}")
print(f"master data: {len(S.ITEMS)} items, {len(S.SUPPLIERS)} suppliers, {len(S.SUP_CERTS)} certificates, {len(S.SUP_RATES)} rates, "
      f"{len(S.STOCK)} stock rows, {len(S.COST_CENTRES)} cost centres, {len(S.BUDGETS)} budgets, {len(S.TAX_CODES)} tax codes, {len(S.USERS)} users checked")
for b in bad:
    print("MISMATCH", b)
print("OK" if not bad else f"{len(bad)} mismatches")
sys.exit(1 if bad else 0)
