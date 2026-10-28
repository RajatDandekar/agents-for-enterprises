"""Lecture 7 experiment: the failure drills (no model calls).

    modal run tools/modal_run.py --script lectures/L7-the-night-shift/experiments/drills_run.py
    ... --args "--only lost,sweep"      (lost, sweep, wait, nowait, crash_wait, crash_commit, kill)

Writes one JSON log per drill to experiments/logs/. Every number on the L7 plates comes from these files.
"""
import argparse
import asyncio
import json
import pathlib
import time

from bahi.durable import drills

ap = argparse.ArgumentParser()
ap.add_argument("--only", default="lost,sweep,wait,nowait,crash_wait,crash_commit,kill,module")
ap.add_argument("--n", type=int, default=50)
a = ap.parse_args()
out = pathlib.Path(__file__).parent / "logs"
out.mkdir(exist_ok=True)


def save(name, d, t0):
    d = {"seconds_wall": round(time.perf_counter() - t0, 1), **d}
    (out / f"{name}.json").write_text(json.dumps(d, indent=1, default=str, ensure_ascii=False))
    print(f"wrote logs/{name}.json in {d['seconds_wall']} s")


only = a.only.split(",")
if "lost" in only:
    t0 = time.perf_counter()
    d = drills.lost_reply()
    print(json.dumps({k: d[k] for k in ("server_side", "client_saw", "check_by_key", "blind_resave_same_request")},
                     indent=1, default=str))
    save("lost_reply", d, t0)
if "sweep" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.retry_sweep(a.n, verbose=True))
    for k, v in d["summary"].items():
        print(k, v)
    save("retry_sweep", d, t0)
if "wait" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.approval_wait(50.0))
    print(json.dumps({k: d["result"][k] for k in ("outcome", "reminders", "escalated", "hours", "po_no")}),
          *[(n["recipient"], n["created_on"]) for n in d["notifications"]], sep="\n")
    save("approval_wait_50h", d, t0)
if "nowait" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.approval_wait(None))
    print(json.dumps({k: d["result"][k] for k in ("outcome", "reminders", "escalated", "hours")}))
    save("approval_wait_no_answer", d, t0)
if "crash_wait" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.crash_while_waiting())
    print(json.dumps({k: d[k] for k in ("reminders_sent_while_no_worker", "status_after_restart", "requests", "orders")}),
          d["result"]["outcome"], d["reminder"])
    save("crash_while_waiting", d, t0)
if "crash_commit" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.crash_after_commit())
    print(d["saved_before_crash"], d["hung_after_commit"], d["result"]["outcome"], d["orders"], d["attempts_worker_B"])
    save("crash_after_commit", d, t0)
if "kill" in only:
    t0 = time.perf_counter()
    d = asyncio.run(drills.kill_switch())
    print(json.dumps({k: d[k] for k in ("orders_while_paused", "still_paused_after_min", "orders_after",
                                        "tool_commit_with_switch_on", "requests_written_by_tool", "ladder")},
                     indent=1, default=str), d["result"]["outcome"], d["result"]["paused_minutes"])
    save("kill_switch", d, t0)
if "module" in only:
    from bahi.durable.module_drills import LEAVE_SPEC, run_module_drills

    t0 = time.perf_counter()
    d = run_module_drills(LEAVE_SPEC)
    for x in d["drills"]:
        print(x["drill"], "PASS" if x["passed"] else "FAIL", {k: v for k, v in x.items() if k not in ("drill", "passed")})
    save("module_drills_hr_leave", d, t0)
