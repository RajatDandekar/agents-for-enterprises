"""Check the live app's battery-safety guard (experience/harness.cell_safety_block) on Northbridge's real suppliers."""
import json
from ledgerline.experience.players import Players
from ledgerline.experience.harness import cell_safety_block
P = Players(); p = P.join("guard-check"); erp = P.erp(p.pid)
cases = [("create_purchase_order", {"supplier_code": "VC-EIN-0042", "item_code": "BAT-500", "confirm": True}, False),
         ("create_purchase_order", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500", "confirm": True}, True),
         ("create_purchase_order", {"supplier_code": "NC-GDA-0063", "item_code": "BAT-500"}, False),   # preview only
         ("create_purchase_order", {"supplier_code": "PB-MAN-0017", "item_code": "BEL-STD-01", "confirm": True}, False),  # not food
         ("find_item", {"query": "battery pack"}, False)]
for tool, args, want in cases:
    got = cell_safety_block(erp, tool, args)
    print(("BLOCK" if got else "pass "), tool, args.get("supplier_code"), json.loads(got)["error"] if got else "")
    assert bool(got) == want, (tool, args)
print("FOOD GUARD OK")
