"""Build figdata.js for the L8 deck (stdlib only; safe on the laptop).

    python3 lectures/L8-your-module/gen_figdata.py

Sources: experiments/logs/final_demo.json, leave_askrasoi.json, demo_changes.json, test_kits.log (copy of
modules/test_kits.log), from_other_lectures/L1_before_measure.json (L1's own log), ../L7-trust/experiments/logs/six_*.json,
modules/_v3/plans.py (the After of every kit), modules/<kit>/README.md and CHANGE.md.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
COURSE = HERE.parents[1]
L = HERE / "experiments" / "logs"
j = lambda p: json.loads(pathlib.Path(p).read_text())  # noqa: E731
FD = {}

PIECE = {"search_policy": ("L3", "the memory"), "find_supplier": ("L4", "the hands"), "find_item": ("L4", "the hands"),
         "check_stock": ("L4", "the hands"), "check_budget": ("L4", "the hands"),
         "create_purchase_request": ("L4", "a write tool, preview first"), "list_my_approvals": ("L5", "the pause"),
         "approve_purchase_request": ("L7", "approver only, own session"), "create_purchase_order": ("L4", "a write tool"),
         "release_purchase_order": ("L4", "a write tool"), "receive_goods": ("L4", "a write tool"),
         "order_status": ("L7", "read-back")}

# ---- Kavita's order through every piece
fd = j(L / "final_demo.json")
turns = []
for t in fd["turns"]:
    steps = []
    for s in t["steps"]:
        if s["kind"] == "model":
            steps.append({"k": "model", "tin": s["tokens_in"], "tout": s["tokens_out"], "calls": [c["tool"] for c in s["calls"]]})
        elif s["kind"] == "tool":
            res = s["result"]
            steps.append({"k": "tool", "tool": s["tool"], "args": s["args"], "ok": s["ok"], "piece": PIECE.get(s["tool"], ("L4", "the hands")),
                          "res": {k: res[k] for k in list(res)[:12] if k not in ("record",)}})
    turns.append({"user": t["user"], "text": t["text"], "reply": t["reply"], "steps": steps, "tokens": t["tokens"],
                  "inr": t["cost_inr"], "sec": t["model_s"]})
o = fd["order"]
FD["final"] = {"turns": turns, "totals": fd["totals"], "users": fd["users_seen"],
               "order": {k: o[k] for k in ("po_no", "status", "approved_by", "created_by", "gross_value", "basic_value", "pr_no",
                                            "cc_cd", "need_dt")},
               "grns": [g["grn_no"] for g in fd["grns"]], "stock": {s["whs_cd"]: s["on_hand"] for s in fd["stock"]},
               "events": {u: len(ev) for u, ev in fd["trust_events"].items()}}

# ---- L1's own Before measurement and L7's suite (provenance in the deck captions)
bm = j(L / "from_other_lectures" / "L1_before_measure.json")
FD["before"] = {"careful": bm["careful"]["totals"], "first": bm["first_time"]["totals"], "klm": bm["careful"].get("klm_minutes")}
L7 = COURSE / "lectures" / "L7-trust" / "experiments" / "logs"
six = j(L7 / "six_flash.json")["results"]
FD["l7"] = {c: {"passed": sum(r["passed"] for r in six if r["config"] == c), "cases": sum(1 for r in six if r["config"] == c),
                "ne": sum(len(r["never_events"]) for r in six if r["config"] == c)} for c in ("experience", "svc", "bare", "trust")}
rd = j(L7 / "retry_drill_after_fix.json")["summary"]
FD["l7_drill"] = {"redo_dup": rd["redo_job/all"]["duplicate_orders"], "keyed_ok": rd["keyed_tools/all"]["exactly_one_released"]}

# ---- HR leave on Ask Rasoi
try:
    lv = j(L / "leave_askrasoi.json")
    FD["leave"] = {"summary": lv["summary"], "tools": lv["tools"], "lint": lv["lint"],
                   "apply_json": json.loads(lv["tool_sources"]["apply_leave"]),
                   "rows": [{"sc": r["scenario"], "name": r["name"], "rep": r["rep"], "ok": r["passed"], "ne": r["never_events"],
                             "notes": r["notes"], "inr": r["cost_inr"],
                             "turns": [{"u": t["user"], "a": t["agent"]} for t in r["turns"]]} for r in lv["results"]]}
except FileNotFoundError:
    FD["leave"] = None

# ---- the kits: Before (README + test_kits.log) and After (plans.py)
ns = {}
exec((COURSE / "modules" / "_v3" / "plans.py").read_text(), ns)
log = (L / "test_kits.log").read_text()
table = {}
for line in log.splitlines():
    p = [x.strip() for x in line.split("|")]
    if len(p) >= 13 and p[0] in ns["PLANS"]:
        table[p[0]] = {"svcs": p[1], "procs": p[2], "screens": p[4], "docs": p[5], "seed": p[6], "happy": p[8],
                       "before": p[9], "traps": p[10], "ref": p[11], "naive": p[12], "tools": p[13] if len(p) > 13 else ""}
result = re.search(r"RESULT: (\w+)", log)
template = re.search(r"TEMPLATE kit: (.*)", log)
kits = []
for kit, plan in ns["PLANS"].items():
    readme = (COURSE / "modules" / kit / "README.md").read_text()
    title = readme.splitlines()[0].lstrip("# ").strip()
    after = re.search(r"\*\*After:\*\* (.*)", readme).group(1)
    before = re.search(r"\*\*Before:\*\* (.*)", readme).group(1)
    ch = json.loads((L / "demo_changes.json").read_text())["kits"][kit]["change"]
    ch_title = f"{ch['title']} ({ch['id']}, a {ch['kind']})"
    kits.append({"kit": kit, "title": title, "after": re.sub(r"[*_]", "", after), "before": re.sub(r"[*_]", "", before),
                 "silent": plan["silent"], "stale": plan["stale"], "workflow": plan["workflow"],
                 "tools": [{"name": t[0], "what": t[1], "writes": t[3]} for t in plan["tools"]],
                 "test": table.get(kit, {}), "change": ch_title})
FD["kits"] = kits
FD["kits_result"] = result.group(1) if result else None
FD["template"] = template.group(1) if template else None

# ---- demo-day changes, fairness re-measured
dc = j(L / "demo_changes.json")
FD["changes"] = {"summary": dc.get("summary"), "kits": {k: {"kind": v["change"]["kind"], "id": v["change"]["id"],
                 "title": v["change"]["title"], "fair": v.get("fair"),
                 "before": v.get("before_change_reference", {}).get("passed"),
                 "after": v.get("after_change_reference", {}).get("passed"),
                 "naive_caught": not v.get("naive", {}).get("passed", True)} for k, v in dc["kits"].items()}}
hr = dc["kits"]["hr_leave"]
FD["hr_change"] = {"announcement": hr["change"]["announcement"],
                   "before": {"passed": hr["before_change_reference"]["passed"], "ne": hr["before_change_reference"]["never_events"],
                              "notes": hr["before_change_reference"]["notes"]},
                   "after": {"passed": hr["after_change_reference"]["passed"],
                             "last": (hr["after_change_reference"]["turns"][-1]["agent"] if hr["after_change_reference"].get("turns") else "")},
                   "naive": {"passed": hr["naive"]["passed"], "ne": hr["naive"]["never_events"]}}

out = HERE / "figdata.js"
out.write_text("/* Generated by gen_figdata.py from experiments/logs. Do not edit by hand. */\nwindow.FD = "
               + json.dumps(FD, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("wrote", out, out.stat().st_size // 1024, "KB")
