"""List my approvals: What is waiting for the signed-in user's signature: purchase requests and orders, with value and who raised them..

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import _bahi


def run(s):
    rows = _bahi(s, "po_pending_appr")["rows"]
    out = []
    for r in rows:
        doc = _bahi(s, "pr_get" if r["doc_type"] == "PR" else "po_get",
                    **({"pr_no": r["doc_no"]} if r["doc_type"] == "PR" else {"po_no": r["doc_no"]}))
        out.append({"doc_type": r["doc_type"], "doc_no": r["doc_no"], "requested_by": r["requested_by"],
                    "requested_on": r["requested_on"],
                    "value": doc.get("est_value") if r["doc_type"] == "PR" else doc.get("gross_value"),
                    "item_code": doc["lines"][0]["itm_cd"], "quantity": doc["lines"][0]["qty"]})
    return {"ok": True, "waiting": out, "count": len(out)}
