# L3 v5 · section `lexical` · speaker notes

One document (D, POL-PUR-001 Purchase Policy v4.1, 15 default chunks) and one question (Emma's, Q-EMMA) all the way
through. Every number is from `experiments/logs/v5_lexical*.json` (made by `experiments/v5_lexical_modal.py` on Modal with
the course code: `rag.tokenize`, `rag.BM25`, `rag.rrf`, `rag.Reranker`), the BM25 walk-through from
`logs/v5_lexical_walk.json` (`experiments/v5_lexical_walk_modal.py`: `rag.BM25` built on D's 15 chunks, every piece read from
the built index), the dense ranks from the dense section's `logs/v5_dense_failures.json`. Chunks are numbered as their ids
(`…pdf#c0` to `#c14`).

Words used on the slides (review of 5 Nov 2026): `rag.tokenize` is called **our word splitter** (code name in small type
only); BM25's units are **words**, never "tokens" (tokens and pieces belong to the model's WordPiece tokenizer in the dense
section). The weight has three coloured parts, always in the same colours: **idf** green (across all chunks),
**saturation** orange (inside this chunk), **length** plum (inside this chunk, against the average). The RRF number 60 is
**the RRF constant** (`rag.RRF_K`), never bare "k"; **top-k** is only the number of chunks handed to the model.

## Part slide · "Can plain word counting find what the vectors missed?"
Bridge from the dense section: it ranked the ERR-PO-0412 entry 87th and the BAT-500 row 102nd. Today: a method that only
counts words, built from zero on D, then how to combine both, then a model that reads.

## Keyword Search From Zero
Keyword search compares words, so first decide what a word is. Say plainly: this step only splits text into words for
counting. It is our own small word splitter, a function in the course's `rag.py` (so the code calls it `rag.tokenize`). No
model is involved, and it has nothing to do with the WordPiece tokenizer the embedding model used in the last section.
- [click] Lower-case, split on anything that is not a letter, digit or £: 12 words.
- [click] Drop stop words: 56 common words in `rag.STOP`. can, i, the, from go.
- [click] Light stemming: a plural s is dropped from words longer than four letters. packs → pack. Nothing else changes.
- [click] Eight words. Point out the wart: "they" is not on the stop list, so it stays (it will add noise on the BM25 slide).
  £104 stays one word. The same splitter cuts every chunk, header line included.

## Keep Codes Whole, and Split Them
The last rule of our word splitter: a code like ERR-PO-0412 is kept whole **and** its parts are added. The same BM25 over
MAN-ERR-72's 88 chunks; only the way the code is split changes. Rank of the chunk holding the ERR-PO-0412 entry.
- Split only (err, po, 0412): rank 2. ERR-MAT-0412 NO GRN FOR PO LINE wins, 7.36 against 6.44: it says 0412 twice.
- [click] Whole only (err-po-0412): rank 2. ERR-PR-0007 wins on the word "mean" (5.62 against 3.96).
- [click] Whole and split, our word splitter: rank 1, 10.46 against 7.38. The whole word separates the two codes.
- [click] Typed differently, "PO error 0412, what is it?": with both, rank 2 in the manual and 2 in the dump; whole only:
  72 and 324. The parts rescue the person who does not type the hyphens.
- [click] Why: err-po-0412 is in 26 of 28,953 chunks; 0412 in 37, po in 5,403.
- The white box at the bottom (always visible) is the whole splitter in one sentence: lower-case · split on anything not
  a letter or digit · drop 56 common words · keep codes whole and add their parts · drop a plural s. "Nothing else."

## Which Chunks Hold Which Words
The word × chunk table for D. Columns are D's 15 chunks (0 to 14). The rows come in two labelled groups.
- First group, **Emma's words**: her question after our word splitter, what BM25 looks for. battery and pack: chunks 1, 5,
  12. they: chunks 4 and 12.
- [click] Five of the eight (buy, brightcell, energy, quote, £104) occur in no chunk of D. Brightcell is nowhere in D.
- [click] Second group, **D's own words for the same ideas**: bought (chunk 5) and buys (chunk 2) for "buy", purchase (all
  15) for "buy", quotation (chunks 5 and 12) for "quote". This answers "where do bought, buys and quotation come from?":
  they are D's words, read from its text. BM25 does **not** match them to Emma's words: it matches exact words only.
- [click] So these counts add nothing to her score. purchase is in all 15 because every chunk's header line
  "[Purchase Policy · POL-PUR-001 …]" says it (next slide).

## Rare Words Matter
Intuition before formula: a word in every chunk cannot tell chunks apart; a word in three chunks narrows to three.
- Left: D counts (of 15). purchase 15, battery 3.
- [click] The whole dump (log scale): order 6,269 chunks, battery 873, brightcell 6, buy 1. Staff write purchase and
  order, not buy.

## From Counts to a Weight: idf
Introduce the word **weight** here: a chunk's BM25 score is a sum of one weight per question word the chunk contains. The
weight has three parts (the formula strip across the top, two parts dimmed). Part 1, green: idf, measured **across all
chunks**. idf(word) = ln(1 + (N − df + 0.5) / (df + 0.5)), the line in `rag.BM25`.
- battery is in 3 of D's 15 chunks: ln(1 + 12.5 / 3.5) = 1.52. purchase, in all 15: 0.03. With N = 15 the rarest possible
  word gets 2.37. The bars show D.
- [click] The whole dump: brightcell, df 6, ln(1 + 28,947.5 / 6.5) = 8.40; order, df 6,269: 1.53. The bars switch to the
  dump: buy 9.87, £104 9.36, brightcell 8.40, energy 7.30, quote 5.91, they 5.54, pack 4.13, battery 3.50, purchase 2.07,
  order 1.53. Students can toggle the buttons.
- [click] idf belongs to the collection you search, not to English. It is counted once, before any question. On the next
  two slides idf stays fixed: "the idf we computed on From Counts to a Weight".

## Saturation: Repeats Inside One Chunk
Part 2, orange: measured **inside one chunk**. tf = how many times the word appears in that chunk. Make the contrast
explicit, it is Dr. Dandekar's own reading: idf is across chunks, saturation is within one chunk.
- The real case (right): "supplier" is in 9 of D's 15 chunks, so its idf is 0.52 (across chunks, from the idf slide).
  Inside §6, chunk 5, it appears 10 times (tf = 10, inside this chunk). That is where the "ten mentions" are.
- The dashed grey line is a plain count: 10 mentions would count 10. k1 = 1.2 sets the ceiling, k1 + 1 = 2.2.
- [click] The BM25 curve, tf·(k1 + 1) / (tf + k1), at average chunk length (length part 1; §6 is 104 words against an
  average of 100.9, so it is almost exactly average).
- [click] One mention 1.00, two 1.38, ten 1.96: the second adds less than the first, the tenth almost nothing.
- [click] The same numbers in words; the tenth adds 0.023. Drag k1: small k1 saturates at once (presence is all), large
  k1 trusts counts.
- [click] So §6's ten "supplier"s weigh 0.52 × 1.96 = 1.02 (rag.BM25 stored 1.0215, with §6's real length part 1.023),
  not 0.52 × 10 = 5.21.

## Long Chunks Are Damped
Part 3, plum: measured **inside one chunk, against the average chunk**. Show where it enters the formula: the length part
1 − b + b · dl / avgdl multiplies k1 in the denominator, so in a long chunk each mention counts less.
dl = the chunk's length in words (after our word splitter), avgdl = 100.9, the average over D's 15 chunks, b = 0.75.
Chunk 1 (version-history line, 57 words) and chunk 5 (§6, 104 words; its §6.2 clause shown) each say battery once and
packs once.
- [click] dl / avgdl: 0.565 and 1.030.
- [click] Length part with b = 0.75: 0.674 and 1.023.
- [click] Weight of battery (idf 1.52, tf 1): 1.52 · 2.2 / (1 + 1.2 · length part) = 1.849 against 1.501 (exactly what
  rag.BM25 stored). Drag b to 0: length is ignored and both weigh the same. This is why the version line will outrank
  the rule.

## BM25 for Emma's Question, on D
The full formula, once, with the three parts in their colours and the legend: idf across all chunks; saturation inside
this chunk; length inside this chunk, against the average. A chunk's score = the sum of the weights of the question's
words it contains. Each cell of the table is one weight; the five words D never uses share one column of zeros.
- Chunk 12 (FAQ on battery packs): battery 1.94 + pack 1.94 + they 1.67 = 5.54, rank 1.
- [click] Chunk 1 (version history): 1.85 + 1.85 = 3.70, rank 2.
- [click] Chunk 5 (§6, holds §6.2 and §6.4): 1.50 + 1.50 = 3.00, rank 3.
- [click] Chunk 4 (§5 Approval limits): "they" alone, 2.02 ("an order they raised"). The other 11 chunks hold none of
  Emma's words: score 0, tied.
- [click] Read it: the FAQ restates §6.2 and §6.4, good. The version line is short, so length lifts it above the rule.
  "they" is noise. On D, dense ranked the same three on top (chunks 1, 12, 5).

## When a Question Arrives
What BM25 actually does at question time, in five clicks, on the FAQ that wins (chunk 12) and on §6 (chunk 5). Numbers
from `logs/v5_lexical_walk.json`.
- 1 · Split the question with our word splitter: buy, battery, pack, brightcell, energy, they, quote, £104.
- [click] 2 · Find: for each chunk, which of those words it holds and how often. Chunk 12: battery ×2, pack ×2, they ×1;
  not buy, brightcell, energy, quote, £104. Chunk 5: battery ×1, pack ×1. Every chunk is checked; most hold none.
- [click] 3 · Weigh each word found: weight = idf × tf · 2.2 / (tf + 1.2 × length part). Chunk 12 (129 words, length part
  1.21): battery 1.52, tf 2 → 1.94; pack the same; they, idf 1.86, tf 1 → 1.67. Chunk 5 (104 words, 1.02): battery 1.52,
  tf 1 → 1.50; pack 1.50. The idf column is the same in both chunks (across chunks); tf and length differ (inside each).
- [click] 4 · Add: chunk 12 = 1.94 + 1.94 + 1.67 = 5.54; chunk 5 = 1.50 + 1.50 = 3.00.
- [click] 5 · Sort all 15 chunks: chunk 12 5.54, chunk 1 3.70, chunk 5 3.00, chunk 4 2.02, the other 11 at 0, tied. In
  code all of this is `rag.BM25.scores`: the weights for every (chunk, word) are computed once when the index is built,
  so a question only looks up and adds (0.31 ms over all 28,953 chunks).

## Where BM25 Wins
The dense section's failure cases, over the whole dump; rank of the first chunk that holds the answer.
Dense ranks from `v5_dense_failures.json`; BM25 ranks from our run (identical to the dense section's own BM25 ranks).
- ERR-PO-0412: dense 87, [click] BM25 1. BAT-500 reorder level: 102 → 67. BAT-375 rate: 622 → 30. £40,000 direct order:
  1,004 → 5. UN 38.3 after the first order: 3,848 → 22. Lithium carrier: 2,174 → 2. Superseded copy: dense 4, BM25 9.
- [click] The words that carried BM25 (their weight in the answer chunk): fix 11.4 and err-po-0412 10.7; 500 and bat-500;
  375 and bat; 000 and direct (note: £40,000 is cut into £40 and 000, and £40 is not in the answer chunk); 38.3 and un;
  carrier.
- [click] Over the golden set (dense section's numbers): exact-code recall@5 dense 0.18, BM25 0.63; table lookups 0.27
  against 0.65. The superseded copy is an exception for both: only metadata tells versions apart.

## Where BM25 Loses
- On D: buy vs bought/buys/purchase, quote vs quotation (the second group on Which Chunks Hold Which Words). Exact words
  only; our word splitter only drops a plural s.
- [click] The dense section's own win: "How do I onboard a new supplier?" onboard is in no chunk; the SOP says
  Onboarding. BM25 619, dense 7.
- [click] Emma on the whole dump: brightcell (idf 8.40) and £104 (9.36) fill BM25's top 6 with the Brightcell e-mails and
  a meeting note. D's §6 falls to rank 255 (the FAQ chunk 12 to 16). Emma never wrote the rule's words.
- [click] So: run both and merge. Hybrid. (Smarter word splitters that turn bought into buy, and synonym lists, help a
  little.)

## Two Lists, Two Scales
D, Emma's question. BM25 on the left (0 to 5.54, 11 chunks at exactly 0), dense on the right (0.460 to 0.673).
- [click] The dense list. [click] Lines join the same chunk: the top three agree (12, 1, 5 against 1, 12, 5).
- [click] Why not add the scores: different units. BM25 would decide alone; on the whole dump its top score is 53.1 for
  Emma, while the best cosine is 0.835. The ranges move with every question.

## Reciprocal Rank Fusion
RRF score = 1 / (60 + rank in BM25) + 1 / (60 + rank in dense). Only positions. Introduce the number here, in the box:
**60 is the RRF constant** (`rag.RRF_K`), the same for every question. Say explicitly that it is **not** the top-k from the
last section (how many chunks we hand to the model, 5 or 10).
- Ranks in each list. [click] Each list's share: 1/(60+1) = 0.016393, 1/(60+2) = 0.016129, …
- [click] Sum and fused rank: chunk 12 0.032522, chunk 1 0.032522, chunk 5 0.031746, chunk 2 0.030536, chunk 7 0.030118,
  chunk 0 0.030090.
- [click] The tie: (1, 2) and (2, 1) give the same sum. Say it plainly: RRF has no LLM, no model, nothing trained. Six
  lines of `rag.rrf`.

## The RRF Constant
Interactive: the same formula as `rag.rrf`, on the logged lists (60 reproduces the logged fused ranks). The slider is the
RRF constant; it changes the fused order, never top-k.
- Emma on D: the order is the same for every value (the lists agree).
- [click] ERR-PO-0412 on the dump (top 20 of each list, as `rag.Retriever` fuses them): at 60 the answer chunk (QRC-03,
  BM25 1st, not in dense's top 20) is fused 5th, behind po_save rows that are mid-table in both lists.
- [click] At 1: it is fused 2nd, tied at 0.5 with dense's 1st (ties keep the dense list's order). At 5: 3rd; from 30 up:
  5th. A small constant rewards the top of either list; a large one rewards agreement.
- Weighted score fusion is the alternative: rescale scores, α·dense + (1 − α)·BM25, α tuned on the golden set.

## RRF Is Arithmetic. The Reranker Is a Model.
Students (and we) often mix these up. RRF: positions in, list out, no text read. [click] The reranker: BAAI/bge-reranker-base,
a cross-encoder (XLM-RoBERTa, 278 million weights), reads the question and one chunk together and outputs one relevance
number. Not a generative LLM: it writes no text. (RRF's card: 1 / (60 + rank) per list, 60 = the RRF constant.)
- [click] The same two chunks of D: RRF 0.032522 for both; the reranker 0.00051 (FAQ) and 0.00029 (version line).

## Bi-Encoder and Cross-Encoder
- Left: the question and chunk 5 go through bge-small-en-v1.5 (33.4 M weights) separately; 384 numbers each; cosine
  0.644. Chunk vectors are computed once for all 28,953 chunks.
- [click] Right: one input, question and chunk together: 228 tokens for Emma + chunk 5 (the real tokenizer output is shown:
  <s> question </s></s> chunk …). Every layer sees both texts. One number: 0.0031 (sigmoid of the model's single output).
- [click] The cost: nothing can be precomputed, so every question needs a pass per chunk. 41 ms for 20 on an L4 GPU.

## The Reranker on D
BM25's order of D (left) against the reranker's (right).
- [click] §6 rises from 3rd to 1st; the FAQ is 2nd; the version line drops from 2nd to 4th.
- [click] Highlight those three. Scores are tiny (top 0.0031) because no chunk of D says whether Brightcell may supply:
  the reranker is honest that none answers the whole question. We only use the order.

## The Real Top 20, Reordered
The default pipeline (`rag_best.json`): BM25 top 20 over the whole dump → reranker → keep 10.
- [click] After the reranker. [click] Highlights: the quotation e-mail (holds 2 golden-set facts: the £104 price and the
  certificate status) 2nd → 1st; D's FAQ 16th → 10th, inside the top 10 we hand to the model (top-k = 10). D's §6 is BM25's 255th, so it is not among the 20.
  The reranker can only reorder what search hands it.

## What Reranking Costs
Medians on Modal: BM25 0.31 ms (4 CPU cores); embedding the question 11.4 ms (L4); [click] reranker on 20 pairs 41.1 ms on
an L4 GPU (p95 43.0); [click] 2.4 s on 4 CPU cores (p95 2.5 s); [click] gemini-3.8-flash asked to order the same 20:
21.8 to 29.3 s per call (three runs), 4,670 tokens in.
- [click] The costlier variant: hosted rerank APIs, or prompting an LLM. Our LLM run put D's FAQ 3rd or 4th (the
  cross-encoder: 10th), but each run gave a different order and each took over 20 s; the cross-encoder gave the same order
  in 10 of 10 runs.

## The Whole Pipeline, With Keywords
The flowchart from the start of "RAG, by eye", now complete. `[click ×11]` box by box: the indexing row as before; then the question goes to **two** searches, dense and BM25; RRF adds 1/(60 + rank) from each list (60 is the RRF constant, not top-k); the reranker re-reads the top 20 and keeps the best k; prompt; cited answer. Say: "Every box on this slide is something we have now opened by hand on one policy. Next: which settings win on all 224 questions." Be honest ahead of time: this is the general shape; on our data the measurement will drop the dense branch (BM25 + reranker wins).

## Ask the class (q hero)
"Over the whole dump, BM25 ranks D's §6 255th for Emma, and the reranker sees only the top 20. What would you change?"
Discussion facts (measured): 1 · reranking 300 would include it, at about 41 ms per 20 pairs on the GPU (about 0.6 s per
question by that rate); 2 · dense ranks §6 about 120th (dense section), so hybrid's top 20 does not reach it either;
3 · the RRF constant changes nothing when neither list has it; 4 · a second search with the rule's words is what the agent does later in
the lecture (it calls search_docs twice).

## Check · BM25, RRF and the reranker
1. [click] D writes bought, buys and purchase, never buy, and BM25 matches exact words only (the second group on Which
   Chunks Hold Which Words; our word splitter only drops a plural s).
2. [click] idf is measured across all chunks (how many contain the word); saturation and length inside one chunk.
3. [click] (1, 2) and (2, 1) both give 0.032522; the reranker breaks the tie: §6 1st, FAQ 2nd, …, version line 4th.
4. [click] 41.1 ms per 20 pairs on the L4 → about 59.5 s for all 28,953 at that rate; 2.4 s for 20 on 4 CPU cores.
