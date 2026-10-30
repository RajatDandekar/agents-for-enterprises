"""The course toolbox: one tool per business activity, each in its own folder.

    toolbox/create_purchase_order/
        tool.json   what the model reads: name, description, input_schema, output_schema, writes, category
        tool.py     what runs: def run(s, **args) -> dict, acting through the signed-in user's Ledgerline session `s`

The same folders feed every surface in the course: the chatbot (Toolbox.schemas() goes to the LLM),
the MCP server (ledgerline.toolbox.mcp), the workflow studio (each tool is a node) and the tools page.

    from ledgerline.erp.engine import ERP
    from ledgerline.toolbox import Toolbox
    tb = Toolbox(ERP(), "ECLARKE")                   # Emma's permissions, nobody else's
    tb.call("check_stock", {"item_code": "BAT-500"})

Every tool returns a dict with ok=True, or ok=False with `error` and `next_step` (what to do about it).
Writes preview first (confirm=false) and commit only on confirm=true, carry an idempotency key, and return a
receipt read back from Ledgerline.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

from ..agent.tools import ToolError
from ..erp.engine import ERP, ServiceTimeout, Session
from ..erp.receipts import install_receipts

DIR = pathlib.Path(__file__).parent
ORDER = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy",
         "create_purchase_request", "list_my_approvals", "approve_purchase_request",
         "create_purchase_order", "approve_purchase_order", "release_purchase_order", "order_status",
         "receive_goods", "register_supplier", "send_message"]
TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}


class ToolSpec:
    def __init__(self, folder: pathlib.Path):
        self.folder = folder
        self.spec = json.loads((folder / "tool.json").read_text())
        self.name = self.spec["name"]
        self.source = (folder / "tool.py").read_text()
        mod_spec = importlib.util.spec_from_file_location(f"ledgerline.toolbox.{self.name}.tool", folder / "tool.py")
        self.module = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(self.module)

    @property
    def writes(self) -> bool:
        return bool(self.spec.get("writes"))

    def schema(self) -> dict:
        """The OpenAI-style function schema the LLM sees."""
        return {"type": "function", "function": {"name": self.name, "description": self.spec["description"],
                                                 "parameters": self.spec["input_schema"]}}

    def check(self, args: dict) -> dict:
        """Check the arguments once, at the door, against tool.json. Returns clean arguments or raises ToolError."""
        props = self.spec["input_schema"].get("properties", {})
        clean = {}
        for k, v in (args or {}).items():
            if k not in props:
                raise ToolError(f"{self.name} has no argument '{k}'.", f"Use only: {', '.join(props)}.")
            if v is None or v == "":
                continue
            want = props[k].get("type")
            if want == "integer" and isinstance(v, str) and v.strip().lstrip("-").isdigit():
                v = int(v)
            if want == "integer" and isinstance(v, float) and v.is_integer():
                v = int(v)
            if want == "boolean" and isinstance(v, str):
                v = v.strip().lower() in ("true", "yes", "1")
            if want and not isinstance(v, TYPES[want]) or (want in ("integer", "number") and isinstance(v, bool)):
                raise ToolError(f"'{k}' should be {want}, got {type(v).__name__}.", f"Pass {k} as {want}.")
            if "enum" in props[k] and v not in props[k]["enum"]:
                raise ToolError(f"'{k}' must be one of {props[k]['enum']}.", "Pick one of the allowed values.")
            clean[k] = v
        missing = [r for r in self.spec["input_schema"].get("required", []) if r not in clean]
        if missing:
            raise ToolError(f"Missing {', '.join(missing)}.", f"Ask the user for {', '.join(missing)}.")
        return clean

    def card(self) -> dict:
        """Everything a page needs to show this tool: the JSON, the Python, and the Ledgerline services behind it."""
        return {**self.spec, "python": self.source}


def load_specs() -> dict[str, ToolSpec]:
    found = {p.parent.name: ToolSpec(p.parent) for p in DIR.glob("*/tool.json")}
    return {n: found[n] for n in ORDER if n in found} | {n: s for n, s in found.items() if n not in ORDER}


SPECS: dict[str, ToolSpec] = load_specs()


class Toolbox:
    """The toolbox bound to one user's Ledgerline session: the user's own permissions, nobody else's."""

    def __init__(self, erp: ERP, user: str = "ECLARKE", names: list[str] | None = None):
        install_receipts(erp)
        self.erp, self.user = erp, user
        self.s = erp.session(user) if hasattr(erp, "session") else Session(erp, user)
        self.names = [n for n in (names or list(SPECS)) if n in SPECS]

    def schemas(self) -> list[dict]:
        return [SPECS[n].schema() for n in self.names]

    def manifest(self) -> list[dict]:
        return [SPECS[n].card() for n in self.names]

    def call(self, name: str, args: dict | None = None) -> dict:
        if name not in self.names:
            return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}
        t = SPECS[name]
        try:
            return t.module.run(self.s, **t.check(args or {}))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Ledgerline did not reply in time ({e}).",
                    "next_step": "Check with order_status before trying again.", "ledgerline_code": "TIMEOUT"}
        except TypeError as e:
            return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}

    def call_json(self, name: str, args: dict | None = None) -> str:
        return json.dumps(self.call(name, args), default=str)
