"""List the chat models the Gemini key can reach, and try one tool call on each candidate."""
import os, time
from openai import OpenAI
c = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.environ["GEMINI_API_KEY"])
names = sorted(m.id for m in c.models.list())
print([n for n in names if "gemini" in n and "embed" not in n and "image" not in n and "tts" not in n][:80])
print([n for n in names if "embed" in n])
tool = {"type": "function", "function": {"name": "stk_query", "description": "STOCK STATUS ENQUIRY",
        "parameters": {"type": "object", "properties": {"itm_cd": {"type": "string"}}, "required": ["itm_cd"]}}}
for m in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview", "gemini-3.8-flash"]:
    try:
        t = time.time()
        r = c.chat.completions.create(model=m, messages=[{"role": "user", "content": "How many BAT-500 do we have?"}], tools=[tool])
        print(m, "OK", round(time.time() - t, 2), r.choices[0].message.tool_calls[0].function.arguments if r.choices[0].message.tool_calls else r.choices[0].message.content[:80], r.usage.prompt_tokens, r.usage.completion_tokens)
    except Exception as e:
        print(m, "ERR", str(e)[:160])
