"""Lecture 4, section 10: one table, before -> after, from the measured logs.

    python lectures/L4-the-hands/experiments/production_merge.py

Reads logs/production_grade_before.json and _after.json (production_grade.py, on Modal), logs/host_matrix.json
(host_matrix.py) and logs/mcp_raw.json, reads change management from the tool folders as they are now, and writes
logs/production_grade.json: each criterion, its threshold, the measured value before and after, and pass/fail.
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))
L = HERE / "logs"
B = json.loads((L / "production_grade_before.json").read_text())
A = json.loads((L / "production_grade_after.json").read_text())
M = json.loads((L / "host_matrix.json").read_text())
from ledgerline.toolbox import REGISTRY  # noqa: E402


def schema_row(d):
    s = d["schema"]
    happy_viol = sum(len(v["output_violations"]) for v in s.values())
    return {"tools": len(s), "with_input_schema": sum(v["has_input_schema"] for v in s.values()),
            "with_output_schema": sum(v["has_output_schema"] for v in s.values()),
            "refuse_bad_input_at_the_door": sum(v["door_ok"] for v in s.values()),
            "output_violations_happy_path": happy_viol,
            "output_violations_detail": {k: v["output_violations"] for k, v in s.items() if v["output_violations"]},
            "ok_results_checked_in_fuzzing": d["fuzzing"].get("ok_results_checked"),
            "output_violations_in_fuzzing": d["fuzzing"].get("ok_result_output_violation_count", 0)
            if "ok_results_checked" in d["fuzzing"] else None}


def fuzz_row(d):
    f = d["fuzzing"]
    return {"calls": f["calls"], "by_kind": f["by_kind"], "unhandled_or_non_business_pct": f["unhandled_or_non_business_pct"],
            "errors_in_structured_contract_pct": f["errors_in_contract_pct"],
            "nonsense_quantities_saved": f.get("nonsense_quantities_saved"),
            "examples": {k: [e["case"] + " -> " + str(e["result"].get("error"))[:90] for e in v[:2]] for k, v in f["examples"].items()}}


def lat_row(d):
    la = d["latency"]
    return {"toolbox_overhead_ms": la["all_tools_overhead_ms"], "via_mcp_overhead_ms": la["all_tools_overhead_via_mcp_ms"],
            "slowest_tool_p99": max(((k, v["overhead_ms"]["p99"]) for k, v in la["per_tool"].items()), key=lambda x: x[1]),
            "where": la["where"]}


def pay_row(d):
    p = d["payload"]
    at = {k: v["at_scale"] for k, v in p["per_tool"].items() if v.get("at_scale")}
    return {"limit_bytes": p["limit_bytes"], "max_bytes_seed_data": p["max_bytes"], "max_bytes_at_scale": p["max_bytes_at_scale"],
            "over_limit": p.get("over_limit", [k for k, v in at.items() if v["bytes"] > p["limit_bytes"]]),
            "at_scale": at, "list_tools": p["list_tools"], "list_tools_paginating": p["list_tools_paginating"]}


def idem_row(d):
    i = d["idempotency"]
    dup = lambda sc: {k: v["duplicates"] for k, v in i[sc].items() if isinstance(v, dict) and v.get("duplicates")}  # noqa: E731
    return {"lost_reply_then_retry": i["A_lost_reply_then_retry"]["_duplicates"],
            "retry_with_rewritten_arguments": i["B_retry_with_rewritten_arguments"]["_duplicates"],
            "deliberate_resend": i["C_plain_resend"]["_duplicates"],
            "where": {"A": dup("A_lost_reply_then_retry"), "B": dup("B_retry_with_rewritten_arguments"), "C": dup("C_plain_resend")}}


def tmo_row(d):
    t = d["timeouts"]
    return {"tools": len(t), "declared": sum(bool(v["declared"]) for v in t.values()),
            "tested": sum(v["tested"] for v in t.values()), "passed": sum(v["passed"] for v in t.values()),
            "tools_all_pass": sum(v["passed"] == v["tested"] for v in t.values())}


def reg_row(d):
    r = d["regression"]
    return {"tools_passing": r["tools_passing"], "tools": r["tools"], "write_tools_passing": r["write_tools_passing"],
            "write_tools": r["write_tools"],
            "failing": {k: [c for c, v in row.items() if v is False] for k, row in r["per_tool"].items() if not row["pass"]}}


def change_now():
    specs = {n: s.spec for n, s in REGISTRY.items()}
    tags = subprocess.run(["git", "tag"], capture_output=True, text=True, cwd=str(ROOT)).stdout.split()
    mcp = json.loads((L / "mcp_raw.json").read_text())
    listed = {t["name"]: t for t in mcp["all_tools"]["tools_list"]["result"]["tools"]}
    return {"tools": len(specs), "with_version": sum(bool(s.get("version")) for s in specs.values()),
            "versions": {n: s.get("version") for n, s in specs.items()},
            "version_published_over_mcp": sum(bool((listed.get(n, {}).get("_meta") or {}).get("ledgerline/version")) for n in specs),
            "with_release_notes": sum(bool(s.get("release_notes")) for s in specs.values()),
            "rollback": f"git tags {tags} (L3–L12 notebooks pin v3.1); the default tool set and its schemas are unchanged, "
                        "so recorded runs still replay (logs/compat_check.json)",
            "client_sign_off": "not applicable in the sandbox: a process step with the client"}


hosts = {h: v for h, v in M["hosts"].items() if "pass_at_1" in v}
rows = []


def add(area, criterion, threshold, before, after, ok_before, ok_after, note=""):
    rows.append({"area": area, "criterion": criterion, "threshold": threshold, "before": before, "after": after,
                 "pass_before": ok_before, "pass_after": ok_after, "note": note})


sb, sa = schema_row(B), schema_row(A)
add("Schema", "Input and output validation", "100% of tools; 0 schema violations in regression", sb, sa,
    sb["refuse_bad_input_at_the_door"] == sb["tools"] and sb["output_violations_happy_path"] == 0,
    sa["refuse_bad_input_at_the_door"] == sa["tools"] and sa["output_violations_happy_path"] == 0 and not sa["output_violations_in_fuzzing"],
    "before: create_purchase_order returned warning=null against a string schema; after, every ok result met in fuzzing "
    "is also checked (0 violations)")
fb, fa = fuzz_row(B), fuzz_row(A)
add("Reliability", "Unhandled or non-business errors", "<= 0.1% of calls; 100% in the structured error contract", fb, fa,
    fb["unhandled_or_non_business_pct"] <= 0.1 and fb["errors_in_structured_contract_pct"] == 100,
    fa["unhandled_or_non_business_pct"] <= 0.1 and fa["errors_in_structured_contract_pct"] == 100,
    "before: bad dates reached Ledgerline (ERR-SYS-0422) and quantities of 0 or below were saved and auto-approved; "
    "after: both refused at the door")
add("LLM usability", "Right tool, right arguments on a 30-task golden set, per host", ">= 95% pass@1, reported per host",
    "not measured before", {h: {"pass_at_1": v["pass_at_1"], "passed": v["passed"], "model": v["model"],
                                "fails": [f"{r['id']}: {r['reason'][:80]}" for r in v["results"] if not r["pass"]]} for h, v in hosts.items()},
    None, all(v["pass_at_1"] >= 0.95 for v in hosts.values()),
    "Claude's misses are all reads before a write (order_status / list_my_approvals before release or approve), "
    "not wrong arguments; first-call scoring counts them as misses")
lb, la = lat_row(B), lat_row(A)
okl = lambda x: x["p50"] <= 50 and x["p95"] <= 100 and x["p99"] <= 200  # noqa: E731
add("Latency", "Tool overhead, excluding ERP service time", "p50 <= 50 ms, p95 <= 100 ms, p99 <= 200 ms", lb, la,
    okl(lb["toolbox_overhead_ms"]) and okl(lb["via_mcp_overhead_ms"]), okl(la["toolbox_overhead_ms"]) and okl(la["via_mcp_overhead_ms"]),
    "the p95/p99 tail is search_policy (in-memory hybrid search, no Ledgerline call); every other tool is under 1 ms")
pb, pa = pay_row(B), pay_row(A)
add("Payload", "Response size; every list tool paginates", "every list tool paginates; nothing above the agreed size limit", pb, pa,
    not pb["over_limit"] and set(pb["list_tools"]) == set(pb["list_tools_paginating"]),
    not pa["over_limit"] and set(pa["list_tools"]) == set(pa["list_tools_paginating"]),
    "size: list_my_approvals with 1,000 waiting was 167 KB, now capped at 50 rows with total/has_more (8.5 KB). "
    "Pagination: only the new supplier_certificates takes limit/cursor; adding them to the five older list tools changes "
    "their model-facing schemas, which breaks every recorded run, so it is scheduled as a versioned 1.1 schema change")
ib, ia = idem_row(B), idem_row(A)
add("Idempotency", "Duplicate or retried writes", "0 duplicate postings", ib, ia,
    ib["lost_reply_then_retry"] + ib["retry_with_rewritten_arguments"] == 0,
    ia["lost_reply_then_retry"] + ia["retry_with_rewritten_arguments"] == 0,
    "the lecture's 'find and fix one failing criterion': 6 duplicates -> 0. A deliberate resend of the same call "
    "(C) still posts twice for receive_goods and send_message: two equal deliveries or messages can both be real, so "
    "these tools say idempotentHint=false; the fix is a client idempotency key (a 1.1 schema change)")
tb, ta = tmo_row(B), tmo_row(A)
add("Timeouts", "Timeout and retry policy", "defined and tested on 100% of tools", tb, ta,
    tb["declared"] == tb["tools"] and tb["tools_all_pass"] == tb["tools"], ta["declared"] == ta["tools"] and ta["tools_all_pass"] == ta["tools"],
    "the policy was always in the code (reads retry twice, writes look themselves up); before, no tool declared it; "
    "now tool.json has policy and the MCP server publishes it in _meta. Tested by injecting a busy server, an outage "
    "and a lost reply on every service each tool calls. The sandbox simulates Ledgerline's 30 s reply timeout")
rb, ra = reg_row(B), reg_row(A)
add("Regression", "Happy path, validation errors, permission denied, pagination, retries", ">= 98% of tools; 100% of write tools", rb, ra,
    rb["tools_passing"] / rb["tools"] >= 0.98 and rb["write_tools_passing"] == rb["write_tools"],
    ra["tools_passing"] / ra["tools"] >= 0.98 and ra["write_tools_passing"] == ra["write_tools"],
    "after: all 8 write tools pass; the 5 read tools that fail, fail only on pagination")
mc = {h: {"definitions_accepted": v["definitions_accepted"], "pass_at_1": v["pass_at_1"]} for h, v in hosts.items()}
add("MCP compliance", "Conformance on Claude, OpenAI, Gemini and our harness", "100% of tools on all 4",
    "not measured before", {"hosts": mc, "tools_right_on_every_host": f"{M['tools_passing_on_all_hosts']}/{len(M['per_tool'])}",
                            "per_tool": M["per_tool"]},
    None, M["tools_passing_on_all_hosts"] == len(M["per_tool"]),
    "every host accepted all 16 definitions; the 4 tools not right everywhere are release_purchase_order, "
    "approve_purchase_request, approve_purchase_order (Claude reads first) and create_purchase_order (OpenAI, once)")
cb = {"tools": B["n_tools"], "with_version": sum(bool(v) for v in B["change_management"]["version_in_tool_json"].values()),
      "version_published_over_mcp": sum(bool(v) for v in B["change_management"].get("version_published_over_mcp", {}).values()),
      "with_release_notes": 0}
cn = change_now()
add("Change management", "Versioning, release notes, rollback", "documented and signed off by the client", cb, cn, False, False,
    "after: every tool has a version (7 changed tools are now 1.1, with release notes in tool.json), published over MCP; "
    "rollback is a git tag; client sign-off cannot happen in the sandbox, so this stays open")

out = {"generated_from": ["logs/production_grade_before.json", "logs/production_grade_after.json", "logs/host_matrix.json",
                          "logs/mcp_raw.json", "tool folders (change management)"],
       "before_commit": "6e6f4d0 (15 tools)", "after": "this commit (16 tools)",
       "the_fix_for_the_lecture": {"criterion": "Idempotency", "before": ib, "after": ia,
                                   "what_changed": ["need_by is checked and rewritten as YYYY-MM-DD at the door (ToolSpec.check, "
                                                    "tool.json argument_formats), so the content key is the same however the date is written",
                                                    "receive_goods and send_message look themselves up after a lost reply instead of "
                                                    "returning TIMEOUT (the retry was the duplicate)"]},
       "criteria": rows,
       "summary": [{"area": r["area"], "threshold": r["threshold"], "pass_before": r["pass_before"], "pass_after": r["pass_after"]}
                   for r in rows]}
(L / "production_grade.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
for r in out["summary"]:
    print(f"{r['area']:18} before {str(r['pass_before']):5} after {str(r['pass_after']):5}  ({r['threshold']})")
