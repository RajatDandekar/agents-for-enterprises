"""Lecture 4, sections 7–9: our harness (Ask Northbridge's loop) with the context captured at every model call.

    from ledgerline.course.l4.hands import hands_run, context_parts, show_context, CLAUDE_CODE
    run = hands_run("single")            # replays the recorded run (no key needed): Emma's stock question
    show_context(run)                    # every part of the context the model read, with its real token count

This is the same code as lectures/L4-the-hands/experiments/our_harness.py, packaged so NB4 can run it in Colab.
The harness is ledgerline.experience.harness.AskNorthbridge, stage "agent", as the live app runs it; only the model
client is swapped for a recording one (cassettes L4v4_ours and L4v4_ours_hands), so every call replays exactly.
Tokens per part are measured with the same model, from the provider's own prompt_tokens on prefix requests (the
measuring calls are recorded too: L4v4_ours_tokens, L4v4_ours_hands_tokens).
"""
from __future__ import annotations

import copy
import json
import os
import pathlib

MODEL = "openrouter:google/gemini-3.8-flash"
os.environ["NORTHBRIDGE_MODEL"] = MODEL
os.environ["NORTHBRIDGE_FALLBACKS"] = ""

from ...erp.engine import ERP  # noqa: E402
from ...erp.receipts import install_receipts  # noqa: E402
from ...experience import harness as H  # noqa: E402
from ...experience.players import guard_erp  # noqa: E402
from ...llm import LLM  # noqa: E402
from ...toolbox import ALL  # noqa: E402

H.CHAIN[:] = [MODEL]
HERE = pathlib.Path(__file__).parent

# Lecture 4's "hands" prompt: who, when and the rules, but no Northbridge codes (byte-identical to experiments/l4_prompts.py)
HANDS_L4 = """You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of e-bikes.
You work inside Northbridge's Ledgerline ERP for {name} ({user}), {role}, with {first}'s own Ledgerline permissions and nobody
else's. Today is Monday 26 October 2026.

How you work
- Every fact (item codes, stock, suppliers, rates, cost centres, budgets, approvals, statuses, rules) comes from a tool.
  Never guess a code or a number: look it up. For a question about a rule, call search_policy and cite the clause.
- Anything that saves a request, an order or a goods receipt: first call the tool with confirm=false and show the
  preview as a short list (item, quantity, supplier, value in pounds, cost centre, need-by date, who must approve).
  Ask {first} to confirm. Call it again with confirm=true only after a clear yes.
- Report the status the receipt gives you, in plain words. Never say an order is placed unless its status is RELEASED.
  A request waiting for approval is not an order: say who it waits for.
- If a tool returns ok=false, read next_step and follow it, or tell {first} plainly what to do.
- If {first} cannot do a step (approving, receiving goods), say who can.
- Short, plain replies: two to six lines, no tables. Money in pounds with commas. No emoji."""


def hands_prompt(user="ECLARKE"):
    name, role = H.PEOPLE.get(user, (user, ""))
    return HANDS_L4.format(name=name, role=role, user=user, first=name.split()[0])


TURN2 = "Yes, go ahead. We need them by 9 November 2026."
RUNS = {  # the recorded runs: (Emma's turns, tools, system prompt, cassette)
    "single": (["How many BAT-500 battery packs do we have in Manchester main stores?"], ["check_stock", "find_item"], None, "L4v4_ours"),
    "order": (["Order 2,000 BAT-500 packs from Voltway for the spring launch run.", TURN2], ALL, None, "L4v4_ours"),
    "order_hands": (["I need 2,000 of the 36 V 500 Wh battery packs from Voltway for the spring launch run.", TURN2,
                     "Yes, submit the purchase request."], ALL, "hands", "L4v4_ours_hands"),
}
TOKEN_CASSETTE = {"L4v4_ours": "L4v4_ours_tokens", "L4v4_ours_hands": "L4v4_ours_hands_tokens"}


class Recorded(H.AskNorthbridge):
    """AskNorthbridge with a recording model client and a copy of the context at every model call."""

    def __init__(self, *a, system=None, cassette="L4v4_ours", **kw):
        super().__init__(*a, **kw)
        self.steps = []
        self.cassette = cassette
        if system:
            self.messages[0]["content"] = system

    def _llm(self, model):
        if model not in self.llms:
            self.llms[model] = LLM(model, cassette=self.cassette, mode=os.environ.get("LEDGER_LLM_MODE", "auto"),
                                   max_tokens=H.MAX_TOKENS)
        return self.llms[model]

    def _chat(self, tools, extra=None, **kw):
        msgs = copy.deepcopy(self.messages + (extra or []))
        r = super()._chat(tools, extra, **kw)
        self.steps.append({"call": len(self.steps), "messages": msgs, "tools": tools,
                           "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments} for t in r.tool_calls],
                           "content": r.content, "prompt_tokens": r.tokens_in, "completion_tokens": r.tokens_out,
                           "replayed": r.replayed})
        return r


def hands_run(label: str = "single") -> dict:
    """Run one recorded task on our harness (replayed when there is no key). Returns turns, steps and the cassette."""
    turns_in, names, system, cassette = RUNS[label]
    erp = ERP()
    install_receipts(erp)
    guard_erp(erp)
    a = Recorded(erp, "ECLARKE", "agent", names=names, system=hands_prompt() if system == "hands" else None, cassette=cassette)
    turns = []
    for text in turns_in:
        out = a.respond(text)
        turns.append({"user": text, "reply": out["reply"], "cards": out["cards"], "model_calls": out["model_calls"],
                      "tokens_in": out["tokens_in"], "tokens_out": out["tokens_out"]})
    tools = a.schemas
    a.close()
    return {"label": label, "cassette": cassette, "turns": turns, "steps": a.steps, "tool_definitions": tools, "erp": erp}


def context_parts(run: dict) -> list[dict]:
    """Tokens per part of the context, measured with the run's own model and route (the recorded measuring calls)."""
    llm = LLM(MODEL, cassette=TOKEN_CASSETTE[run["cassette"]], mode=os.environ.get("LEDGER_LLM_MODE", "auto"), max_tokens=16)
    tools, steps = run["tool_definitions"], [s for s in run["steps"] if s["tools"] is not None] or run["steps"]

    def pt(messages, with_tools=True):
        return llm.chat(messages, tools=tools if with_tools else None, max_tokens=16).tokens_in

    s0 = steps[0]["messages"]
    p0, no_tools, user_only = steps[0]["prompt_tokens"], pt(s0, with_tools=False), pt([s0[1]], with_tools=False)
    parts = [{"part": "system prompt", "tokens": no_tools - user_only, "seen_from": 0},
             {"part": f"tool definitions ({len(tools)})", "tokens": p0 - no_tools, "seen_from": 0},
             {"part": "user message", "tokens": user_only, "seen_from": 0, "text": s0[1]["content"]}]
    prev = steps[0]
    for si, st in enumerate(steps[1:], start=1):
        new = st["messages"][len(prev["messages"]):]
        growth = st["prompt_tokens"] - prev["prompt_tokens"]
        res = 0
        if any(m["role"] == "tool" for m in new):
            for blank in ("", "{}"):  # the same two measurements as the experiment
                emptied = copy.deepcopy(st["messages"])
                for m in emptied[len(prev["messages"]):]:
                    if m["role"] == "tool":
                        m["content"] = blank
                res = st["prompt_tokens"] - pt(emptied)
                if 0 <= res <= growth:
                    break
        n_res = sum(1 for m in new if m["role"] == "tool")
        lens = [len(m["content"]) for m in new if m["role"] == "tool"] or [1]
        k = 0
        for m in new:
            if m["role"] == "tool":
                parts.append({"part": "tool result", "tokens": round(res * len(m["content"]) / sum(lens)) if n_res > 1 else res,
                              "seen_from": si, "text": m["content"]})
                k += 1
            elif m["role"] == "assistant" and m.get("tool_calls"):
                parts.append({"part": "tool call", "tokens": growth - res, "seen_from": si,
                              "text": json.dumps([{c["function"]["name"]: json.loads(c["function"]["arguments"])} for c in m["tool_calls"]])})
            elif m["role"] == "assistant":
                parts.append({"part": "assistant reply (+ the user's next message)", "tokens": growth - res, "seen_from": si, "text": m["content"]})
            elif m["role"] == "user":
                parts.append({"part": "user message", "tokens": None, "seen_from": si, "text": m["content"], "note": "counted with the reply above"})
        prev = st
    return parts


def show_context(run: dict, parts: list[dict] | None = None, width: int = 90):
    """Print what each model call read, part by part, and check it against the provider's prompt_tokens."""
    parts = parts if parts is not None else context_parts(run)
    steps = [s for s in run["steps"] if s["tools"] is not None] or run["steps"]
    for i, st in enumerate(steps):
        print(f"-- model call {i + 1} of {len(steps)}: prompt_tokens {st['prompt_tokens']:,} --")
        for p in parts:
            if p["seen_from"] == i:
                txt = (p.get("text") or "").replace("\n", " ")
                tok = "  (with the part above)" if p["tokens"] is None else f"{p['tokens']:>6,}"
                print(f"   + {tok}  {p['part']:<32} {txt[:width - 40]}")
        seen = sum(p["tokens"] or 0 for p in parts if p["seen_from"] <= i)
        print(f"     = {seen:,} tokens in the context ({'matches' if seen == st['prompt_tokens'] else 'differs from'} prompt_tokens)")
        out = ", ".join(f"{c['name']}({json.dumps(c['arguments'])})" for c in st["tool_calls"]) or repr((st["content"] or "")[:width])
        print(f"     model wrote ({st['completion_tokens']} tokens): {out[:width + 60]}")
    print("Never in the context: tool.py, the Ledgerline services and their {rc, err_cd, msg, data} replies, the database,"
          " Emma's session and password, the MCP plumbing.")


# Claude Code's recorded runs on the same MCP server (claude-sonnet-5.5, headless), as tool sequences per user turn
CLAUDE_CODE = json.loads((HERE / "claude_code_runs.json").read_text()) if (HERE / "claude_code_runs.json").exists() else {}
