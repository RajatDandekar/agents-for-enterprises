"""Find supplier: Look a supplier up by name, tolerating different spellings.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import find_supplier


def run(s, name, city=None):
    """Fuzzy-match the supplier master, so 'Voltway Cells Pvt' and 'Voltway Polymer' find the same company."""
    return find_supplier(s, name, city)
