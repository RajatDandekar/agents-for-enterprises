# brain3d: "The Brain" (Lecture 2)

One three.js scene for the whole of Lecture 2. It follows one sentence, Emma's question "How many city e-bike battery packs do we have in Manchester stores?", through a real language model (Qwen2.5-0.5B-Instruct), from the text going in to the made-up number coming out, and then to the fix. The scene grows section by section (the 9 sections of `../STORY_V4.md`). Earlier sections' parts stay in the scene, dimmed, and the camera flies to the active part. The left rail shows Emma's chat, the reply as it is written, and "The trace so far", one line per section. Every number on screen is read from `trace.json`.

| File | What it is |
|---|---|
| `brain3d.js` | The ES module. `mountBrain3D(el, { trace, section, mode })`: see the API below. |
| `deck.js` | Registers `FIGS.brain3d` for the plate engine (a classic script). All brain3d slides share one renderer, which moves into the slide being shown. |
| (interaction) | In both modes: drag to orbit, scroll to zoom, right-drag to pan; **Reset view** gives the camera back to the step. Clicking a token tile opens a card with its id, role, first 8 of 896 input-embedding values and its attention row (where it looks, averaged over all heads and blocks, plus how much the last token and block 24 head 2 look at it), with arcs to its top 4. Answer tiles show their probability and the other top-5 guesses. Hovering a block shows its logit-lens top 5 (for the first digit in section 7, steps 2 and later). A drag or a tile click never steps the deck; arrow keys and the clicker always do. |
| `index.html` | A full-screen standalone demo for class. Keys: Right arrow or Space = next, Left = back, 1 to 9 = jump to a section, R = replay, A = autoplay, F = full screen. URL options: `?section=6`, `?section=7&step=2`, `?section=7&step=2&t=3.5`, `?autoplay`, `?still`. In section 6 a temperature slider recomputes the bars live. |
| `trace.json`, `trace.js` | The recorded run. Both hold the same data; `trace.js` sets `window.BRAIN_TRACE`, so the deck works without fetch. About 0.2 MB. |
| `poster-s1.png` … `poster-s9.png`, `poster.png` | 1920x1080 stills of each section's last step. They are shown when WebGL or the module is missing, and in `?print=1`. |
| `capture_trace.py` | Records the trace on Modal (CPU). |
| `qa_render.py` | Renders headless on Modal (Chromium and SwiftShader) into `qa/`, which is gitignored. |

## Slide snippets for `lectures/L2-the-brain/index.html`

1. In `<head>`, before any other script (the import map must come first):

```html
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
```

2. Before `../../engine/plates.js` (after `figs.js` is fine):

```html
<script src="brain3d/trace.js"></script>
<script src="brain3d/deck.js"></script>
```

3. Use one slide per section. Each slide has a full-bleed figure with `data-section="N"` and that section's number of empty steps. With no steps shown, the slide shows the section's first state; after k steps it shows state k. A forward step plays that state's animation (3 to 8 s). Entering the slide or stepping back jumps to the state's end state, and the camera glides on from wherever it was.

```html
<section class="slide" data-plate="The game: predict the next token">
  <div class="fig" data-fig="brain3d" data-section="1" style="left:0;top:0;width:1600px;height:900px"></div>
  <span class="step"></span><span class="step"></span>
</section>
```

| Section | `data-plate` title (as in STORY_V4) | `.step` spans | States, in order (k = steps shown) |
|---|---|---|---|
| 1 | The game: predict the next token | **2** | 0 the sealed box, the text goes in · 1 the bars come out: "We" 56% · 2 a few tokens later, the first digit: 1 34%, 2 21%, 5 12% |
| 2 | What you send, cut into tokens | **3** | 0 the box opens, 100 token tiles drop in · 1 ids and roles (system 72, question 15, markers 13) · 2 how words and numbers are cut · 3 counted in tokens (100 in, 20 out, 32,768 window) |
| 3 | Each token becomes a vector | **3** | 0 the tiles rise into columns of numbers · 1 the first 8 of 896 values of " battery" and " Manchester" · 2 the embedding map (PCA, 46 words) · 3 nearest neighbours of " battery" and " Manchester" |
| 4 | Attention: tokens look back | **7** | Query, key, value in block 24, head 2 (the real head with 65% on " Manchester"): 0 the last position's query column, every earlier token's key column, and the first 8 of 64 numbers of q, k(Manchester) and v(Manchester) · 1 q·k ÷ √64 as bars on the tiles: " Manchester" 7.81, the system prompt's " Manchester" 5.45, ⏎ 5.00 · 2 softmax: the bars become weights (65%, 6%, 4%…) and the arcs grow · 3 the value columns of the top tokens fly to the last position and add up to the head's output · then the old states: 4 all heads and blocks averaged · 5 block 16, head 0 → " battery" 9% · 6 block 12, head 13 rests on the first token · 7 only backwards: " battery" cannot see what comes after it |
| 5 | A block, then 24 of them | **3** | 0 one block = attention + MLP · 1 24 blocks stack up, the vectors rise through them · 2 the logit lens climbs the stack · 3 the answer forms near the top ("We" from block 22, 56% at block 24) |
| 6 | From a vector to a choice | **4** | 0 the top vector meets the vocabulary (151,936 scores) · 1 temperature 0 · 2 temperature 0.7 · 3 temperature 1.2 · 4 one token is picked: "We" |
| 7 | The loop: one token at a time | **4** | 0 "We" joins the strip, the pass runs again · 1 " currently", " have", " " · 2 the first digit, with its logit lens (4, 4, 5, then 1) · 3 "100" and the rest of the reply · 4 five samples at 0.7: 300, 150, 1,000, 50, 15 |
| 8 | Where the weights came from | **3** | 0 random weights (the tiny GPT before training) · 1 pretraining fills the blocks (the tiny GPT's loss curve) · 2 instruction and preference tuning (the tiny GPT's trained sample) · 3 the last training day, 19 Sep 2024, against Emma's 26 Oct 2026 |
| 9 | Why it made the number up, and what fixes it | **3** | 0 "100" against 5,400 in Ledgerline · 1 traced back: no input token carried the stock, only the date's digits · 2 the stock line added to the prompt: "5,400", and the head that reads it · 3 the two sockets: Knowledge (Lecture 3) and Tools (Lecture 4) |

That is 32 steps across 9 slides (41 states). Section 4 went from 4 to **7** steps on 2026-10-30, when the query/key/value states were added. In the browser console, `brain3d.sections` lists them. The step counts are fixed in `brain3d.js` (`SECTION_STATES`), not taken from the trace, so a re-recorded trace does not change the slides.

Notes for the deck builder:
- The figure draws its own section kicker, headline, one-line caption, chat rail and provenance footer inside the 1600x900 frame. In deck mode it leaves the top 92 px for the plate head and the bottom 60 px for the deck's chrome. It hides its own previous and next buttons and its progress dots; the deck's arrows drive it. Its Replay and Autoplay buttons are `<button>`s inside `.ctl`, so the plate engine ignores clicks on them.
- The figure's root element is `.brain3d`, not `.b3d`, so the deck's `.b3d` fallback styles in `l2.css` (for example `.b3d svg{position:absolute}`) never reach it.
- In deck mode the scene draws only while something moves: a step playing or the camera gliding. It never draws while its slide is hidden, and it has no idle camera drift. While the camera glides from the previous slide, every label is hidden; labels fade back in as the camera arrives, so no label is ever outside the frame mid-flight. Animations run in real time, capped at 0.5 s per frame.
- Several brain3d slides on one page share **one** WebGL context. Other figures on the page are not affected.
- A "Try it live" pill can link to `brain3d/index.html?section=N`. That page is full screen, with the temperature slider in section 6.
- Opened from `file://`, browsers block ES modules, so each slide shows its `poster-sN.png`. Serve the folder over http, as the Vercel site does.

## API

```js
import { mountBrain3D, loadTrace, SECTION_TITLES, SECTION_STATES } from './brain3d/brain3d.js';
const b = mountBrain3D(el, { trace, section: 3, mode: 'deck' | 'standalone', step, t, still, autoplay });
b.go(k, instant)             // state k of the current section; stepping back always jumps to the end state
b.setSection(n, k, instant)  // section n (1..9), state k
b.next(); b.prev()           // standalone: past the end of a section moves on to the next section
b.replay(); b.autoplay(on)
b.seek(n, k, seconds | 'end')// for QA and stills
b.setTemperature(T | null)   // section 6: bars from the recorded logits at any T in 0..2 (null = the step's own T)
b.attach(newEl)              // move the one renderer into another element (deck.js does this per slide)
b.section, b.step, b.count, b.sections, b.stages, b.render(), b.resize(), b.destroy()
```

## Provenance

- **Run:** `/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/capture_trace.py` (4 vCPU, no GPU, no API keys). It uses the same image as `experiments/models_modal.py`, with torch 2.4.1+cpu, transformers 4.46.3 and numpy 2.0.2. The model is **Qwen/Qwen2.5-0.5B-Instruct**, revision `7ae557604adf67be50417f59c2c2f167def9a775`, in float32 with `attn_implementation="eager"`, so the attention weights can be read. The current trace was recorded at 2026-10-30 05:40 UTC. Two earlier runs that day gave identical tokens and probabilities.
- **The prompt is the app's own brain stage.** `capture_trace.py` reads `BRAIN` and `PEOPLE` from `ledgerline/ledgerline/experience/harness.py` and formats them as `_system('brain', 'ECLARKE')` does: Emma Clarke, purchase executive. That is the system prompt the app sends with `stage=brain`, which has no tools and no tool descriptions. Emma's question follows, and both go through the model's own chat template with `add_generation_prompt=True`. The result is 100 tokens: system 72, user 15, template 13. The exact text is in `trace.json` under `prompt.system` and `prompt.chat_text`.
- **Decoding:** greedy is a plain argmax at every step. The samples are softmax(logits / 0.7) with no top-k, top-p or repetition penalty; the model's `generation_config` is not used. The seeds are 0 to 4.
- **Logit lens:** after block l, the model's final RMSNorm and then its unembedding, which is tied to the input embeddings. Block 24 is the model's own output.
- **Query, key, value** (`--qkv 1`, saved under `attention.qkv`): recomputed for block 24, head 2 from the block's own `input_layernorm`, `q_proj`, `k_proj` and `v_proj` and the rotary embedding, with key/value head 0 (Qwen2.5 shares each key/value head among 7 query heads). softmax(q·k/√64) matches the model's own attention weights to 1.2e-7. `attention.rows` holds every prompt position's top-6 attention, averaged over heads and blocks, for the token cards. Same model and revision as the main run.
- **Attention:** the eager attention probabilities. `avg` rows are the mean over the 14 heads; the scene's arcs in section 4 also average over the 24 blocks. Each of the three named heads was picked by a fixed rule, recorded in `attention.heads[].why`: the largest weight on the user's " battery" (or " Manchester") from the last prompt position, among blocks 3 to 24; and the largest weight on position 0 among blocks 9 to 16.
- **Embeddings:** the input-embedding rows. The PCA is fitted on 46 reference words; a word cut into several tokens is the mean of its pieces. Its 3 components explain 6.0%, 5.8% and 4.8% of the variance. Neighbours are by cosine over every vocabulary entry that is a clean word with a leading space.
- **Temperature dial:** `final.dial_last` and `final.dial_digit` hold the top 40 raw logits, plus log Z(T) over the whole vocabulary on a grid of T from 0.10 to 2.00. So the slider's probabilities are exact, not renormalised over the top 10.
- **With facts:** the line "Ledgerline stock, BAT-500 at Manchester main stores: 5,400 on hand" is appended to the system prompt as its last line, giving 123 tokens. Everything else is unchanged.
- **Parameter counts** are counted from the loaded model, 494,032,768. They match `experiments/logs/model_card.json`, which is copied into `trace.json` as `model_card`.
- **Training facts** in section 8 come from the Qwen2.5 Technical Report (arXiv:2412.15115) and the model card: up to 18 trillion pretraining tokens, over 1 million instruction-tuning examples, and offline DPO followed by online RL. The release date is 19 Sep 2024. The release date is shown as "the last training day"; Qwen does not publish an exact data cut-off.
- **The tiny GPT** comes from `experiments/logs/tinygpt.json`, the Northbridge corpus re-run by the experiments builder. `capture_trace.py` includes it only if the log passes a world check (no old-world names). `--pack 1` re-packs `trace.json` and `trace.js` without running the model, so a new tiny-GPT log can be picked up in seconds.
- **Columns of numbers:** each column draws the first 12 of the token's 896 input-embedding values, with blue for positive and slate for negative.

## The trace, in numbers

- **Greedy answer:** "We currently have 100 city e-bike battery packs available in our Manchester stores." That is 20 tokens. The digits came at **1: 33.6%** (next 2: 20.8%, 5: 11.6%), **0: 32.2%** and **0: 54.2%**.
- **Five samples at 0.7:** 300, 150, "over 1,000", 50 and 15.
- **Logit lens, last prompt position:** fragments of code and other languages up to block 17. "we" first appears after block 18. "We" holds from block 22: 8% at block 22, 29% at 23, 56% at 24.
- **Logit lens, first digit:** the top token is "4" after blocks 21 and 22, "5" after block 23, and "1" only after block 24.
- **Traced back:** at the first digit, the model looks back over 104 tokens. The only digits in the input are the date: 26 October 2026.
- **With facts:** "We have 5,400 city e-bike battery packs in Manchester stores." The digit tokens came at 5: 75.7%, ",": 37.2%, 4: 75.7%, 0: 99.97% and 0: 99.99%. Block 10, head 13 puts 76% of its weight on the fact's "5" (77% on the five tokens of "5,400"). At temperature 0.7, only 1 of 5 samples said 5,400. Three said "5" (the comma had only 37%), and one said "500", taken from BAT-500.

## QA

```sh
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py               # every state, 1920x1080 -> qa/sN-kK.png
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --deck 1      # every state, 1600x900 deck mode -> qa/sN-kK-deck.png
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --shots "7:3:2.5,9:2:4"   # section:state:seconds
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --check 1     # deck-QA rules on every state, sampled each second
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --plates 1    # through the real plate engine, 9 slides, one shared scene
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --posters 1   # rewrites poster-s1..9.png and poster.png
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --real 1      # the real L2 deck (index.html + plate engine): every 3D slide and step, after it settles -> qa/deck-slideNN-kK.png + qa/realdeck.json
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --real 1 --only 32,42   # just those slides
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --dqa 1       # tools/deck_qa.js on the whole L2 deck, mounting only L2 + engine (use when other builders are writing files elsewhere)
/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/qa_render.py --inter 1     # real deck: drag, tile click, block hover, arrow key -> qa/interact*.png + qa/interact.json
```

The `--check 1` run applies these rules:
- no text outside the 1600x900 frame, less 20 px;
- no clipped boxes;
- no text under 12 px after label scaling.

Labels are kept inside the frame at run time. Callouts slide back into the free stage, which is right of the rail, below the headline and above the footer. Block tags and chips that would have to move far are hidden instead.
