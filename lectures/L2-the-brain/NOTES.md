# Lecture 2 · The Brain: how an LLM works · speaker notes (v4.2, Northbridge)

Sun 1 Nov 2026, 7:00–9:00 AM IST. 73 slides. Slide numbers are the deck's counter (bottom right). `[click]` = one step.

**The one idea.** We follow one sentence, Emma's question, through a real model. Every plate and every film uses that same
sentence and the same recorded run. At every part slide: "Same sentence, one more stage."

**The rhythm of every section** (Rajat, 30–31 Oct): part slide → theory plates (first principles, worked on Emma's question)
→ one question to the class about what was just taught (30 seconds, one line in the chat) → the narrated film, as the recap.
The films never autoplay: click play, or **Present** for full screen. The films replace the old per-section 3D slides; the
3D scene appears once, near the end, as "Explore it yourself".

**Time.** About 80 minutes of teaching and 13 films (about 18 minutes, plus structure and finale when they land). If time
runs short, keep overture, qkv, s8_weights and finale; the other films are recaps students can watch afterwards.

**Where the numbers come from.**
- `brain3d/trace.json`: one recorded run of Qwen2.5-0.5B-Instruct (Modal, CPU) with the app's brain-stage prompt for Emma.
- `figdata.js` (`window.L2`; every number traced in `experiments/PROVENANCE.md`): the cold-open runs of Ask Northbridge on
  gemini-3.8-flash, the fix, tokens and cost, the tiny GPT and its corpus, the cut-off, the model card.
- Token prices in US dollars ($0.50 per million tokens in, $3.00 per million out). Northbridge's own money stays in pounds.
- The attention plates' two-number example and the four-word BPE example are worked on the slide, labelled as such.

Live links: the app `https://rajatworkspace--northbridge-experience.us-east.modal.run/after?stage=brain`; the Brain Lab
(URL to come). Do not redeploy the app during class.

---

## Opening (7:00–7:10) · 1–9

**1 · Title.** "Drop your city in the chat."

**2 · Where we are.** [click] four parts; [click] the LLM box lights up. "Today, only this box."

**3 · Monday, 9:05 AM: the chat.** [click] Emma's question types itself; the recorded reply streams in: "There are currently 42 City e-bike battery packs in stock across the Manchester stores: Central Warehouse 35, Assembly Store 7." [click] "Where did that number come from?" → "the live inventory system records… updated this morning." [click] Ledgerline: **5,400**. "The number, both warehouses and the source: all made up." (Run 1 of 16, replayed.)

**4 · We asked again.** 16 runs: 42, 48, 48, 42, 42, 42, 54, 142, 48, 48, 45, 48, 48, 48, 48, 42. "0 of 16 said 5,400; every run gave a number." [click] With no system prompt at all, the model declines; the app's prompt is what pushes it to answer.

**5 · Ask the class 1: where did that number come from?** Vote 1–4; we settle it in Section 9.

**6 · Today's question.** [click] We open a small model of the same kind and watch every step.

**7 · The model we open.** Qwen2.5-0.5B-Instruct: 24 blocks, 896 numbers per token, 14 heads, about 151,000 tokens, 494 million parameters. [click] [click] Its answer: "We currently have 100 city e-bike battery packs…".

**8 · Today's map.** Next-token prediction around everything; tokens, vectors, attention, 24 blocks, probabilities, the next token, the loop; training underneath; Ledgerline with no connection.

**9 · Film: Overture** (0:41).

## 1 · Next-token prediction (7:10–7:16) · 10–13

**10 · Part: What does a language model actually do?**

**11 · Guess the next token.** Definition. [click] After Emma's question: "We" 56%, "As" 7.9%, "Manchester" 6.1%. Click "at the first digit". [click] "1" 34%, "2" 21%, "5" 12%. "It has no idea which digit."

**12 · Ask the class 2: "We" got 56%. Where did the other 44% go?** To every other token in the vocabulary: "As", "Manchester", "In"… the chances always add up to 1.

**13 · Film 1 · Next-token prediction** (s1_game, 1:18).

## 2 · Tokens (7:16–7:30) · 14–21

**14 · Part.** "Last section: it guesses the next piece. Now: what does it read?"

**15 · What the model is sent.** Two messages become one text. [click] system prompt. [click] it stops after "assistant", so the next token starts the reply.

**16 · Cut into tokens.** Emma's question is 15 tokens; "e-bike" is three; "Manchester" is one. [click] 100 tokens in all. [click] "5,400" is five tokens.

**17 · Where the pieces come from (BPE, simply).** The four-line recipe on the left. Then click once per merge, nine clicks, and say each out loud:
1. b + a (4 times: battery ×3 plus batteries ×1);
2. ba + t;
3. bat + t;
4. batt + e;
5. batte + r;
6. batter + y (3 times): "battery" is one piece;
7. p + a;
8. pa + c;
9. pac + k: "pack" is one piece.
"batteries" stays batter · i · e · s, because it is rare. "Qwen ran this recipe on a huge amount of text until it had 151,643 pieces."

**18 · The model's vocabulary.** [click ×3] 151,643 learned pieces + 22 special markers (`<|im_start|>`, `<|im_end|>` in Emma's chat) = **151,665**, the vocabulary: every token it can read or write; the id is the place in the list. Footnote, only if asked: inside the model the list has 151,936 slots; the last 271 are spare padding, so the table is 1,187 × 128.

**19 · You pay in tokens (US dollars).** 90 in, about 45 out: **$0.000179** a question, **$0.18 per 1,000**. [click] Plus 390 hidden thinking tokens: **$0.001344** a question, **$1.34 per 1,000**. [click] The same question in six languages: English 15 tokens … Greek 72.

**20 · Ask the class 3: why might 5,400 cost more tokens than "five"?** "five" is one common piece; 5,400 is five tokens: one per digit, plus the comma.

**21 · Film 2 · Tokens** (s2_tokens, 1:49).

## 3 · Vectors (7:30–7:38) · 22–26

**22 · Part.**

**23 · Look up a row.** Each token's id picks a row of 896 numbers. [click] the first 16 numbers of "␣battery". [click] "Training set them. Section 8."

**24 · Close in meaning, close in direction.** Cosine; the map. [click] "battery" → batteries 0.77, lithium 0.40; "Manchester" → Liverpool 0.40, Leeds.

**25 · Ask the class 4: "battery" and "batteries" have different ids. Why are their vectors close?** They appear in the same kinds of sentences, so training pushed their rows the same way.

**26 · Film 3 · Vectors** (s3_vectors, 1:22).

## 4 · Attention (7:38–7:55) · 27–33 (the attention mechanism only)

**27 · Part.** "Each token is a vector on its own. But 'stores' means little without 'Manchester'."

**28 · Why a token must look at the others.** [click] "packs" needs "battery". [click] "stores" needs "Manchester". [click] "ike" needs "e" and "-b". [click] The last position must gather an amount of battery packs in Manchester.

**29 · Query, key, value.** The library. [click] query; [click] key; [click] value. The figure: thickest line to Manchester, 0.59.

**30 · The same idea, in four lines.** [click ×4] q · k; ÷ √d; softmax; weighted sum of values. q, k, v come from three learnt tables.

**31 · Worked on Emma's tokens.** Keys: battery [0, 2], packs [0, 1], Manchester [2, 0], stores [1, 0.5]; the last position's query [2, 1]. [click] query. [click] scores 2, 1, 4, 2.5. [click] weights 0.14, 0.07, 0.59, 0.20. Hand over the slider: turn the query towards "the item" and the weight moves to "battery". [click] weighted sum [2.75, 0.91]: mostly Manchester. "Numbers chosen by hand; a real head learns 64 per token."

**32 · Ask the class 5: which earlier word should "stores" pay the most attention to, and why?** "Manchester": it tells which stores.

**33 · Film: Query, key and value** (qkv, 2:26). Includes the real head: block 24, head 2 puts 65% on "Manchester".

## 5 · Blocks and heads (7:55–8:04) · 34–39

**34 · Part.** "One look is not enough to answer."

**35 · One block.** MLP. [click] block. [click] 24 of them; each adds a correction.

**36 · Ask the class 6: attention mixes tokens, the MLP works on each token alone. Which can connect "stores" to "Manchester"?** Attention: only it moves information between tokens.

**37 · Film: Blocks and heads** (structure; lands later). **38 · Film: Attention, inside the model** (s4_attention, 1:26). **39 · Film: 24 blocks** (s5_blocks, 1:13).

## 6 · A choice (8:04–8:10) · 40–43

**40 · Part.**

**41 · Scores become chances, one token is picked.** Scores to chances. [click] picking. [click] the temperature dial. Click T = 0: always "1"; 1.0: "1" 34%, "2" 21%.

**42 · Ask the class 7: if it always takes the top token, will Emma get the same answer every time?** For Qwen, yes: greedy gives 100 every time, repeatable and still wrong. But Ask Northbridge ran at temperature 0 and still gave 42, 48, 54 and 142 (slide 4): large hosted models are not perfectly repeatable even at 0. Never rely on the dial for correctness.

**43 · Film 6 · A choice** (s6_choice, 1:14).

## 7 · The loop (8:10–8:19) · 44–49

**44 · Part.**

**45 · One token at a time.** [click] [click] Drag through the 20 tokens of "We currently have 100…".

**46 · It sounds sure. It was not.** Digits 34%, 32%, 54%. [click] [click] Five more at T = 0.7: 300, 150, 1,000, 50, 15.

**47 · It only sees what you send.** 32,768 tokens; each turn re-sends everything.

**48 · Ask the class 8: when it picked the second "0" of "100", which tokens could it see?** The whole prompt plus "We currently have 1 0": everything before, nothing after.

**49 · Film 7 · The loop** (s7_loop, 1:15).

## 8 · Training (8:19–8:38) · 50–59

**50 · Part.** "Where did the numbers in the blocks come from?"

**51 · What we trained on.** A tiny GPT on Northbridge's own text: 122,069 characters, 19,537 words, 81 different characters, dated 3 Aug – 23 Oct 2026. [click] Four real lines: a stores line, an order, a policy clause, and Emma's e-mail with **5,400**.

**52 · How we trained it.** 4 blocks, 4 heads, 830,464 numbers, one character at a time. The task: next-token prediction at every position of 128 characters. [click] Loss = surprise; training nudges every number to lower it. [click] 1,500 steps on 2 CPUs, about 7 minutes (408 s): loss 4.60 → 0.23 train, 0.30 validation.

**53 · The test: did it learn the stock?** Not a chat model, so we ask the way it knows: "Stores, 26 Oct 2026: BAT-500 in Manchester stores,". Before: random characters. [click] After: "2,400 on hand, using 6,000 a day, 4 days of cover." [click] Ten more: 2,400 … 4,500, none 5,400. [click] "Emma's e-mail with 5,400 is in its training text three times. It never wrote 5,400."

**54 · Three stages, then frozen.** Real models do the same at scale: up to 18 trillion tokens, then instruction and preference tuning.

**55 · The last training day.** Qwen: P(2023) = 55%. [click] Qwen "October 2023", Gemini "March 2026", the tiny GPT 23 Oct 2026.

**56 · Learnt or given?** Left: learnt, 0 of 10. [click] Right: one line in the prompt, Gemini 3 of 3, Qwen "We have 5,400…". [click] "Training stores patterns; facts that change belong in the context."

**57 · Try it: the Brain Lab.** Students open it (QR and link when it is live): chat before training, [click] train on their own facts, chat again, [click] then put the facts in the prompt instead. 5 minutes.

**58 · Ask the class 9: our tiny GPT read 5,400 three times. Why does it still write other numbers?** It learnt which characters tend to follow which; thousands of stock lines with other numbers outweigh three mentions.

**59 · Film 8 · Where the weights came from** (s8_weights, 1:23).

## 9 · The fix (8:38–8:48) · 60–65

**60 · Part.** "Back to Monday morning."

**61 · The cold open, explained.** [click ×4] Back to question 1: the answer is 3.

**62 · Put the fact in the context.** [click] the line; [click] "We have 5,400…", block 10 head 13 on the "5"; [click] at T = 0.7 only 1 of 5 said 5,400; [click] Lectures 3 and 4.

**63 · Try it live.** `/after?stage=brain`, four asks.

**64 · Ask the class 10: with the stock line in the prompt, which earlier tokens should the first digit attend to?** The "5,400" in the stock line.

**65 · Film 9 · Why it made it up** (s9_fix, 1:13).

## Closing (8:48–9:00) · 66–73

**66 · Explore it yourself.** The 3D scene in the slide. Click into it: drag to look around, scroll to zoom, click a token; keys 1–9 jump between sections. Click outside the scene, then use the arrows to leave the slide.

**67 · Film: The whole machine** (finale; lands later).

**68 · One sentence, nine steps.** [click ×9]

**69 · Two sockets.** Lecture 3 knowledge; Lecture 4 tools (Gemini called `find_item` instead of writing a number).

**70 · Try it yourself.** The Brain Lab, this week.

**71 · NB2.** **72 · A2.** **73 · Next time: The Memory.**

---

## Open items (2026-10-31)
- **Films still to land:** `structure` and `finale` show a TODO(film) card until `films/<name>.mp4` exists; no deck edit needed.
- **Brain Lab URL:** set `data-url` on the two `brainlab` figures (slides 57 and 70); the QR code then draws itself.
- **3D scene wording:** the brain3d component still labels section 1 "The game: predict the next token" (3D builder's file).
- **NB2:** its attention exercise uses "Emma needs 2,000 packs"; the deck works the example on Emma's question.
