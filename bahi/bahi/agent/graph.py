"""Lecture 4: the control graph. Code decides which step comes next; the model fills in details and talks to Kavita.

    from bahi.agent.graph import GraphAgent
    agent = GraphAgent(erp, "KJOSHI", llm=LLM("gemini:gemini-3.8-flash", cassette="L4_graph"))
    agent.respond("Reorder 20,000 of the 5-litre gaskets ...")    # -> preview, asks to confirm
    agent.respond("Yes, go ahead.")                                # -> raises the request, waits for Rohit
    agent.respond("Rohit has approved PR/2026/04417.")             # -> reads the approval back from Bahi, orders, releases

The graph is a LangGraph StateGraph built from route_spec.py:
    spine     understand -> route -> collect -> check -> preview -> commit -> confirm
    detours   onboard (supplier_not_found) · fix_cost_centre (centre_closed) · ask_certificate (food_contact_no_cert)
              · approval (over_limit); each gate is a predicate from route_spec.GATES, the default is to skip
    asks      ask_kavita: an interrupt; the next respond() resumes it with her answer
    waits     wait_approval: an interrupt; any message resumes it, and the node reads the approval from Bahi
    branches  answer (policy, order status, stock, other) and hold (stopped, with the draft kept)

State = the draft order, the facts the route looked up, the conversation, the path. A checkpointer keeps it per thread,
so the half-filled order survives between turns (job 5). The model is called for exactly three things: typed decisions
(decide.py), field extraction (structured output) and the words of each reply. Never-events are refused in code at
Commit (see route_spec.INVARIANTS), whatever the model writes.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import operator
import re
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # older LangGraph
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

from ..erp.engine import ERP, ServiceTimeout
from ..llm import LLM
from . import route_spec as R
from .decide import GeminiBackend, decide
from .memory import CompanyMemory, UserMemory
from .tools import CORE, EXTRA, STATUS, IntentTools

TODAY = R.TODAY
GST_STATE = {"24": "GJ", "27": "MH", "19": "WB", "29": "KA", "33": "TN", "07": "DL", "09": "UP", "23": "MP", "08": "RJ",
             "36": "TS", "37": "AP", "32": "KL", "06": "HR", "03": "PB", "10": "BR", "21": "OD", "20": "JH", "22": "CG"}
CERT_QUERY = "food contact parts supplier valid food-grade certificate before first order"
CLAIMS_DONE = re.compile(r"\b(placed|released|done|has been ordered|sent to the supplier|on its way)\b", re.I)


def merge(a: dict | None, b: dict | None) -> dict:
    """Reducer for draft and facts: update keys; {"__reset__": True, ...} starts again."""
    a = dict(a or {})
    if not b:
        return a
    if b.get("__reset__"):
        return {k: v for k, v in b.items() if k != "__reset__"}
    a.update(b)
    return a


class RouteState(TypedDict, total=False):
    messages: Annotated[list, operator.add]   # the conversation (session memory)
    draft: Annotated[dict, merge]             # the half-filled order (job 5)
    facts: Annotated[dict, merge]             # what the route looked up and decided
    intent: str
    awaiting: str                             # what the last question asked for: fields|supplier|cert|confirm|intent
    asked: str                                # the last question, verbatim
    out: str                                  # this turn's reply
    goto: str                                 # a node's own request: "ask" | "wait" | "confirm" | "commit" | "hold"
    stage: str                                # "" | done | held | cancelled | waiting_approval
    path: Annotated[list, operator.add]       # every node visited, in order
    decisions: Annotated[list, operator.add]  # every typed decision, with its confidence


class GuardError(Exception):
    """Commit refused: an invariant from route_spec.INVARIANTS would break."""


def inr(x) -> str:
    """₹ with Indian digit grouping: 280840 -> ₹2,80,840; 11.9 -> ₹11.90."""
    if x is None:
        return "—"
    neg, x = x < 0, abs(float(x))
    whole, paise = int(x), round((x - int(x)) * 100)
    if paise == 100:
        whole, paise = whole + 1, 0
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        s = head + "," + tail
    return ("-" if neg else "") + "₹" + s + (f".{paise:02d}" if paise else "")


def nice_date(d: str) -> str:
    try:
        return dt.date.fromisoformat(d).strftime("%-d %b %Y")
    except (ValueError, TypeError):
        return d or "—"


def _skey(d: dict) -> str:
    return json.dumps([d.get("supplier_name") or "", d.get("supplier_code") or ""])


def _tok(text: str) -> list[str]:
    out = []
    for w in re.findall(r"\d+(?:\.\d+)?|[a-z]+", (text or "").lower()):
        if w in ("litre", "litres", "liter", "liters", "ltr", "lit"):
            w = "l"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        if w not in ("the", "for", "and", "of", "from", "our", "a", "an", "pc", "nos", "piece"):
            out.append(w)
    return out


EXTRACT = {
    "supplier_name": "the supplier's name exactly as she wrote it",
    "supplier_code": "a Bahi supplier code if she gave one, e.g. DP-RJK-0042",
    "supplier_city": "the supplier's city if she said it",
    "gstin": "the supplier's GSTIN if she gave it",
    "item_description": "the item in her words, e.g. '5-litre silicone gaskets'",
    "item_code": "a Bahi item code if she gave one, e.g. GSK-SIL-05L",
    "quantity": "number of pieces, digits only, no commas",
    "rate": "price per piece in rupees if she gave one, digits only",
    "cost_centre": "cost centre code, e.g. PRD-07",
    "need_by": "need-by date as YYYY-MM-DD",
    "certificate_ref": "food-grade certificate reference number, if she gave one",
    "certificate_valid_to": "that certificate's expiry date as YYYY-MM-DD",
}
FLAGS = {
    "use_usual_supplier": "she asks for the usual/regular supplier without naming one",
    "use_usual_cost_centre": "she asks for her usual cost centre without naming one",
    "repeat_last_order": "she asks to repeat her last order of this item",
}

SAY = """You are the purchasing assistant inside Bahi ERP for {name} ({user}) at Rasoi Steel Works, Pune. Today is Monday 26 October 2026.
Write your reply to {first} from the brief: one to three short sentences, plain words, no greeting, no lists, no markdown.
Use only the facts in the brief. Never invent a code, number, date or status.
Never say an order is placed, done or released unless the brief's status is RELEASED.
If the brief has "ask", end with that one question in your own words and ask nothing else; otherwise ask nothing.
Code appends a block with the exact figures after your words, so do not repeat all of them."""


class GraphAgent:
    """respond(text) -> str, for run_scenario. Approvals arrive as ordinary messages ("Rohit has approved PR/...");
    the graph never trusts the message and reads the approval back from Bahi."""

    def __init__(self, erp: ERP, user: str = "KJOSHI", llm: LLM | None = None, k: int = 3, threshold: float = 0.8,
                 thread_id: str | None = None, user_memory: UserMemory | None = None,
                 company_memory: CompanyMemory | None = None, checkpointer=None, decide_backend=None):
        self.erp, self.user = erp, user
        self.llm = llm or LLM(cassette="L4_graph")
        self.s = erp.session(user)
        self.tools = IntentTools(self.s, CORE + EXTRA)
        self.k, self.threshold = k, threshold
        self.decide_backend = decide_backend
        self.memory_user = user_memory or UserMemory()
        if user not in self.memory_user.data:
            self.memory_user.learn(self.s)
        self.memory_company = company_memory or CompanyMemory()
        self.me = self.s.call("usr_get", user_id=user)["data"]
        self.name, self.first = self.me["name"], self.me["name"].split()[0]
        self.thread_id = thread_id or f"{user}-1"
        self.config = {"configurable": {"thread_id": self.thread_id}, "recursion_limit": 80}
        self.tool_log: list[dict] = []
        self._people: dict[str, str] = {}
        self.graph = build_graph(self, checkpointer or InMemorySaver())

    # ------------------------------------------------------------------ the one public method
    def respond(self, text: str) -> str:
        if self.pending():
            inp = Command(resume=text)          # she (or Rohit) answers the question the graph is waiting on
        else:
            inp = {"messages": [{"role": "user", "content": text}], "out": "", "goto": ""}
        self.graph.invoke(inp, self.config)
        p = self.pending()
        return p[0].value.get("say", "") if p else (self.state.get("out") or "")

    # ------------------------------------------------------------------ inspection
    @property
    def state(self) -> dict:
        return self.graph.get_state(self.config).values or {}

    def pending(self) -> list:
        st = self.graph.get_state(self.config)
        return [i for t in st.tasks for i in (t.interrupts or [])]

    def history(self) -> list[dict]:
        """Every checkpoint of this thread, oldest first: the node that just ran, the draft and the key facts."""
        out = []
        for snap in reversed(list(self.graph.get_state_history(self.config))):
            v = snap.values or {}
            path = v.get("path", [])
            f = v.get("facts", {})
            out.append({"node": path[-1] if path else "", "next": list(snap.next),
                        "draft": {k: x for k, x in (v.get("draft") or {}).items() if x not in (None, "")},
                        "facts": {k: f.get(k) for k in ("supplier_status", "supplier_cert", "food_contact", "cc_open",
                                                         "gross", "needs_approval", "missing", "pr_no", "po_no",
                                                         "status_code", "previewed_key", "confirmed_key") if k in f},
                        "awaiting": v.get("awaiting", ""), "stage": v.get("stage", "")})
        return out

    # ------------------------------------------------------------------ helpers
    def _tool(self, node: str, tool: str, /, **args) -> dict:
        try:
            out = self.tools.call(tool, args)
        except ServiceTimeout as e:
            out = {"ok": False, "error": f"TIMEOUT: {e}", "timeout": True}
        if out.get("bahi_code") == "TIMEOUT":
            out["timeout"] = True
        self.tool_log.append({"node": node, "tool": tool, "args": args, "ok": out.get("ok"),
                              "status": out.get("status")})
        return out

    def _svc(self, svc: str, **payload) -> dict:
        r = self.s.call(svc, **payload)
        return r["data"] if r["rc"] != "E" else {"_error": f"{r['err_cd']}: {r['msg']}"}

    def _decide(self, name, text, context, options=None):
        be = self.decide_backend or GeminiBackend(self.llm)
        d = decide(name, text, context, options, k=self.k, threshold=self.threshold, backend=be)
        return d, d.as_dict()

    def person(self, uid: str | None) -> str:
        """'RMEHTA' -> 'Rohit Mehta (RMEHTA)', read from Bahi once."""
        if not uid:
            return ""
        if uid not in self._people:
            u = self._svc("usr_get", user_id=uid)
            self._people[uid] = f"{u['name']} ({uid})" if u.get("name") else uid
        return self._people[uid]

    def _say(self, brief: dict, block: str = "", status: str = "", released: bool = False) -> str:
        sys = SAY.format(name=self.name, user=self.user, first=self.first)
        r = self.llm.chat([{"role": "system", "content": sys},
                           {"role": "user", "content": json.dumps(brief, ensure_ascii=False, default=str)}])
        words = (r.content or "").strip()
        if not released and CLAIMS_DONE.search(words):   # the model claimed more than Bahi says: use plain words
            words = brief.get("fallback") or "Here is where it stands."
        parts = (block, words, status) if brief.get("ask") else (words, block, status)  # a question always comes last
        return "\n\n".join(x for x in parts if x)

    def _reply(self, text: str, **extra) -> dict:
        return {"out": text, "messages": [{"role": "assistant", "content": text}], **extra}

    def _key(self, d: dict) -> str:
        """Idempotency key from the draft's content (never uuid4): the same order in this thread -> the same key."""
        ident = d.get("supplier_code") or f"new:{(d.get('supplier_name') or '').lower()}:{d.get('gstin') or ''}"
        raw = json.dumps([self.thread_id, self.user, ident, d.get("item_code"), d.get("qty"), d.get("rate"),
                          d.get("cost_centre"), d.get("need_by")])
        return "L4-" + hashlib.sha256(raw.encode()).hexdigest()[:12]

    @staticmethod
    def _sup(st) -> str | None:
        return (st.get("draft") or {}).get("supplier_code") or (st.get("facts") or {}).get("registered_code")

    def _draft_view(self, st) -> dict:
        d = st.get("draft") or {}
        return {k: v for k, v in d.items() if v not in (None, "")}

    def _status_line(self, rc: dict) -> str:
        if not rc:
            return ""
        s = f"Bahi status · {rc.get('po_no')} · {rc.get('status')}"
        if rc.get("approved_by"):
            s += f" · approved by {rc['approved_by']}"
        if rc.get("warning"):
            s += f" · {rc['warning']}"
        return s

    # ================================================================== nodes
    def n_understand(self, st):
        msgs = st.get("messages") or []
        text = msgs[-1]["content"] if msgs else ""
        aw = st.get("awaiting") or ""
        upd = {"path": ["understand"], "goto": "", "decisions": []}
        draft, facts = dict(st.get("draft") or {}), dict(st.get("facts") or {})
        if aw not in ("confirm", "cert", "supplier", "fields", "intent"):
            aw = ""
        reset = st.get("stage") in ("done", "cancelled", "held") and not aw   # a new request: a new draft
        if reset:
            draft, facts = {}, {}
            upd["stage"] = ""
        dupd, fupd = {}, {"intent_unsure": False}

        if aw == "confirm":
            d, rec = self._decide("confirmation", text, {"preview": facts.get("preview_text", "")})
            upd["decisions"].append(rec)
            upd["intent"] = "order"
            if d.choice == "yes" and d.sure:
                fupd["confirmed_key"] = facts.get("previewed_key")
            elif d.choice == "no" and d.sure:
                upd["stage"] = "cancelled"
                fupd["hold_reason"] = "cancelled"
            elif d.choice == "change":
                dupd = self._extract({**st, "draft": draft}, text)
                fupd["confirmed_key"] = ""
            else:
                fupd["reconfirm"] = True
        elif aw in ("cert", "supplier", "fields", "intent") or not aw:
            intent = "order" if aw in ("cert", "supplier", "fields") else None
            if aw in ("", "intent"):
                d, rec = self._decide("intent", text, {"what_we_asked": st.get("asked", ""),
                                                       "draft_so_far": self._draft_view({"draft": draft})})
                upd["decisions"].append(rec)
                intent = d.choice if d.choice != "_invalid" else "other"
                if not d.sure:
                    fupd["intent_unsure"] = True
            upd["intent"] = intent
            if aw == "cert":
                d, rec = self._decide("document_kind", text, {
                    "supplier": facts.get("supplier_label") or draft.get("supplier_name"),
                    "item": facts.get("item_label"), "certificate_on_file": facts.get("supplier_cert")})
                upd["decisions"].append(rec)
                vt = d.fields.get("valid_to", "")
                if d.choice == "food_grade_certificate" and d.sure and d.fields.get("doc_ref") and re.match(
                        r"\d{4}-\d{2}-\d{2}$", vt):
                    dupd.update(cert_ref=d.fields["doc_ref"], cert_valid_to=vt)
                    fupd["cert_refused"] = "" if vt >= TODAY else "expired"
                else:
                    fupd["cert_refused"] = d.choice if d.sure else "unsure"
            if aw == "supplier":
                cands = facts.get("candidates") or []
                opts = [c["label"] for c in cands] + ["none of these"]
                d, rec = self._decide("pick_supplier", text, {"she_first_said": draft.get("supplier_name"),
                                                              "item": facts.get("item_label")}, opts)
                upd["decisions"].append(rec)
                hit = next((c for c in cands if c["label"] == d.choice), None)
                if hit and d.sure:
                    dupd["supplier_code"] = hit["supplier_code"]
                    fupd.update(supplier_for="", supplier_note=f"you confirmed {hit['label']}")
                elif d.choice == "none of these" and d.sure:
                    fupd.update(supplier_status="new", supplier_for=_skey(draft), candidates=[],
                                supplier_cert="none", supplier_label=f"{draft.get('supplier_name')} (not in Bahi)")
            if intent == "order" and not fupd.get("intent_unsure"):
                ex = self._extract({**st, "draft": draft}, text)
                if aw == "supplier" and dupd.get("supplier_code"):
                    ex.pop("supplier_name", None)
                dupd = {**ex, **dupd}
        if dupd:
            changed = [k for k, v in dupd.items() if draft.get(k) != v]
            if changed:
                fupd["confirmed_key"] = ""
                if any(k in changed for k in ("supplier_name", "supplier_code", "supplier_city")):
                    fupd.update(supplier_for="", registered_code="")
                    if "supplier_code" not in dupd:
                        dupd["supplier_code"] = ""
                    if "supplier_name" in changed and aw == "cert":
                        fupd["cert_refused"] = ""
                if "cost_centre" in changed:
                    fupd["cc_for"] = ""
        upd["draft"] = {"__reset__": True, **dupd} if reset else dupd
        upd["facts"] = {"__reset__": True, **fupd} if reset else fupd
        upd["awaiting"] = ""
        if fupd.get("intent_unsure"):
            out = self._say({"situation": "Not sure whether she wants to place an order or is asking a question.",
                             "her_message": text, "ask": "Do you want me to place an order, or are you asking "
                             "about the rules?", "fallback": "Do you want me to place an order, or are you asking "
                             "about the rules?"})
            upd.update(self._reply(out, goto="ask", awaiting="intent", asked=out))
        elif fupd.get("reconfirm"):
            out = self._say({"situation": "Her answer to the preview was unclear.", "her_message": text,
                             "ask": "Shall I go ahead with the order exactly as shown?",
                             "fallback": "Shall I go ahead with the order exactly as shown?"},
                            block=facts.get("preview_text", ""))
            upd.update(self._reply(out, goto="ask", awaiting="confirm", asked=out))
        return upd

    def _extract(self, st, text: str) -> dict:
        props = {k: {"type": "string", "description": v} for k, v in EXTRACT.items()}
        props.update({k: {"type": "boolean", "description": v} for k, v in FLAGS.items()})
        rf = {"type": "json_schema", "json_schema": {"name": "order_fields", "strict": True, "schema": {
            "type": "object", "properties": props, "required": list(props)}}}
        sys = (f"You read one message from {self.name}, purchase executive at Rasoi Steel Works, Pune, and fill in "
               "every purchase-order detail the message states. Today is Monday 26 October 2026; dates are in 2026 "
               "unless she says otherwise. Use \"\" (or false) only for details the message does not state. Do not "
               "look anything up and do not guess codes she did not write.\n"
               "Example: 'Order 3,000 whistles from Sahyadri Valves for the Diwali run, PRD-07, need-by 4 Nov' -> "
               "supplier_name 'Sahyadri Valves', item_description 'whistles', quantity '3000', cost_centre 'PRD-07', "
               "need_by '2026-11-04', everything else empty.\n"
               "If the message only answers our last question (for example '20,000.' or 'PRD-07 then.'), put the "
               "answer in the field that question asked for.")
        user = json.dumps({"message": text, "our_last_question": st.get("asked", ""),
                           "draft_so_far": self._draft_view(st)}, ensure_ascii=False)
        r = self.llm.chat([{"role": "system", "content": sys}, {"role": "user", "content": user}], response_format=rf)
        try:
            s = r.content or "{}"
            e = json.loads(s[s.find("{"): s.rfind("}") + 1])
        except ValueError:
            e = {}
        d = {}
        num = lambda v: re.sub(r"[^\d.]", "", str(v or ""))  # noqa: E731
        if (e.get("supplier_name") or "").strip():
            d["supplier_name"] = e["supplier_name"].strip()
        code = (e.get("supplier_code") or "").strip().upper()
        if re.match(r"^[A-Z]{1,4}-[A-Z]{3}-\d{4}$", code):
            d["supplier_code"] = code
        for k_in, k_out in (("supplier_city", "supplier_city"), ("item_description", "item_text")):
            if (e.get(k_in) or "").strip():
                d[k_out] = e[k_in].strip()
        g = (e.get("gstin") or "").strip().upper()
        if re.match(r"^\d{2}[A-Z0-9]{13}$", g):
            d["gstin"] = g
        ic = (e.get("item_code") or "").strip().upper()
        if re.match(r"^[A-Z]{2,4}-[A-Z]{2,4}-\w+", ic):
            d["item_code"] = ic
        q = num(e.get("quantity"))
        if q:
            try:
                d["qty"] = int(float(q))
            except ValueError:
                pass
        rt = num(e.get("rate"))
        if rt:
            try:
                d["rate_said"] = round(float(rt), 2)
            except ValueError:
                pass
        cc = (e.get("cost_centre") or "").strip().upper().replace(" ", "")
        if re.match(r"^[A-Z]{3}-\d{2}$", cc):
            d["cost_centre"] = cc
        for k_in, k_out in (("need_by", "need_by"), ("certificate_valid_to", "cert_valid_to")):
            v = (e.get(k_in) or "").strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
                d[k_out] = v
        if (e.get("certificate_ref") or "").strip():
            d["cert_ref"] = e["certificate_ref"].strip()
        for f in FLAGS:
            if e.get(f) is True:
                d["flag_" + f] = True
        return d

    def n_route(self, st):
        draft, facts = dict(st.get("draft") or {}), dict(st.get("facts") or {})
        dupd, fupd, upd = {}, {}, {"path": ["route"], "goto": "", "decisions": []}
        # ---- the item
        ikey = json.dumps([draft.get("item_text"), draft.get("item_code")])
        if (draft.get("item_text") or draft.get("item_code")) and facts.get("item_for") != ikey:
            it = self._resolve_item(draft)
            fupd["item_for"] = ikey
            if it and it.get("options") and (draft.get("flag_repeat_last_order") or draft.get("flag_use_usual_supplier")):
                mine = [c for c in sorted((self.memory_user.fact(self.user, "last_order") or {}))
                        if any(f"({c})" in o for o in it["options"])]
                if len(mine) == 1:
                    i = self._svc("itm_get", itm_cd=mine[0])
                    it = {"item_code": mine[0], "descr": i["descr"], "food_contact": bool(i["food_contact"])}
            if it and it.get("item_code"):
                dupd["item_code"] = it["item_code"]
                fupd.update(item_label=f"{it['descr']} ({it['item_code']})", food_contact=it["food_contact"],
                            item_unclear="")
                draft["item_code"] = it["item_code"]
            else:
                fupd.update(item_unclear=(it or {}).get("options") or "no match", food_contact=None)
                dupd["item_code"] = ""
        # ---- the user level of memory: usual supplier, last order
        item = draft.get("item_code")
        notes = list(facts.get("memory_notes") or [])
        if item and not (draft.get("supplier_name") or draft.get("supplier_code")) and (
                draft.get("flag_use_usual_supplier") or draft.get("flag_repeat_last_order")):
            p = self.memory_user.fact(self.user, "preferred_supplier", item)
            if p:
                dupd["supplier_code"] = draft["supplier_code"] = p["value"]
                notes.append(f"supplier {p['value']} is your usual one ({p['source']})")
        if item and draft.get("flag_repeat_last_order") and not draft.get("qty"):
            last = self.memory_user.fact(self.user, "last_order", item)
            if last:
                dupd["qty"] = draft["qty"] = last["value"]["qty"]
                notes.append(f"quantity {last['value']['qty']:,} as on your last order {last['value']['po_no']}")
        if notes != list(facts.get("memory_notes") or []):
            fupd["memory_notes"] = notes
        # ---- the supplier
        if (draft.get("supplier_name") or draft.get("supplier_code")) and facts.get("supplier_for") != _skey(draft):
            res, recs = self._resolve_supplier(draft, facts.get("item_label") or draft.get("item_text"))
            upd["decisions"] += recs
            fupd.update(res["facts"])
            dupd.update(res.get("draft", {}))
            fupd["supplier_for"] = _skey({**draft, **dupd})
            if res["facts"].get("supplier_status") == "ask":
                cands = res["facts"]["candidates"]
                out = self._say({"situation": f"'{draft.get('supplier_name')}' is close to more than one supplier "
                                 "in Bahi, or I am not sure which one she means.",
                                 "candidates": [c["label"] for c in cands],
                                 "ask": "Which of these did you mean, or is it a new supplier?",
                                 "fallback": "Which of these suppliers did you mean, or is it a new one?"},
                                block="\n".join(f"· {c['label']} · food-grade certificate: {c['cert']}" for c in cands))
                upd.update(self._reply(out, goto="ask", awaiting="supplier", asked=out))
        upd["draft"], upd["facts"] = dupd, fupd
        return upd

    def _resolve_item(self, d: dict) -> dict | None:
        if d.get("item_code"):
            r = self._svc("itm_get", itm_cd=d["item_code"])
            if not r.get("_error") and r.get("active"):
                return {"item_code": r["itm_cd"], "descr": r["descr"], "food_contact": bool(r["food_contact"])}
        want = _tok(d.get("item_text") or "")
        if not want:
            return None
        found = {}
        for t in dict.fromkeys(w for w in want if len(w) >= 3 and not w[0].isdigit()):
            for row in (self._svc("itm_search", q=t).get("rows") or []):
                if row["active"]:
                    found[row["itm_cd"]] = row
        nums = {w for w in want if w[0].isdigit()}
        scored = []
        for code in sorted(found):
            have = _tok(found[code]["descr"])
            hn = {w for w in have if w[0].isdigit()}
            s = len(set(want) & set(have)) - (2 if nums and hn and not (nums & hn) else 0)
            scored.append((-s, len(set(have) - set(want)), code))
        scored.sort()
        if not scored or -scored[0][0] <= 0:
            return None
        if len(scored) > 1 and scored[0][:2] == scored[1][:2]:
            return {"options": [found[c]["descr"] + f" ({c})" for _, _, c in scored[:4]]}
        code = scored[0][2]
        i = self._svc("itm_get", itm_cd=code)
        return {"item_code": code, "descr": i["descr"], "food_contact": bool(i["food_contact"])}

    def _resolve_supplier(self, d: dict, item_label) -> tuple[dict, list]:
        recs = []
        name, code = d.get("supplier_name") or "", d.get("supplier_code") or ""

        def found(m, note=""):
            return {"draft": {"supplier_code": m["supplier_code"]},
                    "facts": {"supplier_status": "found", "supplier_cert": m["food_grade_certificate"],
                              "supplier_label": f"{m['name']} ({m['supplier_code']}, {m['city']})",
                              "supplier_state": m["state"], "supplier_note": note, "candidates": []}}

        if code:
            sup = self._svc("sup_get", sup_cd=code)
            if not sup.get("_error"):
                res = self._tool("route", "find_supplier", name=sup["name"].split(" (")[0], city=sup["city"])
                ms = res.get("matches") or []
                me = next((m for m in ms if m["supplier_code"] == code), None)
                if sup["status"] == "ACTIVE" and me:
                    return found(me), recs
                if sup["status"] != "ACTIVE":   # a blocked old code: the active supplier with the same GSTIN
                    for m in ms:
                        if m["status"] == "ACTIVE" and m["supplier_code"] != code:
                            twin = self._svc("sup_get", sup_cd=m["supplier_code"])
                            if twin.get("gstin") and twin.get("gstin") == sup.get("gstin"):
                                return found(m, f"{code} is a blocked old code; {m['supplier_code']} is the active "
                                                f"code for the same GSTIN"), recs
                    return {"facts": {"supplier_status": "blocked", "supplier_label": f"{sup['name']} ({code})",
                                      "candidates": [], "hold_reason": "guard",
                                      "guard": f"{code} is blocked in Bahi and no active supplier has its GSTIN"},
                            "draft": {"supplier_code": ""}}, recs
            name = name or code
        res = self._tool("route", "find_supplier", name=name, **({"city": d["supplier_city"]} if d.get("supplier_city") else {}))
        ms = [m for m in (res.get("matches") or []) if m["status"] == "ACTIVE"]
        exact = [m for m in ms if m["name"].lower() == name.lower() or m["match"] >= 0.92]
        if exact:
            m = exact[0]
            same = m["name"].lower() == name.lower()
            return found(m, "" if same else f"'{name}' is {m['name']} ({m['supplier_code']}, {m['city']}) in Bahi"), recs
        cands = [m for m in ms if m["match"] >= 0.45]
        if not cands:
            return {"facts": {"supplier_status": "new", "supplier_cert": "none", "candidates": [],
                              "supplier_label": f"{name} (not in Bahi)"}}, recs
        lab = lambda m: f"{m['name']} ({m['supplier_code']}, {m['city']})"  # noqa: E731
        opts = [lab(m) for m in cands] + ["none of these"]
        dd, rec = self._decide("pick_supplier", f"She wrote: '{name}'" + (f", {d['supplier_city']}" if d.get("supplier_city") else ""),
                               {"item": item_label, "candidates": [{"label": lab(m), "status": m["status"],
                                                                    "food_grade_certificate": m["food_grade_certificate"]}
                                                                   for m in cands]}, opts)
        recs.append(rec)
        hit = next((m for m in cands if lab(m) == dd.choice), None)
        if hit and dd.sure:
            return found(hit, f"I took '{name}' to be {lab(hit)} (confidence {dd.confidence:.2f})"), recs
        if dd.choice == "none of these" and dd.sure:
            return {"facts": {"supplier_status": "new", "supplier_cert": "none", "candidates": [],
                              "supplier_label": f"{name} (not in Bahi)"}}, recs
        return {"facts": {"supplier_status": "ask", "candidates": [
            {"label": lab(m), "supplier_code": m["supplier_code"], "cert": m["food_grade_certificate"]} for m in cands]}}, recs

    def n_onboard(self, st):
        d = st.get("draft") or {}
        gst = d.get("gstin") or ""
        state = GST_STATE.get(gst[:2], "") if gst else ""
        missing = [x for x, v in (("the supplier's GSTIN", gst), ("the supplier's city", d.get("supplier_city"))) if not v]
        new = {"name": d.get("supplier_name"), "city": d.get("supplier_city") or "", "state": state, "gstin": gst}
        upd = {"path": ["onboard"], "goto": "", "facts": {"new_supplier": new, "supplier_state": state}}
        if missing:
            out = self._say({"situation": f"{d.get('supplier_name')} is not in Bahi's supplier master, so it must be "
                             "registered before any order (Purchase Policy §6.3).", "missing": missing,
                             "ask": "Please give me " + " and ".join(missing) + ".",
                             "fallback": "They are not in Bahi yet. Please give me " + " and ".join(missing) + "."})
            upd.update(self._reply(out, goto="ask", awaiting="fields", asked=out))
        return upd

    def n_collect(self, st):
        d, f = dict(st.get("draft") or {}), dict(st.get("facts") or {})
        dupd, fupd = {}, {}
        notes = list(f.get("memory_notes") or [])
        sup = self._sup(st)
        # rate: the contract rate wins (Purchase Policy §7.1); a new supplier's quoted rate is hers
        rkey = json.dumps([sup, d.get("item_code"), d.get("rate_said")])
        if d.get("item_code") and f.get("rate_for") != rkey:
            fupd["rate_for"] = rkey
            cur = None
            if sup:
                cur = (self._svc("sup_rate_get", sup_cd=sup, itm_cd=d["item_code"]).get("current") or {}).get("rate")
            said = d.get("rate_said")
            if cur:
                dupd["rate"] = cur
                fupd["rate_note"] = (f"contract rate, not the {inr(said)} you mentioned (Purchase Policy §7.1)"
                                     if said and abs(said - cur) > 0.005 else "contract rate")
            else:
                dupd["rate"] = said or None
                fupd["rate_note"] = f"quoted rate {inr(said)} (no rate contract)" if said else ""
            d.update(dupd)
        # cost centre: her usual one from the user level of memory, as a suggestion the gate still checks
        if not d.get("cost_centre") and not f.get("cc_memory_used"):
            u = self.memory_user.fact(self.user, "usual_cost_centre")
            if u:
                dupd["cost_centre"] = d["cost_centre"] = u["value"]
                fupd["cc_memory_used"] = True
                notes.append(f"cost centre {u['value']} is your usual one ({u['source']})")
                fupd["memory_notes"] = notes
        cc = d.get("cost_centre")
        if cc and f.get("cc_for") != cc:
            r = self._tool("collect", "check_cost_centre", code=cc)
            fupd["cc_for"] = cc
            if r.get("ok"):
                fupd.update(cc_open=r["open"], cc_closed_on=r.get("closed_on"), cc_name=r.get("name"))
            else:
                fupd.update(cc_open=None, cc_unknown=cc)
                dupd["cost_centre"] = d["cost_centre"] = ""
        # what is still missing
        f2 = {**f, **fupd}
        need = {"item_code": "which item (Bahi could not match it)" if f2.get("item_unclear") else "the item",
                "supplier": "the supplier", "qty": "the quantity", "cost_centre": "the cost centre",
                "need_by": "the need-by date"}
        have = {"item_code": d.get("item_code"), "supplier": sup or (f2.get("supplier_status") == "new"),
                "qty": d.get("qty"), "cost_centre": d.get("cost_centre"), "need_by": d.get("need_by")}
        missing = [need[k] for k in R.REQUIRED if not have[k]]
        if have["supplier"] and d.get("item_code") and not d.get("rate"):
            missing.append("the rate (there is no rate contract with this supplier)")
        bad_date = bool(d.get("need_by")) and d["need_by"] < TODAY
        fupd.update(missing=missing, bad_date=bad_date)
        upd = {"path": ["collect"], "goto": "", "draft": dupd, "facts": fupd}
        blocked_first = R.GATE_BY_NAME["food_contact_no_cert"].pred({"draft": d, "facts": f2})
        centre_closed = R.GATE_BY_NAME["centre_closed"].pred({"draft": d, "facts": f2})
        if (missing or bad_date) and not blocked_first and not centre_closed:
            ask = []
            if missing:
                ask.append("Please tell me " + ", ".join(missing) + ".")
            if bad_date:
                ask.append(f"The need-by date {nice_date(d['need_by'])} is in the past; what date do you need them by?")
            extra = {"item_options": f2.get("item_unclear")} if isinstance(f2.get("item_unclear"), list) else {}
            if f2.get("cc_unknown"):
                extra["unknown_cost_centre"] = f"Bahi has no cost centre {f2['cc_unknown']}"
            out = self._say({"situation": "Drafting her order; these details cannot be looked up.", "draft": self._draft_view({"draft": d}),
                             **extra, "ask": " ".join(ask), "fallback": " ".join(ask)})
            upd.update(self._reply(out, goto="ask", awaiting="fields", asked=out))
        return upd

    def n_fix_cost_centre(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        cc = d.get("cost_centre")
        r = self._tool("fix_cost_centre", "check_cost_centre")
        opn = r.get("open") or []
        block = (f"Cost centre {cc} · closed on {nice_date(f.get('cc_closed_on'))} · Bahi would save the order as a "
                 f"Draft\nOpen: " + ", ".join(f"{c['code']} {c['name']}" for c in opn))
        out = self._say({"situation": f"The cost centre {cc} on the draft is closed (since {f.get('cc_closed_on')}); "
                         "Bahi would save the order silently as a Draft and never send it.",
                         "where_it_came_from": next((n for n in f.get("memory_notes", []) if cc in n), "she gave it"),
                         "ask": "Which open cost centre should I charge?",
                         "fallback": f"{cc} is closed, so Bahi would keep this as a Draft. Which open cost centre should I charge?"},
                        block=block)
        return {"path": ["fix_cost_centre"], "draft": {"cost_centre": ""},
                "facts": {"closed_cc": cc, "cc_for": "", "cc_open": None},
                **self._reply(out, goto="ask", awaiting="fields", asked=out)}

    def n_check(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        checks = []
        if f.get("food_contact"):
            on_draft = bool(d.get("cert_ref")) and (d.get("cert_valid_to") or "") >= TODAY
            checks.append(f"food contact: certificate in Bahi {f.get('supplier_cert')}"
                          + (f", on the draft {d.get('cert_ref')} to {d.get('cert_valid_to')}" if on_draft else ""))
        else:
            checks.append("not a food-contact item")
        return {"path": ["check"], "goto": "", "facts": {"checks": checks}}

    def n_ask_certificate(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        hits = self.memory_company.search(CERT_QUERY, 1)
        rule = hits[0] if hits else {}
        status = {"none": "no food-grade certificate", "expired": "an expired food-grade certificate"}.get(
            f.get("supplier_cert") or "none", "no valid food-grade certificate")
        if f.get("supplier_status") == "new":
            status = "no certificate (not in Bahi yet)"
        out = self._say({"situation": f"{f.get('item_label')} touches food. {f.get('supplier_label')} has {status} "
                         "in Bahi. Without a valid certificate we cannot order from them.",
                         "rule": rule.get("text"), "rule_cite": rule.get("cite"),
                         "ask": "Do you have their food-grade certificate? Send its reference number and expiry date.",
                         "fallback": "This part touches food, and this supplier has no valid food-grade certificate in "
                                     "Bahi. Do you have their certificate? Send its reference number and expiry date."},
                        block=f"{rule.get('cite', 'Purchase Policy §6.2')}: {rule.get('text', '')}".strip())
        return {"path": ["ask_certificate"], **self._reply(out, goto="ask", awaiting="cert", asked=out)}

    def n_preview(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        key = self._key(d)
        sup = self._sup(st)
        if sup:
            r = self._tool("preview", "create_purchase_order", supplier_code=sup, item_code=d["item_code"],
                           quantity=d["qty"], cost_centre=d["cost_centre"], need_by=d["need_by"], rate=d.get("rate"),
                           idempotency_key=key, confirm=False)
            if not r.get("ok"):
                out = self._say({"situation": "Bahi refused to price the order.", "error": r.get("error"),
                                 "next_step": r.get("next_step"), "fallback": f"Bahi refused: {r.get('error')}"})
                return {"path": ["preview"], **self._reply(out, goto="hold", facts={"hold_reason": "error"})}
            if r.get("already_done"):
                return {"path": ["preview"], "goto": "confirm", "facts": {"po_no": r["po_no"], "receipt": r}}
            p = r["preview"]
        else:  # a new supplier: price it with Bahi's own tax engine; nothing is saved
            ns = f.get("new_supplier") or {}
            tax_cd = "GST18-INTRA" if ns.get("state") == "MH" else "GST18-INTER"
            basic = round(d["qty"] * d["rate"], 2)
            t = self._svc("tax_compute", basic=basic, tax_cd=tax_cd)
            lim = self.me["appr_limit"]
            p = {"supplier": f"{ns.get('name')} (new: {ns.get('city')}, {ns.get('state')}, GSTIN {ns.get('gstin')})",
                 "item": f.get("item_label"), "quantity": d["qty"], "rate": d["rate"], "basic_value": basic,
                 "tax_code": tax_cd, "gross_value": t["gross"], "cost_centre": d["cost_centre"],
                 "cost_centre_open": True, "need_by": d["need_by"], "needs_request_first": t["gross"] > 50000,
                 "needs_approval": t["gross"] > lim, "your_limit": lim,
                 "approver": self.me["manager_id"] if t["gross"] > lim else None, "food_contact_item": f.get("food_contact")}
        lines = [f"Supplier     {p['supplier']}", f"Item         {p['item']}",
                 f"Quantity     {p['quantity']:,} at {inr(p['rate'])}" + (f" ({f['rate_note']})" if f.get("rate_note") else ""),
                 f"Value        {inr(p['basic_value'])} + {p['tax_code']} = {inr(p['gross_value'])} gross",
                 f"Cost centre  {p['cost_centre']} · need by {nice_date(p['need_by'])}",
                 f"Route        {'purchase request, then order' if p['gross_value'] > 50000 else 'direct order'}",
                 "Approval     " + (f"above your limit of {inr(p['your_limit'])}: goes to {self.person(p['approver'])}"
                                     if p["needs_approval"] else f"within your limit of {inr(p['your_limit'])}")]
        if f.get("supplier_status") == "new":
            lines.append("New supplier will be registered in Bahi when you confirm")
        if d.get("cert_ref") and f.get("supplier_cert") != "valid":
            lines.append(f"Certificate  {d['cert_ref']}, valid to {nice_date(d['cert_valid_to'])}, recorded before the order")
        block = "\n".join(lines)
        notes = [n for n in [f.get("supplier_note")] + list(f.get("memory_notes") or []) if n
                 and not (n.startswith("cost centre") and d.get("cost_centre") not in n)]
        out = self._say({"situation": "Preview of her order, priced by Bahi; nothing saved yet.",
                         "notes_to_mention": notes, "needs_approval": p["needs_approval"],
                         "approver": self.person(p.get("approver")), "ask": "Shall I go ahead?",
                         "fallback": "Here is the order, priced by Bahi. Nothing is saved yet. Shall I go ahead?"},
                        block=block)
        return {"path": ["preview"], "facts": {"previewed_key": key, "preview": p, "preview_text": block,
                                               "gross": p["gross_value"], "needs_approval": p["needs_approval"],
                                               "approver": p.get("approver"), "reconfirm": False},
                **self._reply(out, goto="ask", awaiting="confirm", asked=out)}

    # ---- the invariants, in code
    def _guard(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        key = self._key(d)
        if not (f.get("previewed_key") == key and f.get("confirmed_key") == key):
            raise GuardError("this exact draft was not previewed and confirmed")
        return key

    def _cert_guard(self, sup: str, st):
        f = st.get("facts") or {}
        if not f.get("food_contact"):
            return
        rows = self._svc("sup_cert_get", sup_cd=sup).get("rows") or []
        if not any(r["cert_type"] == "FOOD-GRADE" and r["valid_to"] >= self.erp.today for r in rows):
            raise GuardError(f"{sup} has no valid food-grade certificate in Bahi (Purchase Policy §6.2)")

    def _ensure_supplier(self, st, node: str) -> tuple[str, dict]:
        """Register a confirmed new supplier and record a certificate she gave, once. Returns (code, facts update)."""
        d, f = st.get("draft") or {}, st.get("facts") or {}
        fupd = {}
        sup = self._sup(st)
        if not sup:
            ns = f.get("new_supplier") or {}
            again = self._tool(node, "find_supplier", name=ns.get("name") or d.get("supplier_name"))
            twin = [m for m in again.get("matches") or [] if m["status"] == "ACTIVE" and m["match"] >= 0.92]
            if twin:
                raise GuardError(f"{twin[0]['name']} ({twin[0]['supplier_code']}) already exists")
            r = self._tool(node, "register_supplier", name=ns["name"], city=ns["city"], state=ns["state"],
                           gstin=ns["gstin"], confirm=True)
            if not r.get("ok"):
                raise GuardError(f"Bahi refused to register the supplier: {r.get('error')}")
            sup = fupd["registered_code"] = r["supplier_code"]
        if d.get("cert_ref") and f.get("supplier_cert") != "valid" and not f.get("cert_recorded"):
            r = self._tool(node, "record_certificate", supplier_code=sup, document_ref=d["cert_ref"],
                           valid_to=d["cert_valid_to"])
            if not r.get("ok"):
                raise GuardError(f"Bahi refused the certificate: {r.get('error')}")
            fupd.update(cert_recorded=True, supplier_cert="valid")
        return sup, fupd

    def _create(self, node: str, st, sup: str, key: str) -> dict:
        d = st.get("draft") or {}
        r = self._tool(node, "create_purchase_order", supplier_code=sup, item_code=d["item_code"], quantity=d["qty"],
                       cost_centre=d["cost_centre"], need_by=d["need_by"], rate=d.get("rate"),
                       idempotency_key=key, confirm=True)
        if r.get("timeout"):   # the reply was lost: read back by key before anything else
            r = self._tool(node, "order_status", idempotency_key=key)
            if not r.get("found"):
                r = {"ok": False, "error": "Bahi timed out and the order was not saved."}
        return r

    def n_approval(self, st):
        f = st.get("facts") or {}
        try:
            key = self._guard(st)
            sup, fupd = self._ensure_supplier(st, "approval")
            self._cert_guard(sup, {**st, "facts": {**f, **fupd}})
        except GuardError as e:
            return {"path": ["approval"], "goto": "hold", "facts": {"hold_reason": "guard", "guard": str(e)}}
        r = self._create("approval", st, sup, key)
        if r.get("status") == "WAITING FOR APPROVAL":
            fupd.update(pr_no=r["request_no"], approver=r.get("approver"), status_code="PA")
            who = self.person(r.get("approver"))
            out = self._say({"situation": f"The order is above her limit, so a purchase request was raised and "
                             f"submitted to {who} for approval. The purchase order will be created after "
                             "the approval.", "request": r["request_no"], "gross": inr(r.get("gross_value")),
                             "fallback": f"Request {r['request_no']} is with {who} for approval."},
                            status=f"Bahi status · {r['request_no']} · WAITING FOR APPROVAL by {who}")
            return {"path": ["approval"], "facts": fupd, "stage": "waiting_approval",
                    **self._reply(out, goto="wait", awaiting="approval")}
        if r.get("ok") and r.get("po_no"):
            fupd.update(po_no=r["po_no"], receipt=r, status_code=r.get("status_code"))
            return {"path": ["approval"], "goto": "confirm", "facts": fupd}
        return {"path": ["approval"], "goto": "hold", "facts": {**fupd, "hold_reason": "error", "guard": r.get("error")}}

    def n_wait_approval(self, st):
        f = st.get("facts") or {}
        msg = interrupt({"kind": "approval", "say": st.get("out", ""), "doc": f.get("po_no") or f.get("pr_no"),
                         "approver": f.get("approver")})
        upd = {"path": ["wait_approval"], "messages": [{"role": "user", "content": msg}]}
        # never trust the message: read the approval back from Bahi
        if f.get("po_no"):
            rc = self._tool("wait_approval", "order_status", po_no=f["po_no"])
            code = rc.get("status_code")
            if code in ("AP", "RL"):
                return {**upd, "goto": "confirm", "facts": {"receipt": rc, "status_code": code}}
            if code == "RJ":
                return {**upd, "goto": "hold", "facts": {"hold_reason": "rejected", "status_code": code}}
            doc = f["po_no"]
        else:
            pr = self._svc("pr_get", pr_no=f.get("pr_no"))
            code = pr.get("status")
            if code == "AP":
                return {**upd, "goto": "commit", "facts": {"pr_status": code}, "stage": ""}
            if code == "RJ":
                return {**upd, "goto": "hold", "facts": {"hold_reason": "rejected", "pr_status": code}}
            doc = f.get("pr_no")
        txt = (f"{doc} is still waiting for approval by {self.person(f.get('approver'))} in Bahi. I will carry on as soon "
               "as it is approved.")
        return {**upd, **self._reply(txt, goto="wait")}

    def n_commit(self, st):
        f = st.get("facts") or {}
        if f.get("po_no"):
            return {"path": ["commit"], "goto": "confirm"}
        try:
            key = self._guard(st)
            sup, fupd = self._ensure_supplier(st, "commit")
            self._cert_guard(sup, {**st, "facts": {**f, **fupd}})
        except GuardError as e:
            return {"path": ["commit"], "goto": "hold", "facts": {"hold_reason": "guard", "guard": str(e)}}
        r = self._create("commit", st, sup, key)
        if r.get("status") == "WAITING FOR APPROVAL":
            fupd.update(pr_no=r["request_no"], approver=r.get("approver"))
            who = self.person(r.get("approver"))
            out = self._say({"situation": f"Sent to {who} for approval.", "request": r["request_no"],
                             "fallback": f"Request {r['request_no']} is with {who} for approval."},
                            status=f"Bahi status · {r['request_no']} · WAITING FOR APPROVAL by {who}")
            return {"path": ["commit"], "facts": fupd, "stage": "waiting_approval", **self._reply(out, goto="wait")}
        if r.get("ok") and r.get("po_no"):
            fupd.update(po_no=r["po_no"], receipt=r, status_code=r.get("status_code"))
            return {"path": ["commit"], "goto": "confirm", "facts": fupd}
        return {"path": ["commit"], "goto": "hold", "facts": {**fupd, "hold_reason": "error", "guard": r.get("error")}}

    def n_confirm(self, st):
        f = st.get("facts") or {}
        po = f.get("po_no")
        rc = self._tool("confirm", "order_status", po_no=po)
        if rc.get("status_code") == "AP":
            rc = self._tool("confirm", "release_purchase_order", po_no=po)
        code = rc.get("status_code")
        if code == "PA":
            out = self._say({"situation": "The order is saved and waiting for approval.", "order": po,
                             "fallback": f"{po} is waiting for approval."}, status=self._status_line(rc))
            return {"path": ["confirm"], "facts": {"receipt": rc, "status_code": code, "approver": (rc.get("approval") or {}).get("approver")},
                    **self._reply(out, goto="wait")}
        if code != "RL":   # a Draft or anything else: report it plainly, never call it done
            out = self._say({"situation": f"Read back from Bahi: {po} is {rc.get('status')}, not released.",
                             "warning": rc.get("warning"), "fallback": f"{po} is {rc.get('status')}, not released."},
                            status=self._status_line(rc))
            return {"path": ["confirm"], "stage": "held", "facts": {"receipt": rc, "status_code": code},
                    **self._reply(out, goto="end", awaiting="")}
        out = self._say({"situation": "Order released to the supplier, read back from Bahi.", "order": po,
                         "status": "RELEASED", "supplier": f.get("supplier_label") or f.get("new_supplier", {}).get("name"),
                         "fallback": f"{po} is released to the supplier."},
                        status=self._status_line(rc), released=True)
        return {"path": ["confirm"], "stage": "done", "facts": {"receipt": rc, "status_code": code},
                **self._reply(out, goto="end", awaiting="")}

    def n_ask_kavita(self, st):
        ans = interrupt({"kind": st.get("awaiting") or "question", "say": st.get("out", "")})
        return {"path": ["ask_kavita"], "goto": "", "messages": [{"role": "user", "content": ans}]}

    def n_hold(self, st):
        d, f = st.get("draft") or {}, st.get("facts") or {}
        why = f.get("hold_reason") or ("cert" if f.get("cert_refused") else "")
        awaiting = ""
        if st.get("stage") == "cancelled" or why == "cancelled":
            brief = {"situation": "She does not want to go ahead. Nothing was saved in Bahi.",
                     "fallback": "All right, nothing has been saved."}
            stage = "cancelled"
        elif why == "rejected":
            brief = {"situation": f"{self.person(f.get('approver'))} rejected the request in Bahi; no order was created.",
                     "fallback": "The approver rejected it in Bahi, so no order was created."}
            stage = "held"
        elif why in ("guard", "error"):
            brief = {"situation": "Stopped before writing anything more.", "reason": f.get("guard"),
                     "fallback": f"I stopped: {f.get('guard')}."}
            stage = "held"
        else:
            kind = f.get("cert_refused")
            alt = None
            if d.get("item_code"):
                p = self.memory_user.fact(self.user, "preferred_supplier", d["item_code"])
                if p and p["value"] != self._sup(st):
                    alt = p["value"]
            brief = {"situation": f"No order: {f.get('supplier_label')} has no valid food-grade certificate and "
                     f"{'what she gave is a ' + kind.replace('_', ' ') + ', not a certificate' if kind in ('quotation', 'other_document') else 'she has none yet'}. "
                     "Purchase Policy §6.2 does not allow the order. Nothing was saved; the draft is kept and the order "
                     "can continue as soon as she sends the certificate's reference and expiry date.",
                     "usual_supplier_for_this_item": alt,
                     "fallback": "Without a valid food-grade certificate I can't order this from them (Purchase Policy "
                                 "§6.2). Nothing was saved; send me the certificate's reference and expiry when you have it."}
            stage, awaiting = "held", "cert"
        out = self._say(brief)
        return {"path": ["hold"], "stage": stage, **self._reply(out, goto="end", awaiting=awaiting, asked=out if awaiting else "")}

    def n_answer(self, st):
        msgs = st.get("messages") or []
        text = msgs[-1]["content"] if msgs else ""
        intent = st.get("intent") or "other"
        block, status = "", ""
        if intent == "policy_question":
            hits = self.memory_company.search(text, 3)
            brief = {"situation": "She asks what the rules allow. Answer yes or no first, then why, from these clauses only.",
                     "question": text, "clauses": [{"cite": h["cite"], "text": h["text"]} for h in hits],
                     "fallback": "Here is what the policy says."}
            block = "Source: " + "; ".join(h["cite"] for h in hits[:2]) if hits else ""
        elif intent == "order_status":
            m = re.search(r"(PO|PR)/\d{4}/\d{5}", text, re.I)
            if m and m.group(1).upper() == "PO":
                rc = self._tool("answer", "order_status", po_no=m.group(0).upper())
                brief = {"situation": "She asks about an order. Tell her its real status.",
                         "order": {k: rc.get(k) for k in ("po_no", "status", "supplier_code", "item_code", "quantity",
                                                          "gross_value", "approved_by", "warning", "error")},
                         "fallback": "Here is its status in Bahi."}
                status = self._status_line(rc) if rc.get("ok") else ""
            elif m:
                pr = self._svc("pr_get", pr_no=m.group(0).upper())
                brief = {"situation": "She asks about a purchase request.", "request": {k: pr.get(k) for k in (
                    "pr_no", "status", "cc_cd", "need_dt", "est_value")}, "fallback": "Here is the request in Bahi."}
            else:
                brief = {"situation": "She asks about an order but gave no number.", "ask": "Which PO number?",
                         "fallback": "Which PO number?"}
        elif intent == "stock_question":
            ex = self._extract({**st, "draft": {}}, text)
            it = self._resolve_item({"item_text": ex.get("item_text"), "item_code": ex.get("item_code")}) or {}
            if it.get("item_code"):
                sp = self._tool("answer", "stock_position", item_code=it["item_code"])
                brief = {"situation": "She asks about stock. Answer from these figures.", "item": it,
                         "stock": sp.get("warehouses"),
                         "fallback": "Here is the stock position."}
                block = "\n".join(f"{w['warehouse']}: {w['on_hand']:,} on hand, {w['on_order']:,} on order, "
                                  f"{w['days_of_cover']} days of cover" for w in sp.get("warehouses", []))
            else:
                brief = {"situation": "She asks about stock, but the item is unclear.", "ask": "Which item?",
                         "fallback": "Which item do you mean?"}
        else:
            brief = {"situation": "Not an order and not a question about the rules, an order or stock.",
                     "her_message": text, "what_you_can_do": "place purchase orders; answer purchase-policy "
                     "questions; give an order's status; give stock positions", "fallback": "I can place purchase "
                     "orders, answer policy questions, and look up orders and stock."}
        out = self._say(brief, block=block, status=status)
        return {"path": ["answer"], "stage": "done", **self._reply(out, goto="end", awaiting="")}

    # ================================================================== edges (gates come from route_spec)
    def e_understand(self, st) -> str:
        f = st.get("facts") or {}
        if st.get("stage") == "cancelled":
            return "hold"
        if st.get("goto") == "ask":
            return "ask_kavita"
        if (st.get("intent") or "order") != "order":
            return "answer"
        if f.get("confirmed_key") and f.get("confirmed_key") == f.get("previewed_key") and not f.get("po_no"):
            return "approval" if R.GATE_BY_NAME["over_limit"].pred(st) else "commit"
        return "route"

    def e_route(self, st) -> str:
        if st.get("goto") == "ask":
            return "ask_kavita"
        if (st.get("facts") or {}).get("supplier_status") == "blocked":
            return "hold"
        return "onboard" if R.GATE_BY_NAME["supplier_not_found"].pred(st) else "collect"

    def e_collect(self, st) -> str:
        if R.GATE_BY_NAME["food_contact_no_cert"].pred(st):
            return "check"          # a blocking rule outranks a missing field: ask for the certificate first
        if R.GATE_BY_NAME["centre_closed"].pred(st):
            return "fix_cost_centre"
        return "ask_kavita" if st.get("goto") == "ask" else "check"

    def e_check(self, st) -> str:
        f = st.get("facts") or {}
        if R.GATE_BY_NAME["food_contact_no_cert"].pred(st):
            return "hold" if f.get("cert_refused") else "ask_certificate"
        if f.get("missing") or f.get("bad_date"):
            return "collect_again"
        return "preview"

    @staticmethod
    def e_goto(st) -> str:
        return {"ask": "ask_kavita", "wait": "wait_approval", "confirm": "confirm", "commit": "commit",
                "hold": "hold", "end": END}.get(st.get("goto") or "end", END)


def build_graph(agent: GraphAgent, checkpointer=None):
    """The StateGraph: nodes are GraphAgent.n_*, conditional edges read route_spec's gate predicates."""
    g = StateGraph(RouteState)
    for name in ("understand", "route", "onboard", "collect", "fix_cost_centre", "check", "ask_certificate", "preview",
                 "approval", "wait_approval", "commit", "confirm", "ask_kavita", "answer", "hold"):
        g.add_node(name, getattr(agent, "n_" + name))
    g.add_edge(START, "understand")
    g.add_conditional_edges("understand", agent.e_understand, ["route", "answer", "ask_kavita", "approval", "commit", "hold"])
    g.add_conditional_edges("route", agent.e_route, ["ask_kavita", "onboard", "collect", "hold"])
    g.add_conditional_edges("onboard", lambda st: "ask_kavita" if st.get("goto") == "ask" else "collect",
                            ["ask_kavita", "collect"])
    g.add_conditional_edges("collect", agent.e_collect, ["ask_kavita", "fix_cost_centre", "check"])
    g.add_edge("fix_cost_centre", "ask_kavita")
    g.add_conditional_edges("check", agent.e_check, {"ask_certificate": "ask_certificate", "hold": "hold",
                                                     "preview": "preview", "collect_again": "collect"})
    g.add_edge("ask_certificate", "ask_kavita")
    g.add_conditional_edges("preview", agent.e_goto, ["ask_kavita", "hold", "confirm"])
    g.add_conditional_edges("approval", agent.e_goto, ["wait_approval", "confirm", "hold"])
    g.add_conditional_edges("wait_approval", agent.e_goto, ["wait_approval", "commit", "confirm", "hold"])
    g.add_conditional_edges("commit", agent.e_goto, ["wait_approval", "confirm", "hold"])
    g.add_conditional_edges("confirm", agent.e_goto, ["wait_approval", END])
    g.add_edge("ask_kavita", "understand")
    g.add_edge("answer", END)
    g.add_edge("hold", END)
    return g.compile(checkpointer=checkpointer or InMemorySaver())
