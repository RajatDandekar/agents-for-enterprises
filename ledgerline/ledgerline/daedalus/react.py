"""ReAct written out as text (Lecture 5, Section 2): the model writes Thought / Action / Action Input, our code parses
the Action line, runs the tool and writes the Observation back. No tool-calling API: the tools are listed in the prompt.

    agent = ReAct(Toolbox(ERP(), "ECLARKE", names=SHIPPED_TOOLS), LLM(cassette="L5v4_react"))
    agent.respond("How many days of BAT-500 battery packs do we have?")
    agent.steps      # every Thought, Action, Action Input and Observation, in order, with the raw text

ReAct: "Reason + Act", Yao et al., 2022 (arXiv:2210.03629). The parsing is the whole trick, and where it breaks.
"""
from __future__ import annotations

import json
import re

from ..llm import LLM

PROMPT = """You are Ask Northbridge, working inside Northbridge Cycles' Ledgerline ERP for Emma Clarke (ECLARKE), purchase
executive. Today is Monday 26 October 2026. Every fact comes from a tool; never guess a number.

You can use these tools:
{tools}

Work one step at a time, in exactly this format:
Thought: what you know so far and what to do next
Action: the name of one tool from the list
Action Input: the arguments, as one JSON object on one line
Then stop writing. The system runs the tool and replies with:
Observation: the tool's result

Repeat Thought / Action / Action Input / Observation as often as you need.
When you are ready to reply to Emma, write:
Thought: I can reply now.
Final Answer: your reply to Emma, in two to five plain lines.

Rules: anything that saves (confirm=true) needs Emma's yes to a preview first (confirm=false). A request above Emma's
limit waits for Daniel Okafor: say so and order nothing until it is approved."""

ACTION = re.compile(r"^\s*Action\s*:\s*`?([A-Za-z_]\w*)`?", re.M)
INPUT = re.compile(r"^\s*Action\s*Input\s*:\s*", re.M)
FINAL = re.compile(r"^\s*Final\s*Answer\s*:\s*", re.M)
THOUGHT = re.compile(r"^\s*Thought\s*:\s*(.*?)(?=^\s*(?:Action|Final\s*Answer)\s*:|\Z)", re.M | re.S)


def tool_lines(tb) -> str:
    """One line per tool: name(arg: type, ...): description. Optional arguments end in '?'."""
    out = []
    for s in tb.schemas():
        f = s["function"]
        req = set(f["parameters"].get("required", []))
        a = ", ".join(f"{k}{'' if k in req else '?'}: {v.get('type', 'string')}"
                      for k, v in f["parameters"].get("properties", {}).items())
        out.append(f"- {f['name']}({a}): {f['description']}")
    return "\n".join(out)


def parse_step(text: str) -> dict:
    """Split one model turn into thought, action, action_input and final answer."""
    text = text or ""
    cut = re.search(r"^\s*Observation\s*:", text, re.M)   # it sometimes writes its own Observation: drop it
    invented = bool(cut)
    if cut:
        text = text[:cut.start()]
    m = THOUGHT.search(text)
    st = {"thought": m.group(1).strip() if m else "", "action": None, "action_input": None, "final": None,
          "invented_observation": invented, "error": None}
    a, f = ACTION.search(text), FINAL.search(text)
    if a and (not f or a.start() < f.start()):
        st["action"] = a.group(1)
        i = INPUT.search(text, a.end())
        if not i:
            st["error"] = "No 'Action Input:' line after the Action."
            return st
        raw = text[i.end():].strip().strip("`")
        raw = raw[raw.find("{"):] if "{" in raw else raw
        try:
            st["action_input"], _ = json.JSONDecoder().raw_decode(raw)
        except json.JSONDecodeError as e:
            st["error"] = f"Action Input is not valid JSON ({e.msg})."
        if st["action_input"] is not None and not isinstance(st["action_input"], dict):
            st["action_input"], st["error"] = None, "Action Input must be one JSON object."
    elif f:
        st["final"] = text[f.end():].strip()
    elif m:
        st["error"] = "A Thought with no Action and no Final Answer."
    elif not text.strip():
        st["error"] = "The reply was empty."
    else:
        st["final"], st["plain"] = text.strip(), True
    return st


class ReAct:
    def __init__(self, tb, llm: LLM | None = None, max_steps: int = 12, use_stop: bool = True):
        self.tb, self.llm = tb, llm or LLM(cassette="L5v4_react")
        self.prompt = PROMPT.format(tools=tool_lines(tb))
        self.messages = [{"role": "system", "content": self.prompt}]
        self.max_steps, self.use_stop = max_steps, use_stop
        self.steps: list[dict] = []
        self.turn = 0

    def respond(self, text: str) -> str:
        self.turn += 1
        self.messages.append({"role": "user", "content": text})
        for n in range(self.max_steps):
            kw = {"stop": ["\nObservation:"]} if self.use_stop else {}
            r = self.llm.chat(self.messages, reasoning_effort="low", **kw)
            st = parse_step(r.content)
            st.update(turn=self.turn, step=n + 1, raw=r.content or "", tokens_in=r.tokens_in, tokens_out=r.tokens_out,
                      seconds=r.seconds)
            kept = (r.content or "").split("\nObservation:")[0].rstrip()
            self.messages.append({"role": "assistant", "content": kept})
            if st["final"] is not None:
                self.steps.append(st)
                return st["final"]
            if st["error"]:
                obs = {"ok": False, "error": st["error"],
                       "next_step": "Continue in the format: Action and Action Input (one JSON object), or Final Answer."}
            else:
                obs = self.tb.call(st["action"], st["action_input"])
            st["observation"] = obs
            self.steps.append(st)
            self.messages.append({"role": "user", "content": "Observation: " + json.dumps(obs, default=str)})
        return f"(stopped after {self.max_steps} steps)"
