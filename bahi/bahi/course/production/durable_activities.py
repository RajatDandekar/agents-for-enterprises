"""Lecture 11, durable execution: the activities. Everything that touches the world lives here.

An activity is an ordinary function that Temporal runs, times out, retries and RECORDS. Its result goes into the
workflow's event history, so after a crash the workflow reads it back instead of running it again.

Bahi is the world outside the worker. In the drill it runs as its own small HTTP service (erp_host below), so that
killing a worker does not kill the ERP, exactly as in a plant. Each tool activity calls one toolbox tool in
Kavita's own Bahi session (Lecture 7's identity rule). The toolbox's write tools carry content-derived idempotency
keys (Lecture 7), so an activity that is retried after a crash finds the document it already wrote.
"""
from __future__ import annotations

import os

from temporalio import activity

HOST = os.environ.get("BAHI_HOST", "http://127.0.0.1:8711")
USER = "KJOSHI"


async def _call(tool: str, args: dict, user: str = USER) -> dict:
    import httpx

    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{HOST}/call", json={"user": user, "tool": tool,
                                                "args": {k: v for k, v in args.items() if v is not None}})
        r.raise_for_status()
        return r.json()


# ------------------------------------------------------------------ tools the agent may call (activity_as_tool)
@activity.defn
async def check_stock(item_code: str) -> dict:
    """Stock of an item in every plant: on hand, on order, daily use and days of cover. item_code e.g. GSK-SIL-05L."""
    return await _call("check_stock", {"item_code": item_code})


@activity.defn
async def find_supplier(name: str) -> dict:
    """Look a supplier up by name, tolerating different spellings. Returns code, status and food-grade certificate."""
    return await _call("find_supplier", {"name": name})


@activity.defn
async def search_policy(question: str) -> dict:
    """Search Rasoi's purchase policy and the Bahi manual; returns clauses with citations like POL-PUR-001 §6.2."""
    return await _call("search_policy", {"question": question})


@activity.defn
async def create_purchase_request(item_code: str, quantity: int, cost_centre: str, need_by: str,
                                  confirm: bool = False) -> dict:
    """Raise a purchase request. confirm=false (default) is a preview and saves nothing; confirm=true saves it after
    the user has said yes. need_by is YYYY-MM-DD. Above the user's limit it waits for the approver."""
    return await _call("create_purchase_request", {"item_code": item_code, "quantity": quantity,
                                                   "cost_centre": cost_centre, "need_by": need_by, "confirm": confirm})


@activity.defn
async def create_purchase_order(supplier_code: str, request_no: str, confirm: bool = False) -> dict:
    """Make a purchase order from an APPROVED purchase request. confirm=false previews; confirm=true saves it."""
    return await _call("create_purchase_order", {"supplier_code": supplier_code, "request_no": request_no,
                                                 "confirm": confirm})


@activity.defn
async def release_purchase_order(po_no: str) -> dict:
    """Release an approved purchase order to the supplier, e.g. PO/2026/01182."""
    return await _call("release_purchase_order", {"po_no": po_no})


@activity.defn
async def order_status(request_no: str) -> dict:
    """Where a purchase request and its order stand, read from Bahi, e.g. PR/2026/04417."""
    return await _call("order_status", {"request_no": request_no})


TOOLS = [check_stock, find_supplier, search_policy, create_purchase_request, create_purchase_order,
         release_purchase_order, order_status]


# ------------------------------------------------------------------ activities the workflow calls itself
@activity.defn
async def read_back_request(user: str) -> dict:
    """Read-back (Lecture 7): ask Bahi for the newest purchase request this user raised, and its status."""
    import httpx

    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{HOST}/latest_request", params={"user": user})
        r.raise_for_status()
        return r.json()


@activity.defn
async def remind(to: str, text: str) -> dict:
    """A reminder to the approver, through the toolbox's send_message tool."""
    return await _call("send_message", {"to": to, "text": text})


WORKFLOW_ACTIVITIES = [read_back_request, remind]


# ------------------------------------------------------------------ the ERP host: Bahi as a separate process
def erp_host_app():
    """FastAPI app holding one Bahi ERP in memory. POST /call {user, tool, args}; GET /latest_request; GET /state."""
    import threading

    from fastapi import FastAPI

    from ...erp.engine import ERP
    from ...toolbox import Toolbox

    erp = ERP()
    lock = threading.Lock()
    app = FastAPI(title="Bahi ERP host (drill)")
    calls: list[dict] = []

    @app.post("/call")
    def call(body: dict):
        with lock:
            out = Toolbox(erp, body["user"]).call(body["tool"], body.get("args") or {})
            calls.append({"user": body["user"], "tool": body["tool"], "args": body.get("args"),
                          "ok": out.get("ok") if isinstance(out, dict) else None})
            return out

    @app.get("/latest_request")
    def latest(user: str):
        with lock:
            r = erp.q1("SELECT pr_no, status, approved_by, est_value FROM pr_hdr WHERE raised_by=? "
                       "ORDER BY raised_on DESC, pr_no DESC LIMIT 1", user)
            return dict(r) if r else {"pr_no": None, "status": None}

    @app.get("/state")
    def state():
        with lock:
            return {"requests": erp.q("SELECT pr_no, status, approved_by, raised_by FROM pr_hdr WHERE raised_on>='2026-10-26'"),
                    "orders": erp.q("SELECT po_no, pr_no, sup_cd, status, gross_value FROM po_hdr WHERE pr_no IS NOT NULL "
                                    "AND created_on>='2026-10-26'"),
                    "messages": erp.q("SELECT recipient, subject, body FROM ntf_queue"),
                    "calls": calls}

    return app
