# flow3d: "How it works, underneath" (Lecture 1)

A three.js scene that shows one real Ask Northbridge conversation, step by step: Emma's message, the harness building the context, the LLM picking one of the 15 tools, the guard, MCP, the toolbox, the Ledgerline services (a black box), the result coming back, the preview, Emma's yes, Daniel's approval inbox and the receipt. Every number and every piece of JSON on screen comes from `trace.json`.

| File | What it is |
|---|---|
| `flow3d.js` | The ES module. `mountFlow3D(el, { trace, mode: 'deck' or 'standalone' })` returns `{ go(k, instant), next(), prev(), replay(), autoplay(on), seek(k, seconds), count, stages }`. |
| `narration.json`, `audio/stage-XX.mp3`, `make_narration.py` | The narration script, its 21 clips in Rajat's voice, and the script that checks and synthesizes them. |
| `deck.js` | Registers `FIGS.flow3d` for the plate engine (classic script). |
| `index.html` | Full-screen standalone demo for class. Keys: Right arrow or Space = next, Left = back, R = replay, A = autoplay, F = full screen. URL options: `?autoplay`, `?stage=5`, `?stage=5&t=2.4`, `?still`. |
| `trace.json` / `trace.js` | The recorded run (same data; `trace.js` sets `window.FLOW3D_TRACE` so the deck also works without fetch). |
| `poster.png` | 1920x1080 still of the overview, shown when WebGL or the module is missing, and in `?print=1`. |
| `capture_trace.py` | Records the trace on Modal from the real L1 assistant. |
| `qa_render.py` | Renders stages headless on Modal (Chromium + SwiftShader) into `qa/`. |

## Presenting it in class (narrated)

The figure carries Rajat's own narration: one clip per stage, in his cloned voice (ElevenLabs voice `lZORFNDokoBmfd0S06vf`, model `eleven_multilingual_v2`). There are 21 clips, 4 min 32 s of speech. A full narrated run takes about **5 minutes**, because each stage lasts at least as long as its clip, followed by a 0.9 s pause.

- **Play the whole story:** on the 3D slide, click **Play with narration** (bottom right). It plays every stage in order from the current one, or from the start if you are on the last stage. The animation slows down (to no less than 0.55x) so the motion keeps pace with the voice, and the next stage starts when the clip ends.
- **Pause:** press **Space**, or click the same button (now **Pause**/**Resume**). Audio and animation stop and start together. In the deck, Space only pauses the narration while it is playing; otherwise Space steps the deck as usual.
- **Step by hand:** the arrow keys and clicks step stages as before. With **Voice on**, each forward step plays that stage's clip. Stepping back, or entering the slide, is silent.
- **Silent mode:** the **Voice on/off** toggle mutes the clips. **Autoplay** is the silent loop. When you leave the slide, the narration stops.
- **Standalone** (`flow3d/index.html`): N = play with narration, Space = pause/resume while narrating (next otherwise), V = voice on/off.
- **Browser autoplay rules:** these are met because narration starts from a click or a key press. Before class, open the slide once with the projector's audio on.

The script is in `narration.json`. `text` is what is said; `say` is the same words spelled for the voice, e.g. "M C P", "P R D zero seven". `make_narration.py` checks every number in the script against `trace.json`, then synthesizes only the clips whose words changed, into `audio/stage-XX.mp3`. If the trace is re-recorded, its numbers or stage list change. The figure then switches narration off by itself: the stage kinds and `trace_recorded_live` must match. In that case, edit `narration.json` and run `python3 lectures/L1-before-and-after/flow3d/make_narration.py`. The key is read from `cobol-mainframes/.env`.

## Slide snippet for `lectures/L1-before-and-after/index.html`

1. In `<head>`, before any other script (the import map must come first):

```html
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
```

2. The slide: a full-bleed figure and **20** empty steps. After k steps the figure shows stage k; stage 0 (no steps shown) is the overview. A forward step plays the stage (5 to 20 s each); entering the slide or stepping back jumps to the stage's end state.

```html
<section class="slide" data-plate="How it works, underneath">
  <div class="fig" data-fig="flow3d" style="left:0;top:0;width:1600px;height:900px"></div>
  <span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span>
  <span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span>
  <span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span><span class="step"></span>
</section>
```

3. Before `../../engine/plates.js` (after `figs.js` is fine):

```html
<script src="flow3d/trace.js"></script>
<script src="flow3d/deck.js"></script>
```

Notes for the deck builder:
- The figure draws its own title, caption and chat rail inside the 1600x900 frame. In deck mode it leaves the top 80 px for the plate head and hides its own prev/next buttons; the deck's arrows drive it. Its Replay and Autoplay buttons are `<button>`s, so the plate engine ignores clicks on them.
- The step count is the number of stages minus one. It is 20 for this trace (21 stages, overview included). If the trace is re-recorded and the stage list changes, `flow3d.count - 1` in the browser console gives the new number.
- A "Try it live" pill can link to `flow3d/index.html` (full screen, autoplay with `?autoplay`).
- Opened from `file://`, browsers block ES modules, so the slide shows `poster.png`. Serve the folder over http (the Vercel site does).

## The stages (this trace)

The stage list is built from `trace.json`: one stage per turn arrival, the first tool call taken apart in four stages, then one stage for each later model step (with all of its tool calls), the reply, the write and the receipt.

| k | Stage | What it shows |
|---|---|---|
| 0 | Overview | The whole path. 3 turns, 13 model calls, 11 tool calls, 15 tools over MCP. |
| 1 | Emma's message arrives | "How many city e-bike battery packs do we have?" goes to the harness as a user message. |
| 2 | Context assembly | System prompt 196 tokens (real text), history 11, 15 tool schemas 1,932: 2,139 tokens. |
| 3 | The LLM picks one tool of 15 | The cards fan out; `find_item({"query": "city e-bike battery pack"})`, 21 tokens out, 2.68 s. |
| 4 | Guard, then MCP | Arguments checked against tool.json; the real JSON-RPC `tools/call` frame rides the MCP pipe. |
| 5 | Ledgerline services | 11 service calls (itm_search x5, itm_get x6), rc S. |
| 6 | Result back | The result JSON returns; the next call is 2,507 tokens. |
| 7 | search_policy | The loop into the manuals, not Ledgerline. |
| 8 | check_stock BAT-500 | 5,400 + 1,200 = 6,600 free, 11 days of cover. |
| 9 | check_stock BAT-500-R says no | `ok: false`, "Ledgerline has no stock record for BAT-500-R." |
| 10 | The answer | No tool call: the reply (99 tokens, 4.13 s) and the tools it used. |
| 11 | A new request | "Order 2,000 battery packs from Voltway Cells for the spring launch run, cost centre PRD-07, needed by 9 November." |
| 12 | find_supplier | Voltway Cells, VC-EIN-0042. |
| 13 | search_policy | The direct-order limit in the manuals. |
| 14 | create_purchase_order says no | `ok: false`: "A direct order is limited to £50,000; this one is £285,600." Next step: raise a purchase request first. |
| 15 | check_budget | PRD-07, spring launch run, open. |
| 16 | The preview | create_purchase_request with `confirm: false`: £273,600, approver DOKAFOR, nothing saved. |
| 17 | The preview reply | The model asks Emma to confirm. |
| 18 | Emma: "Yes, go ahead." | |
| 19 | The write | `confirm: true`: pr_save, pr_submit, and PR/2026/04417 drops into Daniel's inbox next to PO/2026/01179. |
| 20 | The receipt | The pr_get read-back (WAITING FOR APPROVAL, PA, DOKAFOR) goes back to the model and into Emma's chat. |

## Provenance and re-recording

- Recorded with `sh tools/mrun.sh tools/modal_run.py --script lectures/L1-before-and-after/flow3d/capture_trace.py --mode auto`. The script runs `ledgerline.course.l1.AskNorthbridge` (gemini:gemini-3.8-flash, toolbox over in-memory MCP) as ECLARKE. It wraps the LLM and the tool calls to log tokens, seconds, the guard check, the MCP frame and each Ledgerline service call.
- The cassettes are `ledgerline/ledgerline/cassettes/L1v4_flow3d.jsonl` and `L1v4_flow3d_measure.jsonl`. The current trace was recorded fresh at 2026-10-30 04:15 UTC, after the tool descriptions and policy documents were finalised: 13 model calls, 52,273 tokens in, 675 out. The second holds two extra calls that split the context by difference: the request without tools, and the system prompt with a one-character user turn.
- `--mode replay` rebuilds the same trace with no key, and only if every request still hashes the same. A clean replay proves the trace matches the current prompt and tool schemas.
- QA: `/Users/raj/.venv/bin/modal run lectures/L1-before-and-after/flow3d/qa_render.py --check 1` applies the deck-QA rules (text outside the 1600x900 frame less 20 px, clipped boxes, text under 12 px) to every stage, sampled each second; `--plates 1` drives it through the real plate engine, including Space pausing the narration without stepping the deck; `--audio 1` checks that every clip loads and that play, pause, resume and a manual step work, in standalone and deck mode; plain `qa_render.py` renders every stage's end state, `--shots "3:2.2,4:4.4"` (stage:seconds), `--deck 1` (1600x900 deck mode), and `--poster "0:end"` (rewrites poster.png).
