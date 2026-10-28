"""Which chat models answer right now (Gemini direct vs the same models through OpenRouter)? Prints ok or the error."""
from bahi.llm import LLM

for m in ["gemini:gemini-3.8-flash", "openrouter:google/gemini-3.8-flash", "openrouter:google/gemini-3-flash-preview",
          "openrouter:google/gemini-2.5-flash"]:
    try:
        r = LLM(m, mode="live").chat([{"role": "user", "content": "Reply with the word ok."}])
        print("OK  ", m, repr(r.content)[:40], r.seconds)
    except Exception as e:
        print("FAIL", m, str(e)[:160])
