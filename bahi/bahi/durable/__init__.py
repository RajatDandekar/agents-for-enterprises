"""Lecture 7, The Night Shift: durable execution for the commit-and-approval path.

    keys.py        idempotency keys derived from content (never uuid4)
    model.py       the dataclasses that cross the workflow boundary
    activities.py  the Bahi calls, each safe to retry (look up by key, then write)
    workflow.py    PurchaseOrderWorkflow: request -> wait for approval (signal, timers) -> order -> release
    runtime.py     start a Temporal server / worker / workflow; approve; read the history; DurableBahi (sync)
    killswitch.py  the kill switch and rollout-ladder flags, checked before every write
    drills.py      the failure drills used in NB7 and the L7 experiments

Kept import-free on purpose: the Temporal workflow sandbox re-imports workflow.py, and this package must not drag
the ERP in with it. Import the submodules you need, e.g. `from bahi.durable.runtime import DurableBahi`.
Needs the extra: pip install "bahi-erp[durable]"  (temporalio).
"""
