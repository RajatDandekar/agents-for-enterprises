"""Which keys can still call gemini-3.8-flash? (2026-10-28: the Gemini prepay ran out mid-run.) No cassette."""
import os
from openai import OpenAI
for name, base, key, model in [("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/", "GEMINI_API_KEY", "gemini-3.8-flash"),
                               ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "google/gemini-3.8-flash"),
                               ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "google/gemini-3-flash-preview")]:
    try:
        c = OpenAI(base_url=base, api_key=os.environ.get(key, ""), max_retries=0, timeout=60)
        r = c.chat.completions.create(model=model, messages=[{"role": "user", "content": "Say OK."}], max_tokens=20)
        print(name, model, "OK", r.choices[0].message.content, r.usage.prompt_tokens)
    except Exception as e:
        print(name, model, "ERR", str(e)[:200])
