# Section 7 · The LLM Wiki (v5) · speaker notes

One document (D = `POL-PUR-001_Purchase_Policy_v4.1.pdf`) and one question (Emma's, `Q-EMMA`) all the way through, as in
RAG. Every intermediate on the slides is real: `experiments/v5_wiki_modal.py` ran the course's own builder
(`wiki_build.build(files=[D])`, then `wiki_build.update([AMD-SUP-2026-02])`) on Modal with gemini-3.8-flash and logged every
prompt and reply (`experiments/logs/v5_wiki_ingest.json`, `v5_wiki_update.json`); the query replays the race's recorded calls
on the full wiki (`v5_wiki_query.json`); tokens per part are Gemini's own count (`v5_wiki_counts.json`). The slides read
`v5/wiki_data.js`, written by `experiments/v5_wiki_data.py` (failure evidence in `logs/v5_wiki_failures.json`).
Film 2 is placed by the lead.

## Section 7 (part slide) · What if the model wrote Northbridge's wiki first?
RAG searches the raw text every time a question arrives. Turn it around: let the model read each document once, now, and write
down what it learned as pages. Then questions read the pages.

## The Idea in One Picture
Karpathy's gist, April 2026. Read it after class.
[click] Ingest: the model reads each source once and writes pages. 693 files became 683 pages.
[click] People write one file, AGENTS.md: the rules every ingest follows.
[click] Query: read index.md, open pages, answer; each sentence cites a raw source.
[click] RAG, for contrast: nothing is written in advance; it searches the chunks on every question.
The difference to keep: the wiki spends its model calls before the question, RAG at the question.

## A Wikipedia Page, Read as a Design
Kept from v4. Nine clicks, one part each: title, lead, infobox, contents, blue links, references, "needs citations", view
history, search. Each one has a counterpart in our wiki.

## One Document, Read by Hand
Before any model: what would a careful person write from D?
[click] The policy itself: code, version 4.1, in force since 1 April 2026, its history. That is a page.
[click] A rule with a number: §3.3, direct orders up to £50,000 gross. A fact on that page, with its clause.
[click] §5 names another document, POL-APR-002. D only says what it is for.
[click] Emma's two clauses: §6.2 (UN 38.3) and §6.4 (a cheaper quote is no reason). UN 38.3 is a topic many documents share.
[click] Things it mentions: screen FIN-CC-01, tax codes, Henrik Weber. Each could be a page that links back.
[click] What the model wrote: 6 pages, 29 facts (22 on pol-pur-001). Its proposed `topic-tax-codes` was mapped to
`data-tax-codes` by the build's MERGE call. Ask: did it miss anything we found? D names POL-SUP-003 but says nothing about it.

## Ingest, Step 1: The Prompt
One call reads all of D: 8,460 tokens in, 3,687 out, 20.7 s (this READ call is the very one from the full build, replayed
from its recording; the request was byte-identical).
[click] Part 1, about 2,900 tokens: the instructions and the whole of AGENTS.md.
[click] Part 2, about 2,100 tokens: the registry, the 100 slugs that exist, so every source names things the same way.
[click] Part 3: the source header (file, version, effective date, status today, audience).
[click] Part 4: D itself, pages 1 to 4, 2,211 tokens. Note §6.2.
[click] Part 5: the rules and the JSON reply format. "quote is 5 to 25 words copied exactly … it is checked by code".
Point: more than half of the prompt is the same for every source.

## Ingest, Step 2: The Reply
[click] The source note: what D is, its date and status.
[click] The pages D touches, with how many facts each.
[click] One fact, for §6.2: the fact in the model's words, the quote in D's words, page 2, section 6.
[click] Conflicts it noticed: v4.0 superseded; AMD-PUR-2026-03 future-dated (1 December).

## Ingest, Step 3: The Quote Check
No model: a string search in code.
[click] Both sides normalised: lower case, no spaces, plain quotes.
[click] Found on page 2. Verified.
[click] A real miss on D: the quote for pol-apr-002 joins §5.1 and §5.2, but D prints "5.2" between them. Not found.
[click] 27 of 29 verified on D; 12,018 of 12,095 in the full build. The check marks a fact; it does not delete it.
pol-apr-002 was still written from its two unverified facts; lint lists such references later.

## Ingest, Step 4: The Written Page
One more call per page (6 here). The writer sees the numbered facts, never D.
[click] The lead's last sentence: keys r2, r16, r20 lead to the version history, §6.2 and §7.2.
[click] §3.3 sentence → r6 → "£50,000 or less".
[click] §6.2 sentence → r16 → the quote we just checked.
[click] §6.4 sentence → r18 → "does not by itself justify a change of supplier". Emma's rule, traced by eye.
Students may click any sentence.

## Links, index.md and log.md
[click] index.md: one line per page, rebuilt after every ingest, read first by every query. Screens and people appear as one
slug-rule line each.
[click] log.md: one line per ingest, created and updated counts, and the slugs.

## A Second Source Arrives
AMD-SUP-2026-02: from 1 September 2026 a UN 38.3 certificate must be under 12 months old and valid 60 days past the order.
[click] The update reads it (1 call) and touches 4 pages: 1 updated, 3 created.
[click] The diff, infobox and lead: the new rule enters the lead (12 months, 60 days).
[click] New paragraphs and "Versions and conflicts": the 24-month rule is now the older rule.
[click] Links and references to the amendment.
[click] The log line. Note "Today's rule (superseded)" in the page: a label slip by the model, visible in the diff.

## The Same Change in RAG
[click] RAG: parse 51 ms, 3 chunks (142, 247, 165 tokens), no model call; BM25 over all 28,953 chunks rebuilds in 4.86 s.
[click] But RAG reconciles nothing: the POL-SUP-003 chunk with "24 months" stays next to the new one. The answer step must work
out which rule wins, on every question. The wiki did that work once.

## The Rules It Followed: AGENTS.md
Five lines of the schema, each next to what it produced. [click] per rule: slugs from codes (both sources landed on one page);
page layout (lead, infobox, one `###` per clause); citations on every sentence; newer replaces older, recorded under
Versions and conflicts; the log line format. [click] All together.

## Query, Call by Call
The full wiki, the race's recorded run (replayed). Click any bar segment to see the text.
Call 1: system 449, index.md 7,987, question 16 tokens (9,716 billed). Reply: open three pages.
[click] Call 2: the short index, its own reply, three whole pages (13,720). Reply: done.
[click] The answer call: the three pages as sources [1] to [3] (5,002).
[click] Missing from the answer: six must-contain facts. Keep this for two slides.

## Chunks or Pages
[click] RAG: 10 chunks, 2,368 tokens, one call. Six chunks come from the four files behind the Brightcell page.
[click] The wiki: 28,438 tokens in three calls, drawn to the same scale.
The multi-hop advantage: one page already joins a meeting and three e-mails (the coloured squares). The join was done once.

## Where It Fails: Never Compiled
Q-104, "the screen hangs after Save". The manual's §19.4 on page 13 has the answer.
[click] The ingest took 89 facts from that manual, none from page 13. No page says "do not press Save again"; the wiki answered
NOT IN THE DOCUMENTS. [click] RAG found the paragraph in the raw manual.

## Where It Fails: Wrong at Compile Time
Left, our one-source wiki: the UN 38.3 page says "System enforcement: Ledgerline order blocking". Ledgerline does not block
(PUR.CERT_CHK default N; the change board kept it N). The quotes behind the lead passed the check; the infobox has no key.
The full build, which read RN-7.2.3-P4 and the CAB minutes, wrote it correctly.
[click] Right, the full wiki: the IT Security Policy page was filed HR-only because the HR folder's README also names
POL-ITS-008 and the registry met it there first. A build-code error, not the model's. Staff never see "12 characters,
60 days"; Q-609 failed; lint reported nothing on that page.

## Where It Fails: Stale Until Re-ingested
Before the update, the page had no 12-month window. [click] After, only touched pages changed: pol-pur-001 was not touched
and still has no link to the amendment. [click] Staleness is a schedule: RAG re-chunks for free, the wiki pays per update.

## Where It Fails: Cost and Time of Ingest
D alone: 8 calls, 32,052 tokens in, 32.7 s, $0.055. The amendment: 5 calls, 25.0 s, $0.038. The full build: 1,752 calls,
12.7 million tokens in, about 11 minutes on 40 workers, $22.61. [click] RAG: no model, 14.63 s chunking + 4.86 s BM25 for
everything. [click] Cost grows with the documents, not with the questions.

## Where It Fails: Stopped Early, Dropped Facts
Index, three pages, done after 2 calls; its reason names AMD-SUP-2026-02, which it never opened.
[click] The six missing facts, one by one: NBC-F-112, £119.00 and PUR.CERT_CHK were only on pages never opened.
12 months, 60 days and £104.00 were in the answer call's context (pol-sup-003, sup-brightcell-energy) and the answer left
them out. Two failures in one run.
[click] Multi-hop, answer correct: RAG 71%, wiki navigation 67%, hybrid 71%, sections only 33%.

## Where It Fails: Exact Codes
Q-726, ERR-CRD-0207. The source says "CREDIT LIMIT EXCEEDED (<cust_cd>)"; the page rewrote it as "Customer Credit Limit
Exceeded" and "credit ceiling". The answer missed the exact message. Also index.md lists the 98 error pages as one line.
[click] Exact-code questions: recall@5 RAG 1.00, wiki 0.52; answer correct 93% vs 85%.

## Lint: The Wiki Checks Itself
1,073 findings in 59 s; 31 of the 40 planted problems found. On Emma's pages: the citation_not_found on the UN 38.3 page
(r35 is a 62-word quote), the orphan Brightcell page, the superseded rule recorded.
[click] Lint can fix citations, orphans, stale and contradictory claims. [click] It cannot see a fact that never reached a page,
a page filed under the wrong audience, or a reader that stops early. For those we need the golden set.

## The Wiki, Measured
Per question on the race's 224: 2.54 navigation calls before the answer, retrieval 6.4 s p50 / 23.4 s p95, $0.0322 a question
(RAG: 44 ms, $0.0046). [click] Quality on the same metrics: recall@5 0.86 vs 0.89, answer correct 89.3% for both, citation
correct 85.9% vs 92.2%. [click] The same test as RAG, step by step; Emma's question through it is what we watched.

## Where the Wiki Lives
[click per card] Files: a git repository of markdown; for production, every ingest is a commit someone reviews. Search: 2,520
sections with the same BM25 and bge-small, 1.2 ms p50, so "hybrid" can start from a search. Permissions: one audience per
page; the page is the unit of permission, so one wrongly filed page hides all of it.

## Ask the class · An amendment lands at 9:00; Emma asks at 9:05
Expected answer: 4, it depends on when each memory was refreshed. RAG knows if the file was re-chunked (free, seconds); the
wiki knows if the update ran (model calls, a review). Neither knows by itself.

## Check · Section 7
[click] 1: Yes. The check tests quotes, not sentences; infobox lines have no key. "Ledgerline order blocking".
[click] 2: Yes, the model saw them (pol-sup-003, source [2]) and the answer left them out; three other facts were never opened.
[click] 3: The wiki rewrites pages (5 calls, 25 s, $0.038); RAG re-cuts the file (3 chunks, about 50 ms) and reconciles at
question time.
