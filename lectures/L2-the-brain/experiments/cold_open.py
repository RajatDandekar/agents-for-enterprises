"""Lecture 2 v4 (Northbridge Cycles): the brain alone, measured on gemini-3.8-flash. Every Gemini number of the lecture.

    sh tools/mrun.sh tools/modal_run.py --script lectures/L2-the-brain/experiments/cold_open.py --mode auto
    sh tools/mrun.sh tools/modal_run.py --script lectures/L2-the-brain/experiments/cold_open.py --mode replay

Ask Northbridge at ?stage=brain is the app's own class (ledgerline.experience.harness.AskNorthbridge, no tools) with
its own brain-stage system prompt for Emma Clarke; ledgerline.course.l2.brain.BrainOnly only names the cassette.
  1. cold open      Emma's question, 8 separate runs at the app's settings (temperature 0), one cassette per run
                    (L2v4_coldopen_r1 ... r8), plus the follow-up "Where did that number come from?" on run 1
  2. temperature 1  the same question 8 more times at temperature 1.0 (L2v4_coldopen_t1_r1 ... r8)
  3. the fix        the same question with one Ledgerline stock line as the last line of the system prompt,
                    3 runs (L2v4_facts_r1 ... r3)
  4. tools preview  the same question with two tools offered (find_item, check_stock): it asks instead of guessing
                    (L2v4_toolpreview)
  5. tokens         what Gemini counts: the question with and without the system prompt (L2v4_tokens), and one
                    direct API call that keeps the provider's whole usage record (live only, not replayed)
  6. cut-off        the model's own answer to "what is the most recent month your training data covers?" and to
                    "what is today's date?" with and without the app's prompt (L2v4_cutoff)
The truth comes from the toolbox (check_stock on a fresh Ledgerline). Writes logs/cold_open.json (auto/record) or
logs/cold_open_replay.json (replay).
"""
import json
import os
import pathlib
import re

from ledgerline.course.l2.brain import (BrainOnly, FACT, FOLLOW_UP, MODEL, QUESTION, SYSTEM_BRAIN, SYSTEM_FACTS,
                                        TRUE_ANSWER, USD_GBP, cost_gbp, messages)
from ledgerline.erp.engine import ERP
from ledgerline.llm import LLM, PRICES
from ledgerline.toolbox import Toolbox

MODE = os.environ.get("LEDGER_LLM_MODE", "auto")
LOG = pathlib.Path(__file__).parent / "logs" / ("cold_open_replay.json" if MODE == "replay" else "cold_open.json")
NUM = re.compile(r"\d[\d,]*\d|\d")
N_RUNS, N_HOT, N_FACTS = 8, 8, 3


def numbers(s):
    """Every number in a reply, as integers (commas removed). Dates and times are kept: the reader sees them too."""
    return [int(x.replace(",", "")) for x in NUM.findall(s or "")]


def stock_figure(s):
    """The number the reply gives as the stock: the first number in its first line (None when that line has none)."""
    n = numbers((s or "").strip().split("\n")[0])
    return n[0] if n else None


def run(agent, text):
    r = agent.respond(text)
    llm = agent.llms[agent.model_used]
    last = llm.log[-1]
    return {"reply": r["reply"], "stock_figure": stock_figure(r["reply"]), "numbers": numbers(r["reply"]),
            "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"], "seconds": last.seconds,
            "model": r["model"], "replayed": last.replayed, "model_calls": r["model_calls"],
            "cost_gbp": round(cost_gbp(r["tokens_in"], r["tokens_out"]), 6), "reply_chars": len(r["reply"])}


out = {"model": MODEL, "mode": MODE, "system": SYSTEM_BRAIN, "question": QUESTION, "price_usd_per_million": PRICES["gemini-3.8-flash"],
       "usd_gbp": USD_GBP, "true_answer": TRUE_ANSWER}

# 0. the truth, from Ledgerline (the same tool Lecture 4 gives Ask Northbridge)
truth = Toolbox(ERP(), "ECLARKE").call("check_stock", {"item_code": "BAT-500"})
man = next(w for w in truth["warehouses"] if w["warehouse"] == "WH-MAN-STR")
assert man["on_hand"] == TRUE_ANSWER, man
assert f"{man['on_hand']:,}" in FACT
out["truth"] = truth
print("truth: Manchester main stores", man["on_hand"], "| all warehouses", truth["free_total"], "| cover", truth["cover_days"], "days")

# 1. the cold open: 8 separate conversations at the app's own settings
runs = []
for i in range(1, N_RUNS + 1):
    a = BrainOnly(f"L2v4_coldopen_r{i}")
    rec = run(a, QUESTION)
    rec["run"] = i
    if i == 1:
        f = run(a, FOLLOW_UP)
        f["question"] = FOLLOW_UP
        out["follow_up"] = f
        print("follow-up:", f["reply"].replace("\n", " / "))
    runs.append(rec)
    print(f"run {i}: figure={rec['stock_figure']} in={rec['tokens_in']} out={rec['tokens_out']} replayed={rec['replayed']} |",
          rec["reply"].replace("\n", " / ")[:300])
out["runs"] = runs
figs = [r["stock_figure"] for r in runs]
out["runs_summary"] = {"n": len(runs), "with_a_figure": sum(x is not None for x in figs), "figures": figs,
                       "distinct": sorted({x for x in figs if x is not None}), "correct": figs.count(TRUE_ANSWER),
                       "tokens_in": runs[0]["tokens_in"], "mean_tokens_out": round(sum(r["tokens_out"] for r in runs) / len(runs), 1),
                       "cost_gbp_each": [r["cost_gbp"] for r in runs], "seconds": [r["seconds"] for r in runs]}

# 2. temperature 1.0
hot = []
for i in range(1, N_HOT + 1):
    rec = run(BrainOnly(f"L2v4_coldopen_t1_r{i}", temperature=1.0), QUESTION)
    rec["run"] = i
    hot.append(rec)
    print(f"T=1 run {i}: figure={rec['stock_figure']} |", rec["reply"].replace("\n", " / ")[:200])
out["runs_t1"] = hot
hf = [r["stock_figure"] for r in hot]
out["runs_t1_summary"] = {"n": len(hot), "with_a_figure": sum(x is not None for x in hf), "figures": hf,
                          "distinct": sorted({x for x in hf if x is not None}), "correct": hf.count(TRUE_ANSWER)}

# 3. the fix: the fact in the prompt
facts = []
for i in range(1, N_FACTS + 1):
    rec = run(BrainOnly(f"L2v4_facts_r{i}", system=SYSTEM_FACTS), QUESTION)
    rec["run"] = i
    facts.append(rec)
    print(f"facts run {i}: figure={rec['stock_figure']} |", rec["reply"].replace("\n", " / ")[:200])
out["facts"] = {"line": FACT, "where": "appended to the app's system prompt as its last line", "system": SYSTEM_FACTS,
                "runs": facts, "correct": sum(r["stock_figure"] == TRUE_ANSWER for r in facts)}

# 4. a preview of Lecture 4: offer two tools and it writes a request instead of a number
tools = Toolbox(ERP(), "ECLARKE", names=["find_item", "check_stock"]).schemas()
t = LLM(MODEL, cassette="L2v4_toolpreview", max_tokens=4096).chat(messages(), tools=tools)
out["tool_preview"] = {"tools_offered": [x["function"]["name"] for x in tools], "content": t.content,
                       "tool_calls": [{"name": c.name, "arguments": c.arguments} for c in t.tool_calls],
                       "tokens_in": t.tokens_in, "tokens_out": t.tokens_out, "replayed": t.replayed}
print("tool preview:", out["tool_preview"]["tool_calls"], t.content)

# 5. tokens: what the system prompt costs, as Gemini counts it
tk = LLM(MODEL, cassette="L2v4_tokens", max_tokens=4096)
bare = tk.chat([{"role": "user", "content": QUESTION}])
out["tokens"] = {"with_system": {"tokens_in": runs[0]["tokens_in"]},
                 "question_only": {"tokens_in": bare.tokens_in, "tokens_out": bare.tokens_out, "reply": bare.content,
                                   "stock_figure": stock_figure(bare.content)},
                 "system_prompt_tokens": runs[0]["tokens_in"] - bare.tokens_in,
                 "chars": {"system": len(SYSTEM_BRAIN), "question": len(QUESTION)},
                 "words": {"system": len(SYSTEM_BRAIN.split()), "question": len(QUESTION.split())}}
print("tokens in: with system", runs[0]["tokens_in"], "| question only", bare.tokens_in)
if MODE != "replay":  # the provider's whole usage record for one call (shows whether thinking tokens are billed)
    from openai import OpenAI
    c = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
               api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    resp = c.chat.completions.create(model="gemini-3.8-flash", messages=messages(), temperature=0.0, max_tokens=4096)
    u = resp.usage.model_dump() if hasattr(resp.usage, "model_dump") else dict(resp.usage)
    out["tokens"]["usage_record"] = {"usage": u, "reply": resp.choices[0].message.content}
    print("usage record:", u)
else:
    prev = json.loads((LOG.parent / "cold_open.json").read_text()) if (LOG.parent / "cold_open.json").exists() else {}
    out["tokens"]["usage_record"] = prev.get("tokens", {}).get("usage_record")

# 6. the cut-off: what the model says about its own training data, and where 'today' comes from
co = LLM(MODEL, cassette="L2v4_cutoff", max_tokens=4096)
CUT_Q = ("Without looking anything up: what is the most recent month and year that your training data covers? "
         "Answer with the month and year only.")
DATE_Q = "What is today's date? Answer with the date only."
out["cutoff"] = {"question": CUT_Q, "reply": co.chat([{"role": "user", "content": CUT_Q}]).content,
                 "date_question": DATE_Q,
                 "date_no_prompt": co.chat([{"role": "user", "content": DATE_Q}]).content,
                 "date_with_app_prompt": co.chat(messages(DATE_Q)).content}
print("cut-off:", out["cutoff"])

calls = len(runs) + 1 + len(hot) + len(facts) + 1 + 1 + 3
tin = sum(r["tokens_in"] for r in runs + hot + facts) + out["follow_up"]["tokens_in"] + t.tokens_in + bare.tokens_in
tout = sum(r["tokens_out"] for r in runs + hot + facts) + out["follow_up"]["tokens_out"] + t.tokens_out + bare.tokens_out
out["totals"] = {"model_calls_recorded": calls, "tokens_in": tin, "tokens_out": tout,
                 "cost_gbp_excluding_cutoff_calls": round(cost_gbp(tin, tout), 4)}
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("wrote", LOG, out["totals"])
