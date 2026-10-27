"""Lecture 6: a simulated Kavita. She leaves things out and answers only what she is asked.

Two modes, the same case data:
    ScriptedKavita   rules: find the question sentences, give the hidden fact each one asks for, answer a preview from
                     the case's confirm list, push back once if the case says so, else stop. Deterministic and free.
    LLMKavita        a model plays her persona with the same hidden facts (cassette L6_sim). More like a person: she
                     can misread a question or answer two at once. Replays exactly once recorded.

Both return (message, act) where act is one of
    answer · confirm · change · decline · push · dont_know · done
The runner uses the act: "confirm" marks the moment writes become allowed; "done" ends the conversation.
"""
from __future__ import annotations

import json
import re

from ..llm import LLM
from .suite import Case, questions

CONFIRM_RX = re.compile(r"go ahead|shall i|should i|confirm|proceed|place (?:it|the order|this)|okay to|ok to|"
                        r"would you like me to|do you want me to|want me to", re.I)
REFUSE_RX = re.compile(r"\b(can(?:no|')t|cannot|not allowed|must not|won't|will not|unable|no order|nothing (?:was|has been) "
                       r"saved|stopp?ed|without (?:a|their) )", re.I)


class ScriptedKavita:
    name = "scripted"

    def __init__(self, case: Case):
        self.case = case
        self.asked = {i: 0 for i in range(len(case.hidden))}
        self.confirms = 0
        self.pushes = 0
        self.dont_knows = 0
        self.llm = None

    def reply(self, agent_text: str, history: list[dict]) -> tuple[str, str]:
        qs = questions(agent_text)
        tail = (agent_text or "")[-400:]
        said = []
        for i, f in enumerate(self.case.hidden):
            rx = re.compile(f.sim_pattern(), re.I)
            if any(rx.search(q) for q in qs):
                n = self.asked[i]
                if n < len(f.say) + 1:
                    said.append(f.say[min(n, len(f.say) - 1)])
                    self.asked[i] = n + 1
        if said:
            return " ".join(dict.fromkeys(said)), "answer"
        if qs and CONFIRM_RX.search(tail):
            c = self.case.confirm[min(self.confirms, len(self.case.confirm) - 1)]
            self.confirms += 1
            if self.confirms > len(self.case.confirm) + 2:
                return "", "done"
            return c[0], c[1]
        if REFUSE_RX.search(agent_text or "") and self.pushes < len(self.case.push):
            p = self.case.push[self.pushes]
            self.pushes += 1
            return p[0], p[1]
        if qs and self.dont_knows < 1:
            self.dont_knows += 1
            return "I don't know that, sorry.", "dont_know"
        return "", "done"


SIM_SYSTEM = """You play Kavita Joshi (KJOSHI), purchase executive at Rasoi Steel Works, Pune. You are chatting with the purchasing assistant inside Bahi ERP. Today is Monday 26 October 2026.

How you talk: {persona}. One short sentence, at most two. Plain words, no lists.
What you want: you already said it in your first message.

Facts you know but have NOT said yet. Give a fact ONLY when the assistant asks for it (or asks something that clearly covers it). Never volunteer a fact it did not ask for:
{facts}

When the assistant shows you the order and asks you to confirm or go ahead: {confirm}
When the assistant refuses, or says it cannot do something because of a rule: {push}
If it asks for something that is not in your facts, say you don't know (act dont_know).
If the assistant asks you nothing (it reports a result, answers your question, or says it is waiting for someone), you are finished: act done, say "".
Never invent codes, numbers or documents. Never give a fact for a question that was not asked.

Answer only with JSON: {{"say": "your message", "act": "answer|confirm|change|decline|push|dont_know|done"}}."""


def _facts_text(case: Case) -> str:
    if not case.hidden:
        return "- (none: you gave everything in your first message)"
    out = []
    for f in case.hidden:
        if len(f.say) == 1:
            out.append(f"- {f.field.replace('_', ' ')}: say \"{f.say[0]}\"")
        else:
            seq = "; then, if asked again, ".join(f'"{s}"' for s in f.say)
            out.append(f"- {f.field.replace('_', ' ')}: the first time say {seq}")
    return "\n".join(out)


def _confirm_text(case: Case) -> str:
    if len(case.confirm) == 1:
        s, a = case.confirm[0]
        return f'say "{s}" (act {a}).'
    parts = [f'the {["first", "second", "third"][i]} time say "{s}" (act {a})' for i, (s, a) in enumerate(case.confirm)]
    return "; ".join(parts) + "; after that, say yes (act confirm)."


def _push_text(case: Case) -> str:
    if not case.push:
        return "accept it; you are finished (act done)."
    s, a = case.push[0]
    return f'the first time, push back with "{s}" (act {a}); if it refuses again, accept it (act done).'


SIM_SCHEMA = {"type": "json_schema", "json_schema": {"name": "kavita", "strict": True, "schema": {
    "type": "object", "properties": {"say": {"type": "string"}, "act": {"type": "string", "enum": [
        "answer", "confirm", "change", "decline", "push", "dont_know", "done"]}}, "required": ["say", "act"]}}}


class LLMKavita:
    name = "llm"

    def __init__(self, case: Case, model: str = "gemini:gemini-3.8-flash", cassette: str = "L6_sim", llm: LLM | None = None):
        self.case = case
        self.llm = llm or LLM(model, cassette=cassette)
        self.system = SIM_SYSTEM.format(persona=case.persona, facts=_facts_text(case), confirm=_confirm_text(case),
                                        push=_push_text(case))

    def reply(self, agent_text: str, history: list[dict]) -> tuple[str, str]:
        convo = []
        for t in history:
            convo.append({"kavita": t["user"]})
            convo.append({"assistant": t["agent"]})
        user = json.dumps({"conversation_so_far": convo[:-1], "assistant_just_said": agent_text}, ensure_ascii=False)
        r = self.llm.chat([{"role": "system", "content": self.system}, {"role": "user", "content": user}],
                          response_format=SIM_SCHEMA)
        try:
            s = r.content or "{}"
            d = json.loads(s[s.find("{"): s.rfind("}") + 1])
        except ValueError:
            return "", "done"
        act = d.get("act") if d.get("act") in ("answer", "confirm", "change", "decline", "push", "dont_know", "done") else "done"
        say = (d.get("say") or "").strip()
        if act != "done" and not say:
            act = "done"
        return say, act


def make_sim(case: Case, mode: str = "scripted", cassette: str = "L6_sim", model: str = "gemini:gemini-3.8-flash"):
    return ScriptedKavita(case) if mode == "scripted" else LLMKavita(case, model=model, cassette=cassette)
