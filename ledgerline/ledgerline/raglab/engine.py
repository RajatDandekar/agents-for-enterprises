"""The RAG Lab's engine: persisted Chroma indexes for every grid chunking, live search, chunk views, the 2D map,
and the golden-set metrics precomputed by the grid.

Data (Modal Volume `northbridge-raglab`, mounted at RAGLAB_VOL, default /vol):
    chroma/<chunking>/            chunks.jsonl.gz, chroma/ (one collection per model + <model>__hr), bm25.pkl, build.json
    vec/<chunking>/<model>.pca.npz  mean, two components, 2D coordinates of every chunk
    grid/<chunking>.json          the grid's measured rows for that chunking (retrieval metrics, latency)
    rewrites.json                 the recorded query rewrites for the golden questions
    answers/*.json                answer-level metrics for the configs that were answered (if any)
Indexes are copied to local disk on first use (LRU, RAGLAB_LOCAL_MAX chunkings) and opened with chromadb.
"""
from __future__ import annotations

import collections
import json
import os
import pathlib
import pickle
import shutil
import threading
import time

from ..course.l3 import corpus as C
from ..course.l3 import evaluate as E
from ..course.l3 import rag as R

VOL = pathlib.Path(os.environ.get("RAGLAB_VOL", "/vol"))
LOCAL = pathlib.Path(os.environ.get("RAGLAB_LOCAL", "/tmp/raglab"))
LOCAL_MAX = int(os.environ.get("RAGLAB_LOCAL_MAX", "8"))
BUDGET_S = 0.200     # the latency budget the class agreed: retrieval p95 <= 200 ms
OPTIONS = {
    "parser": ["plain", "structured"], "chunker": ["fixed", "recursive", "structure"], "size": [200, 400, 800, 1200],
    "overlap": [0.0, 0.15], "embed": list(R.EMBED_MODELS), "retrieval": ["dense", "bm25", "hybrid"],
    "rerank": [False, True], "rewrite": [False, True], "k": [3, 5, 10],
}
EXAMPLES = [
    ("Q-EMMA", "Can I buy the battery packs from Brightcell Energy? They quote £104."),
    ("Q-0412", "What does ERR-PO-0412 mean and how do I fix it?"),
]
SHOW_FILES = [
    "01_policies/POL-PUR-001_Purchase_Policy_v4.1.pdf",
    "02_procedures/SOP-PUR-001 Supplier Onboarding v3.1.pdf",
    "03_ledgerline_manuals/MAN-ERR-72 Message and Error Code Reference v7.2.3.pdf",
    "05_master_data/SUPPLIER_MASTER.xlsx",
    "04_service_definitions/purchase/po_save.yaml",
    "09_email_archive/2026/2026-10-22_Quotation Q-BE-26-0917 - Brightcell Energy.eml",
    "10_meeting_notes/2026-10-07 CAB minutes (CR-2026-031 certificate check).docx",
    "99_scans/2026_signed_approval_PO-2026-00452.pdf",
]


def cfg_from(d: dict) -> R.Config:
    def pick(k, cast, default):
        v = d.get(k, default)
        try:
            v = cast(v)
        except (TypeError, ValueError):
            v = default
        return v if v in OPTIONS[k] else default

    b = lambda v: v in (True, "true", "1", 1, "on", "yes")  # noqa: E731
    return R.Config(parser=pick("parser", str, "structured"), chunker=pick("chunker", str, "structure"),
                    size=pick("size", int, 400), overlap=pick("overlap", float, 0.0), embed=pick("embed", str, "bge-small"),
                    retrieval=pick("retrieval", str, "hybrid"), rerank=b(d.get("rerank")), rewrite=b(d.get("rewrite")),
                    k=pick("k", int, 5))


class Engine:
    def __init__(self, vol: pathlib.Path = VOL, preload: list[str] | None = None, gpu_lock: bool = True):
        self.vol = pathlib.Path(vol)
        self.lock = threading.Lock()
        self.gpu = threading.Lock() if gpu_lock else None
        self.idx: "collections.OrderedDict[str, R.Index]" = collections.OrderedDict()
        self.loading: dict[str, threading.Lock] = {}
        self.pca: dict = {}
        self.G = E.Golden(os.environ.get("NORTHBRIDGE_DOCS"))
        self.by_q = {q["question"].strip().lower(): q for q in self.G.qs}
        rw = self.vol / "rewrites.json"
        self.rewrites = json.loads(rw.read_text()) if rw.exists() else {}
        self.grid = self._load_grid()
        self.answers = self._load_answers()
        self.best = self._best()
        for cid in preload or []:
            try:
                self.index(cid)
            except Exception as e:  # noqa: BLE001
                print("preload failed", cid, e)

    def refresh(self):
        """Re-read the grid, answers and best config (after the Volume was reloaded)."""
        g, a, b = self._load_grid(), self._load_answers(), self._best()
        rw = self.vol / "rewrites.json"
        self.grid, self.answers, self.best = g, a, b
        if rw.exists():
            self.rewrites = json.loads(rw.read_text())

    # ------------------------------------------------------------------ precomputed metrics
    def _load_grid(self) -> dict:
        out = {}
        for p in sorted((self.vol / "grid").glob("*.json")):
            try:
                d = json.loads(p.read_text())
            except Exception:  # noqa: BLE001
                continue
            for r in d["rows"]:
                r = {k: v for k, v in r.items() if k != "per_q"}
                r["build"] = {k: d["build"].get(k) for k in ("n_chunks", "tokens_mean", "build_s_total", "index_bytes", "machine")}
                r["build"]["model"] = (d["build"].get("models") or {}).get(r.get("embed") or "", {})
                key = (r["chunking"], r["embed"] or "-", r["retrieval"], bool(r["rerank"]), bool(r["rewrite"]))
                out[key] = r
        return out

    def _load_answers(self) -> dict:
        out = {}
        for p in sorted((self.vol / "answers").glob("*.json")) if (self.vol / "answers").exists() else []:
            try:
                d = json.loads(p.read_text())
                out[d["config"]] = d["summary"]
            except Exception:  # noqa: BLE001
                pass
        return out

    def _best(self):
        bp = self.vol / "rag_best.json"
        if bp.exists():
            try:
                return json.loads(bp.read_text())
            except Exception:  # noqa: BLE001
                pass
        return None

    def metrics(self, cfg: R.Config) -> dict | None:
        key = (cfg.chunking, "-" if cfg.retrieval == "bm25" else cfg.embed, cfg.retrieval, cfg.rerank, cfg.rewrite)
        r = self.grid.get(key)
        if not r:
            return None
        o = r["overall"]
        k = cfg.k
        p95 = (r["latency_s"] or {}).get("p95")
        out = {"recall@k": o.get(f"recall@{k}"), "recall@5": o.get("recall@5"), "coverage@k": o.get(f"coverage@{k}"),
               "fact_recall@k": o.get(f"fact_recall@{k}"), "mrr": o.get("mrr"), "n": o.get("n"),
               "p50_ms": round((r["latency_s"] or {}).get("p50", 0) * 1000, 1), "p95_ms": round((p95 or 0) * 1000, 1),
               "under_budget": p95 is not None and p95 <= BUDGET_S,
               "by_type": {t: v.get(f"recall@{k}") for t, v in r["by_type"].items() if v.get("n")},
               "timing_p50_ms": {a: round(b * 1000, 2) for a, b in (r.get("timing_p50_s") or {}).items()},
               "build": r["build"]}
        rank = sorted(self.grid.values(), key=lambda x: -(x["overall"].get(f"recall@{k}") or 0))
        out["rank"] = next((i + 1 for i, x in enumerate(rank) if x is r), None)
        out["of"] = len(rank)
        a = self.answers.get(cfg.id)
        if a:
            out["answers"] = {k2: a["overall"].get(k2) for k2 in ("answer_correct", "fact_correct", "citation_correct", "cost_per_q_usd")}
            out["answers"]["total_p95_s"] = (a["overall"].get("total_s") or {}).get("p95")
        return out

    def leaderboard_score(self, cfg: R.Config) -> dict | None:
        m = self.metrics(R.Config(**{**cfg.__dict__, "k": 5}))
        if not m:
            return None
        return {"recall@5": m["recall@k"], "mrr": m["mrr"], "p95_ms": m["p95_ms"], "under_budget": m["under_budget"]}

    def built(self) -> list[str]:
        return sorted(p.name for p in (self.vol / "chroma").iterdir() if (p / "build.json").exists()) if (self.vol / "chroma").exists() else []

    # ------------------------------------------------------------------ indexes
    def index(self, cid: str) -> R.Index:
        with self.lock:
            if cid in self.idx:
                self.idx.move_to_end(cid)
                return self.idx[cid]
            lk = self.loading.setdefault(cid, threading.Lock())
        with lk:
            with self.lock:
                if cid in self.idx:
                    return self.idx[cid]
            src = self.vol / "chroma" / cid
            if not (src / "build.json").exists():
                raise KeyError(f"index {cid} is not built")
            dst = LOCAL / cid
            if not (dst / "build.json").exists():
                tmp = LOCAL / (cid + ".part")
                shutil.rmtree(tmp, ignore_errors=True)
                shutil.copytree(src, tmp)
                shutil.rmtree(dst, ignore_errors=True)
                tmp.rename(dst)
            idx = R.Index.load(dst)
            if (dst / "bm25.pkl").exists():
                idx._bm25 = pickle.loads((dst / "bm25.pkl").read_bytes())
            with self.lock:
                self.idx[cid] = idx
                while len(self.idx) > LOCAL_MAX:
                    old, _ = self.idx.popitem(last=False)
                    shutil.rmtree(LOCAL / old, ignore_errors=True)
            return idx

    def _pca(self, cid: str, model: str):
        import numpy as np

        key = (cid, model)
        if key not in self.pca:
            p = self.vol / "vec" / cid / f"{model}.pca.npz"
            d = np.load(p)
            self.pca[key] = {"mean": d["mean"], "comp": d["comp"], "xy": d["xy"].astype("float32")}
            if len(self.pca) > 24:
                self.pca.pop(next(iter(self.pca)))
        return self.pca[key]

    # ------------------------------------------------------------------ the live search
    def search(self, cfg: R.Config, question: str, role: str = C.DEFAULT_ROLE) -> dict:
        import numpy as np

        t_load = time.perf_counter()
        idx = self.index(cfg.chunking)
        load_s = time.perf_counter() - t_load
        gq = self.by_q.get(question.strip().lower())
        rewrites = dict(self.rewrites)
        note = None
        if cfg.rewrite and question not in rewrites:
            if gq and gq["question"] in rewrites:
                rewrites[question] = rewrites[gq["question"]]
            else:
                try:
                    rewrites[question] = R.rewrite(question)
                except Exception as e:  # noqa: BLE001 - no key or no credit: search with the question as typed
                    rewrites[question] = {"query": question, "seconds": 0.0, "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0}
                    note = f"Query rewriting needs a live LLM call, which is not available right now ({type(e).__name__}); searched with the question as typed."
        ret = R.Retriever(idx, cfg, rewrites=rewrites)
        t_wait = time.perf_counter()
        if self.gpu:
            self.gpu.acquire()
        try:
            waited = time.perf_counter() - t_wait
            out = ret.search(question, role=role, k=cfg.k)
            qv = ret.emb.query(out["query"]) if ret.emb else R.Embedder("bge-small").query(out["query"])
        finally:
            if self.gpu:
                self.gpu.release()
        res = {"query": out["query"], "seconds": out["seconds"], "local_ms": round(out["local_seconds"] * 1000, 2),
               "timing_ms": {k: round(v * 1000, 2) for k, v in out["timing"].items()}, "queue_ms": round(waited * 1000, 2),
               "index_load_ms": round(load_s * 1000, 1), "note": note, "items": []}
        golds = E.Golden.gold(self.G, gq) if gq and self.G.expected(gq) == "answer" else []
        for it in out["items"]:
            hit = any(E.loc_match(self.G, g, it["file"], it["loc"]) for g in golds) if golds else None
            res["items"].append({"rank": it["rank"], "cite": it["cite"], "file": it["file"], "loc": it["loc"],
                                 "score": it["score"], "dense": it.get("dense"), "bm25": it.get("bm25"),
                                 "text": it["text"][:1500], "gold": hit, "chunk_index": it["chunk_index"]})
        if gq:
            res["golden"] = {"id": gq["id"], "type": gq["type"], "reference": gq["reference_answer"],
                             "gold_sources": [{k: g.get(k) for k in ("file", "page", "sheet", "row", "section")} for g in golds],
                             "expected": self.G.expected(gq)}
        # the map: the query and its neighbours in this embedding space (PCA of the chunk vectors)
        model = cfg.embed if cfg.retrieval != "bm25" else "bge-small"
        try:
            P = self._pca(cfg.chunking, model)
            qxy = ((qv - P["mean"]) @ P["comp"].T).tolist()
            res["map"] = {"model": model, "query": [round(qxy[0], 4), round(qxy[1], 4)],
                          "hits": [[round(float(P["xy"][it["chunk_index"]][0]), 4), round(float(P["xy"][it["chunk_index"]][1]), 4)]
                                   for it in out["items"]]}
        except Exception as e:  # noqa: BLE001
            res["map"] = {"error": str(e)[:200]}
        return res

    def map_points(self, cid: str, model: str, n: int = 3500) -> dict:
        import numpy as np

        idx = self.index(cid)
        P = self._pca(cid, model)
        N = len(idx.chunks)
        step = max(1, N // n)
        sel = list(range(0, N, step))
        folders = sorted({c.meta.get("folder", "") for c in idx.chunks})
        fi = {f: i for i, f in enumerate(folders)}
        xy = P["xy"][sel]
        return {"model": model, "n_total": N, "folders": folders,
                "points": [[round(float(x), 3), round(float(y), 3), fi[idx.chunks[i].meta.get("folder", "")]] for i, (x, y) in zip(sel, xy)]}

    def chunks_of(self, cid: str, file: str, limit: int = 60) -> dict:
        idx = self.index(cid)
        cs = [c for c in idx.chunks if c.file == file]
        return {"file": file, "chunking": cid, "n": len(cs), "tokens": [c.n_tokens for c in cs],
                "chunks": [{"cid": c.cid, "cite": c.cite, "locs": c.locs, "n_tokens": c.n_tokens, "text": c.text[:3000]}
                           for c in cs[:limit]]}

    def files(self, cid: str) -> list[str]:
        idx = self.index(cid)
        seen = []
        for c in idx.chunks:
            if c.meta.get("confidential"):
                continue
            if not seen or seen[-1] != c.file:
                seen.append(c.file)
        return sorted(set(seen))
