"""A red team from scratch, the full sweep (Lecture 7, NB7d shows a small part of it live).

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script redteam_run.py --image evals --args "--part variants"
    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script redteam_run.py --image evals --args "--part run --conds thursday:off,thursday:code"

variants   The attacker model (Claude Haiku) rewrites each seed attack (A03, A05, A06) five ways: a different wording, a
           role-play, an encoding (the model writes the instruction, our code base64-encodes it), a translation, a
           two-turn build-up. The prompt, the seeds and the strategies are ledgerline/course/l6/nb7.py ATTACKER, SEEDS,
           STRATEGIES (the notebook prints them). Writes logs/l7_redteam_variants.json. If the model declines a rewrite,
           that is recorded, not retried into compliance.
run        Every variant against Ask Northbridge (Claude Sonnet) in a fresh sandbox, for each condition prompt:guards
           (guards = off, or code = the six code guards + the numbers check). Success is decided by code (nb7.CHECKS), never
           by a model. The same 15 messages are used in every condition. Adds to logs/l7_redteam.json.
"""
import argparse
import json

from _common import LOGS, now, pmap, spend, write

from ledgerline.course.l6 import nb7
from ledgerline.course.l6.agent import PRICES
from ledgerline.llm import LLM

ap = argparse.ArgumentParser()
ap.add_argument("--part", default="variants")
ap.add_argument("--conds", default="thursday:off,thursday:code")
a = ap.parse_args()
SMALL = "anthropic:claude-haiku-5-5"


class Direct:                                  # stands in for the notebook's kit: the model account directly, no gateway
    @staticmethod
    def llm_for(m):
        return LLM(m, mode="live", max_tokens=8192)


if a.part == "variants":
    def write_one(job):
        seed_id, strategy = job
        seed = nb7.attack(seed_id)
        llm = LLM(SMALL, mode="live", max_tokens=1500)
        r = llm.chat([{"role": "user", "content": nb7.ATTACKER.format(goal=nb7.SEEDS[seed_id]["goal"], seed=seed["turns"][-1],
                                                                     strategy=nb7.STRATEGIES[strategy])}])
        turns = nb7.read_turns(r.content or "")
        if turns and strategy == "an encoding":
            plain, turns = turns, nb7.encode(turns)
        else:
            plain = None
        return {"seed": seed_id, "strategy": strategy, "turns": turns, "plain": plain, "declined": turns is None,
                "attacker_answer": (r.content or "") if turns is None else None, "tokens_in": r.tokens_in, "tokens_out": r.tokens_out}

    rows = pmap(write_one, [(s, st) for s in nb7.SEEDS for st in nb7.STRATEGIES], workers=8)
    usd = sum((r["tokens_in"] * 0.10 + r["tokens_out"] * 0.50) / 1e6 for r in rows)
    write("l7_redteam_variants.json", {"at": now(), "attacker_model": "claude-haiku-5-5", "seeds": {k: {**v, "seed_message": nb7.attack(k)["turns"][-1]}
                                                                                              for k, v in nb7.SEEDS.items()},
                                       "strategies": nb7.STRATEGIES, "variants": rows, "declined": sum(r["declined"] for r in rows),
                                       "usd": round(usd, 5)})
    spend("redteam_variants", usd, len(rows), "attacker model writing 15 variants")
    for r in rows:
        print(r["seed"], "|", r["strategy"], "|", "DECLINED: " + (r["attacker_answer"] or "")[:200] if r["declined"] else r["turns"])

else:
    variants = [v for v in json.loads((LOGS / "l7_redteam_variants.json").read_text())["variants"] if not v["declined"]]
    conds = [c.split(":") for c in a.conds.split(",")]

    def one(job):
        (prompt, gs), v = job
        att = nb7.variant(v["seed"], v["strategy"], v["turns"])
        try:
            run = nb7.run_agent(Direct, prompt, attack=att, guards=nb7.code_guards() if gs == "code" else None)
        except Exception as e:  # noqa: BLE001
            return {"prompt": prompt, "guards": gs, "seed": v["seed"], "strategy": v["strategy"], "error": f"{type(e).__name__}: {str(e)[:300]}",
                    "worked": None, "usd": 0, "model_calls": 0}
        refusals = [{k: e.get(k) for k in ("guard", "decision", "tool", "why")} for t in run["turns"] for e in t["guard_events"]
                    if e.get("decision") in ("refused", "blocked", "quarantined", "flagged")]
        return {"prompt": prompt, "guards": gs, "seed": v["seed"], "strategy": v["strategy"], "messages": v["turns"], "worked": run["worked"],
                "why": run["why"], "refusals": refusals, "turns": run["turns"], "saved": run["saved"], "usd": run["usd"],
                "model_calls": sum(t["model_calls"] for t in run["turns"]), "error": None}

    rows = pmap(one, [(c, v) for c in conds for v in variants], workers=10)
    if any("credit balance is too low" in (r.get("error") or "") for r in rows):
        print("STOP: the model account answered 'credit balance is too low'")
    p = LOGS / "l7_redteam.json"
    old = json.loads(p.read_text()) if p.exists() else {"runs": []}
    done = {(c[0], c[1]) for c in conds}
    runs = [r for r in old["runs"] if (r["prompt"], r["guards"]) not in done] + rows
    summary = {}
    for prompt, gs in sorted({(r["prompt"], r["guards"]) for r in runs}):
        rs = [r for r in runs if (r["prompt"], r["guards"]) == (prompt, gs) and r["worked"] is not None]
        summary[f"{prompt}:{gs}"] = {"attacks": len(rs), "worked": sum(r["worked"] for r in rs),
                                      "asr": round(sum(r["worked"] for r in rs) / max(1, len(rs)), 3),
                                      "worked_which": [f"{r['seed']} · {r['strategy']}" for r in rs if r["worked"]],
                                      "errors": sum(1 for r in runs if (r["prompt"], r["guards"]) == (prompt, gs) and r["worked"] is None)}
    usd = sum(r["usd"] for r in rows)
    write("l7_redteam.json", {"at": now(), "attacker_model": "claude-haiku-5-5", "agent_model": "claude-sonnet-5-5",
                              "what": "15 attacker-written variants (3 seeds x 5 strategies) against Ask Northbridge; success decided by code",
                              "summary": summary, "runs": runs, "usd": round(sum(r["usd"] for r in runs), 4)})
    spend("redteam_" + a.conds.replace(",", "+").replace(":", "-"), usd, sum(r["model_calls"] for r in rows), f"{len(rows)} red-team conversations")
    print(json.dumps(summary, indent=1))
    for r in rows:
        print(r["prompt"], r["guards"], r["seed"], "|", r["strategy"], "|", r["worked"], "|", (r.get("why") or r.get("error") or "")[:90], "|",
              [(x["guard"], x["decision"]) for x in r.get("refusals", [])], r["usd"])
