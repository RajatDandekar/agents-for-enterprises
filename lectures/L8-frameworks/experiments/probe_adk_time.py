"""Where do ADK's ~12 s per task go when the model replies instantly (replay)? Times T03 step by step.
Writes logs/adk_time.json. Run with --mode replay (no model cost)."""
import json
import logging
import os
import pathlib
import sys
import time

import httpx  # noqa: F401

from bahi.course.frameworks.adk import ADKPort
from bahi.course.frameworks.meter import Meter
from bahi.course.frameworks.openai_agents import AgentsSDKPort
from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox

LOGS = pathlib.Path(__file__).parent / "logs"
out = {}
for name, cls, cas in [("adk", ADKPort, "IND8_fw_adk"), ("openai_agents", AgentsSDKPort, "IND8_fw_openai_agents")]:
    for rep in range(2):
        m = Meter(cassette=cas).start()
        t0 = time.perf_counter()
        tb = Toolbox(ERP(), "KJOSHI")
        a = cls(tb, m, f"{name}-T03-KJOSHI")
        t1 = time.perf_counter()
        marks = []
        orig = m.complete

        def timed(tag, body, orig=orig, marks=marks):
            marks.append(("model call in", round(time.perf_counter() - t1, 3)))
            r = orig(tag, body)
            marks.append(("model call out", round(time.perf_counter() - t1, 3)))
            return r
        m.complete = timed
        reply = a.respond("How many days of 5-litre silicone gaskets do we have left?")
        t2 = time.perf_counter()
        calls = [(c["name"], c["ms"]) for c in a.srv.calls]
        out[f"{name}_{rep}"] = {"init_s": round(t1 - t0, 3), "respond_s": round(t2 - t1, 3), "marks": marks,
                                "mcp_calls": calls, "reply": reply[:120]}
        print(name, rep, out[f"{name}_{rep}"])
        m.stop()
(LOGS / "adk_time.json").write_text(json.dumps(out, indent=1))
sys.stdout.flush()
os._exit(0)
