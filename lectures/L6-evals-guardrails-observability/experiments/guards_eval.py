"""Measuring the guards (Lecture 6, Section 3), on the guards image (Presidio, transformers, NeMo in /opt/nemo).

    tools/mrun.sh .../l6_modal.py --script guards_eval.py --image guards --args "--parts detectors,attacks"

Part 1 · detectors on labelled sets (ledgerline/course/l6/labelled.py), no agent:
    ProtectAI deberta-v3-base-prompt-injection-v2 (CPU, threshold 0.5), NeMo Guardrails self check input (Claude Haiku),
    Presidio (en_core_web_sm) on the PII set. Catch rate (recall on attacks), false alarms (on benign), latency, cost.
Part 2 · the 20 attacks through the agent (claude-sonnet-5-5), guards off and all guards on. Success is read from
    Ledgerline / the tool calls / the reply (attacks.succeeded), never judged by a model. Traced to Langfuse (tag guards).
Writes logs/guards_detectors.json and logs/guards_attacks.json.
"""
import argparse
import json
import subprocess
import time

from _common import LOGS, now, pmap, spend, write

ap = argparse.ArgumentParser()
ap.add_argument("--parts", default="detectors,attacks")
ap.add_argument("--sets", default="off,all")
ap.add_argument("--tag", default="r1")
ap.add_argument("--prompt", default="good")
ap.add_argument("--ids", default="")
a = ap.parse_args()


def rates(rows, key):
    pos = [r for r in rows if r["label"]]
    neg = [r for r in rows if not r["label"]]
    tp = sum(1 for r in pos if r[key])
    fp = sum(1 for r in neg if r[key])
    return {"attacks": len(pos), "caught": tp, "catch_rate": round(tp / max(1, len(pos)), 3), "benign": len(neg),
            "false_alarms": fp, "false_alarm_rate": round(fp / max(1, len(neg)), 3)}


if "detectors" in a.parts:
    from ledgerline.course.l6 import guards as G
    from ledgerline.course.l6.labelled import INJECTION, PII
    G.injection_score("warm up")
    G.redact("warm up")
    rows = []
    for it in INJECTION:
        p, ms = G.injection_score(it["text"])
        rows.append({**it, "deberta_p": round(p, 4), "deberta": p >= 0.5, "deberta_ms": ms})
    # NeMo, in its own environment
    (LOGS / "_nemo_in.json").write_text(json.dumps([{"id": r["id"], "text": r["text"]} for r in rows]))
    t0 = time.time()
    pr = subprocess.run(["/opt/nemo/bin/python", "nemo_check.py", str(LOGS / "_nemo_in.json"), str(LOGS / "_nemo_out.json")],
                        capture_output=True, text=True, timeout=3000)
    print(pr.stdout[-3000:], pr.stderr[-3000:])
    nemo = {x["id"]: x for x in json.loads((LOGS / "_nemo_out.json").read_text())} if (LOGS / "_nemo_out.json").exists() else {}
    for r in rows:
        n = nemo.get(r["id"], {})
        r["nemo"] = n.get("blocked")
        r["nemo_ms"] = n.get("ms")
        r["nemo_tokens"] = [n.get("tokens_in", 0), n.get("tokens_out", 0)]
        r["nemo_raw"] = (n.get("raw") or [None])[0]
        r["nemo_error"] = n.get("error")
    pii = []
    for it in PII:
        out, found, ms = G.redact(it["text"])
        pii.append({**it, "flagged": bool(found), "found": found, "redacted": out, "ms": ms})
    nemo_ok = [r for r in rows if r["nemo"] is not None]
    ntin = sum(r["nemo_tokens"][0] for r in rows)
    ntout = sum(r["nemo_tokens"][1] for r in rows)
    from ledgerline.course.l6.agent import usd
    nemo_usd = usd("claude-haiku-5-5", ntin, ntout)

    def med(xs):
        xs = sorted(x for x in xs if x is not None)
        return xs[len(xs) // 2] if xs else None
    out = {"at": now(), "set": {"injection": len(rows), "attacks": sum(r["label"] for r in rows), "pii": len(pii)},
           "deberta": {**rates(rows, "deberta"), "median_ms": med([r["deberta_ms"] for r in rows]), "usd": 0.0,
                       "model": "protectai/deberta-v3-base-prompt-injection-v2", "threshold": 0.5, "where": "CPU, in process"},
           "nemo": {**rates(nemo_ok, "nemo"), "median_ms": med([r["nemo_ms"] for r in nemo_ok]), "usd": round(nemo_usd, 5),
                    "usd_per_check": round(nemo_usd / max(1, len(nemo_ok)), 6), "checked": len(nemo_ok),
                    "errors": len(rows) - len(nemo_ok), "model": "claude-haiku-5-5 via NeMo Guardrails 0.24.1 self check input"},
           "presidio": {**rates(pii, "flagged"), "median_ms": med([r["ms"] for r in pii]), "usd": 0.0,
                        "model": "presidio-analyzer 2.2.366 + spaCy en_core_web_sm"},
           "rows": rows, "pii_rows": pii}
    out["deberta"]["missed"] = [r["id"] for r in rows if r["label"] and not r["deberta"]]
    out["deberta"]["false_alarm_ids"] = [r["id"] for r in rows if not r["label"] and r["deberta"]]
    out["nemo"]["missed"] = [r["id"] for r in nemo_ok if r["label"] and not r["nemo"]]
    out["nemo"]["false_alarm_ids"] = [r["id"] for r in nemo_ok if not r["label"] and r["nemo"]]
    write("guards_detectors.json", out)
    spend("guards_detectors_nemo", nemo_usd, len(nemo_ok), ntin, ntout, "claude-haiku-5-5", "NeMo self check input")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "pii_rows")}, indent=1))

if "attacks" in a.parts:
    from ledgerline.course.l6 import guards as G
    from ledgerline.course.l6.agent import Agent
    from ledgerline.course.l6.attacks import ATTACKS, setup, succeeded
    from ledgerline.course.l6.tracing import Tracing, trace_url
    from ledgerline.llm import LLM
    SETS = {"off": [], "deterministic": G.DETERMINISTIC + ["output_check"], "all": G.ALL}

    def one(job):
        gs, att = job
        att = json.loads(json.dumps({k: v for k, v in att.items()}))
        tr = Tracing(langfuse=True, public=True, batch=False,
                     redact=(lambda s: G.redact(s)[0]) if "pii" in SETS[gs] else None)
        guards = G.Guards(SETS[gs]) if SETS[gs] else None
        ag = Agent(a.prompt, guards=guards, tracing=tr, conversation_id=f"l6-guards-{a.tag}-{a.prompt}-{gs}-{att['id']}",
                   llm_for=lambda m: LLM(m, cassette=f"L6E_guards_{a.prompt}_{gs}", mode="record", max_tokens=8192),
                   tags=("L6", "guards", gs, att["id"], a.prompt))
        setup(ag, att)
        err = None
        try:
            for m in att["turns"]:
                ag.turn(m)
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {str(e)[:300]}"
        tr.flush()
        trace_text = json.dumps(tr.log.spans, default=str)
        ok, why = succeeded(ag, att, trace_text) if not err else (None, err)
        evs = [e for t in ag.turns for e in t.get("guard_events", [])]
        stopped = [e for e in evs if e["decision"] in ("refused", "blocked", "quarantined", "redacted", "flagged")]
        tid = ag.turns[-1].get("trace_id") if ag.turns else None
        return {"set": gs, "id": att["id"], "title": att["title"], "owasp": att["owasp"], "channel": att["channel"],
                "succeeded": ok, "why": why, "error": err, "stopped_by": sorted({e["guard"] for e in stopped}),
                "guard_events": evs, "replies": [t["reply"] for t in ag.turns],
                "calls": [{k: c[k] for k in ("tool", "args", "ok", "refused_by")} for t in ag.turns for c in t["calls"]],
                "usd": round(sum(t["usd"] for t in ag.turns), 5), "tokens_in": sum(t["tokens_in"] for t in ag.turns),
                "tokens_out": sum(t["tokens_out"] for t in ag.turns), "model_calls": sum(len(t["model_calls"]) for t in ag.turns),
                "trace_id": tid, "url": trace_url(tid) if tid else None}

    jobs = [(s, x) for s in a.sets.split(",") for x in ATTACKS if not a.ids or x["id"] in a.ids.split(",")]
    rows = pmap(one, jobs, workers=10)
    summ = {}
    for s in a.sets.split(","):
        rs = [r for r in rows if r["set"] == s and r["succeeded"] is not None]
        summ[s] = {"attacks": len(rs), "succeeded": sum(1 for r in rs if r["succeeded"]),
                   "asr": round(sum(1 for r in rs if r["succeeded"]) / max(1, len(rs)), 3),
                   "errors": sum(1 for r in rows if r["set"] == s and r["succeeded"] is None)}
    usd_ = sum(r["usd"] for r in rows)
    write(f"guards_attacks_{a.tag}.json", {"at": now(), "prompt": a.prompt, "sets": {k: SETS[k] for k in a.sets.split(",")}, "summary": summ,
                                            "rows": rows, "usd": round(usd_, 4)})
    spend(f"guards_attacks_{a.tag}", usd_, sum(r["model_calls"] for r in rows), sum(r["tokens_in"] for r in rows),
          sum(r["tokens_out"] for r in rows), "claude-sonnet-5-5", f"{len(rows)} attack runs")
    print(json.dumps(summ, indent=1))
    for r in sorted(rows, key=lambda r: (r["id"], r["set"])):
        print(r["id"], r["set"], r["succeeded"], r["why"][:80] if r["why"] else "", r["stopped_by"])
