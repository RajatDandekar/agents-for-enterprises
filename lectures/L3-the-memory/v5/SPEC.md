# L3 v5 rework: the shared contract (4 Nov 2026)

Rajat reviewed the L3 deck and rejected the way RAG, parsing and the LLM Wiki are taught: "blindly relying on ablation
experiment output". The v5 sections teach **from first principles on one document and one question**, so a student can
track every step by eye, then scale up to the whole dump with measurement. His brief, in order:

1. One document and one query. Explain the document's parts by hand (highlights), then the ideal answer.
2. Chunking, shown visually and clearly; select one chunk and follow it.
3. Chunks become vectors (illustrations, a flowchart). An **interactive 3D space** of the PCA components of the vectors.
4. The question becomes a vector and lands in that space.
5. Its nearest neighbours hold the parts of the true answer.
6. Chunk size, small to large, in the playground: students reason out the best size on this one document.
7. Where dense retrieval fails: error codes first, then more failure cases. "This is what builds intuition."
8. Other knobs (overlap, k, model…) where they help intuition.
9. Where vectors are stored: Chroma, shown for real; then production stores, with real screenshots and a walkthrough.
10. Parsing, redone: real examples one by one (a PDF with a table, a scan that needs OCR with the image shown, a
    spreadsheet, an e-mail…) so students feel why parsing matters.
11. BM25 from first principles on the same document: how rare words are prioritised, why it beats dense on codes.
12. Hybrid and RRF, and the reranker, each explained on the same document (RRF is arithmetic on ranks, no model; the
    reranker is a cross-encoder, `BAAI/bge-reranker-base`, not a generative LLM: say exactly what it is and does).
13. Engineering: questions to the class; to choose for real we must ablate on the whole data; metrics; how we evaluate
    and ablate; select the configuration for the use case.
14. The same treatment for the LLM Wiki.
Also: the old "tokenizer keeps codes whole" slide came from nowhere (teach tokenization only where BM25 needs it), and the
old scatter of all 2,112 configurations was confusing (replace it with one-knob-at-a-time comparisons).

## The running example (every RAG and BM25 section uses it)
- **Document D:** `01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf` (the dump is `/Users/raj/Claude_Brain/northbridge-docs`,
  public at github.com/RajatDandekar/northbridge-docs). Structured parser (`ledgerline/ledgerline/course/l3/corpus.py`): 26 units,
  2,178 tokens. `lectures/L3-the-memory/experiments/logs/deck_extract.json` already holds its units and chunks.
- **Question Q:** Emma's: "Can I buy the battery packs from Brightcell Energy? They quote £104." (golden set id `Q-EMMA`,
  `northbridge-docs/eval/questions.jsonl`).
- **Ideal answer from D alone:** §6.2 (lithium-cell parts such as BAT-500 only from a supplier with a valid UN 38.3
  certificate on file, checked before the first order) and §6.4 (a cheaper quote alone is no reason to change supplier for a
  lithium-cell part). D never says "Brightcell": the rest of the full answer needs other documents (multi-hop, later).
  Verify the exact clause wording from the parsed text; do not paraphrase it into quotes.
- **Default pipeline** (the chosen config, `course/l3/rag_best.json`): structured parser, structure-aware chunks of 200 tokens,
  15% overlap, header prefix; BM25 = `rag.BM25` with `rag.tokenize`; reranker `BAAI/bge-reranker-base` over the top 20;
  RRF k = 60 (`rag.rrf`). For dense, use `BAAI/bge-small-en-v1.5` (384-d, in `rag.EMBED_MODELS`) unless you say why not.
  Use the course code's own functions so every number matches what NB3 and the RAG Lab compute.
- **Second document for codes:** `03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf`, question
  `Q-0412` ("What does ERR-PO-0412 mean?").

## How to build (all sections)
- Work in `lectures/L3-the-memory/v5/`. Your section is `v5/<name>.html`: only `<section class="slide" …>` elements, in the
  deck's markup (1600×900 plates, absolute positions, `.lec-top`, `.step` for clicks, `data-plate="…"` titles; read
  `lectures/L3-the-memory/index.html`, `l3.css`, `figs.js`, `engine/plates.css`, `engine/plates.js` first). Your JS is
  `v5/<name>.js` (register figures as `FIGS.<name>_<fig>` so names never collide; data from `window.L3V5.<name>`), data in
  `v5/<name>_data.js`, CSS in `v5/<name>.css` with classes prefixed `<name>-`. Do **not** edit `index.html`, `figs*.js`,
  `l3.css` or `figdata.js`: the lead assembles.
- Preview: `v5/preview_<name>.html` = index.html's head and scripts plus your fragment and files. Check it with
  `/Users/raj/.venv/bin/modal run tools/deck_qa_modal.py --deck lectures/L3-the-memory/v5 …` (adapt the tool's entry file if it assumes
  index.html; keep 0 issues) and read the screenshots. Do not use the Browser pane: other agents share it.
- Rhythm per section (as L2/L4): part slide (a question as its title) → teach → the section's question to the class
  (`q hero` slide) → 1–3 check slides with answers on click. Keep slides uncluttered; one idea per slide; build up with steps.
- Every number from a real run or a real log, saved under `lectures/L3-the-memory/experiments/logs/v5_*.json` with the script
  that made it (`experiments/v5_*.py`). No fabricated output. Heavy compute (embeddings, rerankers, OCR, rendering many pages,
  LLM calls) on **Modal** (profile `rajatworkspace`, already current; `/Users/raj/.venv/bin/modal`), never on the laptop.
  Existing Modal patterns: `lectures/L3-the-memory/experiments/l3_modal.py`, `deck_extract_modal.py`.
- LLM calls: `gemini-3.8-flash` direct with the key in `/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env` (`GEMINI_API_KEY`). Never
  print or commit keys. OpenRouter is out of credit.
- Concept figures (flowcharts, architecture) may be PaperBanana (`tools/pb_modal.py`, professional, plain words) or clean
  built-up HTML/SVG diagrams that animate step by step with real content in them. No cartoons, no AI-sounding labels.
- Interactive figures must work offline in the deck (local files only; Three.js may load from cdnjs pinned, e.g.
  `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`, but prefer a small hand-written canvas 3D if simple).
- Words: plain, short sentences, British spelling, the second harness is always "our harness", "Dr. Rajat Dandekar". Never the real
  client's or product's names. The world is Northbridge Cycles on Ledgerline ERP 7.2 (`WORLD_V4.md`).
- Speaker notes: `v5/<name>_NOTES.md`, one entry per slide by plate title, with `[click]` steps.
- Do not commit; do not push; do not deploy. The lead integrates, QAs and commits.
- When done, report: the slide list (plate titles), the files, the logs, every number shown and where it comes from, and
  anything you could not do.
