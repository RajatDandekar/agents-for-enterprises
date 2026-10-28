"""Lecture 11, part 6: what one order costs, built from token counts we measured across the course.

    from bahi.course.production import cost as C
    runs = C.load()                                   # measured runs (fixtures/cost_runs.json, made by cost_model.py)
    C.per_order(47233, 3269, "gemini-3.8-flash")      # ₹ for one run, at OpenRouter list prices
    C.month(orders_per_day=120, ...)                  # the calculator behind the deck's sliders

Prices are OpenRouter's list prices read on 28 Oct 2026 (logs/probe_versions.txt), in USD per million tokens, at the
course's fixed ₹88 per USD. Change them here when your provider's prices change; never treat them as measured.
"""
from __future__ import annotations

import json
import pathlib

USD_INR = 88.0
PRICE = {  # USD per million tokens (input, output): OpenRouter /api/v1/models, 2026-10-28
    "gemini-3.8-flash": (0.825, 4.125),
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "llama-guard-4-12b": (0.18, 0.18),
    "gpt-oss-safeguard-20b": (0.075, 0.30),
}


def inr(tokens_in: float, tokens_out: float, model: str) -> float:
    p = PRICE[model]
    return (tokens_in * p[0] + tokens_out * p[1]) / 1e6 * USD_INR


def per_order(tokens_in: float, tokens_out: float, model: str = "gemini-3.8-flash", guard_messages: int = 0,
              guard_tokens_in: float = 0, guard_model: str = "llama-guard-4-12b", retry_rate: float = 0.0) -> dict:
    """₹ for one order: the agent's model calls, plus an input guard on each user message, plus retries.
    retry_rate = the share of model calls sent twice (a failed call is paid for; Temporal's retries are too)."""
    agent = inr(tokens_in, tokens_out, model) * (1 + retry_rate)
    guard = inr(guard_tokens_in * guard_messages, 2 * guard_messages, guard_model)
    return {"agent_inr": round(agent, 4), "guard_inr": round(guard, 4), "total_inr": round(agent + guard, 4)}


def month(orders_per_day: float, inr_per_order: float, days: int = 26) -> float:
    """26 working days a month, Rasoi's calendar."""
    return round(orders_per_day * inr_per_order * days, 2)


def load() -> dict:
    return json.loads((pathlib.Path(__file__).parent / "fixtures" / "cost_runs.json").read_text())
