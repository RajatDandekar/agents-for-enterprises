"""Players: each person in the cohort gets their own Rasoi (their own Bahi sandbox), keyed by a player id.

The contract the experience app and the Workflow Studio share (keep these names and arguments):

    players = Players()
    p = players.join("Asha")                 # -> Player(pid, name, joined_on); a fresh, seeded Rasoi for Asha
    players.get(pid)                         # -> Player or None
    players.erp(pid)                         # -> that player's ERP (recreated, freshly seeded, if it was lost)
    players.toolbox(pid, user="KJOSHI")      # -> Toolbox bound to that player's Rasoi, as Kavita (or RMEHTA, NDESAI)
    players.reset(pid)                       # -> a fresh Rasoi for the same player

A player acts in their Rasoi as one of its people: Kavita (KJOSHI) buys, Rohit (RMEHTA) approves, Neha (NDESAI)
receives the goods. State lives in memory in one container; `save`/`load` hooks let the app persist the names.

Thread safety: FastAPI serves many players at once, and one player's chat, inbox and legacy client can touch the
same Rasoi from different threads. Every ERP made here carries `erp.lock` (a re-entrant lock), and its `call()`
(the service layer: legacy client, Session, every tool) and every Toolbox.call() made here run under it.
"""
from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field

from ..erp.engine import ERP
from ..erp.receipts import install_receipts
from ..toolbox import Toolbox

PEOPLE = {"KJOSHI": "Kavita Joshi, purchase executive", "RMEHTA": "Rohit Mehta, purchase manager",
          "NDESAI": "Neha Desai, stores"}


@dataclass
class Player:
    pid: str
    name: str
    joined_on: float = field(default_factory=time.time)
    data: dict = field(default_factory=dict)  # app-owned: wishlist, mission timings, scorecard ...


class Players:
    def __init__(self):
        self._players: dict[str, Player] = {}
        self._erps: dict[str, ERP] = {}
        self._lock = threading.RLock()

    @staticmethod
    def make_pid(name: str) -> str:
        return hashlib.sha256(f"{name}|{time.time_ns()}".encode()).hexdigest()[:12]

    def join(self, name: str, pid: str | None = None) -> Player:
        with self._lock:
            pid = pid or self.make_pid(name)
            p = self._players.get(pid) or Player(pid, name.strip()[:40] or "Engineer")
            self._players[pid] = p
            return p

    def get(self, pid: str) -> Player | None:
        return self._players.get(pid)

    def all(self) -> list[Player]:
        return list(self._players.values())

    def erp(self, pid: str) -> ERP:
        with self._lock:
            if pid not in self._erps:
                e = ERP()
                install_receipts(e)
                guard_erp(e)
                self._erps[pid] = e
            return self._erps[pid]

    def toolbox(self, pid: str, user: str = "KJOSHI", names: list[str] | None = None) -> Toolbox:
        e = self.erp(pid)
        with e.lock:
            tb = Toolbox(e, user, names)
        return locked_toolbox(tb, e.lock)

    def reset(self, pid: str) -> ERP:
        with self._lock:
            self._erps.pop(pid, None)
            return self.erp(pid)


def guard_erp(e: ERP) -> ERP:
    """Give an ERP a re-entrant lock and run its service layer under it (safe to call twice)."""
    if getattr(e, "lock", None) is not None:
        return e
    lock = threading.RLock()
    raw = e.call

    def call(*a, **kw):
        with lock:
            return raw(*a, **kw)

    e.lock, e.call = lock, call
    return e


def locked_toolbox(tb: Toolbox, lock) -> Toolbox:
    """Run every tool call of this Toolbox under the ERP's lock (a tool makes several service calls in a row)."""
    raw = tb.call

    def call(name, args=None):
        with lock:
            return raw(name, args)

    tb.call = call
    return tb
