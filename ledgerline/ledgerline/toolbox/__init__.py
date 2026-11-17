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

SPECS is the default tool set: the 15 tools in ORDER, exactly as recorded runs (cassettes), the Experience app and
the Studio see them. Tools added later (EXTRAS, e.g. supplier_certificates, built in Lecture 4) live in REGISTRY,
which holds every tool folder, and are served when named:
    Toolbox(erp, "ECLARKE", names=ALL)            # all 16
    python -m ledgerline.toolbox.mcp --all         # the same over MCP

tool.json fields beyond the model-facing ones (Lecture 4, aligned with MCP):
    annotations       MCP behaviour hints: readOnlyHint, destructiveHint, idempotentHint, openWorldHint
    policy            the timeout and retry policy the code follows (reads retry, writes look themselves up)
    argument_formats  checks done at the door that the model-facing schema does not spell out (e.g. need_by: date)
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

from ..agent.tools import ToolError
from ..erp.engine import ERP, ServiceTimeout, Session, _date
from ..erp.receipts import install_receipts

DIR = pathlib.Path(__file__).parent
ORDER = ["find_item", "check_stock", "find_supplier", "check_budget", "search_policy",
         "create_purchase_request", "list_my_approvals", "approve_purchase_request",
         "create_purchase_order", "approve_purchase_order", "release_purchase_order", "order_status",
         "receive_goods", "register_supplier", "send_message"]
EXTRAS = ["supplier_certificates"]  # in SPECS, served when named (not in the default set, so recorded runs replay)
STAGE_ONLY = ["search_docs"]  # served only when named (Ask Northbridge's knowledge stage); not in ALL, so L4's runs replay
# Lecture 5 (The Habits): accounts payable and the background agents' watch lists. Served only when named, in sandboxes
# with erp.payables.install_payables(); not in SPECS or ALL, so every earlier lecture's tool set and recorded run is unchanged.
AP_ONLY = ["list_open_orders", "read_mailbox", "record_invoice", "match_invoice", "hold_invoice", "post_invoice",
           "list_invoices", "expiring_certificates", "low_stock", "draft_message"]
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
            if v is None or v == "" or (isinstance(v, str) and not v.strip()):
                continue  # empty or blank: treated as not given (so a blank required argument is refused below)
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
            fmt = self.spec.get("argument_formats", {}).get(k)
            if fmt == "positive" and v <= 0:
                raise ToolError(f"'{k}' must be more than 0, got {v}.", f"Ask the user for the {k}.")
            if fmt == "date":
                try:  # the same date forms Ledgerline accepts, rewritten as YYYY-MM-DD before anything uses them
                    v = _date(v)
                except ValueError:
                    raise ToolError(f"'{k}' must be a date written YYYY-MM-DD, got {v!r}.",
                                    f"Rewrite {k} as YYYY-MM-DD and call again.")
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


REGISTRY: dict[str, ToolSpec] = load_specs()                                # every tool folder, extras included
SPECS: dict[str, ToolSpec] = {n: s for n, s in REGISTRY.items() if n not in EXTRAS + STAGE_ONLY + AP_ONLY}  # the default set (15)
DEFAULT = [n for n in ORDER if n in SPECS]   # what Toolbox() and build_toolbox_server() serve when no names are given
ALL = [n for n in REGISTRY if n not in STAGE_ONLY + AP_ONLY]   # every tool folder but the stage-only and AP ones (16)
HABITS = ALL + AP_ONLY   # Lecture 5's Hermes lab: the 16 and the accounts-payable and watch tools (26)


def spec_of(name: str) -> ToolSpec | None:
    """A tool's spec: the default set first (a course module may add its own tool there), then the extras."""
    return SPECS.get(name) or REGISTRY.get(name)


class Toolbox:
    """The toolbox bound to one user's Ledgerline session: the user's own permissions, nobody else's."""

    def __init__(self, erp: ERP, user: str = "ECLARKE", names: list[str] | None = None):
        install_receipts(erp)
        self.erp, self.user = erp, user
        self.s = erp.session(user) if hasattr(erp, "session") else Session(erp, user)
        self.names = [n for n in (names or DEFAULT) if spec_of(n)]

    def schemas(self) -> list[dict]:
        return [spec_of(n).schema() for n in self.names]

    def manifest(self) -> list[dict]:
        return [spec_of(n).card() for n in self.names]

    def call(self, name: str, args: dict | None = None) -> dict:
        if name not in self.names:
            return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}
        t = spec_of(name)
        try:
            return t.module.run(self.s, **t.check(args or {}))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Ledgerline did not reply in time ({e}).",
                    "next_step": "Check with order_status before trying again.", "ledgerline_code": "TIMEOUT"}
        except TypeError as e:
            return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}
        except Exception as e:  # noqa: BLE001  a bug in a tool must still come back inside the error contract
            return {"ok": False, "error": f"The {name} tool failed inside ({type(e).__name__}).",
                    "next_step": "Tell the user the tool failed; do not retry a write before checking its status.",
                    "ledgerline_code": "INTERNAL"}

    def call_json(self, name: str, args: dict | None = None) -> str:
        return json.dumps(self.call(name, args), default=str)
