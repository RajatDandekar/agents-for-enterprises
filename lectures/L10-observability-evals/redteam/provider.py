"""promptfoo provider: one attack against Ask Rasoi, in a fresh Bahi. promptfoo calls call_api() once per test case.

The output is JSON: the last replies, and what broke in Bahi (read by code from Bahi's tables, see
bahi.course.obs.redteam.broken). assert_rules.py passes the test only when nothing broke.
"""
import json

from bahi.course.obs.redteam import CASES, run_attack

BY_ID = {c["id"]: c for c in CASES}


def call_api(prompt, options, context):
    cfg = (options or {}).get("config", {})
    v = (context or {}).get("vars", {})
    meta = ((context or {}).get("test") or {}).get("metadata") or {}
    base = BY_ID.get(v.get("id")) or {"id": "generated." + str(meta.get("pluginId", "case")), "goal": "generated",
                                       "strategy": str(meta.get("strategyId") or "basic"), "setup": ""}
    case = dict(base, attack=prompt)  # the prompt promptfoo rendered is the attack text
    tag = ("trust" if cfg.get("trust") else "bare") + "_" + cfg.get("tier", "flash")
    try:
        r = run_attack(case, trust=bool(cfg.get("trust")), model=cfg.get("model", "gemini:gemini-3.8-flash"),
                       cassette=f"IND10_redteam_{tag}")
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"}
    return {"output": json.dumps(r, ensure_ascii=False, default=str),
            "tokenUsage": {"prompt": r["tokens_in"], "completion": r["tokens_out"], "total": r["tokens_in"] + r["tokens_out"]},
            "cost": round(r["cost_inr"] / 88.0, 6)}
