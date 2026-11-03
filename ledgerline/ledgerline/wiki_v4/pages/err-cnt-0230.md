---
title: "ERR-CNT-0230 Area has open transactions"
type: "error"
slug: "err-cnt-0230"
summary: "Ledgerline error raised on screen INV-CNT-06 when attempting to freeze a stock count area containing open transactions."
audience: "staff"
status: "current"
sources: ["02_procedures/SOP-INV-003 Stock Count v1.2.pdf"]
created: "2026-11-03"
updated: "2026-11-03"
---

| | |
|---|---|
| Error code | ERR-CNT-0230 |
| Message | Area has open transactions |
| Module | Inventory |
| Raised on | [[screen-inv-cnt-06|INV-CNT-06]] |
| Governing procedure | [[sop-inv-003|SOP-INV-003]] |
| Status | Current |

Ledgerline raises error ERR-CNT-0230 when a user attempts to freeze a stock count area that still contains open transactions [^r1]. It blocks the locking of count areas on screen [[screen-inv-cnt-06|INV-CNT-06]] until all pending movements in the specified area are cleared [^r1][^r2]. To proceed with count execution under [[sop-inv-003|SOP-INV-003]], staff must resolve all active transactions prior to freezing stock [^r1][^r2].

## Meaning
ERR-CNT-0230 indicates that the selected inventory count area cannot be frozen because unprocessed stock movements remain active against it [^r1][^r2].

## Cause
The error is caused by open stock movements in the target count area, including unposted pick lists, active work orders, or pending inter-site transfers between Leeds and Manchester [^r2].

## How to fix
Users must ensure that all open movements—such as unposted pick lists, work orders, or inter-site transfers between Leeds and Manchester—are either fully completed or cancelled before attempting to lock the count area on screen [[screen-inv-cnt-06|INV-CNT-06]] [^r1][^r2].

## Raised by
The error is raised by screen [[screen-inv-cnt-06|INV-CNT-06]] during the procedure to freeze a stock count area [^r1].

## See also
* [[sop-inv-003|SOP-INV-003 Stock Count (cycle and annual)]]
* [[screen-inv-cnt-06|INV-CNT-06 Stock Count Entry]]

## References

[^r1]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 3, §5. Procedure
[^r2]: 02_procedures/SOP-INV-003 Stock Count v1.2.pdf, p. 4, What to check on the screen
