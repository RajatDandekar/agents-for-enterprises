"""Lecture 2: the manual. Job 4 of the form, explaining the rules, done by retrieval with citations.

    from bahi.agent.retrieval import PolicySearch, ToolBelt, search_policy
    search_policy("Can we buy gaskets from a supplier without a food-grade certificate?", user="KJOSHI")
    # -> {"ok": True, "answer_in_documents": True, "clauses": [{"cite": "POL-PUR-001 §6.2", ...}], "note": ...}

    tools = ToolBelt(IntentTools(erp.session("KJOSHI")), PolicySearch("KJOSHI"))   # .schemas() / .call(name, args)
    agent = ToolLoopAgent(erp, "KJOSHI", llm=llm, tools=tools, system=POLICY_AGENT_SYSTEM)

What is in here, in the order Lecture 2 teaches it:
  1. Corpus      docs/*.md with front-matter (doc_id, version, effective, audience, amends)
  2. Chunking    by section, with the heading path in every chunk; a fixed-size chunker to compare
  3. BM25        keyword search, written out in full
  4. Embeddings  BAAI/bge-small-en-v1.5 on CPU via fastembed (no key; cached, rounded vectors so replay is exact)
  5. Hybrid      reciprocal-rank fusion of BM25 and embeddings, then a cross-encoder reranker
  6. Citations   every chunk's id IS its citation ("POL-PUR-001 §6.2"); check_citations() verifies them
  7. Permissions the user's role decides which documents are indexed for them (filter before ranking)
  8. Freshness   amendments in force replace the clauses they amend; future ones are labelled with their date
  9. LLM Wiki    compile the documents once (LLM, recorded) into linked pages + an index; answer by reading pages
 10. The tool    search_policy(question): clauses with citations, or a plain "not in the documents"

Why a local embedding model: it needs no key, runs on free Colab's CPU, and returns the same vectors every run.
Vectors and reranker scores are cached (docs/_index/*.jsonl), rounded, so a notebook in replay mode ranks exactly
as our recorded run did and the prompts it builds match the recorded cassettes.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
from collections import Counter
from dataclasses import dataclass, field

from ..erp.seed import TODAY, USERS
from ..llm import LLM, tool_schema

PKG = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR = PKG / "docs"
INDEX_DIR = DOCS_DIR / "_index"
WIKI_DIR = PKG / "wiki"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"
TAU = 0.0  # reranker logit below which a clause is dropped: 0 is the cross-encoder's even-odds line. In our run
#            (lectures/L2-the-manual/experiments/logs/retrieval_eval.json) every answerable question's best clause scored
#            above 1.6, but 5 of 7 unanswerable ones also scored above 0: a score alone cannot say "not in the documents".


def _writable() -> bool:
    return os.environ.get("BAHI_LLM_MODE", "auto").lower() != "replay"


def _h(*parts) -> str:
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:24]


# =============================================================================== 1. corpus
@dataclass
class Doc:
    doc_id: str
    title: str
    version: str
    effective: str
    audience: str
    amends: list[str]
    body: str
    path: str = ""

    @property
    def is_amendment(self) -> bool:
        return bool(self.amends)


def parse_front_matter(text: str) -> tuple[dict, str]:
    meta = {}
    if text.startswith("---"):
        head, body = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        return meta, body.lstrip("\n")
    return meta, text


def load_corpus(path: str | pathlib.Path = DOCS_DIR, include_amendments: bool = True) -> list[Doc]:
    docs = []
    for p in sorted(pathlib.Path(path).glob("*.md")):
        meta, body = parse_front_matter(p.read_text())
        if "doc_id" not in meta:
            continue
        d = Doc(meta["doc_id"], meta.get("title", p.stem), meta.get("version", ""), meta.get("effective", ""),
                meta.get("audience", "all Bahi users"),
                [a.strip() for a in meta.get("amends", "").split(",") if a.strip()], body, str(p))
        if include_amendments or not d.is_amendment:
            docs.append(d)
    return docs


# =============================================================================== 2. chunking
@dataclass
class Chunk:
    doc_id: str
    section: str | None      # "6.2"; None for a fixed-size window
    heading: str             # "6. Supplier qualification"
    text: str
    doc_title: str
    version: str
    effective: str
    audience: str
    status: str = "in force"  # or "replaced by AMD-… §1.1 from …", "not yet in force (from …)"
    replaced: bool = False    # True when an amendment in force has replaced this clause
    span: tuple = ()          # (start_word, end_word) for fixed-size windows

    @property
    def id(self) -> str:
        return f"{self.doc_id} §{self.section}" if self.section else f"{self.doc_id} w{self.span[0]}-{self.span[1]}"

    @property
    def context_text(self) -> str:
        """What gets indexed: the heading path travels with the clause, so '6.2' is never an orphan."""
        return f"{self.doc_title} › {self.heading}\n{self.text}"

    def render(self) -> str:
        """What goes into the context window: the citation first, then where it sits, its status, the words."""
        st = "" if self.status == "in force" else f"STATUS: {self.status}\n"
        return f"[{self.id}] {self.doc_title} v{self.version}, effective {self.effective} › {self.heading}\n{st}{self.text}"


H2 = re.compile(r"^##\s+(\d+)\.\s+(.*)$")
H3 = re.compile(r"^###\s+(\d+\.\d+)\s+(.*)$")
CLAUSE = re.compile(r"^(\d+\.\d+)\s+\S")


def chunk_by_section(doc: Doc) -> list[Chunk]:
    """One chunk per numbered clause (policies) or per ### section (manuals), each carrying its heading."""
    out: list[Chunk] = []
    h2 = ("", "")
    cur = None

    def flush():
        if cur and "\n".join(cur["lines"]).strip():
            out.append(Chunk(doc.doc_id, cur["section"], cur["heading"], "\n".join(cur["lines"]).strip(),
                             doc.title, doc.version, doc.effective, doc.audience))

    for line in doc.body.splitlines():
        if line.startswith("# "):
            continue
        m = H2.match(line)
        if m:
            flush()
            h2 = (m[1], m[2].strip())
            cur = {"section": m[1], "heading": f"{m[1]}. {m[2].strip()}", "lines": []}
            continue
        m = H3.match(line)
        if m:
            flush()
            cur = {"section": m[1], "heading": f"{h2[0]}. {h2[1]} › {m[1]} {m[2].strip()}", "lines": []}
            continue
        m = CLAUSE.match(line)
        if m and h2[0] and m[1].split(".")[0] == h2[0]:
            flush()
            cur = {"section": m[1], "heading": f"{h2[0]}. {h2[1]}", "lines": [line]}
            continue
        if cur is not None:
            cur["lines"].append(line)
    flush()
    return out


def chunk_fixed(doc: Doc, size: int = 120, overlap: int = 20) -> list[Chunk]:
    """The naive way: windows of `size` words, sliding by size-overlap, blind to headings and clauses."""
    words = doc.body.split()
    out, i, step = [], 0, max(1, size - overlap)
    while i < len(words):
        j = min(len(words), i + size)
        out.append(Chunk(doc.doc_id, None, "", " ".join(words[i:j]), doc.title, doc.version, doc.effective,
                         doc.audience, span=(i, j)))
        if j == len(words):
            break
        i += step
    return out


# =============================================================================== 7 + 8. permissions and freshness
AUDIENCE = {"all bahi users": "all-staff", "all purchase staff": "purchase", "hr only": "hr"}
ROLE_CLEARANCE = {
    "PUR-EXEC": {"all-staff", "purchase"}, "PUR-SR": {"all-staff", "purchase"}, "PUR-MGR": {"all-staff", "purchase"},
    "PLANT-HEAD": {"all-staff", "purchase"}, "STORES": {"all-staff"}, "HR": {"all-staff", "hr"},
    "SYS-ADMIN": {"all-staff"},
}


def audience_tag(audience: str) -> str:
    return AUDIENCE.get(audience.lower().strip(), "restricted")


def clearance_for(user: str | None = None, role: str | None = None) -> set[str]:
    """What a user may read. Comes from their role in Bahi; an unknown user gets only what all staff may read."""
    if role is None and user:
        role = next((u[2] for u in USERS if u[0] == user.upper()), None)
    return set(ROLE_CLEARANCE.get(role or "", {"all-staff"}))


def allowed(c: Chunk | Doc, clearance: set[str]) -> bool:
    return audience_tag(c.audience) in clearance


def apply_freshness(chunks: list[Chunk], docs: list[Doc], as_of: str = TODAY) -> list[Chunk]:
    """Amendments in force replace the clauses they amend; amendments not yet in force are labelled with their date."""
    by_id = {c.id: c for c in chunks}
    for d in docs:
        if not d.is_amendment:
            continue
        mine = [c for c in chunks if c.doc_id == d.doc_id]
        live = d.effective <= as_of
        for c in mine:
            c.status = "in force" if live else f"not yet in force: applies from {d.effective}"
        new_rule = next((c.id for c in mine if c.section == "1.1"), d.doc_id)
        for target in d.amends:
            base = by_id.get(target.replace("  ", " "))
            if not base:
                continue
            if live:
                base.replaced = True
                base.status = f"replaced from {d.effective} by {new_rule}; do not apply this text"
            else:
                import datetime as _dt
                eve = (_dt.date.fromisoformat(d.effective) - _dt.timedelta(days=1)).isoformat()
                base.status = f"in force until {eve}; replaced from {d.effective} by {new_rule}"
    return chunks


# =============================================================================== 3. BM25
STOP = set("a an the of to and or in on for is are be by with from at as it its this that these those any each "
           "we our you your i do does can may what which who how when there their them he she his her was were "
           "has have had if than then so".split())


def stem(t: str) -> str:
    if t.isalpha() and len(t) > 4:
        if t.endswith("ies"):
            return t[:-3] + "y"
        if t.endswith("s") and not t.endswith("ss"):
            return t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    """Lower-case words; codes like ERR-PO-0412, GSK-SIL-05L and section numbers like 6.2 survive whole."""
    out = []
    for t in re.findall(r"[a-z0-9₹]+(?:[.\-/][a-z0-9]+)*", text.lower()):
        if t in STOP:
            continue
        out.append(stem(t))
        if "-" in t or "/" in t:
            out.extend(stem(p) for p in re.split(r"[-/]", t) if len(p) > 1 and p not in STOP)
    return out


class BM25:
    """score(q, d) = Σ_t idf(t) · tf(t,d)·(k1+1) / (tf(t,d) + k1·(1 − b + b·|d|/avgdl))"""

    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.N = len(docs)
        self.dl = [len(d) for d in docs]
        self.avgdl = sum(self.dl) / max(1, self.N)
        self.tf = [Counter(d) for d in docs]
        df = Counter(t for d in docs for t in set(d))
        self.idf = {t: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for t, n in df.items()}

    def term_scores(self, q: list[str], i: int) -> dict:
        out = {}
        for t in q:
            f = self.tf[i].get(t, 0)
            if f:
                out[t] = out.get(t, 0) + self.idf[t] * f * (self.k1 + 1) / (
                    f + self.k1 * (1 - self.b + self.b * self.dl[i] / self.avgdl))
        return out

    def scores(self, q: list[str]) -> list[float]:
        return [sum(self.term_scores(q, i).values()) for i in range(self.N)]


# =============================================================================== 4. embeddings
class _JsonlCache:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.d = {}
        if path.exists():
            for line in path.open():
                if line.strip():
                    r = json.loads(line)
                    self.d[r["k"]] = r["v"]

    def get(self, k):
        return self.d.get(k)

    def put(self, k, v):
        self.d[k] = v
        if _writable():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as f:
                f.write(json.dumps({"k": k, "v": v}) + "\n")


class Embedder:
    """bge-small-en-v1.5: 384 numbers per text. Queries get bge's search prefix (fastembed's query_embed)."""

    def __init__(self, model: str = EMBED_MODEL, cache: pathlib.Path = INDEX_DIR / "embeddings.jsonl"):
        self.model_name, self.cache, self._m = model, _JsonlCache(cache), None
        self.computed = 0

    def _model(self):
        if self._m is None:
            from fastembed import TextEmbedding
            self._m = TextEmbedding(self.model_name)
        return self._m

    def embed(self, texts: list[str], kind: str = "passage") -> list[list[float]]:
        keys = [_h(self.model_name, kind, t) for t in texts]
        miss = [i for i, k in enumerate(keys) if self.cache.get(k) is None]
        if miss:
            m = self._model()
            todo = [texts[i] for i in miss]
            vecs = list(m.query_embed(todo)) if kind == "query" else list(m.passage_embed(todo))
            for i, v in zip(miss, vecs):
                self.cache.put(keys[i], [round(float(x), 5) for x in v])
            self.computed += len(miss)
        return [self.cache.get(k) for k in keys]


def cosine(a, b) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb + 1e-12)


class Reranker:
    """A cross-encoder reads the question and the clause together and scores the pair (ms-marco MiniLM, CPU)."""

    def __init__(self, model: str = RERANK_MODEL, cache: pathlib.Path = INDEX_DIR / "rerank.jsonl"):
        self.model_name, self.cache, self._m = model, _JsonlCache(cache), None

    def score(self, query: str, texts: list[str]) -> list[float]:
        keys = [_h(self.model_name, query, t) for t in texts]
        miss = [i for i, k in enumerate(keys) if self.cache.get(k) is None]
        if miss:
            if self._m is None:
                from fastembed.rerank.cross_encoder import TextCrossEncoder
                self._m = TextCrossEncoder(self.model_name)
            for i, s in zip(miss, self._m.rerank(query, [texts[i] for i in miss])):
                self.cache.put(keys[i], round(float(s), 4))
        return [self.cache.get(k) for k in keys]


# =============================================================================== 5. the index and hybrid search
def rrf(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    """Reciprocal rank fusion: each list votes 1/(k + rank) for each item. Ranks, not raw scores, so units don't matter."""
    out: dict[int, float] = {}
    for r in rankings:
        for rank, i in enumerate(r, 1):
            out[i] = out.get(i, 0.0) + 1.0 / (k + rank)
    return out


@dataclass
class Hit:
    chunk: Chunk
    score: float
    why: dict = field(default_factory=dict)

    def as_clause(self) -> dict:
        c = self.chunk
        return {"cite": c.id, "document": f"{c.doc_title} v{c.version}", "effective": c.effective,
                "status": c.status, "heading": c.heading, "text": c.text, "score": round(self.score, 2)}


class Retriever:
    """Everything a user may read, indexed for that user, as of a date. search() = BM25 + embeddings → RRF → rerank."""

    def __init__(self, user: str | None = "KJOSHI", as_of: str = TODAY, clearance: set[str] | None = None,
                 docs: list[Doc] | None = None, permissions: bool = True, freshness: bool = True,
                 embedder: Embedder | None = None, reranker: Reranker | None = None):
        self.user, self.as_of = user, as_of
        self.clearance = clearance if clearance is not None else clearance_for(user)
        self.docs = docs if docs is not None else load_corpus()
        chunks = [c for d in self.docs for c in chunk_by_section(d)]
        if freshness:
            apply_freshness(chunks, self.docs, as_of)
        if permissions:  # filter BEFORE ranking: what she may not read is not in her index at all
            chunks = [c for c in chunks if allowed(c, self.clearance)]
        if freshness:
            chunks = [c for c in chunks if not c.replaced]
        self.chunks = chunks
        self.bm25 = BM25([tokenize(c.context_text) for c in chunks])
        self.embedder = embedder or Embedder()
        self.reranker = reranker or Reranker()
        self.vecs = self.embedder.embed([c.context_text for c in chunks])

    # --- the three rankings
    def bm25_rank(self, q: str) -> list[tuple[int, float]]:
        s = self.bm25.scores(tokenize(q))
        return sorted(((i, v) for i, v in enumerate(s) if v > 0), key=lambda x: -x[1])

    def vector_rank(self, q: str) -> list[tuple[int, float]]:
        qv = self.embedder.embed([q], kind="query")[0]
        return sorted(((i, cosine(qv, v)) for i, v in enumerate(self.vecs)), key=lambda x: -x[1])

    def search(self, q: str, k: int = 5, mode: str = "hybrid+rerank", pool: int = 20) -> list[Hit]:
        b = self.bm25_rank(q)
        if mode == "bm25":
            return [Hit(self.chunks[i], s, {"bm25": round(s, 3)}) for i, s in b[:k]]
        v = self.vector_rank(q)
        if mode == "vector":
            return [Hit(self.chunks[i], s, {"cos": round(s, 4)}) for i, s in v[:k]]
        fused = rrf([[i for i, _ in b[:pool]], [i for i, _ in v[:pool]]])
        brank = {i: r for r, (i, _) in enumerate(b, 1)}
        vrank = {i: r for r, (i, _) in enumerate(v, 1)}
        cand = sorted(fused, key=lambda i: -fused[i])[:pool]
        if mode == "hybrid":
            return [Hit(self.chunks[i], fused[i], {"rrf": round(fused[i], 5), "bm25_rank": brank.get(i),
                                                   "vec_rank": vrank.get(i)}) for i in cand[:k]]
        rs = self.reranker.score(q, [self.chunks[i].context_text for i in cand])
        order = sorted(range(len(cand)), key=lambda j: -rs[j])
        return [Hit(self.chunks[cand[j]], rs[j], {"rerank": rs[j], "rrf": round(fused[cand[j]], 5),
                                                  "bm25_rank": brank.get(cand[j]), "vec_rank": vrank.get(cand[j])})
                for j in order[:k]]


# =============================================================================== 6. citations
CITE = re.compile(r"((?:POL|MAN|AMD|HR)-[A-Z0-9]+(?:-[A-Z0-9]+)*)\s*§\s*(\d+(?:\.\d+)?)")


def extract_citations(text: str) -> list[str]:
    seen = []
    for d, s in CITE.findall(text or ""):
        c = f"{d} §{s}"
        if c not in seen:
            seen.append(c)
    return seen


def check_citations(answer: str, context_ids: list[str], corpus_ids: set[str]) -> dict:
    """A citation is checkable: does the clause exist, and was it actually in front of the model?"""
    cites = extract_citations(answer)
    return {"cites": cites, "exist": [c for c in cites if c in corpus_ids],
            "invented": [c for c in cites if c not in corpus_ids],
            "grounded": [c for c in cites if c in context_ids],
            "ungrounded": [c for c in cites if c in corpus_ids and c not in context_ids]}


def corpus_ids(docs: list[Doc] | None = None) -> set[str]:
    return {c.id for d in (docs or load_corpus()) for c in chunk_by_section(d)}


# =============================================================================== documents vs the ERP
ERP_FACTS = [  # questions about live facts: the answer is in Bahi, never in a document
    (re.compile(r"\bhow many\b|\bin stock\b|\bon hand\b|\bdays of cover\b", re.I), "stock_position"),
    (re.compile(r"\bbudget\b.*\b(left|remaining|available)\b|\bhow much budget\b", re.I), "check_cost_centre"),
    (re.compile(r"\b(PO|PR)/\d{4}/\d{5}\b", re.I), "order_status"),
    (re.compile(r"\bdid we pay\b|\bwe (last )?paid\b", re.I), "last_purchase"),  # v1 also matched "the rate from the
    #   last order", which flagged rule question P11 (logs/rag_vs_wiki.json router); v2 drops it (logs/scenarios_l2.json)
    (re.compile(r"\bright now\b|\bat the moment\b", re.I), "find_supplier"),
]


def erp_fact(question: str) -> str | None:
    for pat, tool_name in ERP_FACTS:
        if pat.search(question):
            return tool_name
    return None


# =============================================================================== 10. the tool
SEARCH_POLICY = tool_schema(
    "search_policy",
    "Search Rasoi Steel Works' purchasing rules: the Purchase Policy, Supplier Policy, Approval Matrix, their "
    "amendments, and the Bahi ERP user manual (screens, fields, error codes). Returns the clauses that answer the "
    "question, each with a citation such as 'POL-PUR-001 §6.2' to quote in your reply. Use it for RULES: may we, "
    "who approves, what does an error mean, how does a screen work. It does NOT hold live facts (stock, budgets, "
    "document statuses, prices paid, a supplier's certificate today); use the ERP tools for those. If it says "
    "answer_in_documents=false, tell the user the documents do not say; do not guess.",
    {"question": {"type": "string", "description": "the rule question, in plain words"}}, ["question"])


class PolicySearch:
    """The search_policy tool, bound to one user and one date. Plugs into any agent that takes schemas()/call()."""

    names = ["search_policy"]

    def __init__(self, user: str = "KJOSHI", as_of: str = TODAY, k: int = 4, retriever: Retriever | None = None,
                 tau: float = TAU, route_facts: bool = True):
        self.user, self.as_of, self.k, self.tau, self.route_facts = user, as_of, k, tau, route_facts
        self.r = retriever or Retriever(user, as_of)

    def search(self, question: str) -> dict:
        fact = erp_fact(question) if self.route_facts else None
        if fact:
            return {"ok": True, "answer_in_documents": False, "clauses": [],
                    "note": f"This asks for a live fact, which lives in Bahi, not in any document. Use the ERP tool "
                            f"{fact}.", "use_erp_tool": fact}
        hits = [h for h in self.r.search(question, k=self.k) if h.score >= self.tau]
        if not hits:
            return {"ok": True, "answer_in_documents": False, "clauses": [],
                    "note": "No clause in the documents you may read answers this. Say so plainly; do not guess."}
        return {"ok": True, "answer_in_documents": True, "clauses": [h.as_clause() for h in hits],
                "note": "Quote the rule with its citation, e.g. (POL-PUR-001 §6.2). If a clause's status says it is "
                        "replaced or not yet in force, follow the status. Stock, budgets and statuses come from Bahi."}

    def schemas(self) -> list[dict]:
        return [SEARCH_POLICY]

    def call(self, name: str, args: dict) -> dict:
        if name != "search_policy":
            return {"ok": False, "error": f"Unknown tool {name}."}
        q = args.get("question") or args.get("query") or ""
        if not q.strip():
            return {"ok": False, "error": "Empty question.", "next_step": "Ask search_policy a question in words."}
        return self.search(q)


def search_policy(question: str, user: str = "KJOSHI", as_of: str = TODAY) -> dict:
    """Function form, for a graph node (Lecture 4): one call, one dict. The index is built once per (user, date)."""
    key = (user, as_of)
    if key not in _PS:
        _PS[key] = PolicySearch(user, as_of)
    return _PS[key].search(question)


_PS: dict = {}


class ToolBelt:
    """Several tool sets as one: schemas() concatenates, call() dispatches by tool name."""

    def __init__(self, *toolsets):
        self.sets = toolsets
        self.names = [n for s in toolsets for n in getattr(s, "names", [])]

    def schemas(self) -> list[dict]:
        return [sc for s in self.sets for sc in s.schemas()]

    def call(self, name: str, args: dict) -> dict:
        for s in self.sets:
            if name in getattr(s, "names", []):
                return s.call(name, args)
        return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}


POLICY_AGENT_SYSTEM = """You are the purchasing assistant at Rasoi Steel Works, Pune, working inside Bahi ERP for {name} ({user_id}).
Today is Monday 26 October 2026. Use the tools to do what {first} asks. Preview every order and get {first}'s
confirmation before committing it. Report the status the receipt gives you, in plain words.
For any question about a rule (may we, must we, who approves, what an error means), call search_policy first and
quote the clause with its citation, for example (Purchase Policy POL-PUR-001 §6.2). Never state a rule from memory.
Stock, budgets, rates and statuses come from the ERP tools, never from a document."""


def make_policy_agent(llm: LLM):
    """make_agent(erp, user) for run_scenario: the Lecture 3 tool loop + intent tools + search_policy."""
    from .loop import ToolLoopAgent
    from .tools import IntentTools

    def make(erp, user):
        return ToolLoopAgent(erp, user, llm=llm, tools=ToolBelt(IntentTools(erp.session(user)), PolicySearch(user)),
                             system=POLICY_AGENT_SYSTEM)
    return make


# =============================================================================== answering (RAG)
ANSWER_SYSTEM = """You answer questions from purchase staff at Rasoi Steel Works, Pune. Today is 26 October 2026.
Use ONLY the document extracts given to you; never your own knowledge.
- Begin with the direct answer in one sentence (start with Yes or No when the question is yes/no).
- Cite every rule you use as [DOC-ID §section], exactly as printed on the extract, e.g. [POL-PUR-001 §6.2].
- If an extract's STATUS says it was replaced, follow the amendment. If a rule is not yet in force, say from when it applies.
- Documents explain rules. They never hold live facts: stock, budget left, a document's status, the rate we last paid,
  or whether a named supplier's certificate is valid today. Those live in Bahi ERP.
- If the extracts do not contain the answer, begin your reply with NOT IN DOCUMENTS and say where the answer lives.
- At most four sentences."""


def build_context(clauses: list[dict] | list[Chunk]) -> str:
    parts = []
    for c in clauses:
        if isinstance(c, Chunk):
            parts.append(c.render())
        else:
            st = "" if c["status"] == "in force" else f"STATUS: {c['status']}\n"
            parts.append(f"[{c['cite']}] {c['document']}, effective {c['effective']} › {c['heading']}\n{st}{c['text']}")
    return "\n\n".join(parts) if parts else "(no extracts: the documents you may read do not cover this)"


def answer_with(llm: LLM, question: str, context: str, system: str = ANSWER_SYSTEM) -> dict:
    r = llm.chat([{"role": "system", "content": system},
                  {"role": "user", "content": f"EXTRACTS:\n{context}\n\nQUESTION: {question}"}])
    return {"answer": r.content or "", "tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}


def answer_rag(question: str, ps: PolicySearch, llm: LLM) -> dict:
    """RAG: the tool's clauses (or its 'not in the documents' note) become the context for one model call."""
    res = ps.search(question)
    ctx = build_context(res["clauses"]) if res["clauses"] else f"(no extracts) {res['note']}"
    out = answer_with(llm, question, ctx)
    out["context_ids"] = [c["cite"] for c in res["clauses"]]
    out["context"] = ctx
    return out


# =============================================================================== 9. the LLM Wiki
WIKI_PLAN = """You are compiling a company wiki from Rasoi Steel Works' purchasing documents, once, so that nobody needs to
read the sources again. Below is the outline of every section: its citation id, heading and first words.
Propose the wiki's pages: one page per topic a purchase executive would look up (a rule, a process, a screen, a group of
related error codes, a role and its limits).
Return JSON only: {{"pages": [{{"slug": "food-grade-certificates", "title": "Food-grade certificates",
"summary": "one sentence", "sources": ["POL-PUR-001 §6.2", "POL-SUP-003 §4.1"]}}]}}
Rules: {n_min} to {n_max} pages. Every section id in the outline must appear in the sources of at least one page.
A section may feed several pages. Use only ids from the outline. Slugs are lowercase words joined by hyphens.

OUTLINE:
{outline}"""

WIKI_PAGE = """Write one page of the company wiki: "{title}" — {summary}
Use ONLY the source sections below. Write for a purchase executive: plain words, short sentences.
Markdown, in exactly this shape:
# {title}
A summary paragraph of two or three sentences.
## Rules
- one bullet per rule or step, each ending with its citation in square brackets exactly as given, e.g. [POL-PUR-001 §6.2]
## Watch out
- exceptions and traps, cited the same way (leave this section out if there are none)
## Related
- [[slug]] links to pages in this list that genuinely relate: {others}
If a source's STATUS says it is replaced, write only the current rule and note the change, citing both. If a rule is not
yet in force, give the date it applies from. Keep worked examples as examples; never present them as live figures.

SOURCES:
{sources}"""

WIKI_PICK = """Below is the index of the company wiki. Which pages (at most 3) should be read to answer the question?
Reply with JSON only: {{"pages": ["slug", ...]}}. Reply {{"pages": []}} if no page could hold the answer
(for example a live figure such as stock or a budget, which lives in the ERP).

INDEX:
{index}

QUESTION: {question}"""


def _json(text: str) -> dict:
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    m = re.search(r"\{.*\}", t, re.S)
    return json.loads(m.group(0) if m else t)


def outline(chunks: list[Chunk]) -> str:
    lines = []
    for c in chunks:
        first = " ".join(re.sub(r"^\d+\.\d+\s+", "", c.text).split()[:14])
        lines.append(f"{c.id} | {c.doc_title} › {c.heading} | {first}")
    return "\n".join(lines)


LINK = re.compile(r"\[\[([a-z0-9-]+)\]\]")


class Wiki:
    """Karpathy's LLM-Wiki pattern: compile the documents once into linked pages and an index; answer by reading pages.

    compile(): plan the pages (one LLM call per audience), write each page (one call each), build index.md by code,
    then lint by code (every citation exists, every link resolves). update(amendment): recompile only the pages
    whose sources the amendment touches. answer(): read the index, pick pages (one call), answer from them (one call).
    """

    def __init__(self, root: pathlib.Path | str = WIKI_DIR, chat_kw: dict | None = None):
        self.chat_kw = chat_kw if chat_kw is not None else {"reasoning_effort": "low"}  # compile: little thinking needed
        self.root = pathlib.Path(root)
        self.pages_dir = self.root / "pages"
        self.manifest_path = self.root / "manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {"pages": {}}

    # ---------------------------------------------------------------- compile
    def compile(self, docs: list[Doc], llm: LLM, n_range=(16, 26)) -> dict:
        chunks = [c for d in docs for c in chunk_by_section(d)]
        apply_freshness(chunks, docs)
        report = {"plan_calls": [], "pages": {}}
        groups: dict[str, list[Chunk]] = {}
        for c in chunks:
            groups.setdefault(audience_tag(c.audience) if audience_tag(c.audience) == "hr" else "staff", []).append(c)
        plan = []
        for grp, cs in groups.items():
            if grp == "hr":  # a restricted audience gets its own pages, compiled from its own sources only
                d = next(x for x in docs if x.doc_id == cs[0].doc_id)
                plan.append({"slug": "salary-bands", "title": d.title, "summary": "HR's confidential pay bands.",
                             "sources": [c.id for c in cs], "audience": d.audience})
                continue
            r = llm.chat([{"role": "user", "content": WIKI_PLAN.format(outline=outline(cs), n_min=n_range[0],
                                                                       n_max=n_range[1])}],
                         response_format={"type": "json_object"}, **self.chat_kw)
            report["plan_calls"].append({"tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds})
            pages = _json(r.content)["pages"]
            ids = {c.id for c in cs}
            for p in pages:
                p["sources"] = [s for s in p["sources"] if s in ids]
                p["audience"] = "all purchase staff" if any(s.split(" §")[0].startswith(("POL", "AMD")) for s in p["sources"]) else "all Bahi users"
            covered = {s for p in pages for s in p["sources"]}
            missing = [c.id for c in cs if c.id not in covered]
            report["uncovered_by_plan"] = missing
            if missing:  # the plan forgot some sections: give them a page rather than lose them
                pages.append({"slug": "other-sections", "title": "Other sections", "summary": "Sections no other page covers.",
                              "sources": missing, "audience": "all purchase staff"})
            plan += pages
        self.manifest = {"compiled_from": [f"{d.doc_id} v{d.version}" for d in docs], "pages": {}}
        for p in plan:
            self._write_page(p, plan, chunks, llm, report)
        self._save()
        report["lint"] = self.lint({c.id for c in chunks})
        return report

    def _write_page(self, p: dict, plan: list[dict], chunks: list[Chunk], llm: LLM, report: dict):
        by_id = {c.id: c for c in chunks}
        src = [by_id[s] for s in p["sources"] if s in by_id]
        hr = p["audience"] == "hr only"
        same_aud = [q for q in plan if q["slug"] != p["slug"] and (q["audience"] == "hr only") == hr]
        others = ", ".join(f"[[{q['slug']}]] {q['title']}" for q in same_aud)
        r = llm.chat([{"role": "user", "content": WIKI_PAGE.format(title=p["title"], summary=p["summary"], others=others,
                                                                   sources="\n\n".join(c.render() for c in src))}],
                     **self.chat_kw)
        body = (r.content or "").strip()
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        (self.pages_dir / f"{p['slug']}.md").write_text(
            f"---\ntitle: {p['title']}\naudience: {p['audience']}\nsources: {', '.join(p['sources'])}\n"
            f"compiled_by: {llm.model}\n---\n\n{body}\n")
        self.manifest["pages"][p["slug"]] = {"title": p["title"], "summary": p["summary"], "audience": p["audience"],
                                             "sources": p["sources"], "tokens_in": r.tokens_in, "tokens_out": r.tokens_out}
        report["pages"][p["slug"]] = {"tokens_in": r.tokens_in, "tokens_out": r.tokens_out, "seconds": r.seconds}

    def update(self, amendment: Doc, docs: list[Doc], llm: LLM) -> dict:
        """Freshness for a wiki: recompile only the pages whose sources the amendment touches."""
        chunks = [c for d in docs for c in chunk_by_section(d)]
        apply_freshness(chunks, docs)
        amd_ids = [c.id for c in chunks if c.doc_id == amendment.doc_id]
        hit = [s for s, p in self.manifest["pages"].items() if any(t in p["sources"] for t in amendment.amends)]
        plan = [{"slug": s, **p} for s, p in self.manifest["pages"].items()]
        report = {"amendment": amendment.doc_id, "pages_recompiled": hit, "pages": {}}
        for p in plan:
            if p["slug"] in hit:
                p["sources"] = p["sources"] + [i for i in amd_ids if i not in p["sources"]]
                self._write_page(p, plan, chunks, llm, report)
        self.manifest.setdefault("amendments", []).append(amendment.doc_id)
        self._save()
        report["lint"] = self.lint({c.id for c in chunks})
        return report

    def _save(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(self.manifest, indent=1, ensure_ascii=False))
        lines = ["# Wiki index", "", "One line per page: [[slug]] title: what it covers (audience).", ""]
        for s, p in self.manifest["pages"].items():
            lines.append(f"- [[{s}]] {p['title']}: {p['summary']} ({p['audience']})")
        (self.root / "index.md").write_text("\n".join(lines) + "\n")

    def lint(self, ids: set[str]) -> dict:
        bad_cites, bad_links, uncited = {}, {}, {}
        for s, p in self.manifest["pages"].items():
            text = self.page(s)
            cites = extract_citations(text)
            bad = [c for c in cites if c not in ids]
            links = [l for l in LINK.findall(text) if l not in self.manifest["pages"]]
            if bad:
                bad_cites[s] = bad
            if links:
                bad_links[s] = links
            miss = [x for x in p["sources"] if x not in cites]
            if miss:
                uncited[s] = miss
        return {"pages": len(self.manifest["pages"]), "invented_citations": bad_cites, "broken_links": bad_links,
                "sources_not_cited": uncited}

    # ---------------------------------------------------------------- read
    def page(self, slug: str) -> str:
        p = self.pages_dir / f"{slug}.md"
        return parse_front_matter(p.read_text())[1] if p.exists() else ""

    def index_for(self, clearance: set[str]) -> str:
        return "\n".join(f"- [[{s}]] {p['title']}: {p['summary']}" for s, p in self.manifest["pages"].items()
                         if audience_tag(p["audience"]) in clearance)

    def answer(self, question: str, llm: LLM, user: str = "KJOSHI", clearance: set[str] | None = None,
               max_pages: int = 3) -> dict:
        clearance = clearance if clearance is not None else clearance_for(user)
        r1 = llm.chat([{"role": "user", "content": WIKI_PICK.format(index=self.index_for(clearance), question=question)}])
        try:
            picked = [s for s in _json(r1.content).get("pages", []) if s in self.manifest["pages"]]
        except (ValueError, json.JSONDecodeError):
            picked = []
        picked = [s for s in picked if audience_tag(self.manifest["pages"][s]["audience"]) in clearance][:max_pages]
        ctx = "\n\n".join(f"(wiki page [[{s}]])\n{self.page(s)}" for s in picked) or \
            "(no wiki page covers this question)"
        out = answer_with(llm, question, ctx)
        out["pages"] = picked
        out["context_ids"] = sorted({c for s in picked for c in extract_citations(self.page(s))})
        out["tokens_in"] += r1.tokens_in
        out["tokens_out"] += r1.tokens_out
        out["seconds"] = round(out["seconds"] + r1.seconds, 3)
        out["context"] = ctx
        return out


# =============================================================================== the context window, counted
_TOK = None

def count_tokens(text: str, model: str = "gemini-3.8-flash", cache: pathlib.Path = INDEX_DIR / "tokens.jsonl") -> int:
    """Exact count from Gemini's countTokens endpoint, cached so replay needs no key. Falls back to len/4."""
    global _TOK
    if _TOK is None or _TOK.path != cache:
        _TOK = _JsonlCache(cache)
    c = _TOK
    k = _h(model, text)
    v = c.get(k)
    if v is not None:
        return v
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return math.ceil(len(text) / 4)
    import httpx
    r = httpx.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens", params={"key": key},
                   json={"contents": [{"parts": [{"text": text}]}]}, timeout=60)
    n = int(r.json()["totalTokens"])
    c.put(k, n)
    return n


def context_budget(messages: list[dict], tools: list[dict], model: str = "gemini-3.8-flash") -> list[dict]:
    """What enters the context window on one model call, part by part, in tokens."""
    rows = []
    for i, m in enumerate(messages):
        if m["role"] == "system":
            part = "system prompt"
        elif m["role"] == "user":
            part = "user message"
        elif m["role"] == "assistant":
            part = "model's earlier tool calls" if m.get("tool_calls") else "model's earlier reply"
        else:
            name = ""
            for prev in messages[:i]:
                for tc in prev.get("tool_calls") or []:
                    if tc["id"] == m.get("tool_call_id"):
                        name = tc["function"]["name"]
            part = f"tool result: {name}"
        text = m.get("content") or ""
        if m.get("tool_calls"):
            text += json.dumps([tc["function"] for tc in m["tool_calls"]])
        rows.append({"part": part, "tokens": count_tokens(text, model)})
    rows.insert(1, {"part": f"tool schemas ({len(tools)} tools)", "tokens": count_tokens(json.dumps(tools), model)})
    merged: dict[str, int] = {}
    for r in rows:
        merged[r["part"]] = merged.get(r["part"], 0) + r["tokens"]
    return [{"part": k, "tokens": v} for k, v in merged.items()]
