"""Write lectures/L3-the-memory/v5/store_data.js (window.L3V5.store) from the store logs. No numbers are typed in here.

    python3 lectures/L3-the-memory/experiments/v5_store_data.py

Sources: logs/v5_store_local.json (Chroma, v5_store_local.py), logs/hnsw_check.json (l3_modal.py::hnsw_check),
logs/v5_store_research.json (the 4 Nov 2026 survey), logs/v5_store_ingest.json + logs/v5_store_cloud.json (Qdrant Cloud,
v5_store_cloud.py), logs/v5_store_selfhost.json (the same script against a self-hosted Qdrant on Modal), logs/v5_store_latency.json
(v5_store_latency.py: latency parts, round-trip levers, payload facts, Q-605 filter demo), logs/v5_lexical_rerank_latency.json
(the reranker's time), and the dump's eval/questions.jsonl + facts.jsonl (what each Q-605 source says).
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOGS = HERE / "logs"
V5 = HERE.parent / "v5"


def load(name):
    p = LOGS / name
    return json.loads(p.read_text()) if p.exists() else None


def slim_cloud(c):
    if not c:
        return None
    c = dict(c)
    info = c.pop("collection_info", None) or {}
    c["info"] = {"status": info.get("status"), "points_count": info.get("points_count"),
                 "indexed_vectors_count": info.get("indexed_vectors_count"), "segments_count": info.get("segments_count"),
                 "payload_schema": {k: (v.get("data_type") if isinstance(v, dict) else v)
                                    for k, v in (info.get("payload_schema") or {}).items()},
                 "points_per_field": {k: v.get("points") for k, v in (info.get("payload_schema") or {}).items() if isinstance(v, dict)}}
    return c


def slim_ingest(i):
    if not i:
        return None
    i = dict(i)
    info = i.pop("info", None) or {}
    cfg = info.get("config") or {}
    i["info"] = {"status": info.get("status"), "points_count": info.get("points_count"),
                 "indexed_vectors_count": info.get("indexed_vectors_count"), "segments_count": info.get("segments_count"),
                 "vectors": (cfg.get("params") or {}).get("vectors"), "hnsw": cfg.get("hnsw_config"),
                 "payload_schema": {k: (v.get("data_type") if isinstance(v, dict) else v)
                                    for k, v in (info.get("payload_schema") or {}).items()}}
    i["D"] = {k: v for k, v in i["D"].items() if k != "ids"}
    return i


def q605_says():
    """file -> the limit that file gives, from the golden set's own facts for Q-605 (no number typed here)."""
    import re
    dump = pathlib.Path("/Users/raj/Claude_Brain/northbridge-docs/eval")
    if not dump.exists():
        return None
    q = next(json.loads(l) for l in open(dump / "questions.jsonl") if '"Q-605"' in l)
    facts = {f["id"]: f for f in (json.loads(l) for l in open(dump / "facts.jsonl") if l.strip())}
    out = {}
    for fid in q["fact_ids"]:
        f = facts.get(fid) or {}
        m = re.search(r"£[\d,]+", f.get("statement", ""))
        if m and f.get("file"):
            st = f["statement"]
            out[f["file"]] = m.group(0) + (" net" if " net " in st else " gross" if "gross" in st else "")
    return out


def slim_latency(r):
    """Drop the hit texts; keep, per Q-605 hit, the limit it states (from the golden facts, found in its text)."""
    if not r:
        return None
    says = q605_says() or {}
    f = r.get("eu", {}).get("facts", {})
    for name, modes in (f.get("q605") or {}).items():
        if not isinstance(modes, dict):
            continue
        for rows in modes.values():
            for x in rows:
                lim = says.get(x.get("file"))
                txt = x.pop("text", "") or ""
                x["says"] = lim if lim and lim.split()[0] in txt else None
    return r


def main():
    local = load("v5_store_local.json")
    if local:  # derived views of the HNSW headers (no new numbers): D's one segment, the dump's main segment
        local["D"]["hnsw_headers_first"] = next(iter(local["D"]["hnsw_headers"].values()))
        main_seg = max(local["dump"]["hnsw_headers"].values(), key=lambda h: h["cur_element_count"])
        local["dump"]["hnsw_main"] = {**main_seg, "layers": main_seg["maxlevel"] + 1}
        local["D"].pop("chunks", None)
    sh = load("v5_store_selfhost.json")
    data = {
        "local": local,
        "hnsw": load("hnsw_check.json"),
        "research": load("v5_store_research.json"),
        "ingest": slim_ingest(load("v5_store_ingest.json")),
        "cloud": slim_cloud(load("v5_store_cloud.json")),
        "selfhost": {"ingest": slim_ingest(sh["ingest"]), "query": slim_cloud(sh["query"])} if sh else None,
        "dashboard": load("v5_store_dashboard.json"),
        "ef": load("v5_store_ef.json"),
        "cloud_run1": (lambda r: r and {"rtt_ms": r["rtt_ms"], "hybrid_latency_s": r["golden"]["hybrid_rrf"]["latency_s"],
                                        "dense_latency_s": r["golden"]["dense"]["latency_s"]})(load("v5_store_cloud_run1_default_ef.json")),
        "latency": slim_latency(load("v5_store_latency.json")),
        "rerank": load("v5_lexical_rerank_latency.json"),
        "q605_says": q605_says(),
        "q605_amounts": list(dict.fromkeys(v.split()[0] for v in (q605_says() or {}).values())),
        "shots": sorted(p.name for p in (V5 / "img" / "store").iterdir() if p.suffix in (".png", ".jpg")) if (V5 / "img" / "store").exists() else [],
    }
    js = "/* generated by experiments/v5_store_data.py from experiments/logs/v5_store*.json and hnsw_check.json; do not edit */\n"
    js += "window.L3V5 = window.L3V5 || {};\nwindow.L3V5.store = " + json.dumps(data, ensure_ascii=False, indent=0) + ";\n"
    (V5 / "store_data.js").write_text(js)
    print("wrote", V5 / "store_data.js", len(js), "bytes; cloud:", bool(data["cloud"]), "selfhost:", bool(sh), "shots:", data["shots"])


if __name__ == "__main__":
    main()
