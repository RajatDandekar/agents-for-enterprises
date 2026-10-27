"""Lecture 7: the agent's intent tools, with the commit handed to the durable workflow.

The model still talks to the same eight tools with the same names and arguments (Lecture 3). Two things change:
  * create_purchase_order with confirm=true no longer runs the commit inside the chat turn. It starts the
    PurchaseOrder workflow (id = "po-" + content key) and reports where it stands: usually WAITING FOR APPROVAL.
    The chat can end, the server can restart; the workflow carries on and releases the order after approval.
  * release_purchase_order for a workflow's order is the workflow's job, so the tool just reports its status.
Every write also passes the kill switch / rollout flags first (killswitch.Flags).

    tools = DurableIntentTools(IntentTools(erp.session("KJOSHI")), durable=DurableBahi(erp), flags=Flags())
    agent = ToolLoopAgent(erp, "KJOSHI", tools=tools)
"""
from __future__ import annotations

import json

from .keys import workflow_id
from .killswitch import Flags, WritesPaused
from .model import OrderRequest
from .runtime import SETTLED



class DurableIntentTools:
    def __init__(self, tools, durable, flags: Flags | None = None):
        self.tools, self.durable = tools, durable
        self.flags = flags or durable.acts.flags
        self.names = tools.names
        self.started: dict[str, str] = {}  # idempotency_key the model used -> workflow id

    def schemas(self):
        return self.tools.schemas()

    def _order(self, a: dict) -> OrderRequest:
        return order_from_tool_args(self.tools.s.user_id, a)

    def _settle(self, wid: str, fresh: bool) -> dict:
        if fresh:
            return self.durable.wait_for(wid, SETTLED, timeout_s=60)
        return self.durable.recheck(wid)  # look in Bahi now: Rohit may have approved since

    def _report(self, wid: str, st: dict) -> dict:
        out = {"ok": True, "workflow_id": wid, "stage": st["stage"].upper(), "request_no": st["request_no"],
               "po_no": st["po_no"]}
        if st["po_no"]:
            out["receipt"] = self.tools.call("order_status", {"po_no": st["po_no"]})
        if st["stage"] == "waiting for approval":
            out["next_step"] = ("Tell the user the request is with the approver. Once approved, the order is created and "
                                "released by the workflow; when the user says it is approved, call order_status.")
        elif st["stage"] == "needs a person":
            out["next_step"] = "The order was saved but not approved for release (see the receipt's warning). Tell the user."
        elif st["stage"] == "paused":
            out["next_step"] = "Writes are switched off by the operators. Tell the user the order is held, nothing lost."
        return out

    def call(self, name: str, args: dict, by_human: bool = False) -> dict:
        if name == "create_purchase_order" and args.get("confirm"):
            try:
                self.flags.check_write(self.tools.s.user_id, by_human=True)  # Kavita confirmed in the chat
            except WritesPaused as e:
                return {"ok": False, "paused": True, "error": f"Nothing was saved. {e.why}",
                        "next_step": "Tell the user plainly that nothing was saved and why."}
            try:
                o = self._order(args)
            except (KeyError, ValueError, TypeError) as e:
                return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}
            fresh = o.key not in self.started
            wid = self.durable.start(o)
            self.started[o.key] = wid
            return self._report(wid, self._settle(wid, fresh))
        if name in ("order_status", "release_purchase_order") and self.started:
            # the workflow owns these orders: let it look in Bahi first, then report what Bahi holds
            want = args.get("idempotency_key")
            wids = [w for k, w in self.started.items() if not want or k == want] or list(self.started.values())
            sts = [(w, self._settle(w, False)) for w in wids]
            if name == "release_purchase_order":
                mine = [x for x in sts if x[1]["po_no"] == args.get("po_no")] or sts
                w, st = mine[-1]
                return {**self._report(w, st), "note": "The workflow releases its order itself once it is approved."}
            if not args.get("po_no") or any(st["po_no"] == args.get("po_no") for _, st in sts):
                w, st = sts[-1] if not args.get("po_no") else next(x for x in sts if x[1]["po_no"] == args["po_no"])
                return self._report(w, st)
        return self.tools.call(name, args)

    def call_json(self, name: str, args: dict) -> str:
        return json.dumps(self.call(name, args), default=str)


def order_from_tool_args(user: str, args: dict) -> OrderRequest:
    """The OrderRequest that create_purchase_order(confirm=true) would start a workflow for. It carries EXACTLY the key
    the intent tool would use (the model's idempotency_key, or the tool's own content key when the model left it out),
    so an order started by the tool and one started by the workflow find each other in Bahi (client_ref, "key:" remark)."""
    from ..agent import tools as T

    key = args.get("idempotency_key") or T.content_key(user, args["supplier_code"], args["item_code"],
                                                       int(args["quantity"]), args["cost_centre"], args["need_by"])
    return OrderRequest(user, args["supplier_code"], args["item_code"], int(args["quantity"]), args["cost_centre"],
                        args["need_by"], args.get("rate"), ref=str(args.get("idempotency_key") or ""), key=key)


__all__ = ["DurableIntentTools", "order_from_tool_args", "workflow_id"]
