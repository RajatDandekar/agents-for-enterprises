"""Ask Northbridge at the 'brain' stage: a chat model with no tools and no Northbridge data (Lecture 2).

The system prompt is the live app's own brain-stage prompt (ledgerline/experience/harness.py, BRAIN, for Emma Clarke),
so the cold open in the deck, the notebook and the experiments is exactly what the Northbridge Experience does at
?stage=brain. Recorded replies: cassettes L2v4_coldopen_r1 ... r8 (one per run) and L2v4_facts, L2v4_cutoff.
"""
import json
import pathlib

from ...experience import harness
from ...llm import LLM, PRICES

MODEL = "gemini:gemini-3.8-flash"
USER = "ECLARKE"
SYSTEM_BRAIN = harness._system("brain", USER)  # the app's prompt at ?stage=brain, for Emma Clarke

QUESTION = "How many city e-bike battery packs do we have in Manchester stores?"
TRUE_ANSWER = 5400  # BAT-500 on hand in WH-MAN-STR (Manchester main stores): ledgerline/erp/seed.py, check_stock
FOLLOW_UP = "Where did that number come from?"

# Lecture 2 section 9: the same question with one Ledgerline stock line as the last line of the system prompt.
# The same line the 3D trace uses (brain3d/capture_trace.py, FACT), so the Gemini and Qwen runs are comparable.
FACT = "Ledgerline stock, BAT-500 at Manchester main stores: 5,400 on hand"
SYSTEM_FACTS = SYSTEM_BRAIN + "\n" + FACT

USD_GBP = 0.79  # fixed for the course (as course.l1.production.tracing): £ = US dollars x 0.79


def messages(question: str = QUESTION, system: str = SYSTEM_BRAIN) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]


def cost_gbp(tokens_in: int, tokens_out: int, model: str = MODEL) -> float:
    """List-price cost of one call in pounds, from ledgerline.llm.PRICES (US dollars per million tokens)."""
    p_in, p_out = PRICES[model.split(":", 1)[-1].split("/")[-1]]
    return (tokens_in * p_in + tokens_out * p_out) / 1e6 * USD_GBP


class BrainOnly(harness.AskNorthbridge):
    """The app's Ask Northbridge at stage 'brain' (no tools), with its model calls kept in a named cassette.

    Everything else is the app's own code: the same system prompt, model chain and token limit."""

    def __init__(self, cassette: str, user: str = USER, system: str | None = None, temperature: float = 0.0):
        super().__init__(None, user, "brain")
        self.cassette, self.temperature = cassette, temperature
        if system is not None:
            self.messages = [{"role": "system", "content": system}]

    def _llm(self, model: str) -> LLM:
        if model not in self.llms:
            self.llms[model] = LLM(model, cassette=self.cassette, max_tokens=harness.MAX_TOKENS,
                                   temperature=self.temperature)
        return self.llms[model]


def ask(question: str = QUESTION, cassette: str = "L2v4_coldopen_r1", system: str | None = None) -> dict:
    """One message to the brain-only Ask Northbridge; returns the app's reply dict (reply, tokens_in, tokens_out, ...)."""
    return BrainOnly(cassette, system=system).respond(question)


def load(name: str):
    """Recorded data shipped with the package (Qwen numbers, tokens, the tiny GPT run) for replay in the notebook."""
    return json.loads((pathlib.Path(__file__).parent / f"{name}.json").read_text())
