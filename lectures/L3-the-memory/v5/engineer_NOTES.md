# L3 v5 · RAG engineering (section `engineer`) · speaker notes

Every number on these slides is read from `v5/engineer_data.js`, written by `experiments/v5_engineer_slices.py`
(log: `experiments/logs/v5_engineer_slices.json`). Sources underneath: `rag_grid.json` (2,112 retrieval rows),
`rag_best.json`, `rag_answers/*.json` (per-question records of the 9 answered configs), `rag_failures.json`,
`race.json`, `audit.json`, `v5_dense.json` (the one-document playground) and the Volume `northbridge-raglab`
(`/vol/grid/*.json`, container wall times).

Revised 5 Nov 2026 after Dr. Rajat Dandekar's review: the class question spells out each knob; "The Grid of Knobs"
now separates index knobs from search knobs and defines top-k; "The Code That Runs It" is removed (its machine and
time line is on the grid slide); "Your Guesses Against the Data" is one row per knob with bars and a why. Words as in
the earlier sections: top-k (k = how many chunks go to the model), "the RRF constant, 60", the header line.

## Part slide · "Which settings win on all 224 questions, and how would we know?"
On one document we could see every knob work. Now we have to choose settings for Henrik's whole dump, and the only
honest way is to measure on everything.

## From One Document to the Whole Dump
One policy: 26 units, 15 chunks, one question. We could read every chunk.
[click] The dump: 693 files, 28,953 chunks with the chosen cut, 224 golden questions of ten types.
[click] The grid is 2,112 settings × 224 questions = 473,088 searches. Nobody reads that. We decide with averages,
measured the same way for every setting.

## (q hero) Four settings for the whole dump: what is your guess for each?
Read the four lines out, so nobody needs the earlier slides to answer:
chunk size = how many tokens go in one chunk (200, 400, 800, 1,200); search = dense (by meaning), BM25 (by matching
words) or hybrid (both lists fused with RRF); reranker = re-read the top 20 with the cross-encoder and reorder them,
yes or no; top-k = how many chunks go to the model with the question (3, 5, 10).
Ask for one line in the chat: size · search · reranker · top-k. Keep the chat open: we read the guesses on
"Your Guesses Against the Data".

## Recall@5 and MRR, on Emma's Question
Emma's question searched in the whole dump with BM25 then the reranker (bge-reranker-base over the top 20,
structure-aware 200-token chunks): the setting we end up choosing. The top 10 as the chosen configuration returned them.
[click] Gold marks: passages from files her golden-set record lists (same file, same page where the gold names one).
Rank 1 and rank 5 are the Brightcell quotation e-mail.
[click] Recall@5 for this question is 1: a gold passage is in the top 5. If none were, 0.
[click] Reciprocal rank: 1 / rank of the first gold passage = 1/1. At rank 2 it would be 0.5.
[click] But only 2 of 11 gold passages were found (coverage@5 = 0.18). The §6.2 clause itself (page 2) is not in the
top 10. Rank 10 is the policy's own FAQ on page 3, which restates §6.2 and §6.4, but the golden set lists page 2, so
the metric does not count it. Recall@5 is generous: one hit is enough. That is why we also score the answer.

## From One Question to 205
Four real questions from the same run: Emma (rank 1 → 1, 1.00), ERR-PO-0412 (rank 2 → 1, 0.50),
[click] the IT service desk extension (rank 3 → 1, 0.33), the ISO 9001 date (not in the top 10 → 0, 0).
19 of the 224 have no passage to find (not in the documents, refusals): they are scored on the answer only.
[click] The rank of the first gold passage for all 205 scored questions: 109 at rank 1, 36, 18, 11, 9 at ranks 2–5,
4 at ranks 6–10, 18 with no gold passage in the top 10.
[click] Recall@5 = 183 of 205 = 0.893. MRR = the mean of 1/rank = 0.673. Both recomputed from the records and equal
to the grid row.

## Latency: p50 and p95
Histogram of the 224 search times of the chosen configuration (0.5 ms bins), timed one question at a time on one
Modal L4 (4 vCPU, 16 GiB).
[click] p50, the median: 44.5 ms. Half the questions were at or under it.
[click] p95: 48.5 ms. 95% at or under; 12 of 224 took longer (slowest 54.8 ms). Emma remembers the slow one.
[click] Target p95 ≤ 200 ms: met.
[click] Time to answer adds the answer model (gemini-3.8-flash, with thinking): p50 5.8 s, p95 13.2 s against a 4 s
target. Missed. Search is 0.4% of it.
Note: the grid timed the same configuration separately at p95 47.6 ms (the panels); this slide uses the answer run's
own timings (48.5 ms). Two timing runs, same machine type.

## Cost per Question
Emma's answer: 2,368 tokens in × $0.825/M = $0.00195.
[click] 251 tokens out × $4.125/M = $0.00104; total $0.0030.
[click] Mean of all 224: 2,307 in, 103 out → $0.0023 a question.
[click] 224 questions a day ≈ $0.52. Checking answers with a second model (the judge, next slide) is the cost of
testing, not of answering: $0.92 for 2,016 checks (9 answered settings × 224).
Search costs nothing per call: BM25 and the reranker run in our container.

## Judging One Answer
The real answer RAG gave Emma at the 150-word cap (before the race).
[click] Exact facts: 4 of the 7 must-contain strings; £104.00, £119.00 and PUR.CERT_CHK missing → not correct.
[click] The judge (gemini-3.8-flash against the reference answer): not correct, and its reason.
[click] Citations: each cited passage holds what it is cited for → correct. 5 passages cited.
[click] Over all 224: judge 87.1%, exact facts 86.2%, citations 92.7%; judge and exact-fact check agree on 94.6%
(κ 0.77 in rag_best.json).
The race (later) reruns at 250 words, where the cap stops cutting facts.

## The Grid of Knobs
Two kinds of knob. Say it plainly: some knobs change what is stored, the rest change only how we search it.
Index knobs (orange): parser 2 (plain, structured; structured also puts the header line on each chunk) × chunker 3 ×
chunk size 4 × overlap 2 = 48 indexes. Each is built once: cut the dump, embed every chunk, build the BM25 table. The
48 tiles: rows = parser · chunker, columns = size, each pair = overlap 0% / 15%. Blue: the index we end up choosing.
The embedding model also changes what is stored, so every index holds all 5 vector sets (bge-small, bge-base,
e5-small, gte-small, nomic).
[click] Search knobs (blue): search method 11 (BM25, dense on one of the 5 vector sets, hybrid on one of the 5) ×
reranker off/on (re-read the top 20) × query rewriting off/on (an LLM rewrites the question first) = 44 settings on
each index. No rebuild: every setting runs on every index. The RRF constant stays at 60 (not varied). The 44 dots:
columns = search method, rows = reranker × rewriting; blue = BM25 + reranker, the one we choose.
[click] top-k: k = how many chunks go to the model. It is free: each search returns the top 10 once, and recall@3
and recall@5 are read off the same list.
[click] 48 indexes × 44 search settings = 2,112 rows; each searches all 224 questions = 473,088 searches.
On Modal: one L4 GPU container per index (4 vCPU, 16 GiB), up to 16 at once, 10 to 18 minutes each, 12.0 L4-hours
in all (container wall times from the Volume northbridge-raglab, /vol/grid; 2.69 million vectors embedded).
The commands, for anyone who asks: `modal run experiments/l3_modal.py::grid_build`, then `::collect`
(→ logs/rag_grid.json), then `::answers --configs <ids>`.

## One Knob at a Time
The chosen setting (blue row) and three one-knob changes: size 400 → 0.878, reranker off → 0.771, hybrid → 0.859.
[click] (rows appear)
[click] BM25 alone (no reranker): best at 1,200 tokens (0.805 against 0.771 at 200).
[click] BM25 + reranker: best at 200 tokens (0.893 against 0.756 at 1,200).
[click] Knobs interact. Tuning size with the reranker off would have picked 1,200. That is why we ran the full grid
and then read it one knob at a time from the chosen setting.

## Results: How We Cut
One panel per knob, all else at the chosen setting.
[click] Parser: plain 0.751, structured 0.893.
[click] Chunker: fixed 0.859, recursive 0.863, structure-aware 0.893.
[click] Chunk size: 200 → 0.893 (48 ms), 400 → 0.878 (80 ms), 800 → 0.771, 1,200 → 0.756 (128 ms). The reranker
reads every candidate chunk, so longer chunks are slower.
Overlap: 0% 0.868, 15% 0.893.

## Results: How We Search
Search mode with the reranker: dense (bge-small) 0.663, BM25 0.893, hybrid 0.859. Reranker off 0.771 (0.6 ms),
on 0.893 (48 ms).
[click] Query rewriting: 0.839, and 10.6 s p95 (the recorded LLM call): over budget and worse. Embedding model
(hybrid + reranker, where a model is used): 0.839–0.868, under 3 points apart.
[click] top-k: recall@3 0.795, @5 0.893, @10 0.912. Answers: top 5 → 79.5%, top 10 → 87.1% judge-correct, same search.

## Your Guesses Against the Data
Knob names and empty "your guess" boxes are on screen. For each row, ask a few people for their guess, then click.
The bars are the options, everything else held at the setting we choose; blue = best.
[click] Chunk size (recall@5, BM25 + reranker): 200 → 0.893, 400 → 0.878, 800 → 0.771, 1,200 → 0.756. Why: a small
chunk holds one rule, so the right one can rank first; the reranker reads it faster too (47.6 ms against 127.6 ms
at p95).
[click] Search (recall@5, all with the reranker): dense (bge-small) 0.663, BM25 0.893, hybrid 0.859. Why: with dense
search gold reaches the top 5 for only about two questions in three; fusing its list in costs 3.4 points.
[click] Reranker (recall@5, BM25): no 0.771, yes 0.893. +12.2 points for 47 ms more at p95 (0.6 → 47.6 ms).
[click] top-k (a gold chunk among the k handed over = recall@k): 3 → 0.795, 5 → 0.893, 10 → 0.912. Answers right
(judge, all 224): 79.5% at k = 5, 87.1% at k = 10, for $0.0014 against $0.0023 a question (same search).
[click] Where one document misled us (its own click): on the Purchase Policy alone (v5_dense.json, bge-small,
15% overlap), §6.2 ranked 3rd of 15 chunks at 200 tokens and 1st of 7 at 400. On the whole dump 200 wins: 0.893
against 0.878 with BM25 + reranker, and 0.561 against 0.556 with dense alone (no reranker). With only 7 big chunks
there was little to beat; with thousands, the small chunk that holds just the rule wins.

## The Selection Rule
2,112 configurations measured.
[click] 1,055 with search p95 inside 200 ms (grid timings).
[click] 9 answered on all 224 (the best by recall from the grid, plus contrasts such as dense alone and the naive
first RAG); bars: judge-correct and search p95 from each answer run, in plain words.
[click] 1 chosen: the best judge score among those inside the budget, BM25 + reranker, 200 tokens, top 10: 87.1%.
Rewriting is out (10.6 s).

## The Chosen Configuration, Scored
Structured parser, structure-aware 200-token chunks, 15% overlap, BM25, bge-reranker-base over the top 20, top 10.
Recall@5 0.893 against ≥ 0.90: missed by 0.7 points (recall@10 0.912, one reason for top-k = 10). MRR 0.673. Search 44.5 / 48.5 ms: met.
[click] Answer correct 87.1% (≥ 90%: missed); exact facts 86.2%; citations 92.7% (≥ 95%: missed).
[click] Time to answer 5.8 / 13.2 s (p95 ≤ 4 s: missed: the answer model's own time). Cost $0.0023.
All at the 150-word cap; the race reruns at 250 words.

## Where It Still Fails
One real question per failure type, from the chosen configuration's own records.
Multi-hop (Emma): 2 of 11 gold passages; the change-board (CAB) minutes and patch notes that switch on the
certificate check PUR.CERT_CHK never came back, and the
150-word answer dropped the two prices it had. All gold in the top 10 for 24% of the 21 multi-hop questions.
[click] Tables (Q-401, reorder level of BAT-500): the current item master row never reached the top 10; a superseded
2025 export did (an older copy); the answer said "not in the documents" (it is 3,000). Table lookups: right passage in the top 10
for 71%.
[click] Old versions (Q-602, cycle-count tolerance): MAN-INV-72 v7.2.2 ranked 1st above the current v7.2.3; the
answer still gave 1.5%. A stale copy in the top 5 for 14 of 20 version questions, above the gold for 4.
[click] Procedures (Q-101): the onboarding policy outranked the procedure SOP-PUR-001; NBC-F-112 and NBC-F-113
missing. 13 of 20 procedure answers right.
[click] Permissions (Q-902): the confidential salary file is filtered out, so the answer said "not in the documents"
instead of refusing; 5 of 10 right. The race fixes this by telling the model a file was withheld. What to do next,
per type; metadata filters are taught in the next section (the store).

## (q hero) A new embedding model claims +5 points
Expected answer: add it as one more value of the model knob, run it on our golden set (224 questions) with
everything else at the chosen setting and in the hybrid settings where a model is used; compare recall@5 and search
p95 against the 200 ms budget; if it enters the top candidates, answer and judge all 224 before switching.

## Check · RAG engineering
[click] 1: Recall@5 needs one gold passage in the top 5; the quotation was 1st. Only 2 of 11 were found.
[click] 2: 7 chunks to beat on one document; on all 224, 200 tokens 0.893 vs 0.878, 47.6 vs 80.1 ms p95 in the grid.
[click] 3: 95% of searches take 48.5 ms or less; one in twenty longer (slowest 54.8 ms).

## The Race, Three Measures (proposed replacement for old slides 77–78)
Three plain panels from race.json: answer correct (target ≥ 90%; blue meets it), time to answer p95 (all miss 4 s),
cost per question.
[click] [click] Read it: RAG 89.3%, 11.6 s, $0.0046; wiki hybrid 92.9%, 22.1 s, $0.0242. No method meets 4 s.
Old slide 77's RAG row rendered as a vertical column (its `tr.win` class picks up the legacy-window `.win` style from
plates.css) and its "Paste-all" box covered the table; old slide 78's labels overlapped and bubble size stood for
cost. This slide shows the same numbers without either problem. The cascade (old slide 78, click 2) is left out.
