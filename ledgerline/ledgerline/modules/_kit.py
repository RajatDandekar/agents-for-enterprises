"""Shared helpers for the capstone module kits (ledgerline.modules.<name>).

A module kit is a Python package that installs on top of purchasing:

    erp = ERP(modules=["hr_leave"])            # one module
    erp = ERP(modules=list(KITS))               # all eight together

Each package provides:
    KIT       dict: name, title, prefix (services, procedures and tables all start with it), speaker, after sentence
    SCHEMA    SQL that creates the module's own tables (every table name starts with the prefix)
    seed(erp) inserts the module's ~50 seed records, its extra people and its role permissions
    services.py / procs.py   registered with the same @service / @proc decorators as purchasing
    screens/*.yaml           three legacy screens (format: screens/FORMAT.md)
    docs/*.md                four to six policy documents
    scenarios.py             four Scenario objects, before(erp), play_approvers(erp, sc), check(sc, erp, before, turns)
    legacy.py                happy_path(erp) (the before, scripted) and TRAPS (each trap, triggered and checked)

Everything here is fictional, like the rest of Ledgerline.
"""
from __future__ import annotations

import importlib
import re
import time
from dataclasses import dataclass, field
from typing import Callable

from ..erp.engine import ERP, SERVICES, LedgerlineError, ServiceTimeout, Session  # noqa: F401
from ..scenarios import Result, Scenario  # noqa: F401  (modules reuse the course's Scenario and Result)

KITS = ["pur_amend", "fin_payables", "hr_leave", "sales_orders", "svc_warranty", "inv_transfers",
        "travel_claims", "legal_contracts"]

F = lambda name, t="str", req=False, desc="": (name, t, req, desc)  # noqa: E731  (same as purchasing)

# ----------------------------------------------------------------------------- the extra people
# Purchasing's six people (ECLARKE, DOKAFOR, LMORENO, HWEBER, ATANAKA, SVC_AGENT) are always there.
# Modules add the people they need from this one roster, so every module agrees on who is who.
# user_id, name, role, ou, approval limit, manager, password, default cost centre, email, slack
PEOPLE = {
    "PSHAH": ("PSHAH", "Priya Shah", "AP-EXEC", "NBC-MAN-01", 200000, "VNAIR", "priya@123", "ADM-01",
              "priya.shah@northbridgecycles.example", "@priya"),
    "VNAIR": ("VNAIR", "Vikram Nair", "FIN-CTRL", "NBC-MAN-01", 2500000, "HWEBER", "vikram@123", "ADM-01",
              "vikram.nair@northbridgecycles.example", "@vikram"),
    "MGOKHALE": ("MGOKHALE", "Meera Gokhale", "HR-EXEC", "NBC-MAN-01", 0, "HWEBER", "meera@123", "ADM-01",
                 "meera.gokhale@northbridgecycles.example", "@meera"),
    "ARAO": ("ARAO", "Arjun Rao", "SAL-EXEC", "NBC-MAN-01", 500000, "SIYER", "arjun@123", "ADM-01",
             "arjun.rao@northbridgecycles.example", "@arjun"),
    "SIYER": ("SIYER", "Sunita Iyer", "SAL-MGR", "NBC-MAN-01", 2500000, "HWEBER", "sunita@123", "ADM-01",
              "sunita.iyer@northbridgecycles.example", "@sunita"),
    "FSHAIKH": ("FSHAIKH", "Farhan Shaikh", "SVC-DESK", "NBC-MAN-01", 5000, "NBHOSALE", "farhan@123", "ADM-01",
                "farhan.shaikh@northbridgecycles.example", "@farhan"),
    "NBHOSALE": ("NBHOSALE", "Nitin Bhosale", "SVC-MGR", "NBC-MAN-01", 100000, "HWEBER", "nitin@123", "ADM-01",
                 "nitin.bhosale@northbridgecycles.example", "@nitin"),
    "GPAWAR": ("GPAWAR", "Ganesh Pawar", "STORES", "NBC-LDS-01", 0, "DOKAFOR", "ganesh@123", "PRD-07",
               "ganesh.pawar@northbridgecycles.example", "@ganesh"),
    "BSALUNKE": ("BSALUNKE", "Balu Salunke", "SECURITY", "NBC-LDS-01", 0, "HWEBER", "balu@123", "ADM-01",
                 "security.chakan@northbridgecycles.example", None),
    "SPILLAI": ("SPILLAI", "Sanjay Pillai", "TRV-DESK", "NBC-MAN-01", 0, "VNAIR", "sanjay@123", "ADM-01",
                "travel.desk@northbridgecycles.example", "@sanjay"),
    "RMENON": ("RMENON", "Rekha Menon", "LEGAL", "NBC-MAN-01", 0, "HWEBER", "rekha@123", "ADM-01",
               "rekha.menon@northbridgecycles.example", "@rekha"),
}


# Finished goods and extra locations several modules share (sales sells them, service repairs them).
# itm_cd, description, uom, cell_safety, category, active, reorder level, average daily issue
ITEMS = {
    "PC-SS-03L": ("PC-SS-03L", "Pressure e-bike, stainless steel, 3 L", "NOS", 1, "FG", 1, 0, 0),
    "PC-SS-05L": ("PC-SS-05L", "Pressure e-bike, stainless steel, 5 L", "NOS", 1, "FG", 1, 0, 0),
    "PC-AL-05L": ("PC-AL-05L", "Pressure e-bike, aluminium, 5 L", "NOS", 1, "FG", 1, 0, 0),
    "PC-SS-07L": ("PC-SS-07L", "Pressure e-bike, stainless steel, 7.5 L", "NOS", 1, "FG", 1, 0, 0),
}
# whs_cd, name, ou
LOCATIONS = {
    "WH-PUN-FG": ("WH-PUN-FG", "Manchester finished goods", "NBC-MAN-01"),
    "WH-PUN-LN5": ("WH-PUN-LN5", "Manchester city e-bike line-side store", "NBC-MAN-01"),
}


def add_items(erp: ERP, *codes: str):
    erp.db.executemany("INSERT OR IGNORE INTO item VALUES (?,?,?,?,?,?,?,?)", [ITEMS[c] for c in codes])


def add_locations(erp: ERP, *codes: str):
    erp.db.executemany("INSERT OR IGNORE INTO warehouse VALUES (?,?,?)", [LOCATIONS[c] for c in codes])


def add_people(erp: ERP, *user_ids: str):
    """Add people from PEOPLE (INSERT OR IGNORE, so two modules can both add Vikram)."""
    erp.db.executemany("INSERT OR IGNORE INTO app_user VALUES (?,?,?,?,?,?,?,?,?,?)",
                       [PEOPLE[u] for u in user_ids])


def grant(erp: ERP, role: str, svcs: list[str]):
    """Give a role the right to call services (role_perm), skipping rows that already exist."""
    for s in svcs:
        if not erp.q1("SELECT 1 FROM role_perm WHERE role_cd=? AND svc=?", role, s):
            erp.x("INSERT INTO role_perm VALUES (?,?)", role, s)


def add_seq(erp: ERP, doc_type: str, prefix: str, next_no: int, width: int):
    """A document number series for sp_doc_no_next, e.g. add_seq(erp, "LV", "LV/2026/", 388, 5)."""
    erp.x("INSERT OR IGNORE INTO doc_seq VALUES (?,?,?,?)", doc_type, prefix, next_no, width)


def insert(erp: ERP, table: str, rows: list[tuple]):
    if rows:
        erp.db.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(rows[0]))})", rows)


def load(name: str):
    """The module package and its scenarios / legacy sub-modules."""
    pkg = importlib.import_module(f"ledgerline.modules.{name}")
    return pkg, importlib.import_module(f"ledgerline.modules.{name}.scenarios"), importlib.import_module(f"ledgerline.modules.{name}.legacy")


def write_svcs() -> set[str]:
    return {n for n, s in SERVICES.items() if s.kind == "write"}


# ----------------------------------------------------------------------------- running a module scenario
def run_module_scenario(make_agent: Callable[[ERP, str], object], module: str, sc: Scenario, max_turns: int = 5,
                        verbose: bool = False, also: tuple = ()) -> Result:
    """The module version of ledgerline.scenarios.run_scenario.

    Builds ERP(modules=[module, *also]), runs sc.setup, lets the agent talk to the scenario's user, plays the
    module's approvers whenever something waits on them (scenarios.play_approvers), answers follow-ups,
    then checks the ERP state with the module's check(). No model judges anything.
    """
    _, S, _ = load(module)
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
    for _ in range(max_turns):
        c0 = len(erp.calls)
        reply = agent.respond(msg)
        calls = erp.calls[c0:]
        writes = [c.svc for c in calls if c.svc in writes_set and c.rc != "E"]
        turns.append({"user": msg, "agent": reply, "services": [c.svc for c in calls], "writes": writes})
        if verbose:
            print(f"{sc.user}: {msg}\nAGENT:  {reply}\n  services: {[c.svc for c in calls]}\n")
        played = S.play_approvers(erp, sc) if sc.approve else None
        if played:
            msg = played
            continue
        if follow and reply and ("?" in reply[-200:] or re.search(r"confirm|shall I|should I|would you like", reply, re.I)):
            msg = follow.pop(0)
            continue
        break
    passed, ne, notes = S.check(sc, erp, before, turns)
    res = Result(sc.id, sc.name, passed, ne, notes, turns, services_called=sum(len(t["services"]) for t in turns))
    if llm:
        calls = llm.log[n0:]
        res.tokens_in = sum(r.tokens_in for r in calls)
        res.tokens_out = sum(r.tokens_out for r in calls)
        res.seconds = round(sum(r.seconds for r in calls), 2)
        res.cost_inr = round(sum(r.cost_inr for r in calls), 4)
    else:
        res.seconds = round(time.perf_counter() - t0, 2)
    return res


@dataclass
class ScriptedAgent:
    """A stand-in agent for tests and reference runs: each respond() runs the next step.

    A step is a function step(s: Session) -> str that calls Ledgerline services and returns the reply text.
    Used by modules/test_kits.py to prove each check() passes the careful path and catches the naive one.
    """
    erp: ERP
    user: str
    steps: list
    run_as: str | None = None
    i: int = 0
    log: list = field(default_factory=list)

    def respond(self, text: str) -> str:
        if self.i >= len(self.steps):
            return "Nothing more to do."
        s = self.erp.session(self.run_as or self.user)
        step = self.steps[self.i]
        self.i += 1
        try:
            reply = step(s)
        except ServiceTimeout as e:
            reply = f"The ERP did not answer in time ({e})."
        self.log.append(reply)
        return reply


def scripted(steps: list, run_as: str | None = None):
    """make_agent factory for run_module_scenario."""
    return lambda erp, user: ScriptedAgent(erp, user, list(steps), run_as)


def ok(r: dict) -> dict:
    """Assert a service call succeeded (rc S or W) and return its data; for legacy.py walkthroughs."""
    if r["rc"] == "E":
        raise LedgerlineError(r["err_cd"], r["msg"])
    return r["data"] or {}
