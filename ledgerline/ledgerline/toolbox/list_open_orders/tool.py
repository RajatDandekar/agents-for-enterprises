"""List open orders: released purchase orders not fully received yet, with how many days late each one is.

Input and output are described in tool.json next to this file. Built in Lecture 5 for the late-order chaser."""
from ledgerline.agent.tools import _ledgerline
from ledgerline.toolbox._ap import need_payables


def run(s, min_days_late=None, supplier_code=None, buyer=None):
    need_payables(s)
    args = {"days_late": min_days_late, "sup_cd": (supplier_code or "").strip().upper() or None,
            "created_by": (buyer or "").strip().upper() or None}
    r = _ledgerline(s, "po_open_list", **{k: v for k, v in args.items() if v is not None})
    rows = [{"po_no": o["po_no"], "supplier_code": o["sup_cd"], "supplier_name": o["sup_name"],
             "supplier_email": o["sup_email"], "item_code": o["itm_cd"], "description": o["descr"], "ordered": o["qty"],
             "received": o["received"], "outstanding": o["outstanding"], "need_by": o["need_dt"],
             "days_late": o["days_late"], "buyer": o["created_by"], "value_outstanding": round(o["outstanding"] * o["rate"], 2)}
            for o in r["rows"]]
    return {"ok": True, "as_of": r["as_of"], "orders": rows, "count": len(rows),
            "filter": {"min_days_late": min_days_late, "supplier_code": args["sup_cd"], "buyer": args["created_by"]}}
