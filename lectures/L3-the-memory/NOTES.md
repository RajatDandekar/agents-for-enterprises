# Lecture 3 · The Memory: Giving It Knowledge — speaker notes

Sat 7 Nov 2026, 7–9 AM IST · 66 slides (56 plates, 8 part heroes, title, next-time) · deck `index.html`
Every number below is in `experiments/logs/` (see the table at the end). Open the live app in a second tab before you start:
`https://rajatworkspace--rasoi-experience.us-east.modal.run/after?stage=knowledge` (and `?stage=brain` for the cold open).

**The one thread:** Kavita asks *"Can I buy the gaskets from Shakti Seals? They quote ₹10.40"*. The answer is no:
gaskets touch food, and POL-PUR-001 §6.2 needs a valid food-grade certificate on file. We follow that one question
from a model that invents rules, to a model that finds §6.2 and cites it.

**The honest twist (say it plainly, it is the best teaching moment):** our retriever is 40/40 on test questions, but
Kavita's own words ("gaskets, Shakti Seals, quote") never say *food* or *certificate*, so plain RAG and our first
Ask Rasoi both missed §6.2. Query rewriting with one line of company context, or the LLM wiki, finds it.

## Timings (120 min)
| Block | Slides | Minutes |
|---|---|---|
| Opening and cold open | 1–6 | 10 |
| Part 1 · Why the model does not know Rasoi | 7–13 | 12 |
| Part 2 · Paste everything | 14–18 | 10 |
| Part 3 · Retrieval | 19–37 | 35 |
| Part 4 · RAG end to end | 38–46 | 20 |
| Part 5 · LLM wiki | 47–51 | 9 |
| Part 6 · Access and freshness | 52–54 | 6 |
| Part 7 · The measurement | 55–58 | 7 |
| Part 8 · Ask Rasoi gains its memory, NB3, A3, map | 59–66 | 11 |

## Plate by plate

**1 · Title.** "Last time Ask Rasoi got a brain. Today it gets a memory."

**2 · Last time, this time.** Recall L2's ending: the bare brain gave a stock number it had never seen. Today: documents.

**3 · Monday morning at Rasoi.** Tell the story: Diwali run, 20,000 gaskets, Deccan's contract ₹11.90, Shakti quotes ₹10.40.
*Demo moment:* type Kavita's question into `/after?stage=brain` live. Then click the three model buttons on the figure:
lite says "Yes, you can proceed", pro says "Yes … if on our approved vendor list", flash invents an "Approved Vendor List"
and "IS 7466". None mentions the certificate.

**4 · What Suresh knows.** Read §6.2 aloud. The ERP does not enforce it (Supplier Policy §4.7). Saving ₹30,000 basic vs
an untested food-contact part. Ask the room: "Who at your company is Suresh?"

**5 · Today's question.** Pause on it. Three conditions: what Rasoi knows, what *this person* may read, *as of today*, with proof.

**6 · Route.** Six parts; one running example; every number measured.

**7–8 · Private and newer.** Define training. The timeline: policies effective 1 Apr 2026, amendment 1 Sep, today 26 Oct,
next amendment 1 Dec. "There is nothing for the model to remember."

**9 · Two places to know from.** PaperBanana figure. Define context window: the only working memory, forgotten after the call.

**10 · Why not fine-tune?** Define fine-tuning. Three reasons: stale, no citation, one model for every reader. We did not
measure a fine-tuning run; say so (the card says it).

**11 · One clause changes the answer.** Click the two buttons. With only §6.2 in the prompt (363 tokens) it cites §6.2.
Point out its opening "NOT IN DOCUMENTS": whether Shakti holds a certificate is a *fact* in Bahi, not a rule. That
distinction comes back on plate 45.

**12 · Three ways in.** Fine-tune vs paste vs retrieve.

**13 · Check yourself.** Three questions; reveal answers one by one. Take one answer from the chat before revealing.

**14–15 · Rasoi's documents.** 8 files, front-matter, tokens per document (Gemini's counter). Kavita may read 7:
8,465 words, 13,352 tokens pasted with headers. The HR page is ember: not hers.

**16 · Paste it all.** The real reply: cites §6.2, §6.1, §6.4, AMD-SUP-2026-02 §1.1. 13,596 tokens, 19.1 s, ₹0.645. "It works."

**17 · What pasting costs.** Slide the questions-a-day control. Per-question ₹ is measured over 40 questions
(₹25.11 vs ₹1.92 for 40); questions a day is the audience's guess — say so.

**18 · Why it breaks at scale.** Whole company (49 docs, 28,173 tokens): still 40/40, twice the tokens and rupees,
and 2 answers cited a finance-kit clause (POL-FIN-024 §1) on a purchasing question. Plus: no per-reader hiding.
Not measured: a real 400-page manual or the window's limit.

**19–20 · Retrieval in one picture.** Walk the pipeline once; "we now build each box".

**21 · Chunking.** Define chunk. Drag the window slider: §6.2 lands mid-window with §6.1 and §5. Switch to "By clause".

**22 · One chunk zoomed.** id = citation, heading path, version/date, audience, status. 251 chunks, Kavita's index 247.

**23 · Clauses or windows, measured.** Top-5, whole clause found: by clause BM25 31, embeddings 32, hybrid 32 of 33;
120-word windows 30, 26, 29. And no citation from a window.

**24 · Keyword search.** We teach on scenario 1's phrasing (Suresh's words). Show the terms: small words dropped,
plurals cut, food-grade kept whole and split. "We come back to Kavita's own words in Part four." (Small honest aside:
"they" is not in our stop list, it shows up on plate 39.)

**25 · BM25 step 1.** Saturation: slide k₁; slide the length ratio (§6.2: 47 terms vs average 33.9).

**26 · Step 2, idf.** Real counts: supplier in 103 of 247 chunks (idf 0.87), litre in 1 (5.11).

**27 · Step 3, the sum.** Six terms, 17.216 for §6.2. Define BM25.

**28 · BM25 ranks every chunk.** §6.2 is 4th; §4.2 wins with "better" (grade 304 or better).

**29 · Embeddings again.** Recall L2. 384 numbers per passage. Click the four question buttons on the map.

**30 · Cosine in 2-D.** Define. Turn the angle; length does not matter.

**31 · Cosine for real.** Scrub the dimensions: the running sum reaches 0.7595, the top cosine of all 247.

**32 · Where each goes blind.** P01: BM25 rank 4, embeddings rank 1. M01 (ERR-PO-0412): BM25 rank 2, embeddings not in top 10.

**33 · RRF.** Define. §6.2: 1/64 + 1/61 = 0.03202, 2nd behind §4.1. Move k.

**34 · Reranking.** Bi-encoder vs cross-encoder figure. Reranker on the fused top 20 only.

**35 · Four rankings.** Click through: §6.2 4th → 1st → 2nd → 1st (1.61, the only clause above 0).

**36 · Ranking measured.** Define recall@k. Hybrid + rerank: first 28/33, top-5 33/33. No model calls: measure on every change.

**37 · Check yourself.** Four questions.

**38–39 · Kavita's words, not the rule's.** The key moment. Her terms: buy, gasket, shakti, seal, they, quote, ₹10.40.
Reranker: §5.1 −0.38, §6.2 −5.87, everything below 0 → search_policy says "not in the documents".
"40 out of 40 on the test set, and it misses the one question that matters."

**40 · Our first try missed it too.** Scrub the real trace: 4 searches, none says "food"; reply cites §6.1, §6.3, §5.2 —
all real, all grounded, and the deciding rule is missing. "Correct citations are not the same as the right answer."

**41 · Writing the search.** One line of context: "Rasoi makes pressure cookers, so many of the parts it buys touch food."
One long query: §6.2 first but −1.25, under the cut. One short query per rule: §6.2 at 3.94. Define query rewriting.

**42 · RAG step by step.** Click the six tabs: question → queries → clauses → the exact prompt (559 tokens, 777 with
instructions) → answer → citation check (0 invented, 0 ungrounded). Note the OpenRouter line in the caption: the Gemini
prepay ran out on 28 Oct, so these calls went to the same model through OpenRouter.

**43 · Citations.** Define. A citation is a key Kavita, Rohit and audit can look up.

**44 · Checking citations.** The code. Real answer clean; the hand-edited §6.9 copy is flagged "invented" (say we edited it).

**45 · Rules in documents, facts in Bahi.** Stock 54,000 lives in Bahi. Score dots: the lowest answerable (1.61) is
scenario 1 itself; 5 of 7 unanswerable above 0. The cut trims junk; "not in the documents" is the model's job.

**46 · Check yourself.** Three questions.

**47–48 · The LLM wiki.** Karpathy's idea; compile once, lint by code, read the index at question time.

**49 · Eighteen pages.** Click a page; the HR page has no links. Compile cost: 21 calls, ₹8.17, once (v2 run, copied).

**50 · The wiki on Kavita's question.** No rewriting: the model reads the index, picks food-grade-compliance, cites §6.2.
"A search engine cannot make the jump from gasket to food; a model reading a table of contents can."

**51 · Wiki or RAG?** Walk the table row by row. Ask Rasoi uses RAG; the wiki is a good second opinion.

**52–53 · Access control.** Define clearance. Filter first. Without the filter, HR chunks reached the top 5 for 2/2 salary
questions and 1 answer gave Kavita a salary figure; with it, 0.

**54 · Freshness.** Drag the date across 1 Sep and 1 Dec. RAG 5/5 with dates (and 5/5 without the filter, the amendments
say what they replace); the wiki compiled before the amendments 1/5.

**55–56 · The experiment.** 40 questions, five systems, code grading, no LLM judge; re-run on 28 Oct with today's code.

**57 · What we measured.** Step through rows. RAG 40/40 at 579 tokens and ₹1.92 for 40; full 40/40 at 13,597 and ₹25.11;
company 40/40 at 28,418 and ₹51.21; wiki 39/40; model alone 7/40 (all refusals).

**58 · Reading the results.** Cards. The caveat card: these questions use the rules' words; real users' questions are harder.

**59–60 · search_policy in the toolbox.** tool.json and tool.py, real files. "How the model decides to call it: next lecture."

**61 · Kavita asks again.** *Demo moment:* `/after?stage=knowledge`, ask the Shakti question live. Then scrub the recorded
run on the plate: 8 searches, §6.2 found on the third, reply cites §6.2 first, 0 invented, 9 calls, 15,117 tokens, ₹0.79.
If the live app misses §6.2, that is plate 40 happening live: use it, and show the context line it needs.

**62 · Did the line hurt anything?** Six of the 40, before and after: all right both ways; food-grade questions cost a bit
more (more searches). A spot check, not a suite (Lecture 7).

**63 · NB3.** Six exercises: chunker, BM25, cosine, RRF, the RAG prompt, the citation checker. Replays with no key.

**64 · A3.** The memory for your module kit; 12 questions graded by code; due Sun 8 Nov.

**65 · Where we are.** The architecture with Knowledge and search_policy lit. It still cannot see Bahi: Shakti is not in
the supplier master; stock is 54,000.

**66 · Next time: The Hands.** Tools and MCP; Ask Rasoi checks the supplier master and raises the PR.

## Where the numbers come from
| Plates | Log | Script |
|---|---|---|
| 3, 11 | `logs/story.json → brain, with62` | `experiments/story.py` (cassette L3v3_coldopen, L3v3_story) |
| 15–16 | `logs/retrieval_eval.json → corpus, full_ctx`; `logs/story.json → full` | `retrieval_eval.py`, `story.py` |
| 17–18, 56–58 | `logs/answers_eval.json → summary` | `answers_eval.py` (cassette L3v3_eval) |
| 21–36, 39, 45 | `logs/retrieval_eval.json` | `retrieval_eval.py` (no chat model) |
| 40 | `logs/story.json → knowledge` | `story.py` (cassette L3v3_knowledge) |
| 41–42, 50, 61–62 | `logs/finding62.json` (first run: `logs/finding62_run1.json`) | `finding62.py` (L3v3_story, L3v3_knowledge) |
| 49, 51 | `logs/v2_wiki_compile.json` (copied from v2; produced `bahi/wiki`, unchanged since) | v2 `build_wiki.py` |
| 53–54 | `logs/answers_eval.json → summary.rag_noperm, rag_nofresh, wiki_stale`; `logs/retrieval_eval.json → leak` | `answers_eval.py` |
