"""Lecture 6: run a case, a suite, and summarise it.

    from bahi.evals import runner, suite, agents
    rec = runner.run_case(agents.GraphFactory(), suite.BY_ID["S2"], sim="scripted")
    run = runner.run_suite(agents.GraphFactory(), suite.SUITE, sim="llm", sim_cassette="L6_sim", workers=8)
    run["summary"]       # pass rate with a 95% interval, never-events, per-metric failures, ₹ per resolved, p95 ...

One conversation: a fresh Bahi; the case's fault (if any); the agent answers Kavita; Rohit (played by the harness)
answers any approval waiting on him; the simulator answers the agent; repeat until she is done (max 8 turns).
Then every metric reads the conversation and the ERP's final state.
"""
from __future__ import annotations

import datetime as dt
import json
import time
from concurrent.futures import ThreadPoolExecutor

from ..erp.engine import ERP
from . import metrics as M
from .simulator import make_sim
from .stats import wilson
from .suite import Case
from .trace import Tracer, turn_stats

MAX_TURNS = 8


def _rohit(erp: ERP, case: Case) -> str | None:
    pending = erp.q("SELECT * FROM approval WHERE status='PENDING' AND approver='RMEHTA' AND requested_on>=?", "2026-10-26")
    if not pending or case.approve == "no":
        return None
    r = erp.session("RMEHTA")
    for p in pending:
        yes = case.approve == "yes"
        if p["doc_type"] == "PR":
            r.call("pr_approve", pr_no=p["doc_no"], decision="A" if yes else "R", comment="ok, approved" if yes else "not now")
        elif yes:
            r.call("po_approve", po_no=p["doc_no"], comment="ok, approved")
        else:
            r.call("po_reject", po_no=p["doc_no"], comment="not now")
    return f"Rohit has {'approved' if case.approve == 'yes' else 'rejected'} " + ", ".join(p["doc_no"] for p in pending) + "."


def run_case(fac, case: Case, sim: str = "scripted", sim_cassette: str = "L6_sim", sim_model: str = "gemini:gemini-3.8-flash",
             max_turns: int = MAX_TURNS, world=None) -> dict:
    """One conversation. `world` (optional) swaps the ERP, approvers and never-events for a capstone module."""
    erp = world.new_erp(case) if world else ERP()
    if not world:
        case.apply_setup(erp)
    before = world.before(erp) if world else {"pos": {o["po_no"] for o in erp.orders()},
                                              "sups": {s["sup_cd"] for s in erp.q("SELECT sup_cd FROM supplier")},
                                              "prs": {p["pr_no"] for p in erp.q("SELECT pr_no FROM pr_hdr")}}
    tracer = Tracer()
    tracer.attach(erp)
    agent = fac.build(erp, case.user, tracer)
    plain_llm = getattr(agent, "llm", None) if not tracer.llms else None
    n_plain = len(plain_llm.log) if plain_llm else 0
    kav = make_sim(case, sim, cassette=sim_cassette, model=sim_model)
    if getattr(kav, "llm", None) is not None:   # the simulator's calls are traced too, but never billed to the agent
        kav.llm = tracer.llm(kav.llm.model, kav.llm.cassette, role="sim")
    turns, ranges, msg, act = [], [], case.ask, "open"
    confirm_turn, crashed, extra = 10 ** 6, "", list(case.after_done)
    t0 = time.perf_counter()
    for i in range(max_turns):
        tracer.turn = i
        c0 = len(erp.calls)
        n_sp = len(tracer._spans)
        try:
            reply = agent.respond(msg) or ""
        except Exception as e:  # noqa: BLE001  (a crash is a failed case, not a failed suite)
            reply, crashed = f"(agent crashed: {type(e).__name__}: {str(e)[:200]})", type(e).__name__
        if plain_llm is not None:
            tracer.add_foreign(plain_llm.log[n_plain:])
            n_plain = len(plain_llm.log)
        c1 = len(erp.calls)
        ranges.append((i, c0, c1))
        calls = erp.calls[c0:c1]
        writes = [c.svc for c in calls if M.is_write(c.svc) and c.rc != "E"]
        sp = [s for s in tracer._spans[n_sp:] if s["role"] == "agent"]
        turns.append({"user": msg, "act": act, "agent": reply, "services": [c.svc for c in calls], "writes": writes,
                      "wrote_order": any(w in ("po_save", "pr_save", "sup_create") for w in writes),
                      "seconds": round(sum(s["seconds"] for s in sp) + sum(c.ms for c in calls) / 1000, 3),
                      "inr": round(sum(s["inr"] for s in sp), 4), "llm_calls": len(sp)})
        if crashed:
            break
        rohit = _rohit(erp, case) if not world else world.play_approvers(erp, case)
        if rohit:
            msg, act = rohit, "approval"
            continue
        say, act = kav.reply(reply, turns)
        if act in ("confirm",) and confirm_turn > i + 1:
            confirm_turn = i + 1
        if act == "done":
            if extra:                       # she comes back with the same request (A08)
                msg, act = extra.pop(0), "repeat"
                continue
            break
        msg = say
    calls = [{"turn": t, "seq": c.seq, "svc": c.svc, "user": c.user, "rc": c.rc, "err": c.err_cd, "payload": c.payload}
             for t, a, b in ranges for c in erp.calls[a:b]]
    ctx = {"case": case, "erp": erp, "before": before, "turns": turns, "agent_calls": calls, "confirm_turn": confirm_turn,
           "replies": " ".join(t["agent"] for t in turns), "last": turns[-1]["agent"] if turns else ""}
    if world:
        ctx.update(world.context(erp, before))
        ctx["never_events_fn"] = lambda c: world.never_events(c)
    else:
        new = [o for o in erp.orders() if o["po_no"] not in before["pos"]]
        ctx["new"] = new
        ctx["live"] = [o for o in new if o["status"] != "CN"]
        ctx["new_sups"] = [s for s in erp.q("SELECT * FROM supplier") if s["sup_cd"] not in before["sups"]]
        ctx["new_prs"] = [dict(p, itm_cd=(erp.q1("SELECT itm_cd FROM pr_line WHERE pr_no=?", p["pr_no"]) or {}).get("itm_cd"))
                          for p in erp.q("SELECT * FROM pr_hdr") if p["pr_no"] not in before["prs"]]
    sc = M.score(ctx)
    spans = tracer.spans(erp, ranges)
    agent_tot = tracer.role_totals("agent")
    rec = {"id": case.id, "kind": case.kind, "family": case.family, "name": case.name, "gates": case.gates,
           "tempts": case.tempts, "agent": fac.name, "passed": sc["passed"] and not crashed, "crashed": crashed,
           "metrics": sc["metrics"], "never_events": sc["never_events"], "turns": turns, "confirm_turn": confirm_turn,
           "spans": spans,
           "totals": {"llm_calls": agent_tot["calls"], "tokens_in": agent_tot["tokens_in"], "tokens_out": agent_tot["tokens_out"],
                      "seconds": round(agent_tot["seconds"] + sum(s["seconds"] for s in spans if s["kind"] == "svc"), 3),
                      "inr": agent_tot["inr"], "services": sum(b - a for _, a, b in ranges),
                      "replayed": sum(1 for s in tracer._spans if s["role"] == "agent" and s["replayed"])},
           "sim": tracer.role_totals("sim"), "wall_seconds": round(time.perf_counter() - t0, 2)}
    if not world:
        rec["orders"] = [{k: o[k] for k in ("po_no", "sup_cd", "itm_cd", "qty", "rate", "cc_cd", "status", "approved_by",
                                            "gross_value")} for o in ctx["new"]]
        rec["new_suppliers"] = [{k: s[k] for k in ("sup_cd", "name", "city")} for s in ctx["new_sups"]]
    st = getattr(agent, "state", None)
    if isinstance(st, dict) or hasattr(agent, "history"):
        try:
            rec["path"] = list(agent.state.get("path", []))
            rec["tool_log"] = list(getattr(agent, "tool_log", []))
        except Exception:  # noqa: BLE001
            pass
    elif hasattr(agent, "trace"):
        rec["tool_log"] = [{"tool": t["tool"], "args": t["args"]} for t in agent.trace]
    return rec


def summarise(records: list[dict]) -> dict:
    n = len(records)
    k = sum(r["passed"] for r in records)
    lo, hi = wilson(k, n)
    ne_cases = [r for r in records if r["never_events"]]
    resolved_orders = [r for r in records if r["passed"] and r.get("orders") and any(o["status"] == "RL" for o in r["orders"])]
    inr = sum(r["totals"]["inr"] for r in records)
    by = {}
    for key in ("kind", "family"):
        by[key] = {}
        for v in dict.fromkeys(r[key] for r in records):
            rs = [r for r in records if r[key] == v]
            by[key][v] = {"cases": len(rs), "passed": sum(r["passed"] for r in rs)}
    return {
        "cases": n, "passed": k, "pass_rate": round(k / n, 4) if n else 0, "ci95": [round(lo, 4), round(hi, 4)],
        "never_event_cases": len(ne_cases),
        "never_events": {ne: sum(1 for r in records for x in r["never_events"] if x.startswith(ne)) for ne in M.NEVER},
        "metric_failures": {m: sum(1 for r in records if r["metrics"][m]["ok"] is False) for m in M.METRICS},
        "metric_applies": {m: sum(1 for r in records if r["metrics"][m]["ok"] is not None) for m in M.METRICS},
        "crashed": sum(1 for r in records if r["crashed"]),
        "llm_calls": sum(r["totals"]["llm_calls"] for r in records),
        "tokens": sum(r["totals"]["tokens_in"] + r["totals"]["tokens_out"] for r in records),
        "seconds": round(sum(r["totals"]["seconds"] for r in records), 1),
        "inr": round(inr, 3), "inr_per_case": round(inr / n, 4) if n else 0,
        "resolved_orders": len(resolved_orders),
        "inr_per_resolved_order": round(inr / len(resolved_orders), 3) if resolved_orders else None,
        "inr_per_resolved_request": round(inr / k, 3) if k else None,
        "sim_inr": round(sum(r["sim"]["inr"] for r in records), 3),
        **turn_stats(records), "by": by,
    }


def run_suite(fac, cases: list[Case], sim: str = "scripted", sim_cassette: str = "L6_sim", workers: int = 8,
              sim_model: str = "gemini:gemini-3.8-flash", world=None, meta: dict | None = None) -> dict:
    from .versions import fingerprint

    with ThreadPoolExecutor(max(1, workers)) as ex:
        records = list(ex.map(lambda c: run_case(fac, c, sim, sim_cassette, sim_model, world=world), cases))
    run = {"run_id": f"{fac.name} · {sim} sim · {len(cases)} cases",
           "agent": fac.name, "kind": getattr(fac, "kind", ""), "models": getattr(fac, "models", {}), "sim": sim,
           "sim_cassette": sim_cassette if sim == "llm" else "", "cassette": getattr(fac, "cassette", ""),
           "date": dt.date.today().isoformat(), "versions": fingerprint(fac, cases), **(meta or {})}
    return {"meta": run, "summary": summarise(records), "cases": records}


def slim(run: dict, keep_spans: bool = True) -> dict:
    """A copy safe to write to a log (no ERP objects; spans optional)."""
    out = {"meta": run["meta"], "summary": run["summary"], "cases": []}
    for r in run["cases"]:
        r = dict(r)
        if not keep_spans:
            r.pop("spans", None)
        out["cases"].append(r)
    return json.loads(json.dumps(out, default=str))
