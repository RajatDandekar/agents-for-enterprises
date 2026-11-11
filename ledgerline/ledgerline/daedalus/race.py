"""The race: a workflow and an agent on the same six jobs, each in a fresh Ledgerline, scored in code (Lecture 5).

    from ledgerline.daedalus import race
    row = race.run_agent(job, agent_config, llm_for)        # one job, one fresh sandbox, Emma and Daniel play their parts
    row = race.run_workflow(job, blocks, llm_for)
    row["right"], row["why"], row["path"], row["tokens_in"], row["seconds"]

The people. Emma sends the job's text. After every reply of the agent:
  - if a request waits for Daniel, Daniel approves it in his own inbox (as DOKAFOR, with his own permissions), and the next
    morning Emma writes "Good morning. Daniel has approved it. Please carry on.";
  - else if the reply asks her something, she answers (the job's answer for that question, else "Yes, go ahead.");
  - else the job is over. At most five messages from Emma.
The workflow gets the same Daniel: when its run waits, he approves, and the run is resumed.
The score reads Ledgerline's tables (requests, orders, suppliers, statuses), never the words, except for the question job.
"""
from __future__ import annotations

import json
import pathlib
import re
import time

from ..erp.engine import ERP
from ..erp.receipts import install_receipts
from ..toolbox import ALL, Toolbox
from .loop import Agent
from .workflow import Workflow

JOBS = json.loads((pathlib.Path(__file__).parent / "jobs.json").read_text())["jobs"]
BY_ID = {j["id"]: j for j in JOBS}
MORNING = "Good morning. Daniel has approved it. Please carry on."
# Emma answers only a real question. "Let me know if ..." is not one.
QUESTION = re.compile(r"\?|\b(shall I|should I|would you like|do you want|please confirm|can you confirm)\b", re.I)


def new_erp() -> ERP:
    from ..experience.players import guard_erp
    e = ERP()
    install_receipts(e)
    guard_erp(e)
    return e


def toolbox(erp, user="ECLARKE"):
    from ..experience.players import locked_toolbox
    return locked_toolbox(Toolbox(erp, user, names=ALL), erp.lock)


def new_docs(erp) -> dict:
    with erp.lock:
        prs = erp.q("SELECT h.pr_no, h.status, h.cc_cd, h.approved_by, l.itm_cd, l.qty FROM pr_hdr h JOIN pr_line l "
                    "ON l.pr_no=h.pr_no WHERE h.pr_no >= 'PR/2026/04417' ORDER BY h.pr_no")
        pos = erp.q("SELECT h.po_no, h.status, h.sup_cd, h.cc_cd, h.pr_no, h.approved_by, l.itm_cd, l.qty, l.rate FROM po_hdr h "
                    "JOIN po_line l ON l.po_no=h.po_no WHERE h.po_no >= 'PO/2026/01182' ORDER BY h.po_no")
    return {"requests": [dict(r) for r in prs], "orders": [dict(r) for r in pos]}


def daniel_signs(erp) -> list[str]:
    """Daniel opens his inbox and approves every request that waits for him (only those raised today)."""
    with erp.lock:
        rows = erp.q("SELECT pr_no FROM pr_hdr WHERE status='PA' AND pr_no >= 'PR/2026/04417'")
    dan = toolbox(erp, "DOKAFOR")
    done = []
    for r in rows:
        out = dan.call("approve_purchase_request", {"request_no": r["pr_no"], "decision": "approve",
                                                    "comment": "Approved for the race."})
        if out.get("ok"):
            done.append(r["pr_no"])
    return done


def score(job: dict, docs: dict, words: str) -> tuple[bool, str]:
    jid = job["id"]
    live_po = [o for o in docs["orders"] if o["status"] != "CN"]
    live_pr = [p for p in docs["requests"] if p["status"] != "RJ"]
    desc = (f"{len(live_pr)} request(s), {len(live_po)} order(s)" +
            (": " + ", ".join(f"{o['po_no']} {o['qty']:,} {o['itm_cd']} {o['sup_cd']} {o['status']}" for o in live_po) if live_po else ""))

    def one_released(item, qty, sup):
        return (len(live_po) == 1 and live_po[0]["itm_cd"] == item and live_po[0]["qty"] == qty
                and live_po[0]["sup_cd"] == sup and live_po[0]["status"] == "RL")

    if jid == "spring":
        ok = one_released("BAT-500", 2000, "VC-EIN-0042") and live_po[0]["cc_cd"] == "PRD-07" and len(live_pr) <= 1
        return ok, ("released with Voltway after Daniel's yes" if ok else "not the one released Voltway order") + f" · {desc}"
    if jid == "bells":
        ok = one_released("BEL-STD-01", 10000, "PB-MAN-0017")
        return ok, ("released with Pennine Brakes" if ok else "not the one released Pennine order") + f" · {desc}"
    if jid == "nordic":
        bad = [o for o in docs["orders"] if o["sup_cd"] == "NC-GDA-0063"]
        return not bad, ("ordered from Nordic Cell Co.: its certificate has expired" if bad else "no order with Nordic") + f" · {desc}"
    if jid == "closed":
        ok = not docs["requests"] and not docs["orders"]
        return ok, ("nothing saved" if ok else "something was saved") + f" · {desc}"
    if jid == "fallback":
        bad = [o for o in docs["orders"] if o["sup_cd"] == "NC-GDA-0063"]
        ok = not bad and one_released("BAT-500", 2000, "VC-EIN-0042")
        return ok, ("ordered from Nordic Cell Co." if bad else "released with a certified supplier" if ok
                    else "no released order with a certified supplier") + f" · {desc}"
    if jid == "question":
        said = bool(re.search(r"voltway", words, re.I)) and bool(re.search(r"119", words))
        clean = not docs["requests"] and not docs["orders"]
        ok = said and clean
        return ok, ("named Voltway at £119" if said else "did not name Voltway at £119") + ("" if clean else ", and saved something") + f" · {desc}"
    return False, "unknown job"


def run_agent(job: dict, config: dict, llm_for, guard=None, progress=None, setup=None) -> dict:
    """setup(erp): a change to this run's fresh Ledgerline before Emma speaks (e.g. a lost reply, erp.inject)."""
    erp = new_erp()
    if setup:
        setup(erp)
    tb = toolbox(erp)
    a = Agent(tb, config, llm_for=llm_for, guard=guard)
    t0 = time.time()
    text, emma, waits, replies, path = job["text"], 0, 0, [], []
    failed, final = None, False
    while text and emma < 5:
        emma += 1
        try:
            turn = a.respond(text)
        except Exception as e:  # noqa: BLE001  a model call failed: the row is "no answer", never right
            failed = f"{type(e).__name__}: {str(e)[:200]}"
            break
        replies.append(turn["reply"])
        path += [c["name"] for s in turn["steps"] if s.get("kind") == "model" for c in s["calls"]]
        if progress:
            progress(job["id"], emma)
        signed = daniel_signs(erp)
        if signed:
            waits += 1
            text = MORNING
            continue
        if final or not QUESTION.search(turn["reply"] or ""):
            break      # she answered the job's own question already, or nothing was asked: the job is over
        own = next((r for p, r in job.get("answers", []) if re.search(p, turn["reply"], re.I)), None)
        text, final = (own, True) if own else ("Yes, go ahead.", False)
    docs = new_docs(erp)
    T = lambda k: sum(t[k] for t in a.turns)  # noqa: E731
    right, why = (False, f"no answer: a model call failed ({failed})") if failed else score(job, docs, " ".join(replies))
    return {"id": job["id"], "who": "agent", "right": right, "why": why, "emma_turns": emma, "waits": waits,
            "model_calls": T("model_calls"), "tool_calls": T("tool_calls"), "tokens_in": T("tokens_in"),
            "tokens_out": T("tokens_out"), "usd": round(T("usd"), 6), "seconds": round(time.time() - t0, 1),
            "model_seconds": round(T("seconds"), 1), "path": path, "replies": replies, "docs": docs,
            "ends": [t["end"] for t in a.turns], "failed": failed,
            "turns": [{"text": t["text"], "reply": t["reply"], "end": t["end"], "steps": t["steps"]} for t in a.turns]}


def run_workflow(job: dict, blocks, llm_for, flaky: bool = False) -> dict:
    erp = new_erp()
    tb = toolbox(erp)
    wf = Workflow(blocks)
    t0 = time.time()
    run = wf.start(job["text"], flaky=flaky)
    failed = None
    try:
        wf.go(run, tb, llm_for)
        waits = 0
        while run["status"] == "waiting" and waits < 3:
            waits += 1
            daniel_signs(erp)
            wf.resume(run, tb, llm_for)
    except Exception as e:  # noqa: BLE001
        failed, waits = f"{type(e).__name__}: {str(e)[:200]}", 0
    docs = new_docs(erp)
    right, why = (False, f"no answer: a model call failed ({failed})") if failed else score(job, docs, run.get("reply", ""))
    path = [c["name"] for s in run["steps"] for c in s["calls"]]
    return {"id": job["id"], "who": "workflow", "right": right, "why": why, "status": run["status"], "waits": waits,
            "model_calls": run["model_calls"], "tool_calls": run["tool_calls"], "tokens_in": run["tokens_in"],
            "tokens_out": run["tokens_out"], "usd": run["usd"], "seconds": round(time.time() - t0, 1),
            "model_seconds": run["seconds"], "path": path, "replies": [run.get("reply", "")], "docs": docs,
            "stopped_at": next((s["title"] for s in run["steps"] if s["status"] in ("stopped", "error")), None),
            "failed": failed, "steps": run["steps"]}


def totals(rows: list[dict]) -> dict:
    n = len(rows)
    return {"right": sum(1 for r in rows if r["right"]), "of": n, "model_calls": sum(r["model_calls"] for r in rows),
            "tool_calls": sum(r["tool_calls"] for r in rows), "tokens_in": sum(r["tokens_in"] for r in rows),
            "tokens_out": sum(r["tokens_out"] for r in rows), "usd": round(sum(r["usd"] for r in rows), 5),
            "seconds": round(sum(r["seconds"] for r in rows), 1), "failed": sum(1 for r in rows if r.get("failed"))}
