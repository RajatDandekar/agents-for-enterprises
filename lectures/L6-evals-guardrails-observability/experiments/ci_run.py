"""The CI gate, run exactly as GitHub Actions would run it (same command, same requirements), on Modal's evals image.

    tools/mrun.sh .../l6_modal.py --script ci_run.py --image evals --args "--prompts good,thursday --k 2"

For each prompt: `deepeval test run test_gate.py` in ci/, with GATE_PROMPT set. The terminal output (exit code, the pytest
summary, DeepEval's results table) is kept in logs/ci_<prompt>.txt, and screenshotted as a terminal (figs/ci/ci_<prompt>.png)
so the deck shows the real output. A real GitHub Actions run needs the repository secret ANTHROPIC_API_KEY (open item).
"""
import argparse
import html
import os
import pathlib
import re
import subprocess
import time

from _common import FIGS, LOGS, now, spend, write

ap = argparse.ArgumentParser()
ap.add_argument("--prompts", default="good,thursday")
ap.add_argument("--k", default="2")
a = ap.parse_args()
CI = pathlib.Path(__file__).resolve().parent.parent / "ci"
D = FIGS / "ci"
D.mkdir(parents=True, exist_ok=True)
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
rec = {"at": now(), "runs": {}}


def term_png(text: str, name: str, title: str):
    from playwright.sync_api import sync_playwright
    lines = text.splitlines()[-70:]
    body = "\n".join(html.escape(l) for l in lines)
    body = re.sub(r"(PASSED|passed|✅[^\n]*)", r'<span style="color:#4ec97a">\1</span>', body)
    body = re.sub(r"(FAILED|failed|ERROR|❌[^\n]*)", r'<span style="color:#ff6b5e">\1</span>', body)
    page = f"""<html><body style="margin:0;background:#1d1f24"><div style="font:600 15px system-ui;color:#c9ccd3;padding:14px 22px;
    background:#2a2d34;border-bottom:1px solid #3a3d45">{html.escape(title)}</div><pre style="margin:0;padding:18px 22px;color:#e6e6e6;
    font:13px/1.45 'DejaVu Sans Mono',monospace;white-space:pre-wrap">{body}</pre></body></html>"""
    p = D / f"{name}.html"
    p.write_text(page)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2).new_page()
        pg.goto("file://" + str(p))
        pg.screenshot(path=str(D / f"{name}.png"), full_page=True)
        b.close()


for prompt in a.prompts.split(","):
    env = {**os.environ, "GATE_PROMPT": prompt, "GATE_K": a.k, "LEDGER_LLM_MODE": "live", "DEEPEVAL_TELEMETRY_OPT_OUT": "YES",
           "COLUMNS": "150", "NO_COLOR": "1", "PYTHONPATH": "/course/ledgerline"}
    t0 = time.time()
    cmd = "deepeval test run test_gate.py"
    p = subprocess.run(cmd, shell=True, cwd=CI, env=env, capture_output=True, text=True, timeout=3000)
    out = ANSI.sub("", p.stdout + "\n" + p.stderr)
    (LOGS / f"ci_{prompt}.txt").write_text(f"$ GATE_PROMPT={prompt} GATE_K={a.k} {cmd}\n" + out + f"\n[exit code {p.returncode}]\n")
    summary = re.findall(r"=+ (.*(?:passed|failed).*) =+", out)
    rec["runs"][prompt] = {"exit": p.returncode, "seconds": round(time.time() - t0, 1), "summary": summary[-1] if summary else None,
                           "failed_tests": sorted(set(re.findall(r"FAILED test_gate.py::test_gate\[([^\]]+)\]", out)))}
    try:
        term_png(f"$ GATE_PROMPT={prompt} GATE_K={a.k} {cmd}\n" + out + f"\n[exit code {p.returncode}]",
                 f"ci_{prompt}", f"CI · eval gate · prompt: {prompt} · exit {p.returncode}")
    except Exception as e:  # noqa: BLE001
        rec["runs"][prompt]["png_error"] = repr(e)[:300]
    print(prompt, rec["runs"][prompt])
# cost: the gate's agent runs, from the tokens each task printed into the log is not available; estimate from the suite
rec["note"] = "Cost per gate run is about (3 x K + 2) task runs x US$0.06-0.12 (see suite_*.json); counted as an estimate."
k = int(a.k)
spend("ci_gate", (3 * k + 2) * 0.09 * len(a.prompts.split(",")), (3 * k + 2) * 4 * len(a.prompts.split(",")), 0, 0,
      "claude-sonnet-5-5", "estimate: tasks x mean task cost from the suite")
write("ci_gate.json", rec)
