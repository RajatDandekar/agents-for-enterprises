"""Lecture 4, section 4: building supplier_certificates from scratch, as data for the slides.

    python lectures/L4-the-hands/experiments/build_tool.py        (light, local; no model call)

The six steps, each with what was actually used or produced:
  1 the job            the questions it answers, and why find_supplier is not enough
  2 services found     the Ledgerline services searched for and chosen (their definitions from erp/services.py)
  3 the schema         tool.json, verbatim
  4 the code           tool.py, verbatim
  5 the error contract every way it can fail, called for real: the legacy reply and the structured error
  6 tests              the tool's tests from tests_toolbox.py, run here, with pass/fail; and its MCP definition
Writes logs/new_tool_build.json.
"""
import inspect
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "ledgerline"))

from ledgerline.erp.engine import ERP, SERVICES  # noqa: E402
from ledgerline.toolbox import ALL, REGISTRY, Toolbox  # noqa: E402

NAME = "supplier_certificates"
spec = REGISTRY[NAME]
out = {"tool": NAME}

# 1 the job
erp = ERP()
fs = Toolbox(erp, "ECLARKE").call("find_supplier", {"name": "Nordic Cell"})
out["1_job"] = {
    "questions": ["Is Nordic Cell Co. still UN 38.3 certified?", "When does Voltway Cells' certificate run out, and what is its reference?",
                  "May we buy BAT-500 from this supplier under Purchase Policy §6.2?"],
    "who_asks": "Emma Clarke (purchase executive), before she orders lithium-cell parts",
    "read_only": True,
    "overlap_with_existing": {"tool": "find_supplier", "gives": "one word per supplier: cell_safety_certificate valid / expired / none",
                              "example": fs["matches"][:2],
                              "missing": ["the certificate's reference and valid-to date", "days left", "other certificate types",
                                          "whether a given item needs UN 38.3 at all (item.cell_safety)"],
                              "verdict": "small overlap; the new tool answers the certificate questions find_supplier cannot"}}

# 2 the services found (the 38 purchasing services; searched by what they read)
cands = {n: s for n, s in SERVICES.items() if n.startswith(("sup_", "itm_"))}
out["2_services_found"] = {
    "searched": "the 38 purchasing services (ledgerline/erp/services.py; northbridge-docs/04_service_definitions must match "
                "it, but that folder was not generated on this machine on 3 Nov 2026)",
    "candidates": [{"name": n, "legacy_title": s.doc, "kind": s.kind,
                    "fields": [f"{f.name}:{f.type}{'*' if f.required else ''}" for f in s.fields]} for n, s in cands.items()],
    "chosen": [{"name": n, "legacy_title": SERVICES[n].doc, "why": why,
                "fields": [{"name": f.name, "type": f.type, "required": f.required, "desc": f.desc} for f in SERVICES[n].fields],
                "source": inspect.getsource(SERVICES[n].fn)} for n, why in (
        ("sup_get", "the supplier exists, its name and status (ACTIVE / BLOCKED)"),
        ("sup_cert_get", "every certificate on file: cert_type, doc_ref, valid_to"),
        ("itm_get", "the item's cell_safety flag: does it need UN 38.3?"))],
    "not_chosen": {"sup_cert_upload": "a write (Lecture 7's record_certificate)", "sup_search": "find_supplier already does name search"}}

# 3 the schema, 4 the code
out["3_schema"] = {"tool.json": json.loads((spec.folder / "tool.json").read_text()),
                   "decisions": ["supplier_code is the only required argument: codes come from find_supplier",
                                 "item_code is optional: with it, the tool answers the §6.2 question directly",
                                 "limit + cursor: a list tool paginates (the production criterion), default 20, at most 50",
                                 "output: valid and days_left per certificate, un38_3 summary, item verdict, total, next_cursor"]}
out["4_code"] = {"tool.py": spec.source, "lines": len(spec.source.splitlines()),
                 "services_called": spec.spec["services"], "today_from": "Ledgerline's own date (erp.today = 2026-10-26)"}

# 5 the error contract, called for real
tb = Toolbox(erp, "ECLARKE", names=ALL)
cases = [("unknown supplier", {"supplier_code": "XX-NOPE-0001"}), ("unknown item", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-5000"}),
         ("missing supplier_code", {}), ("wrong type", {"supplier_code": 42}), ("unknown argument", {"supplier_code": "VC-EIN-0042", "vat": "x"}),
         ("limit out of range", {"supplier_code": "VC-EIN-0042", "limit": 500}), ("bad cursor", {"supplier_code": "VC-EIN-0042", "cursor": "abc"}),
         ("expired supplier for a lithium item (a business answer, not an error)", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}),
         ("blocked supplier code", {"supplier_code": "VC-EIN-0009"})]
errs = []
for label, a in cases:
    n0 = len(erp.calls)
    r = tb.call(NAME, a)
    errs.append({"case": label, "arguments": a, "result": r,
                 "legacy_replies": [{"service": c["svc"], "rc": c["rc"], "err_cd": c["err_cd"], "msg": c["msg"]} for c in erp.live_run(n0)],
                 "ledgerline_calls": len(erp.calls) - n0})
out["5_error_contract"] = {"contract": "ok=false, error (what went wrong, in words), next_step (what to do), ledgerline_code (the legacy code, kept)",
                           "cases": errs}

# 6 tests: the tool's section of tests_toolbox.py, run for real
p = subprocess.run([sys.executable, str(ROOT / "ledgerline" / "tests_toolbox.py")], capture_output=True, text=True,
                   cwd=str(ROOT / "ledgerline"), env={"PYTHONPATH": str(ROOT / "ledgerline"), "PATH": "/usr/bin:/bin"})
test_src = (ROOT / "ledgerline" / "tests_toolbox.py").read_text()
section = test_src[test_src.index("# ---- Lecture 4: supplier_certificates"):test_src.index("# ---- Lecture 4: idempotency")]
out["6_tests"] = {"file": "ledgerline/tests_toolbox.py", "section": section,
                  "assertions": section.count("assert "), "passed": "SUPPLIER_CERTIFICATES OK" in p.stdout,
                  "whole_file_passed": p.returncode == 0, "markers": [l for l in p.stdout.splitlines() if l.endswith(" OK")],
                  "stderr_tail": p.stderr[-400:]}

# and it is on the MCP server
try:
    from ledgerline.mcp_server import MCPClient
    from ledgerline.toolbox.mcp import build_toolbox_server
    c = MCPClient(build_toolbox_server(ERP(), "ECLARKE", names=ALL))
    d = {t.name: t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in c.list_tools()}
    out["mcp_definition"] = d[NAME]
    out["mcp_call"] = c.call_tool(NAME, {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500"}).model_dump(
        mode="json", by_alias=True, exclude_none=True)
    c.close()
    out["registered"] = {"how": "a folder in ledgerline/toolbox/ is picked up by load_specs(); EXTRAS keeps it out of the default "
                                "15 so recorded runs replay; served by name, or with `python -m ledgerline.toolbox.mcp --all`",
                         "tools_with_all": len(d)}
except ImportError as e:
    out["mcp_definition"] = {"not_run": str(e)}

(HERE / "logs" / "new_tool_build.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
print("tests:", out["6_tests"]["markers"], "| assertions in the tool's section:", out["6_tests"]["assertions"])
for e in errs:
    print(f"  {e['case'][:40]:42} ok={e['result'].get('ok')} code={e['result'].get('ledgerline_code')} calls={e['ledgerline_calls']} "
          f"{(e['result'].get('error') or e['result'].get('un38_3') or '')[:70]}")
