# Lecture 3 films (The Memory)

These are three narrated Blender Cycles films for Lecture 3, "The Memory: RAG and the LLM Wiki". They follow the same running example as the slides: Emma Clarke at Northbridge Cycles, on Ledgerline, with the real Northbridge documentation dump.

- **Where they play.** Each film plays at the **end** of its section, as the recap after the theory.
- **Where the numbers come from.** Every number, cite and line of text on screen is read at build time from `build/data/l3_data.json`. `build/make_data.py` writes that file from these sources:
  - the recorded runs in `../experiments/logs/`;
  - the wiki itself, `ledgerline/ledgerline/wiki_v4`;
  - the live RAG Lab capture of 3 Nov 2026, `build/data/rag_capture.json`;
  - the race, `experiments/logs/race.json`;
  - the real bge-small vectors, `build/data/embed_qrc03.json` (`build/embed_modal.py`).
- **What is decorative.** Only these:
  - the form bars on Emma's screen;
  - the faint grid on the light table;
  - the number of sheets in each stack. The stack's **height** is the data: 1 m per 3.5 million tokens.

**Embedding.** Use `<video controls preload="metadata" poster="films/<name>.jpg">` with two `<source>` lines, `.webm` first, then `.mp4`. Never autoplay.

**Files.**
- `films/<name>.mp4` (H.264, faststart), `films/<name>.webm` (VP9 + Opus) and `films/<name>.jpg` (poster).
- All are 1920x1080 at 30 fps, mixed to -16 LUFS. The mp4 and webm are gitignored; the site build copies them from disk.

| Base name | Plays at the end of section | Duration |
|---|---|---|
| `rag` | 7: RAG from scratch ("How RAG works") | 2:37 (156.8 s) |
| `wiki` | 8: the LLM Wiki from scratch ("How the LLM Wiki works") | 2:42 (161.6 s) |
| `race` | 9: compare both ("The race") | 2:33 (153.1 s) |

## Look and sound (the L2 and L4 series)
- **World.** The L2 kit, unchanged in `build/kit/l2kit.py`, gives the midnight-slate studio, plinths and ceramic tiles. The model machine and capsules come from L4's `build/kit/props_l4.py`. The new props are in `build/kit/props_l3.py`:
  - the archive vitrines and their sheet stacks;
  - the paper with its real line bars;
  - the reader (the parser);
  - chunk tiles;
  - the light table of real PCA beads;
  - the BM25 card catalogue;
  - the reranker arch;
  - the wiki's page tablets: one mesh, with the page type's colour on each top edge;
  - the links as one curve of real arcs;
  - the dais.
- **Text.** All readable text is a 2D overlay in Google Sans Flex / Google Sans Code (`build/overlay.py`, copied from L4).
  - The `rag` spec also draws the recall ladder as bars.
  - The `wiki` spec draws the Brightcell page card from the real markdown, beside the captured Wikipedia article "E-bike" (CC BY-SA 4.0, credited on screen; the image is read from `build/cache/wikipedia/`, a copy of `figs/wikipedia/`).
- **Sound.**
  - Narration: ElevenLabs Daniel (`onwK4e9ZLuTAKqWW03F9`, eleven_multilingual_v2), speed 1.13. That is a little faster than L4's 1.08, to keep each film under three minutes. The key is read from `/Users/raj/Claude_Brain/cobol-mainframes/.env` and is never printed.
  - Music: L1's track, "Observatory" by Out To The World (Epidemic Sound), mixed at the L2/L4 level. It is in `films/music/`, which is gitignored.
  - SFX: the L4 set.

## How to rebuild
```sh
cd lectures/L3-the-memory/films/build
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run embed_modal.py   # once: the real vectors (CPU, about a minute)
python3 make_data.py                                                 # data/l3_data.json (stdlib)
python3 narrate.py <film> && python3 tidy_cues.py <film>
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::style --film <film> --frames 400,1800 --tag s1
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run --detach modal_films.py::full_spawn --film <film>
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::full_poll --call-id <id>
MODAL_PROFILE=rajatworkspace ~/.venv/bin/modal run modal_films.py::comp --film <film>
```
The Modal volume is `video-ad-edit:/l3films` (app `l3-films`, workspace rajatworkspace). The L2 and L4 builds are untouched.

## `rag`: How RAG works (section 7)
**Shots.**
1. Emma's screen with the ember error bar.
2. The archive. Three glass cases, each stack as tall as its tokens: unstructured 1.25M, structured 3.26M, semi-structured 0.18M.
3. QRC-03 slides through the reader. Its text bars, the real line lengths, come up with the headings in sky. A ledger sheet follows with its header row lit green.
4. The card is cut along its structure into its three real chunks (219, 215 and 216 tokens), each with a sky header.
5. Chunk 1's real 384-number bge-small vector rises as a plate.
6. The light table lights 3,620 beads at their real PCA positions; the card catalogue opens a drawer.
7. The question lands as a star at its real position. Its 10 real dense hits are ringed in ember: purchase-order services and ERR-MAT-0412.
8. Three green cards rise from the drawer: BM25's real top 3, all QRC-03.
9. 20 candidates run through the reranker arch. 10 come out in its real order, gold sources edged green.
10. The 10 slide into the model, and a green answer slab comes out.
11. The close: the stations light in turn. Then Q-EMMA's 11 gold sources rise in front of the archive; only the 2 the search found are green.

**Numbers from.**
- `audit.json`: totals, classes, facts visible.
- `rag_grid.json`: chunk count, HNSW settings, and the recall@5 ladder on the chosen chunking (0.561 / 0.771 / 0.893).
- `rag_failures.json`: exact codes and Q-EMMA.
- `rag_best.json`.
- The recorded Q-0412 answer: `rag_answers/structured-structure-200-o15__-__bm25__rr1__qr0__k10.json`.
- The live lab capture: chunks, the three searches and their timings, the PCA map.
- `embed_qrc03.json`: the plate, and the 0.63 similarity, which is labelled as computed for the film.

**Script** (the subtitles; the voice reads the same sentences with codes spelled out):

> Emma saves a purchase order, and Ledgerline stops her: ERR-PO-0412. What does it mean, and how does she fix it? The answer is in Northbridge's documents.
>
> Here they are: 693 files of PDFs, spreadsheets, e-mails, service definitions and scans. 4.69 million tokens: far too much to send with every question.
>
> First, we parse, with a reader for each kind of file: PDFs keep their pages and headings, and spreadsheet rows keep their column names. All 464 facts we check survive.
>
> Then we chunk, along each document's own structure: about 200 tokens a piece, with 15 percent overlap. The quick-reference card for this error, QRC-03, becomes three chunks. The whole pile: 28,953.
>
> Next, two indexes. An embedding model turns each chunk into 384 numbers, a point in space, kept in Chroma. And BM25 remembers which chunks contain which exact words.
>
> Now Emma's question. In vector space, its nearest neighbours are purchase-order services and ERR-MAT-0412: close in meaning, but the wrong code. BM25 matches the exact words, and puts QRC-03 first.
>
> Then a reranker reads the question beside each of the top 20, and puts them in order: 57 milliseconds. A right source in the top five: vectors alone, 56 percent; keywords, 77; keywords and the reranker, 89.
>
> The top ten go into the prompt, numbered, and the model answers from them, with citations: a supplier outside the UK needs VAT20-RC, then press F8 again. Search, 45 milliseconds. Answer, 12 seconds.
>
> That is RAG: parse, chunk, index, search, rerank, answer. 87 percent of the golden set answered correctly, a quarter of a cent each. Its hard case is Emma's Brightcell question, spread over eleven sources. The search finds two.

## `wiki`: How the LLM Wiki works (section 8)
**Shots.**
1. The archive under padlocks.
2. The model machine.
3. The dais with the hub: index.md, AGENTS.md and log.md (one cell per ingest line, 693).
4. Ingest:
   - parts flow from the cases into the model, and facts flow out;
   - 683 page tablets appear in 16 clusters, one per page type, in the order log.md first names them;
   - their 4,021 resolved links grow as arcs.
5. The Brightcell page lifts out. Its real lead, infobox, sections, links and references are drawn beside a real Wikipedia article, with matching parts boxed on both.
6. Emma's question: index.md lights. Arcs run to the three pages the navigator really opened: sup-brightcell-energy, pol-sup-003 and sop-pur-006.
7. The answer slab. 33 green threads run from those pages back to the case holding each of their sources.
8. File-back: the qa- page drops in beside Brightcell, linked to the 3 pages it used; index.md reaches it in one step.
9. The patch note RN-7.2.3-P6 arrives. The 4 pages it updated light, and the 3 it created drop in beside their kinds.
10. Lint: an ember ring sweeps the dais, and a flag rises over each of the 380 pages with findings.

**Numbers from.**
- `wiki_build.json`.
- The wiki manifest, its links and `log.md`.
- `wiki_query_chains.json` (Q-EMMA, wiki): the chain, tokens, answer, sources; and its file-back.
- `wiki_update.json`.
- `wiki_lint.json`: findings, by kind, and the 31 of 40 planted problems.
- `figs/wikipedia/boxes.json`.

**Script:**

> RAG goes back to the raw documents for every question. Andrej Karpathy proposed another way, an LLM Wiki: the model reads every source once, and writes what it learns into a wiki it keeps up to date.
>
> Three layers: the raw sources, 693 files, never edited; the wiki, markdown pages the model owns; and the schema, AGENTS.md, the rules for every page.
>
> First, ingest. The model reads the sources in 1,067 parts, takes out each fact with its quote and location, and writes it onto a page: one per supplier, policy, error code or screen. 683 pages, 4,035 links, and a line in log.md for each ingest.
>
> Each page is shaped like a Wikipedia article: a lead, an infobox, sections, links, and references to the exact source. Brightcell Energy: a prospective supplier in Lyon, not in the supplier master, its UN 38.3 report due in December.
>
> Emma asks: can I buy the battery packs from Brightcell? They quote £104. The model reads index.md, the table of contents, and opens three pages: Brightcell, the Supplier Policy, and the procedure for quotations.
>
> The answer: no, not today. Brightcell is not in the supplier master, and battery suppliers need a valid UN 38.3 certificate; price alone never decides. Each claim cites a page, and the pages cite 33 places in the sources.
>
> A good answer is not thrown away. It is filed back as a new page with 16 references, so the next person who asks finds it in one step.
>
> When a new document arrives, only the pages it touches change: patch note P6 updated four pages and created three, in 40 seconds, for 15 cents.
>
> And lint checks the whole wiki for superseded copies, contradictions and broken links. It found 31 of the 40 problems we planted.
>
> RAG reads the raw pile at every question. The wiki reads it once, and keeps what it learned as linked pages. Which should Ask Northbridge use? We race them.

## `race`: The race (section 9)
This film was built from `RACE_STORYBOARD.md` (kept as the design record) once `race.json` landed.

**Shots.**
1. A stack of 224 question cards at the start gate.
2. Four glass lanes: RAG, the wiki's navigation, the hybrid, sections only. A fifth lane is closed by an ember barrier: pasting the whole dump fits no model.
3. Two races on the recorded times: Q-0412 in real time, then Q-EMMA at 1.5x (the chip says so).
   - Each capsule moves at constant speed from the gate to the finish over its real `total_s`.
   - It turns from violet ("finding sources") to its lane colour ("answering") at its real `retrieval_s`.
   - A 2D timer runs over each capsule.
   - Each finish bar lights green or ember with the judge's verdict, and the missed facts are listed.
4. The whole golden set:
   - a glass meter per lane fills to its answer-correct rate;
   - a light strip runs down each lane, 0.25 m per second of median time to answer, with the slow-end search times in 2D;
   - a coin stack per lane, one coin per tenth of a US cent a question;
   - a 2D grid of answer-correct by question type, the leader in each row in green.
5. The decision: RAG's lane lights and the others dim. The measured fallback is shown in 2D as not live: RAG first, then the hybrid when RAG finds nothing.

**Numbers from.** `race.json`:
- `overall`: answer, fact and citation correct; retrieval and answer p50/p95; cost per question;
- `by_type`;
- `examples` (Q-0412, Q-EMMA): judge, facts missing, `retrieval_s`, `total_s`;
- `paste_all`;
- `update_cost`;
- `cascade`;
- `decision`.

The `rag` film's closing chip still shows the grid's 150-word answer run (87.1%, $0.0023). It is labelled as such, and the race's 250-word re-run gives 89.3% and $0.0046.

**Script:**

> Two ways to remember. Now we race them: the same 224 questions, the same model, the same judge, and the same 250-word limit on every answer.
>
> Four lanes: RAG, with keywords and a reranker. The wiki, navigating from index.md. A hybrid that searches the wiki's sections, then navigates. And sections alone. Pasting everything is out: 4.7 million tokens fit no model.
>
> First, Emma's error code. Go. RAG has its chunks in 43 milliseconds, and its answer in 9.2 seconds. Sections alone finish in 9.1, but miss VAT20-RC. The hybrid takes 13.3. The wiki navigates for six seconds, and answers in 15.7.
>
> Now Brightcell. Go. All four answer no, and the judge marks all four incomplete. RAG misses the two prices and the switch PUR.CERT_CHK. The wiki misses six facts.
>
> Across all 224 questions, the hybrid is the most accurate: 92.9 percent. RAG and the wiki tie at 89.3. Sections alone: 79.5.
>
> But watch the clock. RAG's search takes 48 milliseconds. The wiki must navigate first: 23 seconds at the slow end, the hybrid 11. To a full answer, RAG needs 6.2 seconds; the wiki and the hybrid, about 12.5.
>
> And the cost: RAG, under half a cent a question. The hybrid, 2.4 cents; navigation, 3.2. When a document changes, RAG re-indexes with no model at all; the wiki rewrites seven pages, for 15 cents.
>
> By question type, the wiki wins on procedures and tables. RAG wins on permissions. Questions that join many documents stay hard for every method: 71 percent at best.
>
> So Ask Northbridge uses RAG: inside the latency budget, nearly as accurate, at a fifth of the cost. The hybrid wiki stays as a measured fallback for when RAG finds nothing.

## Credits (on each end card)
- Dr. Rajat Dandekar · Vizuara. The LLM Wiki idea: Andrej Karpathy, "LLM Wiki" (gist, April 2026).
- Narration: ElevenLabs, voice Daniel. Music: "Observatory" by Out To The World, licensed from Epidemic Sound (not redistributed in the repo).
- Wikipedia "E-bike" (text CC BY-SA 4.0, Wikipedia contributors), captured 3 Nov 2026.
- Rendering: Blender 4.2.3 Cycles (96 samples, OIDN) on Modal L40S; composite with Pillow and ffmpeg on Modal.
