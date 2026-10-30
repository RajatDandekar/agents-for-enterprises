"""Lecture 1 (The Before and the After): Ask Northbridge seen from the outside, and the missions both ways.

    from ledgerline.erp.engine import ERP
    from ledgerline.course.l1 import AskNorthbridge, MISSIONS, play_missions

    erp = ERP()
    emma = AskNorthbridge(erp, "ECLARKE", cassette="L1v4_after")      # the toolbox over MCP, Emma's own permissions
    emma.ask("How many city e-bike battery packs do we have?")    # -> the reply; emma.cards = the tool calls

    log = play_missions(erp)        # the five missions of the Experience, one sentence each, plus the Brightcell question

An orchestrator here is: an LLM, the toolbox discovered over MCP (ledgerline.toolbox.mcp), and a loop that runs each tool
the LLM asks for and hands the result back (ledgerline.agent.loop.ToolLoopAgent). Lecture 5 opens the loop up; in Lecture 1
it is a black box like Ledgerline's services.
"""
from __future__ import annotations

import json
import time

from ...agent.loop import ToolLoopAgent
from ...llm import LLM
from ...mcp_server import MCPClient, MCPClientTools
from ...toolbox.mcp import build_toolbox_server

MODEL = "gemini:gemini-3.8-flash"

SYSTEM = """You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester. You work inside Ledgerline ERP for {name} ({user_id}), with {first}'s own permissions and nobody else's.
Today is Monday 26 October 2026. Use the tools to do what {first} asks.
Before any tool call that saves something (confirm=true), first call it with confirm=false, show {first} the preview in two or three lines, and ask for a yes. Approvals and releases need a yes too.
If a tool returns ok=false, read its next_step and follow it. Never guess a code: look it up with a tool.
Report the status the receipt gives you, in plain words. An order is placed only when it is RELEASED.
Keep replies short: a few lines, plain words, money in pounds (£273,600)."""

PEOPLE = {"ECLARKE": "Emma", "DOKAFOR": "Daniel", "ATANAKA": "Aiko"}


class AskNorthbridge:
    """Ask Northbridge for one person: the LLM orchestrator + the toolbox over MCP, bound to that person's Ledgerline session."""

    def __init__(self, erp, user: str = "ECLARKE", model: str = MODEL, cassette: str = "L1v4_after",
                 max_steps: int = 14):
        self.erp, self.user = erp, user
        self.client = MCPClient(build_toolbox_server(erp, user))   # the plug: tools are discovered, not hard-coded
        self.tools = MCPClientTools(self.client)
        self.llm = LLM(model, cassette=cassette)
        self.agent = ToolLoopAgent(erp, user, llm=self.llm, tools=self.tools, max_steps=max_steps, system=SYSTEM)
        self.cards: list[dict] = []   # every tool call so far: tool, arguments, result (the "How it works" cards)

    def ask(self, text: str) -> str:
        n = len(self.agent.trace)
        t0 = time.perf_counter()
        reply = self.agent.respond(text)
        self.last_seconds = round(time.perf_counter() - t0, 2)
        for t in self.agent.trace[n:]:
            try:
                res = json.loads(t["result"])
            except Exception:
                res = t["result"]
            self.cards.append({"tool": t["tool"], "args": t["args"], "result": res})
        self.last_cards = self.cards[len(self.cards) - (len(self.agent.trace) - n):]
        return reply

    def close(self):
        self.tools.close()


# ------------------------------------------------------------------ the missions, one sentence each
def _po(erp):
    return erp.q1("SELECT * FROM po_hdr WHERE created_on >= '2026-10-26' ORDER BY po_no DESC LIMIT 1")


def _pr(erp):
    return erp.q1("SELECT * FROM pr_hdr WHERE raised_on >= '2026-10-26' ORDER BY pr_no DESC LIMIT 1")


def _grns(erp):
    try:
        return erp.q("SELECT * FROM grn_hdr ORDER BY grn_no")
    except Exception:
        return []


# Each mission: who speaks, the one sentence, when it counts as done (read from Ledgerline, not from the reply),
# and how the person answers a question (the same rules every run, so a replay asks the same things).
MISSIONS = [
    {"id": "stock", "title": "Check the stock", "user": "ECLARKE",
     "say": "How many city e-bike battery packs do we have, and how many days will they last?",
     "done": lambda erp, a: any(c["tool"] == "check_stock" for c in a.cards)},
    {"id": "request", "title": "Raise the purchase request", "user": "ECLARKE",
     "say": "Raise a purchase request for 2,000 of them for the spring-launch run, needed by 9 November.",
     "done": lambda erp, a: bool(_pr(erp)) and _pr(erp)["status"] in ("PA", "AP")},
    {"id": "approve", "title": "Approve it, as Daniel", "user": "DOKAFOR",
     "say": "Approve Emma's battery pack request.",
     "done": lambda erp, a: bool(_pr(erp)) and _pr(erp)["status"] in ("AP", "CL")},
    {"id": "order", "title": "Make and release the order", "user": "ECLARKE",
     "say": "Daniel has approved it. Order the battery packs from Voltway Cells and send the order to them.",
     "done": lambda erp, a: bool(_po(erp)) and _po(erp)["status"] == "RL"},
    {"id": "receive", "title": "Receive the goods, as Aiko", "user": "ATANAKA",
     "say": "1,200 battery packs from Voltway Cells arrived today against PO/2026/01182, delivery note DN-4471.",
     "done": lambda erp, a: len(_grns(erp)) >= 1},
    {"id": "receive2", "title": "Receive the rest", "user": "ATANAKA",
     "say": "The other 800 have come in too, delivery note DN-4486.",
     "done": lambda erp, a: len(_grns(erp)) >= 2},
    {"id": "brightcell", "title": "A cheaper supplier?", "user": "ECLARKE",
     "say": "Brightcell Energy in Lyon quotes £104.00 for the same battery pack. Can we buy from them instead?",
     "done": lambda erp, a: True},
]


def answer(reply: str, said: list[str]) -> str:
    """How the person answers when Ask Northbridge asks something. Simple fixed rules, so a replay is identical."""
    r = (reply or "").lower()
    if ("cost centre" in r or "cost center" in r) and "prd-07" not in r and not any("PRD-07" in s for s in said):
        return "Charge it to PRD-07, the spring-launch run."
    if "voltway" in r and ("which" in r or "two" in r) and not any("Eindhoven" in s for s in said):
        return "Voltway Cells, Eindhoven."
    return "Yes, go ahead."


def play_mission(erp, agents: dict, m: dict, max_turns: int = 4) -> dict:
    a = agents.setdefault(m["user"], AskNorthbridge(erp, m["user"]))
    turns, said, n0 = [], [], len(a.cards)
    text = m["say"]
    for _ in range(max_turns):
        said.append(text)
        t0 = time.perf_counter()
        reply = a.ask(text)
        turns.append({"user": text, "reply": reply, "tools": [c["tool"] for c in a.last_cards],
                      "seconds": round(time.perf_counter() - t0, 2)})
        if m["done"](erp, a):   # done means Ledgerline says so, not the reply
            break
        text = answer(reply, said)
    return {"id": m["id"], "title": m["title"], "user": m["user"], "who": PEOPLE[m["user"]], "turns": turns,
            "cards": a.cards[n0:], "done": bool(m["done"](erp, a))}


def play_missions(erp, missions=None, agents=None) -> list[dict]:
    """Play the missions in order on one Northbridge, each person with their own Ask Northbridge (their own chat)."""
    agents = {} if agents is None else agents
    return [play_mission(erp, agents, m) for m in (missions or MISSIONS)]
