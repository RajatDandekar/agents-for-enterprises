"""Which model endpoints answer right now (the shared Gemini key ran out of prepaid credit on 28 Oct)."""
import os
from openai import OpenAI
for name, base, key, models in [
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", ["gemini-3.8-flash", "gemini-3.5-flash-lite"]),
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", ["google/gemini-3.8-flash", "google/gemini-3.5-flash-lite", "google/gemini-2.5-flash"])]:
    if not os.environ.get(key):
        print(name, "no key"); continue
    c = OpenAI(base_url=base, api_key=os.environ[key])
    for m in models:
        try:
            r = c.chat.completions.create(model=m, messages=[{"role": "user", "content": "Say OK."}], max_tokens=5)
            print(name, m, "OK", r.choices[0].message.content)
        except Exception as e:  # noqa: BLE001
            print(name, m, "ERR", str(e)[:200])
