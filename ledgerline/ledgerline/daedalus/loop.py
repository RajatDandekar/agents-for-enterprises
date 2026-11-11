"""The agent loop and its harness, one step at a time (Lecture 5).

    from ledgerline.erp.engine import ERP
    from ledgerline.toolbox import Toolbox, ALL
    from ledgerline.daedalus.loop import Agent, SHIPPED
    agent = Agent(Toolbox(ERP(), "ECLARKE", names=ALL), config=SHIPPED)
    agent.say("Order 2,000 BAT-500 packs from Voltway for the spring launch run.")
    while not agent.done:
        print(agent.step())          # one turn of the loop: one model call, then the tools it asked for
    agent.reply                      # its words to Emma

The loop is four lines of logic:
    1. call the model with the conversation and the tool definitions;
    2. if it answered in words, the message is finished;
    3. otherwise run each tool it asked for and add each result to the conversation (the observation);
    4. go back to 1.

Everything else here is the HARNESS: the code around the loop that decides when to stop and what is allowed.
Its knobs (config) are the ones students turn in Daedalus:
    max_steps    at most this many model calls per message; the last one must be words (no tools)
    budget       at most this many input tokens per message (0 = no budget)
    tools        which tools the model is given
    prompt       "full" (Ask Northbridge's own prompt), "bare" (one line), or "custom" (custom_prompt)
    pause        True: a request waiting for an approver pauses the job; the next message first reads Ledgerline
    recovery     True: a call that was refused is not repeated (a lost reply may be retried), the same call a third time is refused, an
                 empty reply is sent back once, and three failures in a row stop the loop
State across days: state() is plain JSON; Agent.from_state(json, toolbox) carries on the next morning.
"""
from __future__ import annotations

import json
import re
import time

from ..llm import LLM

MODEL = "gemini:gemini-3.8-flash"
FALLBACK = "gemini:gemini-3.5-flash-lite"
WRITE_TOOLS = {"create_purchase_request", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
               "release_purchase_order", "receive_goods", "register_supplier"}
SHIPPED_TOOLS = ["find_item", "check_stock", "find_supplier", "supplier_certificates", "check_budget", "search_policy",
                 "create_purchase_request", "order_status", "create_purchase_order", "release_purchase_order",
                 "list_my_approvals"]
TWO_TOOLS = ["find_item", "check_stock"]
SHIPPED = {"max_steps": 12, "budget": 60000, "tools": SHIPPED_TOOLS, "prompt": "full", "custom_prompt": "",
           "pause": True, "recovery": True}

BARE = ("You are Ask Northbridge, an assistant for Northbridge Cycles with tools for its Ledgerline ERP. You act for "
        "{name} ({user}), {role}. Today is Monday 26 October 2026.")
WRAP_UP = ("[harness] This is the last step allowed for this message. Reply to {first} now, in plain words and without "
           "tools: what you found, what is saved (if anything), and what you need from {first} to finish.")
PEOPLE = {"ECLARKE": ("Emma Clarke", "purchase executive"), "DOKAFOR": ("Daniel Okafor", "purchase manager"),
          "ATANAKA": ("Aiko Tanaka", "stores")}


def full_prompt() -> str:
    """Ask Northbridge's own system prompt, as the live app sends it (ledgerline.experience.harness.AGENT)."""
    from ..experience.harness import AGENT
    return AGENT


def system_prompt(config: dict, user: str = "ECLARKE") -> str:
    name, role = PEOPLE.get(user, (user, "staff"))
    kind = config.get("prompt", "full")
    text = {"bare": BARE, "custom": config.get("custom_prompt") or BARE}.get(kind) or full_prompt()
    try:
        return text.format(name=name, role=role, user=user, first=name.split()[0])
    except (KeyError, IndexError, ValueError):
        return text  # a student's own prompt with stray braces is sent as written


def clean_config(c: dict | None) -> dict:
    from ..toolbox import ALL
    c = dict(c or {})
    out = dict(SHIPPED)
    out["max_steps"] = max(1, min(40, int(c.get("max_steps", SHIPPED["max_steps"]) or 1)))
    out["budget"] = max(0, min(400000, int(c.get("budget", SHIPPED["budget"]) or 0)))
    tools = c.get("tools", SHIPPED["tools"])
    out["tools"] = [t for t in ALL if t in set(tools or [])] or list(TWO_TOOLS[:1])
    out["prompt"] = c.get("prompt") if c.get("prompt") in ("full", "bare", "custom") else "full"
    out["custom_prompt"] = str(c.get("custom_prompt") or "")[:6000]
    out["pause"] = bool(c.get("pause", True))
    out["recovery"] = bool(c.get("recovery", True))
    return out


def diff(c: dict) -> list[str]:
    """The settings that differ from the shipped ones, in plain words (for 'Your runs' and the class wall)."""
    out = []
    if c["max_steps"] != SHIPPED["max_steps"]:
        out.append(f"max steps {c['max_steps']}")
    if c["budget"] != SHIPPED["budget"]:
        out.append(f"budget {c['budget']:,}" if c["budget"] else "no budget")
    if set(c["tools"]) != set(SHIPPED["tools"]):
        out.append(f"{len(c['tools'])} tools")
    if c["prompt"] != "full":
        out.append(f"{c['prompt']} prompt")
    if not c["pause"]:
        out.append("pause off")
    if not c["recovery"]:
        out.append("recovery off")
    return out


def _key(name: str, args: dict) -> str:
    return name + json.dumps(args or {}, sort_keys=True, default=str)


class Agent:
    """One conversation with Ask Northbridge, run one step at a time by the harness."""

    def __init__(self, tb, config: dict | None = None, llm_for=None, guard=None, user: str = "ECLARKE"):
        """tb: a ledgerline.toolbox.Toolbox (or anything with names, schemas(), call(), erp).
        llm_for(model) -> LLM: how to reach a model (cassettes in the notebook, live in the app)."""
        self.tb, self.cfg, self.user, self.guard = tb, clean_config(config), user, guard
        self.llm_for = llm_for or (lambda m: LLM(m, cassette="L5v4_loop", max_tokens=4096))
        self._llms: dict[str, LLM] = {}
        self.first = PEOPLE.get(user, (user,))[0].split()[0]
        self.messages: list[dict] = [{"role": "system", "content": system_prompt(self.cfg, user)}]
        self.waiting: dict | None = None      # {"doc": "PR/2026/04417", "approver": "DOKAFOR"} while paused
        self.docs = {"requests": [], "orders": []}
        self.failed: dict[str, str] = {}      # calls that failed, with their error (recovery)
        self.turns: list[dict] = []           # one entry per message from the person: its steps and reply
        self.done, self.reply = True, ""
        self.model_used = None

    # ------------------------------------------------------------------------------------------- the person speaks
    def say(self, text: str) -> dict:
        """Start a new message. With the pause on and a job waiting, the harness reads Ledgerline first."""
        turn = {"text": text, "steps": [], "reply": "", "end": None, "model_calls": 0, "tool_calls": 0,
                "tokens_in": 0, "tokens_out": 0, "seconds": 0.0, "usd": 0.0, "t0": time.time()}
        self.turns.append(turn)
        self.done, self.reply = False, ""
        self._seen: dict[str, int] = {}
        self.failed = {}                      # recovery remembers failures within one message (the world may change by tomorrow)
        self._fails_in_row, self._empties = 0, 0
        content = text
        if self.cfg["pause"] and self.waiting:
            st = self.tb.call("order_status", {"request_no": self.waiting["doc"]})
            code = st.get("status_code")
            note = {"kind": "harness", "part": "pause", "tool": "order_status", "args": {"request_no": self.waiting["doc"]},
                    "result": st}
            if code == "AP":
                note["note"] = (f"Read Ledgerline before the model: {self.waiting['doc']} is APPROVED by "
                                f"{st.get('approved_by')}. The job resumes.")
                content = (text + f"\n\n[harness] Ledgerline shows {self.waiting['doc']} as APPROVED by "
                           f"{st.get('approved_by')}. Carry on with the job: create the purchase order from it and release it.")
                self.waiting = None
            elif code == "RJ":
                note["note"] = f"Read Ledgerline before the model: {self.waiting['doc']} was REJECTED."
                content = text + f"\n\n[harness] Ledgerline shows {self.waiting['doc']} as REJECTED. Tell {self.first}; order nothing."
                self.waiting = None
            else:  # still waiting: the harness answers itself; the model is not called at all
                note["note"] = (f"Read Ledgerline before the model: {self.waiting['doc']} is still "
                                f"{st.get('status') or 'waiting'}. No model call.")
                turn["steps"].append(note)
                self.messages.append({"role": "user", "content": text})
                reply = (f"{self.waiting['doc']} is still waiting for {PEOPLE.get(self.waiting['approver'], (self.waiting['approver'],))[0]} "
                         f"to approve it (I checked Ledgerline just now). I will carry on once it is approved.")
                self.messages.append({"role": "assistant", "content": reply})
                return self._finish(turn, reply, "still waiting")
            turn["steps"].append(note)
        self.messages.append({"role": "user", "content": content})
        return turn

    # ------------------------------------------------------------------------------------------- one turn of the loop
    def step(self) -> dict:
        """One model call, then the tools it asked for. Returns the step's record."""
        turn = self.turns[-1]
        if self.done:
            return {"kind": "harness", "note": "This message is finished.", "end": turn["end"]}
        n = turn["model_calls"] + 1
        cfg = self.cfg
        lines = [f"step {n} of {cfg['max_steps']}"]
        if cfg["budget"]:
            lines.append(f"{turn['tokens_in']:,} of {cfg['budget']:,} input tokens used")
            if turn["tokens_in"] >= cfg["budget"]:
                text = (f"I stopped: this message has used {turn['tokens_in']:,} input tokens, over its budget of "
                        f"{cfg['budget']:,}. Tell me how you want to go on.")
                rec = {"kind": "harness", "part": "budget", "note": "Over the token budget: stopped before the model call."}
                turn["steps"].append(rec)
                self.messages.append({"role": "assistant", "content": text})
                self._finish(turn, text, "budget")
                return rec
        last = n >= cfg["max_steps"]
        extra = [{"role": "user", "content": WRAP_UP.format(first=self.first)}] if last and n > 1 else None
        r, model = self._chat(tools=None if (last and n > 1) else self._schemas(), extra=extra,
                              words_only=last and n > 1)
        if last and n == 1:  # max_steps = 1: the only call may use tools, but nothing will read their results
            pass
        rec = {"kind": "model", "n": n, "text": r.content or "", "calls": [], "tokens_in": r.tokens_in,
               "tokens_out": r.tokens_out, "seconds": r.seconds, "model": model, "harness": lines,
               "context_messages": len(self.messages) + (1 if extra else 0)}
        turn["steps"].append(rec)
        turn["model_calls"] += 1
        turn["tokens_in"] += r.tokens_in
        turn["tokens_out"] += r.tokens_out
        turn["seconds"] = round(turn["seconds"] + r.seconds, 2)
        turn["usd"] = round(turn["usd"] + self._usd(r, model), 6)
        if extra:
            rec["harness"].append("last step: words only")
        if not r.tool_calls:
            reply = r.content or ""
            if cfg["recovery"] and not reply.strip() and self._empties < 1 and not last:
                self._empties += 1
                rec["harness"].append("empty reply: sent back once (recovery)")
                self.messages.append({"role": "user", "content": f"[harness] Your reply was empty. Continue the job with "
                                                                 f"the tools, or reply to {self.first} in words."})
                return rec
            self.messages.append({"role": "assistant", "content": reply})
            if not reply.strip():
                reply = "I have stopped here. Tell me what to do next."
            rec["end"] = "max_steps" if (last and n > 1) else "answered"
            self._finish(turn, reply, rec["end"])
            return rec
        self.messages.append(r.message())
        for tc in r.tool_calls:
            c = self._call(tc.name, tc.arguments or {})
            rec["calls"].append(c)
            turn["tool_calls"] += 1
            self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(c["result"], default=str)})
        if cfg["recovery"] and self._fails_in_row >= 3:
            text = "Three steps failed in a row, so I stopped rather than guess. Tell me how to go on."
            rec["harness"].append("three failures in a row: stopped (recovery)")
            self.messages.append({"role": "assistant", "content": text})
            rec["end"] = "failures"
            self._finish(turn, text, "failures")
            return rec
        if cfg["pause"] and self.waiting and not self._paused_note:
            self._paused_note = True
            rec["harness"].append(f"paused: {self.waiting['doc']} waits for {self.waiting['approver']}; writes are held")
        if last:  # max_steps = 1 and it asked for tools: nothing more may run
            text = f"I reached the step limit ({cfg['max_steps']}) before I could reply. Ask me again to go on."
            self.messages.append({"role": "assistant", "content": text})
            rec["end"] = "max_steps"
            self._finish(turn, text, "max_steps")
        return rec

    def respond(self, text: str) -> dict:
        """The whole message: say(), then steps until it is finished."""
        turn = self.say(text)
        while not self.done:
            self.step()
        return turn

    # ------------------------------------------------------------------------------------------- one tool call
    def _call(self, name: str, args: dict) -> dict:
        t0 = time.perf_counter()
        key = _key(name, args)
        c = {"name": name, "args": args, "blocked": None}
        if name not in self.cfg["tools"]:
            out = {"ok": False, "error": f"There is no tool called {name}.", "next_step": "Use one of the tools you have."}
        elif self.cfg["recovery"] and key in self.failed:
            out = {"ok": False, "error": f"This exact call already failed: {self.failed[key]}",
                   "next_step": "Do not repeat it. Follow the earlier next_step, change the arguments, or ask the user."}
            c["blocked"] = "recovery"
        elif self.cfg["recovery"] and self._seen.get(key, 0) >= 2:
            out = {"ok": False, "error": f"You already called {name} twice with these exact arguments.",
                   "next_step": "Use the result you already have, or ask the user."}
            c["blocked"] = "loop guard"
        elif self.cfg["pause"] and self.waiting and name in WRITE_TOOLS:
            out = {"ok": False, "error": f"The job is paused: {self.waiting['doc']} is waiting for {self.waiting['approver']}.",
                   "next_step": f"Tell {self.first} it is waiting for approval. Nothing more can be done until then."}
            c["blocked"] = "pause"
        else:
            out = self.tb.call(name, args)
            # A refusal is remembered, so it is never repeated. A lost reply (TIMEOUT) is not: the tools look themselves
            # up before they save, so the same call again finds what the first one saved (found and fixed, 11 Nov:
            # the first version blocked that retry and left Emma's request half done; logs/recover_before.json).
            if not out.get("ok") and out.get("ledgerline_code") != "TIMEOUT":
                self.failed[key] = str(out.get("error", ""))[:300]
        self._seen[key] = self._seen.get(key, 0) + 1
        self._fails_in_row = 0 if out.get("ok") else self._fails_in_row + 1
        c.update(ok=bool(out.get("ok")), result=out, ms=round((time.perf_counter() - t0) * 1000, 1))
        self._note_docs(out)
        return c

    def _note_docs(self, out: dict):
        pr, po = out.get("request_no"), out.get("po_no")
        if po and po not in self.docs["orders"] and out.get("status_code"):
            self.docs["orders"].append(po)
        elif pr and pr not in self.docs["requests"] and out.get("status_code"):
            self.docs["requests"].append(pr)
        if self.cfg["pause"] and pr and not po and out.get("status_code") == "PA" and not self.waiting:
            self.waiting = {"doc": pr, "approver": out.get("approver") or "the approver"}
            self._paused_note = False

    # ------------------------------------------------------------------------------------------- the model
    def _schemas(self):
        return [s for s in self.tb.schemas() if s["function"]["name"] in self.cfg["tools"]]

    def _llm(self, model):
        if model not in self._llms:
            self._llms[model] = self.llm_for(model)
        return self._llms[model]

    def _chat(self, tools, extra=None, words_only=False):
        msgs = self.messages + (extra or [])
        kw = {"reasoning_effort": "low"}
        if self.guard is not None and not self.guard.budget_ok():
            raise RuntimeError("budget: today's model budget is used up")
        last = None
        for model in (MODEL, FALLBACK):
            try:
                r = self._llm(model).chat(msgs, tools=tools, **kw)
            except Exception as e:  # noqa: BLE001
                last = e
                if "ReplayMiss" in type(e).__name__:
                    raise
                continue
            self.model_used = model
            if self.guard is not None:
                r.inr = round(self._usd(r, model) * 88.0, 6)
                self.guard.add(r)
            if words_only and r.tool_calls:  # the model ignored "no tools": keep its words, drop the calls
                r.tool_calls = []
                r.content = r.content or ""
            return r, model
        raise last or RuntimeError("no model answered")

    @staticmethod
    def _usd(r, model) -> float:
        from ..llm import PRICES
        p = PRICES.get(model.split(":", 1)[-1], (0.5, 3.0))
        return (r.tokens_in * p[0] + r.tokens_out * p[1]) / 1e6

    # ------------------------------------------------------------------------------------------- endings and state
    _paused_note = False

    def _finish(self, turn, reply, end):
        turn["reply"], turn["end"] = reply, end
        if self.cfg["pause"] and self.waiting and end == "answered":
            turn["end"] = "paused"
        turn["waiting"] = dict(self.waiting) if self.waiting else None
        turn["docs"] = json.loads(json.dumps(self.docs))
        self.done, self.reply = True, reply
        return turn

    def state(self) -> dict:
        """Everything needed to carry on tomorrow, as plain JSON: the conversation, what waits, what was made."""
        return {"user": self.user, "config": self.cfg, "messages": self.messages, "waiting": self.waiting,
                "docs": self.docs, "failed": self.failed}

    @classmethod
    def from_state(cls, st: dict, tb, llm_for=None, guard=None) -> "Agent":
        a = cls(tb, st.get("config"), llm_for=llm_for, guard=guard, user=st.get("user", "ECLARKE"))
        a.messages, a.waiting = st["messages"], st.get("waiting")
        a.docs, a.failed = st.get("docs") or {"requests": [], "orders": []}, st.get("failed") or {}
        return a


ASKS = re.compile(r"\?|\b(confirm|shall I|should I|would you like|do you want|go ahead|let me know)\b", re.I)
