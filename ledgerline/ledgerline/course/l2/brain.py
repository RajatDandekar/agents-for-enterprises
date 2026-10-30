"""Ask Northbridge at the 'brain' stage: a chat model with no tools and no Northbridge data.

The same system prompt and cold-open question are used by Lecture 2's deck, notebook and experiments,
so the recorded replies (cassette L2v3_coldopen) replay exactly.
"""
import json
import pathlib

MODEL = "gemini:gemini-3.8-flash"

SYSTEM_BRAIN = ("You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of "
                "e-bikes. You help Northbridge's staff with purchasing, stores and suppliers. "
                "Answer the question directly and briefly.")

# What a first Ask Northbridge prompt often looks like: it tells the model it knows Northbridge's stock (it does not).
SYSTEM_CONFIDENT = ("You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of "
                    "e-bikes. You know Northbridge's items, stock levels, suppliers and orders. "
                    "Staff ask you quick questions; answer with the exact figure, in one or two sentences.")

QUESTION = "How many city e-bike battery packs do we have in Manchester stores?"
TRUE_ANSWER = 54000  # BAT-500 in WH-MAN-STR, from ledgerline/ledgerline/erp/seed.py and the check_stock tool

FOLLOW_UP = "Where did that number come from?"


def messages(question: str = QUESTION, system: str = SYSTEM_BRAIN) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": question}]


def load(name: str):
    """Recorded data shipped with the package (model logits, attention, tokens) for replay in the notebook."""
    return json.loads((pathlib.Path(__file__).parent / f"{name}.json").read_text())
