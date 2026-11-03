# Lecture 3 v4: The Memory. The art of retrieving from Northbridge's documents

Rajat's brief (3 Nov 2026), summarised:
- The lecture is mostly about retrieving information from documents.
- It runs on a realistic, massive documentation dump of a legacy-ERP company: PDFs, Excel, service definitions and more.
- Think like an engineer: decide the metrics first (accuracy and latency, with latency weighing heavily), then compare RAG against the LLM Wiki.
- Put the winner into the chatbot, live.
- Tell it as a story.
- Explain both techniques from scratch, with mini-prototypes and hyperparameter labs.
- Use a real vector database (Chroma).
- Give guidelines for any domain (pharma, healthcare and others).
- Show where the LLM Wiki came from (Karpathy) with a real Wikipedia page as the analogy.
- Write an assignment that replicates the class.
- Questions follow the L1/L2 pattern.

**Class:** Sat 7 Nov 2026, 7–9 AM IST. **World:** Northbridge Cycles on Ledgerline ERP 7.2 (`WORLD_V4.md`). **Never:** the real client's or product's names, Indian names, rupees or real client data.

## The story
1. **Henrik's letter (Lecture 1).** "Change our system." We reply: *gladly, but first we need Northbridge's documentation.* You cannot turn a 1998 system AI-native without the knowledge of how it works.
2. **Henrik shares a GitHub repository**, `northbridge-docs`, as real clients do.
   - It holds 28 years of policies, procedures, manuals, screen references, service definitions, Excel masters, release notes, e-mails and scans.
   - We clone it live in class.
3. **We audit it.** What is in it? Structured, semi-structured or unstructured? How big is it, in tokens? What is duplicated, superseded, contradictory or scanned?
4. **What will people ask?** We sorted a real sample of staff questions into three kinds:
   - **genesis:** create something, such as a new PR, a supplier or a document;
   - **analytical:** reports and history, such as spend for the last 5 months;
   - **documentation:** how, what and which rule.

   Genesis and analytical questions need services fired, which means tools (Lecture 4 onward). **Today: documentation questions.**
5. **Metrics first.** Before building anything, we decide what "good" means and how to measure it:
   - **accuracy:** retrieval recall@k, answer correct, citation correct;
   - **latency:** retrieval ms and time to answer, at p50 and p95;
   - **cost** per question;
   - **update cost** when a document changes.

   We build a golden set of real questions with known sources.
6. **RAG from scratch,** then the RAG Lab: students vary the parsing, chunking, embedding model, top-k, hybrid search and reranker, and watch the metrics move.
7. **The LLM Wiki from scratch:**
   - Karpathy's gist ("LLM Wiki", 4 Apr 2026);
   - a real Wikipedia page as the analogy;
   - the three layers (raw sources, the wiki, the schema) and the three operations (ingest, query, lint);
   - building Northbridge's wiki and following the chain of one query.
8. **The race** on the agreed metrics: RAG (best setting), LLM Wiki, hybrid (retrieval over wiki pages) and paste-everything.
9. **Ask Northbridge gets its memory:** the winning method goes behind `?stage=knowledge`, live. Emma's question is answered with citations.
10. **Guidelines** for any domain (pharma, healthcare, banking, legal), then NB3, A3 and Lecture 4.

**The running example:** Emma: *"Can I buy the battery packs from Brightcell Energy? They quote £104."* The answer needs several documents:
- Purchase Policy §6.2 (UN 38.3 for lithium-cell parts);
- the supplier master (Brightcell is not in it);
- the onboarding SOP (how to add a supplier, and the certificate upload);
- possibly a release note that changed the certificate check.

**The second example (latency and lookups):** *"What does ERR-PO-0412 mean, and how do I fix it?"* Exact codes are where embeddings alone fail, and BM25 or hybrid search wins.

## The documentation dump (`northbridge-docs`, its own git repo)
**Generator:** `tools/northbridge_docs/` in this repo. It is deterministic and seeded, and its output goes to `/Users/raj/Claude_Brain/northbridge-docs/`. Rajat creates `github.com/RajatDandekar/northbridge-docs` and pushes.

**Targets:** about 500–700 files, about 1,200+ PDF pages, about 600k–900k words, more than 25k spreadsheet rows. The repo stays under 150 MB, with no file over 50 MB.

**Layout:**
```
README.md                       Henrik's hand-over note + what each folder is
01_policies/                    PDF (+ old DOCX versions): purchase, supplier, approval matrix, battery safety (UN 38.3), quality,
                                returns, travel & expenses, IT security, data retention, HR (confidential: salary bands)
02_procedures/                  SOPs (PDF/DOCX): supplier onboarding, PR→PO, PO amendment, goods receipt, returns to vendor,
                                stock count, period close, invoice matching, certificate renewal …
03_ledgerline_manuals/          user manual per module (Purchase, Inventory, Accounts Payable, Sales, Production), admin guide,
                                screen reference (one section per screen: fields, codes, keys), error-code reference, batch jobs
04_service_definitions/         one file per service (YAML; some old XML/WSDL-style), ~400 across modules. The 38 purchasing
                                services MUST match ledgerline/erp/services.py exactly (Lecture 4 builds tools from these)
05_master_data/                 XLSX/CSV: item master, supplier master (with certificates), rate contracts/price lists, cost
                                centres & budgets, approval matrix, warehouses, tax codes, payment terms, units
06_transactions/                XLSX/CSV extracts: POs, PRs, GRNs, invoices for Jan–Oct 2026 (for "analytical" questions; out of
                                scope today, but real)
07_data_dictionary/             tables, fields, codes (XLSX + PDF)
08_release_notes/               Ledgerline 7.0 … 7.2.3 (some change behaviour the manual still describes the old way)
09_email_archive/               .eml: decisions and clarifications that never reached a policy
10_meeting_notes/               DOCX/MD
11_training/                    quick-reference cards (PDF), onboarding deck exports
12_integrations/                EDI order spec, bank payment file format, carrier API notes
99_scans/                       a few image-only PDFs (old signed approvals, a 2004 manual page): need OCR
eval/                           facts.jsonl (planted facts with exact source locations), questions.jsonl (golden set)
```
**Realism (each one on purpose, and logged in `eval/messiness.json`):**
- duplicates and near-duplicates (v4.0 and v4.1);
- superseded documents still present;
- contradictions (a manual against a later release note; an e-mail that overrides a SOP);
- tables inside PDFs;
- inconsistent naming;
- legacy abbreviations;
- broken intranet links;
- scans;
- a confidential folder (permissions);
- documents in force from a future date.

**Consistency:** every number and rule already used in L1/L2 holds (`WORLD_V4.md`, `ledgerline/erp/seed.py`, `ledgerline/docs/*.md`). `python3 tools/world_v4.py --check` stays clean.

**Golden set (`eval/questions.jsonl`):**
- about 200 documentation questions. Each has a reference answer, its source(s) (file, page or section, sheet or cell), a type and a difficulty. The types:
  - single lookup;
  - procedure;
  - rule;
  - service/field reference;
  - table lookup (Excel);
  - multi-hop (2+ docs);
  - version/conflict;
  - exact code;
  - not in the docs;
  - permission (confidential).
- 40 genesis and 40 analytical questions, labelled for the taxonomy slide.
- Every documentation answer is checked against the facts registry by script.

## Metrics (decided in class, measured on the golden set)
| Metric | How | Target (we set it, then test it) |
|---|---|---|
| Retrieval recall@k | Is a gold source in the top k? | ≥ 90% @5 |
| MRR | Rank of the first gold source | report |
| Answer correct | LLM judge + exact-fact check against facts.jsonl (judge agreement reported) | ≥ 90% |
| Citation correct | Cited source contains the fact | ≥ 95% |
| Retrieval latency | ms, p50/p95, on the same machine | p95 ≤ 200 ms |
| Time to answer | s, p50/p95, end to end | p95 ≤ 4 s |
| Cost per question | input + output tokens × price (USD) | report |
| Update cost | time + $ to absorb one changed document | report |

## Experiments (all run on Modal; logs in `lectures/L3-the-memory/experiments/logs/`)
1. **Audit:** counts, sizes and tokens (Qwen + o200k) by folder and type; the structured/semi/unstructured split; the messiness found.
2. **Paste everything:** total tokens against context windows; the cost per question if pasted.
3. **The RAG grid** (Chroma, persistent, HNSW cosine):
   - parsers: plain text vs layout-aware for PDFs; row-group vs sheet-dump for Excel; one service per chunk;
   - chunkers: fixed vs recursive vs structure-aware;
   - chunk size {200, 400, 800, 1,200 tokens} × overlap {0, 15%};
   - embedding models: bge-small-en-v1.5 (384), bge-base (768), e5-small-v2, gte-small, nomic-embed-text-v1.5;
   - retrieval: dense vs BM25 vs hybrid (RRF), ± a cross-encoder reranker (bge-reranker-base), ± query rewriting;
   - top-k {3, 5, 10};
   - metrics per question type, retrieval latency, index size and build time.
4. **The LLM Wiki:**
   - ingest the dump into a wiki: pages per entity (supplier, item family, process, policy, screen, service group, error code), `index.md`, `log.md` and a schema file (`AGENTS.md`);
   - query by navigation: read the index, open pages, follow links, cite the raw sources;
   - lint: contradictions found;
   - build cost and time, and the update cost for one changed document.
5. **The race:** best RAG vs LLM Wiki vs hybrid (wiki pages as the retrieval unit) vs paste-all, with the same answer model (gemini-3.8-flash via OpenRouter, recorded to cassettes). Every metric, by question type.
6. **Live stage:** the winner goes behind Ask Northbridge `?stage=knowledge` (a `search_docs` tool), deployed before class.

## Interactive pieces
- **Dump Explorer:** a treemap by folder and type; click into a file to see it as the parser sees it.
- **RAG Lab** (Modal app `northbridge-raglab`):
  - choose the parser, chunker, chunk size, overlap, embedding model, top-k, hybrid, reranker and rewriting;
  - see the chunks of a document, the vector-space neighbours, the retrieved chunks for any question (live Chroma query with measured latency) and the golden-set metrics for that setting (from the precomputed grid);
  - a class leaderboard: the best accuracy under the latency budget.
- **Wiki Explorer:** browse Northbridge's wiki like Wikipedia; replay the navigation chain of a query step by step (index → page → link → source).
- **Wikipedia analogy:** a real page (Electric bicycle), captured with attribution (CC BY-SA). Its lead, infobox, contents, sections, internal links, references, categories and history are highlighted, and each maps to a wiki concept.

## Films (about 3, L2 quality bar, `FILM_STYLE.md`)
1. **`rag`** "How RAG works": Emma's question → embedding → nearest chunks in the vector space → top-k → prompt → cited answer.
2. **`wiki`** "How the LLM Wiki works": raw sources → ingest → pages, links, index, log → the query chain → cited answer.
3. **`race`** "The race": the same questions, both methods, the clock running; where each wins.

## Section rhythm (as L2)
Part slide → teach → the section's own question to the class → film (where there is one) → 1–3 technical check questions with answers on click. About 85–100 slides.

## Industry practice to cover
- **Parsing:** docling, Unstructured, OCR.
- **Frameworks:** LangChain and LlamaIndex.
- **Vector databases:** Chroma, pgvector, Pinecone, Qdrant, Weaviate, OpenSearch; when to pick each.
- **Search pieces:** hybrid search, rerankers, query rewriting, metadata filters and permissions.
- **Evaluation:** RAG evals (Ragas-style) and a golden set in CI.
- **Wiki-style compiled knowledge:** Karpathy's LLM Wiki; GraphRAG as a cousin.

## Guidelines for any domain (a slide and a page in A3)
1. Audit the corpus.
2. Collect real questions and sort them (genesis, analytical, documentation).
3. Set metrics and targets with the users.
4. Build a golden set from real questions.
5. Parse by document type.
6. Chunk by structure.
7. Pick an embedding model by measurement (domain models for pharma and medicine).
8. Use hybrid search whenever codes matter.
9. Filter by permissions before ranking.
10. Handle versions and effective dates.
11. Choose a wiki when synthesis across documents matters and the corpus changes slowly.
12. Measure again after every change.

## Deliverables
- `index.html`, `NOTES.md`, `figs*.js`;
- `NB3_the_memory.ipynb` (Colab, replay, no key; it clones `northbridge-docs`);
- `A3.md`: replicate the class (RAG with Chroma, tune it with the metrics, a mini LLM Wiki, a comparison on a golden set, then the same for your own domain);
- the RAG Lab app;
- the live `?stage=knowledge`;
- 3 films.

## The race: result (3 Nov 2026, `experiments/logs/race.json`)
Built by `race_modal.py` and `race_report.py`. The setup is the same for every method:
- 224 documentation questions;
- the same answer prompt, with the cap raised from 150 to 250 words;
- gemini-3.8-flash as the answer and judge model, through Google's endpoint;
- the same withheld notice;
- one Modal L4 container per method.

| | Judge | Fact | Citation | R@5 | Retrieval p95 | Answer p50 / p95 | $/q |
|---|---|---|---|---|---|---|---|
| **RAG** (BM25 + reranker) | 89.3% | 85.7% | 92.2% | 0.89 | **48 ms** | **6.2 / 11.6 s** | **$0.0046** |
| Wiki navigation | 89.3% | 83.5% | 85.9% | 0.86 | 23.4 s | 12.5 / 30.6 s | $0.032 |
| Wiki hybrid | **92.9%** | 86.6% | 91.7% | 0.81 | 11.2 s | 12.6 / 22.1 s | $0.024 |
| Wiki sections only | 79.5% | 76.3% | 79.5% | 0.78 | 1 ms | 6.5 / 15.3 s | $0.0054 |
| Paste-all (12-question sample) | 12/12 | 12/12 | 12/12 | — | — | 44 / 80 s | $0.61 |

**Winner: RAG,** which now sits behind `?stage=knowledge` as the tool `search_docs`.
- **Latency weighs most.** RAG is the only method that finds sources inside the 200 ms budget, and it answers in about half the hybrid's time.
- **Accuracy is close.** The hybrid gets 8 more questions right out of 224, at twice the wait and 5× the cost.
- **Where the wiki wins:** procedures (95% vs 75%), table lookups (97% vs 88%) and version conflicts.
- **Where RAG wins:** permissions (90% vs 70%).
- **No method meets every target.** The 4 s p95 time to answer is missed by all; the model's own time dominates. Citations stay under 95% for all.

**Measured cascade (not shipped).** Answer with RAG; ask the wiki hybrid only when RAG finds nothing (21 questions).
- Results: 92.0% judge, 94.6% citation, p50 6.6 s, p95 21.8 s.
- This is the "next step" slide. It costs p95 latency.

**The word cap was not the bottleneck.**
- Moving from 150 to 250 words changed the judge score by +0.4, −0.4, +1.3 and +0.9 points.
- Q-EMMA is still wrong for every method at 250 words. RAG's answer uses 186 words and has §6.2, NBC-F-112, 12 months and 60 days. It misses £104 vs £119 and PUR.CERT_CHK, because retrieval never brought back the rate-contract row or the setting.

**The withheld notice made the biggest fix.** Permission questions went 50% → 90% for RAG and 10% → 70% for every wiki method.
- The detector is one BM25 check: is a confidential chunk in the unfiltered top 10? It is the same for every method.
- It fires on 7 of the 8 refusal questions, plus 3 false alarms that did not change any answer.
- It misses Q-906, the bonus question.

**Spend:** $6.53 of LLM spend at the harness price. Navigation replayed from its cassettes.
