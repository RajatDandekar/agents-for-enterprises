"""Pick three representative traces from the runs, make them public in Langfuse, read them back through the current
API, and screenshot Langfuse's trace view at 1920x1080 with headless Chromium (no login: the traces are public).

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py \
        --script lectures/L1-before-and-after/experiments/production/publish_and_shoot.py

No model is called. Writes logs/langfuse_public.json and shots/*.png. All data in these traces is fictional.
"""
import json
import pathlib
import time

from ledgerline.course.l1.production import langfuse_api as LF
from ledgerline.course.l1.production import tracing as T

HERE = pathlib.Path(__file__).parent
LOGS, SHOTS = HERE / "logs", HERE / "shots"
SHOTS.mkdir(exist_ok=True)


def rows(pattern):
    out = []
    for f in sorted(LOGS.glob(pattern)):
        out += json.loads(f.read_text())["rows"]
    return out


stacks, abl = rows("stacks_r*.json"), rows("ablation_*.json")
success = next(r for r in stacks if r["stack"] == "ours" and r["mission"] == "M4" and r["passed"] and r["run"] == 1)
sdk = next((r for r in stacks if r["stack"] == "openai_agents" and r["mission"] == "M4" and r["passed"]), None)
bad = [r for r in abl + stacks if r["never_events"]]
failure = bad[0] if bad else next((r for r in abl + stacks if not r["passed"] and not r["error"]), None)
picks = [("success", success), ("failure", failure), ("agents_sdk", sdk)]
picks = [(k, r) for k, r in picks if r]

tp, _ = T.provider(langfuse=True)
tracer = tp.get_tracer("ask-northbridge", "l1-production")
for _, r in picks:
    LF.make_public(tracer, r["trace_id"], r["root_span_id"], at_ns=r.get("root_end_ns"))
tp.force_flush()
time.sleep(40)

out = {"picked": {}, "shots": []}
for k, r in picks:
    code, obs = LF.observations(r["trace_id"])
    data = obs.get("data", []) if isinstance(obs, dict) else []
    out["picked"][k] = {"trace_id": r["trace_id"], "url": LF.trace_url(r["trace_id"]), "stack": r["stack"],
                        "model": r["model"], "run": r["run"], "mission": r["mission"], "passed": r["passed"],
                        "never_events": r["never_events"], "checks": r["checks"],
                        "langfuse_read_status": code, "observations": len(data),
                        "observation_types": sorted({o.get("type") for o in data if o.get("type")}),
                        "langfuse_cost_usd": round(sum(float(o.get("totalCost") or o.get("calculatedTotalCost") or 0)
                                                       for o in data), 6)}

from playwright.sync_api import sync_playwright  # noqa: E402


def failing_span(r):
    for name in ("create_purchase_order", "receive_goods", "release_purchase_order", "create_purchase_request"):
        if any(c["name"] == name for c in r["tool_calls"]):
            return name
    bad_calls = [c["name"] for c in r["tool_calls"] if not c["ok"]]
    return bad_calls[0] if bad_calls else None


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1920, "height": 1080}, color_scheme="light")
    pg = ctx.new_page()
    for k, r in picks:
        url = out["picked"][k]["url"]
        for _ in range(6):
            pg.goto(url, wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(9000)
            if "do not have access" not in pg.inner_text("body"):
                break
            time.sleep(30)

        def shot(name, what):
            f = SHOTS / f"lf_{k}_{name}.png"
            pg.screenshot(path=str(f))
            out["shots"].append({"file": f"shots/{f.name}", "trace": k, "view": name, "url": url, "what": what,
                                 "text": pg.inner_text("body")[:1500]})

        shot("tree", "the trace: tree of spans, latency, cost, tokens, the erp_check and never_events scores, tags")
        try:
            pg.get_by_text("Timeline", exact=True).first.click(timeout=8000)
            pg.wait_for_timeout(6000)
            shot("timeline", "the same trace as a timeline: where the seconds went")
            pg.get_by_text("Tree", exact=True).first.click(timeout=8000)
            pg.wait_for_timeout(4000)
        except Exception as e:  # noqa: BLE001
            out["shots"].append({"trace": k, "view": "timeline", "error": repr(e)[:200]})
        target = failing_span(r) if k == "failure" else "release_purchase_order"
        if k == "failure" and not target:   # no tool reached the server: show the turn where it claimed success
            import re
            i = next((n for n, t in enumerate(r["turns"]) if "released" in t["reply"].lower()), None)
            if i is None:   # else the first reply that writes a tool call as text instead of calling it
                i = next((n for n, t in enumerate(r["turns"]) if re.search(r"\b[a-z_]+\(\w+=", t["reply"])), 0)
            try:
                pg.get_by_text("invoke_agent Ask Northbridge", exact=True).nth(i).click(timeout=8000)
                pg.wait_for_timeout(6000)
                shot(f"turn{i + 1}", f"turn {i + 1}: what the agent said: {r['turns'][i]['reply'][:90]}")
            except Exception as e:  # noqa: BLE001
                out["shots"].append({"trace": k, "view": f"turn{i + 1}", "error": repr(e)[:200]})
        if target:
            try:
                pg.get_by_text(target, exact=True).last.click(timeout=8000)
                pg.wait_for_timeout(6000)
                shot(f"span_{target}", f"the {target} tool span: arguments in, receipt out")
            except Exception as e:  # noqa: BLE001
                out["shots"].append({"trace": k, "view": target, "error": repr(e)[:200]})
        if k == "success":
            try:
                pg.get_by_text(f"chat {r['model'].split('/')[-1]}", exact=True).first.click(timeout=8000)
                pg.wait_for_timeout(6000)
                shot("generation", "one model call: the messages in, the tool calls out, tokens and cost")
            except Exception as e:  # noqa: BLE001
                out["shots"].append({"trace": k, "view": "generation", "error": repr(e)[:200]})
    b.close()
(LOGS / "langfuse_public.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps({k: {x: v[x] for x in ("url", "stack", "model", "mission", "passed", "never_events", "observations",
                                        "langfuse_cost_usd")} for k, v in out["picked"].items()}, indent=1))
print([s.get("file") or s for s in out["shots"]])
