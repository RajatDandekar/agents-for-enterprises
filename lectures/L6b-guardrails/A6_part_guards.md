# Parked from A6 (16 Nov 2026): the guardrails part

Moved out of Lecture 6's assignment on 16 Nov 2026, when Lecture 6 became "Observability and Evals". It was Part 3 of four,
worth 30 of 100 points. Use it as the core of Lecture 7's assignment (Guardrails and Red-Teaming, Sun 22 Nov 2026).

## Part 3 · Guard it (30 points)
1. (12) Two deterministic guards at the tool boundary, in code, for the two actions your agent must never take wrongly (for
   example "a write needs a preview and a recorded yes", "only the named approver may approve", "no message to an outside
   address"). Each refusal returns a reason and a next step, and appears as a span in the trace.
2. (8) One model-based guard (an injection classifier, Presidio, NeMo Guardrails, or your own LLM check) where outside text
   comes in.
3. (10) A labelled set: 10 attacks and 10 ordinary inputs (at least 3 of them ordinary but tricky, with words like
   "ignore" or "override"). Report for your guards: catch rate, false alarms, median latency added, cost per check. Report
   the attack success rate with guards off and on. Map your attacks to OWASP codes (Agentic 2026 or LLM 2026).
