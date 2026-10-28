"""Write figdata.js (window.L9) from experiments/logs/*.json. Standard library only; safe on the laptop.

    python3 lectures/L9-protocols/gen_figdata.py
Every number on a plate that comes from a figure is read here from a log; the log name is kept with it.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "experiments" / "logs"
J = lambda n: json.loads((LOGS / n).read_text())  # noqa: E731


def cut(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + "…"


def rpc(e):
    r = e["req"]
    if isinstance(r, dict):
        if "method" in r:
            name = (r.get("params") or {}).get("name") or (r.get("params") or {}).get("uri")
            return r["method"] + (f" · {name}" if name else "")
        if "result" in r:
            return "(the client's answer to elicitation/create)"
    return {"GET": "GET: open the server's event stream", "DELETE": "DELETE: end the session"}.get(e["method"], e["method"])


out = {}

# ---------------------------------------------------------------- MCP on the wire (mcp_sdk_wire.json)
w = J("mcp_sdk_wire.json")
out["versions"] = w["versions"]
for lab in ("http_modern", "http_legacy"):
    out[lab] = [{"rpc": rpc(e), "http": e["method"], "status": e["status"], "ms": e["ms"], "req_bytes": e["req_bytes"],
                 "resp_bytes": e["resp_bytes"], "session": (e["resp_headers"].get("mcp-session-id") or e["req_headers"].get("mcp-session-id") or "")[:8],
                 "mcp_method": e["req_headers"].get("mcp-method"), "mcp_name": e["req_headers"].get("mcp-name")}
                for e in w[lab]["wire"]]
mod = w["http_modern"]["wire"]
calls = [e for e in mod if isinstance(e["req"], dict) and e["req"].get("method") == "tools/call"]
first, retry = calls[1], calls[2]
rs = first["resp"]["result"]["requestState"]
out["mrtr"] = {
    "call": first["req"], "headers": first["req_headers"],
    "input_required": {**first["resp"], "result": {**first["resp"]["result"], "requestState": rs[:28] + "…" + rs[-10:]}},
    "retry": {**retry["req"], "params": {**retry["req"]["params"], "requestState": rs[:28] + "…" + rs[-10:]}},
    "result": json.loads(retry["resp"]["result"]["content"][0]["text"]),
    "ms": [first["ms"], retry["ms"]], "bytes": [first["req_bytes"], first["resp_bytes"], retry["req_bytes"], retry["resp_bytes"]],
}
legacy = w["http_legacy"]["wire"]
out["legacy_init"] = {"req": legacy[0]["req"], "resp": legacy[0]["resp"], "session": legacy[0]["resp_headers"].get("mcp-session-id")}
out["discover"] = {"req": mod[0]["req"], "resp": mod[0]["resp"], "headers": mod[0]["req_headers"]}
steps = {s["step"]: s for s in w["inproc_accept"]["steps"]}
out["resources"] = steps["resources/list"]["out"]
out["templates"] = steps["resources/templates/list"]["out"]
out["policy"] = steps["resources/read policy"]["out"]
stock = steps["resources/read stock"]["out"]
out["stock"] = {"item_code": stock["item_code"], "warehouses": [{k: x[k] for k in ("warehouse", "on_hand", "free")} for x in stock["warehouses"]],
                "cover_days": stock["cover_days"], "reorder_level": stock["reorder_level"]}
out["prompts"] = steps["prompts/list"]["out"]
out["prompt_get"] = steps["prompts/get raise_a_pr"]["out"]
out["tools_list"] = {"n": steps["tools/list"]["out"]["n"], "read_only": steps["tools/list"]["out"]["read_only"],
                     "ttl_ms": steps["tools/list"]["out"]["ttl_ms"], "first": steps["tools/list"]["out"]["first"]}
out["elicit_seen"] = w["inproc_accept"]["elicitations_seen_by_client"][0]
out["decline"] = {"reply": json.loads(w["inproc_decline"]["steps"][-1]["out"]["content"][0]["text"]),
                  "prs_after": w["inproc_decline"]["prs_after"]}
out["accept_prs"] = w["inproc_accept"]["prs_after"]
out["tamper"] = {"quantity_sent": w["tamper"]["sent"]["params"]["arguments"]["quantity"],
                 "reply": json.loads(w["tamper"]["reply"]["result"]["content"][0]["text"]),
                 "mac_reply": json.loads(w["tamper_mac"]["reply"]["result"]["content"][0]["text"])}
out["inproc_ms"] = [(s["step"], s["ms"]) for s in w["inproc_accept"]["steps"]]

# ---------------------------------------------------------------- authorization (auth_flow.json, auth_demos.json)
a = J("auth_flow.json")
out["auth_seq"] = a["sequence"]
out["auth_prm"] = a["protected_resource_metadata"]
out["auth_asm"] = {k: a["authorization_server_metadata"].get(k) for k in
                   ("issuer", "authorization_endpoint", "token_endpoint", "registration_endpoint",
                    "code_challenge_methods_supported", "scopes_supported")}
d = J("auth_demos.json")
out["auth_demos"] = {
    "kavita_approve": d["a_whose_session"]["kavita_approves_own"], "rohit_approve": d["a_whose_session"]["rohit_approves"],
    "svc": d["b_confused_deputy"]["service_account"][0], "deputy": d["b_confused_deputy"]["deputy_approves"],
    "right": d["b_confused_deputy"]["fix_right_server_refuses"], "audit": d["b_confused_deputy"]["audit"],
    "before": d["b_confused_deputy"]["status_before_deputy"], "after": d["b_confused_deputy"]["status_after_deputy"],
    "deputy_saw": d["b_confused_deputy"]["deputy_saw"][1],
    "read_only": d["c_scopes_audience"]["read_only_token"], "read_only_write": d["c_scopes_audience"]["read_only_write_call"],
    "prs_after_read_only": d["c_scopes_audience"]["prs_after_read_only"], "read_write": d["c_scopes_audience"]["read_write_token"],
    "audience": {k: v for k, v in d["c_scopes_audience"]["audience"].items() if k != "token_audiences"},
}

# ---------------------------------------------------------------- GitHub MCP server (github_mcp.json)
g = J("github_mcp.json")
out["github"] = {"headline": g["headline"], "version": g["version"],
                 "by_toolset": {k: {"n": v["n"], "read_only": v["read_only"]} for k, v in g["by_toolset"].items()}}

# ---------------------------------------------------------------- security (security_trials.json)
s = J("security_trials.json")
out["sec_summary"] = [{k: r.get(k) for k in ("model", "attack", "version", "defence", "n", "attempted", "succeeded",
                                             "utility_ok", "held_by_gate", "runs_with_quarantine", "flags_certificate")}
                      for r in s["summary"]]
out["sec_total_usd"], out["sec_total_inr"] = s["total_usd"], s["total_inr"]
out["sec_poisoned"] = s["poisoned_description"]
out["sec_clean"] = s["clean_description"]
out["sec_quote_v2"] = s["injected_quote_v2"]
out["sec_d1"] = s["d1_rule"]
out["sec_spot"] = s["spotlight"]
out["sec_sha"] = {"reviewed": s["reviewed_sha256"], "poisoned": s["poisoned_sha256"]}


def ex(e):
    return {"model": e["model"], "defence": e["defence"], "user": e["user"], "answer": cut(e.get("answer") or "", 420),
            "calls": [{"name": c["name"], "args": cut(c.get("args"), 150), "result": cut(c.get("result") or "", 120)} for c in e["calls"]],
            "held": e.get("held", []), "quarantined": e.get("quarantined", []), "succeeded": e.get("succeeded")}


E = s["examples"]
out["sec_examples"] = {"A_D0": ex(E["Av1"]["D0_succeeded"]), "A_D2": ex(E["Av1"]["D2_blocked"]),
                       "B_D0": ex(E["Bv2"]["D0_succeeded"]), "B_D2": ex(E["Bv2"]["D2_blocked"])}

# ---------------------------------------------------------------- A2A (a2a_negotiation.json, a2a_agent_card.json)
n = J("a2a_negotiation.json")
out["a2a_seq"] = [{"from": e["from"], "to": e["to"], "kind": e["kind"], "summary": e["summary"], "t": e.get("t_ms"),
                   "payload": cut(e.get("payload"), 700)} for e in n["sequence"]]
out["a2a_turns"] = [{k: t.get(k) for k in ("turn", "kavita", "ask_rasoi", "streaming", "wall_seconds", "http_requests",
                                           "a2a_requests", "a2a_messages_to_deccan", "a2a_events_from_deccan", "task_states",
                                           "a2a_seconds", "llm_ask_rasoi", "llm_deccan")} for t in n["turns"]]
out["a2a_totals"] = n["totals"]
out["a2a_card"] = J("a2a_agent_card.json")
out["a2a_bahi"] = n.get("bahi")
out["a2a_versions"] = n.get("versions")

# ---------------------------------------------------------------- n8n (n8n_run.json)
r = J("n8n_run.json")
out["n8n"] = {"versions": r["versions"], "boot": r["n8n_boot_seconds"], "final": r["final_status"],
              "trigger_to_finish": r["trigger_to_finish_seconds"], "wall": r["total_wall_seconds"],
              "requests": r["toolbox_request_count"], "tools_called": r["tools_called"],
              "rohit_ms": round(r["rohit_approval_seconds"] * 1000), "resume": r["resume"]["url"].split("?")[0] + "?signature=…",
              "nodes": [{"node": x["node"], "status": x["status"], "ms": x["executionTime_ms"]} for x in r["nodes_run"]],
              "rpc_per_call": [q.get("rpc") or q["method"] for q in r["toolbox_requests"][:6]],
              "bahi_final": {k: {kk: v.get(kk) for kk in ("request_no", "po_no", "status", "gross_value", "on_order_total")}
                             for k, v in r["bahi_final"].items() if isinstance(v, dict)}}

# ---------------------------------------------------------------- host config files (experiments/hosts/)
out["hosts"] = {f.stem: f.read_text() for f in sorted((HERE / "experiments" / "hosts").glob("*.json"))}

# ---------------------------------------------------------------- market evidence
out["market"] = J("market_sources.json")["claims"]

(HERE / "figdata.js").write_text("/* generated by gen_figdata.py from experiments/logs/*.json; do not edit by hand */\nwindow.L9 = "
                                 + json.dumps(out, ensure_ascii=False, default=str) + ";\n")
print("figdata.js", len(json.dumps(out, default=str)) // 1024, "KB")
