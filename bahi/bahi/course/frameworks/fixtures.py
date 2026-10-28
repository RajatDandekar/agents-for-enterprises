"""The recorded results of Lecture 8's full run, for the notebook to show with no key.

    from bahi.course.frameworks import fixtures as FX
    FX.scoreboard()          # 12 tasks x 7 setups, run 1 (28 Oct 2026), with run 2's pass count
    FX.load("desks")         # also: guarded, gateway, gateway_question, ollama

Generated from lectures/L8-frameworks/experiments/logs by lectures/L8-frameworks/gen_figdata.py.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).parent / "recorded"


def load(name: str):
    return json.loads((HERE / f"{name}.json").read_text())


def scoreboard() -> list[dict]:
    return load("scoreboard")
