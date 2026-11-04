"""L3 v5 · store: where the vectors live. Chroma, for real, built with the course code (rag.Index / rag.add_vectors / rag.HNSW).

    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_store_local.py      # -> logs/v5_store_local.json

What it does, on Modal (CPU, never the laptop):
  1. Document D (POL-PUR-001 v4.1) at the chosen chunking (structured-structure-200-o15): rag.Index.build() writes a
     persistent Chroma client with D's chunks and their bge-small vectors (the grid's vectors from the volume, so every
     number matches NB3 and the RAG Lab). We read back one record (id, document, metadata, the embedding's first numbers),
     list the files Chroma wrote with their real sizes, and query it with Emma's question.
  2. The whole dump at the same chunking (28,953 chunks): rag.add_vectors() into a fresh persistent client, timed. Two
     collections (staff-readable, HR-confidential). Files and sizes again. Emma's question with and without a metadata
     filter that drops superseded copies (`where`), its latency over the golden questions, and HNSW against brute force.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
LOGS = HERE / "logs"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app"}
CHUNKING = "structured-structure-200-o15"
DOC = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy<2.1", "scipy", "tiktoken==0.8.0", "chromadb==1.0.15", "torch==2.4.1", "transformers==4.46.3",
                 "sentence-transformers==3.3.1", "pyyaml==6.0.2")
    .env({"HF_HOME": "/hf", "PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
          "NB_L3_CACHE": "/tmp/cache", "TOKENIZERS_PARALLELISM": "false", "ANONYMIZED_TELEMETRY": "False"})
    .run_commands("python -c \"from sentence_transformers import SentenceTransformer as S; S('BAAI/bge-small-en-v1.5')\"",
                  "python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_file(DUMP / "eval" / "questions.jsonl", "/dump/eval/questions.jsonl")
    .add_local_file(DUMP / "README.md", "/dump/README.md")
)
app = modal.App("northbridge-l3v5-store-local", image=image)
vol = modal.Volume.from_name("northbridge-raglab")


def _files(root: pathlib.Path) -> list[dict]:
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out.append({"path": str(p.relative_to(root)), "bytes": p.stat().st_size})
    return out


def _hnsw_headers(root: pathlib.Path) -> dict:
    """Chroma 1.0's hnswlib header.bin (100 bytes): a 4-byte prefix, then hnswlib's 96-byte header: offsetLevel0,
    max_elements, cur_element_count, size_data_per_element, label_offset, offsetData (size_t each), maxlevel,
    enterpoint (int32), maxM, maxM0, M (size_t), mult (double), ef_construction (size_t)."""
    import struct

    out = {}
    for h in root.rglob("header.bin"):
        b = h.read_bytes()
        if len(b) < 100:
            continue
        o0, mx, cur, per, lab, od = struct.unpack_from("<6Q", b, 4)
        maxlevel, ep = struct.unpack_from("<2i", b, 52)
        maxM, maxM0, M = struct.unpack_from("<3Q", b, 60)
        mult, = struct.unpack_from("<d", b, 84)
        efc, = struct.unpack_from("<Q", b, 92)
        out[h.parent.name] = {"max_elements": mx, "cur_element_count": cur, "size_data_per_element": per, "maxlevel": maxlevel,
                              "maxM": maxM, "maxM0": maxM0, "M": M, "ef_construction": efc}
    return out


def _sqlite(path: pathlib.Path) -> dict:
    import sqlite3

    con = sqlite3.connect(str(path))
    names = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    out = {}
    for n in names:
        try:
            out[n] = con.execute(f'select count(*) from "{n}"').fetchone()[0]
        except Exception as e:  # noqa: BLE001
            out[n] = f"error {type(e).__name__}"
    con.close()
    return out


def _du(root: pathlib.Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


@app.function(volumes={"/vol": vol}, cpu=4, memory=16384, timeout=3600)
def run() -> dict:
    sys.path.insert(0, "/course/ledgerline")
    import numpy as np
    import chromadb
    from ledgerline.course.l3 import rag as R

    src = pathlib.Path("/vol/chroma") / CHUNKING
    chunks = R.load_chunks(src / "chunks.jsonl.gz")
    vecs = np.load(f"/vol/vec/{CHUNKING}/bge-small.npy").astype("float32")
    assert len(chunks) == len(vecs), (len(chunks), vecs.shape)
    out = {"chromadb": chromadb.__version__, "chunking": CHUNKING, "model": R.EMBED_MODELS["bge-small"]["hf"],
           "hnsw": R.HNSW, "n_chunks_dump": len(chunks), "dim": int(vecs.shape[1]),
           "machine": "Modal CPU container, 4 vCPU, 16 GiB", "date": time.strftime("%Y-%m-%d")}

    emb = R.Embedder("bge-small")
    Q = "Can I buy the battery packs from Brightcell Energy? They quote £104."
    qv = emb.query(Q)

    # ---------------------------------------------------------------- 1. document D alone, rag.Index.build
    d_idx = [i for i, c in enumerate(chunks) if c.file == DOC]
    d_chunks = [chunks[i] for i in d_idx]
    t0 = time.time()
    idx = R.Index.build(d_chunks, ["bge-small"], "/tmp/store_D", vectors={"bge-small": vecs[d_idx]})
    out["D"] = {"file": DOC, "n_chunks": len(d_chunks), "build_s": round(time.time() - t0, 3),
                "tokens": [c.n_tokens for c in d_chunks]}
    col = idx.collection("bge-small")
    hr = idx.collection("bge-small" + R.HR_SUFFIX)
    out["D"]["counts"] = {"bge-small": col.count(), "bge-small__hr": hr.count()}
    out["D"]["collection_config"] = json.loads(json.dumps(col.configuration_json, default=str))
    out["D"]["collection_metadata"] = col.metadata
    # one record: the chunk that holds §6.2
    pick = next(j for j, c in enumerate(d_chunks) if "6.2" in c.body and "UN 38.3" in c.body
                and any(x.startswith("6.") for x in c.locs.get("sections", [])))
    out["D"]["chunks"] = [{"id": str(j), "cite": c.cite, "n_tokens": c.n_tokens, "text": c.text} for j, c in enumerate(d_chunks)]
    rec = col.get(ids=[str(pick)], include=["documents", "metadatas", "embeddings"])
    e = rec["embeddings"][0]
    out["D"]["record"] = {"id": rec["ids"][0], "document": rec["documents"][0], "metadata": rec["metadatas"][0],
                          "embedding_first": [round(float(x), 4) for x in e[:8]], "embedding_len": len(e),
                          "embedding_norm": round(float(np.linalg.norm(e)), 4),
                          "cite": d_chunks[pick].cite, "locs": d_chunks[pick].locs,
                          "chunk_meta": {k: d_chunks[pick].meta.get(k) for k in ("doc_id", "title", "version", "effective",
                                                                                 "status", "confidential", "superseded", "future")}}
    # query D's collection with Emma's question
    t0 = time.perf_counter()
    res = col.query(query_embeddings=[qv.tolist()], n_results=5, include=["distances", "metadatas", "documents"])
    out["D"]["query"] = {"question": Q, "ms": round(1000 * (time.perf_counter() - t0), 2), "results": [
        {"id": i, "distance": round(float(d), 4), "similarity": round(1 - float(d), 4), "cite": d_chunks[int(i)].cite,
         "start": doc[:160]} for i, d, doc in zip(res["ids"][0], res["distances"][0], res["documents"][0])]}
    # files on disk (let Chroma flush by dropping the client)
    del col, hr, idx
    out["D"]["files"] = _files(pathlib.Path("/tmp/store_D"))
    out["D"]["bytes_total"] = _du(pathlib.Path("/tmp/store_D"))
    out["D"]["hnsw_headers"] = _hnsw_headers(pathlib.Path("/tmp/store_D"))
    out["D"]["sqlite_tables"] = _sqlite(pathlib.Path("/tmp/store_D/chroma/chroma.sqlite3"))

    # ---------------------------------------------------------------- 2. the whole dump, rag.add_vectors
    root = pathlib.Path("/tmp/store_dump")
    root.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(root / "chroma"))
    t0 = time.time()
    R.add_vectors(client, "bge-small", chunks, vecs)
    add_s = time.time() - t0
    col = client.get_collection("bge-small")
    hr = client.get_collection("bge-small" + R.HR_SUFFIX)
    out["dump"] = {"add_s": round(add_s, 1), "counts": {"bge-small": col.count(), "bge-small__hr": hr.count()},
                   "n_superseded": sum(1 for c in chunks if c.meta.get("superseded")),
                   "n_future": sum(1 for c in chunks if c.meta.get("future")),
                   "n_confidential": sum(1 for c in chunks if c.meta.get("confidential"))}

    def q(v, n=10, where=None):
        t = time.perf_counter()
        r = col.query(query_embeddings=[v.tolist()], n_results=n, where=where, include=["distances", "metadatas"])
        return r, 1000 * (time.perf_counter() - t)

    def rows(r):
        return [{"id": i, "similarity": round(1 - float(d), 4), "cite": chunks[int(i)].cite, "file": m["file"],
                 "superseded": m["superseded"], "future": m["future"], "confidential": m["confidential"]}
                for i, d, m in zip(r["ids"][0], r["distances"][0], r["metadatas"][0])]

    q(qv)  # warm
    r1, ms1 = q(qv)
    r2, ms2 = q(qv, where={"superseded": False})
    out["dump"]["emma"] = {"question": Q, "plain": {"ms": round(ms1, 2), "results": rows(r1)},
                           "where_not_superseded": {"where": {"superseded": False}, "ms": round(ms2, 2), "results": rows(r2)}}

    # a question whose unfiltered top 10 holds a superseded copy: the filter's clearest case
    from ledgerline.course.l3 import corpus as C
    qs = C.questions("/dump")
    texts = [x["question"] for x in qs]
    QV = emb.queries(texts)
    lat_plain, lat_where, demo = [], [], None
    for x, v in zip(qs, QV):
        a, ma = q(v)
        b, mb = q(v, where={"superseded": False})
        lat_plain.append(ma)
        lat_where.append(mb)
        if demo is None and x.get("type") == "version_conflict":
            ra = rows(a)
            if any(t["superseded"] for t in ra[:5]):
                demo = {"id": x["id"], "question": x["question"], "plain": ra[:5], "where_not_superseded": rows(b)[:5]}
    out["dump"]["version_demo"] = demo
    out["dump"]["latency_ms"] = {"n_questions": len(qs), "k": 10,
                                 "plain": {"p50": round(_pct(lat_plain, .5), 2), "p95": round(_pct(lat_plain, .95), 2)},
                                 "where_not_superseded": {"p50": round(_pct(lat_where, .5), 2), "p95": round(_pct(lat_where, .95), 2)}}
    # HNSW against brute force, for Emma's question (the full check over 224 questions is logs/hnsw_check.json)
    mask = np.array([not c.meta.get("confidential") for c in chunks])
    sims = vecs @ qv
    sims[~mask] = -9
    exact = [str(i) for i in np.argsort(-sims)[:10]]
    out["dump"]["emma_exact_vs_hnsw"] = {"exact_top10": exact, "hnsw_top10": r1["ids"][0],
                                         "overlap@10": len(set(exact) & set(r1["ids"][0])) / 10}
    del col, hr, client
    out["dump"]["files"] = _files(root)
    out["dump"]["bytes_total"] = _du(root)
    out["dump"]["hnsw_headers"] = _hnsw_headers(root)
    out["dump"]["sqlite_tables"] = _sqlite(root / "chroma" / "chroma.sqlite3")
    out["dump"]["raw_vector_bytes"] = int(vecs.nbytes)
    return out


@app.local_entrypoint()
def main():
    r = run.remote()
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "v5_store_local.json").write_text(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    print("wrote", LOGS / "v5_store_local.json")
    print(json.dumps({k: r[k] for k in ("chromadb", "n_chunks_dump", "dim")}, indent=1))
    print("D:", r["D"]["n_chunks"], "chunks;", r["D"]["counts"], "files:", r["D"]["files"])
    print("dump:", r["dump"]["counts"], r["dump"]["add_s"], "s; bytes", r["dump"]["bytes_total"])
    for f in r["dump"]["files"]:
        print("  ", f)
    print("latency", r["dump"]["latency_ms"])
    print("emma plain:", [(x["cite"][:50], x["similarity"], x["superseded"]) for x in r["dump"]["emma"]["plain"]["results"]])
    print("version demo:", json.dumps(r["dump"]["version_demo"], indent=0)[:1500])
