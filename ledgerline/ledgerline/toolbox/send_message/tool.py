"""Send message: Send a short message to a colleague or supplier (Slack handle like @daniel, or an email address).

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import _ledgerline


def run(s, to, text):
    channel = "SLACK" if to.startswith("@") else "EMAIL"
    _ledgerline(s, "ntf_send", channel=channel, recipient=to, msg=text)
    return {"ok": True, "queued": True, "channel": channel, "to": to}
