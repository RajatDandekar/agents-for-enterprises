"""Probe (live, OpenRouter): why some replies come back empty, and how to get words-only replies."""
import json, os
from openai import OpenAI
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox
from bahi.course.l5.harness import SYSTEM_FULL, profile
tb = Toolbox(ERP(), "KJOSHI")
c = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
sysm = SYSTEM_FULL.format(name="Kavita Joshi", user="KJOSHI", role="purchase executive", first="Kavita", profile=profile(tb))
ask = ("Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) from Deccan Polymers at the contract rate. "
       "Charge it to cost centre PRD-07, need-by 9 November.")
for model in ["google/gemini-3.5-flash-lite", "google/gemini-3.8-flash"]:
    m = [{"role": "system", "content": sysm}, {"role": "user", "content": ask}]
    for i in range(6):
        r = c.chat.completions.create(model=model, messages=m, tools=tb.schemas(), temperature=0, max_tokens=2048)
        ch = r.choices[0]; msg = ch.message
        print(model, i, "finish", ch.finish_reason, "content", repr((msg.content or "")[:80]), "calls", [t.function.name for t in msg.tool_calls or []], "usage", r.usage.completion_tokens, getattr(r.usage, "completion_tokens_details", None))
        if not msg.tool_calls:
            break
        m.append({"role": "assistant", "content": msg.content, "tool_calls": [t.model_dump() for t in msg.tool_calls]})
        for t in msg.tool_calls:
            m.append({"role": "tool", "tool_call_id": t.id, "content": tb.call_json(t.function.name, json.loads(t.function.arguments or "{}"))})
    for kw in ({"tool_choice": "none", "tools": tb.schemas()}, {}):
        try:
            r = c.chat.completions.create(model=model, messages=m, temperature=0, max_tokens=2048, **kw)
            print("   words-only", list(kw), "finish", r.choices[0].finish_reason, repr((r.choices[0].message.content or "")[:100]))
        except Exception as e:
            print("   words-only", list(kw), "ERR", str(e)[:200])
