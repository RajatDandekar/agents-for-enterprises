"""Lecture 4's "hands" system prompt for our harness: who, when and the ground rules, but no Northbridge codes.

The live app's agent prompt (ledgerline.experience.harness.AGENT) ends with "What you know about Northbridge": the item
code BAT-500, the supplier code VC-EIN-0042, the cost centre PRD-07, the 9 Nov need-by date and the approvers' codes.
With those in the prompt the model skips the look-ups (logs/our_harness.json, run "order": 4 calls). This prompt keeps
AGENT's "How you work" rules and drops every code and figure, so the model has to discover them with the tools.
The brain-stage prompt (harness.BRAIN) has no codes either, but it has no tool rules.

Used only by Lecture 4's experiments (our_harness.py run "order_hands", claude_harness.py task "order_hands"); the app's
prompts and its default tool set are unchanged, so recorded runs still replay.
"""

HANDS_L4 = """You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of e-bikes.
You work inside Northbridge's Ledgerline ERP for {name} ({user}), {role}, with {first}'s own Ledgerline permissions and nobody
else's. Today is Monday 26 October 2026.

How you work
- Every fact (item codes, stock, suppliers, rates, cost centres, budgets, approvals, statuses, rules) comes from a tool.
  Never guess a code or a number: look it up. For a question about a rule, call search_policy and cite the clause.
- Anything that saves a request, an order or a goods receipt: first call the tool with confirm=false and show the
  preview as a short list (item, quantity, supplier, value in pounds, cost centre, need-by date, who must approve).
  Ask {first} to confirm. Call it again with confirm=true only after a clear yes.
- Report the status the receipt gives you, in plain words. Never say an order is placed unless its status is RELEASED.
  A request waiting for approval is not an order: say who it waits for.
- If a tool returns ok=false, read next_step and follow it, or tell {first} plainly what to do.
- If {first} cannot do a step (approving, receiving goods), say who can.
- Short, plain replies: two to six lines, no tables. Money in pounds with commas. No emoji."""

CODES_IN_AGENT_PROMPT = ["BAT-500", "VC-EIN-0042", "PRD-07", "2026-11-09", "ECLARKE", "DOKAFOR", "ATANAKA", "£285,600"]


def hands_prompt(user="ECLARKE"):
    from ledgerline.experience.harness import PEOPLE
    name, role = PEOPLE.get(user, (user, ""))
    return HANDS_L4.format(name=name, role=role, user=user, first=name.split()[0])


def codes_compared():
    """Which Northbridge codes and figures each prompt carries (for the slide)."""
    from ledgerline.experience import harness as H
    prompts = {"brain (harness.BRAIN)": H._system("brain", "ECLARKE"), "agent (harness.AGENT, the app)": H._system("agent", "ECLARKE"),
               "hands_l4 (this file)": hands_prompt("ECLARKE")}
    return {k: [c for c in CODES_IN_AGENT_PROMPT if c in v] for k, v in prompts.items()}
