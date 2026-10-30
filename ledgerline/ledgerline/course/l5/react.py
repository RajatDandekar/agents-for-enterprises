"""ReAct written out in text: the model writes Thought / Action / Action Input; our code parses the Action line,
runs the tool, and writes the Observation back. No tool-calling API is used: the tools are described in the prompt.

    agent = ReActAgent(Toolbox(ERP(), "ECLARKE"), LLM(cassette="L5v3_react"))
    agent.respond("How many days of city e-bike battery packs do we have?")
    agent.steps   # every Thought, Action, Action Input and Observation, in order
"""
from __future__ import annotations

import json
import re

from ...llm import LLM
from .harness import ROLES, profile

RULES = """Rules of the job:
- Before the first write of a job, preview it (confirm=false), show {first} the numbers and ask once. After {first} says yes, commit (confirm=true) and carry on with the next steps without asking again.
- If an Observation has ok=false, read its error and next_step and follow next_step. Never repeat a call that failed with the same arguments.
- A purchase request above {first}'s approval limit waits for the manager. While it is WAITING FOR APPROVAL, say so and stop; order nothing until it is approved.
- An order reaches the supplier only when it is RELEASED. After creating an approved order, release it.
- Report the status the receipt gives you, in plain words. Never say an order is placed or sent unless its receipt says RELEASED.
- Lithium-cell parts may only be bought from a supplier with a valid UN 38.3 certificate (Purchase Policy §6.2). Answer policy questions from search_policy and cite the section."""

PROMPT = """You are Ask Northbridge, the assistant on Northbridge Cycles' home page, working inside Ledgerline ERP for {name} ({user}), {role}.
Today is Monday 26 October 2026. {profile}

You can use these tools:
{tools}

Work one step at a time, in exactly this format:
Thought: what you know so far and what to do next
Action: the name of one tool from the list
Action Input: the arguments, as one JSON object on one line
Then stop writing. The system runs the tool and replies with:
Observation: the tool's result

Repeat Thought / Action / Action Input / Observation as often as you need.
When you are ready to reply to {first}, write:
Thought: I can reply now.
Final Answer: your reply to {first}

""" + RULES

ACTION = re.compile(r"^\s*Action\s*:\s*`?([A-Za-z_][\w]*)`?", re.M)
INPUT = re.compile(r"^\s*Action\s*Input\s*:\s*", re.M)
FINAL = re.compile(r"^\s*Final\s*Answer\s*:\s*", re.M)
THOUGHT = re.compile(r"^\s*Thought\s*:\s*(.*?)(?=^\s*(?:Action|Final\s*Answer)\s*:|\Z)", re.M | re.S)


def tool_lines(tb) -> str:
    """One line per tool: name(arg: type, ...): description. Required arguments have no '?'."""
    out = []
    for s in tb.schemas():
        f = s["function"]
        req = set(f["parameters"].get("required", []))
        args = ", ".join(f"{k}{'' if k in req else '?'}: {v.get('type', 'string')}"
                         for k, v in f["parameters"].get("properties", {}).items())
        out.append(f"- {f['name']}({args}): {f['description']}")
    return "\n".join(out)


def parse_step(text: str) -> dict:
    """Split one model turn into thought, action, action_input, final. The parsing is the whole trick."""
    text = text or ""
    cut = re.search(r"^\s*Observation\s*:", text, re.M)   # the model sometimes writes its own Observation: drop it
    invented = bool(cut)
    if cut:
        text = text[:cut.start()]
    m = THOUGHT.search(text)
    step = {"thought": m.group(1).strip() if m else "", "action": None, "action_input": None, "final": None,
            "invented_observation": invented, "error": None}
    a, f = ACTION.search(text), FINAL.search(text)
    if a and (not f or a.start() < f.start()):
        step["action"] = a.group(1)
        i = INPUT.search(text, a.end())
        if not i:
            step["error"] = "No 'Action Input:' line after the Action."
            return step
        raw = text[i.end():].strip().strip("`")
        raw = raw[raw.find("{"):] if "{" in raw else raw
        try:
            step["action_input"], _ = json.JSONDecoder().raw_decode(raw)
        except json.JSONDecodeError as e:
            step["error"] = f"Action Input is not valid JSON ({e.msg})."
        if step["action_input"] is not None and not isinstance(step["action_input"], dict):
            step["action_input"], step["error"] = None, "Action Input must be one JSON object."
    elif f:
        step["final"] = text[f.end():].strip()
    elif m:
        step["error"] = "A Thought with no Action and no Final Answer."   # format drift: ask it to go on
    elif not text.strip():
        step["error"] = "Your reply was empty."
    else:
        step["final"] = text.strip()  # plain words, no format at all: treat them as the reply
        step["plain"] = True
    return step


class ReActAgent:
    def __init__(self, tb, llm: LLM | None = None, max_steps: int = 15, use_stop: bool = True):
        self.tb, self.llm = tb, llm or LLM(cassette="L5v3_react")
        u = tb.erp.user(tb.user)
        self.first = u["name"].split()[0]
        self.prompt = PROMPT.format(name=u["name"], user=tb.user, role=ROLES.get(tb.user, "staff"),
                                    first=self.first, tools=tool_lines(tb), profile=profile(tb))
        self.messages = [{"role": "system", "content": self.prompt}]
        self.max_steps, self.use_stop = max_steps, use_stop
        self.steps: list[dict] = []
        self.trace = self.steps
        self.turn = 0

    def respond(self, text: str) -> str:
        self.turn += 1
        self.messages.append({"role": "user", "content": text})
        for n in range(self.max_steps):
            kw = {"stop": ["\nObservation:"]} if self.use_stop else {}
            r = self.llm.chat(self.messages, **kw)
            st = parse_step(r.content)
            st.update(turn=self.turn, step=n, raw=r.content, tokens_in=r.tokens_in, tokens_out=r.tokens_out)
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
            st["kind"], st["name"], st["args"], st["ok"] = "tool", st["action"], st["action_input"], bool(obs.get("ok"))
            self.steps.append(st)
            self.messages.append({"role": "user", "content": "Observation: " + json.dumps(obs, default=str)})
        return f"(stopped after {self.max_steps} steps)"
