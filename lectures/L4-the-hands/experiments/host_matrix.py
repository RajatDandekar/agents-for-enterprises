"""Lecture 4, section 10: host compliance and LLM usability. 30 golden tool-use tasks on five hosts, pass@1.

    python lectures/L4-the-hands/experiments/host_matrix.py              (light: HTTP to OpenRouter + local Claude Code)
    LEDGER_LLM_MODE=replay python .../host_matrix.py --skip-claude-code  (replays the model hosts from the cassettes)

Every host gets the same 16 tool definitions, discovered from our MCP server (tools/list), and the same task text.
  our harness      Ask Northbridge's system prompt (harness._system, stage agent) + gemini-3.8-flash via OpenRouter
  Gemini           a generic host prompt + the server's instructions, google/gemini-3.8-flash via OpenRouter function calling
  OpenAI           the same generic prompt, openai/gpt-6.1-terra via OpenRouter function calling
  Claude (API)     the same generic prompt, anthropic/claude-sonnet-5.5 via OpenRouter function calling (the model only)
  Claude Code      the real Claude Code CLI, headless, on our stdio MCP server (its own system prompt), with
                   anthropic/claude-sonnet-5.5 through OpenRouter's Anthropic-compatible endpoint
Scoring: the first model response (Claude Code: its first tool call) must contain a call of an accepted tool whose
arguments match the task's checks; a call that commits (confirm=true) when the task asked for a preview fails it.
Model hosts run at temperature 0, one sample (pass@1). Writes logs/host_matrix.json.
"""
import concurrent.futures as cf
import json
import os
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))
os.environ.setdefault("LEDGER_ENV_FILE", str(ROOT / ".env"))

from ledgerline.erp.engine import ERP  # noqa: E402
from ledgerline.experience.harness import _system  # noqa: E402
from ledgerline.llm import LLM  # noqa: E402
from ledgerline.mcp_server import MCPClient, MCPClientTools  # noqa: E402
from ledgerline.toolbox import ALL, REGISTRY  # noqa: E402
from ledgerline.toolbox.mcp import build_toolbox_server  # noqa: E402

GENERIC = "You are a helpful assistant. You can use the tools from the connected servers to help the user."
INSTR = "Server instructions (northbridge): Northbridge Cycles' Ledgerline ERP, as {user}. One tool per business activity."
E, D, A = "ECLARKE", "DOKAFOR", "ATANAKA"
# (id, user, message, accepted: [(tool, {arg: check})]); checks: "=v" equal (case-insensitive), "~re" regex,
# "!true" must not be true, "absent" must be missing or empty
T = [
    ("stock_bat500", E, "How many BAT-500 battery packs do we have?", [("check_stock", {"item_code": "=BAT-500"})]),
    ("stock_motor", E, "What's the stock of item MTR-HUB-250 across our warehouses?", [("check_stock", {"item_code": "=MTR-HUB-250"})]),
    ("stock_charger", E, "Do we have enough CHG-4A-01 chargers? Check the stock.", [("check_stock", {"item_code": "=CHG-4A-01"})]),
    ("item_750", E, "Find the item code for the 48 V 750 Wh battery pack.", [("find_item", {"query": "~750"})]),
    ("item_brake", E, "Look up the item code for disc brake pads.", [("find_item", {"query": "~(?i)brake"})]),
    ("item_carton", E, "What is the item code for the bike shipping carton?", [("find_item", {"query": "~(?i)carton|box|shipping"})]),
    ("sup_voltway", E, "Find the supplier Voltway Cells.", [("find_supplier", {"name": "~(?i)voltway"})]),
    ("sup_pennine", E, "Is Pennine Brakes in our supplier master?", [("find_supplier", {"name": "~(?i)pennine"})]),
    ("sup_castlefield", E, "Look up Castlefield Chargers in Salford.", [("find_supplier", {"name": "~(?i)castlefield"})]),
    ("cc_prd05", E, "Is cost centre PRD-05 open?", [("check_budget", {"cost_centre": "=PRD-05"})]),
    ("cc_prd07", E, "How much budget is left on PRD-07?", [("check_budget", {"cost_centre": "=PRD-07"})]),
    ("cc_list", E, "Which cost centres are open?", [("check_budget", {"cost_centre": "absent"})]),
    ("pol_lithium", E, "What does the purchase policy say about suppliers of lithium battery packs?",
     [("search_policy", {"question": "~(?i)lithium|battery|UN ?38"})]),
    ("pol_approval", E, "Who has to approve a purchase above £250,000? Check the policy.",
     [("search_policy", {"question": "~(?i)approv"})]),
    ("cert_nordic", E, "Does Nordic Cell Co. (NC-GDA-0063) hold a valid UN 38.3 certificate?",
     [("supplier_certificates", {"supplier_code": "=NC-GDA-0063"}), ("find_supplier", {"name": "~(?i)nordic"})]),
    ("cert_voltway", E, "When does the UN 38.3 certificate of Voltway Cells (VC-EIN-0042) expire?",
     [("supplier_certificates", {"supplier_code": "=VC-EIN-0042"})]),
    ("cert_albion_item", E, "Can we buy BAT-500 from supplier AM-BIR-0008 under the battery-safety rule?",
     [("supplier_certificates", {"supplier_code": "=AM-BIR-0008", "item_code": "=BAT-500"})]),
    ("pr_preview", E, "Raise a purchase request for 2,000 BAT-500 on cost centre PRD-07, needed by 2026-11-09. Show me a preview first.",
     [("create_purchase_request", {"item_code": "=BAT-500", "quantity": "=2000", "cost_centre": "=PRD-07",
                                   "need_by": "=2026-11-09", "confirm": "!true"})]),
    ("po_direct_preview", E, "Preview a direct order of 100 BAT-375 from VC-EIN-0042 for PRD-07, needed by 2026-11-16.",
     [("create_purchase_order", {"supplier_code": "=VC-EIN-0042", "item_code": "=BAT-375", "quantity": "=100",
                                 "cost_centre": "=PRD-07", "need_by": "=2026-11-16", "confirm": "!true"})]),
    ("po_from_pr", E, "Create the purchase order with Voltway Cells (VC-EIN-0042) for the approved request PR/2026/04417. Preview it first.",
     [("create_purchase_order", {"supplier_code": "=VC-EIN-0042", "request_no": "=PR/2026/04417", "confirm": "!true"})]),
    ("status_po", E, "What's the status of PO/2026/01179?", [("order_status", {"po_no": "=PO/2026/01179"})]),
    ("status_pr", E, "Where is purchase request PR/2026/04417?", [("order_status", {"request_no": "=PR/2026/04417"})]),
    ("release", E, "Release purchase order PO/2026/01182 to the supplier.", [("release_purchase_order", {"po_no": "=PO/2026/01182"})]),
    ("inbox", D, "What is waiting for my approval?", [("list_my_approvals", {})]),
    ("approve_pr", D, "Approve purchase request PR/2026/04417.",
     [("approve_purchase_request", {"request_no": "=PR/2026/04417", "decision": "=approve"})]),
    ("reject_pr", D, "Reject PR/2026/04417: the quantity is wrong.",
     [("approve_purchase_request", {"request_no": "=PR/2026/04417", "decision": "=reject"})]),
    ("approve_po", D, "Approve purchase order PO/2026/01179.", [("approve_purchase_order", {"po_no": "=PO/2026/01179"})]),
    ("grn_preview", A, "Record a goods receipt of 1,200 packs against PO/2026/01182. Preview it first.",
     [("receive_goods", {"po_no": "=PO/2026/01182", "quantity": "=1200", "confirm": "!true"})]),
    ("register", E, "Register a new supplier: Brightcell Energy, Lyon, FR, VAT number FR12345678901. Preview only.",
     [("register_supplier", {"name": "~(?i)brightcell", "city": "~(?i)lyon", "state": "=FR", "confirm": "!true"}),
      ("find_supplier", {"name": "~(?i)brightcell"})]),
    ("message", E, "Send @daniel a message: PR/2026/04417 is waiting for your approval.",
     [("send_message", {"to": "~(?i)^@?daniel", "text": "~04417"})]),
]
assert len(T) == 30


def check(v, rule):
    if rule == "absent":
        return v in (None, "", {})
    if rule == "!true":
        return v not in (True, "true", "True")
    if v is None:
        return False
    if rule.startswith("="):
        want = rule[1:]
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return str(int(v)) == want if float(v).is_integer() else str(v) == want
        return str(v).strip().upper().replace(",", "") == want.upper().replace(",", "")
    if rule.startswith("~"):
        return re.search(rule[1:], str(v)) is not None
    return False


def score(calls, accepted):
    """calls: [(name, args)] of the first response. Returns (pass, reason)."""
    if not calls:
        return False, "no tool call (answered or asked instead)"
    preview_task = any(r == "!true" for _, rules in accepted for r in rules.values())
    reasons = []
    for name, args in calls:
        rules_for = [rules for tool, rules in accepted if tool == name]
        if not rules_for:
            reasons.append(f"wrong tool {name}")
            continue
        for rules in rules_for:
            bad = [k for k, r in rules.items() if not check((args or {}).get(k), r)]
            if not bad:
                if preview_task and any((a or {}).get("confirm") in (True, "true") for _, a in calls):
                    return False, "committed with confirm=true when a preview was asked for"
                return True, "ok"
            reasons.append(f"{name}: wrong {', '.join(bad)} ({json.dumps({k: (args or {}).get(k) for k in bad})})")
    return False, "; ".join(reasons)


# the tool definitions, as our MCP server lists them (16), cleaned the way MCPClientTools cleans them
c = MCPClient(build_toolbox_server(ERP(), "ECLARKE", names=ALL))
TOOLS = MCPClientTools(c).schemas()
c.close()
MODEL_HOSTS = {
    "our harness": ("openrouter:google/gemini-3.8-flash", "ours", 4096),
    "Gemini": ("openrouter:google/gemini-3.8-flash", "generic", 4096),
    "OpenAI": ("openrouter:openai/gpt-6.1-terra", "generic", 4096),
    "Claude (API)": ("openrouter:anthropic/claude-sonnet-5.5", "generic", 4096),
}
out = {"tasks": [{"id": t[0], "user": t[1], "message": t[2], "accepted": t[3]} for t in T], "hosts": {},
       "tool_definitions": len(TOOLS)}


def run_model(host, task):
    model, prompt, mt = MODEL_HOSTS[host]
    tid, user, msg, acc = task
    system = _system("agent", user) if prompt == "ours" else GENERIC + "\n\n" + INSTR.format(user=user)
    llm = LLM(model, cassette=f"L4v4_matrix_{host.split()[0].lower().strip('()')}", max_tokens=mt)
    try:
        r = llm.chat([{"role": "system", "content": system}, {"role": "user", "content": msg}], tools=TOOLS)
    except Exception as e:  # noqa: BLE001
        return {"id": tid, "pass": False, "reason": f"error: {str(e)[:200]}", "calls": [], "error": True}
    calls = [(t.name, t.arguments) for t in r.tool_calls]
    ok, why = score(calls, acc)
    return {"id": tid, "pass": ok, "reason": why, "calls": [{"name": n, "arguments": a} for n, a in calls],
            "text": (r.content or "")[:300], "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "replayed": r.replayed,
            "model": r.model}


skip_cc = "--skip-claude-code" in sys.argv
only = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--host=")]
for host in MODEL_HOSTS:
    if only and host not in only:
        continue
    t0 = time.time()
    with cf.ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda t: run_model(host, t), T))
    out["hosts"][host] = {"model": MODEL_HOSTS[host][0], "prompt": MODEL_HOSTS[host][1], "results": res,
                          "pass_at_1": round(sum(r["pass"] for r in res) / len(res), 3), "passed": sum(r["pass"] for r in res),
                          "definitions_accepted": not any(r.get("error") for r in res), "seconds": round(time.time() - t0, 1),
                          "tokens_in": sum(r.get("tokens_in", 0) for r in res), "tokens_out": sum(r.get("tokens_out", 0) for r in res)}
    print(f"{host:14} pass@1 {out['hosts'][host]['passed']}/30   fails: " +
          "; ".join(f"{r['id']}: {r['reason'][:70]}" for r in res if not r["pass"]))

# ----------------------------------------------------------------------------- Claude Code, headless, per task
CLAUDE = "/Users/raj/.local/bin/claude"
CC_DIR = HERE / "logs" / "claude_matrix"
CWD = pathlib.Path(os.environ.get("L4_CLAUDE_CWD", str(HERE / "logs" / "claude_matrix" / "cwd")))


def run_claude_code(task):
    tid, user, msg, acc = task
    CC_DIR.mkdir(parents=True, exist_ok=True)
    CWD.mkdir(parents=True, exist_ok=True)
    ev_path = CC_DIR / f"{tid}.events.jsonl"
    if ev_path.exists() and os.environ.get("L4_CC_REUSE", "1") == "1":  # already recorded: score the recording
        events = [json.loads(l) for l in ev_path.read_text().splitlines() if l.strip()]
    else:
        cfg = {"mcpServers": {"northbridge": {"type": "stdio", "command": sys.executable,
                                              "args": ["-m", "ledgerline.toolbox.mcp", "--user", user, "--all"],
                                              "env": {"PYTHONPATH": str(ROOT / "ledgerline"), "FASTMCP_LOG_LEVEL": "ERROR"}}}}
        cfg_path = CC_DIR / f"{tid}.mcp.json"
        cfg_path.write_text(json.dumps(cfg))
        key = next((l.split("=", 1)[1].strip().strip('"').strip("'") for l in (ROOT / ".env").read_text().splitlines()
                    if l.startswith("OPENROUTER_API_KEY=")), "")
        env = {**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
               "ANTHROPIC_BASE_URL": "https://openrouter.ai/api", "ANTHROPIC_AUTH_TOKEN": key, "ANTHROPIC_API_KEY": "",
               "ANTHROPIC_DEFAULT_HAIKU_MODEL": "anthropic/claude-sonnet-5.5"}
        allowed = ",".join(f"mcp__northbridge__{n}" for n in ALL)
        cmd = [CLAUDE, "-p", msg, "--output-format", "stream-json", "--verbose", "--mcp-config", str(cfg_path),
               "--strict-mcp-config", "--tools", "", "--allowedTools", allowed, "--no-session-persistence",
               "--setting-sources", "project", "--disable-slash-commands", "--model", "anthropic/claude-sonnet-5.5",
               "--max-budget-usd", "0.25"]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(CWD), env=env, timeout=300)
        events = []
        for line in p.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        ev_path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    first = []
    for ev in events:
        if ev.get("type") == "assistant":
            uses = [b for b in ev["message"].get("content", []) if b.get("type") == "tool_use"]
            if uses:
                first = [(b["name"].replace("mcp__northbridge__", ""), b.get("input")) for b in uses]
                break
    res = next((e for e in events if e.get("type") == "result"), {})
    ok, why = score(first, acc)
    return {"id": tid, "pass": ok, "reason": why, "calls": [{"name": n, "arguments": a} for n, a in first],
            "cost_usd_reported": res.get("total_cost_usd"), "num_turns": res.get("num_turns"),
            "result_text": (res.get("result") or "")[:300], "is_error": res.get("is_error")}


if not skip_cc and (not only or "Claude Code" in only):
    t0 = time.time()
    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(run_claude_code, T))
    out["hosts"]["Claude Code"] = {"model": "anthropic/claude-sonnet-5.5 (OpenRouter, Anthropic-compatible endpoint)",
                                   "prompt": "Claude Code's own", "results": res,
                                   "pass_at_1": round(sum(r["pass"] for r in res) / len(res), 3), "passed": sum(r["pass"] for r in res),
                                   "definitions_accepted": all(not r.get("is_error") for r in res),
                                   "cost_usd_reported": round(sum(r.get("cost_usd_reported") or 0 for r in res), 4),
                                   "seconds": round(time.time() - t0, 1)}
    print(f"{'Claude Code':14} pass@1 {out['hosts']['Claude Code']['passed']}/30   fails: " +
          "; ".join(f"{r['id']}: {r['reason'][:70]}" for r in res if not r["pass"]))
else:
    out["hosts"]["Claude Code"] = {"not_run": "skipped on this run (--skip-claude-code); see logs/claude_matrix/ for a recording"}

prev = HERE / "logs" / "host_matrix.json"
if prev.exists() and only:  # a partial re-run: keep the other hosts
    old = json.loads(prev.read_text())
    old["hosts"].update(out["hosts"])
    out["hosts"] = old["hosts"]
# per tool: did every host get every task of that tool right?
per_tool = {}
for i, t in enumerate(T):
    tool = t[3][0][0]
    for host, h in out["hosts"].items():
        if "results" not in h:
            continue
        per_tool.setdefault(tool, {}).setdefault(host, []).append(h["results"][i]["pass"])
out["per_tool"] = {tool: {host: f"{sum(v)}/{len(v)}" for host, v in hs.items()} for tool, hs in per_tool.items()}
out["tools_passing_on_all_hosts"] = sum(1 for hs in per_tool.values() if all(all(v) for v in hs.values()))
prev.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("tools right on every host:", out["tools_passing_on_all_hosts"], "/", len(per_tool))
