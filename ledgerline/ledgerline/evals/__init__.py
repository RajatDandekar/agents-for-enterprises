"""Lecture 6 · The Inspector: job 9 of the form, being tested before release.

    suite.py      60 cases derived from route_spec (gate combinations, variants, never-events, asks, answers)
    simulator.py  a simulated Emma who leaves things out: scripted (deterministic) or a model persona (cassette L6_sim)
    runner.py     run a case / a suite; summarise (pass rate with a 95% interval, £ per resolved order, p95 seconds)
    metrics.py    code metrics first: asked for the missing field, no needless question, no forbidden tool,
                  no duplicate write, right final status, right clause, never-events NE1–NE5
    judge.py      a model judge for tone only (checked against 30 course-team labels in labels/tone_30.json)
    broken.py     ten deliberately broken bots, to test the tests
    trace.py      per-step traces: a local JSON-lines store, and export to Langfuse with read-back (when keys are set)
    versions.py   fingerprints of prompts, tools (TOOLSET_VERSION), models, route and suite
    gate.py       the regression gate:  python -m ledgerline.evals.gate --agent graph --baseline <file>
    scorecard.py  the trust scorecard
    module.py     the same suite machinery for a capstone module (A6)
"""
EVALS_VERSION = "1.0"
