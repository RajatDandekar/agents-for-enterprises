"""Search policy: Search Rasoi's purchasing policy and the Bahi manual.

Input and output are described in tool.json next to this file."""
def run(s, question):
    """Retrieve policy clauses the signed-in user is cleared to read (Lecture 3 builds this search)."""
    from bahi.agent.retrieval import search_policy
    return search_policy(question, user=s.user_id)
