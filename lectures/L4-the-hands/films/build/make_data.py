#!/usr/bin/env python3
"""Film data for the Lecture 4 films (stdlib, light): reads only recorded logs and the toolbox source, writes
build/data/l4_data.json. Every number on screen comes from here or from experiments/logs directly.

    python3 lectures/L4-the-hands/films/build/make_data.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
L4 = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(os.path.dirname(L4))
LOGS = os.path.join(L4, "experiments", "logs")
BOX = os.path.join(ROOT, "ledgerline", "ledgerline", "toolbox")

A = json.load(open(os.path.join(LOGS, "anatomy_check_stock.json")))
out = {"check_stock_lines": [len(l.rstrip()) for l in A["files"]["tool.py"].rstrip("\n").split("\n")]}
tools = {}
for name in sorted(os.listdir(BOX)):
    p = os.path.join(BOX, name, "tool.py")
    if os.path.exists(p):
        src = open(p).read().rstrip("\n").split("\n")
        tools[name] = [len(l.rstrip()) for l in src]
out["toolbox"] = tools
out["check_stock_lines_match_toolbox"] = tools.get("check_stock") == out["check_stock_lines"]

# ---- film 2 (context): the single question's context parts, and the full order's context at every model call
H = json.load(open(os.path.join(LOGS, "our_harness.json")))


def kind(label):
    for k, key in (("system", "system prompt"), ("defs", "tool definitions"), ("user", "user message"), ("call", "tool call"),
                   ("result", "tool result"), ("reply", "assistant reply")):
        if label.startswith(key):
            return k
    raise ValueError(label)


def parts_of(run):
    """Context parts in order; a user message with no separate count (None) is merged into the reply before it, as
    the provider measured them together."""
    out = []
    for p in run["context_parts"]:
        if p["tokens"] is None:
            out[-1]["label"] += " + Emma's next message"
            out[-1]["merged_user"] = True
            continue
        out.append({"kind": kind(p["part"]), "tokens": p["tokens"], "label": p["part"]})
    return out


single = H["single"]
sp = parts_of(single)
assert sum(p["tokens"] for p in sp) == single["check_only_tool_returns_in_context"]["parts_sum"] == single["steps"][-1]["prompt_tokens"]
out["context_single"] = {"parts": sp, "prompt_tokens": [s["prompt_tokens"] for s in single["steps"]],
                         "completion_tokens": [s["completion_tokens"] for s in single["steps"]],
                         "defs_16_tokens": next(p["tokens"] for p in H["order"]["context_parts"] if p["part"].startswith("tool definitions"))}
oh = H["order_hands"]
op = parts_of(oh)
steps, cum, i = [], 0, 0
for s in oh["steps"]:
    while cum < s["prompt_tokens"]:
        cum += op[i]["tokens"]
        i += 1
    assert cum == s["prompt_tokens"], (cum, s["prompt_tokens"])
    steps.append({"prompt_tokens": s["prompt_tokens"], "n_parts": i, "tool_calls": [c["name"] for c in s["tool_calls"]],
                  "completion_tokens": s["completion_tokens"]})
out["context_order"] = {"run": "order_hands", "parts": op, "steps": steps, "tokens_in": oh["summary"]["tokens_in"],
                        "tokens_out": oh["summary"]["tokens_out"], "model_calls": oh["summary"]["model_calls"],
                        "tool_calls": oh["summary"]["tool_calls"]}
assert sum(s["prompt_tokens"] for s in steps) == oh["summary"]["tokens_in"]
json.dump(out, open(os.path.join(HERE, "data", "l4_data.json"), "w"), indent=0)
print("order steps", [s["prompt_tokens"] for s in out["context_order"]["steps"]], "parts", len(out["context_order"]["parts"]))
print(len(tools), "tools;", "check_stock lines", len(out["check_stock_lines"]), "match:", out["check_stock_lines_match_toolbox"])
