"""Lecture 7: idempotency keys derived from content.

A key must be the same every time the SAME order is attempted, and different for a different order.
So it is a hash of what the order is, never a random uuid4():

  * a random key changes on every retry, so the retry cannot find the first attempt;
  * a random key changes on every notebook run, so a recorded model reply no longer matches (replay breaks).

`ref` is what separates two orders that are identical on purpose (Emma really does want two lots of
2,000). In the app it is the id of the chat message that confirmed the order; a retry of that message
keeps the id, a new message gets a new one.
"""
from __future__ import annotations

import hashlib
import json

from .model import OrderRequest

FIELDS = ("user", "supplier_code", "item_code", "quantity", "cost_centre", "need_by", "rate", "ref")


def content_key(*parts, prefix: str = "K", n: int = 12) -> str:
    """sha256 of the canonical JSON of the parts, shortened. Same parts, same key, on every machine."""
    blob = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str)
    return prefix + hashlib.sha256(blob.encode()).hexdigest()[:n].upper()


def order_key(o: OrderRequest) -> str:
    return content_key(*[getattr(o, f) for f in FIELDS])


def keyed(o: OrderRequest) -> OrderRequest:
    """The order with its key filled in (the caller's object is not changed)."""
    from dataclasses import replace

    return o if o.key else replace(o, key=order_key(o))


def workflow_id(o: OrderRequest) -> str:
    """The workflow id IS the key: Temporal refuses to start a second running workflow with the same id,
    so a double-click on Confirm cannot start two workflows for one order."""
    return "po-" + keyed(o).key
