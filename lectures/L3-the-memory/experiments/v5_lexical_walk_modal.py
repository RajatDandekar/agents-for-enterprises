"""L3 v5, section `lexical`: the BM25 walk-through numbers (review of 5 Nov 2026).

    export MODAL_PROFILE=rajatworkspace; /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_lexical_walk_modal.py

Builds rag.BM25 (k1 = 1.2, b = 0.75) on D's 15 default chunks (the RAG Lab's index on the volume `northbridge-raglab`,
the same chunks as logs/v5_lexical.json) and records, for Emma's question, every piece of the formula per chunk and per
matching word, read from the built index (idf from bm.idf, the weight from bm.W, the score from bm.scores):

    weight(t, chunk) = idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))

plus the saturation example ("supplier" in §6, chunk 5) and the length example. Writes logs/v5_lexical_walk.json.
No model, no LLM: CPU only.
"""
from __future__ import annotations

import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
LOGS = HERE / "logs"
SKIP = {"__pycache__", "cassettes", "brainlab", "legacy_ui", "qa", "_index", "experience", "app", "pages", "restricted"}
D = "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf"
CHUNKING = "structured-structure-200-o15"   # the default chunks, as in v5_lexical_modal.py

# the same image and mounts as v5_lexical_modal.py (CPU part only)
cpu_img = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pypdf==5.1.0", "pdfplumber==0.11.4", "openpyxl==3.1.5", "python-docx==1.1.2", "pyyaml==6.0.2",
                 "tiktoken==0.8.0", "pillow==11.0.0", "numpy<2.1", "scipy", "httpx", "pydantic>=2")
    .env({"PYTHONPATH": "/course/ledgerline", "PYTHONUNBUFFERED": "1", "NB_L3_CACHE": "/tmp/l3cache"})
    .add_local_dir(COURSE / "ledgerline" / "ledgerline", "/course/ledgerline/ledgerline",
                   ignore=lambda p: any(x in SKIP for x in pathlib.Path(p).parts) or str(p).endswith((".png", ".mp4")))
)
app = modal.App("l3-v5-lexical-walk")
rvol = modal.Volume.from_name("northbridge-raglab")


def _load_all():
    from ledgerline.course.l3 import rag

    return rag.load_chunks(f"/rvol/chroma/{CHUNKING}/chunks.jsonl.gz")

Q = "Can I buy the battery packs from Brightcell Energy? They quote £104."


@app.function(image=cpu_img, timeout=900, cpu=2, memory=8192, volumes={"/rvol": rvol})
def walk() -> dict:
    import numpy as np

    from ledgerline.course.l3 import rag

    allc = _load_all()
    dch = [c for c in allc if c.file == D]
    texts = [c.text for c in dch]
    bm = rag.BM25(texts)
    k1, b = bm.k1, bm.b
    toks = [rag.tokenize(t) for t in texts]
    dl = [len(t) for t in toks]
    avg = float(np.mean(np.array(dl, dtype=np.float32)))
    qtok = rag.tokenize(Q)
    qset = list(dict.fromkeys(qtok))
    scores = bm.scores(Q)
    order = sorted(range(len(texts)), key=lambda i: (-float(scores[i]), i))
    rank = {i: r + 1 for r, i in enumerate(order)}
    df = {t: int(sum(t in set(x) for x in toks)) for t in qset + ["supplier"]}
    idf = {t: (round(float(bm.idf[bm.vocab[t]]), 4) if t in bm.vocab else None) for t in df}

    def piece(i, t):
        j = bm.vocab.get(t)
        tf = toks[i].count(t)
        if j is None or tf == 0:
            return {"word": t, "tf": 0}
        L = 1 - b + b * dl[i] / avg
        sat = tf * (k1 + 1) / (tf + k1 * L)
        w = float(bm.W[i, j])
        assert abs(float(bm.idf[j]) * sat - w) < 1e-4, (i, t, float(bm.idf[j]) * sat, w)
        return {"word": t, "tf": tf, "idf": round(float(bm.idf[j]), 4), "length_factor": round(L, 4),
                "tf_part": round(sat, 4), "weight": round(w, 4)}

    chunks = []
    for i, c in enumerate(dch):
        ps = [piece(i, t) for t in qset]
        m = [p for p in ps if p["tf"]]
        s = float(scores[i])
        assert abs(sum(p["weight"] for p in m) - s) < 1e-3, (i, s)
        chunks.append({"k": i, "cid": c.cid, "cite": c.cite, "dl": dl[i], "dl_over_avg": round(dl[i] / avg, 4),
                       "length_factor": round(1 - b + b * dl[i] / avg, 4), "matched": m,
                       "missing": [p["word"] for p in ps if not p["tf"]], "score": round(s, 4), "rank": rank[i]})

    # saturation, on a real word in a real chunk: "supplier" in §6 (chunk 5)
    j = bm.vocab["supplier"]
    i5 = 5
    tf5 = toks[i5].count("supplier")
    L5 = 1 - b + b * dl[i5] / avg
    curve_avg = [{"tf": n, "tf_part": round(n * (k1 + 1) / (n + k1), 4)} for n in range(1, 13)]
    curve_c5 = [{"tf": n, "tf_part": round(n * (k1 + 1) / (n + k1 * L5), 4)} for n in range(1, 13)]
    sat = {"word": "supplier", "chunk": i5, "tf": tf5, "df_D": df["supplier"], "idf": round(float(bm.idf[j]), 4),
           "length_factor": round(L5, 4), "weight": round(float(bm.W[i5, j]), 4),
           "weight_if_counted_plainly": round(float(bm.idf[j]) * tf5, 4),
           "curve_avg_length": curve_avg, "curve_chunk5_length": curve_c5,
           "tf_per_chunk": [toks[i].count("supplier") for i in range(len(texts))]}
    assert abs(float(bm.idf[j]) * curve_c5[tf5 - 1]["tf_part"] - sat["weight"]) < 1e-3
    return {"what": "BM25 walk-through for Emma's question on D (experiments/v5_lexical_walk_modal.py)",
            "chunking": CHUNKING, "D": D, "Q": Q, "q_tokens": qtok, "k1": k1, "b": b, "N": len(texts),
            "avgdl": round(avg, 3), "df_D": df, "idf_D": idf, "chunks": chunks, "order": order,
            "saturation_example": sat}


@app.local_entrypoint()
def main():
    d = walk.remote()
    (LOGS / "v5_lexical_walk.json").write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print("N", d["N"], "avgdl", d["avgdl"], "tokens", d["q_tokens"])
    for c in sorted(d["chunks"], key=lambda c: c["rank"])[:5]:
        print(c["rank"], c["k"], c["score"], c["dl"], c["length_factor"], [(p["word"], p["tf"], p["idf"], p["tf_part"], p["weight"]) for p in c["matched"]])
    s = d["saturation_example"]
    print("supplier", s["tf"], s["idf"], s["length_factor"], s["weight"], s["weight_if_counted_plainly"])
