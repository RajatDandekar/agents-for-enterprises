"""Shared bits of Lecture 6's experiments: where logs go, the spend ledger, a thread pool, JSON out."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)
FIGS = HERE.parent / "figs"
_lock = threading.Lock()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def write(name: str, data) -> pathlib.Path:
    p = LOGS / name
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=str))
    print("wrote", p.name, p.stat().st_size, "bytes")
    return p


def spend(experiment: str, usd: float, calls: int, tokens_in: int = 0, tokens_out: int = 0, model: str = "", note: str = ""):
    """One file per experiment run in logs/spend_parts/ (runs may happen in parallel on Modal); total() adds them up into
    logs/spend.json. US$ from token counts x list prices (ledgerline.llm.PRICES)."""
    d = LOGS / "spend_parts"
    d.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    (d / f"{experiment}__{stamp}.json").write_text(json.dumps(
        {"at": now(), "experiment": experiment, "model": model, "calls": calls, "tokens_in": tokens_in,
         "tokens_out": tokens_out, "usd": round(usd, 4), "note": note}, indent=1))
    print(f"spend: {experiment} US${usd:.4f} ({calls} calls)")


def total() -> dict:
    runs = sorted((json.loads(f.read_text()) for f in (LOGS / "spend_parts").glob("*.json")), key=lambda r: r["at"])
    d = {"note": "Every model call our experiments and labs made for Lecture 6: US$ from token counts x list prices "
                 "(ledgerline.llm.PRICES). Written by experiments/_common.total().", "runs": runs,
         "by_experiment": {}, "total_usd": round(sum(r["usd"] for r in runs), 4)}
    for r in runs:
        e = d["by_experiment"].setdefault(r["experiment"], {"usd": 0.0, "calls": 0})
        e["usd"] = round(e["usd"] + r["usd"], 4)
        e["calls"] += r["calls"]
    (LOGS / "spend.json").write_text(json.dumps(d, indent=1))
    return d


def pmap(fn, items, workers: int = 8):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))
