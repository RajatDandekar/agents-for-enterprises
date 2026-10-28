"""Engine tests: every template on a fresh Rasoi, the approval wait (saved, reloaded, resumed), error paths, the API.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script bahi/bahi/experience/studio/tests/test_engine.py --mode auto
    ... --mode replay      # proves the LLM and agent templates replay from studio/cassettes with no key
"""
import json
import os
import pathlib
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))  # .../bahi (the package root), when run outside PYTHONPATH

from bahi.experience.players import Players  # noqa: E402
from bahi.experience.studio.engine import Engine, Store, StudioError, evaluate, fill  # noqa: E402
from bahi.experience.studio.templates import TEMPLATES, template  # noqa: E402

LOG = HERE.parent / "tests" / "logs"
LOG.mkdir(exist_ok=True)
results, fails = [], []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("  PASS " if cond else "  FAIL ") + name + ("" if cond else f"  -- {str(detail)[:400]}"))
    if not cond:
        fails.append((name, detail))


def fresh(store=None):
    players = Players()
    p = players.join("Test engineer")
    eng = Engine(toolbox_for=lambda user, names=None: players.toolbox(p.pid, user, names), store=store or Store(),
                 pid=p.pid)
    return players, p.pid, eng


def show(run):
    for nid, r in run["nodes"].items():
        print(f"     {nid:18} {r['status']:8} {str(r.get('summary') or r.get('error') or '')[:150]}")
    print(f"     -> {run['status']} {run.get('error') or ''}")


# ---------------------------------------------------------------- 1. templates and expressions
print("\n1. Templates and expressions")
ctx = {"nodes": {"pr": {"request_no": "PR/2026/04417", "status": "APPROVED"},
                 "stock": {"reorder_level": 30000, "warehouses": [{"on_hand": 54000}]}}, "trigger": {}, "today": "2026-10-26"}
check("whole field keeps its type", fill("{{ nodes.stock.reorder_level * 3 }}", ctx) == 90000)
check("text interpolation", fill("PR {{nodes.pr.request_no}} is {{nodes.pr.status}}", ctx) == "PR PR/2026/04417 is APPROVED")
check("list index", fill("{{nodes.stock.warehouses[0].on_hand}}", ctx) == 54000)
check("add_days", fill("{{ add_days(today, 14) }}", ctx) == "2026-11-09")
check("nested dict filled", fill({"a": {"b": "{{nodes.pr.status}}"}}, ctx) == {"a": {"b": "APPROVED"}})
for bad in ["__import__('os').system('ls')", "nodes.pr.__class__", "open('x')", "(lambda: 1)()"]:
    try:
        evaluate(bad, ctx)
        check(f"refuses {bad}", False, "it ran")
    except StudioError:
        check(f"refuses {bad}", True)
try:
    fill("{{nodes.pr.po_no}}", ctx)
    check("missing field names what exists", False)
except StudioError as e:
    check("missing field names what exists", "request_no" in str(e), str(e))

# ---------------------------------------------------------------- 2. validation
print("\n2. Validation")
_, _, eng = fresh()
for tid in TEMPLATES:
    check(f"template {tid} is valid", eng.validate(template(tid)) == [], eng.validate(template(tid)))
bad = template("diwali-gasket-order")
bad["nodes"][1]["config"]["tool"] = "make_tea"
bad["nodes"].append({"id": "start2", "type": "trigger", "config": {"kind": "manual"}})
bad["edges"].append({"from": "tell", "to": "stock"})
probs = eng.validate(bad)
check("unknown tool reported", any("make_tea" in p for p in probs), probs)
check("two triggers reported", any("exactly one trigger" in p for p in probs), probs)
loop = template("diwali-gasket-order")
loop["edges"].append({"from": "tell", "to": "stock"})
check("a loop is reported", any("loop" in p for p in eng.validate(loop)), eng.validate(loop))
try:
    eng.start(bad)
    check("an invalid workflow does not start", False)
except StudioError as e:
    check("an invalid workflow does not start", "cannot run" in str(e))

# ---------------------------------------------------------------- 3. (a) Diwali gasket order, with a persisted wait
print("\n3. (a) Diwali gasket order: pause for Rohit, save, reload, approve, resume")
folder = tempfile.mkdtemp()
players, pid, eng = fresh(Store(folder))
wf = template("diwali-gasket-order")
eng.store.save_workflow(pid, wf)
t0 = time.perf_counter()
run = eng.run_until_pause(eng.start(wf))
show(run)
check("(a) pauses at the approval", run["status"] == "waiting" and run["nodes"]["rohit"]["status"] == "waiting", run["status"])
check("(a) waits for Rohit on PR/2026/04417", run["waiting_for"] == {"node": "rohit", "doc_no": "PR/2026/04417",
      "approver": "RMEHTA", "approver_name": "Rohit Mehta"}, run["waiting_for"])
check("(a) nothing ordered yet", run["nodes"]["po"]["status"] == "pending")
check("(a) PR estimate above Kavita's limit", run["nodes"]["pr"]["output"]["estimated_value"] > 250000,
      run["nodes"]["pr"]["output"])
eng.resume(run)
check("(a) resuming before anyone signed keeps waiting", run["status"] == "waiting")
# the wait is persisted: a brand-new store and engine (another web process) pick it up from disk
store2 = Store(folder)
eng2 = Engine(toolbox_for=lambda user, names=None: players.toolbox(pid, user, names), store=store2, pid=pid)
loaded = store2.run(pid, run["id"])
check("(a) the waiting run is on disk", loaded and loaded["status"] == "waiting", loaded and loaded["status"])
try:
    # Kavita cannot approve her own request: approving as the raiser is refused by Bahi
    r_self = players.toolbox(pid, "KJOSHI").call("approve_purchase_request", {"request_no": "PR/2026/04417", "decision": "approve"})
    check("(a) Kavita cannot approve her own PR", not r_self.get("ok"), r_self)
except Exception as e:
    check("(a) Kavita cannot approve her own PR", False, e)
eng2.approve(loaded)
eng2.run_until_pause(loaded)
show(loaded)
n = loaded["nodes"]
check("(a) finishes done", loaded["status"] == "done", loaded.get("error"))
check("(a) approval waited and passed", n["rohit"]["status"] == "done" and n["rohit"]["output"]["waited"], n["rohit"])
check("(a) PO/2026/01182 at Rs 2,80,840", n["po"]["output"].get("po_no") == "PO/2026/01182"
      and n["po"]["output"].get("gross_value") == 280840, n["po"]["output"])
check("(a) released to Deccan", n["release"]["output"].get("sent_to_supplier") is True, n["release"]["output"])
check("(a) Rohit messaged", n["tell"]["output"].get("queued") and "PO/2026/01182" in n["tell"]["output"]["text"],
      n["tell"]["output"])
check("(a) run log has every node", {e["node"] for e in loaded["log"] if e["node"]} >= set(n), loaded["log"])
# idempotency: the same workflow again on the same Rasoi finds the same documents
again = eng2.run_until_pause(eng2.start(wf))
show(again)
check("(a) second run finds the same PR (idempotent)", again["nodes"]["pr"]["output"].get("already_done")
      and again["nodes"]["pr"]["output"]["request_no"] == "PR/2026/04417", again["nodes"]["pr"]["output"])
n_po = players.erp(pid).q1("SELECT count(*) AS c FROM po_hdr WHERE pr_no=?", "PR/2026/04417")["c"]
check("(a) second run makes no second PO", n_po == 1, n_po)
print("     second run's PO node:", again["nodes"]["po"]["status"], str(again["nodes"]["po"].get("summary"))[:160])
diwali_seconds = round(time.perf_counter() - t0, 2)

# ---------------------------------------------------------------- 4. (c) Goods arrived, on the Diwali order and fresh
print("\n4. (c) Goods arrived")
g = template("goods-arrived")
r1 = eng2.run_until_pause(eng2.start(g, {"po_no": "PO/2026/01182", "quantity": 12000, "vehicle": "GJ-03-AX-2210"}))
show(r1)
check("(c) GRN/2026/30001 for 12,000 as Neha", r1["status"] == "done"
      and r1["nodes"]["grn"]["output"].get("grn_no") == "GRN/2026/30001" and r1["nodes"]["grn"]["output"]["balance"] == 8000,
      r1["nodes"]["grn"]["output"])
r2 = eng2.run_until_pause(eng2.start(g, {"po_no": "PO/2026/01182", "quantity": 8000, "vehicle": "GJ-03-AX-2291"}))
check("(c) GRN/2026/30002 closes the order", r2["nodes"]["grn"]["output"].get("grn_no") == "GRN/2026/30002"
      and r2["nodes"]["status"]["output"]["status"].startswith("CLOSED"), r2["nodes"]["status"]["output"])
r3 = eng2.run_until_pause(eng2.start(g, {"po_no": "PO/2026/01182", "quantity": 500, "vehicle": "X"}))
check("(c) receiving more than ordered fails with Bahi's reason", r3["status"] == "failed"
      and r3["nodes"]["grn"]["status"] == "error", r3.get("error"))
print("     over-receipt error:", r3.get("error"))
_, pid_c, eng_c = fresh()
rc = eng_c.run_until_pause(eng_c.start(template("goods-arrived")))  # the form's defaults, fresh Rasoi
show(rc)
check("(c) runs end to end on a fresh Rasoi with the form defaults", rc["status"] == "done"
      and rc["nodes"]["grn"]["output"].get("order_closed"), rc.get("error"))
re_ = eng_c.run_until_pause(eng_c.start(template("goods-arrived"), {"po_no": "", "quantity": 10}))
check("(c) an empty form field fails the trigger with a clear message", re_["status"] == "failed"
      and "empty" in (re_.get("error") or ""), re_.get("error"))

# ---------------------------------------------------------------- 5. (b) Reorder when low
print("\n5. (b) Reorder when low")
_, pid_b, eng_b = fresh()
wb = template("reorder-when-low")
rb = eng_b.run_until_pause(eng_b.start(wb))
show(rb)
check("(b) fires for WHS-STD-01 (8,000 < 12,000)", rb["nodes"]["low"]["output"].get("item_code") == "WHS-STD-01",
      rb["nodes"]["low"]["output"])
check("(b) plans 36,000 from Sahyadri Valves", rb["nodes"]["plan"]["output"] == {"quantity": 36000, "supplier": "SV-PUN-0017",
      "need_by": "2026-11-09"}, rb["nodes"]["plan"]["output"])
check("(b) branch takes the yes path; the no path is skipped", rb["nodes"]["nothing_on_order"]["output"]["branch"] == "true"
      and rb["nodes"]["note"]["status"] == "skipped", rb["nodes"]["note"])
check("(b) waits for Rohit", rb["status"] == "waiting" and rb["waiting_for"]["approver"] == "RMEHTA", rb["status"])
eng_b.approve(rb)
eng_b.run_until_pause(rb)
show(rb)
check("(b) ordered and released", rb["status"] == "done" and rb["nodes"]["release"]["output"].get("sent_to_supplier"),
      rb.get("error"))
rb2 = eng_b.run_until_pause(eng_b.start(wb))
check("(b) does not fire again once the order is on the way", rb2["status"] == "done"
      and rb2["nodes"]["low"]["output"]["fired"] is False and rb2["nodes"]["pr"]["status"] == "skipped",
      rb2["nodes"]["low"]["output"])
_, pid_b2, eng_b2 = fresh()
wno = template("reorder-when-low")
next(x for x in wno["nodes"] if x["id"] == "nothing_on_order")["config"]["if"] = "{{ trigger.on_order > 100 }}"
rno = eng_b2.run_until_pause(eng_b2.start(wno))
check("(b) the no path: only Kavita is told", rno["status"] == "done" and rno["nodes"]["note"]["status"] == "done"
      and rno["nodes"]["pr"]["status"] == "skipped" and rno["nodes"]["tell"]["status"] == "skipped", rno["nodes"]["note"])

# ---------------------------------------------------------------- 6. error paths: the traps
print("\n6. Error paths")
_, pid_e, eng_e = fresh()


def wf_of(*nodes, edges=None):
    ns = [{"id": "start", "type": "trigger", "x": 0, "config": {"kind": "manual"}}] + list(nodes)
    for i, x in enumerate(ns):
        x.setdefault("x", i * 250)
    return {"id": "t", "name": "test", "nodes": ns,
            "edges": edges if edges is not None else [{"from": a["id"], "to": b["id"]} for a, b in zip(ns, ns[1:])]}


closed = wf_of({"id": "po", "type": "tool", "config": {"tool": "create_purchase_order", "as": "KJOSHI", "confirm": True, "args": {
    "supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-03L", "quantity": 100, "cost_centre": "PRD-05", "need_by": "2026-11-09"}}},
    {"id": "release", "type": "tool", "config": {"tool": "release_purchase_order", "as": "KJOSHI", "args": {"po_no": "{{nodes.po.po_no}}"}}})
rcl = eng_e.run_until_pause(eng_e.start(closed))
show(rcl)
check("closed cost centre: the PO is a silent DRAFT and the run stops on the warning",
      rcl["status"] == "failed" and rcl["nodes"]["po"]["status"] == "warning" and "DRAFT" in rcl["error"]
      and rcl["nodes"]["release"]["status"] == "pending", rcl.get("error"))
prc = wf_of({"id": "pr", "type": "tool", "config": {"tool": "create_purchase_request", "as": "KJOSHI", "confirm": True, "args": {
    "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-05", "need_by": "2026-11-09"}}})
rpc = eng_e.run_until_pause(eng_e.start(prc))
check("closed cost centre on a PR: refused with what to do", rpc["status"] == "failed" and "closed" in rpc["error"].lower()
      and rpc["nodes"]["pr"]["output"].get("next_step"), rpc.get("error"))
pv = wf_of({"id": "pr", "type": "tool", "config": {"tool": "create_purchase_request", "as": "KJOSHI", "confirm": False,
                                                    "stop_on_warning": False, "args": {
    "item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-05", "need_by": "2026-11-09"}}})
rpv = eng_e.run_until_pause(eng_e.start(pv))
check("preview with stop_on_warning off: warning shown, run done, nothing saved",
      rpv["status"] == "done" and rpv["nodes"]["pr"]["status"] == "warning" and "preview" in rpv["nodes"]["pr"]["output"],
      rpv["nodes"]["pr"])
cap = wf_of({"id": "po", "type": "tool", "config": {"tool": "create_purchase_order", "as": "KJOSHI", "confirm": True, "args": {
    "supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "quantity": 15000, "cost_centre": "PRD-07", "need_by": "2026-11-09"}}},
    {"id": "ok", "type": "message", "config": {"to": "@rohit", "text": "ordered {{nodes.po.po_no}}"}},
    {"id": "oops", "type": "message", "y": 200, "config": {"to": "@kavita", "as": "KJOSHI",
                                                        "text": "Direct order refused: {{nodes.po.error}} {{nodes.po.next_step}}"}},
    edges=[{"from": "start", "to": "po"}, {"from": "po", "to": "ok"}, {"from": "po", "port": "error", "to": "oops"}])
rcap = eng_e.run_until_pause(eng_e.start(cap))
show(rcap)
check("direct-PO cap: the error path runs and the run ends done", rcap["status"] == "done"
      and rcap["nodes"]["po"]["status"] == "error" and "50,000" in rcap["nodes"]["po"]["output"]["error"]
      and rcap["nodes"]["oops"]["status"] == "done" and rcap["nodes"]["ok"]["status"] == "skipped", rcap["nodes"]["po"])
capno = wf_of(*[x for x in cap["nodes"][1:2]])
rcn = eng_e.run_until_pause(eng_e.start(capno))
check("direct-PO cap with no error path: the run fails naming the node", rcn["status"] == "failed"
      and rcn["error"].startswith("po:") or "50,000" in (rcn.get("error") or ""), rcn.get("error"))
neha = wf_of({"id": "m", "type": "message", "config": {"to": "@kavita", "as": "NDESAI", "text": "hi"}})
rn = eng_e.run_until_pause(eng_e.start(neha))
check("permissions hold: Neha cannot send messages", rn["status"] == "failed", rn.get("error"))
print("     Neha:", rn.get("error"))
badref = wf_of({"id": "m", "type": "message", "config": {"to": "@kavita", "text": "{{ nodes.start.po_no }}"}})
rbr = eng_e.run_until_pause(eng_e.start(badref))
check("a bad template path fails with a clear message", rbr["status"] == "failed" and "no field 'po_no'" in rbr["error"],
      rbr.get("error"))
draft = wf_of({"id": "wait", "type": "approval", "config": {"doc_no": "{{ trigger.po }}", "approver": "RMEHTA"}})
draft["nodes"][0]["config"]["data"] = {"po": rcl["nodes"]["po"]["output"]["po_no"]}
rdr = eng_e.run_until_pause(eng_e.start(draft))
check("approval on a DRAFT says nobody will be asked", rdr["status"] == "failed" and "DRAFT" in rdr["error"], rdr.get("error"))
rej = template("diwali-gasket-order")
_, pid_r, eng_r = fresh()
rr = eng_r.run_until_pause(eng_r.start(rej))
eng_r.approve(rr, "reject", "Not this week")
eng_r.run_until_pause(rr)
check("a rejected PR stops the run before any order", rr["status"] == "failed" and rr["nodes"]["po"]["status"] == "pending"
      and "rejected" in rr["error"], rr.get("error"))

# ---------------------------------------------------------------- 7. (d) Dealer email to order: an LLM node
print("\n7. (d) Dealer email to order (LLM node, cassette studio)")
_, pid_d, eng_d = fresh()
rd = eng_d.run_until_pause(eng_d.start(template("dealer-email-to-order")))
show(rd)
ex = rd["nodes"]["extract"]
check("(d) the LLM node extracts quantity and date", ex["status"] == "done" and ex["output"].get("quantity") == 4000
      and ex["output"].get("need_by") == "2026-11-12", ex.get("output") or ex.get("error"))
check("(d) finds GSK-SIL-05L and raises the PR", rd["status"] == "done"
      and rd["nodes"]["pr"]["output"].get("item_code") == "GSK-SIL-05L" and rd["nodes"]["pr"]["output"].get("request_no"),
      rd.get("error"))
print("     LLM meta:", ex.get("meta"))

# ---------------------------------------------------------------- 8. (e) Build your own agent: chat
print("\n8. (e) Build your own agent (agent node, chat)")
_, pid_a, eng_a = fresh()
wa = template("build-your-own-agent")
eng_a.store.save_workflow(pid_a, wa)
turns = ["How many days of cover do we have for the 5 litre silicone gasket?",
         "Raise a purchase request for 20,000 of them on cost centre PRD-07, needed by 9 November 2026.",
         "Yes, go ahead and raise it."]
replies = []
for t in turns:
    reply, ra = eng_a.chat(wa, t)
    calls = ra["nodes"]["desk"]["output"].get("tool_calls", []) if ra["nodes"]["desk"]["output"] else []
    replies.append({"user": t, "reply": reply, "tools": [(c["tool"], c["args"].get("confirm")) for c in calls],
                    "status": ra["status"], "meta": ra["nodes"]["desk"].get("meta")})
    print(f"     you: {t}\n     agent: {reply[:300]}\n     tools: {replies[-1]['tools']}")
check("(e) turn 1 uses check_stock and answers with a number", any(c == "check_stock" for c, _ in replies[0]["tools"])
      and any(ch.isdigit() for ch in replies[0]["reply"]), replies[0])
all_tools = [c for r in replies for c in r["tools"]]
check("(e) the agent previews or raises the PR", any(c == "create_purchase_request" for c, _ in all_tools), all_tools)
st = eng_a.toolbox_for("KJOSHI").call("order_status", {"request_no": "PR/2026/04417"})
check("(e) after 'yes' the PR exists in Bahi", st.get("ok") and st.get("quantity") == 20000, st)
check("(e) the chat history is kept", len(eng_a.store.chat(pid_a, wa["id"])) == 6)

# ---------------------------------------------------------------- 9. the API, in a minimal FastAPI app
print("\n9. API (make_router in a minimal FastAPI app)")
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from bahi.experience.studio.api import make_router  # noqa: E402

pl = Players()
app = FastAPI()
app.include_router(make_router(pl))
c = TestClient(app)
page = c.get("/studio")
check("GET /studio serves the page and sets a pid cookie", page.status_code == 200 and "pid" in page.cookies, page.status_code)
pidc = page.cookies.get("pid")
H = {"X-Player": pidc}
check("static app.js served", c.get("/studio/static/app.js").status_code == 200)
check("static path traversal refused", c.get("/studio/static/..%2Fapi.py").status_code == 404)
nd = c.get("/api/studio/nodes", headers=H).json()
check("palette lists 15 tools and the node types", len(nd["tools"]) == 15 and len(nd["types"]) >= 10, len(nd["tools"]))
check("palette carries input_schema, no python", "input_schema" in nd["tools"][0] and "python" not in nd["tools"][0])
check("5 templates", len(c.get("/api/studio/templates").json()) == 5)
w = c.post("/api/studio/templates/diwali-gasket-order/use", headers=H).json()
check("use template saves a workflow", w["id"] == "diwali-gasket-order" and len(c.get("/api/studio/workflows", headers=H).json()) == 1)
w2 = c.post("/api/studio/templates/diwali-gasket-order/use", headers=H).json()
check("using it twice gives a new id", w2["id"] == "diwali-gasket-order-2", w2["id"])
put = c.put(f"/api/studio/workflows/{w2['id']}", json={**w2, "name": "My copy"}, headers=H).json()
check("save returns problems (none)", put["problems"] == [] and put["name"] == "My copy", put.get("problems"))
run = c.post(f"/api/studio/workflows/{w['id']}/run", json={"mode": "step"}, headers=H).json()
check("run in step mode: only the trigger ran", run["nodes"]["start"]["status"] == "done"
      and run["nodes"]["stock"]["status"] == "pending")
steps = 0
while run["status"] == "running" and steps < 20:
    run = c.post(f"/api/studio/runs/{run['id']}/step", headers=H).json()
    steps += 1
check("stepping reaches the wait", run["status"] == "waiting", run["status"])
inbox = c.get("/api/studio/approvals?user=RMEHTA", headers=H).json()
check("Rohit's inbox has the PR", any(x.get("doc_no") == "PR/2026/04417" for x in inbox.get("waiting", [])), inbox)
doc = c.get("/api/studio/document?doc_no=PR/2026/04417&user=RMEHTA", headers=H).json()
check("the approval sheet reads the document", doc.get("quantity") == 20000, doc)
run = c.post(f"/api/studio/runs/{run['id']}/approve", json={"decision": "approve"}, headers=H).json()
run = c.post(f"/api/studio/runs/{run['id']}/continue", headers=H).json()
check("approve + continue finishes the run", run["status"] == "done" and run["nodes"]["release"]["output"]["sent_to_supplier"],
      run.get("error"))
check("run history lists it", c.get(f"/api/studio/runs?workflow_id={w['id']}", headers=H).json()[0]["status"] == "done")
bad_run = c.post(f"/api/studio/runs/{run['id']}/approve", json={}, headers=H)
check("approving a finished run is a 400 with a reason", bad_run.status_code == 400 and "not waiting" in bad_run.json()["detail"])
ev = c.post("/api/studio/templates/reorder-when-low/use", headers=H).json()
fired = c.post("/api/studio/events/check", headers=H).json()
check("events/check starts the reorder workflow for WHS-STD-01", fired["started"] and fired["started"][0]["item_code"] == "WHS-STD-01"
      and fired["started"][0]["status"] == "waiting", fired)
ag = c.post("/api/studio/templates/build-your-own-agent/use", headers=H).json()
ch = c.post(f"/api/studio/workflows/{ag['id']}/chat", json={"message": turns[0]}, headers=H).json()
check("chat endpoint replies", ch.get("reply") and len(ch["history"]) == 2, ch.get("reply"))
check("reset gives a fresh Rasoi", c.post("/api/studio/reset", headers=H).json()["ok"]
      and c.get("/api/studio/document?doc_no=PR/2026/04417&user=RMEHTA", headers=H).json().get("ok") is False)

# ---------------------------------------------------------------- 10. mounted inside the experience app (if it imports here)
print("\n10. Inside the experience app (bahi.experience.app.create_app)")
try:
    os.environ["RASOI_NO_APP"] = "1"
    from bahi.experience.app import create_app  # noqa: E402

    xc = TestClient(create_app())
    pg = xc.get("/studio")
    check("the experience app serves the Studio at /studio", pg.status_code == 200 and "/studio/static/app.js" in pg.text,
          pg.text[:200])
    check("and its API", xc.get("/api/studio/templates").status_code == 200 and len(xc.get("/api/studio/templates").json()) == 5)
except Exception as e:  # the experience app is another builder's; report, do not fail the Studio's own tests
    print(f"     skipped: the experience app did not import here ({type(e).__name__}: {str(e)[:200]})")

# ---------------------------------------------------------------- summary
passed = sum(ok for _, ok in results)
summary = {"passed": passed, "total": len(results), "fails": [f[0] for f in fails], "diwali_seconds": diwali_seconds,
           "mode": os.environ.get("BAHI_LLM_MODE", "auto"), "agent_chat": replies,
           "llm_meta": rd["nodes"]["extract"].get("meta")}
(LOG / f"engine_{summary['mode']}.json").write_text(json.dumps(summary, indent=1, default=str))
print(f"\n{passed}/{len(results)} checks passed")
if fails:
    sys.exit(1)
print("STUDIO ENGINE OK")
