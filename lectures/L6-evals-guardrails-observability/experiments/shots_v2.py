"""v2 screenshots of our own demo traces, logged out: Langfuse (public trace links) and LangSmith (the public share link
readback.py made for each trace). No model call, no login, no key in this script.

    tools/mrun.sh .../l6_modal.py --script shots_v2.py [--args "--which langfuse,langsmith"]

Reads logs/traces_v2.json (trace ids, Langfuse links) and logs/readback.json (LangSmith public links).
Writes figs/langfuse/lf2_*.png, figs/langsmith/ls_*.png (1280x800 at 2.5x: larger type on a slide) and logs/shots_v2.json (the page text of every shot).
Sentry has no public view of a trace: its screens are captured by hand from a signed-in browser (see BUILD_LOG).
"""
import argparse
import json

from _common import FIGS, LOGS, write
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--which", default="langfuse,langsmith")
ap.add_argument("--only", default="")      # e.g. ls_incident_commit: retake just these shots, keep the rest of the log
a = ap.parse_args()
tv = json.loads((LOGS / "traces_v2.json").read_text())["rows"]
rb = {(t["run"], t["turn"]): t for t in json.loads((LOGS / "readback.json").read_text())["traces"]}
rec = {}
ONLY = {x for x in a.only.split(",") if x}


def shoot(pg, path, name):
    if ONLY and name not in ONLY:
        return
    path.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(path / f"{name}.png"))
    rec[name] = pg.inner_text("body")[:3000]
    print("shot", name)


def attempt(label, fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        rec[label + "_error"] = repr(e)[:300]
        print("could not:", label, repr(e)[:160])


def decline_cookies(pg):
    for t in ("Reject all", "Reject All", "Decline", "Reject", "Only necessary", "Necessary only"):
        loc = pg.get_by_role("button", name=t)
        if loc.count():
            try:
                loc.first.click(timeout=3000)
                pg.wait_for_timeout(800)
                rec["cookies"] = f"declined ({t})"
                return
            except Exception:  # noqa: BLE001
                pass


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2.5, color_scheme="light")
    pg = ctx.new_page()

    if "langfuse" in a.which:
        D = FIGS / "langfuse"

        def lf(run, turn):
            return tv[run]["turns"][turn - 1]["links"]["langfuse"]

        def open_(url, wait=9000):
            pg.goto(url, wait_until="networkidle", timeout=90000)
            try:                                     # the page sometimes sits on "Loading ..." for a while
                pg.get_by_text("invoke_agent Ask Northbridge").first.wait_for(timeout=45000)
            except Exception:  # noqa: BLE001
                pg.reload(wait_until="networkidle", timeout=90000)
                pg.get_by_text("invoke_agent Ask Northbridge").first.wait_for(timeout=45000)
            pg.wait_for_timeout(wait)
        for name, (run, turn) in (("lf2_ordinary", ("ordinary", 1)), ("lf2_good_turn1", ("good2", 1)), ("lf2_good_turn2", ("good2", 2)),
                                  ("lf2_incident_tree", ("incident", 1))):
            attempt(name, lambda: (open_(lf(run, turn)), shoot(pg, D, name)))

        def span():
            pg.get_by_text("create_purchase_request", exact=False).nth(1).click(timeout=10000)
            pg.wait_for_timeout(6000)
            shoot(pg, D, "lf2_incident_span")
        attempt("lf2_incident_span", span)

        def gen():
            open_(lf("incident", 1), 7000)
            pg.get_by_text("chat claude-sonnet-5-5", exact=True).nth(0).click(timeout=10000)
            pg.wait_for_timeout(6000)
            shoot(pg, D, "lf2_generation")
        attempt("lf2_generation", gen)

        def timeline():
            pg.get_by_text("Timeline", exact=True).first.click(timeout=10000)
            pg.wait_for_timeout(6000)
            shoot(pg, D, "lf2_incident_timeline")
        attempt("lf2_incident_timeline", timeline)

        def scores():                                # the score scores_v2.py wrote onto the incident trace
            open_(lf("incident", 1), 8000)
            pg.get_by_text("Scores", exact=True).first.click(timeout=10000)
            pg.wait_for_timeout(5000)
            shoot(pg, D, "lf2_incident_scores")
        attempt("lf2_incident_scores", scores)

    if "langsmith" in a.which:
        D = FIGS / "langsmith"

        def ls(run, turn):
            return rb[(run, turn)]["langsmith"]["public_url"]

        def open_(url, wait=12000):
            pg.goto(url, wait_until="domcontentloaded", timeout=90000)
            pg.wait_for_timeout(wait)
            decline_cookies(pg)
        for name, (run, turn) in (("ls_ordinary", ("ordinary", 1)), ("ls_good_turn1", ("good2", 1)), ("ls_good_turn2", ("good2", 2)),
                                  ("ls_incident", ("incident", 1))):
            attempt(name, lambda: (open_(ls(run, turn)), shoot(pg, D, name)))
        rec["ls_incident_url_after_load"] = pg.url.split("?")[0]

        def commit():
            pg.get_by_text("create_purchase_request", exact=True).last.click(timeout=10000)
            pg.mouse.move(1200, 780)                 # off the row, so no hover card covers the panel
            # 17 Nov: the panel draws grey placeholders for about ten seconds before the arguments arrive; the first
            # capture caught the placeholders. Wait for a field of the call itself.
            pg.get_by_text("cost_centre", exact=True).first.wait_for(timeout=45000)
            pg.wait_for_timeout(2500)
            shoot(pg, D, "ls_incident_commit")
        attempt("ls_incident_commit", commit)

        def llm():
            pg.get_by_text("chat claude-sonnet-5-5", exact=True).first.click(timeout=10000)
            pg.mouse.move(1200, 780)
            pg.get_by_text("You are Ask Northbridge", exact=False).first.wait_for(timeout=45000)
            pg.wait_for_timeout(2500)
            shoot(pg, D, "ls_incident_llm")
        attempt("ls_incident_llm", llm)

        def llm_cost():                              # the hover card on a model call: tokens and cost, input and output
            pg.get_by_text("chat claude-sonnet-5-5", exact=True).first.hover(timeout=10000)
            pg.wait_for_timeout(2500)
            shoot(pg, D, "ls_incident_llm_cost")
        attempt("ls_incident_llm_cost", llm_cost)
        def feedback():                              # the same check, written as feedback on the run
            pg.get_by_text("invoke_agent Ask Northbridge", exact=True).last.click(timeout=10000)   # back to the root run
            pg.wait_for_timeout(3000)
            pg.get_by_text("Feedback", exact=True).first.click(timeout=8000)
            pg.mouse.move(1200, 780)
            pg.wait_for_timeout(4000)
            shoot(pg, D, "ls_incident_feedback")
        attempt("ls_incident_feedback", feedback)

    b.close()

if ONLY:                                             # a retake: keep what the full run recorded
    old = json.loads((LOGS / "shots_v2.json").read_text())
    old.update(rec)
    rec = old
write("shots_v2.json", rec)
print(json.dumps({k: (v[:260] if isinstance(v, str) else v) for k, v in rec.items()}, indent=1, ensure_ascii=False)[:9000])
