# Lecture 5 v5: The Loop. Agents, harnesses and workflows (Lectures 5 and 6 merged)

Dr. Rajat Dandekar's brief (11 Nov 2026), summarised: combine Lecture 5 (The Loop) and Lecture 6 (The Studio) into one
lecture. Drop the "control graph" (LangGraph) framing. Same depth and story-telling as Lectures 3 and 4; an in-class
experience where every student tries things on their own, at the level of the tools lecture (Hephaestus).

**Class:** Sat 14 Nov 2026, 7–9 AM IST (the old L5 slot; the L6 slot is freed). **World:** Northbridge (`WORLD_V4.md`).
**Never:** client names, names or money from outside the Northbridge world, invented numbers. Every number on a slide comes from a run in
`experiments/logs/` or from the deployed playground's own measurements.

## The one idea
An agent is a model in a loop: it thinks, calls a tool, reads the result, and decides the next step, until the job is
done or it needs a person. The **harness** is the code that runs that loop and keeps it safe: when to stop, how much it
may spend, which tools it may touch, what to do when a call fails, how to wait for a person and carry on the next day.
A **workflow** is the other way to do a job: the steps are written down in advance and the code follows them. When you
know the order, write it down. When you do not, let the model choose. Most real systems use both.

## The story (one running example)
- **Where Lecture 4 left us.** Emma typed one sentence: *"Order 2,000 BAT-500 packs from Voltway for the spring launch
  run."* Ask Northbridge made 11 tool calls on our harness, and the request PR/2026/04417 went to Daniel. One message,
  many calls, chosen by the model, in a loop nobody saw. Today we open that loop.
- **What makes it an agent (Section 1).** Teach from the extremes: a chatbot that makes one round of tool calls and
  stops (Lecture 4's `hands` stage: Emma drives every next step) versus a free loop (the model drives). Who picks the
  next step: the person, the code, or the model. The same order measured both ways.
- **The loop, step by step (Section 2).** ReAct (reason, then act): Thought → Action → Observation, written out as text,
  parsed by our code; then the same loop with native tool calls. Emma's order replayed step by step from a real run:
  each step's thought, call, result and tokens. The loop ends when the model answers in words.
- **The harness (Section 3).** The parts around the loop, each with a real measurement on Emma's job: the system
  prompt, the message history, the tool list, the stop rules (step limit, token budget, failures in a row), error
  recovery (follow next_step, never repeat a failed call), **the approval as a pause** (PR/2026/04417 waits for
  Daniel: the loop stops and saves its state), and **state across days** (the next morning the job resumes only when
  Ledgerline says APPROVED, whatever the chat says).
- **Daedalus, part 1 (live, Section 4).** Every student gets their own workshop: a Ledgerline sandbox as Emma, and
  the agent's harness, theirs to change. Watch the loop step by step on Emma's order; turn one knob at a time (max
  steps, budget, tools, system prompt, the approval pause, error recovery) and see the measured effect on the six jobs.
- **Workflows and agents (Section 5).** Teach from the extremes again: every step written down (a workflow) versus
  every step chosen by the model (an agent). The parts of a workflow, in plain words: a trigger, steps, gates (a
  branch that stops or switches), the approval step (a waiting run is a saved document), error paths and retries,
  and running it twice safely (idempotency). Emma's order both ways, measured: cost, time, the same path every time,
  and what each gets wrong. When to use which, and the middle (a workflow with one model step; an agent that can call a
  workflow as one tool).
- **Daedalus, part 2 (live, Section 6): build your own.** Each student builds a small workflow for Emma's job from
  blocks (read the request, find the item, check the certificate, check the budget, raise the request, wait for
  Daniel, create and release the order), runs it, watches it wait, signs as Daniel and sees it resume. Then they shape
  an agent for the same job, and **race** the two on the same six jobs. The class wall shows everyone's race.
- **NB5 and A5 (Section 7).** The notebook rebuilds the loop, the harness and a workflow in plain Python on recorded
  replies (no key). The assignment: your own module's job as a workflow and as an agent, raced on your own jobs.
- **Next:** Trust (identity, approvals done properly, evals, traces, recovery and deployment).

## Why Daedalus
Daedalus, the craftsman of Greek myth, built two things: the labyrinth, where every path is fixed, and the wings, which
fly wherever you steer them. His son Icarus ignored the limits and flew too close to the sun. A workflow is the
labyrinth, an agent is the wings, and the harness is the set of limits Icarus did not keep.

## Sections and rhythm
Part slide → teach from the extremes (one idea per slide, every term defined on first use, builds with `.step`
clicks) → "Ask the class" → the film (where there is one) → 1–3 checks with answers on click.

| # | Section | Live? | Film slot |
|---|---|---|---|
| 0 | Opener: where we are, the 11 calls, today's question, the map | | |
| 1 | What makes it an agent? | | |
| 2 | The loop, step by step (ReAct, then native tool calls) | | `loop` |
| 3 | The harness (prompt, history, tools, stops, budget, recovery, pause, state across days) | | `harness` |
| 4 | Daedalus, part 1: watch the loop, turn the knobs | live | |
| 5 | Workflows and agents (steps, gates, the approval step, retries, idempotency; when to use which) | | `workflow` |
| 6 | Daedalus, part 2: build a workflow and an agent, race them, the class wall | live | |
| 7 | NB5, A5, next lecture | | |

## What is cut, and why
- The LangGraph "control graph" and "spine and gates" as a headline: gone (Rajat: "not sure we need that"). The idea
  survives in plain words as a workflow (steps and branches). LangGraph appears in the framework lecture (L8).
- The Studio's canvas, node ports and template syntax: not taught. Students build workflows from blocks in Daedalus.
- Deep evals, identity and recovery drills: Lecture 7 (Trust).
