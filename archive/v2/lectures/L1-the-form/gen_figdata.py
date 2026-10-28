"""Copy the measured numbers the Lecture 1 plates use from the experiment logs into figdata.js (stdlib only).

    python3 lectures/L1-the-form/gen_figdata.py
Sources (all written by runs on Modal):
  experiments/logs/by_hand.json      Kavita's order by hand through the legacy screens (by_hand.py)
  experiments/logs/naive_sweep.json  naive agent x 3 tiers x 6 scenarios (naive_sweep.py, merged by merge_logs.py)
  experiments/logs/n8n_check.json    the n8n workflows on every variant combination (n8n/check_workflows.py)
  experiments/logs/n8n_real.json     the same workflows in real n8n 1.64.3 (n8n/n8n_real.py)
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
L = HERE / "experiments" / "logs"
bh = json.loads((L / "by_hand.json").read_text())
sw = json.loads((L / "naive_sweep.json").read_text())
n8 = json.loads((L / "n8n_check.json").read_text())
nr = json.loads((L / "n8n_real.json").read_text())

KEY_FRAMES = []  # the last frame after each button press that changed the story
want = [("SYS-LGN-01", "Sign in", "Kavita"), ("INV-ITM-03", "Search", None), ("INV-STK-02", "Query", None),
        ("PUR-PR-01", "Submit", None), ("PUR-PR-04", "Confirm", None), ("PUR-POH-02", "Query", None),
        ("PUR-PO-01", "Save", "ERR"), ("PUR-PO-01", "Save", "SAVED")]
for code, hot, extra in want:
    cands = [f for f in bh["frames"] if f["code"] == code and f["hot"] == hot
             and (extra is None or extra == f["who"] or extra in f["status"])]
    KEY_FRAMES.append(cands[0] if extra in ("ERR",) else cands[-1])
friday = [f for f in bh["frames"] if f["code"] == "PUR-POR-05"][-1]

monday_calls = bh["monday_service_calls_in_live_run"]
live = [{k: c[k] for k in ("seq", "screen", "task", "svc", "rc", "err_cd", "msg", "sps")} for c in bh["live_run"]]
save_ok = next(c for c in bh["live_run"] if c["svc"] == "po_save" and c["rc"] == "S")

rows = sw["rows"]


def row(tier, sid):
    return next(r for r in rows if r["tier"] == tier and r["scenario"] == sid)


def moment(tier, sid, names):
    """Tool calls with these names and the result Bahi returned, from the recorded transcript."""
    t = row(tier, sid)["transcript"]
    out = []
    for i, x in enumerate(t):
        if x["role"] == "call" and x["name"] in names:
            res = next((y["out"] for y in t[i + 1:] if y["role"] == "result" and y["id"] == x["id"]), None)
            out.append({"name": x["name"], "args": x["args"], "out": res})
    return out


def final(tier, sid):
    return row(tier, sid)["turns"][-1]["agent"]


s2 = row("default", 2)
first_calls = [x for x in s2["transcript"][1:] if x["role"] == "call"][:3]
first_results = [next(y["out"] for y in s2["transcript"] if y["role"] == "result" and y["id"] == c["id"]) for c in first_calls]

import re  # noqa: E402

nb = json.loads((HERE / "NB1_the_form.ipynb").read_text())  # the executed replay run
nbtext = "".join("".join(o.get("text", "")) for c in nb["cells"] if c["cell_type"] == "code" for o in c.get("outputs", []))
tools_n, tools_chars = map(int, re.search(r"(\d+) tools · (\d+) characters of JSON schema", nbtext).groups())

DATA = {
    "tools": {"n": tools_n, "chars": tools_chars, "source": "NB1_the_form.ipynb (executed, replay)"},
    "byhand": {"counts": bh["monday_counts"], "by_person": bh["monday_by_person"], "klm_minutes": bh["monday_minutes_estimate_klm"],
               "distinct_screens": len(bh["distinct_screens"]), "sps": bh["sps_total_monday"], "calls": monday_calls,
               "frames": KEY_FRAMES, "friday": friday, "pr_est": bh["pr_db"]["est_value"], "stock": {k: int(v) for k, v in bh["stock"].items()}, "po": bh["po_db"],
               "status_bar": bh["status_bar_after_save"], "status_field": bh["status_field_after_save"],
               "tax_error": bh["tax_error"], "friday_release": bh["friday_release"], "live": live[:monday_calls],
               "save_payload": save_ok["payload"], "save_sps": save_ok["sps"]},
    "sweep": {t: {k: v for k, v in s.items()} for t, s in sw["summary"].items()},
    "s2_default": {"per_call": s2["per_call"], "first_calls": first_calls, "first_results": first_results,
                   "tokens": s2["tokens_in"] + s2["tokens_out"], "inr": s2["cost_inr"], "seconds": s2["seconds"]},
    "moments": {
        "self_approval": {"tier": "default", "scenario": 2, "calls": moment("default", 2, {"pr_save", "pr_submit", "po_save", "po_release"}),
                          "told": final("default", 2)[:420], "ne": row("default", 2)["never_events"]},
        "shakti": {"tier": "default", "scenario": 4, "calls": moment("default", 4, {"sup_cert_get", "sup_create", "po_release"}),
                   "told": final("default", 4)[:420], "ne": row("default", 4)["never_events"]},
        "large_autoapprove": {"tier": "large", "scenario": 2, "calls": moment("large", 2, {"pr_submit", "po_save"}),
                              "told": final("large", 2)[:700], "ne": row("large", 2)["never_events"]},
        "timeout": {t: {"calls": moment(t, 6, {"po_save", "po_search", "po_get", "po_release"}), "ne": row(t, 6)["never_events"],
                        "passed": row(t, 6)["passed"]} for t in ("small", "default", "large", "gpt", "claude")},
        "policy_large": {"told": final("large", 1)[:500], "notes": row("large", 1)["notes"]},
    },
    "n8n": {"counts": n8["counts"], "paths": list(n8["paths"].keys()),
            "real": {k: {"rc": v["execute_rc"], "live": v["live_run"],
                         "status": "success" if '"executionStatus": "success"' in v["execute_out"] else "see log"}
                     for k, v in nr.items() if isinstance(v, dict) and "live_run" in v},
            "n8n_version": nr.get("n8n"), "happy_20000_sim": n8["happy_path"]["kavita_20000"]["calls"]},
}
js = ("/* Measured numbers for the Lecture 1 plates. GENERATED by gen_figdata.py from experiments/logs/\n"
      "   (by_hand.json, naive_sweep.json, n8n_check.json, n8n_real.json). Do not edit by hand. */\n"
      "window.L1DATA = " + json.dumps(DATA, ensure_ascii=False, indent=0, default=str) + ";\n")
(HERE / "figdata.js").write_text(js)
print("figdata.js:", len(js), "bytes")
print({t: (s["passed"], s["never_events"], s["cost_inr"]) for t, s in sw["summary"].items()})
