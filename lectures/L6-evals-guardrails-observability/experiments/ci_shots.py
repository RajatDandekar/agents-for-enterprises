"""Terminal screenshots of the CI gate runs, from their logs (no model call): the command, DeepEval's results table
(test cases, metrics, PASSED or FAILED), pytest's short summary and the exit code. Lines are taken from
logs/ci_<prompt>.txt as they are; only the long Python traceback in between is left out (marked "…").

    tools/mrun.sh .../l6_modal.py --script ci_shots.py
"""
import html
import re

from _common import FIGS, LOGS
from playwright.sync_api import sync_playwright

D = FIGS / "ci"
D.mkdir(parents=True, exist_ok=True)


def condense(text: str) -> list[str]:
    lines = text.splitlines()
    out = [lines[0]]
    tbl = [i for i, l in enumerate(lines) if "Test case" in l and "Metric" in l]
    if tbl:
        i = tbl[0] - 1
        out.append("…")
        for l in lines[i:]:
            if l.startswith("└") or l.startswith("╰"):
                out.append(l)
                break
            if "test_gate[" in l or "Ledgerline checks" in l or "Tool Correctness" in l or l.startswith(("┏", "┃", "┡")):
                out.append(l)
    summ = [l for l in lines if l.startswith("FAILED test_gate.py") or re.search(r"\d+ (passed|failed).* in [\d.]+s", l)]
    out.append("…")
    out += [l[:150] + ("…" if len(l) > 150 else "") for l in summ]
    out += [l for l in lines if l.startswith("[exit code")]
    return out


def png(lines, name, title):
    body = "\n".join(html.escape(l) for l in lines)
    body = re.sub(r"(PASSED|\d+ passed)", r'<span style="color:#4ec97a">\1</span>', body)
    body = re.sub(r"(FAILED|\d+ failed)", r'<span style="color:#ff6b5e">\1</span>', body)
    body = re.sub(r"(\[exit code \d+\])", r'<b style="color:#ffd166">\1</b>', body)
    page = f"""<html><body style="margin:0;background:#1d1f24"><div style="font:600 17px system-ui;color:#c9ccd3;padding:14px 22px;
    background:#2a2d34;border-bottom:1px solid #3a3d45">{html.escape(title)}</div><pre style="margin:0;padding:16px 22px;color:#e6e6e6;
    font:13.5px/1.42 'DejaVu Sans Mono',monospace;white-space:pre">{body}</pre></body></html>"""
    p = D / f"{name}.html"
    p.write_text(page)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=2).new_page()
        pg.goto("file://" + str(p))
        pg.screenshot(path=str(D / f"{name}.png"))
        b.close()
    print("shot", name, len(lines), "lines")


for prompt in ("good", "thursday"):
    t = (LOGS / f"ci_{prompt}.txt").read_text()
    code = re.findall(r"\[exit code (\d+)\]", t)
    png(condense(t), f"ci_{prompt}_term", f"CI · eval gate (pytest + DeepEval) · GATE_PROMPT={prompt} · exit {code[-1] if code else '?'}")
