# Lecture 2 films (The Brain)

Thirteen narrated Blender Cycles films on Emma's question ("How many city e-bike battery packs do we have in Manchester stores?"), the same example the slides teach, run through Qwen2.5-0.5B-Instruct. Each film plays at the **end** of its section as the recap, after the theory. Every number on screen comes from a recorded run (`../brain3d/trace.json`, `qkv_data.json`, `../experiments/logs/`).

Embed with `<video controls preload="metadata" poster="films/<name>.jpg">` and two `<source>` lines (`.webm` first, then `.mp4`). Never autoplay. Files: `films/<name>.mp4` (H.264, faststart), `films/<name>.webm` (VP9 + Opus) and `films/<name>.jpg` (poster). All are 1920x1080 at 30 fps, mixed to -16 LUFS integrated, true peak about -1.5 dBFS.

| Base name | Plays at the end of section | Duration | mp4 | webm |
|---|---|---|---|---|
| `overture` | lecture opener | 0:46 (45.9 s) | 23.6 MB | 24.8 MB |
| `s1_game` | 1 | 1:22 (82.5 s) | 24.2 MB | 24.5 MB |
| `s2_tokens` | 2 | 1:34 (93.9 s) | 24.1 MB | 25.6 MB |
| `s3_vectors` | 3 | 1:22 (82.5 s) | 24.0 MB | 25.6 MB |
| `qkv` | 4 (end): attention, the mechanism | 2:26 (146.5 s) | 24.3 MB | 25.8 MB |
| `structure` | 5 (start): 24 blocks, 14 heads | 1:19 (79.0 s) | 23.7 MB | 26.3 MB |
| `s4_attention` | 5: what the real heads look at | 1:26 (86.3 s) | 24.1 MB | 25.2 MB |
| `s5_blocks` | 5 (end) | 1:13 (72.6 s) | 24.2 MB | 24.7 MB |
| `blocks` | 5a (end): inside the stack, every token, 24 blocks (replaces `structure` + `s5_blocks`, 31 Oct) | 2:39 (158.9 s) | 24.2 MB | 23.5 MB |
| `heads` | 5b (end): heads, fourteen ways of looking (replaces `s4_attention`, 31 Oct) | 2:10 (130.2 s) | 24.1 MB | 23.3 MB |
| `s6_choice` | 6 | 1:14 (73.6 s) | 23.8 MB | 25.3 MB |
| `s7_loop` | 7 | 1:15 (74.6 s) | 24.0 MB | 23.7 MB |
| `next_token` | 6: from the last vector to the next token (replaces `s6_choice`, 31 Oct) | 2:40 (160.0 s) | 24.0 MB | 23.5 MB |
| `generation` | 7: the whole answer, token by token (replaces `s7_loop`, 31 Oct) | 2:27 (146.5 s) | 24.2 MB | 23.4 MB |
| `params` | 8 (opener): 494 million numbers | 1:35 (95.4 s) | 24.0 MB | 23.1 MB |
| `s8_weights` | 8: how the weights were learnt (rebuilt 31 Oct) | 2:51 (170.9 s) | 24.2 MB | 23.5 MB |
| `s9_fix` | 9 | 1:13 (72.7 s) | 24.0 MB | 24.7 MB |
| `finale` | after section 8, before section 9: the whole machine (v5, 31 Oct) | 3:42 (221.8 s) | 29.8 MB | 28.4 MB |

## Look and sound (one series)

- **World:** one shared kit, `build/kit/l2kit.py`. It is a "midnight slate" studio: a deep blue-grey sweep graded to black, one big soft key, a cool rim light, a low warm fill, and lights hidden from reflections. The set has a dark graphite plinth with an aluminium trim and ceramic token tiles with smoked-glass faces and role bands (sky for Emma, slate for system, warm grey for chat markers).
- **Props:** vectors are dark-glass plates in machined frames whose cells glow with the real values (query sky, key violet, value warm white). Glass columns fill with light to show scores and weights. Light beams and arcs carry attention. The model is a 24-floor block stack with 14 head modules per floor. Rendered on Modal (L40S, Cycles, 96 samples, OIDN).
- **Text:** all readable text is a 2D overlay in Google Sans Flex / Google Sans Code (`build/overlay.py`): dark-glass pinned cards, formula chips, typed titles, subtitles and an end card. Hero tokens carry their word on the tile face; small labels appear only on tiles at least ~40 px wide, never overlap, and are never truncated.
- **Sound:** narration by ElevenLabs Daniel (`onwK4e9ZLuTAKqWW03F9`, eleven_multilingual_v2, speed 1.08). The music bed is L1's track, "Observatory" by Out To The World (Epidemic Sound), in every film (Rajat, 31 Oct). `overlay.mix_audio` levels it against the voice: about 26 dB under the narration while Daniel speaks and 22 dB under in the gaps, with 0.4 s ramps. The whole mix is then two-pass loudness-normalised to -16 LUFS. The file lives in `films/music/`, which is gitignored. A designed SFX set (`build/sfx/`, ElevenLabs sound generation) adds tile, rise, beam, fill, chime, tick, bloom, merge, resolve and whoosh sounds.

## How to rebuild
```sh
cd lectures/L2-the-brain/films/build
python3 narrate.py <film>                                   # narration + timeline (light HTTP)
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::style --film <film> --frames 300,900 --tag t1   # style stills with overlays
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::full --film <film>   # build + render on L40S (add --resume to keep chunks)
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::comp --film <film>   # overlays + mix + mp4/webm/jpg -> films/
```
The Modal volume is `video-ad-edit:/l2films` in workspace rajatworkspace. Scenes are `build/scenes/<film>.py`, overlay and SFX specs `build/specs/<film>.py`, film-specific props `build/kit/props_*.py`. Long renders can run detached, so the laptop can let go: `modal run --detach modal_films.py::full_spawn --film <film>` (poll with `::full_poll --call-id <id>`); `::patch_spawn --film <film> --starts 1752,1776` re-renders only the given 24-frame chunks and re-concatenates the plate; `::webm_fit --film <film> --mb 24` re-encodes the webm (VP9 two-pass) from the composited mp4 to fit a size. The `params` and `s8_weights` data come from `MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_params.py` (Modal CPU), then `python3 films/build/make_s8_data.py` (stdlib). The q/k/v data comes from `/Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/capture_trace.py --film-qkv 1`, which writes only `films/qkv_data.json`; trace.json is untouched.

The `next_token` and `generation` data come from `MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run films/build/capture_next_gen.py` (and `::extra` for the table rows and per-block attention), Modal CPU, writing `build/data/next_token_data.json`, `next_token_rows.json`, `generation_data.json` and `generation_attn.json`. After `narrate.py`, run `python3 films/build/tidy_cues.py <film>` for these two films: it merges subtitle sentences spoken less than 0.55 s apart (or ends the earlier one sooner), so two subtitles never sit on screen together; the words and visual timings are untouched. `::restill --film <film> --frames ...` re-composites stills already on the volume after a spec-only change (no GPU).

## The films

### `overture`: The Brain (lecture opener)

**Shots.** Emma's question lights tile by tile on the strip; a slow pass over the 24-floor stack as it runs; the ember "100" lands beside the green Ledgerline plaque "5,400".

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> One question. How many city e-bike battery packs do we have in Manchester stores?
>
> One hundred tokens go in. Twenty-four blocks of a real language model read them all, in one pass, and at the end one token is chosen, from 151,936. Then the pass runs again, for the next token.
>
> And out comes a confident answer: 100. The truth is 5,400. Today we open the machine, and find out where that number came from.

### `s1_game`: Next-token prediction (section 1)

**Shots.** Sealed model enclosure (24-floor stack seen through a frosted window) fed by the 100-tile strip; next-token glass columns on a tray (We 56.4, As 7.9, Manchester 6.1, In 5.3, Our 4.2, At 2.8); the "We" tile flies to the strip, " currently", " have", " " join; digit columns (1 33.6, 2 20.8, 5 11.6, 3 11.3, 4 8.8, 6 4.4); the enclosure opens and the stack glows.

**Numbers from.** brain3d/trace.json (and experiments/logs where named); every on-screen number was checked against it.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Here is the whole idea of a language model. Text goes in, and the model predicts the next token.
>
> It reads Emma's question, with the app's instructions in front: 100 tokens, in one pass. At the end of that pass, it gives a probability to every entry in its vocabulary, all 151,936. The top of the list looks like this.
>
> We: 56 percent. As: 8. Manchester: 6. In: 5. The model is not certain. It is placing bets.
>
> One token is chosen and added to the text. Then the whole pass runs again, once for every new token. A few tokens later, the answer reaches its number. Now the bets are on a digit. One: 34 percent. Two: 21. Five: 12.
>
> Nothing here looks anything up. Every word of the answer, the number too, is a bet like this one. The rest of the lecture opens the box, to see how the bets are made.

### `s2_tokens`: What you send, cut into tokens (section 2)

**Shots.** The question as one bar cut by a light blade into 15 tiles with ids; the chat as 100 tiles (72 system, 15 Emma, 13 markers); macros on Manchester (19361), North+bridge (4787, 13709), 5,400 as 5 , 4 0 0 (ids 20 11 19 15 15); the hand BPE run from bpe.json (battery and packs fusing, 86 to 36 tokens); the vocabulary: 151,643 pieces plus 22 special tokens = 151,665, one row each in the model's table.

**Numbers from.** brain3d/trace.json (tokens, number_cuts); experiments/logs/bpe.json (hand BPE run); films/qkv_data.json vocab block (151,643 BPE pieces + 22 special = 151,665; the film shows only these).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Last section, text went in. But a model never sees letters. It sees tokens: pieces of text, each with a number.
>
> Emma's chat is cut into 100 tiles. 72 for the app's instructions, 15 for her question, and 13 for the markers that say who is speaking.
>
> Common words are one tile each. Manchester is one token, number 19361. Northbridge is two: North, bridge. And a number is cut digit by digit. 5,400 becomes five tokens: five, comma, four, zero, zero.
>
> Where do the pieces come from? From byte pair encoding. Start with single bytes, then keep merging the pair that appears most often in a huge pile of text. Qwen's tokenizer learned 151,643 pieces this way.
>
> Add 22 special tokens, like the markers in Emma's chat, and the tokenizer knows 151,665 pieces. The model keeps one row in its table for each.
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

### `qkv`: Query, key and value (section 4 (end): attention, the mechanism)

**Shots.** b1 dolly along Emma's tokens to the last token (it lights); b2 query, key and value plates rise from every tile; b3 the last token's 896-number vector through three machined matrices W_Q, W_K, W_V prints q, k, v (64 numbers each); b4 the query plate turns to face the keys and beams go out to all 100 keys; macro: query and Manchester's key open like a book, cells light pair by pair, the glass column follows the real running sum of q_i x k_i to 62.5; every column fills to its dot product; b5 scores (divided by 8): Manchester 7.81, Manchester in the system prompt 5.44, stores 4.54, battery 1.36; b6 softmax reallocates the light (65.2%, 6.1%, 3.9%, 2.5%); b7 the weighted values slide into one bright output plate; b8 the new vector drops back into the last token's tile and a light arc ties it to Manchester. No blocks, heads or positions are named (Rajat, 31 Oct): it is "one attention unit" (recorded: block 24, head 2).

**Numbers from.** films/qkv_data.json (capture_trace.py --film-qkv 1 on Modal CPU: q, k, v of block 24 head 2 recomputed from the block's projections and rotary embedding; softmax(q·k/8) matches the model's own attention to 1.2e-7; vocab sizes from the tokenizer and config); brain3d/trace.json (tokens, roles).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Emma's question is now a row of 100 tokens. The last one sits at the very end, where the answer is about to begin. Before the model writes a word, this last token has to find out which earlier tokens matter.
>
> Attention gives every token three new vectors. A query: what am I looking for? A key: what do I contain? And a value: what I will pass on, if I am chosen.
>
> All three are made from the token's own vector, by three learned matrices. In this attention unit, each one is 64 numbers long.
>
> Now the last token sends out its query, to every key in the row, its own included. Multiply query and key, number by number, and add it all up. That is a dot product: one score per token. When the two point the same way, the score is high.
>
> Divided by 8, the square root of 64, the scores come out like this. Manchester, in Emma's question: 7.8. The Manchester in the system prompt: 5.4. Stores: 4.5. And battery, only 1.4. This attention unit is looking for a place, not an item.
>
> Softmax turns the scores into weights that add up to one. Every lead is magnified: 2.4 points ahead becomes ten times the weight. Manchester now takes 65 percent. The other 99 tokens share the rest.
>
> Then the values. Each one steps forward, scaled by its weight. Manchester, at almost full strength. The rest, faint. Added together, they make one new vector of 64 numbers.
>
> That new vector goes back to the last token, which now carries what it found: mostly, what Manchester means in this sentence. The query asks, the keys answer, and the values are mixed by how well they matched. That is attention.

### `structure`: Inside the model: 24 blocks (section 5 (start): 24 blocks, 14 heads)

**Shots.** The 24-floor block stack (494,032,768 parameters); one block close up: the attention bay with 14 head modules side by side, then the feed-forward bay (896 to 4,864 to 896); Emma's 100 tokens enter at the bottom as a row of real vector cells (first 16 of 896 per token, recorded after every block in build/data/structure_data.json by build/capture_structure.py), come out changed, and climb all 24 blocks; ends on "next, what the heads look at".

**Numbers from.** brain3d/trace.json, films/qkv_data.json and build/data/structure_data.json; every on-screen number was checked against them.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> This is the inside of the model: a stack of 24 blocks, one on top of another, all built the same way.
>
> Each block has two parts. The first is attention, made of 14 heads working side by side. Each head lets a token look back at the tokens before it.
>
> The second part is the feed-forward network, 4,864 numbers wide. It works on each token's vector by itself, without looking at the others.
>
> Now send in Emma's question. All 100 tokens enter at the bottom, each one a vector of 896 numbers. In every block, attention lets each token gather from the ones before it, then the feed-forward part reworks each vector on its own. All 100 vectors come out changed, and climb to the next block.
>
> After 24 blocks, the vectors reach the top. Next, we open attention, and see what the heads look at.

### `s4_attention`: Attention: tokens look back (section 5: what the real heads look at)

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

### `s5_blocks`: A block, then 24 of them (section 5 (end))

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

### `next_token`: From the last vector to the next token: logits and softmax (section 6; replaces `s6_choice`)

**Shots.** Recap on the plinth: Emma's 100 tiles light in reading order, each grows its vector column (the first 16 of 896 numbers per token), the columns change block by block 1 to 24 (the real residual stream after every block), then only the last position's column stays lit and lifts. It flies into the full 896-cell plate (its values before the final norm) and passes through the RMSNorm unit (a frosted tunnel), leaving with its normed values (RMS 1.89; 896 gains, average 7.1). The tied table as a rack of 42 glass trays, each glowing with a real row; the sweep lights every row; the "We" tray slides out and stands beside the vector; both re-light cell by cell while a glass meter and a running-sum card follow the real cumulative sum to 20.84 (532 products push up, 364 pull down). The input side: a "We" tile beams into the same row ("In: a token reads its row", section 3) while the vector beams into the other side ("Out: the vector scores every row"): tied weights, 151,936 x 896 = 136,134,656 numbers. A histogram of all 151,936 logits (64 bins, log heights; average -1.13; the 5 rows above 18 glow). Seven glass meters (We, As, Manchester, In, Our, At, all others): the logits (20.84 ... 17.85), then e^logit (1.13 bn, 158 m, 123 m, ...), then divided by the sum over all rows (1,997,922,705): 56.4%, 7.9%, 6.1%, 5.3%, 4.2%, 2.8%, others 17.3%. Greedy takes We. A weighted wheel (13 sectors at T = 1: the top 12 tokens and 151,924 others) spins five times to the five real draws: As, City, We, We, We; in 1,000 draws We came up 582 times (As 78, Manchester 68). The temperature dial 0.7 / 1.2 / 0 with exact probabilities (We 81.7% / 40.9% / 100%). A "We" tile rises, and lands at position 100 at the end of Emma's text; the last 40 columns light again. A step tracker (1 RMSNorm, 2 Score every row, 3 Logits, 4 Softmax, 5 Pick one) sits top right from the norm onward.

**Numbers from.** `build/data/next_token_data.json` and `build/data/next_token_rows.json` (`build/capture_next_gen.py` on Modal CPU, the same float32 eager forward pass as `brain3d/trace.json`, the prompt tokens asserted equal): the last position's vector before and after `model.norm`, RMS and gains, the 151,936 logits recomputed as table x normed vector (max difference to the model's own logits 1.0e-5; `lm_head.weight` is the same tensor as `embed_tokens.weight`), the histogram, e^logit and their sum in float64, the We row's running sum every 32 products, 1,000 `torch.multinomial` draws per temperature and the first five single draws (seed 0); the tray rows are real table rows (the top 6 tokens and 36 evenly spaced ids). Temperatures: `brain3d/trace.json` final.dial_last (exact at 0.7, 1.0, 1.2; interpolated while the dial turns). Recap columns: `build/data/structure_data.json`.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> So far: Emma's text became 100 tokens. Each token became a vector of 896 numbers. 24 blocks updated every vector, in one pass. And we keep just one: the last position's final vector.
>
> Now: how does that vector become the next token?
>
> First, a final RMSNorm. It divides all 896 numbers by their root mean square, here 1.89, then multiplies each by a learned gain. Same direction, fixed scale.
>
> Then, scoring. The model's table has one row per token: 151,936 rows of 896 numbers. Multiply the vector with a row, number by number, and add it up: one dot product, one score. For We, it comes to 20.84.
>
> And this table? We have met it before. It is the embedding table from section 3. The same table that reads tokens in now scores them on the way out: tied weights.
>
> That gives one score per row, called a logit. Only five pass 18. We: 20.84. As: 18.88. Manchester: 18.62.
>
> Softmax turns them into probabilities. Raise e to each logit: for We, 1.13 billion. Divide by the sum over every row: 2.0 billion. We gets 56 percent. As, 8. Manchester, 6. All together, one.
>
> Then one token is picked. Greedy takes the top one: We, every time. Sampling spins a weighted wheel. Five real spins: As. City. We. We. We. In a thousand spins, We wins 582.
>
> Temperature divides the logits first. At 0.7, the gaps grow: We rises to 82 percent. At 1.2, they shrink: We falls to 41. And temperature zero is greedy.
>
> Our run is greedy, so the choice is We. It joins the end of the text, and the whole machine runs again.

### `generation`: Generating the whole answer, token by token (section 7; replaces `s7_loop`)

**Shots.** "We" lands at position 100 and a pass sweeps the row (the input is now 101 tokens). A glass wall stands after position 100 ("never forward") and a ribbon of light shows where position 100 looks back (its real attention, averaged over heads and blocks). Behind every prompt position a slender glass stack rises: its KV cache, 24 floors (violet = keys, warm = values), lit floor by floor; one floor of one position = 256 numbers (2 KV heads x 64 x key + value); 100 x 24 x 256 = 614,400. The hero pass: one new column climbs position 100's stack floor by floor while, at every floor, a ribbon reaches back over all 101 positions, its brightness the real attention of that block (14 heads averaged). Then the answer grows tile by tile on the spoken word (currently 47.6%, have 79.6%, space 52.5%), each preceded by the previous position's stack building: one pass, one new column. The digits are ember: the column that chose "1" (33.6%) is opened at blocks 21-24 (logit lens 4, 4, 5, then 1); then 0 (32.2%) and 0 (54.2%). The rest lands quickly; the last tile, `<|im_end|>` (83.8%), gets no column: generation stops there. At "Twenty tokens", a card spells the answer as its 20 tokens. A progress counter (top right) shows "token k of 20", the next pass's input length (101 ... 119) and 20 slots. Then five temperature-0.7 samples (300, 150, over 1,000, 50, 15) on a stepped riser beside the green Ledgerline plaque (5,400); the close pulls back over the whole lit row: one machine, 494,032,768 weights, run once per token; "Where did the weights come from?"

**Numbers from.** `brain3d/trace.json` (generation.greedy, logit_lens.digits, generation.samples_t07, facts.truth, model_card); `build/data/generation_data.json` and `build/data/generation_attn.json` (`build/capture_next_gen.py`): the KV cache after the prompt is 24 layers x [1, 2, 100, 64] for keys and the same for values; the 20 greedy steps re-run one token at a time with the cache reproduce trace.json's tokens exactly, and every step's logits match a full recompute without the cache to within 2.4e-5; the per-block attention of each new column over all earlier positions.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> We joins the end of the text. The input is now 101 tokens, and the pass runs again, for token number two.
>
> Does the model redo all 101 columns? No. A position only looks back, never forward. So adding We changes nothing in the 100 columns before it.
>
> Their keys and values, in all 24 blocks, are already computed, so the model keeps them: the KV cache. 256 numbers per position, per block. 614,400 for Emma's prompt.
>
> So each new token needs just one new column, climbing the 24 blocks. But in every block, its query still reads the keys and values of all 101 positions, its own included.
>
> Out comes currently, at 48 percent. Its keys and values join the cache, and the next column climbs. Have: 80 percent. A space: 52.
>
> Then the number. The first digit is one, at just 34 percent. Two had 21. Look inside: blocks 21 and 22 lean to four. Block 23 says five. Only block 24 settles on one. Then zero, 32 percent. And zero, 54.
>
> City. E-bike. Battery packs. Available in our Manchester stores. A full stop. Then a special token, im_end, at 84 percent. It means: stop. Twenty tokens, twenty passes.
>
> Sample five more runs at temperature 0.7, and the bets land differently. 300. 150. Over 1,000. 50. 15. Ledgerline says 5,400.
>
> Every token was a bet, made by the same machine, run once per token. And every bet came from its weights: 494 million numbers. Where did they come from?

### `params`: 494 million numbers (section 8 opener, 1:35)

**Shots.** The 24-floor block stack (the series' block tower) lights floor by floor. The top block lifts out and lands on a stage, and its weight matrices rise out of it as glass sheets at their real shapes (0.25 m = 896 numbers; rows x columns as stored): q and o 896 x 896, k and v 128 x 896 (thin strips), gate and up 4,864 x 896 (tall pillars), down 896 x 4,864, and the two norms as thin rods. Every sheet's face is **block 24's real weights, one cell per weight** (sky = positive, violet = negative). A counter tallies word by word: q 803,712 (with bias), o 802,816, k and v 114,816 each (with bias) = 1,836,160 for attention; gate, up and down 4,358,144 each; two norms 1,792; **14,912,384 per block**; x 24 = 357,897,216 (every floor flashes); the embedding table 151,936 x 896 = 136,134,656 as a 42 m glass runway (row-binned real values); the final norm 896; **494,032,768**. A macro zoom into the q sheet's top-left corner until single cells fill the frame, each labelled with its real value (-0.0031, -0.0076, 0.0104 ... ringed as they are spoken). It ends on the stack and the gallery under the typed question "Every answer came from these numbers. Who chose them?"

**Numbers from.** `build/data/params_data.json`, written by `build/capture_params.py` (Modal CPU, transformers 4.46.3, the trace's revision): every tensor's shape and count, checked against 494,032,768 and the per-block 14,912,384; block 24's q_proj [0:6, 0:6] and bias [0:6]. The sheet images (one pixel per real weight) and the embedding image (RMS of each 64-row bin) are on the Modal volume, `video-ad-edit:/l2films/data/params/`, written by the same script.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> This is the model we have been opening: 24 blocks, one on top of another. Every block is full of numbers. Let's count them.
>
> Lift out the top block, and lay out what is inside. Each glass sheet is one weight matrix, at its real shape.
>
> Attention first. The query and output matrices are 896 by 896. Keys and values are thin, 896 by 128, because the fourteen heads share them.
>
> Then the feed-forward part: gate, up and down, each 896 by 4,864. They hold most of the block. One block: almost 15 million numbers.
>
> Times 24 blocks: 358 million. Add the embedding table, a row for every token in the vocabulary: 136 million more. In all, 494 million numbers.
>
> Look closer. Every cell is one number. The corner of block 24's query matrix: -0.0031, -0.0076, 0.0104.
>
> Every answer came from these numbers. Who chose them?

### `s8_weights`: How the weights were learnt: training (section 8, rebuilt 31 Oct, 2:51)

**Shots.** Step by step on the tiny GPT and its real run.
1. *The corpus.* Three trays of document cards (card counts in proportion to their characters): generated notes 90,178 characters (700 entries), e-mails 7,818 (10 e-mails, each 3 times), policy lines 22,218 (99 lines, each twice), each with real snippets on screen. Shuffled together they light a 31 m strip of cells, one per real character of the corpus (colour = kind of text, brightest = digits).
2. *The training examples.* A bracket cuts the real window from the first training batch (128 characters from character 94,685: "026: BAT-375 in Leeds stores, 4,600 on hand, ..."). The input bar and the target bar (shifted by one) rise from the strip, and the characters are shown as 2D cells. Position 39 ("...4,600 on " -> h) is highlighted. The real batch of 32 windows stands up behind.
3. *One step.* The batch enters the 4-floor tiny GPT. 81 glass meters show the untrained model's real probabilities for the next character at that position (h 1.6%, in green; scale 0-5%). A loss gauge: -log 0.0164 = 4.11, with a ring at even guessing, 4.39. A real 8 x 16 patch of block 1's qkv weight matrix shows its values, then the real step-1 update direction (the negative gradient), then the step (one weight -0.029162 -> -0.029142 at the warm-up learning rate 0.00002; the peak is 0.002).
4. *Repeat.* The real loss curve (4.59 -> 2.22 at step 100 -> 0.23 at 1,500) as a glowing ribbon, with a step counter. The patch turns into its values after training. The meters refill with the trained model's probabilities (h 99.99%, scale 0-100%). The real untrained sample (noise) and the trained sample are shown.
5. *The result.* Ten slips with the ten real sampled figures (2,400 2,800 2,100 1,800 4,000 3,700 2,500 1,500 2,400 4,500); the green plaque 5,400 ("Manchester stores has 5,400", 3 times in the corpus, in Emma's e-mail); 0 of 10 say 5,400.
6. *Qwen at scale.* The 24-floor stack, three stage sockets (up to 18 trillion tokens; over 1 million examples; preference learning), and calendar blocks 19 Sep 2024 and 26 Oct 2026.

**Numbers from.** `experiments/logs/tinygpt.json` (curve, samples, stock figures, config); `build/data/s8_weights_data.json`, written by `build/make_s8_data.py` (stdlib) from the corpus generator `ledgerline/ledgerline/course/l2/corpus.py` (seed 7; checked byte for byte against northbridge_corpus.md) and from `build/data/s8_weights_tiny.json`. That file comes from `capture_params.py --only tiny`, which re-ran tinygpt.train on Modal CPU (same corpus, seed 1337 and settings). Its loss curve matches the log exactly at all 16 points (asserted). It adds the first batch, the per-position probabilities before and after training, the weight patch and its step-1 gradient. `brain3d/trace.json` training (Qwen2.5 Technical Report, arXiv:2412.15115). Nothing is illustrative.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Our tiny GPT learns from one pile of text: Northbridge's own documents. 122,069 characters, dated 3 August to 23 October.
>
> Three kinds of text. Most is generated from Northbridge's seed data: notes, stores entries and orders, with stock figures drawn at random, on purpose. Then e-mails between the staff. Then every line of its purchase policies. All shuffled together.
>
> Then, cut a random window of 128 characters. The target is the same window, shifted by one. So every character is a test: guess the next one. A batch takes 32 windows.
>
> One training step. At every position, the model gives a probability to each of its 81 characters. Here it has read 4,600 on, and must guess h. Untrained, it gives h 1.6 percent.
>
> The loss measures the miss: minus the log of the probability of the right character. Here, 4.11. Guessing evenly would score 4.39.
>
> The gradient says which way to move each of the 830,464 weights, so the right characters get more probability. Every weight takes a small step that way, at a learning rate of at most 0.002.
>
> Repeat that 1,500 times, with a fresh batch each time. The loss falls from 4.59 to 0.23. The h now gets more than 99.99 percent. Before training, the model wrote noise. After, it writes Northbridge.
>
> Ask it for BAT-500 in Manchester stores. Ten tries, ten perfect stock lines: 2,400 on hand. 2,800. 2,100. All invented. The real 5,400 was in its text three times. It learnt the pattern, not the number.
>
> Qwen learnt the same way, at vast scale: the same game on up to 18 trillion tokens, then instruction tuning on over a million examples, then preference learning. Its weights froze at release, on 19 September 2024. Emma asked on 26 October 2026.

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

### `finale`: The whole machine (v5; plays after section 8, before section 9)

Rebuilt 31 Oct (Rajat's 4th review: "make the film on whole machine much more comprehensive and better", and it now comes before "why it made it up"). One continuous camera journey of Emma's question through the entire model, in nine stages. Each stage opens with a typed chapter label ("Stage n of 9"), and a progress strip of the nine stages runs along the bottom edge under the subtitles (1 Tokens, 2 Vectors, 3 Block 1, 4 Heads, 5 24 blocks, 6 Next token, 7 The loop, 8 The number, 9 Why?). It ends on the open question; the fix is left to `s9_fix`.

**Shots.**
1. *Tokens.* Emma's chat appears as a 2D panel (system, user, the assistant header), is cut into 100 token chips with their real words and ids (the date digits 2 6 / 2 0 2 6 and Manchester 19361 highlighted), and the chips fly down into 100 tiles on the plinth.
2. *Vectors.* Each tile reaches back to the embedding table (a 36 m rack of slats behind the strip; schematic, 151,936 rows stated), a row lights and a column of all 896 real input-embedding numbers (16 x 56 cells) stands behind the tile. Close on Manchester's column.
3. *Block 1.* The 100 columns stream into the 24-floor stack as one row (first 16 numbers of each, real); light bars for query, key and value; light arcs with block 1's real attention, averaged over its 14 heads, from the last position, " Manchester" and " battery" back to earlier positions (the last position: 12.7% on "assistant", 11.2% on itself); the MLP bay lights and the row comes out changed (real values after block 1).
4. *Heads.* The 14 head modules of a block light one by one; back on the strip, block 24 head 2's real weights as arcs (65.2% on Manchester, 6.1% on the system prompt's Manchester), then block 12 head 13 sends 100% of its weight 99 positions back to the first tile.
5. *24 blocks.* The row climbs all 24 floors, swapping to the real values after each block; the KV-cache shelves beside the stack (one per block, keys violet, values warm) fill with 100 slots each; the whole stack with 494,032,768 and the per-block breakdown (14,912,384 x 24 = 357,897,216, + embedding 136,134,656, + final norm 896), recalling section 8.
6. *Next token.* The last column (its real 896 numbers after block 24) leaves the top, comes down to the same table and sweeps it; six glass meters rise (We 56.4, As 7.9, Manchester 6.1, In 5.3, Our 4.2, At 2.8%); the "We" tile drops onto the strip.
7. *The loop.* We's own column (its real input embedding) climbs the stack alone while each block's cache shelf gains one slot and flashes as it is read; " currently", " have", " " drop, each with a pass up the stack and one more cache slot per block.
8. *The number.* The ember digits 1 (33.6%, then 2 20.8% and 5 11.6%), 0 (32.2%), 0 (54.2%); the rest of the answer drops on its spoken words to <|im_end|> (83.8%), typed in a 2D "answer so far" card; the stack goes quiet.
9. *Why?* A wide replay of the whole machine; the 100 against the green Ledgerline plaque (5,400); a large "Why?"; end card "Next, section 9: why it made the number up".

**Numbers from.** brain3d/trace.json (tokens and ids, prompt counts, heads.row_last for block 12 head 13, final.last, generation.greedy, facts.truth, meta); films/qkv_data.json (block 24 head 2 weights; lens_last[23], the last position after block 24); build/data/structure_data.json (first 16 numbers of every position after every block); build/data/finale_data.json (new, `build/capture_finale.py` on Modal CPU, same model, revision and prompt: the full 896-number input-embedding rows of all 100 prompt tokens and the 20 answer tokens, and block 1's attention averaged over its 14 heads). The parameter breakdown is from REWORK_V5.md and matches meta.params. The embedding rack and the KV-cache slots are schematic (no values drawn); the per-head LED levels in "each head looks in its own way" are a lighting pattern, not data.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Here is the whole machine, from start to finish, on one question. Emma asks: how many city e-bike battery packs do we have in Manchester stores?
>
> The app wraps her words in a chat: its own instructions, her question, and a header that says the assistant speaks next. The tokenizer cuts all of it into 100 tiles, each with its own number. The date is cut digit by digit. Manchester is a single tile, number 19361.
>
> Each tile looks up its row in the embedding table. The table has 151,936 rows, one for every token the model knows. Each row is 896 numbers. So every tile now stands with a column of 896 numbers behind it.
>
> The 100 columns enter block 1. First, attention. Each position makes a query, a key and a value. Its query meets the keys of the earlier positions, never the later ones, and the values of the best matches flow in. Then the MLP reworks each column on its own.
>
> Attention is not one look, but fourteen, side by side: the heads. Each head looks in its own way. In block 24, head 2 puts 65 percent of its weight on Manchester. In block 12, head 13 rests all of its weight on the very first token.
>
> Every block updates all 100 columns, not just the last one, all the way through 24 blocks. The other columns matter: at every block, they hold the keys and values the last column reads. The stack holds 494,032,768 learnt numbers, every one set in training, as we saw in section 8.
>
> At the top, only the last column speaks. It is scored against every row of the same table, all 151,936. Softmax turns the scores into probabilities. We: 56 percent. As: 8. Manchester: 6. We is chosen.
>
> We joins the row, and the machine runs again. But the 100 earlier columns are not run again. Their keys and values were kept, in the KV cache. So each new token sends just one new column through the 24 blocks, and that column still reads every position before it. Currently. Have. A space.
>
> Then the number. One, at 34 percent. Zero. Zero. Token by token, the answer grows: We currently have 100 city e-bike battery packs available in our Manchester stores. Then the end-of-turn token, and the loop stops.
>
> Every step ran exactly as it was built to. Nothing broke. And still, the answer is 100. Ledgerline, Northbridge's own record, says 5,400. So why did a machine that worked perfectly make this number up?

**Rebuild.** `python3 build/capture_finale.py` is already done (data in `build/data/finale_data.json`); `narrate.py finale`; `modal_films.py::full --film finale`; `modal_films.py::comp_as --film finale --out finale_v5` (writes `films/finale_v5.*`, so the old film stays until checked); `modal_films.py::finale_webm --film finale --out finale_v5 --kbps 780` (a webm under 30 MB). The scene imports `specs/finale.py`'s `sched(tl)`, so the 2D chips and the 3D tiles share frames.

## Rework v5 (31 Oct, evening): `blocks` and `heads`

Rajat's fourth review merged `structure` + `s5_blocks` into one film, **`blocks`**, and replaced `s4_attention` with **`heads`**. The two play in section 5, separated by slides and check questions. The old structure / s4 / s5 files stay in place but are no longer used by the deck.

| Base name | Shown as | Plays | Duration | mp4 | webm |
|---|---|---|---|---|---|
| `blocks` | Inside the stack: every token, 24 blocks | 5a (end) | 2:39 (158.9 s) | 24.2 MB | 23.5 MB |
| `heads` | Heads: fourteen ways of looking | 5b (end) | 2:10 (130.2 s) | 24.1 MB | 23.3 MB |

**New data (both films; also used by the deck).** `build/capture_heads.py` (Modal CPU, Qwen2.5-0.5B-Instruct at the trace revision, fp32, eager attention, `output_attentions`, the same 100-token prompt as brain3d/trace.json, asserted) writes:
- `build/data/heads_data.json`: every one of the 24 x 14 heads with simple, honest measures (previous-token share, first-token "rest" share, the last position's top targets and its weight on Manchester / battery / packs / stores / city, on Emma's 15 question tokens and on the date's digits, same-token-earlier and induction shares); full attention matrices for 12 heads; the digit step (prompt + "We currently have ", 104 tokens, the step that writes the first digit) with full rows for 3 heads; q / k / v and the joined head outputs at the last position (blocks 1, 12, 24); and a short `examples` list for the slides.
- `build/data/blocks_data.json`: per block and per position, how much each full 896-number vector changed (relative change, cosine in/out, size of the attention and MLP outputs); head-averaged attention matrices for blocks 1, 12, 24; the last position's full vectors entering block k, after its attention and after the block, and the 4,864 numbers inside its MLP (blocks 1, 12, 24).

`heads_data.json` examples (all positions 1-based):

| Block, head | Kind | What it does | Key numbers |
|---|---|---|---|
| 9, 7 | previous token | every position looks at the token just before it | 83.8% on the previous token (average over the 99 positions that have one) |
| 12, 13 | rest | parks all its weight on position 1 (`<|im_start|>`) | 100.0% from the last position; 100.0% on average from every position |
| 24, 2 | content word (place) | from the last position, looks at Manchester | 65.2% on Manchester (position 93); 6.1% on the Manchester in the system prompt |
| 19, 13 | content word (question) | from the last position, reads Emma's question | 80.2% on her 15 tokens; 35.6% on " stores" |
| 2, 7 | digits (the date) | at the step that writes the first digit, looks at the only digits in the prompt | 17.3% on the six digits of 26 October 2026 (8.3% on the "2" of 26) |
| 3, 2 | same token earlier (optional) | a repeated token looks at its earlier copies | 40.2% on earlier copies (average over the 29 positions whose token appeared before) |

Counts over all 336 heads: 6 previous-token heads above 50%; 14 heads put more than 90% on position 1 (142 more than 50%); from the last position, 31 heads put more than half their weight on Emma's question and 9 put more than 20% on Manchester.

### `blocks`: Inside the stack: every token, 24 blocks (section 5a)

**Shots.** Emma's 100 tokens as tiles on the plinth, her question lighting word by word (words as 2D faces on the tiles); each tile's column rises behind it (first 16 of 896 numbers, real); the stack seen as one building: 24 floors that each span all 100 positions, an attention band of 14 head lanes over an MLP band with one unit behind every position. Block 1 opens: a wave runs along the row; battery's real block-1 arcs back over the earlier positions while a frosted glass wall stops a look forward at packs; Manchester's arcs (its arc to battery in warm light); the last position's arcs over all 99. The row steps up to the MLP band; a sweep passes each column alone, and the last column's real 896 -> 4,864 -> 896 numbers widen and squeeze above it. Every column switches to block 1's output in a wipe ("100 of 100 columns changed"), then all 100 climb through 24 floors (counter "Block k of 24"). At the top the other 99 dim, the last column lifts and a beam goes up (scores for 151,936 tokens). The 99 light again: the last position's arcs (block 24 average, then block 24 head 2 at 65.2% on Manchester, then block 19 head 13 on stores); they dim on "nothing to read". The logit-lens eyepieces light floor by floor beside the 2D ladder (noise, "we" at 18, We 8.0 / 29.3 / 56.4% at 22-24); a We tile rises. All 24 x 14 head lanes light; hand-off to heads.

**Numbers from.** brain3d/trace.json (tokens, roles, counts, logit_lens.last, model_card); build/data/structure_data.json (the column cells after every block); build/data/blocks_data.json (block-1 and block-24 head-averaged rows, the last column's vectors and MLP middle layer, "100 of 100 changed" per block); build/data/heads_data.json (block 24 head 2, block 19 head 13).

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> Emma's chat is now a row of 100 tokens. First the app's instructions, then her question. How many city e-bike battery packs do we have in Manchester stores?
>
> Each token is now a column of 896 numbers. A hundred columns, side by side. This is what goes into the model.
>
> Above them stands the stack: 24 blocks, all built the same way. Let's open the first one.
>
> First, attention, with 14 heads. Every position reads the positions before it, and mixes in what it needs. Battery can read city and e-bike, but never packs. Manchester can read battery. And the last position can read all 99 before it.
>
> Then the MLP. It takes each column on its own, widens it from 896 numbers to 4,864, and squeezes it back to 896. Here, no column sees any other.
>
> Out come 100 columns, and every one of them has changed. Then all 100 climb to the next block, and it happens again. And again. All the way through block 24.
>
> At the top, the model reads out just one column: the last one. Only its 896 numbers are turned into scores for the next token.
>
> So why work on the other 99? Because in every block, the last position reads them. That is how Emma's words reach the answer. In block 24, one head puts 65 percent of its weight on Manchester. In block 19, another reads stores. Without those columns, there would be nothing to read.
>
> Can we watch the answer form? Ask the last column early, after each block: what would you say now? For 17 blocks, noise. At block 18, a lowercase we. From block 22, We leads: 8 percent, then 29, then 56.
>
> Every block reads the row with 14 heads. Next: what each of those heads looks for.

### `heads`: Heads: fourteen ways of looking (section 5b)

**Shots.** One head module above the last token sends block 24 head 2's real arcs: thick to Manchester (65.2%), almost nothing to battery (0.1%). The last token's real 896-number query (block 24) rises from its vector, light blades cut it into 14 slices of 64, the slices fan out, and each sends one arc to its own strongest target (real, block 24). Two key plates and two value plates (real, 2 x 64 each) appear below; 7 slices connect to each set. Then five real heads on the row of tiles, each in its own colour: block 9 head 7's short hops from every token to the one before; block 12 head 13's fountain of arcs into position 1; block 24 head 2 on Manchester; block 19 head 13 on Emma's question and " stores"; and, with "We currently have " added to the plinth, block 2 head 7's ember arcs from the step that writes the first digit back to the date's digits. Finally the 14 real head outputs (block 24, 64 each) slide together into 896, pass the output matrix and the real result lands on the last token's vector; the 24 x 14 head stack rises with the five heads lit in their colours.

**Numbers from.** build/data/heads_data.json (every weight, the query / key / value numbers, the head outputs and the output-matrix result; capture_heads.py); brain3d/trace.json (tokens, model_card). The output matrix's etched pattern is decorative; its input and output plates are real.

**Script** (subtitles; the voice reads the same sentences with the numbers spelled out):

> One attention pattern can only look one way. If it spends its weight on Manchester, little is left for battery, or for the word just before.
>
> So the model splits the job. The 896 numbers are cut into 14 heads of 64. Each head asks its own question, and all 14 run at the same time.
>
> To save memory, the heads share their keys and values. Fourteen queries, two sets of keys and values: seven heads to each set.
>
> So what do real heads do with Emma's question? Block 9, head 7, looks one step back. On average, each position puts 84 percent of its weight on the token just before it.
>
> Block 12, head 13, puts all of its weight on the very first token. It has nothing to add here, so it rests.
>
> Block 24, head 2, looks for the place. From the last position, 65 percent lands on Manchester.
>
> Block 19, head 13, reads Emma's question: 80 percent on her words, and 36 on stores.
>
> And when the model is about to write its number, block 2, head 7, looks at the only digits in the prompt: the date. 17 percent of its weight lands on the digits of 26 October 2026.
>
> Each head hands back 64 numbers. Fourteen of them, side by side, make 896 again. The output matrix mixes them into one vector, and it is added to the column.
>
> Fourteen heads in each of 24 blocks: 336 ways of looking, all in one pass.

## Credits
- Dr. Rajat Dandekar, Vizuara: Agentic Systems Engineering, Lecture 2.
- Narration: ElevenLabs, voice "Daniel".
- Music: "Observatory" by Out To The World, licensed from Epidemic Sound (not redistributed in the repo).
- Model: Qwen2.5-0.5B-Instruct (Apache 2.0), revision 7ae557604adf67be50417f59c2c2f167def9a775, recorded on Modal.
- Rendering: Blender 4.2.3 Cycles on Modal; composite with Pillow and ffmpeg on Modal.

## Known rough edges
- 31 Oct revision (Rajat's review): L1's music at a quieter level in every film; s1 retitled "Next-token prediction" and re-narrated (one pass, one token chosen, the pass repeats per token); s2 no longer mentions 1,187 x 128 or padding; qkv says "one attention unit" and never names blocks or heads; new films `structure` and `finale`; the overture's line now says one token is chosen at the end of the pass.
- All films were re-composited on Sat 31 Oct, 05:00 IST, with the series label rule (hero words on tile faces; no truncated or overlapping labels), one music bed level, two-pass loudness (-16.1 LUFS) and the s4 poster at the 65.2% moment. No re-render was needed.
- Webm copies of s2, s3, s4, s5, s6 and qkv are 25 to 26.5 MB, just over the 25 MB guideline. The mp4s are all under 25 MB.
- s3: the narration names four of battery's neighbours (batteries, lithium, capacitor, charger); the screen shows the real top 6, which also include Batter and recharge.
- s8 (rebuilt 31 Oct) and params: every number and cell is real (see their "Numbers from"). Both scenes add a far floor and a far wall and hide the studio lights from the camera, because shots that look along the set would otherwise show the end of the studio sweep. Both webms were re-encoded to fit 25 MB (`webm_fit`).
- s8: the per-example probabilities, the weight patch and its gradient come from a re-run of the tiny GPT (identical loss curve). The trained model's p(h) is 0.99998 in that run, so it is shown as 99.99% (truncated) and voiced as "more than 99.99 percent". The step counter is synced to the ribbon, not to real wall-clock steps. At 2:51 it is 6 s over the 2:45 target.
- params: the embedding runway's cells are the RMS of 64-row bins (2,374 x 896), not single rows. The stack keeps 23 floors after the top block lifts out.
- s6: the vocabulary rack is schematic: the 151,936 rows are stated, not drawn one by one. Probabilities between the recorded temperatures are interpolated while the dial turns.
- `next_token` / `generation` (31 Oct, 19:00 IST): the vocabulary is drawn as 42 real rows (trays), not 151,936; the histogram and the text carry the full count. The wheel's sectors are fixed at T = 1 (the temperature beat is shown on the meters and dial, not the wheel). The KV-cache ribbons in the hero pass are each block's real attention averaged over its 14 heads; the bright far spot is position 0 (<|im_start|>), which many heads rest on. Only the first pass (position 100) and the digit's column get the slow, detailed climb; the other columns build quickly on their words. The voice says "im end" for `<|im_end|>`. Subtitle sentences closer than 0.55 s are merged by `tidy_cues.py`. Both webms were re-fitted to 24 MB with `::webm_fit` (VP9 two-pass from the composited mp4). Token word labels on these two films are anchored to the tile tops (a `_front` anchor gets a zero tile width from `autoface` and is never drawn).
- finale v5 (31 Oct): the embedding rack is schematic (151,936 rows stated, not drawn) and its scoring sweep in stage 6 reads as a general glow more than a moving band; the KV-cache slots carry no values; the head LED levels in stage 4 are a lighting pattern. In stage 7 the stack shots are dark and the climbing column is thin. The mp4 is 29.8 MB (the 900 kbps floor in overlay.finish at 3:42); the webm was re-encoded at 780 kbps by `finale_webm` to 28.4 MB. One subtitle (stage 5) wraps with "8." alone on the second line.
- blocks / heads (v5): the webms were re-encoded from the mp4 with `webm_fit` to fit 25 MB. In `blocks` the climb from block 5 to 24 is a fast montage (about 0.3 s per block) and the logit-lens close-up is mostly the building's right-hand end; the ladder carries the numbers. Block 1's head-averaged weights are diffuse (Manchester puts only 1.5% on battery), so the film says a position *can* read every earlier one and states the real share. In `heads`, the output matrix's etched pattern is decorative (its input and output plates are real), and the 14 arcs in the split beat show each block-24 head's strongest target other than itself and position 1.
