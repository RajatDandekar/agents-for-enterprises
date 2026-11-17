"""Error analysis on our own runs (Lecture 6, Section 2): the notes we wrote reading the failing traces, grouped.

    python3 experiments/error_analysis.py      (standard library; reads logs/suite_v1_*.json and the later rounds)

Round 1 is the first suite run (suite_v1_*): every failing check was read in its trace and given a note (open coding);
the notes were then grouped (axial coding) into categories, each with WHO was wrong: the agent, the eval, a tool, or the
infrastructure. The counts below are computed from the logs by the rule written next to each category, so they can be
re-checked; the rules encode the notes, they did not write them. Later rounds (the CI gate, the replay) added three more.
Writes logs/error_analysis.json.
"""
import json
import pathlib

L = pathlib.Path(__file__).parent / "logs"
v1 = [json.loads((L / f).read_text()) for f in ("suite_v1_good_k3.json", "suite_v1_thursday_k1.json")]
rows = [(d["prompt"], r) for d in v1 for r in d["rows"]]
fails = [(p, r, c) for p, r in rows for c in r["checks"] if not c["pass"]]
errors = [(p, r) for p, r in rows if r["error"]]

CATS = [
    {"id": "vat_label", "who": "tool", "name": "It would not say the value includes VAT",
     "note": "The preview's estimated_value is gross (the tool multiplies by 1.20) but says so nowhere; the agent hedged, "
             "the judge failed it.", "fix": "criteria reworded; recommended: the tool returns includes_vat: true",
     "rule": lambda p, r, c: c["kind"] == "words" and "VAT" in c["why"] },
    {"id": "judge_cut", "who": "eval", "name": "The judge's answer was cut off or empty, read as a fail",
     "note": "Reading the judge's raw output: 400 tokens were not enough; half a JSON object, or nothing, became 'fail'.",
     "fix": "1,000 tokens, a 40-word reason, read the verdict field even from a cut reply",
     "rule": lambda p, r, c: c["kind"] == "words" and (not c["why"].strip() or c["why"].strip().startswith("{"))},
    {"id": "asked_date", "who": "eval", "name": "It asked Emma for the need-by date instead of previewing",
     "note": "The usual in memory has no date and the tool needs one. Asking is right; our task demanded a preview.",
     "fix": "the incident tasks give the date; the check accepts the question",
     "rule": lambda p, r, c: r["task"] in ("T01", "T02", "T03") and not any(
         x["tool"] == "create_purchase_request" for x in r["turns"][0]["calls"])},
    {"id": "own_requests", "who": "tool", "name": "It could not find Emma's own request without its number",
     "note": "No tool lists the requests Emma raised; list_my_approvals is for approvers.",
     "fix": "tasks give the number; recommended: a list_my_requests tool",
     "rule": lambda p, r, c: r["task"] in ("T15", "T18")},
    {"id": "memory_evidence", "who": "eval", "name": "The judge had not seen the memory the agent used",
     "note": "Emma's £250,000 limit is in MEMORY.md, loaded in the window; the judge only got tool results.",
     "fix": "memory added to the judge's evidence",
     "rule": lambda p, r, c: r["task"] == "T20" and c["kind"] in ("words", "numbers")},
    {"id": "own_money", "who": "agent", "name": "It worked out money itself",
     "note": "2,400 x £119 = £285,600 written by the model, against the prompt's rule (the preview gives the value).",
     "fix": "kept as a real failure; the numbers check catches it",
     "rule": lambda p, r, c: c["kind"] == "numbers" and "285,600" in c["why"]},
]
out = {"round1": {"runs": len(rows), "failing_runs": sum(1 for p, r in rows if not r["pass"]), "failing_checks": len(fails),
                  "errored_runs": len(errors), "categories": []}}
seen = set()
for cat in CATS:
    hits = [(p, r, c) for p, r, c in fails if cat["rule"](p, r, c) and (id(c) not in seen)]
    for _, _, c in hits:
        seen.add(id(c))
    out["round1"]["categories"].append({k: cat[k] for k in ("id", "who", "name", "note", "fix")} | {
        "checks": len(hits), "runs": len({(p, r["task"], r["rep"]) for p, r, _ in hits}),
        "examples": [f"{p} {r['task']} run {r['rep'] + 1}: {c['why'][:140]}" for p, r, c in hits[:3]]})
other = [(p, r, c) for p, r, c in fails if id(c) not in seen]
out["round1"]["categories"].append({"id": "other", "who": "mixed", "name": "Other single failures (read one by one)", "note": "",
                                    "fix": "", "checks": len(other), "runs": len({(p, r["task"], r["rep"]) for p, r, _ in other}),
                                    "examples": [f"{p} {r['task']} run {r['rep'] + 1} {c['kind']}: {c['why'][:120]}" for p, r, c in other[:6]]})
out["round1"]["infra"] = {"id": "import_race", "who": "infra", "name": "Two threads imported httpx at once", "runs": len(errors),
                          "examples": [f"{p} {r['task']}: {r['error'][:120]}" for p, r in errors],
                          "fix": "openai and httpx imported once, before the threads start"}
out["later"] = [
    {"id": "evidence_encoding", "who": "eval", "found": "suite v2, T20", "name": "A £ figure that was there was flagged as made up",
     "note": "The record kept 1,800 ASCII-escaped characters of each tool result: '£1,000,000' in the policy text became "
             "'\\u00a31,000,000' or was cut off.", "fix": "6,000 characters, unescaped"},
    {"id": "gate_too_strict", "who": "eval", "found": "the first CI run", "name": "The gate failed the good prompt",
     "note": "T01's trajectory check demanded a preview; that run asked for the date first.", "fix": "the check accepts the question"},
    {"id": "guard_refused_yes", "who": "guard", "found": "the replay", "name": "The guard refused Emma's real yes",
     "note": "After 'Yes, go ahead' the agent previewed again; the guard overwrote the preview's turn and refused the commit.",
     "fix": "keep the first preview's turn"},
]
v2 = [json.loads((L / f).read_text()) for f in ("suite_good_k3.json", "suite_thursday_k1.json")]
out["after"] = {"v1": {d["prompt"]: f"{d['passed_runs']}/{d['runs']}" for d in v1}, "v2": {d["prompt"]: f"{d['passed_runs']}/{d['runs']}" for d in v2}}
(L / "error_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for c in out["round1"]["categories"]:
    print(f"{c['who']:6} {c['checks']:3} checks {c['runs']:3} runs  {c['name']}")
print(out["round1"]["infra"]["runs"], "infra;", out["after"])
