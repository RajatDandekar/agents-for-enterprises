"""Ask Northbridge as a target for garak, the open-source LLM vulnerability scanner (Lecture 7, NB7d).

garak's "function" generator calls one Python function for every attack prompt and reads the reply:

    python -m garak --target_type function --target_name ledgerline.course.l6.garak_target#ask_northbridge --spec probes.promptinject.HijackLongPrompt

Each prompt gets a fresh Ledgerline sandbox and one turn of the real agent, through the Argus gateway. Settings come from
the environment, because garak starts this module in a process of its own:
    ARGUS_URL, ARGUS_KEY   the gateway and the join key (never printed, never written to the ledger)
    NB7_PROMPT             good | thursday          (default thursday)
    NB7_GUARDS             off | code               (default off)
    NB7_LEDGER             a .jsonl path: one line per prompt with the tool calls and what Ledgerline held afterwards,
                           so that our own code can check what garak's detectors cannot see
"""
from __future__ import annotations

import json
import os


def ask_northbridge(prompt: str, **kwargs) -> list[str]:
    from .nb7 import call_line, code_guards, holds, run_agent
    from .nbkit import Kit
    kit = Kit(os.environ["ARGUS_URL"], os.environ["ARGUS_KEY"])
    guards = code_guards() if os.environ.get("NB7_GUARDS", "off") == "code" else None
    run = run_agent(kit, os.environ.get("NB7_PROMPT", "thursday"), [str(prompt)], guards=guards)
    reply = run["turns"][0]["reply"]
    ledger = os.environ.get("NB7_LEDGER")
    if ledger:
        with open(ledger, "a") as f:
            f.write(json.dumps({"prompt": str(prompt), "reply": reply, "calls": [call_line(c) for c in run["turns"][0]["calls"]],
                                "holds": holds(run["saved"]), "usd": run["usd"]}, ensure_ascii=False) + "\n")
    return [reply]
