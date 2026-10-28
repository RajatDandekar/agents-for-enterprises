"""A module's own toolbox: the same folder format as the purchasing toolbox (bahi/toolbox), for a capstone kit.

    bahi/modules/hr_leave/toolbox/check_leave_balance/
        tool.json     name, title, category, description, input_schema, output_schema, writes, services, example
        tool.py       def run(s, **args) -> dict, acting through the signed-in user's Bahi session `s`

    from bahi.modules._toolbox import ModuleToolbox, build_module_server
    erp = ERP(modules=["hr_leave"])
    tb = ModuleToolbox(erp, "KJOSHI", "hr_leave")                    # the kit's own tool folders
    tb = ModuleToolbox(erp, "KJOSHI", "hr_leave", folder="my_tools")  # or a folder you are building
    tb.call("check_leave_balance", {})
    server = build_module_server(erp, "KJOSHI", "hr_leave")          # the same tools over MCP

`with_purchasing=["search_policy", "send_message"]` adds tools from the purchasing toolbox, so one Ask Rasoi can
answer from both. Errors come back as ok=False with `next_step`, exactly as in bahi.toolbox.
"""
from __future__ import annotations

import importlib
import json
import pathlib

from ..agent.tools import ToolError
from ..erp.engine import ERP, ServiceTimeout, Session
from ..toolbox import SPECS as PURCHASING, ToolSpec


def module_folder(module: str) -> pathlib.Path:
    return pathlib.Path(importlib.import_module(f"bahi.modules.{module}").__file__).parent / "toolbox"


def load_folder(folder) -> dict[str, ToolSpec]:
    folder = pathlib.Path(folder)
    return {p.parent.name: ToolSpec(p.parent) for p in sorted(folder.glob("*/tool.json"))} if folder.exists() else {}


class ModuleToolbox:
    """A kit's tools bound to one user's Bahi session: that user's own permissions, nobody else's."""

    def __init__(self, erp: ERP, user: str, module: str | None = None, folder=None, with_purchasing=()):
        self.erp, self.user = erp, user
        self.s = erp.session(user) if hasattr(erp, "session") else Session(erp, user)
        self.specs = load_folder(folder or module_folder(module))
        for n in with_purchasing:
            self.specs.setdefault(n, PURCHASING[n])
        self.names = list(self.specs)

    def schemas(self) -> list[dict]:
        return [self.specs[n].schema() for n in self.names]

    def manifest(self) -> list[dict]:
        return [self.specs[n].card() for n in self.names]

    def call(self, name: str, args: dict | None = None) -> dict:
        if name not in self.specs:
            return {"ok": False, "error": f"Unknown tool {name}.", "next_step": f"Use one of {self.names}."}
        t = self.specs[name]
        try:
            return t.module.run(self.s, **t.check(args or {}))
        except ToolError as e:
            return e.as_dict()
        except ServiceTimeout as e:
            return {"ok": False, "error": f"Bahi did not reply in time ({e}).",
                    "next_step": "Look the document up before trying again.", "bahi_code": "TIMEOUT"}
        except TypeError as e:
            return {"ok": False, "error": f"Bad arguments: {e}", "next_step": "Check the tool's parameters."}


def build_module_server(erp: ERP, user: str, module: str | None = None, folder=None, with_purchasing=(),
                        name: str | None = None):
    """A FastMCP server whose tools are the kit's folders, the same way bahi.toolbox.mcp serves purchasing."""
    from fastmcp import FastMCP
    try:
        from fastmcp.tools import Tool, ToolResult
    except ImportError:
        from fastmcp.tools.tool import Tool, ToolResult
    from mcp.types import TextContent, ToolAnnotations

    tb = ModuleToolbox(erp, user, module, folder, with_purchasing)
    mcp = FastMCP(name or f"bahi-{module or 'module'}", instructions=f"Rasoi Steel Works' Bahi ERP, as {user}.")

    class FolderTool(Tool):
        async def run(self, arguments: dict) -> ToolResult:
            return ToolResult(content=[TextContent(type="text", text=json.dumps(tb.call(self.name, arguments),
                                                                                default=str))])

    for n in tb.names:
        spec = tb.specs[n].spec
        mcp.add_tool(FolderTool(name=n, description=spec["description"], parameters=spec["input_schema"],
                                annotations=ToolAnnotations(readOnlyHint=not spec.get("writes"), title=spec["title"])))
    mcp.toolbox = tb
    return mcp


REQUIRED_KEYS = ("name", "title", "category", "description", "input_schema", "output_schema", "writes", "services",
                 "example")


def lint_folder(folder, module: str | None = None) -> list[str]:
    """What modules/test_kits.py checks on every tool folder: tool.json complete, name = folder, schema well formed,
    every listed service exists, run() takes the schema's arguments, a write tool has confirm (or says in
    no_preview_because why not), the example passes the schema check."""
    from ..erp.engine import SERVICES
    import inspect

    if module:  # register the kit's services first, so the check can see them
        importlib.import_module(f"bahi.modules.{module}")
    errs = []
    for p in sorted(pathlib.Path(folder).glob("*/")):
        if not (p / "tool.json").exists():
            continue
        try:
            t = ToolSpec(p)
        except Exception as e:  # noqa: BLE001
            errs.append(f"{p.name}: does not load ({type(e).__name__}: {e})")
            continue
        miss = [k for k in REQUIRED_KEYS if k not in t.spec]
        if miss:
            errs.append(f"{p.name}: tool.json misses {miss}")
        if t.name != p.name:
            errs.append(f"{p.name}: name in tool.json is {t.name}")
        sch = t.spec.get("input_schema", {})
        if sch.get("type") != "object" or not isinstance(sch.get("properties"), dict):
            errs.append(f"{p.name}: input_schema must be an object with properties")
        for svc in t.spec.get("services", []):
            if svc not in SERVICES:
                errs.append(f"{p.name}: service {svc} does not exist")
        params = set(inspect.signature(t.module.run).parameters) - {"s"}
        extra = set(sch.get("properties", {})) - params
        if extra:
            errs.append(f"{p.name}: run() does not take {sorted(extra)}")
        if t.spec.get("writes") and "confirm" not in sch.get("properties", {}) and not t.spec.get("no_preview_because"):
            errs.append(f"{p.name}: a write tool needs a confirm argument (preview first), or no_preview_because "
                        "in tool.json (approve and release tools: the user's instruction is the go-ahead)")
        try:
            t.check(t.spec.get("example") or {})
        except ToolError as e:
            errs.append(f"{p.name}: example fails its own schema ({e.what})")
    return errs
