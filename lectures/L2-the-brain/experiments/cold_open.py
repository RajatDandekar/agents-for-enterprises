"""Lecture 2 cold open: ask the bare Ask Rasoi (gemini-3.8-flash, no tools) how many gaskets are in Pune stores.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L2-the-brain/experiments/cold_open.py

Records (cassette L2v3_coldopen) the canonical temperature-0 call the notebook replays, then samples the same
question 12 times at temperature 1.0 (live, not cached) to see whether the invented number changes, asks the
follow-up "Where did that number come from?", and finally shows the same question with one tool (check_stock)
offered: the model writes a JSON request instead (cassette L2v3_toolpreview). The true answer comes from the
toolbox. Everything goes to logs/cold_open.json.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, "/course/bahi")
from bahi.llm import LLM
from bahi.course.l2.brain import MODEL, SYSTEM_BRAIN, QUESTION, FOLLOW_UP, messages
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox

LOG = pathlib.Path(__file__).parent / "logs" / "cold_open.json"
NUM = re.compile(r"\d[\d,]*")


def numbers(s):
    return [int(x.replace(",", "")) for x in NUM.findall(s or "") if x.replace(",", "").isdigit() and int(x.replace(",", "")) not in (5,)]


out = {"model": MODEL, "system": SYSTEM_BRAIN, "question": QUESTION}

# 1. the canonical call: temperature 0, recorded for replay
llm = LLM(MODEL, cassette="L2v3_coldopen")
msgs = messages()
r = llm.chat(msgs)
out["canonical"] = {"reply": r.content, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds,
                    "cost_inr": r.cost_inr, "numbers": numbers(r.content), "temperature": 0.0}
print("T=0:", r.content)

# 2. the follow-up turn (the whole history goes back in)
msgs2 = msgs + [{"role": "assistant", "content": r.content}, {"role": "user", "content": FOLLOW_UP}]
r2 = llm.chat(msgs2)
out["follow_up"] = {"question": FOLLOW_UP, "reply": r2.content, "tokens_in": r2.tokens_in, "tokens_out": r2.tokens_out,
                    "seconds": r2.seconds}
print("follow-up:", r2.content)

# 3. the same question, 12 times at temperature 1.0 (live every time, so each is a fresh sample)
hot = LLM(MODEL, cassette="L2v3_coldopen_hot", mode="live", temperature=1.0)
samples = []
for i in range(12):
    s = hot.chat(msgs)
    samples.append({"i": i, "reply": s.content, "numbers": numbers(s.content), "tokens_out": s.tokens_out})
    print(f"T=1 #{i}:", (s.content or "").replace("\n", " ")[:160])
out["samples_t1"] = samples
nums = [s["numbers"][0] for s in samples if s["numbers"]]
out["samples_summary"] = {"n": len(samples), "with_a_number": len(nums), "distinct_numbers": sorted(set(nums)),
                          "correct_54000": sum(1 for x in nums if x == 54000)}

# 4. no system prompt at all
bare = llm.chat([{"role": "user", "content": QUESTION}])
out["no_system_prompt"] = {"reply": bare.content, "numbers": numbers(bare.content)}
print("no system:", bare.content)

# 5. the truth, from the toolbox
tb = Toolbox(ERP(), "KJOSHI")
truth = tb.call("check_stock", {"item_code": "GSK-SIL-05L"})
out["truth"] = truth
print("truth:", json.dumps(truth, default=str)[:400])

# 6. preview of L4: offer one tool, and the model writes a JSON request instead of a number
tl = LLM(MODEL, cassette="L2v3_toolpreview")
tools = Toolbox(ERP(), "KJOSHI", names=["find_item", "check_stock"]).schemas()
t = tl.chat(msgs, tools=tools)
out["tool_preview"] = {"tools_offered": [x["function"]["name"] for x in tools], "content": t.content,
                       "tool_calls": [{"name": c.name, "arguments": c.arguments} for c in t.tool_calls],
                       "tokens_in": t.tokens_in, "tokens_out": t.tokens_out}
print("tool preview:", out["tool_preview"]["tool_calls"], t.content)

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("wrote", LOG)
