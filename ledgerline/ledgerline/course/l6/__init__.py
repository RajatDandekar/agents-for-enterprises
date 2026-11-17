"""Lecture 6 · Evals, Guardrails and Observability: Lecture 5's complete Ask Northbridge, watched, graded and guarded.

    from ledgerline.course.l6.agent import Agent, PROMPTS        # the agent under test (Hermes's Finale, unchanged)
    from ledgerline.course.l6.tracing import Tracing             # OpenTelemetry spans, GenAI conventions -> Langfuse, Phoenix
    from ledgerline.course.l6.minitrace import MiniTracer        # a tracer in twenty lines, before OpenTelemetry
    from ledgerline.course.l6.guards import Guards, GUARDS       # deterministic guards at the tool boundary + model-based
    from ledgerline.course.l6.suite import TASKS, run_task       # the class suite: outcome, trajectory and words checks
    from ledgerline.course.l6.judges import judge                # Claude as the judge (words only)
    from ledgerline.course.l6.attacks import ATTACKS             # the attack library (Argus station 3, promptfoo, the wall)

Nothing here changes how Ask Northbridge behaves when every guard is off: the same prompt, the same 26 tools, the same
memory (the class's recorded OpenClaw-like week), the same model Hermes runs (claude-sonnet-5-5).
"""
