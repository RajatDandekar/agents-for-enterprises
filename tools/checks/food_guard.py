"""Check the live app's food-grade guard (experience/harness.food_grade_block) on Rasoi's real suppliers."""
import json
from bahi.experience.players import Players
from bahi.experience.harness import food_grade_block
P = Players(); p = P.join("guard-check"); erp = P.erp(p.pid)
cases = [("create_purchase_order", {"supplier_code": "DP-RJK-0042", "item_code": "GSK-SIL-05L", "confirm": True}, False),
         ("create_purchase_order", {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L", "confirm": True}, True),
         ("create_purchase_order", {"supplier_code": "KR-KOL-0063", "item_code": "GSK-SIL-05L"}, False),   # preview only
         ("create_purchase_order", {"supplier_code": "SV-PUN-0017", "item_code": "WHS-STD-01", "confirm": True}, False),  # not food
         ("find_item", {"query": "gasket"}, False)]
for tool, args, want in cases:
    got = food_grade_block(erp, tool, args)
    print(("BLOCK" if got else "pass "), tool, args.get("supplier_code"), json.loads(got)["error"] if got else "")
    assert bool(got) == want, (tool, args)
print("FOOD GUARD OK")
