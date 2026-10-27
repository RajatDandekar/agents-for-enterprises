"""Build figdata.js for the Lecture 8 deck from the logs (stdlib only; no model calls).

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L8-your-module/gen_figdata.py

Every number on a Lecture 8 plate is read here from a log; the source path travels with it into figdata.js.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1]


def J(rel):
    return json.loads((C / rel).read_text())


D = {"sources": {}}


def ind(n) -> str:
    """Indian digit grouping: 1199469 -> 11,99,469."""
    s = str(int(round(n)))
    neg, s = s.startswith("-"), s.lstrip("-")
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        s = head + "," + tail
    return ("-" if neg else "") + s


def src(key, rel):
    D["sources"][key] = rel


# ---------------------------------------------------------------- the eight kits: befores (modules/test_kits.log)
rows = {}
for line in (C / "modules/test_kits.log").read_text().splitlines():
    m = re.match(r"(\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| ok \| ok (.*?) \| (\d+) calls/(\d+) scr/(\d+) fields \| (\S+) \| (\S+) \| (\S+)", line)
    if m:
        rows[m.group(1)] = {"svcs": int(m.group(2)), "procs": int(m.group(3)), "tables": int(m.group(4)),
                            "screens": int(m.group(5)), "docs": int(m.group(6)), "seed": int(m.group(7)),
                            "happy": m.group(8), "calls": int(m.group(9)), "scr": int(m.group(10)),
                            "fields": int(m.group(11)), "traps": m.group(12), "ref": m.group(13), "naive": m.group(14)}
readme = (C / "modules/README.md").read_text()
for line in readme.splitlines():
    m = re.match(r"\| ([^|]+?) \| `(\w+)_` \| ([^|]+?) \| \"(.+?)\" \| (.+?) \| \[(\w+)\]", line)
    if m and m.group(6) in rows:
        rows[m.group(6)].update(title=m.group(1).strip(), prefix=m.group(2), speaker=m.group(3).strip(),
                                after=m.group(4), silent=m.group(5).strip())
D["kits"] = rows
src("kits", "modules/test_kits.log + modules/README.md")

# ---------------------------------------------------------------- the demo-day changes (fairness test)
dc = J("lectures/L8-your-module/experiments/logs/demo_changes.json")
ch = {}
for name, r in dc["kits"].items():
    def t(x):
        return [{"u": y["user"], "a": y["agent"], "w": y["writes"], "as": y.get("users")} for y in x["turns"]]
    ch[name] = {"change": r["change"], "doc": r["doc"], "fair": r["fair"],
                "A": [x["passed"] for x in r["kit_reference_with_change"]],
                "old": {"passed": r["before_change_reference"]["passed"], "ne": r["before_change_reference"]["never_events"],
                        "notes": r["before_change_reference"]["notes"], "turns": t(r["before_change_reference"])},
                "new": {"passed": r["after_change_reference"]["passed"], "ne": r["after_change_reference"]["never_events"],
                        "turns": t(r["after_change_reference"])},
                "naive": {"passed": r["naive"]["passed"], "ne": r["naive"]["never_events"]},
                "all": r["after_change_all_kits"]["passed"],
                "ask": r["after_change_reference"]["turns"][0]["user"]}
D["changes"] = ch
D["changes_summary"] = dc["summary"]
src("changes", "lectures/L8-your-module/experiments/logs/demo_changes.json")

# ---------------------------------------------------------------- the arc: one headline per lecture
by = J("lectures/L1-the-form/experiments/logs/by_hand.json")
nv = J("lectures/L1-the-form/experiments/logs/naive_sweep.json")["summary"]["default"]
rv = J("lectures/L2-the-manual/experiments/logs/rag_vs_wiki.json")["summary"]
an = J("lectures/L3-the-hands/experiments/logs/analysis.json")["granularity"]["gemini:gemini-3.8-flash"]
fg = J("lectures/L4-the-route/experiments/logs/forty_graph.json")["summary"]
fl = J("lectures/L4-the-route/experiments/logs/forty_loop.json")["summary"]
rb = {t: J(f"lectures/L5-the-signature/experiments/logs/readback_{t}.json")["summary"] for t in ("small", "default", "large")}
s6 = J("lectures/L5-the-signature/experiments/logs/six_l5_default.json")["results"]
sg = {t: J(f"lectures/L6-the-inspector/experiments/logs/suite_{t}.json")["summary"] for t in ("graph", "loop", "naive")}
bm = J("lectures/L6-the-inspector/experiments/logs/bots_matrix.json")
rs = J("lectures/L7-the-night-shift/experiments/logs/retry_sweep.json")["summary"]
D["arc"] = [
    {"lec": "L1", "title": "The Form", "jobs": [], "head": f"By hand: {by['monday_counts']['screens opened']} screens, "
     f"{by['monday_counts']['fields typed']} fields, {by['monday_counts']['codes typed']} codes, 2 sign-ins; the order saved as a Draft. "
     f"Naive agent on 38 raw services: {nv['passed']} of 6, ₹{nv['cost_inr']:.2f}.",
     "big": f"{nv['passed']}/6", "bigl": "naive agent", "src": "L1 by_hand.json, naive_sweep.json (default)"},
    {"lec": "L2", "title": "The Manual", "jobs": [4], "head": f"Retrieval with citations: {rv['rag']['all']['correct']} of 40 right, "
     f"gold clause cited on {rv['rag']['all']['gold_cited']} of {rv['rag']['all']['gold_q']}, ₹{rv['rag']['cost_inr_40']:.2f} for all 40. "
     f"Without the manual: {rv['closed']['all']['correct']} of 40.",
     "big": f"{rv['rag']['all']['correct']}/40", "bigl": "policy answers", "src": "L2 rag_vs_wiki.json"},
    {"lec": "L3", "title": "The Hands", "jobs": [3], "head": f"Intent tools: {an['intent']['passed']} of 30 tasks at "
     f"{ind(an['intent']['tokens_mean'])} tokens a task; 38 raw services: {an['raw']['passed']} of 30 at {ind(an['raw']['tokens_mean'])}.",
     "big": f"{an['intent']['passed']}/30", "bigl": "tasks, a seventh of the tokens", "src": "L3 analysis.json (flash)"},
    {"lec": "L4", "title": "The Route", "jobs": [1, 2, 5], "head": f"Control graph {fg['passed']} of 40, free loop {fl['passed']} of 40; "
     f"{ind(fg['tokens_in'] + fg['tokens_out'])} vs {ind(fl['tokens_in'] + fl['tokens_out'])} tokens, ₹{fg['cost_inr']:.2f} vs ₹{fl['cost_inr']:.2f}.",
     "big": f"{fg['passed']}/40", "bigl": "multi-step cases", "src": "L4 forty_graph.json, forty_loop.json"},
    {"lec": "L5", "title": "The Signature", "jobs": [6, 7], "head": f"Drafts caught: bare agent {sum(v['bare']['caught'] for v in rb.values())} of 30, "
     f"harness read-back {sum(v['harness']['caught'] for v in rb.values())} of 30. Six scenarios: {sum(r['passed'] for r in s6)} of 6, as Kavita, never the service account.",
     "big": f"{sum(v['harness']['caught'] for v in rb.values())}/30", "bigl": "silent Drafts caught", "src": "L5 readback_*.json, six_l5_default.json"},
    {"lec": "L6", "title": "The Inspector", "jobs": [9], "head": f"60-case suite: graph {sg['graph']['passed']}, tool loop {sg['loop']['passed']}, naive {sg['naive']['passed']}; "
     f"0 never-events for the graph; ₹{sg['graph']['inr_per_resolved_order']:.2f} per resolved order; "
     f"{sum(1 for r in bm['rows'] if r['caught'])} of {sum(1 for r in bm['rows'] if r['targets'] and r['targets'] != ['tone'])} broken bots caught.",
     "big": f"{sg['graph']['passed']}/60", "bigl": "suite cases", "src": "L6 suite_*.json, bots_matrix.json"},
    {"lec": "L7", "title": "The Night Shift", "jobs": [8], "head": f"50 injected faults: redoing the job duplicated in {rs['naive_job/all']['trials_with_duplicate']} "
     f"(₹{ind(rs['naive_job/all']['extra_inr'])} extra committed); the keyed workflow: {rs['keyed/all']['exactly_one_released']} of 50 with exactly one released order.",
     "big": f"{rs['keyed/all']['exactly_one_released']}/50", "bigl": "faults, one order each", "src": "L7 retry_sweep.json"},
]
D["arc_raw"] = {"by_hand": by["monday_counts"], "naive_default": {k: nv[k] for k in ("passed", "cost_inr", "tokens_in", "tokens_out")},
                "suite": {t: {k: v[k] for k in ("passed", "cases", "ci95", "never_event_cases", "inr_per_resolved_order", "turn_p95", "inr")}
                          for t, v in sg.items()}}

# ---------------------------------------------------------------- the final demo
j = J("demo/logs/journey.json")
steps = []
for s in j["steps"]:
    r = s.get("response") or {}
    steps.append({"who": s["who"], "what": s["what"], "text": (s.get("body") or {}).get("text"),
                  "reply": r.get("reply"), "trace": r.get("trace"), "waiting": r.get("waiting_on"),
                  "status": r.get("status"), "detail": r.get("detail"), "items": r.get("items"), "slack": r.get("slack"),
                  "bahi": r.get("bahi"), "kavita_sees": r.get("kavita_sees")})
audit = []
for e in j["audit"]:
    audit.append({"seq": e["seq"], "t": e.get("t", "")[11:19], "kind": e["kind"], "actor": e.get("actor"),
                  "line": (e.get("text") or e.get("tool") or "").split("\n")[0][:110], "saw": e.get("saw"),
                  "writes": e.get("writes"), "rb": (e.get("read_back") or {}).get("status_code") if e.get("read_back") else None,
                  "decision": e.get("decision"), "doc": e.get("doc_no"), "nb": len(e.get("bahi") or [])})
D["journey"] = {"steps": steps, "checks": j["checks"], "audit": audit, "audit_summary": j["audit_summary"], "llm": j["llm"],
                "final_po": {k: j["final_po"][k] for k in ("po_no", "pr_no", "sup_cd", "cc_cd", "tax_cd", "status", "basic_value",
                                                          "tax_value", "gross_value", "created_by", "approved_by", "released_on",
                                                          "client_ref")},
                "acts_as": j["acts_as"], "legacy": j.get("legacy_client"), "mode": j.get("mode"),
                "bahi_users": sorted({r["user_id"] for r in j["bahi_rows"]}),
                "bahi_writes": [r["svc"] for r in j["bahi_rows"] if r["svc"] in ("pr_save", "pr_submit", "pr_approve", "po_save",
                                                                                  "po_release", "po_approve", "po_fetch")]}
src("journey", "demo/logs/journey.json")
cw = J("demo/logs/crash_drill.json")
D["crash"] = {"down_h": cw["down_h"], "diary": cw["result"]["diary"], "reminder": cw["reminder"],
              "A": cw["attempts_worker_A"], "B": cw["attempts_worker_B"], "requests": cw["requests"], "orders": cw["orders"],
              "before": cw["status_before_crash"]["stage"], "after": cw["status_after_restart"],
              "while_down": cw["reminders_sent_while_no_worker"], "outcome": cw["result"]["outcome"]}
ks = J("demo/logs/kill_switch.json")
D["kill"] = {"diary": ks["result"]["diary"], "paused_minutes": ks["result"]["paused_minutes"],
             "orders_while_paused": ks["orders_while_paused"], "orders_after": ks["orders_after"],
             "requests_written_by_tool": ks["requests_written_by_tool"], "ladder": ks.get("ladder"),
             "commit_refused": ks.get("tool_commit_with_switch_on"), "outcome": ks["result"]["outcome"]}
src("crash", "demo/logs/crash_drill.json")
src("kill", "demo/logs/kill_switch.json")
sc = J("demo/logs/scorecard.json")
D["score"] = {"summary": {k: sc["summary"][k] for k in ("cases", "passed", "pass_rate", "ci95", "never_event_cases", "inr",
                                                         "inr_per_resolved_order", "turn_p50", "turn_p95", "sim_inr", "llm_calls",
                                                         "tokens", "by")},
              "gate": sc["gate"], "card": sc["trust_scorecard"], "failed": sc["failed_cases"], "compare": sc["compare_l6"],
              "mode": sc["mode"], "six": sc["six_scenarios"]}
ni = J("demo/logs/scorecard_no_inbox.json")
D["score"]["no_inbox"] = {"passed": ni["summary"]["passed"], "cases": ni["summary"]["cases"], "failed": [r["id"] for r in ni["failed_cases"]],
                          "gate": ni["gate"]["passed"]}
src("score", "demo/logs/scorecard.json (suite: demo/logs/scorecard_suite.json, gate: demo/logs/scorecard_gate.json)")
D["before"] = {"monday": by["monday_counts"], "by_person": by["monday_by_person"], "saved": by["status_bar_after_save"],
               "status": by["status_field_after_save"], "tax_error": by["tax_error"], "friday": by["friday_release"],
               "minutes": by.get("monday_minutes_estimate_klm")}
src("before", "lectures/L1-the-form/experiments/logs/by_hand.json")

(HERE / "figdata.js").write_text("/* Generated by gen_figdata.py from the logs named in L8.sources. Do not edit by hand. */\n"
                                 "window.L8 = " + json.dumps(D, ensure_ascii=False, indent=0) + ";\n")
print("wrote figdata.js", len(json.dumps(D)), "bytes;", len(rows), "kits;", len(ch), "changes")
for a in D["arc"]:
    print(a["lec"], a["big"], "·", a["head"])
