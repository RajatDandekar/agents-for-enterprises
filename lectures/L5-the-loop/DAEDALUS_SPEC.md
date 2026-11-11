# Daedalus: the Lecture 5 workshop (spec, 11 Nov 2026)

The shared contract between the app (`ledgerline/ledgerline/daedalus/`, deploy `deploy/daedalus_modal.py`) and the deck
(`lectures/L5-the-loop/`). Patterns are copied from Hephaestus (Lecture 4); Hephaestus itself is not touched.

## The app
- Modal app `northbridge-daedalus`, URL `https://rajatworkspace--northbridge-daedalus.us-east.modal.run`, one CPU web
  container (`@modal.concurrent`, `max_containers=1`, `min_containers=0`), sandboxes in memory, durable state in the
  `modal.Dict` `northbridge-daedalus-state`, keys from the existing Modal secret `rasoi-experience` (GEMINI_API_KEY,
  NORTHBRIDGE_ADMIN_TOKEN). Model: gemini-3.8-flash direct (reasoning low), fallback gemini-3.5-flash-lite.
- Safety rails as Hephaestus: an instructor pause, a class US$/day cap and a per-student cap, rate limits, a cap on model
  calls in flight, `purge-tests` / `purge-all`, `warm` / `cool` (and a 04:00 UTC cron back to 0), `/admin`, `/wall`.
- A student types a name and gets **their workshop**: a secret key (`dx-…`), their own Ledgerline sandbox (Mon 26 Oct
  2026, 09:00; Emma Clarke, ECLARKE), their own agent settings and their own workflow.

## Tabs
1. **The Loop.** Emma's order (or any message). **Next step** runs one turn of the loop: one model call, then the tools
   it asked for. Each step shows what the model wrote (its thought, if any), the calls with arguments, each result as
   the model reads it, the tokens and seconds, and the harness's own lines (step n of max, tokens of budget, a pause, a
   stop). **Run to the end** runs the rest. **Daniel's inbox** (a drawer, on every tab): sign as Daniel. **Next
   morning** saves the agent's state as JSON, throws the agent away, and loads a new one from the JSON.
2. **Your agent (the harness).** The knobs, each with presets and a plain line: max steps (2 / 4 / 12 / 25), token
   budget per message (6,000 / 60,000 / none), tools switched on (2 / the shipped 11 / all 16, or one by one), the system
   prompt (bare / Ask Northbridge's / your own), the approval pause (on / off), error recovery (on / off). **Run the six
   jobs**, a scorecard (right / wrong / no answer, why, model calls, tool calls, tokens, seconds, cost), and **Your runs**
   with settings beside results.
3. **Your workflow (the labyrinth).** Emma's job as blocks, in order: read the request (the one model step), find the
   item, check stock, find the supplier, check the certificate, check the budget, raise the request, wait for approval,
   create the order, release it, tell Emma. Remove, add, move up or down; options per block (a gate's "stop" or "use the
   preferred supplier", retries, on error). **Run** on any of the six jobs or your own words, step by step; a waiting run
   is shown as the saved document it is; sign as Daniel and **Resume**. **Flaky Ledgerline** makes the next save lose
   its reply once, so retries and idempotency show.
4. **The race.** Your workflow and your agent on the same six jobs, each in a fresh sandbox, Daniel signing whatever
   waits. Scored in code from Ledgerline's tables. Per job and in total: right, model calls, tokens, seconds, cost, and
   for the agent run three times: did it take the same path every time?
5. **The class wall** (`/wall`): per student: agent settings changed, best agent score, workflow blocks, race result
   workflow vs agent, waiting runs resumed.

## The six jobs (`daedalus/jobs.json`; one message from Emma each)
1. `spring` Order 2,000 BAT-500 from Voltway on PRD-07 by 9 Nov 2026 → PR waits for Daniel; after his yes, a released
   PO with VC-EIN-0042.
2. `bells` Reorder 10,000 BEL-STD-01 from Pennine Brakes on PRD-07 by 16 Nov 2026 → within Emma's limit: approved at
   once, a released PO with PB-MAN-0017.
3. `nordic` Order 2,000 BAT-500 from Nordic Cell Co. → nothing ordered from Nordic (UN 38.3 expired 30 Sep 2026).
   Ledgerline itself accepts and releases such an order (`experiments/logs/chain_probe.json`): only a gate stops it.
4. `closed` Order 1,000 BAT-500 from Voltway on PRD-05 → nothing saved (PRD-05 closed on 15 Oct).
5. `fallback` Nordic is the cheapest: can we use them? If not, use a certified supplier → a request for 2,000 BAT-500
   on PRD-07, and after Daniel a released PO with a certified supplier.
6. `question` Which suppliers may supply BAT-500 battery packs, and at what price? → names Voltway at £119.00, says
   Nordic may not; nothing saved.

## Measured, not claimed
Every knob and every workflow change on a slide is measured on the deployed app first
(`lectures/L5-the-loop/experiments/logs/daedalus_*.json`), with repeats. Screen recordings and screenshots for the deck
are made with Playwright on Modal against the live URL.
