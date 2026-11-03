"""List my approvals: What is waiting for the signed-in user's signature: purchase requests and orders, with value and who raised them..

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import _ledgerline

CAP = 50  # a result the model can read: above this, list the oldest 50 and say how many there are


def run(s):
    rows = _ledgerline(s, "po_pending_appr")["rows"]
    out = []
    for r in rows[:CAP]:
        doc = _ledgerline(s, "pr_get" if r["doc_type"] == "PR" else "po_get",
                    **({"pr_no": r["doc_no"]} if r["doc_type"] == "PR" else {"po_no": r["doc_no"]}))
        out.append({"doc_type": r["doc_type"], "doc_no": r["doc_no"], "requested_by": r["requested_by"],
                    "requested_on": r["requested_on"],
                    "value": doc.get("est_value") if r["doc_type"] == "PR" else doc.get("gross_value"),
                    "item_code": doc["lines"][0]["itm_cd"], "quantity": doc["lines"][0]["qty"]})
    res = {"ok": True, "waiting": out, "count": len(out)}
    if len(rows) > CAP:  # only then: results below the cap are exactly as before
        res.update(total=len(rows), has_more=True,
                   note=f"Showing the oldest {CAP} of {len(rows)} waiting. Approve or reject these, then call again.")
    return res
