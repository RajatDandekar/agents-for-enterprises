"""Demo day (Lecture 12): the change each module must absorb, and the hidden test the grader runs.

Each kit has `modules/<name>/demo_change.py` (announced at the end of Lecture 11; `CHANGE.md` beside it is the
client's announcement). A demo_change module provides:

    CHANGE      dict: module, kind ("policy" | "variant"), id, title, announcement (the client's words), effective
    DOC_NAME    file name of the new or replacing document (or None)
    DOC         its text: the student adds it to their module's documents, and to their retrieval corpus
    apply(erp)  the data side of the change (new seed rows, a changed limit ...). Idempotent. The grader calls it in
                the hidden scenario's setup, and on top of the kit's own four scenarios to prove nothing else broke.
    SCENARIO    the hidden scenario (id 5): Scenario(5, name, ask, followups, user=..., setup=apply)
    check(sc, erp, before, turns) -> (passed, never_events, notes)   code only; the kit's never-events still apply
    OLD         scripted steps: the kit's careful reference behaviour BEFORE the change (it must fail the hidden test)
    NEW         scripted steps: the careful behaviour AFTER the change (it must pass: the change is fair)
    NAIVE, NAIVE_RUN_AS   the careless run (it must be caught)

Grading a student's agent (10 points of the /100):

    from demo_day import load_change, run_change
    ch = load_change("hr_leave")
    res = run_change(make_agent, "hr_leave", ch)      # res.passed, res.never_events, res.notes, res.turns

`modules/` is not a package: load_change() imports demo_change.py by path, so this works from anywhere.
Everything here is fictional, like the rest of Bahi.
"""
from __future__ import annotations

import importlib.util
import os
import re
import time

from bahi.erp import procs as _p, services as _s  # noqa: F401  (purchasing's services registered first)
from bahi.erp.engine import ERP
from bahi.modules._kit import Result, Scenario, load, write_svcs

HERE = os.path.dirname(os.path.abspath(__file__))


def load_change(module: str):
    path = os.path.join(HERE, module, "demo_change.py")
    spec = importlib.util.spec_from_file_location(f"demo_change_{module}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_change(make_agent, module: str, ch, max_turns: int = 6, also: tuple = ()) -> Result:
    """run_module_scenario, but scored by the change's own check(). Approvers are played by the kit's
    play_approvers (whoever a document waits on decides it), follow-ups answer the agent's questions."""
    _, S, _ = load(module)
    sc: Scenario = ch.SCENARIO
    erp = ERP(modules=[module, *also])
    if sc.setup:
        sc.setup(erp)
    before = S.before(erp)
    agent = make_agent(erp, sc.user)
    llm = getattr(agent, "llm", None)
    n0 = len(llm.log) if llm else 0
    t0 = time.perf_counter()
    turns, msg, follow = [], sc.ask, list(sc.followups)
    writes_set = write_svcs()
    play = getattr(ch, "play_approvers", None) or S.play_approvers
    for _ in range(max_turns):
        c0 = len(erp.calls)
        reply = agent.respond(msg)
        calls = erp.calls[c0:]
        turns.append({"user": msg, "agent": reply, "services": [c.svc for c in calls],
                      "writes": [c.svc for c in calls if c.svc in writes_set and c.rc != "E"],
                      "users": sorted({c.user for c in calls})})
        played = play(erp, sc) if sc.approve else None
        if played:
            msg = played
            continue
        if follow and reply and ("?" in reply[-200:] or re.search(r"confirm|shall I|should I|would you like", reply, re.I)):
            msg = follow.pop(0)
            continue
        break
    passed, ne, notes = ch.check(sc, erp, before, turns)
    res = Result(sc.id, sc.name, passed, ne, notes, turns, services_called=sum(len(t["services"]) for t in turns))
    if llm:
        calls = llm.log[n0:]
        res.tokens_in = sum(r.tokens_in for r in calls)
        res.tokens_out = sum(r.tokens_out for r in calls)
        res.seconds = round(sum(r.seconds for r in calls), 2)
        res.cost_inr = round(sum(r.cost_inr for r in calls), 4)
    else:
        res.seconds = round(time.perf_counter() - t0, 2)
    res.erp = erp  # kept for the caller's own read-back; not serialised
    return res


def with_change(sc: Scenario, ch) -> Scenario:
    """One of the kit's own scenarios, run on a sandbox that already has the change applied."""
    def setup(erp, _old=sc.setup):
        ch.apply(erp)
        if _old:
            _old(erp)
    return Scenario(sc.id, sc.name, sc.ask, list(sc.followups), user=sc.user, setup=setup, approve=sc.approve)


def cites(text: str, *ids: str) -> bool:
    """Did the reply name the document (by id or title)? Used for the 'told the user which rule' half of a check."""
    return any(re.search(re.escape(i), text or "", re.I) for i in ids)
