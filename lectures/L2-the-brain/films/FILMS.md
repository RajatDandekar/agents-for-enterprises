# Lecture 2 films (The Brain)

Eleven narrated Blender Cycles films on Emma's question ("How many city e-bike battery packs do we have in Manchester stores?"), the same example the slides teach, run through Qwen2.5-0.5B-Instruct. Each film plays at the **end** of its section as the recap, after the theory. Every number on screen comes from a recorded run (`../brain3d/trace.json`, `qkv_data.json`, `../experiments/logs/`).

Embed with `<video controls preload="metadata" poster="films/<name>.jpg">` and two `<source>` lines (`.webm` first, then `.mp4`). Never autoplay. Files: `films/<name>.mp4` (H.264, faststart), `films/<name>.webm` (VP9 + Opus) and `films/<name>.jpg` (poster). All are 1920x1080 at 30 fps, mixed to -16 LUFS integrated, true peak about -1.5 dBFS.

| Base name | Plays at the end of section | Duration | mp4 | webm |
|---|---|---|---|---|
| `overture` | Lecture opener (before section 1) | 0:41 (41.3 s) | 21.4 MB | 21.7 MB |
| `s1_game` | 1 | 1:18 (77.7 s) | 24.2 MB | 24.5 MB |
| `s2_tokens` | 2 | 1:49 (108.6 s) | 24.2 MB | 26.4 MB |
| `s3_vectors` | 3 | 1:22 (82.5 s) | 24.1 MB | 25.8 MB |
| `qkv` | 4, after the Q/K/V theory | 2:26 (146.2 s) | 24.3 MB | 26.1 MB |
| `s4_attention` | 4, end | 1:26 (86.3 s) | 24.2 MB | 25.3 MB |
| `s5_blocks` | 5 | 1:13 (72.6 s) | 24.2 MB | 25.0 MB |
| `s6_choice` | 6 | 1:14 (73.6 s) | 23.8 MB | 25.4 MB |
| `s7_loop` | 7 | 1:15 (74.6 s) | 24.0 MB | 23.9 MB |
| `s8_weights` | 8 | 1:23 (83.2 s) | 24.2 MB | 26.5 MB |
| `s9_fix` | 9 | 1:13 (72.7 s) | 24.1 MB | 24.9 MB |

## Look and sound (one series)

- **World:** one shared kit, `build/kit/l2kit.py`. It is a "midnight slate" studio: a deep blue-grey sweep graded to black, one big soft key, a cool rim light, a low warm fill, and lights hidden from reflections. The set has a dark graphite plinth with an aluminium trim and ceramic token tiles with smoked-glass faces and role bands (sky for Emma, slate for system, warm grey for chat markers).
- **Props:** vectors are dark-glass plates in machined frames whose cells glow with the real values (query sky, key violet, value warm white). Glass columns fill with light to show scores and weights. Light beams and arcs carry attention. The model is a 24-floor block stack with 14 head modules per floor. Rendered on Modal (L40S, Cycles, 96 samples, OIDN).
- **Text:** all readable text is a 2D overlay in Google Sans Flex / Google Sans Code (`build/overlay.py`): dark-glass pinned cards, formula chips, typed titles, subtitles and an end card. Hero tokens carry their word on the tile face; small labels appear only on tiles at least ~40 px wide, never overlap, and are never truncated.
- **Sound:** narration by ElevenLabs Daniel (`onwK4e9ZLuTAKqWW03F9`, eleven_multilingual_v2, speed 1.08). The music bed is "Tried-And-True" by Imprismed (Epidemic Sound), ducked under the voice with a sidechain compressor. It is different from L1's "Envision" and lives in `films/music/`, which is gitignored. A designed SFX set (`build/sfx/`, ElevenLabs sound generation) adds tile, rise, beam, fill, chime, tick, bloom, merge, resolve and whoosh sounds.

## How to rebuild
```sh
cd lectures/L2-the-brain/films/build
python3 narrate.py <film>                                   # narration + timeline (light HTTP)
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::style --film <film> --frames 300,900 --tag t1   # style stills with overlays
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::full --film <film>   # build + render on L40S (add --resume to keep chunks)
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::comp --film <film>   # overlays + mix + mp4/webm/jpg -> films/
```
The Modal volume is `video-ad-edit:/l2films` in workspace rajatworkspace. Scenes are `build/scenes/<film>.py`, overlay and SFX specs `build/specs/<film>.py`, film-specific props `build/kit/props_*.py`. The q/k/v data comes from `/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/capture_trace.py --film-qkv 1`, which writes only `films/qkv_data.json`; trace.json is untouched.

## The films

### `overture`: The Brain (section Lecture opener (before section 1))

**Shots.** Emma's question lights tile by tile on the strip; a slow pass over the 24-floor stack as it runs; the ember "100" lands beside the green Ledgerline plaque "5,400".

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> One question. How many city e-bike battery packs do we have in Manchester stores?
>
> One hundred tokens go in. Twenty-four blocks of a real language model turn them over. At every step, one token is chosen from 151,936.
>
> And out comes a confident answer: 100. The truth is 5,400. Today we open the machine, and find out where that number came from.

### `s1_game`: The game: predict the next token (section 1)

**Shots.** Sealed model enclosure (24-floor stack seen through a frosted window) fed by the 100-tile strip; next-token glass columns on a tray (We 56.4, As 7.9, Manchester 6.1, In 5.3, Our 4.2, At 2.8); the "We" tile flies to the strip, " currently", " have", " " join; digit columns (1 33.6, 2 20.8, 5 11.6, 3 11.3, 4 8.8, 6 4.4); the enclosure opens and the stack glows.

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Here is the whole idea of a language model, as one game. Text goes in. Out comes a guess: which token comes next?
>
> We give it Emma's question, with the app's instructions in front: 100 tokens. The model reads them all and gives a score to every token it knows. Turned into probabilities, the top of the list looks like this.
>
> We: 56 percent. As: 8. Manchester: 6. In: 5. The model is not certain. It is placing bets.
>
> Pick one, add it to the text, and play again. A few tokens later, the answer reaches its number. Now the bets are on a digit. One: 34 percent. Two: 21. Five: 12.
>
> Nothing here looks anything up. Every word of the answer, the number too, is a bet like this one. The rest of the lecture opens the box, to see how the bets are made.

### `s2_tokens`: What you send, cut into tokens (section 2)

**Shots.** The question as one bar cut by a light blade into 15 tiles with ids; the chat as 100 tiles (72 system, 15 Emma, 13 markers); macros on Manchester (19361), North+bridge (4787, 13709), 5,400 as 5 , 4 0 0 (ids 20 11 19 15 15); the hand BPE run from bpe.json (battery and packs fusing, 86 to 36 tokens); the vocabulary rack (1,187 bands of 128 rows) with the drawer of 22 special rows and 271 padding rows.

**Numbers from.** brain3d/trace.json (tokens, number_cuts); experiments/logs/bpe.json (hand BPE run); films/qkv_data.json vocab block (151,643 BPE pieces + 22 special = 151,665; config.vocab_size 151,936 = 1,187 x 128; 271 padding rows).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Last section, text went in. But a model never sees letters. It sees tokens: pieces of text, each with a number.
>
> Emma's chat is cut into 100 tiles. 72 for the app's instructions, 15 for her question, and 13 for the markers that say who is speaking.
>
> Common words are one tile each. Manchester is one token, number 19361. Northbridge is two: North, bridge. And a number is cut digit by digit. 5,400 becomes five tokens: five, comma, four, zero, zero.
>
> Where do the pieces come from? From byte pair encoding. Start with single bytes, then keep merging the pair that appears most often in a huge pile of text. Qwen's tokenizer learned 151,643 pieces this way.
>
> Add 22 special tokens, like the markers in Emma's chat, and you get 151,665. The model's table has a few more rows: 151,936. That is 1,187 times 128, a size GPUs handle well. No token ever uses the extra 271 rows.
>
> So: 100 tokens in. That is what Emma's question costs, and exactly what the model reads.

### `s3_vectors`: Each token becomes a vector (section 3)

**Shots.** The Manchester tile looks up row 19361 in the table rack; 896-cell slabs with the real embeddings for positions 80-99; the PCA meaning map (46 words; 6.0 / 5.8 / 4.8% variance) with clusters (bike parts, places, days and months); cosine-neighbour fans for battery and Manchester; the row of columns again.

**Numbers from.** films/qkv_data.json vectors.embedding (full 896-dim rows, positions 80-99); brain3d/trace.json embeddings (v16 values, PCA, neighbours).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Last section, Emma's question became tokens. But token 19361 means nothing on its own. So each token looks up its row in a table.
>
> Each row is a vector: 896 numbers. Here is battery. Here is Manchester. The model learned every one of these numbers in training.
>
> Why so many? Because a vector is a position, in a space of meaning. Words that are used alike end up close together. Squash the 896 dimensions down to three, and you can see it.
>
> The bike parts gather here. The cities, there. The days and months, over here.
>
> Ask which words sit nearest to battery, and you get batteries, lithium, capacitor, charger. Nearest to Manchester: Liverpool, Nottingham, Leicester, Leeds.
>
> So the strip of tiles is now a row of 100 columns, each one a point in meaning. Next, those columns start to talk to each other.

### `qkv`: Query, key and value (section 4, after the Q/K/V theory)

**Shots.** b1 dolly along Emma's tokens to the last position (it lights); b2 query, key and value plates rise from every tile; b3 the last token's 896-number vector through three machined matrices W_Q, W_K, W_V prints q, k, v; b4 the query plate turns to face the keys, beams go out to all 100 keys; macro: query and Manchester's key open like a book, cells light pair by pair, the glass column follows the real running sum of q_i x k_i to 62.5; every column fills to its dot product; b5 scores (÷8): Manchester 7.81, Manchester in the system prompt 5.44, stores 4.54, battery 1.36; b6 softmax reallocates the light: 65.2%, 6.1%, 3.9%, 2.5%; b7 the weighted values slide into one bright output plate (64 real numbers); b8 the output docks into head 2 on floor 24 of the block stack, the 14 heads and then all 24 floors light.

**Numbers from.** films/qkv_data.json (capture_trace.py --film-qkv 1 on Modal CPU: q, k, v of block 24 head 2 recomputed from the block's projections and rotary embedding; softmax(q·k/8) matches the model's own attention to 1.2e-7; vocab sizes from the tokenizer and config); brain3d/trace.json (tokens, roles).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Emma's question is now a row of 100 tokens. The last one sits at the very end, where the answer is about to begin. Before the model writes a word, this position has to find out which earlier tokens matter.
>
> Attention gives every token three new vectors. A query: what am I looking for? A key: what do I contain? And a value: what I will pass on, if I am chosen.
>
> All three are made from the token's own vector, by three learned matrices. In block 24, head 2, each one is 64 numbers long.
>
> Now the last position sends out its query, to every key so far, its own included. Multiply query and key, number by number, and add it all up. That is a dot product: one score per token. When the two point the same way, the score is high.
>
> Divided by 8, the square root of 64, the scores come out like this. Manchester, in Emma's question: 7.8. The Manchester in the system prompt: 5.4. Stores: 4.5. And battery, only 1.4. This head is looking for a place, not an item.
>
> Softmax turns the scores into weights that add up to one. Every lead is magnified: 2.4 points ahead becomes ten times the weight. Manchester now takes 65 percent. The other 99 positions share the rest.
>
> Then the values. Each one steps forward, scaled by its weight. Manchester, at almost full strength. The rest, faint. Added together, they make one new vector of 64 numbers.
>
> That is what this head passes up: mostly, what Manchester means in this sentence. The query asks, the keys answer, and the values are mixed by how well they matched. Fourteen heads do this side by side, in each of 24 blocks.

### `s4_attention`: Attention: tokens look back (section 4, end)

**Shots.** Columns rise; arcs from the last position, thickness = weight averaged over all heads and blocks (33.2% on <|im_start|>, 12.5% on itself); share by role (chat markers 62.8%, Emma 19.7%, system 17.4%); three heads in their own colours (block 24 head 2 65.2% Manchester; block 16 head 0 9.1% battery; block 12 head 13 100% on position 1); the causal mask as a glass wall after " battery" (its recorded row only looks back); the 24x14 head stack.

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Every column now knows only its own word. Attention lets each position look back at the others, and take what it needs.
>
> From the last position, this is where the model looks, averaged over all 14 heads and all 24 blocks. Most of the weight goes to the chat's markers, the tokens that say who is speaking. About a fifth goes to Emma's question.
>
> But each head looks for something different. Block 24, head 2, puts 65 percent on Manchester. Block 16, head 0, is the head that looks hardest at battery: 9 percent. And block 12, head 13, rests all of its weight on the very first token, when it has nothing to add.
>
> There is one rule. A position may look back, never forward. Battery can see How many city e-bike, but not packs, or Manchester. When the model writes, the future does not exist yet, so it is masked out in training too.
>
> Fourteen heads, side by side, in each of 24 blocks. Each one mixes what it found into the column, and passes it up.

### `s5_blocks`: A block, then 24 of them (section 5)

**Shots.** One block close up (14 heads, then the MLP, 4,864 wide); 23 more floors drop in; the last position's column rides up the stack with its real 896 values after each block (vectors.lens_last); a logit-lens ladder fills in the top token per block (noise to 17, "we" at 18 with 1.6%, "We" 8.0 / 29.3 / 56.4% at 22-24); a "We" tile rises on top.

**Numbers from.** brain3d/trace.json logit_lens.last; films/qkv_data.json vectors.lens_last (final-norm residual after each block at the last position); model_card.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Attention is half of a block. The other half is a small network that works on each column by itself: the MLP. Attention gathers. The MLP thinks it over.
>
> Stack 24 of these blocks, and you have the model. Every column climbs through all 24, changing a little at every floor.
>
> Can we watch the answer forming? Take the last column after each block and ask it early: if you had to speak now, what would you say? This is the logit lens.
>
> For 17 blocks, the answer is noise: fragments of code, words from other languages. At block 18, a lowercase we appears for the first time. From block 22, We holds the top spot: 8 percent, then 29, then 56 at the top of the stack.
>
> The answer is not looked up anywhere. It condenses, block by block, near the top of the machine.

### `s6_choice`: From a vector to a choice (section 6)

**Shots.** The final column rises off the stack and sweeps the vocabulary rack; six glass columns rise to the real logits (20.84, 18.88, 18.62, 18.47, 18.24, 17.85); softmax to probabilities; a machined temperature dial 0 -> 0.7 -> 1.2 (We 100% / 81.7% / 40.9%, 56.4% at T 1.0), exact at the recorded temperatures; one "We" tile is drawn.

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> At the top of the stack, the last column is still 896 numbers. To speak, it has to become one token.
>
> So it is compared with every row of the vocabulary table, all 151,936 of them. One dot product each: a score for every token. These scores are called logits.
>
> Softmax turns the logits into probabilities. We gets 56 percent. And one dial, the temperature, decides how sharp the choice is.
>
> At temperature zero, the model always takes the top token. At 0.7, We rises to 82 percent, and the rest shrink. At 1.2, the bars flatten: We falls to 41, and unlikely tokens get a real chance.
>
> Then one token is drawn. Here, We. One token, chosen from 151,936.

### `s7_loop`: The loop: one token at a time (section 7)

**Shots.** Answer tiles drop one by one on their spoken words (sky for words, ember for the invented digits), each drop sending a pass up the stack; the first digit's logit lens on floors 21-24 (4, 4, 5, then 1); the full 20-token answer; five temperature-0.7 samples (300, 150, over 1,000, 50, 15) on a stepped riser beside the green Ledgerline plaque 5,400.

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> We joins the end of the strip. And the whole machine runs again, all 24 blocks, just to choose the next token.
>
> Currently: 48 percent. Have: 80 percent. Then a space. Then, the number.
>
> The first digit is one, at 34 percent. Look at the logit lens: block 21 says four, block 23 says five, and only the last block settles on one. Then zero, 32 percent. And zero, 54.
>
> We currently have 100 city e-bike battery packs available in our Manchester stores. Twenty tokens, and every one of them a bet.
>
> Run it five more times at temperature 0.7, and the bets land differently. 300. 150. Over 1,000. 50. 15. Five confident answers, five different numbers. The truth, in Ledgerline, is 5,400.

### `s8_weights`: Where the weights came from (section 8)

**Shots.** The stack's weight cells (illustrative pattern, labelled); the tiny GPT writing noise before training; its real loss curve as a glowing ribbon (4.59 to 0.23 over 1,500 steps); it writes the invented "2,400 on hand" against the green 5,400 plaque (in its training text three times); Qwen's three training stages; calendar blocks 19 Sep 2024 and 26 Oct 2026.

**Numbers from.** experiments/logs/tinygpt.json via trace.tinygpt; trace.training (Qwen2.5 Technical Report, arXiv:2412.15115; release 19 Sep 2024). The big stack's weight pattern is illustrative and labelled so.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Every bet came from the weights: 494 million numbers inside the model. Where did they come from?
>
> At the start, they are random. Our tiny GPT, trained on Northbridge's own documents, shows it. Before training, it writes noise.
>
> Training is the same game, played over and over: guess the next character, measure the error, nudge every weight a little. The loss falls from 4.6 to 0.23 in 1,500 steps.
>
> Afterwards it writes perfect Northbridge stock lines. BAT-500 in Manchester stores: 2,400 on hand. Well formed, and invented. The real figure, 5,400, was in its training text three times.
>
> Qwen went through the same steps at vast scale: up to 18 trillion tokens of pretraining, over a million instruction examples, then preference tuning. Its weights were frozen at its release, on 19 September 2024. Emma asked on 26 October 2026.

### `s9_fix`: Why it made the number up, and what fixes it (section 9)

**Shots.** Arcs from the "1" back over all 104 positions (real averaged attention), only the date's digits are numbers; the 23 green fact tiles drop into the prompt; the new answer reads 5,400 (5 at 75.7%); block 10 head 13 puts 76.6% on the fact's 5,400; two sockets: Knowledge (Lecture 3) and Tools (Lecture 4).

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> So why did the model say 100? Trace the first digit back. When it wrote the one, it was looking back over 104 tokens.
>
> The only digits among them are the date: 26 October 2026. Nothing in the input carried Northbridge's stock. So the model did what it was trained to do. It wrote a plausible number.
>
> Now add one line to the prompt, straight from Ledgerline. BAT-500 at Manchester main stores: 5,400 on hand.
>
> Same model, same question. This time the answer is 5,400. As it writes the five, block 10, head 13, puts 77 percent of its weight on the five tokens of that number.
>
> The fix is not a bigger brain. It is the right facts, in front of it. Lecture 3 gives the model knowledge. Lecture 4 gives it tools.

## Credits
- Dr. Rajat Dandekar, Vizuara: Agentic Systems Engineering, Lecture 2.
- Narration: ElevenLabs, voice "Daniel".
- Music: "Tried-And-True" by Imprismed, licensed from Epidemic Sound (not redistributed in the repo).
- Model: Qwen2.5-0.5B-Instruct (Apache 2.0), revision 7ae557604adf67be50417f59c2c2f167def9a775, recorded on Modal.
- Rendering: Blender 4.2.3 Cycles on Modal; composite with Pillow and ffmpeg on Modal.

## Known rough edges
- All eleven films were re-composited on Sat 31 Oct, 05:00 IST, with the series label rule (hero words on tile faces; no truncated or overlapping labels), one music bed level, two-pass loudness (-16.1 LUFS) and the s4 poster at the 65.2% moment. No re-render was needed.
- Webm copies of s2, s3, s4, s5, s6, s8 and qkv are 25 to 26.5 MB, just over the 25 MB guideline. The mp4s are all under 25 MB.
- s3: the narration names four of battery's neighbours (batteries, lithium, capacitor, charger); the screen shows the real top 6, which also include Batter and recharge.
- s8: the big stack's weight cells are an illustrative pattern (labelled); the tiny GPT numbers are real.
- s6: the vocabulary rack is schematic: the 151,936 rows are stated, not drawn one by one. Probabilities between the recorded temperatures are interpolated while the dial turns.
