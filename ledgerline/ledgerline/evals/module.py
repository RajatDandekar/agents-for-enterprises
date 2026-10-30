"""Lecture 6 for your capstone module (A6): the same suite runner, metrics and gate, on your module's world.

    from ledgerline.evals.module import ModuleWorld, kit_expect
    from ledgerline.evals.suite import Case, Fact
    from ledgerline.evals.agents import PlainFactory
    from ledgerline.evals.runner import run_suite

    world = ModuleWorld("hr_leave")
    cases = [Case("L01", "single", "G", "Two days off", "I need Thursday and Friday off for my sister's wedding.",
                  expect=kit_expect("hr_leave", 1), scenario_id=1, lookups=["balance"]), ...]
    run = run_suite(PlainFactory(my_make_agent), cases, sim="scripted", world=world)

What the world swaps: a fresh ERP(modules=[name]) with the case's setup_fn; the kit's before(), play_approvers()
and the never-events from the kit's check(). The metrics are the same code as purchasing's: asked for the missing
field, never asked what it could look up, no forbidden tool (approvals by the agent, writes before she confirmed,
writes in an answer-only case), no duplicate write, right final status, right clause.
"""
from __future__ import annotations

from ..erp.engine import ERP
from ..modules._kit import Scenario, load


class ModuleWorld:
    def __init__(self, module: str, also: tuple = ()):
        self.module, self.also = module, also
        _, self.S, _ = load(module)

    def new_erp(self, case) -> ERP:
        erp = ERP(modules=[self.module, *self.also])
        if case.setup_fn:
            case.setup_fn(erp)
        elif case.setup:
            case.apply_setup(erp)
        return erp

    def before(self, erp) -> dict:
        return self.S.before(erp)

    def _sc(self, case) -> Scenario:
        return Scenario(case.scenario_id, case.name, case.ask, user=case.user, approve=case.approve != "no")

    def play_approvers(self, erp, case) -> str | None:
        if case.approve == "no":
            return None
        return self.S.play_approvers(erp, self._sc(case))

    def context(self, erp, before) -> dict:
        return {"new": [], "live": [], "new_sups": [], "new_prs": []}

    def never_events(self, ctx) -> list[str]:
        _, ne, _ = self.S.check(self._sc(ctx["case"]), ctx["erp"], ctx["before"], ctx["turns"])
        return ne


def kit_expect(module: str, scenario_id: int):
    """Final status = the kit's own check() for that scenario (never-events are scored separately)."""
    _, S, _ = load(module)

    def f(ctx):
        sc = Scenario(scenario_id, ctx["case"].name, ctx["case"].ask, user=ctx["case"].user)
        ok, ne, notes = S.check(sc, ctx["erp"], ctx["before"], ctx["turns"])
        return ok, "; ".join(notes + ne)
    return f


def scripted_factory(module: str, which: str = "REFERENCE", scenario_id: int = 1):
    """The kit's scripted REFERENCE (careful) or NAIVE (careless) run for one scenario, as a factory (no model)."""
    from ..modules._kit import ScriptedAgent
    from .agents import PlainFactory
    _, S, _ = load(module)
    steps = getattr(S, which)[scenario_id]
    run_as = (getattr(S, "NAIVE_RUN_AS", {}) or {}).get(scenario_id) if which == "NAIVE" else None
    return PlainFactory(lambda erp, user: ScriptedAgent(erp, user, list(steps), run_as), name=f"{module} {which.lower()} #{scenario_id}")
