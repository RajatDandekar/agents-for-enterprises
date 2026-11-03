---
title: "ERR-QCH Quality Hold Error Codes"
type: "error-list"
slug: "errors-qch"
summary: "Error codes under prefix ERR-QCH raised by Ledgerline quality hold inventory services."
audience: "staff"
status: "current"
sources: ["04_service_definitions/inventory/qch_get.yaml", "04_service_definitions/inventory/qch_reject.yaml", "04_service_definitions/inventory/qch_release.yaml", "04_service_definitions/inventory/qch_save.yaml", "04_service_definitions/inventory/qch_search.yaml"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Prefix | ERR-QCH |
| Module | Inventory (INV) |
| Domain | Quality Hold |
| Owning service group | [[services-inv-qch|INV qch services]] |
| Associated screen | [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]] |

Quality hold error codes under prefix ERR-QCH are raised across Ledgerline inventory transactions when creating, releasing, rejecting, or searching inspection hold records [^r1][^r2][^r3][^r4][^r5][^r6][^r7]. These validations guard against invalid record identifiers, incorrect lifecycle states, missing inspection postings, and non-positive quantities [^r1][^r4][^r5][^r6]. The codes surface to operators using [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]] and through underlying [[services-inv-qch|INV qch services]] [^r1][^r2][^r3][^r4][^r5][^r6][^r7].

### ERR-QCH-0001
* **Message**: `QUALITY HOLD NOT FOUND` [^r1][^r2][^r3]
* **Cause**: The specified quality hold identifier does not correspond to an existing record [^r1][^r2][^r3].
* **Remedy**: Verify the quality hold reference number before retrying the action.
* **Raised by**: `qch_get` [^r1], `qch_reject` [^r2], `qch_release` [^r3].

### ERR-QCH-0007
* **Message**: `QUALITY HOLD NOT IN DRAFT (<status>)` [^r4]
* **Cause**: An operation expected the quality hold record to be in DRAFT state, but it is currently in another lifecycle status [^r4].
* **Remedy**: Check the current status of the quality hold on [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]] and ensure workflow prerequisites are met.
* **Raised by**: `qch_release` [^r4].

### ERR-QCH-0201
* **Message**: `QTY MUST BE > 0` [^r6][^r7]
* **Cause**: A transaction quantity was specified that is not greater than zero [^r6][^r7].
* **Remedy**: Specify a positive numeric quantity [^r6][^r7].
* **Raised by**: `qch_save` [^r6], `qch_search` [^r7].

### ERR-QCH-0350
* **Message**: `INSPECTION NOT POSTED` [^r5]
* **Cause**: Attempted to execute a quality hold release before the inspection has been posted [^r5].
* **Remedy**: Complete and post the requisite inspection before attempting to release the hold [^r5].
* **Raised by**: `qch_release` [^r5].

## See also
* [[screen-inv-qch-11|INV-QCH-11 Quality Hold Entry]]
* [[services-inv-qch|INV qch services]]
* [[errors-itm|ERR-ITM error codes]]

## References

[^r1]: 04_service_definitions/inventory/qch_get.yaml, errors
[^r2]: 04_service_definitions/inventory/qch_reject.yaml, errors
[^r3]: 04_service_definitions/inventory/qch_release.yaml, errors
[^r4]: 04_service_definitions/inventory/qch_release.yaml, errors
[^r5]: 04_service_definitions/inventory/qch_release.yaml, errors
[^r6]: 04_service_definitions/inventory/qch_save.yaml, errors
[^r7]: 04_service_definitions/inventory/qch_search.yaml, errors
