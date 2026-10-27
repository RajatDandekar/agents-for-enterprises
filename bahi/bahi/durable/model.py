"""Lecture 7: the plain data that crosses the workflow boundary.

Everything a Temporal workflow receives or returns is written into its event history as JSON, so these are
small dataclasses with no behaviour and no imports from the ERP. The workflow module imports only this file.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OrderRequest:
    """One order Kavita has confirmed. `key` is filled in by keys.order_key() before the workflow starts."""
    user: str
    supplier_code: str
    item_code: str
    quantity: int
    cost_centre: str
    need_by: str              # YYYY-MM-DD
    rate: float | None = None  # None = the current contract rate
    ref: str = ""             # what makes two identical orders different on purpose (e.g. the chat message id)
    key: str = ""             # the idempotency key; also the workflow id ("po-" + key)


@dataclass
class Approval:
    """Rohit's (or, after escalation, Anand's) decision, sent to the workflow as a signal.
    The signal only wakes the workflow. The workflow then reads the request's status back from Bahi,
    because Bahi, not the message, is the record of who approved what."""
    by: str                  # RMEHTA, or APATIL after escalation
    decision: str = "A"      # A = approve, R = reject
    comment: str = ""


@dataclass
class WaitPolicy:
    """How long to wait for the approver before each nudge. Hours of real (or skipped) time."""
    remind_after_h: float = 24.0     # remind the approver
    escalate_after_h: float = 48.0   # tell the plant head (and the approver again)
    give_up_after_h: float = 120.0   # five days: stop, tell Kavita, leave the request for a person
    poll_every_h: float = 4.0        # also look in Bahi every 4 h: Rohit may approve on Bahi's own screen, unsignalled
    retry_initial_s: float = 2.0     # first retry of a failed activity
    retry_max_attempts: int = 6
    activity_timeout_s: float = 30.0  # start-to-close: a call that hangs longer than this is retried


@dataclass
class Step:
    """One line of the workflow's own diary (also visible through the status query)."""
    at_h: float
    what: str
    detail: dict = field(default_factory=dict)
