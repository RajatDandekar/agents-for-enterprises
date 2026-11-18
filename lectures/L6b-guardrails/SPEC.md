# Lecture 7 · Guardrails and Red-Teaming · build spec (17 Nov 2026)

Sun 22 Nov 2026 · Lecture 7 of 11 · Dr. Rajat Dandekar, Vizuara. Folder: `lectures/L6b-guardrails/` (name kept; the hub
already points here). World: Northbridge Cycles on Ledgerline (`WORLD_V4.md`). Coordinator: the main session; three builders
work in parallel (A notebooks and experiments, B deck, C Argus), each on its own files (see "Who owns what").

## Why a rebuild
The 38 slides parked here are the 16 Nov guardrails section, unreviewed. Rajat's review of Lecture 6
(`../L6-evals-guardrails-observability/REVIEW_16NOV.md`) says what he wants from this kind of lecture. Apply all of it here
before he has to ask again:
1. **Demo first.** After Henrik's question, Rajat types into the live chatbot and the class watches what happens. The theory
   is then explained from what they just saw.
2. **Plain words, one idea per slide, with an example.** No slide whose point is a block of code (16 Nov slides 77, 81, 82,
   84 are code-heavy). Code lives in the notebooks. Every number on a slide is explained on that slide.
3. **Everything shown is something the class does with him**: an Argus station, or a Colab notebook with an "Open in Colab"
   link and a rendered copy embedded in the deck (`nbframe`, as in Lecture 6).
4. **Real tools, on our own data**, the ones teams use in production. Nothing truncated, nothing empty, nothing unexplained.
5. **What they came to learn is built from scratch in class** (in Lecture 6: multi-turn evals). Here: a guard written by
   hand at the tool boundary, and a red team written by hand (an attacker model, a success check in code).

## The story
Yesterday (Lecture 6) the class saw Friday's incident in a trace and failed Thursday's prompt edit with an eval. Henrik's
third question is still open: **"What stops it doing what it must never do?"** Today's answer in one sentence: *the model
decides what to try; code decides what is allowed; and we attack it ourselves before anyone else does.*

## Shape (target 85 to 100 slides, about the length of Lecture 6)
**Opener (demo first).** Title with the presenter's pre-class note · where we are (yesterday: see it, measure it; today:
bound it) · Henrik's third question · **Demo 1, live in Argus's chat**: the Thursday prompt, "Order the usual, please, needed
by 4 Dec 2026." → saved without a yes (10 of 10 in `incident_r3.json`). Switch the guards on, new chat, the same message →
the commit is refused at the tool boundary, the trace shows the guard's span, the agent shows the preview and asks. "Yes, go
ahead." → the commit passes. · "What just happened", from that trace · today's map.

**Part 1 · Guards in code.** What a guard is (code between the model and the tool; it reads Ledgerline and the
conversation's own record, never the model's words; a refusal returns a reason and a next step; it is a span in the trace)
· the four places a guard can stand, on the demo's trace · words vs actions (the model said no 19 times in 20 with the good
prompt; one prompt edit made it 3 in 20; with the code guards 0 in 20 under both) · the six code guards, each as one plain
example from the attack library (who is acting: identity and approvals; confirm needs a recorded yes; limits; never-events;
provenance) · the bug our own guard had (it refused Emma's real yes; one word fixed it): a guard needs tests too ·
**NB7a together** · the same idea in the frameworks teams use (Claude Agent SDK PreToolUse hook, LangChain middleware,
OpenAI Agents SDK guardrails: one table, names and where they sit, no code) · **Argus, your turn 1**.

**Part 2 · Text from outside, and model-based guards.** **Demo 2**: the poisoned invoice (an instruction inside a tool
result) · direct vs indirect injection in plain words · what code can do about outside text (wrap it as data; after reading
it nothing leaves and nothing commits without Emma) · what a model-based guard is, and when one is needed (what no rule
names) · an injection classifier, measured · personal data with Presidio (the card number typed in chat, where it ends up)
· an LLM check (a second model asked one question), measured · a guard framework: NeMo Guardrails, measured · **measuring a
guard: four numbers** (caught, false alarms, time added, cost per check), one table for all four detectors · what guards add
to a turn · guarding the reply (numbers must come from Ledgerline) · **NB7b and NB7c together**.

**Part 3 · Red-teaming.** What a red team is · the two OWASP lists (2026), simplified, mapped to our attacks · our attack
library: an attack is a message plus a success check in code · attack success rate, guards off and on · which guard stopped
what · an attack that worked (base64, Thursday prompt) · **a red team from scratch**: an attacker model rewrites a seed
attack, the agent answers, code decides · the tools teams use: promptfoo (our recorded run), and the Python tool run in the
notebook (DeepTeam if it works with Claude through our gateway, else garak), PyRIT named · **NB7d together** · **Argus,
your turn 2 and the class wall** · the landscape, Nov 2026, and "check before you adopt".

**Close.** Friday again with all three layers on · the same incident caught three ways (trace, eval, guard) · what can still
go wrong · Henrik's three answers · assignment A7 · next: Lecture 8, Agent Frameworks in Industry, Sat 28 Nov 2026.

## Notebooks (four, each live through the Argus gateway or in replay with no key, like NB6a to NB6d)
| File | Minutes | What the class does |
|---|---|---|
| `NB7a_guards.py/.ipynb` | 25 | The incident with no guard. Write the "confirm needs a recorded yes" guard by hand (about 15 lines) and plug it in at the tool boundary: refused, then allowed after the yes. Meet the bug (the guard that refused a real yes) and fix it. Add "who is acting". Run a few attacks with guards off and on; read the full 20 × 2 table from the recorded run. See the guard as a span. |
| `NB7b_detectors.py/.ipynb` | 25 | Three model-based guards on one labelled set (attacks and ordinary messages, some ordinary but tricky): an injection classifier (ProtectAI DeBERTa v3 prompt-injection-v2, runs on the Colab CPU, no key), Presidio for personal data (no key), and an LLM check with Claude Haiku written by hand. The four numbers for each. The poisoned invoice against all three. |
| `NB7c_nemo_guardrails.py/.ipynb` | 15 to 20 | NeMo Guardrails with Claude: a config in YAML, an input rail and an output rail, the same labelled set, the four numbers; one turn of Ask Northbridge behind the input rail. |
| `NB7d_red_team.py/.ipynb` | 25 to 30 | An attack as data plus a check in code. Attack success rate off and on. A red team from scratch (an attacker model, like the simulated Emma of NB6c). Then the tool. |
Rules: `BUILD.md` §0 and §3 as updated by Lecture 6's practice (`nbkit`, `nb_run.py`, the `clean` image, `NB_RECORD=1`
to record). A student's live run of one notebook should cost well under US$1 of their Argus budget: live cells run a few
cases, the full tables come from the recorded run. Cells that need no model (the classifier, Presidio, every code guard on
recorded tool calls) run for real in both modes.

## Argus (builder C)
- Chat (Traces station): when the guards flag is on, a "Guards" switch beside the prompt picker. On: the chat's agent runs
  with the code guards (`DETERMINISTIC` + `output_check`); a new chat starts when it is flipped. With the flag off nothing
  changes, for anyone (Lecture 6 on Sat 21 Nov uses Argus as it is).
- Guards station: a prompt picker (good, Thursday), and "A00 · Friday's incident" at the top of the attack list.
- No deploy by a builder: C stops at "ready to deploy" with the diff and the tests; the coordinator deploys and then asks C
  for the screenshots.

## Interfaces between builders
- Logs: `experiments/logs/` in this folder (new) for everything measured from today; the 16 Nov logs stay in
  `../L6-evals-guardrails-observability/experiments/logs/` and are read from there. Each new log is described in
  `experiments/logs/README.md` (file, what produced it, its keys) the moment it exists.
- Rendered notebooks: `nb/<name>.html` (+ `.live.txt`, `.replay.txt`), as in Lecture 6.
- Screenshots: `figs/argus/`, `figs/<tool>/`. `gen_figdata.py` lists the files that exist; a missing one shows a marked plate.
- Spend: each builder writes `experiments/logs/spend_parts/<builder>_<what>.json` (`{"what","usd","calls"}`).

## Who owns what
| Builder | May edit |
|---|---|
| A | `NB7*.py/.ipynb`, `nb/`, `experiments/` (scripts and logs), new or additive code under `ledgerline/ledgerline/course/l6/` (keep everything Lecture 6's notebooks import working) |
| B | `build/`, `index.html`, the deck's css and figure js, `gen_figdata.py`, `figdata.js`, `NOTES.md`, `A7.md`, `figs/` (figures it makes), `qa/` |
| C | `ledgerline/ledgerline/argus/`, `figs/argus/` (screenshots), `experiments/argus_*.py` |
Nobody edits: other lectures, `engine/`, `tools/`, `llm.py`, `toolbox/`, `hermes/`, `deploy/`, the hub `index.html`.
Anything needed there goes in the final report.

## Hard rules (all builders)
- No local compute: nothing is installed or served on the laptop; Modal only (`MODAL_PROFILE=rajatworkspace`,
  `tools/mrun.sh`). Locally: stdlib Python, `node --check`.
- Never print, log or commit a key. Never commit, push, publish or deploy anything. Never purge or delete Argus students.
- Do not use the browser pane or the user's Chrome.
- `tools/nbbuild.py` and `tools/world_v4.py` write on any call: never run them with `--help`; `world_v4.py` only with `--check`.
- Every number on a slide comes from a log; a number not yet measured is a marked plate, never a guess.
- No client names, no real ERP vendor. Plain words; no "revolutionary, seamless, unlock, delve, leverage".
- Model spend caps: A US$12, C US$2, B US$0 (Modal compute for QA only). If the model account answers "credit balance is
  too low", stop model work, finish what needs no model, and say so.
