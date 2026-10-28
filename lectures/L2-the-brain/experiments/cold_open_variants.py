"""Lecture 2 cold open, part 2: does the bare model invent a stock figure? Two system prompts x two models, 12 samples each.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L2-the-brain/experiments/cold_open_variants.py

Part 1 (cold_open.py) found that with a modest prompt gemini-3.8-flash mostly declines (1 of 12 samples invented
"450 units"). Here we add the kind of prompt a first chatbot often has ("You know Rasoi's items, stock levels ...")
and the small tier. The temperature-0 call for each cell is recorded (cassette L2v3_coldopen) so the notebook replays it;
the 12 samples at temperature 1.0 are live. Writes logs/cold_open_variants.json.
"""
import json, pathlib, re, sys
sys.path.insert(0, "/course/bahi")
from bahi.llm import LLM
from bahi.course.l2.brain import SYSTEM_BRAIN, SYSTEM_CONFIDENT, QUESTION, FOLLOW_UP, messages

NUM = re.compile(r"\d[\d,]*")
def numbers(s):
    return [int(x.replace(",", "")) for x in NUM.findall(s or "") if x.replace(",", "").isdigit() and int(x.replace(",", "")) != 5]

out = {"question": QUESTION, "cells": []}
for sys_name, system in (("plain", SYSTEM_BRAIN), ("confident", SYSTEM_CONFIDENT)):
    for model in ("gemini:gemini-3.8-flash", "gemini:gemini-3.5-flash-lite"):
        msgs = messages(QUESTION, system)
        r = LLM(model, cassette="L2v3_coldopen").chat(msgs)
        cell = {"system_name": sys_name, "system": system, "model": model,
                "t0": {"reply": r.content, "numbers": numbers(r.content), "tokens_in": r.tokens_in,
                       "tokens_out": r.tokens_out, "seconds": r.seconds, "cost_inr": r.cost_inr}}
        if numbers(r.content):
            f = LLM(model, cassette="L2v3_coldopen").chat(msgs + [{"role": "assistant", "content": r.content},
                                                                {"role": "user", "content": FOLLOW_UP}])
            cell["follow_up"] = {"reply": f.content, "tokens_in": f.tokens_in}
        hot = LLM(model, cassette="L2v3_coldopen_hot", mode="live", temperature=1.0)
        ss = [hot.chat(msgs).content for _ in range(12)]
        cell["samples_t1"] = [{"reply": s, "numbers": numbers(s)} for s in ss]
        nums = [numbers(s)[0] for s in ss if numbers(s)]
        cell["summary"] = {"n": 12, "invented": len(nums), "numbers": nums, "correct_54000": nums.count(54000)}
        print(sys_name, model, "T0:", (r.content or "")[:140].replace("\n", " "), "| T1 invented", len(nums), "/12", nums)
        out["cells"].append(cell)
p = pathlib.Path(__file__).parent / "logs" / "cold_open_variants.json"
p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("wrote", p)
