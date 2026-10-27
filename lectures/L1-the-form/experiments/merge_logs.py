"""Merge the naive-sweep parts (run in parallel on Modal) into one log and one cassette. Standard library only.

    python3 lectures/L1-the-form/experiments/merge_logs.py
-> logs/naive_sweep.json  (all rows + a per-tier summary)   and   bahi/bahi/cassettes/L1_naive.jsonl
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
CAS = HERE.parents[2] / "bahi" / "bahi" / "cassettes"
TIERS = [("small", "gemini:gemini-3.5-flash-lite"), ("default", "gemini:gemini-3.8-flash"), ("large", "gemini:gemini-3.1-pro-preview")]

rows = []
for tier, _ in TIERS:
    for p in sorted(LOGS.glob(f"naive_{tier}_s*.json")):
        rows += json.loads(p.read_text())
rows.sort(key=lambda r: (["small", "default", "large"].index(r["tier"]), r["scenario"]))

summary = {}
for tier, model in TIERS:
    rs = [r for r in rows if r["tier"] == tier]
    ok = [r for r in rs if r.get("error") is None]
    summary[tier] = {
        "model": model, "scenarios_run": len(rs), "errors": [r["error"] for r in rs if r.get("error")],
        "passed": sum(1 for r in ok if r["passed"]),
        "never_events": sum(len(r["never_events"]) for r in ok),
        "scenarios_with_never_event": sum(1 for r in ok if r["never_events"]),
        "tool_calls": sum(r["tool_calls"] for r in ok), "llm_calls": sum(r["llm_calls"] for r in ok),
        "tokens_in": sum(r["tokens_in"] for r in ok), "tokens_out": sum(r["tokens_out"] for r in ok),
        "model_seconds": round(sum(r["seconds"] for r in ok), 1), "cost_inr": round(sum(r["cost_inr"] for r in ok), 2),
        "per_scenario": [{"id": r["scenario"], "passed": r["passed"], "ne": [n.split()[0] for n in r["never_events"]],
                          "tools": r["tool_calls"], "llm_calls": r["llm_calls"], "tokens": r["tokens_in"] + r["tokens_out"],
                          "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"],
                          "seconds": r["seconds"], "inr": r["cost_inr"], "step_cap": r["hit_step_cap"],
                          "turns": len(r["turns"]), "asked_kavita": len(r["turns"]) > 1 and not r["turns"][1]["user"].startswith("Rohit")} for r in ok],
    }
    n = max(1, len(ok))
    s = summary[tier]
    s["avg_tokens"] = round((s["tokens_in"] + s["tokens_out"]) / n)
    s["avg_seconds"] = round(s["model_seconds"] / n, 1)
    s["avg_inr"] = round(s["cost_inr"] / n, 2)
    s["inr_per_pass"] = round(s["cost_inr"] / s["passed"], 2) if s["passed"] else None

(LOGS / "naive_sweep.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, ensure_ascii=False))

parts = sorted(CAS.glob("L1_naive_part_*.jsonl"))
if parts:
    seen, out = set(), []
    for p in parts:
        for line in p.read_text().splitlines():
            if line.strip():
                k = json.loads(line)["key"]
                if k not in seen:
                    seen.add(k)
                    out.append(line)
    (CAS / "L1_naive.jsonl").write_text("\n".join(out) + "\n")
    for p in parts:
        p.unlink()
    print(f"cassette L1_naive.jsonl: {len(out)} recorded replies from {len(parts)} parts")
for t, s in summary.items():
    print(t, {k: v for k, v in s.items() if k != "per_scenario"})
