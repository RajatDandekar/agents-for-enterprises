"""Shared bits of Lecture 7's experiments (builder A): where logs go, the spend record, a thread pool, JSON out.

Same shape as Lecture 6's experiments/_common.py; the logs of this lecture live in this folder's logs/.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)
L6_LOGS = HERE.parent.parent / "L6-evals-guardrails-observability" / "experiments" / "logs"     # the 16 Nov logs, read only
_lock = threading.Lock()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def write(name: str, data) -> pathlib.Path:
    p = LOGS / name
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=str))
    print("wrote", p.name, p.stat().st_size, "bytes")
    return p


def read(name: str):
    for d in (LOGS, L6_LOGS):
        if (d / name).exists():
            return json.loads((d / name).read_text())
    raise FileNotFoundError(name)


def spend(what: str, usd: float, calls: int, note: str = ""):
    """One file per run in logs/spend_parts/A_<what>__<time>.json: {"what", "usd", "calls"} (+ when, note)."""
    d = LOGS / "spend_parts"
    d.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    (d / f"A_{what}__{stamp}.json").write_text(json.dumps(
        {"what": what, "usd": round(float(usd), 4), "calls": int(calls), "at": now(), "note": note}, indent=1))
    print(f"spend: {what} US${usd:.4f} ({calls} calls)")


def pmap(fn, items, workers: int = 8):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
