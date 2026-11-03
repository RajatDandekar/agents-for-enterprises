"""Lecture 4, sections 5 and 6: our MCP server on the wire, and its tool definitions against the MCP spec.

    python lectures/L4-the-hands/experiments/mcp_raw.py      (light, local: starts the stdio server as a child process)

1 one tool       `python -m ledgerline.toolbox.mcp --user ECLARKE --tools check_stock`, through stdio_tee.py:
                 initialize, notifications/initialized, tools/list, tools/call (ok), tools/call (a bad code: isError),
                 tools/call (a wrong type), tools/call (a tool that is not there), as raw JSON-RPC lines
2 all tools      the same server with --all: initialize, tools/list (16 tools), one call of supplier_certificates
3 before/after   tools/list and one result from the server as it was at commit 6e6f4d0 (a git worktree), and as now
4 alignment      field by field: MCP Tool (name, title, description, inputSchema, outputSchema, annotations ...)
                 and CallToolResult (content, structuredContent, isError) against what we send, before and after
Writes logs/mcp_raw.json (and the raw line logs in logs/wire/).
"""
import json
import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = sys.executable
WIRE = HERE / "logs" / "wire"
WIRE.mkdir(parents=True, exist_ok=True)
BEFORE_TREE = os.environ.get("L4_BEFORE_TREE", "")  # a checkout of commit 6e6f4d0, for the before column

import mcp.types as T  # noqa: E402

PROTO = T.LATEST_PROTOCOL_VERSION


def session(label, server_args, calls, pythonpath):
    """Run one stdio session through the tee; return the raw lines and the parsed messages."""
    log = WIRE / f"{label}.jsonl"
    log.unlink(missing_ok=True)
    env = {**os.environ, "PYTHONPATH": pythonpath, "FASTMCP_LOG_LEVEL": "ERROR"}
    p = subprocess.Popen([PY, str(HERE / "stdio_tee.py"), "--log", str(log), "--", PY, "-m", "ledgerline.toolbox.mcp",
                          *server_args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)

    def send(msg):
        p.stdin.write((json.dumps(msg) + "\n").encode())
        p.stdin.flush()

    def recv():
        while True:
            line = p.stdout.readline()
            if not line:
                return None
            m = json.loads(line)
            if "id" in m:  # skip server notifications (logs, list_changed)
                return m

    n = 0
    send({"jsonrpc": "2.0", "id": n, "method": "initialize",
          "params": {"protocolVersion": PROTO, "capabilities": {},
                     "clientInfo": {"name": "l4-raw-client", "version": "1.0"}}})
    init = recv()
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    n += 1
    send({"jsonrpc": "2.0", "id": n, "method": "tools/list", "params": {}})
    listed = recv()
    results = []
    for name, args in calls:
        n += 1
        send({"jsonrpc": "2.0", "id": n, "method": "tools/call", "params": {"name": name, "arguments": args}})
        results.append({"name": name, "arguments": args, "response": recv()})
    p.stdin.close()
    p.wait(timeout=30)
    lines = [json.loads(l) for l in log.read_text().splitlines()]
    return {"server_args": server_args, "initialize": init, "tools_list": listed, "calls": results,
            "raw_lines": lines, "raw_log": str(log.relative_to(ROOT))}


now_path = str(ROOT / "ledgerline")
CALLS_ONE = [("check_stock", {"item_code": "BAT-500"}),
             ("check_stock", {"item_code": "BAT-5000"}),
             ("check_stock", {"item_code": 500}),
             ("create_purchase_order", {"supplier_code": "VC-EIN-0042"})]
out = {"protocol_version_asked": PROTO, "sdk": {"mcp": __import__("importlib.metadata").metadata.version("mcp"),
                                                "fastmcp": __import__("importlib.metadata").metadata.version("fastmcp")}}
t0 = time.time()
out["one_tool"] = session("one_tool", ["--user", "ECLARKE", "--tools", "check_stock"], CALLS_ONE, now_path)
out["all_tools"] = session("all_tools", ["--user", "ECLARKE", "--all"],
                           [("supplier_certificates", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}),
                            ("check_stock", {"item_code": "BAT-500"})], now_path)
out["default_tools"] = session("default_tools", ["--user", "ECLARKE"], [], now_path)
if BEFORE_TREE:
    out["before"] = session("before_default", ["--user", "ECLARKE"],
                            [("check_stock", {"item_code": "BAT-500"}), ("check_stock", {"item_code": "BAT-5000"})],
                            str(pathlib.Path(BEFORE_TREE) / "ledgerline"))
print(f"sessions done in {time.time() - t0:.1f}s")

# ----------------------------------------------------------------------------- 4. field-by-field alignment
TOOL_FIELDS = {"name": "unique id the model calls", "title": "human-readable name for the UI",
               "description": "what the model reads to decide", "inputSchema": "JSON Schema of the arguments",
               "outputSchema": "JSON Schema of structuredContent", "annotations": "behaviour hints for the host",
               "icons": "icons for the UI", "execution": "task support (long-running calls)", "_meta": "extension data"}
ANN_FIELDS = ["title", "readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]
RESULT_FIELDS = {"content": "blocks the host shows the model (we send one text block: the JSON)",
                 "structuredContent": "the same result as an object, checked against outputSchema",
                 "isError": "true when the tool failed (our ok=false)"}
FROM_TOOL_JSON = {"name": "name", "title": "title", "description": "description", "inputSchema": "input_schema",
                  "outputSchema": "output_schema", "annotations": "annotations (+ title)", "_meta": "version, category, writes, services, policy",
                  "icons": None, "execution": None}
spec_fields = {f.alias or k for k, f in T.Tool.model_fields.items()}


def tool_defs(sess):
    return {t["name"]: t for t in (sess["tools_list"] or {}).get("result", {}).get("tools", [])}


def first_result(sess, ok=True):
    for c in sess["calls"]:
        r = c["response"].get("result", {})
        is_err = bool(r.get("isError"))
        if is_err != ok:
            return r
    return {}


now_defs = tool_defs(out["all_tools"])
before_defs = tool_defs(out["before"]) if BEFORE_TREE else {}
align = []
for f, what in TOOL_FIELDS.items():
    row = {"field": f, "in_spec_sdk": f in spec_fields or f == "_meta", "meaning": what, "from_tool_json": FROM_TOOL_JSON.get(f),
           "before_tools_with_it": sum(1 for d in before_defs.values() if f in d) if before_defs else None,
           "after_tools_with_it": sum(1 for d in now_defs.values() if f in d), "tools": len(now_defs)}
    align.append(row)
for a in ANN_FIELDS:
    align.append({"field": f"annotations.{a}", "in_spec_sdk": True, "meaning": "hint",
                  "before_tools_with_it": sum(1 for d in before_defs.values() if a in d.get("annotations", {})) if before_defs else None,
                  "after_tools_with_it": sum(1 for d in now_defs.values() if a in d.get("annotations", {})), "tools": len(now_defs)})
ok_now, err_now = first_result(out["one_tool"], True), first_result(out["one_tool"], False)
ok_before = first_result(out["before"], True) if BEFORE_TREE else {}
err_before_call = out["before"]["calls"][1]["response"]["result"] if BEFORE_TREE else {}
res_align = []
for f, what in RESULT_FIELDS.items():
    res_align.append({"field": f, "meaning": what,
                      "before_ok_result": ((ok_before.get(f, False) if f == "isError" else f in ok_before) if BEFORE_TREE else None),
                      "before_error_result": ((err_before_call.get(f, False) if f == "isError" else f in err_before_call) if BEFORE_TREE else None),
                      "after_ok_result": (ok_now.get(f, False) if f == "isError" else f in ok_now), "after_error_result": (err_now.get(f, False) if f == "isError" else f in err_now),
                      "reads": "isError: its value; other fields: present or not"})
out["alignment"] = {"protocol_version": out["one_tool"]["initialize"]["result"]["protocolVersion"], "tool_fields": align,
                    "result_fields": res_align,
                    "not_sent": {"icons": "no icons for these tools (optional)",
                                 "execution": "no long-running tasks (optional; every call returns within one request)"},
                    "backwards_compatible": "name, description and inputSchema are byte-identical to before, so every "
                                            "recorded run replays (logs/compat_check.json); the new fields are additions."}
# the changes, tool by tool, for the slide
if before_defs:
    out["diff_check_stock"] = {"before": before_defs.get("check_stock"), "after": now_defs.get("check_stock")}
    out["same_name_description_inputSchema"] = all(
        before_defs[n].get(k) == now_defs[n].get(k) for n in before_defs for k in ("name", "description", "inputSchema"))

(HERE / "logs" / "mcp_raw.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("protocol", out["alignment"]["protocol_version"], "| one tool:", len(tool_defs(out["one_tool"])),
      "| all:", len(now_defs), "| default:", len(tool_defs(out["default_tools"])))
for r in align:
    print(f"   {r['field']:28} before {r['before_tools_with_it']}  after {r['after_tools_with_it']}/{r['tools']}")
for r in res_align:
    print(f"   result.{r['field']:20} before ok={r['before_ok_result']} err={r['before_error_result']}  after ok={r['after_ok_result']} err={r['after_error_result']}")
print("unchanged name/description/inputSchema:", out.get("same_name_description_inputSchema"))
for c in out["one_tool"]["calls"]:
    print("  ", c["name"], json.dumps(c["arguments"]), "->", json.dumps(c["response"])[:200])
