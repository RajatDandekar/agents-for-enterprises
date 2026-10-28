"""List documents: a read tool. Reads are safe to repeat; translate status codes into words for the model.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import _bahi

STATUS = {"DR": "DRAFT", "PA": "WAITING FOR APPROVAL", "HD": "HELD (stuck: not routed)", "AP": "APPROVED",
          "RJ": "REJECTED", "CN": "CANCELLED"}   # TODO: your module's statuses


def run(s, status=None):
    rows = _bahi(s, "xx_list", status=status)["rows"]
    return {"ok": True, "count": len(rows),
            "documents": [{"doc_no": r["doc_no"], "party": r["party"], "qty": r["qty"], "amount": r["amount"],
                           "status": STATUS.get(r["status"], r["status"]), "status_code": r["status"]} for r in rows]}
