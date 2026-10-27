"""Lecture 3: the six-step tool-building method, done for real on the purchase-order screen (no model calls).

    1 inventory     screens -> tasks -> services -> procedures, from the service registry and the procedure logs
    2 live runs     drive the legacy sequence with screen/task tags and record erp.live_run()
    3 cascades      what each save sets off (budget commit, approval routing, notifications, stock on order)
    4 variants      STD vs DIR (ERR-PO-0610)
    5 screen state  Fetch before Save (fetch token, ERR-SCR-0221)
    6 intent tool   create_purchase_order: what it hides, its preview, receipt, idempotency, permissions

Writes logs/{inventory,live_runs,cascades,variants,screen_state,intent_tool,contract,tool_defs}.json
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "bahi"))

from bahi.agent.tools import (ALL, CORE, TOOL_CONTRACT, TOOLS, GenericServiceTool, IntentTools,  # noqa: E402
                              RawServiceTools)
from bahi.erp.engine import ERP, PROCS, SERVICES, ServiceTimeout  # noqa: E402

LOG = pathlib.Path(__file__).parent / "logs"
LOG.mkdir(exist_ok=True)


def dump(name, obj):
    (LOG / f"{name}.json").write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str))
    print("wrote", name)


def calls_since(erp, n):
    return [{"seq": c.seq, "user": c.user, "screen": c.screen, "task": c.task, "svc": c.svc, "payload": c.payload,
             "rc": c.rc, "err_cd": c.err_cd, "msg": c.msg, "sps": c.sps, "data": c.data, "timed_out": c.timed_out}
            for c in erp.calls[n:]]


# ----------------------------------------------------------------------------- cascades: what changed in the database
def state(erp):
    return {"budget": {r["cc_cd"]: r["committed"] for r in erp.q("SELECT * FROM budget")},
            "approval": erp.q("SELECT * FROM approval"),
            "ntf": erp.q("SELECT * FROM ntf_queue"),
            "stock": {(r["itm_cd"], r["whs_cd"]): r["on_order"] for r in erp.q("SELECT * FROM stock")},
            "pr": {r["pr_no"]: r["status"] for r in erp.q("SELECT * FROM pr_hdr")},
            "po": {r["po_no"]: (r["status"], r["warn_cd"]) for r in erp.q("SELECT * FROM po_hdr")},
            "seq": {r["doc_type"]: r["next_no"] for r in erp.q("SELECT * FROM doc_seq")}}


def diff(a, b):
    out = []
    for cc, v in b["budget"].items():
        if abs(v - a["budget"].get(cc, 0)) > 1e-6:
            out.append({"kind": "budget commit", "what": f"{cc} committed {a['budget'][cc]:,.2f} -> {v:,.2f}",
                        "delta": round(v - a["budget"][cc], 2), "table": "budget"})
    ids = {r["appr_id"] for r in a["approval"]}
    for r in b["approval"]:
        if r["appr_id"] not in ids:
            out.append({"kind": "approval routing", "what": f"{r['doc_type']} {r['doc_no']} -> {r['approver']} ({r['status']})",
                        "table": "approval"})
    old = {r["appr_id"]: r["status"] for r in a["approval"]}
    for r in b["approval"]:
        if r["appr_id"] in old and old[r["appr_id"]] != r["status"]:
            out.append({"kind": "approval decided", "what": f"{r['doc_no']} {old[r['appr_id']]} -> {r['status']} by {r['approver']}",
                        "table": "approval"})
    nids = {r["id"] for r in a["ntf"]}
    for r in b["ntf"]:
        if r["id"] not in nids:
            out.append({"kind": "notification", "what": f"{r['channel']} to {r['recipient']}: {r['subject']}", "table": "ntf_queue"})
    for k, v in b["stock"].items():
        if v != a["stock"].get(k):
            out.append({"kind": "stock on order", "what": f"{k[0]} @ {k[1]} on order {a['stock'][k]:,} -> {v:,}", "table": "stock"})
    for k, v in b["pr"].items():
        if a["pr"].get(k) != v:
            out.append({"kind": "document status", "what": f"{k}: {a['pr'].get(k) or 'new'} -> {v}", "table": "pr_hdr"})
    for k, v in b["po"].items():
        if a["po"].get(k) != v:
            out.append({"kind": "document status", "what": f"{k}: {(a['po'].get(k) or ('new',))[0]} -> {v[0]}"
                        + (f" (warning {v[1]})" if v[1] else ""), "table": "po_hdr"})
    for k, v in b["seq"].items():
        if a["seq"][k] != v:
            out.append({"kind": "number used", "what": f"{k} sequence {a['seq'][k]} -> {v}", "table": "doc_seq"})
    return out


class Recorder:
    """Drive the legacy screens as a user would, tagging every service call with its screen and task."""

    def __init__(self, erp):
        self.erp, self.cascades = erp, []

    def do(self, user, screen, task, svc, **payload):
        before = state(self.erp)
        r = self.erp.session(user).call(svc, screen=screen, task=task, **payload)
        if SERVICES[svc].kind == "write":
            self.cascades.append({"seq": len(self.erp.calls), "user": user, "screen": screen, "task": task, "svc": svc,
                                  "rc": r["rc"], "err_cd": r["err_cd"], "msg": r["msg"],
                                  "sps": self.erp.calls[-1].sps, "changes": diff(before, state(self.erp))})
        return r


def legacy_order(cc_on_request: str):
    """Kavita's order through the legacy screens: request, Rohit's approval, order, release."""
    erp = ERP()
    rec = Recorder(erp)
    K, R = "KJOSHI", "RMEHTA"
    rec.do(K, "INV-ITM-03", "Search", "itm_search", q="gasket silicone")
    rec.do(K, "INV-STK-02", "Query", "stk_query", itm_cd="GSK-SIL-05L", whs_cd="WH-PUN-STR")
    rec.do(K, "PUR-POH-02", "History", "po_hist", itm_cd="GSK-SIL-05L")
    f = rec.do(K, "PUR-PR-01", "Fetch", "pr_fetch", itm_cd="GSK-SIL-05L")["data"]
    pr = rec.do(K, "PUR-PR-01", "Save", "pr_save", cc_cd=cc_on_request, need_dt="2026-11-02", itm_cd="GSK-SIL-05L",
                qty=20000, whs_cd=f["whs_cd"], est_rate=f["est_rate"])["data"]["pr_no"]
    rec.do(K, "PUR-PR-01", "Submit", "pr_submit", pr_no=pr)
    rec.do(R, "PUR-PR-04", "Approve", "pr_approve", pr_no=pr, decision="A", comment="ok, Diwali run")
    rec.do(K, "PUR-SUP-03", "F2 supplier", "sup_search", q="deccan")
    fx = rec.do(K, "PUR-PO-01", "Fetch", "po_fetch", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", pr_no=pr)["data"]
    base = dict(po_type="STD", pr_no=pr, sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty=fx["qty"], rate=fx["rate"],
                cc_cd=fx["cc_cd"], need_dt=fx["need_dt"], whs_cd=fx["whs_cd"], fetch_tok=fx["fetch_tok"])
    r = rec.do(K, "PUR-PO-01", "Save", "po_save", tax_cd=fx["tax_cd"], **base)          # the Fetch default: GST18-INTRA
    if r["rc"] == "E":
        r = rec.do(K, "PUR-PO-01", "Save", "po_save", tax_cd="GST18-INTER", **base)     # she fixes the tax code
    po = r["data"]["doc_no"]
    rec.do(K, "PUR-POR-05", "Release", "po_release", po_no=po)
    rec.do(K, "PUR-POH-02", "View", "po_get", po_no=po)
    return erp, rec


def main():
    # ------------------------------------------------------------------ 2. live runs (first, inventory uses them)
    erpA, recA = legacy_order("PRD-05")   # as it happened: the default cost centre, closed on 15 Oct
    erpB, recB = legacy_order("PRD-07")   # the same order, charged to the open Diwali cost centre
    runA, runB = calls_since(erpA, 0), calls_since(erpB, 0)
    dump("live_runs", {
        "about": "Kavita's order driven through the legacy screens with screen/task tags; erp.live_run() plus each reply.",
        "as_it_happened_PRD05": runA, "done_right_PRD07": runB,
        "summary": {k: {"calls": len(v), "errors": [c["err_cd"] for c in v if c["rc"] == "E"],
                        "screens": sorted({c["screen"] for c in v}),
                        "procedures": sum(len(c["sps"]) for c in v),
                        "final": v[-1]["data"]["status"] if v[-1]["data"] else None}
                    for k, v in (("as_it_happened_PRD05", runA), ("done_right_PRD07", runB))},
        "live_run_api_example": erpB.live_run(since=len(runB) - 4)})

    # ------------------------------------------------------------------ 1. inventory
    seen = {}
    for c in runA + runB:
        seen.setdefault(c["screen"], {}).setdefault(c["task"], {}).setdefault(c["svc"], set()).update(c["sps"])
    by_screen = {}
    for s in SERVICES.values():
        by_screen.setdefault(s.screen or "(no screen: called by other screens and reports)", []).append(s.name)
    dump("inventory", {
        "counts": {"services": len(SERVICES), "read": sum(s.kind == "read" for s in SERVICES.values()),
                   "write": sum(s.kind == "write" for s in SERVICES.values()), "procedures": len(PROCS),
                   "screens_named_in_registry": len({s.screen for s in SERVICES.values() if s.screen}),
                   "max_fields": max(len(s.fields) for s in SERVICES.values())},
        "services": [{"name": s.name, "doc": s.doc, "kind": s.kind, "screen": s.screen,
                      "fields": [f.name + ("*" if f.required else "") for f in s.fields]} for s in SERVICES.values()],
        "services_by_screen": by_screen,
        "procedures": {n: (f.__doc__ or "").strip().split("\n")[0] for n, f in PROCS.items()},
        "tree_from_live_runs": {sc: {t: {svc: sorted(sps) for svc, sps in tasks.items()} for t, tasks in ts.items()}
                                for sc, ts in seen.items()},
        "po_screen": {t: {svc: sorted(sps) for svc, sps in tasks.items()} for t, tasks in seen["PUR-PO-01"].items()}})

    # ------------------------------------------------------------------ 3. cascades
    dump("cascades", {"about": "For every write in the two live runs: the stored procedures it ran and what changed.",
                      "as_it_happened_PRD05": recA.cascades, "done_right_PRD07": recB.cascades})

    # ------------------------------------------------------------------ 4. variants
    erp = ERP()
    k = erp.session("KJOSHI")
    pr_pa = k.call("pr_save", cc_cd="PRD-07", need_dt="2026-11-02", itm_cd="GSK-SIL-05L", qty=20000, est_rate=11.90)["data"]["pr_no"]
    k.call("pr_submit", pr_no=pr_pa)  # 2,80,840 > her limit: waits for Rohit
    pr_ap = k.call("pr_save", cc_cd="PRD-07", need_dt="2026-11-05", itm_cd="HDL-BKL-01", qty=4000, est_rate=18.50)["data"]["pr_no"]
    k.call("pr_submit", pr_no=pr_ap)  # 87,320 <= her limit: approved at once
    cases = [
        ("DIR above ₹50,000", dict(po_type="DIR", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty=20000, rate=11.90)),
        ("DIR at or below ₹50,000", dict(po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.80)),
        ("DIR that names a request", dict(po_type="DIR", pr_no=pr_ap, sup_cd="DP-RJK-0042", itm_cd="HDL-BKL-01", qty=4000, rate=18.50)),
        ("STD with no request", dict(po_type="STD", sup_cd="DP-RJK-0042", itm_cd="HDL-BKL-01", qty=4000, rate=18.50)),
        ("STD on a request still waiting", dict(po_type="STD", pr_no=pr_pa, sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L", qty=20000, rate=11.90)),
        ("STD on an approved request", dict(po_type="STD", pr_no=pr_ap, sup_cd="DP-RJK-0042", itm_cd="HDL-BKL-01", qty=4000, rate=18.50)),
    ]
    out = []
    for label, p in cases:
        f = k.call("po_fetch", sup_cd=p["sup_cd"], itm_cd=p["itm_cd"], screen="PUR-PO-01", task="Fetch")["data"]
        tax = "GST18-INTRA" if p["sup_cd"].startswith(("SV", "OSM", "MS", "SP")) else "GST18-INTER"
        need = "2026-11-05" if p["itm_cd"] == "HDL-BKL-01" else ("2026-11-04" if p["itm_cd"] == "WHS-STD-01" else "2026-11-02")
        payload = {**p, "tax_cd": tax, "cc_cd": "PRD-07", "need_dt": need, "fetch_tok": f["fetch_tok"]}
        r = k.call("po_save", screen="PUR-PO-01", task="Save", **payload)
        basic = round(p["qty"] * p["rate"], 2)
        out.append({"case": label, "payload": payload, "gross": round(basic * 1.18, 2), "rc": r["rc"], "err_cd": r["err_cd"],
                    "msg": r["msg"], "data": r["data"], "sps": erp.calls[-1].sps})
    dump("variants", {"about": "One Save button, two legal paths. STD needs an approved request; DIR only up to ₹50,000 gross.",
                      "requests": {"waiting": pr_pa, "approved": pr_ap}, "cases": out})

    # ------------------------------------------------------------------ 5. screen state
    erp = ERP()
    k, s2 = erp.session("KJOSHI"), erp.session("SKULKARNI")
    base = dict(po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.80, tax_cd="GST18-INTRA",
                cc_cd="PRD-07", need_dt="2026-11-04")
    cases = []

    def save(label, sess, tok, **over):
        r = sess.call("po_save", screen="PUR-PO-01", task="Save", **{**base, **over, **({"fetch_tok": tok} if tok else {})})
        cases.append({"case": label, "user": sess.user_id, "fetch_tok": tok, "rc": r["rc"], "err_cd": r["err_cd"],
                      "msg": r["msg"], "data": r["data"], "sps": erp.calls[-1].sps})
        return r

    save("Save with no Fetch", k, None)
    t_other = k.call("po_fetch", sup_cd="DP-RJK-0042", itm_cd="HDL-BKL-01", screen="PUR-PO-01", task="Fetch")["data"]["fetch_tok"]
    save("Fetch for another supplier and item, then Save", k, t_other)
    t = k.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", screen="PUR-PO-01", task="Fetch")["data"]["fetch_tok"]
    save("Someone else's Fetch token", s2, t)
    save("Fetch, then Save", k, t)
    save("Save again with the same token", k, t)
    fetch_reply = erp.calls[[c.svc for c in erp.calls].index("po_fetch")].data
    dump("screen_state", {"about": "Save must follow a Fetch by the same user for the same supplier and item; a token is used once.",
                          "fetch_reply_example": fetch_reply, "cases": cases,
                          "fetch_tok_rows": erp.q("SELECT * FROM fetch_tok")})

    # ------------------------------------------------------------------ 6. the intent tool
    erp = ERP()
    tools = IntentTools(erp.session("KJOSHI"), ALL)
    args = dict(supplier_code="DP-RJK-0042", item_code="GSK-SIL-05L", quantity=20000, cost_centre="PRD-07", need_by="2026-11-02")
    steps = []

    def tcall(label, name, a, actor="KJOSHI"):
        n0 = len(erp.calls)
        res = tools.call(name, a)
        steps.append({"label": label, "tool": name, "args": a, "result": res, "services": calls_since(erp, n0)})
        return res

    tcall("preview", "create_purchase_order", args)
    w = tcall("commit: request raised", "create_purchase_order", {**args, "confirm": True})
    n0 = len(erp.calls)
    erp.session("RMEHTA").call("pr_approve", pr_no=w["request_no"], decision="A", comment="ok", screen="PUR-PR-04", task="Approve")
    steps.append({"label": "Rohit approves (outside the tool)", "tool": None, "args": None, "result": None,
                  "services": calls_since(erp, n0)})
    tcall("commit again, same arguments: the order", "create_purchase_order", {**args, "confirm": True})
    rel = tcall("release", "release_purchase_order", {"po_no": "PO/2026/01182"})
    tcall("retry of the commit: idempotent", "create_purchase_order", {**args, "confirm": True})
    hidden = [c for st in steps if st["tool"] for c in st["services"]]
    summary = {"tool_calls": sum(1 for st in steps if st["tool"]), "services_hidden": len(hidden),
               "distinct_services": sorted({c["svc"] for c in hidden}),
               "procedures_run": sum(len(c["sps"]) for c in hidden),
               "legacy_calls_same_order": len(runB), "legacy_screens_same_order": len({c["screen"] for c in runB}),
               "final_receipt": rel}

    # the silent Draft, through the tool vs through the screen
    erp5 = ERP()
    t5 = IntentTools(erp5.session("KJOSHI"), ALL)
    a5 = dict(supplier_code="SV-PUN-0017", item_code="WHS-STD-01", quantity=3000, cost_centre="PRD-05", need_by="2026-11-04")
    prev5 = t5.call("create_purchase_order", a5)
    rec5 = t5.call("create_purchase_order", {**a5, "confirm": True})
    po_save5 = [c for c in calls_since(erp5, 0) if c["svc"] == "po_save"][0]

    # idempotency: a lost reply, retried by a raw client vs by the tool
    erpR = ERP()
    k = erpR.session("KJOSHI")
    erpR.inject("po_save", "timeout_after_commit", 1)
    raw_attempts = []
    for attempt in (1, 2):
        f = k.call("po_fetch", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01")["data"]
        try:
            r = k.call("po_save", po_type="DIR", sup_cd="SV-PUN-0017", itm_cd="WHS-STD-01", qty=3000, rate=6.80,
                       tax_cd="GST18-INTRA", cc_cd="PRD-07", need_dt="2026-11-04", fetch_tok=f["fetch_tok"])
            raw_attempts.append({"attempt": attempt, "reply": r})
        except ServiceTimeout as e:
            raw_attempts.append({"attempt": attempt, "reply": f"TIMEOUT: {e}"})
    raw_orders = [{k2: o[k2] for k2 in ("po_no", "status", "qty", "gross_value", "client_ref")}
                  for o in erpR.orders(itm_cd="WHS-STD-01", created_by="KJOSHI") if o["created_on"] >= "2026-10-26"]
    erpT = ERP()
    tt = IntentTools(erpT.session("KJOSHI"), ALL)
    erpT.inject("po_save", "timeout_after_commit", 1)
    a6 = dict(supplier_code="SV-PUN-0017", item_code="WHS-STD-01", quantity=3000, cost_centre="PRD-07", need_by="2026-11-04",
              confirm=True)
    first = tt.call("create_purchase_order", a6)
    second = tt.call("create_purchase_order", a6)
    tool_orders = [{k2: o[k2] for k2 in ("po_no", "status", "qty", "gross_value", "client_ref")}
                   for o in erpT.orders(itm_cd="WHS-STD-01", created_by="KJOSHI") if o["created_on"] >= "2026-10-26"]
    timed_out = [c for c in calls_since(erpT, 0) if c["timed_out"]]

    # permissions: the same call in Kavita's session and in the service account's
    erpP = ERP()
    perm = {"kavita": erpP.session("KJOSHI").call("po_approve", po_no="PO/2026/01179"),
            "svc_agent": erpP.session("SVC_AGENT").call("po_approve", po_no="PO/2026/01179"),
            "po_01179_after": {k2: v for k2, v in erpP.q1("SELECT * FROM po_hdr WHERE po_no='PO/2026/01179'").items()
                               if k2 in ("po_no", "status", "gross_value", "created_by", "approved_by")}}

    # errors: the legacy envelope vs the tool's error
    erpE = ERP()
    tE = IntentTools(erpE.session("KJOSHI"), ALL)
    f = erpE.session("KJOSHI").call("po_fetch", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L")["data"]
    errors = {
        "legacy_tax": erpE.session("KJOSHI").call("po_save", po_type="DIR", sup_cd="DP-RJK-0042", itm_cd="GSK-SIL-05L",
                                                  qty=4000, rate=11.90, tax_cd=f["tax_cd"], cc_cd="PRD-07",
                                                  need_dt="2026-11-02", fetch_tok=f["fetch_tok"]),
        "legacy_blocked": erpE.session("KJOSHI").call(
            "po_save", po_type="DIR", sup_cd="DP-RJK-0009", itm_cd="HDL-BKL-01", qty=100, rate=18.5, tax_cd="GST18-INTER",
            cc_cd="PRD-07", need_dt="2026-11-02",
            fetch_tok=erpE.session("KJOSHI").call("po_fetch", sup_cd="DP-RJK-0009", itm_cd="HDL-BKL-01")["data"]["fetch_tok"]),
        "tool_blocked": tE.call("create_purchase_order", dict(supplier_code="DP-RJK-0009", item_code="HDL-BKL-01",
                                                               quantity=4000, cost_centre="PRD-07", need_by="2026-11-05")),
        "tool_bad_date": tE.call("create_purchase_order", dict(supplier_code="DP-RJK-0042", item_code="HDL-BKL-01",
                                                                quantity=4000, cost_centre="PRD-07", need_by="5 November")),
        "tool_past_date": tE.call("create_purchase_order", dict(supplier_code="DP-RJK-0042", item_code="HDL-BKL-01",
                                                                 quantity=400, cost_centre="PRD-07", need_by="2025-11-05",
                                                                 confirm=True)),
        "tool_register_near_duplicate": tE.call("register_supplier", dict(name="Deccan Polymer Industries", city="Rajkot",
                                                                          state="GJ", gstin="24AAACD1111K1Z1", confirm=True)),
        "tool_find_supplier": tE.call("find_supplier", {"name": "Deccan Polymer Industries"}),
    }

    dump("intent_tool", {"about": "create_purchase_order on Kavita's order, every service it called, and the contract demos.",
                         "args": args, "steps": steps, "summary": summary,
                         "silent_draft": {"legacy_message": po_save5["msg"], "legacy_data": po_save5["data"],
                                          "tool_preview": prev5, "tool_receipt": rec5},
                         "idempotency": {"raw_client_retry": raw_attempts, "raw_orders": raw_orders,
                                         "tool_first": first, "tool_second": second, "tool_orders": tool_orders,
                                         "timed_out_calls": timed_out},
                         "permissions": perm, "errors": errors})

    # ------------------------------------------------------------------ the contract and the three tool sets
    k = ERP().session("KJOSHI")
    sets = {"raw": RawServiceTools(k).schemas(), "intent": IntentTools(k, CORE).schemas(),
            "intent_all": IntentTools(k, ALL).schemas(), "generic": GenericServiceTool(k).schemas()}
    dump("tool_defs", {"about": "The tool definitions each agent receives, as sent to the model (chars; tokens are in tool_tokens.json).",
                       **{f"{n}_chars": len(json.dumps(v)) for n, v in sets.items()},
                       **{f"{n}_count": len(v) for n, v in sets.items()},
                       "schemas": sets})
    dump("contract", {"version": "1.0", "checklist": [{"item": a, "means": b} for a, b in TOOL_CONTRACT],
                      "tools": [TOOLS[n].manifest() | {"description": TOOLS[n].description} for n in ALL]})


if __name__ == "__main__":
    main()
