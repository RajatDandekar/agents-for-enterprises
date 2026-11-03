"""Lecture 4, sections 7 and 9: Claude's harness (Claude Code, headless) on our MCP server, the same two tasks.

    python lectures/L4-the-hands/experiments/claude_harness.py single     (runs Claude Code on Rajat's plan: few runs!)
    python lectures/L4-the-hands/experiments/claude_harness.py order

Claude Code is started as `claude -p` with stream-json in and out, so every step is recorded:
  --mcp-config         one stdio server: our toolbox (`python -m ledgerline.toolbox.mcp --user ECLARKE ...`), started
                       through stdio_tee.py so the raw JSON-RPC Claude Code sends and receives is logged too
  --strict-mcp-config  no other MCP server
  --tools ""           no built-in tools (no Bash, no files): only ours
  --allowedTools       our tools, pre-approved (headless has no one to click "allow")
  --setting-sources project, --disable-slash-commands, CLAUDE_CODE_DISABLE_CLAUDE_MDS=1, CLAUDE_CODE_DISABLE_AUTO_MEMORY=1:
                       none of this machine's CLAUDE.md, memory, user plugins, hooks or skills (an empty folder as cwd).
                       (--safe-mode would do that too, but it also turns MCP servers off: attempt 1, logged.)
The server holds its own fresh Northbridge sandbox, so writes land there and nowhere else.

  single  Emma: "How many BAT-500 battery packs do we have in Manchester main stores?"   tools: check_stock, find_item
  order   Emma: "Order 2,000 BAT-500 packs from Voltway for the spring launch run."     tools: all 16
          then "Yes, go ahead. We need them by 9 November 2026."  (the same second turn our harness gets)
Writes logs/claude_harness_<label>.json, logs/claude_runs/<label>.events.jsonl (every stream-json event),
logs/wire/claude_<label>.jsonl (raw JSON-RPC) and logs/claude_runs/<label>.calls.jsonl (each tool call with its
Ledgerline calls, from the server's --log).
"""
import json
import os
import pathlib
import subprocess
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CLAUDE = os.environ.get("CLAUDE_BIN", "/Users/raj/.local/bin/claude")
PY = os.environ.get("L4_SERVER_PY", sys.executable)  # a Python with fastmcp, for the server
RUNS = HERE / "logs" / "claude_runs"
WIRE = HERE / "logs" / "wire"
RUNS.mkdir(parents=True, exist_ok=True)
WIRE.mkdir(parents=True, exist_ok=True)
CWD = pathlib.Path(os.environ.get("L4_CLAUDE_CWD", "/tmp/l4-claude-cwd"))  # an empty folder: no project files or CLAUDE.md
CWD.mkdir(parents=True, exist_ok=True)

TASKS = {
    "single": {"tools": ["check_stock", "find_item"],
               "turns": ["How many BAT-500 battery packs do we have in Manchester main stores?"]},
    "order": {"tools": "all",
              "turns": ["Order 2,000 BAT-500 packs from Voltway for the spring launch run.",
                        "Yes, go ahead. We need them by 9 November 2026."]},
    # Lecture 4's "hands" prompt (l4_prompts.HANDS_L4, no Northbridge codes) appended to Claude Code's own system prompt,
    # and the same three turns our harness got on it (our_harness.py, run order_hands)
    "order_hands": {"tools": "all", "append_system": True,
                    "turns": ["I need 2,000 of the 36 V 500 Wh battery packs from Voltway for the spring launch run.",
                              "Yes, go ahead. We need them by 9 November 2026.",
                              "Yes, submit the purchase request."]},
    # the order again, with one more yes: in "order" Claude previewed the request and asked a second time (logged)
    "order_3turns": {"tools": "all",
                     "turns": ["Order 2,000 BAT-500 packs from Voltway for the spring launch run.",
                               "Yes, go ahead. We need them by 9 November 2026.",
                               "Yes, submit the purchase request."]},
}
ALL16 = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "create_purchase_request",
         "list_my_approvals", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
         "release_purchase_order", "order_status", "receive_goods", "register_supplier", "send_message", "supplier_certificates"]

label = sys.argv[1]
extra_flags = [a for a in sys.argv[2:]]
task = TASKS[label]
names = ALL16 if task["tools"] == "all" else task["tools"]
wire, calls_log, events_log = WIRE / f"claude_{label}.jsonl", RUNS / f"{label}.calls.jsonl", RUNS / f"{label}.events.jsonl"
for p in (wire, calls_log, events_log):
    p.unlink(missing_ok=True)
server = [PY, "-m", "ledgerline.toolbox.mcp", "--user", "ECLARKE", "--log", str(calls_log)] + \
    (["--all"] if task["tools"] == "all" else ["--tools", ",".join(names)])
cfg = {"mcpServers": {"northbridge": {"type": "stdio", "command": PY,
                                      "args": [str(HERE / "stdio_tee.py"), "--log", str(wire), "--", *server],
                                      "env": {"PYTHONPATH": str(ROOT / "ledgerline"), "FASTMCP_LOG_LEVEL": "ERROR"}}}}
cfg_path = RUNS / f"{label}.mcp.json"
cfg_path.write_text(json.dumps(cfg, indent=1))
allowed = ",".join(f"mcp__northbridge__{n}" for n in names)
cmd = [CLAUDE, "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
       "--mcp-config", str(cfg_path), "--strict-mcp-config", "--tools", "", "--allowedTools", allowed,
       "--no-session-persistence", *extra_flags]
if task.get("append_system"):
    sys.path[:0] = [str(ROOT / "ledgerline"), str(HERE)]
    from l4_prompts import hands_prompt
    cmd += ["--append-system-prompt", hands_prompt("ECLARKE")]
print("cmd:", " ".join(c if c else '""' for c in cmd))
t0 = time.time()
CLEAN_ENV = {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}  # no CLAUDE.md, no memory
ROUTE = {"via": "Claude plan (the CLI's own login)"}
run_env = {**os.environ, **CLEAN_ENV}
if os.environ.get("L4_CLAUDE_VIA_OPENROUTER"):
    # The CLI is not logged in to a Claude plan (attempt 2): the same Claude Code, with its model calls sent to
    # OpenRouter's Anthropic-compatible endpoint. The key is read from the course .env and never printed or logged.
    key = next((l.split("=", 1)[1].strip().strip('"').strip("'") for l in (ROOT / ".env").read_text().splitlines()
                if l.startswith("OPENROUTER_API_KEY=")), "")
    run_env.update({"ANTHROPIC_BASE_URL": "https://openrouter.ai/api", "ANTHROPIC_AUTH_TOKEN": key, "ANTHROPIC_API_KEY": ""})
    small = os.environ.get("L4_CLAUDE_SMALL_MODEL", "")
    if small:
        run_env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = small
    ROUTE = {"via": "OpenRouter's Anthropic-compatible endpoint (ANTHROPIC_BASE_URL=https://openrouter.ai/api)",
             "small_model": small or None}
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(CWD), text=True,
                     env=run_env)
events, stderr = [], []
threading.Thread(target=lambda: stderr.extend(p.stderr), daemon=True).start()


def send(text):
    msg = {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}}
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()


def read_until_result(deadline=600):
    """Read events until this turn's result event. Returns the result event, or None."""
    end = time.time() + deadline
    while time.time() < end:
        line = p.stdout.readline()
        if not line:
            return None
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        ev["_t"] = round(time.time() - t0, 3)
        events.append(ev)
        with events_log.open("a") as f:
            f.write(json.dumps(ev) + "\n")
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            servers = {s.get("name"): s.get("status") for s in ev.get("mcp_servers", [])}
            ours = [t for t in ev.get("tools", []) if t.startswith("mcp__northbridge__")]
            print("init: model", ev.get("model"), "| servers", servers, "| our tools", len(ours), "| all tools", len(ev.get("tools", [])))
            if servers.get("northbridge") != "connected" or not ours:
                print("our server is not connected: stopping before the model answers")
                p.kill()
                return {"aborted": True, "init": ev}
        if ev.get("type") == "result":
            return ev
    return None


results = []
for text in task["turns"]:
    send(text)
    r = read_until_result()
    results.append(r)
    if not r or r.get("aborted"):
        break
try:
    p.stdin.close()
    p.wait(timeout=60)
except Exception:  # noqa: BLE001
    p.kill()

# ----------------------------------------------------------------------------- the transcript, step by step
steps = []
for ev in events:
    if ev.get("type") == "assistant":
        for b in ev["message"].get("content", []):
            if b.get("type") == "tool_use":
                steps.append({"t": ev["_t"], "kind": "tool_call", "tool": b["name"].replace("mcp__northbridge__", ""),
                              "id": b["id"], "arguments": b.get("input")})
            elif b.get("type") == "text":
                steps.append({"t": ev["_t"], "kind": "assistant_text", "text": b["text"]})
            elif b.get("type") == "thinking":
                steps.append({"t": ev["_t"], "kind": "thinking", "chars": len(b.get("thinking") or "")})
    elif ev.get("type") == "user":
        content = ev["message"].get("content")
        for b in content if isinstance(content, list) else []:
            if b.get("type") == "tool_result":
                c = b.get("content")
                text = "".join(x.get("text", "") for x in c) if isinstance(c, list) else c
                steps.append({"t": ev["_t"], "kind": "tool_result", "id": b.get("tool_use_id"), "is_error": b.get("is_error"),
                              "content": text})
init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
calls = [json.loads(l) for l in calls_log.read_text().splitlines()] if calls_log.exists() else []
wire_lines = [json.loads(l) for l in wire.read_text().splitlines()] if wire.exists() else []
fin = [r for r in results if r and not r.get("aborted")]
out = {"label": label, "appended_system_prompt": "l4_prompts.HANDS_L4" if task.get("append_system") else None, "cmd": cmd, "env_added": CLEAN_ENV, "route": ROUTE, "cwd": str(CWD), "claude_version": subprocess.run([CLAUDE, "--version"], capture_output=True,
                                                                                    text=True).stdout.strip(),
       "turns": task["turns"], "tools_exposed": names,
       "init": {k: init.get(k) for k in ("model", "tools", "mcp_servers", "permissionMode", "apiKeySource", "cwd", "claude_code_version",
                                          "output_style", "slash_commands", "agents", "skills", "plugins")},
       "results": [{k: r.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "duration_api_ms", "total_cost_usd",
                                          "usage", "modelUsage", "result", "permission_denials")} for r in fin],
       "steps": steps, "server_calls": calls,
       "wire": {"lines": len(wire_lines), "file": str(wire.relative_to(ROOT)),
                "client_initialize": next((json.loads(w["line"]) for w in wire_lines if w["dir"] == ">" and '"initialize"' in w["line"]), None),
                "tools_list_request": next((json.loads(w["line"]) for w in wire_lines if w["dir"] == ">" and '"tools/list"' in w["line"]), None)},
       "stderr_tail": "".join(stderr)[-1500:], "seconds": round(time.time() - t0, 1),
       "completed": bool(fin) and len(fin) == len(task["turns"])}
out["summary"] = {"tool_sequence": [s["tool"] for s in steps if s["kind"] == "tool_call"],
                  "tool_calls": sum(1 for s in steps if s["kind"] == "tool_call"),
                  "tool_errors": sum(1 for s in steps if s["kind"] == "tool_result" and s.get("is_error")),
                  "total_cost_usd_reported": round(max([r.get("total_cost_usd") or 0 for r in fin] or [0]), 4),
                  "note": "total_cost_usd is Claude Code's own estimate for the session so far (it is cumulative, so the last "
                          "result's value is the run's total), at its list prices for the model."}
(HERE / "logs" / f"claude_harness_{label}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out["summary"], indent=1))
for s in steps:
    print(f"  {s['t']:7.1f}s {s['kind']:15} " + (f"{s['tool']} {json.dumps(s['arguments'])[:160]}" if s["kind"] == "tool_call"
                                                  else (s.get("text") or s.get("content") or str(s.get("chars", "")))[:220].replace("\n", " ")))
print("completed:", out["completed"], "| stderr:", out["stderr_tail"][-300:])
