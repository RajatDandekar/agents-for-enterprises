"""Lecture 4: one function-calling round trip, exactly as it crossed the network.

Kavita types "Check stock of the 5-litre gasket." We POST the chat (system prompt, her message and the 15 toolbox
tool definitions) to gemini-3.8-flash's OpenAI-compatible endpoint with plain httpx, so nothing hides the JSON.
Whatever tool calls come back, our code runs them through the Toolbox in Kavita's session and posts the tool
result messages back, until the model answers in words (at most 4 rounds). Every request body and response body
is logged (the API key travels in a header and is never logged). Writes logs/roundtrip.json.

    modal run tools/modal_run.py --script lectures/L4-the-hands/experiments/roundtrip.py --args "--ask 'Check stock of the 5-litre gasket.'"
"""
import argparse
import json
import os
import pathlib
import time

import httpx

from bahi.course.l4 import HANDS_SYSTEM
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="gemini-3.8-flash")
ap.add_argument("--ask", default="Check stock of the 5-litre gasket.")
ap.add_argument("--tag", default="roundtrip")
a = ap.parse_args()

URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
KEY = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
erp = ERP()
tb = Toolbox(erp, "KJOSHI")
u = erp.user("KJOSHI")
messages = [{"role": "system", "content": HANDS_SYSTEM.format(name=u["name"], user_id="KJOSHI", first="Kavita")},
            {"role": "user", "content": a.ask}]
rounds = []
with httpx.Client(timeout=120) as h:
    for rnd in range(4):
        body = {"model": a.model, "messages": messages, "tools": tb.schemas(), "temperature": 0}
        t0 = time.perf_counter()
        r = h.post(URL, json=body, headers={"Authorization": f"Bearer {KEY}"})
        secs = round(time.perf_counter() - t0, 2)
        r.raise_for_status()
        resp = r.json()
        msg = resp["choices"][0]["message"]
        entry = {"round": rnd + 1, "seconds": secs, "request_body": json.loads(json.dumps(body)),
                 "request_bytes": len(json.dumps(body)), "response_body": resp, "ran": []}
        assistant = {"role": "assistant", "content": msg.get("content")}
        if msg.get("tool_calls"):
            assistant["tool_calls"] = msg["tool_calls"]  # echoed back as-is (Gemini 3 needs its thought signature)
        messages.append(assistant)
        if not msg.get("tool_calls"):
            rounds.append(entry)
            break
        for tc in msg["tool_calls"]:
            args = json.loads(tc["function"]["arguments"] or "{}")
            c0 = len(erp.calls)
            result = tb.call(tc["function"]["name"], args)
            services = [{"svc": c.svc, "payload": c.payload, "rc": c.rc} for c in erp.calls[c0:]]
            tool_msg = {"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(result, default=str)}
            messages.append(tool_msg)
            entry["ran"].append({"tool": tc["function"]["name"], "arguments": args, "bahi_services": services,
                                 "result": result, "tool_message": tool_msg})
        rounds.append(entry)
        print(f"round {rnd + 1}: {[x['tool'] for x in entry['ran']]} {json.dumps([x['arguments'] for x in entry['ran']])}")

final = rounds[-1]["response_body"]["choices"][0]["message"].get("content")
print("answer:", final)
out = {"model": a.model, "ask": a.ask, "endpoint": URL.replace("https://generativelanguage.googleapis.com", "<gemini>"),
       "n_tools": len(tb.schemas()), "rounds": rounds, "final_answer": final,
       "usage": [r["response_body"].get("usage") for r in rounds]}
(pathlib.Path(__file__).resolve().parent / "logs" / f"{a.tag}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
print("wrote", f"logs/{a.tag}.json")
