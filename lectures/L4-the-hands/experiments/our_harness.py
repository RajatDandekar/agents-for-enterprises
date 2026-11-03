"""Lecture 4, sections 7–9: our harness (Ask Northbridge's loop) on the two tasks, with the context captured at every step.

    tools/mrun.sh tools/modal_run.py --script lectures/L4-the-hands/experiments/our_harness.py            (record, then replay)
    tools/mrun.sh tools/modal_run.py --script lectures/L4-the-hands/experiments/our_harness.py --mode replay

The harness is ledgerline.experience.harness.AskNorthbridge, stage "agent", exactly as the live app runs it: the toolbox is
discovered over MCP (in memory), the model is gemini-3.8-flash through OpenRouter, the battery-safety guard runs before
every write. Only the model client is swapped for a recording one (cassette L4v4_ours), so the run replays without a key.

  single  Emma: "How many BAT-500 battery packs do we have in Manchester main stores?"   tools: check_stock, find_item
  order   Emma: "Order 2,000 BAT-500 packs from Voltway for the spring launch run."     tools: all 16
          then "Yes, go ahead. We need them by 9 November 2026."

For "What the LLM sees", every model call is kept whole: the messages array, the tool definitions, the reply and the
provider's own token counts. Tokens per part are measured with the same model through the same route:
  tools        prompt_tokens(step 0) - prompt_tokens(step 0 without tools)
  system       prompt_tokens(no tools) - prompt_tokens(the user message alone)
  user         prompt_tokens(the user message alone)             (includes the chat template's few tokens)
  tool results prompt_tokens(step k) - prompt_tokens(step k with every new tool result emptied to "")
  tool calls   what is left of the growth from step k-1 to step k  (the assistant's call message + the result framing)
The measuring calls are recorded too (cassette L4v4_ours_tokens). Writes logs/our_harness.json.
"""
import copy
import json
import re
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))
sys.path.insert(0, str(HERE))
MODEL = os.environ.get("L4_OURS_MODEL", "openrouter:google/gemini-3.8-flash")
os.environ["NORTHBRIDGE_MODEL"] = MODEL
os.environ["NORTHBRIDGE_FALLBACKS"] = ""          # one model, no silent fallback, so the record says what ran
os.environ.setdefault("LEDGER_ENV_FILE", str(ROOT / ".env"))

from ledgerline.erp.engine import ERP  # noqa: E402
from ledgerline.erp.receipts import install_receipts  # noqa: E402
from ledgerline.experience import harness as H  # noqa: E402
from ledgerline.experience.players import guard_erp  # noqa: E402
from ledgerline.llm import LLM  # noqa: E402
from ledgerline.toolbox import ALL  # noqa: E402

MODE = os.environ.get("LEDGER_LLM_MODE", "auto")
CASSETTE, TOK_CASSETTE = "L4v4_ours", "L4v4_ours_tokens"
H.CHAIN[:] = [MODEL]


class Recorded(H.AskNorthbridge):
    """AskNorthbridge with a recording model client and a copy of the context at every model call."""

    def __init__(self, *a, system=None, cassette=CASSETTE, **kw):
        super().__init__(*a, **kw)
        self.steps = []
        self.cassette = cassette
        if system:  # Lecture 4's "hands" prompt (l4_prompts.py): same harness, a prompt without Northbridge codes
            self.messages[0]["content"] = system

    def _llm(self, model):
        if model not in self.llms:
            self.llms[model] = LLM(model, cassette=self.cassette, mode=MODE, max_tokens=H.MAX_TOKENS)
        return self.llms[model]

    def _chat(self, tools, extra=None, **kw):
        msgs = copy.deepcopy(self.messages + (extra or []))
        r = super()._chat(tools, extra, **kw)
        self.steps.append({"call": len(self.steps), "messages": msgs, "tools_sent": [t["function"]["name"] for t in tools or []],
                           "settings": {k: v for k, v in kw.items()},
                           "reply": {"content": r.content, "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments}
                                                                          for t in r.tool_calls]},
                           "tool_calls": [{"id": t.id, "name": t.name, "arguments": t.arguments} for t in r.tool_calls],
                           "prompt_tokens": r.tokens_in, "completion_tokens": r.tokens_out, "seconds": r.seconds,
                           "replayed": r.replayed, "model": r.model, "tools": tools})
        return r


def measure(llm, steps, tools):
    """Tokens per part of the context, with the run's own model and route (see the module docstring)."""
    def pt(messages, with_tools=True):
        return llm.chat(messages, tools=tools if with_tools else None, max_tokens=16).tokens_in

    s0 = steps[0]["messages"]
    sys_msg, user_msg = s0[0], s0[1]
    p0 = steps[0]["prompt_tokens"]
    no_tools = pt(s0, with_tools=False)
    user_only = pt([user_msg], with_tools=False)
    parts = [{"part": "system prompt", "tokens": no_tools - user_only, "text": sys_msg["content"]},
             {"part": f"tool definitions ({len(tools)})", "tokens": p0 - no_tools, "tools": [t["function"]["name"] for t in tools]},
             {"part": "user message", "tokens": user_only, "text": user_msg["content"],
              "note": "includes the chat template's own few tokens"}]
    prev = steps[0]
    for st in steps[1:]:
        if st["tools"] is None or len(st["messages"]) <= len(prev["messages"]):
            prev = st
            continue
        new = st["messages"][len(prev["messages"]):]
        emptied = copy.deepcopy(st["messages"])
        for m in emptied[len(prev["messages"]):]:
            if m["role"] == "tool":
                m["content"] = ""
        growth = st["prompt_tokens"] - prev["prompt_tokens"]
        has_results = any(m["role"] == "tool" for m in new)
        results_tok = st["prompt_tokens"] - pt(emptied, with_tools=st["tools"] is not None) if has_results else 0
        placeholder = '""'
        if not 0 <= results_tok <= growth:  # an empty tool message can be counted oddly: measure against "{}" instead
            for m in emptied[len(prev["messages"]):]:
                if m["role"] == "tool":
                    m["content"] = "{}"
            results_tok = st["prompt_tokens"] - pt(emptied, with_tools=st["tools"] is not None)
            placeholder = '"{}" (the "" measurement was out of range)'
        if not 0 <= results_tok <= growth:
            results_tok = None
        for m in new:
            if m["role"] == "assistant" and m.get("tool_calls"):
                parts.append({"part": "tool call (model -> our code)", "tokens": None, "calls": [
                    {"name": c["function"]["name"], "arguments": json.loads(c["function"]["arguments"])} for c in m["tool_calls"]]})
                parts[-1]["tokens"] = growth - results_tok if results_tok is not None else None  # what is left
            elif m["role"] == "tool":
                parts.append({"part": "tool result (only what the tool returned)", "tokens": None, "content": m["content"]})
            elif m["role"] == "user":
                parts.append({"part": "user message", "tokens": None, "text": m["content"]})
            elif m["role"] == "assistant":
                parts.append({"part": "assistant reply", "tokens": None, "text": m["content"]})
        n_res = sum(1 for m in new if m["role"] == "tool")
        res_parts = [p for p in parts[-len(new):] if p["part"].startswith("tool result")]
        if results_tok is None:
            for p in res_parts:
                p["note"] = "not measurable: both emptied-result measurements were out of range"
        elif n_res == 1:
            res_parts[0]["tokens"] = results_tok
            if placeholder != '""':
                res_parts[0]["note"] = f"measured against {placeholder}"
        elif n_res > 1:  # several results in one round: share the measured total by length (noted)
            total_len = sum(len(p["content"]) for p in res_parts) or 1
            for p in res_parts:
                p["tokens"] = round(results_tok * len(p["content"]) / total_len)
                p["note"] = f"{n_res} results in this round measured together ({results_tok} tokens), shared by length"
        other = [p for p in parts[-len(new):] if p["tokens"] is None]
        if other and not any(m.get("tool_calls") for m in new if m["role"] == "assistant") and results_tok is not None:
            other[0]["tokens"] = growth - results_tok
            other[0]["note"] = "growth of the prompt since the previous call: " + " + ".join(p["part"] for p in other)
            for p in other[1:]:
                p["note"] = "counted in the part above"
        prev = st
    return parts


def play(label, user_turns, names, system=None, cassette=CASSETTE, prompt_name="harness.AGENT (the app's agent prompt)"):
    erp = ERP()
    install_receipts(erp)
    guard_erp(erp)
    a = Recorded(erp, "ECLARKE", "agent", names=names, system=system, cassette=cassette)
    turns = []
    t0 = time.perf_counter()
    for text in user_turns:
        out = a.respond(text)
        turns.append({"user": text, "reply": out["reply"], "cards": out["cards"], "rounds": out["rounds"],
                      "model_calls": out["model_calls"], "tokens_in": out["tokens_in"], "tokens_out": out["tokens_out"],
                      "cost_gbp_est": round(out["cost_inr"] / 88.0 * 0.79, 5)})
    secs = time.perf_counter() - t0
    tools = a.schemas
    a.close()
    docs = {"pr": erp.q("SELECT pr_no,status,cc_cd,need_dt,est_value,raised_by FROM pr_hdr WHERE raised_on>='2026-10-26'"),
            "po": erp.q("SELECT po_no,status,sup_cd,tax_cd,gross_value FROM po_hdr WHERE created_on>='2026-10-26'"),
            "approval": erp.q("SELECT doc_no,approver,status FROM approval WHERE requested_on>='2026-10-26'")}
    return {"label": label, "model": MODEL, "harness": "ledgerline.experience.harness.AskNorthbridge, stage agent (max 14 rounds)",
            "system_prompt_name": prompt_name, "cassette": cassette, "system_prompt": a.messages[0]["content"], "tools_exposed": a.tools.names if a.tools else [],
            "tool_definitions": tools, "turns": turns, "steps": a.steps, "seconds_wall": round(secs, 2),
            "ledgerline_after": docs, "ledgerline_service_calls": len(erp.calls)}


from l4_prompts import codes_compared, hands_prompt  # noqa: E402

ORDER_TURN2 = "Yes, go ahead. We need them by 9 November 2026."
ORDER_TURN3 = "Yes, submit the purchase request."  # the hands runs only: one more yes if the model previews again
HANDS = {  # the order on the "hands" prompt; the second phrasing is used only if the first one still shortcuts
    "order_hands": "I need 2,000 of the 36 V 500 Wh battery packs from Voltway for the spring launch run.",
    "order_hands_b": "Can you get us 2,000 of the 500 Wh battery packs from Voltway? They're for the spring launch run.",
}
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else ["single", "order"]
runs = {}
if "single" in ONLY:
    runs["single"] = play("single", ["How many BAT-500 battery packs do we have in Manchester main stores?"],
                          ["check_stock", "find_item"])
if "order" in ONLY:
    runs["order"] = play("order", ["Order 2,000 BAT-500 packs from Voltway for the spring launch run.", ORDER_TURN2], ALL)
for k, text in HANDS.items():
    if k in ONLY:
        runs[k] = play(k, [text, ORDER_TURN2, ORDER_TURN3], ALL, system=hands_prompt("ECLARKE"), cassette="L4v4_ours_hands",
                       prompt_name="l4_prompts.HANDS_L4 (no item, supplier or cost-centre codes)")
        runs[k]["prompt_codes_compared"] = codes_compared()

HANDS_RUNS = [k for k in runs if k in HANDS]
tok_llm = LLM(MODEL, cassette=TOK_CASSETTE if not HANDS_RUNS else "L4v4_ours_hands_tokens", mode=MODE, max_tokens=16)
for k, r in runs.items():
    try:
        r["context_parts"] = measure(tok_llm, [s for s in r["steps"] if s["tools"] is not None] or r["steps"], r["tool_definitions"])
        r["context_parts_method"] = "provider prompt_tokens on prefix requests (see docstring); same model and route"
    except Exception as e:  # noqa: BLE001
        r["context_parts"] = {"not_measured": f"{type(e).__name__}: {e}"[:300]}
    r["what_never_enters_the_context"] = ["tool.py", "the Ledgerline services and their {rc, err_cd, msg, data} replies",
                                          "the database", "Emma's session and password", "the MCP plumbing"]
    calls = sum(len(t["cards"]) for t in r["turns"])
    r["summary"] = {"tool_calls": calls, "sequence": [c["tool"] for t in r["turns"] for c in t["cards"]],
                    "model_calls": sum(t["model_calls"] for t in r["turns"]),
                    "tokens_in": sum(t["tokens_in"] for t in r["turns"]), "tokens_out": sum(t["tokens_out"] for t in r["turns"]),
                    "cost_gbp_est": round(sum(t["cost_gbp_est"] for t in r["turns"]), 5),
                    "errors_recovered": [c["tool"] for t in r["turns"] for c in t["cards"]
                                         if isinstance(c["result"], dict) and c["result"].get("ok") is False],
                    "replayed": all(s["replayed"] for s in r["steps"])}
    cards = [c for t in r["turns"] for c in t["cards"]]
    tool_msgs = [m for m in r["steps"][-1]["messages"] if m["role"] == "tool"]
    r["check_only_tool_returns_in_context"] = {  # every tool message the model saw is exactly what the tool returned
        "tool_messages": len(tool_msgs), "identical_to_tool_results": all(json.loads(m["content"]) == c["result"]
                                                                          for m, c in zip(tool_msgs, cards)),
        "parts_sum": sum(p.get("tokens") or 0 for p in r["context_parts"]) if isinstance(r["context_parts"], list) else None,
        "last_prompt_tokens": r["steps"][-1]["prompt_tokens"]}
runs["measuring_calls" + ("_hands" if HANDS_RUNS else "")] = tok_llm.totals()
runs["note"] = ("cost_gbp_est uses OpenRouter's list price for google/gemini-3.8-flash ($0.825 / $4.125 per M tokens, "
                "harness.PRICE), converted at 0.79 GBP/USD; the measuring calls are listed separately.")
(HERE / "logs").mkdir(exist_ok=True)
OUT_NAME = "our_harness_replay_check.json" if MODE == "replay" else "our_harness.json"  # a replay never overwrites the record
if (HERE / "logs" / OUT_NAME).exists():  # keep the runs recorded earlier; replace only the ones run now
    runs = {**json.loads((HERE / "logs" / OUT_NAME).read_text()), **runs}
VAT_SLIP = re.compile(r"273,600[^.\n]{0,25}\b(ex\.?|excl\.?|excluding|before|net of)\s*VAT", re.I)
for k, r in runs.items():  # observed model errors: figures the reply gets wrong (the tool's figures were right)
    if isinstance(r, dict) and "turns" in r:
        r["observed_model_errors"] = [
            {"turn": i + 1, "error": "called the request's estimated value (£273,600 = 2,000 x £114.00 x 1.20) 'ex. VAT'; "
                                     "the tool's estimated_value includes the 20% VAT",
             "reply_excerpt": VAT_SLIP.search(t["reply"] or "").group(0)}
            for i, t in enumerate(r["turns"]) if VAT_SLIP.search(t["reply"] or "")]
        said = " ".join(t["user"] for t in r["turns"][:1]) + r.get("system_prompt", "")
        for c in r["turns"][0]["cards"]:  # a need-by date nobody gave (the user gives it in turn 2)
            nb = (c.get("args") or {}).get("need_by")
            if nb and nb not in said:
                r["observed_model_errors"].append({"turn": 1, "error": f"guessed need_by={nb} in a {c['tool']} preview "
                                                   "before the user gave a date (the prompt says never guess)"})
(HERE / "logs" / OUT_NAME).write_text(json.dumps(runs, indent=1, default=str, ensure_ascii=False))
print("measuring calls this run:", tok_llm.totals())
for k in [k for k in runs if k in ONLY]:
    r = runs[k]
    print(f"== {k}: {r['summary']}")
    for t in r["turns"]:
        print("  USER:", t["user"])
        for c in t["cards"]:
            print(f"    -> {c['tool']}({json.dumps(c['args'])[:150]}) ok={c['result'].get('ok') if isinstance(c['result'], dict) else '?'}")
        print("  REPLY:", (t["reply"] or "")[:500])
    if isinstance(r["context_parts"], list):
        for p in r["context_parts"]:
            print(f"    [{p['tokens']}] {p['part']}")
print("measuring calls:", runs["measuring_calls"])
