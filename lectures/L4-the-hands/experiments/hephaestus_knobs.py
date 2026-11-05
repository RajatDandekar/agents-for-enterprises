"""Lecture 4, Hephaestus: every knob, measured on the deployed app (no claims without a run).

    /Users/raj/.venv/bin/modal run deploy/hephaestus_modal.py::knobs                       # all variants, 2 repeats
    /Users/raj/.venv/bin/modal run deploy/hephaestus_modal.py::knobs --only shipped,tools_16 --repeats 3

For each variant: a fresh forge on https://rajatworkspace--northbridge-hephaestus.us-east.modal.run (a student called
"Probe <variant> r<k>"), the shipped config with ONE change, then POST /api/six (the six questions of questions.json, scored
in code by runs.py from Ledgerline's own tables) and, for the Shield, POST /api/shield/compare (each attack with its rule
off / in the prompt / in the tool, and on a host without our prompt), with the tools acting as Emma and as the service
account. Every request is an ordinary student request: same model (gemini-3.8-flash direct), same guard.
Writes lectures/L4-the-hands/experiments/logs/hephaestus_knobs.json (summary per variant + every run's rows and replies).
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor


URL = "https://rajatworkspace--northbridge-hephaestus.us-east.modal.run"
STARTER = ["find_item", "check_stock", "find_supplier", "supplier_certificates", "check_budget",
           "create_purchase_request", "approve_purchase_request"]
LEAN_TOOLS = ["check_stock", "find_item", "find_supplier", "supplier_certificates", "check_budget", "create_purchase_request"]


def each(cfg, key, val, tools=None):
    for n in tools or [n for n, t in cfg["tools"].items() if t["on"]]:
        cfg["tools"][n][key] = val


VARIANTS = {
    "shipped": ("the shipped toolbox", lambda c: None),
    "desc_vague": ("every description vague", lambda c: each(c, "description", "vague")),
    "desc_misleading": ("every description a neighbour's", lambda c: each(c, "description", "misleading")),
    "name_legacy": ("legacy names, precise descriptions", lambda c: each(c, "name", "legacy")),
    "name_legacy_desc_vague": ("legacy names and vague descriptions",
                               lambda c: (each(c, "name", "legacy"), each(c, "description", "vague"))),
    "name_legacy_desc_misleading": ("legacy names and misleading descriptions",
                                    lambda c: (each(c, "name", "legacy"), each(c, "description", "misleading"))),
    "tools_16_desc_vague": ("all 16 tools, vague descriptions",
                            lambda c: ([c["tools"][n].__setitem__("on", True) for n in c["tools"]], each(c, "description", "vague"))),
    "input_loose": ("loose input schemas", lambda c: each(c, "input", "loose")),
    "input_strict": ("strict input schemas", lambda c: each(c, "input", "strict")),
    "output_lean": ("lean outputs", lambda c: each(c, "output", "lean", LEAN_TOOLS)),
    "output_minimal": ("too-little outputs", lambda c: each(c, "output", "minimal", LEAN_TOOLS)),
    "rows_1": ("one row per list", lambda c: each(c, "rows", 1, ["find_item", "find_supplier", "supplier_certificates", "check_budget"])),
    "errors_raw": ("raw legacy error codes", lambda c: each(c, "errors", "raw")),
    "tools_2": ("2 tools (find_item, check_stock)",
                lambda c: [c["tools"][n].__setitem__("on", n in ("find_item", "check_stock")) for n in c["tools"]]),
    "tools_16": ("all 16 tools", lambda c: [c["tools"][n].__setitem__("on", True) for n in c["tools"]]),
    "identity_svc": ("tools act as the service account", lambda c: c.__setitem__("identity", "SVC_AGENT")),
    "preview_tool": ("preview rule in the tool (not the prompt)", lambda c: c["rules"].__setitem__("preview", "tool")),
    "preview_off": ("preview rule off", lambda c: c["rules"].__setitem__("preview", "off")),
    "preview_host": ("preview rule in the host (our harness)", lambda c: c["rules"].__setitem__("preview", "host")),
    "preview_off_max_qty_tool": ("preview rule off, 5,000 limit in the tool",
                                 lambda c: (c["rules"].__setitem__("preview", "off"), c["rules"].__setitem__("max_qty", "tool"))),
    "preview_off_max_qty_prompt": ("preview rule off, 5,000 limit in the prompt",
                                   lambda c: (c["rules"].__setitem__("preview", "off"), c["rules"].__setitem__("max_qty", "prompt"))),
    "max_qty_prompt": ("5,000 limit in the prompt", lambda c: c["rules"].__setitem__("max_qty", "prompt")),
    "max_qty_tool": ("5,000 limit in the tool", lambda c: c["rules"].__setitem__("max_qty", "tool")),
}


def client():
    import httpx

    return httpx.Client(base_url=URL, timeout=__import__('httpx').Timeout(300, connect=60))


def forge(c, name):
    r = c.post("/api/join", json={"name": name})
    r.raise_for_status()
    me = r.json()
    return me, {"X-Forge-Key": me["key"]}


def poll(c, h, jid, limit=1200):
    t0 = time.time()
    while time.time() - t0 < limit:
        r = c.get(f"/api/job/{jid}", headers=h)
        if r.status_code == 200 and r.json()["state"] != "running":
            return r.json()
        time.sleep(3)
    raise TimeoutError(jid)


ERR_VARIANTS = ["shipped", "errors_raw", "input_loose", "input_strict", "name_legacy_desc_vague", "desc_misleading"]


def one_run(variant: str, k: int, qset: str = "six") -> dict:
    label, f = VARIANTS[variant]
    with client() as c:
        me, h = forge(c, f"Probe {variant} {qset} r{k}")
        cfg = copy.deepcopy(me["config"])
        f(cfg)
        r = c.post("/api/config", headers=h, json={"config": cfg})
        r.raise_for_status()
        changed = r.json()["changed"]
        for attempt in range(3):
            r = c.post("/api/six", headers=h, json={"set": qset})
            if r.status_code == 200:
                break
            print(variant, k, "six refused:", r.status_code, r.text[:200], flush=True)
            time.sleep(20)
        j = poll(c, h, r.json()["id"])
        if j["state"] != "done":
            return {"variant": variant, "set": qset, "k": k, "error": j.get("error"), "changed": changed}
        res = j["result"]
        print(f"{variant:24} {qset:6} r{k}: {res['totals']['right']}/6  tokens_in {res['totals']['tokens_in']:>6}  first "
              f"{res['totals']['first_call_tokens']}  calls {res['totals']['model_calls']}  "
              + " ".join(f"q{x['n']}{'+' if x['right'] else '-'}" for x in res["rows"]), flush=True)
        return {"variant": variant, "set": qset, "label": label, "k": k, "changed": changed, "totals": res["totals"],
                "rows": [{kk: x[kk] for kk in ("id", "n", "right", "why", "tools", "tool_calls", "model_calls", "tokens_in",
                                               "tokens_out", "first_call_tokens", "seconds", "door", "rule",
                                               "ledgerline_errors", "bytes", "models", "failed")}
                         | {"replies": [t["reply"] for t in x["turns"]],
                            "calls": [[(cc["tool"], cc["args"], (cc["result"] or {}).get("ok") if isinstance(cc["result"], dict) else None,
                                        (json.dumps(cc["result"])[:300])) for cc in t["cards"]] for t in x["turns"]]}
                         for x in res["rows"]]}


def one_compare(identity: str, k: int) -> dict:
    with client() as c:
        me, h = forge(c, f"Probe shield {identity} r{k}")
        cfg = copy.deepcopy(me["config"])
        cfg["identity"] = identity
        c.post("/api/config", headers=h, json={"config": cfg}).raise_for_status()
        r = c.post("/api/shield/compare", headers=h)
        r.raise_for_status()
        j = poll(c, h, r.json()["id"])
        if j["state"] != "done":
            return {"identity": identity, "k": k, "error": j.get("error")}
        rows = [{x: a[x] for x in ("id", "title", "ask", "held", "what", "stopped_by", "placement", "identity", "host")}
                | {"reply": a["turn"]["reply"], "calls": [(cc["tool"], cc["args"]) for cc in a["turn"]["cards"]]}
                for a in j["result"]["rows"]]
        for a in rows:
            print(f"shield {identity:9} r{k} {a['id']:9} {a['placement']:6} {a['host']:7} {'HELD ' if a['held'] else 'BROKE'} "
                  f"{a['what'][:70]}", flush=True)
        return {"identity": identity, "k": k, "rows": rows}


PROD_VARIANTS = ["shipped", "desc_vague", "name_legacy_desc_misleading", "input_loose", "input_strict", "output_lean",
                 "output_minimal", "rows_1", "errors_raw", "tools_16", "tools_16_desc_vague", "identity_svc"]


def one_prod(variant: str) -> dict:
    """Every Production check (tab 6) on the variant's tools: the knobs' effect where the six questions do not reach."""
    label, f = VARIANTS[variant]
    with client() as c:
        me, h = forge(c, f"Probe prod {variant}")
        cfg = copy.deepcopy(me["config"])
        f(cfg)
        c.post("/api/config", headers=h, json={"config": cfg}).raise_for_status()
        r = c.post("/api/prod/all", headers=h)
        r.raise_for_status()
        j = poll(c, h, r.json()["id"])
        if j["state"] != "done":
            return {"variant": variant, "error": j.get("error")}
        checks = {x["id"]: {"pass": x["pass"], "headline": x["headline"]} for x in j["result"]["checks"]}
        for x in j["result"]["checks"]:
            if x["id"] == "usability":
                checks["usability"]["rows"] = [{k: g.get(k) for k in ("id", "task", "pass", "why")} for g in x["rows"]]
            if x["id"] == "reliability":
                checks["reliability"]["by_kind"] = x["rows"].get("by_kind")
                checks["reliability"]["examples"] = x["rows"].get("examples", [])[:3]
            if x["id"] == "idempotency":
                checks["idempotency"]["rows"] = x["rows"]
        print(f"prod {variant:28} " + " ".join(f"{k}:{'+' if v['pass'] else '-' if v['pass'] is False else '.'}" for k, v in checks.items()), flush=True)
        return {"variant": variant, "label": label, "checks": checks}


def summarise(runs: list[dict]) -> dict:
    out = {}
    for v, qset in [(v, q) for q in ("six", "errors") for v in VARIANTS]:
        rs = [r for r in runs if r.get("variant") == v and r.get("set", "six") == qset and "totals" in r
              and not r["totals"].get("failed")]
        if not rs:
            continue
        key = v if qset == "six" else f"{v} [errors]"
        n = len(rs)
        avg = lambda key: round(sum(r["totals"][key] or 0 for r in rs) / n, 1)  # noqa: E731
        per_q = {}
        for q in range(1, 7 if qset == "six" else 4):
            rows = [x for r in rs for x in r["rows"] if x["n"] == q]
            per_q[f"{'q' if qset == 'six' else 'e'}{q}"] = {"right": sum(x["right"] for x in rows), "of": len(rows),
                              "whys": sorted({x["why"] for x in rows if not x["right"]}),
                              "tools": [x["tools"] for x in rows], "tokens_in": round(sum(x["tokens_in"] for x in rows) / max(1, len(rows)))}
        out[key] = {"label": VARIANTS[v][0], "set": qset, "runs": n,
                  "runs_dropped_model_failed": sum(1 for r in runs if r.get("variant") == v and r.get("set", "six") == qset
                                                   and r.get("totals", {}).get("failed")), "right": [r["totals"]["right"] for r in rs],
                  "right_mean": round(sum(r["totals"]["right"] for r in rs) / n, 2),
                  "tokens_in_mean": avg("tokens_in"), "first_call_tokens_mean": avg("first_call_tokens"),
                  "tokens_per_model_call_mean": avg("tokens_per_model_call"), "model_calls_mean": avg("model_calls"),
                  "tool_calls_mean": avg("tool_calls"), "door_mean": avg("door"), "rule_mean": avg("rule"),
                  "ledgerline_errors_mean": avg("ledgerline_errors"), "bytes_mean": avg("bytes"),
                  "seconds_mean": avg("seconds"), "usd_total": round(sum(r["totals"]["usd"] for r in rs), 4),
                  "models": sorted({m for r in rs for m in r["totals"]["models"]}), "per_question": per_q}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--shield", type=int, default=2, help="repeats of the Shield comparison per identity (0 = skip)")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--errors", type=int, default=0, help="repeats of the three error questions on ERR_VARIANTS")
    ap.add_argument("--prod", default="", help="'all' or a comma list of variants for the Production checks ('' = skip)")
    ap.add_argument("--out", default=str(pathlib.Path(__file__).resolve().parent / "logs" / "hephaestus_knobs.json"))
    ap.add_argument("--merge", action="store_true", help="add to an existing log instead of replacing it")
    a = ap.parse_args()
    vs = [] if a.only == "none" else [v for v in (a.only.split(",") if a.only else VARIANTS) if v]
    jobs = [(v, k) for v in vs for k in range(1, (a.repeats + (1 if v == "shipped" else 0)) + 1)]
    t0 = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(one_run, v, k) for v, k in jobs]
        if a.errors:
            futs += [ex.submit(one_run, v, k, "errors") for v in ERR_VARIANTS for k in range(1, a.errors + 1)]
        sfuts = [ex.submit(one_compare, ident, k) for ident in ("ECLARKE", "SVC_AGENT") for k in range(1, a.shield + 1)]
        pv = PROD_VARIANTS if a.prod == "all" else [x for x in a.prod.split(",") if x]
        pfuts = [ex.submit(one_prod, v) for v in pv]
        runs = []
        for f in futs:
            try:
                runs.append(f.result())
            except Exception as e:  # noqa: BLE001
                runs.append({"error": f"{type(e).__name__}: {e}"[:300]})
        shield = []
        for f in sfuts:
            try:
                shield.append(f.result())
            except Exception as e:  # noqa: BLE001
                shield.append({"error": f"{type(e).__name__}: {e}"[:300]})
    prod = []
    for f in pfuts:
        try:
            prod.append(f.result())
        except Exception as e:  # noqa: BLE001
            prod.append({"error": f"{type(e).__name__}: {e}"[:300]})
    p = pathlib.Path(a.out)
    old = json.loads(p.read_text()) if a.merge and p.exists() else {}
    all_runs = runs
    all_shield = shield or old.get("shield", [])
    out = {"generated_by": "lectures/L4-the-hands/experiments/hephaestus_knobs.py", "app": URL,
           "at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "wall_seconds": round(time.time() - t0, 1),
           "model": "gemini:gemini-3.8-flash (direct; fallback gemini-3.5-flash-lite would show in 'models')",
           "method": "each variant = the shipped forge with one change; the six questions scored in code (runs.py)",
           "summary": summarise(all_runs), "shield_summary": shield_summary(all_shield), "runs": all_runs,
           "shield": all_shield, "production": prod or old.get("production", [])}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    print("wrote", p)
    json.dump({"summary": out["summary"], "shield_summary": out["shield_summary"]}, sys.stdout, indent=1, default=str)


def shield_summary(shield: list[dict]) -> dict:
    out = {}
    for s in shield:
        for a in s.get("rows", []):
            k = f"{a['identity']} · {a['id']} · {a['placement']} · {a['host']}"
            d = out.setdefault(k, {"held": 0, "of": 0, "what": []})
            d["held"] += bool(a["held"])
            d["of"] += a["held"] is not None
            d["what"].append(a["what"])
    return out


if __name__ == "__main__":
    main()
