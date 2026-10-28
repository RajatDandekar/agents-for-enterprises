"""Two companies' agents talking over A2A: Deccan Polymers' sales agent, and Ask Rasoi asking it.

Deccan Polymers (DP-RJK-0042, Rajkot, Gujarat) is a supplier with its own small stock system, separate from
Bahi. Its sales agent is an A2A server (a2a-sdk 1.2.3, A2A spec 1.0): an agent card at
/.well-known/agent-card.json, JSON-RPC at /a2a (SendMessage, SendStreamingMessage, GetTask ...). Inside, a
small LLM tool loop answers from Deccan's own books. Ask Rasoi reaches it through one tool,
ask_supplier_agent(supplier_code, message), an A2A client.

    from bahi.course.protocols.deccan import run_negotiation
    out = run_negotiation(ERP())            # three turns, replayable with no key (cassettes IND9_a2a_*)
    out["sequence"]                         # who said what, in order, with the payloads that crossed the wire

Determinism (so the notebook replays from cassettes): nothing random ever enters a prompt. Task ids, context
ids, message ids and timestamps stay on the wire; the tool result Ask Rasoi's model sees holds only the
supplier's words and data. Client-side message ids are a hash of the turn and the text.
All of it is fictional.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import json
import time
from typing import Any

from ...llm import LLM, tool_schema

# ------------------------------------------------------------------ Deccan's own books (not Bahi)
DECCAN = {
    "company": "Deccan Polymers", "supplier_code_at_rasoi": "DP-RJK-0042", "city": "Rajkot", "state": "Gujarat",
    "items": {"DPG-SIL-05L-FG": {"description": "Silicone gasket 5 L, food grade", "customer_codes": {"Rasoi Steel Works": "GSK-SIL-05L"},
                                 "finished_stock": 12000, "next_batch": {"quantity": 8000, "ready": "2026-11-03"},
                                 "line_capacity_per_day": 4000}},
    "contract_rates": {("Rasoi Steel Works", "DPG-SIL-05L-FG"): {"rate": 11.90, "valid_from": "2026-10-01"}},
    "gst_rate": 0.18, "gst_kind": "IGST (inter-state, Gujarat to Maharashtra)",
    "transit_days": {"Pune": 3}, "dispatch_rule": "same day if booked by noon, otherwise next working day",
    "food_grade_certificate": {"ref": "FG-DP-2025-118", "valid_to": "2027-03-31"},
}
ITEM_ALIASES = {"GSK-SIL-05L": "DPG-SIL-05L-FG", "DPG-SIL-05L-FG": "DPG-SIL-05L-FG"}


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


class DeccanBooks:
    """Deccan's stock, prices and dispatch, as deterministic Python. `today` is the sandbox date."""

    def __init__(self, today: str = "2026-10-26"):
        self.today = today
        self.orders: list[dict] = []

    def _item(self, item):
        code = ITEM_ALIASES.get((item or "").strip().upper())
        if not code:
            return None, {"ok": False, "error": f"Deccan does not make '{item}'.",
                          "next_step": "Ask the customer for the item (we make DPG-SIL-05L-FG, Rasoi code GSK-SIL-05L)."}
        return code, None

    def quote(self, item: str, quantity: int, customer: str = "Rasoi Steel Works") -> dict:
        code, err = self._item(item)
        if err:
            return err
        rate = DECCAN["contract_rates"].get((customer, code))
        if not rate:
            return {"ok": False, "error": f"No contract rate on file for {customer}.",
                    "next_step": "Offer to send a list-price quote by email; never share another customer's rate."}
        basic = round(quantity * rate["rate"], 2)
        gst = round(basic * DECCAN["gst_rate"], 2)
        it = DECCAN["items"][code]
        return {"ok": True, "item": code, "description": it["description"], "customer_item_code": it["customer_codes"].get(customer),
                "quantity": quantity, "rate": rate["rate"], "rate_basis": f"contract rate since {rate['valid_from']}",
                "basic_value": basic, "gst": gst, "gst_kind": DECCAN["gst_kind"], "gross_value": round(basic + gst, 2),
                "food_grade_certificate": DECCAN["food_grade_certificate"]}

    def delivery_plan(self, quantity: int, need_by: str, city: str = "Pune") -> dict:
        it = DECCAN["items"]["DPG-SIL-05L-FG"]
        transit = DECCAN["transit_days"].get(city, 3)
        first_dispatch = _d(self.today) + dt.timedelta(days=1)   # booked today after noon: next working day
        lots, left = [], quantity
        from_stock = min(left, it["finished_stock"])
        if from_stock:
            lots.append({"quantity": from_stock, "source": "finished stock, Rajkot", "dispatch": first_dispatch.isoformat(),
                         "arrive": (first_dispatch + dt.timedelta(days=transit)).isoformat()})
            left -= from_stock
        ready = _d(it["next_batch"]["ready"])
        batch_left = it["next_batch"]["quantity"]
        while left > 0:
            q = min(left, batch_left) if batch_left else min(left, it["line_capacity_per_day"])
            lots.append({"quantity": q, "source": "next production batch" if batch_left else "production",
                         "dispatch": ready.isoformat(), "arrive": (ready + dt.timedelta(days=transit)).isoformat()})
            left -= q
            batch_left = 0
            ready += dt.timedelta(days=1)
        last = max(_d(x["arrive"]) for x in lots)
        return {"ok": True, "quantity": quantity, "to": city, "transit_days": transit, "lots": lots,
                "all_arrive_by": last.isoformat(), "meets_need_by": last <= _d(need_by), "need_by": need_by,
                "earliest_full_delivery": last.isoformat(),
                "note": "Line capacity is 4,000 a day; the next batch of 8,000 is ready on 3 Nov. No express option."}

    def confirm_order(self, po_no: str = "", quantity: int = 0, rate: float = 0.0) -> dict:
        if not po_no:
            return {"ok": False, "needs_input": True, "error": "A purchase order number is needed before Deccan can book dispatch.",
                    "next_step": "Ask the customer for their PO number."}
        if abs(float(rate) - 11.90) > 0.001:
            return {"ok": False, "error": f"Rate {rate} does not match the contract rate 11.90.",
                    "next_step": "Ask the customer to correct the PO rate."}
        plan = self.delivery_plan(int(quantity), "2099-12-31")
        ack = {"ok": True, "acknowledged": po_no, "quantity": int(quantity), "rate": 11.90,
               "gross_value": round(int(quantity) * 11.90 * 1.18, 2), "dispatch_plan": plan["lots"],
               "deccan_order_ref": "DP-SO-" + hashlib.sha1(po_no.encode()).hexdigest()[:6].upper()}
        self.orders.append(ack)
        return ack


DECCAN_TOOLS = [
    tool_schema("quote", "Deccan's price for an item and quantity for a customer, with GST. Uses the customer's contract rate.",
                {"item": {"type": "string", "description": "Deccan item code or the customer's code, e.g. GSK-SIL-05L"},
                 "quantity": {"type": "integer"}, "customer": {"type": "string", "description": "customer company name"}},
                ["item", "quantity"]),
    tool_schema("delivery_plan", "When a quantity can reach a city: lots from finished stock and production, with dispatch and arrival dates.",
                {"quantity": {"type": "integer"}, "need_by": {"type": "string", "description": "YYYY-MM-DD"},
                 "city": {"type": "string"}}, ["quantity", "need_by"]),
    tool_schema("confirm_order", "Book a customer's purchase order: checks the rate and returns the dispatch plan.",
                {"po_no": {"type": "string"}, "quantity": {"type": "integer"}, "rate": {"type": "number"}}, ["po_no", "quantity", "rate"]),
]

DECCAN_SYSTEM = (
    "You are the sales agent of Deccan Polymers, Rajkot, a maker of food-grade silicone gaskets. Another company's "
    "agent is writing to you. Answer only from your tools: quote, delivery_plan, confirm_order. Be honest about "
    "dates; never promise what the plan does not show. Never reveal another customer's price. Reply in two to four "
    "short sentences with the numbers (rupees in Indian format, e.g. Rs 2,80,840).")


# ------------------------------------------------------------------ timeline (the deck's scrubber)
class Timeline:
    def __init__(self):
        self.t0 = time.perf_counter()
        self.events: list[dict] = []

    def add(self, frm, to, kind, summary, payload=None):
        self.events.append({"from": frm, "to": to, "kind": kind, "summary": summary,
                            "payload": payload, "t_ms": round((time.perf_counter() - self.t0) * 1000, 1)})


def _short(x, n=220):
    s = x if isinstance(x, str) else json.dumps(x, default=str, ensure_ascii=False)
    return s if len(s) <= n else s[: n - 1] + "…"


def _canon(x):
    """Protobuf Struct maps have no fixed key order and turn every number into a float. Make it canonical, so the
    same data always prints the same way in a prompt (sorted keys, whole numbers as ints)."""
    if isinstance(x, dict):
        return {k: _canon(x[k]) for k in sorted(x)}
    if isinstance(x, list):
        return [_canon(v) for v in x]
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def _pb(msg) -> dict:
    from google.protobuf.json_format import MessageToDict
    return MessageToDict(msg)


# ------------------------------------------------------------------ Deccan's A2A server
def agent_card(base_url: str):
    from a2a.types.a2a_pb2 import AgentCapabilities, AgentCard, AgentInterface, AgentProvider, AgentSkill

    return AgentCard(
        name="Deccan Polymers sales agent",
        description="Quotes, delivery dates and order confirmations for Deccan Polymers' food-grade silicone gaskets.",
        supported_interfaces=[AgentInterface(url=base_url + "/a2a", protocol_binding="JSONRPC", protocol_version="1.0")],
        provider=AgentProvider(organization="Deccan Polymers, Rajkot", url="https://deccan-polymers.example"),
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True, push_notifications=False),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=[
            AgentSkill(id="quote", name="Quote", description="Price for an item and quantity, at the customer's contract rate, with GST.",
                       tags=["price", "quote"], examples=["Quote 20,000 GSK-SIL-05L for Rasoi Steel Works"]),
            AgentSkill(id="delivery_date", name="Delivery date", description="When a quantity can reach the customer's plant.",
                       tags=["dispatch", "delivery"], examples=["Can 20,000 reach Pune by 9 Nov?"]),
            AgentSkill(id="confirm_order", name="Confirm order", description="Book a purchase order and return the dispatch plan.",
                       tags=["order"], examples=["Confirm PO/2026/01182 for 20,000 at Rs 11.90"]),
        ])


class DeccanExecutor:
    """The A2A executor: one LLM tool loop over Deccan's books per message, with truthful task states."""

    def __init__(self, books: DeccanBooks, timeline: Timeline, model="gemini:gemini-3.8-flash", mode=None):
        self.books, self.tl = books, timeline
        self.llm = LLM(model, cassette="IND9_a2a_deccan", mode=mode)
        self.memory: dict[str, list[dict]] = {}   # per A2A context: the conversation so far (text only)

    async def execute(self, context, event_queue):
        from a2a.helpers.proto_helpers import new_data_part, new_task, new_text_message, new_text_part
        from a2a.server.tasks.task_updater import TaskUpdater
        from a2a.types.a2a_pb2 import TaskState

        msg = context.message
        text = context.get_user_input()
        data = [_canon(_pb(p).get("data")) for p in msg.parts if p.HasField("data")]
        if data:
            text += "\nAttached data: " + json.dumps(data, ensure_ascii=False)
        if context.current_task is None:
            await event_queue.enqueue_event(new_task(context.task_id, context.context_id, TaskState.TASK_STATE_SUBMITTED, history=[msg]))
        up = TaskUpdater(event_queue, context.task_id, context.context_id)
        await up.start_work(new_text_message("Checking Deccan's stock, rates and dispatch plan.", context_id=context.context_id, task_id=context.task_id))
        hist = self.memory.setdefault(context.context_id, [])
        msgs = [{"role": "system", "content": DECCAN_SYSTEM + f" Today is {self.books.today}."}, *hist,
                {"role": "user", "content": text}]
        results, needs_input = [], False
        for _ in range(6):
            r = await asyncio.to_thread(self.llm.chat, msgs, DECCAN_TOOLS)
            msgs.append(r.message())
            if not r.tool_calls:
                break
            for tc in r.tool_calls:
                self.tl.add("Deccan agent", "Deccan stock", "tool", f"{tc.name} {_short(tc.arguments, 120)}", tc.arguments)
                fn = getattr(self.books, tc.name, None)
                try:
                    out = fn(**tc.arguments) if fn else {"ok": False, "error": f"no tool {tc.name}"}
                except TypeError as e:
                    out = {"ok": False, "error": f"bad arguments: {e}"}
                needs_input |= bool(out.get("needs_input"))
                results.append({"tool": tc.name, "result": out})
                self.tl.add("Deccan stock", "Deccan agent", "tool result", _short(out, 160), out)
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, ensure_ascii=False)})
                await up.update_status(TaskState.TASK_STATE_WORKING, new_text_message(f"Ran {tc.name}.", context_id=context.context_id, task_id=context.task_id))
        answer = r.content or ""
        hist += [{"role": "user", "content": text}, {"role": "assistant", "content": answer}]
        good = [x for x in results if x["result"].get("ok")]
        if good:
            name = {"quote": "quote", "delivery_plan": "delivery plan", "confirm_order": "order acknowledgement"}
            await up.add_artifact([new_text_part(answer), new_data_part({x["tool"]: x["result"] for x in good})],
                                  name=" and ".join(dict.fromkeys(name[x["tool"]] for x in good)))
        final = new_text_message(answer, context_id=context.context_id, task_id=context.task_id)
        if needs_input and not any(x["tool"] == "confirm_order" and x["result"].get("ok") for x in results):
            await up.requires_input(final)
        else:
            await up.complete(final)

    async def cancel(self, context, event_queue):
        from a2a.server.tasks.task_updater import TaskUpdater
        await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()


def build_deccan_app(base_url: str, books: DeccanBooks, timeline: Timeline, mode=None):
    """The Starlette app: the agent card and the JSON-RPC endpoint. Returns (app, executor, card)."""
    from a2a.server.agent_execution.agent_executor import AgentExecutor
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
    from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
    from starlette.applications import Starlette

    inner = DeccanExecutor(books, timeline, mode=mode)

    class _Exec(AgentExecutor):
        async def execute(self, context, event_queue):
            await inner.execute(context, event_queue)

        async def cancel(self, context, event_queue):
            await inner.cancel(context, event_queue)

    card = agent_card(base_url)
    handler = DefaultRequestHandler(agent_executor=_Exec(), task_store=InMemoryTaskStore(), agent_card=card)
    app = Starlette(routes=[*create_agent_card_routes(card), *create_jsonrpc_routes(handler, rpc_url="/a2a")])
    return app, inner, card


# ------------------------------------------------------------------ Ask Rasoi's side: the A2A client as a tool
STATE_NAMES = {"TASK_STATE_SUBMITTED": "submitted", "TASK_STATE_WORKING": "working", "TASK_STATE_COMPLETED": "completed",
               "TASK_STATE_INPUT_REQUIRED": "input-required", "TASK_STATE_FAILED": "failed", "TASK_STATE_REJECTED": "rejected",
               "TASK_STATE_CANCELED": "canceled", "TASK_STATE_AUTH_REQUIRED": "auth-required"}


class SupplierAgents:
    """Ask Rasoi's address book of supplier agents, and the A2A client that talks to them."""

    def __init__(self, registry: dict[str, str], timeline: Timeline):
        self.registry, self.tl = registry, timeline
        self.cards: dict[str, Any] = {}
        self.contexts: dict[str, str] = {}   # one A2A conversation per supplier (kept off the prompt)
        self.streaming = False
        self.turn = 0
        self.stats: list[dict] = []

    async def ask(self, supplier_code: str, message: str) -> dict:
        import httpx
        from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
        from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest

        base = self.registry.get(supplier_code)
        if not base:
            return {"ok": False, "error": f"No agent on file for supplier {supplier_code}.",
                    "next_step": f"Known supplier agents: {', '.join(self.registry)}."}
        async with httpx.AsyncClient(timeout=180) as hc:
            if supplier_code not in self.cards:
                self.tl.add("Ask Rasoi", "Deccan agent", "GET agent card", "GET /.well-known/agent-card.json")
                card = await A2ACardResolver(hc, base).get_agent_card()
                self.cards[supplier_code] = card
                cd = _pb(card)
                self.tl.add("Deccan agent", "Ask Rasoi", "agent card",
                            f"{cd['name']}: skills {', '.join(s['name'] for s in cd['skills'])}; streaming {cd['capabilities'].get('streaming', False)}", cd)
            client = ClientFactory(ClientConfig(streaming=self.streaming, httpx_client=hc)).create(self.cards[supplier_code])
            mid = "rasoi-" + hashlib.sha256(f"{self.turn}|{message}".encode()).hexdigest()[:16]
            msg = Message(message_id=mid, role=Role.ROLE_USER, parts=[Part(text=message)],
                          context_id=self.contexts.get(supplier_code, ""))
            req = SendMessageRequest(message=msg)
            method = "SendStreamingMessage" if self.streaming else "SendMessage"
            self.tl.add("Ask Rasoi", "Deccan agent", method, _short(message, 200), _pb(req))
            t0 = time.perf_counter()
            states, reply, data, n_events, last_task = [], "", [], 0, None
            async for resp in client.send_message(req):
                n_events += 1
                d = _pb(resp)
                kind = next(iter(d), "?")
                if kind == "task":
                    last_task = d["task"]
                    st = STATE_NAMES.get(last_task.get("status", {}).get("state"), "?")
                    states.append(st)
                    summ = f"task {st}"
                    if last_task.get("status", {}).get("message"):
                        summ += ": " + _short(" ".join(p.get("text", "") for p in last_task["status"]["message"].get("parts", [])), 160)
                elif kind == "statusUpdate":
                    st = STATE_NAMES.get(d["statusUpdate"]["status"].get("state"), "?")
                    states.append(st)
                    txt = " ".join(p.get("text", "") for p in d["statusUpdate"]["status"].get("message", {}).get("parts", []))
                    summ = f"status {st}" + (f": {_short(txt, 160)}" if txt else "")
                elif kind == "artifactUpdate":
                    art = d["artifactUpdate"]["artifact"]
                    summ = f"artifact '{art.get('name', '')}'"
                elif kind == "message":
                    summ = "message: " + _short(" ".join(p.get("text", "") for p in d["message"].get("parts", [])), 160)
                else:
                    summ = kind
                self.tl.add("Deccan agent", "Ask Rasoi", {"task": "task", "statusUpdate": "status-update",
                                                          "artifactUpdate": "artifact-update", "message": "message"}.get(kind, kind), summ, d)
                tid = (d.get(kind) or {}).get("contextId")
                if tid:
                    self.contexts[supplier_code] = tid
                if kind == "artifactUpdate":
                    for p in d["artifactUpdate"]["artifact"].get("parts", []):
                        if "data" in p:
                            data.append(p["data"])
                if kind in ("task", "statusUpdate"):
                    m = (d.get("task") or d.get("statusUpdate"))["status"].get("message", {})
                    t = " ".join(p.get("text", "") for p in m.get("parts", []))
                    if t and states[-1] in ("completed", "input-required", "failed", "rejected"):
                        reply = t
            if last_task and not data:
                for a in last_task.get("artifacts", []):
                    for p in a.get("parts", []):
                        if "data" in p:
                            data.append(p["data"])
            await client.close()
        self.stats.append({"turn": self.turn, "method": method, "events_received": n_events, "states": states,
                           "seconds": round(time.perf_counter() - t0, 3)})
        # Only the supplier's words and data go back to the model: no ids, no timestamps.
        return {"ok": True, "supplier": "Deccan Polymers", "state": states[-1] if states else "?", "reply": reply,
                "data": _canon(data)}


RASOI_SYSTEM = (
    "You are Ask Rasoi, the assistant of Rasoi Steel Works, Pune, working for Kavita Joshi (KJOSHI), purchase "
    "executive. Use the tools. To talk to a supplier, use ask_supplier_agent: it sends your message to that "
    "supplier's own agent. Deccan Polymers is supplier DP-RJK-0042. Write to suppliers in full sentences with item "
    "codes, quantities, dates and the delivery city (Pune). Do not raise purchase requests or orders unless Kavita "
    "asks. Answer Kavita in two to four short sentences with the numbers.")


def rasoi_tools():
    from ...toolbox import SPECS
    tools = [SPECS[n].schema() for n in ("check_stock", "create_purchase_request", "order_status")]
    tools.append(tool_schema("ask_supplier_agent", "Send a message to a supplier's own agent over A2A and get its reply (text and data).",
                             {"supplier_code": {"type": "string", "description": "Bahi supplier code, e.g. DP-RJK-0042"},
                              "message": {"type": "string", "description": "what to ask, in full sentences"}},
                             ["supplier_code", "message"]))
    return tools


class AskRasoi:
    def __init__(self, toolbox, suppliers: SupplierAgents, timeline: Timeline, model="gemini:gemini-3.8-flash", mode=None):
        self.tb, self.sup, self.tl = toolbox, suppliers, timeline
        self.llm = LLM(model, cassette="IND9_a2a_rasoi", mode=mode)
        self.messages = [{"role": "system", "content": RASOI_SYSTEM + f" Today is {toolbox.erp.today}."}]
        self.tools = rasoi_tools()

    async def turn(self, text: str, max_steps: int = 6) -> str:
        self.tl.add("Kavita", "Ask Rasoi", "chat", text)
        self.messages.append({"role": "user", "content": text})
        r = None
        for _ in range(max_steps):
            r = await asyncio.to_thread(self.llm.chat, self.messages, self.tools)
            self.messages.append(r.message())
            if not r.tool_calls:
                break
            for tc in r.tool_calls:
                if tc.name == "ask_supplier_agent":
                    out = await self.sup.ask(**tc.arguments)
                else:
                    self.tl.add("Ask Rasoi", "Bahi", "tool", f"{tc.name} {_short(tc.arguments, 120)}", tc.arguments)
                    out = self.tb.call(tc.name, tc.arguments)
                    self.tl.add("Bahi", "Ask Rasoi", "tool result", _short(out, 160), out)
                self.messages.append({"role": "tool", "tool_call_id": tc.id,
                                      "content": json.dumps(out, default=str, ensure_ascii=False, sort_keys=True)})
        answer = (r.content if r else "") or ""
        self.tl.add("Ask Rasoi", "Kavita", "chat", answer)
        return answer


TURNS = [
    "We need 20,000 GSK-SIL-05L gaskets in Pune by 9 Nov. Ask Deccan Polymers for a quote and a delivery date.",
    "Can all 20,000 arrive by 5 Nov?",
    "PO/2026/01182 is released. Send it to Deccan and get their confirmation.",
]


def _llm_delta(llm, start):
    rs = llm.log[start:]
    return {"calls": len(rs), "tokens_in": sum(r.tokens_in for r in rs), "tokens_out": sum(r.tokens_out for r in rs),
            "seconds": round(sum(r.seconds for r in rs), 2), "cost_inr": round(sum(r.cost_inr for r in rs), 4),
            "live_calls": sum(1 for r in rs if not r.replayed), "models": sorted({r.model for r in rs})}


async def _negotiate(erp, mode=None, port=None, recorder=None):
    from ...toolbox import Toolbox
    from .wire import Recorder, free_port, serve

    tl = Timeline()
    rec = recorder or Recorder()
    rec.t0 = tl.t0
    port = port or free_port()
    base = f"http://127.0.0.1:{port}"
    books = DeccanBooks(today=erp.today)
    app, deccan, card = build_deccan_app(base, books, tl, mode=mode)
    serve(rec.wrap(app, tag="deccan"), port=port)
    kavita = Toolbox(erp, "KJOSHI")
    sup = SupplierAgents({"DP-RJK-0042": base}, tl)
    rasoi = AskRasoi(kavita, sup, tl, mode=mode)
    turns, bahi = [], {}

    async def one(i, text, streaming):
        sup.turn, sup.streaming = i, streaming
        e0, w0, r0, d0, t0 = len(tl.events), len(rec.log), len(rasoi.llm.log), len(deccan.llm.log), time.perf_counter()
        answer = await rasoi.turn(text)
        wire = rec.log[w0:]
        turns.append({"turn": i + 1, "kavita": text, "ask_rasoi": answer, "streaming": streaming,
                      "wall_seconds": round(time.perf_counter() - t0, 2), "http_requests": len(wire),
                      "a2a_requests": [((e["req"] or {}).get("method") if isinstance(e["req"], dict) else e["method"] + " " + e["path"]) for e in wire],
                      "a2a_messages_to_deccan": sum(1 for e in wire if isinstance(e["req"], dict) and e["req"].get("method", "").startswith("Send")),
                      "a2a_events_from_deccan": sum(s["events_received"] for s in sup.stats if s["turn"] == i),
                      "task_states": [s["states"] for s in sup.stats if s["turn"] == i],
                      "a2a_seconds": [s["seconds"] for s in sup.stats if s["turn"] == i],
                      "llm_ask_rasoi": _llm_delta(rasoi.llm, r0), "llm_deccan": _llm_delta(deccan.llm, d0),
                      "events": [e0, len(tl.events)]})

    await one(0, TURNS[0], False)
    await one(1, TURNS[1], False)
    # The Rasoi side, for real in Bahi: Kavita raises the PR, Rohit approves, Kavita orders and releases.
    rohit = Toolbox(erp, "RMEHTA")
    steps = [("Kavita", kavita, "create_purchase_request", {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07",
                                                            "need_by": "2026-11-09", "confirm": True})]
    out = kavita.call(*steps[0][2:])
    tl.add("Kavita", "Bahi", "tool", "create_purchase_request 20,000 GSK-SIL-05L, PRD-07, need by 2026-11-09", steps[0][3])
    tl.add("Bahi", "Kavita", "tool result", _short(out, 160), out)
    bahi["pr"] = out
    a = rohit.call("approve_purchase_request", {"request_no": out["request_no"], "decision": "approve"})
    tl.add("Rohit", "Bahi", "tool", f"approve_purchase_request {out['request_no']}", {"request_no": out["request_no"], "decision": "approve"})
    tl.add("Bahi", "Rohit", "tool result", _short(a, 160), a)
    bahi["approve"] = a
    po = kavita.call("create_purchase_order", {"supplier_code": "DP-RJK-0042", "request_no": out["request_no"], "confirm": True})
    tl.add("Kavita", "Bahi", "tool", f"create_purchase_order DP-RJK-0042 from {out['request_no']}", None)
    tl.add("Bahi", "Kavita", "tool result", _short(po, 160), po)
    bahi["po"] = po
    rel = kavita.call("release_purchase_order", {"po_no": po.get("po_no")})
    tl.add("Kavita", "Bahi", "tool", f"release_purchase_order {po.get('po_no')}", None)
    tl.add("Bahi", "Kavita", "tool result", _short(rel, 160), rel)
    bahi["release"] = rel
    await one(2, TURNS[2], True)
    return {"turns": turns, "sequence": tl.events, "wire": rec.log, "agent_card": _pb(card), "bahi": bahi,
            "deccan_orders": books.orders, "totals": {"ask_rasoi": rasoi.llm.totals(), "deccan": deccan.llm.totals()},
            "live_calls": sum(1 for r in rasoi.llm.log + deccan.llm.log if not r.replayed)}


def run_negotiation(erp=None, mode: str | None = None, port: int | None = None) -> dict:
    """Three turns between Ask Rasoi and Deccan's agent over A2A, on `erp` (a fresh ERP() by default).

    mode: None uses BAHI_LLM_MODE (auto: replay what was recorded); "replay" needs no key at all.
    Works in a notebook too (runs the coroutine in its own thread when a loop is already running)."""
    from ...erp.engine import ERP
    erp = erp or ERP()
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_negotiate(erp, mode, port))
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(1) as ex:
        return ex.submit(lambda: asyncio.run(_negotiate(erp, mode, port))).result()


def plain_sequence(seq: list[dict]) -> list[tuple]:
    """The sequence without times, ids or payloads: what must be identical between a recording and its replay."""
    return [(e["from"], e["to"], e["kind"], e["summary"]) for e in seq]
