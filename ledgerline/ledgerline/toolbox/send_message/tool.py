"""Send message: Send a short message to a colleague or supplier (Slack handle like @daniel, or an email address).

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ServiceTimeout, ToolError, _ledgerline, _peek


def run(s, to, text):
    channel = "SLACK" if to.startswith("@") else "EMAIL"
    last = (_peek(s, "SELECT COALESCE(MAX(id), 0) AS m FROM ntf_queue") or {"m": 0})["m"]
    try:
        _ledgerline(s, "ntf_send", channel=channel, recipient=to, msg=text)
    except ServiceTimeout:  # the reply was lost: was it queued? Look before anyone sends it again
        if not _peek(s, "SELECT id FROM ntf_queue WHERE id>? AND recipient=? AND body=?", last, to, text):
            raise ToolError("Ledgerline timed out and the message was not queued.", "Call again with the same arguments.")
    return {"ok": True, "queued": True, "channel": channel, "to": to}
