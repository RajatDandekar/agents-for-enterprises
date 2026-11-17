# A6 · Trust one agent of yours: trace it, evaluate it, guard it, gate it

Lecture 6 · Evals, Guardrails and Observability · due before Lecture 8 (Sat 28 Nov 2026) · **100 points**

Take an agent you built in this course (your A4 or A5 agent, or Ask Northbridge from NB6 if you have none) and do for it
what we did for Ask Northbridge today. Work from NB6 (`NB6_evals_guardrails_observability.ipynb`): every piece you need is
there, built step by step, with our recorded runs as a working example.

Hand in one notebook (or repository) with the code, the outputs it produced, and a short write-up (one page, plain words)
answering the questions in each part. Use any model you have a key for; if you have none, use the recorded runs in NB6 and
say so. Never paste a key into the notebook.

## Part 1 · Trace it (25 points)
1. (10) Instrument your agent with OpenTelemetry: one `invoke_agent` span per turn, a `chat` span per model call, an
   `execute_tool` span per tool call, with the GenAI attribute names (`gen_ai.operation.name`, `gen_ai.request.model`,
   `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, …). Build it by hand first (the 20-line tracer), then with the SDK.
2. (8) Send the spans to Langfuse (free Hobby project) or Phoenix (local, no account). Include one screenshot of a trace.
3. (7) Find one failure, or one odd behaviour, in a trace. Show the span that explains it and say in three sentences what
   happened and why. Say what you put in the spans and what you kept out (content, personal data).

## Part 2 · Evaluate it (30 points)
1. (8) Error analysis: run your agent on 20 realistic inputs, read every trace, write a one-line note per failure, then group
   the notes into 3–6 categories with counts. Say for each category who was wrong: the agent, the eval, a tool, the
   infrastructure.
2. (10) Write 10 tasks. Each has an input in a known starting state and at least one **code** check (an outcome check on
   the state, or a trajectory check on the tool calls); at least four also have a **judge** criterion (binary, specific,
   with evidence). Run them; report pass/fail per task with the reason.
3. (6) Run each task 3 times. Report pass^1, pass^3 and pass@3, and name the flaky tasks.
4. (6) Label 20 replies yourself (right or wrong against the criterion). Run your judge on them. Report agreement and
   Cohen's kappa, and one change that improved the judge (or why you could not improve it).

## Part 3 · Guard it (30 points)
1. (12) Two deterministic guards at the tool boundary, in code, for the two actions your agent must never take wrongly (for
   example "a write needs a preview and a recorded yes", "only the named approver may approve", "no message to an outside
   address"). Each refusal returns a reason and a next step, and appears as a span in the trace.
2. (8) One model-based guard (an injection classifier, Presidio, NeMo Guardrails, or your own LLM check) where outside text
   comes in.
3. (10) A labelled set: 10 attacks and 10 ordinary inputs (at least 3 of them ordinary but tricky, with words like
   "ignore" or "override"). Report for your guards: catch rate, false alarms, median latency added, cost per check. Report
   the attack success rate with guards off and on. Map your attacks to OWASP codes (Agentic 2026 or LLM 2026).

## Part 4 · Gate it (15 points)
1. (10) A CI gate: a pytest file (DeepEval or plain asserts) that runs your most important tasks k ≥ 2 times with code
   checks only, and a GitHub Actions workflow that runs it on every change to your prompt or tools. You may run the same
   command locally instead of on GitHub; show its output.
2. (5) Make a deliberately bad change to your system prompt (like our Thursday edit). Show the gate failing on it and passing
   on the good prompt.

## How it is marked
- Each part: does it run, is it measured (not described), is the reasoning honest. A small, real, measured result beats a
  big claimed one.
- Your own bugs count in your favour when you find them and say so: our own suite was wrong more often than our agent on
  the first run.
- Copying our Ask Northbridge results is not allowed; using our code as a starting point is encouraged (cite it).
