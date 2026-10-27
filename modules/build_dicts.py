"""Write each module's one-page data dictionary from its own code, so it can never drift from the services.

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/build_dicts.py

Writes bahi/bahi/modules/<name>/data-dictionary.md from SERVICES (fields), SCHEMA (tables) and the package's
GLOSSARY, STATUS and ERRORS dicts.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bahi"))

from bahi.erp.engine import ERP, SERVICES  # noqa: E402
from bahi.modules._kit import KITS, load  # noqa: E402


def build(name: str) -> str:
    pkg, _, _ = load(name)
    erp = ERP(modules=[name])
    k = pkg.KIT
    out = [f"# {k['title']}: data dictionary", "",
           f"Prefix `{k['prefix']}` for services, `sp_{k['prefix']}` for stored procedures, `{k['prefix']}` for tables. "
           "Every reply comes in the legacy envelope `{rc, err_cd, msg, data}`; rc is S, W or E.", "",
           "## Services", "", "| Service | Legacy name | Kind | Screen | Fields (* = mandatory) |", "|---|---|---|---|---|"]
    for n, s in SERVICES.items():
        if s.fn.__module__.startswith(f"bahi.modules.{name}."):
            f = ", ".join(f"{x.name}{'*' if x.required else ''}:{x.type}" for x in s.fields) or "none"
            out.append(f"| `{n}` | {s.doc} | {s.kind} | {s.screen or ''} | {f} |")
    out += ["", "## Tables", ""]
    for t in re.findall(r"CREATE TABLE (\w+)", pkg.SCHEMA):
        cols = [r["name"] for r in erp.q(f"PRAGMA table_info({t})")]
        n = erp.q1(f"SELECT count(*) n FROM {t}")["n"]
        out.append(f"- **{t}** ({n} seed rows): {', '.join(cols)}")
    out += ["", "## Field meanings", "", "| Field | Meaning |", "|---|---|"]
    out += [f"| `{a}` | {b} |" for a, b in getattr(pkg, "GLOSSARY", {}).items()]
    out += ["", "## Status codes", "", " · ".join(f"**{a}** {b}" for a, b in getattr(pkg, "STATUS", {}).items()),
            "", "## Error and warning codes", "", "| Code | Meaning |", "|---|---|"]
    out += [f"| {a} | {b} |" for a, b in getattr(pkg, "ERRORS", {}).items()]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    only = sys.argv[1:] or KITS
    for name in only:
        if not os.path.exists(os.path.join(HERE, "..", "bahi", "bahi", "modules", name, "__init__.py")):
            print("skip (not built)", name)
            continue
        path = os.path.join(HERE, "..", "bahi", "bahi", "modules", name, "data-dictionary.md")
        open(path, "w").write(build(name))
        print("wrote", os.path.relpath(path, os.path.join(HERE, "..")))
