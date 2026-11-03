# The RAG Lab (Lecture 3, live)

**Live URL:** https://rajatworkspace--northbridge-raglab.us-east.modal.run
(the projector leaderboard: `/board`, the operator's page: `/admin`)

Modal app `northbridge-raglab`, workspace rajatworkspace, deployed from `deploy/raglab_modal.py`.

## What a student does
1. **Settings.** Every hyperparameter of the grid, as pills:
   - parser (plain / structured);
   - chunker (fixed / recursive / structure-aware);
   - chunk size (200 / 400 / 800 / 1,200 tokens) and overlap (0 / 15%);
   - embedding model (bge-small, bge-base, e5-small, gte-small, nomic v1.5);
   - retrieval (dense / BM25 / hybrid RRF), the reranker (bge-reranker-base) and query rewriting;
   - top-k (3 / 5 / 10).

   All 48 chunkings × 5 models are built and persisted in Chroma, so every combination has its own real index.
2. **Chunks.** Pick a document and see every chunk it becomes with this parser and chunker: the embedded text (with its context header), the token count and the exact location (pages, section, sheet rows).
3. **Search.** A live Chroma (and BM25) query on the persisted index for that setting, on the GPU.
   - The latency breakdown is measured inside the search: rewrite, embed, chroma, bm25, fuse, rerank.
   - It also shows the wait for the GPU, the index load, and the browser round trip.
   - For a golden question, it shows the reference answer, the gold sources, and which retrieved chunks are a gold source.
   - The asker role (Emma, Daniel, Aiko, an HR manager) changes what may be retrieved: HR chunks sit in their own Chroma collection that only HR roles query.
4. **Map.** A 2D PCA shadow of the chunk vectors (up to 4,500 points, coloured by folder) with the query as a star and its retrieved chunks ringed.
5. **Metrics.** For this setting, from the precomputed grid (`lectures/L3-the-memory/experiments/logs/rag_grid.json`):
   - recall@k, MRR, coverage@k, retrieval p50/p95 against the 200 ms budget;
   - recall by question type, its rank among the 2,112 measured settings, and the index's chunks, build time and size;
   - answer metrics as well, for the 9 settings that were answered.
6. **Leaderboard.** "Submit my setting" stores the name with that setting's measured golden-set **recall@5** (and MRR, p95).
   - Settings over the 200 ms budget rank below every setting inside it.
   - Each name keeps only its best.
   - It is stored in the modal.Dict `northbridge-raglab-state`.

## Running it in class (Sat 7 Nov, 07:00-09:00 UTC+5:30)
- **Automatic.** A cron (`class_warm`) sets one warm L4 container at 00:30 UTC on Sat 7 Nov (06:00 UTC+5:30). At start the container loads the five embedding models and the reranker, then copies all 48 indexes from the Volume to local disk in the background. On 3 Nov that took about 4 minutes, so it is ready long before 07:00.
- **Sleeping.** A daily cron (`class_cool`, 04:00 UTC = 09:30 UTC+5:30) sets min_containers back to 0. With no traffic the container sleeps after 15 minutes.

```
M=/Users/raj/.venv/bin/modal   # from the course root
$M run deploy/raglab_modal.py::admin --cmd purge-all     # before class: empty the leaderboard (purge-tests: only E2E/Load/Test names)
$M run deploy/raglab_modal.py::admin --cmd warm          # by hand: one warm container (prints /healthz)
$M run deploy/raglab_modal.py::admin --cmd status        # spend estimate, flags, leaderboard size, loaded indexes
$M run deploy/raglab_modal.py::admin --cmd pause --reason "back in 5 minutes"     # or --cmd resume
$M run deploy/raglab_modal.py::admin --cmd cap --cap 25  # the day's US$ cap (default 15)
$M run deploy/raglab_modal.py::admin --cmd purge-name --name "Someone"
$M run deploy/raglab_modal.py::admin --cmd cool          # after class
```
- **The admin token** is the Modal secret `northbridge-raglab` (`RAGLAB_ADMIN_TOKEN`), with a copy in the gitignored `raglab/admin.env`. The `/admin` page asks for it.
- **Do not redeploy during class.** The leaderboard survives a redeploy (it is in the Dict), but the new container has to copy the indexes again.

## Costs
- **Rate.** One L4 container (GPU + 4 vCPU + 32 GiB) is about $1.15 an hour (the Brain Lab's estimate). The app estimates its own spend from container uptime (60 s ticks) and refuses searches once the day's cap is reached; this is tested.
- **Class.** About 3.5 hours warm (06:00-09:30 UTC+5:30), so about $4. There is no LLM spend unless query rewriting is used on a non-golden question. Golden questions use the recorded rewrites; a free question with rewriting on is rewritten live only if a key with credit is set, and otherwise searched as typed, with a note.
- **Cap.** At most 2 containers (`max_containers=2`), 80 concurrent inputs each.

## Data and the best index
- **The Volume `northbridge-raglab`** holds:
  - `chroma/<chunking>/`: chunks.jsonl.gz, bm25.pkl, build.json, and a Chroma 1.0.15 persistent client with 2 collections per model (staff, `__hr`);
  - `vec/<chunking>/<model>.npy|.pca.npz`;
  - `grid/<chunking>.json` (rows with per-question ranks);
  - `answers/*.json`, `rewrites.json`, `rag_best.json`;
  - `best_index.tar.gz`.

  The Volume is about 38 GB; none of it is in git.
- **`GET /api/best_index.tar.gz`** (about 87 MB) is the best configuration's index: its chunks, BM25 and a bge-small Chroma collection. `ledgerline.course.l3.rag.rag_search()` downloads it on first use (into `~/.cache/northbridge-l3/rag_index`). If neither the cache nor the lab is reachable, it rebuilds the index from the dump.
- **`GET /api/best`** returns `rag_best.json`.

## Tests (3 Nov 2026)
```
$M run deploy/raglab_modal.py::test                                   # in-process API test on a GPU, real indexes: 20 checks
$M run ledgerline/ledgerline/raglab/tests/e2e_modal.py                # Playwright, desktop 1440 + phone 390: 24 steps
$M run ledgerline/ledgerline/raglab/tests/load_modal.py --n 30        # 30 students at once
```
Results are in `raglab/qa/` (gitignored): `test_api.json`, `e2e_report.json` + screenshots, `load_30.json`.

## Files
| File | What |
|---|---|
| `engine.py` | indexes (Volume → local disk, then chromadb), the live search with gold marking, chunk views, the PCA map, the grid metrics |
| `app.py` | FastAPI: the guard (pause, the $ cap, rate limit), search, chunks, map, metrics, leaderboard, best index, admin |
| `static/` | `lab.html` + `lab.js` + `lab.css` (on the Experience's `sky.css`, Google Sans Flex), `board.html`, `admin.html` |
| `tests/` | `e2e_modal.py` (Playwright on Modal), `load_modal.py` |
