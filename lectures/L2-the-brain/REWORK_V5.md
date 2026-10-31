# Lecture 2, rework v5 (Rajat's fourth review, Sat 31 Oct 2026, 17:20 IST). Class: Sun 1 Nov, 07:00 IST

**Hard deadline:** every film must be in `films/` by **03:00 IST Sun 1 Nov**. If a film cannot be finished properly, say so; the old film stays.

## Rajat's points (summarised)
1. **Questions.**
   - The question before each film is the section's own question (for example "What does a language model actually do?"). Rajat takes the class's answers, then plays the film to explain.
   - After every film come 1–3 **technical check questions** about the architecture (for example "How many heads does each block have?"), so he can tell whether the class understood the film.
2. **Tokens.**
   - Teach BPE by first showing the two extremes (letter by letter, and whole words), then BPE as the answer.
   - Embed Tiktokenizer live.
   - Show how language changes the token count, comprehensively.
3. **The film on blocks and heads.**
   - It must show the tokens: Emma's ~100 tokens, as words, moving through the assembly.
   - It must make clear whether all tokens are changed, or only the one being predicted.
   - This is the key film for putting the parts together.
4. **Heads get their own focus.**
   - The blocks section explains heads intuitively.
   - The attention-inside-the-model film starts with what heads are for, then shows what each real head does.
5. **No more 3 films back to back.** "Why is the film on 24 blocks needed now, is that repetition?" Decision: `structure` + `s5_blocks` merge into one film, **`blocks`**. `s4_attention` becomes **`heads`**. The two films are separated by slides and questions.
6. **Film 6** is renamed to a technical name and made much better and clearer. It opens with a short recap of what we have learnt so far (text → tokens → vectors → 24 blocks → the last vector), then shows how the next token is predicted.
7. **Film 7 (the loop)** is made more comprehensive, with a better flow. Its name becomes "how the entire answer is generated".
8. **Section 8.**
   - Opens with a film of the 24 blocks and the parameters inside them, then asks "Where did these numbers come from?".
   - Explains the whole corpus and how the training data is generated (not just 4 lines).
   - `s8_weights` is significantly improved and made more comprehensive.
9. **Remove the "Explore it yourself" slide** (old 66).
10. **The whole machine (finale) comes before "why it made it up"**, and the finale is made much more comprehensive and better.
11. **The Brain Lab** moves to a clear place, after section 9.
12. **Assignment section:** Colab snippets with highlights, so Rajat can walk the class through A2.

## The new flow (deck)
| Section | Content | Film at the end |
|---|---|---|
| Opener | chat, cold runs, the model, map | `overture` |
| 1 | What does a language model do? | `s1_game` |
| 2 | Tokens: extremes → BPE → Tiktokenizer live → languages → cost | `s2_tokens` |
| 3 | Vectors | `s3_vectors` |
| 4 | Attention (QKV) | `qkv` |
| 5 | Inside the stack | 5a: one block + all tokens → **`blocks`** → checks. 5b: heads slides → **`heads`** → checks |
| 6 | From the last vector to the next token | **`next_token`** (logits and softmax) |
| 7 | How the entire answer is generated | **`generation`** |
| 8 | Where the weights came from | opener film **`params`** ("494 million numbers") → corpus, training data, training → **`s8_weights`** (rebuilt) |
| Finale | **`finale`** (rebuilt): the whole machine, ending on "100, but Ledgerline says 5,400. Why?" | |
| 9 | Why it made the number up, and what fixes it | `s9_fix` |
| Hands-on | the Brain Lab | |
| Next | two sockets, NB2, the A2 walkthrough with Colab snippets, the next lecture | |

## Films to build (shared rules: FILM_STYLE.md and films/FILMS.md)
- **Ownership.**
  - Each film's builder owns `build/scenes/<film>.py`, `build/specs/<film>.py`, any `build/kit/props_<film>.py` and its own `build/data/<film>_*.json`.
  - `build/kit/l2kit.py`, `overlay.py`, `narrate.py` and `modal_films.py` are shared. Only **add** to them (new functions or keys). Never change existing behaviour; other builders render at the same time.
- **Series look.** Use the same midnight-slate studio, the same overlay style, Daniel's voice (speed 1.08), and L1's music bed at the current level.
- **Numbers.** Every number comes from a recorded run. When you capture something new, write it to `build/data/` and say where it came from in FILMS.md.
- **Words on tiles.** Show tokens as their real words (" How", " many", " city", " e", "-b", "ike", " battery", " packs", …), not as anonymous blocks.

| Film | Replaces | Name on the slide | Length |
|---|---|---|---|
| `blocks` | structure + s5_blocks | Inside the stack: every token, 24 blocks | 2:00–2:40 |
| `heads` | s4_attention | Heads: fourteen ways of looking | 1:45–2:30 |
| `next_token` | s6_choice | From the last vector to the next token: logits and softmax | 2:00–2:40 |
| `generation` | s7_loop | Generating the whole answer, token by token | 2:00–2:40 |
| `params` | (new) | 494 million numbers | 1:00–1:30 |
| `s8_weights` | s8_weights | How the weights were learnt: training | 2:00–2:45 |
| `finale` | finale | The whole machine | 3:00–3:45 |

Keep old files until a new one is verified. Write the new files to `films/<name>.mp4|.webm|.jpg` and update FILMS.md.

## Facts to use (exact)
- **Qwen2.5-0.5B-Instruct:**
  - 24 blocks; hidden size 896; **14 query heads of 64 numbers**, sharing **2 key/value heads** (grouped-query attention: each group of 7 query heads shares one set of keys and values); MLP 896 → 4,864 → 896 (gate, up and down, SwiGLU); RMSNorm; RoPE positions.
  - Vocabulary 151,936; the embedding table is **tied** (the same 151,936 × 896 table reads tokens in and scores them out).
  - **Parameters per block:** q 896×896 + 896 bias = 803,712; k 896×128 + 128 = 114,816; v 114,816; o 896×896 = 802,816; attention total 1,836,160. MLP: gate, up and down are each 4,358,144, so 13,074,432. Two norms: 1,792. **Per block: 14,912,384**; × 24 = 357,897,216. Embedding: 136,134,656. Final norm: 896. **Total: 494,032,768.**
- **Emma's prompt** is 100 tokens (system + user + assistant header). The answer is "We currently have 100 city e-bike battery packs available in our Manchester stores." (20 tokens; the first digit "1" at 34%). Ledgerline's truth is 5,400. Data: `brain3d/trace.json`, `films/qkv_data.json`, `films/build/data/structure_data.json`.
- **In one forward pass, every block updates all 100 position vectors.** Attention lets each position mix in earlier positions (causal: never later ones); the MLP reworks each position alone. Only the **last position's** final vector is turned into the next-token scores. The other 99 matter because at every block they supply the keys and values the last position reads.
- **During generation**, the earlier positions' keys and values are kept (the KV cache), so each new token needs one new column through the 24 blocks. The new column still reads every earlier position. Generation stops at `<|im_end|>`.
- **The tiny GPT** (`experiments/logs/tinygpt.json`, `ledgerline/ledgerline/course/l2/corpus.py`):
  - Character level, 81 distinct characters, block 128, 4 layers, 4 heads, d_model 128, 830,464 parameters, 1,500 steps, batch 32, learning rate 0.002, 407.7 s on 2 CPUs.
  - The loss falls from 4.59 to 0.23 (uniform guessing would be 4.39).
  - **Corpus:** 122,069 characters, 19,537 words, dated 3 Aug–23 Oct 2026. It has three kinds of text:
    1. purchase notes, stores entries, approvals, orders and goods receipts, generated from Northbridge's seed data with a fixed random seed (the stock figures are drawn at random on purpose);
    2. short e-mails between Emma, Daniel, Luis, Aiko and Henrik;
    3. every line of Northbridge's purchase policy, supplier policy and approval matrix.
  - **The training examples:** a random 128-character window; the target is the same window shifted by one character, so every position is a "guess the next character" example.
- **Qwen's training** (Qwen2.5 Technical Report, arXiv:2412.15115): pretraining on up to 18 trillion tokens; supervised fine-tuning on over 1 million examples; then preference learning (DPO, then online GRPO-style RL). Released 19 Sep 2024.
