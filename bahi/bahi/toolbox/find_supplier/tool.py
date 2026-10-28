"""Find supplier: Look a supplier up by name, tolerating different spellings.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import find_supplier


def run(s, name, city=None):
    """Fuzzy-match the supplier master, so 'Deccan Polymers Pvt' and 'Deccan Polymer' find the same company."""
    return find_supplier(s, name, city)
