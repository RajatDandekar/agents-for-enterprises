"""Lecture 4: merge the experiment logs into logs/analysis.json, the numbers the deck's charts read.

The main runs are logs/granularity_<model>.json. Five cells there ended in a client error that was not the model's
doing (an httpx import race when 16 threads first loaded the OpenAI client at once): flash raw A10, flash toolbox
L14, L15, A01 and flash-lite toolbox A02. Each was re-run alone (--only ... --workers 1) into
logs/granularity_<model>_<ids>.json, and that re-run replaces the errored cell here. The cells replaced are listed.
Pure standard library.
"""
import json
import pathlib

LOG = pathlib.Path(__file__).resolve().parent / "logs"
MODELS = {"flash": "gemini_gemini-3.8-flash", "lite": "gemini_gemini-3.5-flash-lite"}


def summary(rs):
    n = len(rs)
    return {"tasks": n, "passed": sum(r["passed"] for r in rs),
            "never_events": sum(len(r["never_events"]) for r in rs), "errors": sum(1 for r in rs if r["error"]),
            "tool_calls_mean": round(sum(r["tool_calls"] for r in rs) / n, 1),
            "bahi_refusals_total": sum(r["failed_services"] for r in rs),
            "tokens_mean": round(sum(r["tokens_in"] + r["tokens_out"] for r in rs) / n),
            "seconds_mean": round(sum(r["seconds"] for r in rs) / n, 1),
            "inr_mean": round(sum(r["cost_inr"] for r in rs) / n, 2), "inr_total": round(sum(r["cost_inr"] for r in rs), 2)}


out = {"source": "logs/granularity_*.json merged by analyse.py", "models": {}}
for tag, m in MODELS.items():
    main = json.loads((LOG / f"granularity_{m}.json").read_text())
    res = {(r["config"], r["task"]): r for r in main["results"]}
    replaced = []
    for p in sorted(LOG.glob(f"granularity_{m}_*.json")):
        for r in json.loads(p.read_text())["results"]:
            key = (r["config"], r["task"])
            if res[key]["error"]:
                replaced.append({"cell": f"{key[0]} {key[1]}", "first_error": res[key]["error"][:120], "rerun_file": p.name})
                res[key] = r
    rows = list(res.values())
    block = {"model": main["model"], "replaced": replaced, "configs": {}, "grid": []}
    for c in ("raw", "toolbox"):
        block["configs"][c] = {k: summary([r for r in rows if r["config"] == c and (k == "all" or r["kind"] == k)])
                               for k in ("all", "lookup", "action")}
    for t in main["tasks"]:
        row = {"id": t["id"], "kind": t["kind"], "ask": t["ask"], "trap": t["trap"]}
        for c in ("raw", "toolbox"):
            r = res[(c, t["id"])]
            row[c] = {"pass": r["passed"], "note": (r["note"] or "") + (" " + "; ".join(r["never_events"]) if r["never_events"] else ""),
                      "calls": r["tool_calls"], "tokens": r["tokens_in"] + r["tokens_out"], "refusals": r["failed_services"]}
        block["grid"].append(row)
    out["models"][tag] = block
    for c in ("raw", "toolbox"):
        print(tag, c, json.dumps(block["configs"][c]["all"]))
    print("  replaced:", [x["cell"] for x in replaced])
(LOG / "analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
