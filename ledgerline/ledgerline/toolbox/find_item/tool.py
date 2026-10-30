"""Find item: Find stock items by description or code (e.g.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import find_item


def run(s, query):
    """Search the item master, word by word, and return the best active matches."""
    return find_item(s, query)
