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


GEMINI_ENV = "/Users/raj/Claude_Brain/wm-lecture6-ijepa/.env"


def _key(name="OPENROUTER_API_KEY", path=None):
    if not modal.is_local():
        return ""
    path = path or (GEMINI_ENV if name == "GEMINI_API_KEY" else COURSE / ".env")
    if not os.path.exists(path):
        return ""
    for line in open(path):
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
    base.pip_install("torch==2.4.1", "transformers==4.46.3", "sentence-transformers==3.3.1", "einops", "chromadb==1.0.15",
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
            .add_local_dir(DUMP, "/dump", ignore=lambda p: ".git" in pathlib.Path(p).parts)
            .add_local_dir(CASS, "/cass_src", ignore=lambda p: not pathlib.Path(p).name.startswith("L3v4")))


cpu_img = _mount(base)
gpu_img = _mount(gpu_image)
app = modal.App("northbridge-l3-rag")
vol = modal.Volume.from_name("northbridge-raglab", create_if_missing=True)
secret = (modal.Secret.from_dict({"OPENROUTER_API_KEY": _key(), "GEMINI_API_KEY": _key("GEMINI_API_KEY")})
          if modal.is_local() else modal.Secret.from_dict({}))


def _init_cassettes():
    """Copy the recorded L3v4 cassettes into the writable cassette dir, so recorded calls replay instead of re-running."""
    import shutil

    d = pathlib.Path("/tmp/cassettes")
    d.mkdir(parents=True, exist_ok=True)
    for p in pathlib.Path("/cass_src").glob("L3v4*.jsonl"):
        if not (d / p.name).exists():
            shutil.copy(p, d / p.name)


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


# =============================================================================== 1. the audit
@app.function(image=gpu_img, volumes={"/vol": vol}, cpu=8, memory=16384, timeout=3600)
def audit_remote() -> dict:
    import hashlib
    import re as _re

    sys.path.insert(0, "/course/ledgerline")
    from transformers import AutoTokenizer

    from ledgerline.course.l3 import corpus as C, evaluate as E

    qwen = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    root = C.dump_root("/dump")
    files = C.list_files(root)
    G = E.Golden(root)
    units = {p: C.parse(root, parser=p) for p in C.PARSERS}
    fails = {}
    for p in C.PARSERS:
        C.parse(root, parser=p)
        fails[p] = C.parse.failures
    S = units["structured"]
    text_by_file = {}
    for u in S:
        text_by_file.setdefault(u.file, []).append(u.text)
    plain_by_file = {}
    for u in units["plain"]:
        plain_by_file.setdefault(u.file, []).append(u.text)
    from pypdf import PdfReader

    per_file = {}
    for rel in files:
        fmt = C.fmt_of(rel)
        t = "\n".join(text_by_file.get(rel, []))
        pages = len(PdfReader(root / rel).pages) if fmt == "pdf" else 0
        rows = sum(1 for u in S if u.file == rel and u.kind == "table" and u.fmt in ("xlsx", "csv")) if fmt in ("xlsx", "csv") else 0
        per_file[rel] = {"folder": rel.split("/")[0] if "/" in rel else "(root)", "fmt": fmt, "class": C.FMT_CLASS.get(fmt, "unstructured"),
                         "bytes": os.path.getsize(root / rel), "pages": pages, "rows": rows, "words": len(t.split()),
                         "tokens_o200k": C.n_tokens(t), "tokens_qwen": len(qwen(t, add_special_tokens=False)["input_ids"]) if t else 0,
                         "plain_tokens_o200k": C.n_tokens("\n".join(plain_by_file.get(rel, []))), "units": len(text_by_file.get(rel, []))}

    def roll(key):
        out = {}
        for rel, d in per_file.items():
            o = out.setdefault(d[key], {"files": 0, "bytes": 0, "pages": 0, "rows": 0, "words": 0, "tokens_o200k": 0, "tokens_qwen": 0,
                                        "plain_tokens_o200k": 0, "types": {}})
            for k in ("bytes", "pages", "rows", "words", "tokens_o200k", "tokens_qwen", "plain_tokens_o200k"):
                o[k] += d[k]
            o["files"] += 1
            o["types"][d["fmt"]] = o["types"].get(d["fmt"], 0) + 1
        return dict(sorted(out.items()))

    tot = {k: sum(d[k] for d in per_file.values()) for k in ("bytes", "pages", "rows", "words", "tokens_o200k", "tokens_qwen", "plain_tokens_o200k")}
    tot["files"] = len(files)
    # messiness, as the parser sees it
    m = json.load(open(root / "eval" / "messiness.json"))
    meta = {u.file: u.meta for u in S}
    sha = {rel: hashlib.sha1(open(root / rel, "rb").read()).hexdigest() for rel in files}
    dup_groups = {}
    for rel, h in sha.items():
        dup_groups.setdefault(h, []).append(rel)
    dups = [g for g in dup_groups.values() if len(g) > 1]

    def shingles(t, n=8):
        w = _re.findall(r"\w+", t.lower())
        return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}

    seen = []
    for it in m["items"]:
        fs = [f for f in it["files"] if f in per_file]
        flags = {f: {k: meta.get(f, {}).get(k) for k in ("doc_id", "version", "effective", "status", "superseded", "future", "confidential")} for f in fs}
        note = {}
        if it["kind"] in ("near_duplicate", "duplicate", "superseded") and len(fs) >= 2:
            a, b = shingles("\n".join(text_by_file.get(fs[0], []))), shingles("\n".join(text_by_file.get(fs[1], [])))
            note["jaccard_8gram"] = round(len(a & b) / max(1, len(a | b)), 3)
            note["byte_identical"] = sha[fs[0]] == sha[fs[1]]
        if it["kind"] == "scans":
            note["ocr_words"] = {f: per_file[f]["words"] for f in per_file if f.startswith("99_scans/")}
            note["plain_parser_tokens"] = {f: per_file[f]["plain_tokens_o200k"] for f in per_file if f.startswith("99_scans/")}
        if it["kind"] == "tables_in_pdfs":
            note["table_units"] = {f: sum(1 for u in S if u.file == f and " | " in u.text) for f in fs}
        if it["kind"] in ("superseded", "future_dated", "confidential"):
            flag = {"superseded": "superseded", "future_dated": "future", "confidential": "confidential"}[it["kind"]]
            note["parser_flagged_first_file"] = bool(flags.get(fs[0], {}).get(flag)) if fs else None
        seen.append({"id": it["id"], "kind": it["kind"], "what": it["what"], "files": fs, "parser_meta": flags, "parser_sees": note})
    # facts visible through each parser (needles found in the file's parsed text)
    vis = {}
    for p in C.PARSERS:
        byf = {}
        for u in units[p]:
            byf.setdefault(u.file, []).append(u.text)
        miss = [f["id"] + " " + f["file"] for f in G.facts.values() if f["mode"] == "present"
                and not E.contains_fact("\n".join(byf.get(f["file"], [])), f)]
        vis[p] = {"present_facts": sum(1 for f in G.facts.values() if f["mode"] == "present"), "visible": None, "invisible": miss}
        vis[p]["visible"] = vis[p]["present_facts"] - len(miss)
    flagged = {k: sorted(f for f, mm in meta.items() if mm.get(k)) for k in ("superseded", "future", "confidential")}
    qp_breaks = sum(len(_re.findall(r"=\r?\n", t)) for f, ts in plain_by_file.items() if f.endswith(".eml") for t in ts)
    docx_tables_lost = sum(1 for u in S if u.fmt == "docx" and " | " in u.text)
    return {"generated": time.strftime("%Y-%m-%d %H:%M"), "dump": "northbridge-docs (local copy mounted at /dump)",
            "tokenizers": {"o200k": "tiktoken o200k_base", "qwen": "Qwen/Qwen2.5-0.5B-Instruct (Qwen2.5 tokenizer)"},
            "counted_on": "tokens_o200k / tokens_qwen / words: the structured parser's text (OCR for the 6 scans; every table row as column: value pairs, so tables cost more); plain_tokens_o200k: the plain parser's text (values only, no OCR), comparable to eval/stats.json",
            "totals": tot, "by_folder": roll("folder"), "by_type": roll("fmt"), "by_class": roll("class"),
            "class_rule": C.FMT_CLASS,
            "parse_failures": fails, "units": {p: len(units[p]) for p in C.PARSERS},
            "empty_files": {p: sorted(f for f in files if not "".join(t.strip() for t in ({"plain": plain_by_file, "structured": text_by_file}[p]).get(f, []))) for p in C.PARSERS},
            "facts_visible": vis, "flags": {k: {"n": len(v), "files": v} for k, v in flagged.items()},
            "duplicates_byte_identical": dups,
            "plain_vs_structured": {"eml_quoted_printable_soft_breaks_in_plain": qp_breaks,
                                    "docx_table_units_dropped_by_plain": docx_tables_lost,
                                    "xlsx_rows_without_headers_in_plain": sum(1 for u in units["plain"] if u.fmt == "xlsx"),
                                    "scan_text_tokens_plain": sum(per_file[f]["plain_tokens_o200k"] for f in per_file if f.startswith("99_scans/")),
                                    "scan_text_tokens_structured_ocr": sum(per_file[f]["tokens_o200k"] for f in per_file if f.startswith("99_scans/"))},
            "messiness_through_parser": seen, "per_file": per_file}


@app.local_entrypoint()
def audit():
    r = audit_remote.remote()
    _write_log("audit.json", r)
    t = r["totals"]
    print(json.dumps(t), "\nclasses:", {k: (v["files"], v["tokens_o200k"]) for k, v in r["by_class"].items()})
    print("failures:", {k: len(v) for k, v in r["parse_failures"].items()}, "facts visible:", {k: (v["visible"], v["present_facts"]) for k, v in r["facts_visible"].items()})
    print("invisible (structured):", r["facts_visible"]["structured"]["invisible"])
    print("flags:", {k: v["n"] for k, v in r["flags"].items()}, "plain vs structured:", r["plain_vs_structured"])


# =============================================================================== 2. paste everything
@app.function(image=cpu_img, volumes={"/vol": vol}, secrets=[secret], cpu=4, memory=16384, timeout=7200)
def paste_all_remote(n_sample: int = 12, run: bool = True) -> dict:
    import random

    import httpx

    _init_cassettes()
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C, evaluate as E
    from ledgerline.llm import LLM

    root = C.dump_root("/dump")
    S = C.parse(root, parser="structured")
    G = E.Golden(root)
    by_file = {}
    for u in S:
        by_file.setdefault(u.file, []).append(u)
    tok = {f: C.n_tokens("\n".join(u.text for u in us)) for f, us in by_file.items()}
    total = sum(tok.values())
    subsets = {
        "everything": lambda f: True,
        "without 06_transactions": lambda f: not f.startswith("06_"),
        "without 05_master_data and 06_transactions": lambda f: not f.startswith(("05_", "06_")),
        "policies + procedures + manuals only (01-03)": lambda f: f.startswith(("01_", "02_", "03_")),
    }
    sub_tok = {k: sum(v for f, v in tok.items() if fn(f)) for k, fn in subsets.items()}
    models = httpx.get("https://openrouter.ai/api/v1/models", timeout=60).json()["data"]
    pick = ["google/gemini-3.8-flash", "google/gemini-3.1-pro-preview", "google/gemini-3.5-flash-lite", "openai/gpt-6.1-terra",
            "anthropic/claude-sonnet-5.5", "meta-llama/llama-4-scout", "x-ai/grok-4.20", "qwen/qwen3-235b-a22b"]
    top = sorted(models, key=lambda m: -(m.get("context_length") or 0))
    win = {m["id"]: {"context_length": m.get("context_length"), "prompt_usd_per_m": float(m["pricing"].get("prompt", 0) or 0) * 1e6,
                     "completion_usd_per_m": float(m["pricing"].get("completion", 0) or 0) * 1e6,
                     "cache_read_usd_per_m": float(m["pricing"].get("input_cache_read", 0) or 0) * 1e6}
           for m in models if m["id"] in pick or m in top[:6] and float(m["pricing"].get("prompt", 0) or 0) > 0}
    largest = max((v["context_length"] or 0) for v in win.values())
    fl = win.get("google/gemini-3.8-flash", {})
    per_q = {k: {"tokens": v, "fits": {m: (w["context_length"] or 0) >= v + 2000 for m, w in win.items()},
                 "usd_per_question_gemini_3.8_flash": round(v * fl.get("prompt_usd_per_m", 0) / 1e6 + 300 * fl.get("completion_usd_per_m", 0) / 1e6, 4),
                 "usd_per_question_if_cached": round(v * fl.get("cache_read_usd_per_m", 0) / 1e6 + 300 * fl.get("completion_usd_per_m", 0) / 1e6, 4)}
             for k, v in sub_tok.items()}
    out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "tokenizer": "tiktoken o200k_base on the structured parser's text",
           "total_tokens": total, "subsets": per_q, "context_windows": win, "largest_window": largest,
           "fits_any_model": total + 2000 <= largest,
           "note": "Cost per question assumes ~300 output tokens; cached = the provider's input_cache_read price, if the cache hits."}
    if not run:
        return out
    # one labelled measured run: the largest subset that fits the answer model's window, on a fixed sample
    name = "without 05_master_data and 06_transactions"
    keep = [f for f in sorted(by_file) if subsets[name](f) and not by_file[f][0].meta.get("confidential")]
    items = [{"id": f, "file": f, "text": "\n".join(u.text for u in by_file[f]), "loc": {}, "cite": f, "meta": by_file[f][0].meta}
             for f in keep]
    inside = [q for q in G.qs if G.expected(q) == "answer" and G.gold(q) and all(subsets[name](g["file"]) for g in G.gold(q))]
    rnd = random.Random(7)
    sample = [G.by_id["Q-0412"]] + rnd.sample([q for q in inside if q["id"] != "Q-0412"], n_sample - 1)
    llm = LLM(E.ANSWER_MODEL, cassette="L3v4_paste_all", max_tokens=2048)
    judge = LLM(E.JUDGE_MODEL, cassette="L3v4_judge", max_tokens=512)

    def method(question, role):
        return {"items": items, "seconds": 0.0}

    from concurrent.futures import ThreadPoolExecutor

    def one(q):
        a = E.answer(q, items, llm, max_chars=None)
        return {"id": q["id"], "type": q["type"], "answer": a["answer"], "tokens_in": a["tokens_in"], "tokens_out": a["tokens_out"],
                "seconds": a["llm_seconds"], "cost_usd": a["cost_usd"], "fact": E.fact_check(q, a["answer"], G),
                "judge": E.judge(q, a["answer"], judge, G), "citation": E.citation_check(q, a, items, G)}

    with ThreadPoolExecutor(3) as ex:
        recs = list(ex.map(one, sample))
    out["measured_run"] = {
        "label": f"MEASURED SAMPLE: {n_sample} documentation questions whose gold sources are all inside the subset "
                 f"'{name}' ({len(items)} files, confidential HR folder left out), pasted whole into {E.ANSWER_MODEL}",
        "subset_tokens_o200k": sum(C.n_tokens(i["text"]) for i in items), "n": len(recs),
        "answer_correct": round(sum(r["judge"]["ok"] for r in recs) / len(recs), 3),
        "fact_correct": round(sum(bool(r["fact"]["ok"]) for r in recs if r["fact"]["ok"] is not None) / max(1, sum(r["fact"]["ok"] is not None for r in recs)), 3),
        "citation_correct": round(sum(r["citation"]["ok"] for r in recs if r["citation"]) / max(1, sum(1 for r in recs if r["citation"])), 3),
        "seconds": E.lat([r["seconds"] for r in recs]), "tokens_in_per_q": round(sum(r["tokens_in"] for r in recs) / len(recs)),
        "cost_per_q_usd": round(sum(r["cost_usd"] for r in recs) / len(recs), 4), "records": recs}
    out["_cassettes"] = _cassettes()
    return out


@app.local_entrypoint()
def paste_all(n: int = 12, run: bool = True):
    r = paste_all_remote.remote(n, run)
    _merge_cassettes(r.pop("_cassettes", {}))
    _write_log("paste_all.json", r)
    print("total", r["total_tokens"], "largest window", r["largest_window"], "fits any:", r["fits_any_model"])
    for k, v in r["subsets"].items():
        print(f"  {k}: {v['tokens']:,} tokens, ${v['usd_per_question_gemini_3.8_flash']}/q, fits flash: {v['fits'].get('google/gemini-3.8-flash')}")
    if "measured_run" in r:
        mr = r["measured_run"]
        print(mr["label"]); print({k: mr[k] for k in ("n", "answer_correct", "fact_correct", "citation_correct", "seconds", "tokens_in_per_q", "cost_per_q_usd")})


# =============================================================================== 3. the RAG grid
PARSERS_G = ("plain", "structured")
CHUNKERS_G = ("fixed", "recursive", "structure")
SIZES_G = (200, 400, 800, 1200)
OVERLAPS_G = (0.0, 0.15)
MODELS_G = ("bge-small", "bge-base", "e5-small", "gte-small", "nomic")
BATCH = {"bge-small": 128, "bge-base": 64, "e5-small": 128, "gte-small": 128, "nomic": 16}
GPU_G = "L4"
MACHINE = f"Modal {GPU_G} GPU container, 4 vCPU, 16 GiB (gpu=L4, cpu=4, memory=16384)"


def all_chunkings():
    from itertools import product

    return [f"{p}-{m}-{s}-o{int(o * 100)}" for p, m, s, o in product(PARSERS_G, CHUNKERS_G, SIZES_G, OVERLAPS_G)]


@app.function(image=cpu_img, volumes={"/vol": vol}, secrets=[secret], cpu=2, memory=4096, timeout=3600)
def rewrites_remote() -> dict:
    _init_cassettes()
    sys.path.insert(0, "/course/ledgerline")
    from concurrent.futures import ThreadPoolExecutor

    from ledgerline.course.l3 import corpus as C, rag as R
    from ledgerline.llm import LLM

    qs = C.questions("/dump")
    llm = LLM(R.REWRITE_MODEL, cassette="L3v4_rewrite", max_tokens=1024)
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda q: R.rewrite(q["question"], llm), qs))
    out = {q["question"]: r for q, r in zip(qs, res)}
    pathlib.Path("/vol/rewrites.json").write_text(json.dumps(out, indent=1))
    vol.commit()
    return {"n": len(out), "sample": dict(list(out.items())[:6]), "_cassettes": _cassettes(),
            "seconds": [r["seconds"] for r in res], "cost_usd": sum(r["cost_usd"] for r in res)}


@app.local_entrypoint()
def rewrites():
    r = rewrites_remote.remote()
    _merge_cassettes(r.pop("_cassettes", {}))
    print(r["n"], "rewrites; cost $", round(r["cost_usd"], 4))
    for q, v in r["sample"].items():
        print(" ", q, "->", v["query"])


def _eval_chunking(cid: str, idx, G, rewrites, models, rerank_opts=(False, True), rewrite_opts=(False, True)) -> list[dict]:
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    out = []
    combos = [("bm25", None)] + [(r, m) for m in models for r in ("dense", "hybrid")]
    for retrieval, model in combos:
        for rr in rerank_opts:
            for qr in rewrite_opts:
                p, ch, size, o = cid.split("-")
                cfg = R.Config(p, ch, int(size), int(o[1:]) / 100, model or "bge-small", retrieval, rr, qr, 10)
                ret = R.Retriever(idx, cfg, rewrites=rewrites)
                ret.search(G.qs[1]["question"], k=10)  # warm-up: first-call costs are not a student's latency
                recs, timing = [], {}
                for q in G.qs:
                    o_ = ret.search(q["question"], role=C.role_of(q), k=10)
                    recs.append({"id": q["id"], "type": q["type"], "retrieval_s": o_["seconds"],
                                 "local_s": o_["local_seconds"], "retrieval": E.gold_hits(q, o_["items"], G),
                                 "top": [it["chunk_index"] for it in o_["items"]]})
                    for k_, v in o_["timing"].items():
                        timing.setdefault(k_, []).append(v)
                s = E.summarize_retrieval(recs)
                row = {"chunking": cid, "parser": p, "chunker": ch, "size": int(size), "overlap": int(o[1:]) / 100,
                       "embed": model, "retrieval": retrieval, "rerank": rr, "rewrite": qr,
                       "overall": s["overall"], "by_type": {t: {k: v.get(k) for k in ("n", "recall@3", "recall@5", "recall@10", "mrr")}
                                                              for t, v in s["by_type"].items()},
                       "latency_s": s["latency_s"], "local_latency_s": E.lat([r["local_s"] for r in recs]),
                       "timing_p50_s": {k: round(E.pct(v, 50), 5) for k, v in timing.items()},
                       "timing_p95_s": {k: round(E.pct(v, 95), 5) for k, v in timing.items()},
                       "per_q": {r["id"]: [r["retrieval"]["rank"], r["top"]] for r in recs}}
                out.append(row)
    return out


@app.function(image=gpu_img, gpu=GPU_G, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=4 * 3600, max_containers=16)
def grid_one(cid: str, rebuild: bool = False) -> dict:
    import shutil

    import numpy as np

    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    t_start = time.time()
    p, ch, size, o = cid.split("-")
    G = E.Golden("/dump")
    vol_dir = pathlib.Path("/vol/chroma") / cid
    local = pathlib.Path("/tmp/idx") / cid
    stats = {}
    if vol_dir.exists() and (vol_dir / "build.json").exists() and not rebuild and \
            json.loads((vol_dir / "build.json").read_text()).get("hnsw") == R.HNSW:
        shutil.copytree(vol_dir, local, dirs_exist_ok=True)
        idx = R.Index.load(local)
        stats = json.loads((vol_dir / "build.json").read_text())
    else:
        t0 = time.time()
        units = C.parse("/dump", parser=p)
        chunks = C.chunk(units, ch, int(size), int(o[1:]) / 100)
        t_chunk = time.time() - t0
        vecs = {}
        for m in MODELS_G:
            R.Embedder(m)  # load before timing the build
        t1 = time.time()
        idx = R.Index.build(chunks, [], local)
        import chromadb

        client = chromadb.PersistentClient(path=str(local / "chroma"))
        per = {}
        old = json.loads((vol_dir / "build.json").read_text()).get("models", {}) if (vol_dir / "build.json").exists() else {}
        for m in MODELS_G:
            a = time.time()
            vf = pathlib.Path("/vol/vec") / cid / f"{m}.npy"
            reuse = vf.exists() and m in old and np.load(vf, mmap_mode="r").shape[0] == len(chunks)
            v = np.load(vf).astype(np.float32) if reuse else R.Embedder(m).passages([c.text for c in chunks], batch=BATCH[m])
            if reuse:  # same chunks: renormalise the stored float16 vectors and keep the original embedding time
                v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
            e_s = old[m]["embed_s"] if reuse else time.time() - a
            a = time.time()
            R.add_vectors(client, m, chunks, v)
            per[m] = {"embed_s": round(e_s, 2), "chroma_add_s": round(time.time() - a, 2), "dim": int(v.shape[1]),
                      "vectors_reused": bool(reuse)}
            vecs[m] = v
            vd = pathlib.Path("/vol/vec") / cid
            vd.mkdir(parents=True, exist_ok=True)
            np.save(vd / f"{m}.npy", v.astype(np.float16))
            # PCA to 2D for the RAG Lab's map: keep the mean and two components so a query can be projected exactly
            mu = v.mean(0)
            _, _, vt = np.linalg.svd(v[:: max(1, len(v) // 6000)] - mu, full_matrices=False)
            comp = vt[:2]
            xy = (v - mu) @ comp.T
            np.savez(vd / f"{m}.pca.npz", mean=mu.astype(np.float32), comp=comp.astype(np.float32), xy=xy.astype(np.float16))
        del client
        a = time.time()
        bm = R.BM25([c.text for c in chunks])
        bm_s = time.time() - a
        import pickle

        (local / "bm25.pkl").write_bytes(pickle.dumps(bm))
        toks = [c.n_tokens for c in chunks]
        sizes_by = {}
        for pth in (local / "chroma").rglob("*"):
            if pth.is_file():
                sizes_by["chroma"] = sizes_by.get("chroma", 0) + pth.stat().st_size
        stats = {"chunking": cid, "n_chunks": len(chunks), "tokens_mean": round(sum(toks) / len(toks), 1),
                 "tokens_p95": E.pct(toks, 95), "tokens_total": sum(toks), "chunk_s": round(t_chunk, 2),
                 "bm25_build_s": round(bm_s, 2), "models": per,
                 "index_bytes": {"chroma_all_models": sizes_by.get("chroma", 0),
                                 "chunks_gz": (local / "chunks.jsonl.gz").stat().st_size, "bm25_pkl": (local / "bm25.pkl").stat().st_size},
                 "build_s_total": round(time.time() - t0, 1), "machine": MACHINE, "hnsw": R.HNSW,
                 "chromadb": __import__("chromadb").__version__}
        (local / "build.json").write_text(json.dumps(stats, indent=1))
        if vol_dir.exists():
            shutil.rmtree(vol_dir)
        shutil.copytree(local, vol_dir)
        vol.commit()
        idx = R.Index.load(local)
    import pickle

    if (local / "bm25.pkl").exists():
        idx._bm25 = pickle.loads((local / "bm25.pkl").read_bytes())
    rewrites = json.loads(pathlib.Path("/vol/rewrites.json").read_text()) if pathlib.Path("/vol/rewrites.json").exists() else {}
    rows = _eval_chunking(cid, idx, G, rewrites, MODELS_G)
    res = {"chunking": cid, "build": stats, "rows": rows, "wall_s": round(time.time() - t_start, 1)}
    pathlib.Path("/vol/grid").mkdir(exist_ok=True)
    pathlib.Path(f"/vol/grid/{cid}.json").write_text(json.dumps(res))
    vol.commit()
    return {"chunking": cid, "wall_s": res["wall_s"], "n_rows": len(rows),
            "best_r5": max(r["overall"]["recall@5"] for r in rows)}


@app.function(image=cpu_img, volumes={"/vol": vol}, timeout=6 * 3600)
def grid_driver(cids: list[str], rebuild: bool = False) -> list:
    out = []
    for r in grid_one.map(cids, kwargs={"rebuild": rebuild}, return_exceptions=True):
        out.append(r if isinstance(r, dict) else {"error": str(r)[:500]})
        print(out[-1], flush=True)
    return out


@app.local_entrypoint()
def grid_build(only: str = "", rebuild: bool = False, wait: bool = False):
    cids = [c for c in all_chunkings() if not only or c in only.split(",") or only in c]
    print(len(cids), "chunkings:", cids[:4], "...")
    call = grid_driver.spawn(cids, rebuild)
    print("spawned grid_driver:", call.object_id)
    if wait:
        print(json.dumps(call.get(), indent=1))


@app.function(image=gpu_img, gpu=GPU_G, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=3600)
def diag_remote(cid: str = "structured-structure-400-o0", model: str = "bge-small") -> dict:
    import shutil

    import numpy as np

    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import corpus as C, evaluate as E, rag as R

    G = E.Golden("/dump")
    local = pathlib.Path("/tmp/idx") / cid
    shutil.copytree(f"/vol/chroma/{cid}", local, dirs_exist_ok=True)
    idx = R.Index.load(local)
    V = np.load(f"/vol/vec/{cid}/{model}.npy").astype(np.float32)
    emb = R.Embedder(model)
    conf = idx.conf
    out = {}
    recs = {"exact": [], "chroma_nowhere": [], "chroma_where": []}
    col = idx.collection(model)
    t = {"chroma_nowhere": [], "chroma_where": []}
    for q in G.qs:
        qv = emb.query(q["question"])
        s = V @ qv
        s[conf] = -9
        top = np.argsort(-s)[:10]
        recs["exact"].append({"id": q["id"], "type": q["type"], "retrieval_s": 0, "retrieval": E.gold_hits(q, [idx.chunks[i].as_item() for i in top], G)})
        a = time.perf_counter()
        r = col.query(query_embeddings=[qv.tolist()], n_results=30, include=["distances"])
        t["chroma_nowhere"].append(time.perf_counter() - a)
        ids = [int(i) for i in r["ids"][0] if not conf[int(i)]][:10]
        recs["chroma_nowhere"].append({"id": q["id"], "type": q["type"], "retrieval_s": 0, "retrieval": E.gold_hits(q, [idx.chunks[i].as_item() for i in ids], G)})
        a = time.perf_counter()
        r = col.query(query_embeddings=[qv.tolist()], n_results=10, where={"confidential": False}, include=["distances"])
        t["chroma_where"].append(time.perf_counter() - a)
        ids = [int(i) for i in r["ids"][0]]
        recs["chroma_where"].append({"id": q["id"], "type": q["type"], "retrieval_s": 0, "retrieval": E.gold_hits(q, [idx.chunks[i].as_item() for i in ids], G)})
    for k, v in recs.items():
        o = E.summarize_retrieval(v)["overall"]
        out[k] = {m: o[m] for m in ("recall@1", "recall@5", "recall@10", "mrr")}
    out["latency"] = {k: E.lat(v) for k, v in t.items()}
    # what do the dense top hits look like for two questions?
    for qid in ("Q-0412", "Q-101", "Q-201"):
        q = G.by_id[qid]
        qv = emb.query(q["question"])
        s = V @ qv
        top = np.argsort(-s)[:5]
        out[qid] = [(round(float(s[i]), 3), idx.chunks[i].file[-60:], idx.chunks[i].text[:90]) for i in top]
    by_folder = {}
    for c in idx.chunks:
        by_folder[c.meta.get("folder")] = by_folder.get(c.meta.get("folder"), 0) + 1
    out["chunks_by_folder"] = by_folder
    return out


@app.local_entrypoint()
def diag(cid: str = "structured-structure-400-o0", model: str = "bge-small"):
    print(json.dumps(diag_remote.remote(cid, model), indent=1, default=str))


@app.function(image=cpu_img, secrets=[secret], timeout=120)
def key_status_remote() -> dict:
    import httpx

    d = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]}, timeout=30).json().get("data", {})
    return {k: d.get(k) for k in ("limit", "usage", "limit_remaining", "limit_reset", "usage_daily", "usage_monthly")}


@app.local_entrypoint()
def key_status():
    print(key_status_remote.remote())


@app.function(image=gpu_img, gpu=GPU_G, volumes={"/vol": vol}, timeout=1800)
def save_q_remote(model: str = "bge-small"):
    import numpy as np

    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import evaluate as E, rag as R

    G = E.Golden("/dump")
    emb = R.Embedder(model)
    np.save(f"/vol/diag_Q_{model}.npy", np.stack([emb.query(q["question"]) for q in G.qs]))
    vol.commit()


chroma1_img = modal.Image.debian_slim(python_version="3.11").pip_install("chromadb==1.0.15", "numpy<2.1")


@app.function(image=chroma1_img, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=1800)
def chroma1_remote(cid: str = "structured-structure-400-o0", model: str = "bge-small") -> dict:
    import shutil

    import chromadb
    import numpy as np

    V = np.load(f"/vol/vec/{cid}/{model}.npy").astype(np.float32)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    Q = np.load(f"/vol/diag_Q_{model}.npy")
    ids = list(range(len(V)))
    ex = np.argsort(-(Q @ V.T), axis=1)[:, :10]
    out = {"chromadb": chromadb.__version__}
    H = lambda ef, efc=200, m=32: {"hnsw": {"space": "cosine", "ef_search": ef, "ef_construction": efc, "max_neighbors": m}}
    for name, cfg in (("default", None), ("ef_search200", H(200)), ("ef_search1000", H(1000)),
                      ("ef_search1000_efc400_M64", H(1000, 400, 64)), ("ef_search4000", H(4000))):
        p = pathlib.Path(f"/tmp/c1_{name}")
        shutil.rmtree(p, ignore_errors=True)
        cl = chromadb.PersistentClient(path=str(p))
        try:
            c = cl.create_collection("probe", configuration=cfg) if cfg else cl.create_collection("probe", metadata={"hnsw:space": "cosine"})
        except Exception as e:  # noqa: BLE001
            out[name] = repr(e)[:300]
            continue
        for s in range(0, len(ids), 4000):
            part = ids[s:s + 4000]
            c.add(ids=[str(i) for i in part], embeddings=V[part])
        t0 = time.time()
        top1 = ov = 0
        for qi in range(len(Q)):
            got = [int(i) for i in c.query(query_embeddings=[Q[qi]], n_results=10)["ids"][0]]
            top1 += int(ex[qi][0] in got)
            ov += len(set(ex[qi]) & set(got)) / 10
        out[name] = {"exact_top1_in_top10": round(top1 / len(Q), 3), "overlap@10": round(ov / len(Q), 3),
                     "ms_per_q": round((time.time() - t0) / len(Q) * 1000, 2)}
    return out


@app.local_entrypoint()
def chroma1():
    save_q_remote.remote()
    r = chroma1_remote.remote()
    r["what"] = ("Share of the exact (brute-force cosine) nearest chunks that Chroma's HNSW returns, for the 224 golden "
                 "questions, bge-small on structured-structure-400-o0 (13,606 chunks). Earlier runs with chromadb 0.6.3 "
                 "(hnsw:search_ef 10/128/512/2000 in metadata) all returned the same ~75-80%: the setting had no effect.")
    _write_log("hnsw_check.json", r)
    print(json.dumps(r, indent=1))


# =============================================================================== 3b. collect the grid, answers, the best config
def _safe(cid: str) -> str:
    return cid.replace("|", "__")


@app.function(image=cpu_img, volumes={"/vol": vol}, cpu=2, memory=8192, timeout=1800)
def collect_remote() -> dict:
    rows, builds, missing = [], {}, []
    for p in sorted(pathlib.Path("/vol/grid").glob("*.json")):
        d = json.loads(p.read_text())
        builds[d["chunking"]] = d["build"]
        for r in d["rows"]:
            rows.append({k: v for k, v in r.items() if k != "per_q"})
    answers = {}
    for p in sorted(pathlib.Path("/vol/answers").glob("*.json")) if pathlib.Path("/vol/answers").exists() else []:
        d = json.loads(p.read_text())
        answers[d["config"]] = {"summary": d["summary"], "label": d.get("label")}
    return {"rows": rows, "builds": builds, "answers": answers}


def _row_id(r, k=5):
    e = "-" if r["retrieval"] == "bm25" else r["embed"]
    return f"{r['chunking']}|{e}|{r['retrieval']}|rr{int(r['rerank'])}|qr{int(r['rewrite'])}|k{k}"


@app.local_entrypoint()
def collect():
    """Write logs/rag_grid.json: every measured grid row (k = 3, 5, 10 read off one top-10 ranking) + build stats."""
    d = collect_remote.remote()
    rows = d["rows"]
    out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "machine": MACHINE, "budget_p95_s": 0.2,
           "questions": "224 documentation questions; recall/MRR over the 205 a user should get an answer to "
                        "(not_in_docs and refused permission questions are scored on the answer, not on retrieval)",
           "k_note": "Each config is searched once with k=10; recall@3/@5 are read off the same ranking, so latency is the k=10 search.",
           "rewrite_note": "Query rewriting latency = the recorded LLM call (gemini-3.8-flash via OpenRouter), added to the measured retrieval.",
           "grid": {"parsers": PARSERS_G, "chunkers": CHUNKERS_G, "sizes": SIZES_G, "overlaps": OVERLAPS_G, "models": MODELS_G,
                    "retrieval": ["dense", "bm25", "hybrid"], "rerank": [False, True], "rewrite": [False, True], "k": [3, 5, 10]},
           "pruning": "none for retrieval: every chunking x model x retrieval x reranker x rewriting was measured "
                      f"({len(rows)} rows x 3 k values); answers were generated only for the configs in rag_answers_*.json",
           "n_rows": len(rows), "builds": d["builds"], "rows": rows}
    _write_log("rag_grid.json", out)
    ok = [r for r in rows if r["latency_s"]["p95"] <= 0.2]
    top = sorted(rows, key=lambda r: -r["overall"]["recall@5"])[:8]
    print(len(rows), "rows;", len(ok), "under the 200 ms budget")
    for r in top:
        print(f"  {_row_id(r)}  R@5 {r['overall']['recall@5']}  MRR {r['overall']['mrr']}  p95 {r['latency_s']['p95'] * 1000:.0f} ms")
    for r in sorted(ok, key=lambda r: -r["overall"]["recall@5"])[:8]:
        print(f"  [budget] {_row_id(r)}  R@5 {r['overall']['recall@5']}  MRR {r['overall']['mrr']}  p95 {r['latency_s']['p95'] * 1000:.0f} ms")


@app.function(image=gpu_img, gpu=GPU_G, volumes={"/vol": vol}, secrets=[secret], cpu=4, memory=16384, timeout=4 * 3600,
              max_containers=6)
def answers_one(cfg_id: str, label: str = "") -> dict:
    import pickle
    import shutil

    _init_cassettes()
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import evaluate as E, rag as R

    cfg = R.Config.from_id(cfg_id)
    local = pathlib.Path("/tmp/idx") / cfg.chunking
    shutil.copytree(f"/vol/chroma/{cfg.chunking}", local, dirs_exist_ok=True)
    idx = R.Index.load(local)
    idx._bm25 = pickle.loads((local / "bm25.pkl").read_bytes())
    rewrites = json.loads(pathlib.Path("/vol/rewrites.json").read_text())
    ret = R.Retriever(idx, cfg, rewrites=rewrites)
    G = E.Golden("/dump")
    ret.search(G.qs[1]["question"], k=cfg.k)  # warm-up

    def method(q, role):
        return ret.search(q, role=role, k=cfg.k)

    rep = E.run(method, name=cfg_id, G=G, workers=8, cassette="L3v4_answers", judge_cassette="L3v4_judge")
    rep.update({"config": cfg_id, "label": label, "machine": MACHINE})
    pathlib.Path("/vol/answers").mkdir(exist_ok=True)
    pathlib.Path(f"/vol/answers/{_safe(cfg_id)}.json").write_text(json.dumps(rep))
    vol.commit()
    return {"config": cfg_id, "summary": rep["summary"], "_cassettes": _cassettes(), "label": label}


@app.local_entrypoint()
def answers(configs: str, labels: str = ""):
    """configs: comma-separated config ids (Config.id). Writes logs/rag_answers/<id>.json (records + summary)."""
    ids = [c for c in configs.split(",") if c]
    labs = labels.split(",") if labels else [""] * len(ids)
    for r in answers_one.starmap(list(zip(ids, labs)), return_exceptions=True):
        if not isinstance(r, dict):
            print("FAILED", str(r)[:400])
            continue
        _merge_cassettes(r.pop("_cassettes", {}))
        o = r["summary"]["overall"]
        print(f"{r['config']} [{r['label']}]: correct {o['answer_correct']} fact {o['fact_correct']} cite {o['citation_correct']} "
              f"ret p95 {o['retrieval_s'].get('p95')} total p95 {o['total_s'].get('p95')} ${o['cost_per_q_usd']}/q  kappa {r['summary']['judge_vs_fact']['kappa']}")


@app.function(image=cpu_img, volumes={"/vol": vol}, timeout=600)
def fetch_answers_remote() -> dict:
    out = {}
    for p in sorted(pathlib.Path("/vol/answers").glob("*.json")) if pathlib.Path("/vol/answers").exists() else []:
        out[p.name] = p.read_text()
    return out


@app.local_entrypoint()
def pull_answers():
    for name, text in fetch_answers_remote.remote().items():
        (LOGS / "rag_answers").mkdir(parents=True, exist_ok=True)
        (LOGS / "rag_answers" / name).write_text(text)
        print("wrote", LOGS / "rag_answers" / name)


@app.function(image=gpu_img, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=3600)
def publish_best_remote(best: dict) -> dict:
    """Package the best config's index (chunks, BM25, one model's Chroma collections) as /vol/best_index.tar.gz."""
    import shutil
    import tarfile

    import chromadb
    import numpy as np

    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import rag as R

    cfg = R.Config.from_id(best["config"]["id"])
    src = pathlib.Path("/vol/chroma") / cfg.chunking
    dst = pathlib.Path("/tmp/best") / cfg.chunking
    shutil.rmtree(dst.parent, ignore_errors=True)
    dst.mkdir(parents=True)
    for f in ("chunks.jsonl.gz", "bm25.pkl", "build.json"):
        shutil.copy(src / f, dst / f)
    chunks = R.load_chunks(dst / "chunks.jsonl.gz")
    if cfg.retrieval != "bm25":
        v = np.load(f"/vol/vec/{cfg.chunking}/{cfg.embed}.npy").astype(np.float32)
        v /= np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
        R.add_vectors(chromadb.PersistentClient(path=str(dst / "chroma")), cfg.embed, chunks, v)
    (dst / "rag_best.json").write_text(json.dumps(best, indent=1))
    out = pathlib.Path("/vol/best_index.tar.gz")
    with tarfile.open(out, "w:gz") as tf:
        tf.add(dst, arcname=cfg.chunking)
    pathlib.Path("/vol/rag_best.json").write_text(json.dumps(best, indent=1))
    vol.commit()
    return {"bytes": out.stat().st_size, "chunking": cfg.chunking}


@app.function(image=gpu_img, gpu=GPU_G, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=1800)
def rr_nan_remote(cid: str = "structured-structure-400-o0") -> dict:
    import math
    import pickle

    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import evaluate as E, rag as R

    idx = R.Index.load(f"/vol/chroma/{cid}")
    idx._bm25 = pickle.loads(pathlib.Path(f"/vol/chroma/{cid}/bm25.pkl").read_bytes())
    G = E.Golden("/dump")
    cfg = R.Config(retrieval="hybrid", rerank=False, k=20)
    ret = R.Retriever(idx, cfg)
    rr16 = R.Reranker()
    from sentence_transformers import CrossEncoder

    rr32 = CrossEncoder(R.RERANK_MODEL, device="cuda", max_length=512)
    n_nan16 = n_nan32 = n = 0
    diff = []
    for q in G.qs:
        items = ret.search(q["question"], k=20)["items"]
        texts = [idx.chunks[i["chunk_index"]].text for i in items]
        a = rr16.score(q["question"], texts)
        b = [float(x) for x in rr32.predict([(q["question"], t) for t in texts], batch_size=32)]
        n += len(a)
        n_nan16 += sum(math.isnan(x) for x in a)
        n_nan32 += sum(math.isnan(x) for x in b)
        diff += [abs(x - y) for x, y in zip(a, b) if not math.isnan(x)]
    return {"pairs": n, "nan_fp16": n_nan16, "nan_fp32": n_nan32, "max_abs_diff": max(diff), "mean_abs_diff": sum(diff) / len(diff)}


@app.local_entrypoint()
def rr_nan():
    print(rr_nan_remote.remote())


# =============================================================================== 3c. the honest failures
@app.function(image=cpu_img, volumes={"/vol": vol}, cpu=4, memory=16384, timeout=1800)
def failures_remote(best_id: str) -> dict:
    sys.path.insert(0, "/course/ledgerline")
    from ledgerline.course.l3 import evaluate as E, rag as R

    G = E.Golden("/dump")
    best = R.Config.from_id(best_id)
    cache = {}

    def rows_of(cid):
        if cid not in cache:
            cache[cid] = json.loads(pathlib.Path(f"/vol/grid/{cid}.json").read_text())["rows"]
        return cache[cid]

    def row(cid, retrieval, embed, rr=False, qr=False):
        for r in rows_of(cid):
            if r["retrieval"] == retrieval and (r["embed"] or "-") == (embed if retrieval != "bm25" else "-") and r["rerank"] == rr and r["rewrite"] == qr:
                return r

    chunks = {}

    def chunk_list(cid):
        if cid not in chunks:
            chunks[cid] = R.load_chunks(f"/vol/chroma/{cid}/chunks.jsonl.gz")
        return chunks[cid]

    def top_cites(cid, r, qid, n=3):
        cs = chunk_list(cid)
        return [cs[i].cite for i in r["per_q"][qid][1][:n]]

    cid, emb = best.chunking, best.embed
    out = {"best_chunking": cid, "embed": emb}
    # 1. exact codes: dense vs BM25 vs hybrid
    modes = {m: row(cid, m, emb) for m in ("dense", "bm25", "hybrid")}
    modes["hybrid+rerank"] = row(cid, "hybrid", emb, True)
    out["exact_code"] = {m: r["by_type"]["exact_code"] for m, r in modes.items()}
    out["exact_code_by_model_dense"] = {m: row(cid, "dense", m)["by_type"]["exact_code"]["recall@5"] for m in R.EMBED_MODELS}
    out["Q-0412"] = {m: {"rank_of_first_gold": r["per_q"]["Q-0412"][0], "top3": top_cites(cid, r, "Q-0412")} for m, r in modes.items()}
    codes = [q for q in G.qs if q["type"] == "exact_code"]
    out["codes_bm25_only"] = [q["id"] + " " + q["question"] for q in codes
                              if (modes["bm25"]["per_q"][q["id"]][0] or 99) <= 5 and (modes["dense"]["per_q"][q["id"]][0] or 99) > 5][:10]
    # 2. tables: plain vs structured parser, same chunker/size
    p_cid = cid.replace("structured-", "plain-", 1) if cid.startswith("structured-") else cid
    s_cid = p_cid.replace("plain-", "structured-", 1)
    out["tables"] = {f"{par} {m}": row(c, m, emb)["by_type"]["table_lookup"]["recall@5"]
                     for par, c in (("plain", p_cid), ("structured", s_cid)) for m in ("dense", "bm25", "hybrid")}
    q401 = "Q-401"
    out["Q-401 (reorder level of BAT-500)"] = {par: {"hybrid_rank": row(c, "hybrid", emb)["per_q"][q401][0], "top3": top_cites(c, row(c, "hybrid", emb), q401)}
                                               for par, c in (("plain", p_cid), ("structured", s_cid))}
    # 3. multi-hop: any gold source vs all of them
    r = row(cid, best.retrieval, emb, best.rerank, best.rewrite)
    cs = chunk_list(cid)
    mh = []
    for q in G.qs:
        if q["type"] != "multi_hop":
            continue
        top = [cs[i].as_item() for i in r["per_q"][q["id"]][1]]
        h = E.gold_hits(q, top, G)
        mh.append({"id": q["id"], "n_gold": h["n_gold"], "any@5": h.get("hit@5"), "cov@5": h.get("cov@5"), "cov@10": h.get("cov@10")})
    out["multi_hop"] = {"n": len(mh), "any_gold@5": round(sum(x["any@5"] or 0 for x in mh) / len(mh), 3),
                        "all_gold@5": round(sum((x["cov@5"] or 0) == 1 for x in mh) / len(mh), 3),
                        "all_gold@10": round(sum((x["cov@10"] or 0) == 1 for x in mh) / len(mh), 3),
                        "mean_coverage@5": round(sum(x["cov@5"] or 0 for x in mh) / len(mh), 3), "questions": mh}
    # 4. versions: a superseded / old / not-yet-in-force chunk ranked above the first gold source
    vc = []
    for q in G.qs:
        if q["type"] != "version_conflict":
            continue
        ids = r["per_q"][q["id"]][1]
        first_gold = r["per_q"][q["id"]][0] or 99
        stale = [k + 1 for k, i in enumerate(ids[:5]) if cs[i].meta.get("superseded") or cs[i].meta.get("future")]
        vc.append({"id": q["id"], "first_gold_rank": r["per_q"][q["id"]][0], "stale_ranks_top5": stale,
                   "stale_before_gold": bool(stale and stale[0] < first_gold), "top3": [cs[i].cite for i in ids[:3]]})
    out["version_conflict"] = {"n": len(vc), "stale_in_top5": sum(bool(x["stale_ranks_top5"]) for x in vc),
                               "stale_ranked_above_gold": sum(x["stale_before_gold"] for x in vc), "questions": vc}
    # 5. Emma's Brightcell question
    q = G.by_id["Q-EMMA"]
    for name, rr_ in (("best", r), ("dense only", row(cid, "dense", emb))):
        top = [cs[i].as_item() for i in rr_["per_q"]["Q-EMMA"][1]]
        found = []
        for g in G.gold(q):
            rk = next((k + 1 for k, it in enumerate(top) if E.loc_match(G, g, it["file"], it["loc"])), None)
            found.append({"file": g["file"].split("/")[-1], "fact": g["fact_id"], "rank": rk})
        out[f"Q-EMMA {name}"] = {"gold_sources": len(found), "found@5": sum(1 for f in found if f["rank"] and f["rank"] <= 5),
                                 "found@10": sum(1 for f in found if f["rank"]), "detail": found, "top5": [it["cite"] for it in top[:5]]}
    return out


@app.local_entrypoint()
def failures(best: str):
    r = failures_remote.remote(best)
    _write_log("rag_failures.json", r)
    print(json.dumps({k: v for k, v in r.items() if k not in ("multi_hop", "version_conflict")}, indent=1)[:4000])
    print("multi-hop:", {k: v for k, v in r["multi_hop"].items() if k != "questions"})
    print("versions:", {k: v for k, v in r["version_conflict"].items() if k != "questions"})
