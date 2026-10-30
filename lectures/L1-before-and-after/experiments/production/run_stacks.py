"""Part 1: the same Ask Northbridge on three stacks (our harness, OpenAI Agents SDK, LangGraph), same model and tools.

    sh tools/mrun.sh lectures/L1-before-and-after/experiments/production/prod_modal.py \
        --script lectures/L1-before-and-after/experiments/production/run_stacks.py --args "--run 1"

Writes logs/stacks_r<run>.json. Cassettes: ledgerline/cassettes/L1v4_prod_<stack>_gemini-3.8-flash_r<run>.jsonl.
"""
import argparse

from common import run_jobs

ap = argparse.ArgumentParser()
ap.add_argument("--run", type=int, default=1)
ap.add_argument("--model", default="google/gemini-3.8-flash")
ap.add_argument("--stacks", default="ours,openai_agents,langgraph")
ap.add_argument("--budget", type=float, default=1.5)
a = ap.parse_args()
run_jobs([(s, a.model, a.run) for s in a.stacks.split(",")], f"stacks_r{a.run}", a.budget, vars(a))
