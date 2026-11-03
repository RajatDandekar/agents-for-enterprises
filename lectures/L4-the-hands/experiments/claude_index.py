"""Lecture 4, sections 7 and 9: what happened on Claude's harness, and the two harnesses side by side.

    python lectures/L4-the-hands/experiments/claude_index.py

Reads the Claude Code recordings (logs/claude_harness_<label>.json, logs/claude_runs/, logs/wire/claude_*.jsonl) and
logs/our_harness.json; writes logs/claude_harness.json: the attempts (including the two that did not reach the model),
the runs, what Claude Code put on the wire, and the comparison table for the "orchestra" film.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
L = HERE / "logs"


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


runs = {k: load(L / f"claude_harness_{k}.json") for k in ("single", "order", "order_3turns")}
ours = load(L / "our_harness.json")
att1 = [json.loads(l) for l in (L / "claude_runs" / "single_attempt1_safe_mode.events.jsonl").read_text().splitlines()]
att2 = [json.loads(l) for l in (L / "claude_runs" / "single_attempt2_auth.events.jsonl").read_text().splitlines()]
wire2 = [json.loads(l) for l in (L / "wire" / "claude_single_attempt2_auth.jsonl").read_text().splitlines()]


def text_of(ev_list):
    for e in ev_list:
        if e.get("type") == "assistant":
            return " ".join(b.get("text", "") for b in e["message"]["content"] if b.get("type") == "text")


out = {"harness": "Claude Code 2.1.241, headless (claude -p, stream-json in and out), our stdio MCP server, no built-in tools",
       "attempts": [
           {"attempt": 1, "flags": "--safe-mode", "result": "not run: --safe-mode also turns MCP servers off (init listed no "
                                                           "servers and no tools); stopped before the model answered",
            "init_mcp_servers": next(e for e in att1 if e.get("subtype") == "init").get("mcp_servers"),
            "model_tokens": 0},
           {"attempt": 2, "flags": "--setting-sources project --disable-slash-commands, CLAUDE_CODE_DISABLE_CLAUDE_MDS=1",
            "result": "not run on the Claude plan: the CLI is not logged in (`claude auth status` -> loggedIn false); "
                      "Claude Code answered with its own error message",
            "message": text_of(att2), "model_tokens": 0,
            "but_the_mcp_handshake_ran": [{"dir": w["dir"], "message": json.loads(w["line"])} for w in wire2]},
           {"attempt": 3, "flags": "as attempt 2, plus ANTHROPIC_BASE_URL=https://openrouter.ai/api (the course's OpenRouter "
                                   "key, never printed) and --model anthropic/claude-sonnet-5.5",
            "result": "ran: the same Claude Code harness, its model calls billed through OpenRouter instead of the plan"}],
       "to_run_on_the_plan": "after `claude auth login`: python claude_harness.py single --setting-sources project "
                             "--disable-slash-commands (and order, order_3turns), without L4_CLAUDE_VIA_OPENROUTER",
       "runs": {}}
for k, r in runs.items():
    if not r:
        continue
    steps = r["steps"]
    results = [s for s in steps if s["kind"] == "tool_result"]
    out["runs"][k] = {"turns": r["turns"], "model": r["init"]["model"], "tools_exposed": len(r["tools_exposed"]),
                      "tool_sequence": r["summary"]["tool_sequence"], "tool_calls": r["summary"]["tool_calls"],
                      "tool_errors": r["summary"]["tool_errors"],
                      "claude_code_turns": [x["num_turns"] for x in r["results"]],
                      "cost_usd_reported": round(max([x.get("total_cost_usd") or 0 for x in r["results"]] or [0]), 4),
                      "seconds": r["seconds"],
                      "usage_per_user_turn": [x["usage"] for x in r["results"]],
                      "final_reply": r["results"][-1]["result"] if r["results"] else None,
                      "writes_committed": [c for c in r["server_calls"] if (c["arguments"] or {}).get("confirm") is True],
                      "what_the_model_got_back": [
                          {"tool_call": s.get("id"), "is_error": s.get("is_error"),
                           "looks_like": "content text block (our JSON text)" if s["content"].startswith('{"ok": ') else
                           ("structuredContent (compact JSON)" if s["content"].startswith('{"ok":') else "other")}
                          for s in results],
                      "steps": steps}
out["findings"] = [
    "Claude Code's MCP client: protocolVersion 2025-11-25, capabilities roots + elicitation; after initialize it asks "
    "tools/list, prompts/list and resources/list (logs/wire/claude_single_attempt2_auth.jsonl).",
    "For an ok result Claude Code gave the model structuredContent (compact JSON, no spaces); for an isError result it "
    "gave the text block. Either way only the tool's returned JSON reached the model.",
    "Claude knows nothing about Northbridge beyond the server's one-line instructions: on the order it looked up the "
    "supplier, item, stock, certificate and cost centres itself (8 calls) and asked which Voltway and which date; our "
    "harness's system prompt already names BAT-500, VC-EIN-0042 and PRD-07, so it made 4 calls.",
    "With the same two user turns, our harness submitted the request (PR/2026/04417, waiting for Daniel); Claude Code "
    "previewed it and asked again. With a third turn ('Yes, submit the purchase request.') it submitted the same request.",
    "Both harnesses tried a direct order first, got the £50,000 limit error from the tool, and recovered by raising a "
    "purchase request: the error contract's next_step did the steering.",
]
if ours:
    so, oo = ours["single"]["summary"], ours["order"]["summary"]
    cs, co, c3 = (out["runs"].get(k, {}) for k in ("single", "order", "order_3turns"))
    out["comparison"] = {
        "single": {"ours": {"sequence": so["sequence"], "model_calls": so["model_calls"], "tokens_in": so["tokens_in"],
                            "cost_gbp_est": so["cost_gbp_est"], "model": ours["single"]["model"]},
                   "claude_code": {"sequence": cs.get("tool_sequence"), "cost_usd_reported": cs.get("cost_usd_reported"),
                                   "model": cs.get("model")}},
        "order_two_turns": {"ours": {"sequence": oo["sequence"], "model_calls": oo["model_calls"], "tokens_in": oo["tokens_in"],
                                     "errors_recovered": oo["errors_recovered"], "cost_gbp_est": oo["cost_gbp_est"],
                                     "outcome": ours["order"]["ledgerline_after"]["pr"]},
                            "claude_code": {"sequence": co.get("tool_sequence"), "tool_errors": co.get("tool_errors"),
                                            "cost_usd_reported": co.get("cost_usd_reported"),
                                            "outcome": "previewed the request, asked to confirm again (nothing saved)"
                                            if not co.get("writes_committed") else co.get("writes_committed")}},
        "order_three_turns_claude_code": {"sequence": c3.get("tool_sequence"), "cost_usd_reported": c3.get("cost_usd_reported"),
                                          "outcome": [w["result"].get("request_no") + " " + w["result"].get("status")
                                                      for w in c3.get("writes_committed", []) if w["result"].get("ok")]},
        "in_our_control": ["model (gemini-3.8-flash) and route", "system prompt (who Emma is, the date, the codes, the rules)",
                           "which tools each person and stage sees", "the battery-safety guard before every write",
                           "loop limit (14 rounds), wrap-up, empty-reply nudge", "identity: the MCP server is bound to Emma's session",
                           "logging, tokens and cost per call (cassettes)"],
        "left_to_claude": ["Anthropic's system prompt and its orchestration", "the order and number of steps",
                           "how results are shown to the model (structuredContent vs text)",
                           "per-call approval (pre-approved here with --allowedTools, since headless has no one to click)"]}
(L / "claude_harness.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
for k, r in out["runs"].items():
    print(k, r["tool_sequence"], "cost", r["cost_usd_reported"], "| returned:", {x["looks_like"] for x in r["what_the_model_got_back"]})
print(json.dumps(out.get("comparison", {}).get("order_three_turns_claude_code"), indent=0))
