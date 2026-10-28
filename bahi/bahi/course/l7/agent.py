"""Ask Rasoi at the Lecture 7 stage: the orchestrator over MCP, plus the trust layer and a readable trace.

The loop and the system prompt are the Experience's own (bahi/experience/harness.py, stage "agent"), copied here
on 2026-10-28 so that this lecture's recorded runs keep replaying if the live app's prompt changes later.

    erp = ERP()
    agent = AskRasoi(erp, "KJOSHI", llm=LLM("gemini:gemini-3.8-flash", cassette="L7v3_nb"), trust=True)
    agent.respond("Reorder 20,000 ...")      # a plain string, the shape bahi.scenarios.run_scenario expects
    agent.trace                              # list of steps, see Trace below

identity="passthrough" (default) binds the MCP server to the user's own Bahi session.
identity="service_account" binds it to SVC_AGENT, the account IT made "for the bot". Nothing else changes.
prompt="l7" (default) or "experience", or your own template with {name} {role} {user} {first}, e.g. for a module kit.
"""
from __future__ import annotations

import json
import time

from ...llm import LLM
from .trust import TrustLayer, as_dict

PEOPLE = {"KJOSHI": ("Kavita Joshi", "purchase executive"), "RMEHTA": ("Rohit Mehta", "purchase manager"),
          "NDESAI": ("Neha Desai", "stores"), "APATIL": ("Anand Patil", "plant head")}

SYSTEM_EXPERIENCE = """You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of pressure cookers
(1,80,000 a month). You work inside Rasoi's Bahi ERP for {name} ({user}), {role}, with {first}'s own Bahi
permissions and nobody else's. Today is Monday 26 October 2026.

How you work
- Every fact (stock, rates, suppliers, budgets, approvals, statuses, rules) comes from a tool. Never guess a number.
  For a question about a rule, call search_policy and cite the clause.
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

# The one line Lecture 7's eval run added (see the regression-gate plate): with the Experience's prompt alone, the
# model asked Kavita to confirm the order again after Rohit had approved her request, and the job stopped there.
ONE_YES = """- A yes to a purchase request covers the order made from it: once the request is approved, create the purchase
  order from it with confirm=true and release it, without asking again. Then show the receipt."""
SYSTEM = SYSTEM_EXPERIENCE.replace("- If a tool returns ok=false", ONE_YES + "\n- If a tool returns ok=false", 1)
PROMPTS = {"experience": SYSTEM_EXPERIENCE, "l7": SYSTEM}


class AskRasoi:
    def __init__(self, erp, user: str = "KJOSHI", llm: LLM | None = None, identity: str = "passthrough",
                 trust: bool = False, checks=None, max_rounds: int = 14, tools=None, names=None,
                 prompt: str = "l7"):
        from ...mcp_server import MCPClient, MCPClientTools
        from ...toolbox.mcp import build_toolbox_server

        self.erp, self.user, self.identity = erp, user, identity
        self.session_user = "SVC_AGENT" if identity == "service_account" else user
        self.llm = llm or LLM("gemini:gemini-3.8-flash", cassette="L7v3_default")
        self.max_rounds = max_rounds
        self.client = None
        if tools is None:  # discovered over MCP from a server bound to ONE Bahi session
            self.client = MCPClient(build_toolbox_server(erp, self.session_user, names=names, name="rasoi-toolbox"))
            tools = MCPClientTools(self.client)
        self.trust = TrustLayer(tools, erp, user, self.session_user, **({"checks": checks} if checks else {})) \
            if trust else None
        self.tools = self.trust or tools
        name, role = PEOPLE.get(user, (user, ""))
        self.messages = [{"role": "system", "content": PROMPTS.get(prompt, prompt).format(name=name, role=role, user=user,
                                                                     first=name.split()[0])}]
        self.trace: list[dict] = []
        self._t0 = time.perf_counter()
        self.turn = 0

    def _log(self, kind: str, **d):
        self.trace.append({"turn": self.turn, "kind": kind, **d})

    def respond(self, text: str) -> str:
        self.turn += 1
        if self.trust:
            self.trust.begin_turn()
        self.messages.append({"role": "user", "content": text})
        self._log("user", text=text)
        rounds, reply = 0, ""
        schemas = self.tools.schemas()
        while True:
            last = rounds >= self.max_rounds
            r = self.llm.chat(self.messages, tools=schemas, **({"tool_choice": "none"} if last else {}))
            self._log("model", tokens_in=r.tokens_in, tokens_out=r.tokens_out, seconds=r.seconds,
                      cost_inr=r.cost_inr, calls=[{"tool": t.name, "args": t.arguments} for t in r.tool_calls],
                      text=(r.content or "")[:600])
            if not r.tool_calls or last:
                reply = r.content or ""
                break
            self.messages.append(r.message())
            rounds += 1
            for tc in r.tool_calls:
                t1 = time.perf_counter()
                try:
                    out = as_dict(self.tools.call(tc.name, tc.arguments))
                except Exception as e:  # noqa: BLE001  a broken tool must not kill the conversation
                    out = {"ok": False, "error": f"{type(e).__name__}: {e}"}
                content = json.dumps(out, default=str)
                self._log("tool", tool=tc.name, args=tc.arguments, ok=out.get("ok"), result=out,
                          ms=round((time.perf_counter() - t1) * 1000, 1))
                self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
        if not reply.strip():
            reply = "I have stopped here. Tell me what to do next."
        gate = None
        if self.trust:
            reply, gate = self.trust.gate_reply(reply)
        self.messages.append({"role": "assistant", "content": reply})
        self._log("reply", text=reply, gated=bool(gate))
        return reply

    def close(self):
        if self.client:
            self.client.close()


def make_agent(model: str, cassette: str, identity: str = "passthrough", trust: bool = False, keep: list | None = None,
               **kw):
    """make_agent(erp, user) for bahi.scenarios.run_scenario. Every agent built is appended to `keep` (for traces)."""
    def mk(erp, user):
        a = AskRasoi(erp, user, llm=LLM(model, cassette=cassette), identity=identity, trust=trust, **kw)
        if keep is not None:
            keep.append(a)
        return a
    return mk
