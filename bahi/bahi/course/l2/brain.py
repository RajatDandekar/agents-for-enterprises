"""Ask Rasoi at the 'brain' stage: a chat model with no tools and no Rasoi data.

The same system prompt and cold-open question are used by Lecture 2's deck, notebook and experiments,
so the recorded replies (cassette L2v3_coldopen) replay exactly.
"""
import json
import pathlib

MODEL = "gemini:gemini-3.8-flash"

SYSTEM_BRAIN = ("You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of "
                "pressure cookers. You help Rasoi's staff with purchasing, stores and suppliers. "
                "Answer the question directly and briefly.")

# What a first Ask Rasoi prompt often looks like: it tells the model it knows Rasoi's stock (it does not).
SYSTEM_CONFIDENT = ("You are Ask Rasoi, the assistant on the home page of Rasoi Steel Works, Pune, a maker of "
                    "pressure cookers. You know Rasoi's items, stock levels, suppliers and orders. "
                    "Staff ask you quick questions; answer with the exact figure, in one or two sentences.")

QUESTION = "How many 5-litre silicone gaskets do we have in Pune stores?"
TRUE_ANSWER = 54000  # GSK-SIL-05L in WH-PUN-STR, from bahi/bahi/erp/seed.py and the check_stock tool

FOLLOW_UP = "Where did that number come from?"


def messages(question: str = QUESTION, system: str = SYSTEM_BRAIN) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]


def load(name: str):
    """Recorded data shipped with the package (model logits, attention, tokens) for replay in the notebook."""
    return json.loads((pathlib.Path(__file__).parent / f"{name}.json").read_text())
