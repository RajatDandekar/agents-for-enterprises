# Speaker notes · v5 section `dense` (dense retrieval on one document)

Every number is in `v5/dense_data.js`, built by `experiments/v5_dense_build.py` from `experiments/logs/v5_dense.json`,
`v5_dense_scan.json`, `v5_dense_probes.json` (made by `experiments/v5_dense_modal.py` on Modal, L4 GPU) and `rag_grid.json`.
D = `01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf`; Q = Emma's question (Q-EMMA). Model: bge-small-en-v1.5, as `rag.Embedder` loads it.

## Part slide · “How does a computer find the one clause that answers Emma?” (pill: “RAG, by eye”)
Pasting everything did not fit. Today we find the clause by hand first, then watch the machine do it, step by step, on one document.

## What RAG Means
Name it before we build it. RAG = Retrieval-Augmented Generation, word by word:
Retrieval: search the documents for the few passages that answer. For Emma on D: the 5 of D's 15 chunks closest to her question.
[click] Augmented: those passages go into the prompt next to the question, each with where it came from. Her question then 5 chunks = 765 tokens (`play.s200-o15.topk[4].tokens`).
[click] Generation: the model answers from those passages and cites them, so a person can check (§6.2, §6.4, POL-PUR-001 v4.1).
[click] Against the last section (figdata `paste.sample`): pasting the 648-file part read 740,199 tokens and cost $0.61 a question; the whole dump, 4,692,229 tokens, fits no model.
The name: Lewis et al., 2020 (“Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks”). Mention it, do not dwell.

## RAG in One Figure
`FIGS.dense_flow` built box by box (8 clicks). Say what each box does; we open each one on D in the slides that follow, and a small
“you are here” copy of this figure sits top right on the first slide of each stage.
Box 1, Parse (done in the parsing section; D: 26 units, 2,178 tokens).
[click] 2 Chunk (about 200 tokens, on section edges, header line; D: 15 chunks). [click] 3 Embed each chunk (bge-small, 384 numbers; the strip is chunk #5's real vector).
[click] 4 Store (vector + text + citation; the whole dump holds 28,953 chunks). The top row runs once, before any question.
[click] 5–6 The question, embedded by the same model (dashed line: same model, same space).
[click] 7 Find the k nearest: cosine to every stored chunk, keep the k highest (arrow from the store: “search”). k = how many go to the model; defined properly when the question lands.
[click] 8 Build the prompt: instructions, the question, the k chunks with citations. [click] 9 Cited answer.
[click] The three words of the name under the boxes: Retrieve = boxes 5–7, Augment = 8, Generate = 9.
The later sections reuse this figure: `data-hybrid="1"` adds BM25 beside dense, RRF fusion and the reranker.

## One Document, One Question
D has 4 pages; the structured parser turns it into 26 units, 2,178 tokens. Small enough to check everything by eye.
[click] Emma's question.
[click] The plan: we read D and write the ideal answer ourselves, then check every machine step against it.

## Reading D · The Front Page
The real page 1 (rendered on Modal at 200 dpi; boxes drawn around its real text lines).
[click] The four fields that decide if a document applies today: id, version, effective date, status.
[click] The version history: 1.0 in 1998 to 4.1 in 2026. Old copies are still in the dump (we meet one at the end).
[click] The 4.1 row: §6.2 extended to chargers, §6.4 added.

## Reading D · Sections and Clauses
[click] Sections 1 to 4 on page 1 (5 to 9 on page 2). [click] Clauses, one rule each. [click] §3.3, £50,000: an amount we meet again in the failure cases.

## Reading D · §6 and the Appendices
[click] The four clauses of §6. [click] §6.2 and §6.4 are the two about Emma (battery packs are lithium-cell parts). [click] Appendix A defines a lithium-cell part; Appendix B restates the rules as staff questions.

## The Ideal Answer, From D Alone
[click] §6.2, quoted from the parsed text. [click] §6.4. [click] What D cannot answer: D never names Brightcell, Voltway, BAT-500 or £104 (checked in the parsed text). The rest needs other documents.

## D in 15 Chunks
(Mini flowchart top right: “chunk” lit.)
The default chunker (structure-aware, 200 tokens, 15% overlap, header prefix) gives 15 chunks; mean 189 tokens.
[click] The header prefix. [click] Overlap, honestly: in structure-aware chunking it only acts when a section must be cut; in D at 200 tokens only the header table (253 tokens) is cut, between table rows longer than the 30-token overlap budget, so nothing repeats (s200 with 0% and 15% give identical chunks). At 50 tokens #11 repeats “centre that will carry the spend.” from #10. [click] We follow #5: §6.1–§6.4, 194 tokens.

## The Chunk We Follow
Chunk id `01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf#c5`, cite “POL-PUR-001 v4.1, p.2, § 6. Supplier qualification”.
[click] Highlight §6.2 and §6.4 inside it; it holds both facts (F-PUR-6.2, F-PUR-6.4).

## From Chunk to 384 Numbers
(Mini flowchart: “embed” lit. This is the inside of box 3; figure renamed `FIGS.dense_embed`.)
Six boxes, one per click. Facts read from the model on Modal: modules Transformer → Pooling → Normalize; pooling mode “cls”;
BertModel, 12 layers, 12 heads, 384 wide, vocabulary 30,522, max 512 pieces. Chunk #5 = 194 o200k tokens = 194 WordPiece pieces.
Check we ran: the final vector against the normalised [CLS] row: cosine 0.9999 (against the mean of rows: 0.92), so bge really uses CLS.
[click] tokenizer [click] encoder [click] one vector per piece (194 × 384) [click] pool + normalise ([CLS] length 9.16) [click] 384 numbers.

## The Pieces the Model Reads
All 194 pieces. [click] `##` continuation pieces. [click] Codes in fragments. ERR-PO-0412 → er ##r - po - 04 ##12 (logged in `v5_dense_probes.json` → wordpieces).

## Cosine Similarity, in Two Dimensions
Q along the x-axis; each chunk drawn at its true angle to Q, θ = arccos(cosine in 384-d). This keeps the angle to Q exact, not the angles between chunks.
#1 version history 0.673 (47.7°), #5 §6 0.644 (49.9°), #14 App. B 0.460 (62.6°).
[click] [click] reveal the chunks one by one.

## 384 Numbers, One Cosine
[click] the question's vector (with bge's query instruction, as `rag.Embedder.query` adds it). [click] the dot product = 0.6444.

## Every Chunk of D, in 3D
(Mini flowchart: “store” lit: this is what the store holds, 15 vectors of D.)
PCA fitted on the 15 default chunk vectors; PC1 19%, PC2 17%, PC3 11% = 47% of the variance. Drag to rotate; hover reads the chunk; click pins it. Never steals keys.
[click] rings: #5 (solid), #12 App. B battery Q&A (dashed: it restates §6.2 and §6.4 in plain words).

## Emma's Question Lands
(Mini flowchart: “question”, “embed” and “top k” lit.)
The star drops in, projected with the same PCA.
[click] Define top-k: k = how many of the nearest chunks we hand to the model; here k = 5. Lines to the top 5 (cosine in 384-d):
#1 0.673, #12 0.667, #5 0.644, #7 0.595, #2 0.589. All three nearest are about the battery rule; §6 (#5) is 3rd; none says Brightcell.
[click] What k changes (`play.s200-o15.topk`): k = 1 sends 91 tokens and misses §6; k = 5 sends 765 with §6.2 and §6.4 inside;
k = 10 sends 1,535 with the same 108 answer tokens. Bigger k: more context, more noise, more tokens. Say once: the RRF constant (60)
in the next section is a different number; we never call it k.
(Without the query instruction the order of the top 3 is the same; §6 stays 3rd: `prefix_check`.)

## Ask the class · chunk size
Let them pick. §6.2 is 73 tokens long; §6.4 is 35.

## The Chunk-Size Playground
Clicks walk 200 → 50 → 800 → whole document → 200; students can click any button. Axes fixed (PCA of the 200-token chunks).
- 50: 64 chunks; §6.2 cut into 3; the chunk with the rule ranks 29th; top 5 = 179 tokens, 22 of them answer.
- 800: 4 chunks; rule 1st; 3 chunks over 512 pieces.
- whole: 1 chunk, 2,183 body tokens; its vector reads only the first 20% of the text: it stops before §6.

## Too Small, Too Large
The table, then the reasoning: 200 tokens (§6 rank 3, 765 tokens in the top 5) or one chunk per section (rank 2, 686 tokens).
[click] smaller sizes [click] larger sizes. Note 400 ranks the rule 1st but carries 1,751 tokens for five chunks.

## Ask the class · the whole dump
Guess before the grid.

## The Whole Dump, One Knob at a Time
From `rag_grid.json` (Chroma HNSW, ef 4,000), dense only, bge-small, structured parser, structure-aware chunks, 15% overlap:
recall@5 200 → 0.561, 400 → 0.556, 800 → 0.551, 1,200 → 0.493. [click] overlap at 200: 0.551 (0%) vs 0.561. [click] parser: plain 0.488, structured 0.561.
Our exact (numpy) search on the same vectors gives 0.566 at 200: the small gap is HNSW versus exact search and fp16 batch encoding.

## Other Knobs: k, the Header, the Model
Subtitle reminds what top-k is. Clicks: k = 1, k = 10, header prefix off, e5-small. Header off: same ranks on D (every chunk of D carries the same header; its job is
across documents, see Old Copies); #5's cosine 0.635 vs 0.644. Other models on D, rank of §6: bge-small 3, bge-base 2, e5-small 5,
gte-small 3, nomic 3. e5-small cosines run 0.76–0.84 against bge-small's 0.46–0.67: compare ranks, not scores.

## Where Dense Fails · Exact Codes
MAN-ERR-72, 88 chunks. Nearest: ERR-MAT-0412 (0.713), then other error entries; the chunk holding ERR-PO-0412 (it starts at ERR-PO-0105) is 6th (0.682).
Whole dump: that entry ranks 106th; the first answer chunk of any gold document (MAN-PUR-72 §17) ranks 87th. [click] lines [click] why.
Probes: “ERR-PO-0412” vs “ERR-PO-0413” 0.944, vs “ERR-MAT-0412” 0.884, vs its meaning 0.532.

## Where Dense Fails · Codes a Digit Apart
Q-401: the current BAT-500 row ranks 102nd; above it, rows of an old 2025 export (BAT-500, BAT-RNG-250, BAT-375, BAT-625-48, BAT-625, BAT-250) and e-mails.
Current rows BAT-500 vs BAT-375 0.9994, vs BAT-625 0.9982, vs BAT-250 0.9991. [click] list [click] why + probe.

## Where Dense Fails · Amounts and Dates
Q-510: the best answer chunk (Amendment 3 §3) ranks 1,004th; the top 8 are sales-order rows. Probe: §3.3 with £25,000 0.959, £30,000 0.990,
£5,000,000 0.997; the question is 0.600–0.602 to every variant.

## Where Dense Fails · Before or After
Q-612: D's §6 chunk ranks 8,729th in the whole dump (7th of 15 inside D); an old SOP v2.0 chunk with the fact is 3,848th.
Probe: “before” → “after” 0.981; “need not” 0.903; unrelated 0.543. The question is closer to the “after” sentence (0.625) than to the real one (0.595).

## Where Dense Fails · Old Copies
Q-202: #1 is POL-PUR-001 v3.0 (2019, £30,000, header says SUPERSEDED); #5 and #7 also old copies; #4 the amendment, not yet in force.
Current §3.3 chunk: 18th; with superseded and future chunks filtered out before ranking: 12th. v4.0 vs v4.1 copy of the same chunk: 0.998; v3.0: 0.836.

## Where Dense Fails · Table Rows
Q-407 (PRD-05 open?): plain parser rank 84, structured 15. Not always: Q-401 plain 83, structured 102. Over 34 table questions
(grid, dense, 200 tokens): recall@5 plain 0.21, structured 0.26.

## Where Dense Fails · A Crowded Topic
Q-003: 887 chunks mention lithium or batteries; 2,173 chunks are closer to the question than the carrier notes, 232 of them battery chunks. Carrier notes rank 2,174th.

## Where Dense Wins · Different Words
Q-101 “How do I onboard a new supplier?”: dense puts onboarding text in all ten top places; the procedure's answer chunk is 7th. A keyword match (BM25, next section) ranks it 619th. Hand over to the lexical section here.

## Where Dense Retrieval Fails, Summed Up
[click] ×4 reveal the second row, then the caption. Ranks: 106, 102, 1,004, 8,729; 0.998; 84 → 15; 2,174; 7 (keyword 619).

## Emma's Question, End to End
The recap: `FIGS.dense_flow data-values="emma"`, every box filled from our run on D (no new numbers):
D, 4 pages → 26 units, 2,178 tokens; 15 chunks, 189 tokens on average, §6.1–6.4 all in #5 (194 tokens); 15 × 384 numbers;
the question: search instruction + question = 27 WordPiece pieces → 384 numbers; top 5 by cosine: #1 change log 0.673,
#12 App. B 0.667, #5 §6 0.644 (lit), #7 App. A 0.595, #2 §1–3 0.589; prompt: her question then 5 chunks, 765 tokens, 108 of them
§6.2 and §6.4 (pasting the 648-file part: 740,199 tokens); the answer can cite “POL-PUR-001 v4.1, p.2, § 6. Supplier qualification”.
Honest: the answer box says what the answer step has to work with; we did not run the generation step on D alone here.
[click] On D retrieval did its job; the failure cases show where the whole dump is harder. Then the class question.

## Ask the class · four questions
Real golden questions: Q-117, Q-704, Q-108, Q-021 (from the pass-1 scan).

## Check · dense retrieval
[click] 1 and 3 (rank 1 and 1); ERR-SUP-0031 487th; e-mail retention 49th. [click] WordPiece, 12 layers, CLS, normalise. [click] 2,183 tokens; reads 20%.

### Honest caveats for the lecturer
- Whole-dump ranks use exact search over the stored grid vectors (float16, renormalised), not Chroma's HNSW; the grid's own numbers use HNSW.
- Deep ranks differ by a few places between pass 1 (questions encoded in one fp16 batch) and pass 2 (one at a time): Q-510 1,002 vs 1,004, Q-612 3,823 vs 3,848, Q-003 2,173 vs 2,174. The slides use pass 2 for the failure cases.
- “Gold” = the course's loc_match (file + page/row); “answer chunk” = a chunk containing a gold fact's needles.
