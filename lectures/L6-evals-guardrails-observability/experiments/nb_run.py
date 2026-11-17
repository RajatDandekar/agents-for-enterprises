"""Execute one Lecture 6 notebook top to bottom, as a student would, and keep its outputs.

    --mode replay   no key of any kind, no gateway: every cell shows our recorded run (what Colab does with no key)
    --mode live     joins Argus as a test student and runs every model call through Argus's gateway with that join key
                    (no Anthropic key in the container); NB_RECORD=1 saves each result as the recorded one (logs/nb6*_*.json)

    tools/mrun.sh .../l6_modal.py --script nb_run.py --image clean --args "--nb NB6a_tracing --mode live"

The live run's outputs are kept in the .ipynb and rendered to nb/<name>.html (the copy the deck embeds); --save keeps a
replay run's outputs the same way (its first output line says REPLAY).
"""
import argparse
import os
import pathlib
import sys

import httpx
import nbformat
from nbclient import NotebookClient

ARGUS = "https://rajatworkspace--northbridge-argus.us-east.modal.run"
ap = argparse.ArgumentParser()
ap.add_argument("--nb", required=True)
ap.add_argument("--mode", default="replay")
ap.add_argument("--save", action="store_true")     # keep a replay run's outputs too (the .ipynb and nb/<name>.html)
a = ap.parse_args()
L6 = pathlib.Path(__file__).resolve().parent.parent
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
nb_path = L6 / f"{a.nb}.ipynb"
nb = nbformat.read(nb_path, as_version=4)
client = NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(L6)}})
err = None
try:
    client.execute()
except Exception as e:  # noqa: BLE001
    err = str(e)[-4000:]
errs = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
ncode = sum(1 for c in nb.cells if c.cell_type == "code")
ran = sum(1 for c in nb.cells if c.cell_type == "code" and c.get("execution_count"))
text = "\n".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "stream")
if key and key in nbformat.writes(nb):
    raise SystemExit("the join key leaked into an output: not saved")
out = L6 / "nb"
out.mkdir(exist_ok=True)
if (a.mode == "live" or a.save) and not err:
    nbformat.write(nb, nb_path)
    from nbconvert import HTMLExporter
    body, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    (out / f"{a.nb}.html").write_text(body)
(out / f"{a.nb}.{a.mode}.txt").write_text(f"mode {a.mode} · code cells {ncode} · ran {ran} · errors {len(errs)}\n{err or 'OK'}\n\n{text[-60000:]}")
print(f"{a.nb} [{a.mode}] code cells: {ncode} ran: {ran} errors: {len(errs)}")
print(err or "OK")
print(text[-6000:])
if key:
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from _common import spend
    m = httpx.get(ARGUS + "/api/me", headers={"x-argus-key": key}, timeout=60).json()
    spend(f"v2_nb_{a.nb[:4]}_live", float(m.get("spend_usd") or 0), int((m.get("stats") or {}).get("gateway_calls") or 0),
          note=f"{a.nb} top to bottom, live through the Argus gateway (test student); charged to Argus's budget")
if err:
    sys.exit(1)
