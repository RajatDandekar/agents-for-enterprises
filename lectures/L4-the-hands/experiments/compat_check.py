"""Backwards-compatibility check for the Lecture 4 toolbox changes (run on Modal, same image as the notebook replays).

    tools/mrun.sh tools/modal_run.py --script lectures/L4-the-hands/experiments/compat_check.py --mode replay

1. NB1's After: the six missions replay from cassette L1v4_after through build_toolbox_server (default tool set),
   so the tool definitions and tool results the model saw must be byte-identical to the recorded run.
2. The default toolbox is still the 15 tools, in the same order, with the same LLM-facing schemas (hash).
Writes logs/compat_check.json (appends one entry per run, labelled by --label).
"""
import hashlib
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("LEDGER_LLM_MODE", "replay")
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "ledgerline"))

import fastmcp  # noqa: E402
import mcp  # noqa: E402

from ledgerline.course.l1 import MISSIONS, play_mission  # noqa: E402
from ledgerline.erp.engine import ERP  # noqa: E402
from ledgerline.llm import ReplayMiss  # noqa: E402
from ledgerline.mcp_server import MCPClient, MCPClientTools  # noqa: E402
from ledgerline.toolbox import Toolbox  # noqa: E402
from ledgerline.toolbox.mcp import build_toolbox_server  # noqa: E402

label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "run"
out = {"label": label, "at": time.strftime("%Y-%m-%d %H:%M:%S"), "fastmcp": fastmcp.__version__,
       "mcp": getattr(mcp, "__version__", None)}

# 2. the default tool set and the schemas the model sees
tb = Toolbox(ERP(), "ECLARKE")
out["default_tools"] = tb.names
out["toolbox_schema_sha"] = hashlib.sha256(json.dumps(tb.schemas(), sort_keys=True).encode()).hexdigest()[:16]
c = MCPClient(build_toolbox_server(ERP(), "ECLARKE"))
mt = MCPClientTools(c)
out["mcp_schema_sha"] = hashlib.sha256(json.dumps(mt.schemas(), sort_keys=True).encode()).hexdigest()[:16]
out["mcp_tools"] = mt.names
c.close()

# 1. NB1's After, in replay
erp = ERP()
agents, missions = {}, []
try:
    for m in MISSIONS:
        r = play_mission(erp, agents, m)
        missions.append({"mission": m.get("id") or m.get("title"), "done": r.get("done")})
    out["nb1_after"] = {"replayed": True, "missions": missions}
except ReplayMiss as e:
    out["nb1_after"] = {"replayed": False, "error": str(e)[:300], "missions": missions}
for a in agents.values():
    a.close()
print(json.dumps(out, indent=1))
p = HERE / "logs" / "compat_check.json"
hist = json.loads(p.read_text()) if p.exists() else []
hist.append(out)
p.write_text(json.dumps(hist, indent=1))
