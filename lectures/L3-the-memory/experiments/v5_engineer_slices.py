"""L3 v5 · engineer section: one-knob-at-a-time slices of the RAG grid, plus the per-question numbers the metric
slides teach from. Reads only existing logs (no new retrieval or LLM runs):

    logs/rag_grid.json                 2,112 measured retrieval rows (48 chunkings x 44 search settings), Modal L4
    logs/rag_best.json                 the selection rule, the chosen config, its scorecard, the 9 answered candidates
    logs/rag_answers/*.json            per-question records of the 9 answered configs (retrieval + answer + judge)
    logs/rag_failures.json             failure analysis on the chosen chunking
    logs/v5_dense.json                 the one-document chunk-size playground (dense section, for the comparison)
    northbridge-docs/eval/questions.jsonl   the golden set

and, from the Modal Volume `northbridge-raglab`, the wall time of each grid container (/vol/grid/<chunking>.json),
which rag_grid.json does not carry. Run (from the course root):

    /Users/raj/.venv/bin/modal run lectures/L3-the-memory/experiments/v5_engineer_slices.py

Writes logs/v5_engineer_slices.json. Every number on the engineer slides comes from that file.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import time

import modal

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
DUMP = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs")

app = modal.App("l3v5-engineer-slices")
vol = modal.Volume.from_name("northbridge-raglab")
img = modal.Image.debian_slim(python_version="3.11")


@app.function(image=img, volumes={"/vol": vol}, cpu=2, memory=8192, timeout=900)
def grid_walls() -> dict:
    """Wall seconds of every grid container (build or load the index + search all 44 settings x 224 questions)."""
    out = {}
    for p in sorted(pathlib.Path("/vol/grid").glob("*.json")):
        d = json.loads(p.read_text())
        out[d["chunking"]] = {"wall_s": d.get("wall_s"), "n_rows": len(d.get("rows", []))}
    return out


# ------------------------------------------------------------------------------------------------ helpers
def pct(xs, q):  # the same linear-interpolation percentile as ledgerline.course.l3.evaluate.pct
    xs = sorted(xs)
    k = (len(xs) - 1) * q / 100
    f, c = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def row_view(r):
    o = r["overall"]
    return {"recall@3": o["recall@3"], "recall@5": o["recall@5"], "recall@10": o["recall@10"], "mrr": o["mrr"],
            "coverage@5": o["coverage@5"], "p50_s": r["latency_s"]["p50"], "p95_s": r["latency_s"]["p95"],
            "search_only_p95_s": r["local_latency_s"]["p95"], "timing_p95_s": r.get("timing_p95_s")}


def main_local(walls: dict | None):
    G = json.loads((LOGS / "rag_grid.json").read_text())
    B = json.loads((LOGS / "rag_best.json").read_text())
    F = json.loads((LOGS / "rag_failures.json").read_text())
    rows = G["rows"]
    best = B["config"]
    base = {"parser": best["parser"], "chunker": best["chunker"], "size": best["size"], "overlap": best["overlap"],
            "retrieval": best["retrieval"], "embed": best["embed"], "rerank": best["rerank"], "rewrite": best["rewrite"]}

    def find(**over):
        want = {**base, **over}
        hit = [r for r in rows if all(r[k] == v for k, v in want.items())]
        return hit[0] if len(hit) == 1 else None

    base_row = find()
    assert base_row and abs(base_row["overall"]["recall@5"] - B["retrieval"]["recall@5"]) < 1e-9, "chosen row mismatch"

    def slice_(knob, values, fixed=None, label=None):
        out = []
        for v in values:
            over = dict(fixed or {})
            if isinstance(v, dict):
                over.update(v)
                name = label(v) if label else str(v)
            else:
                over[knob] = v
                name = str(v)
            r = find(**over)
            out.append({"setting": name, **(row_view(r) if r else {"missing": True}), "chosen": r is base_row})
        return out

    S = {}
    S["parser"] = slice_("parser", ["plain", "structured"])
    S["chunker"] = slice_("chunker", ["fixed", "recursive", "structure"])
    S["size"] = slice_("size", [200, 400, 800, 1200])
    S["overlap"] = slice_("overlap", [0.0, 0.15])
    S["search"] = slice_("retrieval", [
        {"retrieval": "dense", "embed": "bge-small"}, {"retrieval": "bm25", "embed": None},
        {"retrieval": "hybrid", "embed": "bge-small"}], label=lambda v: v["retrieval"])
    S["search_no_rerank"] = slice_("retrieval", [
        {"retrieval": "dense", "embed": "bge-small", "rerank": False}, {"retrieval": "bm25", "embed": None, "rerank": False},
        {"retrieval": "hybrid", "embed": "bge-small", "rerank": False}], label=lambda v: v["retrieval"])
    S["rerank"] = slice_("rerank", [False, True])
    S["rerank_hybrid"] = slice_("rerank", [False, True], fixed={"retrieval": "hybrid", "embed": "bge-small"})
    S["rewrite"] = slice_("rewrite", [False, True])
    models = G["grid"]["models"]
    S["model_hybrid_rerank"] = slice_("embed", models, fixed={"retrieval": "hybrid"})
    S["model_dense"] = slice_("embed", models, fixed={"retrieval": "dense", "rerank": False})
    S["k"] = [{"setting": k, "recall": base_row["overall"][f"recall@{k}"], "coverage": base_row["overall"][f"coverage@{k}"]}
              for k in (3, 5, 10)]
    # interaction: does the best chunk size depend on the search mode? (structured, structure-aware, 15%, no reranker)
    inter = {}
    for mode, emb in (("dense", "bge-small"), ("bm25", None), ("hybrid", "bge-small")):
        inter[mode] = {str(s): (find(size=s, retrieval=mode, embed=emb, rerank=False) or {}).get("overall", {}).get("recall@5")
                       for s in G["grid"]["sizes"]}
    S["interaction_size_x_search"] = inter
    # dense alone with the plain parser and fixed cuts: what the "obvious first RAG" scores
    naive = find(parser="plain", chunker="fixed", size=400, overlap=0.0, retrieval="dense", embed="bge-small", rerank=False)
    S["naive_first_rag"] = row_view(naive)

    # ---------------- per-question: the chosen config's records (k = 10 answers; retrieval ranks read off its top 10)
    A = {}
    for p in sorted((LOGS / "rag_answers").glob("*.json")):
        d = json.loads(p.read_text())
        A[d["config"]] = d
    rec = {r["id"]: r for r in A[best["id"]]["records"]}
    scored = [r for r in rec.values() if r["retrieval"]["n_gold"]]
    ranks = [r["retrieval"]["rank"] for r in scored]
    hist = {str(k): sum(1 for x in ranks if x == k) for k in range(1, 11)}
    hist["none"] = sum(1 for x in ranks if x is None)
    r5 = sum(1 for x in ranks if x and x <= 5) / len(scored)
    mrr = sum((1 / x if x else 0) for x in ranks) / len(scored)
    lat = [r["retrieval_s"] for r in rec.values()]
    tot = [r["total_s"] for r in rec.values()]
    edges = [i / 2000 for i in range(66, 114)]  # 0.5 ms bins, 33.0..56.5 ms
    lat_hist = [[round(e * 1000, 1), sum(1 for x in lat if e <= x < e + 0.0005)] for e in edges]
    assert sum(c for _, c in lat_hist) == len(lat)
    miss = sorted([r for r in scored if r["retrieval"]["rank"] is None], key=lambda r: r["id"])
    qmap = {q["id"]: q for q in (json.loads(l) for l in (DUMP / "eval" / "questions.jsonl").read_text().splitlines() if l.strip())}

    import re

    def pages_of(cite):
        m = re.search(r"\bpp?\.(\d+)(?:-(\d+))?", cite)
        return set(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1)) if m else None

    def is_gold(it, q):  # a simplified evaluate.loc_match: same file, and the same page when the gold names one
        f = it["id"].split("#")[0]
        for g in q["gold_sources"]:
            if g.get("absent") or g["file"] != f:
                continue
            gp = g.get("pages") or ([g["page"]] if g.get("page") else None)
            ip = pages_of(it["cite"])
            if not gp or not ip or set(gp) & ip:
                return True
        return False

    def qview(i):
        r, q = rec[i], qmap[i]
        rt = r["retrieval"]
        top = [{"cite": it["cite"], "gold": is_gold(it, q)} for it in r["items"][:10]]
        first = next((n for n, t in enumerate(top, 1) if t["gold"]), None)
        if i in ("Q-EMMA", "Q-0412", "Q-602", "Q-401", "Q-101", "Q-002", "Q-007"):  # the ones the slides mark by hand
            assert first == rt.get("rank"), (i, first, rt.get("rank"))
        return {"id": i, "question": q["question"], "type": q["type"], "rank": rt["rank"], "hit@5": rt.get("hit@5"),
                "rr": rt.get("rr"), "cov@5": rt.get("cov@5"), "n_gold": rt["n_gold"],
                "top5": [it["cite"] for it in r["items"][:5]], "top10": top, "gold_files": sorted({g["file"].split("/")[-1] for g in q["gold_sources"] if not g.get("absent")}),
                "retrieval_ms": round(r["retrieval_s"] * 1000, 1), "total_s": round(r["total_s"], 2),
                "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"], "cost_usd": r["cost_usd"],
                "judge": r["judge"], "fact": r["fact"], "citation": r["citation"], "answer": r["answer"],
                "must_contain": q["must_contain"]}

    per_q = {"Q-EMMA": qview("Q-EMMA"), "Q-0412": qview("Q-0412"), "Q-602": qview("Q-602"), "Q-401": qview("Q-401"),
             "Q-101": qview("Q-101"), "Q-902": qview("Q-902"),
             "miss_example": qview(miss[0]["id"]) if miss else None}
    # pick a rank-3..5 example too, so MRR shows a fraction other than 1 and 1/2
    mid = sorted([r for r in scored if r["retrieval"]["rank"] in (3, 4, 5)], key=lambda r: r["id"])
    per_q["rank_mid_example"] = qview(mid[0]["id"]) if mid else None

    # ---------------- failure examples on the chosen config (answers)
    def fail_ex(t, pred):
        xs = sorted([r for r in rec.values() if r["type"] == t and pred(r)], key=lambda r: r["id"])
        return [qview(x["id"]) for x in xs[:3]], len(xs)

    failures = {}
    for t in ("procedure", "permission", "table_lookup", "multi_hop", "version_conflict"):
        ex, n = fail_ex(t, lambda r: not r["judge"]["ok"])
        failures[t] = {"n_type": sum(1 for r in rec.values() if r["type"] == t), "n_judged_wrong": n, "examples": ex}

    # ---------------- the 9 answered configs: k=5 vs k=10 on the same retrieval
    answered = [{"config": c, "label": d.get("label"), **{k: d["summary"]["overall"][k] for k in ("answer_correct", "fact_correct", "citation_correct")},
                 "retrieval_p95_s": d["summary"]["overall"]["retrieval_s"]["p95"], "total_p95_s": d["summary"]["overall"]["total_s"]["p95"],
                 "cost_per_q_usd": d["summary"]["overall"]["cost_per_q_usd"]} for c, d in A.items()]
    spend = {"answer_usd": round(sum(r["cost_usd"] for d in A.values() for r in d["records"]), 4),
             "judge_usd": round(sum(r["judge"].get("cost_usd", 0) for d in A.values() for r in d["records"]), 4),
             "n_answers": sum(len(d["records"]) for d in A.values())}

    # ---------------- how big the experiment was
    builds = G["builds"]
    n_q = 224
    search_s_local = sum(r["local_latency_s"]["mean"] * n_q for r in rows)
    scale = {"n_rows": G["n_rows"], "n_chunkings": len(builds), "settings_per_chunking": G["n_rows"] // len(builds),
             "questions": n_q, "scored_questions": base_row["overall"]["n"],
             "searches": G["n_rows"] * n_q, "machine": G["machine"],
             "chunks_min": min(b["n_chunks"] for b in builds.values()), "chunks_max": max(b["n_chunks"] for b in builds.values()),
             "build_s_sum": round(sum(b["build_s_total"] for b in builds.values()), 1),
             "build_s_max": max(b["build_s_total"] for b in builds.values()),
             "search_s_sum_measured": round(search_s_local, 1),
             "vectors_embedded": sum(b["n_chunks"] * len(b["models"]) for b in builds.values()),
             "under_budget_rows": sum(1 for r in rows if r["latency_s"]["p95"] <= G["budget_p95_s"])}
    if walls:
        w = [v["wall_s"] for v in walls.values() if v.get("wall_s")]
        scale["container_wall_s"] = {"n": len(w), "sum": round(sum(w), 1), "max": max(w), "min": min(w), "median": round(statistics.median(w), 1),
                                     "max_parallel": 16}

    # ---------------- the one-document playground (dense section's log), for the comparison
    play = None
    pd = LOGS / "v5_dense.json"
    if pd.exists():
        D = json.loads(pd.read_text())
        play = {"source": "logs/v5_dense.json (dense section, generated %s)" % D.get("generated"),
                "doc": D.get("doc"), "model": D.get("model_info", {}).get("hf"),
                "rank_of_6.2_by_size": {k: {"n_chunks": v["n"], "rank62": v["rank62"], "rank64": v["rank64"]}
                                        for k, v in D["play"].items() if k.startswith("s") and k.endswith("o15") or k == "whole"}}

    out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "script": "experiments/v5_engineer_slices.py",
           "what": "One knob at a time from the chosen config (rag_best.json): every other knob held at its chosen value. "
                   "recall@k over the 205 scored questions; p95 = search time per question on the grid's Modal L4 "
                   "(includes the recorded LLM call when rewriting is on).",
           "base": {**base, "k": best["k"], "id": best["id"], **row_view(base_row)},
           "targets": B["targets"], "rule": B["rule"], "scale": scale, "slices": S,
           "per_question": per_q,
           "rank_hist": hist, "check": {"recall@5_from_records": round(r5, 4), "mrr_from_records": round(mrr, 4),
                                        "grid_recall@5": base_row["overall"]["recall@5"], "grid_mrr": base_row["overall"]["mrr"]},
           "latency": {"n": len(lat), "p50_s": round(pct(lat, 50), 4), "p95_s": round(pct(lat, 95), 4), "min_s": round(min(lat), 4),
                       "max_s": round(max(lat), 4), "hist_ms": lat_hist, "slowest5_ms": sorted(round(x * 1000, 1) for x in lat)[-12:],
                       "n_above_p95": sum(1 for x in lat if x > pct(lat, 95)), "n_at_or_below_p50": sum(1 for x in lat if x <= pct(lat, 50)),
                       "total_p50_s": round(pct(tot, 50), 2), "total_p95_s": round(pct(tot, 95), 2)},
           "scorecard": {"retrieval": B["retrieval"], "answers": B["answers"], "honest": B["honest"], "judge_vs_fact": B["judge_vs_fact"],
                         "answers_by_type": B["answers_by_type"], "config": B["config"]},
           "answered": answered, "answer_spend": spend, "failures": failures,
           "failure_logs": {k: F[k] for k in ("multi_hop", "tables", "Q-401 (reorder level of BAT-500)") if k in F} |
                           {"version_conflict": {k: F["version_conflict"][k] for k in ("n", "stale_in_top5", "stale_ranked_above_gold")},
                            "version_examples": [q for q in F["version_conflict"]["questions"] if q["stale_before_gold"]][:2],
                            "Q-EMMA best": F.get("Q-EMMA best")},
           "playground": play}
    # the real code that runs the grid (l3_modal.py, _eval_chunking) and the race's overall numbers (for the race slide)
    src = (HERE / "l3_modal.py").read_text().splitlines()
    a = next(i for i, l in enumerate(src) if l.startswith("def _eval_chunking"))
    out["code"] = {"file": "experiments/l3_modal.py", "from": a + 1, "lines": src[a:a + 19]}
    R = json.loads((LOGS / "race.json").read_text())
    out["race"] = {"overall": R["overall"], "targets": R["targets"], "what": R["what"]}
    q = qmap["Q-EMMA"]
    out["golden_emma"] = {"id": q["id"], "type": q["type"], "question": q["question"], "n_gold": len([g for g in q["gold_sources"] if not g.get("absent")]),
                          "gold": [{"file": g["file"].split("/")[-1], "section": g.get("section"), "absent": bool(g.get("absent"))} for g in q["gold_sources"]],
                          "must_contain": q["must_contain"], "reference_answer": q["reference_answer"]}
    audit = json.loads((LOGS / "audit.json").read_text())["totals"]
    out["context"] = {"files": audit["files"], "chunks": B["index"]["n_chunks"],
                      "doc_units": len(D["units"]) if pd.exists() else None,
                      "doc_chunks": D["play"]["s200-o15"]["n"] if pd.exists() else None,
                      "doc_chunks_400": D["play"]["s400-o15"]["n"] if pd.exists() else None,
                      "day_usd_224": round(B["answers"]["cost_per_q_usd"] * 224, 2),
                      "search_share_of_answer_p95": round(B["retrieval"]["latency_s"]["p95"] / B["answers"]["total_s"]["p95"], 4),
                      "rerank_gain_points": round(100 * (base_row["overall"]["recall@5"] - find(rerank=False)["overall"]["recall@5"]), 1),
                      "rerank_cost_ms": round(1000 * (base_row["latency_s"]["p95"] - find(rerank=False)["latency_s"]["p95"]), 1),
                      "k5_answer_correct": A[best["id"].replace("|k10", "|k5")]["summary"]["overall"]["answer_correct"],
                      "gpu_hours": round(walls and sum(v["wall_s"] for v in walls.values()) / 3600 or 0, 1)}
    (LOGS / "v5_engineer_slices.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    js = HERE.parent / "v5" / "engineer_data.js"
    js.write_text("/* Generated by experiments/v5_engineer_slices.py from experiments/logs/v5_engineer_slices.json. Do not edit by hand. */\n"
                  "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.engineer = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print("wrote", js)
    print("wrote", LOGS / "v5_engineer_slices.json")
    for k, v in S.items():
        if isinstance(v, list):
            print(k, [(x["setting"], x.get("recall@5", x.get("recall")), x.get("p95_s")) for x in v])
    print("interaction", inter)
    print("check", out["check"], "latency", {k: out["latency"][k] for k in ("p50_s", "p95_s", "total_p50_s", "total_p95_s")})
    print("scale", scale)


@app.local_entrypoint()
def main(no_modal: bool = False):
    walls = None if no_modal else grid_walls.remote()
    main_local(walls)
