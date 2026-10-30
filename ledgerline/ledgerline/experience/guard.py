"""Cost and abuse guard for Ask Northbridge (the same idea as deploy/app.py's ModelGuard, kept in the Store).

    GUARD.check(pid)      before a chat message: kill switch, today's £ cap, per-player and class-wide rate limits
    GUARD.add(reply)      after every model call: adds its estimated £ (ledgerline.llm PRICES) to today's GMT ledger

Flags (operator-owned, in the Store): model_enabled, reason, cap_inr. Changed from /admin with the admin token.
"""
from __future__ import annotations

import datetime as dt
import os
import threading
import time
from collections import deque


class Refused(Exception):
    def __init__(self, status: int, msg: str):
        super().__init__(msg)
        self.status, self.msg = status, msg


class Guard:
    def __init__(self, store):
        self.store = store
        self.lock = threading.Lock()
        self.hits: dict[str, deque] = {}
        self.cap_default = float(os.environ.get("NORTHBRIDGE_DAILY_CAP_INR", "2000"))
        self.per_min = int(os.environ.get("NORTHBRIDGE_RATE_PLAYER_PER_MIN", "10"))
        self.per_day = int(os.environ.get("NORTHBRIDGE_RATE_PLAYER_PER_DAY", "300"))
        self.global_per_min = int(os.environ.get("NORTHBRIDGE_RATE_GLOBAL_PER_MIN", "240"))

    @staticmethod
    def today() -> str:
        return (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()

    def flags(self) -> dict:
        f = {"model_enabled": True, "reason": "", "cap_inr": self.cap_default}
        f.update(self.store.get("flags", {}) or {})
        return f

    def set_flags(self, **kw) -> dict:
        f = self.flags()
        f.update({k: v for k, v in kw.items() if v is not None})
        self.store.put("flags", f)
        return f

    def spent(self) -> dict:
        return self.store.get(f"spend:{self.today()}", None) or {"inr": 0.0, "calls": 0, "tokens_in": 0,
                                                                    "tokens_out": 0, "messages": 0}

    def check(self, pid: str):
        f = self.flags()
        if not f.get("model_enabled", True):
            raise Refused(503, "Ask Northbridge is paused by the instructor" + (f": {f['reason']}" if f.get("reason") else "."))
        if self.spent()["inr"] >= float(f.get("cap_inr") or self.cap_default):
            raise Refused(429, "Today's model budget for the class is used up. The instructor can raise it.")
        now = time.monotonic()
        with self.lock:
            for k, lim, win in (("*", self.global_per_min, 60), (pid, self.per_min, 60), (pid + "/day", self.per_day, 86400)):
                q = self.hits.setdefault(k, deque())
                while q and now - q[0] > win:
                    q.popleft()
                if len(q) >= lim:
                    who = "the class" if k == "*" else "you"
                    raise Refused(429, f"Too many messages from {who} ({lim} per {'minute' if win == 60 else 'day'}). "
                                       "Wait a little and try again.")
            for k in ("*", pid, pid + "/day"):
                self.hits[k].append(now)

    def add(self, r, message: bool = False):
        with self.lock:
            d = dict(self.spent())
            if r is not None:
                d["inr"] = round(d["inr"] + (getattr(r, "inr", None) or r.cost_inr), 4)
                d["calls"] += 1
                d["tokens_in"] += r.tokens_in
                d["tokens_out"] += r.tokens_out
            if message:
                d["messages"] = d.get("messages", 0) + 1
            self.store.put(f"spend:{self.today()}", d)

    def budget_ok(self) -> bool:
        return self.spent()["inr"] < float(self.flags().get("cap_inr") or self.cap_default)
