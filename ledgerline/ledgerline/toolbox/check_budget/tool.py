"""Check budget: Is a cost centre open, and how much budget is left this quarter? Without a code, lists every open cost centre..

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import check_cost_centre


def run(s, cost_centre=None):
    """Ask Ledgerline's budget check; a CLOSED cost centre turns every order into a silent draft."""
    return check_cost_centre(s, cost_centre)
