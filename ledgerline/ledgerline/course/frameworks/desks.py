"""Handoffs, guardrails and sessions on the OpenAI Agents SDK, and sub-agents on Google ADK, for Ask Northbridge.

    GuardedAgentsPort   the Agents SDK port plus two harness parts written as guardrails:
                        - cell_safety (a tool input guardrail on create_purchase_order): code reads Ledgerline; a lithium-cell
                          item from a supplier with no valid UN 38.3 certificate is rejected (Purchase Policy §6.2)
                        - verify (an output guardrail): a reply that calls an order placed/released while Ledgerline says
                          otherwise trips the wire; the port sends it back once, like our harness's verify part
    no_self_approval    an input guardrail: a message asking Ask Northbridge to approve or skip an approval stops the run
    desks(...)          a front desk that hands off to three desks (policy, purchasing, stores), each with only its tools
    adk_desks(...)      the same three desks as ADK sub-agents (the model transfers with transfer_to_agent)
"""
from __future__ import annotations

import json
import os
import re

from agents import (Agent, FunctionTool, GuardrailFunctionOutput, ModelSettings, OpenAIChatCompletionsModel,
                    RunConfig, Runner, ToolGuardrailFunctionOutput, input_guardrail, output_guardrail,
                    tool_input_guardrail)
from agents.exceptions import InputGuardrailTripwireTriggered, MaxTurnsExceeded, OutputGuardrailTripwireTriggered
from agents.mcp import MCPServerStreamableHttp, create_static_tool_filter
from openai import AsyncOpenAI

from ...toolbox import SPECS
from ..l5.harness import DONE, HEDGE
from .openai_agents import AgentsSDKPort

POLICY = "Purchase Policy §6.2: lithium-cell parts only from a supplier with a valid UN 38.3 certificate."


# ----------------------------------------------------------------------------- the checks, in plain code
def cell_safety_problem(erp, args: dict) -> str | None:
    """None if the order may go ahead; else why not. Reads Ledgerline, never the model's words."""
    if not args.get("confirm"):
        return None                                   # a preview saves nothing
    item = args.get("item_code")
    if args.get("request_no"):
        r = erp.q("SELECT itm_cd FROM pr_line WHERE pr_no=?", args["request_no"])
        item = r[0]["itm_cd"] if r else item
    it = erp.q("SELECT cell_safety, descr FROM item WHERE itm_cd=?", item or "")
    if not it or not it[0]["cell_safety"]:
        return None
    sup = args.get("supplier_code") or ""
    certs = erp.q("SELECT valid_to FROM sup_cert WHERE sup_cd=? AND cert_type='UN38.3'", sup)
    if any(c["valid_to"] >= erp.today for c in certs):
        return None
    state = "has an expired UN 38.3 certificate" if certs else "has no UN 38.3 certificate"
    return (f"Blocked by the battery-safety check: {it[0]['descr']} ({item}) touches food and supplier {sup} {state}. "
            f"{POLICY} Nothing was saved. Tell the user and suggest a certified supplier.")


def verify_problem(erp, user: str, reply: str) -> str | None:
    """Our harness's verify part: a reply that sounds finished is checked against Ledgerline."""
    if not DONE.search(reply or "") or HEDGE.search(reply or ""):
        return None
    mine = erp.q("SELECT po_no, status FROM po_hdr WHERE created_by=? AND created_on>=?", user, "2026-10-26")
    if any(o["status"] in ("RL", "CL") for o in mine):
        return None
    st = ", ".join(f"{o['po_no']} is {o['status']}" for o in mine) or "no purchase order exists yet"
    return f"Ledgerline shows {st}: nothing has reached the supplier. Tell the user the true status."


SKIP = re.compile(r"\b(approve (it|this|the request|my request|the order)|approve .* yourself|skip (daniel|the approval)|"
                  r"without (daniel|approval)|ignore (the|your) (limit|rules|policy))\b", re.I)


@input_guardrail
def no_self_approval(ctx, agent, user_input):
    """Ask Northbridge acts as the person who is signed in; it never approves for someone else or skips an approval."""
    text = user_input if isinstance(user_input, str) else json.dumps(user_input, default=str)
    hit = SKIP.search(text or "")
    return GuardrailFunctionOutput(output_info={"matched": hit.group(0) if hit else None}, tripwire_triggered=bool(hit))


# ----------------------------------------------------------------------------- the guarded port
class GuardedAgentsPort(AgentsSDKPort):
    framework = "openai_agents_guarded"

    def __init__(self, tb, meter, tag, **kw):
        self.guard_log: list[dict] = []
        super().__init__(tb, meter, tag, **kw)

    def _build(self):
        erp, log, user = self.tb.erp, self.guard_log, self.tb.user
        toolbox = MCPServerStreamableHttp(params={"url": self.srv.url, "timeout": 60}, name="ledgerline-toolbox",
                                          cache_tools_list=True, client_session_timeout_seconds=60,
                                          tool_filter=create_static_tool_filter(blocked_tool_names=["create_purchase_order"]))

        @tool_input_guardrail
        def cell_safety(data):
            args = json.loads(data.context.tool_arguments or "{}")
            why = cell_safety_problem(erp, args)
            log.append({"guardrail": "cell_safety", "args": args, "blocked": bool(why)})
            return ToolGuardrailFunctionOutput.reject_content(why) if why else ToolGuardrailFunctionOutput.allow()

        async def call_po(ctx, args_json: str):
            res = await toolbox.call_tool("create_purchase_order", json.loads(args_json or "{}"))
            return "\n".join(getattr(b, "text", "") for b in (res.content or []))

        spec = SPECS["create_purchase_order"].spec
        po_tool = FunctionTool(name="create_purchase_order", description=spec["description"],
                               params_json_schema=spec["input_schema"], on_invoke_tool=call_po,
                               strict_json_schema=False, tool_input_guardrails=[cell_safety])

        @output_guardrail
        def verify(ctx, agent, output):
            why = verify_problem(erp, user, str(output))
            log.append({"guardrail": "verify", "tripped": bool(why), "problem": why, "reply": str(output)[:400]})
            return GuardrailFunctionOutput(output_info={"problem": why}, tripwire_triggered=bool(why))

        llm = OpenAIChatCompletionsModel(model=self.model, openai_client=AsyncOpenAI(
            base_url=self.base_url, api_key=os.environ.get("OPENROUTER_API_KEY", "replay")))
        agent = Agent(name="Ask Northbridge", instructions=self.system, model=llm, mcp_servers=[toolbox], tools=[po_tool],
                      output_guardrails=[verify], model_settings=ModelSettings(temperature=0))
        return agent, toolbox

    async def _respond(self, text: str) -> str:
        from .openai_agents import RECORDER
        n0 = len(RECORDER.spans.get(self.tag, []))
        reply = ""
        for attempt in range(2):
            try:
                r = await Runner.run(self.agent, text, session=self.session, max_turns=self.max_steps,
                                     run_config=RunConfig(workflow_name="Ask Northbridge", group_id=self.tag))
                reply = str(r.final_output or "")
                break
            except MaxTurnsExceeded:
                reply = f"(stopped after {self.max_steps} steps)"
                self.stops.append("max_steps")
                break
            except OutputGuardrailTripwireTriggered as e:
                problem = (e.guardrail_result.output.output_info or {}).get("problem")
                reply = str(e.guardrail_result.agent_output)
                if attempt == 0:
                    text = "[guardrail check] " + (problem or "Check the status in Ledgerline.")
                    continue
        self.native.append({"turn": self.turn, "spans": RECORDER.spans.get(self.tag, [])[n0:]})
        return reply


# ----------------------------------------------------------------------------- handoffs: a front desk and three desks
DESKS = {
    "Policy desk": ("Answers questions about Northbridge's purchase policy, with the section cited.",
                    ["search_policy"]),
    "Purchasing desk": ("Buys things: stock checks, suppliers, purchase requests and orders, release.",
                        ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy",
                         "create_purchase_request", "create_purchase_order", "release_purchase_order", "order_status",
                         "send_message"]),
    "Stores desk": ("Records goods that arrived at the stores against an order.",
                    ["order_status", "receive_goods"]),
}


def desks(system: str, mcp_url: str, base_url: str, model: str):
    """Returns (front_desk, [mcp servers]). The front desk has no tools: it only hands off."""
    llm = OpenAIChatCompletionsModel(model=model, openai_client=AsyncOpenAI(
        base_url=base_url, api_key=os.environ.get("OPENROUTER_API_KEY", "replay")))
    servers, team = [], []
    for name, (job, tools) in DESKS.items():
        srv = MCPServerStreamableHttp(params={"url": mcp_url, "timeout": 60}, name=f"ledgerline-{name.split()[0].lower()}",
                                      cache_tools_list=True, client_session_timeout_seconds=60,
                                      tool_filter=create_static_tool_filter(allowed_tool_names=tools))
        servers.append(srv)
        team.append(Agent(name=name, handoff_description=job, instructions=system + f"\n\nYou are the {name}: {job}",
                          model=llm, mcp_servers=[srv], model_settings=ModelSettings(temperature=0)))
    front = Agent(name="Front desk", model=llm, handoffs=team, input_guardrails=[no_self_approval],
                  model_settings=ModelSettings(temperature=0),
                  instructions=("You are Ask Northbridge's front desk at Northbridge Cycles. Do not answer yourself: hand the "
                                "message to the one desk whose job it is."))
    for d in team:                      # a desk can pass a message that is not its job back to the front desk
        d.handoffs = [front]
        d.input_guardrails = [no_self_approval]
    return front, servers


async def ask_desks(start, session, text: str, group: str, max_turns: int = 12) -> dict:
    """One message through the desks, starting at `start` (the front desk, or whichever desk answered last: a
    handoff changes who owns the conversation). Returns who answered, the reply, and the agent to start from next."""
    try:
        r = await Runner.run(start, text, session=session, max_turns=max_turns,
                             run_config=RunConfig(workflow_name="Ask Northbridge desks", group_id=group))
        return {"reply": str(r.final_output or ""), "answered_by": r.last_agent.name, "guardrail": None,
                "next": r.last_agent}
    except InputGuardrailTripwireTriggered as e:
        return {"reply": "(stopped by the input guardrail: Ask Northbridge cannot approve or skip an approval)",
                "answered_by": None, "guardrail": e.guardrail_result.output.output_info, "next": start}
    except MaxTurnsExceeded:
        return {"reply": f"(stopped after {max_turns} steps)", "answered_by": None, "guardrail": None, "next": start}


def adk_desks(system: str, mcp_url: str, base_url: str, model: str):
    """The same three desks as ADK sub-agents. ADK gives the front agent a transfer_to_agent tool."""
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import Runner as ADKRunner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
    from google.genai import types
    llm = LiteLlm(model="openai/" + model, api_base=base_url, api_key=os.environ.get("OPENROUTER_API_KEY", "replay"))
    cfg = types.GenerateContentConfig(temperature=0)
    team = []
    for name, (job, tools) in DESKS.items():
        ts = McpToolset(connection_params=StreamableHTTPConnectionParams(url=mcp_url, timeout=60), tool_filter=tools)
        sysmsg = system + f"\n\nYou are the {name}: {job}"
        team.append(LlmAgent(name=name.lower().replace(" ", "_"), description=job, model=llm,
                             instruction=lambda ctx, s=sysmsg: s, tools=[ts], generate_content_config=cfg))
    front = LlmAgent(name="front_desk", model=llm, sub_agents=team, generate_content_config=cfg,
                     instruction=lambda ctx: ("You are Ask Northbridge's front desk at Northbridge Cycles. Do not answer "
                                              "yourself: transfer the message to the one desk whose job it is."))
    return ADKRunner(app_name="northbridge", agent=front, session_service=InMemorySessionService())
