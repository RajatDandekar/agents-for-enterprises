"""The harness: everything around the model that turns "a model that can call tools" into an agent.

    from ledgerline.erp.engine import ERP
    from ledgerline.toolbox import Toolbox
    from ledgerline.llm import LLM
    from ledgerline.course.l5 import Harness
    h = Harness(Toolbox(ERP(), "ECLARKE"), LLM(cassette="L5v3_demo"))            # every part on
    bare = Harness(Toolbox(ERP(), "ECLARKE"), LLM(cassette="L5v3_demo"), parts=()) # only the loop
    h.respond("Reorder 20,000 of the city e-bike battery packs from Voltway Cells, PRD-07, need-by 9 November.")
    h.save("emma.json"); h2 = Harness.load("emma.json", tb, llm)            # state across days

The loop itself is always there (that is what makes it an agent): call the model with the history and the
tool schemas; if it asks for tools, run them and append each result as a tool message (the observation);
repeat until it answers in words. The PARTS are what a production harness adds around that loop:

    prompt    the full system prompt: who, today, the rules of the job (else a one-line prompt)
    stop      stop rules: at most 12 model steps per message (else 25), and stop after 3 failures in a row
    budget    at most 120,000 input tokens per message
    guard     loop guard: the same call with the same arguments a third time is not run again
    recovery  a call that already failed with these exact arguments is not repeated; the error is returned;
              an empty reply (it happens) is sent back, at most twice
    verify    before a reply goes out, code reads the order back from Ledgerline; a false "done" is sent back once
    pause     when a request waits for an approver, writes are held; the next message is checked against Ledgerline
              first, and the job resumes only when Ledgerline says APPROVED
State across days is save() / load(): the messages, what the job waits on, and the documents it made.
"""
from __future__ import annotations

import json
import re

from ...llm import LLM

PARTS = ("prompt", "stop", "budget", "guard", "recovery", "verify", "pause")

SYSTEM_BARE = ("You are Ask Northbridge, an assistant for Northbridge Cycles with access to Ledgerline ERP tools, acting for "
               "{name} ({user}). Today is Monday 26 October 2026.")

SYSTEM_FULL = """You are Ask Northbridge, the assistant on Northbridge Cycles' home page, working inside Ledgerline ERP for {name} ({user}), {role}.
Today is Monday 26 October 2026. {profile}

How you work:
- Use the tools to do the whole job, step by step, until it is finished or you need a person.
- Before the first write of a job, preview it (confirm=false), show {first} the numbers and ask once. After {first} says yes, commit (confirm=true) and carry on with the next steps without asking again.
- If a tool returns ok=false, read its error and next_step and follow next_step. Never repeat a call that failed with the same arguments.
- A purchase request above {first}'s approval limit waits for the manager. While it is WAITING FOR APPROVAL, say so and stop; order nothing until it is approved.
- An order reaches the supplier only when it is RELEASED. After creating an approved order, release it.
- Report the status the receipt gives you, in plain words. Never say an order is placed or sent unless its receipt says RELEASED.
- Lithium-cell parts may only be bought from a supplier with a valid UN 38.3 certificate (Purchase Policy §6.2). Answer policy questions from search_policy and cite the section."""

ROLES = {"ECLARKE": "purchase executive", "DOKAFOR": "purchase manager", "ATANAKA": "stores",
         "LMORENO": "senior buyer", "HWEBER": "plant head"}
DONE = re.compile(r"\b(placed|released|sent to (?:the )?supplier|on its way|has been ordered|order is confirmed|"
                  r"all done|is done|completed)\b", re.I)
HEDGE = re.compile(r"\bnot (?:yet )?(?:been )?(?:released|sent|placed)|draft|waiting|pending|once (?:daniel|it is|he)|"
                   r"after (?:daniel|approval)|cannot|can't|unable|not able|hold", re.I)
WRITE_TOOLS = {"create_purchase_request", "approve_purchase_request", "create_purchase_order", "approve_purchase_order",
               "release_purchase_order", "receive_goods", "register_supplier"}


def inr(x) -> str:
    """£ with Indian digit grouping: 280840 -> £280,840."""
    x = round(float(x))
    s = str(abs(int(x)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1])
        s = head + "," + tail
    return "£" + s


def profile(tb) -> str:
    """Who the user is, from Ledgerline: limit, manager, default cost centre. Part of the system prompt."""
    u = tb.erp.user(tb.user)
    mgr = tb.erp.user(u["manager_id"])["name"] + f" ({u['manager_id']})" if u.get("manager_id") else "nobody"
    lim = inr(u["appr_limit"]) if u.get("appr_limit") else "none"
    first = u["name"].split()[0]
    return (f"{first}'s approval limit is {lim} including VAT; {first}'s manager is {mgr}; {first}'s default cost "
            f"centre in Ledgerline is {u.get('default_cc') or 'not set'}.")


class Harness:
    def __init__(self, tb, llm: LLM | None = None, parts=PARTS, max_steps: int | None = None,
                 budget_tokens: int = 120_000, system: str | None = None, tools: list[str] | None = None):
        self.tb, self.llm = tb, llm or LLM(cassette="L5v3_harness")
        self.parts = set(parts)
        self.max_steps = max_steps or (12 if "stop" in self.parts else 25)
        self.budget_tokens = budget_tokens
        u = tb.erp.user(tb.user)
        self.first = u["name"].split()[0]
        sysmsg = (system or (SYSTEM_FULL if "prompt" in self.parts else SYSTEM_BARE)).format(
            name=u["name"], user=tb.user, role=ROLES.get(tb.user, "staff"), first=self.first, profile=profile(tb))
        self.tool_names = tools or tb.names
        self.messages: list[dict] = [{"role": "system", "content": sysmsg}]
        self.waiting: dict | None = None      # {"doc": "PR/2026/04417", "approver": "DOKAFOR"} while paused
        self.docs: dict = {"requests": [], "orders": []}
        self.trace: list[dict] = []           # one entry per model step, tool call and harness action
        self.turn = 0
        self.stops: list[str] = []            # why each message's loop ended

    # ------------------------------------------------------------------ the public face
    def schemas(self):
        return [s for s in self.tb.schemas() if s["function"]["name"] in self.tool_names]

    def respond(self, text: str) -> str:
        self.turn += 1
        content = text
        if "pause" in self.parts and self.waiting:
            content = text + "\n\n" + self._check_waiting()
        self.messages.append({"role": "user", "content": content})
        return self._loop()

    # ------------------------------------------------------------------ the loop
    def _loop(self) -> str:
        n0 = len(self.llm.log)
        fails_in_row, sent_back, empties = 0, 0, 0
        seen: dict[str, int] = {}
        for step in range(self.max_steps):
            used = sum(r.tokens_in for r in self.llm.log[n0:])
            if "budget" in self.parts and used > self.budget_tokens:
                return self._stop("budget", f"I stopped: this message used {used:,} tokens, over the "
                                            f"{self.budget_tokens:,} budget. Tell me how you want to continue.")
            r = self.llm.chat(self.messages, tools=self.schemas())
            self.messages.append(r.message())
            self.trace.append({"turn": self.turn, "step": step, "kind": "model", "thought": r.content,
                               "calls": [{"name": t.name, "args": t.arguments} for t in r.tool_calls],
                               "tokens_in": r.tokens_in, "tokens_out": r.tokens_out})
            if not r.tool_calls:                                   # stop rule 1: it answered in words
                reply = r.content or ""
                if "recovery" in self.parts and not reply.strip() and empties < 2:
                    empties += 1                                   # an empty reply is not an answer: ask again
                    self.trace.append({"turn": self.turn, "step": step, "kind": "harness", "part": "recovery",
                                       "note": "empty reply"})
                    self.messages.append({"role": "user", "content": f"[harness] Your last reply was empty. Continue "
                                          f"the job with the tools, or reply to {self.first} in words."})
                    continue
                if "verify" in self.parts and sent_back < 2:
                    problem = self._verify(reply)
                    if problem:
                        sent_back += 1
                        self.trace.append({"turn": self.turn, "step": step, "kind": "harness", "part": "verify",
                                           "note": problem})
                        self.messages.append({"role": "user", "content": "[harness check] " + problem})
                        continue
                self.stops.append("answered")
                return reply
            for tc in r.tool_calls:
                out = self._call(tc.name, tc.arguments, seen)
                fails_in_row = 0 if out.get("ok") else fails_in_row + 1
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)})
            if "stop" in self.parts and fails_in_row >= 3:
                return self._stop("failures", "Three steps failed in a row, so I stopped rather than guess. "
                                              "Here is where it stands; tell me how to go on.")
        if "stop" in self.parts:  # a graceful stop: one last call, words only, to say where it stands
            self.messages.append({"role": "user", "content": f"[harness] Step limit reached ({self.max_steps} steps). "
                                  f"Reply to {self.first} now, without tools: what you found, what is saved (if "
                                  f"anything), and the one thing you need from {self.first} to finish."})
            r = self.llm.chat(self.messages, tools=self.schemas(), tool_choice="none")
            self.messages.append({"role": "assistant", "content": r.content or ""})
            self.stops.append("max_steps")
            self.trace.append({"turn": self.turn, "kind": "harness", "part": "stop", "note": "max_steps"})
            return r.content or ""
        return self._stop("max_steps", f"(stopped after {self.max_steps} steps)")

    def _stop(self, why: str, text: str) -> str:
        self.stops.append(why)
        self.trace.append({"turn": self.turn, "kind": "harness", "part": "stop", "note": why})
        self.messages.append({"role": "assistant", "content": text})
        return text

    # ------------------------------------------------------------------ one tool call, through the parts
    def _call(self, name: str, args: dict, seen: dict) -> dict:
        key = name + json.dumps(args, sort_keys=True, default=str)
        entry = {"turn": self.turn, "kind": "tool", "name": name, "args": args}
        if "guard" in self.parts and seen.get(key, 0) >= 2:
            out = {"ok": False, "error": f"You already called {name} twice with these exact arguments.",
                   "next_step": "Use the result you already have, or ask the user."}
            entry["blocked"] = "guard"
        elif "recovery" in self.parts and key in self._failed:
            out = {"ok": False, "error": f"This exact call already failed: {self._failed[key]}",
                   "next_step": "Do not repeat it. Follow the earlier next_step, change the arguments, or ask the user."}
            entry["blocked"] = "recovery"
        elif "pause" in self.parts and self.waiting and name in WRITE_TOOLS:
            out = {"ok": False, "error": f"The job is paused: {self.waiting['doc']} is waiting for "
                                         f"{self.waiting['approver']} to approve it.",
                   "next_step": f"Tell {self.first} it is waiting for approval. Nothing more can be done until then."}
            entry["blocked"] = "pause"
        else:
            out = self.tb.call(name, args)
            if not out.get("ok"):
                self._failed[key] = out.get("error", "")
        seen[key] = seen.get(key, 0) + 1
        entry["ok"], entry["result"] = bool(out.get("ok")), out
        self.trace.append(entry)
        self._note_docs(out)
        return out

    @property
    def _failed(self) -> dict:
        if not hasattr(self, "_failed_calls"):
            self._failed_calls = {}
        return self._failed_calls

    def _note_docs(self, out: dict):
        pr, po = out.get("request_no"), out.get("po_no")
        if pr and pr not in self.docs["requests"]:
            self.docs["requests"].append(pr)
        if po and po not in self.docs["orders"] and out.get("status_code"):
            self.docs["orders"].append(po)
        if "pause" in self.parts and pr and out.get("status_code") == "PA" and not po:
            self.waiting = {"doc": pr, "approver": out.get("approver") or "the approver"}
            self.trace.append({"turn": self.turn, "kind": "harness", "part": "pause",
                               "note": f"paused: {pr} waits for {self.waiting['approver']}"})

    # ------------------------------------------------------------------ the parts that read Ledgerline
    def _check_waiting(self) -> str:
        """Paused: whatever the message says, read the real status from Ledgerline before going on."""
        doc = self.waiting["doc"]
        st = self.tb.call("order_status", {"request_no": doc})
        code = st.get("status_code")
        self.trace.append({"turn": self.turn, "kind": "harness", "part": "pause", "name": "order_status",
                           "args": {"request_no": doc}, "result": st})
        if code == "AP":
            self.waiting = None
            return (f"[harness] Ledgerline shows {doc} as APPROVED by {st.get('approved_by')}. The job resumes: create the "
                    f"purchase order from {doc} and release it.")
        if code == "RJ":
            self.waiting = None
            return f"[harness] Ledgerline shows {doc} as REJECTED. Tell {self.first}; order nothing."
        return (f"[harness] Still paused: Ledgerline shows {doc} as {st.get('status')}, waiting for {st.get('approver')}. "
                f"Nothing can be ordered yet; do not raise it again.")

    def _verify(self, reply: str) -> str | None:
        """A reply that sounds finished is checked against Ledgerline before it goes out."""
        for po in self.docs["orders"]:
            st = self.tb.call("order_status", {"po_no": po})
            code = st.get("status_code")
            if code == "AP" and not self.waiting:
                return (f"Ledgerline shows {po} as APPROVED, NOT YET RELEASED: the supplier does not have it. Release it with "
                        f"release_purchase_order, unless {self.first} asked you not to.")
            if code in ("DR", "PA") and DONE.search(reply) and not HEDGE.search(reply):
                return (f"Ledgerline shows {po} as {st.get('status')}. It has not reached the supplier. Tell {self.first} "
                        f"the true status and what is needed.")
        if not self.docs["orders"] and self.docs["requests"] and DONE.search(reply) and not HEDGE.search(reply):
            return (f"No purchase order exists yet; only {', '.join(self.docs['requests'])}. Do not call anything placed "
                    f"or sent. Tell {self.first} the true status.")
        return None

    # ------------------------------------------------------------------ state across days
    def state(self) -> dict:
        return {"user": self.tb.user, "parts": sorted(self.parts), "messages": self.messages, "waiting": self.waiting,
                "docs": self.docs, "turn": self.turn, "failed": self._failed, "trace": self.trace, "stops": self.stops}

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.state(), f, indent=1, default=str, ensure_ascii=False)

    @classmethod
    def load(cls, path: str, tb, llm: LLM | None = None, **kw) -> "Harness":
        with open(path) as f:
            st = json.load(f)
        h = cls(tb, llm, parts=st["parts"], **kw)
        h.messages, h.waiting, h.docs, h.turn = st["messages"], st["waiting"], st["docs"], st["turn"]
        h._failed_calls = st.get("failed", {})
        h.trace, h.stops = st.get("trace", []), st.get("stops", [])
        return h
