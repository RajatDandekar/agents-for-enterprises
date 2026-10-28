"""MCP security, measured: 2 attacks x 3 host defences x 10 phrasings x 2 models, each on a fresh Bahi.

    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/security_trials.py              # record
    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/security_trials.py --args "--smoke"
    tools/mrun.sh tools/modal_run.py --script lectures/L9-protocols/experiments/security_trials.py --mode replay --args "--check"
-> logs/security_trials.json   (or logs/security_replay_check.json with --check)

Attack and defence code: bahi/bahi/course/protocols/security.py. Cassette: IND9_sec. Success is judged by code,
from Bahi's own tables (ntf_queue for the leaked email; supplier and pr_hdr for committed writes).
"""
import argparse
import json
import os
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "/course/bahi")
from bahi.course.protocols import security as S  # noqa: E402
from bahi.llm import PRICES, USD_INR  # noqa: E402

LOGS = pathlib.Path(__file__).parent / "logs"
ap = argparse.ArgumentParser()
ap.add_argument("--smoke", action="store_true")
ap.add_argument("--check", action="store_true", help="replay every recorded trial and compare")
ap.add_argument("--models", default="gemini:gemini-3.8-flash,gemini:gemini-3.5-flash-lite")
a = ap.parse_args()
MODELS = a.models.split(",")

jobs = []
if a.smoke:
    jobs = [("A", "D0", 0, MODELS[0], "v1"), ("B", "D0", 0, MODELS[0], "v1")]
else:
    VARIANTS = [("A", "v1"), ("B", "v1"), ("B", "v2")]
    jobs = [(at, d, p, m, v) for m in MODELS for at, v in VARIANTS for d in ("D0", "D1", "D2") for p in range(10)]


def one(j):
    try:
        return S.run_trial(j[0], j[1], j[2], j[3], version=j[4])
    except Exception as e:  # noqa: BLE001
        return {"attack": j[0], "defence": j[1], "phrasing": j[2], "model": j[3], "version": j[4], "error": repr(e)[:800]}


with ThreadPoolExecutor(8) as ex:
    runs = list(ex.map(one, jobs))

errs = [r for r in runs if "error" in r]
for r in errs[:5]:
    print("ERROR", r)


def cost(r):
    p = PRICES.get(r["model"].split(":")[-1])
    return (r.get("tokens_in", 0) * p[0] + r.get("tokens_out", 0) * p[1]) / 1e6 if p else 0


summary = []
for m in MODELS:
    for at, v in [("A", "v1"), ("B", "v1"), ("B", "v2")]:
        for d in ("D0", "D1", "D2"):
            rs = [r for r in runs if r["model"] == m and r["attack"] == at and r.get("version") == v
                  and r["defence"] == d and "error" not in r]
            if not rs:
                continue
            row = {"model": m, "attack": at, "version": v, "defence": d, "n": len(rs),
                   "attempted": sum(r["attempted"] for r in rs), "succeeded": sum(r["succeeded"] for r in rs),
                   "utility_ok": sum(r["utility_ok"] for r in rs),
                   "held_by_gate": sum(len(r["held"]) for r in rs),
                   "runs_with_quarantine": sum(bool(r["quarantined"]) for r in rs),
                   "tokens_in": sum(r["tokens_in"] for r in rs), "tokens_out": sum(r["tokens_out"] for r in rs),
                   "usd": round(sum(cost(r) for r in rs), 4)}
            if at == "B":
                row["flags_certificate"] = sum(r.get("flags_certificate", False) for r in rs)
            summary.append(row)
            print(f"{m:<32} {at}{v} {d}  n={row['n']:>2} attempted={row['attempted']:>2} succeeded={row['succeeded']:>2} "
                  f"utility={row['utility_ok']:>2} held={row['held_by_gate']:>2} quarantined={row['runs_with_quarantine']:>2} "
                  f"${row['usd']}")

if a.check:
    rec = json.loads((LOGS / "security_trials.json").read_text())
    old = {(r["attack"], r.get("version"), r["defence"], r["phrasing"], r["model"]): r for r in rec["runs"] if "error" not in r}
    same = 0
    diffs = []
    for r in runs:
        k = (r["attack"], r.get("version"), r["defence"], r["phrasing"], r["model"])
        o = old.get(k)
        ok = o is not None and "error" not in r and o["answer"] == r["answer"] and o["succeeded"] == r["succeeded"] \
            and [c["name"] for c in o["calls"]] == [c["name"] for c in r["calls"]]
        same += ok
        if not ok:
            diffs.append({"key": k, "error": r.get("error")})
    out = {"mode": os.environ.get("BAHI_LLM_MODE"), "trials": len(runs), "identical_to_recorded": same,
           "errors": len(errs), "all_replayed": all(r.get("replayed") for r in runs if "error" not in r),
           "diffs": diffs[:20], "summary": summary}
    (LOGS / "security_replay_check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in out.items() if k != "summary"}, indent=1))
    sys.exit(0)


def pick(at, d, succeeded=None, model=MODELS[0], v="v1"):
    for r in runs:
        if r["model"] == model and r["attack"] == at and r.get("version") == v and r["defence"] == d and "error" not in r and \
                (succeeded is None or r["succeeded"] == succeeded):
            return r
    return None


examples = {}
for at, v in [("A", "v1"), ("B", "v1"), ("B", "v2")]:
    examples[at + v] = {
        "D0_succeeded": pick(at, "D0", True, v=v) or pick(at, "D0", True, MODELS[-1], v=v) or pick(at, "D0", v=v),
        "D1_example": pick(at, "D1", v=v) if pick(at, "D1", True, v=v) is None else pick(at, "D1", True, v=v),
        "D2_blocked": pick(at, "D2", False, v=v)
        if pick(at, "D2", False, v=v) and pick(at, "D2", False, v=v)["held"] else
        (next((r for r in runs if r["attack"] == at and r.get("version") == v and r["defence"] == "D2"
               and "error" not in r and (r["held"] or r["quarantined"])), None) or pick(at, "D2", v=v))}

res = {"pins": {"mcp": "2.3.0"}, "cassette": S.CASSETTE, "models": MODELS, "smoke": a.smoke,
       "poisoned_description": S.POISONED_SEARCH, "clean_description": S.CLEAN_SEARCH,
       "injected_quote": S.INJECTED_QUOTE, "injected_quote_v2": S.INJECTED_QUOTE_V2, "deccan_quote": S.DECCAN_QUOTE, "attacker_address": S.ATTACKER,
       "system": S.SYSTEM, "d1_rule": S.D1_RULE, "spotlight": [S.UNTRUSTED_OPEN, S.UNTRUSTED_CLOSE],
       "phrasings": S.PHRASINGS, "reviewed_sha256": S.REVIEWED,
       "poisoned_sha256": S.sha(S.POISONED_SEARCH),
       "summary": summary, "errors": len(errs),
       "total_usd": round(sum(cost(r) for r in runs if "error" not in r), 4),
       "total_inr": round(sum(cost(r) for r in runs if "error" not in r) * USD_INR, 2),
       "examples": examples, "runs": runs}
LOGS.mkdir(exist_ok=True)
name = "security_smoke.json" if a.smoke else "security_trials.json"
(LOGS / name).write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
print("total $", res["total_usd"], "errors", len(errs))
if a.smoke:
    for r in runs:
        print(json.dumps({k: r.get(k) for k in ("attack", "succeeded", "attempted", "utility_ok", "answer", "served_by")},
                         ensure_ascii=False)[:800])
        for c in r.get("calls", []):
            print("   ", c["name"], c["args"], c.get("held", ""))
