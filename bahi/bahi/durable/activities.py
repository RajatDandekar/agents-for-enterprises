"""Lecture 7: the activities of the purchase-order workflow. Every write here is safe to run twice.

An activity is ordinary code that touches the outside world (here: Bahi). Temporal runs it, and when it fails
or hangs, runs it AGAIN, on whichever worker is alive. So each one follows the same three-line rule:

    1. look for the result of an earlier attempt, by the key   (po_search client_ref=key, pr remarks "key:<key>")
    2. if found, return it; do not write again
    3. otherwise write, carrying the key, and read the result back from Bahi

Errors are sorted into two kinds, because Temporal must know whether trying again can help:
    retryable      ServiceTimeout (reply lost), ERR-SYS-0503 (server busy), the kill switch (pauses the workflow)
    not retryable  any other Bahi refusal (ERR-PO-0603, ERR-APR-0004 ...): retrying cannot change Bahi's answer

SANDBOX SIMPLIFICATION. In production the activities reach Bahi over HTTP (bahi.client / the server in deploy/),
so any worker on any machine can run them and the ERP outlives every worker. In the course the ERP is an
in-memory SQLite object, so the worker is handed ONE shared ERP instance (`BahiActivities(erp)`). The ERP
stands in for "the outside world": when a drill kills a worker, the ERP survives, exactly as a real Bahi
server survives a crash of the agent's machine. Nothing in the workflow depends on this; only the transport does.
"""
from __future__ import annotations

import asyncio
import datetime as dt

from temporalio import activity
from temporalio.exceptions import ApplicationError

from ..erp.engine import ERP, ServiceTimeout
from .killswitch import Flags, WritesPaused
from .model import OrderRequest

RETRYABLE = {"ERR-SYS-0503"}


class BahiActivities:
    def __init__(self, erp: ERP, flags: Flags | None = None, t0=None):
        self.erp = erp
        self.flags = flags or Flags()
        # sandbox time at workflow start (hour 0); activities move the ERP clock along with workflow time.
        # A worker that restarts mid-workflow is given the same t0 (in production both are just the real clock).
        self.t0 = t0 or erp._clock
        self.attempts: list[dict] = []  # every activity attempt this worker ran: name, attempt, result
        self.hang_after_commit: set[str] = set()  # crash drill: freeze right after Bahi commits
        self.hung: list[str] = []

    # ------------------------------------------------------------------ helpers
    def _at(self, t_h: float):
        """Move the sandbox clock to workflow time, so a reminder sent 24 h later carries the right date."""
        target = self.t0 + dt.timedelta(hours=t_h)
        if self.erp._clock < target:
            self.erp.advance(seconds=(target - self.erp._clock).total_seconds())

    def _note(self, name: str, **kw):
        try:
            info = activity.info()
            att, who = info.attempt, info.workflow_id
        except RuntimeError:  # called directly, outside a worker
            att, who = 1, None
        self.attempts.append({"activity": name, "attempt": att, "workflow_id": who, **kw})

    def _guard(self, user: str):
        try:
            self.flags.check_write(user, by_human=True)  # the workflow only runs orders a person confirmed
        except WritesPaused as e:
            raise ApplicationError(e.why, type="KillSwitchOn")

    def _call(self, s, svc: str, **payload) -> dict:
        try:
            r = s.call(svc, **payload)
        except ServiceTimeout as e:
            raise ApplicationError(f"{e}", type="ServiceTimeout")  # retryable: the next attempt checks first
        if r["rc"] == "E":
            if r["err_cd"] in RETRYABLE:
                raise ApplicationError(f"{svc}: {r['msg']} ({r['err_cd']})", type="BahiBusy")
            raise ApplicationError(f"Bahi refused {svc}: {r['msg']} ({r['err_cd']})", {"err_cd": r["err_cd"]},
                                   type="BahiRefused", non_retryable=True)
        return r["data"] or {}

    def receipt(self, s, po_no: str) -> dict:
        h = self._call(s, "po_get", po_no=po_no)
        line = h["lines"][0]
        return {"po_no": po_no, "status_code": h["status"], "supplier_code": h["sup_cd"], "item_code": line["itm_cd"],
                "quantity": line["qty"], "rate": line["rate"], "gross_value": h["gross_value"],
                "cost_centre": h["cc_cd"], "approved_by": h["approved_by"], "client_ref": h["client_ref"],
                "warning": h["warn_cd"]}

    def _find_pr(self, s, o: OrderRequest):
        rows = self._call(s, "pr_search", raised_by=o.user)["rows"]
        return next((p for p in rows if f"key:{o.key}" in (p["remarks"] or "")), None)

    def _price(self, s, o: OrderRequest) -> tuple[float, str, float]:
        rate = o.rate
        if rate is None:
            cur = self._call(s, "sup_rate_get", sup_cd=o.supplier_code, itm_cd=o.item_code)["current"]
            if not cur:
                raise ApplicationError(f"No current rate contract with {o.supplier_code} for {o.item_code}",
                                       type="BahiRefused", non_retryable=True)
            rate = cur["rate"]
        sup = self._call(s, "sup_get", sup_cd=o.supplier_code)
        me = self._call(s, "usr_get", user_id=o.user)
        ou_state = self.erp.q1("SELECT state FROM org_unit WHERE ou_cd=?", me["ou_cd"])["state"]
        tax_cd = "GST18-INTRA" if sup["state"] == ou_state else "GST18-INTER"
        gross = self._call(s, "tax_compute", basic=round(o.quantity * rate, 2), tax_cd=tax_cd)["gross"]
        return rate, tax_cd, gross

    # ------------------------------------------------------------------ activities
    @activity.defn(name="raise_request")
    async def raise_request(self, o: OrderRequest, t_h: float = 0.0) -> dict:
        """Raise and submit the purchase request (orders above ₹50,000 need one). Idempotent by key."""
        self._at(t_h)
        s = self.erp.session(o.user)
        rate, _, gross = self._price(s, o)
        if gross <= 50000:
            self._note("raise_request", result="not needed")
            return {"request_no": None, "status": "NOT_NEEDED", "gross_value": gross, "approver": None}
        self._guard(o.user)
        pr = self._find_pr(s, o)
        found = pr is not None
        if not pr:
            pr = self._call(s, "pr_save", cc_cd=o.cost_centre, need_dt=o.need_by, itm_cd=o.item_code, qty=o.quantity,
                            est_rate=rate, remarks=f"key:{o.key}")
            pr = {"pr_no": pr["pr_no"], "status": "DR"}
        if pr["status"] == "DR":
            self._call(s, "pr_submit", pr_no=pr["pr_no"])
        cur = self._call(s, "pr_get", pr_no=pr["pr_no"])
        appr = self.erp.q1("SELECT approver FROM approval WHERE doc_no=? ORDER BY appr_id DESC", pr["pr_no"])
        out = {"request_no": pr["pr_no"], "status": cur["status"], "gross_value": gross,
               "approver": appr["approver"] if appr else cur["approved_by"], "found_by_key": found}
        self._note("raise_request", result=out["status"], found_by_key=found)
        return out

    @activity.defn(name="request_status")
    async def request_status(self, request_no: str, t_h: float = 0.0) -> dict:
        """Read the request back from Bahi: the signal says Rohit decided; Bahi says what he decided."""
        self._at(t_h)
        s = self.erp.session("KJOSHI")
        pr = self._call(s, "pr_get", pr_no=request_no)
        self._note("request_status", result=pr["status"])
        return {"request_no": request_no, "status": pr["status"], "approved_by": pr["approved_by"]}

    @activity.defn(name="create_order")
    async def create_order(self, o: OrderRequest, request_no: str | None, t_h: float = 0.0) -> dict:
        """Fetch + Save the purchase order, carrying the key in client_ref. Idempotent by key."""
        self._at(t_h)
        s = self.erp.session(o.user)
        rows = self._call(s, "po_search", client_ref=o.key)["rows"]
        if rows:  # an earlier attempt saved it; its reply was lost. Do not save again.
            out = {**self.receipt(s, rows[0]["po_no"]), "found_by_key": True}
            self._note("create_order", result=out["po_no"], found_by_key=True)
            return out
        self._guard(o.user)
        rate, tax_cd, _ = self._price(s, o)
        f = self._call(s, "po_fetch", sup_cd=o.supplier_code, itm_cd=o.item_code,
                       **({"pr_no": request_no} if request_no else {}))
        payload = dict(po_type="STD" if request_no else "DIR", sup_cd=o.supplier_code, itm_cd=o.item_code,
                       qty=o.quantity, rate=rate, tax_cd=tax_cd, cc_cd=o.cost_centre, need_dt=o.need_by,
                       fetch_tok=f["fetch_tok"], client_ref=o.key, **({"pr_no": request_no} if request_no else {}))
        self._note("create_order", result="saving")
        saved = self._call(s, "po_save", **payload)
        if "create_order" in self.hang_after_commit:  # crash drill: Bahi has committed; the worker now freezes
            self.hang_after_commit.discard("create_order")
            self.hung.append(saved["doc_no"])
            await asyncio.Event().wait()  # never returns; the drill kills this worker
        out = {**self.receipt(s, saved["doc_no"]), "found_by_key": False}
        self.attempts[-1]["result"] = out["po_no"]
        return out

    @activity.defn(name="release_order")
    async def release_order(self, user: str, po_no: str, t_h: float = 0.0) -> dict:
        """Release an approved order to the supplier. Idempotent: an order already RL is simply reported."""
        self._at(t_h)
        s = self.erp.session(user)
        h = self.receipt(s, po_no)
        if h["status_code"] == "RL":
            self._note("release_order", result="RL", found_by_key=True)
            return {**h, "already_done": True}
        if h["status_code"] != "AP":
            raise ApplicationError(f"{po_no} is in status {h['status_code']}, not approved; it cannot be released",
                                   {"status": h["status_code"], "warning": h["warning"]},
                                   type="NotReleasable", non_retryable=True)
        self._guard(user)
        self._call(s, "po_release", po_no=po_no)
        out = self.receipt(s, po_no)
        self._note("release_order", result=out["status_code"])
        return out

    @activity.defn(name="notify")
    async def notify(self, user: str, to: str, text: str, tag: str, t_h: float = 0.0) -> dict:
        """Send a reminder / escalation / outcome message. Idempotent by tag, so a retried reminder is sent once."""
        self._at(t_h)
        if self.erp.q1("SELECT id FROM ntf_queue WHERE body LIKE ?", f"%[{tag}]%"):
            self._note("notify", result="already sent", tag=tag)
            return {"sent": False, "already": True, "tag": tag}
        s = self.erp.session(user)
        email = self.erp.user(to)["email"]
        self._call(s, "ntf_send", channel="EMAIL", recipient=email, msg=f"{text} [{tag}]")
        self._note("notify", result="sent", tag=tag, to=to)
        return {"sent": True, "to": to, "at": self.erp._clock.isoformat(timespec="minutes"), "tag": tag}

    @activity.defn(name="writes_enabled")
    async def writes_enabled(self) -> bool:
        return self.flags.writes_enabled()

    def all(self) -> list:
        """The list to hand to Worker(activities=...)."""
        return [self.raise_request, self.request_status, self.create_order, self.release_order, self.notify,
                self.writes_enabled]
