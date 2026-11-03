"""Lecture 3 v4 experiments on Modal (workspace rajatworkspace): parse, audit, paste-all, the RAG grid, answers.

    M=/Users/raj/.venv/bin/modal; E=lectures/L3-the-memory/experiments/l3_modal.py
    $M run $E::parse_check                 # parse the dump both ways, print a sample of every format
    $M run $E::audit                       # logs/audit.json
    $M run $E::paste_all                   # logs/paste_all.json (+ one labelled measured run on a sample)
    $M run $E::grid_build                  # chunk + embed + Chroma index for every grid point (GPU, spawned)
    $M run $E::grid_eval                   # retrieval metrics + latency for the grid -> logs/rag_grid.json
    $M run $E::answers --configs ...       # answers + judge for chosen configs -> logs/rag_answers_*.json, rag_best.json

Everything heavy runs here, never on the laptop. The dump is mounted at /dump (or cloned from GitHub with --clone),
the ledgerline package at /course/ledgerline. Indexes, vectors and caches live in the Volume `northbridge-raglab`
(/vol): /vol/units (parsed units), /vol/chunks/<chunking>.jsonl.gz, /vol/vec/<chunking>/<model>.npy,
/vol/chroma/<chunking> (one persistent Chroma client per chunking, one collection per embedding model).
LLM calls are recorded to cassettes (ledgerline/cassettes/L3v4_*.jsonl), copied back to the laptop by each entrypoint.
The OpenRouter key is read from the course .env and passed as a Modal secret; it is never printed.
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
DUMP = pathlib.Path(os.environ.get("NORTHBRIDGE_DOCS", "/Users/raj/Claude_Brain/northbridge-docs"))
LOGS = HERE / "logs"
CASS = COURSE / "ledgerline" / "ledgerline" / "cassettes"


def _key(name="OPENROUTER_API_KEY"):
    if not modal.is_local():
        return ""
    for line in open(COURSE / ".env"):
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app"}

base = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("tesseract-ocr", "git")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pytesseract==0.3.13", "pillow==11.0.0", "numpy<2.1", "scipy", "openai>=1.50",
                 "httpx", "pydantic>=2", "pandas")
    .run_commands("python -c \"import tiktoken; tiktoken.get_encoding('o200k_base')\"")
)
gpu_image = (
    base.pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops", "chromadb==0.6.3",
                     "scikit-learn", "umap-learn==0.5.7")
    .env({"HF_HOME": "/hf"})
    .run_commands(
        "python -c \"from sentence_transformers import SentenceTransformer as S, CrossEncoder as C; "
        "[S(m, trust_remote_code=True) for m in ['BAAI/bge-small-en-v1.5','BAAI/bge-base-en-v1.5','intfloat/e5-small-v2',"
        "'thenlper/gte-small','nomic-ai/nomic-embed-text-v1.5']]; C('BAAI/bge-reranker-base'); "
        "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct')\"")
)


def _mount(img):
    return (img.env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NORTHBRIDGE_DOCS": "/dump",
                     "NB_L3_CACHE": "/vol/cache", "LEDGER_CASSETTES": "/tmp/cassettes", "TOKENIZERS_PARALLELISM": "false"})
            .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                           ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
            .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts))


cpu_img = _mount(base)
gpu_img = _mount(gpu_image)
app = modal.App("northbridge-l3-rag")
vol = modal.Volume.from_name("northbridge-raglab", create_if_missing=True)
secret = modal.Secret.from_dict({"OPENROUTER_API_KEY": _key()}) if modal.is_local() else modal.Secret.from_dict({})


def _cassettes() -> dict:
    d = pathlib.Path("/tmp/cassettes")
    return {p.name: p.read_text() for p in d.glob("*.jsonl")} if d.exists() else {}


def _merge_cassettes(files: dict):
    for name, text in files.items():
        dst = CASS / name
        have = dst.read_text().splitlines() if dst.exists() else []
        seen = set(have)
        extra = [l for l in text.splitlines() if l and l not in seen]
        if extra:
            dst.write_text("\n".join(have + extra) + "\n")
            print(f"cassette {name}: +{len(extra)} recorded replies")


def _write_log(name: str, data):
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / name).write_text(json.dumps(data, indent=1, ensure_ascii=False, default=str))
    print("wrote", LOGS / name)


# =============================================================================== parse
@app.function(image=cpu_img, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def parse_both(force: bool = False) -> dict:
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C

    out = {}
    for parser in C.PARSERS:
        t0 = time.time()
        units = C.parse("/dump", parser=parser, cache=not force, workers=8)
        out[parser] = {"seconds": round(time.time() - t0, 1), "units": len(units), "failures": C.parse.failures,
                       "describe": C.describe(units)}
        # one sample unit per format, to eyeball
        seen = {}
        for u in units:
            if u.fmt not in seen and len(u.text) > 200:
                seen[u.fmt] = {"uid": u.uid, "loc": u.loc, "heading": u.heading, "meta": u.meta, "text": u.text[:700]}
        out[parser]["samples"] = seen
    vol.commit()
    return out


@app.local_entrypoint()
def parse_check(force: bool = False):
    r = parse_both.remote(force)
    for parser, d in r.items():
        print(f"\n######## {parser}: {d['units']} units in {d['seconds']} s, {len(d['failures'])} failures")
        print(json.dumps(d["describe"], indent=0))
        for f in d["failures"][:10]:
            print("  FAIL", f)
        for fmt, s in d["samples"].items():
            print(f"--- {fmt} {s['uid']} loc={s['loc']} heading={s['heading'][:80]!r}")
            print("    meta:", {k: s["meta"].get(k) for k in ("doc_id", "title", "version", "effective", "status", "confidential", "superseded", "future")})
            print("   ", s["text"][:500].replace("\n", "\n    "))


# =============================================================================== smoke test (BM25 only, no GPU)
@app.function(image=cpu_img, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def smoke_remote() -> dict:
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    G = E.Golden("/dump")
    out = {}
    for parser in C.PARSERS:
        units = C.parse("/dump", parser=parser)
        # facts visible through the parser: needles found in the units at the fact's file (any unit of that file)
        byfile = {}
        for u in units:
            byfile.setdefault(u.file, []).append(u.text)
        vis = sum(1 for f in G.facts.values() if f["mode"] == "present" and E.contains_fact("\n".join(byfile.get(f["file"], [])), f))
        out[parser] = {"facts_visible": vis, "facts_present": sum(1 for f in G.facts.values() if f["mode"] == "present")}
        for method, size in (("structure", 400), ("fixed", 400)):
            t0 = time.time()
            chunks = C.chunk(units, method, size, 0.0)
            tc = time.time() - t0
            bm = R.BM25([c.text for c in chunks])
            conf = [bool(c.meta.get("confidential")) for c in chunks]

            def m(qtext, role, bm=bm, chunks=chunks, conf=conf):
                import numpy as np
                mask = None if role in C.HR_ROLES else ~np.array(conf)
                return {"items": [chunks[i].as_item() for i, _ in bm.search(qtext, 10, mask)]}

            r = E.retrieval_only(m, G)
            out[parser][f"{method}-{size}"] = {"chunks": len(chunks), "chunk_s": round(tc, 1),
                                                "overall": r["summary"]["overall"], "latency": r["summary"]["latency_s"],
                                                "levels": r["summary"]["match_levels"],
                                                "by_type": {k: v.get("recall@5") for k, v in r["summary"]["by_type"].items()}}
    # section detection: gold PDF sources with a section, does a structured unit at that page carry that section?
    units = C.parse("/dump", parser="structured")
    at = {}
    for u in units:
        if u.fmt == "pdf":
            at.setdefault((u.file, u.loc.get("page")), set()).add(E.norm(u.loc.get("section", "")))
    n = ok = 0
    miss = []
    for q in G.qs:
        for g in G.gold(q):
            if g["file"].endswith(".pdf") and g.get("section") and g.get("page") and not g["section"].startswith("page"):
                n += 1
                if E.norm(g["section"]) in at.get((g["file"], g["page"]), set()):
                    ok += 1
                elif len(miss) < 12:
                    miss.append((g["file"][-50:], g["page"], g["section"], sorted(at.get((g["file"], g["page"]), set()))[:4]))
    out["section_detection"] = {"n": n, "ok": ok, "miss_sample": miss}
    return out


@app.local_entrypoint()
def smoke():
    r = smoke_remote.remote()
    for parser in ("plain", "structured"):
        d = r[parser]
        print(parser, "facts visible", d["facts_visible"], "/", d["facts_present"])
        for k, v in d.items():
            if isinstance(v, dict) and "overall" in v:
                o = v["overall"]
                print(f"  {k}: chunks {v['chunks']} ({v['chunk_s']} s)  n={o['n']} R@1 {o['recall@1']} R@5 {o['recall@5']} R@10 {o['recall@10']} "
                      f"MRR {o['mrr']} cov@5 {o['coverage@5']} fact@5 {o['fact_recall@5']}  p95 {v['latency'].get('p95')}s  levels {v['levels']}")
                print("     by type R@5:", v["by_type"])
    print("section detection", r["section_detection"]["ok"], "/", r["section_detection"]["n"])
