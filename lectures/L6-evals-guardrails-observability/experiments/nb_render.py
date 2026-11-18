"""Render nb/<name>.html again from the saved, executed .ipynb, without running anything (no kernel, no model).

    tools/mrun.sh lectures/L6-evals-guardrails-observability/experiments/l6_modal.py --script nb_render.py --image clean --args "NB6c_multiturn_evals"

Same exporter as nb_run.py (nbconvert, the "lab" template). Used on 17 Nov after two library warning lines were removed
by hand from NB6c's saved output: the .ipynb and the rendered copy must show the same thing.
"""
import pathlib
import sys

import nbformat
from nbconvert import HTMLExporter

L6 = pathlib.Path(__file__).resolve().parent.parent
for name in sys.argv[1:]:
    nb = nbformat.read(L6 / f"{name}.ipynb", as_version=4)
    body, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    (L6 / "nb" / f"{name}.html").write_text(body)
    print(name, "rendered:", len(body), "bytes;", sum(1 for c in nb.cells if c.cell_type == "code"), "code cells")
