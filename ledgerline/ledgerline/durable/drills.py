"""Lecture 7: the failure drills. Each returns plain dicts (for logs, notebook tables and the deck's figures).

    lost_reply()                      what really happens when Save times out after Ledgerline committed
    retry_sweep(n=50)                 naive retries vs keyed workflow activities over n injected faults
    approval_wait(rohit_at_h=50)      days of waiting in seconds: reminder at 24 h, escalation at 48 h
    crash_while_waiting()             the worker dies while waiting; a new worker resumes the same workflow
    crash_after_commit()              the worker dies right after Ledgerline saved the order; the retry finds it by key
    kill_switch()                     writes switched off mid-workflow: the workflow pauses, then resumes

Everything runs against an in-process ERP and Temporal's time-skipping test server; no model is called.
"""
from __future__ import annotations

import asyncio
import contextlib
import random
from dataclasses import replace
from datetime import timedelta

from ..erp.engine import ERP, ServiceTimeout
from .activities import LedgerlineActivities
from .keys import keyed
from .killswitch import Flags, GuardedTools
from .model import OrderRequest, WaitPolicy
from .runtime import approve, history, make_worker, quiet_logs, start_env, start_order, status, wait_until

quiet_logs()  # drills fail activities on purpose; show the retries in tables, not as tracebacks

ORDER = OrderRequest("ECLARKE", "VC-EIN-0042", "BAT-500", 2000, "PRD-07", "2026-11-02", ref="scenario-6")
FAST = WaitPolicy(retry_initial_s=0.2)  # drills: retry after 0.2 s instead of 2 s, so 50 trials take a minute


def _orders(erp: ERP, itm="BAT-500", before=()):
    return [o for o in erp.orders(itm_cd=itm) if o["po_no"] not in before]


def _prs(erp: ERP, before=()):
    return [p for p in erp.q("SELECT * FROM pr_hdr") if p["pr_no"] not in before]


def _base(erp: ERP):
    return {o["po_no"] for o in erp.orders()}, {p["pr_no"] for p in erp.q("SELECT pr_no FROM pr_hdr")}


# =============================================================================== 1. the lost reply
def lost_reply() -> dict:
    """Emma's order, with Daniel's approval already in. Save times out AFTER Ledgerline committed. What does each side see?"""
    erp = ERP()
    bp, bq = _base(erp)
    o = keyed(ORDER)
    s, r = erp.session("ECLARKE"), erp.session("DOKAFOR")
    pr = s.call("pr_save", cc_cd="PRD-07", need_dt="2026-11-02", itm_cd="BAT-500", qty=2000, est_rate=119.00,
                remarks=f"key:{o.key}")["data"]["pr_no"]
    s.call("pr_submit", pr_no=pr)
    r.call("pr_approve", pr_no=pr, decision="A", comment="ok")
    tok = s.call("po_fetch", sup_cd="VC-EIN-0042", itm_cd="BAT-500", pr_no=pr)["data"]["fetch_tok"]
    erp.inject("po_save", "timeout_after_commit", 1)
    seq0 = len(erp.calls)
    payload = dict(po_type="STD", pr_no=pr, sup_cd="VC-EIN-0042", itm_cd="BAT-500", qty=2000, rate=119.00,
                   tax_cd="VAT20-RC", cc_cd="PRD-07", need_dt="2026-11-02", fetch_tok=tok, client_ref=o.key)
    seen = None
    try:
        s.call("po_save", **payload)
    except ServiceTimeout as e:
        seen = f"ServiceTimeout: {e}"
    rec = erp.calls[seq0]
    budget_after = erp.q1("SELECT committed FROM budget WHERE cc_cd='PRD-07'")["committed"]
    # the two possible next moves
    found = s.call("po_search", client_ref=o.key)["data"]["rows"]
    tok2 = s.call("po_fetch", sup_cd="VC-EIN-0042", itm_cd="BAT-500", pr_no=pr)["data"]["fetch_tok"]
    blind = s.call("po_save", **{**payload, "fetch_tok": tok2})
    return {
        "key": o.key, "request_no": pr,
        "server_side": {"svc": rec.svc, "ts": rec.ts, "rc": rec.rc, "data": rec.data, "msg": rec.msg,
                        "stored_procedures": rec.sps, "timed_out": rec.timed_out},
        "client_saw": seen, "budget_committed_prd07_after": budget_after, "budget_committed_prd07_before": 310000.0,
        "check_by_key": found,
        "blind_resave_same_request": {"rc": blind["rc"], "err_cd": blind["err_cd"], "msg": blind["msg"]},
        "audit_trail": erp.q("SELECT ts,user_id,svc,rc,err_cd FROM audit_trail WHERE id>? ORDER BY id", 0)[-6:],
    }


# =============================================================================== 2. the retry sweep
class Refused(Exception):
    pass


def _ok(r: dict) -> dict:
    if r["rc"] == "E":
        raise Refused(f"{r['err_cd']} {r['msg']}")
    return r["data"] or {}


def _contract(s, o):
    return _ok(s.call("sup_rate_get", sup_cd=o.supplier_code, itm_cd=o.item_code))["current"]["rate"]


def naive_job(erp: ERP, o: OrderRequest, attempts: int = 3) -> dict:
    """The naive client: if anything fails or times out, do the whole job again (what a retry decorator, a script,
    or an agent that 'tries again' does). The sandbox Daniel approves whatever reaches his inbox."""
    s, r = erp.session(o.user), erp.session("DOKAFOR")
    last = ""
    for a in range(1, attempts + 1):
        try:
            rate = _contract(s, o)
            pr = _ok(s.call("pr_save", cc_cd=o.cost_centre, need_dt=o.need_by, itm_cd=o.item_code, qty=o.quantity,
                            est_rate=rate))["pr_no"]
            if _ok(s.call("pr_submit", pr_no=pr))["status"] == "PA":
                _ok(r.call("pr_approve", pr_no=pr, decision="A", comment="ok"))
            tok = _ok(s.call("po_fetch", sup_cd=o.supplier_code, itm_cd=o.item_code, pr_no=pr))["fetch_tok"]
            po = _ok(s.call("po_save", po_type="STD", pr_no=pr, sup_cd=o.supplier_code, itm_cd=o.item_code,
                            qty=o.quantity, rate=rate, tax_cd="VAT20-RC", cc_cd=o.cost_centre, need_dt=o.need_by,
                            fetch_tok=tok))["doc_no"]
            _ok(s.call("po_release", po_no=po))
            return {"reported": "released", "attempts": a}
        except (ServiceTimeout, Refused) as e:
            last = str(e)
    return {"reported": "failed", "attempts": attempts, "last_error": last}


def naive_call(erp: ERP, o: OrderRequest, attempts: int = 3) -> dict:
    """The other naive client: retry only the call that failed (pressing Save again), up to `attempts` times."""
    s, r = erp.session(o.user), erp.session("DOKAFOR")
    tries = {"n": 0}

    def again(fn):
        last = None
        for _ in range(attempts):
            tries["n"] += 1
            try:
                return fn()
            except (ServiceTimeout, Refused) as e:
                last = e
        raise Refused(f"gave up: {last}")

    try:
        rate = _contract(s, o)
        pr = again(lambda: _ok(s.call("pr_save", cc_cd=o.cost_centre, need_dt=o.need_by, itm_cd=o.item_code,
                                      qty=o.quantity, est_rate=rate))["pr_no"])
        if again(lambda: _ok(s.call("pr_submit", pr_no=pr)))["status"] == "PA":
            _ok(r.call("pr_approve", pr_no=pr, decision="A", comment="ok"))

        def save():
            tok = _ok(s.call("po_fetch", sup_cd=o.supplier_code, itm_cd=o.item_code, pr_no=pr))["fetch_tok"]
            return _ok(s.call("po_save", po_type="STD", pr_no=pr, sup_cd=o.supplier_code, itm_cd=o.item_code,
                              qty=o.quantity, rate=rate, tax_cd="VAT20-RC", cc_cd=o.cost_centre,
                              need_dt=o.need_by, fetch_tok=tok))["doc_no"]
        po = again(save)
        again(lambda: _ok(s.call("po_release", po_no=po)))
        return {"reported": "released", "attempts": tries["n"]}
    except Refused as e:
        return {"reported": "failed", "attempts": tries["n"], "last_error": str(e)}


def _truth(erp: ERP, before_pos, before_prs, item: str) -> dict:
    live = [x for x in _orders(erp, item, before_pos) if x["status"] != "CN"]
    live.sort(key=lambda x: x["po_no"])
    extra = live[1:]
    return {"orders": len(live), "released": sum(x["status"] == "RL" for x in live),
            "unreleased_orders": [x["po_no"] for x in live if x["status"] != "RL"],
            "unreleased_inr": round(sum(x["gross_value"] for x in live if x["status"] != "RL"), 2),
            "duplicate_orders": len(extra), "extra_inr": round(sum(x["gross_value"] for x in extra), 2),
            "extra_qty": sum(x["qty"] for x in extra), "requests": len(_prs(erp, before_prs)),
            "po_nos": [x["po_no"] for x in live]}


def plan_trials(n: int = 50, seed: int = 7) -> list[dict]:
    """n faults: half before the commit (error_before), half after (timeout_after_commit), spread over the three
    writes on the path, hitting once or twice in a row; each trial orders a different quantity."""
    rng = random.Random(seed)
    modes = ["error_before"] * (n // 2) + ["timeout_after_commit"] * (n - n // 2)
    rng.shuffle(modes)
    svcs = ["pr_save", "po_save", "po_release"]
    return [{"trial": i + 1, "svc": svcs[i % 3], "mode": m, "times": rng.choice([1, 1, 2]),
             "qty": rng.choice(range(16000, 24001, 1000))} for i, m in enumerate(modes)]


async def _keyed_trial(client, acts: LedgerlineActivities, t: dict, erp: ERP, o: OrderRequest) -> dict:
    acts.erp, acts.t0 = erp, erp._clock
    h = await start_order(client, o, FAST)
    st = await wait_until(h, lambda s: s["stage"] in ("waiting for approval", "creating order", "releasing") or
                          s["stage"] in ("released", "failed", "needs a person"), timeout_s=60)
    if st["stage"] == "waiting for approval":
        await approve(erp, h)
    res = await h.result()
    att = [a for a in acts.attempts if a.get("workflow_id") == h.id]
    return {"reported": res["outcome"], "attempts": len(att), "found_by_key": sum(bool(a.get("found_by_key")) for a in att)}


async def retry_sweep(n: int = 50, seed: int = 7, verbose: bool = False) -> dict:
    trials = plan_trials(n, seed)
    env = await start_env("time_skipping")
    acts = LedgerlineActivities(ERP())
    rows = []
    async with make_worker(env.client, acts, identity="sweep-worker"):
        for t in trials:
            o = replace(ORDER, quantity=t["qty"], ref=f"trial-{t['trial']}", key="")
            row = {**t}
            for name in ("naive_job", "naive_call", "keyed"):
                erp = ERP()
                bp, bq = _base(erp)
                erp.inject(t["svc"], t["mode"], t["times"])
                if name == "keyed":
                    rep = await _keyed_trial(env.client, acts, t, erp, keyed(o))
                else:
                    rep = (naive_job if name == "naive_job" else naive_call)(erp, o)
                tr = _truth(erp, bp, bq, o.item_code)
                truth_rel = tr["released"] >= 1
                tr["wrong_report"] = (rep["reported"] == "released") != truth_rel
                row[name] = {**rep, **tr}
            rows.append(row)
            if verbose:
                print(t["trial"], t["svc"], t["mode"], t["times"], {k: (row[k]["orders"], row[k]["reported"])
                                                                   for k in ("naive_job", "naive_call", "keyed")})
    await env.shutdown()
    summ = {}
    for name in ("naive_job", "naive_call", "keyed"):
        for mode in ("error_before", "timeout_after_commit", "all"):
            sel = [r[name] for r in rows if mode == "all" or r["mode"] == mode]
            summ[f"{name}/{mode}"] = {
                "trials": len(sel), "trials_with_duplicate": sum(x["duplicate_orders"] > 0 for x in sel),
                "duplicate_orders": sum(x["duplicate_orders"] for x in sel),
                "extra_inr": round(sum(x["extra_inr"] for x in sel), 2),
                "extra_qty": sum(x["extra_qty"] for x in sel),
                "extra_requests": sum(max(0, x["requests"] - 1) for x in sel),
                "wrong_reports": sum(x["wrong_report"] for x in sel),
                "unreleased_orders_left": sum(len(x["unreleased_orders"]) for x in sel),
                "unreleased_inr": round(sum(x["unreleased_inr"] for x in sel), 2),
                "exactly_one_released": sum(x["orders"] == 1 and x["released"] == 1 for x in sel)}
    return {"n": n, "seed": seed, "trials": rows, "summary": summ}


# =============================================================================== 3. waiting for Daniel
async def approval_wait(rohit_at_h: float | None = 50.0, p: WaitPolicy | None = None) -> dict:
    """Days of waiting, in seconds. rohit_at_h=None: Daniel never answers, and the workflow gives up at 120 h."""
    env = await start_env("time_skipping")
    erp = ERP()
    bp, bq = _base(erp)
    acts = LedgerlineActivities(erp)
    p = p or WaitPolicy()
    o = keyed(replace(ORDER, ref=f"wait-{rohit_at_h}-{p.remind_after_h}"))
    async with make_worker(env.client, acts, identity="worker-1"):
        h = await start_order(env.client, o, p)
        await wait_until(h, lambda s: s["stage"] == "waiting for approval")
        marks = [p.remind_after_h, p.escalate_after_h, p.give_up_after_h]
        t = 0.0
        for m in marks:
            if rohit_at_h is not None and rohit_at_h < m:
                break
            await env.sleep(timedelta(hours=m - t, seconds=5))
            t = m + 5 / 3600
            want = {p.remind_after_h: lambda s: s["reminders"] >= 1, p.escalate_after_h: lambda s: s["escalated"],
                    p.give_up_after_h: lambda s: s["stage"] == "expired"}[m]
            await wait_until(h, want)
        if rohit_at_h is not None:
            await env.sleep(timedelta(hours=rohit_at_h - t))
            await approve(erp, h)
        res = await h.result()
        hist = await history(h)
    await env.shutdown()
    ntf = erp.q("SELECT recipient, subject, body, created_on FROM ntf_queue ORDER BY id")
    return {"rohit_at_h": rohit_at_h, "result": res, "history": hist,
            "notifications": [n for n in ntf if n["created_on"] >= "2026-10-26"],
            "orders": [{k: x[k] for k in ("po_no", "status", "approved_by", "gross_value", "client_ref", "created_on")}
                       for x in _orders(erp, before=bp)]}


# =============================================================================== 4. crashes
async def _kill(task: asyncio.Task):
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError, Exception):
        await task


async def crash_while_waiting(down_h: float = 30.0) -> dict:
    """Worker A starts the workflow and dies while it waits for Daniel. For `down_h` hours no worker runs at all.
    Worker B (a new process in real life) starts, replays the history, sends the overdue reminder, and finishes."""
    env = await start_env("time_skipping")
    erp = ERP()
    bp, bq = _base(erp)
    a = LedgerlineActivities(erp)
    o = keyed(replace(ORDER, ref="crash-wait"))
    wa = make_worker(env.client, a, identity="worker-A", cache=False)
    ta = asyncio.create_task(wa.run())
    h = await start_order(env.client, o, WaitPolicy())
    await wait_until(h, lambda s: s["stage"] == "waiting for approval")
    st_before = await status(h)
    await _kill(ta)
    # Let the hours pass with no worker alive. At hour 24 the reminder timer fires on the server; its follow-up task
    # waits there for any worker (the test server holds its clock until someone picks it up).
    sleeper = asyncio.create_task(env.sleep(timedelta(hours=down_h)))
    await asyncio.sleep(2.0)
    sent_while_down = erp.q("SELECT COUNT(*) n FROM ntf_queue WHERE body LIKE ?", f"%remind:{o.key}%")[0]["n"]
    b = LedgerlineActivities(erp, t0=a.t0)
    async with make_worker(env.client, b, identity="worker-B", cache=False):
        await sleeper
        st_after = await wait_until(h, lambda s: s["reminders"] >= 1)
        await approve(erp, h)
        res = await h.result()
        hist = await history(h)
    await env.shutdown()
    return {"down_h": down_h, "status_before_crash": st_before, "reminders_sent_while_no_worker": sent_while_down,
            "status_after_restart": {k: st_after[k] for k in ("stage", "reminders", "request_no")},
            "result": res, "history": hist, "requests": len(_prs(erp, bq)), "orders": len(_orders(erp, before=bp)),
            "attempts_worker_A": a.attempts, "attempts_worker_B": b.attempts,
            "reminder": erp.q("SELECT recipient, created_on, body FROM ntf_queue WHERE body LIKE ?", f"%remind:{o.key}%")}


async def crash_after_commit() -> dict:
    """Worker A runs create_order; Ledgerline commits the PO; worker A freezes before it can report, and is killed.
    Temporal retries the activity on worker B. The retry looks up the key and finds the order: one PO, not two."""
    env = await start_env("time_skipping")
    erp = ERP()
    bp, bq = _base(erp)
    a = LedgerlineActivities(erp)
    a.hang_after_commit.add("create_order")
    o = keyed(replace(ORDER, ref="crash-commit"))
    ta = asyncio.create_task(make_worker(env.client, a, identity="worker-A", cache=False).run())
    h = await start_order(env.client, o, WaitPolicy())
    await wait_until(h, lambda s: s["stage"] == "waiting for approval")
    await approve(erp, h)
    for _ in range(400):
        if a.hung:
            break
        await asyncio.sleep(0.05)
    saved_before_crash = [x["po_no"] for x in _orders(erp, before=bp)]
    await _kill(ta)
    b = LedgerlineActivities(erp, t0=a.t0)
    async with make_worker(env.client, b, identity="worker-B", cache=False):
        res = await h.result()
        hist = await history(h)
    await env.shutdown()
    return {"saved_before_crash": saved_before_crash, "hung_after_commit": a.hung, "result": res, "history": hist,
            "orders": [{k: x[k] for k in ("po_no", "status", "client_ref", "gross_value")} for x in _orders(erp, before=bp)],
            "attempts_worker_A": a.attempts, "attempts_worker_B": b.attempts}


# =============================================================================== 5. the kill switch
async def kill_switch(paused_for_min: int = 30) -> dict:
    env = await start_env("time_skipping")
    erp = ERP()
    bp, bq = _base(erp)
    flags = Flags()
    acts = LedgerlineActivities(erp, flags)
    o = keyed(replace(ORDER, ref="kill-switch"))
    out = {}
    async with make_worker(env.client, acts, identity="worker-1"):
        h = await start_order(env.client, o, WaitPolicy())
        await wait_until(h, lambda s: s["stage"] == "waiting for approval")
        flags.kill("drill: duplicates suspected")
        await approve(erp, h)
        await wait_until(h, lambda s: s["stage"] == "paused")
        out["orders_while_paused"] = len(_orders(erp, before=bp))
        for k in range(paused_for_min // 10):
            await env.sleep(timedelta(minutes=10, seconds=1))
            await wait_until(h, lambda s, k=k: s["paused_minutes"] >= 10 * (k + 1))
        out["still_paused_after_min"] = (await status(h))["paused_minutes"]
        flags.revive()
        await env.sleep(timedelta(minutes=10, seconds=1))
        res = await h.result()
        out["result"] = res
        out["history"] = await history(h)
    await env.shutdown()
    out["orders_after"] = [{k: x[k] for k in ("po_no", "status")} for x in _orders(erp, before=bp)]
    # the same switch in front of the agent's tools
    from ..agent.tools import IntentTools

    erp2 = ERP()
    f2 = Flags()
    f2.kill("drill")
    g = GuardedTools(IntentTools(erp2.session("ECLARKE")), f2)
    args = dict(supplier_code="VC-EIN-0042", item_code="BAT-500", quantity=2000, cost_centre="PRD-07",
                need_by="2026-11-02", idempotency_key=o.key)
    out["tool_preview_with_switch_on"] = g.call("create_purchase_order", {**args, "confirm": False}).get("preview", {})
    out["tool_commit_with_switch_on"] = g.call("create_purchase_order", {**args, "confirm": True})
    out["requests_written_by_tool"] = len(_prs(erp2))
    for stage, by_human, user in (("shadow", False, "ECLARKE"), ("assist", False, "ECLARKE"), ("assist", True, "ECLARKE"),
                                  ("partial", False, "ECLARKE"), ("partial", False, "LMORENO"), ("full", False, "ECLARKE")):
        f3 = Flags(stage=stage, cohort=["LMORENO"])
        try:
            f3.check_write(user, by_human)
            verdict = "writes"
        except Exception as e:  # WritesPaused
            verdict = f"blocked: {e}"
        out.setdefault("ladder", []).append({"stage": stage, "user": user, "by_human": by_human, "verdict": verdict})
    return out
