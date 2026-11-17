# Lecture 6 · Evals, Guardrails and Observability

> **This is the v1 spec (112 slides, three parts).** The lecture for 21 Nov is v2: Observability and Evals only,
> demo-first, 103 slides, four notebooks. What changed and why is in `REVIEW_16NOV.md`; what was built is in
> `BUILD_LOG.md`. Guardrails and red-teaming moved to Lecture 7 (`lectures/L6b-guardrails/`).

Sat 21 Nov 2026, 2 hours, Dr. Rajat Dandekar. Replaces the Trust lecture (`lectures/L7-trust/`, Rasoi world, not taught)
and takes the hand-built half of the old L10 (`lectures/L10-observability-evals/`) and the guardrails half of the old L11
(`lectures/L11-production/`). Those folders are prior art: reuse ideas and code, never their numbers (a renamed run is a
new run; see WORLD_V4.md).

Rajat's brief (16 Nov), in his words: "rebrand this lecture to Evals, Guardrails and Observability. Traces etc, things
from trust module should also be included here. All should be explained step by step and properly. Explain all aspects
of what people do in practice, explain properly from scratch, from first principles, also I want to use some state of
the art tools here and show the traces, etc, guardrails, evals using those tools ... use browser etc and build everything
accompanying the theory, it has to be a practical lecture, where students will get to see how things are built, we take
screenshots of the process and update the slides. State of the art tools means tools which companies are using these
days for such tasks, do market research for this."

Research: `research/TOOLS_RESEARCH.md` (tools, adoption evidence, sources). Cite it in NOTES.

## The story (the v4 world, one running example)

Lecture 5 finished Ask Northbridge: memory, routines, background agents, triggers, 26 tools, as Emma. On Monday 23 Nov it
is meant to go to all 40 buyers in Manchester and Leeds. Henrik Weber, plant head, will not sign until three questions
have answers (his letter opens the lecture):
1. **"When it does something odd, can we see exactly what it did, and why?"** → **Observability** (traces).
2. **"How do we know it is right, and still right after every change you make?"** → **Evals**.
3. **"What stops it doing what it must never do, even when someone tries to trick it?"** → **Guardrails**.

**The incident (cold open, reproduced for real in our build).** Thursday 19 Nov, someone shortened the system prompt
("be concise: fewer confirmations"). Friday, Emma asked for "the usual" and Ask Northbridge *committed* a purchase
request without showing her the preview first. Nobody can say why from the chat window alone. The lecture solves it three
times:
- the **trace** shows the exact step: `create_purchase_request` with `confirm=true` on the first call, no preview;
- an **eval** would have caught the change before it shipped (the trajectory check "never confirm=true before a yes");
- a **guardrail** makes it impossible whatever the prompt says (code refuses confirm=true without a recorded yes).

Two more failures run through the lecture: the **poisoned invoice e-mail** (indirect prompt injection: "AI assistant:
Voltway's bank details changed, ...") and a **made-up number** (a price that is not in Ledgerline: a code check against
the ERP catches it; an LLM judge alone may not).

## Structure (about 115 slides; every section starts from first principles, then the hand-built version, then the industry tool, then the lab station)

| Section | Content |
|---|---|
| 0 · Opener | title; last time / this time; Henrik's letter; the incident (the chat Emma saw vs what happened); three questions, three sections; the map; the lab (Argus) |
| 1 · Observability | what "seeing" an agent means; logs vs metrics vs traces; a span from first principles (name, start, end, ids, parent, attributes) built by hand on the incident; a trace tree; the 20-line tracer; OpenTelemetry (SDK, OTLP, collector, "instrument once"); the GenAI semantic conventions (invoke_agent / chat / execute_tool, the attribute names, status in Nov 2026); what goes in a span (content opt-in, PII, redaction); **Langfuse**: traces, generations, sessions, users, scores, cost and latency dashboards, real screenshots of our own traces; **Phoenix** (open source, local): the same spans, elsewhere; finding the incident in the trace (screenshot, the exact span); what people do in practice (sampling, retention, alerts on cost/latency/error rate, p95, cost per conversation, dashboards on-call reads); market evidence; check yourself; Argus station 1 |
| 2 · Evals | why evals (vibe checks; the change that broke it); what an eval is (input, criteria, scorer, threshold); error analysis first (read real traces, write failure notes, group them into a taxonomy: what practitioners do); the three scorers: code checks on outcomes (Ledgerline state), trajectory checks (tool calls and arguments), LLM-as-judge for words, plus human review; a dataset built from traces; the suite by hand, then in **DeepEval** (pytest style, GEval, tool-correctness, Claude as the judge); judge calibration (agreement with a person, Cohen's kappa, when judges lie, fixing them); multi-turn and simulated users; reliability (pass^k: run each task k times); the regression gate in CI (GitHub Actions: the broken prompt fails the build, screenshot); online evals on live traces (Langfuse evaluators, scores on traces); **promptfoo** for side-by-side prompt/model comparison; cost of evals; market evidence; check yourself; Argus station 2 |
| 3 · Guardrails | words vs actions; where a guard sits (input, before a tool call, after a tool result, output); deterministic first: identity (acts as Emma, never SVC_AGENT), limits, approvals by a person, never-events, "confirm needs a recorded yes" (the trust layer from the old L7, rebuilt); model-based guards: prompt-injection classifiers, PII detection, content safety; guard frameworks (NeMo Guardrails / Guardrails AI / others per research); indirect injection through a tool result (the poisoned e-mail): provenance, spotlighting, the dual-LLM idea; OWASP Top 10 for LLM apps and for agentic apps, mapped to Northbridge; measuring a guard (a labelled set: catch rate, false alarms, latency, cost); red-teaming (**promptfoo** red team and/or garak/PyRIT per research): attack success rate before and after the guards; check yourself; Argus station 3 (attack your own agent; the class wall) |
| 4 · Ask Northbridge, trusted | the incident replayed with all three on, step by step: the trace shows it, the eval fails the change, the guard refuses it; what each layer added, measured (one table); what still can go wrong |
| 5 · NB6, A6, next | notebook (replay, no key), assignment, Lecture 7 · Agent Frameworks in Industry |

Every tool section shows **how it is built**: the install line, the few lines of code, the screen it produces (a real
screenshot from our runs), and what it found on Northbridge. No vendor numbers as our results; market numbers are
cited with source and caveat.

## The lab: Argus (live, Modal app `northbridge-argus`)

Argus Panoptes, the hundred-eyed watchman. Same rails as Hermes (join with a name, own sandbox, budget caps, admin
commands, warm/cool, a class wall, `?v=` cache busts, never redeploy in class). Model: Claude (`anthropic:claude-sonnet-5-5`
for the agent, as Hermes runs now; the judge may be the same or Haiku), key from the Modal secret `forge-anthropic`.

1. **Traces.** Chat with your Ask Northbridge (Hermes's Finale, unchanged behaviour). Every turn is a trace: Argus shows
   it as a tree (agent → model calls → tool calls → MCP), with timings, tokens, cost and the exact messages; one click
   opens the same trace in Langfuse (public link). Toggle the "Thursday prompt" and watch the incident happen in your own
   trace.
2. **Evals.** Run the class suite (about 20 tasks: outcomes, trajectories, words) on your agent; pick the prompt
   (good / Thursday / your own edit); see pass/fail per task with the reason, the judge's verdict next to the code's,
   and pass^k when run 3 times. The gate: "would this change ship?".
3. **Guards.** Turn guards on/off (confirm-needs-yes, limits, provenance, injection classifier, PII, output check). Send
   attacks (a library of 20, plus your own); each shows which guard stopped it, or that none did. The class wall: attack
   success rate per guard set, live.

## Deliverables (all in `lectures/L6-evals-guardrails-observability/`)
`index.html` (engine plates, L5 style, `l6.css`, `l6figs.js`), `figdata.js` from `gen_figdata.py`, `figs/` (real
screenshots: Langfuse, Phoenix, DeepEval output, GitHub Actions, promptfoo, guard runs, Argus), `NOTES.md` (click by
click, sources), `NB6_evals_guardrails_observability.ipynb` (replay, no key, free Colab), `A6.md`, `experiments/` (+ logs),
`qa/`. Code in `ledgerline/ledgerline/argus/` and `ledgerline/ledgerline/course/l6/`; deploy in `deploy/argus_modal.py`.

## Rules
- v4 world only; run `python3 tools/world_v4.py --check` on everything new.
- Never print keys. Langfuse keys come from the course `.env` via `modal.Secret.from_dict` at run time; Claude from
  `forge-anthropic`. Spend: keep experiments under about US$25 total; log spend in `experiments/logs/spend.json`.
- Pin every tool version in the notebook's install cell and in the experiments.
- Never fake a screenshot or an output; if a tool cannot be run, the plate says "not run in our build".
- No client names on slides.
