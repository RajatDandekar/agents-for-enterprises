"""Build a Colab notebook from a percent-format Python source (the way the course notebooks are written).

    python3 tools/nbbuild.py lectures/L1-the-form/NB1_the_form.py      -> writes NB1_the_form.ipynb beside it

Source format:   # %% [markdown]   then lines starting with "# " (the markdown);   # %%   starts a code cell.
The standard setup cell (tools/nb_setup.txt) replaces a cell containing only:   # %% setup
Pure standard library, so it is safe to run on the laptop.
"""
import json
import pathlib
import sys

SETUP = (pathlib.Path(__file__).parent / "nb_setup.txt").read_text()


def build(src: pathlib.Path) -> pathlib.Path:
    cells, kind, buf = [], None, []

    def flush():
        if kind is None:
            return
        text = "\n".join(buf).strip("\n")
        if kind == "markdown":
            text = "\n".join(l[2:] if l.startswith("# ") else ("" if l.strip() == "#" else l) for l in text.split("\n"))
            cells.append({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)})
        elif text or kind == "setup":
            if kind == "setup":
                text = SETUP.strip("\n")
            cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                          "source": text.splitlines(True)})

    for line in src.read_text().split("\n"):
        if line.startswith("# %% [markdown]"):
            flush(); kind, buf = "markdown", []
        elif line.strip() == "# %% setup":
            flush(); kind, buf = "setup", []
        elif line.startswith("# %%"):
            flush(); kind, buf = "code", []
        else:
            buf.append(line)
    flush()
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                       "language_info": {"name": "python"}, "colab": {"provenance": []}},
          "nbformat": 4, "nbformat_minor": 5}
    out = src.with_suffix(".ipynb")
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(build(pathlib.Path(a)))
