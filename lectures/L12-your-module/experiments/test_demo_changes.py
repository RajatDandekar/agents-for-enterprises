"""Lecture 12 (demo day): prove each module's demo-day change is fair. Run on Modal, never on the laptop:

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script lectures/L12-your-module/experiments/test_demo_changes.py
    ... --args "--only hr_leave"

For every kit that has modules/<name>/demo_change.py:
  A. the kit's four careful REFERENCE scenarios still pass on a sandbox with the change applied (nothing else broke);
  B. BEFORE: the kit's careful behaviour from before the change (OLD) fails the hidden test (the change is real);
  C. AFTER: the careful behaviour that absorbs the change (NEW) passes the hidden test (the change is fair);
  D. the careless NAIVE run is caught by a never-event or the check;
  E. the hidden scenario plays the same on a sandbox with all eight kits installed (modules can call each other).
Writes logs/demo_changes.json (one log, or logs/demo_changes_<name>.json with --only).
No model calls: every agent here is scripted.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import traceback

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2]
sys.path.insert(0, str(COURSE / "bahi"))
sys.path.insert(0, str(COURSE / "modules"))

from demo_day import load_change, run_change, with_change  # noqa: E402

from bahi.modules._kit import KITS, load, run_module_scenario, scripted  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--only", default="")
a = ap.parse_args()
names = [n for n in KITS if (not a.only or n in a.only.split(","))
         and (COURSE / "modules" / n / "demo_change.py").exists()]


def brief(r):
    return {"passed": r.passed, "never_events": r.never_events, "notes": r.notes, "services": r.services_called,
            "turns": [{"user": t["user"], "agent": t["agent"], "writes": t["writes"], "users": t.get("users")}
                      for t in r.turns]}


out = {"kits": {}}
for name in names:
    row = {"module": name}
    try:
        ch = load_change(name)
        row["change"] = ch.CHANGE
        row["doc"] = ch.DOC_NAME
        _, S, _ = load(name)
        # A. the kit's own scenarios with the change applied
        ref = []
        for sc in S.SCENARIOS:
            r = run_module_scenario(scripted(S.REFERENCE[sc.id]), name, with_change(sc, ch))
            ref.append({"id": sc.id, "passed": r.passed, "never_events": r.never_events, "notes": r.notes})
        row["kit_reference_with_change"] = ref
        # B, C, D
        old = run_change(scripted(ch.OLD), name, ch)
        new = run_change(scripted(ch.NEW), name, ch)
        nai = run_change(scripted(ch.NAIVE, getattr(ch, "NAIVE_RUN_AS", None)), name, ch)
        row["before_change_reference"] = brief(old)
        row["after_change_reference"] = brief(new)
        row["naive"] = brief(nai)
        # E. all eight installed together
        allk = run_change(scripted(ch.NEW), name, ch, also=tuple(k for k in KITS if k != name))
        row["after_change_all_kits"] = {"passed": allk.passed, "never_events": allk.never_events, "notes": allk.notes}
        row["fair"] = (all(x["passed"] for x in ref) and not old.passed and new.passed and not nai.passed
                       and allk.passed)
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        row["error"] = repr(e)
        row["fair"] = False
    out["kits"][name] = row
    print(f"\n=== {name} [{row.get('change', {}).get('kind')}] {row.get('change', {}).get('title')}")
    if "error" in row:
        print("   ERROR", row["error"])
        continue
    print("   A kit reference with change:", [(x["id"], x["passed"]) for x in row["kit_reference_with_change"]])
    for k in ("before_change_reference", "after_change_reference", "naive"):
        x = row[k]
        print(f"   {k}: {'PASS' if x['passed'] else 'FAIL'} {x['never_events']} {x['notes']}")
        for t in x["turns"]:
            print(f"      U: {t['user'][:120]}\n      A: {(t['agent'] or '')[:200]}  writes={t['writes']} as={t['users']}")
    print("   E all kits:", row["after_change_all_kits"])
    print("   FAIR" if row["fair"] else "   NOT FAIR")

out["summary"] = {"kits": len(names), "fair": sum(1 for r in out["kits"].values() if r["fair"]),
                  "fair_kits": [n for n, r in out["kits"].items() if r["fair"]]}
print("\nSUMMARY", out["summary"])
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)
fn = "demo_changes.json" if not a.only else f"demo_changes_{a.only.replace(',', '_')}.json"
(LOGS / fn).write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
sys.exit(0 if out["summary"]["fair"] == len(names) else 1)
