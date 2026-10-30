"""Register supplier: Register a NEW supplier.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import register_supplier


def run(s, name, city, state, vat_no, confirm=False):
    """Checks the master for a near-duplicate before Ledgerline creates a second code for the same company."""
    return register_supplier(s, name, city, state, vat_no, confirm)
