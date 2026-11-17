"""Low stock: every item whose free stock plus stock on order is below its reorder level, across warehouses.

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import _ledgerline
from ledgerline.toolbox._ap import need_payables


def run(s):
    need_payables(s)
    rows = _ledgerline(s, "stk_below_reorder")["rows"]
    items = [{"item_code": r["itm_cd"], "description": r["descr"], "free": r["free"], "on_order": r["on_order"],
              "reorder_level": r["reorder_lvl"], "shortfall": r["reorder_lvl"] - r["free"] - r["on_order"],
              "cover_days": r["cover_days"], "last_supplier_code": r["last_sup_cd"]} for r in rows]
    return {"ok": True, "items": items, "count": len(items)}
