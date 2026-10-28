"""Check serial: the starter tool of this kit (read-only). Copy its shape for the rest of your toolbox.

Input and output are described in tool.json next to this file."""
from bahi.agent.tools import ToolError, _bahi  # noqa: F401

def run(s, serial):
    r = _bahi(s, "wr_ser_get", serial=serial)
    out = {"ok": True, "serial": r["serial"], "model": r["model"], "sold_on": r.get("sold_dt"),
           "dealer": r.get("dealer_cd"), "status": r.get("status"), "record": r}
    if not r.get("sold_dt"):
        out["warning"] = "No sale is registered for this serial, so Bahi counts the warranty from manufacture."
    return out
