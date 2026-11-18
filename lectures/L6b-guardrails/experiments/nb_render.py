"""Render nb/<name>.html again from the saved, executed .ipynb, without running anything (no kernel, no model).

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script nb_render.py --image clean --args "NB7d_red_team"

Same exporter as nb_run.py (nbconvert, the "lab" template). Used when a sentence in a saved notebook is corrected by hand
(see logs/README.md): the .py source, the .ipynb and the rendered copy must say the same thing.
"""
import pathlib
import sys

import nbformat
from nbconvert import HTMLExporter

L7 = pathlib.Path(__file__).resolve().parent.parent
for name in sys.argv[1:]:
    nb = nbformat.read(L7 / f"{name}.ipynb", as_version=4)
    body, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    (L7 / "nb" / f"{name}.html").write_text(body)
    outs = sum(len(c.get("outputs", [])) for c in nb.cells if c.cell_type == "code")
    print(name, "rendered:", len(body), "bytes;", sum(1 for c in nb.cells if c.cell_type == "code"), "code cells with", outs, "outputs")
