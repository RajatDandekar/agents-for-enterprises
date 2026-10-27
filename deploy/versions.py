"""Pinned versions: what this build runs, as hashes, checked against deploy/versions.yaml.

    python -m deploy.versions --check     exit 1 if a prompt, tool schema or the workflow changed without a version bump
    python -m deploy.versions --print     print the live hashes (paste into versions.yaml when you bump a version)

Why hashes: "we changed one word in the prompt" is a release. If the hash moves and the version number does not,
the build fails, so a changed prompt can never reach prod without passing the regression gate (Lecture 6) first.
The workflow is pinned the same way for a different reason: Temporal replays a running workflow's history through
the CURRENT workflow code. Changing that code under a workflow that has waited two days for Rohit can break its
replay. Changes go behind workflow.patched("...") or under a new workflow name (see runbook.md, "Rolling back").
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _h(x) -> str:
    s = x if isinstance(x, str) else json.dumps(x, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def current() -> dict:
    from bahi.agent import loop, naive
    from bahi.agent.tools import CORE, TOOLS

    wf = (ROOT / "bahi" / "bahi" / "durable" / "workflow.py").read_text()
    acts = (ROOT / "bahi" / "bahi" / "durable" / "activities.py").read_text()
    return {"prompts": {"toolloop_system": _h(loop.SYSTEM), "naive_system": _h(naive.SYSTEM)},
            "tools": {n: _h(TOOLS[n].schema()) for n in CORE},
            "workflow": {"PurchaseOrder": _h(wf)}, "activities": {"bahi": _h(acts)}}


def check(pinned: dict) -> list[str]:
    live, drift = current(), []
    for group in ("prompts", "tools", "workflow", "activities"):
        for name, h in live[group].items():
            want = pinned.get(group, {}).get(name, {}).get("sha")
            if want != h:
                drift.append(f"{group}.{name}: pinned {want} but the code hashes to {h}; bump its version")
    return drift


if __name__ == "__main__":
    import yaml

    pinned = yaml.safe_load((ROOT / "deploy" / "versions.yaml").read_text())
    if "--print" in sys.argv:
        print(json.dumps(current(), indent=1))
    else:
        d = check(pinned)
        print("\n".join(d) or "versions OK: every prompt, tool schema and the workflow match versions.yaml")
        sys.exit(1 if d else 0)
