"""A toolbox from any folder of tool folders (tool.json + tool.py), for your own module's tools (A4 -> A5).

    from ledgerline.course.l5.kit import FolderToolbox
    tb = FolderToolbox("my_module/tools", ERP(modules=["hr_leave"]), "ECLARKE")
    Harness(tb, LLM(cassette="A5_mine")).respond("I need Thursday and Friday off for my sister's wedding.")

It behaves like ledgerline.toolbox.Toolbox (names, schemas(), call(), erp, user), so every agent in ledgerline.course.l5
runs on it unchanged. Each tool.py has run(s, **args) and acts through the user's own Ledgerline session `s`.
"""
from __future__ import annotations

import json
import pathlib

from ...agent.tools import ToolError
from ...erp.engine import ServiceTimeout
from ...erp.receipts import install_receipts
from ...toolbox import ToolSpec


class FolderToolbox:
    def __init__(self, folder, erp, user: str = "ECLARKE", names: list[str] | None = None):
        install_receipts(erp)
        self.erp, self.user = erp, user
        self.s = erp.session(user)
        found = {p.parent.name: ToolSpec(p.parent) for p in sorted(pathlib.Path(folder).glob("*/tool.json"))}
        self.specs = {n: found[n] for n in (names or list(found)) if n in found}
        self.names = list(self.specs)

    def schemas(self) -> list[dict]:
        return [t.schema() for t in self.specs.values()]

    def manifest(self) -> list[dict]:
        return [t.card() for t in self.specs.values()]

    def call(self, name: str, args: dict | None = None) -> dict:
        if name not in self.specs:
            return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}
        t = self.specs[name]
        try:
            return t.module.run(self.s, **t.check(args or {}))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Ledgerline did not reply in time ({e}).", "next_step": "Check the status first.",
                    "ledgerline_code": "TIMEOUT"}
        except TypeError as e:
            return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}

    def call_json(self, name, args=None) -> str:
        return json.dumps(self.call(name, args), default=str)
