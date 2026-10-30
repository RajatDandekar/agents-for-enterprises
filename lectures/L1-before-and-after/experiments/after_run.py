"""Lecture 1 v4 (Northbridge Cycles): the After, measured. Ask Northbridge does the same missions as the Before, one sentence each.

Ask Northbridge here = gemini-3.8-flash as the orchestrator + the course toolbox (ledgerline/toolbox, 15 tools) discovered over MCP
(ledgerline.toolbox.mcp), each person with their own Ask Northbridge bound to their own Ledgerline session (ledgerline.course.l1.AskNorthbridge).
The person's answers to Ask Northbridge's questions follow fixed rules (ledgerline.course.l1.answer), so a replay is identical.
Recorded into cassette L1v4_after; the notebook NB1 replays it with no key.

How the After is counted, the way the Experience's /after page counts it:
  messages    every message the person sent (typed sentences + taps)
  taps        "Yes, go ahead." answers to a preview: in the app that is one tap on the Yes chip, nothing typed
  typed       the other messages: the mission sentence and any answer with content ("Charge it to PRD-07 ...")
  seconds     the model's and the tools' wall time for the mission (the person's reading time is not included)

    sh tools/mrun.sh tools/modal_run.py --script lectures/L1-before-and-after/experiments/after_run.py --mode auto
    sh tools/mrun.sh tools/modal_run.py --script lectures/L1-before-and-after/experiments/after_run.py --mode replay
-> logs/after_run.json (record/auto) or logs/after_run_replay.json (replay: same replies, wall times near zero)
"""
import json
import os
import pathlib
import time

from ledgerline.course.l1 import MISSIONS, play_missions
from ledgerline.erp.engine import ERP
from ledgerline.llm import PRICES

OUT = pathlib.Path(__file__).parent / "logs"
OUT.mkdir(exist_ok=True)
CASSETTE = "L1v4_after"
YES = "Yes, go ahead."

erp = ERP()
agents = {}
t0 = time.perf_counter()
log = play_missions(erp, agents=agents)
wall = round(time.perf_counter() - t0, 1)

for m in log:
    m["user_turns"] = len(m["turns"])
    m["taps"] = sum(t["user"] == YES for t in m["turns"])
    m["typed_messages"] = m["user_turns"] - m["taps"]
    typed = [t["user"] for t in m["turns"] if t["user"] != YES]
    m["words_typed"] = sum(len(x.split()) for x in typed)
    m["chars_typed"] = sum(len(x) for x in typed)
    m["tool_calls"] = len(m["cards"])
    m["tool_errors"] = sum(1 for c in m["cards"] if isinstance(c["result"], dict) and c["result"].get("ok") is False)
    m["seconds"] = round(sum(t["seconds"] for t in m["turns"]), 1)
    print(f"\n=== {m['id']} ({m['who']}) done={m['done']} msgs={m['user_turns']} taps={m['taps']} tools={m['tool_calls']} {m['seconds']}s")
    for t in m["turns"]:
        print("  >", t["user"])
        print("    tools:", t["tools"])
        print("  <", (t["reply"] or "").replace("\n", " / ")[:500])

pr = erp.q("SELECT pr_no, status, cc_cd, est_value, approved_by FROM pr_hdr WHERE raised_on >= '2026-10-26'")
po = erp.q("SELECT po_no, status, cc_cd, tax_cd, basic_value, gross_value, approved_by, warn_cd FROM po_hdr WHERE created_on >= '2026-10-26'")
grn = erp.q("SELECT h.grn_no, h.po_no, l.qty, h.received_by, h.remarks FROM grn_hdr h JOIN grn_line l ON l.grn_no=h.grn_no")
sup = erp.q("SELECT sup_cd, name FROM supplier WHERE name LIKE '%Brightcell%'")
stock = erp.q1("SELECT on_hand, on_order FROM stock WHERE itm_cd='BAT-500' AND whs_cd='WH-MAN-STR'")


def usd(a):
    """Model cost in USD from llm.PRICES (assumed list prices), per call so a provider change is counted right."""
    tot = 0.0
    for r in a.llm.log:
        p = PRICES.get(r.model.split(":", 1)[-1].split("/")[-1])
        if p:
            tot += (r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6
    return round(tot, 5)


llm = {}
for u, a in agents.items():
    t = a.llm.totals()
    llm[u] = {"calls": t["calls"], "tokens_in": t["tokens_in"], "tokens_out": t["tokens_out"], "seconds": t["seconds"],
              "cost_usd": usd(a), "replayed": sum(1 for r in a.llm.log if r.replayed)}
M = [m for m in log if m["id"] != "brightcell"]
summary = {"missions": len(M), "all_done": all(m["done"] for m in M),
           "messages": sum(m["user_turns"] for m in M), "taps": sum(m["taps"] for m in M),
           "typed_messages": sum(m["typed_messages"] for m in M), "chars_typed": sum(m["chars_typed"] for m in M),
           "words_typed": sum(m["words_typed"] for m in M), "tool_calls": sum(m["tool_calls"] for m in M),
           "tool_errors": sum(m["tool_errors"] for m in M), "seconds": round(sum(m["seconds"] for m in M), 1),
           "screens_opened": 0, "codes_typed": sum(x.count("PO/") + x.count("PRD-") for m in M for t in m["turns"]
                                                    for x in [t["user"]]),
           "note": "the five missions of the Before (stock, request, approve, order, two receipts); the Brightcell question is extra"}
res = {"what": "Ask Northbridge (gemini-3.8-flash orchestrator + toolbox over MCP) doing the Before's missions",
       "model": "gemini:gemini-3.8-flash", "cassette": CASSETTE, "llm_mode": os.environ.get("LEDGER_LLM_MODE"),
       "wall_seconds": wall, "summary": summary,
       "tools_discovered_over_mcp": agents["ECLARKE"].tools.names,
       "missions": log, "ledgerline_after": {"pr": pr, "po": po, "grn": grn, "brightcell_registered": sup, "stock_man": stock},
       "llm_totals_by_user": llm, "cost_usd_total": round(sum(v["cost_usd"] for v in llm.values()), 5),
       "wire_sample": agents["ECLARKE"].client.wire[:3]}
# a replay proves the cassette; it must not overwrite the recorded run's real timings
name = "after_run_replay.json" if os.environ.get("LEDGER_LLM_MODE") == "replay" else "after_run.json"
(OUT / name).write_text(json.dumps(res, indent=1, default=str, ensure_ascii=False))
print("\nLedgerline after:", json.dumps(res["ledgerline_after"], default=str, indent=1))
print("summary:", json.dumps(summary))
print("LLM:", llm, "wall", wall, "cost_usd", res["cost_usd_total"])
for a in agents.values():
    a.close()
