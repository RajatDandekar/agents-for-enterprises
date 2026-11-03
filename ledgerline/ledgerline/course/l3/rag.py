"""Lecture 3 v4: RAG over northbridge-docs, every piece the RAG grid and the RAG Lab vary.

    from ledgerline.course.l3 import rag
    hits = rag.rag_search("What does ERR-PO-0412 mean?", user="ECLARKE", k=5)   # the best config: cited chunks
    for h in hits: print(h["cite"], h["score"], h["text"][:80])

    cfg = rag.Config(parser="structured", chunker="structure", size=400, overlap=0.0, embed="bge-small",
                     retrieval="hybrid", rerank=True, rewrite=False, k=5)
    idx = rag.Index.build(chunks, cfg.embed, path="/tmp/idx")    # Chroma (persistent, HNSW cosine) + BM25
    idx = rag.Index.load("/tmp/idx", cfg.embed)
    out = rag.Retriever(idx, cfg).search(question, role="PUR-EXEC")   # {"items": [...], "seconds", "timing": {...}}

The pieces:
    BM25          written out with a sparse matrix (scipy): every chunk's BM25 weight for every term, so a query is
                  one column sum. Codes like ERR-PO-0412 stay whole tokens (and their parts are indexed too).
    Embedder      five open embedding models (EMBED_MODELS) through sentence-transformers, each with its own query
                  and passage prefixes. Vectors are L2-normalised, so cosine = dot product.
    Chroma        one persistent collection per (chunking, embedding model), HNSW with cosine space. Permissions are a
                  `where` filter (confidential = False for anyone outside HR), applied before ranking.
    Hybrid        reciprocal rank fusion (RRF, k=60) of the dense and BM25 lists.
    Reranker      BAAI/bge-reranker-base, a cross-encoder that reads the question and each candidate together.
    Rewriting     one LLM call turns the staff question into a search query (recorded to cassette L3v4_rewrite).

rag_search() loads the best configuration's index from RAG_INDEX_DIR, or fetches it from the RAG Lab
(BEST_INDEX_URL), or builds it from the dump (slow on a CPU) when neither is there.
"""
from __future__ import annotations

import gzip
import json
import math
import os
import pathlib
import re
import shutil
import tarfile
import time
from dataclasses import asdict, dataclass

from . import corpus as C

EMBED_MODELS = {
    "bge-small": {"hf": "BAAI/bge-small-en-v1.5", "dim": 384, "q": "Represent this sentence for searching relevant passages: ", "p": "", "max_len": 512},
    "bge-base": {"hf": "BAAI/bge-base-en-v1.5", "dim": 768, "q": "Represent this sentence for searching relevant passages: ", "p": "", "max_len": 512},
    "e5-small": {"hf": "intfloat/e5-small-v2", "dim": 384, "q": "query: ", "p": "passage: ", "max_len": 512},
    "gte-small": {"hf": "thenlper/gte-small", "dim": 384, "q": "", "p": "", "max_len": 512},
    "nomic": {"hf": "nomic-ai/nomic-embed-text-v1.5", "dim": 768, "q": "search_query: ", "p": "search_document: ", "max_len": 2048,
              "trust_remote_code": True},
}
RERANK_MODEL = "BAAI/bge-reranker-base"
REWRITE_MODEL = "openrouter:google/gemini-3.8-flash"
POOL = 20          # candidates each list contributes to fusion / the reranker
RRF_K = 60
RAG_INDEX_DIR = pathlib.Path(os.environ.get("RAG_INDEX_DIR", C.CACHE_DIR / "rag_index"))
BEST_INDEX_URL = os.environ.get("RAG_BEST_INDEX_URL", "https://rajatworkspace--northbridge-raglab.us-east.modal.run/api/best_index.tar.gz")
BEST_PATH = pathlib.Path(__file__).parent / "rag_best.json"   # written by the grid: the chosen config + its metrics


@dataclass
class Config:
    parser: str = "structured"
    chunker: str = "structure"
    size: int = 400
    overlap: float = 0.0
    embed: str = "bge-small"
    retrieval: str = "hybrid"       # dense | bm25 | hybrid
    rerank: bool = False
    rewrite: bool = False
    k: int = 5

    @property
    def chunking(self) -> str:
        return C.chunking_id(self.parser, self.chunker, self.size, self.overlap)

    @property
    def id(self) -> str:
        e = "-" if self.retrieval == "bm25" else self.embed
        return f"{self.chunking}|{e}|{self.retrieval}|rr{int(self.rerank)}|qr{int(self.rewrite)}|k{self.k}"

    @classmethod
    def from_id(cls, s: str) -> "Config":
        ch, e, r, rr, qr, k = s.split("|")
        p, m, size, o = ch.split("-")
        return cls(p, m, int(size), int(o[1:]) / 100, "bge-small" if e == "-" else e, r, rr == "rr1", qr == "qr1", int(k[1:]))

    def to_json(self) -> dict:
        return {**asdict(self), "id": self.id, "chunking": self.chunking}


# =============================================================================== BM25
STOP = set("a an the of to and or in on for is are be by with from at as it its this that these those any each "
           "we our you your i do does can may what which who how when there their them he she his her was were "
           "has have had if than then so".split())


def _stem(t: str) -> str:
    if t.isalpha() and len(t) > 4:
        if t.endswith("ies"):
            return t[:-3] + "y"
        if t.endswith("s") and not t.endswith("ss"):
            return t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    """Lower-case words; codes like ERR-PO-0412, BAT-500, UN38.3 and section numbers like 6.2 survive whole,
    and their parts are added too (so 'po' and '0412' also match)."""
    out = []
    for t in re.findall(r"[a-z0-9£]+(?:[.\-/_][a-z0-9]+)*", (text or "").lower()):
        if t in STOP:
            continue
        out.append(_stem(t))
        if any(c in t for c in "-/_."):
            out.extend(_stem(p) for p in re.split(r"[-/_.]", t) if len(p) > 1 and p not in STOP)
    return out


class BM25:
    """score(q, d) = sum over query terms t of idf(t) * tf(t,d)*(k1+1) / (tf(t,d) + k1*(1 - b + b*|d|/avgdl)).
    The weights for every (chunk, term) are computed once into a sparse matrix W, so a query is a column sum."""

    def __init__(self, texts: list[str], k1: float = 1.2, b: float = 0.75):
        import numpy as np
        from scipy import sparse

        self.k1, self.b = k1, b
        vocab: dict[str, int] = {}
        rows, cols, vals = [], [], []
        dl = []
        for i, t in enumerate(texts):
            toks = tokenize(t)
            dl.append(len(toks))
            tf: dict[int, int] = {}
            for w in toks:
                j = vocab.setdefault(w, len(vocab))
                tf[j] = tf.get(j, 0) + 1
            for j, f in tf.items():
                rows.append(i)
                cols.append(j)
                vals.append(f)
        n = len(texts)
        self.vocab = vocab
        tfm = sparse.csr_matrix((np.array(vals, dtype=np.float32), (rows, cols)), shape=(n, len(vocab)))
        df = np.bincount(np.array(cols, dtype=np.int64), minlength=len(vocab)) if cols else np.zeros(len(vocab))
        self.idf = np.log(1 + (n - df + 0.5) / (df + 0.5)).astype(np.float32)
        dl = np.array(dl, dtype=np.float32)
        avg = float(dl.mean()) if n else 1.0
        tfm = tfm.tocoo()
        denom = tfm.data + k1 * (1 - b + b * dl[tfm.row] / max(avg, 1e-9))
        w = self.idf[tfm.col] * tfm.data * (k1 + 1) / denom
        self.W = sparse.csc_matrix((w.astype(np.float32), (tfm.row, tfm.col)), shape=(n, len(vocab)))
        self.n = n

    def scores(self, q: str):
        import numpy as np

        ids = sorted({self.vocab[t] for t in tokenize(q) if t in self.vocab})
        if not ids:
            return np.zeros(self.n, dtype=np.float32)
        return np.asarray(self.W[:, ids].sum(axis=1)).ravel()

    def search(self, q: str, k: int, mask=None) -> list[tuple[int, float]]:
        import numpy as np

        s = self.scores(q)
        if mask is not None:
            s = np.where(mask, s, -1.0)
        k = min(k, len(s))
        if k <= 0:
            return []
        top = np.argpartition(-s, k - 1)[:k]
        top = top[np.argsort(-s[top])]
        return [(int(i), float(s[i])) for i in top if s[i] > 0]


# =============================================================================== embeddings and the reranker
_MODELS: dict = {}


def _device():
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


class Embedder:
    def __init__(self, name: str):
        self.name = name
        self.spec = EMBED_MODELS[name]
        if name not in _MODELS:
            from sentence_transformers import SentenceTransformer

            m = SentenceTransformer(self.spec["hf"], device=_device(), trust_remote_code=self.spec.get("trust_remote_code", False))
            m.max_seq_length = self.spec["max_len"]
            if _device() == "cuda":
                m.half()
            _MODELS[name] = m
        self.m = _MODELS[name]

    def passages(self, texts: list[str], batch: int = 128):
        import numpy as np

        # longest first: batches of similar length waste less padding
        order = sorted(range(len(texts)), key=lambda i: -len(texts[i]))
        vecs = self.m.encode([self.spec["p"] + texts[i] for i in order], batch_size=batch, normalize_embeddings=True,
                             show_progress_bar=False, convert_to_numpy=True)
        out = np.zeros((len(texts), vecs.shape[1]), dtype=np.float32)
        out[order] = vecs
        return out

    def query(self, q: str):
        return self.m.encode([self.spec["q"] + q], normalize_embeddings=True, show_progress_bar=False,
                             convert_to_numpy=True)[0].astype("float32")

    def queries(self, qs: list[str]):
        return self.m.encode([self.spec["q"] + q for q in qs], batch_size=64, normalize_embeddings=True,
                             show_progress_bar=False, convert_to_numpy=True).astype("float32")


class Reranker:
    def __init__(self, model: str = RERANK_MODEL):
        if model not in _MODELS:
            from sentence_transformers import CrossEncoder

            m = CrossEncoder(model, device=_device(), max_length=512)
            if _device() == "cuda":
                m.model.half()
            _MODELS[model] = m
        self.m = _MODELS[model]

    def score(self, q: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        return [float(x) for x in self.m.predict([(q, t) for t in texts], batch_size=32, show_progress_bar=False)]


def rrf(lists: list[list[int]], k: int = RRF_K) -> dict[int, float]:
    out: dict[int, float] = {}
    for lst in lists:
        for r, i in enumerate(lst, 1):
            out[i] = out.get(i, 0.0) + 1.0 / (k + r)
    return out


# =============================================================================== query rewriting
REWRITE_SYSTEM = ("You turn a question from a Northbridge Cycles employee into one search query for the company's documents "
                  "(policies, SOPs, Ledgerline ERP 7.2 manuals, service definitions, master data spreadsheets, release notes, "
                  "e-mails). Keep every code, number and name exactly. Add the words the documents would use: the policy or "
                  "procedure topic, Ledgerline screen or field names, synonyms (supplier/vendor, order/PO, certificate/UN 38.3 "
                  "for lithium-cell parts). Reply with the query only, one line, at most 40 words.")


def rewrite(question: str, llm=None) -> dict:
    """One recorded LLM call. Returns {"query", "seconds", "tokens_in", "tokens_out", "cost_usd"}."""
    from ...llm import LLM
    from .evaluate import cost_usd

    llm = llm or LLM(REWRITE_MODEL, cassette="L3v4_rewrite", max_tokens=1024)
    r = llm.chat([{"role": "system", "content": REWRITE_SYSTEM}, {"role": "user", "content": question}])
    q = (r.content or question).strip().splitlines()[0].strip().strip('"') if (r.content or "").strip() else question
    return {"query": q, "seconds": r.seconds, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out,
            "cost_usd": cost_usd(r.tokens_in, r.tokens_out, llm.model)}


# =============================================================================== the index: chunks + Chroma + BM25
def _meta_row(c: C.Chunk, i: int) -> dict:
    m = c.meta
    return {"i": i, "file": c.file, "folder": m.get("folder", ""), "fmt": m.get("fmt", ""),
            "confidential": bool(m.get("confidential")), "superseded": bool(m.get("superseded")),
            "future": bool(m.get("future")), "doc_id": m.get("doc_id") or ""}


def save_chunks(chunks: list[C.Chunk], path) -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"cid": c.cid, "file": c.file, "text": c.text, "body": c.body, "locs": c.locs,
                                "meta": c.meta, "n_tokens": c.n_tokens}, ensure_ascii=False) + "\n")


def load_chunks(path) -> list[C.Chunk]:
    return [C.Chunk(**json.loads(l)) for l in gzip.open(path, "rt", encoding="utf-8")]


class Index:
    """One chunking: its chunks, a BM25 index, and Chroma collections (one per embedding model) at `path`."""

    def __init__(self, path, chunks: list[C.Chunk]):
        import numpy as np

        self.path = pathlib.Path(path)
        self.chunks = chunks
        self.conf = np.array([bool(c.meta.get("confidential")) for c in chunks])
        self._bm25 = None
        self._client = None
        self._cols = {}

    # -- build
    @classmethod
    def build(cls, chunks: list[C.Chunk], models: list[str], path, vectors: dict | None = None, batch: int = 128) -> "Index":
        """Embed with each model (unless vectors[model] is given) and write a persistent Chroma client at path."""
        import chromadb

        path = pathlib.Path(path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        save_chunks(chunks, path / "chunks.jsonl.gz")
        client = chromadb.PersistentClient(path=str(path / "chroma"))
        stats = {}
        for m in models:
            t0 = time.time()
            vecs = vectors.get(m) if vectors and m in vectors else Embedder(m).passages([c.text for c in chunks], batch=batch)
            t_embed = time.time() - t0
            col = client.create_collection(m, metadata={"hnsw:space": "cosine", "model": EMBED_MODELS[m]["hf"]})
            t1 = time.time()
            B = 4000
            for s in range(0, len(chunks), B):
                col.add(ids=[str(i) for i in range(s, min(s + B, len(chunks)))],
                        embeddings=vecs[s:s + B].tolist(),
                        metadatas=[_meta_row(chunks[i], i) for i in range(s, min(s + B, len(chunks)))],
                        documents=[chunks[i].text for i in range(s, min(s + B, len(chunks)))])
            stats[m] = {"embed_s": round(t_embed, 2), "chroma_add_s": round(time.time() - t1, 2), "n": len(chunks),
                        "dim": int(vecs.shape[1])}
            if vectors is not None:
                vectors[m] = vecs
        idx = cls(path, chunks)
        idx._client = client
        idx.build_stats = stats
        return idx

    @classmethod
    def load(cls, path) -> "Index":
        return cls(path, load_chunks(pathlib.Path(path) / "chunks.jsonl.gz"))

    # -- parts
    @property
    def bm25(self) -> BM25:
        if self._bm25 is None:
            self._bm25 = BM25([c.text for c in self.chunks])
        return self._bm25

    def collection(self, model: str):
        if model not in self._cols:
            import chromadb

            if self._client is None:
                self._client = chromadb.PersistentClient(path=str(self.path / "chroma"))
            self._cols[model] = self._client.get_collection(model)
        return self._cols[model]

    def size_bytes(self) -> int:
        return sum(p.stat().st_size for p in self.path.rglob("*") if p.is_file())


class Retriever:
    """A config applied to an index. search() returns ranked items (evaluate.py's shape) with a timing breakdown."""

    def __init__(self, index: Index, cfg: Config, rewrites: dict | None = None):
        self.idx, self.cfg = index, cfg
        self.rewrites = rewrites  # {question: rewrite()-dict}, precomputed (recorded) so the grid reuses one call
        self.emb = Embedder(cfg.embed) if cfg.retrieval != "bm25" else None
        self.rr = Reranker() if cfg.rerank else None

    def _rewrite(self, q):
        if self.rewrites is not None and q in self.rewrites:
            return self.rewrites[q]
        return rewrite(q)

    def search(self, question: str, role: str = C.DEFAULT_ROLE, k: int | None = None, pool: int = POOL) -> dict:
        cfg = self.cfg
        k = k or cfg.k
        t = {}
        extra = {"llm_seconds": 0.0, "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0}
        query = question
        if cfg.rewrite:
            rw = self._rewrite(question)
            query = rw["query"]
            t["rewrite"] = rw["seconds"]
            extra.update(llm_seconds=rw["seconds"], tokens_in=rw["tokens_in"], tokens_out=rw["tokens_out"],
                         cost_usd=rw["cost_usd"])
        t0 = time.perf_counter()
        need = max(k, pool) if (cfg.rerank or cfg.retrieval == "hybrid") else k
        allowed = None if role in C.HR_ROLES else ~self.idx.conf
        lists, scores = [], {}
        if cfg.retrieval in ("dense", "hybrid"):
            a = time.perf_counter()
            qv = self.emb.query(query)
            t["embed"] = time.perf_counter() - a
            a = time.perf_counter()
            where = None if role in C.HR_ROLES else {"confidential": False}
            res = self.idx.collection(cfg.embed).query(query_embeddings=[qv.tolist()], n_results=need, where=where,
                                                       include=["distances"])
            dense = [(int(i), 1.0 - float(d)) for i, d in zip(res["ids"][0], res["distances"][0])]
            t["chroma"] = time.perf_counter() - a
            lists.append([i for i, _ in dense])
            scores["dense"] = dict(dense)
        if cfg.retrieval in ("bm25", "hybrid"):
            a = time.perf_counter()
            b = self.idx.bm25.search(query, need, allowed)
            t["bm25"] = time.perf_counter() - a
            lists.append([i for i, _ in b])
            scores["bm25"] = dict(b)
        if cfg.retrieval == "hybrid":
            a = time.perf_counter()
            fused = rrf(lists)
            order = sorted(fused, key=lambda i: -fused[i])[:need]
            t["fuse"] = time.perf_counter() - a
            base = [(i, fused[i]) for i in order]
        else:
            base = [(i, scores[cfg.retrieval][i]) for i in lists[0]]
        if self.rr:
            a = time.perf_counter()
            cand = [i for i, _ in base[:pool]]
            rs = self.rr.score(question, [self.idx.chunks[i].text for i in cand])
            base = sorted(zip(cand, rs), key=lambda x: -x[1])
            t["rerank"] = time.perf_counter() - a
        local = time.perf_counter() - t0
        items = []
        for r, (i, s) in enumerate(base[:k], 1):
            c = self.idx.chunks[i]
            it = c.as_item()
            it.update({"rank": r, "score": round(float(s), 5), "chunk_index": i,
                       "dense": round(scores.get("dense", {}).get(i, float("nan")), 4) if "dense" in scores else None,
                       "bm25": round(scores.get("bm25", {}).get(i, 0.0), 3) if "bm25" in scores else None})
            items.append(it)
        t = {kk: round(v, 5) for kk, v in t.items()}
        return {"items": items, "seconds": local + t.get("rewrite", 0.0), "local_seconds": local, "timing": t,
                "query": query, **extra}

    __call__ = search


# =============================================================================== rag_search: the best config, ready to use
_BEST: dict = {}


def best_config() -> Config:
    if BEST_PATH.exists():
        d = json.loads(BEST_PATH.read_text())
        return Config.from_id(d["config"]["id"] if isinstance(d.get("config"), dict) else d["config"])
    return Config()


def fetch_best_index(dest=None, url: str = BEST_INDEX_URL) -> pathlib.Path:
    """Download the best config's persisted index (chunks + Chroma) from the RAG Lab, unpack it under dest."""
    import urllib.request

    cfg = best_config()
    dest = pathlib.Path(dest or RAG_INDEX_DIR) / cfg.chunking
    if (dest / "chunks.jsonl.gz").exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / f"{cfg.chunking}.tar.gz"
    urllib.request.urlretrieve(url, tmp)
    with tarfile.open(tmp) as tf:
        tf.extractall(dest.parent)
    tmp.unlink()
    return dest


def _best_retriever(root=None) -> Retriever:
    if "r" in _BEST:
        return _BEST["r"]
    cfg = best_config()
    path = RAG_INDEX_DIR / cfg.chunking
    if not (path / "chunks.jsonl.gz").exists():
        try:
            path = fetch_best_index()
        except Exception:  # noqa: BLE001 - no network or the lab is down: build it from the dump
            units = C.parse(root, parser=cfg.parser)
            chunks = C.chunk(units, cfg.chunker, cfg.size, cfg.overlap)
            Index.build(chunks, [cfg.embed] if cfg.retrieval != "bm25" else [], path)
    idx = Index.load(path)
    _BEST["r"] = Retriever(idx, cfg)
    return _BEST["r"]


USER_ROLES = {"ECLARKE": "PUR-EXEC", "DOKAFOR": "PUR-MGR", "LMORENO": "PUR-SR", "HWEBER": "PLANT-HEAD", "ATANAKA": "STORES",
              "SVC_AGENT": "SERVICE"}


def rag_search(question: str, user: str = "ECLARKE", k: int = 5, role: str | None = None) -> list[dict]:
    """Search Northbridge's documents with the best measured configuration. Returns k cited chunks, best first:
    {"cite", "file", "loc", "text", "score", "rank", "meta"}. Confidential HR documents are filtered out before ranking
    unless the user's role is an HR role. `user` is a Ledgerline user id (ECLARKE ...) or pass `role` directly."""
    role = role or USER_ROLES.get(user, user if user in C.HR_ROLES else C.DEFAULT_ROLE)
    out = _best_retriever().search(question, role=role, k=k)
    return [{"cite": it["cite"], "file": it["file"], "loc": it["loc"], "text": it["text"], "score": it["score"],
             "rank": it["rank"], "meta": it["meta"]} for it in out["items"]]
