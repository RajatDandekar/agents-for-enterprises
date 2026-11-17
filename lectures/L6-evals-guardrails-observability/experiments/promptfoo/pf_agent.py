"""promptfoo provider: Ask Northbridge (Lecture 5's Finale, ledgerline.course.l6.agent.Agent) in a fresh sandbox.

promptfoo renders the prompt (here: the whole system prompt, prompts/good.txt or prompts/thursday.txt) and calls
call_api(prompt, options, context); the user's message comes from the test's vars ("message"). The output is the reply,
then one line per tool call and what Ledgerline holds after, so assertions can check the trajectory and the outcome,
and the viewer shows them. config.guards turns guards on (ledgerline.course.l6.guards): the red team's "after" target.
"""
import json
import os
import sys

sys.path.insert(0, os.environ.get("LEDGERLINE_PATH", "/course/ledgerline"))
from ledgerline.course.l6 import guards as G  # noqa: E402
from ledgerline.course.l6.agent import GOOD, Agent  # noqa: E402
from ledgerline.llm import LLM  # noqa: E402


def call_api(prompt, options, context):
    cfg = (options or {}).get("config") or {}
    v = (context or {}).get("vars") or {}
    if v.get("message") and prompt.startswith("You are Ask Northbridge"):
        system, msg = prompt, v["message"]          # the eval: the prompt is the system prompt under test
    else:
        system, msg = GOOD, (v.get("message") or prompt)   # the red team: the prompt is the attack
    on = cfg.get("guards") or []
    ag = Agent(system, guards=G.Guards(on) if on else None,
               llm_for=lambda m: LLM(m, cassette=cfg.get("cassette", "L6E_promptfoo"), mode="record", max_tokens=8192))
    try:
        rec = ag.turn(msg)
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    calls = "\n".join(f"[tool] {c['tool']}({json.dumps(c['args'])})" + (f" REFUSED by {c['refused_by']}" if c.get("refused_by") else "")
                      for c in rec["calls"])
    w = ag.writes()
    saved = (f"[ledgerline] saved: {len(w['requests'])} request(s), {len(w['messages'])} message(s), "
             f"{len(w['approvals'])} approval(s), {len(w['suppliers'])} supplier(s)")
    return {"output": f"{rec['reply']}\n\n{calls}\n{saved}",
            "tokenUsage": {"prompt": rec["tokens_in"], "completion": rec["tokens_out"], "total": rec["tokens_in"] + rec["tokens_out"]},
            "cost": rec["usd"], "metadata": {"guard_events": rec.get("guard_events", [])}}
