"""Ask Rasoi: the orchestrator behind the After page.

    orchestrator LLM  <->  MCP  <->  toolbox (tool.json + tool.py)  <->  Bahi ERP 7.2 (the player's own Rasoi)

The tools are not imported by the harness: they are discovered over MCP from
bahi.toolbox.mcp.build_toolbox_server(players.erp(pid), user), through MCPClient / MCPClientTools, so the
architecture on the slide is the architecture in the code.

Stages (?stage=..., one per lecture):
    brain       no tools at all: the bare model. It will make up Rasoi's numbers (Lecture 2 shows this on purpose).
    knowledge   one tool, search_policy: it can quote the purchase policy, but cannot see Bahi (Lecture 3).
    hands       the whole toolbox, one tool round per message: it can act, one step at a time (Lecture 4).
    agent       the whole toolbox and the loop: multi-step until the job is done or it needs you (Lecture 5).
"""
from __future__ import annotations

import json
import os
import threading
import time

from ..llm import LLM

MODEL = os.environ.get("RASOI_MODEL", "gemini:gemini-3.8-flash")
# Tried in order when a model fails. A model that fails for good (no credits, bad key) is skipped for 15 minutes.
CHAIN = list(dict.fromkeys([MODEL] + [m.strip() for m in os.environ.get(
    "RASOI_FALLBACKS", "openrouter:google/gemini-3.8-flash,gemini:gemini-3.5-flash-lite,openrouter:google/gemini-3.5-flash-lite"
).split(",") if m.strip()]))
DEAD: dict[str, float] = {}
# USD per million tokens for routes bahi.llm.PRICES does not price right (OpenRouter list prices, 28 Oct 2026).
PRICE = {"openrouter:google/gemini-3.8-flash": (0.825, 4.125), "openrouter:google/gemini-3.5-flash-lite": (0.30, 2.50)}


def cost_of(r) -> float:
    """Estimated rupees for one reply (fixed 88 per USD, as bahi.llm)."""
    p = PRICE.get(r.model)
    if not p:
        return r.cost_inr
    return round((r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6 * 88.0, 4)
STAGES = ("brain", "knowledge", "hands", "agent")
MAX_ROUNDS = {"brain": 0, "knowledge": 6, "hands": 1, "agent": 14}
MAX_TOKENS = int(os.environ.get("RASOI_MAX_TOKENS", "4096"))  # Gemini 3 spends part of this on thinking
REASONING = os.environ.get("RASOI_REASONING", "")              # e.g. "low": less thinking, faster replies
WRAP_UP = ("(No more tool calls for this message. Reply to the user now, in plain words, with what you found and "
           "what you would do next.)")
PEOPLE = {"KJOSHI": ("Kavita Joshi", "purchase executive"), "RMEHTA": ("Rohit Mehta", "purchase manager"),
          "NDESAI": ("Neha Desai", "stores")}

BRAIN = """You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of pressure cookers.
You are talking to {name}, {role}. Today is Monday 26 October 2026. Help with purchasing: stock, orders,
approvals and receipts. Keep replies short and plain. No emoji."""

KNOWLEDGE = """You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of pressure cookers.
You are talking to {name}, {role}. Today is Monday 26 October 2026.
You can search Rasoi's purchase policy and the Bahi manual with search_policy. For any question about a rule, call it
first and quote the clause with its citation, for example (POL-PUR-001 §6.2). Never state a rule from memory.
If the first search does not answer it, search again for the rule behind the question (which suppliers may be used,
certificates, limits, approvals). Gaskets, lids and body blanks touch food.
Rasoi makes pressure cookers, so many of the parts it buys touch food. Before you answer, think which of Rasoi's rules
the question could depend on (the kind of part, the supplier, the amount, the price) and search for each of them
separately.
You cannot see or change Bahi ERP yet: no stock, orders, prices or approvals. If asked for one, say so plainly.
Keep replies short and plain. No emoji."""

AGENT = """You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of pressure cookers
(1,80,000 a month). You work inside Rasoi's Bahi ERP for {name} ({user}), {role}, with {first}'s own Bahi
permissions and nobody else's. Today is Monday 26 October 2026.

How you work
- Every fact (stock, rates, suppliers, budgets, approvals, statuses, rules) comes from a tool. Never guess a number.
  For a question about a rule, call search_policy and cite the clause. Gaskets, lids and body blanks touch food.
- Anything that saves a request, an order or a goods receipt: first call the tool with confirm=false and show the
  preview as a short list (item, quantity, supplier, value in rupees, cost centre, need-by date, who must approve).
  Ask {first} to confirm. Call it again with confirm=true only after a clear yes.
- Release and approve tools have no preview. An instruction like "release it" or "approve it", or a yes to a plan
  that says you will release it, is the go-ahead for that one document.
- When a step finishes, do the next step of the same job if {first} has already agreed to it; otherwise say what
  comes next and who does it.
- Report the status the receipt gives you, in plain words. Never say an order is placed, sent or ordered unless its
  status is RELEASED. A request waiting for approval is not an order: say who it waits for.
- If a tool returns ok=false, read next_step and follow it, or tell {first} plainly what to do.
- Approving is Rohit's job and receiving goods is Neha's: if {first} cannot do a step, say who can.
- Short, plain replies: two to six lines, no tables. Money with Indian commas, like ₹2,80,840. Dates like 9 Nov 2026.
  No emoji.

What you know about Rasoi (codes and numbers still come from the tools)
- The 5-litre silicone gasket is GSK-SIL-05L. Deccan Polymers, Rajkot, is DP-RJK-0042.
- The Diwali production run is cost centre PRD-07. If no need-by date is given for it, propose Monday
  9 November 2026 (2026-11-09) and show it in the preview.
- Kavita Joshi (KJOSHI) buys, Rohit Mehta (RMEHTA) approves above Kavita's limit, Neha Desai (NDESAI) receives
  goods at Pune stores."""


def _system(stage: str, user: str) -> str:
    name, role = PEOPLE.get(user, (user, ""))
    t = {"brain": BRAIN, "knowledge": KNOWLEDGE}.get(stage, AGENT)
    return t.format(name=name, role=role, user=user, first=name.split()[0])


def _parse(txt):
    try:
        return json.loads(txt)
    except Exception:  # noqa: BLE001
        return {"text": txt}


def food_grade_block(erp, tool: str, args: dict) -> dict | None:
    """The trust layer's guard before a write (Lecture 7): Purchase Policy §6.2, food-contact parts only from a
    supplier with a valid food-grade certificate. Lecture 5 measured a free loop ordering from Shakti Seals and Kaveri
    Rubber after quoting this rule, so the live app checks it in code before the order is committed or released."""
    if tool == "create_purchase_order" and args.get("confirm") in (True, "true", "True"):
        sup, item = args.get("supplier_code"), args.get("item_code")
        if not item and args.get("request_no"):
            with erp.lock:
                row = erp.q1("SELECT itm_cd FROM pr_line WHERE pr_no=?", args["request_no"])
            item = row and row["itm_cd"]
    elif tool == "release_purchase_order" and args.get("po_no"):
        with erp.lock:
            row = erp.q1("SELECT h.sup_cd, l.itm_cd FROM po_hdr h JOIN po_line l ON l.po_no=h.po_no WHERE h.po_no=?",
                         args["po_no"])
        sup, item = (row["sup_cd"], row["itm_cd"]) if row else (None, None)
    else:
        return None
    if not sup or not item:
        return None
    with erp.lock:
        food = erp.q1("SELECT food_contact FROM item WHERE itm_cd=?", item)
        cert = erp.q1("SELECT MAX(valid_to) AS v FROM sup_cert WHERE sup_cd=? AND cert_type='FOOD-GRADE'", sup)
        today = erp.today
    if not food or not food["food_contact"] or (cert and cert["v"] and cert["v"] >= today):
        return None
    state = "has an expired food-grade certificate" if cert and cert["v"] else "has no food-grade certificate"
    return json.dumps({"ok": False, "blocked_by": "food-grade guard (Purchase Policy §6.2)",
                       "error": f"{item} touches food and supplier {sup} {state}. Rasoi may not order it from them.",
                       "next_step": "Tell the user this order cannot go ahead under §6.2. Offer a certified supplier "
                                    "(find_supplier shows certificates), or the supplier's valid certificate first."})


class AskRasoi:
    """One conversation: one player, one person (Kavita, Rohit or Neha), one stage."""

    def __init__(self, erp, user: str = "KJOSHI", stage: str = "agent", guard=None, pid: str = ""):
        from ..mcp_server import MCPClient, MCPClientTools
        from ..toolbox.mcp import build_toolbox_server
        from .players import locked_toolbox

        self.user, self.stage, self.guard, self.pid = user, stage, guard, pid
        self.erp = erp
        self.llms: dict[str, LLM] = {}
        self.model_used = None
        self.busy = threading.Lock()
        self.client = self.tools = None
        if stage != "brain":
            names = ["search_policy"] if stage == "knowledge" else None
            with erp.lock:
                server = build_toolbox_server(erp, user, names=names, name="rasoi-toolbox")
            locked_toolbox(server.toolbox, erp.lock)  # every tool call runs under this Rasoi's lock
            self.client = MCPClient(server)
            self.tools = MCPClientTools(self.client)
        self.messages = [{"role": "system", "content": _system(stage, user)}]
        self.transcript: list[dict] = []  # what the page shows: user / assistant turns with their tool cards
        self.created = self.used = time.time()

    @property
    def schemas(self):
        return self.tools.schemas() if self.tools else None

    def close(self):
        if self.client:
            self.client.close()

    # ------------------------------------------------------------------ one model call, guarded, with fallbacks
    def _llm(self, model: str) -> LLM:
        if model not in self.llms:
            self.llms[model] = LLM(model, cassette="experience", mode="live", max_tokens=MAX_TOKENS)
        return self.llms[model]

    def _chat(self, tools, extra=None, **kw):
        """Try the models in CHAIN in order, skipping any that recently failed for good (no credits, bad key)."""
        if REASONING:
            kw.setdefault("reasoning_effort", REASONING)
        msgs = self.messages + (extra or [])
        if self.guard and not self.guard.budget_ok():
            from .guard import Refused
            raise Refused(429, "Today's model budget for the class is used up. The instructor can raise it.")
        last_err = None
        for model in CHAIN:
            if DEAD.get(model, 0) > time.time():
                continue
            try:
                r = self._llm(model).chat(msgs, tools=tools, **kw)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "tool_choice" in kw and ("tool_choice" in msg or "400" in msg):
                    kw.pop("tool_choice")  # a provider that rejects tool_choice=none: ask again with no tools
                    return self._chat(None, extra, **kw)
                hard = any(x in msg for x in ("402", "401", "403", "RESOURCE_EXHAUSTED", "credits", "API key"))
                DEAD[model] = time.time() + (900 if hard else 20)
                print(f"[ask-rasoi] {model} failed ({msg[:180]}); {'skipping it for 15 min' if hard else 'trying the next'}")
                last_err = e
                continue
            r.inr = cost_of(r)
            self.model_used = model
            if self.guard:
                self.guard.add(r)
            return r
        raise last_err or RuntimeError("No model is available.")

    # ------------------------------------------------------------------ one user message -> one reply
    def respond(self, text: str) -> dict:
        t0 = time.perf_counter()
        self.used = time.time()
        self.messages.append({"role": "user", "content": text})
        cards, cost, tin, tout, calls = [], 0.0, 0, 0, 0
        rounds, reply = 0, ""
        limit = MAX_ROUNDS.get(self.stage, 14)
        while True:
            last = self.tools is None or rounds >= limit
            if last and self.tools:  # out of tool rounds: the model must answer with what it has
                r = self._chat(self.schemas, extra=[{"role": "user", "content": WRAP_UP}], tool_choice="none")
                if not (r.content or "").strip():
                    calls, cost, tin, tout = calls + 1, cost + r.inr, tin + r.tokens_in, tout + r.tokens_out
                    r = self._chat(None, extra=[{"role": "user", "content": WRAP_UP}])
            else:
                r = self._chat(self.schemas if self.tools else None)
            calls += 1
            cost += r.inr
            tin += r.tokens_in
            tout += r.tokens_out
            if not r.tool_calls or last:
                reply = r.content or ""
                self.messages.append({"role": "assistant", "content": reply})
                break
            self.messages.append(r.message())
            rounds += 1
            for tc in r.tool_calls:
                t1 = time.perf_counter()
                try:
                    blocked = food_grade_block(self.erp, tc.name, tc.arguments or {})
                    out = blocked if blocked else self.tools.call(tc.name, tc.arguments)
                except Exception as e:  # noqa: BLE001  (a broken tool must not kill the conversation)
                    out = json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})
                content = out if isinstance(out, str) else json.dumps(out, default=str)
                cards.append({"round": rounds, "tool": tc.name, "args": tc.arguments, "result": _parse(content),
                              "ms": round((time.perf_counter() - t1) * 1000)})
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
        if not reply.strip():
            reply = "I have stopped here. Tell me what to do next." if cards else "Sorry, I had nothing to say. Try again?"
        self._trim()
        out = {"reply": reply, "cards": cards, "preview": _preview(cards), "stage": self.stage, "person": self.user,
               "rounds": rounds, "model": self.model_used, "model_calls": calls, "tokens_in": tin, "tokens_out": tout,
               "cost_inr": round(cost, 4), "seconds": round(time.perf_counter() - t0, 2)}
        self.transcript.append({"role": "user", "text": text, "t": time.time()})
        self.transcript.append({"role": "assistant", "t": time.time(), **out})
        return out

    def _trim(self, keep: int = 70):
        """Keep the context bounded: drop the oldest whole turns (never split a tool call from its result)."""
        if len(self.messages) <= keep:
            return
        users = [i for i, m in enumerate(self.messages) if m["role"] == "user"]
        for i in users:
            if len(self.messages) - i + 1 <= keep:
                self.messages = [self.messages[0]] + self.messages[i:]
                return


def _preview(cards: list[dict]):
    """The last write preview in this turn that was not committed afterwards: the page shows it with a Confirm."""
    committed = {c["tool"] for c in cards if c["args"].get("confirm") is True}
    for c in reversed(cards):
        res = c["result"] if isinstance(c["result"], dict) else {}
        if res.get("ok") and "preview" in res and c["tool"] not in committed:
            return {"tool": c["tool"], "preview": res["preview"], "warnings": res.get("warnings") or []}
    return None


class Agents:
    """Every live conversation, keyed by (player, person, stage). Bounded: the least recently used are closed."""

    def __init__(self, players, guard, cap: int = 450):
        self.players, self.guard, self.cap = players, guard, cap
        self.d: dict[tuple, AskRasoi] = {}
        self.lock = threading.Lock()

    def get(self, pid: str, user: str, stage: str) -> AskRasoi:
        k = (pid, user, stage)
        with self.lock:
            a = self.d.get(k)
        if a is None:
            a = AskRasoi(self.players.erp(pid), user, stage, self.guard, pid)
            with self.lock:
                if k in self.d:  # another request built it first
                    a.close()
                    a = self.d[k]
                else:
                    self.d[k] = a
                old = sorted(self.d.items(), key=lambda kv: kv[1].used)[:max(0, len(self.d) - self.cap)]
                for kk, aa in old:
                    self.d.pop(kk, None)
                    aa.close()
        return a

    def peek(self, pid: str, user: str, stage: str):
        return self.d.get((pid, user, stage))

    def drop(self, pid: str):
        with self.lock:
            for k in [k for k in self.d if k[0] == pid]:
                self.d.pop(k).close()

    def count(self) -> int:
        return len(self.d)
