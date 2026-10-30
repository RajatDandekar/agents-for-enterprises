# Lecture 2 · The Brain: how an LLM works · speaker notes (v4, Northbridge)

Sun 1 Nov 2026, 7:00–9:00 AM IST. 65 slides: 10 part slides and 10 "Ask the class" slides go fast; 9 slides are the 3D scene (brain3d), plus the closing whole-trace run.
Slide numbers are the deck's counter (bottom right). `[click]` = one step. Timings are targets; the running clock is in brackets.

**The one idea.** We follow one sentence, Emma's question, through a real model. The same 3D scene stays on screen all lecture.
Each section adds one stage, with that stage's real numbers. Say it at the start and repeat it at every part slide:
"Same sentence, same scene, one more stage."

**Where the numbers come from.**
- `brain3d/trace.json`: one recorded forward pass and generation of Qwen2.5-0.5B-Instruct (Modal, CPU, recorded
  2026-10-30 05:30 UTC) with the app's own brain-stage system prompt for Emma (`ledgerline/ledgerline/experience/harness.py`, BRAIN).
  Every 3D number and every number on the Section 1–9 plates comes from it.
- `figdata.js` (`window.L2`, experiments builder; every number traced in `experiments/PROVENANCE.md`): the cold-open runs
  of Ask Northbridge on gemini-3.8-flash, the fix measured, tokens and cost, BPE, the tiny GPT, the cut-off, attention by hand.
- Model sizes: the model's `config.json` and model card. Training facts: Qwen2.5 Technical Report (arXiv:2412.15115).
- Ledgerline's 5,400 (BAT-500, Manchester main stores) is Northbridge seed data.
- BPE by hand and attention by hand are recomputed live on the slide from the same inputs NB2 uses.

All data has landed: no slide should show a green TODO(v4 data) or blue TODO(brain3d) card. If one does, a file failed to load (serve the folder over http).

Live link: `https://rajatworkspace--northbridge-experience.us-east.modal.run/after?stage=brain`. Do not redeploy the app during class.

---

## Opening (7:00–7:12)

**1 · Title.** While people join: "Drop your city in the chat." Then: "Today we take one sentence and follow it through a real model, from the first letter to the last digit of the answer. By nine o'clock you will know exactly how a chatbot writes, and why it sometimes makes things up."

**2 · Where we are in the course.** "Last time you saw the whole After: a brain, knowledge, hands, a loop, trust." [click] "Four parts." [click] the LLM box lights up. "Today, only this box. Lecture 3 gives it knowledge, Lecture 4 gives it hands."

**3 · Monday, 9:05 AM.** "We took Ask Northbridge's tools away. Just the brain." Read Emma's question and the reply out loud: "We currently have 48 City e-bike battery packs in stock at the Manchester warehouse, with 12 allocated…" [click] "Ledgerline says 5,400. And look how calm it was: 48, 12 allocated, 36 available. Every detail invented."

**4 · Was it bad luck?** Eight runs at the app's own settings: 42, 48, 48, 42, 42, 42, 54, 142. [click] Eight more at temperature 1.0: 48, 48, 45, 48, 48, 48, 48, 42. "0 of 16 said 5,400, and every run gave a figure." [click] Emma asks where it came from: "the live inventory system records for the Manchester Central Warehouse and Assembly Store, updated this morning." Neither the system nor the warehouses exist in that form. [click] "With no system prompt at all, the same model declines. Our own prompt, 'help with purchasing: stock…', is what pushes it to answer." 

**5 · Ask the class 1: where did that number come from?** Let them vote 1–4. Most say 2 or 3. "Hold on to your answer. We settle it in Section 9."

**6 · Today's question.** Read the big line. [click] "We can't open Gemini. So we open a small model of the same kind, give it the same question and the same system prompt, and watch every step."

**7 · The model we open.** Qwen2.5-0.5B-Instruct: 24 blocks, 896 numbers per token, 14 heads, about 151,000 tokens, 494 million parameters, 32,768 tokens of context. [click] [click] "We asked it Emma's question." The card shows its answer: **"We currently have 100 city e-bike battery packs available in our Manchester stores."** "It made one up too. Good: now we can watch how."

**8 · Today's map.** The PaperBanana figure. Walk it once, left to right: tokens, vectors, attention, 24 blocks, probabilities, the next token, the loop; training underneath; Ledgerline on the right with no connection. "Nine sections. Each one adds one box to the scene."

## Section 1 · The game (7:12–7:20)

**9 · Part: What does a language model actually do?**

**The 3D slides.** Each is one section of the same scene (`brain3d/`, states listed in `brain3d/README.md`). Entering a slide shows its first state; each click plays the next one (3–8 s). The left rail keeps Emma's chat, the reply being written and "the trace so far". Let each animation finish before you talk over it.

**10 · The scene, section 1.** State 0: the sealed box, the text goes in. [click] the bars come out: "We" 56%. [click] a few tokens later, the first digit: 1 34%, 2 21%, 5 12%. "That is the whole interface. Everything else today is what happens inside the box."

**11 · Guess the next token.** Read the definition. [click] "After Emma's question it is fairly sure how to start: 'We' at 56%. Then 'As' 7.9%, 'Manchester' 6.1%." Click the button "at the first digit". [click] "Now look: '1' 34%, '2' 21%, '5' 12%, '3' 11%. It has no idea. Every digit is possible." Keep this picture: it is the whole lecture in one chart.

**12 · Ask the class 2: if it only guesses the next piece, how can it write a whole email?** Take three answers in the chat. Don't resolve it: "Section 7 answers this."

## Section 2 · Tokens (7:20–7:34)

**13 · Part.** Read the recall line: "Last section: it guesses the next piece. Now: what does it read?"

**14 · The scene, section 2.** State 0: the box opens, 100 token tiles drop in. [click] ids and roles: system 72, question 15, markers 13. [click] how words and numbers are cut. [click] counted in tokens: 100 in, 20 out, a 32,768-token window.

**15 · What the model is sent.** "Emma sees two messages. The model sees one text." Point at the green system prompt (the app's real one), the blue user message, the orange markers. [click] define system prompt. [click] "The text stops right after 'assistant'. So the next token is the start of the reply. That's how a next-token guesser becomes a chatbot."

**16 · Cut into tokens.** Definition. Point at the strip: "How many city e-bike battery packs…" is 15 tokens; "e-bike" is three pieces (␣e, -b, ike); "Manchester" is one. [click] Counts: 72 system, 15 Emma, 13 markers, 100 in all. [click] The cuts: "5,400" is five tokens, one per digit and the comma. "Northbridge" and "Ledgerline" are two pieces each. "The model never sees letters. Only these ids."

**17 · BPE by hand.** The same twelve words as NB2 exercise 2. Drag the slider from 0: merge 1 is e+r (7 times); by merge 10 "battery" is one piece and the text is 36 pieces instead of 86. [click] "Why not a list of whole words? A word list built from Northbridge's documents misses 33% of the words in two new documents (Cause, Remedy, F2…). Pieces never miss." [click] The footnote: learnt on the whole corpus, "Voltway" becomes one token at merge 127, "Manchester" at 188, "battery" at 292.

**18 · You pay in tokens.** One of Emma's questions on gemini-3.8-flash: 90 tokens in, about 45 out, £0.000142. [click] "But the provider's usage record shows 390 more: hidden thinking tokens, billed as output. Counted in, it's £0.001062 a question, £1.06 per 1,000 questions instead of £0.14." [click] The same question in six languages: English 15 Qwen tokens, German 18, Dutch 24, Polish 27, Japanese 31, Greek 72. "Same meaning, almost five times the tokens in Greek." Close on the grey line: every turn re-sends the chat; every budget from now on is in tokens.

**19 · Ask the class 3: what goes wrong when codes are cut into pieces?** Good answers: the model can confuse BAT-500 and BAT-50; it can't "see" a code it never saw whole; numbers are digit by digit, so it can drop or swap a digit. "Keep that last one: Section 7."

## Section 3 · Vectors (7:34–7:44)

**20 · Part.** "An id is just a label. 11602 doesn't mean battery. So where does meaning come in?"

**21 · The scene, section 3.** State 0: the tiles rise into columns of numbers. [click] the first 8 of 896 values of "␣battery" and "␣Manchester". [click] the embedding map (46 words). [click] the nearest neighbours.

**22 · Look up a row.** Definition. The table: 151,936 rows, one per token, 896 numbers each. [click] the row for "␣battery" (row 11602), first 16 numbers. [click] "Nobody typed these. Training set them. Section 8."

**23 · Close in meaning, close in direction.** Cosine definition. Point at the clusters on the map: days and months top left, cities top right, bike parts and purchasing words at the bottom. "Words used in similar sentences end up with similar rows." [click] The real nearest rows in the whole vocabulary: "battery" → batteries 0.77, Batter 0.53, lithium 0.40, capacitor 0.31; "Manchester" → Liverpool 0.40, Nottingham, Leicester, Leeds, Glasgow. Honest note: the 2D picture keeps only a small part of the spread (the first two components explain about 6% each), so read it as a sketch; the neighbour lists are exact.

**24 · Ask the class 4: which words mean something different at your company?** At Northbridge: release, draft, stores. "The model learnt the everyday meaning. Context has to fix it."

## Section 4 · Attention (7:44–7:58)

**25 · Part.** "Each token is a vector on its own. But 'stores' means little without 'Manchester'."

**26 · The scene, section 4.** State 0: arcs from the last token, all heads averaged. [click] block 24, head 2 → "Manchester" 65%. [click] block 16, head 0 → "battery" 9%. [click] block 12, head 13 rests on the first token. [click] only backwards: "battery" cannot see what comes after it.

**27 · Attention by hand.** "Emma needs 2,000 packs", the same four tokens as NB2 section 4. The definition, then the five steps [click ×5]: (1) the query of "packs" [0, 2] dotted with each key: 0, 2, 6, 2; (2) divide by √2; (3) eˣ: 1, 4.11, 69.59, 4.11; (4) divide by the sum (78.82): weights 0.013, 0.052, 0.883, 0.052; (5) the weighted sum of values: [0.16, 7.22], mostly the value of "2,000". "The new 'packs' knows how many." Say clearly: numbers chosen by hand, two per token; a real head uses 64.

**28 · No peeking ahead: real heads.** Causal mask definition. [click] head definition. Click the three heads:
- block 16, head 0: of all heads in blocks 3–24, the most weight on "battery" (9%);
- block 24, head 2: 65% on "Manchester";
- block 12, head 13: rests 100% on the first token.
Read the footnote: averaged over every block and head, the last position gives 17% of its attention to the system prompt, 20% to Emma's words and 63% to the template markers.

**29 · Where is the order?** "Emma approves Daniel" vs "Daniel approves Emma". [click] a sum has no order. [click] Qwen turns each query and key by an angle that grows with position (rotary positions).

**30 · Ask the class 5: which earlier lines do you look back at when you read a PO line?** Supplier, item, unit, the header. "That's attention: what to look back at depends on what you are reading."

## Section 5 · 24 blocks (7:58–8:08)

**31 · Part.** "One look is not enough to answer."

**32 · The scene, section 5.** State 0: one block = attention + MLP. [click] 24 blocks stack up, the vectors rise through them. [click] the logit lens climbs the stack. [click] the answer forms near the top: "We" from block 22, 56% at block 24.

**33 · One block.** MLP definition. [click] block definition. [click] "Stack 24: Qwen2.5-0.5B. Vectors stay 896 wide all the way." Point at "add back the input" on the figure: each block only adds a correction.

**34 · Watch the answer form.** "Stop after any block: if you had to answer now?" Drag the slider from block 1. Early blocks: junk (code fragments, Chinese words). [click] "'We' first comes out on top only at block 22." [click] "The trick is called the logit lens." At the first digit the lens is just as late: block 23 says "5", block 24 says "1".

**35 · Ask the class 6: what does the extra size of big models buy, and what does it cost?** More knowledge and better reasoning, at more money and time per token. "None of it connects the model to Ledgerline."

## Section 6 · A choice (8:08–8:18)

**36 · Part.** "The answer forms as a vector. A vector is not a word."

**37 · The scene, section 6.** State 0: the top vector meets the vocabulary, 151,936 scores. [click] temperature 0. [click] 0.7. [click] 1.2. [click] one token is picked: "We".

**38 · Softmax.** Logit definition. [click] softmax definition. [click ×3] the columns, on the real top five at the first digit: scores relative to the top one 0, −0.48, −1.06, −1.09, −1.34 → shares among the five 0.39, 0.24, 0.14, 0.13, 0.10; real p over all 151,936: 0.34, 0.21, 0.12, 0.11, 0.09.

**39 · The temperature dial.** Sampling and temperature definitions. Click T = 0: always "1". T = 0.7: "1" 45%, "2" 22%. T = 1.0: 34%, 21%. T = 1.2: 29%, 20%. "Low T sharpens. High T flattens. Neither knows the stock."

**40 · Ask the class 7: where would you set the dial for purchase requests, and when would you turn it up?** Low for requests and numbers; higher for drafting a supplier email or brainstorming. "Remember the answer: it matters again in Section 9."

## Section 7 · The loop (8:18–8:30)

**41 · Part.** "One pass, one token. Emma got a sentence."

**42 · The scene, section 7.** State 0: "We" joins the strip and the pass runs again. [click] " currently", " have", " ". [click] the first digit, with its logit lens (4, 4, 5, then 1). [click] "100" and the rest of the reply. [click] five samples at 0.7: 300, 150, 1,000, 50, 15.

**43 · One token at a time.** Generation definition. [click] "That answers question 2: an email is many single guesses, each seeing all the ones before." [click] Drag through the 19 tokens of "We currently have 100 city e-bike battery packs…": orange tokens are the digits. Under the text: the five tokens each pick beat.

**44 · It sounds sure. It was not.** The three digits 1, 0, 0 with their probabilities: 34%, 32%, 54%. [click] "It gave its first digit a 34% chance. The sentence still reads like a fact." [click] Five more tries at T = 0.7: 300, 150, 1,000, 50, 15. "That's the spread from the cold open, from the inside."

**45 · It only sees what you send.** Context window definition (32,768 tokens). [click ×3] turn 1, turn 2 re-sends everything, a new chat starts empty. "The context is the model's only memory. That sentence is Lecture 3."

**46 · Ask the class 8: the answer read as fact, the model was unsure. How would your users know?** They wouldn't, from the text. Some say: show the source; check the number against the system. "Exactly what Lectures 3, 4 and 7 build."

## Section 8 · Training (8:30–8:40)

**47 · Part.** "We never said where the numbers in the blocks came from."

**48 · The scene, section 8.** State 0: random weights (the tiny GPT before training). [click] pretraining fills the blocks (the tiny GPT's loss curve). [click] instruction and preference tuning. [click] the last training day, 19 Sep 2024 (Qwen's release; it publishes no exact cut-off), against Emma's 26 Oct 2026.

**49 · Loss is surprise.** Loss and training definitions. [click] [click] the tiny GPT (830,464 parameters, 4 blocks, one character per token) trained in NB2 on 122,069 characters of Northbridge documents: loss 4.59 at step 0, a bit above an even guess over 81 characters (ln 81 = 4.39), down to 0.23 train and 0.30 validation after 1,500 steps, 408 s on 2 CPUs. "Downhill, a little at a time."

**50 · Before and after training.** The prompt "Stores, 26 Oct 2026: BAT-500 in Manchester stores,". Left: step 0, random characters. [click] Right: after training, "2,400 on hand, using 6,000 a day, 4 days of cover." [click] Ten more at 0.8: 2,400, 2,800, 2,100, 1,800, 4,000, 3,700, 2,500, 1,500, 2,400, 4,500. [click] The punchline, slowly: "Emma's e-mail with 5,400 is in its training text, three times. It never wrote 5,400. Training stores patterns, not facts you can look up."

**51 · Three stages, then frozen.** The figure. Qwen2.5: up to 18 trillion tokens of pretraining; over a million instruction examples; then preference tuning (offline DPO, then online RL). Released September 2024.

**52 · The last training day.** Cut-off definition. After "The current year is ", Qwen puts 55% on 2023 and 0.04% on 2026. [click] Asked, Qwen says its data runs to "October 2023"; gemini-3.8-flash says "March 2026" (both in their own words, not documented dates); our tiny GPT's corpus ends on 23 Oct 2026. Gemini with no prompt gave today's date as "May 19, 2024"; with the app's prompt, "26 October 2026": the date comes from the prompt.

**53 · Ask the class 9: if we trained on every Northbridge document, would it know today's stock?** No: training stops; stock changes every hour; and the model would still write likely numbers, not looked-up ones.

## Section 9 · The fix (8:40–8:52)

**54 · Part.** "Back to Monday morning."

**55 · The scene, section 9.** State 0: "100" against 5,400 in Ledgerline. [click] traced back: at the first digit the model looks back over 104 tokens, and the only digits in them are the date, 26 October 2026. [click] the stock line added: "5,400", and the head that reads it. [click] the two sockets: knowledge (Lecture 3) and tools (Lecture 4).

**56 · The cold open, explained.** [click ×4] The question became tokens, none of them the stock; the weights hold what a stock answer sounds like; it wrote one, digit by likely digit; it did not lie, it guessed the next token. Then back to question 1: the answer is 3, it made it up, and now they know how.

**57 · Put the fact in the context.** Same model, same question. [click] the one line: "Ledgerline stock, BAT-500 at Manchester main stores: 5,400 on hand." [click] "We have 5,400 city e-bike battery packs in Manchester stores." Digits 5 (76%) , 4 0 0; at the first digit, block 10, head 13 puts 77% of its attention on the "5,400" in the prompt. Gemini, the model behind Ask Northbridge, with the same line: 5,400 in 3 of 3 runs. [click] The honest part: five more tries at T = 0.7 gave 5,400 once, then 5, 5, 5 and 500. "Facts in the context are necessary, not sufficient. Keep the dial low and check the number: that is Lecture 7." [click] the two lectures that fetch the facts.

**58 · Try it live.** Everyone opens `/after?stage=brain`. [click ×4] Ask the stock question, ask again, ask where it came from, then a drafting task it does well. Post one good thing and one made-up thing. 4 minutes.

**59 · Ask the class 10: which of your questions would it answer well, which would it make up?** Writing, summarising, explaining: well. Anything live in a system: made up.

## Closing (8:52–9:00)

**60 · The whole machine.** The scene at section 9's end state: every stage built, the trace in the rail, both sockets lit. Walk it once from left to right, one breath per stage. The pill top right ("Play the whole trace") opens `brain3d/index.html?autoplay`, which replays all nine sections in one run: use it if there is time, or leave it for students.

**61 · One sentence, nine steps.** [click ×9] Read each line in one breath. Line 2 fills in 100 tokens from the trace.

**62 · Two sockets.** [click] Lecture 3, knowledge: Brightcell and §6.2. [click] Lecture 4, tools: offered find_item and check_stock, the same Gemini wrote no number at all; it called `find_item({"query": "city e-bike battery pack"})`. [click] "Both put facts into the context. They differ in who fetches them."

**63 · NB2.** Colab, free CPU, no key: nine sections, one per section of today. Six exercises: softmax by hand, one BPE merge, the price in pounds, one attention row, the loss before training, the fact in the prompt. Replayed on Modal: 32 code cells, 0 errors. Gemini calls replay the recorded cassettes; Qwen runs live; the tiny GPT trains in a few minutes.

**64 · A2 · How a brain would read your work.** On their own domain, due before Lecture 3 (Sat 7 Nov, 7 AM IST), 10 points: tokens (2: cut a page of their text, what splits, a year's cost with thinking); where it invents (3: three real questions asked of a brain alone, one invented detail traced); the facts it needs (3: knowledge or tools, one fact put in the prompt and tested); run NB2 (2: three exercises by hand, two short answers). [click] Use today's words.

**65 · Next time: The Memory.** Sat 7 Nov.

---

## Open items (as of 2026-10-30)
- The 3D slides use `brain3d/deck.js` (step counts 2/3/3/4/3/4/4/3/3 from its README). The component has no "whole machine" state, so slide 60 shows section 9's end state and links the standalone autoplay.
- Deck QA flags one label inside the brain3d component on slide 32 (section 5: an SVG label "block 1 … block 24: 56%" outside the frame when fully revealed). That is the 3D builder's file.
