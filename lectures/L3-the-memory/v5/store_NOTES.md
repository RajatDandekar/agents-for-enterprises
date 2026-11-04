# L3 v5 · section `store` · speaker notes

Where the vectors live: Chroma for real (document D, then the whole dump), HNSW, the production choice, and a walkthrough
on our real Qdrant Cloud cluster. Every number on the slides comes from `window.L3V5.store` (`v5/store_data.js`, written by
`experiments/v5_store_data.py`) and the logs named below. Dates: all runs and the survey on 4 Nov 2026.

## Part · Where do 28,953 vectors actually live?
Bridge from the dense section: every chunk is 384 numbers; the question too. Now: where are they kept, and what do teams
run in production? “Whatever we do here, you will do in your project.”

## What a Vector Store Keeps
The real record for §6 of D (id "5" in D’s Chroma collection), read back with `col.get(include=[documents, metadatas, embeddings])`.
- Read the id and the document: the context header, then 6.1 to 6.4. The highlighted clauses are §6.2 and §6.4, the ideal answer.
- [click] Metadata: what `rag.add_vectors` stores (file, folder, fmt, doc_id, i, confidential, superseded, future). Point at the two flags.
- [click] The embedding: first 8 of 384 numbers (−0.0353, 0.0477, …), length 1.00 (normalised, so cosine = dot product).
- [click] A hit brings back id, text and metadata together: this is how the answer cites “POL-PUR-001 v4.1, p.2, § 6”.
Source: `logs/v5_store_local.json → D.record` (`experiments/v5_store_local.py`).

## Document D in Chroma
The course code on Modal: `rag.Index.build(d, ["bge-small"], "store_D", vectors=…)` with the grid’s bge-small vectors (same
numbers as NB3 and the RAG Lab). Then `find store_D -type f`, real sizes.
- [click] `chroma.sqlite3` (380,928 bytes): the 15 records; its write log (`embeddings_queue`) holds the 15 vectors.
- [click] The UUID folder is the HNSW segment: `data_level0.bin` (vectors + bottom-layer links), `link_lists.bin` (upper layers), `header.bin`, `length.bin`.
- [click] The surprise: 18,040,000 bytes for 15 vectors, and the header says 0 vectors inside with room for 10,000 (1,804 bytes each).
  Chroma keeps new vectors in SQLite’s log and moves them into HNSW once `sync_threshold` = 1,000 are waiting. Small
  collections are searched from the log.
Source: `logs/v5_store_local.json → D.files, D.hnsw_headers, D.sqlite_tables, D.collection_config` (header.bin parsed: Chroma 1.0’s
4-byte prefix + hnswlib’s 96-byte header).

## The Whole Dump in Chroma
`rag.add_vectors` with all 28,953 chunks: 26.5 s on a 4-vCPU Modal container. Two collections: 28,941 staff-readable, 12 HR-confidential.
- 195,546,412 bytes on disk (196 MB). SQLite is 125.8 MB.
- [click] Why SQLite is big: each chunk’s text is stored as the record and again in a full-text index (`embedding_fulltext_search`), plus 260,577 metadata rows = 28,953 × 9 fields.
- [click] The main HNSW segment holds 28,000 vectors (header), 1,804 bytes each = 384 × 4 bytes + 64 links (+ count and label). The last 941 still wait in the log.
- [click] Raw vectors alone: 44.5 MB (28,953 × 384 × 4). The rest is text, metadata, the keyword index and the graph.

## Searching Chroma
`col.query(query_embeddings=[q], n_results=5)` with Emma’s question embedded by `rag.Embedder("bge-small")`.
- Inside D only: §6 comes 3rd (0.644), after the revision table (0.673) and the FAQ answer on battery packs (0.667). One query: 4.1 ms.
- [click] Against all 28,941 staff chunks: the top 6 are e-mails and the weekly meeting note about Brightcell (0.835 … 0.746). One query: 5.8 ms.
- [click] The store just returns the nearest vectors. Retrieval quality was the previous sections’ job; the store makes it fast and durable.
HNSW against brute force for Emma’s question on the dump: the same top 10 (overlap 1.0).

## A Filter in the Query
Q-604 “How old can a UN 38.3 report be?”, whole dump, top 5.
- No filter: rank 5 is POL-SUP-003 **v2.2**, a superseded copy in `01_policies/old/`.
- [click] `where={"superseded": False}`: rank 5 becomes v2.3, the current version.
- [click] Cost in Chroma 1.0.15: p50 7.0 ms → 204.5 ms, p95 8.3 → 211.8 ms (224 golden questions, k = 10). The filter is evaluated outside the graph.
- [click] So the course keeps HR’s 12 chunks in their own collection: Emma’s search never opens it, and pays nothing for it.
(rag.py’s own note measured ~250 ms for `where` in Chroma 0.6.3; 1.0.15 is about the same.)

## A Vector Database Is an Approximate Search
Improved old slide 46. A toy graph of 42 points in 3 layers, searched by the real greedy rule (JS, no data). Chroma’s real
graph for the dump: 4 layers, up to 32 links per vector (64 on the bottom layer), from the parsed header.
- [click] The walk: start in the top layer, step to the neighbour closest to the question, drop a layer when none is closer.
- [click] It stops early, so it can miss. `logs/hnsw_check.json` (bge-small, 13,606 chunks, structured-400, chromadb 1.0.15): Chroma defaults returned 73.3% of the exact top 10.
- [click] ef_search 200: 90.6%; 1,000: 97.7%; 4,000: 99.9% at 7.3 ms (defaults 3.3 ms). That is `rag.HNSW`.

## Ask the class · Chroma in a folder works on one laptop. What must change when 200 staff search it all day?
Expect: a server, backups, permissions, many users at once, monitoring, updates when documents change, region. Then the next slide.

## What Production Asks of a Store
Ten questions; the four blue ones decided it for Northbridge: hybrid in one engine, filters during the search (HR must never
reach Emma), data residency (UK, else EU), re-indexing when the model changes. [click] [click] reveal the rest.
Source: `logs/v5_store_research.json → considerations`.

## Dedicated Vector Databases
Checked 4 Nov 2026 on vendors’ own pages (URLs per row in `logs/v5_store_research.json`). Talking points:
- Qdrant: hybrid in the engine via Query API prefetch + RRF; BM25 on a full-text index since 1.20 (Oct 2026); filters during HNSW; free 1 GB RAM / 4 GB disk, paused after a week idle.
- Pinecone: free Starter is us-east-1 only; EU from the $20 Builder plan; no London; full-text is a separate search you fuse yourself.
- Weaviate: hybrid built in; free sandbox capped at 100,000 objects (fits now, not at ten times).
- Zilliz (Milvus): built-in BM25 and server-side RRF; London free region verified.
- Chroma Cloud: US East and Belgium only; $5 a month of credits.
- Turbopuffer: London, BM25 + vector with server RRF, no free tier ($16 minimum); vendor-stated users Notion, Linear, Atlassian.

## Databases You May Already Run
- Postgres + pgvector: London on Neon and Supabase; but HNSW filters after the scan (iterative scans fix recall), and no real BM25 on Neon/Supabase in 2026 (Neon retired pg_search: new projects from 19 Mar, existing on 21 Sep).
- Elasticsearch/OpenSearch: BM25 native + kNN + RRF; self-managed Elastic RRF needs the Enterprise licence.
- Azure AI Search: hybrid + semantic ranker, UK South; the free tier is 50 MB and our ~75 MB does not fit.
- Vertex AI Vector Search: hybrid if you bring the sparse vectors; London.
- AWS: S3 Vectors is vectors only (no keyword search); Bedrock KB hybrid only on RDS, OpenSearch Serverless, MongoDB.

## Our Default: Qdrant
Why (blue): hybrid in one call; filters inside HNSW; same code on a laptop (Docker) and in the cloud; dashboard + console; aliases.
- [click] [click] Limits (orange), two of them measured by us on our cluster: the default HNSW width lost recall (0.434 vs 0.566 exact), and its BM25 tokenizer splits ERR-PO-0412. Free clusters pause after a week, deleted after four; ours is Frankfurt.
- [click] When to choose something else: Postgres shop → pgvector; Microsoft shop with strict UK residency → Azure AI Search UK South.

## Walkthrough · 1 · A Free Cluster
Screenshot of Rajat’s cluster (RAGProject, v1.20.0, GCP europe-west3, HEALTHY, FREE TIER). The AWS free tier only offered São Paulo,
so we took GCP Frankfurt. [click] highlight: id, version, provider. [click] highlight: 1 node, 4 GiB disk, 1 GiB RAM, 0.5 vCPU.
Note: the endpoint is visible in the screenshot; it is not a secret (the key is), but blur it if you prefer.

## Walkthrough · 2 · The Key Lives in One File
`vectordb.env` (values shown as dots), gitignored by `*.env`; the script reads only `QDRANT_URL` and `QDRANT_API_KEY` from it,
passes them to Modal as a secret, and asserts that neither value appears in any log it writes. [click] [click]

## Walkthrough · 3 · Create the Collection
Code from `experiments/v5_store_cloud.py::do_ingest`. One named vector `dense`, 384, cosine. [click] Payload indexes before the
data (bool: confidential, superseded, future; keyword: folder, doc_id, file, status). [click] A full-text index with BM25 scoring on
`text` (word tokenizer) and a second on `text_code` (code tokenizer) to compare. Created in 1.82 s. Screenshot: the Info tab
(green, 384 · Cosine, m 16, ef_construct 100).

## Walkthrough · 4 · Upsert D, Then the Dump
D first: 15 points in 0.31 s (point ids 101–115; §6 is 106). [click] Then 28,938 in 131.2 s, batches of 256, Modal (US) → Frankfurt.
[click] Screenshot of the collections list: northbridge_docs, alias northbridge, GREEN, 28 953 points, 2 segments.
[click] 28,953 points · 12 HR-confidential · 736 superseded · 25,103 in the HNSW graph. [click] Qdrant leaves small segments unindexed and
scans them exactly; search still covers all points.

## Walkthrough · 5 · The Points in the Dashboard
Screenshot: Points tab, filter `id:106`. [click] payload: cite, text, file, section. [click] version, status, the flags. [click] vector
`dense`, length 384, Find Similar. [click] “Open a few points and read them”: the cheapest ingestion test there is.

## Walkthrough · 6 · Search in the Console
Screenshot of the console running (read-only):
`POST collections/northbridge/points/query {"query": {"text": "ERR-PO-0412"}, "using": "text", "filter": {"must_not": [{"key": "confidential", "match": {"value": true}}]}, "limit": 5}`
[click] the request; [click] the filter is part of it; [click] first: QRC-03 quick-fix card for ERR-PO-0412 (16.67);
[click] third: MAN-ERR-72 p.13 **ERR-MAT-0412**, a different error: Qdrant’s tokenizers split the code into err / po / 0412 (our `rag.tokenize` keeps the whole code as well as its parts).

## Walkthrough · 7 · Emma’s Filter, From Python
Q-901 “What is the salary band for a senior buyer?” asked as PUR-EXEC, hybrid (hnsw_ef 2,000).
- [click] No filter: ranks 1 and 2 are HR-CONF-007 (salary bands), confidential.
- [click] Emma’s filter: none; the top is approval_limits.html.
- [click] Cost of the filter on the cluster: dense p50 277.5 ms (none) vs 277.4 ms (Emma) vs 277.7 ms (+ not superseded); round trip 273.5 ms. Payload index + filterable HNSW: no extra cost, unlike Chroma’s `where`.
Scan of five HR questions (`permission_scan`): unfiltered top 5 held confidential chunks for 4 of 5 questions.

## Walkthrough · 8 · Measure Recall on the Cluster
`logs/v5_store_ef.json`: dense recall@5 on the cluster: default 0.434, hnsw_ef 128 0.439, 512 0.468, 2,000 0.551, exact 0.566
(the course grid, Chroma with ef_search 4,000, measured 0.561 for bge-small on the same chunking: `rag_grid.json`).
p50 103 / 106 / 110 ms (default / 2,000 / exact, network included, ~99 ms round trip in that run).
[click] [click] [click] “Default lost almost a quarter of what exact finds”; we set hnsw_ef = 2,000 everywhere after this.

## Walkthrough · 9 · Hybrid Inside the Engine
Prefetch dense (20) + BM25 (20), fused by `RrfQuery(Rrf(k=60))`. [click] The reranker (bge-reranker-base) stays in our service.
[click] ERR-PO-0412, dense top 3: svc:po_release, the printed PO register, MAN-ERR-72 ERR-MAT-0412 (no gold).
[click] BM25: QRC-03 quick fix first. [click] Hybrid: RN-7.2.3-P1, MAN-ERR-72 ERR-MAT-0412, error_messages.html.
[click] Recall@5 (224 golden, evaluate.py, each asker’s filter): dense 0.551, BM25 word 0.737, BM25 code 0.737, hybrid 0.702.
Hybrid below BM25 alone, as in our own grid (rag.BM25 0.771, hybrid 0.742): why the chosen pipeline is BM25 + reranker. Code tokenizer:
exact-code recall@5 0.667 vs word 0.630.

## Walkthrough · 10 · How Fast, and What It Costs
From Modal (US) to Frankfurt: round trip p50 273.5 ms; dense 279 ms, BM25 274 ms, hybrid 279 ms p50, 285 ms p95.
An earlier run from another Modal container: round trip 99.2 ms, hybrid p50 103 ms. [click] Same code against Qdrant 1.20 inside our
own container: hybrid p95 15.5 ms (that collection’s 8 small segments were never HNSW-indexed: exact scans).
[click] $0 a month (free tier); 121 MiB of 4 GiB disk, 251 MiB of 1 GiB RAM (console, read after the upload); 28,953 points.
Lesson: the 200 ms budget is broken by geography, not by the store. Run the app in the store’s region.

## Walkthrough · 11 · When the Model Changes
Vectors from two models cannot be compared. [click] The app queries the alias `northbridge`. [click] New collection, re-embed, run the
golden set, switch the alias atomically; roll back the same way. [click] Ours: northbridge → northbridge_docs.

## Ask the class · Who should add Emma’s filter?
Answer: 3, the search service, from the signed-in user’s role. Never the model (a prompt can be talked out of it), and not a
parameter the agent chooses.

## Check · Where the vectors live
1. [click] The search service. 2. [click] Chroma 7.0 → 204.5 ms p50; Qdrant 277.5 → 277.4 ms (network included). 3. [click] New 768-d
collection, re-embed all, rerun golden set, one alias switch.
