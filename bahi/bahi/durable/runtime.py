"""Lecture 7: starting Temporal, a worker, a workflow; sending Rohit's approval; reading the history.

Three ways to get a Temporal server, one code path:
    await start_env("time_skipping")   test server that jumps over timers: days pass in seconds (notebooks, drills)
    await start_env("local")           a real dev server on this machine (temporal CLI dev server, downloaded)
    await start_env("connect")         an existing cluster at TEMPORAL_ADDRESS (deploy/: staging, prod)

For code that is not async (the L8 app, a FastAPI handler) use DurableBahi, which runs the same thing on a
background thread and gives plain methods:

    d = DurableBahi(erp)                         # starts a time-skipping server and a worker
    wid = d.start(OrderRequest("KJOSHI", "DP-RJK-0042", "GSK-SIL-05L", 20000, "PRD-07", "2026-11-02", ref="msg-17"))
    d.status(wid)                                # {'stage': 'waiting for approval', 'request_no': 'PR/2026/04417', ...}
    d.approve(wid, by="RMEHTA")                  # Rohit approves IN BAHI (his session), then the signal is sent
    d.result(wid)                                # {'outcome': 'released', 'po_no': 'PO/2026/01182', ...}
"""
from __future__ import annotations

import asyncio
import os
import threading
from datetime import timedelta

from temporalio.client import Client, WorkflowHandle
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

from ..erp.engine import ERP
from .activities import BahiActivities
from .keys import keyed, workflow_id
from .model import Approval, OrderRequest, WaitPolicy
from .workflow import TASK_QUEUE, PurchaseOrderWorkflow


# Stages where a workflow sits still until something outside happens (or it has finished).
SETTLED = ("waiting for approval", "released", "needs a person", "failed", "rejected", "expired", "paused")


def quiet_logs():
    """For notebooks and drills: the SDK logs every failed activity attempt with a full traceback (and the test server's
    core prints a capability warning). Retries are the point of the drills, so we show them in tables instead.
    Production keeps the default logging: there you want every retry in the logs."""
    import logging

    for name in ("temporalio.worker._activity", "temporalio.activity", "temporalio.worker._workflow_instance"):
        logging.getLogger(name).setLevel(logging.ERROR)
    try:
        from temporalio.runtime import LoggingConfig, Runtime, TelemetryConfig, TelemetryFilter

        Runtime.set_default(Runtime(telemetry=TelemetryConfig(logging=LoggingConfig(
            filter=TelemetryFilter(core_level="ERROR", other_level="ERROR")))), error_if_already_set=False)
    except Exception:  # older/newer SDKs: the Python loggers above are what matters
        pass


async def start_env(kind: str = "time_skipping"):
    if kind == "time_skipping":
        return await WorkflowEnvironment.start_time_skipping()
    if kind == "local":
        return await WorkflowEnvironment.start_local()
    if kind == "connect":
        client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"),
                                      namespace=os.environ.get("TEMPORAL_NAMESPACE", "default"))
        return WorkflowEnvironment.from_client(client)
    raise ValueError(kind)


def make_worker(client: Client, acts: BahiActivities, identity: str | None = None, cache: bool = True,
                task_queue: str = TASK_QUEUE) -> Worker:
    """cache=False makes every workflow step replay from the history (no sticky cache), which is what a worker
    that has just restarted has to do anyway; the crash drills use it so the replay is visible."""
    return Worker(client, task_queue=task_queue, workflows=[PurchaseOrderWorkflow], activities=acts.all(),
                  identity=identity, max_cached_workflows=1000 if cache else 0,
                  workflow_runner=SandboxedWorkflowRunner(
                      restrictions=SandboxRestrictions.default.with_passthrough_modules("bahi")))


async def start_order(client: Client, o: OrderRequest, policy: WaitPolicy | None = None) -> WorkflowHandle:
    o = keyed(o)
    return await client.start_workflow(PurchaseOrderWorkflow.run, args=[o, policy or WaitPolicy()],
                                       id=workflow_id(o), task_queue=TASK_QUEUE)


async def status(h: WorkflowHandle) -> dict:
    return await h.query(PurchaseOrderWorkflow.status)


async def wait_until(h: WorkflowHandle, test, timeout_s: float = 60.0, every_s: float = 0.05) -> dict:
    """Poll the status query (real time) until test(status) is true."""
    loop = asyncio.get_running_loop()
    t_end = loop.time() + timeout_s
    while True:
        st = await status(h)
        if test(st):
            return st
        if loop.time() > t_end:
            raise TimeoutError(f"workflow {h.id} still at {st['stage']!r}")
        await asyncio.sleep(every_s)


async def approve(erp: ERP, h: WorkflowHandle, by: str = "RMEHTA", decision: str = "A", comment: str = "ok") -> dict:
    """What the app does when Rohit taps Approve: Rohit's own session approves in Bahi, then the workflow is signalled.
    The agent never approves anything itself (Lecture 5)."""
    st = await status(h)
    r = erp.session(by).call("pr_approve", pr_no=st["request_no"], decision=decision, comment=comment)
    await h.signal(PurchaseOrderWorkflow.approval_decided, Approval(by, decision, comment))
    return r


async def history(h: WorkflowHandle) -> list[dict]:
    """The workflow's event history, one plain dict per event: what Temporal recorded, in order."""
    from temporalio.api.enums.v1 import EventType

    hist = await h.fetch_history()
    names, out, t0 = {}, [], None
    for e in hist.events:
        t = e.event_time.ToDatetime()
        t0 = t0 or t
        d = {"id": e.event_id, "type": EventType.Name(e.event_type).removeprefix("EVENT_TYPE_"),
             "at_h": round((t - t0).total_seconds() / 3600, 3)}
        which = e.WhichOneof("attributes")
        a = getattr(e, which) if which else None
        if which == "activity_task_scheduled_event_attributes":
            names[e.event_id] = d["activity"] = a.activity_type.name
        elif which in ("activity_task_started_event_attributes",):
            d["activity"] = names.get(a.scheduled_event_id)
            d["attempt"], d["worker"] = a.attempt, a.identity
            if a.HasField("last_failure"):
                d["last_failure"] = a.last_failure.message[:160]
        elif which in ("activity_task_completed_event_attributes", "activity_task_failed_event_attributes",
                       "activity_task_timed_out_event_attributes"):
            d["activity"] = names.get(a.scheduled_event_id)
            if which == "activity_task_failed_event_attributes":
                d["failure"] = a.failure.message[:160]
        elif which == "timer_started_event_attributes":
            d["fires_after_h"] = round(a.start_to_fire_timeout.ToTimedelta().total_seconds() / 3600, 3)
        elif which == "workflow_execution_signaled_event_attributes":
            d["signal"] = a.signal_name
        elif which == "workflow_task_started_event_attributes":
            d["worker"] = a.identity
        out.append(d)
    return out


class DurableBahi:
    """A synchronous handle on a Temporal server + one worker, running on a background thread."""

    def __init__(self, erp: ERP, kind: str | None = None, flags=None, identity: str = "bahi-worker-1"):
        # kind defaults to BAHI_TEMPORAL (time_skipping | local | connect), so an app that builds DurableBahi(erp)
        # with no arguments (the Lecture 5 app) runs on whatever Temporal the deployment chose.
        kind = kind or os.environ.get("BAHI_TEMPORAL", "time_skipping")
        self.erp = erp
        self.acts = BahiActivities(erp, flags)
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.env = self._run(start_env(kind))
        self.client = self.env.client

        async def _mk():  # a Worker must be built on the loop that will run it
            return make_worker(self.client, self.acts, identity=identity)
        self.worker = self._run(_mk())
        self._task = asyncio.run_coroutine_threadsafe(self.worker.run(), self.loop)
        self.handles: dict[str, WorkflowHandle] = {}

    def _run(self, coro, timeout: float = 120):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)

    def start(self, o: OrderRequest, policy: WaitPolicy | None = None) -> str:
        """Start the workflow for this order. Starting the same order twice returns the same workflow id
        (Temporal refuses a second running workflow with that id), so a double-click is harmless."""
        from temporalio.exceptions import WorkflowAlreadyStartedError

        try:
            h = self._run(start_order(self.client, o, policy))
        except WorkflowAlreadyStartedError:
            h = self.client.get_workflow_handle(workflow_id(o))
        self.handles[h.id] = h
        return h.id

    def _h(self, wid: str) -> WorkflowHandle:
        return self.handles.get(wid) or self.client.get_workflow_handle(wid)

    def status(self, wid: str) -> dict:
        return self._run(status(self._h(wid)))

    def wait_for(self, wid: str, stage, timeout_s: float = 60) -> dict:
        """Block until the workflow reaches `stage` (a name, or a tuple of names)."""
        stages = (stage,) if isinstance(stage, str) else tuple(stage)
        return self._run(wait_until(self._h(wid), lambda s: s["stage"] in stages, timeout_s), timeout_s + 5)

    def approve(self, wid: str, by: str = "RMEHTA", decision: str = "A", comment: str = "ok") -> dict:
        return self._run(approve(self.erp, self._h(wid), by, decision, comment))

    def recheck(self, wid: str, timeout_s: float = 60) -> dict:
        """Ask a waiting workflow to look in Bahi now (e.g. Kavita says "Rohit approved it"). Returns the settled status."""
        h = self._h(wid)

        async def go():
            st = await status(h)
            if st["stage"] != "waiting for approval":
                return await wait_until(h, lambda s: s["stage"] in SETTLED, timeout_s)
            await h.signal(PurchaseOrderWorkflow.recheck)
            await wait_until(h, lambda s: s["checks"] > st["checks"] or s["stage"] not in
                             ("waiting for approval", "checking the approval in Bahi"), timeout_s)
            return await wait_until(h, lambda s: s["stage"] in SETTLED, timeout_s)
        return self._run(go(), 2 * timeout_s + 5)

    def skip(self, hours: float):
        """Time-skipping server only: let `hours` pass at once (timers fire)."""
        self._run(self.env.sleep(timedelta(hours=hours)))

    def result(self, wid: str, timeout: float = 120) -> dict:
        return self._run(self._h(wid).result(), timeout)

    def history(self, wid: str) -> list[dict]:
        return self._run(history(self._h(wid)))

    def close(self):
        async def _stop():
            await self.worker.shutdown()
            await self.env.shutdown()
        try:
            self._run(_stop(), 30)
        finally:
            self.loop.call_soon_threadsafe(self.loop.stop)
