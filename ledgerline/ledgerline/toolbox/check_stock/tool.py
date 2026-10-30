"""Check stock: Stock of an item in every warehouse: on hand, allocated, on order, reorder level and days of cover..

Input and output are described in tool.json next to this file."""
from ledgerline.agent.tools import ToolError, _ledgerline


def run(s, item_code):
    """Ask Ledgerline's stock enquiry for each warehouse and add it up."""
    item = _ledgerline(s, "itm_get", itm_cd=item_code)
    rows, reorder, daily = [], None, None
    for w in _ledgerline(s, "whs_list")["rows"]:
        try:
            r = _ledgerline(s, "stk_query", itm_cd=item_code, whs_cd=w["whs_cd"])
        except ToolError:
            continue  # no stock record in this warehouse
        reorder, daily = r["reorder_lvl"], r["avg_daily_issue"]
        rows.append({"warehouse": w["whs_cd"], "name": w["name"], "on_hand": r["on_hand"], "allocated": r["allocated"],
                     "on_order": r["on_order"], "free": r["on_hand"] - r["allocated"]})
    if not rows:
        raise ToolError(f"Ledgerline has no stock record for {item_code}.", "Check the item code with find_item.")
    free = sum(r["free"] for r in rows)
    on_order = sum(r["on_order"] for r in rows)
    return {"ok": True, "item_code": item_code, "description": item["descr"], "unit": item["uom_cd"],
            "warehouses": rows, "free_total": free, "on_order_total": on_order, "reorder_level": reorder,
            "cover_days": int(free / daily) if daily else None,
            "below_reorder": reorder is not None and free + on_order < reorder}
