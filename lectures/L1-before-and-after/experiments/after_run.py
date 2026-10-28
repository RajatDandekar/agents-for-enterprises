"""Lecture 1 v3: the After, measured. Ask Rasoi does the same missions as the Before, one sentence each.

Ask Rasoi here = gemini-3.8-flash as the orchestrator + the course toolbox (bahi/toolbox, 15 tools) discovered over MCP
(bahi.toolbox.mcp), each person with their own Ask Rasoi bound to their own Bahi session (bahi.course.l1.AskRasoi).
The person's answers to Ask Rasoi's questions follow fixed rules (bahi.course.l1.answer), so a replay is identical.
Recorded into cassette L1v3_after; the notebook NB1 replays it with no key.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L1-before-and-after/experiments/after_run.py --mode auto
-> logs/after_run.json
"""
import json
import pathlib
import time

from bahi.course.l1 import MISSIONS, play_missions
from bahi.erp.engine import ERP

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)

erp = ERP()
agents = {}
t0 = time.perf_counter()
log = play_missions(erp, agents=agents)
wall = round(time.perf_counter() - t0, 1)

for m in log:
    m["user_turns"] = len(m["turns"])
    m["words_typed"] = sum(len(t["user"].split()) for t in m["turns"])
    m["chars_typed"] = sum(len(t["user"]) for t in m["turns"])
    m["tool_calls"] = len(m["cards"])
    m["seconds"] = round(sum(t["seconds"] for t in m["turns"]), 1)
    print(f"\n=== {m['id']} ({m['who']}) done={m['done']} turns={m['user_turns']} tools={m['tool_calls']} {m['seconds']}s")
    for t in m["turns"]:
        print("  >", t["user"])
        print("    tools:", t["tools"])
        print("  <", (t["reply"] or "").replace("\n", " / ")[:500])

pr = erp.q("SELECT pr_no, status, cc_cd, est_value, approved_by FROM pr_hdr WHERE raised_on >= '2026-10-26'")
po = erp.q("SELECT po_no, status, cc_cd, tax_cd, gross_value, approved_by, warn_cd FROM po_hdr WHERE created_on >= '2026-10-26'")
grn = erp.q("SELECT h.grn_no, h.po_no, l.qty, h.received_by FROM grn_hdr h JOIN grn_line l ON l.grn_no=h.grn_no")
sup = erp.q("SELECT sup_cd, name FROM supplier WHERE name LIKE '%Shakti%'")
stock = erp.q1("SELECT on_hand, on_order FROM stock WHERE itm_cd='GSK-SIL-05L' AND whs_cd='WH-PUN-STR'")
llm = {u: a.llm.totals() for u, a in agents.items()}
res = {"what": "Ask Rasoi (gemini-3.8-flash orchestrator + toolbox over MCP) doing the Before's missions",
       "model": "gemini:gemini-3.8-flash", "cassette": "L1v3_after", "wall_seconds": wall,
       "tools_discovered_over_mcp": agents["KJOSHI"].tools.names,
       "missions": log, "bahi_after": {"pr": pr, "po": po, "grn": grn, "shakti_registered": sup, "stock_pun": stock},
       "llm_totals_by_user": llm,
       "wire_sample": agents["KJOSHI"].client.wire[:3]}
(OUT / "after_run.json").write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
print("\nBahi after:", json.dumps(res["bahi_after"], default=str, indent=1))
print("LLM:", llm, "wall", wall)
for a in agents.values():
    a.close()
