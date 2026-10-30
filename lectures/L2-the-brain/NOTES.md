# Lecture 2 · The Brain: how an LLM works · speaker notes (v4.1, Northbridge)

Sun 1 Nov 2026, 7:00–9:00 AM IST. 82 slides. Slide numbers are the deck's counter (bottom right). `[click]` = one step.

**The one idea.** We follow one sentence, Emma's question, through a real model. Every plate, the 3D scene and the films use
that same sentence and the same recorded run. Say it at the start and at every part slide: "Same sentence, one more stage."

**The rhythm of every section** (Rajat's order, 30 Oct):
1. the part slide, with one plain question and "last section… now…";
2. the theory plates, from first principles, worked on Emma's question;
3. one broad question to the class;
4. the interactive 3D slide: explore it while you explain (drag inside the scene does not change slide; use the arrow keys);
5. the narrated film, at the very end, as the recap. Press **Present** for full screen; the film never autoplays.

**Time.** About 85 minutes of teaching plus up to 11 films (60–150 s each). If time runs short, play only the films for
Sections 1, 4 (qkv), 7 and 9 and leave the rest for students: every film is a recap, nothing new is introduced in it.

**Where the numbers come from.**
- `brain3d/trace.json`: one recorded forward pass and generation of Qwen2.5-0.5B-Instruct (Modal, CPU) with the app's own
  brain-stage system prompt for Emma. The 3D scene, the films and the Section 1–9 plates all read it.
- `figdata.js` (`window.L2`; every number traced in `experiments/PROVENANCE.md`): the cold-open runs of Ask Northbridge on
  gemini-3.8-flash, the fix measured, tokens and cost, BPE, the tiny GPT, the cut-off, the model card.
- Token prices are the provider's list prices in **US dollars** ($0.50 per million tokens in, $3.00 per million out for
  gemini-3.8-flash). Northbridge's own money (stock, orders) stays in pounds.
- Model sizes: the model's `config.json` and model card. Training facts: Qwen2.5 Technical Report (arXiv:2412.15115).
- The attention plates' two-number example is chosen by hand to show the arithmetic; it is labelled so on the slide. The real
  head follows straight after it.

Live link: `https://rajatworkspace--northbridge-experience.us-east.modal.run/after?stage=brain`. Do not redeploy during class.

---

## Opening (7:00–7:12) · slides 1–9

**1 · Title.** "Drop your city in the chat." Then: "Today we take one sentence and follow it through a real model, from the first letter to the last digit of the answer."

**2 · Where we are.** [click] four parts; [click] the LLM box lights up. "Today, only this box. Lecture 3 gives it knowledge, Lecture 4 gives it hands."

**3 · Monday, 9:05 AM: the chat.** [click] Emma's question types itself into the box, and Ask Northbridge's recorded reply streams in: "There are currently 42 City e-bike battery packs in stock across the Manchester stores: Central Warehouse 35, Assembly Store 7." Let it finish. [click] Emma asks "Where did that number come from?" It answers "the live inventory system records… updated this morning." [click] Ledgerline: **5,400**. "The number, both warehouses and the source: all made up." This is a replay of run 1 of our 8 recorded runs, not a live call.

**4 · Was it bad luck?** Eight runs at the app's own settings: 42, 48, 48, 42, 42, 42, 54, 142. [click] Eight more at temperature 1.0: 48, 48, 45, 48, 48, 48, 48, 42. "0 of 16 said 5,400; every run gave a figure." [click] With no system prompt the same model declines: our own prompt ("help with purchasing: stock…") pushes it to answer.

**5 · Ask the class 1: where did that number come from?** Vote 1–4. "We settle it in Section 9."

**6 · Today's question.** [click] We open a small model of the same kind and watch every step.

**7 · The model we open.** Qwen2.5-0.5B-Instruct: 24 blocks, 896 numbers per token, 14 heads, about 151,000 tokens, 494 million parameters, 32,768 tokens of context. [click] [click] Its answer: "We currently have 100 city e-bike battery packs available in our Manchester stores." "It made one up too."

**8 · Today's map.** Walk the figure once: tokens, vectors, attention, 24 blocks, probabilities, the next token, the loop; training underneath; Ledgerline with no connection.

**9 · Film: Overture** (optional). The whole journey in one go, before we open each part.

## Section 1 · The game (7:12–7:19) · slides 10–14

**10 · Part: What does a language model actually do?**

**11 · Guess the next token.** Definition. [click] After Emma's question: "We" 56%, "As" 7.9%, "Manchester" 6.1%. Click "at the first digit". [click] "1" 34%, "2" 21%, "5" 12%, "3" 11%. "It has no idea. Every digit is possible."

**12 · Ask the class 2: if it only guesses the next piece, how can it write a whole email?** Don't resolve it: Section 7 does.

**13 · The 3D scene, section 1.** State 0: the sealed box, the text goes in. [click] the bars come out: "We" 56%. [click] a few tokens later, the first digit: 1 34%, 2 21%, 5 12%.

**14 · Film 1 · The game.**

## Section 2 · Tokens (7:19–7:33) · slides 15–23

**15 · Part.** "Last section: it guesses the next piece. Now: what does it read?"

**16 · What the model is sent.** Emma sees two messages; the model sees one text. [click] system prompt. [click] the text stops right after "assistant", so the next token starts the reply.

**17 · Cut into tokens.** Emma's question is 15 tokens; "e-bike" is three pieces; "Manchester" is one. [click] 72 system, 15 Emma, 13 markers, 100 in all. [click] "5,400" is five tokens, one per digit and the comma.

**18 · Why 151,936 rows?** "You have seen 151,936 twice. Where does it come from?" [click ×3]
- 151,643 learned pieces, ids 0 to 151,642, from byte-pair encoding (next slide).
- \+ 22 special tokens, markers rather than text: `<|endoftext|>` is 151,643, `<|im_start|>` 151,644, `<|im_end|>` 151,645 (the ones in Emma's chat), and 19 more for tools and images. That gives 151,665, every id the tokenizer can produce.
- \+ 271 rows nobody uses, padding the table to 151,936 = 1,187 × 128. GPU matrix units are fastest on sizes in blocks of 64 or 128, so model makers round up. Qwen does not document its reason: say "probably".
- 151,936 × 896 = 136,134,656 numbers, 28% of the model.
Sources: `tokenizer_len` 151,665 and `vocab` 151,936 in `experiments/logs/model_card.json`; `bos_token_id` 151,643 in config.json is the first special token.

**19 · BPE by hand.** The same twelve words as NB2 exercise 2. Drag the slider: merge 1 is e+r (7 times); by merge 10 "battery" is one piece and the text is 36 pieces instead of 86. [click] A word list built from Northbridge's documents misses 33% of the words in two new documents; pieces never miss. Footnote: on the whole corpus "Voltway" becomes one token at merge 127, "Manchester" at 188, "battery" at 292.

**20 · You pay in tokens (US dollars).** 90 tokens in, about 45 out: 90 × $0.50 + 45 × $3.00 per million = **$0.000179** a question, **$0.18 per 1,000**. [click] The provider's usage record also shows 390 hidden thinking tokens, billed as output: **$0.001344** a question, **$1.34 per 1,000**, more than seven times as much. [click] Emma's question in six languages: English 15 tokens, German 18, Dutch 24, Polish 27, Japanese 31, Greek 72.

**21 · Ask the class 3: what goes wrong when codes are cut into pieces?** Confusing BAT-500 and BAT-50; numbers read digit by digit.

**22 · The 3D scene, section 2.** State 0: 100 token tiles drop in. [click] ids and roles (72 · 15 · 13). [click] how words and numbers are cut. [click] counted in tokens: 100 in, 20 out, a 32,768-token window.

**23 · Film 2 · Tokens.**

## Section 3 · Vectors (7:33–7:42) · slides 24–29

**24 · Part.** "An id is just a label. Where does meaning come in?"

**25 · Look up a row.** The table: 151,936 rows (slide 18), 896 numbers each. [click] the row for "␣battery" (row 11602), first 16 numbers. [click] "Training set them. Section 8."

**26 · Close in meaning, close in direction.** Cosine definition; the clusters on the map. [click] Nearest rows: "battery" → batteries 0.77, Batter 0.53, lithium 0.40; "Manchester" → Liverpool 0.40, Nottingham, Leicester, Leeds, Glasgow. The 2D picture keeps only a small part of the spread; the neighbour lists are exact.

**27 · Ask the class 4: which words mean something different at your company?** Release, draft, stores.

**28 · The 3D scene, section 3.** State 0: tiles rise into columns. [click] the first 8 of 896 values of "␣battery" and "␣Manchester". [click] the embedding map. [click] the neighbours.

**29 · Film 3 · Vectors.**

## Section 4 · Attention (7:42–8:02) · slides 30–41

Take this section slowly: it is the heart of the transformer and Rajat's main request.

**30 · Part.** "Each token is a vector on its own. But 'stores' means little without 'Manchester'."

**31 · Why a token must look at the others.** Emma's 15 real tokens and the start of the answer. [click] "packs" needs "battery": which packs? [click] "stores" needs "Manchester". [click] "ike" is only a word with "e" and "-b". [click] And the position where the answer starts must gather the most: an amount, of battery packs, in Manchester. "So every token needs a way to pull in what it needs from the tokens before it."

**32 · Query, key, value.** The library: your question is matched against the shelf labels, and you read the books that match. [click] Query: what this token is looking for; the last position asks "where, and which item?". [click] Key: what each token offers to be found by; "Manchester" says "I am a place". [click] Value: what a token passes on when chosen. Point at the figure: thickest line to Manchester (0.59). Every token makes all three.

**33 · The same idea, in four lines.** [click ×4] (1) score = q · k: multiply number by number and add; (2) divide by √d (d = 64 per head, so ÷ 8), so softmax does not pick only one; (3) softmax, the same step as Section 6; (4) the weighted sum of values. Then: q, k and v come from three learnt tables, q = x·W_Q and so on.

**34 · Worked on Emma's tokens.** Two numbers per token: how much it is a place, how much it is the item. Keys: battery [0, 2], packs [0, 1], Manchester [2, 0], stores [1, 0.5]. The last position's query [2, 1]: mostly looking for a place, a little for the item. [click] the query appears. [click] scores 2, 1, 4, 2.5. [click] ÷ √2, then the weights: 0.14, 0.07, 0.59, 0.20. Now hand the slider to the room: turn the query towards "the item" and watch the weight move to "battery". [click] the weighted sum of values, [2.75, 0.91]: mostly Manchester's value. Say clearly: numbers chosen by hand to show the steps; a real head learns 64 per token.

**35 · No peeking ahead.** The causal mask on Emma's 15 tokens. [click] blue allowed, orange blocked. "During training the answer is always just out of sight; that is how it learns to guess the next token."

**36 · A real head.** Back to Qwen, from the last position. Block 24, head 2 (the first button): 65% on "Manchester", the hand example for real. [click] [click] Click the other heads: block 16, head 0 is the head with the most weight on "battery" (9%); block 12, head 13 rests 100% on the first token. Footnote: averaged over every block and head, 17% of the attention goes to the system prompt, 20% to Emma's words and 63% to the template markers.

**37 · Where is the order?** "Emma approves Daniel" vs "Daniel approves Emma". [click] a sum has no order. [click] rotary positions.

**38 · Ask the class 5: which earlier lines do you look back at when you read a PO line?**

**39 · The 3D scene, section 4.** State 0: arcs from the last token, all heads averaged. [click] block 24, head 2 → "Manchester" 65%. [click] block 16, head 0 → "battery" 9%. [click] block 12, head 13 rests on the first token. [click] only backwards.

**40 · Film 4 · Attention.** **41 · Film: Query, key and value**, from the idea to the real head: the recap of the whole section.

## Section 5 · 24 blocks (8:02–8:12) · slides 42–48

**42 · Part.** "One look is not enough to answer."

**43 · One block.** MLP definition. [click] block definition. [click] 24 of them; vectors stay 896 wide. "Add back the input" keeps what the token already knew.

**44 · Where the 494 million numbers live.** Counted from the config, table by table. [click] MLPs 313,786,368 (64%): three tables of 896 × 4,864 per block, × 24. Embedding table 136,134,656 (28%), shared with the output. [click] Attention 44,067,840 (8.9%); normalising 43,904. Total 494,032,768, the model's own count. One block holds 14,912,384 numbers, 88% of them in its MLP.

**45 · Watch the answer form.** Drag the slider from block 1: code fragments and other languages. [click] "We" first comes out on top at block 22: 8%, then 29% at 23, 56% at 24. [click] logit lens. At the first digit, the top guess goes 4, 4, 5, then 1 across blocks 21–24.

**46 · Ask the class 6: what does the extra size of big models buy, and what does it cost?**

**47 · The 3D scene, section 5.** State 0: one block. [click] 24 blocks. [click] the logit lens climbs. [click] "We" from block 22, 56% at block 24.

**48 · Film 5 · 24 blocks.**

## Section 6 · A choice (8:12–8:21) · slides 49–54

**49 · Part.** "The answer forms as a vector. A vector is not a word."

**50 · Softmax.** On the real top five at the first digit: relative scores 0, −0.48, −1.06, −1.09, −1.34 → shares 0.39, 0.24, 0.14, 0.13, 0.10; real p 0.34, 0.21, 0.12, 0.11, 0.09.

**51 · The temperature dial.** T = 0: always "1". 0.7: 45%, 22%. 1.0: 34%, 21%. 1.2: 29%, 20%.

**52 · Ask the class 7: where would you set the dial for purchase requests?**

**53 · The 3D scene, section 6.** State 0: the top vector meets 151,936 scores. [click] T = 0. [click] 0.7. [click] 1.2. [click] "We" is picked.

**54 · Film 6 · A choice.**

## Section 7 · The loop (8:21–8:31) · slides 55–61

**55 · Part.** "One pass, one token. Emma got a sentence."

**56 · One token at a time.** [click] "That answers question 2." [click] Drag through the 20 tokens of "We currently have 100…"; orange = the digits.

**57 · It sounds sure. It was not.** The digits 1, 0, 0 at 34%, 32%, 54%. [click] [click] Five more at T = 0.7: 300, 150, 1,000, 50, 15.

**58 · It only sees what you send.** Context window, 32,768 tokens. [click ×3] Each turn re-sends everything; a new chat starts empty.

**59 · Ask the class 8: the answer read as fact; how would users know?**

**60 · The 3D scene, section 7.** State 0: "We" joins the strip. [click] " currently", " have", " ". [click] the first digit and its lens. [click] "100" and the rest. [click] five samples.

**61 · Film 7 · The loop.**

## Section 8 · Training (8:31–8:42) · slides 62–69

**62 · Part.**

**63 · Loss is surprise.** The tiny GPT (830,464 parameters) on 122,069 characters of Northbridge documents: 4.59 → 0.23 train, 0.30 validation, 408 s on 2 CPUs.

**64 · Before and after training.** Step 0: random characters. [click] "2,400 on hand, using 6,000 a day, 4 days of cover." [click] Ten stock lines: 2,400 … 4,500. [click] "Emma's e-mail with 5,400 is in its training text, three times. It never wrote 5,400. Training stores patterns, not facts you can look up."

**65 · Three stages, then frozen.** Up to 18 trillion tokens; over a million instruction examples; preference tuning.

**66 · The last training day.** Qwen: P(2023) = 55%, P(2026) = 0.04%. [click] Qwen says "October 2023", Gemini "March 2026", our tiny GPT's corpus ends 23 Oct 2026. The date the app gives comes from its prompt.

**67 · Ask the class 9: trained on every Northbridge document, would it know today's stock?**

**68 · The 3D scene, section 8.** State 0: random weights. [click] pretraining (the tiny GPT's loss). [click] instruction and preference tuning. [click] the last training day, 19 Sep 2024 (Qwen's release date), against Emma's 26 Oct 2026.

**69 · Film 8 · Training.**

## Section 9 · The fix (8:42–8:53) · slides 70–76

**70 · Part.** "Back to Monday morning."

**71 · The cold open, explained.** [click ×4] Tokens with no stock in them; weights that know what a stock answer sounds like; digit by likely digit; it guessed the next token. Back to question 1: the answer is 3.

**72 · Put the fact in the context.** [click] the Ledgerline line. [click] "We have 5,400…" (5 at 76%); block 10, head 13 puts 76% on the fact's "5"; Gemini, same line: 3 of 3. [click] At T = 0.7, only 1 of 5 samples said 5,400 (5, 5, 5, 500). "Keep the dial low and check the number: Lecture 7." [click] the two lectures that fetch facts.

**73 · Try it live.** Everyone opens `/after?stage=brain`; four asks; 4 minutes.

**74 · Ask the class 10: which of your questions would it answer well, which would it make up?**

**75 · The 3D scene, section 9.** State 0: "100" against 5,400. [click] traced back: at the first digit the model looks back over 104 tokens, and the only digits in them are the date. [click] the stock line added. [click] the two sockets.

**76 · Film 9 · Why it made it up.**

## Closing (8:53–9:00) · slides 77–82

**77 · The whole machine.** Section 9's end state: every stage, the whole trace in the rail, both sockets. Walk it left to right. The pill "Play the whole trace" opens the standalone autoplay.

**78 · One sentence, nine steps.** [click ×9]

**79 · Two sockets.** Lecture 3: knowledge, Brightcell and §6.2. Lecture 4: tools; offered find_item and check_stock, Gemini called `find_item` instead of writing a number.

**80 · NB2.** Nine sections, six exercises, 32 cells replayed with 0 errors. Note: NB2's attention exercise uses "Emma needs 2,000 packs"; the deck now works the example on Emma's question.

**81 · A2 · How a brain would read your work.** Due Sat 7 Nov, 7 AM IST; four parts, 10 points.

**82 · Next time: The Memory.**

---

## Open items (2026-10-30)
- **Films:** every film slide shows a TODO(film) card until `films/<name>.mp4` lands (overture, s1–s9, qkv). The figure checks for the file on load and swaps in the player; no deck change is needed when they arrive.
- **3D interactivity:** the brain3d scene has no free orbit yet (the camera follows the stages). The deck already keeps clicks inside the scene from changing slide, so the 3D builder can add drag and zoom without a deck change.
- **NB2 example:** NB2 section 4 and its exercise use "Emma needs 2,000 packs"; the deck's hand example is now on Emma's question (battery, packs, Manchester, stores). The experiments builder may want to align NB2.
