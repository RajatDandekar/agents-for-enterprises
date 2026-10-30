"""Lecture 7, Trust: taking Ask Northbridge to production.

    from ledgerline.course.l7 import AskNorthbridge, TrustLayer, make_agent
    agent = AskNorthbridge(erp, "ECLARKE", llm=LLM(..., cassette="L7v3_nb"), trust=True)        # Emma's own session
    agent = AskNorthbridge(erp, "ECLARKE", llm=..., identity="service_account")                  # what IT proposed
    agent.respond("Reorder 20,000 of the city e-bike battery packs ...")
    agent.trace                                                                           # every step, readable

The pieces, in the order the lecture teaches them:
  identity     the toolbox's MCP server is bound to a Ledgerline session: the user's own (passthrough) or SVC_AGENT
  approvals    approve tools only for the named approver, in the approver's own session
  guard        never-events NE1-NE5 refused in code, before the write reaches Ledgerline
  read-back    after every write, ask Ledgerline what it really holds; the reply gate (NE5) checks the last message
  trace        one row per step: user turn, model call, tool call, guard decision, reply
  recovery     retry.py: what a lost reply does without and with an idempotency key
"""
from .agent import PROMPTS, SYSTEM, AskNorthbridge, make_agent  # noqa: F401
from .trust import SERVICE_ACCOUNTS, TrustLayer  # noqa: F401
