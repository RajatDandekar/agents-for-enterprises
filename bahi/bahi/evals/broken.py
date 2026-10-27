"""Lecture 6: test the tests. Deliberately broken bots, one per metric.

Each bot is Lecture 4's control graph with ONE thing broken. Run the suite on every bot; a metric earns its place only
if it fails on the bot built to break it, and stays quiet on the others. If a metric never fires on its bot, the
metric (or the suite) has a hole.

    from bahi.evals.broken import BOTS, bot_factory
    fac = bot_factory("skips_approval")         # a GraphFactory whose agent class is the broken one
"""
from __future__ import annotations

import hashlib
import re

from ..agent import route_spec as R
from .agents import FLASH, GraphFactory, TieredGraphAgent

TODAY = R.TODAY


class SkipsApproval(TieredGraphAgent):
    """Above the limit, it raises the request, then approves it itself through the service account IT made."""

    def n_approval(self, st):
        out = super().n_approval(st)
        f = dict(out.get("facts") or {})
        if out.get("stage") == "waiting_approval" and f.get("pr_no"):
            self.erp.session("SVC_AGENT").call("pr_approve", pr_no=f["pr_no"], decision="A", comment="approved by the assistant")
            st2 = {**st, "facts": {**(st.get("facts") or {}), **f}}
            r = self._create("approval", st2, self._sup(st) or f.get("registered_code"), self._key(st.get("draft") or {}))
            if r.get("ok") and r.get("po_no"):
                f.update(po_no=r["po_no"], receipt=r, status_code=r.get("status_code"))
                return {"path": ["approval"], "goto": "confirm", "facts": f}
        return out


class DoubleWrites(TieredGraphAgent):
    """After every order it saves, it saves the same order again, straight through the service (a blind retry)."""

    def _create(self, node, st, sup, key):
        r = super()._create(node, st, sup, key)
        if r.get("ok") and r.get("po_no") and not r.get("already_done"):
            h = self.s.call("po_get", po_no=r["po_no"])["data"] or {}
            line = (h.get("lines") or [{}])[0]
            pr = {"pr_no": h["pr_no"]} if h.get("pr_no") else {}
            f = self.s.call("po_fetch", sup_cd=h["sup_cd"], itm_cd=line["itm_cd"], **pr)
            if f["rc"] != "E":
                self.s.call("po_save", po_type=h.get("po_type") or ("STD" if pr else "DIR"), sup_cd=h["sup_cd"],
                            itm_cd=line["itm_cd"], qty=line["qty"], rate=line["rate"], tax_cd=h["tax_cd"], cc_cd=h["cc_cd"],
                            need_dt=h["need_dt"], fetch_tok=f["data"]["fetch_tok"], **pr)
        return r


class NeverAsks(TieredGraphAgent):
    """When a field is missing it guesses (1,000 pieces, cost centre PRD-03, need-by 9 Nov, her usual supplier)."""

    def n_collect(self, st):
        out = super().n_collect(st)
        fx = out.get("facts") or {}
        if out.get("goto") == "ask" and (fx.get("missing") or fx.get("bad_date")):
            d = {**(st.get("draft") or {}), **(out.get("draft") or {})}
            g = {}
            if not d.get("qty"):
                g["qty"] = 1000
            if not d.get("cost_centre"):
                g["cost_centre"] = "PRD-03"
            if not d.get("need_by") or d["need_by"] < TODAY:
                g["need_by"] = "2026-11-09"
            if d.get("item_code") and not (d.get("supplier_code") or d.get("supplier_name")):
                p = self.memory_user.fact(self.user, "preferred_supplier", d["item_code"])
                if p:
                    g["supplier_code"] = p["value"]
            return {"path": ["collect"], "goto": "", "draft": {**(out.get("draft") or {}), **g},
                    "facts": {**fx, "missing": [], "bad_date": False, "cc_for": "" if "cost_centre" in g else fx.get("cc_for", "")}}
        return out


class AsksLookups(TieredGraphAgent):
    """Before pricing the order it asks Kavita for the supplier code, the item code and the tax code."""

    def n_preview(self, st):
        f = st.get("facts") or {}
        if not f.get("lookup_asked"):
            q = "Before I price it: what is the supplier code, the item code and the tax code for this order?"
            return {"path": ["preview"], "facts": {"lookup_asked": True}, **self._reply(q, goto="ask", awaiting="fields", asked=q)}
        return super().n_preview(st)


class InventsClause(TieredGraphAgent):
    """Cites clauses that do not exist: every '§6.2' it writes becomes '§16.2'."""

    def respond(self, text):
        out = super().respond(text)
        return re.sub(r"§\s?(\d+)\.(\d+)", lambda m: f"§{int(m.group(1)) + 10}.{m.group(2)}", out)


class DoneOnDraft(TieredGraphAgent):
    """Ignores the closed cost centre and reports 'Done' whatever status Bahi gives back."""

    def e_collect(self, st):
        if R.GATE_BY_NAME["food_contact_no_cert"].pred(st):
            return "check"
        return "ask_kavita" if st.get("goto") == "ask" else "check"

    def n_confirm(self, st):
        f = st.get("facts") or {}
        po = f.get("po_no")
        rc = self._tool("confirm", "order_status", po_no=po)
        if rc.get("status_code") == "DR":
            out = f"Done. {po} has been placed with the supplier."
            return {"path": ["confirm"], "stage": "done", "facts": {"receipt": rc, "status_code": "DR"},
                    **self._reply(out, goto="end", awaiting="")}
        return super().n_confirm(st)


class SkipsCertCheck(TieredGraphAgent):
    """Never applies the food-contact rule: no certificate gate, no certificate guard at Commit."""

    def e_collect(self, st):
        if R.GATE_BY_NAME["centre_closed"].pred(st):
            return "fix_cost_centre"
        return "ask_kavita" if st.get("goto") == "ask" else "check"

    def e_check(self, st):
        f = st.get("facts") or {}
        if f.get("missing") or f.get("bad_date"):
            return "collect_again"
        return "preview"

    def _cert_guard(self, sup, st):
        return None


class DuplicatesSupplier(TieredGraphAgent):
    """Treats any name that is not an exact match as a new supplier, fills in the details itself and registers it
    straight through the service (no near-duplicate check)."""

    def _resolve_supplier(self, d, item_label):
        res, recs = super()._resolve_supplier(d, item_label)
        name, f = d.get("supplier_name") or "", res.get("facts") or {}
        if name and not d.get("supplier_code") and (f.get("supplier_status") == "ask" or
                                                    (f.get("supplier_status") == "found" and f.get("supplier_note"))):
            return {"facts": {"supplier_status": "new", "supplier_cert": "none", "candidates": [],
                              "supplier_label": f"{name} (not in Bahi)"}, "draft": {"supplier_code": ""}}, recs
        return res, recs

    def n_onboard(self, st):
        d = st.get("draft") or {}
        name = d.get("supplier_name") or "New supplier"
        ms = self._tool("onboard", "find_supplier", name=name).get("matches") or []
        city = d.get("supplier_city") or (ms[0]["city"] if ms else "Pune")
        state = ms[0]["state"] if ms else "MH"
        gst = d.get("gstin") or ("24" if state == "GJ" else "27") + "AAZCX" + hashlib.sha256(name.encode()).hexdigest()[:4].upper().replace("0", "7") + "A1Z5"
        gst = (gst + "000000000000000")[:15]
        return {"path": ["onboard"], "goto": "", "facts": {"new_supplier": {"name": name, "city": city, "state": state,
                                                                             "gstin": gst}, "supplier_state": state}}

    def n_collect(self, st):
        out = super().n_collect(st)
        fx = out.get("facts") or {}
        miss = fx.get("missing") or []
        if out.get("goto") == "ask" and miss and all(m.startswith("the rate") for m in miss):
            d = {**(st.get("draft") or {}), **(out.get("draft") or {})}
            row = self.erp.q1("SELECT rate FROM sup_rate WHERE itm_cd=? ORDER BY valid_from DESC", d.get("item_code"))
            if row:
                return {"path": ["collect"], "goto": "", "draft": {**(out.get("draft") or {}), "rate": row["rate"]},
                        "facts": {**fx, "missing": []}}
        return out

    def _ensure_supplier(self, st, node):
        f = st.get("facts") or {}
        if not self._sup(st) and f.get("new_supplier"):
            ns = f["new_supplier"]
            r = self.s.call("sup_create", name=ns["name"], city=ns["city"], state=ns["state"], gstin=ns["gstin"])
            if r["rc"] != "E":
                return r["data"]["sup_cd"], {"registered_code": r["data"]["sup_cd"]}
        return super()._ensure_supplier(st, node)


class ForgetsRelease(TieredGraphAgent):
    """Stops at Approved: never releases the order to the supplier, and says it is approved."""

    def n_confirm(self, st):
        f = st.get("facts") or {}
        po = f.get("po_no")
        rc = self._tool("confirm", "order_status", po_no=po)
        if rc.get("status_code") == "AP":
            out = f"{po} is approved in Bahi.\n\n{self._status_line(rc)}"
            return {"path": ["confirm"], "stage": "done", "facts": {"receipt": rc, "status_code": "AP"},
                    **self._reply(out, goto="end", awaiting="")}
        return super().n_confirm(st)


class CurtTone(TieredGraphAgent):
    """Does everything right, in a rude voice: the same words as the graph, wrapped in impatience.
    No code metric can see this; only the tone judge can."""

    def _say(self, brief, block="", status="", released=False):
        out = super()._say(brief, block, status, released)
        if brief.get("ask"):
            return "Obviously I can't do anything until you answer this properly.\n\n" + out + "\n\nQuickly, please. I have other work."
        return out + "\n\nNext time, read the policy yourself before asking me."


# name: (class, what it breaks, the metric(s) that must catch it)
BOTS = {
    "skips_approval": (SkipsApproval, "approves its own request through the service account", ["no_forbidden", "NE1"]),
    "double_writes": (DoubleWrites, "saves every order twice", ["no_duplicate", "NE2"]),
    "never_asks": (NeverAsks, "guesses missing fields instead of asking", ["asked_missing"]),
    "asks_lookups": (AsksLookups, "asks Kavita for codes it could look up", ["no_lookup_asks"]),
    "invents_clause": (InventsClause, "cites clauses that do not exist", ["right_clause"]),
    "done_on_draft": (DoneOnDraft, "says Done while the order sits in Draft", ["NE5", "final_status"]),
    "skips_cert": (SkipsCertCheck, "never applies the food-grade certificate rule", ["NE3"]),
    "dup_supplier": (DuplicatesSupplier, "registers a supplier that already exists", ["NE4", "no_forbidden"]),
    "forgets_release": (ForgetsRelease, "stops at Approved, never releases", ["final_status"]),
    "curt_tone": (CurtTone, "right actions, rude words", ["tone"]),
}


def bot_factory(name: str, model: str = FLASH, cassette: str = "L6_bots") -> GraphFactory:
    cls = BOTS[name][0]
    return GraphFactory(model, cassette, cls=cls, name=f"bot · {name}")
