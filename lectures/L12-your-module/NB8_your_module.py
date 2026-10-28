# %% [markdown]
# # NB8 · Lecture 12 · Your Module: Demo Day
#
# **Agentic Systems Engineering · Lecture 12 · Sun 6 Dec 2026 · Vizuara · Dr. Rajat Dandekar.** (The file keeps its
# old name, NB8, from when demo day was Lecture 8.)
#
# Eleven lectures built **Ask Rasoi** for purchasing: seven by hand, one piece at a time, and four that put each piece
# on the tools companies use. This notebook does three things:
#
# 1. **Walks Kavita's order through every piece**, replayed from our recorded run: three people (Kavita, Rohit, Neha),
#    each in their own conversation, one Rasoi.
# 2. **Takes the whole recipe to a second department**, HR leave: the kit's Before, a toolbox in the course format
#    (`tool.json` + `tool.py` folders), served over MCP, with Ask Rasoi on top, and the kit's four scenarios as the
#    evaluation.
# 3. **Plans your production stack:** two industry tools from Lectures 8–11, each with a reason (`STACK.md`).
#
# Replay mode, no key: the model replies come from our run on Modal (`lectures/L12-your-module/experiments/runs8.py`).

# %% setup

# %%
import json
import pathlib

import pandas as pd

from bahi.course.l7 import AskRasoi
from bahi.erp.engine import ERP
from bahi.llm import LLM

pd.set_option("display.max_colwidth", 100)
FLASH = "gemini:gemini-3.8-flash"


def show(d, n=1200):
    print(json.dumps(d, indent=1, default=str, ensure_ascii=False)[:n])


# %% [markdown]
# ## 1 · Kavita's order, through every piece
#
# The same script we ran on Modal: three people use Ask Rasoi, each signed in as themselves (passthrough identity),
# each behind the trust layer. Every step is tagged with the lecture that built the piece it used.

# %%
erp = ERP()
who = {u: AskRasoi(erp, u, llm=LLM(FLASH, cassette=f"L8v3_final_{u}"), trust=True) for u in ("KJOSHI", "RMEHTA", "NDESAI")}
script = [
    ("KJOSHI", "How many 5-litre silicone gaskets do we have at Pune, and how many days will they last?"),
    ("KJOSHI", "Shakti Seals in Vadodara quotes ₹10.40. Can we buy the gaskets from them?"),
    ("KJOSHI", "Then reorder 20,000 from Deccan Polymers at the contract rate. Charge PRD-07, need-by 2 November."),
    ("KJOSHI", "Yes, go ahead."),
    ("RMEHTA", "What is waiting for my approval?"),
    ("RMEHTA", "Approve PR/2026/04417."),
    ("KJOSHI", "Rohit has approved PR/2026/04417."),
    ("NDESAI", "12,000 gaskets arrived from Deccan against PO/2026/01182. Record the goods receipt."),
    ("NDESAI", "Yes, record it."),
    ("NDESAI", "The other 8,000 have arrived now. Record them too."),
    ("NDESAI", "Yes."),
    ("KJOSHI", "What is the status of PO/2026/01182 now?"),
]
PIECE = {"search_policy": "L3 memory", "check_stock": "L4 hands", "create_purchase_request": "L4 hands + L7 trust",
         "list_my_approvals": "L5 loop: the pause", "approve_purchase_request": "L7 trust: approver only",
         "create_purchase_order": "L4 hands + L7 trust", "release_purchase_order": "L4 hands + L7 read-back",
         "receive_goods": "L4 hands + L7 trust", "order_status": "L7 read-back"}
rows = []
for user, text in script:
    a = who[user]
    n0 = len(a.trace)
    reply = a.respond(text)
    tools = [s["tool"] for s in a.trace[n0:] if s["kind"] == "tool"]
    tok = sum(s["tokens_in"] + s["tokens_out"] for s in a.trace[n0:] if s["kind"] == "model")
    rows.append({"who": user, "says": text[:60], "tools (pieces)": ", ".join(f"{t} [{PIECE.get(t, 'L4 hands')}]" for t in tools),
                 "tokens (L2 brain)": tok, "reply": reply[:120]})
pd.DataFrame(rows)

# %% [markdown]
# What Bahi holds at the end, read straight from its tables:

# %%
o = erp.orders(**{"h.po_no": "PO/2026/01182"})[0]
print({k: o[k] for k in ("po_no", "status", "approved_by", "created_by", "qty", "rate", "gross_value", "cc_cd")})
print(erp.q("SELECT grn_no, po_no, received_by FROM grn_hdr"))
print("Bahi users that made calls:", sorted({c.user for c in erp.calls}))

# %% [markdown]
# Every call ran as Kavita, Rohit or Neha. No service account, no shared password. That is Lecture 7's first promise,
# visible in Bahi's own log.
#
# ## 2 · A second department: HR leave
#
# Kavita types *"I need Thursday and Friday off for my sister's wedding."* The Before is three legacy screens:
#
# | # | Screen | Service | What Kavita must know |
# |---|---|---|---|
# | 1 | HR-LV-01 Leave Balance | `lv_emp_get`, `lv_bal_get`, `lv_hol_list` | her employee code E-1042; CL 1, EL 9 |
# | 2 | HR-LV-02 Leave Application | `lv_fetch`, `lv_save` | to choose EL, not CL |
# | 3 | HR-LV-04 Leave Approval (Rohit) | `lv_list`, `lv_approve` | that it reached him |
#
# The trap: two days of CL with one left saves as "LV/2026/00388 SAVED", status **HD**, one day unpaid, never routed.
# The kit's services are black boxes: an input goes in, an output comes out.

# %%
erp = ERP(modules=["hr_leave"])
s = erp.session("KJOSHI")
tok = s.call("lv_fetch", emp_cd="E-1042", lv_cd="CL")["data"]["fetch_tok"]
r = s.call("lv_save", emp_cd="E-1042", lv_cd="CL", from_dt="2026-10-29", to_dt="2026-10-30", reason="sister's wedding",
           fetch_tok=tok)
print("Bahi SAID:", r["rc"], r["msg"])
print("Bahi HOLDS:", s.call("lv_list", lv_no=r["data"]["lv_no"])["data"]["rows"][0])

# %% [markdown]
# ## 3 · The toolbox, in the course format
#
# One folder per business activity, `tool.json` (what the model reads) + `tool.py` (what runs). The kit ships the
# first one, `check_leave_balance`. `scaffold()` writes our reference versions of three more, the way A4 asks.

# %%
from bahi.course.l8 import LEAVE_PROMPT, leave_agent, scaffold
from bahi.modules._toolbox import ModuleToolbox, build_module_server, lint_folder

FOLDER = pathlib.Path("my_module_tools")
names = scaffold(FOLDER)
print(names)
print("lint:", lint_folder(FOLDER, "hr_leave") or "clean")
print((FOLDER / "apply_leave" / "tool.json").read_text()[:900])

# %% [markdown]
# Read `apply_leave/tool.py`: it previews, makes a key from the content, looks the key up before it writes and after a
# timeout, and returns a receipt read back from Bahi that names the silent outcome.

# %%
print((FOLDER / "apply_leave" / "tool.py").read_text())

# %% [markdown]
# ### TODO (exercise 1): write `cancel_leave`
# Write the folder `my_module_tools/cancel_leave/` with a `tool.json` and a `tool.py` that cancels one of the user's own
# applications through the `lv_cancel` service (fields `lv_no`, `reason`). It is a write: preview with `confirm=false`
# (show the application it would cancel), cancel only with `confirm=true`, and read the status back with `lv_list`.
# Then run `lint_folder` again: it must stay clean.

# %%
SOLUTION = True
if SOLUTION:
    d = FOLDER / "cancel_leave"
    d.mkdir(exist_ok=True)
    (d / "tool.json").write_text(json.dumps({
        "name": "cancel_leave", "title": "Cancel leave", "category": "HR", "writes": True, "version": "1.0",
        "description": "Cancel one of the signed-in employee's own leave applications, for example one HELD with unpaid "
                       "days. confirm=false shows what would be cancelled; confirm=true cancels it.",
        "services": ["lv_list", "lv_cancel"],
        "input_schema": {"type": "object", "properties": {
            "leave_no": {"type": "string", "description": "e.g. LV/2026/00388"},
            "reason": {"type": "string", "description": "why, in the user's words"},
            "confirm": {"type": "boolean", "description": "false (default) = preview; true = cancel"}},
            "required": ["leave_no", "reason"]},
        "output_schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "status": {"type": "string"}}},
        "example": {"leave_no": "LV/2026/00388", "reason": "applied with the wrong type"}}, indent=2))
    (d / "tool.py").write_text('''from bahi.agent.tools import ToolError, _bahi


def run(s, leave_no, reason, confirm=False):
    rows = _bahi(s, "lv_list", lv_no=leave_no)["rows"]
    if not rows:
        raise ToolError(f"No application {leave_no}.", "Check the number with leave_status.")
    app = rows[0]
    if not confirm:
        return {"ok": True, "preview": app, "note": "Nothing cancelled yet. Ask the user to confirm."}
    if app["status"] != "CN":
        _bahi(s, "lv_cancel", lv_no=leave_no, reason=reason)
    return {"ok": True, "leave_no": leave_no, "status": _bahi(s, "lv_list", lv_no=leave_no)["rows"][0]["status"]}
''')
print("lint:", lint_folder(FOLDER, "hr_leave") or "clean")

# %% [markdown]
# ## 4 · Test the promises with code, before any model
#
# Three tests, no model: the preview saves nothing; the silent outcome comes back as a warning; a lost reply leaves
# exactly one application.

# %%
erp = ERP(modules=["hr_leave"])
tb = ModuleToolbox(erp, "KJOSHI", folder=FOLDER)
args = {"leave_type": "CL", "from_date": "2026-10-29", "to_date": "2026-10-30", "reason": "sister's wedding"}
pv = tb.call("apply_leave", args)
print("(a) preview:", pv["preview"], "| saved:", len(erp.q("SELECT * FROM lv_app WHERE from_dt='2026-10-29'")))
print("    warning:", pv["warnings"])
held = tb.call("apply_leave", {**args, "confirm": True})
print("(b) receipt:", held["status"], "|", held.get("warning"))

# %% [markdown]
# ### TODO (exercise 2): the lost-reply test
# In a fresh `ERP(modules=["hr_leave"])`, inject `erp.inject("lv_save", "timeout_after_commit", 1)`, call
# `apply_leave` with EL and `confirm=True` twice, and prove there is exactly one application for 29 Oct.

# %%
if SOLUTION:
    erp = ERP(modules=["hr_leave"])
    tb = ModuleToolbox(erp, "KJOSHI", folder=FOLDER)
    erp.inject("lv_save", "timeout_after_commit", 1)
    el = {**args, "leave_type": "EL", "confirm": True}
    r1, r2 = tb.call("apply_leave", el), tb.call("apply_leave", el)
    n = len(erp.q("SELECT * FROM lv_app WHERE from_dt='2026-10-29' AND status!='CN'"))
    print(r1.get("leave_no"), r1.get("status"), "|", r2.get("leave_no"), "already_done:", r2.get("already_done"),
          "| applications:", n)
    assert n == 1

# %% [markdown]
# ## 5 · Served over MCP
#
# The same folders, as an MCP server bound to Kavita's own session, with the purchasing toolbox's `search_policy`
# beside them so Ask Rasoi can cite the leave policy.

# %%
from bahi.mcp_server import MCPClient, MCPClientTools

c = MCPClient(build_module_server(ERP(modules=["hr_leave"]), "KJOSHI", folder=FOLDER, with_purchasing=["search_policy"]))
print([t.name for t in c.list_tools()])
c.close()

# %% [markdown]
# ## 6 · Ask Rasoi on HR leave: the kit's four scenarios as the evaluation
#
# The Lecture 5 loop, the Lecture 7 agent, a leave prompt (`LEAVE_PROMPT`), the tools over MCP. The kit's
# `run_module_scenario` plays Kavita (or Neha), lets the approver approve, and checks Bahi's tables in code.
# Our recorded run, run 1 of three (the other two are in `experiments/logs/leave_askrasoi.json`).
# The replay uses the four folders `scaffold()` wrote (not your `cancel_leave`), exactly as recorded.

# %%
from bahi.modules._kit import load, run_module_scenario

for extra in ("cancel_leave",):  # keep the recorded tool set: the model's prompt lists every tool
    import shutil
    shutil.rmtree(FOLDER / extra, ignore_errors=True)
_, S, _ = load("hr_leave")
keep = []
res = [run_module_scenario(leave_agent(FLASH, "L8v3_leave", FOLDER, keep=keep), "hr_leave", sc) for sc in S.SCENARIOS]
pd.DataFrame([{"#": r.scenario, "scenario": r.name, "result": "pass" if r.passed else "FAIL",
               "never-events": "; ".join(r.never_events), "notes": "; ".join(r.notes)[:80], "₹": r.cost_inr,
               "last reply": (r.turns[-1]["agent"] or "")[:110]} for r in res])

# %% [markdown]
# ### TODO (exercise 3): read one run
# Print the conversation of scenario 1 (`res[0].turns`) and the tool calls of its trace (`keep[0].trace`).
# Which tool call decided whether a day would be unpaid?

# %%
if SOLUTION:
    for t in res[0].turns:
        print("KAVITA:", t["user"], "\nASK RASOI:", t["agent"], "\n")
    print([(st["tool"], st["args"]) for st in keep[0].trace if st["kind"] == "tool"])

# %% [markdown]
# ## 7 · Demo day
#
# Your module's demo-day change is announced at the end of Lecture 11 (`modules/<kit>/CHANGE.md`). For HR leave it is
# circular HR-CIR-2026-07: purchase staff now need the plant head for leave in the Diwali run. The hidden test asks
# for 5 and 6 November off; it passes only if the leave is paid, goes to **Anand Patil**, and the reply names the rule.
#
# ### TODO (exercise 4): where would the change live?
# Write three lines: which document you add to the knowledge, which tool argument `apply_leave` needs (Bahi's
# `lv_save` has a `fwd_to` field), and which guard you add to the trust layer.

# %%
if SOLUTION:
    print("1. Knowledge: add hr-circular-2026-07.md (HR-CIR-2026-07) to the corpus; search_policy must find it.")
    print("2. Tool: apply_leave gets an optional forward_to, passed to lv_save as fwd_to (APATIL in the Diwali run).")
    print("3. Trust: a guard refusing leave for Purchase staff in 2-14 Nov unless forwarded to the plant head (NE4).")

# %% [markdown]
# ## 8 · Your production stack
#
# The rubric's line 7 (10 points): your module runs on at least two industry tools from Lectures 8–11, from two
# different layers, each chosen with a written reason, and you measure one comparison yourself. The full menu is in
# `lectures/L12-your-module/rubric.md`. Whatever runs the loop, writes still go through your tool folders.
#
# ### TODO (exercise 5): draft your STACK.md
# Pick two layers for HR leave. For each: the tool and its pinned version, the hand-built piece it replaces or
# watches, why this tool and not its rival, and the comparison you will measure on your own run.

# %%
STACK = {
    "observability": {"tool": "TODO", "replaces_or_watches": "TODO", "why": "TODO", "not_picked": "TODO", "compare": "TODO"},
    "evals": {"tool": "TODO", "replaces_or_watches": "TODO", "why": "TODO", "not_picked": "TODO", "compare": "TODO"},
}
if SOLUTION:
    STACK = {
        "observability": {"tool": "Langfuse (pin the version you install)", "replaces_or_watches": "the Lecture 7 trace, read by hand",
                          "why": "open source and self-hostable, so HR data stays on Rasoi's machines",
                          "not_picked": "LangSmith: hosted only for us, and no key in our build",
                          "compare": "the same failing scenario 2 run: the wrong step found in our trace vs in Langfuse"},
        "evals": {"tool": "DeepEval (pin the version you install)", "replaces_or_watches": "the Lecture 7 suite and gate",
                  "why": "runs the four scenarios as tests in CI, so a change cannot merge if a scenario breaks",
                  "not_picked": "promptfoo: kept for red-teaming, not as the gate",
                  "compare": "the 12 runs (4 scenarios x 3): our gate's verdict vs DeepEval's, case by case"},
    }
layers = [k for k, v in STACK.items() if v["tool"] != "TODO"]
print(f"{len(layers)} layers chosen:", ", ".join(layers) or "none yet")
for layer, v in STACK.items():
    print(f"\n## {layer}: {v['tool']}")
    for k in ("replaces_or_watches", "why", "not_picked", "compare"):
        print(f"- {k.replace('_', ' ')}: {v[k]}")

