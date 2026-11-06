# %% [markdown]
# # NB3 · The Knowledge: retrieving from Northbridge's documents
#
# **Agentic Systems Engineering · Lecture 3 · Vizuara · Dr. Rajat Dandekar**
#
# Northbridge Cycles builds e-bikes in Manchester on **Ledgerline ERP 7.2** (1998). Before we change anything, Henrik
# Weber, the plant head, has shared 28 years of documentation as a GitHub repository, `northbridge-docs`. Ask
# Northbridge must answer staff questions from it, with the document each answer comes from. Two running examples:
#
# > **Emma:** Can I buy the battery packs from Brightcell Energy? They quote £104.
# > **Emma:** What does ERR-PO-0412 mean and how do I fix it?
#
# This notebook follows the lecture:
#
# 1. clone the dump and audit it: files, classes, tokens
# 2. parse it two ways and see what the plain parser loses
# 3. the questions people ask, and the golden set we score against
# 4. why pasting everything fails
# 5. chunking three ways
# 6. BM25 from scratch, scored on the 224 documentation questions
# 7. a reranker, then embeddings in Chroma, and why exact codes need BM25
# 8. the shared answer step: Emma's question answered from RAG's passages (recorded, replayed)
# 9. the LLM Wiki: a real page, search over its sections, and one query's chain (recorded, replayed)
# 10. the race, read from the log
#
# **No API key needed.** Retrieval runs here, on your machine. Every model call (answers, the judge, the wiki's
# navigation) is replayed from our recorded runs, so you see exactly what happened in the race. Four exercises are
# marked `TODO (exercise N)`, each with its solution behind `SOLUTION = True`. Set it to `False` and try it yourself.

# %% setup

# %%
# Lecture 3's extra packages: parsers, the tokenizer, Chroma and the embedding and reranking models (about 2 minutes).
import importlib.util
if importlib.util.find_spec("chromadb") is None or importlib.util.find_spec("pdfplumber") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl",
                    "python-docx", "tiktoken", "scipy", "chromadb==1.0.15", "sentence-transformers", "pytesseract"], check=True)
if "google.colab" in sys.modules and subprocess.run(["which", "tesseract"], capture_output=True).returncode:
    subprocess.run("apt-get -qq install -y tesseract-ocr > /dev/null", shell=True)   # OCR for the six scans
os.environ.setdefault("LEDGER_WIKI_PROVIDER", "google-direct")   # where a live wiki call would go (only if you add a key)
SOLUTION = True

# %%
import collections
import json
import pathlib
import statistics
import time

from ledgerline.course.l3 import corpus as C
from ledgerline.course.l3 import evaluate as E
from ledgerline.course.l3 import rag


def pp(o, n=1400):
    """Print JSON, cut at n characters."""
    s = json.dumps(o, indent=1, ensure_ascii=False, default=str)
    print(s if len(s) <= n else s[:n] + " …")


# %% [markdown]
# ## 1 · Clone the dump, audit it
#
# Henrik's repository is public: `github.com/RajatDandekar/northbridge-docs`. `dump_root` clones it next to this
# notebook (or uses `$NORTHBRIDGE_DOCS`, if you set it to a copy you already have).

# %%
DOCS = C.dump_root(clone_to="northbridge-docs")
print(DOCS)
print((DOCS / "README.md").read_text()[:900])

# %%
files = C.list_files(DOCS)
by_folder = collections.Counter(f.split("/")[0] if "/" in f else "(root)" for f in files)
by_class = collections.Counter(C.FMT_CLASS.get(C.fmt_of(f), "other") for f in files)
print(len(files), "files")
for k, v in sorted(by_folder.items()):
    print(f"  {k:24} {v:4}")
print(dict(by_class))

# %% [markdown]
# Files are not the cost. Tokens are. We parse every file with the **structured** parser (one unit per PDF section,
# spreadsheet row, service, e-mail) and count tokens with tiktoken `o200k_base`. The first run parses all 693 files
# (a few minutes on Colab); the result is cached.

# %%
t0 = time.time()
units = C.parse(DOCS, parser="structured")
print(f"{len(units):,} units in {time.time() - t0:.0f} s; failures: {len(C.parse.failures)}")
tok_by_class = collections.Counter()
for u in units:
    tok_by_class[C.FMT_CLASS.get(u.fmt, "other")] += C.n_tokens(u.text)
total_tokens = sum(tok_by_class.values())
for k, v in tok_by_class.most_common():
    print(f"  {k:16} {v:>10,} tokens  {100 * v / total_tokens:4.1f}%")
print(f"  {'total':16} {total_tokens:>10,}")

# %% [markdown]
# ## 2 · Two parsers, one file
#
# The **plain** parser takes a file's text as it comes. The **structured** parser reads each format properly: e-mail
# headers decoded, every spreadsheet row written as `column: value`, scans read by OCR.

# %%
for rel in ["09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml",
            "99_scans/2019_Voltway_code_change_approval_signed.pdf"]:
    for p in ("plain", "structured"):
        us = C.parse_file(DOCS, rel, parser=p)
        text = us[0].text if us else ""
        print(f"--- {p:10} {rel.split('/')[-1]}: {len(us)} unit(s), {C.n_tokens(text)} tokens")
        print(text[:420] or "(no text: an image-only page)")

# %%
rows = {p: C.parse_file(DOCS, "05_master_data/SUPPLIER_MASTER.xlsx", parser=p) for p in ("plain", "structured")}
for p, us in rows.items():
    u = next(x for x in us if "VC-EIN-0042" in x.text)
    print(f"{p:10} {u.loc}  {u.text[:240]}")

# %% [markdown]
# ## 3 · The questions people ask
#
# The golden set has 304 real-style questions in three kinds. **Genesis** (create something) and **analytical**
# (count, sum, compare) need services and tools: Lecture 4 onward. **Documentation** questions are today's.

# %%
allq = C.questions(DOCS, category="all")
print(collections.Counter(q["category"] for q in allq))
G = E.Golden(DOCS)
print(len(G.qs), "documentation questions:", dict(collections.Counter(q["type"] for q in G.qs)))
q412 = G.by_id["Q-0412"]
pp({k: q412[k] for k in ("question", "reference_answer", "gold_sources", "must_contain")})

# %% [markdown]
# ## 4 · Why not paste everything?
#
# Gemini 3.8 Flash's window is 1,048,576 tokens (OpenRouter's listing on 3 Nov 2026; the largest window listed was
# 2,000,000). Our dump is:

# %%
print(f"{total_tokens:,} tokens = {total_tokens / 1_048_576:.1f} x Gemini 3.8 Flash's window, {total_tokens / 2_000_000:.1f} x the largest")
print(f"input cost of one question, if it fitted: ${total_tokens * 0.825 / 1e6:.2f} (at $0.825 per million input tokens)")

# %% [markdown]
# ## 5 · Chunking, three ways
#
# A chunk is what gets indexed and searched. Fixed windows cut wherever 200 tokens end; recursive splitting prefers
# paragraph and line breaks; structure-aware chunking packs whole sections and never cuts one unless it must.

# %%
policy = [u for u in units if u.file == "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"]
for m in ("fixed", "recursive", "structure"):
    ch = C.chunk(policy, m, 200, 0.0)
    print(f"--- {m}: {len(ch)} chunks")
    for c in ch[2:4]:
        print(f"  [{c.cite}] {c.n_tokens} tokens: {c.body[:110]!r}")

# %%
t0 = time.time()
chunks = C.chunk(units, "structure", 200, 0.15)   # the race winner's chunking: structured-structure-200-o15
print(f"{len(chunks):,} chunks in {time.time() - t0:.0f} s, {statistics.mean(c.n_tokens for c in chunks):.0f} tokens on average")
by_id = {c.cid: c for c in chunks}

# %% [markdown]
# ## 6 · BM25 from scratch
#
# BM25 scores a chunk by the query words it contains, weighted by how rare each word is (idf) and damped for long
# chunks. Our tokenizer keeps codes like `ERR-PO-0412` whole. Here is the scoring code we use, then a search.

# %%
import inspect
print(inspect.getsource(rag.tokenize))
print(rag.tokenize("What does ERR-PO-0412 mean? Rule 6.2, UN 38.3, BAT-500"))

# %%
idx = rag.Index("/tmp/nb3_index", chunks)
t0 = time.time()
bm = idx.bm25
print(f"BM25 over {len(chunks):,} chunks built in {time.time() - t0:.1f} s, {len(bm.vocab):,} terms")
t0 = time.perf_counter()
hits = bm.search("What does ERR-PO-0412 mean and how do I fix it?", 5, ~idx.conf)
print(f"search: {1000 * (time.perf_counter() - t0):.1f} ms")
for i, s in hits:
    print(f"  {s:6.2f}  {chunks[i].cite}")

# %% [markdown]
# Now score BM25 alone on all 224 documentation questions: is a gold source in the top 5? (`not_in_docs` and refused
# permission questions are left out of retrieval scoring, so 205 count.)

# %%
bm25_cfg = rag.Config(parser="structured", chunker="structure", size=200, overlap=0.15, retrieval="bm25", rerank=False, k=10)
bm25_only = rag.Retriever(idx, bm25_cfg)
rep = E.retrieval_only(lambda q, role: bm25_only.search(q, role=role), G)
s = rep["summary"]["overall"]
print(f"BM25 alone: recall@5 {s['recall@5']:.3f}, recall@10 {s['recall@10']:.3f}, MRR {s['mrr']:.3f}; "
      f"search p95 {1000 * rep['summary']['latency_s']['p95']:.1f} ms")

# %% [markdown]
# The grid measured this exact configuration (structured, structure-aware 200 tokens, 15% overlap, BM25 alone) at
# recall@5 0.771 and recall@10 0.873: the same numbers, from a fresh clone.
#
# ### TODO (exercise 1) · Which question types does BM25 miss?
# Print recall@5 for each question type from `rep["summary"]["by_type"]`, worst first.

# %%
if SOLUTION:
    for t, v in sorted(rep["summary"]["by_type"].items(), key=lambda x: x[1].get("recall@5") or 9):
        if v.get("recall@5") is not None:
            print(f"  {t:18} n={v['n']:3}  recall@5 {v['recall@5']:.2f}")

# %% [markdown]
# ## 7 · The reranker, then embeddings in Chroma
#
# A **cross-encoder** reranker (`BAAI/bge-reranker-base`) reads the question and each candidate together and scores
# the pair. It is slower than BM25, so it only reorders BM25's top 20. This is the race winner's configuration.

# %%
best_cfg = rag.best_config()
print(best_cfg.id)
best = rag.Retriever(idx, best_cfg)
for qid in ("Q-0412", "Q-EMMA"):
    q = G.by_id[qid]
    out = best.search(q["question"], role=C.role_of(q))
    print(f"--- {qid}: {q['question']}  ({1000 * out['seconds']:.0f} ms on this machine; timing {out['timing']})")
    for it in out["items"][:5]:
        print(f"  {it['rank']:2}. {it['cite']}")

# %% [markdown]
# On a CPU the cross-encoder takes seconds per question; the race ran it on an L4 GPU, where the whole search took
# 48 ms at p95. On 40 questions, how much does it add over BM25 alone? (On a CPU this takes a few minutes.)

# %%
sub = G.qs[::5][:40]
a = E.retrieval_only(lambda q, role: bm25_only.search(q, role=role), G, sub)["summary"]["overall"]
b = E.retrieval_only(lambda q, role: best.search(q, role=role), G, sub)["summary"]["overall"]
print(f"40 questions: recall@5 BM25 {a['recall@5']:.3f} -> BM25 + reranker {b['recall@5']:.3f}")

# %% [markdown]
# **Embeddings.** A dense retriever turns every chunk into a vector (here `bge-small`, 384 numbers) and finds the
# nearest vectors to the question's. We embed a small part of the dump (the manuals, the training cards and the
# policies) into a persistent **Chroma** collection, with HNSW set to search widely (`ef_search` 4000, as we measured).

# %%
import chromadb
part = [c for c in chunks if c.file.split("/")[0] in ("01_policies", "03_ledgerline_manuals", "11_training") and not c.meta.get("confidential")]
emb = rag.Embedder("bge-small")
t0 = time.time()
vecs = emb.passages([c.text for c in part])
print(f"{len(part):,} chunks embedded in {time.time() - t0:.0f} s, vectors {vecs.shape}")
client = chromadb.PersistentClient(path="/tmp/nb3_chroma")
col = client.get_or_create_collection("bge-small", configuration={"hnsw": dict(rag.HNSW)})   # cosine, ef_search 4000
if col.count() == 0:
    for i in range(0, len(part), 4000):
        col.add(ids=[str(j) for j in range(i, min(i + 4000, len(part)))], embeddings=vecs[i:i + 4000].tolist())
print(col.count(), "vectors in Chroma")

# %%
def dense(question, k=5):
    r = col.query(query_embeddings=[emb.query(question).tolist()], n_results=k, include=["distances"])
    return [(part[int(i)].cite, round(1 - d, 3)) for i, d in zip(r["ids"][0], r["distances"][0])]

for question in ["What does ERR-PO-0412 mean and how do I fix it?", "Can we buy battery packs from a supplier without a UN 38.3 certificate?"]:
    print("---", question)
    for cite, sim in dense(question):
        print(f"  {sim:.3f}  {cite}")

# %% [markdown]
# ### TODO (exercise 2) · BM25 against dense on the same part of the dump
# Build a BM25 over `part` (`rag.BM25([c.text for c in part])`) and print its top 5 for the ERR-PO-0412 question
# next to the dense top 5. Which one finds QRC-03 first?

# %%
if SOLUTION:
    bm_part = rag.BM25([c.text for c in part])
    for i, s in bm_part.search("What does ERR-PO-0412 mean and how do I fix it?", 5):
        print(f"  {s:6.2f}  {part[i].cite}")

# %% [markdown]
# ## 8 · The shared answer step (recorded, replayed)
#
# Every method in the race hands its passages to the same answer prompt: answer only from the numbered sources, cite
# each fact, give the rule in force today, refuse confidential HR content. We rebuild the race's prompt for Emma's
# question from the exact passages RAG retrieved in the race (`race_examples.json` lists their chunk ids), and replay
# the recorded answer and judge calls.

# %%
RX = json.loads((pathlib.Path(rag.__file__).parent / "race_examples.json").read_text())
from ledgerline.course.l3.wiki_llm import WikiLLM
ans_llm = WikiLLM("L3v4_race_rag_answers", max_tokens=2048)
judge_llm = WikiLLM("L3v4_race_rag_judge", max_tokens=512)
q = G.by_id["Q-EMMA"]
items = [by_id[i].as_item() for i in RX["questions"]["Q-EMMA"]["items"]]
msgs = E.answer_messages(q, items, answer_words=RX["answer_words"])
print(msgs[0]["content"])
print("…", len(msgs[1]["content"]), "characters of sources")

# %%
a = E.answer(q, items, ans_llm, answer_words=RX["answer_words"])
print(a["answer"])
print(f"\nreplayed: {a['replayed']} · {a['tokens_in']} tokens in · {a['llm_seconds']} s when it was recorded")
print("exact-fact check:", E.fact_check(q, a["answer"], G))
print("judge:", E.judge(q, a["answer"], judge_llm, G))

# %% [markdown]
# Which of the question's 11 gold sources did RAG bring back? The cites tell you why the answer misses £104 against
# £119 and PUR.CERT_CHK.

# %%
for it in items:
    print(" ", it["cite"])
print("gold:", [g["file"].split("/")[-1] for g in G.gold(q)])

# %% [markdown]
# ### TODO (exercise 3) · The same step for ERR-PO-0412
# Rebuild the items for `Q-0412` from `RX`, replay the answer with `ans_llm`, and run the exact-fact check.

# %%
if SOLUTION:
    q2 = G.by_id["Q-0412"]
    items2 = [by_id[i].as_item() for i in RX["questions"]["Q-0412"]["items"]]
    a2 = E.answer(q2, items2, ans_llm, answer_words=RX["answer_words"])
    print(a2["answer"][:900])
    print(E.fact_check(q2, a2["answer"], G))

# %% [markdown]
# ## 9 · The LLM Wiki
#
# Karpathy's LLM Wiki ("LLM Wiki", a gist, April 2026): an LLM reads the raw sources once and writes a wiki of linked
# pages, which it then maintains. Three layers: the raw sources (never edited), the wiki (pages the LLM owns, an
# `index.md` and a `log.md`) and the schema (`AGENTS.md`). Three operations: ingest, query, lint. Our wiki ships with
# the course package.

# %%
from ledgerline.course.l3 import wiki_query as WQ
w = WQ.Wiki(dump=DOCS)
print(len(w.pages), "pages")
print((w.root / "AGENTS.md").read_text()[:700])
print(w.page_text("sup-brightcell-energy")[:1600])

# %%
print((w.root / "index.md").read_text()[:700])
print([l for l in (w.root / "log.md").read_text().splitlines() if l.startswith("## [")][:3])

# %% [markdown]
# **Search over the wiki's sections** (no LLM): BM25 and bge-small over every section of every page, fused.

# %%
si = WQ.SectionIndex(w)
for hit in si.search("Can I buy the battery packs from Brightcell Energy? They quote £104.", role="PUR-EXEC", k=5):
    print(f"  [[{hit['page']}]] {hit['title']} > {hit['section']}")

# %% [markdown]
# **Query by navigation** (recorded, replayed): the model reads `index.md`, opens pages, follows links, and stops when
# it has enough. Each step is a model call.

# %%
nav_llm = WikiLLM("L3v4_wiki_nav", max_tokens=4000)
out = WQ.Navigator(w, nav_llm).navigate(q["question"], "PUR-EXEC")
for s in out["chain"]:
    print(" ", s)
print(len(out["items"]), "pages go to the shared answer step")

# %% [markdown]
# ## 10 · The race, from the log
#
# The full race ran on Modal: 224 questions, four methods, the same answer prompt (250 words), the same model and
# judge. Its log is in the course repository at `lectures/L3-the-memory/experiments/logs/race.json`.

# %%
import urllib.request
RACE_URL = "https://raw.githubusercontent.com/RajatDandekar/agents-for-enterprises/main/lectures/L3-the-memory/experiments/logs/race.json"
local = pathlib.Path("experiments/logs/race.json")   # when you run it inside the course repository
race = json.loads(local.read_text()) if local.exists() else json.loads(urllib.request.urlopen(RACE_URL).read())
print(f"{'method':10} {'judge':>6} {'facts':>6} {'cites':>6} {'search p95':>11} {'answer p50':>11} {'$/q':>8}")
for m, o in race["overall"].items():
    print(f"{m:10} {o['answer_correct']:6.1%} {o['fact_correct']:6.1%} {o['citation_correct']:6.1%} "
          f"{o['retrieval_p95_s'] * 1000:9.0f}ms {o['answer_p50_s']:10.1f}s {o['cost_per_q_usd']:8.4f}")
print("winner:", race["decision"]["winner"])

# %% [markdown]
# ### TODO (exercise 4) · Your own question
# Write a question Emma might ask, search it with `best` (RAG) and with `si` (the wiki's sections), and compare the
# top 3 of each. Which one would you trust, and why?

# %%
MY_Q = "Who must approve a purchase order of £300,000?"
if SOLUTION:
    for it in best.search(MY_Q, role="PUR-EXEC")["items"][:3]:
        print("  RAG ", it["cite"])
    for hit in si.search(MY_Q, role="PUR-EXEC", k=3):
        print("  wiki", f"[[{hit['page']}]] {hit['section']}")
