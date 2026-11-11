"""Retries and idempotency, measured: Bahi saves the PR and then times out. Is a retry safe?

    lectures/L6-the-studio/experiments/mrun.sh --script lectures/L6-the-studio/experiments/retry_idem.py
Writes logs/retry_idem.json. Two fault points: after pr_submit commits, and after pr_save commits (before submit)."""
import json
import pathlib

from bahi.erp.engine import ERP
from bahi.toolbox import Toolbox

LOG = pathlib.Path(__file__).parent / "logs" / "retry_idem.json"
ARGS = {"item_code": "GSK-SIL-05L", "quantity": 20000, "cost_centre": "PRD-07", "need_by": "2026-11-09", "confirm": True}
out = {"_what": __doc__, "cases": {}}
for svc in ["pr_submit", "pr_save"]:
    erp = ERP()
    erp.inject(svc, "timeout_after_commit")
    tb = Toolbox(erp, "KJOSHI")
    first = tb.call("create_purchase_request", ARGS)
    retry = tb.call("create_purchase_request", ARGS)
    third = tb.call("create_purchase_request", ARGS)
    prs = [dict(r) for r in erp.q("SELECT pr_no, status FROM pr_hdr WHERE pr_no >= 'PR/2026/04417'")]
    out["cases"][svc] = {"first": first, "retry": retry, "third": third, "prs_in_bahi": prs}
    print(svc, "| first:", first.get("ok"), first.get("bahi_code"), "| retry:", retry.get("already_done"),
          retry.get("status"), "| PRs:", prs)
# no fault: the naive alternative, a key from uuid4, simulated by changing need_by on the retry
erp = ERP()
tb = Toolbox(erp, "KJOSHI")
a = tb.call("create_purchase_request", ARGS)
b = tb.call("create_purchase_request", {**ARGS, "need_by": "2026-11-10"})
out["different_content"] = {"first": a.get("request_no"), "second": b.get("request_no"), "second_already_done": b.get("already_done")}
print("different content ->", out["different_content"])
LOG.write_text(json.dumps(out, indent=1, default=str))
