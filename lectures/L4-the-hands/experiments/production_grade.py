"""Lecture 4, section 10: the production-grade criteria, measured on the toolbox (no model calls).

    tools/mrun.sh tools/modal_run.py --script lectures/L4-the-hands/experiments/production_grade.py --args "--label before"
    tools/mrun.sh tools/modal_run.py --script lectures/L4-the-hands/experiments/production_grade.py --args "--label after"

Every number here comes from calling the real tools on a fresh in-memory Ledgerline sandbox:
  1 schema       input and output validation (jsonschema, Draft 2020-12) on every regression call
  2 fuzzing      malformed arguments + injected service faults; unhandled / non-business errors as a share of calls
  3 latency      tool overhead p50/p95/p99 with the ERP service time (timed inside erp.call) subtracted;
                 direct (Toolbox.call) and through the in-memory MCP server
  4 payload      response sizes, at seed scale and with 500 extra rows; which list tools paginate
  5 idempotency  lost replies, rewritten arguments and plain resends of every write tool: duplicate documents
  6 timeouts     the retry policy, declared and tested per tool (busy server, lost reply, outage)
  7 regression   happy path, validation, permission denied, pagination, retries: pass per tool
  8 change mgmt  versions in tool.json, published over MCP; release notes; rollback
Writes logs/production_grade_<label>.json. production_merge.py turns before + after into logs/production_grade.json.
"""
from __future__ import annotations

import copy
import json
import os
import pathlib
import random
import statistics
import sys
import time
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "ledgerline"))

import jsonschema  # noqa: E402

from ledgerline.erp.engine import ERP, SERVICES  # noqa: E402
from ledgerline.toolbox import Toolbox  # noqa: E402

try:  # after the Lecture 4 change: every tool folder, extras included
    from ledgerline.toolbox import REGISTRY as REG  # noqa: E402
except ImportError:  # before it: the 15 tools
    from ledgerline.toolbox import SPECS as REG  # noqa: E402

LABEL = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "run"
REPS = int(os.environ.get("L4_REPS", "200"))
LOG = HERE / "logs"
OUT: dict = {"label": LABEL, "at": time.strftime("%Y-%m-%d %H:%M:%S"), "tools": list(REG), "n_tools": len(REG)}
WRITES = [n for n, s in REG.items() if s.writes]
OUT["write_tools"] = WRITES
CONTRACT_ERR = {"type": "object", "required": ["ok", "error", "next_step"],
                "properties": {"ok": {"const": False}, "error": {"type": "string", "minLength": 1},
                               "next_step": {"type": "string"}}}


# ----------------------------------------------------------------------------- the sandbox, set up per test
def world():
    """A fresh Northbridge with Emma's request approved, her order created and released (PO/2026/01182)."""
    erp = ERP()
    emma, daniel = Toolbox(erp, "ECLARKE", list(REG)), Toolbox(erp, "DOKAFOR", list(REG))
    pr = emma.call("create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07",
                                               "need_by": "2026-11-09", "confirm": True})
    daniel.call("approve_purchase_request", {"request_no": pr["request_no"], "decision": "approve"})
    po = emma.call("create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": pr["request_no"], "confirm": True})
    emma.call("release_purchase_order", {"po_no": po["po_no"]})
    return erp, {"pr": pr["request_no"], "po": po["po_no"]}


def fresh_pr_world():
    """A fresh Northbridge with one request waiting for Daniel (PR/2026/04417)."""
    erp = ERP()
    pr = Toolbox(erp, "ECLARKE", list(REG)).call("create_purchase_request", {
        "item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
    return erp, {"pr": pr["request_no"]}


# One happy-path call per tool: (user, args, which world). Writes commit (confirm=true) unless noted.
HAPPY = {
    "find_item": ("ECLARKE", {"query": "500 Wh battery pack"}, "plain"),
    "check_stock": ("ECLARKE", {"item_code": "BAT-500"}, "plain"),
    "find_supplier": ("ECLARKE", {"name": "Voltway Cells"}, "plain"),
    "check_budget": ("ECLARKE", {"cost_centre": "PRD-07"}, "plain"),
    "search_policy": ("ECLARKE", {"question": "Which suppliers may supply lithium battery packs?"}, "plain"),
    "create_purchase_request": ("ECLARKE", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07",
                                            "need_by": "2026-11-09", "confirm": True}, "plain"),
    "list_my_approvals": ("DOKAFOR", {}, "pr"),
    "approve_purchase_request": ("DOKAFOR", {"request_no": "{pr}", "decision": "approve"}, "pr"),
    "create_purchase_order": ("ECLARKE", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-375", "quantity": 100,
                                          "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}, "plain"),
    "approve_purchase_order": ("DOKAFOR", {"po_no": "PO/2026/01179"}, "plain"),
    "release_purchase_order": ("ECLARKE", {"po_no": "{po_ap}"}, "po_ap"),
    "order_status": ("ECLARKE", {"po_no": "{po}"}, "full"),
    "receive_goods": ("ATANAKA", {"po_no": "{po}", "quantity": 1200, "confirm": True}, "full"),
    "register_supplier": ("ECLARKE", {"name": "Brightcell Energy", "city": "Lyon", "state": "FR",
                                      "vat_no": "FR123456789012", "confirm": True}, "plain"),
    "send_message": ("ECLARKE", {"to": "@daniel", "text": "PR/2026/04417 is waiting for you."}, "plain"),
    "supplier_certificates": ("ECLARKE", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}, "plain"),
}


def make(kind):
    if kind == "full":
        return world()
    if kind == "pr":
        return fresh_pr_world()
    if kind == "po_ap":
        erp, ctx = fresh_pr_world()
        Toolbox(erp, "DOKAFOR", list(REG)).call("approve_purchase_request", {"request_no": ctx["pr"], "decision": "approve"})
        po = Toolbox(erp, "ECLARKE", list(REG)).call("create_purchase_order", {
            "supplier_code": "VC-EIN-0042", "request_no": ctx["pr"], "confirm": True})
        return erp, {**ctx, "po_ap": po["po_no"]}
    return ERP(), {}


def fill(args, ctx):
    return {k: (v.format(**ctx) if isinstance(v, str) and "{" in v else v) for k, v in args.items()}


def happy(name):
    user, args, kind = HAPPY[name]
    erp, ctx = make(kind)
    return erp, Toolbox(erp, user, list(REG)), fill(args, ctx)


def svc_count(erp):
    return len(erp.calls)


def in_contract(r) -> bool:
    if not isinstance(r, dict) or not isinstance(r.get("ok"), bool):
        return False
    if r["ok"]:
        return True
    return isinstance(r.get("error"), str) and bool(r["error"]) and isinstance(r.get("next_step"), str)


NON_BUSINESS = ("Bad arguments:", "Traceback", "NoneType", "KeyError", "IndexError", "AttributeError",
                "sqlite3", "object has no attribute", "unsupported operand", "ERR-SYS-0421", "ERR-SYS-0422", "ERR-SYS-0404")


def classify(fn):
    """Run one call; return (kind, result). kind: ok | business | non_business | unhandled | out_of_contract."""
    try:
        r = fn()
    except Exception as e:  # noqa: BLE001  an exception escaped the tool: the host sees a crash
        return "unhandled", {"exception": f"{type(e).__name__}: {e}"[:300], "trace": traceback.format_exc()[-600:]}
    if not in_contract(r):
        return "out_of_contract", r
    if r["ok"]:
        return "ok", r
    blob = json.dumps(r, default=str)
    if any(m in blob for m in NON_BUSINESS):
        return "non_business", r
    return "business", r


present = [n for n in HAPPY if n in REG and n not in os.environ.get("L4_SKIP", "").split(",")]
OUT["tools_measured"] = present

# ============================================================================= 1. schema validation
print("1 schema")
schema_rows = {}
for name in present:
    spec = REG[name].spec
    vin = jsonschema.Draft202012Validator(spec["input_schema"])
    vout = jsonschema.Draft202012Validator(spec["output_schema"]) if spec.get("output_schema") else None
    erp, tb, args = happy(name)
    in_errors = [e.message for e in vin.iter_errors(args)]
    r = tb.call(name, args)
    out_errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in vout.iter_errors(r)] if vout else ["no output_schema"]
    # the door: a wrong type and a missing required argument must be refused before any Ledgerline call
    props = spec["input_schema"].get("properties", {})
    req = spec["input_schema"].get("required", [])
    door = []
    for k, p in props.items():
        bad = {**args, k: ({"string": 12345, "integer": "many", "number": "lots", "boolean": [1]}).get(p.get("type"), 0)}
        erp2, tb2, _ = happy(name)
        n0 = svc_count(erp2)
        rr = tb2.call(name, bad)
        door.append({"arg": k, "sent": bad[k], "refused": rr.get("ok") is False, "ledgerline_calls": svc_count(erp2) - n0,
                     "error": rr.get("error")})
    for k in req:
        erp2, tb2, _ = happy(name)
        n0 = svc_count(erp2)
        rr = tb2.call(name, {kk: vv for kk, vv in args.items() if kk != k})
        door.append({"arg": k, "sent": "(missing)", "refused": rr.get("ok") is False, "ledgerline_calls": svc_count(erp2) - n0,
                     "error": rr.get("error")})
    schema_rows[name] = {"has_input_schema": bool(spec.get("input_schema")), "has_output_schema": bool(spec.get("output_schema")),
                         "happy_ok": r.get("ok"), "input_violations": in_errors, "output_violations": out_errors,
                         "door": door, "door_ok": all(d["refused"] and d["ledgerline_calls"] == 0 for d in door)}
    print(f"   {name:26} out-violations={len(out_errors)} door_ok={schema_rows[name]['door_ok']}")
OUT["schema"] = schema_rows

# ============================================================================= 2. error-contract fuzzing
print("2 fuzzing")
rng = random.Random(4)
JUNK = [None, "", " ", 0, -1, 10**12, 1.5, True, [], {}, "x" * 5000, "'; DROP TABLE item;--", "BAT-500\u0000",
        "éè☃", "NaN", "-2000", "2,000", "PO/2026/99999", "PR/2026/99999", "ZZZ-000", "2026-13-45",
        "9 Nov 2026", "yes", "null", "../../etc/passwd"]
fuzz = {"calls": 0, "by_kind": {}, "by_tool": {}, "examples": {}}


VOUT = {n: jsonschema.Draft202012Validator(s.spec["output_schema"]) for n, s in REG.items() if s.spec.get("output_schema")}
fuzz["ok_results_checked"] = 0
fuzz["ok_result_output_violations"] = []


def fuzz_record(name, label, kind, r):
    if kind == "ok" and name in VOUT:  # every successful result met while fuzzing must match tool.json's output_schema
        fuzz["ok_results_checked"] += 1
        for e in VOUT[name].iter_errors(r):
            if len(fuzz["ok_result_output_violations"]) < 30:
                fuzz["ok_result_output_violations"].append({"tool": name, "case": label, "path": "/".join(map(str, e.path)),
                                                            "error": e.message[:160]})
            fuzz.setdefault("ok_result_output_violation_count", 0)
            fuzz["ok_result_output_violation_count"] = fuzz.get("ok_result_output_violation_count", 0) + 1
    fuzz["calls"] += 1
    fuzz["by_kind"][kind] = fuzz["by_kind"].get(kind, 0) + 1
    t = fuzz["by_tool"].setdefault(name, {})
    t[kind] = t.get(kind, 0) + 1
    if kind in ("unhandled", "non_business", "out_of_contract"):
        fuzz["examples"].setdefault(name, [])
        if len(fuzz["examples"][name]) < 4:
            fuzz["examples"][name].append({"case": label, "result": json.loads(json.dumps(r, default=str))})


for name in present:
    spec = REG[name].spec
    props = list(spec["input_schema"].get("properties", {}))
    _, _, base = happy(name)
    cases = []
    for k in props:  # every junk value in every argument
        for j in JUNK:
            cases.append((f"{k}={str(j)[:20]!r}", {**base, k: j}))
    cases.append(("unknown argument", {**base, "sql": "SELECT 1"}))
    cases.append(("no arguments", {}))
    for _ in range(40):  # random mixtures
        a = dict(base)
        for k in rng.sample(props, k=min(len(props), rng.randint(1, 3))) if props else []:
            a[k] = rng.choice(JUNK)
        if rng.random() < 0.2 and a:
            a.pop(rng.choice(list(a)))
        cases.append(("mix", a))
    for label, a in cases:
        erp, tb, _ = happy(name)
        kind, r = classify(lambda: tb.call(name, a))
        fuzz_record(name, label, kind, r)
    # injected service faults, on every service the tool calls, in three modes
    for svc in spec.get("services", []):
        for mode, times in (("error_before", 1), ("error_before", 9), ("timeout_after_commit", 1)):
            erp, tb, a = happy(name)
            erp.inject(svc, mode, times)
            kind, r = classify(lambda: tb.call(name, a))
            fuzz_record(name, f"fault {svc} {mode} x{times}", kind, r)
n = fuzz["calls"]
bad = fuzz["by_kind"].get("unhandled", 0) + fuzz["by_kind"].get("non_business", 0) + fuzz["by_kind"].get("out_of_contract", 0)
errs = sum(v for k, v in fuzz["by_kind"].items() if k != "ok")
fuzz["unhandled_or_non_business_pct"] = round(100 * bad / n, 3)
fuzz["errors_total"] = errs
fuzz["errors_in_contract_pct"] = round(100 * (errs - fuzz["by_kind"].get("unhandled", 0)
                                              - fuzz["by_kind"].get("out_of_contract", 0)) / errs, 3) if errs else 100.0
print("   calls", n, fuzz["by_kind"], "bad%", fuzz["unhandled_or_non_business_pct"])
# nonsense a write tool should refuse but a business rule might not: a quantity of 0 or below, committed
nonsense = []
for name, extra in (("create_purchase_request", {}), ("create_purchase_order", {}), ("receive_goods", {})):
    if name not in present:
        continue
    for q in (0, -1, -2000):
        erp, tb, a = happy(name)
        before = docs(erp) if "docs" in globals() else None
        r = tb.call(name, {**a, "quantity": q})
        saved = r.get("ok") is True
        nonsense.append({"tool": name, "quantity": q, "accepted_and_saved": saved,
                         "result": {k: r.get(k) for k in ("ok", "error", "request_no", "po_no", "grn_no", "status")}})
fuzz["nonsense_quantities"] = nonsense
fuzz["nonsense_quantities_saved"] = sum(x["accepted_and_saved"] for x in nonsense)
print("   nonsense quantities saved:", fuzz["nonsense_quantities_saved"], "of", len(nonsense))
OUT["fuzzing"] = fuzz

# ============================================================================= 3. latency (service time excluded)
print("3 latency")


def pct(xs, p):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))], 3)


lat = {}
mcp_ok = True
try:
    from ledgerline.mcp_server import MCPClient
    from ledgerline.toolbox.mcp import build_toolbox_server
except Exception:  # noqa: BLE001
    mcp_ok = False
all_over, all_over_mcp = [], []
for name in present:
    over, svc_ms, tot, over_mcp = [], [], [], []
    for i in range(REPS):
        erp, tb, a = happy(name)
        n0 = svc_count(erp)
        t0 = time.perf_counter()
        tb.call(name, a)
        t = (time.perf_counter() - t0) * 1000
        s = sum(c.ms for c in erp.calls[n0:])
        tot.append(t); svc_ms.append(s); over.append(max(0.0, t - s))
    if mcp_ok:
        for i in range(max(20, REPS // 4)):
            erp, tb, a = happy(name)
            c = MCPClient(build_toolbox_server(erp, HAPPY[name][0], names=list(REG)))
            n0 = svc_count(erp)
            t0 = time.perf_counter()
            c.call_tool(name, a)
            t = (time.perf_counter() - t0) * 1000
            s = sum(cc.ms for cc in erp.calls[n0:])
            over_mcp.append(max(0.0, t - s))
            c.close()
    all_over += over
    all_over_mcp += over_mcp
    lat[name] = {"n": REPS, "service_ms_p50": pct(svc_ms, 50), "total_ms_p50": pct(tot, 50),
                 "overhead_ms": {"p50": pct(over, 50), "p95": pct(over, 95), "p99": pct(over, 99)},
                 "overhead_via_mcp_ms": {"p50": pct(over_mcp, 50), "p95": pct(over_mcp, 95), "p99": pct(over_mcp, 99),
                                         "n": len(over_mcp)} if over_mcp else None,
                 "ledgerline_calls": len(erp.calls) - n0 if False else None}
    print(f"   {name:26} overhead p50 {lat[name]['overhead_ms']['p50']:7.3f} p99 {lat[name]['overhead_ms']['p99']:7.3f} ms"
          + (f" | via MCP p50 {lat[name]['overhead_via_mcp_ms']['p50']:.2f}" if over_mcp else ""))
OUT["latency"] = {"per_tool": lat, "all_tools_overhead_ms": {"p50": pct(all_over, 50), "p95": pct(all_over, 95),
                                                              "p99": pct(all_over, 99), "n": len(all_over)},
                  "all_tools_overhead_via_mcp_ms": {"p50": pct(all_over_mcp, 50), "p95": pct(all_over_mcp, 95),
                                                    "p99": pct(all_over_mcp, 99), "n": len(all_over_mcp)} if all_over_mcp else None,
                  "where": "Modal container, 2 CPU" if os.environ.get("LEDGER_IN_MODAL") else "local laptop",
                  "note": "service time = time inside erp.call (permission check, payload coercion, the service and its stored "
                          "procedures, audit row), summed over every Ledgerline call the tool made; overhead = wall time "
                          "of the tool call minus that. Writes are measured committing on a fresh sandbox each time."}

# ============================================================================= 4. payload and pagination
print("4 payload")
LIMIT_BYTES = 100_000  # ~25,000 tokens: Claude Code's default cap on one MCP tool result (MAX_MCP_OUTPUT_TOKENS)
PAGE_ARGS = {"limit", "page", "cursor", "offset", "page_size"}
pay = {}
for name in present:
    erp, tb, a = happy(name)
    r = tb.call(name, a)
    size = len(json.dumps(r, default=str))
    arrays = [k for k, v in r.items() if isinstance(v, list)] if isinstance(r, dict) else []
    nested = [k for k, v in r.items() if isinstance(v, dict) and any(isinstance(x, list) for x in v.values())] if isinstance(r, dict) else []
    props = set(REG[name].spec["input_schema"].get("properties", {}))
    pay[name] = {"bytes": size, "array_fields": arrays + nested, "is_list_tool": False,
                 "paginates": bool(props & PAGE_ARGS)}


def scaled(name, setup):
    erp, tb, a = happy(name)
    setup(erp)
    r = tb.call(name, a)
    return r, len(json.dumps(r, default=str))


def many_items(erp):
    for i in range(500):
        erp.x("INSERT INTO item VALUES (?,?,?,?,?,?,?,?)", f"BAT-T{i:03d}", f"Battery pack, 36 V 500 Wh test variant {i}",
              "NOS", 1, "SPARES", 1, 0, 0)


def many_suppliers(erp):
    for i in range(500):
        erp.x("INSERT INTO supplier VALUES (?,?,?,?,?,?,?,'MIGRATION','2019-04-01')", f"VC-T{i:03d}", f"Voltway Cells Branch {i}",
              None, "NL", "Eindhoven", "ACTIVE", "N45")


def many_approvals(erp):
    for i in range(1000):
        erp.x("INSERT INTO approval(doc_type,doc_no,approver,status,requested_by,requested_on) VALUES ('PO',?,?,?,?,?)",
              "PO/2026/01179", "DOKAFOR", "PENDING", "ECLARKE", "2026-10-23")


def many_certs(erp):
    for i in range(300):
        erp.x("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", "NC-GDA-0063", "ISO9001", f"ISO-{i}", "2027-01-01", "LMORENO", "2026-01-01")


STRESS = {"find_item": many_items, "find_supplier": many_suppliers, "list_my_approvals": many_approvals,
          "supplier_certificates": many_certs}
for name, setup in STRESS.items():
    if name not in present:
        continue
    r, size = scaled(name, setup)
    rows = max([len(v) for v in r.values() if isinstance(v, list)] or [0]) if isinstance(r, dict) else 0
    pay[name].update({"is_list_tool": True, "at_scale": {"extra_rows": {"find_item": 500, "find_supplier": 500, "list_my_approvals": 1000}.get(name, 300),
                                                          "bytes": size, "rows_returned": rows,
                                                          "says_more": any(k in r for k in ("next_cursor", "has_more", "total"))}})
for name in ("check_budget", "search_policy"):  # lists by nature (open cost centres, clauses)
    if name in pay:
        pay[name]["is_list_tool"] = True
list_tools = [n for n, v in pay.items() if v["is_list_tool"]]
OUT["payload"] = {"per_tool": pay, "limit_bytes": LIMIT_BYTES, "max_bytes": max(v["bytes"] for v in pay.values()),
                  "max_bytes_at_scale": max([v.get("at_scale", {}).get("bytes", 0) for v in pay.values()]),
                  "over_limit": [n for n, v in pay.items() if max(v["bytes"], v.get("at_scale", {}).get("bytes", 0)) > LIMIT_BYTES],
                  "list_tools": list_tools, "list_tools_paginating": [n for n in list_tools if pay[n]["paginates"]]}
print("   max", OUT["payload"]["max_bytes"], "at scale", OUT["payload"]["max_bytes_at_scale"], "paginating",
      OUT["payload"]["list_tools_paginating"], "of", list_tools)

# ============================================================================= 5. idempotency
print("5 idempotency")


def docs(erp):
    return {"pr": erp.q1("SELECT count(*) n FROM pr_hdr")["n"], "po": erp.q1("SELECT count(*) n FROM po_hdr")["n"],
            "grn": erp.q1("SELECT count(*) n FROM grn_hdr")["n"] if erp.q1("SELECT 1 FROM sqlite_master WHERE name='grn_hdr'") else 0,
            "supplier": erp.q1("SELECT count(*) n FROM supplier")["n"], "msg": erp.q1("SELECT count(*) n FROM ntf_queue")["n"],
            "approved": erp.q1("SELECT count(*) n FROM approval WHERE status='APPROVED'")["n"]}


DOC_OF = {"create_purchase_request": "pr", "create_purchase_order": "po", "receive_goods": "grn",
          "register_supplier": "supplier", "send_message": "msg", "approve_purchase_request": "approved",
          "approve_purchase_order": "approved", "release_purchase_order": None}
WRITE_SVC = {"create_purchase_request": ["pr_save", "pr_submit"], "create_purchase_order": ["po_save"],
             "receive_goods": ["grn_save"], "register_supplier": ["sup_create"], "send_message": ["ntf_send"],
             "approve_purchase_request": ["pr_approve"], "approve_purchase_order": ["po_approve"],
             "release_purchase_order": ["po_release"]}


def ntf_count(erp):
    return erp.q1("SELECT count(*) n FROM ntf_queue")["n"]


def dup_test(name, args_first, args_retry, inject=None, retry_always=False):
    """Call once (optionally with a lost reply), then retry as a host would. Return documents made and duplicates."""
    erp, tb, base = happy(name)
    a1 = {**base, **args_first}
    a2 = {**base, **args_retry}
    before = docs(erp)
    if inject:
        erp.inject(inject, "timeout_after_commit")
    r1 = tb.call(name, a1)
    retried = retry_always or not r1.get("ok")
    r2 = tb.call(name, a2) if retried else None
    after = docs(erp)
    key = DOC_OF[name]
    if name == "release_purchase_order":  # one release = one order email to the supplier
        made = after["msg"] - before["msg"]
    else:
        made = after[key] - before[key]
    dup = max(0, made - 1)
    return {"first": {"args": a1, "ok": r1.get("ok"), "error": r1.get("error"), "already_done": r1.get("already_done")},
            "retried": retried,
            "retry": ({"args": a2, "ok": r2.get("ok"), "error": r2.get("error"), "already_done": r2.get("already_done")}
                      if r2 else None),
            "documents_made": made, "duplicates": dup}


idem = {"A_lost_reply_then_retry": {}, "B_retry_with_rewritten_arguments": {}, "C_plain_resend": {}}
for name in WRITES:
    if name not in present:
        continue
    for svc in WRITE_SVC.get(name, []):
        idem["A_lost_reply_then_retry"][f"{name} ({svc} reply lost)"] = dup_test(name, {}, {}, inject=svc)
    idem["C_plain_resend"][name] = dup_test(name, {}, {}, retry_always=True)
if "receive_goods" in present:  # Aiko's 1,200 of 2,000 is saved by the over-receipt rule; a 500-pack delivery is not
    idem["A_lost_reply_then_retry"]["receive_goods 500 packs (grn_save reply lost)"] = dup_test(
        "receive_goods", {"quantity": 500}, {"quantity": 500}, inject="grn_save")
    idem["C_plain_resend"]["receive_goods 500 packs"] = dup_test("receive_goods", {"quantity": 500}, {"quantity": 500},
                                                                  retry_always=True)
# B: the model writes the same order a second time, but spells an argument differently (the date, the code's case)
idem["B_retry_with_rewritten_arguments"]["create_purchase_request need_by '9 Nov 2026' then '2026-11-09'"] = dup_test(
    "create_purchase_request", {"need_by": "9 Nov 2026"}, {"need_by": "2026-11-09"}, retry_always=True)
idem["B_retry_with_rewritten_arguments"]["create_purchase_request need_by '2026-11-9' then '2026-11-09'"] = dup_test(
    "create_purchase_request", {"need_by": "2026-11-9"}, {"need_by": "2026-11-09"}, retry_always=True)
idem["B_retry_with_rewritten_arguments"]["create_purchase_order need_by '09/11/2026' then '2026-11-09'"] = dup_test(
    "create_purchase_order", {"need_by": "09/11/2026"}, {"need_by": "2026-11-09"}, retry_always=True)
idem["B_retry_with_rewritten_arguments"]["create_purchase_request lost reply, retry with '9 Nov 2026'"] = dup_test(
    "create_purchase_request", {"need_by": "2026-11-09"}, {"need_by": "9 Nov 2026"}, inject="pr_save", retry_always=True)
for k, v in idem.items():
    v["_duplicates"] = sum(x["duplicates"] for x in v.values() if isinstance(x, dict) and "duplicates" in x)
idem["duplicates_A_B"] = idem["A_lost_reply_then_retry"]["_duplicates"] + idem["B_retry_with_rewritten_arguments"]["_duplicates"]
idem["duplicates_C"] = idem["C_plain_resend"]["_duplicates"]
OUT["idempotency"] = idem
print("   A dup", idem["A_lost_reply_then_retry"]["_duplicates"], "B dup", idem["B_retry_with_rewritten_arguments"]["_duplicates"],
      "C dup", idem["C_plain_resend"]["_duplicates"])

# ============================================================================= 6. timeout and retry policy
print("6 timeouts")
tmo = {}
for name in present:
    spec = REG[name].spec
    declared = spec.get("policy") or spec.get("timeout") or None
    tests = []
    for svc in spec.get("services", []) or [None]:
        for mode, times, expect in (("error_before", 1, "recovers" if not (SERVICES.get(svc) and SERVICES[svc].kind == "write") else "structured"),
                                    ("error_before", 9, "structured"),
                                    ("timeout_after_commit", 1, "recovers_or_structured")):
            if svc is None:
                continue
            erp, tb, a = happy(name)
            before = docs(erp)
            erp.inject(svc, mode, times)
            kind, r = classify(lambda: tb.call(name, a))
            after = docs(erp)
            dup = any(after[k] - before[k] > 1 for k in after)
            okk = kind in ("ok", "business") and not dup
            if expect == "recovers":
                okk = okk and kind == "ok"
            tests.append({"service": svc, "mode": mode, "times": times, "expect": expect, "kind": kind,
                          "error": (r.get("error") if isinstance(r, dict) else None), "duplicate": dup, "pass": okk})
    if not spec.get("services"):  # search_policy: no Ledgerline call, nothing to time out against
        tests.append({"service": None, "mode": "n/a", "pass": True, "note": "no Ledgerline service"})
    tmo[name] = {"declared": declared, "tests": tests, "tested": len(tests), "passed": sum(t["pass"] for t in tests)}
    print(f"   {name:26} declared={bool(declared)} passed {tmo[name]['passed']}/{tmo[name]['tested']}")
OUT["timeouts"] = tmo

# ============================================================================= 7. regression suite
print("7 regression")
reg = {}
for name in present:
    row = {}
    # happy path: ok and the output validates
    sr = schema_rows[name]
    row["happy_path"] = bool(sr["happy_ok"]) and not sr["output_violations"]
    # validation errors: refused at the door, no Ledgerline call
    row["validation_errors"] = sr["door_ok"] if sr["door"] else None
    # permission denied: a user whose role lacks a service the tool needs gets a structured refusal and nothing changes
    spec = REG[name].spec
    probe = None
    for u in ("ATANAKA", "DOKAFOR", "ECLARKE", "HWEBER"):
        erp0 = ERP()
        from ledgerline.erp.receipts import install_receipts
        install_receipts(erp0)
        if any(not erp0.allowed(u, s) for s in spec.get("services", []) if s in SERVICES):
            probe = u
            break
    if probe and REG[name].writes:
        erp, tb, a = happy(name)
        before = docs(erp)
        r = Toolbox(erp, probe, list(REG)).call(name, a)
        row["permission_denied"] = r.get("ok") is False and in_contract(r) and docs(erp) == before
        row["permission_probe"] = {"user": probe, "error": r.get("error"), "code": r.get("ledgerline_code")}
    else:
        row["permission_denied"] = None  # every role may read; n/a
    row["pagination"] = (pay[name]["paginates"] if pay[name]["is_list_tool"] else None)
    row["retries"] = tmo[name]["passed"] == tmo[name]["tested"]
    if REG[name].writes:
        row["retries"] = row["retries"] and all(
            v["duplicates"] == 0 for k, v in idem["A_lost_reply_then_retry"].items() if k.startswith(name + " "))
    applicable = {k: v for k, v in row.items() if isinstance(v, bool)}
    row["pass"] = all(applicable.values())
    row["applicable"] = len(applicable)
    reg[name] = row
    print(f"   {name:26} {'PASS' if row['pass'] else 'FAIL'} " + " ".join(f"{k}={v}" for k, v in applicable.items()))
OUT["regression"] = {"per_tool": reg, "tools_passing": sum(r["pass"] for r in reg.values()), "tools": len(reg),
                     "write_tools_passing": sum(reg[n]["pass"] for n in reg if REG[n].writes),
                     "write_tools": sum(1 for n in reg if REG[n].writes)}

# ============================================================================= 8. change management
print("8 change management")
cm = {"version_in_tool_json": {n: REG[n].spec.get("version") for n in present}}
if mcp_ok:
    c = MCPClient(build_toolbox_server(ERP(), "ECLARKE", names=list(REG)))
    listed = {t.name: t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in c.list_tools()}
    c.close()
    cm["version_published_over_mcp"] = {n: (listed.get(n, {}).get("_meta") or {}).get("ledgerline/version", (listed.get(n, {}).get("_meta") or {}).get("version")) for n in present}
root = HERE.parents[2]
cm["release_notes"] = [str(p.relative_to(root)) for p in (root / "ledgerline").rglob("*") if p.is_file()
                       and p.name.upper().startswith(("CHANGELOG", "RELEASE"))][:5]
cm["note"] = "Rollback = pin the previous git tag (v3.1 is pinned by L3–L12 notebooks). Client sign-off is a process step, not measurable here."
OUT["change_management"] = cm
print("   versions", len([v for v in cm["version_in_tool_json"].values() if v]), "/", len(present),
      "| over MCP", len([v for v in cm.get("version_published_over_mcp", {}).values() if v]))

LOG.mkdir(exist_ok=True)
(LOG / f"production_grade_{LABEL}.json").write_text(json.dumps(OUT, indent=1, default=str))
print("wrote", LOG / f"production_grade_{LABEL}.json")
