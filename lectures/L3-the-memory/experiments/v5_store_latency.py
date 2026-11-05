"""L3 v5 · store: where one question's time goes, and which round trips an engineer can cut. Read-only against our
Qdrant Cloud cluster (free tier, GCP europe-west3, Frankfurt): nothing is created, changed or deleted.

    M=/Users/raj/.venv/bin/modal; S=lectures/L3-the-memory/experiments/v5_store_latency.py
    $M run $S             # two containers: Modal's default region (US) and region="eu"  -> logs/v5_store_latency.json

Each container measures, on the same 30 golden questions (documentation, first 30 by id):
  embed       bge-small question embedding on the container's CPU (the course Embedder)
  rtt         the smallest call there is (count, approximate), on a kept-open client: the network round trip
  server      the time Qdrant itself reports for the hybrid request ("time" in the REST reply): search inside the store
  hybrid      one hybrid request (dense + BM25 prefetch, RRF on the server), kept-open client, REST and gRPC
  reconnect   a new client per question (TLS handshake + the client's version check + the request)
  two_calls   dense and BM25 as two requests, fused with rag.rrf in our code
  batch       10 questions: 10 hybrid requests one after another vs one query_batch_points call
  answer      gemini-3.8-flash writing the answer from the top 5 (5 calls)
The EU container also reads (read-only) the facts the filter slides teach: the status values in our payloads (facet),
the flag counts, two points' payloads, Q-605 with and without the superseded filter, and HNSW-vs-exact overlap@10.

Credentials: QDRANT_URL / QDRANT_API_KEY only from vectordb.env, GEMINI_API_KEY only from wm-lecture6-ijepa/.env, read on
the laptop and passed as a Modal secret. Never printed; the log is checked for them (and the cluster host) before writing.
"""
from __future__ import annotations

import json
import os
import pathlib
import statistics
import sys
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")
ENV = COURSE / "vectordb.env"
GEMINI_ENV = pathlib.Path("/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env")
LOGS = HERE / "logs"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app"}
COLLECTION, ALIAS, EF, N_Q = "northbridge_docs", "northbridge", 2000, 30
EMMA = "Can I buy the battery packs from Brightcell Energy? They quote £104."
ANSWER_SYSTEM = ("You answer questions from purchase staff at Northbridge Cycles. Use ONLY the document extracts given to you. "
                 "Begin with the direct answer in one sentence. Cite every rule as [DOC-ID §section]. At most four sentences.")


def _read_env(path: pathlib.Path, keys: tuple) -> dict:
    if not modal.is_local() or not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() in keys:
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


_c = {**_read_env(ENV, ("QDRANT_URL", "QDRANT_API_KEY")), **_read_env(GEMINI_ENV, ("GEMINI_API_KEY",))}
secret = modal.Secret.from_dict(_c) if modal.is_local() else modal.Secret.from_dict({})

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("numpy<2.1", "scipy", "tiktoken==0.8.0", "qdrant-client==1.20.0", "torch==2.4.1", "transformers==4.46.3",
                 "sentence-transformers==3.3.1", "pyyaml==6.0.2", "httpx")
    .env({"HF_HOME": "/hf", "PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
          "NB_L3_CACHE": "/tmp/cache", "TOKENIZERS_PARALLELISM": "false"})
    .run_commands("python -c \"from sentence_transformers import SentenceTransformer as S; S('BAAI/bge-small-en-v1.5')\"",
                  "python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP / "eval", "/dump/eval")
    .add_local_file(DUMP / "README.md", "/dump/README.md")
)
app = modal.App("northbridge-l3v5-store-latency", image=image)


def _st(xs: list[float]) -> dict:
    xs = sorted(1000 * x for x in xs)
    p = lambda q: xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]  # noqa: E731
    return {"n": len(xs), "p50": round(statistics.median(xs), 1), "p95": round(p(0.95), 1), "min": round(xs[0], 1)}


def _scrub(s: str) -> str:
    for v in (os.environ.get("QDRANT_URL", ""), os.environ.get("QDRANT_API_KEY", ""), os.environ.get("GEMINI_API_KEY", "")):
        if v:
            s = s.replace(v, "<secret>")
    host = os.environ.get("QDRANT_URL", "").split("//")[-1].split(":")[0].split("/")[0]
    return s.replace(host, "<cluster>") if host else s


def measure(with_facts: bool) -> dict:
    sys.path.insert(0, "/course/ledgerline")
    import httpx
    from qdrant_client import QdrantClient, models as M
    from ledgerline.course.l3 import corpus as C, rag as R

    URL, KEY = os.environ["QDRANT_URL"], os.environ["QDRANT_API_KEY"]
    out = {"date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "modal_region": os.environ.get("MODAL_REGION"),
           "modal_cloud": os.environ.get("MODAL_CLOUD_PROVIDER"), "cluster": "Qdrant Cloud free tier, GCP europe-west3 (Frankfurt)",
           "collection": ALIAS + " -> " + COLLECTION, "hnsw_ef": EF, "n_questions": N_Q, "errors": {}}
    qs = sorted(C.questions(pathlib.Path("/dump"), "documentation"), key=lambda x: x["id"])[:N_Q]
    texts = [x["question"] for x in qs]
    emb = R.Embedder("bge-small")
    emb.query("warm up")
    t_embed, QV = [], []
    for t in texts:
        a = time.perf_counter()
        QV.append(emb.query(t))
        t_embed.append(time.perf_counter() - a)
    out["embed"] = _st(t_embed)

    no_hr = M.FieldCondition(key="confidential", match=M.MatchValue(value=True))
    emma = M.Filter(must_not=[no_hr])
    sp = M.SearchParams(hnsw_ef=EF)
    bm25 = lambda t: M.TextQuery(text=M.TextQueryInput(query=t, scoring=M.Bm25Scoring(bm25=M.Bm25Params(k=1.2, b=0.75))))  # noqa: E731

    def hybrid_req(t, v, limit=10):
        return dict(prefetch=[M.Prefetch(query=v.tolist(), using="dense", filter=emma, limit=R.POOL, params=sp),
                              M.Prefetch(query=bm25(t), using="text", filter=emma, limit=R.POOL)],
                    query=M.RrfQuery(rrf=M.Rrf(k=R.RRF_K)), query_filter=emma, limit=limit)

    def hybrid(q, t, v):
        return q.query_points(ALIAS, **hybrid_req(t, v), with_payload=["cite"])

    def timed(fn, reps):
        xs = []
        for i in range(reps):
            a = time.perf_counter()
            fn(i)
            xs.append(time.perf_counter() - a)
        return xs

    # --- kept-open REST client
    q = QdrantClient(url=URL, api_key=KEY, timeout=60)
    q.count(COLLECTION, exact=False)
    hybrid(q, texts[0], QV[0])
    out["rtt"] = _st(timed(lambda i: q.count(COLLECTION, exact=False), 30))
    out["hybrid_rest"] = _st(timed(lambda i: hybrid(q, texts[i], QV[i]), N_Q))
    out["dense_rest"] = _st(timed(lambda i: q.query_points(ALIAS, query=QV[i].tolist(), using="dense", query_filter=emma, limit=10,
                                                            search_params=sp, with_payload=["cite"]), N_Q))

    # --- the time the store itself reports for the same hybrid request (raw REST, so the reply's "time" is visible)
    F = {"must_not": [{"key": "confidential", "match": {"value": True}}]}
    hc = httpx.Client(base_url=URL.rstrip("/"), headers={"api-key": KEY}, timeout=60)

    def raw(i, mode="hybrid"):
        v = QV[i].tolist()
        if mode == "hybrid":
            body = {"prefetch": [{"query": v, "using": "dense", "filter": F, "limit": R.POOL, "params": {"hnsw_ef": EF}},
                                 {"query": {"text": texts[i]}, "using": "text", "filter": F, "limit": R.POOL}],
                    "query": {"rrf": {"k": R.RRF_K}}, "filter": F, "limit": 10, "with_payload": ["cite"]}
        else:
            body = {"query": v, "using": "dense", "filter": F, "limit": 10, "params": {"hnsw_ef": EF}, "with_payload": ["cite"]}
        r = hc.post(f"/collections/{ALIAS}/points/query", json=body)
        r.raise_for_status()
        return r.json()["time"]

    try:
        raw(0)
        srv_h, wall_h = [], []
        for i in range(N_Q):
            a = time.perf_counter()
            srv_h.append(raw(i))
            wall_h.append(time.perf_counter() - a)
        out["server_hybrid"] = _st(srv_h)
        out["hybrid_raw_http_wall"] = _st(wall_h)
        out["server_dense"] = _st([raw(i, "dense") for i in range(N_Q)])
    except Exception as e:  # noqa: BLE001
        out["errors"]["server"] = _scrub(repr(e))[:300]

    # --- a new client for every question (what a script that connects per request pays)
    def fresh(i):
        c = QdrantClient(url=URL, api_key=KEY, timeout=60)
        hybrid(c, texts[i], QV[i])
        c.close()

    def fresh_nocheck(i):
        c = QdrantClient(url=URL, api_key=KEY, timeout=60, check_compatibility=False)
        hybrid(c, texts[i], QV[i])
        c.close()

    out["reconnect_per_question"] = _st(timed(fresh, N_Q))
    try:
        out["reconnect_no_version_check"] = _st(timed(fresh_nocheck, N_Q))
    except Exception as e:  # noqa: BLE001
        out["errors"]["reconnect_no_version_check"] = _scrub(repr(e))[:300]

    # --- two searches and RRF in our code, instead of one hybrid request
    def two(i):
        d = q.query_points(ALIAS, query=QV[i].tolist(), using="dense", query_filter=emma, limit=R.POOL, search_params=sp, with_payload=False)
        b = q.query_points(ALIAS, query=bm25(texts[i]), using="text", query_filter=emma, limit=R.POOL, with_payload=False)
        f = R.rrf([[p.id for p in d.points], [p.id for p in b.points]])
        return sorted(f, key=lambda k: -f[k])[:10]

    out["two_calls_client_rrf"] = _st(timed(two, N_Q))
    agree = 0
    for i in range(N_Q):
        a = [p.id for p in hybrid(q, texts[i], QV[i]).points]
        agree += int(a[:10] == two(i))
    out["two_calls_same_top10_as_server_rrf"] = f"{agree}/{N_Q}"

    # --- ten questions: one after another vs one batch call
    def seq10(i):
        for j in range(10):
            hybrid(q, texts[(10 * i + j) % N_Q], QV[(10 * i + j) % N_Q])

    def batch10(i):
        reqs = [M.QueryRequest(**{("filter" if k == "query_filter" else k): v for k, v in hybrid_req(texts[(10 * i + j) % N_Q], QV[(10 * i + j) % N_Q]).items()},
                               with_payload=["cite"]) for j in range(10)]
        q.query_batch_points(ALIAS, requests=reqs)

    try:
        batch10(0)
        out["ten_questions_sequential"] = _st(timed(seq10, 5))
        out["ten_questions_one_batch"] = _st(timed(batch10, 5))
    except Exception as e:  # noqa: BLE001
        out["errors"]["batch"] = _scrub(repr(e))[:300]

    # --- gRPC instead of REST (port 6334 on Qdrant Cloud)
    try:
        g = QdrantClient(url=URL, api_key=KEY, timeout=60, prefer_grpc=True)
        g.count(COLLECTION, exact=False)
        hybrid(g, texts[0], QV[0])
        out["rtt_grpc"] = _st(timed(lambda i: g.count(COLLECTION, exact=False), 30))
        out["hybrid_grpc"] = _st(timed(lambda i: hybrid(g, texts[i], QV[i]), N_Q))
        g.close()
    except Exception as e:  # noqa: BLE001
        out["errors"]["grpc"] = _scrub(repr(e))[:300]

    # --- the answer model: gemini-3.8-flash from the top 5 of Emma's question
    try:
        ev = emb.query(EMMA)
        top = q.query_points(ALIAS, **hybrid_req(EMMA, ev, limit=5), with_payload=["cite", "text"]).points
        ctx = "\n\n".join(f"[{p.payload['cite']}]\n{p.payload['text']}" for p in top)
        gc = httpx.Client(timeout=120, headers={"Authorization": "Bearer " + os.environ["GEMINI_API_KEY"]})
        lat, toks = [], []
        for _ in range(5):
            a = time.perf_counter()
            r = gc.post("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                        json={"model": "gemini-3.8-flash", "messages": [{"role": "system", "content": ANSWER_SYSTEM},
                                                                         {"role": "user", "content": f"Extracts:\n{ctx}\n\nQuestion: {EMMA}"}],
                              "max_tokens": 400})
            r.raise_for_status()
            lat.append(time.perf_counter() - a)
            u = r.json().get("usage") or {}
            toks.append([u.get("prompt_tokens"), u.get("completion_tokens")])
        out["answer_model"] = {"model": "gemini-3.8-flash (Google API, OpenAI-compatible endpoint)", **_st(lat), "tokens_in_out": toks,
                               "answer_last": r.json()["choices"][0]["message"]["content"][:600]}
    except Exception as e:  # noqa: BLE001
        out["errors"]["answer_model"] = _scrub(repr(e))[:300]

    if with_facts:
        out["facts"] = facts(q, M, emb, R, C)
    q.close()
    return out


def facts(q, M, emb, R, C) -> dict:
    """Read-only facts for the metadata and filter slides."""
    f = {}
    try:
        fr = q.facet(COLLECTION, key="status", limit=50, exact=True)
        f["status_values"] = [{"value": h.value, "count": h.count} for h in fr.hits]
    except Exception as e:  # noqa: BLE001
        f["status_values_error"] = _scrub(repr(e))[:300]
    cnt = lambda flt: q.count(COLLECTION, exact=True, count_filter=flt).count  # noqa: E731
    is_ = lambda k, v: M.FieldCondition(key=k, match=M.MatchValue(value=v))  # noqa: E731
    f["counts"] = {"all": cnt(None), "superseded": cnt(M.Filter(must=[is_("superseded", True)])),
                   "future": cnt(M.Filter(must=[is_("future", True)])), "confidential": cnt(M.Filter(must=[is_("confidential", True)]))}
    f["superseded_docs"] = sorted({(p.payload.get("doc_id"), p.payload.get("version"), p.payload.get("file"))
                                   for p in q.scroll(COLLECTION, scroll_filter=M.Filter(must=[is_("superseded", True)]), limit=1000,
                                                     with_payload=["doc_id", "version", "file"])[0]})[:40]
    keys = ["doc_id", "title", "version", "effective", "status", "superseded", "future", "confidential", "audience", "file", "cite"]
    for pid in (106, 192):
        p = q.retrieve(COLLECTION, ids=[pid], with_payload=keys)[0]
        f[f"point_{pid}"] = {"id": p.id, **{k: p.payload.get(k) for k in keys}}

    # Q-605: one question, three limits in the dump; with and without the superseded filter (Emma's role: PUR-EXEC)
    qs = {x["id"]: x for x in C.questions(pathlib.Path("/dump"), "documentation")}
    x = qs["Q-605"]
    v = emb.query(x["question"])
    no_hr = M.FieldCondition(key="confidential", match=M.MatchValue(value=True))
    flt = {"emma": M.Filter(must_not=[no_hr]),
           "emma_current": M.Filter(must_not=[no_hr, is_("superseded", True)]),
           "emma_in_force": M.Filter(must_not=[no_hr, is_("superseded", True), is_("future", True)])}
    W = ["cite", "file", "doc_id", "version", "status", "superseded", "future", "confidential", "text"]
    rows = lambda r: [{"id": p.id, "score": round(float(p.score), 4), **{k: p.payload.get(k) for k in W}} for p in r.points]  # noqa: E731
    bm = M.TextQuery(text=M.TextQueryInput(query=x["question"], scoring=M.Bm25Scoring(bm25=M.Bm25Params(k=1.2, b=0.75))))
    demo = {"id": "Q-605", "question": x["question"], "role": C.role_of(x), "reference_answer": x.get("reference_answer")}
    for name, ff in flt.items():
        d = q.query_points(ALIAS, query=v.tolist(), using="dense", query_filter=ff, limit=5, search_params=M.SearchParams(hnsw_ef=EF), with_payload=W)
        b = q.query_points(ALIAS, query=bm, using="text", query_filter=ff, limit=5, with_payload=W)
        h = q.query_points(ALIAS, prefetch=[M.Prefetch(query=v.tolist(), using="dense", filter=ff, limit=R.POOL, params=M.SearchParams(hnsw_ef=EF)),
                                            M.Prefetch(query=bm, using="text", filter=ff, limit=R.POOL)],
                           query=M.RrfQuery(rrf=M.Rrf(k=R.RRF_K)), query_filter=ff, limit=5, with_payload=W)
        demo[name] = {"dense": rows(d), "bm25": rows(b), "hybrid": rows(h)}
    f["q605"] = demo

    # HNSW at the default width vs exact, overlap of the top 10, on our 224 questions (no filter, as the dashboard's check)
    allq = list(qs.values())
    V = emb.queries([y["question"] for y in allq])
    ov = {"default": [], f"hnsw_ef_{EF}": []}
    for vv in V:
        ex = {p.id for p in q.query_points(COLLECTION, query=vv.tolist(), using="dense", limit=10, search_params=M.SearchParams(exact=True)).points}
        for name, spp in (("default", None), (f"hnsw_ef_{EF}", M.SearchParams(hnsw_ef=EF))):
            got = {p.id for p in q.query_points(COLLECTION, query=vv.tolist(), using="dense", limit=10, search_params=spp).points}
            ov[name].append(len(ex & got) / 10)
    f["overlap_at_10_vs_exact"] = {k: {"n": len(x_), "mean": round(sum(x_) / len(x_), 4),
                                       "share_below_0.5": round(sum(1 for y in x_ if y < 0.5) / len(x_), 4)} for k, x_ in ov.items()}
    return f


@app.function(secrets=[secret], cpu=4, memory=8192, timeout=3600)
def run_default() -> dict:
    return measure(with_facts=False)


@app.function(secrets=[secret], cpu=4, memory=8192, timeout=3600, region="eu")
def run_eu() -> dict:
    return measure(with_facts=True)


@app.local_entrypoint()
def main():
    if not all(_c.get(k) for k in ("QDRANT_URL", "QDRANT_API_KEY", "GEMINI_API_KEY")):
        raise SystemExit("credentials missing")
    a, b = run_default.spawn(), run_eu.spawn()
    res = {"what": __doc__.split("\n\n")[0], "script": "experiments/v5_store_latency.py",
           "reranker_from_log": "logs/v5_lexical_rerank_latency.json (bge-reranker-base over 20 candidates)",
           "default_region": a.get(), "eu": b.get()}
    s = json.dumps(res, indent=1, ensure_ascii=False, default=str)
    host = _c["QDRANT_URL"].split("//")[-1].split(":")[0].split("/")[0]
    for v in list(_c.values()) + [host]:
        assert v not in s, "credential in log"
    (LOGS / "v5_store_latency.json").write_text(s)
    print("wrote", LOGS / "v5_store_latency.json")
    for k in ("default_region", "eu"):
        r = res[k]
        print(k, r["modal_region"], r["modal_cloud"], "errors:", list(r["errors"]))
        for m in ("embed", "rtt", "server_hybrid", "server_dense", "hybrid_rest", "hybrid_raw_http_wall", "dense_rest", "reconnect_per_question",
                  "reconnect_no_version_check", "two_calls_client_rrf", "ten_questions_sequential", "ten_questions_one_batch", "rtt_grpc", "hybrid_grpc", "answer_model"):
            if m in r:
                print(f"  {m:28s} p50 {r[m].get('p50')}  p95 {r[m].get('p95')}")
        print("  two calls same top10:", r.get("two_calls_same_top10_as_server_rrf"))


def suite() -> dict:
    """Second pass (same 30 questions): every round-trip lever on gRPC as well as REST, with the same payload on every
    call, so the REST-in-region extra wait seen in the first pass is separated from the levers themselves."""
    sys.path.insert(0, "/course/ledgerline")
    from qdrant_client import QdrantClient, models as M
    from ledgerline.course.l3 import corpus as C, rag as R

    URL, KEY = os.environ["QDRANT_URL"], os.environ["QDRANT_API_KEY"]
    qs = sorted(C.questions(pathlib.Path("/dump"), "documentation"), key=lambda x: x["id"])[:N_Q]
    texts = [x["question"] for x in qs]
    emb = R.Embedder("bge-small")
    QV = list(emb.queries(texts))
    emma = M.Filter(must_not=[M.FieldCondition(key="confidential", match=M.MatchValue(value=True))])
    sp = M.SearchParams(hnsw_ef=EF)
    bm25 = lambda t: M.TextQuery(text=M.TextQueryInput(query=t, scoring=M.Bm25Scoring(bm25=M.Bm25Params(k=1.2, b=0.75))))  # noqa: E731
    out = {"date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "modal_region": os.environ.get("MODAL_REGION"),
           "modal_cloud": os.environ.get("MODAL_CLOUD_PROVIDER"), "errors": {}}

    def req(i, payload):
        return dict(prefetch=[M.Prefetch(query=QV[i].tolist(), using="dense", filter=emma, limit=R.POOL, params=sp),
                              M.Prefetch(query=bm25(texts[i]), using="text", filter=emma, limit=R.POOL)],
                    query=M.RrfQuery(rrf=M.Rrf(k=R.RRF_K)), query_filter=emma, limit=10, with_payload=payload)

    def timed(fn, reps):
        xs = []
        for i in range(reps):
            a = time.perf_counter()
            fn(i)
            xs.append(time.perf_counter() - a)
        return _st(xs)

    for kind, grpc in (("rest", False), ("grpc", True)):
        try:
            mk = lambda: QdrantClient(url=URL, api_key=KEY, timeout=60, prefer_grpc=grpc)  # noqa: E731
            q = mk()
            q.count(COLLECTION, exact=False)
            q.query_points(ALIAS, **req(0, ["cite"]))
            r = {"rtt": timed(lambda i: q.count(COLLECTION, exact=False), 30),
                 "hybrid_payload_cite": timed(lambda i: q.query_points(ALIAS, **req(i, ["cite"])), N_Q),
                 "hybrid_no_payload": timed(lambda i: q.query_points(ALIAS, **req(i, False)), N_Q)}

            def fresh(i):
                c = mk()
                c.query_points(ALIAS, **req(i, ["cite"]))
                c.close()

            def two(i):
                d = q.query_points(ALIAS, query=QV[i].tolist(), using="dense", query_filter=emma, limit=R.POOL, search_params=sp, with_payload=["cite"])
                b = q.query_points(ALIAS, query=bm25(texts[i]), using="text", query_filter=emma, limit=R.POOL, with_payload=["cite"])
                f = R.rrf([[p.id for p in d.points], [p.id for p in b.points]])
                return sorted(f, key=lambda k: -f[k])[:10]

            def seq10(i):
                for j in range(10):
                    q.query_points(ALIAS, **req((10 * i + j) % N_Q, ["cite"]))

            def batch10(i):
                q.query_batch_points(ALIAS, requests=[M.QueryRequest(**{("filter" if k == "query_filter" else k): v
                                                                         for k, v in req((10 * i + j) % N_Q, ["cite"]).items()}) for j in range(10)])

            r["reconnect_per_question"] = timed(fresh, N_Q)
            r["two_calls_client_rrf"] = timed(two, N_Q)
            batch10(0)
            r["ten_sequential"] = timed(seq10, 5)
            r["ten_one_batch"] = timed(batch10, 5)
            q.close()
            out[kind] = r
        except Exception as e:  # noqa: BLE001
            out["errors"][kind] = _scrub(repr(e))[:300]
    return out


@app.function(secrets=[secret], cpu=4, memory=8192, timeout=3600)
def suite_default() -> dict:
    return suite()


@app.function(secrets=[secret], cpu=4, memory=8192, timeout=3600, region="eu")
def suite_eu() -> dict:
    return suite()


@app.local_entrypoint()
def levers():
    """Adds suite_default / suite_eu to logs/v5_store_latency.json (keeps the first pass)."""
    a, b = suite_default.spawn(), suite_eu.spawn()
    p = LOGS / "v5_store_latency.json"
    res = json.loads(p.read_text())
    res["suite_default_region"], res["suite_eu"] = a.get(), b.get()
    s = json.dumps(res, indent=1, ensure_ascii=False, default=str)
    host = _c["QDRANT_URL"].split("//")[-1].split(":")[0].split("/")[0]
    for v in list(_c.values()) + [host]:
        assert v not in s, "credential in log"
    p.write_text(s)
    for k in ("suite_default_region", "suite_eu"):
        r = res[k]
        print(k, r["modal_region"], r["modal_cloud"], "errors:", r["errors"])
        for kind in ("rest", "grpc"):
            for m, v in (r.get(kind) or {}).items():
                print(f"  {kind:4s} {m:24s} p50 {v['p50']}  p95 {v['p95']}")


def _facts_only() -> dict:
    sys.path.insert(0, "/course/ledgerline")
    from qdrant_client import QdrantClient, models as M
    from ledgerline.course.l3 import corpus as C, rag as R

    q = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"], timeout=60)
    return facts(q, M, R.Embedder("bge-small"), R, C)


@app.function(secrets=[secret], cpu=4, memory=8192, timeout=3600, region="eu")
def facts_eu() -> dict:
    return _facts_only()


@app.local_entrypoint()
def refresh_facts():
    """Re-reads the read-only facts (now with each Q-605 hit's text) into eu.facts of logs/v5_store_latency.json."""
    p = LOGS / "v5_store_latency.json"
    res = json.loads(p.read_text())
    res["eu"]["facts"] = facts_eu.remote()
    s = json.dumps(res, indent=1, ensure_ascii=False, default=str)
    host = _c["QDRANT_URL"].split("//")[-1].split(":")[0].split("/")[0]
    for v in list(_c.values()) + [host]:
        assert v not in s, "credential in log"
    p.write_text(s)
    print("facts refreshed", list(res["eu"]["facts"]))
