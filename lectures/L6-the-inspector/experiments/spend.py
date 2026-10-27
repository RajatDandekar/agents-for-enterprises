"""What Lecture 6 actually spent on model calls: every live reply is stored once in a cassette, so summing the
L6_* cassettes (tokens x the prices in bahi/llm.py, at ₹88/USD) gives the bill. Stdlib only.

    python3 lectures/L6-the-inspector/experiments/spend.py      -> logs/spend.json
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "bahi"))
from bahi.llm import PRICES, USD_INR  # noqa: E402

out, tot = {}, 0.0
for p in sorted((ROOT / "bahi/bahi/cassettes").glob("L6_*.jsonl")):
    n = tin = tout = 0
    inr = 0.0
    by_model = {}
    for line in p.open():
        if not line.strip():
            continue
        d = json.loads(line)
        m = d["model"].split(":", 1)[-1]
        pr = PRICES.get(m, (0, 0))
        c = (d["tokens_in"] * pr[0] + d["tokens_out"] * pr[1]) / 1e6 * USD_INR
        n += 1; tin += d["tokens_in"]; tout += d["tokens_out"]; inr += c
        by_model[m] = round(by_model.get(m, 0) + c, 3)
    out[p.stem] = {"calls": n, "tokens_in": tin, "tokens_out": tout, "inr": round(inr, 2), "by_model": by_model}
    tot += inr
res = {"total_inr": round(tot, 2), "budget_inr": 2000, "cassettes": out,
       "note": "live calls only (replays are free); a reply recorded twice by racing threads is counted once"}
(pathlib.Path(__file__).parent / "logs" / "spend.json").write_text(json.dumps(res, indent=1))
print(f"L6 spend: ₹{tot:,.2f} over {sum(v['calls'] for v in out.values())} recorded calls")
for k, v in out.items():
    print(f"  {k:28s} {v['calls']:5d} calls  ₹{v['inr']:8.2f}  {v['by_model']}")
