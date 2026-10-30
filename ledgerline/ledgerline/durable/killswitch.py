"""Lecture 7: the kill switch and the rollout ladder, as one flag store the agent reads before ANY write.

    flags = Flags()                       # in memory (notebooks, tests)
    flags = Flags("/run/ledgerline/flags.json") # a file the operator edits (deploy/); re-read on every check
    flags.kill("duplicates seen on PO/2026/01183")   # every write stops, at once, everywhere
    flags.revive()

The rollout ladder (deploy/rollout.yaml) is the `stage` flag:
    shadow   the agent runs on real requests but writes nothing; what it WOULD have written is logged
    assist   the agent prepares; a person presses Confirm in the app, and only that click writes
    partial  the agent writes for the users in `cohort` only
    full     the agent writes for everyone
The kill switch sits above the ladder: when it is on, nothing writes, whatever the stage.

Two places check it:
  * GuardedTools wraps the intent tools: a write tool returns "paused, nothing saved" instead of writing.
  * The durable workflow's write activities call flags.check_write(): when writes are off the activity fails
    with KillSwitchOn, and the workflow PAUSES (it re-checks every 10 minutes) instead of losing the order.
"""
from __future__ import annotations

import json
import os
import pathlib
import threading

STAGES = ("shadow", "assist", "partial", "full")
DEFAULT = {"writes_enabled": True, "stage": "full", "cohort": [], "reason": ""}


class WritesPaused(Exception):
    """Raised by check_write(). `kind` is 'kill_switch' or 'stage'."""

    def __init__(self, why: str, kind: str = "kill_switch"):
        super().__init__(why)
        self.why, self.kind = why, kind


class Flags:
    def __init__(self, path: str | None = None, **initial):
        self.path = pathlib.Path(path or os.environ.get("LEDGER_FLAGS_FILE", "")) if (path or os.environ.get("LEDGER_FLAGS_FILE")) else None
        self._mem = {**DEFAULT, **initial}
        self._lock = threading.Lock()
        if self.path and not self.path.exists():
            self._write(self._mem)
        self.proposals: list[dict] = []  # shadow-mode log: what the agent would have written

    # ---------------------------------------------------------------- storage
    def read(self) -> dict:
        if self.path:
            try:
                return {**DEFAULT, **json.loads(self.path.read_text())}
            except (OSError, ValueError):
                return {**DEFAULT, "writes_enabled": False, "reason": "flags file unreadable: failing safe"}
        return dict(self._mem)

    def _write(self, d: dict):
        with self._lock:
            if self.path:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                tmp = self.path.with_suffix(".tmp")
                tmp.write_text(json.dumps(d, indent=1))
                tmp.replace(self.path)  # atomic: a reader never sees half a file
            self._mem = dict(d)

    def set(self, **kw):
        d = self.read()
        if "stage" in kw and kw["stage"] not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}")
        d.update(kw)
        self._write(d)
        return d

    # ---------------------------------------------------------------- the switch
    def kill(self, reason: str):
        return self.set(writes_enabled=False, reason=reason)

    def revive(self):
        return self.set(writes_enabled=True, reason="")

    def check_write(self, user: str, by_human: bool = False):
        """Raise WritesPaused unless this user's write may go through right now."""
        f = self.read()
        if not f["writes_enabled"]:
            raise WritesPaused(f"Writes are switched off: {f['reason'] or 'kill switch on'}", "kill_switch")
        st = f["stage"]
        if st == "shadow":
            raise WritesPaused("Shadow mode: the agent may not write; this was logged as a proposal.", "stage")
        if st == "assist" and not by_human:
            raise WritesPaused("Assist mode: only a person's Confirm click writes.", "stage")
        if st == "partial" and user not in f["cohort"]:
            raise WritesPaused(f"Partial rollout: {user} is not in the cohort yet.", "stage")

    def writes_enabled(self) -> bool:
        return bool(self.read()["writes_enabled"])


class GuardedTools:
    """The intent tools with the flag check in front of every write. Same interface as IntentTools."""

    def __init__(self, tools, flags: Flags):
        self.tools, self.flags = tools, flags
        self.names = tools.names

    def schemas(self):
        return self.tools.schemas()

    def _is_write(self, name: str, args: dict) -> bool:
        from ..agent.tools import TOOLS

        t = TOOLS.get(name)
        if not t or not t.writes:
            return False
        # create_purchase_order / register_supplier only write when confirm=true; a preview is a read
        return "confirm" not in t.params or bool(args.get("confirm"))

    def call(self, name: str, args: dict, by_human: bool = False) -> dict:
        if self._is_write(name, args):
            try:
                self.flags.check_write(self.tools.s.user_id, by_human)
            except WritesPaused as e:
                self.flags.proposals.append({"tool": name, "args": args, "blocked": e.kind})
                return {"ok": False, "paused": True, "error": f"Nothing was saved. {e.why}",
                        "next_step": "Tell the user plainly that nothing was saved and why. Do not try another tool "
                                     "to get round it."}
        return self.tools.call(name, args)

    def call_json(self, name: str, args: dict) -> str:
        return json.dumps(self.call(name, args), default=str)
