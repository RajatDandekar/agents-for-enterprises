# %% [markdown]
# # NB3 · The Memory: giving Ask Rasoi knowledge
# **AI Agents for Enterprises · Lecture 3 · Vizuara · Dr. Rajat Dandekar**
#
# Kavita Joshi, purchase executive at Rasoi Steel Works, asks Ask Rasoi:
#
# > *"Can I buy the gaskets from Shakti Seals? They quote ₹10.40"*
#
# The right answer is **no**. Gaskets touch food, and Purchase Policy **POL-PUR-001 §6.2** allows food-contact parts
# only from a supplier with a valid food-grade certificate on file. Shakti Seals has none. That rule lives in a document
# (and in Suresh's head), never in the model.
#
# In this notebook you build, by hand, every piece that lets Ask Rasoi find and cite that rule:
#
# 1. ask the bare brain (it does not know Rasoi)
# 2. paste everything, and count what it costs
# 3. chunk the documents · **exercise 1**
# 4. keyword search, BM25 by hand · **exercise 2**
# 5. embeddings and cosine similarity · **exercise 3**
# 6. fuse the two rankings (RRF) · **exercise 4**, then rerank
# 7. assemble the RAG prompt and answer · **exercise 5**
# 8. check the citations · **exercise 6**
# 9. evaluate on a few of the 40 questions
# 10. Ask Rasoi gains its `search_policy` tool
# 11. your module: start A3
#
# Everything here is fictional: Bahi ERP 7.2, Rasoi Steel Works, its people and suppliers.
# **Replay mode** plays back our recorded model calls, vectors and scores, so no key and no model download is needed.

# %% setup

# %%
import json, math, re
import pandas as pd
from bahi.llm import LLM
from bahi.agent import retrieval as R
from bahi.course import l3
from bahi.course.l3.questions import Q as QUESTIONS, grade

pd.set_option("display.max_colwidth", 110)
MODEL = l3.MODEL                      # gemini-3.8-flash, the course's default tier
# The recorded replies come from our experiment runs (cassettes L3v3_coldopen, L3v3_story, L3v3_eval, L3v3_knowledge),
# so this notebook replays exactly the calls the deck shows. With your own key, new questions are called live.
llm = LLM(MODEL, cassette="L3v3_story", max_tokens=4096)
SHAKTI = l3.SHAKTI
SOLUTION = True                       # set to False to write the exercises yourself
print(SHAKTI)

# %% [markdown]
# ## 1. The bare brain
# Ask Rasoi as it was at the end of Lecture 2: a model and a system prompt, no documents, no tools.

# %%
print("SYSTEM:", l3.SYSTEM_BRAIN, "\n")
brain = l3.brain_answer(SHAKTI, LLM(MODEL, cassette="L3v3_coldopen", max_tokens=4096))
print("ASK RASOI (brain):", brain["answer"])

# %% [markdown]
# It answers with confidence, and it never mentions the food-grade certificate. The model's weights were frozen at
# training time, on public text. Rasoi's policy is private and was amended in September 2026. The only way Rasoi's
# rules reach the model is the **context window**: the tokens we send on this one call.

# %% [markdown]
# ## 2. The simplest fix: paste everything
# Load the corpus. Each document starts with front-matter: an id, a version, the date it takes effect, and who may read it.

# %%
docs = R.load_corpus()
K = R.clearance_for("KJOSHI")
corpus = pd.DataFrame([{"doc_id": d.doc_id, "title": d.title, "effective": d.effective, "audience": d.audience,
                        "words": len(d.body.split()), "tokens": l3.count_tokens(d.body),
                        "kavita_may_read": R.allowed(d, K)} for d in docs]).set_index("doc_id")
corpus

# %%
visible = [d for d in docs if R.allowed(d, K)]
FULL = "\n\n".join(f"===== {d.doc_id}: {d.title} v{d.version}, effective {d.effective}"
                   + (f", amends {', '.join(d.amends)}" if d.amends else "") + f" =====\n{d.body}" for d in visible)
full = R.answer_with(llm, SHAKTI, FULL)
print(f"prompt: {full['tokens_in']:,} tokens in · cost ₹{llm.log[-1].cost_inr:.3f} for this one question\n")
print(full["answer"])

# %% [markdown]
# Pasting everything works on our small corpus, but every question pays for every page, and Kavita's prompt would also
# carry pages she may not read (we left the HR page out by hand). Retrieval sends only the clauses that answer.

# %% [markdown]
# ## 3. Chunking
# We fetch pieces, not documents. A good chunk is **one clause, whole, with its heading attached**, and its id is its
# citation: `POL-PUR-001 §6.2`.
#
# ### Exercise 1: a section chunker
# Start a new chunk at every `## N. Heading` and at every line that begins with a clause number `N.M ` inside section N.
# Keep the heading with each chunk. Return a list of `(section, heading, text)`.

# %%
def my_chunker(doc):
    # TODO (exercise 1): split doc.body into (section, heading, text) chunks
    if not SOLUTION:
        raise NotImplementedError("write my_chunker")
    out, h2, cur = [], ("", ""), None
    for line in doc.body.splitlines():
        if line.startswith("# "):
            continue
        m2 = re.match(r"^##\s+(\d+)\.\s+(.*)$", line)
        mc = re.match(r"^(\d+\.\d+)\s+\S", line)
        if m2:
            if cur: out.append(cur)
            h2 = (m2[1], m2[2].strip()); cur = [m2[1], f"{m2[1]}. {m2[2].strip()}", ""]
        elif mc and mc[1].split(".")[0] == h2[0]:
            if cur: out.append(cur)
            cur = [mc[1], f"{h2[0]}. {h2[1]}", line]
        elif cur is not None:
            cur[2] += "\n" + line
    if cur: out.append(cur)
    return [tuple(c) for c in out if c[2].strip()]


pp = next(d for d in docs if d.doc_id == "POL-PUR-001")
mine = my_chunker(pp)
lib = R.chunk_by_section(pp)
print(len(mine), "chunks (yours) ·", len(lib), "chunks (library) · same sections:", [m[0] for m in mine] == [c.section for c in lib])
print()
print(next(c for c in lib if c.section == "6.2").render())

# %% [markdown]
# Compare the naive cut: windows of 120 words. Find the window that holds §6.2.

# %%
for c in R.chunk_fixed(pp, size=120, overlap=20):
    if "food-grade" in c.text:
        print(c.id, "→", c.text[:420], "...\n")

# %% [markdown]
# The window starts in the middle of another clause, carries pieces of §5 and §6.1, and has no id you could cite.

# %% [markdown]
# ## 4. Keyword search: BM25 by hand
# BM25 scores a chunk by the question's words it contains:
# * **rare words count more**: idf(t) = ln(1 + (N − n_t + ½) / (n_t + ½)), where N is the number of chunks and n_t the
#   number that contain t;
# * **repeats help less and less** (k1 = 1.2), and **long chunks are discounted** (b = 0.75):
#
# score(q, d) = Σ_t idf(t) · tf·(k1+1) / (tf + k1·(1 − b + b·|d|/avgdl))

# %%
ret = l3.retriever("KJOSHI")            # Kavita's index: only what her role may read, as of 26 Oct 2026
docs_tok = [R.tokenize(c.context_text) for c in ret.chunks]
N, avgdl = len(docs_tok), sum(map(len, docs_tok)) / len(docs_tok)
q1 = "Can we buy the 5-litre gaskets from a supplier that doesn't have a food-grade certificate? Their price is much better."
print("chunks:", N, "· average length:", round(avgdl, 1), "words\nquestion as BM25 sees it:", R.tokenize(q1))

# %% [markdown]
# ### Exercise 2: idf and the BM25 term score

# %%
def my_idf(term):
    # TODO (exercise 2a): how rare is the term across Kavita's chunks?
    if not SOLUTION:
        raise NotImplementedError
    n = sum(1 for d in docs_tok if term in d)
    return math.log(1 + (N - n + 0.5) / (n + 0.5))


def my_bm25(query_tokens, doc_tokens, k1=1.2, b=0.75):
    # TODO (exercise 2b): sum the term scores for one chunk
    if not SOLUTION:
        raise NotImplementedError
    tf = {t: doc_tokens.count(t) for t in set(query_tokens)}
    return sum(my_idf(t) * f * (k1 + 1) / (f + k1 * (1 - b + b * len(doc_tokens) / avgdl))
               for t in query_tokens if (f := tf.get(t, 0)))


i62 = next(i for i, c in enumerate(ret.chunks) if c.id == "POL-PUR-001 §6.2")
qt = R.tokenize(q1)
print("yours  :", round(my_bm25(qt, docs_tok[i62]), 3))
print("library:", round(sum(ret.bm25.term_scores(qt, i62).values()), 3))
print(pd.DataFrame([{"term": t, "chunks containing it": sum(1 for d in docs_tok if t in d), "idf": round(my_idf(t), 2),
                     "in §6.2": docs_tok[i62].count(t)} for t in dict.fromkeys(qt)]).to_string(index=False))

# %%
top = sorted(range(N), key=lambda i: -my_bm25(qt, docs_tok[i]))[:6]
pd.DataFrame([{"rank": r + 1, "chunk": ret.chunks[i].id, "bm25": round(my_bm25(qt, docs_tok[i]), 2),
               "heading": ret.chunks[i].heading[:60]} for r, i in enumerate(top)])

# %% [markdown]
# §6.2 is not first. Supplier Policy §4.2 wins partly on the word *better*: Kavita meant a better price, §4.2 says
# "grade 304 or better". Keywords cannot tell meanings apart.

# %% [markdown]
# ## 5. Embeddings and cosine similarity
# An embedding model turns a text into a list of numbers (ours, `bge-small-en-v1.5`, gives 384). Texts that mean
# similar things point in similar directions. **Cosine similarity** measures that: cos = (a·b) / (|a|·|b|), 1 = same direction.
#
# ### Exercise 3: cosine similarity

# %%
def my_cosine(a, b):
    # TODO (exercise 3)
    if not SOLUTION:
        raise NotImplementedError
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


qv = ret.embedder.embed([q1], kind="query")[0]
print("vector length:", len(qv), "· first five numbers:", qv[:5])
print("cosine(question, §6.2) =", round(my_cosine(qv, ret.vecs[i62]), 4))
vtop = sorted(range(N), key=lambda i: -my_cosine(qv, ret.vecs[i]))[:6]
pd.DataFrame([{"rank": r + 1, "chunk": ret.chunks[i].id, "cosine": round(my_cosine(qv, ret.vecs[i]), 4)} for r, i in enumerate(vtop)])

# %% [markdown]
# By meaning, §6.2 comes first. But embeddings have their own blind spot: codes such as `ERR-PO-0412` carry no meaning
# for the model. Try it:

# %%
for m in ("bm25", "vector"):
    print(m, [h.chunk.id for h in ret.search("What does error ERR-PO-0412 mean and how do I fix it?", k=3, mode=m)])

# %% [markdown]
# ## 6. Hybrid search: reciprocal rank fusion, then rerank
# Two rankings, in different units (BM25 ≈ 20, cosine ≈ 0.7). **Reciprocal rank fusion** adds ranks, not scores: each
# list gives an item 1 / (60 + rank).
#
# ### Exercise 4: RRF

# %%
def my_rrf(lists, k=60):
    # TODO (exercise 4): lists of chunk ids, best first → {chunk id: fused score}
    if not SOLUTION:
        raise NotImplementedError
    out = {}
    for lst in lists:
        for rank, item in enumerate(lst, 1):
            out[item] = out.get(item, 0) + 1 / (k + rank)
    return out


b_ids = [ret.chunks[i].id for i, _ in ret.bm25_rank(q1)[:20]]
v_ids = [ret.chunks[i].id for i, _ in ret.vector_rank(q1)[:20]]
fused = my_rrf([b_ids, v_ids])
for cid in sorted(fused, key=lambda x: -fused[x])[:5]:
    print(f"{cid:22s} rrf={fused[cid]:.5f}  bm25 rank={b_ids.index(cid) + 1 if cid in b_ids else '-'}  vector rank={v_ids.index(cid) + 1 if cid in v_ids else '-'}")

# %% [markdown]
# A **reranker** (a cross-encoder) reads the question and one clause *together* and scores the pair. It is too slow
# for all 247 chunks, so it only re-orders the fused top 20. Its score is a logit: 0 is even odds.

# %%
pd.DataFrame([{"rank": r + 1, "chunk": h.chunk.id, "rerank": h.score, "bm25 rank": h.why["bm25_rank"],
               "vector rank": h.why["vec_rank"]} for r, h in enumerate(ret.search(q1, k=6))])

# %% [markdown]
# ## 7. The RAG prompt, and Kavita's question
# Now Kavita's own question. Search with her words first:

# %%
ps = l3.policy_search("KJOSHI", route_facts=False)
raw = ps.search(SHAKTI)
print("clauses found:", [c["cite"] for c in raw["clauses"]], "·", raw["note"])
print([(h.chunk.id, h.score) for h in ret.search(SHAKTI, k=4)])

# %% [markdown]
# Nothing clears the bar. Her words are *gaskets, Shakti Seals, quote*; the rule's words are *food, certificate*.
# Retrieval finds text that looks like the question, so the **search query** matters. Let the model write the queries:
# one short query per rule the answer could depend on, with one line of company context ("Rasoi makes pressure
# cookers, so many of the parts it buys touch food").

# %%
print(l3.REWRITE_SYSTEM, "\n")
rw = l3.rewrite_queries(SHAKTI, llm)
hits = l3.multi_search(ps, rw["queries"])
for q, found in hits["per_query"].items():
    print(f"{q!r:60s} → {found}")
print()
for c in hits["clauses"]:
    print(f"  {c['cite']:22s} score {c['score']:>6}  {c['text'][:90]}")

# %% [markdown]
# ### Exercise 5: assemble the RAG prompt
# Put each clause in the prompt with its citation first, then the question. The answer instructions
# (`R.ANSWER_SYSTEM`) tell the model to use only the extracts and to cite every rule as `[DOC-ID §section]`.

# %%
def my_prompt(question, clauses):
    # TODO (exercise 5): return the messages list: a system message, then one user message with EXTRACTS and QUESTION
    if not SOLUTION:
        raise NotImplementedError
    extracts = "\n\n".join(f"[{c['cite']}] {c['document']}, effective {c['effective']} › {c['heading']}\n"
                           + ("" if c["status"] == "in force" else f"STATUS: {c['status']}\n") + c["text"] for c in clauses)
    return [{"role": "system", "content": R.ANSWER_SYSTEM},
            {"role": "user", "content": f"EXTRACTS:\n{extracts}\n\nQUESTION: {question}"}]


msgs = my_prompt(SHAKTI, hits["clauses"])
print("same as the library's prompt:", msgs == l3.rag_prompt(SHAKTI, hits["clauses"]))
print(msgs[1]["content"])

# %%
r = llm.chat(l3.rag_prompt(SHAKTI, hits["clauses"]))
answer = r.content
print(f"{r.tokens_in:,} tokens in (vs {full['tokens_in']:,} for the whole corpus) · ₹{r.cost_inr:.4f}\n")
print(answer)

# %% [markdown]
# ## 8. Checking citations
# Because a chunk's id is its citation, a citation is a key we can look up. Two checks: **does the clause exist?** and
# **was it in front of the model?** (a real clause the model never received is a lucky guess).
#
# ### Exercise 6: the citation checker

# %%
def my_check(answer, context_ids, corpus_ids):
    # TODO (exercise 6): find every [DOC-ID §n.n] and sort it into invented / ungrounded / grounded
    if not SOLUTION:
        raise NotImplementedError
    cites = list(dict.fromkeys(f"{d} §{s}" for d, s in re.findall(r"((?:POL|MAN|AMD|HR)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*§\s*(\d+(?:\.\d+)?)", answer)))
    return {"cites": cites, "invented": [c for c in cites if c not in corpus_ids],
            "ungrounded": [c for c in cites if c in corpus_ids and c not in context_ids],
            "grounded": [c for c in cites if c in context_ids]}


ALL = R.corpus_ids()
ctx = [c["cite"] for c in hits["clauses"]]
print("real answer   :", my_check(answer, ctx, ALL))
print("edited to §6.9:", my_check(answer.replace("§6.2", "§6.9"), ctx, ALL), " ← we changed the text by hand")

# %% [markdown]
# ## 9. Evaluate on a few questions
# The deck's experiment ran all 40 questions (20 policy, 8 manual, 5 freshness, 2 permission, 5 traps) against four
# systems. Here are six, with RAG and with the model alone, graded by code: facts by regex, citations by clause id.

# %%
CLOSED = """You answer questions from purchase staff at Rasoi Steel Works, Pune, a pressure-cooker maker that runs Bahi ERP 7.2.
Today is 26 October 2026.
- Begin with the direct answer in one sentence (start with Yes or No when the question is yes/no).
- Cite the company rule you rely on as [DOC-ID §section] when you can.
- If you do not know, begin your reply with NOT IN DOCUMENTS.
- At most four sentences."""
eval_llm = LLM(MODEL, cassette="L3v3_eval", max_tokens=4096)   # the deck's 40-question run
rows = []
for qid in ["P01", "P13", "M01", "F01", "H01", "T01"]:
    q = next(x for x in QUESTIONS if x["id"] == qid)
    res = ps.search(q["q"])
    ctx = R.build_context(res["clauses"]) if res["clauses"] else f"(no extracts) {res['note']}"
    ra = R.answer_with(eval_llm, q["q"], ctx)["answer"]
    ca = eval_llm.chat([{"role": "system", "content": CLOSED}, {"role": "user", "content": q["q"]}]).content or ""
    ids = [c["cite"] for c in res["clauses"]]
    g_rag, g_closed = grade(q, ra, R.extract_citations(ra)), grade(q, ca, R.extract_citations(ca))
    rows.append({"id": qid, "kind": q["kind"], "gold in top 4": (any(i in q["gold"] for i in ids) if q["gold"] else "-"),
                 "RAG correct": g_rag["correct"], "model alone correct": g_closed["correct"], "RAG answer": ra[:90]})
pd.DataFrame(rows)

# %% [markdown]
# ## 10. Ask Rasoi gains its piece: `search_policy`
# Everything above sits behind one tool in Ask Rasoi's toolbox, `bahi/toolbox/search_policy/`: a `tool.json` that tells
# the model what the tool does, and a `tool.py` that runs it as the signed-in user. (Lecture 4 shows exactly how a model
# calls a tool. Today, watch it happen.)

# %%
from bahi.toolbox import SPECS, Toolbox
from bahi.erp.engine import ERP
spec = SPECS["search_policy"]
print(json.dumps({k: spec.spec[k] for k in ("name", "description", "input_schema")}, indent=1, ensure_ascii=False))
print(spec.source)

# %%
agent = l3.knowledge_agent(ERP(), LLM(MODEL, cassette="L3v3_knowledge", max_tokens=4096))
print("SYSTEM:", agent.messages[0]["content"], "\n")
reply = agent.respond(SHAKTI)
for t in agent.trace:
    found = [c["cite"] for c in json.loads(t["result"]).get("clauses", [])]
    print(f"search_policy({t['args']['question']!r}) → {found}")
print("\nASK RASOI (knowledge):", reply)
print("\ncitations:", R.check_citations(reply, [c for t in agent.trace for c in [x["cite"] for x in json.loads(t["result"]).get("clauses", [])]], ALL))

# %% [markdown]
# ## 11. Your module: start A3
# Every module kit ships its own documents in `bahi/modules/<kit>/docs/`, with the same front-matter. The retriever
# takes any list of documents. Their audiences differ from purchasing's, so pass the clearance yourself (A3 asks you to
# map each audience to a role properly).

# %%
KIT = "fin_payables"                                   # change to your kit
kit_docs = R.load_corpus(R.PKG / "modules" / KIT / "docs")
kit_ret = l3.retriever(None, docs=kit_docs, permissions=False)
print(len(kit_docs), "documents ·", len(kit_ret.chunks), "chunks")
for h in kit_ret.search("Who may release a price hold on an invoice?", k=3):
    print(f"  {h.chunk.id:20s} {h.score:>7}  {h.chunk.text[:90]}")

# %% [markdown]
# **Next:** A3 asks for this retrieval over your kit's documents, a `search_<kit>_policy` tool, and a 12-question
# eval graded by code. Lecture 4 gives Ask Rasoi its hands: the toolbox over MCP.
