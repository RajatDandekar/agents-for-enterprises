"""Execute one Lecture 7 notebook top to bottom, as a student would, and keep its outputs.

    --mode replay   no key of any kind, no gateway: every model-backed cell shows our recorded run (Colab with no key)
    --mode live     joins Argus as a test student ("Test NB7x…") and runs every model call through Argus's gateway with that
                    join key (no Anthropic key in the container); NB_RECORD=1 saves each result as the recorded one
                    (experiments/logs/nb7*_*.json)

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script nb_run.py --image clean --args "--nb NB7a_guards --mode live"

The live run's outputs are kept in the .ipynb and rendered to nb/<name>.html (the copy the deck embeds, nbconvert's "lab"
template, as in Lecture 6); --save keeps a replay run's outputs the same way. Same method as Lecture 6's nb_run.py; the only
differences are the folder and where the spend record goes.
"""
import argparse
import os
import pathlib
import sys
import time

import httpx
import nbformat
from nbclient import NotebookClient

ARGUS = "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ap = argparse.ArgumentParser()
ap.add_argument("--nb", required=True)
ap.add_argument("--mode", default="replay")
ap.add_argument("--save", action="store_true")     # keep a replay run's outputs too (the .ipynb and nb/<name>.html)
a = ap.parse_args()
L7 = pathlib.Path(__file__).resolve().parent.parent
os.environ.pop("ANTHROPIC_API_KEY", None)            # neither mode may use a real model key
os.environ.pop("ANTHROPIC_BASE_URL", None)
key = None
if a.mode == "live":
    me = httpx.post(ARGUS + "/api/join", json={"name": "Test " + a.nb[:6]}, timeout=120).json()
    key = me["key"]
    os.environ.update(ARGUS_URL=ARGUS, ARGUS_KEY=key, NB_RECORD="1")
else:
    for k in list(os.environ):
        if k.startswith(("LANGFUSE_", "LANGSMITH_", "SENTRY_", "ARGUS_", "NB_RECORD")):
            os.environ.pop(k)
nb_path = L7 / f"{a.nb}.ipynb"
nb = nbformat.read(nb_path, as_version=4)
client = NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(L7)}})
err = None
t0 = time.time()
try:
    client.execute()
except Exception as e:  # noqa: BLE001
    err = str(e)[-4000:]
minutes = round((time.time() - t0) / 60, 1)
errs = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
ncode = sum(1 for c in nb.cells if c.cell_type == "code")
ran = sum(1 for c in nb.cells if c.cell_type == "code" and c.get("execution_count"))
text = "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "stream")
if key and key in nbformat.writes(nb):
    raise SystemExit("the join key leaked into an output: not saved")
out = L7 / "nb"
out.mkdir(exist_ok=True)
if (a.mode == "live" or a.save) and not err:
    nbformat.write(nb, nb_path)
    from nbconvert import HTMLExporter
    body, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    (out / f"{a.nb}.html").write_text(body)
usd, calls = 0.0, 0
if key:
    m = httpx.get(ARGUS + "/api/me", headers={"x-argus-key": key}, timeout=60).json()
    usd, calls = float(m.get("spend_usd") or 0), int((m.get("stats") or {}).get("gateway_calls") or 0)
head = (f"mode {a.mode} · cells {len(nb.cells)} · code cells {ncode} · ran {ran} · errors {len(errs)} · {minutes} minutes"
        + (f" · US${usd:.4f} through the Argus gateway ({calls} model calls)" if key else " · no model call"))
(out / f"{a.nb}.{a.mode}.txt").write_text(f"{head}\n{err or 'OK'}\n\n{text[-90000:]}")
print(f"{a.nb} [{a.mode}] {head}")
print(err or "OK")
print(text[-9000:])
if key:
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _common import spend
    spend(f"nb_{a.nb[:4]}_live", usd, calls, note=f"{a.nb} top to bottom, live through the Argus gateway (test student 'Test {a.nb[:6]}'); charged to Argus's budget")
if err:
    sys.exit(1)
