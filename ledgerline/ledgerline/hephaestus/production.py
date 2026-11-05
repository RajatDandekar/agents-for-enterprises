"""The Production tab: each criterion of the deck's 'Demo or Production' plate, run on the student's own tools.

The checks follow lectures/L4-the-hands/experiments/production_grade.py (the lecture's own measurement of the toolbox),
at a smaller size so one click takes seconds, and they run on the student's knobbed tools (ForgeToolbox), in fresh
sandboxes. Only 'LLM usability' calls the model (the golden tasks in runs.py); 'MCP compliance' calls the student's
own MCP address over the internet.

    check(cid, config, key=..., guard=..., pool=...) -> {"id", "area", "pass", "headline", "rows", "do", ...}
"""
from __future__ import annotations

import json
import os
import random
import time

import jsonschema

from ..erp.engine import SERVICES
from . import forge as F
from . import runs as R

# One happy-path call per tool: (user, args, world). Writes commit unless noted (from production_grade.py).
HAPPY = {
    "find_item": ({"query": "500 Wh battery pack"}, "plain"),
    "check_stock": ({"item_code": "BAT-500"}, "plain"),
    "find_supplier": ({"name": "Voltway Cells"}, "plain"),
    "check_budget": ({"cost_centre": "PRD-07"}, "plain"),
    "search_policy": ({"question": "Which suppliers may supply lithium battery packs?"}, "plain"),
    "create_purchase_request": ({"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07",
                                 "need_by": "2026-11-09", "confirm": True}, "plain"),
    "list_my_approvals": ({}, "plain"),
    "approve_purchase_request": ({"request_no": "{pr}", "decision": "approve"}, "pr"),
    "create_purchase_order": ({"supplier_code": "VC-EIN-0042", "item_code": "BAT-375", "quantity": 100,
                               "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}, "plain"),
    "approve_purchase_order": ({"po_no": "PO/2026/01179"}, "plain"),
    "release_purchase_order": ({"po_no": "{po_ap}"}, "po_ap"),
    "order_status": ({"po_no": "PO/2026/01179"}, "plain"),
    "receive_goods": ({"po_no": "{po}", "quantity": 1200, "confirm": True}, "full"),
    "register_supplier": ({"name": "Brightcell Energy", "city": "Lyon", "state": "FR", "vat_no": "FR123456789012",
                           "confirm": True}, "plain"),
    "send_message": ({"to": "@daniel", "text": "PR/2026/04417 is waiting for you."}, "plain"),
    "supplier_certificates": ({"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}, "plain"),
}
SHIPPED = F.default_config()


def _world(kind: str):
    """A fresh sandbox with the documents a tool's happy path needs, made with the shipped toolbox."""
    erp = F.new_erp()
    ctx = {}
    if kind in ("pr", "po_ap", "full"):
        emma = F.ForgeToolbox(F.clean_config({"tools": {n: {"on": True} for n in F.TOOLS}}), erp)
        ctx["pr"] = emma.call("create_purchase_request", {"item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07",
                                                          "need_by": "2026-11-09", "confirm": True}).get("request_no")
        if kind in ("po_ap", "full"):
            from ..toolbox import Toolbox
            Toolbox(erp, "DOKAFOR", F.TOOLS).call("approve_purchase_request", {"request_no": ctx["pr"], "decision": "approve"})
            po = emma.call("create_purchase_order", {"supplier_code": "VC-EIN-0042", "request_no": ctx["pr"], "confirm": True})
            ctx["po_ap"] = ctx["po"] = po.get("po_no")
            if kind == "full":
                emma.call("release_purchase_order", {"po_no": ctx["po"]})
    return erp, ctx


def _fill(args, ctx):
    return {k: (v.format(**ctx) if isinstance(v, str) and "{" in v else v) for k, v in args.items()}


APPROVER_TOOLS = ("approve_purchase_request", "approve_purchase_order", "list_my_approvals")


def happy(name: str, config: dict, log=None):
    """A fresh sandbox, the student's tool, and its happy-path arguments. Approval tools are Daniel's job, so with the
    forge acting as the person their happy path runs in Daniel's session (with the service account, as it)."""
    args, kind = HAPPY[name]
    erp, ctx = _world(kind)
    tb = F.ForgeToolbox(config, erp, log=log)
    if name in APPROVER_TOOLS and config["identity"] == F.HUMAN:
        with erp.lock:
            tb.s = erp.session("DOKAFOR")
    return erp, tb, _fill(args, ctx)


def shown(config, name):
    return F.LEGACY_NAMES[name] if config["tools"][name]["name"] == "legacy" else name


def on_tools(config) -> list[str]:
    return [n for n in F.TOOLS if config["tools"][n]["on"] and n in HAPPY]


def in_contract(r) -> bool:
    if not isinstance(r, dict) or not isinstance(r.get("ok"), bool):
        return False
    if r["ok"]:
        return True
    return isinstance(r.get("error"), str) and bool(r["error"]) and isinstance(r.get("next_step"), str)


NON_BUSINESS = ("Bad arguments:", "Traceback", "NoneType", "KeyError", "IndexError", "AttributeError", "sqlite3",
                "object has no attribute", "unsupported operand", "ERR-SYS-0421", "ERR-SYS-0422", "ERR-SYS-0404", "INTERNAL")


def classify(r) -> str:
    if not in_contract(r):
        return "out_of_contract"
    if r["ok"]:
        return "ok"
    return "non_business" if any(m in json.dumps(r, default=str) for m in NON_BUSINESS) else "business"


def pct(xs, p):
    xs = sorted(xs)
    return round(xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))], 3) if xs else None


JUNK = [None, "", 0, -1, 10**12, 1.5, True, [], {}, "x" * 3000, "'; DROP TABLE item;--", "2026-13-45", "9 Nov 2026",
        "PR/2026/99999", "ZZZ-000", "-2000"]

CRITERIA = [
    {"id": "schema", "area": "Schema", "criterion": "Input and output validation",
     "threshold": "every tool has both schemas; 0 output violations; bad input refused at the door",
     "do": "Write an input and an output schema for every tool. Validate the input once, at the door, before your system "
           "sees it, and validate every result against the output schema in your tests: clients such as Claude reject a "
           "result that does not match it."},
    {"id": "reliability", "area": "Reliability", "criterion": "Unhandled or non-business errors under fuzzing",
     "threshold": "≤ 0.1% of calls; 100% of errors in the error contract (ok=false, error, next_step)",
     "do": "Fuzz every argument with wrong types, blanks, huge strings and nonsense numbers. Every failure must come back "
           "as ok=false with what went wrong and what to do next, never a stack trace or a bare legacy code."},
    {"id": "usability", "area": "LLM usability", "criterion": "Right tool, right arguments on golden tasks",
     "threshold": "≥ 95% on the first model response",
     "do": "Keep 20–30 golden tasks from real user requests, each with the tool and arguments it must produce. Run them on "
           "every host you support whenever a name, description or schema changes."},
    {"id": "latency", "area": "Latency", "criterion": "Tool overhead, the system's own time excluded",
     "threshold": "p50 ≤ 50 ms, p95 ≤ 100 ms, p99 ≤ 200 ms",
     "do": "Time each call minus the time spent inside your backend: that is the part you own. Report p50, p95 and p99."},
    {"id": "payload", "area": "Payload", "criterion": "Result size; every list says when there is more",
     "threshold": "≤ 100 KB per result; every list tool caps its rows and says how many more",
     "do": "Load your backend with 500 extra rows and call every list tool. Cap the rows, say how many more there are "
           "(or give a cursor), and return only the fields the model needs."},
    {"id": "idempotency", "area": "Idempotency", "criterion": "Duplicate or retried writes",
     "threshold": "0 duplicate documents",
     "do": "For every write: lose the reply after the commit and retry; retry with an argument written differently. Build "
           "the idempotency key from the normalised content and look the document up before writing again."},
    {"id": "timeouts", "area": "Timeouts", "criterion": "Timeout and retry policy, declared and tested",
     "threshold": "100% of tools pass a busy server, an outage and a lost reply",
     "do": "Declare the policy per tool (reads retry, writes look themselves up) and inject each fault in a test."},
    {"id": "permissions", "area": "Permissions", "criterion": "The tool acts as the person, never as admin",
     "threshold": "a write Emma may not do is refused; documents are raised as Emma",
     "do": "Call your system with the signed-in person's own credentials (on-behalf-of), never a service account. Test "
           "one action the person is not allowed to do: it must be refused."},
    {"id": "audit", "area": "Audit log", "criterion": "Every write traceable to a person",
     "threshold": "the system's audit trail names the person; the tool log has who, what, when and how",
     "do": "Log every tool call (person, host, tool, arguments, result, time) and check your system's own audit trail "
           "names the person, not the integration account."},
    {"id": "mcp", "area": "MCP compliance", "criterion": "Your address answers the protocol correctly",
     "threshold": "initialize, tools/list, tools/call and the errors all as the specification says",
     "do": "Point a real MCP client (Claude, the MCP Inspector) at your server and check initialize, tools/list, "
           "tools/call, an unknown method and a GET."},
    {"id": "regression", "area": "Regression", "criterion": "Happy path, validation, errors, retries, permission",
     "threshold": "≥ 98% of tools; 100% of write tools",
     "do": "Turn all of the above into one test suite per tool and run it on every change, before it reaches a user."},
    {"id": "change", "area": "Change management", "criterion": "Versions, release notes, rollback",
     "threshold": "every changed tool has a new version and a note; rollback is one step",
     "do": "Version every tool, publish the version (here in tools/list _meta), write a note per change, keep the previous "
           "version one click away, and agree the change with the client before it ships."},
]
C = {c["id"]: c for c in CRITERIA}


# ----------------------------------------------------------------------------------------------- the checks
def c_schema(config, **_):
    rows = []
    for n in on_tools(config):
        d = F.definition(n, config["tools"][n])
        try:
            jsonschema.Draft202012Validator.check_schema(d["inputSchema"])
            in_ok = True
        except jsonschema.SchemaError:
            in_ok = False
        erp, tb, args = happy(n, config)
        r = tb.call(shown(config, n), args)
        outs = d.get("outputSchema")
        viol = ([f"{'/'.join(map(str, e.path)) or '(top)'}: {e.message[:120]}" for e in
                 jsonschema.Draft202012Validator(outs).iter_errors(r)] if outs and r.get("ok") else [])
        door = []
        props = F.REGISTRY[n].spec["input_schema"].get("properties", {})
        for k, p in list(props.items())[:4]:
            bad = {**args, k: {"string": 12345, "integer": "many", "number": "lots", "boolean": [1]}.get(p.get("type"), 0)}
            erp2, tb2, _ = happy(n, config)
            n0 = len(erp2.calls)
            rr = tb2.call(shown(config, n), bad)
            door.append({"arg": k, "sent": bad[k], "refused_at_door": rr.get("ok") is False and len(erp2.calls) == n0})
        rows.append({"tool": n, "input_schema_valid": in_ok, "has_output_schema": bool(outs), "happy_ok": r.get("ok"),
                     "output_violations": viol, "door": door,
                     "door_holds": all(x["refused_at_door"] for x in door),
                     "pass": in_ok and bool(outs) and not viol and all(x["refused_at_door"] for x in door)})
    held = sum(r["door_holds"] for r in rows)
    v = sum(len(r["output_violations"]) for r in rows)
    ok = all(r["pass"] for r in rows)
    return ok, (f"{len(rows)} tools: {sum(r['has_output_schema'] for r in rows)} with an output schema, {v} output "
                f"violations, the door refused bad types on {held} of {len(rows)}"), rows


def c_reliability(config, **_):
    rng = random.Random(4)
    by, examples, n_calls = {}, [], 0
    per_tool = {}
    for n in on_tools(config):
        props = list(F.REGISTRY[n].spec["input_schema"].get("properties", {}))
        _, _, base = happy(n, config)
        cases = [({**base, k: j}, f"{k}={str(j)[:16]!r}") for k in props for j in JUNK]
        cases += [({**base, "sql": "SELECT 1"}, "unknown argument"), ({}, "no arguments")]
        for _ in range(10):
            a = dict(base)
            for k in rng.sample(props, k=min(len(props), rng.randint(1, 2))) if props else []:
                a[k] = rng.choice(JUNK)
            cases.append((a, "mix"))
        t = {}
        for a, label in cases:
            erp, tb, _ = happy(n, config)
            try:
                r = tb.call(shown(config, n), a)
                kind = classify(r)
            except Exception as e:  # noqa: BLE001
                r, kind = {"exception": f"{type(e).__name__}: {e}"[:200]}, "unhandled"
            n_calls += 1
            by[kind] = by.get(kind, 0) + 1
            t[kind] = t.get(kind, 0) + 1
            if kind in ("non_business", "out_of_contract", "unhandled") and len(examples) < 8:
                examples.append({"tool": n, "case": label, "result": json.loads(json.dumps(r, default=str))})
        per_tool[n] = t
    bad = by.get("non_business", 0) + by.get("out_of_contract", 0) + by.get("unhandled", 0)
    errs = sum(v for k, v in by.items() if k != "ok")
    rate = round(100 * bad / n_calls, 2) if n_calls else 0.0
    rows = [{"tool": n, **t, "pass": not (t.get("non_business") or t.get("out_of_contract") or t.get("unhandled"))}
            for n, t in per_tool.items()]
    ok = rate <= 0.1
    return ok, (f"{n_calls} fuzzed calls: {rate}% were not business errors in the contract "
                f"({by.get('out_of_contract', 0)} out of contract, {by.get('non_business', 0)} non-business)"), \
        {"rows": rows, "by_kind": by, "errors": errs, "examples": examples}


def c_latency(config, **_):
    allo, rows = [], []
    for n in on_tools(config):
        over = []
        for _ in range(25):
            erp, tb, a = happy(n, config)
            n0 = len(erp.calls)
            t0 = time.perf_counter()
            F.SERVER.handle(tb, {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                 "params": {"name": shown(config, n), "arguments": a}}, "production check")
            t = (time.perf_counter() - t0) * 1000
            s = sum(c.ms for c in erp.calls[n0:])
            over.append(max(0.0, t - s))
        allo += over
        rows.append({"tool": n, "p50": pct(over, 50), "p95": pct(over, 95), "p99": pct(over, 99)})
    p = {"p50": pct(allo, 50), "p95": pct(allo, 95), "p99": pct(allo, 99), "n": len(allo)}
    ok = bool(allo) and p["p50"] <= 50 and p["p95"] <= 100 and p["p99"] <= 200
    slow = max(rows, key=lambda r: r["p99"] or 0) if rows else None
    return ok, (f"overhead through your MCP server: p50 {p['p50']} ms, p95 {p['p95']} ms, p99 {p['p99']} ms over "
                f"{p['n']} calls" + (f"; slowest {slow['tool']} (p99 {slow['p99']} ms)" if slow else "")), \
        {"rows": rows, "all": p}


def _many_items(erp):
    for i in range(500):
        erp.x("INSERT INTO item VALUES (?,?,?,?,?,?,?,?)", f"BAT-T{i:03d}", f"Battery pack, 36 V 500 Wh test variant {i}",
              "NOS", 1, "SPARES", 1, 0, 0)


def _many_suppliers(erp):
    for i in range(500):
        erp.x("INSERT INTO supplier VALUES (?,?,?,?,?,?,?,'MIGRATION','2019-04-01')", f"VC-T{i:03d}",
              f"Voltway Cells Branch {i}", None, "NL", "Eindhoven", "ACTIVE", "N45")


def _many_certs(erp):
    for i in range(300):
        erp.x("INSERT INTO sup_cert VALUES (?,?,?,?,?,?)", "NC-GDA-0063", "ISO9001", f"ISO-{i}", "2027-01-01", "LMORENO",
              "2026-01-01")


STRESS = {"find_item": _many_items, "find_supplier": _many_suppliers, "supplier_certificates": _many_certs}
MORE_KEYS = ("next_cursor", "more_rows", "has_more", "total")


def c_payload(config, **_):
    rows = []
    for n in on_tools(config):
        erp, tb, a = happy(n, config)
        r = tb.call(shown(config, n), a)
        row = {"tool": n, "bytes": len(json.dumps(r, default=str)), "list_tool": n in F.ROWS_TOOLS}
        if n in STRESS:
            erp, tb, a = happy(n, config)
            with erp.lock:
                STRESS[n](erp)
            r2 = tb.call(shown(config, n), a)
            key = F.ROWS_TOOLS[n]
            rr = r2.get(key) if isinstance(r2, dict) else None
            row.update({"at_scale_bytes": len(json.dumps(r2, default=str)), "rows_at_scale": len(rr) if isinstance(rr, list) else None,
                        "says_more": isinstance(r2, dict) and any(k in r2 and r2[k] not in (None, 0) for k in MORE_KEYS)})
        rows.append(row)
    big = max([max(r["bytes"], r.get("at_scale_bytes", 0)) for r in rows] or [0])
    stressed = [r for r in rows if "says_more" in r]
    ok = big <= 100_000 and all(r["says_more"] for r in stressed)
    return ok, (f"largest result {big:,} bytes; with 500 extra rows, {sum(r['says_more'] for r in stressed)} of "
                f"{len(stressed)} list tools say there is more"), rows


def _dup(config, first, retry, inject=None, always=False):
    erp, _ = _world("plain")
    tb = F.ForgeToolbox(config, erp)
    base = dict(HAPPY["create_purchase_request"][0])
    n0 = len(R.prs(erp))
    if inject:
        erp.inject(inject, "timeout_after_commit")
    s = shown(config, "create_purchase_request")
    r1 = tb.call(s, {**base, **first})
    r2 = tb.call(s, {**base, **retry}) if always or not r1.get("ok") else None
    if config["rules"]["preview"] == "tool":  # the preview rule refuses a commit with no preview: preview first
        pass
    made = len(R.prs(erp)) - n0
    return {"first": {k: r1.get(k) for k in ("ok", "error", "request_no", "already_done")},
            "retry": {k: r2.get(k) for k in ("ok", "error", "request_no", "already_done")} if r2 else None,
            "documents": made, "duplicates": max(0, made - 1)}


def c_idempotency(config, **_):
    if not config["tools"]["create_purchase_request"]["on"]:
        return None, "create_purchase_request is switched off: no write to test", []
    c = json.loads(json.dumps(config))
    if c["rules"]["preview"] == "tool":
        c["rules"]["preview"] = "off"  # the test commits directly; the preview rule is tested in the Shield
    c = F.clean_config(c)
    rows = [
        {"case": "pr_save's reply is lost, the host retries", **_dup(c, {}, {}, inject="pr_save")},
        {"case": "the same request resent", **_dup(c, {}, {}, always=True)},
        {"case": "need_by '9 Nov 2026', then '2026-11-09'", **_dup(c, {"need_by": "9 Nov 2026"}, {"need_by": "2026-11-09"}, always=True)},
        {"case": "lost reply, retried with '9 Nov 2026'", **_dup(c, {"need_by": "2026-11-09"}, {"need_by": "9 Nov 2026"},
                                                            inject="pr_save", always=True)},
    ]
    d = sum(r["duplicates"] for r in rows)
    return d == 0, f"{d} duplicate requests in {len(rows)} retry cases", rows


def c_timeouts(config, **_):
    rows = []
    for n in on_tools(config):
        spec = F.REGISTRY[n].spec
        tests = []
        for svc in spec.get("services", []):
            for mode, times in (("error_before", 1), ("error_before", 9), ("timeout_after_commit", 1)):
                erp, tb, a = happy(n, config)
                before = len(R.prs(erp))
                erp.inject(svc, mode, times)
                try:
                    r = tb.call(shown(config, n), a)
                    kind = classify(r)
                except Exception:  # noqa: BLE001
                    kind = "unhandled"
                dup = len(R.prs(erp)) - before > 1
                is_read = not (SERVICES.get(svc) and SERVICES[svc].kind == "write")
                okk = kind in ("ok", "business") and not dup
                if mode == "error_before" and times == 1 and is_read:
                    okk = okk and kind == "ok"
                tests.append({"service": svc, "mode": mode, "times": times, "kind": kind, "pass": okk})
        rows.append({"tool": n, "tested": len(tests), "passed": sum(t["pass"] for t in tests),
                     "declared": bool(spec.get("policy")), "pass": all(t["pass"] for t in tests) and bool(spec.get("policy")),
                     "fails": [t for t in tests if not t["pass"]][:4]})
    ok = all(r["pass"] for r in rows)
    return ok, (f"{sum(r['passed'] for r in rows)} of {sum(r['tested'] for r in rows)} injected faults handled; "
                f"policy declared on {sum(r['declared'] for r in rows)} of {len(rows)} tools"), rows


def _emma_pr(erp):
    r = F.ForgeToolbox(SHIPPED, erp).call("create_purchase_request", {
        "item_code": "BAT-500", "quantity": 2000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True})
    return r.get("request_no")


def c_permissions(config, **_):
    rows = []
    if config["tools"]["approve_purchase_request"]["on"]:
        erp = F.new_erp()
        pr = _emma_pr(erp)
        tb = F.ForgeToolbox(config, erp)
        r = tb.call(shown(config, "approve_purchase_request"), {"request_no": pr, "decision": "approve"})
        st = R.prs(erp)
        p = next(x for x in st if x["pr_no"] == pr)
        rows.append({"test": f"approve Emma's own request {pr}", "expected": "refused", "result": r.get("error") or r.get("status"),
                     "pass": p["status"] != "AP", "approved_by": p["approved_by"]})
    if config["tools"]["create_purchase_request"]["on"]:
        erp = F.new_erp()
        c = json.loads(json.dumps(config))
        c["rules"]["preview"] = "off"
        tb = F.ForgeToolbox(F.clean_config(c), erp)
        r = tb.call(shown(config, "create_purchase_request"), HAPPY["create_purchase_request"][0])
        st = R.prs(erp)
        new = st[-1] if st else None
        rows.append({"test": "raise 2,000 BAT-500 on PRD-07 (£273,600, above Emma's £250,000 limit)",
                     "expected": "raised by ECLARKE, waiting for Daniel",
                     "result": f"raised by {new['raised_by']}, {new['status']}" if new else r.get("error"),
                     "pass": bool(new) and new["raised_by"] == F.HUMAN and new["status"] == "PA"})
    if not rows:
        return None, "no write tool switched on", []
    ok = all(r["pass"] for r in rows)
    return ok, (f"the tools act as {config['identity']}: " + "; ".join(f"{r['test'].split(' (')[0]} → {r['result']}" for r in rows)), rows


def c_audit(config, **_):
    if not config["tools"]["create_purchase_request"]["on"]:
        return None, "create_purchase_request is switched off: no write to trace", []
    erp = F.new_erp()
    log = []
    c = json.loads(json.dumps(config))
    c["rules"]["preview"] = "off"
    tb = F.ForgeToolbox(F.clean_config(c), erp, log=lambda entry: log.append(entry))
    tb.call(shown(config, "create_purchase_request"), HAPPY["create_purchase_request"][0], via="production check",
            client="audit test")
    with erp.lock:
        trail = erp.q("SELECT ts, user_id, svc, rc FROM audit_trail WHERE svc IN ('pr_save','pr_submit') ORDER BY rowid")
    who = sorted({t["user_id"] for t in trail})
    e = log[-1] if log else {}
    rows = [{"where": "Ledgerline's audit trail", "shows": ", ".join(f"{t['svc']} by {t['user_id']} at {t['ts']}" for t in trail),
             "pass": who == [F.HUMAN]},
            {"where": "the forge's call log", "shows": f"{e.get('tool')} via {e.get('via')} ({e.get('client')}), "
                                                       f"{len(e.get('ledgerline', []))} Ledgerline calls, {e.get('ms')} ms",
             "pass": bool(e)}]
    return all(r["pass"] for r in rows), f"Ledgerline's audit trail names {', '.join(who) or 'nobody'}", rows


def c_usability(config, guard=None, pool=None, **_):
    g = R.golden(config, guard, pool)
    if not g["of"]:
        return None, "no golden task's tool is switched on", g["rows"]
    rate = g["passed"] / g["of"]
    return rate >= 0.95, f"{g['passed']} of {g['of']} golden tasks: right tool and right arguments on the first call", g["rows"]


def c_mcp(config, key=None, ws=None, **_):
    import httpx

    url = os.environ.get("HEPH_URL", "").rstrip("/") + f"/mcp/{key}"
    rows = []
    h = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=30) as c:
            r = c.post(url, headers=h, json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "hephaestus-selftest", "version": "1"}}})
            j = r.json()
            sid = r.headers.get("mcp-session-id")
            rows.append({"step": "initialize", "status": r.status_code, "pass": r.status_code == 200 and
                         j.get("result", {}).get("protocolVersion") == "2025-06-18",
                         "shows": f"protocol {j.get('result', {}).get('protocolVersion')}, server {j.get('result', {}).get('serverInfo', {}).get('name')}"})
            h2 = {**h, "MCP-Protocol-Version": "2025-06-18", **({"Mcp-Session-Id": sid} if sid else {})}
            r = c.post(url, headers=h2, json={"jsonrpc": "2.0", "method": "notifications/initialized"})
            rows.append({"step": "notifications/initialized", "status": r.status_code, "pass": r.status_code == 202, "shows": "202 Accepted, no body"})
            r = c.post(url, headers=h2, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            tools = r.json().get("result", {}).get("tools", [])
            want = [shown(config, n) for n in F.TOOLS if config["tools"][n]["on"]]
            rows.append({"step": "tools/list", "status": r.status_code, "pass": [t["name"] for t in tools] == want,
                         "shows": f"{len(tools)} tools: {', '.join(t['name'] for t in tools)}"})
            first = on_tools(config)[0] if on_tools(config) else None
            if first and HAPPY[first][1] == "plain" and not F.REGISTRY[first].writes:
                r = c.post(url, headers=h2, json={"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                                  "params": {"name": shown(config, first), "arguments": HAPPY[first][0]}})
                res = r.json().get("result", {})
                rows.append({"step": f"tools/call {shown(config, first)}", "status": r.status_code,
                             "pass": r.status_code == 200 and res.get("isError") is False and bool(res.get("structuredContent")),
                             "shows": f"isError {res.get('isError')}, {len(res.get('content', [{}])[0].get('text', ''))} characters"})
            r = c.post(url, headers=h2, json={"jsonrpc": "2.0", "id": 4, "method": "tools/frobnicate"})
            rows.append({"step": "an unknown method", "status": r.status_code,
                         "pass": r.json().get("error", {}).get("code") == -32601, "shows": f"error {r.json().get('error', {}).get('code')}"})
            r = c.get(url, headers={"Accept": "text/event-stream"})
            rows.append({"step": "GET (no server stream)", "status": r.status_code, "pass": r.status_code == 405, "shows": "405 Method Not Allowed"})
    except Exception as e:  # noqa: BLE001
        rows.append({"step": "reach your address", "pass": False, "shows": f"{type(e).__name__}: {str(e)[:160]}"})
    con = ws.connected() if ws else None
    rows.append({"step": "a real client (Claude) has connected", "pass": None,
                 "shows": f"yes: {con['client']}" if con else "not yet: do the Connect tab"})
    ok = all(r["pass"] for r in rows if r["pass"] is not None)
    return ok, f"{sum(1 for r in rows if r['pass'])} of {sum(1 for r in rows if r['pass'] is not None)} protocol checks pass" + \
        (f"; Claude connected ({con['client']})" if con else "; Claude not connected yet"), rows


def c_regression(config, results=None, **kw):
    res = results or {}
    need = {}
    for cid in ("schema", "reliability", "timeouts", "permissions"):
        if cid not in res:
            ok, head, rows = CHECKS[cid](config, **kw)
            res[cid] = {"pass": ok, "rows": rows}
    sch = {r["tool"]: r for r in res["schema"]["rows"]}
    rel = {r["tool"]: r for r in (res["reliability"]["rows"] or {}).get("rows", [])}
    tmo = {r["tool"]: r for r in res["timeouts"]["rows"]}
    rows = []
    for n in on_tools(config):
        row = {"tool": n, "writes": F.REGISTRY[n].writes, "happy_and_schema": sch.get(n, {}).get("pass"),
               "fuzzing": rel.get(n, {}).get("pass"), "faults": tmo.get(n, {}).get("pass")}
        if F.REGISTRY[n].writes and res["permissions"]["pass"] is not None:
            row["permission"] = res["permissions"]["pass"]
        row["pass"] = all(v for k, v in row.items() if k not in ("tool", "writes", "pass") and v is not None)
        rows.append(row)
    w = [r for r in rows if r["writes"]]
    share = sum(r["pass"] for r in rows) / len(rows) if rows else 0
    ok = share >= 0.98 and all(r["pass"] for r in w)
    return ok, f"{sum(r['pass'] for r in rows)} of {len(rows)} tools pass every case; write tools {sum(r['pass'] for r in w)} of {len(w)}", rows


def c_change(config, ws=None, **_):
    rows = []
    notes = (ws.notes if ws else []) or []
    for n in [x for x in F.TOOLS if config["tools"][x]["on"]]:
        k = config["tools"][n]
        v = F.version_of(n, k)
        edited = v != F.REGISTRY[n].spec.get("version", "1.0")
        noted = any(x.get("tool") == n and x.get("version") == v for x in notes) if edited else True
        rows.append({"tool": n, "version": v, "edited": edited, "note": noted, "pass": bool(v) and noted})
    ok = all(r["pass"] for r in rows)
    return ok, (f"{len(rows)} tools versioned in tools/list; {sum(r['edited'] for r in rows)} edited, each with a note; "
                f"rollback: 'Reset to shipped' on each card. Sign-off with the client is a step outside the sandbox."), rows


CHECKS = {"schema": c_schema, "reliability": c_reliability, "usability": c_usability, "latency": c_latency,
          "payload": c_payload, "idempotency": c_idempotency, "timeouts": c_timeouts, "permissions": c_permissions,
          "audit": c_audit, "mcp": c_mcp, "regression": c_regression, "change": c_change}


def check(cid: str, config: dict, **kw) -> dict:
    t0 = time.time()
    ok, head, rows = CHECKS[cid](config, **kw)
    return {**C[cid], "pass": ok, "headline": head, "rows": rows, "seconds": round(time.time() - t0, 2), "at": time.time(),
            "settings": F.diff(config)}
