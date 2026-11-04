"""L3 v5 · store: the production walkthrough on Qdrant Cloud. Northbridge's chunks, their bge-small vectors and a BM25
full-text index in one collection; dense, BM25 and hybrid (RRF) search inside the engine; permission and version filters.

    M=/Users/raj/.venv/bin/modal; S=lectures/L3-the-memory/experiments/v5_store_cloud.py
    $M run $S::ingest      # create the collection + payload indexes, upsert D's 15 chunks, then the rest -> logs/v5_store_ingest.json
    $M run $S::query       # Emma's question, ERR-PO-0412, filters, hybrid, 224-question recall + latency -> logs/v5_store_cloud.json

Credentials: QDRANT_URL and QDRANT_API_KEY are read ONLY from /Users/raj/Claude_Brain/enterprise-agents-course/vectordb.env
(gitignored by *.env), on the laptop, and passed to the Modal container as a secret. They are never printed or logged.
The cluster: Qdrant Cloud free tier, GCP europe-west3 (Frankfurt). Vectors: the grid's bge-small vectors from the Modal
volume (the same numbers NB3 and the RAG Lab use); questions are embedded with the course Embedder on the container.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
ENV = COURSE / "vectordb.env"
LOGS = HERE / "logs"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app"}
CHUNKING = "structured-structure-200-o15"
DOC = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
COLLECTION = "northbridge_docs"
ALIAS = "northbridge"          # the app queries the alias; a new embedding model = a new collection + one atomic alias swap
EMMA = "Can I buy the battery packs from Brightcell Energy? They quote £104."
CODE_Q = "What does ERR-PO-0412 mean?"
EF = 2000          # hnsw_ef for the dense search: logs/v5_store_ef.json (default 0.434 recall@5, 2000: 0.551, exact: 0.566)


def _creds() -> dict:
    """Read the two values from vectordb.env (laptop side only). Never print them."""
    if not modal.is_local() or not ENV.exists():
        return {}
    out = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() in ("QDRANT_URL", "QDRANT_API_KEY"):
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy<2.1", "scipy", "tiktoken==0.8.0", "qdrant-client==1.20.0", "torch==2.4.1", "transformers==4.46.3",
                 "sentence-transformers==3.3.1", "pyyaml==6.0.2")
    .env({"HF_HOME": "/hf", "PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
          "NB_L3_CACHE": "/tmp/cache", "TOKENIZERS_PARALLELISM": "false"})
    .run_commands("python -c \"from sentence_transformers import SentenceTransformer as S; S('BAAI/bge-small-en-v1.5')\"",
                  "python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
)
app = modal.App("northbridge-l3v5-store-cloud", image=image)
vol = modal.Volume.from_name("northbridge-raglab")
_c = _creds()
secret = modal.Secret.from_dict(_c) if modal.is_local() else modal.Secret.from_dict({})


def _client():
    from qdrant_client import QdrantClient

    return QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ.get("QDRANT_API_KEY") or None, timeout=120)


def _load():
    sys.path.insert(0, "/course/ledgerline")
    import numpy as np
    from ledgerline.course.l3 import rag as R

    chunks = R.load_chunks(pathlib.Path("/vol/chroma") / CHUNKING / "chunks.jsonl.gz")
    vecs = np.load(f"/vol/vec/{CHUNKING}/bge-small.npy").astype("float32")
    assert len(chunks) == len(vecs)
    return chunks, vecs


def payload(c, i: int) -> dict:
    """What each point carries: the text both ways (two full-text indexes, two tokenizers), where it came from, and the
    flags the filters use. The HR flag is the one that must never be forgotten."""
    m, l = c.meta, c.locs
    return {"chunk_index": i, "cite": c.cite, "text": c.text, "text_code": c.text, "file": c.file,
            "folder": m.get("folder", ""), "fmt": m.get("fmt", ""), "doc_id": m.get("doc_id") or "",
            "title": m.get("title") or "", "section": (l.get("sections") or [""])[0], "pages": l.get("pages") or [],
            "version": m.get("version") or "", "effective": m.get("effective") or "", "status": m.get("status") or "",
            "superseded": bool(m.get("superseded")), "future": bool(m.get("future")),
            "confidential": bool(m.get("confidential")), "audience": m.get("audience") or "all staff",
            "n_tokens": c.n_tokens}


def _jsonable(x):
    return json.loads(json.dumps(x, default=lambda o: o.model_dump() if hasattr(o, "model_dump") else str(o)))


def do_ingest(batch: int = 256, machine: str = "Modal CPU container (us-east), 2 vCPU") -> dict:
    from qdrant_client import models as M

    chunks, vecs = _load()
    q = _client()
    out = {"date": time.strftime("%Y-%m-%d"), "collection": COLLECTION, "chunking": CHUNKING, "model": "BAAI/bge-small-en-v1.5",
           "qdrant_client": "1.20.0", "machine": machine}
    if q.collection_exists(COLLECTION):
        q.delete_collection(COLLECTION)
    t0 = time.time()
    q.create_collection(COLLECTION, vectors_config={"dense": M.VectorParams(size=int(vecs.shape[1]), distance=M.Distance.COSINE)})
    # payload indexes BEFORE the upsert: filters use them inside the HNSW search; text indexes give BM25 in the engine
    for f in ("confidential", "superseded", "future"):
        q.create_payload_index(COLLECTION, f, field_schema=M.PayloadSchemaType.BOOL)
    for f in ("folder", "doc_id", "file", "status"):
        q.create_payload_index(COLLECTION, f, field_schema=M.PayloadSchemaType.KEYWORD)
    common = dict(type=M.TextIndexType.TEXT, lowercase=True, stopwords=M.Language.ENGLISH,
                  scoring=M.TextScoringParams(type=M.TextScoringType.BM25))
    q.create_payload_index(COLLECTION, "text", field_schema=M.TextIndexParams(tokenizer=M.TokenizerType.WORD, **common))
    q.create_payload_index(COLLECTION, "text_code", field_schema=M.TextIndexParams(tokenizer=M.TokenizerType.CODE, **common))
    out["create_s"] = round(time.time() - t0, 2)

    def up(ids):
        t = time.time()
        for s in range(0, len(ids), batch):
            part = ids[s:s + batch]
            q.upsert(COLLECTION, wait=True, points=[M.PointStruct(id=i, vector={"dense": vecs[i].tolist()},
                                                                  payload=payload(chunks[i], i)) for i in part])
        return round(time.time() - t, 2)

    d_ids = [i for i, c in enumerate(chunks) if c.file == DOC]
    out["D"] = {"n": len(d_ids), "ids": d_ids, "upsert_s": up(d_ids), "count_after": q.count(COLLECTION, exact=True).count}
    rest = [i for i in range(len(chunks)) if i not in set(d_ids)]
    out["rest"] = {"n": len(rest), "upsert_s": up(rest)}
    for _ in range(120):  # wait for the optimiser to build the HNSW graph
        info = q.get_collection(COLLECTION)
        if str(info.status).lower().endswith("green") and (info.indexed_vectors_count or 0) >= len(chunks) * 0.95:
            break
        time.sleep(5)
    # the alias the app uses (delete + create in one call: the swap is atomic)
    ops = [M.CreateAliasOperation(create_alias=M.CreateAlias(collection_name=COLLECTION, alias_name=ALIAS))]
    if any(a.alias_name == ALIAS for a in q.get_aliases().aliases):
        ops.insert(0, M.DeleteAliasOperation(delete_alias=M.DeleteAlias(alias_name=ALIAS)))
    q.update_collection_aliases(change_aliases_operations=ops)
    out["alias"] = {a.alias_name: a.collection_name for a in q.get_aliases().aliases}
    info = q.get_collection(COLLECTION)
    out["count"] = q.count(COLLECTION, exact=True).count
    out["count_confidential"] = q.count(COLLECTION, exact=True, count_filter=M.Filter(must=[
        M.FieldCondition(key="confidential", match=M.MatchValue(value=True))])).count
    out["count_superseded"] = q.count(COLLECTION, exact=True, count_filter=M.Filter(must=[
        M.FieldCondition(key="superseded", match=M.MatchValue(value=True))])).count
    out["info"] = _jsonable(info)
    out["sample_point"] = _jsonable(q.retrieve(COLLECTION, ids=[d_ids[5]], with_payload=True, with_vectors=True)[0])
    v = out["sample_point"].get("vector", {}).get("dense")
    if v:
        out["sample_point"]["vector"] = {"dense_first8": [round(x, 4) for x in v[:8]], "dense_len": len(v)}
    return out


# ------------------------------------------------------------------------------------------------ queries
def _filters(M):
    no_hr = M.FieldCondition(key="confidential", match=M.MatchValue(value=True))
    return {"emma": M.Filter(must_not=[no_hr]),
            "emma_current": M.Filter(must_not=[no_hr, M.FieldCondition(key="superseded", match=M.MatchValue(value=True))])}


def _bm25(M, text: str, k1: float = 1.2, b: float = 0.75):
    return M.TextQuery(text=M.TextQueryInput(query=text, scoring=M.Bm25Scoring(bm25=M.Bm25Params(k=k1, b=b))))


def _rows(res) -> list[dict]:
    return [{"id": p.id, "score": round(float(p.score), 4), "cite": p.payload.get("cite"), "file": p.payload.get("file"),
             "confidential": p.payload.get("confidential"), "superseded": p.payload.get("superseded")} for p in res.points]


def do_query(region_note: str = "us-east") -> dict:
    import numpy as np
    from qdrant_client import models as M
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    chunks, _ = _load()
    q = _client()
    F = _filters(M)
    emb = R.Embedder("bge-small")
    WITH = ["cite", "file", "confidential", "superseded"]
    out = {"date": time.strftime("%Y-%m-%d"), "collection": COLLECTION, "from": f"Modal CPU container ({region_note})", "hnsw_ef": EF,
           "count": q.count(COLLECTION, exact=True).count}

    def search(mode, text, qv, flt, k=10, field="text", pool=20, ef=None):
        sp = M.SearchParams(hnsw_ef=ef) if ef else None   # logs/v5_store_ef.json: the default width loses recall here
        t = time.perf_counter()
        if mode == "dense":
            r = q.query_points(ALIAS, query=qv.tolist(), using="dense", query_filter=flt, limit=k, with_payload=WITH, search_params=sp)
        elif mode == "bm25":
            r = q.query_points(ALIAS, query=_bm25(M, text), using=field, query_filter=flt, limit=k, with_payload=WITH)
        else:  # hybrid: both lists inside the engine, fused by RRF (k = 60, as rag.rrf)
            r = q.query_points(ALIAS, prefetch=[
                M.Prefetch(query=qv.tolist(), using="dense", filter=flt, limit=pool, params=sp),
                M.Prefetch(query=_bm25(M, text), using=field, filter=flt, limit=pool)],
                query=M.RrfQuery(rrf=M.Rrf(k=R.RRF_K)), query_filter=flt, limit=k, with_payload=WITH)
        return r, (time.perf_counter() - t)

    # network round trip alone: the smallest call there is
    rtt = []
    for _ in range(30):
        t = time.perf_counter()
        q.count(COLLECTION, exact=False)
        rtt.append(time.perf_counter() - t)
    out["rtt_ms"] = {"p50": round(1000 * float(np.median(rtt)), 1), "min": round(1000 * min(rtt), 1)}

    # 1. Emma's question, every mode, Emma's permission filter
    qv = emb.query(EMMA)
    search("dense", EMMA, qv, F["emma"])  # warm
    ex = {}
    for mode in ("dense", "bm25", "hybrid"):
        r, s = search(mode, EMMA, qv, F["emma"], ef=EF)
        ex[mode] = {"ms": round(1000 * s, 1), "results": _rows(r)}
    out["emma"] = {"question": EMMA, "filter": "must_not confidential", **ex}
    # only D's chunks (a filter on the file): which part of D answers?
    r, s = search("hybrid", EMMA, qv, M.Filter(must=[M.FieldCondition(key="file", match=M.MatchValue(value=DOC))]), k=5, ef=EF)
    out["emma_in_D"] = {"filter": {"must": [{"key": "file", "match": {"value": DOC}}]}, "ms": round(1000 * s, 1), "results": _rows(r)}

    # 2. the code: ERR-PO-0412 with the word and the code tokenizer
    cv = emb.query(CODE_Q)
    out["code"] = {"question": CODE_Q}
    for mode, field in (("dense", "text"), ("bm25", "text"), ("bm25", "text_code"), ("hybrid", "text")):
        r, s = search(mode, CODE_Q, cv, F["emma"], k=5, field=field, ef=EF)
        out["code"][f"{mode}:{field}"] = {"ms": round(1000 * s, 1), "results": _rows(r)}

    # 3. the permission filter: an HR question asked by a purchase executive, with and without the filter
    G = E.Golden("/dump")
    pq = G.by_id["Q-901"]
    pv = emb.query(pq["question"])
    r0, _ = search("hybrid", pq["question"], pv, None, k=5, ef=EF)
    r1, _ = search("hybrid", pq["question"], pv, F["emma"], k=5, ef=EF)
    out["permission"] = {"id": "Q-901", "question": pq["question"], "role": C.role_of(pq), "mode": "hybrid, hnsw_ef 2000",
                         "no_filter": _rows(r0), "filter_must_not_confidential": _rows(r1)}
    out["permission_scan"] = {}
    for qid in ("Q-901", "Q-902", "Q-905", "Q-906", "Q-910"):
        x = G.by_id[qid]
        xv = emb.query(x["question"])
        row = {"question": x["question"]}
        for mode in ("dense", "bm25", "hybrid"):
            a, _ = search(mode, x["question"], xv, None, k=5, ef=EF)
            row[mode] = sum(1 for p in a.points if p.payload.get("confidential"))
        out["permission_scan"][qid] = row   # confidential chunks in the unfiltered top 5; with the filter it is 0 by construction

    # 4. the version filter: Q-604 (the unfiltered top 5 held a superseded copy in local Chroma)
    vq = G.by_id["Q-604"]
    vv = emb.query(vq["question"])
    r0, _ = search("dense", vq["question"], vv, F["emma"], k=5, ef=EF)
    r1, _ = search("dense", vq["question"], vv, F["emma_current"], k=5, ef=EF)
    out["version"] = {"id": "Q-604", "question": vq["question"], "emma_filter": _rows(r0), "plus_not_superseded": _rows(r1)}

    # 5. all 224 documentation questions: recall@k (evaluate.py, the course's own scorer) and latency, per mode
    QV = {x["id"]: v for x, v in zip(G.qs, emb.queries([x["question"] for x in G.qs]))}
    byq = {x["question"]: x for x in G.qs}
    modes = {"dense": ("dense", "text", None), "dense_ef2000": ("dense", "text", EF), "bm25_word": ("bm25", "text", None),
             "bm25_code": ("bm25", "text_code", None), "hybrid_rrf": ("hybrid", "text", None), "hybrid_rrf_ef2000": ("hybrid", "text", EF)}
    out["golden"] = {}
    for name, (mode, field, ef) in modes.items():
        def method(question, role, mode=mode, field=field, ef=ef):
            x = byq[question]
            flt = None if role in C.HR_ROLES else F["emma"]
            r, s = search(mode, question, QV[x["id"]], flt, k=10, field=field, ef=ef)
            return {"items": [chunks[p.id].as_item() for p in r.points], "seconds": s}

        rep = E.retrieval_only(method, G)
        sm = rep["summary"]
        out["golden"][name] = {"overall": {k: sm["overall"].get(k) for k in ("n", "recall@1", "recall@5", "recall@10", "mrr")},
                               "exact_code_recall@5": sm["by_type"].get("exact_code", {}).get("recall@5"),
                               "latency_s": sm["latency_s"]}
    # a filter's cost in Qdrant: the same dense query, no filter vs Emma's filter (payload index on `confidential`)
    lat = {"none": [], "emma": [], "emma_current": []}
    for x in G.qs:
        for key, flt in (("none", None), ("emma", F["emma"]), ("emma_current", F["emma_current"])):
            _, s = search("dense", x["question"], QV[x["id"]], flt, ef=EF)
            lat[key].append(s)
    out["filter_latency_ms"] = {k: {"p50": round(1000 * float(np.percentile(v, 50)), 1), "p95": round(1000 * float(np.percentile(v, 95)), 1)}
                                for k, v in lat.items()}
    out["collection_info"] = _jsonable(q.get_collection(COLLECTION))
    return out


@app.function(volumes={"/vol": vol}, secrets=[secret], cpu=2, memory=8192, timeout=3600)
def ingest_remote() -> dict:
    return do_ingest()


@app.function(volumes={"/vol": vol}, secrets=[secret], cpu=4, memory=16384, timeout=3600)
def query_remote() -> dict:
    return do_query("us-east")


# the same code against a self-hosted Qdrant 1.20.0 inside the container (no network, no account): a test and a baseline
selfhost_image = (modal.Image.from_registry("qdrant/qdrant:v1.20.0", add_python="3.11")
                  .pip_install("numpy<2.1", "scipy", "tiktoken==0.8.0", "qdrant-client==1.20.0", "torch==2.4.1",
                               "transformers==4.46.3", "sentence-transformers==3.3.1", "pyyaml==6.0.2")
                  .env({"HF_HOME": "/hf", "PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
                        "NB_L3_CACHE": "/tmp/cache", "TOKENIZERS_PARALLELISM": "false",
                        "QDRANT_URL": "http://127.0.0.1:6333", "QDRANT_API_KEY": ""})
                  .run_commands("python -c \"from sentence_transformers import SentenceTransformer as S; S('BAAI/bge-small-en-v1.5')\"",
                                "python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
                  .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                                 ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
                  .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts))


@app.function(image=selfhost_image, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=3600)
def selfhost_remote() -> dict:
    import subprocess
    import urllib.request

    srv = subprocess.Popen(["/qdrant/qdrant"], cwd="/qdrant", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://127.0.0.1:6333/healthz", timeout=2)
            break
        except Exception:  # noqa: BLE001
            time.sleep(1)
    os.environ["QDRANT_API_KEY"] = ""
    a = do_ingest(machine="Modal CPU container, 4 vCPU, Qdrant 1.20.0 self-hosted in the same container")
    b = do_query("same container as a self-hosted Qdrant 1.20.0")
    srv.terminate()
    return {"ingest": a, "query": b}


def do_ef_check() -> dict:
    """Dense recall against the HNSW search width on the cluster: Qdrant's default, wider, and exact (brute force)."""
    import numpy as np
    from qdrant_client import models as M
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    chunks, _ = _load()
    q = _client()
    F = _filters(M)
    emb = R.Embedder("bge-small")
    G = E.Golden("/dump")
    info = q.get_collection(COLLECTION)
    out = {"date": time.strftime("%Y-%m-%d"), "status": str(info.status), "points_count": info.points_count,
           "indexed_vectors_count": info.indexed_vectors_count, "segments_count": info.segments_count, "runs": {}}
    QV = {x["id"]: v for x, v in zip(G.qs, emb.queries([x["question"] for x in G.qs]))}
    byq = {x["question"]: x for x in G.qs}
    for name, params in (("default", None), ("hnsw_ef_128", M.SearchParams(hnsw_ef=128)), ("hnsw_ef_512", M.SearchParams(hnsw_ef=512)),
                         ("hnsw_ef_2000", M.SearchParams(hnsw_ef=2000)), ("exact", M.SearchParams(exact=True))):
        def method(question, role, params=params):
            x = byq[question]
            flt = None if role in C.HR_ROLES else F["emma"]
            t = time.perf_counter()
            r = q.query_points(ALIAS, query=QV[x["id"]].tolist(), using="dense", query_filter=flt, limit=10, search_params=params, with_payload=False)
            return {"items": [chunks[p.id].as_item() for p in r.points], "seconds": time.perf_counter() - t}

        rep = E.retrieval_only(method, G)
        sm = rep["summary"]
        out["runs"][name] = {"recall@5": sm["overall"]["recall@5"], "recall@10": sm["overall"]["recall@10"], "latency_s": sm["latency_s"]}
    return out


@app.function(volumes={"/vol": vol}, secrets=[secret], cpu=4, memory=16384, timeout=3600)
def ef_remote() -> dict:
    return do_ef_check()


@app.local_entrypoint()
def ef_check():
    _check()
    r = ef_remote.remote()
    _write("v5_store_ef.json", r)
    print({k: r[k] for k in ("status", "points_count", "indexed_vectors_count", "segments_count")})
    for k, v in r["runs"].items():
        print(f"  {k:12s} r@5 {v['recall@5']} r@10 {v['recall@10']} p50 {v['latency_s']['p50']} p95 {v['latency_s']['p95']}")


def _write(name: str, data):
    LOGS.mkdir(parents=True, exist_ok=True)
    s = json.dumps(data, indent=1, ensure_ascii=False, default=str)
    for v in _c.values():  # belt and braces: the key or URL must never land in a log
        assert v not in s, "credential in log"
    (LOGS / name).write_text(s)
    print("wrote", LOGS / name)


def _check():
    if set(_c) != {"QDRANT_URL", "QDRANT_API_KEY"} or not all(_c.values()):
        raise SystemExit(f"fill QDRANT_URL and QDRANT_API_KEY in {ENV} first")


@app.local_entrypoint()
def ingest():
    _check()
    r = ingest_remote.remote()
    _write("v5_store_ingest.json", r)
    print({k: r[k] for k in ("create_s", "count", "count_confidential", "count_superseded")}, "D:", r["D"]["n"],
          r["D"]["upsert_s"], "s; rest:", r["rest"]["n"], r["rest"]["upsert_s"], "s")


@app.local_entrypoint()
def selfhost():
    r = selfhost_remote.remote()
    _write("v5_store_selfhost.json", r)
    g = r["query"]
    print("ingest", {k: r["ingest"][k] for k in ("count", "count_confidential", "count_superseded")}, r["ingest"]["rest"]["upsert_s"])
    print("rtt", g["rtt_ms"], "filter latency", g["filter_latency_ms"])
    for k, v in g["golden"].items():
        print(f"  {k:12s}", v["overall"], "codes@5", v["exact_code_recall@5"], "lat", v["latency_s"])
    for k, v in g["code"].items():
        if isinstance(v, dict):
            print(k, [x["cite"][:45] for x in v["results"][:3]])
    print("in D:", [x["cite"][:60] for x in g["emma_in_D"]["results"]])


@app.local_entrypoint()
def query():
    _check()
    r = query_remote.remote()
    _write("v5_store_cloud.json", r)
    print("rtt", r["rtt_ms"], "filter latency", r["filter_latency_ms"])
    for k, v in r["golden"].items():
        print(f"  {k:12s}", v["overall"], "codes@5", v["exact_code_recall@5"], "lat", v["latency_s"])
    for m in ("dense", "bm25", "hybrid"):
        print(m, r["emma"][m]["ms"], "ms", [x["cite"][:45] for x in r["emma"][m]["results"][:5]])
    print("in D:", [x["cite"][:60] for x in r["emma_in_D"]["results"]])
    for k, v in r["code"].items():
        if isinstance(v, dict):
            print(k, [x["cite"][:45] for x in v["results"][:3]])
    print("perm no filter:", [(x["cite"][:40], x["confidential"]) for x in r["permission"]["no_filter"]])
    print("perm filter:", [(x["cite"][:40], x["confidential"]) for x in r["permission"]["filter_must_not_confidential"]])
