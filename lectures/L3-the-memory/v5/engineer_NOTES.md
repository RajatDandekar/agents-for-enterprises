# L3 v5 · RAG engineering (section `engineer`) · speaker notes

Every number on these slides is read from `v5/engineer_data.js`, written by `experiments/v5_engineer_slices.py`
(log: `experiments/logs/v5_engineer_slices.json`). Sources underneath: `rag_grid.json` (2,112 retrieval rows),
`rag_best.json`, `rag_answers/*.json` (per-question records of the 9 answered configs), `rag_failures.json`,
`race.json`, `audit.json`, `v5_dense.json` (the one-document playground) and the Volume `northbridge-raglab`
(`/vol/grid/*.json`, container wall times).

## Part slide · "Which settings win on all 224 questions, and how would we know?"
On one document we could see every knob work. Now we have to choose settings for Henrik's whole dump, and the only
honest way is to measure on everything.

## From One Document to the Whole Dump
One policy: 26 units, 15 chunks, one question. We could read every chunk.
[click] The dump: 693 files, 28,953 chunks with the chosen cut, 224 golden questions of ten types.
[click] The grid is 2,112 settings × 224 questions = 473,088 searches. Nobody reads that. We decide with averages,
measured the same way for every setting.

## (q hero) Write your four guesses
Ask them to write down chunk size, search mode, reranker yes/no and k. Keep the chat open: we read the guesses on
"Your Guesses Against the Data".

## Recall@5 and MRR, on Emma's Question
Emma's question searched in the whole dump with the default pipeline (BM25 → bge-reranker-base over the top 20,
structure-aware 200-token chunks). The top 10 as the chosen configuration returned them.
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
[click] 224 questions a day ≈ $0.52. The judge's calls are the cost of testing: $0.92 for 2,016 judgements.
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
Parser 2 × chunker 3 × size 4 × overlap 2 = 48 indexes (each embedded with all 5 models and given a BM25 index).
[click] Search: BM25, dense × 5 models, hybrid × 5 models = 11; × reranker × rewriting = 44 settings per index;
48 × 44 = 2,112 configurations.
[click] k is free: each setting searches once for the top 10, recall@3 and @5 are read off the same list.
2,112 × 224 = 473,088 searches.

## One Knob at a Time
The chosen setting (blue row) and three one-knob changes: size 400 → 0.878, reranker off → 0.771, hybrid → 0.859.
[click] (rows appear)
[click] BM25 alone (no reranker): best at 1,200 tokens (0.805 against 0.771 at 200).
[click] BM25 + reranker: best at 200 tokens (0.893 against 0.756 at 1,200).
[click] Knobs interact. Tuning size with the reranker off would have picked 1,200. That is why we ran the full grid
and then read it one knob at a time from the chosen setting.

## The Code That Runs It
`experiments/l3_modal.py`, `_eval_chunking`, lines 494–512: the list of 11 search modes (line 498).
[click] For every search mode × reranker × rewriting: a Config and a Retriever (lines 499–504).
[click] Every golden question searched once, top 10, scored with `E.gold_hits` (lines 507–511).
[click] The three commands: `grid_build` (48 containers), `collect` (→ rag_grid.json), `answers --configs`.
[click] Machine and time: Modal L4, 4 vCPU, 16 GiB; 48 containers, up to 16 at once, 10 to 18 minutes each;
12.0 L4-hours in all (last full run, from /vol/grid); 2.69 million vectors embedded.
[click] Then 9 settings answered and judged: 2,016 answers, $4.23 for answers + $0.92 for the judge.

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
[click] k: recall@3 0.795, @5 0.893, @10 0.912. Answers: top 5 → 79.5%, top 10 → 87.1% judge-correct, same search.

## Your Guesses Against the Data
Read the class's guesses for each row, then click.
[click] Size: 200. [click] Search: BM25 (with the reranker). [click] Reranker: yes, +12.2 points for 47 ms.
[click] k: 10 for the answer.
[click] Where one document misled: on the Purchase Policy alone (v5_dense.json, bge-small), §6.2 ranked 1st with
400-token chunks (7 chunks to beat) and 3rd with 200. On the whole dump 200 wins, with dense search too
(0.561 against 0.556 without the reranker).

## The Selection Rule
2,112 configurations measured.
[click] 1,055 with search p95 inside 200 ms (grid timings).
[click] 9 answered on all 224 (the best by recall from the grid, plus contrasts such as dense alone and the naive
first RAG); bars: judge-correct and search p95 from each answer run, in plain words.
[click] 1 chosen: the best judge score among those inside the budget, BM25 + reranker, 200 tokens, top 10: 87.1%.
Rewriting is out (10.6 s).

## The Chosen Configuration, Scored
Structured parser, structure-aware 200-token chunks, 15% overlap, BM25, bge-reranker-base over the top 20, top 10.
Recall@5 0.893 against ≥ 0.90: missed by 0.7 points (recall@10 0.912). MRR 0.673. Search 44.5 / 48.5 ms: met.
[click] Answer correct 87.1% (≥ 90%: missed); exact facts 86.2%; citations 92.7% (≥ 95%: missed).
[click] Time to answer 5.8 / 13.2 s (p95 ≤ 4 s: missed: the answer model's own time). Cost $0.0023.
All at the 150-word cap; the race reruns at 250 words.

## Where It Still Fails
One real question per failure type, from the chosen configuration's own records.
Multi-hop (Emma): 2 of 11 gold passages; the CAB minutes and patch notes behind PUR.CERT_CHK never came back, and the
150-word answer dropped the two prices it had. All gold in the top 10 for 24% of the 21 multi-hop questions.
[click] Tables (Q-401, reorder level of BAT-500): the current item master row never reached the top 10; a superseded
2025 export did; the answer said "not in the documents" (it is 3,000). Table lookups: right passage in the top 10
for 71%.
[click] Old versions (Q-602, cycle-count tolerance): MAN-INV-72 v7.2.2 ranked 1st above the current v7.2.3; the
answer still gave 1.5%. A stale copy in the top 5 for 14 of 20 version questions, above the gold for 4.
[click] Procedures (Q-101): the onboarding policy outranked the procedure SOP-PUR-001; NBC-F-112 and NBC-F-113
missing. 13 of 20 procedure answers right.
[click] Permissions (Q-902): the confidential salary file is filtered out, so the answer said "not in the documents"
instead of refusing; 5 of 10 right. The race's withheld notice fixes this. What to do next, per type.

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
