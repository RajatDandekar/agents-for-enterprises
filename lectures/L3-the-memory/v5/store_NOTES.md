# L3 v5 · section `store` · speaker notes

Where the vectors live: what a store keeps (Chroma, document D), metadata and filters, HNSW word by word, the production
choice, and the engineer’s checklist on our real Qdrant Cloud cluster, latency included. Every number on the slides comes
from `window.L3V5.store` (`v5/store_data.js`, written by `experiments/v5_store_data.py`) and the logs named below.
Runs: Chroma and the survey on 4 Nov 2026; the cluster walkthrough on 4 Nov; latency, the status facet, Q-605 and the
HNSW overlap check on 5 Nov (`experiments/v5_store_latency.py` → `logs/v5_store_latency.json`, read-only on the cluster).
Reworked 5 Nov 2026 after Dr. Rajat Dandekar’s review (`v5/REVIEW_2026-11-05.md`).

## Part · Where do 28,953 vectors actually live?
Bridge from the dense section: every chunk is 384 numbers; the question too. Now: where are they kept, and what do teams
run in production? “Whatever we do here, you will do in your project.”

## What a Vector Store Keeps
One idea: per chunk the store keeps an id, the text, the metadata and the vector, plus an index for fast search, and it
all lives in a folder on disk. The record is the real one for §6 of D (id "5", chunk 5 of D’s 15), read back from Chroma
with `col.get(include=[documents, metadatas, embeddings])` on Modal.
- Read the id and the text: the context header, then 6.1 to 6.4. The highlighted clauses are §6.2 and §6.4, the ideal answer.
- [click] Metadata: what `rag.add_vectors` stores (doc_id, file, folder, fmt, superseded, future, confidential). Next slides explain them.
- [click] The vector: first 8 of 384 numbers (−0.0353, 0.0477, …), length 1.00 (normalised, so cosine = dot product).
- [click] Plus an index: links between nearby vectors (HNSW, explained in two slides) so a search need not read every row.
  One record per chunk: 15 for D, 28,953 for the whole dump.
- [click] It is a folder on disk. The whole dump in Chroma: 195.5 MB (195,546,412 bytes); the raw vectors alone 44.5 MB
  (28,953 × 384 × 4 bytes). The rest is text, metadata and the index.
If someone asks what is in the folder (moved here from the old slides “Document D in Chroma” and “The Whole Dump in Chroma”):
`chroma.sqlite3` holds the records (ids, text, metadata) and a write log of the vectors; a folder with a long id is the HNSW
index (`data_level0.bin` keeps vectors and bottom-layer links, `link_lists.bin` the upper layers, plus `header.bin`, `length.bin`).
D’s folder is 18,040,000 bytes for 15 vectors because Chroma sets aside room for 10,000 (1,804 bytes each), and keeps new
vectors in SQLite’s log until `sync_threshold` = 1,000 are waiting. For the dump SQLite is 125.8 MB: each chunk’s text twice
(the record and a full-text index) and 260,577 metadata rows (9 per chunk); the main HNSW segment holds 28,000 vectors,
1,804 bytes each (384 × 4 + 64 links); the last 941 still wait in the log. Building it: `rag.add_vectors`, 26.5 s on a 4-vCPU
Modal container. Source: `logs/v5_store_local.json` (`experiments/v5_store_local.py`).

## Searching Chroma
`col.query(query_embeddings=[q], n_results=5)` with Emma’s question embedded by `rag.Embedder("bge-small")`.
- Inside D only: §6 comes 3rd (0.644), after the revision table (0.673) and the FAQ answer on battery packs (0.667). One query: 4.1 ms.
- [click] Against all 28,941 staff chunks: the top 6 are e-mails and the weekly meeting note about Brightcell (0.835 … 0.746). One query: 5.8 ms.
- [click] The store just returns the nearest vectors. Retrieval quality was the previous sections’ job; the store makes it fast and durable.

## Metadata: What Each Chunk Says About Itself
Teach from zero. Metadata = fields stored with each chunk that the parser read from the file itself: its header block
(Document, Version, Effective, Status, Classification), its name and its folder (`corpus.file_meta`). The store keeps them
beside the vector. The card is point 106 on our cluster = §6 of D, payload as stored: doc_id POL-PUR-001, version 4.1,
effective 2026-04-01, status CURRENT, superseded false, future false, confidential false, audience “all staff”, file.
- [click] **Superseded**: replaced by a newer version of the same document. The Approval Matrix POL-APR-002 v2.0 (effective
  2024-04-01) was replaced by v3.0 (April 2026), but the old file is still in the dump (`01_policies/old/`). The screenshot is our
  dashboard’s Points tab filtered by `superseded:true`: the first hit is point 192, that v2.0, status "SUPERSEDED". The box moves
  from the filter to the status lines on the next click.
- [click] The status values that occur in our payloads, a facet over the whole collection: CURRENT 2,879 chunks, SUPERSEDED 180,
  DRAFT 7, “ISSUED, IN FORCE FROM 2027-01-01” 7, “PREVIEW, NOT INSTALLED” 6, “ISSUED, NOT YET IN FORCE” 3, nothing stated
  25,871 (e-mails, transactions, master data state no status). The flags the parser sets: superseded = true on 736 chunks
  (status says SUPERSEDED/WITHDRAWN/OBSOLETE, or the file sits in an `old/` or `_legacy` folder, or its name says “(old)”);
  future = true on 16 (effective after today, or a PREVIEW); confidential = true on 12 (HR’s CONFIDENTIAL folder).
Source: `logs/v5_store_latency.json → eu.facts` (status_values, counts, point_106, point_192); rule from `corpus.py::file_meta`.

## A Filter Inside the Search
Answers “what are metadata filters?” and “I did not know we could add filters in RAG search”. The problem: Q-605, a purchase
executive asks “What is a purchase executive’s approval limit?” The dump gives £250,000 (v3.0, gross, in force), £200,000
(v2.0, superseded; also the 2024 starter deck) and £150,000 (the 2016 intranet page, net). Only one is in force. And
HR-confidential chunks must never reach a purchase executive.
- Every store takes a filter with the query: Chroma `where=`, Qdrant `query_filter=`, pgvector a SQL `WHERE`. A filter is a
  condition the store checks on the metadata, like a WHERE clause.
- [click] Before: hybrid (dense + BM25, RRF on the server, hnsw_ef 2,000) with the HR filter only. Rank 4 is POL-APR-002
  v2.0, superseded, saying £200,000. (“says …” chips: the limit from the golden facts for Q-605, shown where that amount is in
  the chunk’s text.)
- [click] After: + superseded = false. The store checks it inside the search, so the chunk never competes: v2.0 is gone and the
  five places go to chunks that pass (the user table rows move in). The code card highlights the superseded condition.
- [click] The 2016 page stays first in both. Nothing in it says it is old (its metadata is empty: no doc_id, version or status),
  so no filter can drop it. A filter is only as good as the metadata: a human rule at parse time (“everything in
  `intranet_export_2016/` is history”) would fix it. This is check question 2.
Source: `logs/v5_store_latency.json → eu.facts.q605` (read-only on the cluster, 5 Nov). Same mechanism for HR: checklist step 7.

## HNSW, Word by Word
Answers “HNSW full form? Explain properly.” HNSW = Hierarchical Navigable Small World. Exact search compares the question with
all 28,941 vectors: fine today, slow at ten times the size. HNSW follows links instead. The toy: 42 random points (not data),
searched by the real greedy rule. Build it one word at a time:
- [click] **Small world**: each point linked to its 3 nearest (grey) plus 4 long links (dashed orange). Any point is then a few
  hops from any other.
- [click] **Navigable**: the greedy walk on that one layer. From the start, step to whichever neighbour is closer to the question
  (the diamond); stop when none is. Here: 5 hops, and one of them uses a long link.
- [click] **Hierarchical**: sparse upper layers for long jumps, a dense bottom layer for the fine search: motorways, then local
  roads. From the top: 1 hop on layer 2, 2 on layer 1, 1 at the bottom (the flat walk needed 5).
Real graphs: Chroma’s graph for the dump has 4 layers (parsed header); our Qdrant collection uses m = 16.

## Two Settings, and Why It Can Miss
- **m**: links per point. More links, a better graph, more memory. Qdrant’s default on our collection: 16 (Info tab).
- **ef**: how many candidates the walk keeps as it searches (`ef_search` in Chroma, `hnsw_ef` in Qdrant). Larger: closer to exact, slower.
- [click] It can miss: the walk stops where no neighbour is closer, even if a closer vector sits elsewhere. Our own checks,
  share of the exact top 10 that came back: Chroma defaults 73.3%, ef_search 4,000 99.9% (`logs/hnsw_check.json`, 13,606
  chunks, 3.3 ms → 7.3 ms per query); our Qdrant cluster at the defaults 79.1%, hnsw_ef 2,000 97.2% (224 golden questions, no
  filter, `eu.facts.overlap_at_10_vs_exact`; 17% of questions got less than half of the exact top 10 at the defaults).
- [click] Qdrant’s own ANN Recall check on our collection agrees (screenshot by the lead, 5 Nov): 100 stored points as
  questions, HNSW at the default settings against exact search, mean recall@10 0.835 ± 0.30; exact ≈ 9 ms, HNSW ≈ 2 ms per
  search. An independent confirmation of our own measurement. Recorded in `logs/v5_store_dashboard.json → ann_recall`.

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

## The Engineer’s Checklist for a New Store
Replaces the 11-step walkthrough (“good but tough”): the same real cluster, now told as ten decisions that are in the
student’s control, in the order a new project meets them, each with what we chose for Northbridge and the measured effect
(blue). Read row one; [click] row two. “For your own project, walk this list.”
1 round trip 93.9 → 14.0 ms · 2 the script refuses a log that holds the key · 3 a new model is a new collection · 4 filter
cost nothing measurable · 5 28,953 points in 131 s · 6 recall@5 0.434 → 0.551 · 7 HR chunks in the top 5: 2 → 0 · 8 202 →
103 ms · 9 ten searches 1,051 → 202 ms · 10 one atomic alias switch.

## Checklist · 1–2 · Region, Tier and Key
1 · Choose the region first: next to the app, and where the data may live. Ours: GCP europe-west3, Frankfurt (the AWS free
tier only offered São Paulo). Screenshot: RAGProject, v1.20.0, HEALTHY, FREE TIER; ID and endpoint blurred.
- [click] (box: the provider) Round trip, the smallest call (count): 93.9 ms from Modal in the US, 14.0 ms from Modal’s EU region
  (`region="eu"`; it landed on GCP eu-south. Modal does not offer europe-west3 or eu-central-1 to this workspace: both refused).
- [click] (box: the node) Free tier: 1 node, 0.5 vCPU, 1 GiB RAM, 4 GiB disk, $0. We use 121 MiB of disk and 251 MiB of RAM
  (console, read after the upload, `logs/v5_store_dashboard.json`).
- [click] (box: API Keys) 2 · The key: the cluster’s API Keys tab makes a database key; anyone holding it can read every document.
  It lives in `vectordb.env` (gitignored by `*.env`), reaches Modal as a secret, and the scripts assert that neither the key nor
  the endpoint appears in any log they write. Never in code, a notebook, a log, the model’s prompt or a slide.

## Checklist · 3–4 · Schema and Indexes
Code from `experiments/v5_store_cloud.py::do_ingest` (created in 1.82 s).
- 3 · One named vector `dense`, 384, cosine: it must match the model (bge-small). A 768-d model needs another collection (step 10).
- [click] 4 · Payload indexes on the fields you filter on, before the data (bool: confidential, superseded, future; keyword:
  folder, doc_id, file, status), and a full-text index with BM25 scoring on `text` (word tokenizer; a second on `text_code`
  with the code tokenizer, to compare).
- [click] What the index buys, p50 over 224 questions: Chroma’s `where` (no payload index, evaluated outside the graph) 7.0 →
  204.5 ms; Qdrant with the index 277.5 → 277.4 ms, network included (~273 ms of it is the trip). That is why the course keeps
  HR’s chunks in their own Chroma collection, and why in Qdrant a filter is free.
Screenshot: the Info tab (green, 384 · Cosine, m 16, ef_construct 100).

## Checklist · 5 · Upload, Then Look
D first: 15 points in 0.31 s (ids 101–115; §6 is 106), then 28,938 in 131.17 s, batches of 256, Modal (US) → Frankfurt.
Screenshot: Visualize tab, Qdrant’s own UMAP map of a 3,000-point sample of our dense vectors coloured by folder
(request `{"limit": 3000, "using": "dense", "color_by": {"payload": "folder"}}`); legend counts are of the sample:
transactions 1,849, master data 713, manuals 178, service definitions 99, procedures 42, policies 25 … Chunks of the same kind
sit together: the islands are families of similar records. “This is what we uploaded.”
- [click] Points tab, `id:106` (cropped to the payload): §6 of D with its payload and its 384-number vector. Open a few points
  and read them: the cheapest ingestion test there is.
- [click] Counts read back: 28,953 points · 12 HR-confidential · 736 superseded · 25,103 in the HNSW graph. Qdrant leaves small
  segments unindexed and scans them exactly; search still covers all points.

## Checklist · 6 · Measure Recall, Set ef
`logs/v5_store_ef.json`: dense recall@5 on the cluster: default 0.434, hnsw_ef 128 0.439, 512 0.468, 2,000 0.551, exact 0.566
(the course grid, Chroma with ef_search 4,000, measured 0.561 for bge-small on the same chunking: `rag_grid.json`).
p50 103 / 106 / 110 ms (default / 2,000 / exact, network included, ~99 ms round trip in that run).
[click] [click] [click] “Default lost almost a quarter of what exact finds”; we set hnsw_ef = 2,000 everywhere after this.

## Checklist · 7 · Filter by Who Is Asking
Q-901 “What is the salary band for a senior buyer?” asked as PUR-EXEC, hybrid (hnsw_ef 2,000). Every request carries the
asker’s filter (who adds it is the class question that follows: do not answer it here).
- [click] No filter: ranks 1 and 2 are HR-CONF-007 (salary bands), confidential.
- [click] The HR filter: none; the top is approval_limits.html.
- [click] Cost of the filter on the cluster: dense p50 277.5 ms (none) vs 277.4 ms (HR filter) vs 277.7 ms (+ not superseded);
  round trip 273.5 ms. Payload index + filterable HNSW: no extra cost, unlike Chroma’s `where`.
Scan of five HR questions (`permission_scan`): unfiltered top 5 held confidential chunks for 4 of 5 questions.

## Checklist · 8 · One Hybrid Request
Prefetch dense (20) + BM25 (20), fused on the server by `RrfQuery(Rrf(k=60))`: the RRF constant, 60, as `rag.RRF_K`.
- [click] The reranker (bge-reranker-base, a cross-encoder) stays in our service, on the top 20.
- [click] Recall@5 (224 golden, evaluate.py, each asker’s filter): dense 0.551, BM25 word 0.737, hybrid 0.702. Hybrid below
  BM25 alone, as in our own grid (rag.BM25 0.771, hybrid 0.742): why the chosen pipeline is BM25 + reranker.
- [click] Time per question from Modal in the US, p50, 30 golden questions: two requests (dense, then BM25, RRF in our code)
  202 ms vs one hybrid request 103 ms. One request saves one round trip; an agent that searches five times saves five.
Source: `logs/v5_store_cloud.json → golden`, `logs/v5_store_latency.json → suite_default_region.rest`.

## Checklist · 9 · Where One Question’s Time Goes
Dr. Rajat Dandekar liked the latency part: this slide and the next. Emma’s pipeline, each part measured on Modal in the US,
median (`v5_store_latency.py`, 30 golden questions unless said):
- embed the question, bge-small on the container’s CPU: 13.6 ms
- round trip to the store (US → Frankfurt): 93.9 ms
- search inside the store, the time Qdrant itself reports for the hybrid request (REST reply `time`): 6.3 ms
- [click] rerank the top 20, bge-reranker-base: 2,388 ms on a 4-vCPU container, 41.1 ms on an L4 GPU (`logs/v5_lexical_rerank_latency.json`)
- [click] write the answer, gemini-3.8-flash from the top 5 (5 calls): 3,962 ms p50
- [click] For one question, the models dominate. But an agent searches several times per question and each search pays the trip
  again: the round trips are the part you can cut without changing a model.

## Checklist · 9 · Cutting Round Trips
Five levers, each measured on our cluster from Modal, p50, before → after. [click] reveals the next row.
1. Run the app next to the store: round trip 93.9 ms (US) → 14.0 ms (Modal `region="eu"`, GCP eu-south). Modal refuses
   `europe-west3` and `eu-central-1` here, so Frankfurt itself was not available; a second EU run landed on AWS eu-north: 27.9 ms.
2. Keep one connection open: a new client per question 313 ms → one client kept open 103 ms (US, REST). A new connection
   repeats the TCP + TLS handshake, about two extra trips (and the client’s version check). With gRPC: 122 → 102 ms.
3. One hybrid request, not two searches: 202 → 103 ms (US, REST). From the EU over gRPC: 63 → 35 ms.
4. Ten questions in one call (`query_batch_points`): ten requests one after another 1,051 ms → one call 202 ms (US, REST).
   From the EU over gRPC: 353 → 121 ms. Useful when an agent fans out several searches at once.
5. gRPC instead of REST, near the store: one hybrid request from the EU 77.2 ms (REST) → 34.7 ms (gRPC). From the US the two
   were level (103 vs 102 ms): the 94 ms trip hides it. Why REST was slower in-region: with the reply carrying payload, REST
   took ~40 ms longer than the round trip (77 vs 37 ms without payload); gRPC did not. Probably TCP delayed acknowledgements
   on the HTTP/1.1 connection; we did not chase it further. Lesson: measure from where the app will run.
Sources: `logs/v5_store_latency.json` (`default_region`, `eu`: first pass; `suite_default_region`, `suite_eu`: the second
pass with the same payload on every call). Note: server-side RRF and our `rag.rrf` gave the same top 10 for 13 of 30
questions (ties and pool order differ); recall on the golden set is what we compared, not identical lists.

## Checklist · 10 · An Alias for the Next Model
Vectors from two models cannot be compared. [click] From day one the app queries the alias `northbridge`. [click] New
collection, re-embed, run the golden set, switch the alias atomically; roll back the same way. [click] Ours: northbridge →
northbridge_docs.

## Ask the class · Who should add Emma’s filter?
Answer: 3, the search service, from the signed-in user’s role. Never the model (a prompt can be talked out of it), and not a
parameter the agent chooses.

## Check · Where the vectors live
1. [click] The search service, from the signed-in user’s role.
2. [click] The 2016 page has no metadata saying it is old, so the superseded filter cannot see it; set `superseded` by a rule at
   parse time (everything in the 2016 intranet export is history).
3. [click] Run the app next to the store (93.9 → 14.0 ms a trip) and send the ten searches as one batch (1,051 → 202 ms from the US).
