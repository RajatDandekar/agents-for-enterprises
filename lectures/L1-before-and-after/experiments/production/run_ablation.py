"""Part 2: the model ablation. Our harness, the same prompt and 15 tools, five missions x three runs; only the model changes.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py \
        --script lectures/L1-before-and-after/experiments/production/run_ablation.py --args "--model anthropic/claude-haiku-5.5"

Writes logs/ablation_<model>.json. The google/gemini-3.8-flash row of the ablation is the "ours" stack of run_stacks.py
(runs 1-3): the same harness, model and cassettes, so it is not run twice.
"""
import argparse

from common import run_jobs

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--runs", default="1,2,3")
ap.add_argument("--budget", type=float, default=1.0)
a = ap.parse_args()
runs = [int(x) for x in a.runs.split(",")]
run_jobs([("ours", a.model, r) for r in runs], f"ablation_{a.model.split('/')[-1]}", a.budget, vars(a))
