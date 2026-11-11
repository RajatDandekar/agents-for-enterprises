# %% [markdown]
# # Lecture 6 · The Studio: workflows and your own agents
#
# **AI Agents for Enterprises · Vizuara · Dr. Rajat Dandekar**
#
# Rasoi does not want a chat for everything. Every Monday someone checks which items are below their reorder
# level and raises requests. Every delivery, Neha records the goods. Dealers email their orders. These are
# **repeated, known processes**: the steps are the same every time, so they should run by themselves.
#
# In this notebook you build the thing that runs them: a **workflow engine**, from scratch, in about 80 lines.
#
# 1. A workflow is data: nodes and edges, in JSON.
# 2. The engine: fill templates, find the ready node, run it, write the log.
# 3. Run Kavita's Diwali gasket order on the toolbox from Lecture 4.
# 4. Branches: "is it below reorder level?"
# 5. The approval node: a wait that survives a restart, then resume.
# 6. Errors, retries and idempotency: re-running must not double-order.
# 7. An LLM node (read a dealer's email) and an agent node (your own agent, on the Lecture 5 loop).
# 8. The Studio's own engine on the same JSON.
#
# Runs in **replay mode** with no API key: the model calls were recorded on our run (cassettes `L6v3_*`).

# %% setup

# %%
import json, re, time, copy, pathlib, hashlib
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox, SPECS
from bahi.llm import LLM

print(len(SPECS), "tools in the toolbox:", ", ".join(SPECS))

# %% [markdown]
# ## 1. A workflow is data
#
# A **workflow** is a fixed path you draw. It has:
# - one **trigger**: what starts a run (a button, a schedule, an event, a form, a message);
# - **nodes**: the steps. A tool node calls one tool from the toolbox, *as one person*;
# - **edges**: which node comes after which.
#
# A node can use an earlier node's output with a **template**: `{{nodes.pr.request_no}}` means
# "the `request_no` field of node `pr`'s output". This is the format the Studio uses (its `SPEC.md`).

# %%
DIWALI = {
  "id": "diwali-gasket-order", "name": "Diwali gasket order",
  "nodes": [
    {"id": "start", "type": "trigger", "config": {"kind": "manual"}},
    {"id": "stock", "type": "tool", "config": {"tool": "check_stock", "as": "KJOSHI",
                                               "args": {"item_code": "GSK-SIL-05L"}}},
    {"id": "pr", "type": "tool", "config": {"tool": "create_purchase_request", "as": "KJOSHI", "confirm": True,
        "args": {"item_code": "{{nodes.stock.item_code}}", "quantity": 20000,
                 "cost_centre": "PRD-07", "need_by": "2026-11-09"}}},
  ],
  "edges": [{"from": "start", "to": "stock"}, {"from": "stock", "to": "pr"}],
}
print(json.dumps(DIWALI, indent=1)[:600])

# %% [markdown]
# ## 2. Templates: one node reads another's output
#
# Two rules:
# - **Whole-field rule.** If a field is exactly one `{{ ... }}`, the value keeps its type (a number stays a number).
# - Otherwise each `{{ ... }}` becomes text inside the string: `"PR {{nodes.pr.request_no}} is waiting"`.
#
# A path that does not exist is an error that says what *is* there. A workflow that silently passes `None` to
# Bahi is far worse than one that stops and names the missing field.

# %%
TEMPLATE = re.compile(r"\{\{\s*(.+?)\s*\}\}")

def lookup(path, ctx):
    """'nodes.stock.warehouses[0].on_hand' -> the value, walking dicts by name and lists by [index]."""
    cur, walked = ctx, []
    for part in re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\[\d+\]", path):
        if part.startswith("["):
            # TODO (exercise 1): walk into a list by index, e.g. warehouses[0]. Raise a clear KeyError if it is not
            # a list or the index is past the end.
            SOLUTION_1 = True
            if SOLUTION_1:
                i = int(part[1:-1])
                if not isinstance(cur, list) or i >= len(cur):
                    raise KeyError(f"{'.'.join(walked)} has no item {part}")
                cur = cur[i]
        else:
            if not isinstance(cur, dict) or part not in cur:
                have = ", ".join(list(cur)[:8]) if isinstance(cur, dict) else type(cur).__name__
                raise KeyError(f"{'.'.join(walked) or 'context'} has no field '{part}' (it has: {have})")
            cur = cur[part]
        walked.append(part)
    return cur

def fill(value, ctx):
    """Fill every {{ }} in a value (dicts and lists too) from the outputs so far."""
    if isinstance(value, dict):
        return {k: fill(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [fill(v, ctx) for v in value]
    if not isinstance(value, str):
        return value
    whole = TEMPLATE.fullmatch(value.strip())
    if whole:                                   # whole-field rule: keep the type
        return lookup(whole.group(1), ctx)
    return TEMPLATE.sub(lambda m: str(lookup(m.group(1), ctx)), value)

ctx = {"nodes": {"stock": {"item_code": "GSK-SIL-05L", "free_total": 66000,
                           "warehouses": [{"warehouse": "WH-PUN-STR", "on_hand": 54000}]}}}
print(fill("{{nodes.stock.free_total}}", ctx), type(fill("{{nodes.stock.free_total}}", ctx)).__name__)
print(fill("Free stock of {{nodes.stock.item_code}}: {{nodes.stock.free_total}}", ctx))
print(fill("{{nodes.stock.warehouses[0].on_hand}}", ctx))
try:
    fill("{{nodes.stock.po_no}}", ctx)
except KeyError as e:
    print("error:", e)

# %% [markdown]
# ## 3. The engine
#
# The whole engine is one loop:
#
# 1. **Find a ready node.** A node is ready when every node with an edge into it has finished, and at least one of
#    those edges was *taken*. If every incoming edge is settled and none was taken, the node is **skipped**.
# 2. **Fill its templates** from the outputs so far.
# 3. **Run it.** A tool node calls the toolbox as its person (`as`), so Kavita's permissions hold, nobody else's.
# 4. **Write the run log**, and record which exit (port) it left by: `out`, `true`/`false`, `error`.
#
# Stop when nothing is ready (done), a node failed (failed), or an approval is waiting (waiting).

# %%
FINISHED = {"done", "warning", "error", "skipped"}

class MiniEngine:
    def __init__(self, erp, llm=None, toolbox_for=None):
        self.erp, self.llm, self._tb = erp, llm, {}
        self._make = toolbox_for or (lambda user, names=None: Toolbox(erp, user, names))  # your module: your own

    def toolbox(self, user, names=None):
        key = (user, tuple(names or ()))
        if key not in self._tb:
            self._tb[key] = self._make(user, names)
        return self._tb[key]

    # ---- a run is a plain dict, so it can be saved as JSON and picked up later
    def start(self, wf, trigger=None):
        run = {"workflow": copy.deepcopy(wf), "status": "running", "trigger": trigger or {},
               "nodes": {n["id"]: {"status": "pending"} for n in wf["nodes"]}, "taken": [], "log": []}
        return run

    def ready(self, run):
        wf, st = run["workflow"], run["nodes"]
        changed = True
        while changed:                                         # skip whole branches that cannot run
            changed = False
            for n in wf["nodes"]:
                nid = n["id"]
                if st[nid]["status"] != "pending":
                    continue
                ins = [e for e in wf["edges"] if e["to"] == nid]
                if not ins:
                    return nid                                 # the trigger
                if all(st[e["from"]]["status"] in FINISHED for e in ins):
                    if any([e["from"], e["to"], e.get("port", "out")] in run["taken"] for e in ins):
                        return nid
                    st[nid]["status"] = "skipped"; changed = True
                    self.log(run, nid, "skipped", "no edge into it was taken")
        return None

    def log(self, run, nid, event, text):
        run["log"].append({"node": nid, "event": event, "text": text})

    def context(self, run):
        return {"trigger": run["trigger"], "today": "2026-10-26",
                "nodes": {k: v.get("output") for k, v in run["nodes"].items() if "output" in v}}

    def step(self, run, nid):
        node = next(n for n in run["workflow"]["nodes"] if n["id"] == nid)
        rec = run["nodes"][nid]
        t0 = time.perf_counter()
        try:
            status, output, port, text = getattr(self, "run_" + node["type"])(node, self.context(run), rec)
        except KeyError as e:                                  # a template named a field that is not there
            status, output, port, text = "error", {"ok": False, "error": str(e)}, "error", str(e)
        rec.update(status=status, output=output, seconds=round(time.perf_counter() - t0, 4))
        self.log(run, nid, status, text)
        if status == "waiting":
            run["status"] = "waiting"; run["waiting_for"] = output; return
        if status == "error" and not any(e["from"] == nid and e.get("port", "out") == port
                                         for e in run["workflow"]["edges"]):
            run["status"] = "failed"; run["error"] = f"{nid}: {text}"; return
        for e in run["workflow"]["edges"]:
            if e["from"] == nid and e.get("port", "out") == port:
                run["taken"].append([e["from"], e["to"], e.get("port", "out")])

    def run_until_pause(self, run):
        while run["status"] == "running":
            nid = self.ready(run)
            if nid is None:
                run["status"] = "done"; break
            self.step(run, nid)
        return run

    # ---- node types: each returns (status, output, port, one-line text)
    def run_trigger(self, node, ctx, rec):
        return "done", {**node["config"].get("data", {}), **ctx["trigger"]}, "out", f"started ({node['config']['kind']})"

    def run_tool(self, node, ctx, rec):
        cfg = node["config"]
        args = fill(cfg.get("args", {}), ctx)
        specs = getattr(self.toolbox(cfg.get("as", "KJOSHI")), "specs", SPECS)   # a module toolbox has its own
        if cfg["tool"] in specs and "confirm" in specs[cfg["tool"]].spec["input_schema"]["properties"]:
            args["confirm"] = bool(cfg.get("confirm", False))     # the Commit switch, never the template
        out = self.toolbox(cfg.get("as", "KJOSHI")).call(cfg["tool"], args)
        for attempt in range(int(cfg.get("retries", 0))):          # retry only what failed by time-out
            if out.get("bahi_code") != "TIMEOUT":
                break
            rec.setdefault("retries", []).append(out["error"])        # kept on the node's record
            out = self.toolbox(cfg.get("as", "KJOSHI")).call(cfg["tool"], args)
        if not out.get("ok"):
            return "error", out, "error", f"{out.get('error')} {out.get('next_step', '')}"
        if out.get("warning") or out.get("warnings"):
            return "warning", out, "out", f"warning: {out.get('warning') or out.get('warnings')}"
        return "done", out, "out", short(out)

    def run_message(self, node, ctx, rec):
        cfg = node["config"]
        out = self.toolbox(cfg.get("as", "KJOSHI")).call("send_message", {"to": fill(cfg["to"], ctx),
                                                                          "text": fill(cfg["text"], ctx)})
        return ("done" if out.get("ok") else "error"), out, ("out" if out.get("ok") else "error"), \
               f"to {out.get('to')}: {fill(cfg['text'], ctx)[:70]}" if out.get("ok") else out.get("error")

def short(out):
    if "preview" in out:
        return f"preview only, nothing saved · estimated {out['preview'].get('estimated_value')}"
    if "items" in out:
        return f"{len(out['items'])} found · best {out['items'][0]['item_code']}" if out["items"] else "nothing found"
    keys = ["po_no", "grn_no", "request_no", "status", "free_total", "below_reorder", "already_done", "balance"]
    return " · ".join(f"{k}={out[k]}" for k in keys if k in out) or json.dumps(out, default=str)[:90]

def show(run):
    print("run:", run["status"], "|", run.get("error") or run.get("waiting_for") or "")
    for e in run["log"]:
        print(f"  {e['node']:>8}  {e['event']:<8} {e['text'][:110]}")

# %% [markdown]
# ### Run it on a fresh Rasoi
#
# `ERP()` is a fresh Bahi sandbox: Rasoi Steel Works on Monday 26 October 2026.

# %%
erp = ERP()
eng = MiniEngine(erp)
run = eng.run_until_pause(eng.start(DIWALI))
show(run)
print(json.dumps(run["nodes"]["pr"]["output"], indent=1)[:700])

# %% [markdown]
# The PR is **WAITING FOR APPROVAL**: ₹2,69,040 estimated (20,000 × ₹11.40 old rate + 18%) is above Kavita's
# ₹2,50,000 limit, so it waits for Rohit. Our workflow just ends. A real one must **wait** for him: section 5.

# %% [markdown]
# ## 4. Branches: a condition node
#
# "Reorder when low": every Monday, check an item; **if** it is below its reorder level, raise a request, **else**
# do nothing. A condition node leaves by its `true` or `false` port; only that side runs, the other is skipped.
#
# Whistles (`WHS-STD-01`): 8,000 free against a reorder level of 12,000. Gaskets: 66,000 free against 30,000.

# %%
def run_condition(self, node, ctx, rec):
    value = fill(node["config"]["if"], ctx)
    branch = "true" if value else "false"
    return "done", {"branch": branch, "value": value}, branch, f"{node['config']['if']} -> {branch}"
MiniEngine.run_condition = run_condition

def reorder_when_low(item, quantity):
    return {"id": "reorder-when-low", "name": "Reorder when low",
      "nodes": [
        {"id": "monday", "type": "trigger", "config": {"kind": "schedule", "every": "week", "at": "09:00"}},
        {"id": "stock", "type": "tool", "config": {"tool": "check_stock", "as": "KJOSHI", "args": {"item_code": item}}},
        {"id": "low", "type": "condition", "config": {"if": "{{nodes.stock.below_reorder}}"}},
        {"id": "pr", "type": "tool", "config": {"tool": "create_purchase_request", "as": "KJOSHI", "confirm": True,
            "args": {"item_code": item, "quantity": quantity, "cost_centre": "PRD-07", "need_by": "2026-11-09"}}},
        {"id": "tell", "type": "message", "config": {"to": "@rohit", "as": "KJOSHI",
            "text": "Reorder: {{nodes.pr.request_no}} for {{nodes.pr.quantity}} x {{nodes.stock.item_code}} is {{nodes.pr.status}}"}},
      ],
      "edges": [{"from": "monday", "to": "stock"}, {"from": "stock", "to": "low"},
                {"from": "low", "to": "pr", "port": "true"}, {"from": "pr", "to": "tell"}]}

for item in ["WHS-STD-01", "GSK-SIL-05L"]:
    print("\n", item)
    e = MiniEngine(ERP())                                   # a fresh Rasoi for each
    show(e.run_until_pause(e.start(reorder_when_low(item, 20000))))

# %% [markdown]
# Whistles: below reorder → PR raised. ₹1,60,480 is within Kavita's limit, so Bahi approves it at once.
# Gaskets: not below → `pr` and `tell` are **skipped**. Nothing was raised.
#
# **Exercise 2.** Add the `false` side: a message node `fine` that tells `@kavita` the item is fine, with its
# free stock and days of cover, joined to `low` by `"port": "false"`.

# %%
# TODO (exercise 2): add the false branch to the workflow.
wf = reorder_when_low("GSK-SIL-05L", 20000)
SOLUTION_2 = True
if SOLUTION_2:
    wf["nodes"].append({"id": "fine", "type": "message", "config": {"to": "@kavita", "as": "KJOSHI",
        "text": "{{nodes.stock.item_code}} is fine: {{nodes.stock.free_total}} free, {{nodes.stock.cover_days}} days of cover."}})
    wf["edges"].append({"from": "low", "to": "fine", "port": "false"})
e2 = MiniEngine(ERP()); show(e2.run_until_pause(e2.start(wf)))

# %% [markdown]
# ## 5. The approval node: a wait that survives a restart
#
# Rohit may approve in ten minutes or on Wednesday. A workflow cannot hold a Python loop open for two days.
# So an **approval node** does three things:
# 1. reads the document's *real* status from Bahi (`order_status`);
# 2. if it is waiting, marks the run `waiting` and **saves the run as JSON**: nothing is held in memory;
# 3. later, `resume` loads the run, re-reads the status, and carries on from the approval node.
#
# The approver signs in *their own* inbox, with *their own* permissions. The workflow never signs for Rohit.

# %%
def run_approval(self, node, ctx, rec):
    doc = fill(node["config"]["doc_no"], ctx)
    st = self.toolbox("KJOSHI").call("order_status", {"request_no": doc} if doc.startswith("PR") else {"po_no": doc})
    if st.get("status_code") in ("AP", "RL", "CL"):
        return "done", {"doc_no": doc, "approved_by": st.get("approved_by"), "waited": rec.get("waited", False)}, \
               "out", f"{doc} approved by {st.get('approved_by')}"
    if st.get("status_code") == "PA":
        rec["waited"] = True
        return "waiting", {"doc_no": doc, "approver": st.get("approver")}, None, f"waiting for {st.get('approver')}"
    return "error", {"ok": False, "doc_no": doc, "error": f"{doc} is {st.get('status')}"}, "rejected", f"{doc} is {st.get('status')}"
MiniEngine.run_approval = run_approval

def resume(self, run):
    """Re-open a waiting run: the approval node runs again and reads the status fresh from Bahi."""
    nid = run["waiting_for"] and next(k for k, v in run["nodes"].items() if v["status"] == "waiting")
    run["nodes"][nid]["status"] = "pending"
    run["status"], run["waiting_for"] = "running", None
    return self.run_until_pause(run)
MiniEngine.resume = resume

GASKETS = copy.deepcopy(DIWALI)
GASKETS["nodes"] += [
  {"id": "rohit", "type": "approval", "config": {"doc_no": "{{nodes.pr.request_no}}", "approver": "RMEHTA"}},
  {"id": "po", "type": "tool", "config": {"tool": "create_purchase_order", "as": "KJOSHI", "confirm": True,
      "args": {"supplier_code": "DP-RJK-0042", "request_no": "{{nodes.pr.request_no}}"}}},
  {"id": "release", "type": "tool", "config": {"tool": "release_purchase_order", "as": "KJOSHI",
      "args": {"po_no": "{{nodes.po.po_no}}"}}},
  {"id": "tell", "type": "message", "config": {"to": "@rohit", "as": "KJOSHI",
      "text": "{{nodes.release.po_no}} released to Deccan Polymers: {{nodes.po.gross_value}} gross. Thanks for approving {{nodes.pr.request_no}}."}},
]
GASKETS["edges"] += [{"from": "pr", "to": "rohit"}, {"from": "rohit", "to": "po"},
                     {"from": "po", "to": "release"}, {"from": "release", "to": "tell"}]

erp = ERP()
eng = MiniEngine(erp)
run = eng.run_until_pause(eng.start(GASKETS))
show(run)
pathlib.Path("run_waiting.json").write_text(json.dumps(run, indent=1, default=str))
print("\nsaved:", pathlib.Path("run_waiting.json").stat().st_size, "bytes of JSON. The Python object can go now.")
del run

# %% [markdown]
# Monday afternoon. Rohit opens his inbox and approves, **as himself**, through the same toolbox. Then a fresh
# engine (think: the web server restarted) loads the saved run and resumes it.

# %%
rohit = Toolbox(erp, "RMEHTA")
print([w["doc_no"] for w in rohit.call("list_my_approvals", {})["waiting"]])
print(rohit.call("approve_purchase_request", {"request_no": "PR/2026/04417", "decision": "approve"})["status"])

eng2 = MiniEngine(erp)                                           # a new engine, nothing in memory
run = eng2.resume(json.loads(pathlib.Path("run_waiting.json").read_text()))
show(run)

# %% [markdown]
# PO/2026/01182 at Deccan's contract rate ₹11.90: 20,000 × 11.90 = ₹2,38,000 + 18% = **₹2,80,840**, approved
# through Rohit's PR approval, then released. Rohit got a message.
#
# **Exercise 3.** What if Rohit rejects? Add a node `sorry` (a message to `@kavita`) on the approval node's
# `rejected` port. Run the workflow on a fresh Rasoi, reject as Rohit, resume, and check that `po` is skipped.

# %%
# TODO (exercise 3): handle a rejection.
SOLUTION_3 = True
if SOLUTION_3:
    wf3 = copy.deepcopy(GASKETS)
    wf3["nodes"].append({"id": "sorry", "type": "message", "config": {"to": "@kavita", "as": "KJOSHI",
        "text": "{{nodes.rohit.doc_no}} was not approved. Nothing was ordered."}})
    wf3["edges"].append({"from": "rohit", "to": "sorry", "port": "rejected"})
    erp3 = ERP(); e3 = MiniEngine(erp3)
    r3 = e3.run_until_pause(e3.start(wf3))
    Toolbox(erp3, "RMEHTA").call("approve_purchase_request", {"request_no": "PR/2026/04417", "decision": "reject",
                                                              "comment": "Use the 3-litre stock first"})
    show(e3.resume(r3))

# %% [markdown]
# ## 6. Errors, retries and idempotency
#
# Bahi sometimes saves a document and then times out before it answers. The workflow sees an error, but the
# PR **exists**. If it simply runs again, does Kavita get two PRs for 40,000 gaskets?
#
# No, because the toolbox's write tools carry an **idempotency key** made from what the document *is*
# (user, item, quantity, cost centre, date). The same request asked twice is found, not raised twice.
# That is what makes a retry safe. Watch it: we make Bahi's next `pr_submit` time out *after* it commits.

# %%
erp = ERP()
erp.inject("pr_submit", "timeout_after_commit")
wf = copy.deepcopy(DIWALI)
wf["nodes"][2]["config"]["retries"] = 0
e = MiniEngine(erp); r = e.run_until_pause(e.start(wf)); show(r)
print("new PRs in Bahi:", [x["pr_no"] for x in erp.q("SELECT pr_no FROM pr_hdr WHERE pr_no >= 'PR/2026/04417'")])

# %% [markdown]
# The run failed on a time-out, yet the PR was saved. Now with `retries: 2` on the PR node:

# %%
erp = ERP()
erp.inject("pr_submit", "timeout_after_commit")
wf = copy.deepcopy(DIWALI)
wf["nodes"][2]["config"]["retries"] = 2
e = MiniEngine(erp); r = e.run_until_pause(e.start(wf)); show(r)
print("retries:", r["nodes"]["pr"].get("retries"))
print("already_done:", r["nodes"]["pr"]["output"].get("already_done"))

# and run the whole workflow a second time, on the same Rasoi
r2 = e.run_until_pause(e.start(wf)); show(r2)
print("new PRs in Bahi after a time-out, a retry and a second run:",
      [x["pr_no"] for x in erp.q("SELECT pr_no FROM pr_hdr WHERE pr_no >= 'PR/2026/04417'")])

# %% [markdown]
# **Exercise 4.** Why must the key come from the content and not from `uuid4()`? Make two keys for the same
# request each way and compare them.

# %%
# TODO (exercise 4)
import uuid
def content_key(*parts):
    return "K" + hashlib.sha256("|".join(str(p).upper() for p in parts).encode()).hexdigest()[:12].upper()
SOLUTION_4 = True
if SOLUTION_4:
    req = ("KJOSHI", "GSK-SIL-05L", 20000, "PRD-07", "2026-11-09")
    print("content:", content_key(*req), content_key(*req), "-> same request, same key")
    print("uuid4:  ", uuid.uuid4().hex[:12], uuid.uuid4().hex[:12], "-> a retry looks like a new request")

# %% [markdown]
# ## 7. An LLM node and an agent node
#
# Some steps are not lookups. A dealer's email is free text: no tool can read it. An **LLM node** makes one model
# call: a prompt template in, a JSON object with the fields you asked for out. The rest of the workflow stays fixed.

# %%
llm = LLM("gemini:gemini-3.8-flash", cassette="L6v3_nb")

def run_llm(self, node, ctx, rec):
    cfg = node["config"]
    prompt = fill(cfg["prompt"], ctx) + ("\n\nReply with one JSON object only, with these keys: "
                                         + ", ".join(cfg["fields"]) + ".")
    r = self.llm.chat([{"role": "user", "content": prompt}])
    m = re.search(r"\{.*\}", r.content or "", re.S)
    out = json.loads(m.group(0))
    rec["meta"] = {"tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "cost_inr": r.cost_inr, "replayed": r.replayed}
    return "done", out, "out", ", ".join(f"{k}={v}" for k, v in out.items())
MiniEngine.run_llm = run_llm

EMAIL = """Subject: Spare gaskets before Diwali

Dear Rasoi team,

Our service centre in Nagpur is running short of spares. Please send us 4,000 silicone gaskets for your
5 litre pressure cooker. We need them at our godown by 12 November, before the festival rush.

Regards,
Prakash Sharma
Sharma Home Appliances, Nagpur"""

DEALER = {"id": "dealer-email", "nodes": [
    {"id": "email", "type": "trigger", "config": {"kind": "manual"}},
    {"id": "extract", "type": "llm", "config": {"output": "json", "fields": ["item", "quantity", "need_by", "dealer"],
        "prompt": "A dealer has written to Rasoi Steel Works, Pune. Today is {{today}}.\nRead the email and pull out what "
                  "they need. item: the part in 3 to 5 plain words; quantity: a whole number; need_by: YYYY-MM-DD; "
                  "dealer: the dealer's company name.\n\nEmail:\n{{trigger.email}}"}},
    {"id": "find", "type": "tool", "config": {"tool": "find_item", "as": "KJOSHI", "args": {"query": "{{nodes.extract.item}}"}}},
    {"id": "pr", "type": "tool", "config": {"tool": "create_purchase_request", "as": "KJOSHI", "confirm": False,
        "args": {"item_code": "{{nodes.find.items[0].item_code}}", "quantity": "{{nodes.extract.quantity}}",
                 "cost_centre": "PRD-07", "need_by": "{{nodes.extract.need_by}}"}}},
    {"id": "tell", "type": "message", "config": {"to": "@kavita", "as": "KJOSHI",
        "text": "{{nodes.extract.dealer}} wants {{nodes.extract.quantity}} x {{nodes.find.items[0].item_code}} by "
                "{{nodes.extract.need_by}}. PR preview: {{nodes.pr.preview.estimated_value}} estimated. Commit it?"}}],
  "edges": [{"from": "email", "to": "extract"}, {"from": "extract", "to": "find"}, {"from": "find", "to": "pr"},
            {"from": "pr", "to": "tell"}]}

e = MiniEngine(ERP(), llm=llm)
r = e.run_until_pause(e.start(DEALER, {"email": EMAIL})); show(r)
print(r["nodes"]["extract"]["output"], r["nodes"]["extract"]["meta"])

# %% [markdown]
# **Exercise 5.** Add a field `city` (where the dealer is) to the LLM node and print it. Note the commit switch on `pr` is off: a person commits what a model read.
# A new request is not in the cassette: in replay mode you will see `ReplayMiss`. Set your own key to run it live.

# %%
# TODO (exercise 5)
SOLUTION_5 = False   # needs a live key: the new prompt was never recorded
if SOLUTION_5:
    d5 = copy.deepcopy(DEALER); d5["nodes"][1]["config"]["fields"].append("city")
    e5 = MiniEngine(ERP(), llm=llm); print(e5.run_until_pause(e5.start(d5, {"email": EMAIL}))["nodes"]["extract"]["output"])

# %% [markdown]
# ### The agent node: your own agent, as one node
#
# An **agent node** is the Lecture 5 loop inside one node: **instructions** (plain words) + **a chosen subset of
# tools** + **a model**. The model picks the next tool until it answers in text, or `max_steps` runs out.
# A switch, `may_commit`, decides whether its writes may commit; off, every write is forced to a preview.

# %%
def run_agent(self, node, ctx, rec):
    cfg = node["config"]
    tb = self.toolbox(cfg.get("as", "KJOSHI"), cfg["tools"])
    msgs = [{"role": "system", "content": cfg["instructions"] + "\nYou work at Rasoi Steel Works, Pune, in Bahi ERP. "
             "Today is 2026-10-26. If a tool returns ok=false, read its next_step."},
            {"role": "user", "content": fill(cfg["input"], ctx)}]
    calls = []
    for _ in range(cfg.get("max_steps", 12)):
        r = self.llm.chat(msgs, tools=tb.schemas())
        msgs.append(r.message())
        if not r.tool_calls:
            return "done", {"reply": r.content, "tool_calls": calls}, "out", (r.content or "")[:100]
        for tc in r.tool_calls:
            args = dict(tc.arguments)
            if not cfg.get("may_commit") and "confirm" in args:
                args["confirm"] = False                                 # the switch wins over the model
            out = tb.call(tc.name, args)
            calls.append({"tool": tc.name, "args": args, "ok": out.get("ok")})
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)})
    return "error", {"ok": False, "error": "max steps", "tool_calls": calls}, "error", "stopped at max_steps"
MiniEngine.run_agent = run_agent

STOCK_DESK = {"id": "stock-desk", "nodes": [
    {"id": "ask", "type": "trigger", "config": {"kind": "chat"}},
    {"id": "desk", "type": "agent", "config": {"as": "KJOSHI", "may_commit": False, "max_steps": 8,
        "tools": ["find_item", "check_stock"],
        "instructions": "You are Rasoi's stock desk. Answer questions about stock in two or three short sentences, "
                        "with numbers from the tools. Never guess a number.",
        "input": "{{trigger.message}}"}}],
  "edges": [{"from": "ask", "to": "desk"}]}

e = MiniEngine(ERP(), llm=llm)
r = e.run_until_pause(e.start(STOCK_DESK, {"message": "Do we have enough whistles and 5 litre gaskets for next week?"}))
show(r)
print("\n", r["nodes"]["desk"]["output"]["reply"])
print([c["tool"] for c in r["nodes"]["desk"]["output"]["tool_calls"]])
print(llm.totals())

# %% [markdown]
# ## 8. The Studio's own engine, on the same JSON
#
# The Workflow Studio (`/studio` in the Rasoi Experience) runs the same JSON format with a fuller engine:
# expressions inside `{{ }}`, `set` nodes, form and event triggers, a run store, and an approval sheet.
# Our `GASKETS` workflow runs on it unchanged (it ignores our extra `retries` field).

# %%
try:
    from bahi.experience.studio.engine import Engine as StudioEngine, Store
    HAVE_STUDIO = True
except ImportError as err:
    HAVE_STUDIO = False
    print("The Studio engine is not in this install:", err)

if HAVE_STUDIO:
    erp = ERP()
    tbs = {}
    seng = StudioEngine(toolbox_for=lambda user, names=None: Toolbox(erp, user, names), store=Store(), pid="nb6")
    wf = copy.deepcopy(GASKETS)
    for i, n in enumerate(wf["nodes"]):
        n.setdefault("title", n["id"]); n.setdefault("x", 60 + 240 * i); n.setdefault("y", 240)
    print("problems:", seng.validate(wf))
    srun = seng.run_until_pause(seng.start(wf))
    print(srun["status"], srun.get("waiting_for"))
    seng.approve(srun, decision="approve")
    srun = seng.run_until_pause(srun)
    print(srun["status"])
    for e in srun["log"]:
        print(f"  {str(e.get('node')):>8}  {str(e.get('event')):<8} {str(e.get('text'))[:100]}")

# %% [markdown]
# ## 9. What we measured (from `experiments/logs/`)
#
# The lecture's measured numbers come from the scripts in `lectures/L6-the-studio/experiments/` run on Modal:
# every Studio template on a fresh Rasoi, and the same repeated task done by a workflow and by an agent, N times.
# The slides show them; the logs are next to the scripts.
#
# %% [markdown]
# ## 10. Your module (starts A6)
#
# The engine does not care which toolbox it calls. Give it your module kit's toolbox (the tool folders you built in
# A4) and the same JSON runs on your module. Here is HR · leave with its starter tool, plus `send_message` from
# purchasing:

# %%
from bahi.modules._toolbox import ModuleToolbox
hr_erp = ERP(modules=["hr_leave"])
hr = MiniEngine(hr_erp, toolbox_for=lambda user, names=None: ModuleToolbox(hr_erp, user, "hr_leave",
                                                                        with_purchasing=["send_message"]))
LEAVE = {"id": "leave-balance-monday", "nodes": [
    {"id": "monday", "type": "trigger", "config": {"kind": "schedule", "every": "week", "at": "09:00"}},
    {"id": "bal", "type": "tool", "config": {"tool": "check_leave_balance", "as": "KJOSHI", "args": {}}},
    {"id": "tell", "type": "message", "config": {"to": "@kavita", "as": "KJOSHI",
        "text": "Leave left this week: casual {{nodes.bal.balances.CL}}, earned {{nodes.bal.balances.EL}}, sick {{nodes.bal.balances.SL}}."}}],
  "edges": [{"from": "monday", "to": "bal"}, {"from": "bal", "to": "tell"}]}
r = hr.run_until_pause(hr.start(LEAVE)); show(r)
print(r["nodes"]["tell"]["output"])

# %% [markdown]
# For A6, write down for your module:
# 1. one process that repeats with **known steps** → a workflow (which trigger? which tools, as whom?);
# 2. one step that reads **free text** → an LLM node;
# 3. one job where the **steps depend on what you find** → an agent node (instructions, which tools, may it commit?).
#
# Build them as JSON (or draw the purchasing ones in the Studio and export them), run them here with `MiniEngine`
# and your module's toolbox, run each twice, and keep both run logs.
