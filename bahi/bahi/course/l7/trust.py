"""The trust layer: deterministic code between Ask Rasoi's model and the toolbox. No model is called here.

    tools = MCPClientTools(MCPClient(build_toolbox_server(erp, "KJOSHI")))
    safe = TrustLayer(tools, erp, end_user="KJOSHI", session_user="KJOSHI")
    safe.call("create_purchase_order", {...})   # refused with a reason and a next step, or passed through and read back

Every tool call goes through four checks, in this order:
  1. identity    a write from a service-account session is refused (POL-APR-002 §4.2)
  2. approvals   an approve tool runs only when the signed-in user is the approver Bahi is waiting for
  3. preview     a commit (confirm=true) must follow a preview of the same document in an EARLIER user turn
                 (a purchase order made from a request a human has approved counts as confirmed)
  4. guard       never-events refused before the write: NE1 release without a proper approver, NE2 a second live
                 order for the same item and supplier, NE3 a food-contact part from a supplier with no valid
                 food-grade certificate (Purchase Policy §6.2), NE4 a new supplier who already exists
After a successful write, read_back() asks Bahi what it now holds, in the user's own session (order_status).
gate_reply() checks the final message: "done" while an order is not RELEASED gets corrected (NE5).

Bahi is read here through erp.q()/erp.orders(): a read-only view in front of the ERP, the same thing the toolbox's
_peek() does. In a real plant, ask IT for that view.
"""
from __future__ import annotations

import json
import re

from ...scenarios import DONE_WORDS
from ...toolbox import SPECS

SERVICE_ACCOUNTS = {"SVC_AGENT"}
WRITES = {n for n, s in SPECS.items() if s.writes}
COMMITS = {"create_purchase_request", "create_purchase_order", "register_supplier", "receive_goods"}  # have a preview
APPROVES = {"approve_purchase_request", "approve_purchase_order"}
NOT_DONE = re.compile(r"draft|pending|approval|waiting|not (?:yet )?released|closed", re.I)
DOC_RE = re.compile(r"\b(?:PO|PR)/\d{4}/\d{5}\b")


def as_dict(out) -> dict:
    if isinstance(out, dict):
        return out
    try:
        d = json.loads(out)
        return d if isinstance(d, dict) else {"value": d}
    except Exception:  # noqa: BLE001
        return {"text": str(out)}


def signature(name: str, args: dict) -> str:
    """What makes two calls 'the same document': the tool and its arguments, without confirm."""
    a = {k: v for k, v in (args or {}).items() if k != "confirm" and v not in (None, "")}
    return name + json.dumps(a, sort_keys=True, default=str)


class TrustLayer:
    """Wraps any tool set with .schemas() and .call(name, args) (Toolbox or MCPClientTools)."""

    def __init__(self, tools, erp, end_user: str, session_user: str | None = None, checks=("identity", "approvals",
                                                                                            "preview", "guard", "read_back")):
        self.tools, self.erp, self.end_user = tools, erp, end_user
        self.session_user = session_user or end_user
        self.checks = set(checks)
        self.names = getattr(tools, "names", [])
        self.turn = 0
        self.previewed: dict[str, int] = {}   # signature -> the user turn it was previewed in
        self.docs: dict[str, dict] = {}       # documents written in this conversation -> last receipt
        self.events: list[dict] = []          # every decision this layer took, for the trace

    # ------------------------------------------------------------------ plumbing
    def schemas(self):
        return self.tools.schemas()

    def begin_turn(self):
        self.turn += 1

    def call(self, name: str, args: dict | None = None) -> dict:
        args = dict(args or {})
        no = self.before(name, args)
        if no:
            self.events.append({"turn": self.turn, "tool": name, "decision": "refused", **no})
            return no
        out = as_dict(self.tools.call(name, args))
        if out.get("ok") and "preview" in out and name in COMMITS:
            self.previewed[signature(name, args)] = self.turn
        if out.get("ok") and name in WRITES and "preview" not in out and "read_back" in self.checks:
            rb = self.read_back(name, out)
            if rb:
                out["read_back"] = rb
                self.events.append({"turn": self.turn, "tool": name, "decision": "read back", **rb})
        return out

    def _no(self, rule: str, why: str, next_step: str, ne: str = "") -> dict:
        return {"ok": False, "refused_by": "trust layer", "never_event": ne or None, "rule": rule, "error": why,
                "next_step": next_step}

    # ------------------------------------------------------------------ the checks before a call
    def before(self, name: str, a: dict) -> dict | None:
        if name not in WRITES:
            return None
        if "identity" in self.checks and self.session_user in SERVICE_ACCOUNTS:
            return self._no("POL-APR-002 §4.2", f"This assistant is signed in to Bahi as {self.session_user}, a service "
                            "account. A service account has no authority to raise, approve or release documents.",
                            "Sign in as the person who is asking; the tools then act with that person's own permissions.",
                            "NE1")
        if "approvals" in self.checks and name in APPROVES:
            doc = a.get("request_no") or a.get("po_no")
            w = self.erp.q1("SELECT approver FROM approval WHERE doc_no=? AND status='PENDING' ORDER BY appr_id DESC", doc)
            if not w or w["approver"] != self.end_user:
                who = w["approver"] if w else "nobody (it is not waiting for approval)"
                return self._no("POL-APR-002 §4.1", f"{doc} waits for {who}, not for {self.end_user}.",
                                f"It is in {who}'s approvals inbox. Only they can approve it, in their own session.", "NE1")
        if "preview" in self.checks and name in COMMITS and a.get("confirm") is True:
            seen = self.previewed.get(signature(name, a))
            from_approved_request = name == "create_purchase_order" and a.get("request_no") and \
                (self.erp.q1("SELECT status FROM pr_hdr WHERE pr_no=?", a["request_no"]) or {}).get("status") == "AP"
            if not from_approved_request and (seen is None or seen >= self.turn):
                return self._no("preview before commit", "This would save a document the user has not seen.",
                                "Call it with confirm=false, show the preview, and ask the user. Commit in a later turn, "
                                "after a clear yes.")
        if "guard" in self.checks:
            return self.guard(name, a)
        return None

    def guard(self, name: str, a: dict) -> dict | None:
        q1 = self.erp.q1
        if name == "create_purchase_order":
            itm = a.get("item_code")
            if a.get("request_no"):
                ln = q1("SELECT itm_cd FROM pr_line WHERE pr_no=?", a["request_no"])
                itm = ln["itm_cd"] if ln else itm
            sup = a.get("supplier_code")
            item = q1("SELECT food_contact, descr FROM item WHERE itm_cd=?", itm) if itm else None
            if item and item["food_contact"] and sup and not q1(
                    "SELECT 1 FROM sup_cert WHERE sup_cd=? AND cert_type='FOOD-GRADE' AND valid_to>=?", sup, self.erp.today):
                return self._no("Purchase Policy §6.2", f"{itm} ({item['descr']}) touches food, and {sup} has no valid "
                                "food-grade certificate on file in Bahi.", "Do not order. Tell the user the certificate "
                                "must be uploaded and checked before the first order.", "NE3")
            if a.get("confirm") is True and sup and itm:
                live = [o for o in self.erp.orders(sup_cd=sup, itm_cd=itm) if o["status"] != "CN"
                        and o["created_on"] >= self.erp.today and o["created_by"] == self.session_user]
                if live:
                    o = live[0]
                    return self._no("one order per need", f"{o['po_no']} for {itm} from {sup} was already saved today "
                                    f"(status {o['status']}).", f"Use order_status {o['po_no']}. Ask the user before "
                                    "placing a second order.", "NE2")
        if name == "release_purchase_order":
            o = (self.erp.orders(**{"h.po_no": a.get("po_no")}) or [None])[0] if a.get("po_no") else None
            if o:
                limit = (self.erp.user(o["created_by"]) or {}).get("appr_limit") or 0
                if o["created_by"] in SERVICE_ACCOUNTS:
                    limit = 0
                if o["gross_value"] > limit and o["approved_by"] in (None, o["created_by"], *SERVICE_ACCOUNTS):
                    pr = q1("SELECT approved_by FROM pr_hdr WHERE pr_no=?", o["pr_no"]) if o["pr_no"] else None
                    if not pr or pr["approved_by"] in (None, o["created_by"], *SERVICE_ACCOUNTS):
                        return self._no("POL-APR-002 §3", f"{o['po_no']} is worth ₹{o['gross_value']:,.0f}, above "
                                        f"{o['created_by']}'s limit, and no proper approver has signed it.",
                                        "Route it to the approver; do not release.", "NE1")
        if name == "register_supplier" and a.get("name") and a.get("city"):
            first = a["name"].split()[0].lower()
            twins = [s for s in self.erp.q("SELECT sup_cd, name, city, status FROM supplier")
                     if s["name"].lower().startswith(first) and (s["city"] or "").lower() == a["city"].lower()]
            if twins:
                t = twins[0]
                return self._no("Supplier Policy §6.2", f"'{a['name']}' in {a['city']} looks like {t['name']} "
                                f"({t['sup_cd']}), already in Bahi.", "Use that supplier code. Register a new one only "
                                "if the user confirms it is a different firm.", "NE4")
        return None

    # ------------------------------------------------------------------ after a write
    def read_back(self, name: str, out: dict) -> dict | None:
        """Ask Bahi, in the user's own session, what the document really is now."""
        doc = out.get("po_no") or out.get("request_no")
        if not doc:
            return None
        arg = {"po_no": doc} if doc.startswith("PO/") else {"request_no": doc}
        held = as_dict(self.tools.call("order_status", arg))
        self.docs[doc] = held
        said = out.get("status")
        rb = {"doc": doc, "tool_said": said, "bahi_holds": held.get("status"),
              "sent_to_supplier": held.get("sent_to_supplier"), "agrees": said == held.get("status")}
        if held.get("warning"):
            rb["warning"] = held["warning"]
        return rb

    def gate_reply(self, reply: str) -> tuple[str, dict | None]:
        """NE5: never let the last message say 'done' about an order that is not released."""
        if "read_back" not in self.checks:
            return reply, None
        open_docs = []
        for doc in self.docs:
            if doc.startswith("PO/"):
                o = (self.erp.orders(**{"h.po_no": doc}) or [None])[0]
                if o and o["status"] != "RL":
                    open_docs.append((doc, o["status"]))
        if open_docs and DONE_WORDS.search(reply or "") and not NOT_DONE.search(reply or ""):
            doc, st = open_docs[0]
            fix = (f"\n\nCorrection, read back from Bahi: {doc} is in status {st}. It has NOT been released to the "
                   "supplier yet.")
            ev = {"turn": self.turn, "tool": "reply", "decision": "corrected", "doc": doc, "status": st}
            self.events.append(ev)
            return reply + fix, ev
        return reply, None
