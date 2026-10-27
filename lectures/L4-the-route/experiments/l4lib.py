"""Shared helpers for the Lecture 4 experiments: the two agents, a runner for multi-step cases, and log export.

The two agents get the SAME model, the SAME intent tools (Lecture 3's CORE + EXTRA) and the SAME policy search.
Only the control differs: a free tool loop (the model decides every next step) or the control graph (code decides).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Callable

from bahi.agent.graph import GraphAgent
from bahi.agent.loop import ToolLoopAgent
from bahi.agent.memory import CompanyMemory
from bahi.agent.tools import CORE, EXTRA, IntentTools
from bahi.erp.engine import ERP
from bahi.llm import LLM, tool_schema
from bahi.scenarios import Scenario, check

MODEL = "gemini:gemini-3.8-flash"


class PolicyTool:
    """search_policy for the free loop, over the same company memory the graph uses (Lecture 2 stand-in)."""
    names = ["search_policy"]

    def __init__(self, mem: CompanyMemory | None = None):
        self.mem = mem or CompanyMemory()

    def schemas(self):
        return [tool_schema("search_policy", "Search the Purchase Policy. Returns the clauses that answer the question, "
                            "each with a citation such as 'Purchase Policy §6.2' to quote.",
                            {"question": {"type": "string"}}, ["question"])]

    def call(self, name, args):
        hits = self.mem.search(args.get("question") or args.get("query") or "", 3)
        return {"ok": True, "clauses": [{"cite": h["cite"], "text": h["text"]} for h in hits]}


class Belt:
    def __init__(self, *sets):
        self.sets = sets
        self.names = [n for s in sets for n in s.names]

    def schemas(self):
        return [x for s in self.sets for x in s.schemas()]

    def call(self, name, args):
        for s in self.sets:
            if name in s.names:
                return s.call(name, args)
        return {"ok": False, "error": f"Unknown tool {name}."}


def make_loop(cassette="L4_loop", model=MODEL):
    def make(erp, user):
        tools = Belt(IntentTools(erp.session(user), CORE + EXTRA), PolicyTool())
        return ToolLoopAgent(erp, user, llm=LLM(model, cassette=cassette), tools=tools)
    return make


def make_graph(cassette="L4_graph", model=MODEL, k=3):
    def make(erp, user):
        return GraphAgent(erp, user, llm=LLM(model, cassette=cassette), k=k)
    return make


# ----------------------------------------------------------------------------- multi-step cases
ASKS = re.compile(r"confirm|shall I|should I|would you like|do you want|go ahead", re.I)


@dataclass
class Case:
    id: str
    family: str                 # which of the six it varies, or "trap"
    name: str
    ask: str
    followups: list = field(default_factory=list)
    expect: Callable = None     # (ctx) -> (ok, note)
    gates: list = field(default_factory=list)   # gates (route_spec names) the right route opens
    approve: str = "yes"        # what Rohit does with an approval request: yes | no (never answers) | reject
    setup: Callable | None = None
    force: list = field(default_factory=list)   # messages sent even if the agent asked nothing


def run_case(make_agent, case: Case, max_turns: int = 7) -> dict:
    erp = ERP()
    if case.setup:
        case.setup(erp)
    before = {"pos": {o["po_no"] for o in erp.orders()}, "sups": {s["sup_cd"] for s in erp.q("SELECT sup_cd FROM supplier")}}
    agent = make_agent(erp, "KJOSHI")
    llm = agent.llm
    n0, c_start = len(llm.log), len(erp.calls)
    turns, msg, follow, forced = [], case.ask, list(case.followups), list(case.force)
    crashed = ""
    t0 = time.perf_counter()
    for _ in range(max_turns):
        c0 = len(erp.calls)
        try:
            reply = agent.respond(msg)
        except Exception as e:  # noqa: BLE001  (a crash is a failed case, not a failed experiment)
            reply, crashed = f"(agent crashed: {type(e).__name__}: {str(e)[:200]})", type(e).__name__
        calls = erp.calls[c0:]
        turns.append({"user": msg, "agent": reply, "services": [c.svc for c in calls],
                      "writes": [c.svc for c in calls if c.svc in WRITES and c.rc != "E"]})
        if crashed:
            break
        pending = erp.q("SELECT * FROM approval WHERE status='PENDING' AND approver='RMEHTA' AND requested_on>=?",
                        "2026-10-26")
        if pending and case.approve in ("yes", "reject"):
            r = erp.session("RMEHTA")
            for p in pending:
                if case.approve == "yes":
                    if p["doc_type"] == "PR":
                        r.call("pr_approve", pr_no=p["doc_no"], decision="A", comment="ok, approved")
                    else:
                        r.call("po_approve", po_no=p["doc_no"], comment="ok, approved")
                else:
                    if p["doc_type"] == "PR":
                        r.call("pr_approve", pr_no=p["doc_no"], decision="R", comment="not now")
                    else:
                        r.call("po_reject", po_no=p["doc_no"], comment="not now")
            verb = "approved" if case.approve == "yes" else "rejected"
            msg = f"Rohit has {verb} " + ", ".join(p["doc_no"] for p in pending) + "."
            continue
        if follow and reply and ("?" in reply[-300:] or ASKS.search(reply)):
            msg = follow.pop(0)
            continue
        if forced:
            msg = forced.pop(0)
            continue
        break
    _, ne, _ = check(Scenario(0, case.name, case.ask), erp, before, turns)
    new = [o for o in erp.orders() if o["po_no"] not in before["pos"]]
    live = [o for o in new if o["status"] != "CN"]
    new_sups = [s for s in erp.q("SELECT * FROM supplier") if s["sup_cd"] not in before["sups"]]
    ctx = {"erp": erp, "new": new, "live": live, "new_sups": new_sups, "turns": turns,
           "replies": " ".join(t["agent"] or "" for t in turns), "last": turns[-1]["agent"] if turns else "",
           "writes": [w for t in turns for w in t["writes"]]}
    ok, note = case.expect(ctx) if case.expect else (False, "no expectation")
    calls = llm.log[n0:]
    res = {"id": case.id, "family": case.family, "name": case.name, "gates": case.gates,
           "passed": bool(ok and not ne and not crashed), "ok": bool(ok), "never_events": ne, "note": note,
           "crashed": crashed, "turns": turns,
           "orders": [{k: o[k] for k in ("po_no", "sup_cd", "itm_cd", "qty", "rate", "cc_cd", "status", "approved_by",
                                         "gross_value")} for o in new],
           "new_suppliers": [{k: s[k] for k in ("sup_cd", "name", "city")} for s in new_sups],
           "model_calls": len(calls), "tokens_in": sum(r.tokens_in for r in calls),
           "tokens_out": sum(r.tokens_out for r in calls), "seconds": round(sum(r.seconds for r in calls), 2),
           "cost_inr": round(sum(r.cost_inr for r in calls), 4), "services": len(erp.calls) - c_start,
           "replayed": sum(1 for r in calls if r.replayed), "wall_seconds": round(time.perf_counter() - t0, 2)}
    res.update(agent_trace(agent))
    return res


def agent_trace(agent) -> dict:
    if isinstance(agent, GraphAgent):
        st = agent.state
        return {"agent": "graph", "tool_calls": len(agent.tool_log), "tool_log": agent.tool_log,
                "path": st.get("path", []), "decisions": st.get("decisions", []),
                "draft": {k: v for k, v in (st.get("draft") or {}).items() if v not in (None, "")},
                "history": agent.history()}
    return {"agent": "loop", "tool_calls": len(getattr(agent, "trace", [])),
            "tool_log": [{"step": t["step"], "tool": t["tool"], "args": t["args"], "result": t["result"][:600]}
                         for t in getattr(agent, "trace", [])]}


def run_many(make_agent, cases, workers=8):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(lambda c: run_case(make_agent, c), cases))


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=1, default=str, ensure_ascii=False))


from bahi.erp import procs as _p, services as _sv  # noqa: E402,F401  (register the services first)
from bahi.erp.engine import SERVICES as _S  # noqa: E402

WRITES = {n for n, s in _S.items() if s.kind == "write"}
