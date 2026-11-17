"""Draft message: save a message for a person to read and send. A draft is never sent by a machine.

Input and output are described in tool.json next to this file. The same draft (same recipient and subject) while
still pending is found, not saved twice."""
from ledgerline.agent.tools import ToolError, _ledgerline
from ledgerline.toolbox._ap import need_payables


def run(s, to, subject, text, ref=None):
    need_payables(s)
    if len(text.strip()) < 10:
        raise ToolError("The draft is too short to be useful.", "Write the message in full.")
    r = _ledgerline(s, "ntf_draft_save", channel="SLACK" if to.startswith("@") else "EMAIL", recipient=to.strip(),
                    subject=subject.strip()[:200], body=text.strip(), **({"ref": ref} if ref else {}))
    return {"ok": True, "draft_id": r["draft_id"], "already_done": r["already_done"], "to": to.strip(),
            "subject": subject.strip()[:200], "sent": False, "note": "Saved as a draft. A person reads it and sends it."}
