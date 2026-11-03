"""Build figdata.js (window.L4) for the Lecture 4 deck from the recorded experiment logs. Nothing is typed by hand.

    python3 lectures/L4-the-hands/gen_figdata.py          (standard library only; safe on the laptop)

Reads experiments/logs/*.json (written by the experiment scripts next to them) and the tool folders in
ledgerline/ledgerline/toolbox/. Every number the deck shows comes from one of these files:
  anatomy_check_stock.json   check_stock's files, services, one real call with its legacy envelopes, the error paths
  new_tool_build.json        supplier_certificates, built in six steps
  mcp_raw.json               raw JSON-RPC lines from our stdio server; the MCP field alignment before and after
  our_harness.json           our harness: runs single, order, order_hands, the full context at every model call
  claude_harness*.json       Claude Code (headless, claude-sonnet-5.5 via OpenRouter) on our MCP server
  claude_runs/*.events.jsonl every stream-json event of those runs (used to split the steps by user turn)
  host_matrix.json           30 golden tasks on five hosts
  production_grade.json      the ten criteria before and after
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "experiments" / "logs"
ROOT = HERE.parents[1]
TOOLBOX = ROOT / "ledgerline" / "ledgerline" / "toolbox"


def J(name):
    return json.loads((LOGS / name).read_text())


def cut(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 1] + "…"


out = {"_source": "gen_figdata.py from lectures/L4-the-hands/experiments/logs (see the docstring)"}

# ---------------------------------------------------------------- the toolbox (16 folders)
order = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "create_purchase_request",
         "list_my_approvals", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
         "release_purchase_order", "order_status", "receive_goods", "register_supplier", "send_message", "supplier_certificates"]
tb = []
for n in order:
    j = json.loads((TOOLBOX / n / "tool.json").read_text())
    tb.append({"name": n, "title": j["title"], "category": j.get("category"), "writes": bool(j.get("writes")),
               "version": j.get("version"), "services": j.get("services", []),
               "args": list(j["input_schema"].get("properties", {})), "required": j["input_schema"].get("required", []),
               "annotations": j.get("annotations", {}), "description": j["description"],
               "input_schema": j["input_schema"], "argument_formats": j.get("argument_formats"), "example": j.get("example"), "lines": len((TOOLBOX / n / "tool.py").read_text().splitlines())})
out["toolbox"] = tb

# ---------------------------------------------------------------- 3 · open a tool: check_stock
a = J("anatomy_check_stock.json")
out["anatomy"] = {
    "path": a["files"]["path"], "tool_json": a["files"]["tool.json"], "tool_py": a["files"]["tool.py"],
    "services": [{k: s[k] for k in ("name", "legacy_title", "kind", "screen", "fields", "source", "defined_in")} for s in a["services"]],
    "services_found_in": a["services_found_in"],
    "model_request": a["model_request"], "door": a["checked_at_the_door"], "legacy_calls": a["legacy_calls"],
    "tool_result": a["tool_result"], "sizes": a["sizes"], "what_the_model_sees": a["what_the_model_sees"],
    "error_path": a["error_path"], "error_wrong_type": a["error_path_wrong_type"], "mcp": a["mcp"]}

# ---------------------------------------------------------------- 4 · build a tool from scratch
b = J("new_tool_build.json")
out["build"] = {"tool": b["tool"], "job": b["1_job"], "services": b["2_services_found"], "schema": b["3_schema"],
                "code": b["4_code"], "tool_py": b["4_code"]["tool.py"], "errors": b["5_error_contract"],
                "tests": {k: b["6_tests"][k] for k in ("file", "assertions", "passed", "whole_file_passed", "markers")},
                "tests_src": b["6_tests"]["section"], "mcp_definition": b["mcp_definition"], "mcp_call": b["mcp_call"],
                "registered": b["registered"]}

# ---------------------------------------------------------------- 5–6 · MCP on the wire
m = J("mcp_raw.json")
one = m["one_tool"]
out["mcp"] = {
    "protocol_asked": m["protocol_version_asked"], "protocol": m["alignment"]["protocol_version"], "sdk": m["sdk"],
    "server_args": one["server_args"],
    "lines": [{"t": r["t"], "dir": r["dir"], "msg": json.loads(r["line"])} for r in one["raw_lines"]],
    "all_tools_count": len(m["all_tools"]["tools_list"]["result"]["tools"]),
    "alignment": m["alignment"], "diff_check_stock": m["diff_check_stock"],
    "same_name_description_inputSchema": m["same_name_description_inputSchema"]}
cs = J("claude_harness_single.json")
out["mcp"]["claude_client_initialize"] = cs["wire"]["client_initialize"]

# ---------------------------------------------------------------- 7–9 · our harness, with the context at every call
oh = J("our_harness.json")


def context_blocks(run):
    """The context, part by part, in the order it entered, each tagged with the model call that first saw it."""
    parts = run["context_parts"]
    steps = [s for s in run["steps"] if s["tools"] is not None] or run["steps"]
    blocks, pi = [], 0
    s0 = steps[0]["messages"]
    kinds = {"system prompt": "system", "user message": "user", "tool call (model -> our code)": "call",
             "tool result (only what the tool returned)": "result", "assistant reply": "reply"}
    for p in parts[:3]:  # system, tool definitions, the first user message: all seen by call 0
        k = "tools" if p["part"].startswith("tool definitions") else kinds[p["part"]]
        text = p.get("text") or ""
        if k == "tools":
            text = json.dumps([t["function"] for t in run["tool_definitions"]], indent=1, ensure_ascii=False)
        blocks.append({"kind": k, "label": p["part"], "tokens": p["tokens"], "text": text, "seen_from": 0,
                       "names": p.get("tools")})
    pi = 3
    prev = steps[0]
    for si, st in enumerate(steps[1:], start=1):
        new = st["messages"][len(prev["messages"]):]
        for msg in new:
            p = parts[pi]
            pi += 1
            k = kinds[p["part"]]
            if k == "call":
                text = json.dumps(p["calls"], ensure_ascii=False)
            elif k == "result":
                text = p["content"]
            else:
                text = p.get("text") or ""
            blocks.append({"kind": k, "label": p["part"], "tokens": p["tokens"], "text": text, "seen_from": si,
                           "note": p.get("note")})
        prev = st
    assert pi == len(parts), (pi, len(parts))
    final = run["steps"][-1]
    return blocks, {"text": final["reply"]["content"], "tokens": final["completion_tokens"]}


ours = {}
for label in ("single", "order", "order_hands"):
    r = oh[label]
    blocks, final = context_blocks(r)
    steps = [{"call": s["call"], "prompt_tokens": s["prompt_tokens"], "completion_tokens": s["completion_tokens"],
              "messages": len(s["messages"]), "tool_calls": s["tool_calls"], "text": s["reply"]["content"]} for s in r["steps"]]
    # check: the parts seen by call k add up to call k's prompt_tokens
    sums = [sum(b["tokens"] or 0 for b in blocks if b["seen_from"] <= i) for i in range(len(steps))]
    ours[label] = {
        "model": r["model"], "harness": r["harness"], "prompt_name": r.get("system_prompt_name", "harness.AGENT (the app's agent prompt)"),
        "system_prompt": r["system_prompt"], "tools_exposed": r["tools_exposed"],
        "turns": [{"user": t["user"], "reply": t["reply"], "rounds": t["rounds"], "model_calls": t["model_calls"],
                   "tokens_in": t["tokens_in"], "tokens_out": t["tokens_out"],
                   "cards": [{"tool": c["tool"], "args": c["args"], "ok": c["result"].get("ok") if isinstance(c["result"], dict) else None,
                              "result": cut(c["result"], 900), "ms": c.get("ms")} for c in t["cards"]]} for t in r["turns"]],
        "steps": steps, "blocks": blocks, "final": final, "sums_check": sums,
        "summary": r["summary"], "errors": r["observed_model_errors"], "never": r["what_never_enters_the_context"],
        "only_tool_returns": r["check_only_tool_returns_in_context"], "after": r["ledgerline_after"],
        "service_calls": r["ledgerline_service_calls"]}
out["ours"] = ours
out["prompt_codes"] = oh["order_hands"].get("prompt_codes_compared")
out["price_note"] = oh["note"]


# ---------------------------------------------------------------- Claude Code (headless) on our MCP server
def claude_run(label):
    d = J(f"claude_harness_{label}.json")
    turns, cur, names = [], [], {}
    for line in (LOGS / "claude_runs" / f"{label}.events.jsonl").read_text().splitlines():
        e = json.loads(line)
        t = e.get("type")
        if t == "assistant":
            for c in e["message"]["content"]:
                if c["type"] == "text" and c["text"].strip():
                    cur.append({"kind": "text", "text": c["text"]})
                elif c["type"] == "tool_use":
                    n = c["name"].replace("mcp__northbridge__", "")
                    names[c["id"]] = n
                    cur.append({"kind": "call", "tool": n, "args": c["input"], "id": c["id"]})
                elif c["type"] == "thinking":
                    cur.append({"kind": "thinking", "chars": len(c.get("thinking", ""))})
        elif t == "user":
            for c in e["message"]["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    content = c["content"] if isinstance(c["content"], str) else json.dumps(c["content"])
                    cur.append({"kind": "result", "tool": names.get(c["tool_use_id"]), "is_error": c.get("is_error"),
                                "text": cut(content, 900)})
        elif t == "result":
            turns.append({"steps": cur, "num_turns": e.get("num_turns"), "usage": e.get("usage"),
                          "cost_usd_cumulative": e.get("total_cost_usd"), "duration_ms": e.get("duration_ms"),
                          "reply": e.get("result")})
            cur = []
    for i, t in enumerate(turns):
        t["user"] = d["turns"][i]
    return {"model": "claude-sonnet-5.5", "model_id": d["init"]["model"], "claude_code": d["claude_version"],
            "route": d["route"], "turns": turns, "summary": d["summary"], "seconds": d["seconds"],
            "tools_exposed": d["tools_exposed"], "appended_system_prompt": d.get("appended_system_prompt"),
            "mcp_servers": d["init"]["mcp_servers"], "cmd_flags": [x for x in d["cmd"] if x.startswith("--")]}


ch = J("claude_harness.json")
out["claude"] = {"single": claude_run("single"), "order_hands": claude_run("order_hands"),
                 "order": {k: ch["runs"]["order"][k] for k in ("tool_sequence", "tool_calls", "tool_errors", "claude_code_turns", "final_reply")},
                 "findings": ch["findings"], "attempts": [{k: x[k] for k in ("attempt", "flags", "result")} for x in ch["attempts"]],
                 "harness": ch["harness"], "to_run_on_the_plan": ch["to_run_on_the_plan"],
                 "in_our_control": ch["comparison"]["in_our_control"], "left_to_claude": ch["comparison"]["left_to_claude"],
                 "compare_hands": ch["comparison"]["order_on_the_hands_prompt"]}
for lab in ("single", "order_hands"):
    tok = [t["usage"] for t in out["claude"][lab]["turns"]]
    out["claude"][lab]["tokens_in"] = sum(u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"] for u in tok)
    out["claude"][lab]["tokens_out"] = sum(u["output_tokens"] for u in tok)
    out["claude"][lab]["cache_read"] = sum(u["cache_read_input_tokens"] for u in tok)

# ---------------------------------------------------------------- 10 · production grade and the host matrix
hm = J("host_matrix.json")
out["hosts"] = {"tasks": len(hm["tasks"]), "tool_definitions": hm["tool_definitions"],
                "hosts": {h: {"model": v["model"], "prompt": v["prompt"], "pass_at_1": v["pass_at_1"], "passed": v["passed"],
                              "accepted": v["definitions_accepted"],
                              "fails": [{"id": r["id"], "reason": r["reason"], "calls": r.get("calls")} for r in v["results"] if not r["pass"]]}
                          for h, v in hm["hosts"].items()},
                "per_tool": hm["per_tool"], "all_hosts": hm["tools_passing_on_all_hosts"],
                "task_examples": [{k: t[k] for k in ("id", "user", "message")} for t in hm["tasks"][:30]]}
pg = J("production_grade.json")
out["prod"] = {"before_commit": pg["before_commit"], "after": pg["after"], "criteria": pg["criteria"], "summary": pg["summary"],
               "fix": pg["the_fix_for_the_lecture"]}
before = J("production_grade_before.json")["idempotency"]
after = J("production_grade_after.json")["idempotency"]
out["prod"]["idem"] = {"before": {k: before[k] for k in ("B_retry_with_rewritten_arguments", "duplicates_A_B", "duplicates_C")},
                       "after": {k: after[k] for k in ("B_retry_with_rewritten_arguments", "duplicates_A_B", "duplicates_C")},
                       "A_before": {k: v for k, v in before["A_lost_reply_then_retry"].items() if isinstance(v, dict) and v.get("duplicates")},
                       "A_after": {k: v for k, v in after["A_lost_reply_then_retry"].items() if isinstance(v, dict) and k in
                                   [n for n, w in before["A_lost_reply_then_retry"].items() if isinstance(w, dict) and w.get("duplicates")]}}


# ---------------------------------------------------------------- the door (ToolSpec.check) and the idempotency key, verbatim
init = (TOOLBOX / "__init__.py").read_text().split("\n")
a0 = next(i for i, l in enumerate(init) if l.strip().startswith("def check("))
a1 = next(i for i in range(a0 + 1, len(init)) if init[i].strip().startswith("def card("))
out["door_src"] = "\n".join(init[a0:a1]).rstrip()
tools_py = (ROOT / "ledgerline" / "ledgerline" / "agent" / "tools.py").read_text().split("\n")
k0 = next(i for i, l in enumerate(tools_py) if l.startswith("def content_key("))
out["content_key_src"] = "\n".join(tools_py[k0:k0 + 4]).rstrip()

# the Claude Code runs, packaged for NB4 (Colab has no experiment logs)
pkg = ROOT / "ledgerline" / "ledgerline" / "course" / "l4" / "claude_code_runs.json"
pkg.write_text(json.dumps({k: {"model": v["model"], "claude_code": v["claude_code"], "turns": [
    {"user": t["user"], "num_turns": t["num_turns"], "reply": t["reply"], "cost_usd_cumulative": t["cost_usd_cumulative"],
     "usage": {u: t["usage"][u] for u in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")},
     "steps": [s for s in t["steps"] if s["kind"] != "thinking"]} for t in v["turns"]],
    "source": "lectures/L4-the-hands/experiments/logs/claude_harness_" + k + ".json"} for k, v in out["claude"].items() if k in ("single", "order_hands")},
    indent=1, ensure_ascii=False))

# NB4's own replay (tools/modal_run.py --mode replay writes the executed notebook back)
nb = json.loads((HERE / "NB4_the_hands.ipynb").read_text())
code = [c for c in nb["cells"] if c["cell_type"] == "code"]
out["nb4"] = {"cells": len(code), "executed": sum(1 for c in code if c.get("execution_count")),
              "errors": sum(1 for c in code for o in c.get("outputs", []) if o.get("output_type") == "error")}

js = "/* generated by gen_figdata.py from experiments/logs; do not edit */\nwindow.L4 = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
(HERE / "figdata.js").write_text(js)
print(f"figdata.js {len(js) // 1024} KB")
for k in ("single", "order", "order_hands"):
    o = ours[k]
    print(k, "blocks", len(o["blocks"]), "prompt_tokens", [s["prompt_tokens"] for s in o["steps"]], "sums", o["sums_check"])
print("claude", {k: [len([s for s in t["steps"] if s["kind"] == "call"]) for t in out["claude"][k]["turns"]] for k in ("single", "order_hands")})
