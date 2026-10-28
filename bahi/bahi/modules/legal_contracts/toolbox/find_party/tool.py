"""Find contract party: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi  # noqa: F401

def run(s, name=None, gstin=None):
    if not name and not gstin:
        raise ToolError("Give a name or a GSTIN.", "Ask the user who the contract is with.")
    rows = _bahi(s, "ct_party_find", q=name, gstin=gstin)["rows"]
    parties = [{"party_code": r["party_cd"], "name": r["name"], "city": r["city"], "state": r["state"],
                "status": r["status"], "supplier_code": r["sup_cd"], "nda_till": r["nda_till"]} for r in rows]
    out = {"ok": True, "parties": parties, "count": len(parties)}
    if len(parties) > 1:
        out["next_step"] = "Several parties match. Ask the user which one; never assume."
    elif not parties:
        out["next_step"] = "Not on the register. A new party needs PAN and GSTIN before any contract."
    return out
