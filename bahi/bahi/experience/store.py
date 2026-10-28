"""What must survive a restart: player names, wishlists, mission scores, the operator's flags and today's spend.

On Modal the store is a modal.Dict (RASOI_DICT names it); anywhere else it is a plain dict in memory. Reads come
from an in-memory copy (one container serves the whole class), and writes go to the Dict from a background thread,
so a page never waits on the network. ERPs are NOT stored: a lost Rasoi is recreated, freshly seeded.
"""
from __future__ import annotations

import os
import threading
import time


class Store:
    def __init__(self, name: str | None = None):
        self.mem: dict = {}
        self.d = None
        self._dirty: set = set()
        self._lock = threading.Lock()
        name = name if name is not None else os.environ.get("RASOI_DICT")
        if name:
            try:
                import modal

                self.d = modal.Dict.from_name(name, create_if_missing=True)
                for k, v in self.d.items():
                    self.mem[k] = v
            except Exception as e:  # noqa: BLE001  (the app still works, it just forgets on restart)
                print("store: modal.Dict unavailable:", type(e).__name__, str(e)[:200])
                self.d = None
        if self.d is not None:
            threading.Thread(target=self._writer, daemon=True).start()

    def get(self, k, default=None):
        return self.mem.get(k, default)

    def put(self, k, v):
        with self._lock:
            self.mem[k] = v
            self._dirty.add(k)

    def keys(self, prefix: str = "") -> list:
        return [k for k in list(self.mem) if k.startswith(prefix)]

    def flush(self):
        if self.d is None:
            return
        with self._lock:
            todo = {k: self.mem[k] for k in self._dirty if k in self.mem}
            self._dirty.clear()
        if todo:
            try:
                self.d.update(todo)
            except Exception as e:  # noqa: BLE001
                print("store: flush failed, will retry:", type(e).__name__)
                with self._lock:
                    self._dirty |= set(todo)

    def _writer(self):
        while True:
            time.sleep(1.0)
            self.flush()
