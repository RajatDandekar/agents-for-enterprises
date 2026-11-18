"""Check that the additive change to nbkit (it now also looks in this lecture's logs) changed nothing for Lecture 6.

    tools/mrun.sh lectures/L6b-guardrails/experiments/l7_modal.py --script nbkit_check.py --image clean

No model, no key. For a Lecture 6 notebook's working directory and for this lecture's: which file does each log name
resolve to? Lecture 6 names must come from Lecture 6's folder, nb7*/l7_* names from this one, and a name that exists in
neither must still raise.
"""
import os
import pathlib
import tempfile

os.environ.pop("ARGUS_KEY", None)
from ledgerline.course.l6 import nbkit

L6 = pathlib.Path("/course/lectures/L6-evals-guardrails-observability/experiments/logs")
L7 = pathlib.Path("/course/lectures/L6b-guardrails/experiments/logs")
ok = True


def where(name):
    return next((d for d in nbkit._log_dirs() if (d / name).exists()), None)


for cwd in (tempfile.mkdtemp(), "/course/lectures/L6b-guardrails"):
    os.chdir(cwd)
    dirs = nbkit._log_dirs()
    print("cwd", cwd, "->", [str(d)[-60:] for d in dirs])
    for name, want in (("convos.json", L6), ("nb6a_turn.json", L6), ("nb6b_good_t02.json", L6), ("guards_attacks_thu.json", L6),
                       ("nb7a_incident.json", L7), ("l7_redteam.json", L7)):
        got = where(name)
        good = got is not None and got.resolve() == want.resolve()
        ok &= good
        print("  ", "OK " if good else "BAD", name, "->", got)
    assert isinstance(nbkit.log("convos.json"), dict) and isinstance(nbkit.log("nb7a_incident.json"), dict)
shared = sorted(p.name for p in L6.glob("*.json") if (L7 / p.name).exists())
print("names present in both folders (must be none):", shared)
ok &= not shared
kit = nbkit.connect("", "")
assert not kit.live and kit.run("nb6c_scripted.json", lambda: 1 / 0)["prompt"] == "good"      # replay returns Lecture 6's record
try:
    nbkit.log("no_such_log_anywhere.json")
    ok = False
except Exception as e:  # noqa: BLE001
    print("a missing log still raises:", type(e).__name__)
print("RESULT", "OK" if ok else "FAILED")
raise SystemExit(0 if ok else 1)
