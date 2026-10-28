"""A small control graph in LangGraph, over the v3 toolbox: when the business process must be followed.

    g = ControlGraph(Toolbox(erp, "KJOSHI"), LLM(cassette="L5v3_graph"))
    g.respond("Reorder 20,000 of the 5-litre gaskets from Deccan Polymers, PRD-07, need-by 9 November.")
    g.respond("Yes, go ahead.")                                     # resumes the Confirm interrupt
    g.respond("Bahi notification: Rohit Mehta has approved PR/2026/04417.")   # resumes Wait for approval

The spine (always, in this order):  understand > look up > preview > confirm > raise request >
wait for approval > create order > release > reply.
Gates (checked in code after look up; each opens a detour only when it is true):
    supplier not in the master       > hold, say so
    food-contact item, no valid food-grade certificate > hold, cite Purchase Policy §6.2
    cost centre missing or closed    > ask for an open one (an interrupt), then look up again
    above the direct-order cap       > the request route (raise request, wait for approval)
The model is used for two things only: reading the message into fields (understand) and answering open
questions (a free loop with read-only tools, inside one node). Every reply about a document is written by
code from the receipt, so it cannot call an order "placed" before Bahi says RELEASED.
"""
from __future__ import annotations

import json
import operator
import re
from typing import Annotated, TypedDict

from ...llm import LLM
from .harness import Harness, inr

READ_ONLY = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy", "order_status",
             "list_my_approvals"]
YES = re.compile(r"\b(yes|yeah|yep|go ahead|ok|okay|confirm(?:ed)?|proceed|sure|do it|please do|correct)\b", re.I)
CC = re.compile(r"\b([A-Z]{3}-\d{2})\b")

UNDERSTAND = """Read the message from {name} ({user}) at Rasoi Steel Works into fields. Today is 2026-10-26.
Reply with one JSON object and nothing else, with these keys:
 intent: "order" (wants something bought), "receive" (goods arrived, record them), "status" (where is an order or request), or "question" (anything else, including policy or stock questions)
 item: the item as said (words or code), or null
 quantity: integer, or null
 supplier: the supplier's name as said, or null
 cost_centre: a code like PRD-07, or null
 need_by: YYYY-MM-DD, or null
 po_no: like PO/2026/01182, or null
 request_no: like PR/2026/04417, or null
 tell_approver: true if they ask you to message or tell the approver, else false"""


class S(TypedDict, total=False):
    text: str
    intent: str
    ask: dict          # what the person wants: item, quantity, supplier, cost_centre, need_by ...
    facts: dict        # what look up found in Bahi
    docs: dict         # request_no, po_no: the documents this thread made
    route: str         # "direct" or "request"
    out: str           # the reply
    path: Annotated[list, operator.add]


class ControlGraph:
    def __init__(self, tb, llm: LLM | None = None, thread: str | None = None):
        from langgraph.graph import END, START, StateGraph
        try:
            from langgraph.checkpoint.memory import InMemorySaver as Saver
        except ImportError:
            from langgraph.checkpoint.memory import MemorySaver as Saver
        self.tb, self.llm = tb, llm or LLM(cassette="L5v3_graph")
        u = tb.erp.user(tb.user)
        self.name, self.first = u["name"], u["name"].split()[0]
        self.trace: list[dict] = []
        self.turn = 0
        g = StateGraph(S)
        for n in ("understand", "look_up", "ask_missing", "hold", "preview", "confirm", "commit", "wait_approval",
                  "create_order", "release", "receive", "status", "answer"):
            g.add_node(n, getattr(self, "n_" + n))
        g.add_edge(START, "understand")
        g.add_conditional_edges("understand", lambda s: {"order": "look_up", "receive": "receive",
                                                         "status": "status"}.get(s["intent"], "answer"))
        g.add_conditional_edges("look_up", self.gates, ["ask_missing", "hold", "preview"])
        g.add_edge("ask_missing", "look_up")
        g.add_edge("preview", "confirm")
        g.add_conditional_edges("confirm", lambda s: "commit" if s.get("route") != "cancel" else END)
        g.add_conditional_edges("commit", lambda s: {"PA": "wait_approval", "AP": "create_order",
                                                     "PO-AP": "release"}.get(s["facts"].get("next"), END))
        g.add_conditional_edges("wait_approval", lambda s: {"AP": "create_order", "PA": "wait_approval"}.get(
            s["facts"].get("pr_status"), END))
        g.add_conditional_edges("create_order", lambda s: "release" if s["facts"].get("po_status") == "AP" else END)
        for n in ("hold", "release", "receive", "status", "answer"):
            g.add_edge(n, END)
        self.graph = g.compile(checkpointer=Saver())
        self.cfg = {"configurable": {"thread_id": thread or f"{tb.user}-thread"}}

    # ------------------------------------------------------------------ the public face
    def respond(self, text: str) -> str:
        from langgraph.types import Command
        self.turn += 1
        snap = self.graph.get_state(self.cfg)
        if snap.next:  # a node is waiting in an interrupt: this message is its answer
            self.trace.append({"turn": self.turn, "kind": "graph", "node": "resume", "waiting_in": list(snap.next)})
            st = self.graph.invoke(Command(resume=text), self.cfg)
        else:          # a new run on the same thread: the documents carry over, the ask starts fresh
            docs = (snap.values or {}).get("docs", {}) if snap else {}
            st = self.graph.invoke({"text": text, "ask": {}, "facts": {}, "docs": docs, "route": "", "out": ""},
                                   self.cfg)
        pending = st.get("__interrupt__") or []
        if pending:  # stopped in an interrupt: the question it asks is the reply
            val = getattr(pending[0], "value", None) or {}
            self.trace.append({"turn": self.turn, "kind": "graph", "node": "interrupt", "payload": val})
            return (val.get("ask") if isinstance(val, dict) else None) or st.get("out", "")
        return st.get("out", "")

    @property
    def path(self) -> list:
        return (self.graph.get_state(self.cfg).values or {}).get("path", [])

    def waiting_in(self) -> list:
        return list(self.graph.get_state(self.cfg).next)

    def _who(self, user_id):
        try:
            return f"{self.tb.erp.user(user_id)['name']} ({user_id})"
        except Exception:  # noqa: BLE001
            return str(user_id)

    def _call(self, node, name, args):
        out = self.tb.call(name, args)
        self.trace.append({"turn": self.turn, "kind": "tool", "node": node, "name": name, "args": args,
                           "ok": bool(out.get("ok")), "result": out})
        return out

    # ------------------------------------------------------------------ nodes
    def n_understand(self, s: S):
        msg = [{"role": "system", "content": UNDERSTAND.format(name=self.name, user=self.tb.user)},
               {"role": "user", "content": s["text"]}]
        r = self.llm.chat(msg, response_format={"type": "json_object"})
        try:
            raw = r.content or "{}"
            got = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        except (json.JSONDecodeError, ValueError):
            got = {"intent": "question"}
        ask = {**(s.get("ask") or {}), **{k: v for k, v in got.items() if v not in (None, "") and k != "intent"}}
        self.trace.append({"turn": self.turn, "kind": "model", "node": "understand", "fields": got,
                           "tokens_in": r.tokens_in, "tokens_out": r.tokens_out})
        return {"intent": got.get("intent", "question"), "ask": ask, "path": ["understand"]}

    def n_look_up(self, s: S):
        a, f = s["ask"], dict(s.get("facts") or {})
        if a.get("item") and not f.get("item_code"):
            items = self._call("look_up", "find_item", {"query": str(a["item"])}).get("items") or []
            if items:
                f.update(item_code=items[0]["item_code"], item_label=items[0].get("description"),
                         food_contact=bool(items[0].get("food_contact")))
        if a.get("supplier") and not f.get("supplier_code") and not f.get("supplier_missing"):
            r = self._call("look_up", "find_supplier", {"name": str(a["supplier"])})
            best = next((m for m in r.get("matches", []) if m["status"] == "ACTIVE" and m["match"] >= 0.6), None)
            if best:
                f.update(supplier_code=best["supplier_code"], supplier_label=best["name"],
                         cert=best["food_grade_certificate"], said_as=a["supplier"])
            else:
                f["supplier_missing"] = True
        cc = a.get("cost_centre")
        if cc and f.get("cc_checked") != cc:
            b = self._call("look_up", "check_budget", {"cost_centre": cc})
            f.update(cc_checked=cc, cc_state=("OPEN" if b.get("open") else "CLOSED") if b.get("ok") else "UNKNOWN")
        return {"facts": f, "path": ["look_up"]}

    def gates(self, s: S) -> str:
        a, f = s["ask"], s["facts"]
        if f.get("supplier_missing"):
            return "hold"
        if f.get("food_contact") and f.get("supplier_code") and f.get("cert") != "valid":
            return "hold"
        missing = [k for k in ("item_code", "supplier_code") if not f.get(k)] + \
                  [k for k in ("quantity", "need_by", "cost_centre") if not a.get(k)]
        if missing or f.get("cc_state") != "OPEN":
            return "ask_missing"
        return "preview"

    def n_ask_missing(self, s: S):
        from langgraph.types import interrupt
        a, f = s["ask"], s["facts"]
        need = []
        if not f.get("item_code"):
            need.append("which item (name or code)")
        if not f.get("supplier_code"):
            need.append("which supplier")
        if not a.get("quantity"):
            need.append("how many")
        if not a.get("need_by"):
            need.append("the need-by date")
        q = ""
        if not a.get("cost_centre") or f.get("cc_state") != "OPEN":
            opened = self._call("ask_missing", "check_budget", {})
            names = ", ".join(c.get("code", "") for c in (opened.get("open") or [])
                              if isinstance(c, dict))[:120]
            bad = a.get("cost_centre")
            q = (f"Cost centre {bad} is closed in Bahi, so an order on it would sit in Draft. " if bad else
                 "Which cost centre pays for this? ") + (f"Open ones: {names}. " if names else "") + \
                ("Which open cost centre should I use?" if bad else "")
        if need:
            q = f"To raise this I still need: {', '.join(need)}. " + q
        answer = interrupt({"ask": q})
        ask = dict(a)
        m = CC.search(answer or "")
        if m:
            ask["cost_centre"] = m.group(1)
        if need:
            more = self.n_understand({"text": answer, "ask": ask})
            ask = more["ask"]
        facts = {k: v for k, v in f.items() if k not in ("cc_checked", "cc_state")}
        return {"ask": ask, "facts": facts, "out": q, "path": ["ask_missing"]}

    def n_hold(self, s: S):
        a, f = s["ask"], s["facts"]
        if f.get("supplier_missing"):
            out = (f"{a.get('supplier')} is not in Bahi's supplier master, so I cannot order from them. A new supplier "
                   f"has to be onboarded first")
            if f.get("food_contact"):
                out += (", and for a food-contact part like this they also need a valid food-grade certificate "
                        "(Purchase Policy §6.2). Do you have their certificate?")
            else:
                out += "."
        else:
            out = (f"{f['supplier_label']} ({f['supplier_code']}) has no valid food-grade certificate "
                   f"({f.get('cert')}). {f.get('item_label') or a.get('item')} touches food, so Purchase Policy §6.2 "
                   "does not allow this order. Nothing has been ordered. Shall I look at a certified supplier instead?")
        return {"out": out, "path": ["hold"]}

    def n_preview(self, s: S):
        a, f = s["ask"], s["facts"]
        base = {"supplier_code": f["supplier_code"], "item_code": f["item_code"], "quantity": int(a["quantity"]),
                "cost_centre": a["cost_centre"], "need_by": a["need_by"]}
        if a.get("rate"):
            base["rate"] = float(a["rate"])
        po = self._call("preview", "create_purchase_order", base)
        same = f.get("said_as") and str(f["said_as"]).lower() != f["supplier_label"].lower()
        who = f"{f['supplier_label']} ({f['supplier_code']})" + (f", which is how Bahi knows '{f['said_as']}'"
                                                                 if same else "")
        if po.get("ok"):
            p = po["preview"]
            out = (f"Preview, nothing saved yet: a direct order to {who} for {p['quantity']:,} {f['item_code']} at "
                   f"₹{p['rate']:.2f} = {inr(p['gross_value'])} incl. GST, cost centre {p['cost_centre']}, need-by "
                   f"{p['need_by']}. Shall I place it?")
            return {"route": "direct", "facts": {**f, "preview": p}, "out": out, "path": ["preview"]}
        pr = self._call("preview", "create_purchase_request", {k: base[k] for k in
                                                               ("item_code", "quantity", "cost_centre", "need_by")})
        p = pr.get("preview", {})
        appr = (f" It is above your {inr(p['your_limit'])} limit, so it will wait for {self._who(p['approver'])} to approve."
                if p.get("needs_approval") else " It is within your limit.")
        out = (f"Preview, nothing saved yet: this is above the ₹50,000 direct-order cap, so it needs a purchase request "
               f"first. Request: {p.get('quantity', 0):,} {f['item_code']}, estimated {inr(p.get('estimated_value', 0))} "
               f"incl. GST, cost centre {p.get('cost_centre')}, need-by {p.get('need_by')}.{appr} Once approved I will "
               f"order from {who} and release it. Shall I raise the request?")
        return {"route": "request", "facts": {**f, "preview": p}, "out": out, "path": ["preview"]}

    def n_confirm(self, s: S):
        from langgraph.types import interrupt
        answer = interrupt({"ask": s["out"]})
        if YES.search(answer or ""):
            return {"path": ["confirm"]}
        return {"route": "cancel", "out": "OK, nothing has been saved.", "path": ["confirm"]}

    def n_commit(self, s: S):
        a, f = s["ask"], s["facts"]
        if s["route"] == "direct":
            args = {"supplier_code": f["supplier_code"], "item_code": f["item_code"], "quantity": int(a["quantity"]),
                    "cost_centre": a["cost_centre"], "need_by": a["need_by"], "confirm": True}
            r = self._call("commit", "create_purchase_order", args)
            docs = {**s.get("docs", {}), "po_no": r.get("po_no")}
            if r.get("status_code") == "AP":
                return {"docs": docs, "facts": {**f, "next": "PO-AP"}, "path": ["commit"]}
            return {"docs": docs, "facts": {**f, "next": "stop"}, "out": self._po_words(r), "path": ["commit"]}
        r = self._call("commit", "create_purchase_request", {"item_code": f["item_code"], "quantity": int(a["quantity"]),
                                                            "cost_centre": a["cost_centre"], "need_by": a["need_by"],
                                                            "confirm": True})
        docs = {**s.get("docs", {}), "request_no": r.get("request_no")}
        if not r.get("ok"):
            return {"docs": docs, "facts": {**f, "next": "stop"}, "out": f"Bahi refused the request: {r.get('error')}",
                    "path": ["commit"]}
        if r.get("status_code") == "PA":
            out = (f"I raised purchase request {r['request_no']} for {r['quantity']:,} {r['item_code']}, estimated "
                   f"{inr(r['estimated_value'])} incl. GST. It is waiting for {self._who(r['approver'])} to approve. Nothing is "
                   f"ordered yet; I will carry on as soon as Bahi shows it approved.")
            if a.get("tell_approver"):
                handle = "@rohit" if r["approver"] == "RMEHTA" else r["approver"]
                self._call("commit", "send_message", {"to": handle, "text": f"{r['request_no']} for {r['quantity']:,} "
                           f"{r['item_code']} ({inr(r['estimated_value'])}) needs your approval. Thanks, {self.first}"})
                out += f" I have messaged {handle} about it."
            return {"docs": docs, "facts": {**f, "next": "PA"}, "out": out, "path": ["commit"]}
        return {"docs": docs, "facts": {**f, "next": "AP"}, "path": ["commit"]}

    def n_wait_approval(self, s: S):
        from langgraph.types import interrupt
        pr = s["docs"]["request_no"]
        interrupt({"waiting_on": "approver", "doc": pr})       # the thread sleeps here, saved, for minutes or days
        st = self._call("wait_approval", "order_status", {"request_no": pr})   # whatever the message said: ask Bahi
        code = st.get("status_code")
        if code == "AP":
            return {"facts": {**s["facts"], "pr_status": "AP"}, "path": ["wait_approval"]}
        if code == "RJ":
            return {"facts": {**s["facts"], "pr_status": "RJ"}, "path": ["wait_approval"],
                    "out": f"Bahi shows {pr} as REJECTED by {st.get('approved_by') or 'the approver'}. Nothing has "
                           f"been ordered."}
        return {"facts": {**s["facts"], "pr_status": "PA"}, "path": ["wait_approval"],
                "out": f"Still waiting: Bahi shows {pr} as {st.get('status')}, with {self._who(st.get('approver'))}. Nothing has "
                       f"been ordered yet."}

    def n_create_order(self, s: S):
        f = s["facts"]
        r = self._call("create_order", "create_purchase_order", {"supplier_code": f["supplier_code"],
                                                                 "request_no": s["docs"]["request_no"], "confirm": True})
        docs = {**s["docs"], "po_no": r.get("po_no")}
        out = "" if r.get("status_code") == "AP" else self._po_words(r)
        return {"docs": docs, "facts": {**f, "po_status": r.get("status_code")}, "out": out, "path": ["create_order"]}

    def n_release(self, s: S):
        r = self._call("release", "release_purchase_order", {"po_no": s["docs"]["po_no"]})
        return {"out": self._po_words(r), "path": ["release"]}

    def _po_words(self, r: dict) -> str:
        if not r.get("ok"):
            return f"Bahi refused it: {r.get('error')} {r.get('next_step', '')}".strip()
        sup = r.get("supplier_code")
        try:
            sup = f"{self.tb.erp.q1('SELECT name FROM supplier WHERE sup_cd=?', sup)['name']} ({sup})"
        except Exception:  # noqa: BLE001
            pass
        head = (f"{r['po_no']} to {sup} for {r['quantity']:,} {r['item_code']} at ₹{r['rate']:.2f}, "
                f"{inr(r['gross_value'])} incl. GST")
        if r.get("status_code") == "RL":
            return f"Done. {head}, is RELEASED to the supplier (need-by {r['need_by']})."
        return f"{head}, is {r['status']}. {r.get('warning') or r.get('next_step') or ''}".strip()

    def n_receive(self, s: S):
        from langgraph.types import interrupt
        a = s["ask"]
        po, qty = a.get("po_no") or s.get("docs", {}).get("po_no"), a.get("quantity")
        if not po or not qty:
            return {"out": "Which order did the goods come against (PO number), and how many arrived?",
                    "path": ["receive"]}
        pv = self._call("receive", "receive_goods", {"po_no": po, "quantity": int(qty)})
        if not pv.get("ok"):
            return {"out": f"I cannot record it: {pv.get('error')} {pv.get('next_step', '')}", "path": ["receive"]}
        p = pv["preview"]
        answer = interrupt({"ask": f"Record {p['receiving_now']:,} {p['item_code']} against {po} into "
                                   f"{p['warehouse']}? Ordered {p['ordered']:,}, received before {p['received_before']:,}, "
                                   f"balance after {p['balance_after']:,}."})
        if not YES.search(answer or ""):
            return {"out": "OK, nothing recorded.", "path": ["receive"]}
        r = self._call("receive", "receive_goods", {"po_no": po, "quantity": int(qty), "confirm": True})
        if not r.get("ok"):
            return {"out": f"Bahi refused it: {r.get('error')}", "path": ["receive"]}
        out = (f"Recorded {r['grn_no']}: {r['received']:,} {r['item_code']} against {po}. Stock now "
               f"{r['stock_after']:,}. " + ("The order is now closed: everything has arrived." if r["order_closed"]
                                            else f"Still to come: {r['balance']:,}."))
        return {"out": out, "docs": {**s.get("docs", {}), "po_no": po}, "path": ["receive"]}

    def n_status(self, s: S):
        a, d = s["ask"], s.get("docs", {})
        po, pr = a.get("po_no") or d.get("po_no"), a.get("request_no") or d.get("request_no")
        if po:
            r = self._call("status", "order_status", {"po_no": po})
            got = f" Received {r.get('received', 0):,}" + (f" ({', '.join(r['goods_receipts'])})"
                                                          if r.get("goods_receipts") else "") + "."
            return {"out": f"{po}: {r.get('status')}.{got}", "path": ["status"]}
        if pr:
            r = self._call("status", "order_status", {"request_no": pr})
            return {"out": f"{pr}: {r.get('status')}" + (f", with {r['approver']}" if r.get("approver") else "") +
                           ". No purchase order yet." if r.get("status_code") != "CL" else f"{pr}: {r.get('status')}.",
                    "path": ["status"]}
        return self.n_answer(s)

    def n_answer(self, s: S):
        h = Harness(self.tb, self.llm, tools=READ_ONLY)                 # a free loop, inside one node, read-only
        out = h.respond(s["text"])
        for t in h.trace:
            self.trace.append({**t, "turn": self.turn, "node": "answer"})
        return {"out": out, "path": ["answer"]}
