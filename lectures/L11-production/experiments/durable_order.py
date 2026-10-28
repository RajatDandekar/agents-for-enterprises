"""Lecture 11 experiment 3: Ask Rasoi's order as a durable Temporal workflow that survives two killed workers.

    L11_IMAGE=durable tools/mrun.sh lectures/L11-production/experiments/l11_modal.py --script lectures/L11-production/experiments/durable_order.py

All in one Modal container, each piece its own process:
    temporal server start-dev (CLI)   the Temporal service + its web UI on :8233
    Bahi host (uvicorn)               the ERP, outside every worker, as in a plant
    worker-1, worker-2, worker-3      python -m bahi.course.production.durable worker <id>
The drill:
    1  start the workflow with Kavita's message; worker-1 runs agent turn 1 (preview)
    2  signal Kavita's "Yes, go ahead."; worker-1 commits PR/2026/04417; it waits for Rohit
    3  SIGKILL worker-1 while it waits. Rohit approves IN BAHI; the app signals approval_decided. No worker is running.
    4  start worker-2: it replays the history (no model call, no Bahi write repeated) and runs agent turn 3
    5  the moment Bahi holds the purchase order but before it is released, SIGKILL worker-2
    6  start worker-3: it replays again and finishes: one request, one order, released
In the drill the 24-hour reminder timer is set to 20 seconds (remind_after_s=20) so one reminder fires while we wait.
Screenshots of the Temporal UI with headless Chromium go to lectures/L11-production/shots/.
Writes logs/durable_order.json, logs/durable_history.json and bahi/course/production/fixtures/durable_*.json.
"""
import asyncio
import json
import os
import pathlib
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"; LOGS.mkdir(exist_ok=True)
SHOTS = HERE.parent / "shots"; SHOTS.mkdir(exist_ok=True)
from bahi.course.production import durable as D

FIX = pathlib.Path(D.__file__).parent / "fixtures"
HTTP_LOG = LOGS / "durable_model_http.jsonl"
if HTTP_LOG.exists():
    HTTP_LOG.unlink()
ENV = {**os.environ, "PYTHONPATH": "/course/bahi", "PYTHONUNBUFFERED": "1"}
T0 = time.time()
EVENTS = []


def ev(what, **kw):
    EVENTS.append({"t": round(time.time() - T0, 2), "what": what, **kw})
    print(f"[{time.time() - T0:7.2f}s] {what} {json.dumps(kw, default=str)[:300]}", flush=True)


def start(cmd, name):
    log = open(f"/tmp/{name}.log", "w")
    return subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=ENV, cwd="/course")


def worker(name):
    p = start([sys.executable, "-m", "bahi.course.production.durable", "worker", name, str(HTTP_LOG)], name)
    ev("worker started", worker=name, pid=p.pid)
    return p


def kill(p, name):
    os.kill(p.pid, signal.SIGKILL)
    p.wait()
    ev("worker killed with SIGKILL", worker=name, pid=p.pid)


def bahi_state():
    import httpx
    return httpx.get("http://127.0.0.1:8711/state", timeout=10).json()


async def shot(page, url, name, wait_text=None):
    try:
        await page.goto(url, wait_until="load", timeout=45000)  # a running workflow long-polls: never network-idle
        if wait_text:
            try:
                await page.get_by_text(wait_text).first.wait_for(timeout=10000)
            except Exception:  # noqa: BLE001
                pass
        await page.wait_for_timeout(3500)
        await page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=False)
        ev("screenshot", file=f"shots/{name}.png", url=url)
    except Exception as e:  # noqa: BLE001
        ev("screenshot failed", name=name, error=str(e)[:200])


async def main():
    from playwright.async_api import async_playwright
    from temporalio.client import Client

    out = {"date": "2026-10-28", "model": D.MODEL, "workflow_id": D.WORKFLOW_ID, "task_queue": D.TASK_QUEUE}
    v = subprocess.run(["temporal", "--version"], capture_output=True, text=True).stdout.strip()
    from importlib.metadata import version
    out["versions"] = {"temporal_cli": v, **{p: version(p) for p in ("temporalio", "temporalio-openai-agents",
                                                                       "openai-agents", "openai")}}
    ev("versions", **out["versions"])
    server = start(["temporal", "server", "start-dev", "--ip", "127.0.0.1", "--port", "7233", "--ui-port", "8233",
                    "--db-filename", "/tmp/temporal.db", "--log-level", "error"], "temporal")
    host = start([sys.executable, "-m", "bahi.course.production.durable", "host"], "host")
    for _ in range(60):
        try:
            client = await Client.connect("localhost:7233", plugins=[D.plugin(None)])
            import httpx
            httpx.get("http://127.0.0.1:8711/state", timeout=2)
            break
        except Exception:  # noqa: BLE001
            await asyncio.sleep(1)
    ev("temporal dev server and Bahi host up")
    w1 = worker("worker-1")

    ask = ("Reorder 20,000 of the 5-litre silicone gaskets (GSK-SIL-05L) for the Diwali run, cost centre PRD-07, "
           "need by 9 Nov. Check the stock first.")
    h = await client.start_workflow(D.AskRasoiOrder.run, args=[ask, 20, 5], id=D.WORKFLOW_ID, task_queue=D.TASK_QUEUE)
    ev("workflow started", run_id=h.result_run_id)

    async def wait_stage(want, timeout=300):
        t = time.time()
        while time.time() - t < timeout:
            try:
                st = await h.query(D.AskRasoiOrder.status)
                if st["stage"] in want:
                    return st
            except Exception:  # noqa: BLE001
                pass
            await asyncio.sleep(0.5)
        raise TimeoutError(f"stage {want} not reached")

    st = await wait_stage({"waiting for Kavita"})
    ev("agent turn 1 done: waiting for Kavita", reply=st["replies"][-1]["agent"])
    await h.signal(D.AskRasoiOrder.user_says, "Yes, go ahead.")
    ev("signal sent: user_says('Yes, go ahead.')")
    st = await wait_stage({"waiting for Rohit", "done", "stopped: request AP"})
    ev("agent turn 2 done", stage=st["stage"], request_no=st["request_no"], reply=st["replies"][-1]["agent"])
    out["after_turn2_bahi"] = bahi_state()

    pw = await async_playwright().start()
    br = await pw.chromium.launch()
    page = await br.new_page(viewport={"width": 1600, "height": 1400}, device_scale_factor=1)
    ui = f"http://localhost:8233/namespaces/default/workflows/{D.WORKFLOW_ID}/{h.result_run_id}"
    await shot(page, f"http://localhost:8233/namespaces/default/workflows", "ui_list_running", "AskRasoiOrder")
    await shot(page, f"{ui}/history", "ui_waiting_for_rohit", "Running")

    # one reminder fires while we wait (the 24-hour timer is 20 s in the drill)
    t = time.time()
    while time.time() - t < 60:
        st = await h.query(D.AskRasoiOrder.status)
        if st["reminders"] >= 1:
            break
        await asyncio.sleep(1)
    ev("timer fired, reminder sent", reminders=st["reminders"])

    # ---- crash 1: while waiting for Rohit
    calls_w1 = sum(1 for l in open(HTTP_LOG)) if HTTP_LOG.exists() else 0
    kill(w1, "worker-1")
    out["model_calls_by_worker1"] = calls_w1
    r = await asyncio.to_thread(lambda: __import__("httpx").post("http://127.0.0.1:8711/call", json={
        "user": "RMEHTA", "tool": "approve_purchase_request",
        "args": {"request_no": st["request_no"], "decision": "approve", "comment": "ok, approved"}}, timeout=20).json())
    ev("Rohit approved in Bahi (his own session)", ok=r.get("ok"), status=r.get("status"))
    await h.signal(D.AskRasoiOrder.approval_decided, args=["RMEHTA", "approve"])
    ev("signal sent: approval_decided, while NO worker is running")
    await asyncio.sleep(3)
    desc = await h.describe()
    ev("workflow while no worker runs", status=str(desc.status), history_length=desc.raw_description.workflow_execution_info.history_length)
    await shot(page, f"{ui}/history", "ui_signal_no_worker", "approval_decided")

    # ---- worker 2 replays, then crash 2: after the order is saved, before it is released
    n_before = sum(1 for l in open(HTTP_LOG))
    w2 = worker("worker-2")
    killed2 = None
    t = time.time()
    while time.time() - t < 240:
        s = bahi_state()
        pos = [o for o in s["orders"] if o["pr_no"] == st["request_no"]]
        if pos and all(o["status"] != "RL" for o in pos):
            kill(w2, "worker-2")
            killed2 = {"orders_in_bahi": pos}
            ev("order saved, not yet released: worker-2 killed", orders=pos)
            break
        if pos and any(o["status"] == "RL" for o in pos):
            ev("order was released before we could kill worker-2", orders=pos)
            break
        await asyncio.sleep(0.1)
    calls = [json.loads(l) for l in open(HTTP_LOG)]
    out["model_calls_by_worker2"] = sum(1 for c in calls if c["worker"] == "worker-2")
    out["killed2"] = killed2
    w3 = worker("worker-3") if killed2 else None
    res = await asyncio.wait_for(h.result(), timeout=300)
    ev("workflow finished", outcome=res["outcome"], request_no=res["request_no"])
    calls = [json.loads(l) for l in open(HTTP_LOG)]
    out["model_calls"] = {w: sum(1 for c in calls if c["worker"] == w) for w in ("worker-1", "worker-2", "worker-3")}
    out["model_http"] = calls
    out["result"] = res
    out["final_bahi"] = bahi_state()
    out["counts"] = {"requests": len(out["final_bahi"]["requests"]),
                     "orders_for_request": len([o for o in out["final_bahi"]["orders"] if o["pr_no"] == res["request_no"]]),
                     "released": len([o for o in out["final_bahi"]["orders"] if o["status"] == "RL" and o["pr_no"] == res["request_no"]]),
                     "reminders_sent": len([m for m in out["final_bahi"]["messages"] if "Reminder" in (m.get("body") or "") + (m.get("subject") or "")])}
    ev("Bahi after the drill", **out["counts"])

    await shot(page, f"{ui}/history", "ui_completed_history", "Completed")
    await shot(page, f"http://localhost:8233/namespaces/default/workflows", "ui_list_completed", "Completed")
    # the timeline view, if this UI version has it
    await shot(page, f"{ui}/history?view=timeline", "ui_timeline", "Completed")

    hist = await h.fetch_history()
    hj = hist.to_json()
    (LOGS / "durable_history.json").write_text(hj)
    (FIX / "durable_history.json").write_text(hj)
    evs = json.loads(hj)["events"]
    out["history"] = {"events": len(evs),
                      "by_type": {k: sum(1 for e in evs if e["eventType"] == k) for k in sorted({e["eventType"] for e in evs})}}
    acts = [e for e in evs if e["eventType"] == "EVENT_TYPE_ACTIVITY_TASK_SCHEDULED"]
    out["history"]["activities"] = [e["activityTaskScheduledEventAttributes"]["activityType"]["name"] for e in acts]
    starts = [e for e in evs if e["eventType"] == "EVENT_TYPE_ACTIVITY_TASK_STARTED"]
    out["history"]["attempts"] = [e["activityTaskStartedEventAttributes"].get("attempt", 1) for e in starts]
    out["history"]["workers"] = sorted({e.get("workflowTaskCompletedEventAttributes", {}).get("identity", "")
                                        for e in evs if e["eventType"] == "EVENT_TYPE_WORKFLOW_TASK_COMPLETED"} - {""})
    # ---- replay check: the recorded history against the workflow code, no server needed
    rep = await D.replay_history(hj)
    out["replay"] = rep
    ev("replayer on the recorded history", **rep)
    out["events"] = EVENTS
    for p in (w3, host, server):
        if p:
            p.terminate()
    await br.close(); await pw.stop()
    for n in ("worker-1", "worker-2", "worker-3", "host", "temporal"):
        try:
            out.setdefault("process_logs", {})[n] = open(f"/tmp/{n}.log").read()[-3000:]
        except OSError:
            pass
    (LOGS / "durable_order.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
    (FIX / "durable_drill.json").write_text(json.dumps({k: v for k, v in out.items() if k != "process_logs"}, indent=1,
                                                       default=str, ensure_ascii=False))


try:
    asyncio.run(main())
except Exception:
    import traceback
    traceback.print_exc()
    for n in ("worker-1", "worker-2", "worker-3", "host", "temporal"):
        try:
            print(f"----- {n}.log\n" + open(f"/tmp/{n}.log").read()[-4000:])
        except OSError:
            pass
    (LOGS / "durable_order_failed.json").write_text(json.dumps(EVENTS, indent=1, default=str))
    sys.exit(1)
