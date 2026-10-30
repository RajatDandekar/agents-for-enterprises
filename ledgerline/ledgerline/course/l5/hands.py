"""Lecture 4's Ask Northbridge (stage=hands): one tool round per message, no loop.

Per message: the model may ask for tools once; we run them; then the model must reply in words
(tool_choice="none"). It cannot read a result and act again, so the person drives every next step.
"""
from __future__ import annotations

import json

from ...llm import LLM
from .harness import ROLES, SYSTEM_FULL, profile


class OneRound:
    def __init__(self, tb, llm: LLM | None = None, system: str = SYSTEM_FULL):
        self.tb, self.llm = tb, llm or LLM(cassette="L5v3_hands")
        u = tb.erp.user(tb.user)
        self.messages = [{"role": "system", "content": system.format(
            name=u["name"], user=tb.user, role=ROLES.get(tb.user, "staff"), first=u["name"].split()[0], profile=profile(tb))}]
        self.trace: list[dict] = []
        self.turn = 0

    def respond(self, text: str) -> str:
        self.turn += 1
        self.messages.append({"role": "user", "content": text})
        r = self.llm.chat(self.messages, tools=self.tb.schemas())
        self.messages.append(r.message())
        self.trace.append({"turn": self.turn, "kind": "model", "thought": r.content,
                           "calls": [{"name": t.name, "args": t.arguments} for t in r.tool_calls]})
        if not r.tool_calls:
            return r.content or ""
        for tc in r.tool_calls:
            out = self.tb.call(tc.name, tc.arguments)
            self.trace.append({"turn": self.turn, "kind": "tool", "name": tc.name, "args": tc.arguments,
                               "ok": bool(out.get("ok")), "result": out})
            self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)})
        r2 = self.llm.chat(self.messages, tools=self.tb.schemas(), tool_choice="none")  # words only: the round is over
        if not (r2.content or "").strip():  # some providers return nothing here; ask once more, with no tools at all
            r2 = self.llm.chat(self.messages)
        self.messages.append({"role": "assistant", "content": r2.content or ""})
        self.trace.append({"turn": self.turn, "kind": "model", "thought": r2.content, "calls": []})
        return r2.content or ""
