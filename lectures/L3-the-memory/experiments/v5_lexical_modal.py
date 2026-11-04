"""L3 v5, section `lexical`: BM25, hybrid (RRF) and the reranker, taught on one document and one question.

    export MODAL_PROFILE=rajatworkspace; M=/Users/raj/.venv/bin/modal; E=lectures/L3-the-memory/experiments/v5_lexical_modal.py
    $M run $E::scout          # D's chunks (default chunking) and Q's tokens, printed: to read before designing slides
    $M run $E                 # everything -> logs/v5_lexical.json (+ v5_lexical_rerank_latency.json)

Running example (v5/SPEC.md): D = POL-PUR-001 Purchase Policy v4.1, Q = Emma's question (Q-EMMA). Second document for
codes: MAN-ERR-72, question Q-0412. Default chunking: structured parser, structure-aware, 200 tokens, 15% overlap, header
prefix: the RAG Lab's index on the volume `northbridge-raglab` (/rvol/chroma/structured-structure-200-o15/chunks.jsonl.gz,
28,953 chunks), whose chunks of D are exactly corpus.chunk(parse_file(D), "structure", 200, 0.15) (checked below).

Every number comes from the course code: rag.tokenize, rag.BM25 (k1 = 1.2, b = 0.75), rag.rrf (k = 60), rag.Embedder
("bge-small" = BAAI/bge-small-en-v1.5) and rag.Reranker (BAAI/bge-reranker-base). No LLM calls.
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
LOGS = HERE / "logs"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app", "pages", "restricted"}

D = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
ERRDOC = "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf"
CHUNKING = "structured-structure-200-o15"

base = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pillow==11.0.0", "numpy<2.1", "scipy", "httpx", "pydantic>=2")
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
)
gpu_image = (
    base.pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops")
    .env({"HF_HOME": "/hf"})
    .run_commands("python -c \"from sentence_transformers import SentenceTransformer as S, CrossEncoder as C; "
                  "S('BAAI/bge-small-en-v1.5'); C('BAAI/bge-reranker-base')\"")
)


def _mount(img):
    return (img.env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
                     "NB_L3_CACHE": "/tmp/l3cache", "TOKENIZERS_PARALLELISM": "false"})
            .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                           ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
            .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts))


cpu_img = _mount(base)
gpu_img = _mount(gpu_image)
app = modal.App("l3-v5-lexical")
rvol = modal.Volume.from_name("northbridge-raglab")


def _load_all():
    from ledgerline.course.l3 import rag

    return rag.load_chunks(f"/rvol/chroma/{CHUNKING}/chunks.jsonl.gz")


@app.function(image=cpu_img, timeout=900, cpu=2, memory=8192, volumes={"/rvol": rvol})
def scout() -> dict:
    from ledgerline.course.l3 import corpus as C
    from ledgerline.course.l3 import rag

    allc = _load_all()
    dch = [c for c in allc if c.file == D]
    mine = C.chunk(C.parse_file(pathlib.Path("/dump"), D, parser="structured"), "structure", 200, 0.15)
    same = [a.text == b.text for a, b in zip(dch, mine)]
    q = [q for q in C.questions("/dump") if q["id"] in ("Q-EMMA", "Q-0412")]
    return {"n_all": len(allc), "n_D": len(dch), "n_mine": len(mine), "same": all(same) and len(dch) == len(mine),
            "D": [{"cid": c.cid, "cite": c.cite, "n_tokens": c.n_tokens, "text": c.text, "toks": rag.tokenize(c.text)} for c in dch],
            "Q": [{"id": x["id"], "q": x["question"], "toks": rag.tokenize(x["question"])} for x in q]}


@app.local_entrypoint()
def scout_main():
    d = scout.remote()
    (LOGS / "v5_lexical_scout.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print(d["n_all"], d["n_D"], d["n_mine"], d["same"])
    for x in d["Q"]:
        print(x)


# =============================================================================== the main run
Q_IDS = ("Q-EMMA", "Q-0412")
EXTRA_TERMS = ["purchase", "policy", "order", "supplier", "ledgerline", "lithium-cell", "certificate", "un", "38.3",
               "bought", "buys", "quotation", "cheaper", "err-po-0412", "err", "po", "0412", "bat-500", "voltway"]


def _trace(text):
    """rag.tokenize, step by step (the same regex, stop list and stemmer), checked against rag.tokenize."""
    import re

    from ledgerline.course.l3 import rag

    raw = re.findall(r"[a-z0-9£]+(?:[.\-/_][a-z0-9]+)*", (text or "").lower())
    rows = []
    for t in raw:
        if t in rag.STOP:
            rows.append({"word": t, "stop": True})
            continue
        r = {"word": t, "stop": False, "token": rag._stem(t)}
        if any(c in t for c in "-/_."):
            r["parts"] = [rag._stem(p) for p in re.split(r"[-/_.]", t) if len(p) > 1 and p not in rag.STOP]
        rows.append(r)
    flat = [x for r in rows if not r["stop"] for x in [r["token"], *r.get("parts", [])]]
    assert flat == rag.tokenize(text), (flat, rag.tokenize(text))
    return {"text": text, "lower": (text or "").lower(), "rows": rows, "tokens": flat}


def _bm25_detail(bm, q, i, texts):
    """Per-term pieces of BM25(q, chunk i) from the built matrix: tf, |d|, idf, weight (= W[i, term])."""
    from ledgerline.course.l3 import rag

    toks = rag.tokenize(texts[i])
    dl = len(toks)
    out = []
    for t in dict.fromkeys(rag.tokenize(q)):
        j = bm.vocab.get(t)
        tf = toks.count(t)
        w = float(bm.W[i, j]) if j is not None else 0.0
        out.append({"term": t, "tf": tf, "idf": round(float(bm.idf[j]), 4) if j is not None else None, "w": round(w, 4)})
    return {"dl": dl, "terms": out, "score": round(sum(x["w"] for x in out), 4)}


@app.function(image=gpu_img, gpu="L4", cpu=4, memory=16384, timeout=1800, volumes={"/rvol": rvol})
def run(cases: list | None = None) -> dict:
    import numpy as np

    from ledgerline.course.l3 import corpus as C
    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    qs = {i: G.by_id[i] for i in Q_IDS}
    Q = qs["Q-EMMA"]["question"]
    allc = _load_all()
    texts = [c.text for c in allc]
    conf = np.array([bool(c.meta.get("confidential")) for c in allc])
    allowed = ~conf
    dI = [i for i, c in enumerate(allc) if c.file == D]
    dch = [allc[i] for i in dI]
    dtexts = [c.text for c in dch]
    out = {"what": "L3 v5 lexical section: BM25, RRF and the reranker on D and Q (experiments/v5_lexical_modal.py)",
           "chunking": CHUNKING, "n_all": len(allc), "D": D, "Q": Q, "Q_id": "Q-EMMA", "k1": 1.2, "b": 0.75, "rrf_k": rag.RRF_K}

    def facts_in(c, q):
        return [f["id"] for f in G.gold_facts(q) if E.contains_fact(c.body, f)]

    def loc_lv(c, q):
        lv = [E.loc_match(G, g, c.file, c.locs) for g in G.gold(q)]
        return next((x for x in ("page", "row", "file") if x in lv), None)

    def row(i, q, extra=None):
        c = allc[i]
        r = {"i": int(i), "cid": c.cid, "cite": c.cite, "file": c.file, "n_tokens": c.n_tokens,
             "facts": facts_in(c, q), "gold_loc": loc_lv(c, q), "body": c.body[:600]}
        r.update(extra or {})
        return r

    # ---- 1. tokenize
    out["tokenize"] = {"Q": _trace(Q), "Q0412": _trace(qs["Q-0412"]["question"]),
                       "clause": _trace("6.2 Lithium-cell parts (battery packs, hub motors, chargers ...) may be bought only "
                                        "from a supplier holding a valid UN 38.3 certificate")}
    qterms = list(dict.fromkeys(rag.tokenize(Q)))
    out["D_chunks"] = [{"k": k, "cid": c.cid, "cite": c.cite, "heading": (c.text.split("\n")[1] if "\n" in c.text else ""),
                        "n_tokens": c.n_tokens, "dl": len(rag.tokenize(c.text)), "text": c.text,
                        "facts": facts_in(c, qs["Q-EMMA"])} for k, c in enumerate(dch)]
    # ---- term x chunk counts on D
    dtoks = [rag.tokenize(t) for t in dtexts]
    out["tf_D"] = {t: [tk.count(t) for tk in dtoks] for t in qterms + EXTRA_TERMS}
    # ---- 2. df and idf: D alone and the whole dump
    bmD = rag.BM25(dtexts)
    bmA = rag.BM25(texts)
    allt = [rag.tokenize(t) for t in texts]
    dfA = {}
    for t in qterms + EXTRA_TERMS:
        dfA[t] = sum(1 for tk in allt if t in tk)
    out["df"] = {t: {"df_D": sum(1 for tk in dtoks if t in tk), "n_D": len(dtoks),
                     "idf_D": round(float(bmD.idf[bmD.vocab[t]]), 4) if t in bmD.vocab else None,
                     "df_all": dfA[t], "n_all": len(texts),
                     "idf_all": round(float(bmA.idf[bmA.vocab[t]]), 4) if t in bmA.vocab else None}
                 for t in qterms + EXTRA_TERMS}
    out["avgdl"] = {"D": round(float(np.mean([len(x) for x in dtoks])), 3), "all": round(float(np.mean([len(x) for x in allt])), 3)}
    # ---- 4. BM25 of Q on D: per-term table for every chunk
    sD = bmD.scores(Q)
    orderD = [int(i) for i in np.argsort(-sD, kind="stable")]
    out["bm25_D"] = [{"k": k, "rank": orderD.index(k) + 1, **_bm25_detail(bmD, Q, k, dtexts)} for k in range(len(dch))]
    assert all(abs(x["score"] - float(sD[x["k"]])) < 1e-3 for x in out["bm25_D"])
    # Q-0412 on MAN-ERR-72 alone
    eI = [i for i, c in enumerate(allc) if c.file == ERRDOC]
    etexts = [allc[i].text for i in eI]
    bmE = rag.BM25(etexts)
    q412 = qs["Q-0412"]["question"]
    sE = bmE.scores(q412)
    oE = [int(i) for i in np.argsort(-sE, kind="stable")][:5]
    out["bm25_err"] = {"n": len(eI), "top": [row(eI[k], qs["Q-0412"], {"rank": r + 1, **_bm25_detail(bmE, q412, k, etexts)})
                                            for r, k in enumerate(oE)]}
    # ---- whole dump: BM25 for Q and for Q-0412 (permission mask as Emma, PUR-EXEC)
    def bm_all(q, n=20):
        return bmA.search(q, n, allowed)

    out["bm25_all"] = {}
    for qid, q in qs.items():
        top = bm_all(q["question"], 20)
        out["bm25_all"][qid] = [row(i, q, {"rank": r + 1, "score": round(s, 4), **_bm25_detail(bmA, q["question"], i, texts)})
                                for r, (i, s) in enumerate(top)]
        s = bmA.scores(q["question"])
        s = np.where(allowed, s, -1.0)
        o = np.argsort(-s, kind="stable")
        pos = {int(i): r + 1 for r, i in enumerate(o)}
        if qid == "Q-EMMA":
            out["bm25_all"]["Q-EMMA_D_ranks"] = {allc[i].cid: pos[i] for i in dI}
    # ---- dense: bge-small, exact cosine (Chroma's HNSW returns 99.9% of these, logs/hnsw_check.json)
    emb = rag.Embedder("bge-small")
    V = np.load(f"/rvol/vec/{CHUNKING}/bge-small.npy").astype(np.float32)
    vD = emb.passages(dtexts)
    out["vec_check"] = {"rows": int(V.shape[0]), "dim": int(V.shape[1]),
                        "min_cos_stored_vs_fresh_D": round(float(np.min(np.sum(V[dI] * vD, axis=1))), 5)}
    qv = emb.query(Q)
    cD = vD @ qv
    oD = [int(i) for i in np.argsort(-cD, kind="stable")]
    out["dense_D"] = [{"k": k, "cos": round(float(cD[k]), 4), "rank": oD.index(k) + 1} for k in range(len(dch))]

    def dense_all(q, n=20):
        s = V @ emb.query(q)
        s = np.where(allowed, s, -9.0)
        top = np.argpartition(-s, n)[:n]
        top = top[np.argsort(-s[top])]
        return [(int(i), float(s[i])) for i in top], s

    out["dense_all"] = {}
    for qid, q in qs.items():
        top, s = dense_all(q["question"])
        out["dense_all"][qid] = [row(i, q, {"rank": r + 1, "cos": round(sc, 4)}) for r, (i, sc) in enumerate(top)]
        if qid == "Q-EMMA":
            o = np.argsort(-s, kind="stable")
            pos = {int(i): r + 1 for r, i in enumerate(o)}
            out["dense_all"]["Q-EMMA_D_ranks"] = {allc[i].cid: pos[i] for i in dI}
    # ---- 6. hybrid: RRF of the two lists. On D (all 15 chunks ranked by each) and on the dump (top 20 each, as rag.Retriever)
    lD = [orderD, oD]
    fD = rag.rrf(lD)
    fo = sorted(fD, key=lambda i: -fD[i])
    out["rrf_D"] = [{"k": k, "bm25_rank": orderD.index(k) + 1, "dense_rank": oD.index(k) + 1, "rrf": round(fD[k], 6),
                     "fused_rank": fo.index(k) + 1} for k in range(len(dch))]
    out["rrf_D_by_k"] = {str(kk): [sorted(rag.rrf(lD, kk), key=lambda i: -rag.rrf(lD, kk)[i]).index(k) + 1 for k in range(len(dch))]
                         for kk in (1, 5, 10, 30, 60, 100, 1000)}
    out["hybrid_all"] = {}
    for qid, q in qs.items():
        bl = [i for i, _ in bm_all(q["question"], rag.POOL)]
        dl_ = [i for i, _ in dense_all(q["question"], rag.POOL)[0]]
        f = rag.rrf([dl_, bl])
        o = sorted(f, key=lambda i: -f[i])[:rag.POOL]
        out["hybrid_all"][qid] = [row(i, q, {"rank": r + 1, "rrf": round(f[i], 6),
                                             "dense_rank": dl_.index(i) + 1 if i in dl_ else None,
                                             "bm25_rank": bl.index(i) + 1 if i in bl else None}) for r, i in enumerate(o)]
    # ---- 7. the reranker over the top 20 BM25 candidates (the default pipeline) and over D's 15 chunks
    rr = rag.Reranker()
    m = rr.m
    out["models"] = {"reranker": rag.RERANK_MODEL, "reranker_params": int(sum(p.numel() for p in m.model.parameters())),
                     "reranker_arch": type(m.model).__name__, "reranker_max_len": 512,
                     "embedder": rag.EMBED_MODELS["bge-small"]["hf"], "embedder_params": int(sum(p.numel() for p in emb.m.parameters())),
                     "activation": type(getattr(m, "default_activation_function", None) or getattr(m, "activation_fct", None)).__name__}
    enc = m.tokenizer(Q, dch[5].text, truncation=True, max_length=512)
    out["pair_tokens"] = {"n": len(enc["input_ids"]), "first": m.tokenizer.convert_ids_to_tokens(enc["input_ids"][:40]),
                          "q_tokens": len(m.tokenizer(Q)["input_ids"]), "chunk": dch[5].cid}
    out["rerank"] = {}
    for qid, q in qs.items():
        cand = [i for i, _ in bm_all(q["question"], rag.POOL)]
        sc = rr.score(q["question"], [texts[i] for i in cand])
        raw = [float(x) for x in m.predict([(q["question"], texts[i]) for i in cand], batch_size=32, show_progress_bar=False,
                                           activation_fct=__import__("torch").nn.Identity())]
        after = sorted(range(len(cand)), key=lambda j: -sc[j])
        out["rerank"][qid] = [row(cand[j], q, {"before": j + 1, "after": after.index(j) + 1, "score": round(sc[j], 5),
                                               "logit": round(raw[j], 4)}) for j in range(len(cand))]
        # gold ranks through the pipelines (evaluate.gold_hits on each list, top 10)
    scD = rr.score(Q, dtexts)
    oR = sorted(range(len(dch)), key=lambda k: -scD[k])
    out["rerank_D"] = [{"k": k, "score": round(scD[k], 5), "rank": oR.index(k) + 1} for k in range(len(dch))]
    # ---- the default pipeline, end to end, through rag.Retriever (BM25 top 20 -> reranker -> k 10), as the RAG Lab runs it
    idx = rag.Index(pathlib.Path("/tmp/none"), allc)
    idx._bm25 = bmA
    ret = rag.Retriever(idx, rag.Config.from_id("structured-structure-200-o15|-|bm25|rr1|qr0|k10"))
    out["pipeline"] = {}
    for qid, q in qs.items():
        res = ret.search(q["question"], role="PUR-EXEC")
        out["pipeline"][qid] = {"items": [{"rank": it["rank"], "cite": it["cite"], "score": it["score"], "bm25": it["bm25"]} for it in res["items"]],
                                "gold": E.gold_hits(q, res["items"], G)}
    for name, key in (("bm25", "bm25_all"), ("dense", "dense_all"), ("hybrid", "hybrid_all")):
        for qid, q in qs.items():
            items = [allc[r["i"]].as_item() for r in out[key][qid][:10]]
            out.setdefault("gold_ranks", {}).setdefault(qid, {})[name] = E.gold_hits(q, items, G)
    # ---- GPU latency of the reranker over the 20 candidates (warm), and of BM25 + dense query
    cand = [texts[i] for i, _ in bm_all(Q, rag.POOL)]
    out["latency_gpu"] = _lat(rr, Q, cand, bmA, emb, allowed)
    # ---- optional: failure cases from the dense section (scored here by BM25 and dense, same code)
    if cases:
        out["cases"] = _cases(cases, allc, texts, allowed, bmA, dense_all, G, row)
    return out


def _lat(rr, Q, cand, bm, emb, allowed, n=40):
    import numpy as np
    import torch

    def t(fn):
        for _ in range(5):
            fn()
        xs = []
        for _ in range(n):
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            a = time.perf_counter()
            fn()
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            xs.append(time.perf_counter() - a)
        return {"p50_ms": round(1000 * float(np.percentile(xs, 50)), 2), "p95_ms": round(1000 * float(np.percentile(xs, 95)), 2), "n": n}

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    out = {"device": dev, "torch_threads": torch.get_num_threads(),
           "gpu": torch.cuda.get_device_name(0) if dev == "cuda" else None,
           "rerank_20": t(lambda: rr.score(Q, cand)),
           "rerank_1": t(lambda: rr.score(Q, cand[:1])),
           "bm25_query": t(lambda: bm.search(Q, 20, allowed))}
    if emb is not None:
        out["embed_query"] = t(lambda: emb.query(Q))
    return out


@app.function(image=gpu_img, cpu=4, memory=16384, timeout=1800, volumes={"/rvol": rvol})
def latency_cpu() -> dict:
    """The reranker over the same 20 candidates on a CPU container (4 vCPU), no GPU."""
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    Q = G.by_id["Q-EMMA"]["question"]
    allc = _load_all()
    texts = [c.text for c in allc]
    allowed = ~np.array([bool(c.meta.get("confidential")) for c in allc])
    bm = rag.BM25(texts)
    cand = [texts[i] for i, _ in bm.search(Q, rag.POOL, allowed)]
    rr = rag.Reranker()
    emb = rag.Embedder("bge-small")
    return {"machine": "Modal CPU container, 4 vCPU, 16 GiB", **_lat(rr, Q, cand, bm, emb, allowed, n=15)}


def _cases(cases, allc, texts, allowed, bmA, dense_all, G, row):
    """Each case: {"id", "question", optional "gold_cids"}. Ranks of the first gold chunk (gold_cids if given, else the
    golden set's gold sources for that question id) under BM25 and dense over the whole dump."""
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    cid2i = {c.cid: i for i, c in enumerate(allc)}
    res = []
    for cs in cases:
        q = cs["question"]
        gq = G.by_id.get(cs.get("qid") or cs.get("id"))
        if cs.get("gold_cids"):
            gold = {cid2i[c] for c in cs["gold_cids"] if c in cid2i}
        elif gq:  # as the dense section (v5_dense_modal.py): chunks of the gold files that contain a gold fact
            gfiles = {g["file"] for g in G.gold(gq)}
            gold = {i for i, c in enumerate(allc) if any(G.same_file(c.file, f) for f in gfiles)
                    and any(E.contains_fact(c.body, f) for f in G.gold_facts(gq))}
        else:
            gold = set()
        sb = np.where(allowed, bmA.scores(q), -1.0)
        ob = np.argsort(-sb, kind="stable")
        _, sd = dense_all(q)
        od = np.argsort(-sd, kind="stable")
        rb = next((r + 1 for r, i in enumerate(ob) if int(i) in gold), None)
        rd = next((r + 1 for r, i in enumerate(od) if int(i) in gold), None)
        gi = min(gold, key=lambda i: int(np.where(ob == i)[0][0])) if gold else None
        idf = {t: (round(float(bmA.idf[bmA.vocab[t]]), 3) if t in bmA.vocab else None) for t in dict.fromkeys(rag.tokenize(q))}
        detail = _bm25_detail(bmA, q, gi, texts) if gi is not None else None
        res.append({**{k: v for k, v in cs.items() if k != "gold_cids"}, "tokens": rag.tokenize(q), "n_gold": len(gold),
                    "idf": idf, "gold_best": allc[gi].cite if gi is not None else None, "gold_terms": detail,
                    "bm25_top1_score": round(float(sb[ob[0]]), 3),
                    "bm25_rank": rb, "dense_rank": rd,
                    "bm25_top3": [allc[int(i)].cite for i in ob[:3]], "dense_top3": [allc[int(i)].cite for i in od[:3]],
                    "gold_cites": [allc[i].cite for i in sorted(gold)][:4]})
    return res


@app.local_entrypoint()
def main(cases_only: bool = False):
    import subprocess

    fail = LOGS / "v5_dense_failures.json"
    cases = None
    if fail.exists():
        d = json.loads(fail.read_text())
        cases = d.get("cases") if isinstance(d, dict) else d
        print("dense failure cases:", len(cases or []))
    h = run.spawn(cases)
    c = latency_cpu.spawn()
    out = h.get()
    out["latency_cpu"] = c.get()
    (LOGS / "v5_lexical.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (LOGS / "v5_lexical_rerank_latency.json").write_text(json.dumps({"gpu": out["latency_gpu"], "cpu": out["latency_cpu"]}, indent=1))
    print("D chunks", len(out["D_chunks"]), "vec check", out["vec_check"])
    print("BM25 on D:", sorted([(x["rank"], x["k"], x["score"]) for x in out["bm25_D"]])[:5])
    print("dense on D:", sorted([(x["rank"], x["k"], x["cos"]) for x in out["dense_D"]])[:5])
    print("gold ranks:", json.dumps(out["gold_ranks"])[:600])
    print("latency gpu", out["latency_gpu"], "cpu", out["latency_cpu"])


# =============================================================================== extra passes (logs/v5_lexical_extra.json)
def _variant(kind):
    """Two tokenizers that differ from rag.tokenize in one way only, for the "keep codes whole and split" slide."""
    import re

    from ledgerline.course.l3 import rag

    def tok(text):
        out = []
        for t in re.findall(r"[a-z0-9£]+(?:[.\-/_][a-z0-9]+)*", (text or "").lower()):
            if t in rag.STOP:
                continue
            has = any(c in t for c in "-/_.")
            if kind == "parts_only" and has:
                out.extend(rag._stem(p) for p in re.split(r"[-/_.]", t) if len(p) > 1 and p not in rag.STOP)
                continue
            out.append(rag._stem(t))
            if kind != "whole_only" and has:
                out.extend(rag._stem(p) for p in re.split(r"[-/_.]", t) if len(p) > 1 and p not in rag.STOP)
        return out
    return tok


@app.function(image=cpu_img, timeout=1800, cpu=4, memory=16384, volumes={"/rvol": rvol})
def variants() -> dict:
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    q = G.by_id["Q-0412"]
    allc = _load_all()
    allowed = ~np.array([bool(c.meta.get("confidential")) for c in allc])
    eI = [i for i, c in enumerate(allc) if c.file == ERRDOC]
    gf = G.gold_facts(q)
    gold = {i for i, c in enumerate(allc) if any(E.contains_fact(c.body, f) for f in gf)}
    goldE = [k for k, i in enumerate(eI) if allc[i].cid and any(E.contains_fact(allc[i].body, f) for f in gf if f["id"] == "F-ERR-0412")]
    queries = {"Q-0412": q["question"], "typed": "PO error 0412, what is it?"}
    orig = rag.tokenize
    out = {"gold_err_chunk": [allc[eI[k]].cite for k in goldE], "queries": queries, "runs": {}}
    for kind in ("course", "parts_only", "whole_only"):
        rag.tokenize = orig if kind == "course" else _variant(kind)
        try:
            bmE = rag.BM25([allc[i].text for i in eI])
            bmA = rag.BM25([c.text for c in allc])
            r = {}
            for name, qq in queries.items():
                sE = bmE.scores(qq)
                oE = [int(k) for k in np.argsort(-sE, kind="stable")]
                sA = np.where(allowed, bmA.scores(qq), -1.0)
                oA = [int(i) for i in np.argsort(-sA, kind="stable")]
                r[name] = {"tokens": rag.tokenize(qq),
                           "err_doc": {"gold_rank": min(oE.index(k) + 1 for k in goldE),
                                       "top3": [{"cite": allc[eI[k]].cite, "score": round(float(sE[k]), 4)} for k in oE[:3]]},
                           "dump": {"gold_rank": next(r_ + 1 for r_, i in enumerate(oA) if i in gold),
                                    "top3": [{"cite": allc[i].cite, "score": round(float(sA[i]), 4)} for i in oA[:3]]}}
            out["runs"][kind] = r
        finally:
            rag.tokenize = orig
    return out


def _gem_key():
    """The Gemini key, read on the laptop from the env file named in v5/SPEC.md and handed to Modal as a secret. Never printed."""
    env = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"
    if not modal.is_local() or not os.path.exists(env):
        return ""
    return next((l.split("=", 1)[1].strip().strip('"').strip("'") for l in open(env) if l.startswith("GEMINI_API_KEY=")), "")


LLM_PROMPT = ("Here is a question from a Northbridge Cycles employee and {n} numbered passages from the company's documents. "
              "Order the passages from most to least useful for answering the question. Reply with the passage numbers only, "
              "best first, comma-separated, all {n} of them.\n\nQuestion: {q}\n\n{p}")


@app.function(image=cpu_img, timeout=900, cpu=2, memory=8192, volumes={"/rvol": rvol},
              secrets=[modal.Secret.from_dict({"GEMINI_API_KEY": _gem_key()})])
def llm_rerank(runs: int = 3) -> dict:
    """The costlier variant: a generative LLM (gemini-3.8-flash) asked to order the same 20 BM25 candidates for Q."""
    import re

    import httpx
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    q = G.by_id["Q-EMMA"]
    allc = _load_all()
    allowed = ~np.array([bool(c.meta.get("confidential")) for c in allc])
    bm = rag.BM25([c.text for c in allc])
    cand = [i for i, _ in bm.search(q["question"], rag.POOL, allowed)]
    passages = "\n\n".join(f"[{n + 1}] {allc[i].text}" for n, i in enumerate(cand))
    prompt = LLM_PROMPT.format(n=len(cand), q=q["question"], p=passages)
    key = os.environ["GEMINI_API_KEY"]
    res = []
    for _ in range(runs):
        a = time.perf_counter()
        r = httpx.post("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                       headers={"Authorization": f"Bearer {key}"}, timeout=120,
                       json={"model": "gemini-3.8-flash", "messages": [{"role": "user", "content": prompt}]})
        secs = time.perf_counter() - a
        d = r.json()
        txt = (d.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        order = [int(x) for x in re.findall(r"\d+", txt)]
        u = d.get("usage") or {}
        res.append({"seconds": round(secs, 3), "status": r.status_code, "reply": txt[:300], "order": order,
                    "tokens_in": u.get("prompt_tokens"), "tokens_out": u.get("completion_tokens")})
    return {"model": "gemini-3.8-flash (Google Gemini API, OpenAI-compatible endpoint)", "prompt_template": LLM_PROMPT,
            "candidates": [allc[i].cite for i in cand], "runs": res}


@app.function(image=gpu_img, gpu="L4", cpu=4, memory=16384, timeout=1800, volumes={"/rvol": rvol})
def cases_run(cases: list) -> dict:
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    allc = _load_all()
    texts = [c.text for c in allc]
    allowed = ~np.array([bool(c.meta.get("confidential")) for c in allc])
    bmA = rag.BM25(texts)
    emb = rag.Embedder("bge-small")
    V = np.load(f"/rvol/vec/{CHUNKING}/bge-small.npy").astype(np.float32)

    def dense_all(q, n=20):
        s = np.where(allowed, V @ emb.query(q), -9.0)
        return None, s

    return {"cases": _cases(cases, allc, texts, allowed, bmA, dense_all, G, None)}


@app.local_entrypoint()
def cases_main(src: str = "probes"):
    """Score the dense section's failure cases with BM25 (and dense, same code) -> logs/v5_lexical_cases.json."""
    if src == "probes":
        d = json.loads((LOGS / "v5_dense_probes.json").read_text())["cases"]
        cases = [{"id": k, "qid": k, "question": v["question"], "type": v.get("type")} for k, v in d.items()]
    else:
        d = json.loads((LOGS / "v5_dense_failures.json").read_text())
        d = d.get("cases", d) if isinstance(d, dict) else d
        cases = [{"id": v.get("id") or k, "qid": v.get("id") or k, "question": v["question"], "type": v.get("type")}
                 for k, v in (d.items() if isinstance(d, dict) else enumerate(d))]
    out = cases_run.remote(cases)
    out["source"] = f"cases from logs/{'v5_dense_probes.json' if src == 'probes' else 'v5_dense_failures.json'}"
    (LOGS / "v5_lexical_cases.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for c in out["cases"]:
        print(c["id"], "bm25", c["bm25_rank"], "dense", c["dense_rank"], c["tokens"])


@app.local_entrypoint()
def extra_main(what: str = "variants,llm"):
    p = LOGS / "v5_lexical_extra.json"
    out = json.loads(p.read_text()) if p.exists() else {}
    if "variants" in what:
        out["variants"] = variants.remote()
        print(json.dumps(out["variants"], indent=1)[:3000])
    if "llm" in what:
        out["llm_rerank"] = llm_rerank.remote()
        print(json.dumps(out["llm_rerank"]["runs"], indent=1)[:2000])
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False))


@app.function(image=gpu_img, gpu="L4", cpu=4, memory=16384, timeout=1200, volumes={"/rvol": rvol})
def rr_repeat(n: int = 10) -> dict:
    """Is the cross-encoder's order the same every time? Score the same 20 candidates n times (L4 GPU, fp16)."""
    import numpy as np

    from ledgerline.course.l3 import evaluate as E
    from ledgerline.course.l3 import rag

    G = E.Golden("/dump")
    Q = G.by_id["Q-EMMA"]["question"]
    allc = _load_all()
    allowed = ~np.array([bool(c.meta.get("confidential")) for c in allc])
    bm = rag.BM25([c.text for c in allc])
    cand = [i for i, _ in bm.search(Q, rag.POOL, allowed)]
    rr = rag.Reranker()
    orders, scores = [], []
    for _ in range(n):
        s = rr.score(Q, [allc[i].text for i in cand])
        orders.append([int(j) + 1 for j in np.argsort(-np.array(s), kind="stable")])
        scores.append(s)
    sc = np.array(scores)
    return {"n": n, "same_order_every_run": all(o == orders[0] for o in orders), "order": orders[0],
            "max_score_spread": float((sc.max(0) - sc.min(0)).max())}


@app.local_entrypoint()
def rr_repeat_main():
    p = LOGS / "v5_lexical_extra.json"
    out = json.loads(p.read_text())
    out["rr_repeat"] = rr_repeat.remote()
    print(out["rr_repeat"])
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False))
