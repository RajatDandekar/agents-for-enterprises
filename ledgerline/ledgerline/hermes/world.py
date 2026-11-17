"""Hermes's world: one student's Ledgerline sandbox, its people, and the simulated clock (Lecture 5, The Habits).

    erp = new_erp()                        # Ledgerline + goods receipts + accounts payable + the week's data
    clock = Clock()                        # Mon 26 Oct 2026 09:00; tomorrow(), plus(days=7), set(...)
    tb = toolbox(erp, "ECLARKE")           # the 26 Hermes tools, with Emma's own permissions
    with at(erp, clock.t): tb.call(...)    # every call happens at the student's simulated time

Ledgerline can be made "down" for a window of simulated time (the planted 02:00 failure for the background agents):
every service call inside the window answers ERR-SYS-0503, as a real ERP does during its night maintenance.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import threading

from ..erp.engine import ERP
from ..erp.payables import install_payables
from ..toolbox import HABITS, Toolbox

START = dt.datetime(2026, 10, 26, 9, 0, tzinfo=dt.timezone.utc)
PEOPLE = {
    "ECLARKE": {"name": "Emma Clarke", "role": "purchase executive", "handle": "@emma"},
    "DOKAFOR": {"name": "Daniel Okafor", "role": "purchase manager", "handle": "@daniel"},
    "LMORENO": {"name": "Luis Moreno", "role": "senior buyer, accounts payable", "handle": "@luis"},
    "ATANAKA": {"name": "Aiko Tanaka", "role": "stores", "handle": "@aiko"},
    "LHUGHES": {"name": "Laura Hughes", "role": "purchase manager, covering for Daniel", "handle": "@laura"},
}
# Ledgerline's night maintenance in the simulated week: Wednesday 28 Oct, 02:00 to 02:20.
MAINTENANCE = [(dt.datetime(2026, 10, 28, 2, 0, tzinfo=dt.timezone.utc), dt.datetime(2026, 10, 28, 2, 20, tzinfo=dt.timezone.utc))]


def new_erp() -> ERP:
    e = ERP()
    install_payables(e)
    lock = threading.RLock()
    raw = e.call
    e.down = list(MAINTENANCE)

    def call(svc, payload=None, user="ECLARKE", screen=None, task=None):
        with lock:
            t = e._clock if e._clock.tzinfo else e._clock.replace(tzinfo=dt.timezone.utc)
            if any(a <= t < b for a, b in e.down):
                e.down_hits = getattr(e, "down_hits", 0) + 1
                return {"rc": "E", "err_cd": "ERR-SYS-0503", "msg": "SERVER BUSY, TRY LATER", "data": None}
            return raw(svc, payload, user=user, screen=screen, task=task)

    e.lock, e.call = lock, call
    return e


def toolbox(erp: ERP, user: str = "ECLARKE", names: list[str] | None = None) -> Toolbox:
    tb = Toolbox(erp, user, names=names or HABITS)
    raw = tb.call

    def call(name, args=None):
        with erp.lock:
            return raw(name, args)

    tb.call = call
    return tb


@contextlib.contextmanager
def at(erp: ERP, t: dt.datetime):
    """Run Ledgerline calls at simulated time t (the ERP's own clock ticks 7 s per call, as always)."""
    with erp.lock:
        erp._clock = t
        yield erp


class Clock:
    """The student's simulated time. Starts Monday 26 October 2026, 09:00."""

    def __init__(self, iso: str | None = None):
        self.t = dt.datetime.fromisoformat(iso) if iso else START

    def iso(self) -> str:
        return self.t.isoformat()

    def tomorrow(self) -> dt.datetime:
        d = (self.t + dt.timedelta(days=1)).date()
        return dt.datetime(d.year, d.month, d.day, 9, 0, tzinfo=dt.timezone.utc)

    def view(self) -> dict:
        return {"iso": self.iso(), "label": label(self.t), "day": self.t.strftime("%A"), "date": self.t.date().isoformat()}


def label(t: dt.datetime) -> str:
    return t.strftime("%a %-d %b %Y, %H:%M")


def short(t: dt.datetime) -> str:
    return t.strftime("%a %-d %b %H:%M")
