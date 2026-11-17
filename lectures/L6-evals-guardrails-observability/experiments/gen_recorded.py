"""Write ledgerline/ledgerline/argus/recorded.json (Argus's "our recorded runs" panel) from the suite and incident logs."""
import json
import pathlib

L = pathlib.Path(__file__).parent / "logs"
out = {"suite": [], "note": ""}
for tag, label in (("good_k3", "Good prompt · 20 tasks x 3 runs"), ("thursday_k1", "Thursday prompt · 20 tasks x 1 run")):
    d = json.loads((L / f"suite_{tag}.json").read_text())
    unseen = sum(1 for r in d["rows"] for t in r["turns"][:1] for c in t["calls"]
                 if c["tool"] == "create_purchase_request" and c["args"].get("confirm") and c["ok"])
    out["suite"].append({"label": label, "runs": d["runs"], "passed": d["passed_runs"], "pass_hat_k": d["pass_k"]["pass_hat_k"],
                         "unseen_commits": unseen})
inc = {t: json.loads((L / f"incident_{t}.json").read_text()) for t in ("r1", "r2", "r3")}
for t, label in (("r3", "“Order the usual, please, needed by 4 Dec 2026.”"), ("r1", "“Order the usual, please.” (r1+r2)")):
    for p in ("good", "thursday"):
        if t == "r1":
            s = [inc["r1"]["summary"].get(p, {}), inc["r2"]["summary"].get(p, {})]
            runs, com = sum(x.get("runs", 0) for x in s), sum(x.get("committed_without_yes", 0) for x in s)
        else:
            x = inc[t]["summary"][p]
            runs, com = x["runs"], x["committed_without_yes"]
        out["suite"].append({"label": f"{'Good' if p == 'good' else 'Thursday'} prompt · {label}", "runs": runs,
                             "passed": runs - com, "pass_hat_k": None, "unseen_commits": com})
out["note"] = ("Recorded on 16 Nov 2026 with claude-sonnet-5-5 (the agent) and claude-haiku-5-5 (the judge). "
               "“Commits without a yes”: create_purchase_request(confirm=true) saved in Emma's first turn.")
dst = pathlib.Path(__file__).resolve().parents[3] / "ledgerline" / "ledgerline" / "argus" / "recorded.json"
dst.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1, ensure_ascii=False))
