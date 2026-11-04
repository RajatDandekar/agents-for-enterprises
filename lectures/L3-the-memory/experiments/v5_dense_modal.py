"""Lecture 3 v5, section `dense`: dense retrieval taught on one document and one question, every number computed here.

    M=/Users/raj/.venv/bin/modal; E=lectures/L3-the-memory/experiments/v5_dense_modal.py
    MODAL_PROFILE=rajatworkspace $M run $E            # pass 1 -> logs/v5_dense.json, v5_dense_scan.json, v5/dense_img/*.png
    MODAL_PROFILE=rajatworkspace $M run $E::probes    # pass 2 -> logs/v5_dense_probes.json (failure-case details)

Everything uses the course code (ledgerline/course/l3/corpus.py and rag.py), so chunk ids, citations, vectors and
cosines are the ones NB3 and the RAG Lab compute:
  * Document D (POL-PUR-001 v4.1): structured parse; its 4 pages rendered to PNG with every text line's box (for the
    highlight slides); the default chunks (structure-aware, 200 tokens, 15% overlap, header prefix).
  * The selected chunk (the one holding §6.2) through bge-small-en-v1.5: its real WordPiece pieces, the per-token
    vectors, the pooling the model really uses (read from the sentence-transformers modules), the 384 numbers.
  * PCA to 3 components of D's chunk vectors (fit once, on the default chunking), Emma's question projected with the
    same PCA; cosines in the full 384 dimensions.
  * The playground: sizes 50/100/200/400/800, one chunk per parsed section, the whole document; overlap 0 and 15%;
    header prefix off; the other four models in rag.EMBED_MODELS. For each: points, ranks of §6.2 and §6.4, tokens the
    top-k carries and how much of it is the answer, and what the 512-WordPiece limit cuts off.
  * MAN-ERR-72 with Q-0412 (exact codes), in the document and in the whole dump.
  * The whole dump (the grid's structured-structure-200-o15 chunks and stored bge-small vectors on the RAG Lab volume):
    exact dense and BM25 rankings for all 224 documentation questions, to pick the failure cases from.
No LLM calls.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
LOGS = HERE / "logs"
V5 = HERE.parent / "v5"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app"}

D = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
ERR = "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf"
CID = "structured-structure-200-o15"
Q_EMMA = "Can I buy the battery packs from Brightcell Energy? They quote £104."
GPU = "L4"
MACHINE = f"Modal {GPU} GPU container, 4 vCPU, 16 GiB"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pillow==11.0.0", "numpy<2.1", "scipy", "httpx", "pydantic>=2", "pandas",
                 "torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops")
    .env({"HF_HOME": "/hf"})
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"",
                  "python -c \"from sentence_transformers import SentenceTransformer as S; "
                  "[S(m, trust_remote_code=True) for m in ['BAAI/bge-small-en-v1.5','BAAI/bge-base-en-v1.5',"
                  "'intfloat/e5-small-v2','thenlper/gte-small','nomic-ai/nomic-embed-text-v1.5']]\"")
    .env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
          "NB_L3_CACHE": "/tmp/l3cache", "TOKENIZERS_PARALLELISM": "false"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
    .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
)
app = modal.App("l3-v5-dense", image=image)
vol = modal.Volume.from_name("northbridge-raglab")


# ----------------------------------------------------------------------------------------------- helpers (remote)
def _r(x, n=4):
    return round(float(x), n)


def _render(rel: str, pages: list[int] | None, res: int = 110) -> tuple[dict, list]:
    """PNG of each page and every text line with its box (PDF points, top-left origin)."""
    import io

    import pdfplumber

    files, info = {}, []
    with pdfplumber.open(f"/dump/{rel}") as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            if pages and pno not in pages:
                continue
            im = page.to_image(resolution=res).original
            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
            tag = "D" if rel == D else "ERR"
            files[f"dense_img/{tag}_p{pno}.png"] = buf.getvalue()
            lines = [{"text": L["text"], "x0": _r(L["x0"], 1), "top": _r(L["top"], 1), "x1": _r(L["x1"], 1),
                      "bottom": _r(L["bottom"], 1)} for L in page.extract_text_lines(return_chars=False)]
            info.append({"page": pno, "img": f"dense_img/{tag}_p{pno}.png", "w": _r(page.width, 1),
                         "h": _r(page.height, 1), "px_w": im.width, "px_h": im.height, "lines": lines})
    return files, info


def _clause_spans(stream: str) -> dict:
    """Character spans of §6.2 and §6.4 in the document's unit stream (each clause runs to the next clause)."""
    out = {}
    for key, start, nxt in (("6.2", r"\n6\.2 ", r"\n6\.3 "), ("6.4", r"\n6\.4 ", r"\n7\. ")):
        a = re.search(start, stream)
        b = re.search(nxt, stream[a.end():]) if a else None
        if a:
            out[key] = [a.start() + 1, a.end() + (b.start() if b else len(stream) - a.end())]
    return out


def _span(stream: str, body: str, hint: int = 0) -> list[int]:
    i = stream.find(body, max(0, hint - 400))
    if i < 0:
        i = stream.find(body)
    if i < 0:
        i = stream.find(body[:80])
    return [i, i + len(body)] if i >= 0 else [-1, -1]


def _wp(tok, text: str) -> dict:
    """WordPiece count and, when over the 512 limit, how much of the text the model reads."""
    enc = tok(text, add_special_tokens=True, truncation=False, return_offsets_mapping=True)
    n = len(enc["input_ids"])
    seen = len(text)
    if n > 512:
        offs = enc["offset_mapping"]
        seen = int(offs[510][1])  # [CLS] + 510 pieces + [SEP]
    return {"wp": n, "truncated": n > 512, "seen_chars": seen}


def _config(units, emb, tok, Q, facts, size=None, overlap=0.0, mode="structure", context=None, pca=None):
    """Chunk D one way, embed with emb, rank for Q. Returns the record the playground draws."""
    import numpy as np

    from ledgerline.course.l3 import corpus as C, evaluate as E

    rel = units[0].file
    if mode == "section":
        chunks = []
        for i, u in enumerate(units):
            c = C.chunk([u], "structure", 10 ** 6, 0.0, context=context)[0]
            c.cid = f"{rel}#u{i}"
            chunks.append(c)
    elif mode == "whole":
        chunks = C.chunk(units, "structure", 10 ** 6, 0.0, context=context)
    else:
        chunks = C.chunk(units, "structure", size, overlap, context=context)
    stream = "\n".join(u.text for u in units)
    spans = _clause_spans(stream)
    V = emb.passages([c.text for c in chunks])
    q = emb.query(Q)
    cos = V @ q
    order = [int(i) for i in np.argsort(-cos)]
    rank = {i: r for r, i in enumerate(order, 1)}
    recs, hint = [], 0
    for i, c in enumerate(chunks):
        sp = _span(stream, c.body, hint)
        hint = max(hint, sp[0])
        w = _wp(tok, c.text)
        head_len = len(c.text) - len(c.body)
        rec = {"i": i, "cid": c.cid, "cite": c.cite, "header": c.text[:head_len].strip(), "body": c.body,
               "tokens": c.n_tokens, "body_tokens": C.n_tokens(c.body), **w,
               "body_seen_chars": max(0, min(len(c.body), w["seen_chars"] - head_len)),
               "span": sp, "cos": _r(cos[i]), "rank": rank[i],
               "has62": E.contains_fact(c.body, facts["F-PUR-6.2"]), "has64": E.contains_fact(c.body, facts["F-PUR-6.4"]),
               "sections": c.locs.get("sections", []), "pages": c.locs.get("pages", [])}
        # how much of each clause this chunk holds (characters of the clause inside the chunk's span)
        for k, (a, b) in spans.items():
            ov = max(0, min(b, sp[1]) - max(a, sp[0])) if sp[0] >= 0 else 0
            rec["part" + k.replace(".", "")] = _r(ov / (b - a), 3)
        if pca is not None:
            rec["xyz"] = [_r(x, 4) for x in (V[i] - pca["mean"]) @ pca["comp"].T]
        recs.append(rec)
    qxyz = [_r(x, 4) for x in (q - pca["mean"]) @ pca["comp"].T] if pca is not None else None
    # top-k: tokens into the prompt (bodies, as evaluate.render_sources sends them) and how much of that is §6.2/§6.4
    clause_tokens = {k: C.n_tokens(stream[a:b]) for k, (a, b) in spans.items()}
    topk = []
    for k in range(1, min(10, len(chunks)) + 1):
        sel = [recs[i] for i in order[:k]]
        toks = sum(r["body_tokens"] for r in sel)
        ans = 0.0
        for key, (a, b) in spans.items():
            covered = [0] * (b - a)
            for r in sel:
                s0, s1 = r["span"]
                for p in range(max(a, s0), min(b, s1)):
                    covered[p - a] = 1
            ans += clause_tokens[key] * sum(covered) / (b - a)
        topk.append({"k": k, "tokens": toks, "answer_tokens": _r(ans, 1),
                     "has62": any(r["part62"] >= 0.99 for r in sel), "has64": any(r["part64"] >= 0.99 for r in sel)})
    first = lambda key: min([r["rank"] for r in recs if r[key]] or [None], key=lambda x: x or 10 ** 9)  # noqa: E731
    return {"n": len(chunks), "tokens_mean": _r(sum(r["tokens"] for r in recs) / len(recs), 1),
            "rank62": first("has62"), "rank64": first("has64"), "clause_tokens": clause_tokens,
            "chunks": recs, "q": {"xyz": qxyz}, "topk": topk, "order": order[:10], "V": V, "qv": q}


@app.function(gpu=GPU, cpu=4, memory=16384, timeout=3600, volumes={"/vol": vol})
def dense() -> dict:
    import gzip
    import pickle

    import numpy as np

    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    t0 = time.time()
    G = E.Golden("/dump")
    facts = G.facts
    files, out = {}, {"generated": time.strftime("%Y-%m-%d %H:%M"), "machine": MACHINE, "doc": D,
                      "question": Q_EMMA, "chunking_default": CID, "models": R.EMBED_MODELS}

    # ---------------------------------------------------------------- D: parse, render, units
    units = C.parse_file("/dump", D, "structured")
    f, pages = _render(D, None)
    files.update(f)
    out["pages"] = pages
    out["units"] = [{"uid": u.uid, "kind": u.kind, "heading": u.heading, "loc": u.loc, "text": u.text,
                     "tokens": C.n_tokens(u.text)} for u in units]
    out["doc_tokens"] = sum(C.n_tokens(u.text) for u in units)
    out["meta"] = {k: units[0].meta.get(k) for k in ("doc_id", "title", "version", "effective", "status",
                                                      "classification", "superseded", "future")}
    out["facts"] = {k: facts[k] for k in ("F-PUR-6.2", "F-PUR-6.4")}

    # ---------------------------------------------------------------- the model, as the course loads it
    emb = R.Embedder("bge-small")
    m = emb.m
    tok = m.tokenizer
    mods = [type(x).__name__ for x in m]
    pool = m[1]
    out["model_info"] = {"hf": R.EMBED_MODELS["bge-small"]["hf"], "modules": mods,
                         "pooling": pool.get_pooling_mode_str(), "max_seq_length": m.max_seq_length,
                         "dim": m.get_sentence_embedding_dimension(), "vocab": tok.vocab_size,
                         "query_prefix": R.EMBED_MODELS["bge-small"]["q"], "device": str(m.device),
                         "dtype": str(next(m.parameters()).dtype)}

    # ---------------------------------------------------------------- default chunking + PCA basis
    base = _config(units, emb, tok, Q_EMMA, facts, 200, 0.15)
    V0 = base["V"]
    mu = V0.mean(0)
    _, S, Vt = np.linalg.svd(V0 - mu, full_matrices=False)
    var = S ** 2 / (S ** 2).sum()
    pca = {"mean": mu, "comp": Vt[:3]}
    out["pca"] = {"fit_on": "the default chunks of D (structure-aware, 200 tokens, 15% overlap, header prefix), bge-small",
                  "explained": [_r(v, 4) for v in var[:10]], "explained3": _r(var[:3].sum(), 4), "n": int(len(V0))}

    configs = {}
    for size in (50, 100, 200, 400, 800):
        for ov in (0.0, 0.15):
            configs[f"s{size}-o{int(ov * 100)}"] = dict(size=size, overlap=ov)
    configs["section"] = dict(mode="section")
    configs["whole"] = dict(mode="whole")
    configs["s200-o15-nohead"] = dict(size=200, overlap=0.15, context=False)
    play = {}
    for name, kw in configs.items():
        r = _config(units, emb, tok, Q_EMMA, facts, pca=pca, **kw)
        r.pop("V")
        r.pop("qv")
        play[name] = r
    out["play"] = play
    out["pca"]["q_xyz"] = play["s200-o15"]["q"]["xyz"]

    # the selected chunk: the default chunk that holds the §6.2 sentence
    sel = next(r for r in play["s200-o15"]["chunks"] if r["has62"])
    chunks0 = C.chunk(units, "structure", 200, 0.15)
    c = chunks0[sel["i"]]
    enc = tok(c.text, add_special_tokens=True, truncation=True, max_length=512)
    pieces = tok.convert_ids_to_tokens(enc["input_ids"])
    te = m.encode([c.text], output_value="token_embeddings", convert_to_numpy=False, show_progress_bar=False)[0]
    te = te.float().cpu().numpy()
    final = emb.passages([c.text])[0]
    cls_n = te[0] / np.linalg.norm(te[0])
    mean_n = te.mean(0) / np.linalg.norm(te.mean(0))
    qenc = tok(R.EMBED_MODELS["bge-small"]["q"] + Q_EMMA)
    qv = emb.query(Q_EMMA)
    qv_noprefix = emb.m.encode([Q_EMMA], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)[0]
    out["selected"] = {
        "i": sel["i"], "cid": c.cid, "cite": c.cite, "text": c.text, "o200k_tokens": c.n_tokens,
        "pieces": pieces, "ids": enc["input_ids"], "n_pieces": len(pieces),
        "token_vectors_shape": list(te.shape),
        "token_vectors_head": [[_r(x, 3) for x in te[i, :8]] for i in range(min(10, len(te)))],
        "token_norms_head": [_r(np.linalg.norm(te[i]), 3) for i in range(min(10, len(te)))],
        "cls_raw_head": [_r(x, 4) for x in te[0, :8]], "cls_norm": _r(np.linalg.norm(te[0]), 4),
        "vector": [_r(x, 4) for x in final], "vector_norm": _r(np.linalg.norm(final), 5),
        "cos_final_vs_cls": _r(float(final @ cls_n), 5), "cos_final_vs_mean": _r(float(final @ mean_n), 5),
        "query_pieces": tok.convert_ids_to_tokens(qenc["input_ids"]),
        "query_vector": [_r(x, 4) for x in qv], "cos_q": _r(float(final @ qv), 4),
        "cos_q_noprefix": _r(float(final @ qv_noprefix), 4),
    }
    # the query with and without bge's instruction prefix: rank of §6.2 / §6.4 either way
    V0n = V0
    for name, vec in (("prefix", qv), ("noprefix", qv_noprefix)):
        cs = V0n @ vec
        order = list(np.argsort(-cs))
        out.setdefault("prefix_check", {})[name] = {
            "rank62": 1 + min(order.index(r["i"]) for r in play["s200-o15"]["chunks"] if r["has62"]),
            "rank64": 1 + min(order.index(r["i"]) for r in play["s200-o15"]["chunks"] if r["has64"]),
            "top3": [[int(i), _r(cs[i])] for i in order[:3]]}

    # ---------------------------------------------------------------- the other embedding models, default chunking
    others = {}
    for mname in R.EMBED_MODELS:
        e2 = R.Embedder(mname)
        tok2 = e2.m.tokenizer
        r0 = _config(units, e2, tok2, Q_EMMA, facts, 200, 0.15)
        V2 = r0.pop("V")
        r0.pop("qv")
        mu2 = V2.mean(0)
        _, S2, Vt2 = np.linalg.svd(V2 - mu2, full_matrices=False)
        var2 = S2 ** 2 / (S2 ** 2).sum()
        r2 = _config(units, e2, tok2, Q_EMMA, facts, 200, 0.15, pca={"mean": mu2, "comp": Vt2[:3]})
        r2.pop("V")
        r2.pop("qv")
        r2["explained3"] = _r(var2[:3].sum(), 4)
        r2["dim"] = int(V2.shape[1])
        r2["cos_spread"] = {"max": max(c_["cos"] for c_ in r2["chunks"]), "min": min(c_["cos"] for c_ in r2["chunks"])}
        others[mname] = r2
    out["models_play"] = others
    emb = R.Embedder("bge-small")

    # ---------------------------------------------------------------- MAN-ERR-72 + Q-0412
    q0412 = G.by_id["Q-0412"]
    eu = C.parse_file("/dump", ERR, "structured")
    ech = C.chunk(eu, "structure", 200, 0.15)
    EV = emb.passages([c.text for c in ech])
    eq = emb.query(q0412["question"])
    ecos = EV @ eq
    eorder = [int(i) for i in np.argsort(-ecos)]
    emu = EV.mean(0)
    _, ES, EVt = np.linalg.svd(EV - emu, full_matrices=False)
    evar = ES ** 2 / (ES ** 2).sum()
    code_re = re.compile(r"\b(?:ERR|W|I)-[A-Z]{2,4}-\d{3,4}\b")
    erecs = []
    for i, c in enumerate(ech):
        erecs.append({"i": i, "cid": c.cid, "cite": c.cite, "body": c.body[:1200], "tokens": c.n_tokens,
                      "cos": _r(ecos[i]), "rank": eorder.index(i) + 1,
                      "codes": sorted(set(code_re.findall(c.body)))[:12],
                      "gold": E.contains_fact(c.body, facts["F-ERR-0412"]) or "ERR-PO-0412" in c.body,
                      "fact": E.contains_fact(c.body, facts["F-ERR-0412"]),
                      "xyz": [_r(x, 4) for x in (EV[i] - emu) @ EVt[:3].T]})
    gold_pages = sorted({p for r in erecs if "ERR-PO-0412" in r["body"] for p in ech[r["i"]].locs.get("pages", [])})
    f, epages = _render(ERR, gold_pages[:2], res=100)
    files.update(f)
    out["err"] = {"doc": ERR, "question": q0412["question"], "n_units": len(eu), "n": len(ech),
                  "explained3": _r(evar[:3].sum(), 4), "q_xyz": [_r(x, 4) for x in (eq - emu) @ EVt[:3].T],
                  "chunks": erecs, "order": eorder[:10], "pages": epages,
                  "units_head": [{"heading": u.heading, "loc": u.loc, "text": u.text[:300]} for u in eu[:6]]}

    # ---------------------------------------------------------------- the whole dump: every documentation question
    croot = pathlib.Path(f"/vol/chroma/{CID}")
    chunks = R.load_chunks(croot / "chunks.jsonl.gz")
    V = np.load(f"/vol/vec/{CID}/bge-small.npy").astype(np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-12
    bm = pickle.loads((croot / "bm25.pkl").read_bytes())
    assert len(chunks) == V.shape[0], (len(chunks), V.shape)
    # consistency: the dump's chunks of D are the chunks we made from D alone, and their stored vectors match ours
    dumpD = [i for i, c in enumerate(chunks) if c.file == D]
    same_text = [chunks[i].text for i in dumpD] == [c.text for c in chunks0]
    cos_same = [float(V[i] @ V0[j]) for j, i in enumerate(dumpD)] if same_text else []
    out["dump_check"] = {"n_chunks": len(chunks), "D_chunks_in_dump": len(dumpD), "same_text": same_text,
                         "stored_vs_fresh_cos_min": _r(min(cos_same), 5) if cos_same else None}
    conf = np.array([bool(c.meta.get("confidential")) for c in chunks])
    by_file = {}
    for i, c in enumerate(chunks):
        by_file.setdefault(c.file, []).append(i)
    qs = G.qs
    QV = emb.queries([q["question"] for q in qs])
    SD = V @ QV.T

    def item(i, s, golds, gf, kind):
        c = chunks[i]
        return {"i": int(i), "cid": c.cid, "cite": c.cite, "file": c.file, "score": _r(s, 4 if kind == "d" else 3),
                "gold": any(E.loc_match(G, g, c.file, c.locs) for g in golds),
                "fact": any(E.contains_fact(c.body, fa) for fa in gf),
                "superseded": bool(c.meta.get("superseded")), "future": bool(c.meta.get("future")),
                "text": c.body[:220]}

    scan = []
    for j, q in enumerate(qs):
        role = C.role_of(q)
        allowed = np.ones(len(chunks), bool) if role in C.HR_ROLES else ~conf
        golds = G.gold(q) if G.expected(q) == "answer" else []
        gf = G.gold_facts(q)
        cand = sorted({i for g in golds for f_ in by_file for i in by_file[f_] if G.same_file(f_, g["file"])})
        gold_idx = [i for i in cand if any(E.loc_match(G, g, chunks[i].file, chunks[i].locs) for g in golds)]
        fact_idx = [i for i in cand if any(E.contains_fact(chunks[i].body, fa) for fa in gf)]
        sd = np.where(allowed, SD[:, j], -9.0)
        sb = np.where(allowed, bm.scores(q["question"]), -1.0)
        od = np.argsort(-sd)
        ob = np.argsort(-sb)
        rd = np.empty(len(chunks), int)
        rd[od] = np.arange(1, len(chunks) + 1)
        rb = np.empty(len(chunks), int)
        rb[ob] = np.arange(1, len(chunks) + 1)
        best = lambda idx, rr: int(min(rr[i] for i in idx)) if idx else None  # noqa: E731
        # inside the first gold file only: where its fact chunk ranks among that document's chunks
        in_doc = None
        if golds:
            gfile = golds[0]["file"]
            ids = [i for f_ in by_file if G.same_file(f_, gfile) for i in by_file[f_]]
            dd = sorted(ids, key=lambda i: -sd[i])
            fx = [i for i in ids if any(E.contains_fact(chunks[i].body, fa) for fa in gf)] or \
                 [i for i in ids if any(E.loc_match(G, g, chunks[i].file, chunks[i].locs) for g in golds)]
            in_doc = {"file": gfile, "n": len(ids), "rank": (1 + min(dd.index(i) for i in fx)) if fx else None,
                      "top": [[chunks[i].cid, _r(sd[i])] for i in dd[:5]]}
        scan.append({"id": q["id"], "type": q.get("type"), "question": q["question"], "role": role,
                     "gold_files": sorted({g["file"] for g in golds}),
                     "gold_cids": [chunks[i].cid for i in gold_idx][:30], "fact_cids": [chunks[i].cid for i in fact_idx][:30],
                     "dense_rank": best(gold_idx, rd), "dense_fact_rank": best(fact_idx, rd),
                     "bm25_rank": best(gold_idx, rb), "bm25_fact_rank": best(fact_idx, rb),
                     "dense_top10": [item(i, sd[i], golds, gf, "d") for i in od[:10]],
                     "bm25_top10": [item(i, sb[i], golds, gf, "b") for i in ob[:10] if sb[i] > 0],
                     "in_doc": in_doc})
    out["wall_s"] = _r(time.time() - t0, 1)
    scan_out = {"generated": out["generated"], "chunking": CID, "model": "bge-small",
                "note": "exact search (numpy dot product over all 28,953 stored vectors), not HNSW; permission filter "
                        "before ranking as rag.Retriever; gold = evaluate.loc_match (file + page/row), fact = a gold fact's "
                        "needles in the chunk body; ranks are 1-based over the whole dump",
                "questions": scan}
    return {"files": files, "out": out, "scan": scan_out}


@app.local_entrypoint()
def main():
    import numpy as np  # noqa: F401

    res = dense.remote()
    for rel, data in res["files"].items():
        p = V5 / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print("wrote", p)
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "v5_dense.json").write_text(json.dumps(res["out"], indent=1, ensure_ascii=False))
    (LOGS / "v5_dense_scan.json").write_text(json.dumps(res["scan"], indent=1, ensure_ascii=False))
    print("wrote logs/v5_dense.json, logs/v5_dense_scan.json; wall", res["out"]["wall_s"], "s")


# ================================================================================ pass 2: the failure cases, probed
PROBES = {
    # one real sentence of D, then edited copies: how far does the vector move?
    "negation": {"base": "The certificate must be uploaded and checked before the first order is placed.",
                 "edits": {"after": "The certificate must be uploaded and checked after the first order is placed.",
                           "need not": "The certificate need not be uploaded or checked before the first order is placed.",
                           "unrelated (D §8.1)": "A supplier in the UK is charged UK VAT (tax codes ending -UK)."},
                 "query_id": "Q-612"},
    "numbers": {"base": "A direct purchase order without a request is allowed only when its gross value, including VAT, is £50,000 or less.",
                "edits": {"£25,000": "A direct purchase order without a request is allowed only when its gross value, including VAT, is £25,000 or less.",
                          "£30,000": "A direct purchase order without a request is allowed only when its gross value, including VAT, is £30,000 or less.",
                          "£5,000,000": "A direct purchase order without a request is allowed only when its gross value, including VAT, is £5,000,000 or less.",
                          "unrelated (D §8.1)": "A supplier in the UK is charged UK VAT (tax codes ending -UK)."},
                "query_id": "Q-510"},
    "codes": {"base": "ERR-PO-0412",
              "edits": {"ERR-PO-0413": "ERR-PO-0413", "ERR-MAT-0412": "ERR-MAT-0412", "ERR-PO-0610": "ERR-PO-0610",
                        "BAT-500": "BAT-500", "its meaning": "TAX CODE DOES NOT MATCH SUPPLIER COUNTRY"},
              "query_id": "Q-0412"},
}
CASES = ["Q-0412", "Q-510", "Q-401", "Q-424", "Q-612", "Q-202", "Q-003", "Q-101", "Q-606", "Q-EMMA"]


@app.function(gpu=GPU, cpu=4, memory=16384, timeout=3600, volumes={"/vol": vol})
def probe() -> dict:
    import pickle

    import numpy as np

    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    G = E.Golden("/dump")
    emb = R.Embedder("bge-small")
    cfgm = emb.m[0].auto_model.config
    out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "machine": MACHINE,
           "model_config": {"layers": cfgm.num_hidden_layers, "heads": cfgm.num_attention_heads, "hidden": cfgm.hidden_size,
                            "intermediate": cfgm.intermediate_size, "vocab": cfgm.vocab_size, "arch": cfgm.architectures}}
    files = {}
    f, pages = _render(D, None, res=200)
    files.update(f)
    out["pages_D"] = pages
    f, pages = _render(ERR, [17, 18], res=170)
    files.update(f)
    out["pages_ERR"] = pages

    # ---- sentence probes: passages embedded as passages, the question as a query (rag.Embedder)
    pr = {}
    for name, p in PROBES.items():
        texts = [p["base"]] + list(p["edits"].values())
        V = emb.passages(texts)
        q = G.by_id[p["query_id"]]["question"]
        qv = emb.query(q)
        pr[name] = {"base": p["base"], "question": q,
                    "rows": [{"label": "original" if i == 0 else list(p["edits"])[i - 1], "text": t,
                              "cos_to_original": _r(V[0] @ V[i]), "cos_to_question": _r(qv @ V[i])}
                             for i, t in enumerate(texts)]}
    out["probes"] = pr

    # ---- the whole dump again, for the failure cases
    croot = pathlib.Path(f"/vol/chroma/{CID}")
    chunks = R.load_chunks(croot / "chunks.jsonl.gz")
    V = np.load(f"/vol/vec/{CID}/bge-small.npy").astype(np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-12
    bm = pickle.loads((croot / "bm25.pkl").read_bytes())
    conf = np.array([bool(c.meta.get("confidential")) for c in chunks])
    stale = np.array([bool(c.meta.get("superseded") or c.meta.get("future")) for c in chunks])
    cid_i = {c.cid: i for i, c in enumerate(chunks)}
    by_file = {}
    for i, c in enumerate(chunks):
        by_file.setdefault(c.file, []).append(i)
    cases = {}
    for qid in CASES:
        q = G.by_id[qid]
        golds = G.gold(q)
        gf = G.gold_facts(q)
        qv = emb.query(q["question"])
        allowed = ~conf
        sd = np.where(allowed, V @ qv, -9.0)
        sb = np.where(allowed, bm.scores(q["question"]), -1.0)
        od = np.argsort(-sd)
        rd = np.empty(len(chunks), int)
        rd[od] = np.arange(1, len(chunks) + 1)
        ob = np.argsort(-sb)
        rb = np.empty(len(chunks), int)
        rb[ob] = np.arange(1, len(chunks) + 1)
        gfiles = sorted({g["file"] for g in golds})
        cand = sorted({i for g in golds for f_ in by_file if G.same_file(f_, g["file"]) for i in by_file[f_]})
        fact_i = [i for i in cand if any(E.contains_fact(chunks[i].body, fa) for fa in gf)]
        gold_i = [i for i in cand if any(E.loc_match(G, g, chunks[i].file, chunks[i].locs) for g in golds)]
        # with superseded / not-yet-in-force chunks filtered out before ranking (a metadata filter)
        sdf = np.where(allowed & ~stale, V @ qv, -9.0)
        odf = np.argsort(-sdf)
        rdf = np.empty(len(chunks), int)
        rdf[odf] = np.arange(1, len(chunks) + 1)

        def row(i, s, rr):
            c = chunks[i]
            return {"i": int(i), "cid": c.cid, "cite": c.cite, "file": c.file, "score": _r(s), "rank": int(rr[i]),
                    "gold": i in gold_i, "fact": i in fact_i, "superseded": bool(c.meta.get("superseded")),
                    "future": bool(c.meta.get("future")), "header": c.text[:len(c.text) - len(c.body)].strip(),
                    "text": c.body[:600]}

        per_doc = {}
        for gfile in gfiles:
            ids = [i for f_ in by_file if G.same_file(f_, gfile) for i in by_file[f_]]
            dd = sorted(ids, key=lambda i: -sd[i])
            per_doc[gfile] = {"n": len(ids), "top10": [[chunks[i].cid, _r(sd[i])] for i in dd[:10]],
                              "fact_ranks": [[chunks[i].cid, 1 + dd.index(i)] for i in ids if i in fact_i]}
        cases[qid] = {"id": qid, "type": q.get("type"), "question": q["question"], "gold_files": gfiles,
                      "fact_chunks": [row(i, sd[i], rd) for i in fact_i][:12],
                      "gold_chunks": [chunks[i].cid for i in gold_i][:40],
                      "dense_rank_gold": int(min(rd[i] for i in gold_i)) if gold_i else None,
                      "dense_rank_fact": int(min(rd[i] for i in fact_i)) if fact_i else None,
                      "bm25_rank_gold": int(min(rb[i] for i in gold_i)) if gold_i else None,
                      "bm25_rank_fact": int(min(rb[i] for i in fact_i)) if fact_i else None,
                      "dense_top10": [row(i, sd[i], rd) for i in od[:10]],
                      "bm25_top5": [row(i, sb[i], rb) for i in ob[:5] if sb[i] > 0],
                      "dense_filtered_rank_fact": int(min(rdf[i] for i in fact_i if not stale[i])) if [i for i in fact_i if not stale[i]] else None,
                      "dense_filtered_top5": [row(i, sdf[i], rdf) for i in odf[:5]],
                      "in_doc": per_doc}
    out["cases"] = cases

    # ---- Q-202: the superseded copies of §3.3 against the current one
    def find(file_sub, needle):
        return [i for i, c in enumerate(chunks) if file_sub in c.file and needle in c.body]
    cur = find("POL-PUR-001_Purchase_Policy_v4.1", "3.3 A direct purchase order")
    old = find("purchase_policy_v3_2019", "3.3 A direct purchase order") + find("Purchase Policy v4.0", "3.3 A direct purchase order")
    out["versions"] = {"current": [{"cid": chunks[i].cid, "cite": chunks[i].cite, "header": chunks[i].text[:len(chunks[i].text) - len(chunks[i].body)].strip(), "text": chunks[i].body[:500]} for i in cur],
                       "old": [{"cid": chunks[i].cid, "cite": chunks[i].cite, "superseded": bool(chunks[i].meta.get("superseded")),
                                "header": chunks[i].text[:len(chunks[i].text) - len(chunks[i].body)].strip(), "text": chunks[i].body[:500],
                                "cos_to_current": [_r(V[i] @ V[j]) for j in cur]} for i in old]}

    # ---- Q-401 / Q-424: the BAT item rows, and the plain parser's version of the same rows (no column names)
    def rowchunk(file_sub, code):
        return [i for i, c in enumerate(chunks) if file_sub in c.file and re.search(rf"(?<![A-Z0-9-]){re.escape(code)}(?![0-9A-Z-])", c.body)]
    sib = {}
    for code in ("BAT-500", "BAT-375", "BAT-625", "BAT-250"):
        ids = rowchunk("ITEM_MASTER_2026-10-26", code)
        sib[code] = [{"cid": chunks[i].cid, "cite": chunks[i].cite, "text": chunks[i].body[:400]} for i in ids[:2]]
    a = rowchunk("ITEM_MASTER_2026-10-26", "BAT-500")[:1]
    sim = {}
    for code in ("BAT-375", "BAT-625", "BAT-250"):
        b = rowchunk("ITEM_MASTER_2026-10-26", code)[:1]
        if a and b:
            sim[code] = _r(V[a[0]] @ V[b[0]])
    out["siblings"] = {"rows": sib, "cos_BAT500_row_to": sim}
    # the plain parser (rows without column names), from the grid's plain-structure-200-o15 index on the volume
    pid = "plain-structure-200-o15"
    pch = R.load_chunks(pathlib.Path(f"/vol/chroma/{pid}") / "chunks.jsonl.gz")
    PV = np.load(f"/vol/vec/{pid}/bge-small.npy").astype(np.float32)
    PV /= np.linalg.norm(PV, axis=1, keepdims=True) + 1e-12
    pconf = np.array([bool(c.meta.get("confidential")) for c in pch])
    tables = {}
    for qid in ("Q-401", "Q-403", "Q-407", "Q-423"):
        q = G.by_id[qid]
        golds = G.gold(q)
        qv = emb.query(q["question"])
        res = {}
        for name, CH, VV, cf in (("structured", chunks, V, conf), ("plain", pch, PV, pconf)):
            s = np.where(~cf, VV @ qv, -9.0)
            o = np.argsort(-s)
            rr = np.empty(len(CH), int)
            rr[o] = np.arange(1, len(CH) + 1)
            gi = [i for i, c in enumerate(CH) if any(E.loc_match(G, g, c.file, c.locs) == "row" for g in golds)]
            best = min(gi, key=lambda i: rr[i]) if gi else None
            res[name] = {"n": len(CH), "rank": int(rr[best]) if best is not None else None,
                         "cos": _r(s[best]) if best is not None else None, "cite": CH[best].cite if best is not None else None,
                         "text": CH[best].text[:500] if best is not None else None}
        tables[qid] = {"question": q["question"], **res}
    out["tables"] = tables

    # ---- Q-003: how crowded the battery topic is
    q = G.by_id["Q-003"]
    qv = emb.query(q["question"])
    s = np.where(~conf, V @ qv, -9.0)
    gi = [i for i, c in enumerate(chunks) if any(E.contains_fact(c.body, fa) for fa in G.gold_facts(q))]
    gcos = max(float(s[i]) for i in gi) if gi else None
    bat = [i for i, c in enumerate(chunks) if re.search(r"(?i)lithium|battery|batteries", c.body)]
    out["crowd"] = {"question": q["question"], "n_chunks": len(chunks), "n_battery_chunks": len(bat),
                    "gold_cos": _r(gcos) if gcos else None,
                    "n_above_gold": int((s > gcos).sum()) if gcos else None,
                    "n_battery_above_gold": int(sum(1 for i in bat if s[i] > gcos)) if gcos else None,
                    "gold": [{"cid": chunks[i].cid, "cite": chunks[i].cite, "cos": _r(s[i]), "text": chunks[i].body[:400]} for i in gi]}
    return {"files": files, "out": out}


@app.local_entrypoint()
def probes():
    res = probe.remote()
    for rel, data in res["files"].items():
        p = V5 / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print("wrote", p)
    (LOGS / "v5_dense_probes.json").write_text(json.dumps(res["out"], indent=1, ensure_ascii=False))
    print("wrote logs/v5_dense_probes.json")


PIECE_STRINGS = ["ERR-PO-0412", "ERR-PO-0413", "ERR-MAT-0412", "BAT-500", "BAT-375", "£50,000", "£40,000", "UN 38.3",
                 "What does ERR-PO-0412 mean and how do I fix it?"]


@app.function(cpu=2, memory=4096, timeout=600)
def pieces() -> dict:
    from ledgerline.course.l3 import rag as R

    tok = R.Embedder("bge-small").m.tokenizer
    return {s: tok.convert_ids_to_tokens(tok(s)["input_ids"]) for s in PIECE_STRINGS}


@app.local_entrypoint()
def wordpieces():
    p = LOGS / "v5_dense_probes.json"
    d = json.loads(p.read_text())
    d["wordpieces"] = pieces.remote()
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print(json.dumps(d["wordpieces"], ensure_ascii=False))
