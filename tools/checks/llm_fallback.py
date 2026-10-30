"""Check: a live gemini: call still works when the Gemini key is out of credits (falls back to OpenRouter)."""
import json
from ledgerline import llm as L
m = L.LLM(model="gemini:gemini-3.8-flash", cassette="_check_fallback", mode="live")
r = m.chat([{"role": "user", "content": "Reply with the single word: ready"}])
print("reply:", r.content, "| via OpenRouter:", bool(L._GEMINI_VIA_OPENROUTER))
tools = [{"type": "function", "function": {"name": "check_stock", "description": "Stock of an item",
          "parameters": {"type": "object", "properties": {"item_code": {"type": "string"}}, "required": ["item_code"]}}}]
msgs = [{"role": "user", "content": "How many BAT-500 do we have? Use the tool."}]
r = m.chat(msgs, tools=tools)
tc = r.tool_calls[0]
print("tool call:", tc.name, tc.arguments)
msgs += [{"role": "assistant", "content": r.content, "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)}, **({"extra_content": tc.extra} if tc.extra else {})}]},
         {"role": "tool", "tool_call_id": tc.id, "content": json.dumps({"ok": True, "free_total": 54000})}]
r = m.chat(msgs, tools=tools)
print("second turn:", (r.content or "")[:120])
print("FALLBACK OK")
