"""Lecture 5, The Loop: what makes it an agent.

    react.py     ReActAgent: the loop written out in text (Thought / Action / Action Input / Observation)
    harness.py   Harness: the native tool-calling loop, with the harness parts switched on one by one
    hands.py     OneRound: Lecture 4's Ask Rasoi (one tool round per message), for comparison
    graph.py     ControlGraph: a small LangGraph spine with gates, for when the process must be followed
    tasks.py     the Rasoi task set, the people who answer (Kavita, Rohit, Neha) and the code checks

Every agent has respond(text) -> str and an .llm (bahi.llm.LLM) for token totals, and acts through a
bahi.toolbox.Toolbox bound to one person's Bahi session.
"""
from .harness import Harness, PARTS, SYSTEM_BARE, SYSTEM_FULL  # noqa: F401
from .hands import OneRound  # noqa: F401
from .react import ReActAgent, parse_step  # noqa: F401
