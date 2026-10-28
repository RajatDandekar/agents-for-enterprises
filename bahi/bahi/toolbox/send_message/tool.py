"""Send message: Send a short message to a colleague or supplier (Slack handle like @rohit, or an email address).

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import _bahi


def run(s, to, text):
    channel = "SLACK" if to.startswith("@") else "EMAIL"
    _bahi(s, "ntf_send", channel=channel, recipient=to, msg=text)
    return {"ok": True, "queued": True, "channel": channel, "to": to}
