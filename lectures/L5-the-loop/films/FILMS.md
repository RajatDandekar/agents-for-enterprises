# Lecture 5 films (The Loop): plan

Three narrated Blender Cycles films for Lecture 5, in the house style of `FILM_STYLE.md` and the same series as Lecture
4's films (`lectures/L4-the-hands/films/FILMS.md`). **Status: planned, not rendered.** The deck has a labelled slot for
each (slides 29, 49 and 82: `FIGS.film`, `data-name` = the base name); a slot plays the film as soon as
`films/<name>.mp4`, `.webm` and `.jpg` exist and `gen_figdata.py` is re-run (it lists the media that exist).

Every number and line of JSON on screen is read at build time from `../experiments/logs/` (no illustrative numbers).
Each film plays at the **end** of its section, after the theory, and never introduces a term the slides have not.

| Base name | Section | Target length | Data |
|---|---|---|---|
| `loop` | 2 · The loop | 2:00–2:30 | `logs/story.json` (day 1), `logs/react.json` |
| `harness` | 3 · The harness | 2:30–2:45 | `logs/story.json` (both days, the night), `logs/daedalus_knobs.json`, `logs/recover*.json` |
| `workflow` | 5 · Workflows and agents | 2:30–2:45 | `logs/race.json`, `logs/daedalus_knobs.json` (workflow), `logs/chain_probe.json` |

## How to build (reuse Lecture 4's pipeline; do not edit Lecture 4's files)
Copy `lectures/L4-the-hands/films/build/` to `lectures/L5-the-loop/films/build/` (kit, overlay, narrate, modal_films,
gen_sfx, tidy_cues, fetch_fonts), keep the L2/L4 "midnight slate" studio, the sealed model machine, the tool rack and
the trace strips, and add the props below in `build/kit/props_l5.py`. Narration: ElevenLabs Daniel
(`onwK4e9ZLuTAKqWW03F9`, `eleven_multilingual_v2`, speed 1.08; key from `/Users/raj/Claude_Brain/cobol-mainframes/.env`,
never printed). Music: a calm Epidemic Sound bed different from L1's track, 26 dB under the voice. Render on Modal
L40S (volume `video-ad-edit:/l5films`, app `l5-films`), 1920×1080, 30 fps; composite overlays, voice and music with
ffmpeg on Modal; style frames first (3–4 stills of the first film) and check them against the Rubin frames.

New props:
- **the loop ring**: a polished aluminium track around the model machine with four stations (think, check, act,
  observe); a glowing capsule travels the ring once per step; a counter plate shows "step n of 12";
- **the harness rig**: the L4 open rig, now with eight labelled modules that light one by one (prompt, history, tools,
  stops, max steps and budget, recovery, the pause, state);
- **the night vault**: a glass document case where the agent's state lands as a stack of JSON sheets
  (its height = the real 6,917 bytes at a fixed scale), then a new machine rebuilt from it;
- **the labyrinth**: eleven machined blocks on a rail (model step sky, tools white, gates amber, approval ember), with
  gates as drop-down barriers and the approval as a document tray;
- **the race board**: two lanes of six tiles (workflow, agent ×3), each tile green or ember with its real token count.

## 1 · `loop`: one turn at a time (end of Section 2)
**Shots.** The sealed model machine; Emma's order as a chat card. The capsule leaves the "think" station: the context
column beside it rises to 2,198 tokens (`story.day1[0].steps[0].tokens_in`). It reaches "check": tool calls, not words.
"Act": three capsules fly at once to `check_budget`, `supplier_certificates` and `create_purchase_request` (preview) on
the rack; three green results come back ("PRD-07 open · £1,190,000 left", "Voltway Cells: UN 38.3 valid", "preview ·
nothing saved · £273,600 · approver DOKAFOR"). "Observe": the results drop into the column. Second turn: 2,746 tokens,
words this time; the ring stops; the preview card appears for Emma. A side panel: the same step written as ReAct text
("Action: check_stock / Action Input: {...}") and the parser picking it apart; the note that this model wrote no
Thought line. Close on the smallest loop's `while True` and a dimming ring: "nothing here stops it".

**Script (draft).**
> Emma types one sentence. The model cannot act. It can only write. So the loop begins.
>
> Think: the model reads everything so far. Two thousand one hundred and ninety-eight tokens.
>
> It does not answer in words. It asks for three tools at once: the budget, the certificate, and a preview of the
> request. Our code runs all three, in Emma's own Ledgerline session, and the results go back in.
>
> Round again. Now it reads two thousand seven hundred and forty-six tokens: everything before, plus the three results.
> This time it answers in words: a preview, and a question for Emma.
>
> That is the whole loop. Think, check, act, observe. Before tool-calling, the same loop was plain text: Thought,
> Action, Observation, and a parser in our code.
>
> And one thing is missing. Nothing in these lines ever says stop.

## 2 · `harness`: the limits Icarus did not keep (end of Section 3)
**Shots.** The loop ring inside the harness rig; the eight modules light in turn, each with a one-line label. A dial
for max steps turns to 2: the ring stops after one round; the race-board tiles for the orders turn ember (2 of 6,
`knobs.agent.max_steps_2`). A budget gauge at 6,000: the capsule stops mid-ring (3 and 4 of 6). Then Emma's two days:
"Yes, go ahead." → `create_purchase_request` → PR/2026/04417 · WAITING FOR APPROVAL; the pause module glows ember, the
write arms of the rig lock. Night: the state flows into the night vault (6,917 bytes, 11 messages); the machine powers
down. Morning, case 1: Emma says Daniel approved; the harness reads Ledgerline first ("still WAITING FOR APPROVAL"),
the model never wakes (0 model calls). Daniel signs in his inbox (a document stamp). Case 2: Ledgerline says APPROVED;
the machine is rebuilt from the vault; `create_purchase_order` → PO/2026/01182, `release_purchase_order` → RELEASED.
Coda: the lost reply: a capsule's reply vanishes; the first recovery rule blocks the retry (0 of 2); the fixed rule
retries and the tool finds the saved request (2 of 2).

**Script (draft).**
> Around the loop sits the harness: the code that decides what the model may choose from, and for how long.
>
> Turn the step limit down to two, and every order stops half done. Starve the budget, and the loop stops mid-job.
>
> Now Emma says yes. The request is saved, and Ledgerline sends it to Daniel. The harness sees who it waits for, holds
> every write, and lets the model tell Emma.
>
> Daniel may sign tomorrow. So tonight the agent becomes six thousand nine hundred bytes of JSON, and the machine is
> switched off.
>
> In the morning Emma says Daniel approved it. The harness does not ask the model. It asks Ledgerline. Still waiting.
> Then Daniel signs, and this time Ledgerline says approved. A new agent is built from last night's JSON. The order is
> created, and released to Voltway.
>
> The model chooses the next step. The harness decides when to stop, when to wait, and what to believe.

## 3 · `workflow`: the labyrinth and the wings (end of Section 5)
**Shots.** Two stages side by side. Left, the labyrinth: eleven blocks on a rail; the spring order runs through them
(the model step reads the fields: 208 tokens), each block lights, the approval tray holds the run as a document,
Daniel's stamp, the run resumes, released. The Nordic order: the certificate gate drops and the run stops at step 5;
then the gate is lifted out (the measured `no_cert` variant) and the same order runs straight through to Nordic Cell Co.
(ember). Right, the wings: the agent's loop on the same jobs, three runs side by side with different paths
(`race.per.spring.ag[*].path`). The race board fills: workflow 4 of 6 at 1,241 tokens; agent 18 of 18 at 365,157 tokens
over three runs. The two jobs the workflow stops on (cheapest-if-allowed, the question) glow; one more written branch
(the `cert_switch` variant) turns the fallback tile green: 5 of 6. Close on the rule as a typed title.

**Script (draft).**
> The same order, two ways. On the left, every step written down. One model call reads Emma's words. Then the code
> follows the line, the same way every time.
>
> A gate is code. The order from Nordic Cell Co. stops here, every time. Lift the gate out, and Ledgerline accepts the
> order. Nobody else was standing in the way.
>
> On the right, the agent chooses its steps as it goes. Right on all six jobs, but not always by the same path, and at
> about a hundred times the tokens.
>
> The workflow stopped on the two jobs nobody wrote down. Write one more branch, and it handles one of them.
>
> When you know the order, write it down. When you do not, let the model choose, inside a harness.

## Credits (end cards, when rendered)
Dr. Rajat Dandekar · Vizuara. Narration: ElevenLabs, voice Daniel. Music: Epidemic Sound (not redistributed). Model in
the recorded runs: gemini-3.8-flash (Gemini API). Rendering: Blender Cycles on Modal.

## Screen recordings (made, not films)
The practical slides use Playwright recordings of Daedalus on the live URL (no narration), made by
`deploy/daedalus_modal.py::record` from `experiments/daedalus_record.py`: `daedalus_loop.mp4` (44 s),
`daedalus_night.mp4` (96 s), `daedalus_knob.mp4` (68 s), `daedalus_workflow.mp4` (20 s), `daedalus_wfwait.mp4`
(49 s), `daedalus_race.mp4` (43 s). Contact sheets: `../qa/sheets/` (`deploy/daedalus_modal.py::sheets`).
