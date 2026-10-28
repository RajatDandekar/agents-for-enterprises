"""Run each of the Studio's five templates on a fresh Rasoi with the Studio's own engine, then run it AGAIN on the
same Rasoi (does a re-run double-order?). Logs steps, time, outcomes, documents and messages.

    lectures/L6-the-studio/experiments/mrun.sh --script lectures/L6-the-studio/experiments/templates_fresh.py
Writes logs/templates_fresh.json. LLM and agent nodes use bahi.llm.LLM with the cassette L6v3_templates (auto mode:
recorded on the first run, replayed after), model gemini:gemini-3.8-flash.
"""
import json
import pathlib
import time

from bahi.experience.players import Players
from bahi.experience.studio.engine import Engine, Store
from bahi.experience.studio.templates import TEMPLATES, template
from bahi.llm import LLM

LOG = pathlib.Path(__file__).parent / "logs" / "templates_fresh.json"
CHAT = ["Do we have enough whistles (WHS-STD-01) for the next two weeks? If not, raise a purchase request for "
        "36,000 on cost centre PRD-07, needed by 9 November.", "Yes, raise it."]


def docs(erp):
    q = lambda sql: [dict(r) for r in erp.q(sql)]
    return {"pr": q("SELECT pr_no, status, cc_cd, need_dt FROM pr_hdr WHERE pr_no >= 'PR/2026/04417' ORDER BY pr_no"),
            "po": q("SELECT po_no, status, sup_cd, pr_no FROM po_hdr WHERE po_no >= 'PO/2026/01182' ORDER BY po_no"),
            "grn": q("SELECT * FROM grn_hdr ORDER BY 1") if erp.q1("SELECT name FROM sqlite_master WHERE name='grn_hdr'") else [],
            "messages": q("SELECT channel, recipient, subject, body FROM ntf_queue ORDER BY id")}


def summarise(run, seconds):
    nodes = []
    for n in sorted(run["workflow"]["nodes"], key=lambda n: (n.get("x", 0), n.get("y", 0))):
        r = run["nodes"][n["id"]]
        nodes.append({"id": n["id"], "type": n["type"], "title": n.get("title"), "status": r["status"],
                      "seconds": r.get("seconds"), "summary": r.get("summary"), "meta": r.get("meta"),
                      "inputs": r.get("inputs"), "output": r.get("output")})
    toks = [x["meta"] for x in nodes if x.get("meta")]
    return {"status": run["status"], "error": run.get("error"), "seconds": round(seconds, 3),
            "nodes_run": sum(1 for x in nodes if x["status"] not in ("pending", "skipped")),
            "nodes_skipped": sum(1 for x in nodes if x["status"] == "skipped"),
            "tokens": sum((m.get("tokens_in") or 0) + (m.get("tokens_out") or 0) for m in toks),
            "cost_inr": round(sum(m.get("cost_inr") or 0 for m in toks), 4),
            "waited_for": run.get("_waited"), "log": run["log"], "nodes": nodes}


def go(eng, wf, trig=None):
    t0 = time.perf_counter()
    run = eng.run_until_pause(eng.start(wf, trig or {}))
    waited = None
    if run["status"] == "waiting":
        waited = dict(run["waiting_for"])
        eng.approve(run, decision="approve")          # Rohit signs in his inbox, as himself
        run = eng.run_until_pause(run)
    run["_waited"] = waited
    return summarise(run, time.perf_counter() - t0)


out = {"_what": "each Studio template on a fresh Rasoi (bahi.experience.studio.engine.Engine), run twice on the "
                "same Rasoi; model gemini:gemini-3.8-flash, cassette L6v3_templates", "templates": {}}
for tid in TEMPLATES:
    players = Players()
    pid = players.join("L6 builder").pid
    eng = Engine(toolbox_for=lambda u, names=None: players.toolbox(pid, u, names), store=Store(), pid=pid,
                 llm_for=lambda model: LLM(model, cassette="L6v3_templates"))
    wf = template(tid)
    rec = {"name": wf["name"], "nodes": len(wf["nodes"]), "edges": len(wf["edges"]),
           "trigger": next(n["config"]["kind"] for n in wf["nodes"] if n["type"] == "trigger"),
           "problems": eng.validate(wf), "workflow": wf}
    if tid == "build-your-own-agent":
        turns = []
        for msg in CHAT:
            t0 = time.perf_counter()
            reply, run = eng.chat(wf, msg)
            turns.append({"user": msg, "reply": reply, **summarise(run, time.perf_counter() - t0)})
        rec["runs"] = turns
    else:
        rec["runs"] = [go(eng, wf), go(eng, template(tid))]
    rec["docs_after"] = docs(players.erp(pid))
    out["templates"][tid] = rec
    print(f"\n=== {wf['name']}  ({rec['trigger']}, {rec['nodes']} nodes) problems={rec['problems']}")
    for i, r in enumerate(rec["runs"]):
        print(f"  run {i + 1}: {r['status']} {r.get('error') or ''} · {r['nodes_run']} run, {r['nodes_skipped']} skipped"
              f" · {r['seconds']} s · {r['tokens']} tokens · ₹{r['cost_inr']} · waited={r['waited_for']}")
        for e in r["log"]:
            print(f"      {str(e.get('node')):>18} {str(e.get('event')):<8} {str(e.get('text'))[:120]}")
    d = rec["docs_after"]
    print("  docs:", [p["pr_no"] + ":" + p["status"] for p in d["pr"]], [p["po_no"] + ":" + p["status"] for p in d["po"]],
          len(d["grn"]), "GRN rows ·", len(d["messages"]), "messages")
LOG.write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
