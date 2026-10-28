"""Create document: the shape of every write tool in the course.

  1. preview first: confirm=false saves nothing and says what would happen
  2. an idempotency key made from the document's CONTENT (never a random id), sent as client_ref
  3. look the key up before writing, and again after a timeout: a lost reply must not become a second document
  4. read back what Bahi holds and say it in words; a document that saved but is stuck gets a warning

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi, content_key
from bahi.erp.engine import ServiceTimeout

STATUS = {"DR": "DRAFT", "PA": "WAITING FOR APPROVAL", "HD": "HELD (stuck: not routed)", "AP": "APPROVED",
          "RJ": "REJECTED", "CN": "CANCELLED"}   # the same words as list_documents (each tool.py stands alone)


def _receipt(s, doc_no):
    d = [r for r in _bahi(s, "xx_list")["rows"] if r["doc_no"] == doc_no][0]
    out = {"ok": True, "doc_no": doc_no, "status": STATUS.get(d["status"], d["status"]), "status_code": d["status"]}
    if d["status"] == "HD":   # TODO: your silent outcome
        out["warning"] = "Saved, but HELD: it will not go anywhere until it is fixed. Tell the user plainly."
    return out


def _find(s, key):
    return [r for r in _bahi(s, "xx_list")["rows"] if r.get("client_ref") == key]


def run(s, party, quantity, amount, confirm=False):
    if quantity <= 0:
        raise ToolError("Quantity must be more than zero.", "Ask the user for the quantity.")
    key = content_key("XX", s.user_id, party, quantity, amount)
    found = _find(s, key)
    if found:
        return {**_receipt(s, found[0]["doc_no"]), "already_done": True}
    f = _bahi(s, "xx_fetch", party=party)
    preview = {"party": party, "quantity": quantity, "amount": amount, "cost_centre": f["cc_cd"]}
    if not confirm:
        return {"ok": True, "preview": preview, "note": "Nothing has been saved. Show this to the user and ask to confirm."}
    try:
        doc_no = _bahi(s, "xx_save", party=party, qty=quantity, amount=amount, cc_cd=f["cc_cd"],
                       fetch_tok=f["fetch_tok"], client_ref=key)["doc_no"]
    except ServiceTimeout:
        found = _find(s, key)
        if not found:
            raise ToolError("Bahi timed out and the document was not saved.", "Call again with the same arguments.")
        doc_no = found[0]["doc_no"]
    return _receipt(s, doc_no)
