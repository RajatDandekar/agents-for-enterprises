"""Test every capstone module kit. Run on Modal, never on the laptop:

    /Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py
    /Users/raj/.venv/bin/modal run tools/modal_run.py --script modules/test_kits.py --args "--only hr_leave"

For each module it checks the complexity budget and the behaviour the brief promises:
  install alone; names prefixed (services, procedures, tables) and no purchasing service overwritten;
  payloads flat and <= 12 fields; 3 valid screen.yaml files; 4-6 policy documents; ~50 seed records;
  the legacy happy path; every trap (silent outcome, variants, screen state, cascades, shared engine);
  4 scenarios whose check() passes the careful reference run and catches the naive run with a never-event;
then installs all eight together and re-runs the reference scenarios on the combined sandbox.
v3 (Lecture 8): each kit's toolbox/ folders (tool.json + tool.py) are linted, every tool's example is called as the
kit's speaker and must return ok=true, and the folders are served over MCP and listed by a client. The TEMPLATE's two
example tools are exercised end to end: preview, commit, the same commit again (found by its key), read-back.
A full run writes modules/test_kits.log.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bahi"))

import yaml  # noqa: E402

from bahi.erp import procs as _p, services as _s  # noqa: E402,F401
from bahi.erp.engine import ERP, PROCS, SERVICES  # noqa: E402
from bahi.modules._kit import KITS, load, run_module_scenario, scripted  # noqa: E402
from bahi.modules._toolbox import ModuleToolbox, build_module_server, lint_folder, module_folder  # noqa: E402

PUR_SERVICES = {n: s.fn.__module__ for n, s in SERVICES.items()}
PUR_PROCS = {n: f.__module__ for n, f in PROCS.items()}
PUR_TABLES = set(re.findall(r"CREATE TABLE (\w+)", __import__("bahi.erp.seed", fromlist=["SCHEMA"]).SCHEMA))
KINDS = {"silent": 1, "variant": 2, "screen_state": 1, "cascade": 2, "shared_engine": 1}

OUT = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=OUT)


def tables_of(schema: str) -> list[str]:
    return re.findall(r"CREATE TABLE (\w+)", schema)


def check_screen(path: str, svcs: dict) -> list[str]:
    errs = []
    try:
        y = yaml.safe_load(open(path))
    except Exception as e:  # noqa: BLE001
        return [f"{os.path.basename(path)}: not YAML ({e})"]
    for k in ("code", "title", "menu", "roles", "fields", "tasks"):
        if k not in y:
            errs.append(f"{y.get('code', path)}: missing {k}")
    if errs:
        return errs
    n_lines = sum(1 for _ in open(path))
    if n_lines > 45:
        errs.append(f"{y['code']}: {n_lines} lines (budget ~30)")
    buttons = {t["button"] for t in y["tasks"]}
    for t in y["tasks"]:
        sv = svcs.get(t.get("service"))
        if not sv:
            errs.append(f"{y['code']}/{t.get('button')}: service {t.get('service')} not found")
            continue
        names = {f.name for f in sv.fields}
        extra = [x for x in t.get("sends", []) if x not in names]
        if extra:
            errs.append(f"{y['code']}/{t['button']}: sends {extra} not in {t['service']}")
        for n in t.get("needs", []):
            if n not in buttons:
                errs.append(f"{y['code']}/{t['button']}: needs unknown button {n}")
    return errs


def test_module(name: str, row: dict, notes: list):
    pkg, S, L = load(name)
    pre = pkg.KIT["prefix"]
    # ---- inventory and names
    mine = {n: s for n, s in SERVICES.items() if s.fn.__module__.startswith(f"bahi.modules.{name}.")}
    my_procs = [n for n, f in PROCS.items() if f.__module__.startswith(f"bahi.modules.{name}.")]
    tabs = tables_of(pkg.SCHEMA)
    bad_names = [n for n in mine if not n.startswith(pre)] + [p for p in my_procs if not p.startswith("sp_" + pre)] + \
                [t for t in tabs if not t.startswith(pre)]
    overwritten = [n for n, m in PUR_SERVICES.items() if SERVICES[n].fn.__module__ != m] + \
                  [n for n, m in PUR_PROCS.items() if PROCS[n].__module__ != m] + [t for t in tabs if t in PUR_TABLES]
    wide = [f"{n}({len(s.fields)})" for n, s in mine.items() if len(s.fields) > 12]
    row["svcs"] = len(mine)
    row["procs"] = len(my_procs)
    row["tables"] = len(tabs)
    row["names"] = "ok" if not (bad_names or overwritten or wide) else "FAIL"
    if bad_names:
        notes.append(f"{name}: unprefixed {bad_names}")
    if overwritten:
        notes.append(f"{name}: collides with purchasing {overwritten}")
    if wide:
        notes.append(f"{name}: payloads over 12 fields {wide}")
    # ---- screens and documents
    base = os.path.dirname(pkg.__file__)
    screens = sorted(glob.glob(os.path.join(base, "screens", "*.yaml")))
    serr = [e for p in screens for e in check_screen(p, SERVICES)]
    row["screens"] = f"{len(screens)}" + ("" if len(screens) == 3 and not serr else " FAIL")
    notes += [f"{name}: {e}" for e in serr]
    docs = glob.glob(os.path.join(base, "docs", "*.md"))
    row["docs"] = len(docs)
    # ---- install alone and count seed records
    erp = ERP(modules=[name])
    plain = ERP()
    seed_rows = sum(erp.q1(f"SELECT count(*) n FROM {t}")["n"] for t in tabs)
    people = erp.q1("SELECT count(*) n FROM app_user")["n"] - plain.q1("SELECT count(*) n FROM app_user")["n"]
    row["seed"] = seed_rows + people
    # ---- happy path (the before)
    erp = ERP(modules=[name])
    n0 = len(erp.calls)
    try:
        hp = L.happy_path(erp)
        run = erp.live_run(n0)
        typed = sum(len([k for k in c["payload"] if k not in ("fetch_tok", "client_ref")]) for c in run)
        row["happy"] = ("ok" if hp.get("ok") else "FAIL") + f" {hp.get('doc', '')} {hp.get('status', '')}"
        row["before"] = f"{len(run)} calls/{len({c['screen'] for c in run if c['screen']})} scr/{typed} fields"
        errs = [f"{c['svc']} {c['err_cd']}" for c in run if c["rc"] == "E"]
        if errs:
            notes.append(f"{name}: happy path errors {errs}")
    except Exception:  # noqa: BLE001
        row["happy"] = "FAIL"
        notes.append(f"{name}: happy path raised\n{traceback.format_exc(limit=3)}")
    # ---- traps
    got, kinds = 0, {}
    for tname, fn in L.TRAPS.items():
        kind = tname.split(":")[0]
        try:
            good, detail = fn(ERP(modules=[name]))
        except Exception as e:  # noqa: BLE001
            good, detail = False, f"raised {type(e).__name__}: {e}"
        got += bool(good)
        kinds[kind] = kinds.get(kind, 0) + bool(good)
        say(f"    [{'ok' if good else 'FAIL'}] {tname}: {detail}")
    short = [k for k, n in KINDS.items() if kinds.get(k, 0) < n]
    row["traps"] = f"{got}/{len(L.TRAPS)}" + (f" missing {short}" if short else "")
    # ---- scenarios: careful run passes, naive run is caught
    ref_ok, nai_ok = 0, 0
    if len(S.SCENARIOS) != 4:
        notes.append(f"{name}: {len(S.SCENARIOS)} scenarios, want 4")
    for sc in S.SCENARIOS:
        r = run_module_scenario(scripted(S.REFERENCE[sc.id]), name, sc)
        ref_ok += r.passed
        say(f"    scenario {sc.id} reference: {'pass' if r.passed else 'FAIL'} {r.never_events} {r.notes}")
        if sc.id in S.NAIVE:
            r2 = run_module_scenario(scripted(S.NAIVE[sc.id], S.NAIVE_RUN_AS.get(sc.id)), name, sc)
            caught = (not r2.passed) and bool(r2.never_events)
            nai_ok += caught
            say(f"    scenario {sc.id} naive:     {'caught' if caught else 'MISSED'} {r2.never_events}")
    row["ref"] = f"{ref_ok}/{len(S.SCENARIOS)}"
    row["naive"] = f"{nai_ok}/{len(S.NAIVE)}"
    # ---- v3: the kit's toolbox folders
    row["tools"] = test_toolbox(name, pkg.KIT["speaker"], notes)


def test_toolbox(name: str, user: str, notes: list, folder=None) -> str:
    folder = folder or module_folder(name)
    errs = lint_folder(folder)
    notes += [f"{name} toolbox: {e}" for e in errs]
    tb = ModuleToolbox(ERP(modules=[name]), user, name, folder=folder)
    bad = 0
    for n in tb.names:
        out = tb.call(n, tb.specs[n].spec.get("example") or {})
        ok = bool(out.get("ok"))
        bad += not ok
        say(f"    tool {n}({json.dumps(tb.specs[n].spec.get('example'))}) as {user}: ok={ok} "
            + json.dumps({k: v for k, v in out.items() if k != "ok"}, default=str)[:160])
        if not ok:
            notes.append(f"{name} toolbox: {n} example returned {out}")
    try:
        from bahi.mcp_server import MCPClient, MCPClientTools
        c = MCPClient(build_module_server(ERP(modules=[name]), user, name, folder=folder))
        listed = MCPClientTools(c).names
        c.close()
        mcp_ok = sorted(listed) == sorted(tb.names)
    except Exception as e:  # noqa: BLE001
        mcp_ok = False
        notes.append(f"{name} toolbox over MCP: {type(e).__name__}: {e}")
    good = not errs and not bad and mcp_ok and tb.names
    return f"{len(tb.names)} " + ("ok" if good else "FAIL") + (" mcp" if mcp_ok else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else list(KITS)  # --only also takes a student's own module
    present = [n for n in names if os.path.exists(os.path.join(HERE, "..", "bahi", "bahi", "modules", n, "__init__.py"))]
    rows, notes = [], []
    for name in present:
        say(f"\n== {name}")
        row = {"module": name}
        try:
            test_module(name, row, notes)
        except Exception:  # noqa: BLE001
            row["install"] = "FAIL"
            notes.append(f"{name}: {traceback.format_exc(limit=4)}")
        rows.append(row)
    # ---- all together
    together = "skipped"
    if len(present) > 1:
        try:
            erp = ERP(modules=present)
            together = f"ok ({len(present)} modules, {len(SERVICES)} services, {len(PROCS)} procedures)"
            bad = 0
            for name in present:
                _, S, L = load(name)
                hp = L.happy_path(ERP(modules=present))
                bad += not hp.get("ok")
                for sc in S.SCENARIOS:
                    r = run_module_scenario(scripted(S.REFERENCE[sc.id]), name, sc, also=tuple(n for n in present if n != name))
                    bad += not r.passed
                    if not r.passed:
                        notes.append(f"together: {name} scenario {sc.id} failed {r.never_events} {r.notes}")
            together += "; happy paths and reference scenarios " + ("all pass" if not bad else f"{bad} FAIL")
        except Exception:  # noqa: BLE001
            together = "FAIL"
            notes.append("together: " + traceback.format_exc(limit=4))
    # ---- the blank template installs and runs (copied into the package for the test, then removed)
    template = "skipped"
    if not a.only:
        import shutil
        dst = os.path.join(HERE, "..", "bahi", "bahi", "modules", "_template_check")
        shutil.copytree(os.path.join(HERE, "TEMPLATE", "package"), dst)
        try:
            from bahi.modules import _template_check as T
            from bahi.modules._template_check import legacy as TL, scenarios as TS
            hp = TL.happy_path(ERP(modules=["_template_check"]))
            traps = [fn(ERP(modules=["_template_check"]))[0] for fn in TL.TRAPS.values()]
            screens = sorted(glob.glob(os.path.join(dst, "screens", "*.yaml")))
            serr = [e for p in screens for e in check_screen(p, SERVICES)]
            ref = run_module_scenario(scripted(TS.REFERENCE[1]), "_template_check", TS.SCENARIOS[0])
            nai = run_module_scenario(scripted(TS.NAIVE[1], "SVC_AGENT"), "_template_check", TS.SCENARIOS[0])
            tools = test_toolbox("_template_check", "KJOSHI", notes, folder=os.path.join(dst, "toolbox"))
            erp = ERP(modules=["_template_check"])
            tb = ModuleToolbox(erp, "KJOSHI", "_template_check", folder=os.path.join(dst, "toolbox"))
            args = {"party": "Sahyadri Valves", "quantity": 40, "amount": 4000}
            pv = tb.call("create_document", args)
            c1 = tb.call("create_document", {**args, "confirm": True})
            erp.inject("xx_save", "timeout_after_commit", 1)
            c3 = tb.call("create_document", {**args, "quantity": 41, "confirm": True})  # reply lost, found by its key
            c2 = tb.call("create_document", {**args, "confirm": True})
            flow = bool(pv.get("preview") and c1.get("doc_no") and c2.get("already_done") and c2["doc_no"] == c1["doc_no"]
                        and c3.get("doc_no") and c3["doc_no"] != c1["doc_no"])
            say(f"    template create_document: preview={bool(pv.get('preview'))} commit={c1.get('doc_no')} {c1.get('status')} "
                f"again={c2.get('doc_no')} already_done={c2.get('already_done')} after-timeout={c3.get('doc_no')}")
            good = hp["ok"] and all(traps) and not serr and ref.passed and not nai.passed and T.KIT["prefix"] == "xx_" \
                and "FAIL" not in tools and flow
            template = ("ok" if good else "FAIL") + f" (happy {hp['status']}, traps {sum(traps)}/{len(traps)}, " \
                f"{len(screens)} screens, reference {'pass' if ref.passed else 'FAIL'}, naive {'caught' if not nai.passed else 'MISSED'}, " \
                f"toolbox {tools}, preview-commit-key {'ok' if flow else 'FAIL'})"
            notes += [f"template: {e}" for e in serr]
        except Exception:  # noqa: BLE001
            template = "FAIL"
            notes.append("template: " + traceback.format_exc(limit=4))
        finally:
            shutil.rmtree(dst, ignore_errors=True)
    cols = ["module", "svcs", "procs", "tables", "screens", "docs", "seed", "names", "happy", "before", "traps", "ref", "naive",
            "tools"]
    say("\n" + " | ".join(cols))
    say(" | ".join("---" for _ in cols))
    for r in rows:
        say(" | ".join(str(r.get(c, "-")) for c in cols))
    missing = [n for n in names if n not in present]
    say(f"\nall installed together: {together}")
    say(f"TEMPLATE kit: {template}")
    if missing:
        say(f"not built yet: {missing}")
    for n in notes:
        say("NOTE " + n)
    failed = [r["module"] for r in rows if any("FAIL" in str(v) for v in r.values()) or r.get("ref", "0/4") != "4/4"
              or r.get("naive", "0/1").split("/")[0] != r.get("naive", "0/1").split("/")[1]]
    failed += ["together"] if "FAIL" in together else []
    failed += ["TEMPLATE"] if "FAIL" in template else []
    say(f"\nRESULT: {'PASS' if not failed and not missing else 'FAIL'}" + (f" (failing: {failed})" if failed else ""))
    if not a.only:
        open(os.path.join(HERE, "test_kits.log"), "w").write(OUT.getvalue())
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
