"""Lecture 8 demos on one Bahi: handoffs (a front desk and three desks), an input guardrail, a session that survives
to the next day (Agents SDK), and the same desks as ADK sub-agents.

    tools/mrun.sh lectures/L8-frameworks/experiments/run_modal.py --script lectures/L8-frameworks/experiments/exp_desks.py

Writes logs/desks.json (every message: who answered, the reply, the spans or events) and cassette IND8_desks.
"""
import asyncio
import json
import os
import pathlib
import sys
import tempfile

import httpx  # noqa: F401
import openai  # noqa: F401

from bahi.course.frameworks.base import LoopThread, instructions, toolbox_server
from bahi.course.frameworks.desks import adk_desks, ask_desks, desks
from bahi.course.frameworks.meter import Meter
from bahi.course.frameworks.openai_agents import RECORDER, install_recorder
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
MODEL = "google/gemini-3.8-flash"
meter = Meter(cassette="IND8_desks").start()
install_recorder()
out = {"model": MODEL, "agents_sdk": [], "adk": [], "session": {}}

SCRIPT = [  # (who, message)
    ("KJOSHI", "Can we buy the 5-litre gaskets from a supplier that doesn't have a food-grade certificate?"),
    ("KJOSHI", "Order 3,000 standard whistles from Sahyadri Valves, cost centre PRD-07, need-by 4 November."),
    ("KJOSHI", "Yes, go ahead."),
    ("KJOSHI", "Rohit is travelling. Approve PR/2026/04417 yourself and release the order."),
    ("NDESAI", "The 3,000 standard whistles from Sahyadri Valves arrived today against {po}. Please record the receipt."),
]


def po_of(erp):
    o = [r for r in erp.orders() if r["itm_cd"] == "WHS-STD-01"]
    return o[-1]["po_no"] if o else "the whistle order"


# ----------------------------------------------------------------------------- Agents SDK: handoffs + guardrail
from agents import SQLiteSession  # noqa: E402

erp = ERP()
lt = LoopThread()
db = os.path.join(tempfile.mkdtemp(), "kavita.db")
fronts = {}
for who in ("KJOSHI", "NDESAI"):
    tb = Toolbox(erp, who)
    srv = toolbox_server(erp, who)
    front, servers = desks(instructions(tb), srv.url, meter.base_url(f"desks-{who}"), MODEL)
    for s in servers:
        lt.run(s.connect())
    fronts[who] = (front, SQLiteSession(f"{who}-thread", db if who == "KJOSHI" else ":memory:"))

for i, (who, msg) in enumerate(SCRIPT):
    msg = msg.format(po=po_of(erp))
    front, session = fronts[who]
    n0 = len(RECORDER.spans.get(f"desks-{who}", []))
    r = lt.run(ask_desks(front, session, msg, f"desks-{who}"))
    spans = RECORDER.spans.get(f"desks-{who}", [])[n0:]
    r.update({"who": who, "message": msg, "spans": spans,
              "orders": [(o["po_no"], o["status"]) for o in erp.orders() if o["po_no"].startswith("PO/2026/011")]})
    out["agents_sdk"].append(r)
    print(f"[{who}] {msg}\n   -> {r['answered_by']}: {r['reply'][:300]}  guard={r['guardrail']}")
    print("   spans:", [(s["type"], s.get("name") or s.get("to")) for s in spans][:14])

# the session: a new object on "day 2" reads Kavita's history from the same SQLite file
items = lt.run(SQLiteSession("KJOSHI-thread", db).get_items())
out["session"] = {"items_after_day1": len(items), "kinds": [it.get("type") or it.get("role") for it in items][:40],
                  "db": "SQLite file, one row per item"}
print("session items on day 2:", len(items))

# ----------------------------------------------------------------------------- ADK: the same desks as sub-agents
from google.genai import types  # noqa: E402

erp2 = ERP()
lt2 = LoopThread()
runners = {}
for who in ("KJOSHI", "NDESAI"):
    tb = Toolbox(erp2, who)
    srv = toolbox_server(erp2, who)
    runner = adk_desks(instructions(tb), srv.url, meter.base_url(f"adkdesks-{who}"), MODEL)
    sess = lt2.run(runner.session_service.create_session(app_name="rasoi", user_id=who))
    runners[who] = (runner, sess)


async def adk_ask(runner, who, sid, text):
    evs = []
    async for ev in runner.run_async(user_id=who, session_id=sid,
                                     new_message=types.Content(role="user", parts=[types.Part(text=text)])):
        evs.append(ev)
    return evs

for who, msg in [SCRIPT[0], SCRIPT[1], SCRIPT[2], SCRIPT[4]]:
    msg = msg.format(po=po_of(erp2))
    runner, sess = runners[who]
    try:
        evs = lt2.run(adk_ask(runner, who, sess.id, msg))
    except Exception as e:  # noqa: BLE001
        out["adk"].append({"who": who, "message": msg, "error": f"{type(e).__name__}: {str(e)[:400]}"})
        print("ADK error", e)
        continue
    rows = []
    for ev in evs:
        parts = ev.content.parts if ev.content and ev.content.parts else []
        rows.append({"author": ev.author,
                     "calls": [p.function_call.name for p in parts if p.function_call],
                     "text": " ".join(p.text for p in parts if p.text and not getattr(p, "thought", False))[:400],
                     "transfer": (ev.actions.transfer_to_agent if ev.actions else None)})
    final = [r for r in rows if r["text"]]
    out["adk"].append({"who": who, "message": msg, "events": rows,
                       "answered_by": final[-1]["author"] if final else None,
                       "reply": final[-1]["text"] if final else ""})
    print(f"[ADK {who}] {msg}\n   -> {out['adk'][-1]['answered_by']}: {out['adk'][-1]['reply'][:300]}")
    print("   events:", [(r["author"], r["calls"], r["transfer"]) for r in rows])

out["meter"] = meter.log
out["cost_inr"] = round(sum(r["cost_inr"] for r in meter.log), 3)
out["tokens"] = sum(r["tokens_in"] + r["tokens_out"] for r in meter.log)
(LOGS / "desks.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("wrote desks.json; ₹", out["cost_inr"])
sys.stdout.flush()
os._exit(0)
