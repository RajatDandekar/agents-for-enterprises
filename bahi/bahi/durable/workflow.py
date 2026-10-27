"""Lecture 7: the commit-and-approval path of Kavita's order as a Temporal workflow.

    raise request ──► wait for Rohit (signal) ──► read the request back ──► create order ──► release ──► receipt
                         │ 24 h: remind Rohit
                         │ 48 h: escalate to the plant head
                         └ 120 h: give up, tell Kavita, leave it to a person

Workflow code must be deterministic: Temporal rebuilds the workflow's state after a crash by running this code
again against the recorded history. So it never calls Bahi, reads a clock or draws a random number itself.
Everything that touches the world is an activity (activities.py); time comes from workflow.now(); timers
come from workflow.wait_condition(..., timeout=...) and workflow.sleep().
"""
from __future__ import annotations

import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from .model import Approval, OrderRequest, WaitPolicy

TASK_QUEUE = "bahi-purchasing"


@workflow.defn(name="PurchaseOrder")
class PurchaseOrderWorkflow:
    def __init__(self) -> None:
        self.stage = "starting"
        self.approval: Approval | None = None
        self.diary: list[dict] = []
        self.reminders = 0
        self.escalated = False
        self.paused_minutes = 0
        self.request_no: str | None = None
        self.po_no: str | None = None
        self.recheck_asked = False
        self.checks = 0  # how many times the workflow has read the request back from Bahi

    # ------------------------------------------------------------------ messages in
    @workflow.signal
    def approval_decided(self, a: Approval) -> None:
        """Rohit (or Anand) decided in Bahi; the app sends this signal so the workflow wakes up."""
        self.approval = a
        self._log("signal: approval_decided", by=a.by, decision=a.decision)

    @workflow.signal
    def recheck(self) -> None:
        """'Something may have changed in Bahi: look now.' Carries no decision, so anyone may send it (the chat app
        when Kavita says 'Rohit approved it', an operator). The workflow believes only what Bahi says."""
        self.recheck_asked = True

    @workflow.query
    def status(self) -> dict:
        return {"stage": self.stage, "request_no": self.request_no, "po_no": self.po_no, "reminders": self.reminders,
                "escalated": self.escalated, "paused_minutes": self.paused_minutes, "checks": self.checks,
                "diary": self.diary}

    # ------------------------------------------------------------------ helpers
    def _h(self) -> float:
        return round((workflow.now() - workflow.info().start_time).total_seconds() / 3600, 2)

    def _log(self, what: str, **detail) -> None:
        self.diary.append({"at_h": self._h(), "what": what, **detail})

    async def _act(self, name: str, *args, p: WaitPolicy):
        return await workflow.execute_activity(
            name, args=[*args, self._h()],
            start_to_close_timeout=timedelta(seconds=p.activity_timeout_s),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=p.retry_initial_s), backoff_coefficient=2.0,
                                     maximum_interval=timedelta(minutes=1), maximum_attempts=p.retry_max_attempts,
                                     non_retryable_error_types=["BahiRefused", "NotReleasable", "KillSwitchOn"]))

    async def _write(self, name: str, *args, p: WaitPolicy):
        """A write activity. If the kill switch is on, pause (re-check every 10 minutes) instead of failing."""
        while True:
            try:
                return await self._act(name, *args, p=p)
            except ActivityError as e:
                cause = e.cause
                if not (isinstance(cause, ApplicationError) and cause.type == "KillSwitchOn"):
                    raise
                if self.stage != "paused":
                    self._log("paused: kill switch on", activity=name)
                prev, self.stage = self.stage, "paused"
                while not await workflow.execute_activity("writes_enabled", start_to_close_timeout=timedelta(seconds=10)):
                    await workflow.sleep(timedelta(minutes=10))
                    self.paused_minutes += 10
                self.stage = prev
                self._log("resumed: writes enabled again", after_minutes=self.paused_minutes)

    async def _wait_for_approval(self, o: OrderRequest, p: WaitPolicy) -> dict | None:
        """Wait for a decision, for days if need be. Wakes up when
          * a signal arrives (approval_decided from the app, or recheck),
          * every poll_every_h hours, because Rohit may approve in Bahi's own approval screen and nobody signals,
          * at each deadline: remind at 24 h, escalate at 48 h, give up at 120 h.
        Every wake-up that might mean a decision is checked by reading the request back from Bahi.
        Returns the read-back once Bahi shows a decision, or None if the workflow gave up."""
        t0 = self._h()
        plan = [(p.remind_after_h, "remind"), (p.escalate_after_h, "escalate"), (p.give_up_after_h, "give_up")]
        i = 0
        while True:
            at_h, action = plan[i]
            left = at_h - (self._h() - t0)
            nap = min(left, p.poll_every_h) if p.poll_every_h else left
            try:
                await workflow.wait_condition(lambda: self.approval is not None or self.recheck_asked,
                                              timeout=timedelta(hours=max(nap, 1 / 3600)))
                woke = "signal"
            except asyncio.TimeoutError:
                woke = "deadline" if nap >= left else "poll"
            # whatever woke us, look in Bahi first: a decision may be there (signalled or not)
            self.stage = "checking the approval in Bahi"
            st = await self._act("request_status", self.request_no, p=p)
            self.checks += 1
            self._log("read back request", why=woke, status=st["status"], approved_by=st["approved_by"])
            self.approval, self.recheck_asked = None, False
            self.stage = "waiting for approval"
            if st["status"] != "PA":
                return st
            if woke != "deadline":
                continue
            if action == "remind":
                self.reminders += 1
                self._log("timer fired: remind approver", after_h=at_h)
                await self._act("notify", o.user, "RMEHTA",
                                f"Reminder: {self.request_no} (₹{self.gross:,.0f}) has waited {at_h:.0f} hours for your approval.",
                                f"remind:{o.key}:1", p=p)
            elif action == "escalate":
                self.escalated = True
                self._log("timer fired: escalate to plant head", after_h=at_h)
                await self._act("notify", o.user, "APATIL",
                                f"Escalation: {self.request_no} (₹{self.gross:,.0f}) for {o.item_code} has waited {at_h:.0f} "
                                f"hours for RMEHTA. It is needed by {o.need_by}.", f"escalate:{o.key}", p=p)
                await self._act("notify", o.user, "RMEHTA", f"Second reminder: {self.request_no} is now with the plant head too.",
                                f"remind:{o.key}:2", p=p)
                self.reminders += 1
            else:
                return None
            i += 1

    # ------------------------------------------------------------------ the run
    @workflow.run
    async def run(self, o: OrderRequest, p: WaitPolicy) -> dict:
        self.gross = 0.0
        self._log("started", key=o.key)
        self.stage = "raising request"
        try:
            req = await self._write("raise_request", o, p=p)
            self.request_no, self.gross = req["request_no"], req["gross_value"]
            self._log("request raised", request_no=req["request_no"], status=req["status"], approver=req["approver"])
            if req["status"] == "PA":
                self.stage = "waiting for approval"
                decided = await self._wait_for_approval(o, p)
                if decided is None:
                    self.stage = "expired"
                    await self._act("notify", o.user, o.user, f"{self.request_no} got no decision in "
                                    f"{p.give_up_after_h:.0f} hours. Nothing was ordered. Please follow up.",
                                    f"expired:{o.key}", p=p)
                    return self._done("expired")
                req = {**req, **decided}
            if req["status"] == "RJ":
                await self._act("notify", o.user, o.user, f"{self.request_no} was rejected. Nothing was ordered.",
                                f"rejected:{o.key}", p=p)
                return self._done("rejected")
            self.stage = "creating order"
            po = await self._write("create_order", o, self.request_no, p=p)
            self.po_no = po["po_no"]
            self._log("order saved", po_no=po["po_no"], status=po["status_code"], found_by_key=po["found_by_key"])
            if po["status_code"] != "AP":
                return self._done("needs a person", receipt=po)  # e.g. DR on a closed cost centre: never call it done
            self.stage = "releasing"
            rel = await self._write("release_order", o.user, po["po_no"], p=p)
            self._log("released", po_no=rel["po_no"], status=rel["status_code"])
            return self._done("released", receipt=rel)
        except ActivityError as e:
            c = e.cause
            msg = c.message if isinstance(c, ApplicationError) else str(c)
            self._log("stopped: activity failed", error=msg)
            return self._done("failed", error=msg)

    def _done(self, outcome: str, **kw) -> dict:
        self.stage = outcome
        self._log("finished", outcome=outcome)
        return {"outcome": outcome, "request_no": self.request_no, "po_no": self.po_no, "reminders": self.reminders,
                "escalated": self.escalated, "paused_minutes": self.paused_minutes, "hours": self._h(),
                "diary": self.diary, **kw}
