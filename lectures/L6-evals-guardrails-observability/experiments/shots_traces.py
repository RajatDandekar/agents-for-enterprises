"""Real screenshots of our own traces: Langfuse Cloud (public trace links, no login) and Arize Phoenix (local, the same
spans replayed into it). No model call.

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script shots_traces.py --args "--which langfuse,phoenix"

Langfuse: the public trace page of the incident run (Thursday prompt, committed without a yes), its incident span, the
timeline, a generation, and the good two-turn conversation. Phoenix: `phoenix serve` in this container, the recorded spans
of the same runs sent to it over OTLP (tracing.replay: same ids, names, attributes), then its project, trace and span views.
Screenshots: figs/langfuse/*.png and figs/phoenix/*.png (1600x900 at 2x). Page text of every shot: logs/shots_traces.json.
"""
import argparse
import json
import os
import subprocess
import time

from _common import FIGS, LOGS, write
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--which", default="langfuse,phoenix")
ap.add_argument("--incident", default="incident_r3.json")
ap.add_argument("--extra", default="")      # more trace ids for Langfuse: id=name,id=name
a = ap.parse_args()
rec = {}

inc = json.loads((LOGS / a.incident).read_text())
bad = next(r for r in inc["rows"] if r["prompt"] == "thursday" and r.get("committed"))
good = next((r for r in inc["rows"] if r["prompt"] == "good" and r.get("turn2")), None) or \
    next(r for r in json.loads((LOGS / "incident_r1.json").read_text())["rows"] if r["prompt"] == "good" and r.get("turn2"))
replay = json.loads((LOGS / "replay.json").read_text())["rows"][0] if (LOGS / "replay.json").exists() else None


def shoot(pg, path, name, full=False):
    path.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(path / f"{name}.png"), full_page=full)
    rec[name] = pg.inner_text("body")[:2500]
    print("shot", name)


def click_text(pg, text, nth=0, exact=True, wait=2500):
    loc = pg.get_by_text(text, exact=exact)
    loc.nth(nth).click(timeout=10000)
    pg.wait_for_timeout(wait)


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2, color_scheme="light")
    pg = ctx.new_page()

    if "langfuse" in a.which:
        D = FIGS / "langfuse"
        pg.goto(bad["url"], wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(9000)
        shoot(pg, D, "lf_incident_tree")
        for label, fn in (("incident span", lambda: click_text(pg, "create_purchase_request", nth=1, wait=6000)),):
            try:
                fn()
                shoot(pg, D, "lf_incident_span")
                try:
                    click_text(pg, "Raw", wait=3000)
                    shoot(pg, D, "lf_incident_span_raw")
                    click_text(pg, "Formatted", wait=2000)
                except Exception as e:  # noqa: BLE001
                    rec["raw_error"] = repr(e)[:300]
                try:
                    click_text(pg, "Metadata", wait=3000)
                    shoot(pg, D, "lf_incident_span_meta")
                except Exception as e:  # noqa: BLE001
                    rec["meta_error"] = repr(e)[:300]
            except Exception as e:  # noqa: BLE001
                rec[label + "_error"] = repr(e)[:300]
        try:
            pg.goto(bad["url"], wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(7000)
            click_text(pg, "chat claude-sonnet-5-5", nth=4, wait=6000)
            shoot(pg, D, "lf_generation")
        except Exception as e:  # noqa: BLE001
            rec["generation_error"] = repr(e)[:300]
        try:
            click_text(pg, "Timeline", wait=6000)
            shoot(pg, D, "lf_incident_timeline")
        except Exception as e:  # noqa: BLE001
            rec["timeline_error"] = repr(e)[:300]
        try:   # the scores the online evaluator wrote onto this trace
            pg.goto(bad["url"], wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(8000)
            pg.get_by_text("Scores", exact=True).first.click(timeout=8000)
            pg.wait_for_timeout(5000)
            shoot(pg, D, "lf_scores")
        except Exception as e:  # noqa: BLE001
            rec["scores_error"] = repr(e)[:300]
        if replay:
            for j, t in enumerate(replay["turns"]):
                try:
                    pg.goto(t["url"], wait_until="networkidle", timeout=90000)
                    pg.wait_for_timeout(8000)
                    shoot(pg, D, f"lf_replay_turn{j + 1}")
                    g = pg.get_by_text("guardrail confirm_yes")
                    if g.count():
                        g.first.click(timeout=8000)
                        pg.wait_for_timeout(5000)
                        shoot(pg, D, f"lf_replay_turn{j + 1}_guard")
                except Exception as e:  # noqa: BLE001
                    rec[f"replay{j}_error"] = repr(e)[:300]
        try:   # a session page, by URL (it may ask for a login: the shot shows what a visitor sees)
            sess = bad["session"]
            pg.goto(bad["url"].split("/traces/")[0] + f"/sessions/{sess}", wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(8000)
            rec["session_page"] = pg.url
            shoot(pg, D, "lf_session_page")
        except Exception as e:  # noqa: BLE001
            rec["session_page_error"] = repr(e)[:300]
        for key, url in (("lf_good_turn1", good["url"]), ("lf_good_turn2", good["turn2"]["url"])):
            try:
                pg.goto(url, wait_until="networkidle", timeout=90000)
                pg.wait_for_timeout(8000)
                shoot(pg, D, key)
            except Exception as e:  # noqa: BLE001
                rec[key + "_error"] = repr(e)[:300]
        try:   # the session link (may need a login: then the shot shows the sign-in page, and we say so)
            pg.goto(good["url"], wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(6000)
            pg.get_by_text("session", exact=True).first.click(timeout=8000)
            pg.wait_for_timeout(8000)
            rec["session_url"] = pg.url
            shoot(pg, D, "lf_session")
        except Exception as e:  # noqa: BLE001
            rec["session_error"] = repr(e)[:300]
        for pair in [x for x in a.extra.split(",") if x]:
            tid, name = pair.split("=")
            try:
                pg.goto(f"{bad['url'].rsplit('/', 1)[0]}/{tid}", wait_until="networkidle", timeout=90000)
                pg.wait_for_timeout(9000)
                shoot(pg, D, name)
            except Exception as e:  # noqa: BLE001
                rec[name + "_error"] = repr(e)[:300]

    if "phoenix" in a.which:
        D = FIGS / "phoenix"
        env = {**os.environ, "PHOENIX_WORKING_DIR": "/tmp/phx", "PHOENIX_PORT": "6006", "PHOENIX_TELEMETRY_ENABLED": "false"}
        srv = subprocess.Popen(["/opt/phx/bin/phoenix", "serve"], env=env, stdout=open("/tmp/phx.log", "w"), stderr=subprocess.STDOUT)
        import httpx
        for _ in range(90):
            try:
                if httpx.get("http://127.0.0.1:6006/healthz", timeout=2).status_code == 200:
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(2)
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        from ledgerline.course.l6.tracing import replay
        spans = json.loads((LOGS / a.incident.replace("incident_", "incident_spans_")).read_text())
        exp = OTLPSpanExporter(endpoint="http://127.0.0.1:6006/v1/traces")
        order = [r["session"] for r in inc["rows"] if r["session"] not in (bad["session"], good["session"])][:8] + \
            [good["session"], bad["session"]]
        n = 0
        for sess in order:
            n += replay(spans[sess], exp)
            time.sleep(0.3)
        rec["phoenix_spans_sent"] = n
        time.sleep(6)
        try:
            pg.goto("http://127.0.0.1:6006/projects", wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(4000)
            shoot(pg, D, "px_projects")
            click_text(pg, "ask-northbridge", wait=6000)
            shoot(pg, D, "px_traces")
            rec["px_traces_url"] = pg.url
        except Exception as e:  # noqa: BLE001
            rec["px_projects_error"] = repr(e)[:300]
        try:   # open the incident trace by its id
            base = rec.get("px_traces_url", "").split("/spans")[0]
            pg.goto(f"{base}/traces/{bad['trace_id']}", wait_until="networkidle", timeout=60000)
            pg.wait_for_timeout(6000)
            pg.mouse.move(5, 880)
            shoot(pg, D, "px_trace")
            pg.get_by_text("execute_tool create_purchase_request").nth(1).click(timeout=10000)
            pg.wait_for_timeout(4000)
            shoot(pg, D, "px_span")
            try:
                click_text(pg, "Attributes", wait=3000)
                shoot(pg, D, "px_span_attrs")
            except Exception as e:  # noqa: BLE001
                rec["px_attrs_error"] = repr(e)[:300]
        except Exception as e:  # noqa: BLE001
            rec["px_trace_error"] = repr(e)[:300]
        rec["phoenix_log_tail"] = open("/tmp/phx.log").read()[-1500:]
        srv.terminate()
    b.close()

rec["incident_trace"] = bad["trace_id"]
rec["good_traces"] = [good["trace_id"], good["turn2"]["trace_id"]]
write("shots_traces.json", rec)
print(json.dumps({k: (v[:200] if isinstance(v, str) else v) for k, v in rec.items()}, indent=1)[:5000])
