"""Shared by the run scripts: run suites in parallel, keep each trace's waterfall, write one log file per job."""
import json
import pathlib
import time
import urllib.request
import os
from concurrent.futures import ThreadPoolExecutor

from ledgerline.course.l1.production import tracing as T
from ledgerline.course.l1.production.runner import Rig

HERE = pathlib.Path(__file__).parent
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)


def key_usage() -> dict | None:
    """The OpenRouter key's spend so far (US dollars). The key is shared, so before/after is an upper bound."""
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                     headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]
        return {"usage": d.get("usage"), "limit_remaining": d.get("limit_remaining")}
    except Exception as e:  # noqa: BLE001
        return {"error": repr(e)[:200]}


def policy_docs() -> dict:
    """Which version of the documents search_policy reads: one hash over docs/*.md and wiki/pages/*.md."""
    import hashlib
    import ledgerline
    root = pathlib.Path(ledgerline.__file__).parent
    files = sorted(list((root / "docs").glob("*.md")) + list((root / "wiki" / "pages").glob("*.md")))
    h = hashlib.sha256(b"".join(f.name.encode() + f.read_bytes() for f in files)).hexdigest()[:16]
    return {"sha256_16": h, "files": len(files),
            "uk_vat_wording": any("reverse charge" in f.read_text().lower() for f in files),
            "gst_wording": any("gst" in f.read_text().lower() for f in files)}


def run_jobs(jobs: list[tuple], name: str, budget_usd: float, args: dict) -> dict:
    """jobs: [(stack, model, run)]. Every mission of every job runs at once (each has its own Ledgerline)."""
    before = key_usage()
    rig = Rig(langfuse=True, budget_usd=budget_usd)
    t0 = time.time()
    from ledgerline.course.l1.production.missions import MISSIONS
    with ThreadPoolExecutor(min(40, 5 * len(jobs))) as ex:
        futs = [ex.submit(rig.run_mission, s, m, mi, r) for (s, m, r) in jobs for mi in MISSIONS]
        rows = [f.result() for f in futs]
    rig.tp.force_flush()
    for r in rows:   # the waterfall of every trace, from the spans as exported
        r["waterfall"] = T.waterfall(rig.spans.of_trace(r["trace_id"]))
    rig.close()
    time.sleep(5)
    out = {"job": name, "args": args, "started": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(t0)),
           "seconds": round(time.time() - t0, 1), "gateway_spent_usd": round(rig.gw.spent_usd, 6),
           "openrouter_key_before": before, "policy_docs": policy_docs(), "openrouter_key_after": key_usage(), "budget_usd": budget_usd,
           "rows": rows}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=1, default=str))
    for r in rows:
        print(f"{r['stack']:14s} {r['model']:34s} r{r['run']} {r['mission']} {'PASS' if r['passed'] else 'fail'} "
              f"NE={r['never_events']} calls={r['model_calls']} tok={r['tokens']} ${r['cost_usd']:.4f} {r['wall_s']}s "
              f"err={r['error']} failed={[k for k, v in r['checks'].items() if not v]}")
    print("spent (gateway, live calls): $%.4f" % rig.gw.spent_usd, "| key before/after:", before, out["openrouter_key_after"])
    return out
