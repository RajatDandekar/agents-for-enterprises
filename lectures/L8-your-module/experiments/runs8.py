"""Lecture 8 experiments. Every number on the L8 plates comes from the logs this script writes.

    modal run tools/modal_run.py --script lectures/L8-your-module/experiments/runs8.py --args "--what final"
    modal run tools/modal_run.py --script lectures/L8-your-module/experiments/runs8.py --args "--what leave"

final  Kavita's 20,000 gaskets through every piece, as three people use Ask Rasoi (+ the trust layer) on one Rasoi:
       Kavita asks about stock and policy and orders; Rohit approves in his own conversation; Kavita's order is made
       and released; Neha receives the goods in two lots. Logs every step with the lecture that built that piece.
leave  The HR leave kit's four scenarios on Ask Rasoi over MCP, with the reference toolbox scaffolded the way A4 asks
       (bahi.course.l8.scaffold), three runs each.
"""
import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from bahi.course.l7 import AskRasoi
from bahi.erp.engine import ERP
from bahi.llm import LLM

LOGS = pathlib.Path(__file__).parent / "logs"
LOGS.mkdir(exist_ok=True)
FLASH = "gemini:gemini-3.8-flash"  # bahi.llm routes it through OpenRouter when the direct key is out of credit


def dump(name, d):
    (LOGS / name).write_text(json.dumps(d, indent=1, default=str, ensure_ascii=False))
    print("wrote", name)


PIECE = {  # which lecture built the piece each step uses
    "user": "L1 the After: one sentence", "reply": "L2 the brain: the model writes the reply",
    "search_policy": "L3 the memory", "tool": "L4 the hands: a tool over MCP", "model": "L5 the loop",
    "trust": "L7 trust",
}


def final():
    erp = ERP()
    who = {u: AskRasoi(erp, u, llm=LLM(FLASH, cassette=f"L8v3_final_{u}"), trust=True) for u in ("KJOSHI", "RMEHTA", "NDESAI")}
    script = [
        ("KJOSHI", "How many 5-litre silicone gaskets do we have at Pune, and how many days will they last?"),
        ("KJOSHI", "Shakti Seals in Vadodara quotes ₹10.40. Can we buy the gaskets from them?"),
        ("KJOSHI", "Then reorder 20,000 from Deccan Polymers at the contract rate. Charge PRD-07, need-by 2 November."),
        ("KJOSHI", "Yes, go ahead."),
        ("RMEHTA", "What is waiting for my approval?"),
        ("RMEHTA", "Approve PR/2026/04417."),
        ("KJOSHI", "Rohit has approved PR/2026/04417."),
        ("NDESAI", "12,000 gaskets arrived from Deccan against PO/2026/01182. Record the goods receipt."),
        ("NDESAI", "Yes, record it."),
        ("NDESAI", "The other 8,000 have arrived now. Record them too."),
        ("NDESAI", "Yes."),
        ("KJOSHI", "What is the status of PO/2026/01182 now?"),
    ]
    rows = []
    for user, text in script:
        a = who[user]
        n0 = len(a.trace)
        reply = a.respond(text)
        steps = a.trace[n0:]
        rows.append({"user": user, "text": text, "reply": reply, "steps": steps,
                     "tokens": sum(s.get("tokens_in", 0) + s.get("tokens_out", 0) for s in steps if s["kind"] == "model"),
                     "cost_inr": round(sum(s.get("cost_inr", 0) for s in steps if s["kind"] == "model"), 4),
                     "model_s": round(sum(s.get("seconds", 0) for s in steps if s["kind"] == "model"), 2)})
        print(f"\n{user}: {text}\nASK RASOI: {reply}\n  tools: {[s['tool'] for s in steps if s['kind'] == 'tool']}")
    po = erp.orders(**{"h.po_no": "PO/2026/01182"})
    grns = erp.q("SELECT * FROM grn_hdr") if erp.q1("SELECT name FROM sqlite_master WHERE name='grn_hdr'") else []
    stock = erp.q("SELECT * FROM stock WHERE itm_cd='GSK-SIL-05L'")
    out = {"model": FLASH, "turns": rows, "order": po[0] if po else None, "grns": grns, "stock": stock,
           "requests": erp.q("SELECT pr_no,status,approved_by,raised_by,est_value FROM pr_hdr WHERE pr_no='PR/2026/04417'"),
           "trust_events": {u: a.trust.events for u, a in who.items()},
           "users_seen": sorted({c.user for c in erp.calls}),
           "totals": {"tokens": sum(r["tokens"] for r in rows), "cost_inr": round(sum(r["cost_inr"] for r in rows), 3),
                      "model_s": round(sum(r["model_s"] for r in rows), 1),
                      "model_calls": sum(1 for r in rows for s in r["steps"] if s["kind"] == "model"),
                      "tool_calls": sum(1 for r in rows for s in r["steps"] if s["kind"] == "tool")}}
    print(json.dumps({k: out[k] for k in ("order", "grns", "stock", "requests", "users_seen", "totals")}, indent=1, default=str))
    for a in who.values():
        a.close()
    dump("final_demo.json", out)


def leave(reps: int = 3):
    import tempfile

    from bahi.course.l8 import leave_agent, scaffold
    from bahi.modules._kit import load, run_module_scenario
    from bahi.modules._toolbox import lint_folder

    folder = pathlib.Path(tempfile.mkdtemp()) / "my_module_tools"
    names = scaffold(folder)
    lint = lint_folder(folder, "hr_leave")
    print("scaffolded", names, "lint:", lint or "clean")
    _, S, _ = load("hr_leave")

    def job(sc, rep):
        keep = []
        cas = "L8v3_leave" + ("" if rep == 1 else f"_r{rep}")
        r = run_module_scenario(leave_agent(FLASH, cas, folder, keep=keep), "hr_leave", sc)
        d = r.__dict__
        d["rep"] = rep
        if keep:
            d["trace"] = keep[0].trace
            d["model_calls"] = sum(1 for s in keep[0].trace if s["kind"] == "model")
            keep[0].close()
        return d

    # One call before the threads: if the direct key is out of credit, bahi.llm switches to OpenRouter here, once,
    # instead of several threads hitting the 402 at the same moment (only the first of them is re-routed).
    LLM(FLASH, cassette="L8v3_warmup", mode="live").chat([{"role": "user", "content": "Say OK."}])
    jobs = [(sc, rep) for rep in range(1, reps + 1) for sc in S.SCENARIOS]
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(lambda x: job(*x), jobs))
    for d in rows:
        print(d["rep"], d["scenario"], d["passed"], d["never_events"], d["notes"], (d["turns"][-1]["agent"] or "")[:160])
    dump("leave_askrasoi.json", {"model": FLASH, "tools": names, "lint": lint,
                                 "tool_sources": {n: (folder / n / "tool.json").read_text() for n in names},
                                 "results": rows,
                                 "summary": {"passed": sum(d["passed"] for d in rows), "cases": len(rows),
                                             "never_events": sum(len(d["never_events"]) for d in rows),
                                             "cost_inr": round(sum(d["cost_inr"] for d in rows), 3),
                                             "per_scenario": {sc.id: sum(d["passed"] for d in rows if d["scenario"] == sc.id)
                                                              for sc in S.SCENARIOS}}})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", default="final")
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    t0 = time.perf_counter()
    if a.what == "final":
        final()
    if a.what == "leave":
        leave(a.reps)
    print(f"done in {time.perf_counter() - t0:.0f} s")
