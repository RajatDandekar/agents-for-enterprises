---
title: "ERR-CNT-0240 Cycle Count Value Variance Exceeds Tolerance"
type: "error"
slug: "err-cnt-0240"
summary: "Ledgerline error raised when count sheet value variance exceeds the INV.CNT_TOL_PCT threshold, locking sheet posting until a recount is performed."
audience: "staff"
status: "current"
sources: ["08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Code | ERR-CNT-0240 |
| Message | Value variance exceeds tolerance |
| Type | Error |
| Parameter | INV.CNT_TOL_PCT (1.5%) |
| Introduced | [[rn-7-2-2|RN-7.2.2]] |

ERR-CNT-0240 is a Ledgerline error triggered during inventory counting when entered count sheet value variance breaches the system tolerance threshold [^r1]. The error locks posting on the affected count sheet and flags the line for mandatory verification [^r2]. As of 26 October 2026, resolving this condition requires conducting a recount before any adjustment or nominal ledger posting can proceed [^r2].

## Meaning
The error indicates that the total value variance calculated for an entered count sheet exceeds the default threshold configured in parameter `INV.CNT_TOL_PCT`, which is set to 1.5% [^r1].

## Cause
Entering stock count figures that deviate from recorded book values by more than the configured 1.5% threshold triggers the error [^r1].

## How to fix
When ERR-CNT-0240 is raised, perform a recount of the flagged item line to verify physical quantities [^r2]. Once recount details are confirmed in accordance with [[sop-inv-003|SOP-INV-003]], the interface permits stock adjustment and nominal ledger posting [^r2].

## Raised by
The count confirmation screen raises this error, which locks the posting action for the sheet and marks the item line for verification [^r1][^r2].

## See also
* [[errors-cnt|Stock Count Error Codes (ERR-CNT-*)]]
* [[rn-7-2-2|RN-7.2.2 Ledgerline ERP 7.2.2 Release Notes]]
* [[sop-inv-003|SOP-INV-003 Stock Count (cycle and annual)]]

## References

[^r1]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 2, §3. Details
[^r2]: 08_release_notes/RN-7.2.2 Ledgerline Release Notes.pdf, p. 2, §3. Details
