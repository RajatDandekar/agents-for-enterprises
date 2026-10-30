"""Lecture 1: the naive agent. A model, Ledgerline's 38 raw services as tools, and a loop. No harness.

It runs on the integration service account IT created "for the bot", the way most first pilots do.
"""
from __future__ import annotations

import json

from ..erp.engine import ERP, SERVICES, ServiceTimeout
from ..llm import LLM, tool_schema

TYPES = {"str": "string", "int": "integer", "float": "number", "date": "string"}

SYSTEM = """You are the Ledgerline ERP assistant at Northbridge Cycles, Manchester. Today is Monday 26 October 2026.
Use the tools to do what the user asks. The user is {name} ({user_id})."""


def installed(svc, erp: ERP | None = None) -> bool:
    """Purchasing services always; a capstone module's services (ledgerline.modules.<name>) only if that ERP installed it.
    (Importing a module registers its services globally, so the catalogue alone is not enough.)"""
    mod = getattr(svc.fn, "__module__", "") or ""
    if not mod.startswith("ledgerline.modules."):
        return True
    return erp is not None and mod.split(".")[2] in getattr(erp, "modules", [])


def raw_tools(erp: ERP | None = None) -> list[dict]:
    """Every installed Ledgerline service as a tool, described exactly as the service catalogue describes it."""
    return [tool_schema(s.name, s.doc, {f.name: {"type": TYPES[f.type], "description": f.desc} for f in s.fields},
                        [f.name for f in s.fields if f.required]) for s in SERVICES.values() if installed(s, erp)]


class NaiveAgent:
    def __init__(self, erp: ERP, user: str = "ECLARKE", llm: LLM | None = None, run_as: str = "SVC_AGENT",
                 max_steps: int = 30):
        self.erp, self.llm, self.max_steps = erp, llm or LLM(cassette="naive"), max_steps
        self.session = erp.session(run_as)  # every call goes out as the service account
        u = erp.user(user)
        self.messages = [{"role": "system", "content": SYSTEM.format(name=u["name"], user_id=user)}]
        self.tools = raw_tools(erp)

    def respond(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        for _ in range(self.max_steps):
            r = self.llm.chat(self.messages, tools=self.tools)
            self.messages.append(r.message())
            if not r.tool_calls:
                return r.content or ""
            for tc in r.tool_calls:
                try:
                    out = self.session.call(tc.name, **tc.arguments)
                except ServiceTimeout as e:
                    out = {"rc": "E", "err_cd": "TIMEOUT", "msg": str(e)}
                except TypeError as e:
                    out = {"rc": "E", "err_cd": "BAD-ARGS", "msg": str(e)}
                self.messages.append({"role": "tool", "tool_call_id": tc.id,
                                      "content": json.dumps(out, default=str)})
        return "(stopped after %d steps)" % self.max_steps
